# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('twittur', '0022_auto_20150616_1845'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('desc', models.CharField(max_length=200)),
                ('picture', models.ImageField(default=b'picture/default.gif', upload_to=b'picture/', blank=True, help_text=b'Dieses Bild wird auf Deinem Profil (gro&szlig;) und in deinen Nachrichten (klein) angezeigt.', verbose_name=b'Profilbild')),
                ('date', models.DateField(auto_now_add=True)),
                ('groupprofile', models.OneToOneField(to='auth.Group')),
            ],
        ),
    ]
