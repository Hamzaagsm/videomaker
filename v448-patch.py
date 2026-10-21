#!/usr/bin/env python3
# MEER v4.48 - DOWNLOAD FLOOD FIX (sirf zaroori scenes download honge)
# Saboot (Hamza ke screenshots, 2026-10-21 11:48): Suspense video banane gaya to
# Download Manager me "38 files downloading" - Bilal/Fahad waghera ke scenes bhi
# utar rahe thay; app ghante bhar "Scenes download ho rahe hain... 6 baqi" par
# atki rahi, net theek honay ke bawajood.
# Wajah code me dekhi: suspLoad() / journeyLoad() / loadManifest() teeno apne
# manifest ke ATE hi POORI library ke saare clips pehle se download karne lag
# jate thay (prefetch) - 15 kahaniyan x 6 = ~90 clips ki line lag jati, aur
# suspEnsureClips ka intezar sirf 60 second ka tha, is liye asal 6 scenes line
# me phanse rehte thay.
# Fix:
#  1) Teeno prefetch loops band - ab koi scene pehle se nahi utrega; sirf wohi
#     scenes download honge jo usi video ke liye chahiye hon (ensure functions
#     pehle se aisa hi karte hain, unhe haath nahi lagaya).
#  2) suspEnsureClips ka intezar 60s -> 900s (15 min) aur journey ka 150s -> 900s;
#     status har 1.5s par "X baqi" batata rahega - app beech me haar nahi manegi.
import re

HP = 'android/app/src/main/assets/www/index.html'
html = open(HP, encoding='utf-8').read()

html, n1 = re.subn(r"APP_VER\s*=\s*[\"'][\d.]+[\"']", 'APP_VER="4.48"', html)
html, n2 = re.subn(r"v4\.\d+ MEER", "v4.48 MEER", html)
print('V448 APP_VER bump:', n1, n2)

FIXES = [
 ('adv_prefetch',
  "(function(n){ try{ if(!advOk(n)&&typeof RealClipBridge!=='undefined'&&RealClipBridge.downloadOneClip) RealClipBridge.downloadOneClip(n); }catch(e){} })(j[i].clip);",
  "(function(n){ /* MEER v4.48: prefetch band - sirf zaroori scenes download honge */ })(j[i].clip);"),
 ('susp_prefetch',
  "(function(n){ try{ if(!advOk(n)&&typeof RealClipBridge!=='undefined'&&RealClipBridge.downloadSuspClip)RealClipBridge.downloadSuspClip(n); }catch(e){} })(bs[k].clip);",
  "(function(n){ /* MEER v4.48: prefetch band - sirf zaroori scenes download honge */ })(bs[k].clip);"),
 ('journey_prefetch',
  "(function(n){ try{ if(!advOk(n)&&typeof RealClipBridge!=='undefined'&&RealClipBridge.downloadOneClip)RealClipBridge.downloadOneClip(n); }catch(e){} })(ls[k].clip);",
  "(function(n){ /* MEER v4.48: prefetch band - sirf zaroori scenes download honge */ })(ls[k].clip);"),
 ('susp_wait',
  "while(waited<60000)",
  "while(waited<900000) /* MEER v4.48: 15 min tak intezar - beech me haar nahi */"),
 ('journey_wait',
  "while(waited<150000)",
  "while(waited<900000) /* MEER v4.48: 15 min tak intezar */"),
]
for name, old, new in FIXES:
    c = html.count(old)
    if c == 1:
        html = html.replace(old, new, 1)
    print('V448', name, ':', c)

open(HP, 'w', encoding='utf-8').write(html)
print('V448 done')
