# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('twittur', '0006_auto_20150711_1508'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='favorite',
            field=models.ManyToManyField(related_name='favorite', to=settings.AUTH_USER_MODEL),
        ),
    ]
