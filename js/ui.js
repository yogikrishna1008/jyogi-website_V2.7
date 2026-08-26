// ============================================================
// ui.js — UI: stars, nav, theme, pickers, spinners, admin
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

// ── Ephemeris helpers ──────────────────────────────────────────────────────

function renderServices(){
  const g=document.getElementById('services-grid');
  g.innerHTML=SERVICES.map(s=>`
    <div class="service-card">
      <div class="svc-icon">${s.icon}</div>
      <div class="svc-name">${s.name}</div>
      <div class="svc-price">${s.price}</div>
      <div class="svc-duration">Duration: ${s.duration}</div>
      <div class="svc-desc">${s.desc}</div>
      <div class="svc-includes">${s.includes.map(i=>`<span class="svc-tag">✓ ${i}</span>`).join('')}</div>
      <button class="btn-book" onclick="openWhatsApp('${s.msg.replace(/'/g,"\'")}')" >
        <span>💬</span> Book via WhatsApp
      </button>
    </div>
  `).join('');
}

// ─── RENDER SHOP ──────────────────────────────────────────────────────────

// ─── CRYSTAL MODAL ────────────────────────────────────────────────────────
function openCrystalModal(id){
  const b = BRACELETS.find(x => x.id === id);
  if(!b) return;

  const m = document.getElementById('crystal-modal');
  if(!m) return;

  // Populate modal
  document.getElementById('cm-img').src     = b.img;
  document.getElementById('cm-img').onerror = function(){ this.src='image/'+b.id+'.jpg'; };
  document.getElementById('cm-badge').textContent        = b.badge;
  document.getElementById('cm-badge').style.background   = b.badgeColor;
  document.getElementById('cm-name').textContent         = b.name;
  document.getElementById('cm-sub').textContent          = b.sub;
  document.getElementById('cm-tagline').textContent      = b.tagline;
  document.getElementById('cm-price').textContent        = b.price;
  document.getElementById('cm-original').textContent     = b.original;
  document.getElementById('cm-planet').textContent       = '🪐 ' + b.planet;
  document.getElementById('cm-chakra').textContent       = '✦ ' + b.chakra + ' Chakra';
  document.getElementById('cm-chakra-dot').style.background = b.chakraColor;
  document.getElementById('cm-benefits').innerHTML =
    b.benefits.map(x => '<span class="benefit-tag">'+x+'</span>').join('');
  document.getElementById('cm-ritual').textContent = b.ritual;
  document.getElementById('cm-order-btn').onclick =
    function(){ openWhatsApp(b.msg); };

  m.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeCrystalModal(){
  const m = document.getElementById('crystal-modal');
  if(m) m.classList.remove('open');
  document.body.style.overflow = '';
}

// Close on Escape key
document.addEventListener('keydown', function(e){
  if(e.key === 'Escape') closeCrystalModal();
});

function renderShop(){
  const g=document.getElementById('shop-grid');
  // Show 4 featured on main page — full list at crystals.html
  const featured = BRACELETS.filter(b => ['pyrite_citrine','sunstone_bronzite','lepidolite_amethyst','moonstone_pearl'].includes(b.id));
  g.innerHTML=featured.map(b=>`
    <div class="bracelet-card" onclick="openCrystalModal('${b.id}')" style="cursor:pointer;">
      <div class="bracelet-img-wrap">
        <img src="${b.img}" alt="${b.name}" loading="lazy" style="width:100%;height:100%;object-fit:cover;display:block;" onerror="this.src='image/${b.id}.jpg'">
        <div class="bracelet-badge" style="background:${b.badgeColor}">${b.badge}</div>
      </div>
      <div class="bracelet-body">
        <div class="bracelet-price-bubble">
          <div class="bpb-price">${b.price}</div>
          <div class="bpb-original">${b.original}</div>
        </div>
        <div class="bracelet-name">${b.name}</div>
        <div class="bracelet-sub">${b.sub}</div>
        <div class="bracelet-tagline">${b.tagline}</div>
        <div class="bracelet-planet">
          <span class="chakra-dot" style="background:${b.chakraColor}"></span>
          ${b.planet} · ${b.chakra} Chakra
        </div>
        <div class="bracelet-benefits">${b.benefits.map(x=>`<span class="benefit-tag">${x}</span>`).join('')}</div>
        <div class="bracelet-ritual">🕯️ ${b.ritual}</div>
        <button onclick="openCrystalModal('${b.id}');event.stopPropagation();" style="width:100%;margin-bottom:8px;padding:11px;background:rgba(255,195,64,0.07);border:1px solid rgba(255,195,64,0.25);border-radius:10px;color:var(--gold);font-family:'Cormorant SC',serif;font-size:13px;letter-spacing:0.2em;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.background='rgba(255,195,64,0.13)'" onmouseout="this.style.background='rgba(255,195,64,0.07)'">
          ✦ View Details & Ritual
        </button>
        <button class="btn-order" onclick="openWhatsApp('${b.msg.replace(/'/g,"\'")}')" >
          <span>💬</span> Order on WhatsApp
        </button>
        <button onclick="openWhatsApp('Hi Jyogi! Can you help me find the perfect crystal bracelet for my birth chart and current energy?')" style="width:100%;margin-top:8px;padding:10px;background:transparent;border:1px solid rgba(255,195,64,0.2);border-radius:10px;color:var(--gold);font-family:'Cormorant SC',serif;font-size:13px;letter-spacing:0.15em;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.background='rgba(255,195,64,0.07)'" onmouseout="this.style.background='transparent'">
          ✦ Not Sure? Consult Jyogi for Your Perfect Match
        </button>
      </div>
    </div>
  `).join('');
}

// ─── RENDER REVIEWS ───────────────────────────────────────────────────────
var _activeReviewTag = 'All';

function renderReviews(filterTag){
  filterTag = filterTag || 'All';
  _activeReviewTag = filterTag;
  document.querySelectorAll('.rv-pill').forEach(function(pill){
    var isActive = pill.dataset.tag === filterTag;
    pill.style.background  = isActive ? 'rgba(255,195,64,0.15)' : 'transparent';
    pill.style.borderColor = isActive ? 'rgba(255,195,64,0.5)'  : 'rgba(255,195,64,0.15)';
    pill.style.color       = isActive ? '#FFC340' : '#8a7355';
    pill.style.fontWeight  = isActive ? '600' : '400';
  });
  var list = filterTag === 'All' ? REVIEWS : REVIEWS.filter(function(r){ return r.tag === filterTag; });
  var g = document.getElementById('reviews-grid');
  if(!list.length){
    g.innerHTML = '<div style="text-align:center;padding:40px;color:#8a7355;font-style:italic;grid-column:1/-1;">No reviews in this category yet.</div>';
    return;
  }
  g.innerHTML = list.map(function(r){
    var tc = REVIEW_TAG_COLORS[r.tag] || REVIEW_TAG_COLORS['Vedic'];
    return '<div class="review-card">'+
      '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">'+
        '<div class="review-stars">'+'★'.repeat(r.rating)+'</div>'+
        '<span style="font-size:11px;padding:3px 10px;border-radius:20px;border:1px solid '+tc.border+';background:'+tc.bg+';color:'+tc.color+';font-family:Cormorant SC,serif;letter-spacing:0.1em;">'+r.tag+'</span>'+
      '</div>'+
      '<div class="review-product">'+r.product+'</div>'+
      '<div class="review-text">"'+r.text+'"</div>'+
      '<div class="review-user">'+
        '<div class="review-avatar">'+r.avatar+'</div>'+
        '<div>'+
          '<div class="review-name">'+r.user+'</div>'+
          '<div class="review-location">'+r.location+'</div>'+
        '</div>'+
      '</div>'+
    '</div>';
  }).join('');
}
function renderGallery(){
  const g=document.getElementById('god-grid');
  g.innerHTML=GOD_GALLERY.map(d=>`
    <div class="god-card">
      <div class="god-img-ring">
        <img src="${d.img}" alt="${d.deity}" loading="lazy">
      </div>
      <div class="god-name">${d.deity}</div>
      <div class="god-mantra">${d.mantra}</div>
      <div class="god-meaning">${d.meaning}</div>
    </div>
  `).join('');
}

// ─── TAROT READER ─────────────────────────────────────────────────────────
var currentSpread='single';


async function openAdmin(){
  const pass=prompt('Enter admin password:');
  if(pass!==ADMIN_PASS){alert('Incorrect password.');return;}
  // Create modal overlay
  let modal=document.getElementById('admin-modal');
  if(!modal){
    modal=document.createElement('div');
    modal.id='admin-modal';
    modal.style.cssText='position:fixed;inset:0;z-index:9999;background:rgba(3,1,10,0.97);overflow-y:auto;padding:0;';
    modal.innerHTML=
      '<div style="background:#0f0428;border-bottom:1px solid rgba(255,195,64,0.2);padding:12px 24px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;position:sticky;top:0;z-index:10;">'+
        '<div style="display:flex;align-items:center;gap:8px;">'+
          '<span style="font-family:Cinzel,serif;color:#FFC340;font-size:16px;">✦ Jyogi Admin</span>'+
          '<div style="display:flex;background:rgba(0,0,0,0.3);border-radius:8px;padding:3px;gap:2px;">'+
            '<button onclick="admSetTab(&apos;subs&apos;)" id="adm-tab-subs" style="padding:5px 14px;border-radius:6px;border:none;background:rgba(255,195,64,0.15);color:#FFC340;cursor:pointer;font-size:12px;font-family:Cormorant SC,serif;letter-spacing:0.1em;">Submissions</button>'+
            '<button onclick="admSetTab(&apos;blog&apos;)" id="adm-tab-blog" style="padding:5px 14px;border-radius:6px;border:none;background:transparent;color:#8a7355;cursor:pointer;font-size:12px;font-family:Cormorant SC,serif;letter-spacing:0.1em;">Blog Editor</button>'+
          '</div>'+
        '</div>'+
        '<div style="display:flex;gap:8px;align-items:center;">'+
          '<div id="adm-stats" style="display:flex;gap:8px;"></div>'+
          '<button onclick="admDownload(&apos;csv&apos;)" id="adm-btn-csv" style="padding:6px 14px;border-radius:20px;border:none;background:linear-gradient(135deg,#2B7A0B,#1a5208);color:#fff;cursor:pointer;font-size:13px;">⬇ CSV</button>'+
          '<button onclick="admDownload(&apos;json&apos;)" id="adm-btn-json" style="padding:6px 14px;border-radius:20px;border:none;background:linear-gradient(135deg,#1d4ed8,#1e3a8a);color:#fff;cursor:pointer;font-size:13px;">⬇ JSON</button>'+
          '<button onclick="admRefresh()" id="adm-btn-refresh" style="padding:6px 14px;border-radius:20px;border:1px solid rgba(255,195,64,0.3);background:transparent;color:#FFC340;cursor:pointer;font-size:13px;">↻</button>'+
          '<button onclick="admClearLocal()" id="adm-btn-clear" style="padding:6px 12px;border-radius:20px;border:1px solid rgba(248,113,113,0.3);background:transparent;color:#f87171;cursor:pointer;font-size:13px;">🗑</button>'+
          '<button onclick="document.getElementById(&apos;admin-modal&apos;).remove()" style="padding:6px 12px;border-radius:20px;border:1px solid rgba(255,255,255,0.15);background:transparent;color:#9d8c6a;cursor:pointer;font-size:13px;">✕</button>'+
        '</div>'+
      '</div>'+
      '<div style="padding:6px 24px;display:flex;align-items:center;gap:16px;">'+
        
        '</div>'+
        '<div id="adm-note" style="padding:2px 24px 8px;font-size:14px;color:#6b5e44;"></div>'+
      '<div id="adm-subs-panel">'+
      '<div style="padding:6px 24px;display:flex;align-items:center;gap:16px;">'+
        '<div id="adm-server-status-inner" style="font-size:13px;color:#6b5e44;"></div>'+
      '</div>'+
      '<div id="adm-note" style="padding:2px 24px 8px;font-size:14px;color:#6b5e44;"></div>'+
      '<div id="adm-table" style="padding:16px 24px;overflow-x:auto;"><p style="color:#9d8c6a;text-align:center;padding:40px;font-style:italic;">⏳ Loading submissions…</p></div>'+
    '</div>'+
    '<div id="adm-blog-panel" style="display:none;"></div>';
    document.body.appendChild(modal);
  } else {
    modal.style.display='';
  }
  admRefresh();
}

function admStatBox(num,lbl){
  return '<div style="background:rgba(255,195,64,0.07);border:1px solid rgba(255,195,64,0.15);border-radius:8px;padding:8px 14px;text-align:center;min-width:60px;">'+
    '<div style="font-size:20px;color:#FFC340;font-weight:bold;">'+num+'</div>'+
    '<div style="font-size:14px;color:#6b5e44;letter-spacing:0.12em;margin-top:2px;">'+lbl+'</div></div>';
}

function admRenderTable(data, source){
  const tbl=document.getElementById('adm-table');
  const note=document.getElementById('adm-note');
  const stats=document.getElementById('adm-stats');
  const upd=document.getElementById('adm-updated');
  if(!tbl) return;
  if(!data.length){
    tbl.innerHTML='<p style="color:#6b5e44;text-align:center;padding:40px;">No submissions yet.</p>';
    note.textContent='0 submissions — '+source;
    stats.innerHTML=admStatBox(0,'TOTAL')+admStatBox(0,'CHARTS')+admStatBox(0,'TAROT')+admStatBox(0,'BOOKINGS')+admStatBox(0,'VISITS');
    upd.textContent='Updated: '+new Date().toLocaleTimeString('en-IN');
    return;
  }
  // Sort newest first
  data.sort((a,b)=>(b.ts_epoch||0)-(a.ts_epoch||0));
  let charts=0,tarot=0,bookings=0,visits=0;
  data.forEach(e=>{
    const t=e.type||'';
    if(t==='tarot') tarot++;
    else if(t==='whatsapp_booking') bookings++;
    else if(t==='page_visit') visits++;
    else if(t==='chart'||t==='chart_result') charts++;
  });
  stats.innerHTML=admStatBox(data.length,'TOTAL')+admStatBox(charts,'CHARTS')+admStatBox(tarot,'TAROT')+admStatBox(bookings,'BOOKINGS')+admStatBox(visits,'VISITS');
  note.textContent=data.length+' event(s) — '+source;
  upd.textContent='Updated: '+new Date().toLocaleTimeString('en-IN');
  const cols=['#','TIME (IST)','TYPE','DETAILS'];
  let html='<table style="width:100%;border-collapse:collapse;font-size:13px;">';
  html+='<thead><tr>'+cols.map(c=>'<th style="background:#160840;color:#FFC340;padding:10px 12px;text-align:left;font-size:14px;letter-spacing:0.1em;white-space:nowrap;border-bottom:2px solid rgba(255,195,64,0.15);">'+c+'</th>').join('')+'</tr></thead><tbody>';
  data.forEach((e,i)=>{
    const t=e.type||'event';
    const TYPE_COLOR={
      chart:'#86efac', chart_result:'#4ade80',
      tarot:'#a78bfa', compatibility:'#f472b6',
      whatsapp_booking:'#25D366', page_visit:'#6b7280',
      CODE_FAIL:'#f87171', UNLOCKED:'#34d399'
    };
    const tc=TYPE_COLOR[t]||'#FFC340';
    const bg=i%2===0?'rgba(255,255,255,0.02)':'transparent';
    // Build rich detail string per event type
    let detail='';
    if(t==='chart'){
      detail='<span style="color:#FFC340;font-weight:bold;">'+(e.name||'?')+'</span>'
        +' &nbsp;<span style="color:#9d8c6a;">'+(e.dob||'')+'</span>'
        +(e.time&&e.time!=='unknown'?' '+e.time:'')
        +' &nbsp;<span style="color:#86efac;">'+(e.city||'')+'</span>'
        +(e.question&&e.question!=='—'?'<br><span style="color:#c4a97a;font-style:italic;font-size:14px;">Q: '+e.question+'</span>':'');
    } else if(t==='chart_result'){
      detail='<span style="color:#FFC340;font-weight:bold;">'+(e.name||'?')+'</span>'
        +' &nbsp;<span style="color:#fbbf24;">'+[e.lagna,e.moon,e.nakshatra].filter(Boolean).join(' · ')+'</span>'
        +(e.dasha?' &nbsp;<span style="color:#9d8c6a;">'+e.dasha+' dasha</span>':'')
        +' &nbsp;<span style="color:#86efac;">'+(e.city||'')+'</span>';
    } else if(t==='tarot'){
      detail='<span style="color:#a78bfa;">'+(e.spread||'Reading')+'</span>'
        +(e.question&&e.question!=='—'?' &nbsp;<span style="color:#c4a97a;font-style:italic;">'+e.question+'</span>':'')
        +(e.cards?'<br><span style="color:#6b5e44;font-size:13px;">'+(e.cards||'')+'</span>':'');
    } else if(t==='compatibility'){
      detail='<span style="color:#FFC340;">'+(e.c1||'?')+'</span>'
        +' × <span style="color:#FFC340;">'+(e.c2||'?')+'</span>'
        +' &nbsp;<span style="color:#fbbf24;font-weight:bold;">'+(e.score||'?')+'/36</span>'
        +' ('+Math.round(e.pct||0)+'%)';
    } else if(t==='whatsapp_booking'){
      detail='<span style="color:#25D366;">'+(e.message||'Booking').slice(0,150)+'</span>';
    } else if(t==='page_visit'){
      detail='<span style="color:#6b7280;">from: '+(e.ref||'direct')+'</span>'
        +(e.screen?' &nbsp;'+e.screen:'');
    } else if(t==='CODE_FAIL'){
      detail='<span style="color:#FFC340;">'+(e.name||'?')+'</span>'
        +' tried invalid code: <span style="color:#f87171;">'+(e.code||'?')+'</span>';
    } else if(t==='UNLOCKED'){
      detail='<span style="color:#FFC340;">'+(e.name||'?')+'</span>'
        +' unlocked full reading with code: <span style="color:#34d399;">'+(e.code||'?')+'</span>';
    } else {
      detail='<span style="color:#6b5e44;font-size:13px;">'+JSON.stringify(e).replace(/[<>]/g,'').slice(0,120)+'</span>';
    }
    html+='<tr style="border-bottom:1px solid rgba(255,255,255,0.04);background:'+bg+'">'+
      '<td style="padding:8px 10px;color:#6b5e44;font-size:13px;">'+(i+1)+'</td>'+
      '<td style="padding:8px 10px;color:#9d8c6a;white-space:nowrap;font-size:13px;">'+(e.ts||'—')+'</td>'+
      '<td style="padding:8px 10px;white-space:nowrap;"><span style="color:'+tc+';font-size:13px;letter-spacing:0.06em;background:rgba(255,255,255,0.06);padding:2px 7px;border-radius:4px;">'+t.replace('_',' ').toUpperCase()+'</span></td>'+
      '<td style="padding:8px 12px;line-height:1.6;">'+detail+'</td>'+
    '</tr>';
  });
  html+='</tbody></table>';
  tbl.innerHTML=html;
}

async function admSetTab(tab){
  var subsPanel=document.getElementById('adm-subs-panel');
  var blogPanel=document.getElementById('adm-blog-panel');
  var tabSubs=document.getElementById('adm-tab-subs');
  var tabBlog=document.getElementById('adm-tab-blog');
  var csvBtn=document.getElementById('adm-btn-csv');
  var jsonBtn=document.getElementById('adm-btn-json');
  var refreshBtn=document.getElementById('adm-btn-refresh');
  var clearBtn=document.getElementById('adm-btn-clear');
  if(tab==='subs'){
    if(subsPanel) subsPanel.style.display='';
    if(blogPanel) blogPanel.style.display='none';
    tabSubs.style.background='rgba(255,195,64,0.15)';tabSubs.style.color='#FFC340';
    tabBlog.style.background='transparent';tabBlog.style.color='#8a7355';
    if(csvBtn){csvBtn.style.display='';jsonBtn.style.display='';refreshBtn.style.display='';clearBtn.style.display='';}
  } else {
    if(subsPanel) subsPanel.style.display='none';
    if(blogPanel) blogPanel.style.display='';
    tabBlog.style.background='rgba(255,195,64,0.15)';tabBlog.style.color='#FFC340';
    tabSubs.style.background='transparent';tabSubs.style.color='#8a7355';
    if(csvBtn){csvBtn.style.display='none';jsonBtn.style.display='none';refreshBtn.style.display='none';clearBtn.style.display='none';}
    admInitBlogEditor();
  }
}

function admInitBlogEditor(){
  var p=document.getElementById('adm-blog-panel');
  if(!p) return;
  if(p.dataset.init){admLoadPosts();return;}
  p.dataset.init='1';
  var today=new Date().toLocaleDateString('en-IN',{month:'long',year:'numeric'});
  p.innerHTML=admBuildEditorHTML(today);
  // Wire toolbar buttons via data attributes (avoids quote escaping)
  p.querySelectorAll('[data-fmt]').forEach(function(btn){
    btn.addEventListener('click',function(){admFmt(this.dataset.fmt);});
  });
  p.querySelectorAll('[data-wrap]').forEach(function(btn){
    btn.addEventListener('click',function(){admWrap(this.dataset.wrap,this.dataset.wrap);});
  });
  p.querySelectorAll('[data-ins]').forEach(function(btn){
    btn.addEventListener('click',function(){admIns(this.dataset.ins);});
  });
  document.getElementById('be-desc').addEventListener('input',admAnalyseSEO);
  admLoadPosts();
  admAnalyseSEO();
}

function admBuildEditorHTML(today){
  return '<div style="display:grid;grid-template-columns:240px 1fr 210px;height:calc(100vh - 100px);overflow:hidden;">'

  // ── LEFT: post list ───────────────────────────────────────
  +'<div style="border-right:1px solid rgba(255,195,64,0.1);display:flex;flex-direction:column;overflow:hidden;background:#06010f;">'
    +'<div style="padding:12px 14px;border-bottom:1px solid rgba(255,195,64,0.08);display:flex;align-items:center;justify-content:space-between;">'
      +'<span style="font-family:Cormorant SC,serif;font-size:10px;letter-spacing:0.2em;color:#6b5e44;">SAVED POSTS</span>'
      +'<button onclick="admNewPost()" style="padding:3px 10px;border-radius:10px;border:1px solid rgba(255,195,64,0.25);background:transparent;color:#FFC340;cursor:pointer;font-size:11px;">+ New</button>'
    +'</div>'
    +'<div id="be-post-list" style="flex:1;overflow-y:auto;padding:6px 10px;"></div>'
  +'</div>'

  // ── CENTRE: editor ────────────────────────────────────────
  +'<div style="display:flex;flex-direction:column;overflow:hidden;">'

    // Meta fields
    +'<div style="padding:8px 12px;border-bottom:1px solid rgba(255,195,64,0.07);display:grid;grid-template-columns:1fr 1fr 110px 130px;gap:8px;background:#0f0428;flex-shrink:0;">'
      +'<div><div style="font-size:9px;letter-spacing:0.2em;color:#6b5e44;font-family:Cormorant SC,serif;margin-bottom:3px;">TITLE</div>'
      +'<input id="be-title" oninput="admAnalyseSEO()" style="width:100%;background:#030108;border:1px solid rgba(255,195,64,0.1);border-radius:5px;padding:5px 8px;color:#f8f0e0;font-size:14px;" placeholder="Post title..."></div>'
      +'<div><div style="font-size:9px;letter-spacing:0.2em;color:#6b5e44;font-family:Cormorant SC,serif;margin-bottom:3px;">FOCUS KEYWORD</div>'
      +'<input id="be-kw" oninput="admAnalyseSEO()" style="width:100%;background:#030108;border:1px solid rgba(255,195,64,0.1);border-radius:5px;padding:5px 8px;color:#f8f0e0;font-size:14px;" placeholder="e.g. Sade Sati"></div>'
      +'<div><div style="font-size:9px;letter-spacing:0.2em;color:#6b5e44;font-family:Cormorant SC,serif;margin-bottom:3px;">AUTHOR</div>'
      +'<input id="be-author" value="Jyogi" style="width:100%;background:#030108;border:1px solid rgba(255,195,64,0.1);border-radius:5px;padding:5px 8px;color:#f8f0e0;font-size:14px;"></div>'
      +'<div><div style="font-size:9px;letter-spacing:0.2em;color:#6b5e44;font-family:Cormorant SC,serif;margin-bottom:3px;">DATE</div>'
      +'<input id="be-date" value="'+today+'" style="width:100%;background:#030108;border:1px solid rgba(255,195,64,0.1);border-radius:5px;padding:5px 8px;color:#f8f0e0;font-size:14px;"></div>'
    +'</div>'

    // Toolbar — uses data attributes, wired by JS above
    +'<div style="padding:5px 10px;border-bottom:1px solid rgba(255,195,64,0.06);display:flex;gap:2px;align-items:center;flex-wrap:wrap;background:#0f0428;flex-shrink:0;">'
      +'<button data-fmt="# " style="padding:3px 8px;border-radius:4px;border:none;background:transparent;color:#8a7355;cursor:pointer;font-size:10px;font-family:Cormorant SC,serif;">H1</button>'
      +'<button data-fmt="## " style="padding:3px 8px;border-radius:4px;border:none;background:transparent;color:#8a7355;cursor:pointer;font-size:10px;font-family:Cormorant SC,serif;">H2</button>'
      +'<button data-fmt="### " style="padding:3px 8px;border-radius:4px;border:none;background:transparent;color:#8a7355;cursor:pointer;font-size:10px;font-family:Cormorant SC,serif;">H3</button>'
      +'<span style="color:rgba(255,255,255,0.08);padding:0 2px;">|</span>'
      +'<button data-wrap="**" style="padding:3px 8px;border-radius:4px;border:none;background:transparent;color:#8a7355;cursor:pointer;font-size:12px;font-weight:bold;">B</button>'
      +'<button data-wrap="*" style="padding:3px 8px;border-radius:4px;border:none;background:transparent;color:#8a7355;cursor:pointer;font-size:12px;font-style:italic;">I</button>'
      +'<span style="color:rgba(255,255,255,0.08);padding:0 2px;">|</span>'
      +'<button data-fmt="> " style="padding:3px 8px;border-radius:4px;border:none;background:transparent;color:#8a7355;cursor:pointer;font-size:13px;">&ldquo;</button>'
      +'<button data-fmt="- " style="padding:3px 8px;border-radius:4px;border:none;background:transparent;color:#8a7355;cursor:pointer;font-size:14px;">&#8226;</button>'
      +'<button data-ins="\n---\n" style="padding:3px 8px;border-radius:4px;border:none;background:transparent;color:#8a7355;cursor:pointer;font-size:12px;">&#8212;</button>'
      +'<span style="color:rgba(255,255,255,0.08);padding:0 2px;">|</span>'
      +'<button onclick="admInsertImage()" style="padding:3px 10px;border-radius:4px;border:1px solid rgba(255,195,64,0.15);background:transparent;color:#FFC340;cursor:pointer;font-size:11px;font-family:Cormorant SC,serif;">+ Image</button>'
      +'<button data-ins="\n> **Key fact:** Write your key insight here.\n" style="padding:3px 10px;border-radius:4px;border:1px solid rgba(45,212,191,0.2);background:transparent;color:#2dd4bf;cursor:pointer;font-size:11px;font-family:Cormorant SC,serif;">+ Fact</button>'
      +'<button data-ins="\n---\n**Ready for a reading?** [Book on WhatsApp](https://wa.me/919437794561)\n---\n" style="padding:3px 10px;border-radius:4px;border:1px solid rgba(167,139,250,0.2);background:transparent;color:#a78bfa;cursor:pointer;font-size:11px;font-family:Cormorant SC,serif;">+ CTA</button>'
      +'<span style="flex:1;"></span>'
      +'<span id="be-wc" style="font-size:11px;color:#6b5e44;font-family:Cormorant SC,serif;margin-right:8px;">0 words</span>'
      +'<span id="be-save-ind" style="font-size:11px;"></span>'
    +'</div>'

    // Writing area
    +'<textarea id="be-editor" oninput="admAnalyseSEO()" spellcheck="true"'
    +' style="flex:1;width:100%;background:transparent;border:none;outline:none;color:#f8f0e0;font-family:Cormorant Garamond,Georgia,serif;font-size:17px;line-height:1.85;resize:none;padding:24px 28px;caret-color:#FFC340;"'
    +' placeholder="Start writing your article here...&#10;&#10;## First Section Heading&#10;&#10;Write your paragraphs. Use the toolbar above for headings, bold, images.&#10;&#10;The SEO score on the right updates as you write."></textarea>'

    // Bottom action bar
    +'<div style="padding:8px 14px;border-top:1px solid rgba(255,195,64,0.07);display:flex;gap:8px;justify-content:flex-end;align-items:center;background:#0f0428;flex-shrink:0;">'
      +'<span style="flex:1;font-size:11px;color:#6b5e44;font-family:Cormorant SC,serif;">Cmd+S to save · auto-saves every 3s</span>'
      +'<button onclick="admSaveBlogPost()" style="padding:6px 16px;border-radius:16px;border:1px solid rgba(255,195,64,0.25);background:transparent;color:#FFC340;cursor:pointer;font-size:12px;font-family:Cormorant SC,serif;letter-spacing:0.08em;">Save Draft</button>'
      +'<button onclick="admExportCurrent()" style="padding:6px 16px;border-radius:16px;border:none;background:linear-gradient(135deg,#2B7A0B,#1a5208);color:#fff;cursor:pointer;font-size:12px;font-family:Cormorant SC,serif;letter-spacing:0.08em;">&#8595; Export HTML</button>'
    +'</div>'
  +'</div>'

  // ── RIGHT: SEO panel ──────────────────────────────────────
  +'<div style="border-left:1px solid rgba(255,195,64,0.1);overflow-y:auto;padding:14px;background:#04010b;">'
    +'<div style="font-size:9px;letter-spacing:0.22em;color:#6b5e44;font-family:Cormorant SC,serif;margin-bottom:10px;">SEO SCORE</div>'
    +'<div style="display:flex;align-items:center;gap:10px;padding:10px 12px;background:rgba(255,195,64,0.03);border:1px solid rgba(255,195,64,0.08);border-radius:10px;margin-bottom:14px;">'
      +'<span id="be-seo-score" style="font-size:28px;font-family:Cinzel,serif;color:#8a7355;min-width:40px;">0</span>'
      +'<div style="flex:1;">'
        +'<div style="font-size:10px;color:#6b5e44;margin-bottom:5px;">out of 100</div>'
        +'<div style="height:3px;background:rgba(255,255,255,0.05);border-radius:2px;">'
          +'<div id="be-seo-bar" style="height:100%;border-radius:2px;width:0%;transition:width 0.4s;"></div>'
        +'</div>'
      +'</div>'
    +'</div>'
    +'<div id="be-seo-checks" style="margin-bottom:14px;"></div>'
    +'<div style="font-size:9px;letter-spacing:0.22em;color:#6b5e44;font-family:Cormorant SC,serif;margin-bottom:6px;">META DESCRIPTION</div>'
    +'<textarea id="be-desc" rows="3" style="width:100%;background:#030108;border:1px solid rgba(255,195,64,0.08);border-radius:7px;padding:7px 9px;color:#c4a97a;font-size:12px;line-height:1.5;resize:none;" placeholder="120-155 char Google summary..."></textarea>'
    +'<div id="be-desc-count" style="font-size:10px;color:#6b5e44;margin:3px 0 14px;">0 / 155</div>'
    +'<div style="font-size:9px;letter-spacing:0.22em;color:#6b5e44;font-family:Cormorant SC,serif;margin-bottom:8px;">AI SEARCH TIPS</div>'
    +'<div style="font-size:11px;color:#6b5e44;line-height:1.9;padding:10px;background:rgba(255,255,255,0.02);border-radius:8px;">'
      +'&#x2726; Answer Who/What/Why/How directly<br>'
      +'&#x2726; Name planets, texts, techniques<br>'
      +'&#x2726; Sentences under 20 words<br>'
      +'&#x2726; Add 2+ external source links<br>'
      +'&#x2726; Keyword in first paragraph'
    +'</div>'
  +'</div>'

  +'</div>';
}


function admSaveBlogPost(){
  var title=document.getElementById('be-title').value.trim();
  var kw=document.getElementById('be-kw').value.trim();
  var desc=document.getElementById('be-desc').value.trim();
  var content=document.getElementById('be-editor').value;
  var author=document.getElementById('be-author').value.trim()||'Jyogi';
  var date=document.getElementById('be-date').value.trim();
  var slug=title.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');

  if(!title){alert('Add a title first.');return;}

  // Save to localStorage
  var posts=JSON.parse(localStorage.getItem('jyogi_blog_posts')||'[]');
  var existing=posts.findIndex(function(p){return p.slug===slug;});
  var post={slug:slug,title:title,kw:kw,desc:desc,content:content,author:author,date:date,saved:new Date().toISOString()};
  if(existing>=0) posts[existing]=post; else posts.unshift(post);
  localStorage.setItem('jyogi_blog_posts',JSON.stringify(posts));

  // Show saved indicator
  var ind=document.getElementById('be-save-ind');
  if(ind){ind.textContent='✓ Saved';ind.style.color='#86efac';setTimeout(function(){ind.textContent='';},2000);}

  admLoadPosts();
  admAnalyseSEO();
}

function admLoadPosts(){
  var posts=JSON.parse(localStorage.getItem('jyogi_blog_posts')||'[]');
  var list=document.getElementById('be-post-list');
  if(!list) return;
  if(!posts.length){list.innerHTML='<div style="color:#8a7355;font-size:13px;font-style:italic;padding:8px 0;">No posts yet — write your first one</div>';return;}
  list.innerHTML=posts.map(function(p,i){
    return '<div style="display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid rgba(255,195,64,0.08);">'+
      '<span style="flex:1;font-size:13px;color:#c4a97a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'+p.title+'</span>'+
      '<button onclick="admLoadPost('+i+')" style="padding:3px 10px;border-radius:12px;border:1px solid rgba(255,195,64,0.2);background:transparent;color:#FFC340;cursor:pointer;font-size:11px;">Edit</button>'+
      '<button onclick="admExportPost('+i+')" style="padding:3px 10px;border-radius:12px;border:none;background:rgba(74,222,128,0.1);color:#86efac;cursor:pointer;font-size:11px;">Export</button>'+
      '<button onclick="admDeletePost('+i+')" style="padding:3px 8px;border-radius:12px;border:none;background:rgba(248,113,113,0.1);color:#f87171;cursor:pointer;font-size:11px;">✕</button>'+
    '</div>';
  }).join('');
}

function admLoadPost(idx){
  var posts=JSON.parse(localStorage.getItem('jyogi_blog_posts')||'[]');
  var p=posts[idx];
  if(!p) return;
  document.getElementById('be-title').value=p.title||'';
  document.getElementById('be-kw').value=p.kw||'';
  document.getElementById('be-desc').value=p.desc||'';
  document.getElementById('be-editor').value=p.content||'';
  document.getElementById('be-author').value=p.author||'Jyogi';
  document.getElementById('be-date').value=p.date||'';
  admAnalyseSEO();
}

function admDeletePost(idx){
  if(!confirm('Delete this post?')) return;
  var posts=JSON.parse(localStorage.getItem('jyogi_blog_posts')||'[]');
  posts.splice(idx,1);
  localStorage.setItem('jyogi_blog_posts',JSON.stringify(posts));
  admLoadPosts();
}

function admNewPost(){
  ['be-title','be-kw','be-desc','be-editor'].forEach(function(id){
    var el=document.getElementById(id);
    if(el) el.value='';
  });
  document.getElementById('be-editor').focus();
}

function admExportPost(idx){
  var posts=JSON.parse(localStorage.getItem('jyogi_blog_posts')||'[]');
  var p=posts[idx]||{title:'',content:'',desc:'',author:'Jyogi',date:''};
  admDownloadHTML(p.title,p.content,p.desc,p.author,p.date);
}

function admExportCurrent(){
  var title=document.getElementById('be-title').value.trim();
  var content=document.getElementById('be-editor').value;
  var desc=document.getElementById('be-desc').value.trim();
  var author=document.getElementById('be-author').value.trim()||'Jyogi';
  var date=document.getElementById('be-date').value.trim();
  admDownloadHTML(title,content,desc,author,date);
}

function admDownloadHTML(title,content,desc,author,date){
  var slug=(title||'blog-post').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
  var body=admMdToHtml(content);
  var html='<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<title>'+admEsc(title)+' | Jyogi</title>\n<meta name="description" content="'+admEsc(desc)+'">\n<meta name="author" content="'+admEsc(author)+'">\n<meta name="robots" content="index, follow">\n<link rel="canonical" href="https://jyogi.in/blog/'+slug+'.html">\n<meta property="og:title" content="'+admEsc(title)+' | Jyogi">\n<meta property="og:description" content="'+admEsc(desc)+'">\n<meta property="og:url" content="https://jyogi.in/blog/'+slug+'.html">\n<meta property="og:image" content="https://jyogi.in/images/og-image.jpg">\n<meta property="og:type" content="article">\n<script type="application/ld+json">\n{"@context":"https://schema.org","@type":"BlogPosting","headline":"'+admEsc(title)+'","author":{"@type":"Person","name":"'+admEsc(author)+'"},"datePublished":"'+new Date().toISOString().split("T")[0]+'","publisher":{"@type":"Organization","name":"Jyogi","url":"https://jyogi.in"},"description":"'+admEsc(desc)+'"}\n<\/script>\n<link rel="preconnect" href="https://fonts.googleapis.com">\n<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=Cormorant+SC:wght@400&display=swap" rel="stylesheet">\n<style>\n:root{--bg:#03010a;--bg2:#060112;--card:#0f0428;--gold:#FFC340;--gold-lt:#ffe9a3;--text:#f8f0e0;--muted:#c4a97a;--dim:#8a7355;--border:rgba(255,195,64,0.12);--teal:#2dd4bf;}\n*{margin:0;padding:0;box-sizing:border-box;}\nbody{background:var(--bg);color:var(--text);font-family:\'Cormorant Garamond\',Georgia,serif;font-size:19px;line-height:1.9;overflow-x:hidden;}\na{color:var(--teal);}\nnav{position:sticky;top:0;z-index:100;background:rgba(3,1,10,0.95);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);padding:14px 24px;display:flex;align-items:center;justify-content:space-between;}\n.nav-logo{font-family:\'Cinzel\',serif;font-size:20px;color:var(--gold);letter-spacing:0.1em;}\n.nav-back{font-size:14px;color:var(--muted);}\n.nav-back:hover{color:var(--gold);}\n.hero{padding:64px 24px 48px;background:linear-gradient(180deg,var(--bg2),var(--bg));text-align:center;border-bottom:1px solid var(--border);}\n.atag{display:inline-block;background:rgba(255,195,64,0.08);border:1px solid rgba(255,195,64,0.2);border-radius:100px;padding:5px 18px;font-size:11px;letter-spacing:0.25em;color:var(--gold);font-family:\'Cormorant SC\',serif;margin-bottom:20px;}\n.hero h1{font-family:\'Cinzel\',serif;font-size:clamp(22px,4vw,40px);font-weight:400;line-height:1.2;max-width:700px;margin:0 auto 14px;}\n.byline{font-size:13px;color:var(--dim);font-family:\'Cormorant SC\',serif;letter-spacing:0.1em;}\narticle{max-width:700px;margin:0 auto;padding:52px 24px 80px;}\nh2{font-family:\'Cinzel\',serif;font-size:clamp(18px,2.8vw,26px);font-weight:400;color:var(--gold);margin:48px 0 16px;}\nh3{font-family:\'Cinzel\',serif;font-size:17px;font-weight:400;color:var(--muted);margin:32px 0 12px;}\np{margin-bottom:22px;color:var(--muted);}\nstrong{color:var(--gold-lt);font-weight:600;}\nblockquote{margin:28px 0;padding:18px 22px;border-left:3px solid var(--gold);background:rgba(255,195,64,0.04);border-radius:0 10px 10px 0;font-style:italic;font-size:19px;color:var(--muted);}\nhr{border:none;height:1px;background:linear-gradient(90deg,transparent,rgba(255,195,64,0.2),transparent);margin:36px 0;}\nul{padding-left:22px;margin-bottom:20px;}\nli{margin-bottom:6px;color:var(--muted);}\nimg{max-width:100%;border-radius:12px;margin:20px 0;display:block;}\n.img-caption{font-size:13px;color:var(--dim);text-align:center;font-style:italic;margin-top:-12px;margin-bottom:20px;}\n.blog-nav{display:flex;justify-content:space-between;padding:16px 24px;border-top:1px solid var(--border);}\n.blog-nav a{font-family:\'Cormorant SC\',serif;font-size:12px;letter-spacing:0.12em;color:var(--muted);}\n.blog-nav a:hover{color:var(--gold);}\nfooter{text-align:center;padding:32px 24px;border-top:1px solid var(--border);font-size:13px;color:var(--dim);font-family:\'Cormorant SC\',serif;}\nfooter a{color:var(--gold);}\n@media(max-width:600px){article{padding:36px 18px 60px;}}\n</style>\n</head>\n<body>\n<nav>\n  <a href="../index.html" class="nav-back">← Jyogi</a>\n  <a href="../index.html" class="nav-logo">Jyogi</a>\n  <a href="index.html" style="font-family:\'Cormorant SC\',serif;font-size:11px;color:var(--dim);letter-spacing:0.2em;">BLOG</a>\n</nav>\n<div class="hero">\n  <div class="atag">✦ JYOTISH INSIGHTS ✦</div>\n  <h1>'+admEsc(title)+'</h1>\n  <div class="byline">'+admEsc(author)+' · '+admEsc(date)+'</div>\n</div>\n<article>\n'+body+'\n</article>\n<div class="blog-nav">\n  <a href="index.html">← All Posts</a>\n  <a href="../index.html">Jyogi.in →</a>\n</div>\n<footer>© 2026 <a href="../index.html">Jyogi.in</a> · Vedic Astrology · Tarot · Sacred Crystals</footer>\n</body>\n</html>';

  var blob=new Blob([html],{type:'text/html'});
  var a=document.createElement('a');
  a.href=URL.createObjectURL(blob);
  a.download=slug+'.html';
  a.click();
}

function admMdToHtml(md){
  if(!md) return '';
  var t=md;
  t=t.replace(/^### (.+)$/gm,'<h3>$1</h3>');
  t=t.replace(/^## (.+)$/gm,'<h2>$1</h2>');
  t=t.replace(/^# (.+)$/gm,'<h2>$1</h2>');
  t=t.replace(/^---$/gm,'<hr>');
  t=t.replace(/^> (.+)$/gm,'<blockquote>$1</blockquote>');
  t=t.replace(/^[-*] (.+)$/gm,'<li>$1</li>');
  t=t.replace(/(<li>[\s\S]*?<\/li>)/g,'<ul>$1</ul>');
  t=t.replace(/<\/ul>\s*<ul>/g,'');
  t=t.replace(/!\[([^\]]*)\]\(([^)]+)\)/g,'<img src="$2" alt="$1" loading="lazy"><div class="img-caption">$1</div>');
  t=t.replace(/\[([^\]]+)\]\(([^)]+)\)/g,'<a href="$2" target="_blank">$1</a>');
  t=t.split('\n').map(function(l){
    if(/^<(h[23]|ul|ol|li|blockquote|hr|img|div)/.test(l.trim())) return l;
    if(!l.trim()) return '';
    l=l.replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>');
    l=l.replace(/\*(.+?)\*/g,'<em>$1</em>');
    return '<p>'+l+'</p>';
  }).join('\n');
  t=t.replace(/<p>\s*<\/p>/g,'');
  return t;
}

