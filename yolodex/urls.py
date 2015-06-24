from django.conf.urls import patterns, url

from .views import (
    RealmView,
    EntitySearchView,
    EntityListView,
    EntityDetailView,
    EntityDetailNetworkEmbedView,
)
from .api_views import (
    YolodexRouter,
    EntityViewSet,
    EntityTypeViewSet
)

router = YolodexRouter()
router.register(r'api/entity', EntityViewSet, 'entity')
router.register(r'api/entitytype', EntityTypeViewSet, 'entitytype')

entity_urls = [
    url(r'^$', RealmView.as_view(), name='overview'),
    url(r'^search/$', EntitySearchView.as_view(), name='search'),
    url(r'^(?P<type>[\w-]+)/$',
        EntityListView.as_view(),
        name='entity_list'),
    url(r'^(?P<type>[\w-]+)/(?P<slug>[\w-]+)/$',
        EntityDetailView.as_view(),
        name='entity_detail'),
    url(r'^(?P<type>[\w-]+)/(?P<slug>[\w-]+)/embed/$',
        EntityDetailNetworkEmbedView.as_view(),
        name='entity_detail_embed'),
]

urlpatterns = router.urls

urlpatterns += patterns('', *entity_urls)
