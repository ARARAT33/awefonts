#!/usr/bin/env python3
"""Validate font glyph coverage against sourced language exemplar character sets.

Requires: python -m pip install fonttools brotli
This checks character presence in cmap tables; it does NOT validate shaping,
orthography, mark positioning, ligatures, or full language usability.
"""
import argparse
import hashlib
import json
import os
import sys
import unicodedata
from pathlib import Path

try:
    from fontTools.ttLib import TTFont
except ImportError:
    print("Missing dependency. Install with: python -m pip install fonttools brotli", file=sys.stderr)
    raise SystemExit(2)


def load_json(path):
    with open(path, "r", encoding="utf-8") as stream:
        return json.load(stream)


def required_codepoints(value):
    result = set()
    for char in value or "":
        category = unicodedata.category(char)
        if category.startswith(("L", "M", "N")):
            result.add(ord(char))
    return result


def inspect_font(path, expected_hash=None):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    actual_hash = digest.hexdigest()
    if expected_hash and actual_hash != expected_hash:
        raise ValueError("SHA-256 mismatch")
    font = TTFont(str(path), lazy=True, recalcBBoxes=False, recalcTimestamp=False)
    try:
        cmap = font.getBestCmap() or {}
        return set(cmap.keys()), actual_hash
    finally:
        font.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fonts-root", required=True, help="Root used by the corpus importer")
    parser.add_argument("--corpus", required=True, help="verified-fonts.json from the importer")
    parser.add_argument("--exemplars", required=True, help="JSON with sourced language exemplarCharacters")
    parser.add_argument("--out", default="cmap-coverage.json")
    parser.add_argument("--minimum-ratio", type=float, default=1.0)
    args = parser.parse_args()
    if not 0 < args.minimum_ratio <= 1:
        parser.error("--minimum-ratio must be in (0, 1]")

    root = Path(args.fonts_root).resolve()
    corpus = load_json(args.corpus)
    language_data = load_json(args.exemplars)
    families = corpus.get("families", [])
    languages = language_data.get("languages", [])
    usable_languages = []
    rejected_languages = []
    for item in languages:
        chars = item.get("exemplarCharacters", "")
        source = item.get("sourceUrl") or item.get("source")
        required = required_codepoints(chars)
        if not item.get("id") or not isinstance(source, str) or not source.startswith(("https://", "http://")) or not required:
            rejected_languages.append({
                "id": item.get("id"),
                "reason": "requires id, sourceUrl/source, and non-empty exemplarCharacters"
            })
            continue
        usable_languages.append({
            "id": str(item["id"]),
            "name": item.get("name"),
            "sourceUrl": source,
            "required": required
        })

    family_codepoints = {}
    errors = []
    for family in families:
        family_id = str(family.get("id") or "")
        combined = set()
        for file_record in family.get("sourceFiles", []):
            rel = file_record.get("path")
            if not rel:
                errors.append({"familyId": family_id, "reason": "font file record has no path"})
                continue
            path = (root / rel).resolve()
            if root not in path.parents:
                errors.append({"familyId": family_id, "file": rel, "reason": "path escapes fonts root"})
                continue
            try:
                codepoints, digest = inspect_font(path, file_record.get("sha256"))
                combined.update(codepoints)
            except Exception as exc:
                errors.append({"familyId": family_id, "file": rel, "reason": str(exc)})
        if family_id:
            family_codepoints[family_id] = combined

    results = []
    for lang in usable_languages:
        required = lang["required"]
        exact = []
        qualifying = []
        partial = []
        for family_id, available in family_codepoints.items():
            present = required & available
            ratio = len(present) / len(required)
            if ratio == 1.0:
                exact.append(family_id)
            if ratio >= args.minimum_ratio:
                qualifying.append(family_id)
            elif ratio:
                partial.append({
                    "familyId": family_id,
                    "ratio": round(ratio, 6),
                    "missingCodepoints": [f"U+{cp:04X}" for cp in sorted(required - available)[:100]]
                })
        partial.sort(key=lambda x: (-x["ratio"], x["familyId"]))
        results.append({
            "id": lang["id"],
            "name": lang["name"],
            "sourceUrl": lang["sourceUrl"],
            "requiredCharacterCount": len(required),
            "completeFamilyCount": len(exact),
            "completeFamilyIds": sorted(exact),
            "thresholdQualifiedFamilyCount": len(qualifying),
            "thresholdQualifiedFamilyIds": sorted(qualifying),
            "partialFamilyCount": len(partial),
            "bestPartial": partial[:20],
            "minimumRatio": args.minimum_ratio,
            "evidence": "cmap codepoint presence against sourced exemplarCharacters; not shaping validation"
        })

    output = {
        "version": 1,
        "fontsRoot": os.path.relpath(root, Path.cwd()),
        "familyCountInspected": len(family_codepoints),
        "languageCountChecked": len(results),
        "languageCountRejected": len(rejected_languages),
        "familiesWithAnyCmapData": sum(bool(v) for v in family_codepoints.values()),
        "errors": errors,
        "rejectedLanguages": rejected_languages,
        "languages": results,
        "limitations": [
            "Cmap presence does not prove shaping, mark positioning, ligatures, orthography, or rendering quality.",
            "An exemplar is only as complete as its cited source; full language support needs specialist review.",
            "No language support is inferred from script names or generic subset labels."
        ]
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: output[k] for k in ("familyCountInspected", "languageCountChecked", "languageCountRejected", "familiesWithAnyCmapData", "errorCount") if k in output} | {"errors": len(errors)}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
