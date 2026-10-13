"""„Ab wann lohnt sich …?“ – Rechnung für Premiumkarten (AT und DE).

Daten: daten/<land>/lohnt.json (Guthaben, Lounge, Abos, Willkommensbonus je Karte und die Annahmen).
Erzeugt: <land>/kreditkarten/bestenlisten/lohnt-sich/ (Übersicht) und …/lohnt-sich/<slug>/ (je Karte),
setzt den Block „Top-Karten, wenn …“ oben auf die Bestenlisten-Übersicht und ergänzt Sitemap und llms.txt.
Läuft in build.sh direkt nach karten.py.
"""
import html, json, math, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import karten as K
from score import eur

R = K.R; SP = K.SP; E = K.E
PROFILE = [
    dict(k='selten', t='Du reist ein- bis zweimal im Jahr', d='4 Lounge-Besuche, 1.000 € Kartenumsatz im Monat, Guthaben nutzt du nicht, eine Reiseversicherung brauchst du ohnehin.',
         p=dict(credits=False, lounge=4, guests=0, spend=1000, vers=True, subs=False)),
    dict(k='geniesser', t='Du nutzt alle Guthaben', d='Restaurant-, Reise- und Entertainment-Guthaben voll genutzt, 6 Lounge-Besuche, 1.500 € Umsatz im Monat, Reiseversicherung nötig.',
         p=dict(credits=True, lounge=6, guests=0, spend=1500, vers=True, subs=False)),
    dict(k='viel', t='Du fliegst oft', d='20 Lounge-Besuche im Jahr, davon 6 mit Begleitung, 2.500 € Umsatz im Monat, Guthaben und Abos genutzt, Reiseversicherung nötig.',
         p=dict(credits=True, lounge=20, guests=6, spend=2500, vers=True, subs=True)),
]

def load(land):
    p = SP + f'/daten/{land}/lohnt.json'
    return json.load(open(p)) if os.path.exists(p) else None

def free_visits(x):
    v = (x.get('lounge') or {}).get('visits')
    return math.inf if v == 'unbegrenzt' else (v or 0)

def value(c, x, A, p):
    """Wert der genutzten Vorteile pro Jahr (ohne Willkommensbonus) und Aufschlüsselung."""
    parts = []
    if p['credits']:
        for g in x.get('credits') or []: parts.append((g['name'], g['eur']))
    lv = min(p['lounge'], free_visits(x))
    if lv: parts.append((f'{lv if lv != math.inf else p["lounge"]} Lounge-Besuche', lv * A['lounge_eur']))
    gf = (x.get('lounge') or {}).get('guests_free') or 0
    gv = min(p['guests'], lv, math.inf if gf == 'unbegrenzt' else gf)
    if gv: parts.append((f'{gv} Begleitpersonen in der Lounge', gv * A['lounge_eur']))
    if p['spend'] and x.get('punkte_pro_100'): parts.append(('Punkte oder Meilen', p['spend'] * 12 / 100 * x['punkte_pro_100']))
    if p['vers'] and c.get('tier'): parts.append(('Reiseversicherung (statt eigener Jahrespolizze)', A['vers'][str(c['tier'])]))
    if p['subs']:
        for s in x.get('subs') or []: parts.append((s['name'], s['eur_month'] * 12))
    for e in x.get('extra') or []:
        if e.get('immer'): parts.append((e['name'], e['eur']))
    return sum(v for _, v in parts), parts

def need_visits(c, x, A, credits):
    """Wie viele Lounge-Besuche braucht es, bis die Karte die Jahresgebühr wieder hereinholt?"""
    base, _ = value(c, x, A, dict(credits=credits, lounge=0, guests=0, spend=1000, vers=True, subs=False))
    rest = (c['fee'] or 0) - base
    if rest <= 0: return 0
    n = math.ceil(rest / A['lounge_eur'])
    return n if n <= free_visits(x) else None

def verdict(c, x, A):
    fee = c['fee'] or 0
    cr = sum(g['eur'] for g in x.get('credits') or [])
    n1, n0 = need_visits(c, x, A, True), need_visits(c, x, A, False)
    s = []
    if cr: s.append(f'Die Guthaben sind zusammen {eur(cr)} € im Jahr wert' + (', mehr als die Jahresgebühr' if cr >= fee else f', die Jahresgebühr beträgt {eur(fee)} €') + '.')
    if n1 == 0: s.append('Nutzt du die Guthaben voll und brauchst ohnehin eine Reiseversicherung, hast du die Jahresgebühr schon ohne Lounge-Besuch wieder herein.')
    elif n1: s.append(f'Mit allen Guthaben, der Reiseversicherung und 1.000 € Umsatz im Monat lohnt sie sich ab etwa {n1} Lounge-Besuchen im Jahr.')
    if cr and n0 is not None and n0 != n1: s.append(f'Ohne die Guthaben brauchst du etwa {n0} Lounge-Besuche.' if n0 else 'Selbst ohne Guthaben reicht die Reiseversicherung mit den Punkten aus.')
    if n1 is None and n0 is None: s.append('Mit den enthaltenen Lounge-Besuchen allein holst du die Jahresgebühr nicht herein. Sie lohnt sich nur, wenn du Abos, Status oder Versicherung sehr gut nutzt.')
    return ' '.join(s)

