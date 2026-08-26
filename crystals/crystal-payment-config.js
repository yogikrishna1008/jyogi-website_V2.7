/**
 * crystal-payment-config.js — Jyogi Crystal Bracelet Payment Configuration
 *
 * Loaded by every /crystals/{slug}.html product page AND crystals.html.
 *
 * Add one reusable Razorpay Payment Page URL per bracelet SKU.
 *
 * Empty value:
 *   Buy Now remains hidden and WhatsApp becomes the ordering action.
 *
 * Customers ordering multiple pieces should contact Jyogi on WhatsApp.
 *
 * Rules:
 *  • URLs must be HTTPS on exactly rzp.io or pages.razorpay.com.
 *  • Do NOT place secret keys, API secrets or webhook secrets here.
 *
 * Mode: Test / Live — operator must confirm after creating pages in
 *       the Razorpay Dashboard.
 */

/* jshint esversion: 6 */

// Comments below use the approved GLOBAL Razorpay names (per naming review).
// The live site's product names in crystals_data.js are UNCHANGED for now --
// that rename is a separate, not-yet-authorized step. See the delivery
// report for details.
const CRYSTAL_PAYMENT_PAGES = Object.freeze({
  // Price confirmed by operator: ₹799. NOTE: Reference ID JY-CHAKRA-599 still
  // embeds the OLD ₹599 amount -- this is a cosmetic Razorpay-reporting
  // mismatch only (does not affect the live charge amount), but worth
  // relabelling the Reference ID to JY-CHAKRA-799 in the Dashboard for
  // clean reconciliation later.
  seven_chakra:        'https://rzp.io/rzp/5v3xiYrV',   // Jyogi Chakra Balance Bracelet  ₹799  (see Ref ID note above)
  money_magnet:        'https://rzp.io/rzp/oKQbS0SF',   // Jyogi Wealth Alignment Bracelet     ₹1,199  JY-WEALTH-1199
  
  // money_magnet:        'https://rzp.io/rzp/ofrzqCi9',   // Jyogi Wealth Alignment Bracelet     ₹1,499  JY-WEALTH-1499
  pyrite_solo:         'https://rzp.io/rzp/Ra8Xgsfx',   // Jyogi Pyrite Prosperity Bracelet    ₹799    JY-PYRITE-799
  rose_quartz_love:    'https://rzp.io/rzp/E81goCGV',   // Jyogi Love Harmony Bracelet         ₹999    JY-LOVE-999
  // Price confirmed by operator: crystals_data.js updated to ₹1,699 to match.
  // NOTE: this Payment Page code is 7 characters (vs. 8 elsewhere) -- verify
  // it is not a truncated link with one manual click-through before relying
  // on it for real customers.
  moonstone_pearl:     'https://rzp.io/rzp/ApUrsO9',    // Jyogi Feminine Energy Bracelet  ₹1,699  JY-FEMININE-1699
  green_aventurine:    'https://rzp.io/rzp/3R80Iv0w',   // Jyogi Luck & Opportunity Bracelet   ₹899    JY-LUCK-899
  black_tourmaline:    'https://rzp.io/rzp/gLtaMMH',    // Jyogi Protection Shield Bracelet    ₹1,299  JY-PROTECT-1299 -- CHECK: 7-char code, verify not truncated
  lepidolite_amethyst: 'https://rzp.io/rzp/gl1UacpY',   // Jyogi Inner Calm Bracelet           ₹1,299  JY-CALM-1299
  // Price confirmed by operator: raised to ₹1,699 to match this Razorpay page.
  // NOTE: crystals_data.js "original" (strikethrough) price is also ₹1,699 --
  // identical to the new sale price, so the product page will currently show
  // no discount badge. Confirm whether "original" should be raised (e.g. to
  // show a genuine discount) or left as a straight ₹1,699, no-discount listing.
  tourmaline_cluster:  'https://rzp.io/rzp/ohi9EL3G',   // Jyogi Saturn Grounding Bracelet  ₹1,699  JY-SATURN-1699
  tiger_eye_solo:      'https://rzp.io/rzp/p6uBR6O2',   // Jyogi Courage & Confidence Bracelet ₹799    JY-COURAGE-799
  fluorite_clear:      'https://rzp.io/rzp/AqI3jE4o',   // Jyogi Focus & Clarity Bracelet      ₹999    JY-FOCUS-999
  lapis_amethyst:      'https://rzp.io/rzp/at0tzuB',    // Jyogi Intuition & Insight Bracelet  ₹1,599  JY-INTUITION-1599 -- CHECK: 7-char code, verify not truncated
  sunstone_bronzite:   'https://rzp.io/rzp/6TfiCVVN',   // Jyogi Executive Presence Bracelet   ₹1,899  JY-EXECUTIVE-1899

  shani_bracelet:      'https://rzp.io/rzp/l5bS564Y',   // Jyogi Saturn Shield Bracelet — Razorpay URL TBD

});

/**
 * Exact-host HTTPS validation.
 * Accepts ONLY https: on exactly rzp.io or pages.razorpay.com.
 * Rejects: http, credentials (user@), non-standard ports, subdomains of razorpay.com,
 * lookalikes (rzp.io.evil.com), substring matches, empty strings.
 *
 * @param  {string} value
 * @returns {boolean}
 */
function isRazorpayUrl(value) {
  if (!value) return false;
  try {
    const url = new URL(value);
    return (
      url.protocol === 'https:' &&
      !url.username &&
      !url.password &&
      !url.port &&
      (url.hostname === 'rzp.io' || url.hostname === 'pages.razorpay.com')
    );
  } catch {
    return false;
  }
}
