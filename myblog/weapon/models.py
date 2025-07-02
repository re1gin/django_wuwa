# weapon/models.py
from django.db import models
import os

def weapon_icon_upload_path(instance):
    base_filename = instance.weapon_name.replace(' ', '_')
    new_filename = f"{base_filename}.png"
    
    return os.path.join('weapon', new_filename)

def weapontype_icon_upload_path(instance):
    base_filename = instance.name.replace(' ', '_')
    new_filename = f"{base_filename}.png"
    
    return os.path.join('type', new_filename)


class WeaponType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon_type = models.ImageField(upload_to=weapontype_icon_upload_path, blank=True, null=True)
    
    def __str__(self):
        return self.name

class Weapon(models.Model):
    weapon_name = models.CharField(max_length=100, unique=True)
    rarity = models.IntegerField(default=1)
    weapon_type = models.ForeignKey(WeaponType, on_delete=models.SET_NULL, null=True, blank=True)
    base_atk = models.IntegerField(default=0) 
    SECONDARY_STAT_CHOICES = [
        ('ATK%', 'ATK%'),
        ('DEF%', 'DEF%'),
        ('HP%', 'HP%'),
        ('Energy Regen', 'Energy Regen'),
        ('Crit Rate', 'Crit Rate'),
        ('Crit DMG', 'Crit DMG'),
    ]
    secondary_stat = models.CharField(
        max_length=50,
        choices=SECONDARY_STAT_CHOICES,
        default='ATK%'
    )
    secondary_value = models.CharField(max_length=20, default='0')
    passive_skill_description = models.TextField(null=True, blank=True)
    
    # Image field
    icon_image = models.ImageField(upload_to=weapon_icon_upload_path, blank=True, null=True)

    def __str__(self):
        return self.weapon_name

    class Meta:
        verbose_name = "Weapon"
        verbose_name_plural = "Weapons"
        ordering = ['weapon_name']