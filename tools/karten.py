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
    return 'unbekannt' if v is None else 'kostenlos' if v==0 else f'{eur(v)} € für 200 €' if isinstance(v,float) else 'kostenlos, aber verzinst'
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
def pros(c):
    p=[]
    f=c.get('fee')
    if f==0: p.append('Keine Jahresgebühr')
    elif c.get('fee1')==0 and f: p.append(f'Im 1. Jahr 0 € statt {eur(f)} €')
    if c.get('fx')==0: p.append('Keine Fremdwährungsgebühr')
    elif c.get('fx') is not None and c['fx']<=1.5: p.append(f'Niedrige Fremdwährungskosten ({fxT(c)})')
    v=cash200(c.get('cash'))
    if v==0: p.append('Bargeld ohne Automatengebühr' + (' (Gratis-Abhebungen begrenzt)' if (c.get('cash') or [''])[0]=='freeN' else ''))
    if (c.get('tier') or 0)>=2: p.append(TIER[c['tier']][1])
    if c.get('cbText') and c['ex'].get('cb'): p.append(c['cbText'])
    if c['ex'].get('lg') and c.get('lgText'): p.append(c['lgText'])
    if c['ex'].get('credits') and c.get('creditsText'): p.append(c['creditsText'])
    if c.get('giro') is False: p.append('Kein Girokonto beim Anbieter nötig')
    if c.get('auto') and c['typ']=='Kreditkarte': p.append('Volle Abbuchung per Lastschrift möglich')
    if c.get('auto') and c['typ']=='Charge' and c['land']=='at': p.append('Automatischer Rechnungsausgleich per Lastschrift')
    for x in c.get('extra') or []:
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
    if (c.get('tier') or 0)>=1: t.append(('p','Reiseversicherung'))
    if c.get('pay'): t.append(('a','Apple Pay &amp; Google Pay'))
    if c['ex'].get('cb'): t.append(('g','Cashback / Punkte'))
    if c['ex'].get('ml'): t.append(('p','Meilen'))
    if c['ex'].get('lg'): t.append(('a','Lounge'))
    if c.get('fee')==0: t.append(('g','Dauerhaft ohne Jahresgebühr'))
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
def ratecards(cards):
    for c in cards:
        c['ex'].setdefault('offer',bool(c.get('offer') or (c.get('fee1')==0 and c.get('fee'))))
        sc=score(c); c['score']=sc; c['stars']=sc['stars']; c['note']=note(sc['stars'])
        c['pros']=pros(c); c['cons']=cons(c)
    priv=[c for c in cards if c['art']=='Privat' and c['stars'] is not None and not c.get('nurfuer')]
    priv.sort(key=lambda c:(-c['stars'],c['fee'] if c['fee'] is not None else 1e9,-(c['score']['total'] or 0),c['titel']))
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
    out+=r('Apple / Google Pay',(E(c.get('payText')) if c.get('pay') and c.get('payText') else b(c.get('pay')) if c.get('pay') is not None else na))
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
def faq(c):
    q=[(f'Was kostet die {c["titel"]}?', (f'Die Jahresgebühr beträgt {eur(c["fee"])} €'+(f', das sind {eur(c["price"])} € im Monat' if c.get('period')=='Monat' and c.get('price') else '')+'.'+(f' Im ersten Jahr zahlst du {eur(c["fee1"])} €.' if c.get('fee1') is not None and c['fee1']!=c['fee'] else '')+(f' {c["feeNote"]}.' if c.get('feeNote') and c['land']=='de' else '')) if c.get('fee') is not None else 'Die Jahresgebühr konnten wir noch nicht bestätigen.'),
       ('Was kostet das Zahlen im Ausland?','Zahlungen in fremder Währung kosten nichts extra.' if c.get('fx')==0 else f'Pro Zahlung in fremder Währung: {fxT(c)}.' if c.get('fx') is not None else 'Das konnten wir noch nicht bestätigen.'),
       (L['cashq'],cash_answer(c)+(' Achtung: Bargeld wird ab dem Abhebungstag verzinst.' if c.get('cashInterest') else '')),
       ('Ist eine Reiseversicherung dabei?', ('Ja: '+TIER[c['tier']][1]+'. Die Details stehen im Abschnitt Versicherung.') if (c.get('tier') or 0)>0 else 'Nein, ohne Aufpreis ist keine Reiseversicherung enthalten.' if c.get('tier')==0 else 'Das konnten wir noch nicht bestätigen.'),
       ('Brauche ich ein Girokonto beim Anbieter?', 'Ja'+(f', und zwar {c["konto"]}.' if c.get('konto') else '.') if c.get('giro') else 'Nein, dein bestehendes Konto bei einer beliebigen Bank reicht.' if c.get('giro') is False else 'Das konnten wir noch nicht bestätigen.'),
       ('Wie zahle ich die Rechnung?', 'Umsätze werden direkt vom Konto abgebucht.' if c['typ'] in ('Debit','Prepaid') else ('Der Betrag wird automatisch per Lastschrift eingezogen.'+(f' {c["autoNote"]}.' if c.get('autoNote') else '')) if c.get('auto') else ('Du überweist den Betrag selbst.'+(f' Was offen bleibt, kostet {zinsT(c)}.' if zinsT(c) else '')) if c.get('auto') is False else 'Das konnten wir noch nicht bestätigen.'),
       ('Geht Apple Pay und Google Pay?','Ja, laut Anbieter.' if c.get('pay') else 'Laut unseren Unterlagen nicht.' if c.get('pay') is False else 'Das konnten wir noch nicht bestätigen.'),
       ('Gibt es Lounge-Zugang?', ('Ja: '+c['lgText'].rstrip('.')+'.' if c['ex'].get('lg') else c['lgText'].rstrip('.')+'.') if c.get('lgText') else 'Laut unseren Unterlagen nicht.')]
    if c.get('stars') is not None: q.append(('Wie kommt die Bewertung zustande?',f'Die Karte bekommt {de1(c["stars"])} von 5 Sternen. Das ist der gewichtete Durchschnitt aus 7 Kriterien, die Aufschlüsselung steht im Abschnitt Bewertung.'))
    return q
