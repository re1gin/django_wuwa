# build/templatetags/build_filters.py
from django import template
from django.conf import settings # Import settings
from django.contrib.staticfiles.storage import staticfiles_storage # Import staticfiles_storage

register = template.Library()

@register.filter
def format_filename(value):
    """
    Mengganti spasi dengan underscore untuk nama file.
    """
    if value is None:
        return ""
    formatted_value = value.replace(' ', '_')
    return formatted_value

@register.filter
def get_icon_url(item_name, item_type):
    """
    Mengembalikan URL lengkap untuk ikon berdasarkan tipe item dan namanya.
    item_type diharapkan 'weapon', 'echo', atau 'sonata'.
    """
    if not item_name or not item_type:
        return staticfiles_storage.url("assets/ikon/default.png") # Atau gambar default spesifik

    # Format nama file
    formatted_name = format_filename(item_name) # Panggil filter format_filename yang sudah ada

    # Tentukan sub-folder berdasarkan item_type
    folder_path = ""
    if item_type == 'weapon':
        folder_path = "weapon"
    elif item_type == 'echo':
        folder_path = "echo"
    elif item_type == 'sonata':
        folder_path = "sonata"
    else:
        # Tipe tidak dikenal, kembalikan default atau kosong
        return staticfiles_storage.url("assets/ikon/default.png")

    # Bangun path relatif ke file statis
    relative_path = f"{settings.STATIC_URL}assets/ikon/{folder_path}/{formatted_name}.png"

    # Gunakan staticfiles_storage untuk mendapatkan URL lengkap
    return staticfiles_storage.url(relative_path)