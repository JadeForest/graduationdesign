from django import forms
from django.core.exceptions import ValidationError

from ..models import Item, ItemType, Diagnose
from ..util import BootstrapModelForm, SearchForm
from ..abstractviews import ListView, AddView, EditView, DetailView, DelView

'''
体检项目\类别相关视图
'''

## 体检项目 列表 增删改查
class ItemModelForm(BootstrapModelForm):
    "体检项目表单 包含字段验证"
    not_required_fields = ['ref','low_lmt','high_lmt','unit']

    class Meta:
        model = Item
        exclude = ['item_id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['ref'].label += '（非数值型）'
        self.fields['high_lmt'].label += '（数值型）'
        self.fields['low_lmt'].label += '（数值型）'
        self.fields['unit'].label += '（数值型）'

    def clean_ref(self):
        input = self.cleaned_data['ref']
        cate = self.cleaned_data['cate']

        if cate == 1 and input is None:
            raise ValidationError('请填写参考值。')
        if cate == 0 and input is not None:
            raise ValidationError('数值型项目不能填写此字段。')
        return input
        
    def clean_high_lmt(self):
        input = self.cleaned_data['high_lmt']
        cate = self.cleaned_data['cate']

        if cate == 1 and input is not None:
            raise ValidationError('非数值型项目不能填写此字段。')
        return input
        
    def clean_low_lmt(self):
        input = self.cleaned_data['low_lmt']
        cate = self.cleaned_data['cate']

        if cate == 1 and input:
            raise ValidationError('非数值型项目不能填写此字段。')
        return input

    def clean_unit(self):
        input = self.cleaned_data['unit']
        cate = self.cleaned_data['cate']

        if cate == 0 and input == '':
            raise ValidationError('请填写单位。')
        if cate == 1 and input != '':
            raise ValidationError('非数值型项目不能填写此字段。')
        return input 

class ItemSearchForm(SearchForm):
    "搜索"
    item = forms.CharField(label='搜索名称...')

class ItemListView(ListView):
    "体检项目列表页"
    Model = Item
    template = 'item_list.html'
    SeForm = ItemSearchForm
    Form = ItemModelForm
    search_args = [['item'], ['itype']]
    ordering_field = 'item_id'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request)
        context['itype_form'] = ItemModelForm(data=request.GET)
        return context


class AddItemView(AddView):
    Form = ItemModelForm

class EditItemView(EditView):
    Form = ItemModelForm
    Model = Item
    id_field = 'item_id'

class ItemDetail(DetailView):
    Model = Item
    id_field = 'item_id'
    value_fields = ['item','itype','unit','ref','low_lmt','high_lmt','cate']

class DelItemView(DelView):
    Model = Item
    id_field = 'item_id'

    

## 体检类别 列表 增删改查
class ItemTypeModelForm(BootstrapModelForm):
    class Meta:
        model = ItemType
        exclude = ['id']

class ItemTypeSearchForm(SearchForm):
    name = forms.CharField(label='搜索名称...')

class ItypeListView(ListView):
    Model = ItemType
    template = 'itype_list.html'
    SeForm = ItemTypeSearchForm
    Form = ItemTypeModelForm
    search_args = [['name']]
    ordering_field = 'index'


class AddItypeView(AddView):
    Form = ItemTypeModelForm

class EditItypeView(EditView):
    Form = ItemTypeModelForm
    Model = ItemType
    id_field = 'id'

class ItypeDetail(DetailView):
    Model = ItemType
    id_field = 'id'
    value_fields = ['name','index']

class DelItypeView(DelView):
    Model = ItemType
    id_field = 'id'



## 诊断结果 列表 增删改查
class DiagModelForm(BootstrapModelForm):
    class Meta:
        model = Diagnose
        exclude = ['id']

class DiagSearchForm(SearchForm):
    value = forms.CharField(label='搜索...')

class DiagListView(ListView):
    Model = Diagnose
    template = 'diag_list.html'
    SeForm = DiagSearchForm
    Form = DiagModelForm
    search_args = [['value']]
    ordering_field = 'id'
    per_page = 20


class AddDiagView(AddView):
    Form = DiagModelForm

class EditDiagView(EditView):
    Form = DiagModelForm
    Model = Diagnose
    id_field = 'id'

class DiagDetail(DetailView):
    Model = Diagnose
    id_field = 'id'
    value_fields = ['value']

class DelDiagView(DelView):
    Model = Diagnose
    id_field = 'id'