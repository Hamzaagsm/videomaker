#!/usr/bin/env python3
"""MEER build gate: syntax-check the BUILT index.html before the APK ships.

Why: v4.32 shipped with `var $` (v430 shim, <head>) + `const $` (base, <body>)
in the same global scope -> "Identifier '$' has already been declared" on
Hamza's phone. A per-script check would NOT catch it; concatenating all
classic scripts reproduces the shared global scope, so node --check DOES.

Usage: python3 validate_js.py path/to/index.html
Exit 0 = all clear, exit 1 = broken JS (fail the build).
"""
import re
import subprocess
import sys
import tempfile
import os

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else 'android/app/src/main/assets/www/index.html'
    html = open(path, encoding='utf-8').read()

    classic_parts = []
    module_parts = []
    # find inline scripts (skip external src=)
    for m in re.finditer(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>',
                         html, re.DOTALL | re.IGNORECASE):
        tag = m.group(0)[:200]
        body = m.group(1)
        if not body.strip():
            continue
        if re.search(r'type\s*=\s*["\']module["\']', tag, re.IGNORECASE):
            module_parts.append(body)
        else:
            classic_parts.append(body)

    print(f"found {len(classic_parts)} classic scripts, {len(module_parts)} module scripts")

    failures = []

    def check(name, code):
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False,
                                         encoding='utf-8') as f:
            f.write(code)
            tmp = f.name
        try:
            r = subprocess.run(['node', '--check', tmp],
                               capture_output=True, text=True, timeout=60)
            if r.returncode != 0:
                failures.append((name, (r.stderr or r.stdout).strip()[:500]))
                print(f"FAIL: {name}\n{(r.stderr or r.stdout).strip()[:500]}")
            else:
                print(f"OK: {name}")
        finally:
            os.unlink(tmp)

    # Classic scripts share ONE global scope -> concatenate to catch
    # cross-script redeclarations (var $ vs const $, etc.)
    check('classic-scripts-concatenated', '\n;\n'.join(classic_parts))
    for i, body in enumerate(module_parts):
        check(f'module-script-{i}', body)

    if failures:
        print(f"\nVALIDATION FAILED: {len(failures)} bad script group(s) - DO NOT SHIP")
        return 1
    print("\nVALIDATION PASSED: built JS parses cleanly")
    return 0

if __name__ == '__main__':
    sys.exit(main())
