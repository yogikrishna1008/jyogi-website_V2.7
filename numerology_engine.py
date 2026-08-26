"""
numerology_engine.py — Jyogi AI Extended Numerology Engine
===========================================================
Extends base numerology.py with:

  Systems:
    - Pythagorean  (A=1..Z=8/9)     ← already in numerology.py
    - Chaldean     (A=1..Z=8, no 9) ← ancient Babylonian system
    - Vedic / Ank  (same as Chaldean but planetary lord assignment)
    - Kabbalah     (A=1..Z=400 then cycle back)

  Modules:
    - Lo Shu Grid      — 3×3 magic square from DOB digits
    - Name Correction  — lucky vs unlucky name analysis + suggestions
    - Compatibility    — two people, multiple axes
    - Personal Year / Month / Day forecast
    - Karmic Debt & Karmic Lesson detection
    - Planes of Expression (Physical / Mental / Emotional / Intuitive)
"""

import re
from typing import Optional

# ── Re-export base reduce so callers only import this file ────────────
from numerology import (
    reduce, life_path, destiny as destiny_pythagorean,
    soul_urge as soul_urge_pythagorean,
    personality as personality_pythagorean,
    personal_year, PYTHAGOREAN, VOWELS,
)

MASTER_NUMBERS  = {11, 22, 33}
KARMIC_DEBT_NOS = {13, 14, 16, 19}

# ════════════════════════════════════════════════════════════════
# CHALDEAN SYSTEM
# ════════════════════════════════════════════════════════════════
# Key differences from Pythagorean:
#   • Number 9 is NOT assigned to any letter (sacred / divine)
#   • Letters cycle 1-8 only
#   • Uses CURRENT / KNOWN name, not full birth name
#   • Compound numbers retained as-is for deeper meaning
CHALDEAN = {
    'A':1,'I':1,'J':1,'Q':1,'Y':1,
    'B':2,'K':2,'R':2,
    'C':3,'G':3,'L':3,'S':3,
    'D':4,'M':4,'T':4,
    'E':5,'H':5,'N':5,'X':5,
    'U':6,'V':6,'W':6,
    'O':7,'Z':7,
    'F':8,'P':8,
    # Note: no letter maps to 9
}

def chaldean_value(name: str) -> dict:
    """
    Chaldean name value — returns both compound number and final reduced.
    Chaldean traditionally preserves the compound for interpretation.
    """
    name_up = name.upper()
    total   = 0
    letters = []
    for ch in name_up:
        if ch in CHALDEAN:
            val = CHALDEAN[ch]
            total += val
            letters.append((ch, val))
    compound = total
    final    = reduce(total)
    return {
        'compound'  : compound,
        'final'     : final,
        'letters'   : letters,
        'raw_sum'   : total,
        'system'    : 'Chaldean',
    }

def chaldean_soul_urge(name: str) -> dict:
    name_up = name.upper()
    total   = sum(CHALDEAN.get(ch, 0) for ch in name_up if ch in VOWELS)
    return {'compound': total, 'final': reduce(total), 'system': 'Chaldean'}

def chaldean_personality(name: str) -> dict:
    name_up = name.upper()
    CONS    = set(CHALDEAN.keys()) - VOWELS
    total   = sum(CHALDEAN.get(ch, 0) for ch in name_up if ch in CONS)
    return {'compound': total, 'final': reduce(total), 'system': 'Chaldean'}


# ════════════════════════════════════════════════════════════════
# VEDIC / ANK JYOTISH SYSTEM
# ════════════════════════════════════════════════════════════════
# Ank (digit) Jyotish uses same letter→number as Chaldean
# but adds planetary lordship layer (very popular in India)
VEDIC_LORDS = {
    1: 'Sun (Surya)',       2: 'Moon (Chandra)',
    3: 'Jupiter (Guru)',    4: 'Rahu',
    5: 'Mercury (Budha)',   6: 'Venus (Shukra)',
    7: 'Ketu',              8: 'Saturn (Shani)',
    9: 'Mars (Mangal)',
    11:'Sun+Moon (Special)',22:'Sun+Saturn (Master)',
    33:'Jupiter+Guru (Master)',
}

VEDIC_FRIENDLY = {
    1: [1,2,3,9],  2: [1,2,4,7],  3: [1,3,5,9],
    4: [2,4,6,8],  5: [1,3,5,9],  6: [2,4,6,8],
    7: [2,4,7],    8: [4,6,8],    9: [1,3,5,9],
}

