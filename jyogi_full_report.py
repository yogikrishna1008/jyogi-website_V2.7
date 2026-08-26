"""
Jyogi AI — Premium Full Kundali Report
=======================================
9-page professional Vedic report with:
  P1  Cover — Identity Header + Panchanga
  P2  Birth Chart D1 + Navamsha D9 (side by side)
  P3  Graha Spashta Table + dignity colour coding
  P4  Ashtakavarga Matrix (8×12 grid)
  P5  Shadbala & Bhava Bala strength gauges
  P6  Saturn Precision Module — Sade Sati Gantt + Sodhya Pinda
  P7  Vimshottari Dasha Chronology (3 levels)
  P8  AI Insights — Psychology / Career / Saturn's Discipline
  P9  Closing + Disclaimer
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units   import mm, cm
from reportlab.lib.colors  import HexColor, white, black
from reportlab.lib.enums   import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.styles  import ParagraphStyle
from reportlab.platypus    import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether, FrameBreak
)
from reportlab.graphics.shapes import (
    Drawing, Rect, Line, Circle, Polygon, String,
    Group, Path
)
from reportlab.graphics import renderPDF
import datetime, math

# ── Page geometry ─────────────────────────────────────────────
W, H      = A4                    # 595 × 842
ML = MR   = 18*mm
MT        = 20*mm
MB        = 18*mm
CW        = W - ML - MR          # 559 pt content width

# ── Cosmic Professional Palette ──────────────────────────────
NAVY      = HexColor('#0D1B2A')   # Deep navy — primary dark
NAVY2     = HexColor('#162032')   # Slightly lighter navy
NAVY3     = HexColor('#1E2D40')   # Card background
SLATE     = HexColor('#4A5568')   # Slate gray — body text
SLATE2    = HexColor('#718096')   # Secondary text
SILVER    = HexColor('#CBD5E0')   # Borders, dividers
SILVER2   = HexColor('#EDF2F7')   # Zebra / row bg
GOLD      = HexColor('#C9A84C')   # Primary accent
GOLD2     = HexColor('#E8C96E')   # Lighter gold
GOLD_BG   = HexColor('#FBF6E9')   # Gold tint bg
WHITE     = HexColor('#FFFFFF')
CREAM     = HexColor('#FAFAF7')   # Off-white pages
VIOLET    = HexColor('#6B5EA8')   # Accent violet
TEAL      = HexColor('#2B8A7A')   # Exalted — green teal
RED_SOFT  = HexColor('#C0514A')   # Debilitated — soft red
ORANGE    = HexColor('#D97706')   # Retrograde
INDIGO    = HexColor('#3730A3')   # Muted indigo

# Dignity colours
DIG_EXALT  = HexColor('#1A7A5E')
DIG_OWN    = HexColor('#2563EB')
DIG_FRIEND = HexColor('#059669')
DIG_NEUTRAL= SLATE
DIG_ENEMY  = HexColor('#D97706')
DIG_DEBIL  = HexColor('#DC2626')

# ── Typography ────────────────────────────────────────────────
def S(name, **kw):
    defaults = dict(fontName='Helvetica', fontSize=10,
                    textColor=SLATE, leading=14, spaceAfter=4)
    defaults.update(kw)
    return ParagraphStyle(name, **defaults)

STYLES = {
    # Headings (Times = closest serif in ReportLab builtins)
    'h_cover'  : S('h_cover',  fontName='Times-Bold',   fontSize=38, textColor=WHITE,
                   leading=46, alignment=TA_CENTER),
    'h_cover2' : S('h_cover2', fontName='Times-Bold',   fontSize=20, textColor=GOLD,
                   leading=26, alignment=TA_CENTER),
    'h1'       : S('h1',       fontName='Times-Bold',   fontSize=18, textColor=NAVY,
                   leading=24, spaceBefore=4, spaceAfter=3),
    'h2'       : S('h2',       fontName='Times-Bold',   fontSize=13, textColor=NAVY,
                   leading=18, spaceBefore=2, spaceAfter=2),
    'h3'       : S('h3',       fontName='Times-BoldItalic', fontSize=10.5, textColor=VIOLET,
                   leading=15, spaceAfter=2),
    'tag'      : S('tag',      fontName='Helvetica-Bold', fontSize=7, textColor=GOLD,
                   letterSpacing=3, spaceAfter=2),
    # Body
    'body'     : S('body',     fontName='Helvetica', fontSize=9.5, textColor=SLATE,
                   leading=14.5, alignment=TA_JUSTIFY, spaceAfter=6),
    'body_sm'  : S('body_sm',  fontName='Helvetica', fontSize=8.5, textColor=SLATE,
                   leading=13, spaceAfter=4),
    'mono'     : S('mono',     fontName='Courier',   fontSize=8.5, textColor=NAVY,
                   leading=13),
    'mono_sm'  : S('mono_sm',  fontName='Courier',   fontSize=7.5, textColor=SLATE,
                   leading=12),
    # Table cells
    'th'       : S('th',       fontName='Helvetica-Bold', fontSize=7.5, textColor=WHITE,
                   alignment=TA_CENTER),
    'th_l'     : S('th_l',     fontName='Helvetica-Bold', fontSize=7.5, textColor=WHITE,
                   alignment=TA_LEFT),
    'td'       : S('td',       fontName='Courier',   fontSize=8.5, textColor=NAVY,
                   alignment=TA_CENTER, leading=12),
    'td_l'     : S('td_l',     fontName='Courier',   fontSize=8.5, textColor=NAVY,
                   alignment=TA_LEFT, leading=12),
    'td_ex'    : S('td_ex',    fontName='Courier-Bold', fontSize=8.5, textColor=DIG_EXALT,
                   alignment=TA_CENTER),
    'td_own'   : S('td_own',   fontName='Courier-Bold', fontSize=8.5, textColor=DIG_OWN,
                   alignment=TA_CENTER),
    'td_deb'   : S('td_deb',   fontName='Courier-Bold', fontSize=8.5, textColor=DIG_DEBIL,
                   alignment=TA_CENTER),
    'td_ret'   : S('td_ret',   fontName='Courier-Bold', fontSize=8.5, textColor=ORANGE,
                   alignment=TA_CENTER),
    'td_num'   : S('td_num',   fontName='Courier-Bold', fontSize=9, textColor=NAVY,
                   alignment=TA_CENTER),
    'td_num_hi': S('td_num_hi',fontName='Courier-Bold', fontSize=9, textColor=DIG_EXALT,
                   alignment=TA_CENTER),
    'td_num_lo': S('td_num_lo',fontName='Courier-Bold', fontSize=9, textColor=DIG_DEBIL,
                   alignment=TA_CENTER),
    # Panchanga
    'panch_l'  : S('panch_l',  fontName='Helvetica-Bold', fontSize=7, textColor=SLATE2,
                   letterSpacing=1.5, alignment=TA_LEFT),
    'panch_v'  : S('panch_v',  fontName='Times-Bold', fontSize=10, textColor=NAVY,
                   alignment=TA_LEFT, leading=14),
    # Insight
    'ins_tag'  : S('ins_tag',  fontName='Helvetica-Bold', fontSize=7, textColor=GOLD,
                   letterSpacing=2.5, spaceAfter=2),
    'ins_h'    : S('ins_h',    fontName='Times-Bold', fontSize=13.5, textColor=NAVY,
                   leading=18, spaceAfter=4),
    'ins_body' : S('ins_body', fontName='Helvetica', fontSize=9.5, textColor=SLATE,
                   leading=15, alignment=TA_JUSTIFY, spaceAfter=6),
    'sidebar_h': S('sidebar_h',fontName='Helvetica-Bold', fontSize=7.5, textColor=GOLD,
                   letterSpacing=2, spaceAfter=3),
    'sidebar_b': S('sidebar_b',fontName='Helvetica', fontSize=8.5, textColor=NAVY2,
                   leading=13, spaceAfter=4),
    # KPI
    'kpi_val'  : S('kpi_val',  fontName='Times-Bold', fontSize=20, textColor=GOLD,
                   alignment=TA_CENTER, leading=25),
    'kpi_label': S('kpi_label',fontName='Helvetica', fontSize=7, textColor=SLATE2,
                   alignment=TA_CENTER, letterSpacing=1.5),
    'caption'  : S('caption',  fontName='Helvetica', fontSize=7.5, textColor=SLATE2,
                   alignment=TA_CENTER, leading=11),
    'foot'     : S('foot',     fontName='Helvetica', fontSize=7, textColor=SLATE2),
    'dasha_md' : S('dasha_md', fontName='Times-Bold', fontSize=10, textColor=NAVY,
                   leading=14),
    'dasha_ad' : S('dasha_ad', fontName='Courier',   fontSize=8.5, textColor=SLATE,
                   leading=13),
    'dasha_pad': S('dasha_pad',fontName='Courier',   fontSize=7.5, textColor=SLATE2,
                   leading=12),
}


# ═══════════════════════════════════════════════════════════════
# SAMPLE DATA  (plug your vedic_engine output here)
# ═══════════════════════════════════════════════════════════════
D = {
    "name"       : "Jyotirmoy Giri",
    "dob"        : "19 March 1980",
    "tob"        : "03:01 AM  IST  (UT −02:29)",
    "pob"        : "Jajpur, Odisha  (20.85°N 86.33°E)",
    "lagna"      : "Makara (Capricorn)",
    "lagna_deg"  : "12°16'",
    "moon"       : "Mesha (Aries)",
    "moon_deg"   : "04°45'",
    "sun"        : "Meena (Pisces)",
    "nakshatra"  : "Ashwini",
    "pada"       : "2",
    "mahadasha"  : "Shani (Saturn)",
    "antardasha" : "Budha (Mercury)",
    "report_id"  : "JYG-D1-19800319-002",
    # Panchanga
    "samvat"     : "Vikrama Samvat 2037",
    "masa"       : "Phalguna",
    "paksha"     : "Krishna Paksha",
    "tithi"      : "Navami (9th)",
    "vara"       : "Budhavara (Wednesday)",
    "yoga"       : "Siddha",
    "karana"     : "Kaulava",
    "ishtkaal"   : "06:14:32",
    "sunrise"    : "06:14 AM",
    "sunset"     : "06:22 PM",
    # Graha Spashta
    "planets": [
        # name, abbr, lon_str, deg_raw, rashi, naksh, pada, speed, dignity, retro
        ("Sun",     "Su", "Pisces 04°56'",  334.93, "Meena",  "Uttarabhadra", "1", "+0.994", "Neutral", False),
        ("Moon",    "Mo", "Aries  04°45'",    4.75, "Mesha",  "Ashwini",      "2", "+14.96", "Exalted", False),
        ("Mars",    "Ma", "Leo    04°18'R", 124.30, "Simha",  "Magha",        "1", "-0.237", "Neutral", True),
        ("Mercury", "Me", "Aquar. 14°00'R", 314.00, "Kumbha", "Shatabhisha",  "2", "-0.069", "Own",     True),
        ("Jupiter", "Ju", "Leo    08°50'R", 128.83, "Simha",  "Magha",        "2", "-0.107", "Neutral", True),
        ("Venus",   "Ve", "Aries  19°47'",   19.78, "Mesha",  "Bharani",      "4", "+1.083", "Debil.",  False),
        ("Saturn",  "Sa", "Leo    29°41'R", 149.68, "Simha",  "U.Phalguni",   "1", "-0.079", "Neutral", True),
        ("Rahu",    "Ra", "Leo    05°26'R", 125.43, "Simha",  "Magha",        "1", "-0.053", "—",       True),
        ("Ketu",    "Ke", "Aquar. 05°26'R", 305.43, "Kumbha", "Shatabhisha",  "1", "-0.053", "—",       True),
        ("Lagna",   "As", "Capric.12°16'",  282.27, "Makara", "Shravana",     "3", "—",      "—",       False),
    ],
    # Ashtakavarga (rows=planets+total, cols=signs Ar..Pi)
    "ashtak": {
        "labels": ["Su","Mo","Ma","Me","Ju","Ve","Sa","TOTAL"],
        "grid": [
            [3,4,5,3,4,5,3,4,5,4,3,4],
            [5,3,4,5,3,4,5,4,3,5,4,3],
            [4,5,3,4,5,4,3,5,4,3,4,5],
            [3,4,5,4,3,5,4,3,5,4,5,3],
            [5,4,3,5,4,3,4,5,3,4,5,4],
            [4,3,5,4,5,3,5,4,3,5,3,4],
            [2,4,3,5,4,3,5,4,2,4,3,5],
            [26,27,28,30,28,27,29,29,25,29,27,28],
        ]
    },
    # Shadbala (planet, strength 0-100)
    "shadbala": [
        ("Sun",     72), ("Moon",    88), ("Mars",    61),
        ("Mercury", 79), ("Jupiter", 65), ("Venus",   44),
        ("Saturn",  58),
    ],
    # Bhava Bala (house, strength 0-100)
    "bhavabala": [
        ("I",   82), ("II",  54), ("III", 61), ("IV",  48),
        ("V",   70), ("VI",  65), ("VII", 55), ("VIII",78),
        ("IX",  60), ("X",   85), ("XI",  72), ("XII", 42),
    ],
    # Saturn module
    "saturn_natal": {"rashi":"Leo","deg":"29°41'","house":"8th","status":"Retrograde",
                     "nk":"U.Phalguni","speed":"-0.079"},
    "saturn_transit": {"rashi":"Pisces","deg":"20°14'","house":"3rd","status":"Direct",
                       "nk":"Purvabhadra","speed":"+0.083"},
    "sadesati_active": True,
    "sadesati_phase" : "Setting Phase",
    "sadesati_start" : "Nov 2023",
    "sadesati_end"   : "Oct 2026",
    "sodhya_pinda"   : 39,
    "ashtak_saturn"  : 2,   # Saturn's own ashtakavarga score in natal house
    # Sade Sati Gantt rows
    "gantt": [
        ("Sade Sati Rising",  "Nov 2023", "Dec 2024", 0.00, 0.40, TEAL),
        ("Sade Sati Peak",    "Jan 2025", "Jan 2026", 0.40, 0.72, RED_SOFT),
        ("Sade Sati Setting", "Feb 2026", "Oct 2026", 0.72, 1.00, GOLD),
        ("Dhayya (3rd)",      "Jan 2023", "Mar 2025", 0.00, 0.55, VIOLET),
    ],
    # Dasha table (md, ad, pad, start, end)
    "dashas": [
        ("Shani (Saturn)", [
            ("Budha (Mercury)", [
                ("Budha",   "Apr 2024", "Aug 2024"),
                ("Ketu",    "Aug 2024", "Sep 2024"),
                ("Shukra",  "Sep 2024", "Nov 2024"),
                ("Surya",   "Nov 2024", "Dec 2024"),
                ("Chandra", "Dec 2024", "Feb 2025"),
            ], "Apr 2024", "Oct 2025"),
            ("Ketu", [], "Oct 2025", "Nov 2026"),
            ("Shukra (Venus)", [], "Nov 2026", "Jan 2030"),
        ], "Dec 2003", "Dec 2022"),
        ("Budha (Mercury)", [
            ("Budha",   [], "Dec 2022", "Jun 2025"),
            ("Ketu",    [], "Jun 2025", "Jun 2026"),
            ("Shukra",  [], "Jun 2026", "Aug 2028"),
        ], "Dec 2022", "Dec 2039"),
    ],
    # AI Insights
    "insights": {
        "psychology": {
            "title": "The Inner Architecture — Psychology & Self",
            "body": (
                "With Makara (Capricorn) rising and a retrograde Saturn in the 8th house of "
                "transformation, your inner life is sculpted by depth, persistence, and an "
                "acute awareness of impermanence. The Moon in Ashwini nakshatra gifts an "
                "instinctive drive — you process emotion through action rather than reflection. "
                "The stellium of retrograde planets in Leo (Mars, Jupiter, Saturn, Rahu) in "
                "the 8th house marks a psyche that works intensely with inherited patterns, "
                "unresolved ancestral karma, and the shadow-work of institutions. "
                "Solitude is not isolation for you — it is where integration occurs."
            ),
            "takeaways": ["Depth over breadth", "Shadow work is your accelerator",
                          "Ashwini: heal yourself to serve others"],
        },
        "career": {
            "title": "Karmic Path — Career, Wealth & Legacy",
            "body": (
                "Mercury Mahadasha (Dec 2022 – Dec 2039) places your primary karmic focus on "
                "communication, technology, and intellectual leadership. The 10th house "
                "(Libra, ruled by Venus) strongly favours consulting, advisory, and "
                "knowledge-economy work. Saturn Mahadasha's legacy — 19 years of structural "
                "discipline — has built a foundation that Mercury now refines into articulate "
                "expression. The period 2026–2029 (Mercury-Venus dasha) is the most "
                "financially potent window of the next decade. Prioritise: AI, astrology "
                "SaaS, and premium knowledge products."
            ),
            "takeaways": ["2026–29: peak financial window", "Consulting > employment",
                          "Technology + spirituality = niche monopoly"],
        },
        "saturn": {
            "title": "Saturn's Discipline — Current Challenges (2025–26)",
            "body": (
                "Transit Saturn in Pisces (3rd house) overlaps with the closing of Sade Sati "
                "(Setting Phase, Feb–Oct 2026). This dual Saturnian pressure is the final "
                "examination of a 7.5-year cycle: Saturn tests whether the lessons of "
                "contraction were genuinely absorbed. The retrograde window (Jul–Oct 2026) "
                "is a structured internal audit — avoid launches, double-check all "
                "commitments. Post-October 2026 marks a decisive shift: Sade Sati "
                "concludes, Saturn enters Aries, and a new 30-year cycle of lighter "
                "Saturnian energy begins. The harvest of this decade of discipline arrives "
                "in 2027–2028."
            ),
            "takeaways": ["Jul–Oct 2026: no major launches", "Sade Sati ends Oct 2026",
                          "2027 begins the harvest phase"],
        },
    },
}


# ═══════════════════════════════════════════════════════════════
# PAGE TEMPLATE CALLBACKS
# ═══════════════════════════════════════════════════════════════
TS = datetime.datetime.now().strftime("%d %b %Y  %H:%M")

def header_footer(canv, doc):
    canv.saveState()
    pg = doc.page
    if pg > 1:
        # Top rule
        canv.setFillColor(NAVY)
        canv.rect(0, H - 13*mm, W, 13*mm, fill=1, stroke=0)
        canv.setFont('Helvetica-Bold', 8); canv.setFillColor(GOLD)
        canv.drawString(ML, H - 8.5*mm, '\u2736 JYOGI AI')
        canv.setFont('Helvetica', 8); canv.setFillColor(SILVER)
        canv.drawCentredString(W/2, H - 8.5*mm,
            f'Full Kundali Report  \u00b7  {D["name"]}')
        canv.setFont('Courier', 7.5); canv.setFillColor(GOLD)
        canv.drawRightString(W - MR, H - 8.5*mm, D["report_id"])
    # Footer rule
    canv.setFillColor(NAVY)
    canv.rect(0, 0, W, 11*mm, fill=1, stroke=0)
    canv.setFont('Helvetica', 7); canv.setFillColor(SLATE2)
    canv.drawString(ML, 3.8*mm,
        f'Generated {TS}  \u00b7  Swiss Ephemeris  \u00b7  Lahiri Ayanamsa  \u00b7  jyogi.in')
    canv.setFont('Helvetica-Bold', 8); canv.setFillColor(GOLD)
    canv.drawRightString(W - MR, 3.8*mm, f'{pg}')
    # Thin gold line above footer
    canv.setStrokeColor(GOLD); canv.setLineWidth(0.4)
    canv.line(ML, 11*mm, W - MR, 11*mm)
    canv.restoreState()


def cover_bg(canv, doc):
    header_footer(canv, doc)
    canv.saveState()
    # Full navy background
    canv.setFillColor(NAVY); canv.rect(0, 0, W, H, fill=1, stroke=0)
    # Gold top band
    canv.setFillColor(GOLD); canv.rect(0, H - 4*mm, W, 4*mm, fill=1, stroke=0)
    # Geometric star decoration
    import random; random.seed(99)
    canv.setFillColor(WHITE)
    for _ in range(120):
        sx = random.uniform(0, W); sy = random.uniform(0, H * 0.55)
        canv.circle(sx, sy, random.uniform(0.3, 1.1), fill=1, stroke=0)
    # Large decorative circle (mandala ring)
    cx, cy = W/2, H * 0.63
    for r_off, stroke_col, lw in [
        (60, GOLD,   1.2), (72, GOLD2,  0.6),
        (85, SILVER, 0.4), (98, SLATE2, 0.3),
    ]:
        canv.setStrokeColor(stroke_col); canv.setLineWidth(lw)
        canv.circle(cx, cy, r_off, fill=0, stroke=1)
    # Inner planet circle
    canv.setFillColor(NAVY2); canv.circle(cx, cy, 52, fill=1, stroke=0)
    canv.setStrokeColor(GOLD); canv.setLineWidth(1)
    canv.circle(cx, cy, 52, fill=0, stroke=1)
    # Lagna glyph
    canv.setFont('Times-Roman', 30); canv.setFillColor(GOLD)
    canv.drawCentredString(cx, cy - 10, '\u2648')   # Aries glyph as decorative
    canv.setFont('Helvetica-Bold', 8); canv.setFillColor(SILVER)
    canv.drawCentredString(cx, cy - 22, 'D1 \u00b7 KUNDALI')
    # Dotted dividers
    canv.setStrokeColor(GOLD); canv.setLineWidth(0.6)
    canv.line(W/2 - 50, H * 0.78 - 2, W/2 + 50, H * 0.78 - 2)
    canv.restoreState()


# ═══════════════════════════════════════════════════════════════
# DRAWING HELPERS
# ═══════════════════════════════════════════════════════════════
def rule(color=SILVER, thick=0.4, w=CW, before=4, after=6):
    return HRFlowable(width=w, thickness=thick, color=color,
                      spaceBefore=before, spaceAfter=after)

def tag(text): return Paragraph(text.upper(), STYLES['tag'])

def kw_table(items, col_w=None):
    """Key-value pairs in a 2-col table."""
    cw = col_w or [42*mm, CW - 42*mm]
    rows = [[Paragraph(k, STYLES['panch_l']),
             Paragraph(v, STYLES['panch_v'])] for k, v in items]
    t = Table(rows, colWidths=cw)
    t.setStyle(TableStyle([
        ('TOPPADDING',    (0,0),(-1,-1), 3),
        ('BOTTOMPADDING', (0,0),(-1,-1), 3),
        ('LEFTPADDING',   (0,0),(-1,-1), 0),
        ('VALIGN',        (0,0),(-1,-1), 'TOP'),
        ('LINEBELOW',     (0,0),(-1,-1), 0.25, SILVER),
    ]))
    return t


# ─────────────────────────────────────────────────────────────
# NORTH INDIAN CHART DRAWING
# ─────────────────────────────────────────────────────────────
def draw_ni_chart(planet_positions, lagna_idx, retro_map,
                  dignity_map, width=88*mm, title="D1 BIRTH CHART"):
    """
    North Indian Kundali -- SQUARE, correct 12-house grid.
    Lines: outer rect + 2 full corner diagonals + inner diamond = 12 houses.
    """
    S  = width          # SQUARE
    d  = Drawing(S, S + 14)
    CX, CY = S/2, S/2

    # 1. Outer square
    d.add(Rect(0, 0, S, S, fillColor=CREAM, strokeColor=NAVY, strokeWidth=1.4))

    LS = dict(strokeColor=NAVY, strokeWidth=0.9)

    # 2. Two full corner-to-corner diagonals (THE KEY MISSING LINES)
    # ReportLab: y=0 at BOTTOM, so top of square = y=S
    d.add(Line(0, S,  S, 0,  **LS))   # top-left  -> bottom-right
    d.add(Line(S, S,  0, 0,  **LS))   # top-right -> bottom-left

    # 3. Inner diamond: mid-edge to mid-edge
    d.add(Line(CX, S,   S,  CY,  **LS))   # top-mid   -> right-mid
    d.add(Line(S,  CY,  CX, 0,   **LS))   # right-mid -> bottom-mid
    d.add(Line(CX, 0,   0,  CY,  **LS))   # bottom-mid-> left-mid
    d.add(Line(0,  CY,  CX, S,   **LS))   # left-mid  -> top-mid

    # 4. Lagna highlight (H1 = top kite)
    from reportlab.graphics.shapes import Polygon
    d.add(Polygon([CX, S, CX+S/4, CY+S/4, CX, CY, CX-S/4, CY+S/4],
                  fillColor=HexColor("#FFC34012"),
                  strokeColor=GOLD, strokeWidth=1.0))

    # 5. House centroids -- normalised (x,y) in square
    # y=1.0 = TOP of square in our normalised coords (we multiply by S then use as-is)
    # But ReportLab y=0 at bottom, so fy=0.73 means 73% of S from bottom
    # ANTICLOCKWISE from top — standard North Indian Kundali direction
    hc = {
        1:  (0.500, 0.730),   # top kite      -- Lagna
        2:  (0.250, 0.870),   # top-LEFT corner      (anticlockwise)
        3:  (0.130, 0.650),   # left-top triangle
        4:  (0.270, 0.500),   # left kite
        5:  (0.130, 0.350),   # left-bottom triangle
        6:  (0.250, 0.130),   # bottom-LEFT corner
        7:  (0.500, 0.270),   # bottom kite
        8:  (0.750, 0.130),   # bottom-RIGHT corner
        9:  (0.870, 0.350),   # right-bottom triangle
        10: (0.730, 0.500),   # right kite
        11: (0.870, 0.650),   # right-top triangle
        12: (0.750, 0.870),   # top-RIGHT corner
    }

    lr = lagna_idx
    hp = {h: [] for h in range(1, 13)}
    for pname, ridx in planet_positions.items():
        hp[((ridx - lr) % 12) + 1].append(pname)

    # 6. Rashi numbers
    AC = {'Exalted':DIG_EXALT,'Own':DIG_OWN,'Debil.':DIG_DEBIL,
          'Neutral':SLATE,'Friend':DIG_FRIEND,'---':SLATE}
    for h, (fx, fy) in hc.items():
        px, py    = fx*S, fy*S
        rnum      = (lr + h - 1) % 12 + 1
        is_lagna  = (h == 1)
        d.add(String(px, py + 2, str(rnum),
                     fontName='Helvetica-Bold' if is_lagna else 'Helvetica',
                     fontSize=8 if is_lagna else 7,
                     fillColor=GOLD.hexval() if is_lagna else SLATE.hexval(),
                     textAnchor='middle'))

    # 7. Planet abbreviations + retrograde
    for h, planets in hp.items():
        if not planets: continue
        fx, fy  = hc[h]
        bpx, bpy = fx*S, fy*S - 4
        for i, pname in enumerate(planets):
            abbr = pname[:2]
            retro= retro_map.get(pname, False)
            dig  = dignity_map.get(pname, 'Neutral')
            col  = AC.get(dig, SLATE)
            lbl  = abbr + (chr(0x211B) if retro else '')
            d.add(String(bpx, bpy - 10 - i*9, lbl,
                         fontName='Courier-Bold', fontSize=7.5,
                         fillColor=col.hexval(), textAnchor='middle'))

    # 8. ASC label
    fx, fy = hc[1]
    d.add(String(fx*S, fy*S + 10, 'ASC',
                 fontName='Helvetica-Bold', fontSize=6,
                 fillColor=GOLD.hexval(), textAnchor='middle'))

    # 9. Title
    d.add(String(S/2, S + 4, title,
                 fontName='Helvetica-Bold', fontSize=8,
                 fillColor=NAVY.hexval(), textAnchor='middle'))
    return d


def strength_gauge(label, pct, width=CW, height=9, col=GOLD):
    """Horizontal bar gauge for Shadbala / Bhava Bala."""
    d = Drawing(width, height + 2)
    # Background track
    d.add(Rect(0, 1, width, height, fillColor=SILVER2, strokeColor=None))
    # Fill bar
    bar_w = width * pct / 100
    bar_col = DIG_EXALT if pct >= 75 else (GOLD if pct >= 50 else RED_SOFT)
    d.add(Rect(0, 1, bar_w, height, fillColor=bar_col, strokeColor=None))
    # Label
    d.add(String(2, 2.5, label,
                 fontName='Helvetica-Bold', fontSize=7,
                 fillColor=WHITE.hexval() if pct > 20 else SLATE.hexval()))
    # Pct text on right
    d.add(String(width - 2, 2.5, f'{pct}%',
                 fontName='Courier-Bold', fontSize=7,
                 fillColor=NAVY.hexval(), textAnchor='end'))
    return d


# ─────────────────────────────────────────────────────────────
# ASHTAKAVARGA CELL COLOUR
# ─────────────────────────────────────────────────────────────
def akv_cell_style(val, row_idx):
    """Return table paragraph style based on Ashtakavarga value."""
    if row_idx == 7:  # TOTAL row
        if val >= 30: return STYLES['td_num_hi']
        if val <= 25: return STYLES['td_num_lo']
        return STYLES['td_num']
    if val >= 5: return STYLES['td_num_hi']
    if val <= 2: return STYLES['td_num_lo']
    return STYLES['td_num']


# ─────────────────────────────────────────────────────────────
# GANTT CHART (Saturn cycles)
# ─────────────────────────────────────────────────────────────
def draw_gantt(rows, width=CW, row_h=10*mm, padding=3):
    total_h = len(rows) * (row_h + padding) + 16
    d = Drawing(width, total_h)

    label_w = 52*mm
    track_x = label_w + 4
    track_w = width - label_w - 6

    # ── Year axis ─────────────────────────────────────────────
    year_range = (2023, 2027)
    n_years = year_range[1] - year_range[0]
    for i in range(n_years + 1):
        yr = year_range[0] + i
        tx = track_x + (i / n_years) * track_w
        d.add(Line(tx, 0, tx, total_h - 14,
                   strokeColor=SILVER, strokeWidth=0.4))
        d.add(String(tx, total_h - 11, str(yr),
                     fontName='Helvetica', fontSize=6.5,
                     fillColor=SLATE2.hexval(), textAnchor='middle'))

    # ── Rows ──────────────────────────────────────────────────
    for ri, (label, start_str, end_str, frac_s, frac_e, col) in enumerate(rows):
        y = total_h - 14 - (ri + 1) * (row_h + padding)
        # Label
        d.add(String(0, y + row_h/2 - 3, label,
                     fontName='Helvetica-Bold', fontSize=7.5,
                     fillColor=NAVY.hexval()))
        # Background track
        d.add(Rect(track_x, y, track_w, row_h,
                   fillColor=SILVER2, strokeColor=None))
        # Gantt bar
        bx = track_x + frac_s * track_w
        bw = (frac_e - frac_s) * track_w
        d.add(Rect(bx, y + 1, bw, row_h - 2,
                   fillColor=col, strokeColor=None))
        # Date labels inside bar
        if bw > 40:
            d.add(String(bx + 4, y + row_h/2 - 3, start_str,
                         fontName='Helvetica', fontSize=6,
                         fillColor=WHITE.hexval()))
            d.add(String(bx + bw - 4, y + row_h/2 - 3, end_str,
                         fontName='Helvetica', fontSize=6,
                         fillColor=WHITE.hexval(), textAnchor='end'))

    # ── NOW marker ────────────────────────────────────────────
    now_frac = 0.52  # Approx Apr 2025
    nx = track_x + now_frac * track_w
    d.add(Line(nx, 0, nx, total_h - 14,
               strokeColor=GOLD, strokeWidth=1.5))
    d.add(String(nx, total_h - 10, 'NOW',
                 fontName='Helvetica-Bold', fontSize=6,
                 fillColor=GOLD.hexval(), textAnchor='middle'))
    return d


# ─────────────────────────────────────────────────────────────
# SIDEBAR PANEL
# ─────────────────────────────────────────────────────────────
def sidebar_panel(title, items, width=48*mm):
    """Key Takeaways sidebar box."""
    inner = [Paragraph(title, STYLES['sidebar_h'])]
    for it in items:
        inner.append(Paragraph(f'\u2022  {it}', STYLES['sidebar_b']))
    t = Table([[inner]], colWidths=[width - 6])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,-1), GOLD_BG),
        ('LINEBEFORE',    (0,0),(0,-1),  3, GOLD),
        ('LEFTPADDING',   (0,0),(-1,-1), 8),
        ('RIGHTPADDING',  (0,0),(-1,-1), 6),
        ('TOPPADDING',    (0,0),(-1,-1), 8),
        ('BOTTOMPADDING', (0,0),(-1,-1), 8),
    ]))
    return t


# ═══════════════════════════════════════════════════════════════
# BUILD REPORT
# ═══════════════════════════════════════════════════════════════
def build(out, data=None):
    """Generate PDF with live data. Uses local copy of D to avoid cross-request pollution."""
    # Use a LOCAL copy — never modify the module-level D template
    global D
    _D_orig = D
    if data:
        D = dict(_D_orig)   # fresh copy for this request
        D.update(data)      # overwrite with live values (no filter — all keys pass)
    doc = SimpleDocTemplate(
        out,
        leftMargin=ML, rightMargin=MR,
        topMargin=MT + 14*mm, bottomMargin=MB + 12*mm,
        title=f"Jyogi AI Full Kundali — {D['name']}",
        author='Jyogi AI', subject='Vedic Astrology Full Report',
    )
    story = []

    # ─────────────────────────────────────────────────────────
    # PAGE 1 — COVER
    # ─────────────────────────────────────────────────────────
    # Content painted by cover_bg; we just need enough spacers
    story.append(Spacer(1, 22*mm))
    story.append(Paragraph('Full Kundali Report', STYLES['h_cover']))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph('Vedic \u00b7 Jyotish \u00b7 Swiss Ephemeris', STYLES['h_cover2']))
    story.append(Spacer(1, 10*mm))

    # Client identity card (white card on dark bg)
    id_rows = [
        ['Name',      D['name']],
        ['DOB',       D['dob']],
        ['TOB',       D['tob']],
        ['POB',       D['pob']],
        ['Lagna',     f"{D['lagna']}  {D['lagna_deg']}"],
        ['Moon',      f"{D['moon']}  {D['moon_deg']}"],
        ['Nakshatra', f"{D['nakshatra']},  Pada {D['pada']}"],
        ['Mahadasha', f"{D['mahadasha']}  /  {D['antardasha']}"],
        ['Report ID', D['report_id']],
    ]
    id_tbl = Table(
        [[Paragraph(r[0], ParagraphStyle('il', fontName='Helvetica',
              fontSize=8, textColor=SLATE2, letterSpacing=1)),
          Paragraph(r[1], ParagraphStyle('iv', fontName='Times-Bold',
              fontSize=10, textColor=NAVY, leading=14))]
         for r in id_rows],
        colWidths=[38*mm, CW - 38*mm]
    )
    id_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,-1), WHITE),
        ('LINEBELOW',     (0,0),(-1,-2), 0.3, SILVER),
        ('LINEBELOW',     (0,-1),(-1,-1),1.0, GOLD),
        ('LINEABOVE',     (0,0),(-1,0), 2.0, GOLD),
        ('TOPPADDING',    (0,0),(-1,-1), 5),
        ('BOTTOMPADDING', (0,0),(-1,-1), 5),
        ('LEFTPADDING',   (0,0),(-1,-1), 10),
    ]))
    story.append(id_tbl)
    story.append(Spacer(1, 8*mm))

    # Panchanga strip
    panch = Table([[
        Paragraph('SAMVAT\n' + D['samvat'],      STYLES['caption']),
        Paragraph('TITHI\n'  + D['tithi'],       STYLES['caption']),
        Paragraph('VARA\n'   + D['vara'],         STYLES['caption']),
        Paragraph('YOGA\n'   + D['yoga'],         STYLES['caption']),
        Paragraph('KARANA\n' + D['karana'],       STYLES['caption']),
        Paragraph('MASA\n'   + D['masa'],         STYLES['caption']),
    ]], colWidths=[CW/6]*6)
    panch.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,-1), NAVY2),
        ('TEXTCOLOR',     (0,0),(-1,-1), SILVER),
        ('ALIGN',         (0,0),(-1,-1), 'CENTER'),
        ('TOPPADDING',    (0,0),(-1,-1), 7),
        ('BOTTOMPADDING', (0,0),(-1,-1), 7),
        ('LINEBETWEEN',   (0,0),(-1,-1), 0.3, SLATE),
    ]))
    story.append(panch)
    story.append(Spacer(1, 4*mm))

    # Ishtkaal row
    isk = Table([[
        Paragraph('ISHTKAAL\n'  + D['ishtkaal'],   STYLES['caption']),
        Paragraph('SUNRISE\n'   + D['sunrise'],    STYLES['caption']),
        Paragraph('SUNSET\n'    + D['sunset'],     STYLES['caption']),
        Paragraph('PAKSHA\n'    + D['paksha'],     STYLES['caption']),
    ]], colWidths=[CW/4]*4)
    isk.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,-1), NAVY3),
        ('TEXTCOLOR',     (0,0),(-1,-1), GOLD2),
        ('ALIGN',         (0,0),(-1,-1), 'CENTER'),
        ('TOPPADDING',    (0,0),(-1,-1), 6),
        ('BOTTOMPADDING', (0,0),(-1,-1), 6),
        ('LINEBETWEEN',   (0,0),(-1,-1), 0.3, SLATE),
    ]))
    story.append(isk)
    story.append(PageBreak())

    # ─────────────────────────────────────────────────────────
    # PAGE 2 — D1 + D9 CHARTS
    # ─────────────────────────────────────────────────────────
    story.append(tag('§ 02  Visual Engine — Birth Charts'))
    story.append(Paragraph('Main Birth Chart (D1) \u00b7 Navamsha (D9)', STYLES['h1']))
    story.append(rule())

    # Build planet maps from live D['planets'] data
    # D['planets'] rows: (name, abbr, lon_str, lon_float, rashi, naksh, pada, speed, dig, retro)
    _RASHIS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo',
               'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
    lagna_idx = _RASHIS.index(D['lagna']) if D['lagna'] in _RASHIS else 0
    planet_positions = {p[0]: int(p[3] / 30) % 12 for p in D['planets']}
    retro_map        = {p[0]: p[9] for p in D['planets']}
    dignity_map      = {p[0]: p[8] for p in D['planets']}

    d1 = draw_ni_chart(planet_positions, lagna_idx, retro_map, dignity_map,
                       width=87*mm, title='D1 — BIRTH CHART (RASHI)')
    # Navamsha — simplified (different lagna)
    # --- Navamsha (D9) --- compute real positions from planet longitudes
    def _d9_sign(lon):
        si = int(lon / 30) % 12
        deg_in_sign = lon % 30
        n = int(deg_in_sign / (30/9))  # 0-8
        TYPE = [0,1,2, 0,1,2, 0,1,2, 0,1,2]  # Movable=0,Fixed=1,Dual=2
        t = TYPE[si]
        if   t == 0: return (si + n * 4)  % 12   # Movable: Aries-based
        elif t == 1: return (si + n * 4 + 4) % 12 # Fixed: Capricorn-based (offset +4)
        else:        return (si + n * 4 + 8) % 12 # Dual: Libra-based (offset +8)
    NAVAMSHA_OFFSETS = {
        0:0, 1:9, 2:6, 3:3,    # Ar/Ta/Ge/Ca  -> Aries/Cap/Libra/Cancer start
    }
    # Simplified but correct formula:
    def _d9(lon):
        si      = int(lon / 30) % 12
        pos_in  = lon % 30
        pada    = int(pos_in / (30/9))
        STARTS  = [0,9,6,3, 0,9,6,3, 0,9,6,3]  # navamsha start sign for each rashi
        return (STARTS[si] + pada) % 12

    # Build d9_pos from the planet longitudes stored in planet_rows
    # planet_rows = [(pname, abbr, lon_str, lon_float, rashi, naksh, pada, speed, dig, retro)]
    d9_pos   = {}
    d9_lagna = 0
    if D.get('planets'):
        for row in D['planets']:
            pname   = row[0]
            lon_val = row[3]  # float longitude
            d9_pos[pname] = _d9(lon_val)
    # D9 lagna from lagna longitude
    # We need lagna_lon -- approximate from lagna sign and degree
    lagna_lon_approx = lagna_idx * 30 + float(D.get('lagna_deg', '0').replace('°','').replace("'",'') or 0)
    d9_lagna = _d9(lagna_lon_approx)

    d9 = draw_ni_chart(d9_pos, d9_lagna, {}, {},
                       width=87*mm, title='D9 — NAVAMSHA (SOUL CHART)')

    chart_tbl = Table([[d1, d9]], colWidths=[90*mm, 90*mm])
    chart_tbl.setStyle(TableStyle([
        ('ALIGN',       (0,0),(-1,-1), 'CENTER'),
        ('VALIGN',      (0,0),(-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0),(-1,-1), 4),
        ('RIGHTPADDING',(0,0),(-1,-1), 4),
    ]))
    story.append(chart_tbl)
    story.append(Spacer(1, 4))

    # Dignity legend
    legend_items = [
        ('Exalted (Uchcha)', DIG_EXALT),
        ('Own Sign (Swa)',   DIG_OWN),
        ('Debilitated (Neecha)', DIG_DEBIL),
        ('Retrograde ℛ',    ORANGE),
        ('Neutral',         SLATE),
    ]
    leg_cells = [[
        Paragraph(f'<font color="#{c.hexval()[2:]}">■</font>  {l}',
                  ParagraphStyle('leg', fontName='Helvetica', fontSize=7.5,
                                 textColor=SLATE, leading=12))
        for l, c in legend_items
    ]]
    legend_tbl = Table(leg_cells, colWidths=[CW/5]*5)
    legend_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0),(-1,-1), SILVER2),
        ('TOPPADDING', (0,0),(-1,-1), 5),
        ('BOTTOMPADDING',(0,0),(-1,-1), 5),
        ('ALIGN', (0,0),(-1,-1), 'CENTER'),
    ]))
    story.append(legend_tbl)
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        'ℛ = Retrograde  \u00b7  Planets placed in Whole Sign houses from Lagna  '
        '\u00b7  Sidereal Lahiri system  \u00b7  North Indian diamond format',
        STYLES['caption']))
    story.append(PageBreak())

    # ─────────────────────────────────────────────────────────
    # PAGE 3 — GRAHA SPASHTA TABLE
    # ─────────────────────────────────────────────────────────
    story.append(tag('§ 03  Technical Matrix — Graha Spashta'))
    story.append(Paragraph('Planetary Positions \u00b7 Degrees \u00b7 Nakshatras', STYLES['h1']))
    story.append(rule())

    hdrs = ['GRAHA', 'LONGITUDE', 'DEG RAW', 'RASHI', 'NAKSHATRA', 'PADA', 'SPEED °/D', 'DIGNITY', 'R']
    cws  = [22*mm, 30*mm, 20*mm, 22*mm, 30*mm, 12*mm, 22*mm, 22*mm, 10*mm]

    dig_sty = {
        'Exalted': STYLES['td_ex'],
        'Own':     STYLES['td_own'],
        'Debil.':  STYLES['td_deb'],
        'Neutral': STYLES['td'],
        'Friend':  STYLES['td'],
        '—':       STYLES['td'],
    }

    graha_rows = [[Paragraph(h, STYLES['th']) for h in hdrs]]
    for i, p in enumerate(D['planets']):
        name, abbr, lon_s, deg_r, rashi, nk, pada, speed, dignity, retro = p
        r_mark = Paragraph('ℛ', STYLES['td_ret']) if retro else Paragraph('', STYLES['td'])
        graha_rows.append([
            Paragraph(f'{abbr}  {name}',              STYLES['td_l']),
            Paragraph(lon_s,                            STYLES['mono_sm']),
            Paragraph(f'{deg_r:.3f}°',                 STYLES['mono_sm']),
            Paragraph(rashi,                            STYLES['td']),
            Paragraph(nk,                               STYLES['td']),
            Paragraph(pada,                             STYLES['td']),
            Paragraph(speed,                            STYLES['mono_sm']),
            Paragraph(dignity,  dig_sty.get(dignity, STYLES['td'])),
            r_mark,
        ])

    gt = Table(graha_rows, colWidths=cws, repeatRows=1)
    row_bgs = [('BACKGROUND', (0,i+1),(-1,i+1),
                (SILVER2 if i%2 else WHITE)) for i in range(len(D['planets']))]
    gt.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,0),  NAVY),
        ('LINEABOVE',     (0,0),(-1,0),  2, GOLD),
        ('GRID',          (0,0),(-1,-1), 0.3, SILVER),
        ('LEFTPADDING',   (0,0),(-1,-1), 5),
        ('RIGHTPADDING',  (0,0),(-1,-1), 5),
        ('TOPPADDING',    (0,0),(-1,-1), 5),
        ('BOTTOMPADDING', (0,0),(-1,-1), 5),
        ('VALIGN',        (0,0),(-1,-1), 'MIDDLE'),
    ] + row_bgs))
    story.append(gt)
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        'Longitude calculated via Swiss Ephemeris  \u00b7  Lahiri Ayanamsa 23.590°  '
        '\u00b7  Geocentric apparent positions  \u00b7  Retro speeds are negative',
        STYLES['caption']))
    story.append(PageBreak())

    # ─────────────────────────────────────────────────────────
    # PAGE 4 — ASHTAKAVARGA MATRIX
    # ─────────────────────────────────────────────────────────
    story.append(tag('§ 04  Technical Matrix — Ashtakavarga'))
    story.append(Paragraph('Ashtakavarga Numerical Grid  (8 × 12)', STYLES['h1']))
    story.append(rule())
    story.append(Paragraph(
        'Each cell shows the number of benefic bindus (0–8) for the given planet '
        'in each rashi. Values ≥ 5 indicate strength; ≤ 2 indicate weakness. '
        'The TOTAL row is Sarvashtakavarga (sum of all 7 planets per sign).',
        STYLES['body']))

    SIGN_ABBR = ['Ar','Ta','Ge','Ca','Le','Vi','Li','Sc','Sa','Cp','Aq','Pi']
    akv_hdrs  = [''] + SIGN_ABBR + ['∑']
    akv_cws   = [14*mm] + [11.5*mm]*12 + [13*mm]

    akv_rows = [[Paragraph(h, STYLES['th']) for h in akv_hdrs]]
    for ri, (planet_lbl, row_data) in enumerate(
            zip(D['ashtak']['labels'], D['ashtak']['grid'])):
        row_sum = sum(row_data)
        cells = [Paragraph(planet_lbl, STYLES['th_l'])]
        for val in row_data:
            cells.append(Paragraph(str(val), akv_cell_style(val, ri)))
        cells.append(Paragraph(str(row_sum),
                     STYLES['td_num_hi'] if row_sum >= 42 else STYLES['td_num']))
        akv_rows.append(cells)

    akv_t = Table(akv_rows, colWidths=akv_cws, repeatRows=1)
    akv_t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,0),  NAVY),
        ('BACKGROUND',    (0,-1),(-1,-1),NAVY3),
        ('TEXTCOLOR',     (0,-1),(-1,-1),GOLD2),
        ('FONTNAME',      (0,-1),(-1,-1),'Courier-Bold'),
        ('LINEABOVE',     (0,0),(-1,0),  2, GOLD),
        ('GRID',          (0,0),(-1,-1), 0.3, SILVER),
        ('ROWBACKGROUNDS',(0,1),(-1,-2), [WHITE, SILVER2]),
        ('TOPPADDING',    (0,0),(-1,-1), 4),
        ('BOTTOMPADDING', (0,0),(-1,-1), 4),
        ('LEFTPADDING',   (0,0),(-1,-1), 3),
        ('RIGHTPADDING',  (0,0),(-1,-1), 3),
        ('ALIGN',         (0,0),(-1,-1), 'CENTER'),
    ]))
    story.append(akv_t)
    story.append(Spacer(1, 6))

    # Colour legend for Ashtakavarga
    story.append(Paragraph(
        '<font color="#1A7A5E"><b>■ ≥ 5 = Strong</b></font>  '
        '  <font color="#CBD5E0">■ 3–4 = Neutral</font>  '
        '  <font color="#DC2626"><b>■ ≤ 2 = Weak</b></font>',
        ParagraphStyle('akv_leg', fontName='Helvetica', fontSize=8,
                       textColor=SLATE, alignment=TA_CENTER)))
    story.append(PageBreak())

    # ─────────────────────────────────────────────────────────
    # PAGE 5 — SHADBALA + BHAVA BALA
    # ─────────────────────────────────────────────────────────
    story.append(tag('§ 05  Technical Matrix — Shadbala & Bhava Bala'))
    story.append(Paragraph('Planetary & House Strength Gauges', STYLES['h1']))
    story.append(rule())
    story.append(Paragraph(
        'Strength expressed as a percentage of the classical maximum score. '
        'Thresholds: Strong ≥ 75%  \u00b7  Moderate 50–74%  \u00b7  Weak < 50%',
        STYLES['body']))
    story.append(Spacer(1, 4))

    # Two-column: Shadbala left, Bhava Bala right
    def gauge_block(title, data, col_w):
        block = [Paragraph(title.upper(), STYLES['tag'])]
        for label, pct in data:
            block.append(strength_gauge(f'{label:<16}', pct, width=col_w - 10, height=10))
            block.append(Spacer(1, 3))
        return block

    sb_block  = gauge_block('Shadbala (Planetary Strength)',
                             D['shadbala'],  CW/2 - 4*mm)
    bba_block = gauge_block('Bhava Bala (House Strength)',
                             D['bhavabala'], CW/2 - 4*mm)

    gauge_tbl = Table([[sb_block, bba_block]],
                      colWidths=[CW/2, CW/2])
    gauge_tbl.setStyle(TableStyle([
        ('VALIGN',      (0,0),(-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0),(0,-1),  0),
        ('LEFTPADDING', (1,0),(1,-1),  12),
        ('RIGHTPADDING',(0,0),(-1,-1), 0),
        ('TOPPADDING',  (0,0),(-1,-1), 0),
        ('BOTTOMPADDING',(0,0),(-1,-1),0),
    ]))
    story.append(gauge_tbl)
    story.append(Spacer(1, 10))

    # Quick interpretation bullets
    story.append(rule(color=GOLD, thick=0.5))
    story.append(Paragraph(
        '<b>Reading the gauges:</b>  Moon (88%) and Sun (72%) carry the highest '
        'planetary strength in this chart. Venus (44%) is the weakest graha — '
        'consistent with debilitation in Aries.  '
        'Houses X (85%) and I (82%) dominate the Bhava Bala, confirming a '
        'chart strongly oriented toward career authority and identity expression.',
        STYLES['body']))
    story.append(PageBreak())

    # ─────────────────────────────────────────────────────────
    # PAGE 6 — SATURN PRECISION MODULE
    # ─────────────────────────────────────────────────────────
    story.append(tag('§ 06  Saturn Precision Module — Priority Analysis'))
    story.append(Paragraph('Sade Sati \u00b7 Dhayya \u00b7 Saturnian Dignity', STYLES['h1']))
    story.append(rule())

    # Two-col: Gantt left + sidebar right
    gantt = draw_gantt(D['gantt'], width=CW - 54*mm, row_h=10*mm)
    sb = sidebar_panel('KEY TAKEAWAYS', [
        'Sade Sati ends Oct 2026',
        'Setting Phase now active',
        'Saturn AV score: 2 bindus\n(below average)',
        'Sodhya Pinda: 39 pts\n(moderate)',
        'No major launches Jul–Oct 2026',
    ], width=50*mm)

    sat_tbl = Table([[gantt, sb]], colWidths=[CW - 54*mm, 50*mm])
    sat_tbl.setStyle(TableStyle([
        ('VALIGN',      (0,0),(-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0),(0,-1),  0),
        ('RIGHTPADDING',(0,0),(0,-1),  8),
        ('LEFTPADDING', (1,0),(1,-1),  0),
    ]))
    story.append(sat_tbl)
    story.append(Spacer(1, 10))

    # Saturnian Dignity technical block
    story.append(rule(color=GOLD, thick=0.5))
    story.append(tag('Saturnian Dignity Block — Mathematical Verification'))
    story.append(Spacer(1, 4))

    sat_data = [
        ('NATAL SATURN',),
        ('Rashi',              D['saturn_natal']['rashi']),
        ('Degree',             D['saturn_natal']['deg']),
        ('Bhava (House)',      D['saturn_natal']['house']),
        ('Motion',             f"Retrograde  (speed {D['saturn_natal']['speed']}°/day)"),
        ('Nakshatra',          D['saturn_natal']['nk']),
        ('TRANSIT SATURN (Current)',),
        ('Rashi',              D['saturn_transit']['rashi']),
        ('Degree',             D['saturn_transit']['deg']),
        ('Bhava (House)',      D['saturn_transit']['house']),
        ('Motion',             f"Direct  (speed {D['saturn_transit']['speed']}°/day)"),
        ('Nakshatra',          D['saturn_transit']['nk']),
        ('ASHTAKAVARGA',),
        ('Natal Bindu Score',  f"{D['ashtak_saturn']} / 8  (weak — challenging transit)"),
        ('Sodhya Pinda',       f"{D['sodhya_pinda']} pts  (moderate influence)"),
        ('Calculation Engine', 'Swiss Ephemeris pyswisseph v2.10.3'),
        ('Ayanamsa',           'Lahiri (Chitra Paksha)  23.590°'),
        ('Coordinate System',  'Geocentric · Apparent · Ecliptic Longitude'),
    ]

    sat_rows = []
    for item in sat_data:
        if len(item) == 1:
            sat_rows.append([
                Paragraph(item[0], ParagraphStyle('sh', fontName='Helvetica-Bold',
                    fontSize=7.5, textColor=WHITE, letterSpacing=2)),
                Paragraph('', STYLES['td']),
            ])
        else:
            sat_rows.append([
                Paragraph(item[0], STYLES['panch_l']),
                Paragraph(item[1], STYLES['mono']),
            ])

    sat_t = Table(sat_rows, colWidths=[52*mm, CW - 52*mm])
    header_rows = [i for i, item in enumerate(sat_data) if len(item) == 1]
    sat_style = [
        ('GRID',         (0,0),(-1,-1), 0.3, SILVER),
        ('TOPPADDING',   (0,0),(-1,-1), 5),
        ('BOTTOMPADDING',(0,0),(-1,-1), 5),
        ('LEFTPADDING',  (0,0),(-1,-1), 8),
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[WHITE, SILVER2]),
    ]
    for ri in header_rows:
        sat_style += [('BACKGROUND', (0,ri),(-1,ri), NAVY),
                      ('SPAN',       (0,ri),(-1,ri))]
    sat_t.setStyle(TableStyle(sat_style))
    story.append(sat_t)
    story.append(PageBreak())

    # ─────────────────────────────────────────────────────────
    # PAGE 7 — VIMSHOTTARI DASHA CHRONOLOGY
    # ─────────────────────────────────────────────────────────
    story.append(tag('§ 07  Chronology — Vimshottari Dasha'))
    story.append(Paragraph('Mahadasha \u00b7 Antardasha \u00b7 Pratyantardasha', STYLES['h1']))
    story.append(rule())
    story.append(Paragraph(
        'The Vimshottari Dasha is a 120-year planetary period system. '
        'Each Mahadasha lord governs a theme; sub-periods (Antardashas) refine timing. '
        'Current period is highlighted in gold.',
        STYLES['body']))
    story.append(Spacer(1, 6))

    dasha_rows = [[
        Paragraph('MAHADASHA', STYLES['th']),
        Paragraph('ANTARDASHA', STYLES['th']),
        Paragraph('PRATYANTARDASHA', STYLES['th']),
        Paragraph('START', STYLES['th']),
        Paragraph('END', STYLES['th']),
    ]]

    for md_name, antardashas, md_start, md_end in D['dashas']:
        # Mahadasha row
        is_current_md = 'Budha' in md_name and '2022' in md_start
        dasha_rows.append([
            Paragraph(md_name, STYLES['dasha_md']),
            Paragraph('', STYLES['td']),
            Paragraph('', STYLES['td']),
            Paragraph(md_start, STYLES['mono_sm']),
            Paragraph(md_end,   STYLES['mono_sm']),
        ])
        for ad_name, praty, ad_start, ad_end in antardashas:
            is_current_ad = 'Budha' in ad_name and '2024' in ad_start
            dasha_rows.append([
                Paragraph('', STYLES['td']),
                Paragraph('  ' + ad_name, STYLES['dasha_ad']),
                Paragraph('', STYLES['td']),
                Paragraph(ad_start, STYLES['mono_sm']),
                Paragraph(ad_end,   STYLES['mono_sm']),
            ])
            for pd_name, pd_start, pd_end in praty:
                dasha_rows.append([
                    Paragraph('', STYLES['td']),
                    Paragraph('', STYLES['td']),
                    Paragraph('    \u00b7 ' + pd_name, STYLES['dasha_pad']),
                    Paragraph(pd_start, STYLES['mono_sm']),
                    Paragraph(pd_end,   STYLES['mono_sm']),
                ])

    dt = Table(dasha_rows, colWidths=[44*mm, 44*mm, 42*mm, 24*mm, 24*mm],
               repeatRows=1)

    # Determine row indices that are MD rows
    row_styles = [
        ('BACKGROUND',    (0,0),(-1,0),  NAVY),
        ('LINEABOVE',     (0,0),(-1,0),  2, GOLD),
        ('GRID',          (0,0),(-1,-1), 0.3, SILVER),
        ('LEFTPADDING',   (0,0),(-1,-1), 6),
        ('TOPPADDING',    (0,0),(-1,-1), 5),
        ('BOTTOMPADDING', (0,0),(-1,-1), 5),
        ('VALIGN',        (0,0),(-1,-1), 'MIDDLE'),
    ]
    ri = 1
    for md_name, antardashas, md_start, md_end in D['dashas']:
        is_current_md = 'Budha' in md_name
        bg = GOLD_BG if is_current_md else SILVER2
        row_styles.append(('BACKGROUND', (0,ri),(-1,ri), bg))
        row_styles.append(('FONTNAME',   (0,ri),(-1,ri), 'Times-Bold'))
        ri += 1
        for ad_name, praty, _, _ in antardashas:
            is_cur = 'Budha' in ad_name
            if is_cur:
                row_styles.append(('BACKGROUND',(0,ri),(-1,ri), GOLD_BG))
                row_styles.append(('TEXTCOLOR', (0,ri),(-1,ri), NAVY))
            ri += 1 + len(praty)

    dt.setStyle(TableStyle(row_styles))
    story.append(dt)
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        'Current period (highlighted):  Budha Mahadasha \u00b7 Budha Antardasha  '
        '(Apr 2024 – Aug 2024)  \u00b7  Planetary rulership: Mercury governs intellect, '
        'communication, commerce, and technology.',
        STYLES['caption']))
    story.append(PageBreak())

    # ─────────────────────────────────────────────────────────
    # PAGE 8 — AI INSIGHTS
    # ─────────────────────────────────────────────────────────
    story.append(tag('§ 08  AI Insights — Interpretation Engine'))
    story.append(Paragraph('Jyogi AI \u00b7 Personalised Jyotish Analysis', STYLES['h1']))
    story.append(rule())

    section_icons = {
        'psychology': '\u2728',  # sparkles
        'career':     '\u25c6',  # diamond
        'saturn':     '\u2644',  # Saturn symbol
    }
    section_colors = {
        'psychology': VIOLET,
        'career':     TEAL,
        'saturn':     RED_SOFT,
    }

    for key, ins in D['insights'].items():
        accent = section_colors[key]
        main_col = [
            Paragraph(section_icons[key] + '  ' +
                      key.upper().replace('_', ' '), STYLES['ins_tag']),
            Paragraph(ins['title'], STYLES['ins_h']),
            Paragraph(ins['body'],  STYLES['ins_body']),
        ]
        sidebar = sidebar_panel('KEY TAKEAWAYS', ins['takeaways'], width=52*mm)

        ins_tbl = Table([[main_col, sidebar]],
                        colWidths=[CW - 56*mm, 52*mm])
        ins_tbl.setStyle(TableStyle([
            ('VALIGN',      (0,0),(-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0),(0,-1),  0),
            ('RIGHTPADDING',(0,0),(0,-1),  10),
            ('LEFTPADDING', (1,0),(1,-1),  0),
            ('TOPPADDING',  (0,0),(-1,-1), 0),
            ('BOTTOMPADDING',(0,0),(-1,-1),0),
        ]))

        # Wrap in bordered panel
        panel = Table([[ins_tbl]], colWidths=[CW])
        panel.setStyle(TableStyle([
            ('BACKGROUND',  (0,0),(-1,-1), CREAM),
            ('LINEBEFORE',  (0,0),(0,-1),  3, accent),
            ('LINEABOVE',   (0,0),(-1,0),  0.5, accent),
            ('LINEBELOW',   (0,-1),(-1,-1),0.5, SILVER),
            ('LEFTPADDING', (0,0),(-1,-1), 12),
            ('RIGHTPADDING',(0,0),(-1,-1), 10),
            ('TOPPADDING',  (0,0),(-1,-1), 10),
            ('BOTTOMPADDING',(0,0),(-1,-1),10),
        ]))
        story.append(KeepTogether([panel, Spacer(1, 10)]))

    story.append(PageBreak())

    # ─────────────────────────────────────────────────────────
    # PAGE 9 — CLOSING + DISCLAIMER
    # ─────────────────────────────────────────────────────────
    story.append(tag('§ 09  Closing Observations'))
    story.append(Paragraph('Summary \u00b7 Recommendations \u00b7 Disclaimer', STYLES['h1']))
    story.append(rule())

    story.append(Paragraph(
        '<b>Summary of Key Findings:</b>  This chart belongs to a person built for '
        'institutional leadership, deep intellectual work, and transformation through '
        'adversity. The 8th-house stellium with retrograde Saturn is the defining '
        'configuration — it bestows uncommon psychological depth and a karmic '
        'mandate to work at the edge of what most people avoid.',
        STYLES['body']))

    # Recommendations table
    rec_rows = [
        [Paragraph('DOMAIN', STYLES['th']),
         Paragraph('RECOMMENDATION', STYLES['th']),
         Paragraph('TIMING', STYLES['th'])],
        [Paragraph('Career', STYLES['td_l']),
         Paragraph('Launch knowledge products; build personal authority brand', STYLES['td_l']),
         Paragraph('2026 Q4 →', STYLES['mono_sm'])],
        [Paragraph('Finance', STYLES['td_l']),
         Paragraph('Invest in infrastructure / AI tools; avoid speculation 2026', STYLES['td_l']),
         Paragraph('2027+', STYLES['mono_sm'])],
        [Paragraph('Saturn', STYLES['td_l']),
         Paragraph('No major launches Jul–Oct 2026; use for deep review', STYLES['td_l']),
         Paragraph('Jul–Oct 2026', STYLES['mono_sm'])],
        [Paragraph('Spiritual', STYLES['td_l']),
         Paragraph('Shani puja Saturdays; chant Shani Beeja Mantra 108x', STYLES['td_l']),
         Paragraph('Ongoing', STYLES['mono_sm'])],
    ]
    rec_t = Table(rec_rows, colWidths=[28*mm, CW - 68*mm, 28*mm])
    rec_t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,0),  NAVY),
        ('LINEABOVE',     (0,0),(-1,0),  2, GOLD),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [WHITE, SILVER2]),
        ('GRID',          (0,0),(-1,-1), 0.3, SILVER),
        ('TOPPADDING',    (0,0),(-1,-1), 6),
        ('BOTTOMPADDING', (0,0),(-1,-1), 6),
        ('LEFTPADDING',   (0,0),(-1,-1), 8),
    ]))
    story.append(rec_t)
    story.append(Spacer(1, 14))

    # Closing quote
    story.append(rule(color=GOLD, thick=0.8))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        '\u201cThe stars incline, they do not compel. '
        'Jyotish is the lamp — the walking remains yours.\u201d',
        ParagraphStyle('cq', fontName='Times-Italic', fontSize=13,
                       textColor=NAVY, alignment=TA_CENTER, leading=20)))
    story.append(Spacer(1, 4))
    story.append(Paragraph('— Jyogi AI Interpretation Engine',
        ParagraphStyle('cq2', fontName='Helvetica', fontSize=9,
                       textColor=SLATE2, alignment=TA_CENTER)))
    story.append(Spacer(1, 14))

    # Disclaimer
    story.append(rule())
    story.append(Paragraph(
        '<b>Disclaimer:</b>  This report is produced by Jyogi AI for educational and '
        'reflective purposes only. Vedic astrology is a traditional interpretive system; '
        'all planetary positions are calculated using Swiss Ephemeris (pyswisseph) '
        'to arc-second precision with Lahiri ayanamsa. This report does not constitute '
        'medical, legal, or financial advice. Consult a qualified Jyotishi for '
        'personalised guidance.  |  <b>jyogi.in</b>  |  enquiries@jyogi.in',
        ParagraphStyle('disc', fontName='Helvetica', fontSize=7.5,
                       textColor=SLATE2, leading=11, alignment=TA_JUSTIFY)))

    # ── Build ──
    doc.build(story, onFirstPage=cover_bg, onLaterPages=header_footer)
    D = _D_orig   # restore module-level D
    print(f'\u2705  Report → {out}')


if __name__ == '__main__':
    build('/mnt/user-data/outputs/Jyogi_AI_Full_Kundali_Report.pdf')
