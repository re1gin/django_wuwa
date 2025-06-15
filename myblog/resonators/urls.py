# resonators/urls.py

from django.urls import path
from . import views # Mengimpor views dari direktori yang sama (resonators/views.py)

app_name = 'resonators'

urlpatterns = [
    
    
    path('resonator/', views.resonator_selection, name='resonator_selection'),

    path('resonator/<str:character_name>/', views.resonators, name='resonator_detail'),   
]