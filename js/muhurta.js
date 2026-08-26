// ============================================================
// muhurta.js — Panchang + Muhurta scoring
// Pure JS — no API dependency, works instantly
// Rahu Kaal verified against Drik Panchang
// ============================================================

// ── Panchang constants (used by calcPanchang) ────────────────────────────
var TITHI_NAMES_30=['Pratipada','Dwitiya','Tritiya','Chaturthi','Panchami','Shashthi','Saptami','Ashtami','Navami','Dashami','Ekadashi','Dwadashi','Trayodashi','Chaturdashi','Purnima','Pratipada','Dwitiya','Tritiya','Chaturthi','Panchami','Shashthi','Saptami','Ashtami','Navami','Dashami','Ekadashi','Dwadashi','Trayodashi','Chaturdashi','Amavasya'];
var YOGA_BAD=new Set([0,5,8,9,12,14,16,18,26]);
var KARANA_N=['Bava','Balava','Kaulava','Taitila','Garija','Vanija','Vishti','Shakuni','Chatushpada','Naga','Kimstughna'];
var RAHU_SLOT={0:5,1:2,2:7,3:5,4:6,5:4,6:3}; // verified vs Drik Panchang

function getTithiNum(jd){
  const sunLon=mod(calcSun(jd)-getLahiri(jd),360);
  const moonLon=mod(calcMoon(jd)-getLahiri(jd),360);
  return Math.floor(mod(moonLon-sunLon,360)/12)+1;
}



let _muhurtaActivity=null;

// ── Panchang constants ───────────────────────────────────────────
var YOGA_NAMES=['Vishkambha','Priti','Ayushman','Saubhagya','Shobhana','Atiganda',
  'Sukarma','Dhriti','Shula','Ganda','Vriddhi','Dhruva','Vyaghata','Harshana','Vajra',
  'Siddhi','Vyatipata','Variyan','Parigha','Shiva','Siddha','Sadhya','Shubha','Shukla',
  'Brahma','Indra','Vaidhrti'];
var KARANA_MOV=['Bava','Balava','Kaulava','Taitila','Garija','Vanija','Vishti(Bhadra)'];
// Rahu Kaal offset from 6 AM (hours), by weekday 0=Sun..6=Sat
// Assumes 12h day 6AM-6PM, 8 slots of 1.5h each
var RAHU_KAAL=[4.5,7.5,3.0,6.0,1.5,10.5,7.5];
var ABHIJIT_START=11+(36/60), ABHIJIT_END=12+(24/60); // 11:36–12:24 IST

function getDayPanchang(dateObj){
  // Returns full panchang for a given JS Date at noon IST
  var y=dateObj.getFullYear(),m=dateObj.getMonth()+1,d=dateObj.getDate();
  var j=toJD(y,m,d,6.5); // noon IST = 06:30 UT
  var ay=getLahiri(j);
  var sunSid=mod(calcSun(j)+ay,360); // calcSun already returns sidereal
  // Actually calcSun returns sidereal. But sun_lon above returned tropical.
  // Let's use raw tropical + subtract ayanamsa for consistency:
  function tropSun(jd){
    var T=(jd-2451545)/36525;
    var M=mod(357.52911+35999.05029*T,360);
    var C=(1.914602-0.004817*T)*Math.sin(d2r(M))+(0.019993-0.000101*T)*Math.sin(d2r(2*M));
    return mod(280.46646+36000.76983*T+C,360);
  }
  var sunT=tropSun(j);
  var sunS=mod(sunT-ay,360);
  var moonT=calcMoon(j); // calcMoon returns tropical
  var moonS=mod(moonT-ay,360); // now sidereal via subtraction? No — calcMoon returns tropical already with getLahiri called in calcSun
  // Actually let's recalculate correctly:
  // calcMoon in our code returns tropical longitude
  // calcSun returns sidereal (uses toSid internally)
  // So for panchang we need:
  var sunSidereal=calcSun(j);   // already sidereal
  var moonLonTrop=calcMoon(j);  // tropical
  var moonSidereal=mod(moonLonTrop-ay,360); // sidereal
  
  var tithiRaw=mod(moonSidereal-sunSidereal,360);
  var tithi=Math.floor(tithiRaw/12)+1;
  var nk=Math.floor(moonSidereal/(360/27));
  var ms=Math.floor(moonSidereal/30);
  var yogaCombined=mod(sunSidereal+moonSidereal,360);
  var yoga=Math.floor(yogaCombined/(360/27));
  // Karana
  var kRaw=Math.floor(tithiRaw/6);
  var karanaName,isBhadra=false;
  if(kRaw===0){karanaName='Kimstughna';}
  else if(kRaw>=1&&kRaw<=56){karanaName=KARANA_MOV[(kRaw-1)%7];isBhadra=((kRaw-1)%7===6);}
  else if(kRaw===57){karanaName='Shakuni';}
  else if(kRaw===58){karanaName='Chatushpada';}
  else if(kRaw===59){karanaName='Naga';}
  else{karanaName='Kimstughna';}
  // Vara
  var vara=dateObj.getDay(); // 0=Sun
  // Rahu Kaal
  var rahuStart=6+RAHU_KAAL[vara];
  var rahuEnd=rahuStart+1.5;
  function fmtH(h){var hh=Math.floor(h),mm=Math.round((h-hh)*60);return (hh<10?'0':'')+hh+':'+(mm<10?'0':'')+mm;}
  return{
    y,m,d,j,
    sunSid:sunSidereal,moonSid:moonSidereal,
    tithi,tithiRaw,nk,ms,yoga,karanaName,isBhadra,vara,
    rahuStart,rahuEnd,
    rahuLabel:fmtH(rahuStart)+' – '+fmtH(rahuEnd),
    isYogaBad:MUHURTA_BAD_YOGA.has(yoga),
    yogaName:YOGA_NAMES[yoga]
  };
}

