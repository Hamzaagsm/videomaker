#!/usr/bin/env python3
# MEER v4.49 - NAYI KAHANI BHEJO + VAULT (Meri Script ke APNE scenes)
# Saboot (Hamza, 2026-10-21 ~12:51): "Meer mn he option rakho koi main waheen
# story bhj diya krun aor 1 ghnty baad mn dobara check krun to seen ready hon"
# MODEL CORRECTION (Hamza, usi din ~12:57): kahani ka NAAM app ki list me add
# NAHI karna. Uska workflow: kahani Meri Script box me lagao -> button dabao
# (pehli dafa kahani production ke liye bhej di jati hai, video aaj ki
# smart-matching se banti hai) -> ~1 ghanta baad YEHI script dobara lagao ->
# app khud usi kahani ke bane hue scenes (online VAULT, script ke hash par)
# download karke har line ka apna scene laga de; tayyar na hon to intezar
# aur dobara wahi smart-matching video.
# VAULT design (neeche VAULT_JS me tafseel + producer contract):
#  hash = FNV-1a 64-bit over normalized script (normalize spec VAULT_JS me).
#  manifest: raw.githubusercontent.../main/vault/<hash>/manifest.json
#  Java UNCHANGED rakhna tha, aur Java ke mojooda bridge sirf
#  CLIP_BASE_SUSP + 'susp-*' naam download karte hain aur composeVideo ka
#  getClipPath bhi sirf whitelisted/'susp-*' naam manta hai - is liye har
#  vault scene ka LOCAL naam 'susp-vault-<hash>-<i>.mp4' rakha gaya hai aur
#  producer scene files inhi naamo se suspense-clips/ me publish karega
#  (manifest vault/<hash>/ me rahega, clips[] tartib script wali hogi).
# Design:
#  HTML/JS: Suspense wale hisse (suspBtn wali wrap) ke aakhir me naya button
#   "📚 Nayi Kahani Bhejo" + chhupa panel (title input, bari kahani textarea,
#   "📤 Kahani Bhejo" button). Bhejne par JS MeerStoryBridge.sendStory(title,
#   body) call karta hai; tasdeeqi text screen par ata hai; {title, when}
#   localStorage list "meerSentStories" me save hokar "Meri bheji kahaniyan"
#   ke neeche dikhta hai. Bridge na mile to kahani selectable box me dikha
#   dete hain (copy karke chat me bhejna mumkin) - crash nahi, graceful.
#  Java: naya bridge class MeerStoryBridge - sendStory() email intent
#   (ACTION_SENDTO, mailto:) kholta hai: EXTRA_EMAIL=STORY_EMAIL,
#   EXTRA_SUBJECT="MEER KAHANI: "+title, EXTRA_TEXT=body; chooser ke sath
#   taake Hamza apni mail app me Send khud dabe.
#  !!! STORY_EMAIL PROVISIONAL hai - ship karne se pehle main agent confirm
#      karega ke ye inbox asal me monitor ho raha hai. !!!
# Regression-safety: purane code me SIRF APP_VER bump; baqi sab nayi
# insertions hain (naya JS block, naya Java class, 1 registration line).
# Har anchor exactly 1 hona chahiye, warna patch ABORT (koi file nahi likhi
# jayegi).
import re
import sys

HP = 'android/app/src/main/assets/www/index.html'
JP = 'android/app/src/main/java/com/hamza/videomaker/MainActivity.java'
html = open(HP, encoding='utf-8').read()
java = open(JP, encoding='utf-8').read()

ok = True

# ---------- HTML: APP_VER bump (sirf yahi purani line badalti hai) ----------
html, n1 = re.subn(r"APP_VER\s*=\s*[\"'][\d.]+[\"']", 'APP_VER="4.49"', html)
html, n2 = re.subn(r"v4\.\d+ MEER", "v4.49 MEER", html)
print('V449 APP_VER bump:', n1, n2)
if n1 != 1 or n2 != 1:
    ok = False

# ---------- HTML: naya JS block (suspense addUI IIFE ke foran baad) ----------
NEW_JS = r"""
/* ===== MEER v4.49: NAYI KAHANI BHEJO =====
   Hamza app ke andar se hi kahani bhej sakta hai: title + kahani paste ->
   MeerStoryBridge.sendStory (Java) email intent kholta hai; mail bhejne par
   kahani pohonch jati hai aur scenes ban kar kahani Suspense list me naam se
   aa jati hai. Bheji kahaniyon ki list localStorage 'meerSentStories' me
   rehti hai aur form ke neeche dikhti hai. Bridge na mile (purana version /
   browser) to kahani neeche box me dikha dete hain taake copy karke chat me
   bheji ja sake - crash nahi. */
function meerStoryRenderSent(){
  var box=document.getElementById('storySentList'); if(!box)return;
  var list=[]; try{ list=JSON.parse(localStorage.getItem('meerSentStories')||'[]'); }catch(e){}
  if(!list.length){ box.innerHTML=''; return; }
  var h='<div style="font-size:13px;color:#c4b5fd;margin-bottom:4px;">Meri bheji kahaniyan:</div>';
  for(var i=0;i<list.length;i++){
    h+='<div style="font-size:13px;color:#e5e7eb;">• '+String(list[i].title||'').replace(/</g,'&lt;')+' <span style="color:#9ca3af;">('+String(list[i].when||'')+')</span></div>';
  }
  box.innerHTML=h;
}
function meerStoryToggle(){
  var p=document.getElementById('storyPanel'); if(!p)return;
  p.style.display=(p.style.display==='block')?'none':'block';
  if(p.style.display==='block')meerStoryRenderSent();
}
function meerSendStory(){
  var tEl=document.getElementById('storyTitle'), bEl=document.getElementById('storyBody'), msg=document.getElementById('storyMsg');
  var title=(tEl&&tEl.value||'').trim(), body=(bEl&&bEl.value||'').trim();
  if(!title){ alert('Pehle kahani ka naam (title) likho!'); return; }
  if(!body){ alert('Kahani khali hai - pehle kahani paste karo!'); return; }
  var sent=false;
  try{ if(typeof MeerStoryBridge!=='undefined'&&MeerStoryBridge&&typeof MeerStoryBridge.sendStory==='function'){ MeerStoryBridge.sendStory(title,body); sent=true; } }catch(e){}
  var list=[]; try{ list=JSON.parse(localStorage.getItem('meerSentStories')||'[]'); }catch(e){}
  list.unshift({title:title,when:new Date().toLocaleString()});
  if(list.length>30)list=list.slice(0,30);
  try{ localStorage.setItem('meerSentStories',JSON.stringify(list)); }catch(e){}
  meerStoryRenderSent();
  if(msg)msg.style.display='block';
  if(sent){
    if(msg)msg.textContent='Kahani bhej di gayi! ✅ Scenes tayyar hote hi ye kahani Suspense list me naam se aa jayegi — 1-2 ghante baad app khol kar check kar lena.';
    if(tEl)tEl.value=''; if(bEl)bEl.value='';
  }else{
    var fb=document.getElementById('storyFallback');
    if(fb){ fb.style.display='block'; fb.value=title+'\n\n'+body; }
    if(msg)msg.textContent='Mail wala hissa is version me nahi mila - tumhari kahani neeche wale box me hai, use copy karke chat me bhej do. (Kahani yahan list me save kar di hai.)';
  }
}
(function(){
  function addStoryUI(){
    if(document.getElementById('storySendBtn'))return;
    var sb=document.getElementById('suspBtn');
    if(!sb||!sb.parentNode){ setTimeout(addStoryUI,1500); return; }
    var wrap=sb.parentNode;
    var btn=document.createElement('button');
    btn.id='storySendBtn'; btn.className='btn';
    btn.style.cssText='width:100%;margin-top:10px;background:linear-gradient(90deg,#b45309,#db2777);color:#fff;';
    btn.textContent='📚 Nayi Kahani Bhejo';
    btn.onclick=meerStoryToggle;
    var panel=document.createElement('div');
    panel.id='storyPanel'; panel.style.cssText='display:none;margin-top:8px;';
    panel.innerHTML='<input id="storyTitle" placeholder="Kahani ka naam (title)" style="width:100%;padding:10px;border-radius:10px;margin-bottom:8px;font-size:15px;">'
      +'<textarea id="storyBody" rows="8" placeholder="Apni kahani yahan paste karo — har line alag rakho" style="width:100%;padding:10px;border-radius:10px;font-size:14px;"></textarea>'
      +'<button id="storyGo" class="btn" style="width:100%;margin-top:8px;background:linear-gradient(90deg,#065f46,#16a34a);color:#fff;">📤 Kahani Bhejo</button>'
      +'<div id="storyMsg" style="display:none;margin-top:8px;font-size:13px;color:#86efac;text-align:left;"></div>'
      +'<textarea id="storyFallback" rows="6" readonly style="display:none;width:100%;padding:10px;border-radius:10px;margin-top:8px;font-size:13px;"></textarea>'
      +'<div id="storySentList" style="margin-top:10px;text-align:left;"></div>';
    wrap.appendChild(btn);
    wrap.appendChild(panel);
    var go=document.getElementById('storyGo'); if(go)go.onclick=meerSendStory;
    meerStoryRenderSent();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){ setTimeout(addStoryUI,1800); });
  else setTimeout(addStoryUI,1800);
})();
"""

