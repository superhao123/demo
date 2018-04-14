# coding: utf-8

from django.core.cache import cache

from common import rds
from common import keys
from post.models import Post


def page_cache(timeout):
    def wrap1(view_func):
        def wrap2(request):
            key = keys.PAGE_CACHE % request.get_full_path()
            response = cache.get(key)  # 先从缓存取
            print('get from cache', response)
            if response is None:
                response = view_func(request)  # 缓存里没有，直接执行 view 函数
                print('get from view', response)
                cache.set(key, response, timeout)    # 把执行结果添加到缓存
                print('set to cache')
            else:
                if view_func.__name__ == 'read':
                    post_id = int(request.GET.get('post_id'))
                    rds.zincrby(keys.READ_RANK, post_id)  # 增加阅读计数

            return response
        return wrap2
    return wrap1


def get_top_n(n):
    # 获取排名原始数据
    # [
    #     (b'28', 3.0),
    #     (b'26', 3.0),
    #     (b'31', 2.0),
    #     (b'35', 1.0),
    #     (b'30', 1.0)
    # ]
    ori_data = rds.zrevrange(keys.READ_RANK, 0, n - 1, withscores=True)

    # rank_data =[]
    # for data in ori_data:
    #     post_id = int(data[0])
    #     count = int(data[1])
    #     rank_data.append([post_id, count])
    # ======================================
    # rank_data = [
    #     (28, 3),
    #     (26, 3),
    #     (31, 2),
    #     (35, 1),
    #     (30, 1),
    # ]
    rank_data = [[int(data[0]), int(data[1])] for data in ori_data]

    # 获取对应的 Post
    # for data in rank_data:
    #     post = Post.objects.get(id=data[0])
    #     data[0] = post
    id_list = [post_id for post_id, _ in rank_data]
    posts = Post.objects.filter(id__in=id_list)
    posts = sorted(posts, key=lambda post: id_list.index(post.id))

    # 整理数据格式
    rank_data = [(post, data[1]) for post, data in zip(posts, rank_data)]
    return rank_data
