from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render

class ExceptionMiddleware(MiddlewareMixin):
    '''异常反馈中间件 需要在settings中注册'''

    def process_exception(self, request, exception):

        error = exception.__str__()
        return render(request, 'error.html', {'err':error})