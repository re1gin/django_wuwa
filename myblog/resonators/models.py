
from django.db import models

class Resonator(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="The official name of the Resonator.")
    rarity = models.IntegerField(help_text="The star rarity of the Resonator (e.g., 4 or 5).")
    weapon = models.CharField(max_length=50, help_text="The type of weapon the Resonator uses (e.g., Sword, Pistols).")
    attribute = models.CharField(max_length=50, help_text="The elemental attribute of the Resonator (e.g., Aero, Fusion).")
    birthplace = models.CharField(max_length=100, blank=True, null=True, help_text="The origin place of the Resonator.")
    role = models.CharField(max_length=100, blank=True, null=True, help_text="The primary combat role of the Resonator (e.g., Main Damage Dealer, Support).")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Resonator"
        verbose_name_plural = "Resonators"
        ordering = ['name'] # Mengurutkan berdasarkan nama secara default