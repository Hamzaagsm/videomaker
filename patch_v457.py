#!/usr/bin/env python3

# MEER v4.57 patch (HTML) -- repo-form ship script.
#
# Local chain (tasalli-verified) ka repo roop: patch_v457_js ->
# patch_v457_ver. Har stage ka source NECHAY VERBATIM embedded hai
# (anchors/asserts bilkul wahi jo local built-v457-final.html
# (MD5 8bb73eccfa2115eb57a9339c234a4641) banane me istemal hue).
#
# FIX (v4.56 phone bug, Hamza ki screenshot 2026-10-25): REAL VIDEO
# BANAO par "Cannot read properties of null (reading 'length')" --
# ONLINE_CARS null tha (cars.json kamzoor network par load nahi hua)
# aur typeof-guard null par guzar jata hai. ONE-LINE null-guard fix;
# null ho to built-in car istemal hoti hai, video banti hai.
#
# Stage feeding: dono stages argv lete hain -- driver CI target ko
# temp dir me 'built-v456-final.html' ke naam se deta hai, jis se
# js stage ka MD5 guard (d8c087955b3960a44af8735f0435599a) bilkul
# local chain ki tarah fire hota hai; ver stage ka guard input ke
# NAAM ('built-v457.html') + us ki MD5 par fire hota hai.
# Chalana: repo root se  python3 patch_v457.py
# Target: android/app/src/main/assets/www/index.html (workflow ki
# "Sync web assets" + v389..v456 steps ke BAAD ki haalat par).
# Is version me manifest ki KOI tabdeeli nahi hai, Java ki bhi nahi.

import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HP = ROOT / 'android/app/src/main/assets/www/index.html'

EXPECTED_FINAL_MD5 = '8bb73eccfa2115eb57a9339c234a4641'

STAGE_JS = '#!/usr/bin/env python3\n# MEER v4.57 JS patch — REAL VIDEO null-crash fix — LOCAL ONLY (sim-meer2).\n# GitHub upload / APK build is patch ka kaam NAHI hai.\n#\n# BASE: built-v456-final.html (MD5 d8c087955b3960a44af8735f0435599a)\n# — v4.56 final (gate-verified). Base file kabhi modify NAHI hoti —\n# copy par kaam karke built-v457.html likhi jati hai.\n#\n# BUG (Hamza ki screenshot, 2026-10-25 ~10:36 PKT — v4.56, phone):\n#   "❌ Cannot read properties of null (reading \'length\')"\n#   REAL VIDEO BANAO dabate hi. Root cause (verify kiya):\n#   - `let ONLINE_CARS=null;` (line 369) — shuru me null.\n#   - loadOnlineCars() 2s baad cars.json fetch karta hai; Hamza ka\n#     network kamzoor tha to fetch fail/pending raha -> ONLINE_CARS\n#     null hi raha.\n#   - realMakeVideoNative me line 3987:\n#       const onlineCars = (typeof ONLINE_CARS !== \'undefined\'\n#                           && ONLINE_CARS.length >= 3) ? ONLINE_CARS : [];\n#     typeof null === \'object\' hota hai (\'undefined\' NAHI) — guard\n#     guzar jata hai, phir null.length crash. Outer catch banner\n#     dikhata hai (\'❌ Cannot read...\').\n#   - File me ye aik hi `typeof X !== \'undefined\' && X.length`\n#     pattern hai (grep se verify) — crash ki aik hi jagah.\n#\n# FIX: null-guard — wahi pattern jo randomOnlineCar() me pehle se\n# hai (line 408: `ONLINE_CARS&&ONLINE_CARS.length>0`). Null ho to\n# built-in car (\'car-red.png\') istemal hoti hai — video banti hai,\n# crash nahi. Koi aur behaviour nahi badalta; voice engine,\n# watermark, vault/queue flow untouched.\n#\n# Har anchor assert hota hai; aakhir me strip-back proof: tabdeeli\n# ulta karne par base byte-identical wapas milti hai.\n\nimport hashlib\nimport sys\nfrom pathlib import Path\n\nHERE = Path(__file__).resolve().parent\nSRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / \'built-v456-final.html\'\nDST = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / \'built-v457.html\'\nassert SRC.resolve() != DST.resolve(), \'SRC aur DST aik nahi ho sakte — patch ROK diya\'\nif SRC.name == \'built-v456-final.html\':\n    md5 = hashlib.md5(SRC.read_bytes()).hexdigest()\n    assert md5 == \'d8c087955b3960a44af8735f0435599a\', f\'base MD5 galat: {md5} — patch ROK diya\'\n\nhtml = SRC.read_text(encoding=\'utf-8\')\norig = html\napplied = []\nundo = []  # (new, old, count) — strip-back proof ke liye\n\n\ndef rep(old, new, label, count=1):\n    global html\n    n = html.count(old)\n    assert n == count, f\'anchor [{label}] {n} dafa mila ({count} chahiye tha) — patch ROK diya\'\n    html = html.replace(old, new)\n    applied.append(label)\n    undo.append((new, old, count))\n\n\n# =====================================================================\n# F1) ONLINE_CARS null-guard — realMakeVideoNative, car picking\n# =====================================================================\nrep(\n    "      const onlineCars = (typeof ONLINE_CARS !== \'undefined\' && ONLINE_CARS.length >= 3) ? ONLINE_CARS : [];",\n    "      const onlineCars = (ONLINE_CARS && ONLINE_CARS.length >= 3) ? ONLINE_CARS : []; // v4.57: null-guard — cars.json na load ho (kamzoor network) to null.length crash NAHI; built-in car use hogi",\n    \'F1 ONLINE_CARS null-guard\',\n)\n\n\n# ---------- Aakhri asserts ----------\nassert html.count(\'ONLINE_CARS && ONLINE_CARS.length >= 3\') == 1, \'fix line aik dafa honi chahiye\'\nassert html.count("typeof ONLINE_CARS !== \'undefined\' && ONLINE_CARS.length") == 0, \'purana crash pattern khatam hona chahiye\'\nassert html.count(\'let ONLINE_CARS=null;\') == 1, \'ONLINE_CARS init waisa hi\'\nassert html.count(\'if(ONLINE_CARS&&ONLINE_CARS.length>0)\') == 1, \'randomOnlineCar guard waisa hi\'\nassert html.count(\'meerQueueSubmit\') == 2, \'v4.56 auto-submit flow chhua gaya — patch ROK diya\'\nassert html.count(\'suspQueueBtn\') == 2, \'v4.56 queue button chhua gaya — patch ROK diya\'\nassert html.count(\'const APP_VER="4.56";\') == 1, \'version abhi 4.56 hi (ver patch alag se)\'\n# Strip-back proof: tabdeeli ulta karne par base wapas\nchk = html\nfor new, old, cnt in reversed(undo):\n    assert chk.count(new) == cnt, f\'strip-back: naya hissa {cnt} dafa hona chahiye tha: {new[:60]}\'\n    chk = chk.replace(new, old)\nassert chk == orig, \'strip-back FAIL — tabdeeli ke ilawa bhi kuch badla\'\n\nDST.write_text(html, encoding=\'utf-8\')\nprint(\'applied:\', \', \'.join(applied))\nprint(\'WROTE\', DST, f\'({len(html)} chars; base se {len(html) - len(orig):+d})\')\nprint(\'MD5:\', hashlib.md5(DST.read_bytes()).hexdigest())\n'

STAGE_VER = '#!/usr/bin/env python3\n# MEER v4.57 VERSION patch — sirf version pehchan 4.56 -> 4.57 — LOCAL ONLY\n# (sim-meer2). GitHub upload / APK build is patch ka kaam NAHI hai.\n#\n# BASE: built-v457.html (MD5 e479ecf67b7b74a9846ec00c1ecd8ba6) —\n# v4.57 JS stage ki output (ONLINE_CARS null-guard fix).\n# Base file kabhi modify NAHI hoti — copy par kaam karke\n# built-v457-final.html likhi jati hai.\n#\n# Sirf teen user-visible/functional version strings badalte hain,\n# bilkul v4.51/v4.52/v4.53/v4.54/v4.55/v4.56 wale tareeqe se (full\n# anchors, exactly-once assert). Code comments me maujood "v4.56"\n# wale alfaaz NAHI chhoote (wo pichle rounds ke record hain) — is\n# liye koi global count assert nahi, sirf anchors.\n\nimport hashlib\nimport sys\nfrom pathlib import Path\n\nHERE = Path(__file__).resolve().parent\nSRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / \'built-v457.html\'\nDST = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / \'built-v457-final.html\'\nassert SRC.resolve() != DST.resolve(), \'SRC aur DST aik nahi ho sakte — patch ROK diya\'\nif SRC.name == \'built-v457.html\':\n    md5 = hashlib.md5(SRC.read_bytes()).hexdigest()\n    assert md5 == \'e479ecf67b7b74a9846ec00c1ecd8ba6\', f\'base MD5 galat: {md5} — patch ROK diya\'\n\nhtml = SRC.read_text(encoding=\'utf-8\')\norig = html\napplied = []\n\n\ndef rep(old, new, label):\n    global html\n    n = html.count(old)\n    assert n == 1, f\'anchor [{label}] {n} dafa mila (1 chahiye tha) — patch ROK diya\'\n    html = html.replace(old, new)\n    applied.append(label)\n\n\n# ---------- Version strings: 4.56 -> 4.57 ----------\nrep(\'const APP_VER="4.56";\',\n    \'const APP_VER="4.57";\',\n    \'V1 APP_VER\')\n\nrep(\'>v4.56 MEER • 100% Free • No watermark<\',\n    \'>v4.57 MEER • 100% Free • No watermark<\',\n    \'V2 footer\')\n\nrep(\'id="verLabel" style="opacity:.6;font-size:12px">v4.56<\',\n    \'id="verLabel" style="opacity:.6;font-size:12px">v4.57<\',\n    \'V3 verLabel static\')\n\n# ---------- Aakhri asserts ----------\nassert html.count(\'const APP_VER="4.57";\') == 1\nassert html.count(\'const APP_VER="4.56"\') == 0\nassert html.count(\'v4.57 MEER\') == 1 and html.count(\'v4.56 MEER\') == 0\nassert html.count(\'id="verLabel" style="opacity:.6;font-size:12px">v4.57<\') == 1\nassert html.count(\'ONLINE_CARS && ONLINE_CARS.length >= 3\') == 1, \'v4.57 null-guard maujood hona chahiye\'\nassert html.count("typeof ONLINE_CARS !== \'undefined\' && ONLINE_CARS.length") == 0, \'purana crash pattern wapas nahi ana chahiye\'\nassert len(html) == len(orig), \'lambai badli — sirf 4.56->4.57 (barabar size) hona chahiye tha\'\n\nDST.write_text(html, encoding=\'utf-8\')\nprint(\'applied:\', \', \'.join(applied))\nprint(\'WROTE\', DST, f\'({len(html)} chars)\')\nprint(\'MD5:\', hashlib.md5(DST.read_bytes()).hexdigest())\n'

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
        base = td / 'built-v456-final.html'
        base.write_bytes(HP.read_bytes())
        run_stage(STAGE_JS, 'stage_js.py', [base, td / 'built-v457.html'], td)
        run_stage(STAGE_VER, 'stage_ver.py',
                  [td / 'built-v457.html', td / 'built-v457-final.html'], td)
        final = td / 'built-v457-final.html'
        md5 = hashlib.md5(final.read_bytes()).hexdigest()
        assert md5 == EXPECTED_FINAL_MD5, f'final MD5 galat: {md5} -- patch ROK diya'
        HP.write_bytes(final.read_bytes())
        print('v4.57 patch OK -- final MD5:', md5)


if __name__ == '__main__':
    main()
