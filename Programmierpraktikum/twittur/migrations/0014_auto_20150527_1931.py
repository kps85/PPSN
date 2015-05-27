# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0013_auto_20150527_1518'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='id',
            field=models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False, default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
    ]
