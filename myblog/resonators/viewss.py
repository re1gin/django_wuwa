import os
import json
from django.shortcuts import render # get_object_or_404 tidak lagi diperlukan
from django.conf import settings
from django.urls import reverse
from django.http import Http404

# Model Resonator tidak lagi diperlukan karena tidak lagi berinteraksi dengan database
# from .models import Resonator 

def format_folder(name):
    """
    Mengubah nama karakter menjadi format nama folder (spasi diganti underscore).
    """
    formatted_name = name.replace(' ', '_')
    return formatted_name

def load_resonator_data():
    """
    Memuat data resonator dari file JSON statis.
    Mencetak pesan kesalahan jika ada masalah saat membaca file.
    """
    json_filepath = os.path.join(settings.BASE_DIR, 'data', 'resonators_data.json')
    if os.path.exists(json_filepath):
        try:
            with open(json_filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {json_filepath}: {e}")
        except FileNotFoundError: # Seharusnya tidak terpanggil jika os.path.exists sudah cek
            print(f"JSON file not found at {json_filepath}")
        except Exception as e:
            print(f"An unexpected error occurred while loading JSON: {e}")
    else:
        print(f"JSON file NOT found at: {json_filepath}")
    return [] # Mengembalikan list kosong jika ada masalah atau file tidak ditemukan

def resonator_selection(request):
    """
    Menampilkan halaman pemilihan karakter.
    Mengambil semua data resonator dari file JSON statis
    untuk menampilkan kartu karakter.
    """
    # Mengambil semua data resonator dari JSON, bukan dari database
    all_resonators_json_data = load_resonator_data()
    
    # Urutkan berdasarkan nama karakter untuk tampilan yang konsisten
    # Pastikan 'Name' ada di setiap objek JSON
    sorted_resonators = sorted(all_resonators_json_data, key=lambda x: x.get('Name', '').lower())

    char_cards = []
    for char_json_obj in sorted_resonators:
        char_name = char_json_obj.get('Name')
        if not char_name: # Lewati jika tidak ada nama
            continue

        # Nama folder akan menggunakan nama karakter yang diformat
        folder_name = format_folder(char_name) 
        
        # Path URL untuk wallpaper karakter
        wallpaper_path = f"{settings.STATIC_URL}resonator/{folder_name}/Wallpaper.png"
        
        # URL detail akan menggunakan nama karakter mentah dari JSON
        detail_url = reverse('resonators:resonator_detail', kwargs={'character_name': char_name})

        char_cards.append({
            'name': char_name,
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
    Mengambil semua data karakter dari file JSON secara penuh.
    """
    # Muat SEMUA data detail dari resonators_data.json
    all_resonators_json_data = load_resonator_data()
    
    # Cari detail lengkap karakter di data JSON berdasarkan character_name dari URL
    char_obj_raw = None
    for data_from_json in all_resonators_json_data:
        # Bandingkan nama karakter dari JSON dengan character_name dari URL (case-insensitive)
        if data_from_json.get('Name', '').lower() == character_name.lower(): 
            char_obj_raw = data_from_json
            break
    
    # Jika karakter tidak ditemukan di JSON, lempar Http404
    if not char_obj_raw:
        print(f"ERROR: Data detail JSON untuk karakter '{character_name}' tidak ditemukan di resonators_data.json.")
        raise Http404(f"Detail karakter '{character_name}' tidak ditemukan.") 

    # --- Proses char_obj_raw untuk membuat kamus yang ramah template ---
    character_for_template = {}

    # Konversi kunci JSON ke snake_case untuk akses template, tambahkan default
    for key, value in char_obj_raw.items():
        new_key = key.lower().replace(' ', '_').replace('-', '_')
        character_for_template[new_key] = value

    # Pastikan semua kunci yang diharapkan template ada, dengan nilai default
    # Menggunakan .get() dengan nilai default untuk mencegah KeyError
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
    # Handle 'Title' sebagai list, ambil elemen pertama atau default string kosong
    character_for_template['title'] = char_obj_raw.get('Title', [''])[0] if isinstance(char_obj_raw.get('Title'), list) else char_obj_raw.get('Title', 'N/A')
    character_for_template['quote'] = char_obj_raw.get("Quote", "No description available.")

    # Path untuk gambar render akan menggunakan nama karakter dari JSON yang diformat
    folder_name_for_images = char_obj_raw.get('Name', 'unknown') 
    images = {
        "render": f"{settings.STATIC_URL}resonator/{format_folder(folder_name_for_images)}/Render.png",
    }

    icon_chars_data = [] 
    
    # Logika untuk varian Rover (masih akan mengambil dari JSON)
    if "rover -" in char_obj_raw.get('Name', '').lower():
        rover_variants = sorted([
            data for data in all_resonators_json_data 
            if data.get('Name', '').lower().startswith('rover -')
        ], key=lambda x: x.get('Name', ''))

        for variant_json_data in rover_variants:
            icon_char_name = variant_json_data.get('Name', '')
            icon_folder = format_folder(icon_char_name) 
            icon_url = f"{settings.STATIC_URL}resonator/{icon_folder}/Icon.png" 
            
            icon_detail_url = reverse('resonators:resonator_detail', kwargs={'character_name': icon_char_name})
            
            # Periksa apakah ikon ini adalah karakter yang sedang aktif ditampilkan
            is_active_icon = (icon_char_name.lower() == character_name.lower()) 

            icon_chars_data.append({
                'icon_url': icon_url,
                'character_name': icon_char_name,
                'detail_url': icon_detail_url,
                'is_active': is_active_icon,
            })
    else: 
        # Jika bukan Rover, hanya tampilkan ikon karakter saat ini
        icon_char_name = char_obj_raw.get('Name', '')
        icon_folder = format_folder(icon_char_name)
        icon_url = f"{settings.STATIC_URL}resonator/{icon_folder}/Icon.png"
        
        icon_detail_url = reverse('resonators:resonator_detail', kwargs={'character_name': icon_char_name})

        icon_chars_data.append({
            'icon_url': icon_url,
            'character_name': icon_char_name,
            'detail_url': icon_detail_url,
            'is_active': True, 
        })

    context = {
        "character": character_for_template,
        "images": images,
        "all_characters_for_icons": icon_chars_data,
        "builder_url": reverse('build:character_builder', kwargs={'character_name': char_obj_raw.get('Name', '')}), 
    }
    return render(request, 'landingpage/resonator.html', context)