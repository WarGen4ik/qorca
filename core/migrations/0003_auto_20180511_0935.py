# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-05-11 09:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20180511_0545'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userdistance',
            name='result_time',
        ),
        migrations.RemoveField(
            model_name='userdistance',
            name='time',
        ),
    ]
