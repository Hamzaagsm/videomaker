import re

# ============ JAVA: MainActivity.java ============
JP = 'android/app/src/main/java/com/hamza/videomaker/MainActivity.java'
java = open(JP, encoding='utf-8').read()

# J1: CLIPS_V5 set + base URL (after CLIPS_V4 array)
j1_anchor = '''                "suspense-flashlight.mp4"
        };'''
j1_add = j1_anchor + '''
        // v4.36: New Adventure mode - generated scenes (adv-clips)
        private static final String CLIP_BASE_V5 =
                "https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/adv-clips/";
        private static final String[] CLIPS_V5 = {
                "adv-rayo-talk.mp4", "adv-bella-talk.mp4",
                "adv-rayo-beach.mp4", "adv-bella-town.mp4",
                "adv-rusty-town.mp4", "adv-friends.mp4"
        };'''
print('J1 anchor found:', j1_anchor in java)
java = java.replace(j1_anchor, j1_add, 1)

# J2: getClipPath whitelist me CLIPS_V5
j2_anchor = '                if (!ok) for (String c : CLIPS_V3) if (c.equals(name)) { ok = true; break; }'
j2_add = j2_anchor + '\n                if (!ok) for (String c : CLIPS_V5) if (c.equals(name)) { ok = true; break; }'
print('J2 anchor found:', j2_anchor in java)
java = java.replace(j2_anchor, j2_add, 1)

# J3: naye bridge methods (getDownloadedCount se pehle)
j3_anchor = '''        @JavascriptInterface
        public int getDownloadedCount() {'''
j3_add = '''        @JavascriptInterface
        public boolean areAdvClipsReady() {
            File dir = clipDir();
            for (String name : CLIPS_V5) {
                if (!clipOk(new File(dir, name))) return false;
            }
            return true;
        }

        @JavascriptInterface
        public void downloadAdvClips() {
            runOnUiThread(() -> {
                try {
                    File dir = clipDir();
                    // v4.36: pehle APK ke andar bundled scenes copy karo (internet nahi chahiye!)
                    try {
                        String[] bundled = getAssets().list("clips");
                        if (bundled != null) {
                            for (String b : bundled) {
                                boolean want = false;
                                for (String n : CLIPS_V5) if (n.equals(b)) want = true;
                                if (!want) continue;
                                File out = new File(dir, b);
                                if (clipOk(out)) continue;
                                try (java.io.InputStream in = getAssets().open("clips/" + b);
                                     java.io.FileOutputStream fos = new java.io.FileOutputStream(out)) {
                                    byte[] buf = new byte[8192]; int r;
                                    while ((r = in.read(buf)) > 0) fos.write(buf, 0, r);
                                    fos.flush();
                                } catch (Exception ignored) {}
                            }
                        }
                    } catch (Exception ignored) {}
                    // Jo reh jaye wo online download
                    DownloadManager dm = (DownloadManager) getSystemService(Context.DOWNLOAD_SERVICE);
                    int started = 0;
                    for (String name : CLIPS_V5) {
                        File f = new File(dir, name);
                        if (clipOk(f)) continue;
                        if (dlActive("c:" + name, dm)) continue;
                        DownloadManager.Request req =
                                new DownloadManager.Request(Uri.parse(CLIP_BASE_V5 + name));
                        req.setTitle("MEER adventure clip: " + name);
                        req.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE);
                        req.setDestinationUri(Uri.fromFile(f));
                        dlRemember("c:" + name, dm.enqueue(req));
                        started++;
                    }
                    js("onClipMsg('started'," + started + ")");
                    if (started == 0) js("onClipMsg('ready',0)");
                } catch (Exception e) {
                    js("onClipMsg('error',0)");
                }
            });
        }

''' + j3_anchor
print('J3 anchor found:', j3_anchor in java)
java = java.replace(j3_anchor, j3_add, 1)

open(JP, 'w', encoding='utf-8').write(java)
print('JAVA v436 patched')

