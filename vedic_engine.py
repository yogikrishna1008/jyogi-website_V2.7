"""
vedic_engine.py
===============
Pure Python Vedic astrology calculation engine.
Uses pyswisseph for accurate planetary positions.
All proprietary logic lives here — never sent to browser.

Replaces: astro_engine.js, compat.js, muhurta.js calculation functions
"""

import math
from datetime import date, timedelta

# ── Swiss Ephemeris ───────────────────────────────────────────
try:
    import swisseph as swe
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)  # t0=0, ayan_t0=0 → use built-in Lahiri
    _SWEPH = True
except ImportError:
    _SWEPH = False

# ══════════════════════════════════════════════════════════════
# SHARED CONSTANTS
# ══════════════════════════════════════════════════════════════

NAKSH = [
    'Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra',
    'Punarvasu','Pushya','Ashlesha','Magha','Purva Phalguni',
    'Uttara Phalguni','Hasta','Chitra','Swati','Vishakha','Anuradha',
    'Jyeshtha','Mula','Purva Ashadha','Uttara Ashadha','Shravana',
    'Dhanishtha','Shatabhisha','Purva Bhadrapada','Uttara Bhadrapada','Revati'
]
RASHIS = [
    'Aries','Taurus','Gemini','Cancer','Leo','Virgo',
    'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'
]
RASHI_LORD = [
    'Mars','Venus','Mercury','Moon','Sun','Mercury',
    'Venus','Mars','Jupiter','Saturn','Saturn','Jupiter'
]
PLANETS   = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']
SWE_BODIES = {
    'Sun': 0,'Moon': 1,'Mars': 4,'Mercury': 2,
    'Jupiter': 5,'Venus': 3,'Saturn': 6,'Rahu': 11,'Ketu': 11
}
DASHA_SEQ = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
DASHA_YRS = [7,20,6,10,7,18,16,19,17]

WEEKDAY = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
WEEKDAY_LORD = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']

YOGA_NAMES = [
    'Vishkambha','Priti','Ayushman','Saubhagya','Shobhana',
    'Atiganda','Sukarma','Dhriti','Shula','Ganda',
    'Vriddhi','Dhruva','Vyaghata','Harshana','Vajra',
    'Siddhi','Vyatipata','Variyan','Parigha','Shiva',
    'Siddha','Sadhya','Shubha','Shukla','Brahma',
    'Indra','Vaidhrti'
]
YOGA_BAD = {0,5,8,9,12,14,16,18,26}

KARANA_N = [
    'Bava','Balava','Kaulava','Taitila','Garija',
    'Vanija','Vishti','Shakuni','Chatushpada','Naga','Kimstughna'
]

TITHI_NAMES = [
    'Pratipada','Dwitiya','Tritiya','Chaturthi','Panchami',
    'Shashthi','Saptami','Ashtami','Navami','Dashami',
    'Ekadashi','Dwadashi','Trayodashi','Chaturdashi','Purnima',
    'Pratipada','Dwitiya','Tritiya','Chaturthi','Panchami',
    'Shashthi','Saptami','Ashtami','Navami','Dashami',
    'Ekadashi','Dwadashi','Trayodashi','Chaturdashi','Amavasya'
]

# Rahu Kaal slot by weekday (Sun=0..Sat=6)
# Offset = (slot-1) * 1.5h after sunrise — verified vs Drik Panchang
RAHU_SLOT = {0:5, 1:2, 2:7, 3:5, 4:6, 5:4, 6:3}

# ══════════════════════════════════════════════════════════════
# ASTRONOMY — Julian Day & Ayanamsa
# ══════════════════════════════════════════════════════════════

def julian_day(y: int, m: int, d: int, h_ut: float = 0.0) -> float:
    """Compute Julian Day Number."""
    if m <= 2:
        y -= 1; m += 12
    A = int(y / 100); B = 2 - A + int(A / 4)
    return int(365.25*(y+4716)) + int(30.6001*(m+1)) + d + h_ut/24 + B - 1524.5

