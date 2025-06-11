
from django.urls import path
from . import views 

app_name = 'echo'

urlpatterns = [
    path('add/', views.add_echo, name='add_echo'),
    path('add/success/', views.echo_success, name='echo_success'),
]