from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.clickjacking import xframe_options_exempt

from .views import (
    RealmView,
    RealmCorrectionsView,
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
    url(_(r'^corrections/$'), RealmCorrectionsView.as_view(), name='corrections'),
    url(_(r'^search/$'), EntitySearchView.as_view(), name='search'),
    url(r'^(?P<type>[\w-]+)/$',
        EntityListView.as_view(),
        name='entity_list'),
    url(r'^(?P<type>[\w-]+)/(?P<slug>[\w-]+)/$',
        EntityDetailView.as_view(),
        name='entity_detail'),
    url(r'^(?P<type>[\w-]+)/(?P<slug>[\w-]+)/embed/$',
        xframe_options_exempt(EntityDetailNetworkEmbedView.as_view()),
        name='entity_detail_embed'),
]

urlpatterns = router.urls

urlpatterns += entity_urls
