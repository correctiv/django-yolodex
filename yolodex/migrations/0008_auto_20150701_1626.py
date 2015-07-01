# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yolodex', '0007_auto_20150701_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='realm',
            name='corrections',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='realm',
            name='updated_on',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
