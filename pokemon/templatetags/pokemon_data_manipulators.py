import re

from django import template

register = template.Library()


@register.filter
def split(value, arg):
    return re.split(arg, value)


@register.filter
def split_cap(value):
    return ' '.join([term.capitalize() for term in re.split('[ _-]', value) if term])


@register.filter
def float_to_percent(value):
    return str(int(value*100)) + '%'


@register.filter
def mid_slash(value):
    split = value.split()
    if len(split) % 2 != 0:
        return
    return ' '.join(
        split[:int(len(split)/2)]
    ) + '/' + ' '.join(
        split[int(len(split)/2):]
    )

@register.filter
def convert_if_none(value, arg):
    return value or arg


@register.filter
def contains_learn_method(moves, arg):
    for move in moves:
        if move['learn_method']['name'] == arg:
            return True
    return False


@register.filter
def get_key(value, arg):
    return value.get(arg)


@register.filter
def find_matching_name(value, arg):
    for item in value:
        if item['name'] == arg:
            return item
    return None
