from django.http import JsonResponse
from django import forms
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db.utils import IntegrityError

from ..models import Account, Event, User, Item, Record, UserEvent, ItemType, Diagnose
from ..util import deserializer, BootstrapForm
from ..abstractviews import ListView

'''
体检结果录入\查询相关视图
'''

def rec_input(request):
    "体检结果录入页"
    eid, uid = request.GET.get('eid'), request.GET.get('uid')
    context = {'user':None}

    # 如果没有选择事件,则提供选择列表
    if not eid:
        events = Event.objects.filter(status=1).order_by('-time')
        context['events'] = events
    else: # 选择后可以选择该事件安排的用户
        event_obj = Event.objects.filter(eid=eid, status=1).first()
        if not event_obj:
            raise Exception('数据库中没有该体检事件，或事件处于不可录入数据的状态。')
        ue_set = event_obj.userevent_set.filter(status=0).order_by('user_id') #只能录入未完成的
        context['event'] = event_obj #选择的事件
        context['info_set'] = ue_set #事件关联的用户
    
    if uid and eid:
        user_obj = User.objects.filter(account_id=uid).first()
        if not user_obj:
            raise Exception('未找到该用户。')
        context['user'] = user_obj #选择的用户

        types = ItemType.objects.all()
        context['types'] = types #体检项目,按体检类别分

        diags = Diagnose.objects.all()
        context['diags'] = diags
    
    return render(request, 'rec_input.html', context)


@csrf_exempt
def get_uid(request):
    "ajax 用idnum获取用户uid"
    idnum = request.POST.get('idnum')
    acc_obj = Account.objects.filter(idnum=idnum).first()

    if acc_obj:
        uid = acc_obj.uid
        return JsonResponse({'status':True, 'uid':uid})
    else:
        return JsonResponse({'status':False, 'error':'未找到该用户'})
    

@csrf_exempt
def get_rec(request):
    "ajax"
    eid, uid = request.GET.get('eid'), request.GET.get('uid')
    if eid and uid:
        ue = UserEvent.objects.filter(event_id=eid, user_id=uid).first()
        rec_dicts = ue.record_set.values('item_id','rec').all()
        rec_dicts = list(rec_dicts)
        return JsonResponse({'status':True, 'data':rec_dicts})
    return JsonResponse({'status':False})

@csrf_exempt
def rec_submit(request):
    "提交体检结果录入"
    uid, eid = request.POST.get('uid'), request.POST.get('eid')
    if uid and eid:
        rec_dict = deserializer(request.POST.get('info'))
    else:
        return JsonResponse({'status':False, 'error':'提交失败，参数错误'})

    event_obj = Event.objects.filter(eid=eid).first()
    userevent_set = event_obj.userevent_set
    user_exist = userevent_set.filter(user_id=uid).exists()

    if user_exist:
        is_new = False
        ue_obj = userevent_set.filter(user_id=uid).first()
    else:
        is_new = True
        ue_obj = UserEvent(
            user = User.objects.filter(account_id=uid).first(),
            event = event_obj
        )
        ue_obj.save()

    # 先清空再录入（以最新为准）
    Record.objects.filter(userevent=ue_obj).delete()
    for id, rec in rec_dict.items():
        id = int(id)
        item_obj = Item.objects.filter(item_id=id).first()

        # 数值型结果判断异常值
        sign = 1
        if item_obj.cate == 0:
            rec_value = eval(rec)
            if item_obj.low_lmt and rec_value<item_obj.low_lmt:
                sign = 0
            if item_obj.high_lmt and rec_value>item_obj.high_lmt:
                sign = 2

        new_record = Record(
            userevent = ue_obj,
            item = item_obj,
            rec = rec,
            sign = sign
        )
        new_record.save()
    ue_obj.save()
    return JsonResponse({'status':True, 'new':is_new})


