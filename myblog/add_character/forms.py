from django import forms
from .models import Character, BaseStat, FinalStat

class BaseStatForm(forms.ModelForm):
    class Meta:
        model = BaseStat
        fields = '__all__'

class FinalStatForm(forms.ModelForm):
    class Meta:
        model = FinalStat
        fields = '__all__'

class CharacterForm(forms.ModelForm):
    class Meta:
        model = Character
        exclude = ['base_stat', 'final_stat']
