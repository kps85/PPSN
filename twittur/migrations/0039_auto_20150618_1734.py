# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0038_auto_20150618_1731'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='notification',
            field=models.ManyToManyField(related_name='notification', to='twittur.Message'),
        ),
    ]
