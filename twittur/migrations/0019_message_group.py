# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0018_remove_message_read'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='group',
            field=models.ForeignKey(related_name='group', blank=True, to='twittur.GroupProfile', null=True),
        ),
    ]
