// ============================================================
// compat.js — Ashtakoot Guna Milan (8 Kuta engine)
// Pure JS — no API dependency, works instantly
// Tables verified against Parashara's Light
// ============================================================

function openCompPicker(hidId, type){
  _compPickerTarget={hidId, type};
  _pt=null; // disable normal picker
  const ov=document.getElementById('picker-overlay');
  const grid=document.getElementById('picker-items');
  const title=document.getElementById('picker-title');
  const items=[];
  if(type==='day'){title.textContent='Select Day';grid.className='picker-items g4';for(let d=1;d<=31;d++)items.push({v:String(d).padStart(2,'0'),l:String(d).padStart(2,'0')});}
  else if(type==='month'){title.textContent='Select Month';grid.className='picker-items g3';_MONTHS.forEach((m,i)=>items.push({v:String(i+1).padStart(2,'0'),l:m}));}
  else{title.textContent='Select Year';grid.className='picker-items g4';for(let y=new Date().getFullYear();y>=1930;y--)items.push({v:String(y),l:String(y)});}
  const cur=document.getElementById(hidId).value;
  grid.innerHTML=items.map(it=>'<div class="pi'+(cur===it.v?' sel':'')+'" onclick="pickCompVal(\''+it.v+'\',\''+it.l+'\')" >'+it.l+'</div>').join('');
  ov.classList.add('open');
}
function pickCompVal(v,l){
  if(!_compPickerTarget){ closePicker(); return; }
  const t=_compPickerTarget;
  document.getElementById(t.hidId).value=v;
  // Find label span
  const btnId=t.hidId+'-btn';
  const lblId=t.hidId+'-lbl';
  const b=document.getElementById(btnId);
  const lb=document.getElementById(lblId);
  if(lb) lb.textContent=l;
  if(b){b.classList.remove('empty');b.classList.add('filled');}
  _compPickerTarget=null;
  closePicker();
}

// ── Kuta (Ashtakoot) — Full Parashara implementation ──────────────────────

// Nakshatra lords (Dasha lords in order)
var KUTA_LORDS=['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury'];

// Rashi lords
var RASHI_LORD=['Mars','Venus','Mercury','Moon','Sun','Mercury','Venus','Mars','Jupiter','Saturn','Saturn','Jupiter'];

// Varna by rashi: 0=Shudra, 1=Vaishya, 2=Kshatriya, 3=Brahmin
var VARNA_KUTA=[2,1,0,3, 2,1,0,3, 2,1,0,3];

// Vashya table [12x12]: 0=no vashya, 1=one-way, 2=mutual

// Vashya groups for same-group matching
var VASHYA_GROUP=['Chatuspada','Chatuspada','Dwipada','Jalachara',
                  'Vanachara','Dwipada','Dwipada','Keeta',
                  'Dwipada','Chatuspada','Dwipada','Jalachara'];
var VASHYA_TABLE=[
  [2,0,0,0,1,0,0,0,0,0,0,0], // Aries
  [0,2,0,1,0,0,0,0,0,0,0,0], // Taurus
  [0,0,2,0,0,1,0,0,0,0,0,0], // Gemini
  [0,0,0,2,0,0,1,1,0,0,0,0], // Cancer
  [0,0,0,0,2,0,0,0,1,0,0,0], // Leo
  [0,0,1,0,0,2,0,0,0,1,0,0], // Virgo
  [0,0,0,1,0,0,2,0,0,0,0,0], // Libra
  [0,0,0,1,0,0,0,2,0,0,0,1], // Scorpio
  [0,1,0,0,0,0,0,0,2,0,0,0], // Sagittarius
  [1,0,0,0,0,0,0,0,0,2,0,0], // Capricorn
  [1,0,0,0,0,0,0,0,0,0,2,0], // Aquarius
  [1,0,0,1,0,0,0,1,0,0,0,2], // Pisces
];

// Tara scores for positions 1-9 (Janma to Param Mitra)
var TARA_SCORES=[1.5,3,0,3,1.5,3,0,3,3]; // Janma=1.5,Sampat=3,Vipat=0,Kshema=3,Pratyak=1.5,Sadhana=3,Naidhana=0,Mitra=3,ParamMitra=3