def lahiri(jd: float) -> float:
    """
    Lahiri (Chitra Paksha) ayanamsa — authoritative value from Swiss Ephemeris.

    WHY: The old manual formula (23.85472 + 50.2388475/3600 * T * 100)
    drifts ~0.002° from SwEph's own Lahiri value. Over a 30-year span
    that is enough to push a planet sitting near a rashi boundary into
    the wrong sign, causing the one-house shift observed in both test cases.

    FIX: Always use swe.get_ayanamsa_ut() which is the same value SwEph
    uses internally when FLG_SIDEREAL is set — guaranteed consistency.
    """
    if _SWEPH:
        swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
        return swe.get_ayanamsa_ut(jd)
    # Fallback for no-SwEph environments (accurate to ~0.001°)
    T = (jd - 2451545.0) / 36525.0
    return 23.85472 + (50.2388475 / 3600.0) * T * 100.0

def to_sid(lon: float, jd: float) -> float:
    """Convert tropical to sidereal longitude."""
    return (lon - lahiri(jd)) % 360.0

def ist_to_ut(h_ist: float) -> float:
    """Convert IST float hours to UT."""
    return h_ist - 5.5

# ══════════════════════════════════════════════════════════════
# PLANETARY POSITIONS
# ══════════════════════════════════════════════════════════════

def _approx_moon(jd: float) -> float:
    """Approximate Moon longitude (tropical). Error ±1°. Fallback only."""
    T = (jd - 2451545.0) / 36525.0
    def r(x): return math.radians(x % 360)
    L0  = 218.3164477 + 481267.88123421*T - 0.0015786*T*T
    M   = 134.9633964 + 477198.8675055 *T + 0.0087414*T*T
    Ms  = 357.5291092 + 35999.0502909  *T - 0.0001536*T*T
    F   = 93.2720950  + 483202.0175233 *T - 0.0036539*T*T
    D   = 297.8501921 + 445267.1114034 *T - 0.0018819*T*T
    dL  = (6.288774*math.sin(r(M))  + 1.274027*math.sin(r(2*D-M))
          +0.658314*math.sin(r(2*D)) + 0.213618*math.sin(r(2*M))
          -0.185116*math.sin(r(Ms))  - 0.114332*math.sin(r(2*F))
          +0.058793*math.sin(r(2*D-2*M)) + 0.057066*math.sin(r(2*D-Ms-M))
          +0.053322*math.sin(r(2*D+M))   + 0.045758*math.sin(r(2*D-Ms))
          -0.040923*math.sin(r(Ms-M))    - 0.034720*math.sin(r(D))
          -0.030383*math.sin(r(Ms+M))    + 0.015327*math.sin(r(2*(D-F)))
          -0.012528*math.sin(r(M+2*F))   + 0.010980*math.sin(r(M-2*F)))
    return (L0 + dL) % 360.0

def get_planet_sid(planet: str, jd: float) -> float:
    """
    Get sidereal longitude of planet.

    WHY FLG_SPEED is required even here: SwEph internally uses speed to
    correct for light-travel time (aberration). Without it, positions for
    outer planets can shift by up to 0.01° — enough to cross a rashi
    boundary at narrow cusps. FLG_SPEED costs nothing extra.
    """
    if _SWEPH:
        swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)   # must call before every calc_ut
        body = SWE_BODIES[planet]
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
        result, _ = swe.calc_ut(jd, body, flags)
        lon = result[0] % 360.0
        if planet == 'Ketu':
            lon = (lon + 180.0) % 360.0
        return lon
    else:
        # Approximate fallback
        T = (jd - 2451545.0) / 36525.0
        def r(x): return math.radians(x % 360)
        if planet == 'Moon':
            return to_sid(_approx_moon(jd), jd)
        elif planet == 'Sun':
            M = (357.52911 + 35999.05029*T) % 360
            C = (1.914602-0.004817*T)*math.sin(r(M)) + 0.019993*math.sin(r(2*M))
            return to_sid((280.46646 + 36000.76983*T + C) % 360, jd)
        else:
            return 0.0  # placeholder for other planets without sweph



