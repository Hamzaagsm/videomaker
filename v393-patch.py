# v3.93: Fix REAL addColorStop bug (th.c1 undefined in drawBG)
def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h

    # REAL BUG: drawBG(t,th) is called with {id:S.theme} (no c1/c2!)
    # Line: g.addColorStop(0,th.c1);g.addColorStop(1,th.c2); -> th.c1 is undefined!
    # Fix: Use safe fallback colors if th.c1/c2 missing
    old = "function drawBG(t,th){\n  const W=S.VW,H=S.VH;\n  const g=cx.createLinearGradient(0,0,0,H);g.addColorStop(0,th.c1);g.addColorStop(1,th.c2);"
    if old in h:
        new = """function drawBG(t,th){
  const W=S.VW,H=S.VH;
  const _c1=(th&&th.c1)||'#0d1b2a',_c2=(th&&th.c2)||'#1b3a5c'; // v3.93: safe fallback!
  const g=cx.createLinearGradient(0,0,0,H);g.addColorStop(0,_c1);g.addColorStop(1,_c2);"""
        h = h.replace(old, new, 1)
        print('DRAWBG FIX OK!')
    else:
        print('drawBG anchor not found - trying alternative')
        # Try without newline
        old2 = "g.addColorStop(0,th.c1);g.addColorStop(1,th.c2);"
        if old2 in h:
            new2 = "g.addColorStop(0,(th&&th.c1)||'#0d1b2a');g.addColorStop(1,(th&&th.c2)||'#1b3a5c'); // v3.93 fix"
            h = h.replace(old2, new2, 1)
            print('DRAWBG FIX OK (alt)!')

    # Version 3.93
    import re
    h = re.sub(r"const APP_VER='3\.\d+'", "const APP_VER='3.93'", h)
    h = re.sub(r"v3\.\d+ MEER", "v3.93 MEER", h)

    if h != orig:
        open(p, 'w').write(h)
    print('HTML V3.93 DONE')

import re
patch_html()
print('V3.93 ALL DONE')
