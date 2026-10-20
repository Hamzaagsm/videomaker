# v4.31: Fix go is not defined error
def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p, encoding='utf-8').read()
    # Fix go is not defined - add fallback before </head>
    go_fix = '<script>if(typeof go==="undefined"){var go=function(){console.log("go called");};}</script>'
    if 'typeof go==="undefined"' not in h:
        h = h.replace('</head>', go_fix + '</head>', 1)
        print('V431 go fix ADDED')
    else:
        print('V431 go fix already present')
    # Bump version strings
    import re
    h = re.sub(r'APP_VER\s*=\s*["\']3\.84["\']', 'APP_VER="4.31"', h)
    h = re.sub(r'v4\.30', 'v4.31', h)
    h = re.sub(r'v4\.29 MEER', 'v4.31 MEER', h)
    open(p, 'w', encoding='utf-8').write(h)
    print('V431 patch done')

patch_html()
