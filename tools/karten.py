# Kreditkartenvergleich Österreich und Deutschland: erzeugt alle Karten-, Listen-, Anbieter- und Bestenlisten-Seiten.
# Daten: daten/at/*.json (Österreich) und de-recherche/*.json + overrides.py (Deutschland).
# Jede Karte hat ein eigenes Prüfdatum ("geprueft", JJJJ-MM-TT); es steht auf der Seite, im Schema und in der Sitemap.
import json,glob,os,re,html,sys,datetime,shutil
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from score import score,note,eur,pct,cash200,TIER
SP=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(SP,'..','public')+'/'
E=lambda s: html.escape(str(s)) if s is not None else ''
TODAY=datetime.date.today().isoformat()
def slug(s):
    s=s.lower().replace('é','e').replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss').replace('&','und').replace('+','plus')
    return re.sub(r'[^a-z0-9]+','-',s).strip('-')
def dmy(iso): y,m,d=iso.split('-'); return f'{d}.{m}.{y}'
def de1(x): return f'{x:.1f}'.replace('.',',')

# ---------- Länder ----------
LANDS={
 'de':dict(code='de',name='Deutschland',lang='de-DE',locale='de_DE',cash='abheben',Cash='Bargeld abheben',cashq='Kann ich kostenlos Bargeld abheben?',
           bon='Schufa',bonrow='Bonitätsprüfung (Schufa)',bonstep='in Deutschland meist bei der Schufa',ident=('Identität bestätigen','Meist per Video-Ident oder Online-Ausweis.'),
           aktiv='Die Karte kommt per Post, oft kannst du sie vorher schon digital im Smartphone nutzen.',
           card_title=lambda c:f'{c["titel"]} in Deutschland 2026 | Finvallo'),
 'at':dict(code='at',name='Österreich',lang='de-AT',locale='de_AT',cash='beheben',Cash='Bargeld beheben',cashq='Kann ich gratis Bargeld beheben?',
           bon='KSV1870',bonrow='Bonitätsprüfung',bonstep='in Österreich meist beim KSV1870',ident=('Ausweis zeigen','Deine Identität wird geprüft, meist per Video-Ident.'),
           aktiv='Die Karte kommt per Post, danach schaltest du sie frei.',
           card_title=lambda c:f'{c["titel"]} im Vergleich 2026 | Finvallo'),
}
L=LANDS['de']
def use(land): global L; L=LANDS[land]
RESERVED={'anbieter','bestenlisten','alle','business','methodik','rechner'}

# ---------- Daten laden ----------
def load_de():
    cards=[]
    for f in sorted(glob.glob(SP+'/de-recherche/[A-G].json')):
        try: cards+=json.load(open(f))
        except Exception as e: print('FEHLER',f,e)
    if os.path.exists(SP+'/de-recherche/de_cards.json'): cards+=json.load(open(SP+'/de-recherche/de_cards.json'))
    out={}
    import overrides
    for c in cards:
        if c.get('status','aktiv')!='aktiv': continue
        overrides.apply(c)
        c.setdefault('art','Privat'); c.setdefault('ex',{}); c.setdefault('sek',[]); c.setdefault('geprueft','2026-10-12')
        c['titel']=overrides.title(c,slug); c['slug']=slug(c['titel']); c['land']='de'
        if c['slug'] in out: print('DOPPELT',c['slug']); continue
        out[c['slug']]=c
    return list(out.values())
def load_at():
    cs=[c for c in json.load(open(SP+'/daten/at/karten.json')) if c.get('status','aktiv')=='aktiv']
    for c in cs:
        c.setdefault('ex',{}); c.setdefault('sek',[]); c.setdefault('geprueft','2026-10-11'); c['land']='at'
    return cs
def load(land='de'): return load_de() if land=='de' else load_at()
# Apple Pay / Google Pay je Anbieter (daten/at/anbieter.json, Feld wallet). Kartenfeld pay bleibt der Schalter:
# pay=None → keine Angabe, pay=False → nein; bei pay=True entscheidet der Anbieter-Eintrag, ob „Apple Pay & Google Pay“ oder nur eines steht.
_WALLET={}
def wallet(p,land='at'):
    if land not in _WALLET:
        try:
            if land=='at': _WALLET[land]={k:(v.get('wallet') or {}) for k,v in json.load(open(SP+'/daten/at/anbieter.json')).items()}
            else: _WALLET[land]=json.load(open(SP+'/daten/de/wallet.json')).get('wallet') or {}
        except Exception: _WALLET[land]={}
    return _WALLET[land].get(p) or {}
def wallet_text(c):
    """Badge-Text: nur wenn mindestens ein Dienst belegt ist."""
    if not c.get('pay'): return None
    w=wallet(c.get('p'),c.get('land') or 'at')
    if not w: return 'Apple Pay & Google Pay'
    a,g=w.get('apple'),w.get('google')
    if a and g: return 'Apple Pay & Google Pay'
    if a: return 'Apple Pay'+(' (Google Pay unklar)' if g is None else '')
    if g: return 'Google Pay'+(' (Apple Pay unklar)' if a is None else '')
    return None
def wallet_row(c,b,na):
    """Zeile „Apple / Google Pay“ auf der Kartenseite."""
    w=wallet(c.get('p'),c.get('land') or 'at')
    if not w and c.get('pay') and c.get('payText'): return E(c['payText'])
    if w:
        t=wallet_text(c)
        if t: return E(t)
        a,g=w.get('apple'),w.get('google')
        if a is False and g is False: return 'nein'
        if a is False and g is None: return 'Apple Pay nein, Google Pay unklar'
        return 'unklar'
    return b(c.get('pay')) if c.get('pay') is not None else na
def providers(land,cards):
    P=json.load(open(SP+'/daten/at/anbieter.json')) if land=='at' else {}
    out={}
    for c in cards:
        p=out.setdefault(c['p'],dict(P.get(c['p']) or {}))
        p.setdefault('name',c['anbieter']); p.setdefault('web',None)
        if not p.get('web'): p['web']=c.get('quelle')
    return out

# ---------- Texte ----------
STAR='M12 2.5l2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 17.4l-5.9 3.1 1.2-6.5L2.5 9.4l6.6-.9z'
UID=[0]
def stars(v):
    out=''
    for i in range(5):
        f=max(0,min(1,(v or 0)-i))
        if f>=.75: out+=f'<svg viewBox="0 0 24 24"><path d="{STAR}" fill="var(--star)"></path></svg>'
        elif f>=.25:
            UID[0]+=1; out+=f'<svg viewBox="0 0 24 24"><defs><linearGradient id="dg{UID[0]}"><stop offset="50%" stop-color="var(--star)"></stop><stop offset="50%" stop-color="var(--star-off)"></stop></linearGradient></defs><path d="{STAR}" fill="url(#dg{UID[0]})"></path></svg>'
        else: out+=f'<svg viewBox="0 0 24 24"><path d="{STAR}" fill="var(--star-off)"></path></svg>'
    return f'<span class="st" aria-hidden="true">{out}</span>'
def starrow(c):
    if c.get('stars') is None: return f'<div class="stars">{stars(0)} <span class="nt nr">Nicht bewertet · zu wenige bestätigte Daten</span></div>'
    return f'<div class="stars">{stars(c["stars"])} <b>{de1(c["stars"])}</b> <span class="nt">{c["note"]}</span></div>'
def kcls(c):
    if c['klasse']=='Premium': return 'k-Premium'
    if c['typ'] in ('Debit','Prepaid'): return 'k-Debit'
    return {'Gold':'k-Gold','Std':'k-Std','Basis':'k-Basis'}.get(c['klasse'],'k-Std')
def netzshort(c): return (c.get('netz') or '').upper().replace('VISA/MASTERCARD','VISA / MC').replace('AMERICAN EXPRESS','AMEX')
def face(c,cls=''):
    return f'<div class="face {kcls(c)}{cls}" aria-hidden="true"><span class="pn">{E(c["anbieter"])}</span><span class="chipc"></span><span class="nw">{E(netzshort(c))}</span></div>'
def feeT(c):
    f=c.get('fee')
    if f is None: return 'unbekannt'
    return 'kostenlos' if f==0 else f'{eur(f)} € pro Jahr'
def fxT(c):
    if c.get('fx') is None: return c.get('fxText') or 'unbekannt'
    return '0 %' if c['fx']==0 else (c.get('fxText') or pct(c['fx']))
def cashT(c):
    t=c.get('cashText')
    if t: return t
    v=cash200(c.get('cash'))
    return 'unbekannt' if v is None else 'kostenlos' if v==0 else 'begrenzt kostenlos' if v=='fn' else f'{eur(v)} € für 200 €' if isinstance(v,float) else 'kostenlos, aber verzinst'
def cash_sentence(c):
    t=cashT(c)
    if t.lower()=='kostenlos': return f'{L["Cash"]} kostet 0 %.'
    if re.match(r'^(\d|ca\.|Inland\b)',t): return f'{L["Cash"]} kostet {t}.'
    return f'{L["Cash"]}: {t}.'
def zinsT(c):
    if c.get('soll') and c.get('effz'): return f'{pct(c["soll"])} Soll / {pct(c["effz"])} effektiv'
    if c.get('effz'): return f'{pct(c["effz"])} effektiv'
    return c.get('zins')
TYPLAB={'Kreditkarte':'Kreditkarte mit Teilzahlung','Charge':'Charge-Karte','Debit':'Debitkarte','Prepaid':'Prepaid-Karte'}
TOPICS=[('girokonto','konto beim anbieter','geschäftskonto','hausbank'),('reiseversicherung','versicherungen'),
        ('fremdwährungsgebühr','auslandseinsatz','fremdwährungskosten'),('jahresgebühr',),('membership rewards',),
        ('unbegrenzt gültig','verfallen nicht'),('wolt+',),('^bargeld','^weltweit kostenlos bargeld')]
def dedupe(xs):
    """Doppelte Punkte entfernen: gleich nach Normalisierung (Kleinschreibung, ohne Satzzeichen) oder gleiches Thema mit gleicher Aussage."""
    out=[]; seen=set(); topics={}; keys=set(); pcs=set()
    for x in xs:
        n=re.sub(r'[^\wäöüß%€ ]','',x.lower()); n=re.sub(r'\s+',' ',n).strip()
        # R7.3: Stoppwörter weg (Karten, pro, je, …) und die ersten 25 Zeichen vergleichen
        k=re.sub(r'\s+',' ',re.sub(r'karten|\bpro\b|\bje\b|…','',n)).strip()[:25]
        pc=re.match(r'(\d+(?: ?\d+)?) ?% (cashback|rückvergütung|umsatzrückvergütung)',n)
        if pc and pc.group(0) in pcs: continue
        if pc: pcs.add(pc.group(0))
        if n in seen or any(k.startswith(o) or o.startswith(k) for o in keys if min(len(k),len(o))>=15) or any(n in o or o in n for o in seen if len(o)>12 and len(n)>12): continue
        keys.add(k)
        t=next((i for i,ws in enumerate(TOPICS) if any(re.search(re.escape(w).replace('\\^','^'),x.lower()) for w in ws)),None)
        if t is None and re.search(r'lastschrift|nicht abgebucht',x.lower()):
            if 'abbuchung' in topics: continue
            topics['abbuchung']=x
        if t is None and re.search(r'teilzahlung ist teuer|hoher zins',x.lower()):
            if 'zins' in topics: continue
            topics['zins']=x
        neg=bool(re.match(r'(keine?|nur|ohne|0 €|0 %)(\b|\s)',x.lower()))
        if t is not None and (t,neg) in topics: continue
        if t is not None: topics[(t,neg)]=x
        seen.add(n); out.append(x)
    return out
PRO_NEIN_OK=('Keine Jahresgebühr','Keine Fremdwährungsgebühr','Kein Girokonto','Keine Bonitätsprüfung','Kein Mindestumsatz')
def not_pro(x):
    """Punkt beginnt mit Kein/Keine und ist keine echte Stärke (z. B. „Kein Cashback …“)."""
    if not re.match(r'Keine?\b',x) or x.startswith(PRO_NEIN_OK): return False
    # „Kein Fremdwährungsentgelt“, „Keine Abhebegebühr“, „Kein neues Girokonto nötig“ sind Stärken
    return not re.search(r'gebühr|entgelt|schufa|bonität|girokonto|vertrag nötig|mindestumsatz',x.lower())
def pros(c):
    p=[]
    f=c.get('fee')
    if f==0: p.append('Keine Jahresgebühr' + (f' ({c["feeBis"]})' if c.get('feeBis') else ''))
    elif c.get('fee1')==0 and f: p.append(f'Im 1. Jahr 0 € statt {eur(f)} €')
    if c.get('fx')==0: p.append('Keine Fremdwährungsgebühr' + (' bis zur Freigrenze' if c.get('fxLimit') else ''))
    elif c.get('fx') is not None and c['fx']<=1.5: p.append(f'Niedrige Fremdwährungskosten ({fxT(c)})')
    v=cash200(c.get('cash'))
    if v==0: p.append('Bargeld ohne Automatengebühr')
    elif v=='fn': p.append('Einige Abhebungen pro Monat ohne Gebühr')
    if (c.get('tier') or 0)>=2: p.append(TIER[c['tier']][1])
    if c.get('cbText') and c['ex'].get('cb'): p.append(re.split(r';|\. ',c['cbText'])[0].rstrip('.'))   # Kurzfassung, Details stehen in der Konditionstabelle
    if c['ex'].get('lg') and c.get('lgText'): p.append(c['lgText'])
    if c['ex'].get('credits') and c.get('creditsText'): p.append(c['creditsText'])
    if c.get('giro') is False: p.append('Kein Girokonto beim Anbieter nötig')
    if c.get('auto') and c['typ']=='Kreditkarte': p.append('Volle Abbuchung per Lastschrift möglich')
    if c.get('auto') and c['typ']=='Charge' and c['land']=='at': p.append('Automatischer Rechnungsausgleich per Lastschrift')
    for x in c.get('extra') or []:
        if c.get('feeBis') and re.match(r'Gratis bis',x): continue   # steht schon bei der Jahresgebühr
        if x not in p: p.append(x)
    return p[:9]
def cons(c):
    k=[]
    if c.get('auto') is False and c['typ'] in ('Kreditkarte','Charge'): k.append('Die Rechnung wird nicht abgebucht, du musst sie selbst pünktlich überweisen')
    z=zinsT(c)
    if c['typ']=='Kreditkarte' and z: k.append(f'Teilzahlung ist teuer: {z}')
    if c.get('cashInterest') or cash200(c.get('cash'))=='fi': k.append('Bargeld wird ab dem Abhebungstag verzinst')
    if (c.get('fee') or 0)>=150: k.append(f'Hohe Jahresgebühr ({eur(c["fee"])} €)')
    if c.get('fx') is not None and c['fx']>=1.75: k.append(f'Fremdwährungsgebühr: {fxT(c)}')
    v=cash200(c.get('cash'))
    if isinstance(v,float) and v>=3: k.append(f'Bargeld am Automaten kostet {cashT(c)}')
    if c.get('giro'): k.append('Nur mit Konto beim Anbieter' + (f' ({c["konto"]})' if c.get('konto') else ''))
    if c.get('tier')==0 and (c.get('fee') or 0)>0: k.append('Keine Reiseversicherung inklusive')
    if 'American Express' in (c.get('netz') or ''): k.append('American Express wird seltener akzeptiert als Visa oder Mastercard')
    if c['typ'] in ('Debit','Prepaid'): k.append('Bei Kautionen für Mietwagen oder Hotel oft abgelehnt')
    for x in c.get('cons_extra') or []:
        if x not in k and not (('Akzeptanz' in x) and any('akzeptiert' in y for y in k)): k.append(x)
    return k[:7]
def feats(c):
    t=[]
    if c.get('fx')==0: t.append(('g','Kostenlos im Ausland'))
    if cash200(c.get('cash'))==0: t.append(('b','Gratis Bargeld'))
    elif cash200(c.get('cash'))=='fn': t.append(('b','Bargeld begrenzt gratis'))
    if (c.get('tier') or 0)>=1: t.append(('p','Reiseversicherung'))
    if wallet_text(c): t.append(('a',E(wallet_text(c))))
    if c['ex'].get('cb'): t.append(('g','Cashback / Punkte'))
    if c['ex'].get('ml'): t.append(('p','Meilen'))
    if c['ex'].get('lg'): t.append(('a','Lounge'))
    if c.get('fee')==0: t.append(('g',f'Ohne Jahresgebühr {c["feeBis"]}' if c.get('feeBis') else 'Dauerhaft ohne Jahresgebühr'))
    return ''.join(f'<span class="{a}">{b}</span>' for a,b in t)
def summary(c):
    s=f'Die {c["titel"]} ist eine {TYPLAB.get(c["typ"],c["typ"])} für Kunden in {L["name"]}. '
    f=c.get('fee')
    if f==0: s+='Sie hat keine Jahresgebühr. '
    elif f is not None: s+=f'Sie kostet {eur(f)} € pro Jahr'+(f', im ersten Jahr {eur(c["fee1"])} €' if c.get('fee1') is not None and c['fee1']!=f else '')+'. '
    s+= 'Zahlungen in fremder Währung kosten nichts extra. ' if c.get('fx')==0 else (f'Zahlungen in fremder Währung kosten {fxT(c)}. ' if c.get('fx') is not None else '')
    if cashT(c)!='unbekannt': s+= cash_sentence(c)+' '
    if c.get('tier') is not None: s+= f'Reiseversicherung: {TIER[c["tier"]][1]}. '
    if c['ex'].get('lg') and c.get('lgText'): s+=f'Lounge: {c["lgText"]}. '
    return s
