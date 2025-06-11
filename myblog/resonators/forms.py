# Resonators_app/forms.py
from django import forms
from .models import Resonator

class ResonatorForm(forms.ModelForm):
    # Tidak perlu mendefinisikan choices di luar Meta lagi jika sudah di dalam widget secara langsung.
    # class Meta:
    # ...

    class Meta:
        model = Resonator
        fields = [
            'character', 'codename', 'rarity', 'weapon', 'sex',
            'attribute', 'role', 'birthday', 'affiliation', 'birthplace',
            'hp', 'atk', 'defense', 'energy', 'crit_rate', 'crit_dmg',
            'icon_gambar', 'render_gambar', 'convene_gambar', # field gambar
        ]
        widgets = {
            'character': forms.TextInput(attrs={'placeholder': 'Nama Resonator', 'class': 'form-control'}),
            'rarity': forms.Select(attrs={'class': 'form-control'}, 
                                   choices=[('4 Star', '4 Star'), 
                                            ('5 Star', '5 Star')]),
            
            # PERBAIKAN DI SINI: Gunakan forms.Select
            'weapon': forms.Select(attrs={'class': 'form-control'},
                                   choices=[('Broadblade', 'Broadblade'),
                                            ('Pistols', 'Pistols'),
                                            ('Gauntlets', 'Gauntlets'),
                                            ('Rectifier', 'Rectifier'),
                                            ('Sword', 'Sword')]),
            
            'sex': forms.Select(attrs={'class': 'form-control'}, 
                                 choices=[('Male', 'Male'), 
                                          ('Female', 'Female')]),
            
            # Sangat direkomendasikan menggunakan forms.DateInput untuk 'birthday'
            'birthday': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
            
            'affiliation': forms.TextInput(attrs={'placeholder': 'Afiliasi Karakter', 'class': 'form-control'}),
            'birthplace': forms.TextInput(attrs={'placeholder': 'Tempat Lahir Karakter', 'class': 'form-control'}),
            
            # PERBAIKAN DI SINI: Gunakan forms.Select
            'attribute': forms.Select(attrs={'class': 'form-control'},
                                      choices=[('Fusion', 'Fusion'),
                                               ('Glacio', 'Glacio'),
                                               ('Electro', 'Electro'),
                                               ('Aero', 'Aero'),
                                               ('Spectro', 'Spectro'),
                                               ('Havoc', 'Havoc')]),
            
            # PERBAIKAN DI SINI: Gunakan forms.Select dan tambahkan choices
            'role': forms.Select(attrs={'class': 'form-control'},
                                 choices=[('Main DPS', 'Main DPS'),
                                          ('Sub DPS', 'Sub DPS'),
                                          ('Support', 'Support'),
                                          ('Healer', 'Healer')]), # Sesuaikan pilihan role Anda
            
            'hp': forms.NumberInput(attrs={'class': 'form-control'}),
            'atk': forms.NumberInput(attrs={'class': 'form-control'}),
            'defense': forms.NumberInput(attrs={'class': 'form-control'}),
            'energy': forms.NumberInput(attrs={'class': 'form-control'}),
            'crit_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'crit_dmg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),

            # Widgets untuk field gambar (pastikan ini ada)
            'icon_gambar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'render_gambar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'convene_gambar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'character': 'Nama Resonator', 'rarity': 'Rarity', 'weapon': 'Tipe Senjata', 'sex': 'Jenis Kelamin',
            'codename': 'Codename', 'birthday': 'Tanggal Lahir', 'affiliation': 'Afiliasi', 'birthplace': 'Tempat Lahir',
            'attribute': 'Elemen', 'role': 'Role', 'hp': 'HP', 'atk': 'ATK', 'defense': 'DEF', 'energy': 'Energy Regen',
            'crit_rate': 'Crit Rate (%)', 'crit_dmg': 'Crit DMG (%)',
            'icon_gambar': 'Gambar Ikon', 'render_gambar': 'Gambar Render', 'convene_gambar': 'Gambar Konvensi',
        }