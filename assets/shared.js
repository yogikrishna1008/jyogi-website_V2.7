/* ══════════════════════════════════════════════════════════════════
   shared.js — V2.5 extracted shared infrastructure
   
   Contains: nav/mobile-drawer, theme cycle, i18n, analytics/logging,
   WhatsApp integration (PII-safe), date/time picker widget,
   accessibility controls, admin gate, URL-param handling.
   
   Every standalone tool page loads this file. Tool-specific functions
   and data stay in each tool's own inline <script> or dedicated file.
   
   Extracted from the tools.html monolith during the V2.5 tool split.
   ══════════════════════════════════════════════════════════════════ */
// ── Constants ──
var I18N = {"en":{"auto.book_your_reading":"Enquire on WhatsApp","auto.confused_stuck_or_lost":"Confused, Stuck, or Lost?","auto.confused_stuck_searching_for":"Confused. Stuck. Searching for answers. Here's what happened after their reading.","auto.discover_your_life_path_numb":"Discover your life path number, lucky numbers, and personal year cycle from your date of birth.","auto.draw_your_cards_instantly_si":"Draw your cards instantly. Single card, Past-Present-Future, Celtic Cross, Love & Career spreads.","auto.each_bracelet_is_hand_select":"Each bracelet is hand-selected, cleansed under the full moon, and charged with planetary mantras. Order via WhatsApp for personalised guidance.","auto.each_reading_is_powered_by_a":"Each reading is powered by ancient Vedic wisdom and verified computation — deeply personal, always accurate.","auto.enter_both_birth_dates_for_a":"Enter both birth dates for a Vedic compatibility reading — Moon sign Kuta, Nakshatra match, and Dasha harmony.","auto.free_kundali_with_lagna_naks":"Free Kundali with Lagna, Nakshatra, Dasha & Sadhe Sati. Powered by Swiss Ephemeris.","auto.hand_cleansed_bracelets_pres":"Hand-cleansed bracelets prescribed by planet and chakra.","auto.how_can_jyogi_help":"How Can Jyogi Help?","auto.in_depth_articles_on_vedic_a":"In-depth articles on Vedic astrology, Tarot, remedies, and timing — written by Jyogi from 20+ years of practice.","auto.love_amp_relationship_match":"Love & Relationship Match","auto.vedic_panchang_for_the_next_":"Vedic panchang for the next 7 days — tap a day to see what's auspicious for marriage, travel, business, and more.","auto.vedic_wisdom_amp_guides":"Vedic Wisdom & Guides","auto.view_all_articles":"VIEW ALL ARTICLES","auto.we_begin_every_reading_with_":"We begin every reading with a prayer to the divine. May these sacred energies guide your path.","auto.your_dreams_carry_hidden_mes":"Your dreams carry hidden messages. Record yours and receive a Tarot card — or let Jyogi interpret the deeper meaning.","blog.section_desc":"In-depth articles on Vedic astrology Tarot remedies and timing.","blog.section_title":"Vedic Wisdom & Guides","blog.view_all":"View All Articles","footer.copyright":"© 2026 Jyogi. All rights reserved.","footer.tagline":"Vedic · Tarot · Sacred Crystals","form.calculate_chart":"🪐 Calculate My Vedic Chart","form.city":"City of Birth","form.dob":"Date of Birth","form.full_name":"Full Name","form.question":"Your Question (optional)","form.tob":"Time of Birth","hero.cta_primary":"Enquire on WhatsApp","hero.free_chart":"Free Birth Chart","hero.free_chart_sub":"Vedic · Swiss Ephemeris","hero.free_tarot":"Free Tarot","hero.free_tarot_sub":"Draw your cards now","hero.subtitle":"Your stars hold the answer. Birth chart, Tarot and crystal energy — all in one place.","hero.tagline":"Confused, Stuck, or Lost? The path is here.","nav.astrology":"Astrology","nav.blog":"Blog","nav.book_reading":"Enquire on WhatsApp","nav.crystals":"Crystals","nav.logo_tagline":"Vedic · Tarot · Sacred","nav.numerology":"Numerology","nav.tarot":"Tarot","section.about_title":"The Person Behind Jyogi","section.chart_desc":"Enter your birth details for a complete sidereal Vedic chart.","section.chart_title":"Your Birth Chart","section.compat_title":"Love & Relationship Match","section.dreams_title":"Dream Journal","section.gallery_title":"Divine Blessings","section.how_title":"How a Session Works","section.muhurta_title":"Muhurta — Lucky Days","section.reviews_title":"They Were Exactly Where You Are","section.services_desc":"Vedic astrology Tarot Numerology and sacred crystals — choose your path.","section.services_title":"Sacred Services","section.shop_title":"Crystal Bracelets","section.tarot_desc":"Jyogi's intuitive Tarot deck channels meditative energy and ancient wisdom.","section.tarot_title":"Draw Your Cards"},"hi":{"auto.book_your_reading":"WhatsApp पर पूछें","auto.confused_stuck_or_lost":"उलझे हुए हैं? रास्ता यहाँ है।","auto.confused_stuck_searching_for":"उलझन। ठहराव। उत्तरों की तलाश। देखिए उनकी रीडिंग के बाद क्या हुआ।","auto.discover_your_life_path_numb":"अपने जन्म तिथि से जीवन पथ अंक और शुभ अंक जानें।","auto.draw_your_cards_instantly_si":"तुरंत कार्ड खींचें। सिंगल, अतीत-वर्तमान-भविष्य, सेल्टिक क्रॉस।","auto.each_bracelet_is_hand_select":"हर ब्रेसलेट हाथ से चुना जाता है, पूर्णिमा पर शुद्ध किया जाता है और ग्रह मंत्रों से अभिमंत्रित। व्यक्तिगत मार्गदर्शन के लिए WhatsApp पर ऑर्डर करें।","auto.each_reading_is_powered_by_a":"हर रीडिंग प्राचीन वैदिक ज्ञान और सत्यापित गणना पर आधारित — गहराई से व्यक्तिगत, हमेशा सटीक।","auto.enter_both_birth_dates_for_a":"वैदिक गुण मिलान के लिए दोनों जन्म तिथियाँ भरें — चंद्र राशि कूट, नक्षत्र मिलान और दशा सामंजस्य।","auto.free_kundali_with_lagna_naks":"लग्न, नक्षत्र, दशा और साढ़े-साती के साथ निःशुल्क कुंडली।","auto.hand_cleansed_bracelets_pres":"हस्त-शुद्ध क्रिस्टल कंगन — ग्रह और चक्र के अनुसार निर्धारित।","auto.how_can_jyogi_help":"जयोगी कैसे मदद करेंगे? Vedic astrology, Tarot, Numerology, and sacred crystals — choose your path. वैदिक ज्योतिष, टैरो, अंकशास्त्र और पवित्र क्रिस्टल — अपना मार्ग चुनें।","auto.in_depth_articles_on_vedic_a":"वैदिक ज्योतिष, टैरो, उपाय और शुभ समय पर गहन लेख — जयोगी द्वारा 20+ वर्षों के अनुभव से लिखित।","auto.love_amp_relationship_match":"प्रेम एवं संबंध मिलान","auto.vedic_panchang_for_the_next_":"अगले 7 दिनों का वैदिक पंचांग — किसी दिन पर टैप करें और जानें विवाह, यात्रा, व्यापार आदि के लिए शुभ समय।","auto.vedic_wisdom_amp_guides":"वैदिक ज्ञान एवं मार्गदर्शिका","auto.view_all_articles":"सभी लेख देखें","auto.we_begin_every_reading_with_":"हम हर रीडिंग की शुरुआत ईश्वर की प्रार्थना से करते हैं। ये पवित्र ऊर्जाएँ आपके मार्ग को आलोकित करें।","auto.your_dreams_carry_hidden_mes":"आपके सपनों में छिपे संदेश होते हैं। अपना सपना दर्ज करें और एक टैरो कार्ड पाएँ — या जयोगी से गहरा अर्थ जानें।","blog.section_desc":"वैदिक ज्योतिष टैरो उपाय और शुभ समय पर गहन लेख।","blog.section_title":"वैदिक ज्ञान एवं मार्गदर्शिका","blog.view_all":"सभी लेख देखें","footer.copyright":"© 2026 जयोगी. सर्वाधिकार सुरक्षित।","footer.tagline":"वैदिक · टैरो · पवित्र क्रिस्टल","form.calculate_chart":"🪐 मेरी वैदिक कुंडली देखें","form.city":"जन्म स्थान","form.dob":"जन्म तिथि","form.full_name":"पूरा नाम","form.question":"आपका प्रश्न (वैकल्पिक)","form.tob":"जन्म समय","hero.cta_primary":"WhatsApp पर पूछें","hero.free_chart":"निःशुल्क कुंडली","hero.free_chart_sub":"वैदिक · स्विस एफेमेरिस","hero.free_tarot":"निःशुल्क टैरो","hero.free_tarot_sub":"अभी अपने कार्ड खींचें","hero.subtitle":"आपके सितारों में जवाब है। जन्मपत्री, टैरो और ऊर्जा — सब एक जगह।","hero.tagline":"उलझे हुए हैं? रास्ता यहाँ है।","nav.astrology":"ज्योतिष","nav.blog":"ब्लॉग","nav.book_reading":"WhatsApp पर पूछें","nav.crystals":"क्रिस्टल","nav.logo_tagline":"वैदिक · टैरो · पवित्र","nav.numerology":"अंकशास्त्र","nav.tarot":"टैरो","section.about_title":"जयोगी के पीछे का व्यक्ति","section.chart_desc":"पूर्ण वैदिक जन्मपत्री के लिए अपना जन्म विवरण दर्ज करें।","section.chart_title":"आपकी जन्म कुंडली","section.compat_title":"प्रेम एवं संबंध मिलान","section.dreams_title":"स्वप्न डायरी","section.gallery_title":"दिव्य आशीर्वाद","section.how_title":"सत्र कैसे होता है","section.muhurta_title":"मुहूर्त — शुभ दिन","section.reviews_title":"वे भी ठीक आपकी जगह थे","section.services_desc":"वैदिक ज्योतिष टैरो अंकशास्त्र और पवित्र क्रिस्टल — अपना मार्ग चुनें।","section.services_title":"पवित्र सेवाएँ","section.shop_title":"क्रिस्टल ब्रेसलेट","section.tarot_desc":"जयोगी का सहज टैरो डेक ध्यान-ऊर्जा और प्राचीन ज्ञान का संचार करता है।","section.tarot_title":"अपने कार्ड चुनें"},"or":{"auto.book_your_reading":"WhatsApp ରେ ପଚାରନ୍ତୁ","auto.confused_stuck_or_lost":"ବିଭ୍ରାନ୍ତ, ଅଟକି, କିମ୍ବା ହଜି ଯାଇଛନ୍ତି?","auto.confused_stuck_searching_for":"ଦ୍ୱନ୍ଦ୍ୱ। ଅଚଳାବସ୍ଥା। ଉତ୍ତରର ସନ୍ଧାନ। ଦେଖନ୍ତୁ ସେମାନଙ୍କ ରିଡିଂ ପରେ କଣ ହେଲା।","auto.discover_your_life_path_numb":"ଆପଣଙ୍କ ଜନ୍ମ ତାରିଖରୁ ଜୀବନ ପଥ ଅଙ୍କ ଓ ଶୁଭ ଅଙ୍କ ଜାଣନ୍ତୁ।","auto.draw_your_cards_instantly_si":"ତୁରନ୍ତ କାର୍ଡ ଟାଣନ୍ତୁ। ଏକକ, ଅତୀତ-ବର୍ତ୍ତମାନ-ଭବିଷ୍ୟତ, ସେଲ୍ଟିକ୍ କ୍ରସ୍।","auto.each_bracelet_is_hand_select":"ପ୍ରତ୍ୟେକ ବ୍ରେସଲେଟ୍ ହାତରେ ବଛାଯାଏ, ପୂର୍ଣ୍ଣିମାରେ ଶୁଦ୍ଧ କରାଯାଏ ଓ ଗ୍ରହ ମନ୍ତ୍ରରେ ଅଭିମନ୍ତ୍ରିତ। ବ୍ୟକ୍ତିଗତ ମାର୍ଗଦର୍ଶନ ପାଇଁ WhatsApp ରେ ଅର୍ଡର କରନ୍ତୁ।","auto.each_reading_is_powered_by_a":"ପ୍ରତ୍ୟେକ ରିଡିଂ ପ୍ରାଚୀନ ବୈଦିକ ଜ୍ଞାନ ଓ ଯାଞ୍ଚିତ ଗଣନା ଉପରେ ଆଧାରିତ — ଗଭୀର ଭାବେ ବ୍ୟକ୍ତିଗତ, ସର୍ବଦା ସଠିକ।","auto.enter_both_birth_dates_for_a":"ବୈଦିକ ଗୁଣ ମିଳନ ପାଇଁ ଉଭୟ ଜନ୍ମ ତାରିଖ ଦିଅନ୍ତୁ — ଚନ୍ଦ୍ର ରାଶି କୂଟ, ନକ୍ଷତ୍ର ମିଳନ ଓ ଦଶା ସମନ୍ୱୟ।","auto.free_kundali_with_lagna_naks":"ଲଗ୍ନ, ନକ୍ଷତ୍ର, ଦଶା ଓ ସାଢ଼େ-ସାତୀ ସହିତ ନିଃଶୁଳ୍କ କୁଣ୍ଡଳୀ।","auto.hand_cleansed_bracelets_pres":"ହସ୍ତ-ଶୁଦ୍ଧ କ୍ରିଷ୍ଟାଲ୍ କଙ୍ଗନ — ଗ୍ରହ ଓ ଚକ୍ର ଅନୁସାରେ ନିର୍ଦ୍ଧାରିତ।","auto.how_can_jyogi_help":"ବୈଦିକ ଜ୍ୟୋତିଷ, ଟାରୋ, ଅଙ୍କଶାସ୍ତ୍ର ଓ ପବିତ୍ର କ୍ରିଷ୍ଟାଲ୍ — ଆପଣଙ୍କ ମାର୍ଗ ବାଛନ୍ତୁ।","auto.in_depth_articles_on_vedic_a":"ବୈଦିକ ଜ୍ୟୋତିଷ, ଟାରୋ, ଉପାୟ ଓ ଶୁଭ ସମୟ ଉପରେ ଗଭୀର ପ୍ରବନ୍ଧ — ଜୟୋଗୀଙ୍କ ୨୦+ ବର୍ଷର ଅଭିଜ୍ଞତାରୁ।","auto.love_amp_relationship_match":"ପ୍ରେମ ଓ ସମ୍ପର୍କ ମିଳନ","auto.vedic_panchang_for_the_next_":"ଆଗାମୀ ୭ ଦିନର ବୈଦିକ ପଞ୍ଚାଙ୍ଗ — କୌଣସି ଦିନ ଉପରେ ଟ୍ୟାପ୍ କରନ୍ତୁ ଓ ବିବାହ, ଯାତ୍ରା, ବ୍ୟବସାୟ ଆଦି ପାଇଁ ଶୁଭ ସମୟ ଜାଣନ୍ତୁ।","auto.vedic_wisdom_amp_guides":"ବୈଦିକ ଜ୍ଞାନ ଓ ମାର୍ଗଦର୍ଶିକା","auto.view_all_articles":"ସମସ୍ତ ପ୍ରବନ୍ଧ ଦେଖନ୍ତୁ","auto.we_begin_every_reading_with_":"ଆମେ ପ୍ରତ୍ୟେକ ରିଡିଂ ଈଶ୍ୱରଙ୍କ ପ୍ରାର୍ଥନାରୁ ଆରମ୍ଭ କରୁ। ଏହି ପବିତ୍ର ଶକ୍ତି ଆପଣଙ୍କ ମାର୍ଗକୁ ଆଲୋକିତ କରୁ।","auto.your_dreams_carry_hidden_mes":"ଆପଣଙ୍କ ସ୍ୱପ୍ନରେ ଲୁକ୍କାୟିତ ସନ୍ଦେଶ ଥାଏ। ଆପଣଙ୍କ ସ୍ୱପ୍ନ ଲେଖନ୍ତୁ ଓ ଗୋଟିଏ ଟାରୋ କାର୍ଡ ପାଆନ୍ତୁ — କିମ୍ବା ଜୟୋଗୀଙ୍କଠାରୁ ଗଭୀର ଅର୍ଥ ଜାଣନ୍ତୁ।","blog.section_desc":"ବୈଦିକ ଜ୍ୟୋତିଷ ଟାରୋ ଉପାୟ ଓ ଶୁଭ ସମୟ ଉପରେ ଗଭୀର ପ୍ରବନ୍ଧ।","blog.section_title":"ବୈଦିକ ଜ୍ଞାନ ଓ ମାର୍ଗଦର୍ଶିକା","blog.view_all":"ସମସ୍ତ ପ୍ରବନ୍ଧ ଦେଖନ୍ତୁ","footer.copyright":"© 2026 ଜୟୋଗୀ. ସର୍ବାଧିକାର ସୁରକ୍ଷିତ।","footer.tagline":"ବୈଦିକ · ଟାରୋ · ପବିତ୍ର କ୍ରିଷ୍ଟାଲ୍","form.calculate_chart":"🪐 ମୋ ବୈଦିକ କୁଣ୍ଡଳୀ ଦେଖନ୍ତୁ","form.city":"ଜନ୍ମ ସ୍ଥାନ","form.dob":"ଜନ୍ମ ତାରିଖ","form.full_name":"ପୂରା ନାମ","form.question":"ଆପଣଙ୍କ ପ୍ରଶ୍ନ (ଇଚ୍ଛାଧୀନ)","form.tob":"ଜନ୍ମ ସମୟ","hero.cta_primary":"WhatsApp ରେ ପଚାରନ୍ତୁ","hero.free_chart":"ନିଃଶୁଳ୍କ କୁଣ୍ଡଳୀ","hero.free_chart_sub":"ବୈଦିକ · ସ୍ୱିସ୍ ଏଫେମେରିସ୍","hero.free_tarot":"ନିଃଶୁଳ୍କ ଟାରୋ","hero.free_tarot_sub":"ବର୍ତ୍ତମାନ ଆପଣଙ୍କ କାର୍ଡ ଟାଣନ୍ତୁ","hero.subtitle":"ଆପଣଙ୍କ ତାରାମାନଙ୍କରେ ଉତ୍ତର ଅଛି। କୁଣ୍ଡଳୀ, ଟାରୋ ଓ ଶକ୍ତି — ସବୁ ଏକ ସ୍ଥାନରେ।","hero.tagline":"ବିଭ୍ରାନ୍ତ, ଅଟକି, କିମ୍ବା ହଜି ଯାଇଛନ୍ତି? ପଥ ଏଠାରେ।","nav.astrology":"ଜ୍ୟୋତିଷ","nav.blog":"ବ୍ଲଗ୍","nav.book_reading":"WhatsApp ରେ ପଚାରନ୍ତୁ","nav.crystals":"କ୍ରିଷ୍ଟାଲ୍","nav.logo_tagline":"ବୈଦିକ · ଟାରୋ · ପବିତ୍ର","nav.numerology":"ଅଙ୍କଶାସ୍ତ୍ର","nav.tarot":"ଟାରୋ","section.about_title":"ଜୟୋଗୀଙ୍କ ପଛର ବ୍ୟକ୍ତି","section.chart_desc":"ସମ୍ପୂର୍ଣ୍ଣ ବୈଦିକ କୁଣ୍ଡଳୀ ପାଇଁ ଆପଣଙ୍କ ଜନ୍ମ ବିବରଣୀ ଦିଅନ୍ତୁ।","section.chart_title":"ଆପଣଙ୍କ ଜନ୍ମ କୁଣ୍ଡଳୀ","section.compat_title":"ପ୍ରେମ ଓ ସମ୍ପର୍କ ମିଳନ","section.dreams_title":"ସ୍ୱପ୍ନ ଡାଏରୀ","section.gallery_title":"ଦିବ୍ୟ ଆଶୀର୍ବାଦ","section.how_title":"ସେସନ୍ କିପରି ହୁଏ","section.muhurta_title":"ମୁହୂର୍ତ୍ତ — ଶୁଭ ଦିନ","section.reviews_title":"ସେମାନେ ମଧ୍ୟ ଠିକ୍ ଆପଣଙ୍କ ଜାଗାରେ ଥିଲେ","section.services_desc":"ବୈଦିକ ଜ୍ୟୋତିଷ ଟାରୋ ଅଙ୍କଶାସ୍ତ୍ର ଓ ପବିତ୍ର କ୍ରିଷ୍ଟାଲ୍ — ଆପଣଙ୍କ ମାର୍ଗ ବାଛନ୍ତୁ।","section.services_title":"ପବିତ୍ର ସେବାସମୂହ","section.shop_title":"କ୍ରିଷ୍ଟାଲ୍ ବ୍ରେସଲେଟ୍","section.tarot_desc":"ଜୟୋଗୀଙ୍କ ସହଜ ଟାରୋ ଡେକ୍ ଧ୍ୟାନ-ଶକ୍ତି ଓ ପ୍ରାଚୀନ ଜ୍ଞାନ ସଞ୍ଚାର କରେ।","section.tarot_title":"ଅପଣଙ୍କ କାର୍ଡ ବାଛନ୍ତୁ"}};

