from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from resonators.models import Resonator
from .forms import Build

def add_build(request):
    if request.method == 'POST':
        form = Build(request.POST)
        if form.is_valid():
            form.save()
            return redirect('build:build_success')
    else:
        form = Build()

    context = {
        'form': form,
        'page_title': 'Tambah Stat Rekomendasi'
    }
    return render(request, 'dashboard/build_form.html', context)

def build_success(request):
    return render(request, 'dashboard/success_page.html', {'message': 'Stat rekomendasi berhasil ditambahkan!', 'back_url_name': 'build_app:add_stat_final'})


# --- Helper functions (tetap sama) ---
def format_folder(name):
    formatted_name = name.replace(' ', '_')
    formatted_name = formatted_name.replace('’', '').replace(',', '')
    return formatted_name

# build/views.py atau resonators/views.py (tergantung di mana fungsi ini berada)

from django.urls import reverse # Pastikan ini sudah diimpor
from django.conf import settings
from resonators.models import Resonator # Pastikan model Resonator diimpor

# --- Helper function (format_folder, tetap sama) ---
def format_folder(name):
    formatted_name = name.replace(' ', '_')
    formatted_name = formatted_name.replace('’', '').replace(',', '')
    return formatted_name

def get_icon_chars_data(current_char_obj=None): # Parameter current_char_obj sekarang opsional
    icon_chars_data = []
    
    # Ambil semua objek Resonator dari database
    # Anda mungkin ingin mengurutkannya, misalnya berdasarkan nama karakter
    all_resonators = Resonator.objects.all().order_by('character')

    for resonator in all_resonators:
        icon_folder = format_folder(resonator.character)
        icon_url = f"{settings.MEDIA_URL}{icon_folder}/Icon.png"
        
        # URL detail harus mengarah ke halaman detail resonator yang sesuai
        icon_detail_url = reverse('resonators:resonator_detail', kwargs={'character_name': resonator.character})
        attribute_icon_url = ''
        if resonator.attribute:
            attribute_icon_url = f"{settings.STATIC_URL}assets/ikon/attribute/{resonator.attribute}.png"
        else:
            # Opsional: Ikon default jika elemen tidak ada
            attribute_icon_url = f"{settings.STATIC_URL}assets/ikon/attribute/Default.png"
        # Tentukan apakah ikon ini adalah karakter yang sedang aktif/dilihat
        # Jika current_char_obj diberikan dan cocok, maka set is_active menjadi True
        is_active_icon = False
        if current_char_obj and resonator.character == current_char_obj.character:
            is_active_icon = True

        icon_chars_data.append({
            'icon_url': icon_url,
            'character_name': resonator.character,
            'detail_url': icon_detail_url,
            'is_active': is_active_icon,
            'attribute_icon_url': attribute_icon_url,
            'attribute_name': resonator.attribute,
        })
        
    return icon_chars_data


# --- VIEW UNTUK HALAMAN BUILDER ---
def character_builder_view(request, character_name):
    char_obj = get_object_or_404(Resonator, character=character_name)

    folder_name = format_folder(char_obj.character)
    image_path = f"{settings.MEDIA_URL}{folder_name}/"
    images = {"render": f"{image_path}Render.png"}

    icon_chars_data = get_icon_chars_data(char_obj)

    # Inisialisasi dictionary untuk menyimpan nilai input pengguna (akan diisi dari POST atau default)
    user_input_stats = {
        'hp': 0.0, 'attack': 0.0, 'defense': 0.0, 'energy': 0.0, 'crit_rate': 0.0, 'crit_dmg': 0.0,
        'basic_atk_dmg': 0.0, 'resonance_skill_dmg': 0.0, 'resonance_lib_dmg': 0.0,
        'def_interruption': 0.0, 'healing_bonus': 0.0, 'attribute_dmg_bonus': 0.0, 'attribute_res': 0.0,
    }

    if request.method == 'POST':
        # Ambil semua nilai input dari request.POST
        try:
            for stat_name in user_input_stats.keys():
                user_input_stats[stat_name] = float(request.POST.get(stat_name, 0.0))
        except ValueError:
            # Jika ada input yang bukan angka, Anda bisa menambahkan pesan error
            print("Error: Semua input stat harus berupa angka.")
            messages.error(request, "Input stat harus berupa angka.")
            # Lalu render ulang halaman dengan nilai yang diinput (yang valid) atau nilai default

        # --- TERUSKAN DATA KE HALAMAN PERBANDINGAN/PENILAIAN ---
        # Kita akan menggunakan session untuk meneruskan data, karena data ini tidak disimpan ke DB.
        # Atau, kita bisa meneruskannya sebagai query parameters (jika datanya tidak terlalu banyak)
        # Session lebih baik untuk data yang lebih banyak atau sensitif.

        request.session['user_input_stats'] = user_input_stats
        request.session['character_name_for_comparison'] = char_obj.character # Simpan nama karakter juga

        # Redirect ke halaman penilaian (misalnya, 'build:compare_build')
        # URL ini harus dibuat di build/urls.py
        return redirect('build:compare_build', character_name=character_name)

    # Untuk GET request, kirimkan nilai default (0.0) ke template
    context = {
        "character": char_obj,
        "images": images,
        "all_characters_for_icons": icon_chars_data,
        "user_input_stats": user_input_stats, # Kirimkan dictionary ini ke template
    }
    return render(request, 'landingpage/character_builder.html', context)


