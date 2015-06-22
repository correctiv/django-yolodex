import json

from django.template import Template, Context
from django.shortcuts import get_object_or_404, Http404, redirect
from django.views.generic import DetailView, ListView, TemplateView
from django.core.urlresolvers import resolve

from .models import Realm, Entity, EntityType


def get_current_app(request):
    return resolve(request.path).namespace


class BaseRealmMixin(object):
    _current_app = None

    @property
    def current_app(self):
        if self._current_app is None:
            self._current_app = get_current_app(self.request)
        return self._current_app

    def get_realm(self):
        if not hasattr(self, 'realm'):
            self.realm = get_object_or_404(Realm, slug=self.current_app)
        return self.realm

    def get_queryset(self):
        queryset = super(BaseRealmMixin, self).get_queryset()
        realm = self.get_realm()
        queryset = queryset.filter(realm=realm)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(BaseRealmMixin, self).get_context_data(**kwargs)
        context['realm'] = self.get_realm()
        return context


class RealmView(BaseRealmMixin, TemplateView):
    template_name = 'yolodex/overview.html'


class EntityListView(BaseRealmMixin, ListView):
    model = Entity
    paginate_by = 50

    def get(self, request, *args, **kwargs):
        try:
            self.type = EntityType.objects.translated(slug=kwargs['type']).get()
        except EntityType.DoesNotExist:
            raise Http404
        return super(EntityListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(EntityListView, self).get_queryset()
        return qs.filter(type=self.type).order_by('name')

    def get_context_data(self, **kwargs):
        ctx = super(EntityListView, self).get_context_data(**kwargs)
        ctx['type'] = self.type
        return ctx


class EntityDetailView(BaseRealmMixin, DetailView):
    model = Entity

    def get(self, request, *args, **kwargs):
        resp = super(EntityDetailView, self).get(request, *args, **kwargs)

        obj = self.object
        if obj.type.slug != self.kwargs['type']:
            return redirect(obj)

        return resp

    def get_context_data(self, **kwargs):
        context = super(EntityDetailView, self).get_context_data(**kwargs)

        obj = self.object
        context['network'] = obj.get_network(level=1)

        t = Template(obj.type.template)
        rendered = t.render(Context({'self': obj, 'realm': self.realm}))
        context['rendered'] = rendered

        return context
