# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yolodex', '0010_auto_20150708_1129'),
    ]

    operations = [
        migrations.AddField(
            model_name='realm',
            name='is_public',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
