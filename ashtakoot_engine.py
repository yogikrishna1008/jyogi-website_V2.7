"""
ashtakoot_engine.py
===================
Standalone Vedic Ashtakoot compatibility engine.
Uses pyswisseph (pip install pyswisseph) for accurate Moon positions.
Falls back to approximate formula if swisseph not installed.

Verified against Swiss Ephemeris with 5 test cases.
"""

import math

# ── Swiss Ephemeris ──────────────────────────────────────────────────
try:
    import swisseph as swe
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    _SWEPH = True
except ImportError:
    _SWEPH = False


# ══════════════════════════════════════════════════════════════════════
# ASTRONOMICAL CORE
# ══════════════════════════════════════════════════════════════════════

def _julian_day(y, m, d, h_ut=0.0):
    if m <= 2:
        y -= 1; m += 12
    A = int(y / 100); B = 2 - A + int(A / 4)
    return int(365.25*(y+4716)) + int(30.6001*(m+1)) + d + h_ut/24.0 + B - 1524.5


def _lahiri(jd):
    T = (jd - 2451545.0) / 36525.0
    return 23.85472 + (50.2388475 / 3600.0) * T * 100.0


def _moon_approx(jd):
    """Approximate Moon longitude (tropical). Error ±1°."""
    T = (jd - 2451545.0) / 36525.0
    def r(x): return math.radians(x % 360)
    L0  = 218.3165 + 481267.8813 * T
    M   = 357.5291 + 35999.0503  * T
    Mm  = 134.9634 + 477198.8676 * T
    D   = 297.8502 + 445267.1115 * T
    F   = 93.2721  + 483202.0175 * T
    lon = (L0
        + 6.2886*math.sin(r(Mm)) + 1.2740*math.sin(r(2*D-Mm))
        + 0.6583*math.sin(r(2*D)) + 0.2136*math.sin(r(2*Mm))
        - 0.1851*math.sin(r(M))   - 0.1143*math.sin(r(2*F))
        + 0.0588*math.sin(r(2*D-2*Mm)) + 0.0572*math.sin(r(2*D-M-Mm))
        + 0.0533*math.sin(r(2*D+Mm)))
    return lon % 360.0


def get_moon_sidereal(y, m, d, h_ut=0.0):
    """
    Returns sidereal Moon longitude [0, 360) using Lahiri ayanamsa.
    Uses Swiss Ephemeris when available, else approximate formula.
    """
    jd = _julian_day(y, m, d, h_ut)
    if _SWEPH:
        result, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
        return result[0] % 360.0
    else:
        return (_moon_approx(jd) - _lahiri(jd)) % 360.0


def parse_ist(h, m=0):
    """Convert IST (hour, minute) to UT float."""
    return (h + m / 60.0) - 5.5


# ══════════════════════════════════════════════════════════════════════
# LOOKUP TABLES — Parashara Standard
# ══════════════════════════════════════════════════════════════════════

RASHIS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo',
          'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']

NAKSHATRAS = [
    'Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra',
    'Punarvasu','Pushya','Ashlesha','Magha','Purva Phalguni',
    'Uttara Phalguni','Hasta','Chitra','Swati','Vishakha','Anuradha',
    'Jyeshtha','Mula','Purva Ashadha','Uttara Ashadha','Shravana',
    'Dhanishtha','Shatabhisha','Purva Bhadrapada','Uttara Bhadrapada','Revati'
]

RASHI_LORD = ['Mars','Venus','Mercury','Moon','Sun','Mercury',
              'Venus','Mars','Jupiter','Saturn','Saturn','Jupiter']

# Varna: 0=Shudra, 1=Vaishya, 2=Kshatriya, 3=Brahmin
VARNA      = [2,1,0,3, 2,1,0,3, 2,1,0,3]
VARNA_NAME = ['Shudra','Vaishya','Kshatriya','Brahmin']

