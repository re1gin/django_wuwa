# myproject/urls.py (ini adalah urls.py utama)

from django.contrib import admin
from django.urls import path, include
from . import views # Asumsi views.py untuk home ada di folder proyek utama

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('add/', include('add_character.urls')), # Jika ini aplikasi untuk menambah karakter
    path('resonator/', include('resonators.urls')), # Ini yang penting untuk aplikasi resonators
]