from django import template
import re
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter()
def yellow(text, value):
    if text is not None:
        text = str(text)
        src_str = re.compile(value)
        str_replaced = src_str.sub(f'<span class="yellow">{value}</span>', text)
    else:
        str_replaced = ""

    return mark_safe(str_replaced)
