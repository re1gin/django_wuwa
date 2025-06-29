# resonators/models.py
from django.db import models
from combat.models import Attribute, Role
from region.models import Region
from weapon.models import WeaponType

# --- Resonator Model ---
class Resonator(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="The official name of the Resonator.")
    rarity = models.IntegerField(help_text="The star rarity of the Resonator (e.g., 4 or 5).")
    weapon_type = models.ForeignKey(WeaponType, on_delete=models.CASCADE, null=True, blank=True)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, null=True, blank=True)
    birthplace = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True)
    role = models.ManyToManyField(Role, null=True, blank=True)

    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Resonator"
        verbose_name_plural = "Resonators"
        ordering = ['name']
