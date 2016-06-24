# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-24 15:41
from __future__ import unicode_literals

import data.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0016_auto_20160624_1039'),
    ]

    operations = [
        migrations.AddField(
            model_name='mturker',
            name='batch',
            field=models.CharField(blank=True, max_length=128, null=True),
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
