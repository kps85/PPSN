# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twittur', '0004_auto_20150522_0033'),
    ]

    operations = [
        migrations.CreateModel(
            name='ToUser',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('toUser_from', models.ForeignKey(related_name='toUser_from', to='twittur.User')),
                ('toUser_message', models.ForeignKey(to='twittur.Message')),
                ('toUser_to', models.ForeignKey(related_name='toUser_to', to='twittur.User')),
            ],
        ),
        migrations.RenameField(
            model_name='togroup',
            old_name='togroup_group',
            new_name='toGroup_group',
        ),
        migrations.RenameField(
            model_name='togroup',
            old_name='togroup_message',
            new_name='toGroup_message',
        ),
        migrations.RenameField(
            model_name='togroup',
            old_name='togroup_user',
            new_name='toGroup_user',
        ),
        migrations.AlterField(
            model_name='favorite',
            name='favorite_from_self',
            field=models.ForeignKey(related_name='favorite_from', to='twittur.User'),
        ),
        migrations.AlterField(
            model_name='favorite',
            name='favorite_to_user',
            field=models.ForeignKey(related_name='favorite_to', to='twittur.User'),
        ),
    ]
