# resonators/urls.py

from django.urls import path, reverse_lazy # <-- Pastikan reverse_lazy diimport
from django.views.generic.base import RedirectView # <-- Import RedirectView ini
from . import views

urlpatterns = [
    # Tambahkan baris ini. Ini akan menangani /resonator/
    # dan mengarahkannya ke halaman detail karakter default.
    # GANTI 'Aalto' dengan nama karakter yang valid dari database Anda.
    path('', RedirectView.as_view(url=reverse_lazy('resonator_detail', kwargs={'character_name': 'Aalto'}), permanent=False), name='resonator_default'),

    # Ini adalah URL untuk detail karakter spesifik, tetap sama
    path('characters/<str:character_name>/', views.resonators, name='resonator_detail'),
]