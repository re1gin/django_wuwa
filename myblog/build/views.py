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


def format_folder(name):
    formatted_name = name.replace(' ', '_')
    return formatted_name

def get_icon_chars_data(current_char_obj=None):
    """
    Mengambil data ikon untuk semua karakter resonator, digunakan di sidebar atau daftar.
    Menandai ikon karakter yang sedang aktif/dilihat.
    """
    icon_chars_data = []
    
    # PERBAIKAN: Gunakan 'character_name' sebagai field untuk ordering
    all_resonators = Resonator.objects.all().order_by('character_name')

    for resonator in all_resonators:
        # Nama folder akan persis sama dengan character_name dari database/JSON
        icon_folder = format_folder(resonator.character_name)
        
        # PERBAIKAN: Gunakan settings.STATIC_URL untuk aset statis
        icon_url = f"{settings.STATIC_URL}resonator/{icon_folder}/Icon.png"
        icon_detail_url = reverse('resonators:resonator_detail', kwargs={'character_name': resonator.character_name})
        
        is_active_icon = False
        # PERBAIKAN: Bandingkan berdasarkan character_name
        if current_char_obj and resonator.character_name == current_char_obj.character_name:
            is_active_icon = True

        icon_chars_data.append({
            'icon_url': icon_url,
            'character_name': resonator.character_name, # PERBAIKAN: Gunakan character_name
            'detail_url': icon_detail_url,
            'is_active': is_active_icon,
        })
        
    return icon_chars_data


# --- VIEW UNTUK HALAMAN BUILDER ---
def character_builder_view(request, character_name):
    """
    Menampilkan halaman builder karakter, memungkinkan pengguna memasukkan statistik
    dan kemudian membandingkannya.
    """
    # PERBAIKAN: Mengatasi FieldError. Gunakan 'character_name' untuk mencari di model Resonator.
    # Karena URL Anda juga menggunakan 'character_name' secara mentah (dari re_path),
    # Anda bisa langsung mencocokkannya. Gunakan __iexact untuk pencarian case-insensitive.
    char_obj = get_object_or_404(Resonator, character_name__iexact=character_name)

    # Nama folder akan persis sama dengan character_name dari DB (karena format_folder tidak mengubahnya)
    folder_name = format_folder(char_obj.character_name)
    
    # PERBAIKAN: Gunakan settings.STATIC_URL untuk aset statis
    image_path = f"{settings.STATIC_URL}resonator/{folder_name}/"
    images = {"render": f"{image_path}Render.png"}

    # Mengambil data ikon untuk sidebar
    # Pastikan get_icon_chars_data sudah didefinisikan atau diimpor di file ini
    icon_chars_data = get_icon_chars_data(char_obj)

    # Inisialisasi dictionary untuk menyimpan nilai input pengguna
    user_input_stats = {
        'hp': 0.0, 'attack': 0.0, 'defense': 0.0, 'energy': 0.0, 'crit_rate': 0.0, 'crit_dmg': 0.0,
        'basic_atk_dmg': 0.0, 'resonance_skill_dmg': 0.0, 'resonance_lib_dmg': 0.0,
        'def_interruption': 0.0, 'healing_bonus': 0.0, 'attribute_dmg_bonus': 0.0, 'attribute_res': 0.0,
    }

    if request.method == 'POST':
        # Ambil semua nilai input dari request.POST
        try:
            for stat_name in user_input_stats.keys():
                # Gunakan float() dan default 0.0 jika input kosong atau tidak valid
                user_input_stats[stat_name] = float(request.POST.get(stat_name, 0.0))
        except ValueError:
            # Jika ada input yang bukan angka, tambahkan pesan error
            print("Error: Semua input stat harus berupa angka.") # Untuk debug konsol
            messages.error(request, "Input stat harus berupa angka.") # Untuk ditampilkan di template
            # Tetap render ulang halaman dengan nilai yang diinput (yang valid) atau nilai default
            context = {
                "character": char_obj,
                "images": images,
                "all_characters_for_icons": icon_chars_data,
                "user_input_stats": user_input_stats, # Kirimkan dictionary yang sudah diproses
            }
            return render(request, 'landingpage/character_builder.html', context)


        # Simpan input pengguna dan nama karakter ke session untuk perbandingan selanjutnya
        request.session['user_input_stats'] = user_input_stats
        # PERBAIKAN: Simpan 'character_name' dari char_obj
        request.session['character_name_for_comparison'] = char_obj.character_name 

        # Redirect ke halaman penilaian (misalnya, 'build:compare_build')
        # URL ini harus dibuat di build/urls.py dan akan menerima nama karakter mentah
        return redirect('build:compare_build', character_name=character_name) # character_name adalah nama mentah dari URL

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
