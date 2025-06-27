# build/forms.py
from django import forms
from .models import Build, Weapon, Echo, Sonata, Resonator

class BuildForm(forms.ModelForm):
    # Field yang wajib diisi (main stats)
    hp = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '0.0'}),
        min_value=0.0,
        required=True,
        error_messages={'required': 'Field HP tidak boleh kosong.', 'min_value': 'HP harus angka positif.'}
    )
    attack = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '0.0'}),
        min_value=0.0,
        required=True,
        error_messages={'required': 'Field ATK tidak boleh kosong.', 'min_value': 'ATK harus angka positif.'}
    )
    defense = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '0.0'}),
        min_value=0.0,
        required=True,
        error_messages={'required': 'Field DEF tidak boleh kosong.', 'min_value': 'DEF harus angka positif.'}
    )
    energy = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '0.0'}),
        min_value=0.0,
        required=True,
        error_messages={'required': 'Field Energy Regen tidak boleh kosong.', 'min_value': 'Energy Regen harus angka positif.'}
    )
    crit_rate = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '0.0'}),
        min_value=0.0,
        required=True,
        error_messages={'required': 'Field Critical Rate tidak boleh kosong.', 'min_value': 'Critical Rate harus angka positif.'}
    )
    crit_dmg = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '0.0'}),
        min_value=0.0,
        required=True,
        error_messages={'required': 'Field Critical Damage tidak boleh kosong.', 'min_value': 'Critical Damage harus angka positif.'}
    )

    # Field dropdown yang wajib diisi
    selected_weapon = forms.CharField(
        required=True,
        error_messages={'required': 'Mohon pilih Senjata.'}
    )
    selected_echo = forms.CharField(
        required=True,
        error_messages={'required': 'Mohon pilih Echo.'}
    )
    selected_sonata = forms.CharField(
        required=True,
        error_messages={'required': 'Mohon pilih Efek Sonata.'}
    )

    # Field bonus stat - tidak wajib diisi
    basic_attack_dmg_bonus = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '0.0'}),
        min_value=0.0, required=False, initial=0.0
    )
    heavy_attack_dmg_bonus = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '0.0'}),
        min_value=0.0, required=False, initial=0.0
    )
    resonance_skill_dmg_bonus = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '0.0'}),
        min_value=0.0, required=False, initial=0.0
    )
    resonance_lib_dmg_bonus = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '0.0'}),
        min_value=0.0, required=False, initial=0.0
    )
    
    # --- PERUBAHAN DI SINI: Hanya satu field untuk bonus DMG Atribut ---
    attribute_dmg_bonus = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '0.0'}),
        min_value=0.0, required=False, initial=0.0
    )
    # --- AKHIR PERUBAHAN ---

    healing_bonus = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '0.0'}),
        min_value=0.0, required=False, initial=0.0
    )
    attribute_res = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '0.0'}),
        min_value=0.0, required=False, initial=0.0
    )

    class Meta:
        model = Build
        fields = [
            'character',
            'hp', 'attack', 'defense', 'energy', 'crit_rate', 'crit_dmg',
            'basic_attack_dmg_bonus', 'heavy_attack_dmg_bonus', 'resonance_skill_dmg_bonus',
            'resonance_lib_dmg_bonus', 'healing_bonus',
            'attribute_dmg_bonus', # --- PERUBAHAN DI SINI ---
            'attribute_res',
            'selected_weapon', 'selected_echo', 'selected_sonata'
        ]
        widgets = {
            'character': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'character': 'Karakter',
            'hp': 'HP', 'attack': 'ATK', 'defense': 'DEF',
            'energy': 'Energy Regen', 'crit_rate': 'Crit Rate', 'crit_dmg': 'Crit Dmg',
            'basic_attack_dmg_bonus': 'Basic Attack DMG Bonus',
            'heavy_attack_dmg_bonus': 'Heavy Attack DMG Bonus',
            'resonance_skill_dmg_bonus': 'Resonance Skill DMG Bonus',
            'resonance_lib_dmg_bonus': 'Resonance Liberation DMG Bonus',
            'healing_bonus': 'Healing Bonus',
            'attribute_dmg_bonus': 'Attribute DMG Bonus', # --- PERUBAHAN DI SINI ---
            'attribute_res': 'Attribute Resistance',
            'selected_weapon': 'Senjata',
            'selected_echo': 'Echo',
            'selected_sonata': 'Efek Sonata',
        }

    def clean(self):
        cleaned_data = super().clean()
        
        selected_echo_name = cleaned_data.get('selected_echo')
        selected_sonata_name = cleaned_data.get('selected_sonata')
        selected_weapon_name = cleaned_data.get('selected_weapon')
        
        # Validasi Echo dan Sonata
        if selected_echo_name:
            echo_obj = Echo.objects.filter(name=selected_echo_name).first()
            if not echo_obj:
                self.add_error('selected_echo', f"Echo '{selected_echo_name}' tidak ditemukan. Pilihan Echo dan Sonata direset.")
                cleaned_data['selected_echo'] = ''
                cleaned_data['selected_sonata'] = ''
            elif selected_sonata_name:
                if not echo_obj.sonatas.filter(name=selected_sonata_name).exists():
                    self.add_error('selected_sonata', f"Sonata '{selected_sonata_name}' tidak valid untuk Echo '{selected_echo_name}'. Pilihan direset.")
                    cleaned_data['selected_sonata'] = ''
        elif selected_sonata_name:
            self.add_error('selected_sonata', "Sonata tidak dapat dipilih tanpa Echo yang dipilih. Sonata direset.")
            cleaned_data['selected_sonata'] = ''

        # Validasi Weapon
        if selected_weapon_name:
            weapon_obj = Weapon.objects.filter(weapon_name=selected_weapon_name).first()
            if not weapon_obj:
                self.add_error('selected_weapon', f"Senjata '{selected_weapon_name}' tidak ditemukan. Pilihan senjata direset.")
                cleaned_data['selected_weapon'] = ''
                
        character_obj = cleaned_data.get('character')
        if character_obj:
            if not isinstance(character_obj, Resonator):
                try:
                    character_obj = Resonator.objects.get(pk=character_obj)
                    cleaned_data['character'] = character_obj
                except Resonator.DoesNotExist:
                    self.add_error('character', 'Karakter tidak valid.')
        
        return cleaned_data