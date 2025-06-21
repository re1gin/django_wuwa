# echoes/models.py
from django.db import models
import os

def sonata_icon_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    
    sanitized_sonata_name = instance.name.replace(' ', '_')
    new_filename = f"{sanitized_sonata_name}.{ext}"
    return os.path.join('sonata', new_filename)

def echo_icon_upload_path(instance, filename):
    ext = filename.split('.')[-1]

    sanitized_echo_name = instance.name.replace(' ', '_')
    new_filename = f"{sanitized_echo_name}_Icon.{ext}"

    return os.path.join('echo', new_filename)


class Sonata(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon_sonata = models.ImageField(upload_to=sonata_icon_upload_path, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Sonata"
        verbose_name_plural = "Sonatas"
        ordering = ['name']

class Echo(models.Model):
    name = models.CharField(max_length=100, unique=True)
    cost = models.IntegerField()
    sonatas = models.ManyToManyField(Sonata, blank=True)

    icon_echo = models.ImageField(upload_to=echo_icon_upload_path, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Echo"
        verbose_name_plural = "Echos"
        ordering = ['name']