import re

# ============ JAVA ============
JP = 'android/app/src/main/java/com/hamza/videomaker/MainActivity.java'
java = open(JP, encoding='utf-8').read()

# JA: CLIPS_V5 me 6 ONLINE scenes (ye APK me bundle NAHI honge - app online se legi)
ja_anchor = '''                "adv-rayo-meadow.mp4", "adv-bella-beach.mp4",
                "adv-rusty-farm.mp4"
        };'''
ja_new = '''                "adv-rayo-meadow.mp4", "adv-bella-beach.mp4",
                "adv-rusty-farm.mp4",
                "adv-rayo-city.mp4", "adv-bella-snowtalk.mp4",
                "adv-rusty-beach.mp4", "adv-rayo-night.mp4",
                "adv-bella-rainbow.mp4", "adv-friends-picnic.mp4"
        };'''
print('JA anchor found:', ja_anchor in java)
java = java.replace(ja_anchor, ja_new, 1)

# JB: stamp v439 (ek daffa phir refresh)
jb_anchor = 'private static final String CLIP_STAMP = "v438";'
jb_new = 'private static final String CLIP_STAMP = "v439";'
print('JB anchor found:', jb_anchor in java)
java = java.replace(jb_anchor, jb_new, 1)

# JC: clipExists + downloadOneClip bridges (online library ke liye)
jc_anchor = '''        @JavascriptInterface
        public boolean areClipsReady() {'''
jc_new = '''        @JavascriptInterface
        public boolean clipExists(String name) {
            return clipOk(new File(clipDir(), name));
        }

        @JavascriptInterface
        public boolean downloadOneClip(String name) {
            try {
                File f = new File(clipDir(), name);
                if (clipOk(f)) return true;
                if (f.exists()) f.delete();
                DownloadManager dm = (DownloadManager) getSystemService(Context.DOWNLOAD_SERVICE);
                if (dlActive("v5:" + name, dm)) return true;
                DownloadManager.Request req = new DownloadManager.Request(Uri.parse(CLIP_BASE_V5 + name));
                req.setTitle("MEER scene: " + name);
                req.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE);
                req.setDestinationUri(Uri.fromFile(f));
                dlRemember("v5:" + name, dm.enqueue(req));
                return true;
            } catch (Exception e) { return false; }
        }

''' + jc_anchor
print('JC anchor found:', jc_anchor in java)
java = java.replace(jc_anchor, jc_new, 1)

open(JP, 'w', encoding='utf-8').write(java)
print('JAVA v439 patched')

# ============ HTML ============
HP = 'android/app/src/main/assets/www/index.html'
html = open(HP, encoding='utf-8').read()

html = re.sub(r"APP_VER\s*=\s*[\"'][\d.]+[\"']", 'APP_VER="4.39"', html)
html = re.sub(r"v4\.\d+ MEER", "v4.39 MEER", html)

