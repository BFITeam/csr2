# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-24 15:39
from __future__ import unicode_literals

import data.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0015_auto_20160624_0958'),
    ]

    operations = [
        migrations.RenameField(
            model_name='image',
            old_name='batch',
            new_name='blur',
        ),
        migrations.RenameField(
            model_name='mturker',
            old_name='batch',
            new_name='blur',
        ),
        migrations.AlterField(
            model_name='mturker',
            name='start',
            field=models.DateTimeField(default=data.models.get_now),
        ),
        migrations.AlterField(
            model_name='task',
            name='timestarted',
            field=models.DateTimeField(default=data.models.get_now),
        ),
    ]
