from django.shortcuts import redirect


# декоратор
def staff_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.session.get('is_staff_logged_in'):
            return view_func(request, *args, **kwargs)
        return redirect('staff_login')
    return _wrapped_view


@staff_required
def book_list(request):
    search_type = request.GET.get('type', 'title')
    query = request.GET.get('q', '')

    books = Book.objects.prefetch_related('instances').all()
    if query:
        if search_type == 'title':
            books = books.filter(title__icontains=query)
        elif search_type == 'author':
            books = books.filter(author__icontains=query)
        elif search_type == 'year':
            try:
                books = books.filter(year=int(query))
            except ValueError:
                books = books.none()
        elif search_type == 'isbn':
            books = books.filter(isbn__icontains=query)

    return render(request, 'books/book_list.html', {
        'books': books,
        'query': query,
        'search_type': search_type
    })

from .forms import BookForm
import requests
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from urllib.parse import urlparse
from unidecode import unidecode
from django.core.files.base import ContentFile
from .models import Book, BookInstance
from .forms import BookForm
import os



def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            cover_url = request.POST.get('cover_auto')
            quantity = int(request.POST.get('quantity', 1))

            # Обработка обложки
            if cover_url and not request.FILES.get('cover_image'):
                try:
                    response = requests.get(cover_url)
                    if response.status_code == 200:
                        parsed = urlparse(cover_url)
                        ext = os.path.splitext(parsed.path)[1] or '.jpg'
                        safe_title = unidecode(book.title[:30]).replace(' ', '_')
                        filename = f"auto_cover_{safe_title}{ext}"
                        book.cover_image.save(filename, ContentFile(response.content), save=False)
                except Exception as e:
                    return JsonResponse({'success': False, 'errors': {'cover_image': ['Ошибка при загрузке обложки.']}}, status=400)
            elif request.FILES.get('cover_image'):
                book.cover_image = request.FILES['cover_image']

            try:
                book.save()
                # Генерация экземпляров с уникальными инвентарными номерами
                max_number = BookInstance.objects.filter(book__inventory_prefix=book.inventory_prefix).count()
                for i in range(quantity):
                    instance = BookInstance(book=book)
                    instance.save()  # Генерация inventory_number произойдёт в save() метода BookInstance
            except Exception as e:
                return JsonResponse({'success': False, 'errors': {'general': [f'Ошибка при сохранении книги: {str(e)}']}}, status=400)

            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return redirect('book_list')

def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    book.delete()
    return redirect('book_list')


def write_off_book_by_inventory(request):
    if request.method == 'POST':
        inventory_number = request.POST.get('inventory_number')
        reason = request.POST.get('reason', '')
        try:
            book_instance = BookInstance.objects.get(inventory_number=inventory_number)
            book = book_instance.book
            book_instance.delete()
            if book.instances.count() == 0:
                book.delete()
            context = {
                'book': book,
                'book_instance': book_instance,
                'write_off_date': timezone.now().date(),
                'reason': reason,
            }
            html = render_to_string('books/write_off_print.html', context)
            return JsonResponse({
                'success': True,
                'message': 'Книга успешно списана.',
                'print_html': html
            })
        except BookInstance.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Инвентарный номер не найден.'
            })
    return render(request, 'books/book_list.html')
def print_write_off_manual(request):
    if request.method == 'POST':
        inventory_number = request.POST.get('inventory_number')
        reason = request.POST.get('reason', '')
        try:
            book_instance = BookInstance.objects.get(inventory_number=inventory_number)
            context = {
                'book': book_instance.book,
                'book_instance': book_instance,
                'write_off_date': timezone.now().date(),
                'reason': reason,
            }
            html = render_to_string('books/write_off_print.html', context)
            response = HttpResponse(html)
            response['Content-Disposition'] = f'attachment; filename="act_write_off_{inventory_number}.html"'
            response['Content-Type'] = 'text/html'
            return response
        except BookInstance.DoesNotExist:
            return redirect('book_list')
    return redirect('book_list')