def offer(c,big=False):
    o=c.get('offer')
    if not o: return ''
    end=o.get('end')
    if end:
        try:
            d,m,y=end.split('.')
            if f'{y}-{m}-{d}'<TODAY: return ''
        except ValueError: pass
    f,f1=c.get('fee'),c.get('fee1')
    if f and f1 is not None and f1<f:
        head='1. Jahr gratis' if f1==0 else f'1. Jahr nur {eur(f1)} €'
        rest=[x for x in (o.get('text') or '').split(' · ')[1:]]
        text=' · '.join([f'statt {eur(f)} € pro Jahr']+list(dict.fromkeys(rest))); save=round(f-f1,2)
    else: head,text,save=o.get('head'),o.get('text'),o.get('save')
    if not head: return ''
    return (f'<div class="offer{" big" if big else ""}"><div class="otop"><span class="olabel">🎁 Willkommensangebot</span>{f"<span class=oend>befristet bis {E(end)}</span>" if end else ""}</div>\n'
            f'  <b>{E(head)}</b><span>{E(text)}</span>{f"<span class=osave>Du sparst {eur(save)} €</span>" if save else ""}{f"<span class=osave>Wert {E(o["value"])}</span>" if o.get("value") else ""}\n'
            f'  {f"<small>{E(o["note"])}</small>" if o.get("note") and big else ""}</div>')

# ---------- Bewertung ----------
def _norm(t): return re.sub(r'\s+',' ',re.sub(r'[^\wäöüß%€ ]','',(t or '').lower().replace(',',''))).strip()
def sammel_dedupe(c,pros):
    """Punkte, die nur wiederholen, was im Feld „Sammeln“ (cbText/earnText) steht, nicht noch einmal als Vorteil zeigen."""
    f=_norm((c.get('cbText') or '')+' '+(c.get('earnText') or ''))
    if not f: return pros
    out=[]
    for x in pros:
        n=_norm(x)
        lead=re.match(r'\+?(\d+ ?(?:%|€|meilen?|punkte?|revpoints?)\b(?: pro \d+ ?€)?)',n)
        if n and (n in f or (lead and lead.group(1) in f) or (re.search(r'verfallen nicht|unbegrenzt gültig',n) and re.search(r'verfallen nicht|unbegrenzt gültig',f))): continue
        out.append(x)
    return out
def ratecards(cards):
    for c in cards:
        c['ex'].setdefault('offer',bool(c.get('offer') or (c.get('fee1')==0 and c.get('fee'))))
        sc=score(c); c['score']=sc; c['stars']=sc['stars']; c['note']=note(sc['stars'])
        pr=pros(c); neg=[x for x in pr if not_pro(x)]
        c['pros']=sammel_dedupe(c,dedupe([x for x in pr if not not_pro(x)])); c['cons']=dedupe(cons(c)+neg)
    priv=[c for c in cards if c['art']=='Privat' and c['stars'] is not None and not c.get('nurfuer')]
    priv.sort(key=lambda c:(-c['stars'],c['fee'] if c['fee'] is not None else 1e9,c['titel'].lower()))
    for c in cards: c['rank']=None
    for i,c in enumerate(priv): c['rank']=i+1
    return priv

# ---------- HTML-Grundgerüst ----------
PAIR={}
def pair_rel(c):
    o=PAIR.get((c['land'],c['slug']))
    return f'{"de" if c["land"]=="at" else "at"}/kreditkarten/{o}/' if o else None
def alt_links(at_rel,de_rel): return f'\n<link rel="alternate" hreflang="de-AT" href="https://finvallo.com/{at_rel}"><link rel="alternate" hreflang="de-DE" href="https://finvallo.com/{de_rel}">'
def alt_for(rel,other):
    if not other: return None
    return alt_links(rel,other) if L['code']=='at' else alt_links(other,rel)
def head(title,desc,canon,P,ld,alt=None):
    css=open(R+'index.html').read(); v=re.search(r'site\.css\?v=([a-z0-9]+)',css).group(1); fv=re.search(r'favicon\.svg\?v=([a-z0-9]+)',css).group(1)
    return f'''<!doctype html>
<html lang="{L['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1">
<link rel="canonical" href="https://finvallo.com/{canon}">{alt or ''}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Finvallo">
<meta property="og:locale" content="{L['locale']}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="https://finvallo.com/{canon}">
<meta property="og:image" content="https://finvallo.com/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0f1720">
<meta name='impact-site-verification' value='395412e1-70ac-412c-9ce9-5e53d7b5e5ef'>
<meta name="author" content="Finvallo-Redaktion">
<link rel="icon" href="{P}assets/favicon.svg?v={fv}" type="image/svg+xml">
<link rel="preload" href="{P}assets/fonts/figtree-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{P}assets/site.css?v={v}">
<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False)}</script>
</head>
<body>
'''
def graph(canon,title,desc,crumbs,extra=None,date=None):
    g=[{"@type":"Organization","@id":"https://finvallo.com/#org","name":"Finvallo","url":"https://finvallo.com/","logo":"https://finvallo.com/assets/logo.svg"},
       {"@type":"WebSite","@id":"https://finvallo.com/#website","name":"Finvallo","url":"https://finvallo.com/","inLanguage":"de","publisher":{"@id":"https://finvallo.com/#org"}},
       {"@type":"WebPage","@id":f"https://finvallo.com/{canon}#page","url":f"https://finvallo.com/{canon}","name":title,"description":desc,"inLanguage":L['lang'],"isPartOf":{"@id":"https://finvallo.com/#website"},"dateModified":date or L['stand'],"publisher":{"@id":"https://finvallo.com/#org"}},
       {"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":f"https://finvallo.com/{u}"} for i,(n,u) in enumerate(crumbs)]}]
    if extra: g+=extra
    return {"@context":"https://schema.org","@graph":g}
def land_div(land,P,at_rel,de_rel):
    return (f'<div class="land" role="group" aria-label="Land wählen"><a href="{P}{at_rel}" hreflang="de-AT" aria-current="{"true" if land=="at" else "false"}" title="Österreich">AT</a>'
            f'<a href="{P}{de_rel}" hreflang="de-DE" aria-current="{"true" if land=="de" else "false"}" title="Deutschland">DE</a></div>')
def HDR(P,rel,other=None):
    import header as H
    me=L['code']; o=other or ('de/' if me=='at' else 'at/')
    at_rel,de_rel=(rel,o) if me=='at' else (o,rel)
    return H.build(rel,P,land_div(me,P,at_rel,de_rel))
def footer(P):
    return f'''<footer>
<span><b>finvallo</b> · Unabhängiger Finanzvergleich für {L['name']}</span>
<span>Stand {dmy(L['stand'])} · Bewertung unabhängig von Provisionen, keine bezahlten Platzierungen · Mit * markierte Links sind Affiliate-Links.</span>
<span>Keine Finanzberatung. Konditionen vor Abschluss beim Anbieter prüfen.</span>
<nav aria-label="Fußzeile"><a href="{P}{L['code']}/kreditkarten/methodik/">So bewerten wir</a><a href="{P}so-verdienen-wir-geld/">So verdienen wir Geld</a><a href="{P}ueber-uns/">Über Finvallo</a><a href="{P}impressum/">Impressum</a><a href="{P}datenschutz/">Datenschutz</a><a href="{P}llms.txt">Für KI-Assistenten</a></nav>
</footer>
</div>
</body>
</html>
'''
def footer_land(land,P):
    old=L['code']; use(land); f=footer(P); use(old); return f
WRITTEN=set()
def write(rel,html_):
    os.makedirs(R+rel,exist_ok=True); open(R+rel+'index.html','w').write(html_); WRITTEN.add(rel)
def ext(u,t=None):
    if not u or not u.startswith('http'): return E(u or '')
    d=re.sub(r'^https?://(www\.)?','',u).split('/')[0]
    return f'<a href="{E(u)}" target="_blank" rel="noopener">{E(t or d)} ↗</a>'
def qa(items): return '<div class="qa">'+''.join(f'<div><h4>{E(x["h"])}</h4><p>{x["t"]}</p></div>' for x in items)+'</div>'

# ---------- Kartenseite ----------
def cond(c):
    r=lambda k,v: f'<div class="r"><span>{k}</span><span>{v}</span></div>'
    b=lambda v: 'ja' if v else 'nein' if v is False else '–'
    na='<span class="mut na">beim Anbieter prüfen</span>'
    out='<div class="cond" style="margin-bottom:14px"><div class="gh">Kosten</div>'
    out+=r('Jahresgebühr',E(feeT(c))+(f' <small class="mut">({E(c["feeNote"])})</small>' if c.get('feeNote') else '') if c.get('fee') is not None else na)
    out+=r('1. Jahr',f'{eur(c["fee1"])} €' if c.get('fee1') is not None else '–')
    out+=r('Willkommensangebot',E(c.get('bonus') or ((c.get('offer') or {}).get('head') if offer(c) else None) or '–'))
    out+=r('Zahlen im Ausland',E(fxT(c)) if (c.get('fx') is not None or c.get('fxText')) else na)
    out+=r(L['Cash'],E(cashT(c)) if cashT(c)!='unbekannt' else na)
    if c.get('konto'): out+=r('Nötiges Konto',E(c['konto']))
    out+='</div><div class="cond" style="margin-bottom:14px"><div class="gh">Bezahlen</div>'
    out+=r('Abrechnung',('sofort vom Konto' if c['typ'] in ('Debit','Prepaid') else 'automatisch per Lastschrift' if c.get('auto') else 'per Überweisung' if c.get('auto') is False else '–'))
    if c.get('autoNote'): out+=r('Hinweis',E(c['autoNote']))
    out+=r('Teilzahlung','möglich' if c['typ']=='Kreditkarte' else 'nein')
    z=zinsT(c)
    if z: out+=r('Effektiver Zins',E(z))
    if c.get('zinsfrei'): out+=r('Zinsfrei',f'bis {c["zinsfrei"]} Tage')
    elif c['typ']=='Charge': out+=r('Zinsfrei','bis zur Abbuchung')
    if c.get('rahmen'): out+=r('Kreditrahmen',E(c['rahmen']))
    out+='</div><div class="cond" style="margin-bottom:14px"><div class="gh">Extras</div>'
    if c.get('earnText'): out+=r('Sammelrate',E(c['earnText']))
    out+=r('Cashback / Punkte',E(c.get('cbText') or ('ja' if c['ex'].get('cb') else 'nein')))
    out+=r('Meilen',b(bool(c['ex'].get('ml'))))
    out+=r('Lounge',E(c.get('lgText') or '–'))
    if c.get('ftText'): out+=r('FastTrack',E(c['ftText']))
    if c.get('creditsText'): out+=r('Guthaben',E(c['creditsText']))
    out+=r('Reiseversicherung',TIER[c['tier']][1] if c.get('tier') is not None else na)
    out+='</div><div class="cond" style="margin-bottom:14px"><div class="gh">Voraussetzungen</div>'
    out+=r('Kartentyp',TYPLAB.get(c['typ'],c['typ']))+r('Kartennetz',E(c.get('netz')) if c.get('netz') else na)
    out+=r('Girokonto beim Anbieter','nötig' if c.get('giro') else 'nicht nötig' if c.get('giro') is False else '–')
    out+=r(L['bonrow'],'ja' if c['typ'] in ('Kreditkarte','Charge') else 'meist nur bei Kontoeröffnung')
    out+=r('Für Kautionen','in der Regel ja' if c['typ'] in ('Kreditkarte','Charge') and 'American' not in (c.get('netz') or '') else 'oft nicht' if c['typ'] in ('Debit','Prepaid') else 'eingeschränkt')
    out+=r('Apple / Google Pay',wallet_row(c,b,na))
    if c.get('herausgeber'): out+=r('Herausgeber',E(c['herausgeber']))
    return out+'</div>'
def scorebox(c,P):
    s=c['score']
    rows=''.join(f'<tr><td><b>{E(p["k"])}</b><br><small class="mut">{E(p["v"])}</small></td><td>{p["w"]} %</td><td style="white-space:nowrap">{stars(p["s"])} {de1(p["s"])}</td></tr>' for p in s['parts'])
    if c.get('stars') is None:
        return f'<div class="box"><h3>Noch keine Gesamtnote</h3><p style="color:var(--muted)">Für eine Gesamtnote brauchen wir die Jahresgebühr und bestätigte Daten in mindestens 5 der 7 Kriterien. Hier fehlen noch Angaben. Fehlende Kriterien zählen mit 2,5 Sternen.</p><div class="tbl" style="margin:14px 0"><table class="sct"><thead><tr><th>Kriterium</th><th>Gewicht</th><th>Sterne</th></tr></thead><tbody>{rows}</tbody></table></div><a class="lnk" href="{P}{L["code"]}/kreditkarten/methodik/">ⓘ So funktioniert das Bewertungssystem</a></div>'
    rows=''.join(f'<tr><td><b>{E(p["k"])}</b><br><small class="mut">{E(p["v"])}</small></td><td>{p["w"]} %</td><td style="white-space:nowrap">{stars(p["s"])} {de1(p["s"])}</td></tr>' for p in s['parts'])
    return f'''<div class="box"><div class="scorehead"><div class="big">{de1(c["stars"])}<small>/5</small></div><div>{stars(c["stars"])}<div style="margin-top:4px"><span class="badge ">{c["note"]}</span></div></div></div>
  <div class="tbl" style="margin:14px 0"><table class="sct"><thead><tr><th>Kriterium</th><th>Gewicht</th><th>Sterne</th></tr></thead><tbody>
  {rows}
  <tr><td><b>Gesamt</b><br><small class="mut">gewichteter Durchschnitt</small></td><td>100 %</td><td><b>{de1(c["stars"])}</b></td></tr></tbody></table></div><a class="lnk" href="{P}{L['code']}/kreditkarten/methodik/">ⓘ So funktioniert das Bewertungssystem</a></div>'''
def similar(c,cards):
    pool=[x for x in cards if x is not c and x['art']==c['art'] and x.get('stars') is not None]
    pool.sort(key=lambda x:(x['typ']!=c['typ'],abs((x['fee'] or 0)-(c['fee'] or 0))>60,-(x['stars'] or 0)))
    return pool[:4]
def cash_answer(c):
    t=cashT(c)
    if t=='unbekannt': return 'Das konnten wir noch nicht bestätigen.'
    if t.lower()=='kostenlos': return f'Ja, {L["Cash"].lower().replace("bargeld","Bargeld")} kostet 0 %.'
    if re.match(r'^(\d|ca\.|Inland\b)',t): return f'{L["Cash"]} kostet {t}.'
    return f'Die Bedingungen: {t}.'
def lieferzeit(c):
    """Lieferzeit aus den Vorteilen/Extras des Datensatzes (z. B. „Lieferung in ca. 7 Werktagen“), sonst None."""
    for x in (c.get('extra') or [])+(c.get('pros') or []):
        m=re.search(r'(?:Lieferung|Plastikkarte|Karte kommt)[^;,.]*?((?:ca\. )?\d+(?:[–-]\d+)? (?:Werktagen|Werktage|Tagen|Tage))',x)
        if m: return m.group(1).replace('Werktage','Werktagen').replace(' Tage',' Tagen') if not m.group(1).endswith('n') else m.group(1)
    return None
def ins_limits(c):
    """Einschränkungen der Reiseversicherung aus dem Versicherungstext (nur wörtlich belegte Sätze)."""
    txt=' '.join([c.get('insText') or '']+[x.get('t','') for x in ((c.get('blocks') or {}).get('ins') or {}).get('items',[])])
    sents=re.split(r'(?<=[.;])\s+',txt)
    hit=[x.strip(' ;') for x in sents if re.search(r'nicht versichert|gilt nicht|nicht für|endet mit|\bkein(?:e|en)? \w*(?:schutz|versicherung)|nur wenn|ausgeschlossen',x,re.I)]
    out=[]
    for h in hit:
        h=h[0].upper()+h[1:]
        if not h.endswith('.'): h+='.'
        if h not in out: out.append(h)
    return out[:3]
