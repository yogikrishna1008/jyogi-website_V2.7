"""
jyogi_numerology_report.py — Jyogi AI 4-Page Numerology Report
===============================================================
PAGE 1  Chart Identity (Name, DOB, LP, Destiny, SU, Moolank, Kua)
PAGE 2  Multi-System Comparison Table (Pythagorean | Chaldean | Vedic/Ank)
PAGE 3  Lo Shu Grid — Vedic pool ONLY (no Pythagorean name lessons here)
PAGE 4  Name Correction · Pythagorean Karmic Name Lessons · Planes
"""
import sys, os, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reportlab.lib.pagesizes  import A4
from reportlab.lib.units       import mm
from reportlab.lib.colors      import HexColor
from reportlab.lib.enums       import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles      import ParagraphStyle
from reportlab.platypus        import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.graphics.shapes import Drawing, Rect, String

W, H   = A4
ML = MR = 18*mm; MT = 22*mm; MB = 18*mm; CW = W - ML - MR
TS = datetime.datetime.now().strftime('%d %b %Y  %H:%M')

NAVY   = HexColor('#0D1B2A'); NAVY2 = HexColor('#0f0428')
VIO    = HexColor('#7c3aed');  VIO2  = HexColor('#a78bfa')
GOLD   = HexColor('#FFC340'); GOLD2 = HexColor('#e8a800')
TEAL2  = HexColor('#2dd4bf'); ROSE  = HexColor('#e11d48')
SIL    = HexColor('#CBD5E0'); SIL2  = HexColor('#EDF2F7')
WHITE  = HexColor('#FFFFFF'); CREAM = HexColor('#FAFAF7')
SLATE  = HexColor('#4A5568'); MUTED = HexColor('#c4a97a')
DIM    = HexColor('#8a7355'); GRN   = HexColor('#86efac')
DK_VIO = HexColor('#2D2860')

def S(name,**kw):
    d=dict(fontName='Helvetica',fontSize=10,textColor=HexColor('#D1D5DB'),leading=14,spaceAfter=3)
    d.update(kw); return ParagraphStyle(name,**d)

ST = {
    'ptag' : S('ptag', fontName='Helvetica-Bold', fontSize=7.5,
                textColor=VIO2, letterSpacing=3, spaceAfter=3),
    'h1'   : S('h1',  fontName='Times-Bold',  fontSize=22, textColor=WHITE, leading=28),
    'h2'   : S('h2',  fontName='Times-Bold',  fontSize=13, textColor=WHITE, leading=18, spaceAfter=3),
    'body' : S('body',fontName='Helvetica',   fontSize=9.5,textColor=HexColor('#D1D5DB'),leading=14.5,
                spaceAfter=5, alignment=TA_JUSTIFY),
    'bull' : S('bull',fontName='Helvetica',   fontSize=9.5,textColor=HexColor('#D1D5DB'),leading=14,leftIndent=12),
    'mono' : S('mono',fontName='Courier',     fontSize=8.5,textColor=HexColor('#CBD5E0'), leading=12),
    'mono_g':S('mono_g',fontName='Courier-Bold',fontSize=9.5,textColor=GOLD, leading=13,alignment=TA_CENTER),
    'th'   : S('th',  fontName='Helvetica-Bold',fontSize=7.5,textColor=WHITE,alignment=TA_CENTER),
    'th_l' : S('th_l',fontName='Helvetica-Bold',fontSize=7.5,textColor=WHITE,alignment=TA_LEFT),
    'td'   : S('td',  fontName='Courier',     fontSize=9, textColor=HexColor('#E2E8F0'), alignment=TA_CENTER,leading=13),
    'td_l' : S('td_l',fontName='Courier',     fontSize=9, textColor=HexColor('#E2E8F0'), alignment=TA_LEFT, leading=13),
    'td_g' : S('td_g',fontName='Courier-Bold',fontSize=10,textColor=GOLD2,alignment=TA_CENTER,leading=14),
    'td_v' : S('td_v',fontName='Courier-Bold',fontSize=10,textColor=VIO2, alignment=TA_CENTER,leading=14),
    'td_t' : S('td_t',fontName='Courier-Bold',fontSize=10,textColor=TEAL2,alignment=TA_CENTER,leading=14),
    'bd'   : S('bd',  fontName='Courier',     fontSize=7.5,textColor=HexColor('#c4a97a'), alignment=TA_CENTER,leading=11),
    'cap'  : S('cap', fontName='Helvetica',   fontSize=7.5,textColor=HexColor('#94A3B8'),  alignment=TA_CENTER,leading=11),
    'kv_g' : S('kv_g',fontName='Times-Bold',  fontSize=28,textColor=GOLD,  alignment=TA_CENTER,leading=34),
    'kv_v' : S('kv_v',fontName='Times-Bold',  fontSize=28,textColor=VIO2,  alignment=TA_CENTER,leading=34),
    'kv_t' : S('kv_t',fontName='Times-Bold',  fontSize=28,textColor=TEAL2, alignment=TA_CENTER,leading=34),
    'kl'   : S('kl',  fontName='Helvetica-Bold',fontSize=6.5,textColor=HexColor('#94A3B8'),alignment=TA_CENTER,letterSpacing=2),
    'ks'   : S('ks',  fontName='Helvetica',   fontSize=8, textColor=HexColor('#c4a97a'), alignment=TA_CENTER,leading=11),
    'klo'  : S('klo', fontName='Times-Italic',fontSize=9, textColor=VIO2,  alignment=TA_CENTER),
    'ins_h': S('ins_h',fontName='Times-Bold', fontSize=12,textColor=WHITE, leading=16,spaceAfter=3),
    'ins_b': S('ins_b',fontName='Helvetica',  fontSize=9.5,textColor=HexColor('#D1D5DB'),leading=14.5,alignment=TA_JUSTIFY),
    'sug_n': S('sug_n',fontName='Times-Bold', fontSize=12,textColor=WHITE),
    'sug_w': S('sug_w',fontName='Helvetica',  fontSize=9, textColor=HexColor('#D1D5DB'), leading=13),
}

