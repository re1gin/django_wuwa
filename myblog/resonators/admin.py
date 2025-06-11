from django.contrib import admin
from .models import Resonator

class ResonatorAdmin(admin.ModelAdmin):
    list_display = (
        'character', 'rarity', 'weapon', 'sex', 'attribute', 'role',
        'hp', 'atk', 'defense', 'energy', 'crit_rate', 'crit_dmg'
    )
    list_filter = ('rarity', 'weapon', 'attribute', 'sex')
    search_fields = ('character', 'codename', 'affiliation', 'birthplace')
    ordering = ('character',)
    list_display_links = ('character',)
    fieldsets = (
        (None, {
            'fields': ('character', 'codename', 'rarity', 'weapon', 'attribute', 'role')
        }),
        ('Informasi Pribadi', {
            'fields': ('sex', 'birthday', 'affiliation', 'birthplace'),
            'classes': ('collapse',),
        }),
        ('Statistik Dasar', {
            'fields': ('hp', 'atk', 'defense', 'energy', 'crit_rate', 'crit_dmg'),
            'classes': ('wide', 'extrapretty'),
        }),
    )

admin.site.register(Resonator, ResonatorAdmin)
