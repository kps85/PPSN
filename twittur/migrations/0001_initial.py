# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('fromUser', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='favorite_from')),
                ('toUser', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='favorite_to')),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=256)),
                ('picture', models.ImageField(blank=True, default='picture/defaultG.gif', upload_to='picture/')),
                ('date', models.DateTimeField(verbose_name='date published')),
                ('superGroup', models.ForeignKey(blank=True, to='twittur.Group', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Has',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
            ],
        ),
        migrations.CreateModel(
            name='Hashtag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='IsInGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('group', models.ForeignKey(to='twittur.Group')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('text', models.CharField(max_length=254)),
                ('picture', models.ImageField(blank=True, upload_to='picture/')),
                ('date', models.DateTimeField(verbose_name='date published')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Nav',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
            ],
        ),
        migrations.CreateModel(
            name='ToGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('group', models.ForeignKey(to='twittur.Group')),
                ('message', models.ForeignKey(to='twittur.Message')),
            ],
        ),
        migrations.CreateModel(
            name='ToUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('message', models.ForeignKey(to='twittur.Message')),
                ('toUser', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('studentNumber', models.IntegerField(default=0)),
                ('academicDiscipline', models.CharField(max_length=200)),
                ('picture', models.ImageField(blank=True, default='picture/default.gif', upload_to='picture/')),
                ('userprofile', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='has',
            name='hashtag',
            field=models.ForeignKey(to='twittur.Hashtag'),
        ),
        migrations.AddField(
            model_name='has',
            name='message',
            field=models.ForeignKey(to='twittur.Message'),
        ),
    ]
