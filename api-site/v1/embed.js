(function(){
"use strict";
var script=document.currentScript;
if(!script)return;
var api=(script.src||"").replace(/\/v1\/embed(?:\.v\d+)?\.js(?:\?.*)?$/,"");
var names=(script.getAttribute("data-font")||"").split(",").map(function(x){return x.trim();}).filter(Boolean);
var weights=(script.getAttribute("data-weights")||"400;700").split(/[;, ]+/).filter(Boolean);
var familyStack=[];
function addStyle(css){var s=document.createElement("style");s.setAttribute("data-awefonts","");s.textContent=css;document.head.appendChild(s);}
function addLink(href){if(document.querySelector('link[data-awefonts-href="'+href.replace(/"/g,"%22")+'"]'))return;var l=document.createElement("link");l.rel="stylesheet";l.href=href;l.setAttribute("data-awefonts-href",href);document.head.appendChild(l);}
function slug(s){return s.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,"").replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"");}
function googleCss(f){var available=(f.weights||[400]).map(Number).filter(function(x){return Number.isFinite(x);});if(!available.length)available=[400];var low=Math.min.apply(null,available),high=Math.max.apply(null,available);var w=weights.map(Number).filter(function(x){return Number.isFinite(x)&&(available.indexOf(x)>=0||(f.variable&&x>=low&&x<=high));});if(!w.length)w=f.variable&&available.length>1?[low,high]:[available[0]];var fam=encodeURIComponent(f.family).replace(/%20/g,"+");return "https://fonts.googleapis.com/css2?family="+fam+(w.length?":wght@"+w.join(";"):"")+"&display=swap";}
fetch(api+"/v1/catalog.json",{mode:"cors"}).then(function(r){if(!r.ok)throw Error("AWEFonts catalog "+r.status);return r.json();}).then(function(data){
 var catalog=data.fonts||[];
 names.forEach(function(name){
  var key=slug(name),f=catalog.find(function(x){return x.id===name||slug(x.family)===key||x.id===key;});
  if(!f){console.warn("[AWEFonts] Font not found:",name);return;}
  familyStack.push('"'+f.family.replace(/["\\]/g,"")+'"');
  if(f.source==="sil"&&f.webFontUrl){var w=(f.weights||[400])[0]||400;addStyle("@font-face{font-family:"+JSON.stringify(f.family)+";src:url("+JSON.stringify(f.webFontUrl)+") format('woff2');font-style:normal;font-weight:"+w+";font-display:swap}");}
  else if(f.source==="google")addLink(googleCss(f));
  else if(f.providerCss)addLink(f.providerCss);
 });
 if(familyStack.length&&script.getAttribute("data-apply")==="true"){var selector=script.getAttribute("data-selector")||"body";addStyle(selector+"{font-family:"+familyStack.join(",")+",sans-serif}");}
 document.dispatchEvent(new CustomEvent("awefonts:ready",{detail:{families:familyStack}}));
}).catch(function(e){console.error("[AWEFonts]",e);});
})();