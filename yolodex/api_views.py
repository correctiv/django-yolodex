from django.shortcuts import get_object_or_404
from django.core.cache import cache

from rest_framework import viewsets, serializers
from rest_framework.response import Response
from rest_framework.routers import (Route, DynamicDetailRoute, DynamicListRoute,
                                    SimpleRouter)
from rest_framework.decorators import detail_route, list_route

from .models import Realm, Entity, EntityType
from .network import make_network, undirected_comp
from .utils import get_current_app


def search(qs, query, filters=None):
    if query and len(query) > 2:
        qs = qs.filter(name__contains=query)
    else:
        qs = qs.none()
    return qs


class CustomReadOnlyRouter(SimpleRouter):
    """
    A router for read-only APIs, which doesn't use trailing slashes.
    """
    routes = [
        Route(
            url=r'^{prefix}/$',
            mapping={'get': 'list'},
            name='{basename}-list',
            initkwargs={}
        ),
        DynamicListRoute(
            url=r'^{prefix}/{methodnamehyphen}/$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
        Route(
            url=r'^{prefix}/{lookup}/$',
            mapping={'get': 'retrieve'},
            name='{basename}-detail',
            initkwargs={}
        ),
        DynamicDetailRoute(
            url=r'^{prefix}/{lookup}/{methodnamehyphen}/$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        )
    ]


class YolodexRouter(CustomReadOnlyRouter):
    pass


class EntitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Entity


class TypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = EntityType


class RealmApiMixin(object):
    permission_classes = ()
    authentication_classes = ()

    def get_realm(self, request):
        current_app = get_current_app(request)
        self.realm = get_object_or_404(Realm, slug=current_app)
        return self.realm


def make_cache_key(realm, obj, kind='entity'):
    return 'yolodex:api:{kind}:network:{realm}:{obj}'.format(
        kind=kind,
        realm=realm.pk,
        obj=obj.pk
    )


def clear_network_cache(realm, entities):
    types = set()
    cache_keys = set()
    for e in entities:
        types.add(e.type)
        cache_keys.add(make_cache_key(realm, e, kind='entity'))
    for t in types:
        cache_keys.add(make_cache_key(realm, t, kind='entitytype'))
    cache.delete_many(cache_keys)


class EntityViewSet(RealmApiMixin, viewsets.ReadOnlyModelViewSet):
    """
    A viewset that provides the standard actions
    """
    serializer_class = EntitySerializer

    def get_queryset(self):
        realm = self.get_realm(self.request)
        return Entity.objects.filter(realm=realm)

    @list_route()
    def search(self, request, **kwargs):
        query = request.query_params.get('q', '')
        qs = search(self.get_queryset(), query)
        return Response({
            'query': query,
            'results': EntitySerializer(qs, many=True).data
        })

    @detail_route()
    def network(self, request, **kwargs):
        """
        Returns a list of all the group names that the given
        user belongs to.
        """
        obj = self.get_object()
        realm = self.get_realm(request)

        cache_key = make_cache_key(realm, obj, kind='entity')

        network = cache.get(cache_key)
        if network is None:
            network = obj.get_network(level=2).to_dict(realm=realm)
            cache.set(cache_key, network, None)
        return Response(network)


class EntityTypeViewSet(RealmApiMixin, viewsets.ReadOnlyModelViewSet):
    """
    A viewset that provides the standard actions
    """
    serializer_class = EntitySerializer

    def get_queryset(self):
        realm = self.get_realm(self.request)
        return realm.entitytype_set.all()

    def make_entity_filter(self, obj):
        def entity_filter(entity, rels):
            connectedness = 0
            for r in rels:
                if undirected_comp(
                        lambda a, b: a == entity and b.type_id == obj.pk, r):
                    connectedness += 1
            return connectedness > 1
        return entity_filter

    @detail_route()
    def network(self, request, **kwargs):
        """
        Returns a list of all the group names that the given
        user belongs to.
        """
        obj = self.get_object()
        realm = self.get_realm(request)

        cache_key = make_cache_key(realm, obj, kind='entitytype')

        network = cache.get(cache_key)
        if network is None:
            qs = Entity.objects.filter(realm=realm, type=obj)
            entity_filter = self.make_entity_filter(obj)
            network = make_network(qs, level=1, entity_filter=entity_filter)
            network = network.to_dict(realm=realm)
            cache.set(cache_key, network, None)
        return Response(network)
