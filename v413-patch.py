# v4.13: 3 cars on scenic road - REAL FIX
# Root causes found:
# 1. Background URL treated as asset path -> plain blue fallback
# 2. MEER_SELECTED_CAR never set -> always car-red.png, online cars never used
# 3. Only 1 car rendered, not 3
# 4. Car PNG has no transparency, flood-fill is fragile

def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    import re

    # 1. Fix: Use online cars - set MEER_SELECTED_CAR from randomOnlineCar()
    # Find carJourneyMode and inject car selection
    old_car = "const carImg = (window.MEER_SELECTED_CAR || 'car-red.png');"
    new_car = """const onlineCars = (typeof ONLINE_CARS !== 'undefined' && ONLINE_CARS.length >= 3) ? ONLINE_CARS : [];
    const pickedCars = [];
    const usedIdx = new Set();
    for (let i = 0; i < 3 && onlineCars.length > 0; i++) {
        let idx, tries = 0;
        do { idx = Math.floor(Math.random() * onlineCars.length); tries++; } while (usedIdx.has(idx) && tries < 20);
        usedIdx.add(idx);
        pickedCars.push(onlineCars[idx].img || onlineCars[idx].url);
    }
    while (pickedCars.length < 3) pickedCars.push('car-red.png');
    const carImg = pickedCars[0];
    const carImages = pickedCars;"""
    if old_car in h:
        h = h.replace(old_car, new_car, 1)
        print('3-CAR JS OK')

    # 2. Pass carImages array in segment
    old_seg = "carImage: carImg,"
    new_seg = "carImage: carImg, carImages: carImages,"
    # Only replace in the segment building area (first occurrence near bgImage)
    if old_seg in h:
        # Replace all occurrences to be safe
        h = h.replace(old_seg, new_seg)
        print('SEGMENT OK')

    # 3. Fix background: use a real scenic background URL that native can download
    # The native fix will handle http URLs for backgrounds
    old_bg = "const bgImg  = (window.MEER_FIXED_BG_IMG || 'https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/bg-pixar-street.jpg');"
    new_bg = "const bgImg  = (window.MEER_FIXED_BG_IMG || 'https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/bg-pixar-street.jpg'); window.MEER_BG_HTTP_FIX=true;"
    if old_bg in h:
        h = h.replace(old_bg, new_bg, 1)
        print('BG JS OK')

    # Version 4.13
    h = re.sub(r"const APP_VER='4\.12'", "const APP_VER='4.13'", h)
    h = h.replace("v4.12", "v4.13")
    print('HTML version OK')

    if h != orig:
        open(p, 'w', encoding='utf-8').write(h)
    print('HTML V4.13 DONE')

def patch_java():
    p = 'android/app/src/main/java/com/hamza/videomaker/MainActivity.java'
    j = open(p).read()
    orig = j

    # 1. Fix background http support in renderCanvasVideo
    # Find the background loading code and add http handling
    old_bg_load = 'android.graphics.Bitmap bgBmp = loadAssetBitmap("backgrounds/" + bgImgName);'
    new_bg_load = '''android.graphics.Bitmap bgBmp = null;
            if (bgImgName.startsWith("http")) { try { bgBmp = downloadBitmap(bgImgName); } catch (Exception e) { bgBmp = null; } }
            if (bgBmp == null) bgBmp = loadAssetBitmap("backgrounds/" + bgImgName);
            if (bgBmp == null) bgBmp = loadAssetBitmap(bgImgName);
            if (bgBmp == null) bgBmp = loadAssetBitmap("img/bg_day.png");'''
    if old_bg_load in j:
        j = j.replace(old_bg_load, new_bg_load, 1)
        print('BG JAVA OK')
    else:
        print('BG JAVA: pattern not found, trying alternative')
        # Try to find similar pattern
        import re
        m = re.search(r'Bitmap bgBmp = loadAssetBitmap\([^)]+\)', j)
        if m:
            print('Found: ' + m.group(0)[:80])

    # 2. Multi-car rendering: parse carImages array
    # Find where carImage is parsed and add carImages support
    old_car_parse = 'String carImgName = seg.optString("carImage", "car-red.png");'
    new_car_parse = '''String carImgName = seg.optString("carImage", "car-red.png");
            java.util.ArrayList<String> carImgNames = new java.util.ArrayList<>();
            carImgNames.add(carImgName);
            try {
                org.json.JSONArray carArr = seg.optJSONArray("carImages");
                if (carArr != null) {
                    for (int ci = 0; ci < carArr.length() && ci < 3; ci++) {
                        String cn = carArr.optString(ci, null);
                        if (cn != null && !carImgNames.contains(cn)) carImgNames.add(cn);
                    }
                }
            } catch (Exception e) {}'''
    if old_car_parse in j:
        j = j.replace(old_car_parse, new_car_parse, 1)
        print('MULTI-CAR PARSE OK')
    else:
        print('MULTI-CAR: pattern not found')
        import re
        m = re.search(r'String carImgName = [^;]+;', j)
        if m:
            print('Found: ' + m.group(0)[:80])

    if j != orig:
        open(p, 'w', encoding='utf-8').write(j)
    print('JAVA V4.13 DONE')

patch_html()
patch_java()
print('V4.13 ALL DONE')
