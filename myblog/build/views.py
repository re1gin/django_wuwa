import json # Pastikan ini diimpor di bagian atas file
from datetime import datetime
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

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
            
        is_active_icon = False
        if current_char_obj and resonator.name == current_char_obj.name:
            is_active_icon = True
        
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
    
    if request.method == 'GET':
        if 'user_input_stats' in request.session:
            del request.session['user_input_stats']
        if 'character_name_for_comparison' in request.session:
            del request.session['character_name_for_comparison']
            
    folder_name = format_folder(char_obj.name)
    image_path = f"{settings.MEDIA_URL}resonator/{folder_name}/"
    images = {"render": f"{image_path}Render.png"}

    all_characters_for_icons = get_icon_chars_data(char_obj)

    weapons_data_db = Weapon.objects.filter(weapon_type=char_obj.weapon_type).order_by('weapon_name')
    echos_data_db = Echo.objects.all().order_by('name')
    sonatas_data_db = Sonata.objects.all().order_by('name')

    user_input_stats = {
        'hp': 0.0, 'attack': 0.0, 'defense': 0.0, 'energy': 0.0, 'crit_rate': 0.0, 'crit_dmg': 0.0,
        'basic_atk_dmg': 0.0, 'heavy_atk_dmg': 0.0, 'resonance_skill_dmg': 0.0, 'resonance_lib_dmg': 0.0,
        'healing_bonus': 0.0, 
        'attribute_dmg_bonus': 0.0,
        'selected_weapon': '',
        'selected_echo': '',
        'selected_sonata': '',
    }

    if 'user_input_stats' in request.session and request.session.get('character_name_for_comparison') == char_obj.name:
        user_input_stats.update(request.session['user_input_stats'])
    
    if request.method == 'POST':
        try:
            for stat_name in ['hp', 'attack', 'defense', 'energy', 'crit_rate', 'crit_dmg',
                             'basic_atk_dmg', 'heavy_atk_dmg', 'resonance_skill_dmg', 'resonance_lib_dmg',
                             'healing_bonus', 
                             'attribute_dmg_bonus']:
                user_input_stats[stat_name] = float(request.POST.get(stat_name, 0.0) or 0.0)
        except ValueError:
            messages.error(request, "Input stat harus berupa angka.")
            
        user_input_stats['selected_weapon'] = request.POST.get('selected_weapon', '')
        user_input_stats['selected_echo'] = request.POST.get('selected_echo', '')
        user_input_stats['selected_sonata'] = request.POST.get('selected_sonata', '')

        selected_echo_name = user_input_stats['selected_echo']
        selected_sonata_name = user_input_stats['selected_sonata']

        if selected_echo_name:
            selected_echo_obj_from_post = Echo.objects.filter(name=selected_echo_name).first()
            if selected_echo_obj_from_post:
                if selected_sonata_name:
                    if not selected_echo_obj_from_post.sonatas.filter(name=selected_sonata_name).exists():
                        messages.error(request, f"Sonata '{selected_sonata_name}' tidak valid untuk Echo '{selected_echo_name}'. Pilihan direset.")
                        user_input_stats['selected_sonata'] = ''
            else:
                messages.error(request, f"Echo '{selected_echo_name}' tidak ditemukan. Pilihan Echo dan Sonata direset.")
                user_input_stats['selected_echo'] = ''
                user_input_stats['selected_sonata'] = ''
        elif selected_sonata_name:
            messages.error(request, "Sonata tidak dapat dipilih tanpa Echo yang dipilih. Sonata direset.")
            user_input_stats['selected_sonata'] = ''

        request.session['user_input_stats'] = user_input_stats
        request.session['character_name_for_comparison'] = char_obj.name

        if 'NILAI BUILD' in request.POST:
            return redirect('build:review_build_page', name=char_obj.name)
            
    selected_weapon_obj = None
    selected_echo_obj = None
    selected_sonata_obj = None

    if user_input_stats['selected_weapon']:
        selected_weapon_obj = Weapon.objects.filter(weapon_name=user_input_stats['selected_weapon']).first()
    if user_input_stats['selected_echo']:
        selected_echo_obj = Echo.objects.filter(name=user_input_stats['selected_echo']).first()
    if user_input_stats['selected_sonata'] and selected_echo_obj:
        selected_sonata_obj = Sonata.objects.filter(name=user_input_stats['selected_sonata']).first()
        if not selected_sonata_obj or not selected_echo_obj.sonatas.filter(name=selected_sonata_obj.name).exists():
            selected_sonata_obj = None

    if selected_echo_obj:
        sonatas_data_db = selected_echo_obj.sonatas.all().order_by('name')
    else:
        sonatas_data_db = Sonata.objects.all().order_by('name')

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

