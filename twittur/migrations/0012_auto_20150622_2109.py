# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0011_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='date',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='notification',
            name='follower',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True, related_name='ntfcFollower'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='group',
            field=models.ForeignKey(to='twittur.GroupProfile', null=True, blank=True, related_name='ntfcGroup2'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='message',
            field=models.ForeignKey(to='twittur.Message', null=True, blank=True, related_name='ntfcMessage'),
        ),
    ]