def short(c, x, A):
    n1 = need_visits(c, x, A, True)
    if n1 == 0: return 'Lohnt sich schon, wenn du die Guthaben voll nutzt'
    if n1: return f'Lohnt sich ab etwa {n1} Lounge-Besuchen im Jahr' + (' mit allen Guthaben' if x.get('credits') else '')
    return 'Lohnt sich nur bei sehr intensiver Nutzung'

CSS_DONE = False
def calc_html(c, x, A):
    data = dict(fee=c['fee'] or 0, lounge=A['lounge_eur'], visits=None if free_visits(x) == math.inf else free_visits(x), guests=(x.get('lounge') or {}).get('guests_free') or 0,
                pp100=x.get('punkte_pro_100') or 0, vers=A['vers'].get(str(c.get('tier')), 0) if c.get('tier') else 0,
                credits=[dict(n=g['name'], v=g['eur']) for g in x.get('credits') or []], subs=[dict(n=s['name'], v=s['eur_month'] * 12) for s in x.get('subs') or []],
                welcome=(x.get('welcome') or {}).get('eur') or 0)
    cr = ''.join(f'<label class="lc"><input type="checkbox" data-credit="{i}" checked> {E(g["name"])} <b>{eur(g["eur"])} €</b></label>' for i, g in enumerate(x.get('credits') or []))
    sb = ''.join(f'<label class="lc"><input type="checkbox" data-sub="{i}"> {E(s["name"])} <b>{eur(s["eur_month"] * 12)} €</b></label>' for i, s in enumerate(x.get('subs') or []))
    wl = f'<label class="lc"><input type="checkbox" data-welcome> Willkommensbonus im ersten Jahr <b>{eur(data["welcome"])} €</b></label>' if data['welcome'] else ''
    return f'''<div class="box lcalc" data-lohnt='{html.escape(json.dumps(data), quote=True)}' hidden>
  <h2 style="margin-top:0">Rechne mit deinen Zahlen</h2>
  <div class="lgrid"><label>Lounge-Besuche im Jahr<input type="number" min="0" max="200" value="6" data-in="lounge"></label>
  <label>davon mit Begleitung<input type="number" min="0" max="200" value="0" data-in="guests"></label>
  <label>Kartenumsatz pro Monat (€)<input type="number" min="0" step="100" value="1000" data-in="spend"></label></div>
  {cr}{sb}{wl}
  <label class="lc"><input type="checkbox" data-vers checked> Ich bräuchte sonst eine eigene Reiseversicherung <b>{eur(data["vers"])} €</b></label>
  <div class="lres"><div><small>Wert deiner Vorteile</small><b data-out="val">–</b></div><div><small>Jahresgebühr</small><b>{eur(data["fee"])} €</b></div><div><small>Ergebnis pro Jahr</small><b data-out="net">–</b></div></div>
  <p class="note" data-out="txt"></p>
</div>'''

