# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2017-04-11 22:49
from __future__ import unicode_literals

from django.db import migrations, models
import messagegenerator.models


class Migration(migrations.Migration):

    dependencies = [
        ('messagegenerator', '0005_practitioner_on_call'),
    ]

    operations = [
        migrations.AddField(
            model_name='practitioner',
            name='location',
            field=models.IntegerField(default=messagegenerator.models.g),
        ),
    ]
