# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0006_group_group_picture'),
    ]

    operations = [
        migrations.RenameField(
            model_name='favorite',
            old_name='favorite_from_self',
            new_name='favorite_from',
        ),
        migrations.RenameField(
            model_name='favorite',
            old_name='favorite_to_user',
            new_name='favorite_to',
        ),
    ]
