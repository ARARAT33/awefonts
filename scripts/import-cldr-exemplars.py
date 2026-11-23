#!/usr/bin/env python3
"""Extract Unicode CLDR language exemplar characters from common/main XML.

CLDR exemplars are modern-locale evidence, not a complete world-language census.
Explicit codepoint ranges and Unicode escapes are expanded. Multi-character
exemplar strings are preserved separately; cmap validation checks codepoints only.
"""
import argparse
import json
import re
import subprocess
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

TOKEN_RE = re.compile(r"\\[uU][0-9A-Fa-f]{4,8}|\\[\\]|\\[{}-]|\[:[^]]*:\]|\{[^{}]*\}|[^\s]")

def parse_set(value):
    text = (value or "").strip()
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1]
    tokens = TOKEN_RE.findall(text)
    chars, sequences, warnings, decoded = set(), set(), [], []
    for token in tokens:
        if token.startswith("{") and token.endswith("}"):
            seq = unicodedata.normalize("NFC", token[1:-1])
            if seq:
                sequences.add(seq)
            continue
        if token.startswith("[:") and token.endswith(":]"):
            warnings.append("UnicodeSet property pattern not expanded: " + token)
            continue
        if token.startswith("\\u") or token.startswith("\\U"):
            try:
                decoded.append(chr(int(token[2:], 16)))
            except (ValueError, OverflowError):
                warnings.append("invalid Unicode escape " + token)
        elif token.startswith("\\"):
            if len(token) == 2:
                decoded.append(token[1])
            else:
                warnings.append("unsupported escape " + token)
        else:
            decoded.append(token)
    i = 0
    while i < len(decoded):
        if i + 2 < len(decoded) and decoded[i + 1] == "-":
            left, right = ord(decoded[i]), ord(decoded[i + 2])
            if left <= right and right - left <= 4096:
                chars.update(chr(cp) for cp in range(left, right + 1))
            else:
                warnings.append("invalid or oversized range " + decoded[i] + "-" + decoded[i + 2])
            i += 3
        else:
            chars.add(decoded[i])
            i += 1
    chars = {unicodedata.normalize("NFC", c) for c in chars if c}
    return "".join(sorted(chars, key=ord)), sorted(sequences), warnings

def self_test():
    chars, sequences, warnings = parse_set(r"[a-z {ch} \u00E9]")
    assert "a" in chars and "z" in chars and "m" in chars and "é" in chars
    assert sequences == ["ch"]
    assert not warnings
    chars, _, warnings = parse_set(r"[A-C \U0001F600]")
    assert all(c in chars for c in "ABC") and "😀" in chars
    assert not warnings

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cldr-root", help="CLDR repository checkout")
    ap.add_argument("--out", default="cldr-language-exemplars.json")
    ap.add_argument("--include-auxiliary", action="store_true")
    ap.add_argument("--revision", help="Immutable CLDR commit SHA; defaults to git HEAD")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        print("CLDR exemplar parser tests passed")
        return
    if not args.cldr_root:
        ap.error("--cldr-root is required unless --self-test is used")
    root = Path(args.cldr_root).resolve()
    main_dir = root / "common" / "main"
    if not main_dir.is_dir():
        ap.error("--cldr-root must contain common/main")
    revision = args.revision
    if not revision:
        try:
            revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        except Exception:
            ap.error("Pass --revision when the CLDR source is not a Git checkout")
    records, errors = [], []
    for path in sorted(main_dir.glob("*.xml")):
        try:
            xml_root = ET.parse(path).getroot()
            identity = xml_root.find("./identity")
            language_node = identity.find("./language") if identity is not None else None
            if language_node is None:
                continue
            code = language_node.attrib.get("type", "").strip()
            if not code:
                continue
            name_node = xml_root.find("./localeDisplayNames/languages/language[@type='" + code + "']")
            name = (name_node.text or "").strip() if name_node is not None else code
            exemplar = xml_root.find("./characters/exemplarCharacters[@type='main']")
            if exemplar is None:
                exemplar = xml_root.find("./characters/exemplarCharacters")
            if exemplar is None or not exemplar.text:
                continue
            main_chars, main_sequences, warns = parse_set(exemplar.text)
            all_chars, all_sequences = set(main_chars), set(main_sequences)
            if args.include_auxiliary:
                aux = xml_root.find("./characters/exemplarCharacters[@type='auxiliary']")
                if aux is not None and aux.text:
                    aux_chars, aux_sequences, aux_warnings = parse_set(aux.text)
                    all_chars.update(aux_chars)
                    all_sequences.update(aux_sequences)
                    warns.extend(aux_warnings)
            script_node = identity.find("./script") if identity is not None else None
            territory_node = identity.find("./territory") if identity is not None else None
            records.append({
                "id": code,
                "name": name or code,
                "source": "Unicode CLDR",
                "sourceUrl": "https://github.com/unicode-org/cldr/tree/" + revision + "/common/main/" + path.name,
                "cldrRevision": revision,
                "script": script_node.attrib.get("type") if script_node is not None else None,
                "territory": territory_node.attrib.get("type") if territory_node is not None else None,
                "exemplarCharacters": "".join(sorted(all_chars, key=ord)),
                "mainExemplarCharacters": main_chars,
                "exemplarSequences": sorted(all_sequences),
                "exemplarCharacterCount": len(all_chars),
                "exemplarWarnings": sorted(set(warns))
            })
        except Exception as exc:
            errors.append({"file": path.name, "error": str(exc)})
    output = {
        "schemaVersion": 1,
        "source": "Unicode CLDR common/main",
        "sourceRevision": revision,
        "includeAuxiliary": args.include_auxiliary,
        "languageCount": len(records),
        "errorCount": len(errors),
        "languages": records,
        "limitations": [
            "CLDR covers modern locales and is not a census of all world languages.",
            "Locale identifiers are not interchangeable with Glottolog IDs or ISO 639-3 codes without explicit crosswalks.",
            "Exemplar sets are practical character repertoires, not exhaustive orthographies.",
            "Multi-character strings are retained separately; this cmap pipeline checks codepoint presence only."
        ],
        "errors": errors
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"revision": revision, "languageCount": len(records), "errorCount": len(errors), "includeAuxiliary": args.include_auxiliary}, indent=2))
    if errors:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