function admEsc(s){ return (s||'').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

function admInsertImage(){
  var url=prompt('Image URL or path (e.g. image/my-photo.jpg):');
  if(!url) return;
  var alt=prompt('Alt text (describe the image):','') || '';
  var ta=document.getElementById('be-editor');
  var pos=ta.selectionStart;
  var ins='\n!['+alt+']('+url+')\n';
  ta.value=ta.value.slice(0,pos)+ins+ta.value.slice(pos);
  ta.selectionStart=ta.selectionEnd=pos+ins.length;
  ta.focus();
  admAnalyseSEO();
}

function admFmt(prefix){
  var ta=document.getElementById('be-editor');
  var s=ta.selectionStart;
  var lineStart=ta.value.lastIndexOf('\n',s-1)+1;
  ta.value=ta.value.slice(0,lineStart)+prefix+ta.value.slice(lineStart);
  ta.selectionStart=ta.selectionEnd=lineStart+prefix.length;
  ta.focus(); admAnalyseSEO();
}

function admWrap(b,a){
  var ta=document.getElementById('be-editor');
  var s=ta.selectionStart,e=ta.selectionEnd;
  var sel=ta.value.slice(s,e)||'text';
  ta.value=ta.value.slice(0,s)+b+sel+a+ta.value.slice(e);
  ta.selectionStart=s+b.length;ta.selectionEnd=s+b.length+sel.length;
  ta.focus(); admAnalyseSEO();
}

function admIns(text){
  var ta=document.getElementById('be-editor');
  var s=ta.selectionStart;
  ta.value=ta.value.slice(0,s)+text+ta.value.slice(s);
  ta.selectionStart=ta.selectionEnd=s+text.length;
  ta.focus(); admAnalyseSEO();
}

function admAnalyseSEO(){
  var title=(document.getElementById('be-title')||{}).value||'';
  var kw=(document.getElementById('be-kw')||{}).value||'';
  var body=(document.getElementById('be-editor')||{}).value||'';
  var bodyLow=body.toLowerCase();
  var titleLow=title.toLowerCase();
  var words=body.trim()?body.trim().split(/\s+/).length:0;
  var kwParts=kw.toLowerCase().split(/[,\s]+/).filter(Boolean);
  var score=0;
  var checks=[];

  function c(ok,label,detail,pts){
    checks.push({ok:ok,label:label,detail:detail});
    if(ok) score+=pts;
  }

  c(title.length>=30&&title.length<=65,'Title (30–65 chars)',title.length?title.length+' chars':'Add a title',15);
  c(kw&&kwParts.some(function(k){return titleLow.includes(k);}),
    'Keyword in title',!kw?'Set focus keyword':kwParts.some(function(k){return titleLow.includes(k);})?'✓ Found':'Not in title — add it',15);
  c(words>=800,'Word count (800+ words)',words+' words'+(words<800?' — keep writing':''),15);
  c(kw&&bodyLow.includes(kwParts[0]),'Keyword in body',!kw?'Set keyword':bodyLow.includes(kwParts[0])?'✓ Found in body':'Missing from body',15);
  c(/^## /m.test(body),'H2 headings',/^## /m.test(body)?'✓ Found':'Add ## section headings',15);
  var metaLen=(document.getElementById('be-desc')||{value:''}).value.trim().length;
  c(metaLen>=120&&metaLen<=155,'Meta description',metaLen?metaLen+' chars (aim 120–155)':'Write meta description',15);
  c(/\[.+?\]\(https?:\/\//.test(body),'External links',/\[.+?\]\(https?:\/\//.test(body)?'✓ Links found':'Add at least 2 source links',10);

  var pct=Math.min(100,score);
  var seoEl=document.getElementById('be-seo-score');
  var barEl=document.getElementById('be-seo-bar');
  var colour=pct>=80?'#86efac':pct>=50?'#FFC340':'#f87171';
  if(seoEl){seoEl.textContent=pct+'/100';seoEl.style.color=colour;}
  if(barEl){barEl.style.width=pct+'%';barEl.style.background=colour;}

  var chEl=document.getElementById('be-seo-checks');
  if(chEl) chEl.innerHTML=checks.map(function(ch){
    var col=ch.ok?'#86efac':'#f87171';
    var sym=ch.ok?'✓':'✗';
    return '<div style="display:flex;gap:8px;padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.04);font-size:12px;line-height:1.5;">'+
      '<span style="color:'+col+';min-width:12px;">'+sym+'</span>'+
      '<span style="color:#c4a97a;"><span style="color:#f8f0e0;">'+ch.label+'</span><br>'+ch.detail+'</span>'+
    '</div>';
  }).join('');

  // Word count
  var wcEl=document.getElementById('be-wc');
  if(wcEl){
    var mins=Math.max(1,Math.ceil(words/200));
    wcEl.textContent=words.toLocaleString()+' words · '+mins+' min read';
  }

  // Auto-save
  clearTimeout(window.beTimer);
  window.beTimer=setTimeout(admSaveBlogPost,3000);
}

async function admRefresh(){
  const tbl=document.getElementById('adm-table');
  const note=document.getElementById('adm-note');
  if(!tbl) return;

  // ── STEP 1: Show local logs IMMEDIATELY ───────────────────────────────────
  const localData = getLocalLogs();
  if(localData.length){
    admRenderTable(localData, '📱 Local device (instant)');
    note.style.color='#FFC340';
  } else {
    tbl.innerHTML='<p style="color:#9d8c6a;text-align:center;padding:20px;font-style:italic;">📱 No local logs yet. Trying server…</p>';
  }

  // ── STEP 2: Try server with timeout ──────────────────────────────────────
  const statusEl = document.getElementById('adm-server-status');
  if(statusEl) statusEl.textContent='⏳ Connecting to server…';

  try{
    const ctrl = new AbortController();
    const timeout = setTimeout(()=>ctrl.abort(), 12000);
    const r = await fetch(API_BASE+'/api/logs?secret='+LOG_SECRET+'&format=json',{signal:ctrl.signal});
    clearTimeout(timeout);
    if(!r.ok) throw new Error('HTTP '+r.status);
    const serverData = await r.json();
    // Merge: server is authoritative, but add any local entries not on server
    const serverEpochs = new Set(serverData.map(e=>e.ts_epoch));
    const localOnly = localData.filter(e=>e.ts_epoch && !serverEpochs.has(e.ts_epoch));
    const merged = [...serverData, ...localOnly];
    // Re-save merged back to localStorage
    saveLocalLogs(merged);
    admRenderTable(merged, '☁️ Server + Local ('+serverData.length+' server, '+localOnly.length+' local-only)');
    if(statusEl) statusEl.textContent='✅ Server connected';
    note.style.color='#34d399';
  } catch(err){
    // Server failed — already showing local data
    const isTimeout = err.name==='AbortError';
    const msg = isTimeout
      ? '⚠️ Server timeout (Render sleeping) — showing '+localData.length+' local log(s). Render wakes in ~30s.'
      : '⚠️ Server unreachable — showing '+localData.length+' local log(s). Error: '+err.message;
    if(statusEl) statusEl.textContent = isTimeout ? '💤 Server sleeping (free tier)' : '❌ Server offline';
    if(note){
      note.style.color='#f59e0b';
      if(!localData.length) note.textContent=msg;
      else note.textContent=localData.length+' local submission(s) shown. Server offline.';
    }
    if(!localData.length && tbl){
      tbl.innerHTML='<div style="text-align:center;padding:40px;">'+
        '<p style="color:#f59e0b;font-size:15px;margin-bottom:12px;">'+
        (isTimeout?'💤 Render server is sleeping (free tier cold start)':'❌ Cannot reach server')+
        '</p>'+
        '<p style="color:#6b5e44;font-size:13px;">'+
        (isTimeout?'Wait ~30 seconds and click Refresh. Or visit <a href="'+API_BASE+'/api/logs?secret='+LOG_SECRET+'&format=json" target="_blank" style="color:#FFC340;">server directly</a>.':'Check Render dashboard for errors.')+
        '</p></div>';
    }
  }
}

function admDownload(fmt){
  // Try server first, fall back to local download
  const localData = getLocalLogs();
  if(fmt==='csv'){
    // Build CSV from local data if server is unreachable
    const cols=['ts','type','name','dob','time','city','question','lagna','moon','nakshatra'];
    let csv=cols.join(',')+'\n';
    localData.forEach(e=>{csv+=cols.map(c=>'"'+(String(e[c]||'')).replace(/"/g,'""')+'"').join(',')+'\n';});
    const blob=new Blob([csv],{type:'text/csv'});
    const a=document.createElement('a');
    a.href=URL.createObjectURL(blob);
    a.download='jyogi_logs_'+new Date().toISOString().slice(0,10)+'.csv';
    a.click();
    return;
  }
  if(fmt==='json'){
    const blob=new Blob([JSON.stringify(localData,null,2)],{type:'application/json'});
    const a=document.createElement('a');
    a.href=URL.createObjectURL(blob);
    a.download='jyogi_logs_'+new Date().toISOString().slice(0,10)+'.json';
    a.click();
    return;
  }
  window.open(API_BASE+'/api/logs?secret='+LOG_SECRET+'&format='+fmt,'_blank');
}

function admClearLocal(){
  const n = getLocalLogs().length;
  if(!confirm('Delete '+n+' locally stored events? Server logs (if any) remain safe.')) return;
  localStorage.removeItem(LS_KEY);
  CLIENT_LOG.length=0;
  admRefresh();
}


// ─── WHATSAPP ─────────────────────────────────────────────────────────────
function openWhatsApp(msg){
  // Log every WhatsApp booking click
  saveLog({ type:'whatsapp_booking', message: msg.slice(0,120) });
  window.location.href=`https://wa.me/${WA_NUMBER}?text=${encodeURIComponent(msg)}`;
}

// ─── INIT ─────────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded',()=>{
  // Render all sections immediately — Safari IO can miss deferred sections
  renderServices();
  renderMuhurta();
  // Slight delay for below-fold to not block first paint
  setTimeout(()=>{
    renderShop();
    renderReviews();
    renderGallery();
  }, 200);
});

// ─── INTERSECTION OBSERVER (fade in) ──────────────────────────────────────
const observer=new IntersectionObserver((entries)=>{
  entries.forEach(e=>{
    if(e.isIntersecting){
      e.target.style.opacity='1';
      e.target.style.transform='translateY(0)';
    }
  });
},{threshold:0.1});

window.addEventListener('DOMContentLoaded',()=>{
  // Skip scroll animations on mobile — saves IntersectionObserver overhead
  if(window.innerWidth < 600) return;
  document.querySelectorAll('.service-card,.bracelet-card,.review-card,.god-card').forEach(el=>{
    el.style.opacity='0';el.style.transform='translateY(24px)';
    el.style.transition='opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
  });
});

// ── Custom Picker ─────────────────────────────────────────────────
var _MONTHS=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
var _pt=null;
function openPicker(t){
  _pt=t;
  const ov=document.getElementById('picker-overlay');
  const grid=document.getElementById('picker-items');
  const title=document.getElementById('picker-title');
  let items=[];
  if(t==='day'){
    title.textContent='Select Day';
    grid.className='picker-items g4';
    for(let d=1;d<=31;d++) items.push({v:String(d).padStart(2,'0'),l:String(d).padStart(2,'0')});
  } else if(t==='month'){
    title.textContent='Select Month';
    grid.className='picker-items g3';
    _MONTHS.forEach((m,i)=>items.push({v:String(i+1).padStart(2,'0'),l:m}));
  } else if(t==='year'){
    title.textContent='Select Year';
    grid.className='picker-items g4';
    for(let y=new Date().getFullYear();y>=1930;y--) items.push({v:String(y),l:String(y)});
  } else if(t==='hour'){
    title.textContent='Select Hour';
    grid.className='picker-items g4';
    for(let h=1;h<=12;h++) items.push({v:String(h),l:String(h).padStart(2,'0')});
  } else if(t==='min'){
    title.textContent='Select Minute';
    grid.className='picker-items g4';
    for(let m=0;m<60;m+=5) items.push({v:String(m).padStart(2,'0'),l:String(m).padStart(2,'0')});
  }
  const hidId=t==='day'?'dob-day':t==='month'?'dob-month':t==='year'?'dob-year':t==='hour'?'time-hour':'time-min';
  const curV=document.getElementById(hidId).value;
  grid.innerHTML=items.map(it=>{
    const sel=curV===it.v?' sel':'';
    return '<div class="pi'+sel+'" onclick="pickVal(this)" data-v="'+it.v+'" data-l="'+it.l+'">'+it.l+'</div>';
  }).join('');
  ov.classList.add('open');
  // Scroll to selected item after render
  setTimeout(()=>{
    const s=grid.querySelector('.sel');
    if(s) s.scrollIntoView({block:'center',behavior:'instant'});
  },80);
}
function pickVal(el){const v=el.dataset.v,l=el.dataset.l;
  if(_pt==='day'){document.getElementById('dob-day').value=v;setBtn('btn-day','lbl-day',l);}
  else if(_pt==='month'){document.getElementById('dob-month').value=v;setBtn('btn-month','lbl-month',l);}
  else if(_pt==='year'){document.getElementById('dob-year').value=v;setBtn('btn-year','lbl-year',l);}
  // hour/min handled by spinners
  closePicker();
}
function setBtn(btnId,lblId,l){
  document.getElementById(lblId).textContent=l;
  const b=document.getElementById(btnId);
  b.classList.remove('empty');b.classList.add('filled');
}
function closePicker(){document.getElementById('picker-overlay').classList.remove('open');_pt=null;}
function setAMPM(v){
  document.getElementById('time-ampm').value=v;
  document.getElementById('ampm-am').classList.toggle('active',v==='AM');
  document.getElementById('ampm-pm').classList.toggle('active',v==='PM');
}
window.addEventListener('popstate',closePicker);

// ── Scroll Spinners ───────────────────────────────────────────────
function buildSpinner(trackId, items, hiddenId, defaultVal){
  const track=document.getElementById(trackId);
  if(!track) return;
  // Build items
  track.innerHTML=items.map(v=>
    '<div class="spinner-item" data-val="'+v+'">'+v+'</div>'
  ).join('');
  // Scroll to default
  const defaultIdx=items.indexOf(defaultVal);
  if(defaultIdx>=0){
    // Use 150ms timeout + dynamic height so CSS has applied before scroll
    setTimeout(()=>{
      // Use offsetHeight (more reliable than getBoundingClientRect for hidden elements)
      const firstItem=track.querySelector('.spinner-item');
      const itemH=firstItem?(firstItem.offsetHeight||firstItem.getBoundingClientRect().height):0;
      // Validate: must be between 30-80px; fall back to CSS-defined value
      const ITEM_H=48; // matches CSS .spinner-item height
      const itemHSafe=(itemH>=30&&itemH<=80)?itemH:ITEM_H;
      window._spinnerItemH=itemHSafe; // cache for snapSpinner
      track.scrollTop=defaultIdx*itemHSafe;
      document.getElementById(hiddenId).value=defaultVal;
      updateSpinnerActive(track,hiddenId);
    },300);
  }
  // On scroll update hidden input + highlight
  let scrollTimer;
  track.addEventListener('scroll',()=>{
    clearTimeout(scrollTimer);
    scrollTimer=setTimeout(()=>{
      snapSpinner(track,hiddenId,items);
    },80);
  },{passive:true});
}

function snapSpinner(track,hiddenId,items){
  // Use cached height from buildSpinner (avoids reflow; more accurate)
  const firstItem=track.querySelector('.spinner-item');
  const measured=firstItem?(firstItem.offsetHeight||firstItem.getBoundingClientRect().height):0;
  const ITEM_H=48;
  const itemHSafe=(measured>=30&&measured<=80)?measured:(window._spinnerItemH||ITEM_H);
  const idx=Math.round(track.scrollTop/itemHSafe);
  const snapped=Math.max(0,Math.min(items.length-1,idx));
  track.scrollTo({top:snapped*itemHSafe,behavior:'smooth'});
  const val=items[snapped];
  document.getElementById(hiddenId).value=val;
  updateSpinnerActive(track,hiddenId);
}

function updateSpinnerActive(track,hiddenId){
  const cur=document.getElementById(hiddenId).value;
  track.querySelectorAll('.spinner-item').forEach(el=>{
    el.classList.toggle('active',el.dataset.val===cur);
  });
}

function initSpinners(){
  // Hours: 01–12
  const hours=[];
  for(let h=1;h<=12;h++) hours.push(String(h).padStart(2,'0'));
  buildSpinner('spin-hour-track', hours, 'time-hour', '08');

  // Minutes: 00–59 every 1 minute
  const mins=[];
  for(let m=0;m<60;m++) mins.push(String(m).padStart(2,'0'));
  buildSpinner('spin-min-track', mins, 'time-min', '00');
}
// Init spinners after fonts loaded for accurate offsetHeight measurement
if(document.fonts && document.fonts.ready){
  document.fonts.ready.then(initSpinners);
} else {
  setTimeout(initSpinners, 100); // simple defer — works on all browsers incl Safari
}



// ── North Indian Kundli Chart ─────────────────────────────────────
// ════════════════════════════════════════════════════════════════
// NORTH INDIAN KUNDALI — Full diagonals + inner diamond geometry
// Matches reference chart exactly. All text centered on cell centroid.
// H1 (inner-top kite) = Lagna. Anti-clockwise numbering 1-12.
// ════════════════════════════════════════════════════════════════