def rule(c=SIL,t=0.4):
    return HRFlowable(width=CW,thickness=t,color=c,spaceBefore=4,spaceAfter=6)
def ptag(n,s):
    return Paragraph(f'PAGE {n}  ·  {s.upper()}',ST['ptag'])

LO_LAYOUT  = [[4,9,2],[3,5,7],[8,1,6]]
LO_LABELS  = {
    1:'Intelligence / Mind',    2:'Intuition / Sensitivity',
    3:'Action / Motivation',    4:'Practicality / Organisation',
    5:'Balance / Freedom',      6:'Creativity / Vision',
    7:'Wisdom / Learning',      8:'Prosperity / Power',
    9:'Idealism / Ambition',
}

def draw_loshu(dc, width=90*mm):
    cell = 28*mm; h = cell*3+12
    d = Drawing(width, h); off = (width-cell*3)/2
    for ri,row in enumerate(LO_LAYOUT):
        for ci,n in enumerate(row):
            cnt = dc.get(n,0)
            x = off+ci*cell; y = (2-ri)*cell+10
            fill   = (HexColor('#FFC34018') if cnt>=3 else
                      HexColor('#7c3aed12') if cnt>0  else
                      HexColor('#e11d4810'))
            stroke = (GOLD if cnt>=3 else VIO2 if cnt>0 else HexColor('#e11d4838'))
            d.add(Rect(x,y,cell-3,cell-3,fillColor=fill,
                       strokeColor=stroke,strokeWidth=0.8,rx=6,ry=6))
            col = GOLD if cnt>=3 else (VIO2 if cnt>0 else DIM)
            d.add(String(x+cell/2-2,y+cell/2+3,str(n),
                         fontName='Times-Bold',fontSize=17,
                         fillColor=col.hexval(),textAnchor='middle'))
            label = ('·'*min(cnt,5)) if cnt>0 else '∅'
            d.add(String(x+cell/2-2,y+7,label,
                         fontName='Courier',fontSize=8,
                         fillColor=col.hexval(),textAnchor='middle'))
    return d

def bar(label,pct,col=GOLD,width=CW,h=11):
    d=Drawing(width,h+2); bw=(width-62)*pct/100
    d.add(Rect(62,2,width-62,h,fillColor=SIL2,strokeColor=None))
    d.add(Rect(62,2,max(bw,0),h,fillColor=col,strokeColor=None))
    d.add(String(2,3.5,label,fontName='Helvetica-Bold',fontSize=7.5,fillColor=SLATE.hexval()))
    d.add(String(width-2,3.5,f'{pct}%',fontName='Courier-Bold',fontSize=7.5,
                 fillColor=NAVY.hexval(),textAnchor='end'))
    return d

