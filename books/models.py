from django.db import models
import os


class Book(models.Model):
    FUND_TYPE_CHOICES = [
        ('fiction', 'Художественный'),
        ('educational', 'Учебный'),
        ('reference', 'Справочный'),
    ]
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    publisher = models.CharField(max_length=100, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    isbn = models.CharField(max_length=13, blank=True, null=True)
    inventory_prefix = models.CharField(max_length=20, blank=True, null=True) # префикс экземпляра
    batch_number = models.CharField(max_length=20, blank=True, null=True)  # Номер партии
    inventory_digit = models.CharField(max_length=20, blank=True, null=True)  # Инвентарный номер inventory_digit
    fund_type = models.CharField(max_length=20, choices=FUND_TYPE_CHOICES, default='fiction')
    acquisition_date = models.DateField("Дата поступления", blank=True, null=True)
    acquisition_source = models.CharField("Источник поступления", max_length=200, blank=True, null=True)
    acquisition_price = models.DecimalField("Сумма поступления", max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        if self.cover_image and os.path.isfile(self.cover_image.path):
            os.remove(self.cover_image.path)
        super().delete(*args, **kwargs)

    @property
    def quantity(self):
        return self.instances.count()
class BookInstance(models.Model):
    book = models.ForeignKey(Book, related_name='instances', on_delete=models.CASCADE)
    inventory_number = models.CharField(max_length=50, unique=True, blank=True, null=True) #номер экземпляра

    def save(self, *args, **kwargs):
        if not self.inventory_number and self.book.inventory_prefix:
            max_number = BookInstance.objects.filter(book__inventory_prefix=self.book.inventory_prefix).count()
            self.inventory_number = f"{self.book.inventory_prefix}{max_number + 1}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title} - {self.inventory_number}"
from django.contrib.auth.hashers import make_password, check_password

class Reader(models.Model):
    registration_year = models.IntegerField("Год регистрации")
    last_name = models.CharField("Фамилия", max_length=50)
    first_name = models.CharField("Имя", max_length=50)
    middle_name = models.CharField("Отчество", max_length=50, blank=True, null=True)
    birth_year = models.IntegerField("Год рождения", blank=True, null=True)
    address = models.CharField("Домашний адрес", max_length=200, blank=True, null=True)
    phone = models.CharField("Телефон", max_length=20, blank=True, null=True)
    school_class = models.CharField("Класс", max_length=10)
    telegram_username = models.CharField("Telegram", max_length=100, blank=True, null=True)
    chat_id = models.BigIntegerField("Chat ID Telegram", null=True, blank=True)
    password = models.CharField("Пароль", max_length=128)

    def __str__(self):
        telegram = self.telegram_username if self.telegram_username else 'без Telegram'
        return f"{self.last_name} {self.first_name} {self.middle_name or ''} ({telegram})"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

from django.db import models
from django.utils import timezone
from datetime import timedelta
class BookIssue(models.Model):
    reader = models.ForeignKey('Reader', on_delete=models.CASCADE)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    inventory_number = models.CharField("Инвентарный номер", max_length=50, blank=True, null=True)
    issued_by = models.CharField("Сотрудник", max_length=100, blank=True, null=True)
    issue_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(default=timezone.now() + timedelta(days=14))
    returned_date = models.DateField("Дата возврата", blank=True, null=True)
    is_returned = models.BooleanField("Возвращена", default=False)
    def __str__(self):
        return f"{self.reader} — {self.book} ({self.inventory_number or 'Без инв. номера'})"
class BookFeedback(models.Model):
    reader = models.ForeignKey('Reader', on_delete=models.CASCADE)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    is_like = models.BooleanField(null=True)
    comment = models.TextField("Отзыв", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('reader', 'book')  # Один отзыв на книгу от одного читат
    def __str__(self):
        return f"{self.reader.full_name} -> {self.book.title}"