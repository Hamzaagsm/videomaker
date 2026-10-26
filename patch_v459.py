#!/usr/bin/env python3
# MEER v4.59 COIN REMOVAL — LOCAL ONLY (sim-meer2).
# GitHub upload / APK build is patch ka kaam NAHI hai.
#
# BASE: built-v458-final.html (MD5 ac90bcff8a2aca92f0c406dbabcefadb)
# — v4.58 final (gate-verified, coin wallet). Base file kabhi modify
# NAHI hoti — copy par kaam karke built-v459-final.html likhi jati hai.
#
# FEATURE (Hamza, 2026-10-26 ~11:10 PKT): "Coin hata do" — poora
# coin wallet system hatao; videos phir se FREE, jaise v4.58 se
# pehle thi. Sirf coin system hata hai — aur KUCH NAHI badla.
#
# TAREEQA: v4.58 JS patch (patch_v458_js.py) ki har tabdeeli ko
# EXACT ulta karo (us ke apne strip-back proof wala tareeqa), phir
# version 4.58 -> 4.59. Aakhir me strip-back proof: version strings
# wapas 4.57 karke built-v457-final.html se BYTE-IDENTICAL hona
# chahiye — is se sabit hota hai ke coin ke ilawa kuch nahi badla.
#
# HATAYA GAYA (v4.58 ne ye sab joda tha):
#   W1) Wallet JS block (meerCoins* functions, localStorage keys
#       meer_coins / meer_coins_code, 100 starting coins, pill +
#       screen render, code setup/verify, top-up)
#   W2) Coin pill (header, fixed top-right, har screen par)
#   W3) Home screen "Coins — Wallet Kholo" button
#   W4) Coins screen (s-coins: balance, owner-code setup, top-up
#       +100/+500/+1000/+10000/custom, wrong-code lock)
#   C1-C8) Charge hooks — meerCoinsCharge() calls (native funnel
#       meerComposeFlowAsync + 7 canvas flows + clipStudioRecord)
#   E1-E13) Early-check hooks — meerCoinsBlock() calls (7 native
#       entries + 6 clip-studio modes)
# Stale localStorage value (meer_coins) phone par reh bhi jaye to
# bekaar hai — koi code use parhta hi nahi.

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / 'built-v458-final.html'
DST = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / 'built-v459-final.html'
assert SRC.resolve() != DST.resolve(), 'SRC aur DST aik nahi ho sakte — patch ROK diya'
if SRC.name == 'built-v458-final.html':
    md5 = hashlib.md5(SRC.read_bytes()).hexdigest()
    assert md5 == 'ac90bcff8a2aca92f0c406dbabcefadb', f'base MD5 galat: {md5} — patch ROK diya'

html = SRC.read_text(encoding='utf-8')
orig = html
removed = []


def rep(old, new, label, count=1):
    global html
    n = html.count(old)
    assert n == count, f'anchor [{label}] {n} dafa mila ({count} chahiye tha) — patch ROK diya'
    html = html.replace(old, new)
    removed.append(label)


