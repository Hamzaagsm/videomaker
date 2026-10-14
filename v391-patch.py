# v3.91: New MEER icon (yellow Pixar car) + Pixar street background!
# (No PIL - just copy the 512px icon, Android scales it)
import os, shutil

def patch_all():
    # 1. ICON: Copy meer-icon-512.png to all mipmap folders
    # Android will scale it automatically. No PIL needed!
    icon_src = 'meer-icon-512.png'
    res_base = 'android/app/src/main/res'
    if os.path.exists(icon_src):
        print('Installing icon (Android will scale)...')
        for folder in ['mipmap-mdpi', 'mipmap-hdpi', 'mipmap-xhdpi', 'mipmap-xxhdpi', 'mipmap-xxxhdpi']:
            d = os.path.join(res_base, folder)
            os.makedirs(d, exist_ok=True)
            shutil.copy2(icon_src, os.path.join(d, 'ic_launcher.png'))
            shutil.copy2(icon_src, os.path.join(d, 'ic_launcher_round.png'))
            print(f'  {folder}/ic_launcher.png OK')
        print('ICON INSTALLED!')
    else:
        print('meer-icon-512.png not found, skipping icon')

    # 2. BACKGROUND: Set bg-pixar-street.jpg as default
    p = 'android/app/src/main/assets/www/index.html'
    if os.path.exists(p):
        h = open(p).read()
        orig = h
        old_bg = "const bgImg = (window.MEER_FIXED_BG_IMG || 'bg-hills.jpg');"
        new_bg = "const bgImg = (window.MEER_FIXED_BG_IMG || 'https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/bg-pixar-street.jpg'); // v3.91: Pixar street!"
        if old_bg in h:
            h = h.replace(old_bg, new_bg, 1)
            print('BACKGROUND SET TO PIXAR STREET!')
        else:
            print('Background anchor not found')
        import re
        h = re.sub(r"const APP_VER='3\.\d+'", "const APP_VER='3.91'", h)
        h = re.sub(r"v3\.\d+ MEER", "v3.91 MEER", h)
        if h != orig:
            open(p, 'w').write(h)
            print('HTML v3.91 saved')
    print('V3.91 PATCH DONE')

patch_all()
