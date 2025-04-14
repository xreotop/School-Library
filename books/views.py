
def book_list(request):
    search_type = request.GET.get('type', 'title')
    query = request.GET.get('q', '')

    books = Book.objects.all()
    if query:
        if search_type == 'title':
            books = books.filter(title__icontains=query)
        elif search_type == 'author':
            books = books.filter(author__icontains=query)
        elif search_type == 'year':
            books = books.filter(year__icontains=query)

    return render(request, 'books/book_list.html', {
        'books': books,
        'query': query,
        'search_type': search_type
    })



from .forms import BookForm



import os
from urllib.parse import urlparse
from django.core.files.base import ContentFile
import requests

def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)

            # Автозагрузка обложки, если файл не загружен вручную
            cover_url = request.POST.get('cover_auto')
            if cover_url and not request.FILES.get('cover_image'):
                try:
                    response = requests.get(cover_url)
                    if response.status_code == 200:
                        ext = os.path.splitext(urlparse(cover_url).path)[-1]
                        if not ext:
                            ext = '.jpg'  # по умолчанию
                        filename = f"auto_cover_{book.title[:10].replace(' ', '_')}{ext}"
                        book.cover_image.save(filename, ContentFile(response.content), save=False)
                except Exception as e:
                    print("Ошибка при загрузке обложки:", e)

            book.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False}, status=405)





def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    book.delete()
    return redirect('book_list')


def autocomplete(request):
    term = request.GET.get('term', '')
    search_type = request.GET.get('type', 'title')

    if search_type == 'title':
        suggestions = Book.objects.filter(title__icontains=term).values_list('title', flat=True)
    elif search_type == 'author':
        suggestions = Book.objects.filter(author__icontains=term).values_list('author', flat=True)
    elif search_type == 'year':
        suggestions = Book.objects.filter(year__icontains=term).values_list('year', flat=True)
    else:
        suggestions = []

    return JsonResponse(list(set(suggestions))[:10], safe=False)
from django.template.loader import render_to_string
from django.http import JsonResponse

def ajax_book_list(request):
    search_type = request.GET.get('type', 'title')
    query = request.GET.get('q', '')

    books = Book.objects.all()
    if query:
        if search_type == 'title':
            books = books.filter(title__icontains=query)
        elif search_type == 'author':
            books = books.filter(author__icontains=query)
        elif search_type == 'year':
            books = books.filter(year__icontains=query)

    html = render_to_string('books/book_cards.html', {'books': books})
    return JsonResponse({'html': html})
from django.shortcuts import render, redirect
from django.http import JsonResponse

def login_choice(request):
    return render(request, 'books/login_choice.html')

def staff_login(request):
    return render(request, 'books/staff_login.html')

def verify_pin(request):
    if request.method == 'POST':
        pin = request.POST.get('pin')
        if pin == 'admin1001':
            return redirect('book_list')
        else:
            return render(request, 'books/staff_login.html', {'error': 'Неверный пин-код'})
    return redirect('staff_login')
from django.shortcuts import render, redirect

def staff_login_view(request):
    if request.method == 'POST':
        pin = request.POST.get('pin')
        if pin == 'admin1001':
            return redirect('book_list')  # переход на /books/
        else:
            return render(request, 'books/staff_login.html', {'error': 'Неверный пин-код'})
    return render(request, 'books/staff_login.html')


import requests

def fetch_cover(request):
    title = request.GET.get('title', '')
    if not title:
        return JsonResponse({'image_urls': [], 'author': ''})

    try:
        response = requests.get(
            'https://www.googleapis.com/books/v1/volumes',
            params={'q': title, 'maxResults': 5},
            timeout=5
        )
        data = response.json()
        items = data.get('items', [])
        image_urls = []
        author = ''

        for item in items:
            volume_info = item.get('volumeInfo', {})
            if not author:
                authors = volume_info.get('authors')
                if authors:
                    author = authors[0]
            image_links = volume_info.get('imageLinks', {})
            for key in ['thumbnail', 'smallThumbnail']:
                url = image_links.get(key)
                if url and url not in image_urls:
                    if url.startswith('http://'):
                        url = url.replace('http://', 'https://')
                    image_urls.append(url)

        return JsonResponse({'image_urls': image_urls, 'author': author})
    except Exception as e:
        print("Ошибка при получении обложек:", e)

    return JsonResponse({'image_urls': [], 'author': ''})
