"""Prüft die gebaute Website, bevor sie veröffentlicht wird. Exit-Code 1 bei Fehlern.

Prüft: interne Links und hreflang-Ziele, JSON-LD, doppelte Titel, Länge der Beschreibungen,
Sitemap-Einträge und interne Begriffe, die nicht öffentlich sichtbar sein dürfen.
"""
import glob, json, os, re, sys
from urllib.parse import urljoin, urlparse
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public') + '/'
INTERN = re.compile(r'hochgeladen|Faktencheck|Prüfkandidat|Prüfstatus|Sekundärquelle|[Cc]apitalo|Screenshot|Excel|Kund:innen|class="sek"|Vorprüfung')
err = []
pages = glob.glob(R + '**/index.html', recursive=True) + [R + '404.html']
titles = {}
for f in pages:
    rel = f[len(R):]
    s = open(f, encoding='utf-8').read()
    spa = rel == 'at/kreditkarten/rechner/index.html'
    base = 'https://finvallo.com/' + (rel[:-10] if rel.endswith('index.html') else '')
    if not spa:
        for h in re.findall(r'(?:href|src)="([^"#?]*)[^"]*"', s):
            if not h or h.startswith(('mailto:', 'tel:', 'javascript')): continue
            u = urlparse(urljoin(base, h))
            if u.scheme not in ('http', 'https'): err.append(f'{rel}: kaputter Link {h[:80]}'); continue
            if u.netloc != 'finvallo.com': continue
            p = u.path.lstrip('/'); t = p + 'index.html' if (p == '' or p.endswith('/')) else p
            if not os.path.exists(R + t) and rel != '404.html': err.append(f'{rel}: Link ins Leere {h}')
        txt = re.sub(r'<script type="application/ld\+json">.*?</script>', '', s, flags=re.S)
        m = INTERN.search(re.sub(r'<script.*?</script>', '', txt, flags=re.S))
        if m: err.append(f'{rel}: interner Begriff „{m.group(0)}“')
    for a in re.findall(r'hreflang="de-..". href="https://finvallo.com/([^"]*)"', s):
        if not os.path.exists(R + a + 'index.html'): err.append(f'{rel}: hreflang-Ziel fehlt {a}')
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try: json.loads(m)
        except Exception as e: err.append(f'{rel}: JSON-LD ungültig ({e})')
    t = re.search(r'<title>(.*?)</title>', s)
    if t: titles.setdefault(t.group(1), []).append(rel)
    d = re.search(r'<meta name="description" content="(.*?)"', s)
    if d and len(d.group(1)) > 160: err.append(f'{rel}: Beschreibung zu lang ({len(d.group(1))})')
for t, v in titles.items():
    if len(v) > 1: err.append(f'doppelter Titel „{t}“: {", ".join(v[:3])}')
sm = re.findall(r'<loc>https://finvallo.com/([^<]*)</loc>', open(R + 'sitemap.xml').read())
for u in sm:
    if not os.path.exists(R + (u + 'index.html' if u == '' or u.endswith('/') else u)): err.append(f'Sitemap: Seite fehlt {u}')
if len(sm) != len(set(sm)): err.append('Sitemap: doppelte Einträge')
for fn in ('at', 'de'):
    try: json.load(open(R + f'{fn}/daten/kreditkarten.json'))
    except Exception as e: err.append(f'{fn}/daten/kreditkarten.json ungültig: {e}')
print(f'{len(pages)} Seiten, {len(sm)} Sitemap-Einträge geprüft')
if err:
    print('FEHLER:'); print('\n'.join(err[:100])); sys.exit(1)
print('alles in Ordnung')
