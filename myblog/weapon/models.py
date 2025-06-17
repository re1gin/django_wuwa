# build/models.py

from django.db import models

class Weapon(models.Model):
    weapon_name = models.CharField(max_length=100, unique=True)
    rarity = models.IntegerField()
    weapon_type = models.CharField(max_length=50)

    def __str__(self):
        return self.weapon_name

    class Meta:
        verbose_name = "Weapon"
        verbose_name_plural = "Weapons"