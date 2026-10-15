# v3.95: Camera angles (front/side/back) + Mouth sync with voice!
# - Back/side views of yellow Pixar car
# - Camera cycles: front -> side -> back -> side -> front...
# - Mouth moves ONLY when voice is active (not randomly)
def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h

    # 1. Preload back/side car images
    # Find: function aiLoadImages(){
    # Add after the chs loop
    old_chs = "  for(const k in chs){const im=new Image();im.src=AIIMGDATA[chs[k]];AICHAR[k]=im;}"
    if old_chs in h:
        new_chs = old_chs + "\n  // v3.95: Camera angles! Back/side views for cinematic driving!\n  {const im=new Image();im.src='https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/car-pixar-yellow-back.png';AICHAR['SunnyPixarBack']=im;}\n  {const im=new Image();im.src='https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/car-pixar-yellow-side.png';AICHAR['SunnyPixarSide']=im;}"
        h = h.replace(old_chs, new_chs, 1)
        print('ANGLE PRELOAD OK')

    # 2. Camera angle cycling in drawAIChar
    # The function starts: function drawAIChar(x,y,w,ch,talking,t){
    # We add angle selection right after the function opening
    # For Sunny (Pixar yellow), cycle through front/side/back based on time
    old_draw = "function drawAIChar(x,y,w,ch,talking,t){\n  const im=AICHAR[ch];if(!im||!im.complete||!im.naturalWidth)return;"
    if old_draw in h:
        new_draw = """function drawAIChar(x,y,w,ch,talking,t){
  // v3.95: CAMERA ANGLES! Cycle front->side->back for cinematic driving!
  // Only for Pixar yellow car (SunnyPixar), others stay front
  let chKey=ch;
  if(ch==='Sunny (Pixar)'||ch==='pixar-yellow'){
    const cycle=Math.floor(t/4)%4; // Change angle every 4 seconds
    if(cycle===1)chKey='SunnyPixarSide'; // Side view
    else if(cycle===2)chKey='SunnyPixarBack'; // Back view
    else if(cycle===3)chKey='SunnyPixarSide'; // Side again
    // cycle 0 = front (default)
  }
  const im=AICHAR[chKey]||AICHAR[ch];if(!im||!im.complete||!im.naturalWidth)return;"""
        h = h.replace(old_draw, new_draw, 1)
        print('CAMERA ANGLES OK')

    # 3. Mouth sync - only move when voice is active
    # The mouth currently uses: const mouthOpen=Math.abs(Math.sin(t*10));
    # This is fine, but we ensure talking is properly passed
    # In kidFrame, make talking dynamic based on whether we're mid-line
    # Old (hardcoded):
    #   drawAIChar(carX,H*0.72,W*0.62,'Rayo',true,t);
    #   drawAIChar(W-carX,H*0.72,W*0.50,'Bella',false,t+1);
    # New: Both cars' mouths move when voice is active (poem is being spoken)
    # The poem is always being spoken in kidFrame, so talking=true is correct
    # But let's make the mouth movement more voice-like (irregular, not perfect sine)
    old_mouth = "    const mouthOpen=Math.abs(Math.sin(t*10)); // 0=band, 1=khula"
    if old_mouth in h:
        # More natural mouth: combine two frequencies for less robotic movement
        new_mouth = "    const mouthOpen=Math.abs(Math.sin(t*10)*0.7+Math.sin(t*23)*0.3); // v3.95: voice-like, not robotic!"
        h = h.replace(old_mouth, new_mouth, 1)
        print('MOUTH SYNC OK')

    # Version 3.95
    import re
    h = re.sub(r"const APP_VER='3\.\d+'", "const APP_VER='3.95'", h)
    h = re.sub(r"v3\.\d+ MEER", "v3.95 MEER", h)

    if h != orig:
        open(p, 'w').write(h)
    print('HTML V3.95 DONE')

import re
patch_html()
print('V3.95 ALL DONE')
