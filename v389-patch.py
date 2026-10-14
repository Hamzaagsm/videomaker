# v3.89: COMPLETE clean patch (base se seedha!)
# - Flood-fill background removal
# - URL loading for cars
# - Screenshot style: bari gari (700px), CENTERED, no flat road, no wheels, no 2nd car
# - Voice: single voice + distinct voices
# - Silent tail fix

def patch_java():
    p = 'android/app/src/main/java/com/hamza/videomaker/MainActivity.java'
    s = open(p).read()
    orig = s

    # 1. removeTealBackground -> removeCarBackground (flood-fill)
    if 'carBmp = removeTealBackground(carBmp);' in s:
        s = s.replace('carBmp = removeTealBackground(carBmp);',
                      'carBmp = removeCarBackground(carBmp); // v3.89: flood-fill!', 1)
        print('BG REMOVAL OK')

    # 2. Add helpers (flood-fill + downloadBitmap) before renderCanvasVideo
    if 'private static android.graphics.Bitmap removeCarBackground' not in s:
        anchor = '        @JavascriptInterface\n        public String renderCanvasVideo('
        assert anchor in s, 'ANCHOR NOT FOUND'
        helpers = '''        // v3.89: Flood-fill (sirf bahar ka background!)
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
        s = s.replace(anchor, helpers + anchor, 1)
        print('HELPERS OK')

    # 3. URL loading for car
    old_load = 'android.graphics.Bitmap carBmp = loadAssetBitmap("cars/" + carImgName);\n                if (carBmp == null) carBmp = loadAssetBitmap(carImgName);'
    if old_load in s:
        new_load = '''android.graphics.Bitmap carBmp;
                if (carImgName.startsWith("http")) {
                    carBmp = downloadBitmap(carImgName);
                } else {
                    carBmp = loadAssetBitmap("cars/" + carImgName);
                    if (carBmp == null) carBmp = loadAssetBitmap(carImgName);
                }'''
        s = s.replace(old_load, new_load, 1)
        print('URL LOAD OK')

    # 4. Big car: 420 -> 700
    if 'int cw = 420;' in s:
        s = s.replace('int cw = 420;', 'int cw = 700; // v3.89: BARI gari!', 1)
        print('SIZE 700 OK')

    # 5. Car CENTERED (not left-right drive)
    # Base has TWO: outer (line 1429) aur fallback else-block (line 1447)
    # Outer ko centered karo, fallback wali DECLARATION hatao (outer wali use hogi!)
    if 'float carX = -450 + progress * (W + 900);' in s:
        # Pehle outer wali (pehli occurrence) ko replace karo
        s = s.replace('float carX = -450 + progress * (W + 900);',
                      'float carX = (W - 700) / 2; // v3.89: CENTER! (700px car)', 1)
        print('CENTER OK (outer)')
        # Ab fallback wali (doosri occurrence) ki declaration hatao - sirf comment
        # (outer carX hi use hogi, dobara declare nahi kar sakte!)
        if 'float carX = -450 + progress * (W + 900);' in s:
            s = s.replace('float carX = -450 + progress * (W + 900);',
                          '// v3.89: outer carX use hogi (centered!)', 1)
            print('FALLBACK CARX REMOVED OK')

    # 6. Car Y: screenshot style (center + bob), not on road
    # Base has: float carY = roadTop - carScaled.getHeight() * 0.82f + bounce;
    if 'float carY = roadTop - carScaled.getHeight() * 0.82f + bounce;' in s:
        s = s.replace('float carY = roadTop - carScaled.getHeight() * 0.82f + bounce;',
                      'float carY = H * 0.30f + (float)(Math.sin(frameNum * 0.08) * 12); // v3.89: center+bob!', 1)
        print('CARY OK')

    # 7. Remove flat road (3D bg has its own road!)
    if 'canvas.drawRect(0, roadTop, W, H, paint);' in s:
        s = s.replace('canvas.drawRect(0, roadTop, W, H, paint);',
                      '// v3.89: flat road nahi! (3D bg ka apna road)', 1)
        print('ROAD REMOVED OK')

    # 8. Remove drawn wheels (main car)
    # Base has wheel code - replace with comment
    import re
    # Match the wheel block for main car
    wheel_pat = r'                            // Wheels: 2 rotating wheels \(car ke asal wheels par!\)\n(?:.*\n){6}                            drawWheel\(canvas, w2x, wy, wheelR, wheelAngle, wheelPaint, spokePaint\);'
    s_new = re.sub(wheel_pat, '                            // v3.89: no drawn wheels! (car ke apne!)', s, count=1)
    if s_new != s:
        s = s_new
        print('WHEELS REMOVED OK')
    else:
        print('WHEELS PATTERN NOT FOUND - trying alt')
        # Alt: just comment out drawWheel lines for main car
        s = s.replace('drawWheel(canvas, w1x, wy, wheelR, wheelAngle, wheelPaint, spokePaint);',
                      '// v3.89 no wheels', 1)
        s = s.replace('drawWheel(canvas, w2x, wy, wheelR, wheelAngle, wheelPaint, spokePaint);',
                      '// v3.89 no wheels', 1)

    if s != orig:
        open(p, 'w').write(s)
    print('JAVA V3.89 DONE')

def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h

    # Picker: selected car yaad rakho
    if 'window.MEER_SELECTED_CAR' not in h:
        old = "if(nm)nm.value=c.name;\n        showBanner"
        if old in h:
            h = h.replace(old,
                "if(nm)nm.value=c.name;\n        window.MEER_SELECTED_CAR=c.img;\n        try{localStorage.setItem('MEER_CAR_IMG',c.img);}catch(e){}\n        showBanner", 1)
            print('PICKER OK')

    # Single voice flag in carJourneyMode
    if 'window.MEER_SINGLE_VOICE=true' not in h:
        old = 'window.MEER_SINGLE_BG=true;window.MEER_FIXED_BG=null;'
        if old in h:
            h = h.replace(old, old + "window.MEER_SINGLE_VOICE=true; // v3.89", 1)
            print('SINGLE VOICE FLAG OK')

    # Single voice OFF in regular mode
    if 'window.MEER_SINGLE_VOICE=false' not in h:
        old = 'async function realMakeVideo(){'
        if old in h:
            h = h.replace(old, old + "\n  window.MEER_SINGLE_VOICE=false; // v3.89", 1)
            print('VOICE OFF OK')

    # castPitchFor: single voice logic
    if 'v3.89: Single Voice' not in h:
        old = 'function castPitchFor(line){'
        if old in h:
            new = '''function castPitchFor(line){
  // v3.89: Single Voice - aik gari ki aik hi awaz!
  if(window.MEER_SINGLE_VOICE){
    try{
      const cn=(document.getElementById('realName1')||{}).value||'Rayo';
      const cast=detectCast();
      const names=Object.keys(cast);
      let v=cast[cn.trim()]||(names.length?cast[names[0]]:'male');
      return CASTPITCH[v]||1.0;
    }catch(e){return 1.0;}
  }'''
            h = h.replace(old, new, 1)
            print('CASTPITCH OK')

    # Distinct voices in detectCast
    if 'v3.89: Har character ki ALAG awaz' not in h:
        old = '  return cast;\n}\nfunction renderVoiceCast(){'
        if old in h:
            new = '''  // v3.89: Har character ki ALAG awaz!
  const _used={};
  for(const _k of Object.keys(cast)){
    let _v=cast[_k];
    if(_used[_v]){
      for(const _alt of ['female','male','child','normal']){if(!_used[_alt]){_v=_alt;break;}}
      cast[_k]=_v;
    }
    _used[_v]=1;
  }
  return cast;
}
function renderVoiceCast(){'''
            h = h.replace(old, new, 1)
            print('DISTINCT OK')

    # Silent tail fix
    if 'const dur=Math.max(1.0,audioDurSec+0.3);' in h:
        h = h.replace('const dur=Math.max(1.0,audioDurSec+0.3);',
                      'const dur=Math.max(0.8,audioDurSec+0.1); // v3.89: silent tail fix', 1)
        print('SILENT TAIL OK')

    # Version 3.89
    h = re.sub(r"const APP_VER='3\.\d+'", "const APP_VER='3.89'", h)
    h = re.sub(r"v3\.\d+ MEER", "v3.89 MEER", h)

    if h != orig:
        open(p, 'w').write(h)
    print('HTML V3.89 DONE')

import re
patch_java()
patch_html()
print('V3.89 ALL DONE')
