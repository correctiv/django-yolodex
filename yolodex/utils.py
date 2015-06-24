from django.core.urlresolvers import resolve


def get_current_app(request):
    return resolve(request.path).namespace