def faq(c):
    """Fragen nur, wenn die Antwort mehr sagt als ein Einzelwert der Konditionstabelle (3 bis 6 Fragen, Kartenname in jeder Antwort)."""
    T=c['titel']; q=[]
    # Wer bekommt die Karte?
    w=[]
    if c.get('nurfuer'): w.append(f'Die {T} gibt es nur für bestimmte Kundengruppen: {c["nurfuer"]}.')
    if c['typ'] in ('Kreditkarte','Charge'): w.append(f'Für die {T} prüft {c["anbieter"]} deine Bonität{" beim KSV1870" if c["land"]=="at" else " bei der Schufa"}.')
    if c.get('giro'): w.append(f'Für die {T} brauchst du ein Konto bei {c["anbieter"]}'+(f' ({c["konto"]})' if c.get('konto') else '')+'.')
    elif c.get('giro') is False: w.append(f'Ein Girokonto bei {c["anbieter"]} brauchst du für die {T} nicht, dein bestehendes Konto reicht.')
    w.append(f'Beantragen kannst du sie mit Wohnsitz in {L["name"]}.')
    q.append((f'Wer bekommt die {T}?',' '.join(w)))
    lz=lieferzeit(c)
    if lz: q.append((f'Wie lange dauert es, bis die {T} da ist?',f'Laut {c["anbieter"]} kommt die {T} nach {lz}.'))
    z=zinsT(c)
    if c['typ']=='Kreditkarte' and z:
        q.append(('Was passiert, wenn ich die Rechnung nicht ganz bezahle?',f'Bei der {T} wird der offene Betrag in Raten zurückgezahlt und verzinst: {z}. Stell die Rückzahlung auf 100 %, dann fallen keine Zinsen an.'+(' Die Rechnung wird abgebucht.' if c.get('auto') else ' Du überweist den Betrag selbst, also achte auf den Termin.' if c.get('auto') is False else '')))
    if c['typ'] in ('Kreditkarte','Charge'):
        q.append((f'Kann ich mit der {T} ein Auto mieten oder ein Hotel reservieren?',f'Meist ja. Die {T} ist eine {TYPLAB.get(c["typ"],c["typ"]).replace(" mit Teilzahlung","")} mit Kreditrahmen, die Vermieter und Hotels in der Regel für Kautionen annehmen. Ob die Karte akzeptiert wird'+(' (American Express wird seltener genommen)' if 'American Express' in (c.get('netz') or '') else '')+', prüfst du am besten vorher beim Vermieter.'))
    else:
        q.append((f'Kann ich mit der {T} ein Auto mieten oder ein Hotel reservieren?',f'Oft nicht. Die {T} ist eine {TYPLAB.get(c["typ"],c["typ"])}, und viele Mietwagenfirmen und Hotels verlangen für die Kaution eine echte Kreditkarte. Frag vorher beim Vermieter nach.'))
    lim=ins_limits(c)
    if (c.get('tier') or 0)>0 and lim:
        q.append((f'Was deckt die Reiseversicherung bei der {T} nicht ab?',f'Laut Versicherungsbedingungen der {T}: '+' '.join(lim)))
    kc=[x for x in (c.get('cons') or []) if not x.startswith('Bei Kautionen')][:3]
    if kc:
        q.append((f'Für wen lohnt sich die {T} nicht?',f'Die {T} passt weniger zu dir, wenn dich einer dieser Punkte stört: '+' '.join(x.rstrip('.')+'.' for x in kc)))
    if len(q)<3 and c.get('stars') is not None:
        q.append((f'Wie kommt die Bewertung der {T} zustande?',f'Die {T} bekommt {de1(c["stars"])} von 5 Sternen. Das ist der gewichtete Durchschnitt aus 7 Kriterien, die Aufschlüsselung steht im Abschnitt Bewertung.'))
    if len(q)<3 and c.get('lgText'): q.append((f'Gibt es mit der {T} Lounge-Zugang?',f'Zur {T}: {c["lgText"].rstrip(".")}.'))
    return q[:6]
def who(c):
    a=[]; b=[]
    if c.get('fee')==0 and c.get('fx')==0: a.append('Sie passt zu allen, die ohne Jahresgebühr und ohne Auslandsgebühren zahlen wollen, etwa auf Reisen.')
    elif (c.get('tier') or 0)>=3: a.append('Sie passt zu Vielreisenden, die einen umfassenden Versicherungsschutz und Extras wollen und die Jahresgebühr dafür in Kauf nehmen.')
    elif c['typ'] in ('Debit','Prepaid'): a.append('Sie passt zu allen, die ohne Kreditrahmen bezahlen wollen und die Ausgaben direkt vom Konto abbuchen lassen.')
    elif c.get('fee') is not None and c['fee']<=30: a.append('Sie passt zu allen, die eine günstige Karte für den Alltag und Online-Shopping suchen.')
    elif c.get('stars') is None: a.append('Für eine Empfehlung fehlen uns noch bestätigte Daten.')
    else: a.append('Sie passt zu allen, denen die Leistungen dieser Karte den Preis wert sind.')
    if c['ex'].get('lg'): a.append('Wer oft fliegt, nutzt die enthaltenen Lounge-Besuche.')
    if c['ex'].get('cb') and not re.match(r'(Kein|Nur Partner)',c.get('cbText') or ''):
        t=((c.get('cbText') or '')+' '+(c.get('earnText') or '')).lower()
        geld=bool(re.search(r'cashback|geld zurück|gutschrift|% zurück',t)); pkt=bool(re.search(r'punkt|meile|revpoint|rewards|payback|bonus',t))
        if 'saveback' in t: a.append('Wer gerne spart, bekommt einen Teil der Umsätze in den Sparplan.')
        elif re.search(r'reisebuchung',t) and not (geld or pkt): a.append('Wer über den Partner bucht, bekommt einen Teil des Reisepreises zurück.')
        elif re.search(r'rabatt|rückvergütung|erstattung',t) and not pkt: a.append('Wer gerne sammelt, bekommt Geld zurück.')
        else: a.append('Wer gerne sammelt, bekommt Punkte und Geld zurück.' if geld and pkt else 'Wer gerne sammelt, bekommt Geld zurück.' if geld else 'Wer gerne sammelt, bekommt Punkte oder Meilen.' if pkt else 'Wer gerne sammelt, bekommt Vorteile beim Einkaufen.')
    if c.get('giro'): a.append(f'Am meisten Sinn ergibt sie, wenn du schon Kunde bei {c["anbieter"]} bist.')
    if c['typ']=='Kreditkarte' and not c.get('auto'): b.append('Wenn du Termine leicht vergisst, nimm besser eine Karte mit automatischer Abbuchung. Hier kosten offene Beträge hohe Zinsen.')
    if c['typ']=='Kreditkarte' and c.get('auto'): b.append('Achte darauf, die Rückzahlung auf 100 % zu stellen, sonst fallen Zinsen an.')
    if c['typ'] in ('Debit','Prepaid'): b.append('Für Mietwagen- und Hotelkautionen ist eine echte Kredit- oder Charge-Karte besser.')
    if (c.get('fx') or 0)>=1.75: b.append('Für Reisen außerhalb des Euroraums gibt es günstigere Karten.')
    return a,b
def how(c):
    if c['typ']=='Kreditkarte':
        return f'Die Karte ist eine echte Kreditkarte mit Teilzahlung. Nach der Bonitätsprüfung ({L["bon"]}) bekommst du einen Kreditrahmen{" von "+c["rahmen"] if c.get("rahmen") else ""}. '+('Die Monatsrechnung kann per Lastschrift eingezogen werden. ' if c.get('auto') else 'Die Monatsrechnung zahlst du selbst per Überweisung. ')+f'Zahlst du alles pünktlich, kostet ein Einkauf keine Zinsen{", und du hast bis zu "+str(c["zinsfrei"])+" Tage Zeit" if c.get("zinsfrei") else ""}. Zahlst du nur einen Teil, fallen Zinsen an{", und zwar "+zinsT(c) if zinsT(c) else ""}.'
    if c['typ']=='Charge':
        return 'Die Karte ist eine Charge-Karte: Alle Zahlungen eines Monats werden gesammelt und einmal im Monat '+(f'vom Girokonto bei {c["anbieter"]} abgebucht' if c.get('giro') else 'per Lastschrift abgebucht' if c.get('auto') is not False else 'per Rechnung fällig')+'. Bis dahin zahlst du keine Zinsen.'
    if c['typ']=='Debit':
        return f'Die Karte ist eine Debitkarte: Jede Zahlung wird sofort von deinem Konto bei {c["anbieter"]} abgebucht. Es gibt keinen Kreditrahmen und keine Zinsen, dafür lehnen manche Mietwagenfirmen und Hotels sie für Kautionen ab.'
    return 'Die Karte ist eine Prepaid-Karte: Du lädst Guthaben auf und kannst nur so viel ausgeben, wie darauf ist.'
def steps(c):
    if c.get('giro'):
        st=[('Konto prüfen',f'Hast du noch kein Girokonto bei {c["anbieter"]}, eröffnest du zuerst eines.'),('Karte beantragen','Du beantragst die Karte im Online-Banking, in der App oder in der Filiale.'),
            ('Bonität prüfen lassen',f'Die Bank prüft deine Bonität{" und legt den Kartenrahmen fest" if c["typ"] in ("Kreditkarte","Charge") else ""}.'),('Karte aktivieren','Die Karte kommt per Post, und du schaltest sie in der App oder im Online-Banking frei.')]
    else:
        st=[('Online-Antrag ausfüllen',f'Du gibst deine Daten, deinen Job und deine Adresse in {L["name"]} an.'),L['ident'],
            ('Bonität prüfen lassen',f'{c["anbieter"]} fragt deine Bonität ab, {L["bonstep"]}{", und legt den Rahmen fest" if c["typ"] in ("Kreditkarte","Charge") else ""}.'),('Karte aktivieren',L['aktiv'])]
    return ''.join(f'<div class="step"><span class="no">{i+1}</span><div><b>{E(a)}</b><p>{E(b)}</p></div></div>' for i,(a,b) in enumerate(st))
def ins_block(c):
    b=(c.get('blocks') or {}).get('ins') or {}
    if b.get('items'):
        return (f'\n  <p class="note" style="margin-top:-4px">{b["note"]}</p>' if b.get('note') else '\n  ')+qa(b['items'])+(f'<p class="src" style="margin-top:8px">{b["src"]}</p>' if b.get('src') else '')
    if c.get('insText'):
        return f'<div class="qa"><div><h4>Was ist versichert?</h4><p>{E(c["insText"])}</p></div></div>'+(f'<p class="src" style="margin-top:8px">Quelle: {ext(c["insQuelle"])}</p>' if c.get('insQuelle') else '')
    if b.get('info'): return f'\n  <div class="info"><span class="ic">i</span><div><p style="margin:0">{b["info"]}</p></div></div>'
    return '<p>Ohne Aufpreis ist keine Reiseversicherung enthalten.</p>' if c.get('tier')==0 else '<div class="info"><span class="ic">i</span><div><p style="margin:0">Zur Reiseversicherung dieser Karte haben wir keine bestätigten Angaben gefunden. Bitte beim Anbieter prüfen.</p></div></div>'
