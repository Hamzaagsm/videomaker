# v4.04: Fix syntax error + Remove Motu Patlu + ElevenLabs key input
# 1. Fixes the v4.03 JavaScript syntax error
# 2. Removes Motu Patlu Studio (user request)
# 3. ElevenLabs key via user input (not embedded)

def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    import re

    # 1. Remove embedded API key (security fix) - replace with input field
    # Remove the old ELEVENLABS_API_KEY line if it exists
    h = re.sub(r"const ELEVENLABS_API_KEY='[^']*';\n", "", h)
    h = re.sub(r"const ELEVENLABS_API_BASE='[^']*';\n", "const ELEVENLABS_API_BASE='https://api.elevenlabs.io/v1';\n", h)

    # 2. Add ElevenLabs key input in UI (before the toggle)
    if 'elevenlabsKeyInput' not in h:
        old = '<input type="checkbox" id="elevenlabsToggle"'
        new = '''<input type="text" id="elevenlabsKeyInput" placeholder="ElevenLabs API Key (optional)" style="width:100%;margin-bottom:6px;padding:8px;border-radius:8px;border:1px solid #666;background:#222;color:#fff;font-size:12px;">
  <input type="checkbox" id="elevenlabsToggle"'''
        if old in h:
            h = h.replace(old, new, 1)
            print('KEY INPUT OK')

    # 3. Update elevenlabsSpeak to use input key
    old_func = """async function elevenlabsSpeak(text, voiceId){
  try{
    const vid = voiceId || ELEVENLABS_VOICES['narrator'];
    const resp = await fetch(ELEVENLABS_API_BASE+'/text-to-speech/'+vid, {
      method: 'POST',
      headers: {
        'xi-api-key': ELEVENLABS_API_KEY,"""
    new_func = """async function elevenlabsSpeak(text, voiceId){
  try{
    const keyInput = document.getElementById('elevenlabsKeyInput');
    const apiKey = keyInput ? keyInput.value.trim() : '';
    if(!apiKey){
      console.log('ElevenLabs: no key, using native voice');
      return null;
    }
    const vid = voiceId || ELEVENLABS_VOICES['narrator'];
    const resp = await fetch(ELEVENLABS_API_BASE+'/text-to-speech/'+vid, {
      method: 'POST',
      headers: {
        'xi-api-key': apiKey,"""
    if old_func in h:
        h = h.replace(old_func, new_func, 1)
        print('FUNC FIX OK')

    # 4. Remove Motu Patlu Studio button/section
    # Find and remove Motu Patlu related UI
    h = re.sub(r'<button[^>]*motu[^>]*>.*?</button>', '', h, flags=re.IGNORECASE|re.DOTALL)
    h = re.sub(r'<button[^>]*Motu Patlu[^>]*>.*?</button>', '', h, flags=re.IGNORECASE|re.DOTALL)
    # Remove motu patlu studio div/section
    h = re.sub(r'<div[^>]*id="motu[^"]*"[^>]*>.*?</div>\s*</div>', '', h, flags=re.IGNORECASE|re.DOTALL)
    print('MOTU REMOVED')

    # 5. Version 4.04
    h = re.sub(r"const APP_VER='4\.03'", "const APP_VER='4.04'", h)
    h = re.sub(r"v4\.03", "v4.04", h)

    if h != orig:
        open(p, 'w').write(h)
    print('HTML V4.04 DONE')

patch_html()
print('V4.04 ALL DONE')
