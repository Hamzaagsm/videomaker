# v3.86 patch script
import sys
def patch_java():
    p = 'android/app/src/main/java/com/hamza/videomaker/MainActivity.java'
    s = open(p).read()
    old_call = 'carBmp = removeTealBackground(carBmp);'
    assert old_call in s, 'JAVA CALL NOT FOUND'
    s = s.replace(old_call, 'carBmp = removeCarBackground(carBmp);')
    anchor = '        @JavascriptInterface\n        public String renderCanvasVideo('
    assert anchor in s, 'JAVA ANCHOR NOT FOUND'
    helpers = open('v386-helpers.txt').read()
    s = s.replace(anchor, helpers + anchor)
    old_load = 'android.graphics.Bitmap carBmp = loadAssetBitmap("cars/" + carImgName);\n                if (carBmp == null) carBmp = loadAssetBitmap(carImgName);'
    assert old_load in s, 'JAVA LOAD NOT FOUND'
    new_load = 'android.graphics.Bitmap carBmp;\n                if (carImgName.startsWith("http")) {\n                    carBmp = downloadBitmap(carImgName);\n                } else {\n                    carBmp = loadAssetBitmap("cars/" + carImgName);\n                    if (carBmp == null) carBmp = loadAssetBitmap(carImgName);\n                }'
    s = s.replace(old_load, new_load)
    open(p, 'w').write(s)
    print('JAVA PATCHED OK')
def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    old_pick = "if(nm)nm.value=c.name;\n        showBanner"
    assert old_pick in h, 'PICKER NOT FOUND'
    new_pick = "if(nm)nm.value=c.name;\n        window.MEER_SELECTED_CAR=c.img;\n        try{localStorage.setItem('MEER_CAR_IMG',c.img);}catch(e){}\n        showBanner"
    h = h.replace(old_pick, new_pick, 1)
    old_rst = 'setTimeout(loadOnlineCars,2000);'
    assert old_rst in h, 'RESTORE ANCHOR NOT FOUND'
    h = h.replace(old_rst, old_rst + "\ntry{var sc=localStorage.getItem('MEER_CAR_IMG');if(sc)window.MEER_SELECTED_CAR=sc;}catch(e){}", 1)
    open(p, 'w').write(h)
    print('HTML PATCHED OK')
patch_java()
patch_html()
print('V3.86 ALL PATCHES APPLIED')
