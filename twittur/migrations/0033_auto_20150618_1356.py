# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0032_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupprofile',
            name='password',
            field=models.CharField(help_text=b'Geben Sie ein Passwort zum Beitreten ihrer Gruppe ein. (optional)', max_length=128, blank=True),
        ),
    ]
