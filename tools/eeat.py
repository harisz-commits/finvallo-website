"""Über Finvallo, Autorenbox, Prüfdaten und strukturierte Daten (läuft als letzter Schritt in build.sh, idempotent).

- /ueber-uns/ aus dem freigegebenen Text
- Autorenbox auf Kartenseiten, Bestenlisten und Ratgebern
- Prüfdatum: „Quelle: Preisblatt … · geprüft am …“ auf Kartenseiten, „Konditionen geprüft bis …“ auf Listen,
  „Aktualisiert am …“ auf Ratgebern; kein „Stand“ mehr in Kopfzeile und Fußzeile
- meta author, Organization + Person in jedem JSON-LD-Graph (ein @graph je Seite), Article, Product mit Review,
  FAQPage und BreadcrumbList, wo sie fehlen
Datumsquellen: Feld `geprueft` je Karte (karten.json / DE-Recherche), `updated`/`published` je Ratgeber (ratgeber.py).
"""
import glob, html as H, json, os, re, sys
from urllib.parse import quote
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import karten as K

R = K.R; E = K.E
ORG = {"@type": "Organization", "@id": "https://finvallo.com/#org", "name": "Finvallo", "url": "https://finvallo.com/",
       "logo": "https://finvallo.com/assets/og.png", "email": "hallo@finvallo.com", "founder": {"@id": "https://finvallo.com/ueber-uns/#haris"}}
PERSON = {"@type": "Person", "@id": "https://finvallo.com/ueber-uns/#haris", "name": "Haris", "url": "https://finvallo.com/ueber-uns/",
          "image": "https://finvallo.com/assets/haris.jpg", "jobTitle": "Gründer", "worksFor": {"@id": "https://finvallo.com/#org"},
          "knowsAbout": ["Kreditkarten", "Datenanalyse", "Finanzvergleich"]}
AUTH = {"@id": "https://finvallo.com/ueber-uns/#haris"}
DATE = re.compile(r'\d{2}\.\d{2}\.\d{4}')
RESERVED = {'anbieter', 'bestenlisten', 'alle', 'business', 'methodik', 'rechner'}
IMG_ERR = ' onerror="this.remove()"'   # Foto wird nachgeliefert; bis dahin kein kaputtes Bild

def dmy(iso): return K.dmy(iso)

