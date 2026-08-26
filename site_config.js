/*
 * site_config.js — Centralised site configuration for Jyogi.
 * Single source of truth for contact details, API base, and headline stats.
 * Loaded (before crystals_data.js) on index.html, crystals.html, privacy.html,
 * numerology.html, and the /admin/* pages.
 *
 * Canonical WhatsApp number: +91 94377 94561  (919437794561).
 * The older 918310319870 is stale — do not reintroduce it.
 *
 * apiBase cutover: change the ONE value below from the Render URL to
 * https://api.jyogi.in when DNS is ready. No other file needs editing.
 */
window.SITE_CONFIG = {
  brand: {
    name: "Jyogi",
    tagline: "Ancient Wisdom. Intelligent Guidance."
  },

  // ── Contact ─────────────────────────────────────────────
  whatsappNumber:  "919437794561",
  whatsappDisplay: "+91 94377 94561",
  whatsappLink:    "https://wa.me/919437794561",
  // Grievance / support uses the same number unless a page documents otherwise.
  grievanceNumber:  "919437794561",
  grievanceDisplay: "+91 94377 94561",

  social: {
    instagram: "https://instagram.com/jyogi.tarot",
    youtube:   "https://youtube.com/@jyogi1008"
  },

  // ── Headline stats (approved canonical values; no unsupported rating) ──
  stats: {
    experience: "20+",   experienceLabel: "Years",
    views:      "2M+",   viewsLabel:      "Views",
    community:  "9.7K+", communityLabel:  "Community"
  },

  // ── API ─────────────────────────────────────────────────
  // ONE-LINE cutover point: Render today → api.jyogi.in at DNS switch.
  apiBase: "https://jyogi-api.onrender.com",

  // ── Service wording ─────────────────────────────────────
  service: {
    whatsappResponse:  "Typically replies within a few hours",
    crystalShipping:   "Dispatched within 24 hours of confirmation"
  }
};

/* Convenience helper: bind [data-config] text and [data-config-href] links.
 * Optional — pages may also read window.SITE_CONFIG directly. */
(function () {
  function val(path, obj) {
    return path.split('.').reduce(function (o, k) { return (o || {})[k]; }, obj);
  }
  function apply() {
    var C = window.SITE_CONFIG; if (!C) return;
    document.querySelectorAll('[data-config]').forEach(function (el) {
      var v = val(el.getAttribute('data-config'), C);
      if (v != null) el.textContent = v;
    });
    document.querySelectorAll('[data-config-href]').forEach(function (el) {
      var v = val(el.getAttribute('data-config-href'), C);
      if (v != null) el.setAttribute('href', v);
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', apply);
  } else { apply(); }
})();
