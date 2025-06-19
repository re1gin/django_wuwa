# build/urls.py
from django.urls import path
from . import views
from django.views.decorators.http import require_POST

app_name = 'build'

urlpatterns = [
    path('builder/<str:name>/', views.character_builder_view, name='character_builder'),
    path('get_item_details_ajax/', views.get_item_details_ajax, name='get_item_details_ajax'),
    path('history/', views.build_history_view, name='build_history'),
    path('history/<int:build_id>/', views.view_saved_build_detail, name='view_saved_build_detail'),
    path('history/<int:build_id>/delete/', require_POST(views.delete_saved_build), name='delete_saved_build'),
    path('compare_stats/<str:character_name>/', views.compare_stats_view, name='compare_stats'), # URL untuk halaman perbandingan
]