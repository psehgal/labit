# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2017-04-12 00:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messagegenerator', '0008_auto_20170411_2320'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordermessage',
            name='taken_by_doctor',
            field=models.BooleanField(default=False),
        ),
    ]