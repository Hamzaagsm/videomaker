# v4.30: Fix $ is not defined error
def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    # Define $ fallback if jQuery not loaded - prevents ReferenceError
    fix = '<script>if(typeof $==="undefined"){var $=function(s){return document.querySelector(s);};}</script>'
    if 'typeof $==="undefined"' not in h:
        h = h.replace('</head>', fix + '</head>', 1)
        print('V430 $ fix ADDED')
    h = h.replace("const APP_VER='4.29'", "const APP_VER='4.30'")
    if h != orig:
        open(p, 'w', encoding='utf-8').write(h)
    print('HTML V4.30 DONE')
def patch_java():
    print('JAVA V4.30 DONE')
patch_html()
patch_java()
print('V4.30 ALL DONE')
