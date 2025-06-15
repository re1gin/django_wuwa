import math

def calculate_defense_multiplier(char_level, enemy_def, def_shred=0):
    """
    Menghitung defense multiplier berdasarkan level karakter, defense musuh, dan defense shred.
    Asumsi: Level musuh sama dengan level karakter untuk perhitungan dasar.
    """
    
    # Efektif defense setelah defense shred
    effective_enemy_def = enemy_def * (1 - def_shred)
    
    defense_multiplier = (char_level + 100) / ((effective_enemy_def) + (char_level + 100))
    return defense_multiplier

def calculate_damage_formula(base_attack, skill_multiplier, crit_rate, crit_damage, def_multiplier, res_multiplier, damage_bonus, crit_rate_buff=0, crit_damage_buff=0):
    """
    Menghitung damage rata-rata yang diberikan oleh satu serangan.
    """
    
    # Total crit rate dan crit damage setelah buff
    final_crit_rate = min(1.0, crit_rate + crit_rate_buff) # Crit rate maks 100%
    final_crit_damage = crit_damage + crit_damage_buff

    # Damage tanpa crit
    non_crit_damage = base_attack * skill_multiplier * (1 + damage_bonus) * def_multiplier * res_multiplier
    
    # Damage dengan crit
    crit_total_damage = non_crit_damage * (1 + final_crit_damage)

    # Damage rata-rata mempertimbangkan kemungkinan crit
    average_damage = (non_crit_damage * (1 - final_crit_rate)) + (crit_total_damage * final_crit_rate)
    
    return average_damage