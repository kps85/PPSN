# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0011_auto_20150522_2313'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='togroup',
            name='user',
        ),
        migrations.RemoveField(
            model_name='touser',
            name='fromUser',
        ),
        migrations.AlterField(
            model_name='touser',
            name='toUser',
            field=models.ForeignKey(to='twittur.User'),
        ),
    ]
