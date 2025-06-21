# weapon/models.py
from django.db import models
import os

def weapon_icon_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    base_filename = instance.weapon_name.replace(' ', '_')
    new_filename = f"{base_filename}.{ext}"
    
    return os.path.join('weapon', new_filename)


class WeaponType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class Weapon(models.Model):
    weapon_name = models.CharField(max_length=100, unique=True)
    rarity = models.IntegerField()
    weapon_type = models.ForeignKey(WeaponType, on_delete=models.SET_NULL, null=True, blank=True)
    
    icon_image = models.ImageField(upload_to=weapon_icon_upload_path, blank=True, null=True)

    def __str__(self):
        return self.weapon_name

    class Meta:
        verbose_name = "Weapon"
        verbose_name_plural = "Weapons"
        ordering = ['weapon_name']