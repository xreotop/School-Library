# Generated by Django 5.1.7 on 2025-06-08 05:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0005_remove_book_inventory_number_remove_book_quantity_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookissue',
            name='inventory_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Инвентарный номер'),
        ),
        migrations.AlterField(
            model_name='bookissue',
            name='return_date',
            field=models.DateField(default=datetime.datetime(2025, 6, 22, 5, 58, 57, 15557, tzinfo=datetime.timezone.utc)),
        ),
    ]
