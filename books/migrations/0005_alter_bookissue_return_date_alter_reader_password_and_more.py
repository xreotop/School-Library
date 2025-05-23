# Generated by Django 5.1.7 on 2025-04-14 09:21

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0004_alter_bookissue_return_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookissue',
            name='return_date',
            field=models.DateField(default=datetime.datetime(2025, 4, 28, 9, 21, 38, 325354, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='reader',
            name='password',
            field=models.CharField(max_length=128, verbose_name='Пароль'),
        ),
        migrations.CreateModel(
            name='BookFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_like', models.BooleanField(null=True)),
                ('comment', models.TextField(blank=True, verbose_name='Отзыв')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.book')),
                ('reader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.reader')),
            ],
            options={
                'unique_together': {('reader', 'book')},
            },
        ),
    ]
