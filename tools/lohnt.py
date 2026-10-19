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
TOP = 300
NUM = ['Kein typischer Fall', 'Ein typischer Fall', 'Zwei typische Fälle', 'Drei typische Fälle']

def load(land):
    p = SP + f'/daten/{land}/lohnt.json'
    return json.load(open(p)) if os.path.exists(p) else None

def free_visits(x):
    v = (x.get('lounge') or {}).get('visits')
    return math.inf if v == 'unbegrenzt' else (v or 0)

def wien_only(x): return (x.get('lounge') or {}).get('scope') == 'wien'

def lw(x): return ' am Flughafen Wien' if wien_only(x) else ''

def guests_free(x):
    g = (x.get('lounge') or {}).get('guests_free') or 0
    return math.inf if g == 'unbegrenzt' else g

def subs(x, A):
    """Partner-Abos der Karte mit Jahreswert (None, wenn der reguläre Preis nicht bestätigt ist)."""
    P = A.get('abos') or {}
    return [dict(name=n, eur=round(P[n]['eur_monat'] * 12, 2) if (P.get(n) or {}).get('eur_monat') else None, monat=(P.get(n) or {}).get('eur_monat')) for n in x.get('subs_names') or []]

def priced(x, A): return [s for s in subs(x, A) if s['eur']]

def value(c, x, A, p):
    """Wert der genutzten Vorteile pro Jahr (ohne Willkommensbonus) und Aufschlüsselung."""
    parts = []
    if p.get('credits'):
        for g in x.get('credits') or []: parts.append((g['name'], g['eur']))
    if p.get('subs'):
        for g in priced(x, A): parts.append((g['name'], g['eur']))
    lo = p.get('wien', p['lounge']) if wien_only(x) else p['lounge']
    lv = min(lo, free_visits(x))
    if (p.get('spend') or 0) * 12 < ((x.get('lounge') or {}).get('min_umsatz') or 0): lv = 0
    if lv: parts.append((f'{lv} Lounge-Besuche', lv * A['lounge_eur']))
    gv = min(p.get('guests') or 0, lv, guests_free(x))
    if gv: parts.append((f'{gv} Begleitpersonen in der Lounge', gv * A['lounge_eur']))
    if p['spend'] and x.get('punkte_pro_100'): parts.append(('Punkte oder Meilen', min(p['spend'] * 12 / 100 * x['punkte_pro_100'], x.get('punkte_max') or 1e9)))
    if p.get('vers') and c.get('tier'): parts.append((f'Reiseversicherung (statt eigener {K.t("jahrespolizze")})', A['vers'][str(c['tier'])]))
    for e in x.get('extra') or []:
        if e.get('immer'): parts.append((e['name'], e['eur']))
    return sum(v for _, v in parts), parts

def namelist(n):
    n = list(n)
    return n[0] if len(n) == 1 else ', '.join(n[:-1]) + ' und ' + n[-1]

def profiles(c, x, A):
    """Typische Fälle, nur mit den Vorteilen, die diese Karte wirklich hat."""
    lg, gf, pp = free_visits(x), guests_free(x), x.get('punkte_pro_100')
    cr, sb = x.get('credits') or [], priced(x, A)
    out = []
    d = []
    if lg: d.append(f'4 Lounge-Besuche{lw(x)} im Jahr' if lg >= 4 else f'{lg} Lounge-Besuch{"e" if lg > 1 else ""}{lw(x)} im Jahr')
    if pp: d.append('1.000 € Kartenumsatz im Monat')
    nu = [w for w, h in (('Guthaben', cr), ('Partner-Abos', sb)) if h]
    out.append(dict(t='Du reist ein- bis zweimal im Jahr', d=namelist(d) + '.' if d else 'Du nutzt nur die Grundfunktionen der Karte.',
                    n=f'{namelist(nu)} nutzt du nicht.' if nu else '', p=dict(lounge=min(4, lg), spend=1000)))
    if cr or sb:
        what = []
        if cr: what.append(f'Du löst {namelist(g["name"] for g in cr)} voll ein')
        if sb: what.append(('und würdest ' if cr else 'Du würdest ') + f'die Partner-Abos {namelist(g["name"] for g in sb)} sonst selbst bezahlen')
        d = [w for w in (f'{min(6, lg)} Lounge-Besuch{"e" if min(6, lg) != 1 else ""}{lw(x)}' if lg else '', '1.500 € Umsatz im Monat' if pp else '') if w]
        out.append(dict(t='Du nutzt alle Guthaben' if cr and not sb else 'Du nutzt alle Partner-Abos' if sb and not cr else 'Du nutzt alle Guthaben und Abos',
                        d=' '.join(what) + '.' + (f' Dazu {namelist(d)}.' if d else ''), n='', p=dict(credits=True, subs=True, lounge=min(6, lg), spend=1500)))
    elif pp:
        out.append(dict(t='Du zahlst fast alles mit der Karte', d='3.000 € Kartenumsatz im Monat' + (f', {min(6, lg)} Lounge-Besuch{"e" if min(6, lg) != 1 else ""}{lw(x)} im Jahr.' if lg else '.'), n='',
                        p=dict(lounge=min(6, lg), spend=3000)))
    if lg and lg > 6:
        n = min(20, lg); g = min(6, gf)
        d = f'{n} Lounge-Besuch{"e" if n != 1 else ""}{lw(x)} im Jahr' + (f', davon {g} mit Begleitung' if g else '') + (', 2.500 € Umsatz im Monat' if pp else '')
        rest = [w for w, h in (('Guthaben', cr), ('Abos', sb)) if h]
        out.append(dict(t='Du fliegst oft', d=d + '.' + (f' {namelist(rest)} nutzt du auch.' if rest else ''), n='',
                        p=dict(credits=True, subs=True, lounge=n, guests=g, spend=2500)))
    if c.get('tier') and len(out) < 3:
        w = A['vers'][str(c['tier'])]
        out.append(dict(t='Du bräuchtest sonst eine Reiseversicherung', d=f'Statt einer eigenen {K.t("jahrespolizze")} (etwa {eur(w)} €) nutzt du die Reiseversicherung der Karte ({K.TIER[c["tier"]][1]})' + (', dazu ' + namelist([w for w in (f'{min(4, lg)} Lounge-Besuch{"e" if min(4, lg) != 1 else ""}{lw(x)}' if lg else '', '1.000 € Umsatz im Monat' if pp else '') if w]) if lg or pp else '') + '.', n='',
                        p=dict(lounge=min(4, lg), spend=1000, vers=True)))
    for o in out: o['p'].setdefault('vers', False)
    return out

