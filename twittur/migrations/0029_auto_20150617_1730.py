# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('twittur', '0028_auto_20150617_1650'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupprofile',
            name='member',
            field=models.ManyToManyField(related_name='member', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='groupprofile',
            name='admin',
            field=models.ForeignKey(related_name='admin', to=settings.AUTH_USER_MODEL),
        ),
    ]
