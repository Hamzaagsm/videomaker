# v4.11: Remove car picker UI, auto-select cars
# Hamza: "Oper jo garyan nazar aa rhi haen wo khtam kro select wala option gariyan khud se bany"
# Hide the car picker thumbnails, auto-select cars

def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    import re

    # 1. Hide carPickerBox via CSS - add style to hide it
    old_style = "</style>"
    new_style = "#carPickerBox{display:none!important;}</style>"
    if old_style in h and "#carPickerBox{display:none" not in h:
        h = h.replace(old_style, new_style, 1)
        print('HIDE PICKER CSS OK')

    # 2. Make renderCarPicker a no-op (don't render thumbnails)
    old_render = """function renderCarPicker(){
  try{
    let box=document.getElementById('carPickerBox');
    if(!box||!ONLINE_CARS)return;
    box.innerHTML='';"""
    new_render = """function renderCarPicker(){
  try{
    let box=document.getElementById('carPickerBox');
    if(box)box.style.display='none';
    return; // v4.11: Car picker hidden - auto select only!
    if(!box||!ONLINE_CARS)return;
    box.innerHTML='';"""
    if old_render in h:
        h = h.replace(old_render, new_render, 1)
        print('RENDER PICKER DISABLE OK')

    # Version 4.11
    h = re.sub(r"const APP_VER='4\.10'", "const APP_VER='4.11'", h)
    h = h.replace("v4.10", "v4.11")
    print('HTML version OK')

    if h != orig:
        open(p, 'w', encoding='utf-8').write(h)
    print('HTML V4.11 DONE')

patch_html()
print('V4.11 ALL DONE')
