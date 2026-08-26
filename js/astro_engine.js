// ============================================================
// astro_engine.js — Shared constants + astronomical calculations
// Pure JS — Moon, Sun, planets, Julian Day, Lahiri ayanamsa
// ============================================================


// ─── STAR FIELD ─ deferred to after page load ────────────────────────────
function _initStars(){
  const c=document.getElementById('stars-canvas');
  if(!c) return;
  const ctx=c.getContext('2d');
  let stars=[];
  function resize(){c.width=window.innerWidth;c.height=window.innerHeight;}
  function init(){
    resize();stars=[];
    // Fewer stars on mobile to save GPU/CPU
    const starCount = window.innerWidth < 600 ? 80 : 160;
    for(let i=0;i<starCount;i++){
      stars.push({x:Math.random()*c.width,y:Math.random()*c.height,r:Math.random()*1.4+0.2,a:Math.random(),da:(Math.random()-0.5)*0.003});
    }
  }
  let _starRunning=true;
  document.addEventListener('visibilitychange',()=>{_starRunning=!document.hidden;});
  function draw(ts){
    requestAnimationFrame(draw);
    if(ts-_lastStarFrame<(window._isMobile?50:33))return;
    _lastStarFrame=ts;
    ctx.clearRect(0,0,c.width,c.height);
    stars.forEach(s=>{
      s.a=Math.max(0.05,Math.min(1,s.a+s.da));
      if(s.a<=0.05||s.a>=1)s.da*=-1;
      ctx.beginPath();ctx.arc(s.x,s.y,s.r,0,Math.PI*2);
      ctx.fillStyle=`rgba(255,220,140,${s.a})`;ctx.fill();
    });
  }
  let _lastStarFrame=0;
  window._isMobile=window.innerWidth<600;
  window.addEventListener('resize',()=>{resize();});
  init();draw();
}
// Stars deferred until after page load — doesn't block render
if(document.readyState==='complete') _initStars();
else window.addEventListener('load', _initStars);

// ─── NAV SCROLL FX ────────────────────────────────────────────────────────
window.addEventListener('scroll',()=>{
  document.getElementById('main-nav').style.background=
    window.scrollY>60?'rgba(3,1,10,0.96)':'rgba(3,1,10,0.82)';
});
function jyogiScroll(id){
  var el=document.querySelector(id);
  if(!el) return;
  // Offset for fixed nav bar (64px desktop, 56px mobile)
  var navH = window.innerWidth <= 600 ? 56 : 64;
  var top = el.getBoundingClientRect().top + window.pageYOffset - navH - 8;
  try{
    window.scrollTo({top: top, behavior: 'smooth'});
  }catch(e){
    window.scrollTo(0, top); // Safari fallback
  }
  // Close mobile nav if open
  var mn = document.getElementById('mobile-nav');
  if(mn && mn.classList.contains('open')) mn.classList.remove('open');
}
function toggleMobileNav(){
  const nav      = document.getElementById('mobile-nav');
  const backdrop = document.getElementById('mobile-nav-backdrop');
  const isOpen   = nav.classList.toggle('open');
  if(backdrop) backdrop.classList.toggle('open', isOpen);
  document.body.style.overflow = isOpen ? 'hidden' : '';
}
// Ensure backdrop closes drawer on both click AND touch
(function(){
  document.addEventListener('DOMContentLoaded', function(){
    var bd = document.getElementById('mobile-nav-backdrop');
    if(bd){
      bd.addEventListener('click',  function(e){ e.stopPropagation(); toggleMobileNav(); });
      bd.addEventListener('touchend', function(e){ e.preventDefault(); e.stopPropagation(); toggleMobileNav(); });
    }
  });
})();
function setLang(lang){
  currentLang = lang;
  document.body.classList.toggle('hindi', lang==='hi');
  document.querySelectorAll('.lang-btn').forEach(b=>{
    b.classList.toggle('active', b.dataset.lang===lang);
  });
  if(lang==='hi'){
    document.querySelectorAll('[data-placeholder-hi]').forEach(el=>{
      if(!el.getAttribute('placeholder-orig')) el.setAttribute('placeholder-orig',el.placeholder);
      el.placeholder=el.getAttribute('data-placeholder-hi');
    });
  } else {
    document.querySelectorAll('[data-placeholder-hi]').forEach(el=>{
      if(el.getAttribute('placeholder-orig')) el.placeholder=el.getAttribute('placeholder-orig');
    });
  }
  const tq=document.getElementById('tarot-question');
  if(tq) tq.placeholder=lang==='hi'?'अपना मन एकाग्र करें और प्रश्न टाइप करें…':'Focus your mind and type your question...';
  try{ localStorage.setItem('jyogi_lang', lang); }catch(e){}
}
function updateMobileLang(lang){
  document.getElementById('mob-en-btn').classList.toggle('active', lang==='en');
  document.getElementById('mob-hi-btn').classList.toggle('active', lang==='hi');
}
function toggleTheme(){
  const isLight = document.body.classList.toggle('light-theme');
  document.getElementById('theme-icon').textContent = isLight ? '🌙' : '☀️';
  document.getElementById('theme-label').textContent = isLight ? 'DARK' : 'LIGHT';
  document.getElementById('mob-theme-icon').textContent = isLight ? '🌙' : '☀️';
  document.getElementById('mob-theme-label').textContent = isLight ? 'Dark Mode' : 'Light Mode';
  try{ localStorage.setItem('jyogi_theme', isLight ? 'light' : 'dark'); }catch(e){}
}

// ── FONT SIZE CONTROL ──────────────────────────────────────────
const FS_MIN = 16, FS_MAX = 28, FS_DEFAULT = 20, FS_STEP = 2;
var currentFS = FS_DEFAULT; try{ var _sf=localStorage.getItem('jyogi_fs'); if(_sf) currentFS=parseInt(_sf); }catch(e){}
function applyFontSize(size){
  document.body.style.fontSize = size + 'px';
  try{ localStorage.setItem('jyogi_fs', size); }catch(e){}
  currentFS = size;
}
function changeFontSize(dir){
  if(dir === 0){ applyFontSize(FS_DEFAULT); return; }
  const next = currentFS + dir * FS_STEP;
  if(next >= FS_MIN && next <= FS_MAX) applyFontSize(next);
}
// Restore saved preferences — wrapped for Safari private mode
(function(){
  try{
    var lang = localStorage.getItem('jyogi_lang');
    if(lang === 'hi'){ setLang('hi'); updateMobileLang('hi'); }
    var theme = localStorage.getItem('jyogi_theme');
    if(theme === 'light'){ toggleTheme(); }
    var fs = localStorage.getItem('jyogi_fs');
    if(fs) applyFontSize(parseInt(fs));
  }catch(e){ /* Safari private mode blocks localStorage — silently ignore */ }
})();

// ── Go to Tarot: scroll + auto-draw cards ─────────────────────────────────
function goToChart(){
  document.querySelector('#astrology').scrollIntoView({behavior:'smooth'});
  setTimeout(()=>{
    const n=document.getElementById('astro-name');
    if(n){ n.focus(); }
  },700);
}
function goToTarot(){
  document.querySelector('#tarot').scrollIntoView({behavior:'smooth'});
  setTimeout(()=>{
    const btn=document.getElementById('draw-btn');
    if(btn && window._drawnCards===undefined) btn.click();
  },700);
}

// ── Language Toggle ────────────────────────────────────────────────────────
let currentLang='en';
// setLang is defined above with theme support

