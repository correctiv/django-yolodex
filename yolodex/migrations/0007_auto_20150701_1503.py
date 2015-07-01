# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yolodex', '0006_auto_20150624_1750'),
    ]

    operations = [
        migrations.AddField(
            model_name='entity',
            name='degree',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entity',
            name='in_degree',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entity',
            name='out_degree',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
