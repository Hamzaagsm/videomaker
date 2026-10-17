# v4.17: Hide Motu section with CORRECT ID
def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    import re
    hide_css = '<style>#s-motu { display: none !important; }</style>'
    h = re.sub(r'<style>#motuStudio[^<]*</style>', '', h)
    h = re.sub(r'<style>#s-motu[^<]*</style>', '', h)
    if '<head>' in h:
        h = h.replace('<head>', '<head>' + hide_css, 1)
        print('MOTU HIDE OK')
    h = re.sub(r"const APP_VER\s*=\s*['\"]4\.\d+['\"]", "const APP_VER='4.17'", h)
    if h != orig:
        open(p, 'w', encoding='utf-8').write(h)
    print('HTML V4.17 DONE')
def patch_java():
    print('JAVA V4.17 DONE')
patch_html()
patch_java()
print('V4.17 ALL DONE')
