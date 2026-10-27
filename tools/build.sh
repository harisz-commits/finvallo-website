#!/bin/bash
# Kompletter Neuaufbau aller generierten Seiten in der richtigen Reihenfolge.
set -e; cd "$(dirname "$0")/.."
python3 tools/karten.py
python3 tools/girokonto.py
python3 tools/festgeld.py
python3 tools/lohnt.py
python3 tools/rechnen.py seite
python3 tools/ratgeber.py
python3 tools/rechner.py
python3 tools/header.py >/dev/null
python3 tools/landing.py
python3 tools/cleanup.py
python3 tools/listui.py
python3 tools/rechnen.py
python3 tools/eeat.py
V=$(sha256sum public/assets/site.css | cut -c1-8)
find public -name '*.html' -exec sed -i -E "s#(assets/site\.css)\?v=[a-z0-9]+\"#\1?v=$V\"#g" {} +
# Verifizierungs-Tag (Impact) auf allen Seiten, auch den statischen; idempotent
python3 - <<'PY'
import glob,re
TAG="<meta name='impact-site-verification' value='395412e1-70ac-412c-9ce9-5e53d7b5e5ef'>"
for f in glob.glob('public/**/*.html',recursive=True):
    s=open(f).read()
    if 'impact-site-verification' in s or '<head' not in s: continue
    m=re.search(r'<meta name="viewport"[^>]*>',s)
    s=s[:m.end()]+'\n'+TAG+s[m.end():] if m else s.replace('<head>','<head>\n'+TAG,1)
    open(f,'w').write(s)
PY
rm -rf tools/__pycache__
echo "fertig, css v=$V"
# SEO-Prüfung (C26); bricht bei Fehlern mit Exit-Code 1 ab
if command -v node >/dev/null; then node scripts/seo-check.mjs; fi
