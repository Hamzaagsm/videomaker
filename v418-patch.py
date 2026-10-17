# v4.18: Remove vestigial clip gate from Journey mode
def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    import re
    old_block = """          // v3.67: Clips ready nahi to PEHLE download karo!
          if(typeof RealClipBridge.areClipsReady==='function'&&!RealClipBridge.areClipsReady()){
            showBanner('⬇️ Clips download ho rahi hain... thora intezar!','ok');
            if(typeof RealClipBridge.downloadClips==='function'){
              RealClipBridge.downloadClips();
              // 30 sec tak wait karo
              for(let w=0;w<30;w++){
                await new Promise(r=>setTimeout(r,1000));
                if(RealClipBridge.areClipsReady())break;
              }
            }
            if(!RealClipBridge.areClipsReady()){
              throw new Error('Clips download nahi hui! "Clips Download Karo" dabao.');
            }
          }"""
    if old_block in h:
        h = h.replace(old_block, "          // v4.18: Journey is canvas-based, no clips needed!", 1)
        print('JOURNEY GATE REMOVED')
    old_check = "if(!(function(){try{return RealClipBridge.getDownloadedCount()>=5;}catch(e){return false;}})())throw new Error('Pehle clips download karo!');"
    if old_check in h:
        new_check = "if(!window.MEER_SINGLE_BG){" + old_check + "}"
        h = h.replace(old_check, new_check, 1)
        print('CHECK CONDITIONAL')
    h = re.sub(r"const APP_VER\s*=\s*['\"]4\.\d+['\"]", "const APP_VER='4.18'", h)
    if h != orig:
        open(p, 'w', encoding='utf-8').write(h)
    print('HTML V4.18 DONE')
def patch_java():
    print('JAVA V4.18 DONE')
patch_html()
patch_java()
print('V4.18 ALL DONE')
