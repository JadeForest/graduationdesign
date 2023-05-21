from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django import forms
from django.db.utils import IntegrityError
from django.core.validators import RegexValidator
from django.views.decorators.csrf import csrf_exempt
from django.utils.safestring import mark_safe


import xlrd
import re

from ..models import User, Account
from ..util import BootstrapModelForm, SearchForm
from ..abstractviews import ListView, AddView, EditView, DetailView

'''
体检用户管理相关视图
'''

IDNUM_REGEX = r'^([1-6][1-9]|50)[0-9]{4}(19|20)[0-9]{2}((0[1-9])|10|11|12)(([0-2][1-9])|10|20|30|31)[0-9]{3}[0-9Xx]$'

## 体检用户管理列表 增删改查
class AccountModelForm(BootstrapModelForm):
    idnum = forms.CharField(
        label='身份证号',
        validators=[RegexValidator(IDNUM_REGEX , '请输入正确的身份证号码')],
        error_messages={'unique':'身份证号已存在。'}
    )

    class Meta:
        model = Account
        fields = ['idnum']

        
class UserModelForm(BootstrapModelForm):
    not_required_fields = ['phone','career','factor']

    gender_choice = ((0,'男'),(1,'女'))
    marriage_choice = ((0,'未婚'),(1,'已婚'))

    class Meta:
        model = User
        exclude = ['account']


class UserSearchForm(SearchForm):
    account__idnum = forms.CharField(label='身份证号')
    name = forms.CharField(label='姓名')
    phone = forms.CharField(label='手机号')
    dep = forms.CharField(label='科室')
    gender = forms.ChoiceField(choices=((None,'性别'),(0,'男'),(1,'女')))
    gender.widget.attrs['style'] = 'width: 90px;'


class UserListView(ListView):
    """用户列表"""
    Model = User
    template = 'user_list.html'
    SeForm = UserSearchForm
    AForm = AccountModelForm
    Form = UserModelForm
    search_args = [
        ['account__idnum','name','phone','dep'],
        ['gender']
    ]
    ordering_field = '-account_id'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request)
        context['a_form'] = self.AForm()
        return context

class UploadFileForm(forms.Form):
    '''上传人员名单表单'''
    file = forms.FileField(label='上传xls文件')
    name_col = forms.IntegerField(initial=1, label='姓名列')
    idnum_col = forms.IntegerField(initial=2, label='身份证号列')
    dep_col = forms.IntegerField(initial=3, label='科室列')
    phone_col = forms.IntegerField(required=False, label='手机号列')
    startfrom = forms.IntegerField(initial=1, min_value=1, label='从第几行开始')

def handle_upload_file(wb, form):
    '''处理上传文件'''
    errors = ''
    for table in wb.sheets():
        start_row_index = form.cleaned_data['startfrom'] - 1
        name_col_index = form.cleaned_data['name_col'] - 1
        idnum_col_index = form.cleaned_data['idnum_col'] - 1
        dep_col_index = form.cleaned_data['dep_col'] - 1
        phone_col_index = form.cleaned_data.get('phone_col')

        try:
            name_col = table.col_values(name_col_index)
            idnum_col = table.col_values(idnum_col_index)
            dep_col = table.col_values(dep_col_index)
            if phone_col_index:
                phone_col_index -= 1
                phone_col = table.col_values(phone_col_index)
            else:
                phone_col = None
        except:
            errors += f'{table.name} 内容错误。'
            return errors

        for i in range(start_row_index, len(name_col)):
            idnum = idnum_col[i]
            if not re.match(IDNUM_REGEX, idnum):
                errors += f'{table.name} 第{i+1}行 '+idnum+' 格式错误，已跳过<br>'
                continue
            password = idnum[-7:-1]

            new_acc = Account(idnum=idnum, pwd=password, atype=1)
            try:
                new_acc.save()
            except IntegrityError:
                errors += f'{table.name} 第{i+1}行 '+idnum+' 已存在该用户，已跳过<br>'
                continue

            args = {'account':new_acc}
            args['name'] = name_col[i]
            args['dep'] = dep_col[i]
            if phone_col:
                args['phone'] = phone_col[i]
            new_user = User(**args)
            new_user.save()

    return errors

def upload_page(request):
    '''上传页'''
    if request.method == 'GET':
        form = UploadFileForm()
        return render(request, 'users_upload.html', {'form':form})

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            list_f = form.cleaned_data['file']
            try:
                wb = xlrd.open_workbook(file_contents=list_f.read())
            except xlrd.XLRDError:
                form.add_error('file','文件类型错误。')
                return render(request, 'users_upload.html', {'form':form})
            
            errors = handle_upload_file(wb, form)    
            wb.release_resources()

            if errors:
                context = {
                    'form':form,
                    'err_str':mark_safe('文件内容存在错误，请重新检查<br>'+errors)
                }
                return render(request, 'users_upload.html', context)
            else:
                return redirect('/user/list/')
            
        else: return render(request, 'users_upload.html', {'form':form})


