# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0017_auto_20150622_2308'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='read',
        ),
    ]