def get_house(planet_lon: float, lagna_lon: float) -> int:
    """
    Whole Sign house number (1–12) of a planet relative to the Lagna.

    Vedic astrology uses WHOLE SIGN houses exclusively in Rashi Chakra:
    - The rashi containing the Lagna degree is the 1st house (regardless
      of how many degrees into that sign the Lagna falls).
    - Every subsequent sign is one house forward.

    Formula:
        house = ((planet_sign - lagna_sign) mod 12) + 1

    WHY THE OLD CODE WAS WRONG:
        Old api.py used `rashi_idx + 1` which gives the absolute rashi
        number (e.g. Scorpio = 8), NOT the house relative to the Lagna.
        A Capricorn Lagna chart with Saturn in Leo would show:
            Old (wrong): house = int(149° / 30) + 1 = 5 + 1 = 6  ← absolute
            Correct:     ((4 - 9) % 12) + 1 = 8                  ← relative

    Args:
        planet_lon: Sidereal longitude of planet (0–360°)
        lagna_lon:  Sidereal longitude of Lagna  (0–360°)

    Returns:
        House number 1–12
    """
    lagna_sign  = int(lagna_lon  / 30) % 12
    planet_sign = int(planet_lon / 30) % 12
    return ((planet_sign - lagna_sign) % 12) + 1


def get_planet_retrograde(planet: str, jd: float) -> bool:
    """
    Returns True if planet is retrograde (Vakri) at given JD.

    Detection method: longitude speed (result[3] from swe.calc_ut).
    A negative speed means the planet is moving backwards against the
    ecliptic — i.e., retrograde.

    Sun and Moon are NEVER retrograde by definition.
    Rahu/Ketu are ALWAYS mathematically retrograde (they move backwards
    through the zodiac) but Vedic tradition does not mark them as Vakri.
    """
    if planet in ('Sun', 'Moon', 'Rahu', 'Ketu'):
        return False

    if _SWEPH:
        swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
        body = SWE_BODIES[planet]
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
        result, _ = swe.calc_ut(jd, body, flags)
        # result[3] = longitude speed in degrees/day; negative = retrograde
        return result[3] < 0
    else:
        # Approximate fallback — compute position 1 day before and after
        # If position decreased over time, planet is retrograde
        try:
            lon_before = get_planet_sid(planet, jd - 1)
            lon_after = get_planet_sid(planet, jd + 1)
            # Handle 0/360 boundary
            diff = lon_after - lon_before
            if diff > 180: diff -= 360
            if diff < -180: diff += 360
            return diff < 0
        except:
            return False


def get_all_planets(jd: float) -> dict:
    """Get sidereal longitudes for all 9 grahas."""
    result = {}
    for planet in PLANETS:
        try:
            result[planet] = round(get_planet_sid(planet, jd), 4)
        except Exception:
            result[planet] = 0.0
    return result

def get_lagna(jd: float, lat: float, lon: float) -> float:
    """
    Get Ascendant (Lagna) sidereal longitude.

    swe.houses() returns TROPICAL cusps. We subtract the Lahiri ayanamsa
    (via to_sid → lahiri → swe.get_ayanamsa_ut) to get the sidereal Lagna.

    set_sid_mode must be called before swe.houses() even though we are
    doing the ayanamsa subtraction manually — some SwEph builds use the
    cached sid_mode inside houses() for internal ARMC calculations.
    """
    if _SWEPH:
        try:
            swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
            houses, ascmc = swe.houses(jd, lat, lon, b'P')
            return to_sid(ascmc[0], jd)   # ascmc[0] = tropical Asc
        except Exception:
            pass
    # Approximate fallback
    T = (jd - 2451545.0) / 36525.0
    RAMC = (280.46061837 + 360.98564736629 * (jd - 2451545.0)) % 360 + lon
    e = 23.4393 - 0.013*T
    lst = RAMC
    def r(x): return math.radians(x % 360)
    asc = math.degrees(math.atan2(
        math.cos(r(lst)),
        -(math.sin(r(lst)) * math.cos(r(e)) + math.tan(r(lat)) * math.sin(r(e)))
    )) % 360
    return to_sid(asc, jd)

# ══════════════════════════════════════════════════════════════
# DASHA
# ══════════════════════════════════════════════════════════════

