"""„Persönlich rechnen“ auf der Kartenliste und der Kreditkarten-Rechner (AT und DE).

Daten je Karte: Gebühren und Versicherung aus karten.py, Cashback/Punkte/Lounge aus daten/<land>/ertrag.json,
Premiumkarten (Guthaben, Abos, Lounge, Punkte) aus daten/<land>/lohnt.json.
`rechnen.py seite` schreibt <land>/kreditkarten/rechner/ (läuft nach lohnt.py, vor header.py).
`rechnen.py` setzt den Rechner über den Filter der Kartenliste und einen Ergebnis-Platz in jede Karte (läuft nach listui.py).
Rechenlogik für beide: public/assets/rechnen.js. Idempotent.
"""
import hashlib, html, json, math, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import karten as K
import lohnt as LO
from score import eur

R = K.R; SP = K.SP; E = K.E

def load(p):
    return json.load(open(p)) if os.path.exists(p) else {}

def lim(v): return None if v in (None, 'unbegrenzt', math.inf) else v

def card_data(land, cards):
    ER = load(SP + f'/daten/{land}/ertrag.json').get('karten', {})
    LD = LO.load(land) or {'annahmen': {}, 'karten': []}
    A = LD['annahmen']; LX = {x['slug']: x for x in LD['karten']}
    out = {}; prov = {'cr': [], 'sb': []}
    for c in cards:
        e = ER.get(c['slug'], {}); x = LX.get(c['slug'])
        d = dict(fee=c.get('fee'), fx=c.get('fx'), cash=c.get('cash'), effz=c.get('effz'), tier=c.get('tier') or 0)
        if c.get('fee1') is not None and c.get('fee1') != c.get('fee'): d['fee1'] = c['fee1']
        if c.get('cashAus'): d['cashA'] = c['cashAus']
        if c.get('cashFx'): d['cfx'] = c['cashFx']
        if x:
            d['pct'] = x.get('punkte_pro_100') or 0
            if x.get('punkte_max'): d['cap'] = x['punkte_max']
            if x.get('punkte_hinweis'): d['ph'] = x['punkte_hinweis']
            d['fix'] = [[g['name'], g['eur']] for g in x.get('extra') or [] if g.get('immer')]
            if (x.get('welcome') or {}).get('eur'): d['wel'] = [x['welcome']['eur'], x['welcome'].get('text') or '']
            cr = sum(g['eur'] for g in x.get('credits') or [])
            sb = sum(g['eur'] for g in LO.priced(x, A))
            if cr: d['cr'] = round(cr, 2); prov['cr'].append(LO.tag(c))
            if sb: d['sb'] = round(sb, 2); prov['sb'].append(LO.tag(c))
            lg = x.get('lounge')
        else:
            for k in ('pct', 'cap', 'kosten', 'anteil'):
                if e.get(k) is not None: d[k] = e[k]
            if e.get('fx_only'): d['fxo'] = 1
            if e.get('hinweis'): d['ph'] = e['hinweis']
            lg = e.get('lounge')
        if lg and lg.get('visits'):
            d['lg'] = dict(v=lim(lg['visits']), g=lim(lg.get('guests_free') or 0), w=1 if lg.get('scope') == 'wien' else 0, m=lg.get('min_umsatz') or 0)
        out[c['slug']] = d
    tags = {k: ', '.join(dict.fromkeys(v)) for k, v in prov.items()}
    return dict(cards=out, lounge=A.get('lounge_eur', 30), vers=A.get('vers', {}), tiers={str(k): K.TIER[k][1] for k in range(1, 5)}), tags

