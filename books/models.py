from django.db import models
import os
from django.conf import settings
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    publisher = models.CharField(max_length=100, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        if self.cover_image and os.path.isfile(self.cover_image.path):
            os.remove(self.cover_image.path)
        super().delete(*args, **kwargs)

class Reader(models.Model):
    full_name = models.CharField("Имя и фамилия", max_length=100)
    telegram_username = models.CharField("Telegram", max_length=100)
    chat_id = models.BigIntegerField("Chat ID Telegram", null=True, blank=True)
    password = models.CharField("Пароль", max_length=100)  # Пока храним в открытом виде, позже заменим

    def __str__(self):
        return f"{self.full_name} ({self.telegram_username})"
from django.db import models
from django.utils import timezone
from datetime import timedelta

class BookIssue(models.Model):
    reader = models.ForeignKey('Reader', on_delete=models.CASCADE)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    issued_by = models.CharField("Сотрудник", max_length=100)  # ← это должно быть
    issue_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(default=timezone.now() + timedelta(days=14))

    def __str__(self):
        return f"{self.reader} — {self.book}"

