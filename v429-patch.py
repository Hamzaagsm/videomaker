# v4.29: Fix footer version
def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    h = h.replace('v4.15 MEER', 'v4.29 MEER')
    h = h.replace("const APP_VER='4.28'", "const APP_VER='4.29'")
    if h != orig:
        open(p, 'w', encoding='utf-8').write(h)
    print('HTML V4.29 DONE')
def patch_java():
    print('JAVA V4.29 DONE')
patch_html()
patch_java()
print('V4.29 ALL DONE')













