#!/usr/bin/env python3
"""
build_translations.py
──────────────────────
Converts master_translations.csv → translations.json

Usage:
    python3 build_translations.py

Run this every time you edit the CSV, then redeploy translations.json.
"""
import csv
import json
import sys

CSV_PATH = "master_translations.csv"
JSON_PATH = "translations.json"
LANGS = ["en", "hi", "or"]  # add a column + add here if a 4th language is ever needed


def build():
    data = {lang: {} for lang in LANGS}
    seen_keys = set()
    row_count = 0
    warnings = []

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Validate header has what we need
        required = {"key", *LANGS}
        missing = required - set(reader.fieldnames or [])
        if missing:
            sys.exit(f"CSV is missing required columns: {missing}")

        for i, row in enumerate(reader, start=2):  # row 2 = first data row (after header)
            key = (row.get("key") or "").strip()
            if not key:
                continue  # skip blank rows

            if key in seen_keys:
                warnings.append(f"Row {i}: duplicate key '{key}' — last one wins")
            seen_keys.add(key)

            for lang in LANGS:
                value = (row.get(lang) or "").strip()
                if not value and lang != "en":
                    # Missing translation: fall back to English at build time.
                    # (The JS also has a runtime fallback, this is a belt-and-suspenders copy.)
                    value = (row.get("en") or "").strip()
                    warnings.append(f"Row {i}: '{key}' missing '{lang}' — using English")
                data[lang][key] = value
            row_count += 1

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)

    print(f"✅ Built {JSON_PATH}: {row_count} keys × {len(LANGS)} languages")
    if warnings:
        print(f"\n⚠️  {len(warnings)} warning(s):")
        for w in warnings:
            print(f"   {w}")


if __name__ == "__main__":
    build()
