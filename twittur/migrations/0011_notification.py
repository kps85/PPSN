# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('twittur', '0010_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('read', models.BooleanField(default=False)),
                ('date', models.DateTimeField(default=datetime.datetime.now, blank=True)),
                ('note', models.TextField(default=None, blank=True)),
                ('follower', models.ForeignKey(blank=True, related_name='ntfcFollower', to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(blank=True, related_name='ntfcGroup2', to='twittur.GroupProfile')),
                ('message', models.ForeignKey(blank=True, related_name='ntfcMessage', to='twittur.Message')),
                ('user', models.ForeignKey(related_name='ntfcUser', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
