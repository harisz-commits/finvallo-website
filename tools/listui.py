"""Kartenlisten: kurze Werte mit Fußnoten, Filter-Daten und Filterleiste (idempotent).

Läuft in build.sh nach cleanup.py über alle Seiten mit Kartenlisten (AT und DE).
"""
import glob, hashlib, html as H, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import karten as G

R = G.R
STARS = ['*', '**', '***']
LABEL = {'Ausland': 'Ausland', 'Bargeld Inland': 'Bargeld', 'Jahresgebühr': 'Jahresgebühr'}

def short(label, raw):
    """Kurzwert für die Kachel und die Erklärung dazu (oder None, None, wenn der Wert schon kurz ist)."""
    t = H.unescape(re.sub(r'<[^>]+>', '', raw)).strip()
    if label.startswith('Bargeld'):
        if t == '0 € (verzinst)': return '0 €', 'Keine Gebühr, aber ab dem Tag der Abhebung fallen Zinsen an.'
        m = re.match(r'^(\d+) Gratis-Abhebungen/Monat', t)
        if m: return f'{m.group(1)}× gratis/Monat', t + '.'
        if re.match(r'^weltweit kostenlos', t, re.I): return 'Kostenlos', t + '.'
    if len(t) <= 20: return None, None
    m = re.match(r'^((?:ca\. )?\d+(?:,\d+)?\s?(?:%|€))', t)
    if m: return m.group(1), t.rstrip('.') + '.'
    return None, None

def earn(a):
    """Langen Sammel-Text in der Kachel kürzen; der volle Text bleibt einmal in den Punkten."""
    m = re.search(r'(<div class="earn"><span>[^<]*</span><b>)(.*?)(</b></div>)', a)
    if not m: return a, None
    full = H.unescape(m.group(2))
    if len(full) <= 60: return a, None
    sh = re.split(r';|\. |, ausgenommen', re.sub(r' \([^)]*\)', '', full))[0].strip()
    if len(sh) > 60: sh = sh[:57].rsplit(' ', 1)[0] + ' …'
    a = a[:m.start(2)] + H.escape(sh, quote=False) + a[m.end(2):]
    in_list = re.search(r'<li>' + re.escape(m.group(2)) + r'</li>', a)
    return a, None if in_list else full

def footnotes(a):
    if 'class="fns"' in a: return a
    a, extra = earn(a)
    notes = []
    def rep(m):
        lab, cls, raw = m.group(1), m.group(2), m.group(3)
        s, note = short(lab, raw)
        if not s: return m.group(0)
        mark = STARS[len(notes)]
        notes.append((mark, LABEL.get(lab, lab), note))
        return f'<div><small>{lab}</small><b{cls}>{H.escape(s, quote=False)}<sup>{mark}</sup></b></div>'
    a = re.sub(r'<div><small>([^<]*)</small><b([^>]*)>(.*?)</b></div>', rep, a)
    if extra: notes.append((STARS[len(notes)], 'Sammeln', extra.rstrip('.') + '.'))
    if not notes: return a
    fn = '<div class="fns">' + ''.join(f'<p><sup>{mk}</sup> {H.escape(lb)}: {H.escape(nt, quote=False)}</p>' for mk, lb, nt in notes) + '</div>'
    i = a.find('<ul class="checks"')
    if i >= 0:
        j = a.find('</ul>', i) + 5
        return a[:j] + '\n    ' + fn + a[j:]
    i = a.find('<div class="acts">')
    return a[:i] + fn + '\n    ' + a[i:] if i >= 0 else a

# ---------- Filter-Daten ----------
def card_index():
    D = G.prepare()
    return {(land, c['slug']): c for land in D for c in D[land][0]}

def flags(c, a):
    f = []
    if c.get('fee') == 0: f.append('fee0')
    if c.get('fx') == 0: f.append('fx0')
    m = re.search(r'<small>Bargeld[^<]*</small><b[^>]*>(.*?)</b>', a)
    if m and re.match(r'(Kostenlos|kostenlos|0 €|\d+× gratis)', re.sub(r'<[^>]+>', '', m.group(1))): f.append('cash0')
    if (c.get('tier') or 0) >= 1: f.append('ins')
    ex = c.get('ex') or {}
    if ex.get('cb'): f.append('cb')
    if ex.get('ml'): f.append('ml')
    if ex.get('lg'): f.append('lg')
    if c.get('pay'): f.append('pay')
    return ' '.join(f)

