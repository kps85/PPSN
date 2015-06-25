# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0023_userprofile_securitylevel'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='securityLevel',
            new_name='safety',
        ),
    ]
