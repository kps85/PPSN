# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0027_auto_20150617_1644'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupprofile',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
