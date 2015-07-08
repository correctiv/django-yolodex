# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yolodex', '0009_auto_20150708_1035'),
    ]

    operations = [
        migrations.AddField(
            model_name='realm',
            name='edge_url',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='realm',
            name='node_url',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
    ]