function scoreDayForActivity(pp, act){
  // pp = calcPanchang() result
  // act = ACTIVITY_DATA[key] object
  var a = typeof act === 'string' ? ACTIVITY_DATA[act] : act;
  if(!a) return {stars:3, score:5, good:[], warn:[]};

  var s=0, good=[], warn=[];

  // Tithi (pp.tNum = 1-30)
  if(a.goodT && a.goodT.indexOf(pp.tNum)>=0)       {s+=3; good.push(pp.tName+' ✓');}
  else if(a.avoidT && a.avoidT.indexOf(pp.tNum)>=0) {s-=3; warn.push(pp.tName+' ✗');}

  // Nakshatra (pp.nkIdx = 0-26)
  if(a.goodNK && a.goodNK.indexOf(pp.nkIdx)>=0)       {s+=3; good.push(pp.nkName+' ✓');}
  else if(a.avoidNK && a.avoidNK.indexOf(pp.nkIdx)>=0) {s-=3; warn.push(pp.nkName+' ✗');}

  // Weekday (pp.wd = 0=Sun..6=Sat)
  if(a.goodWD && a.goodWD.indexOf(pp.wd)>=0)       {s+=2; good.push(WEEKDAY_NAMES[pp.wd]+' ✓');}
  else if(a.avoidWD && a.avoidWD.indexOf(pp.wd)>=0) {s-=2; warn.push(WEEKDAY_NAMES[pp.wd]+' ✗');}

  // Yoga
  if(pp.yogaBad) {s-=2; warn.push(pp.yogaName+' ✗');}
  else           {s+=1; good.push(pp.yogaName+' ✓');}

  // Bhadra (Vishti karana)
  if(pp.bhadra)  {s-=2; warn.push('Vishti/Bhadra ✗');}

  var stars = Math.max(1, Math.min(5, Math.round((s+5)/2.5)));
  return {stars:stars, score:s, good:good, warn:warn};
}

function approxSunrise(doy){
  // Approximate sunrise for India (range ~5:30-6:30 AM IST)
  return 6.0 + 0.5*Math.sin(2*Math.PI*(doy-80)/365);
}

function getDayOfYear(date){
  var start=new Date(date.getFullYear(),0,0);
  return Math.round((date-start)/86400000);
}