// ─── DATA ─────────────────────────────────────────────────────────────────
var TAROT_CARDS = [{"name": "0_The_Fool", "meaning": "New beginnings, enthusiasm, adventures, fresh opportunities, the potential to bring your dreams to life, having faith, a transitional period of awakening, optimism, innocence, light-heartedness and being spontaneous", "shadow": "Naivety, assuming you already have the answer, rash or overly impulsive choices, lacking experience, analysis-paralysis, being bogged down, foolishness, jumping before you look", "affirmation": "I embrace the unknown with an open heart and trust the Universe to catch me."}, {"name": "1_The_Magician", "meaning": "Inspired action, willpower, manifestation, resourcefulness, desire, creation, the power to bring your visions into reality, harnessing your skills and talents", "shadow": "Manipulation, out-of-alignment desires, greed, trickery, illusions, not using your gifts, untapped potential, deceit", "affirmation": "I have all the tools I need. I create my reality with intention and will."}, {"name": "2_The_High_Priestess", "meaning": "Intuition, sacred feminine wisdom, higher powers, the subconscious, mystery, deep knowing, psychic ability, the power of the inner voice, patience and stillness", "shadow": "Secrets, hidden agendas, disconnected from your intuition, a need to listen more deeply, repressed feelings, gossip", "affirmation": "I trust my inner knowing. My intuition is my greatest guide."}, {"name": "3_The_Empress", "meaning": "Abundance, femininity, fertility, nurturing, the earth, creativity, sensuality, beauty, pregnancy, motherhood, the fullness of life", "shadow": "Creative block, dependence, smothering, neglecting self-care, not nurturing yourself or others, feeling disconnected from the earth", "affirmation": "I am abundant, creative, and deeply connected to the flow of life."}, {"name": "4_The_Emperor", "meaning": "Authority, structure, stability, leadership, fatherhood, discipline, establishment, logic, power and control used for good", "shadow": "Domination, rigidity, inflexibility, abuse of power, an overbearing authority figure, lack of discipline, control issues", "affirmation": "I lead with wisdom, discipline, and compassion."}, {"name": "5_The_Hierophant", "meaning": "Tradition, spiritual wisdom, religious institutions, conformity, establishment, a spiritual mentor or teacher, conventional paths, shared beliefs, ceremony", "shadow": "Dogma, challenging tradition, feeling restricted by convention, a need to find your own path, corruption, rebellion", "affirmation": "I honor the wisdom of tradition while staying true to my own soul path."}, {"name": "6_The_Lovers", "meaning": "Love, harmony, relationships, alignment of values, choices, soulmate connections, union, attraction, partnerships built on mutual respect", "shadow": "Disharmony, imbalance in relationships, misaligned values, difficult choices, a love triangle, broken communication", "affirmation": "I choose love. I attract relationships that reflect my highest values."}, {"name": "7_The_Chariot", "meaning": "Willpower, determination, victory, ambition, control, success, overcoming obstacles, forward momentum, the drive to achieve your goals", "shadow": "Lack of control, aggression, opposition, scattered energy, no clear direction, forcing outcomes", "affirmation": "I move forward with focused intention and unstoppable determination."}, {"name": "8_Strength", "meaning": "Courage, inner strength, compassion, patience, soft power, influence, taming the ego, resilience, the power of love over force", "shadow": "Self-doubt, weakness, giving in to fear, lack of self-discipline, raw emotion overtaking reason, insecurity", "affirmation": "My greatest strength comes from love, patience, and compassion."}, {"name": "9_The_Hermit", "meaning": "Soul-searching, introspection, solitude, inner wisdom, a spiritual guide, a period of withdrawal for self-discovery, enlightenment, being a light for others", "shadow": "Isolation, loneliness, withdrawn too far from the world, reclusive behaviour, refusing guidance, loss of direction", "affirmation": "I find wisdom in stillness and carry my light to illuminate the path for others."}, {"name": "10_Wheel_of_Fortune", "meaning": "Fate, karma, turning points, good luck, life cycles, destiny, unexpected change, the flow of the Universe, what goes around comes around", "shadow": "Bad luck, resistance to change, feeling out of control, a negative cycle, clinging to the past", "affirmation": "I flow with life cycles with grace. Every turn brings new opportunity."}, {"name": "11_Justice", "meaning": "Truth, fairness, cause and effect, law, accountability, balance, integrity, honesty, karmic justice, decisions made with clear logic", "shadow": "Injustice, dishonesty, lack of accountability, unfair treatment, avoiding consequences, biased decisions", "affirmation": "I act with integrity. The Universe always returns truth and fairness."}, {"name": "12_The_Hanged_Man", "meaning": "Surrender, pause, new perspectives, sacrifice, suspension, letting go of control, enlightenment through release, a different point of view", "shadow": "Stalling, martyrdom, indecision, delay, refusing to let go, a period of stagnation, wasted potential", "affirmation": "I surrender to the divine flow and find wisdom in the pause."}, {"name": "13_Death", "meaning": "Transformation, endings, new beginnings, transition, letting go, change, the cycle of life, metamorphosis, releasing what no longer serves", "shadow": "Resistance to change, inability to move on, stagnation, holding on too tightly, fear of the unknown", "affirmation": "I release what no longer serves me and welcome beautiful transformation."}, {"name": "14_Temperance", "meaning": "Balance, patience, moderation, purpose, harmony, alchemy, inner peace, a middle path, healing, the blending of opposites", "shadow": "Imbalance, excess, a lack of long-term vision, impatience, discord, extremes, misalignment", "affirmation": "I bring balance and harmony to every area of my life."}, {"name": "15_The_Devil", "meaning": "Bondage, shadow self, materialism, addiction, unhealthy attachments, restriction, patterns that keep you trapped, facing your darker nature", "shadow": "Detachment, breaking free, releasing chains, reclaiming power, the beginning of recovery, awareness of limiting beliefs", "affirmation": "I recognise my shadows with compassion and choose freedom over fear."}, {"name": "16_The_Tower", "meaning": "Sudden upheaval, chaos, revelation, awakening, the crumbling of false structures, radical change, a breakthrough disguised as a breakdown", "shadow": "Avoiding disaster, delaying the inevitable, fear of change, resisting necessary disruption, clinging to broken structures", "affirmation": "Even in chaos, I trust that what falls was never meant to stand."}, {"name": "17_The_Star", "meaning": "Hope, renewal, serenity, inspiration, faith, healing, a guiding light, calm after the storm, the promise of better things to come, spiritual connection", "shadow": "Despair, hopelessness, disconnection from faith, feeling lost, a lack of inspiration, disappointment", "affirmation": "I am filled with hope. The Universe is always working in my favour."}, {"name": "18_The_Moon", "meaning": "Illusion, fear, the subconscious, intuition, dreams, hidden truths, the shadow self, anxiety, mystery, what lies beneath the surface", "shadow": "Confusion lifting, fears releasing, repressed emotions coming to light, unhealthy coping mechanisms, misunderstanding", "affirmation": "I navigate the unknown with trust. My intuition lights the way through illusion."}, {"name": "19_The_Sun", "meaning": "Joy, success, vitality, optimism, clarity, warmth, abundance, positivity, childhood innocence, a radiant YES from the Universe", "shadow": "Pessimism, temporary sadness, blocked joy, inner child wounds, unrealistic expectations, arrogance", "affirmation": "I radiate joy, warmth, and gratitude. Life is beautiful."}, {"name": "20_Judgement", "meaning": "Reflection, reckoning, inner calling, awakening, absolution, a significant transition, hearing a higher calling, rebirth, evaluation", "shadow": "Self-doubt, ignoring your calling, fear of being judged, inability to forgive yourself, an inability to move forward", "affirmation": "I answer my highest calling with courage and open my heart to rebirth."}, {"name": "21_The_World", "meaning": "Completion, accomplishment, wholeness, integration, travel, the end of one cycle and the beginning of another, fulfilment, success", "shadow": "Incompletion, stagnation, a lack of closure, shortcuts taken, not fully integrating lessons before moving on", "affirmation": "I am whole. I celebrate my journey and step forward with wisdom."}, {"name": "Ace_of_Wands", "meaning": "Inspiration, new opportunities, growth, passion, potential, a creative spark, the beginning of something exciting, energy and enthusiasm", "shadow": "Delays, lack of passion, creative block, an idea that has not fully formed, false starts, lost motivation", "affirmation": "I seize this spark of inspiration and channel it into bold, creative action."}, {"name": "Two_of_Wands", "meaning": "Future planning, progress, decisions, courage, stepping outside comfort zone, long-term vision, a world of possibilities", "shadow": "Fear of the unknown, indecision, playing it too safe, lack of planning, feeling trapped in one place", "affirmation": "I plan boldly, trust my vision, and step forward into my expansive future."}, {"name": "Three_of_Wands", "meaning": "Expansion, foresight, overseas opportunities, preparation, looking ahead, growth already in motion, awaiting results of past efforts", "shadow": "Delays, obstacles to travel or expansion, a lack of foresight, plans falling through, impatience", "affirmation": "My horizons are expanding. What I have planted is growing beautifully."}, {"name": "Four_of_Wands", "meaning": "Celebration, joy, harmony, home, community, milestones, relaxation, weddings and happy events, a stable foundation", "shadow": "Instability at home, cancelled celebrations, lack of support, family conflicts, transition periods", "affirmation": "I celebrate how far I have come and cherish the community that surrounds me."}, {"name": "Five_of_Wands", "meaning": "Conflict, disagreements, competition, creative tension, diversity of opinions, healthy debate, challenges that lead to growth", "shadow": "Avoiding conflict, suppressed tension, a need for compromise, unnecessary aggression, chaos", "affirmation": "I rise above conflict with grace and find the wisdom in differing perspectives."}, {"name": "Six_of_Wands", "meaning": "Victory, success, public recognition, progress, self-confidence, acclaim, achievement after hard work, leadership", "shadow": "Ego, a fall from grace, lack of recognition, self-doubt, seeking validation from others, short-lived success", "affirmation": "I embrace my victory with humility and gratitude."}, {"name": "Seven_of_Wands", "meaning": "Perseverance, defending your position, challenge, competition, holding your ground, courage under pressure, standing up for your beliefs", "shadow": "Exhaustion, giving up, feeling overwhelmed, paranoia, not picking your battles wisely", "affirmation": "I stand my ground with confidence. I am worth defending."}, {"name": "Eight_of_Wands", "meaning": "Fast-paced change, movement, swift action, communication, travel, things suddenly accelerating, alignment, momentum", "shadow": "Delays, frustration, scattered energy, miscommunication, being overwhelmed by speed of change", "affirmation": "I embrace the beautiful momentum carrying me towards my goals."}, {"name": "Nine_of_Wands", "meaning": "Resilience, courage, persistence, last push, boundaries, grit, the strength to continue when you are almost at the finish line", "shadow": "Exhaustion, giving up too soon, paranoia, excessive defensiveness, not asking for help when needed", "affirmation": "I am resilient. I have the strength to see this through to the end."}, {"name": "Ten_of_Wands", "meaning": "Burden, responsibility, overcommitment, hard work, carrying too much, the need to delegate or release some weight", "shadow": "Inability to delegate, martyrdom, carrying others' burdens, burnout, refusing help", "affirmation": "I release what is not mine to carry and ask for help without guilt."}, {"name": "Page_of_Wands", "meaning": "Inspiration, discovery, an adventurous spirit, curiosity, a new creative path, enthusiasm, a message of exciting news, potential", "shadow": "Immaturity, a lack of direction, unfocused energy, too many ideas and not enough action, restlessness", "affirmation": "I explore with curiosity and follow my creative spark wherever it leads."}, {"name": "Knight_of_Wands", "meaning": "Energy, passion, adventure, impulsiveness, action, confidence, a fearless pursuit of goals, daring and bold energy", "shadow": "Recklessness, hot-headed behaviour, scattered focus, impulsivity without planning, burnout from moving too fast", "affirmation": "I pursue my passions boldly while tempering my fire with wisdom."}, {"name": "Queen_of_Wands", "meaning": "Courage, confidence, determination, warmth, independence, charisma, a natural leader, someone who uplifts others, creative power", "shadow": "Jealousy, manipulation, demanding behaviour, burned out confidence, feeling unheard", "affirmation": "I radiate warmth and confidence. My fire inspires everyone around me."}, {"name": "King_of_Wands", "meaning": "Natural leader, vision, honour, entrepreneurial spirit, big-picture thinking, inspiration, boldness, a successful and charismatic authority", "shadow": "Impulsiveness, overbearing behaviour, unrealistic expectations, arrogance, ruthlessness", "affirmation": "I lead with vision, honour, and inspire others to reach their highest potential."}, {"name": "Ace_of_Cups", "meaning": "New love, compassion, creativity, emotional abundance, the beginning of a deep emotional journey, a new relationship or spiritual connection, joy", "shadow": "Emotional blockage, repressed feelings, a relationship that is not growing, creative drought, sadness", "affirmation": "I open my heart fully to love, compassion, and creative abundance."}, {"name": "Two_of_Cups", "meaning": "Unified love, partnership, mutual attraction, harmony, the meeting of two souls, a deep soulmate connection, balance in relationship", "shadow": "Imbalance in a relationship, a broken connection, lack of communication, codependency, separation", "affirmation": "I attract and nurture relationships built on mutual love, respect, and harmony."}, {"name": "Three_of_Cups", "meaning": "Celebration, friendship, community, creativity, joy, abundance, coming together, support, sisterhood and brotherhood", "shadow": "Overindulgence, gossip, third-party interference, cliques, celebrations gone wrong, isolation", "affirmation": "I celebrate life with my community and cherish the bonds that lift me higher."}, {"name": "Four_of_Cups", "meaning": "Contemplation, meditation, apathy, boredom, re-evaluation, a period of withdrawal, not seeing the opportunities before you", "shadow": "New awareness, motivation returning, accepting an offer, emerging from a period of stagnation", "affirmation": "I look within for answers and open my eyes to the gifts already around me."}, {"name": "Five_of_Cups", "meaning": "Loss, grief, disappointment, focusing on the negative, regret, mourning, the need to process sadness before moving on", "shadow": "Acceptance, moving on, finding hope after loss, forgiveness, turning towards what remains", "affirmation": "I honour my grief, then gently turn to face the blessings that remain."}, {"name": "Six_of_Cups", "meaning": "Nostalgia, childhood memories, innocence, revisiting the past, comfort, reunion, generosity, simple joys, healing the inner child", "shadow": "Stuck in the past, idealising old times, refusing to grow, an unhealthy attachment to how things were", "affirmation": "I honour my past with gratitude while standing fully present in today's gifts."}, {"name": "Seven_of_Cups", "meaning": "Choices, fantasy, illusion, wishful thinking, imagination, having many options, searching for purpose, daydreaming", "shadow": "Clarity returning, cutting through illusion, making a decision, aligning with reality, facing the truth", "affirmation": "I see through illusion and choose my path with clarity, wisdom, and intention."}, {"name": "Eight_of_Cups", "meaning": "Walking away, disillusionment, leaving behind what no longer serves, a brave exit, seeking deeper meaning, spiritual quest", "shadow": "Fear of change, staying in a situation past its time, inability to walk away, clinging to the familiar", "affirmation": "I have the courage to walk away from what no longer serves my highest good."}, {"name": "Nine_of_Cups", "meaning": "Contentment, satisfaction, gratitude, emotional fulfilment, wishes granted, happiness, pleasure, the dream made real", "shadow": "Overindulgence, superficiality, complacency, inner emptiness beneath outward success, unfulfilled wishes", "affirmation": "I am grateful for the abundance in my life. My heart is full."}, {"name": "Ten_of_Cups", "meaning": "Divine love, blissful relationships, family harmony, deep contentment, a joyful home life, alignment with your heart's desire", "shadow": "Broken family, unhappy home, disconnected relationships, values out of alignment, a gap between the dream and reality", "affirmation": "I am surrounded by love, harmony, and the warmth of deep connection."}, {"name": "Page_of_Cups", "meaning": "Creative opportunities, intuitive messages, emotional sensitivity, dreams, a gentle and curious heart, unexpected news, artistic beginnings", "shadow": "Emotional immaturity, daydreaming without action, vulnerability used against you, naivety in relationships", "affirmation": "I trust the whispers of my heart and follow my creative intuition with joy."}, {"name": "Knight_of_Cups", "meaning": "Romance, charm, imagination, following the heart, an invitation or offer, the pursuit of dreams, a creative and idealistic soul", "shadow": "Moodiness, unrealistic expectations, over-romanticism, emotional manipulation, scattered dreams", "affirmation": "I follow my heart with courage, charm, and an open spirit."}, {"name": "Queen_of_Cups", "meaning": "Compassion, deep intuition, emotional wisdom, nurturing, empathy, a caring presence, inner emotional knowing, healing", "shadow": "Emotional dependency, martyrdom, being overwhelmed by emotions, codependency, suppressed feelings", "affirmation": "I nurture myself and others from a place of deep compassion and wisdom."}, {"name": "King_of_Cups", "meaning": "Emotional balance, wisdom, diplomacy, compassion, generosity, a calm and steady presence, mastery of the emotional world", "shadow": "Emotional manipulation, moodiness, repressed emotions, using feelings as weapons, cold behaviour", "affirmation": "I lead with emotional intelligence, compassion, and steady inner calm."}, {"name": "Ace_of_Swords", "meaning": "Breakthrough, new ideas, mental clarity, truth, justice, clarity of thought, cutting through confusion, a moment of sharp realisation", "shadow": "Confusion, brutal honesty used as a weapon, chaos, scattered thinking, miscommunication", "affirmation": "I cut through confusion with clarity and speak my truth with courage."}, {"name": "Two_of_Swords", "meaning": "A difficult decision, weighing options, a stalemate, avoiding the truth, being at a crossroads, a need to look within for answers", "shadow": "Indecision ending, information coming to light, seeing clearly after confusion, breaking a stalemate", "affirmation": "I trust my intuition to guide me through difficult decisions with clarity."}, {"name": "Three_of_Swords", "meaning": "Heartbreak, emotional pain, grief, sorrow, betrayal, loss, the clearing of old pain, a necessary wound that allows healing", "shadow": "Recovery, healing, releasing pain, forgiveness, the beginning of moving forward after grief", "affirmation": "I allow myself to grieve and trust that healing is already underway."}, {"name": "Four_of_Swords", "meaning": "Rest, recovery, contemplation, sanctuary, a needed break, stillness, withdrawal from conflict, healing through rest", "shadow": "Restlessness, refusing to rest, burnout from overactivity, being forced to slow down", "affirmation": "I give myself permission to rest. Stillness is where I restore my power."}, {"name": "Five_of_Swords", "meaning": "Conflict, defeat, hollow victory, tension, disagreements, a battle where everyone loses something, knowing when to walk away", "shadow": "Reconciliation, moving past conflict, releasing the need to win, forgiving and letting go", "affirmation": "I choose peace over victory and release what no longer needs to be fought."}, {"name": "Six_of_Swords", "meaning": "Transition, moving on, calmer waters ahead, rite of passage, leaving turbulence behind, travel, healing through change", "shadow": "Resistance to change, unable to move on, carrying old baggage into a new situation, unresolved grief", "affirmation": "I move towards calmer waters, releasing the past with grace."}, {"name": "Seven_of_Swords", "meaning": "Deception, strategy, stealth, getting away with something, cunning, avoiding confrontation, keeping secrets", "shadow": "Being caught, coming clean, realising deception, guilt, the consequences of dishonest behaviour", "affirmation": "I act with honesty and integrity. The truth always serves my highest good."}, {"name": "Eight_of_Swords", "meaning": "Self-imposed restriction, negative thoughts, feeling trapped, victim mentality, a situation that feels like no way out — but there is", "shadow": "Liberation, removing the blindfold, taking back your power, a shift in perspective that sets you free", "affirmation": "I am free. I release the thoughts that bind me and step into my power."}, {"name": "Nine_of_Swords", "meaning": "Anxiety, worry, nightmares, fear, sleepless nights, catastrophising, a mind in turmoil, deep-seated fears surfacing", "shadow": "Hope returning, fears releasing, reaching out for help, the worst is over, healing from anxiety", "affirmation": "I release my fears and breathe in peace. The worst exists only in my mind."}, {"name": "Ten_of_Swords", "meaning": "Painful endings, betrayal, a crisis point, rock bottom, an unavoidable conclusion, the darkest moment before the dawn", "shadow": "Recovery, rising again, refusing to be a victim, the turn-around after hitting bottom, resilience", "affirmation": "I have survived this. I rise from the ashes with hard-won wisdom."}, {"name": "Page_of_Swords", "meaning": "Curiosity, new ideas, thirst for knowledge, enthusiasm for truth, a quick mind, messages and communication, a watchful observer", "shadow": "Gossip, haste, scattered ideas, impulsive speech, cutting words, unreliable information", "affirmation": "I seek truth with curiosity and speak with clarity and kindness."}, {"name": "Knight_of_Swords", "meaning": "Ambitious, action-oriented, determined, swift movement towards goals, defending beliefs, a fast-moving situation", "shadow": "Recklessness, rushing in without thinking, aggression, impatience, verbal conflict", "affirmation": "I pursue my goals with focus and temper my ambition with wisdom."}, {"name": "Queen_of_Swords", "meaning": "Independent, sharp mind, clear boundaries, unbiased judgement, wisdom from experience, direct communication, seeing through facades", "shadow": "Overly critical, cold, isolation, cutting people off harshly, using intellect to wound", "affirmation": "I speak my truth with clarity and compassion. My mind is sharp, my heart is open."}, {"name": "King_of_Swords", "meaning": "Mental clarity, intellectual power, authority, truth, decisive leadership, a brilliant strategist, integrity in decision-making", "shadow": "Tyranny, manipulation, cold logic without heart, using intellect to control, ruthlessness", "affirmation": "I lead with clear thought, fair judgement, and unwavering integrity."}, {"name": "Ace_of_Pentacles", "meaning": "A new financial or career opportunity, abundance, prosperity, manifestation, a seed of material potential, grounded beginnings", "shadow": "Missed opportunity, poor financial planning, greed, a venture that will not grow, not valuing what you have", "affirmation": "I welcome abundance into my life and plant seeds that will flourish."}, {"name": "Two_of_Pentacles", "meaning": "Balance, adaptability, time management, juggling multiple priorities, flexibility, playfulness amid challenges", "shadow": "Overwhelmed, poor time management, financial instability, dropping the ball, inability to prioritise", "affirmation": "I balance my responsibilities with ease, grace, and a sense of play."}, {"name": "Three_of_Pentacles", "meaning": "Teamwork, collaboration, skill development, learning, building something together, recognition for your craft, mastery through effort", "shadow": "Lack of teamwork, poor communication, disorganisation, mediocrity, conflicts in a group project", "affirmation": "I build success through collaboration, dedication, and the mastery of my craft."}, {"name": "Four_of_Pentacles", "meaning": "Financial security, saving, stability, a cautious approach to money, holding on, the desire to protect what you have built", "shadow": "Greed, hoarding, scarcity mindset, excessive control, blocking the flow of abundance", "affirmation": "I am secure in my abundance and trust in the flow of prosperity."}, {"name": "Five_of_Pentacles", "meaning": "Financial hardship, poverty consciousness, isolation, feeling left out in the cold, material loss, a call to seek help", "shadow": "Recovery, help available if you ask, turning hardship into resilience, community support, finding your way back", "affirmation": "Even in difficulty, support is available. I reach out and trust that help is near."}, {"name": "Six_of_Pentacles", "meaning": "Generosity, giving and receiving, sharing wealth and resources, charity, gratitude, a kind and balanced exchange", "shadow": "Strings attached to generosity, power imbalance in giving, charity that disempowers, debt and obligation", "affirmation": "I give and receive with an open heart, knowing abundance flows both ways."}, {"name": "Seven_of_Pentacles", "meaning": "Long-term vision, patience, sustainable results, a pause to assess your progress, investment, the fruits of your labour beginning to show", "shadow": "Impatience, poor investment, working hard without results, lack of vision, giving up too soon", "affirmation": "I trust in the process and know that my patient efforts will bear beautiful fruit."}, {"name": "Eight_of_Pentacles", "meaning": "Diligence, skill-building, mastery, commitment to craft, hard work, attention to detail, becoming an expert through practice", "shadow": "Perfectionism, lack of ambition, doing work that does not align with your passion, boredom, mediocre effort", "affirmation": "I dedicate myself to mastering my craft with love, focus, and devotion."}, {"name": "Nine_of_Pentacles", "meaning": "Abundance, luxury, self-sufficiency, financial independence, enjoying the fruits of your labour, refinement, confidence", "shadow": "Overindulgence, dependence on others, not enjoying what you have, hollow success, reckless spending", "affirmation": "I enjoy the beautiful abundance I have created through my own effort."}, {"name": "Ten_of_Pentacles", "meaning": "Legacy, family wealth, long-term security, inheritance, tradition, the culmination of material success, a stable and loving home", "shadow": "Family conflict over money, financial instability, broken legacy, disputes over inheritance", "affirmation": "I build a legacy of love and abundance that will bless generations after me."}, {"name": "Page_of_Pentacles", "meaning": "Manifestation, a new financial or educational opportunity, ambition, practicality, skill development, a studious and grounded energy", "shadow": "Lack of focus, procrastination, poor planning, a missed opportunity, unrealistic dreams with no action", "affirmation": "I take practical steps every day to bring my dreams into beautiful, grounded reality."}, {"name": "Knight_of_Pentacles", "meaning": "Hardworking, reliable, methodical, committed, efficient, responsible, a steady and trustworthy approach to goals", "shadow": "Stubbornness, stuck in routine, overly conservative, boring, resistance to change", "affirmation": "Through steady effort and reliability, I build the life I truly desire."}, {"name": "Queen_of_Pentacles", "meaning": "Nurturing, practical, financially savvy, warm and homely, a caretaker of others, creating comfort and security, resourceful", "shadow": "Neglecting self-care, overworking, smothering, financial insecurity, putting others first to your own detriment", "affirmation": "I nurture my world with practicality and love, beginning always with myself."}, {"name": "King_of_Pentacles", "meaning": "Wealth, abundance, business leadership, discipline, stability, a successful and generous authority, the master of material affairs", "shadow": "Stubbornness, materialism, obsession with status, using wealth as control, rigidity", "affirmation": "I lead with wisdom and generosity, building an empire rooted in integrity."}];

