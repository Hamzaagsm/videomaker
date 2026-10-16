# v4.01: Fix clips download stuck at 5/50!
# downloadClips() used CLIP_BASE directly instead of clipBaseFor()
# So bg-* files tried wrong URL and failed. Now uses clipBaseFor()!

def patch_java():
    p = 'android/app/src/main/java/com/hamza/videomaker/MainActivity.java'
    s = open(p).read()
    orig = s

    # Fix: downloadClips me CLIP_BASE ki jagah clipBaseFor(name) use karo!
    old_dl = 'new DownloadManager.Request(Uri.parse(CLIP_BASE + name));'
    if old_dl in s and 'v4.01: clipBaseFor fix' not in s:
        new_dl = 'new DownloadManager.Request(Uri.parse(clipBaseFor(name))); // v4.01: clipBaseFor fix! (bg-* sahi URL se!)'
        s = s.replace(old_dl, new_dl, 1)
        print('DOWNLOAD FIX OK')

    # Also fix getClipPath if it has the same issue
    old_path = 'return new File(clipDir(), name).getAbsolutePath();'
    # Check if getClipPath uses CLIP_BASE (it shouldn't for local path, skip)

    if s != orig:
        open(p, 'w').write(s)
    print('JAVA V4.01 DONE')

def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    import re

    # Version 4.01
    h = re.sub(r"const APP_VER='4\.00'", "const APP_VER='4.01'", h)
    h = re.sub(r"v4\.00 MEER", "v4.01 MEER", h)

    if h != orig:
        open(p, 'w').write(h)
    print('HTML V4.01 DONE')

import re
patch_java()
patch_html()
print('V4.01 ALL DONE')