def ajax_book_list(request):
    search_type = request.GET.get('type', 'title')
    query = request.GET.get('q', '')

    books = Book.objects.prefetch_related('instances').all()
    if query:
        if search_type == 'title':
            books = books.filter(title__icontains=query)
        elif search_type == 'author':
            books = books.filter(author__icontains=query)
        elif search_type == 'year':
            try:
                books = books.filter(year=int(query))
            except ValueError:
                books = books.none()
        elif search_type == 'isbn':
            books = books.filter(isbn__icontains=query)

    html = render_to_string('books/book_cards.html', {'books': books})
    return JsonResponse({'html': html})
from django.shortcuts import render, redirect
from django.conf import settings


def login_choice(request):
    return render(request, 'books/login_choice.html')


def staff_login(request):
    return render(request, 'books/staff_login.html')


def verify_pin(request):
    if request.method == 'POST':
        pin = request.POST.get('pin')
        if pin == settings.STAFF_PIN:
            request.session['is_staff_logged_in'] = True  #  флаг авторизации
            return redirect('book_list')
        else:
            return render(request, 'books/staff_login.html', {'error': 'Неверный пин-код'})
    return redirect('staff_login')


def staff_logout(request):
    request.session.flush()
    return redirect('staff_login')


from django.shortcuts import render, redirect

import requests


def fetch_cover(request):
    title = request.GET.get('title', '')
    if not title:
        return JsonResponse({'image_urls': [], 'authors': []})

    try:
        response = requests.get(
            'https://www.googleapis.com/books/v1/volumes',
            params={'q': title, 'maxResults': 6},
            timeout=5
        )
        data = response.json()
        items = data.get('items', [])
        image_urls = []
        authors_set = set()

        for item in items:
            volume_info = item.get('volumeInfo', {})
            for author in volume_info.get('authors', []):
                authors_set.add(author)
            image_links = volume_info.get('imageLinks', {})
            for key in ['thumbnail']:
                url = image_links.get(key)
                if url and url not in image_urls:
                    if url.startswith('http://'):
                        url = url.replace('http://', 'https://')
                    image_urls.append(url)

        return JsonResponse({
            'image_urls': image_urls,
            'authors': list(authors_set)
        })
    except Exception as e:
        print("Ошибка при получении обложек:", e)

    return JsonResponse({'image_urls': [], 'authors': []})


from .models import Reader


# читатели список


@staff_required
def readers_list(request):
    readers = Reader.objects.all()
    return render(request, 'books/readers_list.html', {'readers': readers})

from django.template.loader import render_to_string
from django.http import JsonResponse
from .models import Reader
from django.db.models import Q

from django.shortcuts import render
from django.http import JsonResponse
from .models import Reader


@staff_required
def ajax_reader_search(request):
    query = request.GET.get('q', '')
    readers = Reader.objects.filter(
        last_name__icontains=query
    ) | Reader.objects.filter(
        first_name__icontains=query
    )
    html = render(request, 'books/partials/reader_rows.html', {'readers': readers}).content.decode('utf-8')
    return JsonResponse({'html': html})


from django.shortcuts import get_object_or_404, redirect


def delete_reader(request, reader_id):
    reader = get_object_or_404(Reader, id=reader_id)
    if request.method == 'POST':
        reader.delete()
    return redirect('readers_list')


from django.views.decorators.csrf import csrf_protect
from django.shortcuts import redirect
from django.contrib import messages
from .models import Reader

from django.views.decorators.csrf import csrf_protect
from django.shortcuts import redirect
from django.contrib import messages
from .models import Reader

