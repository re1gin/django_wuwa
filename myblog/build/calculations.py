# build/calculations.py
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Import models
from resonators.models import ResonatorRecommendedWeapon, ResonatorRecommendedEcho
from build.models import Echo
# --- Inisialisasi Sistem Fuzzy Logic (Dilakukan sekali saat modul dimuat) ---
_fuzzy_stat_simulator = None

def _initialize_fuzzy_system():
    global _fuzzy_stat_simulator
    if _fuzzy_stat_simulator is not None:
        return _fuzzy_stat_simulator # Return if already initialized

    # 1. Antecedents (Input Variables): Gap antara stat user dan stat ideal
    # Rentang ini sangat penting dan harus disesuaikan dengan skala stat di game Anda.
    # Contoh: -0.5 = user 50% lebih tinggi dari ideal, 0.5 = user 50% lebih rendah dari ideal
    crit_rate_gap = ctrl.Antecedent(np.arange(-0.5, 0.51, 0.01), 'crit_rate_gap')
    attack_gap = ctrl.Antecedent(np.arange(-0.5, 0.51, 0.01), 'attack_gap')
    energy_gap = ctrl.Antecedent(np.arange(-0.5, 0.51, 0.01), 'energy_gap')
    # Tambahkan antecedents untuk stat lain jika ingin difuzzykan

    # 2. Consequents (Output Variables): Prioritas rekomendasi (0-100)
    priority_crit_rate = ctrl.Consequent(np.arange(0, 101, 1), 'priority_crit_rate')
    priority_attack = ctrl.Consequent(np.arange(0, 101, 1), 'priority_attack')
    priority_energy = ctrl.Consequent(np.arange(0, 101, 1), 'priority_energy')
    
    overall_priority_recommendation = ctrl.Consequent(np.arange(0, 101, 1), 'overall_priority_recommendation')

    # --- Membership Functions (Fungsi Keanggotaan) ---
    # Bentuk (trimf, trapmf, gbellmf, sigmf) dan titiknya perlu disesuaikan.
    # Gap Stat:
    # Overcapped: User stat jauh di atas ideal
    # Good: User stat mendekati ideal
    # Low: User stat agak di bawah ideal
    # Very Low: User stat jauh di bawah ideal

    # Crit Rate Gap
    crit_rate_gap['overcapped'] = fuzz.trimf(crit_rate_gap.universe, [-0.5, -0.5, -0.15]) # -50% to -15% better
    crit_rate_gap['good'] = fuzz.trimf(crit_rate_gap.universe, [-0.2, 0, 0.2])        # -20% to +20% from ideal
    crit_rate_gap['low'] = fuzz.trimf(crit_rate_gap.universe, [0.1, 0.3, 0.5])         # +10% to +50% from ideal (means user is low)
    crit_rate_gap['very_low'] = fuzz.trimf(crit_rate_gap.universe, [0.3, 0.5, 0.5])     # +30% to +50% from ideal (means user is very low)

    # Attack Gap
    attack_gap['overcapped'] = fuzz.trimf(attack_gap.universe, [-0.5, -0.5, -0.15])
    attack_gap['good'] = fuzz.trimf(attack_gap.universe, [-0.2, 0, 0.2])
    attack_gap['low'] = fuzz.trimf(attack_gap.universe, [0.1, 0.3, 0.5])
    attack_gap['very_low'] = fuzz.trimf(attack_gap.universe, [0.3, 0.5, 0.5])
    
    # Energy Gap
    energy_gap['overcapped'] = fuzz.trimf(energy_gap.universe, [-0.5, -0.5, -0.1])
    energy_gap['good'] = fuzz.trimf(energy_gap.universe, [-0.15, 0, 0.15])
    energy_gap['low'] = fuzz.trimf(energy_gap.universe, [0.05, 0.25, 0.45])
    energy_gap['very_low'] = fuzz.trimf(energy_gap.universe, [0.3, 0.5, 0.5])

    # Output Priorities (0-100)
    for p in [priority_crit_rate, priority_attack, priority_energy, overall_priority_recommendation]:
        p['none'] = fuzz.trimf(p.universe, [0, 0, 20])
        p['low'] = fuzz.trimf(p.universe, [10, 30, 50])
        p['medium'] = fuzz.trimf(p.universe, [40, 60, 80])
        p['high'] = fuzz.trimf(p.universe, [70, 90, 100])

    # --- Fuzzy Rules ---
    rules = []

    # Rules for Crit Rate Priority
    rules.append(ctrl.Rule(crit_rate_gap['very_low'], priority_crit_rate['high']))
    rules.append(ctrl.Rule(crit_rate_gap['low'], priority_crit_rate['medium']))
    rules.append(ctrl.Rule(crit_rate_gap['good'], priority_crit_rate['low']))
    rules.append(ctrl.Rule(crit_rate_gap['overcapped'], priority_crit_rate['none']))

    # Rules for Attack Priority
    rules.append(ctrl.Rule(attack_gap['very_low'], priority_attack['high']))
    rules.append(ctrl.Rule(attack_gap['low'], priority_attack['medium']))
    rules.append(ctrl.Rule(attack_gap['good'], priority_attack['low']))
    rules.append(ctrl.Rule(attack_gap['overcapped'], priority_attack['none']))
    
    # Rules for Energy Priority
    rules.append(ctrl.Rule(energy_gap['very_low'], priority_energy['high']))
    rules.append(ctrl.Rule(energy_gap['low'], priority_energy['medium']))
    rules.append(ctrl.Rule(energy_gap['good'], priority_energy['low']))
    rules.append(ctrl.Rule(energy_gap['overcapped'], priority_energy['none']))

    # Rules for Overall Priority Recommendation (combining individual priorities)
    # These rules are critical for determining the primary focus.
    rules.append(ctrl.Rule(
        (priority_crit_rate['high'] | priority_attack['high'] | priority_energy['high']),
        overall_priority_recommendation['high']
    ))
    rules.append(ctrl.Rule(
        (priority_crit_rate['medium'] | priority_attack['medium'] | priority_energy['medium']) &
        (priority_crit_rate['low'] | priority_attack['low'] | priority_energy['low']),
        overall_priority_recommendation['medium']
    ))
    rules.append(ctrl.Rule(
        priority_crit_rate['none'] & priority_attack['none'] & priority_energy['none'],
        overall_priority_recommendation['none']
    ))
    # Add more complex rules as needed, e.g., if crit is good but atk is very low, prioritize atk.
    # Example:
    rules.append(ctrl.Rule(
        crit_rate_gap['good'] & attack_gap['very_low'],
        overall_priority_recommendation['high']
    ))
    rules.append(ctrl.Rule(
        crit_rate_gap['low'] & attack_gap['good'],
        overall_priority_recommendation['medium']
    ))


    # 4. Control System
    stat_recommendation_ctrl = ctrl.ControlSystem(rules)
    _fuzzy_stat_simulator = ctrl.ControlSystemSimulation(stat_recommendation_ctrl)
    
    return _fuzzy_stat_simulator

