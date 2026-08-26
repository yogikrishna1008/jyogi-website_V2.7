/**
 * product-page.js — Jyogi Crystal Bracelet Product Page Engine
 *
 * Loaded by every /crystals/{slug}.html wrapper.
 * Reads <body data-product-sku="seven_chakra">, finds the matching
 * entry in BRACELETS (from ../crystals_data.js), and populates the page.
 *
 * DEPENDENCIES (must load before this script):
 *   ../crystals_data.js              → BRACELETS array
 *   crystal-payment-config.js        → CRYSTAL_PAYMENT_PAGES + isRazorpayUrl
 *
 * Crystal orders WhatsApp: 919437794561
 * (Separate from the consultation number used in index.html)
 */

(function () {
  'use strict';

  var WA_CRYSTAL = '919437794561';

  /* ── Asset path resolver ─────────────────────────────────────────────────
   * Product pages live in /crystals/ but crystals_data.js stores paths as
   * root-relative-looking strings such as "image/seven_chakra.jpg".
   * Prepend "../" so they resolve correctly from /crystals/.
   * Absolute URLs (https://, data:, blob:) are returned unchanged.
   * A leading "/" is stripped before prepending "..".
   */
  function resolveProductAsset(src) {
    if (!src) return '';
    if (/^(https?:|data:|blob:)/i.test(src)) return src;
    return '../' + String(src).replace(/^\/+/, '');
  }

  /* ── V2.5 optimised asset resolver ────────────────────────────────────
   * Maps an original image path (e.g. "image/shani_bracelet.jpg") to its
   * pre-generated AVIF/WebP/JPEG derivatives under image/opt/, using the
   * manifest built at image-processing time. Products without derivatives
   * (most SKUs currently lack real photography) fall through untouched —
   * initGallery() below uses the plain original <img> path exactly as
   * before, so this is purely additive and cannot regress any SKU it
   * doesn't cover. Never overwrites or references original files. */
  var OPTIMIZED_BASES = {
    /* sku -> [basename, basename2, ...] matching image/opt/<base>-<w>.<ext> */
    shani_bracelet:      ['shani_bracelet','shani_bracelet_2','shani_bracelet_3'],
    money_magnet:        ['money_magnet','money_magnet_2','money_magnet_3','money_magnet_4'],
    seven_chakra:        ['seven_chakra'],
    rose_quartz_love:    ['rose_quartz','rose_quartz_2','rose_quartz_3'],
    pyrite_solo:         ['pyrite_solo','pyrite_solo2','pyrite_solo3','pyrite_solo4'],
    moonstone_pearl:     ['moonstone_pearl','moonstone_pearl_2','moonstone_pearl_3'],
    dhan_yog_rudraksha:  ['DhanYog1','DhanYog2','DhanYog3']
  };

  function optimizedBaseFor(sku, index) {
    var bases = OPTIMIZED_BASES[sku];
    if (!bases || !bases[index]) return null;
    return bases[index];
  }

  /* Builds a <picture> for a given (sku, image-index, alt, priority) if an
   * optimised derivative exists; otherwise returns null so the caller can
   * fall back to the plain <img> path unchanged. */
  function buildOptimizedPicture(sku, index, src, alt, isPrimary) {
    var base = optimizedBaseFor(sku, index);
    if (!base) return null;
    var loading = isPrimary ? 'eager' : 'lazy';
    var fp = isPrimary ? ' fetchpriority="high"' : '';
    return '<picture>'
      + '<source type="image/avif" srcset="../image/opt/' + base + '-640.avif 640w, ../image/opt/' + base + '-1152.avif 1152w" sizes="(min-width:1150px) 560px, 100vw">'
      + '<source type="image/webp" srcset="../image/opt/' + base + '-640.webp 640w, ../image/opt/' + base + '-1152.webp 1152w" sizes="(min-width:1150px) 560px, 100vw">'
      + '<img id="pp-main-img" class="pp-main-img" src="../image/opt/' + base + '-640.jpg" alt="' + alt + '"'
      + ' width="1152" height="1152" loading="' + loading + '"' + fp + ' decoding="async"'
      + ' onerror="window.__ppApplyImageFallback && window.__ppApplyImageFallback(this)">'
      + '</picture>';
  }

  /* One-time fallback guard — prevents infinite onerror loops.
   * Main product image: falls back to the real placeholder and hides the
   * thumbnail strip + circular "Personally Prepared" badge, so only one
   * clean placeholder is ever shown.
   * Gallery thumbnail: removed outright rather than swapped to a placeholder,
   * so several broken gallery entries can never produce repeated identical
   * placeholder thumbnails. */
  function applyImageFallback(img) {
    if (img.dataset.fallbackApplied === 'true') {
      img.onerror = null;
      return;
    }
    img.dataset.fallbackApplied = 'true';

    if (img.id === 'pp-main-img') {
      img.src = '../image/crystal-placeholder.jpg';
      var thumbs = document.getElementById('pp-thumbs');
      var badge = document.querySelector('.pp-temple-badge');
      var imgWrap = document.querySelector('.pp-main-img-wrap');
      if (thumbs) thumbs.style.display = 'none';
      if (badge) badge.style.display = 'none';
      /* Reduced mobile footprint while showing a placeholder -- once real
         product photography is available this class never gets applied,
         so the real photo still uses the full square presentation. */
      if (imgWrap) imgWrap.classList.add('pp-placeholder-active');
      return;
    }

    var thumbEl = img.closest('.pp-thumb');
    if (thumbEl) {
      thumbEl.remove();
      return;
    }

    img.src = '../image/crystal-placeholder.jpg';
  }

  /* ── Utility ─────────────────────────────────────────────────────────── */
  function findBracelet(sku) {
    if (typeof BRACELETS === 'undefined') return null;
    return BRACELETS.find(function (b) { return b.id === sku; }) || null;
  }
  function setText(id, val) { var e = document.getElementById(id); if (e) e.textContent = val || ''; }
  function show(id) { var e = document.getElementById(id); if (e) e.style.display = ''; }
  function hide(id) { var e = document.getElementById(id); if (e) e.style.display = 'none'; }

  /* ── Discount percentage ─────────────────────────────────────────────── */
  function discountPct(price, original) {
    try {
      var p = parseInt(String(price).replace(/[^0-9]/g, ''));
      var o = parseInt(String(original).replace(/[^0-9]/g, ''));
      if (o > p) return Math.round((1 - p / o) * 100) + '% OFF';
    } catch (e) {}
    return '';
  }

  /* ── Gallery logic ───────────────────────────────────────────────────────
   * V2.5: if optimised AVIF/WebP derivatives exist for this SKU (checked via
   * OPTIMIZED_BASES), the static <img id="pp-main-img"> is swapped ONCE for
   * a <picture> element built by buildOptimizedPicture(); the id/class are
   * preserved on the inner <img> so every later reference to #pp-main-img
   * (including this same function's own gallery-click handler) keeps
   * working unchanged. SKUs with no derivatives take the exact original
   * code path — this function cannot regress them. ─────────────────────── */
  function initGallery(b) {
    var mainImg = document.getElementById('pp-main-img');
    if (!mainImg) return;

    var alt = b.name + ' crystal bracelet';
    var firstPicture = buildOptimizedPicture(b.id, 0, b.img, alt, true);
    if (firstPicture) {
      var wrap = mainImg.closest('.pp-main-img-wrap') || mainImg.parentNode;
      var temp = document.createElement('div');
      temp.innerHTML = firstPicture;
      var newPicture = temp.firstChild;
      wrap.replaceChild(newPicture, mainImg);
      mainImg = document.getElementById('pp-main-img'); /* re-fetch: new node, same id */
    } else {
      /* Unmodified original path for SKUs without optimised derivatives */
      mainImg.src = resolveProductAsset(b.img);
      mainImg.alt = alt;
      mainImg.onerror = function () { applyImageFallback(this); };
    }

    var thumbs = document.getElementById('pp-thumbs');
    if (!thumbs) return;

    /* Build resolved image list (used for both thumb <img> src and the
     * gallery-click swap target — unchanged from the original behaviour) */
    var rawImgs = (b.gallery && b.gallery.length) ? b.gallery : [b.img];
    var imgs = rawImgs.map(resolveProductAsset);

    if (imgs.length <= 1) {
      thumbs.style.display = 'none';
      return;
    }

    thumbs.innerHTML = imgs.map(function (src, i) {
      var safeSrc = String(src).replace(/"/g, '&quot;');
      var base = optimizedBaseFor(b.id, i);
      /* Thumbnails: WebP if an optimised derivative exists, else original.
       * No AVIF here — thumbnails are tiny (160px) and WebP support is
       * already near-universal, so a third format isn't worth the markup. */
      var thumbSrc = base ? '../image/opt/' + base + '-160.webp' : safeSrc;
      return '<div class="pp-thumb' + (i === 0 ? ' active' : '') + '"'
           + ' role="button" tabindex="0" aria-label="View photo ' + (i + 1) + '">'
           + '<img src="' + thumbSrc + '" alt="' + b.name + ' view ' + (i + 1) + '"'
           + ' width="160" height="160" loading="lazy" decoding="async"'
           + ' data-fallback-applied="false"'
           + ' onerror="window.__ppApplyImageFallback && window.__ppApplyImageFallback(this)">'
           + '</div>';
    }).join('');

    thumbs.querySelectorAll('.pp-thumb').forEach(function (th, i) {
      function activate() {
        var img = document.getElementById('pp-main-img');
        var base = optimizedBaseFor(b.id, i);
        if (base && img.tagName === 'IMG' && img.closest('picture')) {
          /* Swap sources inside the existing <picture> for full-size AVIF/WebP,
           * mirroring the same width choices as the initial load. */
          var picture = img.closest('picture');
          var avifSrc = picture.querySelector('source[type="image/avif"]');
          var webpSrc = picture.querySelector('source[type="image/webp"]');
          if (avifSrc) avifSrc.srcset = '../image/opt/' + base + '-640.avif 640w, ../image/opt/' + base + '-1152.avif 1152w';
          if (webpSrc) webpSrc.srcset = '../image/opt/' + base + '-640.webp 640w, ../image/opt/' + base + '-1152.webp 1152w';
          img.src = '../image/opt/' + base + '-640.jpg';
          img.loading = 'lazy';
          img.removeAttribute('fetchpriority'); /* only the first-loaded image is high priority */
        } else {
          img.src = imgs[i];
        }
        thumbs.querySelectorAll('.pp-thumb').forEach(function (t) { t.classList.remove('active'); });
        th.classList.add('active');
      }
      th.addEventListener('click', activate);
      th.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); activate(); }
      });
    });
  }

  /* ── WhatsApp message (product-page always uses buildWaMsg) ─────────── */
  function buildWaMsg(b) {
    return 'Namaste Jyogi, I am interested in the ' + b.name + ' bracelet'
      + ' (SKU: ' + b.id + ', price: ' + b.price + ').'
      + '\n\nPlease share:'
      + '\n• Ordering details and payment steps'
      + '\n• After payment verification, Jyogi will collect my name, Gotra if known, and Sankalp intention before preparation. I may provide my name and intention if I do not know my Gotra.'
      + '\n• Delivery timeline'
      + '\n\nMy delivery PIN code: [PIN]'
      + '\nName and Gotra for Sankalp (if known): [Name / Gotra]';
  }

  function openWa(b) {
    /* Always use the richer product-page message, not b.msg */
    var msg = buildWaMsg(b);
    if (typeof gtag === 'function') {
      gtag('event', 'whatsapp_crystal_enquiry', { service_id: b.id });
    }
    window.open(
      'https://wa.me/' + WA_CRYSTAL + '?text=' + encodeURIComponent(msg),
      '_blank', 'noopener,noreferrer'
    );
  }

  /* ── Payment handler ─────────────────────────────────────────────────── */
  function openPayment(sku, button) {
    var pages = (typeof CRYSTAL_PAYMENT_PAGES !== 'undefined') ? CRYSTAL_PAYMENT_PAGES : {};
    if (!Object.prototype.hasOwnProperty.call(pages, sku)) return;
    var url = pages[sku];
    if (!url || typeof isRazorpayUrl !== 'function' || !isRazorpayUrl(url)) return;
    button.disabled = true;
    setTimeout(function () { button.disabled = false; }, 1500);
    if (typeof gtag === 'function') {
      gtag('event', 'razorpay_button_clicked', { service_id: sku });
    }
    window.open(url, '_blank', 'noopener,noreferrer');
  }

  /* ── "Is This For You?" — V2.5 decision-support section ─────────────────
   * Bullets are derived MECHANICALLY from the canonical vedicUse string,
   * never hand-authored per product. All 15 active vedicUse strings follow
   * the pattern "For X, Y, Z, or W." (verified against crystals_data.js) —
   * this parser strips the leading "For "/"Universal remedy when " framing,
   * the trailing period, and splits on commas, cleaning a leading "or " on
   * the final clause. If parsing yields no usable bullets the section is
   * hidden outright rather than showing something invented. ─────────────── */
  function parseVedicUseToBullets(vedicUse) {
    if (!vedicUse) return [];
    var text = String(vedicUse).split(/\.\s/)[0]; /* first sentence only */
    text = text.replace(/^For\s+/i, '').replace(/^Universal remedy when\s+/i, '');
    text = text.replace(/\.$/, '');
    var parts = text.split(/,\s*/).map(function (s) {
      return s.replace(/^or\s+/i, '').trim();
    }).filter(Boolean);
    /* Capitalise first letter of each bullet */
    return parts.map(function (s) {
      return s.charAt(0).toUpperCase() + s.slice(1);
    });
  }

  function renderIsThisForMe(b) {
    var section = document.getElementById('pp-isforme-section');
    var list = document.getElementById('pp-isforme-list');
    if (!section || !list) return;
    var bullets = parseVedicUseToBullets(b.vedicUse);
    if (!bullets.length) { section.style.display = 'none'; return; }
    list.innerHTML = bullets.map(function (t) {
      return '<li>' + t + '</li>';
    }).join('');
    var askLink = document.getElementById('pp-isforme-ask');
    if (askLink) {
      var msg = 'Namaste Jyogi, I would like to know whether the ' + b.name
        + ' bracelet suits my chart. My delivery PIN code: [PIN]';
      askLink.href = 'https://wa.me/' + WA_CRYSTAL + '?text=' + encodeURIComponent(msg);
    }
    section.style.display = '';
  }

  /* ── Related products — canonical relationship only, never image-driven ──
   * Selection rule: same `category` AND at least one shared planet token
   * (case-insensitive, split on "/"), excluding the current SKU. This
   * mirrors the reasoning used for the Shani prototype (Protection Shield /
   * Burnout Recovery / Tech Defender all share category:'protection' and a
   * Saturn planet token) rather than picking whichever products happen to
   * have photography.
   *
   * PRODUCTS_WITH_PHOTOS is a presentation-only allowlist (NOT part of
   * crystals_data.js) recording which SKUs currently have real photography
   * on disk, per the V2.5 image audit. A card is only rendered for a SKU
   * in this list; if a category+planet match lacks a photo, it is skipped
   * rather than shown as a placeholder card, per Part 19 (hide, don't
   * fake). Update this array as new product photography is added. ────────── */
  var PRODUCTS_WITH_PHOTOS = [
    'shani_bracelet', 'money_magnet', 'seven_chakra', 'rose_quartz_love',
    'pyrite_solo', 'moonstone_pearl', 'dhan_yog_rudraksha'
  ];

  function planetTokens(planetStr) {
    return String(planetStr || '').split('/').map(function (s) {
      return s.trim().toLowerCase();
    }).filter(Boolean);
  }

  function findRelatedProducts(b, max) {
    if (typeof BRACELETS === 'undefined') return [];
    var myPlanets = planetTokens(b.planet);
    var slugs = (typeof CRYSTAL_SLUGS !== 'undefined') ? CRYSTAL_SLUGS : {};
    var candidates = BRACELETS.filter(function (o) {
      if (!o || o.id === b.id || o.active === false) return false;
      if (PRODUCTS_WITH_PHOTOS.indexOf(o.id) === -1) return false;
      /* Must also have a standalone page to link to — e.g. dhan_yog_rudraksha
       * has photography but no product page yet (pre-existing, tracked
       * separately), so it must not be offered as a related-product link. */
      if (!slugs[o.id]) return false;
      var sameCategory = o.category === b.category;
      var sharedPlanet = planetTokens(o.planet).some(function (p) { return myPlanets.indexOf(p) !== -1; });
      return sameCategory && sharedPlanet;
    });
    return candidates.slice(0, max || 3);
  }

  function renderRelatedProducts(b) {
    var section = document.getElementById('pp-related-section');
    var grid = document.getElementById('pp-related-grid');
    if (!section || !grid) return;
    var related = findRelatedProducts(b, 3);
    if (!related.length) { section.style.display = 'none'; return; }

    var slugs = (typeof CRYSTAL_SLUGS !== 'undefined') ? CRYSTAL_SLUGS : {};
    grid.innerHTML = related.map(function (o) {
      var href = slugs[o.id] ? '../' + slugs[o.id] : '#';
      var disc = discountPct(o.price, o.original);
      var priceHtml = '<span class="pp-related-price">' + o.price
        + (disc ? '<s>' + o.original + '</s>' : '') + '</span>';
      var base = optimizedBaseFor(o.id, 0);
      var imgSrc = base ? '../image/opt/' + base + '-640.webp' : resolveProductAsset(o.img);
      return '<a class="pp-related-card" href="' + href + '" aria-label="View ' + o.name + '">'
        + '<div class="pp-related-img"><img src="' + imgSrc + '" alt="' + o.name + '"'
        + ' width="400" height="400" loading="lazy" decoding="async"'
        + ' onerror="window.__ppApplyImageFallback && window.__ppApplyImageFallback(this)"></div>'
        + '<div class="pp-related-body"><div class="pp-related-name">' + o.name + '</div>' + priceHtml + '</div>'
        + '</a>';
    }).join('');
    section.style.display = '';
  }

  /* ── Populate page ───────────────────────────────────────────────────── */
  function populatePage(b) {
    var pages = (typeof CRYSTAL_PAYMENT_PAGES !== 'undefined') ? CRYSTAL_PAYMENT_PAGES : {};
    var payUrl = Object.prototype.hasOwnProperty.call(pages, b.id) ? pages[b.id] : '';
    var hasPayUrl = !!(payUrl && typeof isRazorpayUrl === 'function' && isRazorpayUrl(payUrl));
    var disc = discountPct(b.price, b.original);

    /* Badge */
    var badgeEl = document.getElementById('pp-badge');
    if (badgeEl) { badgeEl.textContent = b.badge || ''; badgeEl.style.background = b.badgeColor || '#555'; }

    /* Name + stone composition + intention */
    setText('pp-name', b.name);
    setText('pp-stones', (b.sub || '') + ' Bracelet');
    setText('pp-product-stones', b.sub || '');
    setText('pp-intention', b.tagline);
    setText('pp-breadcrumb-current', b.name);

    /* Price */
    setText('pp-price', b.price);
    // Original (strikethrough) price shown ONLY when it is a genuine discount
    // (original > price) — reuses the same check as the % badge below, so an
    // identical original/price pair (e.g. tourmaline_cluster ₹1,699/₹1,699)
    // never renders misleading "sale" styling.
    if (b.original && disc) { setText('pp-original', b.original); show('pp-original'); } else { hide('pp-original'); }
    var discEl = document.getElementById('pp-discount');
    if (discEl) { discEl.textContent = disc; discEl.style.display = disc ? '' : 'none'; }

    /* Meta chips */
    setText('pp-planet', b.planet);
    var dotEl = document.getElementById('pp-chakra-dot');
    if (dotEl) dotEl.style.background = b.chakraColor || '#888';
    var chakraLabel = /chakra/i.test(b.chakra) ? b.chakra : b.chakra + ' Chakra';
    setText('pp-chakra', chakraLabel);

    /* Benefits */
    var benEl = document.getElementById('pp-benefits');
    if (benEl && b.benefits) {
      benEl.innerHTML = b.benefits.map(function (x) {
        return '<span class="pp-benefit-tag">' + x + '</span>';
      }).join('');
    }

    /* Vedic prescription */
    if (b.vedicUse) { setText('pp-vedic', b.vedicUse); show('pp-vedic-section'); } else { hide('pp-vedic-section'); }

    /* Wearing ritual */
    setText('pp-ritual', b.ritual);

    /* Gallery */
    initGallery(b);

    /* Stock */
    var stockEl = document.getElementById('pp-stock');
    if (stockEl) {
      /* All active bracelets are in_stock; made_to_order shows fulfilment note */
      if (b.stock !== 'made_to_order') {
        stockEl.innerHTML = '<span class="pp-stock-dot"></span> In Stock — Available to order';
        stockEl.style.color = '#2E6B4E';
      } else {
        stockEl.innerHTML = '<span class="pp-stock-dot" style="background:#b07d2a"></span>'
          + ' Handcrafted to Order — Prepared after payment verification';
        stockEl.style.color = '#b07d2a';
      }
    }

    /* Buy Now / WhatsApp visibility and wording.
     * hasPayUrl true  -> Primary: "Buy Now — {price}" (+ sticky Buy Now + Razorpay
     *                    note). Secondary WA button reads "Ask a Question" -- it is
     *                    support, not the ordering path, so it must not look primary.
     * hasPayUrl false -> Buy Now, sticky Buy Now and Razorpay note all hidden. WA is
     *                    the sole action and is honestly labelled "Order on WhatsApp"
     *                    (not "Ask a Question") since it IS how the order is placed.
     * No "setup in progress" message is ever shown -- the shop must not look unfinished. */
    var buyBtn        = document.getElementById('pp-btn-buy');
    var stickyBuy      = document.getElementById('pp-sticky-buy');
    var razorpayNoteEl = document.getElementById('pp-razorpay-note');
    var waBtn          = document.getElementById('pp-btn-wa');
    var stickyWaBtn     = document.getElementById('pp-sticky-wa');
    var payLabelEl      = document.getElementById('pp-trust-pay-label');

    if (hasPayUrl) {
      if (buyBtn) {
        buyBtn.style.display = '';
        buyBtn.disabled = false;
        buyBtn.addEventListener('click', function () { openPayment(b.id, buyBtn); });
        setText('pp-btn-buy-label', 'Buy Now — ' + b.price);
      }
      if (stickyBuy) {
        stickyBuy.style.display = '';
        stickyBuy.disabled = false;
        stickyBuy.textContent = 'Buy Now — ' + b.price;
        stickyBuy.addEventListener('click', function () { openPayment(b.id, stickyBuy); });
      }
      if (razorpayNoteEl) razorpayNoteEl.style.display = '';
      if (waBtn) waBtn.classList.remove('pp-btn-wa-primary');
      if (stickyWaBtn) stickyWaBtn.classList.remove('pp-sticky-btn-wa-full');
      setText('pp-btn-wa-label', 'Ask a Question');
      if (payLabelEl) payLabelEl.textContent = 'Secure Pay';
    } else {
      if (buyBtn) buyBtn.style.display = 'none';
      if (stickyBuy) stickyBuy.style.display = 'none';
      if (razorpayNoteEl) razorpayNoteEl.style.display = 'none';
      if (waBtn) waBtn.classList.add('pp-btn-wa-primary');
      if (stickyWaBtn) stickyWaBtn.classList.add('pp-sticky-btn-wa-full');
      setText('pp-btn-wa-label', 'Order on WhatsApp');
      if (payLabelEl) payLabelEl.textContent = 'WhatsApp Ordering';
    }

    /* WhatsApp CTAs -- always use buildWaMsg(b), which includes the product
     * name and the currently displayed price, for both inline and sticky. */
    ['pp-btn-wa', 'pp-sticky-wa'].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.addEventListener('click', function () { openWa(b); });
    });

    /* Prevent duplicate WhatsApp CTAs on screen at once: the sticky bar
     * starts hidden (see CSS) and is only revealed once the inline primary
     * CTA (Buy Now if available, otherwise the WA button) scrolls out of
     * the viewport. Scrolling back up hides it again. */
    var stickyBarEl = document.querySelector('.pp-sticky-bar');
    var primaryInlineEl = (hasPayUrl && buyBtn) ? buyBtn : waBtn;
    if (stickyBarEl && primaryInlineEl && 'IntersectionObserver' in window) {
      var stickyObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            stickyBarEl.classList.remove('pp-sticky-visible');
          } else {
            stickyBarEl.classList.add('pp-sticky-visible');
          }
        });
      }, { threshold: 0 });
      stickyObserver.observe(primaryInlineEl);
    } else if (stickyBarEl) {
      /* No IntersectionObserver support: fail safe to always-visible sticky
         bar rather than never showing it. */
      stickyBarEl.classList.add('pp-sticky-visible');
    }

    /* Sticky bar */
    setText('pp-sticky-name', b.name);
    setText('pp-sticky-price', b.price);

    /* Title fallback */
    if (document.title.indexOf('Loading') !== -1) {
      document.title = b.name + ' Bracelet — Jyogi';
    }

    /* V2.5 additions */
    renderIsThisForMe(b);
    renderRelatedProducts(b);
  }

  /* Expose for inline onerror="" handlers (thumbnails use this) */
  window.__ppApplyImageFallback = applyImageFallback;

  /* ── Entry ───────────────────────────────────────────────────────────── */
  function init() {
    var sku = document.body.getAttribute('data-product-sku');
    if (!sku) { console.error('[product-page.js] Missing data-product-sku on <body>.'); return; }
    var b = findBracelet(sku);
    if (!b) {
      var c = document.getElementById('pp-container');
      if (c) c.innerHTML = '<p style="padding:40px;text-align:center;color:#777;">'
        + 'Product not found. <a href="../crystals.html">Back to collection</a>.</p>';
      return;
    }
    populatePage(b);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
