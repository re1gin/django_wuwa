# build_app/urls.py
from django.urls import path
from . import views 

app_name = 'build'

urlpatterns = [
    path('add/', views.add_build, name='add_build'),
    path('add/success/', views.add_build, name='build_success'),
]