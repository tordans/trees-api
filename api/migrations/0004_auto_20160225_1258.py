# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-25 12:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20160225_1231'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tree',
            name='current_ingest',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.Ingest'),
        ),
    ]