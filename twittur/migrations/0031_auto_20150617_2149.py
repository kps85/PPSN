# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0030_auto_20150617_1937'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupprofile',
            name='password',
            field=models.CharField(default='', max_length=128),
        ),
        migrations.AddField(
            model_name='groupprofile',
            name='short',
            field=models.CharField(default=0, max_length=10),
            preserve_default=False,
        ),
    ]