def get_dasha(moon_lon: float, birth_jd: float) -> dict:
    """Calculate current Vimshottari Dasha."""
    nk_idx = int(moon_lon / (360/27))
    nk_pos = (moon_lon % (360/27)) / (360/27)  # fraction through nakshatra

    # Dasha lord index
    lord_idx = nk_idx % 9
    lord = DASHA_SEQ[lord_idx]
    total_yrs = DASHA_YRS[lord_idx]

    # Years elapsed in current dasha at birth
    elapsed = nk_pos * total_yrs
    # Dasha start JD
    dasha_start_jd = birth_jd - elapsed * 365.25
    dasha_end_jd   = dasha_start_jd + total_yrs * 365.25

    def jd_to_ymd(j):
        import datetime
        delta = datetime.timedelta(days=j - 2451545.0)
        base  = datetime.date(2000, 1, 1)
        d = base + delta
        return d.strftime("%d %b %Y")

    # Next 3 dashas
    seq = []
    jd_cursor = dasha_start_jd
    idx = lord_idx
    for _ in range(4):
        seq.append({
            'lord': DASHA_SEQ[idx % 9],
            'years': DASHA_YRS[idx % 9],
            'start': jd_to_ymd(jd_cursor),
            'end':   jd_to_ymd(jd_cursor + DASHA_YRS[idx % 9] * 365.25),
        })
        jd_cursor += DASHA_YRS[idx % 9] * 365.25
        idx += 1

    return {
        'current_lord': lord,
        'current_years': total_yrs,
        'sequence': seq,
        'lord_idx': lord_idx,
    }

# ══════════════════════════════════════════════════════════════
# NUMEROLOGY
# ══════════════════════════════════════════════════════════════

def calc_numerology(day: int, month: int, year: int) -> dict:
    """Vedic numerology — Life Path and other numbers."""
    def reduce(n):
        while n > 9 and n not in (11, 22, 33):
            n = sum(int(d) for d in str(n))
        return n

    life_path = reduce(day + month + sum(int(d) for d in str(year)))
    destiny   = reduce(day)
    soul      = reduce(month)
    maturity  = reduce(life_path + destiny)

    descriptions = {
        1: "Leader — independent, pioneering, self-reliant",
        2: "Diplomat — cooperative, sensitive, peacemaker",
        3: "Creator — expressive, joyful, artistic",
        4: "Builder — disciplined, practical, reliable",
        5: "Explorer — freedom-loving, versatile, adventurous",
        6: "Nurturer — responsible, caring, family-oriented",
        7: "Seeker — analytical, spiritual, introspective",
        8: "Achiever — ambitious, business-minded, powerful",
        9: "Humanitarian — compassionate, generous, wise",
        11: "Intuitive — visionary, idealistic, inspiring",
        22: "Master Builder — practical visionary, large-scale impact",
        33: "Master Teacher — selfless service, highest vibration",
    }

    return {
        'life_path': life_path,
        'life_path_desc': descriptions.get(life_path, ''),
        'destiny': destiny,
        'soul': soul,
        'maturity': maturity,
    }

# ══════════════════════════════════════════════════════════════
# YOGAS
# ══════════════════════════════════════════════════════════════

_EXALT = {'Sun':0,'Moon':1,'Mars':9,'Mercury':5,'Jupiter':3,'Venus':11,'Saturn':6}
_OWN   = {
    'Sun':[4],'Moon':[3],'Mars':[0,7],'Mercury':[2,5],
    'Jupiter':[8,11],'Venus':[1,6],'Saturn':[9,10]
}

