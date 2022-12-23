from django.template import Library

register = Library()


@register.simple_tag
def edit_query(request, **kwargs):
    qd = request.GET.copy()
    for key, value in kwargs.items():
        qd[key] = value
    querystring = qd.urlencode()
    return querystring