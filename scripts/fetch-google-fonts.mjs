#!/usr/bin/env node
/**
 * Fetch selected Google Fonts families into a local, licence-aware snapshot.
 * Metadata is fetched first; font binaries are checked out only for selected families.
 * Requires Git with partial-clone support. --all may consume substantial disk space.
 *
 * Usage:
 *   node scripts/fetch-google-fonts.mjs --out ./upstream-fonts/google-fonts --limit 100
 *   node scripts/fetch-google-fonts.mjs --out ./upstream-fonts/google-fonts --families "Noto Sans,Roboto"
 *   node scripts/fetch-google-fonts.mjs --out ./upstream-fonts/google-fonts --all
 */
import { spawnSync } from "node:child_process";
import { readFile, mkdir, writeFile, copyFile, stat } from "node:fs/promises";
import { resolve, join, basename } from "node:path";

const args=process.argv.slice(2);
const get=k=>{const i=args.indexOf(k);return i<0?null:args[i+1]};
const has=k=>args.includes(k);
const out=resolve(get("--out")||"./upstream-fonts/google-fonts");
const limit=Number(get("--limit")||"0");
const wanted=new Set((get("--families")||"").split(",").map(x=>x.trim().toLowerCase()).filter(Boolean));
const all=has("--all");
if(!all&&!limit&&!wanted.size){console.error("Choose --limit N, --families \"Name,Name\", or --all.");process.exit(2);}
const run=(cmd,argv,cwd)=>{const r=spawnSync(cmd,argv,{cwd,encoding:"utf8",maxBuffer:64*1024*1024});if(r.status!==0)throw Error((r.stderr||r.stdout||cmd).trim());return r.stdout.trim()};
const root=join(out,".google-fonts-source");
await mkdir(out,{recursive:true});
if(!(await stat(root).catch(()=>null)))run("git",["clone","--filter=blob:none","--depth","1","--no-checkout","https://github.com/google/fonts.git",root]);
const revision=run("git",["rev-parse","HEAD"],root);
run("git",["sparse-checkout","init","--no-cone"],root);
run("git",["sparse-checkout","set","--no-cone","ofl/*/METADATA.pb","apache/*/METADATA.pb","ufl/*/METADATA.pb"],root);
run("git",["checkout","HEAD","--","ofl","apache","ufl"],root);
const metadataPaths=run("git",["ls-files","-z"],root).split("\0").filter(p=>p.endsWith("/METADATA.pb"));
const parseScalar=(s,key)=>{const re=new RegExp("^\\s*"+key+":\\s*\\\"([^\\\"]*)\\\"","m");const m=s.match(re);return m?m[1]:""};
const parseList=(s,key)=>[...s.matchAll(new RegExp("^\\s*"+key+":\\s*\\\"([^\\\"]*)\\\"","gm"))].map(m=>m[1]);
const parseBlocks=(s,key)=>[...s.matchAll(new RegExp("^"+key+"\\s*\\{([\\s\\S]*?)^\\s*\\}","gm"))].map(m=>m[1]);
const families=[];
for(const p of metadataPaths){
 const content=run("git",["show","HEAD:"+p],root);
 const family=parseScalar(content,"name")||basename(join(root,p,".."));
 const license=parseScalar(content,"license"),id=p.split("/")[1];
 const licenseMap={OFL:"OFL-1.1",APACHE:"Apache-2.0",UFL:"Ubuntu-Font-1.0"};
 const fonts=parseBlocks(content,"fonts").map(b=>({filename:parseScalar(b,"filename"),style:parseScalar(b,"style")||"normal",weight:Number(parseScalar(b,"weight")||400)})).filter(x=>x.filename);
 families.push({id,family,license,licenseId:licenseMap[license]||license,fonts,subsets:parseList(content,"subsets"),primaryScript:parseScalar(content,"primary_script"),designer:parseScalar(content,"designer"),path:p});
}
const selected=families.filter(f=>!wanted.size||wanted.has(f.family.toLowerCase())||wanted.has(f.id.toLowerCase())).sort((a,b)=>a.family.localeCompare(b.family));
const chosen=all?selected:(limit?selected.slice(0,limit):selected);
if(!chosen.length){console.error("No matching Google Fonts families.");process.exit(1);}
const dirs=chosen.map(f=>f.path.slice(0,-"METADATA.pb".length));
run("git",["sparse-checkout","set","--no-cone",...dirs.map(p=>p+"*")],root);
run("git",["checkout","HEAD","--",...dirs],root);
let copied=0,bytes=0,skipped=0;
for(const f of chosen){
 const sourceDir=join(root,f.path,".."),destDir=join(out,f.id);
 await mkdir(destDir,{recursive:true});
 const localFiles=[];
 for(const file of f.fonts){
  const src=join(sourceDir,file.filename);
  if(!await stat(src).catch(()=>null)){skipped++;continue;}
  const dest=join(destDir,file.filename);
  await copyFile(src,dest);
  const st=await stat(dest);copied++;bytes+=st.size;
  localFiles.push({path:file.filename,variant:{weight:file.weight,style:file.style}});
 }
 const licenseName=f.license==="OFL"?"OFL.txt":f.license==="APACHE"?"LICENSE.txt":"UFL.txt";
 const licensePath=join(sourceDir,licenseName);
 if(await stat(licensePath).catch(()=>null))await copyFile(licensePath,join(destDir,licenseName));
 const meta={id:f.id,canonicalId:f.id,family:f.family,designer:f.designer||null,provider:"Google Fonts",sourceUrl:"https://github.com/google/fonts/tree/"+revision+"/"+dirs[chosen.indexOf(f)],sourceRevision:revision,license:{id:f.licenseId,url:f.license==="OFL"?"https://openfontlicense.org/open-font-license-official-text/":null},languages:[],subsets:f.subsets,primaryScript:f.primaryScript||null,sourceFiles:localFiles,languageEvidence:"not inferred from subset names; requires exact language tags or cmap validation"};
 await writeFile(join(destDir,"family.json"),JSON.stringify(meta,null,2)+"\n");
}
const report={source:"https://github.com/google/fonts",revision,generatedAt:new Date().toISOString(),requested:all?"all":limit?{limit}:Array.from(wanted),selectedFamilies:chosen.length,copiedFontFiles:copied,skippedFontFiles:skipped,bytes,bytesMiB:Number((bytes/1048576).toFixed(2)),note:"Subset labels are not language tags. Review each family licence before redistribution."};
await writeFile(join(out,"google-fonts-fetch-report.json"),JSON.stringify(report,null,2)+"\n");
console.log(JSON.stringify(report,null,2));
