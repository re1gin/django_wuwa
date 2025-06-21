# regions/models.py
from django.db import models

class Region(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Main Region"
        verbose_name_plural = "Main Regions"
        ordering = ['name']