from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from resonators.models import Resonator
from .forms import Build
from weapon.models import Weapon
from echo.models import Sonata, Echo # Pastikan Sonata dan Echo sudah diimpor


def format_folder(name):
    formatted_name = name.replace(' ', '_')
    return formatted_name

def get_icon_chars_data(current_char_obj=None):
    icon_chars_data = []
    all_resonators = Resonator.objects.all().order_by('name')
    for resonator in all_resonators:
        icon_folder = format_folder(resonator.name)
        icon_url = f"{settings.STATIC_URL}resonator/{icon_folder}/Icon.png"
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

# build/views.py

def get_item_details_ajax(request):
    # Pastikan ini POST karena JavaScript Anda mengirim POST
    item_type = request.POST.get('item_type')
    item_name = request.POST.get('item_name')
    selected_echo_name = request.POST.get('selected_echo_name') # Juga harus POST

    details = {}
    image_url = ""

    if item_type == 'weapon':
        weapon_obj = Weapon.objects.filter(weapon_name=item_name).first()
        if weapon_obj:
            details = {
                'name': weapon_obj.weapon_name,
            }
            image_url = f"{settings.STATIC_URL}assets/ikon/weapon/{format_folder(weapon_obj.weapon_name)}.png"

    elif item_type == 'echo':
        echo_obj = Echo.objects.filter(name=item_name).first()
        if echo_obj:
            details = {
                'name': echo_obj.name,
            }
            image_url = f"{settings.STATIC_URL}assets/ikon/echo/{format_folder(echo_obj.name)}_Icon.png"

    elif item_type == 'sonata':
        sonata_obj = Sonata.objects.filter(name=item_name).first()
        if sonata_obj:
            details = {
                'name': sonata_obj.name,
            }
            # Path ini sudah benar
            image_url = f"{settings.STATIC_URL}assets/ikon/sonata/{format_folder(sonata_obj.name)}.png"

    # --- Bagian Baru untuk Validasi Echo -> Sonata (dengan ManyToManyField) ---
    filtered_sonatas_data = []

    if selected_echo_name:
        selected_echo_obj = Echo.objects.filter(name=selected_echo_name).first()
        if selected_echo_obj:
            # Mengambil semua Sonata yang terkait dengan Echo yang dipilih
            filtered_sonatas_data = list(selected_echo_obj.sonatas.all().values('name'))
        else:
            # Jika Echo dipilih tapi tidak ditemukan, tampilkan semua sonata (atau kosongkan)
            filtered_sonatas_data = list(Sonata.objects.all().values('name'))
    else:
        # Jika tidak ada Echo yang dipilih, tampilkan semua Sonata
        filtered_sonatas_data = list(Sonata.objects.all().values('name'))

    # Echos tidak difilter oleh AJAX di sini karena logika hanya satu arah (Echo -> Sonata)
    filtered_echos_data = list(Echo.objects.all().values('name'))

    return JsonResponse({
        'details': details,
        'image_url': image_url,
        'filtered_echos': filtered_echos_data, # Akan selalu semua jika tidak ada filter balik
        'filtered_sonatas': filtered_sonatas_data,
    })

