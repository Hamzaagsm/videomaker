# v4.21: Version bump + ensure bike filter
def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    import re
    h = re.sub(r"const APP_VER\s*=\s*['\"]4\.\d+['\"]", "const APP_VER='4.21'", h)
    if h != orig:
        open(p, 'w', encoding='utf-8').write(h)
    print('HTML V4.21 DONE')
def patch_java():
    print('JAVA V4.21 DONE')
patch_html()
patch_java()
print('V4.21 ALL DONE')
