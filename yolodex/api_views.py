from django.shortcuts import get_object_or_404
from django.core.cache import cache

from rest_framework import viewsets, serializers
from rest_framework.response import Response
from rest_framework.routers import Route, DynamicDetailRoute, SimpleRouter
from rest_framework.decorators import detail_route

from .models import Realm, Entity, EntityType
from .network import make_network, undirected_comp
from .views import get_current_app


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


class EntityViewSet(RealmApiMixin, viewsets.ReadOnlyModelViewSet):
    """
    A viewset that provides the standard actions
    """
    serializer_class = EntitySerializer

    def get_queryset(self):
        realm = self.get_realm(self.request)
        return Entity.objects.filter(realm=realm)

    @detail_route()
    def network(self, request, **kwargs):
        """
        Returns a list of all the group names that the given
        user belongs to.
        """
        obj = self.get_object()
        realm = self.get_realm(request)
        return Response(obj.get_network(level=2).to_dict(realm=realm))


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

        cache_key = 'yolodex:api:entitype:network:{realm}:{type}'.format(
            realm=realm.pk,
            type=obj.pk
        )
        network = cache.get(cache_key)
        if network is None:
            qs = Entity.objects.filter(realm=realm, type=obj)
            entity_filter = self.make_entity_filter(obj)
            network = make_network(qs, level=1, entity_filter=entity_filter)
            network = network.to_dict(realm=realm)
            cache.set(cache_key, network)
        return Response(network)
