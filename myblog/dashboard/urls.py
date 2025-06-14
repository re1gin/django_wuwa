# dashboard/urls.py

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('home/', views.home_dashboard, name='home'), # Halaman utama dashboard

    # Builds
    path('builds/', views.build_list, name='build_list'),
    path('builds/add/', views.build_create, name='build_create'),
    path('builds/<int:pk>/', views.build_detail_update, name='build_detail_update'),
    path('builds/<int:pk>/delete/', views.build_delete, name='build_delete'),
]