def tag(a, land, idx):
    m = re.search(r'<h3 class="iname"><a href="(?:[^"]*/)?([^"/]+)/">', a)
    if not m: return a
    c = idx.get((land, m.group(1)))
    if not c: return a
    a = re.sub(r'^(<article class="item" id="[^"]*")[^>]*>', r'\1>', a)
    fee = c.get('fee') if c.get('fee') is not None else 99999
    q = f'{c.get("titel", "")} {c.get("anbieter", "")}'.lower()
    if 'american express' in q or (c.get('netz') or '').lower() == 'american express': q += ' amex'
    q = H.escape(q)
    attrs = f' data-f="{flags(c, a)}" data-typ="{c.get("typ") or ""}" data-netz="{H.escape((c.get("netz") or "").lower())}" data-fee="{fee}" data-q="{q}"'
    return re.sub(r'^(<article class="item" id="[^"]*")>', lambda x: x.group(1) + attrs + '>', a)

def bar(n):
    chips = [('fee0', 'Ohne Jahresgebühr'), ('fx0', '0 % im Ausland'), ('cash0', 'Gratis Bargeld'), ('ins', 'Reiseversicherung'),
             ('cb', 'Cashback &amp; Punkte'), ('ml', 'Meilen'), ('lg', 'Lounge'), ('pay', 'Apple Pay / Google Pay')]
    opt = lambda xs: ''.join(f'<option value="{v}">{t}</option>' for v, t in xs)
    return f'''<div class="box filt" id="filt" hidden>
    <label class="fq"><span class="sr">Suche</span><input type="search" data-q placeholder="Karte oder Bank suchen" autocomplete="off"></label>
    <div class="chips">{"".join(f'<button type="button" class="chip" data-flag="{k}" aria-pressed="false">{t}</button>' for k, t in chips)}</div>
    <div class="frow"><select data-typ aria-label="Kartenart">{opt([("", "Alle Kartenarten"), ("Kreditkarte", "Kreditkarte mit Teilzahlung"), ("Charge", "Charge-Karte"), ("Debit", "Debitkarte"), ("Prepaid", "Prepaid-Karte")])}</select>
    <select data-netz aria-label="Kartennetz">{opt([("", "Alle Netze"), ("visa", "Visa"), ("mastercard", "Mastercard"), ("american express", "American Express"), ("diners", "Diners Club")])}</select>
    <select data-sort aria-label="Sortierung">{opt([("rank", "Nach Bewertung"), ("fee", "Günstigste zuerst"), ("name", "Nach Name")])}</select></div>
    <div class="fbot"><b data-count>{n} Karten</b><button type="button" class="lnk" data-reset hidden>Filter zurücksetzen</button></div>
  </div>
  '''

def main():
    idx = card_index()
    v = hashlib.sha256(open(R + 'assets/filter.js', 'rb').read()).hexdigest()[:8]
    for f in glob.glob(R + '**/*.html', recursive=True):
        rel = f[len(R):]
        if 'kreditkarten/rechner/' in rel: continue
        s0 = s = open(f, encoding='utf-8').read()
        s = s.replace('<label class="cmp"> Vergleichen</label>', '')
        if '<article class="item"' in s:
            land = rel.split('/')[0]
            s = re.sub(r'<article class="item".*?</article>', lambda m: footnotes(tag(m.group(0), land, idx)), s, flags=re.S)
        if rel in ('at/kreditkarten/index.html', 'de/kreditkarten/index.html'):
            s = re.sub(r'<div class="facts prose"><p><b>Kurz gesagt:</b>.*?</p></div>', '', s, count=1, flags=re.S)
            s = re.sub(r'\n  <p class="upd">Zuletzt geprüft: [^<]*</p>', '', s, count=1)
            s = re.sub(r'<div class="box filt" id="filt".*?</div>\n  </div>\n  ', '', s, flags=re.S)
            n = s.count('<article class="item"')
            s = s.replace('<details class="box howscore">', bar(n) + '<details class="box howscore">', 1)
            s = re.sub(r'<script src="[^"]*assets/filter\.js[^"]*" defer></script>', '', s)
            s = s.replace('</body>', f'<script src="../../assets/filter.js?v={v}" defer></script>\n</body>', 1)
        if s != s0: open(f, 'w', encoding='utf-8').write(s)

if __name__ == '__main__': main()
