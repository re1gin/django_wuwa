from django.urls import path
from . import views

urlpatterns = [
    path('simulate/', views.simulation_view, name='combat_simulation'),
]