def hf(canv,doc):
    canv.saveState(); pg=doc.page; nm=getattr(doc,'_nm','')
    canv.setFillColor(NAVY); canv.rect(0,H-13*mm,W,13*mm,fill=1,stroke=0)
    canv.setFont('Helvetica-Bold',8); canv.setFillColor(GOLD)
    canv.drawString(ML,H-8.5*mm,'\u2736 JYOGI AI')
    canv.setFont('Helvetica',8); canv.setFillColor(SIL)
    canv.drawCentredString(W/2,H-8.5*mm,f'Numerology Intelligence Report  \u00b7  {nm}')
    canv.setFont('Courier',7.5); canv.setFillColor(GOLD)
    canv.drawRightString(W-MR,H-8.5*mm,f'Page {pg}')
    canv.setFillColor(NAVY); canv.rect(0,0,W,11*mm,fill=1,stroke=0)
    canv.setFont('Helvetica',7); canv.setFillColor(SIL)
    canv.drawString(ML,3.8*mm,f'Generated {TS}  \u00b7  Pythagorean \u00b7 Chaldean \u00b7 Vedic/Ank  \u00b7  jyogi.in')
    canv.setFont('Helvetica-Bold',7.5); canv.setFillColor(GOLD)
    canv.drawRightString(W-MR,3.8*mm,str(pg))
    canv.setStrokeColor(GOLD); canv.setLineWidth(0.4)
    canv.line(ML,11*mm,W-MR,11*mm)
    canv.restoreState()


