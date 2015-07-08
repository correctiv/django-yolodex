from django.contrib import admin
from django.shortcuts import redirect
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import PermissionDenied

from parler.admin import TranslatableAdmin

from .models import Realm, EntityType, Entity, Relationship, RelationshipType
from .importer import YolodexImporter
from .api_views import clear_network_cache


class RealmAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

    def get_urls(self):
        urls = super(RealmAdmin, self).get_urls()
        my_urls = [
            url(r'^(?P<realm_id>\d+)/update-graph/$',
                self.admin_site.admin_view(self.update_graph),
                name='yolodex-admin_update_graph'),
        ]
        return my_urls + urls

    def update_graph(self, request, realm_id):
        if not request.method == 'POST':
            raise PermissionDenied
        if not self.has_change_permission(request):
            raise PermissionDenied

        realm = Realm.objects.get(pk=realm_id)
        yimp = YolodexImporter(realm)
        try:
            yimp.import_graph_from_urls(
                realm.node_url, realm.edge_url,
                update=True,
            )
            clear_network_cache(realm, Entity.objects.filter(realm=realm))
        except Exception as e:
            self.message_user(request, _("Graph update failed: %s" % e))
        else:
            self.message_user(request, _("Graph updated: %s" % yimp.stats))
        return redirect('admin:yolodex_realm_change', realm.pk)


class EntityTypeAdmin(TranslatableAdmin):
    list_display = ('name', 'name_plural')

    def get_prepopulated_fields(self, request, obj=None):
        return {
            'slug': ('name',)
        }


class RelationshipTypeAdmin(TranslatableAdmin):
    list_display = ('name', 'verb', 'reverse_verb')

    def get_prepopulated_fields(self, request, obj=None):
        return {
            'slug': ('name',)
        }


class RelationshipAdmin(admin.ModelAdmin):
    list_filter = ('realm', 'type',)
    search_fields = ('source__name', 'target__name',)
    list_display = ('__str__', 'source', 'target', 'type')
    raw_id_fields = ('source', 'target')


class EntityAdmin(admin.ModelAdmin):
    list_filter = ('realm', 'type',)
    search_fields = ('name',)


admin.site.register(Realm, RealmAdmin)
admin.site.register(EntityType, EntityTypeAdmin)
admin.site.register(Entity, EntityAdmin)
admin.site.register(Relationship, RelationshipAdmin)
admin.site.register(RelationshipType, RelationshipTypeAdmin)
