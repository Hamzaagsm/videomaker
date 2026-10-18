# v4.24: Classic engine
def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    import re
    code = '''<canvas id="v424canvas" width="720" height="1280" style="display:none;"></canvas><script>var v424_cx=null,v423_AICHAR={};function v424_init(){var cv=document.getElementById("v424canvas");if(cv)v424_cx=cv.getContext("2d");}function v424_drawCar(x,y,w,ch,talking,t){var cx=v424_cx;if(!cx)return;var im=v423_AICHAR[(ch||"").toLowerCase()];if(!im||!im.complete||!im.naturalWidth)return;var h=w*(im.naturalHeight/im.naturalWidth);cx.save();cx.translate(x+Math.sin(t*1.2)*w*0.06,y-Math.abs(Math.sin(t*6))*h*0.02);cx.drawImage(im,-w/2,-h/2,w,h);if(talking){cx.fillStyle="#5c1a1a";cx.beginPath();cx.ellipse(0,h*0.22,w*0.14,w*0.05,0,0,7);cx.fill();}cx.restore();}if(document.readyState==="loading"){document.addEventListener("DOMContentLoaded",v424_init);}else{v424_init();}</script>'''
    if 'v424_drawCar' not in h:
        h = h.replace('</body>', code + '</body>', 1)
        print('V424 OK')
    h = re.sub(r"const APP_VER\s*=\s*['\"]4\.\d+['\"]", "const APP_VER='4.24'", h)
    if h != orig:
        open(p, 'w', encoding='utf-8').write(h)
    print('HTML V4.24 DONE')
def patch_java():
    print('JAVA V4.24 DONE')
patch_html()
patch_java()
print('V4.24 ALL DONE')
