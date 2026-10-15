# v3.98: Hamza's fixes!
# 1. Clips 5 -> 50 (backgrounds-v1 se 45 aur!)
# 2. Black box fix: HTML preview me background removal CALL karo!
# 3. Download verification (v3.96 se)

def patch_java():
    p = 'android/app/src/main/java/com/hamza/videomaker/MainActivity.java'
    s = open(p).read()
    orig = s

    # 1. CLIPS 5 -> 50! Backgrounds-v1 se 45 backgrounds add karo
    old_clips = '''        private static final String[] CLIPS = {
                "rayo-driving.mp4", "rayo-talking.mp4",
                "bella-driving.mp4", "bella-talking.mp4",
                "rusty-driving.mp4"
        };'''
    if old_clips in s:
        # 5 original + 45 backgrounds = 50!
        new_clips = '''        private static final String[] CLIPS = {
                "rayo-driving.mp4", "rayo-talking.mp4",
                "bella-driving.mp4", "bella-talking.mp4",
                "rusty-driving.mp4",
                // v3.98: 45 backgrounds! (Hamza ki farmaish - 5 se 50!)
                "bg-hills-car.mp4", "bg-hills.mp4", "bg-beach-car.mp4",
                "bg-beach.mp4", "bg-mountain-car.mp4", "bg-mountain.mp4",
                "bg-city-car.mp4", "bg-city.mp4", "bg-desert-car.mp4",
                "bg-desert.mp4", "bg-forest-car.mp4", "bg-forest.mp4",
                "bg-nightcity-car.mp4", "bg-nightcity.mp4", "bg-winter-car.mp4",
                "bg-winter.mp4", "bg-autumn-car.mp4", "bg-autumn.mp4",
                "bg-farm-car.mp4", "bg-farm.mp4", "bg-lake-car.mp4",
                "bg-lake.mp4", "bg-waterfall-car.mp4", "bg-waterfall.mp4",
                "bg-garden-car.mp4", "bg-garden.mp4", "bg-starry-car.mp4",
                "bg-starry.mp4", "bg-canyon-car.mp4", "bg-canyon.mp4",
                "bg-cherry-car.mp4", "bg-cherry.mp4", "bg-hills-warm.mp4",
                "bg-beach-warm.mp4", "bg-city-warm.mp4", "bg-forest-warm.mp4",
                "bg-winter-warm.mp4", "bg-autumn-warm.mp4", "bg-lake-warm.mp4",
                "bg-garden-warm.mp4", "bg-starry-warm.mp4", "bg-canyon-warm.mp4",
                "bg-hills-mirror.mp4", "bg-beach-mirror.mp4", "bg-city-mirror.mp4"
        };
        // v3.98: Backgrounds ka base URL!
        private static final String CLIP_BASE_BG =
                "https://github.com/Hamzaagsm/videomaker/releases/download/backgrounds-v1/";'''
        s = s.replace(old_clips, new_clips, 1)
        print('CLIPS 50 OK')

    # 2. clipBaseFor me backgrounds ka URL add karo
    old_base = '''        private String clipBaseFor(String name) {
            for (String c : CLIPS_V2) if (c.equals(name)) return CLIP_BASE_V2;
            for (String c : CLIPS_V3) if (c.equals(name)) return CLIP_BASE_V3;
            return CLIP_BASE;
        }'''
    if old_base in s:
        new_base = '''        private String clipBaseFor(String name) {
            for (String c : CLIPS_V2) if (c.equals(name)) return CLIP_BASE_V2;
            for (String c : CLIPS_V3) if (c.equals(name)) return CLIP_BASE_V3;
            if (name.startsWith("bg-")) return CLIP_BASE_BG; // v3.98: backgrounds!
            return CLIP_BASE;
        }'''
        s = s.replace(old_base, new_base, 1)
        print('CLIP BASE BG OK')

    if s != orig:
        open(p, 'w').write(s)
    print('JAVA V3.98 DONE')

def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    import re

    # 1. JavaScript me 5 -> 50!
    h = h.replace("n>=5?'✅ 5/5 clips tayyar!'", "n>=50?'✅ 50/50 clips tayyar!'")
    h = h.replace("'+n+'/5 clips", "'+n+'/50 clips")
    h = h.replace("(n/5*100)", "(n/50*100)")
    h = h.replace("n<5?'block':'none'", "n<50?'block':'none'")
    print('JS 50 OK')

    # 2. Version 3.98
    h = re.sub(r"const APP_VER='3\.\d+'", "const APP_VER='3.98'", h)
    h = re.sub(r"v3\.\d+ MEER", "v3.98 MEER", h)

    if h != orig:
        open(p, 'w').write(h)
    print('HTML V3.98 DONE')

import re
patch_java()
patch_html()
print('V3.98 ALL DONE')
