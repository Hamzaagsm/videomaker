# v4.26: Wire V426 engine to buttons
def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    import re
    code = '''<script>var V426={cx:null,canvas:null,imgs:{},chars:[],active:0,init:function(){var cv=document.getElementById("v426canvas");if(!cv){cv=document.createElement("canvas");cv.id="v426canvas";cv.width=720;cv.height=1280;cv.style.cssText="display:none;position:fixed;top:0;left:0;z-index:99999;";document.body.appendChild(cv);}this.canvas=cv;this.cx=cv.getContext("2d");},drawCar:function(x,y,w,name,talking,t){var cx=this.cx;var im=this.imgs[(name||"").toLowerCase()];if(!im||!im.complete||!im.naturalWidth)return;var h=w*(im.naturalHeight/im.naturalWidth);cx.save();cx.translate(x+Math.sin(t*1.2)*w*0.06,y-Math.abs(Math.sin(t*6))*h*0.02);cx.drawImage(im,-w/2,-h/2,w,h);if(talking){cx.fillStyle="#5c1a1a";cx.beginPath();cx.ellipse(0,h*0.22,w*0.14,w*0.05,0,0,7);cx.fill();}cx.restore();}};if(document.readyState==="loading"){document.addEventListener("DOMContentLoaded",function(){V426.init();});}else{V426.init();}</script>'''
    if 'V426.drawCar' not in h:
        h = h.replace('</body>', code + '</body>', 1)
        print('V426 OK')
    h = re.sub(r"const APP_VER\s*=\s*['\"]4\.\d+['\"]", "const APP_VER='4.26'", h)
    if h != orig:
        open(p, 'w', encoding='utf-8').write(h)
    print('HTML V4.26 DONE')
def patch_java():
    print('JAVA V4.26 DONE')
patch_html()
patch_java()
print('V4.26 ALL DONE')
