# dashboard/urls.py

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home_dashboard, name='home'), # Halaman utama dashboard
    # Resonators
    path('resonators/', views.resonator_list, name='resonator_list'),
    path('resonators/add/', views.resonator_create, name='resonator_create'),
    path('resonators/<int:pk>/', views.resonator_detail_update, name='resonator_detail_update'),
    path('resonators/<int:pk>/delete/', views.resonator_delete, name='resonator_delete'),

    # Weapons
    path('weapons/', views.weapon_list, name='weapon_list'),
    path('weapons/add/', views.weapon_create, name='weapon_create'),
    path('weapons/<int:pk>/', views.weapon_detail_update, name='weapon_detail_update'),
    path('weapons/<int:pk>/delete/', views.weapon_delete, name='weapon_delete'),

    # Builds
    path('builds/', views.build_list, name='build_list'),
    path('builds/add/', views.build_create, name='build_create'),
    path('builds/<int:pk>/', views.build_detail_update, name='build_detail_update'),
    path('builds/<int:pk>/delete/', views.build_delete, name='build_delete'),

    # Echoes
    path('echoes/', views.echo_list, name='echo_list'),
    path('echoes/add/', views.echo_create, name='echo_create'),
    path('echoes/<int:pk>/', views.echo_detail_update, name='echo_detail_update'),
    path('echoes/<int:pk>/delete/', views.echo_delete, name='echo_delete'),
]