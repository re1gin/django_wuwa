from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from build.models import UserBuild
from resonators.models import Resonator
from .forms import Build
from weapon.models import Weapon
from echo.models import Sonata, Echo
from .calculations import compare_stats, calculate_character_stats 

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
            return

    elif item_type == 'echo':
        echo_obj = Echo.objects.filter(name=item_name).first()
        if echo_obj:
            details = {
                'name': echo_obj.name,
                'cost': echo_obj.cost,
            }
            image_url = echo_obj.icon_echo.url

    elif item_type == 'sonata':
        sonata_obj = Sonata.objects.filter(name=item_name).first()
        if sonata_obj:
            details = {
                'name': sonata_obj.name,
            }
            image_url = sonata_obj.icon_sonata.url

    # --- Bagian Baru untuk Validasi Echo -> Sonata (dengan ManyToManyField) ---
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
        'def_interruption': 0.0, 'healing_bonus': 0.0, 'attribute_dmg_bonus': 0.0, 'attribute_res': 0.0,
        
        'selected_weapon': '',
        'selected_echo': '',
        'selected_sonata': '',
    }


    selected_weapon_obj = None
    selected_echo_obj = None
    selected_sonata_obj = None

    # --- Bagian POST Request ---
    if request.method == 'POST':
        # Tangani input stat
        try:
            for stat_name in ['hp', 'attack', 'defense', 'energy', 'crit_rate', 'crit_dmg',
                             'basic_atk_dmg', 'resonance_skill_dmg', 'resonance_lib_dmg',
                             'def_interruption', 'healing_bonus', 'attribute_dmg_bonus', 'attribute_res']:
                user_input_stats[stat_name] = float(request.POST.get(stat_name, 0.0))
        except ValueError:
            messages.error(request, "Input stat harus berupa angka.")
            # Pada error, kita akan membiarkan logika di bawah (di luar POST) yang mengisi selected_obj dan sonatas_data_db.
            # Jangan return di sini agar alur kode tetap berlanjut.

        # Ambil pilihan dropdown dari POST
        user_input_stats['selected_weapon'] = request.POST.get('selected_weapon', '')
        user_input_stats['selected_echo'] = request.POST.get('selected_echo', '')
        user_input_stats['selected_sonata'] = request.POST.get('selected_sonata', '')

        # Validasi backend: Jika Echo dipilih, Sonata harus sesuai (dengan ManyToManyField)
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
        
   
    if user_input_stats['selected_weapon']:
        selected_weapon_obj = Weapon.objects.filter(weapon_name=user_input_stats['selected_weapon']).first()
        if not selected_weapon_obj:
            user_input_stats['selected_weapon'] = ''

    if user_input_stats['selected_echo']:
        selected_echo_obj = Echo.objects.filter(name=user_input_stats['selected_echo']).first()
        if not selected_echo_obj:
            user_input_stats['selected_echo'] = '' # RESET NILAI DI user_input_stats
            user_input_stats['selected_sonata'] = '' # RESET SONATA JUGA
            selected_echo_obj = None # PASTIKAN OBJEKNYA NONE
    else: # JIKA selected_echo DARI SESI/INPUT SUDAH KOSONG DARI AWAL
        user_input_stats['selected_sonata'] = ''
        selected_echo_obj = None
        selected_sonata_obj = None


    # --- Filtering data untuk dropdown Sonata berdasarkan Echo yang dipilih ---
    current_selected_echo_name = user_input_stats.get('selected_echo')
    if current_selected_echo_name:
        echo_for_filter = Echo.objects.filter(name=current_selected_echo_name).first()
        if echo_for_filter:
            sonatas_data_db = echo_for_filter.sonatas.all().order_by('name')
            # Sekarang validasi Sonata yang dipilih: apakah masih valid untuk Echo ini?
            if user_input_stats.get('selected_sonata'):
                selected_sonata_obj = Sonata.objects.filter(name=user_input_stats['selected_sonata']).first()
                if not selected_sonata_obj or not sonatas_data_db.filter(name=selected_sonata_obj.name).exists():
                    messages.warning(request, f"Sonata '{user_input_stats['selected_sonata']}' tidak valid untuk Echo '{current_selected_echo_name}'. Sonata direset.")
                    user_input_stats['selected_sonata'] = ''
                    selected_sonata_obj = None # Pastikan objeknya juga None
        else: # Echo yang dipilih dari session/POST tidak ditemukan di DB
            sonatas_data_db = Sonata.objects.all().order_by('name') # Tampilkan semua Sonata
            messages.warning(request, f"Echo '{current_selected_echo_name}' tidak ditemukan. Sonata direset.")
            user_input_stats['selected_echo'] = ''
            user_input_stats['selected_sonata'] = ''
            selected_echo_obj = None
            selected_sonata_obj = None
            # Update session agar konsisten dengan apa yang ditampilkan (jika tidak di-redirect)
            request.session['user_input_stats'] = user_input_stats
    else: # Jika tidak ada Echo yang dipilih (user_input_stats['selected_echo'] kosong)
        sonatas_data_db = Sonata.objects.all().order_by('name')
        # Pastikan Sonata juga direset jika Echo kosong
        user_input_stats['selected_sonata'] = ''
        selected_sonata_obj = None

    # Pastikan image_url ditambahkan ke objek terpilih sebelum dikirim ke konteks
    if selected_weapon_obj:
        selected_weapon_obj.image_url = f"{settings.MEDIA_URL}resonator/{format_folder(char_obj.weapon)}/{format_folder(selected_weapon_obj.weapon_name)}.png"
    if selected_echo_obj:
        selected_echo_obj.image_url = f"{settings.MEDIA_URL}{selected_echo_obj.icon_echo.url}"
    if selected_sonata_obj:
        selected_sonata_obj.image_url = f"{settings.MEDIA_URL}{selected_sonata_obj.icon_sonata.url}.png"

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

