#!/usr/bin/env python3
"""Bringt die Live-nginx-Konfiguration von finvallo.com auf den Stand der Vorlage (läuft aus update.sh).

In den server-Blöcken mit `root /var/www/finvallo/public;`:
- include der 301-Weiterleitungen (server/redirects.conf)
- Cache-Control für HTML, XML, TXT, JSON: 10 Minuten, must-revalidate (Server-Ebene)
- CSS/JS (per ?v=Hash versioniert): 1 Jahr, immutable; Bilder, Schriften, Manifest: 1 Tag
- Sicherheits-Header (server/security-headers.conf) auf Server-Ebene und in jeder location mit eigenem add_header
- HTTP/2 auf den 443-Listen-Zeilen; Brotli nur, wenn das Modul im nginx vorhanden ist
Sicher: Sicherungskopie, `nginx -t`, bei Fehler Rückbau. Ohne Änderung passiert nichts.
"""
import os, re, shutil, subprocess, sys

CONF = '/etc/nginx/sites-available/finvallo'
ROOT = 'root /var/www/finvallo/public;'
INC = 'include /var/www/finvallo/server/redirects.conf;'
HTML = 'add_header Cache-Control "public, max-age=600, must-revalidate";'
SEC = 'include /var/www/finvallo/server/security-headers.conf;'
CSS = 'location ~* \\.(css|js)$ { add_header Cache-Control "public, max-age=31536000, immutable"; ' + SEC + ' }'
IMG = 'location ~* \\.(png|jpg|jpeg|webp|svg|ico|webmanifest)$ { add_header Cache-Control "public, max-age=86400"; ' + SEC + ' }'
FONT = 'location ~* \\.woff2?$ { add_header Cache-Control "public, max-age=31536000, immutable"; ' + SEC + ' }'
BR = ('brotli on;\n    brotli_comp_level 5;\n    brotli_types text/css text/plain application/json application/javascript '
      'image/svg+xml application/xml application/manifest+json;')

def has_brotli():
    try: v = subprocess.run(['nginx', '-V'], capture_output=True, text=True).stderr
    except Exception: return False
    import glob
    return 'brotli' in v or bool(glob.glob('/etc/nginx/modules-enabled/*brotli*'))
if not os.path.exists(CONF): sys.exit(0)
old = open(CONF).read(); s = old
if INC not in s: s = s.replace(ROOT, ROOT + '\n    ' + INC)
# HTML-Cache: alte Server-Zeile ersetzen oder neu setzen
s = re.sub(r'add_header Cache-Control "public, max-age=3600";', HTML, s)
if HTML not in s: s = s.replace(ROOT, ROOT + '\n    ' + HTML)
# location / ohne eigenen Header (sonst überschreibt er die Server-Zeile)
s = re.sub(r'(location / \{ try_files \$uri \$uri/ =404;) add_header Cache-Control "[^"]*";', r'\1', s)
# Asset-Regeln auf den neuen Stand bringen (je eine location für CSS/JS und für Bilder/Schriften)
s = re.sub(r'location ~\* \\\.\([^)]*\bcss\b[^)]*\)\$ \{[^}]*\}', lambda m: CSS, s)
s = re.sub(r'location ~\* \\\.\([^)]*\bpng\b[^)]*\)\$ \{[^}]*\}', lambda m: IMG, s)
# Schriften: eigene location mit langem Cache (Dateien ändern sich nicht)
if FONT not in s: s = s.replace(IMG, IMG + '\n    ' + FONT)
# Sicherheits-Header auf Server-Ebene (gilt für alle locations ohne eigenes add_header)
if SEC + '\n' not in s.replace(CSS, '').replace(IMG, '').replace(FONT, ''): s = s.replace(ROOT, ROOT + '\n    ' + SEC)
# HTTP/2 auf allen 443-Listen-Zeilen
s = re.sub(r'(listen\s+(?:\[::\]:)?443\s+ssl)(?![^;]*\bhttp2\b)', r'\1 http2', s)
def apply(new, cur):
    """Schreibt new, prüft mit nginx -t, nimmt bei Fehler zurück. True, wenn übernommen."""
    shutil.copy(CONF, CONF + '.bak')
    open(CONF, 'w').write(new)
    if subprocess.run(['nginx', '-t'], capture_output=True).returncode != 0:
        shutil.copy(CONF + '.bak', CONF); return False
    return True

changed = False
if s != old:
    if not apply(s, old): print('nginx-Konfiguration ungültig, Änderung zurückgenommen.'); sys.exit(1)
    changed = True
# Brotli getrennt: scheitert es, bleiben die übrigen Änderungen
if 'brotli on;' not in s and 'gzip_vary on;' in s and has_brotli():
    if apply(s.replace('gzip_vary on;', 'gzip_vary on;\n    ' + BR), s): changed = True
    else: print('Brotli nicht aktiviert (nginx -t schlägt fehl).')
if changed:
    subprocess.run(['systemctl', 'reload', 'nginx'])
    print('nginx-Konfiguration aktualisiert und neu geladen.')
