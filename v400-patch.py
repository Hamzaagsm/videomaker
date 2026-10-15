# v4.00: AI Singing with MusicGPT! (sur-taal wali poem!)
def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h

    # 1. MusicGPT API key (Hamza ka - secure!)
    # Note: Key app me embedded hai (client-side). Free tier: 500 credits/month.
    if 'MUSICGPT_API_KEY' not in h:
        old = "const APP_VER='3.99'"
        new = """const APP_VER='4.00';
// v4.00: MusicGPT AI Singing! (sur-taal wali poem!)
const MUSICGPT_API_KEY='41Fkfuj7OT3LcNcakoF1EBa--Ssg9lfWW1lUax829hY';
const MUSICGPT_API_BASE='https://api.musicgpt.com/api/public/v1';"""
        if old in h:
            h = h.replace(old, new, 1)
            print('API KEY OK')

    # 2. AI Sing function
    if 'musicgptSing' not in h:
        old = "async function carJourneyMode(){"
        new = """// v4.00: MusicGPT se poem ko ASAL GANA banao! (sur-taal!)
async function musicgptSing(lyrics, style){
  try{
    showBanner('🎤 AI gana bana raha hai... 1-2 min lagega!','ok');
    // Step 1: Generate song request
    const resp = await fetch(MUSICGPT_API_BASE+'/musicai', {
      method: 'POST',
      headers: {
        'Authorization': MUSICGPT_API_KEY,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        prompt: style || 'Cheerful children song, happy melody',
        lyrics: lyrics,
        title: 'MEER Poem Song'
      })
    });
    const data = await resp.json();
    if(!data.success && !data.task_id){
      throw new Error('MusicGPT: '+(data.message||'request failed'));
    }
    const taskId = data.task_id;
    showBanner('🎵 Gana ban raha hai... thora intezar!','ok');
    // Step 2: Poll for completion (max 3 min)
    for(let i=0;i<36;i++){
      await new Promise(r=>setTimeout(r,5000));
      const stResp = await fetch(MUSICGPT_API_BASE+'/musicai/'+taskId, {
        headers: {'Authorization': MUSICGPT_API_KEY}
      });
      const stData = await stResp.json();
      if(stData.status==='completed' || stData.status==='SUCCESS'){
        const audioUrl = stData.audio_url || stData.conversion_url || (stData.data&&stData.data.audio_url);
        if(audioUrl){
          showBanner('✅ Gana tayyar! Download ho raha...','ok');
          return audioUrl;
        }
      }
      if(stData.status==='failed' || stData.status==='FAILED'){
        throw new Error('Gana banane me masla!');
      }
      if(i%6===0) showBanner('🎵 Gana ban raha hai... ('+Math.round(i/12)+' min)','ok');
    }
    throw new Error('Time out! Dobara try karo.');
  }catch(e){
    showBanner('❌ '+e.message,'err');
    return null;
  }
}

async function carJourneyMode(){"""
        if old in h:
            h = h.replace(old, new, 1)
            print('SING FUNC OK')

    # 3. AI Sing toggle in UI (Single Car Journey section ke paas)
    if 'aiSingToggle' not in h:
        old = '<button class="btn btn2" onclick="carJourneyMode()" style="margin-top:10px">🚗 SINGLE CAR JOURNEY (poem + drive!)</button>'
        new = '''<button class="btn btn2" onclick="carJourneyMode()" style="margin-top:10px">🚗 SINGLE CAR JOURNEY (poem + drive!)</button>
  <label style="display:block;margin-top:8px;color:#fff;font-size:14px;"><input type="checkbox" id="aiSingToggle" style="transform:scale(1.3);margin-right:6px;">🎤 AI Se Gao (sur-taal! 1-2 min lagega)</label>'''
        if old in h:
            h = h.replace(old, new, 1)
            print('TOGGLE UI OK')

    # 4. Use AI singing in carJourneyMode (poem generation ke baad)
    if 'aiSingToggle' in h and 'MUSICGPT_POEM_AUDIO' not in h:
        # Poem lines banne ke baad, agar toggle on hai to AI se gao
        old = "    showBanner('🚗 Journey ready! Video ban rahi hai...','ok');"
        new = """    // v4.00: AI Singing! (agar toggle on hai)
    window.MUSICGPT_POEM_AUDIO=null;
    try{
      const aiToggle=$('aiSingToggle');
      if(aiToggle&&aiToggle.checked&&MUSICGPT_API_KEY){
        const poemLyrics=fullLines.map(l=>l.replace(/^[A-Za-z]+\\s*:\\s*/,'' )).join('\\n');
        showBanner('🎤 AI se gaya ja raha hai...','ok');
        const audioUrl=await musicgptSing(poemLyrics,'Cheerful kids poem song, happy tune');
        if(audioUrl){
          window.MUSICGPT_POEM_AUDIO=audioUrl;
          showBanner('✅ AI gana tayyar! Video me lagega!','ok');
        }
      }
    }catch(e){ console.log('AI sing skip:',e); }
    showBanner('🚗 Journey ready! Video ban rahi hai...','ok');"""
        if old in h:
            h = h.replace(old, new, 1)
            print('AI INTEGRATION OK')

    # Version 4.00
    import re
    h = re.sub(r"const APP_VER='3\.\d+'", "const APP_VER='4.00'", h)
    h = re.sub(r"v3\.\d+ MEER", "v4.00 MEER", h)

    if h != orig:
        open(p, 'w').write(h)
    print('HTML V4.00 DONE')

import re
patch_html()
print('V4.00 ALL DONE')
