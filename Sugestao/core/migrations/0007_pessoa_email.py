# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2020-04-08 14:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_finalizacao'),
    ]

    operations = [
        migrations.AddField(
            model_name='pessoa',
            name='email',
            field=models.CharField(default='ricardo.pimentel@ifto.edu.br', max_length=70),
            preserve_default=False,
        ),
    ]
