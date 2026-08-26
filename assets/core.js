/* ── Jyogi core.js — shared: nav, theme, i18n, stars (loaded on every page) ── */
var currentLang = 'en';
var currentFS = 100; const FS_STEP=10, FS_MIN=80, FS_MAX=130, FS_DEFAULT=100, FS_BASE_PX=22;

var I18N = {"en":{"auto.book_your_reading":"Book Your Reading","auto.confused_stuck_or_lost":"Confused, Stuck, or Lost?","auto.confused_stuck_searching_for":"Confused. Stuck. Searching for answers. Here's what happened after their reading.","auto.discover_your_life_path_numb":"Discover your life path number, lucky numbers, and personal year cycle from your date of birth.","auto.draw_your_cards_instantly_si":"Draw your cards instantly. Single card, Past-Present-Future, Celtic Cross, Love & Career spreads.","auto.each_bracelet_is_hand_select":"Each bracelet is hand-selected, cleansed under the full moon, and charged with planetary mantras. Order via WhatsApp for personalised guidance.","auto.each_reading_is_powered_by_a":"Each reading is powered by ancient Vedic wisdom and AI precision — deeply personal, always accurate.","auto.enter_both_birth_dates_for_a":"Enter both birth dates for a Vedic compatibility reading — Moon sign Kuta, Nakshatra match, and Dasha harmony.","auto.free_kundali_with_lagna_naks":"Free Kundali with Lagna, Nakshatra, Dasha & Sadhe Sati. Powered by Swiss Ephemeris.","auto.hand_cleansed_bracelets_pres":"Hand-cleansed bracelets prescribed by planet and chakra. 16 sacred combinations.","auto.how_can_jyogi_help":"How Can Jyogi Help?","auto.in_depth_articles_on_vedic_a":"In-depth articles on Vedic astrology, Tarot, remedies, and timing — written by Jyogi from 20+ years of practice.","auto.love_amp_relationship_match":"Love & Relationship Match","auto.vedic_panchang_for_the_next_":"Vedic panchang for the next 7 days — tap a day to see what's auspicious for marriage, travel, business, and more.","auto.vedic_wisdom_amp_guides":"Vedic Wisdom & Guides","auto.view_all_articles":"VIEW ALL ARTICLES","auto.we_begin_every_reading_with_":"We begin every reading with a prayer to the divine. May these sacred energies guide your path.","auto.your_dreams_carry_hidden_mes":"Your dreams carry hidden messages. Record yours and receive a Tarot card — or let Jyogi interpret the deeper meaning.","blog.section_desc":"In-depth articles on Vedic astrology Tarot remedies and timing.","blog.section_title":"Vedic Wisdom & Guides","blog.view_all":"View All Articles","footer.copyright":"© 2026 Jyogi AI. All rights reserved.","footer.tagline":"Vedic · Tarot · Sacred Crystals","form.calculate_chart":"🪐 Calculate My Vedic Chart","form.city":"City of Birth","form.dob":"Date of Birth","form.full_name":"Full Name","form.question":"Your Question (optional)","form.tob":"Time of Birth","hero.cta_primary":"Book a Personal Reading","hero.free_chart":"Free Birth Chart","hero.free_chart_sub":"Vedic · Swiss Ephemeris","hero.free_tarot":"Free Tarot","hero.free_tarot_sub":"Draw your cards now","hero.subtitle":"Your stars hold the answer. Birth chart, Tarot and crystal energy — all in one place.","hero.tagline":"Confused, Stuck, or Lost? The path is here.","nav.astrology":"Astrology","nav.blog":"Blog","nav.book_reading":"Book Reading","nav.crystals":"Crystals","nav.logo_tagline":"Vedic · Tarot · Sacred","nav.numerology":"Numerology","nav.tarot":"Tarot","section.about_title":"The Person Behind Jyogi","section.chart_desc":"Enter your birth details for a complete sidereal Vedic chart.","section.chart_title":"Your Birth Chart","section.compat_title":"Love & Relationship Match","section.dreams_title":"Dream Journal","section.gallery_title":"Divine Blessings","section.how_title":"How a Session Works","section.muhurta_title":"Muhurta — Lucky Days","section.reviews_title":"They Were Exactly Where You Are","section.services_desc":"Vedic astrology Tarot Numerology and sacred crystals — choose your path.","section.services_title":"Sacred Services","section.shop_title":"Crystal Bracelets","section.tarot_desc":"Jyogi's intuitive Tarot deck channels meditative energy and ancient wisdom.","section.tarot_title":"Draw Your Cards"},"hi":{"auto.book_your_reading":"अभी बुक करें","auto.confused_stuck_or_lost":"उलझे हुए हैं? रास्ता यहाँ है।","auto.confused_stuck_searching_for":"उलझन। ठहराव। उत्तरों की तलाश। देखिए उनकी रीडिंग के बाद क्या हुआ।","auto.discover_your_life_path_numb":"अपने जन्म तिथि से जीवन पथ अंक और शुभ अंक जानें।","auto.draw_your_cards_instantly_si":"तुरंत कार्ड खींचें। सिंगल, अतीत-वर्तमान-भविष्य, सेल्टिक क्रॉस।","auto.each_bracelet_is_hand_select":"हर ब्रेसलेट हाथ से चुना जाता है, पूर्णिमा पर शुद्ध किया जाता है और ग्रह मंत्रों से अभिमंत्रित। व्यक्तिगत मार्गदर्शन के लिए WhatsApp पर ऑर्डर करें।","auto.each_reading_is_powered_by_a":"हर रीडिंग प्राचीन वैदिक ज्ञान और AI की सटीकता पर आधारित — गहराई से व्यक्तिगत, हमेशा सटीक।","auto.enter_both_birth_dates_for_a":"वैदिक गुण मिलान के लिए दोनों जन्म तिथियाँ भरें — चंद्र राशि कूट, नक्षत्र मिलान और दशा सामंजस्य।","auto.free_kundali_with_lagna_naks":"लग्न, नक्षत्र, दशा और साढ़े-साती के साथ निःशुल्क कुंडली।","auto.hand_cleansed_bracelets_pres":"हस्त-शुद्ध क्रिस्टल कंगन — ग्रह और चक्र के अनुसार निर्धारित।","auto.how_can_jyogi_help":"जयोगी कैसे मदद करेंगे? Vedic astrology, Tarot, Numerology, and sacred crystals — choose your path. वैदिक ज्योतिष, टैरो, अंकशास्त्र और पवित्र क्रिस्टल — अपना मार्ग चुनें।","auto.in_depth_articles_on_vedic_a":"वैदिक ज्योतिष, टैरो, उपाय और शुभ समय पर गहन लेख — जयोगी द्वारा 20+ वर्षों के अनुभव से लिखित।","auto.love_amp_relationship_match":"प्रेम एवं संबंध मिलान","auto.vedic_panchang_for_the_next_":"अगले 7 दिनों का वैदिक पंचांग — किसी दिन पर टैप करें और जानें विवाह, यात्रा, व्यापार आदि के लिए शुभ समय।","auto.vedic_wisdom_amp_guides":"वैदिक ज्ञान एवं मार्गदर्शिका","auto.view_all_articles":"सभी लेख देखें","auto.we_begin_every_reading_with_":"हम हर रीडिंग की शुरुआत ईश्वर की प्रार्थना से करते हैं। ये पवित्र ऊर्जाएँ आपके मार्ग को आलोकित करें।","auto.your_dreams_carry_hidden_mes":"आपके सपनों में छिपे संदेश होते हैं। अपना सपना दर्ज करें और एक टैरो कार्ड पाएँ — या जयोगी से गहरा अर्थ जानें।","blog.section_desc":"वैदिक ज्योतिष टैरो उपाय और शुभ समय पर गहन लेख।","blog.section_title":"वैदिक ज्ञान एवं मार्गदर्शिका","blog.view_all":"सभी लेख देखें","footer.copyright":"© 2026 जयोगी AI. सर्वाधिकार सुरक्षित।","footer.tagline":"वैदिक · टैरो · पवित्र क्रिस्टल","form.calculate_chart":"🪐 मेरी वैदिक कुंडली देखें","form.city":"जन्म स्थान","form.dob":"जन्म तिथि","form.full_name":"पूरा नाम","form.question":"आपका प्रश्न (वैकल्पिक)","form.tob":"जन्म समय","hero.cta_primary":"पर्सनल रीडिंग बुक करें","hero.free_chart":"निःशुल्क कुंडली","hero.free_chart_sub":"वैदिक · स्विस एफेमेरिस","hero.free_tarot":"निःशुल्क टैरो","hero.free_tarot_sub":"अभी अपने कार्ड खींचें","hero.subtitle":"आपके सितारों में जवाब है। जन्मपत्री, टैरो और ऊर्जा — सब एक जगह।","hero.tagline":"उलझे हुए हैं? रास्ता यहाँ है।","nav.astrology":"ज्योतिष","nav.blog":"ब्लॉग","nav.book_reading":"बुक करें","nav.crystals":"क्रिस्टल","nav.logo_tagline":"वैदिक · टैरो · पवित्र","nav.numerology":"अंकशास्त्र","nav.tarot":"टैरो","section.about_title":"जयोगी के पीछे का व्यक्ति","section.chart_desc":"पूर्ण वैदिक जन्मपत्री के लिए अपना जन्म विवरण दर्ज करें।","section.chart_title":"आपकी जन्म कुंडली","section.compat_title":"प्रेम एवं संबंध मिलान","section.dreams_title":"स्वप्न डायरी","section.gallery_title":"दिव्य आशीर्वाद","section.how_title":"सत्र कैसे होता है","section.muhurta_title":"मुहूर्त — शुभ दिन","section.reviews_title":"वे भी ठीक आपकी जगह थे","section.services_desc":"वैदिक ज्योतिष टैरो अंकशास्त्र और पवित्र क्रिस्टल — अपना मार्ग चुनें।","section.services_title":"पवित्र सेवाएँ","section.shop_title":"क्रिस्टल ब्रेसलेट","section.tarot_desc":"जयोगी का सहज टैरो डेक ध्यान-ऊर्जा और प्राचीन ज्ञान का संचार करता है।","section.tarot_title":"अपने कार्ड चुनें"},"or":{"auto.book_your_reading":"ବର୍ତ୍ତମାନ ବୁକ୍ କରନ୍ତୁ","auto.confused_stuck_or_lost":"ବିଭ୍ରାନ୍ତ, ଅଟକି, କିମ୍ବା ହଜି ଯାଇଛନ୍ତି?","auto.confused_stuck_searching_for":"ଦ୍ୱନ୍ଦ୍ୱ। ଅଚଳାବସ୍ଥା। ଉତ୍ତରର ସନ୍ଧାନ। ଦେଖନ୍ତୁ ସେମାନଙ୍କ ରିଡିଂ ପରେ କଣ ହେଲା।","auto.discover_your_life_path_numb":"ଆପଣଙ୍କ ଜନ୍ମ ତାରିଖରୁ ଜୀବନ ପଥ ଅଙ୍କ ଓ ଶୁଭ ଅଙ୍କ ଜାଣନ୍ତୁ।","auto.draw_your_cards_instantly_si":"ତୁରନ୍ତ କାର୍ଡ ଟାଣନ୍ତୁ। ଏକକ, ଅତୀତ-ବର୍ତ୍ତମାନ-ଭବିଷ୍ୟତ, ସେଲ୍ଟିକ୍ କ୍ରସ୍।","auto.each_bracelet_is_hand_select":"ପ୍ରତ୍ୟେକ ବ୍ରେସଲେଟ୍ ହାତରେ ବଛାଯାଏ, ପୂର୍ଣ୍ଣିମାରେ ଶୁଦ୍ଧ କରାଯାଏ ଓ ଗ୍ରହ ମନ୍ତ୍ରରେ ଅଭିମନ୍ତ୍ରିତ। ବ୍ୟକ୍ତିଗତ ମାର୍ଗଦର୍ଶନ ପାଇଁ WhatsApp ରେ ଅର୍ଡର କରନ୍ତୁ।","auto.each_reading_is_powered_by_a":"ପ୍ରତ୍ୟେକ ରିଡିଂ ପ୍ରାଚୀନ ବୈଦିକ ଜ୍ଞାନ ଓ AI ସଠିକତା ଉପରେ ଆଧାରିତ — ଗଭୀର ଭାବେ ବ୍ୟକ୍ତିଗତ, ସର୍ବଦା ସଠିକ।","auto.enter_both_birth_dates_for_a":"ବୈଦିକ ଗୁଣ ମିଳନ ପାଇଁ ଉଭୟ ଜନ୍ମ ତାରିଖ ଦିଅନ୍ତୁ — ଚନ୍ଦ୍ର ରାଶି କୂଟ, ନକ୍ଷତ୍ର ମିଳନ ଓ ଦଶା ସମନ୍ୱୟ।","auto.free_kundali_with_lagna_naks":"ଲଗ୍ନ, ନକ୍ଷତ୍ର, ଦଶା ଓ ସାଢ଼େ-ସାତୀ ସହିତ ନିଃଶୁଳ୍କ କୁଣ୍ଡଳୀ।","auto.hand_cleansed_bracelets_pres":"ହସ୍ତ-ଶୁଦ୍ଧ କ୍ରିଷ୍ଟାଲ୍ କଙ୍ଗନ — ଗ୍ରହ ଓ ଚକ୍ର ଅନୁସାରେ ନିର୍ଦ୍ଧାରିତ।","auto.how_can_jyogi_help":"ବୈଦିକ ଜ୍ୟୋତିଷ, ଟାରୋ, ଅଙ୍କଶାସ୍ତ୍ର ଓ ପବିତ୍ର କ୍ରିଷ୍ଟାଲ୍ — ଆପଣଙ୍କ ମାର୍ଗ ବାଛନ୍ତୁ।","auto.in_depth_articles_on_vedic_a":"ବୈଦିକ ଜ୍ୟୋତିଷ, ଟାରୋ, ଉପାୟ ଓ ଶୁଭ ସମୟ ଉପରେ ଗଭୀର ପ୍ରବନ୍ଧ — ଜୟୋଗୀଙ୍କ ୨୦+ ବର୍ଷର ଅଭିଜ୍ଞତାରୁ।","auto.love_amp_relationship_match":"ପ୍ରେମ ଓ ସମ୍ପର୍କ ମିଳନ","auto.vedic_panchang_for_the_next_":"ଆଗାମୀ ୭ ଦିନର ବୈଦିକ ପଞ୍ଚାଙ୍ଗ — କୌଣସି ଦିନ ଉପରେ ଟ୍ୟାପ୍ କରନ୍ତୁ ଓ ବିବାହ, ଯାତ୍ରା, ବ୍ୟବସାୟ ଆଦି ପାଇଁ ଶୁଭ ସମୟ ଜାଣନ୍ତୁ।","auto.vedic_wisdom_amp_guides":"ବୈଦିକ ଜ୍ଞାନ ଓ ମାର୍ଗଦର୍ଶିକା","auto.view_all_articles":"ସମସ୍ତ ପ୍ରବନ୍ଧ ଦେଖନ୍ତୁ","auto.we_begin_every_reading_with_":"ଆମେ ପ୍ରତ୍ୟେକ ରିଡିଂ ଈଶ୍ୱରଙ୍କ ପ୍ରାର୍ଥନାରୁ ଆରମ୍ଭ କରୁ। ଏହି ପବିତ୍ର ଶକ୍ତି ଆପଣଙ୍କ ମାର୍ଗକୁ ଆଲୋକିତ କରୁ।","auto.your_dreams_carry_hidden_mes":"ଆପଣଙ୍କ ସ୍ୱପ୍ନରେ ଲୁକ୍କାୟିତ ସନ୍ଦେଶ ଥାଏ। ଆପଣଙ୍କ ସ୍ୱପ୍ନ ଲେଖନ୍ତୁ ଓ ଗୋଟିଏ ଟାରୋ କାର୍ଡ ପାଆନ୍ତୁ — କିମ୍ବା ଜୟୋଗୀଙ୍କଠାରୁ ଗଭୀର ଅର୍ଥ ଜାଣନ୍ତୁ।","blog.section_desc":"ବୈଦିକ ଜ୍ୟୋତିଷ ଟାରୋ ଉପାୟ ଓ ଶୁଭ ସମୟ ଉପରେ ଗଭୀର ପ୍ରବନ୍ଧ।","blog.section_title":"ବୈଦିକ ଜ୍ଞାନ ଓ ମାର୍ଗଦର୍ଶିକା","blog.view_all":"ସମସ୍ତ ପ୍ରବନ୍ଧ ଦେଖନ୍ତୁ","footer.copyright":"© 2026 ଜୟୋଗୀ AI. ସର୍ବାଧିକାର ସୁରକ୍ଷିତ।","footer.tagline":"ବୈଦିକ · ଟାରୋ · ପବିତ୍ର କ୍ରିଷ୍ଟାଲ୍","form.calculate_chart":"🪐 ମୋ ବୈଦିକ କୁଣ୍ଡଳୀ ଦେଖନ୍ତୁ","form.city":"ଜନ୍ମ ସ୍ଥାନ","form.dob":"ଜନ୍ମ ତାରିଖ","form.full_name":"ପୂରା ନାମ","form.question":"ଆପଣଙ୍କ ପ୍ରଶ୍ନ (ଇଚ୍ଛାଧୀନ)","form.tob":"ଜନ୍ମ ସମୟ","hero.cta_primary":"ବ୍ୟକ୍ତିଗତ ରିଡିଂ ବୁକ୍ କରନ୍ତୁ","hero.free_chart":"ନିଃଶୁଳ୍କ କୁଣ୍ଡଳୀ","hero.free_chart_sub":"ବୈଦିକ · ସ୍ୱିସ୍ ଏଫେମେରିସ୍","hero.free_tarot":"ନିଃଶୁଳ୍କ ଟାରୋ","hero.free_tarot_sub":"ବର୍ତ୍ତମାନ ଆପଣଙ୍କ କାର୍ଡ ଟାଣନ୍ତୁ","hero.subtitle":"ଆପଣଙ୍କ ତାରାମାନଙ୍କରେ ଉତ୍ତର ଅଛି। କୁଣ୍ଡଳୀ, ଟାରୋ ଓ ଶକ୍ତି — ସବୁ ଏକ ସ୍ଥାନରେ।","hero.tagline":"ବିଭ୍ରାନ୍ତ, ଅଟକି, କିମ୍ବା ହଜି ଯାଇଛନ୍ତି? ପଥ ଏଠାରେ।","nav.astrology":"ଜ୍ୟୋତିଷ","nav.blog":"ବ୍ଲଗ୍","nav.book_reading":"ବୁକ୍ କରନ୍ତୁ","nav.crystals":"କ୍ରିଷ୍ଟାଲ୍","nav.logo_tagline":"ବୈଦିକ · ଟାରୋ · ପବିତ୍ର","nav.numerology":"ଅଙ୍କଶାସ୍ତ୍ର","nav.tarot":"ଟାରୋ","section.about_title":"ଜୟୋଗୀଙ୍କ ପଛର ବ୍ୟକ୍ତି","section.chart_desc":"ସମ୍ପୂର୍ଣ୍ଣ ବୈଦିକ କୁଣ୍ଡଳୀ ପାଇଁ ଆପଣଙ୍କ ଜନ୍ମ ବିବରଣୀ ଦିଅନ୍ତୁ।","section.chart_title":"ଆପଣଙ୍କ ଜନ୍ମ କୁଣ୍ଡଳୀ","section.compat_title":"ପ୍ରେମ ଓ ସମ୍ପର୍କ ମିଳନ","section.dreams_title":"ସ୍ୱପ୍ନ ଡାଏରୀ","section.gallery_title":"ଦିବ୍ୟ ଆଶୀର୍ବାଦ","section.how_title":"ସେସନ୍ କିପରି ହୁଏ","section.muhurta_title":"ମୁହୂର୍ତ୍ତ — ଶୁଭ ଦିନ","section.reviews_title":"ସେମାନେ ମଧ୍ୟ ଠିକ୍ ଆପଣଙ୍କ ଜାଗାରେ ଥିଲେ","section.services_desc":"ବୈଦିକ ଜ୍ୟୋତିଷ ଟାରୋ ଅଙ୍କଶାସ୍ତ୍ର ଓ ପବିତ୍ର କ୍ରିଷ୍ଟାଲ୍ — ଆପଣଙ୍କ ମାର୍ଗ ବାଛନ୍ତୁ।","section.services_title":"ପବିତ୍ର ସେବାସମୂହ","section.shop_title":"କ୍ରିଷ୍ଟାଲ୍ ବ୍ରେସଲେଟ୍","section.tarot_desc":"ଜୟୋଗୀଙ୍କ ସହଜ ଟାରୋ ଡେକ୍ ଧ୍ୟାନ-ଶକ୍ତି ଓ ପ୍ରାଚୀନ ଜ୍ଞାନ ସଞ୍ଚାର କରେ।","section.tarot_title":"ଅପଣଙ୍କ କାର୍ଡ ବାଛନ୍ତୁ"}};

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

