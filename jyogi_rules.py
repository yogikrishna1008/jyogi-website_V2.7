#!/usr/bin/env python3
"""
Jyogi Rule Engine v1.0
Classical Vedic Astrology + Tarot + Numerology interpretations
Zero AI dependency — pure classical knowledge encoded as logic
"""

# ═══════════════════════════════════════════════════════════════
# VEDIC ASTROLOGY RULES
# ═══════════════════════════════════════════════════════════════

# ── 27 NAKSHATRAS ──────────────────────────────────────────────
NAKSHATRAS = {
    "Ashwini": {
        "deity": "Ashwini Kumaras", "lord": "Ketu", "element": "Fire",
        "symbol": "Horse's head", "gana": "Deva",
        "nature": "Swift, pioneering, healing energy. You move fast and start things others only dream of. Natural healer with strong instincts. Impatient with delay — you are meant to initiate, not wait.",
        "career": "Medicine, sports, military, entrepreneurship, emergency services.",
        "remedy": "Honour Ketu — simplicity, detachment, service."
    },
    "Bharani": {
        "deity": "Yama", "lord": "Venus", "element": "Earth",
        "symbol": "Yoni", "gana": "Manushya",
        "nature": "Carries what others cannot hold. Deep creative and destructive power. Strong sense of justice. You feel everything intensely — the full spectrum from pleasure to pain. Tremendous endurance.",
        "career": "Creative arts, occult, psychology, surgery, finance.",
        "remedy": "Honour Venus — beauty, creativity, devotion."
    },
    "Krittika": {
        "deity": "Agni", "lord": "Sun", "element": "Fire",
        "symbol": "Razor / Flame", "gana": "Rakshasa",
        "nature": "Sharp, critical, purifying. You cut through illusion to truth. High standards — for yourself first, then others. Leadership through excellence. The nakshatra of courage and transformation by fire.",
        "career": "Leadership, military, teaching, surgery, spiritual practice.",
        "remedy": "Honour Sun — discipline, service, morning Surya namaskar."
    },
    "Rohini": {
        "deity": "Brahma", "lord": "Moon", "element": "Earth",
        "symbol": "Chariot / Ox cart", "gana": "Manushya",
        "nature": "Most creative and fertile of nakshatras. Magnetic beauty and charisma. Strong desires, aesthetic sensibility, love of luxury. Moon is exalted here — deep emotional intelligence and nurturing power.",
        "career": "Arts, music, fashion, agriculture, hospitality, beauty industry.",
        "remedy": "Honour Moon — fasting on Mondays, water offerings."
    },
    "Mrigashira": {
        "deity": "Soma", "lord": "Mars", "element": "Air",
        "symbol": "Deer's head", "gana": "Deva",
        "nature": "Eternal seeker — always searching for something just beyond reach. Gentle, sensitive, curious mind. Excellent researcher and communicator. The search itself is the purpose.",
        "career": "Research, writing, travel, sales, teaching, music.",
        "remedy": "Honour Mars — physical discipline, courage."
    },
    "Ardra": {
        "deity": "Rudra", "lord": "Rahu", "element": "Air",
        "symbol": "Teardrop / Diamond", "gana": "Manushya",
        "nature": "The storm that brings renewal. Intense mental power, grief that transforms. Shiva's energy — destruction followed by rebirth. Exceptional intelligence, but experience must come through struggle.",
        "career": "Science, technology, research, writing, occult.",
        "remedy": "Honour Shiva — Shiva puja, acceptance of change."
    },
    "Punarvasu": {
        "deity": "Aditi", "lord": "Jupiter", "element": "Air",
        "symbol": "Bow and quiver", "gana": "Deva",
        "nature": "The return of light. Optimism, renewal, restoration. Lord Ram was born here. Generous, philosophical, always returning to goodness after difficulty. Protected by divine mother energy.",
        "career": "Teaching, healing, philosophy, law, counselling.",
        "remedy": "Honour Jupiter — wisdom, generosity, Thursday fasting."
    },
    "Pushya": {
        "deity": "Brihaspati", "lord": "Saturn", "element": "Water",
        "symbol": "Flower / Cow's udder", "gana": "Deva",
        "nature": "Most auspicious nakshatra. Nourishing, protective, devoted. Gives without expectation. Saturn here loses malefic nature. Deep capacity for care — of family, community, tradition.",
        "career": "Hospitality, teaching, medicine, public service, food.",
        "remedy": "Honour Saturn through service to others."
    },
    "Ashlesha": {
        "deity": "Nagas", "lord": "Mercury", "element": "Water",
        "symbol": "Coiled serpent", "gana": "Rakshasa",
        "nature": "Serpent wisdom — penetrating, perceptive, hypnotic. Sees what others cannot. Powerful intuition and strategic intelligence. Can heal or poison — the choice is always yours.",
        "career": "Research, psychology, occult, medicine, politics.",
        "remedy": "Honour Nagas — truthfulness, controlled speech."
    },
    "Magha": {
        "deity": "Pitrs (Ancestors)", "lord": "Ketu", "element": "Fire",
        "symbol": "Royal throne", "gana": "Rakshasa",
        "nature": "Royal nakshatra. Connection to lineage and ancestral power. Natural authority and pride. Honours tradition while building legacy. Strong sense of duty to family and heritage.",
        "career": "Leadership, politics, law, aristocracy, heritage.",
        "remedy": "Honour ancestors — Pitru tarpan, family remembrance."
    },
    "Purva Phalguni": {
        "deity": "Bhaga", "lord": "Venus", "element": "Fire",
        "symbol": "Front legs of bed / Hammock", "gana": "Manushya",
        "nature": "Pleasure, creativity, love. Magnetic personal charm. Enjoyment of life's gifts without guilt. Strong marital happiness potential. Artist and lover — beauty is your natural language.",
        "career": "Entertainment, arts, luxury, hospitality, relationships.",
        "remedy": "Honour Venus — devotion, creative expression."
    },
    "Uttara Phalguni": {
        "deity": "Aryaman", "lord": "Sun", "element": "Fire",
        "symbol": "Back legs of bed / Fig tree", "gana": "Manushya",
        "nature": "Partnerships built on honour and mutual benefit. Generous leadership. Strong social contract — you keep your word. Sun exalted in Aries brings out this nakshatra's best when directed outward.",
        "career": "Management, contracts, social work, public relations.",
        "remedy": "Honour Sun — integrity, keeping promises."
    },
    "Hasta": {
        "deity": "Savitar", "lord": "Moon", "element": "Earth",
        "symbol": "Hand", "gana": "Deva",
        "nature": "Skilled hands and quick wit. Craft, dexterity, healing through touch. Humorous and adaptable. What you make with your hands carries your soul. Excellent at any skill requiring precision.",
        "career": "Craft, surgery, healing arts, writing, trade.",
        "remedy": "Honour Moon — purification, water rituals."
    },
    "Chitra": {
        "deity": "Tvashtar / Vishwakarma", "lord": "Mars", "element": "Air",
        "symbol": "Bright jewel / Pearl", "gana": "Rakshasa",
        "nature": "Architect of beauty. The most aesthetically gifted nakshatra. Sees perfection in form — then creates it. Proud, perceptive, drawn to excellence. The universe itself was designed here.",
        "career": "Architecture, design, jewellery, arts, fashion, engineering.",
        "remedy": "Honour Mars — discipline applied to creative work."
    },
    "Swati": {
        "deity": "Vayu", "lord": "Rahu", "element": "Air",
        "symbol": "Sword / Coral", "gana": "Deva",
        "nature": "Independent as the wind. Flexible, adaptable, commercially gifted. Excels in trade, negotiation, diplomacy. Needs freedom to move. Rahu here gives exceptional ability to navigate between worlds.",
        "career": "Business, trade, diplomacy, travel, law.",
        "remedy": "Honour Rahu — meditation, facing fears directly."
    },
    "Vishakha": {
        "deity": "Indra and Agni", "lord": "Jupiter", "element": "Fire",
        "symbol": "Triumphal arch / Potter's wheel", "gana": "Rakshasa",
        "nature": "Goal-oriented, competitive, determined. Does not quit. The success comes late but it comes completely. Fuelled by desire for recognition — channel this into worthy goals.",
        "career": "Politics, business, competition, religion, leadership.",
        "remedy": "Honour Jupiter — patience, ethical ambition."
    },
    "Anuradha": {
        "deity": "Mitra", "lord": "Saturn", "element": "Water",
        "symbol": "Lotus / Triumphal arch", "gana": "Deva",
        "nature": "Deep capacity for friendship and devotion. Loyal beyond measure. Succeeds far from birthplace. Saturn here brings discipline to emotional depth — profound relationships built on real commitment.",
        "career": "Foreign lands, management, occult, astrology, friendship.",
        "remedy": "Honour Saturn — loyalty, long-term thinking."
    },
    "Jyeshtha": {
        "deity": "Indra", "lord": "Mercury", "element": "Water",
        "symbol": "Circular amulet / Umbrella", "gana": "Rakshasa",
        "nature": "Chief among chiefs. Protective power — especially of family and dependents. Carries heavy responsibility with dignity. Mercury here gives sharp intellect with elder's wisdom. The oldest soul in the room.",
        "career": "Leadership, protective services, occult, administration.",
        "remedy": "Honour Mercury — truthful speech, clear communication."
    },
    "Mula": {
        "deity": "Nirriti", "lord": "Ketu", "element": "Fire",
        "symbol": "Bunch of roots / Elephant goad", "gana": "Rakshasa",
        "nature": "Goes to the root of everything — pulls out what is not real. Dissolution that serves truth. Philosophical depth, power, and at times, painful transformation. Ketu here strips away all that is false.",
        "career": "Research, medicine, occult, philosophy, healing.",
        "remedy": "Honour Ketu — letting go, spiritual practice."
    },
    "Purva Ashadha": {
        "deity": "Apas (Water)", "lord": "Venus", "element": "Fire",
        "symbol": "Fan / Winnowing basket", "gana": "Manushya",
        "nature": "Invincible inner conviction. Cannot be defeated once committed. Purifying energy — separates real from false. Strong pride that requires humility to direct wisely.",
        "career": "Law, writing, philosophy, water-related fields, debate.",
        "remedy": "Honour Venus — beauty, purity, right relationship."
    },
    "Uttara Ashadha": {
        "deity": "Vishvadevas", "lord": "Sun", "element": "Earth",
        "symbol": "Elephant tusk / Small bed", "gana": "Manushya",
        "nature": "Final victory — earned slowly, built to last. Universal in nature, ethical in action. Sun here brings out highest solar qualities — responsibility, dignity, universal care.",
        "career": "Service, leadership, military, law, education.",
        "remedy": "Honour Sun — integrity, service to all."
    },
    "Shravana": {
        "deity": "Vishnu", "lord": "Moon", "element": "Air",
        "symbol": "Ear / Three footprints", "gana": "Deva",
        "nature": "The listener. Deep wisdom through careful hearing. Vishnu's nakshatra — preserving, protecting, connecting. Learning through story and tradition. The three steps of Vamana — one humble step reaches everywhere.",
        "career": "Teaching, counselling, media, music, religion.",
        "remedy": "Honour Moon and Vishnu — listening, learning."
    },
    "Dhanishtha": {
        "deity": "Eight Vasus", "lord": "Mars", "element": "Air",
        "symbol": "Drum / Flute", "gana": "Rakshasa",
        "nature": "Rhythm, wealth, abundance. Mars here gives drive with musical sensitivity. Excellent at building material prosperity. The drum is the heartbeat of creation — you feel it naturally.",
        "career": "Music, wealth management, property, military, rhythm-based arts.",
        "remedy": "Honour Mars — disciplined action, generosity."
    },
    "Shatabhisha": {
        "deity": "Varuna", "lord": "Rahu", "element": "Air",
        "symbol": "Empty circle / Thousand stars", "gana": "Rakshasa",
        "nature": "The healer with a hundred medicines. Mysterious, independent, scientific. Rahu here gives unconventional genius. Sees patterns others miss. Needs solitude to recharge. Cosmic in perspective.",
        "career": "Medicine, research, technology, astrology, healing arts.",
        "remedy": "Honour Varuna — truth, keeping vows."
    },
    "Purva Bhadrapada": {
        "deity": "Aja Ekapada", "lord": "Jupiter", "element": "Air",
        "symbol": "Sword / Front legs of funeral cot", "gana": "Manushya",
        "nature": "Transformation through fire — passionate, intense, willing to burn what needs burning. Jupiter here gives philosophical framework to intense experience. The spiritual warrior.",
        "career": "Occult, research, philosophy, teaching, transformation work.",
        "remedy": "Honour Jupiter — channelling intensity into wisdom."
    },
    "Uttara Bhadrapada": {
        "deity": "Ahir Budhnya", "lord": "Saturn", "element": "Ether",
        "symbol": "Twins / Back legs of funeral cot", "gana": "Manushya",
        "nature": "The serpent of the deep. Profound wisdom, patience, depth. Saturn here gives greatest spiritual endurance. Sees the long arc of karma. Compassionate and restrained — the elder teacher.",
        "career": "Spiritual leadership, counselling, occult, service.",
        "remedy": "Honour Saturn — patience, deep practice."
    },
    "Revati": {
        "deity": "Pushan", "lord": "Mercury", "element": "Ether",
        "symbol": "Fish / Drum", "gana": "Deva",
        "nature": "The nurturer who guides safe passage. Compassionate, artistic, spiritually refined. Mercury here gives gentle wisdom. The last nakshatra — contains all experiences of the zodiac. Deep universal empathy.",
        "career": "Healing, arts, travel, spirituality, childcare.",
        "remedy": "Honour Mercury — clear speech, kindness."
    },
}

