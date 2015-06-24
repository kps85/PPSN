# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0020_auto_20150624_1602'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupprofile',
            name='joinable',
            field=models.BooleanField(default=True),
        ),
    ]