v439_script = """
<script>
// MEER v4.39: ONLINE LIBRARY - har hisse me 3 scenes, baqi app online se leti hai!
function advOk(n){ try{ return (typeof RealClipBridge!=='undefined'&&RealClipBridge.clipExists)?!!RealClipBridge.clipExists(n):true; }catch(e){ return true; } }
var _manifest=null;
function manifestSlots(){
  if(!_manifest) return null;
  var slots=[[],[],[],[],[],[]];
  for(var i=0;i<_manifest.length;i++){ var e=_manifest[i]; if(e.slot>=1&&e.slot<=6) slots[e.slot-1].push({ch:e.ch,clip:e.clip,text:e.line}); }
  for(var j=0;j<6;j++){ if(!slots[j].length) return null; }
  return slots;
}
function loadManifest(){
  try{ var saved=localStorage.getItem('meer_manifest'); if(saved){ _manifest=JSON.parse(saved); } }catch(e){}
  try{
    fetch('https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/adv-clips/manifest.json',{cache:'no-store'}).then(function(r){ return r.json(); }).then(function(j){
      if(j&&j.length){
        _manifest=j;
        try{ localStorage.setItem('meer_manifest',JSON.stringify(j)); }catch(e){}
        for(var i=0;i<j.length;i++){ (function(n){ try{ if(!advOk(n)&&typeof RealClipBridge!=='undefined'&&RealClipBridge.downloadOneClip) RealClipBridge.downloadOneClip(n); }catch(e){} })(j[i].clip); }
      }
    }).catch(function(){});
  }catch(e){}
}
loadManifest();
ADV_SLOTS=[
 [{ch:'Rayo',clip:'adv-rayo-talk.mp4',text:'Hi friends! I am Rayo! Welcome to Sunny Park! Today we are going on a brand new adventure!'},
  {ch:'Rayo',clip:'adv-rayo-meadow.mp4',text:'Hi friends! I am Rayo! Look at this flower meadow! Butterflies are dancing everywhere!'},
  {ch:'Rayo',clip:'adv-rayo-city.mp4',text:'Hi friends! I am Rayo! Welcome to the big colorful city! So many tall buildings and happy people!'}],
 [{ch:'Bella',clip:'adv-bella-talk.mp4',text:'Hello everyone! I am Bella! Look at these beautiful flowers! I am so happy today!'},
  {ch:'Bella',clip:'adv-bella-beach.mp4',text:'Hello everyone! I am Bella! Welcome to the sunny beach! Can you hear the ocean waves?'},
  {ch:'Bella',clip:'adv-bella-snowtalk.mp4',text:'Hello everyone! I am Bella! Welcome to the snowy village! Soft snowflakes are falling all around!'}],
 [{ch:'Rayo',clip:'adv-rayo-beach.mp4',text:'Wow, the beach road! I can see the ocean! Racing by the sea is the best feeling ever!'},
  {ch:'Rayo',clip:'adv-rayo-snow.mp4',text:'Wow, snowy mountains! Everything is white and sparkling! Driving in the snow is a cool adventure!'},
  {ch:'Rayo',clip:'adv-rayo-night.mp4',text:'Wow, the night road! Stars are twinkling and the big moon is shining! Night driving is magical!'}],
 [{ch:'Bella',clip:'adv-bella-town.mp4',text:'Look, the rainbow town! Balloons, colors, and yummy cakes! This place is magical!'},
  {ch:'Bella',clip:'adv-bella-autumn.mp4',text:'Look at the autumn forest! Red and orange leaves are falling everywhere! So beautiful!'},
  {ch:'Bella',clip:'adv-bella-rainbow.mp4',text:'Wow, a rainbow road in the sky! Driving on colors and clouds feels like a dream!'}],
 [{ch:'Rusty',clip:'adv-rusty-town.mp4',text:'Howdy friends! Rusty here! In this town, I help everyone. A friend in need is a friend indeed!'},
  {ch:'Rusty',clip:'adv-rusty-farm.mp4',text:'Hello friends! Rusty here, at the green farm! Helping on the farm makes me happy!'},
  {ch:'Rusty',clip:'adv-rusty-beach.mp4',text:'Howdy friends! Rusty here at the sunny harbor! Boats, seagulls, and the big blue sea!'}],
 [{ch:'Rayo',clip:'adv-friends.mp4',text:'What a perfect day with my best friends! Remember kids, adventures are better together! Bye bye!'},
  {ch:'Rayo',clip:'adv-friends-race.mp4',text:'Racing with my best friends is the best fun ever! Remember kids, friends make every day special! Bye bye!'},
  {ch:'Rayo',clip:'adv-friends-picnic.mp4',text:'Picnic time with my best friends! Yummy sandwiches and lots of laughter! Friends make every day yummy! Bye bye!'}]
];
(function(){
  try{
    if(typeof advBuildLines==='function'){
      var prevBuild=advBuildLines;
      advBuildLines=function(){
        var ms=manifestSlots();
        if(ms){ ADV_SLOTS=ms; }
        ADV_SLOTS=ADV_SLOTS.map(function(s){
          var f=s.filter(function(o){ return advOk(o.clip); });
          return f.length?f:s;
        });
        return prevBuild();
      };
    }
  }catch(e){}
})();
SJ_CLIPS={
 Rayo:['adv-rayo-talk.mp4','adv-rayo-meadow.mp4','adv-rayo-city.mp4','adv-rayo-beach.mp4','adv-rayo-snow.mp4','adv-rayo-night.mp4','rayo-driving.mp4'].filter(advOk),
 Bella:['adv-bella-talk.mp4','adv-bella-beach.mp4','adv-bella-snowtalk.mp4','adv-bella-town.mp4','adv-bella-autumn.mp4','adv-bella-rainbow.mp4','bella-driving.mp4'].filter(advOk),
 Rusty:['adv-rusty-town.mp4','adv-rusty-farm.mp4','adv-rusty-beach.mp4','rusty-driving.mp4'].filter(advOk)
};
(function(){
  try{
    if(typeof realGetNameMap!=='function')return;
    var prevMap=realGetNameMap;
    var pools={
      Rayo:{talk:['rayo-talking.mp4','adv-rayo-talk.mp4','adv-rayo-meadow.mp4','adv-rayo-city.mp4'],drive:['rayo-driving.mp4','adv-rayo-beach.mp4','adv-rayo-snow.mp4','adv-rayo-night.mp4']},
      Bella:{talk:['bella-talking.mp4','adv-bella-talk.mp4','adv-bella-beach.mp4','adv-bella-snowtalk.mp4'],drive:['bella-driving.mp4','adv-bella-town.mp4','adv-bella-autumn.mp4','adv-bella-rainbow.mp4']},
      Rusty:{talk:['rusty-driving.mp4','adv-rusty-town.mp4','adv-rusty-farm.mp4','adv-rusty-beach.mp4'],drive:['rusty-driving.mp4','adv-rusty-town.mp4','adv-rusty-farm.mp4','adv-rusty-beach.mp4']}
    };
    function pickF(a){ var f=a.filter(advOk); var s=f.length?f:a; return s[Math.floor(Math.random()*s.length)]; }
    realGetNameMap=function(){
      var m=prevMap();
      try{
        if(_manifest){
          for(var i=0;i<_manifest.length;i++){ var e=_manifest[i]; var pp=pools[e.ch]; if(pp&&e.kind&&pp[e.kind]&&pp[e.kind].indexOf(e.clip)<0) pp[e.kind].push(e.clip); }
        }
        for(var k in m){ var p=pools[m[k].voice]; if(p){ m[k].clip=pickF(p.talk); m[k].clip2=pickF(p.drive); } }
      }catch(e){}
      return m;
    };
  }catch(e){}
})();
</script>
</body>"""
if '</body>' in html:
    html = html.replace('</body>', v439_script, 1)
    print('V439 script injected: True')
else:
    print('V439 script injected: False')

open(HP, 'w', encoding='utf-8').write(html)
print('HTML v439 done')
print('V439 ALL DONE')
