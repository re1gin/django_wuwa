# build/fuzzy_logic/utils.py

import math
from ..constants import MAX_BONUS_DMG_PERCENT # Pastikan ini diimpor dari lokasi yang benar relatif terhadap utils.py

def format_folder(name):
    """Mengubah nama menjadi format folder yang aman (lowercase, spasi diganti underscore)."""
    return name.replace(" ", "_").lower()

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb_color):
    return '#{:02x}{:02x}{:02x}'.format(int(rgb_color[0]), int(rgb_color[1]), int(rgb_color[2]))

def interpolate_color(color1_rgb, color2_rgb, factor):
    """Interpolasi antara dua warna RGB. Factor 0-1."""
    r = color1_rgb[0] + factor * (color2_rgb[0] - color1_rgb[0])
    g = color1_rgb[1] + factor * (color2_rgb[1] - color1_rgb[1])
    b = color1_rgb[2] + factor * (color2_rgb[2] - color1_rgb[2])
    return (r, g, b)

def get_interpolated_color(score):
    """
    Menentukan warna berdasarkan skor 0-100 (dari Fuzzy Logic).
    Ini adalah versi yang disederhanakan dari yang Anda berikan, fokus pada skor 0-100.
    Score 0 = Merah
    Score 50 = Kuning
    Score 100 = Hijau
    """
    if score < 0:
        score = 0
    elif score > 100:
        score = 100

    if score <= 50:
        # Interpolasi dari Merah ke Kuning
        r = 255
        g = int(255 * (score / 50))
        b = 0
    else:
        # Interpolasi dari Kuning ke Hijau
        r = int(255 * ((100 - score) / 50))
        g = 255
        b = 0

    return f"#{r:02x}{g:02x}{b:02x}"


