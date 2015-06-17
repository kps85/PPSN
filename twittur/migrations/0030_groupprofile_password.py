# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0029_auto_20150617_1730'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupprofile',
            name='password',
            field=models.CharField(max_length=50, blank=True),
        ),
    ]
