# damager/models.py
# Ini adalah versi yang benar, tanpa Attribute dan Role, dan mengimpor Resonator

from django.db import models
from resonators.models import Resonator # Impor Resonator dari resonators app

# Model Attribute dan Role TIDAK ADA di sini.

class Skill(models.Model):
    """
    Model untuk menyimpan deskripsi umum skill karakter.
    Terhubung ke model Resonator.
    """
    resonator = models.ForeignKey(Resonator, on_delete=models.CASCADE, related_name='combat_skills', verbose_name="Resonator")
    name = models.CharField(max_length=200, verbose_name="Nama Skill/Serangan Utama")
    description = models.TextField(verbose_name="Deskripsi Combat")
    skill_type_category = models.CharField(
        max_length=50,
        choices=[
            ('Basic Attack', 'Basic Attack'),
            ('Heavy Attack', 'Heavy Attack'),
            ('Mid-air Attack', 'Mid-air Attack'),
            ('Dodge Counter', 'Dodge Counter'),
            ('Resonance Skill', 'Resonance Skill'),
            ('Resonance Liberation', 'Resonance Liberation'),
            ('Intro Skill', 'Intro Skill'),
            ('Outro Skill', 'Outro Skill'),
            ('Forte Circuit', 'Forte Circuit'),
        ],
        verbose_name="Kategori Tipe Skill"
    )

    def __str__(self):
        return f"{self.resonator.name} - {self.name}"

    class Meta:
        verbose_name = "Skill Resonator"
        verbose_name_plural = "Skill Resonator"
        unique_together = ('resonator', 'name')

class SkillMultiplier(models.Model):
    """
    Model untuk menyimpan multiplier damage spesifik dari setiap serangan/tahap skill.
    """
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='multipliers', verbose_name="Skill Terkait")
    attack_name = models.CharField(max_length=200, verbose_name="Nama Serangan (Detail)")
    multiplier_value = models.FloatField(verbose_name="Nilai Multiplier (%)")
    attack_type = models.CharField(
        max_length=50,
        choices=[
            ('basic', 'Basic Attack'),
            ('heavy', 'Heavy Attack'),
            ('skill', 'Resonance Skill'),
            ('liberation', 'Resonance Liberation'),
            ('intro', 'Intro Skill'),
            ('outro', 'Outro Skill'),
            ('forte', 'Forte Circuit'),
        ],
        verbose_name="Tipe Perhitungan DMG Bonus"
    )

    def __str__(self):
        return f"{self.skill.resonator.name} - {self.skill.name} - {self.attack_name}"

    class Meta:
        verbose_name = "Multiplier Skill Resonator"
        verbose_name_plural = "Multiplier Skill Resonator"
        unique_together = ('skill', 'attack_name')