var SPREAD_TYPES = {
  single: {name:'Single Card',positions:['Your Message'],cards:1},
  three: {name:'Past · Present · Future',positions:['Past','Present','Future'],cards:3},
  celtic: {name:'Celtic Cross',positions:['Present','Challenge','Past','Future','Above','Below','Advice','External','Hopes','Outcome'],cards:6},
  love: {name:'Love & Relationship',positions:['You','Your Partner','Connection','Challenge','Outcome'],cards:5},
  career: {name:'Career & Money',positions:['Current Path','Obstacle','Hidden Strength','Action','Outcome'],cards:5},
};

const SERVICES = [
  {id:'vedic_reading',name:'Full Vedic Reading',icon:'🪐',price:'₹1,500',duration:'60 min',
    desc:'Complete birth chart analysis, Dasha periods, Sadhe Sati, planetary remedies, and life predictions. Includes PDF report.',
    includes:['Birth chart (Sidereal Lahiri)','Mahadasha analysis','Relationship & career insights','Vedic remedies (Upayas)','PDF report'],
    msg:"Hi Jyogi! I would like to book a Full Vedic Reading (₹1,500). Please let me know your availability."},
  {id:'tarot_session',name:'Live Tarot Session',icon:'🎴',price:'₹800',duration:'30 min',
    desc:'One-on-one tarot reading via WhatsApp video. Ask your burning question and receive Jyogi\u2019s intuitive guidance.',
    includes:['3-card or 5-card spread','Jyogi Tarot — intuitive reading','Voice explanation','WhatsApp video call','Recorded session'],
    msg:"Hi Jyogi! I would like to book a Live Tarot Session (₹800). Please let me know your availability."},
  {id:'crystal_consult',name:'Crystal Prescription',icon:'💎',price:'₹500',duration:'20 min',
    desc:'Based on your birth chart and current challenges, Jyogi prescribes the exact crystals and wearing protocol for you.',
    includes:['Chart-based crystal selection','Wearing protocol','Mantra recommendations','WhatsApp follow-up','Discount on purchase'],
    msg:"Hi Jyogi! I would like a Crystal Prescription consultation (₹500). Please let me know your availability."},
  {id:'numerology',name:'Numerology Deep-Dive',icon:'🔢',price:'₹699',duration:'30 min',
    desc:'Your Life Path, Expression, Soul Urge, and Personal Year numbers decoded. Discover your life blueprint.',
    includes:['Life Path analysis','Expression number','Soul Urge reading','Personal Year forecast','PDF summary'],
    msg:"Hi Jyogi! I would like a Numerology Deep-Dive session (₹699). Please let me know your availability."},
];

const BRACELETS = [
  {id:'pyrite_citrine',name:'Money Magnet',sub:'Pyrite & Citrine',tagline:'Attract wealth. Amplify abundance.',
    price:'₹1,199',original:'₹1,499',planet:'Jupiter / Sun',chakra:'Solar Plexus',chakraColor:'#FFD700',
    badge:'Best Seller',badgeColor:'#2B7A0B',
    benefits:['Wealth & prosperity','Career growth','Confidence boost','Abundance mindset'],
    ritual:"Wear on left wrist. Chant Om Shreem Hreem Kleem 108 times on Thursdays.",
    img:'image/Shop/Crystals/Bracelets/pyrite_citrine.png?w=800&q=80&auto=format&fit=crop',
    msg:"Hi Jyogi! I want to order the Money Magnet bracelet (₹1,499). Please guide me."},
  {id:'sunstone_bronzite',name:'Executive Presence',sub:'Sunstone & Bronzite',tagline:'Command respect. Lead with clarity.',
    price:'₹1,599',original:'₹2,200',planet:'Sun / Jupiter',chakra:'Solar Plexus',chakraColor:'#E67E22',
    badge:'Leadership',badgeColor:'#8E44AD',
    benefits:['Leadership confidence','Decision-making authority','Public speaking ease','Respect from peers'],
    ritual:"Wear on your dominant hand during presentations or high-stakes meetings.",
    img:'image/Shop/Crystals/Bracelets/Sunstone_Bronzite.jpg?w=800&q=80&auto=format&fit=crop',
    msg:"Hi Jyogi! I want to order the Executive Presence bracelet (₹1,599)."},
  {id:'tigers_hematite',name:'Deep Work Anchor',sub:"Tiger's Eye & Hematite",tagline:'Zero distractions. Maximum output.',
    price:'₹1,149',original:'₹1,650',planet:'Mars / Saturn',chakra:'Root & Solar Plexus',chakraColor:'#5D4037',
    badge:'Tech Favorite',badgeColor:'#2C3E50',
    benefits:['Mental endurance','Sprints & deadline focus','Logic-based problem solving','Grounding'],
    ritual:"Keep on your desk or wear during deep-work blocks. Cleanse under moonlight monthly.",
    img:'image/Shop/Crystals/Bracelets/TigerEyeHematite.png?w=800&q=80&auto=format&fit=crop',
    msg:"Hi Jyogi! I want to order the Deep Work Anchor (₹1,149)."},
  {id:'lepidolite_amethyst',name:'Burnout Recovery',sub:'Lepidolite & Amethyst',tagline:'Decompress deeply. Restore your edge.',
    price:'₹1,299',original:'₹1,850',planet:'Saturn / Moon',chakra:'Third Eye',chakraColor:'#9B59B6',
    badge:'Self-Care',badgeColor:'#16A085',
    benefits:['Anxiety reduction','Emotional stability after work','Improved sleep quality','Mental reset'],
    ritual:"Wear after 6 PM. Hold for 2 minutes and breathe deeply to signal the end of the workday.",
     img:'image/Shop/Crystals/Bracelets/AmethystLepidolite.png?w=800&q=80&auto=format&fit=crop',
    msg:"Hi Jyogi! I want to order the Burnout Recovery bracelet (₹1,299)."},
  /*{id:'sodalite_agate',name:'The Negotiator',sub:'Sodalite & Blue Lace Agate',tagline:'Persuasive speech. Strategic silence.',
    price:'₹1,399',original:'₹1,900',planet:'Mercury',chakra:'Throat',chakraColor:'#3498DB',
    badge:'Strategic',badgeColor:'#2980B9',
    benefits:['Articulation clarity','Calmness under fire','Active listening','Winning negotiations'],
    ritual:'Chant "Ham" 21 times while holding the beads before a negotiation.',
    img:'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=800&q=85&auto=format&fit=crop',
    msg:"Hi Jyogi! I want to order The Negotiator (₹1,399)."},
  {id:'fluorite_clear',name:'Flow State Shield',sub:'Rainbow Fluorite & Clear Quartz',tagline:'Organize chaos. Master your flow.',
    price:'₹1,249',original:'₹1,700',planet:'Mercury / Uranus',chakra:'Crown',chakraColor:'#FFFFFF',
    badge:'Efficiency',badgeColor:'#7F8C8D',
    benefits:['Mental organization','Quick context switching','Creative problem solving','Clarity'],
    ritual:"Wear on days with heavy back-to-back meetings. Rinse with cold water to 'refresh' energy.",
    img:'https://images.unsplash.com/photo-1551029506-0807d46295a0?w=800&q=85&auto=format&fit=crop',
    msg:"Hi Jyogi! I want to order the Flow State Shield (₹1,249)."},
  {id:'student_fluorite',name:'The Focus Scholar',sub:'Rainbow Fluorite & Sodalite',tagline:'Master your curriculum. Calm the exam nerves.',
    price:'₹1,099',original:'₹1,500',planet:'Mercury / Ketu',chakra:'Third Eye & Throat',chakraColor:'#4A90E2',
    badge:'Academic',badgeColor:'#2E86C1',
    benefits:['Information retention','Mental organization','Exam anxiety reduction','Clear articulation'],
    ritual:"Wear on your non-dominant hand while studying. Hold during 5-minute deep breathing before exams.",
    img:'https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=800&q=85&auto=format&fit=crop',
    msg:"Hi Jyogi! I want to order the Focus Scholar bracelet (₹1,099). Please guide me."},
  {id:'shani_discipline',name:"Saturn's Discipline",sub:"Blue Tiger's Eye & Hematite",tagline:'Build your empire. Master the grind.',
    price:'₹1,399',original:'₹1,900',planet:'Saturn',chakra:'Root',chakraColor:'#2C3E50',
    badge:'Karmic',badgeColor:'#1B2631',
    benefits:['Long-term career stability','Discipline & consistency','Protection from delays','Grounding energy'],
    ritual:"Wear on your left wrist on Saturdays. Chant 'Om Sham Shanicharaya Namaha' 108 times at dusk.",
    img:'https://images.unsplash.com/photo-1615484477780-d3c813346712?w=800&q=85&auto=format&fit=crop',
    msg:"Hi Jyogi! I want to order the Shani Discipline bracelet (₹1,399). Please guide me."},
  {id:'aura_recognition',name:'Aura of Recognition',sub:"Sunstone & Tiger's Eye",tagline:'Command the room. Get the credit you deserve.',
    price:'₹1,549',original:'₹2,100',planet:'Sun / Jupiter',chakra:'Solar Plexus',chakraColor:'#F39C12',
    badge:'High Demand',badgeColor:'#E67E22',
    benefits:['Professional visibility','Leadership charisma','Winning social respect','Confidence in public speaking'],
    ritual:"Wear on your right (active) wrist during meetings, interviews, or public events.",
    img:'https://images.unsplash.com/photo-1615484477201-9f495046eabd?w=800&q=85&auto=format&fit=crop',
    msg:"Hi Jyogi! I want to order the Aura of Recognition (₹1,549). Please guide me."},
  {id:'tourmaline_cluster',name:'The Tech Defender',sub:'Raw Black Tourmaline',tagline:'EMF Shielding. Zero Negativity.',
    price:'₹2,499',original:'₹3,500',planet:'Saturn',chakra:'Root',chakraColor:'#000000',
    badge:'Office Must-Have',badgeColor:'#2C3E50',
    benefits:['Neutralizes electronic smog','Protects workspace energy','Grounding for high-stress roles'],
    ritual:"Place between your monitor and yourself. Rinse under running water once a month to reset.",
    img:'https://images.unsplash.com/photo-1615484477720-9f495046eabd?w=800&q=85&auto=format&fit=crop',
    msg:"Hi Jyogi! I want to order the Tech Defender cluster (₹2,499)."},
  {id:'citrine_pyramid',name:'The Wealth Vertex',sub:'Citrine & Pyrite Pyramid',tagline:'Strategic abundance. Professional growth.',
    price:'₹3,299',original:'₹4,500',planet:'Sun / Jupiter',chakra:'Solar Plexus',chakraColor:'#FFD700',
    badge:'Executive Gift',badgeColor:'#8E44AD',
    benefits:['Attracts high-value opportunities','Enhances leadership confidence','Professional recognition'],
    ritual:'Place in the Southeast corner of your office or desk to activate growth energy.',
    img:'https://images.unsplash.com/photo-1599643478518-17488fbbcd75?w=800&q=85&auto=format&fit=crop',
    msg:"Hi Jyogi! I want to order the Wealth Vertex pyramid (₹3,299)."},
  {id:'selenite_tower',name:'The Clarity Column',sub:'Satin Spar Selenite',tagline:'Mental reset. Instant focus.',
    price:'₹1,899',original:'₹2,600',planet:'Moon',chakra:'Crown',chakraColor:'#FFFFFF',
    badge:'Best Seller',badgeColor:'#7F8C8D',
    benefits:['Clears mental fog','Rapid de-stressing','Purifies office atmosphere'],
    ritual:"Hold for 30 seconds between stressful meetings to 'clear' your mental slate.",
    img:'https://images.unsplash.com/photo-1551029506-0807d46295a0?w=800&q=85&auto=format&fit=crop',
    msg:"Hi Jyogi! I want to order the Clarity Column (₹1,899)."},
  {id:'rose_quartz',name:'Self-Love Mala',sub:'Rose Quartz & Clear Quartz',tagline:'Heal your heart. Open to love.',
    price:'₹999',original:'₹1,400',planet:'Venus',chakra:'Heart',chakraColor:'#FF69B4',
    badge:'Most Loved',badgeColor:'#c9910a',
    benefits:['Emotional healing','Attract love','Inner peace','Self-confidence'],
    ritual:"Hold over your heart each morning. Affirm: I am worthy of deep love.",
    img:'https://images.unsplash.com/photo-1602173574767-37ac01994b2a?w=800&q=85&auto=format&fit=crop',
    msg:"Hi Jyogi! I want to order the Self-Love Mala (₹999). Please guide me."},
  {id:'black_tourmaline',name:'Protection Shield',sub:'Black Tourmaline & Obsidian',tagline:'Block negativity. Ground your aura.',
    price:'₹1,299',original:'₹1,800',planet:'Saturn / Ketu',chakra:'Root',chakraColor:'#8B0000',
    badge:'Powerful',badgeColor:'#4a4a6a',
    benefits:['Psychic protection','EMF shielding','Grounding','Removes negativity'],
    ritual:'Place near your front door or workspace. Cleanse monthly under running water.',
    img:'https://images.unsplash.com/photo-1615484477780-d3c813346712?w=800&q=85&auto=format&fit=crop',
    msg:"Hi Jyogi! I want to order the Protection Shield bracelet (₹1,299). Please guide me."},*/
  {id:'lapis_amethyst',name:'Third Eye Awakener',sub:'Lapis Lazuli & Amethyst',tagline:'Activate intuition. Deepen meditation.',
    price:'₹1,199',original:'₹1,600',planet:'Ketu / Jupiter',chakra:'Third Eye & Crown',chakraColor:'#6A0DAD',
    badge:'Spiritual',badgeColor:'#5b3f8c',
    benefits:['Psychic intuition','Deep meditation','Spiritual wisdom','Dream clarity'],
    ritual:'Meditate with bracelet on left wrist. Place on third eye during Shavasana.',
    img:'image/Shop/Crystals/Bracelets/Amethyst_lapiz.png?w=800&q=80&auto=format&fit=crop',
    msg:"Hi Jyogi! I want to order the Third Eye Awakener (₹1,199). Please guide me."},
  {id:'green_aventurine',name:'Lucky Charm',sub:'Green Aventurine & Jade',tagline:'Invite luck. Seize opportunity.',
    price:'₹1,099',original:'₹1,500',planet:'Mercury / Venus',chakra:'Heart',chakraColor:'#228B22',
    badge:'New',badgeColor:'#1a6b8a',
    benefits:['Good luck','New opportunities','Business success','Positive energy'],
    ritual:'Wear during important meetings, interviews, and new beginnings.',
    img:'image/Shop/Crystals/Bracelets/green_aventurine.png?w=800&q=80&auto=format&fit=crop',
    msg:"Hi Jyogi! I want to order the Lucky Charm bracelet (₹1,099). Please guide me."},
  {id:'moonstone_pearl',name:'Divine Feminine',sub:'Moonstone & Pearl',tagline:'Align with the moon. Embrace your power.',
    price:'₹1,349',original:'₹1,800',planet:'Moon / Venus',chakra:'Sacral & Crown',chakraColor:'#C0C0C0',
    badge:'Sacred',badgeColor:'#7a5c8a',
    benefits:['Hormonal balance','Feminine power','Emotional balance','Moon connection'],
    ritual:'Charge under the full moon overnight. Wear during new and full moon days.',
    img:'image/Shop/Crystals/Bracelets/Divine_feminine.png?w=800&q=80&auto=format&fit=crop',
    msg:"Hi Jyogi! I want to order the Divine Feminine bracelet (₹1,349). Please guide me."},
];

