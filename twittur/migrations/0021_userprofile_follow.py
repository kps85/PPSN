# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('twittur', '0020_auto_20150608_1227'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='follow',
            field=models.ManyToManyField(related_name='follow', to=settings.AUTH_USER_MODEL),
        ),
    ]
