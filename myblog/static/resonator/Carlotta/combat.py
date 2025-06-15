import json
from combat_utils import calculate_damage_formula, calculate_defense_multiplier

class CarlottaCombat:
    def __init__(self, character_data_file="characters_data.json"):
        self.char_name = "Carlotta"
        
        # Memuat data karakter dari file JSON
        try:
            with open(character_data_file, 'r') as f:
                data = json.load(f)
                self.char_data = data.get(self.char_name)
                if not self.char_data:
                    raise ValueError(f"Character '{self.char_name}' not found in {character_data_file}")
        except FileNotFoundError:
            raise FileNotFoundError(f"'{character_data_file}' not found. Please ensure the JSON file exists.")
        except json.JSONDecodeError:
            raise ValueError(f"Error decoding JSON from '{character_data_file}'. Check file format.")
        
        # Inisialisasi atribut dari data JSON Carlotta
        self.skill_data = self.char_data.get("damage_data", {})
        
        self.crit_rate = self.char_data.get("crit_rate", 0.05)
        self.crit_damage = self.char_data.get("crit_damage", 1.50)
        
        # Default ke 0.0 jika null atau tidak ada
        self.glacio_damage_bonus = self.char_data.get("glacio_damage_bonus", 0.0) or 0.0 
        self.final_attack = self.char_data.get("final_attack") # Bisa None atau nilai spesifik

        # Asumsi level karakter, bisa diubah jika perlu
        self.char_level = 90 
        
        # Carlotta's unique mechanics/buffs (example)
        # Ini adalah tempat Anda akan menambahkan status atau buff Carlotta yang dinamis
        self.forte_gauge = 0 
        self.forte_max = 100 # Contoh
        
        print(f"{self.char_name} Combat instance created. Default skill level implicitly 10.")

    def calculate_damage(self, skill_name, base_attack, enemy_def, enemy_res_multi, def_shred=0, is_resonance_skill_dmg=False, buffs=None):
        """
        Menghitung damage rata-rata untuk skill tertentu Carlotta.
        Karena data JSON sudah implicitly level 10, kita hanya mengambil 'percentage'.
        """
        if buffs is None:
            buffs = {}

        skill_info = self.skill_data.get(skill_name)
        if not skill_info:
            print(f"Warning: Skill '{skill_name}' not found for Carlotta. Returning 0 damage.")
            return 0

        # Mengambil percentage langsung dari skill_info
        percentages = skill_info.get("percentage") 
        hits = skill_info.get("hits", 1) # Default hits 1 jika tidak ditentukan

        # Pastikan percentages adalah list agar bisa diiterasi, bahkan jika hanya satu nilai
        if not isinstance(percentages, list):
            percentages = [percentages]

        total_damage = 0
        for percentage in percentages:
            # Mengambil defense shred spesifik skill jika ada, override def_shred umum jika diset
            # Karena di JSON baru ini tidak ada def_shred per skill, ini akan selalu 0 dari parameter fungsi
            
            damage = calculate_damage_formula(
                base_attack=base_attack,
                skill_multiplier=percentage,
                crit_rate=self.crit_rate,
                crit_damage=self.crit_damage,
                def_multiplier=calculate_defense_multiplier(self.char_level, enemy_def, def_shred),
                res_multiplier=enemy_res_multi,
                damage_bonus=(self.glacio_damage_bonus + buffs.get("glacio_damage_bonus", 0)),
                crit_rate_buff=buffs.get("crit_rate", 0),
                crit_damage_buff=buffs.get("crit_damage", 0)
            )
            total_damage += damage

        return total_damage

    def perform_basic_attack(self, stage, base_attack, enemy_def, enemy_res_multi, buffs=None):
        """Mengeksekusi serangan dasar Carlotta berdasarkan stage."""
        if stage == 1:
            skill_name = "Basic Attack Stage 1"
        elif stage == 2:
            skill_name = "Basic Attack Stage 2"
        # Tambahkan stage lain jika diperlukan
        else:
            print(f"Invalid Basic Attack Stage: {stage}")
            return 0
        
        return self.calculate_damage(skill_name, base_attack, enemy_def, enemy_res_multi, buffs=buffs)

    def perform_heavy_attack(self, attack_type, base_attack, enemy_def, enemy_res_multi, buffs=None):
        """Mengeksekusi serangan berat Carlotta."""
        if attack_type == "Phase 1":
            skill_name = "Heavy Attack Phase 1"
        elif attack_type == "Phase 2":
            skill_name = "Heavy Attack Phase 2"
        elif attack_type == "Phase 3":
            skill_name = "Heavy Attack Phase 3"
        elif attack_type == "Imminent Oblivion":
            skill_name = "Heavy Attack Imminent Oblivion"
        elif attack_type == "Containment Tactics":
            skill_name = "Containment Tactics" # Ini penggabungan dari Phase 1-3
        else:
            print(f"Invalid Heavy Attack Type: {attack_type}")
            return 0
        return self.calculate_damage(skill_name, base_attack, enemy_def, enemy_res_multi, buffs=buffs)

    def use_resonance_skill(self, skill_variant, base_attack, enemy_def, enemy_res_multi, buffs=None):
        """Mengeksekusi Resonance Skill Carlotta."""
        if skill_variant == "Art of Violence":
            skill_name = "Resonance Skill Art of Violence"
        elif skill_variant == "Chromatic Splendor":
            skill_name = "Resonance Skill Chromatic Splendor"
        else:
            print(f"Invalid Resonance Skill variant: {skill_variant}")
            return 0
        return self.calculate_damage(skill_name, base_attack, enemy_def, enemy_res_multi, buffs=buffs)

    def use_resonance_liberation(self, skill_variant, base_attack, enemy_def, enemy_res_multi, buffs=None):
        """Mengeksekusi Resonance Liberation Carlotta."""
        def_shred_lib = 0.18 # Default def shred untuk Liberation
        if skill_variant == "Era of New Wave":
            skill_name = "Resonance Liberation Skill DMG"
        elif skill_variant == "Death Knell Base": # Ini Death Knell bagian base hit
            skill_name = "Death Knell Base"
        elif skill_variant == "Death Knell Crystal Shard": # Ini Death Knell bagian crystal shard
            skill_name = "Death Knell Crystal Shard"
        elif skill_variant == "Fatal Finale":
            skill_name = "Fatal Finale"
        else:
            print(f"Invalid Resonance Liberation variant: {skill_variant}")
            return 0
        
        return self.calculate_damage(skill_name, base_attack, enemy_def, enemy_res_multi, def_shred=def_shred_lib, is_resonance_skill_dmg=True, buffs=buffs)
    
    def use_intro_skill(self, base_attack, enemy_def, enemy_res_multi, buffs=None):
        """Mengeksekusi Intro Skill Carlotta."""
        def_shred_intro = 0.18 # Default def shred untuk Intro Skill
        skill_name = "Intro Skill Wintertime Aria"
        return self.calculate_damage(skill_name, base_attack, enemy_def, enemy_res_multi, def_shred=def_shred_intro, buffs=buffs)

    def use_outro_skill(self, base_attack, enemy_def, enemy_res_multi, buffs=None):
        """Mengeksekusi Outro Skill Carlotta."""
        skill_name = "Outro Skill Closing Remark"
        return self.calculate_damage(skill_name, base_attack, enemy_def, enemy_res_multi, buffs=buffs)
        
    # Anda bisa menambahkan lebih banyak fungsi untuk interaksi skill Carlotta di sini
    # Contoh: mengelola Forte Gauge, Transformed State, dll.
    
