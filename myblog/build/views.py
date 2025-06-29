from datetime import date
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from resonators.models import Resonator
from weapon.models import Weapon
from echo.models import Sonata, Echo


def format_folder(name):
    return name.replace(' ', '_')

def get_icon_chars_data(current_char_obj=None):
    icon_chars_data = []
    all_resonators = Resonator.objects.all().order_by('name')
    for resonator in all_resonators:
        # --- PERUBAHAN DI SINI: Membangun URL ikon secara manual ---
        folder_name = format_folder(resonator.name)
        icon_url = f"{settings.MEDIA_URL}resonator/{folder_name}/Icon.png"
        # -------------------------------------------------------------
        
        try:
            # Mengarahkan ikon ke halaman builder untuk karakter tersebut
            icon_detail_url = reverse('build:character_builder', kwargs={'name': resonator.name})
        except Exception: # Fallback jika URL tidak ditemukan
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
            # Menggunakan ImageField URL jika ada
            image_url = weapon_obj.icon_image.url if weapon_obj.icon_image else ""
    elif item_type == 'echo':
        echo_obj = Echo.objects.filter(name=item_name).first()
        if echo_obj:
            details = {
                'name': echo_obj.name,
                'cost': echo_obj.cost,
            }
            # Menggunakan ImageField URL jika ada
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
            # Menggunakan ImageField URL jika ada
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
            
    # Images for the builder page (Constructed manually as requested)
    folder_name = format_folder(char_obj.name)
    image_path = f"{settings.MEDIA_URL}resonator/{folder_name}/"
    images = {"render": f"{image_path}Render.png"}

    # Menggunakan fungsi get_icon_chars_data
    all_characters_for_icons = get_icon_chars_data(char_obj)

    weapons_data_db = Weapon.objects.filter(weapon_type=char_obj.weapon_type).order_by('weapon_name')
    echos_data_db = Echo.objects.all().order_by('name')
    sonatas_data_db = Sonata.objects.all().order_by('name')

    user_input_stats = {
        'hp': 0.0, 'attack': 0.0, 'defense': 0.0, 'energy': 0.0, 'crit_rate': 0.0, 'crit_dmg': 0.0,
        'basic_atk_dmg': 0.0, 'heavy_atk_dmg': 0.0, 'resonance_skill_dmg': 0.0, 'resonance_lib_dmg': 0.0, # Pastikan heavy_atk_dmg ada
        'healing_bonus': 0.0, 
        'attribue_dmg_bonus': 0.0,
        'selected_weapon': '',
        'selected_echo': '',
        'selected_sonata': '',
    }

    if 'user_input_stats' in request.session and request.session.get('character_name_for_comparison') == char_obj.name:
        user_input_stats.update(request.session['user_input_stats'])
    
    selected_weapon_obj = None
    selected_echo_obj = None
    selected_sonata_obj = None

    if request.method == 'POST':
        try:
            for stat_name in ['hp', 'attack', 'defense', 'energy', 'crit_rate', 'crit_dmg',
                               'basic_atk_dmg', 'heavy_atk_dmg', 'resonance_skill_dmg', 'resonance_lib_dmg', # Pastikan heavy_atk_dmg ada di loop
                               'healing_bonus', 
                               'aero_dmg_bonus', 'fusion_dmg_bonus', 'electro_dmg_bonus',
                               'glacio_dmg_bonus', 'havoc_dmg_bonus', 'spectro_dmg_bonus',
                               'attribute_res']:
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
        
        if user_input_stats['selected_weapon']:
            selected_weapon_obj = Weapon.objects.filter(weapon_name=user_input_stats['selected_weapon']).first()
        if user_input_stats['selected_echo']:
            selected_echo_obj = Echo.objects.filter(name=user_input_stats['selected_echo']).first()
        if user_input_stats['selected_sonata'] and selected_echo_obj:
            selected_sonata_obj = Sonata.objects.filter(name=user_input_stats['selected_sonata']).first()
            if not selected_sonata_obj or not selected_echo_obj.sonatas.filter(name=selected_sonata_obj.name).exists():
                 selected_sonata_obj = None

    else:
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

