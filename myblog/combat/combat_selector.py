import importlib

# Kita impor CarlottaCombat secara eksplisit di sini agar bisa digunakan sebagai
# fallback yang andal jika combat handler untuk karakter lain belum dibuat.
from .resonator_combat.carlotta import CarlottaCombat

def get_combat_handler(char_name, character_data_file="characters_data.json"):
    """
    Secara dinamis mengimpor dan membuat instance combat handler untuk karakter tertentu.
    Ini bertindak sebagai "factory" yang memilih kelas yang tepat berdasarkan nama.

    Args:
        char_name (str): Nama karakter (misalnya, "Carlotta", "Jianxin").
        character_data_file (str): Path ke file data JSON.

    Returns:
        Sebuah instance dari kelas combat karakter, atau instance CarlottaCombat sebagai fallback.
    """
    try:
        # Konvensi penamaan:
        # Nama karakter "Jianxin" -> nama file "jianxin.py", nama kelas "JianxinCombat"
        module_path = f"combat.resonator_combat.{char_name.lower()}"
        class_name = f"{char_name}Combat"

        # 1. Mengimpor modul secara dinamis berdasarkan path
        char_module = importlib.import_module(module_path)

        # 2. Mendapatkan kelas dari modul yang sudah diimpor
        CombatClass = getattr(char_module, class_name)

        print(f"Berhasil memuat combat handler untuk: {char_name}")
        return CombatClass(character_data_file=character_data_file)

    except (ModuleNotFoundError, AttributeError):
        print(f"Peringatan: Combat handler untuk '{char_name}' tidak ditemukan.")
        print("Menggunakan logika combat Carlotta sebagai fallback karena hanya itu yang tersedia saat ini.")
        return CarlottaCombat(character_data_file=character_data_file)
    except Exception as e:
        print(f"Terjadi kesalahan tak terduga saat memuat combat handler untuk '{char_name}': {e}")
        return None