# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('twittur', '0023_groupprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupprofile',
            name='admin',
            field=models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='groupprofile',
            name='picture',
            field=models.ImageField(default=b'picture/default.gif', upload_to=b'picture/', blank=True, help_text=b'Geben sie ein Foto ein!', verbose_name=b'Profilbild'),
        ),
    ]
