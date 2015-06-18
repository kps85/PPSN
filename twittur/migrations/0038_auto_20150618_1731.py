# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0037_auto_20150618_1728'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='notification',
            field=models.ManyToManyField(to='twittur.Message'),
        ),
    ]
