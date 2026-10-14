# v3.88 patch: Screenshot style! (bari gari samne se, 3D street, no flat road)
# Works on POST-v386 state (v386 patch already ran)
def patch_java():
    p = 'android/app/src/main/java/com/hamza/videomaker/MainActivity.java'
    s = open(p).read()

    # 1. BARI gari! 420 -> 700 (screenshot jaisi - frame bhar!)
    if 'int cw = 420;' in s:
        s = s.replace('int cw = 420;', 'int cw = 700; // v3.88: BARI gari (screenshot style!)', 1)
        print('CAR SIZE 700 OK')
    elif 'int cw = 600;' in s:
        s = s.replace('int cw = 600;', 'int cw = 700; // v3.88: BARI gari (screenshot style!)', 1)
        print('CAR SIZE 600->700 OK')
    elif 'int cw = 700;' in s:
        print('CAR SIZE ALREADY 700')

    # 2. DOOSRI gari HATAO! (single car only!)
    old_car2 = '''                            // v3.86: DOOSRI gari - sath me chalegi!
                            if (carScaled2 != null) {
                                float car2X = carX - 220; // Peeche!
                                float car2Y = carY + 60; // Thodi neeche!
                                canvas.drawBitmap(carScaled2, car2X, car2Y, paint);
                                // Doosri gari ke wheels (chhote!)
                                float wheelR2 = 30;
                                float w1x2 = car2X + carScaled2.getWidth() * 0.30f;
                                float w2x2 = car2X + carScaled2.getWidth() * 0.74f;
                                float wy2 = car2Y + carScaled2.getHeight() * 0.83f;
                                drawWheel(canvas, w1x2, wy2, wheelR2, wheelAngle, wheelPaint, spokePaint);
                                drawWheel(canvas, w2x2, wy2, wheelR2, wheelAngle, wheelPaint, spokePaint);
                            }'''
    if old_car2 in s:
        s = s.replace(old_car2, '                            // v3.88: Single car only! (doosri gari hata di)', 1)
        print('CAR2 REMOVED OK')
    else:
        print('CAR2 NOT FOUND (maybe already removed)')

    # 3. UGLY drawn wheels HATAO! (main car ke)
    old_wheels = '''                            float wheelR = 36;
                            float w1x = carX + carScaled.getWidth() * 0.30f;
                            float w2x = carX + carScaled.getWidth() * 0.74f;
                            float wy = carY + carScaled.getHeight() * 0.83f;
                            float wheelAngle = frameNum * 14; // Road speed se match!
                            drawWheel(canvas, w1x, wy, wheelR, wheelAngle, wheelPaint, spokePaint);
                            drawWheel(canvas, w2x, wy, wheelR, wheelAngle, wheelPaint, spokePaint);'''
    if old_wheels in s:
        s = s.replace(old_wheels,
            '                            // v3.88: Koi drawn wheels nahi! (car ke apne wheels!)', 1)
        print('WHEELS REMOVED OK')
    else:
        print('WHEELS NOT FOUND')

    # 4. v3.88: Gari CENTER me! (left-right drive nahi, screenshot style!)
    # carX ko centered karo (cw variable hai, carW nahi!)
    if 'float carX = -carW + progress * (W + carW * 2);' in s:
        s = s.replace('float carX = -carW + progress * (W + carW * 2);',
                      'float carX = (W - cw) / 2; // v3.88: CENTER! (screenshot style)', 1)
        print('CARX CENTERED OK')
    elif 'float carX = -450 + progress * (W + 900);' in s:
        s = s.replace('float carX = -450 + progress * (W + 900);',
                      'float carX = (W - cw) / 2; // v3.88: CENTER! (screenshot style)', 1)
        print('CARX CENTERED OK (alt)')
    # Agar pehle se (W - carW) hai to theek karo
    if 'float carX = (W - carW) / 2;' in s:
        s = s.replace('float carX = (W - carW) / 2;',
                      'float carX = (W - cw) / 2; // v3.88: CENTER! (screenshot style)', 1)
        print('CARX FIXED (carW->cw)')

    # carY ko screenshot style (center, thodi neeche) + halki bob
    if 'float carY = roadTop - carScaled.getHeight() * 0.82f + bounce;' in s:
        s = s.replace('float carY = roadTop - carScaled.getHeight() * 0.82f + bounce;',
                      'float carY = H * 0.30f + (float)(Math.sin(frameNum * 0.08) * 12); // v3.88: Center + halki bob!', 1)
        print('CARY FIXED OK')

    # 5. v3.88: Flat ROAD mat draw karo! (3D street ka apna road hai!)
    # Road wale rect ko skip karo
    old_road = '                        canvas.drawRect(0, roadTop, W, H, paint);'
    if old_road in s:
        s = s.replace(old_road,
                      '                        // v3.88: Flat road nahi! (3D background ka apna road!)', 1)
        print('FLAT ROAD REMOVED OK')

    # 6. v3.88: wheelAngle ka leftover hatao! (wheels remove ho gaye, lekin reference reh gaya!)
    # 'float w2a = wheelAngle;' ya similar lines dhoondo aur hatao
    import re
    # wheelAngle ke akelay references hatao (jo drawWheel me nahi hain)
    lines = s.split('\n')
    new_lines = []
    for line in lines:
        # Agar line me wheelAngle hai lekin drawWheel nahi, aur ye definition nahi hai
        if 'wheelAngle' in line and 'drawWheel' not in line and 'float wheelAngle' not in line:
            # Comment out karo
            stripped = line.lstrip()
            indent = line[:len(line)-len(stripped)]
            new_lines.append(indent + '// v3.88 removed: ' + stripped)
            print('WHEELANGLE REF REMOVED: ' + stripped[:60])
        else:
            new_lines.append(line)
    s = '\n'.join(new_lines)

    open(p, 'w').write(s)
    print('JAVA V3.88 PATCHED OK')

def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()

    # v3.88: carImage2 hatao (single car!)
    if 'carImage2:carImg2' in h:
        h = h.replace('carImage:carImg,carImage2:carImg2,bgImage:bgImg', 'carImage:carImg,bgImage:bgImg')
        print('CARIMAGE2 REMOVED')

    # v3.88: Silent tail khatam! (4-5 sec khamoshi fix)
    # Har segment me +0.3s jama ho kar 4-5s ban jata tha!
    if 'const dur=Math.max(1.0,audioDurSec+0.3);' in h:
        h = h.replace('const dur=Math.max(1.0,audioDurSec+0.3);',
                      'const dur=Math.max(0.8,audioDurSec+0.1); // v3.88: silent tail khatam! (+0.3 -> +0.1)', 1)
        print('SILENT TAIL FIXED')

    # Version 3.88
    h = h.replace("const APP_VER='3.86'", "const APP_VER='3.88'")
    h = h.replace("const APP_VER='3.87'", "const APP_VER='3.88'")
    h = h.replace("v3.86 MEER", "v3.88 MEER")
    h = h.replace("v3.87 MEER", "v3.88 MEER")

    open(p, 'w').write(h)
    print('HTML V3.88 PATCHED OK')

patch_java()
patch_html()
print('V3.88 DONE')