# ============ HTML: index.html (android copy) ============
HP = 'android/app/src/main/assets/www/index.html'
html = open(HP, encoding='utf-8').read()

# H1: REAL VIDEO me composeVideo PEHLE (canvas wala kaala dabba baad me fallback)
h1_anchor = """    if(typeof RealClipBridge.renderCanvasVideo==='function'){
      try{
        result=RealClipBridge.renderCanvasVideo(JSON.stringify(segments),fileName);
      }catch(e){ result='error:canvas:'+e.message; }
    }"""
h1_new = """    try{
        result=RealClipBridge.composeVideo(JSON.stringify(segments),fileName);
      }catch(e){ result='error:compose:'+e.message; }"""
print('H1 anchor found:', h1_anchor in html)
html = html.replace(h1_anchor, h1_new, 1)

# H2: fallback ab canvas hai
h2_anchor = """      console.log('[MEER] Canvas failed, fallback to composeVideo:',result);
      result=RealClipBridge.composeVideo(JSON.stringify(segments),fileName);"""
h2_new = """      console.log('[MEER] Compose failed, fallback to canvas:',result);
      try{ result=RealClipBridge.renderCanvasVideo(JSON.stringify(segments),fileName); }catch(e){ result='error:canvas:'+e.message; }"""
print('H2 anchor found:', h2_anchor in html)
html = html.replace(h2_anchor, h2_new, 1)

# H3: version
html = re.sub(r"APP_VER\s*=\s*'[\d.]+'", "APP_VER = '4.36'", html)
html = re.sub(r"v4\.\d+ MEER", "v4.36 MEER", html)

