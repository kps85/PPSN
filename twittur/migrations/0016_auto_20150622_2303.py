# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0015_auto_20150622_2227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='attags',
            field=models.ManyToManyField(through='twittur.Notification', related_name='attags', to=settings.AUTH_USER_MODEL),
        ),
    ]
