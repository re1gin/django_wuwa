import os
from django.db import models

def get_weapon_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{instance.nama.replace(" ", "_").lower()}.{ext}'
    # Path: media/weapons/nama_senjata.ext
    return os.path.join('weapons', filename)


class Weapon(models.Model):
    nama = models.CharField(max_length=100, unique=True)
    gambar = models.ImageField(upload_to=get_weapon_image_path, blank=True, null=True)
    tipe_senjata = models.CharField(max_length=50)
    rarity = models.IntegerField()
    stat_utama = models.FloatField(null=True, blank=True)
    stat_kedua = models.CharField(max_length=100, blank=True, null=True)
    skill_pasif = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = "Weapons"