# Pastikan file ini berada di dalam direktori `myblog/combat/`
# agar impor `combat_selector` berfungsi.

from combat_selector import get_combat_handler

def run_simulation_for_character(char_name):
    """
    Menjalankan simulasi damage untuk karakter yang diberikan menggunakan 
    combat handler yang sesuai yang didapat dari selector.
    """
    print(f"\n--- Memulai Simulasi untuk: {char_name} ---")
    
    # 1. Dapatkan combat handler yang sesuai menggunakan selector.
    #    Fungsi ini akan menangani semua logika pemilihan untuk Anda.
    combat_handler = get_combat_handler(char_name, character_data_file="characters_data.json")

    if not combat_handler:
        print(f"Tidak dapat melanjutkan simulasi, combat handler untuk '{char_name}' tidak dapat dimuat.")
        return

    # 2. Siapkan parameter simulasi (sama seperti sebelumnya)
    example_base_attack = 2000
    example_enemy_defense = 1000
    example_enemy_resistance_multiplier = 0.9

    # 3. Gunakan metode dari instance combat_handler yang dikembalikan.
    #    Tidak peduli objek apa yang dikembalikan (CarlottaCombat atau lainnya),
    #    Anda bisa memanggil metodenya dengan cara yang sama.
    dmg_skill = combat_handler.use_resonance_skill(
        "Art of Violence", 
        example_base_attack, 
        example_enemy_defense, 
        example_enemy_resistance_multiplier
    )
    print(f"Damage Resonance Skill: {dmg_skill:.2f}")
    print("-" * 30)


if __name__ == "__main__":
    # Jalankan simulasi untuk Carlotta.
    # Selector akan menemukan `carlotta.py` dan `CarlottaCombat`.
    run_simulation_for_character("Carlotta")

    # Jalankan simulasi untuk karakter yang belum ada (misal: Jianxin).
    # Selector akan gagal menemukan `jianxin.py`, lalu secara otomatis
    # menggunakan `CarlottaCombat` sebagai fallback, sesuai logika kita.
    run_simulation_for_character("Jianxin")