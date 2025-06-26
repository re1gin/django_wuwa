from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from resonators.models import Resonator
from weapon.models import Weapon
from echo.models import Sonata, Echo


def format_folder(name):
    formatted_name = name.replace(' ', '_')
    return formatted_name

def get_icon_chars_data(current_char_obj=None):
    icon_chars_data = []
    all_resonators = Resonator.objects.all().order_by('name')
    for resonator in all_resonators:
        icon_folder = format_folder(resonator.name)
        icon_url = f"{settings.MEDIA_URL}resonator/{icon_folder}/Icon.png"
        icon_detail_url = reverse('resonators:resonator_detail', kwargs={'name': resonator.name})
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

    if item_type == 'weapon':
        weapon_obj = Weapon.objects.filter(weapon_name=item_name).first()
        if weapon_obj: # Pastikan weapon_obj ditemukan
            details = {
                'name': weapon_obj.weapon_name,
                'rarity': weapon_obj.rarity,
                'weapon_type': weapon_obj.weapon_type.name
            }
            image_url = weapon_obj.icon_image.url
        else:
            return JsonResponse({'details': {}, 'image_url': '', 'filtered_echos': [], 'filtered_sonatas': []}) 

    elif item_type == 'echo':
        echo_obj = Echo.objects.filter(name=item_name).first()
        if echo_obj:
            details = {
                'name': echo_obj.name,
                'cost': echo_obj.cost,
            }
            image_url = echo_obj.icon_echo.url
        else:
            return JsonResponse({'details': {}, 'image_url': '', 'filtered_echos': [], 'filtered_sonatas': []}) 

    elif item_type == 'sonata':
        sonata_obj = Sonata.objects.filter(name=item_name).first()
        if sonata_obj:
            details = {
                'name': sonata_obj.name,
            }
            image_url = sonata_obj.icon_sonata.url
        else:
            return JsonResponse({'details': {}, 'image_url': '', 'filtered_echos': [], 'filtered_sonatas': []}) 

    
    filtered_sonatas_data = []

    if selected_echo_name:
        selected_echo_obj = Echo.objects.filter(name=selected_echo_name).first()
        if selected_echo_obj:
            filtered_sonatas_data = list(selected_echo_obj.sonatas.all().values('name'))
        else:
            filtered_sonatas_data = list(Sonata.objects.all().values('name'))
    else:
        filtered_sonatas_data = list(Sonata.objects.all().values('name'))

    filtered_echos_data = list(Echo.objects.all().values('name'))

    return JsonResponse({
        'details': details,
        'image_url': image_url,
        'filtered_echos': filtered_echos_data,
        'filtered_sonatas': filtered_sonatas_data,
    })
    
