# build.models.py
from django.db import models
from resonators.models import Resonator

class Build(models.Model):
    character = models.ForeignKey(Resonator, on_delete=models.CASCADE)
    hp = models.FloatField(null=True, blank=True)
    attack = models.FloatField(null=True, blank=True)
    defense = models.FloatField(null=True, blank=True)
    energy = models.FloatField(null=True, blank=True)
    crit_rate = models.FloatField(null=True, blank=True)
    crit_dmg = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Stat Final for {self.character.character}" # <--- PERBAIKAN DI SINI!

    class Meta:
        verbose_name_plural = "Final Builds"