// Yoni by nakshatra (0=Horse,1=Elephant,2=Sheep,3=Snake,4=Dog,5=Cat,6=Rat,7=Cow,8=Buffalo,9=Tiger,10=Deer,11=Mongoose)
// Yoni by nakshatra: 0=Horse,1=Elephant,2=Sheep,3=Serpent,4=Dog,5=Cat,6=Rat,7=Cow,8=Buffalo,9=Tiger,10=Deer,11=Mongoose,12=Lion
var YONI_NK=[0,1,2,3,3,4,5,2,5,6,6,7,8,9,8,9,10,10,4,11,11,11,12,0,12,7,1];
var YONI_NAME=['Horse','Elephant','Sheep','Serpent','Dog','Cat','Rat','Cow','Buffalo','Tiger','Deer','Mongoose','Lion'];
var YONI_ENEMY={0:1,1:0, 2:3,3:2, 4:5,5:4, 6:7,7:6, 8:9,9:8, 10:12,12:10};

// Planetary friendship (Parashara)
var PL_FRIENDS={
  Mars:['Sun','Moon','Jupiter'],
  Venus:['Mercury','Saturn'],
  Mercury:['Sun','Venus'],
  Moon:['Sun','Mercury'],
  Sun:['Moon','Mars','Jupiter'],
  Jupiter:['Sun','Moon','Mars'],
  Saturn:['Mercury','Venus'],
  Rahu:['Venus','Saturn','Mercury'],
  Ketu:['Mars','Venus','Saturn']
};
var PL_NEUTRAL={
  Sun:['Mercury'],
  Moon:['Mars','Jupiter','Venus','Saturn'],
  Mars:['Venus','Saturn'],
  Mercury:['Moon','Mars','Jupiter','Saturn'],
  Jupiter:['Saturn','Venus'],
  Venus:['Moon','Mars','Jupiter'],
  Saturn:['Moon','Jupiter']
};
function plRelation(a,b){
  if(a===b) return 'same';
  var f=PL_FRIENDS[a]||[];
  var n=PL_NEUTRAL[a]||[];
  if(f.indexOf(b)>=0) return 'friend';
  if(n.indexOf(b)>=0) return 'neutral';
  return 'enemy';
}

// Gana by nakshatra: 0=Deva, 1=Manushya, 2=Rakshasa (Parashara standard)
var GANA_NK=[
  0, // 0  Ashwini       Deva
  1, // 1  Bharani        Manushya
  2, // 2  Krittika       Rakshasa
  0, // 3  Rohini         Deva
  0, // 4  Mrigashira     Deva
  2, // 5  Ardra          Manushya (some say Rakshasa; Parashara = Manushya — using 2 per most sources)
  0, // 6  Punarvasu      Deva
  0, // 7  Pushya         Deva
  2, // 8  Ashlesha       Rakshasa
  2, // 9  Magha          Rakshasa
  1, // 10 Purva Phalguni Manushya
  0, // 11 Uttara Phalguni Deva
  0, // 12 Hasta          Deva
  2, // 13 Chitra         Rakshasa
  0, // 14 Swati          Deva
  2, // 15 Vishakha       Rakshasa
  0, // 16 Anuradha       Deva
  2, // 17 Jyeshtha       Rakshasa
  2, // 18 Mula           Rakshasa
  1, // 19 Purva Ashadha  Manushya
  1, // 20 Uttara Ashadha Manushya  ← key: was wrong in old engine
  0, // 21 Shravana       Deva
  2, // 22 Dhanishtha     Rakshasa
  0, // 23 Shatabhisha    Deva
  0, // 24 Purva Bhadrapada Deva
  0, // 25 Uttara Bhadrapada Deva
  0, // 26 Revati         Deva
];
// Gana score matrix [g1][g2]
var GANA_MATRIX=[[6,6,0],[5,6,0],[0,0,6]]; // Deva+Deva=6,Deva+Manushya=6,Deva+Rakshasa=0,Manushya+Deva=5,Manushya+Manushya=6,Rakshasa+Rakshasa=6 // D-D=6,D-M=5,D-R=0,M-M=6,M-R=0,R-R=6 // D-D=6, D-M=5, D-R=1, M-M=6, M-R=0, R-R=6

// Nadi: 0=Adya(Vata), 1=Madhya(Pitta), 2=Antya(Kapha) — simple repeating pattern
// Nadi table matching Parashara's Light (middle group of 9 reversed)
var NADI_NK=[0,1,2,0,1,2,0,1,2, 2,1,0,2,1,0,2,1,0, 0,1,2,0,1,2,0,1,2]; // PL standard

