# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2020-03-03 09:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20200212_1238'),
    ]

    operations = [
        migrations.AddField(
            model_name='sugestao',
            name='titulo',
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
    ]
