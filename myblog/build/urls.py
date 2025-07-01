# build/urls.py
from django.urls import path
from . import views
from django.views.decorators.http import require_POST

app_name = 'build'

urlpatterns = [
    path('builder/<str:name>/', views.character_builder_view, name='character_builder'),
    path('get_item_details_ajax/', views.get_item_details_ajax, name='get_item_details_ajax'),
    path('review/<str:name>/', views.build_review_page, name='review_build_page'),
    path('reset_build_session/', require_POST(views.reset_build_session), name='reset_build_session'),
]