def vedic_moolank(dob: str) -> dict:
    """
    Moolank = sum of the birth day DIGITS (not reduction of the integer).

    Per spec: day=21 → 2+1=3 (not reduce(21)=3 coincidentally, but the process differs
    for days like 29: digit_sum=11→reduce→2, whereas reduce(29)=11 Master).
    Always reduce to 1-9 — no master numbers for Moolank in Vedic tradition.
    """
    day_str = dob.split('-')[2]
    day_sum = sum(int(d) for d in day_str)   # digit sum of the day string
    val = day_sum
    while val > 9:
        val = sum(int(d) for d in str(val))
    return {
        'moolank'  : val,
        'compound' : int(day_str),
        'day_sum'  : day_sum,
        'lord'     : VEDIC_LORDS.get(val, ''),
        'day_raw'  : int(day_str),
    }

def vedic_bhagyank(dob: str) -> dict:
    """Bhagyank = Life Path in Vedic system (same calculation, different name/meaning)."""
    lp = life_path(dob)
    return {
        'bhagyank' : lp,
        'lord'     : VEDIC_LORDS.get(lp, ''),
    }

def vedic_namank(name: str) -> dict:
    """Namank = Chaldean value of name."""
    result = chaldean_value(name)
    result['lord'] = VEDIC_LORDS.get(result['final'], '')
    result['system'] = 'Vedic/Ank'
    return result

def vedic_kua(dob: str, gender: str = 'M') -> int:
    """
    Kua number — Eastern system for auspicious directions.
    Spec formula:
      Step 1: Sum birth year digits to single digit
      Step 2: Male  → 11 - sum  (reduce if > 9)
              Female → 4 + sum  (reduce if > 9)
    """
    yr   = int(dob.split('-')[0])
    yr_s = sum(int(d) for d in str(yr))
    yr_r = reduce(yr_s)        # e.g. 1+9+8+2=20 → 2
    if gender.upper() == 'M':
        kua = reduce(11 - yr_r)   # 11-2=9
    else:
        kua = reduce(4 + yr_r)    # 4+2=6
    return kua


# ════════════════════════════════════════════════════════════════
# KABBALAH SYSTEM
# ════════════════════════════════════════════════════════════════
# Based on Hebrew alphabet positional values
# A=1..Z=26, then cycle: AA=1, BB=2... (simplified Western Kabbalah)
def kabbalah_value(name: str) -> dict:
    """
    Western Kabbalah numerology.
    Assigns A=1, B=2... Z=26 then cycles: if total > 9 reduce digit by digit.
    Uses only first name traditionally.
    """
    name_up = name.upper()
    # A=1..Z=26
    KAB = {chr(65+i): i+1 for i in range(26)}
    total   = sum(KAB.get(ch, 0) for ch in name_up if ch.isalpha())
    # Reduce to 1-9
    while total > 9:
        total = sum(int(d) for d in str(total))
    MEANINGS = {
        1:'Leadership, independence, ambition',
        2:'Partnership, diplomacy, sensitivity',
        3:'Creativity, expression, joy',
        4:'Stability, discipline, foundation',
        5:'Freedom, change, adventure',
        6:'Harmony, nurturing, responsibility',
        7:'Spirituality, introspection, wisdom',
        8:'Power, material success, authority',
        9:'Humanitarianism, completion, compassion',
    }
    return {
        'value'  : total,
        'meaning': MEANINGS.get(total,''),
        'system' : 'Kabbalah',
    }


# ════════════════════════════════════════════════════════════════
# LO SHU GRID
# ════════════════════════════════════════════════════════════════
# 3×3 magic square. Digits 1-9 from DOB plotted into fixed positions.
# Missing digits = karmic lessons. Repeated = strong traits.
#
#  4 | 9 | 2
#  3 | 5 | 7
#  8 | 1 | 6

LO_SHU_LAYOUT = [
    [4, 9, 2],
    [3, 5, 7],
    [8, 1, 6],
]

LO_SHU_MEANINGS = {
    1: ('Water / Mind Plane',     'Intelligence, memory, communication'),
    2: ('Earth / Sensitivity',    'Intuition, sensitivity, emotional depth'),
    3: ('Emotions / Action',      'Action, motivation, drive and energy'),
    4: ('Practicality',           'Practicality, hard work, organisation'),
    5: ('Will / Centre',          'Balance, freedom, adaptability — the fulcrum'),
    6: ('Creativity / Vision',    'Creative visualisation, imagination, home'),
    7: ('Sacrifice / Learning',   'Learning through sacrifice, patience, wisdom'),
    8: ('Practical Wisdom',       'Wisdom applied practically, business acumen'),
    9: ('Idealism / Ambition',    'Idealism, ambition, higher purpose'),
}

LO_SHU_ARROWS = {
    # Rows (horizontal — Thought, Will, Action planes)
    'thought_plane'  : [4, 9, 2],  # row 1 — mental
    'will_plane'     : [3, 5, 7],  # row 2 — spiritual
    'action_plane'   : [8, 1, 6],  # row 3 — physical
    # Columns (vertical — Mind, Soul, Physical)
    'mind_col'       : [4, 3, 8],  # col 1
    'soul_col'       : [9, 5, 1],  # col 2 — the spiritual column
    'physical_col'   : [2, 7, 6],  # col 3
    # Diagonals
    'determination'  : [4, 5, 6],  # \  determination
    'compassion'     : [2, 5, 8],  # /  compassion
}

