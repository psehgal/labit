# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2017-04-12 21:53
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('messagegenerator', '0022_auto_20170412_1508'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordermessage',
            name='time_claimed',
            field=models.DateTimeField(default=None),
        ),
        migrations.AlterField(
            model_name='ordermessage',
            name='time_ordered',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 12, 21, 53, 50, 117632, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='practitioner',
            name='location',
            field=models.IntegerField(default=2),
        ),
    ]