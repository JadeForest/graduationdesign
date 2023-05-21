from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django import forms
from django.core.exceptions import ValidationError

from ..models import Account
from ..util import BootstrapModelForm, CsrfExemptView, pagination

'''
管理员视图
'''

class AccountModelForm(BootstrapModelForm):
    "账户表单"
    idnum = forms.CharField(
        label='管理员账号',
        error_messages={'unique':'账户名已存在。'}    
    )

    class Meta:
        model = Account
        fields = ['idnum','pwd']


class AdminListView(View):
    """管理员列表"""    
    def get_context(self, request):
        admin_set = Account.objects.filter(atype=0).order_by('-uid')
        # 分页
        page, count = pagination(request, 10, admin_set)

        context = {
            'page':page,
            'totalnum':count
        }
        return context

    def get(self, request):
        context = self.get_context(request)
        a_form = AccountModelForm()
        context['a_form'] = a_form
        return render(request, 'admin_list.html', context)


class AddAdminView(CsrfExemptView):
    "增"
    def get_forms(self, request):
        a_form = AccountModelForm(data=request.POST)
        return a_form

    def post(self, request):
        a_form = self.get_forms(request)
        if a_form.is_valid():
            a_form.instance.atype=0
            a_form.save()
            
            return JsonResponse( {'status':True} )
        
        return JsonResponse( {'status':False, 'a_err':a_form.errors} )


class EditAdminView(CsrfExemptView):
    "改"
    def get_forms(self, request):
        uid = request.GET.get('uid')
        acc = Account.objects.filter(uid=uid).first()

        a_form = AccountModelForm(data=request.POST, instance=acc)
        return a_form

    def post(self, request):
        a_form = self.get_forms(request)
        if a_form.is_valid():
            a_form.save()
            return JsonResponse( {'status':True} )
        return JsonResponse( {'status':False, 'a_err':a_form.errors} )



class GetAdminDetail(View):
    "查"
    def get(self, request):
        uid = request.GET.get('uid')
        obj_dict = Account.objects.filter(uid=uid).values('idnum','pwd').first()

        if obj_dict:
            return JsonResponse({'status':True, 'data':obj_dict})
        else:
            return JsonResponse({'status':False,'error':'数据库中没有找到该项目。'})



def admin_pg(request):
    "管理员主页"
    return render(request, 'admin_index.html') 