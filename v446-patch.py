#!/usr/bin/env python3
# MEER v4.46 - NEW ADVENTURE LAMBI VIDEO FIX
# Saboot (Hamza ki video, 2026-10-21): "3 minutes ki thi, choti si bani" - video 25.9s, 5-6 segments.
# Wajah: advBuildLines() har slot se SIRF EK line chunta hai - 6 slots = hamesha 6 lines (~30s),
# duration select ka is par koi asar hi nahi. Online pool me 34 lines / ~22 scenes maujood hain.
# Fix: chunk ke aakhir me advBuildLines ki nayi tareef - duration ke hisaab se slot-rounds me
# lines jorti hai; pehle har scene sirf ek dafa, phir bhi chhoti ho to nayi lines (koi line
# dobara NAHI). Wrapper wala manifest-refresh + advOk filter nayi tareef ke andar bhi hai.
import re

HP = 'android/app/src/main/assets/www/index.html'
html = open(HP, encoding='utf-8').read()

html, n1 = re.subn(r"APP_VER\s*=\s*[\"'][\d.]+[\"']", 'APP_VER="4.46"', html)
html, n2 = re.subn(r"v4\.\d+ MEER", "v4.46 MEER", html)
print('V446 APP_VER bump:', n1, n2)

NEW_BLOCK = r"""
/* ===== MEER v4.46: NEW ADVENTURE duration-true builder =====
   advBuildLines ab select ki hui duration ke hisaab se lines jorta hai:
   slot-rounds me, pehle har scene sirf EK dafa; phir bhi chhoti ho to nayi
   lines (koi line kabhi dobara nahi). Purani 6-line wali hard limit khatam. */
advBuildLines=function(){
  try{ var ms=manifestSlots(); if(ms){ ADV_SLOTS=ms; } }catch(e){}
  var slots=ADV_SLOTS.map(function(s){ var f=s.filter(function(o){ return advOk(o.clip); }); return f.length?f:s; });
  var target=165; try{ var dm=parseInt(document.getElementById('realDur').value)||3; target=dm*60*0.92; }catch(e){}
  function advEst(t){ var w=((t||'').trim().split(/\s+/).filter(Boolean).length)||1; return Math.max(2.5, w*0.36+0.6); }
  var maxV=0; for(var i=0;i<slots.length;i++) maxV=Math.max(maxV, slots[i].length);
  var out=[], sec=0, usedClip={}, usedLine={};
  for(var v=0; v<maxV && sec<target; v++){
    for(var s2=0; s2<slots.length && sec<target; s2++){
      var e=slots[s2][v]; if(!e||!e.clip) continue;
      if(usedClip[e.clip]) continue;
      usedClip[e.clip]=1; usedLine[e.clip+'|'+e.text]=1;
      out.push({ch:e.ch, clip:e.clip, text:e.text}); sec+=advEst(e.text);
    }
  }
  if(sec<target){
    for(var v2=0; v2<maxV && sec<target; v2++){
      for(var s3=0; s3<slots.length && sec<target; s3++){
        var e2=slots[s3][v2]; if(!e2||!e2.clip) continue;
        if(usedLine[e2.clip+'|'+e2.text]) continue;
        usedLine[e2.clip+'|'+e2.text]=1;
        out.push({ch:e2.ch, clip:e2.clip, text:e2.text}); sec+=advEst(e2.text);
      }
    }
  }
  if(!out.length){ for(var i2=0;i2<slots.length;i2++){ if(slots[i2].length) out.push(slots[i2][0]); } }
  return out;
};

/* ===== MEER v4.46: Real Family Studio HATA diya (Hamza ki hidayat 2026-10-21) =====
   Paanchon modes (Story/Kids/Interview/Drama/Family) 1-2 fixed clips hi ghumate thay -
   kaam ke nahi thay. Sirf is studio ka home button + screen chhupaya gaya hai;
   baqi poori app ko haath nahi lagaya. */
function meerHideRealFam(){
  try{
    var scr=document.getElementById('s-realfam'); if(scr) scr.style.display='none';
    var btns=document.querySelectorAll('button');
    for(var i=0;i<btns.length;i++){ if(btns[i].textContent.indexOf('Real Family Studio')>=0) btns[i].style.display='none'; }
  }catch(e){}
}
meerHideRealFam();
try{ document.addEventListener('DOMContentLoaded', meerHideRealFam); }catch(e){}
var _hrfT=0; var _hrfIv=setInterval(function(){ meerHideRealFam(); _hrfT++; if(_hrfT>12) clearInterval(_hrfIv); }, 800);
"""

anchor = "\n(function(){\n  function rebind()"
if anchor in html:
    html = html.replace(anchor, NEW_BLOCK + anchor, 1)
    print('V446 adventure builder override: True')
else:
    print('V446 adventure builder override: False  <-- ANCHOR MISSING')

open(HP, 'w', encoding='utf-8').write(html)
print('V446 done')
