# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2017-04-12 18:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messagegenerator', '0015_auto_20170412_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='practitioner',
            name='location',
            field=models.IntegerField(default=3),
        ),
    ]