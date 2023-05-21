from django import template
from datetime import datetime  
  
register = template.Library()  
  
@register.filter(name='getage')
def getage(idnum):
  if idnum:
    bir_year = int(idnum[6:10])
    curr_year = datetime.now().year
    return curr_year - bir_year
  return ''