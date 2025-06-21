# combat/models.py

from django.db import models
import os

def attribute_icon_upload_path(instance, filename):
    return os.path.join('attribute', filename)

class Attribute(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon_attribute = models.ImageField(upload_to=attribute_icon_upload_path, blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Attribute"
        verbose_name_plural = "Attributes"
        ordering = ['name']


def role_icon_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    sanitized_role_name = instance.name.replace(' ', '_')
    new_filename = f"Icon_{sanitized_role_name}.{ext}"
    return os.path.join('roles', new_filename)

class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon_role = models.ImageField(upload_to=role_icon_upload_path, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        ordering = ['name']