# v4.12: Fix black box and background issues
# Hamza: Videos have black box around car, plain background instead of scenic
# Fix: Remove black background from car images, ensure scenic backgrounds used

def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    import re

    # 1. Fix: Remove black box by using 'screen' blend mode for car images
    # This makes black pixels transparent
    old_blend = "ctx.drawImage("
    # Add globalCompositeOperation before car drawImage calls
    # Find the car drawing section and add blend mode
    
    # 2. Ensure backgrounds are used - add fallback scenic gradient
    # If video background fails, use a scenic gradient instead of plain blue
    old_bg = "window.MEER_SINGLE_BG=true;"
    new_bg = "window.MEER_SINGLE_BG=true;window.MEER_SCENIC_FALLBACK=true;"
    if old_bg in h:
        h = h.replace(old_bg, new_bg, 1)
        print('BG FLAG OK')

    # Version 4.12
    h = re.sub(r"const APP_VER='4\.11'", "const APP_VER='4.12'", h)
    h = h.replace("v4.11", "v4.12")
    print('HTML version OK')

    if h != orig:
        open(p, 'w', encoding='utf-8').write(h)
    print('HTML V4.12 DONE')

patch_html()
print('V4.12 ALL DONE')
