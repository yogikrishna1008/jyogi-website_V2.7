"""
jyogi_logic.py — Jyogi AI Proprietary Interpretation Rules
============================================================
Five structured logic rules that override standard Vedic scoring.
These sit on top of vedic_engine.py and apply AFTER base positions
are computed.

Rules:
  Rule 1 — Navamsha Strength-Flip (D9 overrides D1 dignity)
  Rule 2 — Setting House Penalty  (7th house −25%)
  Rule 3 — Yoni Hierarchy         (Lagna→Moon→Venus→7th Lord for relationships)
  Rule 4 — 10th-7th Career Link   (social work / foreign market signal)
  Rule 5 — Smoke Condition        (Saturn/Rahu in 7th → Late Recognition)

Usage:
    from jyogi_logic import JyogiLogic
    logic = JyogiLogic(planets, lagna_lon, d9)
    result = logic.full_analysis()
"""

from typing import Optional

# ── Re-use constants from vedic_engine ──────────────────────────────
_EXALT = {
    'Sun': 0, 'Moon': 1, 'Mars': 9,
    'Mercury': 5, 'Jupiter': 3, 'Venus': 11, 'Saturn': 6,
}
_DEBIL = {
    'Sun': 6, 'Moon': 7, 'Mars': 3,
    'Mercury': 11, 'Jupiter': 9, 'Venus': 5, 'Saturn': 0,
}
_OWN = {
    'Sun': [4], 'Moon': [3], 'Mars': [0, 7],
    'Mercury': [2, 5], 'Jupiter': [8, 11],
    'Venus': [1, 6], 'Saturn': [9, 10],
}
# Planetary lords of each rashi (0=Aries … 11=Pisces)
_RASHI_LORD = {
    0: 'Mars',    1: 'Venus',   2: 'Mercury',  3: 'Moon',
    4: 'Sun',     5: 'Mercury', 6: 'Venus',    7: 'Mars',
    8: 'Jupiter', 9: 'Saturn', 10: 'Saturn',  11: 'Jupiter',
}
RASHIS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces',
]
NAKSH = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni',
    'Uttara Phalguni', 'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha',
    'Jyeshtha', 'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana',
    'Dhanishtha', 'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati',
]

# ── Nakshatra animal / yoni table ───────────────────────────────────
# (nakshatra_index: (animal, nature))
# nature: 'loyal' | 'dominant' | 'neutral' | 'aggressive' | 'sensitive'
_YONI = {
    0:  ('Horse',    'dominant'),   # Ashwini
    1:  ('Elephant', 'sensitive'),  # Bharani
    2:  ('Goat',     'neutral'),    # Krittika
    3:  ('Serpent',  'aggressive'), # Rohini
    4:  ('Serpent',  'aggressive'), # Mrigashira
    5:  ('Dog',      'loyal'),      # Ardra
    6:  ('Cat',      'neutral'),    # Punarvasu
    7:  ('Goat',     'neutral'),    # Pushya
    8:  ('Cat',      'neutral'),    # Ashlesha
    9:  ('Rat',      'dominant'),   # Magha
    10: ('Rat',      'dominant'),   # Purva Phalguni
    11: ('Cow',      'loyal'),      # Uttara Phalguni
    12: ('Buffalo',  'dominant'),   # Hasta
    13: ('Tiger',    'aggressive'), # Chitra
    14: ('Buffalo',  'dominant'),   # Swati
    15: ('Tiger',    'aggressive'), # Vishakha
    16: ('Deer',     'sensitive'),  # Anuradha
    17: ('Deer',     'sensitive'),  # Jyeshtha
    18: ('Dog',      'loyal'),      # Mula
    19: ('Monkey',   'neutral'),    # Purva Ashadha
    20: ('Monkey',   'neutral'),    # Uttara Ashadha
    21: ('Monkey',   'neutral'),    # Shravana
    22: ('Lion',     'aggressive'), # Dhanishtha
    23: ('Horse',    'dominant'),   # Shatabhisha
    24: ('Lion',     'aggressive'), # Purva Bhadrapada
    25: ('Cow',      'loyal'),      # Uttara Bhadrapada
    26: ('Elephant', 'sensitive'),  # Revati
}

BENEFICS  = {'Jupiter', 'Venus', 'Moon', 'Mercury'}
MALEFICS  = {'Saturn', 'Mars', 'Rahu', 'Ketu', 'Sun'}
MARAKA_LORDS_FOR_LAGNA = {
    # lagna_sign: [2nd lord, 7th lord] — both are maraka
    # 7th lord is our focus
    0:  'Venus',    # Aries  → 7th lord is Libra/Venus
    1:  'Mars',     # Taurus → 7th lord is Scorpio/Mars
    2:  'Jupiter',  # Gemini → 7th lord is Sag/Jupiter
    3:  'Saturn',   # Cancer → 7th lord is Cap/Saturn
    4:  'Saturn',   # Leo    → 7th lord is Aquarius/Saturn
    5:  'Jupiter',  # Virgo  → 7th lord is Pisces/Jupiter
    6:  'Mars',     # Libra  → 7th lord is Aries/Mars
    7:  'Venus',    # Scorpio→ 7th lord is Taurus/Venus
    8:  'Mercury',  # Sag    → 7th lord is Gemini/Mercury
    9:  'Moon',     # Cap    → 7th lord is Cancer/Moon
    10: 'Sun',      # Aquarius→ 7th lord is Leo/Sun
    11: 'Mercury',  # Pisces → 7th lord is Virgo/Mercury
}


# ════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════════
def _house_of(planet_lon: float, lagna_lon: float) -> int:
    """Whole Sign house 1-12."""
    return ((int(planet_lon / 30) - int(lagna_lon / 30)) % 12) + 1

