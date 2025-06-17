# build/templatetags/build_filters.py

from django import template

# Ini adalah instance dari template.Library yang digunakan untuk mendaftarkan tag dan filter.
register = template.Library()

@register.filter
def get_item_by_name(collection, item_name):
    """
    Mengambil objek dari sebuah koleksi (list atau QuerySet)
    berdasarkan atribut 'name', 'Echo_name', atau 'weapon_name'.
    """
    for item in collection:
        # Coba cari berdasarkan Echo_name (untuk Echos)
        if hasattr(item, 'Echo_name') and item.Echo_name == item_name:
            return item
        # Coba cari berdasarkan name (untuk Sonatas)
        if hasattr(item, 'name') and item.name == item_name:
            return item
        # Coba cari berdasarkan weapon_name (untuk Weapons)
        if hasattr(item, 'weapon_name') and item.weapon_name == item_name:
            return item
    return None # Mengembalikan None jika tidak ditemukan

@register.filter
def replace_spaces(value, replacement=''):
    """
    Mengganti spasi dengan karakter pengganti.
    Digunakan untuk membuat nama file URL yang valid.
    """
    return value.replace(' ', replacement)

@register.filter
def replace_hashes(value, replacement=''):
    """
    Mengganti karakter '#' dengan karakter pengganti.
    Digunakan untuk membersihkan nama file URL yang valid.
    """
    return value.replace('#', replacement)