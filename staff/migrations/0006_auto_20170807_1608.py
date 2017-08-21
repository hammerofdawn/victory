# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-07 16:08
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('staff', '0005_auto_20170807_1605'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='teamleaders',
        ),
        migrations.AddField(
            model_name='team',
            name='teamleaders',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]