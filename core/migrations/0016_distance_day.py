# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-05-07 16:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_competition_is_creating_finished'),
    ]

    operations = [
        migrations.AddField(
            model_name='distance',
            name='day',
            field=models.SmallIntegerField(default=1, verbose_name='Day number'),
            preserve_default=False,
        ),
    ]
