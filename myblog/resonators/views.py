import os
import json
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.urls import reverse
from django.http import Http404 

from .models import Resonator 

def format_folder(name):
    formatted_name = name.replace(' ', '_')
    return formatted_name.strip()

def load_resonator_data():
    json_filepath = os.path.join(settings.BASE_DIR, 'data', 'resonators_data.json')
    if os.path.exists(json_filepath):
        try:
            with open(json_filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {json_filepath}: {e}")
        except FileNotFoundError: 
            print(f"JSON file not found at {json_filepath}")
        except Exception as e:
            print(f"An unexpected error occurred while loading JSON: {e}")
    else:
        print(f"JSON file NOT found at: {json_filepath}")
    return []

def resonator_selection(request):
    
    all_resonators_db = Resonator.objects.all().order_by('name')
    char_cards = []
    for char_db_obj in all_resonators_db:
        folder_name = format_folder(char_db_obj.name) 
        
        wallpaper_path = f"{settings.MEDIA_URL}resonator/{folder_name}/Wallpaper.png"
        
        detail_url = reverse('resonators:resonator_detail', kwargs={'name': char_db_obj.name})

        char_cards.append({
            'name': char_db_obj.name,
            'wallpaper_url': wallpaper_path,
            'detail_url': detail_url,
        })
    
    context = {
        'characters': char_cards,
        'page_title': 'Pilih Resonator Anda' 
    }
    return render(request, 'landingpage/resonators_selection.html', context)

def resonators(request, name): 
    try:
        char_db_obj = get_object_or_404(Resonator, name__iexact=name) 
    except Http404: 
        raise Http404(f"Karakter '{name}' tidak ditemukan di database.")

    all_resonators_json_data = load_resonator_data()
    
    char_obj_raw = None
    for data_from_json in all_resonators_json_data:
        if data_from_json.get('name', '').lower() == char_db_obj.name.lower(): 
            char_obj_raw = data_from_json
            break
    
    if not char_obj_raw:
        print(f"ERROR: Data detail JSON untuk karakter '{char_db_obj.name}' tidak ditemukan di resonators_data.json.")
        raise Http404("Detail karakter tidak ditemukan.") 

    character_for_template = {}

    for key, value in char_obj_raw.items():
        new_key = key.lower().replace(' ', '_').replace('-', '_')
        character_for_template[new_key] = value

    character_for_template['name'] = character_for_template.get('name', 'N/A')
    character_for_template['codename'] = character_for_template.get('codename', 'N/A')
    character_for_template['birthday'] = character_for_template.get('birthday', 'N/A')
    character_for_template['sex'] = character_for_template.get('sex', 'N/A')
    character_for_template['birthplace'] = character_for_template.get('birthplace', 'N/A')
    character_for_template['affiliation'] = character_for_template.get('affiliation', 'N/A')
    character_for_template['attribute'] = character_for_template.get('attribute', 'N/A')
    character_for_template['weapon'] = character_for_template.get('weapon_type', 'N/A')
    character_for_template['hp'] = character_for_template.get('hp', 0)
    character_for_template['atk'] = character_for_template.get('atk', 0)
    character_for_template['def'] = character_for_template.get('def', 0)
    character_for_template['energy'] = character_for_template.get('energy', 0)
    
    roles = character_for_template.get('role_name', [])
    character_for_template['role'] = character_for_template.get('role_name', [])
    if not isinstance(character_for_template['role'], list):
        character_for_template['role'] = []
    
    character_for_template['rarity'] = character_for_template.get('rarity', 0)
    
    titles = character_for_template.get('titles', [])
    character_for_template['title'] = titles[0] if isinstance(titles, list) and titles else 'N/A'
    
    character_for_template['quote'] = character_for_template.get("quote", "No description available.")

    folder_name_for_images = format_folder(char_obj_raw.get('name', 'unknown')) 
    images = {
        "render": f"{settings.MEDIA_URL}resonator/{folder_name_for_images}/Render.png",
    }

    icon_chars_data = [] 
    
    icon_folder = format_folder(char_obj_raw.get('name', ''))
    icon_url = f"{settings.MEDIA_URL}resonator/{icon_folder}/Icon.png"
    
    icon_detail_url = reverse('resonators:resonator_detail', kwargs={'name': char_obj_raw.get('name', '')})

    icon_chars_data.append({
        'icon_url': icon_url,
        'character_name': char_obj_raw.get('name', ''),
        'detail_url': icon_detail_url,
        'is_active': True, 
    })

    context = {
        "character": character_for_template,
        "images": images,
        "all_characters_for_icons": icon_chars_data,
        "builder_url": reverse('build:character_builder', kwargs={'name': char_obj_raw.get('name', '')}),
        "page_title": character_for_template.get('name', 'Detail Resonator')
    }
    return render(request, 'landingpage/resonator.html', context)