def _sign_of(lon: float) -> int:
    return int(lon / 30) % 12

def _naksh_of(lon: float) -> int:
    return int(lon / (360 / 27)) % 27

def _d1_dignity(planet: str, lon: float) -> str:
    sign = _sign_of(lon)
    if _EXALT.get(planet) == sign:   return 'Exalted'
    if _DEBIL.get(planet) == sign:   return 'Debilitated'
    if sign in _OWN.get(planet, []): return 'Own'
    return 'Neutral'

def _d9_dignity(planet: str, d9_sign: int) -> str:
    if _EXALT.get(planet) == d9_sign:    return 'Exalted'
    if _DEBIL.get(planet) == d9_sign:    return 'Debilitated'
    if d9_sign in _OWN.get(planet, []):  return 'Own'
    return 'Neutral'

def _is_afflicted(planet: str, planets: dict, lagna_lon: float) -> bool:
    """
    A planet is afflicted if:
    - Rahu or Saturn conjuncts it (same house, within 10°) or aspects it
    - Rahu aspects by conjunction; Saturn aspects 3rd, 7th, 10th from its position
    """
    p_lon = planets.get(planet)
    if p_lon is None: return False
    p_sign = _sign_of(p_lon)
    for afflicting in ('Rahu', 'Saturn'):
        if afflicting not in planets or afflicting == planet: continue
        a_sign = _sign_of(planets[afflicting])
        # Conjunction (same sign)
        if a_sign == p_sign:
            return True
        # Saturn special aspects: 3, 7, 10
        if afflicting == 'Saturn':
            for asp in (3, 7, 10):
                if (a_sign + asp - 1) % 12 == p_sign:
                    return True
        # Rahu aspects: 5, 9 (Trine aspects in some traditions) + 7th
        if afflicting == 'Rahu':
            for asp in (5, 7, 9):
                if (a_sign + asp - 1) % 12 == p_sign:
                    return True
    return False


# ════════════════════════════════════════════════════════════════
# RULE 1 — NAVAMSHA STRENGTH FLIP
# D9 has 1.5x weightage over D1. Final strength derived from both.
# ════════════════════════════════════════════════════════════════
def rule1_navamsha_flip(
    planet: str,
    d1_lon: float,
    d9_sign: int,
) -> dict:
    """
    Rule 1: D9 (Navamsha) is the final word on planetary strength.

    Scoring:
      D1 dignity  → weight 1.0
      D9 dignity  → weight 1.5  (D9 is the fruit; D1 is only the seed)

    Dignity points:
      Exalted  → +2
      Own      → +1
      Neutral  → 0
      Debilitated → -2

    Combined score determines final verdict:
      ≥ 2   → Strong/Benefic
      0–1.9 → Moderate
      < 0   → Weak/Malefic

    Special Override Cases:
      Exalted D1 + Debilitated D9 → FORCED Weak   (Neecha cancels the fruit)
      Debilitated D1 + Exalted D9 → FORCED Strong  (Neecha Bhanga — D9 rescues)
    """
    DIG_SCORE = {'Exalted': 2, 'Own': 1, 'Neutral': 0, 'Debilitated': -2}

    d1_dig = _d1_dignity(planet, d1_lon)
    d9_dig = _d9_dignity(planet, d9_sign)

    d1_score = DIG_SCORE[d1_dig]
    d9_score = DIG_SCORE[d9_dig]

    # Hard override cases
    if d1_dig == 'Exalted' and d9_dig == 'Debilitated':
        final_strength = 'Weak/Malefic'
        note = (
            f'{planet} is Exalted in D1 (strong seed) but Debilitated in D9 '
            f'(rotten fruit). The planet cannot deliver its promise. '
            f'Results will fall short despite apparent strength.'
        )
        combined = -2.0

    elif d1_dig == 'Debilitated' and d9_dig == 'Exalted':
        final_strength = 'Strong/Benefic'
        note = (
            f'{planet} is Debilitated in D1 (neecha) but Exalted in D9 — '
            f'this is Neecha Bhanga (cancelled debilitation). '
            f'The planet rises from adversity and delivers exceptional results, '
            f'especially in the second half of life.'
        )
        combined = 3.0

    else:
        # Weighted combination
        combined = d1_score * 1.0 + d9_score * 1.5
        if combined >= 2:    final_strength = 'Strong/Benefic'
        elif combined >= 0:  final_strength = 'Moderate'
        else:                final_strength = 'Weak/Malefic'
        note = (
            f'{planet}: D1={d1_dig}({d1_score:+.0f}) × 1.0 + '
            f'D9={d9_dig}({d9_score:+.0f}) × 1.5 = {combined:+.1f} → {final_strength}'
        )

    return {
        'planet':         planet,
        'd1_dignity':     d1_dig,
        'd9_dignity':     d9_dig,
        'd1_score':       d1_score,
        'd9_score':       d9_score,
        'combined_score': combined,
        'final_strength': final_strength,
        'note':           note,
        'rule':           'Rule 1 — Navamsha Strength Flip',
    }