const FS_MIN = 16, FS_MAX = 28, FS_DEFAULT = 20, FS_STEP = 2;

var currentFS = FS_DEFAULT; try{ var _sf=localStorage.getItem('jyogi_fs'); if(_sf) currentFS=parseInt(_sf); }catch(e){}


let currentLang='en';

var WA_NUMBER  = '919437794561';

var API_BASE   = (window.SITE_CONFIG && SITE_CONFIG.apiBase) || 'https://jyogi-api.onrender.com';

var CLIENT_LOG = [];

var LS_KEY = 'jyogi_submissions';

var RAZORPAY_LINKS = Object.freeze({
  vedic_reading:   'https://rzp.io/rzp/sryivWVn',
  tarot_session:   'https://rzp.io/rzp/MqgHmGC',
  crystal_consult: 'https://rzp.io/rzp/ha8fPHO8'
});

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

var _adminSecret = sessionStorage.getItem("jyogi_admin_secret") || "";

var _MONTHS=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

var _pt=null;

var _pickerKbdCtx = null;  // {type, kind:'chart'|'comp', hidId}



const observer=new IntersectionObserver((entries)=>{
  entries.forEach(e=>{
    if(e.isIntersecting){
      e.target.style.opacity='1';
      e.target.style.transform='translateY(0)';
    }
  });
},{threshold:0.1});


