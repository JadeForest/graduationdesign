from django.http import JsonResponse
from django.shortcuts import render, redirect
from django import forms
from django.views.decorators.csrf import csrf_exempt

from ..models import Event, User, UserEvent, Item
from ..util import BootstrapModelForm, SearchForm, CsrfExemptView
from .user import UserListView
from ..abstractviews import ListView, AddView, EditView, DetailView, DelView

from datetime import datetime
import pytz

'''
体检事件与体检人员安排视图
'''

class EventModelForm(BootstrapModelForm):
    "体检事件表单"
    not_required_fields = ['desc']

    class Meta:
        model = Event
        exclude = ['event_id','status']

class EventSearchForm(SearchForm):
    "体检事件搜索"
    time__gt = forms.DateField(label='开始日期')
    time__lt = forms.DateField(label='结束日期')
    status = forms.ChoiceField(choices=((None,'状态'),(0,'可编辑'),(1,'已锁定'),(2,'已存档')))
    status.widget.attrs['style'] = 'width: 90px;'

class EventListView(ListView):
    "体检时间安排页"
    Model = Event
    template = 'event_list.html'
    SeForm = EventSearchForm
    Form = EventModelForm
    search_kwargs = {
        'filter_field_list':['status'],
        'str_field_list':['time__gt','time__lt']
    }
    ordering_field = '-time'
    per_page = 10


class AddEventView(AddView):
    "增"
    Form = EventModelForm

    def get_form(self, request):
        form = super().get_form(request)
        # 时间不能早于当前
        new_time = datetime.strptime(request.POST['time'], '%Y-%m-%d %H:%M')
        new_time = pytz.UTC.localize(new_time)
        if new_time < datetime.now(tz=pytz.UTC):
            form.add_error('time','安排时间必须晚于当前时间。')
        return form

class EditEventView(EditView):
    "改"
    Form = EventModelForm
    Model = Event
    id_field = 'eid'
    model_field = 'eid'

    def get_form(self, request):
        form = super().get_form(request)
        # 时间不能变早
        new_time = datetime.strptime(request.POST['time'], '%Y-%m-%d %H:%M')
        new_time = pytz.UTC.localize(new_time)
        if new_time < form.instance.time:
            form.add_error('time','调整后时间必须晚于原时间。')
        return form

class EventDetail(DetailView):
    "查"
    Model = Event
    id_field = 'eid'
    model_field = 'eid'
    value_fields = ['time','desc']

    def get_dict(self, request):
        valuedict = super().get_dict(request)
        #格式化时间
        valuedict['time'] = datetime.strftime(valuedict['time'], '%Y-%m-%d %H:%M') 
        return valuedict

class DelEventView(DelView):
    "删"
    Model = Event
    id_field = 'eid'
    model_field = 'eid'


@csrf_exempt
def lock_event(request):
    "Ajax 锁定体检事件编辑"
    eid = request.POST.get('eid')
    event_obj = Event.objects.filter(eid=eid).first()

    if not event_obj:
        return JsonResponse({'status':False, 'error':'数据库中没有该数据。'})
    
    event_obj.status = 1
    event_obj.save()

    return JsonResponse({'status':True})


@csrf_exempt
def archive_event(request):
    "ajax 存档体检事件"
    eid = request.POST.get('eid')
    event_obj = Event.objects.filter(eid=eid).first()
    if event_obj:
        # 删除未完成体检的用户   
        ue_set = event_obj.userevent_set.all()
        ue_set.filter(status=0).delete()
        event_obj.status = 2
        event_obj.save()
        return JsonResponse({'status':True})
    return JsonResponse({'status':False})


class UserSearchForm(SearchForm):
    "用户搜索表"
    user__account__idnum = forms.CharField(label='身份证号')
    user__name = forms.CharField(label='姓名')
    status = forms.ChoiceField(choices=((None,'状态'),(0,'未完成'),(1,'已完成')))
    status.widget.attrs['style'] = 'width: 90px;'


