# v3.94: Kids Video (poem) - Car on ROAD! (not field)
# + Pixar street background for kidFrame
def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h

    # 1. Preload Pixar street into AIBG
    # Find: function aiLoadImages(){
    # Add street preload after the bgs loop
    old_load = "  for(const k in bgs){const im=new Image();im.src=AIIMGDATA[bgs[k]];AIBG[k]=im;}"
    if old_load in h:
        new_load = old_load + "\n  // v3.94: Pixar street for Kids Video road style!\n  {const im=new Image();im.src='https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/bg-pixar-street.jpg';AIBG['street']=im;}"
        h = h.replace(old_load, new_load, 1)
        print('STREET PRELOAD OK')

    # 2. kidFrame: Use street background (road!) instead of park/town
    # Old: const aibgs=['park','town','beach','night','race','day'];
    old_aibgs = "  const aibgs=['park','town','beach','night','race','day'];"
    if old_aibgs in h:
        # v3.94: ALWAYS use street (road) for Kids Video!
        new_aibgs = "  const aibgs=['street']; // v3.94: ROAD only! (Hamza: car road pe chalni chahye)"
        h = h.replace(old_aibgs, new_aibgs, 1)
        print('KIDFRAME STREET OK')

    # 3. Remove grass (green field) - replace with road
    # The grass is drawn as fillRect with green. We'll keep it but it will be covered by street image.
    # Actually, the street image covers the top 75%, grass is at bottom 82-100%.
    # For road style, we want the road to go to the bottom. Let's adjust.
    # Simpler: Make the street image cover more.
    # The current: const sc=Math.max(W/iw,H*0.75/ih),dw=iw*sc,dh=ih*sc; cx.drawImage(aibg,(W-dw)/2,0,dw,dh);
    # Change H*0.75 to H*1.0 to cover full height
    old_draw = "    const sc=Math.max(W/iw,H*0.75/ih),dw=iw*sc,dh=ih*sc;"
    if old_draw in h:
        new_draw = "    const sc=Math.max(W/iw,H*1.0/ih),dw=iw*sc,dh=ih*sc; // v3.94: full height road!"
        h = h.replace(old_draw, new_draw, 1)
        print('STREET FULL HEIGHT OK')

    # Version 3.94
    import re
    h = re.sub(r"const APP_VER='3\.\d+'", "const APP_VER='3.94'", h)
    h = re.sub(r"v3\.\d+ MEER", "v3.94 MEER", h)

    if h != orig:
        open(p, 'w').write(h)
    print('HTML V3.94 DONE')

import re
patch_html()
print('V3.94 ALL DONE')
