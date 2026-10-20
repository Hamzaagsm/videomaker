import re

# ============ JAVA: CLIPS_V5 me 3 naye scenes ============
JP = 'android/app/src/main/java/com/hamza/videomaker/MainActivity.java'
java = open(JP, encoding='utf-8').read()

ja_anchor = '''                "adv-rusty-town.mp4", "adv-friends.mp4"
        };'''
ja_new = '''                "adv-rusty-town.mp4", "adv-friends.mp4",
                "adv-rayo-snow.mp4", "adv-bella-autumn.mp4",
                "adv-friends-race.mp4"
        };'''
print('JA anchor found:', ja_anchor in java)
java = java.replace(ja_anchor, ja_new, 1)

# JB: composeVideo me har segment clip ke RANDOM hisse se shuru ho (alag movement har daffa!)
jb_anchor = '''                        long segmentDurationUs = (long)(durationSec * 1000000);
                        long videoStartPts = videoPtsUs;'''
jb_new = jb_anchor + '''
                        // v4.37: har daffa ALAG movement! (clip ke random hisse se shuru)
                        long segStartOffsetUs = 0;
                        try {
                            if (videoFormat.containsKey(android.media.MediaFormat.KEY_DURATION)) {
                                long clipDurUs = videoFormat.getLong(android.media.MediaFormat.KEY_DURATION);
                                long maxOff = clipDurUs - segmentDurationUs - 200000;
                                if (maxOff > 500000) segStartOffsetUs = (long)(Math.random() * maxOff);
                            }
                        } catch (Exception ignored) {}'''
print('JB anchor found:', jb_anchor in java)
java = java.replace(jb_anchor, jb_new, 1)

# JC: pehli pass me seek 0 ki jagah random offset se
jc_anchor = '''                        while (videoPtsUs - videoStartPts < segmentDurationUs && loopCount < 20) {
                            videoExtractor.seekTo(0, android.media.MediaExtractor.SEEK_TO_CLOSEST_SYNC);'''
jc_new = '''                        while (videoPtsUs - videoStartPts < segmentDurationUs && loopCount < 20) {
                            videoExtractor.seekTo(loopCount == 0 ? segStartOffsetUs : 0, android.media.MediaExtractor.SEEK_TO_CLOSEST_SYNC);'''
print('JC anchor found:', jc_anchor in java)
java = java.replace(jc_anchor, jc_new, 1)

open(JP, 'w', encoding='utf-8').write(java)
print('JAVA v437 patched')

# ============ HTML ============
HP = 'android/app/src/main/assets/www/index.html'
html = open(HP, encoding='utf-8').read()

# Adventure: har daffa random scenes chunne ke liye ADV_LINES builder lagao
hb_anchor = "    var bar=document.getElementById('realBar'), prog=document.getElementById('realProg');"
hb_new = "    var ADV_LINES=advBuildLines();\n" + hb_anchor
print('HB anchor found:', hb_anchor in html)
html = html.replace(hb_anchor, hb_new, 1)

# Version
html = re.sub(r"APP_VER\s*=\s*'[\d.]+'", "APP_VER = '4.37'", html)
html = re.sub(r"v4\.\d+ MEER", "v4.37 MEER", html)

