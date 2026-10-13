"""Bereinigt alle öffentlichen Seiten von internen Recherche-Notizen (idempotent).

Läuft am Ende von build.sh über public/. Entfernt Faktencheck-Blöcke, Sek.-Marker,
Prüfstatus, Hinweise auf Vergleichsportale, gegenderte Formen und stellt
„Auf einen Blick“ vor das Abschnittsmenü der Kartenseiten.
"""
import glob, json, os, re, shutil

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public') + '/'

# ---------- Ziel-URLs statt Vergleichsportal-Links ----------
URLS = {
    'https://www.capitalo.at/kreditkarte': 'https://www.santanderconsumer.at/',
    'https://www.capitalo.at/anbieter/traderepublic/produkte/kreditkarte': 'https://traderepublic.com/de-at/karte',
    'https://www.capitalo.at/anbieter/wise/produkte/debitkarte': 'https://wise.com/at/card/',
}

# ---------- reine Textersetzungen (HTML, JSON, TXT, XML) ----------
TEXT = [
    # Gendern -> generisches Maskulinum
    (r'und:innen', 'unden'),
    (r'\bKund:in\b', 'Kunde'),
    (r'Partner:innen', 'Partner'), (r'Partner:in\b', 'Partner'),
    (r'Maturant:innen', 'Maturanten'), (r'gefährt:innen', 'gefährten'),
    (r'(\w+)er:innen', r'\1er'), (r'(\w+)er:in\b', r'\1er'),
    # Prüfkandidat
    (r' \(Prüfkandidat\)', ''), (r'-karte-pruefkandidat', '-karte'), (r' ?(Zusätzlicher )?Anbieter-Prüfkandidat\.?', ''),
    (r' Prüfkandidat\.', ''),
    # Vergleichsportale / Sekundärquellen
    (r' „Sek\.“ = Wert nur aus Vergleichsportal oder Fachblog\.', ''),
    (r' Haben wir einen Wert nur von einem Vergleichsportal oder Fachblog, (steht „Sek\.“ daneben|markieren wir ihn mit „Sek\.“)\.', ''),
    (r' Werte, die wir nur bei Vergleichsportalen finden, markieren wir mit „Sek\.“\.', ''),
    (r', teils Vergleichsportale \(in den Details als „Sek\.“ markiert\)', ''),
    (r' Jede Korrektur steht mit Quelle im Faktencheck\.', ''),
    (r' Alle Quellen stehen im <a href="[^"]*faktencheck/">Faktencheck</a>\.', ''),
    (r'Laut Capitalo kosten Zahlungen in Fremdwährung', 'Zahlungen in Fremdwährung kosten'),
    (r'\(Capitalo: ', '('), (r'[Ll]aut Capitalo,? ?', ''),
    (r'Laut Vergleichsportal ', ''), (r'[Ll]aut Vergleichsportalen?:? ?', ''),
    (r' Diese Angabe stammt von einem Vergleichsportal und sollte im Vertrag geprüft werden\.', ' Details bitte im Vertrag prüfen.'),
    (r' \(laut Portal\)', ''), (r' laut Portal', ''), (r' \(Betrag nur aus Portal\)', ''),
    (r'\(laut Portal ([^)]*)\)', r'(\1)'),
    (r'Stand Blogs \d{4}/\d{4}, ', ''), (r' Summen und Bedingungen nicht geprüft\.', ''),
    (r'[;,]? ?laut Sekundärquelle', ''), (r' ?\(zwei Sekundärquellen übereinstimmend\)', ''),
    (r'Sekundärquelle \(Capitalo\)[.;]? ?', ''), (r' ?\(Capitalo\)', ''), (r'(?<=": ")Sekundärquelle[.;]? ?', ''), (r' ?Mindestbetrag dort widersprüchlich\.', ''),
    (r'Preiskonflikt: [^;"]*; ', ''), (r' \(Sekundärquelle\)', ''), (r'Konditionen nur aus Sekundärquelle', 'Konditionen beim Anbieter prüfen'),
    (r'Sekundärquelle; im Vertrag prüfen\.', 'Im Vertrag prüfen.'), (r' ?· nur aus Sekundärquelle', ''), (r' ?Daten bisher nur aus Sekundärquelle\.', ''),
    (r' ?\(laut Portal; auf Bankseite nicht beziffert\)', ''), (r'\(Portale: bis ([^)]*)\)', r'(meist bis \1)'), (r'Laut Portal: ', ''),
    (r' ?Werte aus Sekundärquellen sind mit „Sek\.“ markiert\.', ''),
    (r'Prüfkandidat\. ?', ''),
    (r' ?Jede Korrektur (?:steht|dokumentieren wir) mit Quelle im ?(?:<a [^>]*>Faktencheck</a>)?\s?\.', ''),
    (r' und dokumentieren Änderungen im (?:<a [^>]*>)?Faktencheck(?:</a>)?\.', '.'),
    (r'Recherche \d\d\.\d\d\.\d{4} · Faktencheck (\d\d\.\d\d\.\d{4})', r'Stand \1'),
    (r'Inland laut Anbieter widersprüchlich', 'Inland beim Anbieter prüfen'),
    (r'Folgejahrespreis beim Anbieter widersprüchlich \((\d+)/(\d+) €\)', r'Folgejahrespreis \1 bis \2 €, beim Anbieter prüfen'),
    (r'Alterswortlaut 75 widersprüchlich\.', 'Altersgrenze 75 im Vertrag prüfen.'),
    (r'Für wen passt die Karte\?', 'Für wen ist die Karte geeignet?'),
    # Bargeld-Sätze grammatisch: „kostet Kostenlos“ -> „kostet 0 %“, Wortangaben als Doppelpunkt-Form
    (r'(Bargeld (?:beheben|abheben)) kostet:? [Kk]ostenlos\b', r'\1 kostet 0 %'),
    (r'Das kostet: [Kk]ostenlos\.', 'Bargeld beheben kostet 0 %.'),
    (r'(Bargeld (?:beheben|abheben)\?(?:</summary><p>|", "acceptedAnswer": \{"@type": "Answer", "text": "))Bargeld beheben kostet 0 %\.', r'\1Ja, Bargeld beheben kostet 0 %.'),
    (r'(Bargeld (?:beheben|abheben)) kostet:? (?=(?!Inland\b)[A-ZÄÖÜ])', r'\1: '),
    (r'(Bargeld (?:beheben|abheben)) kostet: (?=\d)', r'\1 kostet '),
    (r'Das kostet: (?=(?!Inland\b)[A-ZÄÖÜ])', 'Die Bedingungen: '),
    (r' \(von dir hochgeladen\)', ''), (r', von dir hochgeladen\)', ')'),
    # „unklar“
    (r'Ausland unklar', 'Ausland beim Anbieter prüfen'), (r'Geltung für DE unklar', 'Geltung für Deutschland beim Anbieter prüfen'),
    (r'Kartennetz noch nicht bestätigt', 'Kartennetz beim Anbieter prüfen'),
    (r'Jahresgebühr nicht bestätigt', 'Jahresgebühr beim Anbieter erfragen'),
    # Methodik / Landing
    (r', Abweichungen dokumentieren wir im Faktencheck\.', '.'),
]
TEXT = [(re.compile(a), b) for a, b in TEXT]

