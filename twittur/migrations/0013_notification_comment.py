# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0012_auto_20150622_2109'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='comment',
            field=models.BooleanField(default=False),
        ),
    ]
