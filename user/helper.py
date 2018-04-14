# coding: utf-8

from django.shortcuts import render

from user.models import User


def login_required(view_func):
    def wrap(request):
        uid = request.session.get('uid')
        if uid is None:
            return render(request, 'login.html', {'error': '请先登录'})
        return view_func(request)
    return wrap


def need_permission(need_perm):
    def wrap1(view_func):
        def wrap2(request):
            uid = request.session.get('uid')
            user = User.objects.get(id=uid)

            if user.has_permission(need_perm):
                return view_func(request)
            else:
                return render(request, 'blockers.html')
        return wrap2
    return wrap1
