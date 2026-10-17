# v4.10: Fix autoMode() to actually create video
# autoMode() was only showing banners, never calling the video creation
# Fix: make it populate the script and call carJourneyMode()

def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    import re

    # Fix autoMode() - make it actually create the video
    old_auto = """async function autoMode(){
  try{
    showBanner('🤖 Auto Mode! Sab kuch automatic ho raha hai...','ok');
    // Step 1: Random car select karo
    const cars = ['rayo', 'bella', 'rusty', 'sunny', 'pinky'];
    const randomCar = cars[Math.floor(Math.random()*cars.length)];
    showBanner('🚗 Car: '+randomCar+' (auto-selected!)','ok');

    // Step 2: Auto story generate karo (simple template)
    const stories = [
      'ek din {car} jungle me gaya. Wahan usne ek dost banaya. Dono ne milkar khub masti ki!',
      '{car} ne socha: aaj race karenge! Sab dost aaye. Race shuru hui. {car} jeet gaya!',
      'subah {car} utha. Usne dekha aasman neela hai. Chalo adventure par chalte hain!'
    ];
    const template = stories[Math.floor(Math.random()*stories.length)];
    const story = template.replace(/{car}/g, randomCar);

    // Step 3: Car select karo (UI me)
    // ... (existing car selection logic)

    // Step 4: Story ko script me convert karo
    const lines = story.split('. ').filter(s=>s.trim()).map(s=>randomCar+': '+s.trim());

    // Step 5: Video banao (existing carJourneyMode logic with auto lines)
    showBanner('🎬 Auto video ban rahi hai...','ok');
    // Call the journey mode with pre-filled lines
    // (This integrates with existing flow)

    showBanner('✅ Auto video tayyar!','ok');
  }catch(e){
    showBanner('❌ Auto Mode: '+e.message,'err');
  }
}"""
    
    new_auto = """async function autoMode(){
  try{
    showBanner('🤖 Auto Mode! Sab kuch automatic ho raha hai...','ok');
    // Step 1: Random car select karo
    const cars = ['rayo', 'bella', 'rusty', 'sunny', 'pinky'];
    const randomCar = cars[Math.floor(Math.random()*cars.length)];
    showBanner('🚗 Car: '+randomCar+' (auto-selected!)','ok');

    // Step 2: Auto story generate karo (simple template)
    const stories = [
      'ek din {car} jungle me gaya. Wahan usne ek dost banaya. Dono ne milkar khub masti ki!',
      '{car} ne socha: aaj race karenge! Sab dost aaye. Race shuru hui. {car} jeet gaya!',
      'subah {car} utha. Usne dekha aasman neela hai. Chalo adventure par chalte hain!'
    ];
    const template = stories[Math.floor(Math.random()*stories.length)];
    const story = template.replace(/{car}/g, randomCar);

    // Step 3: Story ko script me convert karo aur textarea me dalo
    const lines = story.split('. ').filter(s=>s.trim()).map(s=>randomCar+': '+s.trim());
    const scriptText = lines.join('\\n');
    
    // Find the script textarea and populate it
    const textareas = document.querySelectorAll('textarea');
    for(let ta of textareas){
      if(ta.placeholder && ta.placeholder.toLowerCase().includes('naam')){
        ta.value = scriptText;
        ta.dispatchEvent(new Event('input'));
        break;
      }
    }
    // Fallback: try by common IDs
    const scriptBox = document.getElementById('scriptInput') || document.getElementById('scriptText');
    if(scriptBox){
      scriptBox.value = scriptText;
      scriptBox.dispatchEvent(new Event('input'));
    }

    // Step 4: Video banao - ACTUALLY CALL the video creation!
    showBanner('🎬 Auto video ban rahi hai...','ok');
    await carJourneyMode();
    
  }catch(e){
    showBanner('❌ Auto Mode: '+e.message,'err');
  }
}"""
    
    if old_auto in h:
        h = h.replace(old_auto, new_auto, 1)
        print('AUTOMODE FIX OK')
    else:
        print('AUTOMODE FIX SKIP - pattern not found')

    # Version 4.10
    h = re.sub(r"const APP_VER='4\.09'", "const APP_VER='4.10'", h)
    h = h.replace("v4.09", "v4.10")
    print('HTML version OK')

    if h != orig:
        open(p, 'w', encoding='utf-8').write(h)
    print('HTML V4.10 DONE')

patch_html()
print('V4.10 ALL DONE')
