# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2017-04-11 22:45
from __future__ import unicode_literals

from django.db import migrations, models
import messagegenerator.models


class Migration(migrations.Migration):

    dependencies = [
        ('messagegenerator', '0004_auto_20170403_2125'),
    ]

    operations = [
        migrations.AddField(
            model_name='practitioner',
            name='on_call',
            field=models.BooleanField(default=messagegenerator.models.f),
        ),
    ]
