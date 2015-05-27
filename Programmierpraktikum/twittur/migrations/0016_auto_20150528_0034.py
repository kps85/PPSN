# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0015_remove_userprofile_lastseen'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='user',
            new_name='userprofile',
        ),
        migrations.AlterField(
            model_name='message',
            name='user',
            field=models.ForeignKey(to='twittur.UserProfile'),
        ),
    ]
