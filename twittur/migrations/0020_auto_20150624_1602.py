# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0019_message_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='ignoreM',
            field=models.ManyToManyField(related_name='ignoreM', to='twittur.Message', blank=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='ignoreU',
            field=models.ManyToManyField(related_name='ignoreU', to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
