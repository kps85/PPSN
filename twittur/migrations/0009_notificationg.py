# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('twittur', '0008_auto_20150622_1456'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationG',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('read', models.BooleanField(default=False)),
                ('date', models.DateTimeField(default=datetime.datetime.now, blank=True)),
                ('note', models.TextField(default=None, blank=True)),
                ('group', models.ForeignKey(to='twittur.GroupProfile', related_name='ntfcGroup')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='ntfcMember')),
            ],
        ),
    ]
