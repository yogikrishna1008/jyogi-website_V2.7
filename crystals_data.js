/*
 * ═══════════════════════════════════════════════════════════════════════
 * crystals_data.js — Single source of truth for the crystal bracelet catalogue.
 *
 * BOTH index.html AND crystals.html load this file via <script src="...">.
 * Edit ONCE here, both pages reflect changes.
 *
 * To update stock status: change stock:'in_stock' or stock:'made_to_order'
 * To add multi-image gallery: add gallery:['url1','url2',...] to a bracelet
 * To add a new product: copy any entry, change the fields.
 * ═══════════════════════════════════════════════════════════════════════
 */

/**
 * CRYSTAL_SLUGS — maps each bracelet id to its static product-page URL.
 * Used by index.html renderShop() and crystals.html renderGrid() so both
 * pages link cards to /crystals/{slug}.html.
 * Kept here alongside BRACELETS so adding a new product in one place
 * automatically updates slugs too.
 */
const CRYSTAL_SLUGS = {
  seven_chakra:        'crystals/seven-chakra-bracelet.html',
  shani_bracelet:      'crystals/shani-bracelet.html',
  money_magnet:        'crystals/money-magnet-bracelet.html',
  pyrite_solo:         'crystals/pyrite-power-bracelet.html',
  rose_quartz_love:    'crystals/love-marriage-bracelet.html',
  moonstone_pearl:     'crystals/divine-feminine-bracelet.html',
  green_aventurine:    'crystals/lucky-charm-bracelet.html',
  black_tourmaline:    'crystals/protection-shield-bracelet.html',
  lepidolite_amethyst: 'crystals/burnout-recovery-bracelet.html',
  tourmaline_cluster:  'crystals/tech-defender-bracelet.html',
  tiger_eye_solo:      'crystals/tiger-eye-courage-bracelet.html',
  fluorite_clear:      'crystals/focus-scholar-bracelet.html',
  lapis_amethyst:      'crystals/third-eye-awakener-bracelet.html',
  sunstone_bronzite:   'crystals/executive-presence-bracelet.html',
  
};

