# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_picture',
            field=models.ImageField(upload_to=None, blank=True),
        ),
        migrations.AlterField(
            model_name='group',
            name='group_over',
            field=models.ForeignKey(to='twittur.Group', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='message_picture',
            field=models.ImageField(upload_to=None, blank=True),
        ),
    ]