def build_numerology_report_safe(out, name, dob, gender='M'):
    import importlib.util as ilu
    def load(mod, path):
        sp=ilu.spec_from_file_location(mod,path); m=ilu.module_from_spec(sp)
        sp.loader.exec_module(m); return m
    base_dir = os.path.dirname(os.path.abspath(__file__))
    eng  = load('numerology_engine', os.path.join(base_dir,'numerology_engine.py'))

    today = datetime.date.today()
    lp   = eng.life_path(dob)
    dest = eng.destiny_pythagorean(name)
    su   = eng.soul_urge_pythagorean(name)
    pers = eng.personality_pythagorean(name)
    mool = eng.vedic_moolank(dob)
    kua  = eng.vedic_kua(dob, gender)
    cv   = eng.chaldean_value(name)
    csu  = eng.chaldean_soul_urge(name)
    cprs = eng.chaldean_personality(name)
    ls   = eng.lo_shu_grid(dob, gender)
    ka   = eng.karmic_analysis(name, dob)
    nc   = eng.name_correction(name, dob)
    pl   = eng.planes_of_expression(name)
    fc   = eng.forecast(dob, today.year, today.month, today.day)
    py   = eng.personal_year(dob, today.year)

    PYTH=eng.PYTHAGOREAN; CHALD=eng.CHALDEAN; VOW=eng.VOWELS
    upper=name.upper().replace(' ','')
    pa=[(c,PYTH.get(c,0)) for c in upper if c in PYTH]
    ca=[(c,CHALD.get(c,0)) for c in upper if c in CHALD]
    pv=[(c,PYTH.get(c,0))  for c in upper if c in VOW and c in PYTH]
    cv2=[(c,CHALD.get(c,0)) for c in upper if c in VOW and c in CHALD]
    CP=set(PYTH.keys())-VOW; CC=set(CHALD.keys())-VOW
    pc=[(c,PYTH.get(c,0))  for c in upper if c in CP]
    cc=[(c,CHALD.get(c,0)) for c in upper if c in CC]
    def bd(pairs): return '  '.join(f'{c}={v}' for c,v in pairs)

    MASTER={11,22,33}; VL=eng.VEDIC_LORDS
    dob_p=dob.split('-')
    MONL=['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    dob_disp=f"{int(dob_p[2])} {MONL[int(dob_p[1])]} {dob_p[0]}"

    doc=SimpleDocTemplate(out,pagesize=A4,leftMargin=ML,rightMargin=MR,
        topMargin=MT+14*mm,bottomMargin=MB+12*mm,
        title=f'Jyogi AI Numerology — {name}',author='Jyogi AI')
    doc._nm=name; story=[]

    # ─────────────────────────────────────────────────────────
    # PAGE 1 — CHART IDENTITY
    # ─────────────────────────────────────────────────────────
    story.append(ptag('1','Chart Identity'))
    story.append(Paragraph('Numerology Intelligence Report',ST['h1']))
    story.append(rule(VIO,1.2))
    story.append(Spacer(1,4))

    # Identity card
    id_t=Table([
        [Paragraph('NAME',         ST['kl']),
         Paragraph(name,           ParagraphStyle('idv',fontName='Times-Bold',fontSize=14,textColor=WHITE,leading=18))],
        [Paragraph('DATE OF BIRTH',ST['kl']),
         Paragraph(dob_disp,       ParagraphStyle('idv2',fontName='Times-Bold',fontSize=14,textColor=WHITE,leading=18))],
        [Paragraph('GENDER',       ST['kl']),
         Paragraph('Male' if gender.upper()=='M' else 'Female',
                   ParagraphStyle('idv3',fontName='Times-Bold',fontSize=14,textColor=WHITE,leading=18))],
    ], colWidths=[38*mm,CW-38*mm])
    id_t.setStyle(TableStyle([
        ('BACKGROUND',   (0,0),(-1,-1),NAVY2),
        ('LINEABOVE',    (0,0),(-1,0), 2,GOLD),
        ('LINEBELOW',    (0,-1),(-1,-1),1,GOLD),
        ('LINEBELOW',    (0,0),(-1,-2), 0.3,DK_VIO),
        ('TOPPADDING',   (0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
        ('LEFTPADDING',  (0,0),(-1,-1),14),
    ]))
    story.append(id_t); story.append(Spacer(1,14))

    # KPI grid
    story.append(Paragraph('Core Numbers',ST['h2'])); story.append(rule())

    yr_sum=sum(int(d) for d in dob_p[0]); yr_r=yr_sum
    while yr_r>9 and yr_r not in MASTER: yr_r=sum(int(d) for d in str(yr_r))
    kua_formula=(f"Year {dob_p[0]}: {yr_sum}→{yr_r}, 11−{yr_r}={kua}"
                 if gender.upper()=='M' else
                 f"Year {dob_p[0]}: {yr_sum}→{yr_r}, 4+{yr_r}={kua}")

    def kpi_cell(val,lbl,sub,style,lord=''):
        m='★' if val in MASTER else ''
        c=[Paragraph(f'{val}{m}',style),Paragraph(lbl,ST['kl']),Paragraph(sub,ST['ks'])]
        if lord: c.append(Paragraph(lord,ST['klo']))
        return c

    kpi=[
        kpi_cell(lp,  'LIFE PATH',   'Bhagyank — Life purpose',   ST['kv_g'],VL.get(lp,'')),
        kpi_cell(dest,'DESTINY',      'Pythagorean expression',    ST['kv_v']),
        kpi_cell(su,  'SOUL URGE',   "Heart's desire",             ST['kv_g']),
        kpi_cell(pers,'PERSONALITY',  'Outer expression',          ST['kv_v']),
        kpi_cell(mool['moolank'],'MOOLANK',
                 f"Day {int(dob_p[2])} → {mool['moolank']}",      ST['kv_t'],mool['lord']),
        kpi_cell(kua, 'KUA NUMBER',   kua_formula,                 ST['kv_g']),
    ]
    kt=Table([kpi[:3],kpi[3:]],colWidths=[CW/3]*3)
    kt.setStyle(TableStyle([
        ('BACKGROUND',   (0,0),(-1,-1),NAVY2),
        ('LINEABOVE',    (0,0),(-1,0), 2,VIO2),
        ('LINEBETWEEN',  (0,0),(-1,-1),0.4,DK_VIO),
        ('LINEBELOW',    (0,0),(-1,0), 0.4,DK_VIO),
        ('TOPPADDING',   (0,0),(-1,-1),12),('BOTTOMPADDING',(0,0),(-1,-1),12),
        ('ALIGN',        (0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ]))
    story.append(kt); story.append(Spacer(1,8))

    story.append(Paragraph(
        f'Moolank:  day {int(dob_p[2])} → '
        f'{" + ".join(dob_p[2])} = {mool["moolank"]}  '
        f'·  Kua:  {kua_formula}', ST['mono']))
    story.append(Spacer(1,10)); story.append(rule())

    # Personal year strip
    story.append(Paragraph('Personal Year Forecast',ST['h2']))
    PY_TH={1:'New Beginnings',2:'Cooperation',3:'Expression',4:'Foundation',
           5:'Change & Freedom',6:'Responsibility',7:'Introspection',8:'Power & Wealth',
           9:'Completion',11:'Illumination',22:'Master Builder'}
    frows=[[Paragraph(str(fc['personal_year']['value']),ST['kv_v']),
            Paragraph(str(fc['personal_month']['value']),ST['kv_v']),
            Paragraph(str(fc['personal_day']['value']),ST['kv_v'])],
           [Paragraph('PERSONAL YEAR',ST['kl']),
            Paragraph('PERSONAL MONTH',ST['kl']),
            Paragraph('PERSONAL DAY',ST['kl'])],
           [Paragraph(fc['personal_year'].get('theme',''),ST['ks']),
            Paragraph(fc['personal_month'].get('theme',''),ST['ks']),
            Paragraph(fc['personal_day'].get('theme',''),ST['ks'])]]
    ft=Table(frows,colWidths=[CW/3]*3)
    ft.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),NAVY2),
        ('LINEABOVE',(0,0),(-1,0),1.5,TEAL2),('LINEBETWEEN',(0,0),(-1,-1),0.4,DK_VIO),
        ('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9),
        ('ALIGN',(0,0),(-1,-1),'CENTER')]))
    story.append(ft); story.append(PageBreak())

    # ─────────────────────────────────────────────────────────
    # PAGE 2 — NUMEROLOGY PROFILE TABLE
    # ─────────────────────────────────────────────────────────
    story.append(ptag('2','Numerology Profile Table'))
    story.append(Paragraph('Multi-System Comparison',ST['h1']))
    story.append(rule(VIO,1.2))
    story.append(Paragraph(
        'Pythagorean maps A–Z to 1–9 cyclically. '
        'Chaldean maps letters to 1–8 only (9 is sacred, not assigned). '
        'Vedic/Ank uses Chaldean letter values with Vedic planetary lord interpretation.',
        ST['body'])); story.append(Spacer(1,8))

    cw=[42*mm,(CW-42*mm)/3,(CW-42*mm)/3,(CW-42*mm)/3]
    def crow(lbl,pv2,chv,vv,pbd='',cbd='',vnote=''):
        return [Paragraph(lbl,ST['td_l']),
                [Paragraph(str(pv2), ST['td_g']),Paragraph(pbd,ST['bd'])],
                [Paragraph(str(chv), ST['td_v']),Paragraph(cbd,ST['bd'])],
                [Paragraph(str(vv),  ST['td_t']),Paragraph(vnote,ST['bd'])]]

    ct=Table([
        [Paragraph('CORE NUMBER',ST['th_l']),
         Paragraph('PYTHAGOREAN',ST['th']),
         Paragraph('CHALDEAN',ST['th']),
         Paragraph('VEDIC / ANK',ST['th'])],
        crow('Destiny (Expression)',
             dest,cv['final'],cv['final'],
             f"Sum {sum(v for _,v in pa)} → {dest}",
             f"Sum {cv['compound']} → {cv['final']}",
             'Namank — self-expression'),
        crow("Soul Urge (Heart's Desire)",
             su,csu['final'],csu['final'],
             f"Vowels {sum(v for _,v in pv)} → {su}",
             f"Vowels {sum(v for _,v in cv2)} → {csu['final']}",
             'Inner motivation'),
        crow('Personality (Outer Self)',
             pers,cprs['final'],cprs['final'],
             f"Cons. {sum(v for _,v in pc)} → {pers}",
             f"Cons. {sum(v for _,v in cc)} → {cprs['final']}",
             'Public expression'),
    ],colWidths=cw,repeatRows=1)
    ct.setStyle(TableStyle([
        ('BACKGROUND',   (0,0),(-1,0), NAVY),
        ('LINEABOVE',    (0,0),(-1,0), 2,GOLD),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[NAVY2,HexColor('#120533')]),
        ('GRID',         (0,0),(-1,-1),0.3,DK_VIO),
        ('TOPPADDING',   (0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
        ('LEFTPADDING',  (0,0),(-1,-1),7),
        ('VALIGN',       (0,0),(-1,-1),'MIDDLE'),
        ('ALIGN',        (1,0),(-1,-1),'CENTER'),
    ]))
    story.append(ct); story.append(Spacer(1,14))

    # Breakdown table
    story.append(Paragraph('Letter Value Breakdowns',ST['h2'])); story.append(rule())
    bdt=Table([
        [Paragraph('SYSTEM',ST['th']),Paragraph('LETTERS → VALUES → SUM → FINAL',ST['th_l'])],
        [Paragraph('Pythagorean\nDestiny',ST['td']),
         Paragraph(bd(pa)+f'  =  {sum(v for _,v in pa)} → {dest}',ST['mono'])],
        [Paragraph('Pythagorean\nSoul Urge',ST['td']),
         Paragraph(bd(pv)+f'  =  {sum(v for _,v in pv)} → {su}',ST['mono'])],
        [Paragraph('Pythagorean\nPersonality',ST['td']),
         Paragraph(bd(pc)+f'  =  {sum(v for _,v in pc)} → {pers}',ST['mono'])],
        [Paragraph('Chaldean\nDestiny',ST['td']),
         Paragraph(bd(ca)+f'  =  {cv["compound"]} → {cv["final"]}',ST['mono'])],
        [Paragraph('Chaldean\nSoul Urge',ST['td']),
         Paragraph(bd(cv2)+f'  =  {sum(v for _,v in cv2)} → {csu["final"]}',ST['mono'])],
        [Paragraph('Chaldean\nPersonality',ST['td']),
         Paragraph(bd(cc)+f'  =  {sum(v for _,v in cc)} → {cprs["final"]}',ST['mono'])],
    ],colWidths=[34*mm,CW-34*mm],repeatRows=1)
    bdt.setStyle(TableStyle([
        ('BACKGROUND',   (0,0),(-1,0), NAVY),
        ('LINEABOVE',    (0,0),(-1,0), 1.5,VIO2),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[NAVY2,HexColor('#0f0428')]),
        ('GRID',         (0,0),(-1,-1),0.3,DK_VIO),
        ('TOPPADDING',   (0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',  (0,0),(-1,-1),7),
        ('VALIGN',       (0,0),(-1,-1),'MIDDLE'),
    ]))
    story.append(bdt); story.append(Spacer(1,10))

    # Key difference note
    story.append(Paragraph(
        'KEY DIFFERENCE: In Chaldean, the number 9 is not assigned to any letter — '
        'it is considered divine and untouchable. This is why Chaldean and Pythagorean '
        'Destiny numbers often differ for the same name.',
        ParagraphStyle('kd',fontName='Helvetica-Bold',fontSize=8.5,
                       textColor=GOLD,leading=13)))
    story.append(PageBreak())

    # ─────────────────────────────────────────────────────────
    # PAGE 3 — LO SHU GRID (Vedic ONLY)
    # ─────────────────────────────────────────────────────────
    story.append(ptag('3','Lo Shu Grid  ·  Vedic Calculation Only'))
    story.append(Paragraph('Lo Shu Magic Square — Missing Numbers',ST['h1']))
    story.append(rule(VIO,1.2))
    story.append(Paragraph(
        'The Lo Shu Grid uses a Vedic birth-date data pool exclusively. '
        'Pythagorean Karmic Name Lessons — a completely separate calculation '
        '— are printed on Page 4. Do not conflate the two systems.',
        ST['body'])); story.append(Spacer(1,8))

    # Pool breakdown
    raw_d=[int(x) for x in dob.replace('-','') if x!='0']
    pool_all=raw_d+[mool['moolank'],lp,kua]
    pd_t=Table([
        [Paragraph('DATA POOL',ST['th']),   Paragraph('VALUES',ST['th_l'])],
        [Paragraph('Raw DOB digits\n(zeros excluded)',ST['td']),
         Paragraph('  '.join(str(d) for d in raw_d),ST['mono'])],
        [Paragraph('+ Moolank',ST['td']),
         Paragraph(f'{mool["moolank"]}  (day {int(dob_p[2])} → digit sum)',ST['mono'])],
        [Paragraph('+ Life Path (Bhagyank)',ST['td']),Paragraph(str(lp),ST['mono'])],
        [Paragraph('+ Kua Number',ST['td']),Paragraph(str(kua),ST['mono'])],
        [Paragraph('COMPLETE POOL',ST['th']),
         Paragraph('  '.join(str(n) for n in pool_all),ST['mono_g'])],
    ],colWidths=[48*mm,CW-48*mm])
    pd_t.setStyle(TableStyle([
        ('BACKGROUND',   (0,0),(-1,0), NAVY),
        ('BACKGROUND',   (0,-1),(-1,-1),HexColor('#1a0832')),
        ('LINEABOVE',    (0,0),(-1,0), 2,GOLD),
        ('ROWBACKGROUNDS',(0,1),(-1,-2),[NAVY2,HexColor('#0f0428')]),
        ('GRID',         (0,0),(-1,-1),0.3,DK_VIO),
        ('TOPPADDING',   (0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',  (0,0),(-1,-1),8),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ]))
    story.append(pd_t); story.append(Spacer(1,12))

    # Grid + absent table
    gd=draw_loshu(ls['digit_count'],width=90*mm)
    ab_rows=[[Paragraph('MISSING N°',ST['th']),Paragraph('DOMAIN',ST['th_l'])]]
    if ls['absent']:
        for n in ls['absent']:
            m_val=ls['meanings'].get(n,('',''))
            desc=m_val[1] if isinstance(m_val,tuple) else str(m_val)
            ab_rows.append([
                Paragraph(str(n),ParagraphStyle('an',fontName='Courier-Bold',fontSize=16,
                    textColor=ROSE,alignment=TA_CENTER,leading=20)),
                Paragraph(desc,ST['mono'])])
    else:
        ab_rows.append([Paragraph('None',ParagraphStyle('ok',fontName='Courier-Bold',
            fontSize=9,textColor=GRN,alignment=TA_CENTER)),
            Paragraph('All energies present in birth pool.',ST['mono'])])

    ab_t=Table(ab_rows,colWidths=[22*mm,CW-90*mm-22*mm-8*mm])
    ab_t.setStyle(TableStyle([
        ('BACKGROUND',   (0,0),(-1,0), NAVY),
        ('LINEABOVE',    (0,0),(-1,0), 2,ROSE),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[NAVY2,HexColor('#2a0810')]),
        ('GRID',         (0,0),(-1,-1),0.3,DK_VIO),
        ('TOPPADDING',   (0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',  (0,0),(-1,-1),6),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ]))
    mr=Table([[gd,ab_t]],colWidths=[94*mm,CW-94*mm])
    mr.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(0,-1),0),('RIGHTPADDING',(0,0),(0,-1),8),
        ('LEFTPADDING',(1,0),(1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),
    ]))
    story.append(mr); story.append(Spacer(1,6))
    story.append(Paragraph(
        '\u25a0 Gold = dominant (3+)   \u25a0 Violet = present   \u25a0 Red \u2205 = absent',
        ST['cap'])); story.append(Spacer(1,10))

    # Arrows
    if ls.get('arrows_present'):
        story.append(Paragraph('Complete Arrows (Activated Lines)',ST['h2']))
        story.append(rule())
        AN={'thought_plane':'Thought Plane (4-9-2) — strong mental capacity',
            'will_plane':'Will Plane (3-5-7) — determination and inner strength',
            'action_plane':'Action Plane (8-1-6) — physical and material drive',
            'mind_col':'Mind Column (4-3-8) — intellectual focus',
            'soul_col':'Soul Column (9-5-1) — spiritual alignment',
            'physical_col':'Physical Column (2-7-6) — material expression',
            'determination':'Arrow of Determination (4-5-6)',
            'compassion':'Arrow of Compassion (2-5-8)'}
        for a in ls['arrows_present']:
            story.append(Paragraph(f'\u2736  {AN.get(a,a.replace("_"," ").title())}',ST['bull']))
    else:
        story.append(Paragraph(
            'No complete arrows. Each missing number is an energy the soul develops in this lifetime.',
            ST['body']))

    story.append(Spacer(1,10))
    story.append(Paragraph(
        'CRITICAL NOTE: Missing Lo Shu Numbers derive exclusively from the Vedic birth-date pool. '
        'They are not the same as — and must not be mixed with — '
        'Pythagorean Karmic Name Lessons (Page 4, name letters only).',
        ParagraphStyle('warn',fontName='Helvetica-Bold',fontSize=8.5,
                       textColor=GOLD,leading=13)))
    story.append(PageBreak())

    # ─────────────────────────────────────────────────────────
    # PAGE 4 — NAME CORRECTION · KARMIC LESSONS · PLANES
    # ─────────────────────────────────────────────────────────
    story.append(ptag('4','Name Correction  ·  Karmic Lessons  ·  Planes'))
    story.append(Paragraph('Name Alignment & Karmic Analysis',ST['h1']))
    story.append(rule(VIO,1.2))

    # Harmony score
    harmony_label=nc.get('harmony_label') or nc.get('harmony','—')
    sc=nc['harmony_score']
    scol=TEAL2 if sc>=70 else GOLD if sc>=45 else ROSE
    hs_t=Table([[
        Paragraph(str(sc),ParagraphStyle('scv',fontName='Times-Bold',fontSize=44,
                  textColor=scol,alignment=TA_CENTER,leading=50)),
        [Paragraph('/ 100',ParagraphStyle('sc2',fontName='Helvetica',fontSize=12,
                   textColor=SIL,alignment=TA_LEFT)),
         Paragraph('NAME HARMONY SCORE',ST['kl']),
         Spacer(1,4),
         Paragraph(harmony_label,ParagraphStyle('hl',fontName='Times-BoldItalic',
                   fontSize=14,textColor=scol,leading=18)),
         Spacer(1,4),
         Paragraph(
             f'Life Path {nc["life_path"]}  \u00b7  '
             f'Pythagorean Destiny {nc["destiny_pyth"]}  \u00b7  '
             f'Chaldean Destiny {nc["destiny_chaldean"]}',
             ST['mono']),
        ],
    ]],colWidths=[36*mm,CW-36*mm])
    hs_t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),NAVY2),('LINEABOVE',(0,0),(-1,0),2,scol),
        ('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10),
        ('LEFTPADDING',(0,0),(-1,-1),12),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ]))
    story.append(hs_t); story.append(Spacer(1,10))

    # Suggestions
    story.append(Paragraph('Name Adjustment Suggestions',ST['h2'])); story.append(rule())
    if nc['suggestions']:
        for s in nc['suggestions']:
            mn=s.get('modified_name') or s.get('modified','')
            nd=s.get('new_destiny_pyth') or s.get('destiny','')
            lt=s.get('letter_added') or s.get('letter','')
            rn=s.get('reason','')
            sp=Table([[
                [Paragraph(mn,ST['sug_n']),
                 Paragraph(f'Add "{lt}"  \u2192  Pythagorean Destiny becomes {nd}',ST['mono']),
                 Paragraph(rn,ST['sug_w'])],
            ]],colWidths=[CW-4*mm])
            sp.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,-1),NAVY2),('LINEBEFORE',(0,0),(0,-1),3,GOLD),
                ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),10),
                ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
            ]))
            story.append(KeepTogether([sp,Spacer(1,6)]))
        story.append(Paragraph(
            'Method: single letter added to shift Pythagorean Destiny to a '
            'Life Path-compatible number. Consult Jyogi for full Chaldean + Vedic alignment.',
            ST['cap']))
    else:
        story.append(Paragraph('✓ Name is already well-aligned. No adjustment needed.',
            ParagraphStyle('ok3',fontName='Helvetica-Bold',fontSize=10,textColor=GRN)))
    story.append(Spacer(1,12))

    # ── PYTHAGOREAN KARMIC NAME LESSONS ──────────────────────
    story.append(rule(VIO2,1))
    story.append(Paragraph('Pythagorean Karmic Name Lessons',ST['h2']))
    story.append(Paragraph(
        'Numbers 1–9 with no corresponding letter in the full name under the '
        'Pythagorean mapping. These represent qualities the soul develops in '
        'this incarnation. This is a name-letter calculation only — '
        'entirely separate from Lo Shu Missing Numbers (Page 3, birth-date pool).',
        ST['body'])); story.append(Spacer(1,6))

    if ka['karmic_lessons']:
        lr=[[Paragraph('N°',ST['th']),
             Paragraph('QUALITY TO DEVELOP',ST['th_l']),
             Paragraph('MISSING LETTERS',ST['th'])]]
        for l in ka['karmic_lessons']:
            lr.append([
                Paragraph(str(l['number']),ParagraphStyle('ln',fontName='Courier-Bold',
                    fontSize=16,textColor=VIO2,alignment=TA_CENTER,leading=20)),
                Paragraph(l['meaning'],ST['mono']),
                Paragraph('  '.join(l.get('missing_letters',[])),ST['mono']),
            ])
        lt2=Table(lr,colWidths=[22*mm,CW-68*mm,46*mm],repeatRows=1)
        lt2.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),NAVY),('LINEABOVE',(0,0),(-1,0),2,VIO2),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[NAVY2,HexColor('#0f0428')]),
            ('GRID',(0,0),(-1,-1),0.3,DK_VIO),
            ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
            ('LEFTPADDING',(0,0),(-1,-1),8),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ]))
        story.append(lt2)
    else:
        story.append(Paragraph(
            '✓ All numbers 1–9 represented in the name. No karmic name lessons.',
            ParagraphStyle('ok4',fontName='Helvetica-Bold',fontSize=10,textColor=GRN)))
    story.append(Spacer(1,12))

    # ── PLANES OF EXPRESSION ─────────────────────────────────
    story.append(rule(TEAL2,1))
    story.append(Paragraph('Planes of Expression',ST['h2']))
    story.append(Paragraph(
        f'Distribution of name letters across four planes. '
        f'Dominant: {pl["dominant_plane"]}.',ST['body']))
    story.append(Spacer(1,6))
    PC={'Physical':GOLD,'Mental':TEAL2,'Emotional':VIO2,'Intuitive':ROSE}
    PD={'Physical': 'Engages the world through action, practicality, and tangible results.',
        'Mental':   'Processes experience through intellect, analysis, and logic.',
        'Emotional':'Filters reality through feeling, empathy, and values.',
        'Intuitive':'Guided by inner knowing, spiritual perception, and instinct.'}
    for plane in ['Physical','Mental','Emotional','Intuitive']:
        pct=pl[plane]['pct']; col=PC[plane]; dom=(pl['dominant_plane']==plane)
        story.append(bar(f'{plane} Plane{"  ★ DOMINANT" if dom else ""}',pct,col,CW,11))
        story.append(Spacer(1,2))
        story.append(Paragraph(f'  {PD[plane]}',
            ParagraphStyle('pd',fontName='Helvetica',fontSize=8.5,
                           textColor=MUTED,leading=12)))
        story.append(Spacer(1,6))

    # Closing
    story.append(rule(GOLD,0.8)); story.append(Spacer(1,6))
    story.append(Paragraph(
        f'Book a full Name Correction & Vedic chart reading: '
        f'wa.me/919437794561  \u00b7  jyogi.in',
        ParagraphStyle('cta',fontName='Helvetica-Bold',fontSize=9.5,
                       textColor=GOLD,alignment=TA_CENTER)))

    doc.build(story,onFirstPage=hf,onLaterPages=hf)
    return out


def build_numerology_report(out,name,dob,gender='M'):
    return build_numerology_report_safe(out,name,dob,gender)


if __name__=='__main__':
    p='/mnt/user-data/outputs/Jyogi_Numerology_Report.pdf'
    build_numerology_report_safe(p,'Jyotirmoy Giri','1982-02-21','M')
    print(f'\u2705  {p}')
