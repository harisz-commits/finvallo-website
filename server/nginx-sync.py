#!/usr/bin/env python3
"""Bringt die Live-nginx-Konfiguration von finvallo.com auf den Stand der Vorlage (läuft aus update.sh).

In den server-Blöcken mit `root /var/www/finvallo/public;`:
- include der 301-Weiterleitungen (server/redirects.conf)
- Cache-Control für HTML, XML, TXT, JSON: 10 Minuten, must-revalidate (Server-Ebene)
- CSS/JS (per ?v=Hash versioniert): 1 Jahr, immutable; Bilder, Schriften, Manifest: 1 Tag
Sicher: Sicherungskopie, `nginx -t`, bei Fehler Rückbau. Ohne Änderung passiert nichts.
"""
import os, re, shutil, subprocess, sys

CONF = '/etc/nginx/sites-available/finvallo'
ROOT = 'root /var/www/finvallo/public;'
INC = 'include /var/www/finvallo/server/redirects.conf;'
HTML = 'add_header Cache-Control "public, max-age=600, must-revalidate";'
ASSETS = ('location ~* \\.(css|js)$ { add_header Cache-Control "public, max-age=31536000, immutable"; }\n'
          '    location ~* \\.(png|jpg|jpeg|webp|svg|ico|woff2?|webmanifest)$ { add_header Cache-Control "public, max-age=86400"; }')

if not os.path.exists(CONF): sys.exit(0)
old = open(CONF).read(); s = old
if INC not in s: s = s.replace(ROOT, ROOT + '\n    ' + INC)
# HTML-Cache: alte Server-Zeile ersetzen oder neu setzen
s = re.sub(r'add_header Cache-Control "public, max-age=3600";', HTML, s)
if HTML not in s: s = s.replace(ROOT, ROOT + '\n    ' + HTML)
# location / ohne eigenen Header (sonst überschreibt er die Server-Zeile)
s = re.sub(r'(location / \{ try_files \$uri \$uri/ =404;) add_header Cache-Control "[^"]*";', r'\1', s)
# Asset-Regeln auf den neuen Stand bringen
if ASSETS.split('\n')[0] not in s:
    # jede bisherige Asset-Regel (eine location mit css in der Endungsliste) durch die neuen zwei Regeln ersetzen
    s = re.sub(r'location ~\* \\\.\([^)]*\bcss\b[^)]*\)\$ \{[^}]*\}', lambda m: ASSETS, s)
if s == old: sys.exit(0)
shutil.copy(CONF, CONF + '.bak')
open(CONF, 'w').write(s)
if subprocess.run(['nginx', '-t'], capture_output=True).returncode != 0:
    shutil.copy(CONF + '.bak', CONF)
    print('nginx-Konfiguration ungültig, Änderung zurückgenommen.'); sys.exit(1)
subprocess.run(['systemctl', 'reload', 'nginx'])
print('nginx-Konfiguration aktualisiert und neu geladen.')
