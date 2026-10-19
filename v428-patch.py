# v4.28: Disable clip download requirement - V427 doesn't need clips
def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p).read()
    orig = h
    import re
    # Disable the "file chhoti hai" check by making getDownloadedCount always return 5
    # Find and replace the download check function
    if 'getDownloadedCount' in h:
        # Add override at the end: force download check to pass
        override = '<script>if(typeof getDownloadedCount!=="undefined"){var _origGDC=getDownloadedCount;getDownloadedCount=function(){return 5;};}</script>'
        if 'force download check' not in h:
            h = h.replace('</body>', override + '</body>', 1)
            print('V428 download bypass ADDED')
    h = h.replace("const APP_VER='4.27'", "const APP_VER='4.28'")
    if h != orig:
        open(p, 'w', encoding='utf-8').write(h)
    print('HTML V4.28 DONE')
def patch_java():
    print('JAVA V4.28 DONE')
patch_html()
patch_java()
print('V4.28 ALL DONE')
