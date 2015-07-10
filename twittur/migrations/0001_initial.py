# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('question', models.CharField(max_length=100)),
                ('category', models.CharField(max_length=100)),
                ('answer', models.TextField(max_length=1000)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GroupProfile',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('short', models.CharField(max_length=10)),
                ('desc', models.CharField(max_length=200, blank=True)),
                ('password', models.CharField(help_text='Geben Sie ein Passwort zum Beitreten ihrer Gruppe ein. (optional)', max_length=128, blank=True)),
                ('picture', models.ImageField(help_text='Dieses Bild wird auf der Gruppenseite zu sehen sein!', upload_to='picture/', verbose_name='Gruppenbild', default='picture/gdefault.gif', blank=True)),
                ('date', models.DateField(default=datetime.date.today, blank=True)),
                ('joinable', models.BooleanField(default=True)),
                ('admin', models.ForeignKey(related_name='admin', to=settings.AUTH_USER_MODEL)),
                ('member', models.ManyToManyField(related_name='member', to=settings.AUTH_USER_MODEL)),
                ('supergroup', models.ForeignKey(related_name='sgroup', null=True, to='twittur.GroupProfile', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Hashtag',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=254)),
                ('picture', models.ImageField(upload_to='picture/', blank=True)),
                ('date', models.DateTimeField(verbose_name='date published')),
                ('ignore', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Nav',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('comment', models.BooleanField(default=False)),
                ('read', models.BooleanField(default=False)),
                ('notified', models.BooleanField(default=False)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('note', models.TextField(default=None, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('verifyHash', models.CharField(max_length=32, default='')),
                ('academicDiscipline', models.CharField(help_text='&Uuml;ber Ihren Studiengang werden Sie bestimmten Gruppen zugeordnet.', max_length=200)),
                ('picture', models.ImageField(help_text='Dieses Bild wird auf Ihrem Profil (gro&szlig;) und in Ihren Nachrichten (klein) angezeigt.', upload_to='picture/', verbose_name='Profilbild', default='picture/default.gif', blank=True)),
                ('location', models.CharField(help_text='Lassen Sie Ihre KommillitonInnen Sie finden!', max_length=200, default='None')),
                ('ignore', models.BooleanField(default=False)),
                ('safety', models.CharField(max_length=15, default='public')),
                ('follow', models.ManyToManyField(through='twittur.Notification', related_name='follow', to=settings.AUTH_USER_MODEL)),
                ('ignoreM', models.ManyToManyField(related_name='ignoreM', to='twittur.Message', blank=True)),
                ('ignoreU', models.ManyToManyField(related_name='ignoreU', to=settings.AUTH_USER_MODEL, blank=True)),
                ('userprofile', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='notification',
            name='follower',
            field=models.ForeignKey(related_name='ntfcFollower', null=True, to='twittur.UserProfile', blank=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='group',
            field=models.ForeignKey(related_name='ntfcGroup2', null=True, to='twittur.GroupProfile', blank=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='message',
            field=models.ForeignKey(related_name='ntfcMessage', null=True, to='twittur.Message', blank=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='user',
            field=models.ForeignKey(related_name='ntfcUser', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='message',
            name='attags',
            field=models.ManyToManyField(through='twittur.Notification', related_name='attags', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='message',
            name='comment',
            field=models.ForeignKey(related_name='comments', null=True, to='twittur.Message', blank=True),
        ),
        migrations.AddField(
            model_name='message',
            name='group',
            field=models.ForeignKey(related_name='group', null=True, to='twittur.GroupProfile', blank=True),
        ),
        migrations.AddField(
            model_name='message',
            name='hashtags',
            field=models.ManyToManyField(related_name='hashtags', to='twittur.Hashtag'),
        ),
        migrations.AddField(
            model_name='message',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
