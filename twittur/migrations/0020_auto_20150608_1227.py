# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0019_auto_20150608_1221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faq',
            name='author',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
