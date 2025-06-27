# build/admin.py
from django.contrib import admin

from .models import Build, UserBuild
from weapon.models import Weapon
from echo.models import Echo, Sonata


@admin.register(Weapon)
class WeaponAdmin(admin.ModelAdmin):
    list_display = ('weapon_name', 'weapon_type', 'rarity') # Menambahkan weapon_type dan rarity agar lebih informatif
    search_fields = ('weapon_name', 'weapon_type__name')
    list_filter = ('weapon_type', 'rarity') # Tambahkan filter
    ordering = ('weapon_name',) # Urutkan berdasarkan nama

@admin.register(Echo)
class EchoAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost') # Menambahkan cost
    search_fields = ('name',)
    filter_horizontal = ('sonatas',) # Tetap mempertahankan filter_horizontal untuk ManyToMany
    ordering = ('name',)

@admin.register(Sonata)
class SonataAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Build)
class BuildAdmin(admin.ModelAdmin):
    list_display = ('character', 'build_name', 'attack', 'crit_rate', 'crit_dmg', 'energy') # Menyesuaikan list_display
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
            'fields': (
                'attribute_dmg_bonus',
            )
        }),
        ('Other Stats', {
            # 'def_interruption' dan 'attribute_dmg_bonus' dihapus
            'fields': ('healing_bonus',) # 'attribute_res' tetap ada
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
            'fields': (
                'basic_atk_dmg',
                'resonance_skill_dmg',
                'resonance_lib_dmg',
                'attribute_dmg_bonus',
            )
        }),
        ('Other Stats', {
            'fields': ('healing_bonus',) 
        }),
        ('Selected Gear', {
            'fields': ('selected_weapon', 'selected_echo', 'selected_sonata')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )