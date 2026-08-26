# 2026-08-17 — V2.5 Header: Root-Relative Navigation Correction

## What changed
Every internal navigation link in `index.html` converted from document-relative
to root-relative URLs (leading `/`). This included not just the 8 primary header
items but all navigational hrefs site-wide in this file: hero CTAs, Choose Your
Path cards, Core Services cards, Free Tools chips, Featured Crystals "View
Details"/"Explore all" links, About "Explore free tools" link, footer Quick
Links/Resources columns, and the three Featured Wisdom blog-article links.

Asset-loading paths (fonts/*.woff2, fonts/v25-fonts.css, crystals_data.js,
images/jyogi-photo.jpg) were deliberately left as document-relative — these
are resource loads specific to this one document, not navigation, and remain
correct regardless of future header reuse.

## Exact mapping applied
| Label | href |
|---|---|
| Home | `/` |
| Kundli | `/tools.html#astrology` |
| Tarot | `/tools.html#tarot` |
| Reports | `/tools.html#astrology` |
| Consultations | `/#consult` |
| Crystals | `/crystals.html` |
| Blog | `/blog/index.html` |
| About | `/#about` |
| Talk to Jyogi | `https://wa.me/919437794561` (unchanged, already absolute) |

## Cross-directory routing gate

Tested by resolving the actual href strings against `location.href` (the
browser's own URL-resolution algorithm, `new URL(href, base)`) from all 6
required locations:

- homepage (`/index.html`)
- `/blog/index.html`
- a `/blog/*.html` article (`free-kundli-online.html`)
- `/crystals.html`
- a `/crystals/*.html` product page (`shani-bracelet.html`)
- `/tools.html`

**Result: 48/48 checks pass (8 links × 6 locations).** Every link resolves to
the exact same absolute URL regardless of which directory depth it's
evaluated from. No nested-path bugs (`/blog/tools.html`, `/crystals/blog/...`,
etc.) at any tested location.

## Regression re-check after the change
- 10-width overflow (index.html): PASS, unchanged from prior round
- Theme cycle (dark/light/warm) + language persistence: functional, unaffected
- 60-check crystal product regression (6 products × 10 widths): PASS
- `tools.html`: Tarot section present, reviews section still absent
- `git diff --check`: clean, exit 0

## Scope note (not done, per explicit instruction)
Blog, Kundli/tools.html, and Tarot were NOT redesigned this batch. They keep
their existing (pre-V2.5) visual styling, and only ever receive the V2.5
ivory/navy/gold treatment via this new header when reached from index.html —
their own internal navigation and appearance is untouched. Bringing those
pages onto the V2.5 design system is explicitly flagged as next-stage
consistency work, not part of this header-routing batch.
