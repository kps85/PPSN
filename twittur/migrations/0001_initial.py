# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
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
                ('desc', models.CharField(max_length=200)),
                ('password', models.CharField(help_text=b'Geben Sie ein Passwort zum Beitreten ihrer Gruppe ein. (optional)', max_length=128, blank=True)),
                ('picture', models.ImageField(default=b'picture/gdefault.gif', upload_to=b'picture/', blank=True, help_text=b'Geben sie ein Foto ein!', verbose_name=b'Profilbild')),
                ('date', models.DateField(default=datetime.date.today)),
                ('admin', models.ForeignKey(related_name='admin', to=settings.AUTH_USER_MODEL)),
                ('member', models.ManyToManyField(related_name='member', to=settings.AUTH_USER_MODEL)),
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
                ('read', models.BooleanField(default=True)),
                ('message', models.ForeignKey(related_name='message', to='twittur.Message')),
                ('user', models.ForeignKey(related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('studentNumber', models.CharField(default=b'000000', help_text=b'&Uuml;ber deine Matrikel-Nummer kannst Du eindeutig als Student der TU Berlin identifiziert werden.<br>(only numbers, max. 6 chars)', max_length=6)),
                ('academicDiscipline', models.CharField(help_text=b'&Uuml;ber deinen Studiengang wirst Du bestimmten Gruppen zugeordnet.', max_length=200)),
                ('picture', models.ImageField(default=b'picture/default.gif', upload_to=b'picture/', blank=True, help_text=b'Dieses Bild wird auf Deinem Profil (gro&szlig;) und in deinen Nachrichten (klein) angezeigt.', verbose_name=b'Profilbild')),
                ('location', models.CharField(default=b'None', help_text=b'Lass Deine KommilitonInnen Dich finden!', max_length=200)),
                ('follow', models.ManyToManyField(related_name='follow', to=settings.AUTH_USER_MODEL)),
                ('userprofile', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='attags',
            field=models.ManyToManyField(related_name='attags', through='twittur.Notification', to=settings.AUTH_USER_MODEL),
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