# ── PLANETS IN HOUSES ───────────────────────────────────────────
PLANET_IN_HOUSE = {
    ("Sun", 1): "Strong personality and leadership. Health and vitality are central themes. Natural authority — others look to you instinctively. Pride must be tempered with humility.",
    ("Sun", 2): "Wealth through personal effort and family legacy. Strong voice. Father associated with finances. Status through speech and accumulated resources.",
    ("Sun", 3): "Courage, self-expression, strong siblings. Career through communication, writing, or media. Initiative brings results. Competition is natural.",
    ("Sun", 4): "Father associated with home or property. Public life. Emotional nature tied to status. Property gains possible but happiness at home can be variable.",
    ("Sun", 5): "Creative intelligence, leadership through creativity. Children bring pride. Speculative ability. Natural performer and teacher.",
    ("Sun", 6): "Excellent for defeating enemies and competition. Health profession or service. Strong work ethic. Father may face health challenges.",
    ("Sun", 7): "Ego in relationships — partner may be dominant or there may be power struggles. Business partnerships with authority figures. Late marriage or delay.",
    ("Sun", 8): "Interest in mysteries, occult, research. Inheritance possible. Father may have hidden issues or early death. Transformation through crisis.",
    ("Sun", 9): "Dharmic soul. Strong spiritual convictions. Father is a significant influence — for good or ill. Foreign connections, higher education, philosophy.",
    ("Sun", 10): "Excellent for career. Natural leader and authority figure. Recognition comes. Government connections. Career is the central life theme.",
    ("Sun", 11): "Gains and achievements. Powerful social network. Eldest sibling significant. Ambitions are fulfilled — especially in second half of life.",
    ("Sun", 12): "Introspection, foreign lands, spiritual seeking. Father may be absent or weak. Expenditure. Private nature. Hidden strength.",

    ("Moon", 1): "Emotional, empathetic, public-facing. Mind and emotions are prominent. Fluctuating — moods and circumstances change like the Moon. Strong mother connection.",
    ("Moon", 2): "Wealth through nurturing, food, or family business. Emotional eating patterns. Beautiful face. Family wealth. Mother associated with finances.",
    ("Moon", 3): "Creative mind, emotional communication. Travel for emotional reasons. Sibling relationships are emotionally significant.",
    ("Moon", 4): "Excellent placement. Home, mother, emotional security are central joys. Strong connection to roots. Real estate beneficial. Mind is peaceful when home is stable.",
    ("Moon", 5): "Creative, romantic, emotionally invested in children and creativity. Intelligence with emotional depth. Speculative tendencies.",
    ("Moon", 6): "Health fluctuates with emotional state. Service to others emotionally fulfilling. Mother may have health concerns. Mind works well under routine.",
    ("Moon", 7): "Emotional in relationships. Marriage to someone nurturing or associated with water. Public and social nature. Business partnerships with emotional dimension.",
    ("Moon", 8): "Deep emotional nature, psychic sensitivity. Mother connection complex. Interest in occult. Emotional crises transform. Inherited gifts.",
    ("Moon", 9): "Devotion and emotional faith. Philosophy comes from feeling not logic. Mother is spiritually significant. Fortune through dharmic actions.",
    ("Moon", 10): "Career in public life, nurturing professions, or with the public. Mother influences career. Reputation fluctuates. Emotional investment in professional success.",
    ("Moon", 11): "Social and emotionally connected to networks. Gains through women or public. Fulfillment through community. Elder sibling connected to mother.",
    ("Moon", 12): "Introspective emotional nature. Foreign connections. Spiritual and imaginative. Sleep and dreams are significant. Mother may be distant or spiritually oriented.",

    ("Mars", 1): "Energetic, courageous, competitive. Strong physical vitality. Impatient. Leadership through action. Anger must be directed constructively.",
    ("Mars", 2): "Aggressive speech — blunt and direct. Wealth through effort and enterprise. Family conflicts possible. Food and resources acquired through initiative.",
    ("Mars", 3): "Courageous, entrepreneurial, strong siblings — especially brothers. Excellent for sports, military, writing, business. Drive and initiative in communication.",
    ("Mars", 4): "Property acquisition through effort. Domestic conflicts possible. Mother's health needs attention. Real estate and construction profitable.",
    ("Mars", 5): "Passionate creative expression. Competitive intelligence. Children may be strong-willed. Investment and speculation require caution.",
    ("Mars", 6): "Excellent for defeating enemies, competition, and litigation. Health profession, military, or law enforcement. Strong work capacity.",
    ("Mars", 7): "Mangal Dosha considerations. Partner may be active, athletic, or assertive. Business partnerships require careful contracts. Passionate relationships.",
    ("Mars", 8): "Research, occult, surgery. Inheritance through conflict. Accidents possible — caution with vehicles. Transformation through crisis builds strength.",
    ("Mars", 9): "Courageous dharma. Aggressive in beliefs. Father may be strong-willed. Foreign travel for work. Strong physical stamina for spiritual practice.",
    ("Mars", 10): "Excellent career placement. Leadership, engineering, military, surgery, law. Professional recognition through action and enterprise.",
    ("Mars", 11): "Gains through enterprise and competition. Elder sibling may be athletic or assertive. Strong network of active people. Ambitions fulfilled through effort.",
    ("Mars", 12): "Expenditure on property abroad. Hidden aggression. Spiritual warrior. Foreign lands. Sleep affected by active mind.",

    ("Mercury", 1): "Intelligent, communicative, youthful appearance. Quick mind. Writing, speaking, or trading comes naturally. Adaptable and curious.",
    ("Mercury", 2): "Financial intelligence. Speech is a tool for wealth. Business acumen. Good at mathematics, accounts, trade. Family of communicators.",
    ("Mercury", 3): "Excellent — natural home. Brilliant writer, speaker, trader, communicator. Siblings are intellectually connected. Short journeys for business.",
    ("Mercury", 4): "Intellectual home environment. Mother is educated. Early education strong. Real estate through intelligent negotiation.",
    ("Mercury", 5): "Creative intelligence. Teaching, writing, children's education. Investment through information. Speculative success through analysis.",
    ("Mercury", 6): "Sharp analytical mind applied to service and health. Medical field, law, accounting. Disputes resolved through intelligence.",
    ("Mercury", 7): "Business partnerships. Spouse is intelligent, communicative. Marriage through intellectual connection. Trade and contracts with partners.",
    ("Mercury", 8): "Research, investigation, occult studies. Tax, insurance, inheritance. Deeply analytical about hidden matters. Writing about taboo subjects.",
    ("Mercury", 9): "Philosophy and communication combined. Teaching dharma. Foreign languages. Writing on spiritual or legal subjects. Father is educated.",
    ("Mercury", 10): "Career in communication, trade, technology, writing, or education. Reputation for intelligence. Business success through networking.",
    ("Mercury", 11): "Gains through communication and networks. Socially intelligent. Elder siblings connected to business or intellect. Fulfillment through information.",
    ("Mercury", 12): "Introspective thinker. Writing in solitude. Foreign languages or lands. Spiritual study. Mind turns inward for its best work.",

    ("Jupiter", 1): "Wisdom, optimism, generosity. Physical largeness — body or presence. Natural teacher and philosopher. Blessings flow through this person.",
    ("Jupiter", 2): "Excellent for wealth and family. Financial wisdom. Educated family. Sweet speech. Accumulation of resources through dharmic means.",
    ("Jupiter", 3): "Wisdom in communication. Teaching through writing or speaking. Philosophical siblings. Journeys for learning.",
    ("Jupiter", 4): "Home is a place of wisdom and abundance. Educated mother. Excellent property placement. Emotional contentment. Strong inner life.",
    ("Jupiter", 5): "Excellent for children — wise and blessed children. Creative intelligence. Teaching, speculation, spiritual practice. Purvapunya — good karma from past lives.",
    ("Jupiter", 6): "Service through wisdom. Healing professions. Overcomes enemies through righteousness. Health maintained through disciplined lifestyle.",
    ("Jupiter", 7): "Blessed marriage — spouse is wise, generous, dharmic. Business partnerships with ethical people. Law and justice in partnerships.",
    ("Jupiter", 8): "Longevity and interest in occult wisdom. Inheritance of knowledge. Spiritual transformation. Research into ancient wisdom systems.",
    ("Jupiter", 9): "Excellent — Jupiter in its natural house. Strong dharma, fortune, philosophy. Father is wise and generous. Foreign connections blessed. Natural guru.",
    ("Jupiter", 10): "Career as teacher, judge, advisor, or in religious field. Reputation for wisdom and integrity. Authority figure respected by all.",
    ("Jupiter", 11): "Excellent for gains and fulfillment of desires. Social wisdom. Network of philosophers and teachers. Elder sibling brings blessings.",
    ("Jupiter", 12): "Spiritual liberation, foreign lands, charitable giving. Wisdom through renunciation. Ashram or monastery connections. Expenses on dharmic activities.",

    ("Venus", 1): "Beauty, charm, artistic nature. Attractive personality. Love of luxury and aesthetics. Relationships are central to identity.",
    ("Venus", 2): "Wealth through beauty, arts, or luxury goods. Beautiful face and voice. Family of artists or affluent people. Indulgent with food.",
    ("Venus", 3): "Artistic communication. Music, singing, creative writing. Beautiful relationships with siblings. Journeys for pleasure.",
    ("Venus", 4): "Beautiful home. Loving mother. Property through aesthetic means. Emotional happiness through beauty and comfort.",
    ("Venus", 5): "Creative gifts, artistic children, romantic love affairs. Excellent for performing arts. Speculation in beautiful things.",
    ("Venus", 6): "Service in beauty, healing, or arts. Health maintained through pleasure and balance. Relationship conflicts require resolution.",
    ("Venus", 7): "Excellent for marriage — beautiful and loving spouse. Business in luxury or beauty. Partnerships are pleasurable and aesthetic.",
    ("Venus", 8): "Hidden pleasures. Inheritance through spouse or partner. Interest in tantra and transformative relationships. Occult aesthetics.",
    ("Venus", 9): "Dharmic love. Beautiful philosophy. Father associated with arts or luxury. Foreign pleasures. Devotional beauty in spiritual practice.",
    ("Venus", 10): "Career in arts, beauty, luxury, entertainment, or diplomacy. Reputation for charm. Public recognition through aesthetic excellence.",
    ("Venus", 11): "Gains through beauty, arts, or luxury. Social connections in artistic fields. Desires for pleasure are fulfilled. Elder sibling may be artistic.",
    ("Venus", 12): "Private pleasures. Foreign relationships. Spiritual devotion through beauty. Expenditure on luxury and comfort.",

    ("Saturn", 1): "Disciplined, serious, slow but steady. Health challenges in youth that build strength. Mature beyond years. Authority comes through perseverance.",
    ("Saturn", 2): "Slow wealth accumulation — delayed but lasting. Speech is careful and deliberate. Family responsibilities are heavy. Frugal by nature.",
    ("Saturn", 3): "Disciplined communication. Hard work in all endeavours. Siblings may be distant or relationship is dutiful. Persistent effort in all enterprises.",
    ("Saturn", 4): "Emotional restriction. Property gains after delay. Mother faces challenges. Home may feel restrictive. Inner peace comes through acceptance.",
    ("Saturn", 5): "Delayed children or small number. Creative expression through discipline — architect, classical musician, serious writer. Intelligence that develops slowly.",
    ("Saturn", 6): "Excellent for service, health, and defeating enemies through persistence. Medical field, law, or organised labour. Chronic health issues managed through routine.",
    ("Saturn", 7): "Delayed or mature marriage. Spouse may be older, serious, or from a different background. Partnerships require patience. Business endures through discipline.",
    ("Saturn", 8): "Longevity. Research and occult through systematic study. Inheritance delayed. Transformation through sustained effort over many years.",
    ("Saturn", 9): "Dharma through discipline and hard work. Father may be stern or absent. Philosophy earned through experience not books. Fortune comes after 36.",
    ("Saturn", 10): "Excellent for long-term career success. Authority and recognition after sustained effort. Government service. Legacy built through decades of work.",
    ("Saturn", 11): "Gains come slowly but are lasting. Elder sibling may be disciplined or distant. Large goals achieved through systematic effort over years.",
    ("Saturn", 12): "Moksha karaka. Spiritual discipline. Foreign lands for work. Solitude and introspection are natural. Expenditure on structured charitable activity.",

    ("Rahu", 1): "Unusual personality, magnetic, unconventional. Strong ambition. Foreign connections. Health through modern medicine. Obsessive self-focus that must be directed outward.",
    ("Rahu", 2): "Unconventional wealth and speech. Foreign currency or multinational business. Obsessive about accumulation. Family may be mixed or unusual.",
    ("Rahu", 3): "Unconventional courage and communication. Technology and media. Foreign languages. Strong ambition in communication fields.",
    ("Rahu", 4): "Unusual home situation. Foreign country or unconventional property. Mother connection is complex. Obsessive about security.",
    ("Rahu", 5): "Unconventional creativity. Foreign children or unusual relationship with children. Speculation and creativity with technology. Past life creative karma.",
    ("Rahu", 6): "Excellent for defeating enemies through unconventional means. Foreign medicine or alternative healing. Strong service in unusual fields.",
    ("Rahu", 7): "Unconventional or foreign spouse. Business with foreigners. Obsessive in relationships. Partnerships that are unusual or across cultures.",
    ("Rahu", 8): "Research into occult and hidden matters. Inheritance from unusual sources. Longevity through unconventional means. Transformation through taboo.",
    ("Rahu", 9): "Unconventional philosophy and religion. Foreign guru or spiritual path. Father connection is complex. Fortune through foreign or non-traditional means.",
    ("Rahu", 10): "Exceptional career ambition. Foreign or technology-based career. Rapid rise — and possible sudden fall if dharma is neglected. Obsessive about recognition.",
    ("Rahu", 11): "Gains through foreign networks, technology, or unconventional means. Large ambitions that are eventually fulfilled. Unusual elder sibling.",
    ("Rahu", 12): "Foreign residence. Spiritual seeking in unconventional paths. Hidden expenses. Dreams and sleep are significant. Past life karma resolving.",

    ("Ketu", 1): "Past life spirituality in the present personality. Detached, spiritual, unusual health. Moksha orientation. The body is a vehicle for something beyond it.",
    ("Ketu", 2): "Detachment from wealth and family. Past life richness now being released. Speech can be sharp or cutting. Non-materialistic.",
    ("Ketu", 3): "Past life communication skill now somewhat detached. Intuitive rather than logical. Brothers may be spiritually oriented or distant.",
    ("Ketu", 4): "Past life comfort now releasing. Home is not the primary source of joy. Mother connection is spiritually significant. Inner life is rich.",
    ("Ketu", 5): "Past life creativity. Children may have spiritual qualities. Creative gifts are intuitive. Investment in spiritual knowledge.",
    ("Ketu", 6): "Excellent for defeating enemies through spiritual means. Past life service. Health through alternative medicine. Immune system has hidden strengths.",
    ("Ketu", 7): "Past life partnership karma resolving. Spouse may be spiritual or unusual. Business partnerships have karmic quality. Liberation through relationships.",
    ("Ketu", 8): "Moksha placement. Past life occult knowledge. Longevity. Transformation through surrender. Death and rebirth are understood deeply.",
    ("Ketu", 9): "Past life dharma. Spiritual father. Non-traditional religious path. Intuitive philosophy. Fortune through spiritual merit of past lives.",
    ("Ketu", 10): "Unusual career path. Past life professional karma resolving. Work in spiritual or research fields. Recognition in unexpected ways.",
    ("Ketu", 11): "Detachment from gains and social network. Past life social karma. Gains come but are not valued. Elder sibling has spiritual quality.",
    ("Ketu", 12): "Excellent moksha placement. Liberation, foreign spiritual lands, ashram life. Past life spiritual practice bearing fruit. Dreams are prophetic.",
}

