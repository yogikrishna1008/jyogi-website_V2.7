# 2026-08-17 — V2.5 Candidate: Three Pre-Packaging Corrections

**Status:** Candidate for review. NOT deployed.

---

## 1. Local preview documentation

`jyogi-website-master/` (the repository root) MUST be served as the HTTP
document root for local testing — e.g.:

```
cd jyogi-website-master
python3 -m http.server 8080
```

then browse `http://localhost:8080/`.

**Do NOT:**
- Open files via `file://` — root-relative URLs (`/tools.html#astrology`,
  `/#consult`, etc.) resolve against the filesystem root under `file://`,
  not the project root, and will not work.
- Serve from a parent directory or any path that puts `/repo/` or any
  other prefix in front of the project root — this would turn
  `/tools.html` into a request for a file that doesn't exist at that
  path, breaking every root-relative link.
- Serve from inside a subdirectory of the project — the document root
  must be exactly the folder containing `index.html`, `tools.html`,
  `crystals.html`, `crystals/`, `blog/`, etc. at its top level.

Root-relative URLs are production-correct as shipped and must NOT be
reverted to document-relative paths.

---

## 2. Compatibility PII leak — fixed, deployment blocker cleared

**Two separate leak points were found and fixed** (not one — see below).

### Leak A — inside `calcCompatibility()` directly
```js
// BEFORE
saveLog({type:'compatibility',c1:c1n,ms1:RASHIS[ms1],c2:c2n,ms2:RASHIS[ms2],score:total,pct:pct,city:c1city||c2city||''});
// AFTER
saveLog({type:'compatibility',ms1:RASHIS[ms1],ms2:RASHIS[ms2],score:total,pct:pct});
```
This call fires the moment a match is calculated, **before** the user ever
touches the WhatsApp button — both names and city were being logged
unconditionally. Names and city are now dropped entirely; moon signs and
score (non-identifying) are kept.

### Leak B — inside the shared `openWhatsApp()` function
The `#compat` "Enquire on WhatsApp" button built a message containing
both names, and the shared `openWhatsApp(msg)` function reused that exact
string for both the WhatsApp deep link **and** the GA4/log event.

Fixed by adding an **optional** second parameter:
```js
function openWhatsApp(msg, analyticsText){
  var logText = (typeof analyticsText === 'string') ? analyticsText : msg;
  saveLog({ type:'whatsapp_booking', message: logText.slice(0,120) });
  if(typeof gtag==='function'){ gtag('event','whatsapp_booking',{ message_preview: logText.slice(0,80) }); }
  window.location.href = `https://wa.me/${WA_NUMBER}?text=${encodeURIComponent(msg)}`;
}
```
When `analyticsText` is omitted, behaviour is **exactly unchanged** for
every other existing caller (dream journal, Muhurta, numerology, crystal
enquiries, etc.) — none of those were touched. Only the `#compat` call
site now supplies a scrubbed label:
```js
openWhatsApp(
  'Hi Jyogi, Kundali match for '+c1n+' & '+c2n+', score '+total+'/36',   // → WhatsApp deep link (names OK, this is Jyogi's own message)
  'Kundali compatibility match enquiry (score '+total+'/36)'             // → analytics/log (no names)
)
```

### Empirical verification (not just code review)
Tested live in-browser with realistic sensitive data ("Priyanka Sharma",
DOB 14/3/1994; "Rohit Verma", DOB 22/8/1991):

- `gtag()` and `saveLog()` were monkey-patched to capture every call
- `calcCompatibility()` triggered directly → **`saveLog` payload:**
  `{type:'compatibility', ms1:'Pisces', ms2:'Capricorn', score:21, pct:58}`
  — zero names, zero DOB, zero city
- The Enquire button's `onclick` invoked
  `openWhatsApp(msg, analyticsText)` with `msg` correctly containing
  `"...Priyanka Sharma & Rohit Verma..."` (preserved for the real
  WhatsApp message to Jyogi) and `analyticsText` correctly containing
  only `"Kundali compatibility match enquiry (score 21/36)"`
- Automated string search for "Priyanka", "Sharma", "Rohit", "Verma",
  "1994", "1991" across every captured `gtag`/`saveLog` payload:
  **zero matches**

### Functional regression
- Match calculation still renders the full result (score, Kutas,
  Manglik analysis) — unchanged
- WhatsApp deep link still delivers the personalised message with both
  names to Jyogi — unchanged, this is the intended user-to-practitioner
  flow and is explicitly preserved
- Every other `openWhatsApp()` caller elsewhere in `tools.html`
  (dreams, Muhurta, numerology, birth-chart yogas, remedy protocol,
  crystal shop) unaffected — verified via code diff showing zero
  changes to those call sites

**Compatibility was not redesigned** — both fixes are surgical edits to
two `saveLog`/`gtag` call sites; no UI, layout, or calculation logic was
touched.

---

## 3. Homepage language control

**Decision: Option B — hidden, not faked.**

