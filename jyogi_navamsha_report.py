"""
jyogi_navamsha_report.py — Jyogi AI FREE Navamsha (D9) Snapshot
==================================================================
A lightweight, 2-page, genuinely FREE report — distinct from the
paid 9-page Full Kundali PDF (jyogi_full_report.py). This is a
lead-magnet: enough real value to be worth having, not enough
depth to substitute for the paid product.

PAGE 1  Cover — Identity + D1 & D9 charts side by side
PAGE 2  Planet position table + brief Navamsha interpretation + CTA

Reuses draw_ni_chart() and the D9 (Navamsha) calculation logic from
jyogi_full_report.py rather than duplicating ~400 lines of chart-
drawing code. Only chart-drawing (pure function, no module state) is
imported — header_footer is NOT reused since it reads a module-level
global; this file defines its own lightweight header/footer instead.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units    import mm
from reportlab.lib.enums    import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles   import ParagraphStyle
from reportlab.platypus     import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
import datetime

from jyogi_full_report import (
    draw_ni_chart, NAVY, NAVY2, SLATE, SLATE2, SILVER, GOLD, GOLD2,
    GOLD_BG, WHITE, CREAM, VIOLET, TEAL, ORANGE,
)

W, H  = A4
ML = MR = 18 * mm
MT, MB = 20 * mm, 18 * mm
CW = W - ML - MR

TS = datetime.datetime.now().strftime('%d %b %Y, %H:%M IST')

_RASHIS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo',
           'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']

# ── D9 Navamsha lord per navamsha sign — used for the interpretation blurb ──
NAVAMSHA_THEMES = {
    'Aries':'initiative and independence in your inner life',
    'Taurus':'stability and a need for security in relationships',
    'Gemini':'duality and adaptability in your soul purpose',
    'Cancer':'emotional depth and a nurturing core nature',
    'Leo':'a soul drive toward recognition and self-expression',
    'Virgo':'discernment and a refining, service-oriented inner nature',
    'Libra':'partnership and balance as central soul themes',
    'Scorpio':'transformation and intensity in your deeper self',
    'Sagittarius':'a philosophical, freedom-seeking inner nature',
    'Capricorn':'discipline and long-term soul ambition',
    'Aquarius':'individuality and an unconventional inner path',
    'Pisces':'spiritual sensitivity and a compassionate soul nature',
}

def S(name, **kw):
    defaults = dict(fontName='Helvetica', fontSize=10, textColor=SLATE, leading=14, spaceAfter=4)
    defaults.update(kw)
    return ParagraphStyle(name, **defaults)

STYLES = {
    'h_cover'  : S('h_cover',  fontName='Times-Bold', fontSize=26, textColor=WHITE,
                   leading=32, alignment=TA_CENTER),
    'tagline'  : S('tagline', fontName='Helvetica', fontSize=8.5, textColor=GOLD,
                   leading=12, alignment=TA_CENTER),
    'h_cover2' : S('h_cover2', fontName='Times-Bold', fontSize=15, textColor=GOLD,
                   leading=20, alignment=TA_CENTER),
    'h_cover3' : S('h_cover3', fontName='Times-Italic', fontSize=10.5, textColor=SILVER,
                   leading=15, alignment=TA_CENTER),
    'h1'       : S('h1', fontName='Times-Bold', fontSize=15, textColor=NAVY, leading=20, spaceAfter=4),
    'h2'       : S('h2', fontName='Times-Bold', fontSize=11.5, textColor=NAVY, leading=15, spaceAfter=3),
    'tag'      : S('tag', fontName='Helvetica-Bold', fontSize=7, textColor=GOLD,
                   letterSpacing=3, spaceAfter=2),
    'body'     : S('body', fontName='Helvetica', fontSize=9.5, textColor=SLATE,
                   leading=14.5, alignment=TA_JUSTIFY, spaceAfter=6),
    'body_sm'  : S('body_sm', fontName='Helvetica', fontSize=8.5, textColor=SLATE, leading=13),
    'th'       : S('th', fontName='Helvetica-Bold', fontSize=7.5, textColor=WHITE, alignment=TA_CENTER),
    'td'       : S('td', fontName='Courier', fontSize=8.5, textColor=NAVY, alignment=TA_CENTER, leading=12),
    'cta'      : S('cta', fontName='Times-BoldItalic', fontSize=10.5, textColor=VIOLET,
                   leading=15, alignment=TA_CENTER, spaceAfter=4),
    'cta_btn'  : S('cta_btn', fontName='Helvetica-Bold', fontSize=10, textColor=WHITE,
                   leading=14, alignment=TA_CENTER),
    'footer_nav': S('footer_nav', fontName='Helvetica', fontSize=7.5, textColor=SLATE,
                   leading=11, alignment=TA_CENTER),
}

# Module-level identity block, overwritten per-request by the caller (matches
# the pattern used in jyogi_full_report.py / jyogi_saturn_report.py so the
# API layer can reuse the same D_LIVE-style dict shape it already builds).
D = {
    "name": "Sample Client", "dob": "01 Jan 2000", "tob": "12:00 PM IST",
    "pob": "New Delhi", "lagna": "Aries", "lagna_deg": "0.00",
    "report_id": "JYG-DEMO-0000", "planets": [],
}


def _d9(lon):
    """Navamsha sign from a D1 longitude — standard STARTS-array method."""
    si = int(lon / 30) % 12
    pos_in = lon % 30
    pada = int(pos_in / (30 / 9))
    STARTS = [0, 9, 6, 3, 0, 9, 6, 3, 0, 9, 6, 3]
    return (STARTS[si] + pada) % 12


def header_footer(canv, doc):
    canv.saveState()
    pg = doc.page
    if pg > 1:
        canv.setFillColor(NAVY)
        canv.rect(0, H - 13 * mm, W, 13 * mm, fill=1, stroke=0)
        canv.setFont('Helvetica-Bold', 8); canv.setFillColor(GOLD)
        canv.drawString(ML, H - 8.5 * mm, '\u2736 JYOGI AI')
        canv.setFont('Helvetica', 8); canv.setFillColor(SILVER)
        canv.drawCentredString(W / 2, H - 8.5 * mm, f'Free Navamsha Snapshot  \u00b7  {D["name"]}')
        canv.setFont('Courier', 7.5); canv.setFillColor(GOLD)
        canv.drawRightString(W - MR, H - 8.5 * mm, D["report_id"])
    canv.setFillColor(NAVY)
    canv.rect(0, 0, W, 11 * mm, fill=1, stroke=0)
    canv.setFont('Helvetica', 7); canv.setFillColor(SLATE2)
    canv.drawString(ML, 3.8 * mm, f'Generated {TS}  \u00b7  Swiss Ephemeris  \u00b7  Lahiri Ayanamsa  \u00b7  jyogi.in')
    canv.setFont('Helvetica-Bold', 8); canv.setFillColor(GOLD)
    canv.drawRightString(W - MR, 3.8 * mm, f'{pg}')
    canv.setStrokeColor(GOLD); canv.setLineWidth(0.4)
    canv.line(ML, 11 * mm, W - MR, 11 * mm)
    canv.restoreState()


def cover_bg(canv, doc):
    header_footer(canv, doc)
    canv.saveState()
    canv.setFillColor(NAVY)
    canv.rect(0, H - 62 * mm, W, 62 * mm, fill=1, stroke=0)
    canv.setStrokeColor(GOLD); canv.setLineWidth(0.6)
    canv.line(ML, H - 62 * mm, W - MR, H - 62 * mm)
    canv.restoreState()


def rule(color=SILVER, thick=0.4, w=CW, before=4, after=6):
    return HRFlowable(width=w, thickness=thick, color=color, spaceBefore=before, spaceAfter=after)


def build(out, data=None):
    """
    data: dict matching the D_LIVE shape already built in api.py's /api/report
    handler — name, dob, tob, pob, lagna, lagna_deg, report_id, planets
    (list of (pname, abbr, lon_str, lon_float, rashi, naksh, pada, speed, dig, retro) tuples).
    """
    global D
    if data:
        D = data

    doc = SimpleDocTemplate(out, pagesize=A4,
                             leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB)
    story = []

    # ── PAGE 1 : COVER + CHARTS ──────────────────────────────
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph('JYOGI.IN', STYLES['h_cover']))
    story.append(Paragraph('Vedic Astrology &bull; Numerology &bull; Tarot &bull; Muhurat &bull; Kundali AI', STYLES['tagline']))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph('FREE NAVAMSHA SNAPSHOT', STYLES['h_cover2']))
    story.append(Paragraph('Your D9 Soul Chart, at a Glance', STYLES['h_cover3']))
    story.append(Spacer(1, 10 * mm))

    id_tbl = Table([
        ['NAME',  D['name']],
        ['BORN',  f"{D['dob']}  \u00b7  {D['tob']}"],
        ['PLACE', D['pob']],
        ['LAGNA (D1)', f"{D['lagna']}  {D['lagna_deg']}\u00b0"],
    ], colWidths=[35 * mm, CW - 35 * mm])
    id_tbl.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('TEXTCOLOR', (0, 0), (0, -1), GOLD),
        ('TEXTCOLOR', (1, 0), (1, -1), NAVY),
        ('FONTNAME', (1, 0), (1, -1), 'Courier'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('LINEBELOW', (0, 0), (-1, -2), 0.3, SILVER),
    ]))
    story.append(id_tbl)
    story.append(Spacer(1, 10 * mm))

    # Compute D1 chart positions
    lagna_idx = _RASHIS.index(D['lagna']) if D['lagna'] in _RASHIS else 0
    planet_positions = {p[0]: int(p[3] / 30) % 12 for p in D['planets']}
    retro_map = {p[0]: p[9] for p in D['planets']}
    dignity_map = {p[0]: p[8] for p in D['planets']}

    d1_chart = draw_ni_chart(planet_positions, lagna_idx, retro_map, dignity_map,
                              width=82 * mm, title='D1 \u2014 BIRTH CHART (RASHI)')

    # Compute D9 Navamsha positions (same method as the full report)
    d9_pos = {}
    for row in D['planets']:
        pname, lon_val = row[0], row[3]
        d9_pos[pname] = _d9(lon_val)
    lagna_lon_approx = lagna_idx * 30 + float(str(D.get('lagna_deg', '0')).replace('\u00b0', '') or 0)
    d9_lagna = _d9(lagna_lon_approx)
    d9_lagna_sign = _RASHIS[d9_lagna]

    d9_chart = draw_ni_chart(d9_pos, d9_lagna, {}, {},
                              width=82 * mm, title='D9 \u2014 NAVAMSHA (SOUL CHART)')

    chart_tbl = Table([[d1_chart, d9_chart]], colWidths=[CW / 2, CW / 2])
    chart_tbl.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                    ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(chart_tbl)
    story.append(Spacer(1, 6 * mm))

    theme = NAVAMSHA_THEMES.get(d9_lagna_sign, 'a distinctive inner nature')
    story.append(Paragraph(
        f'Your Navamsha Lagna falls in <b>{d9_lagna_sign}</b> \u2014 classically associated with {theme}. '
        f'The Navamsha is your "soul chart": where D1 (Rashi) shows the outer life, D9 refines it, '
        f'confirming or qualifying what D1 promises \u2014 especially for marriage, dharma, and inner character.',
        STYLES['body']
    ))

    # ── PAGE 2 : PLANET TABLE + INTERPRETATION + CTA ─────────
    story.append(Spacer(1, 4 * mm))
    story.append(rule(GOLD, 0.6))
    story.append(Paragraph('PLANETARY POSITIONS (D1)', STYLES['tag']))
    story.append(Spacer(1, 2 * mm))

    rows = [['Planet', 'Sign', 'Degree', 'Nakshatra', 'Status']]
    for p in D['planets']:
        pname, _, lon_str, lon_f, rashi, naksh, pada, speed, dig, retro = p
        status = 'Retrograde' if retro else dig
        rows.append([pname, rashi, f"{lon_f % 30:.2f}\u00b0", naksh, status])

    pt = Table(rows, colWidths=[CW * .18, CW * .22, CW * .18, CW * .27, CW * .15])
    pt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 1), (-1, -1), 'Courier'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [CREAM, WHITE]),
        ('GRID', (0, 0), (-1, -1), 0.3, SILVER),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(pt)
    story.append(Spacer(1, 8 * mm))

    story.append(Paragraph('WHAT THIS SNAPSHOT COVERS \u2014 AND WHAT IT DOESN\u2019T', STYLES['tag']))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        'This free snapshot shows your verified D1 and D9 chart positions, calculated with the same '
        'Swiss Ephemeris precision and Lahiri ayanamsa used across jyogi.in. It is accurate \u2014 but '
        'intentionally brief: it does not include Dasha timing, Shadbala strength scoring, Ashtakavarga, '
        'or house-by-house interpretation, which are covered in the Full Kundali Report.',
        STYLES['body']
    ))
    story.append(Spacer(1, 8 * mm))
    story.append(rule(GOLD, 0.6))
    story.append(Spacer(1, 5 * mm))

    # ── STRONG CTA BLOCK — WhatsApp button + Full Report upsell ──
    cta_box = Table([[
        Paragraph(
            'Need personal guidance?<br/><b>Book a Jyogi reading on WhatsApp.</b>',
            STYLES['cta_btn']
        )
    ]], colWidths=[CW])
    cta_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), NAVY),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(cta_box)
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(
        '\u2192 wa.me/919437794561  \u00b7  Book on WhatsApp',
        STYLES['cta']
    ))
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph(
        'Want the full picture? The 9-page <b>Full Kundali Report</b> adds Dasha chronology, '
        'strength analysis, and personalised remedies \u2014 ask Jyogi for it on WhatsApp.',
        STYLES['body']
    ))
    story.append(Spacer(1, 8 * mm))
    story.append(rule(SILVER, 0.4))
    story.append(Spacer(1, 4 * mm))

    # ── EXPLORE MORE ON JYOGI.IN — compact footer nav, not an ad wall ──
    story.append(Paragraph('EXPLORE MORE ON JYOGI.IN', STYLES['tag']))
    story.append(Paragraph(
        'Free Kundli &nbsp;|&nbsp; Compatibility Check &nbsp;|&nbsp; Tarot Reading &nbsp;|&nbsp; '
        'Muhurat &nbsp;|&nbsp; Numerology &nbsp;|&nbsp; Blog &nbsp;\u2014&nbsp; jyogi.in',
        STYLES['footer_nav']
    ))

    doc.build(story, onFirstPage=cover_bg, onLaterPages=header_footer)


if __name__ == '__main__':
    build('/tmp/navamsha_test.pdf')
    print('Test PDF written to /tmp/navamsha_test.pdf')
