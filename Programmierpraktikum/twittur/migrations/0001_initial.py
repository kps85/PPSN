# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Directed',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
            ],
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('group_name', models.CharField(max_length=50)),
                ('group_date', models.DateTimeField(verbose_name='date published')),
                ('group_description', models.CharField(max_length=256)),
                ('group_over', models.ForeignKey(to='twittur.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('message_date', models.DateTimeField(verbose_name='date published')),
                ('message_text', models.CharField(max_length=254)),
                ('message_picture', models.ImageField(upload_to=None)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('user_name', models.CharField(max_length=200)),
                ('user_nickname', models.CharField(max_length=200)),
                ('user_email', models.EmailField(max_length=200)),
                ('user_password', models.CharField(max_length=200)),
                ('user_lastSeen', models.DateTimeField(verbose_name='date published')),
                ('user_mnr', models.IntegerField(default=0)),
                ('user_studiengang', models.CharField(max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='message_from',
            field=models.ForeignKey(to='twittur.User'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='favorite_from_self',
            field=models.ForeignKey(to='twittur.User', related_name='favorite_self'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='favorite_to_user',
            field=models.ForeignKey(to='twittur.User', related_name='favorite_user'),
        ),
        migrations.AddField(
            model_name='directed',
            name='directed_group',
            field=models.ForeignKey(to='twittur.Group'),
        ),
        migrations.AddField(
            model_name='directed',
            name='directed_message',
            field=models.ForeignKey(to='twittur.Message'),
        ),
        migrations.AddField(
            model_name='directed',
            name='directed_user',
            field=models.ForeignKey(to='twittur.User'),
        ),
    ]
