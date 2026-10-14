# v3.86 patch script - workflow se chalta hai (GitHub upload band hone ki wajah se)
import sys

def patch_java():
    p = 'android/app/src/main/java/com/hamza/videomaker/MainActivity.java'
    s = open(p).read()

    # 1. removeTealBackground ki jagah removeCarBackground call karo
    old_call = 'carBmp = removeTealBackground(carBmp);'
    assert old_call in s, 'JAVA CALL NOT FOUND'
    s = s.replace(old_call, 'carBmp = removeCarBackground(carBmp);')

    # 2. Flood-fill + downloadBitmap helpers add karo
    anchor = '        @JavascriptInterface\n        public String renderCanvasVideo('
    assert anchor in s, 'JAVA ANCHOR NOT FOUND'
    helpers = '''        // v3.86: Flood-fill background removal (teal/white safe - car ke safed hisse mehfooz!)
        private static android.graphics.Bitmap removeCarBackground(android.graphics.Bitmap src) {
            int w = src.getWidth(), h = src.getHeight();
            android.graphics.Bitmap out = src.copy(android.graphics.Bitmap.Config.ARGB_8888, true);
            int[] px = new int[w * h];
            out.getPixels(px, 0, w, 0, 0, w, h);
            int bg = px[5 * w + 5];
            int bgr = android.graphics.Color.red(bg);
            int bgg = android.graphics.Color.green(bg);
            int bgb = android.graphics.Color.blue(bg);
            int th = 55, th2 = th * th;
            boolean[] vis = new boolean[w * h];
            int[] q = new int[w * h];
            int qh = 0, qt = 0;
            int[] sx = {5, w - 6, 5, w - 6};
            int[] sy = {5, 5, h - 6, h - 6};
            for (int k = 0; k < 4; k++) {
                int id = sy[k] * w + sx[k];
                if (!vis[id]) { vis[id] = true; q[qt++] = id; }
            }
            while (qh < qt) {
                int id = q[qh++];
                int pp = px[id];
                int dr = android.graphics.Color.red(pp) - bgr;
                int dg = android.graphics.Color.green(pp) - bgg;
                int db = android.graphics.Color.blue(pp) - bgb;
                if (dr * dr + dg * dg + db * db < th2) {
                    px[id] = 0;
                    int x = id % w, y = id / w;
                    if (x > 0) { int n = id - 1; if (!vis[n]) { vis[n] = true; q[qt++] = n; } }
                    if (x < w - 1) { int n = id + 1; if (!vis[n]) { vis[n] = true; q[qt++] = n; } }
                    if (y > 0) { int n = id - w; if (!vis[n]) { vis[n] = true; q[qt++] = n; } }
                    if (y < h - 1) { int n = id + w; if (!vis[n]) { vis[n] = true; q[qt++] = n; } }
                }
            }
            out.setPixels(px, 0, w, 0, 0, w, h);
            return out;
        }
        // v3.86: URL se car image download karo (online picker wali gariyan!)
        private static android.graphics.Bitmap downloadBitmap(String urlStr) {
            try {
                java.net.URL url = new java.net.URL(urlStr);
                java.net.HttpURLConnection con = (java.net.HttpURLConnection) url.openConnection();
                con.setConnectTimeout(15000);
                con.setReadTimeout(15000);
                java.io.InputStream is = con.getInputStream();
                android.graphics.Bitmap bmp = android.graphics.BitmapFactory.decodeStream(is);
                is.close();
                return bmp;
            } catch (Exception e) { return null; }
        }
'''
    s = s.replace(anchor, helpers + anchor)

    # 3. Online URL se car load karo
    old_load = 'android.graphics.Bitmap carBmp = loadAssetBitmap("cars/" + carImgName);\n                if (carBmp == null) carBmp = loadAssetBitmap(carImgName);'
    assert old_load in s, 'JAVA LOAD NOT FOUND'
    new_load = '''android.graphics.Bitmap carBmp;
                if (carImgName.startsWith("http")) {
                    carBmp = downloadBitmap(carImgName);
                } else {
                    carBmp = loadAssetBitmap("cars/" + carImgName);
                    if (carBmp == null) carBmp = loadAssetBitmap(carImgName);
                }
                // v3.86: DOOSRI gari! (2 garian ek sath chalengi!)
                String carImgName2 = first.optString("carImage2", "");
                android.graphics.Bitmap carBmp2 = null;
                if (!carImgName2.isEmpty()) {
                    if (carImgName2.startsWith("http")) carBmp2 = downloadBitmap(carImgName2);
                    else { carBmp2 = loadAssetBitmap("cars/" + carImgName2); if (carBmp2 == null) carBmp2 = loadAssetBitmap(carImgName2); }
                }'''
    s = s.replace(old_load, new_load)

    # 4. Doosri gari ko scale karo
    old_scale = '''                android.graphics.Bitmap carScaled = null;
                if (carBmp != null) {
                    carBmp = removeCarBackground(carBmp);'''
    assert old_scale in s, 'JAVA SCALE NOT FOUND'
    new_scale = '''                android.graphics.Bitmap carScaled = null;
                android.graphics.Bitmap carScaled2 = null;
                if (carBmp2 != null) {
                    carBmp2 = removeCarBackground(carBmp2);
                    int cw2 = 360;
                    int ch2 = (int) ((float) carBmp2.getHeight() * cw2 / carBmp2.getWidth());
                    carScaled2 = android.graphics.Bitmap.createScaledBitmap(carBmp2, cw2, ch2, true);
                }
                if (carBmp != null) {
                    carBmp = removeCarBackground(carBmp);'''
    s = s.replace(old_scale, new_scale)

    open(p, 'w').write(s)
    print('JAVA PATCHED OK')

