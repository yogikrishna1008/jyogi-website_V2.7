# Payments Phase 1 — Razorpay Payment Links

**Date:** 2026-07-25
**Workstream:** Payments — separate from Phase 2.5 R1 / R2
**Status:** Implemented in scratch environment against repository snapshot.
Awaiting: branch application, git diff --check, user and Genie review.
**Automatic payment verification:** NOT implemented. Verification is manual.

## Services wired

| Service              | id                | Amount | Payment Link URL                 |
|----------------------|-------------------|--------|----------------------------------|
| Full Vedic Reading   | `vedic_reading`   | ₹1,500 | https://rzp.io/rzp/sryivWVn     |
| Live Tarot Session   | `tarot_session`   |   ₹800 | https://rzp.io/rzp/MqgHmGC      |
| Crystal Prescription | `crystal_consult` |   ₹500 | https://rzp.io/rzp/ha8fPHO8     |

**Payment Link mode:** operator to confirm in Razorpay Dashboard (Test / Live).
The three links were provided by the operator from the Dashboard export
on 2026-07-25. Mode was not stated and cannot be determined from the URL.
Do not assume Test or Live until the operator confirms.

**Amount verification status:** cross-checked against the operator-supplied
Dashboard export (₹1,500 / ₹800 / ₹500 shown against the plink_ IDs).
Operator must independently confirm the configured amounts in the Razorpay
Dashboard before public launch — this implementation cannot access Razorpay
directly to verify.

## URL validation

`isRazorpayUrl()` accepts only `https:` on exactly `rzp.io` or
`pages.razorpay.com`. No `*.razorpay.com`, no general `razorpay.com`,
no substring matching. Validated against 10 test cases.

## Handler safeguards

- `event.target.closest('[data-razorpay-service]')` — delegated, no inline onclick
- `Object.prototype.hasOwnProperty.call(RAZORPAY_LINKS, serviceId)` — click-time
- `Object.prototype.hasOwnProperty.call(RAZORPAY_LINKS, s.id)` — render-time
- `isRazorpayUrl(RAZORPAY_LINKS[s.id])` — render-time host+HTTPS check
- `isRazorpayUrl(paymentUrl)` — click-time host+HTTPS check
- `button.disabled = true / setTimeout 1500ms` — duplicate-tab prevention
- `window.open(url, '_blank', 'noopener,noreferrer')` — opener isolation

## Files changed

- **`index.html`** — `RAZORPAY_LINKS` config; `isRazorpayUrl()`; delegated handler
  with render-time and click-time validation; `btn-pay` (gold-filled) and
  `btn-wa-enquiry` (green outline) CSS classes; Pay button and caption in
  `renderServices()` using string concatenation (no nested backticks); Full
  Vedic Reading copy updated for manual PDF delivery; 17 CTA relabels to
  "Enquire on WhatsApp" covering all sections including mobile drawer, reviews,
  About, explanatory text, and inline `var I18N` blob (9 strings); float pill
  visible label → "WhatsApp", `aria-label` → "Enquire on WhatsApp";
  "Save & Draw My Card"; crystal modal unchanged ("Order on WhatsApp").
- **`translations.json`** — 3 keys × 3 languages (en/hi/or), 9 strings total.
- **`privacy.html`** — date 25 July 2026 with scope qualifier; two payment rows
  with Genie-approved wording ("Processed and retained by Razorpay; Jyogi may
  access limited booking and transaction records through the Razorpay Dashboard");
  §3 reworded to accurately distinguish payment credentials from limited Dashboard
  records; new §4 Payments (Razorpay) with five approved statements; §4–§8
  renumbered §5–§9. R0 logging/retention claims untouched (remain for R2).
- **`CHANGELOG.md`** — entry to be merged into existing repo file (not overwritten).
- **`docs/release-notes/2026-07-25-payments-phase-1-razorpay.md`** (this file).
- Unchanged: `payment-success.html`, `refund-policy.html`,
  `docs/privacy-razorpay-fragment.md`.

## CTA convention

| Style class    | Label            | Action                        |
|----------------|------------------|-------------------------------|
| `btn-pay`      | Pay ₹{price}     | data-razorpay-service → rzp.io |
| `btn-wa-enquiry` / `btn btn-wa` | Enquire on WhatsApp | openWhatsApp() / wa.me |
| `btn btn-wa`   | Order on WhatsApp | wa.me (crystal modal, unchanged) |
| submit-btn     | Save & Draw My Card | in-page tool action          |

## Analytics

`razorpay_button_clicked` (service_id only), `payment_success_page_viewed`,
`whatsapp_after_payment_clicked`. No URL, amount, payment ID, name, email,
phone or birth data. Existing cookieless gtag reused.

## Production gate (all must be complete before public launch)

- [x] privacy.html Razorpay disclosure written
- [x] refund-policy.html written
- [x] URL hostnames validated (rzp.io, 2026-07-25)
- [ ] Payment Link mode confirmed (Test / Live) — operator to confirm
- [ ] Configured amounts verified in Razorpay Dashboard — operator to confirm
- [x] payment-success.html wording verified
- [ ] One controlled live transaction completed

## Git commands to run after branch application

```
git diff -- index.html translations.json privacy.html CHANGELOG.md \
  docs/release-notes/2026-07-25-payments-phase-1-razorpay.md
git diff --check
```

Both must pass with zero trailing-whitespace errors before commit.

## Rollback

Set the three `RAZORPAY_LINKS` values to `''` (instantly hides all Pay buttons)
or restore prior `index.html`. Disable Payment Links in Razorpay Dashboard.
Restore prior `privacy.html` and `translations.json`. No backend rollback required.
