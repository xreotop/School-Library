from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from books import views  # 👈 добавляем views из приложения books

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_choice, name='home'),  # 👈 маршрут для главной страницы
    path('books/', include('books.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
