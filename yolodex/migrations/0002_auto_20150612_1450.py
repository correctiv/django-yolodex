# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_hstore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('yolodex', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='entitytype',
            name='settings',
            field=django_hstore.fields.DictionaryField(blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='relationshiptype',
            name='settings',
            field=django_hstore.fields.DictionaryField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='entity',
            name='data',
            field=django_hstore.fields.DictionaryField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='relationship',
            name='data',
            field=django_hstore.fields.DictionaryField(blank=True),
            preserve_default=True,
        ),
    ]
