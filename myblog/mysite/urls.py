from django.contrib import admin
from django.urls import path, include # Pastikan 'include' diimpor
from django.conf import settings     # Import settings (untuk DEBUG)
from django.conf.urls.static import static # Import static helper (untuk development)

from . import views as main_views     # Impor views dari aplikasi utama (untuk halaman home)

urlpatterns = [
    path('admin/', admin.site.urls), # URL untuk halaman admin Django
    path('', main_views.home, name='home'),
    path('', include('resonators.urls')),
]