@csrf_protect
@staff_required
def add_reader(request):
    if request.method == 'POST':
        registration_year = request.POST.get('registration_year')
        last_name = request.POST.get('last_name')
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name', '').strip() or None
        birth_year = request.POST.get('birth_year', '').strip() or None
        address = request.POST.get('address', '').strip() or None
        phone = request.POST.get('phone', '').strip() or None
        school_class = request.POST.get('school_class')
        telegram = request.POST.get('telegram_username', '').strip() or None
        password = request.POST.get('password', '')

        # Проверка Telegram-логина
        if telegram and not telegram.startswith('@'):
            return JsonResponse({'success': False, 'message': 'Telegram логин должен начинаться с символа @'})

        # Проверка обязательных полей
        if not all([registration_year, last_name, first_name, school_class]):
            return JsonResponse({'success': False, 'message': 'Заполните все обязательные поля'})

        # Проверка года регистрации
        try:
            registration_year = int(registration_year)
            if registration_year < 1900:
                return JsonResponse({'success': False, 'message': 'Год регистрации должен быть больше 1900'})
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Год регистрации должен быть числом'})

        # Проверка года рождения (если указан)
        if birth_year:
            try:
                birth_year = int(birth_year)
                if birth_year < 1900:
                    return JsonResponse({'success': False, 'message': 'Год рождения должен быть больше 1900'})
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Год рождения должен быть числом'})
        else:
            birth_year = None

        try:
            reader = Reader(
                registration_year=registration_year,
                last_name=last_name,
                first_name=first_name,
                middle_name=middle_name,
                birth_year=birth_year,
                address=address,
                phone=phone,
                school_class=school_class,
                telegram_username=telegram,
            )
            reader.set_password(password or '')
            reader.save()
            return JsonResponse({'success': True, 'message': 'Читатель успешно добавлен'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Ошибка при добавлении читателя: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Метод не поддерживается'})  # Для не-POST запросов



from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from .models import Reader

@csrf_protect
@staff_required
def edit_reader(request, reader_id):
    reader = get_object_or_404(Reader, id=reader_id)
    if request.method == 'POST':
        registration_year = request.POST.get('registration_year')
        last_name = request.POST.get('last_name')
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name', '').strip() or None
        birth_year = request.POST.get('birth_year', '').strip() or None
        address = request.POST.get('address', '').strip() or None
        phone = request.POST.get('phone', '').strip() or None
        school_class = request.POST.get('school_class')
        telegram = request.POST.get('telegram_username', '').strip() or None
        password = request.POST.get('password', '')

        # Проверка Telegram-логина
        if telegram and not telegram.startswith('@'):
            return JsonResponse({'success': False, 'message': 'Telegram логин должен начинаться с символа @'})

        # Проверка обязательных полей
        if not all([registration_year, last_name, first_name, school_class]):
            return JsonResponse({'success': False, 'message': 'Заполните все обязательные поля'})

        # Проверка года регистрации
        try:
            registration_year = int(registration_year)
            if registration_year < 1900:
                return JsonResponse({'success': False, 'message': 'Год регистрации должен быть больше 1900'})
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Год регистрации должен быть числом'})

        # Проверка года рождения (если указан)
        if birth_year:
            try:
                birth_year = int(birth_year)
                if birth_year < 1900:
                    return JsonResponse({'success': False, 'message': 'Год рождения должен быть больше 1900'})
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Год рождения должен быть числом'})
        else:
            birth_year = None

        try:
            # Обновляем данные читателя
            reader.registration_year = registration_year
            reader.last_name = last_name
            reader.first_name = first_name
            reader.middle_name = middle_name
            reader.birth_year = birth_year
            reader.address = address
            reader.phone = phone
            reader.school_class = school_class
            reader.telegram_username = telegram
            if password:
                reader.set_password(password)
            reader.save()
            return JsonResponse({'success': True, 'message': 'Читатель успешно обновлён'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Ошибка при обновлении читателя: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Метод не поддерживается'})  # Для не-POST запросов

#Информация о выданных книгах


def reader_issues(request, reader_id):
    reader = get_object_or_404(Reader, id=reader_id)
    issues = BookIssue.objects.filter(reader=reader).select_related('book')
    issues_data = [
        {
            'book_title': issue.book.title,
            'inventory_number': issue.inventory_number,
            'issue_date': issue.issue_date.strftime('%Y-%m-%d'),
            'return_date': issue.return_date.strftime('%Y-%m-%d') if issue.return_date else None,
            'returned_date': issue.returned_date.strftime('%Y-%m-%d') if issue.returned_date else None,
            'is_returned': issue.is_returned,
        }
        for issue in issues
    ]
    return JsonResponse({
        'success': True,
        'issues': issues_data,
    })

@staff_required
def book_issue_view(request):
    issues = BookIssue.objects.filter(is_returned=False).select_related('reader', 'book').all()
    readers = Reader.objects.all()
    books = Book.objects.all()
    return render(request, 'books/book_issue.html', {
        'issues': issues,
        'readers': readers,
        'books': books
    })
def clear_history(request):
    if request.method == 'POST':
        BookIssue.objects.filter(is_returned=True).delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'История очищена.'})
        messages.success(request, "История выдач очищена.")
        return redirect('book_issue')
    return redirect('book_issue')

def ajax_history(request):
    query = request.GET.get('q', '').strip()
    history_issues = BookIssue.objects.filter(is_returned=True).select_related('reader', 'book').annotate(
        full_name=Concat(
            'reader__last_name', Value(' '),
            'reader__first_name', Value(' '),
            'reader__middle_name', output_field=CharField()
        )
    )
    if query:
        history_issues = history_issues.filter(full_name__icontains=query)
    html = render_to_string('books/partials/history_rows.html', {'history_issues': history_issues})
    return JsonResponse({'html': html})
from django.contrib import messages

from django.views.decorators.csrf import csrf_protect

@csrf_protect
def add_book_issue(request):
    if request.method == 'POST':
        reader_id = request.POST.get('reader_id')
        telegram_username = request.POST.get('telegram_username', '').strip() or None
        book_id = request.POST.get('book_id')
        inventory_number = request.POST.get('inventory_number')
        issued_by = request.POST.get('issued_by', '').strip() or None

        try:
            reader = Reader.objects.get(id=reader_id)
        except Reader.DoesNotExist:
            messages.error(request, "Читатель не найден.")
            return redirect('book_issue')

        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            messages.error(request, "Книга не найдена.")
            return redirect('book_issue')

        if inventory_number:
            try:
                BookInstance.objects.get(book=book, inventory_number=inventory_number)
            except BookInstance.DoesNotExist:
                messages.error(request, "Инвентарный номер не найден для этой книги.")
                return redirect('book_issue')

            if BookIssue.objects.filter(book=book, inventory_number=inventory_number, is_returned=False).exists():
                messages.error(request, "Этот экземпляр книги уже выдан.")
                return redirect('book_issue')

        issue = BookIssue(
            reader=reader,
            book=book,
            inventory_number=inventory_number,
            issued_by=issued_by,
            issue_date=timezone.now().date(),
            return_date=timezone.now().date() + timezone.timedelta(days=14)
        )
        issue.save()
        messages.success(request, "Книга успешно выдана.")
    return redirect('book_issue')
def ajax_issue_search(request):
    query = request.GET.get('q', '').strip()
    issues = BookIssue.objects.filter(is_returned=False).select_related('reader', 'book').annotate(
        full_name=Concat(
            'reader__last_name', Value(' '),
            'reader__first_name', Value(' '),
            'reader__middle_name', output_field=CharField()
        )
    )
    if query:
        issues = issues.filter(full_name__icontains=query)
    html = render_to_string('books/partials/issue_rows.html', {'issues': issues})
    return JsonResponse({'html': html})

def return_book_issue(request, pk):
    if request.method == 'POST':
        issue = get_object_or_404(BookIssue, pk=pk)
        issue.returned_date = timezone.now().date()
        issue.is_returned = True
        issue.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Книга успешно возвращена.',
                'issue': {
                    'id': issue.pk,
                    'telegram_username': issue.reader.telegram_username or '—',
                    'full_name': f"{issue.reader.last_name} {issue.reader.first_name} {issue.reader.middle_name or ''}",
                    'book_title': issue.book.title,
                    'inventory_number': issue.inventory_number or '—',
                    'issued_by': issue.issued_by or '—',
                    'issue_date': issue.issue_date.strftime('%Y-%m-%d'),
                    'return_date': issue.return_date.strftime('%Y-%m-%d'),
                    'returned_date': issue.returned_date.strftime('%Y-%m-%d'),
                    'status': 'Возвращена'
                }
            })
        messages.success(request, "Книга успешно возвращена.")
        return redirect('book_issue')
    return redirect('book_issue')