# --- v4.58 ke jode hue blocks (patch_v458_js.py se byte-exact) ---
WALLET_JS = "/* ===== MEER v4.58: COIN WALLET =====\n   Har video banane par 10 coins kat te hain — chahe Journey ho,\n   Suspense ho, Real Video ho ya apni script. Balance sirf is phone\n   par localStorage me hai (koi server nahi, koi expiry nahi).\n   Owner (Hamza) apna 4-digit code set karke jitne marzi coins add\n   kar sakta hai — ghalat code par top-up nahi khulta.\n   SAAF BAT: coins se NAYE SCENES nahi bante — scenes library /\n   producer pipeline se aate hain; coins sirf video banane ka\n   wallet hai. Voice engine, vault, manifests — kuch nahi chhua. */\nvar MEER_COIN_COST=10;\nvar MEER_COIN_KEY='meer_coins';\nvar MEER_COIN_CODE_KEY='meer_coins_code';\nfunction meerCoinsGet(){ try{ var v=parseInt(localStorage.getItem(MEER_COIN_KEY),10); if(isNaN(v)||v<0) v=0; return v; }catch(e){ return 0; } }\nfunction meerCoinsSet(v){ try{ localStorage.setItem(MEER_COIN_KEY,String(Math.max(0,Math.floor(v)))); }catch(e){} meerCoinsRender(); }\nfunction meerCoinsRender(){ try{ var n=meerCoinsGet(); var a=document.getElementById('meerCoinNum'); if(a) a.textContent=n; var b=document.getElementById('meerCoinBal'); if(b) b.textContent=n; var em=document.getElementById('meerCoinEmpty'); if(em) em.style.display=(n<MEER_COIN_COST)?'block':'none'; var ok=document.getElementById('meerCoinOk'); if(ok) ok.style.display=(n>=MEER_COIN_COST)?'block':'none'; }catch(e){} }\nfunction meerCoinsInit(){ try{ if(localStorage.getItem(MEER_COIN_KEY)===null) localStorage.setItem(MEER_COIN_KEY,'100'); }catch(e){} meerCoinsRender(); meerCoinsSyncCodeUI(); }\nfunction meerCoinsHas(){ return meerCoinsGet()>=MEER_COIN_COST; }\nfunction meerCoinsBlock(){ if(meerCoinsHas()) return false; meerCoinsShowEmpty(); return true; }\nfunction meerCoinsCharge(){ if(!meerCoinsHas()){ meerCoinsShowEmpty(); return false; } meerCoinsSet(meerCoinsGet()-MEER_COIN_COST); return true; }\nfunction meerCoinsShowEmpty(){ meerCoinsRender(); try{ go('s-coins'); }catch(e){} try{ if(typeof showBanner==='function') showBanner('🪙 Coins khatam — video banane ke liye coins add karo','err'); }catch(e){} }\nfunction meerCoinsOpen(){ meerCoinsRender(); meerCoinsSyncCodeUI(); try{ go('s-coins'); }catch(e){} }\nfunction meerCoinsCodeSet(){ try{ return localStorage.getItem(MEER_COIN_CODE_KEY); }catch(e){ return null; } }\nfunction meerCoinsSyncCodeUI(){ try{ var has=!!meerCoinsCodeSet(); var st=document.getElementById('meerCoinSetup'); if(st) st.style.display=has?'none':'block'; var vf=document.getElementById('meerCoinVerify'); if(vf) vf.style.display=has?'block':'none'; var btn=document.getElementById('meerCoinCodeBtn'); if(btn) btn.textContent=has?'🔓 Code Lagao':'🔑 Owner Code Set Karo'; var tp=document.getElementById('meerCoinTopup'); if(tp) tp.style.display='none'; }catch(e){} }\nfunction meerCoinsCodeGo(){ try{ var inp=document.getElementById('meerCoinCode'); var code=inp?String(inp.value||'').trim():''; var msg=document.getElementById('meerCoinCodeMsg'); var set=function(t){ if(msg) msg.textContent=t; }; if(!/^\\d{4}$/.test(code)){ set('❌ Code 4-digit ka hona chahiye (sirf numbers).'); return; } var saved=meerCoinsCodeSet(); if(!saved){ try{ localStorage.setItem(MEER_COIN_CODE_KEY,code); }catch(e){} set('✅ Owner code set ho gaya — ab coins add karo.'); if(inp) inp.value=''; meerCoinsSyncCodeUI(); var tp=document.getElementById('meerCoinTopup'); if(tp) tp.style.display='block'; return; } if(code===saved){ set('✅ Code theek hai — coins add karo.'); if(inp) inp.value=''; var tp2=document.getElementById('meerCoinTopup'); if(tp2) tp2.style.display='block'; return; } set('❌ Ghalat code — dobara likho.'); }catch(e){} }\nfunction meerCoinsAdd(n){ try{ n=Math.floor(Number(n)||0); if(n<=0) return; meerCoinsSet(meerCoinsGet()+n); if(typeof showBanner==='function') showBanner('✅ '+n+' coins add ho gaye — balance: '+meerCoinsGet()+' coins','ok'); }catch(e){} }\nfunction meerCoinsAddCustom(){ try{ var inp=document.getElementById('meerCoinCustom'); var n=inp?Math.floor(Number(inp.value)||0):0; if(n<=0){ var m=document.getElementById('meerCoinCodeMsg'); if(m) m.textContent='❌ Pehle coins ki tadaad likho (1 ya zyada).'; return; } if(inp) inp.value=''; meerCoinsAdd(n); }catch(e){} }\n(function(){ if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){ meerCoinsInit(); }); else meerCoinsInit(); })();\n/* ===== /MEER v4.58: COIN WALLET ===== */"
COIN_PILL = '<!-- 🪙 Coin wallet pill (v4.58) — har screen par nazar aata hai -->\n<div id="meerCoinPill" onclick="meerCoinsOpen()" style="position:fixed;top:10px;right:10px;z-index:99998;background:linear-gradient(90deg,#b45309,#f59e0b);color:#fff;font-weight:800;padding:8px 14px;border-radius:20px;font-size:15px;box-shadow:0 2px 10px rgba(0,0,0,.45);cursor:pointer">🪙 <span id="meerCoinNum">100</span></div>\n'
HOME_COINS_BTN = '\n    <button class="btn" onclick="meerCoinsOpen()" style="background:linear-gradient(135deg,#b45309,#f59e0b)">🪙 Coins — Wallet Kholo</button>'
COINS_SCREEN = '\n<!-- ============ COINS WALLET (v4.58) ============ -->\n<div class="screen" id="s-coins">\n  <button class="back" onclick="go(\'s-home\')">← Home</button>\n  <h1 style="font-size:26px">🪙 Coins</h1>\n  <p class="sub">Har video banane par 10 coins kat te hain</p>\n  <div class="card">\n    <div style="text-align:center;font-size:48px;line-height:1">🪙</div>\n    <div style="text-align:center;font-size:34px;font-weight:800;margin-top:6px"><span id="meerCoinBal">100</span> coins</div>\n    <p id="meerCoinEmpty" class="sub" style="display:none;color:#fca5a5">⚠️ Coins khatam ho gaye — video banane ke liye pehle coins add karo. Ghabrao nahi, coins add karte hi video ban jayegi.</p>\n    <p id="meerCoinOk" class="sub" style="color:#86efac">✅ Coins maujood hain — video banao!</p>\n    <div class="lbl">🔑 Owner code (sirf Hamza)</div>\n    <p id="meerCoinSetup" class="sub" style="display:none">Pehli dafa apna 4-digit owner code set karo. Ye code sirf is phone par save hota hai — is se coins add honge.</p>\n    <p id="meerCoinVerify" class="sub" style="display:none">Coins add karne ke liye apna owner code likho.</p>\n    <input id="meerCoinCode" type="password" inputmode="numeric" maxlength="4" placeholder="4-digit code" style="width:100%;padding:12px;border-radius:10px;font-size:16px;text-align:center;letter-spacing:6px">\n    <p id="meerCoinCodeMsg" class="sub" style="min-height:18px"></p>\n    <button class="btn" id="meerCoinCodeBtn" onclick="meerCoinsCodeGo()">🔑 Owner Code Set Karo</button>\n    <div id="meerCoinTopup" style="display:none">\n      <div class="lbl" style="margin-top:14px">➕ Coins add karo (jitne marzi)</div>\n      <div style="display:flex;gap:8px;flex-wrap:wrap">\n        <button class="btn btn2" style="flex:1" onclick="meerCoinsAdd(100)">+100</button>\n        <button class="btn btn2" style="flex:1" onclick="meerCoinsAdd(500)">+500</button>\n        <button class="btn btn2" style="flex:1" onclick="meerCoinsAdd(1000)">+1000</button>\n        <button class="btn btn2" style="flex:1" onclick="meerCoinsAdd(10000)">+10000</button>\n      </div>\n      <div style="display:flex;gap:8px;margin-top:8px">\n        <input id="meerCoinCustom" type="number" inputmode="numeric" min="1" placeholder="Apni marzi ke coins" style="flex:1;padding:10px;border-radius:10px;font-size:15px">\n        <button class="btn" onclick="meerCoinsAddCustom()">Add Karo</button>\n      </div>\n      <p class="sub">Coins ki koi expiry nahi — jitne add karo, utne rahenge.</p>\n    </div>\n    <button class="btn btn3" onclick="go(\'s-home\')" style="margin-top:14px">🏠 Home</button>\n  </div>\n  <p class="hint" style="text-align:center">Coins se naye scenes nahi bante — scenes library se aate hain. Coins sirf video banane ka wallet hai.</p>\n</div>\n'

