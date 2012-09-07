from django import template

register = template.Library()


@register.filter
def get(form, field_name):
    return form[field_name]


@register.filter
def is_hidden(form, field_name):
    return form[field_name].is_hidden
