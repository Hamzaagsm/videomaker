# v4.05: Fix the JavaScript syntax error (em-dash outside string)
# The v4.02 patch broke a string by leaving — outside the quotes

def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    import re

    # Fix the broken lines: text was left outside the string by v4.02 patch
    # Broken 1: '⬇️ '+n+'/5 clips' — "Clips Download Karo" dabao';
    # Broken 2: '⬇️ '+n+'/5 clips' download ho rahe...';
    fixes = [
        ("'⬇️ '+n+'/5 clips' — \"Clips Download Karo\" dabao'",
         "'⬇️ '+n+'/5 clips — Clips Download Karo dabao'"),
        ("'⬇️ '+n+'/5 clips' download ho rahe...'",
         "'⬇️ '+n+'/5 clips download ho rahe...'"),
    ]
    for broken, fixed in fixes:
        if broken in h:
            h = h.replace(broken, fixed)
            print(f'FIX OK: {broken[:30]}...')

    # Version 4.05
    h = re.sub(r"const APP_VER='4\.04'", "const APP_VER='4.05'", h)
    h = re.sub(r"v4\.04", "v4.05", h)

    if h != orig:
        open(p, 'w').write(h)
    print('HTML V4.05 DONE')

patch_html()
print('V4.05 ALL DONE')