var REVIEW_TAG_COLORS = {
  'Crystal':      {bg:'rgba(167,139,250,0.12)',border:'rgba(167,139,250,0.3)',color:'#a78bfa'},
  'Vedic':        {bg:'rgba(255,195,64,0.12)', border:'rgba(255,195,64,0.3)', color:'#FFC340'},
  'Tarot':        {bg:'rgba(45,212,191,0.12)', border:'rgba(45,212,191,0.3)', color:'#2dd4bf'},
  'Compatibility':{bg:'rgba(244,114,182,0.12)',border:'rgba(244,114,182,0.3)',color:'#f472b6'},
};
var REVIEWS = [
  {user:'Anjali S.',location:'Pune',rating:5,product:'Money Magnet Bracelet',tag:'Crystal',avatar:'A',text:'Got a promotion I had been waiting two years for — within weeks of wearing this! The energy shift was real and immediate.'},
  {user:'Rahul K.',location:'Delhi',rating:5,product:'Vedic Reading',tag:'Vedic',avatar:'R',text:'Jyogi identified my Saturn transit challenge and gave remedies that actually worked. Her predictions were frighteningly accurate.'},
  {user:'Priya M.',location:'Mumbai',rating:5,product:'Self-Love Mala',tag:'Crystal',avatar:'P',text:'Beautiful quality crystals. The Rose Quartz mala feels genuinely peaceful — I wear it every single day. My relationship with myself transformed.'},
  {user:'Deepak R.',location:'Bangalore',rating:5,product:'Live Tarot Session',tag:'Tarot',avatar:'D',text:'The live tarot reading gave me complete clarity about my career change. Every card spoke directly to my situation. Mind-blowing.'},
  {user:'Meena T.',location:'Hyderabad',rating:5,product:'Protection Shield',tag:'Crystal',avatar:'M',text:'The negative energy in my office genuinely shifted after placing the tourmaline on my desk. My colleagues even noticed the change in atmosphere.'},
  {user:'Sanjay P.',location:'Kolkata',rating:5,product:'Full Vedic Reading',tag:'Vedic',avatar:'S',text:'The PDF report is incredibly detailed. I have referred to it every month for a year and the predictions keep coming true one by one.'},
  {user:'Kavita L.',location:'Jaipur',rating:5,product:'Third Eye Awakener',tag:'Crystal',avatar:'K',text:'Started having vivid dreams and strong gut feelings after wearing this for a week. My meditation practice deepened immediately.'},
  {user:'Arjun N.',location:'Chennai',rating:5,product:'Crystal Prescription',tag:'Crystal',avatar:'A',text:'The personalised crystal prescription was worth every rupee. Jyogi explained exactly which stones suit my chart — no generic advice.'},
  {user:'Sunita V.',location:'Ahmedabad',rating:5,product:'Lucky Charm',tag:'Crystal',avatar:'S',text:'Wore the Lucky Charm to my business pitch and landed a ₹40L contract. Coincidence? I do not think so. Jyogi is the real deal.'},
  {user:'Neeraj B.',location:'Gurgaon',rating:5,product:'Kundali Compatibility',tag:'Compatibility',avatar:'N',text:'Jyogi matched our charts for marriage and explained compatibility in a way no pandit ever had — logical, detailed, and reassuring.'},
  {user:'Shreya D.',location:'Pune',rating:5,product:'Angel Card Reading',tag:'Tarot',avatar:'S',text:'The Angel card reading was deeply moving. Every message felt personally chosen. I left the session with complete peace about my decision.'},
  {user:'Vikram S.',location:'Noida',rating:5,product:'Saturn Sade Sati Reading',tag:'Vedic',avatar:'V',text:'Going through Sade Sati and felt lost. Jyogi mapped the entire 7.5-year period and showed me exactly when relief comes. That alone was worth it.'},
];

const GOD_GALLERY = [
  {deity:'Radha Krishna',mantra:'Jay Shree RadheyKrishna',meaning:'The eternal source of Divine Love and the Grace that guides every soul.',
    img:'image/radha_krishna1.jpeg'},
  {deity:'Jagadguru Shree Kripalu ji Maharaj',mantra:'Jai Jai Shree Radhe',meaning:'My Eternal Gurudev, the soul and blessings behind every prediction I give.',
    img:'image/God/Kripaluji.jpeg'},
    {deity:'Lord Shiva',mantra:'Om Namah Shivaya',meaning:'The destroyer of ego, the transformer of souls',
      img:'image/God/Shiva.jpeg'},
  {deity:'Goddess Lakshmi',mantra:'Om Shreem Mahalakshmiyei Namah',meaning:'Goddess of wealth, beauty, and abundance',
    img:'image/God/LakshmiMata.jpeg'},

  {deity:'Lord Ganesha',mantra:'Om Gan Ganapataye Namah',meaning:'Remover of obstacles, lord of new beginnings',
          img:'image/God/Ganesh.jpeg'},
  {deity:'Hanuman Ji',mantra:'Jai Bajrangbali',meaning:'The protector who removes all fear and grants unwavering strength.',
          img:'image/God/Hanumanji.png'},
          
  // {
  //   deity: "Radha Krishna",
  //     img: "images/radha_krishna.jpeg" // Ensure this filename matches your file exactly
  // },
  // {
  //     name: "Jagadguru Shree Kripalu ji Maharaj",
  //     img: "images/kripalu_ji.jpg" // Ensure this filename matches your file exactly
  // },
  // {
  //     name: "Hanuman Ji",
  //     img: "images/hanuman.jpg" // Ensure this filename matches your file exactly
  // }  
];

var WA_NUMBER  = '919437794561';
var ADMIN_PASS = 'jyogi2025';
var API_BASE   = 'https://jyogi-api.onrender.com';
var LOG_SECRET = 'jyogi2025';

// ─── CLIENT LOG — memory + localStorage + server ─────────────────────────
var CLIENT_LOG = [];
var LS_KEY = 'jyogi_submissions';

function getLocalLogs(){
  try{ return JSON.parse(localStorage.getItem(LS_KEY)||'[]'); }
  catch(e){ return []; }
}
function saveLocalLogs(arr){
  try{ localStorage.setItem(LS_KEY, JSON.stringify(arr.slice(0,500))); }
  catch(e){}
}

function saveLog(entry){
  const full = {
    ...entry,
    ts: new Date().toLocaleString('en-IN',{timeZone:'Asia/Kolkata'}),
    ts_epoch: Date.now(),
    ua: navigator.userAgent.slice(0,80)
  };
  CLIENT_LOG.unshift(full);
  // ── Save to localStorage immediately (no server needed) ──
  const local = getLocalLogs();
  local.unshift(full);
  saveLocalLogs(local);
  // ── Also POST to Render server (best-effort, silent fail) ──
  fetch(API_BASE+'/api/log',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({secret:LOG_SECRET, entry:full})
  }).catch(()=>{});
}

// ── Log page visit + wake up Render ──────────────────────────────────────
(function(){
  const ref = document.referrer ? document.referrer.replace(/https?:\/\//,'').slice(0,60) : 'direct';
  const page_entry = {
    type: 'page_visit',
    ref,
    screen: window.screen.width+'x'+window.screen.height,
    ts_epoch: Date.now()
  };
  const full = {
    ...page_entry,
    ts: new Date().toLocaleString('en-IN',{timeZone:'Asia/Kolkata'}),
    ua: navigator.userAgent.slice(0,80)
  };
  // Save to localStorage
  try{
    const ls = JSON.parse(localStorage.getItem('jyogi_submissions')||'[]');
    ls.unshift(full);
    localStorage.setItem('jyogi_submissions', JSON.stringify(ls.slice(0,500)));
  }catch(e){}
  // Send to server (wake it up too)
  // Fire after page load so it doesn't compete with rendering
  window.addEventListener('load',()=>{
    setTimeout(()=>{
      fetch(API_BASE+'/api/log',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({secret:LOG_SECRET, entry:full})
      }).catch(()=>{});
    },500);
  });
})();

// ─── VEDIC CHART ENGINE ────────────────────────────────────────────────────
var RASHIS=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];
var NAKSH=['Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra','Punarvasu','Pushya','Ashlesha','Magha','Purva Phalguni','Uttara Phalguni','Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha','Mula','Purva Ashadha','Uttara Ashadha','Shravana','Dhanishtha','Shatabhisha','Purva Bhadrapada','Uttara Bhadrapada','Revati'];
const NAKSH_LORDS=['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury'];
const DASHA_SEQ=['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury'];
const DASHA_YRS=[7,20,6,10,7,18,16,19,17];

// ── Ephemeris helpers ──────────────────────────────────────────────────────
function d2r(d){return d*Math.PI/180;}
function r2d(r){return r*180/Math.PI;}
function toJD(y,m,d,h){
  if(h===undefined)h=0;
  if(m<=2){y-=1;m+=12;}
  const A=Math.floor(y/100);const B=2-A+Math.floor(A/4);
  return Math.floor(365.25*(y+4716))+Math.floor(30.6001*(m+1))+d+h/24+B-1524.5;
}
// Lahiri ayanamsha: 23.85472 at J2000, increases ~50.24 arcsec/yr
function getLahiri(jd){
  const T=(jd-2451545)/36525;
  return 23.85472+(50.2388475/3600)*T*100;
}
function toSid(lon,jd){return mod(lon-getLahiri(jd),360);}

// ── Sun ───────────────────────────────────────────────────────────────────
function calcSun(jd){
  const T=(jd-2451545)/36525;
  const M=mod(357.52911+35999.05029*T,360);
  const C=(1.914602-0.004817*T)*Math.sin(d2r(M))+(0.019993-0.000101*T)*Math.sin(d2r(2*M));
  return toSid(mod(280.46646+36000.76983*T+C,360),jd);
}

// ── Moon (Chapront ELP2000) ───────────────────────────────────────────────
function calcMoon(jd){
  const T=(jd-2451545)/36525;
  const L=mod(218.3164477+481267.88123421*T-0.0015786*T*T,360);
  const M=mod(134.9633964+477198.8675055*T+0.0087414*T*T,360);
  const Ms=mod(357.5291092+35999.0502909*T-0.0001536*T*T,360);
  const F=mod(93.2720950+483202.0175233*T-0.0036539*T*T,360);
  const D=mod(297.8501921+445267.1114034*T-0.0018819*T*T,360);
  const dL=6.288774*Math.sin(d2r(M))+1.274027*Math.sin(d2r(2*D-M))
           +0.658314*Math.sin(d2r(2*D))+0.213618*Math.sin(d2r(2*M))
           -0.185116*Math.sin(d2r(Ms))-0.114332*Math.sin(d2r(2*F))
           +0.058793*Math.sin(d2r(2*D-2*M))+0.057066*Math.sin(d2r(2*D-Ms-M))
           +0.053322*Math.sin(d2r(2*D+M))+0.045758*Math.sin(d2r(2*D-Ms))
           -0.040923*Math.sin(d2r(Ms-M))-0.034720*Math.sin(d2r(D))
           -0.030383*Math.sin(d2r(Ms+M))+0.015327*Math.sin(d2r(2*D-2*F))
           -0.012528*Math.sin(d2r(M+2*F))+0.010980*Math.sin(d2r(M-2*F));
  return toSid(mod(L+dL,360),jd);
}

// ── Heliocentric → Geocentric for Mercury, Venus, Mars (Meeus Ch.33) ─────
// Orbital elements at J2000 + secular rates
const ORB={
  Mercury:{a:0.387098,e:0.205635,L0:252.250906,Ldot:149474.0722491,w0:77.45645,wdot:0.15940,O0:48.33167},
  Venus:  {a:0.723330,e:0.006773,L0:181.979801,Ldot:58519.2130302, w0:131.56370,wdot:0.05641,O0:76.67069},
  Earth:  {a:1.000000,e:0.016708,L0:100.464457,Ldot:36000.7698278, w0:102.93768,wdot:0.32327,O0:0},
  Mars:   {a:1.523688,e:0.093405,L0:355.433000,Ldot:19140.2993313, w0:336.04084,wdot:0.44441,O0:49.55953},
};
function helioXY(name,T){
  const p=ORB[name];
  const L=mod(p.L0+p.Ldot*T,360);
  const w=p.w0+p.wdot*T*100;
  const M=mod(L-w,360);
  const e=p.e;
  // Solve Kepler
  let E=d2r(M);
  for(let i=0;i<8;i++) E=d2r(M)+e*Math.sin(E);
  const v=r2d(2*Math.atan2(Math.sqrt(1+e)*Math.sin(E/2),Math.sqrt(1-e)*Math.cos(E/2)));
  const r=p.a*(1-e*Math.cos(E));
  const lon=mod(v+w,360);
  return {x:r*Math.cos(d2r(lon)), y:r*Math.sin(d2r(lon))};
}
function geoLon(name,jd){
  const T=(jd-2451545)/36525;
  const pl=helioXY(name,T), ea=helioXY('Earth',T);
  return toSid(mod(r2d(Math.atan2(pl.y-ea.y,pl.x-ea.x)),360),jd);
}

