# combat/models.py
from django.db import models

class Attribute(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Attribute"
        verbose_name_plural = "Attributes"
        ordering = ['name']

class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        ordering = ['name']

# Rarity dan WeaponType DIHAPUS dari file ini
# class Rarity(models.Model): ...
# class WeaponType(models.Model): ...