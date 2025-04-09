from django.core.management.base import BaseCommand
from django.utils import timezone
from books.models import BookIssue
from books.utils import send_telegram_message
from datetime import timedelta

class Command(BaseCommand):
    help = 'Напоминания о возврате книг'

    def handle(self, *args, **kwargs):
        reminder_date = timezone.now().date() + timedelta(days=3)
        issues = BookIssue.objects.filter(return_date=reminder_date)

        for issue in issues:
            if issue.reader.chat_id:
                send_telegram_message(
                    issue.reader.chat_id,
                    f"⏰ Напоминаем, что книга «{issue.book.title}» должна быть возвращена через 3 дня (до {issue.return_date})."
                )

        self.stdout.write(self.style.SUCCESS("✅ Напоминания отправлены!"))
