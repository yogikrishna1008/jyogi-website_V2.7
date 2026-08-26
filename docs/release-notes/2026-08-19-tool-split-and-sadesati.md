# 2026-08-19 — Tool Split, Sade Sati Calculator, Phase 3 Routing

**Status:** Candidate for review. NOT deployed. Supersedes everything before
this in `docs/release-notes/` — this is the first package since 2026-08-17
to include the work below.

---

## Summary of what's new since the last package (2026-08-17)

1. **Tool-split architecture** — 5 tools extracted from the `tools.html`
   monolith into standalone pages: `dreams.html`, `kundli.html`,
   `tarot.html`, `muhurta.html`, `compatibility.html`. Shared
   infrastructure lives in `assets/shared.css`, `assets/shared.js`,
   `assets/ephemeris.js`, `assets/tarot-data.js`.
2. **Sade Sati & Shani Dhaiya calculator** — new standalone tool,
   `sade-sati-calculator.html`. Uses real ephemeris calculation (not a
   lookup table), verified against the blog article's own worked
   examples for all 3 Sade Sati phases and all 4 Dhaiya houses.
3. **Dhaiya rule correction** — both the calculator and
   `blog/sade-sati.html` now consistently use the 4-house model
   (4th/7th/8th/10th from Moon: Ardha Ashtama, Saptamesh Shani,
   Ashtamesh Shani, Dashamesh Shani), replacing an earlier
   inconsistency where the article's FAQ schema said "4th or 8th only"
   while its own table said 4 houses. Confirmed with the site owner
   which version was correct before changing anything.
4. **Phase 3 routing** — 219 broken blog-article links fixed (they
   pointed to `../index.html#astrology` etc., anchors that stopped
   existing when `index.html` was rebuilt into the V2.5 marketing
   homepage). `tools.html` now has a **surgical** redirect for 6
   specific legacy anchors only (`#tarot`, `#astrology`, `#compat`,
   `#dreams`, `#muhurta` → their new standalone pages; `#shop` →
   `crystals.html`, which has the fuller listing). `#services` (the
   real paid-booking/Razorpay flow), `#gallery`, `#about`, and a bare
   `tools.html` load are deliberately NOT redirected — no replacement
   exists for `#services` anywhere else, and turning this into a
   blanket redirect (as first sketched) would have silently orphaned
   the live booking mechanism.
5. **Homepage Free Tools promotion** — stronger headline ("Real tools.
   Genuinely free."), an explicit trust row (No login/signup · Free,
   always, not a trial · Real Swiss Ephemeris calculations), a FREE
   badge on the Kundli & Birth Chart service card only (the other 3
   service cards are genuinely paid and were not badged), and all 8
   Free Tools chips now point to their real standalone pages instead
   of the old `tools.html#anchor` route.

## Real bugs found and fixed during this work (not just features added)

- **Picker overlay missing** on `kundli.html` and `compatibility.html`
  — the dropdown-arrow date/time picker button threw a JS error on
  click because the overlay markup was never extracted from the
  monolith. Fixed on both pages.
- **28 of 31 V2.5 design tokens undefined** on every tool page —
  `shared.css`'s header/nav/drawer/footer rules referenced spacing and
  color tokens (`--sp-2`, `--text-small`, `--header-h`, etc.) that only
  ever existed in `index.html`'s own stylesheet. Silently made nav
  padding collapse to 0 and font-size inherit the body's 22px serif
  size on all 5 tool pages. Fixed once at the source.
- **`.footer-grid` permanently collapsed to a single column** at every
  width — an earlier fragile regex-based CSS merge mis-scoped
  responsive column-count rules out of their `@media` wrappers.
  Rewritten with a proper brace-depth-aware parser; footer now
  correctly shows 5 columns on desktop.
- **`.service-card` styling accidentally deleted** while adding the
  FREE badge — an editing mistake caught immediately by checking
  computed styles rather than trusting the screenshot; fixed in the
  same session before it went anywhere.

## Verification before this package

- 130-check full regression (13 pages × 10 widths): PASS
- Compatibility PII fix re-verified end-to-end with realistic
  sensitive data: zero leak in `gtag`/`saveLog`, WhatsApp message to
  Jyogi still correctly contains both names
- Sade Sati calculator's 4-house Dhaiya model re-verified against all
  4 of the blog article's own worked examples
- `tools.html#tarot` redirect confirmed landing on `/tarot.html`
- `tools.html#services` confirmed NOT redirecting — booking flow
  (4 services, pay button, Razorpay validation function) confirmed
  still present and functional

## Files excluded from this package

- `index_woking Bkp_25july.html` — stray working backup, not part of
  the live site
- `crystals_data_patch.js`, `crystals_data_shani_patch.js` — stale
  patch-instruction files; both patches were already merged into
  `crystals_data.js` (confirmed: Shani bracelet entries present)

## What's still open — not part of this package

- **Manglik calculator** — deferred pending the owner's decision on
  rule set (Lagna-only vs. Lagna+Moon+Venus, with/without Bhanga
  cancellation)
- **Header dropdown submenus** — IA approved, build deliberately
  deferred to its own pass
- **Homepage Hindi/Odia translation** — language selector intentionally
  hidden on `index.html` until real translated copy exists for the new
  V2.5 sections
- **Visual consistency** — the 5 split tool pages and `tools.html`
  still use the pre-V2.5 dark-cosmic styling for their actual
  calculator UI (by design — this was a structural split, not a
  redesign); bringing them onto the ivory/navy/gold system is tracked
  backlog

## Remaining external deployment blocker (unchanged from every prior package)

**Shani Razorpay URL** (`https://rzp.io/rzp/l5bS564Y`) still requires
manual confirmation that it opens the correct product at ₹1,099. No
network path to verify this from the current environment.
