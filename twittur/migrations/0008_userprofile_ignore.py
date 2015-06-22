# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0007_auto_20150622_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='ignore',
            field=models.BooleanField(default=False),
        ),
    ]
