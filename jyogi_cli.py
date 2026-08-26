#!/usr/bin/env python3
"""
Jyogi CLI — paste birth details, get a Vedic chart in the terminal.

USAGE
  1) Interactive paste:
       python3 jyogi_cli.py
     then paste the block and press Ctrl-D (Mac/Linux) or Ctrl-Z Enter (Windows).

  2) From a file:
       python3 jyogi_cli.py details.txt

  3) Piped:
       cat details.txt | python3 jyogi_cli.py

ACCEPTED PASTE FORMAT (labels are flexible, order doesn't matter):
  Date of birth:
  07.06.1990 (35y)
  Time of birth:
  No data
  Place of birth:
  Greenwich, Greater London, United Kingdom

Date accepts: DD.MM.YYYY, DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD, "7 June 1990".
Time accepts: HH:MM, "8:30 am", "No data" (unknown → noon used, Lagna flagged approximate).
Place: free text; a small built-in gazetteer covers common cities. Unknown places
       fall back to 0,0 (you can pass --lat/--lon to override).
"""

import sys, re, argparse, datetime, unicodedata, json, urllib.request, urllib.error, urllib.parse, webbrowser

# Use the project's own engine
try:
    import vedic_engine as VE
except Exception as e:
    print("ERROR: could not import vedic_engine.py — run this from the folder that contains it.")
    print(f"  ({e})")
    sys.exit(1)

# ── Network geocoder (your live API) — optional fallback ─────────────
API_BASE = "https://jyogi-api.onrender.com"

