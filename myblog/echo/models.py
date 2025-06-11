from django.db import models
import os

# Fungsi untuk menentukan lokasi upload dan nama file
def get_echo_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{instance.nama.replace(" ", "_").lower()}.{ext}'
    # Path: media/echoes/nama_echo.ext
    return os.path.join('echoes', filename)

class Echo(models.Model):
    nama = models.CharField(max_length=100, unique=True)
    gambar = models.ImageField(upload_to=get_echo_image_path, blank=True, null=True)
    set_bonus_2pc = models.TextField(blank=True, null=True)
    set_bonus_5pc = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = "Echoes"