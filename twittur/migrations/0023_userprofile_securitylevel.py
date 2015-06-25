# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0022_groupprofile_supergroup'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='securityLevel',
            field=models.CharField(default=b'public', max_length=15),
        ),
    ]
