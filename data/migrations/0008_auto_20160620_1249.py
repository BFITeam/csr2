# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-20 17:49
from __future__ import unicode_literals

import data.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0007_auto_20160620_1242'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='readable',
            field=models.IntegerField(choices=[(1, b'Yes'), (0, b'No')], null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='timestarted',
            field=models.DateTimeField(default=data.models.get_now),
        ),
    ]
