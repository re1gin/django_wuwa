# damager/admin.py
# Admin untuk model Skill dan SkillMultiplier di aplikasi 'damager'.

from django.contrib import admin
from resonators.models import Resonator # Impor Resonator jika perlu di admin
from .models import Skill, SkillMultiplier

# Inline untuk SkillMultiplier agar bisa ditambahkan langsung di halaman Skill
class SkillMultiplierInline(admin.TabularInline):
    model = SkillMultiplier
    extra = 1

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'resonator', 'skill_type_category')
    list_filter = ('resonator', 'skill_type_category')
    search_fields = ('name', 'description', 'resonator__name')
    inlines = [SkillMultiplierInline]

@admin.register(SkillMultiplier)
class SkillMultiplierAdmin(admin.ModelAdmin):
    list_display = ('attack_name', 'skill', 'multiplier_value', 'attack_type')
    list_filter = ('skill__resonator', 'attack_type')
    search_fields = ('attack_name', 'skill__name', 'skill__resonator__name')
