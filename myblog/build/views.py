import json
from datetime import datetime
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt

from build.constants import (
    HP_NORM, ATK_NORM, DEF_NORM, ENERGY_NORM, CRIT_RATE_NORM, CRIT_DMG_NORM,
    RESONATOR_RATING_WEIGHTS, SKILL_LEVEL_FIELDS, DEFAULT_SKILL_LEVEL
)
from build.fuzzy_logic.engine import calculate_fuzzy_stat_quality, get_overall_build_rating_text
from build.fuzzy_logic.utils import format_comparison_difference, get_interpolated_color
from resonators.models import Resonator
from weapon.models import Weapon
from echo.models import Sonata, Echo

def format_folder(name):
    return name.replace(' ', '_')

def get_icon_chars_data(current_char_obj=None):
    icon_chars_data = []
    all_resonators = Resonator.objects.all().order_by('name')
    for resonator in all_resonators:
        folder_name = format_folder(resonator.name)
        icon_url = f"{settings.MEDIA_URL}resonator/{folder_name}/Icon.png"
        try:
            icon_detail_url = reverse('build:character_builder', kwargs={'name': resonator.name})
        except Exception: 
            icon_detail_url = '#'
        is_active_icon = current_char_obj and resonator.name == current_char_obj.name
        icon_chars_data.append({
            'icon_url': icon_url,
            'character_name': resonator.name,
            'detail_url': icon_detail_url,
            'is_active': is_active_icon,
        })
    return icon_chars_data

def get_item_details_ajax(request):
    item_type = request.POST.get('item_type')
    item_name = request.POST.get('item_name')
    selected_echo_name = request.POST.get('selected_echo_name')

    details = {}
    image_url = ""
    filtered_sonatas_data = []
    filtered_echos_data = list(Echo.objects.all().values('name'))

    if item_type == 'weapon':
        weapon_obj = Weapon.objects.filter(weapon_name=item_name).first()
        if weapon_obj:
            details = {
                'name': weapon_obj.weapon_name,
                'rarity': weapon_obj.rarity,
                'weapon_type': weapon_obj.weapon_type.name if weapon_obj.weapon_type else "N/A"
            }
            image_url = weapon_obj.icon_image.url if weapon_obj.icon_image else ""
    elif item_type == 'echo':
        echo_obj = Echo.objects.filter(name=item_name).first()
        if echo_obj:
            details = {
                'name': echo_obj.name,
                'cost': echo_obj.cost,
            }
            image_url = echo_obj.icon_echo.url if echo_obj.icon_echo else ""
            filtered_sonatas_data = list(echo_obj.sonatas.all().values('name'))
        else:
            filtered_sonatas_data = []
    elif item_type == 'sonata':
        sonata_obj = Sonata.objects.filter(name=item_name).first()
        if sonata_obj:
            details = {
                'name': sonata_obj.name,
            }
            image_url = sonata_obj.icon_sonata.url if sonata_obj.icon_sonata else ""
        
    if selected_echo_name:
        selected_echo_from_ajax = Echo.objects.filter(name=selected_echo_name).first()
        if selected_echo_from_ajax:
            filtered_sonatas_data = list(selected_echo_from_ajax.sonatas.all().values('name'))
        else:
            filtered_sonatas_data = []
    else:
        filtered_sonatas_data = list(Sonata.objects.all().values('name'))

    return JsonResponse({
        'details': details,
        'image_url': image_url,
        'filtered_echos': filtered_echos_data,
        'filtered_sonatas': filtered_sonatas_data,
    })

