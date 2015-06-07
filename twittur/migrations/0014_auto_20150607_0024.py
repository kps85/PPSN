# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('twittur', '0013_auto_20150605_1513'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='attags',
            field=models.ManyToManyField(related_name='attag', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='message',
            name='hashtags',
            field=models.ManyToManyField(to='twittur.Hashtag'),
        ),
    ]
