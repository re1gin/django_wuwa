# build_app/urls.py
from django.urls import path
from . import views 

app_name = 'build'

urlpatterns = [
    path('add/', views.add_build, name='add_build'),
    path('add/success/', views.add_build, name='build_success'),
     path('<str:character_name>/', views.character_builder_view, name='character_builder'),
    # URL baru untuk halaman perbandingan
    path('<str:character_name>/compare/', views.compare_build_view, name='compare_build'),
]
