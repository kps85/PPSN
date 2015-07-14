# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('twittur', '0007_message_favorite'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='retweet',
            field=models.ManyToManyField(related_name='retweet', to=settings.AUTH_USER_MODEL),
        ),
    ]
