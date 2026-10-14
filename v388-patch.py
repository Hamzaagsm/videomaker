# v3.88 patch: CLEAN single car (purane versions jaisa!)
# Works on POST-v386 state (v386 patch already ran)
def patch_java():
    p = 'android/app/src/main/java/com/hamza/videomaker/MainActivity.java'
    s = open(p).read()

    # 1. BARI gari! 420 -> 600 (purane versions jaisi!)
    if 'int cw = 420;' in s:
        s = s.replace('int cw = 420;', 'int cw = 600; // v3.88: BARI gari!', 1)
        print('CAR SIZE 600 OK')
    elif 'int cw = 600;' in s:
        print('CAR SIZE ALREADY 600')

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

    # 3. UGLY drawn wheels HATAO! (main car ke - car image ke apne wheels!)
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

    open(p, 'w').write(s)
    print('JAVA V3.88 PATCHED OK')

def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()

    # v3.88: carImage2 hatao (single car!)
    if 'carImage2:carImg2' in h:
        h = h.replace('carImage:carImg,carImage2:carImg2,bgImage:bgImg', 'carImage:carImg,bgImage:bgImg')
        print('CARIMAGE2 REMOVED')

    # Version 3.88
    h = h.replace("const APP_VER='3.86'", "const APP_VER='3.88'")
    h = h.replace("const APP_VER='3.87'", "const APP_VER='3.88'")
    h = h.replace("v3.86 MEER", "v3.88 MEER")
    h = h.replace("v3.87 MEER", "v3.88 MEER")

    # 3D street background as default!
    # (bgImage ko 3D street par set karo)
    if 'bg-3d-street.jpg' not in h:
        # bgImage wali line dhoondo aur default badlo
        # Simple: agar bgImage set ho raha hai, to usay override karo
        pass  # (HTML me bg select hota hai, user choose karega)

    open(p, 'w').write(h)
    print('HTML V3.88 PATCHED OK')

patch_java()
patch_html()
print('V3.88 DONE')