VAULT_JS = r"""
/* ===== MEER v4.49: VAULT - Meri Script ke APNE scenes =====
   Hamza ka model: kahani Meri Script box me laga kar 'MERI SCRIPT SE VIDEO
   BANAO' dabao. Pehli dafa: kahani MeerStoryBridge se subject
   'VAULT <hash>' ke sath production ke liye bhej di jati hai (sirf AIK
   dafa - localStorage flag 'meerVaultSent_<hash>') aur video aaj wali
   smart-matching (suspMyMakeVideo) se ban jati hai. ~1 ghanta baad wo
   YEHI script dobara lagaye to app pehle online VAULT check karti hai:
   vault/<hash>/manifest.json tayyar ho aur clips ki tadaad script ki
   lines ke barabar ho -> usi kahani ke scenes download karke video
   1 line = 1 scene, script ki tartib me banti hai (awaz TTS se, pitch
   manifest se). Tayyar na ho -> purana smart-matching rasta hi chalta
   hai (aur pehli dafa ho to kahani bhej bhi di jati hai).
   Button ka onclick UI bante waqt ORIGINAL suspMyMakeVideo se bandha
   tha (reference usi waqt copy hota hai), is liye ye block button ko
   dobara wrapper se bind karta hai - original function chhua nahi gaya.
   HASH SPEC (producer ko bhi bilkul yehi karna hai):
     normalize(text): \r\n aur \r -> \n; '\n' par split; har line trim;
       khaali lines hatao; aakhri line /^THE END\.?$/i ho to wo bhi
       hatao (wo boli nahi jati); lines ko '\n' se joro = normalized.
     hash: FNV-1a 64-bit normalized ke UTF-8 bytes par (offset basis
       14695981039346656037, prime 1099511628211); output 16-char
       lowercase hex, zero-padded.
   PRODUCER CONTRACT:
     manifest: vault/<hash>/manifest.json =
       {"clips":["scene-1.mp4", ...script ki tartib me...], "pitch":1.15}
     Entry i (1-based) ki file app ke andar local naam
       'susp-vault-<hash>-<i>.mp4' se clipDir me utarti hai.
     Java bridge sirf CLIP_BASE_SUSP + 'susp-' wale naam download karta
     hai aur composeVideo ka getClipPath bhi sirf 'susp-*' naam manta
     hai, is liye producer ko har scene file inhi local naamo se
     'suspense-clips/' folder me publish karni hai (bytes wohi jo
     vault wali scene-<i>.mp4 ke hain). Har clip 100KB se bari ho
     (Java clipOk ki shart hai). */
var MEER_VAULT_BASE='https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/vault/';
function meerVaultNormalize(text){
  var t=String(text==null?'':text).replace(/\r\n/g,'\n').replace(/\r/g,'\n');
  var parts=t.split('\n'), lines=[];
  for(var i=0;i<parts.length;i++){ var s=parts[i].trim(); if(s.length) lines.push(s); }
  if(lines.length&&/^THE END\.?$/i.test(lines[lines.length-1])) lines.pop();
  return lines;
}
function meerVaultUtf8(str){
  var out=[];
  for(var i=0;i<str.length;i++){
    var c=str.charCodeAt(i);
    if(c<0x80){ out.push(c); }
    else if(c<0x800){ out.push(0xC0|(c>>6),0x80|(c&0x3F)); }
    else if(c>=0xD800&&c<=0xDBFF&&i+1<str.length&&str.charCodeAt(i+1)>=0xDC00&&str.charCodeAt(i+1)<=0xDFFF){
      var cp=0x10000+((c-0xD800)<<10)+(str.charCodeAt(i+1)-0xDC00); i++;
      out.push(0xF0|(cp>>18),0x80|((cp>>12)&0x3F),0x80|((cp>>6)&0x3F),0x80|(cp&0x3F));
    }
    else{ out.push(0xE0|(c>>12),0x80|((c>>6)&0x3F),0x80|(c&0x3F)); }
  }
  return out;
}
function meerVaultHash(text){
  var bytes=meerVaultUtf8(meerVaultNormalize(text).join('\n'));
  var hi=0xCBF29CE4, lo=0x84222325;
  for(var i=0;i<bytes.length;i++){
    lo=(lo^bytes[i])>>>0;
    var a=lo*0x1B3;
    var nHi=(Math.floor(a/4294967296)+hi*0x1B3+lo*0x100)%4294967296;
    var nLo=a%4294967296;
    hi=nHi; lo=nLo;
  }
  function h8(x){ var s=(x>>>0).toString(16); while(s.length<8)s='0'+s; return s; }
  return h8(hi)+h8(lo);
}
function meerVaultLocalName(hash,i){
  return 'susp-vault-'+hash+'-'+(i+1)+'.mp4';
}
function meerVaultDl(url,name){
  /* url = vault/<hash>/ wali asal file ka pata (wazahat/record ke liye);
     asal download stock suspense downloader se hota hai -
     RealClipBridge.downloadSuspClip sirf CLIP_BASE_SUSP + 'name' uthata
     hai, is liye local 'susp-vault-...' naam hi istemal hota hai aur
     producer scene files suspense-clips/ me inhi naamo se rakhta hai. */
  try{ if(typeof RealClipBridge!=='undefined'&&typeof RealClipBridge.downloadSuspClip==='function') return !!RealClipBridge.downloadSuspClip(name); }catch(e){}
  return false;
}
async function meerVaultEnsureClips(clips,hash,srcClips){
  var missing=clips.filter(function(n){ return !advOk(n); });
  if(!missing.length) return true;
  suspSetStatus('Tumhari kahani ke scenes download ho rahe hain ('+missing.length+')...');
  missing.forEach(function(n){
    var i=clips.indexOf(n);
    try{ meerVaultDl(MEER_VAULT_BASE+hash+'/'+(srcClips?srcClips[i]:n),n); }catch(e){}
  });
  var waited=0;
  while(waited<900000){
    await new Promise(function(r){ setTimeout(r,1500); }); waited+=1500;
    var left=clips.filter(function(n){ return !advOk(n); });
    if(!left.length) return true;
    suspSetStatus('Tumhari kahani ke scenes download ho rahe hain... '+left.length+' baqi');
  }
  return clips.every(function(n){ return advOk(n); });
}
async function meerVaultBuild(lines,man,hash){
  try{
    if(typeof RealClipBridge==='undefined'||typeof RealClipBridge.composeVideo!=='function') return false;
    var clips=[];
    for(var i=0;i<lines.length;i++) clips.push(meerVaultLocalName(hash,i));
    if(!await meerVaultEnsureClips(clips,hash,man.clips)) return false;
    var bar=document.getElementById('realBar'), prog=document.getElementById('realProg');
    if(prog)prog.style.display='block';
    var pitch=man.pitch||1.15;
    var segments=[];
    for(var i2=0;i2<lines.length;i2++){
      if(bar)bar.style.width=(5+i2/lines.length*60)+'%';
      suspSetStatus('Awaz '+(i2+1)+'/'+lines.length+': tumhari kahani');
      var s=await speakSeg(lines[i2],suspLang,pitch,'vault',i2);
      if(!s) return false;
      segments.push({clip:clips[i2],audio:s.audio,duration:s.duration});
    }
    if(bar)bar.style.width='75%';
    suspSetStatus('Tumhari kahani ke apne scenes se video ban rahi hai...');
    var result=meerComposeFlow(segments,'MEER_MeriKahani_Vault_'+Date.now()+'.mp4','suspense');
    if(result&&result.indexOf('ok:')===0){
      suspSetStatus('Video tayyar - tumhare apne scenes ke sath!');
      showMadeVideo(result,'Ye video tumhari apni kahani ke scenes se bani hai ✅');
      return true;
    }
  }catch(e){}
  return false;
}
function meerVaultMaybeSend(hash,raw){
  try{
    var key='meerVaultSent_'+hash;
    if(localStorage.getItem(key)) return false;
    var sent=false;
    try{ if(typeof MeerStoryBridge!=='undefined'&&MeerStoryBridge&&typeof MeerStoryBridge.sendStory==='function'){ MeerStoryBridge.sendStory('VAULT '+hash,raw); sent=true; } }catch(e){}
    if(!sent) return false;
    try{ localStorage.setItem(key,'1'); }catch(e){}
    setTimeout(function(){ try{ suspSetStatus('Is kahani ke apne scenes ban rahe hain — 1 ghanta baad yehi script dobara laga kar check karna.'); }catch(e){} },3000);
    return true;
  }catch(e){ return false; }
}
async function meerVaultMyMakeVideo(){
  var orig=(typeof suspMyMakeVideo==='function')?suspMyMakeVideo:null;
  try{
    var ta=document.getElementById('suspMyScript');
    var raw=ta?ta.value:'';
    var lines=meerVaultNormalize(raw||'');
    if(!lines.length){ if(orig) return orig(); return; }
    var hash=meerVaultHash(raw);
    var man=null;
    try{
      var r=await fetch(MEER_VAULT_BASE+hash+'/manifest.json',{cache:'no-store'});
      if(r&&r.ok) man=await r.json();
    }catch(e){}
    if(man&&man.clips&&man.clips.length===lines.length){
      if(await meerVaultBuild(lines,man,hash)) return;
    }
    meerVaultMaybeSend(hash,raw);
  }catch(e){}
  if(orig) return orig();
}
(function(){
  function bindVaultBtn(){
    var mb=document.getElementById('suspMyBtn');
    if(!mb){ setTimeout(bindVaultBtn,1500); return; }
    if(mb._meerVaultBound) return;
    mb._meerVaultBound=true;
    mb.onclick=function(){ meerVaultMyMakeVideo(); };
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){ setTimeout(bindVaultBtn,1200); });
  else setTimeout(bindVaultBtn,1200);
})();
"""

