
# Normalisasi faktor untuk Radar Chart
HP_NORM = 50000.0
ATK_NORM = 4000.0
DEF_NORM = 4000.0
ENERGY_NORM = 300.0
CRIT_RATE_NORM = 100.0
CRIT_DMG_NORM = 350.0

# Bobot untuk komponen rating Resonator keseluruhan
RESONATOR_RATING_WEIGHTS = {
    'level': 0.1,
    'status': 0.4,
    'weapon': 0.2,
    'echo': 0.2,
    'skill': 0.1
}

# Field level skill yang akan diperiksa dan nama tampilannya
SKILL_LEVEL_FIELDS = {
    'basic_atk_level': 'Basic ATK',
    'resonance_skill_level': 'Resonance Skill',
    'forte_circuit_level': 'Forte Circuit',
    'resonance_liberation_level': 'Resonance Liberation',
    'intro_skill_level': 'Intro Skill',
}

# Level skill default jika tidak ditemukan (digunakan di getattr)
DEFAULT_SKILL_LEVEL = 10