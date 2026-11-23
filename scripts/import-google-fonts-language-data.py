#!/usr/bin/env python3
"""Import source-backed Google Fonts language/script profiles, historical flags and exemplars."""
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

def unquote(value):
    try:
        return json.loads(value)
    except Exception:
        return value[1:-1] if value.startswith('"') and value.endswith('"') else value

def parse_fields(block):
    result={}
    for line in block.splitlines():
        m=re.match(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*("(?:\\.|[^"\\])*"|true|false|-?\d+)\s*$',line)
        if not m:
            continue
        key,value=m.groups()
        if value.startswith('"'):
            parsed=unquote(value)
        elif value in ("true","false"):
            parsed=value=="true"
        else:
            try: parsed=int(value)
            except ValueError: parsed=value
        if key in result:
            if not isinstance(result[key],list):
                result[key]=[result[key]]
            result[key].append(parsed)
        else:
            result[key]=parsed
    return result

def extract_blocks(text):
    top=[]
    blocks={}
    current=None
    body=[]
    for line in text.splitlines():
        if current is None:
            m=re.match(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*\{\s*$',line)
            if m:
                current=m.group(1);body=[];continue
            top.append(line)
        else:
            if line.strip()=="}":
                blocks[current]=parse_fields("\n".join(body))
                current=None;body=[]
            else:
                body.append(line)
    return parse_fields("\n".join(top)),blocks

def unique_chars(values):
    seen=set();out=[]
    for value in values:
        for char in value or "":
            if char.isspace() or char in seen:
                continue
            seen.add(char);out.append(char)
    return "".join(out)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",required=True,help="Google Fonts lang Lib/gflanguages/data/languages directory")
    ap.add_argument("--revision",required=True,help="Exact git commit SHA for the source checkout")
    ap.add_argument("--languages",default="v1/languages.json")
    ap.add_argument("--languages-mirror",default="api-site/v1/languages.json")
    ap.add_argument("--out",default="v1/language-evidence.json")
    ap.add_argument("--api-mirror",default="api-site/v1/language-evidence.json")
    ap.add_argument("--health",default="v1/health.json")
    ap.add_argument("--health-mirror",default="api-site/v1/health.json")
    ap.add_argument("--minimum",type=int,default=1600)
    args=ap.parse_args()
    root=Path(args.root)
    profiles=[]
    for path in sorted(root.glob("*.textproto")):
        raw=path.read_text(encoding="utf-8")
        top,blocks=extract_blocks(raw)
        exemplar=blocks.get("exemplar_chars",{})
        sample=blocks.get("sample_text",{})
        profile_id=str(top.get("id") or path.stem)
        id_parts=profile_id.split("_",1)
        lang=str(top.get("language") or (id_parts[0] if id_parts else "")).strip().lower()
        script=str(top.get("script") or (id_parts[1] if len(id_parts)>1 else "")).strip()
        name=str(top.get("name") or top.get("preferred_name") or profile_id).strip()
        if not lang or not script:
            continue
        base=str(exemplar.get("base") or "")
        auxiliary=str(exemplar.get("auxiliary") or "")
        index=str(exemplar.get("index") or "")
        numerals=str(exemplar.get("numerals") or "")
        punctuation=str(exemplar.get("punctuation") or "")
        exemplar_chars=unique_chars([base,index,numerals,punctuation,auxiliary])
        sample_text=str(sample.get("tester") or sample.get("styles") or sample.get("specimen_48") or "")
        sample_chars=unique_chars([sample_text])
        historical=top.get("historical") if isinstance(top.get("historical"),bool) else None
        population=top.get("population") if isinstance(top.get("population"),int) else None
        regions=top.get("region") or []
        if not isinstance(regions,list): regions=[regions]
        source_url=f"https://github.com/googlefonts/lang/blob/{args.revision}/Lib/gflanguages/data/languages/{path.name}"
        profiles.append({
            "id":profile_id,"language":lang,"code":lang,"script":script,
            "name":name,"nameEvidence":"source-name" if top.get("name") else ("preferred-name" if top.get("preferred_name") else "profile-id-fallback"),"preferredName":top.get("preferred_name"),
            "autonym":top.get("autonym"),"population":population,
            "regions":regions,"historical":historical,
            "historicalEvidence":source_url if historical is True else None,
            "populationEvidence":source_url if population is not None else None,
            "exemplarCharacters":exemplar_chars,
            "exemplarParts":{"base":base,"index":index,"numerals":numerals,"punctuation":punctuation,"auxiliary":auxiliary},
            "sampleText":sample_text,"sampleTextCharacters":sample_chars,
            "exemplarType":"language-exemplar" if exemplar_chars else ("sample-text-only" if sample_chars else "none"),
            "sourceUrl":source_url
        })
    if len(profiles)<args.minimum:
        raise SystemExit(f"Only {len(profiles)} Google Fonts language profiles found; expected at least {args.minimum}.")
    profile_ids=[x["id"] for x in profiles]
    if len(profile_ids)!=len(set(profile_ids)):
        raise SystemExit("Duplicate Google Fonts language profile IDs detected.")
    codes=len(set(x["language"] for x in profiles))
    historical=sum(x["historical"] is True for x in profiles)
    exemplars=sum(bool(x["exemplarCharacters"]) for x in profiles)
    sample_only=sum(x["exemplarType"]=="sample-text-only" for x in profiles)
    source={
        "name":"Google Fonts language data",
        "url":"https://github.com/googlefonts/lang",
        "revision":args.revision,
        "license":"Apache-2.0",
        "licenseUrl":"https://github.com/googlefonts/lang/blob/"+args.revision+"/LICENSE.txt",
        "profilePath":"Lib/gflanguages/data/languages/*.textproto"
    }
    evidence={"version":1,"generatedAt":datetime.now(timezone.utc).isoformat(),"source":source,"profileCount":len(profiles),"languageCodeCount":codes,"historicalProfileCount":historical,"exemplarProfileCount":exemplars,"sampleTextOnlyProfileCount":sample_only,"languages":profiles}
    langs_path=Path(args.languages)
    langs=json.loads(langs_path.read_text(encoding="utf-8"))
    by_id={x["id"]:x for x in profiles}
    missing=[]
    for item in langs.get("languages",[]):
        profile=by_id.get(item.get("id"))
        if not profile:
            missing.append(item.get("id"));continue
        for key in ("preferredName","nameEvidence","autonym","population","regions","historical","historicalEvidence","populationEvidence","exemplarCharacters","exemplarParts","sampleText","sampleTextCharacters","exemplarType","sourceUrl"):
            item[key]=profile.get(key)
    langs["historicalProfileCount"]=historical
    langs["exemplarProfileCount"]=exemplars
    langs["sampleTextOnlyProfileCount"]=sample_only
    langs["languageEvidenceSourceRevision"]=args.revision
    langs["languageEvidenceSource"]="Google Fonts language data"
    if missing:
        langs["profilesMissingFromLanguageEvidence"]=missing
    else:
        langs.pop("profilesMissingFromLanguageEvidence",None)
    if len(langs.get("languages",[]))!=len(profiles):
        raise SystemExit(f"Language index/evidence profile count mismatch: {len(langs.get('languages',[]))} vs {len(profiles)}")
    evidence_text=json.dumps(evidence,ensure_ascii=False,separators=(",",":"))+"\n"
    langs_text=json.dumps(langs,ensure_ascii=False,separators=(",",":"))+"\n"
    for path,text in ((args.out,evidence_text),(args.api_mirror,evidence_text),(args.languages,langs_text),(args.languages_mirror,langs_text)):
        target=Path(path);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,encoding="utf-8")
    for path in (args.health,args.health_mirror):
        target=Path(path)
        if target.exists():
            health=json.loads(target.read_text(encoding="utf-8"))
            health["languageEvidenceProfileCount"]=len(profiles)
            health["historicalLanguageProfileCount"]=historical
            health["languageExemplarProfileCount"]=exemplars
            health["sampleTextOnlyLanguageProfileCount"]=sample_only
            health["languageEvidenceSourceRevision"]=args.revision
            target.write_text(json.dumps(health,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"changed":True,"profileCount":len(profiles),"languageCodeCount":codes,"historicalProfileCount":historical,"exemplarProfileCount":exemplars,"sampleTextOnlyProfileCount":sample_only,"sourceRevision":args.revision,"profilesMissingFromIndex":len(missing)}))
if __name__=="__main__":
    main()
