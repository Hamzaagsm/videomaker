# v3.92: Fix addColorStop undefined error (gradient fallback bug)
def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h

    # Fix: Make gradient fallback defensive
    # Old: const bg=bgs[Math.floor(kidRand(seed,1)*bgs.length)];
    #      g.addColorStop(0,bg[0]);g.addColorStop(1,bg[1]);
    # New: Check if bg exists, use default if not
    old = "  const bg=bgs[Math.floor(kidRand(seed,1)*bgs.length)];\n  const g=cx.createLinearGradient(0,0,0,H);\n  g.addColorStop(0,bg[0]);g.addColorStop(1,bg[1]);"
    if old in h:
        new = """  let bg=bgs[Math.floor(kidRand(seed,1)*bgs.length)];
  if(!bg||!bg[0]||!bg[1])bg=['#ff9a9e','#fecfef']; // v3.92: fallback if undefined!
  const g=cx.createLinearGradient(0,0,0,H);
  g.addColorStop(0,bg[0]);g.addColorStop(1,bg[1]);"""
        h = h.replace(old, new, 1)
        print('GRADIENT FIX OK')

    # Version 3.92
    import re
    h = re.sub(r"const APP_VER='3\.\d+'", "const APP_VER='3.92'", h)
    h = re.sub(r"v3\.\d+ MEER", "v3.92 MEER", h)

    if h != orig:
        open(p, 'w').write(h)
    print('HTML V3.92 DONE')

import re
patch_html()
print('V3.92 ALL DONE')
