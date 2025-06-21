# resonators/admin.py
from django.contrib import admin
from .models import Resonator, ResonatorRecommendedWeapon, ResonatorRecommendedEcho, ResonatorRecommendedSonata

class ResonatorRecommendedWeaponInline(admin.TabularInline):
    model = ResonatorRecommendedWeapon
    extra = 1
    fk_name = 'resonator' # <-- Tambahkan baris ini

class ResonatorRecommendedEchoInline(admin.TabularInline):
    model = ResonatorRecommendedEcho
    extra = 1
    fk_name = 'resonator' # <-- Tambahkan baris ini

class ResonatorRecommendedSonataInline(admin.TabularInline):
    model = ResonatorRecommendedSonata
    extra = 1
    fk_name = 'resonator' # <-- Tambahkan baris ini

@admin.register(Resonator)
class ResonatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'weapon_type')
    search_fields = ('name',)
    inlines = [
        ResonatorRecommendedWeaponInline,
        ResonatorRecommendedEchoInline,
        ResonatorRecommendedSonataInline,
    ]