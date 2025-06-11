from django.contrib import admin
from django.urls import path, include # Pastikan 'include' diimpor
from django.conf import settings     # Import settings (untuk DEBUG)
from django.conf.urls.static import static # Import static helper (untuk development)

from . import views as main_views     # Impor views dari aplikasi utama (untuk halaman home)

urlpatterns = [
    path('admin/', admin.site.urls), # URL untuk halaman admin Django
    
    path('', main_views.home, name='home'),
    path('', include('resonators.urls')),
    path('', include('build.urls')),
    path('', include('weapon.urls')),
    path('', include('echo.urls')),
    path('dashboard/', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Tambahkan juga ini untuk memastikan static files terlayani (jika ada)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 