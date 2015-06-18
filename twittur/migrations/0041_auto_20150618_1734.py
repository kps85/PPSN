# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0040_remove_userprofile_notification'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='read',
            name='message',
        ),
        migrations.RemoveField(
            model_name='read',
            name='user',
        ),
        migrations.DeleteModel(
            name='Read',
        ),
    ]
