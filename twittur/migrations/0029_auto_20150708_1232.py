# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0028_notification_notified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='verifyHash',
            field=models.CharField(max_length=32, default=''),
        ),
    ]
