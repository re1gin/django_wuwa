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
    RESONATOR_RATING_WEIGHTS, DEFAULT_SKILL_LEVEL, STAT_WEIGHTS_FOR_AVERAGE
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

    # Menggunakan 'energy' secara konsisten, bukan 'energy_regen'
    user_input_stats = request.session.get('user_input_stats', {
        'hp': 0.0, 'attack': 0.0, 'defense': 0.0, 'energy': 0.0, 'crit_rate': 0.0, 'crit_dmg': 0.0,
        'basic_atk_dmg_bonus': 0.0, 'heavy_atk_dmg_bonus': 0.0,
        'resonance_skill_dmg_bonus': 0.0, 'resonance_lib_dmg_bonus': 0.0,
        'attribute_dmg_bonus': 0.0, 'healing_bonus': 0.0,
        'character_level': DEFAULT_SKILL_LEVEL['character_level'],
        'weapon_level': DEFAULT_SKILL_LEVEL['weapon_level'],
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
    if user_input_stats['selected_sonata'] and selected_echo_obj:
        selected_sonata_obj = selected_echo_obj.sonatas.filter(
            name=user_input_stats['selected_sonata']
        ).first()

    build_instance = None
    try:
        build_instance = resonator.ideal_build
    except ObjectDoesNotExist:
        pass

    ideal_build_stats = {
        'hp': 0.0, 'attack': 0.0, 'defense': 0.0, 'energy': 0.0, 'crit_rate': 0.0, 'crit_dmg': 0.0,
        'basic_atk_dmg_bonus': 0.0, 'heavy_atk_dmg_bonus': 0.0,
        'resonance_skill_dmg_bonus': 0.0, 'resonance_lib_dmg_bonus': 0.0,
        'attribute_dmg_bonus': 0.0, 'healing_bonus': 0.0,
    }

    ideal_weapons_db = []
    ideal_echos_db = []
    ideal_sonatas_db = []

    if build_instance:
        ideal_build_stats.update({
            'hp': build_instance.hp,
            'attack': build_instance.attack,
            'defense': build_instance.defense,
            'energy': build_instance.energy,
            'crit_rate': build_instance.crit_rate,
            'crit_dmg': build_instance.crit_dmg,
            'basic_atk_dmg_bonus': 0, # build_instance.basic_atk_dmg_bonus,
            'heavy_atk_dmg_bonus': 0, # build_instance.heavy_atk_dmg_bonus,
            'resonance_skill_dmg_bonus': 0, # build_instance.resonance_skill_dmg_bonus,
            'resonance_lib_dmg_bonus': 0, # build_instance.resonance_lib_dmg_bonus,
            'attribute_dmg_bonus': build_instance.attribute_dmg_bonus,
            'healing_bonus': build_instance.healing_bonus,
        })
        # Mengambil semua objek terkait dari ManyToManyField, bukan mencoba mengaksesnya sebagai satu objek
        ideal_weapons_db = build_instance.ideal_weapon.all()
        ideal_echos_db = build_instance.ideal_echo.all()
        ideal_sonatas_db = build_instance.ideal_sonata.all()


    resonator_roles = [r.name for r in resonator.role.all()]

    prioritized_specific_dmg_bonus_stats = {
        'basic_atk_dmg_bonus': False,
        'heavy_atk_dmg_bonus': False,
        'resonance_skill_dmg_bonus': False,
        'resonance_lib_dmg_bonus': False,
    }

    ROLE_SPECIFIC_DMG_PRIORITIES_MAP = {
        'Basic Attack Damage': ['basic_atk_dmg_bonus'],
        'Heavy Attack Damage': ['heavy_atk_dmg_bonus'],
        'Resonance Skill Damage': ['resonance_skill_dmg_bonus'],
        'Resonance Liberation Damage': ['resonance_lib_dmg_bonus'],
        
    }

    for role_name in resonator_roles:
        if role_name in ROLE_SPECIFIC_DMG_PRIORITIES_MAP:
            for stat_key in ROLE_SPECIFIC_DMG_PRIORITIES_MAP[role_name]:
                if stat_key in prioritized_specific_dmg_bonus_stats:
                    prioritized_specific_dmg_bonus_stats[stat_key] = True
                    
    # Daftar stat yang akan ditampilkan dan bagaimana mereka harus diproses
    display_stats_config = [
        {'label': "HP", 'key': 'hp', 'category': 'flat', 'is_percentage_display': False, 'type': 'main'},
        {'label': "ATK", 'key': 'attack', 'category': 'flat', 'is_percentage_display': False, 'type': 'main'},
        {'label': "DEF", 'key': 'defense', 'category': 'flat', 'is_percentage_display': False, 'type': 'main'},
        {'label': "Energy Regen", 'key': 'energy', 'category': 'percent', 'is_percentage_display': True, 'type': 'main'},
        {'label': "Critical Rate", 'key': 'crit_rate', 'category': 'percent', 'is_percentage_display': True, 'type': 'main'},
        {'label': "Critical Damage", 'key': 'crit_dmg', 'category': 'percent', 'is_percentage_display': True, 'type': 'main'},
        {'label': "Basic ATK DMG Bonus", 'key': 'basic_atk_dmg_bonus', 'category': 'bonus', 'is_percentage_display': True, 'type': 'bonus'},
        {'label': "Heavy ATK DMG Bonus", 'key': 'heavy_atk_dmg_bonus', 'category': 'bonus', 'is_percentage_display': True, 'type': 'bonus'},
        {'label': "Resonance Skill DMG Bonus", 'key': 'resonance_skill_dmg_bonus', 'category': 'bonus', 'is_percentage_display': True, 'type': 'bonus'},
        {'label': "Resonance Liberation DMG Bonus", 'key': 'resonance_lib_dmg_bonus', 'category': 'bonus', 'is_percentage_display': True, 'type': 'bonus'},
        {'label': "Attribute DMG Bonus", 'key': 'attribute_dmg_bonus', 'category': 'bonus', 'is_percentage_display': True, 'type': 'bonus'},
        {'label': "Healing Bonus", 'key': 'healing_bonus', 'category': 'bonus', 'is_percentage_display': True, 'type': 'bonus'},
    ]

    if 'Main Damage Dealer' in resonator_roles and not any(r in resonator_roles for r in ['Basic Attack Focused', 'Heavy Attack Focused', 'Resonance Skill Focused', 'Resonance Liberation Focused', 'Hybrid DPS', 'Omni DPS']):
        prioritized_specific_dmg_bonus_stats['basic_atk_dmg_bonus'] = True
        prioritized_specific_dmg_bonus_stats['heavy_atk_dmg_bonus'] = True
        prioritized_specific_dmg_bonus_stats['resonance_skill_dmg_bonus'] = True
        prioritized_specific_dmg_bonus_stats['resonance_lib_dmg_bonus'] = True
        prioritized_specific_dmg_bonus_stats['attribute_dmg_bonus'] = True # Untuk Main DPS umum


    # -----------------------------------------------------------
    # 3. MENGHITUNG COMPONENT SCORES
    # -----------------------------------------------------------
    component_scores = {}
    total_weighted_score = 0
    total_actual_weights = 0

    # a. Level Score (tetap sama)
    character_level = int(user_input_stats.get('character_level', DEFAULT_SKILL_LEVEL['character_level']))
    if character_level >= DEFAULT_SKILL_LEVEL['character_level']:
        component_scores['level'] = 100
    else:
        component_scores['level'] = (character_level / DEFAULT_SKILL_LEVEL['character_level']) * 100
    total_weighted_score += component_scores['level'] * RESONATOR_RATING_WEIGHTS['level']
    total_actual_weights += RESONATOR_RATING_WEIGHTS['level']

    # b. Status Score (menggunakan Fuzzy Logic)
    overall_stat_score = 0
    total_stat_weights_for_average_calc = 0

    FUZZY_STAT_CATEGORIES = {
        'hp': 'flat',
        'attack': 'flat',
        'defense': 'flat',
        'energy': 'percent',
        'crit_rate': 'percent',
        'crit_dmg': 'percent',
        'basic_atk_dmg_bonus': 'bonus',
        'heavy_atk_dmg_bonus': 'bonus',
        'resonance_skill_dmg_bonus': 'bonus',
        'resonance_lib_dmg_bonus': 'bonus',
        'attribute_dmg_bonus': 'bonus',
        'healing_bonus': 'bonus',
    }

    # Untuk menyimpan pesan peringatan
    warning_messages = []
    status_differences = []

    for stat_info_config in display_stats_config: # Gunakan display_stats_config
        stat_name = stat_info_config['key']
        category = FUZZY_STAT_CATEGORIES.get(stat_name) # Ambil kategori dari mapping FUZZY_STAT_CATEGORIES
        label = stat_info_config['label']
        is_percentage_display = stat_info_config['is_percentage_display']


        user_val = user_input_stats.get(stat_name, 0.0)
        ideal_val = ideal_build_stats.get(stat_name, 0.0)
        is_priority_for_fuzzy = prioritized_specific_dmg_bonus_stats.get(stat_name, False)

        # Lewatkan stat_name ke calculate_fuzzy_stat_quality jika kategorinya 'bonus'
        if category == 'bonus':
            score = calculate_fuzzy_stat_quality(
                ideal_val, user_val, category, stat_name=stat_name, is_role_priority=is_priority_for_fuzzy
            )
            # Logika pesan peringatan untuk bonus DMG yang diprioritaskan tapi 0
            if is_priority_for_fuzzy and user_val == 0.0:
                warning_messages.append(f"Peringatan: {label} adalah stat **penting** bagi {resonator.name}, tetapi Anda tidak memiliki nilai sama sekali (0%). Ini sangat memengaruhi performa!")
        else:
            score = calculate_fuzzy_stat_quality(
                ideal_val, user_val, category, is_role_priority=is_priority_for_fuzzy # is_role_priority mungkin tidak relevan untuk flat/percent
            )
        
        overall_stat_score += score * STAT_WEIGHTS_FOR_AVERAGE.get(stat_name, 1.0)
        total_stat_weights_for_average_calc += STAT_WEIGHTS_FOR_AVERAGE.get(stat_name, 1.0)

        # TAMBAH: Panggil format_comparison_difference untuk menghasilkan pesan saran
        status_differences.append(format_comparison_difference(
            ideal_val, user_val, label, is_percentage=is_percentage_display, is_prioritized=is_priority_for_fuzzy
        ))

    component_scores['status'] = round(overall_stat_score / total_stat_weights_for_average_calc, 2) if total_stat_weights_for_average_calc > 0 else 0
    total_weighted_score += component_scores['status'] * RESONATOR_RATING_WEIGHTS['status']
    total_actual_weights += RESONATOR_RATING_WEIGHTS['status']

    # c. Weapon Score (tetap sama)
    weapon_score = 0
    if build_instance and ideal_weapons_db.exists():
        # Cek apakah senjata yang dipilih pengguna ada di dalam daftar senjata ideal
        if selected_weapon_obj and ideal_weapons_db.filter(weapon__pk=selected_weapon_obj.pk).exists():
            weapon_score = 100

    component_scores['weapon'] = weapon_score
    total_weighted_score += component_scores['weapon'] * RESONATOR_RATING_WEIGHTS['weapon']
    total_actual_weights += RESONATOR_RATING_WEIGHTS['weapon']

    # d. Echo Score (tetap sama)
    echo_score = 0
    if build_instance and ideal_echos_db.exists() and ideal_sonatas_db.exists():
        # Cek apakah echo dan sonata yang dipilih ada di daftar ideal
        echo_matches = selected_echo_obj and ideal_echos_db.filter(echo__pk=selected_echo_obj.pk).exists()
        sonata_matches = echo_matches and selected_sonata_obj and ideal_sonatas_db.filter(sonata__pk=selected_sonata_obj.pk).exists()

        if echo_matches and sonata_matches:
            echo_score = 100
        elif echo_matches:
            echo_score = 60
        else:
            echo_score = 0
    component_scores['echo'] = min(100, echo_score)
    total_weighted_score += component_scores['echo'] * RESONATOR_RATING_WEIGHTS['echo']
    total_actual_weights += RESONATOR_RATING_WEIGHTS['echo']

    # e. Skill Score (tetap sama)
    # Logika skill score bisa disederhanakan atau dihilangkan jika tidak ada input level skill
    component_scores['skill'] = 100 # Asumsi skill max untuk sementara
    total_weighted_score += component_scores['skill'] * RESONATOR_RATING_WEIGHTS['skill']
    total_actual_weights += RESONATOR_RATING_WEIGHTS['skill']


    # -----------------------------------------------------------
    # 4. FINAL RATING
    # -----------------------------------------------------------
    resonator_rating_final = round(total_weighted_score / total_actual_weights, 2) if total_actual_weights > 0 else 0
    resonator_rating_text = get_overall_build_rating_text(resonator_rating_final)

    # -----------------------------------------------------------
    # 5. DATA UNTUK TAMPILAN
    # -----------------------------------------------------------
    category_scores = {
        'Character': f"{resonator.rarity}/5",
        'Level': f"{round(component_scores['level'] / 10, 1)}/10",
        'Weapon': f"{round(component_scores['weapon'] / 10, 1)}/10",
        'Echo': f"{round(component_scores['echo'] / 10, 1)}/10",
        'Skill': f"{round(component_scores['skill'] / 10, 1)}/10",
        'Stats': f"{round(component_scores['status'] / 10, 1)}/10",
    }

    # Pisahkan overview_stats menjadi dua bagian
    overview_main_stats = []
    overview_bonus_stats = []

    for stat_info in display_stats_config:
        label = stat_info['label']
        key = stat_info['key']
        category = stat_info['category']
        is_percentage_display = stat_info['is_percentage_display']
        stat_type = stat_info['type'] # 'main' or 'bonus'

        user_val = user_input_stats.get(key, 0.0)
        ideal_val = ideal_build_stats.get(key, 0.0)
        is_priority_for_fuzzy_calc = prioritized_specific_dmg_bonus_stats.get(key, False)

        # Hitung skor fuzzy untuk penentuan warna
        # Perhatikan: stat_name harus dilewatkan untuk kategori 'bonus'
        score_for_color = calculate_fuzzy_stat_quality(
            ideal_val, user_val, category, stat_name=key if category == 'bonus' else None, is_role_priority=is_priority_for_fuzzy_calc
        )
        color = get_interpolated_color(score_for_color)

        stat_entry = {
            'label': label,
            'user_value': user_val,
            'ideal_value': ideal_val,
            'is_percentage': is_percentage_display,
            'color': color,
            'is_prioritized': is_priority_for_fuzzy_calc # Tambahkan info ini untuk tampilan
        }

        if stat_type == 'main':
            overview_main_stats.append(stat_entry)
        else: # type == 'bonus'
            overview_bonus_stats.append(stat_entry)


    chart_labels = ['HP', 'ATK', 'DEF', 'Energy Regen', 'Crit Rate', 'Crit Dmg']
    chart_data_normalized = [
        min(100.0, (ideal_build_stats['hp'] / HP_NORM) * 100.0),
        min(100.0, (ideal_build_stats['attack'] / ATK_NORM) * 100.0),
        min(100.0, (ideal_build_stats['defense'] / DEF_NORM) * 100.0),
        min(100.0, (ideal_build_stats['energy'] / ENERGY_NORM) * 100.0),
        min(100.0, ideal_build_stats['crit_rate'] / CRIT_RATE_NORM * 100.0),
        min(100.0, ideal_build_stats['crit_dmg'] / CRIT_DMG_NORM * 100.0),
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

        'ideal_weapons_db': ideal_weapons_db,
        'ideal_echos_db': ideal_echos_db,
        'ideal_sonatas_db': ideal_sonatas_db,

        'overview_main_stats': overview_main_stats,   # Dipisahkan
        'overview_bonus_stats': overview_bonus_stats, # Dipisahkan
        'status_differences': status_differences,
        'category_scores': category_scores,
        'performance_data_json': performance_data_json,
        'resonator_rating': resonator_rating_final,
        'resonator_rating_text': resonator_rating_text,
        'warning_messages': warning_messages, # Pesan peringatan
    }

    print("DEBUG: performance_data_json (before json_script filter):")
    print(json.dumps(performance_data_json, indent=2))

    return render(request, 'landingpage/review.html', context)