function _mobileNavEscHandler(e){
  if(e.key === 'Escape') toggleMobileNav();
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
}

function setTheme(theme){
  document.body.classList.remove('light-theme','warm-theme');
  if(theme === 'light') document.body.classList.add('light-theme');
  else if(theme === 'warm') document.body.classList.add('warm-theme');
  applyThemeUI(theme);
  try{ localStorage.setItem('jyogi_theme', theme); }catch(e){}
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

function sanitizeHTML(str){
  if(!str) return '';
  var d=document.createElement('div');
  d.textContent=String(str);
  return d.innerHTML;
}

function applyFontSize(size){
  // size is a PERCENTAGE (80-130), not literal pixels — was previously setting
  // body.style.fontSize to e.g. "110px" directly, making body text comically
  // huge the moment anyone clicked A+. Scale from the real base (22px) instead.
  document.body.style.fontSize = (FS_BASE_PX * size/100).toFixed(1) + 'px';
  document.documentElement.style.setProperty('--user-font-scale', (size/100).toFixed(2));
  try{ localStorage.setItem('jyogi_fs', size); }catch(e){}
  currentFS = size;
}

function changeFontSize(dir){
  if(dir === 0){ applyFontSize(FS_DEFAULT); return; }
  const next = currentFS + dir * FS_STEP;
  if(next >= FS_MIN && next <= FS_MAX) applyFontSize(next);
}

/* ── boot: stars + restore saved language/theme/font ── */
if(document.readyState==='complete') _initStars();
else window.addEventListener('load', _initStars);
(function(){
  try{
    var lang = localStorage.getItem('jyogi_lang');
    if(lang === 'hi'){ setLang('hi'); if(typeof updateMobileLang==='function') updateMobileLang('hi'); }
    else if(lang === 'or'){ setLang('or'); if(typeof updateMobileLang==='function') updateMobileLang('or'); }
    var theme = localStorage.getItem('jyogi_theme');
    if(theme === 'light' || theme === 'warm'){ setTheme(theme); }
    var fs = localStorage.getItem('jyogi_fs');
    if(fs) applyFontSize(parseInt(fs));
  }catch(e){}
})();