# ---------- 1. Über Finvallo ----------
UEBER = '''<h1>Über Finvallo</h1>
<div class="prose">
<p><b>Kurz gesagt:</b> Finvallo vergleicht Kreditkarten in Österreich und Deutschland nach festen, offenen Regeln. Wir sind keine Finanzberater, und Finvallo ist keine Finanzberatung. Wir kommen aus Daten und Analyse – und genau so arbeiten wir: Zahlen sauber sammeln, alle Karten gleich behandeln, das Ergebnis verständlich zeigen.</p>
<h2>Warum es Finvallo gibt</h2>
<p>Finvallo ist aus einem eigenen Ärger entstanden. Wer eine Kreditkarte sucht, landet auf Vergleichsseiten mit Ranglisten ohne nachvollziehbare Regeln, „Testsiegern“ ohne Test und Konditionen, die mit dem Preisblatt der Bank nicht übereinstimmen.</p>
<p>Dazu kommt: „Welche Karte ist die beste?“ ist die falsche Frage. Wer viel reist, braucht etwas anderes als jemand, der nur eine Reserve für Online-Käufe will. Wer im Ausland Bargeld behebt, zahlt bei manchen Karten drauf, die sonst kostenlos sind. Die richtige Frage ist: Welche Karte passt zu dem, wie du sie nutzt? Dafür gibt es Finvallo – einen Vergleich, der von deiner Nutzung ausgeht und vorrechnet, was eine Karte dich dann wirklich kostet oder bringt.</p>
<h2>Wie wir arbeiten</h2>
<p><b>Quelle zuerst.</b> Jede Kondition stammt aus dem Preisblatt, den Bedingungen oder der Produktseite des Anbieters. Link und Prüfdatum stehen auf jeder Kartenseite.</p>
<p><b>Gleiche Regeln für alle.</b> Sieben Kriterien, feste Gewichte, öffentlich einsehbar. Keine Karte bekommt einen Bonus, weil sie Provision zahlt, und keine einen Abzug, weil sie keine zahlt. <a class="lnk" href="../at/kreditkarten/methodik/">→ So entstehen die Sterne</a></p>
<p><b>Nutzung statt Bauchgefühl.</b> Unsere Rechner zeigen, was eine Karte bei deinem Umsatz, deinem Auslandsanteil und deinen Bargeldbezügen kostet. Zwei Leute mit derselben Karte können völlig verschiedene Ergebnisse bekommen – das ist kein Fehler, das ist der Punkt.</p>
<p><b>Geld.</b> Finvallo finanziert sich über gekennzeichnete Affiliate-Links. Bewertung und Reihenfolge stehen fest, bevor wir prüfen, ob es ein Partnerprogramm gibt. <a class="lnk" href="../so-verdienen-wir-geld/">→ So verdient Finvallo Geld</a></p>
<p><b>Aktualität.</b> Banken ändern Preise ohne Ankündigung. Wir prüfen die Konditionen regelmäßig nach, und jede Seite zeigt, wann zuletzt. Lückenlos ist das nicht. Wenn du eine Abweichung findest, melde sie uns – siehe unten.</p>
<h2>Was Finvallo nicht ist</h2>
<p>Finvallo ist keine Finanzberatung und ersetzt keine. Wir erklären, was im Preisblatt steht, und rechnen vor, was es für verschiedene Nutzungsprofile bedeutet. Ob eine Karte für dich richtig ist, entscheidest du. Beratung zu deiner persönlichen Situation bekommst du bei Stellen, die dafür da sind – in Österreich etwa beim Konsumentenschutz der Arbeiterkammer, in Deutschland bei der Verbraucherzentrale.</p>
<h2>Wer dahinter steht</h2>
<p><img class="founder" src="/assets/haris.jpg" alt="Haris, Gründer von Finvallo" width="120" height="120"''' + IMG_ERR + '''></p>
<p><b>Haris</b> – Gründer, Wien</p>
<p>Hat Finvallo gebaut und betreibt es derzeit allein. Kommt aus Daten und Analyse: sammeln, prüfen, auswerten, aus Zahlen Entscheidungsgrundlagen machen. Kein Finanzberater, kein Banker – und das soll so bleiben. Finvallo liefert Regeln und Rechner, keine Empfehlungen.</p>
<h2>Fehler gefunden?</h2>
<p>Dann wollen wir es wissen. Schreib an <a class="lnk" href="mailto:korrektur@finvallo.com">korrektur@finvallo.com</a> mit Kartenname und Quelle. Wir korrigieren und vermerken das Datum der Korrektur auf der betroffenen Seite.</p>
<h2>Kontakt</h2>
<p><a class="lnk" href="mailto:hallo@finvallo.com">hallo@finvallo.com</a> · Finvallo, Wien</p>
</div>'''
UT = 'Über Finvallo: Wer dahinter steht und wie wir arbeiten | Finvallo'
UD = 'Finvallo vergleicht Kreditkarten in Österreich und Deutschland nach festen, offenen Regeln. Keine Finanzberatung. Wer dahinter steht, wie wir prüfen und wie wir Geld verdienen.'

def ueber(s):
    s = re.sub(r'<title>.*?</title>', f'<title>{E(UT)}</title>', s, count=1)
    for a in ('name="description"', 'property="og:description"'): s = re.sub(rf'<meta {a} content="[^"]*">', f'<meta {a} content="{E(UD)}">', s, count=1)
    s = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{E(UT)}">', s, count=1)
    m = re.search(r'<main[^>]*>(.*?)</main>', s, re.S)
    inner = m.group(1)
    crumb = re.search(r'<div class="crumb">.*?</div>', inner, re.S)
    new = (crumb.group(0) if crumb else '') + '\n' + UEBER + '\n'
    s = s[:m.start(1)] + new + s[m.end(1):]
    s = s.replace('<a href="">Über uns</a>', '<a href="">Über Finvallo</a>').replace('› Über uns</span>', '› Über Finvallo</span>')
    s = s.replace('"name": "Über uns"', '"name": "Über Finvallo"')
    s = re.sub(r'("@type": "AboutPage", "@id": "[^"]*", "url": "[^"]*", "name": )"[^"]*", "description": "[^"]*"', lambda m: m.group(1) + json.dumps(UT, ensure_ascii=False) + ', "description": ' + json.dumps(UD, ensure_ascii=False), s)
    return s

