import os
import json
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.urls import reverse
from django.http import Http404 

from .models import Resonator 

def format_folder(name):
    formatted_name = name.replace(' ', '_')
    return formatted_name

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
    """
    Menampilkan halaman pemilihan karakter, menampilkan semua resonator
    yang ada di database sebagai kartu.
    """
    all_resonators_db = Resonator.objects.all().order_by('character_name')
    char_cards = []
    for char_db_obj in all_resonators_db:
        # Nama folder akan persis sama dengan character_name
        folder_name = format_folder(char_db_obj.character_name) 
        
        # Path URL untuk wallpaper karakter
        wallpaper_path = f"{settings.STATIC_URL}resonator/{folder_name}/Wallpaper.png"
        
        # URL detail akan menggunakan nama karakter mentah
        # Django akan otomatis meng-URL-encode spasi dan karakter khusus lainnya.
        detail_url = reverse('resonators:resonator_detail', kwargs={'character_name': char_db_obj.character_name})

        char_cards.append({
            'name': char_db_obj.character_name,
            'wallpaper_url': wallpaper_path,
            'detail_url': detail_url,
        })
    
    context = {
        'characters': char_cards,
        'page_title': 'Pilih Resonator Anda' 
    }
    return render(request, 'landingpage/resonators_selection.html', context)

def resonators(request, character_name):
    """
    Menampilkan halaman detail untuk satu karakter resonator.
    Mengambil data dari database dan detail lengkap dari file JSON.
    """
    # 1. Cari karakter di database berdasarkan character_name (persis dari URL)
    # Gunakan __exact atau tanpa itu jika Anda yakin case-sensitive cocok.
    # __iexact (case-insensitive exact) tetap aman jika ada variasi kapitalisasi.
    try:
        char_db_obj = Resonator.objects.get(character_name__iexact=character_name)
    except Resonator.DoesNotExist:
        raise Http404(f"Karakter '{character_name}' tidak ditemukan di database.")

    # 2. Muat SEMUA data detail dari resonators_data.json
    all_resonators_json_data = load_resonator_data()
    
    # 3. Cari detail lengkap karakter di data JSON berdasarkan nama karakter dari DB
    char_obj_raw = None
    for data_from_json in all_resonators_json_data:
        # Bandingkan nama karakter dari DB dengan 'Name' di JSON (case-insensitive)
        if data_from_json.get('Name', '').lower() == char_db_obj.character_name.lower(): 
            char_obj_raw = data_from_json
            break
    
    if not char_obj_raw:
        # Jika karakter ada di DB tapi tidak ada di JSON, lempar Http404
        print(f"ERROR: Data detail JSON untuk karakter '{char_db_obj.character_name}' tidak ditemukan di resonators_data.json.")
        raise Http404("Detail karakter tidak ditemukan.") 

    # --- Proses char_obj_raw untuk membuat kamus yang ramah template ---
    character_for_template = {}

    # Konversi kunci JSON ke snake_case untuk akses template, tambahkan default
    for key, value in char_obj_raw.items():
        new_key = key.lower().replace(' ', '_').replace('-', '_')
        character_for_template[new_key] = value

    # Pastikan semua kunci yang diharapkan template ada, dengan nilai default
    character_for_template['name'] = char_obj_raw.get('Name', 'N/A')
    character_for_template['codename'] = char_obj_raw.get('Codename', 'N/A')
    character_for_template['birthday'] = char_obj_raw.get('Birthday', 'N/A')
    character_for_template['sex'] = char_obj_raw.get('Sex', 'N/A')
    character_for_template['birthplace'] = char_obj_raw.get('Birthplace', 'N/A')
    character_for_template['affiliation'] = char_obj_raw.get('Affiliation', 'N/A')
    character_for_template['attribute'] = char_obj_raw.get('Attribute', 'N/A')
    character_for_template['weapon'] = char_obj_raw.get('Weapon', 'N/A')
    character_for_template['hp'] = char_obj_raw.get('HP', 0)
    character_for_template['atk'] = char_obj_raw.get('ATK', 0)
    character_for_template['def'] = char_obj_raw.get('DEF', 0)
    character_for_template['energy'] = char_obj_raw.get('Energy', 0)
    character_for_template['role'] = char_obj_raw.get('Role', 'N/A')
    character_for_template['rarity'] = char_obj_raw.get('Rarity', 0)
    character_for_template['title'] = char_obj_raw['Title'][0]
    character_for_template['quote'] = char_obj_raw.get("Quote", "No description available.")

    # Path untuk gambar render akan menggunakan nama mentah
    folder_name_for_images = char_obj_raw.get('Name', 'unknown') 
    images = {
        "render": f"{settings.STATIC_URL}resonator/{folder_name_for_images}/Render.png",
    }

    icon_chars_data = [] 
    
    # Logika untuk varian Rover
    if "rover -" in char_obj_raw.get('Name', '').lower():
        rover_variants = sorted([
            data for data in all_resonators_json_data 
            if data.get('Name', '').lower().startswith('rover -')
        ], key=lambda x: x.get('Name', ''))

        for variant_json_data in rover_variants:
            # Folder ikon akan menggunakan nama mentah varian
            icon_folder = variant_json_data.get('Name', '')
            icon_url = f"{settings.STATIC_URL}resonator/{icon_folder}/Icon.png" 
            
            # URL reverse akan menggunakan nama mentah varian
            icon_detail_url = reverse('resonators:resonator_detail', kwargs={'character_name': variant_json_data.get('Name', '')})
            
            # Periksa apakah ikon ini adalah karakter yang sedang aktif ditampilkan
            is_active_icon = (variant_json_data.get('Name', '').lower() == char_db_obj.character_name.lower()) 

            icon_chars_data.append({
                'icon_url': icon_url,
                'character_name': variant_json_data.get('Name', ''),
                'detail_url': icon_detail_url,
                'is_active': is_active_icon,
            })
    else: 
        # Jika bukan Rover, hanya tampilkan ikon karakter saat ini
        icon_folder = char_obj_raw.get('Name', '')
        icon_url = f"{settings.STATIC_URL}resonator/{icon_folder}/Icon.png"
        
        # URL reverse akan menggunakan nama mentah karakter saat ini
        icon_detail_url = reverse('resonators:resonator_detail', kwargs={'character_name': char_obj_raw.get('Name', '')})

        icon_chars_data.append({
            'icon_url': icon_url,
            'character_name': char_obj_raw.get('Name', ''),
            'detail_url': icon_detail_url,
            'is_active': True, 
        })

    context = {
        "character": character_for_template,
        "images": images,
        "all_characters_for_icons": icon_chars_data,
        # Untuk URL builder, juga gunakan nama mentah
        "builder_url": reverse('build:character_builder', kwargs={'character_name': char_obj_raw.get('Name', '')}), 
    }
    return render(request, 'landingpage/resonator.html', context)