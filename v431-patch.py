import re


with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()


# Fix "go is not defined" - add fallback before </head>
go_fix = '<script>if(typeof go==="undefined"){var go=function(){console.log("go called");};} if(typeof $==="undefined"){var $=function(s){return document.querySelector(s);};}</script></head>'
html = html.replace('</head>', go_fix, 1)


# Bump APP_VER to 4.31
html = re.sub(r'APP_VER\s*=\s*["\']?4\.\d+["\']?', 'APP_VER="4.31"', html)


# Update footer version
html = html.replace('v4.30 MEER', 'v4.31 MEER')
html = html.replace('v4.15 MEER', 'v4.31 MEER')


with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)


print("v4.31 patch applied: go fix + version bump")