// ── Functions ──

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
  if(isOpen) document.addEventListener('keydown', _mobileNavEscHandler);
  else document.removeEventListener('keydown', _mobileNavEscHandler);
}

/* V2.5 header/drawer open/close — matches the mob-drawer/mob-backdrop IDs
 * used by the V2.5 header markup (index.html and every standalone tool
 * page built from it). toggleMobileNav() above is tools.html's OLDER
 * drawer system (different IDs: mobile-nav/mobile-nav-backdrop) and is
 * kept for reference/back-compat but is not called by any V2.5 page.
 * This gap — the V2.5 pages' hamburger button calling a function that
 * was never actually extracted into shared.js — was caught by directly
 * testing the drawer open/close interaction, not by a static function
 * inventory check. */
function openMobileNav(){
  document.getElementById('mob-backdrop').classList.add('open');
  document.getElementById('mob-drawer').classList.add('open');
  document.body.style.overflow='hidden';
}
function closeMobileNav(){
  document.getElementById('mob-backdrop').classList.remove('open');
  document.getElementById('mob-drawer').classList.remove('open');
  document.body.style.overflow='';
}

function _mobileNavEscHandler(e){
  if(e.key === 'Escape') toggleMobileNav();
}

function toggleTheme(){
  var body = document.body;
  var current = body.classList.contains('warm-theme') ? 'warm'
              : body.classList.contains('light-theme') ? 'light'
              : 'dark';
  // Cycle: dark -> light -> warm -> dark
  var next = current === 'dark' ? 'light' : current === 'light' ? 'warm' : 'dark';
  body.classList.remove('light-theme','warm-theme');
  if(next === 'light') body.classList.add('light-theme');
  else if(next === 'warm') body.classList.add('warm-theme');
  applyThemeUI(next);
  try{ localStorage.setItem('jyogi_theme', next); }catch(e){}
}