def card_page(c,cards,nrated,prov):
    code=L['code']; rel=f'{code}/kreditkarten/{c["slug"]}/'; P='../../../'
    t=c.get('seoTitle')
    if not t:
        t=L['card_title'](c)
        if len(t)>65: t=f'{c["titel"]} ({code.upper()}) 2026 | Finvallo'
        if len(t)>65: t=f'{c["titel"]} | Finvallo'
    bits=[('ohne Jahresgebühr' if c.get('fee')==0 else f'{eur(c["fee"])} € pro Jahr' if code=='at' else f'{eur(c["fee"])} € im Jahr') if c.get('fee') is not None else None,
          ('0 % im Ausland' if c.get('fx')==0 else f'{pct(c["fx"]).replace(",00","")} im Ausland') if c.get('fx') is not None else None,
          TIER[c['tier']][1] if c.get('tier') else None]
    d=f'{c["titel"]} in {L["name"]}: {", ".join(x for x in bits if x)}.'+(f' Bewertung {de1(c["stars"])}/5.' if c.get('stars') else '')+' Alle Kosten, Vor- und Nachteile.'
    if len(d)>155: d=d.replace(' Alle Kosten, Vor- und Nachteile.',' Kosten, Vor- und Nachteile.')
    if len(d)>155: d=d.replace(' Kosten, Vor- und Nachteile.','')
    d=fit_desc(d)
    pc=c['pros']; kc=c['cons']; gp=c['geprueft']
    ld_card={"@type":"CreditCard","@id":f"https://finvallo.com/{rel}#card","name":c['titel'],"url":f"https://finvallo.com/{rel}",
      "provider":{"@type":"BankOrCreditUnion","name":c.get('herausgeber') or c['anbieter'],"url":c.get('quelle')},"areaServed":{"@type":"Country","name":L['name']},
      "category":TYPLAB.get(c['typ'],c['typ']),"feesAndCommissionsSpecification":f"Jahresgebühr {feeT(c)}; Fremdwährung {fxT(c)}; Bargeld {cashT(c)}"}
    if c.get('effz'): ld_card['annualPercentageRate']=c['effz']
    if c.get('fee') is not None: ld_card['offers']={"@type":"Offer","price":c['fee'],"priceCurrency":"EUR","description":"Jahresgebühr","availability":"https://schema.org/InStock"}
    if c.get('stars') is not None:
        ld_card['review']={"@type":"Review","author":{"@id":"https://finvallo.com/#org"},"datePublished":gp,"name":f"{c['titel']} im Finvallo-Vergleich","reviewRating":{"@type":"Rating","ratingValue":c['stars'],"bestRating":5,"worstRating":1},
          "positiveNotes":{"@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"name":x} for i,x in enumerate(pc[:5])]},
          "negativeNotes":{"@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"name":x} for i,x in enumerate(kc[:5])]}}
    fq=faq(c)
    ld=graph(rel,t,d,[(L['name'],f'{code}/'),('Kreditkarten',f'{code}/kreditkarten/'),('Alle Karten',f'{code}/kreditkarten/alle/')]+([(c['anbieter'],f'{code}/kreditkarten/anbieter/{c["p"]}/')] if c['p'] in PROVPAGE.get(code,()) else [])+[(c['titel'],rel)],
             [ld_card,{"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in fq]}],date=gp)
    rk=f', Platz {c["rank"]} von {nrated} bewerteten Privatkarten in {L["name"]}' if c.get('rank') else ''
    glance=summary(c)+(f'Finvallo bewertet sie mit {de1(c["stars"])} von 5 Sternen{rk}. ' if c.get('stars') else '')+f'Stand: {dmy(gp)}.'
    a,b=who(c)
    sim=similar(c,cards)
    simtbl=''.join(f'<tr><td><a class="lnk" href="../{x["slug"]}/">{E(x["titel"])}</a></td><td>{eur(x["fee"]) if x.get("fee") is not None else "–"} €</td><td>{E(fxT(x))}</td><td>{E(cashT(x))}</td><td style="white-space:nowrap">{de1(x["stars"])} ★ {x["note"]}</td></tr>' for x in sim[:3])
    mini=''.join(f'<a class="mini-card" href="../{x["slug"]}/">{face(x)}<b>{E(x["titel"])}</b>{starrow(x)}<span>{eur(x["fee"]) if x.get("fee") is not None else "–"} € im Jahr</span></a>' for x in sim)
    bl=c.get('blocks') or {}
    extras=f'\n  <h2>Extras im Detail</h2>{qa(bl["extras"])}' if bl.get('extras') else ''
    fees=f'\n  <h2>Weitere Gebühren von {E(c["anbieter"])}</h2>{qa(bl["fees"])}' if bl.get('fees') else ''
    best='<span class="reco">★ Bestbewertet</span>' if c.get('rank')==1 else ''
    if c['slug'] in BEST: bb=BEST[c['slug']]; best+=f'<a class="tag best" href="../bestenlisten/{bb[2]}/">🏆 Platz {bb[0]+1} für {E(bb[1])} ({de1(bb[3])} ★ in dieser Kategorie)</a>'
    pv=prov.get(c['p']) or {}
    f1=f'<span class="note">Im 1. Jahr {eur(c["fee1"])} €</span>' if c.get('fee1') is not None and c.get('fee') and c['fee1']!=c['fee'] else ''
    other=pair_rel(c)
    body=f'''{HDR(P,rel,other or ("de" if code=="at" else "at")+"/kreditkarten/")}
<div class="wrap"><main id="app">
<div class="crumb"><span><a href="../alle/">Alle Karten</a> › {f'<a href="../anbieter/{c["p"]}/">{E(c["anbieter"])}</a>' if c['p'] in PROVPAGE.get(code,()) else E(c["anbieter"])}</span><span class="ok">✓ Geprüft am {dmy(gp)}</span></div>
  <div class="dh">{face(c)}<div style="min-width:0"><div class="tags">{best}<span class="tag typ">{TYPLAB.get(c["typ"],c["typ"])}</span><span class="by">von {E(c["anbieter"])}</span></div>
    <h1>{E(c["titel"])}</h1>{starrow(c)}</div></div>
  <div class="feat">{feats(c)}</div>{f'<p class="note"><b>Hinweis:</b> {E(c["nurfuer"])}.</p>' if c.get('nurfuer') else ''}
  {offer(c,True)}
  <div class="box feebox"><small>Jahresgebühr</small><span class="big{" good" if c.get("fee")==0 else ""}">{"kostenlos" if c.get("fee")==0 else (eur(c["fee"])+" €") if c.get("fee") is not None else "beim Anbieter prüfen"}</span>{f1}
    <a class="btn primary block" href="{E(c.get("quelle"))}" target="_blank" rel="noopener">Zum Anbieter ↗</a>
    <div class="actrow"><a class="plink" href="{E(c.get("preis") or c.get("quelle"))}" target="_blank" rel="noopener">{"Preise &amp; Gebühren (PDF) ↗" if (c.get("preis") or "").lower().endswith(".pdf") else "Konditionen beim Anbieter ↗"}</a></div></div>
  <section class="facts box glance" aria-label="Auf einen Blick"><h2 style="margin-top:0">Auf einen Blick</h2><div class="prose"><p>{E(glance)}</p></div></section>
  <nav class="secnav" aria-label="Abschnitte"><a href="#s-ueb" data-sec="s-ueb" class="on">Überblick</a><a href="#s-kond" data-sec="s-kond">Konditionen</a><a href="#s-vers" data-sec="s-vers">Versicherung</a><a href="#s-bew" data-sec="s-bew">Bewertung</a><a href="#s-faq" data-sec="s-faq">Fragen</a></nav>
  <section id="s-ueb">
  <h2>Vorteile und Nachteile</h2>
  <div class="pc"><div class="box pro"><h3>Das spricht dafür</h3>{'<ul class="checks">'+"".join(f"<li>{E(x)}</li>" for x in pc)+'</ul>' if pc else '<p class="note">Noch keine bestätigten Vorteile.</p>'}</div>
  <div class="box con"><h3>Das spricht dagegen</h3>{'<ul class="checks neg">'+"".join(f"<li>{E(x)}</li>" for x in kc)+'</ul>' if kc else '<p class="note">Keine bekannten Nachteile.</p>'}</div></div>
  <h2>Für wen ist die Karte geeignet?</h2><div class="info"><span class="ic">i</span><div><p style="margin:0 0 8px">{E(" ".join(a))}</p>{"<p style='margin:0'>"+E(" ".join(b))+"</p>" if b else ""}</div></div>
  <h2>So funktioniert die Karte</h2><div class="prose"><p>{E(how(c))}</p></div>
  </section>
  <section id="s-kond"><h2>Konditionen im Überblick</h2>{cond(c)}{extras}{fees}
  </section>
  <section id="s-vers"><h2>Reiseversicherung</h2>{ins_block(c)}
  </section>
  <section id="s-bew"><h2>So kommt die Bewertung zustande</h2>{scorebox(c,P)}
  {f"<h2>Im Vergleich mit ähnlichen Karten</h2><div class='tbl wide'><table><thead><tr><th>Karte</th><th>Jahresgebühr</th><th>Zahlung Ausland</th><th>Bargeld</th><th>Bewertung</th></tr></thead><tbody>{simtbl}</tbody></table></div>" if simtbl else ""}
  <h2>So beantragst du die Karte</h2><p class="note" style="margin-top:-6px">Das ist der übliche Ablauf. Die Details legt der Anbieter fest.</p>
  <div class="steps">{steps(c)}</div>
  </section>
  <section id="s-faq"><h2>Fragen und Antworten</h2><div class="faq">{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q,a in fq)}</div></section>
  {f"<h2>Hinweis der Redaktion</h2><p class='note'>{E(c['notiz'])}</p>" if c.get('notiz_public') else ""}
  {f"<h2>Ähnliche Karten</h2><div class='grid2'>{mini}</div>" if mini else ""}
  <div class="box" style="margin-top:22px"><h3>Über {E(c["anbieter"])}</h3>{f'<p style="color:var(--muted);margin:0 0 12px">{E(pv["text"])}</p>' if pv.get("text") else ""}{f'<a class="lnk" href="../anbieter/{c["p"]}/">Alle Karten von {E(c["anbieter"])} →</a>' if c['p'] in PROVPAGE.get(code,()) else f'<a class="lnk" href="../alle/">Alle Karten nach Anbieter →</a>'}</div>
  <p class="src" style="margin-top:18px">Hauptquelle: {ext(c.get("quelle"))}{" · Preisverzeichnis: "+ext(c.get("preis")) if c.get("preis") and c.get("preis")!=c.get("quelle") else ""}{" ("+E(c["stand"])+")" if c.get("stand") else ""}.</p>
</main>
{footer(P)}'''
    write(rel,head(t,d,rel,P,ld,alt=alt_for(rel,other) if c['art']=='Privat' else None)+body)

# ---------- Listen ----------
def list_item(c,P,base=''):
    v=cash200(c.get('cash'))
    st=lambda good,txt: f'<b class="{ "good" if good else ""}">{E(txt)}</b>'
    fee='–' if c.get('fee') is None else ('€ 0,00' if c['fee']==0 else f'€ {eur(c["fee"])}')
    cash="Kostenlos" if v==0 else "Begrenzt gratis" if v=="fn" else "0 € (verzinst)" if v=="fi" else (c.get('cashText') if c.get('cashText') and len(c['cashText'])<=40 else (eur(v)+" €") if isinstance(v,float) else (c.get('cashText') or "–"))
    rank=f'<span class="rank r{c["rank"]}">{c["rank"]}</span>' if c.get('rank') and c['rank']<=3 else (f'<span class="rank">{c["rank"]}</span>' if c.get('rank') else '')
    earn=c.get('earnText') or (c.get('cbText') if c['ex'].get('cb') else None)
    return f'''<article class="item" id="it-{c.get("id") or c["slug"]}">
    <div class="ihead"><div style="display:flex;gap:10px;align-items:center">{rank}{'<span class="reco">★ Bestbewertet</span>' if c.get('rank')==1 else ''}</div></div>
    <div class="irow">{face(c)}<div style="min-width:0"><h3 class="iname"><a href="{base}{c["slug"]}/">{E(c["titel"])}</a></h3><div class="iprov">{E(c["anbieter"])}</div>{starrow(c)}</div></div>
    <div class="tags">{f'<a class="tag best" href="{base}bestenlisten/{BEST[c["slug"]][2]}/">🏆 Platz {BEST[c["slug"]][0]+1} für {E(BEST[c["slug"]][1])} ({de1(BEST[c["slug"]][3])} ★ in dieser Kategorie)</a>' if c["slug"] in BEST else ''}<span class="tag typ">▭ {E(TYPLAB.get(c["typ"],c["typ"]).replace(" mit Teilzahlung",""))}</span><span class="tag kl">{E({"Std":"Standard"}.get(c["klasse"],c["klasse"]))}</span>{'<span class="tag out">+ Girokonto</span>' if c.get('giro') else ''}{f'<span class="tag out">{E(c["netz"])}</span>' if c.get('netz') else ''}</div>
    <div class="stats"><div><small>Jahresgebühr</small>{st(c.get("fee")==0,fee)}</div><div><small>Zahlung Ausland</small>{st(c.get("fx")==0,fxT(c) if c.get("fx") is not None else "–")}</div><div><small>Bargeld Inland</small>{st(v==0,cash)}</div></div>
    {offer(c)}
    {f'<div class="earn"><span>Sammeln</span><b>{E(earn)}</b></div>' if earn else ""}
    <ul class="checks">{"".join(f"<li>{E(x)}</li>" for x in c["pros"][:4])}</ul>
    <div class="acts"><a class="btn primary block" href="{E(c.get("quelle"))}" target="_blank" rel="noopener">Zum Anbieter ↗</a><a class="btn ghost block" href="{base}{c["slug"]}/">Details ansehen</a></div>
  </article>'''
TXT={'de':dict(list_t='Kreditkarten-Vergleich Deutschland 2026 – unabhängig | Finvallo',biz_t='Business-Kreditkarten Deutschland 2026 im Vergleich | Finvallo',
               biz_lede=lambda n:f'{n} Karten für Selbstständige und Firmen, bewertet nach denselben sieben Kriterien wie Privatkarten.',biz_h='Business-Kreditkarten in Deutschland'),
     'at':dict(list_t='Kreditkarten-Vergleich Österreich 2026 | Finvallo',biz_t='Firmenkreditkarten Österreich 2026 im Vergleich | Finvallo',
               biz_lede=lambda n:'Für Selbstständige, Freiberufler und Firmen gelten andere Maßstäbe: Kosten und Abrechnung zählen mehr, Reiseschutz weniger. Wir bewerten Firmenkarten nach denselben sieben Kriterien wie Privatkarten, aber in einer eigenen Liste.',biz_h='Business- und Firmenkarten')}
def list_page(cards,priv,biz):
    code=L['code']; N=L['name']; rel=f'{code}/kreditkarten/'; P='../../'
    n=len(cards); na=len({c['anbieter'] for c in cards})
    t=TXT[code]['list_t']; top=priv[:3]
    nprv=card_count(code,'private')   # Meta: Zahl der Karten, die die Seite zeigt
    if code=='de':
        d=f'{nprv} Privatkarten in Deutschland unabhängig verglichen: Jahresgebühr, Ausland, Bargeld, Versicherung. Platz 1 der Finvallo-Bewertung: {top[0]["titel"]} ({de1(top[0]["stars"])}/5).'
        if len(d)>158: d=f'{nprv} Privatkarten in Deutschland unabhängig verglichen: Jahresgebühr, Ausland, Bargeld und Reiseversicherung. Mit Rangliste und bestbewerteter Karte laut Finvallo-Bewertung.'
    else: d=f'{nprv} Privatkarten in Österreich unabhängig verglichen: Jahresgebühr, Auslandsgebühr, Versicherung und offene Bewertung.'
    ld=graph(rel,t,d,[(N,f'{code}/'),('Kreditkarten',rel)],[{"@type":"ItemList","name":f"Beste Kreditkarten {N}","itemListElement":[{"@type":"ListItem","position":c['rank'],"name":c['titel'],"url":f"https://finvallo.com/{rel}{c['slug']}/"} for c in priv[:20]]}])
    unrated=[c for c in cards if c['art']=='Privat' and c.get('stars') is None and not c.get('nurfuer')]
    special=[c for c in cards if c['art']=='Privat' and c.get('nurfuer')]
    body=f'''{HDR(P,rel,("de" if code=="at" else "at")+"/kreditkarten/")}
<div class="wrap"><main id="app">
<h1>Kreditkarten-Vergleich {N}</h1>
  <p class="lede">{n} Karten in {N}: {card_count(code,'rated')} in der Rangliste, {card_count(code,'special')} für bestimmte Kundengruppen in einer eigenen Liste darunter und {card_count(code,'business')} Business-Karten auf einer <a href="business/">eigenen Seite</a>{f" und {len(unrated)} Karten ohne Bewertung (zu wenig bestätigte Daten)" if unrated else ""}. Sortiert nach unserer Bewertung. Provisionen haben keinen Einfluss auf die Reihenfolge.</p>
  <details class="box howscore"><summary><span><b>So entstehen die Sterne</b><br><small>7 Kriterien, feste Regeln, offene Gewichtung</small></span><span class="lnk">anzeigen</span></summary>
    <div class="wbars">{"".join(f'<div class="wbar"><span>{k}</span><span class="t"><i style="width:{w*4}%"></i></span><em>{w} %</em></div>' for k,w in [("Jahresgebühr",25),("Reiseversicherung",20),("Zahlen im Ausland",15),("Kartenart &amp; Akzeptanz",10),("Alltag &amp; Flexibilität",10),("Bargeld",10),("Extras",10)])}</div>
    <p class="note">Jedes Kriterium bekommt nach festen Regeln 1 bis 5 Sterne. Die Gesamtnote ist der gewichtete Durchschnitt. Ab 4,5 Sternen gilt eine Karte als sehr gut. Fehlende Angaben zählen mit 2,5 Sternen, damit sie keinen Vorteil bringen. Bei gleicher Sternzahl steht die Karte mit der niedrigeren Jahresgebühr vorn.</p>
    <p class="note">Kategorie-Plätze (z. B. „Platz 1 für Reisen“) kommen aus den Bestenlisten, dort sind die Kriterien anders gewichtet. Deshalb kann eine Karte in einer Kategorie vorn liegen und in der Gesamtwertung weiter hinten.</p>
    <a class="lnk" href="{P}{code}/kreditkarten/methodik/">Alle Regeln und ein Rechenbeispiel →</a></details>
  <p class="lhead"><b>{card_count(code,'rated')} Karten in der Rangliste</b></p>
  <div class="list" id="list">{"".join(list_item(c,P) for c in priv)}</div>
  {f'<h2>Noch nicht bewertet</h2><p class="note">Für diese Karten fehlen uns bestätigte Angaben in mindestens drei Kriterien.</p><div class="list">{"".join(list_item(c,P) for c in unrated)}</div>' if unrated else ''}
  {f'<h2>Nur für bestimmte Kundengruppen</h2><p class="note">Diese Karten bekommt nicht jeder. Sie stehen deshalb nicht in der Rangliste.</p><div class="list" data-special>{"".join(list_item(c,P) for c in special)}</div>' if special else ''}
  {f'<h2>Business-Kreditkarten</h2><p class="lede">Firmen- und Business-Karten bewerten wir nach denselben Regeln, aber in einer eigenen Liste.</p><p><a class="btn" href="business/">Alle {len(biz)} Business-Karten ansehen →</a></p>' if biz else ''}
  <p class="note" style="margin-top:18px"><a class="lnk" href="alle/">Alle Karten nach Anbieter →</a></p>
</main>
{footer(P)}'''
    write(rel,head(t,d,rel,P,ld,alt=alt_links('at/kreditkarten/','de/kreditkarten/'))+body)
def biz_page(biz):
    code=L['code']; rel=f'{code}/kreditkarten/business/'; P='../../../'
    t=TXT[code]['biz_t']
    d=f'{len(biz)} Business- und Firmenkreditkarten in {L["name"]} unabhängig verglichen: Kosten, Abrechnung, Extras und Bewertung.'
    biz=sorted(biz,key=lambda c:(-(c.get('stars') or 0),c.get('fee') or 0))
    ld=graph(rel,t,d,[(L['name'],f'{code}/'),('Kreditkarten',f'{code}/kreditkarten/'),('Business',rel)])
    def items(X):
        out=[]
        for c in X:
            r=c.get('rank'); c['rank']=None; out.append(list_item(c,P,'../')); c['rank']=r
        return ''.join(out)
    BJ=json.load(open(SP+f'/daten/{code}/business.json')) if os.path.exists(SP+f'/daten/{code}/business.json') else {}
    w=BJ.get('weitere') or []
    intro=BJ.get('einleitung')   # Text liefert der Auftraggeber; ohne Text wird nichts angezeigt
    kc=[c for c in biz if c['typ'] in ('Kreditkarte','Charge')]; dc=[c for c in biz if c['typ'] not in ('Kreditkarte','Charge')]
    free=[c for c in biz if c.get('fee')==0]
    mit=[c for c in biz if any(re.search(r'(Zusatz|Mitarbeiter)karten?',x) and re.search(r'kostenlos|inklusive|gratis|0 €',x) for x in (c.get('pros') or [])+(c.get('extra') or []))]
    nogiro=[c for c in biz if c.get('giro') is False]
    nl=lambda X: ', '.join(c['titel'] for c in X[:-1])+' und '+X[-1]['titel'] if len(X)>1 else X[0]['titel']
    fq=[]
    if free: fq.append(('Welche Firmenkarte hat keine Jahresgebühr?',f'Ohne Jahresgebühr: {nl(free)}.'+(f' Am besten bewertet davon ist die {max(free,key=lambda c:c.get("stars") or 0)["titel"]}.' if len(free)>1 else '')))
    else: fq.append(('Welche Firmenkarte hat keine Jahresgebühr?','In unserem Vergleich hat derzeit keine Firmenkarte eine Jahresgebühr von 0 €.'))
    if mit: fq.append(('Welche Firmenkarten haben kostenlose Mitarbeiterkarten?',f'Laut Anbieter mit kostenlosen Zusatz- oder Mitarbeiterkarten: {nl(mit)}. Die Bedingungen stehen auf der jeweiligen Kartenseite.'))
    if nogiro: fq.append(('Welche Firmenkarten gibt es ohne Firmenkonto beim Anbieter?',f'Ohne Konto beim Anbieter bekommst du: {nl(nogiro)}.'))
    first=kc[0] if kc else biz[0]
    tie=[c for c in kc if c.get('stars')==first.get('stars')] if first.get('stars') else [first]
    kurz=f'<b>Kurz gesagt:</b> {len(biz)} Firmenkarten im Vergleich. '+(f'Am besten bewertet ist die {first["titel"]}'+(f' mit {de1(first["stars"])} Sternen' if first.get('stars') else '') if len(tie)<2 else f'Am besten bewertet sind mit je {de1(first["stars"])} Sternen: '+nl(tie))+'.'+(f' {len(free)} {"Karte kostet" if len(free)==1 else "Karten kosten"} keine Jahresgebühr.' if free else '')
    ld=graph(rel,t,d,[(L['name'],f'{code}/'),('Kreditkarten',f'{code}/kreditkarten/'),('Business',rel)],[{"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in fq]}])
    body=f'''{HDR(P,rel,("de" if code=="at" else "at")+"/kreditkarten/business/")}
<div class="wrap"><main id="app">
<h1>{TXT[code]["biz_h"]}</h1>
<div class="facts prose"><p>{kurz}</p></div>
<p class="lede">{E(TXT[code]["biz_lede"](len(biz)))}</p>
{f'<div class="prose">{intro}</div>' if intro else ''}
<p class="note">Mehr zu Haftung und Abrechnung im <a href="{P}{code}/ratgeber/business/">Ratgeber Firmenkreditkarten</a>.</p>
<h2>Business-Kredit- und Charge-Karten</h2><div class="list">{items(kc)}</div>
{f'<h2>Business-Debitkarten und Konten</h2><div class="list">{items(dc)}</div>' if dc else ''}
{f'<h2>Weitere Business-Angebote</h2><p class="note" style="margin-top:-6px">Diese Angebote kurz im Überblick. Details und aktuelle Preise beim Anbieter.</p>{qa(w)}' if w else ''}
<h2>Fragen und Antworten</h2><div class="faq">{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q,a in fq)}</div>
</main>
{footer(P)}'''
    write(rel,head(t,d,rel,P,ld,alt=alt_links('at/kreditkarten/business/','de/kreditkarten/business/'))+body)
def initials(n): return re.sub(r'[^A-Za-z0-9]','',n)[:2].upper()
def prow_card(c,base):
    return (f'<a class="prow" href="{base}{c["slug"]}/"><span style="width:52px">{face(c," sm")}</span><span style="min-width:0"><b>{E(c["name"] if c.get("name") and c["titel"].endswith(c["name"]) else c["titel"])}</b>'
            f'<small>{TYPLAB.get(c["typ"],c["typ"]).replace(" mit Teilzahlung","")} · {"kostenlos" if c.get("fee")==0 else (eur(c["fee"])+" €/Jahr") if c.get("fee") is not None else "Preis beim Anbieter"}</small>'
            f'<small>{(de1(c["stars"])+" ★ "+c["note"]) if c.get("stars") else "nicht bewertet"}</small></span><span class="mut">›</span></a>')
def anbieter_pages(cards,prov):
    """Anbieterseiten. Die frühere Übersicht /anbieter/ leitet auf /alle/ um (gleicher Inhalt mit Tabelle).
    Anbieter mit nur einer Karte und ohne Zusatzinfos bekommen keine Seite, sondern einen 301 auf die Kartenseite."""
    code=L['code']; N=L['name']; DT=details(code)
    by={}
    for c in cards: by.setdefault(c['p'],[]).append(c)
    rel=f'{code}/kreditkarten/anbieter/'
    REDIRECTS[f'/{rel}']=f'/{code}/kreditkarten/alle/'
    def best(v): r=[x for x in v if x.get('stars')]; return max(r,key=lambda x:x['stars']) if r else None
    for p,v in by.items():
        pv=prov.get(p) or {}; nm=pv.get('name') or v[0]['anbieter']; dt=DT.get(p) or {}
        rel2=f'{rel}{p}/'; P2='../../../../'
        if p not in PROVPAGE.get(code,()):
            REDIRECTS[f'/{rel2}']=f'/{code}/kreditkarten/{v[0]["slug"]}/'; continue
        v=sorted(v,key=lambda c:(-(c.get('stars') or 0),c.get('fee') if c.get('fee') is not None else 1e9,c['titel'].lower()))
        t2=f'{nm} Kreditkarten im Vergleich 2026 | Finvallo' if code=='at' else f'{nm} Kreditkarten in Deutschland 2026 | Finvallo'
        d2=fit_desc(f'{nm}: {len(v)} {"Karte" if len(v)==1 else "Karten"} im Vergleich, mit Jahresgebühr, Auslandsgebühr, Versicherung und Bewertung.'+(f' {pv["text"]}' if pv.get('text') else ''))
        b=best(v); fees=[c['fee'] for c in v if c.get('fee') is not None]
        facts=''.join(f'<div class="r"><span>{k}</span><span>{E(x)}</span></div>' for k,x in [('Anbietertyp',pv.get('typ')),('Sitz',pv.get('sitz') or dt.get('sitz')),('Karten im Vergleich',str(len(v))),
              ('Bester Score',f'{de1(b["stars"])} Sterne – {b["name"] if b.get("name") and b["titel"].endswith(b["name"]) else b["titel"]}' if b else None),
              ('Jahresgebühren',(('kostenlos' if max(fees)==0 else f'{eur(min(fees))} € bis {eur(max(fees))} €') if len(set(fees))>1 or max(fees)==0 else f'{eur(fees[0])} €') if fees else None)] if x)
        feat=''.join(x for x in [f'<span>📍 {E(pv["sitz"])}</span>' if pv.get('sitz') else '',f'<span class="b">▭ {len(v)} {"Karte" if len(v)==1 else "Karten"}</span>',f'<span class="g">★ bis {de1(b["stars"])}</span>' if b else ''])
        about=''.join(f'<p><b>{lab}:</b> {E(dt[k])}</p>' for k,lab in DETAIL_LABELS if dt.get(k) and (k!='kritik' or kritik_ok(dt)))
        src=' · '.join(ext(u) for u in dt.get('quellen') or [])
        giro=[c for c in v if c.get('giro')]
        if not giro: ga=f'Nein. Für {"keine der Karten" if len(v)>1 else "die Karte"} von {nm} brauchst du ein Girokonto beim Anbieter.'
        elif len(giro)==len(v): ga=f'Ja. {"Alle Karten" if len(v)>1 else "Die Karte"} von {nm} gibt es nur mit einem Konto beim Anbieter' + (f' ({giro[0]["konto"]})' if giro[0].get('konto') else '') + '.'
        else: ga=f'Nur für {", ".join(c["titel"] for c in giro)}. Die anderen Karten von {nm} bekommst du auch ohne Konto beim Anbieter.'
        fq=[(f'Braucht man ein Konto bei {nm}?',ga)]
        if fees:
            mn=min(fees); cheap=[c for c in v if c.get('fee')==mn]
            fq.append((f'Welche Karte von {nm} ist die günstigste?',(f'Die {cheap[0]["titel"]}' if len(cheap)==1 else 'Die '+', '.join(c['titel'] for c in cheap[:-1])+' und die '+cheap[-1]['titel'])+(' kostet keine Jahresgebühr.' if mn==0 else f' mit {eur(mn)} € Jahresgebühr.' if len(cheap)==1 else f' mit je {eur(mn)} € Jahresgebühr.')))
        ld2=graph(rel2,t2,d2,[(N,f'{code}/'),('Kreditkarten',f'{code}/kreditkarten/'),('Alle Karten',f'{code}/kreditkarten/alle/'),(nm,rel2)],
                  [{"@type":"ItemList","name":f"Kreditkarten von {nm}","itemListElement":[{"@type":"ListItem","position":i+1,"name":c['titel'],"url":f"https://finvallo.com/{code}/kreditkarten/{c['slug']}/"} for i,c in enumerate(v)]},
                   {"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in fq]}],
                  date=max(c['geprueft'] for c in v))
        write(rel2,head(t2,d2,rel2,P2,ld2)+f'''{HDR(P2,rel2,("de" if code=="at" else "at")+"/kreditkarten/anbieter/")}
<div class="wrap"><main id="app">
<div class="crumb"><span><a href="../../alle/">Alle Karten</a> › {E(nm)}</span><span>Stand {dmy(max(c['geprueft'] for c in v))}</span></div>
  <div class="dh" style="grid-template-columns:64px 1fr"><span class="plogo" style="width:64px;height:64px;font-size:20px">{initials(nm)}</span><div>{f'<span class="tag">{E(pv["typ"])}</span>' if pv.get('typ') else ''}<h1 style="margin-top:8px">{E(nm)}: Kreditkarten</h1></div></div>
  <div class="facts prose" style="margin-top:12px"><p><b>Kurz gesagt:</b> {E(nm)} hat {len(v)} {"Karte" if len(v)==1 else "Karten"} im Finvallo-Vergleich für {N}.{f' Am besten bewertet ist die {E(b["titel"])} mit {de1(b["stars"])} Sternen.' if b and len(v)>1 else (f' Sie hat {de1(b["stars"])} Sterne.' if b else '')}{(' ' + E(fq[1][1])) if len(fq)>1 and len(v)>1 else ''}</p></div>
  <div class="feat">{feat}</div>
  {f'<a class="btn primary block" style="margin-top:16px" href="{E(pv["web"])}" target="_blank" rel="noopener">Zum Anbieter ↗</a>' if pv.get('web') else ''}
    <div class="cond" style="margin-top:18px"><div class="gh">Auf einen Blick</div>{facts}</div>
    {f'<h2>Über {E(nm)}</h2><div class="prose">' + (f'<p>{E(pv["text"])}</p>' if pv.get('text') else '') + about + '</div>' if pv.get('text') or about else ''}
    <h2>Karten von {E(nm)}</h2><div class="plist">{"".join(prow_card(c,"../../") for c in v)}</div>
    {f'<h2>Für wen passt {E(nm)}</h2><div class="prose"><p>{E(dt["fuer_wen"])}</p></div>' if dt.get('fuer_wen') else ''}
    <h2>Fragen und Antworten</h2><div class="faq">{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q,a in fq)}</div>
    {f'<p class="src">Quellen: {src}</p>' if src else ''}
</main>
{footer(P2)}''')
def write_redirects():
    """301-Regeln aus REDIRECTS: tools/daten/redirects.json, server/redirects.conf (nginx, im Server-Block eingebunden) und public/.htaccess (Apache)."""
    for a,b in list(ENTF.items()):
        if os.path.isdir(R+a.strip('/')): del ENTF[a]   # Seite gibt es wieder
        elif a not in REDIRECTS: REDIRECTS[a]=b
    json.dump(dict(sorted(ENTF.items())),open(ENTF_P,'w'),ensure_ascii=False,indent=1)
    json.dump(dict(sorted(REDIRECTS.items())),open(os.path.join(SP,'daten','redirects.json'),'w'),ensure_ascii=False,indent=1)
    open(os.path.join(R,'..','server','redirects.conf'),'w').write('# automatisch erzeugt von tools/karten.py – nicht von Hand ändern\n'+''.join(f'location = {a} {{ return 301 {b}; }}\n' for a,b in sorted(REDIRECTS.items())))
    HT_CACHE=('<IfModule mod_headers.c>\n  <FilesMatch "\\.(html|htm|xml|txt|json)$">\n    Header set Cache-Control "public, max-age=600, must-revalidate"\n  </FilesMatch>\n'
              '  <FilesMatch "\\.(css|js)$">\n    Header set Cache-Control "public, max-age=31536000, immutable"\n  </FilesMatch>\n'
              '  <FilesMatch "\\.(woff2|png|jpg|jpeg|webp|svg|ico)$">\n    Header set Cache-Control "public, max-age=86400"\n  </FilesMatch>\n</IfModule>\n')
    open(R+'.htaccess','w').write(HT_CACHE+'# automatisch erzeugt von tools/karten.py (für Apache-Hosting)\nRewriteEngine On\nRewriteCond %{HTTP_HOST} ^www\\.finvallo\\.com$ [NC]\nRewriteRule ^(.*)$ https://finvallo.com/$1 [R=301,L]\nRewriteCond %{HTTPS} off\nRewriteRule ^(.*)$ https://finvallo.com/$1 [R=301,L]\n'+''.join(f'Redirect 301 {a} https://finvallo.com{b}\n' for a,b in sorted(REDIRECTS.items()))+'ErrorDocument 404 /404.html\n')
def alle_page(cards,prov):
    code=L['code']; N=L['name']; rel=f'{code}/kreditkarten/alle/'; P='../../../'
    by={}
    for c in cards: by.setdefault(c['p'],[]).append(c)
    t=f'Alle Kreditkarten in {N} nach Anbieter | Finvallo'
    d=f'Alle {len(cards)} Karten (Kredit-, Debit- und Prepaid-Karten) in {N} nach Anbieter sortiert, mit Jahresgebühr, Auslandsgebühr und Bewertung. Stand {dmy(L["stand"])}.'
    sec=''
    for p,v in sorted(by.items(),key=lambda kv:(prov.get(kv[0]) or {}).get('name',kv[1][0]['anbieter']).lower()):
        nm=(prov.get(p) or {}).get('name') or v[0]['anbieter']
        rows=''.join(f'<tr><td><a class="lnk" href="../{c["slug"]}/">{E(c["titel"])}</a></td><td>{E(TYPLAB.get(c["typ"],c["typ"]).replace(" mit Teilzahlung",""))}</td><td>{"0 €" if c.get("fee")==0 else (eur(c["fee"])+" €") if c.get("fee") is not None else "beim Anbieter prüfen"}</td><td>{E(fxT(c)) if c.get("fx") is not None else "–"}</td><td>{(de1(c["stars"])+" ★") if c.get("stars") else "nicht bewertet"}</td></tr>' for c in sorted(v,key=lambda c:-(c.get('stars') or 0)))
        sec+=f'<h2>{(f"<a href=\"../anbieter/{p}/\">{E(nm)}</a>") if p in PROVPAGE.get(code,()) else E(nm)}</h2><div class="tbl"><table><thead><tr><th>Karte</th><th>Typ</th><th>Jahresgebühr</th><th>Zahlung Ausland</th><th>Bewertung</th></tr></thead><tbody>{rows}</tbody></table></div>'
    write(rel,head(t,d,rel,P,graph(rel,t,d,[(N,f'{code}/'),('Kreditkarten',f'{code}/kreditkarten/'),('Alle Karten',rel)]),alt=alt_links('at/kreditkarten/alle/','de/kreditkarten/alle/'))+f'''{HDR(P,rel,("de" if code=="at" else "at")+"/kreditkarten/alle/")}
<div class="wrap"><main id="app">
<div class="crumb"><span><a href="../../">{N}</a> › <a href="../">Kreditkarten</a> › Alle Karten</span><span>Stand {dmy(L["stand"])}</span></div><h1>Alle Kreditkarten in {N}</h1><p class="lede">{len(cards)} Karten von {len(by)} Anbietern. Ein Klick führt zur ausführlichen Kartenseite mit allen Kosten, der Versicherung und unserer Bewertung.</p>{sec}
</main>
{footer(P)}''')
def datafile(cards):
    out=[]
    for c in cards:
        out.append({k:c.get(k) for k in ['id','slug','anbieter','herausgeber','name','titel','art','typ','klasse','netz','fee','fee1','feeNote','fx','fxText','cashText','soll','effz','rahmen','giro','auto','pay','tier','stars','note','rank','pros','cons','quelle','preis','stand','geprueft']}
                   |{'stand':c['geprueft'],'klasse':{'Std':'Standard'}.get(c.get('klasse'),c.get('klasse')),'versicherung':TIER[c['tier']][1] if c.get('tier') is not None else None,'url':f'https://finvallo.com/{L["code"]}/kreditkarten/{c["slug"]}/'})
    os.makedirs(R+f'{L["code"]}/daten',exist_ok=True)
    json.dump({'quelle':f'https://finvallo.com/{L["code"]}/kreditkarten/','stand':L['stand'],'anzahl':card_count(L['code'],'all'),'lizenz':'Frei nutzbar mit Quellenangabe Finvallo',
               'hinweis':'stand = geprueft = Datum der letzten Prüfung der Karte. IDs sind dauerhaft und nicht lückenlos: Entfernte Karten hinterlassen eine Lücke (z. B. AT34, die Austrian Miles & More Smartcard gibt es nur als Business-Karte). url = Kartenseite bei Finvallo, quelle = Anbieterseite, preis = Preisblatt.','karten':out},open(R+f'{L["code"]}/daten/kreditkarten.json','w'),ensure_ascii=False,indent=1)

# ---------- Methodik (DE; AT-Methodik ist eine feste Seite) ----------
def methodik_page(cards,priv):
    rel='de/kreditkarten/methodik/'; P='../../../'
    t='So bewerten wir Kreditkarten in Deutschland | Finvallo'
    d='Die Finvallo-Methodik für Kreditkarten in Deutschland: 7 Kriterien, feste Regeln, offene Gewichte. Mit Rechenbeispiel und Datenquellen.'
    ex=priv[0]
    rows=lambda X: ''.join(f'<tr><td>{a}</td><td>{b}</td></tr>' for a,b in X)
    rules=[('Jahresgebühr · 25 %','Was die Karte ab dem zweiten Jahr kostet. Aktionen im ersten Jahr zählen bei den Extras.',[('0 €','5,0'),('bis 25 €','4,6'),('bis 50 €','4,2'),('bis 100 €','3,6'),('bis 150 €','3,0'),('bis 250 €','2,4'),('bis 450 €','1,8'),('über 450 €','1,2')]),
           ('Zahlen im Ausland · 15 %','Was eine Zahlung in US-Dollar insgesamt extra kostet, also Auslandseinsatzentgelt und Kursaufschlag zusammen.',[('0 %','5,0'),('0 % mit Freigrenze oder Wochenendaufschlag','4,8'),('bis 0,5 %','4,8'),('bis 1 %','4,4'),('bis 1,5 %','4,0'),('bis 2 %','3,4'),('bis 2,7 %','2,6'),('bis 3,2 %','2,0'),('darüber','1,5')]),
           ('Reiseversicherung · 20 %','Wie umfassend der Reiseschutz ist, der ohne Aufpreis enthalten ist.',[('Premium-Reiseschutz','5,0'),('umfassender Reiseschutz (mit Mietwagen)','4,7'),('Reiseversicherung mit Reiserücktritt','4,2'),('Basis-Reiseschutz','3,0'),('keine Reiseversicherung','1,0')]),
           ('Kartenart & Akzeptanz · 10 %','Wo die Karte angenommen wird. Debit- und Prepaid-Karten gehen fast überall, werden aber bei Kautionen für Mietwagen oder Hotels oft abgelehnt.',[('Kredit- oder Charge-Karte mit Visa oder Mastercard','5,0'),('Kredit- oder Charge-Karte, Netz nicht bestätigt','4,5'),('Debit- oder Prepaid-Karte mit Visa oder Mastercard','3,5'),('American Express','3,0'),('Diners Club','2,0')]),
           ('Alltag & Flexibilität · 10 %','Durchschnitt aus drei Punkten. Ist ein Punkt nicht bestätigt, zählt er wie bei allen Kriterien mit 2,5 Sternen.',[('kein Konto beim Anbieter nötig','5,0 (sonst 2,5)'),('automatische Abbuchung','5,0 (sonst 3,0)'),('Apple Pay / Google Pay','5,0 (sonst 1,0)')]),
           ('Bargeld · 10 %','Was eine Abhebung von 200 € am Automaten in Deutschland kostet.',[('kostenlos','5,0'),('kostenlos, aber ab Tag 1 verzinst','4,5'),('kostenlos, aber nur begrenzt viele Abhebungen','4,5'),('bis 2 €','4,2'),('bis 4 €','3,4'),('bis 7 €','2,6'),('darüber','2,0')]),
           ('Extras · 10 %','Jede Karte startet bei 2,5 Sternen. Für jedes Extra gibt es einen Zuschlag, höchstens bis 5,0.',[('Cashback, Punkte oder Partner-Rabatte inklusive','+1,0'),('kostenlose Lounge-Besuche','+1,0'),('nur Lounge-Mitgliedschaft','+0,4'),('Meilen','+0,5'),('Guthaben oder Partner-Abos','+0,5'),('FastTrack','+0,3'),('Aktion im 1. Jahr','+0,3')])]
    rb=''.join(f'<h3 style="margin-top:22px">{a}</h3><p class="note">{b}</p><div class="tbl"><table><tbody>{rows(X)}</tbody></table></div>' for a,b,X in rules)
    exrows=''.join(f'<tr><td><b>{E(p["k"])}</b><br><small class="mut">{E(p["v"])}</small></td><td>{p["w"]} %</td><td>{de1(p["s"])}</td></tr>' for p in ex['score']['parts'])
    fq=[('Wie bewertet Finvallo Kreditkarten in Deutschland?','Jede Karte bekommt in sieben Kriterien nach festen Regeln 1 bis 5 Sterne: Jahresgebühr (25 %), Reiseversicherung (20 %), Zahlen im Ausland (15 %), Kartenart, Alltag, Bargeld und Extras (je 10 %). Die Gesamtnote ist der gewichtete Durchschnitt.'),
        ('Woher kommen die Daten?','Aus den Preis- und Leistungsverzeichnissen, Produktseiten und Versicherungsbedingungen der deutschen Anbieter. Jede Kartenseite nennt die Quelle und das Datum der letzten Prüfung.'),
        ('Wie oft prüft Finvallo die Konditionen?','Wir prüfen die Konditionen jede Woche bei den Anbietern. Das Datum der letzten Prüfung steht auf jeder Kartenseite.'),
        ('Beeinflussen Provisionen die Bewertung?','Nein. Ob wir mit einem Anbieter eine Partnerschaft haben, spielt für Sterne und Reihenfolge keine Rolle.')]
    ld=graph(rel,t,d,[('Deutschland','de/'),('Kreditkarten','de/kreditkarten/'),('Methodik',rel)],[{"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in fq]}])
    write(rel,head(t,d,rel,P,ld,alt=alt_links('at/kreditkarten/methodik/',rel))+f'''{HDR(P,rel,'at/kreditkarten/methodik/')}
<div class="wrap"><main id="app">
<h1>So bewerten wir Kreditkarten in Deutschland</h1><p class="lede">Jede Karte bekommt 1 bis 5 Sterne. Ob wir mit einem Anbieter eine Partnerschaft haben, spielt für Sterne und Reihenfolge keine Rolle. Hier steht genau, wie die Sterne entstehen.</p>
<div class="facts prose"><p><b>Kurz gesagt:</b> Sieben Kriterien, feste Regeln, gleiche Gewichte für alle {len(cards)} Karten. Fehlt eine bestätigte Angabe, zählt das Kriterium mit 2,5 Sternen. Bewertet wird nur, wenn die Jahresgebühr bekannt ist und mindestens 5 der 7 Kriterien bestätigt sind. Stand: {dmy(L['stand'])}.</p></div>
<h2>Die Gewichte</h2><div class="tbl"><table><thead><tr><th>Kriterium</th><th>Gewicht</th></tr></thead><tbody>{rows([("Jahresgebühr","25 %"),("Reiseversicherung","20 %"),("Zahlen im Ausland","15 %"),("Kartenart &amp; Akzeptanz","10 %"),("Alltag &amp; Flexibilität","10 %"),("Bargeld","10 %"),("Extras","10 %")])}</tbody></table></div>
<h2>Die Regeln je Kriterium</h2>{rb}
<h2>Was die Sterne bedeuten</h2><div class="tbl"><table><tbody>{rows([("ab 4,5 Sternen","Sehr gut"),("ab 4,0 Sternen","Gut"),("ab 3,5 Sternen","Befriedigend"),("ab 3,0 Sternen","Ausreichend"),("unter 3,0 Sternen","Mangelhaft")])}</tbody></table></div>
<h2>Beispiel: {E(ex["titel"])}</h2><p class="note">So kommt die Karte auf {de1(ex["stars"])} Sterne.</p><div class="tbl"><table><thead><tr><th>Kriterium</th><th>Gewicht</th><th>Sterne</th></tr></thead><tbody>{exrows}<tr><td><b>Gesamt</b></td><td>100 %</td><td><b>{de1(ex["stars"])}</b></td></tr></tbody></table></div>
<h2>Was die Sterne nicht zeigen</h2><div class="prose"><p>Teure Premiumkarten verlieren durch die Jahresgebühr Sterne, auch wenn sich Guthaben und Lounges für Vielreisende lohnen können. Zinsen für Teilzahlung zählen nicht mit, weil sie nur anfallen, wenn du nicht alles zahlst. Für deinen eigenen Fall nimm den <a href="{P}de/kreditkarten/rechner/">Kreditkarten-Rechner</a> und die <a href="../bestenlisten/">Bestenlisten</a>.</p></div>
<h2>Woher die Daten kommen</h2><div class="prose"><p>Zuerst zählen die deutschen Preis- und Leistungsverzeichnisse, Verträge, Versicherungsbedingungen und Produktseiten der Anbieter. Konditionen aus Österreich übernehmen wir nicht. Die Quelle und das Datum der letzten Prüfung stehen auf jeder Kartenseite.</p></div>
<h2>Fragen und Antworten</h2><div class="faq">{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q,a in fq)}</div>
</main>
{footer(P)}''')
    fa=R+'at/kreditkarten/methodik/index.html'; sa=open(fa).read()
    if 'hreflang="de-DE" href="https://finvallo.com/de/kreditkarten/methodik/"' not in sa:
        sa=sa.replace('<link rel="canonical" href="https://finvallo.com/at/kreditkarten/methodik/">','<link rel="canonical" href="https://finvallo.com/at/kreditkarten/methodik/">'+alt_links('at/kreditkarten/methodik/',rel),1); open(fa,'w').write(sa)

# ---------- Bestenlisten ----------
CATS=[
 dict(k='reisen',t='Reisen',h='Die besten Karten für Reisen',d='Für Reisen zählen vor allem eine gute Reiseversicherung und niedrige Gebühren im Ausland.',f=lambda c:c['typ']!='Prepaid',w={'_bonus':'fokus','fokus':['Reiseversicherung', 'Zahlen im Ausland']}),
 dict(k='gratis',t='Ohne Jahresgebühr',h='Die besten Karten ohne Jahresgebühr',d='Nur Karten, die dauerhaft nichts kosten. Bewertet wie in der Gesamtwertung.',f=lambda c:c.get('fee')==0,w=None),
 dict(k='ausland',t='Ohne Auslandsgebühr',h='Die besten Karten zum Zahlen im Ausland',d='Karten mit höchstens 0,5 % Aufschlag in fremder Währung. Hier zählen vor allem günstiges Zahlen und Abheben im Ausland.',f=lambda c:c.get('fx') is not None and c['fx']<=0.5,w={'_bonus':'fokus','fokus':['Zahlen im Ausland', 'Bargeld']}),
 dict(k='punkte',t='Meilen & Punkte',h='Die besten Karten für Meilen und Punkte',d='Nur Karten mit Meilen- oder Punkteprogramm auf normale Einkäufe, etwa Miles & More, Membership Rewards, Payback oder Hotelpunkte. Je mehr du bei 1.000 € Umsatz im Monat sammelst, desto weiter vorn steht die Karte. Reines Cashback steht in der eigenen Bestenliste.',f=lambda c:c.get('sammel') is not None and c.get('sammelKind')!='cash',w={'_bonus':'sammel'}),
 dict(k='cashback',t='Cashback',h='Die besten Karten mit Cashback',d='Nur Karten, die auf normale Einkäufe Geld zurückgeben. Je mehr bei 1.000 € Umsatz im Monat zurückkommt, desto weiter vorn steht die Karte. Partner- und Reiserabatte zählen hier nicht.',f=lambda c:c.get('sammel') is not None and c.get('sammelKind')=='cash',w={'_bonus':'sammel'}),
 dict(k='lounge',t='Lounge-Zugang',h='Die besten Karten mit Lounge-Zugang',d='Nur Karten mit kostenlosen Lounge-Besuchen. Hier zählt vor allem der Lounge-Zugang: wie viele Besuche gratis sind, ob eine Begleitperson gratis mitkommt und ob die Lounges weltweit gelten.',f=lambda c:bool(c['ex'].get('lg')),w={'_bonus':'mix','fokus':['Lounge-Zugang'],'anteil':0.7}),
 dict(k='premium',t='Premium',h='Die besten Premiumkarten',d='Top-Karten mit Lounges oder Premium-Reiseschutz. Hier zählen vor allem Reiseschutz und Extras.',f=lambda c:c['klasse']=='Premium',w={'_bonus':'fokus','fokus':['Reiseversicherung', 'Extras']}),
 dict(k='studium',f_at=lambda c:bool(re.search(r'Student|Maturant',c['titel'])),t='Studierende',h='Die besten Karten für Studierende und junge Leute',d='Karten, die für Studierende, Azubis oder junge Kunden günstiger oder kostenlos sind, etwa weil das nötige Konto bis zu einem bestimmten Alter nichts kostet. Bewertet wie in der Gesamtwertung, mit dem regulären Preis.',f=lambda c:youth(c) is not None,w=None),
 dict(k='debit',t='Debit & App-Banken',h='Die besten Debitkarten und App-Banken',d='Karten, die sofort vom Konto abbuchen. Hier zählen vor allem günstiges Zahlen und Abheben im Ausland.',f=lambda c:c['typ'] in ('Debit','Prepaid'),w={'_bonus':'fokus','fokus':['Zahlen im Ausland', 'Bargeld']}),
]
YOUTH=r'(unter (?:2|3)\d(?: Jahren|-Jährige| in Ausbildung)?|bis (?:1|2)\d Jahre|bis zum (?:1|2)\d\. Geburtstag|in Ausbildung|Studierende|Student|Young|StartKonto|Azubi)'
def youth(c):
    if c.get('typ') is None: return None
    for k in ('titel','feeNote','konto'):
        m=re.search(r'[^;()]{0,50}'+YOUTH+r'[^;()]{0,30}',str(c.get(k) or ''))
        if m: return m.group(0).strip(' ,')
    for x in c.get('extra') or []:
        if re.search(YOUTH,x): return x
    return None
# Karten nur für bestimmte Gruppen (Studium/Alter, Mitgliedschaft): nicht im Hauptranking, aber in passenden Bestenlisten
KORR=json.load(open(os.path.join(SP,'daten','korrekturen.json'))) if os.path.exists(os.path.join(SP,'daten','korrekturen.json')) else {}
GRUPPEN=KORR.get('gruppen') or {}
def apply_korrekturen(cards,land):
    """Gezielte, belegte Korrekturen aus tools/daten/korrekturen.json."""
    by={c.get('titel'):c for c in cards}
    for k in KORR.get('karten') or []:
        c=by.get(k['titel'])
        if k['land']==land and c: c.update(k['set'])
def apply_gruppen(cards):
    for c in cards:
        t=c.get('titel') or ''
        g=GRUPPEN.get(t)
        if g: c['nurfuer']=g['text']; c['jung']=g.get('jung',False); continue
        if not c.get('nurfuer') and re.search(r'\b(Student|Maturant|Young|Jugend)',t):
            c['nurfuer']='Nur für Studierende oder junge Kundinnen und Kunden (Altersgrenze beim Anbieter)'; c['jung']=True
def lounge_data(land):
    p=os.path.join(SP,'daten',land,'lounge.json')
    return json.load(open(p))['karten'] if os.path.exists(p) else {}
def lg_text(d):
    v=d.get('visits'); g=d.get('guests'); sc=d.get('scope') or ''
    if v in (0,None): t=f'{d.get("program") or "Lounge-Zugang"}: keine Gratis-Besuche, Besuche kosten extra'
    else:
        t=f'{d.get("program") or "Lounges"}: '+('unbegrenzt kostenlose Besuche' if v=='unbegrenzt' else f'{v} kostenlose Besuche pro Jahr')+(', nur am Flughafen Wien' if sc=='Wien' else ', weltweit' if sc=='weltweit' else f', {sc}' if sc else '')
        t+={'unbegrenzt':', Begleitperson gratis','zählt mit':', Begleitpersonen zählen mit',0:', Begleitpersonen zahlen'}.get(g,f', {g} Gäste pro Jahr gratis' if isinstance(g,int) and g>0 else '')
    if d.get('bedingung'): t+=f' ({d["bedingung"].rstrip(".")})'
    return t
def apply_lounge(cards,land):
    """Recherchierte Lounge-Daten (tools/daten/<land>/lounge.json): Text, Extras-Kennzeichen und Lounge-Note."""
    LD=lounge_data(land)
    for c in cards:
        d=LD.get(c.get('slug') or slug(c.get('titel') or ''))
        if not d: continue
        c['lgData']=d; c['lgText']=lg_text(d)
        c.setdefault('ex',{})['lg']=d.get('visits') not in (0,None)
        if c['ex']['lg']: c['ex'].pop('lgm',None)
def lounge_note(d):
    """Lounge-Note aus den Daten: Besuche, Begleitung, Wien oder weltweit."""
    v=d.get('visits')
    if v in (0,None): return None
    big=v=='unbegrenzt' or v>=50   # ab 50 Besuchen im Jahr praktisch unbegrenzt
    s=4.5 if big else 4.0 if v>=10 else 3.5 if v>=6 else 3.0 if v>=4 else 2.5 if v>=2 else 2.0
    g=d.get('guests')
    s+=0.5 if g=='unbegrenzt' else 0.25 if (isinstance(g,int) and g>0) or (g=='zählt mit' and big) else 0
    if d.get('scope')=='Wien': s-=0.5
    return round(max(1.0,min(5.0,s)),1)
def lounge_score(c):
    t=(c.get('lgText') or '')
    if not c['ex'].get('lg'): return None
    m=re.search(r'(\d+)\s*(?:kostenlose |freie |Gratis-)?(?:Besuch|Zutritt|Voucher|Lounge-Besuch)',t,re.I)
    unl=bool(re.search(r'unbegrenzt|ohne Limit|unlimit|Besuche für Karteninhaber kosten(frei|los)|Kostenlose Lounge-Pässe',t,re.I))
    if unl or (m and int(m.group(1))>=50): s=4.8
    elif m: s=min(4.4,2.6+0.15*int(m.group(1)))
    else: s=3.0
    if re.search(r'(Gast|Gäste|Begleitperson)\w* (kostenlos|gratis|frei)|1 Gast kostenlos',t,re.I): s=min(5.0,s+0.2)
    return round(s,1)
SAMMEL_BONUS=[(180,0.5),(120,0.4),(90,0.3),(60,0.2),(36,0.1)]
def sammel_bonus(v):
    """Bonus auf die Gesamtnote für den Sammelwert pro Jahr (vor Jahresgebühr, die steckt schon in der Gesamtnote)."""
    return next((b for lim,b in SAMMEL_BONUS if (v or 0)>=lim),0.0)
def fokus_note(c,fokus):
    """Durchschnitt der Kategorie-Kriterien (Sterne wie in der Gesamtwertung, Lounge-Zugang aus lounge_score)."""
    v=[c.get('lounge') if k=='Lounge-Zugang' else next((p['s'] for p in c['score']['parts'] if p['k']==k),None) for k in fokus]
    v=[x for x in v if x is not None]
    return sum(v)/len(v) if v else None
def fokus_bonus(c,fokus,mx=0.5):
    """Bonus bis +mx (Standard 0,5): Note 2,5 oder weniger in den Kategorie-Kriterien = +0, Note 5,0 = +mx."""
    n=fokus_note(c,fokus)
    return 0.0 if n is None else round(max(0.0,min(1.0,(n-2.5)/2.5))*mx+1e-9,1)
def cat_stars(c,w):
    if c.get('stars') is None: return None
    if not w: return c['stars']
    if w.get('_bonus')=='sammel': return round(min(5.0,c['stars']+sammel_bonus(c.get('sammelEur')))+1e-9,1)
    if w.get('_bonus')=='mix':
        n=fokus_note(c,w['fokus'])
        return c['stars'] if n is None else round(w['anteil']*n+(1-w['anteil'])*c['stars']+1e-9,1)
    if w.get('_bonus')=='fokus':
        return round(min(5.0,c['stars']+fokus_bonus(c,w['fokus'],w.get('max',0.5)))+1e-9,1)
    a=b=0
    for p in c['score']['parts']:
        if p['k'] in w: a+=p['s']*w[p['k']]; b+=w[p['k']]
    if 'Lounge-Zugang' in w and c.get('lounge') is not None: a+=c['lounge']*w['Lounge-Zugang']; b+=w['Lounge-Zugang']
    if 'Sammelwert nach Jahresgebühr' in w and c.get('sammelNetNote') is not None: a+=c['sammelNetNote']*w['Sammelwert nach Jahresgebühr']; b+=w['Sammelwert nach Jahresgebühr']
    return round(a/b+1e-9,1) if b else None
def cat_lists(cards,land):
    import sammeln
    out={}
    for c in cards:
        if c.get('lgData'): c['lounge']=lounge_note(c['lgData'])
        elif land=='de' or c.get('lounge') is None: c['lounge']=lounge_score(c) if land=='de' else c.get('lounge')
        v=sammeln.value(land,c['titel'])
        c['sammel']=sammeln.note(v[0]) if v else None; c['sammelEur']=v[0] if v else None; c['sammelTxt']=v[1]['txt'] if v else None; c['sammelKind']=sammeln.kind(v[1]) if v else None; c['sammelCap']=v[1].get('cap') if v else None
        c['sammelNet']=(v[0]-(c.get('fee') or 0)) if v else None; c['sammelNetNote']=sammeln.net_note(c['sammelNet'])
    for cat in CATS:
        f=cat.get('f_'+land,cat['f'])
        X=[c for c in cards if c['art']=='Privat' and (not c.get('nurfuer') or (cat['k']=='studium' and c.get('jung'))) and c.get('stars') is not None and f(c)]
        out[cat['k']]=sorted(X,key=lambda c:(-(cat_stars(c,cat['w']) or 0),c.get('fee') if c.get('fee') is not None else 1e9,c['titel'].lower()))
    best={}
    for cat in CATS:
        for i,c in enumerate(out[cat['k']][:3]):
            if c['slug'] not in best or i<best[c['slug']][0]: best[c['slug']]=(i,cat['t'],cat['k'],cat_stars(c,cat['w']))
    return out,best
TIERK={0:'keine',1:'Basis',2:'inkl. Storno',3:'umfassend',4:'Premium'}
def k_fee(c): return '–' if c.get('fee') is None else '0 €' if c['fee']==0 else f'{eur(c["fee"])} €'
def k_fx(c): return '–' if c.get('fx') is None else '0 %' if c['fx']==0 else pct(c['fx'])
def k_cash(c):
    t=cashT(c)
    if t=='unbekannt': return '–'
    if re.match(r'(kostenlos|0 €|weltweit kostenlos)',t,re.I): return '0 €'
    m=re.match(r'^(\d+) Gratis-Abhebungen',t)
    if m: return f'{m.group(1)}× gratis/Monat'
    if len(t)<=18: return t
    m=re.match(r'^((?:ca\. )?\d+(?:,\d+)?\s?(?:%|€)(?:, mind\. \d+(?:,\d+)? €)?)',t)
    return m.group(1) if m else 'siehe Karte'
def k_ins(c): return TIERK.get(c.get('tier'),'–')
def k_lg(c):
    d=c.get('lgData')
    if d and d.get('visits') not in (None,):
        v=d['visits']; w=' (Wien)' if d.get('scope')=='Wien' else ''
        return ('unbegrenzt' if v=='unbegrenzt' else 'nur gegen Gebühr' if v==0 else f'{v} pro Jahr')+w
    t=c.get('lgText') or ''
    if re.search(r'unbegrenzt|ohne Limit|unlimit',t,re.I): return 'unbegrenzt'
    m=re.search(r'(\d+)\s*(?:kostenlose |freie |Gratis-)?(?:Besuch|Zutritt|Voucher|Lounge-Besuch)',t,re.I)
    return f'{m.group(1)} pro Jahr' if m else 'ja'
def k_guest(c):
    d=c.get('lgData')
    if d:
        g=d.get('guests')
        return {'unbegrenzt':'gratis','zählt mit':'zählt mit',0:'zahlt'}.get(g,f'{g} pro Jahr gratis' if isinstance(g,int) and g>0 else 'keine Angabe')
    return k_guest_txt(c)
def k_guest_txt(c): return 'gratis' if re.search(r'(Gast|Gäste|Begleitperson)\w* (kostenlos|gratis|frei)|1 Gast kostenlos',c.get('lgText') or '',re.I) else '–'
def k_prog(c): return re.split(r' \(|;',c.get('sammelTxt') or '–')[0].replace('°Punkt','PAYBACK-Punkt')
def k_val(c): return f'≈ {eur(round(c["sammelEur"]))} €' if c.get('sammelEur') is not None else '–'
def k_net(c): return '–' if c.get('sammelNet') is None else f'{"+" if c["sammelNet"]>=0 else "−"}{eur(round(abs(c["sammelNet"])))} €'
def k_youth(c): return 'Studierende' if re.search(r'Student|Maturant',c['titel']) else (youth(c) or '–')
COLS={
 'reisen':[('Versicherung',k_ins),('Zahlung Ausland',k_fx),('Jahresgebühr',k_fee)],
 'gratis':[('Zahlung Ausland',k_fx),('Bargeld',k_cash),('Versicherung',k_ins)],
 'ausland':[('Zahlung Ausland',k_fx),('Bargeld',k_cash),('Jahresgebühr',k_fee)],
 'punkte':[('Sammelrate',k_prog),('Wert pro Jahr¹',k_val),('Nach Gebühr¹',k_net),('Jahresgebühr',k_fee)],
 'cashback':[('Cashback',k_prog),('Wert pro Jahr¹',k_val),('Nach Gebühr¹',k_net),('Jahresgebühr',k_fee)],
 'lounge':[('Lounge-Besuche',k_lg),('Begleitung',k_guest),('Jahresgebühr',k_fee)],
 'premium':[('Versicherung',k_ins),('Lounge',lambda c:k_lg(c) if c['ex'].get('lg') else '–'),('Zahlung Ausland',k_fx),('Jahresgebühr',k_fee)],
 'studium':[('Gilt für',k_youth),('Zahlung Ausland',k_fx),('Jahresgebühr',k_fee)],
 'debit':[('Zahlung Ausland',k_fx),('Bargeld',k_cash),('Jahresgebühr',k_fee)],
}
TXTCOL=('Sammelrate','Cashback','Gilt für')
COLNOTE={'punkte':'¹ Bei 1.000 € Umsatz im Monat, 1 Punkt oder Meile = 1 Cent. „Nach Gebühr“ = Wert minus Jahresgebühr.','cashback':'¹ Bei 1.000 € Umsatz im Monat, mit allen Höchstgrenzen. „Nach Gebühr“ = Wert minus Jahresgebühr.'}
def top_of(n): return f'Top 25 von {n} bewerteten Karten' if n>25 else f'Alle {n} bewerteten Karten'
def bestenlisten(cards,lists,other_lists):
    code=L['code']; N=L['name']; S=dmy(L['stand'])
    base=f'{code}/kreditkarten/bestenlisten/'; P='../../../'
    swap=lambda rel_: rel_.replace(code+'/',('de' if code=='at' else 'at')+'/',1)
    alt=lambda rel_: alt_links(rel_.replace(code+'/','at/',1),rel_.replace(code+'/','de/',1))
    tiles=''
    for cat in CATS:
        X=lists[cat['k']]
        if not X: continue
        c=X[0]; s_=cat_stars(c,cat['w'])
        tiles+=f'<a class="catcard" href="{cat["k"]}/"><span class="ct">{E(cat["t"])}</span><b>{E(c["titel"])}</b><span>{stars(s_)} {de1(s_)}</span><small>{top_of(len(X))} · Liste ansehen →</small></a>'
    from collections import Counter
    firsts=Counter(lists[c['k']][0]['titel'] for c in CATS if lists[c['k']]); nl=sum(1 for c in CATS if lists[c['k']])
    mt_,mc_=firsts.most_common(1)[0] if firsts else ('',0)
    kurz=f'<div class="facts prose"><p><b>Kurz gesagt:</b> {nl} Bestenlisten für {N}, jede mit eigenen Gewichten. '+(f'Am häufigsten auf Platz 1 steht die {E(mt_)} ({mc_} von {nl} Listen).' if mc_>1 else f'Jede Liste hat eine andere Karte auf Platz 1.')+'</p></div>' if nl else ''
    t=f'Beste Kreditkarten {N} 2026 nach Kategorie | Finvallo'
    d=f'Die besten Kreditkarten in {N} für Reisen, ohne Jahresgebühr, ohne Auslandsgebühr, Meilen, Cashback, Lounges, Premium, Studierende und Debit.'
    ld=graph(base,t,d,[(N,f'{code}/'),('Kreditkarten',f'{code}/kreditkarten/'),('Bestenlisten',base)],[{"@type":"ItemList","name":f"Bestenlisten Kreditkarten {N}","itemListElement":[{"@type":"ListItem","position":i+1,"name":cat['h']+' in '+N,'url':f"https://finvallo.com/{base}{cat['k']}/"} for i,cat in enumerate(CATS) if lists[cat['k']]]}])
    why='''<h2>Warum steht eine Karte hier woanders als in der Gesamtwertung?</h2><div class="prose"><p>Die <a href="../">Gesamtwertung</a> gewichtet alle sieben Kriterien gleich für alle Karten. In den Bestenlisten zählt, was in der jeweiligen Kategorie wichtig ist. Eine teure Premiumkarte mit hohem Sammelwert kann deshalb bei „Meilen &amp; Punkte“ weit oben stehen und in der Gesamtwertung weiter hinten, weil dort die Jahresgebühr stärker zählt. Jede Liste zeigt ihre Gewichte.</p></div>'''
    write(base,head(t,d,base,P,ld,alt=alt(base))+f'''{HDR(P,base,swap(base))}
<div class="wrap"><main id="app">
<h1>Beste Kreditkarten in {N} nach Kategorie</h1><p class="lede">Manche Karten sind in einer Disziplin viel stärker als in der Gesamtwertung. Für jede Kategorie gewichten wir die Kriterien anders. Die Gewichte stehen jeweils dabei. Stand: {S}.</p>{kurz}<div class="catgrid">{tiles}</div>
{why}
</main>
{footer(P)}''')
    chips=lambda k: ''.join(f'<a class="chip" href="../{c["k"]}/" aria-pressed="{"true" if c["k"]==k else "false"}" style="text-decoration:none">{E(c["t"])}</a>' for c in CATS if lists[c['k']])
    for cat in CATS:
        X=lists[cat['k']]
        if not X: continue
        rel=f'{base}{cat["k"]}/'; P2='../../../../'
        t=f'{cat["h"]} in {N} 2026 | Finvallo'
        if len(t)>65: t=f'{cat["h"]} ({code.upper()}) 2026 | Finvallo'
        top=X[0]
        d=f'{cat["h"]} in {N}, Stand {S}: Platz 1 ist die {top["titel"]} ({de1(cat_stars(top,cat["w"]))} Sterne). {top_of(len(X))}.'
        if len(d)>155: d=f'{cat["h"]} in {N}: Platz 1 ist die {top["titel"]}. {top_of(len(X))}, Stand {S}.'
        if len(d)>155: d=f'{cat["h"]} in {N}: Platz 1 ist die {top["titel"]}. Stand {S}.'
        wb=''
        if cat['w'] and cat['w'].get('_bonus'):
            wb=('<details class="box howscore"><summary><span><b>So rechnen wir in dieser Kategorie</b></span><span class="lnk">anzeigen</span></summary>'
                f'<p class="note">{E(cat["d"])} Grundlage ist die Gesamtnote der Karte.</p></details>')
        elif cat['w']:
            mx=max(cat['w'].values())
            extra={'lounge':' Die Lounge-Note richtet sich nach Zahl der Gratis-Besuche und danach, ob eine Begleitperson kostenlos mitkommt.',
                   'cashback':' Sammelwert nach Jahresgebühr = was bei 1.000 € Umsatz im Monat pro Jahr zurückkommt, minus Jahresgebühr. Ab 150 € 5,0 Sterne, ab 100 € 4,5, ab 60 € 4,0, ab 30 € 3,5, ab 0 € 3,0, bis −50 € 2,5, bis −150 € 2,0, darunter 1,5. Cashback in Kryptowährung zählt wegen des Kursrisikos zur Hälfte, Höchstgrenzen sind eingerechnet.',
                   'punkte':' Sammelwert nach Jahresgebühr = Wert der Punkte oder Meilen bei 1.000 € Umsatz im Monat pro Jahr, minus Jahresgebühr und Aufpreis fürs Programm. Ein Punkt oder eine Meile zählt mit 1 Cent, ein Hilton-Punkt mit 0,4 Cent. Ab 150 € 5,0 Sterne, ab 100 € 4,5, ab 60 € 4,0, ab 30 € 3,5, ab 0 € 3,0, bis −50 € 2,5, bis −150 € 2,0, darunter 1,5. Wer Punkte gezielt in Business-Class-Flüge tauscht, holt oft mehr heraus; Guthaben und Lounges von Premiumkarten zählen in der Liste „Premium“.'}.get(cat['k'],'')
            wb='<details class="box howscore"><summary><span><b>So gewichten wir in dieser Kategorie</b></span><span class="lnk">anzeigen</span></summary><div class="wbars">'+''.join(f'<div class="wbar"><span>{E(k)}</span><span class="t"><i style="width:{v/mx*100}%"></i></span><em>{v} %</em></div>' for k,v in cat['w'].items())+'</div><p class="note">Die Sterne je Kriterium sind dieselben wie in der Gesamtwertung, nur die Gewichte ändern sich.'+extra+'</p></details>'
        cols=COLS[cat['k']]
        rows=''.join(f'<tr><td><b>{i+1}</b></td><td><a class="lnk" href="../../{c["slug"]}/">{E(c["titel"])}</a></td>'+''.join(f'<td{"" if h in TXTCOL else " class=nw"}>{E(fn(c))}</td>' for h,fn in cols)+(f'<td style="white-space:nowrap"><b>{de1(cat_stars(c,cat["w"]))} ★</b></td>' if cat['w'] else '')+f'<td style="white-space:nowrap">{de1(c["stars"])} ★</td></tr>' for i,c in enumerate(X[:25]))
        thead='<tr><th>#</th><th>Karte</th>'+''.join(f'<th>{E(h)}</th>' for h,_ in cols)+('<th>Kategorie</th>' if cat['w'] else '')+'<th>Gesamt</th></tr>'
        cnote=f'<p class="note" style="margin-top:8px">{E(COLNOTE[cat["k"]]+" " if cat["k"] in COLNOTE else "")}Bei gleicher Note steht die Karte mit der niedrigeren Jahresgebühr vorn.</p>'
        kurz=f'<b>Kurz gesagt:</b> {cat["h"]} in {N}: Platz 1 ist laut Finvallo die {top["titel"]} mit {de1(cat_stars(top,cat["w"]))} Sternen in dieser Kategorie'+(f', vor der {X[1]["titel"]}' if len(X)>1 else '')+(f' und der {X[2]["titel"]}' if len(X)>2 else '')+f'. Die Liste zeigt {"die Top 25 von "+str(len(X))+" bewerteten Karten" if len(X)>25 else "alle "+str(len(X))+" bewerteten Karten"}. Stand: {S}.'
        fq=[(f'Welche Karte ist in {N} am besten in der Kategorie „{cat["t"]}“?',f'In der Kategorie „{cat["t"]}“ liegt laut Finvallo-Bewertung die {top["titel"]} vorn, mit {de1(cat_stars(top,cat["w"]))} von 5 Sternen (Gesamtnote {de1(top["stars"])}). Stand: {S}.'),
            ('Wie entsteht diese Rangliste?',cat['d']+(' Grundlage ist die Gesamtnote der Karte.' if (cat['w'] or {}).get('_bonus') else '')),
            ('Spielen Provisionen eine Rolle?','Nein. Provisionen haben keinen Einfluss auf Sterne oder Reihenfolge, und es gibt keine bezahlten Platzierungen.')]
        ld=graph(rel,t,d,[(N,f'{code}/'),('Kreditkarten',f'{code}/kreditkarten/'),('Bestenlisten',base),(cat['t'],rel)],
                 [{"@type":"ItemList","name":cat['h']+' in '+N,"numberOfItems":len(X),"itemListElement":[{"@type":"ListItem","position":i+1,"name":c['titel'],"url":f"https://finvallo.com/{code}/kreditkarten/{c['slug']}/"} for i,c in enumerate(X[:25])]},
                  {"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in fq]}])
        other=swap(rel) if other_lists.get(cat['k']) else None
        write(rel,head(t,d,rel,P2,ld,alt=alt(rel) if other else None)+f'''{HDR(P2,rel,other or swap(base))}
<div class="wrap"><main id="app">
<div class="crumb"><span><a href="../">Bestenlisten</a> › {E(cat["t"])}</span><span>Stand {S}</span></div><h1>{E(cat["h"])} in {N}</h1><p class="lede">{E(cat["d"])}</p>
<div class="facts prose"><p>{kurz}</p></div>
<div class="chips" style="margin:14px 0">{chips(cat["k"])}</div>
{wb}
<div class="tbl wide blt" style="margin-top:16px"><table><thead>{thead}</thead><tbody>{rows}</tbody></table></div>{cnote}
<h2>Fragen und Antworten</h2><div class="faq">{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q,a in fq)}</div>
{rg_note(cat['k'],code,P2)}<p class="note" style="margin-top:18px"><a class="lnk" href="{P2}{code}/kreditkarten/">Zur Gesamtwertung aller Karten →</a> · <a class="lnk" href="{P2}{code}/kreditkarten/methodik/">So bewerten wir →</a></p>
</main>
{footer(P2)}''')

# Rückverweis von Bestenlisten auf den passenden Ratgeber (eine Seite je Suchabsicht: Liste = „welche Karte“, Ratgeber = „wie, worauf achten“)
LIST_RATGEBER={'studium':('kreditkarte-studenten','Kreditkarte als Student: Bonität ohne Einkommen, Auslandssemester und was nach dem Studium passiert'),
               'gratis':('kostenlose-kreditkarte','Kostenlose Kreditkarte: worauf du bei Gratis-Karten achten musst'),
               'ausland':('fremdwaehrung','Gebühren im Ausland verstehen'),
               'reisen':('reiseversicherung','Reiseversicherung über die Kreditkarte: Bedingungen, Summen, Altersgrenzen'),
               'lounge':('lounges','Lounge-Zugang mit der Kreditkarte'),
               'punkte':('punkte-sammeln-{code}','Punkte und Meilen mit Kreditkarte: Programme, Werte und ab wann es sich lohnt'),
               'cashback':('punkte-sammeln-{code}','Punkte, Meilen und Cashback: Programme, Werte und ab wann es sich lohnt'),
               'debit':('kartentypen','Kredit-, Charge-, Debit- oder Prepaid-Karte?')}
def rg_note(k,code,P2):
    r=LIST_RATGEBER.get(k)
    if not r: return ''
    sl=r[0].replace('{code}',code)
    if not os.path.exists(R+f'{code}/ratgeber/{sl}/index.html'): return ''
    return f'<p class="note" style="margin-top:14px">Hintergrund und Entscheidungshilfe im Ratgeber: <a class="lnk" href="{P2}{code}/ratgeber/{sl}/">{E(r[1])} →</a></p>\n'
# ---------- Tabs-Skript ----------
def tabs_js(P):
    import hashlib
    v=hashlib.sha256(open(R+'assets/tabs.js','rb').read()).hexdigest()[:8]
    return f'<script src="{P}assets/tabs.js?v={v}" defer></script>'
def patch_tabs():
    for f in glob.glob(R+'at/kreditkarten/*/index.html')+glob.glob(R+'de/kreditkarten/*/index.html'):
        s=open(f).read()
        if 'class="secnav"' not in s: continue
        o=s
        s=re.sub(r'<script src="[./]*assets/tabs\.js\?v=[a-z0-9]+" defer></script>\n?','',s)
        s=s.replace('</body>',tabs_js('../../../')+'\n</body>',1)
        if s!=o: open(f,'w').write(s)

# ---------- Sitemap, llms.txt, Kreditkarten-Rechner ----------
def sitemap(DATA):
    p=R+'sitemap.xml'; s=open(p).read()
    s=re.sub(r'<url><loc>https://finvallo\.com/(?:at|de)/kreditkarten/(?!rechner/)[^<]*</loc>.*?</url>\n?','',s)
    add=''
    for land,(cards,prov) in DATA.items():
        use(land); st=L['stand']; base=f'{land}/kreditkarten/'
        urls=[(base,st,'0.9'),(base+'anbieter/',st,'0.7'),(base+'alle/',st,'0.6'),(base+'methodik/',st,'0.6'),(base+'bestenlisten/',st,'0.8')]
        urls+=[(f'{base}bestenlisten/{c["k"]}/',st,'0.8') for c in CATS if os.path.exists(R+f'{base}bestenlisten/{c["k"]}/index.html')]
        if any(c['art']=='Business' for c in cards): urls.append((base+'business/',st,'0.6'))
        urls+=[(f'{base}{c["slug"]}/',c['geprueft'],'0.7') for c in cards]
        urls+=[(f'{base}anbieter/{x}/',max(c['geprueft'] for c in cards if c['p']==x),'0.6') for x in sorted({c['p'] for c in cards})]
        add+=''.join(f'<url><loc>https://finvallo.com/{u}</loc><lastmod>{d}</lastmod><changefreq>weekly</changefreq><priority>{pr}</priority></url>\n' for u,d,pr in urls)
    for lc in ('at','de'):
        if f'https://finvallo.com/{lc}/kreditkarten/rechner/' not in s: add+=f'<url><loc>https://finvallo.com/{lc}/kreditkarten/rechner/</loc><lastmod>{st}</lastmod><changefreq>weekly</changefreq><priority>0.7</priority></url>\n'
    s=s.replace('</urlset>',add+'</urlset>'); open(p,'w').write(s)
def llm_line(c,base):
    bits=[f'Typ: {c["typ"]}',f'Netz: {c.get("netz") or "beim Anbieter prüfen"}',
          'Jahresgebühr: '+(('0 €' if c['fee']==0 else f'{eur(c["fee"])} €')+(f' (1. Jahr {eur(c["fee1"])} €)' if c.get('fee1') is not None and c['fee1']!=c['fee'] else '') if c.get('fee') is not None else 'beim Anbieter prüfen'),
          f'Fremdwährung: {fxT(c)}',f'Bargeld: {cashT(c)}',f'Reiseversicherung: {TIER[c["tier"]][1] if c.get("tier") is not None else "beim Anbieter prüfen"}']
    if zinsT(c) and c['typ']=='Kreditkarte': bits.append(f'Zins: {zinsT(c)}')
    if c['ex'].get('lg') and c.get('lgText'): bits.append(f'Lounge: {c["lgText"]}')
    if c.get('earnText') or (c['ex'].get('cb') and c.get('cbText')): bits.append(f'Sammelrate: {c.get("earnText") or c["cbText"]}')
    bits.append(f'Bewertung: {de1(c["stars"])}/5 ({c["note"]})' if c.get('stars') else 'nicht bewertet')
    bits.append(f'geprüft am {dmy(c["geprueft"])}')
    return f'- [{c["titel"]}](https://finvallo.com/{base}{c["slug"]}/): '+'; '.join(bits)
def llms(DATA):
    de,_=DATA['de']; at,atprov=DATA['at']
    dpriv=sorted([c for c in de if c.get('rank')],key=lambda c:c['rank']); apriv=sorted([c for c in at if c.get('rank')],key=lambda c:c['rank'])
    use('at'); AL,_=cat_lists(at,'at'); use('de'); DL,_=cat_lists(de,'de')
    for fn in ['llms.txt','llms-full.txt']:
        p=R+fn; s=open(p).read()
        s=re.sub(r'\d+ Karten in Österreich und \d+ in Deutschland',f'{len(at)} Karten in Österreich und {len(de)} in Deutschland',s)
        s=re.sub(r'Stand: \d\d\.\d\d\.\d{4}\.',f'Stand: {dmy(max(LANDS["at"]["stand"],LANDS["de"]["stand"]))}.',s,count=1)
        # Deutschland
        s=re.sub(r'\n## Deutschland: Kreditkarten\n.*?(?=\n## |\Z)','',s,flags=re.S)
        top=dpriv[:15 if fn=='llms.txt' else 60]
        blk='\n## Deutschland: Kreditkarten\n'+f'- [Kreditkarten-Vergleich Deutschland](https://finvallo.com/de/kreditkarten/): Rangliste aller {len(de)} Karten, Stand {dmy(LANDS["de"]["stand"])}\n- [Alle Karten nach Anbieter](https://finvallo.com/de/kreditkarten/alle/)\n- [Bestenlisten Deutschland](https://finvallo.com/de/kreditkarten/bestenlisten/): beste Karten nach Kategorie\n- [Bewertungsmethodik Deutschland](https://finvallo.com/de/kreditkarten/methodik/)\n- [Business-Kreditkarten Deutschland](https://finvallo.com/de/kreditkarten/business/)\n- [Anbieter Deutschland](https://finvallo.com/de/kreditkarten/anbieter/)\n- [Daten als JSON](https://finvallo.com/de/daten/kreditkarten.json)\n'
        blk+=''.join(f'- [{c["h"]} in Deutschland](https://finvallo.com/de/kreditkarten/bestenlisten/{c["k"]}/): Platz 1 {DL[c["k"]][0]["titel"]}\n' for c in CATS if DL[c['k']])
        blk+=''.join(llm_line(c,'de/kreditkarten/')+'\n' for c in top)
        i=s.find('\n## Deutschland: Ratgeber'); s=s[:i]+blk+s[i:] if i>=0 else s+blk
        # Österreich
        atb='## Österreich: Bestenlisten\n'+''.join(f'- [{c["h"]} in Österreich 2026](https://finvallo.com/at/kreditkarten/bestenlisten/{c["k"]}/): Platz 1 {AL[c["k"]][0]["titel"]}. {c["d"]}\n' for c in CATS if AL.get(c['k']))
        s=re.sub(r'## Österreich: Bestenlisten\n(?:- .*\n?)*',lambda m:atb,s,count=1)
        if fn=='llms.txt':
            t10='## Österreich: Top 10 laut Bewertung\n'+''.join(llm_line(c,'at/kreditkarten/')+'\n' for c in apriv[:10])
            s=re.sub(r'## Österreich: Top 10 laut Bewertung\n(?:- .*\n?)*',lambda m:t10,s,count=1)
        else:
            names={(atprov.get(c['p']) or {}).get('name') or c['anbieter'] for c in at}
            s=re.sub(r'\n## ([^\n]+)\n(?:- [^\n]*\n?)*',lambda m:'' if m.group(1) in names else m.group(0),s)
            by={}
            for c in at: by.setdefault((atprov.get(c['p']) or {}).get('name') or c['anbieter'],[]).append(c)
            sec=''.join(f'\n## {nm}\n'+''.join(llm_line(c,'at/kreditkarten/')+'\n' for c in sorted(v,key=lambda c:-(c.get('stars') or 0))) for nm,v in sorted(by.items(),key=lambda kv:kv[0].lower()))
            j=s.find('\n## Ratgeber:'); s=s[:j]+sec+s[j:] if j>=0 else s+sec
            s=re.sub(r'^# Finvallo – alle Kreditkarten in Österreich \(Stand [^)]*\)',f'# Finvallo – alle Kreditkarten in Österreich (Stand {dmy(LANDS["at"]["stand"])})',s,flags=re.M)
        s=re.sub(r'\n## Schnellantworten.*?(?=\n## )','',s,flags=re.S)
        j=s.find('\n## ')
        s=s[:j]+f'\n## Schnellantworten (Stand {dmy(max(LANDS["at"]["stand"],LANDS["de"]["stand"]))})\n'+quick_answers(DL,dpriv,AL,apriv)+s[j:]
        s=re.sub(r'\n{3,}','\n\n',s)
        open(p,'w').write(s)
def quick_answers(DL,dpriv,AL,apriv):
    out=f'- Beste Kreditkarte Deutschland (Gesamtwertung): {dpriv[0]["titel"]} ({de1(dpriv[0]["stars"])}/5) – https://finvallo.com/de/kreditkarten/{dpriv[0]["slug"]}/\n'
    out+=f'- Beste Kreditkarte Österreich (Gesamtwertung): {apriv[0]["titel"]} ({de1(apriv[0]["stars"])}/5) – https://finvallo.com/at/kreditkarten/{apriv[0]["slug"]}/\n'
    for k,q in [('gratis','Beste kostenlose Kreditkarte'),('reisen','Beste Kreditkarte für Reisen'),('ausland','Beste Kreditkarte ohne Auslandsgebühr'),('punkte','Beste Kreditkarte für Meilen/Punkte'),('cashback','Beste Karte mit Cashback'),('lounge','Beste Kreditkarte mit Lounge-Zugang'),('debit','Beste Debitkarte/App-Bank')]:
        if DL.get(k): c=DL[k][0]; out+=f'- {q} Deutschland: {c["titel"]} – https://finvallo.com/de/kreditkarten/{c["slug"]}/\n'
        if AL.get(k): c=AL[k][0]; out+=f'- {q} Österreich: {c["titel"]} – https://finvallo.com/at/kreditkarten/{c["slug"]}/\n'
    return out
# ---------- Ablauf ----------
BEST={}
def fit_desc(t,lim=155):
    """Meta Description: ganze Sätze aufnehmen, solange die Länge ≤ lim bleibt (mindestens ein Satz, nie „…“)."""
    t=re.sub(r'\s*…\s*$','',t.strip())
    if len(t)<=lim and t.endswith(('.','!','?')): return t
    sents=re.split(r'(?<=[.!?])\s+(?=[A-ZÄÖÜ0-9„])',t); out=''
    for x in sents:
        y=(out+' '+x).strip()
        if len(y)<=lim: out=y
        else: break
    if len(out)<70:
        x=t if len(out)==0 else t
        out=''
        for sep in ('. ',': ',', ',' – ',' und '):
            i=x[:lim-1].rfind(sep)
            if i>=70: out=x[:i].rstrip(' ,:–.')+'.'; break
        else: out=x[:lim-1].rsplit(' ',1)[0].rstrip(' ,:–')+'.'
    if not out.endswith(('.','!','?')): out=out.rstrip(' ,:;–')+'.'
    return out
TERMS=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'daten','terms.json')))
def t(key,land=None):
    """Länderspezifischer Begriff aus daten/terms.json (z. B. Polizze/Police, beheben/abheben)."""
    return TERMS[land or L['code']][key]
PROVPAGE={}; REDIRECTS={}
DETAIL_LABELS=[('gruendung','Gegründet'),('lizenz_aufsicht','Lizenz und Aufsicht'),('einlagensicherung','Einlagensicherung'),('kundenservice','Kundenservice'),('besonderheiten','Besonderheiten'),('kritik','Kritik')]
KRITIK_QUELLEN=('arbeiterkammer.at','vzhh.de','ris.bka.gv.at','vki.at','verbraucherrecht.at','ogh.gv.at','bundesgerichtshof.de','vzbv.de','verbraucherzentrale')
def kritik_ok(dt):
    """Kritik (Urteile, Verbandsklagen) nur mit Quelle von AK, RIS, VKI, Gericht oder Verbraucherzentrale."""
    return any(any(q in u for q in KRITIK_QUELLEN) for u in dt.get('quellen') or [])
def details(land):
    p=os.path.join(SP,'daten',land,'anbieter-details.json')
    return json.load(open(p))['anbieter'] if os.path.exists(p) else {}
def has_details(dt): return any(v for k,v in (dt or {}).items() if k!='quellen')
COUNTS={}
def card_count(land,scope='all'):
    """Einzige Quelle für Kartenanzahlen (alle Texte, Meta, FAQ, llms.txt, JSON-Export).
    all = alle Karten des Landes inkl. Business, Debit, Prepaid (Startseite, Hubs, Vergleichsseite)
    private = Privatkarten = Liste auf der Vergleichsseite und im Kreditkarten-Rechner (inkl. „nur für bestimmte Kundengruppen“)
    special = davon nur für bestimmte Kundengruppen
    business = Business-Karten
    rated = Privatkarten in der Rangliste (bewertet, für alle erhältlich)
    Bestenlisten: Anzahl bewerteter Karten der Kategorie, siehe cat_lists()."""
    return COUNTS[land][scope]
def prepare():
    """Lädt und bewertet beide Länder (für andere Skripte wie ratgeber.py und listui.py)."""
    DATA={}
    for land in ('at','de'):
        cards=load(land); apply_korrekturen(cards,land); apply_lounge(cards,land); apply_gruppen(cards); ratecards(cards)
        LANDS[land]['stand']=max(c['geprueft'] for c in cards)
        DATA[land]=(cards,providers(land,cards))
        priv=[c for c in cards if c['art']!='Business']
        COUNTS[land]=dict(unrated=sum(1 for c in cards if c.get('stars') is None),all=len(cards),private=len(priv),special=sum(1 for c in priv if c.get('nurfuer')),
                          business=len(cards)-len(priv),rated=sum(1 for c in priv if c.get('stars') is not None and not c.get('nurfuer')))
    at={c['titel']:c['slug'] for c in DATA['at'][0] if c['art']=='Privat'}
    for c in DATA['de'][0]:
        if c['art']=='Privat' and c['titel'] in at:
            PAIR[('de',c['slug'])]=at[c['titel']]; PAIR[('at',at[c['titel']])]=c['slug']
    return DATA
# Entfernte Seiten behalten dauerhaft ihren 301 (tools/daten/entfernt.json, wird von write_redirects übernommen)
ENTF_P=os.path.join(SP,'daten','entfernt.json')
ENTF=json.load(open(ENTF_P)) if os.path.exists(ENTF_P) else {}
def clean_old(land,cards):
    keep={c['slug'] for c in cards}|RESERVED
    for d in os.listdir(R+f'{land}/kreditkarten/'):
        f=R+f'{land}/kreditkarten/{d}'
        if os.path.isdir(f) and d not in keep: shutil.rmtree(f); ENTF[f'/{land}/kreditkarten/{d}/']=f'/{land}/kreditkarten/'; print('entfernt',land,d)
    a=R+f'{land}/kreditkarten/anbieter/'
    if os.path.isdir(a):
        ps=PROVPAGE.get(land) or {c['p'] for c in cards}
        for d in os.listdir(a):
            if os.path.isdir(a+d) and d not in ps:
                shutil.rmtree(a+d); print('entfernt',land,'anbieter',d)
                if f'/{land}/kreditkarten/anbieter/{d}/' not in REDIRECTS: ENTF[f'/{land}/kreditkarten/anbieter/{d}/']=f'/{land}/kreditkarten/alle/'
        if os.path.exists(a+'index.html'): os.remove(a+'index.html')
def main():
    global BEST
    DATA=prepare()
    LISTS={}
    for land in ('at','de'): use(land); LISTS[land]=cat_lists(DATA[land][0],land)
    for land in ('at','de'):
        use(land); cards,prov=DATA[land]
        priv=sorted([c for c in cards if c.get('rank')],key=lambda c:c['rank'])
        biz=[c for c in cards if c['art']=='Business']
        lists,BEST=LISTS[land]
        by={}
        for c in cards: by.setdefault(c['p'],[]).append(c)
        DT=details(land); PROVPAGE[land]={p for p,v in by.items() if len(v)>1 or has_details(DT.get(p))}
        clean_old(land,cards)
        for c in cards: card_page(c,cards,len(priv),prov)
        list_page(cards,priv,biz)
        if biz: biz_page(biz)
        anbieter_pages(cards,prov); alle_page(cards,prov); datafile(cards)
        bestenlisten(cards,lists,LISTS['de' if land=='at' else 'at'][0])
        if land=='de': methodik_page(cards,priv)
        print(L['name'],'Karten',len(cards),'bewertet',len(priv),'business',len(biz),'Stand',L['stand'])
    patch_tabs(); sitemap(DATA); llms(DATA); write_redirects()
    # Für scripts/seo-check.mjs (A6): erlaubte Kartenanzahlen je Land aus card_count() und den Bestenlisten
    Z={land:sorted({card_count(land,x) for x in ('all','private','business','rated','special','unrated')}|{len(v) for v in LISTS[land][0].values()}) for land in ('at','de')}
    for land in ('at','de'):
        by={}
        for c in DATA[land][0]: by[c['p']]=by.get(c['p'],0)+1
        Z['anbieter_'+land]=by
    json.dump(Z,
              open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'daten','zaehler.json'),'w'),indent=1)
    return DATA

if __name__=='__main__': main()
