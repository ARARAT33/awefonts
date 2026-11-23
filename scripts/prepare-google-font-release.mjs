#!/usr/bin/env node
/**
 * Verify and deduplicate an extracted Google Fonts snapshot before release.
 * Requires real files, explicit family metadata and a bundled licence text.
 */
import { readdir, readFile, writeFile, stat, unlink, rm } from "node:fs/promises";
import { createReadStream } from "node:fs";
import { resolve, join, dirname, relative, extname, isAbsolute } from "node:path";
import { createHash } from "node:crypto";

const args=process.argv.slice(2);
const arg=k=>{const i=args.indexOf(k);return i<0?null:args[i+1]};
const root=resolve(arg("--root")||"work/google-fonts");
const out=resolve(arg("--out")||"work/google-fonts-release-manifest.json");
const errors=[],rejected=[],duplicates=[],families=[],binaryHashes=new Map(),familyIdentities=new Map();
const norm=s=>String(s??"").normalize("NFKC").toLowerCase().replace(/[\s\p{P}\p{S}]+/gu,"");
const sha=path=>new Promise((ok,no)=>{const h=createHash("sha256");createReadStream(path).on("data",x=>h.update(x)).on("end",()=>ok(h.digest("hex"))).on("error",no)});
async function walk(dir){
 const out=[];for(const e of await readdir(dir,{withFileTypes:true})){if(e.name===".google-fonts-source")continue;const p=join(dir,e.name);if(e.isDirectory())out.push(...await walk(p));else if(e.name==="family.json")out.push(p)}return out;
}
let totalBytes=0,binaryCount=0;
for(const metadataPath of await walk(root)){
 const dir=dirname(metadataPath);let m;
 try{m=JSON.parse(await readFile(metadataPath,"utf8"))}catch(e){rejected.push({path:metadataPath,reason:"invalid family metadata: "+e.message});await rm(dir,{recursive:true,force:true});continue}
 const family=String(m.family||"").trim(),id=String(m.id||"").trim(),designer=String(m.designer||"").trim();
 const license=String(m.license?.id||"").trim(),sourceUrl=String(m.sourceUrl||"").trim();
 const identity=norm(family)+"|"+norm(designer||id);
 if(!family||!id||!m.canonicalId||!sourceUrl.startsWith("https://")||!["OFL-1.1","Apache-2.0","Ubuntu-Font-1.0"].includes(license)||!Array.isArray(m.sourceFiles)||!m.sourceFiles.length){
  rejected.push({id,family,reason:"missing family identity, immutable source URL, recognized licence or source files"});await rm(dir,{recursive:true,force:true});continue;
 }
 if(familyIdentities.has(identity)){
  duplicates.push({type:"family-identity",id,kept:familyIdentities.get(identity),family,designer});
  await rm(dir,{recursive:true,force:true});continue;
 }
 const licenseNames=["OFL.txt","UFL.txt","LICENSE.txt","License.txt","LICENSE","OFL"];
 let licenseFile=null;for(const name of licenseNames){if(await stat(join(dir,name)).catch(()=>null)){licenseFile=name;break}}
 if(!licenseFile){rejected.push({id,family,reason:"bundled licence text file missing"});await rm(dir,{recursive:true,force:true});continue}
 const accepted=[];
 for(const f of m.sourceFiles){
  const rel=String(f.path||"");const file=resolve(dir,rel),inside=relative(dir,file);
  if(!rel||!inside||isAbsolute(inside)||inside.split(/[\\/]/).includes("..")){rejected.push({id,family,reason:"unsafe binary path: "+rel});continue}
  const st=await stat(file).catch(()=>null);
  if(!st?.isFile()||!st.size||![".ttf",".otf",".woff",".woff2"].includes(extname(file).toLowerCase())){rejected.push({id,family,reason:"missing, empty or unsupported binary: "+rel});continue}
  const digest=await sha(file),prior=binaryHashes.get(digest);
  if(prior){duplicates.push({type:"binary-sha256",id,family,path:rel,kept:prior});await unlink(file);continue}
  binaryHashes.set(digest,id+"/"+rel);
  accepted.push({...f,bytes:st.size,sha256:digest});
  totalBytes+=st.size;binaryCount++;
 }
 if(!accepted.length){rejected.push({id,family,reason:"no unique valid binary files remain"});await rm(dir,{recursive:true,force:true});continue}
 familyIdentities.set(identity,id);
 m.sourceFiles=accepted;
 m.licenseFile=licenseFile;
 await writeFile(metadataPath,JSON.stringify(m,null,2)+"\n");
 families.push({id,family,designer:designer||null,license,sourceUrl,sourceRevision:m.sourceRevision,licenseFile,binaryFiles:accepted.length,bytes:accepted.reduce((n,x)=>n+x.bytes,0),files:accepted.map(x=>({path:x.path,bytes:x.bytes,sha256:x.sha256,variant:x.variant||null}))});
}
const licenseCounts=Object.fromEntries([...new Set(families.map(x=>x.license))].map(k=>[k,families.filter(x=>x.license===k).length]));
const manifest={schemaVersion:1,source:"Google Fonts",sourceUrl:"https://github.com/google/fonts",sourceRevision:families[0]?.sourceRevision||null,generatedAt:new Date().toISOString(),familyCount:families.length,binaryFileCount:binaryCount,totalBytes,licenseCounts,duplicateRecordsRemoved:duplicates.length,rejectedFamilyCount:rejected.length,families,duplicates,rejected};
if(families.length<1000)errors.push("Refusing to release fewer than 1,000 verified Google Fonts families.");
if(!families.length||!binaryCount)errors.push("No verified font binaries remain.");
if(errors.length){console.error(JSON.stringify({errors,manifest:{familyCount:families.length,binaryFileCount:binaryCount,rejectedFamilyCount:rejected.length}},null,2));process.exit(1)}
await writeFile(out,JSON.stringify(manifest,null,2)+"\n");
console.log(JSON.stringify({ok:true,familyCount:families.length,binaryFileCount:binaryCount,totalBytes,licenseCounts,duplicatesRemoved:duplicates.length,rejectedFamilyCount:rejected.length,manifest:out},null,2));
