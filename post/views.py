from math import ceil

from django.shortcuts import render, redirect

from common import rds
from common import keys
from post.models import Post, Comment, Tag
from post.helper import page_cache
from post.helper import get_top_n
from user.helper import login_required
from user.helper import need_permission


def post_list(request):
    page = int(request.GET.get('page', 0)) or 1  # 当前页数
    total = Post.objects.count()              # 文章总数
    pages = ceil(total / 10)                  # 总页数

    start = (page - 1) * 10
    end = start + 10
    posts = Post.objects.all().order_by('-create')[start:end]

    return render(request, 'post_list.html', {'posts': posts, 'pages': range(1, pages + 1)})


@login_required
@need_permission('create')
def create(request):
    if request.method == 'POST':
        uid = request.session['uid']
        title = request.POST.get('title')
        content = request.POST.get('content')
        post = Post.objects.create(uid=uid, title=title, content=content)
        return redirect('/post/read/?post_id=%s' % post.id)

    return render(request, 'create.html')


@page_cache(1)
def read(request):
    post_id = int(request.GET.get('post_id'))
    try:
        post = Post.objects.get(id=post_id)   # 缓存没有取到时，从数据库获取一次
        rds.zincrby(keys.READ_RANK, post.id)  # 增加阅读计数
    except Post.DoesNotExist as e:
        return redirect('/')

    return render(request, 'read.html', {'post': post, 'tags': post.tags()})


@login_required
@need_permission('edit')
def edit(request):
    if request.method == 'POST':
        post_id = int(request.POST.get('post_id'))
        post = Post.objects.get(id=post_id)

        post.title = request.POST.get('title', '')
        post.content = request.POST.get('content', '')
        post.save()

        # 处理 Tags
        tags = request.POST.get('tags', '')
        tag_names = [tag.strip().title() for tag in tags.split(',')]
        post.update_tags(tag_names)
        return redirect('/post/read/?post_id=%s' % post.id)
    else:
        post_id = int(request.GET.get('post_id'))
        post = Post.objects.get(id=post_id)
        tags = ', '.join(t.name for t in post.tags())
        return render(request, 'edit.html', {'post': post, 'tags': tags})


def search(request):
    keyword = request.POST.get('keyword', '')
    posts = Post.objects.filter(content__contains=keyword)
    return render(request, 'search.html', {'posts': posts})


def top10(request):
    # [
    #     (post1, 100),
    #     (post2, 99),
    #     (post3, 90),
    # ]
    rank_data = get_top_n(10)
    return render(request, 'top10.html', {'rank_data': rank_data})


@login_required
@need_permission('comment')
def comment(request):
    if request.method == 'POST':
        uid = request.session['uid']
        pid = request.POST.get('post_id')
        content = request.POST.get('content')
        if content:
            Comment.objects.create(pid=pid, uid=uid, content=content)
        return redirect('/post/read/?post_id=%s' % pid)
    else:
        return redirect('/')


def tag_filter(request):
    tag_id = request.GET.get('tag_id')
    tag = Tag.objects.get(id=tag_id)
    return render(request, 'search.html', {'posts': tag.posts()})
