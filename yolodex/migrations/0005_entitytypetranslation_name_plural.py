# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yolodex', '0004_auto_20150622_1206'),
    ]

    operations = [
        migrations.AddField(
            model_name='entitytypetranslation',
            name='name_plural',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
    ]
