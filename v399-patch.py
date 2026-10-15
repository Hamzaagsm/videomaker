# v3.99: Motu Patlu Studio! (Hamza ki farmaish)
# - Alag Motu Patlu Studio option (caron se alag!)
# - Group video: sare characters ek sath!
# - Cartoon backgrounds!

def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    import re

    # 1. Home par Motu Patlu Studio button (Real Cartoon ke baad)
    old_btn = '''  <div class="row">
    <button class="btn" onclick="go('s-real');realInit()" style="background:linear-gradient(135deg,#00c9ff,#92fe9d);color:#003">🎬 Real Cartoon Studio</button>
  </div>'''
    if old_btn in h:
        new_btn = old_btn + '''
  <div class="row">
    <button class="btn" onclick="go('s-motu');motuInit()" style="background:linear-gradient(135deg,#ff6b35,#f7b733);color:#fff">🎭 Motu Patlu Studio</button>
  </div>'''
        h = h.replace(old_btn, new_btn, 1)
        print('HOME BTN OK')

    # 2. Motu Patlu Studio screen (s-realfam ke baad)
    old_screen = '<!-- ============ 📖 STORY TO VIDEO (v3.22) ============ -->'
    if old_screen in h:
        motu_screen = '''<!-- ============ 🎭 MOTU PATLU STUDIO (v3.99) ============ -->
<div class="screen" id="s-motu">
  <button class="back" onclick="go('s-home')">← Home</button>
  <h1 style="font-size:22px">🎭 Motu Patlu Studio</h1>
  <p class="hint">Sare dost ek sath ek video me! 👇</p>
  <div class="card">
    <div class="lbl">🎭 Characters chuno (jitne marzi!)</div>
    <div id="motuChars" style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:8px 0"></div>
  </div>
  <div class="card">
    <div class="lbl">🏠 Background chuno</div>
    <div id="motuBgs" style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:8px 0"></div>
  </div>
  <div class="card">
    <div class="lbl">✍️ Script (format: <b>Naam: baat</b>)</div>
    <textarea id="motuScript" class="big-idea" style="min-height:150px" placeholder="Motu: Patlu, samose khayen!&#10;Patlu: Haan Motu, chalo!&#10;Chingam: Ruk jao! Inspector Chingam aa gaya!" oninput="motuUpdateEst()"></textarea>
    <p class="hint" id="motuEst" style="text-align:center">📏 0 lines</p>
    <div class="row">
      <div><div class="lbl">🗣️ Zabaan</div>
        <select id="motuLang"><option value="hi" selected>🇮🇳 Hindi</option><option value="ur">🇵🇰 Urdu</option><option value="en">🇬🇧 English</option></select></div>
    </div>
  </div>
  <button class="btn btn3" onclick="motuMakeVideo()">🎬 MOTU PATLU VIDEO BANAO →</button>
  <div class="prog" id="motuProg" style="display:none"><div id="motuBar"></div></div>
  <p class="hint" id="motuStat" style="text-align:center"></p>
  <video id="motuPreview" controls playsinline style="display:none;width:100%;border-radius:12px"></video>
  <button class="btn" id="motuDl" style="display:none">⬇️ DOWNLOAD KARO</button>
</div>

<!-- ============ 📖 STORY TO VIDEO (v3.22) ============ -->'''
        h = h.replace(old_screen, motu_screen, 1)
        print('SCREEN OK')

    # 3. Motu Patlu JS (</body> se pehle ya script ke end me)
    # MOTU_CHARS aur functions add karo
    old_js = 'function realInit(){realClipCheck();}'
    if old_js in h:
        motu_js = '''// v3.99: Motu Patlu Studio!
const MOTU_CHARS=[
 {id:'motu',name:'Motu',img:'https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/motu-bike.png',pitch:0.7},
 {id:'patlu',name:'Patlu',img:'https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/patlu-bike.png',pitch:1.4},
 {id:'don',name:'Don',img:'https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/don-bike.png',pitch:0.6},
 {id:'goon1',name:'Goon1',img:'https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/don-goon1-bike.png',pitch:0.8},
 {id:'goon2',name:'Goon2',img:'https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/don-goon2-bike.png',pitch:1.1},
 {id:'ghaseeta',name:'Ghaseeta',img:'https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/ghaseeta-bike.png',pitch:1.0},
 {id:'jhatka',name:'Jhatka',img:'https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/jhatka-bike.png',pitch:1.3},
 {id:'chingam',name:'Chingam',img:'https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/chingam-bike.png',pitch:0.9},
 {id:'samosa',name:'Samosa',img:'https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/samosa-bike.png',pitch:1.2}
];
const MOTU_BGS=[
 {id:'mela',name:'🎪 Mela',img:'https://github.com/Hamzaagsm/videomaker/releases/download/backgrounds-v1/bg-city-car.mp4'},
 {id:'town',name:'🏠 Furfuri Nagar',img:'https://github.com/Hamzaagsm/videomaker/releases/download/backgrounds-v1/bg-city.mp4'},
 {id:'park',name:'🌳 Park',img:'https://github.com/Hamzaagsm/videomaker/releases/download/backgrounds-v1/bg-garden.mp4'},
 {id:'night',name:'🌃 Raat',img:'https://github.com/Hamzaagsm/videomaker/releases/download/backgrounds-v1/bg-nightcity.mp4'},
 {id:'beach',name:'🏖️ Beach',img:'https://github.com/Hamzaagsm/videomaker/releases/download/backgrounds-v1/bg-beach.mp4'}
];
let motuSelected=['motu','patlu'];
let motuBg='town';
function motuInit(){
  const box=$('motuChars');box.innerHTML='';
  MOTU_CHARS.forEach(c=>{
    const d=document.createElement('div');
    d.style.cssText='cursor:pointer;text-align:center;padding:6px;border-radius:10px;border:2px solid '+(motuSelected.includes(c.id)?'#ff6b35':'#444');
    d.innerHTML='<img src="'+c.img+'" style="width:60px;height:60px;object-fit:contain"><br><small>'+c.name+'</small>';
    d.onclick=()=>{
      const i=motuSelected.indexOf(c.id);
      if(i>=0)motuSelected.splice(i,1);else motuSelected.push(c.id);
      motuInit();
    };
    box.appendChild(d);
  });
  const bgbox=$('motuBgs');bgbox.innerHTML='';
  MOTU_BGS.forEach(b=>{
    const d=document.createElement('button');
    d.className='btn btn2';d.style.border=b.id===motuBg?'3px solid #ff6b35':'';
    d.textContent=b.name;d.onclick=()=>{motuBg=b.id;motuInit();};
    bgbox.appendChild(d);
  });
}
function motuUpdateEst(){
  const t=$('motuScript').value.trim();
  const n=t?t.split('\\n').filter(l=>l.trim()).length:0;
  $('motuEst').textContent='📏 '+n+' lines';
}
async function motuMakeVideo(){
  const text=$('motuScript').value.trim();
  if(!text){alert('Pehle script likho! (Naam: baat)');return;}
  if(!motuSelected.length){alert('Pehle characters chuno!');return;}
  const bar=$('motuBar'),st=$('motuStat');
  $('motuProg').style.display='block';
  const setP=(p,t)=>{bar.style.width=p+'%';st.textContent=t;};
  const lang=$('motuLang').value;
  try{
    if(!realHasBridge())throw new Error('Ye feature MEER app me chalega!');
    const raw=text.split('\\n').filter(l=>l.trim());
    const lines=[];
    for(const ln of raw){
      const m=ln.match(/^([A-Za-z0-9]+)\\s*:\\s*(.+)$/);
      if(!m)continue;
      const nm=m[1].toLowerCase();
      const ch=MOTU_CHARS.find(c=>c.id===nm||c.name.toLowerCase()===nm);
      if(!ch)continue;
      lines.push({ch,text:m[2].trim()});
    }
    if(!lines.length)throw new Error('Script format: Naam: baat (Motu, Patlu, Don...)');
    setP(5,'🎙️ Awazein ban rahi hain...');
    const segs=[];
    for(let i=0;i<lines.length;i++){
      setP(5+i/lines.length*40,'🎙️ '+(i+1)+'/'+lines.length+' '+lines[i].ch.name);
      const au=await carSpeak(lines[i].ch.name,lines[i].text,lang,lines[i].ch.pitch);
      segs.push({ch:lines[i].ch,text:lines[i].text,au,dur:Math.max(2.5,(au.duration||2)+0.5)});
    }
    // Background image load karo
    const bgSel=MOTU_BGS.find(b=>b.id===motuBg);
    setP(50,'🎨 Characters tayyar ho rahe hain...');
    const charImgs={};
    for(const cid of motuSelected){
      const c=MOTU_CHARS.find(x=>x.id===cid);
      const img=new Image();img.crossOrigin='anonymous';
      await new Promise((res,rej)=>{img.onload=res;img.onerror=res;img.src=c.img;});
      charImgs[cid]=img;
    }
    // Canvas par draw karo
    const W=720,H=1280;cv.width=720;cv.height=1280;
    setP(60,'🎬 Recording...');
    cvShowRec();NOIMG=true;
    cx.setTransform(1,0,0,1,0,0);
    const vstream=cv.captureStream(30);
    const tracks=[...vstream.getVideoTracks()];
    if(!tracks.length)throw new Error('Video track nahi mila');
    const actx=new (window.AudioContext||window.webkitAudioContext)();
    const dest=actx.createMediaStreamDestination();
    const allTracks=[...tracks,...dest.stream.getAudioTracks()];
    const rec=new MediaRecorder(new MediaStream(allTracks),{mimeType:'video/webm'});
    const chunks=[];
    rec.ondataavailable=e=>{if(e.data.size)chunks.push(e.data);};
    const recDone=new Promise(res=>rec.onstop=res);
    rec.start(500);
    // Har segment draw karo
    let tIdx=0;
    for(const s of segs){
      setP(60+tIdx/segs.length*35,'🎬 '+s.ch.name+' bol raha hai...');
      // Background gradient (cartoon style)
      const grd=cx.createLinearGradient(0,0,0,H);
      grd.addColorStop(0,'#87CEEB');grd.addColorStop(0.6,'#B0E0E6');grd.addColorStop(1,'#90EE90');
      cx.fillStyle=grd;cx.fillRect(0,0,W,H);
      // Sun
      cx.fillStyle='#FFD700';cx.beginPath();cx.arc(600,150,60,0,7);cx.fill();
      // Ground
      cx.fillStyle='#7CFC00';cx.fillRect(0,950,W,330);
      // Characters ek sath!
      const n=motuSelected.length;
      const cw=Math.min(200,W/(n+0.5));
      motuSelected.forEach((cid,idx)=>{
        const img=charImgs[cid];
        const x=(W-cw*n)/2+idx*cw;
        const y=700;
        const isActive=(cid===s.ch.id);
        if(img&&img.complete&&img.naturalWidth){
          if(isActive){
            cx.save();cx.shadowColor='#ff6b35';cx.shadowBlur=30;
            cx.drawImage(img,x-10,y-10,cw+20,220);cx.restore();
          }else{
            cx.globalAlpha=0.7;cx.drawImage(img,x,y,cw,200);cx.globalAlpha=1;
          }
        }
        // Naam
        cx.fillStyle=isActive?'#ff6b35':'#333';
        cx.font='bold 24px sans-serif';cx.textAlign='center';
        const cn=MOTU_CHARS.find(c=>c.id===cid).name;
        cx.fillText(cn,x+cw/2,y+235);
      });
      // Speaker ka dialogue
      cx.fillStyle='rgba(0,0,0,0.7)';
      cx.fillRect(20,100,W-40,120);
      cx.fillStyle='#fff';cx.font='28px sans-serif';cx.textAlign='center';
      const words=s.text.split(' ');
      let line1='',line2='';
      words.forEach((w,i)=>{if(i<6)line1+=w+' ';else line2+=w+' ';});
      cx.fillText(s.ch.name+': '+line1.trim(),W/2,140);
      if(line2.trim())cx.fillText(line2.trim(),W/2,175);
      // Audio play karo
      const src=actx.createMediaElementSource(s.au);
      src.connect(dest);
      s.au.playbackRate=1;
      await s.au.play().catch(()=>{});
      await new Promise(r=>{s.au.onended=r;setTimeout(r,(s.dur+1)*1000);});
      src.disconnect();
      tIdx++;
      await sleep(300);
    }
    // End
    setP(98,'💾 Save ho raha hai...');
    rec.stop();await recDone;
    const blob=new Blob(chunks,{type:'video/webm'});
    const url=URL.createObjectURL(blob);
    $('motuPreview').src=url;$('motuPreview').style.display='block';
    $('motuDl').style.display='block';
    $('motuDl').onclick=()=>{
      if(realHasBridge()&&typeof RealClipBridge.saveVideo==='function'){
        RealClipBridge.saveVideo(url,'MEER-MotuPatlu.mp4');
      }else{
        const a=document.createElement('a');a.href=url;a.download='MEER-MotuPatlu.mp4';a.click();
      }
    };
    setP(100,'✅ Video tayyar!');
    cvHideRec();NOIMG=false;
  }catch(e){
    setP(0,'❌ '+e.message);
    cvHideRec();NOIMG=false;
  }
}
function realInit(){realClipCheck();}'''
        h = h.replace(old_js, motu_js, 1)
        print('JS OK')

    # 4. Version 3.99
    h = re.sub(r"const APP_VER='3\.\d+'", "const APP_VER='3.99'", h)

    if h != orig:
        open(p, 'w').write(h)
    print('HTML V3.99 DONE')

import re
patch_html()
print('V3.99 ALL DONE')
