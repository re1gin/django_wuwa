from django.urls import path
from . import views 

app_name = 'weapon'

urlpatterns = [
    path('add/', views.add_weapon, name='add_weapon'),
    path('add/success/', views.weapon_success, name='weapon_success'),
]