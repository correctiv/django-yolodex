from django.db import models
from django.db.models import Q
from django.utils.encoding import python_2_unicode_compatible
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from django_hstore import hstore
from parler.models import TranslatableModel, TranslatedFields

from .network import Network


@python_2_unicode_compatible
class Realm(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)

    created_on = models.DateTimeField()

    def __str__(self):
        return self.name


class EntityType(TranslatableModel):
    realms = models.ManyToManyField(Realm)
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        slug=models.SlugField(max_length=255)
    )

    def __str__(self):
        return self.safe_translation_getter('name', language_code='en')


@python_2_unicode_compatible
class Entity(models.Model):
    realm = models.ForeignKey(Realm)
    type = models.ForeignKey(EntityType, null=True, on_delete=models.SET_NULL)

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)

    data = hstore.DictionaryField()

    objects = hstore.HStoreManager()

    class Meta:
        unique_together = ('realm', 'slug')
        verbose_name_plural = _('Entities')

    def __str__(self):
        return u'{name} ({type})'.format(name=self.name, type=self.type)

    def get_absolute_url(self):
        return reverse('yolodex:entity_detail', kwargs={
            'type': self.type.slug,
            'slug': self.slug
        }, current_app=self.realm.slug)

    def get_network(self, level=1):
        assert level < 4
        entities = set()
        entities.add(self)
        relations = set()
        current_level = level
        entity_lookups = [self.pk]
        while current_level > 0:
            rels = list(Relationship.objects.filter(
                Q(source_id__in=entity_lookups) | Q(target_id__in=entity_lookups)
                ).select_related('source', 'target'))
            new_entities = set([r.source for r in rels])
            new_entities |= set([r.target for r in rels])
            relations |= set(rels)
            entity_lookups = [o.pk for o in new_entities]
            entities |= new_entities
            current_level -= 1
        return Network(entities, relations)


class RelationshipType(TranslatableModel):
    realms = models.ManyToManyField(Realm)
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        slug=models.SlugField(max_length=255),
        verb=models.CharField(max_length=255, blank=True),
        reverse_verb=models.CharField(max_length=255, blank=True)
    )

    def __str__(self):
        return self.safe_translation_getter('name', language_code='en')


@python_2_unicode_compatible
class Relationship(models.Model):
    realm = models.ForeignKey(Realm)

    source = models.ForeignKey(Entity,
                               related_name='source_relationships')
    target = models.ForeignKey(Entity,
                               related_name='target_relationships')
    directed = models.BooleanField(default=True)
    type = models.ForeignKey(RelationshipType, null=True, on_delete=models.SET_NULL)

    data = hstore.DictionaryField()

    objects = hstore.HStoreManager()

    def __str__(self):
        return u'%s %s %s' % (
            self.source,
            '->' if self.directed else '<->',
            self.target
        )
