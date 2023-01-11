from django import template
from math import ceil, floor

register = template.Library()



@register.inclusion_tag('includes/stars.html')
def stars(value):
    value = float(value)
    full = floor(value)
    half = ceil(value - full)
    empty = 5 - (full + half)
    return {
        'full': range(full),
        'half': range(half),
        'empty': range(empty)
    }
    
@register.simple_tag
def price_text(request, price):
    currency = request.session.setdefault('currency', 'AZN')
    currency_ratio = request.session.setdefault('currency_ratio', 1)
    result_price = round(price * currency_ratio, 2)
    return '%s %s' % (result_price, currency)