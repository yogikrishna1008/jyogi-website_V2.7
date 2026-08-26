"""
numerology.py — Jyogi AI Numerology Engine
==========================================
Pythagorean system with proper Master Number handling.

Functions:
  reduce(n)              — reduce to single digit, keep 11/22/33
  life_path(dob)         — from YYYY-MM-DD
  destiny(full_name)     — all letters, Pythagorean
  soul_urge(full_name)   — vowels only
  personality(full_name) — consonants only
  personal_year(dob, year)
  numerology_report(full_name, dob) — full dict output
"""

# ── Pythagorean letter → digit map ──────────────────────────────────
# A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
# 1 2 3 4 5 6 7 8 9 1 2 3 4 5 6 7 8 9 1 2 3 4 5 6 7 8
PYTHAGOREAN = {
    'A':1,'B':2,'C':3,'D':4,'E':5,'F':6,'G':7,'H':8,'I':9,
    'J':1,'K':2,'L':3,'M':4,'N':5,'O':6,'P':7,'Q':8,'R':9,
    'S':1,'T':2,'U':3,'V':4,'W':5,'X':6,'Y':7,'Z':8,
}

VOWELS     = set('AEIOU')
CONSONANTS = set(PYTHAGOREAN.keys()) - VOWELS   # B C D F G H J K L M N P Q R S T V W X Y Z

# Master Numbers — never reduce these
MASTER_NUMBERS = {11, 22, 33}


# ── Core reduction ───────────────────────────────────────────────────
def reduce(n: int) -> int:
    """
    Reduce any integer to a single digit (1-9).
    Preserves Master Numbers 11, 22, 33 at each reduction step.

    Examples:
        reduce(29)  → 11  (2+9=11, Master Number — keep)
        reduce(38)  → 11  (3+8=11, Master Number — keep)
        reduce(47)  → 11  (4+7=11, keep)
        reduce(30)  → 3
        reduce(22)  → 22  (already Master)
    """
    while n > 9 and n not in MASTER_NUMBERS:
        n = sum(int(d) for d in str(n))
    return n


# ── Life Path ────────────────────────────────────────────────────────
def life_path(dob: str) -> int:
    """
    Life Path from DOB string 'YYYY-MM-DD'.

    Method: reduce day, month, year SEPARATELY, then sum and reduce again.
    This matches Pythagorean / Felicia Bender standard.

    Example: 1982-02-21
      day   = 21 → 2+1 = 3
      month = 02 → 2
      year  = 1982 → 1+9+8+2 = 20 → 2+0 = 2
      sum   = 3+2+2 = 7  → Life Path 7
    """
    try:
        parts = dob.strip().split('-')
        if len(parts) != 3:
            raise ValueError(f"DOB must be YYYY-MM-DD, got: {dob!r}")
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid DOB format: {e}")

    r_day   = reduce(day)
    r_month = reduce(month)
    r_year  = reduce(sum(int(d) for d in str(year)))   # reduce year digit-sum

    total   = r_day + r_month + r_year
    return reduce(total)


# ── Internal: sum letters matching a filter ─────────────────────────
def _sum_letters(full_name: str, letter_set: set) -> int:
    """
    Sum Pythagorean values of all characters in full_name
    that appear in letter_set. Case-insensitive. Ignores spaces,
    digits, punctuation.

    This single function powers both destiny() and soul_urge()
    to avoid duplicated logic and guarantee consistency.
    """
    total = 0
    for ch in full_name.upper():
        if ch in letter_set:
            total += PYTHAGOREAN[ch]
    return reduce(total)


# ── Destiny (Expression) Number ──────────────────────────────────────
def destiny(full_name: str) -> int:
    """
    Destiny / Expression Number — ALL letters in the full name.
    Uses Pythagorean chart. Spaces and non-alpha characters ignored.

    Example: 'Jyotirmoy Giri'
      J=1 Y=7 O=6 T=2 I=9 R=9 M=4 O=6 Y=7  (first name = 51)
      G=7 I=9 R=9 I=9                         (last name  = 34)
      total = 51+34 = 85 → 8+5 = 13 → 1+3 = 4
    """
    return _sum_letters(full_name, set(PYTHAGOREAN.keys()))


