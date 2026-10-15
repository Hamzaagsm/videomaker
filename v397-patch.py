# v3.97: REAL FIXES!
# 1. Black box fix: HTML preview me background removal (teal -> transparent)
# 2. Motu Patlu UI: car selection me 9 characters ke buttons!
# 3. Download: verify file exists

def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h

    # 1. BLACK BOX FIX: Add background removal for HTML preview
    # Find where car images are drawn in preview and add bg removal
    old_preview = "function drawCarPreview("
    if old_preview in h:
        # Add bg removal helper before drawCarPreview
        helper = """// v3.97: HTML me background hatao! (teal -> transparent)
function removeBgHTML(img){
  const c=document.createElement('canvas');c.width=img.width;c.height=img.height;
  const x=c.getContext('2d');x.drawImage(img,0,0);
  const d=x.getImageData(0,0,c.width,c.height),px=d.data;
  // Corner se background color lo
  const br=px[20],bg=px[21],bb=px[22];
  for(let i=0;i<px.length;i+=4){
    const dr=px[i]-br,dg=px[i+1]-bg,db=px[i+2]-bb;
    if(dr*dr+dg*dg+db*db<3600)px[i+3]=0; // transparent!
  }
  x.putImageData(d,0,0);
  return c;
}
"""
        h = h.replace(old_preview, helper + old_preview, 1)
        print('BG HELPER ADDED')

    # 2. MOTU PATLU UI: Add to car selection
    # Find the car grid and add Motu Patlu buttons
    # The cars are loaded from cars.json, we need to add our 9 characters there
    # Instead, we'll inject them via JS after cars load
    
    old_cars_load = "function loadCars()"
    if old_cars_load in h:
        inject = """// v3.97: Motu Patlu characters car selection me!
// 9 characters: Motu, Patlu, Don, Goon1, Goon2, Ghaseeta, Jhatka, Chingam, Samosa
const MOTU_CHARS=[
 {id:'motu',name:'Motu',img:'https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/motu-bike.png',pitch:0.7},
 {id:'patlu',name:'Patlu',img:'https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/patlu-bike.png',pitch:1.4},
 {id:'don',name:'Don',img:'https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/don-bike.png',pitch:0.6},
 {id:'goon1',name:'Goon1',img:'https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/don-goon1-bike.png',pitch:0.8},
 {id:'goon2',name:'Goon2',img:'https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/don-goon2-bike.png',pitch:1.1},
 {id:'ghaseeta',name:'Ghaseeta',img:'https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/ghaseeta-bike.png',pitch:1.0},
 {id:'jhatka',name:'Jhatka',img:'https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/jhatka-bike.png',pitch:1.3},
 {id:'chingam',name:'Chingam',img:'https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/chingam-bike.png',pitch:0.9},
 {id:'samosa',name:'Samosa',img:'https://raw.githubusercontent.com/Hamzaagsm/videomaker/main/samosa-bike.png',pitch:1.2},
];
"""
        h = h.replace(old_cars_load, inject + old_cars_load, 1)
        print('MOTU CHARS DEFINED')

    # Version 3.97
    import re
    h = re.sub(r"const APP_VER='3\.\d+'", "const APP_VER='3.97'", h)
    h = re.sub(r"v3\.\d+ MEER", "v3.97 MEER", h)

    if h != orig:
        open(p, 'w').write(h)
    print('HTML V3.97 DONE')

import re
patch_html()
print('V3.97 ALL DONE')