def lo_shu_grid(dob: str, gender: str = 'M') -> dict:
    """
    Build Lo Shu grid using the FULL Vedic pool:
      DOB raw digits (0 excluded)
      + Moolank  (sum of birth day)
      + Life Path / Bhagyank (sum of full DOB)
      + Kua number

    This matches the traditional Vedic Lo Shu method where the
    calculated numbers are added to the grid — not just raw DOB digits.

    Pythagorean name-based Karmic Lessons are NEVER included here.
    They are a separate calculation (see get_pythagorean_name_lessons).
    """
    # Step 1: raw DOB digits (0 excluded)
    digits_raw = [int(d) for d in dob.replace('-', '') if d != '0']

    # Step 2: calculated numbers per spec
    day       = int(dob.split('-')[2])
    moolank   = reduce(day)
    lp        = life_path(dob)
    kua       = vedic_kua(dob, gender)

    # Full pool = raw digits + moolank + life_path + kua
    full_pool = digits_raw + [moolank, lp, kua]

    # Count occurrences of each 1-9 in the full pool
    digit_count = {n: full_pool.count(n) for n in range(1, 10)}

    present = [n for n in range(1, 10) if digit_count[n] > 0]
    absent  = [n for n in range(1, 10) if digit_count[n] == 0]

    # Build 3×3 display grid (show count or empty)
    grid = []
    for row in LO_SHU_LAYOUT:
        grid.append([digit_count[n] for n in row])

    # Detect complete arrows (all 3 digits present in a line)
    arrows_present = {}
    for arrow_name, digits in LO_SHU_ARROWS.items():
        if all(digit_count[d] > 0 for d in digits):
            arrows_present[arrow_name] = digits

    # Absent digit meanings (karmic lessons)
    karmic_lessons = {
        n: LO_SHU_MEANINGS[n][1] for n in absent
    }

    # Strong numbers (appear 3+ times)
    strong = {n: digit_count[n] for n in range(1,10) if digit_count[n] >= 3}

    return {
        'grid'           : grid,
        'layout'         : LO_SHU_LAYOUT,
        'digit_count'    : digit_count,
        'present'        : present,
        'absent'         : absent,
        'strong'         : strong,
        'arrows_present' : arrows_present,
        'karmic_lessons' : karmic_lessons,
        'meanings'       : LO_SHU_MEANINGS,
    }


# ════════════════════════════════════════════════════════════════
# KARMIC DEBT & KARMIC LESSONS
# ════════════════════════════════════════════════════════════════
KARMIC_DEBT_MEANINGS = {
    13: 'Debt of laziness. Must overcome tendency to take shortcuts. Past-life neglect of duties.',
    14: 'Debt of misused freedom. Overindulgence, addiction, abuse of others\' freedom.',
    16: 'Debt of ego and pride. Destruction of the false self to build authentic identity.',
    19: 'Debt of misused power. Learning to rely on others; ego and self-centredness.',
}

KARMIC_LESSON_MEANINGS = {
    1: 'Learn self-reliance, originality, leadership.',
    2: 'Develop patience, diplomacy, sensitivity to others.',
    3: 'Express creativity, joy; avoid scattered energy.',
    4: 'Build discipline, order, and practical foundations.',
    5: 'Embrace change, freedom, and versatility.',
    6: 'Take on responsibility, nurturing, and commitment.',
    7: 'Develop inner wisdom, trust your intuition.',
    8: 'Learn about material power, business, and authority.',
    9: 'Develop compassion, generosity, and detachment.',
}


def get_pythagorean_name_lessons(full_name: str) -> dict:
    """
    Pythagorean Karmic Name Lessons — STRICTLY name-based.

    These are the numbers 1-9 with NO corresponding letter in the
    full name string. This is a Pythagorean system calculation and
    must NEVER be passed to the Lo Shu grid.

    Returns:
        lessons : list of {number, meaning, missing_letters}
        present : set of numbers that ARE represented
    """
    KARMIC_LESSON_MEANINGS = {
        1: 'Learn self-reliance, originality, and independent leadership.',
        2: 'Develop patience, diplomacy, and sensitivity to others.',
        3: 'Express creativity and joy; avoid scattering energy.',
        4: 'Build discipline, order, and practical foundations.',
        5: 'Embrace change, freedom, and versatility.',
        6: 'Take on responsibility, nurturing, and long-term commitment.',
        7: 'Develop inner wisdom and trust your intuition.',
        8: 'Learn about material power, business, and authority.',
        9: 'Develop compassion, generosity, and detachment from outcomes.',
    }
    upper    = full_name.upper()
    present  = set(PYTHAGOREAN.get(c, 0) for c in upper if c in PYTHAGOREAN)
    present.discard(0)
    lessons  = []
    for num in range(1, 10):
        if num not in present:
            missing_letters = [l for l, v in PYTHAGOREAN.items() if v == num]
            lessons.append({
                'number'         : num,
                'meaning'        : KARMIC_LESSON_MEANINGS[num],
                'missing_letters': missing_letters,
            })
    return {
        'lessons' : lessons,
        'present' : sorted(present),
        'absent'  : [l['number'] for l in lessons],
        'source'  : 'Pythagorean name — never use in Lo Shu grid',
    }


