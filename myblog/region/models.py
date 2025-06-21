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

class SubRegion(models.Model):
    name = models.CharField(max_length=100, unique=True)
    parent_region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='sub_regions')

    def __str__(self):
        return f"{self.name} ({self.parent_region.name})"

    class Meta:
        verbose_name = "Sub Region"
        verbose_name_plural = "Sub Regions"
        unique_together = ('name', 'parent_region')
        ordering = ['name']