# v3.91: New MEER icon (yellow Pixar car) + Pixar street background!
import os, shutil
from PIL import Image

def patch_all():
    # 1. ICON: meer-icon-512.png -> mipmap folders
    icon_src = 'meer-icon-512.png'
    if os.path.exists(icon_src):
        print('Icon found, installing...')
        # Android mipmap sizes
        sizes = {
            'mipmap-mdpi': 48,
            'mipmap-hdpi': 72,
            'mipmap-xhdpi': 96,
            'mipmap-xxhdpi': 144,
            'mipmap-xxxhdpi': 192,
        }
        base = 'android/app/src/main/res'
        img = Image.open(icon_src)
        for folder, size in sizes.items():
            d = os.path.join(base, folder)
            os.makedirs(d, exist_ok=True)
            # Resize and save as ic_launcher.png
            resized = img.resize((size, size), Image.LANCZOS)
            out = os.path.join(d, 'ic_launcher.png')
            resized.save(out, 'PNG')
            print(f'  {folder}/ic_launcher.png ({size}x{size}) OK')
        # Also round icon
        for folder, size in sizes.items():
            d = os.path.join(base, folder)
            out = os.path.join(d, 'ic_launcher_round.png')
            resized = img.resize((size, size), Image.LANCZOS)
            resized.save(out, 'PNG')
        print('ICON INSTALLED!')
    else:
        print('Icon not found, skipping')

    # 2. BACKGROUND: Set bg-pixar-street.jpg as default
    p = 'android/app/src/main/assets/www/index.html'
    if os.path.exists(p):
        h = open(p).read()
        orig = h
        # v3.91: Default background = Pixar street!
        old_bg = "const bgImg = (window.MEER_FIXED_BG_IMG || 'bg-hills.jpg');"
        new_bg = "const bgImg = (window.MEER_FIXED_BG_IMG || 'https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/bg-pixar-street.jpg'); // v3.91: Pixar street!"
        if old_bg in h:
            h = h.replace(old_bg, new_bg, 1)
            print('BACKGROUND SET TO PIXAR STREET!')
        else:
            print('Background anchor not found')
        # Version 3.91
        import re
        h = re.sub(r"const APP_VER='3\.\d+'", "const APP_VER='3.91'", h)
        h = re.sub(r"v3\.\d+ MEER", "v3.91 MEER", h)
        if h != orig:
            open(p, 'w').write(h)
            print('HTML v3.91 saved')
    print('V3.91 PATCH DONE')

patch_all()
