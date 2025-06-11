import os
from django.db import models
from django.urls import reverse

def get_resonator_icon_path(instance, filename):
    # Nama folder adalah nama resonator (misal: "Jian_Xin")
    folder_name = instance.character.replace(" ", "_").replace("'", "").replace(".", "").lower()
    # Nama file adalah 'Icon.ext'
    ext = filename.split('.')[-1]
    return os.path.join(folder_name, f'Icon.{ext}')

# Fungsi untuk menentukan lokasi upload dan nama file untuk RENDER
def get_resonator_render_path(instance, filename):
    folder_name = instance.character.replace(" ", "_").replace("'", "").replace(".", "").lower()
    ext = filename.split('.')[-1]
    return os.path.join(folder_name, f'Render.{ext}')

# Fungsi untuk menentukan lokasi upload dan nama file untuk CONVENE
def get_resonator_convene_path(instance, filename):
    folder_name = instance.character.replace(" ", "_").replace("'", "").replace(".", "").lower()
    ext = filename.split('.')[-1]
    return os.path.join(folder_name, f'Convene.{ext}') # Asumsi nama file adalah 'Convene'


class Resonator(models.Model):
    character = models.CharField(max_length=100, unique=True)
    
    icon_gambar = models.ImageField(upload_to=get_resonator_icon_path, blank=True, null=True)
    render_gambar = models.ImageField(upload_to=get_resonator_render_path, blank=True, null=True)
    convene_gambar = models.ImageField(upload_to=get_resonator_convene_path, blank=True, null=True)

    rarity = models.CharField(max_length=10, blank=True, null=True)
    weapon = models.CharField(max_length=50, blank=True, null=True)
    sex = models.CharField(max_length=10, blank=True, null=True)
    codename = models.CharField(max_length=100, blank=True, null=True)
    birthday = models.CharField(max_length=20, blank=True, null=True)
    affiliation = models.CharField(max_length=100, blank=True, null=True)
    birthplace = models.CharField(max_length=100, blank=True, null=True)
    attribute = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(max_length=100, blank=True, null=True)
    hp = models.IntegerField(blank=True, null=True) 
    atk = models.IntegerField(blank=True, null=True) 
    defense = models.IntegerField(blank=True, null=True)
    energy = models.IntegerField(blank=True, null=True)
    crit_rate = models.IntegerField(blank=True, null=True)
    crit_dmg = models.IntegerField(blank=True, null=True)
    
    def get_absolute_url(self):
        return reverse('resonator_detail', kwargs={'character_name': self.character})

    def __str__(self):
        return self.character
    
    class Meta:
        verbose_name = 'Resonator'
        verbose_name_plural = 'Resonators'

