# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-05-18 16:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20180511_0936'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdistance',
            name='is_finished',
            field=models.BooleanField(default=False, verbose_name='Is registration finished'),
        ),
    ]