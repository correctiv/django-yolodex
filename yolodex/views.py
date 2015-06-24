from django.template import Template, Context
from django.shortcuts import get_object_or_404, Http404, redirect
from django.views.generic import DetailView, ListView, TemplateView

from .models import Realm, Entity, EntityType
from .api_views import search
from .utils import get_current_app


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


class EntitySearchView(BaseRealmMixin, ListView):
    model = Entity
    paginate_by = 50
    template_name = 'yolodex/entity_search.html'
    allow_empty = True

    def get_queryset(self):
        qs = super(EntitySearchView, self).get_queryset()
        self.query = self.request.GET.get('q', '')
        qs = search(qs, self.query)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super(EntitySearchView, self).get_context_data(**kwargs)
        ctx['query'] = self.query
        ctx['getvars'] = '&q={}'.format(self.query)
        return ctx


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
        context['realm'] = self.get_realm()

        t = Template(obj.type.template)
        rendered = t.render(Context({'self': obj, 'realm': self.realm}))
        context['rendered'] = rendered

        return context