# ── Soul Urge (Heart's Desire) ────────────────────────────────────────
def soul_urge(full_name: str) -> int:
    """
    Soul Urge / Heart's Desire — VOWELS only (A E I O U).
    Y is treated as consonant in standard Pythagorean method.

    Common bug: if full_name is empty or has no vowels, sum=0 → reduce(0)=0.
    This implementation raises a clear error for empty input.

    Example: 'Jyotirmoy Giri'
      Vowels: O I O I I  → 6+9+6+9+9 = 39 → 3+9 = 12 → 1+2 = 3
    """
    if not full_name.strip():
        raise ValueError("Name cannot be empty")
    # Verify at least one vowel exists
    upper = full_name.upper()
    if not any(ch in VOWELS for ch in upper):
        raise ValueError(f"No vowels found in name: {full_name!r}")
    return _sum_letters(full_name, VOWELS)


# ── Personality Number ───────────────────────────────────────────────
def personality(full_name: str) -> int:
    """
    Personality Number — CONSONANTS only.
    Destiny = Soul Urge + Personality (before final reduction).
    """
    return _sum_letters(full_name, CONSONANTS)


# ── Personal Year ────────────────────────────────────────────────────
def personal_year(dob: str, year: int) -> int:
    """
    Personal Year for a given calendar year.
    Formula: reduce(day) + reduce(month) + reduce(year_of_interest)

    Example: DOB 1982-02-21, year 2026
      day=21→3, month=2→2, year=2026→2+0+2+6=10→1+0=1
      3+2+1 = 6 → Personal Year 6
    """
    parts   = dob.strip().split('-')
    month   = reduce(int(parts[1]))
    day     = reduce(int(parts[2]))
    r_year  = reduce(sum(int(d) for d in str(year)))
    return reduce(day + month + r_year)


# ── Full Report ───────────────────────────────────────────────────────
def numerology_report(full_name: str, dob: str, current_year: int = None) -> dict:
    """
    Generate a complete numerology profile.

    Returns:
        dict with all numbers plus intermediate working values
        so calculations can be audited / displayed in UI.
    """
    import datetime
    if current_year is None:
        current_year = datetime.date.today().year

    # Intermediate values for audit trail
    parts    = dob.strip().split('-')
    yr, mo, dy = int(parts[0]), int(parts[1]), int(parts[2])
    r_day    = reduce(dy)
    r_month  = reduce(mo)
    r_year   = reduce(sum(int(d) for d in str(yr)))
    lp_sum   = r_day + r_month + r_year

    # Letter-level breakdown for transparency
    upper = full_name.upper()
    vowel_letters     = [ch for ch in upper if ch in VOWELS]
    consonant_letters = [ch for ch in upper if ch in CONSONANTS]
    vowel_values      = [PYTHAGOREAN[ch] for ch in vowel_letters]
    consonant_values  = [PYTHAGOREAN[ch] for ch in consonant_letters]

    return {
        # ── Core numbers ───────────────────────────────────────
        "life_path"    : life_path(dob),
        "destiny"      : destiny(full_name),
        "soul_urge"    : soul_urge(full_name),
        "personality"  : personality(full_name),
        "personal_year": personal_year(dob, current_year),

        # ── Audit trail ────────────────────────────────────────
        "_audit": {
            "life_path": {
                "day_reduced"  : r_day,
                "month_reduced": r_month,
                "year_reduced" : r_year,
                "sum_before_reduce": lp_sum,
            },
            "soul_urge": {
                "vowels_found" : vowel_letters,
                "vowel_values" : vowel_values,
                "raw_sum"      : sum(vowel_values),
            },
            "destiny": {
                "all_letters"  : [ch for ch in upper if ch in PYTHAGOREAN],
                "all_values"   : [PYTHAGOREAN[ch] for ch in upper if ch in PYTHAGOREAN],
                "raw_sum"      : sum(PYTHAGOREAN[ch] for ch in upper if ch in PYTHAGOREAN),
            },
            "personality": {
                "consonants"   : consonant_letters,
                "con_values"   : consonant_values,
                "raw_sum"      : sum(consonant_values),
            },
            "personal_year": {
                "year"         : current_year,
                "day_red"      : r_day,
                "month_red"    : r_month,
                "year_red"     : reduce(sum(int(d) for d in str(current_year))),
            },
        },
    }