def breakeven(c, x, A, credits, vers=False, sub=False):
    """Ab wann holt die Karte die Jahresgebühr herein?
    ('ok',0) | ('lounge',n) bei 1.000 € Umsatz | ('both',(n,€)) alle enthaltenen Besuche plus Umsatz | ('spend',€) | ('no',None)"""
    fee = c['fee'] or 0
    val = lambda lounge, spend: value(c, x, A, dict(credits=credits, subs=sub, lounge=lounge, guests=0, spend=spend, vers=vers))[0]
    if val(0, 1000) >= fee: return ('ok', 0)
    fv = free_visits(x); pp = x.get('punkte_pro_100') or 0
    if fv:
        n = math.ceil(round(fee - val(0, 1000), 6) / A['lounge_eur'])
        if n <= fv and n <= 60: return ('lounge', n)
    if pp:
        steps = range(1000, 10001, 250)
        if fv and fv != math.inf:
            for sp in steps:
                if val(fv, sp) >= fee: return ('both', (fv, sp))
        else:
            for sp in steps:
                if val(0, sp) >= fee: return ('spend', sp)
    return ('no', None)

def need(k, v, x=None):
    """Teilsatz nach „lohnt sie sich …“."""
    w = lw(x or {})
    u = ' (bei 1.000 € Kartenumsatz im Monat)' if (x or {}).get('punkte_pro_100') else ''
    if k == 'lounge': return (f'ab dem ersten Lounge-Besuch{w} im Jahr' if v == 1 else f'ab etwa {v} Lounge-Besuchen{w} im Jahr') + u
    if k == 'both': return f'mit allen {v[0]} Lounge-Besuchen{w} ab etwa {eur(v[1])} € Kartenumsatz im Monat'
    if k == 'spend': return f'ab etwa {eur(v)} € Kartenumsatz im Monat'
    return ''

def then(k, v, x=None):
    return {'ok': 'holst du die Jahresgebühr damit schon herein.', 'no': 'reicht auch das nicht.'}.get(k) or f'lohnt sie sich {need(k, v, x)}.'

def verdict(c, x, A):
    fee = c['fee'] or 0
    cr = sum(g['eur'] for g in x.get('credits') or [])
    s = []
    if cr: s.append(f'Die Guthaben sind zusammen {eur(cr)} € im Jahr wert, die Jahresgebühr beträgt {eur(fee)} €.')
    k1, v1 = breakeven(c, x, A, True)
    w = [t for t, h in (('allen Guthaben', cr), ('1.000 € Kartenumsatz im Monat', x.get('punkte_pro_100') and k1 in ('ok', 'lounge'))) if h]
    base = 'Mit ' + ' und '.join(w) if w else ''
    if k1 == 'ok': s.append((base or 'Schon ohne Zusatznutzung') + (' holst du die Jahresgebühr herein, auch ohne Lounge-Besuch.' if free_visits(x) else ' holst du die Jahresgebühr herein.'))
    elif k1 == 'both': s.append(f'Mit {"allen Guthaben und " if cr else ""}allen {v1[0]} enthaltenen Lounge-Besuchen{lw(x)} lohnt sie sich ab etwa {eur(v1[1])} € Kartenumsatz im Monat.')
    elif k1 == 'lounge' and v1 == 1: s.append((f'{base} ist die Jahresgebühr' if base else 'Die Jahresgebühr ist') + f' ab dem ersten Lounge-Besuch{lw(x)} gedeckt; jeder weitere Besuch ist ein Plus.')
    elif k1 != 'no': s.append((f'{base} lohnt sie sich ' if base else 'Sie lohnt sich ') + need(k1, v1, x) + '.')
    else:
        h = [w for w, v in (('Guthaben', cr), ('Lounge-Besuchen', free_visits(x)), ('Punkten', x.get('punkte_pro_100'))) if v]
        s.append(f'Mit den enthaltenen {namelist(h)} allein holst du die Jahresgebühr kaum herein.' if h else 'Ohne weitere Vorteile holst du die Jahresgebühr kaum herein.')
    if cr:
        k0, v0 = breakeven(c, x, A, False)
        if (k0, v0) != (k1, v1):
            s.append('Ohne die Guthaben ' + ({'ok': 'reicht das trotzdem.', 'no': 'lohnt sie sich kaum.'}.get(k0) or f'lohnt sie sich {need(k0, v0, x)}.'))
    if c.get('tier') and k1 != 'ok':
        kv, vv = breakeven(c, x, A, True, True); w = A['vers'][str(c['tier'])]
        s.append(f'Brauchst du sonst eine eigene Jahres-Reiseversicherung (etwa {eur(w)} €), ' + then(kv, vv, x))
    sb = priced(x, A)
    if sb and k1 != 'ok':
        ks, vs = breakeven(c, x, A, True, False, True)
        s.append(f'Würdest du alle Partner-Abos sonst selbst bezahlen (zusammen etwa {eur(round(sum(g["eur"] for g in sb)))} € im Jahr), ' + then(ks, vs, x))
    elif x.get('subs_names') and not sb: s.append('Dazu kommen Partner-Abos, die nur zählen, wenn du sie sonst selbst bezahlen würdest.')
    return ' '.join(s)

