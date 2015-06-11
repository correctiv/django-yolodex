from django.contrib import admin

from parler.admin import TranslatableAdmin

from .models import Realm, EntityType, Entity, Relationship, RelationshipType


class RealmAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


class EntityTypeAdmin(TranslatableAdmin):
    def get_prepopulated_fields(self, request, obj=None):
        return {
            'slug': ('name',)
        }


class RelationshipTypeAdmin(TranslatableAdmin):
    def get_prepopulated_fields(self, request, obj=None):
        return {
            'slug': ('name',)
        }


class RelationshipAdmin(admin.ModelAdmin):
    raw_id_fields = ('source', 'target')


class EntityAdmin(admin.ModelAdmin):
    list_filter = ('type',)


admin.site.register(Realm, RealmAdmin)
admin.site.register(EntityType, EntityTypeAdmin)
admin.site.register(Entity, EntityAdmin)
admin.site.register(Relationship, RelationshipAdmin)
admin.site.register(RelationshipType, RelationshipTypeAdmin)
