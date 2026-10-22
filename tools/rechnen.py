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
import sammeln as SM
from score import eur

R = K.R; SP = K.SP; E = K.E

def load(p):
    return json.load(open(p)) if os.path.exists(p) else {}

def lim(v): return None if v in (None, 'unbegrenzt', math.inf) else v

CASHRULES = load(SP + '/daten/bargeld-regeln.json').get('regeln', {})
ESIM = load(SP + '/daten/esim.json')

def card_data(land, cards):
    ER = load(SP + f'/daten/{land}/ertrag.json').get('karten', {})
    LD = LO.load(land) or {'annahmen': {}, 'karten': []}
    A = LD['annahmen']; LX = {x['slug']: x for x in LD['karten']}
    out = {}; prov = {'cr': [], 'sb': []}
    for c in cards:
        e = ER.get(c['slug'], {}); x = LX.get(c['slug'])
        d = dict(fee=c.get('fee'), fx=c.get('fx'), cash=c.get('cash'), effz=c.get('effz'), tier=c.get('tier') or 0)
        if c.get('fee1') is not None and c.get('fee1') != c.get('fee'): d['fee1'] = c['fee1']
        if c.get('feeMonat'): d['fm'] = c['feeMonat']
        if c.get('cashAus'): d['cashA'] = c['cashAus']
        if c.get('cashText') and (c.get('cash') or [''])[0] == 'freeN': d['ct'] = re.sub(r'\s*\(.*?\)', '', c['cashText']).split(';')[0][:90]
        if c.get('cashFx'): d['cfx'] = c['cashFx']
        # Bargeldregel je Monat (Anzahl, Betrag, Mindestbetrag); freeN automatisch
        rg = CASHRULES.get(f'{land}/{c["slug"]}')
        if rg is None and (c.get('cash') or [''])[0] == 'freeN': rg = {'n': c['cash'][1], 'on': {'fix': c['cash'][2]}}
        if rg is not None: d['cx'] = rg
        if (c.get('cash') or [''])[0] == 'free_interest': d['soll'] = c.get('soll') or (round(1200 * ((1 + c['effz'] / 100) ** (1 / 12) - 1), 2) if c.get('effz') else None)
        if x:
            d['pct'] = x.get('punkte_pro_100') or 0
            if x.get('punkte_max'): d['cap'] = x['punkte_max']
            if x.get('punkte_hinweis'): d['ph'] = x['punkte_hinweis']
            d['fix'] = [[g['name'], g['eur']] for g in x.get('extra') or [] if g.get('immer')]
            if (x.get('welcome') or {}).get('eur'): d['wel'] = [x['welcome']['eur'], x['welcome'].get('text') or '']
            cr = sum(g['eur'] for g in x.get('credits') or [] if not g.get('ausland'))
            crx = sum(g['eur'] for g in x.get('credits') or [] if g.get('ausland'))
            if cr: d['crn'] = ', '.join(g['name'] for g in x.get('credits') or [] if not g.get('ausland'))
            if crx: d['crx'] = round(crx, 2); prov.setdefault('crx', []).append(crx)
            tr = LO.tiers(x, A); sb = tr['alle']
            if cr: d['cr'] = round(cr, 2); prov['cr'].append(c['titel'].replace('American Express', 'Amex') + ': ' + ', '.join(f"{g.get('kurz') or g['name']} {eur(g['eur'])} €" for g in x.get('credits') or [] if not g.get('ausland')))
            if sb:
                d['sb'] = round(sb, 2); prov['sb'].append(LO.tag(c))
                few = [g['name'] for g in tr['few']]
                if few: d['sbl'] = tr['few_eur']; d['sbn'] = ', '.join(few); prov.setdefault('sbn', []).append(f"{c['titel']}: {', '.join(few)}")
            if tr['y1']: d['sy1'] = [tr['y1_eur'], ', '.join(g['name'] for g in tr['y1'])]; prov.setdefault('sy1', []).append(', '.join(g['name'] for g in tr['y1']))
            lg = x.get('lounge')
        else:
            for k in ('pct', 'cap', 'kosten', 'anteil'):
                if e.get(k) is not None: d[k] = e[k]
            if e.get('fx_only'): d['fxo'] = 1
            if e.get('hinweis'): d['ph'] = e['hinweis']
            lg = e.get('lounge')
        if lg and lg.get('visits'):
            d['lg'] = dict(v=lim(lg['visits']), g=lim(lg.get('guests_free') or 0), w=1 if lg.get('scope') == 'wien' else 0, m=lg.get('min_umsatz') or 0)
        # Art des Ertrags: echtes Cashback bleibt fix, Punkte und Meilen hängen vom gewählten Punktewert ab
        if d.get('pct'):
            v = SM.value(land, c['titel'])
            kind = SM.kind(v[1]) if v else ('cash' if re.search(r'cashback|saveback|gutschrift|coins|guthaben', ((e.get('art') or '') + ' ' + ((x or {}).get('punkte_hinweis') or '')), re.I) else 'points')
            if kind != 'cash':
                d['pk'] = 1
                pv = SM.pv_of(land, c['titel']) if v else SM.PV
                if pv != SM.PV: d['pv'] = pv
                # lohnt.json nennt den Punktewert schon in € pro 100 € Umsatz: zurück auf Punkte pro 100 €, der Rechner multipliziert mit dem Punktewert
                if x and x.get('punkte_pro_100'):
                    d['pct'] = round(x['punkte_pro_100'] / pv, 4)
                    if d.get('cap'): d['cap'] = round(d['cap'] / pv, 2)
        es = (ESIM.get('karten') or {}).get(f"{land}/{c['slug']}")
        if es: d['esim'] = [es['gb'], ESIM['eur_pro_gb']]; prov.setdefault('esim', []).append(c['titel'])
        out[c['slug']] = d
    tags = {k: ('; ' if k in ('cr', 'sbn') else ', ').join(dict.fromkeys(v)) for k, v in prov.items() if k != 'crx'}
    if prov.get('crx'): tags['crx'] = max(prov['crx'])
    return dict(cards=out, lounge=A.get('lounge_eur', 30), vers=A.get('vers', {}), tiers={str(k): K.TIER[k][1] for k in range(1, 5)}, polizze=K.t('polizze', land)), tags