# ---------- 2. Autorenbox ----------
def author_box(land, title):
    t = re.sub(r'\s*\|\s*Finvallo\s*$', '', H.unescape(title))
    mail = 'mailto:korrektur@finvallo.com?subject=' + quote('Korrektur: ' + t)
    return (f'<!--author--><aside class="author-box" aria-label="Über den Autor"><img src="/assets/haris.jpg" alt="Haris" width="48" height="48"{IMG_ERR}>'
            f'<div><p><b>Haris</b> betreibt Finvallo. Er kommt aus Daten und Analyse, nicht aus der Finanzberatung – deshalb gibt es hier Regeln und Rechner statt Empfehlungen.</p>'
            f'<p class="author-links"><a class="lnk" href="/ueber-uns/">Über Finvallo</a> · <a class="lnk" href="/{land}/kreditkarten/methodik/">So entstehen die Sterne</a> · <a class="lnk" href="{H.escape(mail)}">Fehler melden</a></p></div></aside><!--/author-->')

def put_author(s, box, before):
    s = re.sub(r'<!--author-->.*?<!--/author-->\s*', '', s, flags=re.S)
    for b in before:
        i = s.find(b)
        if i >= 0: return s[:i] + box + '\n' + s[i:]
    i = s.rfind('</main>')
    return s[:i] + box + '\n' + s[i:] if i >= 0 else s

# ---------- 3. Datum ----------
def no_stand(s):
    # Kopfzeile: rechte Datumsspalte im Breadcrumb
    s = re.sub(r'(<div class="crumb">.*?)<span>Stand \d{2}\.\d{2}\.\d{4}</span>(</div>)', r'\1\2', s, count=1, flags=re.S)
    # Fußzeile
    s = re.sub(r'<span>Stand \d{2}\.\d{2}\.\d{4} · ', '<span>© 2026 Finvallo · ', s)
    s = re.sub(r'© (\d{4}) Finvallo · Stand \d{2}\.\d{2}\.\d{4}', r'© \1 Finvallo', s)
    return s

def date_line(s, html_line, cls):
    s = re.sub(rf'<p class="{cls}">.*?</p>\n?', '', s)
    m = re.search(r'</h1>', s)
    return s[:m.end()] + html_line + s[m.end():] if m else s

def list_dates(s, maxd):
    d = dmy(maxd)
    body_start = s.find('<body')
    head, body = s[:body_start], s[body_start:]
    head = re.sub(r'(<meta (?:name="description"|property="og:description") content="[^"]*?)Stand:? \d{2}\.\d{2}\.\d{4}', rf'\g<1>Stand {d}', head)
    body = re.sub(r'\s?Stand: \d{2}\.\d{2}\.\d{4}\.', '', body)
    body = re.sub(r'\s?\(Stand \d{2}\.\d{2}\.\d{4}\)', '', body)
    s = head + body
    return date_line(s, f'<p class="checked-line">Konditionen geprüft bis {d}</p>', 'checked-line')

# ---------- 5. JSON-LD ----------
def ld_merge(s, extra=(), patch=None):
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
    items = []
    for b in blocks:
        try: d = json.loads(b)
        except Exception: continue
        for x in (d.get('@graph') if isinstance(d, dict) and '@graph' in d else d if isinstance(d, list) else [d]):
            if isinstance(x, dict): x.pop('@context', None); items.append(x)
    out = [dict(ORG), dict(PERSON)]
    ids = {ORG['@id'], PERSON['@id']}; once = set()
    for x in items:
        t = x.get('@type'); i = x.get('@id')
        if i and i in ids: continue
        if t in ('Organization', 'Person') and not i: continue
        if t in ('Article', 'FAQPage', 'BreadcrumbList'):
            if t in once: continue
            once.add(t)
        if t == 'Product' and (i or '').endswith('#product'): continue
        if i: ids.add(i)
        out.append(x)
    out += list(extra)
    if patch: patch(out)
    g = json.dumps({"@context": "https://schema.org", "@graph": out}, ensure_ascii=False).replace('</', '<\\/')
    s = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', s, flags=re.S)
    return s.replace('</head>', f'<script type="application/ld+json">{g}</script>\n</head>', 1)

def has(out, t): return any(x.get('@type') == t for x in out)

