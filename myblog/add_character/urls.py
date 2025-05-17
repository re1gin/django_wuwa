from django.urls import path
from .views import add_character

urlpatterns = [
    path('', add_character, name='character-add'),
]