# ── Pretty print ─────────────────────────────────────────────────────
def print_report(full_name: str, dob: str, current_year: int = None):
    """Print a formatted numerology report to stdout."""
    import datetime
    if current_year is None:
        current_year = datetime.date.today().year

    r = numerology_report(full_name, dob, current_year)
    a = r['_audit']

    SEP  = "─" * 56
    SEP2 = "═" * 56

    print(f"\n{SEP2}")
    print(f"  ✦ JYOGI AI — NUMEROLOGY REPORT")
    print(f"{SEP2}")
    print(f"  Name  : {full_name}")
    print(f"  DOB   : {dob}")
    print(f"{SEP}")

    print(f"\n  LIFE PATH  :  {r['life_path']}")
    lp = a['life_path']
    print(f"    Day {int(dob.split('-')[2])} → {lp['day_reduced']}  |  "
          f"Month {int(dob.split('-')[1])} → {lp['month_reduced']}  |  "
          f"Year {dob.split('-')[0]} → {lp['year_reduced']}")
    print(f"    Sum = {lp['sum_before_reduce']} → reduced → {r['life_path']}")

    print(f"\n  DESTINY    :  {r['destiny']}")
    dst = a['destiny']
    pairs = [f"{l}={v}" for l,v in zip(dst['all_letters'], dst['all_values'])]
    print(f"    Letters : {' '.join(pairs)}")
    print(f"    Raw sum : {dst['raw_sum']} → reduced → {r['destiny']}")

    print(f"\n  SOUL URGE  :  {r['soul_urge']}")
    su = a['soul_urge']
    pairs_v = [f"{l}={v}" for l,v in zip(su['vowels_found'], su['vowel_values'])]
    print(f"    Vowels  : {' '.join(pairs_v)}")
    print(f"    Raw sum : {su['raw_sum']} → reduced → {r['soul_urge']}")

    print(f"\n  PERSONALITY:  {r['personality']}")
    pn = a['personality']
    pairs_c = [f"{l}={v}" for l,v in zip(pn['consonants'], pn['con_values'])]
    print(f"    Consonants: {' '.join(pairs_c)}")
    print(f"    Raw sum : {pn['raw_sum']} → reduced → {r['personality']}")

    print(f"\n  PERSONAL YEAR {current_year}: {r['personal_year']}")
    py = a['personal_year']
    print(f"    Day {lp['day_reduced']} + Month {lp['month_reduced']} "
          f"+ Year {current_year}→{py['year_red']} "
          f"= {lp['day_reduced']+lp['month_reduced']+py['year_red']} "
          f"→ {r['personal_year']}")

    print(f"\n{SEP2}\n")


