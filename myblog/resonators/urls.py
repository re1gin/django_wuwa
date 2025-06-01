# resonators/urls.py

from django.urls import path
from . import views # Mengimpor views dari direktori yang sama (resonators/views.py)

app_name = 'resonators' # <--- INI ADALAH NAMESPACE UNTUK APLIKASI INI

urlpatterns = [
    # URL untuk halaman pemilihan karakter (Character Selection)
    # Contoh URL: yourdomain.com/resonators/characters/
    # Nama yang digunakan di template/view: 'resonators:character_selection'
    path('characters/', views.character_selection, name='character_selection'),

    # URL untuk halaman detail karakter
    # Contoh URL: yourdomain.com/resonators/kuro/ atau yourdomain.com/resonators/rover/
    # '<str:character_name>' akan menangkap nama karakter dari URL.
    # Nama yang digunakan di template/view: 'resonators:resonator_detail'
    path('characters/<str:character_name>/', views.resonators, name='resonator_detail'),
]