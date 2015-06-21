# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0004_auto_20150621_0032'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='readcomment',
            field=models.BooleanField(default=False),
        ),
    ]