def api_geocode(city: str, timeout: float = 10.0):
    """Call POST /api/geocode → {lat, lon, address} or None."""
    if not city or not city.strip():
        return None
    body = json.dumps({"city": city.strip()}).encode("utf-8")
    req  = urllib.request.Request(
        API_BASE + "/api/geocode",
        data=body,
        headers={"Content-Type": "application/json",
                 "User-Agent": "jyogi-cli/1.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        print(f"  (geocode HTTP {e.code} — falling back)")
        return None
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        print(f"  (geocode unreachable: {e} — falling back)")
        return None
    except Exception as e:
        print(f"  (geocode error: {e} — falling back)")
        return None

def estimate_tz_from_lon(lon: float) -> float:
    """Rough TZ from longitude (15° per hour). Caller can override with --tz.
    Snaps to half-hour for India-like offsets where common (e.g. lon ~75 → 5.0,
    but India is 5.5). Use --tz for surgical accuracy."""
    return round(lon / 15.0 * 2) / 2.0   # nearest 0.5 hour

# ── Small built-in gazetteer (lat, lon, tz_offset_hours) ─────────────
# tz offset is standard time; used only to convert local clock → UT.
GAZETTEER = {
    'greenwich':        (51.4779,  -0.0015,  0.0),
    'london':           (51.5074,  -0.1278,  0.0),
    'mumbai':           (19.0760,  72.8777,  5.5),
    'delhi':            (28.6139,  77.2090,  5.5),
    'new delhi':        (28.6139,  77.2090,  5.5),
    'bengaluru':        (12.9716,  77.5946,  5.5),
    'bangalore':        (12.9716,  77.5946,  5.5),
    'kolkata':          (22.5726,  88.3639,  5.5),
    'chennai':          (13.0827,  80.2707,  5.5),
    'hyderabad':        (17.3850,  78.4867,  5.5),
    'pune':             (18.5204,  73.8567,  5.5),
    'ahmedabad':        (23.0225,  72.5714,  5.5),
    'jaipur':           (26.9124,  75.7873,  5.5),
    'anantapur':        (14.6819,  77.6006,  5.5),
    'jajpur':           (20.8500,  86.3300,  5.5),
    'new york':         (40.7128, -74.0060, -5.0),
    'dubai':            (25.2048,  55.2708,  4.0),
    'singapore':        ( 1.3521, 103.8198,  8.0),
}

MONTHS = {m.lower():i+1 for i,m in enumerate(
    ['January','February','March','April','May','June','July',
     'August','September','October','November','December'])}
MONTHS.update({m[:3].lower():i+1 for m,i in
    [(k,v) for k,v in zip(
        ['January','February','March','April','May','June','July',
         'August','September','October','November','December'], range(1,13))]})


def _norm(s):
    return unicodedata.normalize('NFKD', s).strip()


def parse_block(text):
    """Parse a pasted birth-details block into {date,time,place} raw strings."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    out = {'date': None, 'time': None, 'place': None}
    # Label → key, with the value usually on the SAME line or the NEXT line
    label_map = [
        (r'date\s*of\s*birth|^dob\b|^born', 'date'),
        (r'time\s*of\s*birth|^tob\b',       'time'),
        (r'place\s*of\s*birth|^pob\b|^location|^city', 'place'),
    ]
    i = 0
    while i < len(lines):
        line = lines[i]
        low = line.lower()
        matched = None
        for pat, key in label_map:
            if re.search(pat, low):
                matched = key
                # value after a colon on same line?
                after = line.split(':', 1)[1].strip() if ':' in line else ''
                if after:
                    out[key] = after
                elif i + 1 < len(lines):
                    out[key] = lines[i+1].strip()
                    i += 1
                break
        i += 1
    # Fallback: if no labels found, try positional (line1=date, line2=time, line3=place)
    if not any(out.values()) and len(lines) >= 1:
        if len(lines) >= 1: out['date']  = lines[0]
        if len(lines) >= 2: out['time']  = lines[1]
        if len(lines) >= 3: out['place'] = lines[2]
    return out


def parse_date(s):
    """Return (year, month, day) or None."""
    if not s:
        return None
    s = s.strip()
    # strip trailing "(35y)" age note
    s = re.sub(r'\(.*?\)', '', s).strip()
    # numeric DD.MM.YYYY / DD/MM/YYYY / DD-MM-YYYY
    m = re.match(r'^(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{4})$', s)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return (y, mo, d)
    # ISO YYYY-MM-DD
    m = re.match(r'^(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})$', s)
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    # "7 June 1990" / "7 Jun 1990"
    m = re.match(r'^(\d{1,2})\s+([A-Za-z]+)\.?\s+(\d{4})$', s)
    if m and m.group(2).lower() in MONTHS:
        return (int(m.group(3)), MONTHS[m.group(2).lower()], int(m.group(1)))
    # "June 7 1990"
    m = re.match(r'^([A-Za-z]+)\.?\s+(\d{1,2}),?\s+(\d{4})$', s)
    if m and m.group(1).lower() in MONTHS:
        return (int(m.group(3)), MONTHS[m.group(1).lower()], int(m.group(2)))
    return None


def parse_time(s):
    """Return (hour24, minute, known_bool)."""
    if not s or re.search(r'no\s*data|unknown|n/?a|none', s, re.I):
        return (12, 0, False)   # default noon when unknown
    s = s.strip().lower()
    ampm = None
    if 'am' in s: ampm = 'am'
    if 'pm' in s: ampm = 'pm'
    m = re.search(r'(\d{1,2}):(\d{2})', s)
    if not m:
        m2 = re.search(r'^(\d{1,2})\s*(am|pm)?$', s)
        if m2:
            h = int(m2.group(1)); mn = 0
        else:
            return (12, 0, False)
    else:
        h, mn = int(m.group(1)), int(m.group(2))
    if ampm == 'pm' and h < 12: h += 12
    if ampm == 'am' and h == 12: h = 0
    return (h % 24, mn % 60, True)


def resolve_place(s, lat_override=None, lon_override=None, tz_override=None, use_network=True):
    """Return (lat, lon, tz_hours, label, found_bool, source)."""
    if lat_override is not None and lon_override is not None:
        return (lat_override, lon_override,
                tz_override if tz_override is not None else 0.0,
                s or "custom", True, "override")
    if not s:
        return (0.0, 0.0, 0.0, "unknown", False, "none")
    key = s.lower()
    # 1) Built-in gazetteer first (fast, offline, exact TZ)
    candidates = [key] + [c.strip() for c in key.split(',')]
    for c in candidates:
        if c in GAZETTEER:
            lat, lon, tz = GAZETTEER[c]
            return (lat, lon, tz, s, True, "gazetteer")
    # 2) Live API geocode fallback
    if use_network:
        geo = api_geocode(s)
        if geo and 'lat' in geo and 'lon' in geo:
            lat = float(geo['lat']); lon = float(geo['lon'])
            tz  = tz_override if tz_override is not None else estimate_tz_from_lon(lon)
            label = geo.get('address') or s
            return (lat, lon, tz, label, True, "api")
    # 3) Nothing matched
    return (0.0, 0.0, 0.0, s, False, "none")


def deg_to_sign(lon):
    sign = VE.RASHIS[int(lon // 30) % 12]
    d = lon % 30
    return sign, d


def run(date_str, time_str, place_str, lat=None, lon=None, tz=None, use_network=True):
    ymd = parse_date(date_str)
    if not ymd:
        print(f"❌ Could not parse date: {date_str!r}")
        print("   Try DD.MM.YYYY (e.g. 07.06.1990) or '7 June 1990'.")
        return
    y, mo, d = ymd
    hh, mm, time_known = parse_time(time_str)
    plat, plon, ptz, plabel, found, src = resolve_place(
        place_str, lat, lon, tz, use_network=use_network)

    # Local clock → UT
    h_local = hh + mm/60.0
    h_ut = h_local - ptz
    jd = VE.julian_day(y, mo, d, h_ut)

    planets = VE.get_all_planets(jd)
    moon = planets.get('Moon', 0.0)
    lagna_lon = VE.get_lagna(jd, plat, plon)
    dasha = VE.get_dasha(moon, jd)
    # Compute the full Vimshottari cycle ourselves so it always reaches today.
    today = datetime.date.today()
    cur_lord = dasha.get('current_lord', '?')
    yrs_left = '?'
    seq = dasha.get('sequence', [])
    if seq:
        try:
            cycle_start = datetime.datetime.strptime(seq[0]['start'], '%d %b %Y').date()
            # Walk forward through repeating Dasha order from the first segment's lord
            order_lords = VE.DASHA_SEQ
            order_yrs   = dict(zip(VE.DASHA_SEQ, VE.DASHA_YRS))
            start_idx = order_lords.index(seq[0]['lord'])
            cursor = cycle_start
            for k in range(18):  # 18 segments ≈ two full 120-yr cycles, always covers today
                lord = order_lords[(start_idx + k) % 9]
                span_days = order_yrs[lord] * 365.25
                seg_end = cursor + datetime.timedelta(days=span_days)
                if cursor <= today < seg_end:
                    cur_lord = lord
                    yrs_left = round((seg_end - today).days / 365.25, 1)
                    break
                cursor = seg_end
        except Exception:
            pass
    nk_idx = int(moon / (360/27))
    pada = int((moon % (360/27)) / ((360/27)/4)) + 1

    # ── Output ──
    W = 64
    print("\n" + "═"*W)
    print("  JYOGI · VEDIC CHART (Lahiri / Swiss Ephemeris)".center(W))
    print("═"*W)
    print(f"  Date   : {datetime.date(y,mo,d).strftime('%d %B %Y')}")
    if time_known:
        print(f"  Time   : {hh:02d}:{mm:02d} (local)   TZ {ptz:+.1f}h → UT {h_ut:.2f}")
    else:
        print(f"  Time   : UNKNOWN → noon assumed.  ⚠ Lagna & houses approximate.")
    pf = "" if found else "  ⚠ not resolved — used 0°,0°. Pass --lat/--lon or check spelling."
    tz_note = ""
    if found and src == "api" and tz is None:
        tz_note = f"  (TZ estimated from longitude; use --tz for precision)"
    print(f"  Place  : {plabel}{pf}")
    print(f"  Coords : {plat:.4f}, {plon:.4f}   [{src}]{tz_note}")
    print("─"*W)

    lsign, ldeg = deg_to_sign(lagna_lon)
    msign, mdeg = deg_to_sign(moon)
    print(f"  Lagna     : {lsign}  {ldeg:5.2f}°" + ("" if time_known else "   (approx)"))
    print(f"  Moon      : {msign}  {mdeg:5.2f}°")
    print(f"  Nakshatra : {VE.NAKSH[nk_idx]}  ·  Pada {pada}")
    print(f"  Mahadasha : {cur_lord}   (≈{yrs_left} yrs remaining)")
    print("─"*W)
    print("  PLANETARY POSITIONS (sidereal)")
    for p in VE.PLANETS:
        s, dg = deg_to_sign(planets[p])
        house = VE.get_house(planets[p], lagna_lon)
        retro = ""
        try:
            if VE.get_planet_retrograde(p, jd): retro = "  ℞"
        except Exception:
            pass
        hs = f"H{house}" if time_known else "—"
        print(f"    {p:<8} {s:<12} {dg:5.2f}°   {hs}{retro}")
    print("═"*W)
    if not time_known:
        print("  Note: With no birth time, Moon/nakshatra/dasha are reliable,")
        print("  but Lagna, house placements & timed events are approximate.")
        print("═"*W)
    print()


def build_jyogi_url(date_str, time_str, place_str, question=None, auto=False,
                    base="https://jyogi.in"):
    """Build a jyogi.in URL with the birth details encoded as query params."""
    params = {}
    ymd = parse_date(date_str)
    if ymd:
        y, mo, d = ymd
        params['d'] = str(d); params['m'] = str(mo); params['y'] = str(y)
    # Convert 24h → 12h + AM/PM for the web form
    if time_str and not re.search(r'no\s*data|unknown|n/?a|none', time_str, re.I):
        hh, mm, _ = parse_time(time_str)
        if hh == 0:
            params['h'] = '12'; params['ampm'] = 'AM'
        elif hh < 12:
            params['h'] = str(hh); params['ampm'] = 'AM'
        elif hh == 12:
            params['h'] = '12'; params['ampm'] = 'PM'
        else:
            params['h'] = str(hh - 12); params['ampm'] = 'PM'
        params['min'] = str(mm)
    if place_str:
        params['city'] = place_str.strip()
    if question:
        params['q'] = question.strip()
    if auto:
        params['auto'] = '1'
    return base + "/?" + urllib.parse.urlencode(params)


def open_in_browser(url):
    """Open URL in the user's default browser. Returns True on success."""
    try:
        return webbrowser.open(url, new=2)  # new=2 = open in new tab if possible
    except Exception as e:
        print(f"  (could not auto-open browser: {e})")
        return False


def main():
    ap = argparse.ArgumentParser(description="Jyogi CLI — paste birth details, get a Vedic chart.")
    ap.add_argument('file', nargs='?', help="optional text file with the pasted block")
    ap.add_argument('--lat', type=float, help="override latitude")
    ap.add_argument('--lon', type=float, help="override longitude")
    ap.add_argument('--tz',  type=float, help="override timezone offset hours (e.g. 5.5)")
    ap.add_argument('--offline', action='store_true',
                    help="skip network geocoder; gazetteer + --lat/--lon only")
    ap.add_argument('--no-browser', action='store_true', dest='no_browser',
                    help="don't open jyogi.in after printing the terminal chart")
    ap.add_argument('--auto-submit', action='store_true', dest='auto_submit',
                    help="auto-submit the form on jyogi.in (otherwise just pre-fills)")
    ap.add_argument('--site', default='https://jyogi.in',
                    help="base URL for the site (default https://jyogi.in)")
    args = ap.parse_args()

    if args.file:
        text = open(args.file, encoding='utf-8').read()
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        # Interactive paste: read lines until BLANK line OR Ctrl-D.
        # This is more discoverable than Ctrl-D.
        print("Paste the birth details below, then press Enter on a blank line to finish")
        print("(or press Ctrl-D / Ctrl-Z Enter):\n")
        lines = []
        try:
            while True:
                line = input()
                if line.strip() == "" and lines:
                    # blank line after at least some input → done
                    break
                if line.strip() != "":
                    lines.append(line)
        except EOFError:
            pass
        text = "\n".join(lines)

    parsed = parse_block(text)
    if not parsed.get('date'):
        print("❌ No date of birth found in the pasted text.")
        print("   Expected something like:\n     Date of birth:\n     07.06.1990")
        sys.exit(1)
    run(parsed['date'], parsed.get('time'), parsed.get('place'),
        lat=args.lat, lon=args.lon, tz=args.tz,
        use_network=not args.offline)

    # After terminal chart, open the live site with pre-filled form
    if not args.no_browser:
        url = build_jyogi_url(
            parsed['date'], parsed.get('time'), parsed.get('place'),
            auto=args.auto_submit, base=args.site,
        )
        print(f"\n  🌐 Opening in browser:")
        print(f"  {url}\n")
        open_in_browser(url)


if __name__ == '__main__':
    main()