// ── Outer planets (mean motion + equation of centre) ─────────────────────
function calcJupiter(jd){
  const days=jd-2451545;
  const M=mod(20.9202+0.08309*days,360);
  const lon=mod(34.3515+0.08309*days+5.5922*Math.sin(d2r(M))+0.1634*Math.sin(d2r(2*M)),360);
  return toSid(lon,jd);
}
function calcSaturn(jd){
  // Precomputed Saturn tropical longitudes (Swiss Ephemeris) every 10 days 1950-2050.
  // Max error vs SwEph: 0.03° — sign placement always correct.
  // Generated from pyswisseph FLG_SWIEPH|FLG_SPEED.
  var _SAT_JD0=2433283.0;
  var _SAT_STEP=10;
  var _SAT_T=[169.436, 169.302, 168.992, 168.52, 167.913, 167.201, 166.426, 165.629, 164.855, 164.147, 163.541, 163.067, 162.746, 162.593, 162.612, 162.805, 163.164, 163.681, 164.343, 165.135, 166.043, 167.05, 168.139, 169.294, 170.497, 171.731, 172.979, 174.222, 175.443, 176.624, 177.743, 178.784, 179.726, 180.55, 181.239, 181.774, 182.143, 182.336, 182.347, 182.178, 181.837, 181.341, 180.719, 180.001, 179.227, 178.441, 177.685, 176.999, 176.418, 175.97, 175.675, 175.546, 175.586, 175.797, 176.171, 176.699, 177.369, 178.167, 179.077, 180.084, 181.17, 182.321, 183.517, 184.741, 185.976, 187.204, 188.406, 189.563, 190.656, 191.666, 192.574, 193.359, 194.006, 194.498, 194.821, 194.969, 194.937, 194.729, 194.355, 193.835, 193.196, 192.473, 191.702, 190.929, 190.192, 189.531, 188.979, 188.56, 188.295, 188.193, 188.259, 188.492, 188.885, 189.428, 190.111, 190.918, 191.834, 192.845, 193.932, 195.079, 196.27, 197.485, 198.707, 199.919, 201.1, 202.232, 203.295, 204.271, 205.139, 205.881, 206.481, 206.925, 207.199, 207.298, 207.221, 206.972, 206.564, 206.02, 205.365, 204.636, 203.871, 203.111, 202.397, 201.762, 201.241, 200.855, 200.622, 200.552, 200.647, 200.906, 201.323, 201.886, 202.586, 203.407, 204.333, 205.35, 206.441, 207.588, 208.775, 209.982, 211.192, 212.386, 213.544, 214.649, 215.679, 216.616, 217.442, 218.137, 218.687, 219.078, 219.3, 219.349, 219.224, 218.933, 218.492, 217.922, 217.253, 216.52, 215.761, 215.017, 214.325, 213.721, 213.232, 212.882, 212.685, 212.65, 212.778, 213.068, 213.512, 214.101, 214.821, 215.66, 216.6, 217.628, 218.725, 219.874, 221.058, 222.258, 223.454, 224.63, 225.765, 226.839, 227.835, 228.731, 229.51, 230.156, 230.653, 230.99, 231.158, 231.154, 230.981, 230.648, 230.173, 229.579, 228.896, 228.16, 227.409, 226.682, 226.016, 225.443, 224.99, 224.678, 224.52, 224.523, 224.689, 225.013, 225.489, 226.106, 226.852, 227.712, 228.671, 229.711, 230.817, 231.97, 233.152, 234.345, 235.529, 236.686, 237.795, 238.838, 239.795, 240.649, 241.38, 241.974, 242.417, 242.698, 242.812, 242.755, 242.535, 242.161, 241.653, 241.036, 240.341, 239.603, 238.862, 238.153, 237.513, 236.974, 236.558, 236.286, 236.17, 236.214, 236.421, 236.784, 237.295, 237.946, 238.72, 239.606, 240.585, 241.642, 242.758, 243.916, 245.098, 246.283, 247.454, 248.59, 249.673, 250.683, 251.601, 252.41, 253.093, 253.634, 254.022, 254.247, 254.306, 254.199, 253.931, 253.518, 252.978, 252.339, 251.633, 250.895, 250.164, 249.476, 248.864, 248.359, 247.983, 247.754, 247.682, 247.771, 248.021, 248.426, 248.977, 249.664, 250.471, 251.384, 252.386, 253.461, 254.589, 255.754, 256.934, 258.113, 259.269, 260.385, 261.44, 262.416, 263.294, 264.058, 264.691, 265.18, 265.514, 265.685, 265.69, 265.532, 265.219, 264.768, 264.198, 263.539, 262.823, 262.087, 261.367, 260.7, 260.117, 259.649, 259.315, 259.13, 259.106, 259.242, 259.539, 259.989, 260.582, 261.307, 262.15, 263.093, 264.12, 265.214, 266.355, 267.526, 268.706, 269.877, 271.019, 272.113, 273.14, 274.082, 274.921, 275.64, 276.225, 276.662, 276.943, 277.061, 277.014, 276.808, 276.452, 275.964, 275.366, 274.688, 273.964, 273.23, 272.523, 271.879, 271.327, 270.896, 270.606, 270.468, 270.493, 270.679, 271.025, 271.522, 272.161, 272.927, 273.806, 274.781, 275.834, 276.947, 278.102, 279.279, 280.459, 281.622, 282.75, 283.823, 284.822, 285.73, 286.53, 287.206, 287.744, 288.131, 288.361, 288.428, 288.333, 288.081, 287.684, 287.16, 286.537, 285.841, 285.11, 284.38, 283.686, 283.065, 282.547, 282.155, 281.909, 281.821, 281.895, 282.134, 282.531, 283.078, 283.763, 284.571, 285.488, 286.496, 287.575, 288.709, 289.877, 291.06, 292.239, 293.395, 294.508, 295.561, 296.533, 297.41, 298.173, 298.807, 299.301, 299.642, 299.824, 299.843, 299.701, 299.406, 298.97, 298.414, 297.765, 297.054, 296.317, 295.591, 294.912, 294.316, 293.831, 293.479, 293.28, 293.242, 293.369, 293.662, 294.111, 294.708, 295.441, 296.293, 297.248, 298.288, 299.394, 300.548, 301.729, 302.919, 304.098, 305.247, 306.346, 307.38, 308.328, 309.174, 309.903, 310.5, 310.953, 311.251, 311.388, 311.363, 311.178, 310.841, 310.369, 309.783, 309.11, 308.385, 307.643, 306.922, 306.26, 305.688, 305.238, 304.928, 304.776, 304.789, 304.97, 305.316, 305.819, 306.468, 307.248, 308.143, 309.136, 310.209, 311.341, 312.514, 313.708, 314.904, 316.083, 317.227, 318.315, 319.331, 320.257, 321.077, 321.776, 322.339, 322.754, 323.013, 323.11, 323.044, 322.819, 322.444, 321.937, 321.322, 320.627, 319.889, 319.143, 318.429, 317.783, 317.237, 316.821, 316.554, 316.449, 316.514, 316.749, 317.149, 317.705, 318.403, 319.23, 320.168, 321.197, 322.301, 323.458, 324.65, 325.857, 327.06, 328.24, 329.379, 330.458, 331.459, 332.367, 333.164, 333.836, 334.37, 334.752, 334.977, 335.038, 334.934, 334.672, 334.262, 333.724, 333.081, 332.366, 331.615, 330.866, 330.158, 329.529, 329.01, 328.628, 328.403, 328.345, 328.462, 328.749, 329.202, 329.809, 330.556, 331.427, 332.405, 333.47, 334.603, 335.784, 336.993, 338.213, 339.423, 340.605, 341.742, 342.814, 343.804, 344.697, 345.476, 346.126, 346.634, 346.989, 347.183, 347.212, 347.075, 346.779, 346.337, 345.769, 345.101, 344.367, 343.604, 342.852, 342.151, 341.539, 341.047, 340.699, 340.515, 340.504, 340.669, 341.007, 341.51, 342.166, 342.96, 343.872, 344.888, 345.985, 347.145, 348.348, 349.575, 350.807, 352.025, 353.211, 354.347, 355.415, 356.398, 357.28, 358.045, 358.677, 359.166, 359.498, 359.666, 359.667, 359.501, 359.175, 358.704, 358.107, 357.416, 356.664, 355.89, 355.137, 354.443, 353.848, 353.381, 353.067, 352.922, 352.956, 353.167, 353.553, 354.104, 354.804, 355.64, 356.591, 357.64, 358.767, 359.952, 1.176, 2.42, 3.663, 4.89, 6.081, 7.219, 8.286, 9.265, 10.14, 10.895, 11.516, 11.989, 12.304, 12.451, 12.428, 12.237, 11.884, 11.386, 10.765, 10.053, 9.284, 8.5, 7.745, 7.059, 6.479, 6.037, 5.754, 5.647, 5.721, 5.976, 6.406, 6.999, 7.74, 8.613, 9.598, 10.677, 11.83, 13.037, 14.28, 15.539, 16.794, 18.03, 19.228, 20.369, 21.438, 22.416, 23.289, 24.039, 24.652, 25.115, 25.416, 25.547, 25.505, 25.292, 24.916, 24.395, 23.752, 23.019, 22.236, 21.443, 20.687, 20.008, 19.443, 19.024, 18.77, 18.697, 18.808, 19.101, 19.569, 20.199, 20.974, 21.879, 22.894, 23.998, 25.173, 26.4, 27.658, 28.93, 30.198, 31.442, 32.648, 33.795, 34.868, 35.849, 36.722, 37.47, 38.08, 38.535, 38.827, 38.946, 38.888, 38.658, 38.262, 37.72, 37.057, 36.307, 35.511, 34.711, 33.954, 33.282, 32.732, 32.333, 32.105, 32.061, 32.204, 32.53, 33.03, 33.691, 34.495, 35.426, 36.464, 37.588, 38.781, 40.023, 41.295, 42.579, 43.857, 45.11, 46.323, 47.477, 48.556, 49.542, 50.417, 51.167, 51.775, 52.227, 52.512, 52.622, 52.552, 52.307, 51.894, 51.334, 50.655, 49.89, 49.082, 48.278, 47.521, 46.855, 46.318, 45.937, 45.732, 45.713, 45.882, 46.235, 46.76, 47.445, 48.271, 49.221, 50.277, 51.417, 52.623, 53.877, 55.159, 56.452, 57.738, 58.999, 60.219, 61.38, 62.464, 63.455, 64.335, 65.086, 65.695, 66.145, 66.426, 66.528, 66.448, 66.19, 65.764, 65.189, 64.495, 63.718, 62.901, 62.093, 61.337, 60.679, 60.153, 59.788, 59.602, 59.603, 59.793, 60.166, 60.71, 61.412, 62.254, 63.217, 64.283, 65.434, 66.648, 67.909, 69.198, 70.497, 71.789, 73.056, 74.282, 75.448, 76.537, 77.532, 78.415, 79.169, 79.778, 80.227, 80.503, 80.598, 80.509, 80.239, 79.801, 79.213, 78.507, 77.721, 76.899, 76.088, 75.336, 74.685, 74.171, 73.82, 73.649, 73.667, 73.872, 74.259, 74.816, 75.529, 76.38, 77.35, 78.422, 79.577, 80.795, 82.059, 83.351, 84.652, 85.947, 87.218, 88.446, 89.616, 90.708, 91.705, 92.59, 93.343, 93.95, 94.396, 94.666, 94.754, 94.655, 94.374, 93.924, 93.325, 92.61, 91.818, 90.992, 90.183, 89.436, 88.793, 88.291, 87.952, 87.794, 87.825, 88.041, 88.438, 89.003, 89.721, 90.575, 91.548, 92.621, 93.775, 94.993, 96.255, 97.547, 98.848, 100.142, 101.412, 102.64, 103.809, 104.901, 105.896, 106.779, 107.529, 108.131, 108.569, 108.831, 108.908, 108.798, 108.505, 108.043, 107.435, 106.712, 105.915, 105.091, 104.285, 103.546, 102.914, 102.423, 102.097, 101.951, 101.991, 102.217, 102.619, 103.188, 103.907, 104.761, 105.732, 106.801, 107.951, 109.165, 110.423, 111.71, 113.007, 114.297, 115.563, 116.787, 117.951, 119.038, 120.028, 120.902, 121.645, 122.236, 122.663, 122.911, 122.973, 122.849, 122.542, 122.067, 121.449, 120.721, 119.923, 119.101, 118.303, 117.575, 116.956, 116.478, 116.165, 116.031, 116.081, 116.313, 116.719, 117.289, 118.007, 118.858, 119.824, 120.888, 122.031, 123.238, 124.489, 125.768, 127.058, 128.34, 129.598, 130.814, 131.969, 133.046, 134.025, 134.887, 135.614, 136.19, 136.598, 136.828, 136.871, 136.728, 136.404, 135.915, 135.288, 134.555, 133.757, 132.942, 132.154, 131.439, 130.836, 130.374, 130.076, 129.954, 130.013, 130.252, 130.662, 131.233, 131.949, 132.796, 133.756, 134.813, 135.949, 137.147, 138.389, 139.658, 140.938, 142.21, 143.456, 144.66, 145.801, 146.863, 147.824, 148.667, 149.374, 149.926, 150.31, 150.515, 150.534, 150.367, 150.023, 149.519, 148.881, 148.144, 147.349, 146.542, 145.768, 145.069, 144.484, 144.041, 143.76, 143.653, 143.723, 143.97, 144.385, 144.957, 145.673, 146.516, 147.471, 148.521, 149.649, 150.837, 152.07, 153.328, 154.595, 155.854, 157.086, 158.273, 159.397, 160.437, 161.376, 162.193, 162.872, 163.395, 163.747, 163.921, 163.909, 163.714, 163.347, 162.825, 162.176, 161.436, 160.645, 159.848, 159.091, 158.412, 157.848, 157.427, 157.165, 157.076, 157.161, 157.418, 157.841, 158.417, 159.134, 159.976, 160.927, 161.972, 163.093, 164.273, 165.495, 166.742, 167.996, 169.24, 170.454, 171.621, 172.722, 173.736, 174.646, 175.432, 176.076, 176.562, 176.878, 177.014, 176.967, 176.741, 176.347, 175.806, 175.145, 174.402, 173.616, 172.832, 172.093, 171.438, 170.898, 170.501, 170.263, 170.194, 170.297, 170.569, 171.002, 171.586, 172.307, 173.151, 174.102, 175.144, 176.26, 177.433, 178.646, 179.882, 181.122, 182.349, 183.544, 184.688, 185.762, 186.746, 187.621, 188.37, 188.973, 189.418, 189.691, 189.784, 189.698, 189.437, 189.014, 188.452, 187.78, 187.034, 186.256, 185.486, 184.768, 184.138, 183.626, 183.257, 183.045, 183.001, 183.126, 183.416, 183.865, 184.461, 185.19, 186.041, 186.995, 188.037, 189.151, 190.32, 191.525, 192.75, 193.976, 195.185, 196.359, 197.476, 198.52, 199.47, 200.307, 201.013, 201.572, 201.969, 202.195, 202.243, 202.114, 201.816, 201.363, 200.78, 200.096, 199.349, 198.579, 197.826, 197.13, 196.528, 196.046, 195.708, 195.527, 195.511, 195.662, 195.976, 196.444, 197.057, 197.8, 198.661, 199.622, 200.669, 201.784, 202.95, 204.149, 205.364, 206.576, 207.767, 208.917, 210.007, 211.017, 211.929, 212.724, 213.384, 213.893, 214.24, 214.415, 214.415, 214.241, 213.905, 213.422, 212.817, 212.123, 211.375, 210.614, 209.879, 209.209, 208.636, 208.187, 207.882, 207.736, 207.752, 207.933, 208.274, 208.767, 209.4, 210.162, 211.037, 212.01, 213.064, 214.182, 215.348, 216.543, 217.749, 218.947, 220.118, 221.243, 222.302, 223.277, 224.148, 224.896, 225.507, 225.965, 226.258, 226.38, 226.33, 226.111, 225.736, 225.223, 224.598, 223.893, 223.146, 222.395, 221.68, 221.036, 220.495, 220.081, 219.813, 219.703, 219.756, 219.971, 220.344, 220.865, 221.524, 222.308, 223.201, 224.188, 225.253, 226.378, 227.545, 228.736, 229.933, 231.116, 232.266, 233.364, 234.392, 235.327, 236.155, 236.855, 237.414, 237.818, 238.056, 238.125, 238.025, 237.76, 237.347, 236.804, 236.159, 235.446, 234.7, 233.961, 233.267, 232.651, 232.143, 231.767, 231.538, 231.468, 231.56, 231.813, 232.221, 232.775, 233.464, 234.274, 235.189, 236.194, 237.272, 238.405, 239.574, 240.763, 241.95, 243.118, 244.246, 245.316, 246.309, 247.204, 247.986, 248.637, 249.142, 249.491, 249.675, 249.69, 249.539, 249.23, 248.778, 248.207, 247.544, 246.822, 246.08, 245.354, 244.682, 244.095, 243.623, 243.286, 243.099, 243.072, 243.207, 243.501, 243.948, 244.539, 245.261, 246.1, 247.041, 248.066, 249.159, 250.301, 251.474, 252.66, 253.837, 254.989, 256.095, 257.135, 258.092, 258.947, 259.682, 260.282, 260.734, 261.028, 261.157, 261.119, 260.919, 260.566, 260.079, 259.48, 258.8, 258.072, 257.334, 256.622, 255.973, 255.418, 254.983, 254.688, 254.546, 254.564, 254.745, 255.084, 255.573, 256.204, 256.962, 257.833, 258.802, 259.849, 260.958, 262.111, 263.288, 264.47, 265.638, 266.773, 267.856, 268.866, 269.786, 270.6, 271.288, 271.838, 272.238, 272.478, 272.554, 272.464, 272.216, 271.823, 271.3, 270.676, 269.98, 269.247, 268.515, 267.819, 267.194, 266.672, 266.276, 266.024, 265.93, 265.996, 266.225, 266.612, 267.147, 267.82, 268.617, 269.522, 270.52, 271.591, 272.717, 273.881, 275.061, 276.241, 277.399, 278.517, 279.575, 280.556, 281.44, 282.212, 282.855, 283.357, 283.706, 283.893, 283.918, 283.779, 283.486, 283.052, 282.498, 281.849, 281.14, 280.403, 279.677, 278.998, 278.4, 277.912, 277.557, 277.351, 277.305, 277.423, 277.702, 278.139, 278.721, 279.439, 280.276, 281.217, 282.244, 283.339, 284.483, 285.658, 286.842, 288.018, 289.166, 290.267, 291.302, 292.253, 293.103, 293.836, 294.435, 294.89, 295.191, 295.329, 295.304, 295.12, 294.783, 294.312, 293.727, 293.056, 292.333, 291.594, 290.876, 290.217, 289.646, 289.194, 288.881, 288.723, 288.727, 288.897, 289.23, 289.718, 290.35, 291.112, 291.991, 292.968, 294.025, 295.144, 296.306, 297.49, 298.679, 299.851, 300.99, 302.075, 303.087, 304.011, 304.828, 305.523, 306.083, 306.494, 306.749, 306.842, 306.771, 306.543, 306.166, 305.659, 305.046, 304.354, 303.62, 302.881, 302.172, 301.531, 300.99, 300.574, 300.305, 300.196, 300.252, 300.476, 300.861, 301.401, 302.083, 302.892, 303.812, 304.824, 305.911, 307.054, 308.233, 309.427, 310.62, 311.789, 312.919, 313.989, 314.981, 315.879, 316.667, 317.328, 317.85, 318.222, 318.435, 318.486, 318.373, 318.104, 317.69, 317.15, 316.51, 315.8, 315.055, 314.315, 313.617, 312.996, 312.485, 312.107, 311.882, 311.822, 311.93, 312.208, 312.648, 313.239, 313.97, 314.824, 315.784, 316.832, 317.948, 319.113, 320.308, 321.513, 322.709, 323.877, 324.998, 326.055, 327.03, 327.906, 328.668, 329.299, 329.789, 330.125, 330.301, 330.313, 330.162, 329.855, 329.406, 328.835, 328.17, 327.442, 326.689, 325.95, 325.262, 324.662, 324.181, 323.841, 323.661, 323.65, 323.811, 324.142, 324.634, 325.277, 326.056, 326.953, 327.952, 329.033, 330.176, 331.363, 332.573, 333.788, 334.989, 336.156, 337.271, 338.319, 339.279, 340.137, 340.876, 341.483, 341.944, 342.25, 342.392, 342.37, 342.184, 341.843, 341.362, 340.763, 340.074, 339.33, 338.569, 337.831, 337.156, 336.576, 336.125, 335.823, 335.686, 335.724, 335.936, 336.318, 336.862, 337.553, 338.377, 339.316, 340.351, 341.463, 342.632, 343.839, 345.065, 346.29, 347.495, 348.664, 349.776, 350.816, 351.766, 352.609, 353.331, 353.917, 354.355, 354.635, 354.749, 354.697, 354.48, 354.108, 353.598, 352.972, 352.262, 351.503, 350.735, 349.999, 349.335, 348.777, 348.355, 348.09, 347.995, 348.079, 348.34, 348.77, 349.362, 350.099, 350.964, 351.941, 353.009, 354.15, 355.343, 356.569, 357.809, 359.044, 0.256, 1.427, 2.539, 3.574, 4.517, 5.351, 6.06, 6.631, 7.05, 7.309, 7.401, 7.322, 7.079, 6.679, 6.142, 5.493, 4.762, 3.989, 3.216, 2.481, 1.829, 1.291, 0.896, 0.667, 0.613, 0.739, 1.045, 1.521, 2.156, 2.933, 3.837, 4.847, 5.945, 7.111, 8.325, 9.568, 10.822, 12.068, 13.286, 14.462, 15.575, 16.61, 17.55, 18.378, 19.079, 19.64, 20.045, 20.288, 20.36, 20.26, 19.993, 19.57, 19.009, 18.338, 17.589, 16.804, 16.024, 15.293, 14.651, 14.132, 13.764, 13.566, 13.549, 13.715, 14.061, 14.577, 15.25, 16.063, 16.999, 18.038, 19.162, 20.349, 21.582, 22.841, 24.107, 25.363, 26.59, 27.771, 28.889, 29.925, 30.865, 31.692, 32.388, 32.942, 33.339, 33.568, 33.626, 33.508, 33.221, 32.777, 32.194, 31.503, 30.739, 29.942, 29.158, 28.43, 27.798, 27.297, 26.953, 26.784, 26.8, 27.0, 27.38, 27.93, 28.635, 29.478, 30.441, 31.504, 32.649, 33.854, 35.102, 36.375, 37.652, 38.917, 40.152, 41.339, 42.462, 43.504, 44.446, 45.273, 45.969, 46.518, 46.909, 47.13, 47.176, 47.044, 46.74, 46.277, 45.676, 44.968, 44.19, 43.383, 42.595, 41.87, 41.247, 40.762, 40.439, 40.295, 40.339, 40.568, 40.977, 41.555, 42.285, 43.152, 44.136, 45.217, 46.377, 47.597, 48.857, 50.14, 51.427, 52.7, 53.943, 55.137, 56.266, 57.312, 58.258, 59.088, 59.785, 60.333, 60.72, 60.935, 60.97, 60.827, 60.508, 60.029, 59.413, 58.69, 57.9, 57.086, 56.295, 55.573, 54.959, 54.488, 54.184, 54.062, 54.128, 54.38, 54.812, 55.411, 56.16, 57.044, 58.043, 59.137, 60.309, 61.539, 62.808, 64.098, 65.392, 66.672, 67.922, 69.122, 70.256, 71.308, 72.259, 73.091, 73.79, 74.337, 74.721, 74.931, 74.958, 74.804, 74.473, 73.98, 73.351, 72.615, 71.815, 70.996, 70.205, 69.487, 68.883, 68.424, 68.137, 68.032, 68.115, 68.386, 68.834, 69.448, 70.211, 71.105, 72.114, 73.216, 74.394, 75.63, 76.904, 78.198, 79.497, 80.782, 82.035, 83.24, 84.379, 85.434, 86.388, 87.222, 87.921, 88.468, 88.848, 89.051, 89.071, 88.906, 88.563, 88.058, 87.417, 86.672, 85.865, 85.043, 84.253, 83.54, 82.946, 82.5, 82.225, 82.135, 82.233, 82.516, 82.976, 83.598, 84.369, 85.269, 86.281, 87.387, 88.566, 89.803, 91.078, 92.374, 93.674, 94.959, 96.214, 97.421, 98.561, 99.616, 100.57, 101.404, 102.1, 102.642, 103.016, 103.212, 103.221, 103.044, 102.69, 102.174, 101.522, 100.769, 99.958, 99.136, 98.35, 97.645, 97.061, 96.627, 96.365, 96.287, 96.395, 96.687, 97.153, 97.78, 98.553, 99.454, 100.466, 101.57, 102.747, 103.981, 105.254, 106.547, 107.844, 109.128, 110.38, 111.584, 112.722, 113.774, 114.724, 115.552, 116.241, 116.775, 117.139, 117.322, 117.318, 117.127, 116.76, 116.231, 115.57, 114.812, 114.0, 113.18, 112.401, 111.706, 111.134, 110.713, 110.463, 110.396, 110.513, 110.812, 111.282, 111.911, 112.683, 113.582, 114.589, 115.688, 116.861, 118.088, 119.355, 120.643, 121.934, 123.212, 124.458, 125.656, 126.786, 127.83, 128.771, 129.588, 130.264, 130.784, 131.132, 131.297, 131.276, 131.068, 130.685, 130.144, 129.474, 128.712, 127.901, 127.087, 126.318, 125.636, 125.078, 124.671, 124.435, 124.379, 124.505, 124.809, 125.282, 125.911, 126.681, 127.576, 128.578, 129.67, 130.836, 132.056, 133.314, 134.593, 135.875, 137.144, 138.38, 139.567, 140.685, 141.716, 142.641, 143.441, 144.098, 144.597, 144.922, 145.064, 145.021, 144.792, 144.39, 143.836, 143.157, 142.392, 141.584, 140.779, 140.024, 139.358, 138.816, 138.427, 138.206, 138.162, 138.298, 138.609, 139.085, 139.715, 140.482, 141.373, 142.37, 143.455, 144.612, 145.823, 147.072, 148.341, 149.611, 150.868, 152.091, 153.262, 154.363, 155.375, 156.278, 157.055, 157.686, 158.156, 158.453, 158.567, 158.495, 158.241, 157.818, 157.248, 156.561, 155.794, 154.992, 154.199, 153.459, 152.812, 152.291, 151.922, 151.719, 151.69, 151.838, 152.158, 152.639, 153.271, 154.039, 154.927, 155.919, 156.998, 158.147, 159.35, 160.588, 161.845, 163.103, 164.344, 165.551, 166.703, 167.782, 168.77, 169.645, 170.391, 170.99, 171.426, 171.687, 171.766, 171.662, 171.379, 170.933, 170.346, 169.651, 168.883, 168.088, 167.309, 166.588, 165.964, 165.467, 165.12, 164.938, 164.928, 165.092, 165.423, 165.913, 166.55, 167.32, 168.208, 169.198, 170.273, 171.416, 172.611, 173.839, 175.084, 176.328, 177.552, 178.738, 179.868, 180.92, 181.878, 182.721, 183.43, 183.99, 184.385, 184.606, 184.645, 184.503, 184.189, 183.717, 183.113, 182.409, 181.643, 180.857, 180.094, 179.395, 178.796, 178.326, 178.005, 177.848, 177.86, 178.043, 178.39, 178.892, 179.538, 180.315, 181.206, 182.197, 183.27, 184.409, 185.597, 186.816, 188.049, 189.278, 190.483, 191.647, 192.75, 193.772, 194.695, 195.499, 196.167, 196.682, 197.032, 197.206, 197.202, 197.02, 196.671, 196.173, 195.551, 194.839, 194.075, 193.299, 192.556, 191.881, 191.31, 190.87, 190.578, 190.45, 190.489, 190.694, 191.061, 191.581, 192.24, 193.027, 193.926, 194.921, 195.996, 197.133, 198.316, 199.527, 200.748, 201.96, 203.146, 204.285, 205.358, 206.346, 207.23, 207.992, 208.613, 209.079, 209.379, 209.504, 209.453, 209.229, 208.845, 208.32, 207.68, 206.961, 206.2, 205.438, 204.714, 204.066, 203.526, 203.118, 202.86, 202.764, 202.833, 203.066, 203.458, 203.998, 204.676, 205.477, 206.388, 207.39, 208.47, 209.608, 210.788, 211.992, 213.2, 214.396, 215.56, 216.672, 217.713, 218.664, 219.505, 220.22, 220.791, 221.205, 221.453, 221.526, 221.426, 221.16, 220.739, 220.187, 219.532, 218.806, 218.05, 217.302, 216.601, 215.982, 215.474, 215.102, 214.881, 214.82, 214.923, 215.188, 215.608, 216.174, 216.874, 217.695, 218.62, 219.634, 220.721, 221.862, 223.041, 224.238, 225.435, 226.614, 227.755, 228.837, 229.844, 230.755, 231.55, 232.216, 232.734, 233.094, 233.286, 233.307, 233.158, 232.849, 232.393, 231.815, 231.144, 230.413, 229.663, 228.931, 228.253, 227.665, 227.193, 226.858, 226.677, 226.655, 226.796, 227.096, 227.55, 228.146, 228.873, 229.716, 230.661, 231.689, 232.786, 233.932, 235.11, 236.301, 237.487, 238.647, 239.763, 240.816, 241.785, 242.654, 243.402, 244.016, 244.481, 244.785, 244.922, 244.89, 244.692, 244.34, 243.85, 243.247, 242.562, 241.828, 241.085, 240.37, 239.718, 239.162, 238.728, 238.433, 238.294, 238.314, 238.496, 238.837, 239.327, 239.957, 240.714, 241.584, 242.55, 243.596, 244.704, 245.857, 247.035, 248.221, 249.394, 250.535, 251.626, 252.647, 253.578, 254.403, 255.103, 255.665, 256.075, 256.323, 256.405, 256.321, 256.076, 255.682, 255.16, 254.533, 253.835, 253.1, 252.365, 251.669, 251.044, 250.522, 250.127, 249.875, 249.78, 249.846, 250.072, 250.455, 250.986, 251.653, 252.444, 253.342, 254.333, 255.398, 256.52, 257.68, 258.859, 260.038, 261.199, 262.321, 263.385, 264.373, 265.265, 266.046, 266.698, 267.207, 267.563, 267.757, 267.786, 267.651, 267.36, 266.927, 266.373, 265.725, 265.015, 264.279, 263.555, 262.878, 262.282, 261.795, 261.441, 261.234, 261.186, 261.299, 261.573, 262.002, 262.576, 263.283, 264.11, 265.04, 266.056, 267.142, 268.278, 269.445, 270.626, 271.799, 272.946, 274.048, 275.085, 276.04, 276.894, 277.631, 278.235, 278.694, 278.997, 279.138, 279.115, 278.931, 278.596, 278.125, 277.542, 276.874, 276.154, 275.419, 274.706, 274.05, 273.484, 273.034, 272.722, 272.562, 272.563, 272.727, 273.05, 273.527, 274.147, 274.896, 275.761, 276.724, 277.767, 278.874, 280.024, 281.199, 282.381, 283.547, 284.681, 285.763, 286.774, 287.696, 288.513, 289.207, 289.765, 290.175, 290.428, 290.519, 290.446, 290.216, 289.839, 289.332, 288.721, 288.034, 287.305, 286.573, 285.872, 285.238, 284.703, 284.291, 284.023, 283.913, 283.964, 284.18, 284.555, 285.082, 285.749, 286.542, 287.445, 288.442, 289.513, 290.64, 291.806, 292.988, 294.17, 295.331, 296.451, 297.514, 298.5, 299.391, 300.171, 300.825, 301.34, 301.704, 301.909, 301.952, 301.834, 301.559, 301.143, 300.603, 299.965, 299.261, 298.525, 297.795, 297.107, 296.497, 295.994, 295.622, 295.399, 295.338, 295.443, 295.712, 296.14, 296.718, 297.433, 298.27, 299.212, 300.243, 301.342, 302.49, 303.67, 304.86, 306.042, 307.197, 308.306, 309.351, 310.313, 311.175, 311.923, 312.54, 313.014, 313.336, 313.498, 313.496, 313.334, 313.019, 312.566, 311.994, 311.332, 310.612, 309.869, 309.143, 308.469, 307.883, 307.412, 307.081, 306.905, 306.895, 307.053, 307.376, 307.858, 308.487, 309.25, 310.131, 311.112, 312.175, 313.302, 314.471, 315.665, 316.863, 318.046, 319.197, 320.295, 321.323, 322.265, 323.102, 323.82, 324.405, 324.843, 325.127, 325.248, 325.206, 325.004, 324.651, 324.162, 323.561, 322.876, 322.141, 321.393, 320.671, 320.013, 319.45, 319.013, 318.723, 318.595, 318.635, 318.846, 319.223, 319.758, 320.438, 321.248, 322.172, 323.191, 324.286, 325.438, 326.628, 327.835, 329.041, 330.227, 331.374, 332.464, 333.479, 334.404, 335.219, 335.912, 336.468, 336.875, 337.124, 337.211, 337.132, 336.893, 336.505, 335.984, 335.355, 334.649, 333.899, 333.147, 332.43, 331.786, 331.249, 330.845, 330.596, 330.514, 330.604, 330.868, 331.298, 331.884, 332.613, 333.468, 334.433, 335.488, 336.613, 337.79, 338.998, 340.219, 341.433, 342.622, 343.768, 344.852, 345.857, 346.768, 347.566, 348.238, 348.77, 349.151, 349.371, 349.426, 349.315, 349.043, 348.622, 348.071, 347.416, 346.69, 345.927, 345.171, 344.459, 343.83, 343.317, 342.947, 342.737, 342.7, 342.839, 343.153, 343.633, 344.268, 345.043, 345.941, 346.943, 348.031, 349.184, 350.384, 351.611, 352.844, 354.067, 355.261, 356.407, 357.488, 358.488, 359.388, 0.174, 0.83, 1.343, 1.702, 1.897, 1.925, 1.786, 1.484, 1.034, 0.456, 359.776, 359.031, 358.256, 357.496, 356.79, 356.176, 355.687, 355.349, 355.177, 355.183, 355.369, 355.729, 356.256, 356.936, 357.753, 358.69, 359.726, 0.844, 2.023, 3.244, 4.487, 5.734, 6.966, 8.166, 9.315, 10.396, 11.392, 12.287, 13.064, 13.709, 14.208, 14.55, 14.726, 14.731, 14.567, 14.24, 13.764, 13.161, 12.459, 11.696, 10.911, 10.147, 9.447, 8.847, 8.381, 8.073, 7.937, 7.983, 8.211, 8.614, 9.183, 9.903, 10.758, 11.729, 12.795, 13.94, 15.141, 16.381, 17.64, 18.899, 20.141, 21.347, 22.501, 23.585, 24.581, 25.474, 26.247, 26.885, 27.375, 27.704, 27.865, 27.852, 27.667, 27.317, 26.818, 26.193, 25.471, 24.692, 23.898, 23.131, 22.436, 21.851, 21.405, 21.124, 21.021, 21.103, 21.368, 21.809, 22.415, 23.17, 24.056, 25.055, 26.147, 27.314, 28.535, 29.79, 31.063, 32.334, 33.585, 34.8, 35.96, 37.048, 38.047, 38.941, 39.714, 40.349, 40.833, 41.154, 41.303, 41.276, 41.074, 40.705, 40.185, 39.54, 38.801, 38.008, 37.206, 36.437, 35.748, 35.175, 34.748, 34.492, 34.417, 34.53, 34.827, 35.3, 35.935, 36.719, 37.63, 38.652, 39.765, 40.949, 42.185, 43.455, 44.739, 46.02, 47.281, 48.503, 49.67, 50.764, 51.768, 52.666, 53.439, 54.074, 54.555, 54.871, 55.012, 54.973, 54.757, 54.372, 53.835, 53.173, 52.419, 51.614, 50.805, 50.036, 49.352, 48.791, 48.381, 48.146, 48.095, 48.233, 48.556, 49.054, 49.713, 50.517, 51.449, 52.488, 53.616, 54.812, 56.06, 57.34, 58.633, 59.922, 61.19, 62.42, 63.593, 64.693, 65.702, 66.604, 67.38, 68.016, 68.496, 68.807, 68.941, 68.893, 68.665, 68.266, 67.715, 67.038, 66.272, 65.458, 64.644, 63.876, 63.198, 62.647, 62.253, 62.035, 62.004, 62.162, 62.504, 63.021, 63.697, 64.516, 65.46, 66.51, 67.647, 68.852, 70.106, 71.393, 72.691, 73.986, 75.26, 76.495, 77.674, 78.779, 79.792, 80.697, 81.476, 82.111, 82.59, 82.897, 83.024, 82.968, 82.728, 82.317, 81.753, 81.065, 80.289, 79.469, 78.653, 77.887, 77.216, 76.675, 76.295, 76.092, 76.077, 76.25, 76.606, 77.135, 77.822, 78.649, 79.601, 80.656, 81.797, 83.005, 84.262, 85.55, 86.852, 88.149, 89.426, 90.663, 91.844, 92.952, 93.967, 94.873, 95.652, 96.286, 96.76, 97.062, 97.181, 97.115, 96.865, 96.442, 95.868, 95.169, 94.387, 93.564, 92.748, 91.987, 91.324, 90.794, 90.426, 90.236, 90.233, 90.418, 90.784, 91.32, 92.012, 92.843, 93.796, 94.851, 95.992, 97.199, 98.455, 99.742, 101.042, 102.338, 103.614, 104.851, 106.031, 107.137, 108.151, 109.054, 109.829, 110.458, 110.925, 111.218, 111.327, 111.249, 110.986, 110.552, 109.966, 109.261, 108.473, 107.65, 106.838, 106.085, 105.432, 104.914, 104.559, 104.381, 104.388, 104.582, 104.954, 105.493, 106.187, 107.017, 107.968, 109.021, 110.157, 111.36, 112.611, 113.893, 115.188, 116.48, 117.751, 118.983, 120.159, 121.259, 122.267, 123.163, 123.929, 124.547, 125.002, 125.281, 125.375, 125.281, 125.005, 124.557, 123.961, 123.249, 122.46, 121.639, 120.834, 120.091, 119.451, 118.948, 118.605, 118.44, 118.457, 118.658, 119.034, 119.575, 120.268, 121.096, 122.042, 123.089, 124.219, 125.415, 126.658, 127.932, 129.22, 130.504, 131.766, 132.99, 134.156, 135.246, 136.243, 137.125, 137.876, 138.478, 138.914, 139.174, 139.249, 139.135, 138.841, 138.379, 137.772, 137.054, 136.265, 135.45, 134.655, 133.925, 133.301, 132.814, 132.486, 132.334, 132.363, 132.57, 132.951, 133.494, 134.185, 135.01, 135.95, 136.991, 138.113, 139.299, 140.534, 141.799, 143.076, 144.35, 145.6, 146.811, 147.964, 149.038, 150.017, 150.88, 151.609, 152.188, 152.6, 152.833, 152.883, 152.745, 152.429, 151.95, 151.332, 150.609, 149.822, 149.014, 148.233, 147.52, 146.914, 146.446, 146.136, 146.0, 146.041, 146.257, 146.644, 147.189, 147.88, 148.702, 149.638, 150.672, 151.786, 152.964, 154.189, 155.443, 156.708, 157.968, 159.205, 160.399, 161.533, 162.587, 163.542, 164.38, 165.08, 165.629, 166.009, 166.211, 166.229, 166.063, 165.722, 165.224, 164.594, 163.866, 163.082, 162.284, 161.518, 160.825, 160.241, 159.795, 159.506, 159.388, 159.444, 159.673, 160.068, 160.618, 161.311, 162.132, 163.066, 164.094, 165.203, 166.373, 167.588, 168.83, 170.083, 171.328, 172.547, 173.721, 174.832, 175.861, 176.787, 177.592, 178.259, 178.77, 179.113, 179.276, 179.258, 179.06, 178.691, 178.172, 177.529, 176.796, 176.016, 175.23, 174.482, 173.812, 173.252, 172.831, 172.567, 172.47, 172.545, 172.789, 173.196, 173.755, 174.454, 175.278, 176.211, 177.238, 178.342, 179.506, 180.711, 181.943, 183.182, 184.411, 185.61, 186.762, 187.846, 188.845, 189.736, 190.504, 191.13, 191.599, 191.898, 192.019, 191.959, 191.725, 191.326, 190.784, 190.128, 189.392, 188.617, 187.845, 187.117, 186.472, 185.94, 185.547, 185.311, 185.239, 185.337, 185.601, 186.023, 186.596, 187.304, 188.135, 189.072, 190.1, 191.202, 192.362, 193.561, 194.782, 196.008, 197.219, 198.397, 199.523, 200.577, 201.541, 202.395, 203.12, 203.701, 204.122, 204.373, 204.447, 204.344, 204.071, 203.641, 203.076, 202.407, 201.668, 200.899, 200.142, 199.436, 198.818, 198.317, 197.955, 197.75, 197.708, 197.833, 198.121, 198.564, 199.154, 199.877, 200.719, 201.665, 202.698, 203.802, 204.959, 206.153, 207.365, 208.577, 209.77, 210.926, 212.024, 213.046, 213.972, 214.783, 215.462, 215.993, 216.363, 216.563, 216.589, 216.44, 216.127, 215.665, 215.077, 214.395, 213.654, 212.893, 212.153, 211.471, 210.882, 210.414, 210.086, 209.915, 209.907, 210.062, 210.379, 210.848, 211.46, 212.203, 213.06, 214.018, 215.06, 216.168, 217.326, 218.517, 219.72, 220.919, 222.093, 223.224, 224.293, 225.279, 226.164, 226.93, 227.56, 228.039, 228.356, 228.502, 228.476, 228.281, 227.928, 227.434, 226.824, 226.13, 225.388, 224.636, 223.914, 223.258, 222.7, 222.267, 221.977, 221.843, 221.872, 222.062, 222.411, 222.911, 223.549, 224.315, 225.192, 226.165, 227.219, 228.335, 229.495, 230.683, 231.878, 233.063, 234.218, 235.323, 236.36, 237.308, 238.15, 238.869, 239.447, 239.872, 240.135, 240.227, 240.15, 239.909, 239.515, 238.99, 238.358, 237.653, 236.912, 236.17, 235.467, 234.839, 234.314, 233.918, 233.668, 233.574, 233.642, 233.871, 234.257, 234.791, 235.46, 236.252, 237.153, 238.145, 239.213, 240.338, 241.503, 242.688, 243.876, 245.046, 246.18, 247.258, 248.261, 249.171, 249.968, 250.637, 251.163, 251.533, 251.74, 251.778, 251.65, 251.363, 250.931, 250.375, 249.724, 249.009, 248.268, 247.539, 246.857, 246.257, 245.767, 245.41, 245.201, 245.151, 245.262, 245.534, 245.959, 246.53, 247.234, 248.057, 248.984, 249.998, 251.081, 252.218, 253.387, 254.57, 255.75, 256.905, 258.018, 259.067, 260.036, 260.905, 261.656, 262.275, 262.749, 263.064, 263.216, 263.201, 263.023, 262.692, 262.222, 261.637, 260.967, 260.244, 259.506, 258.789, 258.129, 257.559, 257.106, 256.79, 256.626, 256.622, 256.779, 257.097, 257.566, 258.177, 258.918, 259.774, 260.73, 261.767, 262.868, 264.016, 265.19, 266.372, 267.544, 268.683, 269.773, 270.795, 271.728, 272.556, 273.262, 273.832, 274.253, 274.515, 274.613, 274.547, 274.321, 273.946, 273.441, 272.829, 272.142, 271.412, 270.677, 269.975, 269.338, 268.8, 268.385, 268.112, 267.995, 268.039, 268.245, 268.611, 269.126, 269.781, 270.562, 271.453, 272.439, 273.501, 274.621, 275.781, 276.96, 278.141, 279.303, 280.427, 281.494, 282.487, 283.385, 284.173, 284.835, 285.357, 285.727, 285.938, 285.984, 285.869, 285.597, 285.181, 284.643, 284.006, 283.302, 282.567, 281.837, 281.15, 280.539, 280.033, 279.659, 279.431, 279.362, 279.457, 279.714, 280.13, 280.694, 281.393, 282.216, 283.144, 284.16, 285.248, 286.387, 287.558, 288.743, 289.922, 291.075, 292.184, 293.229, 294.193, 295.058, 295.808, 296.427, 296.903, 297.226, 297.388, 297.386, 297.223, 296.908, 296.454, 295.883, 295.222, 294.504, 293.765, 293.042, 292.371, 291.786, 291.315, 290.982, 290.801, 290.782, 290.93, 291.24, 291.707, 292.321, 293.068, 293.932, 294.897, 295.945, 297.058, 298.215];
  var _idx=(_jd_={},_jd_=jd,(_jd_-_SAT_JD0)/_SAT_STEP);
  var _i=Math.floor(_idx),_f=_idx-_i;
  if(_i<0)_i=0;if(_i>=_SAT_T.length-1)_i=_SAT_T.length-2;
  var _a=_SAT_T[_i],_b=_SAT_T[_i+1],_d=_b-_a;
  if(_d>180)_d-=360;if(_d<-180)_d+=360;
  var _trop=mod(_a+_d*_f,360);
  return toSid(_trop,jd);
}
function calcRahu(jd){
  const T=(jd-2451545)/36525;
  return toSid(mod(125.0445-1934.1362608*T+0.0020754*T*T,360),jd);
}

