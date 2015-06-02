# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0002_userprofile_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='picture',
            field=models.ImageField(default='defaultG.gif', blank=True, upload_to='picture/'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='picture',
            field=models.ImageField(upload_to='picture/', help_text='Dieses Bild wird auf Deinem Profil und in deinen Nachrichten angezeigt.', verbose_name='Profilbild', blank=True, default='picture/default.gif'),
        ),
    ]