def box(land, tags, wien, page=False):
    sel = '<option value="0">nicht nötig</option>' + ''.join(f'<option value="{k}">{E(K.TIER[k][1])}</option>' for k in range(1, 5))
    lounge = ('<label><span class="flab">Lounge Wien pro Jahr</span><input type="number" min="0" max="200" value="0" data-r="wien" name="wien"></label><label><span class="flab">Lounge Ausland pro Jahr</span><input type="number" min="0" max="200" value="0" data-r="lounge" name="lounge"></label>'
              '<label><span class="flab">davon mit Begleitung</span><input type="number" min="0" max="200" value="0" data-r="guests" name="guests"></label>'
              if wien else '<label><span class="flab">Lounge-Besuche pro Jahr</span><input type="number" min="0" max="200" value="0" data-r="lounge" name="lounge"></label><label><span class="flab">davon mit Begleitung</span><input type="number" min="0" max="200" value="0" data-r="guests" name="guests"></label>')
    cb = ''
    if tags.get('cr'):
        x = f'; weitere {eur(tags["crx"])} € Gourmet-Guthaben im Ausland, nicht gerechnet' if tags.get('crx') else ''
        cb += f'<label class="lc"><input type="checkbox" data-r="cr" name="cr"><span>Guthaben der Karte nutzen <span class="mut">({E(tags["cr"])}{x})</span></span></label>'
    if tags.get('sb'):
        cb += (f'<label class="lc"><input type="checkbox" data-r="sbl" name="sbl"><span>Einige Partner-Abos nutzen <span class="mut">(nur {E(tags["sb"])}; gerechnet nur die bekanntesten Alltags-Abos, die du sonst selbst zahlen würdest: {E(tags.get("sbn", ""))})</span></span></label>'
               f'<label class="lc"><input type="checkbox" data-r="sb" name="sb"><span>Viele Partner-Abos nutzen <span class="mut">(gerechnet mit {int(LO.NUTZUNG * 100)} % des Werts aller Abos der Karte; ersetzt die Auswahl oben)</span></span></label>')
    if tags.get('esim'): cb += f'<label class="lc"><input type="checkbox" data-r="esim" name="esim"><span>eSIM-Daten bei Reisen außerhalb der EU nutzen <span class="mut">(nur {E(tags["esim"])}; gerechnet für deine Reisemonate, zum Revolut-Preis ab {eur(ESIM["eur_pro_gb"])} € pro GB; in der EU kostet Roaming nichts extra)</span></span></label>'
    cb += '<label class="lc"><input type="checkbox" data-r="wel" name="wel"><span>Erstes Jahr rechnen <span class="mut">(mit Willkommensbonus und Aktionspreis' + (f'; dazu Abos, die nur 12 Monate inklusive sind: {E(tags["sy1"])}' if tags.get('sy1') else '') + ')</span></span></label>'
    filt = ('<div class="lgrid rfilt"><label><span class="flab">Kartenart</span><select data-f="typ" name="typ"><option value="" selected>Alle Kartenarten</option><option value="Kreditkarte">Kreditkarte mit Teilzahlung</option><option value="Charge">Charge-Karte</option><option value="Debit">Debitkarte</option><option value="Prepaid">Prepaid-Karte</option></select></label>'
            '<label><span class="flab">Kartennetzwerk</span><select data-f="netz" name="netz"><option value="" selected>Alle Kartennetzwerke</option><option value="visa">Visa</option><option value="mastercard">Mastercard</option><option value="american express">American Express</option><option value="diners">Diners Club</option></select></label>'
            '<label><span class="flab">Jahresgebühr</span><select data-f="fee" name="fee"><option value="" selected>egal</option><option value="0">nur ohne Jahresgebühr</option><option value="100">bis 100 €</option><option value="300">bis 300 €</option></select></label></div>') if page else ''
    head = ('<h2 style="margin:0 0 4px">Deine Nutzung</h2><p class="note" style="margin:0 0 12px">Die Liste unten rechnet bei jeder Änderung sofort neu.</p>' if page else
            '<summary><b>Welche Karte ist die beste für dich?</b><span>Trag ein, wie viel du mit Karte zahlst, wie oft du reist und Bargeld abhebst. Wir rechnen für jede Karte aus, was sie dir im Jahr bringt, und sortieren die beste für dich nach oben.</span><em class="rgo">Jetzt für dich rechnen</em></summary>')
    tag, cls = ('form', 'box lcalc rbox rpage') if page else ('details', 'box lcalc rbox')
    return f'''<!--rechnen--><{tag} class="{cls}" id="rbox"{' data-page="1" onsubmit="return false"' if page else ' hidden'}>
    {head}
    <div class="lgrid two"><label><span class="flab">Umsatz pro Monat (€)</span><input type="number" min="0" step="100" value="1000" data-r="spend" name="spend"></label>
    <label><span class="flab">Fremdwährung pro Jahr (€)</span><input type="number" min="0" step="100" value="1200" data-r="fxs" name="fxs"></label>
    <label><span class="flab">Bargeld Inland: Anzahl pro Jahr</span><input type="number" min="0" max="300" value="2" data-r="cin" name="cin"></label>
    <label><span class="flab">Betrag je Abhebung Inland (€)</span><input type="number" min="0" step="50" value="200" data-r="cia" name="cia"></label>
    <label><span class="flab">Bargeld Ausland: Anzahl pro Jahr</span><input type="number" min="0" max="300" value="0" data-r="cn" name="cn"></label>
    <label><span class="flab">Betrag je Abhebung Ausland (€)</span><input type="number" min="0" step="50" value="200" data-r="ca" name="ca"></label>
    <label><span class="flab">Monate mit Auslandsreisen</span><input type="number" min="1" max="12" value="2" data-r="rm" name="rm"></label>
    <label><span class="flab">Tage bis zur Rückzahlung</span><input type="number" min="0" max="60" value="30" data-r="td" name="td"></label>
    {lounge}{LO.vers_field('r')}
    <label><span class="flab">Wert pro Punkt oder Meile</span><select data-r="pv" name="pv"><option value="d">Standard: 0,5 Cent (fester Anbieterwert, wo es einen gibt)</option><option value="1">1 Cent</option><option value="1.5">1,5 Cent</option><option value="0.5">0,5 Cent für alle</option><option value="0">nicht als Geld bewerten</option></select></label></div>
    <div class="lchecks">{cb}</div>
    {filt}
    <p class="note" style="margin:0"><b>Annahme zum Punktewert:</b> Punkte und Meilen rechnen wir standardmäßig mit 0,5 Cent. Nennt der Anbieter einen festen Wert, nehmen wir diesen, etwa bei PAYBACK 1 Cent pro °Punkt. Den Wert kannst du oben ändern. Der tatsächliche Gegenwert hängt von der Einlösung ab, Punkte sind kein garantiertes Cashback. Wir rechnen außerdem einen Lounge-Besuch mit 30 € und die Reiseversicherung mit dem Preis einer eigenen {K.t("jahrespolizze", land)}. Fremdwährung heißt: Zahlungen und Abhebungen außerhalb des Euroraums. Abhebungen im Inland verteilen wir gleichmäßig auf 12 Monate, im Ausland auf deine Reisemonate, und rechnen die Freigrenzen pro Monat. Bei Karten, die Bargeld sofort verzinsen, rechnen wir den Sollzins für die angegebenen Tage. Unter jeder Karte siehst du, wie das Ergebnis zustande kommt.</p>
  </{tag}><!--/rechnen-->
  '''