// ── Retrograde lookup tables (Swiss Ephemeris, 1 bit per 10 days, 1950-2050) ──
var _RETRO_JD0  = 2433283.0;
var _RETRO_STEP = 10;
var _RETRO_HEX  = {
  Mars:    '07f800000000000000003fc000000000000000007f0000000000000000003f0000000000000000007f000000000000000003fc00000000000000001fe00000000000000001fe00000000000000000ff000000000000000003f8000000000000000001f8000000000000000001f8000000000000000007f000000000000000007f800000000000000003fc00000000000000003fc00000000000000000fe000000000000000001fc000000000000000000fc000000000000000001fc00000000000000000ff00000000000000000ff000000000000000007f800000000000000003fc00000000000000000fe0000000000000000007e0000000000000000007f000000000000000003fc00000000000000001fe00000000000000001fe00000000000000000ff000000000000000003f8000000000000000003f0000000000000000003f8000000000000000007f000000000000000007f800000000000000003fc00000000000000003fc00000000000000000fe000000000000000001f8000000000000000000fc000000000000000001fc00000000000000000ff00000000000000000ff000000000000000007f800000000000000003fc00000000000000000fe00000000000000',
  Mercury: '600600600c01c00c0180300180300600700600c00c00c0380380380600600600c00c00c0180380180300600700600c00e00c0180180180700700700c00c00c0180380180300600300600c00e00c0180180180300300700c00e00c0180180180300700300600c00600c01801c0180300300300e00e00e0180180180300300300600e00600c01801c0180300380300600600601c01c01c0300300300600e00600c01800c0180300380300600600600c00c00c0380300380600600600c01c00c0180300180300600700600c00c00c0180380380600600700c00c00c0180380180300600700600c00e00c0180180180300700700c00c00c0180380180300600300600c00e00c0180180180300300300600c00e0180180180300700300600c00600c01801c0180300300300600e00600c01801c0300300300600e00600c01801c0180300300300600600600c01c01c0380300380600e00600c01800c0180300380300600600600c01c00c0180300380600600600c01c00c0180300180300600700600c00c00c0180380180300600700c00c00c0180380180300600700600c00c00c0180180180300700700600c00e0180380180300700300600c00e00c0180180180300700300600c00e00c',
  Jupiter: '00003ffc0000003ffc0000001ffc0000001ffe0000001ffe0000003ffc0000003ffc0000007ffc0000007ff80000007ff80000007ff80000007ff80000007ff80000003ff80000003ff80000007ff80000007ff8000000fff8000000fff0000000fff0000001fff0000000fff0000000fff0000000fff0000000fff0000000fff0000000fff0000000fff0000001ffe0000001ffe0000003ffe0000003ffc0000003ffc0000001ffc0000001ffe0000001ffe0000001ffe0000001ffe0000003ffe0000003ffc0000007ffc0000007ff80000007ff80000007ff80000007ff80000003ffc0000003ffc0000003ffc0000003ffc0000007ff80000007ff8000000fff0000000fff0000000fff0000000fff0000000fff00000007ff00000007ff00000007ff0000000fff0000000fff0000001fff0000001ffe0000001ffe0000001ffe0000001ffe0000001ffe0000001ffe0000001ffe0000001ffe0000001ffe0000003ffe0000003ffc0000003ffc0000007ffc0000007ffc0000003ffc0000003ffc0000003ffc0000003ffc0000003ffc0000003ffc0000007ff80000007ff8000000fff8000000fff0000000fff0000000fff00000007ff80000007ff80000007ff80000007c',
  Venus:   '7c0000000000001f00000000000003c0000000000000f00000000000001e0000000000000780000000000001f00000000000003c0000000000000f00000000000001e0000000000000780000000000001f00000000000003c0000000000000f00000000000001e0000000000000780000000000001f00000000000003c0000000000000f00000000000001e0000000000000780000000000001f00000000000003c0000000000000f00000000000001e0000000000000780000000000001e00000000000003c0000000000000f00000000000001e0000000000000780000000000001e00000000000003c0000000000000f00000000000001e0000000000000780000000000001e00000000000003c0000000000000f00000000000001e0000000000000780000000000001e00000000000003c0000000000000f00000000000003e0000000000000780000000000001e00000000000003c0000000000000f00000000000003e0000000000000780000000000001e00000000000003c0000000000000f00000000000003e0000000000000780000000000001e00000000000003c0000000000000f00000000000003e0000000000000780000000000001e00000000000003c0000000',
  Saturn:  'fffc000003fff000000fffc000003ffe000001fff8000007ffe000001fff800000fffc000003fff000000fffc000007fff000001fff8000007ffe000001fff800000fffc000003fff000000fffc000003fff000000fff8000003ffe000000fff8000003ffe000000fff8000007ffe000001fff8000007ffe000001fff8000007ffe000001fff8000007ffc000001fff000000fffc000003fff000000fffc000007ffe000001fff8000007ffe000003fff800000fffc000003fff000000fffc000007ffe000001fff8000007ffe000001fff8000007ffc000003fff000000fffc000003fff000000fffc000003fff000000fff8000003ffe000000fff8000003ffe000000fff8000003ffe000001fff8000007ffe000001fff8000007ffe000003fff000000fffc000003fff000001fffc000007ffe000001fff8000007ffe000003fff000000fffc000003fff000000fff8000007ffe000001fff8000007ffe000001fff8000007ffc000001fff0000007ffc000001fff0000007ffc000001fff0000007ffc000003fff000000fffc000003fff000000fffc000003ffe000001fff8000007ffe000001fff8000007ffe000003fff000000fffc000003fff000001fff8000007ffe000'
};

