# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0003_auto_20150710_1800'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='studentNumber',
        ),
    ]