from django.db.models.functions import Concat
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q, Value, CharField
from django.db.models.functions import Concat
from django.utils import timezone
from .models import BookIssue, Reader, Book, BookInstance
def ajax_overdue_search(request):
    query = request.GET.get('q', '').strip()
    today = timezone.now().date()
    overdue_issues = BookIssue.objects.filter(
        return_date__lt=today,
        is_returned=False
    ).select_related('reader', 'book').annotate(
        full_name=Concat(
            'reader__last_name', Value(' '),
            'reader__first_name', Value(' '),
            'reader__middle_name', output_field=CharField()
        )
    )
    if query:
        overdue_issues = overdue_issues.filter(full_name__icontains=query)
    html = render_to_string('books/partials/overdue_rows.html', {'overdue_issues': overdue_issues})
    return JsonResponse({'html': html})
def overdue_issues_partial(request):
    today = timezone.now().date()
    overdue_issues = BookIssue.objects.filter(
        return_date__lt=today,
        is_returned=False
    ).select_related('reader', 'book')
    html = render_to_string('books/partials/overdue_rows.html', {'overdue_issues': overdue_issues})
    return JsonResponse({'html': html})
def get_available_instances(request):
    book_id = request.GET.get('book_id')
    instances = BookInstance.objects.filter(
        book__id=book_id
    ).exclude(
        inventory_number__in=BookIssue.objects.filter(book__id=book_id).values('inventory_number')
    ).values('inventory_number')
    return JsonResponse({'instances': list(instances)})


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


