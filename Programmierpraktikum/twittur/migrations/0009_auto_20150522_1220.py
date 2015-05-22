# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0008_auto_20150522_0051'),
    ]

    operations = [
        migrations.CreateModel(
            name='has',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
            ],
        ),
        migrations.CreateModel(
            name='Hashtag',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('hashtag_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='IsInGroup',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('isInGroup_group', models.ForeignKey(to='twittur.Group')),
                ('isInGroup_user', models.ForeignKey(to='twittur.User')),
            ],
        ),
        migrations.AddField(
            model_name='has',
            name='has_hashtag',
            field=models.ForeignKey(to='twittur.Hashtag'),
        ),
        migrations.AddField(
            model_name='has',
            name='has_message',
            field=models.ForeignKey(to='twittur.Message'),
        ),
    ]
