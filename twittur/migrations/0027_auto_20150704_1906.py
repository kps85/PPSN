# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0026_userprofile_verifyhash'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupprofile',
            name='desc',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='verifyHash',
            field=models.CharField(max_length=16, default=''),
        ),
    ]
