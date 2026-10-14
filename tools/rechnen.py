"""„Persönlich rechnen“ auf der Kartenliste (AT und DE).

Daten je Karte: Gebühren und Versicherung aus karten.py, Cashback/Punkte/Lounge aus daten/<land>/ertrag.json,
Premiumkarten (Guthaben, Abos, Lounge, Punkte) aus daten/<land>/lohnt.json.
Setzt den Rechner über den Filter, einen Ergebnis-Platz in jede Karte und public/assets/rechnen.js.
Läuft in build.sh nach listui.py. Idempotent.
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
        if x:
            d['pct'] = x.get('punkte_pro_100') or 0
            if x.get('punkte_max'): d['cap'] = x['punkte_max']
            if x.get('punkte_hinweis'): d['ph'] = x['punkte_hinweis']
            d['fix'] = [[g['name'], g['eur']] for g in x.get('extra') or [] if g.get('immer')]
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

def box(land, tags, wien):
    sel = '<option value="0">nicht nötig</option>' + ''.join(f'<option value="{k}">{E(K.TIER[k][1])}</option>' for k in range(1, 5))
    lounge = ('<label>Lounge Wien pro Jahr<input type="number" min="0" max="200" value="0" data-r="wien"></label><label>Lounge Ausland pro Jahr<input type="number" min="0" max="200" value="0" data-r="lounge"></label>'
              if wien else '<label>Lounge-Besuche pro Jahr<input type="number" min="0" max="200" value="0" data-r="lounge"></label>')
    cb = ''
    if tags.get('cr'): cb += f'<label class="lc"><input type="checkbox" data-r="cr"><span>Guthaben der Karte voll nutzen <span class="mut">(nur {E(tags["cr"])})</span></span></label>'
    if tags.get('sb'): cb += f'<label class="lc"><input type="checkbox" data-r="sb"><span>Partner-Abos nutzen, die du sonst selbst zahlen würdest <span class="mut">(nur {E(tags["sb"])})</span></span></label>'
    return f'''<!--rechnen--><details class="box lcalc rbox" id="rbox" hidden>
    <summary><b>Persönlich rechnen</b><span>Was bringt dir jede Karte im Jahr? Trag deine Nutzung ein.</span></summary>
    <div class="lgrid"><label>Umsatz pro Monat (€)<input type="number" min="0" step="100" value="1000" data-r="spend"></label>
    <label>davon in Fremdwährung pro Jahr (€)<input type="number" min="0" step="100" value="1000" data-r="fxs"></label>
    <label>Bargeld im Ausland: Abhebungen pro Jahr<input type="number" min="0" max="200" value="0" data-r="cn"></label>
    <label>Betrag je Abhebung (€)<input type="number" min="0" step="50" value="200" data-r="ca"></label>
    {lounge}<label>davon mit Begleitung<input type="number" min="0" max="200" value="0" data-r="guests"></label>
    <label>Reiseversicherung<select data-r="vers">{sel}</select></label></div>
    {f'<div class="lchecks">{cb}</div>' if cb else ''}
    <p class="note" style="margin:0">Wir rechnen Punkte und Meilen mit 1 Cent, Hotelpunkte mit 0,4 Cent, einen Lounge-Besuch mit 30 € und die Reiseversicherung mit dem Preis einer eigenen Jahrespolizze. Fremdwährung heißt: Zahlungen und Abhebungen außerhalb des Euroraums. Unter jeder Karte siehst du, wie das Ergebnis zustande kommt.</p>
  </details><!--/rechnen-->
  '''

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
        slugs = re.findall(r'<h3 class="iname"><a href="(?:[^"]*/)?([^"/]+)/">', s)
        bys = {c['slug']: c for c in DATA[land][0]}
        cards = [bys[x] for x in slugs if x in bys]
        D, tags = card_data(land, cards)
        wien = any((d.get('lg') or {}).get('w') for d in D['cards'].values())
        s = s.replace('<div class="box filt" id="filt"', box(land, tags, wien) + '<div class="box filt" id="filt"', 1)
        s = re.sub(r'(<div class="stats">.*?</div></div>)', r'\1<div class="ires" data-res hidden></div>', s, flags=re.S)
        s = s.replace('</body>', f'<script type="application/json" id="rdata">{json.dumps(D, ensure_ascii=False).replace("</", "<\\/")}</script>\n<script src="../../assets/rechnen.js?v={v}" defer></script>\n</body>', 1)
        open(f, 'w', encoding='utf-8').write(s)
        print('Rechnen', land, len(cards), 'Karten', s.count('data-res hidden'))

if __name__ == '__main__': main()
