#!/usr/bin/env python3
# MEER v4.40 - teen fix ek sath:
# 1) REAL VIDEO: har LINE par alag scene (per-video ek pick wali ghalti khatam)
#    + pools sirf manifest (pakki shakl wale naye scenes) + v1 clips se bante hain
#    -> purani design wali clips (meadow/autumn/park) REAL VIDEO me nahi ayengi
# 2) ADVENTURE: jo scene phone par maujood na ho, us ki line gayab nahi hogi -
#    maujood scene lag jayega (Java missing clip ko chup chaap drop kar deta hai)
# 3) DURATION: hisaab lines gin kar nahi, LAFZON se hoga (chhoti lines wali
#    script bhi muntakhib minutes ke qareeb jayegi)
import re

HP = 'android/app/src/main/assets/www/index.html'
html = open(HP, encoding='utf-8').read()

# --- APP_VER bump ---
html, n1 = re.subn(r"APP_VER\s*=\s*[\"'][\d.]+[\"']", 'APP_VER="4.40"', html)
html, n2 = re.subn(r"v4\.\d+ MEER", "v4.40 MEER", html)
print('V440 APP_VER bump:', n1, n2)

# --- Fix 3: duration by words (auto-extend block) ---
old_block = """      const durMin=parseInt($('realDur').value)||3;
      const needLines=Math.max(4,Math.round(durMin*60/3));
      if(lines.length<needLines){
        const orig=[...lines];
        let oi=0;
        while(lines.length<needLines){
          lines.push(orig[oi%orig.length]);
          oi++;
        }
        setP(2,'\U0001F4DD Script '+orig.length+' se '+lines.length+' lines (poore '+durMin+' min)!...');
      }"""
new_block = """      const durMin=parseInt($('realDur').value)||3;
      // v4.40: hisaab LAFZON se! (chhoti lines = kam seconds; pehle lines gin kar ghalat andaza hota tha)
      const lineSecV440=function(t){ var w=((t||'').trim().split(/\\s+/).filter(Boolean).length)||1; return Math.max(1.4,w*0.45); };
      var estSecV440=0; for(var liV440=0;liV440<lines.length;liV440++)estSecV440+=lineSecV440(lines[liV440].text);
      const targetSecV440=durMin*60*0.9;
      if(estSecV440<targetSecV440){
        const orig=[...lines];
        let oi=0;
        while(estSecV440<targetSecV440&&lines.length<400){
          var addV440=orig[oi%orig.length];
          lines.push(addV440); estSecV440+=lineSecV440(addV440.text);
          oi++;
        }
        setP(2,'\U0001F4DD Script '+orig.length+' se '+lines.length+' lines (poore '+durMin+' min)!...');
      }"""
if old_block in html:
    html = html.replace(old_block, new_block, 1)
    print('V440 duration-by-words: True')
else:
    print('V440 duration-by-words: False  <-- ANCHOR MISSING')

# --- Fix 1 + 2: injected script (v439 layer ke BAAD chalta hai) ---
v440_script = """
<script>
// MEER v4.40: REAL VIDEO har line par ALAG scene + saaf pools; Adventure line-drop guard
(function(){
  function poolFor(ch,kind){
    var base={Rayo:{talk:['rayo-talking.mp4'],drive:['rayo-driving.mp4']},
              Bella:{talk:['bella-talking.mp4'],drive:['bella-driving.mp4']},
              Rusty:{talk:['rusty-driving.mp4'],drive:['rusty-driving.mp4']}}[ch];
    var out=base?base[kind].slice():[];
    try{
      if(typeof _manifest!=='undefined'&&_manifest){
        for(var i=0;i<_manifest.length;i++){ var e=_manifest[i];
          if(e.ch===ch&&e.kind===kind&&e.clip&&out.indexOf(e.clip)<0) out.push(e.clip); }
      }
    }catch(e){}
    return out;
  }
  var lastPick={};
  function pickLine(ch,kind,fallback){
    var pool=poolFor(ch,kind);
    var avail=pool;
    try{ if(typeof advOk==='function') avail=pool.filter(function(n){ return advOk(n); }); }catch(e){}
    if(!avail.length) avail=pool;
    if(!avail.length) return fallback;
    var key=ch+'|'+kind, pick=null, tries=0;
    do{ pick=avail[Math.floor(Math.random()*avail.length)]; tries++; }
    while(avail.length>1&&pick===lastPick[key]&&tries<12);
    lastPick[key]=pick;
    return pick;
  }
  // 1) REAL VIDEO: nameMap ki clip/clip2 ko per-access pick banao
  try{
    if(typeof realGetNameMap==='function'){
      var prevMap440=realGetNameMap;
      realGetNameMap=function(){
        var m=prevMap440();
        try{
          for(var k in m){
            (function(entry){
              var voice=entry.voice||k;
              var fbT=entry.clip, fbD=entry.clip2;
              try{
                Object.defineProperty(entry,'clip',{configurable:true,enumerable:true,
                  get:function(){ return pickLine(voice,'talk',fbT); }});
                Object.defineProperty(entry,'clip2',{configurable:true,enumerable:true,
                  get:function(){ return pickLine(voice,'drive',fbD); }});
              }catch(e){}
            })(m[k]);
          }
        }catch(e){}
        return m;
      };
    }
  }catch(e){}
  // 2) ADVENTURE: line gayab na ho - clip maujood na ho to maujood scene lagao
  try{
    if(typeof advBuildLines==='function'){
      var prevBuild440=advBuildLines;
      advBuildLines=function(){
        var lines=prevBuild440();
        try{
          var safe=['adv-friends.mp4','adv-rayo-beach.mp4','adv-bella-talk.mp4','adv-rusty-town.mp4','rayo-driving.mp4'];
          var safeClip=null;
          for(var s=0;s<safe.length;s++){ if(typeof advOk!=='function'||advOk(safe[s])){ safeClip=safe[s]; break; } }
          for(var i=0;i<lines.length;i++){
            if(typeof advOk==='function'&&!advOk(lines[i].clip)){
              var replaced=false;
              try{
                var slot=(typeof ADV_SLOTS!=='undefined'&&ADV_SLOTS[i])?ADV_SLOTS[i]:[];
                for(var j=0;j<slot.length;j++){ if(advOk(slot[j].clip)){ lines[i]={ch:slot[j].ch,clip:slot[j].clip,text:lines[i].text}; replaced=true; break; } }
              }catch(e){}
              if(!replaced&&safeClip){ lines[i]={ch:lines[i].ch,clip:safeClip,text:lines[i].text}; }
            }
          }
        }catch(e){}
        return lines;
      };
    }
  }catch(e){}
})();
</script>
</body>"""
if '</body>' in html:
    html = html.replace('</body>', v440_script, 1)
    print('V440 script injected: True')
else:
    print('V440 script injected: False')

open(HP, 'w', encoding='utf-8').write(html)
print('V440 done')
