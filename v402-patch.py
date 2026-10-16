# v4.02: Clips 50 -> 5 wapas! (backgrounds optional!)
# 45 backgrounds download nahi ho rahe thay, video ruk gayi thi.
# Ab sirf 5 zaroori clips chahiye, backgrounds optional!

def patch_java():
    p = 'android/app/src/main/java/com/hamza/videomaker/MainActivity.java'
    s = open(p).read()
    orig = s

    # areClipsReady: sirf 5 main clips check karo (backgrounds optional!)
    # Pehle wala: saare CLIPS (50) check karta tha
    old_ready = '''        @JavascriptInterface
        public boolean areClipsReady() {
            try {
                File dir = clipDir();
                for (String name : CLIPS) {
                    if (!clipOk(new File(dir, name))) return false;
                }
                return true;
            } catch (Exception e) { return false; }
        }'''

    new_ready = '''        @JavascriptInterface
        public boolean areClipsReady() {
            try {
                // v4.02: Sirf 5 MAIN clips zaroori! (backgrounds optional!)
                String[] MAIN_CLIPS = {"rayo-driving.mp4", "rayo-talking.mp4",
                    "bella-driving.mp4", "bella-talking.mp4", "rusty-driving.mp4"};
                File dir = clipDir();
                for (String name : MAIN_CLIPS) {
                    if (!clipOk(new File(dir, name))) return false;
                }
                return true;
            } catch (Exception e) { return false; }
        }'''

    if old_ready in s and 'v4.02: Sirf 5 MAIN clips' not in s:
        s = s.replace(old_ready, new_ready, 1)
        print('READY FIX OK')

    # getDownloadedCount: 5 se count karo
    old_count = '''        @JavascriptInterface
        public int getDownloadedCount() {
            try {
                File dir = clipDir();
                int n = 0;
                for (String name : CLIPS) {
                    if (clipOk(new File(dir, name))) n++;
                }
                return n;
            } catch (Exception e) { return 0; }
        }'''

    # Ise rehne do - 50 me se kitne hue ye dikhana theek hai

    if s != orig:
        open(p, 'w').write(s)
    print('JAVA V4.02 DONE')

def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    import re

    # JS me 50 -> 5 wapas! (sirf zaroori clips)
    # "n>=50" -> "n>=5"
    if "n>=50?'✅ 50/50 clips tayyar!'" in h:
        h = h.replace("n>=50?'✅ 50/50 clips tayyar!'", "n>=5?'✅ 5/5 clips tayyar! (backgrounds optional)'")
        print('JS READY OK')
    if "'+n+'/50 clips" in h:
        h = h.replace("'+n+'/50 clips", "'+n+'/5 clips'")
        print('JS COUNT OK')
    if "(n/50*100)" in h:
        h = h.replace("(n/50*100)", "(n/5*100)")
        print('JS PROGRESS OK')
    if "n<50?'block':'none'" in h:
        h = h.replace("n<50?'block':'none'", "n<5?'block':'none'")
        print('JS BLOCK OK')

    # Version 4.02
    h = re.sub(r"const APP_VER='4\.01'", "const APP_VER='4.02'", h)
    h = re.sub(r"v4\.01 MEER", "v4.02 MEER", h)

    if h != orig:
        open(p, 'w').write(h)
    print('HTML V4.02 DONE')

import re
patch_java()
patch_html()
print('V4.02 ALL DONE')
