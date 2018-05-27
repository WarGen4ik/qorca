# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-05-27 12:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_userdistance_pre_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userdistance',
            name='time',
        ),
        migrations.AlterField(
            model_name='userdistance',
            name='pre_time',
            field=models.IntegerField(default=0, verbose_name='Time for distance (miliseconds)'),
        ),
    ]
