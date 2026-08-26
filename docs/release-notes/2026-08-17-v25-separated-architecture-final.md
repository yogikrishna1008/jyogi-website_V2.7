# V2.5 Production Candidate — Final Manifest (Separated Architecture)

**Status:** Candidate for review. NOT deployed.
**Baseline:** `jyogi-website-master` (authoritative candidate ZIP)
**Architecture change this round:** `index.html` rebuilt from scratch as a genuinely new marketing homepage (not a CSS retint of the legacy SPA). `tools.html` created as the preserved, working legacy application (Tarot/Astrology/Compatibility/Dreams/Muhurta), with the fake reviews section removed from public rendering.

---

## Files Changed

```
 crystals/burnout-recovery-bracelet.html   |  21 +-
 crystals/divine-feminine-bracelet.html    |  21 +-
 crystals/executive-presence-bracelet.html |  21 +-
 crystals/focus-scholar-bracelet.html      |  21 +-
 crystals/love-marriage-bracelet.html      |  21 +-
 crystals/lucky-charm-bracelet.html        |  21 +-
 crystals/money-magnet-bracelet.html       |  21 +-
 crystals/product-page.css                 | 268 +-
 crystals/product-page.js                  | 211 +-
 crystals/protection-shield-bracelet.html  |  21 +-
 crystals/pyrite-power-bracelet.html       |  21 +-
 crystals/seven-chakra-bracelet.html       |  21 +-
 crystals/shani-bracelet.html              |  21 +-
 crystals/tech-defender-bracelet.html      |  21 +-
 crystals/third-eye-awakener-bracelet.html |  21 +-
 crystals/tiger-eye-courage-bracelet.html  |  21 +-
 crystals_data.js                          |   1 -
 index.html                                | rebuilt (new file, ~28KB, was 563KB legacy SPA)
 tools.html                                | new file (legacy SPA content relocated here, minus fake reviews section)
```

**Added:** `fonts/` (10 self-hosted woff2 + `v25-fonts.css`), `image/opt/` (144 AVIF/WebP/JPEG derivatives + manifest).

**Removed from public rendering:** the fake reviews section (`#reviews`, fabricated names/ratings/claims) — deleted from `tools.html`, was never carried into the new `index.html`.

**Untouched, byte-verified identical to baseline:** `api.py`, `vedic_engine.py`, `ashtakoot_engine.py`, `crystals.html`, `crystal-payment-config.js`, `privacy.html`, `refund-policy.html`, `numerology.html`, all blog articles, admin, all other engines.

---

## A Real Bug Found and Fixed Before Packaging

While preparing the final diffstat, I discovered `crystals/product-page.js` had **not actually received my V2.5 changes** — an earlier `cp` command in this session had a shell argument bug (`cp source.css crystals/product-page.js crystals/` — the middle argument was interpreted as a second source path relative to the current directory, which resolved to itself, producing a silent no-op instead of copying the intended file). The result would have shipped with:
- No AVIF/WebP `<picture>` support (falling back to plain JPEG)
- No "Is This For You?" section
- No Related Products section

**Caught by diffing, not assumed.** I noticed `product-page.js` showed zero diff against baseline in a `git diff --stat` where I expected ~211 changed lines, investigated, found the bug, copied the correct file, and **re-ran the entire 60-check crystal regression suite plus targeted feature verification** against the corrected file before packaging. Confirmed working post-fix: AVIF picture loading, Is-This-For-You bullets, Related Products gating, and the no-fake-discount rule on Tech Defender all verified live in-browser, not just diffed.

---

## Item-by-Item Verification

### 1. Every homepage link resolves — verified, 2 categories of broken links found and fixed

Initial audit found real problems:

| Link | Issue | Fix |
|---|---|---|
| `#reports` (nav, service card, footer — 4 occurrences) | No such anchor existed anywhere | Repointed to `tools.html#astrology` — verified this is where PDF report generation (`downloadReport('full')`/`downloadReport('saturn')`) actually lives, gated behind chart generation |
| `free-kundli-online.html` | File doesn't exist at repo root | Fixed to `blog/free-kundli-online.html` (articles live under `blog/`) |
| `mangal-dosha-manglik.html` | Same | Fixed to `blog/mangal-dosha-manglik.html` |
| `sade-sati.html` (2 occurrences) | Same | Fixed to `blog/sade-sati.html` |
| `/favicon32.png` | Actual file is `favicon-32.png` (hyphenated) | Fixed |
| `/appletouchicon.png` | Actual file is `apple-touch-icon.png` | Fixed |

After fixes: scripted audit of every `href`/`src` in `index.html` against the actual filesystem, plus a live browser network-response check (zero 4xx on any requested asset). All 44 real link targets resolve. One flagged item in my automated script (`image/opt/'+base+'-640.jpg`) was confirmed to be a false positive — that's JS string-concatenation source code inside a `<script>` tag, not an actual href.

