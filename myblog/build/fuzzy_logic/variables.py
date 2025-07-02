# variables.py
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# --- Variabel Input (Antecedents) untuk kualitas stat individual ---
# Selisih untuk stat persentase (e.g., Crit Rate, Crit Dmg, Energy Regen)
diff_small = ctrl.Antecedent(np.arange(-100, 101, 1), 'selisih_kecil')
# Selisih untuk stat flat besar (e.g., HP, ATK, DEF)
diff_large = ctrl.Antecedent(np.arange(-5000, 5001, 1), 'selisih_besar')
# Nilai absolut bonus DMG/Healing (0-100%, sesuaikan rentang jika perlu)
bonus_val_input = ctrl.Antecedent(np.arange(0, 101, 1), 'bonus_nilai_input')

# --- Variabel Output (Consequent) untuk kualitas stat individual ---
stat_quality = ctrl.Consequent(np.arange(0, 101, 1), 'kualitas_stat')

# --- Fungsi Keanggotaan (Membership Functions) untuk Variabel Input Stat Individual ---
diff_small['sangat_kurang'] = fuzz.trimf(diff_small.universe, [-100, -100, -20])
diff_small['kurang'] = fuzz.trimf(diff_small.universe, [-25, -10, 0])
diff_small['netral'] = fuzz.trimf(diff_small.universe, [-5, 0, 5])
diff_small['baik'] = fuzz.trimf(diff_small.universe, [0, 10, 25])
diff_small['sangat_baik'] = fuzz.trimf(diff_small.universe, [20, 100, 100])

diff_large['sangat_kurang'] = fuzz.trimf(diff_large.universe, [-5000, -5000, -500])
diff_large['kurang'] = fuzz.trimf(diff_large.universe, [-1000, -200, 0])
diff_large['netral'] = fuzz.trimf(diff_large.universe, [-100, 0, 100])
diff_large['baik'] = fuzz.trimf(diff_large.universe, [0, 200, 1000])
diff_large['sangat_baik'] = fuzz.trimf(diff_large.universe, [500, 5000, 5000])

bonus_val_input['rendah'] = fuzz.trimf(bonus_val_input.universe, [0, 0, 20])
bonus_val_input['sedang'] = fuzz.trimf(bonus_val_input.universe, [15, 35, 55])
bonus_val_input['tinggi'] = fuzz.trimf(bonus_val_input.universe, [50, 100, 100])

# --- Fungsi Keanggotaan (Membership Functions) untuk Variabel Output Stat Individual ---
stat_quality['buruk'] = fuzz.trimf(stat_quality.universe, [0, 0, 30])
stat_quality['cukup'] = fuzz.trimf(stat_quality.universe, [20, 50, 80])
stat_quality['sangat_baik'] = fuzz.trimf(stat_quality.universe, [70, 100, 100])


# --- Variabel Fuzzy untuk Penilaian Teks Kualitas Build Keseluruhan ---
# Input: overall_performance_score (skor numerik 0-100 dari rating build)
overall_performance_score = ctrl.Antecedent(np.arange(0, 101, 1), 'overall_performance_score')

# Output: text_quality_output (nilai numerik yang akan diconvert ke teks)
text_quality_output = ctrl.Consequent(np.arange(0, 101, 1), 'text_quality_output')

# --- Fungsi Keanggotaan untuk Penilaian Teks Kualitas Build Keseluruhan ---
overall_performance_score['poor_build'] = fuzz.trimf(overall_performance_score.universe, [0, 0, 40])
overall_performance_score['average_build'] = fuzz.trimf(overall_performance_score.universe, [30, 60, 90])
overall_performance_score['excellent_build'] = fuzz.trimf(overall_performance_score.universe, [70, 100, 100])

text_quality_output['low'] = fuzz.trimf(text_quality_output.universe, [0, 0, 30])
text_quality_output['medium'] = fuzz.trimf(text_quality_output.universe, [20, 50, 80])
text_quality_output['high'] = fuzz.trimf(text_quality_output.universe, [70, 100, 100])