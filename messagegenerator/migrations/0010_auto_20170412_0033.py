# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2017-04-12 00:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messagegenerator', '0009_ordermessage_taken_by_doctor'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordermessage',
            name='critical',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='practitioner',
            name='location',
            field=models.IntegerField(default=2),
        ),
    ]