# =====================================================================
# R-W1) Wallet JS block hatao — showBanner ke baad wala hissa
# =====================================================================
rep(
    "  }catch(e){console.log('Banner:',msg);}\n}\n\n" + WALLET_JS,
    "  }catch(e){console.log('Banner:',msg);}\n}",
    'R-W1 wallet JS block',
)

# =====================================================================
# R-W2) Coin pill hatao
# =====================================================================
rep(
    COIN_PILL + "<!-- ============ HOME / AI STUDIO ============ -->",
    "<!-- ============ HOME / AI STUDIO ============ -->",
    'R-W2 coin pill',
)

# =====================================================================
# R-W3) Home screen Coins button hatao
# =====================================================================
rep(
    """<button class="btn" onclick="go('s-videos');meerVideosOpen()" style="background:linear-gradient(135deg,#0ea5e9,#6366f1)">📁 Meri Videos</button>""" + HOME_COINS_BTN,
    """<button class="btn" onclick="go('s-videos');meerVideosOpen()" style="background:linear-gradient(135deg,#0ea5e9,#6366f1)">📁 Meri Videos</button>""",
    'R-W3 home coins button',
)

# =====================================================================
# R-W4) Coins screen hatao — footer abhi v4.58 (ver bump baad me)
# =====================================================================
rep(
    """  <p class="hint" style="text-align:center;margin-top:16px">v4.58 MEER • 100% Free • No watermark</p>
</div>
""" + COINS_SCREEN + """
<!-- ============ AI WORKING ============ -->""",
    """  <p class="hint" style="text-align:center;margin-top:16px">v4.58 MEER • 100% Free • No watermark</p>
</div>

<!-- ============ AI WORKING ============ -->""",
    'R-W4 coins screen',
)

