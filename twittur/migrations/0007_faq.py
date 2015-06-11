# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0006_auto_20150605_0921'),
    ]

    operations = [
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('question', models.CharField(max_length=100)),
                ('category', models.CharField(max_length=100)),
                ('answer', models.TextField(max_length=1000)),
            ],
        ),
    ]