@login_required
def build_history_view(request):
    user_builds = UserBuild.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'user_builds': user_builds
    }
    return render(request, 'landingpage/build_history.html', context)

@login_required
def view_saved_build_detail(request, build_id):
    build = get_object_or_404(UserBuild, id=build_id, user=request.user)
    
    # Prepare user_input_data for calculation/comparison from the saved build
    user_input_data_for_calc = {
        'hp': build.hp,
        'attack': build.attack,
        'defense': build.defense,
        'energy': build.energy,
        'crit_rate': build.crit_rate,
        'crit_dmg': build.crit_dmg,
        'basic_atk_dmg': build.basic_atk_dmg,
        'resonance_skill_dmg': build.resonance_skill_dmg,
        'resonance_lib_dmg': build.resonance_lib_dmg,
        'def_interruption': build.def_interruption,
        'healing_bonus': build.healing_bonus,
        'attribute_dmg_bonus': build.attribute_dmg_bonus,
        'attribute_res': build.attribute_res,
        'selected_weapon': build.selected_weapon.weapon_name if build.selected_weapon else '',
        'selected_echo': build.selected_echo.name if build.selected_echo else '',
        'selected_sonata': build.selected_sonata.name if build.selected_sonata else '',
    }
    
    calculated_results_for_display = calculate_character_stats(user_input_data_for_calc)
    
    # Juga tampilkan perbandingan dengan ideal build di detail view
    # Ini akan memanggil fuzzy logic
    try:
        ideal_build = Build.objects.get(character=build.resonator)
        comparison_results = compare_stats(user_input_data_for_calc, ideal_build)
    except Build.DoesNotExist:
        ideal_build = None
        comparison_results = {'recommendations': ["No ideal build found for this character."], 'item_recommendations': {}, 'priority_stat': 'N/A', 'overall_priority_val': 0}

    context = {
        'build': build,
        'calculated_results': calculated_results_for_display,
        'ideal_build': ideal_build,
        'comparison_results': comparison_results,
        'images': {"render": f"{request.build_absolute_uri('/')}static/resonator/{format_folder(build.resonator.name)}/Render.png"},
    }
    return render(request, 'landingpage/build_detail.html', context)

@login_required
@require_POST
def delete_saved_build(request, build_id):
    build = get_object_or_404(UserBuild, id=build_id, user=request.user)
    build.delete()
    messages.success(request, f"Build '{build.build_name}' deleted successfully.")
    return redirect('build:build_history')

def compare_stats_view(request, character_name):
    character = get_object_or_404(Resonator, name__iexact=character_name)
    
    # Ambil user_input_stats dari sesi (ini adalah stat yang baru saja di-submit dari builder)
    user_stats = request.session.get('user_input_stats', {})
    
    if not user_stats:
        messages.warning(request, "No stats found for comparison. Please create a build first.")
        return redirect('build:character_builder', name=character_name)

    ideal_build = None
    try:
        ideal_build = Build.objects.get(character=character)
    except Build.DoesNotExist:
        messages.error(request, f"No ideal build defined for {character.name}. Cannot compare stats.")
        # Anda bisa redirect atau menampilkan halaman kosong
        return render(request, 'landingpage/compare_stats.html', {
            'character': character,
            'user_stats': user_stats,
            'ideal_build': None,
            'comparison_results': {'recommendations': ["No ideal build found."], 'item_recommendations': {}, 'priority_stat': 'N/A', 'overall_priority_val': 0}
        })
    
    # Panggil fungsi compare_stats yang sudah menggunakan fuzzy logic
    comparison_results = compare_stats(user_stats, ideal_build)

    context = {
        'character': character,
        'ideal_build': ideal_build,
        'user_stats': user_stats,
        'comparison_results': comparison_results,
    }
    return render(request, 'landingpage/compare_stats.html', context)
