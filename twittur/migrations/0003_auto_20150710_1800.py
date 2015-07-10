# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0002_userprofile_academicdiscipline2'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='academicDiscipline2',
            new_name='studentNumber',
        ),
    ]
