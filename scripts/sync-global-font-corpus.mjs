#!/usr/bin/env node
/**
 * Reproducible local corpus importer. No network calls, Workers, Functions or build steps.
 *
 * Usage:
 *   node scripts/sync-global-font-corpus.mjs --fonts ./upstream-fonts --languages ./languoid.csv --write
 * Font input: recursively discovered family.json or metadata.json files following the
 * normalized schema in docs/font-corpus-import.md. Binary paths are relative to the
 * metadata file. Only explicit language tags count as language claims.
 * Language input: Glottolog languoid.csv (or TSV export); status remains unknown unless
 * a separate, cited status field is provided.
 */
import { readFile, readdir, stat, mkdir, writeFile } from "node:fs/promises";
import { resolve, relative, extname, dirname, basename } from "node:path";
import { createHash } from "node:crypto";

const args=process.argv.slice(2),get=(k)=>{const i=args.indexOf(k);return i<0?null:args[i+1]};
const fontRoot=get("--fonts"),languageFile=get("--languages"),write=args.includes("--write");
const out=resolve(get("--out")||"v1/imported");
const errors=[],warnings=[];
const sha=async p=>createHash("sha256").update(await readFile(p)).digest("hex");
const walk=async root=>{const out=[];const visit=async d=>{for(const e of await readdir(d,{withFileTypes:true})){const p=resolve(d,e.name);if(e.isDirectory())await visit(p);else if(["family.json","metadata.json"].includes(e.name))out.push(p)}};await visit(resolve(root));return out};
const norm=s=>String(s||"").normalize("NFKC").toLocaleLowerCase("en").replace(/[\s\p{P}\p{S}]+/gu,"");
const csv=(line,delimiter)=>{const a=[];let s="",q=false;for(let i=0;i<line.length;i++){const c=line[i];if(c==='"'&&line[i+1]==='"'&&q){s+='"';i++}else if(c==='"')q=!q;else if(c===delimiter&&!q){a.push(s);s=""}else s+=c}a.push(s);return a};
const families=[],seen=new Map(),languageRecords=[];
if(fontRoot){
 for(const file of await walk(fontRoot)){
  try{
   const m=JSON.parse(await readFile(file,"utf8"));
   const family=String(m.family||m.name||"").trim(),id=String(m.id||"").trim();
   if(!family||!id)throw Error("family and id are required");
   const lic=typeof m.license==="string"?m.license:(m.license?.id||m.license?.name||"");
   const licenceUrl=typeof m.license==="object"?m.license.url:"";
   if(!lic)throw Error("missing explicit licence");
   const rawFiles=Array.isArray(m.sourceFiles)?m.sourceFiles:(Array.isArray(m.files)?m.files:[]);
   if(!rawFiles.length)throw Error("no declared binary source files");
   const checked=[];
   for(const f of rawFiles){
    const p=resolve(dirname(file),f.path||f.file||"");
    if(!p.startsWith(resolve(dirname(file))+ "/"))throw Error("binary path escapes family directory");
    const st=await stat(p);if(!st.isFile()||!st.size)throw Error("missing or empty binary: "+(f.path||f.file));
    const format=extname(p).slice(1).toLowerCase();
    if(!["ttf","otf","woff","woff2"].includes(format))throw Error("unsupported font format: "+format);
    checked.push({path:relative(resolve(fontRoot),p).replaceAll("\\","/"),format,bytes:st.size,sha256:await sha(p),variant:f.variant||null});
   }
   const identity=norm(m.canonicalId||[family,m.designer||m.foundry||""].join("|"));
   if(seen.has(identity)){const prior=seen.get(identity);prior.alternateSources.push({provider:m.provider||m.source||"unspecified",id,sourceUrl:m.sourceUrl||m.url||"",license:lic});continue}
   const rec={id,canonicalKey:identity,family,designer:m.designer||m.foundry||null,provider:m.provider||m.source||"unspecified",sourceUrl:m.sourceUrl||m.url||"",license:{id:lic,url:licenceUrl||null},languages:[...new Set((m.languages||m.languageTags||[]).map(String))],sourceFiles:checked,alternateSources:[],evidence:"explicit-source-metadata",metadataPath:relative(resolve(fontRoot),file).replaceAll("\\","/")};
   seen.set(identity,rec);families.push(rec);
  }catch(e){errors.push({file,reason:e.message})}
 }
}
if(languageFile){
 const raw=await readFile(resolve(languageFile),"utf8"),lines=raw.split(/\r?\n/).filter(Boolean);
 if(lines.length){
  const delimiter=lines[0].includes("\t")?"\t":",",headers=csv(lines[0],delimiter).map(x=>x.trim());
  for(const line of lines.slice(1)){const vals=csv(line,delimiter);if(vals.length<headers.length)continue;const row=Object.fromEntries(headers.map((h,i)=>[h,vals[i]??""]));const id=row.id||row.glottocode||row.code,name=row.name||row.language;if(!id||!name)continue;
   const level=String(row.level||"").toLowerCase();
   languageRecords.push({id:String(id),name:String(name),level,source:"Glottolog",sourceUrl:"https://glottolog.org/resource/languoid/id/"+encodeURIComponent(id),vitality:row.vitality||row.status||"unknown",vitalityEvidence:row.vitality_source||row.status_source||null,script:"Zzzz",scriptStatus:"unassigned",fontFamilyIds:[]});
  }
 }
}
const report={generatedAt:new Date().toISOString(),inputs:{fontRoot:fontRoot||null,languageFile:languageFile||null},fontFamilies:families.length,languageRecords:languageRecords.length,languageRecordsWithUnknownVitality:languageRecords.filter(x=>x.vitality==="unknown").length,errors,warnings:["No font is counted unless a real binary file exists and has a SHA-256 hash.","No language coverage is inferred from script alone.","Historical/extinct status and script assignment are never guessed.","This importer does not fetch upstream repositories; prepare source snapshots locally and record their immutable revisions."],familyRecords:families,languageRegistry:languageRecords};
if(write){await mkdir(out,{recursive:true});await writeFile(resolve(out,"verified-fonts.json"),JSON.stringify({version:1,count:families.length,families},null,2)+"\n");await writeFile(resolve(out,"world-languages.json"),JSON.stringify({version:1,count:languageRecords.length,languages:languageRecords},null,2)+"\n");await writeFile(resolve(out,"import-report.json"),JSON.stringify({...report,familyRecords:undefined,languageRegistry:undefined},null,2)+"\n")}
else console.log(JSON.stringify({...report,familyRecords:families.slice(0,5),languageRegistry:languageRecords.slice(0,5)},null,2));
if(errors.length)process.exitCode=1;