function applyThemeUI(theme){
  var icon = theme === 'dark' ? '☀️' : theme === 'light' ? '🌙' : '📜';
  var navLabel = theme === 'dark' ? 'LIGHT' : theme === 'light' ? 'WARM' : 'DARK';
  var mobLabel = theme === 'dark' ? 'Light Mode' : theme === 'light' ? 'Warm Light' : 'Dark Mode';
  var navThemeIcon = document.getElementById('nav-mob-theme-icon');
  if(navThemeIcon) navThemeIcon.textContent = icon;
  var ti = document.getElementById('theme-icon'); if(ti) ti.textContent = icon;
  var tl = document.getElementById('theme-label'); if(tl) tl.textContent = navLabel;
  var mi = document.getElementById('mob-theme-icon'); if(mi) mi.textContent = icon;
  var ml = document.getElementById('mob-theme-label'); if(ml) ml.textContent = mobLabel;
  var hvBtn = document.getElementById('hv-toggle-btn');
  if(hvBtn){
    hvBtn.style.display = (theme === 'warm') ? 'flex' : 'none';
    if(theme !== 'warm') hvBtn.setAttribute('aria-pressed','false');
  }
}

function setTheme(theme){
  document.body.classList.remove('light-theme','warm-theme');
  if(theme !== 'warm') document.body.classList.remove('high-visibility'); // only meaningful inside Readable Mode
  if(theme === 'light') document.body.classList.add('light-theme');
  else if(theme === 'warm') document.body.classList.add('warm-theme');
  applyThemeUI(theme);
  try{ localStorage.setItem('jyogi_theme', theme); }catch(e){}
}