def faq_from_html(s):
    qs = re.findall(r'<details>\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>\s*</details>', s, re.S)
    qs += re.findall(r'<details class="hp-faq"><summary>(.*?)</summary><p>(.*?)</p></details>', s, re.S)
    clean = lambda t: H.unescape(re.sub(r'<[^>]+>', '', t)).strip()
    return [(clean(q), clean(a)) for q, a in qs]

def crumbs_from_html(s, rel):
    m = re.search(r'<div class="crumb"><span>(.*?)</span>', s, re.S)
    out = [('Finvallo', '')]
    if m:
        for a, t in re.findall(r'<a href="([^"]*)">(.*?)</a>', m.group(1)):
            u = os.path.normpath(os.path.join('/' + rel, a)).lstrip('/')
            out.append((H.unescape(re.sub(r'<[^>]+>', '', t)), (u + '/') if u and not u.endswith('/') else u))
        last = re.sub(r'<a [^>]*>.*?</a>\s*›?\s*', '', m.group(1)).strip()
        if last: out.append((H.unescape(re.sub(r'<[^>]+>', '', last)), rel))
    else:
        t = re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S)
        out.append((H.unescape(re.sub(r'<[^>]+>', '', t.group(1))).strip() if t else rel, rel))
    return out

def generic_patch(s, rel):
    def p(out):
        if not has(out, 'BreadcrumbList') and rel:
            out.append({"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": f"https://finvallo.com/{u}"} for i, (n, u) in enumerate(crumbs_from_html(s, rel))]})
        faq = faq_from_html(s)
        if faq and not has(out, 'FAQPage'):
            out.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]})
        for x in out:
            if x.get('@type') in ('WebPage', 'AboutPage', 'CollectionPage') and 'publisher' in x: x['publisher'] = {"@id": ORG['@id']}
    return p

