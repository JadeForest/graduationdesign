from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect, render

import re

# 各个atype可以访问的url_pattern
PERMIT_URL_PATTERNS = {
    1:[
        '^/logout/$',
        r'^/user/[0-9]*/',
        '^/rec/$',
        '^/rec/by_item/$',
    ],
    2:[
        '^/logout/$',
        r'^/staff/[0-9]*/',
        '^/item/',
        '^/itype/',
        '^/diag/',
        '^/event/',
        '^/rec/'
    ]
}

class AuthMiddleware(MiddlewareMixin):
    '''权限中间件 需要在settings中注册'''

    def process_request(self, request):
        '''登录限制'''
        # 排除不需登录的页面
        if request.path_info in '/login/':
            return None
        
        # 读取session信息 已登录则继续访问 否则跳转
        info_dict = request.session.get('info')
        if not info_dict:
            return redirect('/login/')

        atype = request.session['atype']
        # 管理员有所有访问权限
        if atype == 0:
            return None
        
        else:
            url_path = request.path
            matchs = [False if re.match(pattern, url_path) else True for pattern in PERMIT_URL_PATTERNS[atype]]
            if all(matchs):
                return render(request, 'error.html', {'err':'没有权限访问。'})
            return None