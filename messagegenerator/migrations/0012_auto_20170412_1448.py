# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2017-04-12 18:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('messagegenerator', '0011_ordermessage_time_ordered'),
    ]

    operations = [
        # migrations.AddField(
        #     model_name='ordermessage',
        #     name='claiming_practitioner',
        #     field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, to='messagegenerator.Practitioner'),
        # ),
        migrations.AlterField(
            model_name='ordermessage',
            name='time_ordered',
            field=models.DateTimeField(),
        ),
    ]