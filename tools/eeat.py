"""Über Finvallo, Autorenbox, Prüfdaten und strukturierte Daten (läuft als letzter Schritt in build.sh, idempotent).

- /ueber-uns/ aus dem freigegebenen Text
- Autorenbox auf Kartenseiten, Bestenlisten und Ratgebern
- Prüfdatum: „Quelle: Preisblatt … · geprüft am …“ auf Kartenseiten, „Konditionen geprüft bis …“ auf Listen,
  „Aktualisiert am …“ auf Ratgebern; kein „Stand“ mehr in Kopfzeile und Fußzeile
- meta author, Organization + Person in jedem JSON-LD-Graph (ein @graph je Seite), Article, Product mit Review,
  FAQPage und BreadcrumbList, wo sie fehlen
Datumsquellen: Feld `geprueft` je Karte (karten.json / DE-Recherche), `updated`/`published` je Ratgeber (ratgeber.py).
"""
import glob, html as H, json, os, re, subprocess, sys
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
SITE = json.load(open(os.path.join(K.SP, 'daten', 'site.json')))
MAIL = {'kontakt': 'hallo@finvallo.com', 'korrektur': 'korrektur@finvallo.com', 'impressum': 'hallo@finvallo.com', **(SITE.get('mail') or {})}
RESERVED = {'anbieter', 'bestenlisten', 'alle', 'business', 'methodik', 'rechner'}
IMG_ERR = ' loading="lazy" decoding="async"'

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
<p><img class="founder" src="/assets/haris.jpg" alt="Haris, Gründer von Finvallo" width="96" height="96"''' + IMG_ERR + '''></p>
<p><b>Haris</b> – Gründer, Wien</p>
<p>Hat Finvallo gebaut und betreibt es derzeit allein. Wir schreiben „wir“, weil Finvallo wachsen soll. Derzeit steckt hinter allem eine Person. Kommt aus Daten und Analyse: sammeln, prüfen, auswerten, aus Zahlen Entscheidungsgrundlagen machen. Kein Finanzberater, kein Banker – und das soll so bleiben. Finvallo liefert Regeln und Rechner, keine Empfehlungen.</p>
<h2>Fehler gefunden?</h2>
<p>Dann wollen wir es wissen. Schreib an <a class="lnk" href="mailto:korrektur@finvallo.com">korrektur@finvallo.com</a> mit Kartenname und Quelle. Wir korrigieren und vermerken das Datum der Korrektur auf der betroffenen Seite.</p>
<h2>Kontakt</h2>
<p><a class="lnk" href="mailto:hallo@finvallo.com">hallo@finvallo.com</a> · Finvallo, Wien</p>
</div>'''
UT = 'Über Finvallo: Wer dahinter steht und wie wir arbeiten | Finvallo'
UD = 'Finvallo vergleicht Kreditkarten in Österreich und Deutschland nach festen, offenen Regeln. Keine Finanzberatung. Wer dahinter steht, wie wir prüfen und wie wir Geld verdienen.'

def ueber(s):
    s = re.sub(r'<title>.*?</title>', f'<title>{E(UT)}</title>', s, count=1)
    for a in ('name="description"', 'property="og:description"'): s = re.sub(rf'<meta {a} content="[^"]*">', f'<meta {a} content="{E(K.fit_desc(UD))}">', s, count=1)
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
    mail = 'mailto:' + MAIL['korrektur'] + '?subject=' + quote('Korrektur: ' + t)
    return (f'<!--author--><aside class="author-box" aria-label="Über den Autor"><img src="/assets/haris.jpg" alt="Haris" width="48" height="48"{IMG_ERR}>'
            f'<div><p><b>Haris</b> betreibt Finvallo. Er kommt aus Daten und Analyse, nicht aus der Finanzberatung – deshalb gibt es hier Regeln und Rechner statt persönlicher Beratung.</p>'
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

# ---------- Links im eigenen Land (A8) ----------
MAP = {}
for _a, _b in json.load(open(os.path.join(K.SP, 'daten', 'hreflang-map.json')))['paare']: MAP[_a] = _b; MAP[_b] = _a
def land_links(s, rel):
    me = rel.split('/')[0]
    if me not in ('at', 'de'): return s
    other = 'de' if me == 'at' else 'at'
    pair = other + rel[2:]
    def fix(m):
        tag, h = m.group(0), m.group(1)
        if 'hreflang=' in tag or h.startswith(('http', 'mailto', '#', '/')): return tag
        t = os.path.normpath(os.path.join(rel, h)).replace('\\', '/')
        if not (t + '/').startswith(other + '/'): return tag
        t = t + '/' if not t.endswith('/') else t
        if t == pair or t == other + '/' or t == MAP.get(rel): return tag.replace('<a ', f'<a hreflang="de-{other.upper()}" ', 1)
        own = me + t[2:]
        if os.path.exists(R + own + 'index.html'):
            return tag.replace(f'href="{h}"', f'href="{os.path.relpath(R + own, R + rel).replace(chr(92), "/")}/"', 1)
        return tag
    head, body = s[:s.find('<body')], s[s.find('<body'):]
    return head + re.sub(r'<a [^>]*href="([^"]*)"[^>]*>', fix, body)

# ---------- interne Links auf 301-Quellen direkt aufs Ziel ----------
RD = json.load(open(os.path.join(K.SP, 'daten', 'redirects.json'))) if os.path.exists(os.path.join(K.SP, 'daten', 'redirects.json')) else {}
def follow_redirects(s, rel):
    if not RD: return s
    def fix(m):
        h = m.group(1)
        if h.startswith(('http', 'mailto', '#')): return m.group(0)
        t = h if h.startswith('/') else '/' + os.path.normpath(os.path.join(rel, h)).replace(chr(92), '/') + ('/' if h.endswith('/') else '')
        if t in RD: return m.group(0).replace(f'href="{h}"', 'href="' + os.path.relpath(R + RD[t].lstrip('/'), R + rel).replace(chr(92), '/') + '/"', 1)
        return m.group(0)
    i = s.find('<body')
    return s[:i] + re.sub(r'<a [^>]*href="([^"#?]*)"[^>]*>', fix, s[i:])

# ---------- zusammenklebende Wörter (B15.1) ----------
GLUE = re.compile(r'(</(?:span|b|a|em|strong|small|sup|i)>)(<(?:span|b|a|em|strong|small|i)[\s>])')
def unglue(s):
    """Leerzeichen zwischen benachbarten Inline-Elementen, damit Text nicht zusammenklebt (Layout per Flex/Grid bleibt gleich)."""
    i = s.find('<body')
    parts = re.split(r'(<script\b.*?</script>|<style\b.*?</style>)', s[i:], flags=re.S)
    return s[:i] + ''.join(p if p.startswith(('<script', '<style')) else GLUE.sub(r'\1 \2', p) for p in parts)

# ---------- hreflang (B11) ----------
XD = {'', 'at/', 'de/', 'at/kreditkarten/', 'de/kreditkarten/', 'at/ratgeber/', 'de/ratgeber/', 'at/rechner/', 'de/rechner/',
      'at/kreditkarten/bestenlisten/', 'de/kreditkarten/bestenlisten/'}
def partner(rel):
    if rel in MAP: return MAP[rel]
    me = rel.split('/')[0]
    if me not in ('at', 'de'): return None
    o = ('de' if me == 'at' else 'at') + rel[2:]
    return o if os.path.exists(R + o + 'index.html') else None

def alternates(rel):
    if rel == '': return {'de-AT': 'at/', 'de-DE': 'de/', 'x-default': ''}
    o = partner(rel)
    if not o: return {}
    at, de = (rel, o) if rel.startswith('at/') else (o, rel)
    d = {'de-AT': at, 'de-DE': de}
    if rel in XD: d['x-default'] = ''
    return d

def set_hreflang(s, rel):
    s = re.sub(r'\n?<link rel="alternate" hreflang="[^"]*" href="[^"]*">', '', s)
    alt = alternates(rel)
    if not alt: return s
    tags = ''.join(f'<link rel="alternate" hreflang="{k}" href="https://finvallo.com/{v}">' for k, v in alt.items())
    return re.sub(r'(<link rel="canonical" href="[^"]*">)', lambda m: m.group(1) + '\n' + tags, s, count=1)

def git_date(path):
    import subprocess
    try: return subprocess.run(['git', 'log', '-1', '--format=%cs', '--', path], capture_output=True, text=True, cwd=os.path.join(R, '..')).stdout.strip() or None
    except Exception: return None

# ---------- 5. JSON-LD ----------
def ld_merge(s, extra=(), patch=None):
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
    items = []
    for b in blocks:
        try: d = json.loads(b)
        except Exception: continue
        for x in (d.get('@graph') if isinstance(d, dict) and '@graph' in d else d if isinstance(d, list) else [d]):
            if isinstance(x, dict): x.pop('@context', None); items.append(x)
    # doppelte Knoten: der zuletzt erzeugte gewinnt (neuere Builds hängen ihre Daten hinten an)
    ids = {ORG['@id'], PERSON['@id']}; once = set(); keep = []
    for x in reversed(items):
        t = x.get('@type'); i = x.get('@id')
        if i and i in ids: continue
        if t in ('Organization', 'Person') and not i: continue
        if t in ('Article', 'FAQPage', 'BreadcrumbList'):
            if t in once: continue
            once.add(t)
        if t == 'Product' and (i or '').endswith('#product'): continue
        if i: ids.add(i)
        keep.append(x)
    out = [dict(ORG), dict(PERSON)] + keep[::-1] + list(extra)
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
            if rel == '' and x.get('@type') == 'WebSite': x.update({"name": "Finvallo", "url": "https://finvallo.com/", "inLanguage": ["de-AT", "de-DE"], "publisher": {"@id": ORG['@id']}}); x.pop('potentialAction', None)
    return p

# ---------- Ablauf ----------
METH = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'daten', 'methodik.json'), encoding='utf-8'))
def methodik(s, land):
    """B19: Grenzwerte wie im Code (score.py vergleicht mit <=), Marker für die offene Regel, Slots und Gültigkeitsdatum."""
    s = re.sub(r'(<(?:span|td)>)bis (?!einschließlich)([\d,]+ (?:%|€))(</(?:span|td)>)', r'\1bis einschließlich \2\3', s)
    s = s.replace('<!-- TODO Methodik -->', '')
    s = re.sub(r'<!--warum-->.*?<!--/warum-->', '', s, flags=re.S)
    w = (METH.get('warum_gewichte') or '').strip()
    blk = f'<!--warum--><h2>Warum diese Gewichte</h2><div class="prose"><p>{E(w)}</p></div><!--/warum-->' if w else '<!--warum--><!-- Slot „Warum diese Gewichte“: Text in tools/daten/methodik.json --><!--/warum-->'
    s = s.replace('<h2>Die Regeln je Kriterium</h2>', blk + '<h2>Die Regeln je Kriterium</h2>', 1)
    calc = f'../../../{land}/rechner/teilzahlung/'
    s = s.replace('<h2>Was die Sterne nicht zeigen</h2>', '<h2>Was nicht in die Bewertung einfließt</h2>', 1)
    s = re.sub(r'<!--gruppen-->.*?<!--/gruppen-->', '', s, flags=re.S)
    s = s.replace('<h2>Was nicht in die Bewertung einfließt</h2>', '<!--gruppen--><h2>Karten für bestimmte Kundengruppen</h2><div class="prose"><p>Manche Karten bekommt nicht jede und jeder: etwa nur Studierende, junge Kundinnen und Kunden bis zu einem bestimmten Alter, Mitglieder eines Verbands oder nur bestehende Kunden. Wir bewerten sie nach denselben Regeln, führen sie aber in einer eigenen Liste unter der Rangliste. In passenden Bestenlisten, zum Beispiel für Studierende, stehen sie trotzdem.</p><p>Ist eine Karte nur bis zu einem bestimmten Alter oder nur vorübergehend gratis, zählt bei der Jahresgebühr der Preis, den du danach zahlst. Braucht eine Karte ein Girokonto beim Anbieter, zählt bei der Jahresgebühr nur der Preis der Karte. Was das Konto kostet, steht auf der Kartenseite direkt beim Preis.</p></div><!--/gruppen--><h2>Was nicht in die Bewertung einfließt</h2>', 1)
    hint = 'Zinsen für Teilzahlung zählen nicht mit, weil sie nur anfallen, wenn du nicht alles zahlst.'
    if hint in s and 'rechner/teilzahlung/' not in s:
        s = s.replace(hint, hint + f' Was sie kosten, zeigt der <a href="{calc}">Teilzahlungsrechner</a>.', 1)
    s = re.sub(r'<p class="note meth-since">.*?</p>', '', s)
    if SITE.get('methodikSeit'):
        s = re.sub(r'(<p class="lede">.*?</p>)', r'\1' + f'<p class="note meth-since">Methodik gültig seit {dmy(SITE["methodikSeit"])}.</p>', s, count=1, flags=re.S)
    return s

DASH = str.maketrans({'\u2013': '-', '\u2014': '-', '\u2212': '-'})
def undash(t):
    """Nur den normalen Bindestrich verwenden (keine Halbgeviert-, Geviert- oder Minuszeichen)."""
    return t.translate(DASH)

try: BUILD = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__))).stdout.strip() or 'unbekannt'
except Exception: BUILD = 'unbekannt'

def main():
    import ratgeber as RG
    DATA = K.prepare()
    cards = {land: {c['slug']: c for c in DATA[land][0]} for land in DATA}
    rdates = RG.dates()
    n = {'author': 0, 'quelle': 0, 'liste': 0, 'ratgeber': 0}
    global LASTMOD, NOINDEX; LASTMOD, NOINDEX = {}, {}
    for f in sorted(glob.glob(R + '**/*.html', recursive=True)):
        rel = f[len(R):]
        rel = '' if rel == 'index.html' else rel[:-len('index.html')] if rel.endswith('index.html') else rel
        s0 = s = open(f, encoding='utf-8').read()
        if '<head>' not in s: continue
        s = s.replace('<meta name="author" content="Finvallo-Redaktion">', '<meta name="author" content="Haris, Finvallo">')
        if 'name="author"' not in s: s = s.replace('<meta name="viewport" content="width=device-width, initial-scale=1">', '<meta name="viewport" content="width=device-width, initial-scale=1">\n<meta name="author" content="Haris, Finvallo">', 1)
        s = re.sub(r'(<a href="[^"]*ueber-uns/"[^>]*>)Über uns(</a>)', r'\1Über Finvallo\2', s)
        s = no_stand(s)
        s = land_links(s, rel)
        s = follow_redirects(s, rel)
        s = unglue(s)
        for attr in ('name="description"', 'property="og:description"'):
            s = re.sub(rf'(<meta {attr} content=")([^"]*)(">)', lambda m: m.group(1) + E(K.fit_desc(H.unescape(m.group(2)))) + m.group(3), s, count=1)
        if rel == 'ueber-uns/': s = ueber(s)
        s = re.sub(r'\n?<link rel="alternate" type="application/json"[^>]*>', '', s)
        if re.match(r'(at|de)/kreditkarten/(?:(?:alle|business|rechner)/|bestenlisten/(?:[a-z-]+/)?)?$', rel):
            s = re.sub(r'(<link rel="canonical"[^>]*>)', lambda m: m.group(1) + f'\n<link rel="alternate" type="application/json" href="/{rel[:2]}/daten/kreditkarten.json" title="Kartendaten als JSON">', s, count=1)
        if rel in ('at/kreditkarten/methodik/', 'de/kreditkarten/methodik/'): s = methodik(s, rel[:2])
        if rel in ('impressum/', 'datenschutz/'):
            s = re.sub(r'(E-Mail: <a href="mailto:)[^"]+(">)[^<]+(</a>)', lambda m: m.group(1) + MAIL['impressum'] + m.group(2) + MAIL['impressum'] + m.group(3), s)
        if rel == 'so-verdienen-wir-geld/':
            s = s.replace('Hinweise gern an <a href="mailto:hallo@finvallo.com">hallo@finvallo.com</a>', f'Hinweise gern an <a href="mailto:{MAIL["korrektur"]}">{MAIL["korrektur"]}</a>')
        if rel == 'impressum/':
            ph = SITE.get('phone') or ''
            s = re.sub(r'<!--phone-->.*?<!--/phone-->', '<!--phone-->' + (f'<br>Telefon: <a href="tel:{E(re.sub(r"[^+0-9]", "", ph))}">{E(ph)}</a>' if ph else '') + '<!--/phone-->', s)
        s = re.sub(r'<!--analytics-->.*?<!--/analytics-->\n?', '', s, flags=re.S)
        if (SITE.get('analytics') or {}).get('enabled'):
            a_ = SITE['analytics']
            s = s.replace('</head>', f'<!--analytics--><script defer data-domain="{E(a_["domain"])}" src="{E(a_["src"])}"></script><!--/analytics-->\n</head>', 1)
        if rel == 'at/':
            da = f'Unabhängiger Finanzvergleich für Österreich: {K.card_count("at", "all")} Karten mit offener Bewertung nach sieben Kriterien, Bestenlisten, Ratgeber und Rechner.'
            s = s.replace('Finvallo vergleicht Finanzprodukte in Österreich unabhängig und nach offenen Regeln. Jetzt: 77 Kreditkarten. Bald: Girokonten, Depots und ETFs.', da)
            s = re.sub(r'Unabhängiger Finanzvergleich für Österreich: \d+ Karten mit offener Bewertung nach sieben Kriterien, Bestenlisten, Ratgeber und Rechner\.', da, s)
        if rel == 'de/':
            dd = f'Unabhängiger Finanzvergleich für Deutschland: {K.card_count("de", "all")} Karten mit offener Bewertung nach sieben Kriterien, Bestenlisten, Ratgeber und Rechner.'
            s = re.sub(r'Kreditkarten in Deutschland: unabhängige Ratgeber zu Punkten, Meilen, Auslandsgebühren, Reiseversicherung und Kartentypen\. Der Kartenvergleich folgt\.', dd, s)
            s = re.sub(r'Unabhängiger Finanzvergleich für Deutschland: \d+ (?:Kreditkarten|Karten|Karten \(Kredit-, Debit- und Prepaid-Karten\)) mit offener Bewertung nach sieben Kriterien, Bestenlisten, Ratgeber und Rechner\.', dd, s)
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
            LASTMOD[rel] = c['geprueft']
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
                LASTMOD[rel] = mx
            hub = rel in (f'{land}/kreditkarten/', f'{land}/kreditkarten/bestenlisten/', f'{land}/kreditkarten/alle/', f'{land}/kreditkarten/business/')
            if parts[2] == 'bestenlisten' and not hub:
                s = put_author(s, author_box(land, title), []); n['author'] += 1
        # Ratgeber
        elif land and len(parts) == 4 and parts[1] == 'ratgeber' and parts[2]:
            d = rdates.get((land, parts[2]), {})
            upd = d.get('updated'); pub = d.get('published') or upd
            if upd: s = date_line(s, f'<p class="updated-line">Aktualisiert am {dmy(upd)}</p>', 'updated-line'); LASTMOD[rel] = upd
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
        md = re.search(r'<meta name="description" content="([^"]*)"', s)
        def patch2(out, _p=patch, _d=H.unescape(md.group(1)) if md else None, _u='https://finvallo.com/' + rel):
            if _p: _p(out)
            # Beschreibung der Seite im JSON-LD = aktuelle Meta Description (keine alten Texte aus früheren Builds)
            for x in out:
                if _d and 'description' in x and (x.get('url') == _u or (x.get('@id') or '').startswith(_u + '#')): x['description'] = _d
        s = ld_merge(s, extra, patch2)
        s = set_hreflang(s, rel)
        if rel not in LASTMOD:
            if land:
                linked = set(re.findall(r'href="(?:\.\./)*(?:(?:at|de)/kreditkarten/)?([a-z0-9-]+)/"', s)) & set(cards[land])
                LASTMOD[rel] = max(cards[land][x]['geprueft'] for x in linked) if linked else K.LANDS[land]['stand']
            else:
                LASTMOD[rel] = git_date(f'public/{rel}index.html' if rel else 'public/index.html') or max(K.LANDS[l]['stand'] for l in K.LANDS)
        NOINDEX[rel] = 'noindex' in (re.search(r'<meta name="robots" content="([^"]*)"', s) or [None, ''])[1]
        if rel == '':   # R2.4: Build-Marker (Commit beim Bauen), live-check vergleicht ihn mit dem Repo
            s = re.sub(r'\n?<meta name="build" content="[^"]*">', '', s)
            s = s.replace('<meta charset="utf-8">', f'<meta charset="utf-8">\n<meta name="build" content="{BUILD}">', 1)
        s = s.replace('<a href="">', '<a href="./" aria-current="page">')   # Link auf die eigene Seite
        s = undash(s)
        if s != s0: open(f, 'w', encoding='utf-8').write(s)
    # Sitemap (B11, B14, B20.8): alle indexierbaren Seiten, lastmod aus Inhaltsdaten, hreflang-Paare, keine 301-Quellen
    redir = set(json.load(open(os.path.join(K.SP, 'daten', 'redirects.json'))).keys()) if os.path.exists(os.path.join(K.SP, 'daten', 'redirects.json')) else set()
    rows = []
    for rel in sorted(LASTMOD, key=lambda r: (r.count('/'), r)):
        if NOINDEX.get(rel) or rel.endswith('.html') or ('/' + rel) in redir: continue
        alt = ''.join(f'<xhtml:link rel="alternate" hreflang="{k}" href="https://finvallo.com/{v}"/>' for k, v in alternates(rel).items())
        rows.append(f'<url><loc>https://finvallo.com/{rel}</loc><lastmod>{LASTMOD[rel]}</lastmod>{alt}</url>')
    open(R + 'sitemap.xml', 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + '\n'.join(rows) + '\n</urlset>\n')
    # llms.txt
    for fn in ('llms.txt', 'llms-full.txt'):
        p = R + fn
        if not os.path.exists(p): continue
        t = open(p, encoding='utf-8').read()
        add = 'Betrieben von Haris (Wien), Hintergrund Daten und Analyse; keine Finanzberatung. Details: https://finvallo.com/ueber-uns/'
        if add not in t: t = re.sub(r'^(> .*)$', lambda m: m.group(1) + ' ' + add, t, count=1, flags=re.M)
        # C25: einheitlicher Abschnitt „Zitieren“, Titel der Volltext-Datei mit dem jüngsten Prüfdatum
        t = t.replace(' Bitte bei Zitaten die jeweilige Seiten-URL als Quelle angeben.', '')
        t = re.sub(r'\n## Zitieren\n[^\n]*\n', '\n', t)
        t = t.replace('\n## ', '\n## Zitieren\nBeim Zitieren bitte die jeweilige Seiten-URL und das Prüfdatum angeben.\n\n## ', 1)
        if fn == 'llms-full.txt':
            mx = max(c['geprueft'] for land in cards for c in cards[land].values() if c.get('geprueft'))
            t = re.sub(r'\A# .*', f'# Finvallo – alle Kreditkarten in Österreich und Deutschland (Stand {dmy(mx)})', t, count=1)
        open(p, 'w', encoding='utf-8').write(t)
    # C25.3: Volltext aufteilen, sobald er größer als 300 KB wird
    full = R + 'llms-full.txt'
    for x in ('llms-full-at.txt', 'llms-full-de.txt'):
        if os.path.exists(R + x): os.remove(R + x)
    if os.path.getsize(full) > 300 * 1024:
        t = open(full, encoding='utf-8').read(); i = t.find('\n## Deutschland: Kreditkarten')
        if i > 0:
            open(R + 'llms-full-at.txt', 'w', encoding='utf-8').write(t[:i] + '\n')
            open(R + 'llms-full-de.txt', 'w', encoding='utf-8').write(t.split('\n', 1)[0] + '\n' + t[i:])
            lt = open(R + 'llms.txt', encoding='utf-8').read()
            if 'llms-full-at.txt' not in lt:
                lt = lt.rstrip() + '\n\n## Volltext\n- [Alle Karten Österreich](https://finvallo.com/llms-full-at.txt)\n- [Alle Karten Deutschland](https://finvallo.com/llms-full-de.txt)\n'
                open(R + 'llms.txt', 'w', encoding='utf-8').write(lt)
    for fn in glob.glob(R + 'llms*.txt') + glob.glob(R + '*/daten/*.json'):
        t = open(fn, encoding='utf-8').read(); u = undash(t)
        if u != t: open(fn, 'w', encoding='utf-8').write(u)
    print('E-E-A-T:', n)

if __name__ == '__main__': main()