function toggleCompatOpt(person){
  var fields=document.getElementById(person+'-opt-fields');
  var arrow=document.getElementById(person+'-opt-arrow');
  if(!fields) return;
  if(fields.style.display==='none'){
    fields.style.display='flex';
    if(arrow) arrow.textContent='▾';
  } else {
    fields.style.display='none';
    if(arrow) arrow.textContent='▸';
  }
}

function parseTimeToUT(timeStr){
  // Parse "10:30 AM" or "22:15" → UT float (subtracts IST 5.5h)
  if(!timeStr||!timeStr.trim()) return 6; // default 11:30 IST
  var tp=timeStr.trim().toUpperCase();
  var pm=tp.indexOf('PM')>=0;
  var am=tp.indexOf('AM')>=0;
  var nums=tp.replace(/[^0-9:]/g,'').split(':');
  var h=parseInt(nums[0])||0;
  var m=nums.length>1?(parseInt(nums[1])||0):0;
  if(pm&&h!==12) h+=12;
  if(am&&h===12) h=0;
  return h+m/60-5.5; // IST → UT
}

function getMoonSignFromDOB(day,month,year,timeStr){
  var utH=parseTimeToUT(timeStr);
  var jd=toJD(year,month,day,utH);
  var moonLon=calcMoon(jd); // calcMoon already returns sidereal via toSid()
  return Math.floor(mod(moonLon,360)/30);
}

function getMoonNakshatra(d,m,y,timeStr){
  var utH=parseTimeToUT(timeStr);
  var jd=toJD(+y,+m,+d,utH);
  var moonLon=mod(calcMoon(jd),360); // calcMoon already returns sidereal via toSid()
  return Math.floor(moonLon/(360/27));
}

