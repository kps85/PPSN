# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0036_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='Read',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('read', models.BooleanField(default=False)),
                ('message', models.ForeignKey(to='twittur.Message')),
            ],
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='notification',
            field=models.ManyToManyField(to='twittur.Message', through='twittur.Read'),
        ),
        migrations.AddField(
            model_name='read',
            name='user',
            field=models.ForeignKey(to='twittur.UserProfile'),
        ),
    ]
