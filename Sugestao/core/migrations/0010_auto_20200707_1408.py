# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2020-07-07 14:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_sugestao_senha'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sugestao',
            name='senha',
            field=models.CharField(default='*', max_length=8),
        ),
    ]