def urls(s):
    for a, b in URLS.items(): s = s.replace(a, b)
    return s

def text(s):
    for a, b in TEXT: s = a.sub(b, s)
    return s

QUELLE = {'Bitpanda': 'https://www.bitpanda.com/de/card', 'bunq': 'https://www.bunq.com/'}

def walk(o):
    """Entfernt Verweise auf Vergleichsportale aus verschachtelten Daten."""
    if isinstance(o, dict):
        for k in list(o):
            v = o[k]
            if isinstance(v, str) and 'capitalo.' in v and k.lower() == 'quelle': del o[k]
            elif v == 'Quelle noch nachzutragen':
                q = QUELLE.get(o.get('anbieter'))
                if q: o[k] = q
                else: del o[k]
            else: walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)

# ---------- HTML-Struktur ----------
def drop_div(s, start):
    """Entfernt ab start (Position eines <div ...>) das ganze Element inkl. verschachtelter divs."""
    depth = 0
    for m in re.compile(r'<div\b|</div>').finditer(s, start):
        depth += 1 if m.group() == '<div' else -1
        if depth == 0: return s[:start] + s[m.end():]
    return s

def html(s):
    # Faktencheck-Block auf Kartenseiten
    while True:
        i = s.find('<h2>Was wir im Faktencheck geändert haben</h2>')
        if i < 0: break
        j = s.find('<div', i)
        s = drop_div(s[:i] + s[j:], i)
        s = re.sub(r'\n  \n', '\n', s)
    s = re.sub(r'<span class="sek"[^>]*>Sek\.</span>', '', s)
    s = re.sub(r'<p class="src"[^>]*>Quelle: <a href="https://www\.capitalo\.[^"]*"[^>]*>[^<]*</a></p>', '', s)
    # Quellenzeile ohne Prüfstatus
    s = re.sub(r'(<p class="src"[^>]*>(?:(?!</p>).)*?)\. Status: [^<]*</p>', r'\1.</p>', s)
    s = re.sub(r'\n?\s*<p class="src"[^>]*>Hauptquelle: Quelle noch nachzutragen\.?</p>', '', s)
    # Linktexte, die noch das Vergleichsportal nennen
    s = re.sub(r'(<a [^>]*href="https?://(?:www\.)?([^/"]+)[^"]*"[^>]*>)capitalo\.at ↗</a>', r'\1\2 ↗</a>', s)
    # Faktencheck-Links (Menü, Footer, Kacheln)
    s = re.sub(r'<a href="[^"]*kreditkarten/faktencheck/"[^>]*>Faktencheck</a>', '', s)
    s = re.sub(r'\n?<link rel="alternate"[^>]*faktencheck/"[^>]*>', '', s)
    # Kartenseite: „Auf einen Blick“ vor das Abschnittsmenü, „Kurz gesagt“ weg
    m = re.search(r'(\s*<nav class="secnav"[^>]*>.*?</nav>)\s*(<section class="facts box)( glance)?(" aria-label="Auf einen Blick">.*?</section>)', s, re.S)
    if m:
        s = s[:m.start()] + '\n  ' + m.group(2) + ' glance' + m.group(4) + m.group(1) + '\n  ' + s[m.end():].lstrip(' ')
    s = re.sub(r'(<section id="s-ueb">)\s*<h2>Kurz gesagt</h2><div class="intro">.*?</div>', r'\1', s, flags=re.S)
    # Glance-Text: kein Kartennetz in Klammern, keine Note in Klammern
    def glance(g):
        t = g.group(0)
        t = re.sub(r' \((?:Visa/Mastercard|Mastercard|Visa|American Express|Diners Club|Maestro|V PAY)\)(?= für Kunden)', '', t)
        t = re.sub(r'(von 5 Sternen) \((?:Sehr gut|Gut|Befriedigend|Ausreichend|Mangelhaft)\)', r'\1', t)
        return t
    s = re.sub(r'<section class="facts box glance".*?</section>', glance, s, flags=re.S)
    return s