# ── DASHA INTERPRETATIONS ───────────────────────────────────────
DASHA_THEMES = {
    "Sun": "Identity, authority, father, and government are the themes of your Sun Mahadasha. This is a period of stepping into leadership — often through challenge first, then recognition. Career advances if you act with integrity. Health of father or authority figures may be significant. The ego is tested and refined.",
    "Moon": "Emotions, mother, public life, and the mind are central in your Moon Mahadasha. This is a deeply feeling period — what you sense matters more than what you think. Home, property, and family are active themes. Relationships with women are significant. The mind must be kept calm and nourished.",
    "Mars": "Action, courage, property, and brothers define your Mars Mahadasha. Energy is high — the question is where you direct it. Property acquisition is favoured. Conflicts arise but can be won. Accidents require caution. This is a period for decisive action on long-held plans.",
    "Rahu": "Ambition, foreign connections, technology, and obsession characterise your Rahu Mahadasha. This 18-year period can bring extraordinary worldly achievement — or extraordinary confusion. The key is honest self-assessment. What you want and what you need may not be the same. Foreign lands or unconventional paths bring results.",
    "Jupiter": "Wisdom, expansion, children, wealth, and dharma define your Jupiter Mahadasha. One of the most blessed periods possible. Growth in all areas — financial, spiritual, relational. Teaching or being taught. Children are significant. Fortune flows when you act with generosity and integrity.",
    "Saturn": "Discipline, karma, restructuring, and mastery characterise your Saturn Mahadasha. The 19-year Saturn period is the longest and most transformative. What is built here lasts a lifetime. Effort is required — but the rewards are real and permanent. This is not a fast period. It is a deep one.",
    "Mercury": "Intellect, communication, trade, and adaptability define your Mercury Mahadasha. Business opportunities arise. Writing, speaking, and information are vehicles for success. Multiple projects. Siblings may be significant. The mind is sharp — use it purposefully.",
    "Ketu": "Spirituality, detachment, past life karma, and liberation are the themes of your Ketu Mahadasha. This 7-year period often feels like things falling away — for good reason. What dissolves was not really yours. What remains is essential. Spiritual practice deepens naturally.",
    "Venus": "Love, beauty, luxury, relationships, and creativity define your Venus Mahadasha. The longest at 20 years — and often the most pleasurable. Marriage often happens here. Artistic and financial success. Relationships are central. The danger is over-indulgence. The gift is joy.",
}

