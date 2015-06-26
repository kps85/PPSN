# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='comment',
            field=models.ForeignKey(related_name='comments', blank=True, to='twittur.Message', null=True),
        ),
    ]
