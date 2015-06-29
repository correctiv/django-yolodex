from django.contrib import admin

from parler.admin import TranslatableAdmin

from .models import Realm, EntityType, Entity, Relationship, RelationshipType


class RealmAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


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