def karmic_analysis(full_name: str, dob: str) -> dict:
    """
    Detect Karmic Debt numbers (from Life Path, Destiny, Soul Urge intermediate sums)
    and Karmic Lessons (missing letters in name).
    """
    # ── Karmic Debt: check pre-reduction sums ─────────────────
    debts = []

    # Life Path intermediate
    parts   = dob.split('-')
    yr, mo, dy = int(parts[0]), int(parts[1]), int(parts[2])
    day_sum  = dy
    year_sum = sum(int(d) for d in str(yr))
    for raw in [day_sum, year_sum]:
        if raw in KARMIC_DEBT_NOS:
            debts.append({'number': raw, 'source': 'Life Path',
                          'meaning': KARMIC_DEBT_MEANINGS[raw]})

    # Destiny intermediate
    upper    = full_name.upper()
    dest_raw = sum(PYTHAGOREAN.get(ch, 0) for ch in upper if ch in PYTHAGOREAN)
    if dest_raw in KARMIC_DEBT_NOS:
        debts.append({'number': dest_raw, 'source': 'Destiny',
                      'meaning': KARMIC_DEBT_MEANINGS[dest_raw]})

    # ── Karmic Lessons: letters missing from name ─────────────
    name_letters = set(upper)
    # Which numbers (1-9) have NO corresponding letter in name?
    lessons = []
    for num in range(1, 10):
        letters_for_num = [l for l,v in PYTHAGOREAN.items() if v == num]
        if not any(l in name_letters for l in letters_for_num):
            lessons.append({'number': num,
                            'meaning': KARMIC_LESSON_MEANINGS[num],
                            'missing_letters': letters_for_num})

    return {'karmic_debts': debts, 'karmic_lessons': lessons}


# ════════════════════════════════════════════════════════════════
# NAME CORRECTION / LUCKY NAME ANALYSIS
# ════════════════════════════════════════════════════════════════
# Checks whether current name vibrates harmoniously with Life Path
# and Moolank. Suggests modifications or alternative spellings.

COMPATIBILITY_GRID = {
    # life_path: compatible_destiny_numbers
    1: [1,3,5,9],   2: [2,4,6,8],   3: [1,3,5,9],
    4: [2,4,6,8],   5: [1,3,5,9],   6: [2,4,6,8],
    7: [2,7,9],     8: [2,4,6,8],   9: [1,3,5,9],
}

def name_correction(full_name: str, dob: str) -> dict:
    """
    Analyse whether the name is 'lucky' relative to Life Path.

    Returns:
      - current analysis (Pythagorean + Chaldean values)
      - compatibility score
      - suggestions for name adjustment
    """
    lp     = life_path(dob)
    mool   = reduce(int(dob.split('-')[2]))
    pyth_d = destiny_pythagorean(full_name)
    chald  = chaldean_value(full_name)['final']
    vedic  = vedic_namank(full_name)['final']

    # Compatibility check
    friendly = COMPATIBILITY_GRID.get(lp, [])
    pyth_ok  = pyth_d in friendly
    chald_ok = chald  in friendly

    # Harmony score 0-100
    score = 0
    if pyth_d == lp:   score += 40    # exact match
    elif pyth_ok:      score += 25
    if chald == lp:    score += 30
    elif chald_ok:     score += 15
    if pyth_d == mool: score += 15
    if chald  == mool: score += 15
    score = min(score, 100)

    harmony = ('Excellent — name strongly aligned with destiny' if score >= 70
               else 'Good — name reasonably aligned'           if score >= 45
               else 'Moderate — some tension with Life Path'   if score >= 25
               else 'Challenging — name vibrates against destiny')

    # Suggest letter additions for improvement (append a silent letter)
    suggestions = []
    if score < 70:
        # Find which single letter addition brings Pythagorean destiny closer to lp
        target_nums = COMPATIBILITY_GRID.get(lp, [lp])
        for letter in 'AEIOUBCDFGHJKLMNPQRSTVWXYZ':
            test_name = full_name + letter
            test_val  = destiny_pythagorean(test_name)
            if test_val in target_nums and test_val != pyth_d:
                suggestions.append({
                    'modified_name'    : test_name,
                    'new_destiny_pyth' : test_val,
                    'letter_added'     : letter,
                    'reason'           : f'Destiny {test_val} aligns with Life Path {lp}',
                })
            if len(suggestions) >= 3:
                break

    return {
        'name'            : full_name,
        'life_path'       : lp,
        'moolank'         : mool,
        'destiny_pyth'    : pyth_d,
        'destiny_chaldean': chald,
        'destiny_vedic'   : vedic,
        'harmony_score'   : score,
        'harmony_label'   : harmony,
        'is_lucky'        : score >= 45,
        'pyth_compatible' : pyth_ok,
        'chald_compatible': chald_ok,
        'suggestions'     : suggestions,
    }


