# v4.23: Classic engine
def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    import re
    code = '<canvas id="v423canvas" width="720" height="1280" style="display:none;"></canvas><script>var v423_cx=null,v423_AICHAR={};function v423_initCanvas(){var cv=document.getElementById("v423canvas");if(!cv)return false;v423_cx=cv.getContext("2d");return true;}function v423_drawAIChar(x,y,w,ch,talking,t){var cx=v423_cx;if(!cx)return;var im=v423_AICHAR[(ch||"").toLowerCase()];if(!im||!im.complete||!im.naturalWidth)return;var h=w*(im.naturalHeight/im.naturalWidth);var dx=Math.sin(t*1.2)*w*0.06,dy=Math.abs(Math.sin(t*6))*h*0.02;cx.save();cx.translate(x+dx,y-dy);cx.rotate(Math.sin(t*1.2+0.5)*0.03);cx.fillStyle="rgba(0,0,0,.3)";cx.beginPath();cx.ellipse(0,h*0.42,w*0.38,h*0.05,0,0,7);cx.fill();cx.drawImage(im,-w/2,-h/2,w,h);if(talking){var mo=Math.abs(Math.sin(t*10)),mw=w*0.28,mh=w*0.05+mo*w*0.10;cx.fillStyle="#5c1a1a";cx.beginPath();cx.ellipse(0,h*0.22,mw/2,mh/2,0,0,7);cx.fill();}cx.restore();}if(document.readyState==="loading"){document.addEventListener("DOMContentLoaded",v423_initCanvas);}else{v423_initCanvas();}</script>'
    if 'v423_drawAIChar' not in h:
        h = h.replace('</body>', code + '</body>', 1)
        print('V423 OK')
    h = re.sub(r"const APP_VER\s*=\s*['\"]4\.\d+['\"]", "const APP_VER='4.23'", h)
    if h != orig:
        open(p, 'w', encoding='utf-8').write(h)
    print('HTML V4.23 DONE')
def patch_java():
    print('JAVA V4.23 DONE')
patch_html()
patch_java()
print('V4.23 ALL DONE')