# ════════════════════════════════════════════════════════════════
# RULE 2 — SETTING HOUSE (7th) PENALTY
# ════════════════════════════════════════════════════════════════
def rule2_seventh_house_penalty(
    planet: str,
    planet_lon: float,
    lagna_lon: float,
    yoga_involves_7th_lord: bool = False,
) -> dict:
    """
    Rule 2: The 7th house is the house of 'setting' — every planet there loses 25%.

    Returns:
      applied       : bool — whether penalty was triggered
      penalty_pct   : int  — 0 or 25 (positive planets) / 20 (yoga dilution)
      yoga_diluted  : bool — True if 7th lord taints a Raj Yoga
      malefic_tinge : str  — interpretation note for benefics in 7th
      note          : str  — full explanation
    """
    house = _house_of(planet_lon, lagna_lon)
    in_7th = (house == 7)

    result = {
        'planet':        planet,
        'house':         house,
        'in_7th':        in_7th,
        'penalty_pct':   0,
        'yoga_diluted':  False,
        'malefic_tinge': '',
        'rule':          'Rule 2 — Setting House Penalty',
        'note':          '',
    }

    if not in_7th:
        result['note'] = f'{planet} is in house {house}, not the 7th. No penalty.'
        return result

    # Core 25% penalty
    result['penalty_pct'] = 25
    base_note = (
        f'{planet} occupies the 7th house — the house of "setting." '
        f'Output score reduced by 25%. The planet gives results, '
        f'but only partially or after compromise.'
    )

    # Malefic tinge for benefics
    if planet in BENEFICS:
        result['malefic_tinge'] = (
            f'{planet} is a Great Benefic in the 7th. It still gives good results '
            f'but with a malefic tinge — relationships may fulfil on the surface '
            f'but leave an inner sense of incompleteness or compromise.'
        )

    # Raj Yoga contamination
    if yoga_involves_7th_lord:
        result['yoga_diluted']  = True
        result['penalty_pct']  += 20   # total 45% penalty if yoga involved
        base_note += (
            f'\n  ⚠ Raj Yoga Contamination: The 7th lord (Maraka) is involved in this '
            f'Raj Yoga. The yoga\'s peak performance is reduced by an additional 20% '
            f'(Maraka kills the full expression of the combination).'
        )

    result['note'] = base_note
    return result


def apply_7th_penalties_to_yogas(
    yogas: list,
    planets: dict,
    lagna_lon: float,
) -> list:
    """
    Scan detected yogas and apply 20% dilution wherever the 7th lord participates.
    Adds 'diluted' and 'dilution_reason' keys to affected yoga dicts.

    The 7th lord for any lagna is: MARAKA_LORDS_FOR_LAGNA[lagna_sign]
    """
    lagna_sign  = _sign_of(lagna_lon)
    seventh_lord = MARAKA_LORDS_FOR_LAGNA.get(lagna_sign, '')

    updated = []
    for yoga in yogas:
        yoga = dict(yoga)   # don't mutate original
        yoga_name = yoga.get('name', '')

        # Check if 7th lord is in 7th (double setting)
        seventh_lord_in_7th = False
        if seventh_lord and seventh_lord in planets:
            sl_house = _house_of(planets[seventh_lord], lagna_lon)
            seventh_lord_in_7th = (sl_house == 7)

        # Check if any yoga planet is the 7th lord — crude heuristic via name matching
        lord_in_yoga = seventh_lord and seventh_lord.lower() in yoga_name.lower()

        if lord_in_yoga or seventh_lord_in_7th:
            yoga['diluted'] = True
            yoga['strength'] = yoga.get('strength', 'Powerful') + ' (Diluted)'
            yoga['dilution_reason'] = (
                f'The 7th lord ({seventh_lord} / Maraka) participates in or '
                f'shares the house of this yoga. Peak results are diminished by ~20%. '
                f'The yoga gives success, but rarely without personal cost or '
                f'compromise in relationships.'
            )
        else:
            yoga['diluted'] = False

        updated.append(yoga)

    return updated


