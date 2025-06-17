import os
import json
from django.conf import settings

def load_json_data(filename):
    json_filepath = os.path.join(settings.BASE_DIR, 'data', filename)
    if os.path.exists(json_filepath):
        try:
            with open(json_filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
            print(f"Error loading {filename}: {e}")
    else:
        print(f"JSON file NOT found at: {json_filepath}")
    return []

def load_echos_data():
    return load_json_data('echos_data.json')

def load_weapons_data():
    return load_json_data('weapons.json')

def load_sonatas_data():
    return load_json_data('sonatas_data.json')

def load_resonator_data():
    return load_json_data('resonators_data.json')

def load_builds_data():
    return load_json_data('builds_data.json')