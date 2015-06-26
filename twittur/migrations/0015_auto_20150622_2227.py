# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0014_auto_20150622_2157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='follower',
            field=models.ForeignKey(null=True, to='twittur.UserProfile', related_name='ntfcFollower', blank=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='follow',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='follow', through='twittur.Notification'),
        ),
    ]
