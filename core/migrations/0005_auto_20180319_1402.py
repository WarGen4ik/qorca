# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-19 14:02
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20180319_1400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competition',
            name='teams',
            field=models.ManyToManyField(null=True, to='core.Team'),
        ),
        migrations.AlterField(
            model_name='competition',
            name='users',
            field=models.ManyToManyField(null=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
