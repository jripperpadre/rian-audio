# shop/templatetags/nav_extras.py
from django import template

register = template.Library()

@register.filter
def in_list(value, arg):
    """
    Usage: {% if request.resolver_match.url_name|in_list:"products,product_detail,category_products" %}
    """
    return value in arg.split(",")
