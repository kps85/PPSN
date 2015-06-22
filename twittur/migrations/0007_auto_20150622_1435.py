# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('twittur', '0006_auto_20150621_0045'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='ignore',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='ignoreM',
            field=models.ManyToManyField(related_name='ignoreM', to='twittur.Message'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='ignoreU',
            field=models.ManyToManyField(related_name='ignoreU', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='groupprofile',
            name='picture',
            field=models.ImageField(default=b'picture/gdefault.gif', upload_to=b'picture/', blank=True, help_text=b'Dieses Bild wird auf der Gruppenseite zu sehen sein!', verbose_name=b'Gruppenbild'),
        ),
    ]
