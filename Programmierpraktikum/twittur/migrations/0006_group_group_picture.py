# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0005_auto_20150522_0039'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='group_picture',
            field=models.ImageField(upload_to=None, blank=True),
        ),
    ]
