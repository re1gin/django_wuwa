
# Normalisasi faktor untuk Radar Chart
HP_NORM = 50000.0
ATK_NORM = 4000.0
DEF_NORM = 4000.0
ENERGY_NORM = 300.0
CRIT_RATE_NORM = 100.0
CRIT_DMG_NORM = 350.0

MAX_BONUS_DMG_PERCENT = {
    'basic_atk_dmg_bonus': 50.0,
    'heavy_atk_dmg_bonus': 50.0,
    'resonance_skill_dmg_bonus': 50.0,
    'resonance_lib_dmg_bonus': 50.0,
    'attribute_dmg_bonus': 80.0,
    'healing_bonus': 80.0,
}

RESONATOR_RATING_WEIGHTS = {
    'level': 0.1,
    'status': 0.4,
    'weapon': 0.2,
    'echo': 0.2,
    'skill': 0.1,
}

STAT_WEIGHTS_FOR_AVERAGE = {
    'hp': 1.0,
    'attack': 1.0,
    'defense': 1.0,
    'energy_regen': 1.0, # Sesuaikan nama field di IdealBuild/user_input_stats
    'critical_rate': 1.0,
    'critical_damage': 1.0,
    'basic_atk_dmg_bonus': 1.0,
    'heavy_atk_dmg_bonus': 1.0,
    'resonance_skill_dmg_bonus': 1.0,
    'resonance_lib_dmg_bonus': 1.0,
    'attribute_dmg_bonus': 1.0,
    'healing_bonus': 1.0,
}

DEFAULT_SKILL_LEVEL = {
    'character_level': 90,
    'weapon_level': 90,
    'skill_level': 10,
}