function calcCompatibility(){
  var c1d=document.getElementById('c1-day').value;
  var c1m=document.getElementById('c1-month').value;
  var c1y=document.getElementById('c1-year').value;
  var c2d=document.getElementById('c2-day').value;
  var c2m=document.getElementById('c2-month').value;
  var c2y=document.getElementById('c2-year').value;
  var c1n=document.getElementById('c1-name').value||'Person 1';
  var c2n=document.getElementById('c2-name').value||'Person 2';
  var c1t=(document.getElementById('c1-time')||{}).value||'';
  var c1city=(document.getElementById('c1-city')||{}).value||'';
  var c2t=(document.getElementById('c2-time')||{}).value||'';
  var c2city=(document.getElementById('c2-city')||{}).value||'';

  if(!c1d||!c1m||!c1y||!c2d||!c2m||!c2y){
    document.getElementById('compat-result').innerHTML='<p style="color:#f87171;text-align:center;padding:12px;">Please select birth dates for both persons.</p>';
    return;
  }

  var ms1=getMoonSignFromDOB(+c1d,+c1m,+c1y,c1t,c1city);
  var ms2=getMoonSignFromDOB(+c2d,+c2m,+c2y,c2t,c2city);
  var nk1=getMoonNakshatra(c1d,c1m,c1y,c1t);
  var nk2=getMoonNakshatra(c2d,c2m,c2y,c2t);
  var scores={};

  // 1. VARNA (1 pt): Boy's varna must be >= Girl's varna
  var v1=VARNA_KUTA[ms1], v2=VARNA_KUTA[ms2];
  scores.varna = (v1 >= v2) ? 1 : 0;

  // 2. VASHYA (2 pts): proper table lookup
  if(VASHYA_GROUP[ms1]===VASHYA_GROUP[ms2]){
    scores.vashya=2;
  } else {
    if(VASHYA_GROUP[ms1]===VASHYA_GROUP[ms2]){
    scores.vashya=2;
  } else {
    scores.vashya=VASHYA_TABLE[ms1][ms2];
  }
  }

  // 3. TARA (3 pts): average of both directions (verified against PL)
  var td1=mod(nk2-nk1,27);
  var td2=mod(nk1-nk2,27);
  scores.tara=(TARA_SCORES[td1%9]+TARA_SCORES[td2%9])/2;

  // 4. YONI (4 pts): by nakshatra animal
  var y1=YONI_NK[nk1], y2=YONI_NK[nk2];
  if(y1===y2) scores.yoni=4;
  else if(YONI_ENEMY[y1]===y2||YONI_ENEMY[y2]===y1) scores.yoni=0;
  else scores.yoni=2;

  // 5. GRAHA MAITRI (5 pts): rashi lord friendship
  var l1=RASHI_LORD[ms1], l2=RASHI_LORD[ms2];
  var r12=plRelation(l1,l2), r21=plRelation(l2,l1);
  if(r12==='same') scores.maitri=5;
  else if(r12==='friend'&&r21==='friend') scores.maitri=5;
  else if(r12==='friend'||r21==='friend') scores.maitri=4;
  else if(r12==='neutral'&&r21==='neutral') scores.maitri=3;
  else if((r12==='friend'&&r21==='enemy')||(r12==='enemy'&&r21==='friend')) scores.maitri=1;
  else if((r12==='neutral'&&r21==='enemy')||(r12==='enemy'&&r21==='neutral')) scores.maitri=0.5;
  else if((r12==='friend'&&r21==='enemy')||(r12==='enemy'&&r21==='friend')) scores.maitri=1;
  else if((r12==='neutral'&&r21==='enemy')||(r12==='enemy'&&r21==='neutral')) scores.maitri=0.5;
  else if(r12==='enemy'&&r21==='enemy') scores.maitri=0;
  else scores.maitri=1;

  // 6. GANA (6 pts): by nakshatra gana
  var g1=GANA_NK[nk1], g2=GANA_NK[nk2];
  scores.gana=GANA_MATRIX[g1][g2];

  // 7. BHAKOOT / RASHI (7 pts): Parashara inauspicious pairs only
  var d1=mod(ms2-ms1,12)+1, d2=mod(ms1-ms2,12)+1;
  var pair=[Math.min(d1,d2),Math.max(d1,d2)].join('/');
  var badPairs=['2/12','5/9','6/8'];
  scores.rashi=badPairs.indexOf(pair)>=0?0:7;

  // 8. NADI (8 pts): different nadi = 8, same = 0
  var n1=NADI_NK[nk1], n2=NADI_NK[nk2];
  var nadiDosha=(n1===n2);
  scores.nadi=nadiDosha?0:8;

  // Nadi Dosha Parihara (cancellation)
  var nadiParihara=false;
  var nadiPariharaReason='';
  if(nadiDosha){
    if(ms1===ms2){nadiParihara=true;nadiPariharaReason='Same Moon sign cancels Nadi Dosha';}
    else if(nk1===nk2){nadiParihara=true;nadiPariharaReason='Same Nakshatra cancels Nadi Dosha';}
    else{
      var rl=plRelation(RASHI_LORD[ms1],RASHI_LORD[ms2]);
      if(rl==='friend'||rl==='same'){nadiParihara=true;nadiPariharaReason='Friendly Rashi lords cancel Nadi Dosha';}
    }
    if(mod(ms2-ms1,12)===6||mod(ms1-ms2,12)===6){nadiParihara=true;nadiPariharaReason='1/7 Moon signs cancel Nadi Dosha';}
    if(nadiParihara) scores.nadi=8; // dosha cancelled — full points
  }

  var total=0;
  var keys=['varna','vashya','tara','yoni','maitri','gana','rashi','nadi'];
  keys.forEach(function(k){total+=scores[k];});
  var pct=Math.round((total/36)*100);
  var verdict=pct>=75?'Highly Compatible':pct>=60?'Good Match':pct>=45?'Average — Needs Awareness':'Challenging — Remedies Advised';
  var verdictColor=pct>=75?'#86efac':pct>=60?'#fbbf24':pct>=45?'#fb923c':'#f87171';

  var GANA_NAME=['Deva','Manushya','Rakshasa'];
  var NADI_NAME=['Adya (Vata)','Madhya (Pitta)','Antya (Kapha)'];
  var nak1Name=NAKSH[nk1]||'', nak2Name=NAKSH[nk2]||'';

  var detailRows=[
    {k:'varna', label:'Varna', max:1},
    {k:'vashya', label:'Vashya', max:2},
    {k:'tara', label:'Tara', max:3},
    {k:'yoni', label:'Yoni', max:4},
    {k:'maitri', label:'Graha Maitri', max:5},
    {k:'gana', label:'Gana', max:6},
    {k:'rashi', label:'Bhakoot', max:7},
    {k:'nadi', label:'Nadi', max:8},
  ];

  var rowsHtml=detailRows.map(function(row){
    var v=scores[row.k], mx=row.max;
    var pf=Math.round((v/mx)*100);
    var fc=pf>=80?'#86efac':pf>=50?'#fbbf24':'#f87171';
    return '<div class="compat-row">'+
      '<span class="compat-label">'+row.label+'</span>'+
      '<div style="flex:1;margin:0 10px;"><div class="compat-bar"><div class="compat-bar-fill" style="width:'+pf+'%;background:'+fc+';"></div></div></div>'+
      '<span class="compat-val" style="color:'+fc+';">'+v+'/'+mx+'</span>'+
      '</div>';
  }).join('');

  var doshaHtml='';
  if(nadiDosha&&!nadiParihara){
    doshaHtml='<div style="margin-top:12px;padding:10px 14px;background:rgba(248,113,113,0.08);border:1px solid rgba(248,113,113,0.25);border-radius:8px;font-size:13px;color:#f87171;">⚠ Nadi Dosha present — consult an astrologer for remedies</div>';
  } else if(nadiDosha&&nadiParihara){
    doshaHtml='<div style="margin-top:12px;padding:10px 14px;background:rgba(134,239,172,0.08);border:1px solid rgba(134,239,172,0.2);border-radius:8px;font-size:13px;color:#86efac;">✓ '+nadiPariharaReason+'</div>';
  }

  var resultHTML=
    '<div style="text-align:center;margin-bottom:20px;">'+
      '<div class="compat-score-ring" style="border-color:'+verdictColor+';background:rgba(255,255,255,0.03);">'+
        '<div class="compat-score-num" style="color:'+verdictColor+';">'+pct+'%</div>'+
        '<div class="compat-score-lbl">MATCH</div>'+
      '</div>'+
      '<div style="font-family:Cinzel,serif;font-size:15px;color:'+verdictColor+';margin-bottom:4px;">'+verdict+'</div>'+
      '<div style="font-size:14px;color:var(--muted);">'+RASHIS[ms1]+' Moon × '+RASHIS[ms2]+' Moon</div>'+
      '<div style="font-size:13px;color:var(--dim);">'+nak1Name+' ('+GANA_NAME[g1]+' / '+NADI_NAME[n1]+') × '+nak2Name+' ('+GANA_NAME[g2]+' / '+NADI_NAME[n2]+')</div>'+
    '</div>'+
    '<div style="margin-bottom:16px;">'+
      rowsHtml+
      '<div style="font-weight:bold;display:flex;justify-content:space-between;padding:10px 0;border-top:1px solid rgba(255,195,64,0.15);margin-top:4px;">'+
        '<span style="font-family:Cinzel,serif;font-size:14px;color:var(--gold);">TOTAL KUTA SCORE</span>'+
        '<span style="font-family:Cinzel,serif;color:'+verdictColor+';">'+total+' / 36</span>'+
      '</div>'+
    '</div>'+
    doshaHtml+
    '<div style="padding:14px;background:rgba(255,195,64,0.05);border:1px solid rgba(255,195,64,0.15);border-radius:10px;text-align:center;margin-top:12px;">'+
      '<div style="font-size:14px;color:var(--muted);margin-bottom:8px;">Full match includes Manglik analysis, Dasha harmony, and personalised remedies.</div>'+
      '<button onclick="openWhatsApp(&apos;Hi Jyogi, Kundali match for '+c1n+' & '+c2n+', score '+total+'/36&apos;)" style="padding:10px 20px;background:linear-gradient(135deg,#e11d48,#9f1239);color:#fff;border:none;border-radius:20px;font-family:inherit;font-size:14px;cursor:pointer;">💑 Book Full Kundali Match →</button>'+
    '</div>';

  document.getElementById('compat-result').innerHTML=resultHTML;
  saveLog({type:'compatibility',c1:c1n,ms1:RASHIS[ms1],c2:c2n,ms2:RASHIS[ms2],score:total,pct:pct,city:c1city||c2city||''});
}

// getMoonNakshatra defined above


// ════════════════════════════════════════════════════════════════
// FEATURE: DREAM JOURNAL
// ════════════════════════════════════════════════════════════════
var _dreamMood='peaceful';

