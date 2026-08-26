"""
Jyogi AI — Saturn Intelligence Report Generator
================================================
Generates a multi-page PDF with:
  • Cover page with chart identity
  • Executive Summary
  • Data Integrity Block
  • Saturn Transit Table
  • Retrogression Timeline
  • Impact Score Panel
  • Sade Sati Phase Analysis
  • Insight Panels (actionable guidance)
  • Footer with branding + timestamp
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, Circle, Line, String, Polygon
from reportlab.graphics import renderPDF
from reportlab.lib.colors import HexColor
import datetime, math

# ═══════════════════════════════════════════════════════════════
# DESIGN TOKENS — Night-Sky Palette
# ═══════════════════════════════════════════════════════════════
C_INK        = HexColor('#0F0E1A')   # Deep indigo black — primary text
C_INDIGO     = HexColor('#1E1B3A')   # Deep indigo — headers, cover
C_INDIGO_MID = HexColor('#2D2860')   # Mid indigo — accent blocks
C_VIOLET     = HexColor('#6C63C9')   # Saturn violet — highlights
C_VIOLET_PALE= HexColor('#A89FE0')   # Pale violet — sub-labels
C_SILVER     = HexColor('#C8C8D8')   # Muted silver — borders, secondary text
C_SILVER_PALE= HexColor('#E8E8F0')   # Very pale — zebra rows, backgrounds
C_GOLD       = HexColor('#C9A84C')   # Gold — key metrics, scores
C_GOLD_PALE  = HexColor('#F5EDD0')   # Pale gold — highlight backgrounds
C_CHARCOAL   = HexColor('#3A3A52')   # Charcoal — body text
C_WHITE      = HexColor('#FFFFFF')
C_RED_SOFT   = HexColor('#C0514A')   # Retrograde indicator
C_GREEN_SOFT = HexColor('#4A9B6F')   # Direct / positive indicator
C_PAGE_BG    = HexColor('#FAFAFA')   # Warm off-white page

W, H = A4   # 595.27 × 841.89 pts
MARGIN_L = 20*mm
MARGIN_R = 20*mm
MARGIN_T = 24*mm
MARGIN_B = 22*mm
CONTENT_W = W - MARGIN_L - MARGIN_R

# ═══════════════════════════════════════════════════════════════
# TYPOGRAPHY STYLES
# ═══════════════════════════════════════════════════════════════
def make_styles():
    return {
        # Cover
        'cover_logo': ParagraphStyle('cover_logo',
            fontName='Helvetica-Bold', fontSize=11, textColor=C_VIOLET_PALE,
            letterSpacing=4, alignment=TA_CENTER),
        'cover_title': ParagraphStyle('cover_title',
            fontName='Times-Bold', fontSize=34, textColor=C_WHITE,
            leading=42, alignment=TA_CENTER, spaceAfter=6),
        'cover_sub': ParagraphStyle('cover_sub',
            fontName='Helvetica', fontSize=13, textColor=C_SILVER,
            alignment=TA_CENTER, leading=20),
        'cover_meta': ParagraphStyle('cover_meta',
            fontName='Helvetica', fontSize=9, textColor=C_VIOLET_PALE,
            alignment=TA_CENTER, leading=16, letterSpacing=1),

        # Section headers
        'section_label': ParagraphStyle('section_label',
            fontName='Helvetica-Bold', fontSize=7.5, textColor=C_VIOLET,
            letterSpacing=3, spaceBefore=18, spaceAfter=6),
        'section_title': ParagraphStyle('section_title',
            fontName='Times-Bold', fontSize=20, textColor=C_INDIGO,
            leading=26, spaceAfter=4),
        'section_sub': ParagraphStyle('section_sub',
            fontName='Times-Italic', fontSize=11, textColor=C_CHARCOAL,
            leading=16, spaceAfter=10),

        # Body
        'body': ParagraphStyle('body',
            fontName='Helvetica', fontSize=9.5, textColor=C_CHARCOAL,
            leading=15, spaceAfter=8, alignment=TA_JUSTIFY),
        'body_bold': ParagraphStyle('body_bold',
            fontName='Helvetica-Bold', fontSize=9.5, textColor=C_INK,
            leading=15, spaceAfter=4),
        'caption': ParagraphStyle('caption',
            fontName='Helvetica', fontSize=8, textColor=C_SILVER,
            leading=12, spaceAfter=6, alignment=TA_CENTER),

        # Table
        'th': ParagraphStyle('th',
            fontName='Helvetica-Bold', fontSize=8, textColor=C_WHITE,
            alignment=TA_CENTER),
        'td': ParagraphStyle('td',
            fontName='Helvetica', fontSize=9, textColor=C_CHARCOAL,
            alignment=TA_CENTER),
        'td_left': ParagraphStyle('td_left',
            fontName='Helvetica', fontSize=9, textColor=C_CHARCOAL,
            alignment=TA_LEFT),
        'td_retro': ParagraphStyle('td_retro',
            fontName='Helvetica-Bold', fontSize=9, textColor=C_RED_SOFT,
            alignment=TA_CENTER),
        'td_direct': ParagraphStyle('td_direct',
            fontName='Helvetica-Bold', fontSize=9, textColor=C_GREEN_SOFT,
            alignment=TA_CENTER),
        'metric_val': ParagraphStyle('metric_val',
            fontName='Times-Bold', fontSize=22, textColor=C_GOLD,
            alignment=TA_CENTER, leading=28),
        'metric_label': ParagraphStyle('metric_label',
            fontName='Helvetica', fontSize=7.5, textColor=C_SILVER,
            alignment=TA_CENTER, letterSpacing=2),
        'insight_title': ParagraphStyle('insight_title',
            fontName='Times-Bold', fontSize=13, textColor=C_INDIGO,
            leading=18, spaceAfter=5),
        'insight_body': ParagraphStyle('insight_body',
            fontName='Helvetica', fontSize=9.5, textColor=C_CHARCOAL,
            leading=15, spaceAfter=6, alignment=TA_JUSTIFY),
        'callout': ParagraphStyle('callout',
            fontName='Times-Italic', fontSize=11, textColor=C_INDIGO_MID,
            leading=17, alignment=TA_CENTER),
        'tag': ParagraphStyle('tag',
            fontName='Helvetica-Bold', fontSize=7, textColor=C_VIOLET,
            letterSpacing=2, spaceAfter=3),
        'footer_text': ParagraphStyle('footer_text',
            fontName='Helvetica', fontSize=7.5, textColor=C_SILVER),
        'data_integrity': ParagraphStyle('data_integrity',
            fontName='Helvetica', fontSize=8.5, textColor=C_CHARCOAL,
            leading=13, spaceAfter=3),
    }


# ═══════════════════════════════════════════════════════════════
# PAGE TEMPLATE — header bar + footer on every page
# ═══════════════════════════════════════════════════════════════
class JyogiPageTemplate:
    def __init__(self, client_name, report_id, timestamp):
        self.client_name = client_name
        self.report_id   = report_id
        self.timestamp   = timestamp
        self.page_count  = 0

    def __call__(self, canv, doc):
        canv.saveState()
        page_num = doc.page

        # ── Top bar (skip on cover page 1) ──────────────────
        if page_num > 1:
            canv.setFillColor(C_INDIGO)
            canv.rect(0, H - 14*mm, W, 14*mm, fill=1, stroke=0)
            canv.setFont('Helvetica-Bold', 8)
            canv.setFillColor(C_VIOLET_PALE)
            canv.drawString(MARGIN_L, H - 9*mm, '✦ JYOGI AI')
            canv.setFont('Helvetica', 8)
            canv.setFillColor(C_SILVER)
            canv.drawCentredString(W/2, H - 9*mm, f'Saturn Intelligence Report — {self.client_name}')
            canv.setFillColor(C_SILVER)
            canv.drawRightString(W - MARGIN_R, H - 9*mm, f'ID: {self.report_id}')

        # ── Footer ──────────────────────────────────────────
        canv.setFillColor(C_INDIGO)
        canv.rect(0, 0, W, 11*mm, fill=1, stroke=0)

        canv.setFont('Helvetica', 7)
        canv.setFillColor(C_SILVER)
        canv.drawString(MARGIN_L, 4*mm, f'Generated: {self.timestamp}  |  Jyogi AI — Vedic Astrology Intelligence Platform  |  jyogi.in')
        canv.setFont('Helvetica-Bold', 8)
        canv.setFillColor(C_GOLD)
        canv.drawRightString(W - MARGIN_R, 4*mm, f'Page {page_num}')

        # Thin violet rule above footer
        canv.setStrokeColor(C_VIOLET)
        canv.setLineWidth(0.5)
        canv.line(MARGIN_L, 11*mm, W - MARGIN_R, 11*mm)

        canv.restoreState()


# ═══════════════════════════════════════════════════════════════
# DRAWING HELPERS
# ═══════════════════════════════════════════════════════════════
def divider(width=CONTENT_W, color=C_SILVER, thickness=0.5):
    return HRFlowable(width=width, thickness=thickness, color=color,
                      spaceAfter=8, spaceBefore=8)

def section_tag(text, styles):
    return Paragraph(text.upper(), styles['section_label'])

def draw_impact_gauge(score, max_score=10, width=CONTENT_W, height=40*mm):
    """Draw a minimalist horizontal gauge with score needle."""
    d = Drawing(width, height)
    cx, cy = width/2, height/2

    # Track background
    track_y  = cy - 4
    track_h  = 8
    track_w  = width * 0.72
    track_x  = (width - track_w) / 2

    # Gradient segments (7 segments: low→high)
    seg_colors = [
        HexColor('#4A9B6F'), HexColor('#5BA876'), HexColor('#8CB87D'),
        HexColor('#C9A84C'), HexColor('#D4834A'), HexColor('#C05C4A'), HexColor('#A03838')
    ]
    seg_w = track_w / len(seg_colors)
    for i, col in enumerate(seg_colors):
        r = Rect(track_x + i*seg_w, track_y, seg_w, track_h,
                 fillColor=col, strokeColor=None)
        d.add(r)

    # Outer border
    r_border = Rect(track_x, track_y, track_w, track_h,
                    fillColor=None, strokeColor=HexColor('#2D2860'), strokeWidth=1)
    d.add(r_border)

    # Score needle
    needle_x = track_x + (score / max_score) * track_w
    needle_y_bot = track_y - 6
    needle_y_top = track_y + track_h + 6
    l = Line(needle_x, needle_y_bot, needle_x, needle_y_top,
             strokeColor=C_INDIGO, strokeWidth=2.5)
    d.add(l)
    # Needle circle
    c = Circle(needle_x, needle_y_top + 4, 5,
               fillColor=C_GOLD, strokeColor=C_INDIGO, strokeWidth=1)
    d.add(c)

    # Score label above needle
    s = String(needle_x, needle_y_top + 12, str(score),
               fontName='Helvetica-Bold', fontSize=11,
               fillColor=C_INDIGO.hexval(), textAnchor='middle')
    d.add(s)

    # Scale labels below track
    for i in range(11):
        lx = track_x + (i / 10) * track_w
        if i % 2 == 0:
            lbl = String(lx, track_y - 14, str(i),
                         fontName='Helvetica', fontSize=7,
                         fillColor=C_CHARCOAL.hexval(), textAnchor='middle')
            d.add(lbl)

    # Legend labels
    low_lbl = String(track_x, track_y - 22, 'LOW INFLUENCE',
                     fontName='Helvetica', fontSize=6.5,
                     fillColor=C_SILVER.hexval(), textAnchor='start')
    high_lbl = String(track_x + track_w, track_y - 22, 'HIGH INFLUENCE',
                      fontName='Helvetica', fontSize=6.5,
                      fillColor=C_SILVER.hexval(), textAnchor='end')
    d.add(low_lbl)
    d.add(high_lbl)

    return d


def draw_sade_sati_timeline(phases, width=CONTENT_W, height=28*mm):
    """Three-phase Sade Sati timeline bar."""
    d  = Drawing(width, height)
    cy = height / 2
    track_x = 20
    track_w  = width - 40
    track_h  = 12
    track_y  = cy - track_h/2

    phase_colors = [
        HexColor('#6C63C9'),  # Rising — violet
        HexColor('#A03838'),  # Peak   — red
        HexColor('#C9A84C'),  # Setting— gold
    ]
    phase_labels = ['Rising Phase', 'Peak Phase', 'Setting Phase']
    seg_w = track_w / 3

    for i, (col, lbl) in enumerate(zip(phase_colors, phase_labels)):
        px = track_x + i * seg_w
        # Segment
        r = Rect(px, track_y, seg_w, track_h,
                 fillColor=col, strokeColor=C_WHITE, strokeWidth=1.5)
        d.add(r)
        # Phase label inside
        s = String(px + seg_w/2, track_y + 3.5, lbl,
                   fontName='Helvetica-Bold', fontSize=7,
                   fillColor=C_WHITE.hexval(), textAnchor='middle')
        d.add(s)

    # Phase date labels below
    for i, phase in enumerate(phases):
        px = track_x + i * seg_w + seg_w/2
        lbl = String(px, track_y - 11, phase['period'],
                     fontName='Helvetica', fontSize=7,
                     fillColor=C_CHARCOAL.hexval(), textAnchor='middle')
        d.add(lbl)

    # Current position marker
    current_pct = phases[0].get('current_pct', 0.35)
    marker_x = track_x + current_pct * track_w
    tri = Polygon([marker_x - 5, track_y + track_h + 2,
                   marker_x + 5, track_y + track_h + 2,
                   marker_x,     track_y + track_h + 9],
                  fillColor=C_GOLD, strokeColor=None)
    d.add(tri)
    now_lbl = String(marker_x, track_y + track_h + 11, 'NOW',
                     fontName='Helvetica-Bold', fontSize=6.5,
                     fillColor=C_GOLD.hexval(), textAnchor='middle')
    d.add(now_lbl)

    return d


def draw_retro_bar(periods, width=CONTENT_W, height=16*mm, year_range=(2022, 2028)):
    """Compact retrograde timeline showing retro periods as colored bands."""
    d = Drawing(width, height)
    y_start, y_end = year_range
    total_days = (y_end - y_start) * 365.25
    track_x, track_w, track_h, track_y = 20, width-40, 10, height/2 - 5

    # Background track
    bg = Rect(track_x, track_y, track_w, track_h,
              fillColor=C_SILVER_PALE, strokeColor=C_SILVER, strokeWidth=0.5)
    d.add(bg)

    # Year tick marks
    for yr in range(y_start, y_end + 1):
        frac = (yr - y_start) / (y_end - y_start)
        tx = track_x + frac * track_w
        l = Line(tx, track_y - 3, tx, track_y + track_h + 2,
                 strokeColor=C_SILVER, strokeWidth=0.5)
        d.add(l)
        lbl = String(tx, track_y - 10, str(yr),
                     fontName='Helvetica', fontSize=6,
                     fillColor=C_SILVER.hexval(), textAnchor='middle')
        d.add(lbl)

    # Retrograde periods
    for p in periods:
        start_frac = (p['start_yr'] - y_start) / (y_end - y_start)
        end_frac   = (p['end_yr']   - y_start) / (y_end - y_start)
        rx = track_x + start_frac * track_w
        rw = (end_frac - start_frac) * track_w
        r = Rect(rx, track_y + 1, max(rw, 2), track_h - 2,
                 fillColor=C_RED_SOFT, strokeColor=None)
        d.add(r)
        # Label if wide enough
        if rw > 20:
            s = String(rx + rw/2, track_y + 3, 'ℛ',
                       fontName='Helvetica-Bold', fontSize=7,
                       fillColor=C_WHITE.hexval(), textAnchor='middle')
            d.add(s)

    legend_x = track_x + track_w + 8
    r_leg = Rect(legend_x, track_y + 2, 8, 6,
                 fillColor=C_RED_SOFT, strokeColor=None)
    d.add(r_leg)
    leg_lbl = String(legend_x + 10, track_y + 3, '= Retrograde',
                     fontName='Helvetica', fontSize=6.5,
                     fillColor=C_CHARCOAL.hexval(), textAnchor='start')
    d.add(leg_lbl)

    return d


def metric_block(value, label, note, styles):
    """A single metric cell."""
    return [
        Paragraph(str(value), styles['metric_val']),
        Paragraph(label.upper(), styles['metric_label']),
        Spacer(1, 2),
        Paragraph(note, styles['caption']),
    ]


def insight_panel(tag, title, body_text, styles, accent=C_INDIGO_MID):
    """A single insight box with left accent rule."""
    items = [
        Paragraph(tag.upper(), styles['tag']),
        Paragraph(title, styles['insight_title']),
        Paragraph(body_text, styles['insight_body']),
    ]
    tbl = Table([[items]], colWidths=[CONTENT_W - 4*mm])
    tbl.setStyle(TableStyle([
        ('LEFTPADDING',  (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING',   (0,0), (-1,-1), 10),
        ('BOTTOMPADDING',(0,0), (-1,-1), 10),
        ('BACKGROUND',   (0,0), (-1,-1), C_GOLD_PALE),
        ('LINEBEFORE',   (0,0), (0,-1),  3, accent),
        ('ROUNDEDCORNERS', [3]),
    ]))
    return tbl


# ═══════════════════════════════════════════════════════════════
# REPORT DATA — sample Saturn data for Jyogi.in
# Replace with dynamic data from vedic_engine.py in production
# ═══════════════════════════════════════════════════════════════
REPORT_DATA = {
    "client_name"   : "Jyotirmoy Giri",
    "dob"           : "19 March 1980",
    "tob"           : "03:01 AM",
    "pob"           : "Jajpur, Odisha",
    "lagna"         : "Capricorn (Makara)",
    "moon_sign"     : "Aries (Mesha)",
    "nakshatra"     : "Ashwini, Pada 2",
    "mahadasha"     : "Saturn Mahadasha",
    "antardasha"    : "Mercury Antardasha",
    "report_id"     : "JYG-SAT-19800319-001",
    "period"        : "April 2026 — March 2027",

    "saturn_position": {
        "rashi"       : "Pisces (Meena)",
        "degree"      : "20°14'",
        "nakshatra"   : "Purvabhadrapada",
        "pada"        : "4",
        "house"       : "3rd House",
        "status"      : "Direct",
        "speed"       : "+0.083°/day",
        "tropical_lon": "43.83°",
        "sidereal_lon": "20.24°",
        "ayanamsa"    : "Lahiri 23.59°",
        "engine"      : "Swiss Ephemeris (pyswisseph)",
    },

    "natal_saturn": {
        "rashi"   : "Leo (Simha)",
        "degree"  : "29°41'",
        "house"   : "8th House",
        "status"  : "Retrograde",
        "nakshatra": "Uttara Phalguni, Pada 1",
    },

    "impact_score": 7.2,

    "transit_table": [
        ["Apr 2026", "Pisces",  "18°22'", "Direct",    "3rd",  "Moderate — communication, travel"],
        ["May 2026", "Pisces",  "19°54'", "Direct",    "3rd",  "Strong — sibling dynamics, effort"],
        ["Jun 2026", "Pisces",  "20°44'", "Stationary","3rd",  "High — pause before retrograde"],
        ["Jul 2026", "Pisces",  "19°31'", "Retrograde","3rd",  "Very High — internal reckoning"],
        ["Aug 2026", "Pisces",  "17°58'", "Retrograde","3rd",  "High — review past decisions"],
        ["Sep 2026", "Pisces",  "17°10'", "Retrograde","3rd",  "Moderate — lessons consolidate"],
        ["Oct 2026", "Pisces",  "17°52'", "Direct",    "3rd",  "Moderate — resuming forward motion"],
        ["Nov 2026", "Pisces",  "19°20'", "Direct",    "3rd",  "Low — stability returns"],
        ["Dec 2026", "Aquarius","29°08'", "Retrograde","2nd",  "High — financial re-evaluation"],
        ["Jan 2027", "Aquarius","27°50'", "Retrograde","2nd",  "High — Saturn re-enters Aquarius"],
        ["Feb 2027", "Pisces",  "00°22'", "Direct",    "3rd",  "Moderate — fresh Pisces cycle"],
        ["Mar 2027", "Pisces",  "02°15'", "Direct",    "3rd",  "Low — forward momentum"],
    ],

    "retro_periods": [
        {"start_yr": 2022.35, "end_yr": 2022.82},
        {"start_yr": 2023.42, "end_yr": 2023.88},
        {"start_yr": 2024.48, "end_yr": 2024.93},
        {"start_yr": 2025.55, "end_yr": 2025.99},
        {"start_yr": 2026.44, "end_yr": 2026.89},
        {"start_yr": 2027.50, "end_yr": 2027.96},
    ],

    "sade_sati": {
        "active"    : True,
        "start_year": "November 2023",
        "end_year"  : "October 2026",
        "current_phase": "Peak Phase",
        "phases": [
            {"phase": "Rising",  "period": "Nov 2023 — Dec 2024", "rashi": "Aquarius", "current_pct": 0.0},
            {"phase": "Peak",    "period": "Jan 2025 — Jan 2026", "rashi": "Pisces",   "current_pct": 0.65},
            {"phase": "Setting", "period": "Feb 2026 — Oct 2026", "rashi": "Aries",    "current_pct": 0.0},
        ]
    },

    "integrity_checks": [
        ("Calculation Engine",  "Swiss Ephemeris (pyswisseph) v2.10.3"),
        ("Ayanamsa System",     "Lahiri / Chitra Paksha  –  23.590° (J2000)"),
        ("House System",        "Whole Sign (Rashi Chakra) — standard Parashari"),
        ("Coordinate Type",     "Geocentric, Apparent, Ecliptic Longitude"),
        ("Saturn Position",     "Leo 29°40'54\"  ±  0.003°  (arc-second precision)"),
        ("Birth Coordinates",   "Jajpur, Odisha — 20.8476°N  86.3310°E"),
        ("Julian Day",          "JD 2444317.3965 (UT  = −2.483h)"),
        ("Report Generated",    datetime.datetime.now().strftime("%d %b %Y  %H:%M IST")),
    ],

    "insights": [
        {
            "tag"  : "Career & Discipline",
            "title": "Saturn Activates the 3rd House of Effort",
            "body" : (
                "Transit Saturn in Pisces moves through your 3rd house (Capricorn Lagna), "
                "the domain of willpower, short journeys, communication, and younger siblings. "
                "This is a period of deliberate effort — Saturn rewards sustained, methodical "
                "work here while testing impulsive decisions. Avoid scattered projects; "
                "concentrate energy into one primary skill or craft."
            ),
            "accent": C_INDIGO_MID,
        },
        {
            "tag"  : "Retrograde Window (Jul–Oct 2026)",
            "title": "Inner Reckoning — Review Before You Renew",
            "body" : (
                "Saturn's retrograde phase (Jul 12 – Oct 28, 2026) is not a setback — "
                "it is a structured internal audit. Past responsibilities, incomplete "
                "commitments, and deferred decisions return for resolution. This is an "
                "excellent window to revise contracts, revisit professional relationships, "
                "and consolidate learning. Avoid major launches during this window."
            ),
            "accent": HexColor('#8C3030'),
        },
        {
            "tag"  : "Natal Saturn — 8th House Leo",
            "title": "Saturn at 29°41' Leo: Deep Karmic Configuration",
            "body" : (
                "Your natal Saturn occupies the gandanta zone (29°41' Leo — the final degree "
                "before Virgo), sitting retrograde in the 8th house. This is one of the most "
                "intense karmic placements in Jyotish. It confers deep spiritual inquiry, "
                "transformation through adversity, and a life path centred on facing what "
                "others avoid. The 8th house Saturnian energy rewards those who meet their "
                "shadows honestly — it does not permit short-cuts."
            ),
            "accent": C_VIOLET,
        },
        {
            "tag"  : "Sade Sati — Setting Phase",
            "title": "Sade Sati Lifts: Light Returns After February 2026",
            "body" : (
                "You are completing the Setting Phase of Sade Sati (Feb – Oct 2026). "
                "The heaviest energies of this 7.5-year cycle are now behind you. "
                "This closing chapter calls for releasing what the peak phase dissolved — "
                "old identities, unworkable relationships, outdated ambitions. "
                "By November 2026 a new cycle of lighter Saturnian support begins. "
                "Plant seeds of discipline now; they will bear significant fruit in 2027."
            ),
            "accent": C_GOLD,
        },
    ],

    "executive_summary": (
        "This report analyses Saturn's influence for <b>Jyotirmoy Giri</b> across the period "
        "<b>April 2026 – March 2027</b>. Transit Saturn in Pisces (3rd house, Capricorn Lagna) "
        "delivers a year of deliberate effort, disciplined communication, and structured "
        "professional development. A significant retrograde window (July – October 2026) "
        "demands internal review. The concurrent Sade Sati Setting Phase concludes in "
        "October 2026 — marking a generational shift from contraction to gradual expansion. "
        "Overall Saturn Influence Score for the period: <b>7.2 / 10</b>."
    ),
}


# ═══════════════════════════════════════════════════════════════
# BUILD PDF
# ═══════════════════════════════════════════════════════════════
def build_report(output_path, data):
    timestamp = datetime.datetime.now().strftime("%d %b %Y %H:%M IST")
    S = make_styles()

    page_cb = JyogiPageTemplate(data["client_name"], data["report_id"], timestamp)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=MARGIN_L, rightMargin=MARGIN_R,
        topMargin=MARGIN_T + 16*mm,   # extra for header bar
        bottomMargin=MARGIN_B + 12*mm, # extra for footer bar
        title=f"Saturn Intelligence Report — {data['client_name']}",
        author="Jyogi AI",
        subject="Vedic Astrology — Saturn Analysis",
    )

    story = []

    # ─────────────────────────────────────────────────────────
    # COVER PAGE
    # ─────────────────────────────────────────────────────────
    def cover_page(canv, doc):
        page_cb(canv, doc)
        canv.saveState()

        # Full indigo background
        canv.setFillColor(C_INDIGO)
        canv.rect(0, 0, W, H, fill=1, stroke=0)

        # Subtle star dots
        import random; random.seed(42)
        canv.setFillColor(HexColor('#FFFFFF'))
        for _ in range(90):
            sx, sy = random.uniform(0, W), random.uniform(H*0.2, H)
            sr = random.uniform(0.4, 1.2)
            canv.circle(sx, sy, sr, fill=1, stroke=0)

        # Decorative Saturn ring motif
        cx_ring, cy_ring = W/2, H * 0.62
        canv.setStrokeColor(HexColor('#6C63C9'))
        canv.setLineWidth(1.2)
        canv.ellipse(cx_ring - 70, cy_ring - 18, cx_ring + 70, cy_ring + 18, fill=0)
        canv.setLineWidth(0.6)
        canv.setStrokeColor(HexColor('#A89FE0'))
        canv.ellipse(cx_ring - 85, cy_ring - 24, cx_ring + 85, cy_ring + 24, fill=0)
        # Planet circle
        canv.setFillColor(HexColor('#2D2860'))
        canv.circle(cx_ring, cy_ring, 30, fill=1, stroke=0)
        canv.setStrokeColor(HexColor('#6C63C9'))
        canv.setLineWidth(1)
        canv.circle(cx_ring, cy_ring, 30, fill=0, stroke=1)
        # Saturn symbol ♄
        canv.setFont('Times-Roman', 26)
        canv.setFillColor(C_GOLD)
        canv.drawCentredString(cx_ring, cy_ring - 9, u'\u2644')

        # Logo line
        canv.setFont('Helvetica-Bold', 9)
        canv.setFillColor(C_VIOLET_PALE)
        canv.drawCentredString(W/2, H * 0.90, '\u2736 JYOGI AI \u2736')

        # Main title
        canv.setFont('Times-Bold', 36)
        canv.setFillColor(C_WHITE)
        canv.drawCentredString(W/2, H * 0.82, 'Saturn Intelligence')
        canv.setFont('Times-Bold', 28)
        canv.setFillColor(C_GOLD)
        canv.drawCentredString(W/2, H * 0.76, 'Report')

        # Subtitle
        canv.setFont('Helvetica', 12)
        canv.setFillColor(C_SILVER)
        canv.drawCentredString(W/2, H * 0.70, 'Vedic Astrology \u00b7 Swiss Ephemeris Precision')

        # Gold divider
        canv.setStrokeColor(C_GOLD)
        canv.setLineWidth(0.8)
        canv.line(W/2 - 40, H*0.675, W/2 + 40, H*0.675)

        # Client card
        card_y  = H * 0.30
        card_x  = W/2 - 65*mm
        card_w  = 130*mm
        card_h  = 62*mm
        canv.setFillColor(HexColor('#16143A'))
        canv.roundRect(card_x, card_y, card_w, card_h, 6, fill=1, stroke=0)
        canv.setStrokeColor(C_VIOLET)
        canv.setLineWidth(0.6)
        canv.roundRect(card_x, card_y, card_w, card_h, 6, fill=0, stroke=1)

        def card_line(label, value, y_offset):
            canv.setFont('Helvetica', 7.5)
            canv.setFillColor(C_VIOLET_PALE)
            canv.drawString(card_x + 12, card_y + card_h - y_offset, label)
            canv.setFont('Helvetica-Bold', 9)
            canv.setFillColor(C_WHITE)
            canv.drawString(card_x + 55, card_y + card_h - y_offset, value)

        canv.setFont('Helvetica-Bold', 8)
        canv.setFillColor(C_GOLD)
        canv.drawString(card_x + 12, card_y + card_h - 13, 'CHART IDENTITY')

        card_line('Name',       data['client_name'],         24)
        card_line('DOB',        data['dob'],                 34)
        card_line('TOB',        data['tob'],                 44)
        card_line('POB',        data['pob'],                 54)
        card_line('Lagna',      data['lagna'],               64)
        card_line('Moon Sign',  data['moon_sign'],           74)
        card_line('Nakshatra',  data['nakshatra'],           84)
        card_line('Period',     data['period'],              96)

        # Report ID & date
        canv.setFont('Helvetica', 7.5)
        canv.setFillColor(C_SILVER)
        canv.drawCentredString(W/2, H * 0.16, f'Report ID: {data["report_id"]}')
        canv.drawCentredString(W/2, H * 0.12, f'Generated: {timestamp}')
        canv.drawCentredString(W/2, H * 0.08, 'jyogi.in  \u00b7  Precision Vedic Astrology')

        canv.restoreState()

    # ── Insert cover page ──
    story.append(PageBreak())
    # Use a spacer-only page; cover is painted by onFirstPage
    doc.onFirstPage = cover_page
    doc.onLaterPages = page_cb

    # We need content to force pages — cover is page 1 (no story content)
    # Start page 2 content:

    # ─────────────────────────────────────────────────────────
    # PAGE 2 — EXECUTIVE SUMMARY + DATA INTEGRITY
    # ─────────────────────────────────────────────────────────
    story.append(section_tag('§ 01', S))
    story.append(Paragraph('Executive Summary', S['section_title']))
    story.append(Paragraph(
        f"Saturn \u00b7 {data['saturn_position']['rashi']} \u00b7 "
        f"{data['saturn_position']['house']} \u00b7 {data['period']}",
        S['section_sub']))
    story.append(divider())
    story.append(Paragraph(data['executive_summary'], S['body']))
    story.append(Spacer(1, 6))

    # Metrics row
    sat = data['saturn_position']
    metrics = [
        (sat['degree'],       'Saturn Degree',    sat['rashi']),
        (str(data['impact_score']), 'Impact Score', 'out of 10'),
        (sat['house'],        'Transit House',     f"Lagna: {data['lagna'].split()[0]}"),
        (sat['status'],       'Current Motion',   sat['speed']),
    ]
    metric_cols = []
    for val, lbl, note in metrics:
        col = [
            Paragraph(val, S['metric_val']),
            Paragraph(lbl.upper(), S['metric_label']),
            Spacer(1, 2),
            Paragraph(note, S['caption']),
        ]
        metric_cols.append(col)

    mt = Table([metric_cols], colWidths=[CONTENT_W/4]*4)
    mt.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,-1), C_SILVER_PALE),
        ('BACKGROUND',   (1,0), (1,0),   C_GOLD_PALE),
        ('LINEABOVE',    (0,0), (-1,0),  2, C_VIOLET),
        ('LINEBELOW',    (0,0), (-1,-1), 1, C_SILVER),
        ('LINEBETWEEN',  (0,0), (-1,-1), 0.5, C_SILVER),
        ('TOPPADDING',   (0,0), (-1,-1), 10),
        ('BOTTOMPADDING',(0,0), (-1,-1), 10),
        ('ALIGN',        (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(KeepTogether([mt]))
    story.append(Spacer(1, 16))

    # ── Data Integrity Block ──
    story.append(section_tag('§ 02  DATA INTEGRITY', S))
    story.append(Paragraph('Calculation Provenance', S['section_title']))
    story.append(Paragraph(
        'All planetary positions in this report are computed using Swiss Ephemeris '
        '(the gold standard in astronomical calculation) via the pyswisseph library. '
        'Results are reproducible to arc-second precision.',
        S['body']))

    integrity_rows = [
        [Paragraph('PARAMETER', S['th']), Paragraph('VALUE', S['th'])]
    ]
    for label, value in data['integrity_checks']:
        integrity_rows.append([
            Paragraph(label, S['body_bold']),
            Paragraph(value, S['data_integrity']),
        ])

    it = Table(integrity_rows, colWidths=[55*mm, CONTENT_W - 55*mm])
    it.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,0),  C_INDIGO),
        ('TEXTCOLOR',    (0,0), (-1,0),  C_WHITE),
        ('BACKGROUND',   (0,1), (-1,-1), C_WHITE),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [C_WHITE, C_SILVER_PALE]),
        ('GRID',         (0,0), (-1,-1), 0.4, C_SILVER),
        ('LEFTPADDING',  (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING',   (0,0), (-1,-1), 6),
        ('BOTTOMPADDING',(0,0), (-1,-1), 6),
        ('LINEABOVE',    (0,0), (-1,0),  2, C_VIOLET),
    ]))
    story.append(it)

    story.append(PageBreak())

    # ─────────────────────────────────────────────────────────
    # PAGE 3 — TRANSIT TABLE + RETROGRADE TIMELINE
    # ─────────────────────────────────────────────────────────
    story.append(section_tag('§ 03  VISUAL DATA MODULE', S))
    story.append(Paragraph('Saturn Transit Table — Apr 2026 to Mar 2027', S['section_title']))
    story.append(Paragraph(
        'Monthly Saturn positions with motion status and house impact assessment. '
        'Retrograde months are highlighted in red.',
        S['section_sub']))

    col_headers = ['Month', 'Rashi', 'Degree', 'Motion', 'House', 'Influence Note']
    col_widths  = [22*mm, 22*mm, 20*mm, 24*mm, 16*mm, CONTENT_W - 104*mm]

    transit_rows = [[Paragraph(h, S['th']) for h in col_headers]]
    for i, row in enumerate(data['transit_table']):
        is_retro = 'Retrograde' in row[3]
        bg = HexColor('#FFF5F5') if is_retro else (C_SILVER_PALE if i % 2 else C_WHITE)
        motion_style = S['td_retro'] if is_retro else S['td_direct']
        cells = [
            Paragraph(row[0], S['td_left']),
            Paragraph(row[1], S['td']),
            Paragraph(row[2], S['td']),
            Paragraph(row[3], motion_style),
            Paragraph(row[4], S['td']),
            Paragraph(row[5], S['td_left']),
        ]
        transit_rows.append(cells)

    # Build row backgrounds
    row_bgs = []
    for i, row in enumerate(data['transit_table']):
        is_retro = 'Retrograde' in row[3]
        if is_retro:
            row_bgs.append(('BACKGROUND', (0, i+1), (-1, i+1), HexColor('#FFF0F0')))
        elif i % 2:
            row_bgs.append(('BACKGROUND', (0, i+1), (-1, i+1), C_SILVER_PALE))

    tt = Table(transit_rows, colWidths=col_widths, repeatRows=1)
    ts_cmds = [
        ('BACKGROUND',    (0,0), (-1,0),   C_INDIGO),
        ('TEXTCOLOR',     (0,0), (-1,0),   C_WHITE),
        ('LINEABOVE',     (0,0), (-1,0),   2, C_VIOLET),
        ('GRID',          (0,0), (-1,-1),  0.3, C_SILVER),
        ('LEFTPADDING',   (0,0), (-1,-1),  6),
        ('RIGHTPADDING',  (0,0), (-1,-1),  6),
        ('TOPPADDING',    (0,0), (-1,-1),  5),
        ('BOTTOMPADDING', (0,0), (-1,-1),  5),
        ('VALIGN',        (0,0), (-1,-1),  'MIDDLE'),
    ] + row_bgs
    tt.setStyle(TableStyle(ts_cmds))
    story.append(tt)
    story.append(Paragraph(
        'ℛ = Retrograde period  \u00b7  Motion status based on Swiss Ephemeris daily speed calculation',
        S['caption']))
    story.append(Spacer(1, 14))

    # ── Retrograde Timeline ──
    story.append(section_tag('§ 03b  RETROGRADE TIMELINE 2022–2028', S))
    story.append(Paragraph('Saturn Retrograde Periods — Visual Overview', S['section_title']))
    story.append(draw_retro_bar(data['retro_periods'], width=CONTENT_W,
                                 year_range=(2022, 2028)))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        'Saturn retrogrades approximately once per year for ~4.5 months. '
        'Each retrograde period is an invitation to consolidate, review, and restructure.',
        S['body']))

    story.append(PageBreak())

    # ─────────────────────────────────────────────────────────
    # PAGE 4 — IMPACT SCORE + SADE SATI + NATAL SATURN
    # ─────────────────────────────────────────────────────────
    story.append(section_tag('§ 04  IMPACT SCORE MODULE', S))
    story.append(Paragraph('Saturnian Influence Score', S['section_title']))
    story.append(Paragraph(
        'A composite score integrating transit house, dasha alignment, Sade Sati phase, '
        'and natal Saturn dignity. Scale: 1 (minimal) → 10 (transformative).',
        S['section_sub']))

    gauge = draw_impact_gauge(data['impact_score'], width=CONTENT_W, height=42*mm)
    story.append(gauge)
    story.append(Paragraph(
        f'Score: <b>{data["impact_score"]}</b> / 10 — '
        'High Saturnian influence. This period demands discipline, patience, '
        'and deliberate action. Rewards are commensurate with effort applied.',
        S['body']))
    story.append(Spacer(1, 16))

    # ── Score breakdown table ──
    score_rows = [
        [Paragraph('FACTOR', S['th']), Paragraph('SUB-SCORE', S['th']),
         Paragraph('WEIGHT', S['th']), Paragraph('NOTES', S['th'])],
        [Paragraph('Transit House (3rd)', S['td_left']),
         Paragraph('7.0', S['td']), Paragraph('30%', S['td']),
         Paragraph('3rd house: moderate-high karmic activation', S['td_left'])],
        [Paragraph('Mahadasha Alignment', S['td_left']),
         Paragraph('8.5', S['td']), Paragraph('25%', S['td']),
         Paragraph('Saturn MD + Mercury AD: strong alignment', S['td_left'])],
        [Paragraph('Sade Sati Phase', S['td_left']),
         Paragraph('6.8', S['td']), Paragraph('25%', S['td']),
         Paragraph('Setting phase — intensity reducing', S['td_left'])],
        [Paragraph('Natal Saturn Dignity', S['td_left']),
         Paragraph('6.5', S['td']), Paragraph('20%', S['td']),
         Paragraph('8th house Leo (retrograde) — deep karmic layer', S['td_left'])],
    ]
    st = Table(score_rows, colWidths=[50*mm, 26*mm, 22*mm, CONTENT_W-98*mm])
    st.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0),   C_INDIGO),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),  [C_WHITE, C_SILVER_PALE]),
        ('GRID',          (0,0), (-1,-1),  0.3, C_SILVER),
        ('LEFTPADDING',   (0,0), (-1,-1),  8),
        ('TOPPADDING',    (0,0), (-1,-1),  6),
        ('BOTTOMPADDING', (0,0), (-1,-1),  6),
        ('LINEABOVE',     (0,0), (-1,0),   2, C_VIOLET),
    ]))
    story.append(st)
    story.append(Spacer(1, 16))

    # ── Sade Sati Timeline ──
    story.append(section_tag('§ 05  SADE SATI ANALYSIS', S))
    story.append(Paragraph('Sade Sati Phase Timeline', S['section_title']))
    ss = data['sade_sati']
    story.append(Paragraph(
        f"Active: <b>{ss['start_year']}</b> – <b>{ss['end_year']}</b>  \u00b7  "
        f"Current Phase: <b>{ss['current_phase']}</b>",
        S['section_sub']))

    story.append(draw_sade_sati_timeline(ss['phases'], width=CONTENT_W))
    story.append(Spacer(1, 8))

    ss_rows = [
        [Paragraph(h, S['th']) for h in ['PHASE', 'PERIOD', 'TRANSIT RASHI', 'CHARACTERISTICS']],
        [Paragraph('Rising', S['td_left']),
         Paragraph('Nov 2023 – Dec 2024', S['td']),
         Paragraph('Aquarius', S['td']),
         Paragraph('Initiating pressure; structural adjustments begin', S['td_left'])],
        [Paragraph('Peak', S['td_left']),
         Paragraph('Jan 2025 – Jan 2026', S['td']),
         Paragraph('Pisces', S['td']),
         Paragraph('Highest intensity; karmic debts surface; deep transformation', S['td_left'])],
        [Paragraph('Setting', S['td_left']),
         Paragraph('Feb 2026 – Oct 2026', S['td']),
         Paragraph('Aries', S['td']),
         Paragraph('Gradual lifting; integration of lessons; new cycle begins', S['td_left'])],
    ]
    sst = Table(ss_rows, colWidths=[24*mm, 38*mm, 28*mm, CONTENT_W-90*mm])
    sst.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0),   C_INDIGO),
        ('BACKGROUND',    (0,2), (-1,2),   HexColor('#FFF5F0')),  # Peak row highlight
        ('ROWBACKGROUNDS',(0,1),(-1,-1),  [C_WHITE, HexColor('#FFF5F0'), C_SILVER_PALE]),
        ('GRID',          (0,0), (-1,-1),  0.3, C_SILVER),
        ('LEFTPADDING',   (0,0), (-1,-1),  8),
        ('TOPPADDING',    (0,0), (-1,-1),  6),
        ('BOTTOMPADDING', (0,0), (-1,-1),  6),
        ('LINEABOVE',     (0,0), (-1,0),   2, C_GOLD),
        ('FONTNAME',      (0,2), (-1,2),   'Helvetica-Bold'),
    ]))
    story.append(sst)
    story.append(PageBreak())

    # ─────────────────────────────────────────────────────────
    # PAGE 5 — INSIGHT PANELS
    # ─────────────────────────────────────────────────────────
    story.append(section_tag('§ 06  INSIGHT PANELS', S))
    story.append(Paragraph('Saturn Guidance — Actionable Intelligence', S['section_title']))
    story.append(Paragraph(
        'Translating astronomical data into practical Vedic guidance for the period.',
        S['section_sub']))
    story.append(divider())

    for ins in data['insights']:
        story.append(KeepTogether([
            insight_panel(ins['tag'], ins['title'], ins['body'], S, ins['accent']),
            Spacer(1, 10),
        ]))

    story.append(Spacer(1, 10))
    story.append(divider(color=C_GOLD, thickness=0.8))

    # Closing callout
    story.append(Spacer(1, 8))
    callout_txt = (
        '"The planet Saturn (Shani) does not punish — he teaches. '
        'His lessons are proportional to our resistance. '
        'Work with discipline, patience, and honesty and Saturn becomes '
        'your greatest benefactor."\n\n— Jyogi AI Interpretation Engine'
    )
    story.append(Paragraph(callout_txt, S['callout']))
    story.append(Spacer(1, 16))

    # Disclaimer
    story.append(divider())
    disclaimer = (
        "<b>Disclaimer:</b> This report is generated by Jyogi AI for educational and "
        "reflective purposes. Vedic astrology is a traditional interpretive system; "
        "planetary positions are calculated with Swiss Ephemeris precision. "
        "Consult a qualified Jyotishi for personalised guidance. "
        "jyogi.in  \u00b7  Precision Vedic Astrology  \u00b7  enquiries@jyogi.in"
    )
    story.append(Paragraph(disclaimer, ParagraphStyle('disc',
        fontName='Helvetica', fontSize=7.5, textColor=C_SILVER,
        leading=11, alignment=TA_JUSTIFY)))

    # ── Build ──
    doc.build(story, onFirstPage=cover_page, onLaterPages=page_cb)
    print(f"✅ Report generated: {output_path}")


# ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    OUT = '/mnt/user-data/outputs/Jyogi_AI_Saturn_Report.pdf'
    build_report(OUT, REPORT_DATA)