class ArrListView(ListView):
    '''已安排人员列表'''
    template = 'arr_list.html'
    SeForm = UserSearchForm
    search_args = [['user__name','user__account__idnum'],['status']]
    ordering_field = '-id'

    def get_model(self, request, *args, **kwargs):
        eid = kwargs['eid']
        event_obj = Event.objects.filter(eid=eid).first()
        if not event_obj:
            raise Exception('未找到该项目。')
        self.__setattr__('event_obj',event_obj)
        return event_obj.userevent_set
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['event'] = self.event_obj
        return context


class ArrChooseView(UserListView):
    "人员详细安排 继承用户列表视图"
    template = 'arr_choose.html'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        # 加入当前事件信息
        eid = kwargs['eid']
        event_obj = Event.objects.filter(eid=eid).first()
        context['event'] = event_obj

        return context
    

class ArrChooseAll(UserListView, CsrfExemptView):
    ordering_field = ''
    
    def post(self, request, *args, **kwargs):
        meth = request.POST.get('method')
        if 'SELECT' == meth:
            queryset = self.get_queryset(request, *args, **kwargs)
            uid_set = queryset.values_list('account_id', flat=True)
            uid_list = [str(uid) for uid in uid_set]
        
            if uid_list:
                uid_str = ','.join(uid_list)
                return JsonResponse({'status':True, 'hasValue':True ,'data':uid_str})
            else:
                return JsonResponse({'status':True, 'hasValue':False})
        return JsonResponse({'status':False})

@csrf_exempt
def arr_choose_getexist(request, eid):
    "Ajax 查找已选的用户uid"
    event_obj = Event.objects.filter(eid=eid).first()
    exist_set = [str(uid) for uid in event_obj.userevent_set.values_list('user_id', flat=True).all()]
    if exist_set:
        exist_str = ','.join(exist_set)
        return JsonResponse({'status':True, 'data':exist_str})
    else:
        return JsonResponse({'status':False})

@csrf_exempt
def arr_choose_confirm(request, eid):
    "Ajax 确定安排"
    # 先清空 再更新
    event_obj = Event.objects.filter(eid=eid).first()
    event_obj.userevent_set.all().delete()

    ulist = request.POST.get('ulist').split(',')
    if ulist[0] != '':
        try:
            create_list = [UserEvent(user_id=int(uid), event=event_obj) for uid in ulist]
        except ValueError:
            return JsonResponse({'status':True, 'error':'uid参数存在错误。'}) 

        UserEvent.objects.bulk_create(create_list)
    else: pass

    return JsonResponse({'status':True}) 
   

class RecTableView(ListView):
    template = 'record_table.html'
    per_page = 20

    def get_model(self, request, *args, **kwargs):
        eid = kwargs['eid']
        event_obj = Event.objects.filter(pk=eid).first()
        if not event_obj:
            raise Exception('没有此结果。')
        self.__setattr__('event_obj', event_obj)
        
        return event_obj.userevent_set.filter(status=1)
        
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['event'] = self.event_obj
        context['items'] = Item.objects.all().order_by('itype__index')
        return context
    

# def arr_choose_group(request, eid):
#     "按组安排"
#     if request.method == 'GET':
#         dep_list = User.objects.values_list('dep',flat=True).distinct()
#         return render(request, 'arr_choose_group.html', {'dep_list':dep_list})
    
#     if request.method == 'POST':
#         dep = request.POST.get('dep')

#         event_obj = Event.objects.filter(eid=eid).first()

#         u_set = User.objects.filter(dep=dep)
#         for user in u_set:
#             if user.account_id in event_obj.userevent_set.values_list('user_id', flat=True).all():
#                 continue
#             new_ue = UserEvent(user=user, event=event_obj)
#             new_ue.save()
#         return redirect('../')