# ════════════════════════════════════════════════════════════════
# RULE 3 — YONI HIERARCHY (Relationship & Sexuality Logic)
# ════════════════════════════════════════════════════════════════
def rule3_yoni_hierarchy(
    planets: dict,
    lagna_lon: float,
) -> dict:
    """
    Rule 3: Four-layer hierarchy for relationship personality assessment.

    Layer 1 — Lagna Nakshatra   : Physical capacity, raw animalistic drive
    Layer 2 — Moon Nakshatra    : Mental expectation, emotional fulfillment need
    Layer 3 — Venus Nakshatra   : Sexual desire, aesthetic preferences
    Layer 4 — 7th Lord Nakshatra: What the partner actually provides in reality

    Affliction Flip:
      If an animal is 'loyal' (nature) but its planet is afflicted by Rahu/Saturn
      → flip to 'Extremely Unreliable / Cheating tendency'
    """
    lagna_sign    = _sign_of(lagna_lon)
    seventh_lord  = MARAKA_LORDS_FOR_LAGNA.get(lagna_sign, '')

    # Get nakshatra indices
    lagna_nk_idx  = _naksh_of(lagna_lon)
    moon_nk_idx   = _naksh_of(planets.get('Moon', 0))
    venus_nk_idx  = _naksh_of(planets.get('Venus', 0))
    sl_lon        = planets.get(seventh_lord, 0)
    sl_nk_idx     = _naksh_of(sl_lon)

    def layer_result(label, planet_name, nk_idx, lon):
        animal, nature = _YONI.get(nk_idx, ('Unknown', 'neutral'))
        nk_name        = NAKSH[nk_idx]
        afflicted      = _is_afflicted(planet_name, planets, lagna_lon) if planet_name else False

        # Affliction flip for loyal animals
        if afflicted and nature == 'loyal':
            flipped_nature = 'Extremely Unreliable / Cheating tendency'
            flip_note      = (
                f'WARNING: {nk_name} nakshatra is naturally loyal ({animal}) '
                f'but {planet_name} is afflicted by Rahu/Saturn. '
                f'The loyal nature is inverted — expect betrayal or emotional unavailability.'
            )
        else:
            flipped_nature = nature
            flip_note      = ''

        descriptions = {
            'loyal':      f'Deeply loyal, seeks long-term commitment. '
                          f'The {animal} energy makes them protective and consistent.',
            'dominant':   f'Dominant, assertive in desire. '
                          f'The {animal} energy drives strong physical/sexual appetite.',
            'aggressive': f'Passionate but volatile. '
                          f'The {animal} energy creates intense chemistry with risk of conflict.',
            'sensitive':  f'Emotionally delicate, needs reassurance. '
                          f'The {animal} energy seeks tenderness over intensity.',
            'neutral':    f'Adaptable, comfortable with different dynamics. '
                          f'The {animal} energy is flexible and non-demanding.',
        }
        desc = descriptions.get(flipped_nature,
               f'{flipped_nature} — non-standard response to relationship dynamics.')

        return {
            'layer':      label,
            'planet':     planet_name,
            'nakshatra':  nk_name,
            'nk_index':   nk_idx,
            'animal':     animal,
            'nature':     flipped_nature,
            'afflicted':  afflicted,
            'flip_note':  flip_note,
            'description':desc,
        }

    layers = [
        layer_result('Physical Capacity (Lagna)',        None,          lagna_nk_idx,  lagna_lon),
        layer_result('Mental Expectation (Moon)',        'Moon',        moon_nk_idx,   planets.get('Moon', 0)),
        layer_result('Sexual Desire (Venus)',            'Venus',       venus_nk_idx,  planets.get('Venus', 0)),
        layer_result('Partner Reality (7th Lord)',       seventh_lord,  sl_nk_idx,     sl_lon),
    ]

    # Harmony analysis between layers
    animals   = [l['animal']  for l in layers]
    natures   = [l['nature']  for l in layers]
    conflicts = []
    harmonies = []

    # Key conflicts: Physical vs Partner, Mental vs Sexual
    if layers[0]['animal'] == layers[3]['animal']:
        harmonies.append('Physical drive matches what partner provides — natural alignment.')
    else:
        conflicts.append(
            f"Physical drive ({layers[0]['animal']}) differs from partner reality "
            f"({layers[3]['animal']}) — there may be a chronic feeling of unfulfillment."
        )

    if layers[1]['nature'] == layers[2]['nature']:
        harmonies.append('Mental expectations match sexual desires — internal consistency.')
    else:
        conflicts.append(
            f"Mental expectation ({layers[1]['nature']}) clashes with sexual desire "
            f"({layers[2]['nature']}) — inner conflict about what they want vs what they need."
        )

    flip_warnings = [l['flip_note'] for l in layers if l['flip_note']]

    return {
        'layers':         layers,
        'harmonies':      harmonies,
        'conflicts':      conflicts,
        'flip_warnings':  flip_warnings,
        'seventh_lord':   seventh_lord,
        'rule':           'Rule 3 — Yoni Hierarchy',
        'summary': (
            f"Physical: {layers[0]['animal']} ({layers[0]['nature']}) · "
            f"Mental: {layers[1]['animal']} ({layers[1]['nature']}) · "
            f"Desire: {layers[2]['animal']} ({layers[2]['nature']}) · "
            f"Partner gives: {layers[3]['animal']} ({layers[3]['nature']})"
        ),
    }


# ════════════════════════════════════════════════════════════════
# RULE 4 — 10th-7th CAREER LINK
# ════════════════════════════════════════════════════════════════
def rule4_career_7th_link(
    planets: dict,
    lagna_lon: float,
) -> dict:
    """
    Rule 4: The 7th house acts as 'Love for Society' in career analysis.

    The 10th-7th Link determines:
    1. Whether social work / public-facing roles are karmically indicated
    2. Whether staying local will suppress the native's Raj Yogas
       (7th > Lagna → foreign/outside market mandate)

    7th lord power assessment:
      - In Kendra (1/4/7/10)  → strong
      - In Trikona (1/5/9)    → strong
      - Exalted / Own         → strong
      Strong 7th lord in Kendra/Trikona → Social Work / NGO / Consulting signal
    """
    lagna_sign    = _sign_of(lagna_lon)
    seventh_lord  = MARAKA_LORDS_FOR_LAGNA.get(lagna_sign, '')

    # 7th lord strength
    sl_lon         = planets.get(seventh_lord, 0)
    sl_house       = _house_of(sl_lon, lagna_lon)
    sl_sign        = _sign_of(sl_lon)
    sl_exalted     = (_EXALT.get(seventh_lord) == sl_sign)
    sl_own         = (sl_sign in _OWN.get(seventh_lord, []))
    sl_in_kendra   = sl_house in (1, 4, 7, 10)
    sl_in_trikona  = sl_house in (1, 5, 9)
    sl_strong      = (sl_exalted or sl_own) and (sl_in_kendra or sl_in_trikona)

    # Lagna strength (basic: count of strong planets in lagna house)
    lagna_planets  = [
        p for p in planets
        if _house_of(planets[p], lagna_lon) == 1
        and p not in ('Rahu', 'Ketu')
    ]
    lagna_lord_sign = _sign_of(lagna_lon)  # lagna lord = lord of lagna sign
    lagna_lord_planet = _RASHI_LORD.get(lagna_sign, '')
    ll_lon         = planets.get(lagna_lord_planet, 0)
    ll_house       = _house_of(ll_lon, lagna_lon)
    ll_strong      = ll_house in (1, 4, 5, 7, 9, 10) or (
        _sign_of(ll_lon) == _EXALT.get(lagna_lord_planet) or
        _sign_of(ll_lon) in _OWN.get(lagna_lord_planet, [])
    )

    # 7th house strength vs Lagna house strength
    # Simple metric: 7th lord in angle/trine is "strong 7th"
    # Lagna lord in angle/trine = "strong lagna"
    seventh_stronger_than_lagna = sl_strong and not ll_strong

    # NGO / Social Work signal
    ngo_signal = sl_strong and (sl_in_kendra or sl_in_trikona)

    # Build career signals
    signals = []

    if ngo_signal:
        signals.append({
            'type':    'NGO / Public-Facing Consulting',
            'strength':'High',
            'detail':  (
                f'7th lord ({seventh_lord}) is powerful and placed in a '
                f'{"Kendra" if sl_in_kendra else "Trikona"} (house {sl_house}). '
                f'The native has a karmic mandate for social work, NGOs, '
                f'public service, or consulting where they serve large numbers of people. '
                f'The 7th house\'s "love for society" is activated.'
            ),
        })

    if seventh_stronger_than_lagna:
        signals.append({
            'type':    'Foreign / Outside Market Mandate',
            'strength':'Critical',
            'detail':  (
                f'The 7th house energy overwhelms the Lagna. '
                f'Staying in the birthplace or home market will suppress Raj Yogas. '
                f'The native MUST seek clients, recognition, or business in outside '
                f'markets — geographically distant, online, or international. '
                f'Local roots "starve" the potential. The further from origin, the more success.'
            ),
        })

    if not signals:
        signals.append({
            'type':    'Standard Career Path',
            'strength':'Moderate',
            'detail':  (
                f'7th lord ({seventh_lord}) in house {sl_house} — '
                f'no dominant 7th-career activation. Standard Raj Yoga '
                f'career interpretation applies. 10th house and its lord '
                f'are primary career indicators.'
            ),
        })

    return {
        'seventh_lord':             seventh_lord,
        'seventh_lord_house':       sl_house,
        'seventh_lord_strong':      sl_strong,
        'seventh_in_kendra':        sl_in_kendra,
        'seventh_in_trikona':       sl_in_trikona,
        'lagna_lord':               lagna_lord_planet,
        'seventh_stronger_than_lagna': seventh_stronger_than_lagna,
        'ngo_signal':               ngo_signal,
        'career_signals':           signals,
        'rule':                     'Rule 4 — 10th-7th Career Link',
    }