from .models import Reader

#читатели список

def readers_list(request):
    readers = Reader.objects.all()
    return render(request, 'books/readers_list.html', {'readers': readers})

def ajax_reader_search(request):
    query = request.GET.get('q', '')
    readers = Reader.objects.filter(full_name__icontains=query)
    html = render_to_string('books/partials/reader_rows.html', {'readers': readers})
    return JsonResponse({'html': html})


from django.shortcuts import get_object_or_404, redirect
def delete_reader(request, reader_id):
    reader = get_object_or_404(Reader, id=reader_id)
    if request.method == 'POST':
        reader.delete()
    return redirect('readers_list')
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import redirect
from .models import Reader

from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import redirect

@csrf_protect
def add_reader(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        telegram = request.POST.get('telegram_username', '').strip() or None
        password = request.POST.get('password', '')

        if telegram and not telegram.startswith('@'):
            return redirect('readers_list')

        if full_name:
            reader = Reader(full_name=full_name, telegram_username=telegram)
            reader.set_password(password or '')  # безопасный хеш
            reader.save()

    return redirect('readers_list')



# reader_login



def reader_login_view(request):
    if request.method == 'POST':
        telegram = request.POST.get('telegram_username')
        password = request.POST.get('password')

        try:
            reader = Reader.objects.get(telegram_username=telegram)
            if reader.check_password(password):
                request.session['reader_id'] = reader.id
                return redirect('reader_catalog')
            else:
                messages.error(request, "Неверный пароль.")
        except Reader.DoesNotExist:
            messages.error(request, "Пользователь не найден.")

    return render(request, 'books/reader_login.html')


from django.contrib import messages

def reader_register_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        telegram = request.POST.get('telegram_username')
        password = request.POST.get('password')

        if not telegram.startswith('@'):
            messages.error(request, "Telegram должен начинаться с @")
            return render(request, 'books/reader_login.html')

        if Reader.objects.filter(telegram_username=telegram).exists():
            messages.error(request, "Пользователь с таким Telegram уже зарегистрирован.")
            return render(request, 'books/reader_login.html')

        reader = Reader(full_name=full_name, telegram_username=telegram)
        reader.set_password(password)  # хешируем
        reader.save()

        messages.success(request, "Регистрация успешна. Теперь войдите.")
        return redirect('reader_login')

    return render(request, 'books/reader_login.html')

from django.shortcuts import render
from django.http import JsonResponse
from .models import Book
from django.db.models import Q

def reader_catalog(request):
    reader_id = request.session.get('reader_id')

    if not reader_id:
        return redirect('reader_login')

    #  Проверяем, существует ли читатель
    try:
        Reader.objects.get(id=reader_id)
    except Reader.DoesNotExist:
        request.session.flush()

        return redirect('reader_login')

    # Если всё ок, показываем каталог
    books = Book.objects.all()
    return render(request, 'books/reader_catalog.html', {'books': books})

from django.http import JsonResponse
from django.db.models import Q, Count
from .models import Book, BookFeedback

def ajax_book_search(request):
    query = request.GET.get('q', '')
    books = Book.objects.all()
    if query:
        books = books.filter(Q(title__icontains=query) | Q(author__icontains=query))

    data = []
    for book in books:
        likes = BookFeedback.objects.filter(book=book, is_like=True).count()
        dislikes = BookFeedback.objects.filter(book=book, is_like=False).count()
        data.append({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'cover_image': book.cover_image.url if book.cover_image else None,
            'likes': likes,
            'dislikes': dislikes,
        })

    return JsonResponse({'books': data})


#  выдача книг
from django.shortcuts import render, redirect
from django.contrib import messages

def book_issue_view(request):
    issues = BookIssue.objects.select_related('reader', 'book').all()
    readers = Reader.objects.all()
    books = Book.objects.all()
    return render(request, 'books/book_issue.html', {
        'issues': issues,
        'readers': readers,
        'books': books
    })

from django.shortcuts import redirect
from django.utils import timezone
from datetime import timedelta
from .models import BookIssue, Reader, Book


from books.utils import send_telegram_message  # если send_telegram_message в utils.py

from django.views.decorators.csrf import csrf_protect
from django.shortcuts import redirect
from django.utils import timezone
from datetime import timedelta
from .models import BookIssue, Reader, Book
from books.utils import send_telegram_message

@csrf_protect
def add_book_issue(request):
    if request.method == 'POST':
        telegram = request.POST.get('telegram_username', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        book_title = request.POST.get('book_title', '').strip()
        staff = request.POST.get('issued_by', '').strip()

        try:
            # Ищем всех по имени
            matching_readers = Reader.objects.filter(full_name=full_name)

            if telegram:
                # Если указан Telegram — ищем по имени + логину
                reader = matching_readers.filter(telegram_username=telegram).first()
            else:
                # Если логин не указан — берём того, у кого логина нет
                reader = matching_readers.filter(telegram_username__isnull=True).first()

            if not reader:
                # Если не удалось найти нужного — возвращаемся
                return redirect('book_issue')

            # Поиск книги
            book = Book.objects.get(title=book_title)

            # Создаём запись
            issue = BookIssue.objects.create(
                reader=reader,
                book=book,
                issued_by=staff,
                issue_date=timezone.now().date(),
                return_date=timezone.now().date() + timedelta(days=14)
            )

            # Уведомляем, если есть chat_id
            if reader.chat_id:
                send_telegram_message(
                    reader.chat_id,
                    f"📚 Вам выдана книга: «{book.title}»\n"
                    f"Дата выдачи: {issue.issue_date}\n"
                    f"Дата возврата: {issue.return_date}"
                )

        except Book.DoesNotExist:
            # Можно отобразить сообщение
            pass

    return redirect('book_issue')



from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from books.models import Reader
import json

@csrf_exempt
def register_chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            chat_id = data.get('chat_id')

            if not username or not chat_id:
                return JsonResponse({'error': 'Missing data'}, status=400)

            reader = Reader.objects.filter(telegram_username=username).first()
            if reader:
                reader.chat_id = chat_id
                reader.save()
                return JsonResponse({'message': 'Chat ID registered'}, status=200)
            else:
                return JsonResponse({'error': 'Reader not found'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Only POST allowed'}, status=405)
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from books.models import Reader
import json





# views.py
from django.template.loader import render_to_string
from django.http import JsonResponse

def ajax_issue_search(request):
    query = request.GET.get('q', '')
    issues = BookIssue.objects.filter(reader__full_name__icontains=query)
    html = render_to_string('books/partials/issue_rows.html', {'issues': issues}, request=request)
    return JsonResponse({'html': html})
def delete_issue(request, pk):
    if request.method == 'POST':
        issue = get_object_or_404(BookIssue, pk=pk)
        issue.delete()

    return redirect('book_issue')

from django.utils import timezone
from django.shortcuts import render
from .models import BookIssue

#таблица должников
from django.utils import timezone

def ajax_overdue_search(request):
    query = request.GET.get('q', '')
    today = timezone.now().date()
    overdue_issues = BookIssue.objects.filter(
        return_date__lt=today,
        reader__full_name__icontains=query
    ).select_related('reader', 'book')
    html = render_to_string('books/partials/overdue_rows.html', {'overdue_issues': overdue_issues})
    return JsonResponse({'html': html})
from django.template.loader import render_to_string
from django.http import JsonResponse

def overdue_issues_partial(request):
    today = timezone.now().date()
    overdue_issues = BookIssue.objects.filter(return_date__lt=today)

    html = render_to_string('books/partials/overdue_rows.html', {
        'overdue_issues': overdue_issues
    }, request=request)

    return JsonResponse({'html': html})
#отзывы
from django.http import JsonResponse
from .models import BookFeedback

def get_feedback(request, book_id):
    reader_id = request.session.get('reader_id')
    feedback = BookFeedback.objects.filter(reader_id=reader_id, book_id=book_id).first()
    return JsonResponse({
        'like': feedback.is_like if feedback else None,
        'comment': feedback.comment if feedback else ''
    })
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

@csrf_exempt
def submit_feedback(request):
    if request.method == 'POST':
        reader_id = request.session.get('reader_id')
        book_id = request.POST.get('book_id')
        is_like = request.POST.get('is_like')  # 'like' / 'dislike' / ''
        comment = request.POST.get('comment', '')

        if reader_id and book_id:
            feedback, _ = BookFeedback.objects.update_or_create(
                reader_id=reader_id,
                book_id=book_id,
                defaults={
                    'is_like': True if is_like == 'like' else False if is_like == 'dislike' else None,
                    'comment': comment
                }
            )
            return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Book

@require_POST
def book_reaction(request):
    book_id = request.POST.get('book_id')
    reaction_type = request.POST.get('type')
    reader_id = request.session.get('reader_id')

    if not (book_id and reaction_type and reader_id):
        return JsonResponse({'error': 'Неверные данные'}, status=400)

    try:
        feedback, created = BookFeedback.objects.get_or_create(
            book_id=book_id,
            reader_id=reader_id,
            defaults={'is_like': True if reaction_type == 'like' else False if reaction_type == 'dislike' else None}
        )
        if not created:
            feedback.is_like = True if reaction_type == 'like' else False if reaction_type == 'dislike' else None
            feedback.save()

        return JsonResponse({'status': 'ok'})
    except:
        return JsonResponse({'status': 'error'}, status=400)
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from .models import Book, Reader, BookIssue, BookFeedback

@csrf_exempt
def submit_review(request):
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        review_text = request.POST.get('review')
        reader_id = request.session.get('reader_id')

        if not (reader_id and book_id and review_text):
            return JsonResponse({'error': 'Недостаточно данных'}, status=400)

        try:
            book = Book.objects.get(id=book_id)
            reader = Reader.objects.get(id=reader_id)

            feedback, created = BookFeedback.objects.get_or_create(
                book=book, reader=reader,
                defaults={'comment': review_text}
            )
            if not created:
                feedback.comment = review_text
                feedback.save()

            return JsonResponse({'success': True})
        except (Book.DoesNotExist, Reader.DoesNotExist):
            return JsonResponse({'error': 'Книга или читатель не найдены'}, status=404)

    return JsonResponse({'error': 'Неверный метод'}, status=405)
from django.http import JsonResponse
from .models import BookFeedback, Book

def get_book_reviews(request, book_id):
    feedbacks = BookFeedback.objects.filter(
        book_id=book_id,
        comment__isnull=False
    ).exclude(comment='').select_related('reader')

    data = [{
        'reader': fb.reader.full_name,
        'comment': fb.comment
    } for fb in feedbacks]

    return JsonResponse({'reviews': data})
#статистика
from django.db.models import Count, Q
from .models import Book, BookFeedback, BookIssue



@require_POST
def delete_feedback(request, feedback_id):
    BookFeedback.objects.filter(id=feedback_id).delete()
    return redirect('statistics')


from django.db.models import Count, Q
from .models import Book, BookFeedback, BookIssue

from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count, Q
from .models import Book, BookIssue, BookFeedback, Reader

def statistics_view(request):
    total_books = Book.objects.count()
    total_readers = Reader.objects.count()  # 👈 добавлено
    issued_books = BookIssue.objects.filter(return_date__gte=timezone.now().date()).count()
    overdue_books = BookIssue.objects.filter(return_date__lt=timezone.now().date()).count()

    popular_books = Book.objects.annotate(
        likes=Count('bookfeedback', filter=Q(bookfeedback__is_like=True))
    ).order_by('-likes')[:5]

    unpopular_books = Book.objects.annotate(
        dislikes=Count('bookfeedback', filter=Q(bookfeedback__is_like=False))
    ).order_by('-dislikes')[:5]

    all_feedback = BookFeedback.objects.select_related('book', 'reader').exclude(comment="")

    return render(request, 'books/statistics.html', {
        'total_books': total_books,
        'total_readers': total_readers,  # 👈 передаём в шаблон
        'issued_books': issued_books,
        'overdue_books': overdue_books,
        'popular_books': popular_books,
        'unpopular_books': unpopular_books,
        'all_feedback': all_feedback
    })

from django.views.decorators.http import require_POST
from django.shortcuts import redirect
from .models import BookFeedback

@require_POST
def delete_all_feedback(request):
    # Удаляем только комментарии, оставляя лайки/дизлайки
    BookFeedback.objects.exclude(comment='').update(comment='')
    return redirect('statistics')


