# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0003_auto_20150522_0029'),
    ]

    operations = [
        migrations.RenameField(
            model_name='group',
            old_name='group_over',
            new_name='group_super',
        ),
    ]
