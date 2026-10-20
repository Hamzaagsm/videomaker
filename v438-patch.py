import re

# ============ JAVA ============
JP = 'android/app/src/main/java/com/hamza/videomaker/MainActivity.java'
java = open(JP, encoding='utf-8').read()

# JA: CLIPS_V5 me 3 naye scenes (meadow / beach / farm)
ja_anchor = '''                "adv-rayo-snow.mp4", "adv-bella-autumn.mp4",
                "adv-friends-race.mp4"
        };'''
ja_new = '''                "adv-rayo-snow.mp4", "adv-bella-autumn.mp4",
                "adv-friends-race.mp4",
                "adv-rayo-meadow.mp4", "adv-bella-beach.mp4",
                "adv-rusty-farm.mp4"
        };'''
print('JA anchor found:', ja_anchor in java)
java = java.replace(ja_anchor, ja_new, 1)

# JB: stamp helpers (areClipsReady se pehle)
jb_anchor = '''        @JavascriptInterface
        public boolean areClipsReady() {'''
jb_new = '''        // v4.38: clips version stamp - APK update par purani clips LAZMI replace hongi!
        private static final String CLIP_STAMP = "v438";

        private boolean clipsFresh() {
            try {
                File s = new File(clipDir(), "stamp.txt");
                if (!s.exists()) return false;
                java.io.FileInputStream in = new java.io.FileInputStream(s);
                byte[] b = new byte[32]; int n = in.read(b); in.close();
                return n > 0 && CLIP_STAMP.equals(new String(b, 0, n, "UTF-8").trim());
            } catch (Exception e) { return false; }
        }

        private void refreshBundledClips() {
            try {
                File dir = clipDir();
                String[] bundled = getAssets().list("clips");
                if (bundled != null) {
                    for (String b : bundled) {
                        if (!b.endsWith(".mp4")) continue;
                        File out = new File(dir, b);
                        try (java.io.InputStream in = getAssets().open("clips/" + b);
                             java.io.FileOutputStream fos = new java.io.FileOutputStream(out)) {
                            byte[] buf = new byte[8192]; int r;
                            while ((r = in.read(buf)) > 0) fos.write(buf, 0, r);
                            fos.flush();
                        } catch (Exception ignored) {}
                    }
                }
                java.io.FileOutputStream sf = new java.io.FileOutputStream(new File(dir, "stamp.txt"));
                sf.write(CLIP_STAMP.getBytes("UTF-8"));
                sf.close();
            } catch (Exception ignored) {}
        }

''' + jb_anchor
print('JB anchor found:', jb_anchor in java)
java = java.replace(jb_anchor, jb_new, 1)

# JC: areClipsReady me stamp check
jc_anchor = '''        public boolean areClipsReady() {
            File dir = clipDir();'''
jc_new = '''        public boolean areClipsReady() {
            if (!clipsFresh()) return false;
            File dir = clipDir();'''
print('JC anchor found:', jc_anchor in java)
java = java.replace(jc_anchor, jc_new, 1)

# JD: areAdvClipsReady me stamp check
jd_anchor = '''        public boolean areAdvClipsReady() {
            File dir = clipDir();'''
jd_new = '''        public boolean areAdvClipsReady() {
            if (!clipsFresh()) return false;
            File dir = clipDir();'''
print('JD anchor found:', jd_anchor in java)
java = java.replace(jd_anchor, jd_new, 1)

# JE: downloadClips ke shuru me refresh
je_anchor = '''        public void downloadClips() {
            runOnUiThread(() -> {
                try {
                    File dir = clipDir();'''
je_new = je_anchor + '''
                    if (!clipsFresh()) refreshBundledClips();'''
print('JE anchor found:', je_anchor in java)
java = java.replace(je_anchor, je_new, 1)

# JF: downloadAdvClips ke shuru me refresh
jf_anchor = '''        public void downloadAdvClips() {
            runOnUiThread(() -> {
                try {
                    File dir = clipDir();'''
jf_new = jf_anchor + '''
                    if (!clipsFresh()) refreshBundledClips();'''
print('JF anchor found:', jf_anchor in java)
java = java.replace(jf_anchor, jf_new, 1)

open(JP, 'w', encoding='utf-8').write(java)
print('JAVA v438 patched')

