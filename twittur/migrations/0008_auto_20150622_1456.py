# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0007_auto_20150622_1435'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupprofile',
            name='picture',
            field=models.ImageField(upload_to='picture/', default='picture/gdefault.gif', verbose_name='Gruppenbild', help_text='Dieses Bild wird auf der Gruppenseite zu sehen sein!', blank=True),
        ),
    ]