def character_builder_view(request, name):
    char_obj = get_object_or_404(Resonator, name__iexact=name)

    folder_name = format_folder(char_obj.name)
    image_path = f"{settings.STATIC_URL}resonator/{folder_name}/"
    images = {"render": f"{image_path}Render.png"}

    icon_chars_data = get_icon_chars_data(char_obj)

    weapons_data_db = Weapon.objects.filter(weapon_type__iexact=char_obj.weapon).order_by('weapon_name')
    echos_data_db = Echo.objects.all().order_by('name') # Awalnya semua Echo
    sonatas_data_db = Sonata.objects.all().order_by('name') # Awalnya semua Sonata

    user_input_stats = {
        'hp': 0.0, 'attack': 0.0, 'defense': 0.0, 'energy': 0.0, 'crit_rate': 0.0, 'crit_dmg': 0.0,
        'basic_atk_dmg': 0.0, 'resonance_skill_dmg': 0.0, 'resonance_lib_dmg': 0.0,
        'def_interruption': 0.0, 'healing_bonus': 0.0, 'attribute_dmg_bonus': 0.0, 'attribute_res': 0.0,
        'selected_weapon': '',
        'selected_echo': '',
        'selected_sonata': '',
    }

    if 'user_input_stats' in request.session:
        user_input_stats.update(request.session['user_input_stats'])

    selected_weapon_obj = None
    selected_echo_obj = None
    selected_sonata_obj = None

    if request.method == 'POST':
        try:
            for stat_name in ['hp', 'attack', 'defense', 'energy', 'crit_rate', 'crit_dmg',
                               'basic_atk_dmg', 'resonance_skill_dmg', 'resonance_lib_dmg',
                               'def_interruption', 'healing_bonus', 'attribute_dmg_bonus', 'attribute_res']:
                user_input_stats[stat_name] = float(request.POST.get(stat_name, 0.0))
        except ValueError:
            messages.error(request, "Input stat harus berupa angka.")
            if user_input_stats['selected_weapon']:
                selected_weapon_obj = Weapon.objects.filter(weapon_name=user_input_stats['selected_weapon']).first()
                if selected_weapon_obj:
                    selected_weapon_obj.image_url = f"{settings.STATIC_URL}assets/ikon/weapon/{format_folder(char_obj.weapon)}/{format_folder(selected_weapon_obj.weapon_name)}.png"
                    print(f"DEBUG (POST, Error): Weapon URL: {selected_weapon_obj.image_url}")

            if user_input_stats['selected_echo']:
                selected_echo_obj = Echo.objects.filter(name=user_input_stats['selected_echo']).first()
                if selected_echo_obj:
                    selected_echo_obj.image_url = f"{settings.STATIC_URL}assets/ikon/echo/{format_folder(selected_echo_obj.name)}_Icon.png"

            if user_input_stats['selected_sonata']:
                selected_sonata_obj = Sonata.objects.filter(name=user_input_stats['selected_sonata']).first()
                if selected_sonata_obj:
                    selected_sonata_obj.image_url = f"{settings.STATIC_URL}assets/ikon/sonata/{format_folder(selected_sonata_obj.name)}.png"

            # Untuk memastikan dropdown Sonata difilter ulang saat ada error POST
            current_selected_echo_name = user_input_stats.get('selected_echo')
            if current_selected_echo_name:
                echo_for_filter = Echo.objects.filter(name=current_selected_echo_name).first()
                if echo_for_filter:
                    sonatas_data_db = echo_for_filter.sonatas.all().order_by('name')
                else:
                    sonatas_data_db = Sonata.objects.all().order_by('name') # Fallback jika Echo tidak ditemukan
            else:
                sonatas_data_db = Sonata.objects.all().order_by('name')


            context = {
                "character": char_obj, "images": images, "all_characters_for_icons": icon_chars_data,
                "user_input_stats": user_input_stats, "weapons_data": weapons_data_db,
                "echos_data": echos_data_db, "sonatas_data": sonatas_data_db, # Ini mungkin difilter
                "selected_weapon_obj": selected_weapon_obj,
                "selected_echo_obj": selected_echo_obj,
                "selected_sonata_obj": selected_sonata_obj,
            }
            return render(request, 'landingpage/character_builder.html', context)

        user_input_stats['selected_weapon'] = request.POST.get('selected_weapon', '')
        user_input_stats['selected_echo'] = request.POST.get('selected_echo', '')
        user_input_stats['selected_sonata'] = request.POST.get('selected_sonata', '')

        # Validasi backend: Jika Echo dipilih, Sonata harus sesuai (dengan ManyToManyField)
        if user_input_stats['selected_echo'] and user_input_stats['selected_sonata']:
            selected_echo_from_post = Echo.objects.filter(name=user_input_stats['selected_echo']).first()
            selected_sonata_from_post = Sonata.objects.filter(name=user_input_stats['selected_sonata']).first()

            if selected_echo_from_post and selected_sonata_from_post:
                # Periksa apakah Sonata yang dipilih termasuk dalam ManyToManyField 'sonatas' dari Echo
                if not selected_echo_from_post.sonatas.filter(name=selected_sonata_from_post.name).exists():
                    messages.error(request, f"Sonata '{selected_sonata_from_post.name}' tidak valid untuk Echo '{selected_echo_from_post.name}'.")
                    user_input_stats['selected_sonata'] = '' # Reset Sonata yang tidak valid
                    # selected_sonata_obj = None # Ini akan di-reset di bagian GET nanti
            # Jika salah satu tidak ditemukan, biarkan pengguna memilih (tidak ada validasi paksa di sini)

        request.session['user_input_stats'] = user_input_stats
        request.session['character_name_for_comparison'] = char_obj.name

        if 'NILAI BUILD' in request.POST:
            return redirect('build:compare_build', name=char_obj.name)
        else:
            pass

    # Untuk GET request (atau setelah POST non-'NILAI BUILD')
    # Ambil selected objects dari DB untuk ditampilkan di dropdown (agar tetap 'selected')
    if user_input_stats['selected_weapon']:
        selected_weapon_obj = Weapon.objects.filter(weapon_name=user_input_stats['selected_weapon']).first()
        if selected_weapon_obj:
            selected_weapon_obj.image_url = f"{settings.STATIC_URL}assets/ikon/weapon/{format_folder(char_obj.weapon)}/{format_folder(selected_weapon_obj.weapon_name)}.png"
            print(f"DEBUG (GET): Weapon URL: {selected_weapon_obj.image_url}")

    if user_input_stats['selected_echo']:
        selected_echo_obj = Echo.objects.filter(name=user_input_stats['selected_echo']).first()
        if selected_echo_obj:
            selected_echo_obj.image_url = f"{settings.STATIC_URL}assets/ikon/echo/{format_folder(selected_echo_obj.name)}_Icon.png"

    if user_input_stats['selected_sonata']:
        selected_sonata_obj = Sonata.objects.filter(name=user_input_stats['selected_sonata']).first()
        if selected_sonata_obj:
            selected_sonata_obj.image_url = f"{settings.STATIC_URL}assets/ikon/sonata/{format_folder(selected_sonata_obj.name)}.png"

    # --- Filtering data untuk dropdown awal (atau setelah POST tanpa redirect) ---
    # Jika ada Echo yang dipilih dari sesi, filter Sonata
    current_selected_echo_name = user_input_stats.get('selected_echo')
    if current_selected_echo_name:
        echo_for_filter = Echo.objects.filter(name=current_selected_echo_name).first()
        if echo_for_filter:
            # Mengambil semua Sonata yang terkait dengan Echo ini
            sonatas_data_db = echo_for_filter.sonatas.all().order_by('name')
            # Jika Sonata yang dipilih dari sesi tidak valid untuk Echo ini, reset
            if user_input_stats.get('selected_sonata') and \
               not sonatas_data_db.filter(name=user_input_stats['selected_sonata']).exists():
                user_input_stats['selected_sonata'] = ''
                selected_sonata_obj = None # Juga reset objeknya
        else:
            # Jika Echo dipilih tapi tidak ditemukan, tampilkan semua sonata
            sonatas_data_db = Sonata.objects.all().order_by('name')
            # Reset Sonata jika Echo sebelumnya tidak ditemukan
            if user_input_stats.get('selected_sonata'):
                 user_input_stats['selected_sonata'] = ''
                 selected_sonata_obj = None
    else:
        # Jika tidak ada Echo yang dipilih, tampilkan semua Sonata
        sonatas_data_db = Sonata.objects.all().order_by('name')
    
    # Echos_data_db tetap semua Echo karena Echo tidak difilter oleh pilihan Sonata

    context = {
        "character": char_obj, "images": images, "all_characters_for_icons": icon_chars_data,
        "user_input_stats": user_input_stats, "weapons_data": weapons_data_db,
        "echos_data": echos_data_db, # Ini akan selalu semua Echo
        "sonatas_data": sonatas_data_db, # Ini mungkin difilter
        "selected_weapon_obj": selected_weapon_obj,
        "selected_echo_obj": selected_echo_obj,
        "selected_sonata_obj": selected_sonata_obj,
    }
    return render(request, 'landingpage/character_builder.html', context)


