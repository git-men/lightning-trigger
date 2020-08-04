from api_basebone.core.admin import BSMAdmin, register
from trigger_core.models import Trigger

@register
class GroupAdmin(BSMAdmin):
    display = ['name', 'event', 'enable', 'description']
    modal_form = False
    inline_actions = ['edit', 'delete']

    class Meta:
        model = Trigger