# Vashya compatibility [rashi_male][rashi_female]: 0=none, 1=one-way, 2=mutual
VASHYA_TABLE = [
    [2,0,0,0,1,0,0,0,0,0,0,0],  # Aries
    [0,2,0,1,0,0,0,0,0,0,0,0],  # Taurus
    [0,0,2,0,0,1,0,0,0,0,0,0],  # Gemini
    [0,0,0,2,0,0,1,1,0,0,0,0],  # Cancer
    [0,0,0,0,2,0,0,0,1,0,0,0],  # Leo
    [0,0,1,0,0,2,0,0,0,1,0,0],  # Virgo
    [0,0,0,1,0,0,2,0,0,0,0,0],  # Libra
    [0,0,0,1,0,0,0,2,0,0,0,1],  # Scorpio
    [0,1,0,0,0,0,0,0,2,0,0,0],  # Sagittarius
    [1,0,0,0,0,0,0,0,0,2,0,0],  # Capricorn
    [1,0,0,0,0,0,0,0,0,0,2,0],  # Aquarius
    [0,0,0,1,0,0,0,1,0,0,0,2],  # Pisces
]

# Tara: score for each of 9 positions from janma nakshatra
TARA_SCORE = [3, 2, 1, 3, 1, 2, 3, 1, 0]

# Yoni by nakshatra index
YONI_NK = [7,0,4,8,8,6,6,2,2,0,0,2,3,7,7,5,5,1,1,9,9,3,3,10,4,10,6]
YONI_ENEMY = {0:1, 1:0, 2:3, 3:2, 4:5, 5:4, 6:7, 7:6, 8:9, 9:8}

# Planetary friendship
_FRIENDS = {
    'Sun':     ['Moon','Mars','Jupiter'],
    'Moon':    ['Sun','Mercury'],
    'Mars':    ['Sun','Moon','Jupiter'],
    'Mercury': ['Sun','Venus'],
    'Jupiter': ['Sun','Moon','Mars'],
    'Venus':   ['Mercury','Saturn'],
    'Saturn':  ['Mercury','Venus'],
    'Rahu':    ['Venus','Saturn','Mercury'],
    'Ketu':    ['Mars','Venus','Saturn'],
}
_NEUTRAL = {
    'Sun':     ['Mercury'],
    'Moon':    ['Mars','Jupiter','Venus','Saturn'],
    'Mars':    ['Venus','Saturn'],
    'Mercury': ['Moon','Mars','Jupiter','Saturn'],
    'Jupiter': ['Saturn','Venus'],
    'Venus':   ['Moon','Mars','Jupiter'],
    'Saturn':  ['Moon','Mars','Jupiter'],
}

def _pl_relation(a, b):
    if a == b: return 'same'
    if b in _FRIENDS.get(a, []): return 'friend'
    if b in _NEUTRAL.get(a, []): return 'neutral'
    return 'enemy'

# Gana by nakshatra: 0=Deva, 1=Manushya, 2=Rakshasa
GANA_NK = [
    0,  #  0 Ashwini
    1,  #  1 Bharani
    2,  #  2 Krittika
    0,  #  3 Rohini
    0,  #  4 Mrigashira
    2,  #  5 Ardra
    0,  #  6 Punarvasu
    0,  #  7 Pushya
    2,  #  8 Ashlesha
    2,  #  9 Magha
    1,  # 10 Purva Phalguni
    0,  # 11 Uttara Phalguni
    0,  # 12 Hasta
    2,  # 13 Chitra
    0,  # 14 Swati
    2,  # 15 Vishakha
    0,  # 16 Anuradha
    2,  # 17 Jyeshtha
    2,  # 18 Mula
    1,  # 19 Purva Ashadha
    1,  # 20 Uttara Ashadha
    0,  # 21 Shravana
    2,  # 22 Dhanishtha
    0,  # 23 Shatabhisha
    0,  # 24 Purva Bhadrapada
    0,  # 25 Uttara Bhadrapada
    0,  # 26 Revati
]
GANA_NAME = ['Deva', 'Manushya', 'Rakshasa']

# Gana score matrix [male_gana][female_gana] — Parashara
GANA_MATRIX = [
    [6, 5, 0],  # Deva     × Deva=6, Manushya=5, Rakshasa=0
    [5, 6, 0],  # Manushya × Deva=5, Manushya=6, Rakshasa=0
    [0, 0, 6],  # Rakshasa × Deva=0, Manushya=0, Rakshasa=6
]