# =====================================================================
# R-C1) DEDUCT hatao — native funnel meerComposeFlowAsync
# =====================================================================
rep(
    """async function meerComposeFlowAsync(segments,fileName,mood){
  if(!meerCoinsCharge()) return 'error:coins_khatam'; // v4.58: video banane par 10 coins — balance kam ho to coins screen dikhao, compose shuru hi na karo
  if(!meerAsyncComposeAvail()) return meerComposeFlow(segments,fileName,mood);""",
    """async function meerComposeFlowAsync(segments,fileName,mood){
  if(!meerAsyncComposeAvail()) return meerComposeFlow(segments,fileName,mood);""",
    'R-C1 funnel deduct',
)

# =====================================================================
# R-C2) DEDUCT hatao — editor FINAL VIDEO (buildVideo)
# =====================================================================
rep(
    """  if(!VSEGS.length){
    alert('🎙️ Pehle awaz banao! Editor → Voice tab → "Awaz Dobara Banao"');
    go('s-editor');etab('voice',document.querySelector('#s-editor .tabs button:nth-child(2)'));
    return;
  }
  if(!meerCoinsCharge())return; // v4.58: editor FINAL VIDEO — render shuru hone se pehle 10 coins
  go('s-make');THUMBS=[];""",
    """  if(!VSEGS.length){
    alert('🎙️ Pehle awaz banao! Editor → Voice tab → "Awaz Dobara Banao"');
    go('s-editor');etab('voice',document.querySelector('#s-editor .tabs button:nth-child(2)'));
    return;
  }
  go('s-make');THUMBS=[];""",
    'R-C2 buildVideo deduct',
)

# =====================================================================
# R-C3) DEDUCT hatao — Talking Cars Studio (carMakeVideo)
# =====================================================================
rep(
    """async function carMakeVideo(silent){
  const lines=carParse();
  if(!lines.length){alert('Script me "Naam: baat" format me lines likho!');return;}
  if(!meerCoinsCharge())return; // v4.58: Talking Cars video — render shuru hone se pehle 10 coins""",
    """async function carMakeVideo(silent){
  const lines=carParse();
  if(!lines.length){alert('Script me "Naam: baat" format me lines likho!');return;}""",
    'R-C3 carMakeVideo deduct',
)

