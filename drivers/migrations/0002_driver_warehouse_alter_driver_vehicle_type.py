# Generated by Django 5.2 on 2025-05-09 14:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drivers', '0001_initial'),
        ('warehouses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='warehouse',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='warehouses.warehouse'),
        ),
        migrations.AlterField(
            model_name='driver',
            name='vehicle_type',
            field=models.CharField(max_length=100),
        ),
    ]
