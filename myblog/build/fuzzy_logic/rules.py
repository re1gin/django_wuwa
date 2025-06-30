from skfuzzy import control as ctrl
from .variables import (
    diff_small, diff_large, bonus_val_input, stat_quality,
    overall_performance_score, text_quality_output
)

# --- Aturan Fuzzy (Fuzzy Rules) untuk kualitas stat individual ---
rule_diff_1 = ctrl.Rule(diff_small['sangat_kurang'] | diff_large['sangat_kurang'], stat_quality['buruk'])
rule_diff_2 = ctrl.Rule(diff_small['kurang'] | diff_large['kurang'], stat_quality['buruk'])
rule_diff_3 = ctrl.Rule(diff_small['netral'] | diff_large['netral'], stat_quality['cukup'])
rule_diff_4 = ctrl.Rule(diff_small['baik'] | diff_large['baik'], stat_quality['sangat_baik'])
rule_diff_5 = ctrl.Rule(diff_small['sangat_baik'] | diff_large['sangat_baik'], stat_quality['sangat_baik'])

rule_bonus_1 = ctrl.Rule(bonus_val_input['rendah'], stat_quality['buruk'])
rule_bonus_2 = ctrl.Rule(bonus_val_input['sedang'], stat_quality['cukup'])
rule_bonus_3 = ctrl.Rule(bonus_val_input['tinggi'], stat_quality['sangat_baik'])

# --- Sistem Kontrol Fuzzy (Fuzzy Control System) dan Simulasi untuk stat individual ---
diff_stat_ctrl = ctrl.ControlSystem([rule_diff_1, rule_diff_2, rule_diff_3, rule_diff_4, rule_diff_5])
diff_stat_simulation = ctrl.ControlSystemSimulation(diff_stat_ctrl)

bonus_stat_ctrl = ctrl.ControlSystem([rule_bonus_1, rule_bonus_2, rule_bonus_3])
bonus_stat_simulation = ctrl.ControlSystemSimulation(bonus_stat_ctrl)


# --- Aturan Fuzzy untuk Penilaian Teks Kualitas Build Keseluruhan ---
rule_overall_1 = ctrl.Rule(overall_performance_score['poor_build'], text_quality_output['low'])
rule_overall_2 = ctrl.Rule(overall_performance_score['average_build'], text_quality_output['medium'])
rule_overall_3 = ctrl.Rule(overall_performance_score['excellent_build'], text_quality_output['high'])

# --- Sistem Kontrol Fuzzy dan Simulasi untuk Penilaian Teks Kualitas Build Keseluruhan ---
overall_text_quality_ctrl = ctrl.ControlSystem([rule_overall_1, rule_overall_2, rule_overall_3])
overall_text_quality_sim = ctrl.ControlSystemSimulation(overall_text_quality_ctrl)