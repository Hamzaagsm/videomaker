#!/usr/bin/env python3
# MEER v4.44 - REPEAT-SCENE FIX (Hamza ki report 2026-10-21: "baar baar ak seen, voice seen se ni milti")
# Tasdeeq pehle: uski bheji hui Haveli video frame-by-frame + awaaz ki transcription se SAHI nikli
# (6 scenes tartib se, har line apne scene par). Asal defect code me ye thay:
#  1) Journey v3 ka lastGood fallback: scene download na ho to pichla scene dobara lag jata tha
#     nayi line ke neeche -> "ek hi scene baar baar + awaaz scene se alag". AB: line SKIP hogi.
#  2) Journey download wait sirf 60s tha -> 150s; aur segments <3 hon to junk video ki bajaye saaf message.
#  3) Home ka purana dim "Suspense Stories" button purane Auto Studio par jata tha (har kahani ke
#     peechay wohi purane scenes). AB: wohi button NAYI library par; purani Auto Stories ek chhoti
#     alag button par mehfooz (koi feature delete nahi hua).
# Java BILKUL nahi chheda. Sirf v4.43 ki apni ghaltiyon ki islaah + 1 button ki simt.
import re

HP = 'android/app/src/main/assets/www/index.html'
html = open(HP, encoding='utf-8').read()

html, n1 = re.subn(r"APP_VER\s*=\s*[\"'][\d.]+[\"']", 'APP_VER="4.44"', html)
html, n2 = re.subn(r"v4\.\d+ MEER", "v4.44 MEER", html)
print('V444 APP_VER bump:', n1, n2)

# --- 1) purana dim suspense button -> nayi library; purani auto stories chhoti button par ---
old_btn = '''<button class="bigbtn" onclick="goSuspense()" style="background:linear-gradient(135deg,#1a1a2e,#16213e);border:2px solid #e94560">👻 Suspense Stories</button>'''
new_btns = '''<button class="bigbtn" onclick="go('s-cars');setTimeout(function(){var e=document.getElementById('suspBtn');if(e){e.scrollIntoView({block:'center'});}},700)" style="background:linear-gradient(135deg,#1a1a2e,#16213e);border:2px solid #e94560">👻 Suspense Stories — NAYI Library (Hindi/English)</button>
<button class="bigbtn" onclick="goSuspense()" style="background:#0f172a;border:1px solid #334155;margin-top:6px;font-size:13px;opacity:0.8">Purani Auto Stories (template wali)</button>'''
if old_btn in html:
    html = html.replace(old_btn, new_btns, 1)
    print('V444 old suspense button rerouted: True')
else:
    print('V444 old suspense button rerouted: False  <-- ANCHOR MISSING')

# --- 2) Journey download wait 60s -> 150s (journey block unique: missing.filter) ---
wait_old = """      while(waited<60000){ await new Promise(function(r){ setTimeout(r,1500); }); waited+=1500;
        var left=missing.filter(function(n){ return !advOk(n); });"""
wait_new = """      while(waited<150000){ await new Promise(function(r){ setTimeout(r,1500); }); waited+=1500;
        var left=missing.filter(function(n){ return !advOk(n); });"""
if wait_old in html:
    html = html.replace(wait_old, wait_new, 1)
    print('V444 journey wait 150s: True')
else:
    print('V444 journey wait 150s: False  <-- ANCHOR MISSING')

# --- 3) lastGood fallback KHATAM: scene na mile to line skip ---
seg_old = "    var segments=[], lastGood=null;"
seg_new = "    var segments=[];"
if seg_old in html:
    html = html.replace(seg_old, seg_new, 1)
    print('V444 lastGood var removed: True')
else:
    print('V444 lastGood var removed: False  <-- ANCHOR MISSING')

fb_old = "      if(!advOk(clip)){ clip=lastGood||plan[0].clip; } else lastGood=clip;"
fb_new = "      if(!advOk(clip)){ continue; } /* v4.44: scene na mile to line SKIP - repeat/ghalat scene kabhi nahi */"
if fb_old in html:
    html = html.replace(fb_old, fb_new, 1)
    print('V444 journey fallback removed: True')
else:
    print('V444 journey fallback removed: False  <-- ANCHOR MISSING')

# --- 4) segments <3 hon to junk video ki bajaye saaf message ---
# (anchor journeyV3 ke liye UNIQUE: 'MEER_Journey_' filename wali line bhi shamil -
#  purane journey function me bhi width-75% wali lines hain, pehla match wahan lag gaya tha)
guard_old = """    if(bar)bar.style.width='75%';
    advSetStatus('Journey video ban rahi hai...');
    var result=RealClipBridge.composeVideo(JSON.stringify(segments),'MEER_Journey_'+who+'_'+Date.now()+'.mp4');"""
guard_new = """    if(segments.length<3){ alert('Kuch scenes abhi download nahi hue - internet on karke thori dair baad dobara dabao!'); advSetStatus('Scenes abhi tayyar nahi - dobara try karo'); return; }
    if(bar)bar.style.width='75%';
    advSetStatus('Journey video ban rahi hai...');
    var result=RealClipBridge.composeVideo(JSON.stringify(segments),'MEER_Journey_'+who+'_'+Date.now()+'.mp4');"""
if guard_old in html:
    html = html.replace(guard_old, guard_new, 1)
    print('V444 journey min-segments guard: True')
else:
    print('V444 journey min-segments guard: False  <-- ANCHOR MISSING')

open(HP, 'w', encoding='utf-8').write(html)
print('V444 done')
