# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yolodex', '0008_auto_20150701_1626'),
    ]

    operations = [
        migrations.AddField(
            model_name='entity',
            name='version',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='realm',
            name='version',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='relationship',
            name='version',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
