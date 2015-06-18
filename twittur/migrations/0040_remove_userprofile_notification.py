# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0039_auto_20150618_1734'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='notification',
        ),
    ]