# ============ HTML ============
HP = 'android/app/src/main/assets/www/index.html'
html = open(HP, encoding='utf-8').read()

html = re.sub(r"APP_VER\s*=\s*[\"'][\d.]+[\"']", 'APP_VER="4.38"', html)
html = re.sub(r"v4\.\d+ MEER", "v4.38 MEER", html)

v438_script = """
<script>
// MEER v4.38: har hisse me 2 scenes - har video lazmi alag!
ADV_SLOTS=[
 [{ch:'Rayo',clip:'adv-rayo-talk.mp4',text:'Hi friends! I am Rayo! Welcome to Sunny Park! Today we are going on a brand new adventure!'},
  {ch:'Rayo',clip:'adv-rayo-meadow.mp4',text:'Hi friends! I am Rayo! Look at this flower meadow! Butterflies are dancing everywhere!'}],
 [{ch:'Bella',clip:'adv-bella-talk.mp4',text:'Hello everyone! I am Bella! Look at these beautiful flowers! I am so happy today!'},
  {ch:'Bella',clip:'adv-bella-beach.mp4',text:'Hello everyone! I am Bella! Welcome to the sunny beach! Can you hear the ocean waves?'}],
 [{ch:'Rayo',clip:'adv-rayo-beach.mp4',text:'Wow, the beach road! I can see the ocean! Racing by the sea is the best feeling ever!'},
  {ch:'Rayo',clip:'adv-rayo-snow.mp4',text:'Wow, snowy mountains! Everything is white and sparkling! Driving in the snow is a cool adventure!'}],
 [{ch:'Bella',clip:'adv-bella-town.mp4',text:'Look, the rainbow town! Balloons, colors, and yummy cakes! This place is magical!'},
  {ch:'Bella',clip:'adv-bella-autumn.mp4',text:'Look at the autumn forest! Red and orange leaves are falling everywhere! So beautiful!'}],
 [{ch:'Rusty',clip:'adv-rusty-town.mp4',text:'Howdy friends! Rusty here! In this town, I help everyone. A friend in need is a friend indeed!'},
  {ch:'Rusty',clip:'adv-rusty-farm.mp4',text:'Hello friends! Rusty here, at the green farm! Helping on the farm makes me happy!'}],
 [{ch:'Rayo',clip:'adv-friends.mp4',text:'What a perfect day with my best friends! Remember kids, adventures are better together! Bye bye!'},
  {ch:'Rayo',clip:'adv-friends-race.mp4',text:'Racing with my best friends is the best fun ever! Remember kids, friends make every day special! Bye bye!'}]
];
SJ_CLIPS={
 Rayo:['adv-rayo-talk.mp4','adv-rayo-meadow.mp4','adv-rayo-beach.mp4','adv-rayo-snow.mp4','rayo-driving.mp4'],
 Bella:['adv-bella-talk.mp4','adv-bella-beach.mp4','adv-bella-town.mp4','adv-bella-autumn.mp4','bella-driving.mp4'],
 Rusty:['adv-rusty-town.mp4','adv-rusty-farm.mp4','rusty-driving.mp4']
};
(function(){
  try{
    if(typeof realGetNameMap!=='function')return;
    var prevMap=realGetNameMap;
    var pools={
      Rayo:{talk:['rayo-talking.mp4','adv-rayo-talk.mp4','adv-rayo-meadow.mp4'],drive:['rayo-driving.mp4','adv-rayo-beach.mp4','adv-rayo-snow.mp4']},
      Bella:{talk:['bella-talking.mp4','adv-bella-talk.mp4','adv-bella-beach.mp4'],drive:['bella-driving.mp4','adv-bella-town.mp4','adv-bella-autumn.mp4']},
      Rusty:{talk:['rusty-driving.mp4','adv-rusty-town.mp4','adv-rusty-farm.mp4'],drive:['rusty-driving.mp4','adv-rusty-town.mp4','adv-rusty-farm.mp4']}
    };
    function pick(a){ return a[Math.floor(Math.random()*a.length)]; }
    realGetNameMap=function(){
      var m=prevMap();
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
</script>
</body>"""
if '</body>' in html:
    html = html.replace('</body>', v438_script, 1)
    print('V438 script injected: True')
else:
    print('V438 script injected: False')

open(HP, 'w', encoding='utf-8').write(html)
print('HTML v438 done')
print('V438 ALL DONE')
