# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0017_auto_20150607_1808'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faq',
            name='author',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='academicDiscipline',
            field=models.CharField(max_length=200, help_text='&Uuml;ber deinen Studiengang wirst Du bestimmten Gruppen zugeordnet.'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='location',
            field=models.CharField(max_length=200, default='None', help_text='Lass Deine Kommilitoninnen Dich finden!'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='studentNumber',
            field=models.CharField(max_length=6, default='000000', help_text='&Uuml;ber deine Matrikel-Nummer kannst Du eindeutig als Student der TU Berlin identifiziert werden.<br>(only numbers, max. 6 chars)'),
        ),
    ]