from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Reader

from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Reader

def reader_register_view(request):
    if request.method == 'POST':
        registration_year = 2025  # Текущий год
        last_name = request.POST.get('last_name')
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name', '').strip() or None
        birth_year = request.POST.get('birth_year', '').strip() or None
        address = request.POST.get('address', '').strip() or None
        phone = request.POST.get('phone', '').strip() or None
        school_class = request.POST.get('school_class')
        telegram = request.POST.get('telegram_username')
        password = request.POST.get('password')

        if not all([last_name, first_name, school_class, telegram, password]):
            messages.error(request, "Заполните все обязательные поля")
            return render(request, 'books/reader_login.html')

        if not telegram.startswith('@'):
            messages.error(request, "Telegram должен начинаться с @")
            return render(request, 'books/reader_login.html')

        if Reader.objects.filter(telegram_username=telegram).exists():
            messages.error(request, "Пользователь с таким Telegram уже зарегистрирован.")
            return render(request, 'books/reader_login.html')

        try:
            if birth_year:
                birth_year = int(birth_year)
                if birth_year < 1900:
                    messages.error(request, "Год рождения должен быть больше 1900")
                    return render(request, 'books/reader_login.html')
            else:
                birth_year = None
        except ValueError:
            messages.error(request, "Год рождения должен быть числом")
            return render(request, 'books/reader_login.html')

        reader = Reader(
            registration_year=registration_year,
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name,
            birth_year=birth_year,
            address=address,
            phone=phone,
            school_class=school_class,
            telegram_username=telegram,
        )
        reader.set_password(password)
        reader.save()

        messages.success(request, "Регистрация успешна. Теперь войдите.")
        return redirect('reader_login')

    return render(request, 'books/reader_login.html')

