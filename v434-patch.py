# v4.34: bundle clips in APK + remove v428 bypass
import re

JAVA_COPY = """
                    try {
                        String[] bundled = getAssets().list("clips");
                        if (bundled != null) {
                            for (String an : bundled) {
                                File dest = new File(dir, an);
                                if (!clipOk(dest)) {
                                    java.io.InputStream cin = getAssets().open("clips/" + an);
                                    java.io.FileOutputStream cout = new java.io.FileOutputStream(dest);
                                    byte[] cbuf = new byte[8192];
                                    int cr;
                                    while ((cr = cin.read(cbuf)) != -1) cout.write(cbuf, 0, cr);
                                    cout.flush(); cout.close(); cin.close();
                                }
                            }
                        }
                    } catch (Exception ignored2) {}
"""

def patch_java():
    p = 'android/app/src/main/java/com/hamza/videomaker/MainActivity.java'
    h = open(p, encoding='utf-8').read()
    if 'String[] bundled' in h:
        print('java already patched')
        return
    old = 'public void downloadClips() {\n            runOnUiThread(() -> {\n                try {\n                    File dir = clipDir();'
    if old not in h:
        print('JAVA ANCHOR NOT FOUND')
        return
    h = h.replace(old, old + JAVA_COPY, 1)
    open(p, 'w', encoding='utf-8').write(h)
    print('JAVA v434 patched')

def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p, encoding='utf-8').read()
    override = '<script>if(typeof getDownloadedCount!=="undefined"){var _origGDC=getDownloadedCount;getDownloadedCount=function(){return 5;};}</script>'
    if override in h:
        h = h.replace(override, '')
        print('v428 bypass removed')
    h = re.sub(r"APP_VER\s*=\s*['\"][^'\"]*['\"]", 'APP_VER="4.34"', h)
    for v in ['v4.33 MEER','v4.32 MEER','v4.31 MEER','v4.30 MEER','v4.29 MEER']:
        h = h.replace(v, 'v4.34 MEER')
    open(p, 'w', encoding='utf-8').write(h)
    print('HTML v434 done')

patch_java()
patch_html()
print('V434 ALL DONE')
