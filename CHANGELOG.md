# Changelog

All notable changes to the Jyogi project are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).
Runtime changes and documentation-only changes are labelled explicitly.

## [Unreleased]

### Phase 2.5 — Stabilisation

#### R0 — Baseline & Safeguards — 2026-07-17 (documentation only, **no runtime change**)
- **Added** `docs/phase-2.5/` baseline set: `R0_BASELINE.md`, `ROUTE_BASELINE.md`,
  `API_BASELINE.md`, `SCREENSHOT_INDEX.md`, and the checksum manifest
  `CHECKSUMS_pre-phase-2.5.sha256`.
- **Added** `docs/release-notes/2026-07-17-r0-baseline-and-safeguards.md`.
- **Added** this `CHANGELOG.md`.
- **Recorded** (not fixed): 7 state observations (O-1…O-7) and 6 security/hygiene
  findings (S-1…S-6) for later R-stage triage.
- **Deferred to operator:** creation of Git tag `pre-phase-2.5-stabilisation`
  (no repo/`.git` access from the build environment).
- **Runtime files changed:** none. No `index.html`, `api.py`, privacy, sitemap,
  robots, translations, or dependency changes. Nothing deployed.