def who(c):
    a=[]; b=[]
    if c.get('fee')==0 and c.get('fx')==0: a.append('Sie passt zu allen, die ohne Jahresgebühr und ohne Auslandsgebühren zahlen wollen, etwa auf Reisen.')
    elif (c.get('tier') or 0)>=3: a.append('Sie passt zu Vielreisenden, die einen umfassenden Versicherungsschutz und Extras wollen und die Jahresgebühr dafür in Kauf nehmen.')
    elif c['typ'] in ('Debit','Prepaid'): a.append('Sie passt zu allen, die ohne Kreditrahmen bezahlen wollen und die Ausgaben direkt vom Konto abbuchen lassen.')
    elif c.get('fee') is not None and c['fee']<=30: a.append('Sie passt zu allen, die eine günstige Karte für den Alltag und Online-Shopping suchen.')
    elif c.get('stars') is None: a.append('Für eine Empfehlung fehlen uns noch bestätigte Daten.')
    else: a.append('Sie passt zu allen, denen die Leistungen dieser Karte den Preis wert sind.')
    if c['ex'].get('lg'): a.append('Wer oft fliegt, nutzt die enthaltenen Lounge-Besuche.')
    if c['ex'].get('cb'): a.append('Wer gerne sammelt, bekommt Punkte oder Geld zurück.')
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
    if len(d)>155: d=d[:152].rsplit(' ',1)[0]+' …'
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
    ld=graph(rel,t,d,[(L['name'],f'{code}/'),('Kreditkarten',f'{code}/kreditkarten/'),('Anbieter',f'{code}/kreditkarten/anbieter/'),(c['anbieter'],f'{code}/kreditkarten/anbieter/{c["p"]}/'),(c['titel'],rel)],
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
    if c['slug'] in BEST: bb=BEST[c['slug']]; best+=f'<a class="tag best" href="../bestenlisten/{bb[2]}/">🏆 Platz {bb[0]+1} für {E(bb[1])}</a>'
    pv=prov.get(c['p']) or {}
    f1=f'<span class="note">Im 1. Jahr {eur(c["fee1"])} €</span>' if c.get('fee1') is not None and c.get('fee') and c['fee1']!=c['fee'] else ''
    other=pair_rel(c)
    body=f'''{HDR(P,rel,other or ("de" if code=="at" else "at")+"/kreditkarten/")}
<div class="wrap"><main id="app">
<div class="crumb"><span><a href="../anbieter/">Anbieter</a> › <a href="../anbieter/{c["p"]}/">{E(c["anbieter"])}</a></span><span class="ok">✓ Geprüft am {dmy(gp)}</span></div>
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
  <div class="box" style="margin-top:22px"><h3>Über {E(c["anbieter"])}</h3>{f'<p style="color:var(--muted);margin:0 0 12px">{E(pv["text"])}</p>' if pv.get("text") else ""}<a class="lnk" href="../anbieter/{c["p"]}/">Alle Karten von {E(c["anbieter"])} →</a></div>
  <p class="src" style="margin-top:18px">Hauptquelle: {ext(c.get("quelle"))}{" · Preisverzeichnis: "+ext(c.get("preis")) if c.get("preis") and c.get("preis")!=c.get("quelle") else ""}{" ("+E(c["stand"])+")" if c.get("stand") else ""}.</p>
</main>
{footer(P)}'''
    write(rel,head(t,d,rel,P,ld,alt=alt_for(rel,other) if c['art']=='Privat' else None)+body)

# ---------- Listen ----------
def list_item(c,P,base=''):
    v=cash200(c.get('cash'))
    st=lambda good,txt: f'<b class="{ "good" if good else ""}">{E(txt)}</b>'
    fee='–' if c.get('fee') is None else ('€ 0,00' if c['fee']==0 else f'€ {eur(c["fee"])}')
    cash="Kostenlos" if v==0 else "0 € (verzinst)" if v=="fi" else (c.get('cashText') if c.get('cashText') and len(c['cashText'])<=40 else (eur(v)+" €") if isinstance(v,float) else (c.get('cashText') or "–"))
    rank=f'<span class="rank r{c["rank"]}">{c["rank"]}</span>' if c.get('rank') and c['rank']<=3 else (f'<span class="rank">{c["rank"]}</span>' if c.get('rank') else '')
    earn=c.get('earnText') or (c.get('cbText') if c['ex'].get('cb') else None)
    return f'''<article class="item" id="it-{c.get("id") or c["slug"]}">
    <div class="ihead"><div style="display:flex;gap:10px;align-items:center">{rank}{'<span class="reco">★ Bestbewertet</span>' if c.get('rank')==1 else ''}</div></div>
    <div class="irow">{face(c)}<div style="min-width:0"><h3 class="iname"><a href="{base}{c["slug"]}/">{E(c["titel"])}</a></h3><div class="iprov">{E(c["anbieter"])}</div>{starrow(c)}</div></div>
    <div class="tags">{f'<a class="tag best" href="{base}bestenlisten/{BEST[c["slug"]][2]}/">🏆 Platz {BEST[c["slug"]][0]+1} für {E(BEST[c["slug"]][1])}</a>' if c["slug"] in BEST else ''}<span class="tag typ">▭ {E(TYPLAB.get(c["typ"],c["typ"]).replace(" mit Teilzahlung",""))}</span><span class="tag kl">{E({"Std":"Standard"}.get(c["klasse"],c["klasse"]))}</span>{'<span class="tag out">+ Girokonto</span>' if c.get('giro') else ''}{f'<span class="tag out">{E(c["netz"])}</span>' if c.get('netz') else ''}</div>
    <div class="stats"><div><small>Jahresgebühr</small>{st(c.get("fee")==0,fee)}</div><div><small>Zahlung Ausland</small>{st(c.get("fx")==0,fxT(c) if c.get("fx") is not None else "–")}</div><div><small>Bargeld Inland</small>{st(v==0,cash)}</div></div>
    {offer(c)}
    {f'<div class="earn"><span>Sammeln</span><b>{E(earn)}</b></div>' if earn else ""}
    <ul class="checks">{"".join(f"<li>{E(x)}</li>" for x in c["pros"][:4])}</ul>
    <div class="acts"><a class="btn primary block" href="{E(c.get("quelle"))}" target="_blank" rel="noopener">Zum Anbieter ↗</a><a class="btn ghost block" href="{base}{c["slug"]}/">Details ansehen</a></div>
  </article>'''
TXT={'de':dict(list_t='Kreditkarten Vergleich Deutschland 2026 – unabhängig | Finvallo',biz_t='Business-Kreditkarten Deutschland 2026 im Vergleich | Finvallo',
               biz_lede=lambda n:f'{n} Karten für Selbstständige und Firmen, bewertet nach denselben sieben Kriterien wie Privatkarten.',biz_h='Business-Kreditkarten in Deutschland'),
     'at':dict(list_t='Kreditkarten-Vergleich Österreich 2026 | Finvallo',biz_t='Firmenkreditkarten Österreich 2026 im Vergleich | Finvallo',
               biz_lede=lambda n:'Für Selbstständige, Freiberufler und Firmen gelten andere Maßstäbe: Kosten und Abrechnung zählen mehr, Reiseschutz weniger. Wir bewerten Firmenkarten nach denselben sieben Kriterien wie Privatkarten, aber in einer eigenen Liste.',biz_h='Business- und Firmenkarten')}
def list_page(cards,priv,biz):
    code=L['code']; N=L['name']; rel=f'{code}/kreditkarten/'; P='../../'
    n=len(cards); na=len({c['anbieter'] for c in cards})
    t=TXT[code]['list_t']; top=priv[:3]
    if code=='de':
        d=f'{n} Kreditkarten in Deutschland unabhängig verglichen: Jahresgebühr, Ausland, Bargeld, Versicherung. Testsieger: {top[0]["titel"]} ({de1(top[0]["stars"])}/5).'
        if len(d)>158: d=f'{n} Kreditkarten in Deutschland unabhängig verglichen: Jahresgebühr, Ausland, Bargeld und Reiseversicherung. Mit Testsieger und Rangliste.'
    else: d=f'{n} Kredit-, Debit- und Prepaid-Karten in Österreich unabhängig verglichen: Jahresgebühr, Auslandsgebühr, Versicherung und offene Bewertung.'
    ld=graph(rel,t,d,[(N,f'{code}/'),('Kreditkarten',rel)],[{"@type":"ItemList","name":f"Beste Kreditkarten {N}","itemListElement":[{"@type":"ListItem","position":c['rank'],"name":c['titel'],"url":f"https://finvallo.com/{rel}{c['slug']}/"} for c in priv[:20]]}])
    unrated=[c for c in cards if c['art']=='Privat' and c.get('stars') is None and not c.get('nurfuer')]
    special=[c for c in cards if c['art']=='Privat' and c.get('nurfuer')]
    body=f'''{HDR(P,rel,("de" if code=="at" else "at")+"/kreditkarten/")}
<div class="wrap"><main id="app">
<h1>Kreditkarten Vergleich {N}</h1>
  <p class="lede">{n} Kredit-, Charge-, Debit- und Prepaidkarten von {na} Anbietern. Sortiert nach unserer Bewertung. Provisionen haben keinen Einfluss auf die Reihenfolge.</p>
  <details class="box howscore"><summary><span><b>So entstehen die Sterne</b><br><small>7 Kriterien, feste Regeln, offene Gewichtung</small></span><span class="lnk">anzeigen</span></summary>
    <div class="wbars">{"".join(f'<div class="wbar"><span>{k}</span><span class="t"><i style="width:{w*4}%"></i></span><em>{w} %</em></div>' for k,w in [("Jahresgebühr",25),("Reiseversicherung",20),("Zahlen im Ausland",15),("Kartenart &amp; Akzeptanz",10),("Alltag &amp; Flexibilität",10),("Bargeld",10),("Extras",10)])}</div>
    <p class="note">Jedes Kriterium bekommt nach festen Regeln 1 bis 5 Sterne. Die Gesamtnote ist der gewichtete Durchschnitt. Ab 4,5 Sternen gilt eine Karte als sehr gut. Fehlende Angaben zählen mit 2,5 Sternen, damit sie keinen Vorteil bringen. Bei gleicher Sternzahl steht die Karte mit der niedrigeren Jahresgebühr vorn.</p>
    <a class="lnk" href="{P}{code}/kreditkarten/methodik/">Alle Regeln und ein Rechenbeispiel →</a></details>
  <div class="list" id="list">{"".join(list_item(c,P) for c in priv)}</div>
  {f'<h2>Noch nicht bewertet</h2><p class="note">Für diese Karten fehlen uns bestätigte Angaben in mindestens drei Kriterien.</p><div class="list">{"".join(list_item(c,P) for c in unrated)}</div>' if unrated else ''}
  {f'<h2>Nur für bestimmte Kundengruppen</h2><p class="note">Diese Karten bekommt nicht jeder. Sie stehen deshalb nicht in der Rangliste.</p><div class="list">{"".join(list_item(c,P) for c in special)}</div>' if special else ''}
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
    items=[]
    for c in biz:
        r=c.get('rank'); c['rank']=None; items.append(list_item(c,P,'../')); c['rank']=r
    w=json.load(open(SP+f'/daten/{code}/business.json')).get('weitere') if os.path.exists(SP+f'/daten/{code}/business.json') else []
    body=f'''{HDR(P,rel,("de" if code=="at" else "at")+"/kreditkarten/business/")}
<div class="wrap"><main id="app">
<h1>{TXT[code]["biz_h"]}</h1><p class="lede">{E(TXT[code]["biz_lede"](len(biz)))}</p>
<p class="note">Mehr zu Haftung und Abrechnung im <a href="{P}{code}/ratgeber/business/">Ratgeber Firmenkreditkarten</a>.</p>
<h2>Bewertete Firmenkarten</h2><div class="list">{"".join(items)}</div>
{f'<h2>Weitere Business-Angebote</h2><p class="note" style="margin-top:-6px">Diese Angebote kurz im Überblick. Details und aktuelle Preise beim Anbieter.</p>{qa(w)}' if w else ''}
</main>
{footer(P)}'''
    write(rel,head(t,d,rel,P,ld,alt=alt_links('at/kreditkarten/business/','de/kreditkarten/business/'))+body)
def initials(n): return re.sub(r'[^A-Za-z0-9]','',n)[:2].upper()
def prow_card(c,base):
    return (f'<a class="prow" href="{base}{c["slug"]}/"><span style="width:52px">{face(c," sm")}</span><span style="min-width:0"><b>{E(c["name"] if c.get("name") and c["titel"].endswith(c["name"]) else c["titel"])}</b>'
            f'<small>{TYPLAB.get(c["typ"],c["typ"]).replace(" mit Teilzahlung","")} · {"kostenlos" if c.get("fee")==0 else (eur(c["fee"])+" €/Jahr") if c.get("fee") is not None else "Preis beim Anbieter"}</small>'
            f'<small>{(de1(c["stars"])+" ★ "+c["note"]) if c.get("stars") else "nicht bewertet"}</small></span><span class="mut">›</span></a>')
def anbieter_pages(cards,prov):
    code=L['code']; N=L['name']
    by={}
    for c in cards: by.setdefault(c['p'],[]).append(c)
    rel=f'{code}/kreditkarten/anbieter/'; P='../../../'
    t=f'Kreditkarten-Anbieter in {N} | Finvallo'
    d=f'Alle Kreditkarten-Anbieter in {N} im Überblick: Banken, Kartenherausgeber und Neobanken mit ihren Karten, Gebühren und Bewertungen.'
    def best(v): r=[x for x in v if x.get('stars')]; return max(r,key=lambda x:x['stars']) if r else None
    order=sorted(by.items(),key=lambda kv:(-(best(kv[1]) or {}).get('stars',0) if best(kv[1]) else 0,kv[1][0]['anbieter'].lower()))
    rows=''
    for p,v in order:
        pv=prov.get(p) or {}; b=best(v)
        meta=' · '.join(x for x in [pv.get('typ'),pv.get('sitz'),f'{len(v)} {"Karte" if len(v)==1 else "Karten"}'] if x)
        rows+=(f'<a class="prow" href="{p}/"><span class="plogo">{initials(pv.get("name") or v[0]["anbieter"])}</span><span style="min-width:0"><b>{E(pv.get("name") or v[0]["anbieter"])}</b><small>{E(meta)}</small>'
               +(f'<small>Beste Karte: {E(b["name"] if b.get("name") and b["titel"].endswith(b["name"]) else b["titel"])} ({de1(b["stars"])} ★)</small>' if b else '')+'</span><span class="mut">›</span></a>')
    write(rel,head(t,d,rel,P,graph(rel,t,d,[(N,f'{code}/'),('Kreditkarten',f'{code}/kreditkarten/'),('Anbieter',rel)]),alt=alt_links('at/kreditkarten/anbieter/','de/kreditkarten/anbieter/'))+f'''{HDR(P,rel,("de" if code=="at" else "at")+"/kreditkarten/anbieter/")}
<div class="wrap"><main id="app">
<h1>Kreditkarten-Anbieter in {N}</h1><p class="lede">{len(by)} Anbieter mit ihren Karten. Antippen für Details, Gebühren und alle Produkte.</p>
  <div class="plist">{rows}</div>
</main>
{footer(P)}''')
    for p,v in by.items():
        pv=prov.get(p) or {}; nm=pv.get('name') or v[0]['anbieter']
        rel2=f'{rel}{p}/'; P2='../../../../'
        v=sorted(v,key=lambda c:(-(c.get('stars') or 0),c['titel']))
        t2=f'{nm} Kreditkarten im Vergleich 2026 | Finvallo' if code=='at' else f'{nm} Kreditkarten in Deutschland 2026 | Finvallo'
        d2=f'{nm}: {len(v)} {"Karte" if len(v)==1 else "Karten"} im Vergleich, mit Jahresgebühr, Auslandsgebühr, Versicherung und Bewertung.'+(f' {pv["text"]}' if pv.get('text') else '')
        if len(d2)>158: d2=d2[:155].rsplit(' ',1)[0]+'…'
        b=best(v); fees=[c['fee'] for c in v if c.get('fee') is not None]
        facts=''.join(f'<div class="r"><span>{k}</span><span>{E(x)}</span></div>' for k,x in [('Anbietertyp',pv.get('typ')),('Sitz',pv.get('sitz')),('Karten im Vergleich',str(len(v))),
              ('Bester Score',f'{de1(b["stars"])} Sterne – {b["name"] if b.get("name") and b["titel"].endswith(b["name"]) else b["titel"]}' if b else None),
              ('Jahresgebühren',(('kostenlos' if max(fees)==0 else f'{eur(min(fees))} € bis {eur(max(fees))} €') if len(set(fees))>1 or max(fees)==0 else f'{eur(fees[0])} €') if fees else None)] if x)
        feat=''.join(x for x in [f'<span>📍 {E(pv["sitz"])}</span>' if pv.get('sitz') else '',f'<span class="b">▭ {len(v)} {"Karte" if len(v)==1 else "Karten"}</span>',f'<span class="g">★ bis {de1(b["stars"])}</span>' if b else ''])
        ld2=graph(rel2,t2,d2,[(N,f'{code}/'),('Kreditkarten',f'{code}/kreditkarten/'),('Anbieter',rel),(nm,rel2)],
                  [{"@type":"ItemList","name":f"Kreditkarten von {nm}","itemListElement":[{"@type":"ListItem","position":i+1,"name":c['titel'],"url":f"https://finvallo.com/{code}/kreditkarten/{c['slug']}/"} for i,c in enumerate(v)]}],
                  date=max(c['geprueft'] for c in v))
        write(rel2,head(t2,d2,rel2,P2,ld2)+f'''{HDR(P2,rel2,("de" if code=="at" else "at")+"/kreditkarten/anbieter/")}
<div class="wrap"><main id="app">
<div class="crumb"><span><a href="../">Anbieter</a> › {E(nm)}</span><span>Stand {dmy(max(c['geprueft'] for c in v))}</span></div>
  <div class="dh" style="grid-template-columns:64px 1fr"><span class="plogo" style="width:64px;height:64px;font-size:20px">{initials(nm)}</span><div>{f'<span class="tag">{E(pv["typ"])}</span>' if pv.get('typ') else ''}<h1 style="margin-top:8px">{E(nm)}: Kreditkarten</h1></div></div>
  <div class="feat">{feat}</div>
  {f'<a class="btn primary block" style="margin-top:16px" href="{E(pv["web"])}" target="_blank" rel="noopener">Zum Anbieter ↗</a>' if pv.get('web') else ''}
  {f'<div class="intro">{E(pv["text"])}</div>' if pv.get('text') else ''}
    <div class="cond" style="margin-top:18px"><div class="gh">Auf einen Blick</div>{facts}</div>
    <h2>Karten von {E(nm)}</h2><div class="plist">{"".join(prow_card(c,"../../") for c in v)}</div>
</main>
{footer(P2)}''')
def alle_page(cards,prov):
    code=L['code']; N=L['name']; rel=f'{code}/kreditkarten/alle/'; P='../../../'
    by={}
    for c in cards: by.setdefault(c['p'],[]).append(c)
    t=f'Alle {len(cards)} Kreditkarten in {N} nach Anbieter | Finvallo'
    d=f'Alle {len(cards)} Kreditkarten, Debit- und Prepaid-Karten in {N} nach Anbieter sortiert, mit Jahresgebühr, Auslandsgebühr und Bewertung. Stand {dmy(L["stand"])}.'
    sec=''
    for p,v in sorted(by.items(),key=lambda kv:(prov.get(kv[0]) or {}).get('name',kv[1][0]['anbieter']).lower()):
        nm=(prov.get(p) or {}).get('name') or v[0]['anbieter']
        rows=''.join(f'<tr><td><a class="lnk" href="../{c["slug"]}/">{E(c["titel"])}</a></td><td>{E(TYPLAB.get(c["typ"],c["typ"]).replace(" mit Teilzahlung",""))}</td><td>{"0 €" if c.get("fee")==0 else (eur(c["fee"])+" €") if c.get("fee") is not None else "beim Anbieter prüfen"}</td><td>{E(fxT(c)) if c.get("fx") is not None else "–"}</td><td>{(de1(c["stars"])+" ★") if c.get("stars") else "nicht bewertet"}</td></tr>' for c in sorted(v,key=lambda c:-(c.get('stars') or 0)))
        sec+=f'<h2>{E(nm)}</h2><div class="tbl"><table><thead><tr><th>Karte</th><th>Typ</th><th>Jahresgebühr</th><th>Zahlung Ausland</th><th>Bewertung</th></tr></thead><tbody>{rows}</tbody></table></div>'
    write(rel,head(t,d,rel,P,graph(rel,t,d,[(N,f'{code}/'),('Kreditkarten',f'{code}/kreditkarten/'),('Alle Karten',rel)]),alt=alt_links('at/kreditkarten/alle/','de/kreditkarten/alle/'))+f'''{HDR(P,rel,("de" if code=="at" else "at")+"/kreditkarten/alle/")}
<div class="wrap"><main id="app">
<div class="crumb"><span><a href="../../">{N}</a> › <a href="../">Kreditkarten</a> › Alle Karten</span><span>Stand {dmy(L["stand"])}</span></div><h1>Alle Kreditkarten in {N}</h1><p class="lede">{len(cards)} Karten von {len(by)} Anbietern. Ein Klick führt zur ausführlichen Kartenseite mit allen Kosten, der Versicherung und unserer Bewertung.</p>{sec}
</main>
{footer(P)}''')
def datafile(cards):
    out=[]
    for c in cards:
        out.append({k:c.get(k) for k in ['id','slug','anbieter','herausgeber','name','titel','art','typ','klasse','netz','fee','fee1','feeNote','fx','fxText','cashText','soll','effz','rahmen','giro','auto','pay','tier','stars','note','rank','pros','cons','quelle','preis','stand','geprueft']}
                   |{'klasse':{'Std':'Standard'}.get(c.get('klasse'),c.get('klasse')),'versicherung':TIER[c['tier']][1] if c.get('tier') is not None else None,'url':f'https://finvallo.com/{L["code"]}/kreditkarten/{c["slug"]}/'})
    os.makedirs(R+f'{L["code"]}/daten',exist_ok=True)
    json.dump({'quelle':f'https://finvallo.com/{L["code"]}/kreditkarten/','stand':L['stand'],'lizenz':'Frei nutzbar mit Quellenangabe Finvallo','karten':out},open(R+f'{L["code"]}/daten/kreditkarten.json','w'),ensure_ascii=False,indent=1)

# ---------- Methodik (DE; AT-Methodik ist eine feste Seite) ----------
def methodik_page(cards,priv):
    rel='de/kreditkarten/methodik/'; P='../../../'
    t='So bewerten wir Kreditkarten in Deutschland | Finvallo'
    d='Die Finvallo-Methodik für Kreditkarten in Deutschland: 7 Kriterien, feste Regeln, offene Gewichte. Mit Rechenbeispiel und Datenquellen.'
    ex=priv[0]
    rows=lambda X: ''.join(f'<tr><td>{a}</td><td>{b}</td></tr>' for a,b in X)
    rules=[('Jahresgebühr · 25 %','Was die Karte ab dem zweiten Jahr kostet. Aktionen im ersten Jahr zählen bei den Extras.',[('0 €','5,0'),('bis 25 €','4,6'),('bis 50 €','4,2'),('bis 100 €','3,6'),('bis 150 €','3,0'),('bis 250 €','2,4'),('bis 450 €','1,8'),('über 450 €','1,2')]),
           ('Zahlen im Ausland · 15 %','Was eine Zahlung in US-Dollar insgesamt extra kostet, also Auslandseinsatzentgelt und Kursaufschlag zusammen.',[('0 %','5,0'),('bis 0,5 %','4,8'),('bis 1 %','4,4'),('bis 1,5 %','4,0'),('bis 2 %','3,4'),('bis 2,7 %','2,6'),('bis 3,2 %','2,0'),('darüber','1,5')]),
           ('Reiseversicherung · 20 %','Wie umfassend der Reiseschutz ist, der ohne Aufpreis enthalten ist.',[('Premium-Reiseschutz','5,0'),('umfassender Reiseschutz (mit Mietwagen)','4,7'),('Reiseversicherung mit Reiserücktritt','4,2'),('Basis-Reiseschutz','3,0'),('keine Reiseversicherung','1,0')]),
           ('Kartenart & Akzeptanz · 10 %','Wo die Karte angenommen wird. Debit- und Prepaid-Karten gehen fast überall, werden aber bei Kautionen für Mietwagen oder Hotels oft abgelehnt.',[('Kredit- oder Charge-Karte mit Visa oder Mastercard','5,0'),('Kredit- oder Charge-Karte, Netz nicht bestätigt','4,5'),('Debit- oder Prepaid-Karte mit Visa oder Mastercard','3,5'),('American Express','3,0'),('Diners Club','2,0')]),
           ('Alltag & Flexibilität · 10 %','Durchschnitt aus bis zu drei Punkten. Was wir nicht wissen, zählt nicht mit.',[('kein Konto beim Anbieter nötig','5,0 (sonst 2,5)'),('automatische Abbuchung','5,0 (sonst 3,0)'),('Apple Pay / Google Pay bestätigt','5,0')]),
           ('Bargeld · 10 %','Was eine Abhebung von 200 € am Automaten in Deutschland kostet.',[('kostenlos','5,0'),('kostenlos, aber ab Tag 1 verzinst','4,5'),('bis 2 €','4,2'),('bis 4 €','3,4'),('bis 7 €','2,6'),('darüber','2,0')]),
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
 dict(k='reisen',t='Reisen',h='Die besten Karten für Reisen',d='Hier zählen Reiseversicherung und Auslandsgebühren am meisten.',f=lambda c:c['typ']!='Prepaid',w={'Reiseversicherung':30,'Zahlen im Ausland':25,'Jahresgebühr':15,'Kartenart & Akzeptanz':10,'Extras':10,'Bargeld':10}),
 dict(k='gratis',t='Ohne Jahresgebühr',h='Die besten Karten ohne Jahresgebühr',d='Nur Karten, die dauerhaft nichts kosten. Bewertet wie in der Gesamtwertung.',f=lambda c:c.get('fee')==0,w=None),
 dict(k='ausland',t='Ohne Auslandsgebühr',h='Die besten Karten zum Zahlen im Ausland',d='Karten mit höchstens 0,5 % Aufschlag in fremder Währung. Bargeld und Akzeptanz zählen hier mehr.',f=lambda c:c.get('fx') is not None and c['fx']<=0.5,w={'Zahlen im Ausland':30,'Bargeld':20,'Jahresgebühr':20,'Kartenart & Akzeptanz':15,'Alltag & Flexibilität':15}),
 dict(k='punkte',t='Meilen & Punkte',h='Die besten Karten für Meilen und Punkte',d='Nur Karten mit Meilen- oder Punkteprogramm auf normale Einkäufe, etwa Miles & More, Membership Rewards, Payback oder Hotelpunkte. Am meisten zählt der Sammelwert: was bei 1.000 € Umsatz im Monat pro Jahr zusammenkommt. Reines Cashback steht in der eigenen Bestenliste.',f=lambda c:c.get('sammel') is not None and c.get('sammelKind')!='cash',w={'Sammelwert nach Jahresgebühr':70,'Zahlen im Ausland':10,'Kartenart & Akzeptanz':10,'Reiseversicherung':10}),
 dict(k='cashback',t='Cashback',h='Die besten Karten mit Cashback',d='Nur Karten, die auf normale Einkäufe Geld zurückgeben. Am meisten zählt, wie viel bei 1.000 € Umsatz im Monat pro Jahr zurückkommt, mit allen Höchstgrenzen. Partner- und Reiserabatte zählen hier nicht.',f=lambda c:c.get('sammel') is not None and c.get('sammelKind')=='cash',w={'Sammelwert nach Jahresgebühr':70,'Zahlen im Ausland':10,'Kartenart & Akzeptanz':10,'Reiseversicherung':10}),
 dict(k='lounge',t='Lounge-Zugang',h='Die besten Karten mit Lounge-Zugang',d='Nur Karten mit kostenlosen Lounge-Besuchen. Am meisten zählt, wie gut der Lounge-Zugang ist: wie viele Besuche im Jahr und ob eine Begleitperson gratis mitkommt.',f=lambda c:bool(c['ex'].get('lg')),w={'Lounge-Zugang':60,'Reiseversicherung':15,'Jahresgebühr':15,'Zahlen im Ausland':10}),
 dict(k='premium',t='Premium',h='Die besten Premiumkarten',d='Top-Karten mit Lounges oder Premium-Reiseschutz. Die Jahresgebühr zählt hier weniger.',f=lambda c:c['klasse']=='Premium',w={'Reiseversicherung':30,'Extras':25,'Zahlen im Ausland':15,'Jahresgebühr':10,'Kartenart & Akzeptanz':10,'Bargeld':10}),
 dict(k='studium',f_at=lambda c:bool(re.search(r'Student|Maturant',c['titel'])),t='Studierende',h='Die besten Karten für Studierende und junge Leute',d='Karten, die für Studierende, Azubis oder junge Kunden günstiger oder kostenlos sind, etwa weil das nötige Konto bis zu einem bestimmten Alter nichts kostet. Bewertet wie in der Gesamtwertung, mit dem regulären Preis.',f=lambda c:youth(c) is not None,w=None),
 dict(k='debit',t='Debit & App-Banken',h='Die besten Debitkarten und App-Banken',d='Karten, die sofort vom Konto abbuchen. Kosten im Ausland zählen hier mehr.',f=lambda c:c['typ'] in ('Debit','Prepaid'),w={'Jahresgebühr':30,'Zahlen im Ausland':25,'Extras':15,'Reiseversicherung':15,'Alltag & Flexibilität':15}),
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
def cat_stars(c,w):
    if c.get('stars') is None: return None
    if not w: return c['stars']
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
        if land=='de' or c.get('lounge') is None: c['lounge']=lounge_score(c) if land=='de' else c.get('lounge')
        v=sammeln.value(land,c['titel'])
        c['sammel']=sammeln.note(v[0]) if v else None; c['sammelEur']=v[0] if v else None; c['sammelTxt']=v[1]['txt'] if v else None; c['sammelKind']=sammeln.kind(v[1]) if v else None; c['sammelCap']=v[1].get('cap') if v else None
        c['sammelNet']=(v[0]-(c.get('fee') or 0)) if v else None; c['sammelNetNote']=sammeln.net_note(c['sammelNet'])
    for cat in CATS:
        f=cat.get('f_'+land,cat['f'])
        X=[c for c in cards if c['art']=='Privat' and not c.get('nurfuer') and c.get('stars') is not None and f(c)]
        out[cat['k']]=sorted(X,key=lambda c:(-(cat_stars(c,cat['w']) or 0),c.get('fee') if c.get('fee') is not None else 1e9))
    best={}
    for cat in CATS:
        for i,c in enumerate(out[cat['k']][:3]):
            if c['slug'] not in best or i<best[c['slug']][0]: best[c['slug']]=(i,cat['t'],cat['k'])
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
    t=c.get('lgText') or ''
    if re.search(r'unbegrenzt|ohne Limit|unlimit',t,re.I): return 'unbegrenzt'
    m=re.search(r'(\d+)\s*(?:kostenlose |freie |Gratis-)?(?:Besuch|Zutritt|Voucher|Lounge-Besuch)',t,re.I)
    return f'{m.group(1)} pro Jahr' if m else 'ja'
def k_guest(c): return 'gratis' if re.search(r'(Gast|Gäste|Begleitperson)\w* (kostenlos|gratis|frei)|1 Gast kostenlos',c.get('lgText') or '',re.I) else '–'
def k_prog(c): return re.split(r' \(|;',c.get('sammelTxt') or '–')[0].replace('°Punkt','PAYBACK-Punkt')
def k_val(c): return f'≈ {eur(round(c["sammelEur"]))} €' if c.get('sammelEur') is not None else '–'
def k_net(c): return '–' if c.get('sammelNet') is None else f'{"+" if c["sammelNet"]>=0 else "−"}{eur(round(abs(c["sammelNet"])))} €'
def k_youth(c): return 'Studierende' if re.search(r'Student|Maturant',c['titel']) else ((youth(c) or '–')[:40])
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
        tiles+=f'<a class="catcard" href="{cat["k"]}/"><span class="ct">{E(cat["t"])}</span><b>{E(c["titel"])}</b><span>{stars(s_)} {de1(s_)}</span><small>{len(X)} Karten · Liste ansehen →</small></a>'
    t=f'Beste Kreditkarten {N} 2026 nach Kategorie | Finvallo'
    d=f'Die besten Kreditkarten in {N} für Reisen, ohne Jahresgebühr, ohne Auslandsgebühr, Meilen, Cashback, Lounges, Premium, Studierende und Debit.'
    ld=graph(base,t,d,[(N,f'{code}/'),('Kreditkarten',f'{code}/kreditkarten/'),('Bestenlisten',base)],[{"@type":"ItemList","name":f"Bestenlisten Kreditkarten {N}","itemListElement":[{"@type":"ListItem","position":i+1,"name":cat['h']+' in '+N,'url':f"https://finvallo.com/{base}{cat['k']}/"} for i,cat in enumerate(CATS) if lists[cat['k']]]}])
    why='''<h2>Warum steht eine Karte hier woanders als in der Gesamtwertung?</h2><div class="prose"><p>Die <a href="../">Gesamtwertung</a> gewichtet alle sieben Kriterien gleich für alle Karten. In den Bestenlisten zählt, was in der jeweiligen Kategorie wichtig ist. Eine teure Premiumkarte mit hohem Sammelwert kann deshalb bei „Meilen &amp; Punkte“ weit oben stehen und in der Gesamtwertung weiter hinten, weil dort die Jahresgebühr stärker zählt. Jede Liste zeigt ihre Gewichte.</p></div>'''
    write(base,head(t,d,base,P,ld,alt=alt(base))+f'''{HDR(P,base,swap(base))}
<div class="wrap"><main id="app">
<h1>Beste Kreditkarten in {N} nach Kategorie</h1><p class="lede">Manche Karten sind in einer Disziplin viel stärker als in der Gesamtwertung. Für jede Kategorie gewichten wir die Kriterien anders. Die Gewichte stehen jeweils dabei. Stand: {S}.</p><div class="catgrid">{tiles}</div>
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
        d=f'{cat["h"]} in {N}, Stand {S}: Platz 1 ist die {top["titel"]} ({de1(cat_stars(top,cat["w"]))} Sterne). {len(X)} Karten im Vergleich.'
        if len(d)>158: d=f'{cat["h"]} in {N}: Platz 1 ist die {top["titel"]}. {len(X)} Karten im Vergleich, Stand {S}.'
        if len(d)>156: d=d[:150].rsplit(' ',1)[0]+' …'
        wb=''
        if cat['w']:
            mx=max(cat['w'].values())
            extra={'lounge':' Die Lounge-Note richtet sich nach Zahl der Gratis-Besuche und danach, ob eine Begleitperson kostenlos mitkommt.',
                   'cashback':' Sammelwert nach Jahresgebühr = was bei 1.000 € Umsatz im Monat pro Jahr zurückkommt, minus Jahresgebühr. Ab 150 € 5,0 Sterne, ab 100 € 4,5, ab 60 € 4,0, ab 30 € 3,5, ab 0 € 3,0, bis −50 € 2,5, bis −150 € 2,0, darunter 1,5. Cashback in Kryptowährung zählt wegen des Kursrisikos zur Hälfte, Höchstgrenzen sind eingerechnet.',
                   'punkte':' Sammelwert nach Jahresgebühr = Wert der Punkte oder Meilen bei 1.000 € Umsatz im Monat pro Jahr, minus Jahresgebühr und Aufpreis fürs Programm. Ein Punkt oder eine Meile zählt mit 1 Cent, ein Hilton-Punkt mit 0,4 Cent. Ab 150 € 5,0 Sterne, ab 100 € 4,5, ab 60 € 4,0, ab 30 € 3,5, ab 0 € 3,0, bis −50 € 2,5, bis −150 € 2,0, darunter 1,5. Wer Punkte gezielt in Business-Class-Flüge tauscht, holt oft mehr heraus; Guthaben und Lounges von Premiumkarten zählen in der Liste „Premium“.'}.get(cat['k'],'')
            wb='<details class="box howscore"><summary><span><b>So gewichten wir in dieser Kategorie</b></span><span class="lnk">anzeigen</span></summary><div class="wbars">'+''.join(f'<div class="wbar"><span>{E(k)}</span><span class="t"><i style="width:{v/mx*100}%"></i></span><em>{v} %</em></div>' for k,v in cat['w'].items())+'</div><p class="note">Die Sterne je Kriterium sind dieselben wie in der Gesamtwertung, nur die Gewichte ändern sich.'+extra+'</p></details>'
        cols=COLS[cat['k']]
        rows=''.join(f'<tr><td><b>{i+1}</b></td><td><a class="lnk" href="../../{c["slug"]}/">{E(c["titel"])}</a></td>'+''.join(f'<td{"" if h in TXTCOL else " class=nw"}>{E(fn(c))}</td>' for h,fn in cols)+f'<td style="white-space:nowrap"><b>{de1(cat_stars(c,cat["w"]))} ★</b></td><td style="white-space:nowrap">{de1(c["stars"])} ★</td></tr>' for i,c in enumerate(X[:25]))
        thead='<tr><th>#</th><th>Karte</th>'+''.join(f'<th>{E(h)}</th>' for h,_ in cols)+'<th>Kategorie</th><th>Gesamt</th></tr>'
        cnote=f'<p class="note" style="margin-top:8px">{E(COLNOTE[cat["k"]])}</p>' if cat['k'] in COLNOTE else ''
        kurz=f'<b>Kurz gesagt:</b> {cat["h"]} in {N}: Platz 1 ist laut Finvallo die {top["titel"]} mit {de1(cat_stars(top,cat["w"]))} Sternen in dieser Kategorie'+(f', vor der {X[1]["titel"]}' if len(X)>1 else '')+(f' und der {X[2]["titel"]}' if len(X)>2 else '')+f'. Verglichen haben wir {len(X)} Karten. Stand: {S}.'
        fq=[(f'Welche Karte ist in {N} am besten in der Kategorie „{cat["t"]}“?',f'Laut Finvallo-Bewertung ist es die {top["titel"]} mit {de1(cat_stars(top,cat["w"]))} von 5 Sternen in dieser Kategorie. Stand: {S}.'),
            ('Wie entsteht diese Rangliste?',cat['d']+' Grundlage sind dieselben Sterne je Kriterium wie in der Gesamtwertung, nur anders gewichtet.'),
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
<p class="note" style="margin-top:18px"><a class="lnk" href="{P2}{code}/kreditkarten/">Zur Gesamtwertung aller Karten →</a> · <a class="lnk" href="{P2}{code}/kreditkarten/methodik/">So bewerten wir →</a></p>
</main>
{footer(P2)}''')

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
def prepare():
    """Lädt und bewertet beide Länder (für andere Skripte wie ratgeber.py und listui.py)."""
    DATA={}
    for land in ('at','de'):
        cards=load(land); ratecards(cards)
        LANDS[land]['stand']=max(c['geprueft'] for c in cards)
        DATA[land]=(cards,providers(land,cards))
    at={c['titel']:c['slug'] for c in DATA['at'][0] if c['art']=='Privat'}
    for c in DATA['de'][0]:
        if c['art']=='Privat' and c['titel'] in at:
            PAIR[('de',c['slug'])]=at[c['titel']]; PAIR[('at',at[c['titel']])]=c['slug']
    return DATA
def clean_old(land,cards):
    keep={c['slug'] for c in cards}|RESERVED
    for d in os.listdir(R+f'{land}/kreditkarten/'):
        f=R+f'{land}/kreditkarten/{d}'
        if os.path.isdir(f) and d not in keep: shutil.rmtree(f); print('entfernt',land,d)
    a=R+f'{land}/kreditkarten/anbieter/'
    if os.path.isdir(a):
        ps={c['p'] for c in cards}
        for d in os.listdir(a):
            if os.path.isdir(a+d) and d not in ps: shutil.rmtree(a+d); print('entfernt',land,'anbieter',d)
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
        clean_old(land,cards)
        for c in cards: card_page(c,cards,len(priv),prov)
        list_page(cards,priv,biz)
        if biz: biz_page(biz)
        anbieter_pages(cards,prov); alle_page(cards,prov); datafile(cards)
        bestenlisten(cards,lists,LISTS['de' if land=='at' else 'at'][0])
        if land=='de': methodik_page(cards,priv)
        print(L['name'],'Karten',len(cards),'bewertet',len(priv),'business',len(biz),'Stand',L['stand'])
    patch_tabs(); sitemap(DATA); llms(DATA)
    return DATA

if __name__=='__main__': main()
