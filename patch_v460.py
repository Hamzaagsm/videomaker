#!/usr/bin/env python3
# MEER v4.60 patch (HTML) -- repo-form ship script (CI-safe).
#
# Local chain (tasalli-verified) ka repo roop: local patch_v460.py
# (sim-meer2) ko STAGE_RM me VERBATIM embedded kiya gaya hai — stage
# ka logic, anchors, asserts aur strip-back proof bilkul wahi jo
# local built-v460-final.html (MD5 fe3f3805034ce75f3cd7f6769fba2894)
# banane me istemal hue.
#
# FEATURE (Hamza, 2026-10-26 ~12:57 PKT): in-app video loop — script
# app se jaye, video app me wapas aaye. L1: processing-row vault
# check (meerQueueRefresh); L2: 60s auto-refresh + "Dobara check
# karo" button + imandari wala intezar note. Sirf ADDITIVE — voice
# engine, vault hash, queue submit, compose funnel, coin system
# (pehle hi hata hua) — kuch nahi chhua. Version 4.59 -> 4.60.
#
# FIX NOTE (2026-10-26): pehli repo-form koshish (v4.59, commit
# 7f3ffd7) me LOCAL-ONLY stage seedha upload ho gaya tha — wo repo
# root me 'built-v458-final.html' dhoondta hai, jo CI me hoti hi
# nahi (live file android/app/src/main/assets/www/index.html hai),
# is liye CI run #366 "Apply v4.59 patch" step par FileNotFoundError
# se fail hua. Ye driver wahi ghalti dobara nahi karta: v4.58/v4.59
# wale driver ki tarah live target ko temp dir me
# 'built-v459-final.html' ke naam se deta hai, jis se stage ka
# MD5 guard (a7504b793b286edca1fe851a59c1a72b) bilkul local chain
# ki tarah fire hota hai.
# Chalana: repo root se  python3 patch_v460.py
# Target: android/app/src/main/assets/www/index.html (workflow ki
# "Sync web assets" + v389..v459 steps ke BAAD ki haalat par).
# Is version me manifest ki KOI tabdeeli nahi hai, Java ki bhi nahi.

import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HP = ROOT / 'android/app/src/main/assets/www/index.html'

EXPECTED_FINAL_MD5 = 'fe3f3805034ce75f3cd7f6769fba2894'