# ── SADE SATI PHASES ────────────────────────────────────────────
SADE_SATI = {
    "rising": "Saturn is approaching your Moon sign — you are in the rising phase of Sade Sati. A subtle restlessness has begun. Expenses may be rising without clear cause. Sleep can be disturbed. Something in your life is preparing to shift — you may not yet see what. This phase asks you to become more conscious of what you are building and why.",
    "peak": "Saturn is sitting directly on your Moon sign — the peak of Sade Sati. This is the most intense phase. The Moon rules your mind and emotions. Saturn's pressure here is real — but it is not punishment. It is compression. What is built on solid ground will strengthen. What is built on avoidance will need to be restructured. Work with the pressure rather than against it.",
    "setting": "Saturn has moved past your Moon sign into the setting phase of Sade Sati. The worst is behind you. The mental pressure that characterised the peak phase is gradually lifting. Financial tightness may continue a while longer, but clarity is returning. You are consolidating the lessons of the last five years. What remains is real.",
    "none": "You are not currently in Sade Sati. Check your current Saturn transit position relative to your Moon sign for the next cycle.",
}

# ── LAGNA DESCRIPTIONS ──────────────────────────────────────────
LAGNA_DESC = {
    "Aries": "Mesha Lagna. Mars-ruled. You lead. Initiating, courageous, direct. The world sees your fire first — and your impatience. But underneath is genuine courage that others rely on. Body is strong and athletic. Head and face are prominent. Action is your native language.",
    "Taurus": "Vrishabha Lagna. Venus-ruled. You build. Steady, sensual, determined. The world sees your reliability — and your stubbornness. But underneath is genuine loyalty and love of beauty that creates lasting things. Face and throat are distinctive. Accumulation is your gift.",
    "Gemini": "Mithuna Lagna. Mercury-ruled. You communicate. Curious, adaptable, witty. The world sees your intelligence — and your inconsistency. But underneath is genuine versatility that allows you to inhabit many worlds. Hands and arms are expressive. Connection is your currency.",
    "Cancer": "Karka Lagna. Moon-ruled. You nurture. Sensitive, intuitive, protective. The world sees your care — and your vulnerability. But underneath is genuine emotional intelligence that reads rooms and people with accuracy. Chest and stomach are prominent. Memory is your foundation.",
    "Leo": "Simha Lagna. Sun-ruled. You shine. Generous, proud, creative. The world sees your confidence — and your need for recognition. But underneath is genuine warmth and leadership that inspires others to their best. Heart and spine are central. Performance is your medium.",
    "Virgo": "Kanya Lagna. Mercury-ruled. You refine. Analytical, precise, service-oriented. The world sees your discrimination — and your criticism. But underneath is genuine dedication to improvement that makes everything better. Nervous system and digestion are sensitive. Analysis is your strength.",
    "Libra": "Tula Lagna. Venus-ruled. You balance. Diplomatic, aesthetic, relationship-oriented. The world sees your harmony — and your indecision. But underneath is genuine fairness and beauty sense that creates environments others thrive in. Kidneys and lower back need attention. Justice is your calling.",
    "Scorpio": "Vrishchika Lagna. Mars and Ketu-ruled. You penetrate. Intense, perceptive, transformative. The world sees your power — and your secrecy. But underneath is genuine depth of feeling and investigative intelligence that goes where others won't. Reproductive system is significant. Transformation is your path.",
    "Sagittarius": "Dhanu Lagna. Jupiter-ruled. You seek. Philosophical, adventurous, generous. The world sees your enthusiasm — and your tactlessness. But underneath is genuine wisdom and optimism that expands the horizons of everyone around you. Hips and thighs carry the journey. Truth is your compass.",
    "Capricorn": "Makara Lagna. Saturn-ruled. You build for eternity. Disciplined, ambitious, responsible. The world sees your seriousness — and your austerity. But underneath is genuine commitment to excellence that creates legacies that outlast any individual. Bones and knees are the foundation. Mastery is your reward.",
    "Aquarius": "Kumbha Lagna. Saturn and Rahu-ruled. You serve humanity. Unconventional, intellectual, humanitarian. The world sees your detachment — and your eccentricity. But underneath is genuine care for the collective that thinks beyond personal gain. Circulation and ankles need attention. Innovation is your contribution.",
    "Pisces": "Meena Lagna. Jupiter and Ketu-ruled. You dissolve boundaries. Compassionate, intuitive, artistic. The world sees your sensitivity — and your boundlessness. But underneath is genuine spiritual depth and artistic vision that touches the universal in the particular. Feet carry you between worlds. Liberation is your destination.",
}

