# v4.29: Fix footer version + add V427 test button
def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    # Fix footer: v4.15 -> v4.29
    h = h.replace('v4.15 MEER', "v4.29 MEER")
    h = h.replace("const APP_VER='4.28'", "const APP_VER='4.29'")
    # Add TEST button for V427 engine right after REAL VIDEO BANAO
    test_btn = '<button onclick="if(typeof V427!==\'undefined\'&&V427.makeVideo){var s=document.querySelector(\\'textarea\\');V427.makeVideo(s?s.value:\\'Rayo: Hello!\\',function(b){var a=document.createElement(\\'a\\');a.href=URL.createObjectURL(b);a.download=\\'MEER-v427.webm\\';a.click();alert(\\'Video ban gaya!\\');});}else{alert(\\'V427 not loaded\\');}" style="width:100%;padding:15px;margin:10px 0;background:linear-gradient(90deg,#ff6b6b,#feca57);border:none;border-radius:12px;color:#fff;font-size:18px;font-weight:bold;">🎬 NEW ENGINE TEST (dabao!)</button>'
    if 'NEW ENGINE TEST' not in h:
        # Insert after REAL VIDEO BANAO button
        h = h.replace('REAL VIDEO BANAO', 'REAL VIDEO BANAO' + '</button>' + test_btn + '<button style="display:none"')
        print('V429 test button ADDED')
    if h != orig:
        open(p, 'w', encoding='utf-8').write(h)
    print('HTML V4.29 DONE')
def patch_java():
    print('JAVA V4.29 DONE')
patch_html()
patch_java()
print('V4.29 ALL DONE')