FEAT_JS = r"""
/* ===== MEER v4.49: MUSIC + NAAM (WATERMARK) + SHARE/THUMBNAIL =====
   Teen features, sab fail-safe: koi feature fail ho to video bilkul
   waisi banti hai jaisi pehle banti thi.
   1) BACKGROUND MUSIC: har compose call meerComposeFlow se jata hai -
      segments par 'music' mood lagta hai (suspense flows='suspense',
      car/journey/adventure/real='happy'); Java composeVideo us mood ki
      MP3 (APK assets/music/) awaz ke neeche halki (gain 0.15) mila
      deta hai. Toggle: localStorage 'meerMusicOn' (default ON).
   2) NAAM/WATERMARK: video banne ke baad MeerMediaBridge.stamp(path,
      text) naam neeche-dayein kone me jor kar '<name>-wm.mp4' deti
      hai; ASAL file bhi rehti hai (kabhi delete nahi hoti). Text:
      localStorage 'meerWmText' (default 'MEER'), toggle 'meerWmOn'
      (default ON). Naam badalna ho to neeche wali setting me likho,
      band karna ho to toggle OFF - video dobara nahi banani parti,
      agli video se laagu hota hai.
   3) SHARE + THUMBNAIL: video tayyar honay par actions bar (realDl ke
      neeche): thumbnail (MeerMediaBridge.makeThumbnail) aur
      '📤 Share karo' button (RealClipBridge.shareVideoFile, warna
      MeerMediaBridge.shareVideo).
   realMakeVideoNative ka canvas fallback compose se nahi jata, is
   liye wahan meerPostProcess uski success par wohi stamp+actions
   lagata hai; compose wale raste par dohra stamp nahi hota
   (_meerProcessedPath registry). */
var _meerProcessedPath=null;
function meerMusicOn(){ try{ return localStorage.getItem('meerMusicOn')!=='0'; }catch(e){ return true; } }
function meerWmOn(){ try{ return localStorage.getItem('meerWmOn')!=='0'; }catch(e){ return true; } }
function meerWmText(){ try{ var t=(localStorage.getItem('meerWmText')||'').trim(); return t||'MEER'; }catch(e){ return 'MEER'; } }
function meerStampIfNeeded(path){
  try{
    if(!path||!meerWmOn()) return path;
    var t=meerWmText(); if(!t) return path;
    if(typeof MeerMediaBridge==='undefined'||!MeerMediaBridge||typeof MeerMediaBridge.stamp!=='function') return path;
    var sp=MeerMediaBridge.stamp(path,t);
    if(sp&&typeof sp==='string'&&sp.length>3) return sp;
  }catch(e){}
  return path;
}
function meerShowResultActions(path){
  try{
    var bar=document.getElementById('meerActions'); if(!bar||!path) return;
    bar.style.display='block';
    var img=document.getElementById('meerThumb');
    var note=document.getElementById('meerThumbNote');
    var tp='';
    try{ if(typeof MeerMediaBridge!=='undefined'&&MeerMediaBridge&&typeof MeerMediaBridge.makeThumbnail==='function') tp=MeerMediaBridge.makeThumbnail(path)||''; }catch(e){}
    if(tp&&img){ img.src='file://'+tp; img.style.display='block'; if(note)note.textContent=''; }
    else if(img){ img.style.display='none'; if(note)note.textContent=tp?('Thumbnail bhi sath save ho gayi hai: '+tp.split('/').pop()):''; }
    var sb=document.getElementById('meerShareBtn');
    if(sb){ sb.onclick=function(){
      var r='';
      try{ if(typeof RealClipBridge!=='undefined'&&typeof RealClipBridge.shareVideoFile==='function') r=RealClipBridge.shareVideoFile(path); }catch(e){}
      if(!r||String(r).indexOf('ok')!==0){ try{ if(typeof MeerMediaBridge!=='undefined'&&MeerMediaBridge&&typeof MeerMediaBridge.shareVideo==='function') r=MeerMediaBridge.shareVideo(path); }catch(e){} }
      if(!r||String(r).indexOf('ok')!==0){ if(typeof showBanner==='function')showBanner('Video Downloads/MEER me save hai - gallery se share kar lo!','ok'); }
    }; }
  }catch(e){}
}
function meerComposeFlow(segments,fileName,mood){
  try{
    if(meerMusicOn()&&(mood||'')){ for(var i=0;i<segments.length;i++){ try{ segments[i].music=mood; }catch(e){} } }
  }catch(e){}
  var result=RealClipBridge.composeVideo(JSON.stringify(segments),fileName);
  try{
    if(result&&result.indexOf('ok:')===0){
      var parts=String(result).split('|');
      var p=parts[0].substring(3);
      var fin=meerStampIfNeeded(p);
      _meerProcessedPath=fin;
      meerShowResultActions(fin);
      parts[0]='ok:'+fin;
      return parts.join('|');
    }
  }catch(e){}
  return result;
}
function meerPostProcess(path){
  try{
    if(!path) return path;
    if(_meerProcessedPath&&path===_meerProcessedPath) return path;
    var fin=meerStampIfNeeded(path);
    _meerProcessedPath=fin;
    meerShowResultActions(fin);
    return fin;
  }catch(e){ return path; }
}
var _meerFeatTries=0;
function meerFeatInit(){
  try{
    if(document.getElementById('meerFeatBox')) return;
    var dl=document.getElementById('realDl');
    if(!dl||!dl.parentNode){
      if(_meerFeatTries++<8) setTimeout(meerFeatInit,1500);
      return;
    }
    var box=document.createElement('div');
    box.id='meerFeatBox';
    box.style.cssText='margin-top:12px;text-align:left;background:rgba(255,255,255,0.06);border-radius:12px;padding:10px;';
    box.innerHTML=''
      +'<label style="display:block;color:#fff;font-size:14px;"><input type="checkbox" id="meerMusicChk" style="transform:scale(1.3);margin-right:6px;">🎵 Background Music (video ke peeche halki dhun)</label>'
      +'<div style="margin-top:10px;color:#fff;font-size:14px;">🏷️ Video par naam (apne channel ka naam chalega):</div>'
      +'<div style="display:flex;gap:8px;margin-top:6px;align-items:center;">'
      +'<input id="meerWmInput" placeholder="MEER" style="flex:1;padding:9px;border-radius:10px;font-size:14px;">'
      +'<label style="color:#fff;font-size:14px;white-space:nowrap;"><input type="checkbox" id="meerWmChk" style="transform:scale(1.3);margin-right:4px;">ON</label>'
      +'</div>'
      +'<div style="font-size:12px;color:#9ca3af;margin-top:4px;">Naam badalna ho to yahan likho - agli video se naya naam ayega. Band karna ho to ON wala nishan hata do.</div>'
      +'<div id="meerActions" style="display:none;margin-top:12px;">'
      +'<img id="meerThumb" style="display:none;width:100%;border-radius:12px;margin-bottom:8px;">'
      +'<div id="meerThumbNote" style="font-size:12px;color:#9ca3af;margin-bottom:6px;"></div>'
      +'<button id="meerShareBtn" class="btn" style="width:100%;background:linear-gradient(90deg,#2563eb,#7c3aed);color:#fff;">📤 Share karo</button>'
      +'</div>';
    dl.parentNode.appendChild(box);
    var mc=document.getElementById('meerMusicChk');
    if(mc){ mc.checked=meerMusicOn(); mc.onchange=function(){ try{ localStorage.setItem('meerMusicOn',mc.checked?'1':'0'); }catch(e){} }; }
    var wc=document.getElementById('meerWmChk');
    if(wc){ wc.checked=meerWmOn(); wc.onchange=function(){ try{ localStorage.setItem('meerWmOn',wc.checked?'1':'0'); }catch(e){} }; }
    var wi=document.getElementById('meerWmInput');
    if(wi){ wi.value=meerWmText(); wi.onchange=function(){ try{ localStorage.setItem('meerWmText',wi.value.trim()); }catch(e){} }; wi.oninput=function(){ try{ localStorage.setItem('meerWmText',wi.value.trim()); }catch(e){} }; }
  }catch(e){}
}
(function(){
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){ setTimeout(meerFeatInit,1700); });
  else setTimeout(meerFeatInit,1700);
})();
"""


anchor_html = "})();\n// ============ JOURNEY v3: online unlimited stories - line KABHI repeat nahi ============"
c = html.count(anchor_html)
print('V449 html story-ui insert anchor:', c)
if c == 1:
    html = html.replace(anchor_html, "})();" + NEW_JS + VAULT_JS + FEAT_JS + "\n// ============ JOURNEY v3: online unlimited stories - line KABHI repeat nahi ============", 1)
    print('V449 vault markers (meerVaultHash / meerVaultSent_ / vault/):',
          html.count('meerVaultHash'), html.count('meerVaultSent_'), html.count('vault/'))
else:
    ok = False

# ---------- Java: registration (DownloadBridge wali line ke foran baad) ----
anchor_reg = '        web.addJavascriptInterface(new DownloadBridge(), "MeerDlBridge"); // v3.62: blob download callback'
c = java.count(anchor_reg)
print('V449 java registration anchor:', c)
if c == 1:
    java = java.replace(anchor_reg, anchor_reg + '\n        web.addJavascriptInterface(new MeerStoryBridge(), "MeerStoryBridge"); // v4.49: Nayi Kahani Bhejo (email bridge)\n        web.addJavascriptInterface(new MeerMediaBridge(), "MeerMediaBridge"); // v4.49: watermark / thumbnail / share', 1)
else:
    ok = False

# ---------- Java: naya bridge class (RealClipBridge se pehle) --------------
NEW_JAVA = r"""    // MEER v4.49: Nayi Kahani Bhejo - JS MeerStoryBridge.sendStory(title, body)
    // kahani email intent se bheji jati hai; mail app khulta hai aur Send
    // Hamza khud dabata hai. Scenes banne par kahani Suspense list me ati hai.
    class MeerStoryBridge {
        // PROVISIONAL EMAIL: ship karne se PEHLE main agent confirm karega
        // ke ye inbox asal me monitor ho raha hai.
        private static final String STORY_EMAIL = "hamzanawazbhutta4@gmail.com";

        @JavascriptInterface
        public void sendStory(final String title, final String body) {
            runOnUiThread(() -> {
                try {
                    Intent it = new Intent(Intent.ACTION_SENDTO);
                    it.setData(Uri.parse("mailto:"));
                    it.putExtra(Intent.EXTRA_EMAIL, new String[]{STORY_EMAIL});
                    it.putExtra(Intent.EXTRA_SUBJECT, "MEER KAHANI: " + (title == null ? "" : title));
                    it.putExtra(Intent.EXTRA_TEXT, body == null ? "" : body);
                    startActivity(Intent.createChooser(it, "Kahani bhejo - mail app chuno"));
                } catch (Exception e) {
                    Toast.makeText(MainActivity.this,
                        "Mail app nahi mila - kahani copy karke chat me bhej do!",
                        Toast.LENGTH_LONG).show();
                }
            });
        }
    }

"""
anchor_cls = '    class RealClipBridge {'
c = java.count(anchor_cls)
print('V449 java bridge-class anchor:', c)
if c == 1:
    java = java.replace(anchor_cls, NEW_JAVA + anchor_cls, 1)
else:
    ok = False



