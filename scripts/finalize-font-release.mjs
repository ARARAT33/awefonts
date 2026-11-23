#!/usr/bin/env node
/** Build the public static index for a successfully uploaded GitHub Release. */
import { readFile, readdir, stat, writeFile } from "node:fs/promises";
import { createReadStream } from "node:fs";
import { resolve, join, basename } from "node:path";
import { createHash } from "node:crypto";
const args=process.argv.slice(2),get=k=>{const i=args.indexOf(k);return i<0?null:args[i+1]};
const manifest=JSON.parse(await readFile(resolve(get("--manifest")),"utf8"));
const partsDir=resolve(get("--parts-dir")),tag=get("--tag");
if(!tag)throw Error("--tag is required");
const sha=path=>new Promise((ok,no)=>{const h=createHash("sha256");createReadStream(path).on("data",x=>h.update(x)).on("end",()=>ok(h.digest("hex"))).on("error",no)});
const names=(await readdir(partsDir)).filter(x=>x.startsWith("google-fonts.tar.gz.part-")).sort();
if(!names.length)throw Error("No archive parts found");
const parts=[];
for(const name of names){const path=join(partsDir,name),s=await stat(path);parts.push({name,url:"https://github.com/ARARAT33/awefonts/releases/download/"+tag+"/"+name,bytes:s.size,sha256:await sha(path)})}
const record={schemaVersion:1,status:"available",provider:"Google Fonts",source:manifest.sourceUrl,sourceRevision:manifest.sourceRevision,releaseTag:tag,releaseUrl:"https://github.com/ARARAT33/awefonts/releases/tag/"+tag,generatedAt:new Date().toISOString(),familyCount:manifest.familyCount,binaryFileCount:manifest.binaryFileCount,totalBytes:manifest.totalBytes,licenseCounts:manifest.licenseCounts,duplicateRecordsRemoved:manifest.duplicateRecordsRemoved,rejectedFamilyCount:manifest.rejectedFamilyCount,parts,manifestAsset:{name:"google-fonts-corpus-manifest.json",url:"https://github.com/ARARAT33/awefonts/releases/download/"+tag+"/google-fonts-corpus-manifest.json"},restoreInstructions:{linuxMac:"cat google-fonts.tar.gz.part-* | tar -xz",windowsPowerShell:"Get-Content .\\google-fonts.tar.gz.part-* -AsByteStream | Set-Content google-fonts.tar.gz; tar -xzf google-fonts.tar.gz",note:"Download every part into one directory before reassembling. Verify each part against its SHA-256 first."}};
for(const path of ["v1/corpora/google-fonts.json","api-site/v1/corpora/google-fonts.json"]){const p=resolve(path);await (await import("node:fs/promises")).mkdir(join(p,".."),{recursive:true});await writeFile(p,JSON.stringify(record,null,2)+"\n")}
await writeFile(join(partsDir,"google-fonts-corpus-manifest.json"),JSON.stringify(manifest,null,2)+"\n");
console.log(JSON.stringify(record,null,2));
