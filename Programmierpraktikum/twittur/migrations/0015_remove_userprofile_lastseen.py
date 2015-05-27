# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0014_auto_20150527_1931'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='lastSeen',
        ),
    ]
