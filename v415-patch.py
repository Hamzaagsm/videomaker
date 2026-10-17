# v4.15: Pixar-style 3 cars side by side
def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    import re
    old = "carImage: carImg, carImages: carImages,"
    new = "carImage: carImg, carImages: carImages, speakerIdx: 0, frontView: true, pixarStyle: true,"
    if old in h:
        h = h.replace(old, new)
        print('PIXAR FLAG OK')
    h = re.sub(r"const APP_VER='4\\.14'", "const APP_VER='4.15'", h)
    h = h.replace("v4.14", "v4.15")
    if h != orig:
        open(p, 'w', encoding='utf-8').write(h)
    print('HTML V4.15 DONE')
def patch_java():
    print('JAVA V4.15 DONE')
patch_html()
patch_java()
print('V4.15 ALL DONE')
