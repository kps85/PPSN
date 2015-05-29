# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('twittur', '0012_auto_20150522_2319'),
    ]

    operations = [
        migrations.CreateModel(
            name='Nav',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user', models.OneToOneField(serialize=False, to=settings.AUTH_USER_MODEL, primary_key=True)),
                ('lastSeen', models.DateTimeField(verbose_name='last seen')),
                ('studentNumber', models.IntegerField(default=0)),
                ('academicDiscipline', models.CharField(max_length=200)),
                ('picture', models.ImageField(blank=True, default='picture/default.gif', upload_to='picture/')),
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
            field=models.ImageField(blank=True, default='picture/defaultG.gif', upload_to='picture/'),
        ),
        migrations.AlterField(
            model_name='isingroup',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='message',
            name='picture',
            field=models.ImageField(blank=True, upload_to='picture/'),
        ),
        migrations.AlterField(
            model_name='message',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='user'),
        ),
        migrations.AlterField(
            model_name='touser',
            name='toUser',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='User',
        ),
    ]
