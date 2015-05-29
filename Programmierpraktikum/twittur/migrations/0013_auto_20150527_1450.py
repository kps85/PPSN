# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('twittur', '0012_auto_20150522_2319'),
    ]

    operations = [
        migrations.CreateModel(
            name='Nav',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('lastSeen', models.DateTimeField(verbose_name='last seen')),
                ('studentNumber', models.IntegerField(default=0)),
                ('academicDiscipline', models.CharField(max_length=200)),
                ('picture', models.ImageField(upload_to='picture/', blank=True, default='picture/default.gif')),
            ],
        ),
        migrations.AlterField(
            model_name='favorite',
            name='fromUser',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='favorite_from'),
        ),
        migrations.AlterField(
            model_name='favorite',
            name='toUser',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='favorite_to'),
        ),
        migrations.AlterField(
            model_name='group',
            name='picture',
            field=models.ImageField(upload_to='picture/', blank=True, default='picture/defaultG.gif'),
        ),
        migrations.AlterField(
            model_name='isingroup',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='message',
            name='picture',
            field=models.ImageField(upload_to='picture/', blank=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='user'),
        ),
        migrations.AlterField(
            model_name='touser',
            name='toUser',
            field=models.ForeignKey(to='twittur.UserProfile'),
        ),
        migrations.DeleteModel(
            name='User',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
    ]
