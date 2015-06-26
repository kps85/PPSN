# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0002_message_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupprofile',
            name='password',
            field=models.CharField(blank=True, max_length=128, help_text='Geben Sie ein Passwort zum Beitreten ihrer Gruppe ein. (optional)'),
        ),
        migrations.AlterField(
            model_name='groupprofile',
            name='picture',
            field=models.ImageField(blank=True, verbose_name='Profilbild', upload_to='picture/', default='picture/gdefault.gif', help_text='Geben sie ein Foto ein!'),
        ),
        migrations.AlterField(
            model_name='message',
            name='date',
            field=models.DateTimeField(verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='message',
            name='picture',
            field=models.ImageField(blank=True, upload_to='picture/'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='academicDiscipline',
            field=models.CharField(max_length=200, help_text='&Uuml;ber deinen Studiengang wirst Du bestimmten Gruppen zugeordnet.'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='location',
            field=models.CharField(max_length=200, default='None', help_text='Lass Deine KommilitonInnen Dich finden!'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='picture',
            field=models.ImageField(blank=True, verbose_name='Profilbild', upload_to='picture/', default='picture/default.gif', help_text='Dieses Bild wird auf Deinem Profil (gro&szlig;) und in deinen Nachrichten (klein) angezeigt.'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='studentNumber',
            field=models.CharField(max_length=6, default='000000', help_text='&Uuml;ber deine Matrikel-Nummer kannst Du eindeutig als Student der TU Berlin identifiziert werden.<br>(only numbers, max. 6 chars)'),
        ),
    ]