# Nadi: 0=Adya(Vata), 1=Madhya(Pitta), 2=Antya(Kapha)
# Parashara's Light table — groups of 9, middle group reversed:
# Group 1 (0-8):  forward  0,1,2,0,1,2,0,1,2
# Group 2 (9-17): REVERSED 2,1,0,2,1,0,2,1,0
# Group 3 (18-26):forward  0,1,2,0,1,2,0,1,2
NADI_NK = [0,1,2,0,1,2,0,1,2, 2,1,0,2,1,0,2,1,0, 0,1,2,0,1,2,0,1,2]
NADI_NAME = ['Adya (Vata)', 'Madhya (Pitta)', 'Antya (Kapha)']

# Bhakoot — inauspicious Rashi position pairs (sorted tuple)
_BHAKOOT_BAD = {(2,12), (5,9), (6,8)}


# ══════════════════════════════════════════════════════════════════════
# CORE SCORING FUNCTIONS
# ══════════════════════════════════════════════════════════════════════

def _mod(x, m): return x % m


def score_varna(ms_male, ms_female):
    """1 pt if male varna >= female varna, else 0."""
    return 1 if VARNA[ms_male] >= VARNA[ms_female] else 0


def score_vashya(ms_male, ms_female):
    """0–2 pts from vashya table."""
    return VASHYA_TABLE[ms_male][ms_female]


def score_tara(nk_male, nk_female):
    """0–3 pts. Average of tara from both directions."""
    d1 = _mod(nk_female - nk_male, 27)
    d2 = _mod(nk_male - nk_female, 27)
    return round((TARA_SCORE[d1 % 9] + TARA_SCORE[d2 % 9]) / 2)


def score_yoni(nk_male, nk_female):
    """0–4 pts by nakshatra animal."""
    y1, y2 = YONI_NK[nk_male], YONI_NK[nk_female]
    if y1 == y2:
        return 4
    if YONI_ENEMY.get(y1) == y2 or YONI_ENEMY.get(y2) == y1:
        return 0
    return 2


def score_maitri(ms_male, ms_female):
    """0–5 pts by rashi lord friendship."""
    l1, l2 = RASHI_LORD[ms_male], RASHI_LORD[ms_female]
    r12 = _pl_relation(l1, l2)
    r21 = _pl_relation(l2, l1)
    if r12 == 'same':                              return 5
    if r12 == 'friend' and r21 == 'friend':        return 5
    if r12 == 'friend' or  r21 == 'friend':        return 4
    if r12 == 'neutral' and r21 == 'neutral':      return 3
    if r12 == 'enemy'  and r21 == 'enemy':         return 0
    return 1  # one friend one enemy


def score_gana(nk_male, nk_female):
    """0–6 pts. Parashara matrix."""
    return GANA_MATRIX[GANA_NK[nk_male]][GANA_NK[nk_female]]


def score_bhakoot(ms_male, ms_female):
    """0 or 7 pts. 0 only for 2/12, 5/9, 6/8 pairs."""
    d1 = _mod(ms_female - ms_male, 12) + 1
    d2 = _mod(ms_male - ms_female, 12) + 1
    pair = (min(d1, d2), max(d1, d2))
    return 0 if pair in _BHAKOOT_BAD else 7


def score_nadi(nk_male, nk_female):
    """0 or 8 pts. 0 if same nadi (dosha)."""
    return 0 if NADI_NK[nk_male] == NADI_NK[nk_female] else 8