function i18nLookup(key, lang){
  var t = I18N[lang];
  if(t && Object.prototype.hasOwnProperty.call(t,key)) return t[key];
  var en = I18N['en'];  // fallback to English if a translation is missing
  if(en && Object.prototype.hasOwnProperty.call(en,key)) return en[key];
  return null;
}

function setLang(lang){
  currentLang = lang;
  // Body classes for font switching (Odia/Hindi need their own font)
  document.body.classList.remove('hindi','lang-hi','lang-or');
  if(lang==='hi') document.body.classList.add('hindi','lang-hi');
  else if(lang==='or') document.body.classList.add('lang-or');
  document.querySelectorAll('.lang-btn,.nml-btn').forEach(function(b){
    b.classList.toggle('active', b.dataset.lang===lang);
  });
  // Swap all tagged text nodes
  document.querySelectorAll('[data-i18n]').forEach(function(el){
    var v = i18nLookup(el.getAttribute('data-i18n'), lang);
    if(v!==null) el.textContent = v;
  });
  // Swap placeholders
  document.querySelectorAll('[data-i18n-placeholder]').forEach(function(el){
    var v = i18nLookup(el.getAttribute('data-i18n-placeholder'), lang);
    if(v!==null) el.setAttribute('placeholder', v);
  });
  // Tarot question box (special, language-specific prompt)
  var tq=document.getElementById('tarot-question');
  if(tq){
    tq.placeholder = lang==='hi' ? 'अपना मन एकाग्र करें और प्रश्न टाइप करें…'
                   : lang==='or' ? 'ମନ ସ୍ଥିର କରନ୍ତୁ ଏବଂ ଆପଣଙ୍କ ପ୍ରଶ୍ନ ଲେଖନ୍ତୁ…'
                   : 'Focus your mind and type your question...';
  }
  document.documentElement.setAttribute('lang', lang);
  try{ localStorage.setItem('jyogi_lang', lang); }catch(e){}
}

function updateMobileLang(lang){
  document.getElementById('mob-en-btn').classList.toggle('active', lang==='en');
  document.getElementById('mob-hi-btn').classList.toggle('active', lang==='hi');
  var orBtn=document.getElementById('mob-or-btn');
  if(orBtn) orBtn.classList.toggle('active', lang==='or');
  syncMobileLang(lang);
}

function syncMobileLang(lang){
  // Sync the top-bar mobile language pills
  document.querySelectorAll('.nml-btn').forEach(function(b){
    b.classList.toggle('active', b.dataset.lang===lang);
  });
}

function toggleHighVisibility(){
  if(!document.body.classList.contains('warm-theme')) return; // only available in Readable Mode
  const on = document.body.classList.toggle('high-visibility');
  try{ localStorage.setItem('jyogi_hv', on ? '1' : ''); }catch(e){}
  const btn = document.getElementById('hv-toggle-btn');
  if(btn) btn.setAttribute('aria-pressed', on ? 'true' : 'false');
}

