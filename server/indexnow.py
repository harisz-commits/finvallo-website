#!/usr/bin/env python3
"""Meldet geänderte Seiten per IndexNow (Bing, Yandex, Naver, Seznam u. a.).

Aufruf aus update.sh:  git diff --name-only ALT NEU -- public | python3 indexnow.py
Mit --alle werden alle Seiten aus der Sitemap gemeldet (einmalig beim ersten Lauf).
Der Schlüssel liegt öffentlich als /<KEY>.txt im Web-Verzeichnis.
"""
import json, os, re, sys, urllib.request
KEY = '66ac601e6f99eda720b033227ad1d8dc'
HOST = 'finvallo.com'
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public')

def urls_from_diff(lines):
    out = []
    for f in lines:
        f = f.strip()
        if not f.startswith('public/') or not f.endswith('.html') or f == 'public/404.html': continue
        rel = f[len('public/'):]
        rel = '' if rel == 'index.html' else rel[:-len('index.html')] if rel.endswith('/index.html') else rel
        if os.path.exists(os.path.join(ROOT, f[len('public/'):])): out.append(f'https://{HOST}/{rel}')
    return out

def urls_from_sitemap():
    return re.findall(r'<loc>(https://finvallo\.com/[^<]*)</loc>', open(os.path.join(ROOT, 'sitemap.xml')).read())

def send(urls):
    urls = list(dict.fromkeys(urls))
    for i in range(0, len(urls), 10000):
        body = json.dumps({'host': HOST, 'key': KEY, 'keyLocation': f'https://{HOST}/{KEY}.txt', 'urlList': urls[i:i + 10000]}).encode()
        req = urllib.request.Request('https://api.indexnow.org/indexnow', data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
        try:
            with urllib.request.urlopen(req, timeout=30) as r: print(f'IndexNow: {len(urls[i:i + 10000])} Seiten gemeldet (HTTP {r.status})')
        except Exception as e: print('IndexNow fehlgeschlagen:', e)

if __name__ == '__main__':
    urls = urls_from_sitemap() if '--alle' in sys.argv else urls_from_diff(sys.stdin)
    if urls: send(urls)