def _get_build_review_data(request, resonator_obj):
   
    user_input_stats = request.session.get('user_input_stats', {
        'hp': 0.0, 'attack': 0.0, 'defense': 0.0, 'energy': 0.0, 'crit_rate': 0.0, 'crit_dmg': 0.0,
        'basic_atk_dmg': 0.0, 'heavy_atk_dmg': 0.0, 'resonance_skill_dmg': 0.0, 'resonance_lib_dmg': 0.0,
        'healing_bonus': 0.0, 
        'attribute_dmg_bonus': 0.0, 
        'selected_weapon': '',
        'selected_echo': '',
        'selected_sonata': '',
    })

    selected_weapon_obj_session = None
    if user_input_stats['selected_weapon']:
        selected_weapon_obj_session = Weapon.objects.filter(weapon_name=user_input_stats['selected_weapon']).first()
    if not selected_weapon_obj_session:
        selected_weapon_obj_session = type('Weapon', (object,), {
            'weapon_name': user_input_stats.get('selected_weapon', 'No Weapon Selected'),
            'icon_image': type('ImageFile', (object,), {'url': '/static/combat/images/placeholder_weapon.png'}),
            'atk_value': 0.0, 'energy_regen_value': 0.0, 'crit_dmg_value': 0.0
        })()

    selected_echo_obj_session = None
    if user_input_stats['selected_echo']:
        selected_echo_obj_session = Echo.objects.filter(name=user_input_stats['selected_echo']).first()
    if not selected_echo_obj_session:
        selected_echo_obj_session = type('Echo', (object,), {
            'name': user_input_stats.get('selected_echo', 'No Echo Selected'),
            'icon_echo': type('ImageFile', (object,), {'url': '/static/combat/images/placeholder_echo.png'}),
            'cost': 0, 'main_stat': 'N/A'
        })()
    
    selected_sonata_obj_session = None
    if user_input_stats['selected_sonata'] and selected_echo_obj_session and selected_echo_obj_session.name != 'No Echo Selected':
        selected_sonata_obj_session = selected_echo_obj_session.sonatas.filter(name=user_input_stats['selected_sonata']).first()
    if not selected_sonata_obj_session:
        selected_sonata_obj_session = type('Sonata', (object,), {
            'name': user_input_stats.get('selected_sonata', 'No Sonata Selected'),
            'icon_sonata': type('ImageFile', (object,), {'url': '/static/combat/images/placeholder_sonata.png'}),
            'effect': 'N/A'
        })()

    return {
        'user_input_stats': user_input_stats,
        'selected_weapon_obj': selected_weapon_obj_session, # Ini adalah gear dari sesi/form
        'selected_echo_obj': selected_echo_obj_session,
        'selected_sonata_obj': selected_sonata_obj_session,
    }

