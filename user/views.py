from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password

from user.models import User
from user.forms import RegisterForm


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)  # 保存图片，但不会向数据库提交
            user.password = make_password(user.password)
            user.save()

            # 向 session 写入登陆状态
            request.session['uid'] = user.id
            request.session['nickname'] = user.nickname

            # 返回用户信息页
            return redirect('/user/info/')
        else:
            return render(request, 'register.html', {'error': form.errors})

    return render(request, 'register.html')


def login(request):
    if request.method == 'POST':
        # 取出 POST 数据
        nickname = request.POST.get('nickname')
        password = request.POST.get('password')
        try:
            user = User.objects.get(nickname=nickname)
        except User.DoesNotExist as e:
            return render(request, 'login.html', {'error': e})

        # 验证密码
        if check_password(password, user.password):
            # 向 session 写入登陆状态
            request.session['uid'] = user.id
            request.session['nickname'] = user.nickname
            return redirect('/user/info/')
        else:
            return render(request, 'login.html', {'error': '密码错误'})
    return render(request, 'login.html')


def user_info(request):
    uid = request.session.get('uid')
    user = User.objects.get(id=uid)
    return render(request, 'user_info.html', {'user': user})


def logout(request):
    # 删除用户的 session 数据
    request.session.flush()
    return redirect('/')
