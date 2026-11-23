#!/usr/bin/env node
/**
 * Offline validation for the AWEFonts static site and its public data indexes.
 * No network access, writes, builds, Workers, Functions, or deployment.
 */
import { readFile, readdir, stat } from "node:fs/promises";
import { resolve, relative, sep } from "node:path";

const root=resolve(".");
const errors=[];
const warnings=[];
const readJson=async path=>JSON.parse(await readFile(resolve(root,path),"utf8"));
const exists=async path=>!!(await stat(resolve(root,path)).catch(()=>null));
const files=async dir=>{
  const out=[];
  for(const entry of await readdir(resolve(root,dir),{withFileTypes:true})){
    if(entry.name===".git"||entry.name==="node_modules")continue;
    const p=dir+"/"+entry.name;
    if(entry.isDirectory())out.push(...await files(p));
    else out.push(p);
  }
  return out;
};
const allFiles=await files(".");
const fileSet=new Set(allFiles.map(p=>p.replaceAll("\\","/")));
const [catalog,languages,assets,health,cssIndex]=await Promise.all([
  readJson("v1/catalog.json"),
  readJson("v1/languages.json"),
  readJson("v1/assets-index.json"),
  readJson("v1/health.json"),
  readJson("v1/css-index.json")
]);
const fonts=Array.isArray(catalog.fonts)?catalog.fonts:[];
const languageProfiles=Array.isArray(languages.languages)?languages.languages:[];
const unique=a=>new Set(a.filter(Boolean)).size;
const ids=fonts.map(f=>String(f.id||""));
const missingIds=ids.filter(x=>!x);
const duplicateIds=ids.length-unique(ids);
if(!fonts.length)errors.push("Catalog has no font families.");
if(missingIds.length)errors.push(missingIds.length+" font records have no stable id.");
if(duplicateIds)errors.push(duplicateIds+" duplicate font IDs detected.");
if(catalog.count!=null&&catalog.count!==fonts.length)errors.push("Catalog count does not equal catalog.fonts.length.");
if(!languageProfiles.length)errors.push("Language profile index is empty.");
const profileIds=languageProfiles.map(x=>x.id).filter(Boolean);
if(profileIds.length!==unique(profileIds))errors.push("Duplicate language profile IDs detected.");
if(assets.count!==assets.shards.reduce((n,s)=>n+Number(s.count||0),0))errors.push("Asset shard counts do not sum to assets-index.count.");
for(const shard of assets.shards||[]){
  if(!fileSet.has(shard.path))errors.push("Missing asset shard: "+shard.path);
}
const counts={
  families:fonts.length,
  languageCodes:unique(languageProfiles.map(x=>x.code)),
  languageScriptProfiles:languageProfiles.length,
  scripts:unique(languageProfiles.map(x=>x.script)),
  resources:assets.count,
  faceRecords:assets.faceRecords,
  binaryFontFiles:assets.binaryFiles,
  cssPresets:cssIndex.items?.length??cssIndex.presets?.length??cssIndex.fonts?.length??null
};
for(const [key,expected] of Object.entries({
  catalogCount:counts.families,
  fontAssetCount:counts.resources,
  fontFaceRecords:counts.faceRecords,
  binaryFontFiles:counts.binaryFontFiles,
  languageCount:counts.languageCodes,
  languageScriptProfiles:counts.languageScriptProfiles,
  scriptCount:counts.scripts
})){
  if(health[key]!==expected)errors.push("Health metadata mismatch for "+key+": expected "+expected+", got "+health[key]);
}
if(cssIndex.count!=null&&cssIndex.count!==counts.cssPresets)errors.push("CSS preset count metadata mismatch.");
const cssFiles=allFiles.filter(p=>p.startsWith("api/css/")&&p.endsWith(".css"));
if(counts.cssPresets!==null&&cssFiles.length!==counts.cssPresets)errors.push("CSS preset index and CSS file count differ ("+counts.cssPresets+" vs "+cssFiles.length+").");
for(const f of cssFiles)if((await readFile(resolve(root,f),"utf8")).trim().length===0)errors.push("Empty CSS preset: "+f);

// Check local root-relative references from all top-level HTML documents.
for(const html of allFiles.filter(p=>p.endsWith(".html")&&!p.startsWith("api-site/"))){
  const body=await readFile(resolve(root,html),"utf8");
  for(const m of body.matchAll(/(?:href|src)=["'](\/[^"'?#]*)/gi)){
    const target=m[1].replace(/^\//,"")||"index.html";
    if(target.startsWith("http")||target.startsWith("data:"))continue;
    if(!fileSet.has(target))errors.push(html+" references missing local asset "+m[1]);
  }
}

// Check public API mirrors that are intentionally duplicated.
for(const path of ["catalog.json","coverage-targets.json","css-index.json","health.json","openapi.json","sources.json","world-language-sources.json","embed.v6.js"]){
  const a="v1/"+path,b="api-site/v1/"+path;
  if(await exists(a)&&await exists(b)){
    const [x,y]=await Promise.all([readFile(resolve(root,a)),readFile(resolve(root,b))]);
    if(!x.equals(y))errors.push("Static API mirror mismatch: "+a+" vs "+b);
  }
}
for(const p of allFiles.filter(p=>p.endsWith(".json"))){
  try{await readJson(p);}catch(e){errors.push("Invalid JSON "+p+": "+e.message);}
}
if(fileSet.has("functions")||allFiles.some(p=>p.startsWith("functions/"))||fileSet.has("_worker.js"))errors.push("Unexpected Pages Functions/Worker entry point detected.");
if(counts.languageCodes<7000)warnings.push("The language index currently contains "+counts.languageCodes+" language codes, below the 7,000+ target. Do not inflate it with script aliases or dialects.");
if(counts.families<100000)warnings.push("The distinct-family catalog currently contains "+counts.families+" families; resource/face rows are not distinct font families.");
if(counts.binaryFontFiles===0)warnings.push("No indexed font binaries are present.");
warnings.push("Static validation does not prove every upstream licence, font glyph coverage, shaping quality, or rendering behaviour.");
const result={ok:errors.length===0,counts,warnings,errors};
console.log(JSON.stringify(result,null,2));
if(errors.length)process.exitCode=1;
