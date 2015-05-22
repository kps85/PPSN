# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0009_auto_20150522_1220'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='user_academic_discipline',
            new_name='user_academicDiscipline',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='user_mnr',
            new_name='user_studentNumber',
        ),
        migrations.AlterField(
            model_name='group',
            name='group_picture',
            field=models.ImageField(blank=True, upload_to='profilPicture/'),
        ),
        migrations.AlterField(
            model_name='message',
            name='message_picture',
            field=models.ImageField(blank=True, upload_to='messagePicture/'),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_picture',
            field=models.ImageField(blank=True, upload_to='profilPicture/'),
        ),
    ]
