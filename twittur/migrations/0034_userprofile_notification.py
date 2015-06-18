# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0033_auto_20150618_1356'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='notification',
            field=models.ManyToManyField(to='twittur.Message'),
        ),
    ]
