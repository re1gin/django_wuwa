# echo_app/forms.py
from django import forms
from .models import Echo

class EchoForm(forms.ModelForm):
    class Meta:
        model = Echo
        fields = '__all__'
        widgets = {
            'nama': forms.TextInput(attrs={'placeholder': 'Nama Echo', 'class': 'form-control'}),
            'set_bonus_2pc': forms.Textarea(attrs={'placeholder': 'Bonus 2-Piece Set', 'class': 'form-control', 'rows': 3}),
            'set_bonus_5pc': forms.Textarea(attrs={'placeholder': 'Bonus 5-Piece Set', 'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'nama': 'Nama Echo', 'set_bonus_2pc': 'Bonus 2-Piece Set', 'set_bonus_5pc': 'Bonus 5-Piece Set',
        }