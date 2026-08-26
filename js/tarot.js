// ============================================================
// tarot.js
// ============================================================

function selectSpread(s){
  currentSpread=s;
  document.querySelectorAll('.spread-tab').forEach(t=>t.classList.remove('active'));
  document.querySelector(`[data-spread="${s}"]`).classList.add('active');
  document.getElementById('cards-display').innerHTML='';
  document.getElementById('card-meaning-panel').className='card-meaning-panel';
}

function getCardName(raw){
  return raw.replace(/_/g,' ').replace(/^\d+ /,'');
}

function cardImgFail(img){
  var wrap=img.closest('.card-img-wrap');
  var name=img.alt||'';
  if(wrap){wrap.innerHTML='<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:10px;padding:12px;text-align:center;"><div style="font-size:44px;opacity:0.4;">🔮</div><div style="font-family:Cinzel,serif;font-size:13px;letter-spacing:0.1em;color:var(--muted);opacity:0.7;">'+name+'</div><div style="font-size:14px;color:var(--dim);opacity:0.6;">Add cards/ folder<br>to repo</div></div>';}
}
function drawCards(){
  const spread=SPREAD_TYPES[currentSpread];
  const btn=document.getElementById('draw-btn');
  const display=document.getElementById('cards-display');
  const panel=document.getElementById('card-meaning-panel');
  
  btn.disabled=true;
  display.innerHTML='<div class="loading-ring"></div>';
  panel.className='card-meaning-panel';
  
  // Draw cards immediately
  const shuffled=[...TAROT_CARDS].sort(()=>Math.random()-0.5);
  const drawn=shuffled.slice(0,spread.cards).map((card,i)=>{
    const isReversed=Math.random()<0.35;
    return {...card,reversed:isReversed,position:spread.positions[i]};
  });
    
    // Show cards with shimmer placeholder immediately, load images in background
    display.innerHTML=drawn.map((card,i)=>`
      <div class="card-slot" onclick="showCardMeaning(${i})">
        <div class="card-slot-label">${card.position}</div>
        <div class="card-frame">
          <div class="card-img-wrap" id="cw-${i}" style="position:relative;">
            <div class="card-shimmer" id="shimmer-${i}"></div>
            <img 
              src=""
              data-src="cards/${card.name}.jpg"
              class="${card.reversed?'reversed':''}"
              alt="${getCardName(card.name)}"
              width="160" height="280"
              style="opacity:0;transition:opacity 0.35s;position:relative;z-index:1;"
              onload="this.style.opacity='1';const sh=document.getElementById('shimmer-'+${i});if(sh)sh.remove();"
              onerror="cardImgFail(this);const sh=document.getElementById('shimmer-'+${i});if(sh)sh.remove();"
            >
          </div>
          <div class="card-name-bar">
            <span class="card-name">${getCardName(card.name)}</span>
            <span class="card-orient ${card.reversed?'reversed':'upright'}">${card.reversed?'🔄 Reversed':'↑ Upright'}</span>
          </div>
        </div>
      </div>
    `).join('');
    
    window._drawnCards=drawn;

    // Load ALL card images in parallel immediately (HTTP/2 handles concurrency)
    // Staggering was actually SLOWER — it serialized parallel loads
    drawn.forEach((card,i)=>{
      const wrap=document.getElementById('cw-'+i);
      if(!wrap) return;
      const img=wrap.querySelector('img[data-src]');
      if(img){
        img.decoding='async';
        img.src=img.dataset.src;
        img.removeAttribute('data-src');
      }
    });

    const question=(document.getElementById('tarot-question')?document.getElementById('tarot-question').value.trim():'');
    
    // ── For multi-card spreads: show overview, not first card detail ──
    if(drawn.length===1){
      showCardMeaning(0);
    } else {
      showSpreadOverview(drawn, question);
    }
    
    // ── Get AI interpretation of the question + cards ──
    if(question){
      getAITarotInsight(drawn, question, currentSpread);
    }
    
    // ── Log every tarot reading ──
    saveLog({
      type:'tarot',
      spread:(SPREAD_TYPES[currentSpread]?SPREAD_TYPES[currentSpread].name:currentSpread)||currentSpread,
      cards:drawn.map(c=>c.name+(c.reversed?' (Rev)':'')).join(' | '),
      question:question||'—'
    });
    
  btn.disabled=false;
  btn.textContent='✨ Draw Again';
}