# ---------- Ablauf ----------
def main():
    import ratgeber as RG
    DATA = K.prepare()
    cards = {land: {c['slug']: c for c in DATA[land][0]} for land in DATA}
    rdates = RG.dates()
    n = {'author': 0, 'quelle': 0, 'liste': 0, 'ratgeber': 0}
    for f in sorted(glob.glob(R + '**/*.html', recursive=True)):
        rel = f[len(R):]
        rel = '' if rel == 'index.html' else rel[:-len('index.html')] if rel.endswith('index.html') else rel
        s0 = s = open(f, encoding='utf-8').read()
        if '<head>' not in s: continue
        s = s.replace('<meta name="author" content="Finvallo-Redaktion">', '<meta name="author" content="Haris, Finvallo">')
        if 'name="author"' not in s: s = s.replace('<meta name="viewport" content="width=device-width, initial-scale=1">', '<meta name="viewport" content="width=device-width, initial-scale=1">\n<meta name="author" content="Haris, Finvallo">', 1)
        s = re.sub(r'(<a href="[^"]*ueber-uns/"[^>]*>)Über uns(</a>)', r'\1Über Finvallo\2', s)
        s = no_stand(s)
        if rel == 'ueber-uns/': s = ueber(s)
        parts = rel.split('/')
        land = parts[0] if parts[0] in ('at', 'de') else None
        title = (re.search(r'<title>(.*?)</title>', s, re.S) or [None, ''])[1]
        extra = []; patch = generic_patch(s, rel)
        K.use(land) if land else None
        # Kartenseite
        if land and len(parts) == 4 and parts[1] == 'kreditkarten' and parts[2] not in RESERVED and parts[2] in cards[land]:
            c = cards[land][parts[2]]
            src = c.get('preis') or c.get('quelle')
            line = f'<p class="source-line">Quelle: {"<a class=\"lnk\" href=\"" + E(src) + "\" target=\"_blank\" rel=\"noopener\">Preisblatt</a>" if src else "Preisblatt"} {E(c["anbieter"])} · geprüft am {dmy(c["geprueft"])}</p>'
            s = re.sub(r'<p class="source-line">.*?</p>', '', s)
            s = s.replace('<h2>Konditionen im Überblick</h2>', '<h2>Konditionen im Überblick</h2>' + line, 1); n['quelle'] += 1
            s = put_author(s, author_box(land, title), ['<h2>Ähnliche Karten</h2>']); n['author'] += 1
            url = f'https://finvallo.com/{rel}'
            prod = {"@type": "Product", "@id": url + "#product", "name": c['titel'], "brand": {"@type": "Brand", "name": c['anbieter']}, "url": url}
            if c.get('stars'): prod["review"] = {"@type": "Review", "author": AUTH, "datePublished": c['geprueft'], "reviewRating": {"@type": "Rating", "ratingValue": c['stars'], "bestRating": 5, "worstRating": 1}}
            extra.append(prod)
        # Listen und Bestenlisten
        elif land and len(parts) >= 3 and parts[1] == 'kreditkarten' and (parts[2] in ('', 'alle', 'business', 'bestenlisten')):
            linked = set(re.findall(rf'href="(?:\.\./)*(?:{land}/kreditkarten/)?([a-z0-9-]+)/"', s)) & set(cards[land])
            lohnt_card = len(parts) == 6 and parts[3] == 'lohnt-sich'
            if lohnt_card: linked = {parts[4]} & set(cards[land])
            if linked:
                mx = max(cards[land][x]['geprueft'] for x in linked)
                if lohnt_card:
                    lp = os.path.join(K.SP, 'daten', land, 'lohnt.json')
                    lx = {x['slug']: x for x in json.load(open(lp))['karten']} if os.path.exists(lp) else {}
                    mx = (lx.get(parts[4]) or {}).get('geprueft') or mx
                s = list_dates(s, mx); n['liste'] += 1
            hub = rel in (f'{land}/kreditkarten/', f'{land}/kreditkarten/bestenlisten/', f'{land}/kreditkarten/alle/', f'{land}/kreditkarten/business/')
            if parts[2] == 'bestenlisten' and not hub:
                s = put_author(s, author_box(land, title), []); n['author'] += 1
        # Ratgeber
        elif land and len(parts) == 4 and parts[1] == 'ratgeber' and parts[2]:
            d = rdates.get((land, parts[2]), {})
            upd = d.get('updated'); pub = d.get('published') or upd
            if upd: s = date_line(s, f'<p class="updated-line">Aktualisiert am {dmy(upd)}</p>', 'updated-line')
            corr = d.get('corrections') or []
            s = re.sub(r'<!--korr-->.*?<!--/korr-->', '', s, flags=re.S)
            if corr:
                kb = '<!--korr--><section class="korrekturen"><h2>Korrekturen</h2>' + ''.join(f'<p>Korrigiert am {dmy(k["date"])}: {E(k["note"])}</p>' for k in corr) + '</section><!--/korr-->'
                i = s.find('<h2>Weitere Beiträge</h2>'); i = i if i >= 0 else s.rfind('</main>')
                s = s[:i] + kb + s[i:]
            s = put_author(s, author_box(land, title), ['<h2>Weitere Beiträge</h2>']); n['author'] += 1; n['ratgeber'] += 1
            h1 = re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S)
            canon = re.search(r'<link rel="canonical" href="([^"]+)"', s)
            def rp(out, h1=h1, canon=canon, pub=pub, upd=upd, base=patch):
                base(out)
                art = next((x for x in out if x.get('@type') == 'Article'), None)
                if not art: art = {"@type": "Article"}; out.append(art)
                art.update({"headline": H.unescape(re.sub(r'<[^>]+>', '', h1.group(1))).strip() if h1 else title, "inLanguage": K.LANDS[land]['lang'],
                            "author": AUTH, "publisher": {"@id": ORG['@id']}, "mainEntityOfPage": canon.group(1) if canon else f'https://finvallo.com/{rel}'})
                if pub: art["datePublished"] = pub
                if upd: art["dateModified"] = upd
            patch = rp
        s = ld_merge(s, extra, patch)
        if s != s0: open(f, 'w', encoding='utf-8').write(s)
    # llms.txt
    for fn in ('llms.txt', 'llms-full.txt'):
        p = R + fn
        if not os.path.exists(p): continue
        t = open(p, encoding='utf-8').read()
        add = 'Betrieben von Haris (Wien), Hintergrund Daten und Analyse; keine Finanzberatung. Details: https://finvallo.com/ueber-uns/'
        if add not in t: t = re.sub(r'^(> .*)$', lambda m: m.group(1) + ' ' + add, t, count=1, flags=re.M)
        open(p, 'w', encoding='utf-8').write(t)
    print('E-E-A-T:', n)

if __name__ == '__main__': main()
