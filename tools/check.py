"""Prüft die gebaute Website, bevor sie veröffentlicht wird. Exit-Code 1 bei Fehlern.

Prüft: interne Links und hreflang-Ziele, JSON-LD, doppelte Titel, Länge der Beschreibungen,
Sitemap-Einträge und interne Begriffe, die nicht öffentlich sichtbar sein dürfen.
"""
import glob, html as H, json, os, re, sys
from urllib.parse import urljoin, urlparse
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public') + '/'
INTERN = re.compile(r'hochgeladen|Faktencheck|Prüfkandidat|Prüfstatus|Sekundärquelle|[Cc]apitalo|Screenshot|Excel|Kund:innen|class="sek"|Vorprüfung')
GLUE_OK = ('1822direkt', 'ChatGPT', 'NordVPN', 'eSIM', 'PayPal', 'MasterCard', 'iPhone', 'iOS', 'myFlex', 'WiFi', 'BahnCard', 'eBay', 'MiCA', 'BayernLB', '1822TAN', 'OeNB', '0er-Jahr')
LATER = {'assets/haris.jpg'}   # Foto wird nachgeliefert (bis dahin per onerror ausgeblendet)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import karten as K
_D = K.prepare(); ALLOWED = {}; PROV = {}
COUNT_RE = r'(?<![\w.,])(\d+) (?:bewerteten |bewertete )?(?:(?:Kredit|Debit|Prepaid|Charge|Business)-|Privat|Kredit)?[Kk]arten\b'
COUNT_OK = r'\d+ Kreditkarten in unserem \S+-Vergleich enthalten|\d+ Karten · ansehen'
for _l in ('at', 'de'):
    K.use(_l)
    _lists, _ = K.cat_lists(_D[_l][0], _l)
    ALLOWED[_l] = {K.card_count(_l, x) for x in ('all', 'private', 'business', 'rated', 'special', 'unrated')} | {len(v) for v in _lists.values()}
    PROV[_l] = {}
    for _c in _D[_l][0]: PROV[_l][_c['p']] = PROV[_l].get(_c['p'], 0) + 1