# =====================================================================
# R-C4) DEDUCT hatao — Kids Rhymes (kidMakeVideo)
# =====================================================================
rep(
    """  const text=$('kidScript').value.trim();
  if(!text){alert('Pehle "Script Banao" dabao!');return;}
  if(!meerCoinsCharge())return; // v4.58: Kids video — render shuru hone se pehle 10 coins""",
    """  const text=$('kidScript').value.trim();
  if(!text){alert('Pehle "Script Banao" dabao!');return;}""",
    'R-C4 kidMakeVideo deduct',
)

# =====================================================================
# R-C5) DEDUCT hatao — Motu Patlu (motuMakeVideo)
# =====================================================================
rep(
    """  const text=$('motuScript').value.trim();
  if(!text){alert('Pehle script likho! (Naam: baat)');return;}
  if(!motuSelected.length){alert('Pehle characters chuno!');return;}
  if(!meerCoinsCharge())return; // v4.58: Motu Patlu video — render shuru hone se pehle 10 coins""",
    """  const text=$('motuScript').value.trim();
  if(!text){alert('Pehle script likho! (Naam: baat)');return;}
  if(!motuSelected.length){alert('Pehle characters chuno!');return;}""",
    'R-C5 motuMakeVideo deduct',
)

# =====================================================================
# R-C6) DEDUCT hatao — Real Family (realFamMakeVideo)
# =====================================================================
rep(
    """  const text=$('realFamScript').value.trim();
  if(!text){alert('Pehle script likho! (Naam: baat)');return;}
  if(!meerCoinsCharge())return; // v4.58: Real Family video — render shuru hone se pehle 10 coins""",
    """  const text=$('realFamScript').value.trim();
  if(!text){alert('Pehle script likho! (Naam: baat)');return;}""",
    'R-C6 realFamMakeVideo deduct',
)

# =====================================================================
# R-C7) DEDUCT hatao — Real Video canvas fallback (realMakeVideo)
# =====================================================================
rep(
    """      // Fallback to canvas recording below
    }
  }
  const text=$('realScript').value.trim();
  if(!text){alert('Pehle script likho! (Naam: baat)');return;}
  if(!meerCoinsCharge())return; // v4.58: Real Video canvas fallback — render shuru hone se pehle 10 coins""",
    """      // Fallback to canvas recording below
    }
  }
  const text=$('realScript').value.trim();
  if(!text){alert('Pehle script likho! (Naam: baat)');return;}""",
    'R-C7 realMakeVideo fallback deduct',
)

# =====================================================================
# R-C8) DEDUCT hatao — clip-studio recorder (6 modes, aik funnel)
# =====================================================================
rep(
    """async function clipStudioRecord(segs,cfg){
  if(!meerCoinsCharge())return; // v4.58: story/kids/interview/drama/family/auto video — recording shuru hone se pehle 10 coins
  const E=MODE_EL[cfg.mode];""",
    """async function clipStudioRecord(segs,cfg){
  const E=MODE_EL[cfg.mode];""",
    'R-C8 clipStudioRecord deduct',
)

# =====================================================================
# R-E1) EARLY CHECK hatao — realMakeVideoNative
# =====================================================================
rep(
    """async function realMakeVideoNative(){
  const text=$('realScript').value.trim();
  if(!text){alert('Pehle script likho! (Naam: baat)');return;}
  if(meerCoinsBlock())return; // v4.58: coins kam hon to pehle hi coins screen — lambi awaz ka intezar nahi""",
    """async function realMakeVideoNative(){
  const text=$('realScript').value.trim();
  if(!text){alert('Pehle script likho! (Naam: baat)');return;}""",
    'R-E1 realMakeVideoNative early check',
)

# =====================================================================
# R-E2) EARLY CHECK hatao — suspMakeVideo
# =====================================================================
rep(
    """    var story=suspPickStory();
    if(!story){ alert('Kahaniyan load nahi huin - internet on karke app dobara kholo!'); return; }
    if(meerCoinsBlock())return; // v4.58: coins kam hon to pehle hi coins screen""",
    """    var story=suspPickStory();
    if(!story){ alert('Kahaniyan load nahi huin - internet on karke app dobara kholo!'); return; }""",
    'R-E2 suspMakeVideo early check',
)

