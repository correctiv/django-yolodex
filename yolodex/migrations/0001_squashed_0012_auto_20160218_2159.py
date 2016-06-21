# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-21 09:42
from __future__ import unicode_literals

import django.contrib.postgres.fields.hstore
import django.contrib.postgres.operations
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        django.contrib.postgres.operations.HStoreExtension(
        ),
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
                ('data', django.contrib.postgres.fields.hstore.HStoreField(blank=True)),
            ],
            options={
                'verbose_name_plural': 'Entities',
            },
        ),
        migrations.CreateModel(
            name='EntityType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EntityTypeTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
                ('master', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='yolodex.EntityType')),
                ('template', models.TextField(blank=True)),
                ('name_plural', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'verbose_name': 'entity type Translation',
                'default_permissions': (),
                'db_table': 'yolodex_entitytype_translation',
                'managed': True,
                'db_tablespace': '',
            },
        ),
        migrations.CreateModel(
            name='Realm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
                ('created_on', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('directed', models.BooleanField(default=True)),
                ('data', django.contrib.postgres.fields.hstore.HStoreField(blank=True)),
                ('realm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yolodex.Realm')),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source_relationships', to='yolodex.Entity')),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='target_relationships', to='yolodex.Entity')),
            ],
        ),
        migrations.CreateModel(
            name='RelationshipType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('realms', models.ManyToManyField(to=b'yolodex.Realm')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RelationshipTypeTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
                ('verb', models.CharField(blank=True, max_length=255)),
                ('reverse_verb', models.CharField(blank=True, max_length=255)),
                ('master', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='yolodex.RelationshipType')),
            ],
            options={
                'verbose_name': 'relationship type Translation',
                'default_permissions': (),
                'db_table': 'yolodex_relationshiptype_translation',
                'managed': True,
                'db_tablespace': '',
            },
        ),
        migrations.AlterUniqueTogether(
            name='relationshiptypetranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AddField(
            model_name='relationship',
            name='type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='yolodex.RelationshipType'),
        ),
        migrations.AlterUniqueTogether(
            name='entitytypetranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AddField(
            model_name='entitytype',
            name='realms',
            field=models.ManyToManyField(to=b'yolodex.Realm'),
        ),
        migrations.AddField(
            model_name='entity',
            name='realm',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yolodex.Realm'),
        ),
        migrations.AddField(
            model_name='entity',
            name='type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='yolodex.EntityType'),
        ),
        migrations.AddField(
            model_name='entity',
            name='text',
            field=models.TextField(blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='entity',
            unique_together=set([('realm', 'slug')]),
        ),
        migrations.AddField(
            model_name='entitytype',
            name='settings',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True),
        ),
        migrations.AddField(
            model_name='relationshiptype',
            name='settings',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True),
        ),
        migrations.AddField(
            model_name='realm',
            name='settings',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True),
        ),
        migrations.AlterModelOptions(
            name='entity',
            options={'verbose_name': 'Entit\xe4t', 'verbose_name_plural': 'Entit\xe4ten'},
        ),
        migrations.AlterModelOptions(
            name='entitytype',
            options={'verbose_name': 'Entit\xe4tstyp', 'verbose_name_plural': 'Enit\xe4tstypen'},
        ),
        migrations.AlterModelOptions(
            name='entitytypetranslation',
            options={'default_permissions': (), 'managed': True, 'verbose_name': 'Entit\xe4tstyp Translation'},
        ),
        migrations.AlterModelOptions(
            name='realm',
            options={'verbose_name': 'Gebiet', 'verbose_name_plural': 'Gebiete'},
        ),
        migrations.AlterModelOptions(
            name='relationship',
            options={'verbose_name': 'Beziehung', 'verbose_name_plural': 'Beziehungen'},
        ),
        migrations.AlterModelOptions(
            name='relationshiptype',
            options={'verbose_name': 'Beziehungstyp', 'verbose_name_plural': 'Beziehungstypen'},
        ),
        migrations.AlterModelOptions(
            name='relationshiptypetranslation',
            options={'default_permissions': (), 'managed': True, 'verbose_name': 'Beziehungstyp Translation'},
        ),
        migrations.AddField(
            model_name='entity',
            name='sources',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='relationship',
            name='sources',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='entity',
            name='degree',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='entity',
            name='in_degree',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='entity',
            name='out_degree',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='realm',
            name='corrections',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='realm',
            name='updated_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='entity',
            name='version',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='realm',
            name='version',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='relationship',
            name='version',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='realm',
            name='edge_url',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='realm',
            name='node_url',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='realm',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
    ]
