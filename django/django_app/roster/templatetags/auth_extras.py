from django import template
from django.contrib.auth.models import Group

# custom template tag to check if user is a teamleader (or in the teamleader group)
# if user is in teamleader group then they see their team members toil summary.
register = template.Library()
@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists() 
