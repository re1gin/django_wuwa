from django.conf import settings
from django.db import models
from echo.models import Echo, Sonata
from weapon.models import Weapon
from resonators.models import Resonator

class Build(models.Model):
    character = models.OneToOneField(Resonator, on_delete=models.CASCADE, related_name='ideal_build')
    build_name = models.CharField(max_length=100, default='Default Ideal Build')
    
    # Core Stats
    hp = models.FloatField(default=0.0)
    attack = models.FloatField(default=0.0)
    defense = models.FloatField(default=0.0)
    energy = models.FloatField(default=0.0)
    crit_rate = models.FloatField(default=0.0)
    crit_dmg = models.FloatField(default=0.0)
    
    healing_bonus = models.FloatField(default=0.0)
    attribute_dmg_bonus = models.FloatField(default=0.0)

    # Optional: Untuk menunjukkan item "Best in Slot" yang paling ideal untuk build ini
    ideal_weapon = models.ForeignKey(Weapon, on_delete=models.SET_NULL, null=True, blank=True, related_name='ideal_for_specific_builds')
    ideal_echo = models.ForeignKey(Echo, on_delete=models.SET_NULL, null=True, blank=True, related_name='ideal_for_specific_builds')
    ideal_sonata = models.ForeignKey(Sonata, on_delete=models.SET_NULL, null=True, blank=True, related_name='ideal_for_specific_builds')

    def __str__(self):
        return f"{self.build_name} for {self.character.name}"

    class Meta:
        verbose_name = "Ideal Build"
        verbose_name_plural = "Ideal Builds"
        
class UserBuild(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_builds'
    )
    resonator = models.ForeignKey(
        Resonator,
        on_delete=models.CASCADE,
        related_name='user_saved_builds'
    )
    build_name = models.CharField(max_length=100, default='My Custom Build')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Semua field stat harus sama dengan model 'Build' ideal agar bisa dibandingkan
    hp = models.FloatField(default=0.0)
    attack = models.FloatField(default=0.0)
    defense = models.FloatField(default=0.0)
    energy = models.FloatField(default=0.0)
    crit_rate = models.FloatField(default=0.0)
    crit_dmg = models.FloatField(default=0.0)

    basic_atk_dmg = models.FloatField(default=0.0)
    resonance_skill_dmg = models.FloatField(default=0.0)
    resonance_lib_dmg = models.FloatField(default=0.0)
    healing_bonus = models.FloatField(default=0.0)
    attribute_dmg_bonus = models.FloatField(default=0.0)


    # Item yang dipilih user
    selected_weapon = models.ForeignKey(Weapon, on_delete=models.SET_NULL, null=True, blank=True)
    selected_echo = models.ForeignKey(Echo, on_delete=models.SET_NULL, null=True, blank=True)
    selected_sonata = models.ForeignKey(Sonata, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s build for {self.resonator.name} ({self.build_name})"

    class Meta:
        ordering = ['-created_at']