# ═══════════════════════════════════════════════════════════════
# TAROT RULES
# ═══════════════════════════════════════════════════════════════

TAROT_CARDS = {
    # ── MAJOR ARCANA ──────────────────────────────────────────
    "The Fool": {
        "number": 0, "element": "Air",
        "upright": "New beginning. A leap of faith is required. The path is not yet visible — but your feet are already moving. Trust the step. What looks like foolishness to others is the beginning of your most important journey.",
        "reversed": "You are holding back at a threshold. The fear of looking foolish is the only obstacle. Or: you have leapt without thinking — pause and ground yourself before proceeding."
    },
    "The Magician": {
        "number": 1, "element": "Air",
        "upright": "Everything you need is already in front of you. Skills, tools, timing — all aligned. This is a moment of true power. What you focus on with will and intention, you can create. Act now.",
        "reversed": "Talent is present but misdirected. Manipulation — of self or others. Check your motives. Are you using your gifts in service of something real, or performing for an audience?"
    },
    "The High Priestess": {
        "number": 2, "element": "Water",
        "upright": "Something is not yet visible — but you already know it. Trust your intuition over logic here. The answer will not come through analysis. Go inward. Wait. Listen.",
        "reversed": "Ignoring inner knowing. Secrets coming to light. You have been listening to everyone except yourself. What does the part of you that does not speak in words already know?"
    },
    "The Empress": {
        "number": 3, "element": "Earth",
        "upright": "Abundance, creativity, fertility. Nature is on your side. A time of growth, nurturing, and pleasure. What you have planted is growing. Creativity flows. Relationships are warm.",
        "reversed": "Creative block, dependency, neglect of self-care. Are you giving so much to others that nothing is left for your own growth? Or holding so tightly to control that nothing can bloom?"
    },
    "The Emperor": {
        "number": 4, "element": "Fire",
        "upright": "Structure, authority, stability. The time for dreaming is over — build. Apply discipline and systematic thinking. Take command of your situation. Father figure energy is present.",
        "reversed": "Rigidity, abuse of authority, controlling behaviour. Structure has become a cage. Is the discipline serving growth or suffocating it?"
    },
    "The Hierophant": {
        "number": 5, "element": "Earth",
        "upright": "Tradition, institution, spiritual guidance. A teacher or mentor is significant now. Working within established systems. Ceremony and commitment. Marriage or formal agreements.",
        "reversed": "Questioning convention, breaking from tradition. Personal spiritual path diverging from the institutional. A rebellion against rules — check whether they are worth breaking."
    },
    "The Lovers": {
        "number": 6, "element": "Air",
        "upright": "A significant choice — not just romantic, but about values alignment. What do you truly stand for? The relationship in question may be with a person, a path, or yourself.",
        "reversed": "Misalignment of values, avoiding a necessary choice. A relationship built on attraction without deeper compatibility. The choice being deferred must be made."
    },
    "The Chariot": {
        "number": 7, "element": "Water",
        "upright": "Victory through will and discipline. Conflicting forces brought under control. You move forward — not because the path is clear, but because you have decided it will be. Drive wins.",
        "reversed": "Loss of direction, aggression without purpose, going too fast. The horses are running in different directions. Which part of you wants what?"
    },
    "Strength": {
        "number": 8, "element": "Fire",
        "upright": "Inner strength — not force. Courage that is gentle, patient, persistent. The lion is tamed not through domination but through love. Your greatest power is your compassion.",
        "reversed": "Self-doubt, inner critic running unchecked, suppressed anger coming out sideways. What would you do if you trusted yourself completely?"
    },
    "The Hermit": {
        "number": 9, "element": "Earth",
        "upright": "Withdrawal for wisdom. A period of solitude, inner work, and reflection. The guidance you seek is within. Do not rush back into activity — what you discover in the quiet matters.",
        "reversed": "Excessive isolation, refusing to return from retreat, loneliness mistaken for wisdom. At what point does reflection become avoidance?"
    },
    "Wheel of Fortune": {
        "number": 10, "element": "Fire",
        "upright": "A turn is happening or about to happen. Cycles complete and begin. What goes down, comes up. Fate is in motion — where are you on the wheel? Flow with the turn rather than resist it.",
        "reversed": "Resistance to inevitable change. Clinging to what has already shifted. Or: a turn for the worse that must be navigated with patience. This too will turn again."
    },
    "Justice": {
        "number": 11, "element": "Air",
        "upright": "Fairness, truth, cause and effect. A legal matter, contract, or decision. What is right will prevail if you are honest. Accountability — to others and to yourself.",
        "reversed": "Injustice, avoidance of accountability, dishonesty. Someone is not being straight — possibly yourself. The balance must be restored."
    },
    "The Hanged Man": {
        "number": 12, "element": "Water",
        "upright": "Pause. Surrender. A different perspective is needed — and it comes only when you stop forcing. The delay is the teaching. What do you see when you look at your situation from a completely different angle?",
        "reversed": "Stalling without purpose, martyrdom, refusing to let go. There is a difference between sacred pause and paralysis. Which is this?"
    },
    "Death": {
        "number": 13, "element": "Water",
        "upright": "Transformation. Something must end for something real to begin. This is not physical death — it is the death of a phase, identity, relationship, or way of being. Necessary. Often liberating.",
        "reversed": "Resisting necessary ending, clinging to what is already gone. The transformation is happening whether you participate or not. Better to go willingly."
    },
    "Temperance": {
        "number": 14, "element": "Fire",
        "upright": "Balance, patience, integration. Two things that seemed incompatible are finding a way to coexist. A healing period. Moderation is the path. What you are blending will become something new.",
        "reversed": "Imbalance, excess, forcing a situation that needs patience. Something is too much — too fast, too intense, too focused. What needs to be tempered?"
    },
    "The Devil": {
        "number": 15, "element": "Earth",
        "upright": "Bondage — but the chains are loosely attached. What holds you could be released if you chose to release it. Addiction, materialism, an unhealthy attachment. The power it has is the power you give it.",
        "reversed": "Awakening from bondage, breaking free, seeing the illusion. The chains are off — now what? Freedom requires knowing who you are without the addiction."
    },
    "The Tower": {
        "number": 16, "element": "Fire",
        "upright": "Sudden disruption. Something built on a false foundation is falling. This is not destruction — it is revelation. What collapses now was never as solid as it appeared. The clearing is necessary.",
        "reversed": "Avoiding necessary collapse, trying to maintain what has already fundamentally broken. Or: a disaster averted. The lesson of the Tower — not always the full lightning strike."
    },
    "The Star": {
        "number": 17, "element": "Air",
        "upright": "Hope renewed. After the Tower, the Star. You have come through something difficult and the light is returning. This is a period of healing, faith, and genuine optimism. What you are working toward will come.",
        "reversed": "Loss of faith, hopelessness, disconnection from inspiration. The star is still there — you have stopped looking up. What would it take to believe again?"
    },
    "The Moon": {
        "number": 18, "element": "Water",
        "upright": "Illusion, subconscious, uncertainty. Things are not what they seem. Trust your gut over appearances. A creative and psychically powerful period — also potentially confusing. The light is reflected, not direct.",
        "reversed": "Confusion lifting, secrets revealed, facing fears directly. The illusion dissolves. What was hiding in the shadow is now visible."
    },
    "The Sun": {
        "number": 19, "element": "Fire",
        "upright": "Clarity, joy, success, vitality. This is one of the most positive cards in the deck. What has been hidden or complicated becomes simple. Energy is high. Authentic self shines. Children and creativity flourish.",
        "reversed": "Dimmed joy, excessive ego, blocked vitality. The sun is behind clouds — temporarily. What is preventing your full expression?"
    },
    "Judgement": {
        "number": 20, "element": "Fire",
        "upright": "A calling. An awakening. A summons to rise into your full self. Past actions are being evaluated — not to judge, but to liberate. Answer the call. This is a moment of genuine renewal.",
        "reversed": "Refusing the call, self-judgment, inability to forgive past self. The trumpet has sounded. Why are you still lying in the grave of who you used to be?"
    },
    "The World": {
        "number": 21, "element": "Earth",
        "upright": "Completion. A significant chapter is genuinely done. Integration of all you have learned. Celebration is appropriate. The cycle ends in wholeness. Prepare — a new cycle is about to begin.",
        "reversed": "Incomplete cycle, shortcuts taken, refusing to close a chapter properly. Something is almost done — but the last step has not been taken."
    },

    # ── MINOR ARCANA — WANDS ───────────────────────────────────
    "Ace of Wands": {
        "upright": "A new creative spark. Inspiration, potential, the beginning of a passionate project. The idea is pure — what you do with it is everything.",
        "reversed": "Blocked creativity, false start, lack of direction. The spark is there but conditions are not right. Wait or change approach."
    },
    "Two of Wands": {
        "upright": "Planning, vision, looking ahead. You have achieved something — now you are deciding what is next. The world is wider than your current vantage point.",
        "reversed": "Fear of the unknown, lack of planning, staying safe when expansion is needed."
    },
    "Three of Wands": {
        "upright": "Expansion underway. Ships sent out, results coming back. Enterprise in progress. The initial risk is paying off.",
        "reversed": "Delays, setbacks in plans, waiting longer than expected for results."
    },
    "Four of Wands": {
        "upright": "Celebration, homecoming, stability achieved. A milestone worth marking. Community and joy.",
        "reversed": "Disrupted celebration, instability at home, joy postponed."
    },
    "Five of Wands": {
        "upright": "Competition, conflict, chaos. Multiple forces competing. Not all conflict is bad — some is productive tension.",
        "reversed": "Avoiding conflict, internal struggle, competition becoming destructive."
    },
    "Six of Wands": {
        "upright": "Victory, recognition, public acknowledgment. You have earned this. Receive it with grace.",
        "reversed": "Delayed recognition, fall from position, private victory without public acknowledgment."
    },
    "Seven of Wands": {
        "upright": "Holding your ground against opposition. You have the advantage — but must defend it actively.",
        "reversed": "Giving up position, overwhelmed by opposition, self-doubt in the face of challenge."
    },
    "Eight of Wands": {
        "upright": "Speed. Things are moving fast now. Communication, travel, rapid developments. Act quickly.",
        "reversed": "Delays, missed communications, things moving too fast without direction."
    },
    "Nine of Wands": {
        "upright": "Resilience. Almost there. Wounded but not broken. One more push required.",
        "reversed": "Exhaustion, stubbornness, refusing help when it is needed."
    },
    "Ten of Wands": {
        "upright": "Heavy burden being carried. You have taken on too much — but you are nearly at the destination.",
        "reversed": "Crushing weight, inability to delegate, collapsing under responsibility."
    },
    "Page of Wands": {
        "upright": "Enthusiastic beginner, creative message, new passion. Start before you are ready.",
        "reversed": "Hesitation, all talk no action, creative block."
    },
    "Knight of Wands": {
        "upright": "Passionate action, adventure, moving fast toward desire. Charismatic energy.",
        "reversed": "Recklessness, scattered energy, passion without discipline."
    },
    "Queen of Wands": {
        "upright": "Confident, magnetic, independent woman or energy. Creative leadership. Warm authority.",
        "reversed": "Jealousy, manipulation, demanding attention without giving."
    },
    "King of Wands": {
        "upright": "Visionary leader. Entrepreneurial, passionate, inspiring. Makes things happen through force of personality.",
        "reversed": "Arrogance, impulsive decisions, tyrannical use of authority."
    },

    # ── MINOR ARCANA — CUPS ───────────────────────────────────
    "Ace of Cups": {
        "upright": "New emotional beginning. Love, intuition, compassion overflowing. The heart opens. Something beautiful is beginning.",
        "reversed": "Emotional block, repressed feelings, an offer of love declined or missed."
    },
    "Two of Cups": {
        "upright": "Partnership, attraction, mutual recognition. Two people seeing each other truly. A significant connection.",
        "reversed": "Relationship imbalance, broken connection, misalignment in partnership."
    },
    "Three of Cups": {
        "upright": "Celebration with community. Friendship, joy, creative collaboration. Good times with people you love.",
        "reversed": "Overindulgence, gossip, superficial social connection."
    },
    "Four of Cups": {
        "upright": "Apathy, contemplation, missing what is being offered. Something good is right in front of you.",
        "reversed": "Emerging from withdrawal, new perspective, accepting what was previously rejected."
    },
    "Five of Cups": {
        "upright": "Loss and grief. Focusing on what was lost rather than what remains. Two cups still stand.",
        "reversed": "Moving on, acceptance, beginning to see what remains after loss."
    },
    "Six of Cups": {
        "upright": "Nostalgia, childhood memories, simple joys. The past is visiting — with gifts or lessons.",
        "reversed": "Stuck in the past, idealising what was, refusing to grow up."
    },
    "Seven of Cups": {
        "upright": "Illusion, wishful thinking, too many choices. Fantasy versus reality. What is real here?",
        "reversed": "Clarity emerging, making a decision, seeing through illusion."
    },
    "Eight of Cups": {
        "upright": "Walking away from what no longer fulfils. Difficult but necessary departure. The search for something deeper.",
        "reversed": "Fear of leaving, staying in the unsatisfying, or returning to what was left."
    },
    "Nine of Cups": {
        "upright": "Wish fulfillment. Emotional satisfaction. The wish card. What you asked for is coming.",
        "reversed": "Overindulgence, superficial satisfaction, wish fulfilled but hollow."
    },
    "Ten of Cups": {
        "upright": "Emotional fulfillment, happy family, lasting happiness. The dream of genuine relational joy, realised.",
        "reversed": "Dysfunctional family dynamic, values misalignment, happiness appearing but not felt."
    },
    "Page of Cups": {
        "upright": "Creative message, intuitive surprise, emotional openness. Something unexpected and sweet.",
        "reversed": "Emotional immaturity, blocked intuition, creative sensitivity used badly."
    },
    "Knight of Cups": {
        "upright": "Romantic pursuit, following the heart, creative invitation. The romantic idealist in action.",
        "reversed": "Moodiness, unrealistic expectations, following feeling without discernment."
    },
    "Queen of Cups": {
        "upright": "Deeply empathetic, emotionally intelligent, nurturing. Holds space for others with wisdom.",
        "reversed": "Emotional manipulation, co-dependency, absorbing others pain without boundaries."
    },
    "King of Cups": {
        "upright": "Emotionally mature leader. Balances feeling and reason. Wise, calm, compassionate authority.",
        "reversed": "Emotional manipulation, volatility beneath calm surface, repressed feeling."
    },

    # ── MINOR ARCANA — SWORDS ─────────────────────────────────
    "Ace of Swords": {
        "upright": "Mental clarity, breakthrough, truth cutting through confusion. The mind at its sharpest.",
        "reversed": "Confusion, wrong decision, truth being avoided."
    },
    "Two of Swords": {
        "upright": "Stalemate, avoidance, a decision being deferred. Blindfold removed reveals the choice.",
        "reversed": "Decision finally made, information emerging, seeing what was hidden."
    },
    "Three of Swords": {
        "upright": "Heartbreak, grief, painful truth. This hurts. But the truth that hurts is better than the lie that comforts.",
        "reversed": "Recovery from heartbreak, releasing grief, moving through pain."
    },
    "Four of Swords": {
        "upright": "Rest, recuperation, temporary withdrawal. The mind needs to stop. Strategic pause.",
        "reversed": "Restlessness, burnout from not resting, return to action."
    },
    "Five of Swords": {
        "upright": "Hollow victory, conflict with losers, winning at the cost of relationships. Was it worth it?",
        "reversed": "Moving past conflict, accepting defeat gracefully, reconciliation."
    },
    "Six of Swords": {
        "upright": "Moving away from turbulence toward calmer waters. Not yet healed — but moving. Transition.",
        "reversed": "Resistance to necessary transition, unable to leave what harms."
    },
    "Seven of Swords": {
        "upright": "Deception, strategy, going alone. Something is being hidden — possibly by you.",
        "reversed": "Truth revealed, confession, abandoning a strategy that was dishonest."
    },
    "Eight of Swords": {
        "upright": "Feeling trapped, restricted, blindfolded. The bondage is largely mental. The way out exists.",
        "reversed": "Breaking free, removing the blindfold, recognising self-imposed limitations."
    },
    "Nine of Swords": {
        "upright": "Anxiety, nightmares, the mind torturing itself. 3am thinking. Most fears are smaller in daylight.",
        "reversed": "Releasing anxiety, seeking help, recognising the thoughts are not reality."
    },
    "Ten of Swords": {
        "upright": "Painful ending. Betrayal, defeat, hitting the bottom. But the sun is rising on the horizon. It is over.",
        "reversed": "Recovery beginning, resisting the inevitable end, learning from defeat."
    },
    "Page of Swords": {
        "upright": "Curious, watchful, alert young energy. Gathering information. Think before speaking.",
        "reversed": "Gossip, scattered thinking, all talk."
    },
    "Knight of Swords": {
        "upright": "Fast, direct, committed to truth and action. Charges in without hesitation.",
        "reversed": "Reckless, aggressive, all speed no direction."
    },
    "Queen of Swords": {
        "upright": "Sharp intelligence, clear boundaries, direct communication. Has been through difficulty and gained wisdom.",
        "reversed": "Bitterness, cold manipulation, cruelty disguised as honesty."
    },
    "King of Swords": {
        "upright": "Intellectual authority, clear judgment, ethical leadership through reason.",
        "reversed": "Tyranny of intellect, coldness, using intelligence to control."
    },

    # ── MINOR ARCANA — PENTACLES ──────────────────────────────
    "Ace of Pentacles": {
        "upright": "New material opportunity. A seed of abundance. Financial beginning. The offer is real.",
        "reversed": "Missed opportunity, bad financial decision, planning without execution."
    },
    "Two of Pentacles": {
        "upright": "Balancing multiple responsibilities. Juggling finances. Adaptable and managing, just.",
        "reversed": "Overwhelmed, dropping the ball, financial disorganisation."
    },
    "Three of Pentacles": {
        "upright": "Teamwork, skilled work, collaboration producing something real. Craft recognised.",
        "reversed": "Lack of teamwork, poor workmanship, isolation in work."
    },
    "Four of Pentacles": {
        "upright": "Financial security, conservation, holding on. Stability — or hoarding?",
        "reversed": "Releasing material attachment, financial loss, loosening grip."
    },
    "Five of Pentacles": {
        "upright": "Financial hardship, feeling left out in the cold. Help is nearby — look up.",
        "reversed": "Recovery from financial difficulty, accepting help, improvement beginning."
    },
    "Six of Pentacles": {
        "upright": "Generosity, giving and receiving, charity. The cycle of abundance shared.",
        "reversed": "Strings attached to generosity, dependency, unequal exchange."
    },
    "Seven of Pentacles": {
        "upright": "Investment assessment. Pausing to see if what was planted is growing. Patience.",
        "reversed": "Impatience with results, poor investment, work not paying off yet."
    },
    "Eight of Pentacles": {
        "upright": "Diligent work, skill development, mastery through repetition. Put in the hours.",
        "reversed": "Perfectionism, mediocre work, not developing skills needed."
    },
    "Nine of Pentacles": {
        "upright": "Self-sufficiency, abundance, enjoying the fruits of labour. You earned this.",
        "reversed": "Financial dependency, work without reward, reaching for luxury prematurely."
    },
    "Ten of Pentacles": {
        "upright": "Generational wealth, lasting legacy, family abundance. Built to last beyond one lifetime.",
        "reversed": "Financial instability, family conflict over money, legacy threatened."
    },
    "Page of Pentacles": {
        "upright": "Studious, practical, new approach to material world. Study before acting.",
        "reversed": "Procrastination, unfocused studying, all theory no practice."
    },
    "Knight of Pentacles": {
        "upright": "Methodical, reliable, hard-working. Slow but gets there. The tortoise.",
        "reversed": "Stuck, overly conservative, boring approach that misses opportunity."
    },
    "Queen of Pentacles": {
        "upright": "Nurturing abundance. Practical, warm, materially secure, generous. Home is her sanctuary.",
        "reversed": "Overwork, neglect of home and body, using money to control."
    },
    "King of Pentacles": {
        "upright": "Material mastery, business success, reliable provider. Built it and maintains it.",
        "reversed": "Materialism, stubbornness, financial control as domination."
    },
}

