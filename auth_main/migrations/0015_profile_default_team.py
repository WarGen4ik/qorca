# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-05-21 16:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_main', '0014_profile_age_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='default_team',
            field=models.CharField(default='', max_length=255, verbose_name='Default team name'),
        ),
    ]
