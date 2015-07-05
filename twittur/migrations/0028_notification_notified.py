# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0027_auto_20150704_1906'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='notified',
            field=models.BooleanField(default=False),
        ),
    ]
