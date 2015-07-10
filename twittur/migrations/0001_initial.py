# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question', models.CharField(max_length=100)),
                ('category', models.CharField(max_length=100)),
                ('answer', models.TextField(max_length=1000)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GroupProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('short', models.CharField(max_length=10)),
                ('desc', models.CharField(max_length=200, blank=True)),
                ('password', models.CharField(help_text=b'Geben Sie ein Passwort zum Beitreten ihrer Gruppe ein. (optional)', max_length=128, blank=True)),
                ('picture', models.ImageField(default=b'picture/gdefault.gif', upload_to=b'picture/', blank=True, help_text=b'Dieses Bild wird auf der Gruppenseite zu sehen sein!', verbose_name=b'Gruppenbild')),
                ('date', models.DateField(default=datetime.date.today, blank=True)),
                ('joinable', models.BooleanField(default=True)),
                ('admin', models.ForeignKey(related_name='admin', to=settings.AUTH_USER_MODEL)),
                ('member', models.ManyToManyField(related_name='member', to=settings.AUTH_USER_MODEL)),
                ('supergroup', models.ForeignKey(related_name='sgroup', blank=True, to='twittur.GroupProfile', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Hashtag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=254)),
                ('picture', models.ImageField(upload_to=b'picture/', blank=True)),
                ('date', models.DateTimeField(verbose_name=b'date published')),
                ('ignore', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Nav',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('verifyHash', models.CharField(default=b'', max_length=32)),
                ('studentNumber', models.CharField(default=b'000000', help_text=b'&Uuml;ber Ihre Matrikel-Nummer k&ouml;nnen Sie eindeutig als Student der TU Berlin identifiziert werden.<br>(muss aus 6 Ziffern bestehen)', max_length=6)),
                ('academicDiscipline', models.CharField(help_text=b'&Uuml;ber Ihren Studiengang werden Sie bestimmten Gruppen zugeordnet.', max_length=200)),
                ('picture', models.ImageField(default=b'picture/default.gif', upload_to=b'picture/', blank=True, help_text=b'Dieses Bild wird auf Ihrem Profil (gro&szlig;) und in Ihren Nachrichten (klein) angezeigt.', verbose_name=b'Profilbild')),
                ('location', models.CharField(default=b'None', help_text=b'Lassen Sie Ihre KommillitonInnen Sie finden!', max_length=200)),
                ('ignore', models.BooleanField(default=False)),
                ('safety', models.CharField(default=b'public', max_length=15)),
                ('follow', models.ManyToManyField(related_name='follow', through='twittur.Notification', to=settings.AUTH_USER_MODEL)),
                ('ignoreM', models.ManyToManyField(related_name='ignoreM', to='twittur.Message', blank=True)),
                ('ignoreU', models.ManyToManyField(related_name='ignoreU', to=settings.AUTH_USER_MODEL, blank=True)),
                ('userprofile', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='notification',
            name='follower',
            field=models.ForeignKey(related_name='ntfcFollower', blank=True, to='twittur.UserProfile', null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='group',
            field=models.ForeignKey(related_name='ntfcGroup2', blank=True, to='twittur.GroupProfile', null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='message',
            field=models.ForeignKey(related_name='ntfcMessage', blank=True, to='twittur.Message', null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='user',
            field=models.ForeignKey(related_name='ntfcUser', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='message',
            name='attags',
            field=models.ManyToManyField(related_name='attags', through='twittur.Notification', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='message',
            name='comment',
            field=models.ForeignKey(related_name='comments', blank=True, to='twittur.Message', null=True),
        ),
        migrations.AddField(
            model_name='message',
            name='group',
            field=models.ForeignKey(related_name='group', blank=True, to='twittur.GroupProfile', null=True),
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