# Contoh Penggunaan:
if __name__ == "__main__":
    # Inisialisasi Carlotta Combat
    try:
        carlotta = CarlottaCombat()
    except (FileNotFoundError, ValueError) as e:
        print(f"Failed to initialize CarlottaCombat: {e}")
        exit()

    # Contoh parameter musuh dan stat Carlotta (ini harus disesuaikan dengan build Anda)
    example_base_attack = 2000 # Contoh total Attack Carlotta
    example_enemy_defense = 1000 # Contoh Defense musuh
    example_enemy_resistance_multiplier = 0.9 # Contoh resistance musuh terhadap Glacio (e.g., 10% resist)

    print("\n--- Carlotta Damage Simulation (Level 10 Skills) ---")

    # Simulasi Basic Attack Stage 1
    dmg_ba1 = carlotta.perform_basic_attack(1, example_base_attack, example_enemy_defense, example_enemy_resistance_multiplier)
    print(f"Basic Attack Stage 1 Damage: {dmg_ba1:.2f}")

    # Simulasi Basic Attack Stage 2 (multi-hit)
    dmg_ba2 = carlotta.perform_basic_attack(2, example_base_attack, example_enemy_defense, example_enemy_resistance_multiplier)
    print(f"Basic Attack Stage 2 Total Damage (3 hits): {dmg_ba2:.2f}")

    # Simulasi Resonance Skill
    dmg_skill = carlotta.use_resonance_skill("Art of Violence", example_base_attack, example_enemy_defense, example_enemy_resistance_multiplier)
    print(f"Resonance Skill (Art of Violence) Damage: {dmg_skill:.2f}")

    # Simulasi Resonance Liberation (Era of New Wave)
    dmg_lib = carlotta.use_resonance_liberation("Era of New Wave", example_base_attack, example_enemy_defense, example_enemy_resistance_multiplier)
    print(f"Resonance Liberation (Era of New Wave) Damage: {dmg_lib:.2f}")
    
    # Simulasi Resonance Liberation (Death Knell Base)
    dmg_dk_base = carlotta.use_resonance_liberation("Death Knell Base", example_base_attack, example_enemy_defense, example_enemy_resistance_multiplier)
    print(f"Resonance Liberation (Death Knell Base) Damage: {dmg_dk_base:.2f}")

    # Simulasi Resonance Liberation (Death Knell Crystal Shard)
    dmg_dk_shard = carlotta.use_resonance_liberation("Death Knell Crystal Shard", example_base_attack, example_enemy_defense, example_enemy_resistance_multiplier)
    print(f"Resonance Liberation (Death Knell Crystal Shard) Total Damage (4 hits): {dmg_dk_shard:.2f}")

    # Simulasi Resonance Liberation (Fatal Finale)
    dmg_ff = carlotta.use_resonance_liberation("Fatal Finale", example_base_attack, example_enemy_defense, example_enemy_resistance_multiplier)
    print(f"Resonance Liberation (Fatal Finale) Damage: {dmg_ff:.2f}")
    
    # Simulasi Intro Skill
    dmg_intro = carlotta.use_intro_skill(example_base_attack, example_enemy_defense, example_enemy_resistance_multiplier)
    print(f"Intro Skill Wintertime Aria Total Damage (3 hits): {dmg_intro:.2f}")

    # Contoh dengan buff sementara
    buffs_example = {
        "glacio_damage_bonus": 0.20, # Contoh 20% bonus Glacio DMG
        "crit_rate": 0.15          # Contoh 15% bonus Crit Rate
    }
    dmg_skill_buffed = carlotta.use_resonance_skill("Chromatic Splendor", example_base_attack, example_enemy_defense, example_enemy_resistance_multiplier, buffs=buffs_example)
    print(f"Resonance Skill (Chromatic Splendor) Buffed Damage: {dmg_skill_buffed:.2f}")