def character_builder_view(request, name):
    char_obj = get_object_or_404(Resonator, name__iexact=name)
    
    # Inisialisasi user_input_stats dengan hanya field yang relevan
    user_input_stats = {
        'hp': 0.0, 'attack': 0.0, 'defense': 0.0, 'energy': 0.0, 'crit_rate': 0.0, 'crit_dmg': 0.0,
        'basic_atk_dmg_bonus': 0.0, 
        'resonance_skill_dmg_bonus': 0.0,
        'resonance_lib_dmg_bonus': 0.0, 'healing_bonus': 0.0, 'attribute_dmg_bonus': 0.0,
        'character_level': 90, # Ini sekarang statis di HTML, tidak dari POST
        'weapon_level': 90,   # Ini sekarang statis di HTML, tidak dari POST
        'selected_weapon': '', 'selected_echo': '', 'selected_sonata': '',
    }

    # Penanganan sesi: hapus sesi saat GET request, atau update jika ada sesi yang cocok
    if request.method == 'GET':
        request.session.pop('user_input_stats', None)
        request.session.pop('character_name_for_comparison', None)
    
    if 'user_input_stats' in request.session and request.session.get('character_name_for_comparison') == char_obj.name:
        user_input_stats.update(request.session['user_input_stats'])

    if request.method == 'POST':
        form_is_valid = True

        # Konfigurasi untuk input angka yang ada di HTML
        number_fields_config = {
            'hp': {'type': float, 'min': 0.0, 'label': 'HP'},
            'attack': {'type': float, 'min': 0.0, 'label': 'ATK'},
            'defense': {'type': float, 'min': 0.0, 'label': 'DEF'},
            'energy': {'type': float, 'min': 0.0, 'label': 'ENERGY REGEN'},
            'crit_rate': {'type': float, 'min': 0.0, 'label': 'CRITICAL RATE'},
            'crit_dmg': {'type': float, 'min': 0.0, 'label': 'CRITICAL DAMAGE'},
            'basic_atk_dmg_bonus': {'type': float, 'min': 0.0, 'label': 'Basic Attack DMG Bonus'},
            'resonance_skill_dmg_bonus': {'type': float, 'min': 0.0, 'label': 'Resonance Skill DMG Bonus'},
            'resonance_lib_dmg_bonus': {'type': float, 'min': 0.0, 'label': 'Resonance Liberation DMG Bonus'},
            'healing_bonus': {'type': float, 'min': 0.0, 'label': 'Healing Bonus'},
            'attribute_dmg_bonus': {'type': float, 'min': 0.0, 'label': f"{char_obj.attribute.name} DMG Bonus"},
        }

        for field_name, config in number_fields_config.items():
            value = request.POST.get(field_name)
            label = config['label']
            value_type = config['type']
            min_val = config.get('min', 0.0)
            try:
                if value is None or value.strip() == '':
                    processed_value = min_val if value_type == float else int(min_val)
                else:
                    processed_value = value_type(value)
                if processed_value < min_val:
                    messages.error(request, f"{label} tidak boleh kurang dari {min_val}.")
                    form_is_valid = False
                user_input_stats[field_name] = processed_value
            except ValueError:
                messages.error(request, f"Input '{label}' harus berupa angka yang valid.")
                form_is_valid = False
                user_input_stats[field_name] = value # Simpan nilai yang salah agar form bisa menampilkan error

        # Ambil nilai select box
        user_input_stats['selected_weapon'] = request.POST.get('selected_weapon', '')
        user_input_stats['selected_echo'] = request.POST.get('selected_echo', '')
        user_input_stats['selected_sonata'] = request.POST.get('selected_sonata', '')

        # Validasi pilihan senjata
        if user_input_stats['selected_weapon']:
            if not Weapon.objects.filter(weapon_name=user_input_stats['selected_weapon']).exists():
                messages.error(request, f"Senjata '{user_input_stats['selected_weapon']}' tidak valid.")
                user_input_stats['selected_weapon'] = ''
                form_is_valid = False

        # Validasi pilihan Echo dan Sonata
        selected_echo_name = user_input_stats['selected_echo']
        selected_sonata_name = user_input_stats['selected_sonata']

        if selected_echo_name:
            selected_echo_obj_from_post = Echo.objects.filter(name=selected_echo_name).first()
            if selected_echo_obj_from_post:
                if selected_sonata_name:
                    if not selected_echo_obj_from_post.sonatas.filter(name=selected_sonata_name).exists():
                        messages.error(request, f"Sonata '{selected_sonata_name}' tidak valid untuk Echo '{selected_echo_name}'. Pilihan direset.")
                        user_input_stats['selected_sonata'] = ''
                        form_is_valid = False
            else:
                messages.error(request, f"Echo '{selected_echo_name}' tidak ditemukan. Pilihan Echo dan Sonata direset.")
                user_input_stats['selected_echo'] = ''
                user_input_stats['selected_sonata'] = ''
                form_is_valid = False
        elif selected_sonata_name: # Jika sonata dipilih tapi echo tidak
            messages.error(request, "Sonata tidak dapat dipilih tanpa Echo yang dipilih. Sonata direset.")
            user_input_stats['selected_sonata'] = ''
            form_is_valid = False

        # Simpan status input pengguna ke sesi
        request.session['user_input_stats'] = user_input_stats
        request.session['character_name_for_comparison'] = char_obj.name

        # Redirect jika formulir valid dan tombol 'NILAI BUILD' ditekan
        if form_is_valid and 'NILAI BUILD' in request.POST:
            return redirect('build:review_build_page', name=char_obj.name)

    # Persiapan data untuk render template (GET atau POST dengan error)
    folder_name = format_folder(char_obj.name)
    image_path = f"{settings.MEDIA_URL}resonator/{folder_name}/"
    images = {"render": f"{image_path}Render.png"}
    all_characters_for_icons = get_icon_chars_data(char_obj)
    weapons_data_db = Weapon.objects.filter(weapon_type=char_obj.weapon_type).order_by('weapon_name')
    echos_data_db = Echo.objects.all().order_by('name')
    
    selected_echo_obj = None
    if user_input_stats['selected_echo']:
        selected_echo_obj = Echo.objects.filter(name=user_input_stats['selected_echo']).first()
        if selected_echo_obj:
            sonatas_data_db = selected_echo_obj.sonatas.all().order_by('name')
        else:
            # Jika echo yang dipilih tidak ditemukan, tampilkan semua sonata sebagai fallback
            sonatas_data_db = Sonata.objects.all().order_by('name')
    else:
        # Jika tidak ada echo yang dipilih, tampilkan semua sonata
        sonatas_data_db = Sonata.objects.all().order_by('name')

    selected_weapon_obj = None
    selected_sonata_obj = None

    if user_input_stats['selected_weapon']:
        selected_weapon_obj = Weapon.objects.filter(weapon_name=user_input_stats['selected_weapon']).first()
    
    # Pastikan selected_sonata_obj hanya diisi jika echo dan sonata valid
    if user_input_stats['selected_sonata'] and selected_echo_obj:
        temp_sonata_obj = Sonata.objects.filter(name=user_input_stats['selected_sonata']).first()
        if temp_sonata_obj and selected_echo_obj.sonatas.filter(name=temp_sonata_obj.name).exists():
            selected_sonata_obj = temp_sonata_obj
        else:
            # Jika sonata tidak valid untuk echo yang dipilih, reset
            user_input_stats['selected_sonata'] = ''
            selected_sonata_obj = None

    context = {
        "character": char_obj,
        "images": images,
        "all_characters_for_icons": all_characters_for_icons,
        "user_input_stats": user_input_stats,
        "weapons_data": weapons_data_db,
        "echos_data": echos_data_db,
        "sonatas_data": sonatas_data_db,
        "selected_weapon_obj": selected_weapon_obj,
        "selected_echo_obj": selected_echo_obj,
        "selected_sonata_obj": selected_sonata_obj,
    }
    return render(request, 'landingpage/character_builder.html', context)

