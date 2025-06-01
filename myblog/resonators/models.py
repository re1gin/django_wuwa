from django.db import models
from django.urls import reverse

class Character(models.Model):
    character = models.CharField(max_length=100, unique=True)
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
        verbose_name = 'Character'
        verbose_name_plural = 'Characters'

