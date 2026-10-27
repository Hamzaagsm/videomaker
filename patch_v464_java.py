#!/usr/bin/env python3
# MEER v4.64 patch (Java) -- repo-form ship script (CI-safe).
#
# Local chain (tasalli-verified) ka repo roop: local patch_v464_java.py
# (sim-meer2) ko STAGE_B64 (base64) me VERBATIM embedded kiya gaya
# hai — decode karne par stage ka logic, anchors, asserts aur
# strip-back proof bilkul wahi jo local built-v464.java (MD5 649e9aef1ee7d045417e8c7546cda601)
# banane me istemal hue.
#
# KAM (v4.64): composeVideo ka v3.66 override ("JS wali ignore!",
# duration = ASLI audio + 0.3s) -> Math.max floor:
# durationSec = max(JS duration, audio + 0.3). JS hissa
# patch_v464.py me hai (meerMeriSpeakSeg floor 5.0) — dono mil kar
# scene poora 5s chalate hain; Java akela kaam nahi karega.
# Asar: composeVideo ke HAR caller par (vault, mysusp, library
# suspense, Journey) — JS duration ab floor hai; segment pehle se
# kabhi chhota nahi hota.
#
# Chalana: repo root se  python3 patch_v464_java.py
# Target: android/app/src/main/java/com/hamza/videomaker/MainActivity.java
# (workflow ki v4.62 java patch step ke BAAD ki haalat par — us waqt
# MainActivity.java == local built-v462.java, MD5 guard wahi hai).
# Is version me AndroidManifest ki KOI tabdeeli nahi hai.

import base64
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
JP = ROOT / 'android/app/src/main/java/com/hamza/videomaker/MainActivity.java'

EXPECTED_FINAL_MD5 = '649e9aef1ee7d045417e8c7546cda601'

