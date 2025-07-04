# damager/views.py

from django.shortcuts import render, get_object_or_404
from resonators.models import Resonator
from .models import Skill, SkillMultiplier
import logging

logger = logging.getLogger(__name__)

# Nilai default untuk skill level jika tidak ada di sesi
DEFAULT_SKILL_LEVEL = {
    'character_level': 90, # Contoh default
    'weapon_level': 90,    # Contoh default
}

def character_damage_view(request, name): # Mengganti character_slug menjadi name
    """
    View untuk menghitung dan menampilkan damage karakter tertentu,
    mengambil statistik pengguna dari sesi dan data combat dari database.
    """
    # Mengambil objek Resonator dari database berdasarkan nama (dikonversi ke lowercase)
    # Asumsi model Resonator memiliki field 'name' yang unik dan Anda akan mencocokkan dengan lowercase
    resonator = get_object_or_404(Resonator, name__iexact=name)

    # Mengambil semua multiplier untuk resonator ini dari database
    all_multipliers = SkillMultiplier.objects.filter(skill__resonator=resonator).select_related('skill')

    # Mengambil semua deskripsi skill untuk resonator ini
    combat_descriptions = {skill.name: skill.description for skill in resonator.combat_skills.all()}

    # Mengambil user_input_stats dari sesi.
    user_input_stats = request.session.get('user_input_stats', {
        'hp': 0.0, 'attack': 0.0, 'defense': 0.0, 'energy': 0.0, 'crit_rate': 0.0, 'crit_dmg': 0.0,
        'basic_atk_dmg_bonus': 0.0, 'heavy_atk_dmg_bonus': 0.0,
        'resonance_skill_dmg_bonus': 0.0, 'resonance_lib_dmg_bonus': 0.0,
        'attribute_dmg_bonus': 0.0,
        'healing_bonus': 0.0,
        'character_level': DEFAULT_SKILL_LEVEL['character_level'],
        'weapon_level': DEFAULT_SKILL_LEVEL['weapon_level'],
        'selected_weapon': '',
        'selected_echo': '',
        'selected_sonata': '',
    })

    # Mengambil statistik yang relevan dari user_input_stats
    base_atk = user_input_stats.get('attack', 0.0)
    crit_rate = user_input_stats.get('crit_rate', 0.0) / 100.0
    crit_dmg = user_input_stats.get('crit_dmg', 0.0) / 100.0
    attribute_dmg_bonus = user_input_stats.get('attribute_dmg_bonus', 0.0) / 100.0

    basic_atk_dmg_bonus = user_input_stats.get('basic_atk_dmg_bonus', 0.0) / 100.0
    heavy_atk_dmg_bonus = user_input_stats.get('heavy_atk_dmg_bonus', 0.0) / 100.0
    resonance_skill_dmg_bonus = user_input_stats.get('resonance_skill_dmg_bonus', 0.0) / 100.0
    resonance_lib_dmg_bonus = user_input_stats.get('resonance_lib_dmg_bonus', 0.0) / 100.0

    # Dictionary untuk menyimpan hasil perhitungan damage
    calculated_damage = {}

    # Melakukan perhitungan damage untuk setiap multiplier yang ditemukan
    for multiplier in all_multipliers:
        attack_name = multiplier.attack_name
        multiplier_value = multiplier.multiplier_value
        attack_type = multiplier.attack_type
        skill_type_category = multiplier.skill.skill_type_category # Ambil kategori skill

        # Menentukan bonus damage berdasarkan jenis serangan
        total_dmg_bonus = attribute_dmg_bonus

        if attack_type == "basic":
            total_dmg_bonus += basic_atk_dmg_bonus
        elif attack_type == "heavy":
            total_dmg_bonus += heavy_atk_dmg_bonus
        elif attack_type == "skill":
            total_dmg_bonus += resonance_skill_dmg_bonus
        elif attack_type == "liberation":
            total_dmg_bonus += resonance_lib_dmg_bonus

        # Perhitungan damage dasar (tanpa crit)
        non_crit_damage = base_atk * (multiplier_value / 100) * (1 + total_dmg_bonus)

        # Perhitungan damage kritikal
        crit_damage = non_crit_damage * (1 + crit_dmg)

        calculated_damage[attack_name] = {
            "attack_name": attack_name,  # ⬅️ Tambahkan ini!
            "non_crit": round(non_crit_damage, 2),
            "crit": round(crit_damage, 2),
            "skill_name": multiplier.skill.name,
            "skill_type_category": skill_type_category
        }

    # Konteks yang akan dilewatkan ke template
    context = {
        'character_name': resonator.name,
        'attribute_type': resonator.attribute.name if resonator.attribute else 'Unknown',
        'user_stats': user_input_stats,
        'damage_data': calculated_damage,
        'combat_description': combat_descriptions,
        'damage_chart_data': { # Siapkan data untuk grafik
            'basic_attack': [],
            'resonance_skill': [],
            'resonance_liberation': [],
            'heavy_attack': [],
            'dodge_counter': [],
            'mid_air_attack': [],
        }
    }

    # Kelompokkan data damage berdasarkan kategori skill untuk grafik
    for attack_name, data in calculated_damage.items():
        category = data['skill_type_category']
        # Normalisasi kategori untuk mencocokkan kunci kamus
        normalized_category = category.lower().replace(' ', '_')

        if normalized_category in context['damage_chart_data']:
            context['damage_chart_data'][normalized_category].append(data)
        else:
            # Opsional: log kategori yang tidak cocok jika ada
            logger.warning(f"Peringatan: Kategori skill '{category}' tidak cocok dengan kunci grafik yang ditentukan.")
    
    import json
    print("=== DEBUG DATA ===")
    print(json.dumps(context['damage_chart_data'], indent=2))

    return render(request, 'landingpage/character_damage.html', context)