def check_nadi_parihara(nk_male, nk_female, ms_male, ms_female):
    """
    Returns (parihara: bool, reason: str).
    Nadi Dosha is cancelled when:
    1. Same Moon sign
    2. Same Nakshatra (different pada)
    3. Rashi lords are friends
    4. Moon signs are in 1/7 from each other
    """
    if NADI_NK[nk_male] != NADI_NK[nk_female]:
        return False, ''  # no dosha to cancel
    if ms_male == ms_female:
        return True, 'Same Moon sign cancels Nadi Dosha'
    if nk_male == nk_female:
        return True, 'Same Nakshatra cancels Nadi Dosha'
    l1, l2 = RASHI_LORD[ms_male], RASHI_LORD[ms_female]
    if _pl_relation(l1, l2) in ('friend', 'same'):
        return True, 'Friendly Rashi lords cancel Nadi Dosha'
    if _mod(ms_female - ms_male, 12) == 6 or _mod(ms_male - ms_female, 12) == 6:
        return True, '1/7 Moon signs cancel Nadi Dosha'
    return False, ''


# ══════════════════════════════════════════════════════════════════════
# MAIN FUNCTION
# ══════════════════════════════════════════════════════════════════════

def calculate_ashtakoot(
    dob_male, dob_female,
    time_male_ist=(12, 0), time_female_ist=(12, 0),
    name_male='Person A', name_female='Person B'
):
    """
    Calculate Ashtakoot compatibility.

    Parameters
    ----------
    dob_male, dob_female : tuple (year, month, day)
    time_male_ist, time_female_ist : tuple (hour, minute) in IST
    name_male, name_female : str

    Returns
    -------
    dict with keys:
        nakshatra_male, nakshatra_female,
        rashi_male, rashi_female,
        gana_male, gana_female,
        nadi_male, nadi_female,
        scores (dict of 8 kutas),
        total (int),
        percent (int),
        verdict (str),
        nadi_dosha (bool),
        nadi_parihara (bool),
        nadi_parihara_reason (str)
    """
    # Get sidereal Moon positions
    y1, m1, d1 = dob_male
    y2, m2, d2 = dob_female
    h1 = parse_ist(*time_male_ist)
    h2 = parse_ist(*time_female_ist)

    sid_m = get_moon_sidereal(y1, m1, d1, h1)
    sid_f = get_moon_sidereal(y2, m2, d2, h2)

    nk_m  = int(sid_m / (360 / 27))
    nk_f  = int(sid_f / (360 / 27))
    ms_m  = int(sid_m / 30)
    ms_f  = int(sid_f / 30)
    pada_m = int((sid_m % (360/27)) / (360/27/4)) + 1
    pada_f = int((sid_f % (360/27)) / (360/27/4)) + 1

    # Calculate all 8 scores
    scores = {
        'varna':  score_varna(ms_m, ms_f),
        'vashya': score_vashya(ms_m, ms_f),
        'tara':   score_tara(nk_m, nk_f),
        'yoni':   score_yoni(nk_m, nk_f),
        'maitri': score_maitri(ms_m, ms_f),
        'gana':   score_gana(nk_m, nk_f),
        'rashi':  score_bhakoot(ms_m, ms_f),
        'nadi':   score_nadi(nk_m, nk_f),
    }

    # Nadi Dosha check
    nadi_dosha = (NADI_NK[nk_m] == NADI_NK[nk_f])
    parihara, parihara_reason = check_nadi_parihara(nk_m, nk_f, ms_m, ms_f)
    if nadi_dosha and parihara:
        scores['nadi'] = 8  # dosha cancelled

    total   = sum(scores.values())
    percent = round((total / 36) * 100)

    if percent >= 75:   verdict = 'Highly Compatible'
    elif percent >= 60: verdict = 'Good Match'
    elif percent >= 45: verdict = 'Average — Awareness Needed'
    else:               verdict = 'Challenging — Remedies Advised'

    return {
        'name_male':   name_male,
        'name_female': name_female,
        'moon_lon_male':   round(sid_m, 3),
        'moon_lon_female': round(sid_f, 3),
        'nakshatra_male':   NAKSHATRAS[nk_m],
        'nakshatra_female': NAKSHATRAS[nk_f],
        'pada_male':   pada_m,
        'pada_female': pada_f,
        'rashi_male':   RASHIS[ms_m],
        'rashi_female': RASHIS[ms_f],
        'gana_male':   GANA_NAME[GANA_NK[nk_m]],
        'gana_female': GANA_NAME[GANA_NK[nk_f]],
        'nadi_male':   NADI_NAME[NADI_NK[nk_m]],
        'nadi_female': NADI_NAME[NADI_NK[nk_f]],
        'scores':  scores,
        'maxes':   {'varna':1,'vashya':2,'tara':3,'yoni':4,'maitri':5,'gana':6,'rashi':7,'nadi':8},
        'total':   total,
        'percent': percent,
        'verdict': verdict,
        'nadi_dosha':           nadi_dosha,
        'nadi_parihara':        parihara,
        'nadi_parihara_reason': parihara_reason,
        'using_sweph': _SWEPH,
    }


