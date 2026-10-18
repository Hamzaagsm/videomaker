# v4.20: Proper fixes
def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    import re
    if 'v4.20: bike filter' not in h:
        m = re.search(r"(ONLINE_CARS\s*=\s*[^;]+;)", h)
        if m:
            old = m.group(1)
            new = old + "\n    // v4.20: bike filter backup\n    try{ONLINE_CARS=ONLINE_CARS.filter(function(c){return !c.img||c.img.indexOf('-bike.png')===-1;});}catch(e){}"
            h = h.replace(old, new, 1)
            print('JS BIKE FILTER OK')
    h = re.sub(r"const APP_VER\s*=\s*['\"]4\.\d+['\"]", "const APP_VER='4.20'", h)
    if h != orig:
        open(p, 'w', encoding='utf-8').write(h)
    print('HTML V4.20 DONE')
def patch_java():
    p = 'android/app/src/main/java/com/hamza/videomaker/MainActivity.java'
    j = open(p).read()
    orig = j
    import re
    bg_pat = r'Bitmap\s+bgBmp\s*=\s*loadAssetBitmap\("backgrounds/"\s*\+\s*bgImgName\)\s*;'
    m = re.search(bg_pat, j)
    if m:
        old = m.group(0)
        new = 'Bitmap bgBmp = null;\n            if (bgImgName != null && bgImgName.startsWith("http")) {\n                try { bgBmp = downloadBitmap(bgImgName); } catch (Exception e) { bgBmp = null; }\n            }\n            if (bgBmp == null) bgBmp = loadAssetBitmap("backgrounds/" + bgImgName);'
        j = j.replace(old, new, 1)
        print('BG HTTP OK')
    if 'float scroll = 0;' in j:
        j = j.replace('float scroll = 0;', 'float scroll = (frameNum * 8) % W; // v4.20', 1)
        print('SCROLL OK')
    if j != orig:
        open(p, 'w', encoding='utf-8').write(j)
    print('JAVA V4.20 DONE')
patch_html()
patch_java()
print('V4.20 ALL DONE')
