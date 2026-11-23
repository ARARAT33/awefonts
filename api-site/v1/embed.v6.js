(function(){"use strict";
var script=document.currentScript;if(!script)return;
var api=new URL(script.src,document.baseURI).origin;
var names=(script.getAttribute("data-font")||"").split(",").map(function(x){return x.trim();}).filter(Boolean);
var selector=script.getAttribute("data-selector")||"body";
var size=script.getAttribute("data-size")||"",line=script.getAttribute("data-line-height")||"",spacing=script.getAttribute("data-letter-spacing")||"";
var loaded=[],missing=[],familyNames=[],styleId="awefonts-embed-v6-style";
function slug(x){return String(x).normalize("NFKD").toLowerCase().replace(/[\u0300-\u036f]/g,"").replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"");}
function safeCssValue(v){return /^[0-9.]+(px|rem|em|%|vh|vw)?$/.test(v);}
function emit(name,detail){document.dispatchEvent(new CustomEvent(name,{detail:detail}));}
function addLink(href){if(document.querySelector('link[data-awefonts-href="'+href+'"]'))return;var l=document.createElement("link");l.rel="stylesheet";l.href=href;l.dataset.awefontsHref=href;document.head.appendChild(l);}
function apply(families){if(script.getAttribute("data-apply")!=="true"&&!size&&!line&&!spacing)return;
if(!/^[.#]?[a-zA-Z][\w.-]*(\s+[.#]?[a-zA-Z][\w.-]*)*$/.test(selector))throw Error("Invalid data-selector; use a simple tag, class or ID selector.");
var css=selector+"{font-family:"+families.map(function(n){return '"'+n.replace(/["\\]/g,"")+'"';}).join(",")+",sans-serif";
if(size){if(!safeCssValue(size))throw Error("Invalid data-size CSS value.");css+=";font-size:"+size;}
if(line){if(!safeCssValue(line))throw Error("Invalid data-line-height CSS value.");css+=";line-height:"+line;}
if(spacing){if(!safeCssValue(spacing))throw Error("Invalid data-letter-spacing CSS value.");css+=";letter-spacing:"+spacing;}
css+="}";var old=document.getElementById(styleId);if(old)old.remove();var st=document.createElement("style");st.id=styleId;st.textContent=css;document.head.appendChild(st);}
Promise.all([
fetch(api+"/v1/catalog.json",{mode:"cors"}).then(function(r){if(!r.ok)throw Error("Catalog HTTP "+r.status);return r.json();}),
fetch(api+"/v1/css-index.json",{mode:"cors"}).then(function(r){if(!r.ok)throw Error("CSS index HTTP "+r.status);return r.json();})
]).then(function(results){
var catalog=results[0].fonts||[],available=new Set((results[1].items||[]).map(function(x){return x.id;}));
names.forEach(function(name){var key=slug(name),f=catalog.find(function(x){return x.id===name||slug(x.family)===key||slug(x.id)===key;});if(!f){missing.push({name:name,reason:"not-in-catalog"});return;}
var id=slug(f.id||f.family);if(!available.has(id)){missing.push({name:name,family:f.family,reason:"no-committed-api-css-preset"});return;}
addLink(api+"/api/css/"+id+".css");loaded.push(f.family);familyNames.push(f.family);});
apply(familyNames);var detail={loaded:loaded,missing:missing,api:api,version:6};emit("awefonts:ready",detail);if(missing.length)emit("awefonts:missing",detail);
}).catch(function(error){emit("awefonts:error",{message:error.message,api:api,version:6});if(window.console&&console.error)console.error("[AWEFonts Embed v6]",error);});
})();