Building accurate Hindi and Odia translations for the entire new V2.5
homepage (hero, trust strip, Choose Your Path, Core Services, Free Tools,
Featured Crystals, How It Works, Consultation CTA, Authority, Blog
teasers, About, Footer — roughly 30 distinct text blocks) is a real
content-authoring task, not a mechanical one, and would materially
expand this batch beyond a header/navigation/privacy correction pass.

The language pill (EN / हिं / ଓଡ଼ି) has been **removed from both the
desktop header and the mobile drawer** on `index.html`. It is not
disabled, greyed out, or partially wired — it is not present, so the
homepage never implies a translation capability it doesn't have.

**What's preserved:**
- The underlying `setSiteLang(lang)` function is untouched and still
  defined in `index.html` — dormant, not deleted, ready to be
  reconnected once translated copy exists
- `tools.html` and `blog/` keep their full, working, existing
  Hindi/Odia i18n — completely unaffected by this change
- The theme/appearance control (unrelated to this correction) is fully
  intact on both desktop and mobile

**Tracked as the immediate next task:** full i18n for the new V2.5
homepage copy, followed by re-enabling the language pill once real
translations are wired to the existing `data-i18n` mechanism.

---

## Re-verification after all three corrections

| Check | Result |
|---|---|
| Homepage 10-width overflow + console (12 widths incl. 1220/1150 collapse points) | PASS |
| `#compat` PII empirical test (real sensitive data, captured payloads) | PASS — zero leak |
| `#compat` functional regression (match renders, WhatsApp message correct) | PASS |
| Link/asset HTTP check, repo mounted at `/` (6 representative pages) | See below |
| `git diff --check` (`index.html`, `tools.html`) | PASS — exit 0 both |

**Link/asset check results:**
- `index.html`, `blog/index.html`, `blog/free-kundli-online.html`,
  `crystals/shani-bracelet.html`: **0 broken requests**
- `crystals.html`: **8 pre-existing 404s** — the 8 already-documented
  products with no photography yet (`green_aventurine`,
  `black_tourmaline`, `lepidolite_amethyst`, `tourmaline_cluster`,
  `tiger_eye`, `fluorite_clear`, `lapis_amethyst`, `sunstone_bronzite`).
  Not introduced by this batch, not in scope for these three
  corrections, handled gracefully by the site's existing image-fallback
  mechanism. Tracked separately.
- `tools.html`: **1 blocked request** — `translate.google.com`,
  blocked only by this development sandbox's network allowlist; not a
  real defect, will resolve normally in production.

---

## Remaining external deployment blocker (unchanged)

**Shani Razorpay URL** (`https://rzp.io/rzp/l5bS564Y`) still requires
manual confirmation that it opens the correct product at ₹1,099. This
environment has no network path to verify it. Not touched, not assumed.

---

## Addendum — a packaging bug caught before the first delivery of this round

The first attempt to package this round's corrections shipped a **broken
half-fix**: the `openWhatsApp()` function-signature change (Leak B) never
actually reached disk, even though it had been verified working in an
earlier live test.

**Root cause:** the original edit ran as a single Python script that
performed the function-signature replacement in memory, then attempted a
second replacement (the `#compat` call site) inside the same script. The
second replacement's assertion failed, raising an exception *before* the
script's `.write()` call ever executed — so the function fix was silently
discarded, while a separate, successful `str_replace` call had already
written the call-site half directly to disk. The result was an
inconsistent file: the call site passed a new `analyticsText` argument
that the function itself didn't yet declare or use, so it was silently
ignored by JavaScript and the original leaking behaviour
(`msg.slice(0,80)`, containing full names) remained active.

**How it was caught:** not by re-running the same style of test again,
but by directly inspecting the actual `openWhatsApp` function body in the
packaged file with `grep`/`sed` — the earlier "passing" dynamic tests
turned out to have been unknowingly exercising a monkey-patched stub
function rather than the real code path, a limitation of testing via
full-page-navigation interception. Static, on-disk inspection caught what
dynamic testing had missed.

**Fix applied:** the function-signature change was reapplied directly via
a single `str_replace` edit (which writes immediately, with no
multi-step script that could partially fail), then re-verified with a
test designed to avoid the async-navigation pitfall: `gtag`/`saveLog`
were monkey-patched, the real `openWhatsApp()` was invoked directly with
the exact two arguments the button's `onclick` uses, and the results were
read synchronously within the same `evaluate()` call — before any
navigation could destroy the page context.

**Final confirmed result**, real function, real click, single combined
run:
```
saveLog calls: [
  {type:'compatibility', ms1:'Pisces', ms2:'Capricorn', score:21, pct:58},
  {type:'whatsapp_booking', message:'Kundali compatibility match enquiry (score 21/36)'}
]
gtag calls: [['event','whatsapp_booking',{message_preview:'Kundali compatibility match enquiry (score 21/36)'}]]
button onclick: openWhatsApp('Hi Jyogi, Kundali match for Priyanka Sharma & Rohit Verma, score 21/36', 'Kundali compatibility match enquiry (score 21/36)')
```
Zero PII in either logged payload; the WhatsApp message the user actually
sends still correctly contains both names.

**Any ZIP delivered before this addendum should be treated as
superseded.** The ZIPs accompanying this final version contain the
verified, corrected file.
