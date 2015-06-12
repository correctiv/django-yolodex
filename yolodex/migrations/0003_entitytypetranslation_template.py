# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yolodex', '0002_auto_20150612_1450'),
    ]

    operations = [
        migrations.AddField(
            model_name='entitytypetranslation',
            name='template',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