# Inisialisasi sistem fuzzy saat modul dimuat pertama kali
_initialize_fuzzy_system()


def calculate_character_stats(input_data):
    """
    (Opsional) Fungsi ini bisa digunakan untuk menghitung total stat
    berdasarkan input_data, termasuk stat dari Weapon, Echo, Sonata.
    Ini penting jika Anda ingin menampilkan total stat aktual yang dihitung,
    bukan hanya input stat mentah.

    Ini adalah placeholder. Logika perhitungan akan sangat bergantung pada game Anda.
    """
    # Contoh sederhana:
    total_hp = input_data.get('hp', 0)
    total_attack = input_data.get('attack', 0)
    total_defense = input_data.get('defense', 0)
    total_energy = input_data.get('energy', 0)
    total_crit_rate = input_data.get('crit_rate', 0)
    total_crit_dmg = input_data.get('crit_dmg', 0)

    # Anda akan menambahkan logika di sini untuk:
    # 1. Mendapatkan base stats dari Resonator
    # 2. Mendapatkan stats dari Selected Weapon
    # 3. Mendapatkan stats dari Selected Echoes (main stats, substats)
    # 4. Mendapatkan stats dari Selected Sonata
    # 5. Menjumlahkan semuanya dan menerapkan perhitungan persentase/bonus
    
    # Untuk demo ini, kita hanya mengembalikan input mentah.
    # Anda harus mengganti ini dengan logika perhitungan yang sebenarnya.
    return {
        'total_hp': total_hp,
        'total_attack': total_attack,
        'total_defense': total_defense,
        'total_energy': total_energy,
        'total_crit_rate': total_crit_rate,
        'total_crit_dmg': total_crit_dmg,
        # ... dan stat lainnya
    }