function applyFontSize(size){
  // BUG FIXED: this file's size range is literal PIXELS (16-28, default 20),
  // not a percentage like the 80-130 scheme used elsewhere. The old code did
  // (size/100) to derive the scale variable — at default size=20 that gave
  // 0.20 instead of 1.0, silently shrinking every scaled element to ~1/5 its
  // size the moment any font-size control was touched. Fixed to size/FS_DEFAULT
  // so the multiplier is correctly 1.0 at the default and moves proportionally.
  const scale = size / FS_DEFAULT;
  const root = document.documentElement.style;
  // Real reading content (paragraphs, blog/article/report text) — scales fully.
  root.setProperty('--body-font-scale', scale.toFixed(2));
  // Small-but-important text (form help, card meta) — never goes BELOW 1,
  // so shrinking the page never makes small print harder to read.
  root.setProperty('--small-important-scale', Math.max(scale, 1).toFixed(2));
  // Headings — intentionally limited to ±25% of the body change, not 1:1,
  // since headings are already large/readable and don't need full scaling.
  root.setProperty('--heading-font-scale', (1 + (scale - 1) * 0.25).toFixed(3));
  // Legacy variable kept for anything still referencing it directly.
  root.setProperty('--user-font-scale', scale.toFixed(2));
  try{ localStorage.setItem('jyogi_fs', size); }catch(e){}
  currentFS = size;
}

function resetFontScale(){
  const root = document.documentElement.style;
  root.setProperty('--body-font-scale', '1');
  root.setProperty('--small-important-scale', '1');
  root.setProperty('--heading-font-scale', '1');
  root.setProperty('--user-font-scale', '1');
  try{ localStorage.removeItem('jyogi_fs'); }catch(e){}
  currentFS = FS_DEFAULT;
}

function changeFontSize(dir){
  if(dir === 0){ resetFontScale(); return; }
  const next = currentFS + dir * FS_STEP;
  if(next >= FS_MIN && next <= FS_MAX) applyFontSize(next);
}

function sanitizeHTML(str){
  if(!str) return '';
  var d=document.createElement('div');
  d.textContent=String(str);
  return d.innerHTML;
}

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
  // Server-side logging removed — LOG_SECRET must not be in browser JS
}

function openWhatsApp(msg, analyticsText){
  /* V2.5 privacy fix: analyticsText is an OPTIONAL, pre-scrubbed string
   * for logging/GA4 use. When a caller supplies it, that string (never
   * the raw msg) is what reaches saveLog()/gtag() — so any personal
   * data the user typed into msg (name, birth details, etc.) never
   * leaves the browser except inside the WhatsApp deep link itself,
   * which is the user's own message to Jyogi and is unaffected by this
   * change. When analyticsText is omitted, behaviour is EXACTLY as
   * before (msg.slice(...)) — every pre-existing caller of
   * openWhatsApp() is unaffected by this fix. */
  var logText = (typeof analyticsText === 'string') ? analyticsText : msg;
  // Log every WhatsApp booking click
  saveLog({ type:'whatsapp_booking', message: logText.slice(0,120) });
  // GA4 conversion event — the key metric (WhatsApp booking intent)
  if(typeof gtag==='function'){
    gtag('event','whatsapp_booking',{ message_preview: logText.slice(0,80) });
  }
  window.location.href=`https://wa.me/${WA_NUMBER}?text=${encodeURIComponent(msg)}`;
}

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

function isRazorpayUrl(value) {
  try {
    const url = new URL(value);

    return (
      url.protocol === 'https:' &&
      !url.username &&          // reject https://user@rzp.io/... credential tricks
      !url.password &&
      !url.port &&              // reject non-standard ports
      (
        url.hostname === 'rzp.io' ||
        url.hostname === 'pages.razorpay.com'
      )
    );
  } catch {
    return false;
  }
}

function showPaymentStatus(message){
  const status = document.getElementById('payment-status');
  if (status) status.textContent = message;
}

function timeKbdInput(which, el){
  el.value = el.value.replace(/[^0-9]/g,'').slice(0,2);
  var n = parseInt(el.value,10);
  var valid = false, stored = '';
  if(which==='hour'){
    if(!isNaN(n) && n>=1 && n<=12){ valid=true; stored=String(n).padStart(2,'0'); }
  } else { // min
    if(!isNaN(n) && n>=0 && n<=59){ valid=true; stored=String(n).padStart(2,'0'); }
  }
  if(el.value.length && !valid){ el.classList.add('invalid'); return; }
  el.classList.remove('invalid');
  if(!valid) return;
  // Update hidden field
  var hidId = which==='hour' ? 'time-hour' : 'time-min';
  var hf = document.getElementById(hidId);
  if(hf) hf.value = stored;
  // Scroll the matching spinner to this value
  _scrollSpinnerTo(which==='hour'?'spin-hour-track':'spin-min-track', stored);
}

function _scrollSpinnerTo(trackId, val){
  var track = document.getElementById(trackId);
  if(!track) return;
  var items = Array.prototype.slice.call(track.querySelectorAll('.spinner-item'));
  var idx = items.findIndex(function(it){ return it.dataset.val === val; });
  if(idx < 0) return;
  var itemH = window._spinnerItemH || 48;
  track.scrollTop = idx * itemH;
  // Update active highlight if helper exists
  var hidId = trackId==='spin-hour-track' ? 'time-hour' : 'time-min';
  if(typeof updateSpinnerActive==='function') updateSpinnerActive(track, hidId);
}

function _syncTimeSpinner(){
  var h=document.getElementById('time-hour'), m=document.getElementById('time-min');
  var kh=document.getElementById('kbd-hour'), km=document.getElementById('kbd-min');
  if(kh && h && document.activeElement!==kh) kh.value=h.value;
  if(km && m && document.activeElement!==km) km.value=m.value;
}

function _setTimeVal(type, v, l){
  if(type==='hour'){
    var hf=document.getElementById('time-hour'); if(hf) hf.value=String(parseInt(v,10)).padStart(2,'0');
    if(typeof _syncTimeSpinner==='function') _syncTimeSpinner();
  } else if(type==='min'){
    var mf=document.getElementById('time-min'); if(mf) mf.value=v;
    if(typeof _syncTimeSpinner==='function') _syncTimeSpinner();
  }
}

