# v4.14: Front-facing driving cars with dialogue
def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    import re
    old_seg = "carImage: carImg, carImages: carImages,"
    new_seg = "carImage: carImg, carImages: carImages, speakerIdx: 0, frontView: true,"
    if old_seg in h:
        h = h.replace(old_seg, new_seg)
        print('SPEAKER OK')
    h = re.sub(r"const APP_VER='4\.13'", "const APP_VER='4.14'", h)
    h = h.replace("v4.13", "v4.14")
    if h != orig:
        open(p, 'w', encoding='utf-8').write(h)
    print('HTML V4.14 DONE')
def patch_java():
    print('JAVA V4.14 DONE')
patch_html()
patch_java()
print('V4.14 ALL DONE')