# H4: New Adventure script inject (</body> se pehle)
adv_script = """
<script>
// MEER v4.36: NEW ADVENTURE - generated scenes + voices, one tap!
var ADV_LINES=[
 {ch:'Rayo',clip:'adv-rayo-talk.mp4',text:'Hi friends! I am Rayo! Welcome to Sunny Park! Today we are going on a brand new adventure!'},
 {ch:'Bella',clip:'adv-bella-talk.mp4',text:'Hello everyone! I am Bella! Look at these beautiful flowers! I am so happy today!'},
 {ch:'Rayo',clip:'adv-rayo-beach.mp4',text:'Wow, the beach road! I can see the ocean! Racing by the sea is the best feeling ever!'},
 {ch:'Bella',clip:'adv-bella-town.mp4',text:'Look, the rainbow town! Balloons, colors, and yummy cakes! This place is magical!'},
 {ch:'Rusty',clip:'adv-rusty-town.mp4',text:'Howdy friends! Rusty here! In this town, I help everyone. A friend in need is a friend indeed!'},
 {ch:'Rayo',clip:'adv-friends.mp4',text:'What a perfect day with my best friends! Remember kids, adventures are better together! Bye bye!'}
];
function advSetStatus(t){ var el=document.getElementById('advStat'); if(el)el.textContent=t; var b=document.getElementById('realStat'); if(b)b.textContent=t; }
async function adventureMakeVideo(){
  try{
    if(typeof RealClipBridge==='undefined'||typeof RealClipBridge.composeVideo!=='function'){ alert('Ye feature MEER app me chalega!'); return; }
    if(typeof RealClipBridge.areAdvClipsReady==='function'&&!RealClipBridge.areAdvClipsReady()){
      advSetStatus('Naye scenes tayyar ho rahe hain...');
      try{ RealClipBridge.downloadAdvClips(); }catch(e){}
      var waited=0;
      while(waited<30000){ await new Promise(function(r){setTimeout(r,1000);}); waited+=1000; if(RealClipBridge.areAdvClipsReady())break; }
      if(!RealClipBridge.areAdvClipsReady()){ alert('Scenes abhi tayyar nahi! Thora ruk kar dobara dabao.'); return; }
    }
    var bar=document.getElementById('realBar'), prog=document.getElementById('realProg');
    if(prog)prog.style.display='block';
    var segments=[];
    for(var i=0;i<ADV_LINES.length;i++){
      var L=ADV_LINES[i];
      if(bar)bar.style.width=(5+i/ADV_LINES.length*60)+'%';
      advSetStatus('Awaz '+(i+1)+'/'+ADV_LINES.length+': '+L.ch);
      var pitch=(typeof CARCHARS!=='undefined'&&CARCHARS[L.ch]&&CARCHARS[L.ch].pitch)||1.0;
      var audioDataUri=await nativeSpeakRetry(L.text,'en',pitch,1.0);
      var audioPath='';
      if(audioDataUri&&audioDataUri.length>100){ audioPath=RealClipBridge.saveAudioBase64(audioDataUri,'adv_'+Date.now()+'_'+i+'.wav'); }
      if(!audioPath){ alert('Awaz nahi ban saki (line '+(i+1)+') - dobara try karo!'); return; }
      var audioDurSec=0;
      try{ var auTmp=new Audio(); auTmp.src=audioDataUri; await new Promise(function(res){ var to=setTimeout(res,8000); auTmp.addEventListener('loadedmetadata',function(){clearTimeout(to);res();},{once:true}); auTmp.addEventListener('error',function(){clearTimeout(to);res();},{once:true}); }); if(auTmp.duration&&isFinite(auTmp.duration))audioDurSec=auTmp.duration; }catch(e){}
      segments.push({clip:L.clip,audio:audioPath,duration:Math.max(2.5,audioDurSec+0.6)});
    }
    if(bar)bar.style.width='75%';
    advSetStatus('Video ban rahi hai...');
    var fileName='MEER_Adventure_'+Date.now()+'.mp4';
    var result=RealClipBridge.composeVideo(JSON.stringify(segments),fileName);
    if(result&&result.indexOf('ok:')===0){
      var path=result.split('|')[0].substring(3);
      if(bar)bar.style.width='100%';
      advSetStatus('Video tayyar!');
      var vidEl=document.getElementById('realPreview');
      if(vidEl){ vidEl.src='file://'+path; vidEl.style.display='block'; vidEl.load(); }
      try{ _lastVideoPath=path; }catch(e){}
      if(typeof showBanner==='function')showBanner('Adventure video ban gayi! Downloads/MEER me hai','ok');
      var dl=document.getElementById('realDl');
      if(dl){ dl.style.display='block'; dl.textContent='DOWNLOADS MEIN HAI (MEER folder)'; dl.onclick=function(){ if(typeof showBanner==='function')showBanner('Downloads/MEER folder me dekho!','ok'); }; }
    } else { alert('Video nahi bani: '+result); advSetStatus('Error: '+result); }
  }catch(e){ alert('Masla: '+e.message); }
}
(function(){
  function addBtn(){
    if(document.getElementById('advBtn'))return;
    var btns=document.querySelectorAll('button');
    for(var i=0;i<btns.length;i++){
      if(btns[i].textContent.indexOf('REAL VIDEO BANAO')>=0){
        var b=document.createElement('button');
        b.id='advBtn'; b.className='btn btn3'; b.style.cssText='margin-top:10px;background:linear-gradient(90deg,#ff9a56,#ff5e8a);color:#fff;';
        b.textContent='NEW ADVENTURE VIDEO (naye scenes + awaz!)';
        b.onclick=adventureMakeVideo;
        btns[i].parentNode.insertBefore(b,btns[i].nextSibling);
        var st=document.createElement('div'); st.id='advStat'; st.style.cssText='text-align:center;margin-top:6px;font-size:13px;color:#ffd166;';
        b.parentNode.insertBefore(st,b.nextSibling);
        return;
      }
    }
    setTimeout(addBtn,1500);
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){setTimeout(addBtn,800);});
  else setTimeout(addBtn,800);
})();
</script>
</body>"""
if '</body>' in html:
    html = html.replace('</body>', adv_script, 1)
    print('ADV script injected: True')
else:
    print('ADV script injected: False (no </body>)')

open(HP, 'w', encoding='utf-8').write(html)
print('HTML v436 done')
print('V436 ALL DONE')
