# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-05-07 15:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_competition_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='count_days',
            field=models.SmallIntegerField(default=1, verbose_name='Count days'),
            preserve_default=False,
        ),
    ]
