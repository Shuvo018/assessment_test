from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Allow dict[key] lookups in templates: {{ my_dict|get_item:variable }}"""
    return dictionary.get(str(key))