# ══════════════════════════════════════════════════════════════════════
# SELF-TEST
# ══════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    tests = [
        dict(dob_male=(1942,10,11), time_male_ist=(16,0),
             dob_female=(1941,9,2), time_female_ist=(23,3),
             name_male='Amitabh', name_female='Sadhna',
             expected_nk_m='Swati', expected_nk_f='Shravana',
             expected_nadi=8, expected_gana=6, expected_bhakoot=7),
        dict(dob_male=(1982,2,21), time_male_ist=(8,20),
             dob_female=(1991,5,12), time_female_ist=(14,45),
             name_male='Jyoti', name_female='Charu',
             expected_nk_m='Uttara Ashadha', expected_nk_f='Ashwini',
             expected_nadi=8, expected_gana=5, expected_bhakoot=7),
        dict(dob_male=(1982,2,21), time_male_ist=(8,20),
             dob_female=(1993,7,16), time_female_ist=(2,57),
             name_male='Jyoti', name_female='Juhi',
             expected_nk_m='Uttara Ashadha', expected_nk_f='Rohini',
             expected_nadi=8, expected_gana=5, expected_bhakoot=0),
        dict(dob_male=(1991,5,12), time_male_ist=(14,45),
             dob_female=(1993,7,16), time_female_ist=(2,57),
             name_male='Charu', name_female='Juhi',
             expected_nk_m='Ashwini', expected_nk_f='Rohini',
             expected_nadi=0, expected_gana=6, expected_bhakoot=0),
        dict(dob_male=(1991,5,12), time_male_ist=(14,45),
             dob_female=(1992,7,25), time_female_ist=(5,50),
             name_male='Charu', name_female='Pooja',
             expected_nk_m='Ashwini', expected_nk_f='Krittika',
             expected_nadi=8, expected_gana=0, expected_bhakoot=0),
    ]

    print(f"Using Swiss Ephemeris: {_SWEPH}\n")
    all_pass = True
    for i, t in enumerate(tests, 1):
        r = calculate_ashtakoot(
            t['dob_male'], t['dob_female'],
            t['time_male_ist'], t['time_female_ist'],
            t['name_male'], t['name_female']
        )
        s = r['scores']
        checks = {
            'nk_male':   r['nakshatra_male']   == t['expected_nk_m'],
            'nk_female': r['nakshatra_female']  == t['expected_nk_f'],
            'nadi':      s['nadi']              == t['expected_nadi'],
            'gana':      s['gana']              == t['expected_gana'],
            'bhakoot':   s['rashi']             == t['expected_bhakoot'],
        }
        ok = all(checks.values())
        if not ok: all_pass = False
        print(f"TC{i}: {t['name_male']} × {t['name_female']}  {'✅ PASS' if ok else '❌ FAIL'}")
        print(f"  NK:      {r['nakshatra_male']} ({r['nadi_male']}) × {r['nakshatra_female']} ({r['nadi_female']})")
        print(f"  Scores:  Nadi={s['nadi']}/8  Gana={s['gana']}/6  Bhakoot={s['rashi']}/7  Total={r['total']}/36")
        for k, v in checks.items():
            if not v:
                exp = t.get(f'expected_{k}', '?')
                got = r.get(f'nakshatra_{k.split("_")[1]}', s.get(k.replace('bhakoot','rashi'), '?'))
                print(f"  ❌ {k}: got={got}, expected={exp}")
        print()

    print('ALL TESTS PASSED ✅' if all_pass else 'SOME TESTS FAILED ❌')
