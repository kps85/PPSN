# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0013_auto_20150605_1513'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='studentNumber',
            field=models.CharField(default='000000', max_length=6),
        ),
    ]
