// ============================================================
// dreams.js
// ============================================================

function selectMood(el){
  _dreamMood=el.dataset.mood;
  document.querySelectorAll('.mood-btn').forEach(b=>b.classList.remove('sel'));
  el.classList.add('sel');
}

function saveDream(){
  const text=document.getElementById('dream-text').value.trim();
  if(!text){alert('Please describe your dream first.');return;}
  const dreams=getDreams();
  // Draw a tarot card for this dream
  const card=TAROT_CARDS[Math.floor(Math.random()*TAROT_CARDS.length)];
  const isRev=Math.random()<0.35;
  const entry={
    id:Date.now(),
    text,
    mood:_dreamMood,
    date:new Date().toLocaleDateString('en-IN',{day:'2-digit',month:'short',year:'numeric'}),
    card:card.name,
    cardDisplay:card.name.replace(/_/g,' ').replace(/^\d+\s/,''),
    cardReversed:isRev,
    cardMsg: isRev ? card.shadow : card.meaning,
    tags:extractDreamTags(text)
  };
  dreams.unshift(entry);
  if(dreams.length>30) dreams.pop();
  try{ localStorage.setItem(DREAM_KEY, JSON.stringify(dreams)); }catch(e){}
  clearDreamForm();
  renderDreamLog();
}

function getDreams(){
  try{ const d=localStorage.getItem(DREAM_KEY); return d?JSON.parse(d):[]; }
  catch(e){ return []; }
}

function clearDreamForm(){
  document.getElementById('dream-text').value='';
  _dreamMood='peaceful';
  document.querySelectorAll('.mood-btn').forEach(b=>b.classList.remove('sel'));
}

function clearAllDreams(){
  if(!confirm('Clear all dream entries?')) return;
  try{ localStorage.removeItem(DREAM_KEY); }catch(e){}
  renderDreamLog();
}


function extractDreamTags(text){
  const lower=text.toLowerCase();
  const found=[];
  Object.entries(DREAM_KEYWORDS).forEach(([tag,words])=>{
    if(words.some(w=>lower.includes(w))) found.push(tag);
  });
  return found.slice(0,4);
}


function renderDreamLog(){
  const dreams=getDreams();
  const el=document.getElementById('dream-log');
  if(!el) return;
  if(!dreams.length){
    el.innerHTML='<div class="dream-empty">✦ Your dream log is empty. Record your first dream above and receive a tarot guidance card.</div>';
    return;
  }
  el.innerHTML=dreams.map(d=>`
    <div class="dream-entry">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
        <div class="dream-date">${d.date}</div>
        <div style="font-size:18px;">${{peaceful:'😌',anxious:'😰',confused:'😕',joyful:'😊',fearful:'😨',mysterious:'🌙',powerful:'⚡'}[d.mood]||'😌'}</div>
      </div>
      <div class="dream-text">${d.text.length>200?d.text.slice(0,200)+'…':d.text}</div>
      ${d.tags.length?'<div class="dream-tags">'+d.tags.map(t=>`<span class="dream-tag" title="${DREAM_TAG_MEANINGS[t]||''}">✦ ${t}</span>`).join('')+'</div>':''}
      <div style="margin-top:10px;background:rgba(167,139,250,0.06);border:1px solid rgba(167,139,250,0.2);border-radius:10px;padding:10px;">
        <div style="font-size:14px;letter-spacing:0.2em;color:var(--violet);margin-bottom:4px;">TAROT GUIDANCE • ${d.cardDisplay}${d.cardReversed?' (Reversed)':''}</div>
        <div style="font-size:14px;color:var(--muted);line-height:1.6;">${(d.cardMsg||'').slice(0,120)}…</div>
        <div style="font-size:13px;color:var(--violet);margin-top:6px;cursor:pointer;" onclick="openWhatsApp('Hi Jyogi, I had a dream and received the ${d.cardDisplay} card. I want to understand this deeper.')">Book a dream interpretation session →</div>
      </div>
    </div>
  `).join('');
}

// ════════════════════════════════════════════════════════════════
// FEATURE: MUHURTA — AUSPICIOUS TIMING
// ════════════════════════════════════════════════════════════════

