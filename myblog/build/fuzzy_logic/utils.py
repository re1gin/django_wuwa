# build/fuzzy_logic/utils.py

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

def get_interpolated_color(user_val_vs_ideal_percent):
    """
    Menentukan warna berdasarkan persentase user_val terhadap ideal_val,
    dengan interpolasi di antara titik-titik warna yang ditentukan.
    """
    # Warna dasar dalam format HEX
    COLOR_WHITE = '#FFFFFF'
    COLOR_BLUE = '#007BFF'   # Biru
    COLOR_GREEN = '#28A745'  # Hijau (ideal)
    COLOR_GOLD = '#FFD700'   # Emas (150%)
    COLOR_RED = '#DC3545'    # Merah (200%)

    # Konversi ke RGB untuk interpolasi
    WHITE_RGB = hex_to_rgb(COLOR_WHITE)
    BLUE_RGB = hex_to_rgb(COLOR_BLUE)
    GREEN_RGB = hex_to_rgb(COLOR_GREEN)
    GOLD_RGB = hex_to_rgb(COLOR_GOLD)
    RED_RGB = hex_to_rgb(COLOR_RED)

    # Definisikan titik-titik persentase dan warnanya
    # (Persentase, RGB_Color)
    color_points = [
        (0, WHITE_RGB),      # Jika 0% atau kurang dari 1% (nilai yang sangat rendah)
        (1, WHITE_RGB),      # 1% dari ideal -> Putih
        (50, BLUE_RGB),      # 50% dari ideal -> Biru
        (100, GREEN_RGB),    # 100% dari ideal -> Hijau (ideal)
        (150, GOLD_RGB),     # 150% dari ideal -> Emas
        (200, RED_RGB),      # 200% dari ideal -> Merah
        (float('inf'), RED_RGB) # Lebih dari 200% -> Merah
    ]

    # Pastikan persentase berada dalam rentang yang masuk akal
    percent = max(0, min(user_val_vs_ideal_percent, 200)) # Batasi dari 0% hingga 200%

    # Cari dua titik warna di antara persentase saat ini
    lower_point = color_points[0]
    upper_point = color_points[0]

    for i in range(len(color_points) - 1):
        if color_points[i][0] <= percent <= color_points[i+1][0]:
            lower_point = color_points[i]
            upper_point = color_points[i+1]
            break
        elif percent > color_points[len(color_points)-2][0]: # Jika lebih dari titik terakhir yang didefinisikan
            lower_point = color_points[len(color_points)-2]
            upper_point = color_points[len(color_points)-1]
            break # pastikan tidak keluar dari range color_points index

    # Jika percent tepat di salah satu titik
    if percent == lower_point[0]:
        return rgb_to_hex(lower_point[1])
    if percent == upper_point[0]:
        return rgb_to_hex(upper_point[1])

    # Interpolasi jika berada di antara dua titik
    range_percent = upper_point[0] - lower_point[0]
    if range_percent == 0: # Hindari pembagian oleh nol jika poinnya sama
        return rgb_to_hex(lower_point[1])

    factor = (percent - lower_point[0]) / range_percent
    interpolated_rgb = interpolate_color(lower_point[1], upper_point[1], factor)
    
    return rgb_to_hex(interpolated_rgb)


# Fungsi format_comparison_difference mungkin tidak lagi diperlukan jika Anda menampilkan
# nilai user dan ideal secara langsung dengan warna.
# Jika Anda masih ingin selisih juga ditampilkan, Anda bisa mempertahankannya
# tetapi mungkin tidak lagi memerlukan `color_class` di dalamnya,
# karena warna akan ditentukan di `views.py` dan langsung diteruskan.

def format_comparison_difference(db_val, session_val, label, is_percentage=False):
    """
    Memformat selisih antara nilai stat ideal (DB) dan input user (sesi) untuk ditampilkan di UI.
    """
    # Pastikan session_val adalah float untuk operasi aritmatika
    session_val_float = float(session_val) if isinstance(session_val, (int, float, str)) else 0.0
    diff = db_val - session_val_float
    symbol = ''
    if diff > 0:
        symbol = '&#9650;' # Panah atas
        diff_str = f"+{diff:.1f}" if not is_percentage else f"+{diff:.1f}%"
    elif diff < 0:
        symbol = '&#9660;' # Panah bawah
        diff_str = f"{diff:.1f}" if not is_percentage else f"{diff:.1f}%"
    else:
        symbol = '&#x2713;' # Tanda centang
        diff_str = "Equal"

    # Membersihkan label untuk tampilan unit, memastikan '%' ditambahkan jika diperlukan
    label_unit = label.replace(' DMG', '').replace('Lib.', 'Liberation').replace('Regen', 'Regeneration').strip()
    if is_percentage and not label_unit.endswith('%'):
        label_unit += '%'
    return {'label': label, 'value': diff_str, 'symbol': symbol, 'label_unit': label_unit}

# Anda bisa menambahkan fungsi helper lain di sini di masa mendatang
# Contoh:
# def clamp(value, min_value, max_value):
#     return max(min_value, min(value, max_value))