// ── Show spread overview (all cards, none expanded) for multi-card spreads ──
function showSpreadOverview(cards, question){
  const panel=document.getElementById('card-meaning-panel');
  // Reset all card highlights
  document.querySelectorAll('.card-slot').forEach(el=>{
    el.style.opacity='1';el.style.transform='scale(1)';
  });
  
  let html='';
  // Question display
  if(question){
    html+=`<div style="background:rgba(255,195,64,0.06);border:1px solid rgba(255,195,64,0.15);border-radius:10px;padding:12px 16px;margin-bottom:16px;">
      <div style="font-size:13px;letter-spacing:0.12em;color:var(--muted);margin-bottom:4px;">YOUR QUESTION</div>
      <div style="font-family:'Cormorant Garamond',serif;font-size:16px;color:var(--text);font-style:italic;">"${question}"</div>
      <div id="ai-tarot-insight"><span class="jyogi-loading">✦ Jyogi is reading your cards…</span></div>
    </div>`;
  }
  
  // All cards summary — tap any to expand
  html+=`<div style="font-size:13px;letter-spacing:0.15em;color:var(--muted);margin-bottom:12px;">✦ TAP ANY CARD TO SEE ITS MEANING</div>`;
  cards.forEach((c,i)=>{
    html+=`<div onclick="showCardMeaning(${i})" style="cursor:pointer;padding:14px 16px;border-radius:12px;margin-bottom:8px;
      background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);
      display:flex;align-items:center;gap:14px;transition:all 0.2s;"
      onmouseover="this.style.background='rgba(255,195,64,0.07)';this.style.borderColor='rgba(255,195,64,0.3)'"
      onmouseout="this.style.background='rgba(255,255,255,0.03)';this.style.borderColor='rgba(255,255,255,0.08)'">
      <div style="flex-shrink:0;text-align:center;min-width:60px;">
        <div style="font-size:12px;letter-spacing:0.12em;color:var(--muted);margin-bottom:4px;">${c.position.toUpperCase()}</div>
        <div style="font-size:13px;color:${c.reversed?'#f87171':'var(--green-lt)'};">${c.reversed?'🔄 Rev':'↑ Up'}</div>
      </div>
      <div style="flex:1;min-width:0;">
        <div style="font-family:'Cinzel',serif;color:var(--gold);font-size:13px;margin-bottom:4px;">${getCardName(c.name)}</div>
        <div style="font-size:14px;color:var(--muted);line-height:1.5;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;">${c.reversed?c.shadow:c.meaning}</div>
      </div>
      <div style="color:var(--dim);font-size:18px;flex-shrink:0;">›</div>
    </div>`;
  });
  
  panel.innerHTML=html;
  panel.className='card-meaning-panel visible';
  panel.scrollIntoView({behavior:'smooth',block:'nearest'});
}

// ── Get AI interpretation of question + drawn cards ──
async function getAITarotInsight(cards, question, spreadType){
  const insightEl=document.getElementById('ai-tarot-insight');
  if(!insightEl) return;
  
  const spreadName=(SPREAD_TYPES[spreadType]?SPREAD_TYPES[spreadType].name:spreadType)||spreadType;
  const cardList=cards.map(c=>`${c.position}: ${getCardName(c.name)} (${c.reversed?'Reversed':'Upright'}) — ${(c.reversed?c.shadow:c.meaning).substring(0,80)}`).join('; ');
  
  // Send card names only (not full meanings) — prevents AI repeating what's already shown
  const cardNames=cards.map(c=>`${c.position}: ${getCardName(c.name)} (${c.reversed?'Reversed':'Upright'})`).join(', ');
  const prompt = question
    ? `USER QUESTION: "${question}"

CARDS DRAWN: ${cardNames}
SPREAD: ${spreadName}

INSTRUCTION: You are Jyogi, an intuitive tarot reader. Answer the USER QUESTION directly using these cards as your guide. Speak in second person. Be specific to their question — not generic spiritual advice. Keep it to 3-4 warm, personal sentences. End with one clear action or guidance.`
    : `CARDS DRAWN: ${cardNames}
SPREAD: ${spreadName}

INSTRUCTION: You are Jyogi. Give a warm 3-sentence energy reading of this spread. What energy is present? What should this person be aware of? Be poetic but grounded.`;

  try{
    const controller=new AbortController();
    const timeout=setTimeout(()=>controller.abort(),35000);
    const resp=await fetch('https://jyogi-api.onrender.com/api/insight',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({prompt}),
      signal:controller.signal
    });
    clearTimeout(timeout);
    if(resp.ok){
      const data=await resp.json();
      const text=data.insight||data.text||data.message||'';
      if(text&&insightEl){
        insightEl.innerHTML='<span style="color:var(--gold);font-size:13px;letter-spacing:0.1em;">✦ JYOGI READS YOUR CARDS</span><br><br>'
          +'<span style="font-size:17px;line-height:1.8;font-style:italic;">'+text+'</span>';
        insightEl.style.color='var(--text)';
        insightEl.classList.remove('jyogi-loading');
      }
    } else {
      const errData=await resp.json().catch(()=>({}));
      // FastAPI returns {detail:"..."}, OpenAI errors return {error:{message:"..."}}
      const errMsg = (errData&&errData.detail)||(errData&&errData.error&&errData.error.message) || ('Server error '+resp.status);
      if(insightEl){
        if(resp.status===401){
          insightEl.innerHTML='<span style="color:#f87171;">🔑 OpenAI key invalid — update OPENAI_API_KEY in Render dashboard.</span>';
        } else if(resp.status===500){
          // Server has old code — show local card meaning as fallback
          const localFallback=cards.map(c=>(c.reversed?c.shadow:c.meaning)).join(' • ');
          insightEl.innerHTML='<span style="color:#fbbf24;font-size:13px;">⚠️ AI server needs update — showing card meanings:</span><br><br>'
            +'<span style="font-style:italic;color:var(--muted);">'+localFallback.substring(0,300)+'</span>';
        } else {
          insightEl.innerHTML='<span style="color:#f87171;">⚠️ '+errMsg+'</span>';
        }
        insightEl.classList.remove('jyogi-loading');
      }
    }
  }catch(e){
    if(insightEl){
      const msg=e.name==='AbortError'
        ? '⏱️ Jyogi AI is waking up — try drawing again in 30 seconds'
        : '✦ '+cards.map(c=>c.reversed?c.shadow:c.meaning).slice(0,2).join(' · ');
      insightEl.innerHTML=msg;
      insightEl.style.fontStyle='italic';
      insightEl.classList.remove('jyogi-loading');
    }
  }
}

