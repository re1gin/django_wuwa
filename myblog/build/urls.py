from django.urls import path
from . import views

app_name = 'build'

urlpatterns = [
    path('builder/<str:name>/', views.character_builder_view, name='character_builder'),
    path('compare/<str:name>/', views.compare_build_view, name='compare_build'),
    path('get_item_details_ajax/', views.get_item_details_ajax, name='get_item_details_ajax'),
]