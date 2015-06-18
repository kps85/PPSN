# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0029_auto_20150617_1730'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupprofile',
            name='picture',
            field=models.ImageField(help_text='Geben sie ein Foto ein!', upload_to='picture/', default='picture/gdefault.gif', blank=True, verbose_name='Profilbild'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='location',
            field=models.CharField(help_text='Lass Deine KommilitonInnen Dich finden!', default='None', max_length=200),
        ),
    ]
