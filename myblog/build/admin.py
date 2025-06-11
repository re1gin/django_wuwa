
from django.contrib import admin
from .models import Build

class BuildAdmin(admin.ModelAdmin):
    list_display = ('character', 'hp', 'attack', 'defense', 'energy', 'crit_rate', 'crit_dmg')
    list_filter = ('character',)
    search_fields = ('character__character',) # Mencari berdasarkan nama karakter yang terkait

admin.site.register(Build, BuildAdmin)