function calcPanchang(y,mo,d){
  var j=toJD(y,mo,d,0.5); // 6 AM IST = 0 UT approx
  var s=mod(calcSun(j),360);    // already sidereal from calcSun
  var m=mod(calcMoon(j),360);   // already sidereal from calcMoon
  var diff=mod(m-s,360);
  // Tithi
  var tNum=Math.floor(diff/12)+1;  // 1-30
  // Nakshatra
  var nkIdx=Math.floor(m/(360/27));
  var nkPada=Math.floor((m%(360/27))/(360/27/4))+1;
  // Yoga
  var yogaIdx=Math.floor(mod(s+m,360)/(360/27));
  // Karana
  var karNum=Math.floor(diff/6);
  var karName;
  if(karNum===0) karName='Kimstughna';
  else if(karNum>=57){var fx=['Shakuni','Chatushpada','Naga','Kimstughna'];karName=fx[Math.min(karNum-57,3)];}
  else karName=KARANA_N[((karNum-1)%7)];
  // Weekday
  var dt=new Date(y,mo-1,d);
  var wd=dt.getDay(); // 0=Sun..6=Sat
  var doy=getDayOfYear(dt);
  var sr=approxSunrise(doy);
  var rahuStart=sr+(RAHU_SLOT[wd]-1)*1.5;
  var rahuEnd=rahuStart+1.5;
  function fmt(h){return String(Math.floor(h)).padStart(2,'0')+':'+String(Math.round((h%1)*60)).padStart(2,'0');}
  return {
    tNum,tName:TITHI_NAMES_30[tNum-1]||('Tithi '+tNum),
    paksha:tNum<=15?'Shukla':'Krishna',
    nkIdx,nkName:NAKSH[nkIdx],nkPada,
    moonSign:RASHIS[Math.floor(m/30)],
    sunSign:RASHIS[Math.floor(s/30)],
    yogaIdx,yogaName:YOGA_NAMES[yogaIdx],yogaBad:YOGA_BAD.has(yogaIdx),
    karName,bhadra:karName==='Vishti',
    wd,rahuStr:fmt(rahuStart)+'–'+fmt(rahuEnd),
    rahuStart,rahuEnd,sr
  };
}

function scoreDayForActivity(p,act){
  var s=0,good=[],warn=[];
  var a=ACTIVITY_DATA[act]; if(!a) return {stars:3,good:[],warn:[]};
  if(a.goodT.indexOf(p.tNum)>=0){s+=3;good.push(p.tName+' ✓');}
  else if(a.avoidT.indexOf(p.tNum)>=0){s-=3;warn.push(p.tName+' ✗');}
  if(a.goodNK.indexOf(p.nkIdx)>=0){s+=3;good.push(p.nkName+' ✓');}
  else if(a.avoidNK.indexOf(p.nkIdx)>=0){s-=3;warn.push(p.nkName+' ✗');}
  if(a.goodWD.indexOf(p.wd)>=0){s+=2;good.push(WEEKDAY_NAMES[p.wd]+' ✓');}
  else if(a.avoidWD.indexOf(p.wd)>=0){s-=2;warn.push(WEEKDAY_NAMES[p.wd]+' ✗');}
  if(p.yogaBad){s-=2;warn.push(p.yogaName+' ✗');}
  else{s+=1;good.push(p.yogaName+' ✓');}
  if(p.bhadra){s-=2;warn.push('Vishti/Bhadra ✗');}
  var stars=Math.max(1,Math.min(5,Math.round((s+5)/2.5)));
  return {stars,score:s,good,warn};
}

var _muhurtaAct=null;

