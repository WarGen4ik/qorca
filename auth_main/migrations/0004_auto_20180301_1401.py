# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-01 14:01
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth_main', '0003_auto_20180301_1350'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='club',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='is_coach',
        ),
        migrations.AddField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
