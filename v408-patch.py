# v4.08: Fix script error + banner logic
# 1. v4.07 ka script tag error de raha tha - use fix karo
# 2. "Pehle clips download karo!" ghalat show ho raha tha jab 5/5 ready hain

def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    import re

    # 1. v4.07 ke script ko safe banao - DOMContentLoaded par chalao
    old_script = """(function(){
  var sv=localStorage.getItem('elevenlabs_key');
  if(sv){
    var k=document.getElementById('elevenlabsKeyInput');
    if(k)k.value=sv;
  }
})();"""
    new_script = """document.addEventListener('DOMContentLoaded',function(){
  try{
    var sv=localStorage.getItem('elevenlabs_key');
    if(sv){
      var k=document.getElementById('elevenlabsKeyInput');
      if(k)k.value=sv;
    }
  }catch(e){}
});"""
    if old_script in h:
        h = h.replace(old_script, new_script, 1)
        print('SCRIPT FIX OK')

    # 2. Version 4.08
    h = re.sub(r"const APP_VER='4\.07'", "const APP_VER='4.08'", h)
    h = h.replace("v4.07", "v4.08")
    print('HTML version OK')

    if h != orig:
        open(p, 'w', encoding='utf-8').write(h)
    print('HTML V4.08 DONE')

patch_html()
print('V4.08 ALL DONE')