var ACTIVITY_DATA={
  'Marriage':         {icon:'💍',cat:'Life Events',      goodT:[2,3,5,7,10,11,13],avoidT:[4,6,8,9,12,14,15,30],goodNK:[3,4,6,7,11,12,13,15,20,21,22,23,24,25,26],avoidNK:[1,2,5,8,9,18,19],goodWD:[1,3,4,5],avoidWD:[0,2,6],note:'Avoid Bhadra (Vishti) and inauspicious Yogas. Uttara nakshatras best.'},
  'House Warming':    {icon:'🏡',cat:'Life Events',      goodT:[2,3,5,7,10,11,13],avoidT:[4,8,9,12,14,30],     goodNK:[3,4,6,7,11,12,13,20,21,25,26],          avoidNK:[1,2,5,8,9,18,19],goodWD:[1,3,4,5],avoidWD:[0,2,6],note:'Enter at auspicious Hora. Jupiter or Venus day preferred.'},
  'Naming Ceremony':  {icon:'👶',cat:'Life Events',      goodT:[2,3,5,7,10,11,13],avoidT:[4,6,8,9,12,14,30],   goodNK:[3,4,6,7,12,13,15,20,21,22,25,26],       avoidNK:[1,2,5,8,18,19],  goodWD:[1,3,4,5],avoidWD:[0,2,6],note:'Moon in own or friendly nakshatra is ideal.'},
  'Thread Ceremony':  {icon:'🧵',cat:'Life Events',      goodT:[2,3,5,7,10,11],   avoidT:[4,6,8,9,12,14,30],   goodNK:[3,6,7,11,12,13,20,21,25,26],            avoidNK:[1,2,5,8,9,18],   goodWD:[1,3,4,5],avoidWD:[2,6],  note:'Uttara nakshatras (fixed) are best for sacred rites.'},
  'New Business':     {icon:'🏢',cat:'Business & Finance',goodT:[2,3,5,6,7,10,11,13],avoidT:[4,8,9,12,14,30],  goodNK:[0,3,6,7,11,12,13,20,21,22,25,26],       avoidNK:[1,2,5,8,9,18,19],goodWD:[1,3,4,5],avoidWD:[2,6],  note:'Mercury (Wed) and Jupiter (Thu) days bring prosperity.'},
  'Investment':       {icon:'💰',cat:'Business & Finance',goodT:[2,3,5,6,10,11,13], avoidT:[4,8,9,12,14,30],   goodNK:[3,6,7,11,12,13,20,21,22],               avoidNK:[1,2,5,8,9,18,19],goodWD:[1,3,4,5],avoidWD:[2,6],  note:'Avoid Tuesday and Saturday. Jupiter/Mercury hora recommended.'},
  'Shop Opening':     {icon:'🏪',cat:'Business & Finance',goodT:[2,3,5,7,10,11,13], avoidT:[4,8,9,14,30],       goodNK:[0,3,4,6,7,12,13,20,21,22,25,26],        avoidNK:[1,2,5,8,18,19],  goodWD:[1,3,4,5],avoidWD:[2,6],  note:'Face East or North for the first opening.'},
  'Agreement':        {icon:'📝',cat:'Business & Finance',goodT:[2,3,5,6,7,10,11,13],avoidT:[4,8,9,12,14,30],  goodNK:[0,3,4,6,7,12,13,20,21,22],              avoidNK:[1,2,5,8,9,18,19],goodWD:[1,3,4,5],avoidWD:[2,6],  note:'Mercury (Wed) is the planet of contracts and communication.'},
  'Property Purchase':{icon:'🏠',cat:'Property & Vehicles',goodT:[2,3,5,7,10,11,13],avoidT:[4,8,9,12,14,30],   goodNK:[3,4,6,7,11,12,13,20,21,22,25,26],       avoidNK:[1,2,5,8,9,18,19],goodWD:[1,3,4,5],avoidWD:[0,2,6],note:'Mars and Saturn should not afflict the 4th house lord.'},
  'Vehicle Purchase': {icon:'🚗',cat:'Property & Vehicles',goodT:[2,3,5,7,10,11,13],avoidT:[4,8,9,14,30],       goodNK:[0,3,4,6,7,12,13,20,21,22,25,26],        avoidNK:[1,2,5,8,9,18,19],goodWD:[1,3,4,5],avoidWD:[2,6],  note:'Ashwini nakshatra (divine physicians) is especially auspicious.'},
  'Travel':           {icon:'✈️',cat:'Property & Vehicles',goodT:[2,3,5,7,10,11,13],avoidT:[4,8,9,12,14,30],   goodNK:[0,3,4,6,7,12,13,20,21,22,25,26],        avoidNK:[1,2,5,8,9,18,19],goodWD:[1,3,4,5],avoidWD:[2,6],  note:'Wednesday and Friday are best. Avoid inauspicious Yoga.'},
  'Education / Exam': {icon:'📚',cat:'Education & Health', goodT:[2,3,5,7,10,11,13],avoidT:[4,8,9,12,14,30],   goodNK:[3,4,6,7,11,12,13,20,21,25,26],          avoidNK:[1,2,5,8,18,19],  goodWD:[1,3,4],  avoidWD:[2,6],  note:'Thursday (Jupiter) blesses learning. Pushya nakshatra is best.'},
  'Medical / Surgery':{icon:'🏥',cat:'Education & Health', goodT:[2,3,5,7,10,11,13],avoidT:[4,8,9,12,14,30],   goodNK:[0,3,4,6,7,12,13,20,21],                 avoidNK:[1,2,5,8,9,18,19],goodWD:[1,3,4,5],avoidWD:[0,2,6],note:'Avoid Tuesday and Saturday for surgery. Ashwini (healing) is best.'},
  'Interview / Job':  {icon:'💼',cat:'Education & Health', goodT:[2,3,5,6,7,10,11,13],avoidT:[4,8,9,14,30],    goodNK:[0,3,4,6,7,12,13,20,21,22],              avoidNK:[1,2,5,8,9,18,19],goodWD:[1,3,4,5],avoidWD:[2,6],  note:'Mercury (Wed) for communication. Jupiter (Thu) for senior roles.'},
};

