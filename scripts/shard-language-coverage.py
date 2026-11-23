#!/usr/bin/env python3
"""Shard large language coverage datasets into deploy-safe static JSON assets. Schema v2."""
import argparse
import json
import shutil
from pathlib import Path

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def write(path, data):
    target=Path(path)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(data,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    return target.stat().st_size

def expand(doc, root, folder):
    summaries=doc.get("languages",[])
    if not doc.get("shards"):
        return summaries
    details={}
    for shard in doc["shards"]:
        path=Path(root)/"v1"/shard["path"]
        data=load(path)
        for item in data.get("languages",[]):
            details[item["id"]]=item
    result=[]
    for summary in summaries:
        full=dict(summary)
        full.update(details.get(summary.get("id"),{}))
        result.append(full)
    if len(result)!=doc.get("count",len(result)) and folder=="language-registry":
        raise SystemExit("Language registry shard expansion count mismatch")
    return result

def make_shards(items, root, folder, prefix, chunk_size, kind, summary_mode):
    base=Path(root)/"v1"/folder
    mirror=Path(root)/"api-site"/"v1"/folder
    for directory in (base/"shards",mirror/"shards"):
        if directory.exists(): shutil.rmtree(directory)
        directory.mkdir(parents=True,exist_ok=True)
    summaries=[]
    shards=[]
    for offset in range(0,len(items),chunk_size):
        chunk=items[offset:offset+chunk_size]
        number=offset//chunk_size+1
        shard_id=f"{prefix}-{number:03d}"
        filename=shard_id+".json"
        rel=f"{folder}/shards/{filename}"
        url="/v1/"+rel
        detail={"version":1,"type":kind,"shard":shard_id,"start":offset,"count":len(chunk),"languages":chunk}
        size=write(base/"shards"/filename,detail)
        write(mirror/"shards"/filename,detail)
        shards.append({"id":shard_id,"path":rel,"url":url,"count":len(chunk),"bytes":size,"firstId":chunk[0].get("id"),"lastId":chunk[-1].get("id")})
        for item in chunk:
            if summary_mode=="registry":
                summary={k:v for k,v in item.items() if k not in ("fontFamilyIds","fontCoverageByProfile","sampleTextFamilyIds")}
                summary["topFontFamilyIds"]=(item.get("fontFamilyIds") or [])[:8]
                summary["topSampleTextFamilyIds"]=(item.get("sampleTextFamilyIds") or [])[:8]
            else:
                summary={k:v for k,v in item.items() if k not in ("completeFamilyIds","thresholdQualifiedFamilyIds","bestPartial","completeProviderFamilyIds","thresholdQualifiedProviderFamilyIds","sampleTextFamilyIds","sampleTextProviderFamilyIds","sampleTextThresholdFamilyIds","sampleTextThresholdProviderFamilyIds")}
                summary["topFamilyIds"]=(item.get("completeFamilyIds") or [])[:8]
                summary["topSampleTextFamilyIds"]=(item.get("sampleTextFamilyIds") or [])[:8]
                summary["topThresholdQualifiedFamilyIds"]=(item.get("thresholdQualifiedFamilyIds") or [])[:8]
                summary["bestPartialPreview"]=(item.get("bestPartial") or [])[:5]
            summary["detailsShard"]=url
            summaries.append(summary)
    return summaries,shards

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",default=".")
    ap.add_argument("--registry-chunk-size",type=int,default=250)
    ap.add_argument("--coverage-chunk-size",type=int,default=50)
    args=ap.parse_args()
    root=Path(args.root).resolve()
    registry_path=root/"v1/language-registry.json"
    coverage_path=root/"v1/language-cmap-coverage.json"
    health_path=root/"v1/health.json"
    registry=load(registry_path)
    coverage=load(coverage_path)
    registry_items=expand(registry,root,"language-registry")
    coverage_items=expand(coverage,root,"language-cmap-coverage")
    registry_summary,registry_shards=make_shards(registry_items,root,"language-registry","registry",args.registry_chunk_size,"language-registry-details","registry")
    coverage_summary,coverage_shards=make_shards(coverage_items,root,"language-cmap-coverage","cmap",args.coverage_chunk_size,"language-cmap-coverage-details","coverage")
    registry["languages"]=registry_summary
    registry["shards"]=registry_shards
    registry["detailsMode"]="sharded; use each language record's detailsShard for complete fontFamilyIds and per-script coverage"
    coverage["languages"]=coverage_summary
    coverage["shards"]=coverage_shards
    coverage["detailsMode"]="sharded; use each profile record's detailsShard for completeFamilyIds and partial font matches"
    registry_size=write(registry_path,registry)
    write(root/"api-site/v1/language-registry.json",registry)
    coverage_size=write(coverage_path,coverage)
    write(root/"api-site/v1/language-cmap-coverage.json",coverage)
    health=load(health_path)
    health["languageRegistryShardCount"]=len(registry_shards)
    health["languageRegistryIndexBytes"]=registry_size
    health["languageRegistryMaxShardBytes"]=max(x["bytes"] for x in registry_shards) if registry_shards else 0
    health["languageCmapCoverageShardCount"]=len(coverage_shards)
    health["languageCmapCoverageIndexBytes"]=coverage_size
    health["languageCmapCoverageMaxShardBytes"]=max(x["bytes"] for x in coverage_shards) if coverage_shards else 0
    write(health_path,health)
    write(root/"api-site/v1/health.json",health)
    print(json.dumps({
        "registryRecords":len(registry_items),"registryShards":len(registry_shards),
        "registryIndexBytes":registry_size,"registryMaxShardBytes":health["languageRegistryMaxShardBytes"],
        "coverageProfiles":len(coverage_items),"coverageShards":len(coverage_shards),
        "coverageIndexBytes":coverage_size,"coverageMaxShardBytes":health["languageCmapCoverageMaxShardBytes"]
    },indent=2))

if __name__=="__main__":
    main()
