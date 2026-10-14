# v3.90: Poem MELODY! (sur ke sath!)
def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h

    # Poem melody: prepVoice me pitch pattern
    # Anchor: const cpitch=castPitchFor(S.lines[i]); // per-character voice!
    old = '    const cpitch=castPitchFor(S.lines[i]); // per-character voice!'
    if old in h and 'v3.90: Poem MELODY' not in h:
        new = '''    const cpitch=castPitchFor(S.lines[i]); // per-character voice!
    // v3.90: Poem MELODY! (sur ke sath! - musical pitch pattern)
    let usePitch=cpitch;
    if(window.MEER_SINGLE_VOICE){
      const melody=[1.0,1.18,1.33,1.18,1.0,1.12,1.27,1.42]; // C-D-E-D-C-D-E-G (khushgawar!)
      const mFactor=melody[i%melody.length];
      if(usePitch)usePitch=usePitch*mFactor;
      else usePitch=mFactor;
    }'''
        h = h.replace(old, new, 1)
        print('MELODY PITCH OK')

        # Ab cpitch ki jagah usePitch istemal karo
        # loadAudioNative(parts[c],lang,rate,cpitch) -> usePitch
        h = h.replace('loadAudioNative(parts[c],lang,rate,cpitch)',
                      'loadAudioNative(parts[c],lang,rate,usePitch)', 1)
        print('USEPITCH OK')

    # Version 3.90
    import re
    h = re.sub(r"const APP_VER='3\.\d+'", "const APP_VER='3.90'", h)
    h = re.sub(r"v3\.\d+ MEER", "v3.90 MEER", h)

    if h != orig:
        open(p, 'w').write(h)
    print('HTML V3.90 DONE')

import re
patch_html()
print('V3.90 ALL DONE')
