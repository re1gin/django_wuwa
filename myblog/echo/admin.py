from django.contrib import admin

# Register your models here.
# echo_app/admin.py
from django.contrib import admin
from .models import Echo

class EchoAdmin(admin.ModelAdmin):
    list_display = ('nama', 'set_bonus_2pc', 'set_bonus_5pc')
    search_fields = ('nama', 'set_bonus_2pc', 'set_bonus_5pc')

admin.site.register(Echo, EchoAdmin)