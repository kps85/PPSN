# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0007_auto_20150522_0045'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='user_studiengang',
            new_name='user_academic_discipline',
        ),
        migrations.AlterField(
            model_name='user',
            name='user_lastSeen',
            field=models.DateTimeField(verbose_name='last seen'),
        ),
    ]