def box(land, tags, wien, page=False):
    sel = '<option value="0">nicht nötig</option>' + ''.join(f'<option value="{k}">{E(K.TIER[k][1])}</option>' for k in range(1, 5))
    lounge = ('<label>Lounge Wien pro Jahr<input type="number" min="0" max="200" value="0" data-r="wien"></label><label>Lounge Ausland pro Jahr<input type="number" min="0" max="200" value="0" data-r="lounge"></label>'
              if wien else '<label>Lounge-Besuche pro Jahr<input type="number" min="0" max="200" value="0" data-r="lounge"></label>')
    cb = ''
    if tags.get('cr'): cb += f'<label class="lc"><input type="checkbox" data-r="cr"><span>Guthaben der Karte voll nutzen <span class="mut">(nur {E(tags["cr"])})</span></span></label>'
    if tags.get('sb'): cb += f'<label class="lc"><input type="checkbox" data-r="sb"><span>Partner-Abos nutzen, die du sonst selbst zahlen würdest <span class="mut">(nur {E(tags["sb"])})</span></span></label>'
    cb += '<label class="lc"><input type="checkbox" data-r="wel"><span>Willkommensbonus mitrechnen <span class="mut">(nur im 1. Jahr)</span></span></label>'
    filt = ('<div class="lgrid rfilt"><label>Kartenart<select data-f="typ"><option value="">Alle Kartenarten</option><option value="Kreditkarte">Kreditkarte mit Teilzahlung</option><option value="Charge">Charge-Karte</option><option value="Debit">Debitkarte</option><option value="Prepaid">Prepaid-Karte</option></select></label>'
            '<label>Kartennetzwerk<select data-f="netz"><option value="">Alle Kartennetzwerke</option><option value="visa">Visa</option><option value="mastercard">Mastercard</option><option value="american express">American Express</option><option value="diners">Diners Club</option></select></label>'
            '<label>Jahresgebühr<select data-f="fee"><option value="">egal</option><option value="0">nur ohne Jahresgebühr</option><option value="100">bis 100 €</option><option value="300">bis 300 €</option></select></label></div>') if page else ''
    head = ('<h2 style="margin:0 0 4px">Deine Nutzung</h2><p class="note" style="margin:0 0 12px">Die Liste unten rechnet bei jeder Änderung sofort neu.</p>' if page else
            '<summary><b>Persönlich rechnen</b><span>Was bringt dir jede Karte im Jahr? Trag deine Nutzung ein.</span></summary>')
    tag, cls = ('div', 'box lcalc rbox rpage') if page else ('details', 'box lcalc rbox')
    return f'''<!--rechnen--><{tag} class="{cls}" id="rbox"{' data-page="1"' if page else ''} hidden>
    {head}
    <div class="lgrid"><label>Umsatz pro Monat (€)<input type="number" min="0" step="100" value="1000" data-r="spend"></label>
    <label>davon in Fremdwährung pro Jahr (€)<input type="number" min="0" step="100" value="1000" data-r="fxs"></label>
    <label>Welches Jahr?<select data-r="jahr"><option value="0">Folgejahre (Normalpreis)</option><option value="1">1. Jahr (mit Aktion)</option></select></label>
    <label>Bargeld Inland: Abhebungen pro Jahr<input type="number" min="0" max="300" value="0" data-r="cin"></label>
    <label>Bargeld Ausland: Abhebungen pro Jahr<input type="number" min="0" max="300" value="0" data-r="cn"></label>
    <label>Betrag je Abhebung (€)<input type="number" min="0" step="50" value="200" data-r="ca"></label>
    {lounge}<label>davon mit Begleitung<input type="number" min="0" max="200" value="0" data-r="guests"></label>
    <label>Reiseversicherung<select data-r="vers">{sel}</select></label></div>
    <div class="lchecks">{cb}</div>
    {filt}
    <p class="note" style="margin:0">Wir rechnen Punkte und Meilen mit 1 Cent, Hotelpunkte mit 0,4 Cent, einen Lounge-Besuch mit 30 € und die Reiseversicherung mit dem Preis einer eigenen Jahrespolizze. Fremdwährung heißt: Zahlungen und Abhebungen außerhalb des Euroraums. Unter jeder Karte siehst du, wie das Ergebnis zustande kommt.</p>
  </{tag}><!--/rechnen-->
  '''

