# rules.py
from skfuzzy import control as ctrl
from .variables import (
    diff_small, diff_large, bonus_val_input, stat_quality,
    overall_performance_score, text_quality_output
)

# --- Aturan Fuzzy (Fuzzy Rules) untuk kualitas stat individual ---

# Aturan untuk diff_small (persentase: Energy Regen, Crit Rate, Crit Dmg)
rule_diff_small_sangat_kurang = ctrl.Rule(diff_small['sangat_kurang'], stat_quality['buruk'])
rule_diff_small_kurang = ctrl.Rule(diff_small['kurang'], stat_quality['buruk'])
rule_diff_small_netral = ctrl.Rule(diff_small['netral'], stat_quality['cukup'])
rule_diff_small_baik = ctrl.Rule(diff_small['baik'], stat_quality['sangat_baik'])
rule_diff_small_sangat_baik = ctrl.Rule(diff_small['sangat_baik'], stat_quality['sangat_baik'])

# Aturan untuk diff_large (flat: HP, ATK, DEF)
rule_diff_large_sangat_kurang = ctrl.Rule(diff_large['sangat_kurang'], stat_quality['buruk'])
rule_diff_large_kurang = ctrl.Rule(diff_large['kurang'], stat_quality['buruk'])
rule_diff_large_netral = ctrl.Rule(diff_large['netral'], stat_quality['cukup'])
rule_diff_large_baik = ctrl.Rule(diff_large['baik'], stat_quality['sangat_baik'])
rule_diff_large_sangat_baik = ctrl.Rule(diff_large['sangat_baik'], stat_quality['sangat_baik'])

# Aturan untuk bonus_val_input (DMG Bonus Spesifik)
rule_bonus_rendah = ctrl.Rule(bonus_val_input['rendah'], stat_quality['buruk'])
rule_bonus_sedang = ctrl.Rule(bonus_val_input['sedang'], stat_quality['cukup'])
rule_bonus_tinggi = ctrl.Rule(bonus_val_input['tinggi'], stat_quality['sangat_baik'])


# --- Sistem Kontrol Fuzzy (Fuzzy Control System) dan Simulasi untuk stat individual ---

# Sistem untuk stat persentase (diff_small)
diff_stat_percent_ctrl = ctrl.ControlSystem([
    rule_diff_small_sangat_kurang,
    rule_diff_small_kurang,
    rule_diff_small_netral,
    rule_diff_small_baik,
    rule_diff_small_sangat_baik
])
diff_stat_percent_simulation = ctrl.ControlSystemSimulation(diff_stat_percent_ctrl)

# Sistem untuk stat flat (diff_large)
diff_stat_flat_ctrl = ctrl.ControlSystem([
    rule_diff_large_sangat_kurang,
    rule_diff_large_kurang,
    rule_diff_large_netral,
    rule_diff_large_baik,
    rule_diff_large_sangat_baik
])
diff_stat_flat_simulation = ctrl.ControlSystemSimulation(diff_stat_flat_ctrl)

# Sistem untuk bonus_val_input (DMG Bonus Spesifik)
bonus_stat_ctrl = ctrl.ControlSystem([
    rule_bonus_rendah,
    rule_bonus_sedang,
    rule_bonus_tinggi
])
bonus_stat_simulation = ctrl.ControlSystemSimulation(bonus_stat_ctrl)


# --- Aturan Fuzzy untuk Penilaian Teks Kualitas Build Keseluruhan ---
rule_overall_1 = ctrl.Rule(overall_performance_score['poor_build'], text_quality_output['low'])
rule_overall_2 = ctrl.Rule(overall_performance_score['average_build'], text_quality_output['medium'])
rule_overall_3 = ctrl.Rule(overall_performance_score['excellent_build'], text_quality_output['high'])

# --- Sistem Kontrol Fuzzy dan Simulasi untuk Penilaian Teks Kualitas Build Keseluruhan ---
overall_text_quality_ctrl = ctrl.ControlSystem([rule_overall_1, rule_overall_2, rule_overall_3])
overall_text_quality_sim = ctrl.ControlSystemSimulation(overall_text_quality_ctrl)