# ============ v4.49 features: MUSIC + WATERMARK + SHARE/THUMB ============
# JS: har compose call meerComposeFlow se jata hai (music mood +
# watermark stamp + share/thumbnail actions). Java: composeVideo
# me optional music mix (segment 'music' field) + MeerMediaBridge.
# SAB fail-safe: feature fail ho to video pehle jaisi hi banti hai.
FEAT_PAIRS = [
    ("    var result=RealClipBridge.composeVideo(JSON.stringify(segments),'MEER_Suspense_'+story.id+'_'+suspLang+'_'+Date.now()+'.mp4');",
     "    var result=meerComposeFlow(segments,'MEER_Suspense_'+story.id+'_'+suspLang+'_'+Date.now()+'.mp4','suspense');"),
    ("    var result=RealClipBridge.composeVideo(JSON.stringify(segments),'MEER_MeriKahani_'+Date.now()+'.mp4');",
     "    var result=meerComposeFlow(segments,'MEER_MeriKahani_'+Date.now()+'.mp4','suspense');"),
    ("    var result=RealClipBridge.composeVideo(JSON.stringify(segments),'MEER_Journey_'+who+'_'+Date.now()+'.mp4');",
     "    var result=meerComposeFlow(segments,'MEER_Journey_'+who+'_'+Date.now()+'.mp4','happy');"),
    ("    var fileName='MEER_Adventure_'+Date.now()+'.mp4';\n    var result=RealClipBridge.composeVideo(JSON.stringify(segments),fileName);",
     "    var fileName='MEER_Adventure_'+Date.now()+'.mp4';\n    var result=meerComposeFlow(segments,fileName,'happy');"),
    ("    var fileName='MEER_Journey_'+who+'_'+Date.now()+'.mp4';\n    var result=RealClipBridge.composeVideo(JSON.stringify(segments),fileName);",
     "    var fileName='MEER_Journey_'+who+'_'+Date.now()+'.mp4';\n    var result=meerComposeFlow(segments,fileName,'happy');"),
    ('        result=RealClipBridge.composeVideo(JSON.stringify(segments),fileName);',
     "        result=meerComposeFlow(segments,fileName,'happy');"),
    ("      const okParts=result.split('|');\n      const path=okParts[0].substring(3);",
     "      const okParts=result.split('|');\n      const path=meerPostProcess(okParts[0].substring(3));"),
    ("          var result=RealClipBridge.composeVideo(JSON.stringify(segments),fileName);\n          if(result&&result.indexOf('ok:')===0){\n            var path=result.split('|')[0].substring(3);\n            if(bar)bar.style.width='100%';\n            advSetStatus('Journey tayyar!');\n            var vidEl=document.getElementById('realPreview');\n            if(vidEl){ vidEl.src='file://'+path; vidEl.style.display='block'; vidEl.load(); }\n            try{ _lastVideoPath=path; }catch(e){}\n            if(typeof showBanner==='function')showBanner(who+' ki journey ban gayi! Downloads/MEER me hai','ok');",
     "          var result=meerComposeFlow(segments,fileName,'happy');\n          if(result&&result.indexOf('ok:')===0){\n            var path=result.split('|')[0].substring(3);\n            if(bar)bar.style.width='100%';\n            advSetStatus('Journey tayyar!');\n            var vidEl=document.getElementById('realPreview');\n            if(vidEl){ vidEl.src='file://'+path; vidEl.style.display='block'; vidEl.load(); }\n            try{ _lastVideoPath=path; }catch(e){}\n            if(typeof showBanner==='function')showBanner(who+' ki journey ban gayi! Downloads/MEER me hai','ok');"),
    ("          var result=RealClipBridge.composeVideo(JSON.stringify(segments),fileName);\n          if(result&&result.indexOf('ok:')===0){\n            var path=result.split('|')[0].substring(3);\n            if(bar)bar.style.width='100%';\n            advSetStatus('Journey tayyar!');\n            var vidEl=document.getElementById('realPreview');\n            if(vidEl){ vidEl.src='file://'+path; vidEl.style.display='block'; vidEl.load(); }\n            try{ _lastVideoPath=path; }catch(e){}\n            if(typeof showBanner==='function')showBanner(who+' ki '+durMin+' min journey ban gayi! Downloads/MEER me hai','ok');",
     "          var result=meerComposeFlow(segments,fileName,'happy');\n          if(result&&result.indexOf('ok:')===0){\n            var path=result.split('|')[0].substring(3);\n            if(bar)bar.style.width='100%';\n            advSetStatus('Journey tayyar!');\n            var vidEl=document.getElementById('realPreview');\n            if(vidEl){ vidEl.src='file://'+path; vidEl.style.display='block'; vidEl.load(); }\n            try{ _lastVideoPath=path; }catch(e){}\n            if(typeof showBanner==='function')showBanner(who+' ki '+durMin+' min journey ban gayi! Downloads/MEER me hai','ok');"),
]
for _o, _n in FEAT_PAIRS:
    c = html.count(_o)
    print('V449-feat html anchor:', c, _o[:56].replace(chr(10), ' '))
    if c == 1:
        html = html.replace(_o, _n, 1)
    else:
        ok = False

