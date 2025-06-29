from django.shortcuts import render
import json
from django.conf import settings
import os
from django.http import Http404

def load_weapon_data():
    json_path = os.path.join(settings.BASE_DIR, 'data', 'weapons_data.json')
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading weapon data: {e}")
        return []

def get_weapon_for_template(weapon_name):
    all_weapons_data = load_weapon_data()
    
    # Cari senjata di JSON
    weapon_obj_raw = None
    for data_from_json in all_weapons_data:
        if data_from_json.get('name', '').lower() == weapon_name.lower():
            weapon_obj_raw = data_from_json
            break
    
    if not weapon_obj_raw:
        print(f"ERROR: Data senjata '{weapon_name}' tidak ditemukan di weapons_data.json")
        raise Http404("Data senjata tidak ditemukan")

    # Proses data untuk template
    weapon_for_template = {}
    
    # Konversi semua key ke snake_case dan beri nilai default
    for key, value in weapon_obj_raw.items():
        new_key = key.lower().replace(' ', '_').replace('-', '_')
        weapon_for_template[new_key] = value

    # Pastikan field penting ada
    weapon_for_template['name'] = weapon_for_template.get('name', 'Unknown Weapon')
    weapon_for_template['codename'] = weapon_for_template.get('codename', 'N/A')
    weapon_for_template['rarity'] = weapon_for_template.get('rarity', 0)
    weapon_for_template['type'] = weapon_for_template.get('type', 'Unknown Type')
    weapon_for_template['base_atk'] = weapon_for_template.get('base_atk', 0)
    weapon_for_template['secondary_stat'] = weapon_for_template.get('secondary_stat', 'N/A')
    weapon_for_template['secondary_value'] = weapon_for_template.get('secondary_value', '0%')
    weapon_for_template['passive_skill'] = weapon_for_template.get('passive_skill', 'No skill description')
    
    return weapon_for_template