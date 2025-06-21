# resonators/models.py
from django.db import models
from combat.models import Attribute, Role
from region.models import SubRegion
from weapon.models import WeaponType

class Resonator(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="The official name of the Resonator.")
    rarity = models.IntegerField(help_text="The star rarity of the Resonator (e.g., 4 or 5).")
    weapon_type = models.ForeignKey(WeaponType, on_delete=models.SET_NULL, null=True, blank=True)
    attribute = models.ForeignKey(Attribute, on_delete=models.SET_NULL, null=True, blank=True)
    birthplace = models.ForeignKey(SubRegion, on_delete=models.SET_NULL, null=True, blank=True, related_name='born_resonators')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    
    recommended_weapons = models.ManyToManyField(
        'weapon.Weapon',
        through='ResonatorRecommendedWeapon',
        related_name='recommended_for_resonators'
    )
    recommended_echos = models.ManyToManyField(
        'echo.Echo',
        through='ResonatorRecommendedEcho',
        related_name='recommended_for_resonators_echo'
    )
    recommended_sonatas = models.ManyToManyField(
        'echo.Sonata',
        through='ResonatorRecommendedSonata',
        related_name='recommended_for_resonators_sonata'
    )
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Resonator"
        verbose_name_plural = "Resonators"
        ordering = ['name']

class ResonatorRecommendedWeapon(models.Model):
    resonator = models.ForeignKey(Resonator, on_delete=models.CASCADE)
    
    weapon = models.ForeignKey('weapon.Weapon', on_delete=models.CASCADE)
    PRIORITY_CHOICES = [
        (1, 'Best in Slot'),
        (2, 'Great Alternative'),
        (3, 'Good Option'),
        (4, 'Situational'),
    ]
    priority_level = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=1,
        help_text="Tingkat kelayakan senjata untuk karakter ini (1=terbaik, 4=situasional)"
    )
    notes = models.TextField(blank=True, help_text="Catatan tambahan tentang rekomendasi senjata ini.")

    class Meta:
        unique_together = ('resonator', 'weapon')
        ordering = ['priority_level'] # Agar mudah diurutkan
        verbose_name = "Resonator Recommended Weapon"
        verbose_name_plural = "Resonator Recommended Weapons"

    def __str__(self):
        return f"{self.resonator.name} - {self.weapon.weapon_name} ({self.get_priority_level_display()})"

class ResonatorRecommendedEcho(models.Model):
    resonator = models.ForeignKey(Resonator, on_delete=models.CASCADE)
    
    echo = models.ForeignKey('echo.Echo', on_delete=models.CASCADE)
    PRIORITY_CHOICES = [
        (1, 'Best in Slot'),
        (2, 'Great Alternative'),
        (3, 'Good Option'),
        (4, 'Situational'),
    ]
    priority_level = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=1,
        help_text="Tingkat kelayakan set Echo untuk karakter ini"
    )
    notes = models.TextField(blank=True, help_text="Catatan tambahan tentang rekomendasi Echo ini.")

    class Meta:
        unique_together = ('resonator', 'echo')
        ordering = ['priority_level']
        verbose_name = "Resonator Recommended Echo"
        verbose_name_plural = "Resonator Recommended Echoes"

    def __str__(self):
        return f"{self.resonator.name} - {self.echo.name} ({self.get_priority_level_display()})"

class ResonatorRecommendedSonata(models.Model):
    resonator = models.ForeignKey(Resonator, on_delete=models.CASCADE)
    sonata = models.ForeignKey('echo.Sonata', on_delete=models.CASCADE)
    PRIORITY_CHOICES = [
        (1, 'Best in Slot'),
        (2, 'Great Alternative'),
        (3, 'Good Option'),
        (4, 'Situational'),
    ]
    priority_level = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=1,
        help_text="Tingkat kelayakan Sonata untuk karakter ini"
    )
    notes = models.TextField(blank=True, help_text="Catatan tambahan tentang rekomendasi Sonata ini.")

    class Meta:
        unique_together = ('resonator', 'sonata')
        ordering = ['priority_level']
        verbose_name = "Resonator Recommended Sonata"
        verbose_name_plural = "Resonator Recommended Sonatas"

    def __str__(self):
        return f"{self.resonator.name} - {self.sonata.name} ({self.get_priority_level_display()})"