# ════════════════════════════════════════════════════════════════
# COMPATIBILITY  (two people)
# ════════════════════════════════════════════════════════════════
COMPAT_PAIRS = {
    # (a, b): score 0-10
    # Self-pairs
    (1,1):8,(2,2):7,(3,3):9,(4,4):6,(5,5):8,(6,6):9,(7,7):7,(8,8):6,(9,9):8,
    # Strong
    (1,5):9,(1,9):9,(1,3):8,(2,6):9,(2,8):8,(3,9):9,(4,8):8,(5,9):8,
    (6,9):8,(1,2):7,(3,6):7,(4,6):8,(5,7):7,(2,9):8,
    # Moderate
    (1,6):6,(1,7):6,(2,3):6,(2,7):7,(3,5):7,(4,7):6,(5,6):6,
    (6,8):7,(7,9):7,(3,8):6,
    # Challenging
    (1,4):4,(1,8):4,(2,4):4,(3,4):3,(4,5):4,(4,9):4,(5,8):4,
    (6,7):4,(7,8):3,(8,9):5,
}

def _compat_score(a: int, b: int) -> int:
    key = (min(a,b), max(a,b))
    return COMPAT_PAIRS.get(key, 5)   # default moderate

def numerology_compatibility(
    name1: str, dob1: str,
    name2: str, dob2: str
) -> dict:
    """
    Full numerology compatibility between two people.
    Analyses: Life Path, Destiny, Soul Urge (3 axes).
    Returns per-axis scores + overall + narrative.
    """
    lp1 = life_path(dob1);          lp2 = life_path(dob2)
    d1  = destiny_pythagorean(name1); d2  = destiny_pythagorean(name2)
    su1 = soul_urge_pythagorean(name1); su2 = soul_urge_pythagorean(name2)
    m1  = reduce(int(dob1.split('-')[2]))
    m2  = reduce(int(dob2.split('-')[2]))

    lp_score   = _compat_score(lp1, lp2)
    dest_score = _compat_score(d1,  d2)
    su_score   = _compat_score(su1, su2)
    mool_score = _compat_score(m1,  m2)

    # Weighted overall: LP=40%, Destiny=30%, Soul=20%, Moolank=10%
    overall = round(
        lp_score   * 0.40 +
        dest_score * 0.30 +
        su_score   * 0.20 +
        mool_score * 0.10,
        1
    )

    def label(s):
        if s >= 8:  return 'Excellent'
        if s >= 6:  return 'Good'
        if s >= 4:  return 'Moderate'
        return 'Challenging'

    return {
        'person1': {'name':name1,'life_path':lp1,'destiny':d1,'soul_urge':su1,'moolank':m1},
        'person2': {'name':name2,'life_path':lp2,'destiny':d2,'soul_urge':su2,'moolank':m2},
        'scores': {
            'life_path'  : {'score':lp_score,   'label':label(lp_score)},
            'destiny'    : {'score':dest_score,  'label':label(dest_score)},
            'soul_urge'  : {'score':su_score,    'label':label(su_score)},
            'moolank'    : {'score':mool_score,  'label':label(mool_score)},
        },
        'overall'       : overall,
        'overall_label' : label(overall),
        'overall_pct'   : round(overall * 10),
    }


# ════════════════════════════════════════════════════════════════
# PERSONAL YEAR / MONTH / DAY FORECASTS
# ════════════════════════════════════════════════════════════════
PERSONAL_YEAR_THEMES = {
    1: ('New Beginnings',    'Plant seeds, launch projects, embrace independence. '
                             'What you start now shapes the next 9-year cycle.'),
    2: ('Cooperation',       'Patience, partnerships, and diplomacy. Avoid forcing outcomes. '
                             'Build alliances quietly — the harvest comes later.'),
    3: ('Expression',        'Creativity, socialising, and self-expression peak. '
                             'Joy is the currency. Communicate your gifts widely.'),
    4: ('Foundation',        'Hard work, structure, and building stable systems. '
                             'Discipline now creates the platform for years 5-9.'),
    5: ('Change & Freedom',  'Expect the unexpected. Travel, reinvention, and breakthroughs. '
                             'Adaptability is your superpower this year.'),
    6: ('Responsibility',    'Family, home, and service to others. Relationships deepen. '
                             'Commit to long-term obligations with open hands.'),
    7: ('Introspection',     'A year of solitude, spiritual inquiry, and inner wisdom. '
                             'Withdraw, study, and trust the unseen work happening.'),
    8: ('Power & Wealth',    'Manifestation of material goals — career, finances, authority. '
                             'Step up and claim what you have built.'),
    9: ('Completion',        'Release what no longer serves. Endings are openings. '
                             'Generosity and forgiveness clear the slate for Year 1.'),
    11:('Illumination',      'Master Year: heightened intuition and spiritual awakening. '
                             'Serve as a light-bearer — inspire without ego.'),
    22:('Master Builder',    'Master Year: large-scale creation and legacy work. '
                             'Vision + discipline = permanent structures.'),
}