def page(land, cards, D, tags):
    """Kreditkarten-Rechner: alle Karten nach deinem Ergebnis, mit Rechnung und Vergleich."""
    K.use(land); N = K.L['name']; rel = f'{land}/kreditkarten/rechner/'; P = '../../../'
    wien = any((d.get('lg') or {}).get('w') for d in D['cards'].values())
    t = f'Kreditkarten-Rechner {N}: Was kostet und bringt deine Karte? | Finvallo'
    d = f'Kreditkarten-Rechner {N}: {len(cards)} Karten mit Jahresgebühr, Auslandsgebühr, Bargeld, Cashback, Lounge und Versicherung für deine Nutzung durchgerechnet.'
    if len(d) > 158: d = d[:150].rsplit(' ', 1)[0] + ' …'
    def item(c):
        st = f'<div class="stats"><div><small>Jahresgebühr</small><b>{"0 €" if c.get("fee") == 0 else (eur(c["fee"]) + " €") if c.get("fee") is not None else "–"}</b></div><div><small>Ausland</small><b>{E(K.k_fx(c))}</b></div><div><small>Bargeld</small><b>{E(K.k_cash(c))}</b></div></div>'
        return (f'<article class="item ritem" data-typ="{c.get("typ") or ""}" data-netz="{E((c.get("netz") or "").lower())}" data-fee="{c["fee"] if c.get("fee") is not None else 99999}">'
                f'<div class="rhead"><span class="rk" data-rank></span><div style="min-width:0"><h3 class="iname"><a href="../{c["slug"]}/">{E(c["titel"])}</a></h3><div class="iprov">{E(c["anbieter"])}</div></div>'
                f'<label class="rcmpl"><input type="checkbox" data-cmp> Vergleichen</label></div>{st}<div class="ires" data-res hidden></div></article>')
    fq = [('Wie rechnet der Kreditkarten-Rechner?', 'Er zählt, was dir die Karte im Jahr bringt (Cashback, Punkte und Meilen, Lounge-Besuche, Reiseversicherung, Guthaben und Abos, die du wirklich nutzt) und zieht ab, was sie kostet (Jahresgebühr, Gebühren für Zahlungen in Fremdwährung und für Bargeld). Unter jeder Karte steht die ganze Rechnung.'),
          ('Was ist mit Fremdwährung gemeint?', 'Zahlungen und Abhebungen in einer anderen Währung als Euro, zum Beispiel im Urlaub außerhalb des Euroraums oder in Online-Shops, die in Dollar oder Pfund abrechnen. Im Euroraum fällt keine Fremdwährungsgebühr an.'),
          ('Warum stehen manche Karten weiter hinten, obwohl das Ergebnis gut ist?', 'Wenn für eine Karte eine Gebühr nicht bekannt ist oder ihre Reiseversicherung schwächer ist als die gewünschte, steht sie hinter den Karten mit vollständiger Rechnung. Das ist an der Karte gekennzeichnet.'),
          ('Zählt der Willkommensbonus?', 'Nur, wenn du ihn anhakst. Er gilt meistens nur im ersten Jahr. Für die Frage, ob sich eine Karte dauerhaft lohnt, rechne mit den Folgejahren.')]
    ld = K.graph(rel, t, d, [(N, f'{land}/'), ('Kreditkarten', f'{land}/kreditkarten/'), ('Rechner', rel)],
                 [{"@type": "WebApplication", "name": f"Kreditkarten-Rechner {N}", "applicationCategory": "FinanceApplication", "operatingSystem": "Web", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}},
                  {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}])
    other = ('de' if land == 'at' else 'at') + '/kreditkarten/rechner/'
    v = hashlib.sha256(open(R + 'assets/rechnen.js', 'rb').read()).hexdigest()[:8]
    body = f'''{K.HDR(P, rel, other)}
<div class="wrap"><main id="app">
<div class="crumb"><span><a href="../../">{N}</a> › <a href="../">Kreditkarten</a> › Rechner</span><span>Stand {K.dmy(K.L["stand"])}</span></div>
<h1>Kreditkarten-Rechner {N}</h1>
<p class="lede">Trag ein, wie du deine Karte nutzt. Der Rechner zeigt dir für alle {len(cards)} Karten, was sie dir im Jahr bringen oder kosten, mit allen Gebühren, Cashback, Lounges und Versicherung. Hake bis zu vier Karten an, um sie direkt zu vergleichen.</p>
{box(land, tags, wien, page=True)}
<div class="rcmpbar" id="rcmpbar" hidden><span data-cmpn></span><button type="button" class="btn primary" data-cmpgo>Vergleichen</button><button type="button" class="lnk" data-cmpclr>Auswahl löschen</button></div>
<div class="box rcmp" id="rcmp" hidden></div>
<div class="fbot" style="margin:6px 0 10px"><b data-rcount>{len(cards)} Karten</b><span class="mut">sortiert nach deinem Ergebnis</span></div>
<div id="rlist" class="rlist">{"".join(item(c) for c in cards)}</div>
<h2>So rechnen wir</h2><div class="prose"><p>Cashback, Punkte und Meilen zählen mit ihrem Wert in Euro: ein Punkt oder eine Meile mit 1 Cent, Hotelpunkte mit 0,4 Cent, jeweils bis zur Obergrenze der Karte. Ein Bonusprogramm mit Teilnahmegebühr zählt nur, wenn es sich bei deinem Umsatz lohnt. Ein Lounge-Besuch zählt mit 30 €, die Reiseversicherung mit dem Preis einer eigenen Jahrespolizze in der gewünschten Stufe. Davon ziehen wir die Jahresgebühr, die Gebühr auf Zahlungen in Fremdwährung und die Kosten für Bargeld ab. Bei Kreditkarten ohne Automatengebühr rechnen wir einen Monat Zinsen auf das abgehobene Geld.</p></div>
<h2>Fragen und Antworten</h2><div class="faq">{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in fq)}</div>
<p class="note" style="margin-top:18px"><a class="lnk" href="../">Alle Kreditkarten im Vergleich →</a> · <a class="lnk" href="../bestenlisten/lohnt-sich/">Premiumkarten: ab wann sie sich lohnen →</a></p>
</main>
{K.footer(P)}'''
    body = body.replace('</body>', f'<script type="application/json" id="rdata">{json.dumps(D, ensure_ascii=False).replace("</", "<\\/")}</script>\n<script src="{P}assets/rechnen.js?v={v}" defer></script>\n</body>', 1)
    K.write(rel, K.head(t, d, rel, P, ld, alt=K.alt_links('at/kreditkarten/rechner/', 'de/kreditkarten/rechner/')) + body)