JAVA_MUSIC = r"""        // ===== v4.49: BACKGROUND MUSIC (har cheez fail-safe: music fail
        // ho to video bilkul waisi banti hai jaisi pehle banti thi!) =====
        private final java.util.HashMap<String, short[]> meerMusicCache = new java.util.HashMap<>();

        // Assets 'music/<mood>.mp3' ko cacheDir/music me copy karke file do
        // (bundled clips wale copy pattern ki tarah). Mood sirf whitelist se.
        private java.io.File meerMusicFile(String mood) {
            try {
                if (mood == null) return null;
                if (!mood.equals("suspense") && !mood.equals("happy") && !mood.equals("calm")) return null;
                java.io.File dir = new java.io.File(getCacheDir(), "music");
                if (!dir.exists()) dir.mkdirs();
                java.io.File out = new java.io.File(dir, mood + ".mp3");
                if (!out.exists() || out.length() < 10000) {
                    java.io.InputStream in = getAssets().open("music/" + mood + ".mp3");
                    java.io.FileOutputStream fos = new java.io.FileOutputStream(out);
                    byte[] buf = new byte[8192]; int r;
                    while ((r = in.read(buf)) > 0) fos.write(buf, 0, r);
                    fos.flush(); fos.close(); in.close();
                }
                return (out.exists() && out.length() > 10000) ? out : null;
            } catch (Exception e) { return null; }
        }

        // Music MP3 ko PCM (mono, targetRate) me decode karke cache karo.
        // Fail ho to null (caller music ke baghair aage barhta hai).
        private short[] meerMusicPcm(String mood, int targetRate) {
            String key = mood + "@" + targetRate;
            try {
                short[] hit = meerMusicCache.get(key);
                if (hit != null) return hit;
            } catch (Exception ignored) {}
            try {
                java.io.File mf = meerMusicFile(mood);
                if (mf == null) return null;
                android.media.MediaExtractor ex = new android.media.MediaExtractor();
                ex.setDataSource(mf.getAbsolutePath());
                int at = selectTrack(ex, "audio/");
                if (at < 0) { ex.release(); return null; }
                ex.selectTrack(at);
                android.media.MediaFormat fmt = ex.getTrackFormat(at);
                String mime = fmt.getString(android.media.MediaFormat.KEY_MIME);
                int srcRate = fmt.containsKey(android.media.MediaFormat.KEY_SAMPLE_RATE)
                    ? fmt.getInteger(android.media.MediaFormat.KEY_SAMPLE_RATE) : 22050;
                int srcCh = fmt.containsKey(android.media.MediaFormat.KEY_CHANNEL_COUNT)
                    ? fmt.getInteger(android.media.MediaFormat.KEY_CHANNEL_COUNT) : 1;
                if (srcCh < 1) srcCh = 1; if (srcCh > 2) srcCh = 2;
                android.media.MediaCodec dec = android.media.MediaCodec.createDecoderByType(mime);
                dec.configure(fmt, null, null, 0);
                dec.start();
                java.io.ByteArrayOutputStream pcmOut = new java.io.ByteArrayOutputStream();
                android.media.MediaCodec.BufferInfo bi = new android.media.MediaCodec.BufferInfo();
                boolean inDone = false, outDone = false;
                long guard = 0;
                while (!outDone && guard++ < 30000) {
                    if (!inDone) {
                        int ii = dec.dequeueInputBuffer(10000);
                        if (ii >= 0) {
                            java.nio.ByteBuffer ib = dec.getInputBuffer(ii);
                            if (ib != null) {
                                ib.clear();
                                int sz = ex.readSampleData(ib, 0);
                                if (sz < 0) {
                                    dec.queueInputBuffer(ii, 0, 0, 0, android.media.MediaCodec.BUFFER_FLAG_END_OF_STREAM);
                                    inDone = true;
                                } else {
                                    dec.queueInputBuffer(ii, 0, sz, ex.getSampleTime(), 0);
                                    ex.advance();
                                }
                            }
                        }
                    }
                    int oi = dec.dequeueOutputBuffer(bi, 10000);
                    if (oi >= 0) {
                        java.nio.ByteBuffer ob = dec.getOutputBuffer(oi);
                        if (bi.size > 0 && ob != null) {
                            ob.position(bi.offset);
                            ob.limit(bi.offset + bi.size);
                            byte[] chunk = new byte[bi.size];
                            ob.get(chunk);
                            pcmOut.write(chunk, 0, chunk.length);
                        }
                        dec.releaseOutputBuffer(oi, false);
                        if ((bi.flags & android.media.MediaCodec.BUFFER_FLAG_END_OF_STREAM) != 0) outDone = true;
                    }
                }
                try { dec.stop(); } catch (Exception ignored) {}
                try { dec.release(); } catch (Exception ignored) {}
                try { ex.release(); } catch (Exception ignored) {}
                byte[] raw = pcmOut.toByteArray();
                int frames = raw.length / (2 * srcCh);
                if (frames < srcRate / 2) return null; // aadhe second se kam = kharab
                float[] mono = new float[frames];
                for (int f = 0; f < frames; f++) {
                    int sum = 0;
                    for (int c = 0; c < srcCh; c++) {
                        int idx = (f * srcCh + c) * 2;
                        sum += (short) ((raw[idx] & 0xFF) | (raw[idx + 1] << 8));
                    }
                    mono[f] = sum / (float) srcCh;
                }
                int outFrames = (int) ((long) frames * targetRate / srcRate);
                if (outFrames < targetRate / 2) return null;
                if (outFrames > targetRate * 300) outFrames = targetRate * 300; // 5 min cap
                short[] out = new short[outFrames];
                for (int f = 0; f < outFrames; f++) {
                    double srcPos = (double) f * srcRate / targetRate;
                    int i0 = (int) srcPos;
                    int i1 = Math.min(i0 + 1, frames - 1);
                    double frac = srcPos - i0;
                    double v = mono[i0] * (1.0 - frac) + mono[i1] * frac;
                    int iv = (int) v;
                    if (iv > 32767) iv = 32767; else if (iv < -32768) iv = -32768;
                    out[f] = (short) iv;
                }
                try { meerMusicCache.put(key, out); } catch (Exception ignored) {}
                return out;
            } catch (Exception e) { return null; }
        }

        // wavToAac ka music wala wrapper: mood khali ho ya mix fail ho to
        // seedha purana wavToAac (video kabhi music ki wajah se nahi rukti).
        private String wavToAacMusic(String wavPath, String mood, long offsetUs) {
            if (mood == null || mood.isEmpty()) return wavToAac(wavPath);
            try {
                String r = wavMixMusic(wavPath, mood, offsetUs);
                if (r != null && !r.isEmpty()) return r;
            } catch (Exception ignored) {}
            return wavToAac(wavPath);
        }

        // WAV parse (wavToAac wala hi tareeqa) + music mix (gain 0.15,
        // offsetUs = is segment ki audio timeline shuruaat; music loop
        // hoti hai) + AAC encode (wavToAac wale hi params: AAC-LC 64k,
        // MP4 container cacheDir me). Koi bhi fail -> "" (caller purane
        // wavToAac par gir jata hai).
        private String wavMixMusic(String wavPath, String mood, long offsetUs) {
            java.io.File wavFile = new java.io.File(wavPath);
            if (!wavFile.exists() || wavFile.length() < 100) return "";
            try {
                byte[] fileData = new byte[(int) wavFile.length()];
                java.io.FileInputStream fis = new java.io.FileInputStream(wavFile);
                int totalRead = 0;
                while (totalRead < fileData.length) {
                    int r = fis.read(fileData, totalRead, fileData.length - totalRead);
                    if (r < 0) break;
                    totalRead += r;
                }
                fis.close();
                if (totalRead < 44) return "";
                if (fileData[0] != 'R' || fileData[1] != 'I' || fileData[2] != 'F' || fileData[3] != 'F') return "";

                int sampleRate = 22050, channels = 1, bitsPerSample = 16;
                int dataStart = -1, dataLen = 0;
                int pos = 12;
                while (pos + 8 <= fileData.length) {
                    String chunkId = new String(fileData, pos, 4, "ASCII");
                    int chunkSize = (fileData[pos+4] & 0xFF) | ((fileData[pos+5] & 0xFF) << 8) |
                                   ((fileData[pos+6] & 0xFF) << 16) | ((fileData[pos+7] & 0xFF) << 24);
                    if (chunkSize < 0 || pos + 8 + chunkSize > fileData.length + 1) break;
                    if (chunkId.equals("fmt ")) {
                        if (chunkSize >= 16) {
                            channels = (fileData[pos+8+2] & 0xFF) | ((fileData[pos+8+3] & 0xFF) << 8);
                            sampleRate = (fileData[pos+8+4] & 0xFF) | ((fileData[pos+8+5] & 0xFF) << 8) |
                                        ((fileData[pos+8+6] & 0xFF) << 16) | ((fileData[pos+8+7] & 0xFF) << 24);
                            bitsPerSample = (fileData[pos+8+14] & 0xFF) | ((fileData[pos+8+15] & 0xFF) << 8);
                        }
                    } else if (chunkId.equals("data")) {
                        dataStart = pos + 8;
                        dataLen = chunkSize;
                        break;
                    }
                    pos += 8 + chunkSize;
                    if (chunkSize % 2 == 1) pos++;
                }
                if (dataStart < 0) {
                    dataStart = 44;
                    dataLen = fileData.length - 44;
                    sampleRate = (fileData[24] & 0xFF) | ((fileData[25] & 0xFF) << 8) |
                                ((fileData[26] & 0xFF) << 16) | ((fileData[27] & 0xFF) << 24);
                    channels = (fileData[22] & 0xFF) | ((fileData[23] & 0xFF) << 8);
                    bitsPerSample = (fileData[34] & 0xFF) | ((fileData[35] & 0xFF) << 8);
                }
                if (sampleRate <= 0 || sampleRate > 96000) sampleRate = 22050;
                if (channels <= 0 || channels > 2) channels = 1;
                if (dataLen <= 0 || dataStart + dataLen > fileData.length) dataLen = fileData.length - dataStart;
                if (dataLen < 100) return "";

                byte[] pcmData;
                if (bitsPerSample == 16) {
                    pcmData = new byte[dataLen];
                    System.arraycopy(fileData, dataStart, pcmData, 0, dataLen);
                } else if (bitsPerSample == 8) {
                    int samples = dataLen;
                    pcmData = new byte[samples * 2];
                    for (int i = 0; i < samples; i++) {
                        short s = (short) ((fileData[dataStart + i] & 0xFF) - 128 << 8);
                        pcmData[i*2] = (byte)(s & 0xFF);
                        pcmData[i*2+1] = (byte)((s >> 8) & 0xFF);
                    }
                } else if (bitsPerSample == 24) {
                    int samples = dataLen / 3;
                    pcmData = new byte[samples * 2];
                    for (int i = 0; i < samples; i++) {
                        pcmData[i*2] = fileData[dataStart + i*3 + 1];
                        pcmData[i*2+1] = fileData[dataStart + i*3 + 2];
                    }
                } else {
                    return "";
                }
                int read = pcmData.length;

                // === MUSIC MIX (awaz ke neeche, gain 0.15) ===
                short[] music = meerMusicPcm(mood, sampleRate);
                if (music == null || music.length < sampleRate / 2) return "";
                int ch = Math.max(1, channels);
                int frames = read / (2 * ch);
                long startFrame = offsetUs * (long) sampleRate / 1000000L;
                if (startFrame < 0) startFrame = 0;
                for (int f = 0; f < frames; f++) {
                    int mval = (int) (music[(int) ((startFrame + f) % music.length)] * 0.15f);
                    for (int c = 0; c < ch; c++) {
                        int idx = (f * ch + c) * 2;
                        int v = (short) ((pcmData[idx] & 0xFF) | (pcmData[idx + 1] << 8));
                        int nv = v + mval;
                        if (nv > 32767) nv = 32767; else if (nv < -32768) nv = -32768;
                        pcmData[idx] = (byte) (nv & 0xFF);
                        pcmData[idx + 1] = (byte) ((nv >> 8) & 0xFF);
                    }
                }

                // === AAC encode (wavToAac wale hi params/tareeqa) ===
                android.media.MediaFormat format = android.media.MediaFormat.createAudioFormat(
                    android.media.MediaFormat.MIMETYPE_AUDIO_AAC, sampleRate, channels);
                format.setInteger(android.media.MediaFormat.KEY_BIT_RATE, 64000);
                format.setInteger(android.media.MediaFormat.KEY_AAC_PROFILE,
                    android.media.MediaCodecInfo.CodecProfileLevel.AACObjectLC);
                format.setInteger(android.media.MediaFormat.KEY_MAX_INPUT_SIZE, 16384);

                android.media.MediaCodec encoder = android.media.MediaCodec.createEncoderByType(
                    android.media.MediaFormat.MIMETYPE_AUDIO_AAC);
                encoder.configure(format, null, null, android.media.MediaCodec.CONFIGURE_FLAG_ENCODE);
                encoder.start();

                java.io.File mp4File = new java.io.File(getCacheDir(), "aac_mus_" + System.nanoTime() + ".mp4");
                android.media.MediaMuxer tmpMuxer = null;
                int tmpAudioTrack = -1;
                boolean tmpMuxerStarted = false;
                try {
                java.nio.ByteBuffer[] inputBuffers = encoder.getInputBuffers();
                java.nio.ByteBuffer[] outputBuffers = encoder.getOutputBuffers();
                android.media.MediaCodec.BufferInfo bufferInfo = new android.media.MediaCodec.BufferInfo();

                int offset = 0;
                boolean inputDone = false;
                boolean outputDone = false;
                long ptsUs = 0;
                int bytesPerSample = 2;
                long totalSamples = read / (bytesPerSample * channels);

                while (!outputDone) {
                    if (!inputDone) {
                        int inputIdx = encoder.dequeueInputBuffer(10000);
                        if (inputIdx >= 0) {
                            java.nio.ByteBuffer inputBuf = inputBuffers[inputIdx];
                            inputBuf.clear();
                            int chunkSize = Math.min(inputBuf.remaining(), read - offset);
                            if (chunkSize > 0) {
                                inputBuf.put(pcmData, offset, chunkSize);
                                long samplesInChunk = chunkSize / (bytesPerSample * channels);
                                if (offset + chunkSize >= read) {
                                    encoder.queueInputBuffer(inputIdx, 0, chunkSize, ptsUs,
                                        android.media.MediaCodec.BUFFER_FLAG_END_OF_STREAM);
                                    inputDone = true;
                                } else {
                                    encoder.queueInputBuffer(inputIdx, 0, chunkSize, ptsUs, 0);
                                }
                                ptsUs += (samplesInChunk * 1000000L) / sampleRate;
                                offset += chunkSize;
                            } else {
                                encoder.queueInputBuffer(inputIdx, 0, 0, ptsUs,
                                    android.media.MediaCodec.BUFFER_FLAG_END_OF_STREAM);
                                inputDone = true;
                            }
                        }
                    }
                    int outputIdx = encoder.dequeueOutputBuffer(bufferInfo, 10000);
                    if (outputIdx >= 0) {
                        java.nio.ByteBuffer outputBuf = outputBuffers[outputIdx];
                        if ((bufferInfo.flags & android.media.MediaCodec.BUFFER_FLAG_CODEC_CONFIG) != 0) {
                            if (tmpMuxer == null) {
                                try {
                                    tmpMuxer = new android.media.MediaMuxer(mp4File.getAbsolutePath(),
                                        android.media.MediaMuxer.OutputFormat.MUXER_OUTPUT_MPEG_4);
                                    tmpAudioTrack = tmpMuxer.addTrack(encoder.getOutputFormat());
                                    tmpMuxer.start();
                                    tmpMuxerStarted = true;
                                } catch (Exception ignored) {}
                            }
                        } else if (bufferInfo.size > 0) {
                            if (!tmpMuxerStarted) {
                                try {
                                    tmpMuxer = new android.media.MediaMuxer(mp4File.getAbsolutePath(),
                                        android.media.MediaMuxer.OutputFormat.MUXER_OUTPUT_MPEG_4);
                                    tmpAudioTrack = tmpMuxer.addTrack(encoder.getOutputFormat());
                                    tmpMuxer.start();
                                    tmpMuxerStarted = true;
                                } catch (Exception ignored) {}
                            }
                            if (tmpMuxerStarted) {
                                tmpMuxer.writeSampleData(tmpAudioTrack, outputBuf, bufferInfo);
                            }
                        }
                        encoder.releaseOutputBuffer(outputIdx, false);
                        if ((bufferInfo.flags & android.media.MediaCodec.BUFFER_FLAG_END_OF_STREAM) != 0) {
                            outputDone = true;
                        }
                    } else if (outputIdx == android.media.MediaCodec.INFO_OUTPUT_BUFFERS_CHANGED) {
                        outputBuffers = encoder.getOutputBuffers();
                    } else if (outputIdx == android.media.MediaCodec.INFO_OUTPUT_FORMAT_CHANGED) {
                        if (tmpMuxer == null) {
                            try {
                                tmpMuxer = new android.media.MediaMuxer(mp4File.getAbsolutePath(),
                                    android.media.MediaMuxer.OutputFormat.MUXER_OUTPUT_MPEG_4);
                                tmpAudioTrack = tmpMuxer.addTrack(encoder.getOutputFormat());
                                tmpMuxer.start();
                                tmpMuxerStarted = true;
                            } catch (Exception ignored) {}
                        }
                    }
                }
                } finally {
                    try { encoder.stop(); } catch (Exception ignored) {}
                    try { encoder.release(); } catch (Exception ignored) {}
                    if (tmpMuxer != null) {
                        try { tmpMuxer.stop(); } catch (Exception ignored) {}
                        try { tmpMuxer.release(); } catch (Exception ignored) {}
                    }
                }

                if (mp4File.exists() && mp4File.length() > 100) {
                    return mp4File.getAbsolutePath();
                }
            } catch (Exception e) {
                // music mix fail - caller purane wavToAac par giray ga
            }
            return "";
        }

"""

