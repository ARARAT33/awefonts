#!/usr/bin/env python3
"""Build a source-backed Glottolog language-level registry without guessing scripts or font coverage."""
import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

def key(value):
    return re.sub(r"[^a-z0-9]", "", str(value or "").lower())

def split_values(value):
    if not value:
        return []
    return [x.strip() for x in re.split(r"[;,]", str(value)) if x.strip()]

def number(value):
    try:
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--csv",required=True)
    ap.add_argument("--manifest",required=True)
    ap.add_argument("--out",default="v1/language-registry.json")
    ap.add_argument("--api-mirror",default="api-site/v1/language-registry.json")
    ap.add_argument("--health",default="v1/health.json")
    ap.add_argument("--health-mirror",default="api-site/v1/health.json")
    ap.add_argument("--minimum",type=int,default=7000)
    args=ap.parse_args()
    manifest=json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    source=manifest.get("csv",{})
    with Path(args.csv).open("r",encoding="utf-8-sig",newline="") as handle:
        reader=csv.DictReader(handle)
        headers={key(h):h for h in (reader.fieldnames or [])}
        required={"id","name","level"}
        if not required.issubset(headers):
            raise SystemExit("Glottolog CSV missing required columns: "+", ".join(sorted(required-set(headers))))
        rows=[]
        seen=set()
        for raw in reader:
            row={key(k):v for k,v in raw.items() if k}
            if str(row.get("level","")).strip().lower()!="language":
                continue
            glottocode=str(row.get("id","")).strip().lower()
            name=str(row.get("name","")).strip()
            if not glottocode or not name or glottocode in seen:
                continue
            seen.add(glottocode)
            iso=str(row.get("iso639p3code") or row.get("iso6393") or "").strip().lower() or None
            macroareas=split_values(row.get("macroareas"))
            countries=split_values(row.get("countries"))
            category=str(row.get("category") or "").strip() or None
            aes=str(row.get("aes") or row.get("agglomeratedendangermentstatus") or "").strip() or None
            item={
                "id":glottocode,
                "name":name,
                "level":"language",
                "iso6393":iso,
                "macroareas":macroareas,
                "countries":countries,
                "category":category,
                "latitude":number(row.get("latitude")),
                "longitude":number(row.get("longitude")),
                "classification":str(row.get("classification") or "").strip() or None,
                "endangerment":aes,
                "endangermentEvidence":"Glottolog 5.4 AES field" if aes else None,
                "script":None,
                "scriptStatus":"unassigned",
                "fontCoverage":"unverified",
                "sourceUrl":"https://glottolog.org/resource/languoid/id/"+glottocode
            }
            rows.append(item)
    rows.sort(key=lambda x:(x["name"].casefold(),x["id"]))
    if len(rows)<args.minimum:
        raise SystemExit(f"Only {len(rows)} language-level entries found; refusing to publish below safety threshold {args.minimum}.")
    registry={
        "version":1,
        "name":"AWEFonts World Language Registry",
        "generatedAt":datetime.now(timezone.utc).isoformat(),
        "count":len(rows),
        "languageCount":len(rows),
        "profileCount":1695,
        "source":{
            "name":"Glottolog",
            "release":manifest.get("release"),
            "sourcePage":manifest.get("sourcePage"),
            "downloadUrl":manifest.get("downloadUrl"),
            "csvSha256":source.get("sha256"),
            "license":"CC-BY-4.0",
            "citation":"Hammarström, Harald, Robert Forkel, Martin Haspelmath and Sebastian Bank. 2026. Glottolog 5.4. Leipzig: Max Planck Institute for Evolutionary Anthropology."
        },
        "countingPolicy":"Only Glottolog level=language records are included. Dialects, families, and other languoids are excluded.",
        "coveragePolicy":"Script assignment and font coverage remain unassigned/unverified unless separately evidenced. Glottolog language presence is not font-support evidence.",
        "languages":rows
    }
    out=Path(args.out)
    existing=None
    if out.exists():
        try: existing=json.loads(out.read_text(encoding="utf-8"))
        except Exception: existing=None
    if existing and existing.get("source",{}).get("csvSha256")==source.get("sha256") and existing.get("count")==len(rows):
        print(json.dumps({"changed":False,"count":len(rows),"release":manifest.get("release"),"csvSha256":source.get("sha256")}))
        return
    text=json.dumps(registry,ensure_ascii=False,separators=(",",":"))+"\n"
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(text,encoding="utf-8")
    mirror=Path(args.api_mirror);mirror.parent.mkdir(parents=True,exist_ok=True);mirror.write_text(text,encoding="utf-8")
    for health_path in [args.health,args.health_mirror]:
        hp=Path(health_path)
        if hp.exists():
            h=json.loads(hp.read_text(encoding="utf-8"))
            h["languageRegistryCount"]=len(rows)
            h["languageRegistryRelease"]=manifest.get("release")
            h["languageRegistrySource"]="Glottolog"
            hp.write_text(json.dumps(h,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"changed":True,"count":len(rows),"release":manifest.get("release"),"csvSha256":source.get("sha256")}))
if __name__=="__main__":
    main()
