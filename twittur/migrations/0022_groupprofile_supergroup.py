# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0021_groupprofile_joinable'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupprofile',
            name='supergroup',
            field=models.ForeignKey(related_name='sgroup', blank=True, to='twittur.GroupProfile', null=True),
        ),
    ]
