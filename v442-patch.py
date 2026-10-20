#!/usr/bin/env python3
# MEER v4.42 - Single Journey v2: EK car + muntakhib DURATION ke hisaab se lambi journey
# v4.41 me journey sirf 5-line poem jitni (~20s) banti thi - duration select ka koi asar nahi tha.
# Ab: poem lines lafz-hisaab se repeat hoti hain jab tak muntakhib minutes ke qareeb na ho jayen,
# aur saari lines par EK HI clip (saaf pool se) lagta hai.
import re

HP = 'android/app/src/main/assets/www/index.html'
html = open(HP, encoding='utf-8').read()

html, n1 = re.subn(r"APP_VER\s*=\s*[\"'][\d.]+[\"']", 'APP_VER="4.42"', html)
html, n2 = re.subn(r"v4\.\d+ MEER", "v4.42 MEER", html)
print('V442 APP_VER bump:', n1, n2)

# --- REAL VIDEO duration calibration (v440 wala hisaab asal TTS speed se milao) ---
if 'return Math.max(1.4,w*0.45);' in html:
    html = html.replace('return Math.max(1.4,w*0.45);', 'return Math.max(1.4,w*0.36);', 1)
    print('V442 real-duration calibration: True')
else:
    print('V442 real-duration calibration: False  <-- ANCHOR MISSING')
if 'const targetSecV440=durMin*60*0.9;' in html:
    html = html.replace('const targetSecV440=durMin*60*0.9;', 'const targetSecV440=durMin*60*0.95;', 1)
    print('V442 real-duration target: True')
else:
    print('V442 real-duration target: False  <-- ANCHOR MISSING')

v442_script = """
<script>
// MEER v4.42: SINGLE JOURNEY - ek car + muntakhib minutes ki journey!
(function(){
  function sjPool(who){
    var v1={Rayo:'rayo-driving.mp4',Bella:'bella-driving.mp4',Rusty:'rusty-driving.mp4'};
    var out=[];
    if(v1[who])out.push(v1[who]);
    try{
      if(typeof _manifest!=='undefined'&&_manifest){
        for(var i=0;i<_manifest.length;i++){ var e=_manifest[i];
          if(e.ch===who&&e.clip&&out.indexOf(e.clip)<0) out.push(e.clip); }
      }
    }catch(e){}
    var avail=out;
    try{ if(typeof advOk==='function') avail=out.filter(function(n){ return advOk(n); }); }catch(e){}
    return avail.length?avail:out;
  }
  function lineSec(t){ var w=((t||'').trim().split(/\\s+/).filter(Boolean).length)||1; return Math.max(1.6,w*0.36); }
  try{
    if(typeof singleJourneyClipMode==='function'){
      singleJourneyClipMode=async function(){
        try{
          if(typeof RealClipBridge==='undefined'||typeof RealClipBridge.composeVideo!=='function'){ alert('Ye feature MEER app me chalega!'); return; }
          var who=prompt('Kon si car ki journey? Rayo / Bella / Rusty','Rayo');
          if(!who)return;
          who=who.trim(); who=who.charAt(0).toUpperCase()+who.slice(1).toLowerCase();
          if(typeof SJ_POEMS==='undefined'||!SJ_POEMS[who])who='Rayo';
          if(typeof RealClipBridge.areAdvClipsReady==='function'&&!RealClipBridge.areAdvClipsReady()){
            advSetStatus('Scenes tayyar ho rahe hain...');
            try{ RealClipBridge.downloadAdvClips(); }catch(e){}
            var w=0; while(w<30000){ await new Promise(function(r){setTimeout(r,1000);}); w+=1000; if(RealClipBridge.areAdvClipsReady())break; }
          }
          var poem=SJ_POEMS[who];
          // v4.42: DURATION ke hisaab se poem lines repeat karo (lafz-hisaab)!
          var durMin=3;
          try{ durMin=parseInt(document.getElementById('realDur').value)||3; }catch(e){}
          var targetSec=durMin*60*0.95;
          var lines=[]; var est=0; var pi=0;
          while(est<targetSec&&lines.length<160){
            var add=poem[pi%poem.length];
            lines.push(add); est+=lineSec(add); pi++;
          }
          var pool=sjPool(who);
          var oneClip=pool[Math.floor(Math.random()*pool.length)];
          var bar=document.getElementById('realBar'), prog=document.getElementById('realProg');
          if(prog)prog.style.display='block';
          var segments=[];
          for(var i2=0;i2<lines.length;i2++){
            if(bar)bar.style.width=(5+i2/lines.length*60)+'%';
            advSetStatus('Awaz '+(i2+1)+'/'+lines.length+': '+who+' ('+durMin+' min journey)');
            var pitch=(typeof CARCHARS!=='undefined'&&CARCHARS[who]&&CARCHARS[who].pitch)||1.0;
            var audioDataUri=await nativeSpeakRetry(lines[i2],'en',pitch,1.0);
            var audioPath='';
            if(audioDataUri&&audioDataUri.length>100){ audioPath=RealClipBridge.saveAudioBase64(audioDataUri,'sj_'+Date.now()+'_'+i2+'.wav'); }
            if(!audioPath){ alert('Awaz nahi ban saki!'); return; }
            var audioDurSec=0;
            try{ var auTmp=new Audio(); auTmp.src=audioDataUri; await new Promise(function(res){ var to=setTimeout(res,8000); auTmp.addEventListener('loadedmetadata',function(){clearTimeout(to);res();},{once:true}); auTmp.addEventListener('error',function(){clearTimeout(to);res();},{once:true}); }); if(auTmp.duration&&isFinite(auTmp.duration))audioDurSec=auTmp.duration; }catch(e){}
            segments.push({clip:oneClip,audio:audioPath,duration:Math.max(2.5,audioDurSec+0.6)});
          }
          if(bar)bar.style.width='75%';
          advSetStatus('Journey video ban rahi hai...');
          var fileName='MEER_Journey_'+who+'_'+Date.now()+'.mp4';
          var result=RealClipBridge.composeVideo(JSON.stringify(segments),fileName);
          if(result&&result.indexOf('ok:')===0){
            var path=result.split('|')[0].substring(3);
            if(bar)bar.style.width='100%';
            advSetStatus('Journey tayyar!');
            var vidEl=document.getElementById('realPreview');
            if(vidEl){ vidEl.src='file://'+path; vidEl.style.display='block'; vidEl.load(); }
            try{ _lastVideoPath=path; }catch(e){}
            if(typeof showBanner==='function')showBanner(who+' ki '+durMin+' min journey ban gayi! Downloads/MEER me hai','ok');
            var dl=document.getElementById('realDl');
            if(dl){ dl.style.display='block'; dl.textContent='DOWNLOADS MEIN HAI (MEER folder)'; dl.onclick=function(){ if(typeof showBanner==='function')showBanner('Downloads/MEER folder me dekho!','ok'); }; }
          } else { alert('Video nahi bani: '+result); }
        }catch(e){ alert('Masla: '+e.message); }
      };
    }
  }catch(e){}
})();
</script>
</body>"""
if '</body>' in html:
    html = html.replace('</body>', v442_script, 1)
    print('V442 script injected: True')
else:
    print('V442 script injected: False')

open(HP, 'w', encoding='utf-8').write(html)
print('V442 done')