def compare_build_view(request, character_name):
    char_obj = get_object_or_404(Resonator, character=character_name)

    # Ambil stat ideal dari database
    # Pastikan Anda punya entri BuildStat untuk karakter ini di DB Anda
    ideal_build = get_object_or_404(Build, character=char_obj)

    # Ambil input pengguna dari session
    user_input_stats = request.session.get('user_input_stats', {})
    if not user_input_stats:
        # Jika tidak ada data di session (misalnya, pengguna langsung ke URL ini)
        return redirect('build:character_builder', character_name=character_name) # Kembali ke builder

    # --- Lakukan Logika Perbandingan dan Penilaian di sini ---
    # Contoh sederhana:
    comparison_results = {}
    rating_score = 0
    total_ideal_stats = 0
    total_user_stats = 0

    # Bandingkan stat dasar
    base_stats_to_compare = ['hp', 'attack', 'defense', 'energy', 'crit_rate', 'crit_dmg']
    for stat in base_stats_to_compare:
        ideal_val = getattr(ideal_build, stat)
        user_val = user_input_stats.get(stat, 0.0)
        comparison_results[stat] = {
            'ideal': ideal_val,
            'user': user_val,
            'difference': user_val - ideal_val
        }
        total_ideal_stats += ideal_val
        total_user_stats += user_val
        # Logika penilaian sederhana
        if user_val >= ideal_val:
            rating_score += 10 # Contoh: bonus jika stat user lebih tinggi dari ideal
        else:
            rating_score += (user_val / ideal_val) * 10 # Contoh: skor proporsional

    # Anda juga bisa menampilkan input bonus stat pengguna
    bonus_stats_from_user = {
        'basic_atk_dmg': user_input_stats.get('basic_atk_dmg', 0.0),
        'resonance_skill_dmg': user_input_stats.get('resonance_skill_dmg', 0.0),
        'resonance_lib_dmg': user_input_stats.get('resonance_lib_dmg', 0.0),
        'def_interruption': user_input_stats.get('def_interruption', 0.0),
        'healing_bonus': user_input_stats.get('healing_bonus', 0.0),
        'attribute_dmg_bonus': user_input_stats.get('attribute_dmg_bonus', 0.0),
        'attribute_res': user_input_stats.get('attribute_res', 0.0),
    }

    # Contoh total rating
    overall_rating = "Bad"
    if rating_score > 50:
        overall_rating = "Average"
    if rating_score > 80:
        overall_rating = "Good"
    if rating_score > 100:
        overall_rating = "Excellent!"

    context = {
        'character': char_obj,
        'ideal_build': ideal_build, # Objek stat ideal dari DB
        'user_input_stats': user_input_stats, # Semua input pengguna
        'comparison_results': comparison_results, # Hasil perbandingan stat dasar
        'bonus_stats_from_user': bonus_stats_from_user, # Hanya bonus stats dari input
        'overall_rating': overall_rating, # Penilaian keseluruhan
        'rating_score': rating_score, # Skor mentah
        'page_title': f"Hasil Penilaian Build untuk {char_obj.character}"
    }

    return render(request, 'landingpage/compare_build.html', context) # Buat template ini