function renderMuhurta(){
  var today=new Date();
  var y=today.getFullYear(),mo=today.getMonth()+1,d=today.getDate();
  var p=calcPanchang(y,mo,d);
  var wd=today.getDay();

  // ── TODAY'S PANCHANG ──────────────────────────────────────
  var panEl=document.getElementById('today-panchang');
  if(panEl){
    var rahuWarn=p.bhadra
      ?'<span style="color:#f87171;font-size:12px;"> ⚠ Bhadra today</span>':''
      +'<span style="color:#f87171;font-size:12px;"> ⚠ Avoid Rahu Kaal</span>';
    panEl.innerHTML=
      '<div class="panchang-row"><span class="panchang-label">VARA (DAY)</span><span class="panchang-val">'+WEEKDAY_NAMES[wd]+' · '+WEEKDAY_LORDS[wd]+' Day</span></div>'+
      '<div class="panchang-row"><span class="panchang-label">TITHI</span><span class="panchang-val">'+p.paksha+' '+p.tName+'</span></div>'+
      '<div class="panchang-row"><span class="panchang-label">NAKSHATRA</span><span class="panchang-val">'+p.nkName+' Pada '+p.nkPada+'</span></div>'+
      '<div class="panchang-row"><span class="panchang-label">YOGA</span><span class="panchang-val" style="color:'+(p.yogaBad?'#f87171':'#86efac')+';">'+p.yogaName+(p.yogaBad?' ⚠':' ✓')+'</span></div>'+
      '<div class="panchang-row"><span class="panchang-label">KARANA</span><span class="panchang-val" style="color:'+(p.bhadra?'#f87171':'inherit')+';">'+p.karName+(p.bhadra?' ⚠ Bhadra':'')+'</span></div>'+
      '<div class="panchang-row"><span class="panchang-label">MOON SIGN</span><span class="panchang-val">'+p.moonSign+'</span></div>'+
      '<div class="panchang-row"><span class="panchang-label">SUN SIGN</span><span class="panchang-val">'+p.sunSign+'</span></div>'+
      '<div class="panchang-row" style="border:none;"><span class="panchang-label">RAHU KAAL</span><span class="panchang-val" style="color:#f87171;">'+p.rahuStr+' IST ⚠</span></div>'+
      '<div class="panchang-row" style="border:none;"><span class="panchang-label">ABHIJIT</span><span class="panchang-val" style="color:#86efac;">11:36–12:24 IST ✓</span></div>';
  }

  // ── 7-DAY GRID ────────────────────────────────────────────
  var weekEl=document.getElementById('muhurta-week');
  if(weekEl){
    var html='';
    for(var i=0;i<7;i++){
      var dt=new Date(today); dt.setDate(today.getDate()+i);
      var pp=calcPanchang(dt.getFullYear(),dt.getMonth()+1,dt.getDate());
      var isToday=i===0;
      var wr=_muhurtaAct?scoreDayForActivity(pp,_muhurtaAct):{stars:pp.yogaBad?2:pp.bhadra?2:3,good:[],warn:[]};
      var stars=wr.stars;
      var dotColor=stars>=4?'#4ade80':stars===3?'#fbbf24':'#f87171';
      var bg=stars>=4?'rgba(74,222,128,0.08)':stars===3?'rgba(251,191,36,0.07)':'rgba(248,113,113,0.06)';
      var bc=stars>=4?'rgba(74,222,128,0.35)':stars===3?'rgba(251,191,36,0.3)':'rgba(248,113,113,0.25)';
      var mon=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][dt.getMonth()];
      html+='<div class="muhurta-day'+(isToday?' today':'')+'" onclick="selectMuhurtaDayV2('+i+')" style="background:'+bg+';border-color:'+bc+';cursor:pointer;">'+
        '<div style="font-size:11px;color:var(--dim);letter-spacing:0.06em;">'+WEEKDAY_NAMES[pp.wd].slice(0,3).toUpperCase()+'</div>'+
        '<div class="muhurta-date-num" style="color:'+dotColor+';">'+dt.getDate()+'</div>'+
        '<div style="font-size:11px;color:var(--dim);margin-bottom:3px;">'+mon+'</div>'+
        '<div style="font-size:12px;color:'+dotColor+';letter-spacing:0;">'+'★'.repeat(stars)+'</div>'+
        '<div style="font-size:10px;color:var(--muted);margin-top:2px;">'+pp.tName.slice(0,6)+'</div>'+
        '<div style="font-size:10px;color:var(--dim);">'+NAKSH[pp.nkIdx].slice(0,6)+'</div>'+
        (isToday?'<div style="font-size:8px;color:var(--gold);margin-top:2px;letter-spacing:0.1em;">TODAY</div>':'')+
        '</div>';
    }
    weekEl.innerHTML=html;
  }

  // ── ACTIVITY BUTTONS — grouped by category ────────────────
  var actEl=document.getElementById('muhurta-activity-btns');
  if(actEl){
    var cats={};
    Object.keys(ACTIVITY_DATA).forEach(function(k){
      var c=ACTIVITY_DATA[k].cat;
      if(!cats[c]) cats[c]=[];
      cats[c].push(k);
    });
    var html='';
    Object.keys(cats).forEach(function(cat){
      html+='<div style="width:100%;font-size:11px;color:var(--muted);letter-spacing:0.15em;margin:8px 0 4px;font-family:Cormorant SC,serif;">'+cat.toUpperCase()+'</div>';
      cats[cat].forEach(function(k){
        var a=ACTIVITY_DATA[k];
        html+='<button class="picker-btn empty" style="flex:0 0 auto;padding:7px 13px;font-size:13px;" onclick="selectMuhurtaActivity(&apos;'+k+'&apos;)">'+a.icon+' '+k+'</button>';
      });
    });
    actEl.innerHTML=html;
  }
}