def character_builder_view(request, name):
    char_obj = get_object_or_404(Resonator, name__iexact=name)

    folder_name = format_folder(char_obj.name)
    image_path = f"{settings.MEDIA_URL}resonator/{folder_name}/"
    images = {"render": f"{image_path}Render.png"}

    icon_chars_data = get_icon_chars_data(char_obj)

    weapons_data_db = Weapon.objects.filter(weapon_type=char_obj.weapon_type).order_by('weapon_name')
    echos_data_db = Echo.objects.all().order_by('name')
    sonatas_data_db = Sonata.objects.all().order_by('name') 

    # Inisialisasi default user_input_stats
    user_input_stats = {
        'hp': 0.0, 'attack': 0.0, 'defense': 0.0, 'energy': 0.0, 'crit_rate': 0.0, 'crit_dmg': 0.0,
        'basic_atk_dmg': 0.0, 'resonance_skill_dmg': 0.0, 'resonance_lib_dmg': 0.0,
        'healing_bonus': 0.0, 
        'aero_dmg_bonus': 0.0, 'fusion_dmg_bonus': 0.0, 'electro_dmg_bonus': 0.0,
        'glacio_dmg_bonus': 0.0, 'havoc_dmg_bonus': 0.0, 'spectro_dmg_bonus': 0.0,
        'attribute_res': 0.0,
        'selected_weapon': '',
        'selected_echo': '',
        'selected_sonata': '',
    }

    if 'user_input_stats' in request.session and request.session.get('character_name_for_comparison') == char_obj.name:
        user_input_stats.update(request.session['user_input_stats'])
    
    selected_weapon_obj = None
    selected_echo_obj = None
    selected_sonata_obj = None

    # --- Bagian POST Request ---
    if request.method == 'POST':
        try:
            for stat_name in ['hp', 'attack', 'defense', 'energy', 'crit_rate', 'crit_dmg',
                               'basic_atk_dmg', 'resonance_skill_dmg', 'resonance_lib_dmg',
                               'healing_bonus', 
                               # New attribute DMG bonuses
                               'aero_dmg_bonus', 'fusion_dmg_bonus', 'electro_dmg_bonus',
                               'glacio_dmg_bonus', 'havoc_dmg_bonus', 'spectro_dmg_bonus',
                               'attribute_res']: # attribute_res is still here
                user_input_stats[stat_name] = float(request.POST.get(stat_name, 0.0))
        except ValueError:
            messages.error(request, "Input stat harus berupa angka.")
            
            
        user_input_stats['selected_weapon'] = request.POST.get('selected_weapon', '')
        user_input_stats['selected_echo'] = request.POST.get('selected_echo', '')
        user_input_stats['selected_sonata'] = request.POST.get('selected_sonata', '')

        if user_input_stats['selected_echo'] and user_input_stats['selected_sonata']:
            selected_echo_from_post = Echo.objects.filter(name=user_input_stats['selected_echo']).first()
            selected_sonata_from_post = Sonata.objects.filter(name=user_input_stats['selected_sonata']).first()

            if selected_echo_from_post and selected_sonata_from_post:
                if not selected_echo_from_post.sonatas.filter(name=selected_sonata_from_post.name).exists():
                    messages.error(request, f"Sonata '{selected_sonata_from_post.name}' tidak valid untuk Echo '{selected_echo_from_post.name}'. Sonata direset.")
                    user_input_stats['selected_sonata'] = '' 
                    
            elif selected_echo_from_post and not selected_sonata_from_post:
                pass
            
            
            elif not selected_echo_from_post and selected_sonata_from_post:
                messages.error(request, "Sonata tidak dapat dipilih tanpa Echo yang valid. Sonata direset.")
                user_input_stats['selected_sonata'] = '' 
                
        elif user_input_stats['selected_echo'] and not user_input_stats['selected_sonata']:
            pass
        
        elif not user_input_stats['selected_echo'] and user_input_stats['selected_sonata']:
            messages.error(request, "Sonata tidak dapat dipilih tanpa Echo yang dipilih. Sonata direset.")
            user_input_stats['selected_sonata'] = ''

        # Simpan user_input_stats yang sudah diperbarui (termasuk validasi) ke session
        request.session['user_input_stats'] = user_input_stats
        request.session['character_name_for_comparison'] = char_obj.name

        if 'NILAI BUILD' in request.POST:
            return redirect('build:compare_stats', character_name=char_obj.name)
        
    # --- Load selected item objects based on user_input_stats (whether from POST or session) ---
    if user_input_stats['selected_weapon']:
        selected_weapon_obj = Weapon.objects.filter(weapon_name=user_input_stats['selected_weapon']).first()
        if not selected_weapon_obj:
            user_input_stats['selected_weapon'] = '' # Reset if not found
            messages.warning(request, f"Senjata '{user_input_stats['selected_weapon']}' tidak ditemukan. Pilihan direset.")


    if user_input_stats['selected_echo']:
        selected_echo_obj = Echo.objects.filter(name=user_input_stats['selected_echo']).first()
        if not selected_echo_obj:
            user_input_stats['selected_echo'] = '' 
            user_input_stats['selected_sonata'] = '' 
            selected_echo_obj = None 
            selected_sonata_obj = None
            messages.warning(request, f"Echo '{user_input_stats['selected_echo']}' tidak ditemukan. Pilihan direset.")
    else: 
        user_input_stats['selected_sonata'] = ''
        selected_echo_obj = None
        selected_sonata_obj = None


    current_selected_echo_name = user_input_stats.get('selected_echo')
    if current_selected_echo_name:
        echo_for_filter = Echo.objects.filter(name=current_selected_echo_name).first()
        if echo_for_filter:
            sonatas_data_db = echo_for_filter.sonatas.all().order_by('name')
            
            if user_input_stats.get('selected_sonata'):
                selected_sonata_obj = Sonata.objects.filter(name=user_input_stats['selected_sonata']).first()
                if not selected_sonata_obj or not sonatas_data_db.filter(name=selected_sonata_obj.name).exists():
                    messages.warning(request, f"Sonata '{user_input_stats['selected_sonata']}' tidak valid untuk Echo '{current_selected_echo_name}'. Sonata direset.")
                    user_input_stats['selected_sonata'] = ''
                    selected_sonata_obj = None 
            else: 
                selected_sonata_obj = None
        else:
            sonatas_data_db = Sonata.objects.all().order_by('name')
            messages.warning(request, f"Echo '{current_selected_echo_name}' tidak ditemukan. Sonata direset.")
            user_input_stats['selected_echo'] = ''
            user_input_stats['selected_sonata'] = ''
            selected_echo_obj = None
            selected_sonata_obj = None
            
            request.session['user_input_stats'] = user_input_stats
    else:
        sonatas_data_db = Sonata.objects.all().order_by('name')
        
        user_input_stats['selected_sonata'] = ''
        selected_sonata_obj = None

    context = {
        "character": char_obj,
        "images": images,
        "all_characters_for_icons": icon_chars_data,
        "user_input_stats": user_input_stats,
        "weapons_data": weapons_data_db,
        "echos_data": echos_data_db,
        "sonatas_data": sonatas_data_db,
        "selected_weapon_obj": selected_weapon_obj,
        "selected_echo_obj": selected_echo_obj,
        "selected_sonata_obj": selected_sonata_obj,
    }
    return render(request, 'landingpage/character_builder.html', context)
