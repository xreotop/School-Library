from django.urls import path
from . import views
from .views import register_chat
from books.views import telegram_webhook

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('readers/', views.readers_list, name='readers_list'),
    path('add/', views.add_book, name='add_book'),
    path('delete/<int:pk>/', views.delete_book, name='delete_book'),

    path('ajax-book-list/', views.ajax_book_list, name='ajax_book_list'),
    path('staff-login/', views.staff_login, name='staff_login'),  #  новый маршрут
    path('verify-pin/', views.verify_pin, name='verify_pin'),
    path('staff-logout/', views.staff_logout, name='staff_logout'),
    path('SchoolBookDate_bot/', telegram_webhook),
    path('reader/edit/<int:reader_id>/', views.edit_reader, name='edit_reader'),
    path('login/', views.login_choice, name='login_choice'),           #  главная страница
    path('fetch-cover/', views.fetch_cover, name='fetch_cover'),
    path('ajax-reader-search/', views.ajax_reader_search, name='ajax_reader_search'),
    path('reader-login/', views.reader_login_view, name='reader_login'),
    path('reader-register/', views.reader_register_view, name='reader_register'),
    path('reader-catalog/', views.reader_catalog, name='reader_catalog'),
    path('ajax/book-search/', views.ajax_book_search, name='ajax_book_search'),
    path('readers/delete/<int:reader_id>/', views.delete_reader, name='delete_reader'),
    path('readers/add/', views.add_reader, name='add_reader'),


    path('issue/', views.book_issue_view, name='book_issue'),
    path('issue/add/', views.add_book_issue, name='add_book_issue'),

    path('issue/search/', views.ajax_issue_search, name='ajax_issue_search'),
    path('issues/<int:pk>/return/', views.return_book_issue, name='return_book_issue'),
    path('register-chat/', views.register_chat, name='register_chat'),
    path('issue/overdue/search/', views.ajax_overdue_search, name='ajax_overdue_search'),
    path('issue/overdue-partial/', views.overdue_issues_partial, name='overdue_issues_partial'),
    path('reader/feedback/', views.submit_feedback, name='submit_feedback'),
    path('book/reaction/', views.book_reaction, name='book_reaction'),
    path('book/review/', views.submit_review, name='submit_review'),
    path('book/<int:book_id>/reviews/', views.get_book_reviews, name='book_reviews'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('statistics/delete/<int:feedback_id>/', views.delete_feedback, name='delete_feedback'),
    path('admin/delete-all-feedback/', views.delete_all_feedback, name='delete_all_feedback'),
    path('write-off-by-inventory/', views.write_off_book_by_inventory, name='write_off_by_inventory'),
    path('print-write-off-manual/', views.print_write_off_manual, name='print_write_off_manual'),
    path('get-available-instances/', views.get_available_instances, name='get_available_instances'),
    path('readers/<int:reader_id>/issues/', views.reader_issues, name='reader_issues'),
    path('issues/history/', views.ajax_history, name='ajax_history'),
    path('issues/clear-history/', views.clear_history, name='clear_history'),
]