# ── Tests ─────────────────────────────────────────────────────────────
def run_tests():
    """
    Verify core logic with known-good values.
    Test subject: 'Jyotirmoy Giri', DOB 1982-02-21
    """
    print("Running tests...\n")
    errors = []

    # ── Test: reduce() ────────────────────────────────────────
    cases_reduce = [
        (9,  9),   (10, 1),  (11, 11), (22, 22),
        (33, 33),  (29, 11), (38, 11), (47, 11),
        (44, 8),   (99, 9),  (0,  0),
    ]
    for inp, exp in cases_reduce:
        got = reduce(inp)
        ok  = got == exp
        if not ok: errors.append(f"reduce({inp}): expected {exp}, got {got}")
        print(f"  reduce({inp:>3}) = {got}  {'✅' if ok else '❌ expected '+str(exp)}")

    print()

    # ── Test: Life Path ───────────────────────────────────────
    # Jyotirmoy Giri, DOB 1982-02-21
    # day=21→3, month=2→2, year=1+9+8+2=20→2, sum=7
    lp = life_path('1982-02-21')
    exp_lp = 7
    ok = lp == exp_lp
    if not ok: errors.append(f"life_path: expected {exp_lp}, got {lp}")
    print(f"  life_path('1982-02-21') = {lp}  {'✅' if ok else '❌ expected '+str(exp_lp)}")

    # Additional DOB test
    lp2 = life_path('1990-11-29')
    # day=29→11(M), month=11(M), year=1+9+9+0=19→10→1  sum=11+11+1=23→5
    print(f"  life_path('1990-11-29') = {lp2}  (Master Numbers: 11+11+1=23→5, expected 5) "
          f"{'✅' if lp2==5 else '❌ expected 5'}")
    if lp2 != 5: errors.append(f"life_path('1990-11-29'): expected 5, got {lp2}")

    print()

    # ── Test: Destiny ─────────────────────────────────────────
    # 'Jyotirmoy Giri'
    # J=1,Y=7,O=6,T=2,I=9,R=9,M=4,O=6,Y=7 → 51
    # G=7,I=9,R=9,I=9 → 34
    # total=85 → 13 → 4
    dst = destiny('Jyotirmoy Giri')
    exp_dst = 4
    ok = dst == exp_dst
    if not ok: errors.append(f"destiny: expected {exp_dst}, got {dst}")
    print(f"  destiny('Jyotirmoy Giri') = {dst}  {'✅' if ok else '❌ expected '+str(exp_dst)}")

    print()

    # ── Test: Soul Urge ───────────────────────────────────────
    # Vowels in 'Jyotirmoy Giri': O I O I I
    # Values: O=6, I=9, O=6, I=9, I=9 → sum=39 → 12 → 3
    su = soul_urge('Jyotirmoy Giri')
    exp_su = 3
    ok = su == exp_su
    if not ok: errors.append(f"soul_urge: expected {exp_su}, got {su}")
    print(f"  soul_urge('Jyotirmoy Giri') = {su}  {'✅' if ok else '❌ expected '+str(exp_su)}")

    # Case insensitivity test
    su_lower = soul_urge('jyotirmoy giri')
    ok2 = su_lower == exp_su
    if not ok2: errors.append(f"soul_urge (lowercase): expected {exp_su}, got {su_lower}")
    print(f"  soul_urge('jyotirmoy giri') = {su_lower}  "
          f"{'✅ case-insensitive' if ok2 else '❌ expected '+str(exp_su)}")

    # Master Number soul urge
    su_master = soul_urge('Lee')  # L-E-E: vowels E+E=5+5=10→1... let's just check no crash
    print(f"  soul_urge('Lee') = {su_master}  (E+E=10→1) "
          f"{'✅' if su_master==1 else '❌ expected 1'}")
    if su_master != 1: errors.append(f"soul_urge('Lee'): expected 1, got {su_master}")

    print()

    # ── Test: Personality ────────────────────────────────────
    # Consonants: J Y T R M Y  G R  → 1+7+2+9+4+7+7+9 = 46 → 10 → 1
    pn = personality('Jyotirmoy Giri')
    exp_pn = 1
    ok = pn == exp_pn
    if not ok: errors.append(f"personality: expected {exp_pn}, got {pn}")
    print(f"  personality('Jyotirmoy Giri') = {pn}  {'✅' if ok else '❌ expected '+str(exp_pn)}")

    # Sanity: destiny = soul_urge_raw + personality_raw (pre-reduce)
    upper = 'JYOTIRMOYGIRI'
    raw_su = sum(PYTHAGOREAN[c] for c in upper if c in VOWELS)
    raw_pn = sum(PYTHAGOREAN[c] for c in upper if c in CONSONANTS)
    raw_dst= sum(PYTHAGOREAN[c] for c in upper if c in PYTHAGOREAN)
    ok_sanity = (raw_su + raw_pn) == raw_dst
    print(f"\n  Sanity: soul_urge_raw({raw_su}) + personality_raw({raw_pn}) "
          f"= {raw_su+raw_pn} == destiny_raw({raw_dst})  "
          f"{'✅' if ok_sanity else '❌'}")
    if not ok_sanity: errors.append("raw_su + raw_pn != raw_dst")

    print()

    # ── Test: Personal Year ───────────────────────────────────
    py = personal_year('1982-02-21', 2026)
    # day=3, month=2, year=2026→2+0+2+6=10→1 → 3+2+1=6
    exp_py = 6
    ok = py == exp_py
    if not ok: errors.append(f"personal_year(2026): expected {exp_py}, got {py}")
    print(f"  personal_year('1982-02-21', 2026) = {py}  "
          f"{'✅' if ok else '❌ expected '+str(exp_py)}")

    # ── Summary ───────────────────────────────────────────────
    print()
    if errors:
        print(f"❌ {len(errors)} test(s) FAILED:")
        for e in errors:
            print(f"   • {e}")
    else:
        print("✅ All tests passed.")
    print()
    return len(errors) == 0


# ── Entry point ───────────────────────────────────────────────────────
if __name__ == '__main__':
    # Run tests first
    all_passed = run_tests()

    # Full report for the subject
    print_report('Jyotirmoy Giri', '1982-02-21', 2026)
