# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_hstore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('yolodex', '0003_entitytypetranslation_template'),
    ]

    operations = [
        migrations.AddField(
            model_name='entity',
            name='text',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='realm',
            name='settings',
            field=django_hstore.fields.DictionaryField(blank=True),
            preserve_default=True,
        ),
    ]