# ═══════════════════════════════════════════════════════════════
# NUMEROLOGY RULES
# ═══════════════════════════════════════════════════════════════

LIFE_PATH = {
    1: {
        "name": "The Leader",
        "nature": "You came to initiate, lead, and stand alone when necessary. Independence is not a preference — it is a requirement for your soul. When you lead from authentic self-expression rather than ego, others follow naturally. The lesson: lead yourself first.",
        "strengths": "Initiative, courage, originality, self-reliance.",
        "challenges": "Arrogance, isolation, difficulty following others.",
        "career": "Entrepreneur, pioneer, CEO, innovator, athlete.",
        "relationships": "Need a partner who supports independence. Struggle with dependency in others.",
    },
    2: {
        "name": "The Diplomat",
        "nature": "You came to cooperate, balance, and build bridges. Sensitivity is your gift — you feel the emotional weather of any room instantly. The lesson: your needs matter as much as others'. Learn to receive as well as give.",
        "strengths": "Empathy, diplomacy, patience, mediation, intuition.",
        "challenges": "Over-sensitivity, people-pleasing, indecision.",
        "career": "Counsellor, mediator, diplomat, musician, healer.",
        "relationships": "Deeply loving and devoted. Must maintain boundaries to avoid losing self.",
    },
    3: {
        "name": "The Creator",
        "nature": "You came to express, create, and inspire joy. Communication in all forms — writing, speaking, art, music — is your natural medium. The lesson: discipline the creative gift. Scattered brilliance helps no one.",
        "strengths": "Creativity, communication, optimism, charm, self-expression.",
        "challenges": "Scattered focus, superficiality, moodiness, self-doubt.",
        "career": "Writer, artist, performer, teacher, communicator.",
        "relationships": "Magnetic and charming. Needs intellectual and creative stimulation.",
    },
    4: {
        "name": "The Builder",
        "nature": "You came to create order, build systems, and establish foundations that last. Discipline and method are your tools. The lesson: structure serves life — it does not replace it. Allow spontaneity within the structure.",
        "strengths": "Discipline, reliability, practicality, organisation, endurance.",
        "challenges": "Rigidity, stubbornness, workaholism, resistance to change.",
        "career": "Engineer, architect, accountant, manager, builder.",
        "relationships": "Loyal and reliable partner. Needs to express warmth beyond duty.",
    },
    5: {
        "name": "The Freedom Seeker",
        "nature": "You came to experience, explore, and expand freedom. Change is not disruption for you — it is oxygen. The lesson: freedom chosen is different from freedom fled. Find the adventure within commitment.",
        "strengths": "Adaptability, curiosity, versatility, enthusiasm, resourcefulness.",
        "challenges": "Restlessness, commitment issues, self-indulgence, inconsistency.",
        "career": "Travel, sales, media, marketing, entertainment, entrepreneurship.",
        "relationships": "Exciting partner who needs space. Commitment comes when it feels like freedom.",
    },
    6: {
        "name": "The Nurturer",
        "nature": "You came to care, heal, and create beauty in the world around you. Responsibility for others is natural — it is your love language. The lesson: you cannot fill others from an empty vessel. Nurture yourself first.",
        "strengths": "Compassion, responsibility, healing, creativity, devotion.",
        "challenges": "Martyrdom, perfectionism, over-responsibility, controlling through care.",
        "career": "Doctor, teacher, counsellor, artist, parent, healer.",
        "relationships": "Devoted and caring. Must distinguish between nurturing and controlling.",
    },
    7: {
        "name": "The Seeker",
        "nature": "You came to think deeply, seek truth, and understand what lies beneath the surface. Solitude is not loneliness — it is where you do your best work. The lesson: share what you discover. Wisdom kept private helps no one.",
        "strengths": "Analysis, introspection, research, spiritual depth, intuition.",
        "challenges": "Isolation, scepticism, emotional unavailability, perfectionism.",
        "career": "Researcher, philosopher, spiritual teacher, analyst, scientist.",
        "relationships": "Deeply private. Needs a partner who respects solitude. Loves profoundly when trust is built.",
    },
    8: {
        "name": "The Achiever",
        "nature": "You came to master the material world — money, power, achievement. This is not shallow; it is your dharma. The lesson: power and abundance are to be used in service. Karma around money is particularly strong for you.",
        "strengths": "Ambition, leadership, financial acumen, authority, executive ability.",
        "challenges": "Materialism, workaholism, power struggles, all-or-nothing thinking.",
        "career": "Business, finance, law, executive leadership, real estate.",
        "relationships": "Provides security. Needs a partner who matches ambition or is comfortable with success.",
    },
    9: {
        "name": "The Humanitarian",
        "nature": "You came to serve, complete, and give back. You contain the energies of all previous numbers. The lesson: release — of people, outcomes, attachments. Completion is your purpose, not accumulation.",
        "strengths": "Compassion, wisdom, creativity, generosity, universal love.",
        "challenges": "Difficulty letting go, martyrdom, emotional volatility, disappointment in humanity.",
        "career": "Humanitarian, artist, healer, teacher, counsellor, spiritual worker.",
        "relationships": "Deeply loving but often experiences loss. Attract relationships as mirrors of inner work.",
    },
    11: {
        "name": "The Illuminator (Master Number)",
        "nature": "You came with heightened sensitivity and spiritual awareness to inspire and illuminate. The double 1 brings both the leadership of 1 and the sensitivity of 2 in amplified form. The lesson: ground the vision. Brilliance without grounding helps no one.",
        "strengths": "Intuition, inspiration, spiritual insight, idealism, charisma.",
        "challenges": "Nervous sensitivity, impracticality, self-doubt, overwhelm.",
        "career": "Spiritual teacher, artist, visionary leader, healer, inventor.",
        "relationships": "Intense and inspiring. Needs a grounded partner.",
    },
    22: {
        "name": "The Master Builder (Master Number)",
        "nature": "You came to build something that serves humanity at scale. The most powerful of the master numbers — practical idealism. The lesson: the grand vision must be built one brick at a time. Patience.",
        "strengths": "Vision, leadership, practicality, large-scale achievement.",
        "challenges": "Overwhelming responsibility, self-doubt at scale, perfectionism.",
        "career": "Diplomat, large-scale entrepreneur, architect of systems.",
        "relationships": "Devoted but absorbed in the mission. Partner must share the vision or give space for it.",
    },
    33: {
        "name": "The Master Teacher (Master Number)",
        "nature": "The rarest life path. Complete self-mastery before teaching others. You came to embody compassion at its highest and share it. The lesson: you cannot teach what you have not lived.",
        "strengths": "Compassion, creativity, teaching, healing, universal love.",
        "challenges": "Self-sacrifice, taking on others karma, perfectionism.",
        "career": "Spiritual master, healer, teacher of teachers.",
        "relationships": "Loves unconditionally. Must not lose self in service of others.",
    },
}