STAGE_RM = '#!/usr/bin/env python3\n# MEER v4.60 IN-APP VIDEO LOOP — LOCAL ONLY (sim-meer2).\n# GitHub upload / APK build is patch ka kaam NAHI hai.\n#\n# BASE: built-v459-final.html (MD5 a7504b793b286edca1fe851a59c1a72b)\n# — v4.59 final (gate-verified, coin-free). Base file kabhi modify\n# NAHI hoti — copy par kaam karke built-v460-final.html likhi jati hai.\n#\n# FEATURE (Hamza, 2026-10-26 ~12:57 PKT): "Jaisy tum video generate\n# krty ho waisa he system kiun nai dalty ho — wahi same cheez add\n# krdo." Script app se jaye, video app me wapas aaye.\n#\n# HONEST ARCHITECTURE (patch me yehi laagu hai): mera built-in media\n# pipeline hosted service hai — APK me copy NAHI ho sakta. Portable\n# engine LTX-Video 2B on Kaggle hai (run f45b5d1a se prove hua):\n# app "Library ko Bhejo" -> story_queue -> Kaggle runner -> vault ->\n# app me video. Is patch me sirf APP wala hissa hai — vault/queue\n# ka contract (hash, manifest, clips) bilkul waisa hi hai jaisa\n# v4.49/v4.56 se hai; runner vault publish karta hai, app usi ko\n# parhti hai. Koi naya engine, koi naya server, koi naya flow nahi.\n#\n# BADLA GAYA (sab ADDITIVE — koi maujooda function dobara nahi likha):\n#   L1) Processing wali row ka vault bhi check karo — meerQueueRefresh\n#       ki else branch (status new/processing) pehle vault dekhe baghair\n#       "Ban rahi hai" dikhati thi. Ab done ka PATCH miss ho to bhi\n#       vault tayyar hone par "Tayyar hai" + "Video banao" aa jayega.\n#   L2) "Meri Kahaniyan" list khud-ba-khud taaza hoti rahe — 60 second\n#       ka timer (sirf jab page nazar aa raha ho), plus "Dobara check\n#       karo" button, plus imandari wala intezar note (har scene ~5\n#       minute; 24 lines ≈ 2 ghante — koi jhooti fori video nahi).\n#   V1-V3) Version 4.59 -> 4.60 (v4.59 wale tareeqe se — 3 anchors).\n#\n# NAHI CHHUA: voice engine (speakSeg/nativeSpeak/meerMeriSpeakSeg),\n# vault hash (meerVaultHash), queue submit (meerQueueSubmit), compose\n# funnel (meerComposeFlowAsync), vault build (meerVaultBuild), coin\n# system (v4.59 me pehle hi hata diya — zero markers barkarar).\n\nimport hashlib\nimport sys\nfrom pathlib import Path\n\nHERE = Path(__file__).resolve().parent\nSRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / \'built-v459-final.html\'\nDST = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / \'built-v460-final.html\'\nassert SRC.resolve() != DST.resolve(), \'SRC aur DST aik nahi ho sakte — patch ROK diya\'\nif SRC.name == \'built-v459-final.html\':\n    md5 = hashlib.md5(SRC.read_bytes()).hexdigest()\n    assert md5 == \'a7504b793b286edca1fe851a59c1a72b\', f\'base MD5 galat: {md5} — patch ROK diya\'\n\nhtml = SRC.read_text(encoding=\'utf-8\')\norig = html\nadded = []\n\n\ndef rep(old, new, label, count=1):\n    global html\n    n = html.count(old)\n    assert n == count, f\'anchor [{label}] {n} dafa mila ({count} chahiye tha) — patch ROK diya\'\n    html = html.replace(old, new)\n    added.append(label)\n\n\n# =====================================================================\n# L1) Processing wali row ka vault bhi check karo\n# =====================================================================\nP1_OLD = """    }else{\n      statusHtml=\'⏳ Ban rahi hai\';\n    }"""\nP1_NEW = """    }else{\n      ready=await meerQueueVaultReady(row.hash,lines); // v4.60: processing wali row ka vault bhi check karo — done ka PATCH miss ho to bhi Tayyar dikhe\n      statusHtml=ready?\'✅ Tayyar hai\':\'⏳ Ban rahi hai\';\n    }"""\nrep(P1_OLD, P1_NEW, \'L1 processing-row vault check\')\n\n# =====================================================================\n# L2) Intezar note + Dobara check karo button + 60s auto-refresh\n# =====================================================================\nP2_OLD = """    var list=document.createElement(\'div\');\n    list.id=\'meerQueueList\'; list.style.cssText=\'margin-top:10px;text-align:left;\';\n    mb.parentNode.insertBefore(list,btn.nextSibling);\n    meerQueueRefresh();"""\nP2_NEW = """    var note=document.createElement(\'div\');\n    note.id=\'meerQueueWaitNote\'; note.style.cssText=\'margin-top:8px;font-size:12px;color:#9ca3af;text-align:left;\';\n    note.textContent=\'⏳ Video banne me waqt lagta hai — Kaggle free GPU par har scene ~5 minute; 24 lines ≈ 2 ghante. App khud check karti rahegi, tayyar hote hi "✅ Tayyar hai" + "🎬 Video banao" aa jayega.\';\n    mb.parentNode.insertBefore(note,btn.nextSibling);\n    var list=document.createElement(\'div\');\n    list.id=\'meerQueueList\'; list.style.cssText=\'margin-top:10px;text-align:left;\';\n    mb.parentNode.insertBefore(list,note.nextSibling);\n    var chk=document.createElement(\'button\');\n    chk.id=\'meerQueueCheckBtn\'; chk.className=\'btn\'; chk.style.cssText=\'width:100%;margin-top:8px;background:#1f2937;color:#e5e7eb;\';\n    chk.textContent=\'🔄 Dobara check karo\';\n    chk.onclick=function(){ try{ suspSetStatus(\'Check ho raha hai…\'); }catch(e){} meerQueueRefresh(); };\n    mb.parentNode.insertBefore(chk,list.nextSibling);\n    meerQueueRefresh();\n    if(!window._meerQueueAutoIv){ window._meerQueueAutoIv=setInterval(function(){ try{ if(document.visibilityState!==\'visible\')return; var l=document.getElementById(\'meerQueueList\'); if(!l||!l.offsetParent)return; meerQueueRefresh(); }catch(e){} },60000); } // v4.60: Meri Kahaniyan list khud-ba-khud taaza hoti rahe"""\nrep(P2_OLD, P2_NEW, \'L2 wait note + check button + auto-refresh\')\n\n# =====================================================================\n# Version bump: 4.59 -> 4.60 (v4.59 wale tareeqe se — 3 anchors)\n# =====================================================================\nrep(\'const APP_VER="4.59";\',\n    \'const APP_VER="4.60";\',\n    \'V1 APP_VER\')\n\nrep(\'>v4.59 MEER • 100% Free • No watermark<\',\n    \'>v4.60 MEER • 100% Free • No watermark<\',\n    \'V2 footer\')\n\nrep(\'id="verLabel" style="opacity:.6;font-size:12px">v4.59<\',\n    \'id="verLabel" style="opacity:.6;font-size:12px">v4.60<\',\n    \'V3 verLabel static\')\n\n# ---------- Aakhri asserts ----------\n# Coin system: kuch bhi baqi nahi (v4.59 base me bhi ye 0 thay)\nassert html.count(\'meerCoins\') == 0, \'meerCoins baqi hai\'\nassert html.count(\'meer_coins\') == 0, \'meer_coins baqi hai\'\nassert html.count(\'MEER_COIN\') == 0, \'MEER_COIN baqi hai\'\nassert html.count(\'s-coins\') == 0, \'s-coins baqi hai\'\nassert html.count(\'🪙\') == 0, \'coin emoji baqi hai\'\nassert html.count(\'error:coins_khatam\') == 0, \'coins_khatam error baqi hai\'\nassert html.count(\'Coin\') == 0, \'Coin baqi hai\'\nassert html.count(\'coin\') == 0, \'coin baqi hai\'\n# Version 4.60\nassert html.count(\'const APP_VER="4.60";\') == 1, \'APP_VER 4.60 nahi\'\nassert html.count(\'const APP_VER="4.59"\') == 0, \'APP_VER 4.59 baqi hai\'\nassert html.count(\'>v4.60 MEER • 100% Free • No watermark<\') == 1 and html.count(\'>v4.59 MEER\') == 0, \'footer version ghalat\'\nassert html.count(\'id="verLabel" style="opacity:.6;font-size:12px">v4.60<\') == 1, \'verLabel 4.60 nahi\'\nassert html.count(\'4.59\') == 0, \'4.59 kahin baqi hai\'\n# Naye markers — sirf aik dafa (timer guard bhi aik dafa)\nassert html.count(\'meerQueueWaitNote\') == 1, \'wait note id aik dafa honi chahiye\'\nassert html.count(\'meerQueueCheckBtn\') == 1, \'check button id aik dafa honi chahiye\'\nassert html.count(\'Dobara check karo\') == 1, \'check button text aik dafa hona chahiye\'\nassert html.count(\'_meerQueueAutoIv\') == 2, \'auto-refresh guard 2 dafa hona chahiye (check + set)\'\nassert html.count(\'Video banne me waqt lagta hai\') == 1, \'intezar note aik dafa hona chahiye\'\nassert html.count(\'processing wali row ka vault bhi check karo\') == 1, \'L1 comment aik dafa hona chahiye\'\n# Untouched guards (v4.56 flows + voice + vault + compose)\nassert html.count(\'ONLINE_CARS && ONLINE_CARS.length >= 3\') == 1, \'v4.57 null-guard maujood hona chahiye\'\nassert html.count(\'function meerVaultHash(\') == 1, \'vault hash chhua gaya — patch ROK diya\'\nassert html.count(\'function speakSeg(\') == 1, \'voice engine (speakSeg) chhua gaya — patch ROK diya\'\nassert html.count(\'function nativeSpeak(\') == 1, \'voice engine (nativeSpeak) chhua gaya — patch ROK diya\'\nassert html.count(\'function meerQueueSubmit(\') == 1, \'queue submit chhua gaya — patch ROK diya\'\nassert html.count(\'function meerQueueRefresh(\') == 1, \'queue refresh def aik dafa honi chahiye\'\nassert html.count(\'function meerQueueVaultReady(\') == 1, \'vault-ready def aik dafa honi chahiye\'\nassert html.count(\'function meerVaultBuild(\') == 1, \'vault build def aik dafa honi chahiye\'\nassert html.count(\'meerComposeFlowAsync(\') == 10, \'compose funnel call sites badal gaye (9 calls + 1 def)\'\nassert html.count(\'suspQueueBtn\') == 2, \'v4.56 queue button chhua gaya — patch ROK diya\'\n# Strip-back proof: jode hue blocks hatao + version strings wapas\n# 4.59 karo — baqi sab kuch v4.59 base se BYTE-IDENTICAL hona chahiye.\n_base459 = HERE / \'built-v459-final.html\'\nif _base459.exists():\n    _chk = (html.replace(P1_NEW, P1_OLD)\n                .replace(P2_NEW, P2_OLD)\n                .replace(\'const APP_VER="4.60";\', \'const APP_VER="4.59";\')\n                .replace(\'>v4.60 MEER • 100% Free • No watermark<\', \'>v4.59 MEER • 100% Free • No watermark<\')\n                .replace(\'id="verLabel" style="opacity:.6;font-size:12px">v4.60<\', \'id="verLabel" style="opacity:.6;font-size:12px">v4.59<\'))\n    assert _chk == _base459.read_text(encoding=\'utf-8\'), \'STRIP-BACK FAIL — L1/L2/version ke ilawa bhi kuch badla\'\n    print(\'strip-back proof: v4.59 base se byte-identical (sirf L1 + L2 + 3 version strings 4.59->4.60)\')\nelse:\n    print(\'NOTE: built-v459-final.html maujood nahi — strip-back proof skip (output par asar nahi)\')\n\nDST.write_text(html, encoding=\'utf-8\')\nprint(\'added:\', \', \'.join(added))\nprint(\'WROTE\', DST, f\'({len(html)} chars; base se {len(html) - len(orig):+d})\')\nprint(\'MD5:\', hashlib.md5(DST.read_bytes()).hexdigest())\n'

def run_stage(code, name, args, cwd):
    p = cwd / name
    p.write_text(code, encoding='utf-8')
    r = subprocess.run([sys.executable, str(p)] + [str(a) for a in args],
                       cwd=str(cwd), capture_output=True, text=True)
    print(r.stdout, end='')
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        raise SystemExit(f'{name} FAIL (exit {r.returncode}) -- patch ROK diya')


def main():
    assert HP.exists(), f'target nahi mila: {HP}'
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        base = td / 'built-v459-final.html'
        base.write_bytes(HP.read_bytes())
        run_stage(STAGE_RM, 'stage_v460.py', [base, td / 'built-v460-final.html'], td)
        final = td / 'built-v460-final.html'
        md5 = hashlib.md5(final.read_bytes()).hexdigest()
        assert md5 == EXPECTED_FINAL_MD5, f'final MD5 galat: {md5} -- patch ROK diya'
        HP.write_bytes(final.read_bytes())
        print('v4.60 patch OK -- final MD5:', md5)


if __name__ == '__main__':
    main()
