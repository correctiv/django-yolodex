# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import django_hstore.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
                ('data', django_hstore.fields.DictionaryField()),
            ],
            options={
                'verbose_name_plural': 'Entities',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EntityType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EntityTypeTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(max_length=15, verbose_name='Language', db_index=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
                ('master', models.ForeignKey(related_name='translations', editable=False, to='yolodex.EntityType', null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'yolodex_entitytype_translation',
                'db_tablespace': '',
                'default_permissions': (),
                'verbose_name': 'entity type Translation',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Realm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
                ('created_on', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('directed', models.BooleanField(default=True)),
                ('data', django_hstore.fields.DictionaryField()),
                ('realm', models.ForeignKey(to='yolodex.Realm')),
                ('source', models.ForeignKey(related_name='source_relationships', to='yolodex.Entity')),
                ('target', models.ForeignKey(related_name='target_relationships', to='yolodex.Entity')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RelationshipType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('realms', models.ManyToManyField(to='yolodex.Realm')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RelationshipTypeTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(max_length=15, verbose_name='Language', db_index=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
                ('verb', models.CharField(max_length=255, blank=True)),
                ('reverse_verb', models.CharField(max_length=255, blank=True)),
                ('master', models.ForeignKey(related_name='translations', editable=False, to='yolodex.RelationshipType', null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'yolodex_relationshiptype_translation',
                'db_tablespace': '',
                'default_permissions': (),
                'verbose_name': 'relationship type Translation',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='relationshiptypetranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AddField(
            model_name='relationship',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='yolodex.RelationshipType', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='entitytypetranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AddField(
            model_name='entitytype',
            name='realms',
            field=models.ManyToManyField(to='yolodex.Realm'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entity',
            name='realm',
            field=models.ForeignKey(to='yolodex.Realm'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entity',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='yolodex.EntityType', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='entity',
            unique_together=set([('realm', 'slug')]),
        ),
    ]
