from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('readers/', views.readers_list, name='readers_list'),
    path('add/', views.add_book, name='add_book'),
    path('delete/<int:pk>/', views.delete_book, name='delete_book'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('ajax-book-list/', views.ajax_book_list, name='ajax_book_list'),
    path('staff-login/', views.staff_login_view, name='staff_login'),  # 👈 новый маршрут
    path('login/', views.login_choice, name='login_choice'),           # 👈 главная страница
    path('fetch-cover/', views.fetch_cover, name='fetch_cover'),
    path('ajax-reader-search/', views.ajax_reader_search, name='ajax_reader_search'),
    path('reader-login/', views.reader_login_view, name='reader_login'),
    path('reader-register/', views.reader_register_view, name='reader_register'),
    path('reader-catalog/', views.reader_catalog, name='reader_catalog'),
    path('ajax/book-search/', views.ajax_book_search, name='ajax_book_search'),
    path('readers/delete/<str:telegram_username>/', views.delete_reader, name='delete_reader'),
    path('issue/', views.book_issue_view, name='book_issue'),
    path('issue/add/', views.add_book_issue, name='add_book_issue'),

    path('issue/search/', views.ajax_issue_search, name='ajax_issue_search'),
    path('issue/delete/<int:pk>/', views.delete_issue, name='delete_issue')






]
