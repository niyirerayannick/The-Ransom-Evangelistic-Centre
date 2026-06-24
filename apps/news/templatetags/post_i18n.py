from django import template
from django.utils.translation import get_language

register = template.Library()


@register.simple_tag(takes_context=True)
def post_display_title(context, post):
    language = context.get("current_language") or get_language() or "en"
    return post.title_for_language(language, fallback=False)


@register.simple_tag(takes_context=True)
def post_display_excerpt(context, post):
    language = context.get("current_language") or get_language() or "en"
    return post.excerpt_for_language(language, fallback=False)


@register.simple_tag(takes_context=True)
def post_localized(context, post, field_name):
    language = context.get("preview_lang") or context.get("current_language") or get_language() or "en"
    return post.field_for_language(field_name, language, fallback=False)


@register.simple_tag(takes_context=True)
def post_using_fallback(context, post, field_name):
    return False


@register.simple_tag(takes_context=True)
def post_missing_translation_warning(context, post):
    return False
