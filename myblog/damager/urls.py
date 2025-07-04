# damager/urls.py

from django.urls import path
from . import views

app_name = 'damager' # Ubah nama aplikasi untuk namespace URL

urlpatterns = [
    # URL dinamis untuk menampilkan damage karakter.
    path('<str:name>/', views.character_damage_view, name='character_damage'),
]