function _pickerValidate(type, raw){
  // Returns {ok, v, l} — v=stored value, l=display label
  var n = parseInt(raw, 10);
  if(isNaN(n)) return {ok:false};
  if(type==='day'){
    if(n<1||n>31) return {ok:false};
    return {ok:true, v:String(n).padStart(2,'0'), l:String(n).padStart(2,'0')};
  }
  if(type==='month'){
    if(n<1||n>12) return {ok:false};
    return {ok:true, v:String(n).padStart(2,'0'), l:(typeof _MONTHS!=='undefined'?_MONTHS[n-1]:String(n))};
  }
  if(type==='year'){
    var yNow=new Date().getFullYear();
    if(n<1900||n>yNow) return {ok:false};
    return {ok:true, v:String(n), l:String(n)};
  }
  if(type==='hour'){
    if(n<1||n>12) return {ok:false};
    return {ok:true, v:String(n), l:String(n).padStart(2,'0')};
  }
  if(type==='min'){
    if(n<0||n>59) return {ok:false};
    return {ok:true, v:String(n).padStart(2,'0'), l:String(n).padStart(2,'0')};
  }
  return {ok:false};
}

function pickerKbdInput(el){
  // Strip non-digits, live-validate
  el.value = el.value.replace(/[^0-9]/g,'').slice(0,4);
  var type = _pickerKbdCtx ? _pickerKbdCtx.type : _pt;
  var res = _pickerValidate(type, el.value);
  if(el.value.length && !res.ok){ el.classList.add('invalid'); }
  else { el.classList.remove('invalid'); }
}

function pickerKbdKey(ev){
  if(ev.key==='Enter'){ ev.preventDefault(); pickerKbdConfirm(); }
}

function pickerKbdConfirm(){
  var el = document.getElementById('picker-kbd-input');
  var type = _pickerKbdCtx ? _pickerKbdCtx.type : _pt;
  var res = _pickerValidate(type, el.value);
  if(!res.ok){ el.classList.add('invalid'); el.focus(); return; }
  // Route to the correct setter — compat vs chart
  if(_pickerKbdCtx && _pickerKbdCtx.kind==='comp'){
    pickCompVal(res.v, res.l);
  } else {
    // chart day/month/year/hour/min — reuse pickVal via a synthetic element
    pickVal({dataset:{v:res.v, l:res.l}});
  }
}

function _resetPickerKbd(){
  var el=document.getElementById('picker-kbd-input');
  if(el){ el.value=''; el.classList.remove('invalid'); }
}

function _clampInt(v, lo, hi){
  var n = parseInt(String(v).replace(/[^0-9]/g,''),10);
  if(isNaN(n)) return null;
  if(n<lo) n=lo; if(n>hi) n=hi;
  return n;
}

function syncDateInput(part, raw){
  var clean = String(raw).replace(/[^0-9]/g,'');
  var inp = document.getElementById('dob-'+part+'-input');
  var hid = document.getElementById('dob-'+part);
  if(inp) inp.value = clean;
  // Store live (validated on blur). Keep hidden roughly in sync for partials.
  if(hid) hid.value = clean;
  if(inp){ inp.classList.toggle('empty', clean===''); inp.classList.toggle('filled', clean!==''); }
}

function normalizeDateInput(part){
  var inp = document.getElementById('dob-'+part+'-input');
  var hid = document.getElementById('dob-'+part);
  if(!inp) return;
  var raw = inp.value;
  if(raw===''){ if(hid) hid.value=''; inp.classList.add('empty'); inp.classList.remove('filled'); return; }
  var v;
  if(part==='day')   v=_clampInt(raw,1,31);
  else if(part==='month') v=_clampInt(raw,1,12);
  else /*year*/      v=_clampInt(raw,1900,new Date().getFullYear());
  if(v===null){ inp.value=''; if(hid) hid.value=''; inp.classList.add('empty'); return; }
  var disp = (part==='year') ? String(v) : String(v).padStart(2,'0');
  inp.value = disp;
  if(hid) hid.value = disp;
  inp.classList.remove('empty'); inp.classList.add('filled');
}

function dateInputKey(ev, next){
  // Auto-advance: Enter or reaching maxlength moves to next field
  if(ev.key==='Enter'){
    ev.preventDefault();
    normalizeDateInput(ev.target.id.replace('dob-','').replace('-input',''));
    _focusNextDate(next);
    return;
  }
}

function _focusNextDate(next){
  if(next==='month'){ var e=document.getElementById('dob-month-input'); if(e) e.focus(); }
  else if(next==='year'){ var e=document.getElementById('dob-year-input'); if(e) e.focus(); }
  else if(next==='done'){ var e=document.getElementById('time-hour-input'); if(e) e.focus(); }
}

function syncTimeInput(part, raw){
  var clean = String(raw).replace(/[^0-9]/g,'');
  var inp = document.getElementById('time-'+part+'-input');
  var hid = document.getElementById('time-'+part);
  if(inp) inp.value = clean;
  if(hid) hid.value = clean;
}

function normalizeTimeInput(part){
  var inp = document.getElementById('time-'+part+'-input');
  var hid = document.getElementById('time-'+part);
  if(!inp) return;
  var raw = inp.value;
  if(part==='hour'){
    var n = parseInt(String(raw).replace(/[^0-9]/g,''),10);
    if(isNaN(n)){ n = 8; }
    // Smart 24-hour detection — NEVER silently clamp 00->01 or 13-23 to something wrong.
    // 00 means 12 AM (midnight). 13-23 means 1PM-11PM. 12 stays 12 (needs AM/PM to disambiguate noon/midnight).
    if(n === 0){
      n = 12;
      setAMPM('AM');
    } else if(n >= 13 && n <= 23){
      n = n - 12;
      setAMPM('PM');
    } else if(n > 23){
      n = 12; // genuinely invalid input (24+) — fall back safely, no silent hour-shift
    }
    // n is now correctly 1-12 for display
    var disp = String(n).padStart(2,'0');
    inp.value = disp;
    if(hid) hid.value = disp;
    return;
  }
  // minutes
  var v = _clampInt(raw,0,59);
  if(v===null){ v = 0; }
  var disp2 = String(v).padStart(2,'0');
  inp.value = disp2;
  if(hid) hid.value = disp2;
}

