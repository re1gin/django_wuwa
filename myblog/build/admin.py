# build/admin.py
from django.contrib import admin
from .models import Build, UserBuild, Weapon, Echo, Sonata

@admin.register(Weapon)
class WeaponAdmin(admin.ModelAdmin):
    list_display = ('weapon_name',)
    search_fields = ('weapon_name',)

@admin.register(Echo)
class EchoAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('sonatas',)

@admin.register(Sonata)
class SonataAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Build)
class BuildAdmin(admin.ModelAdmin):
    list_display = ('character', 'build_name', 'hp', 'attack', 'crit_rate', 'crit_dmg')
    search_fields = ('character__name', 'build_name')
    list_filter = ('character',)
    fieldsets = (
        (None, {
            'fields': ('character', 'build_name')
        }),
        ('Core Stats', {
            'fields': ('hp', 'attack', 'defense', 'energy', 'crit_rate', 'crit_dmg')
        }),
        ('Damage Bonus Stats', {
            'fields': ('basic_atk_dmg', 'resonance_skill_dmg', 'resonance_lib_dmg')
        }),
        ('Other Stats', {
            'fields': ('def_interruption', 'healing_bonus', 'attribute_dmg_bonus', 'attribute_res')
        }),
        ('Ideal Gear (Optional)', {
            'fields': ('ideal_weapon', 'ideal_echo', 'ideal_sonata')
        }),
    )

@admin.register(UserBuild)
class UserBuildAdmin(admin.ModelAdmin):
    list_display = ('user', 'resonator', 'build_name', 'created_at')
    search_fields = ('user__username', 'resonator__name', 'build_name')
    list_filter = ('user', 'resonator')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'resonator', 'build_name')
        }),
        ('Core Stats', {
            'fields': ('hp', 'attack', 'defense', 'energy', 'crit_rate', 'crit_dmg')
        }),
        ('Damage Bonus Stats', {
            'fields': ('basic_atk_dmg', 'resonance_skill_dmg', 'resonance_lib_dmg')
        }),
        ('Other Stats', {
            'fields': ('def_interruption', 'healing_bonus', 'attribute_dmg_bonus', 'attribute_res')
        }),
        ('Selected Gear', {
            'fields': ('selected_weapon', 'selected_echo', 'selected_sonata')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )