#!/usr/bin/env python3
# MEER v4.62 patch (HTML) -- repo-form ship script (CI-safe).
#
# Local chain (tasalli-verified) ka repo roop: local patch_v462.py
# (sim-meer2) ko STAGE_RM me VERBATIM embedded kiya gaya hai — stage
# ka logic, anchors, asserts aur strip-back proof bilkul wahi jo
# local built-v462-final.html (MD5 9e1b4765c07f5f0155ee9f8826449c15)
# banane me istemal hue.
#
# KAM (v4.62): SIRF version bump 4.61 -> 4.62 (3 anchors: APP_VER,
# footer, verLabel static). Koi behavior nahi badalta. Watermark ka
# asal fix JAVA side hai (patch_v462_java.py, built-v462.java) — is
# JS patch me us ka kuch nahi. F1 gate (v4.61, khamosh chhoti video
# band), voice engine, vault hash, queue submit, compose funnel —
# kuch nahi chhua. '4.61' sirf aik F1 history comment me rehta hai
# (tareekh, version nahi), '4.60' ke 2 feature comments bhi.
#
# Chalana: repo root se  python3 patch_v462.py
# Target: android/app/src/main/assets/www/index.html (workflow ki
# "Sync web assets" + v389..v461 steps ke BAAD ki haalat par).
# Is version me manifest ki KOI tabdeeli nahi hai.

import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HP = ROOT / 'android/app/src/main/assets/www/index.html'

EXPECTED_FINAL_MD5 = '9e1b4765c07f5f0155ee9f8826449c15'

