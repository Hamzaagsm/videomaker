#!/usr/bin/env python3
# MEER v4.43 - SAB KUCH EK HE VERSION ME (Hamza checklist 2026-10-21):
#  1) Cartoon Suspense mode (online library, unlimited heroes, Hindi+English) - additive
#  2) Home par roshan CARTOON SUSPENSE button
#  3) Journey v3: online unlimited stories - line KABHI repeat nahi, lambai nayi stories se
#  4) Real Video: Kahani Bank (online ready stories script me dalo)
#  5) Suspense me "Meri Script" - apni lines se fori video
# REGRESSION SAFETY (Hamza ki standing hidayat): purana code NAHI chheda jata -
# Java me sirf naye methods/constants + getClipPath me 1 inserted line; JS sirf nayi script.
import re

HP = 'android/app/src/main/assets/www/index.html'
JP = 'android/app/src/main/java/com/hamza/videomaker/MainActivity.java'
html = open(HP, encoding='utf-8').read()
java = open(JP, encoding='utf-8').read()

html, n1 = re.subn(r"APP_VER\s*=\s*[\"'][\d.]+[\"']", 'APP_VER="4.43"', html)
html, n2 = re.subn(r"v4\.\d+ MEER", "v4.43 MEER", html)
print('V443 APP_VER bump:', n1, n2)

# --- HTML: home par roshan Cartoon Suspense button (purane button ke FORAN baad, sirf addition) ---
anchor_home = '''<button class="bigbtn" onclick="goSuspense()" style="background:linear-gradient(135deg,#1a1a2e,#16213e);border:2px solid #e94560">👻 Suspense Stories</button>'''
home_btn = anchor_home + '''
<button class="bigbtn" onclick="go('s-cars');setTimeout(function(){var e=document.getElementById('suspBtn');if(e){e.scrollIntoView({block:'center'});}},700)" style="background:linear-gradient(135deg,#7c3aed,#db2777);border:2px solid #fbbf24;margin-top:8px">👻 CARTOON SUSPENSE — Nayi Kahaniyan (Hindi/English)!</button>'''
if anchor_home in html:
    html = html.replace(anchor_home, home_btn, 1)
    print('V443 home button: True')
else:
    print('V443 home button: False  <-- ANCHOR MISSING')

# --- JAVA 1: suspense base + prefix check (sirf addition) ---
anchor_j1 = '''        private static final String CLIP_BASE_V5 =
                "https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/adv-clips/";'''
susp_decl = anchor_j1 + '''
        // v4.43: Cartoon Suspense library (online, unlimited stories)
        private static final String CLIP_BASE_SUSP =
                "https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/suspense-clips/";
        private boolean isSuspClip(String name) {
            return name != null && name.startsWith("susp-") && name.endsWith(".mp4")
                    && !name.contains("/") && !name.contains("..") && !name.contains("\\\\");
        }'''
if anchor_j1 in java:
    java = java.replace(anchor_j1, susp_decl, 1)
    print('V443 java susp base: True')
else:
    print('V443 java susp base: False  <-- ANCHOR MISSING')

# --- JAVA 2: NAYA downloadSuspClip method (pure addition; purana downloadOneClip nahi chheda) ---
anchor_j2 = '''        @JavascriptInterface
        public boolean downloadOneClip(String name) {'''
susp_method = '''        // v4.43: suspense clips download (naya method - sirf susp-* ke liye)
        @JavascriptInterface
        public boolean downloadSuspClip(String name) {
            try {
                if (!isSuspClip(name)) return false;
                File f = new File(clipDir(), name);
                if (clipOk(f)) return true;
                if (f.exists()) f.delete();
                DownloadManager dm = (DownloadManager) getSystemService(Context.DOWNLOAD_SERVICE);
                if (dlActive("susp:" + name, dm)) return true;
                DownloadManager.Request req = new DownloadManager.Request(Uri.parse(CLIP_BASE_SUSP + name));
                req.setTitle("MEER suspense: " + name);
                req.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE);
                req.setDestinationUri(Uri.fromFile(f));
                dlRemember("susp:" + name, dm.enqueue(req));
                return true;
            } catch (Exception e) { return false; }
        }

''' + anchor_j2
if anchor_j2 in java:
    java = java.replace(anchor_j2, susp_method, 1)
    print('V443 java downloadSuspClip added: True')
