# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-15 20:46
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=256)),
                ('downloaded_at', models.DateTimeField(editable=False)),
                ('ingested_at', models.DateTimeField(editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=256)),
                ('value', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Tree',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('ingest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Dataset')),
            ],
        ),
        migrations.AddField(
            model_name='property',
            name='tree',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Tree'),
        ),
    ]