import os
import json
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.urls import reverse
from .models import Character

def format_folder(name):
    formatted_name = name.replace(' ', '_')
    formatted_name = formatted_name.replace('’', '').replace(',', '')
    
    return formatted_name

# --- View character_selection
def character_selection(request):
    all_characters = Character.objects.all().order_by('character')

    char_cards = []
    for char_obj in all_characters:
        folder_name = format_folder(char_obj.character)

        wallpaper_path = f"{settings.STATIC_URL}assets/character/{folder_name}/Wallpaper.png"
        
        detail_url = reverse('resonators:resonator_detail', kwargs={'character_name': char_obj.character})

        char_cards.append({
            'name': char_obj.character,
            'wallpaper_url': wallpaper_path,
            'detail_url': detail_url,
        })
    
    char_cards.sort(key=lambda x: x['name']) 

    context = {
        'characters': char_cards,
        'page_title': 'Pilih Resonator Anda' 
    }
    return render(request, 'resonators_selection.html', context) 


def resonators(request, character_name):
    char_obj = get_object_or_404(Character, character=character_name)

    # --- Bagian untuk Memuat Data JSON ---
    json_filepath = os.path.join(settings.BASE_DIR, 'data', 'character_quote.json') 
    char_quotes = { 
        "Gelar": "N/A",
        "Quote": "No description available."
    }
    
    if os.path.exists(json_filepath):
        try:
            with open(json_filepath, 'r', encoding='utf-8') as f:
                all_quotes = json.load(f)
                for item in all_quotes:
                    if item.get("Nama") == char_obj.character:
                        char_quotes["Gelar"] = item.get("Gelar", "N/A")
                        char_quotes["Quote"] = item.get("Quote", "No description available.")
                        break
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {json_filepath}: {e}")
        except FileNotFoundError:
            print(f"JSON file not found at {json_filepath}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    else:
        print(f"JSON file NOT found at: {json_filepath}")

    # Logika Gambar Karakter yang Sedang Dilihat.
    folder_name = format_folder(char_obj.character)
    image_path = f"{settings.STATIC_URL}assets/character/{folder_name}/"
    
    # Membuat dictionary 'images' menggunakan path dasar
    images = {
        "render": f"{image_path}Render.png",
    }

    # Logika untuk Icon Container (Khusus untuk Rover, lainnya hanya tampilkan diri sendiri)
    icon_chars_data = [] 
    
    if "rover -" in char_obj.character.lower(): 
        rover_variants = Character.objects.filter(character__icontains='Rover - ').order_by('character')
        
        for variant in rover_variants:
            icon_folder = format_folder(variant.character)
            icon_url = f"{settings.STATIC_URL}assets/character/{icon_folder}/Icon.png" 
            
            icon_detail_url = reverse('resonators:resonator_detail', kwargs={'character_name': variant.character})
            is_active_icon = (variant.character == char_obj.character)

            icon_chars_data.append({
                'icon_url': icon_url,
                'character_name': variant.character,
                'detail_url': icon_detail_url,
                'is_active': is_active_icon,
            })
    else: 
        icon_folder = format_folder(char_obj.character)
        icon_url = f"{settings.STATIC_URL}assets/character/{icon_folder}/Icon.png"
        icon_detail_url = reverse('resonators:resonator_detail', kwargs={'character_name': char_obj.character})

        icon_chars_data.append({
            'icon_url': icon_url,
            'character_name': char_obj.character,
            'detail_url': icon_detail_url,
            'is_active': True, 
        })

    context = {
        "character": char_obj,
        "images": images,
        "json_data": char_quotes,
        "all_characters_for_icons": icon_chars_data, 
    }
    return render(request, 'resonator.html', context)