function showCardMeaning(idx){
  const cards=window._drawnCards;
  if(!cards||!cards[idx]) return;
  const panel=document.getElementById('card-meaning-panel');

  // Build interpretation for all cards if multi-spread
  const isSingle=cards.length===1;

  // Single selected card detail
  const card=cards[idx];
  // Highlight active card
  document.querySelectorAll('.card-slot').forEach((el,i)=>{
    el.style.opacity=(i===idx)?'1':'0.6';
    el.style.transform=(i===idx)?'scale(1.03)':'scale(1)';
  });
  const question=(document.getElementById('tarot-question')?document.getElementById('tarot-question').value.trim():'');
  let html=`
    ${!isSingle?`<button onclick="showSpreadOverview(window._drawnCards,'${question.replace(/'/,"\'")}')" style="margin-bottom:16px;background:transparent;border:1px solid rgba(255,195,64,0.2);color:var(--muted);border-radius:20px;padding:7px 16px;font-family:inherit;font-size:13px;cursor:pointer;display:inline-flex;align-items:center;gap:6px;">‹ All Cards</button>`:''}
    <div class="cmp-card-name">${getCardName(card.name)}</div>
    <div style="margin-bottom:10px;">
      <span class="cmp-orient-badge ${card.reversed?'reversed':'upright'}">${card.reversed?'🔄 Reversed — Shadow Energy':'✦ Upright — Radiant Energy'}</span>
      ${card.position && !isSingle ? `<span style="font-size:13px;letter-spacing:0.12em;color:var(--muted);margin-left:10px;">POSITION: ${card.position.toUpperCase()}</span>` : ''}
    </div>
    <p class="cmp-meaning">${card.reversed?card.shadow:card.meaning}</p>
    <div class="cmp-affirmation">"${card.affirmation}"</div>
  `;
  // Add AI insight div for single card with question
  if(isSingle && question){
    html += '<div id="ai-tarot-insight" style="margin-top:16px;padding:14px;background:rgba(255,195,64,0.05);border:1px solid rgba(255,195,64,0.12);border-radius:10px;"><span class=\"jyogi-loading\">✦ Jyogi is reading your cards…</span></div>';
    setTimeout(()=>getAITarotInsight(cards, question, currentSpread), 50);
  }

  // If multi-card spread: show all cards summary below
  if(!isSingle){
    html+=`<div style="border-top:1px solid rgba(255,195,64,0.15);margin-top:20px;padding-top:16px;">
      <div style="font-size:14px;letter-spacing:0.18em;color:var(--muted);margin-bottom:14px;">✦ ALL CARDS IN YOUR SPREAD ✦</div>`;
    cards.forEach((c,i)=>{
      const isActive=i===idx;
      html+=`
        <div onclick="showCardMeaning(${i})" style="cursor:pointer;padding:12px 14px;border-radius:10px;margin-bottom:8px;
          background:${isActive?'rgba(255,195,64,0.1)':'rgba(255,255,255,0.03)'};
          border:1px solid ${isActive?'rgba(255,195,64,0.4)':'rgba(255,255,255,0.07)'};
          transition:all 0.2s;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
            <span style="font-size:14px;letter-spacing:0.14em;color:var(--muted);">${c.position.toUpperCase()}</span>
            <span style="font-size:14px;color:${c.reversed?'#f87171':'var(--green-lt)'};">${c.reversed?'🔄 Reversed':'↑ Upright'}</span>
          </div>
          <div style="font-family:'Cinzel',serif;color:${isActive?'var(--gold)':'var(--text)'};font-size:13px;margin-bottom:5px;">${getCardName(c.name)}</div>
          <p style="font-size:14px;color:var(--muted);line-height:1.6;margin:0;">
            ${(c.reversed?c.shadow:c.meaning).substring(0,100)}…
          </p>
        </div>`;
    });
    html+=`</div>`;
  }

  panel.innerHTML=html;
  panel.className='card-meaning-panel visible';
  panel.scrollIntoView({behavior:'smooth',block:'nearest'});
}

// ─── ASTROLOGY ────────────────────────────────────────────────────────────
function waBookingLink(name,dob,city,question){
  const msg=`Hi Jyogi! I would like a full Vedic chart reading.\nName: ${name}\nDOB: ${dob}\nCity: ${city}${question?'\nQuestion: '+question:''}`;
  return `https://wa.me/${WA_NUMBER}?text=${encodeURIComponent(msg)}`;
}