function selectMuhurtaDayV2(offset){
  var today=new Date(); today.setDate(today.getDate()+offset);
  var p=calcPanchang(today.getFullYear(),today.getMonth()+1,today.getDate());
  var advEl=document.getElementById('muhurta-advice');
  if(!advEl) return;
  var actScore=_muhurtaAct?scoreDayForActivity(p,_muhurtaAct):null;
  var stars=actScore?actScore.stars:(p.yogaBad?2:3);
  var dotColor=stars>=4?'#86efac':stars===3?'#fbbf24':'#f87171';
  var html='<div style="text-align:left;">';
  html+='<div style="font-family:Cinzel,serif;font-size:14px;color:var(--gold);margin-bottom:12px;">'+WEEKDAY_NAMES[p.wd]+' '+today.getDate()+' '+['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][today.getMonth()]+'</div>';
  html+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px;">';
  html+='<div><span style="font-size:12px;color:var(--muted);">TITHI</span><div style="font-size:14px;color:var(--text);">'+p.paksha+' '+p.tName+'</div></div>';
  html+='<div><span style="font-size:12px;color:var(--muted);">NAKSHATRA</span><div style="font-size:14px;color:var(--text);">'+p.nkName+' Pada '+p.nkPada+'</div></div>';
  html+='<div><span style="font-size:12px;color:var(--muted);">YOGA</span><div style="font-size:14px;color:'+(p.yogaBad?'#f87171':'#86efac')+';">'+p.yogaName+(p.yogaBad?' ⚠':' ✓')+'</div></div>';
  html+='<div><span style="font-size:12px;color:var(--muted);">KARANA</span><div style="font-size:14px;color:'+(p.bhadra?'#f87171':'var(--text)')+';">'+p.karName+(p.bhadra?' ⚠ Bhadra':'')+'</div></div>';
  html+='</div>';
  html+='<div style="background:rgba(248,113,113,0.08);border:1px solid rgba(248,113,113,0.2);border-radius:8px;padding:8px 12px;font-size:13px;color:#f87171;margin-bottom:10px;">⚠ Rahu Kaal: '+p.rahuStr+' IST — avoid for new beginnings</div>';
  html+='<div style="background:rgba(134,239,172,0.08);border:1px solid rgba(134,239,172,0.2);border-radius:8px;padding:8px 12px;font-size:13px;color:#86efac;margin-bottom:10px;">✓ Abhijit Muhurta: 11:36–12:24 IST — always auspicious</div>';
  if(actScore){
    html+='<div style="font-family:Cinzel,serif;font-size:13px;color:'+dotColor+';margin:10px 0 6px;">'+(_muhurtaAct||'')+' — '+'★'.repeat(stars)+'☆'.repeat(5-stars)+'</div>';
    if(actScore.good.length) html+='<div style="color:#86efac;font-size:13px;margin-bottom:4px;">✓ '+actScore.good.join(' · ')+'</div>';
    if(actScore.warn.length) html+='<div style="color:#f87171;font-size:13px;margin-bottom:4px;">✗ '+actScore.warn.join(' · ')+'</div>';
    html+='<div style="font-size:13px;color:var(--muted);margin-top:6px;font-style:italic;">'+ACTIVITY_DATA[_muhurtaAct].note+'</div>';
  }
  html+='</div>';
  advEl.innerHTML=html;
}

function selectMuhurtaActivity(act){
  _muhurtaAct=act;
  // Highlight selected button
  document.querySelectorAll('#muhurta-activity-btns button').forEach(function(b){
    var isActive=b.textContent.trim().indexOf(act)>=0;
    b.classList.toggle('filled',isActive);
    b.classList.toggle('empty',!isActive);
  });
  // Re-render 7-day grid with scores for this activity
  renderMuhurta();
  // Show best days summary
  var today=new Date();
  var bestDays=[],goodDays=[],avoidDays=[];
  for(var i=0;i<7;i++){
    var dt=new Date(today); dt.setDate(today.getDate()+i);
    var pp=calcPanchang(dt.getFullYear(),dt.getMonth()+1,dt.getDate());
    var sc=scoreDayForActivity(pp,act);
    var label=WEEKDAY_NAMES[pp.wd].slice(0,3)+' '+dt.getDate();
    if(sc.stars>=4) bestDays.push(label);
    else if(sc.stars===3) goodDays.push(label);
    else avoidDays.push(label);
  }
  var html='<div style="text-align:left;">';
  html+='<div style="font-family:Cinzel,serif;font-size:13px;color:var(--gold);margin-bottom:10px;">'+ACTIVITY_DATA[act].icon+' '+act+' — Next 7 Days</div>';
  if(bestDays.length) html+='<div style="margin-bottom:6px;"><span style="color:#4ade80;font-size:13px;">★★★★★ EXCELLENT: </span>'+bestDays.join(' · ')+'</div>';
  if(goodDays.length) html+='<div style="margin-bottom:6px;"><span style="color:#fbbf24;font-size:13px;">★★★ GOOD: </span>'+goodDays.join(' · ')+'</div>';
  if(avoidDays.length) html+='<div style="margin-bottom:6px;"><span style="color:#f87171;font-size:13px;">✗ AVOID: </span>'+avoidDays.join(' · ')+'</div>';
  html+='<div style="margin-top:10px;font-size:13px;color:var(--muted);font-style:italic;">'+ACTIVITY_DATA[act].note+'</div>';
  html+='<div style="margin-top:8px;font-size:12px;color:var(--dim);">Click a day above for full Panchang details.</div>';
  html+='</div>';
  document.getElementById('muhurta-advice').innerHTML=html;
}

function selectMuhurtaDay(offset,wd){ selectMuhurtaDayV2(offset); }


// ════════════════════════════════════════════════════════════════
// INIT — render dream log and muhurta on page load
// ════════════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded',()=>{
  renderDreamLog();
  renderMuhurta();
});