else:
    print('V443 java downloadSuspClip added: False  <-- ANCHOR MISSING')

# --- JAVA 3: getClipPath whitelist me susp prefix (sirf 1 inserted line) ---
anchor_j3 = '''                if (!ok) return "";
                File f = new File(clipDir(), name);'''
susp_ok = '''                if (!ok && isSuspClip(name)) ok = true; // v4.43: suspense clips (prefix-whitelisted)
                if (!ok) return "";
                File f = new File(clipDir(), name);'''
if anchor_j3 in java:
    java = java.replace(anchor_j3, susp_ok, 1)
    print('V443 java getClipPath susp: True')
else:
    print('V443 java getClipPath susp: False  <-- ANCHOR MISSING')

open(JP, 'w', encoding='utf-8').write(java)

# --- JS: v4.43 ki nayi script (suspense + meri script + journey v3 + kahani bank) ---
v443_script = r"""
<script>
// MEER v4.43: CARTOON SUSPENSE + JOURNEY v3 (unlimited stories) + KAHANI BANK + MERI SCRIPT
var SUSP_URL='https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/suspense-clips/suspense-manifest.json';
var JOURNEY_URL='https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/journey-manifest.json';
var REAL_STORIES_URL='https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/real-stories.json';
var _susp=null, suspLang='hi', _journey=null;
function suspSetStatus(t){ var el=document.getElementById('suspStat'); if(el)el.textContent=t; var b=document.getElementById('realStat'); if(b)b.textContent=t; }
function measureAudio(dataUri){ return new Promise(function(res){ try{ var au=new Audio(); au.src=dataUri; var to=setTimeout(function(){res(0);},8000); au.addEventListener('loadedmetadata',function(){ clearTimeout(to); res((au.duration&&isFinite(au.duration))?au.duration:0); },{once:true}); au.addEventListener('error',function(){ clearTimeout(to); res(0); },{once:true}); }catch(e){ res(0); } }); }
async function speakSeg(text,lang,pitch,tag,i){
  var d=await nativeSpeakRetry(text,lang,pitch,1.0);
  if(!d||d.length<=100) return null;
  var p=RealClipBridge.saveAudioBase64(d,tag+'_'+Date.now()+'_'+i+'.wav');
  if(!p) return null;
  var dur=await measureAudio(d);
  return {audio:p,duration:Math.max(2.5,dur+0.6)};
}
function showMadeVideo(result,okMsg){
  var path=result.split('|')[0].substring(3);
  var bar=document.getElementById('realBar'); if(bar)bar.style.width='100%';
  var vidEl=document.getElementById('realPreview');
  if(vidEl){ vidEl.src='file://'+path; vidEl.style.display='block'; vidEl.load(); }
  try{ _lastVideoPath=path; }catch(e){}
  if(typeof showBanner==='function')showBanner(okMsg,'ok');
  var dl=document.getElementById('realDl');
  if(dl){ dl.style.display='block'; dl.textContent='DOWNLOADS MEIN HAI (MEER folder)'; dl.onclick=function(){ if(typeof showBanner==='function')showBanner('Downloads/MEER folder me dekho!','ok'); }; }
  return path;
}
// ============ SUSPENSE ============
function suspRender(){
  var sel=document.getElementById('suspStory'); if(!sel)return;
  var cur=sel.value; sel.innerHTML='';
  var st=(_susp&&_susp.stories)||[];
  for(var i=0;i<st.length;i++){
    var o=document.createElement('option'); o.value=st[i].id;
    o.textContent=((suspLang==='hi')?(st[i].title_hi||st[i].title_en):(st[i].title_en||st[i].title_hi))+' - '+st[i].hero;
    sel.appendChild(o);
  }
  if(cur)sel.value=cur;
  var lb=document.getElementById('suspLangBtn'); if(lb)lb.textContent=(suspLang==='hi')?'Language: HINDI':'Language: ENGLISH';
}
function suspLoad(){
  try{ var s=localStorage.getItem('meer_susp'); if(s)_susp=JSON.parse(s); }catch(e){}
  suspRender();
  fetch(SUSP_URL,{cache:'no-store'}).then(function(r){ return r.json(); }).then(function(j){
    _susp=j; try{ localStorage.setItem('meer_susp',JSON.stringify(j)); }catch(e){}
    suspRender();
    try{
      var st=j.stories||[];
      for(var i=0;i<st.length;i++){ var bs=st[i].beats||[];
        for(var k=0;k<bs.length;k++){ (function(n){ try{ if(!advOk(n)&&typeof RealClipBridge!=='undefined'&&RealClipBridge.downloadSuspClip)RealClipBridge.downloadSuspClip(n); }catch(e){} })(bs[k].clip); } }
    }catch(e){}
  }).catch(function(){});
}
function suspToggleLang(){ suspLang=(suspLang==='hi')?'en':'hi'; suspRender(); }
function suspPickStory(){
  var st=(_susp&&_susp.stories)||[];
  var sel=document.getElementById('suspStory'); var story=null;
  for(var i=0;i<st.length;i++) if(sel&&st[i].id===sel.value) story=st[i];
  return story||st[0]||null;
}
async function suspEnsureClips(clips,useSuspDl){
  var missing=clips.filter(function(n){ return !advOk(n); });
  if(!missing.length) return true;
  suspSetStatus('Scenes download ho rahe hain ('+missing.length+')...');
  missing.forEach(function(n){ try{ if(useSuspDl)RealClipBridge.downloadSuspClip(n); else RealClipBridge.downloadOneClip(n); }catch(e){} });
  var waited=0;
  while(waited<60000){
    await new Promise(function(r){ setTimeout(r,1500); }); waited+=1500;
    var left=clips.filter(function(n){ return !advOk(n); });
    if(!left.length) return true;
    suspSetStatus('Scenes download ho rahe hain... '+left.length+' baqi');
  }
  return clips.every(function(n){ return advOk(n); });
}
async function suspMakeVideo(){
  try{
    if(typeof RealClipBridge==='undefined'||typeof RealClipBridge.composeVideo!=='function'){ alert('Ye feature MEER app me chalega!'); return; }
    var story=suspPickStory();
    if(!story){ alert('Kahaniyan load nahi huin - internet on karke app dobara kholo!'); return; }
    var clips=story.beats.map(function(b){ return b.clip; });
    if(!await suspEnsureClips(clips,true)){ alert('Kuch scenes abhi download nahi hue - thora ruk kar dobara dabao!'); return; }
    var bar=document.getElementById('realBar'), prog=document.getElementById('realProg');
    if(prog)prog.style.display='block';
    var segments=[];
    for(var i2=0;i2<story.beats.length;i2++){
      var B=story.beats[i2];
      if(bar)bar.style.width=(5+i2/story.beats.length*60)+'%';
      suspSetStatus('Awaz '+(i2+1)+'/'+story.beats.length+': '+story.hero);
      var text=(suspLang==='hi')?(B.hi||B.en):(B.en||B.hi);
      var s=await speakSeg(text,suspLang,(story.pitch||1.1),'susp',i2);
      if(!s){ alert('Awaz nahi ban saki (line '+(i2+1)+') - dobara try karo!'); return; }
      segments.push({clip:B.clip,audio:s.audio,duration:s.duration});
    }
    if(bar)bar.style.width='75%';
    suspSetStatus('Suspense video ban rahi hai...');
    var result=RealClipBridge.composeVideo(JSON.stringify(segments),'MEER_Suspense_'+story.id+'_'+suspLang+'_'+Date.now()+'.mp4');
    if(result&&result.indexOf('ok:')===0){ suspSetStatus('Suspense video tayyar!'); showMadeVideo(result,'Suspense video ban gayi! Downloads/MEER me hai'); }
    else { alert('Video nahi bani: '+result); suspSetStatus('Error: '+result); }
  }catch(e){ alert('Masla: '+e.message); }
}
async function suspMyMakeVideo(){
  try{
    if(typeof RealClipBridge==='undefined'||typeof RealClipBridge.composeVideo!=='function'){ alert('Ye feature MEER app me chalega!'); return; }
    var ta=document.getElementById('suspMyScript');
    var raw=ta?ta.value.trim():'';
    if(!raw){ alert('Pehle apni kahani ki lines likho!'); return; }
    var lines=raw.split(/\n+/).map(function(s){ return s.trim(); }).filter(function(s){ return s.length>1; });
    if(!lines.length){ alert('Lines samajh nahi ayin - har line alag likho!'); return; }
    var story=suspPickStory();
    if(!story){ alert('Pehle kahaniyan load hone do (internet on rakho)!'); return; }
    var clips=story.beats.map(function(b){ return b.clip; });
    if(!await suspEnsureClips(clips,true)){ alert('Scenes abhi tayyar nahi - thora ruk kar dobara dabao!'); return; }
    var bar=document.getElementById('realBar'), prog=document.getElementById('realProg');
    if(prog)prog.style.display='block';
    var segments=[];
    for(var i2=0;i2<lines.length;i2++){
      if(bar)bar.style.width=(5+i2/lines.length*60)+'%';
      suspSetStatus('Awaz '+(i2+1)+'/'+lines.length+': meri kahani');
      var s=await speakSeg(lines[i2],suspLang,(story.pitch||1.1),'mysusp',i2);
      if(!s){ alert('Awaz nahi ban saki (line '+(i2+1)+') - dobara try karo!'); return; }
      segments.push({clip:clips[i2%clips.length],audio:s.audio,duration:s.duration});
    }
    if(bar)bar.style.width='75%';
    suspSetStatus('Meri kahani ki video ban rahi hai...');
    var result=RealClipBridge.composeVideo(JSON.stringify(segments),'MEER_MeriKahani_'+Date.now()+'.mp4');
    if(result&&result.indexOf('ok:')===0){ suspSetStatus('Meri kahani ki video tayyar!'); showMadeVideo(result,'Tumhari kahani ki video ban gayi! Downloads/MEER me hai'); }
    else { alert('Video nahi bani: '+result); suspSetStatus('Error: '+result); }
  }catch(e){ alert('Masla: '+e.message); }
}
(function(){
  function addUI(){
    if(document.getElementById('suspBtn'))return;
    var adv=document.getElementById('advBtn');
    if(!adv){ setTimeout(addUI,1500); return; }
    var wrap=document.createElement('div'); wrap.style.cssText='margin-top:12px;';
    var sel=document.createElement('select'); sel.id='suspStory'; sel.style.cssText='width:100%;padding:10px;border-radius:10px;margin-bottom:8px;font-size:15px;';
    var lb=document.createElement('button'); lb.id='suspLangBtn'; lb.className='btn'; lb.style.cssText='width:100%;margin-bottom:8px;background:#374151;color:#fff;'; lb.textContent='Language: HINDI'; lb.onclick=suspToggleLang;
    var b=document.createElement('button'); b.id='suspBtn'; b.className='btn btn3'; b.style.cssText='width:100%;background:linear-gradient(90deg,#5b21b6,#111827);color:#fff;'; b.textContent='CARTOON SUSPENSE VIDEO BANAO'; b.onclick=suspMakeVideo;
    var st=document.createElement('div'); st.id='suspStat'; st.style.cssText='text-align:center;margin-top:6px;font-size:13px;color:#c4b5fd;';
    var ta=document.createElement('textarea'); ta.id='suspMyScript'; ta.rows=5; ta.placeholder='Apni kahani ki lines yahan likho - har line alag!'; ta.style.cssText='width:100%;padding:10px;border-radius:10px;margin-top:10px;font-size:14px;';
    var mb=document.createElement('button'); mb.id='suspMyBtn'; mb.className='btn'; mb.style.cssText='width:100%;margin-top:8px;background:linear-gradient(90deg,#065f46,#0ea5e9);color:#fff;'; mb.textContent='MERI SCRIPT SE VIDEO BANAO'; mb.onclick=suspMyMakeVideo;
    wrap.appendChild(sel); wrap.appendChild(lb); wrap.appendChild(b); wrap.appendChild(st); wrap.appendChild(ta); wrap.appendChild(mb);
    var after=(adv.nextSibling&&adv.nextSibling.nextSibling)?adv.nextSibling.nextSibling:adv.nextSibling;
    adv.parentNode.insertBefore(wrap,after);
    suspLoad();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){ setTimeout(addUI,1000); });
  else setTimeout(addUI,1000);
})();
// ============ JOURNEY v3: online unlimited stories - line KABHI repeat nahi ============
function journeyLoad(){
  try{ var s=localStorage.getItem('meer_journey'); if(s)_journey=JSON.parse(s); }catch(e){}
  fetch(JOURNEY_URL,{cache:'no-store'}).then(function(r){ return r.json(); }).then(function(j){
    _journey=j; try{ localStorage.setItem('meer_journey',JSON.stringify(j)); }catch(e){}
    try{ var st=j.stories||[]; for(var i=0;i<st.length;i++){ var ls=st[i].lines||[];
      for(var k=0;k<ls.length;k++){ (function(n){ try{ if(!advOk(n)&&typeof RealClipBridge!=='undefined'&&RealClipBridge.downloadOneClip)RealClipBridge.downloadOneClip(n); }catch(e){} })(ls[k].clip); } } }catch(e){}
  }).catch(function(){});
}
function journeyEstSec(text){ var w=(text||'').trim().split(/\s+/).length; return Math.max(1.4,w*0.36); }
function journeyPlan(who,durMin){
  var all=(_journey.stories||[]).filter(function(s){ return s.car===who; });
  if(!all.length) return [];
  var targetSec=durMin*60*0.95;
  var order=all.slice();
  for(var i=order.length-1;i>0;i--){ var j=Math.floor(Math.random()*(i+1)); var t=order[i]; order[i]=order[j]; order[j]=t; }
  var plan=[], est=0;
  for(var si=0; si<order.length; si++){
    var story=order[si];
    for(var li=0; li<story.lines.length; li++){
      if(est>=targetSec) break;
      plan.push({t:story.lines[li].t, clip:story.lines[li].clip, story:story.title});
      est+=journeyEstSec(story.lines[li].t)+0.6;
    }
    if(est>=targetSec) break;
  }
  return plan;
}
async function journeyV3(){
  try{
    if(typeof RealClipBridge==='undefined'||typeof RealClipBridge.composeVideo!=='function'){ alert('Ye feature MEER app me chalega!'); return; }
    if(!_journey){ journeyLoad(); alert('Journey stories load ho rahi hain - internet on karke 10 second baad dobara dabao!'); return; }
    var who=prompt('Kon si car ki journey? Rayo / Bella / Rusty','Rayo');
    if(!who)return;
    who=who.trim(); who=who.charAt(0).toUpperCase()+who.slice(1).toLowerCase();
    var durMin=3; try{ durMin=parseInt(document.getElementById('realDur').value)||3; }catch(e){}
    var plan=journeyPlan(who,durMin);
    if(!plan.length){ alert('Is car ki stories nahi milin!'); return; }
    var need={}, missing=[];
    plan.forEach(function(p){ if(!need[p.clip]){ need[p.clip]=1; if(!advOk(p.clip)) missing.push(p.clip); } });
    if(missing.length){
      advSetStatus('Journey scenes download ho rahe hain ('+missing.length+')...');
      missing.forEach(function(n){ try{ RealClipBridge.downloadOneClip(n); }catch(e){} });
      var waited=0;
      while(waited<60000){ await new Promise(function(r){ setTimeout(r,1500); }); waited+=1500;
        var left=missing.filter(function(n){ return !advOk(n); });
        if(!left.length) break;
        advSetStatus('Scenes download ho rahe hain... '+left.length+' baqi'); }
    }
    var bar=document.getElementById('realBar'), prog=document.getElementById('realProg');
    if(prog)prog.style.display='block';
    var pitch=(typeof CARCHARS!=='undefined'&&CARCHARS[who]&&CARCHARS[who].pitch)||1.0;
    var segments=[], lastGood=null;
    for(var i2=0;i2<plan.length;i2++){
      var P=plan[i2];
      if(bar)bar.style.width=(5+i2/plan.length*60)+'%';
      advSetStatus('Journey: '+P.story+' - awaz '+(i2+1)+'/'+plan.length);
      var clip=P.clip;
      if(!advOk(clip)){ clip=lastGood||plan[0].clip; } else lastGood=clip;
      var s=await speakSeg(P.t,'en',pitch,'jrn',i2);
      if(!s){ alert('Awaz nahi ban saki (line '+(i2+1)+') - dobara try karo!'); return; }
      segments.push({clip:clip,audio:s.audio,duration:s.duration});
    }
    if(bar)bar.style.width='75%';
    advSetStatus('Journey video ban rahi hai...');
    var result=RealClipBridge.composeVideo(JSON.stringify(segments),'MEER_Journey_'+who+'_'+Date.now()+'.mp4');
    if(result&&result.indexOf('ok:')===0){ advSetStatus('Journey tayyar!'); showMadeVideo(result,who+' ki journey ban gayi! Downloads/MEER me hai'); }
    else { alert('Video nahi bani: '+result); advSetStatus('Error: '+result); }
  }catch(e){ alert('Masla: '+e.message); }
}
(function(){
  function rebind(){
    try{ singleJourneyClipMode=journeyV3; }catch(e){}
    var btns=document.querySelectorAll('button');
    for(var i=0;i<btns.length;i++){
      if(btns[i].textContent.indexOf('SINGLE CAR JOURNEY')>=0){
        btns[i].dataset.jrnV3='1';
        btns[i].onclick=function(ev){ if(ev){ ev.preventDefault(); ev.stopPropagation(); } journeyV3(); return false; };
      }
    }
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){ setTimeout(rebind,2500); setInterval(rebind,5000); });
  else { setTimeout(rebind,2500); setInterval(rebind,5000); }
  journeyLoad();
})();
// ============ REAL VIDEO: KAHANI BANK ============
function realBankLoad(){
  fetch(REAL_STORIES_URL,{cache:'no-store'}).then(function(r){ return r.json(); }).then(function(j){
    var sel=document.getElementById('realBankSel'); if(!sel)return;
    sel.innerHTML='';
    var o0=document.createElement('option'); o0.textContent='Kahani Bank - kahani chuno...'; sel.appendChild(o0);
    (j.stories||[]).forEach(function(s){ var o=document.createElement('option'); o.value=s.title; o.textContent=s.title; o.dataset.script=s.script; sel.appendChild(o); });
  }).catch(function(){});
}
(function(){
  function addBank(){
    if(document.getElementById('realBankSel'))return;
    var ta=document.getElementById('realScript');
    if(!ta){ setTimeout(addBank,1500); return; }
    var wrap=document.createElement('div'); wrap.style.cssText='margin:10px 0;';
    var sel=document.createElement('select'); sel.id='realBankSel'; sel.style.cssText='width:100%;padding:10px;border-radius:10px;margin-bottom:8px;font-size:15px;';
    var o0=document.createElement('option'); o0.textContent='Kahani Bank - kahani chuno...'; sel.appendChild(o0);
    var b=document.createElement('button'); b.className='btn'; b.style.cssText='width:100%;background:linear-gradient(90deg,#0ea5e9,#22c55e);color:#fff;'; b.textContent='YE KAHANI SCRIPT ME DALO';
    b.onclick=function(){
      var s=document.getElementById('realBankSel'); var opt=s?s.options[s.selectedIndex]:null;
      if(opt&&opt.dataset&&opt.dataset.script){ document.getElementById('realScript').value=opt.dataset.script; advSetStatus('Kahani script me aa gayi! Ab REAL VIDEO BANAO dabao.'); }
      else alert('Pehle kahani chuno!');
    };
    wrap.appendChild(sel); wrap.appendChild(b);
    ta.parentNode.insertBefore(wrap,ta);
    realBankLoad();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){ setTimeout(addBank,1200); });
  else setTimeout(addBank,1200);
})();
</script>
</body>"""
if '</body>' in html:
    html = html.replace('</body>', v443_script, 1)
    print('V443 script injected: True')
else:
    print('V443 script injected: False')

open(HP, 'w', encoding='utf-8').write(html)
print('V443 done')
