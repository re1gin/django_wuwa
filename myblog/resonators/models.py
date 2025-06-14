import os
from django.db import models
from django.urls import reverse

class Resonator(models.Model):
    character_name = models.CharField(max_length=100, unique=True)
    
    def get_absolute_url(self):
        return reverse('resonator_detail', kwargs={'character_name': self.name})

    def __str__(self):
        return self.name

