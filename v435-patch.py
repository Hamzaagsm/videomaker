# v4.35: remove V427 button hijack - restore original video system
import re
def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p, encoding='utf-8').read()
    before = len(h)
    h = re.sub(r'<script>var V427=.*?</script>', '', h, flags=re.DOTALL)
    print('V427 removed:', len(h) < before)
    h = re.sub(r"APP_VER\s*=\s*['\"][^'\"]*['\"]", 'APP_VER="4.35"', h)
    for v in ['v4.34 MEER','v4.33 MEER','v4.32 MEER']:
        h = h.replace(v, 'v4.35 MEER')
    open(p, 'w', encoding='utf-8').write(h)
    print('HTML v435 done')
patch_html()
print('V435 ALL DONE')