function timeInputKey(ev, next){
  if(ev.key==='Enter'){
    ev.preventDefault();
    normalizeTimeInput(ev.target.id.replace('time-','').replace('-input',''));
    if(next==='min'){ var e=document.getElementById('time-min-input'); if(e) e.focus(); }
    else if(next==='done'){ ev.target.blur(); }
  }
}

function openPicker(t){
  _pt=t;
  _pickerKbdCtx={type:t, kind:'chart'};
  _resetPickerKbd();
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
    for(let m=0;m<60;m+=1) items.push({v:String(m).padStart(2,'0'),l:String(m).padStart(2,'0')});
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
  // Write to BOTH the hidden field and the visible hybrid input
  function setPair(hidId, inpId, val, filledClass){
    var h=document.getElementById(hidId); if(h) h.value=val;
    var i=document.getElementById(inpId);
    if(i){ i.value=val; if(filledClass){ i.classList.remove('empty'); i.classList.add('filled'); } }
  }
  if(_pt==='day'){ setPair('dob-day','dob-day-input',v,true); }
  else if(_pt==='month'){ setPair('dob-month','dob-month-input',v,true); }
  else if(_pt==='year'){ setPair('dob-year','dob-year-input',v,true); }
  else if(_pt==='hour'){ setPair('time-hour','time-hour-input',v,false); }
  else if(_pt==='min'){ setPair('time-min','time-min-input',v,false); }
  closePicker();
}

function setBtn(btnId,lblId,l){
  document.getElementById(lblId).textContent=l;
  const b=document.getElementById(btnId);
  b.classList.remove('empty');b.classList.add('filled');
}

function closePicker(){document.getElementById('picker-overlay').classList.remove('open');_pt=null;}

function setAMPM(v){
  var hf=document.getElementById('time-ampm'); if(hf) hf.value=v;
  var lbl=document.getElementById('lbl-ampm'); if(lbl) lbl.textContent=v;
  // legacy spinner elements (null-safe)
  var am=document.getElementById('ampm-am'); if(am) am.classList.toggle('active',v==='AM');
  var pm=document.getElementById('ampm-pm'); if(pm) pm.classList.toggle('active',v==='PM');
}

function toggleAMPM(){
  var cur=document.getElementById('time-ampm').value;
  var next=cur==='AM'?'PM':'AM';
  document.getElementById('time-ampm').value=next;
  var lbl=document.getElementById('lbl-ampm');
  if(lbl) lbl.textContent=next;
}

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
  if(typeof _syncTimeSpinner==='function') _syncTimeSpinner();
}

function updateSpinnerActive(track,hiddenId){
  const cur=document.getElementById(hiddenId).value;
  track.querySelectorAll('.spinner-item').forEach(el=>{
    el.classList.toggle('active',el.dataset.val===cur);
  });
}

function initSpinners(){
  // Time now uses the unified modal picker (openPicker 'hour'/'min') — no spinners to build.
  // Defaults already set on hidden fields and button labels (08:00 AM).
}

function showAdminGate(){window.open('/admin/login.html','_blank');}

function hideAdminGate(){var gm=document.getElementById('pdf-gate-modal'),lr=document.getElementById('pdf-lock-row');if(gm)gm.style.display='none';if(lr)lr.style.display='';}

function verifyAdminGate(){window.open('/admin/login.html','_blank');}

function lockAdminSession(){_adminUnlocked=false;var ur=document.getElementById('pdf-unlocked-row'),lr=document.getElementById('pdf-lock-row');if(ur)ur.style.display='none';if(lr)lr.style.display='';try{fetch(_API_RPT+'/api/admin/logout',{method:'POST',credentials:'include'});}catch(e){}}

function _applyURLParams(){
  try{
    var params = new URLSearchParams(window.location.search);
    if(!params.has('d') && !params.has('city') && !params.has('y')) return;

    function setPair(hidId, inpId, val, mark){
      var h=document.getElementById(hidId); if(h) h.value=val;
      var i=document.getElementById(inpId);
      if(i){ i.value=val; if(mark){ i.classList.remove('empty'); i.classList.add('filled'); } }
    }
    var d  = params.get('d');
    var mn = params.get('m');
    var y  = params.get('y');
    var hr = params.get('h');
    var mi = params.get('min');
    var ap = params.get('ampm');
    var ct = params.get('city');
    var q  = params.get('q');

    if(d!==null)  setPair('dob-day',   'dob-day-input',   String(parseInt(d,10)||'').padStart(2,'0'), true);
    if(mn!==null) setPair('dob-month', 'dob-month-input', String(parseInt(mn,10)||'').padStart(2,'0'), true);
    if(y!==null)  setPair('dob-year',  'dob-year-input',  String(parseInt(y,10)||''), true);
    if(hr!==null) setPair('time-hour', 'time-hour-input', String(parseInt(hr,10)||0).padStart(2,'0'), false);
    if(mi!==null) setPair('time-min',  'time-min-input',  String(parseInt(mi,10)||0).padStart(2,'0'), false);
    if(ap){
      var v=String(ap).toUpperCase();
      if((v==='AM'||v==='PM') && typeof setAMPM==='function') setAMPM(v);
    }
    if(ct){
      var c=document.getElementById('astro-city'); if(c) c.value=ct;
    }
    if(q){
      var qe=document.getElementById('astro-question'); if(qe) qe.value=q;
    }

    // Scroll to the chart form so the user can review and click Calculate
    setTimeout(function(){
      var sec=document.getElementById('astrology');
      if(sec) sec.scrollIntoView({behavior:'smooth', block:'start'});
    }, 150);

    // Optional auto-submit (?auto=1) — runs after a small delay so the form is settled
    if(params.get('auto')==='1'){
      setTimeout(function(){
        if(typeof submitAstrology==='function') submitAstrology();
      }, 900);
    }
  }catch(e){ /* fail silent — don't break page on bad URL */ }
}