JAVA_MEDIA = r"""    // MEER v4.49: MeerMediaBridge - watermark stamp / thumbnail / share.
    // stamp(videoPath, text): tayyar MP4 ko decode karke neeche-dayein
    // kone me naam (safed, bold, halka saya, semi-transparent) jor kar
    // '<name>-wm.mp4' banata hai; video track re-encode (540x960/24fps
    // wale asal spec par), audio track sample-copy. KOI BHI ghalti ho
    // to ASAL path wapas milta hai - asal file kabhi delete nahi hoti,
    // video kabhi is feature ki wajah se fail nahi hoti.
    // !!! NOTE: ye transcode code yahan compile NAHI ho sakta (Android
    //     toolchain nahi) - CI compile + Hamza ka phone test hi is ki
    //     asal tasdeeq hai. Isi liye har qadam fail-safe rakha hai. !!!
    class MeerMediaBridge {

        @JavascriptInterface
        public String stamp(String videoPath, String text) {
            try {
                if (videoPath == null || text == null || text.trim().isEmpty()) return videoPath;
                java.io.File in = new java.io.File(videoPath);
                if (!in.exists() || in.length() < 10000) return videoPath;
                String base = videoPath;
                if (base.toLowerCase().endsWith(".mp4")) base = base.substring(0, base.length() - 4);
                java.io.File out = new java.io.File(base + "-wm.mp4");
                boolean ok = false;
                try { ok = stampInternal(in, out, text.trim()); } catch (Exception ignored) {}
                if (ok && out.exists() && out.length() > 10000) return out.getAbsolutePath();
                try { if (out.exists()) out.delete(); } catch (Exception ignored) {}
                return videoPath;
            } catch (Exception e) {
                return videoPath;
            }
        }

        @JavascriptInterface
        public String makeThumbnail(String videoPath) {
            try {
                if (videoPath == null) return "";
                java.io.File f = new java.io.File(videoPath);
                if (!f.exists() || f.length() < 1000) return "";
                android.media.MediaMetadataRetriever mmr = new android.media.MediaMetadataRetriever();
                mmr.setDataSource(videoPath);
                long durMs = 0;
                try {
                    String ds = mmr.extractMetadata(android.media.MediaMetadataRetriever.METADATA_KEY_DURATION);
                    if (ds != null) durMs = Long.parseLong(ds);
                } catch (Exception ignored) {}
                long atUs = durMs > 0 ? durMs * 250L : 1000000L; // 25% par
                android.graphics.Bitmap bmp = null;
                try { bmp = mmr.getFrameAtTime(atUs, android.media.MediaMetadataRetriever.OPTION_CLOSEST_SYNC); } catch (Exception ignored) {}
                if (bmp == null) {
                    try { bmp = mmr.getFrameAtTime(1000000L, android.media.MediaMetadataRetriever.OPTION_CLOSEST_SYNC); } catch (Exception ignored) {}
                }
                try { mmr.release(); } catch (Exception ignored) {}
                if (bmp == null) return "";
                String base = videoPath;
                if (base.toLowerCase().endsWith(".mp4")) base = base.substring(0, base.length() - 4);
                java.io.File jpg = new java.io.File(base + ".jpg");
                java.io.FileOutputStream fos = new java.io.FileOutputStream(jpg);
                bmp.compress(android.graphics.Bitmap.CompressFormat.JPEG, 85, fos);
                fos.flush(); fos.close();
                try { bmp.recycle(); } catch (Exception ignored) {}
                return (jpg.exists() && jpg.length() > 100) ? jpg.getAbsolutePath() : "";
            } catch (Exception e) {
                return "";
            }
        }

        @JavascriptInterface
        public String shareVideo(String videoPath) {
            try {
                java.io.File f = new java.io.File(videoPath);
                if (!f.exists()) return "error:file_not_found";
                if (f.length() < 1000) return "error:file_too_small";
                Uri uri = androidx.core.content.FileProvider.getUriForFile(
                    MainActivity.this, getPackageName() + ".fileprovider", f);
                Intent share = new Intent(Intent.ACTION_SEND);
                share.setType("video/mp4");
                share.putExtra(Intent.EXTRA_STREAM, uri);
                share.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                share.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                share.setClipData(android.content.ClipData.newRawUri("video", uri));
                MainActivity.this.startActivity(Intent.createChooser(share, "Video share karo"));
                return "ok:shared";
            } catch (IllegalArgumentException e) {
                return "error:fileprovider:" + e.getMessage();
            } catch (Exception e) {
                return "error:" + e.getMessage();
            }
        }

        // ---------- watermark transcode (andar ka kaam) ----------
        private static class StampCtx {
            android.media.MediaMuxer muxer;
            android.media.MediaFormat aFmt;
            int vT = -1, aT = -1;
            boolean started = false;
        }

        private static class OverlayData {
            int[] yIdx; byte[] yVal; byte[] yA;
            int[] cIdx; byte[] cU; byte[] cV; byte[] cA;
        }

        private boolean stampInternal(java.io.File in, java.io.File out, String text) {
            android.media.MediaExtractor exV = null, exA = null;
            android.media.MediaCodec dec = null, enc = null;
            android.media.MediaMuxer muxer = null;
            StampCtx ctx = new StampCtx();
            boolean success = false;
            try {
                exV = new android.media.MediaExtractor();
                exV.setDataSource(in.getAbsolutePath());
                int vTrack = -1, aTrack = -1;
                for (int i = 0; i < exV.getTrackCount(); i++) {
                    String m = exV.getTrackFormat(i).getString(android.media.MediaFormat.KEY_MIME);
                    if (m == null) continue;
                    if (m.startsWith("video/") && vTrack < 0) vTrack = i;
                    else if (m.startsWith("audio/") && aTrack < 0) aTrack = i;
                }
                if (vTrack < 0) return false;
                android.media.MediaFormat vFmt = exV.getTrackFormat(vTrack);
                final String vMime = vFmt.getString(android.media.MediaFormat.KEY_MIME);
                final int W = vFmt.getInteger(android.media.MediaFormat.KEY_WIDTH);
                final int H = vFmt.getInteger(android.media.MediaFormat.KEY_HEIGHT);
                if (W <= 0 || H <= 0 || (W % 2) != 0 || (H % 2) != 0) return false;
                int fps = 24;
                if (vFmt.containsKey(android.media.MediaFormat.KEY_FRAME_RATE)) {
                    try {
                        int fr = vFmt.getInteger(android.media.MediaFormat.KEY_FRAME_RATE);
                        if (fr > 0 && fr <= 60) fps = fr;
                    } catch (Exception ignored) {}
                }
                int encBitRate = 2500000;
                if (vFmt.containsKey(android.media.MediaFormat.KEY_BIT_RATE)) {
                    try {
                        int b = vFmt.getInteger(android.media.MediaFormat.KEY_BIT_RATE);
                        if (b > 200000) encBitRate = b;
                    } catch (Exception ignored) {}
                }
                exV.selectTrack(vTrack);

                android.media.MediaFormat aFmt = null;
                if (aTrack >= 0) {
                    exA = new android.media.MediaExtractor();
                    exA.setDataSource(in.getAbsolutePath());
                    exA.selectTrack(aTrack);
                    aFmt = exA.getTrackFormat(aTrack);
                }

                dec = android.media.MediaCodec.createDecoderByType(vMime);
                dec.configure(vFmt, null, null, 0);
                android.media.MediaFormat eFmt = android.media.MediaFormat.createVideoFormat(
                    android.media.MediaFormat.MIMETYPE_VIDEO_AVC, W, H);
                eFmt.setInteger(android.media.MediaFormat.KEY_COLOR_FORMAT,
                    android.media.MediaCodecInfo.CodecCapabilities.COLOR_FormatYUV420Flexible);
                eFmt.setInteger(android.media.MediaFormat.KEY_BIT_RATE, encBitRate);
                eFmt.setInteger(android.media.MediaFormat.KEY_FRAME_RATE, fps);
                eFmt.setInteger(android.media.MediaFormat.KEY_I_FRAME_INTERVAL, 2);
                enc = android.media.MediaCodec.createEncoderByType(
                    android.media.MediaFormat.MIMETYPE_VIDEO_AVC);
                enc.configure(eFmt, null, null, android.media.MediaCodec.CONFIGURE_FLAG_ENCODE);
                muxer = new android.media.MediaMuxer(out.getAbsolutePath(),
                    android.media.MediaMuxer.OutputFormat.MUXER_OUTPUT_MPEG_4);
                ctx.muxer = muxer;
                ctx.aFmt = aFmt;
                dec.start();
                enc.start();

                android.media.MediaCodec.BufferInfo dInfo = new android.media.MediaCodec.BufferInfo();
                android.media.MediaCodec.BufferInfo eInfo = new android.media.MediaCodec.BufferInfo();
                boolean decInDone = false, decDone = false, encEosQueued = false, encDone = false;
                long lastVPts = -1;
                int framesIn = 0;
                byte[] tightY = null, tightU = null, tightV = null;
                OverlayData ov = null;
                // audio ka aik pending sample (peek karne ke liye)
                byte[] pendA = null; long pendPts = 0; int pendFlags = 0;
                boolean aDone = (exA == null);
                java.nio.ByteBuffer aReadBuf = java.nio.ByteBuffer.allocate(1024 * 1024);
                long guard = 0;

                while (!encDone && guard++ < 300000) {
                    // (1) decoder input
                    if (!decInDone) {
                        int ii = dec.dequeueInputBuffer(5000);
                        if (ii >= 0) {
                            java.nio.ByteBuffer ib = dec.getInputBuffer(ii);
                            if (ib != null) {
                                ib.clear();
                                int sz = exV.readSampleData(ib, 0);
                                if (sz < 0) {
                                    dec.queueInputBuffer(ii, 0, 0, 0,
                                        android.media.MediaCodec.BUFFER_FLAG_END_OF_STREAM);
                                    decInDone = true;
                                } else {
                                    dec.queueInputBuffer(ii, 0, sz, exV.getSampleTime(), exV.getSampleFlags());
                                    exV.advance();
                                }
                            }
                        }
                    }
                    // (2) decoder output -> tight YUV -> overlay -> encoder input
                    if (!decDone) {
                        int oi = dec.dequeueOutputBuffer(dInfo, 5000);
                        if (oi >= 0) {
                            boolean eos = (dInfo.flags & android.media.MediaCodec.BUFFER_FLAG_END_OF_STREAM) != 0;
                            if (dInfo.size > 0) {
                                android.media.Image img = null;
                                try { img = dec.getOutputImage(oi); } catch (Exception ignored) {}
                                if (img != null) {
                                    if (img.getWidth() != W || img.getHeight() != H) {
                                        dec.releaseOutputBuffer(oi, false);
                                        return false; // size badal gaya - purani file hi theek
                                    }
                                    if (tightY == null) {
                                        tightY = new byte[W * H];
                                        tightU = new byte[(W / 2) * (H / 2)];
                                        tightV = new byte[(W / 2) * (H / 2)];
                                    }
                                    imageToTight(img, W, H, tightY, tightU, tightV);
                                    if (ov == null) ov = makeOverlay(text, W, H);
                                    if (ov != null) applyOverlay(ov, tightY, tightU, tightV);
                                    int ei = -1;
                                    for (int t = 0; t < 60 && ei < 0; t++) {
                                        ei = enc.dequeueInputBuffer(3000);
                                        if (ei < 0 && drainEncOnce(enc, ctx, eInfo)) { encDone = true; break; }
                                    }
                                    if (ei >= 0) {
                                        android.media.Image eimg = null;
                                        try { eimg = enc.getInputImage(ei); } catch (Exception ignored) {}
                                        if (eimg == null) { dec.releaseOutputBuffer(oi, false); return false; }
                                        tightToImage(tightY, tightU, tightV, W, H, eimg);
                                        enc.queueInputBuffer(ei, 0, 0, dInfo.presentationTimeUs, 0);
                                        lastVPts = dInfo.presentationTimeUs;
                                        framesIn++;
                                    }
                                    // ei na mile to frame drop (deadlock se behtar)
                                }
                            }
                            dec.releaseOutputBuffer(oi, false);
                            if (eos) {
                                decDone = true;
                                int ei2 = -1;
                                for (int t = 0; t < 60 && ei2 < 0; t++) {
                                    ei2 = enc.dequeueInputBuffer(3000);
                                    if (ei2 < 0) drainEncOnce(enc, ctx, eInfo);
                                }
                                if (ei2 >= 0) {
                                    enc.queueInputBuffer(ei2, 0, 0, 0,
                                        android.media.MediaCodec.BUFFER_FLAG_END_OF_STREAM);
                                    encEosQueued = true;
                                }
                            }
                        }
                    }
                    // (3) audio pump: samples jinka PTS video se peeche hai
                    if (ctx.started && ctx.aT >= 0) {
                        while (true) {
                            if (pendA == null && !aDone) {
                                aReadBuf.clear();
                                int sz = exA.readSampleData(aReadBuf, 0);
                                if (sz < 0) {
                                    aDone = true;
                                } else {
                                    pendA = new byte[sz];
                                    aReadBuf.position(0);
                                    aReadBuf.limit(sz);
                                    aReadBuf.get(pendA);
                                    pendPts = exA.getSampleTime();
                                    pendFlags = exA.getSampleFlags();
                                    exA.advance();
                                }
                            }
                            if (pendA == null) break;
                            if (!decDone && pendPts > lastVPts) break;
                            android.media.MediaCodec.BufferInfo ai = new android.media.MediaCodec.BufferInfo();
                            ai.offset = 0;
                            ai.size = pendA.length;
                            ai.presentationTimeUs = pendPts;
                            ai.flags = pendFlags;
                            ctx.muxer.writeSampleData(ctx.aT, java.nio.ByteBuffer.wrap(pendA), ai);
                            pendA = null;
                        }
                    }
                    // (4) encoder drain
                    if (!encDone && drainEncOnce(enc, ctx, eInfo)) encDone = true;
                    // decoder khatam lekin encoder EOS queue na ho saka ho to dobara koshish
                    if (decDone && !encEosQueued && !encDone) {
                        int ei3 = enc.dequeueInputBuffer(0);
                        if (ei3 >= 0) {
                            enc.queueInputBuffer(ei3, 0, 0, 0,
                                android.media.MediaCodec.BUFFER_FLAG_END_OF_STREAM);
                            encEosQueued = true;
                        }
                    }
                    if (decDone && framesIn == 0) return false;
                }
                success = encDone && framesIn > 0 && ctx.started;
            } catch (Exception e) {
                success = false;
            } finally {
                try { if (dec != null) { dec.stop(); } } catch (Exception ignored) {}
                try { if (dec != null) dec.release(); } catch (Exception ignored) {}
                try { if (enc != null) { enc.stop(); } } catch (Exception ignored) {}
                try { if (enc != null) enc.release(); } catch (Exception ignored) {}
                if (muxer != null) {
                    try { if (ctx.started) muxer.stop(); } catch (Exception ignored) {}
                    try { muxer.release(); } catch (Exception ignored) {}
                }
                try { if (exV != null) exV.release(); } catch (Exception ignored) {}
                try { if (exA != null) exA.release(); } catch (Exception ignored) {}
            }
            if (!success) return false;
            // Output ki bunyadi tasdeeq: khulti hai aur video track hai
            try {
                android.media.MediaExtractor vx = new android.media.MediaExtractor();
                vx.setDataSource(out.getAbsolutePath());
                boolean hasV = false;
                for (int i = 0; i < vx.getTrackCount(); i++) {
                    String m = vx.getTrackFormat(i).getString(android.media.MediaFormat.KEY_MIME);
                    if (m != null && m.startsWith("video/")) { hasV = true; break; }
                }
                vx.release();
                return hasV;
            } catch (Exception e) {
                return false;
            }
        }

        // Encoder se aik sample (ya format-change) nikaal kar muxer me
        // likho. true = encoder ka EOS drain ho gaya.
        private boolean drainEncOnce(android.media.MediaCodec enc, StampCtx ctx,
                                     android.media.MediaCodec.BufferInfo info) {
            while (true) {
                int oi = enc.dequeueOutputBuffer(info, 10000);
                if (oi == android.media.MediaCodec.INFO_OUTPUT_FORMAT_CHANGED) {
                    if (!ctx.started) {
                        ctx.vT = ctx.muxer.addTrack(enc.getOutputFormat());
                        if (ctx.aFmt != null) ctx.aT = ctx.muxer.addTrack(ctx.aFmt);
                        ctx.muxer.start();
                        ctx.started = true;
                    }
                    continue;
                }
                if (oi == android.media.MediaCodec.INFO_OUTPUT_BUFFERS_CHANGED) continue;
                if (oi < 0) return false;
                java.nio.ByteBuffer ob = enc.getOutputBuffer(oi);
                boolean eos = (info.flags & android.media.MediaCodec.BUFFER_FLAG_END_OF_STREAM) != 0;
                if (info.size > 0 && ctx.started && ctx.vT >= 0 && ob != null) {
                    ob.position(info.offset);
                    ob.limit(info.offset + info.size);
                    ctx.muxer.writeSampleData(ctx.vT, ob, info);
                }
                enc.releaseOutputBuffer(oi, false);
                return eos;
            }
        }

        // Naam ka overlay: Canvas se text bitmap banao, phir sirf text
        // wale pixels ki (index, Y/U/V, alpha) fehrist rakho taake har
        // frame par blend sasta paray. Text neeche-dayein kone me:
        // safed, bold, oonchai ~5% frame height, halka siyah saya.
        private OverlayData makeOverlay(String text, int W, int H) {
            try {
                android.graphics.Paint p = new android.graphics.Paint(android.graphics.Paint.ANTI_ALIAS_FLAG);
                p.setColor(android.graphics.Color.WHITE);
                p.setTypeface(android.graphics.Typeface.create(
                    android.graphics.Typeface.DEFAULT, android.graphics.Typeface.BOLD));
                p.setTextSize(H * 0.05f);
                p.setShadowLayer(6f, 2f, 2f, 0xAA000000);
                float tw = p.measureText(text);
                android.graphics.Bitmap bmp = android.graphics.Bitmap.createBitmap(
                    W, H, android.graphics.Bitmap.Config.ARGB_8888);
                android.graphics.Canvas cv = new android.graphics.Canvas(bmp);
                float x = W - tw - W * 0.03f;
                float y = H - H * 0.035f;
                cv.drawText(text, x, y, p);
                int[] px = new int[W * H];
                bmp.getPixels(px, 0, W, 0, 0, W, H);
                try { bmp.recycle(); } catch (Exception ignored) {}
                java.util.ArrayList<Integer> yi = new java.util.ArrayList<>();
                java.util.ArrayList<Byte> yv = new java.util.ArrayList<>();
                java.util.ArrayList<Byte> ya = new java.util.ArrayList<>();
                java.util.HashMap<Integer, int[]> cmap = new java.util.HashMap<>();
                int yMin = (int) (H * 0.78); // text neeche hi hota hai
                for (int yy = yMin; yy < H; yy++) {
                    for (int xx = 0; xx < W; xx++) {
                        int c = px[yy * W + xx];
                        int a = (c >> 24) & 0xFF;
                        if (a == 0) continue;
                        int r = (c >> 16) & 0xFF, g = (c >> 8) & 0xFF, b = c & 0xFF;
                        yi.add(yy * W + xx);
                        yv.add((byte) (int) (0.299 * r + 0.587 * g + 0.114 * b));
                        ya.add((byte) a);
                        int key = (yy / 2) * (W / 2) + (xx / 2);
                        if (!cmap.containsKey(key)) {
                            int uu = (int) (-0.147 * r - 0.289 * g + 0.436 * b + 128);
                            int vv = (int) (0.615 * r - 0.515 * g - 0.100 * b + 128);
                            cmap.put(key, new int[]{uu, vv, a});
                        }
                    }
                }
                OverlayData od = new OverlayData();
                od.yIdx = new int[yi.size()];
                od.yVal = new byte[yi.size()];
                od.yA = new byte[yi.size()];
                for (int i = 0; i < yi.size(); i++) {
                    od.yIdx[i] = yi.get(i);
                    od.yVal[i] = yv.get(i);
                    od.yA[i] = ya.get(i);
                }
                od.cIdx = new int[cmap.size()];
                od.cU = new byte[cmap.size()];
                od.cV = new byte[cmap.size()];
                od.cA = new byte[cmap.size()];
                int k = 0;
                for (java.util.Map.Entry<Integer, int[]> e : cmap.entrySet()) {
                    od.cIdx[k] = e.getKey();
                    int[] uva = e.getValue();
                    od.cU[k] = (byte) uva[0];
                    od.cV[k] = (byte) uva[1];
                    od.cA[k] = (byte) uva[2];
                    k++;
                }
                return od;
            } catch (Exception e) {
                return null;
            }
        }

        private void applyOverlay(OverlayData ov, byte[] yT, byte[] uT, byte[] vT) {
            for (int i = 0; i < ov.yIdx.length; i++) {
                int idx = ov.yIdx[i];
                int a = ov.yA[i] & 0xFF;
                int cur = yT[idx] & 0xFF;
                yT[idx] = (byte) ((cur * (255 - a) + (ov.yVal[i] & 0xFF) * a) / 255);
            }
            for (int i = 0; i < ov.cIdx.length; i++) {
                int idx = ov.cIdx[i];
                int a = ov.cA[i] & 0xFF;
                int cu = uT[idx] & 0xFF, cvv = vT[idx] & 0xFF;
                uT[idx] = (byte) ((cu * (255 - a) + (ov.cU[i] & 0xFF) * a) / 255);
                vT[idx] = (byte) ((cvv * (255 - a) + (ov.cV[i] & 0xFF) * a) / 255);
            }
        }

        private void imageToTight(android.media.Image img, int W, int H,
                                  byte[] yT, byte[] uT, byte[] vT) {
            android.media.Image.Plane[] planes = img.getPlanes();
            copyPlane(planes[0], W, H, yT);
            copyPlane(planes[1], W / 2, H / 2, uT);
            copyPlane(planes[2], W / 2, H / 2, vT);
        }

        private void copyPlane(android.media.Image.Plane p, int w, int h, byte[] dst) {
            java.nio.ByteBuffer buf = p.getBuffer();
            int rs = p.getRowStride(), ps = p.getPixelStride();
            if (ps == 1) {
                for (int row = 0; row < h; row++) {
                    buf.position(row * rs);
                    buf.get(dst, row * w, Math.min(w, rs));
                }
            } else {
                for (int row = 0; row < h; row++) {
                    for (int col = 0; col < w; col++) {
                        dst[row * w + col] = buf.get(row * rs + col * ps);
                    }
                }
            }
        }

        private void tightToImage(byte[] yT, byte[] uT, byte[] vT, int W, int H,
                                  android.media.Image img) {
            android.media.Image.Plane[] planes = img.getPlanes();
            writePlane(yT, W, H, planes[0]);
            writePlane(uT, W / 2, H / 2, planes[1]);
            writePlane(vT, W / 2, H / 2, planes[2]);
        }

        private void writePlane(byte[] src, int w, int h, android.media.Image.Plane p) {
            java.nio.ByteBuffer buf = p.getBuffer();
            int rs = p.getRowStride(), ps = p.getPixelStride();
            if (ps == 1 && rs == w) {
                buf.position(0);
                buf.put(src, 0, w * h);
            } else if (ps == 1) {
                for (int row = 0; row < h; row++) {
                    buf.position(row * rs);
                    buf.put(src, row * w, w);
                }
            } else {
                for (int row = 0; row < h; row++) {
                    for (int col = 0; col < w; col++) {
                        buf.put(row * rs + col * ps, src[row * w + col]);
                    }
                }
            }
        }
    }

"""