@csrf_exempt
def reset_build_session(request):
    if request.method == 'POST':
        try:
            request.session.pop('user_input_stats', None)
            request.session.pop('character_name_for_comparison', None)
            return JsonResponse({'status': 'success', 'message': 'Sesi builder berhasil direset.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Gagal mereset sesi: {str(e)}'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Metode tidak diizinkan.'}, status=405)

def build_review_page(request, name):
    resonator = get_object_or_404(Resonator, name__iexact=name)
    folder_name = format_folder(resonator.name)
    image_path = f"{settings.MEDIA_URL}resonator/{folder_name}/"
    images = {"render": f"{image_path}Render.png"}
    roles_with_icons = resonator.role.all().values('name', 'icon_role')

    # Inisialisasi user_input_stats dari sesi, dengan kamus default yang diperbarui
    user_input_stats = request.session.get('user_input_stats', {
        'hp': 0.0, 'attack': 0.0, 'defense': 0.0, 'energy': 0.0,
        'crit_rate': 0.0, 'crit_dmg': 0.0,
        'basic_atk_dmg_bonus': 0.0,'resonance_skill_dmg_bonus': 0.0, 'resonance_lib_dmg_bonus': 0.0,
        'healing_bonus': 0.0,'attribute_dmg_bonus': 0.0,
        'character_level': 90, # Dipertahankan sebagai nilai statis dari builder
        'weapon_level': 90,   # Dipertahankan sebagai nilai statis dari builder
        'basic_atk_level': 10, # Ditambahkan kembali, default max level
        'resonance_skill_level': 10, # Ditambahkan kembali, default max level
        'forte_circuit_level': 10, # Ditambahkan kembali, default max level
        'resonance_liberation_level': 10, # Ditambahkan kembali, default max level
        'intro_skill_level': 10, # Ditambahkan kembali, default max level
        'selected_weapon': '',
        'selected_echo': '',
        'selected_sonata': '',
    })

    selected_weapon_obj = None
    if user_input_stats['selected_weapon']:
        selected_weapon_obj = Weapon.objects.filter(
            weapon_name=user_input_stats['selected_weapon']
        ).first()

    selected_echo_obj = None
    if user_input_stats['selected_echo']:
        selected_echo_obj = Echo.objects.filter(name=user_input_stats['selected_echo']).first()

    selected_sonata_obj = None
    # Kondisi disederhanakan
    if user_input_stats['selected_sonata'] and selected_echo_obj:
        selected_sonata_obj = selected_echo_obj.sonatas.filter(
            name=user_input_stats['selected_sonata']
        ).first()

    build_instance = None
    try:
        build_instance = resonator.ideal_build
    except ObjectDoesNotExist:
        pass

    ideal_hp = 0.0
    ideal_attack = 0.0
    ideal_defense = 0.0
    ideal_energy = 0.0
    ideal_crit_rate = 0.0
    ideal_crit_dmg = 0.0

    selected_weapon_obj_db = None
    selected_echo_obj_db = None
    selected_sonata_obj_db = None

    if build_instance:
        ideal_hp = build_instance.hp
        ideal_attack = build_instance.attack
        ideal_defense = build_instance.defense
        ideal_energy = build_instance.energy
        ideal_crit_rate = build_instance.crit_rate
        ideal_crit_dmg = build_instance.crit_dmg
        selected_weapon_obj_db = build_instance.ideal_weapon
        selected_echo_obj_db = build_instance.ideal_echo
        selected_sonata_obj_db = build_instance.ideal_sonata
    else:
        # Placeholder objek yang diperbarui
        selected_weapon_obj_db = type('Weapon', (object,), {
            'weapon_name': 'No Saved Weapon',
            'icon_image': type('ImageFile', (object,), {'url': '/static/combat/images/placeholder_weapon.png'}),
            'base_atk': 0.0, # Mengganti atk_value menjadi base_atk
            'rarity': 0, # Menambahkan rarity
        })()
        selected_echo_obj_db = type('Echo', (object,), {
            'name': 'No Saved Echo',
            'icon_echo': type('ImageFile', (object,), {'url': '/static/combat/images/placeholder_echo.png'}),
            'cost': 0, # Menambahkan cost
        })()
        selected_sonata_obj_db = type('Sonata', (object,), {
            'name': 'No Saved Sonata',
            'icon_sonata': type('ImageFile', (object,), {'url': '/static/combat/images/placeholder_sonata.png'}),
        })()

    resonator_roles = [r.name for r in resonator.role.all()]
    is_main_dps = 'Main Damage Dealer' in resonator_roles
    is_support_and_healer = 'Support and Healer' in resonator_roles

    overview_stats = []
    stats_config = [
        {'label': "HP", 'user_val': user_input_stats.get('hp', 0.0), 'ideal_val': ideal_hp, 'category': 'flat', 'is_percentage': False},
        {'label': "ATK", 'user_val': user_input_stats.get('attack', 0.0), 'ideal_val': ideal_attack, 'category': 'flat', 'is_percentage': False},
        {'label': "DEF", 'user_val': user_input_stats.get('defense', 0.0), 'ideal_val': ideal_defense, 'category': 'flat', 'is_percentage': False},
        {'label': "Energy Regen", 'user_val': user_input_stats.get('energy', 0.0), 'ideal_val': ideal_energy, 'category': 'percent', 'is_percentage': True},
        {'label': "Critical Rate", 'user_val': user_input_stats.get('crit_rate', 0.0), 'ideal_val': ideal_crit_rate, 'category': 'percent', 'is_percentage': True},
        {'label': "Critical Damage", 'user_val': user_input_stats.get('crit_dmg', 0.0), 'ideal_val': ideal_crit_dmg, 'category': 'percent', 'is_percentage': True},
    ]

    for stat in stats_config:
        user_val_float = float(stat['user_val'])
        current_ideal_val = float(stat['ideal_val'])
        user_val_vs_ideal_percent = 0
        if current_ideal_val > 0:
            user_val_vs_ideal_percent = (user_val_float / current_ideal_val) * 100
        elif current_ideal_val == 0 and user_val_float > 0:
            user_val_vs_ideal_percent = 200 # Nilai user ada tapi ideal 0, anggap sangat baik
        elif current_ideal_val == 0 and user_val_float == 0:
            user_val_vs_ideal_percent = 0 # Keduanya 0, netral atau tidak relevan
        interpolated_color_hex = get_interpolated_color(user_val_vs_ideal_percent)
        overview_stats.append({
            'label': stat['label'],
            'user_value': user_val_float,
            'ideal_value': current_ideal_val,
            'is_percentage': stat['is_percentage'],
            'color': interpolated_color_hex
        })

    status_differences = []
    status_differences.append(format_comparison_difference(ideal_hp, user_input_stats.get('hp', 0.0), "HP"))
    status_differences.append(format_comparison_difference(ideal_attack, user_input_stats.get('attack', 0.0), "ATK"))
    status_differences.append(format_comparison_difference(ideal_defense, user_input_stats.get('defense', 0.0), "DEF"))
    status_differences.append(format_comparison_difference(ideal_energy, user_input_stats.get('energy', 0.0), "Energy Regen", is_percentage=True))
    status_differences.append(format_comparison_difference(ideal_crit_rate, user_input_stats.get('crit_rate', 0.0), "Crit Rate", is_percentage=True))
    status_differences.append(format_comparison_difference(ideal_crit_dmg, user_input_stats.get('crit_dmg', 0.0), "Crit Dmg", is_percentage=True))
    status_differences.append(format_comparison_difference(0.0, user_input_stats.get('basic_atk_dmg_bonus', 0.0), "Basic ATK DMG", is_percentage=True))
    status_differences.append(format_comparison_difference(0.0, user_input_stats.get('resonance_skill_dmg_bonus', 0.0), "Skill DMG", is_percentage=True))
    status_differences.append(format_comparison_difference(0.0, user_input_stats.get('resonance_lib_dmg_bonus', 0.0), "Lib. DMG", is_percentage=True))
    status_differences.append(format_comparison_difference(0.0, user_input_stats.get('attribute_dmg_bonus', 0.0), "Attribute DMG", is_percentage=True))
    status_differences.append(format_comparison_difference(0.0, user_input_stats.get('healing_bonus', 0.0), "Healing Bonus", is_percentage=True))

    component_scores = {}

    level_score = 100
    character_level = int(user_input_stats.get('character_level', 90))
    if character_level < 90:
        level_score -= (90 - character_level) * 0.5
    component_scores['level'] = max(0, min(100, level_score))

    overall_stat_score = 0
    stat_weights_for_average = {
        'hp': 1.0, 'attack': 1.0, 'defense': 1.0, 'energy': 1.0,
        'crit_rate': 1.0, 'crit_dmg': 1.0,
        'basic_atk_dmg': 1.0,
        'resonance_skill_dmg': 1.0,
        'resonance_lib_dmg': 1.0,
        'attribute_dmg_bonus': 1.0,
        'healing_bonus': 1.0,
    }
    overall_stat_score += calculate_fuzzy_stat_quality(ideal_hp, user_input_stats.get('hp', 0.0), 'flat') * stat_weights_for_average['hp']
    overall_stat_score += calculate_fuzzy_stat_quality(ideal_attack, user_input_stats.get('attack', 0.0), 'flat') * stat_weights_for_average['attack']
    overall_stat_score += calculate_fuzzy_stat_quality(ideal_defense, user_input_stats.get('defense', 0.0), 'flat') * stat_weights_for_average['defense']
    overall_stat_score += calculate_fuzzy_stat_quality(ideal_energy, user_input_stats.get('energy', 0.0), 'percent') * stat_weights_for_average['energy']
    overall_stat_score += calculate_fuzzy_stat_quality(ideal_crit_rate, user_input_stats.get('crit_rate', 0.0), 'percent') * stat_weights_for_average['crit_rate']
    overall_stat_score += calculate_fuzzy_stat_quality(ideal_crit_dmg, user_input_stats.get('crit_dmg', 0.0), 'percent') * stat_weights_for_average['crit_dmg']
    overall_stat_score += calculate_fuzzy_stat_quality(0, user_input_stats.get('basic_atk_dmg_bonus', 0.0), 'bonus', is_main_dps) * stat_weights_for_average['basic_atk_dmg']
    overall_stat_score += calculate_fuzzy_stat_quality(0, user_input_stats.get('resonance_skill_dmg_bonus', 0.0), 'bonus', is_main_dps) * stat_weights_for_average['resonance_skill_dmg']
    overall_stat_score += calculate_fuzzy_stat_quality(0, user_input_stats.get('resonance_lib_dmg_bonus', 0.0), 'bonus', is_main_dps) * stat_weights_for_average['resonance_lib_dmg']
    overall_stat_score += calculate_fuzzy_stat_quality(0, user_input_stats.get('attribute_dmg_bonus', 0.0), 'bonus', is_main_dps) * stat_weights_for_average['attribute_dmg_bonus']
    overall_stat_score += calculate_fuzzy_stat_quality(0, user_input_stats.get('healing_bonus', 0.0), 'bonus', is_support_and_healer) * stat_weights_for_average['healing_bonus']
    total_stat_weights = sum(stat_weights_for_average.values())
    
    component_scores['status'] = round(overall_stat_score / total_stat_weights, 2) if total_stat_weights > 0 else 0

    weapon_score = 0
    if build_instance and build_instance.ideal_weapon:
        if selected_weapon_obj and build_instance.ideal_weapon.pk == selected_weapon_obj.pk:
            weapon_score = 100
        elif selected_weapon_obj:
            weapon_rarity = getattr(selected_weapon_obj, 'rarity', 0)
            weapon_level = int(user_input_stats.get('weapon_level', 90)) # Akan selalu 90 dari user_input_stats
            # 'weapon_rank' dihapus
            level_part = (min(weapon_level, 90) / 90) * 50 # Bobot level 50%
            rarity_part = (weapon_rarity / 5) * 50 # Bobot rarity 50%
            weapon_score = rarity_part + level_part
            weapon_score = min(100, weapon_score)
    component_scores['weapon'] = weapon_score

    echo_score = 0
    if build_instance and build_instance.ideal_echo:
        echo_matches = (selected_echo_obj and build_instance.ideal_echo.pk == selected_echo_obj.pk)
        sonata_matches = (echo_matches and selected_sonata_obj and build_instance.ideal_sonata and build_instance.ideal_sonata.pk == selected_sonata_obj.pk)
        if echo_matches and sonata_matches:
            echo_score = 100
        elif echo_matches:
            echo_score = 60
        else:
            echo_score = 0
    component_scores['echo'] = min(100, echo_score)

    # Perhitungan skill_score diaktifkan kembali
    skill_score = 100
    total_skill_levels = 0
    max_level_per_skill = 10
    total_possible_skill_levels = 5 * max_level_per_skill
    for skill_field in [
        'basic_atk_level',
        'resonance_skill_level',
        'forte_circuit_level',
        'resonance_liberation_level',
        'intro_skill_level'
    ]:
        current_level = int(user_input_stats.get(skill_field, max_level_per_skill)) # Mengambil dari user_input_stats
        total_skill_levels += current_level
    
    if total_possible_skill_levels > 0:
        skill_score = (total_skill_levels / total_possible_skill_levels) * 100
    else:
        skill_score = 100 # Fallback jika total_possible_skill_levels adalah 0
    component_scores['skill'] = max(0, min(100, skill_score))

    weighted_sum = (
        component_scores.get('level', 0) * RESONATOR_RATING_WEIGHTS['level'] +
        component_scores.get('status', 0) * RESONATOR_RATING_WEIGHTS['status'] +
        component_scores.get('weapon', 0) * RESONATOR_RATING_WEIGHTS['weapon'] +
        component_scores.get('echo', 0) * RESONATOR_RATING_WEIGHTS['echo'] +
        component_scores.get('skill', 0) * RESONATOR_RATING_WEIGHTS['skill'] # Skill diaktifkan kembali
    )
    total_weights = sum(RESONATOR_RATING_WEIGHTS.values())
    resonator_rating_final = round(weighted_sum / total_weights, 2)
    resonator_rating_text = get_overall_build_rating_text(resonator_rating_final)

    category_scores = {
        'Character': f"{resonator.rarity}/5",
        'Level': f"{round(component_scores['level'] / 10)}/10",
        'Weapon': f"{round(component_scores['weapon'] / 10)}/10",
        'Echo': f"{round(component_scores['echo'] / 10)}/10",
        'Skill': f"{round(component_scores['skill'] / 10)}/10", # Skill diaktifkan kembali
        'Stats': f"{round(component_scores['status'] / 10)}/10"
    }

    chart_labels = ['HP', 'ATK', 'DEF', 'Energy Regen', 'Crit Rate', 'Crit Dmg']
    chart_data_normalized = [
        min(100.0, (ideal_hp / HP_NORM) * 100.0),
        min(100.0, (ideal_attack / ATK_NORM) * 100.0),
        min(100.0, (ideal_defense / DEF_NORM) * 100.0),
        min(100.0, (ideal_energy / ENERGY_NORM) * 100.0),
        min(100.0, ideal_crit_rate / CRIT_RATE_NORM * 100.0),
        min(100.0, ideal_crit_dmg / CRIT_DMG_NORM * 100.0),
    ]
    performance_data_json = {
        'labels': chart_labels,
        'datasets': [{
            'label': 'Resonator Performance (Ideal Build)',
            'data': chart_data_normalized,
            'backgroundColor': 'rgba(255, 99, 132, 0.2)',
            'borderColor': 'rgba(255, 99, 132, 1)',
            'borderWidth': 1
        }]
    }

    current_date = datetime.now().strftime("%Y-%m-%d")
    user_name = request.user.username if request.user.is_authenticated else "Guest"

    context = {
        'resonator': resonator,
        'images': images,
        'user_name': user_name,
        'current_date': current_date,
        'roles_with_icons': roles_with_icons,
        'user_input_stats': user_input_stats,
        
        'selected_weapon_obj': selected_weapon_obj,
        'selected_echo_obj': selected_echo_obj,
        'selected_sonata_obj': selected_sonata_obj,
        
        'overview_stats': overview_stats,
        'status_differences': status_differences,
        'category_scores': category_scores,
        'performance_data_json': performance_data_json,
        'resonator_rating': resonator_rating_final,
        'resonator_rating_text': resonator_rating_text,
    }

    print("DEBUG: performance_data_json (before json_script filter):")
    print(json.dumps(performance_data_json, indent=2))

    return render(request, 'landingpage/review.html', context)
