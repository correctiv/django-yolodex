from django.shortcuts import get_object_or_404

from rest_framework import viewsets, serializers
from rest_framework.response import Response
from rest_framework.routers import Route, DynamicDetailRoute, SimpleRouter
from rest_framework.decorators import detail_route

from .models import Realm, Entity
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
        return Response(obj.get_network(level=2).to_dict())
