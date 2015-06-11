# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0004_auto_20150602_1400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='picture',
            field=models.ImageField(help_text='Dieses Bild wird auf Deinem Profil und in deinen Nachrichten angezeigt.', default='picture/default.gif', upload_to='picture/', verbose_name='Profilbild', blank=True),
        ),
    ]
