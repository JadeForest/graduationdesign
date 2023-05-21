from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django import forms
from django.core.exceptions import ValidationError
from django.views import View

from ..models import Account
from ..util import BootstrapForm
from ..abstractviews import DelView

'''
账户相关视图
'''

class LoginForm(BootstrapForm):
    "登录表单"
    idnum = forms.CharField(label='身份证号/工号')
    pwd = forms.CharField(label='密码', widget=forms.PasswordInput)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['idnum'].widget.attrs['autofocus'] = True

def initial_admin():
    "测试用函数"
    exist = Account.objects.filter(idnum='A001').exists()
    if not exist:
        init_admin = Account(idnum='A001',pwd='0000',atype=0)
        init_admin.save()

class LoginView(View):
    '''登录与验证'''
    def get(self, request):
        initial_admin()

        form = LoginForm()
        return render(request, 'login.html', {'form':form})

    def login_valid(self, idnum, pwd, atype):
        '''验证与参数分配'''
        acc = Account.objects.filter(idnum=idnum, atype=atype).first()
        if not acc:
            return {'valid':False, 'err_field':'idnum', 'err':'不存在该用户'}
        if acc.pwd != pwd:
            return {'valid':False, 'err_field':'pwd', 'err':'密码错误'}
        if atype == 1:
            user = acc.user
            return {'valid':True, 'acc':acc, 'user':user, 'next':'/user/{}/'.format(acc.uid)}
        if atype == 2:
            staff = acc.staff
            return {'valid':True, 'acc':acc, 'user':staff, 'next':'/staff/{}/'.format(acc.uid)}
        if atype == 0:
            return {'valid':True, 'acc':acc, 'user':None, 'next':'/admin/'}
            

    def post(self, request):
        form = LoginForm(data=request.POST)
        atype = request.POST['atype']
        atype = int(atype) if atype.isdecimal() else 0

        if form.is_valid():
            idnum, pwd = form.cleaned_data['idnum'], form.cleaned_data['pwd'] 

            valid = self.login_valid(idnum, pwd, atype)

            if valid['valid']:
                # 正确
                acc, user = valid['acc'], valid['user']
                request.session['atype'] = atype
                request.session['info'] = {'uid':acc.uid, 'idnum':acc.idnum}
                if user:
                    request.session['info']['user_name'] = user.name
                return redirect(valid['next']) # 重定向至初始页面

            # 不正确
            form.add_error(valid['err_field'], valid['err'])
            return render(request, 'login.html', {'form':form})
        
        return render(request, 'login.html', {'form':form})


def logout(request):
    '''注销登录'''
    request.session.clear()
    return redirect('/login/')


 

class ChangePasswordForm(BootstrapForm):
    "密码修改表单"
    old_pwd = forms.CharField(label='原密码', widget=forms.PasswordInput)
    new_pwd = forms.CharField(label='新密码', widget=forms.PasswordInput)
    pwd_confirm = forms.CharField(label='确认密码', widget=forms.PasswordInput)

    def clean_pwd_confirm(self):
        value1 = self.cleaned_data['new_pwd']
        value2 = self.cleaned_data['pwd_confirm']

        if value1 != value2:
            raise ValidationError('两次输入不一致。')
        else:
            return value2

def changepwd(request, uid):
    "修改密码"
    acc_obj = Account.objects.filter(uid=uid).first()
    if not acc_obj:
        return HttpResponse('用户不存在')
    
    if request.method == 'GET':       
        pwd_form = ChangePasswordForm()
        return render(request, 'changepwd.html', {'pwd_form':pwd_form,'acc':acc_obj})
    
