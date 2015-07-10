# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='academicDiscipline2',
            field=models.CharField(default='bla', max_length=200, help_text='&Uuml;ber Ihren Studiengang werden Sie bestimmten Gruppen zugeordnet.'),
        ),
    ]
