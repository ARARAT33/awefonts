#!/usr/bin/env python3
"""Link real cmap results to Glottolog languages without merging script profiles into false claims."""
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def save(path, value):
    target=Path(path);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(value,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--coverage",default="work/language-cmap-coverage.json")
    ap.add_argument("--registry",default="v1/language-registry.json")
    ap.add_argument("--registry-mirror",default="api-site/v1/language-registry.json")
    ap.add_argument("--catalog",default="v1/catalog.json")
    ap.add_argument("--out",default="v1/language-cmap-coverage.json")
    ap.add_argument("--api-mirror",default="api-site/v1/language-cmap-coverage.json")
    ap.add_argument("--health",default="v1/health.json")
    ap.add_argument("--health-mirror",default="api-site/v1/health.json")
    args=ap.parse_args()
    coverage=load(args.coverage)
    registry=load(args.registry)
    catalog=load(args.catalog)
    profile_map={x["id"]:x for x in coverage.get("languages",[])}
    catalog_ids={}
    for family in catalog.get("fonts",[]):
        canonical=family.get("id")
        if not canonical: continue
        for alias in [canonical,*(family.get("aliases") or [])]:
            catalog_ids[str(alias)]=canonical
        for provider in family.get("providers") or []:
            if provider.get("id"): catalog_ids[str(provider["id"])]=canonical
    all_links=0
    languages_with_any=0
    languages_with_exemplar=0
    languages_with_sample_only=0
    for language in registry.get("languages",[]):
        profile_ids=language.get("googleFontsProfileIds") or []
        by_profile=[]
        union=set()
        exemplar_union=set()
        sample_union=set()
        for profile_id in profile_ids:
            record=profile_map.get(profile_id)
            if not record: continue
            mapped=sorted({catalog_ids.get(x,x) for x in record.get("completeFamilyIds",[])})
            union.update(mapped)
            if record.get("evidenceType")=="language-exemplar": exemplar_union.update(mapped)
            if record.get("evidenceType")=="sample-text-only": sample_union.update(mapped)
            by_profile.append({
                "profileId":profile_id,
                "evidenceType":record.get("evidenceType"),
                "completeFamilyCount":len(mapped),
                "fontFamilyIds":mapped,
                "requiredCharacterCount":record.get("requiredCharacterCount")
            })
        if union: languages_with_any+=1
        if exemplar_union: languages_with_exemplar+=1
        if sample_union and not exemplar_union: languages_with_sample_only+=1
        all_links+=len(union)
        language["fontFamilyIds"]=sorted(union)
        language["fontFamilyCount"]=len(union)
        language["fontCoverageByProfile"]=by_profile
        language["fontCoverageScope"]="language-script-profile; profile results are not merged into an assertion that every script is interchangeable"
        if exemplar_union:
            language["fontCoverage"]="cmap-exemplar-profile-match" if len(by_profile)<=1 else "multi-script-profile-matches"
            language["fontCoverageEvidence"]="all required codepoints from a sourced language exemplar are present in each listed matching font family"
        elif sample_union:
            language["fontCoverage"]="sample-text-only-cmap-match"
            language["fontCoverageEvidence"]="matching fonts contain all required codepoints from the cited sample text only; complete orthography is not established"
        elif by_profile:
            language["fontCoverage"]="no-complete-cmap-match"
            language["fontCoverageEvidence"]="no font family covered every required codepoint in the sourced exemplar/sample text"
        else:
            language["fontCoverage"]="unverified"
            language["fontCoverageEvidence"]="no matching language-script profile with usable character evidence"
    registry["cmapCoverage"]={
        "generatedAt":datetime.now(timezone.utc).isoformat(),
        "sourceFontFamilyCountInspected":coverage.get("familyCountInspected"),
        "languageScriptProfilesChecked":coverage.get("languageCountChecked"),
        "languageScriptProfilesRejected":coverage.get("languageCountRejected"),
        "exemplarProfilesChecked":coverage.get("exemplarLanguageCountChecked"),
        "sampleTextOnlyProfilesChecked":coverage.get("sampleTextLanguageCountChecked"),
        "glottologLanguagesWithAnyCompleteMatch":languages_with_any,
        "glottologLanguagesWithExemplarMatches":languages_with_exemplar,
        "glottologLanguagesWithSampleTextOnlyMatches":languages_with_sample_only,
        "languageFontFamilyLinks":all_links,
        "evidence":"FontTools cmap codepoint presence against exact Google Fonts language exemplars or sample text; not shaping validation"
    }
    registry["coveragePolicy"]="fontFamilyIds are only actual cmap matches from the pinned Google Fonts binary corpus. Results are profile-level; sample-text-only results do not prove full orthography. Multi-script language records retain per-profile results. No shaping or rendering claim is made."
    coverage["catalogFamilyIdsMapped"]=True
    coverage["catalogMappingNote"]="Google Fonts source family IDs are mapped to canonical AWEFonts catalog family IDs through exact provider IDs and aliases where available; unmatched IDs remain explicit."
    save(args.out,coverage)
    save(args.api_mirror,coverage)
    save(args.registry,registry)
    save(args.registry_mirror,registry)
    for path in (args.health,args.health_mirror):
        p=Path(path)
        if p.exists():
            health=load(path)
            health["cmapFontFamilyCountInspected"]=coverage.get("familyCountInspected",0)
            health["cmapLanguageScriptProfilesChecked"]=coverage.get("languageCountChecked",0)
            health["cmapLanguageScriptProfilesRejected"]=coverage.get("languageCountRejected",0)
            health["glottologLanguagesWithCmapMatches"]=languages_with_any
            health["glottologLanguagesWithExemplarMatches"]=languages_with_exemplar
            health["glottologLanguagesWithSampleTextOnlyMatches"]=languages_with_sample_only
            health["languageFontFamilyLinks"]=all_links
            save(path,health)
    print(json.dumps({"fontFamiliesInspected":coverage.get("familyCountInspected"),"languageProfilesChecked":coverage.get("languageCountChecked"),"exemplarProfilesChecked":coverage.get("exemplarLanguageCountChecked"),"sampleTextProfilesChecked":coverage.get("sampleTextLanguageCountChecked"),"glottologLanguagesWithAnyCompleteMatch":languages_with_any,"glottologLanguagesWithExemplarMatches":languages_with_exemplar,"glottologLanguagesWithSampleTextOnlyMatches":languages_with_sample_only,"languageFontFamilyLinks":all_links},indent=2))

if __name__=="__main__":
    main()
