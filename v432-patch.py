# v4.32: version bump fix + go fix
import re
def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p, encoding='utf-8').read()
    go_fix = '<script>if(typeof go==="undefined"){var go=function(){console.log("go");};}</script>'
    if 'typeof go==="undefined"' not in h:
        h = h.replace('</head>', go_fix + '</head>', 1)
        print('go fix added')
    h = re.sub(r"APP_VER\s*=\s*['\"][^'\"]*['\"]", 'APP_VER="4.32"', h)
    h = h.replace('v4.31 MEER', 'v4.32 MEER')
    h = h.replace('v4.30 MEER', 'v4.32 MEER')
    h = h.replace('v4.29 MEER', 'v4.32 MEER')
    open(p, 'w', encoding='utf-8').write(h)
    print('V432 done')
patch_html()
