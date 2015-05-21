# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0002_auto_20150521_2339'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Directed',
            new_name='ToGroup',
        ),
        migrations.RenameField(
            model_name='togroup',
            old_name='directed_group',
            new_name='togroup_group',
        ),
        migrations.RenameField(
            model_name='togroup',
            old_name='directed_message',
            new_name='togroup_message',
        ),
        migrations.RenameField(
            model_name='togroup',
            old_name='directed_user',
            new_name='togroup_user',
        ),
    ]
