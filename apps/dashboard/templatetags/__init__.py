from django import template

register = template.Library()


@register.filter
def can_delete_post(user, post):
    return user.can_delete_post(post)
