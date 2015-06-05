# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0010_auto_20150605_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faq',
            name='author',
            field=models.CharField(max_length=25),
        ),
    ]