const BRACELETS = [

    // ════ SHANI REMEDY (Saturn protection, grounding & career growth) ════
  {id:'shani_bracelet',name:'Shani Protection & Career Bracelet',sub:'Lapis Lazuli, Amethyst, Black Obsidian, Hematite & Pyrite',tagline:'Saturn protection, grounding & career growth.',
    price:'₹1,099',original:'₹1,799',planet:'Saturn',chakra:'Third Eye / Root',chakraColor:'#1a1a6e',
    badge:'Introductory Price',badgeColor:'#1a1a6e',category:'protection',stock:'made_to_order',
    benefits:['Saturn transit protection','Discipline & focus','Career & financial growth','Karmic clarity','Sade Sati relief','Psychic shielding'],
    vedicUse:'For Sade Sati, Saturn Mahadasha, weak or afflicted Shani in chart, Dhaiya periods, or 7th/8th house Saturn transits. Astrologically selected 5-stone combination aligned with Saturn energy.',
    ritual:'Wear on left wrist on Saturday during Shani Hora. Cleanse under cold running water before first wear. Chant Om Sham Shanaishcharaya Namah 108 times facing West at dusk.',
    gallery:['image/opt/shani_bracelet-640.jpg','image/opt/shani_bracelet_2-640.jpg','image/opt/shani_bracelet_3-640.jpg'],
    img:'image/opt/shani_bracelet-640.jpg',
    msg:'Hi Jyogi! I want to order the Shani Protection & Career Bracelet (₹1,099). Please guide me.'},

  
  // ════ TIER 2: BESTSELLER WEALTH (highest demand category) ════
  {id:'money_magnet',name:'Money Magnet',sub:'4-Stone Wealth Combo',tagline:'Attract wealth. Amplify abundance.',
    price:'₹1,199',original:'₹1,499',planet:'Jupiter / Sun',chakra:'Solar Plexus',chakraColor:'#FFD700',
    badge:'Best Seller',badgeColor:'#2B7A0B',category:'wealth',stock:'in_stock',
    benefits:['Wealth & prosperity','Career growth','Confidence boost','Abundance mindset'],
    vedicUse:'For weak Jupiter, Mahapurusha yogas malefic, Saturn Mahadasha financial stress, or 2nd/11th house issues.',
    ritual:'Wear on left wrist on Thursday morning. Chant Om Shreem Hreem Kleem 108 times facing East.',
    gallery:['image/opt/money_magnet-640.jpg','image/opt/money_magnet_2-640.jpg','image/opt/money_magnet_3-640.jpg','image/opt/money_magnet_4-640.jpg'],
    img:'image/opt/money_magnet-640.jpg',
    msg:'Hi Jyogi! I want to order the Money Magnet bracelet (₹1,199). Please guide me.'},
  
      // ════ TIER 1: ENTRY GIFTING (high volume, gateway product) ════
  {id:'seven_chakra',name:'Seven Chakra',sub:'7 Stones + Evil Eye',tagline:'Balance all chakras. Daily protection.',
    price:'₹799',original:'₹999',planet:'All Navagraha',chakra:'All 7 Chakras',chakraColor:'#9B59B6',
    badge:'Most Popular',badgeColor:'#2B7A0B',category:'wellness',stock:'in_stock',
    benefits:['Balances all 7 chakras','Evil eye protection','Daily energy alignment','Gift-perfect'],
    vedicUse:'Universal remedy when multiple planets are weak or transitioning. Safe daily wear.',
    ritual:'Wear daily on the left wrist. Cleanse weekly under moonlight or with selenite.',
    gallery:['image/opt/seven_chakra-640.jpg','image/opt/seven_chakra_2-640.jpg','image/opt/seven_chakra_3-640.jpg'],
    img:'image/opt/seven_chakra-640.jpg',
    msg:'Hi Jyogi! I want to order the Seven Chakra + Evil Eye bracelet (₹599). Please guide me.'},


    {id:'dhan_yog_rudraksha',name:'Dhan Yog Pro',sub:'Rudraksha + Wealth Stones',tagline:'Sacred wealth bracelet with Rudraksha.',
    price:'₹2,499',original:'₹3,499',planet:'Jupiter / Saturn',chakra:'Solar Plexus',chakraColor:'#FFD700',
    badge:'Premium',badgeColor:'#8E44AD',category:'wealth',stock:'made_to_order',
    benefits:['Combined wealth + spiritual protection','Business growth','Removes financial obstacles','Shiva blessing'],
    vedicUse:'For Saturn Mahadasha wealth blockages, malefic Rahu in 2nd/11th house, or business owners in tough phases.',
    ritual:'Wear on Monday or Thursday. Recite Om Namah Shivaya 108 times before first wear.',
    gallery:['image/opt/DhanYog1-640.jpg','image/opt/DhanYog2-640.jpg','image/opt/DhanYog3-640.jpg'],
    img:'image/opt/DhanYog1-640.jpg',
    msg:'Hi Jyogi! I want to order the Dhan Yog Pro Rudraksha bracelet (₹2,499). Please guide me.'},
  
  {id:'pyrite_solo',name:'Pyrite Power',sub:'Single Stone Wealth',tagline:'Pure pyrite for raw money manifestation.',
    price:'₹799',original:'₹1,199',planet:'Sun',chakra:'Solar Plexus',chakraColor:'#FFD700',
    badge:'Pure Stone',badgeColor:'#D4AF37',category:'wealth',stock:'in_stock',
    benefits:['Pure pyrite energy','Solar plexus activation','Wealth manifestation','Mental clarity for money decisions'],
    vedicUse:'For weak Sun, low confidence in money matters, or Sun-Saturn opposition in chart.',
    ritual:'Wear on Sunday morning. Place in money safe overnight to charge before first wear.',
    gallery:['image/opt/pyrite_solo-640.jpg','image/opt/pyrite_solo2-640.jpg','image/opt/pyrite_solo3-640.jpg','image/opt/pyrite_solo4-640.jpg'],
    img:'image/opt/pyrite_solo-640.jpg',
    msg:'Hi Jyogi! I want to order the Pyrite Power bracelet (₹799). Please guide me.'},
  
  // ════ TIER 3: LOVE & RELATIONSHIPS (women's bestseller segment) ════
  {id:'rose_quartz_love',name:'Love & Marriage',sub:'Rose Quartz Premium',tagline:'Attract love. Heal relationships. Marriage blessings.',
    price:'₹999',original:'₹1,499',planet:'Venus',chakra:'Heart',chakraColor:'#FF69B4',
    badge:'Top Pick',badgeColor:'#C71585',category:'love',stock:'in_stock',
    benefits:['Attract soulmate','Heal heartbreak','Strengthen marriage','Self-love & emotional healing'],
    vedicUse:'For weak Venus, 7th house malefic, delayed marriage yoga, or post-relationship healing.',
    ritual:'Wear on left wrist on Friday. Hold to heart and set clear marriage/love intention before wearing.',
    gallery:['image/opt/rose_quartz-640.jpg','image/opt/rose_quartz_2-640.jpg','image/opt/rose_quartz_3-640.jpg'],
    img:'image/opt/rose_quartz-640.jpg',
    msg:'Hi Jyogi! I want to order the Love & Marriage Rose Quartz bracelet (₹999). Please guide me.'},
  
  {id:'moonstone_pearl',name:'Divine Feminine',sub:'Moonstone & Pearl',tagline:'Feminine power. Intuition. Fertility blessings.',
    price:'₹1,699',original:'₹2,499',planet:'Moon / Venus',chakra:'Sacral / Third Eye',chakraColor:'#E6E6FA',
    badge:'Sacred',badgeColor:'#8B7AB8',category:'love',stock:'in_stock',
    benefits:['Feminine energy boost','Fertility & pregnancy support','Intuition awakening','Hormonal balance'],
    vedicUse:'For weak Moon, mental restlessness, fertility issues, or Sade Sati emotional turbulence in women.',
    ritual:'Wear during Shukla Paksha. Best activated under a Full Moon — leave outside overnight.',
    gallery:['image/opt/moonstone_pearl-640.jpg','image/opt/moonstone_pearl_2-640.jpg','image/opt/moonstone_pearl_3-640.jpg'],
    img:'image/opt/moonstone_pearl-640.jpg',
    msg:'Hi Jyogi! I want to order the Divine Feminine Moonstone & Pearl bracelet (₹1,799). Please guide me.'},
  
  {id:'green_aventurine',name:'Lucky Charm',sub:'Green Aventurine',tagline:'Luck. Opportunity. Heart openness.',
    price:'₹899',original:'₹1,299',planet:'Mercury / Venus',chakra:'Heart',chakraColor:'#27AE60',
    badge:'Lucky',badgeColor:'#27AE60',category:'love',stock:'in_stock',
    benefits:['Luck in opportunities','Heart chakra healing','Emotional balance','Romantic openness'],
    vedicUse:'For weak Mercury, lack of opportunities in career/love, or 5th house issues.',
    ritual:'Wear on Wednesday. Carry briefly in pocket before important meetings or dates.',
    img:'image/green_aventurine.jpg',
    msg:'Hi Jyogi! I want to order the Lucky Charm Green Aventurine bracelet (₹899). Please guide me.'},
  
  // ════ TIER 4: PROTECTION & HEALING (life-crisis buyers) ════
  {id:'black_tourmaline',name:'Protection Shield',sub:'Black Tourmaline & Obsidian',tagline:'Block negative energy. Psychic shield.',
    price:'₹1,299',original:'₹1,799',planet:'Saturn / Mars',chakra:'Root',chakraColor:'#1C1C1C',
    badge:'Protection',badgeColor:'#1C1C1C',category:'protection',stock:'in_stock',
    benefits:['EMF protection','Repels negative energy','Grounds anxiety','Shields from psychic attack'],
    vedicUse:'For Sade Sati, Mangal Dosha, 8th house affliction, or persistent bad luck despite effort.',
    ritual:'Wear on Saturday on left wrist. Cleanse weekly under cold running water for 30 seconds.',
    img:'image/black_tourmaline.jpg',
    msg:'Hi Jyogi! I want to order the Protection Shield Black Tourmaline bracelet (₹1,299). Please guide me.'},
  
  {id:'lepidolite_amethyst',name:'Burnout Recovery',sub:'Lepidolite & Amethyst',tagline:'Mental peace. Stress relief. Better sleep.',
    price:'₹1,299',original:'₹1,799',planet:'Moon / Saturn',chakra:'Third Eye',chakraColor:'#9B59B6',
    badge:'Healing',badgeColor:'#9B59B6',category:'protection',stock:'in_stock',
    benefits:['Reduces anxiety','Improves sleep quality','Emotional reset','Mental endurance'],
    vedicUse:'For Moon affliction, Saturn-Moon (Vish Yoga), depression, or Sade Sati mental fatigue.',
    ritual:'Wear during sleep on left wrist. Place under pillow on full moon nights to recharge.',
    img:'image/lepidolite_amethyst.jpg',
    msg:'Hi Jyogi! I want to order the Burnout Recovery Lepidolite & Amethyst bracelet (₹1,299). Please guide me.'},
  
  {id:'tourmaline_cluster',name:'Tech Defender',sub:'Raw Black Tourmaline',tagline:'EMF shield for tech professionals.',
    price:'₹1,699',original:'₹1,699',planet:'Saturn',chakra:'Root',chakraColor:'#1C1C1C',
    badge:'For Professionals',badgeColor:'#34495E',category:'protection',stock:'in_stock',
    benefits:['EMF/radiation shielding','Focus during long screen time','Reduces tech-related anxiety','Grounding for remote workers'],
    vedicUse:'For Saturn in 6th house (work stress), Mercury affliction, or tech industry professionals in high-screen roles.',
    ritual:'Keep on desk while working. Wear during meetings. Cleanse under tap water weekly.',
    img:'image/tourmaline_cluster.jpg',
    msg:'Hi Jyogi! I want to order the Tech Defender raw Black Tourmaline bracelet (₹1,199). Please guide me.'},
  
  // ════ TIER 5: FOCUS & SPIRITUAL (premium niche) ════
  {id:'tiger_eye_solo',name:'Tiger Eye Courage',sub:'Solo Tiger Eye',tagline:'Courage. Decision-making. Mens leadership.',
    price:'₹799',original:'₹1,199',planet:'Sun / Mars',chakra:'Solar Plexus',chakraColor:'#FF9900',
    badge:'Mens Choice',badgeColor:'#8B4513',category:'focus',stock:'in_stock',
    benefits:['Courage in confrontation','Sharper decision-making','Confidence in negotiations','Grounding for entrepreneurs'],
    vedicUse:'For weak Sun, low self-esteem, Mars affliction in chart, or job interview confidence.',
    ritual:'Wear on right wrist on Tuesday morning. Hold during important meetings or interviews.',
    img:'image/tiger_eye.jpg',
    msg:'Hi Jyogi! I want to order the Tiger Eye Courage bracelet (₹799). Please guide me.'},
  
  {id:'fluorite_clear',name:'Focus Scholar',sub:'Fluorite & Clear Quartz',tagline:'Mental clarity. Memory. Exam success.',
    price:'₹999',original:'₹1,499',planet:'Mercury',chakra:'Third Eye',chakraColor:'#9B59B6',
    badge:'For Students',badgeColor:'#3498DB',category:'focus',stock:'in_stock',
    benefits:['Sharper memory','Better focus during study','Exam confidence','Mental decluttering'],
    vedicUse:'For weak Mercury, students with concentration issues, or professionals in exam phases (UPSC, CA, GMAT).',
    ritual:'Wear during study sessions. Keep on desk during exams. Cleanse before each major test.',
    img:'image/fluorite_clear.jpg',
    msg:'Hi Jyogi! I want to order the Focus Scholar bracelet (₹999). Please guide me.'},
   
  {id:'lapis_amethyst',name:'Third Eye Awakener',sub:'Lapis Lazuli & Amethyst',tagline:'Intuition. Spiritual insight. Inner wisdom.',
    price:'₹1,599',original:'₹2,199',planet:'Jupiter / Ketu',chakra:'Third Eye',chakraColor:'#4B0082',
    badge:'Spiritual',badgeColor:'#4B0082',category:'focus',stock:'in_stock',
    benefits:['Heightens intuition','Spiritual awakening','Lucid dreaming','Inner truth recognition'],
    vedicUse:'For strong Ketu placements, Jupiter in spiritual houses (9th/12th), or meditation practitioners.',
    ritual:'Wear during meditation. Best activated on Thursday under Pushya Nakshatra.',
    img:'image/lapis_amethyst.jpg',
    msg:'Hi Jyogi! I want to order the Third Eye Awakener bracelet (₹1,599). Please guide me.'},
  
  {id:'sunstone_bronzite',name:'Executive Presence',sub:'Sunstone & Bronzite',tagline:'Leadership. Authority. Boardroom presence.',
    price:'₹1,899',original:'₹2,599',planet:'Sun',chakra:'Solar Plexus',chakraColor:'#FF9900',
    badge:'Executive',badgeColor:'#D35400',category:'focus',stock:'in_stock',
    benefits:['Leadership aura','Decision-making power','Presence in meetings','Magnetism for opportunities'],
    vedicUse:'For weak Sun in 10th house, leadership transitions, or professionals seeking promotions.',
    ritual:'Wear on right hand on Sunday. Recite Surya Mantra at sunrise for 7 days before first wear.',
    img:'image/sunstone_bronzite.jpg',
    msg:'Hi Jyogi! I want to order the Executive Presence bracelet (₹1,899). Please guide me.'},
  
  // ════ TIER 6: HERO PIECES (anchor / premium showcase) ════
 /*  {id:'citrine_pyramid',name:'The Wealth Vertex',sub:'Citrine & Pyrite Pyramid',tagline:'Premium wealth amplifier with pyramid geometry.',
    price:'₹3,299',original:'₹4,499',planet:'Jupiter / Sun',chakra:'Solar Plexus',chakraColor:'#FFD700',
    badge:'Hero Piece',badgeColor:'#D4AF37',category:'wealth',stock:'made_to_order',
    benefits:['Maximum wealth amplification','Pyramid sacred geometry','Hero piece for business owners','Long-term financial transformation'],
    vedicUse:'For serious wealth manifestation. Best for Jupiter Mahadasha or chart with strong Lakshmi yoga indicators.',
    ritual:'Place on a Sri Yantra overnight before first wear. Wear on Thursday during Brahma Muhurta (4-6 AM).',
    img:'image/citrine_pyramid.jpg',
    msg:'Hi Jyogi! I want to order the Wealth Vertex Citrine & Pyrite Pyramid bracelet (₹3,299). Please guide me.'},
   */
/*   {id:'selenite_tower',name:'Clarity Column',sub:'Selenite Tower Bracelet',tagline:'High-vibration cleanser. Charge your aura daily.',
    price:'₹2,199',original:'₹2,999',planet:'Moon',chakra:'Crown',chakraColor:'#FFFFFF',
    badge:'Spiritual Cleanser',badgeColor:'#ECECEC',category:'focus',stock:'made_to_order',
    benefits:['Aura cleansing','Removes energetic debris','Charges other crystals','High-vibration meditation'],
    vedicUse:'For energy practitioners, after major life events, or for those finishing Saturn Mahadasha.',
    ritual:'Never water-cleanse (selenite dissolves). Charge under moonlight. Use to cleanse other bracelets monthly.',
    img:'image/selenite_tower.jpg',
    msg:'Hi Jyogi! I want to order the Clarity Column Selenite Tower bracelet (₹2,199). Please guide me.'},
 */];
