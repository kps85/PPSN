# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0016_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='favorite',
            name='fromUser',
        ),
        migrations.RemoveField(
            model_name='favorite',
            name='toUser',
        ),
        migrations.RemoveField(
            model_name='has',
            name='hashtag',
        ),
        migrations.RemoveField(
            model_name='has',
            name='message',
        ),
        migrations.RemoveField(
            model_name='touser',
            name='message',
        ),
        migrations.RemoveField(
            model_name='touser',
            name='toUser',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='followers',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='academicDiscipline',
            field=models.CharField(help_text=b'&Uuml;ber deinen Studiengang wirst Du bestimmten Gruppen zugeordnet.', max_length=200),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='location',
            field=models.CharField(default=b'None', help_text=b'Lass Deine Kommilitoninnen Dich finden!', max_length=200),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='studentNumber',
            field=models.CharField(default=b'000000', help_text=b'&Uuml;ber deine Matrikel-Nummer kannst Du eindeutig als Student der TU Berlin identifiziert werden.<br>(only numbers, max. 6 chars)', max_length=6),
        ),
        migrations.DeleteModel(
            name='Favorite',
        ),
        migrations.DeleteModel(
            name='Has',
        ),
        migrations.DeleteModel(
            name='ToUser',
        ),
    ]