STAGE_RM = '#!/usr/bin/env python3\n# MEER v4.62 JS VERSION BUMP — LOCAL ONLY (sim-meer2).\n# GitHub upload / APK build is patch ka kaam NAHI hai.\n#\n# BASE: built-v461-final.html (MD5 e4772e5af73320ccc2bce380ccbe03a7)\n# — v4.61 final (Journey short-video fix, gate-verified, coin-free).\n# Base file kabhi modify NAHI hoti — copy par kaam karke\n# built-v462-final.html likhi jati hai.\n#\n# KAM: SIRF version bump 4.61 -> 4.62 (v4.59/v4.60/v4.61 wale\n# tareeqe se — 3 anchors: APP_VER, footer, verLabel static).\n# KUCH AUR NAHI BADALTA: na F1 ka text, na voice engine, na vault,\n# na queue, na compose funnel, na koi behavior. Watermark ka asal\n# fix JAVA side hai (patch_v462_java.py, built-v462.java) — is JS\n# patch me us ka kuch nahi.\n#\n# NOTE: \'4.61\' ka aik occurrence rehta hai — F1 wala history comment\n# (line ~6845, "/* v4.61: KHAMOSH CHHOTI VIDEO BAND ...") — wo\n# tareekh hai, version string nahi; v4.61 ke test ki tarah (wahan\n# \'4.60\' ke 2 feature comments rehte thay) use chhera nahi gaya.\n# \'4.60\' ke 2 comments bhi waisay hi rehte hain.\n#\n# NAHI CHHUA: F1 gate (jMissDl / half-duration stop / paigham),\n# voice engine (speakSeg/nativeSpeak/meerMeriSpeakSeg), vault hash\n# (meerVaultHash), queue submit/refresh (meerQueueSubmit/\n# meerQueueRefresh/meerQueueVaultReady), vault build (meerVaultBuild),\n# compose funnel (meerComposeFlowAsync), wait-loop progress\n# ("X baqi"), coin system (zero markers barkarar).\n\nimport hashlib\nimport sys\nfrom pathlib import Path\n\nHERE = Path(__file__).resolve().parent\nSRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / \'built-v461-final.html\'\nDST = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / \'built-v462-final.html\'\nassert SRC.resolve() != DST.resolve(), \'SRC aur DST aik nahi ho sakte — patch ROK diya\'\nif SRC.name == \'built-v461-final.html\':\n    md5 = hashlib.md5(SRC.read_bytes()).hexdigest()\n    assert md5 == \'e4772e5af73320ccc2bce380ccbe03a7\', f\'base MD5 galat: {md5} — patch ROK diya\'\n\nhtml = SRC.read_text(encoding=\'utf-8\')\norig = html\nadded = []\n\n\ndef rep(old, new, label, count=1):\n    global html\n    n = html.count(old)\n    assert n == count, f\'anchor [{label}] {n} dafa mila ({count} chahiye tha) — patch ROK diya\'\n    html = html.replace(old, new)\n    added.append(label)\n\n\n# =====================================================================\n# Version bump: 4.61 -> 4.62 (v4.61 wale tareeqe se — 3 anchors)\n# =====================================================================\nrep(\'const APP_VER="4.61";\',\n    \'const APP_VER="4.62";\',\n    \'V1 APP_VER\')\n\nrep(\'>v4.61 MEER • 100% Free • No watermark<\',\n    \'>v4.62 MEER • 100% Free • No watermark<\',\n    \'V2 footer\')\n\nrep(\'id="verLabel" style="opacity:.6;font-size:12px">v4.61<\',\n    \'id="verLabel" style="opacity:.6;font-size:12px">v4.62<\',\n    \'V3 verLabel static\')\n\n# ---------- Aakhri asserts ----------\n# Coin system: kuch bhi baqi nahi (v4.61 base me bhi ye 0 thay)\nassert html.count(\'meerCoins\') == 0, \'meerCoins baqi hai\'\nassert html.count(\'meer_coins\') == 0, \'meer_coins baqi hai\'\nassert html.count(\'MEER_COIN\') == 0, \'MEER_COIN baqi hai\'\nassert html.count(\'s-coins\') == 0, \'s-coins baqi hai\'\nassert html.count(\'🪙\') == 0, \'coin emoji baqi hai\'\nassert html.count(\'error:coins_khatam\') == 0, \'coins_khatam error baqi hai\'\nassert html.count(\'Coin\') == 0, \'Coin baqi hai\'\nassert html.count(\'coin\') == 0, \'coin baqi hai\'\n# Version 4.62 (3 anchors); \'4.61\' sirf aik F1 history comment me\n# rehta hai (tareekh, version nahi) — wahan se hatana ghalat hoga;\n# \'4.60\' ke 2 feature comments bhi waisay hi rehte hain\nassert html.count(\'const APP_VER="4.62";\') == 1, \'APP_VER 4.62 nahi\'\nassert html.count(\'const APP_VER="4.61";\') == 0, \'APP_VER 4.61 baqi hai\'\nassert html.count(\'>v4.62 MEER • 100% Free • No watermark<\') == 1 and html.count(\'>v4.61 MEER\') == 0, \'footer version ghalat\'\nassert html.count(\'id="verLabel" style="opacity:.6;font-size:12px">v4.62<\') == 1, \'verLabel 4.62 nahi\'\nassert html.count(\'id="verLabel" style="opacity:.6;font-size:12px">v4.61<\') == 0, \'verLabel 4.61 baqi hai\'\nassert html.count(\'4.62\') == 3, \'4.62 sirf 3 version anchors me hona chahiye\'\nassert html.count(\'4.61\') == 1, \'4.61 sirf aik F1 history comment me rehna chahiye\'\nassert html.count(\'/* v4.61:\') == 1, \'F1 history comment aik hi hona chahiye\'\nassert html.count(\'4.60\') == 2, \'4.60 ke 2 v4.60 comments ke ilawa kahin nahi hona chahiye\'\nassert html.count(\'// v4.60:\') == 2, \'v4.60 feature comments 2 hi hone chahiye\'\n# F1 gate — bilkul waisa hi (v4.61 wala fix chhua nahi gaya)\nassert html.count(\'KHAMOSH CHHOTI VIDEO BAND\') == 1, \'F1 comment aik dafa hona chahiye\'\nassert html.count(\'jMissDl>0\') == 1, \'F1 gate aik dafa hona chahiye\'\nassert html.count(\'jReadySec<jPlanSec/2\') == 1, \'aadhi-lambai wali shart aik dafa honi chahiye\'\nassert html.count("Sirf \'+segments.length+\'/\'+plan.length+\' scenes tayyar hain") == 1, \'F1 paigham aik dafa hona chahiye\'\nassert html.count(\'video har dafa lambi hoti jayegi!\') == 1, \'dobara-dabao wala jumla aik dafa hona chahiye\'\n# Untouched guards (v4.61 flows + voice + vault + compose + journey)\nassert html.count(\'ONLINE_CARS && ONLINE_CARS.length >= 3\') == 1, \'v4.57 null-guard maujood hona chahiye\'\nassert html.count(\'function meerVaultHash(\') == 1, \'vault hash chhua gaya — patch ROK diya\'\nassert html.count(\'function speakSeg(\') == 1, \'voice engine (speakSeg) chhua gaya — patch ROK diya\'\nassert html.count(\'function nativeSpeak(\') == 1, \'voice engine (nativeSpeak) chhua gaya — patch ROK diya\'\nassert html.count(\'function meerQueueSubmit(\') == 1, \'queue submit chhua gaya — patch ROK diya\'\nassert html.count(\'function meerQueueRefresh(\') == 1, \'queue refresh def aik dafa honi chahiye\'\nassert html.count(\'function meerQueueVaultReady(\') == 1, \'vault-ready def aik dafa honi chahiye\'\nassert html.count(\'function meerVaultBuild(\') == 1, \'vault build def aik dafa honi chahiye\'\nassert html.count(\'meerComposeFlowAsync(\') == 10, \'compose funnel call sites badal gaye (9 calls + 1 def)\'\nassert html.count(\'suspQueueBtn\') == 2, \'v4.56 queue button chhua gaya — patch ROK diya\'\nassert html.count(\'function journeyV3Inner(){\') == 1, \'journeyV3Inner def aik dafa honi chahiye\'\nassert html.count("if(!advOk(clip)||usedJ[clip]){ continue; }") == 1, \'skip wali line chhui gayi — patch ROK diya\'\nassert html.count("if(segments.length<3){ alert(\'Kuch scenes abhi download nahi hue") == 1, \'<3 wala guard aik dafa hona chahiye\'\nassert html.count("advSetStatus(\'Scenes download ho rahe hain... \'+left.length+\' baqi\');") == 1, \'wait-loop progress ("X baqi") chhui gayi — patch ROK diya\'\nassert html.count(\'while(waited<900000)\') == 3, \'15-min wait loops 3 hone chahiye (suspEnsure + vault + journey)\'\nassert html.count(\'meerQueueWaitNote\') == 1, \'v4.60 wait note chhua gaya — patch ROK diya\'\nassert html.count(\'meerQueueCheckBtn\') == 1, \'v4.60 check button chhua gaya — patch ROK diya\'\nassert html.count(\'_meerQueueAutoIv\') == 2, \'v4.60 auto-refresh guard chhua gaya — patch ROK diya\'\n# Strip-back proof: version strings wapas 4.61 karo — baqi sab kuch\n# v4.61 base se BYTE-IDENTICAL hona chahiye.\n_base461 = HERE / \'built-v461-final.html\'\nif _base461.exists():\n    _chk = (html.replace(\'const APP_VER="4.62";\', \'const APP_VER="4.61";\')\n                .replace(\'>v4.62 MEER • 100% Free • No watermark<\', \'>v4.61 MEER • 100% Free • No watermark<\')\n                .replace(\'id="verLabel" style="opacity:.6;font-size:12px">v4.62<\', \'id="verLabel" style="opacity:.6;font-size:12px">v4.61<\'))\n    assert _chk == _base461.read_text(encoding=\'utf-8\'), \'STRIP-BACK FAIL — version ke ilawa bhi kuch badla\'\n    print(\'strip-back proof: v4.61 base se byte-identical (sirf 3 version strings 4.61->4.62)\')\nelse:\n    print(\'NOTE: built-v461-final.html maujood nahi — strip-back proof skip (output par asar nahi)\')\n\nDST.write_text(html, encoding=\'utf-8\')\nprint(\'added:\', \', \'.join(added))\nprint(\'WROTE\', DST, f\'({len(html)} chars; base se {len(html) - len(orig):+d})\')\nprint(\'MD5:\', hashlib.md5(DST.read_bytes()).hexdigest())\n'

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
        base = td / 'built-v461-final.html'
        base.write_bytes(HP.read_bytes())
        run_stage(STAGE_RM, 'stage_v462.py', [base, td / 'built-v462-final.html'], td)
        final = td / 'built-v462-final.html'
        md5 = hashlib.md5(final.read_bytes()).hexdigest()
        assert md5 == EXPECTED_FINAL_MD5, f'final MD5 galat: {md5} -- patch ROK diya'
        HP.write_bytes(final.read_bytes())
        print('v4.62 patch OK -- final MD5:', md5)


if __name__ == '__main__':
    main()