# Variety script: adventure slots + REAL VIDEO clip rotation
variety_script = """
<script>
// MEER v4.37: HAR VIDEO ME ALAG SCENES! (random pools)
var ADV_SLOTS=[
 [{ch:'Rayo',clip:'adv-rayo-talk.mp4',text:'Hi friends! I am Rayo! Welcome to Sunny Park! Today we are going on a brand new adventure!'}],
 [{ch:'Bella',clip:'adv-bella-talk.mp4',text:'Hello everyone! I am Bella! Look at these beautiful flowers! I am so happy today!'}],
 [{ch:'Rayo',clip:'adv-rayo-beach.mp4',text:'Wow, the beach road! I can see the ocean! Racing by the sea is the best feeling ever!'},
  {ch:'Rayo',clip:'adv-rayo-snow.mp4',text:'Wow, snowy mountains! Everything is white and sparkling! Driving in the snow is a cool adventure!'}],
 [{ch:'Bella',clip:'adv-bella-town.mp4',text:'Look, the rainbow town! Balloons, colors, and yummy cakes! This place is magical!'},
  {ch:'Bella',clip:'adv-bella-autumn.mp4',text:'Look at the autumn forest! Red and orange leaves are falling everywhere! So beautiful!'}],
 [{ch:'Rusty',clip:'adv-rusty-town.mp4',text:'Howdy friends! Rusty here! In this town, I help everyone. A friend in need is a friend indeed!'}],
 [{ch:'Rayo',clip:'adv-friends.mp4',text:'What a perfect day with my best friends! Remember kids, adventures are better together! Bye bye!'},
  {ch:'Rayo',clip:'adv-friends-race.mp4',text:'Racing with my best friends is the best fun ever! Remember kids, friends make every day special! Bye bye!'}]
];
function advBuildLines(){ var out=[]; for(var i=0;i<ADV_SLOTS.length;i++){ var s=ADV_SLOTS[i]; out.push(s[Math.floor(Math.random()*s.length)]); } return out; }
// REAL VIDEO: clips bhi har daffa ghumao (safed background har daffa nahi!)
(function(){
  try{
    if(typeof realGetNameMap!=='function')return;
    var origMap=realGetNameMap;
    var pools={
      Rayo:{talk:['rayo-talking.mp4','adv-rayo-talk.mp4'],drive:['rayo-driving.mp4','adv-rayo-beach.mp4','adv-rayo-snow.mp4']},
      Bella:{talk:['bella-talking.mp4','adv-bella-talk.mp4'],drive:['bella-driving.mp4','adv-bella-town.mp4','adv-bella-autumn.mp4']},
      Rusty:{talk:['rusty-driving.mp4','adv-rusty-town.mp4'],drive:['rusty-driving.mp4','adv-rusty-town.mp4']}
    };
    function pick(a){ return a[Math.floor(Math.random()*a.length)]; }
    realGetNameMap=function(){
      var m=origMap();
      try{
        var advReady=(typeof RealClipBridge!=='undefined'&&RealClipBridge.areAdvClipsReady&&RealClipBridge.areAdvClipsReady());
        if(advReady){
          for(var k in m){ var p=pools[m[k].voice]; if(p){ m[k].clip=pick(p.talk); m[k].clip2=pick(p.drive); } }
        }
      }catch(e){}
      return m;
    };
  }catch(e){}
})();
// SINGLE JOURNEY (clip version): ek car, asli animated scenes, poem ke saath!
var SJ_POEMS={
 Rayo:['I am Rayo, fast and bright! I love to drive in the morning light!','Through the park and past the sea, driving is the life for me!','Vroom vroom, here I go! Fast or slow, I love the show!','Mountains high and valleys low, every road is fun to go!','When the journey ends today, tomorrow brings a brand new day!'],
 Bella:['I am Bella, sweet and bright! I love to drive in the morning light!','Through the flowers, past the sea, driving is the life for me!','Vroom vroom, here I go! Singing songs as flowers grow!','Rainbow towns and autumn trees, every road is sweet to me!','When the journey ends today, tomorrow brings a brand new day!'],
 Rusty:['I am Rusty, strong and kind! A helping friend is best to find!','Through the town, I roll along, humming my happy tow truck song!','If you need me, call my name! Helping others is my game!','Farms and fields and streets so wide, I enjoy every ride!','When the journey ends today, tomorrow brings a brand new day!']
};
var SJ_CLIPS={
 Rayo:['adv-rayo-talk.mp4','adv-rayo-beach.mp4','adv-rayo-snow.mp4','rayo-driving.mp4'],
 Bella:['adv-bella-talk.mp4','adv-bella-town.mp4','adv-bella-autumn.mp4','bella-driving.mp4'],
 Rusty:['adv-rusty-town.mp4','rusty-driving.mp4','adv-rusty-town.mp4']
};
async function singleJourneyClipMode(){
  try{
    if(typeof RealClipBridge==='undefined'||typeof RealClipBridge.composeVideo!=='function'){ alert('Ye feature MEER app me chalega!'); return; }
    var who=prompt('Kon si car ki journey? Rayo / Bella / Rusty','Rayo');
    if(!who)return;
    who=who.trim(); who=who.charAt(0).toUpperCase()+who.slice(1).toLowerCase();
    if(!SJ_POEMS[who])who='Rayo';
    if(typeof RealClipBridge.areAdvClipsReady==='function'&&!RealClipBridge.areAdvClipsReady()){
      advSetStatus('Scenes tayyar ho rahe hain...');
      try{ RealClipBridge.downloadAdvClips(); }catch(e){}
      var w=0; while(w<30000){ await new Promise(function(r){setTimeout(r,1000);}); w+=1000; if(RealClipBridge.areAdvClipsReady())break; }
    }
    var lines=SJ_POEMS[who], pool=SJ_CLIPS[who].slice();
    for(var i=pool.length-1;i>0;i--){ var j=Math.floor(Math.random()*(i+1)); var t=pool[i]; pool[i]=pool[j]; pool[j]=t; }
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
      segments.push({clip:pool[i2%pool.length],audio:audioPath,duration:Math.max(2.5,audioDurSec+0.6)});
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
      if(typeof showBanner==='function')showBanner(who+' ki journey ban gayi! Downloads/MEER me hai','ok');
      var dl=document.getElementById('realDl');
      if(dl){ dl.style.display='block'; dl.textContent='DOWNLOADS MEIN HAI (MEER folder)'; dl.onclick=function(){ if(typeof showBanner==='function')showBanner('Downloads/MEER folder me dekho!','ok'); }; }
    } else { alert('Video nahi bani: '+result); }
  }catch(e){ alert('Masla: '+e.message); }
}
(function(){
  function rewire(){
    var btns=document.querySelectorAll('button');
    for(var i=0;i<btns.length;i++){
      if(btns[i].textContent.indexOf('SINGLE CAR JOURNEY')>=0 && !btns[i].dataset.sjClip){
        btns[i].dataset.sjClip='1';
        btns[i].onclick=function(ev){ if(ev){ev.preventDefault(); ev.stopPropagation();} singleJourneyClipMode(); return false; };
        return;
      }
    }
    setTimeout(rewire,1500);
  }
  setTimeout(rewire,1200);
})();
</script>
</body>"""
if '</body>' in html:
    html = html.replace('</body>', variety_script, 1)
    print('Variety script injected: True')
else:
    print('Variety script injected: False')

open(HP, 'w', encoding='utf-8').write(html)
print('HTML v437 done')
print('V437 ALL DONE')