def build_review_page(request, name):

    resonator = get_object_or_404(Resonator, name__iexact=name)
    folder_name = format_folder(resonator.name)
    image_path = f"{settings.MEDIA_URL}resonator/{folder_name}/"
    images = {"render": f"{image_path}Render.png"}
    roles_with_icons = resonator.role.all().values('name', 'icon_role')

    # --- Step 1: Get user input and selected equipment ---
    user_input_stats = request.session.get('user_input_stats', {
        'hp': 0.0, 'attack': 0.0, 'defense': 0.0, 'energy': 0.0,
        'crit_rate': 0.0, 'crit_dmg': 0.0,
        'basic_atk_dmg': 0.0, 'heavy_atk_dmg': 0.0,
        'resonance_skill_dmg': 0.0, 'resonance_lib_dmg': 0.0,
        'healing_bonus': 0.0,
        'attribute_dmg_bonus': 0.0,
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
    if (user_input_stats['selected_sonata'] and
            selected_echo_obj and
            selected_echo_obj.name != 'No Echo Selected'):
        selected_sonata_obj = selected_echo_obj.sonatas.filter(
            name=user_input_stats['selected_sonata']
        ).first()

    # --- Step 2: Retrieve ideal build data from the database or set defaults ---
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
    # Tambahkan ideal_val untuk bonus stat di sini jika ada dalam model IdealBuild Anda
    # Atau tetapkan nilai default yang masuk akal sebagai "target ideal" untuk pewarnaan
    ideal_basic_atk_dmg = getattr(build_instance, 'basic_atk_dmg_ideal', 20.0) # Contoh: ideal 20%
    ideal_heavy_atk_dmg = getattr(build_instance, 'heavy_atk_dmg_ideal', 20.0)
    ideal_resonance_skill_dmg = getattr(build_instance, 'resonance_skill_dmg_ideal', 20.0)
    ideal_resonance_lib_dmg = getattr(build_instance, 'resonance_lib_dmg_ideal', 20.0)
    ideal_attribute_dmg_bonus = getattr(build_instance, 'attribute_dmg_bonus_ideal', 20.0)
    ideal_healing_bonus = getattr(build_instance, 'healing_bonus_ideal', 30.0) # Contoh: ideal 30%


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
        # Create dummy objects for display if no ideal build is saved
        selected_weapon_obj_db = type('Weapon', (object,), {
            'weapon_name': 'No Saved Weapon',
            'icon_image': type('ImageFile', (object,), {'url': '/static/combat/images/placeholder_weapon.png'}),
            'atk_value': 0.0,
            'secondary_stat_name': '',
            'secondary_stat_value': 0.0,
            'rarity': 0,
        })()
        selected_echo_obj_db = type('Echo', (object,), {
            'name': 'No Saved Echo',
            'icon_echo': type('ImageFile', (object,), {'url': '/static/combat/images/placeholder_echo.png'}),
            'cost': 0, 'main_stat': 'N/A', 'main_stat_value': 0.0
        })()
        selected_sonata_obj_db = type('Sonata', (object,), {
            'name': 'No Saved Sonata',
            'icon_sonata': type('ImageFile', (object,), {'url': '/static/combat/images/placeholder_sonata.png'}),
            'effect': 'N/A'
        })()

    # --- Step 3: Prepare data for overview stats with dynamic coloring ---
    resonator_roles = [r.name for r in resonator.role.all()]
    is_main_dps = 'Main Damage Dealer' in resonator_roles
    is_support_and_healer = 'Support and Healer' in resonator_roles

    overview_stats = []
    # Daftar konfigurasi stat untuk ditampilkan di overview
    stats_config = [
        {'label': "HP", 'user_val': user_input_stats.get('hp', 0.0), 'ideal_val': ideal_hp, 'category': 'flat', 'is_percentage': False},
        {'label': "ATK", 'user_val': user_input_stats.get('attack', 0.0), 'ideal_val': ideal_attack, 'category': 'flat', 'is_percentage': False},
        {'label': "DEF", 'user_val': user_input_stats.get('defense', 0.0), 'ideal_val': ideal_defense, 'category': 'flat', 'is_percentage': False},
        {'label': "Energy Regen", 'user_val': user_input_stats.get('energy', 0.0), 'ideal_val': ideal_energy, 'category': 'percent', 'is_percentage': True},
        {'label': "Critical Rate", 'user_val': user_input_stats.get('crit_rate', 0.0), 'ideal_val': ideal_crit_rate, 'category': 'percent', 'is_percentage': True},
        {'label': "Critical Damage", 'user_val': user_input_stats.get('crit_dmg', 0.0), 'ideal_val': ideal_crit_dmg, 'category': 'percent', 'is_percentage': True},
        # Untuk stat bonus, gunakan ideal_val yang ditetapkan di atas (atau dari DB jika ada)
        
    ]

    for stat in stats_config:
        user_val_float = float(stat['user_val'])
        current_ideal_val = float(stat['ideal_val']) # Pastikan ideal_val juga float

        # Hitung persentase user_val terhadap ideal_val untuk pewarnaan
        user_val_vs_ideal_percent = 0
        if current_ideal_val > 0:
            user_val_vs_ideal_percent = (user_val_float / current_ideal_val) * 100
        elif current_ideal_val == 0 and user_val_float > 0: # Ideal 0 tapi user ada nilai (misal bonus stat yang selalu "lebih baik lebih tinggi")
            user_val_vs_ideal_percent = 200 # Asumsi sangat tinggi jika ideal 0 tapi user ada nilai
        elif current_ideal_val == 0 and user_val_float == 0: # Ideal 0 dan user 0
            user_val_vs_ideal_percent = 0 # Asumsi paling rendah

        # Dapatkan warna interpolasi
        interpolated_color_hex = get_interpolated_color(user_val_vs_ideal_percent)
        
        overview_stats.append({
            'label': stat['label'],
            'user_value': user_val_float,
            'ideal_value': current_ideal_val,
            'is_percentage': stat['is_percentage'],
            'color': interpolated_color_hex # Mengirim warna HEX langsung ke template
        })

    # --- Step 4: Calculate differences for general display (if still needed) ---
    # Jika Anda masih ingin daftar status_differences yang terpisah untuk tujuan lain,
    # seperti tabel ringkasan selisih, gunakan format_comparison_difference di sini.
    # Namun, karena overview_stats sudah lebih komprehensif, status_differences mungkin redundan
    # untuk bagian yang sama dengan overview_stats.
    # Saya akan mempertahankan panggilan yang sudah ada, tapi pertimbangkan apakah Anda masih memerlukannya.
    status_differences = []
    status_differences.append(format_comparison_difference(ideal_hp, user_input_stats.get('hp', 0.0), "HP"))
    status_differences.append(format_comparison_difference(ideal_attack, user_input_stats.get('attack', 0.0), "ATK"))
    status_differences.append(format_comparison_difference(ideal_defense, user_input_stats.get('defense', 0.0), "DEF"))
    status_differences.append(format_comparison_difference(ideal_energy, user_input_stats.get('energy', 0.0), "Energy Regen", is_percentage=True))
    status_differences.append(format_comparison_difference(ideal_crit_rate, user_input_stats.get('crit_rate', 0.0), "Crit Rate", is_percentage=True))
    status_differences.append(format_comparison_difference(ideal_crit_dmg, user_input_stats.get('crit_dmg', 0.0), "Crit Dmg", is_percentage=True))
    # Untuk stat bonus di sini, format_comparison_difference akan menggunakan ideal 0.0 seperti sebelumnya
    status_differences.append(format_comparison_difference(0.0, user_input_stats.get('basic_atk_dmg', 0.0), "Basic ATK DMG", is_percentage=True))
    status_differences.append(format_comparison_difference(0.0, user_input_stats.get('heavy_atk_dmg', 0.0), "Heavy ATK DMG", is_percentage=True))
    status_differences.append(format_comparison_difference(0.0, user_input_stats.get('resonance_skill_dmg', 0.0), "Skill DMG", is_percentage=True))
    status_differences.append(format_comparison_difference(0.0, user_input_stats.get('resonance_lib_dmg', 0.0), "Lib. DMG", is_percentage=True))
    status_differences.append(format_comparison_difference(0.0, user_input_stats.get('attribute_dmg_bonus', 0.0), "Attribute DMG", is_percentage=True))
    status_differences.append(format_comparison_difference(0.0, user_input_stats.get('healing_bonus', 0.0), "Healing Bonus", is_percentage=True))


    # --- Step 5: Calculate Component Scores (menggunakan Fuzzy Logic) ---
    component_scores = {}

    # Level Score (tidak berubah)
    level_score = 100
    resonator_level_db = getattr(resonator, 'level', 90)
    resonator_chain_db = getattr(resonator, 'resonance_chain', 0)

    if resonator_level_db < 90:
        level_score -= (90 - resonator_level_db) * 0.5
    if resonator_chain_db > 0:
        level_score += min(10, resonator_chain_db * 2)
    component_scores['level'] = max(0, min(100, level_score))

    # Overall Stat Score (menggunakan Fuzzy Logic, tidak berubah dari sebelumnya)
    overall_stat_score = 0
    stat_weights_for_average = {
        'hp': 1.0, 'attack': 1.0, 'defense': 1.0, 'energy': 1.0,
        'crit_rate': 1.0, 'crit_dmg': 1.0,
        'basic_atk_dmg': 1.0, 'heavy_atk_dmg': 1.0, 'resonance_skill_dmg': 1.0,
        'resonance_lib_dmg': 1.0, 'attribute_dmg_bonus': 1.0, 'healing_bonus': 1.0,
    }

    # Perhitungan fuzzy stat quality (memastikan ideal_val yang sesuai digunakan)
    overall_stat_score += calculate_fuzzy_stat_quality(ideal_hp, user_input_stats.get('hp', 0.0), 'flat') * stat_weights_for_average['hp']
    overall_stat_score += calculate_fuzzy_stat_quality(ideal_attack, user_input_stats.get('attack', 0.0), 'flat') * stat_weights_for_average['attack']
    overall_stat_score += calculate_fuzzy_stat_quality(ideal_defense, user_input_stats.get('defense', 0.0), 'flat') * stat_weights_for_average['defense']
    overall_stat_score += calculate_fuzzy_stat_quality(ideal_energy, user_input_stats.get('energy', 0.0), 'percent') * stat_weights_for_average['energy']
    overall_stat_score += calculate_fuzzy_stat_quality(ideal_crit_rate, user_input_stats.get('crit_rate', 0.0), 'percent') * stat_weights_for_average['crit_rate']
    overall_stat_score += calculate_fuzzy_stat_quality(ideal_crit_dmg, user_input_stats.get('crit_dmg', 0.0), 'percent') * stat_weights_for_average['crit_dmg']

    # Untuk stat bonus, calculate_fuzzy_stat_quality menggunakan 0 sebagai ideal_val
    # karena ia menilai nilai absolut user_val jika is_role_priority True.
    overall_stat_score += calculate_fuzzy_stat_quality(0, user_input_stats.get('basic_atk_dmg', 0.0), 'bonus', is_main_dps) * stat_weights_for_average['basic_atk_dmg']
    overall_stat_score += calculate_fuzzy_stat_quality(0, user_input_stats.get('heavy_atk_dmg', 0.0), 'bonus', is_main_dps) * stat_weights_for_average['heavy_atk_dmg']
    overall_stat_score += calculate_fuzzy_stat_quality(0, user_input_stats.get('resonance_skill_dmg', 0.0), 'bonus', is_main_dps) * stat_weights_for_average['resonance_skill_dmg']
    overall_stat_score += calculate_fuzzy_stat_quality(0, user_input_stats.get('resonance_lib_dmg', 0.0), 'bonus', is_main_dps) * stat_weights_for_average['resonance_lib_dmg']
    overall_stat_score += calculate_fuzzy_stat_quality(0, user_input_stats.get('attribute_dmg_bonus', 0.0), 'bonus', is_main_dps) * stat_weights_for_average['attribute_dmg_bonus']
    overall_stat_score += calculate_fuzzy_stat_quality(0, user_input_stats.get('healing_bonus', 0.0), 'bonus', is_support_and_healer) * stat_weights_for_average['healing_bonus']

    total_stat_weights = sum(stat_weights_for_average.values())
    component_scores['status'] = round(overall_stat_score / total_stat_weights, 2) if total_stat_weights > 0 else 0

    # Weapon Score (tidak berubah)
    weapon_score = 0
    if build_instance and build_instance.ideal_weapon:
        if selected_weapon_obj and build_instance.ideal_weapon.pk == selected_weapon_obj.pk:
            weapon_score = 100
        elif selected_weapon_obj:
            weapon_rarity = getattr(selected_weapon_obj, 'rarity', 0)
            weapon_score = (weapon_rarity / 5) * 80
            weapon_score = min(100, weapon_score)
    component_scores['weapon'] = weapon_score

    # Echo Score (tidak berubah)
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

    # Skill Score (tidak berubah)
    skill_score = 100
    total_skill_levels = 0
    
    max_level_per_skill = 10 # Common max skill level
    if build_instance and hasattr(build_instance, 'max_skill_level'): # Jika Anda memiliki ini di ideal build
        max_level_per_skill = build_instance.max_skill_level
    
    total_possible_skill_levels = len(SKILL_LEVEL_FIELDS) * max_level_per_skill

    for skill_field in SKILL_LEVEL_FIELDS.keys():
        current_level = getattr(resonator, skill_field, 0)
        total_skill_levels += current_level

    if total_possible_skill_levels > 0:
        skill_score = (total_skill_levels / total_possible_skill_levels) * 100
    else:
        skill_score = 100 # If no skills or max levels defined, assume perfect score

    component_scores['skill'] = max(0, min(100, skill_score))

    # --- Step 6: Calculate Overall Rating ---
    weighted_sum = (
        component_scores.get('level', 0) * RESONATOR_RATING_WEIGHTS['level'] +
        component_scores.get('status', 0) * RESONATOR_RATING_WEIGHTS['status'] +
        component_scores.get('weapon', 0) * RESONATOR_RATING_WEIGHTS['weapon'] +
        component_scores.get('echo', 0) * RESONATOR_RATING_WEIGHTS['echo'] +
        component_scores.get('skill', 0) * RESONATOR_RATING_WEIGHTS['skill']
    )
    total_weights = sum(RESONATOR_RATING_WEIGHTS.values())
    resonator_rating_final = round(weighted_sum / total_weights, 2)

    resonator_rating_text = get_overall_build_rating_text(resonator_rating_final)

    # --- Step 7: Prepare Context for Template ---
    category_scores = {
        'Character': f"{resonator.rarity}/5",
        'Level': f"{round(component_scores['level'] / 10)}/10",
        'Weapon': f"{round(component_scores['weapon'] / 10)}/10",
        'Echo': f"{round(component_scores['echo'] / 10)}/10",
        'Skill': f"{round(component_scores['skill'] / 10)}/10",
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
        'user_input_stats': user_input_stats, # Ini user_input_stats mentah (untuk referensi jika diperlukan)
        'overview_stats': overview_stats, # Ini daftar stat yang sudah diproses dengan warna
        'selected_weapon_obj': selected_weapon_obj,
        'selected_echo_obj': selected_echo_obj,
        'selected_sonata_obj': selected_sonata_obj,
        'ideal_stats': { # Ini ideal_stats mentah (untuk referensi jika diperlukan)
            'hp': ideal_hp, 'attack': ideal_attack, 'defense': ideal_defense,
            'energy': ideal_energy, 'crit_rate': ideal_crit_rate, 'crit_dmg': ideal_crit_dmg,
            # Tambahkan ideal_val untuk bonus stat di sini jika ada
            'basic_atk_dmg': ideal_basic_atk_dmg, 'heavy_atk_dmg': ideal_heavy_atk_dmg,
            'resonance_skill_dmg': ideal_resonance_skill_dmg, 'resonance_lib_dmg': ideal_resonance_lib_dmg,
            'attribute_dmg_bonus': ideal_attribute_dmg_bonus, 'healing_bonus': ideal_healing_bonus,
        },
        'status_differences': status_differences, # Ini dari format_comparison_difference (jika masih digunakan)
        'category_scores': category_scores,
        'performance_data_json': performance_data_json,
        'resonator_rating': resonator_rating_final,
        'resonator_rating_text': resonator_rating_text,
    }

    print("DEBUG: performance_data_json (before json_script filter):")
    print(json.dumps(performance_data_json, indent=2))

    return render(request, 'landingpage/review.html', context)