def prerendered(cards, D, item, form):
    """B12: Liste mit den Standardwerten des Formulars vorgerechnet und sortiert (Logik aus assets/rechnen.js über Node)."""
    import subprocess
    vals = {m.group(2): m.group(1) for m in re.finditer(r'value="([^"]*)" data-r="(\w+)"', form)}
    try:
        r = subprocess.run(['node', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prerender-karten.js')], input=json.dumps({'D': D, 'vals': vals, 'on': []}), capture_output=True, text=True, check=True)
        res = json.loads(r.stdout)
    except Exception as e:
        print('Vorrendern nicht möglich (node fehlt?):', e); return ''.join(item(c) for c in cards)
    order = sorted(cards, key=lambda c: ((res.get(c['slug']) or {}).get('low', 1), -((res.get(c['slug']) or {}).get('net') if (res.get(c['slug']) or {}).get('net') is not None else -1e9)))
    out = []
    for i, c in enumerate(order, 1):
        x = res.get(c['slug']); h = item(c)
        if x:
            h = h.replace('<article class="item ritem"', f'<article class="item ritem" data-net="{x["net"] if x["net"] is not None else ""}" data-low="{x["low"]}"', 1)
            h = h.replace('<span class="rk" data-rank></span>', f'<span class="rk" data-rank>{i}</span>', 1).replace('<div class="ires" data-res hidden></div>', f'<div class="ires" data-res>{x["html"]}</div>', 1)
        out.append(h)
    return ''.join(out)

def page(land, cards, D, tags):
    """Kreditkarten-Rechner: alle Karten nach deinem Ergebnis, mit Rechnung und Vergleich."""
    K.use(land); N = K.L['name']; rel = f'{land}/kreditkarten/rechner/'; P = '../../../'
    wien = any((d.get('lg') or {}).get('w') for d in D['cards'].values())
    t = f'Kreditkarten-Rechner {N}: Was kostet und bringt deine Karte? | Finvallo'
    d = f'Kreditkarten-Rechner {N}: {len(cards)} Karten mit Jahresgebühr, Auslandsgebühr, Bargeld, Cashback, Lounge und Versicherung für deine Nutzung durchgerechnet.'
    d = K.fit_desc(d)
    def item(c):
        st = f'<div class="stats"><div><small>Jahresgebühr</small><b>{"0 €" if c.get("fee") == 0 else (eur(c["fee"]) + " €") if c.get("fee") is not None else "–"}</b></div><div><small>Zahlung Ausland</small><b>{E(K.k_fx(c))}</b></div><div><small>Bargeld Inland</small><b>{E(K.k_cash(c))}</b></div></div>'
        return (f'<article class="item ritem" data-typ="{c.get("typ") or ""}" data-netz="{E((c.get("netz") or "").lower())}" data-fee="{c["fee"] if c.get("fee") is not None else 99999}">'
                f'<div class="rhead"><span class="rk" data-rank></span><div style="min-width:0"><h3 class="iname"><a href="../{c["slug"]}/">{E(c["titel"])}</a></h3><div class="iprov">{E(c["anbieter"])}</div></div>'
                f'<label class="rcmpl"><input type="checkbox" data-cmp aria-label="{E(c["titel"])} vergleichen"> Vergleichen</label></div>{st}<div class="ires" data-res hidden></div></article>')
    fq = [('Wie rechnet der Kreditkarten-Rechner?', 'Er zählt, was dir die Karte im Jahr bringt (Cashback, Punkte und Meilen, Lounge-Besuche, Reiseversicherung, Guthaben und Abos, die du wirklich nutzt) und zieht ab, was sie kostet (Jahresgebühr, Gebühren für Zahlungen in Fremdwährung und für Bargeld). Unter jeder Karte steht die ganze Rechnung.'),
          ('Was ist mit Fremdwährung gemeint?', 'Zahlungen und Abhebungen in einer anderen Währung als Euro, zum Beispiel im Urlaub außerhalb des Euroraums oder in Online-Shops, die in Dollar oder Pfund abrechnen. Im Euroraum fällt keine Fremdwährungsgebühr an.'),
          ('Warum stehen manche Karten weiter hinten, obwohl das Ergebnis gut ist?', 'Wenn für eine Karte eine Gebühr nicht bekannt ist oder ihre Reiseversicherung schwächer ist als die gewünschte, steht sie hinter den Karten mit vollständiger Rechnung. Das ist an der Karte gekennzeichnet.'),
          ('Zählt der Willkommensbonus?', 'Nur, wenn du „Erstes Jahr rechnen“ anhakst. Dann zählen der Willkommensbonus, ein Aktionspreis für das erste Jahr und Abos, die nur 12 Monate inklusive sind, etwa ChatGPT Go bei Revolut. Ohne Haken rechnet der Rechner mit dem Normalpreis der Folgejahre.')]
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
<p class="note calc-ex"><b>Beispiel:</b> Die Liste ist für 1.000 € Kartenumsatz im Monat vorgerechnet, davon 1.200 € im Jahr in Fremdwährung (10 %), 2 Abhebungen zu je 200 € im Inland und ohne Reiseversicherung. Ändere die Werte oben, dann rechnet sie für dich neu.</p>
<div class="fbot" style="margin:6px 0 10px"><b data-rcount>{len(cards)} Karten</b><span class="mut">sortiert nach deinem Ergebnis</span></div>
<div id="rlist" class="rlist">{prerendered(cards, D, item, box(land, tags, wien, page=True))}</div>
<h2>So rechnen wir</h2><div class="prose"><p>Cashback, Punkte und Meilen zählen mit ihrem Wert in Euro: ein Punkt oder eine Meile mit 0,5 Cent, bei einem festen Anbieterwert wie PAYBACK mit diesem Wert, jeweils bis zur Obergrenze der Karte. Ein Bonusprogramm mit Teilnahmegebühr zählt nur, wenn es sich bei deinem Umsatz lohnt. Ein Lounge-Besuch zählt mit 30 €, die Reiseversicherung mit dem Preis einer eigenen {K.t("jahrespolizze", land)} in der gewünschten Stufe. Davon ziehen wir die Jahresgebühr, die Gebühr auf Zahlungen in Fremdwährung und die Kosten für Bargeld ab. Bei Kreditkarten ohne Automatengebühr rechnen wir einen Monat Zinsen auf das abgehobene Geld.</p></div>
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
