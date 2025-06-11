# build_app/forms.py
from django import forms
from .models import Build

class BuildForm(forms.ModelForm):
    class Meta:
        model = Build
        fields = '__all__'
        widgets = {
            'character': forms.Select(attrs={'class': 'form-control'}),
            'hp': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'attack': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'defense': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'energy': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'crit_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'crit_dmg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels = {
            'character': 'Karakter', 'hp': 'HP', 'attack': 'ATK', 'defense': 'DEF',
            'energy': 'Energy', 'crit_rate': 'Crit Rate', 'crit_dmg': 'Crit Dmg',
        }