# v4.16: REAL FIX
def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    import re
    hide_css = '<style>#motuStudio { display: none !important; }</style>'
    if '<head>' in h:
        h = h.replace('<head>', '<head>' + hide_css, 1)
    h = re.sub(r"const APP_VER\s*=\s*['\"]4\.\d+['\"]", "const APP_VER='4.16'", h)
    if h != orig:
        open(p, 'w', encoding='utf-8').write(h)
    print('HTML V4.16 DONE')
def patch_java():
    p = 'android/app/src/main/java/com/hamza/videomaker/MainActivity.java'
    j = open(p).read()
    orig = j
    import re
    bg_pattern = r'Bitmap\s+bgBmp\s*=\s*loadAssetBitmap\([^)]+\)\s*;'
    m = re.search(bg_pattern, j)
    if m:
        old_bg = m.group(0)
        new_bg = 'Bitmap bgBmp = null;\n            if (bgImgName.startsWith("http")) { try { bgBmp = downloadBitmap(bgImgName); } catch (Exception e) { bgBmp = null; } }\n            if (bgBmp == null) bgBmp = loadAssetBitmap("backgrounds/" + bgImgName);'
        j = j.replace(old_bg, new_bg, 1)
        print('BG HTTP OK')
    if j != orig:
        open(p, 'w', encoding='utf-8').write(j)
    print('JAVA V4.16 DONE')
patch_html()
patch_java()
print('V4.16 ALL DONE')