def compare_build_view(request, name):
    char_obj = get_object_or_404(Resonator, name__iexact=name)
    ideal_build = get_object_or_404(Build, character=char_obj)

    user_input_stats = request.session.get('user_input_stats', {})
    if not user_input_stats:
        return redirect('build:character_builder', name=char_obj.name)

    selected_weapon_obj = None
    selected_echo_obj = None
    selected_sonata_obj = None

    selected_weapon_json_detail = None
    selected_echo_json_detail = None
    selected_sonata_json_detail = None

    if user_input_stats.get('selected_weapon'):
        selected_weapon_obj = Weapon.objects.filter(weapon_name=user_input_stats['selected_weapon']).first()
        if selected_weapon_obj:
            selected_weapon_obj.image_url = f"{settings.STATIC_URL}assets/ikon/weapon/{format_folder(char_obj.weapon)}/{format_folder(selected_weapon_obj.weapon_name)}.png"

    if user_input_stats.get('selected_echo'):
        selected_echo_obj = Echo.objects.filter(name=user_input_stats['selected_echo']).first()
        if selected_echo_obj:
            selected_echo_obj.image_url = f"{settings.STATIC_URL}assets/ikon/echo/{format_folder(selected_echo_obj.name)}_Icon.png"

    if user_input_stats.get('selected_sonata'):
        selected_sonata_obj = Sonata.objects.filter(name=user_input_stats['selected_sonata']).first()
        if selected_sonata_obj:
            selected_sonata_obj.image_url = f"{settings.STATIC_URL}assets/ikon/sonata/{format_folder(selected_sonata_obj.name)}.png"

    # --- Lakukan Logika Perbandingan dan Penilaian di sini ---
    comparison_results = {}
    rating_score = 0

    base_stats_to_compare = ['hp', 'attack', 'defense', 'energy', 'crit_rate', 'crit_dmg']
    for stat in base_stats_to_compare:
        ideal_val = getattr(ideal_build, stat)
        user_val = user_input_stats.get(stat, 0.0)
        comparison_results[stat] = {
            'ideal': ideal_val,
            'user': user_val,
            'difference': user_val - ideal_val
        }
        if ideal_val > 0:
            score_contribution = min(1.0, user_val / ideal_val) * 10
            rating_score += score_contribution
        else:
            if user_val > 0:
                rating_score += 5

    if selected_weapon_obj:
        if selected_weapon_obj.rarity == 5:
            rating_score += 15
        elif selected_weapon_obj.rarity == 4:
            rating_score += 10

    if selected_echo_obj:
        # Menambahkan penilaian berdasarkan cost (jika relevan) atau rarity
        # Contoh: Echo cost 4 bisa beri bonus lebih
        if selected_echo_obj.rarity == 5:
            rating_score += 10
        if selected_echo_obj.cost == 4: # Misalnya jika cost 4 echo adalah yang paling bagus
            rating_score += 5

    if selected_sonata_obj:
        # Contoh: penilaian berdasarkan nama sonata atau efek set
        if selected_sonata_obj.name == 'Molten Rift': # Contoh sonata yang ideal untuk karakter DPS api
            rating_score += 10
        elif selected_sonata_obj.name == 'Lingering Tunes':
            rating_score += 5

    bonus_stats_from_user = {
        'basic_atk_dmg': user_input_stats.get('basic_atk_dmg', 0.0),
        'resonance_skill_dmg': user_input_stats.get('resonance_skill_dmg', 0.0),
        'resonance_lib_dmg': user_input_stats.get('resonance_lib_dmg', 0.0),
        'def_interruption': user_input_stats.get('def_interruption', 0.0),
        'healing_bonus': user_input_stats.get('healing_bonus', 0.0),
        'attribute_dmg_bonus': user_input_stats.get('attribute_dmg_bonus', 0.0),
        'attribute_res': user_input_stats.get('attribute_res', 0.0),
    }

    overall_rating = "Bad"
    if rating_score > 70:
        overall_rating = "Average"
    if rating_score > 120:
        overall_rating = "Good"
    if rating_score > 180:
        overall_rating = "Excellent!"

    context = {
        'character': char_obj,
        'ideal_build': ideal_build,
        'user_input_stats': user_input_stats,
        'comparison_results': comparison_results,
        'bonus_stats_from_user': bonus_stats_from_user,
        'overall_rating': overall_rating,
        'rating_score': round(rating_score, 2),
        'page_title': f"Hasil Penilaian Build untuk {char_obj.name}",
        'selected_weapon_obj': selected_weapon_obj,
        'selected_echo_obj': selected_echo_obj,
        'selected_sonata_obj': selected_sonata_obj,
        'selected_weapon_json_detail': selected_weapon_json_detail,
        'selected_echo_json_detail': selected_echo_json_detail,
        'selected_sonata_json_detail': selected_sonata_json_detail,
    }

    return render(request, 'landingpage/compare_build.html', context)