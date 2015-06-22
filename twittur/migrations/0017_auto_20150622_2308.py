# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0016_auto_20150622_2303'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notificationf',
            name='me',
        ),
        migrations.RemoveField(
            model_name='notificationf',
            name='you',
        ),
        migrations.RemoveField(
            model_name='notificationg',
            name='group',
        ),
        migrations.RemoveField(
            model_name='notificationg',
            name='user',
        ),
        migrations.RemoveField(
            model_name='notificationm',
            name='message',
        ),
        migrations.RemoveField(
            model_name='notificationm',
            name='user',
        ),
        migrations.DeleteModel(
            name='NotificationF',
        ),
        migrations.DeleteModel(
            name='NotificationG',
        ),
        migrations.DeleteModel(
            name='NotificationM',
        ),
    ]
