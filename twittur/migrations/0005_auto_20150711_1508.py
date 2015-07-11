# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0004_remove_userprofile_studentnumber'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='date',
            field=models.DateTimeField(verbose_name='date published', default=datetime.datetime(2015, 7, 11, 13, 8, 23, 421040, tzinfo=utc)),
        ),
    ]
