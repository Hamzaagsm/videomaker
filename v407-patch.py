# v4.07: ElevenLabs key save/load (localStorage)
# Key ek dafa dalo, hamesha yaad rahega. Change karna ho to asani se change.

def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    import re

    # 1. Key input ke saath Save button aur auto-load
    if 'elevenlabsKeySave' not in h:
        old = '<input type="text" id="elevenlabsKeyInput"'
        new = '''<div style="display:flex;gap:6px;margin-bottom:6px;">
  <input type="text" id="elevenlabsKeyInput"'''
        if old in h:
            h = h.replace(old, new, 1)
            print('SAVE WRAP OK')

    # 2. Input ke baad Save button add karo
    if 'id="elevenlabsKeySave"' not in h:
        # Find the input line and add button after it
        pattern = r'(<input type="text" id="elevenlabsKeyInput"[^>]*>)'
        replacement = r'''\1
  <button id="elevenlabsKeySave" onclick="saveElevenKey()" style="padding:8px 12px;border-radius:8px;border:none;background:#4CAF50;color:#fff;font-size:12px;white-space:nowrap;">💾 Save</button>
</div>
<script>
function saveElevenKey(){
  var k=document.getElementById('elevenlabsKeyInput');
  if(k&&k.value.trim()){
    localStorage.setItem('elevenlabs_key',k.value.trim());
    alert('✅ Key save ho gayi!');
  }
}
(function(){
  var sv=localStorage.getItem('elevenlabs_key');
  if(sv){
    var k=document.getElementById('elevenlabsKeyInput');
    if(k)k.value=sv;
  }
})();
</script>'''
        h2 = re.sub(pattern, replacement, h, count=1)
        if h2 != h:
            h = h2
            print('SAVE BTN OK')
        else:
            print('SAVE BTN SKIP')

    # 3. elevenlabsSpeak me localStorage se bhi key lo
    old_key = """    const keyInput = document.getElementById('elevenlabsKeyInput');
    const apiKey = keyInput ? keyInput.value.trim() : '';"""
    new_key = """    const keyInput = document.getElementById('elevenlabsKeyInput');
    var apiKey = keyInput ? keyInput.value.trim() : '';
    if(!apiKey){ apiKey = localStorage.getItem('elevenlabs_key')||''; }"""
    if old_key in h:
        h = h.replace(old_key, new_key, 1)
        print('KEY LOAD OK')

    # Version 4.07
    h = re.sub(r"const APP_VER='4\.06'", "const APP_VER='4.07'", h)
    h = h.replace("v4.06", "v4.07")
    print('HTML version OK')

    if h != orig:
        open(p, 'w', encoding='utf-8').write(h)
    print('HTML V4.07 DONE')

patch_html()
print('V4.07 ALL DONE')