def reader_catalog(request):
    reader_id = request.session.get('reader_id')

    if not reader_id:
        return redirect('reader_login')

    # Проверяем, существует ли читатель
    try:
        reader = Reader.objects.get(id=reader_id)
    except Reader.DoesNotExist:
        request.session.flush()
        return redirect('reader_login')

    # Получаем выданные книги для читателя
    issued_books = BookIssue.objects.filter(reader=reader, is_returned=False).select_related('book')
    # Получаем историю возвращённых книг
    returned_books = BookIssue.objects.filter(reader=reader, is_returned=True).select_related('book')

    # Передаём данные в шаблон
    return render(request, 'books/reader_catalog.html', {
        'books': Book.objects.all(),
        'reader': reader,
        'issued_books': issued_books,
        'returned_books': returned_books,
    })

from django.http import JsonResponse
from django.db.models import Q, Count
from .models import Book, BookFeedback


def ajax_book_search(request):
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'title')  # По умолчанию поиск по названию
    books = Book.objects.all()

    if query:
        if search_type == 'title':
            books = books.filter(title__icontains=query)
        elif search_type == 'author':
            books = books.filter(author__icontains=query)
        elif search_type == 'year':
            try:
                year = int(query)
                books = books.filter(year=year)
            except ValueError:
                books = books.none()  # Если год не число, возвращаем пустой результат
        elif search_type == 'isbn':
            books = books.filter(isbn__iexact=query)

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
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        try:
            body = request.body.decode('utf-8')
            data = json.loads(body)
            message = data.get('message', {})
            chat = message.get('chat', {})
            text = message.get('text', '')
            username = chat.get('username') # Получаем username и chat_id пользователя
            chat_id = chat.get('id')
            # Если пользователь отправил команду /start и есть нужные данные
            if text == '/start' and username and chat_id:
                # Ищем пользователя в базе данных по Telegram-логину (с @)
                reader = Reader.objects.filter(telegram_username='@' + username).first()
                if reader:
                    # Привязываем chat_id к найденному пользователю
                    reader.chat_id = chat_id
                    reader.save()
        except Exception:
            pass
    return JsonResponse({'ok': True})
from django.views.decorators.csrf import csrf_exempt
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
import json
from django.template.loader import render_to_string


# отзывы
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
        is_like = request.POST.get('is_like')
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
        if reader_id and book_id and review_text:
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
            except:
                pass
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})



from django.http import JsonResponse
from .models import BookFeedback, Book


from django.http import JsonResponse
from .models import BookFeedback

def get_book_reviews(request, book_id):
    feedbacks = BookFeedback.objects.filter(
        book_id=book_id,
        comment__isnull=False
    ).exclude(comment='').select_related('reader')
    data = [{
        'reader': f"{fb.reader.last_name} {fb.reader.first_name}",
        'comment': fb.comment
    } for fb in feedbacks]

    return JsonResponse({'reviews': data})

# статистика
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


@staff_required
def statistics_view(request):
    total_readers = Reader.objects.count()
    issued_books = BookIssue.objects.filter(return_date__gte=timezone.now().date()).count()
    overdue_books = BookIssue.objects.filter(return_date__lt=timezone.now().date()).count()
    popular_books = Book.objects.annotate(
        likes=Count('bookfeedback', filter=Q(bookfeedback__is_like=True))
    ).order_by('-likes')[:5]
    unpopular_books = Book.objects.annotate(
        dislikes=Count('bookfeedback', filter=Q(bookfeedback__is_like=False))
    ).order_by('-dislikes')[:5]
    all_feedback = BookFeedback.objects.select_related('book', 'reader').exclude(comment="")

    # Подсчёт книг с экземплярами
    books_with_instances = Book.objects.annotate(instance_count=Count('instances', distinct=True)).filter(
        instance_count__gt=0).count()
    total_instances = BookInstance.objects.count()

    return render(request, 'books/statistics.html', {
        'total_instances': total_instances,
        'issued_books': issued_books,
        'overdue_books': overdue_books,
        'total_readers': total_readers,
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