# ════════════════════════════════════════════════════════════════
# RULE 5 — THE SMOKE CONDITION (Saturn/Rahu in 7th)
# ════════════════════════════════════════════════════════════════
def rule5_smoke_condition(
    planets: dict,
    lagna_lon: float,
) -> dict:
    """
    Rule 5: Saturn or Rahu in the 7th house triggers 'Late Recognition.'

    The native's contributions will be systematically undervalued by society
    until age 40-45. The 'smoke' of Saturn/Rahu obscures their true worth
    during the first half of life.

    Activation: Saturn in 7th OR Rahu in 7th (or both)
    Message: Do not seek validation now — the smoke clears after 40-45.

    Additional nuance:
    - Both Saturn AND Rahu in 7th → amplified condition (smoke clears ~45-50)
    - Saturn alone               → methodical undervaluation (clears ~40)
    - Rahu alone                 → erratic misrecognition (clears ~42-45)
    """
    saturn_house = _house_of(planets.get('Saturn', 0), lagna_lon) if 'Saturn' in planets else 0
    rahu_house   = _house_of(planets.get('Rahu', 0),   lagna_lon) if 'Rahu'   in planets else 0

    saturn_in_7th = (saturn_house == 7)
    rahu_in_7th   = (rahu_house   == 7)

    activated = saturn_in_7th or rahu_in_7th

    if not activated:
        return {
            'activated':       False,
            'planets_in_7th':  [],
            'clearing_age':    None,
            'message':         '',
            'guidance':        '',
            'rule':            'Rule 5 — Smoke Condition',
            'note':            'Neither Saturn nor Rahu in the 7th house. No smoke condition.',
        }

    planets_in_7th = []
    if saturn_in_7th: planets_in_7th.append('Saturn')
    if rahu_in_7th:   planets_in_7th.append('Rahu')

    # Determine clearing age
    if saturn_in_7th and rahu_in_7th:
        clearing_age = '45-50'
        severity     = 'Severe'
        smoke_desc   = (
            'Both Saturn and Rahu occupy the 7th house — maximum smoke condition. '
            'Society will consistently misread, undervalue, or ignore the native\'s contributions. '
            'This is amplified if Saturn is also the lagna lord or rules a significant house.'
        )
    elif saturn_in_7th:
        clearing_age = '40-42'
        severity     = 'Significant'
        smoke_desc   = (
            'Saturn in the 7th creates methodical, slow undervaluation. '
            'Others in the native\'s field will receive recognition they don\'t deserve '
            'while the native\'s work is overlooked or taken for granted. '
            'This is Saturn\'s teaching: build without expectation of applause.'
        )
    else:
        clearing_age = '42-45'
        severity     = 'Moderate'
        smoke_desc   = (
            'Rahu in the 7th creates erratic misrecognition — the native may receive '
            'brief flashes of recognition followed by confusion or misrepresentation. '
            'Others project their own desires onto the native, obscuring authentic contribution.'
        )

    message  = (
        f'Your contributions will be undervalued by society until age {clearing_age}. '
        f'The "smoke" of {"/".join(planets_in_7th)} in your 7th house obscures '
        f'your true worth during the first half of life. '
        f'This is not a permanent condition — it is a test of whether you build '
        f'for the work itself or for external validation.'
    )

    guidance = (
        f'Do not seek validation now. The smoke clears after {clearing_age}. '
        f'Focus on the quality and depth of your output — not the applause. '
        f'Those who persist through the smoke phase emerge as genuine authorities '
        f'rather than fabricated ones. Your late-life recognition will be proportional '
        f'to how honestly you worked during the obscured years.'
    )

    return {
        'activated':       True,
        'planets_in_7th':  planets_in_7th,
        'severity':        severity,
        'clearing_age':    clearing_age,
        'smoke_desc':      smoke_desc,
        'message':         message,
        'guidance':        guidance,
        'rule':            'Rule 5 — Smoke Condition',
    }


