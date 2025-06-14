import os
import json
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.urls import reverse

# Import model Resonator yang disederhanakan (hanya id dan character_name)
from .models import Resonator 

def format_folder(name):
    """
    Memformat nama karakter menjadi nama folder yang sesuai
    dengan mengganti spasi dengan garis bawah dan menghapus apostrof dan koma,
    kemudian mengubahnya menjadi huruf kecil.
    """
    formatted_name = name.replace(' ', '_').replace('’', '').replace(',', '')
    return formatted_name.lower()

def load_resonator_data():
    """
    Memuat semua data resonator dari file 'resonators_data.json'.
    Mengembalikan daftar kamus (list of dictionaries).
    """
    json_filepath = os.path.join(settings.BASE_DIR, 'data', 'resonators_data.json')
    if os.path.exists(json_filepath):
        try:
            with open(json_filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error saat mendekode JSON dari {json_filepath}: {e}")
        except FileNotFoundError:
            print(f"File JSON tidak ditemukan di {json_filepath}")
        except Exception as e:
            print(f"Terjadi kesalahan tak terduga: {e}")
    else:
        print(f"File JSON TIDAK ditemukan di: {json_filepath}")
    return []


def resonator_selection(request):
    all_resonators_db = Resonator.objects.all().order_by('character_name')
    char_cards = []
    for char_db_obj in all_resonators_db:
        folder_name = format_folder(char_db_obj.character_name)
        wallpaper_path = f"{settings.STATIC_URL}resonators/{folder_name}/Wallpaper.png"
        
        detail_url = reverse('resonators:resonator_detail', kwargs={'character_id': char_db_obj.id})

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

def resonators(request, character_id):
    # 1. Validasi character_id dengan database (memastikan ID yang diberikan valid)
    char_db_obj = get_object_or_404(Resonator, id=character_id) 
    
    # 2. Muat SEMUA data detail dari resonators_data.json
    all_resonators_json_data = load_resonator_data()
    
    # 3. Cari detail lengkap karakter di data JSON berdasarkan 'id' dari database
    char_obj_raw = None
    for data_from_json in all_resonators_json_data:
        # Cocokkan ID dari DB dengan 'id' di JSON (pastikan tipe data cocok)
        if str(data_from_json.get('id')) == str(char_db_obj.id): 
            char_obj_raw = data_from_json
            break
    
    if not char_obj_raw:
        # Jika karakter ada di DB tapi tidak ada di JSON, ini adalah kesalahan data.
        # Pertimbangkan untuk mencatat kesalahan ini untuk tujuan debugging.
        return get_object_or_404(None) 

    # --- Proses char_obj_raw untuk membuat kamus yang ramah template ---
    character_for_template = {}

    # Salin semua data dari char_obj_raw ke character_for_template
    # Konversi kunci dengan spasi atau tanda hubung menjadi snake_case untuk akses konsisten di template
    for key, value in char_obj_raw.items():
        new_key = key.lower().replace(' ', '_').replace('-', '_')
        character_for_template[new_key] = value

    # Pastikan kunci spesifik yang mungkin digunakan langsung di template
    # atau memerlukan kapitalisasi asli secara eksplisit ada atau dipetakan.
    # Ini membantu jika template Anda mengharapkan kapitalisasi yang tepat (misalnya, `character.Character`)
    # dan untuk memberikan nilai default jika kunci tidak ada di JSON.
    character_for_template['name'] = char_obj_raw.get('Name') # Gunakan 'Name' dari JSON sekarang
    character_for_template['codename'] = char_obj_raw.get('Codename')
    character_for_template['birthday'] = char_obj_raw.get('Birthday')
    character_for_template['sex'] = char_obj_raw.get('Sex')
    character_for_template['birthplace'] = char_obj_raw.get('Birthplace')
    character_for_template['affiliation'] = char_obj_raw.get('Affiliation')
    character_for_template['attribute'] = char_obj_raw.get('Attribute')
    character_for_template['weapon'] = char_obj_raw.get('Weapon')
    character_for_template['hp'] = char_obj_raw.get('HP')
    character_for_template['atk'] = char_obj_raw.get('ATK')
    character_for_template['def'] = char_obj_raw.get('DEF')
    character_for_template['energy'] = char_obj_raw.get('Energy')
    character_for_template['role'] = char_obj_raw.get('Role')
    character_for_template['rarity'] = char_obj_raw.get('Rarity')
    
    # Tangani secara eksplisit 'Title' dan 'Quote'
    character_for_template['title'] = char_obj_raw.get("Title", ["N/A"])
    character_for_template['quote'] = char_obj_raw.get("Quote", "No description available.")

    # Path untuk gambar render
    folder_name = format_folder(char_obj_raw.get('Name')) # Gunakan 'Name' dari JSON sekarang
    images = {
        "render": f"{settings.STATIC_URL}resonators/{folder_name}/Render.png",
    }

    icon_chars_data = [] 
    
    # Logika untuk varian Rover (ambil dari data JSON yang sudah dimuat)
    # Menggunakan 'name' untuk perbandingan sekarang, sesuai dengan perubahan struktur JSON
    if "rover -" in char_obj_raw.get('Name', '').lower():
        # Filter dan urutkan varian Rover dari data JSON lengkap
        rover_variants = sorted([
            data for data in all_resonators_json_data 
            if data.get('Name', '').lower().startswith('rover -')
        ], key=lambda x: x.get('Name')) # Urutkan berdasarkan 'Name'

        for variant_json_data in rover_variants:
            icon_folder = format_folder(variant_json_data.get('Name'))
            icon_url = f"{settings.STATIC_URL}resonators/{icon_folder}/Icon.png" 
            
            # Gunakan 'id' dari JSON untuk pencarian URL reverse
            icon_detail_url = reverse('resonators:resonator_detail', kwargs={'character_id': variant_json_data.get('id')})
            # Bandingkan dengan ID dari DB, pastikan tipenya cocok jika diperlukan
            is_active_icon = (str(variant_json_data.get('id')) == str(char_db_obj.id)) 

            icon_chars_data.append({
                'icon_url': icon_url,
                'character_name': variant_json_data.get('Name'), # Gunakan 'Name'
                'detail_url': icon_detail_url,
                'is_active': is_active_icon,
            })
    else: 
        # Jika bukan Rover, hanya tampilkan ikon karakter saat ini
        icon_folder = format_folder(char_obj_raw.get('Name'))
        icon_url = f"{settings.STATIC_URL}resonators/{icon_folder}/Icon.png"
        
        icon_detail_url = reverse('resonators:resonator_detail', kwargs={'character_id': char_db_obj.id})

        icon_chars_data.append({
            'icon_url': icon_url,
            'character_name': char_obj_raw.get('Name'),
            'detail_url': icon_detail_url,
            'is_active': True, 
        })

    context = {
        "character": character_for_template, # Ini kamus yang berisi semua detail dari JSON
        "images": images,
        "all_characters_for_icons": icon_chars_data,
        "builder_url": reverse('build:character_builder', kwargs={'character_name': char_obj_raw.get('Name')}), 
    }
    return render(request, 'landingpage/resonator.html', context)