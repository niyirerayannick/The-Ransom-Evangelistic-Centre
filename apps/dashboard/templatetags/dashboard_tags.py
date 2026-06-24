from django import template
from django.utils.formats import date_format

register = template.Library()


@register.inclusion_tag("dashboard/partials/icon.html")
def dash_icon(name, size_class="text-[20px]", filled=False, title=""):
    return {"name": name, "size_class": size_class, "filled": filled, "title": title}


@register.filter
def can_delete_post(user, post):
    return user.can_delete_post(post)


@register.simple_tag
def can_write_module(user, module_key):
    from apps.dashboard.roles import user_can_write_module
    return user_can_write_module(user, module_key)


@register.filter
def get_field(obj, field_name):
    value = getattr(obj, field_name, None)
    if value is None:
        return "—"
    if hasattr(value, "strftime"):
        try:
            return date_format(value, "M j, Y H:i")
        except (ValueError, TypeError):
            return str(value)
    if isinstance(value, bool):
        return value
    return value