class AddUserView(AddView):
    Form = UserModelForm
    AForm = AccountModelForm
    acc_type = 1

    def get_form(self, request):
        a_form = self.AForm(data=request.POST)
        return a_form, super().get_form(request)
    
    def set_pwd(self, idnum):
        return idnum[-7:-1]

    def post(self, request):
        a_form, u_form = self.get_form(request)
        if a_form.is_valid() and u_form.is_valid():
            idnum = a_form.instance.idnum
            a_form.instance.pwd = self.set_pwd(idnum)
            a_form.instance.atype = self.acc_type

            u_form.instance.account = a_form.instance

            a_form.save()
            u_form.save()
            
            return JsonResponse( {'status':True} )
        return JsonResponse( {'status':False, 'a_err':a_form.errors, 'u_err':u_form.errors} )


class EditUserView(EditView):
    Form = UserModelForm
    AForm = AccountModelForm
    Model = User
    id_field = 'uid'
    model_field = 'account_id'

    def get_edit_obj(self, request):
        user_obj = super().get_edit_obj(request)
        acc_obj = user_obj.account
        return acc_obj, user_obj

    def get_form(self, request):
        acc_obj, user_obj = self.get_edit_obj(request)
        a_form = self.AForm(data=request.POST, instance=acc_obj)
        u_form = self.Form(data=request.POST, instance=user_obj)
        return a_form, u_form

    def post(self, request):
        a_form, u_form = self.get_form(request)
        if a_form.is_valid() and u_form.is_valid():
            a_form.save()
            u_form.save()
            return JsonResponse( {'status':True} )
        return JsonResponse( {'status':False, 'a_err':a_form.errors, 'u_err':u_form.errors} )


class GetUserDetail(DetailView):
    Model = User
    id_field = 'uid'
    model_field = 'account_id'
    value_fields = ['account__idnum','name',
                    'dep','phone','gender',
                    'marriage','career','factor']

    def get_dict(self, request):
        obj_dict = super().get_dict(request)
        if obj_dict:
            obj_dict['idnum'] = obj_dict.pop('account__idnum')

        return obj_dict


@csrf_exempt
def reset_pwd(request):
    '''重置密码'''
    uid = request.POST.get('uid')
    acc_obj = Account.objects.filter(uid=uid).first()

    if acc_obj:
        acc_obj.pwd = acc_obj.idnum[-7:-1]
        acc_obj.save()
        return JsonResponse({'status':True})
    return JsonResponse({'status':False,'error':'未找到该用户'})




## 体检用户个人主页
def user_pg(request, uid):
    if uid != request.session['info']['uid']:
        raise Exception('没有权限访问。')

    user_obj = User.objects.filter(account_id=uid).first()

    if not user_obj:
        raise Exception('未找到该用户。')
    
    # 要通知未完成且在未来的事件
    upcoming_ue_set = user_obj.userevent_set.filter(status=0, event__status=1)
    # 最近的5条已完成事件
    past_ue_set = user_obj.userevent_set.filter(status=1)
    past_ue_set = past_ue_set.order_by('-event__time')[:5]

    context = {
        'user':user_obj,
        'upcoming_ue_set':upcoming_ue_set,
        'past_ue_set':past_ue_set
    }
    return render(request, 'user_index.html', context)


class UserInfoEdit(View):
    "修改个人信息"
    template = 'user_infoedit.html'
    Model = User
    Form = UserModelForm

    def get_forms(self, uid, data=None):
        user_obj = self.Model.objects.filter(account_id=uid).first()
        if not user_obj:
            raise Exception('未找到该用户。')
        user_form = self.Form(instance=user_obj, data=data)

        return user_obj, user_form

    def get(self, request, uid):
        user_obj, user_form = self.get_forms(uid)

        return render(request, self.template, {'user':user_obj, 'u_form': user_form})
    
    def post(self, request, uid):
        user_obj, user_form = self.get_forms(uid, data=request.POST)
        if user_form.is_valid():
            user_form.save()
            if 'name' in user_form.changed_data:
                info = request.session['info']
                info['user_name'] = user_form.cleaned_data['name']
                request.session['info'] = info
            return redirect('../')
        else:
            return render(request, self.template, {'user':user_obj, 'u_form': user_form})
         

class UserEventSearchForm(SearchForm):
    event__time__year = forms.CharField(max_length=4, label='输入年份...')

class UserEventList(ListView):
    template = 'user_uelist.html'
    SeForm = UserEventSearchForm
    search_kwargs = {'str_field_list':['event__time__year']}
    ordering_field = '-event__time'

    def get_model(self, request, *args, **kwargs):
        uid = kwargs['uid']
        user_obj = User.objects.filter(account_id=uid).first()
        if not user_obj:
            return 0
        
        ue_set = user_obj.userevent_set.filter(status=1)
        return ue_set