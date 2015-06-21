# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0005_message_readcomment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='readcomment',
            new_name='read',
        ),
    ]
