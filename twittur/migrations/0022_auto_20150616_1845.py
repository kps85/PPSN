# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0021_userprofile_follow'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='superGroup',
        ),
        migrations.RemoveField(
            model_name='isingroup',
            name='group',
        ),
        migrations.RemoveField(
            model_name='isingroup',
            name='user',
        ),
        migrations.RemoveField(
            model_name='togroup',
            name='group',
        ),
        migrations.RemoveField(
            model_name='togroup',
            name='message',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='location',
            field=models.CharField(default=b'None', help_text=b'Lass Deine KommilitonInnen Dich finden!', max_length=200),
        ),
        migrations.DeleteModel(
            name='Group',
        ),
        migrations.DeleteModel(
            name='IsInGroup',
        ),
        migrations.DeleteModel(
            name='ToGroup',
        ),
    ]