function calcRetrograde(name, jd) {
  if (name==='Sun'||name==='Moon'||name==='Rahu'||name==='Ketu') return false;
  var hex = _RETRO_HEX[name];
  if (!hex) return false;
  var idx  = Math.round((jd - _RETRO_JD0) / _RETRO_STEP);
  if (idx < 0) idx = 0;
  var maxIdx = hex.length * 4 - 1; // 4 bits per hex char? No: 8 bits per 2 hex chars
  // Each 2 hex chars = 1 byte = 8 entries
  var byteIdx = Math.floor(idx / 8);
  var bitIdx  = 7 - (idx % 8);  // MSB first
  if (byteIdx * 2 + 1 >= hex.length) return false;
  var byteVal = parseInt(hex.substring(byteIdx*2, byteIdx*2+2), 16);
  return ((byteVal >> bitIdx) & 1) === 1;
}

function getAllPlanets(y,m,d,hr,mn){
  const h=(hr+(mn/60)-5.5); // IST to UT
  const jd=toJD(y,m,d,h);
  const rahu=calcRahu(jd);
  return {
    jd,
    Sun    : calcSun(jd),
    Moon   : calcMoon(jd),
    Mars   : geoLon('Mars',jd),
    Mercury: geoLon('Mercury',jd),
    Jupiter: calcJupiter(jd),
    Venus  : geoLon('Venus',jd),
    Saturn : calcSaturn(jd),
    Rahu   : rahu,
    Ketu   : mod(rahu+180,360),
  };
}
function rashiOf(lon){return RASHIS[Math.floor(lon/30)];}
// Current Saturn sign (page load)
const TODAY_JD=toJD(new Date().getFullYear(),new Date().getMonth()+1,new Date().getDate(),6);
const SATURN_NOW=rashiOf(calcSaturn(TODAY_JD));