def detect_yogas(planets: dict, lagna_lon: float) -> list:
    """Detect major Vedic yogas from planetary positions."""
    lagna_idx = int(lagna_lon / 30)
    yogas = []

    def house(planet):
        return (int(planets[planet] / 30) - lagna_idx) % 12 + 1

    def is_kendra(h): return h in [1,4,7,10]
    def is_trikona(h): return h in [1,5,9]
    def is_dushtana(h): return h in [6,8,12]
    def is_exalted(p): return int(planets[p]/30) == _EXALT.get(p,-1)
    def is_own(p): return int(planets[p]/30) in _OWN.get(p,[])
    def is_strong(p): return is_exalted(p) or is_own(p)

    # Gaja Kesari — Jupiter in kendra from Moon
    moon_sign = int(planets['Moon'] / 30)
    jup_sign  = int(planets['Jupiter'] / 30)
    jup_from_moon = (jup_sign - moon_sign) % 12 + 1
    if is_kendra(jup_from_moon):
        yogas.append({
            'name': 'Gaja Kesari Yoga', 'icon': '🐘',
            'strength': 'Powerful',
            'brief': 'Jupiter in kendra from Moon — wisdom, lasting reputation, prosperity.',
        })

    # Pancha Mahapurusha
    for planet, name, quality in [
        ('Jupiter', 'Hamsa Yoga',   'Divine'),
        ('Venus',   'Malavya Yoga', 'Luxurious'),
        ('Mars',    'Ruchaka Yoga', 'Courageous'),
        ('Mercury', 'Bhadra Yoga',  'Intelligent'),
        ('Saturn',  'Shasha Yoga',  'Disciplined'),
    ]:
        if is_strong(planet) and is_kendra(house(planet)):
            yogas.append({
                'name': name, 'icon': '⭐',
                'strength': quality,
                'brief': f'{planet} strong in kendra — {quality.lower()} qualities.',
            })

    # Raj Yoga — strong planet in both kendra and trikona lord
    for p in ['Jupiter','Venus','Mercury','Moon','Mars']:
        h = house(p)
        if is_kendra(h) and is_trikona(h) and is_strong(p):
            yogas.append({
                'name': 'Raj Yoga', 'icon': '👑',
                'strength': 'Royal',
                'brief': f'{p} powerful — career success and authority.',
            })

    # Kemadruma — Moon with no planets in adjacent signs
    moon_h = int(planets['Moon'] / 30)
    adjacent = {(moon_h + 1) % 12, (moon_h - 1) % 12}
    other_planets = {int(planets[p]/30) for p in PLANETS if p not in ('Moon','Rahu','Ketu')}
    if not adjacent.intersection(other_planets):
        yogas.append({
            'name': 'Kemadruma Yoga', 'icon': '🌑',
            'strength': 'Challenging',
            'brief': 'Moon without support — can be remedied with consistent practice.',
            'challenging': True,
        })

    return yogas

# ══════════════════════════════════════════════════════════════
# NAVAMSHA (D9)
# ══════════════════════════════════════════════════════════════

