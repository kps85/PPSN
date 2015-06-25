# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0024_auto_20150625_1520'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='safety',
            field=models.CharField(max_length=15, default='public'),
        ),
    ]
