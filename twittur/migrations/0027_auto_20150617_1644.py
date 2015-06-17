# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0026_auto_20150617_1642'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupprofile',
            name='date',
            field=models.DateField(default=datetime.datetime.now, blank=True),
        ),
    ]
