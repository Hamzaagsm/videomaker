# v4.33: fix $ already declared error - remove var $ and use window.$
import re
def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p, encoding='utf-8').read()
    # Remove the bad v430 $ script (var $ causes redeclaration error)
    bad = '<script>if(typeof $==="undefined"){var $=function(s){return document.querySelector(s);};}</script>'
    if bad in h:
        h = h.replace(bad, '')
        print('removed bad var $ script')
    # Remove the var go script from v431/v432
    badgo = '<script>if(typeof go==="undefined"){var go=function(){console.log("go called");};}</script>'
    if badgo in h:
        h = h.replace(badgo, '')
        print('removed var go script')
    badgo2 = '<script>if(typeof go==="undefined"){var go=function(){console.log("go");};}</script>'
    if badgo2 in h:
        h = h.replace(badgo2, '')
        print('removed var go script 2')
    # Add SAFE versions using window assignment (no var, no conflict)
    safe = '<script>window.$=window.$||function(s){return document.querySelector(s);};window.go=window.go||function(){console.log("go");};</script>'
    if 'window.$=window.$' not in h:
        h = h.replace('</head>', safe + '</head>', 1)
        print('safe window shim added')
    h = re.sub(r"APP_VER\s*=\s*['\"][^'\"]*['\"]", 'APP_VER="4.33"', h)
    h = h.replace('v4.32 MEER', 'v4.33 MEER')
    h = h.replace('v4.31 MEER', 'v4.33 MEER')
    open(p, 'w', encoding='utf-8').write(h)
    print('V433 done')
patch_html()
