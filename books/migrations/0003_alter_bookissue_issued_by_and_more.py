# Generated by Django 5.1.7 on 2025-04-13 13:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_reader_chat_id_alter_bookissue_return_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookissue',
            name='issued_by',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Сотрудник'),
        ),
        migrations.AlterField(
            model_name='bookissue',
            name='return_date',
            field=models.DateField(default=datetime.datetime(2025, 4, 27, 13, 23, 19, 133068, tzinfo=datetime.timezone.utc)),
        ),
    ]
