from collections import namedtuple

from django.contrib.sitemaps import Sitemap
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse

from .models import Realm, Entity, EntityType
from .views import EntityListView


SitemapLocation = namedtuple('SitemapLocation', 'name, kwargs, query_params, current_app, lastmod')


def update_sitemap(sitemap_dict):
    sitemap_dict.update({
        'yolodex': YolodexSitemap
    })
    return sitemap_dict


class YolodexSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def _items(self):
        """
        Return published entries.
        """
        for realm in Realm.published.all():
            lastmod = realm.updated_on or realm.created_on
            for entity in Entity.objects.filter(realm=realm).select_related('type'):
                yield SitemapLocation('yolodex:entity_detail', {
                    'type': entity.type.slug,
                    'slug': entity.slug
                }, '', realm.slug, lastmod)
            for entity_type in EntityType.objects.filter(realms=realm):
                objects = Entity.objects.filter(type=entity_type)
                paginator = Paginator(objects, EntityListView.paginate_by)
                for page in paginator.page_range:
                    p = '?page=%s' % page if page > 1 else ''
                    yield SitemapLocation('yolodex:entity_list', {
                        'type': entity_type.slug,
                    }, p, realm.slug, lastmod)

    def items(self):
        return list(self._items())

    def location(self, obj):
        url = reverse(obj.name, kwargs=obj.kwargs, current_app=obj.current_app)
        if obj.query_params:
            url += obj.query_params
        return url

    def lastmod(self, obj):
        return obj.lastmod
