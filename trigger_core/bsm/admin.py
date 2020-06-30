from api_basebone.core.admin import BSMAdmin, register
from trigger_core.models import Trigger

@register
class GroupAdmin(BSMAdmin):
    display = ['name', 'event', 'disable', 'description']
    modal_form = False
    inline_actions = ['edit', 'delete']

    class Meta:
        model = Trigger