STAGE_B64 = (
"IyEvdXNyL2Jpbi9lbnYgcHl0aG9uMwojIE1FRVIgdjQuNjQgSkFWQSBwYXRjaCDigJQgY29tcG9z"
"ZVZpZGVvIGR1cmF0aW9uIEZMT09SIChMT0NBTCBPTkxZLCBzaW0tbWVlcjIpLgojIEdpdEh1YiB1"
"cGxvYWQgLyBBUEsgYnVpbGQgaXMgcGF0Y2gga2Ega2FhbSBOQUhJIGhhaS4KIwojIEJBU0U6IGJ1"
"aWx0LXY0NjIuamF2YSAoTUQ1IGU3MDJkOGMxNzNlOGUzYmM5NzM3YmE4NDk4MTExNjcwKQojIOKA"
"lCB2NC42MiBKYXZhIGtpIGZpbmFsIGhhYWxhdCAodjQuNjMgbWUgSmF2YSB0YWJkZWVsaSBuYWhp"
"IHRoaSkuCiMgQmFzZSBmaWxlIGthYmhpIG1vZGlmeSBOQUhJIGhvdGkg4oCUIGNvcHkgcGFyIGth"
"YW0ga2Fya2UKIyBidWlsdC12NDY0LmphdmEgbGlraGkgamF0aSBoYWkuCiMKIyBNQVNMQSAoSGFt"
"emEga2UgcGhvbmUga2Egc2Fib290LCAyMDI2LTEwLTI3OyBtYWluIGFnZW50IG5lIGNvZGUgc2UK"
"IyB2ZXJpZnkga2l5YSk6IEJhYnkgVG95IHZpZGVvIChyb3cgNCwgMTggbGluZXMpIDM2LjhzIGJh"
"bmksIH45MHMga2kKIyBiYWpheS4gSlMgZmxvb3IgMi41cyB0aGEgaGksIGxla2luIEFTQUwga2Fh"
"dCB5YWhhbiBob3RpIHRoaToKIyBjb21wb3NlVmlkZW8ga2EgdjMuNjYgb3ZlcnJpZGUg4oCUICJT"
"ZWdtZW50IGR1cmF0aW9uID0gQVNMSSBhdWRpbyArCiMgMC4zcyBnYXAgKEpTIHdhbGkgaWdub3Jl"
"ISkiIOKAlCBKUyBkdXJhdGlvbiBrbyBhdWRpbyBraSBhc2FsIGxhbWJhaQojIHNlIEJBREFMIGRl"
"dGEgdGhhIChhdWRpbyA+IDAuNXMgaG8gdG8pLiBKUyBmbG9vciA1LjAga2FybmUgc2UgYmhpCiMg"
"a3VjaCBuYWhpIGJhZGFsdGEgamFiIHRhayB5ZSBvdmVycmlkZSByYWhlOiBKYXZhIHBoaXIgYmhp"
"IGhhcgojIHNlZ21lbnQga28gfjJzIHBhciBrYWF0IGRldGEuIElzIGxpeWUgSlMgcGF0Y2ggKHBh"
"dGNoX3Y0NjQucHkpCiMgYWtlbGEga2FhbSBOQUhJIGthcmVnYSDigJQgeWUgSmF2YSBwYXRjaCBk"
"b3NyYSBsYXptaSBoaXNzYSBoYWkuCiMKIyBGSVggKGFpayBsaW5lIGtpIHRhYmRlZWxpLCBxaXNt"
"IHdhaGkg4oCUIHNpcmYgZmxvb3Igam9yYSk6CiMgICBkdXJhdGlvblNlYyA9IChhY3R1YWxBdWRp"
"b0R1clVzIC8gMTAwMDAwMC4wKSArIDAuMzsKIyAgIC0+CiMgICBkdXJhdGlvblNlYyA9IE1hdGgu"
"bWF4KGR1cmF0aW9uU2VjLCAoYWN0dWFsQXVkaW9EdXJVcyAvIDEwMDAwMDAuMCkgKyAwLjMpOwoj"
"IEpTIGR1cmF0aW9uIGFiIEZMT09SIGhhaSAodmF1bHQgNS4wcyk6IHNjZW5lIGthYmhpIDVzIHNl"
"IGNoaG90YSBuYWhpCiMgaG90YTsgYXVkaW8gbGFtYmkgaG8gdG8gc2VnbWVudCBhdWRpbyswLjMg"
"dGFrIGJhcmh0YSBoYWkgKGF3YXoga2FiaGkKIyBuYWhpIGthdC10aSDigJQgdjMuNjYga2EgYXNh"
"bCBtYXFzYWQgYmFycWFyYXIpLiBBdWRpbyBraGF0YW0gaG9uZSBrZQojIGJhYWQgc2VnbWVudCBr"
"ZSBhYWtoaXIgdGFrIFBUUyBwZWhsZSBzZSBiYXJodGEgaGFpIChhdWRpbyBjb3B5IHBoYXNlCiMg"
"bWUgYXVkaW9TZWdFbmQgdGFrIGp1bXAgKyBtdXNpYy10YWlsIGZpbGwpIOKAlCBpcyBsaXllIGxh"
"bWJhIHNlZ21lbnQKIyBraGFtb3NoaSBzZSBuYWhpLCBwb29yaSBzY2VuZSBrZSBzYWF0aCBjaGFs"
"dGEgaGFpLgojCiMgQVNBUiAoaW1hYW5kYXJpIHNlIOKAlCBzaXJmIHZhdWx0IG5haGksIHBvb3Jh"
"IGNvbXBvc2VWaWRlbyk6CiMgeWUgb3ZlcnJpZGUgY29tcG9zZVZpZGVvIGtlIEhBUiBjYWxsZXIg"
"cGFyIGxhZ3RhIGhhaSAodmF1bHQsIG15c3VzcCwKIyBsaWJyYXJ5IHN1c3BlbnNlIHZpYSBzcGVh"
"a1NlZywgSm91cm5leSB2aWEgYnVpbGRTZWdzKS4gU2FiIGtlIGxpeWUKIyBKUyBkdXJhdGlvbiBh"
"YiBmbG9vciBiYW4gamF0YSBoYWkg4oCUIHNlZ21lbnQgcGVobGUgc2Uga2FiaGkgY2hob3RhCiMg"
"bmFoaSBob3RhLCB6eWFkYSBzZSB6eWFkYSBKUy1yZXF1ZXN0ZWQgZHVyYXRpb24gdGFrIGxhbWJh"
"IGhvdGEgaGFpLgojIEpvdXJuZXkvbGlicmFyeSBrZSBKUyBmbG9vciAyLjUgaGkgaGFpbiAodW5j"
"aGFuZ2VkKSwgaXMgbGl5ZSB1biBraQojIHZpZGVvIHp5YWRhIHNlIHp5YWRhIH4wLjNzL3NjZW5l"
"IGxhbWJpIGhvdGkgaGFpIChhdWRpbyswLjMgLT4KIyBhdWRpbyswLjYsIDIuNSBmbG9vcikg4oCU"
"IDMwIGxpbmVzIHBhciB+KzlzLCAxLTUgbWluIHVzb29sIGtlIGFuZGFyLgojIFZhdWx0IDE4IGxp"
"bmVzOiB+MzYuOHMgLT4gfjkwcyAoYXNhbCBmaXgpLgojCiMgSGFyIGFuY2hvciBleGFjdGx5LW9u"
"Y2UgYXNzZXJ0IGhvdGEgaGFpOyBhYWtoaXIgbWUgc3RyaXAtYmFjayBwcm9vZi4KCmltcG9ydCBo"
"YXNobGliCmltcG9ydCBzeXMKZnJvbSBwYXRobGliIGltcG9ydCBQYXRoCgpIRVJFID0gUGF0aChf"
"X2ZpbGVfXykucmVzb2x2ZSgpLnBhcmVudApTUkMgPSBQYXRoKHN5cy5hcmd2WzFdKSBpZiBsZW4o"
"c3lzLmFyZ3YpID4gMSBlbHNlIEhFUkUgLyAnYnVpbHQtdjQ2Mi5qYXZhJwpEU1QgPSBQYXRoKHN5"
"cy5hcmd2WzJdKSBpZiBsZW4oc3lzLmFyZ3YpID4gMiBlbHNlIEhFUkUgLyAnYnVpbHQtdjQ2NC5q"
"YXZhJwphc3NlcnQgU1JDLnJlc29sdmUoKSAhPSBEU1QucmVzb2x2ZSgpLCAnU1JDIGF1ciBEU1Qg"
"YWlrIG5haGkgaG8gc2FrdGUg4oCUIHBhdGNoIFJPSyBkaXlhJwppZiBTUkMubmFtZSA9PSAnYnVp"
"bHQtdjQ2Mi5qYXZhJzoKICAgIG1kNSA9IGhhc2hsaWIubWQ1KFNSQy5yZWFkX2J5dGVzKCkpLmhl"
"eGRpZ2VzdCgpCiAgICBhc3NlcnQgbWQ1ID09ICdlNzAyZDhjMTczZThlM2JjOTczN2JhODQ5ODEx"
"MTY3MCcsIGYnYmFzZSBNRDUgZ2FsYXQ6IHttZDV9IOKAlCBwYXRjaCBST0sgZGl5YScKCnNyYyA9"
"IFNSQy5yZWFkX3RleHQoZW5jb2Rpbmc9J3V0Zi04JykKb3JpZyA9IHNyYwphcHBsaWVkID0gW10K"
"dW5kbyA9IFtdCgoKZGVmIHJlcChvbGQsIG5ldywgbGFiZWwpOgogICAgZ2xvYmFsIHNyYwogICAg"
"biA9IHNyYy5jb3VudChvbGQpCiAgICBhc3NlcnQgbiA9PSAxLCBmJ2FuY2hvciBbe2xhYmVsfV0g"
"e259IGRhZmEgbWlsYSAoMSBjaGFoaXllIHRoYSkg4oCUIHBhdGNoIFJPSyBkaXlhJwogICAgc3Jj"
"ID0gc3JjLnJlcGxhY2Uob2xkLCBuZXcsIDEpCiAgICBhcHBsaWVkLmFwcGVuZChsYWJlbCkKICAg"
"IHVuZG8uYXBwZW5kKChuZXcsIG9sZCkpCgoKIyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09"
"PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KIyBGMSkgdjMuNjYgb3Zl"
"cnJpZGUgLT4gTWF0aC5tYXggZmxvb3IgKEpTIGR1cmF0aW9uIEZMT09SLCBhdWRpbyBjYXAgbmFo"
"aSkKIyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09"
"PT09PT09PT09PT09PT09PT0KcmVwKCIiIiAgICAgICAgICAgICAgICAgICAgICAgIC8vIHYzLjY2"
"OiBTZWdtZW50IGR1cmF0aW9uID0gQVNMSSBhdWRpbyArIDAuM3MgZ2FwIChKUyB3YWxpIGlnbm9y"
"ZSEpCiAgICAgICAgICAgICAgICAgICAgICAgIC8vIElzIHNlIHZpZGVvIGhhbWVzaGEgYXVkaW8g"
"a2UgYmFyYWJhciAtIG5hIG11dGUsIG5hIGRlc3luYyEKICAgICAgICAgICAgICAgICAgICAgICAg"
"aWYgKGFjdHVhbEF1ZGlvRHVyVXMgPiA1MDAwMDApIHsgLy8gMC41cyBzZSB6eWFkYSBhdWRpbyBo"
"YWkKICAgICAgICAgICAgICAgICAgICAgICAgICAgIGR1cmF0aW9uU2VjID0gKGFjdHVhbEF1ZGlv"
"RHVyVXMgLyAxMDAwMDAwLjApICsgMC4zOyIiIiwKICAgICIiIiAgICAgICAgICAgICAgICAgICAg"
"ICAgIC8vIHY0LjY0OiBTZWdtZW50IGR1cmF0aW9uID0gSlMgZHVyYXRpb24gRkxPT1IgeWEgQVNM"
"SSBhdWRpbyArIDAuM3Mg4oCUIGpvIGJhcmEgaG8hCiAgICAgICAgICAgICAgICAgICAgICAgIC8v"
"IEpTIHdhbGkgYWIgaWdub3JlIE5BSEkg4oCUIGZsb29yIGhhaTogc2NlbmUgcG9vcmEgY2hhbGVn"
"YSAodmF1bHQgNS4wcyksCiAgICAgICAgICAgICAgICAgICAgICAgIC8vIGF3YXoga2FiaGkgbmFo"
"aSBrYXQtdGkgKG5hIG11dGUsIG5hIGRlc3luYyDigJQgdjMuNjYga2EgbWFxc2FkIGJhcnFhcmFy"
"KS4KICAgICAgICAgICAgICAgICAgICAgICAgaWYgKGFjdHVhbEF1ZGlvRHVyVXMgPiA1MDAwMDAp"
"IHsgLy8gMC41cyBzZSB6eWFkYSBhdWRpbyBoYWkKICAgICAgICAgICAgICAgICAgICAgICAgICAg"
"IGR1cmF0aW9uU2VjID0gTWF0aC5tYXgoZHVyYXRpb25TZWMsIChhY3R1YWxBdWRpb0R1clVzIC8g"
"MTAwMDAwMC4wKSArIDAuMyk7IiIiLAogICAgJ0YxIGR1cmF0aW9uIE1hdGgubWF4IGZsb29yJykK"
"CiMgLS0tLS0tLS0tLSBBYWtocmkgYXNzZXJ0cyAtLS0tLS0tLS0tCmFzc2VydCBzcmMuY291bnQo"
"J2R1cmF0aW9uU2VjID0gTWF0aC5tYXgoZHVyYXRpb25TZWMsIChhY3R1YWxBdWRpb0R1clVzIC8g"
"MTAwMDAwMC4wKSArIDAuMyk7JykgPT0gMSwgJ25heWEgZmxvb3IgbGluZSBhaWsgZGFmYSBob25p"
"IGNoYWhpeWUnCmFzc2VydCBzcmMuY291bnQoJ2R1cmF0aW9uU2VjID0gKGFjdHVhbEF1ZGlvRHVy"
"VXMgLyAxMDAwMDAwLjApICsgMC4zOycpID09IDAsICdwdXJhbmEgb3ZlcnJpZGUgYmFjaGEnCmFz"
"c2VydCBzcmMuY291bnQoJ0pTIHdhbGkgaWdub3JlJykgPT0gMCwgJ3B1cmFuYSAoSlMgd2FsaSBp"
"Z25vcmUpIGNvbW1lbnQgYmFjaGEnCmFzc2VydCBzcmMuY291bnQoJ3Y0LjY0OiBTZWdtZW50IGR1"
"cmF0aW9uJykgPT0gMSwgJ3Y0LjY0IGNvbW1lbnQgYWlrIGRhZmEgaG9uYSBjaGFoaXllJwphc3Nl"
"cnQgc3JjLmNvdW50KCd9IGVsc2UgaWYgKGR1cmF0aW9uU2VjIDwgMS4wIHx8IGR1cmF0aW9uU2Vj"
"ID4gMzAuMCkgeycpID09IDEsICdpbnZhbGlkLWR1cmF0aW9uIGZhbGxiYWNrIHdhaXNhIGhpIHJl"
"aG5hIGNoYWhpeWUnCmFzc2VydCBzcmMuY291bnQoJ3B1YmxpYyBTdHJpbmcgY29tcG9zZVZpZGVv"
"KCcpID09IDEsICdjb21wb3NlVmlkZW8gZGVmIGFpayBkYWZhIGhvbmkgY2hhaGl5ZScKYXNzZXJ0"
"IHNyYy5jb3VudCgncHVibGljIFN0cmluZyByZW5kZXJDYW52YXNWaWRlbygnKSA9PSAxLCAncmVu"
"ZGVyQ2FudmFzVmlkZW8gY2hodWEgZ2F5YSDigJQgcGF0Y2ggUk9LIGRpeWEnCmFzc2VydCBzcmMu"
"Y291bnQoJ3NlZ0R1clNlYyA9IHNlZy5vcHREb3VibGUoImR1cmF0aW9uIiwgMy4wKTsnKSA9PSAx"
"LCAnY2FudmFzIHJlbmRlcmVyIGthIGR1cmF0aW9uIGNoaHVhIGdheWEg4oCUIHBhdGNoIFJPSyBk"
"aXlhJwphc3NlcnQgc3JjLmNvdW50KCdsb25nIHNlZ21lbnREdXJhdGlvblVzID0gKGxvbmcpKGR1"
"cmF0aW9uU2VjICogMTAwMDAwMCk7JykgPT0gMSwgJ3NlZ21lbnREdXJhdGlvblVzIHdhaXNhIGhp"
"IHJlaG5hIGNoYWhpeWUnCmFzc2VydCBzcmMuY291bnQoJ3ByaXZhdGUgU3RyaW5nIG1lZXJIb2xl"
"RmlsbEFwcGx5KCcpID09IDEsICdob2xlLWZpbGwgY2hodWEgZ2F5YSDigJQgcGF0Y2ggUk9LIGRp"
"eWEnCiMgQnJhY2VzL3BhcmVucyBiYWxhbmNlIGJhc2Uga2UgbXV0YWJpcSBzeW1tZXRyaWMgaG9u"
"YSBjaGFoaXllCmFzc2VydCBzcmMuY291bnQoJ3snKSAtIHNyYy5jb3VudCgnfScpID09IG9yaWcu"
"Y291bnQoJ3snKSAtIG9yaWcuY291bnQoJ30nKSwgJ2JyYWNlIGJhbGFuY2UgYmFkbGEnCmFzc2Vy"
"dCBzcmMuY291bnQoJygnKSAtIHNyYy5jb3VudCgnKScpID09IG9yaWcuY291bnQoJygnKSAtIG9y"
"aWcuY291bnQoJyknKSwgJ3BhcmVuIGJhbGFuY2UgYmFkbGEnCiMgU3RyaXAtYmFjayBwcm9vZjog"
"dGFiZGVlbGkgdWx0YSBrYXJuZSBwYXIgYmFzZSB3YXBhcwpjaGsgPSBzcmMKZm9yIG5ldywgb2xk"
"IGluIHJldmVyc2VkKHVuZG8pOgogICAgYXNzZXJ0IGNoay5jb3VudChuZXcpID49IDEsIGYnc3Ry"
"aXAtYmFjazogbmF5YSBoaXNzYSBuYWhpIG1pbGE6IHtuZXdbOjYwXX0nCiAgICBjaGsgPSBjaGsu"
"cmVwbGFjZShuZXcsIG9sZCwgMSkKYXNzZXJ0IGNoayA9PSBvcmlnLCAnc3RyaXAtYmFjayBGQUlM"
"IOKAlCB0YWJkZWVsaSBrZSBpbGF3YSBiaGkga3VjaCBiYWRsYScKCkRTVC53cml0ZV90ZXh0KHNy"
"YywgZW5jb2Rpbmc9J3V0Zi04JykKcHJpbnQoJ2FwcGxpZWQ6JywgJywgJy5qb2luKGFwcGxpZWQp"
"KQpwcmludCgnV1JPVEUnLCBEU1QsIGYnKHtsZW4oc3JjKX0gY2hhcnM7IGJhc2Ugc2Uge2xlbihz"
"cmMpIC0gbGVuKG9yaWcpOitkfSknKQpwcmludCgnTUQ1OicsIGhhc2hsaWIubWQ1KERTVC5yZWFk"
"X2J5dGVzKCkpLmhleGRpZ2VzdCgpKQo=")
STAGE_RM = base64.b64decode(STAGE_B64).decode('utf-8')


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
    assert JP.exists(), f'target nahi mila: {JP}'
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        base = td / 'built-v462.java'
        base.write_bytes(JP.read_bytes())
        run_stage(STAGE_RM, 'stage_v464_java.py', [base, td / 'built-v464.java'], td)
        final = td / 'built-v464.java'
        md5 = hashlib.md5(final.read_bytes()).hexdigest()
        assert md5 == EXPECTED_FINAL_MD5, f'final MD5 galat: {md5} -- patch ROK diya'
        JP.write_bytes(final.read_bytes())
        print('v4.64 java patch OK -- final MD5:', md5)


if __name__ == '__main__':
    main()
