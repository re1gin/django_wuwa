from django.urls import path
from . import views # Mengimpor views dari direktori yang sama (resonators/views.py)

app_name = 'resonators'

urlpatterns = [
    # URL untuk memilih/melihat daftar resonator
    path('resonator/', views.resonator_selection, name='resonator_selection'),

    # URL untuk detail resonator.
    # Parameter URL sekarang adalah <str:name>
    path('resonator/<str:name>/', views.resonators, name='resonator_detail'),
    # ^^^ Pastikan parameter di sini adalah 'name' ^^^
]