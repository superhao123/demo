# coding: utf-8

import time

from django.utils.deprecation import MiddlewareMixin


def simple_middleware(get_response):
    def wrap(request):
        print('i am in')
        response = get_response(request)
        print('i am out')
        return response
    return wrap


def block_middleware(get_response):
    def wrap(request):
        now = time.time()
        request_times = request.session.get('request_times', [0, 0])
        first = request_times.pop(0)
        request_times.append(now)
        request.session['request_times'] = request_times

        # 如果小于 1 秒，强制等待
        if (now - first) < 1:
            print('等待 100 s')
            time.sleep(100)

        response = get_response(request)
        return response
    return wrap


class BlockMiddleware(MiddlewareMixin):
    def process_request(self, request):
        now = time.time()
        request_times = request.session.get('request_times', [0, 0])
        first = request_times.pop(0)
        request_times.append(now)
        request.session['request_times'] = request_times

        # 如果小于 1 秒，强制等待
        if (now - first) < 1:
            print('等待 100 s')
            time.sleep(100)