err = []
pages = glob.glob(R + '**/index.html', recursive=True) + [R + '404.html']
titles = {}
HREF = {}
FAQ = {}
for f in pages:
    rel = f[len(R):]
    s = open(f, encoding='utf-8').read()
    spa = False
    base = 'https://finvallo.com/' + (rel[:-10] if rel.endswith('index.html') else '')
    if not spa:
        TAGS = {m.group(1): m.group(0) for m in re.finditer(r'<a [^>]*href="([^"#?]*)[^"]*"[^>]*>', s[s.find('<body'):])}
        for h in re.findall(r'(?:href|src)="([^"#?]*)[^"]*"', s[s.find('<body'):]):
            if not h or h.startswith(('mailto:', 'tel:', 'javascript')): continue
            u = urlparse(urljoin(base, h))
            if u.scheme not in ('http', 'https'): err.append(f'{rel}: kaputter Link {h[:80]}'); continue
            if u.netloc != 'finvallo.com': continue
            p = u.path.lstrip('/'); t = p + 'index.html' if (p == '' or p.endswith('/')) else p
            if not os.path.exists(R + t) and rel != '404.html' and t not in LATER: err.append(f'{rel}: Link ins Leere {h}')
            me = rel.split('/')[0]
            if me in ('at', 'de') and p.split('/')[0] in ('at', 'de') and p.split('/')[0] != me and 'hreflang' not in TAGS.get(h, ''):
                err.append(f'{rel}: Link ins andere Land ohne hreflang {h}')
        txt = re.sub(r'<script type="application/ld\+json">.*?</script>', '', s, flags=re.S)
        m = INTERN.search(re.sub(r'<script.*?</script>', '', txt, flags=re.S))
        if m: err.append(f'{rel}: interner Begriff „{m.group(0)}“')
    alts = dict(re.findall(r'<link rel="alternate" hreflang="(de-AT|de-DE)" href="https://finvallo.com/([^"]*)">', s))
    HREF[rel[:-10] if rel.endswith('index.html') else rel] = alts
    for a in alts.values():
        if not os.path.exists(R + a + 'index.html'): err.append(f'{rel}: hreflang-Ziel fehlt {a}')
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try:
            j = json.loads(m)
            if not (isinstance(j, dict) and j.get('@context')): err.append(f'{rel}: JSON-LD ohne @context')
        except Exception as e: err.append(f'{rel}: JSON-LD ungültig ({e})'); continue
        for n in (j.get('@graph') or [j]):
            if n.get('@type') == 'FAQPage':
                for q in n.get('mainEntity') or []:
                    a_ = (q.get('acceptedAnswer') or {}).get('text') or ''
                    if len(a_) > 120: FAQ.setdefault(a_, set()).add(rel[:-10] if rel.endswith('index.html') else rel)
    # B15.1: zusammenklebende Wörter (Label und Wert ohne Leerzeichen)
    if not spa:
        tx = re.sub(r'</?(?:p|div|li|ul|ol|h[1-6]|tr|td|th|table|section|article|aside|nav|header|footer|main|br|summary|details|label|option|select|dt|dd|button|form|small|b)\b[^>]*>', '\n', re.sub(r'<(script|style|svg)\b.*?</\1>', '', s[s.find('<body'):], flags=re.S))
        tx = re.sub(r'https?://\S+|\b[\w.-]+\.(?:com|net|de|at)\b', '', H.unescape(re.sub(r'<[^>]+>', '', tx)))
        for m in re.finditer(r'[a-zäöüß][A-ZÄÖÜ]{2,}|\d(?!\d)[A-Za-zÄÖÜäöü]{2,}', tx):
            w = re.search(r'\S*$', tx[:m.start() + 1]).group(0) + tx[m.start() + 1:m.end()]
            if not any(a_ in tx[max(0, m.start() - 8):m.end() + 8] for a_ in GLUE_OK): err.append(f'{rel}: zusammengeklebt „{tx[max(0, m.start() - 10):m.end() + 10].strip()}“'); break
    # B17.3: höchstens 35 Navigations-/Footer-Links (außerhalb von <main>)
    outside = re.sub(r'<main\b.*?</main>', '', s[s.find('<body'):], flags=re.S)
    if len(re.findall(r'<a\s', outside)) > 35: err.append(f'{rel}: {len(re.findall(r"<a\s", outside))} Links außerhalb von <main>')
    # B14.4: höchstens ein Prüf-/Stand-Datum je Seite
    body_ = re.sub(r'<script.*?</script>|<p class="src">.*?</p>', '', s[s.find('<body'):], flags=re.S)
    ds = set(re.findall(r'(?:Stand:|[Gg]eprüft am|geprüft bis|Aktualisiert am)\s*(\d{2}\.\d{2}\.\d{4})', re.sub(r'<[^>]+>', ' ', body_)))
    if len(ds) > 1: err.append(f'{rel}: mehrere Prüfdaten {sorted(ds)}')
    if re.search('[\u2013\u2014\u2212]', s): err.append(f'{rel}: langer Strich (– — −) statt Bindestrich')
    # R7.7: sichtbares „Aktualisiert am“ = article:modified_time = dateModified
    vis = re.search(r'Aktualisiert am (\d{2})\.(\d{2})\.(\d{4})', s)
    if vis:
        iso = f'{vis.group(3)}-{vis.group(2)}-{vis.group(1)}'
        for lab, m_ in (('article:modified_time', re.search(r'article:modified_time" content="([^"]+)"', s)), ('dateModified', re.search(r'"dateModified": "([^"]+)"', s))):
            if m_ and m_.group(1)[:10] != iso: err.append(f'{rel}: „Aktualisiert am“ {iso} ≠ {lab} {m_.group(1)}')
    t = re.search(r'<title>(.*?)</title>', s)
    if t: titles.setdefault(t.group(1), []).append(rel)
    d = re.search(r'<meta name="description" content="(.*?)"', s)
    if d and len(d.group(1)) > 160: err.append(f'{rel}: Beschreibung zu lang ({len(d.group(1))})')
    if d and len(d.group(1)) < 70: err.append(f'{rel}: Beschreibung zu kurz ({len(d.group(1))})')
    if d and d.group(1).rstrip().endswith(('…', '...')): err.append(f'{rel}: Beschreibung endet mit …')
    if not d and rel != '404.html': err.append(f'{rel}: keine Beschreibung')
    # A6/R3: jede Kartenanzahl stammt aus card_count() (all, private, business, special, rated, unrated),
    # den Bestenlisten-Zählern oder auf Anbieterseiten aus der Kartenzahl des Anbieters
    lc = rel.split('/')[0]
    if lc in ALLOWED:
        txt = re.sub(r'<script.*?</script>', '', s, flags=re.S)
        prov = re.match(r'(?:at|de)/kreditkarten/anbieter/([^/]+)/', rel)
        ok = ALLOWED[lc] | ({PROV[lc].get(prov.group(1))} if prov else set())
        for m in re.finditer(COUNT_RE, txt):
            n = int(m.group(1)); ctx = txt[max(0, m.start() - 12):m.start()]
            if n < 10 or n in ok or ctx.endswith(('Trading ', '▭ ', 'bis zu ')) or re.match(COUNT_OK, txt[m.start():m.start() + 80]): continue
            err.append(f'{rel}: Kartenanzahl {m.group(0)} stammt nicht aus card_count()')
    # R5: Formular-Labels als eigenes Element, Rechner mit Standardwerten im HTML
    if re.search(r'<label>[^<]+<(?:select|input)', s): err.append(f'{rel}: Label-Text ohne eigenes Element (klebt am Feld)')
    if rel.endswith('kreditkarten/rechner/index.html'):
        f_ = re.search(r'<form[^>]*id="rbox".*?</form>', s, re.S)
        if not f_ or len(re.findall(r'<input[^>]*value=', f_.group(0))) < 5: err.append(f'{rel}: Rechner-Formular ohne Standardwerte im HTML')
# B11: hreflang symmetrisch (jede genannte Seite nennt dieselben Partner)
for r, alts in HREF.items():
    for t in alts.values():
        if HREF.get(t, {}) != alts: err.append(f'hreflang nicht symmetrisch: {r} ↔ {t}')
# B18.4: keine wortgleiche FAQ-Antwort (> 120 Zeichen) auf zwei Seiten. Erlaubt sind Länderpaare
# (Seiten, die sich per hreflang gegenseitig nennen) und die Startseite / als Kopie von /at/.
FAQ_OK = [{'', 'at/'}]
for a_, ps in FAQ.items():
    if len(ps) < 2: continue
    grps = {frozenset(HREF.get(p_, {}).values()) for p_ in ps}
    if len(grps) == 1 and ps <= next(iter(grps)) or any(ps <= g | set(HREF.get('at/', {}).values()) for g in FAQ_OK): continue
    err.append(f'FAQ-Antwort auf {len(ps)} Seiten: „{a_[:70]}…“ ({", ".join(sorted(ps)[:3])})')
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