// ════════════════════════════════════════════════════════════════
// ✦ ACCESS CODE CONFIGURATION — edit this block to customise
// ════════════════════════════════════════════════════════════════
var ACCESS_CONFIG = {

  // ── HOW CODES WORK ──────────────────────────────────────────
  // 'admin'   → only admin password unlocks full reading (current)
  // 'code'    → unique codes you send to each client
  // 'open'    → full reading for everyone, no code needed
  mode: 'open',   // Full chart visible to all — booking CTAs drive conversions

  // ── VALID ACCESS CODES ───────────────────────────────────────
  // Add or remove codes here. Each code can have metadata.
  // Future: expiry dates, one-time use flags, client names etc.
  codes: {
    // 'JYOGI-ABC123': { label: 'Client name', expires: null, used: false },
    // 'STAR-XYZ789':  { label: 'Priya session', expires: '2026-04-01', used: false },
  },

  // ── WHAT FULL READING SHOWS ──────────────────────────────────
  // Toggle sections on/off without touching any other code
  fullReading: {
    planetaryPositions : true,   // All 9 grahas with house & sign
    houseAnalysis      : true,   // 12 house breakdown
    antardasha         : true,   // Sub-period (Antardasha) detail
    sadheSati          : true,   // Saturn 7.5 year cycle check
    remedies           : true,   // Mantras & gemstone suggestions
    compatibility      : false,  // Relationship compatibility (future)
  },

  // ── UI TEXT ─────────────────────────────────────────────────
  // Change button labels, locked section text etc. here
  ui: {
    previewTitle     : 'Vedic Preview',
    lockedLabel      : '🔒 Full Reading',
    lockedDesc       : 'Includes: all planetary positions · 12 house analysis · Antardasha · Sadhe Sati · remedies & mantras',
    codePlaceholder  : 'Enter your access code',
    codeButtonLabel  : '✦ Unlock Full Reading',
    waButtonLabel    : '💬 Get Full Reading on WhatsApp',
    wrongCodeMsg     : 'Invalid access code. Please check and try again.',
    successMsg       : '✦ Full Reading Unlocked',
  },
};
// ════════════════════════════════════════════════════════════════

// Validate an access code against config
function validateCode(code) {
  const trimmed = (code||'').trim().toUpperCase();
  // Admin password always works
  if (trimmed === ADMIN_PASS.toUpperCase()) return { valid: true, isAdmin: true };
  // Check registered codes
  const entry = ACCESS_CONFIG.codes[trimmed] || ACCESS_CONFIG.codes[code.trim()];
  if (!entry) return { valid: false };
  // Future: check expiry, one-time use etc.
  // if (entry.expires && new Date() > new Date(entry.expires)) return { valid: false, reason: 'expired' };
  return { valid: true, isAdmin: false, label: entry.label };
}

