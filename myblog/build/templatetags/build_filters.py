# build/templatetags/build_filters.py

from django import template
import re # Meskipun mungkin tidak digunakan langsung di replace_filter sederhana, tidak masalah ada.

register = template.Library()

@register.filter(name='replace') # Pastikan 'replace' adalah nama filternya di sini
def replace_filter(value, arg):
    """
    Mengganti substring 'arg' dalam 'value' dengan spasi.
    Contoh penggunaan di template: {{ my_string|replace:"_" }}
    Perhatikan: Argumen 'arg' di template akan menjadi string yang akan diganti.
    Contoh: {{ stat_name|replace:"_" }} akan mengganti underscore dengan spasi.
    """
    if isinstance(value, str):
        return value.replace(arg, ' ')
    return value