def changepwd_submit(request, uid):
    "修改密码提交"
    acc_obj = Account.objects.filter(uid=uid).first()
    pwd_form = ChangePasswordForm(data=request.POST)
    if pwd_form.is_valid():
        new_pwd = pwd_form.cleaned_data['new_pwd']
        acc_obj.pwd = new_pwd
        acc_obj.save()
        return JsonResponse({'status':True})
    else:
        old_pwd = pwd_form.cleaned_data.get('old_pwd')
        if old_pwd != acc_obj.pwd:
            pwd_form.add_error('old_pwd','密码错误')

        return JsonResponse({'status':False, 'error':pwd_form.errors})
    

class DelAccountView(DelView):
    "删除账户"
    Model = Account
    id_field = 'uid'
    model_field = 'uid'






def debug(request):
    "测试用"
    from .. import models

    a1=models.Account.objects.create( idnum='324012200001010321',pwd='123',atype=1)
    a2=models.Account.objects.create( idnum='324012200201010322',pwd='123',atype=1)
    a3=models.Account.objects.create( idnum='329012200801010323',pwd='123',atype=1)
    a4=models.Account.objects.create( idnum='324012200301010324',pwd='123',atype=1)
    a5=models.Account.objects.create( idnum='324012200101010325',pwd='123',atype=1)
    a6=models.Account.objects.create( idnum='356012196501010327',pwd='123',atype=1)
    a7=models.Account.objects.create( idnum='324012197701010326',pwd='123',atype=1)
    a8=models.Account.objects.create( idnum='324012198601010328',pwd='123',atype=1)
    a9=models.Account.objects.create( idnum='324012199601010329',pwd='123',atype=1)
    a10=models.Account.objects.create(idnum='341012199601010392',pwd='123',atype=1)
    a11=models.Account.objects.create(idnum='324012199601010369',pwd='123',atype=1)
    a12=models.Account.objects.create(idnum='324012199601010389',pwd='123',atype=1)
    a13=models.Account.objects.create(idnum='324012199601010334',pwd='123',atype=1)
    a14=models.Account.objects.create(idnum='324012199601010335',pwd='123',atype=1)
    a15=models.Account.objects.create(idnum='324012199601010336',pwd='123',atype=1)
    a16=models.Account.objects.create(idnum='324012199601010337',pwd='123',atype=1)
    
    a17=models.Account.objects.create(idnum='D010203',pwd='114514',atype=2)
    a18=models.Account.objects.create(idnum='D010213',pwd='114514',atype=2)
    a19=models.Account.objects.create(idnum='D010223',pwd='114514',atype=2)
    a20=models.Account.objects.create(idnum='D010233',pwd='114514',atype=2)
    a21=models.Account.objects.create(idnum='D010243',pwd='114514',atype=2)
    a22=models.Account.objects.create(idnum='D010253',pwd='114514',atype=2)
 

    models.User.objects.create(account=a1, name='张伟1',gender=0,marriage=0,dep='所属1',career='技术员',factor='一些因素。。。',phone='18500006600')
    models.User.objects.create(account=a2, name='张伟2',gender=0,marriage=0,dep='所属2',career='技术员',factor='一些因素。。。',phone='18500006600')
    models.User.objects.create(account=a3, name='张伟3',gender=0,marriage=1,dep='所属3',career='技术员',factor='一些因素。。。',phone='18500006600')
    models.User.objects.create(account=a4, name='张伟4',gender=0,marriage=0,dep='所属3',career='技术员',factor='一些因素。。。',phone='18500006600')
    models.User.objects.create(account=a5, name='张伟5',gender=0,marriage=1,dep='所属1',career='矿山',factor='一些因素。。。',phone='18500006600')
    models.User.objects.create(account=a6, name='张伟6',gender=0,marriage=0,dep='所属1',career='技术员',factor='一些因素。。。',phone='18500006600')
    models.User.objects.create(account=a7, name='张伟7',gender=0,marriage=1,dep='所属3',career='技术员',factor='一些因素。。。',phone='18500006600')
    models.User.objects.create(account=a8, name='张伟8',gender=0,marriage=0,dep='所属1',career='技术员',factor='一些因素。。。',phone='18500006600')
    models.User.objects.create(account=a9, name='张伟9',gender=0,marriage=0,dep='所属3',career='矿山',factor='一些因素。。。',phone='18500006600')
    models.User.objects.create(account=a10, name='张0伟',gender=1,marriage=0,dep='所属2',career='技术员',factor='一些因素。。。' ,phone='13901012323')
    models.User.objects.create(account=a11, name='张伟11',gender=0,marriage=0,dep='所属2',career='技术员',factor='一些因素。。。',phone='13901012323')
    models.User.objects.create(account=a12, name='张伟12',gender=0,marriage=0,dep='所属3',career='技术员',factor='一些因素。。。',phone='13901012323')
    models.User.objects.create(account=a13, name='张伟13',gender=0,marriage=0,dep='所属2',career='技术员',factor='一些因素。。。',phone='13901012323')
    models.User.objects.create(account=a14, name='王薇薇',gender=1,marriage=0,dep='所属1',career='技术员',factor='一些因素。。。',phone='13901012323')
    models.User.objects.create(account=a15, name='张伟',gender=1,marriage=1,dep='所属3',career='技术员',factor='一些因素。。。'  ,phone='13901012323')
    models.User.objects.create(account=a16, name='张伟',gender=0,marriage=0,dep='所属3',career='矿山',factor='一些因素。。。'  ,phone='13901012323')

    models.Staff.objects.create(account=a17, name='医生姓名1', gender=0, phone='12300001111')
    models.Staff.objects.create(account=a18, name='医生姓名2', gender=0, phone='12300001111')
    models.Staff.objects.create(account=a19, name='医生姓名3', gender=0, phone='12300001111')
    models.Staff.objects.create(account=a20, name='医生姓名4', gender=0, phone='12300001111')
    models.Staff.objects.create(account=a21, name='医生姓名5', gender=0, phone='12300001111')
    models.Staff.objects.create(account=a22, name='医生姓名6', gender=0, phone='12300001111')

    t1=models.ItemType.objects.create(index=0, name='常规/其它')
    t2=models.ItemType.objects.create(index=1, name='内科')
    t3=models.ItemType.objects.create(index=2, name='外科')
    t4=models.ItemType.objects.create(index=3, name='眼科')
    t5=models.ItemType.objects.create(index=4, name='尿常规')
    t6=models.ItemType.objects.create(index=5, name='肝功能')
    t7=models.ItemType.objects.create(index=6, name='血液分析')

    d1=models.Diagnose.objects.create(value='正常')
    d2=models.Diagnose.objects.create(value='异常')
    d3=models.Diagnose.objects.create(value='阳性')
    d4=models.Diagnose.objects.create(value='阴性')

    models.Item.objects.create(item='内科项目1',itype=t2,cate=0,low_lmt=1.0,high_lmt=7.8,unit='单位1')
    models.Item.objects.create(item='内科项目2',itype=t2,cate=1,ref=d1)
    models.Item.objects.create(item='视力-左',itype=t4,cate=0,low_lmt=2.0,unit='视力值')
    models.Item.objects.create(item='视力-右',itype=t4,cate=0,low_lmt=2.0,unit='视力值')
    models.Item.objects.create(item='血淋巴细胞染色体',itype=t7,cate=1,ref=d4)
    models.Item.objects.create(item='肝功能项目1',itype=t6,cate=0,low_lmt=6,high_lmt=18,unit='mol')
    models.Item.objects.create(item='肝功能项目2',itype=t6,cate=0,low_lmt=8.2,high_lmt=8.6,unit='pH')
    models.Item.objects.create(item='肝功能项目3',itype=t6,cate=1,ref=d4)
    models.Item.objects.create(item='肝功能项目4',itype=t6,cate=0,high_lmt=12,unit='miumil')
    
    print('初始化完毕')

    return render(request, 'layout.html')