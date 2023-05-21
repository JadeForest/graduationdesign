from django import template
from datetime import datetime  
from django.utils.safestring import mark_safe

register = template.Library()  
  
@register.filter(name='key')
def key(d,key_name):
  value = 0
  try:          
    value = d[key_name]      
  except KeyError:          
    value = 0      
  return value

@register.filter(name='myfilter')
def myfilter(record_set, item_set):
  ret_list = []
  for item in item_set.all():
    rec = record_set.filter(item__pk=item.item_id).values_list('rec','sign').first()
    if not rec:
      ret_list.append('')
    elif rec[1] == 0:
      ret_list.append(mark_safe(rec[0] + '  <span style="color:brown"><i class="glyphicon glyphicon-arrow-down"></i></span>'))
    elif rec[1] == 2:
      ret_list.append(mark_safe(rec[0] + '  <span style="color:brown"><i class="glyphicon glyphicon-arrow-up"></i></span>'))
    else:
      ret_list.append(rec[0])

  return ret_list
