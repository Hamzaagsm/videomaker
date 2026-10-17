# v4.09: Fix areClipsReady vs getDownloadedCount mismatch
# UI uses getDownloadedCount()>=5, but video creation uses areClipsReady() which returns false
# Fix: video creation should use getDownloadedCount()>=5 like the UI

def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    import re

    # Replace areClipsReady() checks with getDownloadedCount()>=5
    # Line 3942, 4136: if(!RealClipBridge.areClipsReady())throw new Error('Pehle clips download karo! ⬇️');
    
    old1 = "if(!RealClipBridge.areClipsReady())throw new Error('Pehle clips download karo! ⬇️');"
    new1 = "if(!(function(){try{return RealClipBridge.getDownloadedCount()>=5;}catch(e){return false;}})())throw new Error('Pehle clips download karo! ⬇️');"
    
    count = h.count(old1)
    h = h.replace(old1, new1)
    print(f'ARECLIPSREADY FIX: {count} occurrences replaced')

    # Also fix areModeClipsReady
    old2 = "if(!RealClipBridge.areModeClipsReady('family'))throw new Error('Pehle clips download karo! ⬇️');"
    new2 = "if(!(function(){try{return RealClipBridge.getDownloadedCount()>=5;}catch(e){return false;}})())throw new Error('Pehle clips download karo! ⬇️');"
    count2 = h.count(old2)
    h = h.replace(old2, new2)
    print(f'AREMODECLIPSREADY family FIX: {count2} occurrences replaced')

    old3 = "if(!RealClipBridge.areModeClipsReady(mode))throw new Error('Pehle clips download karo! ⬇️');"
    new3 = "if(!(function(){try{return RealClipBridge.getDownloadedCount()>=5;}catch(e){return false;}})())throw new Error('Pehle clips download karo! ⬇️');"
    count3 = h.count(old3)
    h = h.replace(old3, new3)
    print(f'AREMODECLIPSREADY mode FIX: {count3} occurrences replaced')

    # Version 4.09
    h = re.sub(r"const APP_VER='4\.08'", "const APP_VER='4.09'", h)
    h = h.replace("v4.08", "v4.09")
    print('HTML version OK')

    if h != orig:
        open(p, 'w', encoding='utf-8').write(h)
    print('HTML V4.09 DONE')

patch_html()
print('V4.09 ALL DONE')
