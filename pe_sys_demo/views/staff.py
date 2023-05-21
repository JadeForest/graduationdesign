from django.http import JsonResponse
from django.shortcuts import render
from django import forms

from django.views.decorators.csrf import csrf_exempt

from ..models import Staff, Account
from ..util import BootstrapModelForm, SearchForm
from . import user

'''
医务人员用户管理相关视图, 部分继承自体检人员用户（user.py中的）视图
'''

## 医务人员列表 增删改查
class StaffAccModelForm(BootstrapModelForm):
    idnum = forms.CharField(
        label='工号',
        error_messages={'unique':'工号已存在。'}    
    )
    
    class Meta:
        model = Account
        fields = ['idnum']


class StaffModelForm(BootstrapModelForm):
    gender_choice = ((0,'男'),(1,'女'))
    gender = forms.ChoiceField(required=False,
                                      label='性别',
                                      choices=gender_choice,
                                      widget=forms.Select)
    class Meta:
        model = Staff
        fields = ['name','gender','phone']

class StaffSearchForm(SearchForm):
    account__idnum = forms.CharField(label='工号')
    name = forms.CharField(label='姓名')
    gender = forms.ChoiceField(choices=((None,'性别'),(0,'男'),(1,'女')))
    gender.widget.attrs['style'] = 'width: 90px;'


class StaffListView(user.UserListView):
    """医务人员列表"""
    Model = Staff
    template = 'staff_list.html'
    SeForm = StaffSearchForm
    AForm = StaffAccModelForm
    Form = StaffModelForm
    search_args = [['name'],['gender']]
    

class AddStaffView(user.AddUserView):
    Form = StaffModelForm
    AForm = StaffAccModelForm
    acc_type = 2
   
    def set_pwd(self, idnum):
        return idnum
    

class EditStaffView(user.EditUserView):
    Form = StaffModelForm
    AForm = StaffAccModelForm
    Model = Staff

class GetStaffDetail(user.GetUserDetail):
    Model = Staff
    value_fields = ['account__idnum',
                    'name','gender','phone']

@csrf_exempt
def reset_pwd(request):
    '''重置密码'''
    uid = request.POST.get('uid')
    acc_obj = Account.objects.filter(uid=uid).first()

    if acc_obj:
        acc_obj.pwd = acc_obj.idnum
        acc_obj.save()
        return JsonResponse({'status':True})
    return JsonResponse({'status':False,'error':'未找到该用户'})



## 医务人员个人页面的视图
def staff_pg(request, uid):
    "医务人员主页"
    if uid != request.session['info']['uid']:
        raise Exception('没有权限访问。')
    
    staff_obj = Staff.objects.filter(account_id=uid).first()

    if not staff_obj:
        raise Exception('未找到该用户。')
    
    context = {
        'user':staff_obj
    }
    return render(request, 'staff_index.html', context)


class StaffInfoEdit(user.UserInfoEdit):
    "编辑信息"
    template = 'staff_infoedit.html'
    Model = Staff
    Form = StaffModelForm