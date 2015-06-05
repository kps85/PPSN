# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0005_auto_20150602_1433'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='location',
            field=models.CharField(max_length=200, default='None'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='picture',
            field=models.ImageField(verbose_name='Profilbild', help_text='Dieses Bild wird auf Deinem Profil (gro&szlig;) und in deinen Nachrichten (klein) angezeigt.', blank=True, default='picture/default.gif', upload_to='picture/'),
        ),
    ]
