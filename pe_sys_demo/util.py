'''
自定义模块与组件
'''

from django.forms import ModelForm, Form
from django.views import View
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import uri_to_iri

from pure_pagination import PageNotAnInteger

## ==========自定义pure_pagination模块============
from pure_pagination.paginator import Paginator, Page

class MyPage(Page):
    def render(self):
        return render_to_string('pagination.html', {
            'current_page': self,
            'page_obj': self
        })
    
class MyPaginator(Paginator):
    def page(self, number):
        "Returns a Page object for the given 1-based page number."
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count
        return MyPage(self.object_list[bottom:top], number, self)




## =================自定义工具函数================
def handle_search_data(GET_dict, contain_field_list=None, filter_field_list=None, str_field_list=None):
    '''搜索函数 搜索参数与SQL查询参数映射的处理'''
    condition_dict = {}
    if contain_field_list:
        for field in contain_field_list:
            qstr = GET_dict.get(field)
            if qstr:
                condition_dict[field+'__contains'] = qstr

    if filter_field_list:
        for field in filter_field_list:
            qstr = GET_dict.get(field)
            if qstr and qstr.isdecimal():
                condition_dict[field] = int(qstr)

    if str_field_list:
        for field in str_field_list:
            qstr = GET_dict.get(field)
            if qstr:
                condition_dict[field] = qstr

    return condition_dict


def deserializer(datastr):
    '''反序列化提交的form数据'''
    if not datastr:
        return False
    recs = datastr.split('&')
    rec_list = [i.split('=') for i in recs]
    return {key:uri_to_iri(value) for key,value in rec_list}


def pagination(request, per_page, queryset):
    ''' 分页 '''
    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        page = 1

    p = MyPaginator(queryset, per_page=per_page, request=request)
    page_obj = p.page(page)
    count = p.count

    return page_obj, count




## ==============自定义表单==============
class Bootstrap():
    '''表单样式组件'''
    not_required_fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs['class'] = "form-control"
            field.widget.attrs['placeholder'] = field.label

        for field in self.not_required_fields:
            self.fields[field].required = False

class BootstrapModelForm(Bootstrap, ModelForm):
    pass
    
class BootstrapForm(Bootstrap, Form):
    pass

class SearchForm(BootstrapForm):
    '''搜索表单样式组件'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs['name'] = name
            field.required = False

            if not field.widget.attrs.get('style'): 
                field.widget.attrs['style'] = "width: 140px;"



## =============自定义视图=============
class CsrfExemptView(View):
    '''需要csrf_exempt装饰器的视图类'''
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(CsrfExemptView, self).dispatch(*args, **kwargs)
