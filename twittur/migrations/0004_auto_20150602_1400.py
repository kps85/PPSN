# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0003_auto_20150602_1214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='picture',
            field=models.ImageField(blank=True, default='/media/picture/default.gif', help_text='Dieses Bild wird auf Deinem Profil und in deinen Nachrichten angezeigt.', upload_to='picture/', verbose_name='Profilbild'),
        ),
    ]