// Safe modulo
function mod(a,b){return((a%b)+b)%b;}

// Vimshottari Dasha from Moon longitude
function getCurrentDasha(moonLon,birthY,birthM,birthD){
  const nakSize=360/27;
  const nakIdx=Math.floor(moonLon/nakSize);
  const lordIdx=mod(nakIdx,9);
  const posInNak=mod(moonLon,nakSize);
  const fracElapsed=posInNak/nakSize;
  const dashaYrsAtBirth=fracElapsed*DASHA_YRS[lordIdx];
  const yearsSinceBirth=(new Date()-new Date(birthY,birthM-1,birthD))/86400000/365.25;
  let remaining=dashaYrsAtBirth+yearsSinceBirth;
  let idx=lordIdx;
  while(remaining>=DASHA_YRS[idx]){remaining-=DASHA_YRS[idx];idx=mod(idx+1,9);}
  const antDuration=ai=>DASHA_YRS[idx]*DASHA_YRS[ai]/120;
  let antRemaining=remaining;
  let ai=idx;
  while(antRemaining>=antDuration(ai)){antRemaining-=antDuration(ai);ai=mod(ai+1,9);}
  return {
    current:DASHA_SEQ[idx], next:DASHA_SEQ[mod(idx+1,9)],
    yrsLeft:(DASHA_YRS[idx]-remaining).toFixed(1),
    antardasha:DASHA_SEQ[ai], antNext:DASHA_SEQ[mod(ai+1,9)],
    antYrsLeft:(antDuration(ai)-antRemaining).toFixed(2),
    lordIdx:idx
  };
}

// ─── VIMSHOTTARI DASHA TREE (Mahadasha → Antardasha → Pratyantardasha →
// Sookshma → Prana) ─────────────────────────────────────────────────────
const DASHA_ABBR={Ketu:'Ke',Venus:'Ve',Sun:'Su',Moon:'Mo',Mars:'Ma',Rahu:'Ra',Jupiter:'Ju',Saturn:'Sa',Mercury:'Me'};
const DASHA_COLORS={Ketu:'#c4915a',Venus:'#e06fc4',Sun:'#e0705f',Moon:'#c9c9d8',Mars:'#f0784a',Rahu:'#8b9bb0',Jupiter:'#e0a938',Saturn:'#6b8fe8',Mercury:'#5cc47a'};
const DASHA_LEVEL_NAMES=['Mahadasha','Antardasha','Pratyantardasha','Sookshma','Prana'];
const DASHA_DAY_ABBR=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];

function dashaAddYears(date,yrs){return new Date(date.getTime()+yrs*365.2425*86400000);}

function formatDashaDate(date){
  const dd=String(date.getDate()).padStart(2,'0');
  const mm=String(date.getMonth()+1).padStart(2,'0');
  return DASHA_DAY_ABBR[date.getDay()]+' '+dd+'-'+mm+'-'+date.getFullYear();
}

// First Mahadasha lord + its (possibly pre-birth) start date, from Moon longitude.
function dashaBirthAnchor(moonLon,birthDate){
  const nakSize=360/27;
  const nakIdx=Math.floor(moonLon/nakSize);
  const lordIdx=mod(nakIdx,9);
  const posInNak=mod(moonLon,nakSize);
  const fracElapsed=posInNak/nakSize;
  const elapsedYrs=fracElapsed*DASHA_YRS[lordIdx];
  return {lordIdx,start:dashaAddYears(birthDate,-elapsedYrs)};
}

// The 9 Mahadasha periods spanning a full 120-year Vimshottari cycle from birth.
function buildDashaLevel1(moonLon,birthDate){
  const anchor=dashaBirthAnchor(moonLon,birthDate);
  const rows=[];
  let start=anchor.start, lordIdx=anchor.lordIdx;
  for(let i=0;i<9;i++){
    const yrs=DASHA_YRS[lordIdx];
    rows.push({chain:[lordIdx], start, end:dashaAddYears(start,yrs), yrs});
    start=dashaAddYears(start,yrs);
    lordIdx=mod(lordIdx+1,9);
  }
  return rows;
}

// Sub-periods of any dasha row: 9-fold split starting at the row's own lord,
// same proportional rule at every depth (standard Vimshottari sub-period logic).
function buildDashaChildren(row){
  const parentLordIdx=row.chain[row.chain.length-1];
  const rows=[];
  let start=row.start;
  for(let i=0;i<9;i++){
    const subIdx=mod(parentLordIdx+i,9);
    const yrs=row.yrs*DASHA_YRS[subIdx]/120;
    rows.push({chain:row.chain.concat([subIdx]), start, end:dashaAddYears(start,yrs), yrs});
    start=dashaAddYears(start,yrs);
  }
  return rows;
}

function dashaChainLabel(chain){
  return chain.map(function(i){
    const name=DASHA_SEQ[i];
    return '<span style="color:'+DASHA_COLORS[name]+'">'+DASHA_ABBR[name]+'</span>';
  }).join('<span style="color:var(--dim)">-</span>');
}

function buildFallbackChart(name,dob,time,cityLat,cityLon){
  const parts=dob.split('-').map(Number);
  const y=parts[0],m=parts[1],d=parts[2];
  const tp=(time||'12:00').split(':').map(Number);
  const hr=isNaN(tp[0])?12:tp[0], mn=isNaN(tp[1])?0:tp[1];
  const P=getAllPlanets(y,m,d,hr,mn);
  const moonLon=P.Moon, sunLon=P.Sun;
  const moonSignIdx=Math.floor(moonLon/30);
  const nakshIdx=Math.floor(moonLon/(360/27));
  // Use actual city coordinates — accurate Lagna depends on exact lat/lon
  const lat=cityLat||23.0, lon=cityLon||80.0;
  const utH=hr+(mn/60)-5.5; // IST → UT
  const jdForLagna=toJD(y,m,d,utH);
  const theta=mod(280.46061837+360.98564736629*(jdForLagna-2451545),360); // GAST
  const lst=mod(theta+lon,360); // Local Sidereal Time in degrees
  const eps=23.4407;
  const ramc_r=d2r(lst), phi_r=d2r(lat), e_r=d2r(eps);
  // atan2 handles all quadrants correctly — replaces the buggy atan+quadrant correction
  let ascTrop=Math.atan2(Math.cos(ramc_r),-(Math.sin(ramc_r)*Math.cos(e_r)+Math.tan(phi_r)*Math.sin(e_r)))*180/Math.PI;
  ascTrop=mod(ascTrop,360);
  const ascSid=mod(ascTrop-getLahiri(jdForLagna),360);
  const lagnaIdx=Math.floor(ascSid/30);
  const dasha=getCurrentDasha(moonLon,y,m,d);
  const rashi=i=>RASHIS[mod(i,12)];
  const naksh=i=>NAKSH[mod(i,27)];
  // Build retrograde map using finite-difference speed
  const retrograde={};
  ['Mars','Mercury','Jupiter','Venus','Saturn'].forEach(function(pn){
    if(calcRetrograde(pn,P.jd)) retrograde[pn]=true;
  });

  // Build houseMap: Whole Sign house relative to lagna
  const houseMap={};
  Object.entries(P).forEach(function(kv){
    if(kv[0]==='jd') return;
    houseMap[kv[0]]=((Math.floor(kv[1]/30)-lagnaIdx+12)%12)+1;
  });

  return {
    lagna:rashi(lagnaIdx), moon:rashi(moonSignIdx),
    nakshatra:naksh(nakshIdx), dasha, planets:P,
    moonLon, sunLon, retrograde, houseMap,
    lagnaIdx, planetSignMap: Object.entries(P).reduce(function(acc,kv){if(kv[0]!=='jd')acc[kv[0]]=Math.floor(kv[1]/30);return acc;},{}),
    html:`
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px;">
      <div style="background:rgba(255,195,64,0.07);border:1px solid rgba(255,195,64,0.2);border-radius:12px;padding:14px;">
        <div style="font-size:14px;letter-spacing:0.15em;color:var(--muted);margin-bottom:4px;">LAGNA (ASCENDANT)</div>
        <div style="font-family:'Cinzel',serif;color:var(--gold);font-size:18px;">${rashi(lagnaIdx)}</div>
      </div>
      <div style="background:rgba(255,195,64,0.07);border:1px solid rgba(255,195,64,0.2);border-radius:12px;padding:14px;">
        <div style="font-size:14px;letter-spacing:0.15em;color:var(--muted);margin-bottom:4px;">MOON SIGN (RASHI)</div>
        <div style="font-family:'Cinzel',serif;color:var(--gold);font-size:18px;">${rashi(moonSignIdx)}</div>
      </div>
      <div style="background:rgba(255,195,64,0.07);border:1px solid rgba(255,195,64,0.2);border-radius:12px;padding:14px;">
        <div style="font-size:14px;letter-spacing:0.15em;color:var(--muted);margin-bottom:4px;">BIRTH NAKSHATRA</div>
        <div style="font-family:'Cinzel',serif;color:var(--gold);font-size:18px;">${naksh(nakshIdx)}</div>
      </div>
      <div style="background:rgba(255,195,64,0.07);border:1px solid rgba(255,195,64,0.2);border-radius:12px;padding:14px;">
        <div style="font-size:14px;letter-spacing:0.15em;color:var(--muted);margin-bottom:4px;">MAHADASHA · ANTARDASHA</div>
        <div style="font-family:'Cinzel',serif;color:var(--gold);font-size:16px;">${dasha.current} · ${dasha.antardasha}</div>
        <div style="font-size:13px;color:var(--muted);">${dasha.yrsLeft} yrs in Mahadasha</div>
      </div>
    </div>
    <p style="font-size:14px;color:var(--dim);font-style:italic;text-align:center;">✦ Highly accurate Vedic calculations · Trusted by seekers across India ✦</p>`
  };
}

// ─── RENDER SERVICES ──────────────────────────────────────────────────────
