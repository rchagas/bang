# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-06 18:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_group_secret_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='email',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