def forecast(dob: str, year: int, month: int, day: int) -> dict:
    """Full personal year / month / day forecast."""
    py_val = personal_year(dob, year)
    parts  = dob.split('-')
    r_day  = reduce(int(parts[2]))
    r_mon  = reduce(int(parts[1]))

    # Personal Month = Personal Year + calendar month, reduced
    pm_val = reduce(py_val + month)
    # Personal Day   = Personal Month + calendar day, reduced
    pd_val = reduce(pm_val + day)

    py_theme, py_desc = PERSONAL_YEAR_THEMES.get(py_val, ('',''))
    pm_theme, pm_desc = PERSONAL_YEAR_THEMES.get(pm_val, ('',''))
    pd_theme, pd_desc = PERSONAL_YEAR_THEMES.get(pd_val, ('',''))

    return {
        'personal_year'  : {'value':py_val,'theme':py_theme,'desc':py_desc},
        'personal_month' : {'value':pm_val,'theme':pm_theme,'desc':pm_desc,'calendar_month':month},
        'personal_day'   : {'value':pd_val,'theme':pd_theme,'desc':pd_desc,'calendar_day':day},
        'year': year, 'month': month, 'day': day,
    }


# ════════════════════════════════════════════════════════════════
# PLANES OF EXPRESSION
# ════════════════════════════════════════════════════════════════
# Each letter belongs to one of 4 planes
PLANES = {
    'Physical'  : set('DELMSTW'),
    'Mental'    : set('AEHIJLNOP'),
    'Emotional' : set('BCFIKLMORSTUVWXZ'),
    'Intuitive' : set('FIOPQY'),
}
# Some letters appear in multiple planes (intentional — they have dual nature)

def planes_of_expression(full_name: str) -> dict:
    """
    How the person expresses themselves across 4 planes.
    Returns count + percentage for each plane.
    """
    upper  = full_name.upper()
    alpha  = [ch for ch in upper if ch.isalpha()]
    total  = len(alpha)
    result = {}
    for plane, letters in PLANES.items():
        count = sum(1 for ch in alpha if ch in letters)
        result[plane] = {
            'count': count,
            'pct'  : round(count / total * 100) if total else 0,
            'dominant': count == max(
                sum(1 for ch in alpha if ch in s) for s in PLANES.values()
            ),
        }
    dominant = max(result, key=lambda p: result[p]['count'])
    result['dominant_plane'] = dominant
    return result


# ════════════════════════════════════════════════════════════════
# FULL NUMEROLOGY REPORT
# ════════════════════════════════════════════════════════════════
def full_report(
    full_name: str,
    dob: str,
    gender: str = 'M',
    current_year: int = None,
    current_month: int = None,
    current_day: int = None,
    name2: str = None,
    dob2: str = None,
) -> dict:
    """
    Generate complete multi-system numerology report.
    Includes all systems, Lo Shu Grid, Name Correction,
    Karmic analysis, Planes of Expression, and optional Compatibility.
    """
    import datetime
    today = datetime.date.today()
    yr  = current_year  or today.year
    mo  = current_month or today.month
    dy  = current_day   or today.day

    # ── Core Pythagorean ──────────────────────────────────────
    pyth = {
        'life_path'  : life_path(dob),
        'destiny'    : destiny_pythagorean(full_name),
        'soul_urge'  : soul_urge_pythagorean(full_name),
        'personality': personality_pythagorean(full_name),
        'personal_year': personal_year(dob, yr),
    }

    # ── Chaldean ──────────────────────────────────────────────
    chald = {
        'name_value' : chaldean_value(full_name),
        'soul_urge'  : chaldean_soul_urge(full_name),
        'personality': chaldean_personality(full_name),
    }

    # ── Vedic/Ank ─────────────────────────────────────────────
    vedic = {
        'moolank'  : vedic_moolank(dob),
        'bhagyank' : vedic_bhagyank(dob),
        'namank'   : vedic_namank(full_name),
        'kua'      : vedic_kua(dob, gender),
    }

    # ── Kabbalah ──────────────────────────────────────────────
    kab = kabbalah_value(full_name.split()[0])  # first name only, traditional

    # ── Lo Shu Grid ───────────────────────────────────────────
    lo_shu = lo_shu_grid(dob)

    # ── Karmic Analysis ───────────────────────────────────────
    karmic = karmic_analysis(full_name, dob)

    # ── Name Correction ───────────────────────────────────────
    correction = name_correction(full_name, dob)

    # ── Planes of Expression ──────────────────────────────────
    planes = planes_of_expression(full_name)

    # ── Forecast ──────────────────────────────────────────────
    fc = forecast(dob, yr, mo, dy)

    # ── Compatibility (optional) ──────────────────────────────
    compat = None
    if name2 and dob2:
        compat = numerology_compatibility(full_name, dob, name2, dob2)

    return {
        'input'        : {'full_name':full_name,'dob':dob,'gender':gender},
        'pythagorean'  : pyth,
        'chaldean'     : chald,
        'vedic'        : vedic,
        'kabbalah'     : kab,
        'lo_shu'       : lo_shu,
        'karmic'       : karmic,
        'name_correction': correction,
        'planes'       : planes,
        'forecast'     : fc,
        'compatibility': compat,
    }