PERSONAL_YEAR = {
    1: "Year of New Beginnings. Plant seeds now — they define the next 9-year cycle. What you initiate this year matters enormously. Courage and self-direction are required.",
    2: "Year of Patience and Cooperation. Things build slowly. Partnership and collaboration are the path. Do not force what needs to develop naturally. Listen more than you speak.",
    3: "Year of Expression and Joy. Creativity flows. Social connections expand. Express yourself — through art, communication, relationships. This is a year to be seen.",
    4: "Year of Work and Foundation. Build the structures that will support your next cycle. Hard work now, results later. Organisation and discipline are rewarded.",
    5: "Year of Change and Freedom. Expect the unexpected. New experiences, travel, shifts in direction. Embrace change rather than resist it — it is the point of this year.",
    6: "Year of Responsibility and Relationships. Family, home, and relationships take centre stage. Service and care for others. Beauty and harmony in the environment.",
    7: "Year of Reflection and Depth. Go inward. Study, research, spiritual practice. This is not a year for external pushing — it is for internal deepening. Trust the process.",
    8: "Year of Achievement and Power. What you have built is now paying returns. Career and financial focus. Take charge. Major material achievements possible this year.",
    9: "Year of Completion and Release. The cycle is ending. Release what no longer serves — people, situations, identities. Clear space for what is coming in Year 1.",
}

