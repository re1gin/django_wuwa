from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from echo.models import Echo, Sonata
from weapon.models import Weapon
from resonators.models import Resonator

QUALITY_CHOICES = [
    ('Good', 'Good'),
    ('Great', 'Great'),
    ('Excellent', 'Excellent'),
    ('Best in Slot', 'Best in Slot'),
]

class Build(models.Model):
    character = models.OneToOneField(Resonator, on_delete=models.CASCADE, related_name='ideal_build')
    build_name = models.CharField(max_length=100, default='Default Ideal Build')
    hp = models.FloatField(default=0.0)
    attack = models.FloatField(default=0.0)
    defense = models.FloatField(default=0.0)
    energy = models.FloatField(default=0.0)
    crit_rate = models.FloatField(default=0.0)
    crit_dmg = models.FloatField(default=0.0)
    
    healing_bonus = models.FloatField(default=0.0)
    attribute_dmg_bonus = models.FloatField(default=0.0)
    
    ideal_weapons = models.ManyToManyField(Weapon, through='IdealBuildWeapon', related_name='builds_featuring_this_ideal_weapon')
    ideal_echos = models.ManyToManyField(Echo, through='IdealBuildEcho', related_name='builds_featuring_this_ideal_echo')
    ideal_sonatas = models.ManyToManyField(Sonata, through='IdealBuildSonata', related_name='builds_featuring_this_ideal_sonata')

    def __str__(self):
        return f"{self.build_name} for {self.character.name}"

    class Meta:
        verbose_name = "Ideal Build"
        verbose_name_plural = "Ideal Builds"
        
class IdealBuildWeapon(models.Model):
    build = models.ForeignKey(Build, on_delete=models.CASCADE)
    weapon = models.ForeignKey(Weapon, on_delete=models.CASCADE)
    quality_ranking = models.CharField(
        max_length=15,
        choices=QUALITY_CHOICES,
    )

    class Meta:
        unique_together = ('build', 'weapon')
        verbose_name = "Ideal Build Weapon"
        verbose_name_plural = "Ideal Build Weapons"

    def __str__(self):
        return f"{self.build.build_name} - {self.weapon.name} ({self.get_quality_ranking_display()})"

class IdealBuildEcho(models.Model):
    build = models.ForeignKey(Build, on_delete=models.CASCADE)
    echo = models.ForeignKey(Echo, on_delete=models.CASCADE)
    quality_ranking = models.CharField(
        max_length=15,
        choices=QUALITY_CHOICES,
    )
    
    class Meta:
        unique_together = ('build', 'echo')
        verbose_name = "Ideal Build Echo"
        verbose_name_plural = "Ideal Build Echos"

    def __str__(self):
        return f"{self.build.build_name} - {self.echo.name} ({self.get_quality_ranking_display()})"

class IdealBuildSonata(models.Model):
    build = models.ForeignKey(Build, on_delete=models.CASCADE)
    sonata = models.ForeignKey(Sonata, on_delete=models.CASCADE)
    quality_ranking = models.CharField(
        max_length=15,
        choices=QUALITY_CHOICES,
    )

    class Meta:
        unique_together = ('build', 'sonata')
        verbose_name = "Ideal Build Sonata"
        
    def __str__(self):
        return f"{self.build.build_name} - {self.sonata.name} ({self.get_quality_ranking_display()})"

    def clean(self):
        super().clean()
        if not self.build or not self.sonata:
            return

        ideal_echos_in_build = self.build.ideal_echos.all()

        if not ideal_echos_in_build.exists():
            return 

        sonata_matches_any_echo = False
        for ideal_echo_entry in ideal_echos_in_build:
            if ideal_echo_entry.sonata == self.sonata:
                sonata_matches_any_echo = True
                break

        if not sonata_matches_any_echo:
            raise ValidationError(
            f"Sonata Ideal '{self.sonata.name}' tidak cocok dengan sonata dari Echo ideal manapun yang terdaftar untuk build ini. "
            f"Pastikan Sonata ideal sesuai dengan salah satu Echo ideal pada build ini."
            )

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
    selected_weapon = models.ForeignKey(Weapon, on_delete=models.SET_NULL, null=True, blank=True)
    selected_echo = models.ForeignKey(Echo, on_delete=models.SET_NULL, null=True, blank=True)
    selected_sonata = models.ForeignKey(Sonata, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s build for {self.resonator.name} ({self.build_name})"

    class Meta:
        ordering = ['-created_at']