# ════════════════════════════════════════════════════════════════
# MASTER CLASS — FULL ANALYSIS
# ════════════════════════════════════════════════════════════════
class JyogiLogic:
    """
    Apply all 5 Jyogi Logic rules to a computed chart.

    Input:
        planets    : dict {planet_name: sidereal_longitude}  (from vedic_engine.get_all_planets)
        lagna_lon  : float — sidereal Lagna longitude
        d9         : dict {planet_name: {'nav_sign': int, ...}} (from vedic_engine.calc_navamsha)

    Usage:
        from jyogi_logic import JyogiLogic
        logic  = JyogiLogic(planets, lagna_lon, d9)
        result = logic.full_analysis()
        report = logic.narrative_report(result)
    """

    def __init__(self, planets: dict, lagna_lon: float, d9: dict):
        self.planets   = {k: v for k, v in planets.items() if k != 'jd'}
        self.lagna_lon = lagna_lon
        self.d9        = d9

    def full_analysis(
        self,
        mode: str = 'general',   # 'general' | 'relationship' | 'career'
        yogas: Optional[list] = None,
    ) -> dict:
        """
        Run all applicable rules and return structured results.

        mode: controls which rules are emphasised in the narrative
        """
        PLANETS_TO_SCORE = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']

        # ── Rule 1: Navamsha Flip for all planets ──────────────
        r1_results = {}
        for p in PLANETS_TO_SCORE:
            if p not in self.planets: continue
            d9_sign = self.d9.get(p, {}).get('nav_sign', 0)
            r1_results[p] = rule1_navamsha_flip(p, self.planets[p], d9_sign)

        # ── Rule 2: 7th house penalty for each planet ──────────
        r2_results = {}
        for p in PLANETS_TO_SCORE:
            if p not in self.planets: continue
            r2_results[p] = rule2_seventh_house_penalty(
                p, self.planets[p], self.lagna_lon
            )
        # Planets actually in 7th
        planets_in_7th = [p for p, r in r2_results.items() if r['in_7th']]

        # ── Rule 2b: Yoga dilution ─────────────────────────────
        r2_yogas = []
        if yogas:
            r2_yogas = apply_7th_penalties_to_yogas(
                yogas, self.planets, self.lagna_lon
            )

        # ── Rule 3: Yoni Hierarchy (always computed) ───────────
        r3 = rule3_yoni_hierarchy(self.planets, self.lagna_lon)

        # ── Rule 4: Career 7th Link ────────────────────────────
        r4 = rule4_career_7th_link(self.planets, self.lagna_lon)

        # ── Rule 5: Smoke Condition ────────────────────────────
        r5 = rule5_smoke_condition(self.planets, self.lagna_lon)

        # ── Composite planet score (strength + penalty) ────────
        composite = {}
        for p in PLANETS_TO_SCORE:
            if p not in r1_results: continue
            r1 = r1_results[p]
            r2 = r2_results.get(p, {})
            base_score = r1['combined_score']
            penalty    = r2.get('penalty_pct', 0) / 100
            adj_score  = base_score * (1 - penalty)
            composite[p] = {
                'base_score':     round(base_score, 2),
                'penalty_pct':    r2.get('penalty_pct', 0),
                'adjusted_score': round(adj_score, 2),
                'd1_dignity':     r1['d1_dignity'],
                'd9_dignity':     r1['d9_dignity'],
                'final_strength': r1['final_strength'],
                'in_7th':         r2.get('in_7th', False),
                'malefic_tinge':  r2.get('malefic_tinge', ''),
            }

        return {
            'mode':             mode,
            'rule1_navamsha':   r1_results,
            'rule2_seventh':    r2_results,
            'rule2_yogas':      r2_yogas,
            'planets_in_7th':   planets_in_7th,
            'rule3_yoni':       r3,
            'rule4_career':     r4,
            'rule5_smoke':      r5,
            'composite_scores': composite,
            'lagna_sign':       RASHIS[_sign_of(self.lagna_lon)],
            'seventh_lord':     MARAKA_LORDS_FOR_LAGNA.get(_sign_of(self.lagna_lon), ''),
        }

    def narrative_report(self, result: dict) -> str:
        """
        Generate a human-readable narrative from full_analysis() output.
        Suitable for injecting directly into the AI insight prompt.
        """
        lines = ['═' * 60, '  JYOGI LOGIC — CHART INTERPRETATION LAYER', '═' * 60]

        # Composite scores
        lines.append('\n▸ PLANETARY STRENGTH (D1 × D9 Weighted)')
        for p, c in result['composite_scores'].items():
            strength_icon = '⬆' if 'Strong' in c['final_strength'] else (
                '⬇' if 'Weak' in c['final_strength'] else '→')
            penalty_str = f' [-{c["penalty_pct"]}% 7th]' if c['in_7th'] else ''
            lines.append(
                f"  {p:<10} D1:{c['d1_dignity']:<12} D9:{c['d9_dignity']:<12} "
                f"Score:{c['adjusted_score']:>+5.1f}{penalty_str}  {strength_icon} {c['final_strength']}"
            )

        # Neecha Bhanga highlights
        nb_planets = [
            p for p, r in result['rule1_navamsha'].items()
            if r['d1_dignity'] == 'Debilitated' and r['d9_dignity'] == 'Exalted'
        ]
        strength_flip = [
            p for p, r in result['rule1_navamsha'].items()
            if r['d1_dignity'] == 'Exalted' and r['d9_dignity'] == 'Debilitated'
        ]
        if nb_planets:
            lines.append(f'\n  ✦ Neecha Bhanga: {", ".join(nb_planets)} — rises from debilitation via D9')
        if strength_flip:
            lines.append(f'  ⚠ Strength Flip: {", ".join(strength_flip)} — exalted in D1 but fruit is weak (D9 debilitated)')

        # 7th house planets
        if result['planets_in_7th']:
            lines.append(f"\n▸ 7TH HOUSE (SETTING) PLANETS: {', '.join(result['planets_in_7th'])}")
            lines.append("  Each loses 25% of positive output. Even benefics carry a malefic tinge here.")
            for p in result['planets_in_7th']:
                tinge = result['rule2_seventh'].get(p, {}).get('malefic_tinge', '')
                if tinge: lines.append(f"  {p}: {tinge}")

        # Yoga dilution
        diluted = [y for y in result['rule2_yogas'] if y.get('diluted')]
        if diluted:
            lines.append(f"\n▸ DILUTED YOGAS (Maraka 7th Lord Contamination):")
            for y in diluted:
                lines.append(f"  {y['name']} — {y.get('dilution_reason','')[:120]}…")

        # Smoke condition
        if result['rule5_smoke']['activated']:
            r5 = result['rule5_smoke']
            lines.append(f"\n▸ SMOKE CONDITION ({r5['severity'].upper()})")
            lines.append(f"  {r5['message']}")
            lines.append(f"  Guidance: {r5['guidance']}")

        # Career signals
        if result['rule4_career']['career_signals']:
            lines.append(f"\n▸ CAREER SIGNALS (10th-7th Link)")
            for sig in result['rule4_career']['career_signals']:
                lines.append(f"  [{sig['strength']}] {sig['type']}")
                lines.append(f"  {sig['detail'][:160]}…")

        # Relationship layer
        r3 = result['rule3_yoni']
        lines.append(f"\n▸ RELATIONSHIP HIERARCHY (Yoni Logic)")
        for layer in r3['layers']:
            flip  = ' ⚠ AFFLICTION FLIP' if layer['flip_note'] else ''
            lines.append(
                f"  {layer['layer']:<35} {layer['nakshatra']:<20} "
                f"{layer['animal']:<10} {layer['nature']}{flip}"
            )
        if r3['conflicts']:
            lines.append("  Conflicts:")
            for c in r3['conflicts']: lines.append(f"    ⚡ {c}")
        if r3['harmonies']:
            lines.append("  Harmonies:")
            for h in r3['harmonies']: lines.append(f"    ✓ {h}")
        if r3['flip_warnings']:
            lines.append("  ⚠ AFFLICTION WARNINGS:")
            for w in r3['flip_warnings']: lines.append(f"    {w}")

        lines.append('\n' + '═' * 60)
        return '\n'.join(lines)