# ═══════════════════════════════════════════════════════════════
# QUERY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_nakshatra(name: str) -> dict:
    """Get full nakshatra interpretation"""
    return NAKSHATRAS.get(name, {"nature": f"{name} nakshatra — deep wisdom and unique karmic path."})

def get_planet_in_house(planet: str, house: int) -> str:
    """Get planet placement interpretation"""
    key = (planet, house)
    return PLANET_IN_HOUSE.get(key, f"{planet} in house {house} — this placement requires careful individual chart analysis.")

def get_dasha(planet: str) -> str:
    """Get Mahadasha theme"""
    return DASHA_THEMES.get(planet, f"{planet} Mahadasha — a period of deep engagement with {planet}'s themes in your specific chart.")

def get_lagna(sign: str) -> str:
    """Get Lagna description"""
    return LAGNA_DESC.get(sign, f"{sign} Lagna — your ascendant shapes how the world sees you and how you approach life.")

def get_sade_sati(phase: str) -> str:
    """Get Sade Sati phase interpretation"""
    return SADE_SATI.get(phase, SADE_SATI["none"])

def get_tarot_card(name: str, orientation: str = "upright") -> str:
    """Get tarot card interpretation"""
    card = TAROT_CARDS.get(name)
    if not card:
        return f"The {name} carries its own message for you in this moment."
    return card.get(orientation, card.get("upright", ""))

def get_life_path(number: int) -> dict:
    """Get numerology life path interpretation"""
    return LIFE_PATH.get(number, {"name": "Your Path", "nature": "Your life path carries unique wisdom."})

def get_personal_year(number: int) -> str:
    """Get personal year interpretation"""
    return PERSONAL_YEAR.get(number, "A year of unique unfoldment on your personal path.")

def generate_chart_insight(lagna: str, moon: str, nakshatra: str,
                           dasha: str, dasha_years_left: float) -> str:
    """
    Generate a complete chart insight without any external AI call.
    Pure rule-based interpretation.
    """
    lagna_text = get_lagna(lagna)
    nak_data = get_nakshatra(nakshatra)
    dasha_text = get_dasha(dasha)

    insight = (
        f"{lagna_text} "
        f"Your Moon in {moon}, placed in {nakshatra} nakshatra — {nak_data.get('nature', '')} "
        f"You are currently in {dasha} Mahadasha with {dasha_years_left:.1f} years remaining. "
        f"{dasha_text}"
    )
    return insight

if __name__ == "__main__":
    # Test the engine
    print("=== Jyogi Rule Engine Test ===")
    print()
    print("NAKSHATRA — Ashwini:")
    print(get_nakshatra("Ashwini")["nature"])
    print()
    print("PLANET IN HOUSE — Saturn 7th:")
    print(get_planet_in_house("Saturn", 7))
    print()
    print("TAROT — The Tower upright:")
    print(get_tarot_card("The Tower", "upright"))
    print()
    print("LIFE PATH 8:")
    lp = get_life_path(8)
    print(f"{lp['name']}: {lp['nature']}")
    print()
    print("PERSONAL YEAR 9:")
    print(get_personal_year(9))
    print()
    print("CHART INSIGHT:")
    print(generate_chart_insight("Scorpio", "Libra", "Swati", "Saturn", 4.2))