# =====================================================================
# R-E3) EARLY CHECK hatao — suspMyMakeVideo
# =====================================================================
rep(
    """    if(!lines.length){ alert('Lines samajh nahi ayin - har line alag likho!'); return; }
    if(meerCoinsBlock())return; // v4.58: coins kam hon to pehle hi coins screen""",
    """    if(!lines.length){ alert('Lines samajh nahi ayin - har line alag likho!'); return; }""",
    'R-E3 suspMyMakeVideo early check',
)

# =====================================================================
# R-E4) EARLY CHECK hatao — meerVaultBuild
# =====================================================================
rep(
    """async function meerVaultBuild(lines,man,hash){
  try{
    if(typeof RealClipBridge==='undefined'||typeof RealClipBridge.composeVideo!=='function') return false;
    if(meerCoinsBlock())return false; // v4.58: coins kam hon to pehle hi coins screen""",
    """async function meerVaultBuild(lines,man,hash){
  try{
    if(typeof RealClipBridge==='undefined'||typeof RealClipBridge.composeVideo!=='function') return false;""",
    'R-E4 meerVaultBuild early check',
)

# =====================================================================
# R-E5) EARLY CHECK hatao — journeyV3Inner
# =====================================================================
rep(
    """    if(!plan.length){ alert('Is car ki stories nahi milin!'); return; }
    if(meerCoinsBlock())return; // v4.58: coins kam hon to pehle hi coins screen""",
    """    if(!plan.length){ alert('Is car ki stories nahi milin!'); return; }""",
    'R-E5 journeyV3Inner early check',
)

# =====================================================================
# R-E6) EARLY CHECK hatao — adventureMakeVideo
# =====================================================================
rep(
    """async function adventureMakeVideo(){
  try{
    if(typeof RealClipBridge==='undefined'||typeof RealClipBridge.composeVideo!=='function'){ alert('Ye feature MEER app me chalega!'); return; }
    if(meerCoinsBlock())return; // v4.58: coins kam hon to pehle hi coins screen""",
    """async function adventureMakeVideo(){
  try{
    if(typeof RealClipBridge==='undefined'||typeof RealClipBridge.composeVideo!=='function'){ alert('Ye feature MEER app me chalega!'); return; }""",
    'R-E6 adventureMakeVideo early check',
)

# =====================================================================
# R-E7) EARLY CHECK hatao — singleJourneyClipMode
# =====================================================================
rep(
    """    var who=prompt('Kon si car ki journey? Rayo / Bella / Rusty','Rayo');
    if(!who)return;
    if(meerCoinsBlock())return; // v4.58: coins kam hon to pehle hi coins screen""",
    """    var who=prompt('Kon si car ki journey? Rayo / Bella / Rusty','Rayo');
    if(!who)return;""",
    'R-E7 singleJourneyClipMode early check',
)

# =====================================================================
# R-E8..E13) EARLY CHECK hatao — clip-studio modes (story/kids/
# interview/drama/family/auto)
# =====================================================================
for _mode, _alert in [
    ('story', "alert('Pehle kahani likho!')"),
    ('kids', "alert('Pehle kahani likho!')"),
    ('interview', "alert('Pehle script likho! (Host: / Guest:)')"),
    ('drama', "alert('Pehle kahani likho!')"),
    ('family', "alert('Pehle script likho! (Woman: / Man: / Baby:)')"),
    ('auto', "alert('Pehle KAHANI BANAO dabao!')"),
]:
    _old = ("  const E=MODE_EL.%s,mode='%s';\n"
            "  const text=$(E.script).value.trim();\n"
            "  if(!text){%s;return;}" % (_mode, _mode, _alert))
    _new = _old + "\n  if(meerCoinsBlock())return; // v4.58: coins kam hon to pehle hi coins screen"
    rep(_new, _old, f'R-E-{_mode} early check')

# =====================================================================
# Version bump: 4.58 -> 4.59 (v4.57 wale tareeqe se — 3 anchors)
# =====================================================================
rep('const APP_VER="4.58";',
    'const APP_VER="4.59";',
    'V1 APP_VER')

