from django.shortcuts import render
from .combat_selector import get_combat_handler

def simulation_view(request):
    context = {}
    if request.method == 'POST':
        # Ambil data dari form yang di-submit
        char_name = request.POST.get('char_name')
        skill_name = request.POST.get('skill_name')
        
        # Simpan input pengguna untuk ditampilkan kembali di form
        context = {
            'char_name': char_name,
            'skill_name': skill_name,
            'base_attack': request.POST.get('base_attack'),
            'enemy_defense': request.POST.get('enemy_defense'),
            'enemy_res_multi': request.POST.get('enemy_res_multi'),
        }

        try:
            # Konversi input ke tipe data yang benar
            base_attack = float(request.POST.get('base_attack', 0))
            enemy_def = float(request.POST.get('enemy_defense', 0))
            enemy_res_multi = float(request.POST.get('enemy_res_multi', 1.0))

            # 1. Dapatkan combat handler yang sesuai menggunakan factory/selector
            combat_handler = get_combat_handler(char_name, character_data_file="characters_data.json")

            if not combat_handler:
                context['error'] = f"Gagal memuat combat handler untuk '{char_name}'."
                return render(request, 'combat/simulation.html', context)

            # 2. Gunakan metode `calculate_damage` yang generik
            #    Ini lebih fleksibel daripada memanggil `use_resonance_skill` secara spesifik.
            damage_result = combat_handler.calculate_damage(
                skill_name=skill_name,
                base_attack=base_attack,
                enemy_def=enemy_def,
                enemy_res_multi=enemy_res_multi
            )

            # 3. Tambahkan hasil ke context untuk ditampilkan di template
            context['result'] = damage_result

        except ValueError:
            context['error'] = "Pastikan semua input numerik diisi dengan angka yang valid."
        except Exception as e:
            context['error'] = f"Terjadi kesalahan: {e}"

    return render(request, 'combat/simulation.html', context)