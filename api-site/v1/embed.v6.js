(function(){
"use strict";
var s=document.currentScript;if(!s)return;
var api=new URL(s.src,document.baseURI).origin;
var names=(s.getAttribute("data-font")||"").split(",").map(function(x){return x.trim()}).filter(Boolean);
var selector=s.getAttribute("data-selector")||"body";
var size=s.getAttribute("data-size"),line=s.getAttribute("data-line-height"),spacing=s.getAttribute("data-letter-spacing");
var families=[];
function slug(x){return String(x).toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,"").replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"")}
function quote(x){return '"'+String(x).replace(/["\\]/g,"")+'"'}
function addLink(href){var l=document.createElement("link");l.rel="stylesheet";l.href=href;l.dataset.awefonts="";document.head.appendChild(l)}
function addStyle(text){var st=document.createElement("style");st.dataset.awefonts="";st.textContent=text;document.head.appendChild(st)}
fetch(api+"/v1/catalog.json",{mode:"cors"}).then(function(r){if(!r.ok)throw Error("Catalog "+r.status);return r.json()}).then(function(d){
 (d.fonts||[]).forEach(function(f){
  if(!names.some(function(n){return n===f.id||slug(n)===slug(f.family)||slug(n)===f.id}))return;
  families.push(quote(f.family));
  var path=f.apiCss||("/v1/css/"+encodeURIComponent(f.id)+".css");
  addLink(path.charAt(0)==="/"?api+path:path);
 });
 if(families.length&&(s.dataset.apply==="true"||size||line||spacing)){
  var css=selector+"{font-family:"+families.join(",")+",sans-serif";
  if(size)css+=";font-size:"+size;
  if(line)css+=";line-height:"+line;
  if(spacing)css+=";letter-spacing:"+spacing;
  addStyle(css+"}");
 }
 document.dispatchEvent(new CustomEvent("awefonts:ready",{detail:{families:families,api:api}}));
}).catch(function(e){console.error("[AWEFonts]",e)});
})();