### 2. Practitioner photograph

`images/jyogi-photo.jpg` already exists in the authoritative baseline — a genuine 768×1024 JPEG, 154KB, not a placeholder or corrupt file. The new `index.html` already correctly references this real path (with a graceful 🧘 emoji fallback only if the image ever fails to load). No placeholder was used; no image was generated or invented.

### 3. Featured crystal cards — verified at all 3 required widths

Live DOM check at 1440/912/430px, all 5 cards, every field:

| Product | Tag | Price | Original | Image loaded |
|---|---|---|---|---|
| Shani Protection & Career | Saturn Support | ₹1,099 | ₹1,799 | ✓ (AVIF) |
| Money Magnet | Wealth | ₹1,199 | ₹1,499 | ✓ (AVIF) |
| Seven Chakra | Featured | ₹799 | ₹999 | ✓ (AVIF) |
| Love & Marriage | Relationships | ₹999 | ₹1,499 | ✓ (AVIF) |
| Pyrite Power | Wealth | ₹799 | ₹1,199 | ✓ (AVIF) |

Identical at all three widths. One image initially reported `naturalWidth: 0` at 430px in a quick check — re-verified with a full scroll-settle pass and confirmed genuinely loaded (640px); this was a lazy-load timing artifact in my test methodology, not a real defect (consistent with similar false alarms caught earlier in this project).

### 4. Fake reviews — confirmed absent from both pages

`document.getElementById('reviews')` returns `null` on both `index.html` and `tools.html`. Scripted search for known fabricated names (Priya, Rajesh, Anjali, Deepak) — zero matches on either page. One "★★★★★" pattern match on `tools.html` was investigated and confirmed to be the Muhurta tool's auspicious-day-quality rating label ("★★★★★ Excellent" for timing windows) — a real, functional part of the astrology tool, not a customer testimonial.

### 5. `tools.html` anchors — all five present and populated

`#tarot`, `#astrology`, `#compat`, `#dreams`, `#muhurta` all exist with substantial content (>50 characters, not empty containers). Functional test: actually clicked "Draw Your Cards" in the Tarot tool and received a live, real result (Nine of Wands, upright, with interpretation text) — proving the application runs, not just that markup is present.

### 6. Homepage overflow/console/broken-asset — all 10 widths, all three checks together

| Width | Overflow | Console errors | Broken assets |
|---|---|---|---|
| 1440 / 1280 / 1100 / 1024 / 912 / 896 / 768 / 430 / 390 / 375 | ok | ok | ok |

**PASS — zero failures across 30 checks** (10 widths × 3 check types).

### 7. Crystal regression suite — re-run after the product-page.js fix

60 checks (6 representative products × 10 widths): zero column overlaps, zero horizontal overflow. Re-verified after discovering and fixing the `product-page.js` bug above — this result reflects the corrected file, not the broken one.

### 8. Shani Razorpay verification — still a deployment blocker

**Unchanged from prior rounds.** `isRazorpayUrl('https://rzp.io/rzp/l5bS564Y')` passes structural validation, so Buy Now renders live for Shani. No network path to rzp.io exists in this environment to confirm the checkout amount is genuinely ₹1,099. **This remains a hard deployment blocker until manually confirmed by you.**

---

## `git diff --check`

Run properly against a real baseline commit (not the file-rename-blind first attempt from an earlier round). `index.html` and `crystals/product-page.js`: **clean, exit 0**. `tools.html` flags pre-existing baseline whitespace as "new" because git has no prior file under that exact name to diff against — directly proven by a raw `diff` against the true source (`index.html` baseline), which shows my actual edit is exactly 35 lines (the reviews-section removal), and my own two added lines contain zero trailing whitespace.

---

## Unresolved Issues (carried forward, unchanged)

1. **Razorpay Shani URL unverified** — hard blocker, see §8.
2. **Pre-existing PII leak in `#compat`** (inside `tools.html`, untouched per scope) — user-entered Kundali-match names can reach GA4/logs via `openWhatsApp()`. Not fixed this batch.
3. **8 of 15 crystal products still lack photography** — existing placeholder fallback handles this correctly.
4. **`dhan_yog_rudraksha` has no standalone page** — pre-existing.
5. **Devotional gallery** (`#gallery`) — preserved in `tools.html` as instructed, future placement not decided.
6. **Full i18n wiring for the new homepage** — language pill is present and visually secondary as instructed, but does not yet re-translate the new homepage copy into Hindi/Odia. Flagged as follow-up, not attempted this batch per your explicit instruction not to let Hindi/Odia dictate the English architecture.

## Not Done (Explicitly Out of Scope)

Blog redesign, Consultation page redesign, admin, backend, calculation-engine changes, `#tarot`/`#astrology`/`#compat`/`#dreams`/`#muhurta`/`#gallery` internal re-skinning, the deferred Razorpay privacy fragment, full i18n translation of the new homepage.
