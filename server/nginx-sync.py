#!/usr/bin/env python3
"""Bringt die Live-nginx-Konfiguration von finvallo.com auf den Stand der Vorlage (läuft aus update.sh).

Ergänzt nur fehlende Zeilen in den server-Blöcken mit `root /var/www/finvallo/public;`:
- include der 301-Weiterleitungen (server/redirects.conf)
- Cache-Control für HTML (1 Stunde)
und entfernt den doppelten Cache-Header bei Assets (`expires 30d;` neben add_header).
Sicher: Sicherungskopie, `nginx -t`, bei Fehler Rückbau. Ohne Änderung passiert nichts.
"""
import os, re, shutil, subprocess, sys

CONF = '/etc/nginx/sites-available/finvallo'
ROOT = 'root /var/www/finvallo/public;'
INC = 'include /var/www/finvallo/server/redirects.conf;'
CACHE = 'add_header Cache-Control "public, max-age=3600";'

if not os.path.exists(CONF): sys.exit(0)
old = open(CONF).read(); s = old
if INC not in s:
    s = s.replace(ROOT, ROOT + '\n    ' + INC)
if 'max-age=3600' not in s:
    # auf Server-Ebene: gilt für alle locations ohne eigenes add_header (Assets setzen ihr eigenes)
    s = s.replace(ROOT, ROOT + '\n    ' + CACHE)
s = re.sub(r'expires 30d;\s*(add_header Cache-Control "public, max-age=2592000";)', r'\1', s)
if s == old: sys.exit(0)
shutil.copy(CONF, CONF + '.bak')
open(CONF, 'w').write(s)
if subprocess.run(['nginx', '-t'], capture_output=True).returncode != 0:
    shutil.copy(CONF + '.bak', CONF)
    print('nginx-Konfiguration ungültig, Änderung zurückgenommen.'); sys.exit(1)
subprocess.run(['systemctl', 'reload', 'nginx'])
print('nginx-Konfiguration aktualisiert und neu geladen.')
