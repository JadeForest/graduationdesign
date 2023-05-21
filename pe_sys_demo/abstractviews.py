'''
自定义抽象的视图类，用于对数据库某一张表的数据进行列表显示与增删改查
'''

from django.views import View
from django.http import JsonResponse
from django.shortcuts import render

from .util import MyPaginator, CsrfExemptView, handle_search_data

from pure_pagination import PageNotAnInteger

class ListView(View):
    '''
    列表视图，可对单一Model（或特定的Queryset）进行分页展示，并提供搜索、生成表单功能。
    '''
    Model = None
    template = None
    SeForm = None #搜索表单
    Form = None #编辑表单
    search_args = [] #搜索函数的参数
    search_kwargs = {}
    ordering_field = '' #排序字段
    per_page = 10 #每页显示的条数

    def get_model(self, request, *args, **kwargs):
        return self.Model.objects

    def get_queryset(self, request, *args, **kwargs):
        # 搜索
        model = self.get_model(request, *args, **kwargs)
        if model == 0:
            return model
        if self.SeForm:
            cond_dict = handle_search_data(request.GET, *self.search_args, **self.search_kwargs)
            queryset = model.filter(**cond_dict)
        else:
            queryset = model
        
        ordering_fields = self.ordering_field
        if ordering_fields:
            if isinstance(ordering_fields, str):
                ordering_fields = (ordering_fields,)
        queryset = queryset.order_by(*ordering_fields)
        return queryset
    
    def pagination(self, request, queryset):
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = MyPaginator(queryset, per_page=self.per_page, request=request)
        page_obj = p.page(page)
        count = p.count

        return page_obj, count

    def get_context(self, request, *args, **kwargs):
        # 搜索结果
        queryset = self.get_queryset(request, *args, **kwargs)
        # 分页
        if queryset != 0:
            page, count = self.pagination(request, queryset)
        else:
            page, count = None,
        # 表单与搜索表单（如果有）
        form = self.Form() if self.Form else None
        se_form = self.SeForm(data=request.GET) if self.SeForm else None

        context = {
            'form':form,
            'page':page,
            'se_form':se_form,
            'totalnum':count
        }
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context(request, *args, **kwargs)
        return render(request, self.template, context)


class AddView(CsrfExemptView):
    '''添加视图，处理对某一Model数据添加的ajax请求'''
    Form = None #表单

    def get_form(self, request):
        return self.Form(data=request.POST)
    
    def post(self, request):
        form = self.get_form(request)
        if form.is_valid():
            form.save()
            return JsonResponse( {'status':True} )
        return JsonResponse( {'status':False, 'error':form.errors} )


class EditView(CsrfExemptView):
    '''编辑视图，处理对某一Model数据进行编辑的ajax请求'''
    Form = None
    Model = None
    id_field = None #该数据在ajax请求中的识别字段
    model_field = 'pk' #该数据在Model中的识别字段

    def get_edit_obj(self, request):
        id = request.GET.get(self.id_field)
        cond_dict = {self.model_field:id}
        return self.Model.objects.filter(**cond_dict).first()

    def get_form(self, request):
        obj = self.get_edit_obj(request)
        form = self.Form(data=request.POST, instance=obj)
        return form

    def post(self, request):
        form = self.get_form(request)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': True})
        return JsonResponse({'status':False, 'error':form.errors} )
    

class DetailView(View):
    '''详情视图，处理获取某一Model中特定字段数据的ajax请求'''
    Model = None
    id_field = None
    model_field = 'pk'
    value_fields = None #要获取的字段列表

    def get_dict(self, request):
        id = request.GET.get(self.id_field)
        cond_dict = {self.model_field:id}
        return self.Model.objects.filter(**cond_dict).values(*self.value_fields).first()

    def get(self, request):
        obj_dict = self.get_dict(request)

        if obj_dict:
            return JsonResponse({'status':True, 'data':obj_dict})
        else:
            return JsonResponse({'status':False,'error':'数据库中没有找到该项目。'})


class DelView(CsrfExemptView):
    '''删除视图，处理删除某一Model中数据的ajax请求'''
    Model = None
    id_field = None
    model_field = 'pk'

    def post(self, request):
        id = request.POST.get(self.id_field)
        cond_dict = {self.model_field:id}
        exist = self.Model.objects.filter(**cond_dict).exists()

        if exist:
            self.Model.objects.filter(**cond_dict).delete()
            return JsonResponse({'status': True})
        else:
            return JsonResponse({'status': False, 'error':'数据库中没有找到该项目。'})
