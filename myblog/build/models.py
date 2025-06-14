from django.db import models
from resonators.models import Resonator

class Build(models.Model):
    character = models.OneToOneField(Resonator, on_delete=models.CASCADE, related_name='ideal_build')
    hp = models.FloatField(default=0.0)
    attack = models.FloatField(default=0.0)
    defense = models.FloatField(default=0.0)
    energy = models.FloatField(default=0.0)
    crit_rate = models.FloatField(default=0.0)
    crit_dmg = models.FloatField(default=0.0)

    def __str__(self):
        return f"Ideal Build for {self.character.character_name}"