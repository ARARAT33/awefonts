#!/usr/bin/env node
// Read-only AWEFonts data-integrity audit. No network, writes, builds or deployments.
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
const read=async p=>JSON.parse(await readFile(resolve(p),"utf8"));
const norm=s=>String(s??"").normalize("NFKC").toLocaleLowerCase("en").replace(/[\s\p{P}\p{S}]+/gu,"");
const errors=[],warnings=[],report={};
const [catalog,languages,manifest]=await Promise.all([read("v1/catalog.json"),read("v1/languages.json"),read("v1/assets-index.json")]);
const fonts=Array.isArray(catalog.fonts)?catalog.fonts:[];
const profiles=Array.isArray(languages.languages)?languages.languages:[];
const uniq=a=>new Set(a.filter(Boolean)).size;
report.familyRecords=fonts.length;report.uniqueFamilies=uniq(fonts.map(f=>norm(f.family||f.name)));
report.uniqueIds=uniq(fonts.map(f=>String(f.id??"")));
report.duplicateFamilyRecords=fonts.length-report.uniqueFamilies;report.duplicateIds=fonts.length-report.uniqueIds;
const duplicateNameMap=new Map();
for(const f of fonts){
 const key=norm(f.family||f.name);
 if(!key)continue;
 const list=duplicateNameMap.get(key)||[];
 list.push({id:f.id||null,family:f.family||f.name||null,source:f.source||null,designer:f.designer||null,foundry:f.foundry||null,canonicalId:f.canonicalId||null,license:f.license||null});
 duplicateNameMap.set(key,list);
}
report.duplicateFamilyGroups=[...duplicateNameMap.values()].filter(group=>group.length>1).map(group=>({family:group[0].family,records:group})).slice(0,100);
if(!fonts.length)errors.push("No catalog font records.");
if(catalog.count!=null&&catalog.count!==fonts.length)errors.push("Catalog count mismatch.");
if(report.duplicateFamilyRecords)warnings.push("Repeated normalized display names exist across family records; review designer/foundry identity before treating them as duplicates.");
if(report.duplicateIds)errors.push("Duplicate font IDs detected.");
report.languageCodes=uniq(profiles.map(p=>p.code));report.languageScriptProfiles=profiles.length;report.scriptCount=uniq(profiles.map(p=>p.script));
const profileIds=new Set(profiles.map(p=>p.id)),codes=new Set(profiles.map(p=>p.code)),coverage=new Map(profiles.map(p=>[p.id,new Set()]));
for(const f of fonts)for(const tag of Array.isArray(f.languages)?f.languages:[]){
 if(profileIds.has(tag))coverage.get(tag)?.add(f.id);
 else if(codes.has(tag))for(const p of profiles)if(p.code===tag)coverage.get(p.id)?.add(f.id);
}
report.profilesWithExactLanguageTags=[...coverage.values()].filter(s=>s.size).length;
report.profilesWithoutExactLanguageTags=profiles.length-report.profilesWithExactLanguageTags;
const shards=(manifest.shards||[]).reduce((n,s)=>n+Number(s.count||0),0);
report.resourceRecords=manifest.count;report.shardDeclaredTotal=shards;report.faceRecords=manifest.faceRecords;report.binaryFiles=manifest.binaryFiles;
if(manifest.count!==shards)errors.push("Asset shard sum differs from manifest total.");
if(manifest.familyCount!==report.uniqueFamilies)warnings.push("Asset manifest family count differs from unique catalog families.");
const targets={rareOrEndangered:10,lowDistribution:1000,mediumDistribution:10000,wideDistribution:100000};
const gaps=[];let classified=0;
for(const p of profiles){const tier=p.coverageTier;if(!tier||!(tier in targets))continue;classified++;const actual=coverage.get(p.id)?.size||0;if(actual<targets[tier])gaps.push({profile:p.id,tier,actual,target:targets[tier]});}
report.coverageTargets=targets;report.classifiedProfiles=classified;report.unclassifiedProfiles=profiles.length-classified;report.profilesBelowTarget=gaps.length;
warnings.push("Coverage targets are goals, not inventory claims. Missing fonts must remain gaps; never pad with duplicates or fabricated families.");
warnings.push("Exact language tags are conservative evidence; script presence alone does not prove language coverage.");
console.log(JSON.stringify({ok:!errors.length,report,warnings,errors,first100CoverageGaps:gaps.slice(0,100)},null,2));
if(errors.length)process.exitCode=1;
