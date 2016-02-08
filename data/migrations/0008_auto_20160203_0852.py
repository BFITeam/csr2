# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-03 14:52
from __future__ import unicode_literals

import data.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0007_auto_20160202_1434'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='address',
            new_name='street',
        ),
        migrations.AddField(
            model_name='task',
            name='citystate',
            field=models.CharField(max_length=512, null=True, verbose_name=b'City, State'),
        ),
        migrations.AlterField(
            model_name='task',
            name='timestarted',
            field=models.DateTimeField(default=data.models.get_now),
        ),
    ]