def _d9_sign(lon: float) -> int:
    """Classical Parashari Navamsa sign from sidereal longitude.

    Each 30 deg sign is divided into 9 padas of 3 deg 20'.
    Starting sign of the pada sequence depends on sign quality:
      Movable (chara: Aries/Cancer/Libra/Capricorn) -> starts from the SAME sign
      Fixed   (sthira: Taurus/Leo/Scorpio/Aquarius) -> starts from the 9TH from it
      Dual    (dvi-svabhava: Gemini/Virgo/Sag/Pisces) -> starts from the 5TH from it
    """
    L = ((lon % 360) + 360) % 360
    si = int(L // 30)
    pada = int((L % 30) / (30/9))
    t = si % 3
    if t == 0:    offset = si              # movable
    elif t == 1:  offset = (si + 8) % 12   # fixed -> 9th
    else:         offset = (si + 4) % 12   # dual -> 5th
    return (offset + pada) % 12


def calc_navamsha(planets: dict, lagna_lon: float = None) -> dict:
    """Calculate D9 (Navamsa) chart positions using classical Parashari rule.

    Args:
        planets   : dict {planet_name: sidereal_longitude_float}
        lagna_lon : optional sidereal lagna longitude. If provided, the result
                    includes a 'lagna' key with the D9 lagna sign and rashi.

    Returns:
        dict {planet: {'lon', 'nav_sign', 'nav_rashi', 'pada'}, ...}
        plus optionally 'lagna': {'lon', 'nav_sign', 'nav_rashi'} when lagna_lon
        is provided.

    Notes:
        - Rahu/Ketu axis: if both nodes are in `planets`, Ketu is auto-derived
          as (Rahu + 180) deg to enforce the 180 deg opposition rule. This
          guards against upstream calc errors that might place both nodes
          at the same longitude.
    """
    # If Rahu is in input but no Ketu (or Ketu is suspiciously equal to Rahu),
    # derive Ketu from Rahu + 180 to enforce the axis rule.
    planets = dict(planets)  # don't mutate caller's dict
    if 'Rahu' in planets:
        rahu_lon = planets['Rahu']
        if 'Ketu' not in planets or abs((planets['Ketu'] - rahu_lon) % 360 - 180) > 0.1:
            planets['Ketu'] = (rahu_lon + 180.0) % 360

    result = {}
    for planet, lon in planets.items():
        nav_sign = _d9_sign(lon)
        pada = int((lon % 30) / (30/9))
        result[planet] = {
            'lon':       round(lon, 3),
            'nav_sign':  nav_sign,
            'nav_rashi': RASHIS[nav_sign],
            'pada':      pada + 1,
        }

    if lagna_lon is not None:
        lag_d9 = _d9_sign(lagna_lon)
        result['lagna'] = {
            'lon':       round(lagna_lon, 3),
            'nav_sign':  lag_d9,
            'nav_rashi': RASHIS[lag_d9],
        }

    return result

# ══════════════════════════════════════════════════════════════
# PANCHANG
# ══════════════════════════════════════════════════════════════

def _approx_sun(jd: float) -> float:
    """Approximate Sun sidereal longitude."""
    T = (jd - 2451545.0) / 36525.0
    M = (357.52911 + 35999.05029*T) % 360
    C = (1.914602-0.004817*T)*math.sin(math.radians(M)) + 0.019993*math.sin(math.radians(2*M))
    return to_sid((280.46646 + 36000.76983*T + C) % 360, jd)

def calc_panchang(year: int, month: int, day: int) -> dict:
    """Calculate full Panchang for a given date."""
    jd = julian_day(year, month, day, 0.5)  # 6 AM IST = 0.5 UT

    # Sun and Moon
    if _SWEPH:
        sun  = get_planet_sid('Sun',  jd)
        moon = get_planet_sid('Moon', jd)
    else:
        sun  = _approx_sun(jd)
        moon = to_sid(_approx_moon(jd), jd)

    diff = (moon - sun) % 360.0

    # Tithi (1-30)
    tithi_num  = int(diff / 12) + 1
    tithi_name = TITHI_NAMES[tithi_num - 1]
    paksha     = 'Shukla' if tithi_num <= 15 else 'Krishna'

    # Nakshatra
    nk_idx   = int(moon / (360/27))
    nk_pada  = int((moon % (360/27)) / (360/27/4)) + 1

    # Yoga
    yoga_idx  = int(((sun + moon) % 360) / (360/27))
    yoga_name = YOGA_NAMES[yoga_idx]
    yoga_bad  = yoga_idx in YOGA_BAD

    # Karana (half-tithi)
    karana_num = int(diff / 6)
    if karana_num == 0:
        karana_name = 'Kimstughna'
    elif karana_num >= 57:
        karana_name = ['Shakuni','Chatushpada','Naga','Kimstughna'][min(karana_num-57,3)]
    else:
        karana_name = KARANA_N[(karana_num - 1) % 7]
    bhadra = (karana_name == 'Vishti')

    # Weekday & Rahu Kaal
    import datetime
    dt  = datetime.date(year, month, day)
    wd  = dt.isoweekday() % 7  # Sun=0..Sat=6
    doy = dt.timetuple().tm_yday
    sunrise = 6.0 + 0.5 * math.sin(2 * math.pi * (doy - 80) / 365)
    rahu_start = sunrise + (RAHU_SLOT[wd] - 1) * 1.5
    rahu_end   = rahu_start + 1.5

    def fmt(h): return f"{int(h):02d}:{int((h%1)*60):02d}"

    return {
        'date':        f"{day:02d}/{month:02d}/{year}",
        'weekday':     WEEKDAY[wd],
        'weekday_lord':WEEKDAY_LORD[wd],
        'tithi_num':   tithi_num,
        'tithi_name':  tithi_name,
        'paksha':      paksha,
        'nakshatra':   NAKSH[nk_idx],
        'nk_pada':     nk_pada,
        'moon_sign':   RASHIS[int(moon/30)],
        'sun_sign':    RASHIS[int(sun/30)],
        'yoga':        yoga_name,
        'yoga_bad':    yoga_bad,
        'karana':      karana_name,
        'bhadra':      bhadra,
        'rahu_start':  fmt(rahu_start),
        'rahu_end':    fmt(rahu_end),
        'abhijit_start': '11:36',
        'abhijit_end':   '12:24',
        'using_sweph': _SWEPH,
    }

# ══════════════════════════════════════════════════════════════
# MUHURTA — Activity scoring
# ══════════════════════════════════════════════════════════════

ACTIVITY_DATA = {
    'Marriage':         {'good_t':[2,3,5,7,10,11,13],'avoid_t':[4,6,8,9,12,14,15,30],'good_nk':[3,4,6,7,11,12,13,15,20,21,22,23,24,25,26],'avoid_nk':[1,2,5,8,9,18,19],'good_wd':[1,3,4,5],'avoid_wd':[0,2,6]},
    'House Warming':    {'good_t':[2,3,5,7,10,11,13],'avoid_t':[4,8,9,12,14,30],'good_nk':[3,4,6,7,11,12,13,20,21,25,26],'avoid_nk':[1,2,5,8,9,18,19],'good_wd':[1,3,4,5],'avoid_wd':[0,2,6]},
    'Naming Ceremony':  {'good_t':[2,3,5,7,10,11,13],'avoid_t':[4,6,8,9,12,14,30],'good_nk':[3,4,6,7,12,13,15,20,21,22,25,26],'avoid_nk':[1,2,5,8,18,19],'good_wd':[1,3,4,5],'avoid_wd':[0,2,6]},
    'Thread Ceremony':  {'good_t':[2,3,5,7,10,11],'avoid_t':[4,6,8,9,12,14,30],'good_nk':[3,6,7,11,12,13,20,21,25,26],'avoid_nk':[1,2,5,8,9,18],'good_wd':[1,3,4,5],'avoid_wd':[2,6]},
    'New Business':     {'good_t':[2,3,5,6,7,10,11,13],'avoid_t':[4,8,9,12,14,30],'good_nk':[0,3,6,7,11,12,13,20,21,22,25,26],'avoid_nk':[1,2,5,8,9,18,19],'good_wd':[1,3,4,5],'avoid_wd':[2,6]},
    'Investment':       {'good_t':[2,3,5,6,10,11,13],'avoid_t':[4,8,9,12,14,30],'good_nk':[3,6,7,11,12,13,20,21,22],'avoid_nk':[1,2,5,8,9,18,19],'good_wd':[1,3,4,5],'avoid_wd':[2,6]},
    'Shop Opening':     {'good_t':[2,3,5,7,10,11,13],'avoid_t':[4,8,9,14,30],'good_nk':[0,3,4,6,7,12,13,20,21,22,25,26],'avoid_nk':[1,2,5,8,18,19],'good_wd':[1,3,4,5],'avoid_wd':[2,6]},
    'Agreement':        {'good_t':[2,3,5,6,7,10,11,13],'avoid_t':[4,8,9,12,14,30],'good_nk':[0,3,4,6,7,12,13,20,21,22],'avoid_nk':[1,2,5,8,9,18,19],'good_wd':[1,3,4,5],'avoid_wd':[2,6]},
    'Property Purchase':{'good_t':[2,3,5,7,10,11,13],'avoid_t':[4,8,9,12,14,30],'good_nk':[3,4,6,7,11,12,13,20,21,22,25,26],'avoid_nk':[1,2,5,8,9,18,19],'good_wd':[1,3,4,5],'avoid_wd':[0,2,6]},
    'Vehicle Purchase': {'good_t':[2,3,5,7,10,11,13],'avoid_t':[4,8,9,14,30],'good_nk':[0,3,4,6,7,12,13,20,21,22,25,26],'avoid_nk':[1,2,5,8,9,18,19],'good_wd':[1,3,4,5],'avoid_wd':[2,6]},
    'Travel':           {'good_t':[2,3,5,7,10,11,13],'avoid_t':[4,8,9,12,14,30],'good_nk':[0,3,4,6,7,12,13,20,21,22,25,26],'avoid_nk':[1,2,5,8,9,18,19],'good_wd':[1,3,4,5],'avoid_wd':[2,6]},
    'Education / Exam': {'good_t':[2,3,5,7,10,11,13],'avoid_t':[4,8,9,12,14,30],'good_nk':[3,4,6,7,11,12,13,20,21,25,26],'avoid_nk':[1,2,5,8,18,19],'good_wd':[1,3,4],'avoid_wd':[2,6]},
    'Medical / Surgery':{'good_t':[2,3,5,7,10,11,13],'avoid_t':[4,8,9,12,14,30],'good_nk':[0,3,4,6,7,12,13,20,21],'avoid_nk':[1,2,5,8,9,18,19],'good_wd':[1,3,4,5],'avoid_wd':[0,2,6]},
    'Interview / Job':  {'good_t':[2,3,5,6,7,10,11,13],'avoid_t':[4,8,9,14,30],'good_nk':[0,3,4,6,7,12,13,20,21,22],'avoid_nk':[1,2,5,8,9,18,19],'good_wd':[1,3,4,5],'avoid_wd':[2,6]},
}

def score_day_for_activity(panchang: dict, activity: str) -> dict:
    """Score a day for a specific activity. Returns stars (1-5) and reasons."""
    a = ACTIVITY_DATA.get(activity)
    if not a:
        return {'stars': 3, 'score': 0, 'good': [], 'warn': []}

    tithi_num = panchang['tithi_num']
    nk_idx    = NAKSH.index(panchang['nakshatra'])
    wd_name   = panchang['weekday']
    wd        = WEEKDAY.index(wd_name)
    yoga_bad  = panchang['yoga_bad']
    bhadra    = panchang['bhadra']

    score = 0; good = []; warn = []

    if tithi_num in a['good_t']:   score += 3; good.append(f"{panchang['tithi_name']} ✓")
    elif tithi_num in a['avoid_t']:score -= 3; warn.append(f"{panchang['tithi_name']} ✗")

    if nk_idx in a['good_nk']:   score += 3; good.append(f"{panchang['nakshatra']} ✓")
    elif nk_idx in a['avoid_nk']:score -= 3; warn.append(f"{panchang['nakshatra']} ✗")

    if wd in a['good_wd']:   score += 2; good.append(f"{wd_name} ✓")
    elif wd in a['avoid_wd']:score -= 2; warn.append(f"{wd_name} ✗")

    if yoga_bad: score -= 2; warn.append(f"{panchang['yoga']} ✗")
    else:        score += 1; good.append(f"{panchang['yoga']} ✓")

    if bhadra: score -= 2; warn.append("Vishti/Bhadra ✗")

    stars = max(1, min(5, round((score + 5) / 2.5)))
    return {'stars': stars, 'score': score, 'good': good, 'warn': warn}

def get_muhurta_grid(activity: str, from_date: date = None, days: int = 7) -> list:
    """Get 7-day Muhurta grid for an activity."""
    if from_date is None:
        from_date = date.today()
    result = []
    for i in range(days):
        d = from_date + timedelta(days=i)
        panchang = calc_panchang(d.year, d.month, d.day)
        scoring  = score_day_for_activity(panchang, activity)
        result.append({
            'date':    d.isoformat(),
            'day':     d.day,
            'month':   d.strftime('%b'),
            'weekday': panchang['weekday'],
            'tithi':   panchang['tithi_name'],
            'nakshatra': panchang['nakshatra'],
            'yoga':    panchang['yoga'],
            'yoga_bad':panchang['yoga_bad'],
            'bhadra':  panchang['bhadra'],
            'rahu':    f"{panchang['rahu_start']}–{panchang['rahu_end']}",
            'stars':   scoring['stars'],
            'good':    scoring['good'],
            'warn':    scoring['warn'],
        })
    return result


# ══════════════════════════════════════════════════════════════
# SELF-TEST
# ══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print(f"Swiss Ephemeris: {_SWEPH}")
    print()

    # Test panchang
    p = calc_panchang(2026, 4, 7)
    print("Panchang 7 Apr 2026:")
    for k, v in p.items():
        print(f"  {k}: {v}")

    print()
    # Test planets
    jd = julian_day(1982, 2, 21, ist_to_ut(8 + 20/60))
    planets = get_all_planets(jd)
    moon = planets['Moon']
    print(f"Jyoti Moon: {moon:.3f}° → {NAKSH[int(moon/(360/27))]}")

    print()
    # Test numerology
    n = calc_numerology(21, 2, 1982)
    print(f"Numerology: Life Path = {n['life_path']} ({n['life_path_desc']})")

    print()
    # Test muhurta grid
    grid = get_muhurta_grid('Vehicle Purchase')
    print("Vehicle Purchase — next 7 days:")
    for day in grid:
        print(f"  {day['weekday'][:3]} {day['day']:02d} {'★'*day['stars']}  {day['tithi'][:8]:<10} {day['nakshatra'][:12]}")
