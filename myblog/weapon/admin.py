from django.contrib import admin

# Register your models here.
# weapons_app/admin.py
from django.contrib import admin
from .models import Weapon

class WeaponAdmin(admin.ModelAdmin):
    list_display = ('nama', 'tipe_senjata', 'rarity', 'stat_utama', 'stat_kedua')
    list_filter = ('tipe_senjata', 'rarity')
    search_fields = ('nama', 'skill_pasif')

admin.site.register(Weapon, WeaponAdmin)