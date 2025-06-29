import os
import json
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.urls import reverse
from django.http import Http404 

from .models import Resonator 

def format_folder(name):
    # PERBAIKAN: Tambahkan penanganan tanda hubung jika ada di nama folder Anda
    # Juga tangani jika ada spasi atau karakter khusus lainnya untuk nama folder
    formatted_name = name.replace(' ', '_').replace('-', '_').replace("'", "").replace(".", "") # Tambahan untuk membersihkan nama folder
    return formatted_name.strip() # Hapus spasi di awal/akhir

def load_resonator_data():
    json_filepath = os.path.join(settings.BASE_DIR, 'data', 'resonators_data.json')
    if os.path.exists(json_filepath):
        try:
            with open(json_filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {json_filepath}: {e}")
        except FileNotFoundError: # Ini sebenarnya ditangani oleh os.path.exists, tapi tidak ada salahnya
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
    all_resonators_db = Resonator.objects.all().order_by('name')
    char_cards = []
    for char_db_obj in all_resonators_db:
        # Nama folder akan persis sama dengan nama dari DB
        folder_name = format_folder(char_db_obj.name) 
        
        # Path URL untuk wallpaper karakter
        wallpaper_path = f"{settings.MEDIA_URL}resonator/{folder_name}/Wallpaper.png"
        
        # URL detail akan menggunakan nama karakter mentah
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

def resonators(request, name): # <--- Parameter fungsi view ini sudah benar: 'name'
    # 1. Cari karakter di database berdasarkan nama (dari URL)
    try:
        char_db_obj = get_object_or_404(Resonator, name__iexact=name) 
    except Http404: 
        raise Http404(f"Karakter '{name}' tidak ditemukan di database.")

    # 2. Muat SEMUA data detail dari resonators_data.json
    all_resonators_json_data = load_resonator_data()
    
    # 3. Cari detail lengkap karakter di data JSON berdasarkan nama karakter dari DB
    char_obj_raw = None
    for data_from_json in all_resonators_json_data:
        # Bandingkan nama karakter dari DB dengan 'name' di JSON (case-insensitive)
        # Menggunakan 'name' (huruf kecil) sesuai contoh JSON Anda
        if data_from_json.get('name', '').lower() == char_db_obj.name.lower(): 
            char_obj_raw = data_from_json
            break
    
    if not char_obj_raw:
        print(f"ERROR: Data detail JSON untuk karakter '{char_db_obj.name}' tidak ditemukan di resonators_data.json.")
        raise Http404("Detail karakter tidak ditemukan.") 

    # --- Proses char_obj_raw untuk membuat kamus yang ramah template ---
    character_for_template = {}

    # Konversi kunci JSON ke snake_case untuk akses template, tambahkan default
    for key, value in char_obj_raw.items():
        # Mengonversi kunci JSON (misal "weapon_type") ke snake_case (tetap weapon_type)
        # Jika ada kunci "Name", akan menjadi "name"
        new_key = key.lower().replace(' ', '_').replace('-', '_')
        character_for_template[new_key] = value

    # Pastikan semua kunci yang diharapkan template ada, dengan nilai default
    # Ini opsional jika loop di atas sudah cukup, tapi bagus untuk memastikan
    # jika ada perbedaan penamaan yang tidak tertangkap oleh loop.
    # Saya akan mengasumsikan kunci JSON Anda semua huruf kecil seperti contoh.
    character_for_template['name'] = character_for_template.get('name', 'N/A')
    character_for_template['codename'] = character_for_template.get('codename', 'N/A')
    character_for_template['birthday'] = character_for_template.get('birthday', 'N/A')
    character_for_template['sex'] = character_for_template.get('sex', 'N/A')
    character_for_template['birthplace'] = character_for_template.get('birthplace', 'N/A')
    character_for_template['affiliation'] = character_for_template.get('affiliation', 'N/A')
    character_for_template['attribute'] = character_for_template.get('attribute', 'N/A')
    character_for_template['weapon'] = character_for_template.get('weapon_type', 'N/A') # Menggunakan 'weapon_type' dari JSON
    character_for_template['hp'] = character_for_template.get('hp', 0)
    character_for_template['atk'] = character_for_template.get('atk', 0)
    character_for_template['def'] = character_for_template.get('def', 0)
    character_for_template['energy'] = character_for_template.get('energy', 0)
    
    # Penanganan 'role_name' (list)
    roles = character_for_template.get('role_name', [])
    character_for_template['role'] = character_for_template.get('role_name', [])
    if not isinstance(character_for_template['role'], list):
        character_for_template['role'] = []
    
    character_for_template['rarity'] = character_for_template.get('rarity', 0)
    
    # Penanganan 'titles' (list)
    titles = character_for_template.get('titles', [])
    character_for_template['title'] = titles[0] if isinstance(titles, list) and titles else 'N/A'
    
    character_for_template['quote'] = character_for_template.get("quote", "No description available.")

    # Ambil nilai 'name' dari char_obj_raw untuk folder gambar
    folder_name_for_images = format_folder(char_obj_raw.get('name', 'unknown')) 
    images = {
        "render": f"{settings.MEDIA_URL}resonator/{folder_name_for_images}/Render.png",
    }

    icon_chars_data = [] 
    
    # Logika untuk varian Rover
    if "rover -" in char_obj_raw.get('name', '').lower(): # Menggunakan 'name'
        rover_variants = sorted([
            data for data in all_resonators_json_data 
            if data.get('name', '').lower().startswith('rover -') # Menggunakan 'name'
        ], key=lambda x: x.get('name', '')) # Menggunakan 'name'

        for variant_json_data in rover_variants:
            icon_folder = format_folder(variant_json_data.get('name', '')) 
            icon_url = f"{settings.MEDIA_URL}resonator/{icon_folder}/Icon.png" 
            
            icon_detail_url = reverse('resonators:resonator_detail', kwargs={'name': variant_json_data.get('name', '')})
            
            is_active_icon = (variant_json_data.get('name', '').lower() == char_db_obj.name.lower()) 

            icon_chars_data.append({
                'icon_url': icon_url,
                'character_name': variant_json_data.get('name', ''),
                'detail_url': icon_detail_url,
                'is_active': is_active_icon,
            })
    else: 
        icon_folder = format_folder(char_obj_raw.get('name', '')) # Menggunakan 'name'
        icon_url = f"{settings.MEDIA_URL}resonator/{icon_folder}/Icon.png"
        
        icon_detail_url = reverse('resonators:resonator_detail', kwargs={'name': char_obj_raw.get('name', '')}) # Menggunakan 'name'

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
        "builder_url": reverse('build:character_builder', kwargs={'name': char_obj_raw.get('name', '')}), # Menggunakan 'name'
        "page_title": character_for_template.get('name', 'Detail Resonator') # Tambahkan page_title
    }
    return render(request, 'landingpage/resonator.html', context)