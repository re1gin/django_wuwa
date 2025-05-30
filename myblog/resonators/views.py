import os
import json
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from .models import Character
from django.urls import reverse

def resonators(request, character_name):
    character = get_object_or_404(Character, character=character_name)

    # --- Bagian untuk Memuat Data JSON ---
    json_filepath = os.path.join(settings.BASE_DIR, 'data', 'character_quote.json')
    json_data = {}
    
    if os.path.exists(json_filepath):
        with open(json_filepath, 'r', encoding='utf-8') as f:
            all_quotes = json.load(f)
            for item in all_quotes:
                if item.get("Nama") == character.character:
                    json_data["Gelar"] = item.get("Gelar", "N/A")
                    json_data["Quote"] = item.get("Quote", "No description available.")
                    break

    # --- Logika Gambar Karakter yang Sedang Dilihat ---
    name_resonator = character.character.replace(' ', '_')
    image_resonator = f"assets/character/{name_resonator}/"

    images = {
        "icon": image_resonator + "Icon.png",
        "profile": image_resonator + "Profile.png",
        "sprite": image_resonator + "Sprite.png",
        "convene": image_resonator + "Convene.png",
    }

    # --- Bagian Mengambil Daftar Semua Karakter untuk icon-container (ini tetap ada) ---
    all_characters_for_icons = []
    all_db_characters = Character.objects.all().order_by('character')

    for char_obj in all_db_characters:
        formatted_icon_name = char_obj.character.replace(' ', '_')
        icon_url = f"{settings.STATIC_URL}assets/character/{formatted_icon_name}/icon.png"
        detail_url = reverse('resonator_detail', kwargs={'character_name': char_obj.character})

        all_characters_for_icons.append({
            'character_name': char_obj.character,
            'icon_url': icon_url,
            'detail_url': detail_url,
            'is_active': (char_obj.character == character.character)
        })

    context = {
        "character": character,
        "images": images,
        "json_data": json_data,
        "all_characters_for_icons": all_characters_for_icons,
    }
    return render(request, 'resonator.html', context)