# ---------- Java: composeVideo music mood + per-segment mix ---------------
MOOD_OLD = """                org.json.JSONArray segs = new org.json.JSONArray(segmentsJson);
                if (segs.length() == 0) return "error:no_segments";

                // v3.64: Compose shuru hone par purani temp audio files saf karo (ek dafa!)"""
MOOD_NEW = """                org.json.JSONArray segs = new org.json.JSONArray(segmentsJson);
                if (segs.length() == 0) return "error:no_segments";

                // v4.49: background music mood = pehle non-empty segment
                // ka 'music' field ("" / na mile to music nahi - purani
                // behaviour). JS har segment par mood bhejti hai.
                String meerMusicMood = "";
                try {
                    for (int mi = 0; mi < segs.length(); mi++) {
                        String mv = segs.getJSONObject(mi).optString("music", "");
                        if (mv != null && !mv.isEmpty()) { meerMusicMood = mv; break; }
                    }
                } catch (Exception ignored) { meerMusicMood = ""; }

                // v3.64: Compose shuru hone par purani temp audio files saf karo (ek dafa!)"""
c = java.count(MOOD_OLD)
print('V449-feat java mood anchor:', c)
if c == 1:
    java = java.replace(MOOD_OLD, MOOD_NEW, 1)
else:
    ok = False

