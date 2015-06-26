# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0003_auto_20150619_1759'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationf',
            name='read',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='notificationm',
            name='read',
            field=models.BooleanField(default=False),
        ),
    ]
