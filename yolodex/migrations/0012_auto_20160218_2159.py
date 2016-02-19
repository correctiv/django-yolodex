# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
        ('yolodex', '0011_realm_is_public'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entity',
            name='data',
            field=django.contrib.postgres.fields.hstore.HStoreField(),
        ),
        migrations.AlterField(
            model_name='entitytype',
            name='settings',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True),
        ),
        migrations.AlterField(
            model_name='realm',
            name='settings',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True),
        ),
        migrations.AlterField(
            model_name='relationship',
            name='data',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True),
        ),
        migrations.AlterField(
            model_name='relationshiptype',
            name='settings',
            field=django.contrib.postgres.fields.hstore.HStoreField(),
        ),
    ]