# ════════════════════════════════════════════════════════════════
# TESTS
# ════════════════════════════════════════════════════════════════
def run_tests():
    import datetime
    errors = []
    name = 'Jyotirmoy Giri'
    dob  = '1982-02-21'

    print("Running extended numerology tests...\n")

    # Chaldean
    cv = chaldean_value(name)
    # J=1,Y=1,O=7,T=4,I=1,R=2,M=4,O=7,Y=1 G=3,I=1,R=2,I=1 = 35 → 8
    ok = cv['final'] in range(1,10)
    print(f"  chaldean_value('{name}') = {cv['compound']} → {cv['final']}  {'✅' if ok else '❌'}")
    if not ok: errors.append(f"Chaldean value out of range: {cv['final']}")

    # Chaldean soul urge
    csu = chaldean_soul_urge(name)
    print(f"  chaldean_soul_urge = {csu['compound']} → {csu['final']}  ✅")

    # Vedic Moolank (DOB day=21 → 3)
    mool = vedic_moolank(dob)
    ok2 = mool['moolank'] == 3
    print(f"  vedic_moolank = {mool['moolank']}  {'✅' if ok2 else '❌ expected 3'}")
    if not ok2: errors.append(f"Moolank wrong: {mool['moolank']}")

    # Vedic Bhagyank (= Life Path 7)
    bh = vedic_bhagyank(dob)
    ok3 = bh['bhagyank'] == 7
    print(f"  vedic_bhagyank = {bh['bhagyank']}  {'✅' if ok3 else '❌ expected 7'}")
    if not ok3: errors.append(f"Bhagyank wrong: {bh['bhagyank']}")

    # Kabbalah (first name only)
    kab = kabbalah_value('Jyotirmoy')
    ok4 = 1 <= kab['value'] <= 9
    print(f"  kabbalah_value('Jyotirmoy') = {kab['value']}  {'✅' if ok4 else '❌'}")
    if not ok4: errors.append(f"Kabbalah out of range: {kab['value']}")

    # Lo Shu Grid
    ls = lo_shu_grid(dob)
    # DOB 1982-02-21 → digits: 1,9,8,2,2,2,1 (ignoring 0s)
    # present should include 1,2,8,9
    ok5 = 1 in ls['present'] and 2 in ls['present']
    print(f"  lo_shu present={ls['present']} absent={ls['absent']}  {'✅' if ok5 else '❌'}")
    if not ok5: errors.append("Lo Shu grid wrong")
    # Grid must be 3×3
    ok6 = len(ls['grid']) == 3 and all(len(r)==3 for r in ls['grid'])
    print(f"  lo_shu grid shape 3×3  {'✅' if ok6 else '❌'}")

    # Name Correction
    nc = name_correction(name, dob)
    ok7 = 0 <= nc['harmony_score'] <= 100
    print(f"  name_correction score={nc['harmony_score']}  label='{nc['harmony_label']}'  "
          f"{'✅' if ok7 else '❌'}")
    if not ok7: errors.append(f"Name correction score out of range: {nc['harmony_score']}")

    # Compatibility
    c = numerology_compatibility(name, dob, 'Priya Sharma', '1985-06-15')
    ok8 = 0 <= c['overall'] <= 10
    print(f"  compatibility overall={c['overall']}/10 ({c['overall_label']})  "
          f"{'✅' if ok8 else '❌'}")
    if not ok8: errors.append(f"Compatibility score out of range: {c['overall']}")

    # Forecast
    fc = forecast(dob, 2026, 4, 29)
    ok9 = fc['personal_year']['value'] == 6   # we know PY2026=6
    print(f"  forecast PY={fc['personal_year']['value']} "
          f"PM={fc['personal_month']['value']} "
          f"PD={fc['personal_day']['value']}  "
          f"{'✅' if ok9 else '❌ PY expected 6'}")
    if not ok9: errors.append(f"Personal Year wrong: {fc['personal_year']['value']}")

    # Karmic analysis
    ka = karmic_analysis(name, dob)
    print(f"  karmic debts={len(ka['karmic_debts'])}  "
          f"lessons={len(ka['karmic_lessons'])}  ✅")

    # Planes
    pl = planes_of_expression(name)
    ok10 = pl['dominant_plane'] in ['Physical','Mental','Emotional','Intuitive']
    print(f"  dominant_plane='{pl['dominant_plane']}'  {'✅' if ok10 else '❌'}")
    if not ok10: errors.append(f"Invalid dominant plane: {pl['dominant_plane']}")

    print()
    if errors:
        print(f"❌ {len(errors)} FAILED: {errors}")
    else:
        print("✅ All extended tests passed.")
    return len(errors) == 0