def list_cards(land, DATA):
    s = open(R + f'{land}/kreditkarten/index.html', encoding='utf-8').read()
    slugs = re.findall(r'<h3 class="iname"><a href="(?:[^"]*/)?([^"/]+)/">', s)
    bys = {c['slug']: c for c in DATA[land][0]}
    return [bys[x] for x in dict.fromkeys(slugs) if x in bys]

def pages():
    DATA = K.prepare()
    for land in ('at', 'de'):
        cards = list_cards(land, DATA)
        D, tags = card_data(land, cards)
        page(land, cards, D, tags)
        print('Rechner-Seite', land, len(cards), 'Karten')

def main():
    DATA = K.prepare()
    v = hashlib.sha256(open(R + 'assets/rechnen.js', 'rb').read()).hexdigest()[:8]
    for land in ('at', 'de'):
        K.use(land)
        f = R + f'{land}/kreditkarten/index.html'; s = open(f, encoding='utf-8').read()
        s = re.sub(r'<!--rechnen-->.*?<!--/rechnen-->\n?\s*', '', s, flags=re.S)
        s = re.sub(r'<div class="ires" data-res hidden></div>', '', s)
        s = re.sub(r'<script type="application/json" id="rdata">.*?</script>\n?', '', s, flags=re.S)
        s = re.sub(r'<script src="[^"]*assets/rechnen\.js[^"]*" defer></script>\n?', '', s)
        cards = list_cards(land, DATA)
        D, tags = card_data(land, cards)
        wien = any((d.get('lg') or {}).get('w') for d in D['cards'].values())
        s = s.replace('<div class="box filt" id="filt"', box(land, tags, wien) + '<div class="box filt" id="filt"', 1)
        s = re.sub(r'(<div class="stats">.*?</div></div>)', r'\1<div class="ires" data-res hidden></div>', s, flags=re.S)
        s = s.replace('</body>', f'<script type="application/json" id="rdata">{json.dumps(D, ensure_ascii=False).replace("</", "<\\/")}</script>\n<script src="../../assets/rechnen.js?v={v}" defer></script>\n</body>', 1)
        open(f, 'w', encoding='utf-8').write(s)
        print('Rechnen', land, len(cards), 'Karten', s.count('data-res hidden'))

if __name__ == '__main__': pages() if sys.argv[1:] == ['seite'] else main()
