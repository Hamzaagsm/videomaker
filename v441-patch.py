#!/usr/bin/env python3
# MEER v4.41 - Single Journey: EK journey = EK hi car/clip (Hamza ki demand)
# v4.37 wali singleJourneyClipMode har line par alag clip lagati thi (pool[i2%pool.length]).
# Ye patch us function ko naye siray se define karta hai:
#  - pool saaf: sirf v1 driving clip + manifest ke usi character ke scenes (purani design wali nahi)
#  - pool se EK clip random chun kar POORI journey me wohi lagta hai
#  - harkat me variety Java ke random-start-offset se aati rehti hai
import re

HP = 'android/app/src/main/assets/www/index.html'
html = open(HP, encoding='utf-8').read()

html, n1 = re.subn(r"APP_VER\s*=\s*[\"'][\d.]+[\"']", 'APP_VER="4.41"', html)
html, n2 = re.subn(r"v4\.\d+ MEER", "v4.41 MEER", html)
print('V441 APP_VER bump:', n1, n2)

v441_script = """
<script>
// MEER v4.41: SINGLE JOURNEY - ek journey, ek hi car!
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
          var lines=SJ_POEMS[who];
          var pool=sjPool(who);
          var oneClip=pool[Math.floor(Math.random()*pool.length)];
          var bar=document.getElementById('realBar'), prog=document.getElementById('realProg');
          if(prog)prog.style.display='block';
          var segments=[];
          for(var i2=0;i2<lines.length;i2++){
            if(bar)bar.style.width=(5+i2/lines.length*60)+'%';
            advSetStatus('Awaz '+(i2+1)+'/'+lines.length+': '+who);
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
            if(typeof showBanner==='function')showBanner(who+' ki journey ban gayi! Downloads/MEER me hai','ok');
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
    html = html.replace('</body>', v441_script, 1)
    print('V441 script injected: True')
else:
    print('V441 script injected: False')

open(HP, 'w', encoding='utf-8').write(html)
print('V441 done')