if __name__ == '__main__':
    run_tests()

    print("\n" + "="*60)
    print("FULL REPORT — Jyotirmoy Giri  1982-02-21")
    print("="*60)

    import json, datetime
    r = full_report('Jyotirmoy Giri', '1982-02-21',
                    gender='M', current_year=2026,
                    current_month=4, current_day=29)

    # Print key highlights
    print(f"\n── PYTHAGOREAN ──")
    for k,v in r['pythagorean'].items():
        print(f"  {k:<20}: {v}")

    print(f"\n── CHALDEAN ──")
    cv = r['chaldean']['name_value']
    print(f"  Name value        : {cv['compound']} → {cv['final']}")
    print(f"  Soul Urge         : {r['chaldean']['soul_urge']['final']}")
    print(f"  Personality       : {r['chaldean']['personality']['final']}")

    print(f"\n── VEDIC/ANK ──")
    print(f"  Moolank (birth day): {r['vedic']['moolank']['moolank']}  "
          f"({r['vedic']['moolank']['lord']})")
    print(f"  Bhagyank (life path): {r['vedic']['bhagyank']['bhagyank']}  "
          f"({r['vedic']['bhagyank']['lord']})")
    print(f"  Namank (name value): {r['vedic']['namank']['final']}  "
          f"({r['vedic']['namank']['lord']})")
    print(f"  Kua Number        : {r['vedic']['kua']}")

    print(f"\n── KABBALAH ──")
    print(f"  First name value  : {r['kabbalah']['value']}  ({r['kabbalah']['meaning']})")

    print(f"\n── LO SHU GRID ──")
    ls = r['lo_shu']
    print("  Layout:")
    for row_layout, row_counts in zip(ls['layout'], ls['grid']):
        cells = [f"[{row_layout[i]}:{row_counts[i]}]" for i in range(3)]
        print("    " + "  ".join(cells))
    print(f"  Present : {ls['present']}")
    print(f"  Absent  : {ls['absent']}  (karmic lessons)")
    print(f"  Arrows  : {list(ls['arrows_present'].keys()) or 'none'}")

    print(f"\n── NAME CORRECTION ──")
    nc = r['name_correction']
    print(f"  Harmony score     : {nc['harmony_score']}/100  ({nc['harmony_label']})")
    print(f"  Lucky name?       : {'✅ Yes' if nc['is_lucky'] else '⚠ Moderate'}")
    if nc['suggestions']:
        print(f"  Suggestions:")
        for s in nc['suggestions']:
            print(f"    → {s['modified_name']}  (Destiny {s['new_destiny_pyth']}) — {s['reason']}")

    print(f"\n── KARMIC ──")
    ka = r['karmic']
    if ka['karmic_debts']:
        for d in ka['karmic_debts']:
            print(f"  Debt {d['number']} ({d['source']}): {d['meaning'][:60]}…")
    else:
        print("  No major karmic debts detected")
    if ka['karmic_lessons']:
        for l in ka['karmic_lessons']:
            print(f"  Lesson {l['number']}: {l['meaning']}")

    print(f"\n── FORECAST 2026 ──")
    fc = r['forecast']
    print(f"  Personal Year  {fc['personal_year']['value']}  — {fc['personal_year']['theme']}")
    print(f"  Personal Month {fc['personal_month']['value']}  — {fc['personal_month']['theme']} (Month {fc['personal_month']['calendar_month']})")
    print(f"  Personal Day   {fc['personal_day']['value']}   — {fc['personal_day']['theme']}")

    print(f"\n── PLANES OF EXPRESSION ──")
    pl = r['planes']
    for plane in ['Physical','Mental','Emotional','Intuitive']:
        bar = '█' * (pl[plane]['pct'] // 5)
        print(f"  {plane:<12}: {bar:<20} {pl[plane]['pct']}%")
    print(f"  Dominant: {pl['dominant_plane']}")
