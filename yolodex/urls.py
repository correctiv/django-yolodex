from django.conf.urls import patterns, url, include
from django.utils.translation import ugettext as _

from .views import (
    RealmView,
    EntityDetailView,
    EntityNetworkView,
)

entity_urls = [
    url(r'^$', RealmView.as_view(), name='overview'),
    url(r'^(?P<type>[\w-]+)/(?P<slug>[\w-]+)/$',
        EntityDetailView.as_view(),
        name='entity_detail'),
    url(r'^(?P<type>[\w-]+)/(?P<slug>[\w-]+)/graph\.json$',
        EntityNetworkView.as_view(),
        name='entity_graph_json'),
]

urlpatterns = patterns('', *entity_urls)
