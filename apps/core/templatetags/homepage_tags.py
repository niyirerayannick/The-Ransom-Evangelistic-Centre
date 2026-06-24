from django import template

register = template.Library()


@register.filter
def section_field(section, field_name):
    if not section:
        return ""
    return section.field_for_language(field_name)


@register.filter
def section_heading(section):
    if not section:
        return ""
    return section.heading_for_language()