def _get_difference_stat_data(request, resonator_obj, build_review_data):
    
    user_input_stats_from_session = build_review_data['user_input_stats']

    build_instance = None
    try:
        build_instance = resonator_obj.ideal_build # Mengakses melalui related_name 'ideal_build'
    except ObjectDoesNotExist:
        pass

    # Inisialisasi final_stats dan objek gear dari BUILD DATABASE
    final_hp = 0.0
    final_attack = 0.0
    final_defense = 0.0
    final_energy = 0.0
    final_crit_rate = 0.0
    final_crit_dmg = 0.0
    final_attribute_dmg_bonus = 0.0 
    final_healing_bonus = 0.0

    selected_weapon_obj_db = None
    selected_echo_obj_db = None
    selected_sonata_obj_db = None

    if build_instance:
        final_hp = build_instance.hp
        final_attack = build_instance.attack
        final_defense = build_instance.defense
        final_energy = build_instance.energy
        final_crit_rate = build_instance.crit_rate
        final_crit_dmg = build_instance.crit_dmg

        selected_weapon_obj_db = build_instance.ideal_weapon 
        selected_echo_obj_db = build_instance.ideal_echo     
        selected_sonata_obj_db = build_instance.ideal_sonata 
    else:
        selected_weapon_obj_db = type('Weapon', (object,), {
            'weapon_name': 'No Saved Weapon',
            'icon_image': type('ImageFile', (object,), {'url': '/static/combat/images/placeholder_weapon.png'}),
            'atk_value': 0.0, 'energy_regen_value': 0.0, 'crit_dmg_value': 0.0
        })()
        selected_echo_obj_db = type('Echo', (object,), {
            'name': 'No Saved Echo',
            'icon_echo': type('ImageFile', (object,), {'url': '/static/combat/images/placeholder_echo.png'}),
            'cost': 0, 'main_stat': 'N/A'
        })()
        selected_sonata_obj_db = type('Sonata', (object,), {
            'name': 'No Saved Sonata',
            'icon_sonata': type('ImageFile', (object,), {'url': '/static/combat/images/placeholder_sonata.png'}),
            'effect': 'N/A'
        })()


    # Mengevaluasi Build: Radar Chart & Skor Performa
    HP_NORM = 50000.0   
    ATK_NORM = 4000.0   
    DEF_NORM = 4000.0   
    ENERGY_NORM = 300.0 
    CRIT_RATE_NORM = 100.0
    CRIT_DMG_NORM = 350.0

    chart_labels = ['HP', 'ATK', 'DEF', 'Energy Regen', 'Crit Rate', 'Crit Dmg']
    chart_data_normalized = [
        min(100.0, (final_hp / HP_NORM) * 100.0),        
        min(100.0, (final_attack / ATK_NORM) * 100.0),    
        min(100.0, (final_defense / DEF_NORM) * 100.0),    
        min(100.0, (final_energy / ENERGY_NORM) * 100.0),  
        min(100.0, final_crit_rate),                       
        min(100.0, final_crit_dmg),                         
    ]
    
    resonator_rating = round(sum(chart_data_normalized) / len(chart_data_normalized) if chart_data_normalized else 0.0, 2)
    
    status_differences = []

    def format_comparison_difference(db_val, session_val, label, is_percentage=False):
        diff = db_val - session_val
        symbol = ''
        if diff > 0:
            symbol = '&#9650;' # Panah atas
            diff_str = f"+{diff:.1f}" if not is_percentage else f"+{diff:.1f}%"
        elif diff < 0:
            symbol = '&#9660;' # Panah bawah
            diff_str = f"{diff:.1f}" if not is_percentage else f"{diff:.1f}%"
        else:
            symbol = '&#x2713;' # Tanda centang
            diff_str = "Equal"

        label_parts = label.split(' ')
        label_unit = label_parts[0] if label_parts else ''

        return {'label': label, 'value': diff_str, 'symbol': symbol, 'label_unit': label_unit}

    status_differences.append(format_comparison_difference(final_hp, user_input_stats_from_session['hp'], "HP"))
    status_differences.append(format_comparison_difference(final_attack, user_input_stats_from_session['attack'], "ATK"))
    status_differences.append(format_comparison_difference(final_defense, user_input_stats_from_session['defense'], "DEF"))
    status_differences.append(format_comparison_difference(final_energy, user_input_stats_from_session['energy'], "Energy Regen", is_percentage=True))
    status_differences.append(format_comparison_difference(final_crit_rate, user_input_stats_from_session['crit_rate'], "Crit Rate", is_percentage=True))
    status_differences.append(format_comparison_difference(final_crit_dmg, user_input_stats_from_session['crit_dmg'], "Crit Dmg", is_percentage=True))
    
    status_differences.append(format_comparison_difference(0.0, user_input_stats_from_session.get('basic_atk_dmg', 0.0), "Basic ATK DMG", is_percentage=True)) 
    status_differences.append(format_comparison_difference(0.0, user_input_stats_from_session.get('heavy_atk_dmg', 0.0), "Heavy ATK DMG", is_percentage=True))
    status_differences.append(format_comparison_difference(0.0, user_input_stats_from_session.get('resonance_skill_dmg', 0.0), "Skill DMG", is_percentage=True)) 
    status_differences.append(format_comparison_difference(0.0, user_input_stats_from_session.get('resonance_lib_dmg', 0.0), "Lib. DMG", is_percentage=True)) 
    status_differences.append(format_comparison_difference(0.0, user_input_stats_from_session.get('attribute_dmg_bonus', 0.0), "Attribute DMG", is_percentage=True))
    status_differences.append(format_comparison_difference(0.0, user_input_stats_from_session.get('healing_bonus', 0.0), "Healing Bonus", is_percentage=True))

    # Skor Kategori (Dummy atau Terhitung)
    category_scores = {
        'Character': f"{resonator_obj.rarity}/5", 
        'Weapon': '9/10', # Placeholder
        'Echo': '8/10',   # Placeholder
        'Skill': '10/10', # Placeholder
    }

    return {
        'final_stats': { # Ini adalah stats dari Build yang tersimpan di DB
            'hp': final_hp, 'attack': final_attack, 'defense': final_defense,
            'energy': final_energy, 'crit_rate': final_crit_rate, 'crit_dmg': final_crit_dmg,
            # Bonus DMG dasar, heavy, skill, liberation, attribute_dmg_bonus, healing_bonus TIDAK DIKEMBALIKAN DI SINI
            # karena tidak diambil dari model Build
        },
        'performance_data_json': {
            'labels': chart_labels,
            'datasets': [{
                'label': 'Resonator Performance',
                'data': chart_data_normalized,
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderWidth': 1
            }]
        },
        'resonator_rating': resonator_rating,
        'status_differences': status_differences,
        'category_scores': category_scores,
        'selected_weapon_obj_db': selected_weapon_obj_db, # Gear dari Build di DB
        'selected_echo_obj_db': selected_echo_obj_db,
        'selected_sonata_obj_db': selected_sonata_obj_db,
    }

def build_review_page(request, name):
    resonator = get_object_or_404(Resonator, name__iexact=name) 
    
    # URL gambar karakter
    folder_name = format_folder(resonator.name) 
    image_path = f"{settings.MEDIA_URL}resonator/{folder_name}/"
    images = {"render": f"{image_path}Render.png"}

    # Panggil helper functions untuk mendapatkan bagian-bagian data
    build_review_data = _get_build_review_data(request, resonator)
    difference_stat_data = _get_difference_stat_data(request, resonator, build_review_data) 

    # Gabungkan semua data ke dalam satu konteks
    context = {
        'resonator': resonator,
        'images': images, 
        'user_name': request.user.username if request.user.is_authenticated else 'Guest',
        # PERBAIKAN: Gunakan 'date.today()' karena kita sudah mengimpor 'date' secara langsung
        'current_date': date.today().strftime("%d %B %Y"), 
        'current_character_name': name, 
    }
    
    # Update konteks dengan data dari helper functions
    context.update(build_review_data)
    context.update(difference_stat_data)

    return render(request, 'landingpage/review.html', context)