# ---------- Kreditkarten-Finder (AT-SPA) ----------
def spa(s):
    a = s.index('<script id="data" type="application/json">') + len('<script id="data" type="application/json">')
    b = s.index('</script>', a)
    d = json.loads(s[a:b])
    for k in ('corr', 'portale', 'weitere', 'methodik', 'v7src', 'gebuehren'): d[k] = []
    for c in d['cards']:
        c['sek'] = []
        for k in ('status', 'kosten', 'erst'): c.pop(k, None)
    for p in d.get('providers', {}).values():
        if not p.get('web') and p.get('name') in QUELLE: p['web'] = QUELLE[p['name']]
    walk(d)
    for r in d.get('weitere', []): r.pop('Prüfstatus', None)
    for p in d.get('ins', {}).values():
        for r in (p if isinstance(p, list) else []):
            if isinstance(r, dict): r.pop('Prüfstatus', None)
    s = s[:a] + json.dumps(d, ensure_ascii=False) + s[b:]
    js = [
        (",['faktencheck','Faktencheck']", ''),
        ('<a href="#daten">Rohdaten der Recherche</a>', ''),
        ("else if(h==='faktencheck')", "else if(h==='__fc')"),
        ("else if(h==='daten')", "else if(h==='__daten')"),
        ('<h1>Rohdaten der Recherche</h1><p class="lede">Alle Tabellen aus der Excel-Recherche, nach dem Faktencheck.</p>', '<h1>Daten</h1>'),
        (". Status: ${esc(c.status||'')}</p>", ".</p>"),
        ("? '<span class=\"sek\" title=\"Nur aus Sekundärquelle\">Sek.</span>' : ''", "? '' : ''"),
        ("${x.sek?'<span class=\"sek\">Sek.</span>':''}", ''),
        ("s.push(`Bargeld beheben kostet: ${c.cashText}.`);", "s.push(/^kostenlos$/i.test(c.cashText)?'Bargeld beheben kostet 0 %.':/^(\\d|ca\\.|Inland)/.test(c.cashText)?`Bargeld beheben kostet ${c.cashText}.`:`Bargeld beheben: ${c.cashText}.`);"),
    ]
    for x, y in js: s = s.replace(x, y)
    return s

def main():
    # Faktencheck-Seiten und Prüfkandidat-Ordner
    for d in ('at/kreditkarten/faktencheck', 'de/kreditkarten/faktencheck'):
        shutil.rmtree(R + d, ignore_errors=True)
    for old in glob.glob(R + 'at/kreditkarten/*-karte-pruefkandidat'):
        new = old.replace('-karte-pruefkandidat', '-karte')
        if os.path.exists(new): shutil.rmtree(old)
        else: os.rename(old, new)
    for f in glob.glob(R + '**/*', recursive=True):
        if not os.path.isfile(f) or not f.endswith(('.html', '.json', '.txt', '.xml')): continue
        s0 = s = open(f, encoding='utf-8').read()
        if f.endswith('sitemap.xml'):
            s = re.sub(r'\s*<url>\s*<loc>[^<]*faktencheck/</loc>.*?</url>', '', s, flags=re.S)
        if f.endswith('.txt'):
            s = '\n'.join(l for l in s.split('\n') if 'faktencheck/' not in l and 'Faktencheck' not in l)
        s = urls(s)
        if f.endswith('kreditkarten/rechner/index.html'): s = spa(s)
        if f.endswith('.html'): s = html(s)
        if f.endswith('daten/kreditkarten.json'):
            d = json.loads(s)
            for c in d.get('karten', []):
                if isinstance(c, dict): c.pop('status', None); c['sek'] = []
            walk(d)
            s = json.dumps(d, ensure_ascii=False, indent=1)
        s = text(s)
        if not f.endswith('.json'): s = re.sub(r'\n{3,}', '\n\n', s)
        if s != s0: open(f, 'w', encoding='utf-8').write(s)

if __name__ == '__main__': main()