def patch_draw():
    # Frame loop me doosri gari draw karo
    p = 'android/app/src/main/java/com/hamza/videomaker/MainActivity.java'
    s = open(p).read()

    # v3.86 FIX: duplicate carX hatao (pehle se upar declare hai!)
    old_dup = '                            // Fallback: simple car shape draw karo (ye bhi drive karegi!)\n                            float carX = -450 + progress * (W + 900);'
    if old_dup in s:
        s = s.replace(old_dup,
            '                            // Fallback: simple car shape draw karo (ye bhi drive karegi!)\n                            // (carX upar pehle se set hai!)', 1)
        print('DUP CARX FIXED')
    else:
        # alternative: agar comment alag ho
        import re
        s2 = re.sub(r'(\} else \{\s*\n\s*//[^\n]*\n\s*)float carX = -450 \+ progress \* \(W \+ 900\);',
                    r'\1// (carX upar pehle se set hai!)', s, count=1)
        if s2 != s:
            s = s2
            print('DUP CARX FIXED (regex)')
        else:
            print('DUP CARX NOT FOUND - checking...')

    old_wheels = '''                            drawWheel(canvas, w1x, wy, wheelR, wheelAngle, wheelPaint, spokePaint);
                            drawWheel(canvas, w2x, wy, wheelR, wheelAngle, wheelPaint, spokePaint);
                        } else {'''
    assert old_wheels in s, 'WHEELS ANCHOR NOT FOUND'
    new_wheels = '''                            drawWheel(canvas, w1x, wy, wheelR, wheelAngle, wheelPaint, spokePaint);
                            drawWheel(canvas, w2x, wy, wheelR, wheelAngle, wheelPaint, spokePaint);
                            // v3.86: DOOSRI gari - sath me chalegi!
                            if (carScaled2 != null) {
                                float car2X = carX - 220;
                                float car2Y = carY + 70;
                                canvas.drawBitmap(carScaled2, car2X, car2Y, null);
                                float w2r = 32;
                                float w2a = wheelAngle;
                                drawWheel(canvas, car2X + carScaled2.getWidth() * 0.30f, car2Y + carScaled2.getHeight() * 0.83f, w2r, w2a, wheelPaint, spokePaint);
                                drawWheel(canvas, car2X + carScaled2.getWidth() * 0.74f, car2Y + carScaled2.getHeight() * 0.83f, w2r, w2a, wheelPaint, spokePaint);
                            }
                        } else {'''
    s = s.replace(old_wheels, new_wheels, 1)
    # recycle carScaled2
    old_rec = 'if (carScaled != null) carScaled.recycle();'
    if old_rec in s:
        s = s.replace(old_rec, old_rec + '\n                if (carScaled2 != null) carScaled2.recycle();', 1)
    open(p, 'w').write(s)
    print('DRAW PATCHED OK')

def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()

    # Picker: jo gari select ho wahi video me! (specific anchor - sirf picker wala onclick)
    old_pick = "if(nm)nm.value=c.name;\n        showBanner"
    assert old_pick in h, 'PICKER NOT FOUND'
    new_pick = "if(nm)nm.value=c.name;\n        window.MEER_SELECTED_CAR=c.img;\n        try{localStorage.setItem('MEER_CAR_IMG',c.img);}catch(e){}\n        showBanner"
    h = h.replace(old_pick, new_pick, 1)

    # Load par yaad rakho
    old_rst = 'setTimeout(loadOnlineCars,2000);'
    assert old_rst in h, 'RESTORE ANCHOR NOT FOUND'
    h = h.replace(old_rst,
        old_rst + "\ntry{var sc=localStorage.getItem('MEER_CAR_IMG');if(sc)window.MEER_SELECTED_CAR=sc;}catch(e){}", 1)

    # v3.86: DOOSRI gari! (2 garian ek sath!)
    old_carimg = "const carImg = (window.MEER_SELECTED_CAR || 'car-red.png');"
    assert old_carimg in h, 'CARIMG NOT FOUND'
    new_carimg = old_carimg + "\n      let carImg2='car-blue.png';\n      try{if(ONLINE_CARS&&ONLINE_CARS.length>1){const oth=ONLINE_CARS.filter(c=>c.img!==carImg);if(oth.length>0)carImg2=oth[Math.floor(Math.random()*oth.length)].img;}}catch(e){}"
    h = h.replace(old_carimg, new_carimg, 1)

    old_seg = "carImage:carImg,bgImage:bgImg"
    assert old_seg in h, 'SEG NOT FOUND'
    h = h.replace(old_seg, "carImage:carImg,carImage2:carImg2,bgImage:bgImg", 1)

    open(p, 'w').write(h)
    print('HTML PATCHED OK')

patch_java()
patch_draw()
patch_html()
print('V3.86 ALL PATCHES APPLIED')
