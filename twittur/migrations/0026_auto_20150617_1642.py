# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0025_auto_20150617_1539'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupprofile',
            name='groupprofile',
        ),
        migrations.AddField(
            model_name='groupprofile',
            name='name',
            field=models.CharField(default=None, max_length=50),
            preserve_default=False,
        ),
    ]