def short(c, x, A):
    k, v = breakeven(c, x, A, True)
    g = ' mit allen Guthaben' if x.get('credits') else ''
    if k == 'ok': return 'Lohnt sich schon bei normaler Nutzung' + g
    w = ' in Wien' if wien_only(x) else ''
    if k == 'lounge': return (f'Jahresgebühr ab dem ersten Lounge-Besuch{w} gedeckt' if v == 1 else f'Lohnt sich ab etwa {v} Lounge-Besuchen{w} im Jahr') + g
    if k == 'both': return f'Lohnt sich mit {v[0]} Lounge-Besuchen{w} ab etwa {eur(v[1])} € Umsatz im Monat' + g
    if k == 'spend': return f'Lohnt sich ab etwa {eur(v or 0)} € Umsatz im Monat' + g
    if c.get('tier') and breakeven(c, x, A, True, True)[0] == 'ok': return 'Lohnt sich, wenn du sonst eine Reiseversicherung kaufen würdest'
    return 'Lohnt sich nur bei sehr intensiver Nutzung'

def calc_html(c, x, A):
    lg, gf, pp = free_visits(x), guests_free(x), x.get('punkte_pro_100') or 0
    sb = subs(x, A); ps = [g for g in sb if g['eur']]; np_ = [g['name'] for g in sb if not g['eur']]
    data = dict(fee=c['fee'] or 0, lounge=A['lounge_eur'], visits=None if lg == math.inf else lg, guests=None if gf == math.inf else gf,
                pp100=pp, vers=A['vers'].get(str(c.get('tier')), 0) if c.get('tier') else 0,
                credits=[dict(n=g['name'], v=g['eur']) for g in x.get('credits') or []] + [dict(n=g['name'], v=g['eur']) for g in ps], pmax=x.get('punkte_max') or None,
                welcome=(x.get('welcome') or {}).get('eur') or 0, minsp=(x.get('lounge') or {}).get('min_umsatz') or 0)
    nc = len(x.get('credits') or [])
    PR = profiles(c, x, A); mid = PR[len(PR) // 2]['p'] if PR else dict(lounge=0, spend=1000, vers=False)
    on_cr, on_sb = bool(mid.get('credits')), bool(mid.get('subs'))
    I = dict(spend=mid.get('spend') or 0, lounge=mid.get('lounge') or 0, guests=mid.get('guests') or 0, welcome=False, vers=bool(mid.get('vers') and data['vers']),
             credits=[i for i in range(nc) if on_cr] + [nc + i for i in range(len(ps)) if on_sb])
    cr = ''.join(f'<label class="lc"><input type="checkbox" data-credit="{i}" name="credit{i}"{" checked" if on_cr else ""}> {E(g["name"])} <b>{eur(g["eur"])} €</b></label>' for i, g in enumerate(x.get('credits') or []))
    if ps: cr += '<p class="note" style="margin:6px 0 0">Partner-Abos: Hake nur an, was du sonst selbst bezahlen würdest.</p>' + ''.join(f'<label class="lc"><input type="checkbox" data-credit="{nc + i}" name="credit{nc + i}"{" checked" if on_sb else ""}> {E(g["name"])} <b>{eur(g["eur"])} €</b></label>' for i, g in enumerate(ps))
    if np_: cr += f'<p class="note" style="margin:0">{"Weitere " if ps else ""}Partner-Abos ohne festen Preis, die wir nicht mitrechnen: {E(", ".join(np_))}.</p>'
    wl = f'<label class="lc"><input type="checkbox" data-welcome name="welcome"> Willkommensbonus im ersten Jahr <b>{eur(data["welcome"])} €</b></label>' if data['welcome'] else ''
    vs = f'<label class="lc"><input type="checkbox" data-vers name="vers"{" checked" if I["vers"] else ""}> Ich bräuchte sonst eine eigene Reiseversicherung <b>{eur(data["vers"])} €</b></label>' if data['vers'] else ''
    ins = ''.join(w for w in (
        f'<label><span class="flab">Lounge-Besuche{lw(x)} im Jahr</span><input type="number" min="0" max="200" value="{I['lounge']}" data-in="lounge" name="lounge"></label>' if lg else '',
        f'<label><span class="flab">davon mit Begleitung</span><input type="number" min="0" max="200" value="{I["guests"]}" data-in="guests" name="guests"></label>' if lg and gf else '',
        f'<label><span class="flab">Kartenumsatz pro Monat (€)</span><input type="number" min="0" step="100" value="{I["spend"]}" data-in="spend" name="spend"></label>' if pp else '') if w)
    if not lg: I['lounge'] = I['guests'] = 0
    if not (lg and gf): I['guests'] = 0
    if not pp: I['spend'] = 0
    r = prerender(data, I)
    ex = f'<p class="note calc-ex"><b>Beispiel:</b> Vorgerechnet für den Fall „{E(PR[len(PR) // 2]["t"])}“: {E(PR[len(PR) // 2]["d"])} Ändere die Werte, dann rechnet der Rechner neu.</p>' if PR and r else ''
    return f'''<form class="box lcalc" data-lohnt='{html.escape(json.dumps(data), quote=True)}' onsubmit="return false">
  <h2 style="margin-top:0">Rechne mit deinen Zahlen</h2>
  {f'<div class="lgrid">{ins}</div>' if ins else ''}
  {cr}{wl}{vs}
  <div class="lres"><div><small>Wert deiner Vorteile</small><b data-out="val">{E(r["val"]) if r else "–"}</b></div><div><small>Jahresgebühr</small><b>{eur(data["fee"])} €</b></div><div><small>Ergebnis pro Jahr</small><b data-out="net"{(' class="good"' if r["good"] else ' class="bad"') if r else ""}>{E(r["net"]) if r else "–"}</b></div></div>
  <p class="note" data-out="txt">{E(r["txt"]) if r else ""}</p>
  {ex}
</form>'''

def prerender(D, I):
    """B12: Ergebnis für den mittleren Fall mit der Logik aus assets/lohnt.js (über Node)."""
    import subprocess
    try:
        o = subprocess.run(['node', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prerender-lohnt.js')], input=json.dumps([dict(key='x', D=D, I=I)]), capture_output=True, text=True, check=True)
        return json.loads(o.stdout)['x']
    except Exception as e:
        print('Vorrendern nicht möglich (node fehlt?):', e); return None


def card_page(land, c, x, A, P, prov):
    N = K.L['name']; rel = f'{land}/kreditkarten/bestenlisten/lohnt-sich/{c["slug"]}/'
    t = f'Ab wann lohnt sich die {c["titel"]}? ({land.upper()}) | Finvallo'
    if len(t) > 70: t = f'Lohnt sich die {c["titel"]}? | Finvallo'
    vt = verdict(c, x, A)
    d = f'Ab wann lohnt sich die {c["titel"]} in {N}? {short(c, x, A)}. Mit Rechner für deine Nutzung.'
    d = K.fit_desc(d)
    rows = ''
    for g in x.get('credits') or []: rows += f'<tr><td>{E(g["name"])}</td><td class="nw">{eur(g["eur"])} €</td><td>{E(g.get("hinweis") or g.get("scope") or "")}</td></tr>'
    lg = x.get('lounge') or {}
    if lg.get('visits'): rows += f'<tr><td>Lounge-Besuche ({E(lg.get("program") or "")})</td><td class="nw">pro Besuch ≈ {eur(A["lounge_eur"])} €</td><td>{"unbegrenzt" if lg["visits"] == "unbegrenzt" else str(lg["visits"]) + " pro Jahr"}{"; " + E(lg["hinweis"]) if lg.get("hinweis") else ""}</td></tr>'
    if x.get('punkte_pro_100'): rows += f'<tr><td>Punkte oder Meilen</td><td class="nw">{eur(x["punkte_pro_100"])} € pro 100 € Umsatz</td><td>{E(x.get("punkte_hinweis") or "1 Punkt oder Meile = 1 Cent")}{f", höchstens {eur(x.get('punkte_max') or 0)} € im Jahr" if x.get("punkte_max") else ""}</td></tr>'
    if c.get('tier'): rows += f'<tr><td>Reiseversicherung ({E(K.TIER[c["tier"]][1])})</td><td class="nw">≈ {eur(A["vers"][str(c["tier"])])} €</td><td>so viel kostet eine vergleichbare eigene {K.t("jahrespolizze")}</td></tr>'
    sb = subs(x, A); ps = [g for g in sb if g['eur']]
    if ps: rows += f'<tr><td>Partner-Abos</td><td class="nw">bis {eur(round(sum(g["eur"] for g in ps)))} €</td><td>{E("; ".join(g["name"] + ": " + (A["abos"][g["name"]].get("hinweis") or eur(g["monat"]) + " € pro Monat") for g in ps))}. Zählt nur, was du sonst selbst bezahlen würdest.</td></tr>'
    np_ = [g['name'] for g in sb if not g['eur']]
    if np_: rows += f'<tr><td>{"Weitere " if ps else ""}Partner-Abos</td><td class="nw">je nach Nutzung</td><td>{E(", ".join(np_))}. Zählt nur, was du sonst selbst bezahlen würdest.</td></tr>'
    for e in x.get('extra') or []: rows += f'<tr><td>{E(e["name"])}</td><td class="nw">{eur(e["eur"]) + " €" if e.get("eur") else "–"}</td><td>{E(e.get("hinweis") or "")}</td></tr>'
    if (x.get('welcome') or {}).get('text'): rows += f'<tr><td>Willkommensbonus</td><td class="nw">{eur(x["welcome"]["eur"]) + " €" if x["welcome"].get("eur") else "–"}</td><td>{E(x["welcome"]["text"])}, nur im ersten Jahr</td></tr>'
    prof = ''; PR = profiles(c, x, A)
    for pr in PR:
        v, parts = value(c, x, A, pr['p']); net = v - (c['fee'] or 0)
        prof += f'<div class="lprof"><b>{E(pr["t"])}</b><small>{E((pr["d"] + " " + pr["n"]).strip())}</small><span class="{"good" if net >= 0 else "bad"}">{"+" if net >= 0 else "−"}{eur(round(abs(net)))} € pro Jahr</span></div>'
    T = c['titel']; fee = c['fee'] or 0
    lg_ = (x.get('lounge') or {}).get('visits')
    parts = [p for p, h in ((f'die Guthaben der {T} zum Nennwert', x.get('credits')), (f'jeden Lounge-Besuch mit {eur(A["lounge_eur"])} €', lg_), ('Punkte und Meilen mit 1 Cent', x.get('punkte_pro_100')),
             (f'die Reiseversicherung mit dem Preis einer vergleichbaren eigenen {K.t("jahrespolizze")} (etwa {eur(A["vers"][str(c["tier"])])} €), aber nur, wenn du sonst eine eigene bräuchtest' if c.get('tier') else '', c.get('tier')),
             ('Partner-Abos mit dem günstigsten regulären Tarif des Anbieters, wenn du sie sonst selbst bezahlen würdest', x.get('subs_names'))) if h]
    how_ = f'Bei der {T} zählen wir nur Vorteile, die du wirklich nutzt: ' + '; '.join(parts) + f'. Davon ziehen wir die Jahresgebühr von {eur(fee)} € ab.' if parts else f'Bei der {T} ziehen wir die Jahresgebühr von {eur(fee)} € von den Vorteilen ab, die du wirklich nutzt.'
    fq = [(f'Ab wann lohnt sich die {T}?', vt if T in vt else f'Die {T} kostet {eur(fee)} € im Jahr. ' + vt),
          (f'Wie rechnet Finvallo bei der {T}?', how_),
          ('Zählt der Willkommensbonus mit?', 'Nur im ersten Jahr. Für die Frage, ob sich die Karte dauerhaft lohnt, rechnen wir ohne Bonus.')]
    ld = K.graph(rel, t, d, [(N, f'{land}/'), ('Kreditkarten', f'{land}/kreditkarten/'), ('Bestenlisten', f'{land}/kreditkarten/bestenlisten/'), ('Top-Karten', f'{land}/kreditkarten/bestenlisten/lohnt-sich/'), (c['titel'], rel)],
                 [{"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}], date=x.get('geprueft') or c['geprueft'])
    src = ' · '.join(K.ext(u) for u in dict.fromkeys((x.get('quellen') or []) + [(A['abos'][g['name']]['quelle']) for g in priced(x, A) if A['abos'][g['name']].get('quelle')]))
    body = f'''{K.HDR(P, rel)}
<div class="wrap"><main id="app">
<div class="crumb"><span><a href="../../">Bestenlisten</a> › <a href="../">Top-Karten</a> › {E(c["titel"])}</span><span>Stand {K.dmy(x.get("geprueft") or c["geprueft"])}</span></div>
<h1>Ab wann lohnt sich die {E(c["titel"])}?</h1>
<p class="lede">Die Karte kostet {eur(c["fee"] or 0)} € im Jahr. Ob sich das rechnet, hängt davon ab, welche Vorteile du wirklich nutzt.</p>
<section class="facts box glance" aria-label="Kurzantwort"><h2 style="margin-top:0">Kurzantwort</h2><div class="prose"><p>{E(vt)}</p></div></section>
<h2>Was die Vorteile wert sind</h2><div class="tbl ltab"><table><thead><tr><th>Vorteil</th><th>Wert pro Jahr</th></tr></thead><tbody>{re.sub(r'<tr><td>(.*?)</td><td class="nw">(.*?)</td><td>(.*?)</td></tr>', lambda m: f'<tr><td>{m.group(1)}' + (f'<br><small class="mut">{m.group(3)}</small>' if m.group(3) else '') + f'</td><td class="nw">{m.group(2)}</td></tr>', rows)}</tbody></table></div>
<h2>{NUM[len(PR)]}</h2><div class="lprofs">{prof}</div>
{calc_html(c, x, A)}
<h2>Fragen und Antworten</h2><div class="faq">{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in fq)}</div>
<p class="note" style="margin-top:18px"><a class="lnk" href="../../../{c["slug"]}/">Alle Konditionen der {E(c["titel"])} →</a> · <a class="lnk" href="../">Alle Top-Karten →</a></p>
{f'<p class="src">Quellen: {src}</p>' if src else ''}
</main>
{K.footer(P)}'''
    K.write(rel, K.head(t, d, rel, P, ld) + body.replace('</body>', script(P) + '\n</body>'))
    return rel

def script(P):
    import hashlib
    v = hashlib.sha256(open(R + 'assets/lohnt.js', 'rb').read()).hexdigest()[:8]
    return f'<script src="{P}assets/lohnt.js?v={v}" defer></script>'

def hubprof(split):
    """Fälle für die Übersicht. split: Land hat Karten nur für den Flughafen Wien, dann je Reise ein Besuch in Wien und einer im Ausland."""
    L = lambda n: f'{n} Lounge-Besuche ({n // 2} in Wien, {n // 2} im Ausland)' if split else f'{n} Lounge-Besuche'
    return [
        dict(t='Du reist ein- bis zweimal im Jahr', d=f'{L(4)}, 1.000 € Kartenumsatz im Monat, keine Guthaben oder Abos.', p=dict(lounge=4, wien=2, spend=1000)),
        dict(t='Du nutzt alle Guthaben und Abos', d=f'Guthaben und Partner-Abos der Karte voll genutzt, {L(6)}, 1.500 € Umsatz im Monat.', p=dict(credits=True, subs=True, lounge=6, wien=3, spend=1500)),
        dict(t='Du fliegst oft', d=f'{L(20)} im Jahr, davon 6 mit Begleitung, 2.500 € Umsatz im Monat, Guthaben und Abos genutzt.', p=dict(credits=True, subs=True, lounge=20, wien=10, guests=6, spend=2500)),
    ]

def lounge_line(x):
    lg = x.get('lounge') or {}; v = free_visits(x)
    if not v: return 'Kein Lounge-Zugang'
    n = ('unbegrenzt' if v == math.inf else f'{v}× im Jahr') + (f' ab {eur(lg["min_umsatz"])} € Umsatz im Jahr' if lg.get('min_umsatz') else '')
    return f'Lounge nur am Flughafen Wien, {n}' if wien_only(x) else f'Lounges weltweit, {n} ({lg.get("program")})'

def winners(land, cards, X, A):
    out = []
    for pr in hubprof(any(wien_only(x) for x in X.values())):
        best = None
        for c in cards:
            x = X[c['slug']]; v, _ = value(c, x, A, pr['p']); net = v - (c['fee'] or 0)
            if best is None or net > best[1]: best = (c, net)
        out.append((pr, best))
    return out

def tag(c): return {'American Express': 'Amex'}.get(c['anbieter'], c['anbieter'])

def basekey(n):
    return re.sub(r'\s+(\(.*\)|Complete|Plus|Premium Digital|Standard Digital|Mitgliedschaft)$', '', n)

def hub_data(cards, X, A):
    """Daten für den Filter: je Karte die Vorteile, je Guthaben oder Abo die Anbieter, die es bieten."""
    keys = {}; out = []
    for c in cards:
        x = X[c['slug']]; it = {}
        for g in x.get('credits') or []: it[basekey(g['name'])] = it.get(basekey(g['name']), 0) + g['eur']
        for g in priced(x, A): it[basekey(g['name'])] = it.get(basekey(g['name']), 0) + g['eur']
        for k in it: keys.setdefault(k, []).append(tag(c))
        lg, gf = free_visits(x), guests_free(x)
        out.append(dict(s=c['slug'], wien=wien_only(x), minsp=(x.get('lounge') or {}).get('min_umsatz') or 0, fee=c['fee'] or 0, tier=c.get('tier') or 0, visits=None if lg == math.inf else lg, guests=None if gf == math.inf else gf,
                        pp100=x.get('punkte_pro_100') or 0, pmax=x.get('punkte_max') or None, it=it,
                        fix=sum(e['eur'] for e in x.get('extra') or [] if e.get('immer')), welcome=(x.get('welcome') or {}).get('eur') or 0))
    opts = sorted(keys.items(), key=lambda kv: (kv[1][0], kv[0].lower()))
    return dict(cards=out, lounge=A['lounge_eur'], vers=A['vers']), [(k, ', '.join(dict.fromkeys(v))) for k, v in opts]

INFO = [('Basis-Reiseschutz', 'Vor allem eine Auslandsreise-Krankenversicherung, oft nur mit niedrigen Summen oder nur, wenn du die Reise mit der Karte bezahlt hast.'),
        ('Reiseversicherung inkl. Storno', 'Dazu eine Stornoversicherung: Sie zahlt die Reisekosten, wenn du die Reise aus einem wichtigen Grund nicht antreten kannst, etwa bei Krankheit.'),
        ('Umfassender Reiseschutz', 'Krankenversicherung, Storno, Reiseabbruch, Gepäck und meist eine Unfallversicherung, mit höheren Summen.'),
        ('Premium-Reiseschutz', 'Wie umfassend, aber mit hohen Summen und oft mit Mietwagen-Schutz, Familie und Mitreisenden.')]

def vers_info():
    """Kleines Info-Feld, das die Stufen der Reiseversicherung erklärt."""
    return ('<details class="tip"><summary aria-label="Was bedeuten die Stufen?">i</summary><div class="pop"><b>Die Stufen der Reiseversicherung</b>'
            + ''.join(f'<p><b>{E(t)}:</b> {E(d)}</p>' for t, d in INFO) + '<p class="mut">Was eine Karte genau abdeckt, steht auf ihrer Seite unter „Versicherung“.</p></div></details>')

def vers_field(attr):
    sel = '<option value="0" selected>nicht nötig</option>' + ''.join(f'<option value="{k}">{E(K.TIER[k][1])}</option>' for k in range(1, 5))
    return f'<div class="fld"><span class="flab">Reiseversicherung {vers_info()}</span><select data-{attr}="vers" name="vers" aria-label="Reiseversicherung">{sel}</select></div>'

def filter_html(cards, X, A):
    data, opts = hub_data(cards, X, A)
    sel = '<option value="0">nicht nötig</option>' + ''.join(f'<option value="{k}">{E(K.TIER[k][1])}</option>' for k in range(1, 5))
    cb = ''.join(f'<label class="lc"><input type="checkbox" data-item="{E(k)}"><span>{E(k)} <span class="mut">({E(t)})</span></span></label>' for k, t in opts)
    return f'''<div class="box lcalc lfilter" data-lohnt-hub='{html.escape(json.dumps(data), quote=True)}' hidden>
  <h2 style="margin-top:0">Was würdest du nutzen?</h2>
  <p class="note" style="margin:0">Trag ein, was du wirklich nutzt. Die Karten unten zeigen dann gleich, ob sie für dich ein Plus oder ein Minus ergeben.</p>
  <div class="lgrid">{'<label><span class="flab">Lounge Wien pro Jahr</span><input type="number" min="0" max="200" value="0" data-in="wien"></label><label><span class="flab">Lounge Ausland pro Jahr</span><input type="number" min="0" max="200" value="0" data-in="lounge"></label>' if any(wien_only(x) for x in X.values()) else '<label><span class="flab">Lounge-Besuche im Jahr</span><input type="number" min="0" max="200" value="0" data-in="lounge"></label>'}
  <label><span class="flab">davon mit Begleitung</span><input type="number" min="0" max="200" value="0" data-in="guests"></label>
  <label><span class="flab">Umsatz pro Monat (€)</span><input type="number" min="0" step="100" value="1000" data-in="spend"></label>
  {vers_field('in')}</div>
  {f'<p class="note" style="margin:6px 0 0"><b>Guthaben und Abos, die du nutzen würdest</b> (Abos nur, wenn du sie sonst selbst bezahlen würdest)</p><div class="lchecks">{cb}</div>' if cb else ''}
  <label class="lc"><input type="checkbox" data-welcome> Willkommensbonus im ersten Jahr mitrechnen</label>
</div>'''

def hub(land, cards, X, A, P):
    N = K.L['name']; rel = f'{land}/kreditkarten/bestenlisten/lohnt-sich/'
    t = f'Top-Kreditkarten {N} 2026: Ab wann sich eine Premiumkarte lohnt | Finvallo'
    d = f'Die Top-Kreditkarten in {N} ab {TOP} € im Jahr und weitere Premiumkarten: ab wann sie sich lohnen, mit Guthaben, Lounges und Punkten gerechnet.'
    tile = lambda c: f'<a class="catcard" data-card="{c["slug"]}" href="{c["slug"]}/"><span class="ct">{eur(c["fee"] or 0)} € im Jahr</span><b>{E(c["titel"])}</b><small class="mut">{E(lounge_line(X[c["slug"]]))}</small><span data-def>{E(short(c, X[c["slug"]], A))}</span><span class="lnet" data-net hidden></span><small>Rechnung ansehen →</small></a>'
    top = sorted([c for c in cards if (c['fee'] or 0) >= TOP], key=lambda c: -(c['fee'] or 0))
    rest = sorted([c for c in cards if (c['fee'] or 0) < TOP], key=lambda c: -(c['fee'] or 0))
    win = ''.join((f'<div class="lprof"><b>{E(pr["t"])}</b><small>{E(pr["d"])}</small><span>Am meisten bringt die <a class="lnk" href="{b[0]["slug"]}/">{E(b[0]["titel"])}</a>: +{eur(round(b[1]))} € pro Jahr nach Jahresgebühr</span></div>' if b[1] >= 0 else
                   f'<div class="lprof"><b>{E(pr["t"])}</b><small>{E(pr["d"])}</small><span>Hier lohnt sich keine Premiumkarte. Nimm besser eine <a class="lnk" href="../gratis/">Karte ohne Jahresgebühr</a>.</span></div>') for pr, b in winners(land, cards, X, A))
    fq = [('Lohnt sich eine Premium-Kreditkarte?', 'Nur, wenn du die enthaltenen Vorteile wirklich nutzt. Wir rechnen Guthaben, Lounge-Besuche, Punkte und Reiseversicherung gegen die Jahresgebühr. Für die meisten Menschen ohne viele Flugreisen ist eine kostenlose Karte günstiger.'),
          ('Wie viel ist ein Lounge-Besuch wert?', f'Wir rechnen mit {eur(A["lounge_eur"])} € pro Besuch. {A.get("lounge_quelle", "")}'.strip())]
    ld = K.graph(rel, t, d, [(N, f'{land}/'), ('Kreditkarten', f'{land}/kreditkarten/'), ('Bestenlisten', f'{land}/kreditkarten/bestenlisten/'), ('Top-Karten', rel)],
                 [{"@type": "ItemList", "name": f"Premium-Kreditkarten {N}: ab wann sie sich lohnen", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": c['titel'], "url": f"https://finvallo.com/{rel}{c['slug']}/"} for i, c in enumerate(cards)]},
                  {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}])
    other = f'{"de" if land == "at" else "at"}/kreditkarten/bestenlisten/lohnt-sich/'
    body = f'''{K.HDR(P, rel, other)}
<div class="wrap"><main id="app">
<div class="crumb"><span><a href="../">Bestenlisten</a> › Top-Karten</span><span>Stand {K.dmy(K.L["stand"])}</span></div>
<h1>Top-Kreditkarten in {N}: ab wann sie sich lohnen</h1>
<p class="lede">Premiumkarten kosten viel, bringen aber Guthaben, Lounges und Versicherungen mit. Für jede Karte rechnen wir aus, ab welcher Nutzung sich die Jahresgebühr bezahlt macht. Mit dem Filter siehst du sofort, welche Karte sich für dich rechnet.</p>
{filter_html(cards, X, A)}
<div class="catgrid">{"".join(tile(c) for c in top + rest)}</div>
<h2>Welche Karte passt zu dir?</h2><div class="lprofs">{win}</div>
<h2>So rechnen wir</h2><div class="prose"><p>Guthaben zählen mit ihrem Nennwert, aber nur, wenn du sie auch einlöst. Ein Lounge-Besuch zählt mit {eur(A["lounge_eur"])} €{'. Manche Karten gelten nur für die Lounges am Flughafen Wien, dort zählen nur deine Besuche in Wien' if any(wien_only(x) for x in X.values()) else ''}. Punkte und Meilen zählen mit 1 Cent. Die Reiseversicherung zählt mit dem Preis einer vergleichbaren eigenen {K.t("jahrespolizze")}: {", ".join(f"{K.TIER[int(k)][1]} {eur(v)} €" for k, v in A["vers"].items() if int(k) > 0)}. Abos zählen nur, wenn du sie sonst selbst bezahlen würdest, und zwar mit dem günstigsten regulären Tarif des Anbieters, Jahresabos auf den Monat umgerechnet (Stand {K.dmy(A.get("abos_stand") or K.L["stand"])}). Abos ohne festen Preis zählen nicht. Willkommensboni gelten nur im ersten Jahr und bleiben deshalb außen vor.</p></div>
<h2>Fragen und Antworten</h2><div class="faq">{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in fq)}</div>
</main>
{K.footer(P)}'''
    K.write(rel, K.head(t, d, rel, P, ld, alt=K.alt_links(rel.replace(land + '/', 'at/', 1), rel.replace(land + '/', 'de/', 1)) if load('de' if land == 'at' else 'at') else None) + body.replace('</body>', script(P) + '\n</body>'))
    return rel

def top_block(land, cards, X, A):
    top = sorted([c for c in cards if (c['fee'] or 0) >= TOP], key=lambda c: -(c['fee'] or 0))
    names = ', '.join(c['titel'].replace('American Express', 'Amex') for c in top[:3])
    return (f'<!--lohnt--><a class="catcard top" href="lohnt-sich/"><span class="ct">Top-Karten</span><b>Premiumkarten: hohe Gebühr, viele Vorteile</b>'
            f'<span>{E(names)}{" und mehr" if len(cards) > 3 else ""}: ab wann sie sich lohnen</span><small>{len(cards)} Karten · ansehen →</small></a><!--/lohnt-->')

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
        for c in cards:
            f = R + f'{land}/kreditkarten/{c["slug"]}/index.html'; t = open(f).read()
            t = re.sub(r'<!--lohnt-->.*?<!--/lohnt-->', '', t, flags=re.S)
            t = t.replace('</section>\n  <nav class="secnav"', f'</section>\n  <!--lohnt--><p class="note" style="margin:-4px 0 14px"><a class="lnk" href="../bestenlisten/lohnt-sich/{c["slug"]}/">Ab wann lohnt sich die Karte? {E(short(c, X[c["slug"]], A))} →</a></p><!--/lohnt-->\n  <nav class="secnav"', 1)
            open(f, 'w').write(t)
        f = R + f'{land}/kreditkarten/bestenlisten/index.html'; s = open(f).read()
        s = re.sub(r'<!--lohnt-->.*?<!--/lohnt-->', '', s, flags=re.S)
        s = s.replace('<div class="catgrid">', '<div class="catgrid">' + top_block(land, cards, X, A), 1)
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
