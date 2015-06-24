# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yolodex', '0005_entitytypetranslation_name_plural'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='entity',
            options={'verbose_name': 'Entit\xe4t', 'verbose_name_plural': 'Entit\xe4ten'},
        ),
        migrations.AlterModelOptions(
            name='entitytype',
            options={'verbose_name': 'Entit\xe4tstyp', 'verbose_name_plural': 'Enit\xe4tstypen'},
        ),
        migrations.AlterModelOptions(
            name='entitytypetranslation',
            options={'default_permissions': (), 'verbose_name': 'Entit\xe4tstyp Translation', 'managed': True},
        ),
        migrations.AlterModelOptions(
            name='realm',
            options={'verbose_name': 'Gebiet', 'verbose_name_plural': 'Gebiete'},
        ),
        migrations.AlterModelOptions(
            name='relationship',
            options={'verbose_name': 'Beziehung', 'verbose_name_plural': 'Beziehungen'},
        ),
        migrations.AlterModelOptions(
            name='relationshiptype',
            options={'verbose_name': 'Beziehungstyp', 'verbose_name_plural': 'Beziehungstypen'},
        ),
        migrations.AlterModelOptions(
            name='relationshiptypetranslation',
            options={'default_permissions': (), 'verbose_name': 'Beziehungstyp Translation', 'managed': True},
        ),
        migrations.AddField(
            model_name='entity',
            name='sources',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='relationship',
            name='sources',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