def rec_review(request):
    "结果审核页"
    eid, uid = request.GET.get('eid'), request.GET.get('uid')
    context = {'user':None}

    if not eid:
        events = Event.objects.filter(status=1).order_by('-time')
        context['events'] = events
    else:
        event_obj = Event.objects.filter(eid=eid, status=1).first()
        if not event_obj:
            raise Exception('数据库中没有该体检事件，或事件处于不可录入数据的状态。')
        ue_set = event_obj.userevent_set.filter(status=0).order_by('user_id')
        context['event'] = event_obj
        context['info_set'] = ue_set
    
    if uid and eid:
        ue_obj = UserEvent.objects.filter(user_id=uid, event_id=eid).first()
        if not ue_obj:
            raise Exception('未找到该用户。')
        context['user'] = ue_obj.user
        context['is_complete'] = ue_obj.status

        rec_set = ue_obj.record_set.all().order_by('item__itype_id','item_id')
        context['rec_set'] = rec_set
    return render(request, 'rec_review.html', context)


@csrf_exempt
def rec_review_submit(request):
    "提交结果审核"
    uid, eid = request.POST.get('uid'), request.POST.get('eid')
    if uid and eid:
        data = deserializer(request.POST.get('info'))
    else:
        return JsonResponse({'status':False, 'error':'提交失败，参数错误'})

    try:
        ue_obj = UserEvent.objects.filter(user_id=uid, event_id=eid).first()
        if data:
            ue_obj.review = data['review']
        ue_obj.status = 1
        ue_obj.staff_id = request.session['info']['uid']
        ue_obj.save()

        return JsonResponse({'status':True})
    except IntegrityError:
        return JsonResponse({'status':False,'error':'您不是医务人员，无法提交。'})


def record(request):
    "结果查询页"
    uid, eid, eid2 = request.GET.get('uid'), request.GET.get('eid'), request.GET.get('eid2')
    context = {'compare':False}

    if not uid:
        raise Exception('缺少参数uid。')
    if request.session['atype'] == 1 and request.session['info']['uid'] != int(uid):
        raise Exception('没有权限访问。')
    
    user_obj = User.objects.filter(account_id=uid).first()
    if not user_obj:
        raise Exception('未找到该用户。')
    ue_set = user_obj.userevent_set.filter(status=1)

    context['user'] = user_obj
    context['ue_set'] = ue_set

    if eid:
        ue_obj = user_obj.userevent_set.filter(event_id=eid).first()
        if not ue_obj:
            raise Exception('未找到该事件。')
        rec_set = ue_obj.record_set.all().order_by('item__itype_id','item_id')

        context['ue'] = ue_obj
        context['rec_set'] = rec_set

    if eid and eid2:
        ue_obj2 = user_obj.userevent_set.filter(event_id=eid2).first()
        if not ue_obj2:
            raise Exception('未找到该事件。')
        rec_set2 = ue_obj2.record_set.values('item_id','rec','sign').all()
        item_ids = rec_set.values_list('item_id', flat=True)
        
        rec_dict2 = {ele['item_id']:[ele['rec'],ele['sign']] for ele in rec_set2}

        context['ue2'] = ue_obj2
        context['rec_set2'] = rec_dict2
        context['compare'] = True

    return render(request, 'record.html', context)


class ItypeForm(BootstrapForm):
    tid = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['tid'].widget.choices = ItemType.objects.all().values_list('id','name').order_by('index')

class RecordByItem(ListView):
    template = 'record_byitem.html'
    Form = ItypeForm
    ordering_field = '-event__time'

    def get_model(self, request, *args, **kwargs):
        uid, tid = request.GET.get('uid'), request.GET.get('tid')
        if not uid:
            raise Exception('缺少参数。')
        user_obj = User.objects.filter(account_id=uid).first()
        self.__setattr__('user_obj', user_obj)
        if not tid:
            self.__setattr__('hasitype',False)
            return user_obj.userevent_set.none()
        else:
            self.__setattr__('hasitype',True)
            itype_obj = ItemType.objects.get(pk=tid)
            self.__setattr__('itype_obj', itype_obj)
        
        return user_obj.userevent_set.filter(status=1)
        
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['form'] = self.Form(data=request.GET)
        context['user'] = self.user_obj
        if self.hasitype:
            context['itype'] = self.itype_obj

        return context