TRANSCALL_OLD = "String transcoded = wavToAac(audioPath);"
c = java.count(TRANSCALL_OLD)
print('V449-feat java transcode-call anchor:', c)
if c == 1:
    java = java.replace(TRANSCALL_OLD,
        "String transcoded = wavToAacMusic(audioPath, meerMusicMood, audioPtsUs);", 1)
else:
    ok = False

# music methods wavToAac ke foran baad (getTrackDuration se pehle)
GTD = "        private long getTrackDurationUs(android.media.MediaExtractor extractor, int trackIndex) {"
c = java.count(GTD)
print('V449-feat java getTrackDuration anchor:', c)
if c == 1:
    java = java.replace(GTD, JAVA_MUSIC + GTD, 1)
else:
    ok = False

# MeerMediaBridge class RealClipBridge se pehle (MeerStoryBridge wali
# insertion ke baad bhi anchor unique rehta hai - wo apni class hai)
RCC = "    class RealClipBridge {"
c = java.count(RCC)
print('V449-feat java RealClipBridge anchor:', c)
if c == 1:
    java = java.replace(RCC, JAVA_MEDIA + RCC, 1)
else:
    ok = False

# ---------- Music bundling report (NON-FATAL) ------------------------------
# Tayyar MP3 tracks repo-root 'music/' folder me rehte hain (suspense.mp3 /
# happy.mp3 / calm.mp3 - original/CC0, dekho meer-music/SOURCES.md).
# Workflow me 'Bundle clips into APK' jaisi ek alag step inhe
# android/app/src/main/assets/music/ me copy karti hai (ship ke waqt
# parent add karega). Yahan sirf maujoodgi ki report - tracks na hon to
# bhi build NAHI rukti (Java file na milne par music ke baghair bana
# deta hai).
import glob as _glob, os as _os
_mdirs = [_os.path.join(_os.getcwd(), "music"),
          _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "music")]
_mus = []
for _d in _mdirs:
    _mus = sorted(_glob.glob(_os.path.join(_d, "*.mp3")))
    if _mus:
        break
print("V449 music tracks (assets/music/ ke liye):", len(_mus),
      [_os.path.basename(_m) for _m in _mus])


if not ok:
    print('V449 ABORT: koi anchor 1 nahi mila - koi file NAHI likhi gayi')
    sys.exit(1)

open(HP, 'w', encoding='utf-8').write(html)
open(JP, 'w', encoding='utf-8').write(java)
print('V449 done')