def compare_stats(user_stats, ideal_build):
    """
    Membandingkan stat pengguna dengan stat ideal menggunakan fuzzy logic (untuk stat)
    dan logika crisp (untuk item) lalu menghasilkan rekomendasi.
    """
    recommendations_list = [] # List untuk rekomendasi stat tekstual
    
    # --- 1. Perhitungan Gap Stat untuk Fuzzy Logic ---
    # Hanya fokus pada stat yang akan difuzzykan
    # Penting: Pastikan ideal_build.stat tidak nol untuk menghindari DivisionByZeroError
    crit_rate_gap_val = (user_stats.get('crit_rate', 0) - ideal_build.crit_rate) / ideal_build.crit_rate if ideal_build.crit_rate else 0
    attack_gap_val = (user_stats.get('attack', 0) - ideal_build.attack) / ideal_build.attack if ideal_build.attack else 0
    energy_gap_val = (user_stats.get('energy', 0) - ideal_build.energy) / ideal_build.energy if ideal_build.energy else 0
    
    # Clamp the gap values to the universe of discourse defined in fuzzy system (-0.5 to 0.5)
    crit_rate_gap_val = np.clip(crit_rate_gap_val, -0.5, 0.5)
    attack_gap_val = np.clip(attack_gap_val, -0.5, 0.5)
    energy_gap_val = np.clip(energy_gap_val, -0.5, 0.5)

    # --- 2. Inferensi Fuzzy (Stat Recommendations) ---
    try:
        _fuzzy_stat_simulator.input['crit_rate_gap'] = crit_rate_gap_val
        _fuzzy_stat_simulator.input['attack_gap'] = attack_gap_val
        _fuzzy_stat_simulator.input['energy_gap'] = energy_gap_val
        
        _fuzzy_stat_simulator.compute()

        priority_crit_rate_val = _fuzzy_stat_simulator.output['priority_crit_rate']
        priority_attack_val = _fuzzy_stat_simulator.output['priority_attack']
        priority_energy_val = _fuzzy_stat_simulator.output['priority_energy']
        overall_priority_val = _fuzzy_stat_simulator.output['overall_priority_recommendation']

    except ValueError as e:
        # Tangani kasus di mana input berada di luar universe, atau masalah komputasi lain
        print(f"Fuzzy logic computation error: {e}")
        # Berikan nilai default atau tangani sesuai kebutuhan aplikasi Anda
        priority_crit_rate_val = 0
        priority_attack_val = 0
        priority_energy_val = 0
        overall_priority_val = 0
        recommendations_list.append("Kesalahan dalam perhitungan stat. Pastikan data stat lengkap.")
    
    # --- 3. Menerjemahkan Output Fuzzy ke Rekomendasi Teks ---
    # Rekomendasi umum berdasarkan 'overall_priority_val'
    if overall_priority_val > 80:
        recommendations_list.append("Build Anda membutuhkan perbaikan signifikan pada stat prioritas!")
    elif overall_priority_val > 60:
        recommendations_list.append("Build Anda cukup baik, tetapi ada area yang bisa ditingkatkan secara optimal.")
    elif overall_priority_val > 40:
        recommendations_list.append("Build Anda sudah solid, perbaikan kecil akan membuatnya lebih efisien.")
    elif overall_priority_val > 10:
        recommendations_list.append("Build Anda hampir sempurna. Fokus pada penyempurnaan substat!")
    else:
        recommendations_list.append("Selamat! Build Anda sudah sangat optimal dan seimbang.")

    # Rekomendasi spesifik berdasarkan prioritas individual
    if priority_crit_rate_val > 70:
        recommendations_list.append(f"Fokus utama: Tingkatkan Critical Rate! Target Anda sekitar {ideal_build.crit_rate:.2f}% CR.")
    elif priority_crit_rate_val > 40:
        recommendations_list.append(f"Pertimbangkan untuk sedikit meningkatkan Critical Rate. Idealnya sekitar {ideal_build.crit_rate:.2f}% CR.")

    if priority_attack_val > 70:
        recommendations_list.append(f"Fokus utama: Tingkatkan Attack! Target Anda sekitar {ideal_build.attack:.2f} ATK.")
    elif priority_attack_val > 40:
        recommendations_list.append(f"Pertimbangkan untuk sedikit meningkatkan Attack. Idealnya sekitar {ideal_build.attack:.2f} ATK.")
        
    if priority_energy_val > 70:
        recommendations_list.append(f"Fokus utama: Tingkatkan Energy Regen Anda! Target Anda sekitar {ideal_build.energy:.2f}% ER.")
    elif priority_energy_val > 40:
        recommendations_list.append(f"Pertimbangkan untuk sedikit meningkatkan Energy Regen. Idealnya sekitar {ideal_build.energy:.2f}% ER.")
        
    # Menentukan stat prioritas tunggal untuk highlight
    stat_priorities = {
        "Critical Rate": priority_crit_rate_val,
        "Attack": priority_attack_val,
        "Energy Regeneration": priority_energy_val,
    }
    priority_stat_name = max(stat_priorities, key=stat_priorities.get)
    if stat_priorities[priority_stat_name] < 20: # Jika semua prioritas sangat rendah, berarti sudah seimbang
        priority_stat_name = "Well Balanced"


    # --- 4. Rekomendasi Item (Masih Menggunakan Logika Crisp) ---
    item_recommendations = {
        'weapons': [],
        'echos': [],
        'sonatas': [],
    }

    # Rekomendasi Weapon
    user_selected_weapon_name = user_stats.get('selected_weapon')
    recommended_weapons_for_char = ResonatorRecommendedWeapon.objects.filter(resonator=ideal_build.character).order_by('priority_level')
    
    user_weapon_is_recommended = False
    if user_selected_weapon_name:
        for rec_weapon in recommended_weapons_for_char:
            if rec_weapon.weapon.weapon_name == user_selected_weapon_name:
                user_weapon_is_recommended = True
                item_recommendations['weapons'].append(f"Senjata Anda ({user_selected_weapon_name}) adalah rekomendasi tingkat {rec_weapon.priority_level} ({rec_weapon.get_priority_level_display()}).")
                break
        if not user_weapon_is_recommended:
            item_recommendations['weapons'].append(f"Senjata Anda ({user_selected_weapon_name}) tidak termasuk dalam daftar rekomendasi utama untuk {ideal_build.character.name}. Pertimbangkan opsi berikut:")
    else:
        item_recommendations['weapons'].append("Anda belum memilih senjata. Pertimbangkan:")
        
    for rec_weapon in recommended_weapons_for_char:
        if rec_weapon.weapon.weapon_name != user_selected_weapon_name: # Jangan tampilkan lagi senjata yang sudah dipakai
            item_recommendations['weapons'].append(f"- {rec_weapon.weapon.weapon_name} (Priority: {rec_weapon.get_priority_level_display()}) - {rec_weapon.notes}")
    if not recommended_weapons_for_char.exists():
        item_recommendations['weapons'].append(f"Belum ada rekomendasi senjata spesifik untuk {ideal_build.character.name}.")


    # Rekomendasi Echo
    user_selected_echo_name = user_stats.get('selected_echo')
    recommended_echos_for_char = ResonatorRecommendedEcho.objects.filter(resonator=ideal_build.character).order_by('priority_level')

    user_echo_is_recommended = False
    if user_selected_echo_name:
        for rec_echo in recommended_echos_for_char:
            if rec_echo.echo.name == user_selected_echo_name:
                user_echo_is_recommended = True
                item_recommendations['echos'].append(f"Set Echo Anda ({user_selected_echo_name}) adalah rekomendasi tingkat {rec_echo.priority_level} ({rec_echo.get_priority_level_display()}).")
                break
        if not user_echo_is_recommended:
            item_recommendations['echos'].append(f"Set Echo Anda ({user_selected_echo_name}) tidak termasuk dalam daftar rekomendasi utama untuk {ideal_build.character.name}. Pertimbangkan opsi berikut:")
    else:
        item_recommendations['echos'].append("Anda belum memilih Echo. Pertimbangkan:")

    for rec_echo in recommended_echos_for_char:
        if rec_echo.echo.name != user_selected_echo_name:
            item_recommendations['echos'].append(f"- {rec_echo.echo.name} (Priority: {rec_echo.get_priority_level_display()}) - {rec_echo.notes}")
    if not recommended_echos_for_char.exists():
        item_recommendations['echos'].append(f"Belum ada rekomendasi Echo spesifik untuk {ideal_build.character.name}.")


    # Rekomendasi Sonata (disesuaikan berdasarkan Echo yang sedang dipakai/direkomendasikan)
    user_selected_sonata_name = user_stats.get('selected_sonata')
    
    target_echo_for_sonata_rec = None
    if user_selected_echo_name:
        target_echo_for_sonata_rec = Echo.objects.filter(name=user_selected_echo_name).first()
    elif recommended_echos_for_char.exists():
        target_echo_for_sonata_rec = recommended_echos_for_char.first().echo # Ambil Echo rekomendasi terbaik

    if target_echo_for_sonata_rec:
        compatible_sonatas = target_echo_for_sonata_rec.sonatas.all().order_by('name')
        
        user_sonata_is_compatible = False
        if user_selected_sonata_name:
            if compatible_sonatas.filter(name=user_selected_sonata_name).exists():
                user_sonata_is_compatible = True
                item_recommendations['sonatas'].append(f"Sonata Anda ({user_selected_sonata_name}) kompatibel dengan Echo ({target_echo_for_sonata_rec.name}).")
            else:
                 item_recommendations['sonatas'].append(f"Sonata Anda ({user_selected_sonata_name}) TIDAK kompatibel dengan Echo ({target_echo_for_sonata_rec.name}). Pertimbangkan Sonata yang kompatibel:")
        
        if not user_selected_sonata_name:
            item_recommendations['sonatas'].append(f"Anda belum memilih Sonata untuk Echo {target_echo_for_sonata_rec.name}. Pertimbangkan:")
        elif user_selected_sonata_name and user_sonata_is_compatible:
            item_recommendations['sonatas'].append(f"Sonata yang kompatibel lainnya dengan Echo {target_echo_for_sonata_rec.name}:")

        if compatible_sonatas.exists():
            for comp_sonata in compatible_sonatas:
                if comp_sonata.name != user_selected_sonata_name:
                    item_recommendations['sonatas'].append(f"- {comp_sonata.name}")
        else:
            item_recommendations['sonatas'].append(f"Tidak ada Sonata kompatibel yang didefinisikan untuk Echo '{target_echo_for_sonata_rec.name}'.")
    else:
        item_recommendations['sonatas'].append("Pilih Echo terlebih dahulu untuk mendapatkan rekomendasi Sonata.")

    return {
        'recommendations': recommendations_list, # List rekomendasi stat dari fuzzy logic
        'item_recommendations': item_recommendations, # Dict rekomendasi item (crisp)
        'priority_stat': priority_stat_name, # Stat prioritas dari fuzzy logic
        'overall_priority_val': overall_priority_val # Nilai prioritas keseluruhan dari fuzzy logic
    }