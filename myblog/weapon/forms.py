# weapons_app/forms.py
from django import forms
from .models import Weapon

class WeaponForm(forms.ModelForm):
    class Meta:
        model = Weapon
        fields = '__all__'
        widgets = {
            'nama': forms.TextInput(attrs={'placeholder': 'Nama Senjata', 'class': 'form-control'}),
            'tipe_senjata': forms.TextInput(attrs={'placeholder': 'Tipe Senjata', 'class': 'form-control'}),
            'rarity': forms.NumberInput(attrs={'placeholder': 'Rarity (1-5)', 'class': 'form-control'}),
            'stat_utama': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stat_kedua': forms.TextInput(attrs={'placeholder': 'Stat Kedua (opsional)', 'class': 'form-control'}),
            'skill_pasif': forms.Textarea(attrs={'placeholder': 'Deskripsi Skill Pasif', 'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'nama': 'Nama Senjata', 'tipe_senjata': 'Tipe Senjata', 'rarity': 'Rarity',
            'stat_utama': 'Stat Utama', 'stat_kedua': 'Stat Kedua', 'skill_pasif': 'Skill Pasif',
        }