# v3.87 patch: Single Voice (aik gari = aik awaz!) + version bump
def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()

    # 1. Single Car Journey me single-voice ON
    old1 = 'window.MEER_SINGLE_BG=true;window.MEER_FIXED_BG=null;'
    assert old1 in h, 'JOURNEY ANCHOR NOT FOUND'
    h = h.replace(old1, old1 + "window.MEER_SINGLE_VOICE=true; // v3.87: aik gari = aik awaz!", 1)

    # 2. Regular video me single-voice OFF (per-character voices)
    old2 = 'async function realMakeVideo(){'
    assert old2 in h, 'REALMAKE ANCHOR NOT FOUND'
    h = h.replace(old2, old2 + "\n  window.MEER_SINGLE_VOICE=false; // v3.87: regular mode me har character ki apni awaz", 1)

    # 3. castPitchFor: single-voice mode me sab lines aik hi awaz me
    old3 = 'function castPitchFor(line){'
    assert old3 in h, 'CASTPITCH ANCHOR NOT FOUND'
    new3 = '''function castPitchFor(line){
  // v3.87: Single Voice - aik gari ki aik hi awaz! (character badle, awaz na badle!)
  if(window.MEER_SINGLE_VOICE){
    try{
      const cn=(document.getElementById('realName1')||{}).value||'Rayo';
      const cast=detectCast();
      const names=Object.keys(cast);
      let v=cast[cn.trim()]||(names.length?cast[names[0]]:'male');
      return CASTPITCH[v]||1.0;
    }catch(e){return 1.0;}
  }'''
    h = h.replace(old3, new3, 1)

    # 4. Version 3.87
    h = h.replace("const APP_VER='3.86'", "const APP_VER='3.87'")
    h = h.replace("v3.86 MEER", "v3.87 MEER")

    # 5. v3.87: Har character ki ALAG awaz! (duplicate voice nahi hogi!)
    old5 = '  return cast;\n}\nfunction renderVoiceCast(){'
    assert old5 in h, 'DETECTCAST ANCHOR NOT FOUND'
    new5 = '''  // v3.87: Har character ki ALAG awaz! (koi do ek jaisi awaz nahi!)
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
    h = h.replace(old5, new5, 1)

    open(p, 'w').write(h)
    print('HTML V3.87 PATCHED OK')

patch_html()
print('V3.87 DONE')
