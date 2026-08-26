#!/usr/bin/env python3
"""
sync_csv.py — keep master_translations.csv in sync with the HTML
─────────────────────────────────────────────────────────────────
Scans your HTML file(s) for data-i18n / data-i18n-placeholder / data-i18n-title
/ data-i18n-aria keys. Any key that is NOT already in the CSV gets APPENDED as a
new row, with the English text pre-filled from the HTML and the hi/or columns
left BLANK for you to translate.

It never touches or overwrites existing rows — your translations are safe.

Usage:
    python3 sync_csv.py index.html
    python3 sync_csv.py index.html crystals.html numerology.html   (multiple files)

Then: open master_translations.csv, fill in the blank hi/or cells for the new
rows, and run build_translations.py.
"""
import csv
import re
import sys
import os

CSV_PATH = "master_translations.csv"
LANGS = ["en", "hi", "or"]

# Matches: data-i18n="key", data-i18n-placeholder="key", etc. + captures the
# element's inner text (for data-i18n) as the English default.
ATTR_RE = re.compile(r'data-i18n(?:-(?:placeholder|title|aria))?="([^"]+)"')
# For pulling inner text of <tag data-i18n="key">English here</tag>
TEXT_RE = re.compile(r'data-i18n="([^"]+)"\s*>([^<]*)<')
PH_RE   = re.compile(r'data-i18n-placeholder="([^"]+)"[^>]*placeholder="([^"]*)"')


def load_existing_keys():
    keys = set()
    rows = []
    header = ["key", "section", "en", "hi", "or", "notes"]
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            header = reader.fieldnames or header
            for row in reader:
                k = (row.get("key") or "").strip()
                if k:
                    keys.add(k)
                rows.append(row)
    return keys, rows, header


def scan_html(paths):
    """Return {key: english_default} for every i18n key found in the HTML."""
    found = {}
    for path in paths:
        if not os.path.exists(path):
            print(f"  ⚠️  file not found: {path}")
            continue
        html = open(path, encoding="utf-8").read()

        # data-i18n text keys (capture inner text as English default)
        for key, text in TEXT_RE.findall(html):
            found.setdefault(key, text.strip())
        # placeholder keys (capture placeholder value as English default)
        for key, ph in PH_RE.findall(html):
            found.setdefault(key, ph.strip())
        # any other i18n attr keys (title/aria) — default blank, fill later
        for key in ATTR_RE.findall(html):
            found.setdefault(key, "")
    return found


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: python3 sync_csv.py <file.html> [more.html ...]")

    paths = sys.argv[1:]
    existing_keys, existing_rows, header = load_existing_keys()
    found = scan_html(paths)

    new_keys = [k for k in found if k not in existing_keys]
    if not new_keys:
        print("✅ CSV already in sync — no new keys found.")
        return

    # Append new rows (en pre-filled, hi/or blank for translation)
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for key in new_keys:
            section = key.split(".")[0] if "." in key else ""
            writer.writerow([key, section, found[key], "", "", "NEW — needs hi/or"])

    print(f"✅ Appended {len(new_keys)} new key(s) to {CSV_PATH}:")
    for k in new_keys:
        print(f"   + {k}   (en: \"{found[k][:40]}\")")
    print(f"\nNext: open {CSV_PATH}, fill the blank hi/or cells for these rows,")
    print("then run:  python3 build_translations.py")


if __name__ == "__main__":
    main()