// Build full reading HTML from chart data
function buildFullReadingHTML(name, chart) {
  const cfg = ACCESS_CONFIG.fullReading;
  const c = chart;

  function getPlanetaryPositions() {
    const P   = c.planets;
    const R   = c.retrograde || {};
    const rows = [
      ['☉ Sun',     'Sun',     P.Sun],
      ['☽ Moon',    'Moon',    P.Moon],
      ['♂ Mars',    'Mars',    P.Mars],
      ['☿ Mercury', 'Mercury', P.Mercury],
      ['♃ Jupiter', 'Jupiter', P.Jupiter],
      ['♀ Venus',   'Venus',   P.Venus],
      ['♄ Saturn',  'Saturn',  P.Saturn],
      ['☊ Rahu',    'Rahu',    P.Rahu],
      ['☋ Ketu',    'Ketu',    P.Ketu],
    ];
    return rows.map(([n,key,lon])=>{
      const isR = R[key];
      const deg = (lon%30).toFixed(1);
      const vakriCell = isR
        ? `<td style="padding:6px 10px;"><span style="color:#f87171;font-family:'Cormorant SC',serif;font-size:12px;letter-spacing:0.1em;background:rgba(248,113,113,0.1);border:1px solid rgba(248,113,113,0.25);border-radius:6px;padding:2px 8px;">ℛ Vakri</span></td>`
        : `<td style="padding:6px 10px;color:var(--dim);font-size:12px;">—</td>`;
      const nameStyle = isR
        ? `color:#FFC340;font-style:italic;`
        : `color:var(--gold);`;
      return `<tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
        <td style="padding:6px 10px;${nameStyle}">${n}</td>
        <td style="padding:6px 10px;">${RASHIS[Math.floor(lon/30)]}</td>
        <td style="padding:6px 10px;color:var(--muted);font-size:13px;">${deg}°</td>
        ${vakriCell}
      </tr>`;
    }).join('');
  }

  function getAntardashaTable() {
    const idx = c.dasha.lordIdx;
    const total = DASHA_YRS[idx];
    return DASHA_SEQ.map((sub,i)=>{
      const ai=mod(idx+i,9);
      const yrs=(total*DASHA_YRS[ai]/120).toFixed(2);
      const cur=DASHA_SEQ[ai]===c.dasha.antardasha;
      return `<tr style="${cur?'background:rgba(255,195,64,0.08);':''}">
        <td style="padding:6px 10px;color:var(--gold);">${c.dasha.current}</td>
        <td style="padding:6px 10px;${cur?'color:var(--gold-lt);font-weight:bold;':''}">${DASHA_SEQ[ai]}${cur?' ◀':''}</td>
        <td style="padding:6px 10px;color:var(--muted);font-size:13px;">${yrs} yrs</td></tr>`;
    }).join('');
  }

  function getSaturnTransits() {
    const moonIdx = RASHIS.indexOf(c.moon);
    const satIdx  = RASHIS.indexOf(SATURN_NOW);
    const diff    = mod(satIdx-moonIdx,12);
    const isSS    = diff===11||diff===0||diff===1;
    const isDh4   = diff===3;
    const isDh8   = diff===7;
    const isKant  = diff===3||diff===6||diff===7||diff===9;
    let html=`<div style="font-size:13px;color:var(--muted);margin-bottom:10px;">
      Saturn in <strong style="color:var(--gold)">${SATURN_NOW}</strong> ·
      Your Moon in <strong style="color:var(--gold)">${c.moon}</strong> ·
      ${diff+1}th position from Moon</div>`;
    if(isSS){
      const phase=diff===11?'Rising Phase (12th from Moon)':diff===0?'Peak Phase (1st from Moon)':'Setting Phase (2nd from Moon)';
      html+=`<div style="background:rgba(248,113,113,0.1);border:1px solid rgba(248,113,113,0.35);border-radius:10px;padding:14px;margin-bottom:8px;">
        <div style="color:#f87171;font-weight:bold;margin-bottom:6px;">⚠ SADHE SATI ACTIVE — ${phase}</div>
        <p style="font-size:13px;line-height:1.7;">This 7.5-year Saturn cycle demands patience and inner work. Avoid major new ventures. Focus on spiritual practice.
        Recite <em>Om Sham Shanicharaya Namah</em> 108x every Saturday. Donate sesame and oil on Saturdays.</p></div>`;
    } else {
      html+=`<div style="background:rgba(134,239,172,0.07);border:1px solid rgba(134,239,172,0.2);border-radius:10px;padding:10px;margin-bottom:8px;">
        <div style="color:var(--green-lt);">✓ Sadhe Sati — Not Active</div></div>`;
    }
    if(isDh4||isDh8){
      html+=`<div style="background:rgba(251,191,36,0.08);border:1px solid rgba(251,191,36,0.25);border-radius:10px;padding:14px;margin-bottom:8px;">
        <div style="color:#fbbf24;font-weight:bold;margin-bottom:6px;">⚡ SHANI DHAIYA — ${isDh4?'4th':'8th'} from Moon</div>
        <p style="font-size:13px;line-height:1.7;">A 2.5-year period of Saturn pressure. Health and relationships need extra care.
        Offer blue flowers to Shani Dev on Saturdays.</p></div>`;
    }
    if(isKant&&!isSS){
      const pos=diff===3?'4th':diff===6?'7th':diff===7?'8th':'10th';
      html+=`<div style="background:rgba(167,139,250,0.08);border:1px solid rgba(167,139,250,0.2);border-radius:10px;padding:14px;margin-bottom:8px;">
        <div style="color:var(--violet);font-weight:bold;margin-bottom:6px;">🔱 KANTAKA SHANI — ${pos} from Moon</div>
        <p style="font-size:13px;line-height:1.7;">Kantaka Shani brings obstacles in areas of the ${pos} house. Stay grounded.
        Recite Hanuman Chalisa on Saturdays.</p></div>`;
    }
    if(!isSS&&!isDh4&&!isDh8&&!isKant){
      html+=`<div style="background:rgba(134,239,172,0.07);border:1px solid rgba(134,239,172,0.2);border-radius:10px;padding:10px;">
        <div style="color:var(--green-lt);">✓ No major Saturn affliction active currently.</div></div>`;
    }
    return html;
  }

  const NAKSH_TRAITS = {
    'Ashwini':{q:'Healing and Swift Action',d:'Freedom and independence',s:'Quick decisions, natural healer, pioneering spirit',w:'Impatience, difficulty completing things'},
    'Bharani':{q:'Transformation and Intensity',d:'Deep creative expression',s:'Determined, creative, powerful will',w:'Possessiveness, extreme tendencies'},
    'Krittika':{q:'Purification and Sharpness',d:'Honour and recognition',s:'Courageous, disciplined, sharp intellect',w:'Sharp tongue, overly critical'},
    'Rohini':{q:'Abundance and Beauty',d:'Beauty, love and material comfort',s:'Artistic, magnetic, excellent communicator',w:'Stubbornness, possessiveness'},
    'Mrigashira':{q:'Searching and Curiosity',d:'Knowledge and new experiences',s:'Gentle, curious, excellent researcher',w:'Restlessness, indecisiveness'},
    'Ardra':{q:'Storms and Transformation',d:'Deep understanding and truth',s:'Penetrating mind, transformative power',w:'Destructive impulses, emotional storms'},
    'Punarvasu':{q:'Return and Renewal',d:'Security, comfort and home',s:'Resilient, optimistic, philosophical',w:'Complacency, repeating mistakes'},
    'Pushya':{q:'Nourishment and Protection',d:'To nurture and be nurtured',s:'Caring, responsible, spiritual strength',w:'Over-protective, overly conservative'},
    'Ashlesha':{q:'Serpent Wisdom and Mysticism',d:'Hidden knowledge and power',s:'Psychic ability, strategic mind, healing',w:'Manipulative tendencies, secrecy'},
    'Magha':{q:'Royal Authority and Ancestors',d:'Power, respect and legacy',s:'Leadership, pride, strong ancestral connection',w:'Arrogance, living in the past'},
    'Purva Phalguni':{q:'Pleasure and Creativity',d:'Love, beauty and pleasure',s:'Creative, charming, artistic talent',w:'Laziness, self-indulgence'},
    'Uttara Phalguni':{q:'Patronage and Service',d:'Partnership and social contribution',s:'Generous, reliable, social leadership',w:'Dependent on others approval'},
    'Hasta':{q:'Skill and Craftsmanship',d:'Mastery and practical achievement',s:'Dexterous, witty, excellent at crafts',w:'Nervous energy, overcritical'},
    'Chitra':{q:'Brilliance and Artistry',d:'Beauty, perfection and admiration',s:'Visually gifted, stylish, magnetic',w:'Vanity, need for constant attention'},
    'Swati':{q:'Independence and Flexibility',d:'Freedom and self-determination',s:'Diplomatic, adaptable, business-minded',w:'Indecision, scattered energy'},
    'Vishakha':{q:'Purpose and Achievement',d:'Achievement of goals',s:'Goal-oriented, persuasive, purposeful',w:'Jealousy, fanaticism'},
    'Anuradha':{q:'Devotion and Friendship',d:'Deep friendship and spiritual connection',s:'Loyal, spiritual, excellent organiser',w:'Suppressed feelings, intensity'},
    'Jyeshtha':{q:'Seniority and Protection',d:'Power, recognition and respect',s:'Protective, courageous, intelligent leader',w:'Domineering, jealousy'},
    'Mula':{q:'Root and Dissolution',d:'Truth and the roots of existence',s:'Philosophical, powerful research mind',w:'Destructive tendencies, restlessness'},
    'Purva Ashadha':{q:'Invincibility and Purification',d:'Victory and vindication',s:'Proud, strong convictions, enduring',w:'Stubborn, pride before fall'},
    'Uttara Ashadha':{q:'Universal Victory',d:'Lasting achievement and virtue',s:'Righteous, ambitious, determined',w:'Inflexible, workaholic'},
    'Shravana':{q:'Listening and Learning',d:'Knowledge and tradition',s:'Wise, learned, excellent listener',w:'Gossip, oversensitive to criticism'},
    'Dhanishtha':{q:'Wealth and Rhythm',d:'Wealth, music and fame',s:'Musical talent, generous, ambitious',w:'Marital friction, overconfidence'},
    'Shatabhisha':{q:'Healing and Mystery',d:'Hidden knowledge and healing',s:'Original thinker, healer, independent',w:'Reclusive, secretive, harsh'},
    'Purva Bhadrapada':{q:'Fiery Transformation',d:'Spiritual liberation',s:'Passionate, visionary, intense focus',w:'Anxiety, extremism'},
    'Uttara Bhadrapada':{q:'Depth and Wisdom',d:'Spiritual depth and moksha',s:'Wise, compassionate, excellent teacher',w:'Lazy, procrastination'},
    'Revati':{q:'Journey and Completion',d:'Love, spiritual journey and guidance',s:'Nurturing, spiritual, excellent guide',w:'Over-sensitive, unworldly'},
  };
  const MOON_HIDDEN = {
    'Aries'     :{inner:'Secret desire to lead and be first. Hides vulnerability behind boldness.',hidden:'Craves admiration but fears being seen as weak.'},
    'Taurus'    :{inner:'Deep need for security and sensory beauty. Hides stubbornness behind calm.',hidden:'Secret desire for luxury and permanence.'},
    'Gemini'    :{inner:'Constant internal dialogue. Hides restlessness behind cheerfulness.',hidden:'Fears being truly known — reveals different faces to different people.'},
    'Cancer'    :{inner:'Deeply emotional interior life. Hides sensitivity behind caring for others.',hidden:'Secret desire to be completely protected and cherished.'},
    'Leo'       :{inner:'Burning need for recognition. Hides insecurity behind grand gestures.',hidden:'Fears being ordinary more than anything else.'},
    'Virgo'     :{inner:'Analytical mind that never stops. Hides anxiety behind helpfulness.',hidden:'Secret perfectionist who fears failure deeply.'},
    'Libra'     :{inner:'Constant weighing of every option. Hides indecision behind grace.',hidden:'Deeply craves harmonious relationship but fears dependency.'},
    'Scorpio'   :{inner:'Volcanic emotional depth. Hides intensity behind a calm surface.',hidden:'Desires total merger with another and fears betrayal above all.'},
    'Sagittarius':{inner:'Restless philosophical mind. Hides fear of commitment behind optimism.',hidden:'Secretly fears being trapped or becoming ordinary.'},
    'Capricorn' :{inner:'Driven by ambition and responsibility. Hides emotional need behind stoicism.',hidden:'Deeply desires love but rarely asks for it.'},
    'Aquarius'  :{inner:'Revolutionary thinker. Hides emotional detachment behind idealism.',hidden:'Craves belonging while fearing loss of individuality.'},
    'Pisces'    :{inner:'Boundless compassion and imagination. Hides confusion behind kindness.',hidden:'Absorbs others emotions — seeks spiritual escape from the world.'},
  };

  function getPersonalityAnalysis() {
    const t = NAKSH_TRAITS[c.nakshatra]||{q:'Wisdom',d:'Growth',s:'Inner strength',w:'Finding balance'};
    const mt = MOON_HIDDEN[c.moon]||{inner:'Complex inner world.',hidden:'Deep hidden desires.'};
    return `
      <div style="margin-bottom:14px;">
        <div style="font-size:13px;letter-spacing:0.12em;color:var(--muted);margin-bottom:8px;">NAKSHATRA QUALITIES — ${c.nakshatra.toUpperCase()}</div>
        <div style="background:rgba(255,195,64,0.05);border:1px solid rgba(255,195,64,0.15);border-radius:10px;padding:14px;">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;font-size:13px;line-height:1.7;">
            <div><span style="color:var(--muted);">Core Quality</span><br>${t.q}</div>
            <div><span style="color:var(--muted);">Soul Desire</span><br>${t.d}</div>
            <div><span style="color:var(--green-lt);">✦ Strengths</span><br>${t.s}</div>
            <div><span style="color:#f87171;">✦ Challenges</span><br>${t.w}</div>
          </div>
        </div>
      </div>
      <div>
        <div style="font-size:13px;letter-spacing:0.12em;color:var(--violet);margin-bottom:8px;">🔮 INNER WORLD — ${c.moon.toUpperCase()} MOON</div>
        <div style="background:rgba(167,139,250,0.07);border:1px solid rgba(167,139,250,0.2);border-radius:10px;padding:14px;font-size:13px;line-height:1.8;">
          <p style="margin-bottom:8px;"><strong style="color:var(--text);">Inner World:</strong> ${mt.inner}</p>
          <p><strong style="color:var(--violet);">Hidden Desire:</strong> ${mt.hidden}</p>
        </div>
      </div>`;
  }

  const REMEDIES={
    'Ketu'   :"Worship Lord Ganesha. Donate blankets on Tuesdays. Wear cat's eye (lehsunia). Chant Om Ketave Namah.",
    'Venus'  :'Worship Goddess Lakshmi on Fridays. Wear diamond or white sapphire. Chant Om Shukraya Namah 108x.',
    'Sun'    :'Offer water to the rising Sun daily. Wear ruby on right ring finger. Recite Aditya Hridayam on Sundays.',
    'Moon'   :'Wear natural pearl. Fast on Mondays. Recite Om Chandraya Namah 108 times. Eat white foods.',
    'Mars'   :'Donate red lentils on Tuesdays. Wear red coral. Recite Om Mangalaya Namah. Visit Hanuman temple.',
    'Rahu'   :'Worship Durga Mata. Donate black sesame on Saturdays. Wear hessonite (gomed). Avoid non-veg on Saturdays.',
    'Jupiter':'Wear yellow sapphire on right index finger on Thursday morning. Donate turmeric and yellow items on Thursdays.',
    'Saturn' :'Recite Shani Chalisa every Saturday. Wear blue sapphire (with expert advice). Donate black sesame and mustard oil.',
    'Mercury':'Wear emerald on right little finger on Wednesday. Donate green vegetables. Recite Om Budhaya Namah.',
  };

  return `
    <div style="border-top:1px solid rgba(255,195,64,0.2);margin:24px 0;padding-top:24px;">
      <div style="font-size:13px;letter-spacing:0.2em;color:var(--gold);margin-bottom:20px;text-align:center;">✦ FULL VEDIC READING ✦</div>

      ${cfg.planetaryPositions?`
      <div style="margin-bottom:20px;">
        <div style="font-size:13px;letter-spacing:0.15em;color:var(--muted);margin-bottom:10px;">GRAHA POSITIONS (SIDEREAL LAHIRI)</div>
        <table style="width:100%;border-collapse:collapse;font-size:14px;">
          <tr style="border-bottom:1px solid rgba(255,195,64,0.1);">
            <th style="padding:6px 10px;text-align:left;color:var(--muted);font-weight:normal;font-size:13px;">GRAHA</th>
            <th style="padding:6px 10px;text-align:left;color:var(--muted);font-weight:normal;font-size:13px;">RASHI</th>
            <th style="padding:6px 10px;text-align:left;color:var(--muted);font-weight:normal;font-size:13px;">DEGREE</th>
            <th style="padding:6px 10px;text-align:left;color:var(--muted);font-weight:normal;font-size:13px;">VAKRI</th>
          </tr>${getPlanetaryPositions()}
        </table>
      </div>`:''}

      ${cfg.antardasha?`
      <div style="margin-bottom:20px;">
        <div style="font-size:13px;letter-spacing:0.15em;color:var(--muted);margin-bottom:10px;">
          VIMSHOTTARI DASHA — ${c.dasha.current.toUpperCase()} (${c.dasha.yrsLeft} yrs left) · ANTARDASHA: ${c.dasha.antardasha.toUpperCase()} (${c.dasha.antYrsLeft} yrs left)
        </div>
        <table style="width:100%;border-collapse:collapse;font-size:13px;">
          <tr style="border-bottom:1px solid rgba(255,195,64,0.1);">
            <th style="padding:6px 10px;text-align:left;color:var(--muted);font-weight:normal;font-size:13px;">MAHADASHA</th>
            <th style="padding:6px 10px;text-align:left;color:var(--muted);font-weight:normal;font-size:13px;">ANTARDASHA</th>
            <th style="padding:6px 10px;text-align:left;color:var(--muted);font-weight:normal;font-size:13px;">DURATION</th>
          </tr>${getAntardashaTable()}
        </table>
      </div>`:''}

      ${cfg.sadheSati?`
      <div style="margin-bottom:20px;">
        <div style="font-size:13px;letter-spacing:0.15em;color:var(--muted);margin-bottom:10px;">SATURN TRANSIT — SADHE SATI · DHAIYA · KANTAKA</div>
        ${getSaturnTransits()}
      </div>`:''}

      ${cfg.planetaryPositions?`
      <div style="margin-bottom:20px;">
        <div style="font-size:13px;letter-spacing:0.15em;color:var(--muted);margin-bottom:10px;">PERSONALITY · INNER DESIRES · STRENGTHS · CHALLENGES</div>
        ${getPersonalityAnalysis()}
      </div>`:''}

      ${cfg.remedies?`
      <div style="background:rgba(255,195,64,0.05);border:1px solid rgba(255,195,64,0.15);border-radius:10px;padding:16px;margin-bottom:20px;">
        <div style="font-size:13px;letter-spacing:0.15em;color:var(--muted);margin-bottom:8px;">REMEDIES FOR ${c.dasha.current.toUpperCase()} MAHADASHA</div>
        <p style="font-size:13px;color:var(--text);line-height:1.8;">${REMEDIES[c.dasha.current]||'Consult Jyogi for personalised remedies.'}</p>
      </div>`:''}
    </div>`;
}