rep('>v4.58 MEER • 100% Free • No watermark<',
    '>v4.59 MEER • 100% Free • No watermark<',
    'V2 footer')

rep('id="verLabel" style="opacity:.6;font-size:12px">v4.58<',
    'id="verLabel" style="opacity:.6;font-size:12px">v4.59<',
    'V3 verLabel static')

# ---------- Aakhri asserts ----------
# Coin system: kuch bhi baqi nahi (v4.57 base me bhi ye 0 thay)
assert html.count('meerCoins') == 0, 'meerCoins baqi hai'
assert html.count('meer_coins') == 0, 'meer_coins baqi hai'
assert html.count('MEER_COIN') == 0, 'MEER_COIN baqi hai'
assert html.count('s-coins') == 0, 's-coins baqi hai'
assert html.count('🪙') == 0, 'coin emoji baqi hai'
assert html.count('error:coins_khatam') == 0, 'coins_khatam error baqi hai'
assert html.count('Coin') == 0, 'Coin baqi hai'
assert html.count('coin') == 0, 'coin baqi hai'
# Version 4.59
assert html.count('const APP_VER="4.59";') == 1, 'APP_VER 4.59 nahi'
assert html.count('const APP_VER="4.58"') == 0, 'APP_VER 4.58 baqi hai'
assert html.count('v4.59 MEER') == 1 and html.count('v4.58 MEER') == 0, 'footer version ghalat'
assert html.count('id="verLabel" style="opacity:.6;font-size:12px">v4.59<') == 1, 'verLabel 4.59 nahi'
# Untouched guards (v4.57 fix + v4.56 flows + voice + vault)
assert html.count('ONLINE_CARS && ONLINE_CARS.length >= 3') == 1, 'v4.57 null-guard maujood hona chahiye'
assert html.count("typeof ONLINE_CARS !== 'undefined' && ONLINE_CARS.length") == 0, 'purana crash pattern wapas nahi ana chahiye'
assert html.count('meerQueueSubmit') == 2, 'v4.56 auto-submit flow chhua gaya — patch ROK diya'
assert html.count('suspQueueBtn') == 2, 'v4.56 queue button chhua gaya — patch ROK diya'
assert html.count('function meerVaultHash(') == 1, 'vault hash chhua gaya — patch ROK diya'
assert html.count('function speakSeg(') == 1, 'voice engine (speakSeg) chhua gaya — patch ROK diya'
assert html.count('function nativeSpeak(') == 1, 'voice engine (nativeSpeak) chhua gaya — patch ROK diya'
assert html.count('meerComposeFlowAsync(') == 10, 'compose funnel call sites badal gaye (9 calls + 1 def)'
assert html.count('async function clipStudioRecord(segs,cfg){') == 1, 'clipStudioRecord def aik dafa honi chahiye'
# Strip-back proof: version strings wapas 4.57 karke v4.57 base se
# byte-compare — coin removal ke ilawa KUCH nahi badla hona chahiye.
_base457 = HERE / 'built-v457-final.html'
if _base457.exists():
    _chk = (html.replace('const APP_VER="4.59";', 'const APP_VER="4.57";')
                .replace('>v4.59 MEER • 100% Free • No watermark<', '>v4.57 MEER • 100% Free • No watermark<')
                .replace('id="verLabel" style="opacity:.6;font-size:12px">v4.59<', 'id="verLabel" style="opacity:.6;font-size:12px">v4.57<'))
    assert _chk == _base457.read_text(encoding='utf-8'), 'STRIP-BACK FAIL — coin removal ke ilawa bhi kuch badla'
    print('strip-back proof: v4.57 base se byte-identical (sirf 3 version strings 4.57->4.59)')
else:
    print('NOTE: built-v457-final.html maujood nahi — strip-back proof skip (output par asar nahi)')

DST.write_text(html, encoding='utf-8')
print('removed:', ', '.join(removed))
print('WROTE', DST, f'({len(html)} chars; base se {len(html) - len(orig):+d})')
print('MD5:', hashlib.md5(DST.read_bytes()).hexdigest())