def card_page(land, c, x, A, P, prov):
    N = K.L['name']; rel = f'{land}/kreditkarten/bestenlisten/lohnt-sich/{c["slug"]}/'
    t = f'Ab wann lohnt sich die {c["titel"]}? ({land.upper()}) | Finvallo'
    if len(t) > 70: t = f'Lohnt sich die {c["titel"]}? | Finvallo'
    vt = verdict(c, x, A)
    d = f'Ab wann lohnt sich die {c["titel"]} in {N}? {short(c, x, A)}. Mit Rechner für deine Nutzung.'
    if len(d) > 156: d = d[:150].rsplit(' ', 1)[0] + ' …'
    rows = ''
    for g in x.get('credits') or []: rows += f'<tr><td>{E(g["name"])}</td><td class="nw">{eur(g["eur"])} €</td><td>{E(g.get("hinweis") or g.get("scope") or "")}</td></tr>'
    lg = x.get('lounge') or {}
    if lg.get('visits'): rows += f'<tr><td>Lounge-Besuche ({E(lg.get("program") or "")})</td><td class="nw">je ≈ {eur(A["lounge_eur"])} €</td><td>{"unbegrenzt" if lg["visits"] == "unbegrenzt" else str(lg["visits"]) + " pro Jahr"}{"; " + E(lg["hinweis"]) if lg.get("hinweis") else ""}</td></tr>'
    if x.get('punkte_pro_100'): rows += f'<tr><td>Punkte oder Meilen</td><td class="nw">{eur(x["punkte_pro_100"])} € je 100 € Umsatz</td><td>{E(x.get("punkte_hinweis") or "1 Punkt oder Meile = 1 Cent")}</td></tr>'
    if c.get('tier'): rows += f'<tr><td>Reiseversicherung ({E(K.TIER[c["tier"]][1])})</td><td class="nw">≈ {eur(A["vers"][str(c["tier"])])} €</td><td>so viel kostet eine vergleichbare eigene Jahrespolizze</td></tr>'
    for s in x.get('subs') or []: rows += f'<tr><td>{E(s["name"])}</td><td class="nw">{eur(s["eur_month"] * 12)} €</td><td>{eur(s["eur_month"])} € pro Monat, zählt nur, wenn du es sonst selbst zahlen würdest</td></tr>'
    for e in x.get('extra') or []: rows += f'<tr><td>{E(e["name"])}</td><td class="nw">{eur(e["eur"]) + " €" if e.get("eur") else "–"}</td><td>{E(e.get("hinweis") or "")}</td></tr>'
    if (x.get('welcome') or {}).get('text'): rows += f'<tr><td>Willkommensbonus</td><td class="nw">{eur(x["welcome"]["eur"]) + " €" if x["welcome"].get("eur") else "–"}</td><td>{E(x["welcome"]["text"])}, nur im ersten Jahr</td></tr>'
    prof = ''
    for pr in PROFILE:
        v, parts = value(c, x, A, pr['p']); net = v - (c['fee'] or 0)
        prof += f'<div class="lprof"><b>{E(pr["t"])}</b><small>{E(pr["d"])}</small><span class="{"good" if net >= 0 else "bad"}">{"+" if net >= 0 else "−"}{eur(round(abs(net)))} € pro Jahr</span></div>'
    fq = [(f'Ab wann lohnt sich die {c["titel"]}?', vt),
          ('Wie rechnet Finvallo?', f'Wir zählen nur Vorteile, die du wirklich nutzt: Guthaben zum Nennwert, einen Lounge-Besuch mit {eur(A["lounge_eur"])} €, Punkte und Meilen mit 1 Cent und die Reiseversicherung mit dem Preis einer vergleichbaren eigenen Jahrespolizze. Davon ziehen wir die Jahresgebühr ab.'),
          ('Zählt der Willkommensbonus mit?', 'Nur im ersten Jahr. Für die Frage, ob sich die Karte dauerhaft lohnt, rechnen wir ohne Bonus.')]
    ld = K.graph(rel, t, d, [(N, f'{land}/'), ('Kreditkarten', f'{land}/kreditkarten/'), ('Bestenlisten', f'{land}/kreditkarten/bestenlisten/'), ('Lohnt sich das?', f'{land}/kreditkarten/bestenlisten/lohnt-sich/'), (c['titel'], rel)],
                 [{"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}], date=x.get('geprueft') or c['geprueft'])
    src = ' · '.join(K.ext(u) for u in x.get('quellen') or [])
    body = f'''{K.HDR(P, rel)}
<div class="wrap"><main id="app">
<div class="crumb"><span><a href="../../">Bestenlisten</a> › <a href="../">Lohnt sich das?</a> › {E(c["titel"])}</span><span>Stand {K.dmy(x.get("geprueft") or c["geprueft"])}</span></div>
<h1>Ab wann lohnt sich die {E(c["titel"])}?</h1>
<p class="lede">Die Karte kostet {eur(c["fee"] or 0)} € im Jahr. Ob sich das rechnet, hängt davon ab, welche Vorteile du wirklich nutzt.</p>
<section class="facts box glance" aria-label="Kurzantwort"><h2 style="margin-top:0">Kurzantwort</h2><div class="prose"><p>{E(vt)}</p></div></section>
<h2>Was die Vorteile wert sind</h2><div class="tbl wide blt"><table><thead><tr><th>Vorteil</th><th>Wert pro Jahr</th><th>Hinweis</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>Drei typische Fälle</h2><div class="lprofs">{prof}</div>
{calc_html(c, x, A)}
<h2>Fragen und Antworten</h2><div class="faq">{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in fq)}</div>
<p class="note" style="margin-top:18px"><a class="lnk" href="../../../{c["slug"]}/">Alle Konditionen der {E(c["titel"])} →</a> · <a class="lnk" href="../">Andere Premiumkarten vergleichen →</a></p>
{f'<p class="src">Quellen: {src}</p>' if src else ''}
</main>
{K.footer(P)}'''
    K.write(rel, K.head(t, d, rel, P, ld) + body.replace('</body>', script(P) + '\n</body>'))
    return rel

def script(P):
    import hashlib
    v = hashlib.sha256(open(R + 'assets/lohnt.js', 'rb').read()).hexdigest()[:8]
    return f'<script src="{P}assets/lohnt.js?v={v}" defer></script>'

def winners(land, cards, X, A):
    out = []
    for pr in PROFILE:
        best = None
        for c in cards:
            x = X[c['slug']]; v, _ = value(c, x, A, pr['p']); net = v - (c['fee'] or 0)
            if best is None or net > best[1]: best = (c, net)
        out.append((pr, best))
    return out

def hub(land, cards, X, A, P):
    N = K.L['name']; rel = f'{land}/kreditkarten/bestenlisten/lohnt-sich/'
    t = f'Lohnt sich eine Premium-Kreditkarte? {N} 2026 | Finvallo'
    d = f'Ab wann sich Premium-Kreditkarten in {N} lohnen: Guthaben, Lounges, Versicherung und Punkte gegen die Jahresgebühr gerechnet. Mit Rechner.'
    tiles = ''.join(f'<a class="catcard" href="{c["slug"]}/"><span class="ct">{eur(c["fee"] or 0)} € im Jahr</span><b>{E(c["titel"])}</b><span>{E(short(c, X[c["slug"]], A))}</span><small>Rechnung ansehen →</small></a>'
                    for c in sorted(cards, key=lambda c: c['fee'] or 0))
    win = ''.join(f'<div class="lprof"><b>{E(pr["t"])}</b><small>{E(pr["d"])}</small><span>Am meisten bringt die <a class="lnk" href="{b[0]["slug"]}/">{E(b[0]["titel"])}</a>: {"+" if b[1] >= 0 else "−"}{eur(round(abs(b[1])))} € pro Jahr</span></div>' for pr, b in winners(land, cards, X, A))
    fq = [('Lohnt sich eine Premium-Kreditkarte?', 'Nur, wenn du die enthaltenen Vorteile wirklich nutzt. Wir rechnen Guthaben, Lounge-Besuche, Punkte und Reiseversicherung gegen die Jahresgebühr. Für die meisten Menschen ohne viele Flugreisen ist eine kostenlose Karte günstiger.'),
          ('Wie viel ist ein Lounge-Besuch wert?', f'Wir rechnen mit {eur(A["lounge_eur"])} € pro Besuch. {A.get("lounge_quelle", "")}'.strip())]
    ld = K.graph(rel, t, d, [(N, f'{land}/'), ('Kreditkarten', f'{land}/kreditkarten/'), ('Bestenlisten', f'{land}/kreditkarten/bestenlisten/'), ('Lohnt sich das?', rel)],
                 [{"@type": "ItemList", "name": f"Premium-Kreditkarten {N}: ab wann sie sich lohnen", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": c['titel'], "url": f"https://finvallo.com/{rel}{c['slug']}/"} for i, c in enumerate(cards)]},
                  {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}])
    other = f'{"de" if land == "at" else "at"}/kreditkarten/bestenlisten/lohnt-sich/'
    body = f'''{K.HDR(P, rel, other)}
<div class="wrap"><main id="app">
<div class="crumb"><span><a href="../">Bestenlisten</a> › Lohnt sich das?</span><span>Stand {K.dmy(K.L["stand"])}</span></div>
<h1>Ab wann lohnt sich eine Premium-Kreditkarte?</h1>
<p class="lede">Premiumkarten kosten viel, bringen aber Guthaben, Lounges und Versicherungen mit. Wir rechnen für jede Karte aus, ab welcher Nutzung sich die Jahresgebühr bezahlt macht.</p>
<h2>Top-Karten, je nachdem wie du sie nutzt</h2><div class="lprofs">{win}</div>
<h2>Alle Premiumkarten in {N}</h2><div class="catgrid">{tiles}</div>
<h2>So rechnen wir</h2><div class="prose"><p>Guthaben zählen mit ihrem Nennwert, aber nur, wenn du sie auch einlöst. Ein Lounge-Besuch zählt mit {eur(A["lounge_eur"])} €. Punkte und Meilen zählen mit 1 Cent. Die Reiseversicherung zählt mit dem Preis einer vergleichbaren eigenen Jahrespolizze: {", ".join(f"{K.TIER[int(k)][1]} {eur(v)} €" for k, v in A["vers"].items() if int(k) > 0)}. Abos zählen nur, wenn du sie sonst selbst bezahlen würdest. Willkommensboni gelten nur im ersten Jahr und bleiben deshalb außen vor.</p></div>
<h2>Fragen und Antworten</h2><div class="faq">{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in fq)}</div>
</main>
{K.footer(P)}'''
    K.write(rel, K.head(t, d, rel, P, ld, alt=K.alt_links(rel.replace(land + '/', 'at/', 1), rel.replace(land + '/', 'de/', 1)) if load('de' if land == 'at' else 'at') else None) + body)
    return rel

def top_block(land, cards, X, A):
    win = ''.join(f'<a class="catcard" href="lohnt-sich/{b[0]["slug"]}/"><span class="ct">{E(pr["t"])}</span><b>{E(b[0]["titel"])}</b><span>{"+" if b[1] >= 0 else "−"}{eur(round(abs(b[1])))} € pro Jahr nach Jahresgebühr</span><small>Rechnung ansehen →</small></a>' for pr, b in winners(land, cards, X, A))
    return (f'<!--lohnt--><h2>Top-Karten, je nachdem wie du sie nutzt</h2><p class="note" style="margin-top:-6px">Premiumkarten lohnen sich erst ab einer bestimmten Nutzung. '
            f'<a class="lnk" href="lohnt-sich/">Ab wann lohnt sich welche Karte? →</a></p><div class="catgrid">{win}</div><h2>Bestenlisten nach Kategorie</h2><!--/lohnt-->')

def main():
    DATA = K.prepare()
    pages = []; lines = {}
    for land in ('at', 'de'):
        D = load(land)
        if not D: continue
        K.use(land); A = D['annahmen']
        bys = {c['slug']: c for c in DATA[land][0]}
        X = {x['slug']: x for x in D['karten'] if x['slug'] in bys}
        cards = [bys[s] for s in X]
        base = R + f'{land}/kreditkarten/bestenlisten/lohnt-sich/'
        if os.path.isdir(base):
            import shutil
            for d in os.listdir(base):
                if os.path.isdir(base + d) and d not in X: shutil.rmtree(base + d)
        pages.append(hub(land, cards, X, A, '../../../../'))
        for c in cards: pages.append(card_page(land, c, X[c['slug']], A, '../../../../../', DATA[land][1]))
        f = R + f'{land}/kreditkarten/bestenlisten/index.html'; s = open(f).read()
        s = re.sub(r'<!--lohnt-->.*?<!--/lohnt-->', '', s, flags=re.S)
        s = s.replace('<div class="catgrid">', top_block(land, cards, X, A) + '<div class="catgrid">', 1)
        open(f, 'w').write(s)
        lines[land] = [f'- [Ab wann lohnt sich die {c["titel"]}?](https://finvallo.com/{land}/kreditkarten/bestenlisten/lohnt-sich/{c["slug"]}/): {verdict(c, X[c["slug"]], A)}' for c in cards]
    # Sitemap
    p = R + 'sitemap.xml'; s = open(p).read()
    s = re.sub(r'<url><loc>https://finvallo\.com/(?:at|de)/kreditkarten/bestenlisten/lohnt-sich/[^<]*</loc>.*?</url>\n?', '', s)
    s = s.replace('</urlset>', ''.join(f'<url><loc>https://finvallo.com/{u}</loc><lastmod>{K.LANDS[u[:2]]["stand"]}</lastmod><changefreq>weekly</changefreq><priority>0.7</priority></url>\n' for u in pages) + '</urlset>')
    open(p, 'w').write(s)
    # llms
    for fn in ('llms.txt', 'llms-full.txt'):
        p = R + fn; s = open(p).read()
        s = re.sub(r'\n## (?:Österreich|Deutschland): Ab wann lohnt sich eine Premiumkarte\?\n(?:- .*\n?)*', '\n', s)
        add = ''.join(f'\n## {K.LANDS[l]["name"]}: Ab wann lohnt sich eine Premiumkarte?\n' + '\n'.join(v) + '\n' for l, v in lines.items())
        j = s.find('\n## Finanzrechner'); s = s[:j] + add + s[j:] if j >= 0 else s + add
        open(p, 'w').write(re.sub(r'\n{3,}', '\n\n', s))
    print('Lohnt-sich-Seiten:', len(pages))

if __name__ == '__main__': main()
