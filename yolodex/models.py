from django.db import models
from django.db.models import Q
from django.utils.encoding import python_2_unicode_compatible
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.template import Template, Context

from django_hstore import hstore
from parler.models import TranslatableModel, TranslatedFields

from .network import make_network


@python_2_unicode_compatible
class Realm(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)

    created_on = models.DateTimeField()

    def __str__(self):
        return self.name

    def get_types(self):
        return {
            'node': {
                t.slug: t.get_data() for t in self.entitytype_set.all()
            },
            'edge': {
                t.slug: t.get_data() for t in self.relationshiptype_set.all()
            }
        }


class EntityType(TranslatableModel):
    realms = models.ManyToManyField(Realm)
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        slug=models.SlugField(max_length=255),
        template=models.TextField(blank=True)
    )
    settings = hstore.DictionaryField(blank=True)

    def __str__(self):
        return self.safe_translation_getter('name', language_code='en')

    def get_data(self):
        return {
            'name': self.name,
            'slug': self.slug,
            'settings': self.settings
        }


@python_2_unicode_compatible
class Entity(models.Model):
    realm = models.ForeignKey(Realm)
    type = models.ForeignKey(EntityType, null=True, on_delete=models.SET_NULL)

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)

    data = hstore.DictionaryField(blank=True)

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

    def get_network(self, level=1, include_self=True):
        return make_network([self], level=level, include_self=include_self)


class RelationshipType(TranslatableModel):
    realms = models.ManyToManyField(Realm)
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        slug=models.SlugField(max_length=255),
        verb=models.CharField(max_length=255, blank=True),
        reverse_verb=models.CharField(max_length=255, blank=True)
    )

    settings = hstore.DictionaryField(blank=True)

    def __str__(self):
        return self.safe_translation_getter('name', language_code='en')

    def get_data(self):
        return {
            'name': self.name,
            'slug': self.slug,
            'settings': self.settings
        }

    def _verbify(self, template, edge):
        t = Template(template)
        return t.render(Context({'self': edge.data}))

    def verbify(self, edge):
        return self._verbify(self.verb, edge)

    def reverse_verbify(self, subject):
        return self._verbify(self.reverse_verb, subject)

    def render_with_subject(self, edge, subject=None):
        if (subject is None or subject == edge.source) or not self.reverse_verb:
            return u'{source} {verb} {target}'.format(
                source=edge.source.name,
                verb=self.verbify(edge),
                target=edge.target.name
            )
        return u'{target} {reverse_verb} {source}'.format(
            source=edge.source.name,
            reverse_verb=self.reverse_verbify(edge),
            target=edge.target.name
        )


@python_2_unicode_compatible
class Relationship(models.Model):
    realm = models.ForeignKey(Realm)

    source = models.ForeignKey(Entity,
                               related_name='source_relationships')
    target = models.ForeignKey(Entity,
                               related_name='target_relationships')
    directed = models.BooleanField(default=True)
    type = models.ForeignKey(RelationshipType, null=True, on_delete=models.SET_NULL)

    data = hstore.DictionaryField(blank=True)

    objects = hstore.HStoreManager()

    def __str__(self):
        return u'%s %s %s' % (
            self.source,
            '->' if self.directed else '<->',
            self.target
        )

    def render_with_subject(self, subject=None):
        return self.type.render_with_subject(self, subject)

    def render_without_subject(self, subject=None):
        if subject is None or subject == self.source:
            return u'{target} {reverse_verb}'.format(
                reverse_verb=self.type.reverse_verbify(self),
                target=self.target.name
            )
        return u'{source} {verb}'.format(
            verb=self.type.verbify(self),
            source=self.source.name
        )