def format_comparison_difference(ideal_val, user_val, stat_label, is_percentage=False, is_prioritized=False):
    """
    Membandingkan nilai pengguna dengan nilai ideal dan menghasilkan pesan saran.

    Args:
        ideal_val (float): Nilai ideal stat dari database.
        user_val (float): Nilai stat pengguna.
        stat_label (str): Nama stat (misal "HP", "Critical Rate").
        is_percentage (bool): True jika stat adalah persentase.
        is_prioritized (bool): True jika stat ini diprioritaskan untuk role karakter.

    Returns:
        str: Pesan saran deskriptif.
    """
    diff = user_val - ideal_val
    unit = "%" if is_percentage else ""
    formatted_ideal = f"{ideal_val:.1f}{unit}"
    formatted_user = f"{user_val:.1f}{unit}"

    # Untuk mempermudah perbandingan, kita akan mengubah persentase menjadi desimal untuk perhitungan
    # Namun, tetap tampilkan sebagai persentase di pesan akhir.
    # Hindari pembagian oleh nol jika ideal_val adalah 0
    ideal_for_calc = ideal_val / 100 if is_percentage else ideal_val
    user_for_calc = user_val / 100 if is_percentage else user_val

    # Thresholds untuk saran (sesuaikan sesuai kebutuhan Anda)
    VERY_LOW_THRESHOLD_PCT = 0.30  # Kurang dari 30% dari ideal
    LOW_THRESHOLD_PCT = 0.60     # Kurang dari 60% dari ideal
    SLIGHTLY_LOW_THRESHOLD_PCT = 0.90 # Kurang dari 90% dari ideal
    SLIGHTLY_HIGH_THRESHOLD_PCT = 1.10 # Lebih dari 110% dari ideal
    VERY_HIGH_THRESHOLD_PCT = 1.30   # Lebih dari 130% dari ideal

    # Khusus untuk stat bonus DMG, nama stat harus cocok dengan key di MAX_BONUS_DMG_PERCENT
    stat_key_for_bonus_max = stat_label.replace(' ', '_').lower()

    if is_prioritized:
        # Logika untuk stat yang diprioritaskan (biasanya stat DMG bonus untuk DPS)
        if user_val == 0:
            return f"Untuk {stat_label}, ini adalah stat **KRITIS** bagi {stat_label.replace(' Bonus', '')} karakter ini, tetapi Anda tidak memiliki nilai sama sekali (0%). Anda sangat perlu mencari stat ini!"
        
        # Penanganan kasus di mana ideal_val adalah 0 (karena tidak ada target spesifik, hanya 'semakin banyak semakin baik')
        if ideal_val == 0:
            max_val_for_bonus = MAX_BONUS_DMG_PERCENT.get(stat_key_for_bonus_max, 50.0) # Default 50 jika tidak ditemukan
            if user_val >= max_val_for_bonus * 0.95: # Di atas 95% dari 'maksimal sempurna'
                return f"Nilai {stat_label} Anda ({formatted_user}) sudah sangat optimal untuk karakter ini. Luar biasa!"
            elif user_val > max_val_for_bonus * 0.6:
                return f"Nilai {stat_label} Anda ({formatted_user}) sudah baik, namun masih bisa dioptimalkan lebih lanjut untuk meningkatkan potensi karakter."
            else:
                return f"Nilai {stat_label} Anda ({formatted_user}) masih terlalu rendah untuk stat prioritas ini. Anda perlu mencari lebih banyak lagi."
        
        # Penanganan kasus di mana ideal_val > 0 untuk stat yang diprioritaskan (jika ada target spesifik)
        elif ideal_val > 0:
            if user_for_calc < ideal_for_calc * VERY_LOW_THRESHOLD_PCT:
                return f"Nilai {stat_label} Anda ({formatted_user}) sangat rendah dibandingkan ideal ({formatted_ideal}). Perlu peningkatan drastis untuk performa maksimal."
            elif user_for_calc < ideal_for_calc * LOW_THRESHOLD_PCT:
                return f"Nilai {stat_label} Anda ({formatted_user}) masih rendah. Usahakan untuk mendapatkan lebih banyak lagi untuk mencapai potensi penuh."
            elif user_for_calc < ideal_for_calc * SLIGHTLY_LOW_THRESHOLD_PCT:
                return f"Nilai {stat_label} Anda ({formatted_user}) sedikit di bawah ideal ({formatted_ideal}). Sedikit peningkatan akan sangat membantu."
            elif user_val >= ideal_val:
                return f"Nilai {stat_label} Anda ({formatted_user}) sudah ideal atau sangat baik. Pertahankan!"

    else:
        # Logika untuk stat yang TIDAK diprioritaskan atau stat utama
        # Penanganan kasus ideal_val = 0 (stat tidak relevan)
        if ideal_val == 0:
            if user_val == 0:
                return f"Stat {stat_label} tidak terlalu relevan untuk karakter ini, dan Anda sudah mengelolanya dengan baik (nilai 0%)."
            else: # user_val > 0 meskipun idealnya 0
                return f"Stat {stat_label} Anda ({formatted_user}) tidak relevan untuk karakter ini. Alokasikan stat ini ke yang lebih bermanfaat."

        # Penanganan kasus ideal_val > 0 (stat relevan tapi mungkin bukan prioritas utama DMG)
        # Toleransi kecil untuk nilai yang hampir sama
        if abs(diff) < 0.1 and not is_percentage: # Untuk flat stats
            return f"Nilai {stat_label} Anda ({formatted_user}) sudah sangat mendekati nilai ideal ({formatted_ideal}). Baik!"
        elif is_percentage and abs(user_val - ideal_val) < 1.0: # Untuk persentase, toleransi 1%
            return f"Nilai {stat_label} Anda ({formatted_user}) sudah sangat mendekati nilai ideal ({formatted_ideal}). Baik!"

        if user_val > ideal_val:
            if user_for_calc > ideal_for_calc * VERY_HIGH_THRESHOLD_PCT:
                return f"Nilai {stat_label} Anda ({formatted_user}) **terlalu tinggi** dari ideal ({formatted_ideal}). Pertimbangkan mengalokasikan stat ini ke yang lebih relevan."
            elif user_for_calc > ideal_for_calc * SLIGHTLY_HIGH_THRESHOLD_PCT:
                return f"Nilai {stat_label} Anda ({formatted_user}) sedikit lebih tinggi dari ideal ({formatted_ideal}). Masih bagus, tapi bisa dioptimalkan."
            else: # Di atas ideal tapi tidak terlalu jauh
                return f"Nilai {stat_label} Anda ({formatted_user}) sudah melebihi nilai ideal ({formatted_ideal}). Bagus!"
        else: # user_val < ideal_val
            if user_for_calc < ideal_for_calc * VERY_LOW_THRESHOLD_PCT:
                return f"Nilai {stat_label} Anda ({formatted_user}) **sangat rendah** dibandingkan ideal ({formatted_ideal}). Ini perlu peningkatan drastis."
            elif user_for_calc < ideal_for_calc * LOW_THRESHOLD_PCT:
                return f"Nilai {stat_label} Anda ({formatted_user}) rendah dibandingkan ideal ({formatted_ideal}). Perlu ditingkatkan."
            elif user_for_calc < ideal_for_calc * SLIGHTLY_LOW_THRESHOLD_PCT:
                return f"Nilai {stat_label} Anda ({formatted_user}) sedikit di bawah ideal ({formatted_ideal}). Masih bisa ditingkatkan."
            else: # user_val mendekati ideal tapi sedikit di bawah
                return f"Nilai {stat_label} Anda ({formatted_user}) sudah cukup baik mendekati ideal ({formatted_ideal})."

    # Fallback jika tidak ada kondisi yang cocok (seharusnya tidak terjadi)
    return f"Saran untuk {stat_label} tidak tersedia (user: {formatted_user}, ideal: {formatted_ideal})."