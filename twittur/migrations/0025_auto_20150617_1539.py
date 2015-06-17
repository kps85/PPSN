# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0024_auto_20150617_1537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupprofile',
            name='picture',
            field=models.ImageField(default=b'picture/gdefault.gif', upload_to=b'picture/', blank=True, help_text=b'Geben sie ein Foto ein!', verbose_name=b'Profilbild'),
        ),
    ]