# ════════════════════════════════════════════════════════════════
# TESTS
# ════════════════════════════════════════════════════════════════
def run_tests():
    """
    Verify all 5 rules with TC1: DOB 19 Mar 1980, Jajpur, Capricorn lagna.
    Known positions: Saturn in Leo (4th sign), Lagna Capricorn (9th sign).
    """
    print("Running Jyogi Logic Rule Tests…\n")
    errors = []

    # Simulate chart data (Capricorn lagna, Saturn in Leo 8th house)
    lagna_lon = 282.27   # Capricorn 12°16'
    planets   = {
        'Sun':     334.93,   # Pisces   — house 3
        'Moon':      4.75,   # Aries    — house 4
        'Mars':    124.30,   # Leo      — house 8 (retrograde)
        'Mercury': 314.00,   # Aquarius — house 2
        'Jupiter': 128.83,   # Leo      — house 8
        'Venus':    19.78,   # Aries    — house 4
        'Saturn':  149.68,   # Leo      — house 8 (retrograde)
        'Rahu':    125.43,   # Leo      — house 8
        'Ketu':    305.43,   # Aquarius — house 2
    }
    # Minimal D9 (computed correctly for actual positions)
    d9 = {
        'Sun':     {'nav_sign': 4},  # Leo
        'Moon':    {'nav_sign': 0},  # Aries
        'Mars':    {'nav_sign': 9},  # Capricorn (exalted)
        'Mercury': {'nav_sign': 5},  # Virgo (own)
        'Jupiter': {'nav_sign': 3},  # Cancer (exalted)
        'Venus':   {'nav_sign': 7},  # Scorpio
        'Saturn':  {'nav_sign': 0},  # Aries (debilitated — flip from neutral D1)
    }

    print("─── Rule 1: Navamsha Flip ─────────────────────────────────")
    # Saturn: D1=Neutral (Leo), D9=Debilitated (Aries) → should be Weak
    r1_sat = rule1_navamsha_flip('Saturn', 149.68, 0)
    ok = r1_sat['final_strength'] == 'Weak/Malefic'
    print(f"  Saturn D1=Neutral + D9=Debilitated → {r1_sat['final_strength']}  {'✅' if ok else '❌ expected Weak'}")
    if not ok: errors.append(f"Rule1 Saturn: {r1_sat['final_strength']}")

    # Mars: D1=Neutral (Leo), D9=Capricorn (exalted) → should be Strong
    r1_mars = rule1_navamsha_flip('Mars', 124.30, 9)
    ok2 = r1_mars['final_strength'] == 'Strong/Benefic'
    print(f"  Mars D1=Neutral + D9=Exalted     → {r1_mars['final_strength']}  {'✅' if ok2 else '❌ expected Strong'}")
    if not ok2: errors.append(f"Rule1 Mars: {r1_mars['final_strength']}")

    # Jupiter D1=Neutral (Leo), D9=Cancer (exalted) → Strong
    r1_jup = rule1_navamsha_flip('Jupiter', 128.83, 3)
    ok3 = r1_jup['final_strength'] == 'Strong/Benefic'
    print(f"  Jupiter D1=Neutral + D9=Exalted  → {r1_jup['final_strength']}  {'✅' if ok3 else '❌'}")
    if not ok3: errors.append(f"Rule1 Jupiter: {r1_jup['final_strength']}")

    # Neecha Bhanga test: Venus debil in D1 (Virgo→0 but not our case)
    r1_nb = rule1_navamsha_flip('Venus', 155.0, 11)  # D1=Virgo(debil), D9=Pisces(exalt)
    ok4 = r1_nb['final_strength'] == 'Strong/Benefic'
    print(f"  Venus Debil D1 + Exalt D9 (Neecha Bhanga) → {r1_nb['final_strength']}  {'✅' if ok4 else '❌'}")
    if not ok4: errors.append(f"Rule1 Neecha Bhanga: {r1_nb['final_strength']}")

    print("\n─── Rule 2: 7th House Penalty ─────────────────────────────")
    # No planets in 7th for this chart (7th = Cancer/house 7 = lon 180-210)
    # Test by putting Moon in 7th manually
    test_7th_lon = 105.0   # Cancer = sign 3 = house 7 from Capricorn lagna (Capricorn=sign 9)
    r2_moon = rule2_seventh_house_penalty('Moon', test_7th_lon, lagna_lon)
    ok5 = r2_moon['penalty_pct'] == 25 and r2_moon['in_7th']
    print(f"  Moon in 7th → penalty={r2_moon['penalty_pct']}%  {'✅' if ok5 else '❌ expected 25%'}")
    if not ok5: errors.append(f"Rule2 penalty: {r2_moon['penalty_pct']}")

    r2_saturn = rule2_seventh_house_penalty('Saturn', 149.68, lagna_lon)
    ok6 = not r2_saturn['in_7th'] and r2_saturn['penalty_pct'] == 0
    print(f"  Saturn in 8th (not 7th) → penalty={r2_saturn['penalty_pct']}%  {'✅' if ok6 else '❌ expected 0%'}")
    if not ok6: errors.append(f"Rule2 no-penalty: {r2_saturn['penalty_pct']}")

    print("\n─── Rule 3: Yoni Hierarchy ─────────────────────────────────")
    r3 = rule3_yoni_hierarchy(planets, lagna_lon)
    ok7 = len(r3['layers']) == 4
    print(f"  4 layers computed: {'✅' if ok7 else '❌'}")
    for layer in r3['layers']:
        print(f"  {layer['layer'][:30]:<32} {layer['nakshatra']:<20} {layer['animal']} ({layer['nature']})")
    if not ok7: errors.append("Rule3: wrong layer count")

    print("\n─── Rule 4: Career 7th Link ────────────────────────────────")
    r4 = rule4_career_7th_link(planets, lagna_lon)
    ok8 = bool(r4['career_signals'])
    print(f"  7th lord: {r4['seventh_lord']}  house:{r4['seventh_lord_house']}  strong:{r4['seventh_lord_strong']}")
    for sig in r4['career_signals']:
        print(f"  [{sig['strength']}] {sig['type']}")
    if not ok8: errors.append("Rule4: no signals")

    print("\n─── Rule 5: Smoke Condition ────────────────────────────────")
    # Saturn in 8th, Rahu in 8th for this chart — NOT in 7th
    r5_off = rule5_smoke_condition(planets, lagna_lon)
    ok9 = not r5_off['activated']
    print(f"  Saturn in 8th, Rahu in 8th → activated={r5_off['activated']}  {'✅ no smoke' if ok9 else '❌'}")
    if not ok9: errors.append("Rule5: false positive activation")

    # Force test with Rahu in 7th
    planets_test = dict(planets); planets_test['Rahu'] = 105.0  # Cancer=sign3=house7 from Capricorn
    r5_on = rule5_smoke_condition(planets_test, lagna_lon)
    ok10 = r5_on['activated'] and 'Rahu' in r5_on['planets_in_7th']
    print(f"  Rahu in 7th forced → activated={r5_on['activated']} clearing_age={r5_on.get('clearing_age')}  {'✅' if ok10 else '❌'}")
    if not ok10: errors.append("Rule5: not activated with Rahu in 7th")

    print("\n─── Full Analysis via JyogiLogic class ─────────────────────")
    logic  = JyogiLogic(planets, lagna_lon, d9)
    result = logic.full_analysis(mode='career')
    ok11   = all(k in result for k in
                 ['rule1_navamsha','rule2_seventh','rule3_yoni',
                  'rule4_career','rule5_smoke','composite_scores'])
    print(f"  All keys present: {'✅' if ok11 else '❌'}")
    if not ok11: errors.append("Full analysis: missing keys")

    print(f"  Composite scores computed: {list(result['composite_scores'].keys())}")

    print("\n─── Narrative Report ───────────────────────────────────────")
    report = logic.narrative_report(result)
    ok12   = '7TH HOUSE' in report or 'PLANETARY STRENGTH' in report
    print(f"  Report generated ({len(report)} chars): {'✅' if ok12 else '❌'}")
    print()
    print(report)

    print()
    if errors:
        print(f"❌ {len(errors)} FAILED: {errors}")
    else:
        print("✅ All Jyogi Logic tests passed.")
    return len(errors) == 0


if __name__ == '__main__':
    run_tests()
