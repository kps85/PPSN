# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0025_auto_20150625_2006'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='verifyHash',
            field=models.CharField(default=b'', max_length=16, editable=False),
        ),
    ]
