# Erzeugt den Kreditkartenvergleich Deutschland aus scratchpad/research/*.json (+ de_cards.json)
import json,glob,os,re,html,sys,datetime
sys.path.insert(0,os.path.dirname(__file__))
from score import score,note,eur,pct,cash200,TIER
SP=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','public')+'/'
STAND='2026-10-12'; STAND_DE='12.10.2026'
E=lambda s: html.escape(str(s)) if s is not None else ''
def slug(s):
    s=s.lower().replace('é','e').replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss').replace('&','und').replace('+','plus')
    return re.sub(r'[^a-z0-9]+','-',s).strip('-')
# ---------- Daten laden ----------
def load():
    cards=[]
    for f in sorted(glob.glob(SP+'/de-recherche/[A-G].json')):
        try: cards+=json.load(open(f))
        except Exception as e: print('FEHLER',f,e)
    if os.path.exists(SP+'/de-recherche/de_cards.json'): cards+=json.load(open(SP+'/de-recherche/de_cards.json'))
    out={};
    for c in cards:
        if c.get('status','aktiv')!='aktiv': continue
        import overrides; overrides.apply(c)
        c.setdefault('art','Privat'); c.setdefault('ex',{}); c.setdefault('sek',[])
        c['titel']=overrides.title(c,slug)
        c['slug']=slug(c['titel'])
        if c['slug'] in out: print('DOPPELT',c['slug']); continue
        out[c['slug']]=c
    return list(out.values())
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
def de1(x): return f'{x:.1f}'.replace('.',',')
def starrow(c):
    if c.get('stars') is None: return f'<div class="stars">{stars(0)} <span class="nt nr">Nicht bewertet · zu wenige bestätigte Daten</span></div>'
    return f'<div class="stars">{stars(c["stars"])} <b>{de1(c["stars"])}</b> <span class="nt">{c["note"]}</span></div>'
def kcls(c):
    if c['klasse']=='Premium': return 'k-Premium'
    if c['typ'] in ('Debit','Prepaid'): return 'k-Debit'
    return {'Gold':'k-Gold','Std':'k-Std','Basis':'k-Basis'}.get(c['klasse'],'k-Std')
def face(c,cls=''):
    return f'<div class="face {kcls(c)}{cls}" aria-hidden="true"><span class="pn">{E(c["anbieter"])}</span><span class="chipc"></span><span class="nw">{E((c.get("netz") or "").upper())}</span></div>'
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
def zinsT(c):
    if c.get('soll') and c.get('effz'): return f'{pct(c["soll"])} Soll / {pct(c["effz"])} effektiv'
    if c.get('effz'): return f'{pct(c["effz"])} effektiv'
    return None
TYPLAB={'Kreditkarte':'Kreditkarte mit Teilzahlung','Charge':'Charge-Karte','Debit':'Debitkarte','Prepaid':'Prepaid-Karte'}
def sekb(c,*f): return '<span class="sek" title="Nur aus Sekundärquelle">Sek.</span>' if any(x in c['sek'] for x in f) else ''
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
    for x in c.get('extra') or []:
        if x not in p: p.append(x)
    return p[:9]
def cons(c):
    k=[]
    if c.get('auto') is False and c['typ'] in ('Kreditkarte','Charge'): k.append('Die Rechnung wird nicht abgebucht, du musst sie selbst pünktlich überweisen')
    z=zinsT(c)
    if c['typ']=='Kreditkarte' and z: k.append(f'Teilzahlung ist teuer: {z}')
    if c.get('cashInterest'): k.append('Bargeld wird ab dem Abhebungstag verzinst')
    if c.get('fx') is not None and c['fx']>=1.75: k.append(f'Fremdwährungsgebühr: {fxT(c)}')
    v=cash200(c.get('cash'))
    if isinstance(v,float) and v>=3: k.append(f'Bargeld am Automaten kostet {cashT(c)}')
    if c.get('giro'): k.append('Nur mit Konto beim Anbieter' + (f' ({c["konto"]})' if c.get('konto') else ''))
    if c.get('tier')==0 and (c.get('fee') or 0)>0: k.append('Keine Reiseversicherung inklusive')
    if 'American Express' in (c.get('netz') or ''): k.append('American Express wird seltener akzeptiert als Visa oder Mastercard')
    if c['typ'] in ('Debit','Prepaid'): k.append('Bei Kautionen für Mietwagen oder Hotel oft abgelehnt')
    for x in c.get('cons_extra') or []:
        if x not in k: k.append(x)
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
    s=f'Die {c["titel"]} ist eine {TYPLAB.get(c["typ"],c["typ"])} ({c["netz"]}) für Kund:innen in Deutschland. '
    f=c.get('fee')
    s+= 'Sie hat keine Jahresgebühr. ' if f==0 else (f'Sie kostet {eur(f)} € pro Jahr' + (f' ({c["feeNote"]})' if c.get('feeNote') else '') + '. ') if f is not None else ''
    s+= 'Zahlungen in fremder Währung kosten nichts extra. ' if c.get('fx')==0 else (f'Zahlungen in fremder Währung kosten {fxT(c)}. ' if c.get('fx') is not None else '')
    s+= f'Bargeld abheben: {cashT(c)}. '
    if c.get('tier') is not None: s+= f'Reiseversicherung: {TIER[c["tier"]][1]}. '
    return s
# ---------- Rechner-Datensatz (für /at/kreditkarten/rechner/, Land DE) ----------
def ratecards(cards):
    for c in cards:
        sc=score(c); c['score']=sc; c['stars']=sc['stars']; c['note']=note(sc['stars'])
        c['pros']=pros(c); c['cons']=cons(c)
    priv=[c for c in cards if c['art']=='Privat' and c['stars'] is not None and not c.get('nurfuer')]
    priv.sort(key=lambda c:(-(c['score']['total'] or 0),-c['stars'],c['fee'] if c['fee'] is not None else 1e9))
    for i,c in enumerate(priv): c['rank']=i+1
    for c in cards: c.setdefault('rank',None)
    return priv
# ---------- HTML ----------
ATPAIR={}
def at_pairs():
    for f in glob.glob(R+'at/kreditkarten/*/index.html'):
        m=re.search(r'<title>(.*?) im Vergleich 2026',open(f).read())
        if m: ATPAIR[html.unescape(m.group(1))]=os.path.relpath(os.path.dirname(f),R)+'/'
def head(title,desc,canon,P,ld,lang='de-DE',alt=None):
    css=open(R+'index.html').read(); v=re.search(r'site\.css\?v=([a-z0-9]+)',css).group(1); fv=re.search(r'favicon\.svg\?v=([a-z0-9]+)',css).group(1)
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1">
<link rel="canonical" href="https://finvallo.com/{canon}">{alt or ''}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Finvallo">
<meta property="og:locale" content="de_DE">
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
def graph(canon,title,desc,crumbs,extra=None):
    g=[{"@type":"Organization","@id":"https://finvallo.com/#org","name":"Finvallo","url":"https://finvallo.com/","logo":"https://finvallo.com/assets/logo.svg"},
       {"@type":"WebSite","@id":"https://finvallo.com/#website","name":"Finvallo","url":"https://finvallo.com/","inLanguage":"de","publisher":{"@id":"https://finvallo.com/#org"}},
       {"@type":"WebPage","@id":f"https://finvallo.com/{canon}#page","url":f"https://finvallo.com/{canon}","name":title,"description":desc,"inLanguage":"de-DE","isPartOf":{"@id":"https://finvallo.com/#website"},"dateModified":STAND,"publisher":{"@id":"https://finvallo.com/#org"}},
       {"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":f"https://finvallo.com/{u}"} for i,(n,u) in enumerate(crumbs)]}]
    if extra: g+=extra
    return {"@context":"https://schema.org","@graph":g}
LAND_DE=lambda P:(f'<div class="land" role="group" aria-label="Land wählen"><a href="{P}at/" hreflang="de-AT" aria-current="false" title="Österreich">AT</a><a href="{P}de/" hreflang="de-DE" aria-current="true" title="Deutschland">DE</a></div>')
def footer(P):
    return f'''<footer>
<span><b>finvallo</b> · Unabhängiger Finanzvergleich für Deutschland</span>
<span>Stand {STAND_DE} · Bewertung unabhängig von Provisionen, keine bezahlten Platzierungen · Mit * markierte Links sind Affiliate-Links.</span>
<span>Keine Finanzberatung. Konditionen vor Abschluss beim Anbieter prüfen. „Sek.“ = Wert nur aus Vergleichsportal oder Fachblog.</span>
<nav aria-label="Fußzeile"><a href="{P}de/kreditkarten/methodik/">So bewerten wir</a><a href="{P}de/kreditkarten/faktencheck/">Faktencheck</a><a href="{P}so-verdienen-wir-geld/">So verdienen wir Geld</a><a href="{P}ueber-uns/">Über uns</a><a href="{P}impressum/">Impressum</a><a href="{P}datenschutz/">Datenschutz</a><a href="{P}llms.txt">Für KI-Assistenten</a></nav>
</footer>
</div>
</body>
</html>
'''
def write(rel,html_):
    os.makedirs(R+rel,exist_ok=True); open(R+rel+'index.html','w').write(html_)
def ext(u,t=None):
    if not u: return ''
    d=re.sub(r'^https?://(www\.)?','',u).split('/')[0]
    return f'<a href="{E(u)}" target="_blank" rel="noopener">{E(t or d)} ↗</a>'
def cond(c):
    r=lambda k,v: f'<div class="r"><span>{k}</span><span>{v}</span></div>'
    b=lambda v: 'ja' if v else 'nein' if v is False else '–'
    lg=c.get('lgText') or ('–')
    out='<div class="cond" style="margin-bottom:14px"><div class="gh">Kosten</div>'
    out+=r('Jahresgebühr',E(feeT(c))+(f' <small class="mut">({E(c["feeNote"])})</small>' if c.get('feeNote') else '')+sekb(c,'fee','feeNote'))
    out+=r('1. Jahr',(f'{eur(c["fee1"])} €' if c.get('fee1') is not None else '–')+sekb(c,'fee1'))
    out+=r('Willkommensangebot',E(c.get('bonus') or '–')+sekb(c,'bonus'))
    out+=r('Zahlen im Ausland',E(fxT(c))+sekb(c,'fx','fxText'))
    out+=r('Bargeld abheben',E(cashT(c))+sekb(c,'cash','cashText'))
    if c.get('konto'): out+=r('Nötiges Konto',E(c['konto'])+sekb(c,'konto'))
    out+='</div><div class="cond" style="margin-bottom:14px"><div class="gh">Bezahlen</div>'
    out+=r('Abrechnung',('automatisch per Lastschrift' if c.get('auto') else 'per Überweisung' if c.get('auto') is False else '–')+sekb(c,'auto'))
    if c.get('autoNote'): out+=r('Hinweis',E(c['autoNote']))
    out+=r('Teilzahlung','möglich' if c['typ']=='Kreditkarte' else 'nein')
    z=zinsT(c)
    if z: out+=r('Effektiver Zins',E(z)+sekb(c,'soll','effz'))
    if c.get('zinsfrei'): out+=r('Zinsfrei',f'bis {c["zinsfrei"]} Tage'+sekb(c,'zinsfrei'))
    if c.get('rahmen'): out+=r('Kreditrahmen',E(c['rahmen'])+sekb(c,'rahmen'))
    out+='</div><div class="cond" style="margin-bottom:14px"><div class="gh">Extras</div>'
    out+=r('Cashback / Punkte',E(c.get('cbText') or ('ja' if c['ex'].get('cb') else 'nein'))+sekb(c,'cbText'))
    out+=r('Meilen',b(bool(c['ex'].get('ml'))))
    out+=r('Lounge',E(lg)+sekb(c,'lgText'))
    if c.get('creditsText'): out+=r('Guthaben',E(c['creditsText'])+sekb(c,'creditsText'))
    out+=r('Reiseversicherung',TIER[c['tier']][1] if c.get('tier') is not None else '–')
    out+='</div><div class="cond" style="margin-bottom:14px"><div class="gh">Voraussetzungen</div>'
    out+=r('Kartentyp',TYPLAB.get(c['typ'],c['typ']))+r('Kartennetz',E(c.get('netz')))
    out+=r('Girokonto beim Anbieter','nötig' if c.get('giro') else 'nicht nötig' if c.get('giro') is False else '–')
    out+=r('Bonitätsprüfung (Schufa)','ja' if c['typ'] in ('Kreditkarte','Charge') else 'meist nur bei Kontoeröffnung')
    out+=r('Für Kautionen','in der Regel ja' if c['typ'] in ('Kreditkarte','Charge') and 'American' not in c['netz'] else 'oft nicht' if c['typ'] in ('Debit','Prepaid') else 'eingeschränkt')
    out+=r('Apple / Google Pay',(E(c.get('payText')) if c.get('pay') and c.get('payText') else b(c.get('pay')))+sekb(c,'pay'))
    if c.get('herausgeber'): out+=r('Herausgeber',E(c['herausgeber']))
    return out+'</div>'
def scorebox(c,P):
    s=c['score']
    if c.get('stars') is None:
        return f'<div class="box"><h3>Bewertung</h3><p style="color:var(--muted)">Für eine Bewertung brauchen wir die Jahresgebühr und bestätigte Daten in mindestens 5 der 7 Kriterien. Hier fehlen noch Angaben.</p></div>'
    rows=''.join(f'<tr><td><b>{E(p["k"])}</b><br><small class="mut">{E(p["v"])}</small></td><td>{p["w"]} %</td><td style="white-space:nowrap">{stars(p["s"])} {de1(p["s"])}</td></tr>' for p in s['parts'])
    return f'''<div class="box"><div class="scorehead"><div class="big">{de1(c["stars"])}<small>/5</small></div><div>{stars(c["stars"])}<div style="margin-top:4px"><span class="badge ">{c["note"]}</span></div></div></div>
  <div class="tbl" style="margin:14px 0"><table class="sct"><thead><tr><th>Kriterium</th><th>Gewicht</th><th>Sterne</th></tr></thead><tbody>
  {rows}
  <tr><td><b>Gesamt</b><br><small class="mut">gewichteter Durchschnitt</small></td><td>100 %</td><td><b>{de1(c["stars"])}</b></td></tr></tbody></table></div><a class="lnk" href="{P}de/kreditkarten/methodik/">ⓘ So funktioniert das Bewertungssystem</a></div>'''
def similar(c,cards):
    pool=[x for x in cards if x is not c and x['art']==c['art'] and x.get('stars') is not None]
    pool.sort(key=lambda x:(x['typ']!=c['typ'],abs((x['fee'] or 0)-(c['fee'] or 0))>60,-(x['stars'] or 0)))
    return pool[:4]
def faq(c):
    q=[(f'Was kostet die {c["titel"]}?', f'Die Jahresgebühr beträgt {eur(c["fee"])} €.'+(f' {c["feeNote"]}.' if c.get('feeNote') else '') if c.get('fee') is not None else 'Die Jahresgebühr konnten wir noch nicht bestätigen.'),
       ('Was kostet das Zahlen im Ausland?','Zahlungen in fremder Währung kosten nichts extra.' if c.get('fx')==0 else f'Pro Zahlung in fremder Währung: {fxT(c)}.'),
       ('Kann ich kostenlos Bargeld abheben?',f'Das kostet: {cashT(c)}.'+(' Achtung: Bargeld wird ab dem Abhebungstag verzinst.' if c.get('cashInterest') else '')),
       ('Ist eine Reiseversicherung dabei?', ('Ja: '+TIER[c['tier']][1]+'. Die Details stehen im Abschnitt Versicherung.') if (c.get('tier') or 0)>0 else 'Nein, ohne Aufpreis ist keine Reiseversicherung enthalten.'),
       ('Brauche ich ein Girokonto beim Anbieter?', 'Ja'+(f', und zwar {c["konto"]}.' if c.get('konto') else '.') if c.get('giro') else 'Nein, dein bestehendes Konto bei einer beliebigen Bank reicht.' if c.get('giro') is False else 'Das konnten wir noch nicht bestätigen.'),
       ('Wie zahle ich die Rechnung?', ('Der Betrag wird automatisch per Lastschrift eingezogen.'+(f' {c["autoNote"]}.' if c.get('autoNote') else '')) if c.get('auto') else ('Du überweist den Betrag selbst.'+(f' Was offen bleibt, kostet {zinsT(c)}.' if zinsT(c) else '')) if c.get('auto') is False else 'Umsätze werden direkt vom Konto abgebucht.' if c['typ'] in ('Debit','Prepaid') else 'Das konnten wir noch nicht bestätigen.'),
       ('Geht Apple Pay und Google Pay?','Ja, laut Anbieter.' if c.get('pay') else 'Laut unseren Unterlagen nicht.' if c.get('pay') is False else 'Das konnten wir noch nicht bestätigen.'),
       ('Gibt es Lounge-Zugang?', c.get('lgText') or 'Laut unseren Unterlagen nicht.')]
    if c.get('stars') is not None: q.append(('Wie kommt die Bewertung zustande?',f'Die Karte bekommt {de1(c["stars"])} von 5 Sternen. Das ist der gewichtete Durchschnitt aus 7 Kriterien, die Aufschlüsselung steht im Abschnitt Bewertung.'))
    return q
def who(c):
    a=[]; b=[]
    if c.get('fee')==0 and c.get('fx')==0: a.append('Sie passt zu allen, die ohne Jahresgebühr und ohne Auslandsgebühren zahlen wollen, etwa auf Reisen.')
    elif (c.get('tier') or 0)>=3: a.append('Sie passt zu Vielreisenden, die einen umfassenden Versicherungsschutz und Extras wollen und die Jahresgebühr dafür in Kauf nehmen.')
    elif c['typ'] in ('Debit','Prepaid'): a.append('Sie passt zu allen, die ohne Kreditrahmen bezahlen wollen und die Ausgaben direkt vom Konto abbuchen lassen.')
    else: a.append('Sie passt zu allen, denen die Leistungen dieser Karte den Preis wert sind.')
    if c['ex'].get('cb'): a.append('Wer gerne sammelt, bekommt Punkte oder Geld zurück.')
    if c['typ']=='Kreditkarte' and not c.get('auto'): b.append('Wenn du Termine leicht vergisst, nimm besser eine Karte mit automatischer Abbuchung. Hier kosten offene Beträge hohe Zinsen.')
    if c['typ']=='Kreditkarte' and c.get('auto'): b.append('Achte darauf, die Rückzahlung auf 100 % zu stellen, sonst fallen Zinsen an.')
    if c['typ'] in ('Debit','Prepaid'): b.append('Für Mietwagen- und Hotelkautionen ist eine echte Kredit- oder Charge-Karte besser.')
    if (c.get('fx') or 0)>=1.75: b.append('Für Reisen außerhalb des Euroraums gibt es günstigere Karten.')
    return a,b
def card_page(c,cards,nrated):
    rel=f'de/kreditkarten/{c["slug"]}/'; P='../../../'
    t=f'{c["titel"]} in Deutschland 2026 | Finvallo'
    if len(t)>65: t=f'{c["titel"]} (DE) 2026 | Finvallo'
    if len(t)>65: t=f'{c["titel"]} | Finvallo'
    bits=[('ohne Jahresgebühr' if c.get('fee')==0 else f'{eur(c["fee"])} € im Jahr') if c.get('fee') is not None else None,
          ('0 % im Ausland' if c.get('fx')==0 else f'{pct(c["fx"])} im Ausland') if c.get('fx') is not None else None,
          TIER[c['tier']][1] if c.get('tier') else None]
    d=f'{c["titel"]} in Deutschland: {", ".join(b for b in bits if b)}.'+(f' Bewertung {de1(c["stars"])}/5.' if c.get('stars') else '')+' Alle Kosten, Vor- und Nachteile.'
    if len(d)>155: d=d.replace(' Alle Kosten, Vor- und Nachteile.',' Kosten, Vor- und Nachteile.')
    if len(d)>155: d=d.replace(' Kosten, Vor- und Nachteile.','')
    if len(d)>155: d=d[:152].rsplit(' ',1)[0]+' …'
    pc=c['pros']; kc=c['cons']
    ld_card={"@type":"CreditCard","@id":f"https://finvallo.com/{rel}#card","name":c['titel'],"url":f"https://finvallo.com/{rel}",
      "provider":{"@type":"BankOrCreditUnion","name":c.get('herausgeber') or c['anbieter'],"url":c.get('quelle')},"areaServed":{"@type":"Country","name":"Deutschland"},
      "category":TYPLAB.get(c['typ'],c['typ']),"feesAndCommissionsSpecification":f"Jahresgebühr {feeT(c)}; Fremdwährung {fxT(c)}; Bargeld {cashT(c)}"}
    if c.get('effz'): ld_card['annualPercentageRate']=c['effz']
    if c.get('fee') is not None: ld_card['offers']={"@type":"Offer","price":c['fee'],"priceCurrency":"EUR","description":"Jahresgebühr","availability":"https://schema.org/InStock"}
    if c.get('stars') is not None:
        ld_card['review']={"@type":"Review","author":{"@id":"https://finvallo.com/#org"},"datePublished":STAND,"name":f"{c['titel']} im Finvallo-Vergleich","reviewRating":{"@type":"Rating","ratingValue":c['stars'],"bestRating":5,"worstRating":1},
          "positiveNotes":{"@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"name":x} for i,x in enumerate(pc[:5])]},
          "negativeNotes":{"@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"name":x} for i,x in enumerate(kc[:5])]}}
    fq=faq(c)
    ld=graph(rel,t,d,[('Deutschland','de/'),('Kreditkarten','de/kreditkarten/'),('Anbieter','de/kreditkarten/anbieter/'),(c['anbieter'],f'de/kreditkarten/anbieter/{c["p"]}/'),(c['titel'],rel)],
             [ld_card,{"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in fq]}])
    rk=f', Platz {c["rank"]} von {nrated} bewerteten Privatkarten in Deutschland' if c.get('rank') else ''
    glance=summary(c)+(f'Finvallo bewertet sie mit {de1(c["stars"])} von 5 Sternen ({c["note"]}){rk}. ' if c.get('stars') else '')+f'Stand: {STAND_DE}.'
    a,b=who(c)
    how=''
    if c['typ']=='Kreditkarte':
        how=f'Die Karte ist eine echte Kreditkarte mit Teilzahlung. Nach der Bonitätsprüfung (Schufa) bekommst du einen Kreditrahmen{" von "+c["rahmen"] if c.get("rahmen") else ""}. '+('Die Monatsrechnung kann per Lastschrift eingezogen werden. ' if c.get('auto') else 'Die Monatsrechnung zahlst du selbst per Überweisung. ')+f'Zahlst du alles pünktlich, kostet ein Einkauf keine Zinsen{", und du hast bis zu "+str(c["zinsfrei"])+" Tage Zeit" if c.get("zinsfrei") else ""}. Zahlst du nur einen Teil, fallen Zinsen an{", und zwar "+zinsT(c) if zinsT(c) else ""}.'
    elif c['typ']=='Charge':
        how='Die Karte ist eine Charge-Karte: Du bekommst einen Verfügungsrahmen, und einmal im Monat wird der ganze Betrag von deinem Konto abgebucht. Zinsen fallen dabei nicht an.'
    elif c['typ']=='Debit':
        how='Die Karte ist eine Debitkarte: Jede Zahlung wird direkt von deinem Konto abgebucht. Es gibt keinen Kreditrahmen und keine Zinsen, dafür lehnen manche Mietwagenfirmen und Hotels sie für Kautionen ab.'
    else:
        how='Die Karte ist eine Prepaid-Karte: Du lädst Guthaben auf und kannst nur so viel ausgeben, wie darauf ist.'
    sim=similar(c,cards)
    simtbl=''.join(f'<tr><td><a class="lnk" href="../{x["slug"]}/">{E(x["titel"])}</a></td><td>{eur(x["fee"]) if x.get("fee") is not None else "–"} €</td><td>{E(fxT(x))}</td><td>{E(cashT(x))}</td><td style="white-space:nowrap">{de1(x["stars"])} ★ {x["note"]}</td></tr>' for x in sim[:3])
    mini=''.join(f'<a class="mini-card" href="../{x["slug"]}/">{face(x)}<b>{E(x["titel"])}</b>{starrow(x)}<span>{eur(x["fee"]) if x.get("fee") is not None else "–"} € im Jahr</span></a>' for x in sim)
    ins=''
    if c.get('insText'):
        ins=f'<div class="qa"><div><h4>Was ist versichert?</h4><p>{E(c["insText"])}{sekb(c,"insText")}</p></div></div>'+(f'<p class="src" style="margin-top:8px">Quelle: {ext(c["insQuelle"])}</p>' if c.get('insQuelle') else '')
    else: ins='<p>Ohne Aufpreis ist keine Reiseversicherung enthalten.</p>' if c.get('tier')==0 else '<p>Zur Versicherung haben wir noch keine bestätigten Angaben.</p>'
    hdr=HDR(P,rel)
    best='<span class="reco">★ Bestbewertet</span>' if c.get('rank')==1 else ''
    if c['slug'] in BEST: bb=BEST[c['slug']]; best+=f'<a class="tag best" href="../bestenlisten/{bb[2]}/">🏆 Platz {bb[0]+1} für {E(bb[1])}</a>'
    body=f'''{hdr}
<div class="wrap"><main id="app">
<div class="crumb"><span><a href="../anbieter/">Anbieter</a> › <a href="../anbieter/{c["p"]}/">{E(c["anbieter"])}</a></span><span class="ok">✓ Geprüft am {STAND_DE}</span></div>
  <div class="dh">{face(c)}<div style="min-width:0"><div class="tags">{best}<span class="tag typ">{TYPLAB.get(c["typ"],c["typ"])}</span><span class="by">von {E(c["anbieter"])}</span></div>
    <h1>{E(c["titel"])}</h1>{starrow(c)}</div></div>
  <div class="feat">{feats(c)}</div>{f'<p class="note"><b>Hinweis:</b> {E(c["nurfuer"])}.</p>' if c.get('nurfuer') else ''}
  <div class="box feebox"><small>Jahresgebühr</small><span class="big{" good" if c.get("fee")==0 else ""}">{E(feeT(c).replace(" pro Jahr"," / Jahr"))}</span>
    <a class="btn primary block" href="{E(c.get("quelle"))}" target="_blank" rel="noopener">Zum Anbieter ↗</a>
    <div class="actrow"><a class="plink" href="{E(c.get("preis") or c.get("quelle"))}" target="_blank" rel="noopener">{"Preise &amp; Gebühren (PDF) ↗" if (c.get("preis") or "").lower().endswith(".pdf") else "Konditionen beim Anbieter ↗"}</a></div></div>
  <nav class="secnav" aria-label="Abschnitte"><a href="#s-ueb" class="on">Überblick</a><a href="#s-kond">Konditionen</a><a href="#s-vers">Versicherung</a><a href="#s-bew">Bewertung</a><a href="#s-faq">Fragen</a></nav>
  <section class="facts box" aria-label="Auf einen Blick"><h2 style="margin-top:0">Auf einen Blick</h2><div class="prose"><p>{E(glance)}</p></div></section><section id="s-ueb">
  <h2>Vorteile und Nachteile</h2>
  <div class="pc"><div class="box pro"><h3>Das spricht dafür</h3><ul class="checks">{"".join(f"<li>{E(x)}</li>" for x in pc) or "<li>–</li>"}</ul></div>
  <div class="box con"><h3>Das spricht dagegen</h3><ul class="checks neg">{"".join(f"<li>{E(x)}</li>" for x in kc) or "<li>–</li>"}</ul></div></div>
  <h2>Für wen passt die Karte?</h2><div class="info"><span class="ic">i</span><div><p style="margin:0 0 8px">{E(" ".join(a))}</p>{"<p style='margin:0'>"+E(" ".join(b))+"</p>" if b else ""}</div></div>
  <h2>So funktioniert die Karte</h2><div class="prose"><p>{E(how)}</p></div>
  </section>
  <section id="s-kond"><h2>Konditionen im Überblick</h2>{cond(c)}</section>
  <section id="s-vers"><h2>Reiseversicherung</h2>{ins}</section>
  <section id="s-bew"><h2>So kommt die Bewertung zustande</h2>{scorebox(c,P)}
  {f"<h2>Im Vergleich mit ähnlichen Karten</h2><div class='tbl wide'><table><thead><tr><th>Karte</th><th>Jahresgebühr</th><th>Ausland</th><th>Bargeld</th><th>Bewertung</th></tr></thead><tbody>{simtbl}</tbody></table></div>" if simtbl else ""}
  <h2>So beantragst du die Karte</h2><p class="note" style="margin-top:-6px">Das ist der übliche Ablauf. Die Details legt der Anbieter fest.</p>
  <div class="steps"><div class="step"><span class="no">1</span><div><b>Online-Antrag ausfüllen</b><p>Du gibst deine Daten, deinen Job und deine Adresse in Deutschland an.</p></div></div><div class="step"><span class="no">2</span><div><b>Identität bestätigen</b><p>Meist per Video-Ident oder Online-Ausweis.</p></div></div><div class="step"><span class="no">3</span><div><b>Bonität prüfen lassen</b><p>{E(c["anbieter"])} fragt deine Bonität ab, in Deutschland meist bei der Schufa{", und legt den Rahmen fest" if c["typ"] in ("Kreditkarte","Charge") else ""}.</p></div></div><div class="step"><span class="no">4</span><div><b>Karte aktivieren</b><p>Die Karte kommt per Post, oft kannst du sie vorher schon digital im Smartphone nutzen.</p></div></div></div>
  </section>
  <section id="s-faq"><h2>Fragen und Antworten</h2><div class="faq">{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q,a in fq)}</div></section>
  {f"<h2>Hinweis der Redaktion</h2><p class='note'>{E(c['notiz'])}</p>" if c.get('notiz_public') else ""}
  {f"<h2>Ähnliche Karten</h2><div class='grid2'>{mini}</div>" if mini else ""}
  <div class="box" style="margin-top:22px"><h3>Über {E(c["anbieter"])}</h3><a class="lnk" href="../anbieter/{c["p"]}/">Alle Karten von {E(c["anbieter"])} →</a></div>
  <p class="src" style="margin-top:18px">Hauptquelle: {ext(c.get("quelle"))}{" · Preisverzeichnis: "+ext(c.get("preis")) if c.get("preis") else ""}{" ("+E(c["stand"])+")" if c.get("stand") else ""}.</p>
</main>
{footer(P)}'''
    alt=None; atrel=ATPAIR.get(c['titel'])
    if atrel and c['art']=='Privat':
        alt=f'\n<link rel="alternate" hreflang="de-DE" href="https://finvallo.com/{rel}"><link rel="alternate" hreflang="de-AT" href="https://finvallo.com/{atrel}">'
        fa=R+atrel+'index.html'; sa=open(fa).read()
        sa=re.sub(r'\n<link rel="alternate" hreflang="de-DE" href="https://finvallo.com/de/kreditkarten/[^"]*"><link rel="alternate" hreflang="de-AT" href="[^"]*">','',sa)
        sa=sa.replace(f'<link rel="canonical" href="https://finvallo.com/{atrel}">',f'<link rel="canonical" href="https://finvallo.com/{atrel}">'+alt,1)
        open(fa,'w').write(sa)
    write(rel,head(t,d,rel,P,ld,alt=alt)+body)
def list_item(c,P,base=''):
    v=cash200(c.get('cash'))
    st=lambda good,txt: f'<b class="{ "good" if good else ""}">{E(txt)}</b>'
    fee='–' if c.get('fee') is None else ('€ 0,00' if c['fee']==0 else f'€ {eur(c["fee"])}')
    rank=f'<span class="rank r{c["rank"]}">{c["rank"]}</span>' if c.get('rank') and c['rank']<=3 else (f'<span class="rank">{c["rank"]}</span>' if c.get('rank') else '')
    return f'''<article class="item" id="it-{c["slug"]}">
    <div class="ihead"><div style="display:flex;gap:10px;align-items:center">{rank}{'<span class="reco">★ Bestbewertet</span>' if c.get('rank')==1 else ''}</div></div>
    <div class="irow">{face(c)}<div style="min-width:0"><h3 class="iname"><a href="{base}{c["slug"]}/">{E(c["titel"])}</a></h3><div class="iprov">{E(c["anbieter"])}</div>{starrow(c)}</div></div>
    <div class="tags">{f'<a class="tag best" href="{base}bestenlisten/{BEST[c["slug"]][2]}/">🏆 Platz {BEST[c["slug"]][0]+1} für {E(BEST[c["slug"]][1])}</a>' if c["slug"] in BEST else ''}<span class="tag typ">▭ {E(c["typ"])}</span><span class="tag kl">{E(c["klasse"])}</span><span class="tag out">{E(c["netz"])}</span></div>
    <div class="stats"><div><small>Jahresgebühr</small>{st(c.get("fee")==0,fee)}</div><div><small>Ausland</small>{st(c.get("fx")==0,fxT(c) if c.get("fx") is not None else "–")}</div><div><small>Bargeld Inland</small>{st(v==0,"Kostenlos" if v==0 else (eur(v)+" €") if isinstance(v,float) else "0 € (verzinst)" if v=="fi" else "–")}</div></div>
    {f'<div class="earn"><span>Sammeln</span><b>{E(c["cbText"])}</b></div>' if c.get("cbText") and c["ex"].get("cb") else ""}
    <ul class="checks">{"".join(f"<li>{E(x)}</li>" for x in c["pros"][:4])}</ul>
    <div class="acts"><a class="btn primary block" href="{E(c.get("quelle"))}" target="_blank" rel="noopener">Zum Anbieter ↗</a><a class="btn ghost block" href="{base}{c["slug"]}/">Details ansehen</a></div>
  </article>'''
def list_page(cards,priv,biz):
    rel='de/kreditkarten/'; P='../../'
    n=len(cards); na=len({c['anbieter'] for c in cards})
    t='Kreditkarten Vergleich Deutschland 2026 – unabhängig | Finvallo'
    top=priv[:3]
    d=f'{n} Kreditkarten in Deutschland unabhängig verglichen: Jahresgebühr, Ausland, Bargeld, Versicherung. Testsieger: {top[0]["titel"]} ({de1(top[0]["stars"])}/5).'
    if len(d)>158: d=f'{n} Kreditkarten in Deutschland unabhängig verglichen: Jahresgebühr, Ausland, Bargeld und Reiseversicherung. Mit Testsieger und Rangliste.'
    ld=graph(rel,t,d,[('Deutschland','de/'),('Kreditkarten',rel)],[{"@type":"ItemList","name":"Beste Kreditkarten Deutschland","itemListElement":[{"@type":"ListItem","position":c['rank'],"name":c['titel'],"url":f"https://finvallo.com/{rel}{c['slug']}/"} for c in priv[:20]]}])
    kurz=f'<b>Kurz gesagt:</b> Die bestbewertete Kreditkarte in Deutschland ist laut Finvallo die {top[0]["titel"]} mit {de1(top[0]["stars"])} von 5 Sternen, vor der {top[1]["titel"]} ({de1(top[1]["stars"])}) und der {top[2]["titel"]} ({de1(top[2]["stars"])}). Wir vergleichen {n} Karten von {na} Anbietern nach festen, offen gelegten Regeln. Stand: {STAND_DE}.'
    unrated=[c for c in cards if c['art']=='Privat' and c.get('stars') is None and not c.get('nurfuer')]
    special=[c for c in cards if c['art']=='Privat' and c.get('nurfuer')]
    body=f'''{HDR(P,rel)}
<div class="wrap"><main id="app">
<h1>Kreditkarten Vergleich Deutschland</h1>
  <p class="lede">{n} Kredit-, Charge-, Debit- und Prepaidkarten von {na} Anbietern. Sortiert nach unserer Bewertung. Provisionen haben keinen Einfluss auf die Reihenfolge.</p><div class="facts prose"><p>{kurz}</p></div>
  <p class="upd">Zuletzt geprüft: {STAND_DE}</p>
  <details class="box howscore"><summary><span><b>So entstehen die Sterne</b><br><small>7 Kriterien, feste Regeln, offene Gewichtung</small></span><span class="lnk">anzeigen</span></summary>
    <div class="wbars">{"".join(f'<div class="wbar"><span>{k}</span><span class="t"><i style="width:{w*4}%"></i></span><em>{w} %</em></div>' for k,w in [("Jahresgebühr",25),("Reiseversicherung",20),("Zahlen im Ausland",15),("Kartenart &amp; Akzeptanz",10),("Alltag &amp; Flexibilität",10),("Bargeld",10),("Extras",10)])}</div>
    <p class="note">Jedes Kriterium bekommt nach festen Regeln 1 bis 5 Sterne. Die Gesamtnote ist der gewichtete Durchschnitt. Ab 4,5 Sternen gilt eine Karte als sehr gut. Fehlende Angaben zählen mit 2,5 Sternen, damit sie keinen Vorteil bringen.</p>
    <a class="lnk" href="{P}de/kreditkarten/methodik/">Alle Regeln und ein Rechenbeispiel →</a></details>
  <div class="list" id="list">{"".join(list_item(c,P) for c in priv)}</div>
  {f'<h2>Noch nicht bewertet</h2><p class="note">Für diese Karten fehlen uns bestätigte Angaben in mindestens drei Kriterien.</p><div class="list">{"".join(list_item(c,P) for c in unrated)}</div>' if unrated else ''}
  {f'<h2>Nur für bestimmte Kundengruppen</h2><p class="note">Diese Karten bekommt nicht jede:r. Sie stehen deshalb nicht in der Rangliste.</p><div class="list">{"".join(list_item(c,P) for c in special)}</div>' if special else ''}
  {f'<h2>Business-Kreditkarten</h2><p class="lede">Firmen- und Business-Karten bewerten wir nach denselben Regeln, aber in einer eigenen Liste.</p><p><a class="btn" href="business/">Alle {len(biz)} Business-Karten ansehen →</a></p>' if biz else ''}
</main>
{footer(P)}'''
    write(rel,head(t,d,rel,P,ld)+body)
def biz_page(biz):
    rel='de/kreditkarten/business/'; P='../../../'
    t='Business-Kreditkarten Deutschland 2026 im Vergleich | Finvallo'
    d=f'{len(biz)} Business- und Firmenkreditkarten in Deutschland unabhängig verglichen.'
    biz=sorted(biz,key=lambda c:(-(c.get('stars') or 0),c.get('fee') or 0))
    for i,c in enumerate(biz): c['brank']=i+1
    ld=graph(rel,t,d,[('Deutschland','de/'),('Kreditkarten','de/kreditkarten/'),('Business',rel)])
    items=[]
    for c in biz:
        r=c.get('rank'); c['rank']=None; items.append(list_item(c,P,'../')); c['rank']=r
    body=f'''{HDR(P,rel)}
<div class="wrap"><main id="app">
<h1>Business-Kreditkarten in Deutschland</h1><p class="lede">{len(biz)} Karten für Selbstständige und Firmen, bewertet nach denselben sieben Kriterien wie Privatkarten.</p>
<p class="note">Mehr zu Haftung und Abrechnung im <a href="{P}de/ratgeber/business/">Ratgeber Firmenkreditkarten</a>.</p>
<div class="list">{"".join(items)}</div>
</main>
{footer(P)}'''
    write(rel,head(t,d,rel,P,ld)+body)
def anbieter_pages(cards):
    prov={}
    for c in cards: prov.setdefault(c['p'],[]).append(c)
    rel='de/kreditkarten/anbieter/'; P='../../../'
    t='Kreditkarten-Anbieter in Deutschland | Finvallo'; d=f'{len(prov)} Banken und Kartenanbieter in Deutschland mit allen Kreditkarten im Überblick.'
    tiles=''.join(f'<a class="catcard" href="{p}/"><b>{E(v[0]["anbieter"])}</b><span style="color:var(--muted)">{len(v)} {"Karte" if len(v)==1 else "Karten"}{" · beste: "+de1(max(x["stars"] for x in v if x.get("stars")))+" ★" if any(x.get("stars") for x in v) else ""}</span><small>Alle Karten →</small></a>' for p,v in sorted(prov.items(),key=lambda kv:kv[1][0]['anbieter'].lower()))
    write(rel,head(t,d,rel,P,graph(rel,t,d,[('Deutschland','de/'),('Kreditkarten','de/kreditkarten/'),('Anbieter',rel)]))+f'''{HDR(P,rel)}
<div class="wrap"><main id="app"><h1>Kreditkarten-Anbieter in Deutschland</h1><p class="lede">{len(prov)} Banken und Kartenanbieter. Wähle einen Anbieter, um alle seine Karten zu sehen.</p><div class="catgrid">{tiles}</div></main>
{footer(P)}''')
    for p,v in prov.items():
        rel2=f'{rel}{p}/'; P2='../../../../'; nm=v[0]['anbieter']
        v=sorted(v,key=lambda c:-(c.get('stars') or 0))
        t2=f'{nm} Kreditkarten in Deutschland 2026 | Finvallo'; d2=f'Alle {len(v)} Kreditkarten von {nm} in Deutschland: Gebühren, Versicherung und Bewertung.'
        items=[]
        for c in v:
            r=c.get('rank'); c['rank']=None; items.append(list_item(c,P2,'../../')); c['rank']=r
        write(rel2,head(t2,d2,rel2,P2,graph(rel2,t2,d2,[('Deutschland','de/'),('Kreditkarten','de/kreditkarten/'),('Anbieter',rel),(nm,rel2)]))+f'''{HDR(P2,rel2)}
<div class="wrap"><main id="app"><div class="crumb"><span><a href="../">Anbieter</a> › {E(nm)}</span></div><h1>{E(nm)} Kreditkarten</h1><p class="lede">{len(v)} {"Karte" if len(v)==1 else "Karten"} von {E(nm)} für Kund:innen in Deutschland.</p><div class="list">{"".join(items)}</div></main>
{footer(P2)}''')
    return prov
def datafile(cards):
    out=[]
    for c in cards:
        out.append({k:c.get(k) for k in ['slug','anbieter','herausgeber','name','titel','art','typ','klasse','netz','fee','fee1','feeNote','fx','fxText','cashText','soll','effz','rahmen','giro','auto','pay','tier','stars','note','rank','pros','cons','quelle','preis','stand','sek']}|{'versicherung':TIER[c['tier']][1] if c.get('tier') is not None else None,'url':f'https://finvallo.com/de/kreditkarten/{c["slug"]}/'})
    os.makedirs(R+'de/daten',exist_ok=True)
    json.dump({'quelle':'https://finvallo.com/de/kreditkarten/','stand':STAND,'lizenz':'Frei nutzbar mit Quellenangabe Finvallo','karten':out},open(R+'de/daten/kreditkarten.json','w'),ensure_ascii=False,indent=1)
HDR=None
BEST={}
def main():
    global HDR
    sys.path.insert(0,SP); import header as H
    HDR=lambda P,rel: H.build(rel,P,LAND_DE(P))
    at_pairs(); cards=load(); priv=ratecards(cards)
    biz=[c for c in cards if c['art']=='Business']
    print('Karten',len(cards),'bewertet privat',len(priv),'business',len(biz))
    global BEST
    LISTS,BEST=cat_lists(cards)
    for c in cards: card_page(c,cards,len(priv))
    list_page(cards,priv,biz)
    bestenlisten(cards); methodik_page(cards,priv); faktencheck_page(cards)
    if biz: biz_page(biz)
    anbieter_pages(cards); datafile(cards)
    for c in priv[:12]: print(c['rank'],c['stars'],c['titel'],c['fee'],c['fx'],c['tier'])
    return cards,priv

# ---------- Sitemap, llms.txt, Rechner ----------
def sitemap(cards,prov):
    p=R+'sitemap.xml'; s=open(p).read()
    s=re.sub(r'<url><loc>https://finvallo\.com/de/kreditkarten/[^<]*</loc>.*?</url>\n','',s)
    if 'https://finvallo.com/at/kreditkarten/rechner/' not in s:
        s=s.replace('</urlset>','<url><loc>https://finvallo.com/at/kreditkarten/rechner/</loc><lastmod>'+STAND+'</lastmod><changefreq>weekly</changefreq><priority>0.6</priority></url>\n</urlset>')
    urls=['de/kreditkarten/','de/kreditkarten/anbieter/','de/kreditkarten/methodik/','de/kreditkarten/faktencheck/','de/kreditkarten/bestenlisten/']+[f'de/kreditkarten/bestenlisten/{c["k"]}/' for c in CATS if os.path.exists(R+f'de/kreditkarten/bestenlisten/{c["k"]}/index.html')]+(['de/kreditkarten/business/'] if any(c['art']=='Business' for c in cards) else [])
    urls+=[f'de/kreditkarten/{c["slug"]}/' for c in cards]+[f'de/kreditkarten/anbieter/{x}/' for x in prov]
    add=''.join(f'<url><loc>https://finvallo.com/{u}</loc><lastmod>{STAND}</lastmod><changefreq>weekly</changefreq><priority>{"0.8" if u.count("/")<=3 else "0.6"}</priority></url>\n' for u in urls)
    s=s.replace('</urlset>',add+'</urlset>'); open(p,'w').write(s)
def llms(cards,priv):
    for fn in ['llms.txt','llms-full.txt']:
        p=R+fn; s=open(p).read()
        s=re.sub(r'\n## Deutschland: Kreditkarten\n.*?(?=\n## |\Z)','',s,flags=re.S)
        n=len(cards)
        s=s.replace('Unabhängiger Finanzvergleich für Österreich (und Ratgeber für Deutschland). 77 Kredit-, Charge-, Debit- und Prepaid-Karten',f'Unabhängiger Finanzvergleich für Österreich und Deutschland. 77 Karten in Österreich und {n} in Deutschland (Kredit-, Charge-, Debit- und Prepaid-Karten)')
        s=re.sub(r'77 Karten in Österreich und \d+ in Deutschland',f'77 Karten in Österreich und {n} in Deutschland',s)
        top=priv[:15 if fn=='llms.txt' else 60]
        blk='\n## Deutschland: Kreditkarten\n'+f'- [Kreditkarten-Vergleich Deutschland](https://finvallo.com/de/kreditkarten/): Rangliste aller {n} Karten, Stand {STAND_DE}\n- [Anbieter Deutschland](https://finvallo.com/de/kreditkarten/anbieter/)\n- [Daten als JSON](https://finvallo.com/de/daten/kreditkarten.json)\n'
        blk+=''.join(f'- [{c["titel"]}](https://finvallo.com/de/kreditkarten/{c["slug"]}/): Platz {c["rank"]}, {de1(c["stars"])}/5 ({c["note"]}); Jahresgebühr {feeT(c)}, Ausland {fxT(c)}, {TIER[c["tier"]][1] if c.get("tier") is not None else ""}\n' for c in top)
        i=s.find('\n## Deutschland: Ratgeber')
        s=s[:i]+blk+s[i:] if i>=0 else s+blk
        open(p,'w').write(s)
def rechner(cards,prov):
    p=R+'at/kreditkarten/rechner/index.html'; s=open(p).read()
    m=re.search(r'(<script id="data" type="application/json">)(.*?)(</script>)',s,re.S)
    d=json.loads(m.group(2))
    d['cards']=[c for c in d['cards'] if c.get('land')!='DE']
    d['providers']={k:v for k,v in d['providers'].items() if not k.startswith('de-')}
    for i,c in enumerate(sorted(cards,key=lambda c:(c.get('rank') or 999,c['titel']))):
        cid=f'DE{i+1:03d}'; c['rid']=cid
        ex=c['ex']
        d['cards'].append({'id':cid,'anbieter':c['anbieter'],'p':'de-'+c['p'],'name':(c['titel'][len(c['anbieter'])+1:] if c['titel'].startswith(c['anbieter']+' ') else c['titel']),'typ':c['typ'],'klasse':'Std+' if c['klasse']=='Std' else c['klasse'],'netz':c['netz'],'art':c['art'],
          'fee':c.get('fee'),'fee1':c.get('fee1'),'feeNote':c.get('feeNote'),'price':c.get('fee'),'period':'Jahr','fx':c.get('fx'),'fxText':fxT(c),'cash':c.get('cash'),'cashText':cashT(c),'cashNote':None,
          'zins':zinsT(c),'zf':c.get('zinsfrei'),'rahmen':c.get('rahmen'),'giro':c.get('giro'),'auto':c.get('auto'),'teilz':c['typ']=='Kreditkarte','cb':c.get('cbText') if ex.get('cb') else None,'ml':bool(ex.get('ml')),
          'lg':c.get('lgText') if (ex.get('lg') or ex.get('lgm')) else None,'lgf':bool(ex.get('lg')),'ft':'FastTrack' if ex.get('ft') else None,'pay':c.get('pay'),'bonus':c.get('bonus'),'credits':bool(ex.get('credits')),'bestand':None,
          'vers':None,'prof':None,'tier':c.get('tier'),'vorteile':'; '.join(c['pros'][:3]),'kosten':'','status':'DE-Angebot','quelle':c.get('quelle'),'erst':None,'extra':c.get('extra') or [],'con':[],'sek':c.get('sek') or [],
          'effz':c.get('effz'),'bonitaet':c['typ'] in ('Kreditkarte','Charge'),'kaution':c['typ'] in ('Kreditkarte','Charge'),'lounge':None,'score':c['score'],'stars':c.get('stars'),'note':c.get('note'),
          'pros':c['pros'],'cons':c['cons'],'rank':c.get('rank'),'vorteilRows':[],'land':'DE','preis':c.get('preis'),'earn':c.get('cbText') if ex.get('cb') else None,'offer':None})
    for k,v in prov.items():
        d['providers']['de-'+k]={'name':v[0]['anbieter'],'typ':'Bank','sitz':'','web':v[0].get('quelle'),'text':f'Kartenanbieter in Deutschland. {len(v)} Karten im Finvallo-Vergleich.','slug':'de-'+k,'cards':[c['rid'] for c in v]}
    if '<link rel="canonical"' not in s:
        s=s.replace('<meta name="viewport" content="width=device-width, initial-scale=1">','<meta name="viewport" content="width=device-width, initial-scale=1">\n<meta name="description" content="Kreditkarten-Rechner für Österreich und Deutschland: Jahreskosten, Auslandsgebühren und Bargeld für deine Nutzung berechnen und Karten vergleichen.">\n<link rel="canonical" href="https://finvallo.com/at/kreditkarten/rechner/">',1)
        m=re.search(r'(<script id="data" type="application/json">)(.*?)(</script>)',s,re.S)
    s=s.replace("let ui = {land:LS.get('ka-land','AT')","let ui = {land:(['AT','DE'].includes(new URLSearchParams(location.search).get('land'))?new URLSearchParams(location.search).get('land'):LS.get('ka-land','AT'))")
    m=re.search(r'(<script id="data" type="application/json">)(.*?)(</script>)',s,re.S)
    js=json.dumps(d,ensure_ascii=False).replace('</','<\\/')
    s=s[:m.start(2)]+js+s[m.end(2):]; open(p,'w').write(s)
_main=main
def main():
    cards,priv=_main()
    prov={}
    for c in cards: prov.setdefault(c['p'],[]).append(c)
    sitemap(cards,prov); llms(cards,priv); rechner(cards,prov)
    print('extras ok')

# ---------- Bestenlisten, Methodik, Faktencheck (DE) ----------
CATS=[
 dict(k='reisen',t='Reisen',h='Die besten Karten für Reisen',d='Hier zählen Reiseversicherung und Auslandsgebühren am meisten.',f=lambda c:c['typ']!='Prepaid',w={'Reiseversicherung':30,'Zahlen im Ausland':25,'Jahresgebühr':15,'Kartenart & Akzeptanz':10,'Extras':10,'Bargeld':10}),
 dict(k='gratis',t='Ohne Jahresgebühr',h='Die besten Karten ohne Jahresgebühr',d='Nur Karten, die dauerhaft nichts kosten. Bewertet wie in der Gesamtwertung.',f=lambda c:c.get('fee')==0,w=None),
 dict(k='ausland',t='Ohne Auslandsgebühr',h='Die besten Karten zum Zahlen im Ausland',d='Karten mit höchstens 0,5 % Aufschlag in fremder Währung. Bargeld und Akzeptanz zählen hier mehr.',f=lambda c:c.get('fx') is not None and c['fx']<=0.5,w={'Zahlen im Ausland':30,'Bargeld':20,'Jahresgebühr':20,'Kartenart & Akzeptanz':15,'Alltag & Flexibilität':15}),
 dict(k='punkte',t='Meilen & Punkte',h='Die besten Karten für Meilen, Punkte und Cashback',d='Karten mit Prämienprogramm. Die Extras zählen hier am meisten.',f=lambda c:bool(c['ex'].get('cb') or c['ex'].get('ml')),w={'Extras':35,'Jahresgebühr':20,'Zahlen im Ausland':15,'Reiseversicherung':15,'Kartenart & Akzeptanz':15}),
 dict(k='lounge',t='Lounge-Zugang',h='Die besten Karten mit Lounge-Zugang',d='Nur Karten mit kostenlosen Lounge-Besuchen. Am meisten zählt, wie gut der Lounge-Zugang ist: wie viele Besuche im Jahr und ob eine Begleitperson gratis mitkommt.',f=lambda c:bool(c['ex'].get('lg')),w={'Lounge-Zugang':60,'Reiseversicherung':15,'Jahresgebühr':15,'Zahlen im Ausland':10}),
 dict(k='premium',t='Premium',h='Die besten Premiumkarten',d='Top-Karten mit Lounges oder Premium-Reiseschutz. Die Jahresgebühr zählt hier weniger.',f=lambda c:c['klasse']=='Premium',w={'Reiseversicherung':30,'Extras':25,'Zahlen im Ausland':15,'Jahresgebühr':10,'Kartenart & Akzeptanz':10,'Bargeld':10}),
 dict(k='studium',t='Studierende',h='Die besten Karten für Studierende und junge Leute',d='Karten für Studierende, Azubis und junge Kund:innen sowie kostenlose Karten ohne Mindesteinkommen. Bewertet wie in der Gesamtwertung.',f=lambda c:bool(re.search(r'Student|Young|Jugend|Azubi|Junge',c['titel'])) or (c.get('fee')==0 and c['typ'] in ('Kreditkarte','Charge') and not c.get('giro')),w=None),
 dict(k='debit',t='Debit & App-Banken',h='Die besten Debitkarten und App-Banken',d='Karten, die sofort vom Konto abbuchen. Kosten im Ausland zählen hier mehr.',f=lambda c:c['typ'] in ('Debit','Prepaid'),w={'Jahresgebühr':30,'Zahlen im Ausland':25,'Extras':15,'Reiseversicherung':15,'Alltag & Flexibilität':15}),
]
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
    return round(a/b+1e-9,1) if b else None
def cat_reason(c,k):
    r=[]
    if k=='reisen':
        if (c.get('tier') or 0)>=2: r.append(TIER[c['tier']][1])
        if c.get('fx')==0: r.append('0 % im Ausland')
    if k=='ausland':
        r.append('0 % Aufschlag' if c.get('fx')==0 else fxT(c)); r.append('Bargeld: '+cashT(c))
    if k=='lounge' and c.get('lgText'): r.append(c['lgText'])
    if k in ('punkte','premium') and c.get('cbText') and c['ex'].get('cb'): r.append(c['cbText'])
    if k=='debit': r.append('Ausland: '+('0 %' if c.get('fx')==0 else fxT(c)))
    if not r and c['pros']: r.append(c['pros'][0])
    return ' · '.join(x[:110] for x in r[:2])
def cat_lists(cards):
    out={}
    for c in cards: c['lounge']=lounge_score(c)
    for cat in CATS:
        L=[c for c in cards if c['art']=='Privat' and not c.get('nurfuer') and c.get('stars') is not None and cat['f'](c)]
        L=sorted(L,key=lambda c:(-(cat_stars(c,cat['w']) or 0),c.get('fee') if c.get('fee') is not None else 1e9))
        out[cat['k']]=L
    best={}
    for cat in CATS:
        for i,c in enumerate(out[cat['k']][:3]):
            if c['slug'] not in best or i<best[c['slug']][0]: best[c['slug']]=(i,cat['t'],cat['k'])
    return out,best
def bestenlisten(cards):
    lists,best=cat_lists(cards)
    base='de/kreditkarten/bestenlisten/'; P='../../../'
    tiles=''
    for cat in CATS:
        L=lists[cat['k']]
        if not L: continue
        c=L[0]; s=cat_stars(c,cat['w'])
        tiles+=f'<a class="catcard" href="{cat["k"]}/"><span class="ct">{E(cat["t"])}</span><b>{E(c["titel"])}</b><span>{stars(s)} {de1(s)}</span><small>{len(L)} Karten · Liste ansehen →</small></a>'
    t='Beste Kreditkarten Deutschland 2026 nach Kategorie | Finvallo'
    d='Die besten Kreditkarten in Deutschland für Reisen, ohne Jahresgebühr, ohne Auslandsgebühr, für Punkte, Lounges, Premium, Studierende und Debit.'
    ld=graph(base,t,d,[('Deutschland','de/'),('Kreditkarten','de/kreditkarten/'),('Bestenlisten',base)],[{"@type":"ItemList","name":"Bestenlisten Kreditkarten Deutschland","itemListElement":[{"@type":"ListItem","position":i+1,"name":cat['h']+' in Deutschland','url':f"https://finvallo.com/{base}{cat['k']}/"} for i,cat in enumerate(CATS) if lists[cat['k']]]}])
    write(base,head(t,d,base,P,ld)+f'''{HDR(P,base)}
<div class="wrap"><main id="app">
<h1>Beste Kreditkarten in Deutschland nach Kategorie</h1><p class="lede">Manche Karten sind in einer Disziplin viel stärker als in der Gesamtwertung. Für jede Kategorie gewichten wir die Kriterien anders. Die Gewichte stehen jeweils dabei. Stand: {STAND_DE}.</p><div class="catgrid">{tiles}</div>
</main>
{footer(P)}''')
    chips=lambda k: ''.join(f'<a class="chip" href="../{c["k"]}/" aria-pressed="{"true" if c["k"]==k else "false"}" style="text-decoration:none">{E(c["t"])}</a>' for c in CATS if lists[c['k']])
    for cat in CATS:
        L=lists[cat['k']]
        if not L: continue
        rel=f'{base}{cat["k"]}/'; P2='../../../../'
        t=f'{cat["h"]} in Deutschland 2026 | Finvallo'
        if len(t)>65: t=f'{cat["h"]} (DE) 2026 | Finvallo'
        top=L[0]
        d=f'{cat["h"]} in Deutschland, Stand {STAND_DE}: Platz 1 ist die {top["titel"]} ({de1(cat_stars(top,cat["w"]))} Sterne). {len(L)} Karten im Vergleich.'
        if len(d)>158: d=f'{cat["h"]} in Deutschland: Platz 1 ist die {top["titel"]}. {len(L)} Karten im Vergleich, Stand {STAND_DE}.'
        if len(d)>158: d=d[:155].rsplit(' ',1)[0]+' …'
        wb=''
        if cat['w']:
            mx=max(cat['w'].values())
            wb='<details class="box howscore"><summary><span><b>So gewichten wir in dieser Kategorie</b></span><span class="lnk">anzeigen</span></summary><div class="wbars">'+''.join(f'<div class="wbar"><span>{E(k)}</span><span class="t"><i style="width:{v/mx*100}%"></i></span><em>{v} %</em></div>' for k,v in cat['w'].items())+'</div><p class="note">Die Sterne je Kriterium sind dieselben Sterne wie in der Gesamtwertung, nur die Gewichte ändern sich.'+(' Die Lounge-Note richtet sich nach Zahl der Gratis-Besuche und danach, ob eine Begleitperson kostenlos mitkommt.' if cat['k']=='lounge' else '')+'</p></details>'
        rows=''.join(f'<tr><td><b>{i+1}</b></td><td><a class="lnk" href="../../{c["slug"]}/">{E(c["titel"])}</a></td><td>{E(cat_reason(c,cat["k"]))}</td><td>{eur(c["fee"]) if c.get("fee") is not None else "–"} €</td><td style="white-space:nowrap"><b>{de1(cat_stars(c,cat["w"]))} ★</b></td><td style="white-space:nowrap">{de1(c["stars"])} ★</td></tr>' for i,c in enumerate(L[:25]))
        kurz=f'<b>Kurz gesagt:</b> {cat["h"]} in Deutschland: Platz 1 ist laut Finvallo die {top["titel"]} mit {de1(cat_stars(top,cat["w"]))} Sternen in dieser Kategorie'+(f', vor der {L[1]["titel"]}' if len(L)>1 else '')+(f' und der {L[2]["titel"]}' if len(L)>2 else '')+f'. Verglichen haben wir {len(L)} Karten. Stand: {STAND_DE}.'
        fq=[(f'Welche Karte ist in Deutschland am besten in der Kategorie „{cat["t"]}“?',f'Laut Finvallo-Bewertung ist es die {top["titel"]} mit {de1(cat_stars(top,cat["w"]))} von 5 Sternen in dieser Kategorie. Stand: {STAND_DE}.'),
            ('Wie entsteht diese Rangliste?',cat['d']+' Grundlage sind dieselben sieben Kriterien wie in der Gesamtwertung.' ),
            ('Spielen Provisionen eine Rolle?','Nein. Provisionen haben keinen Einfluss auf Sterne oder Reihenfolge, und es gibt keine bezahlten Platzierungen.')]
        ld=graph(rel,t,d,[('Deutschland','de/'),('Kreditkarten','de/kreditkarten/'),('Bestenlisten',base),(cat['t'],rel)],
                 [{"@type":"ItemList","name":cat['h']+' in Deutschland',"numberOfItems":len(L),"itemListElement":[{"@type":"ListItem","position":i+1,"name":c['titel'],"url":f"https://finvallo.com/de/kreditkarten/{c['slug']}/"} for i,c in enumerate(L[:25])]},
                  {"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in fq]}])
        atrel=f'at/kreditkarten/bestenlisten/{cat["k"]}/'
        alt=f'\n<link rel="alternate" hreflang="de-DE" href="https://finvallo.com/{rel}"><link rel="alternate" hreflang="de-AT" href="https://finvallo.com/{atrel}">' if os.path.exists(R+atrel+'index.html') else None
        write(rel,head(t,d,rel,P2,ld,alt=alt)+f'''{HDR(P2,rel)}
<div class="wrap"><main id="app">
<div class="crumb"><span><a href="../">Bestenlisten</a> › {E(cat["t"])}</span><span>Stand {STAND_DE}</span></div><h1>{E(cat["h"])} in Deutschland</h1><p class="lede">{E(cat["d"])}</p>
<div class="facts prose"><p>{kurz}</p></div>
<div class="chips" style="margin:14px 0">{chips(cat["k"])}</div>
{wb}
<div class="tbl wide" style="margin-top:16px"><table><thead><tr><th>#</th><th>Karte</th><th>Darum</th><th>Jahresgebühr</th><th>Kategorie</th><th>Gesamt</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>Fragen und Antworten</h2><div class="faq">{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q,a in fq)}</div>
<p class="note" style="margin-top:18px"><a class="lnk" href="{P2}de/kreditkarten/">Zur Gesamtwertung aller Karten →</a> · <a class="lnk" href="{P2}de/kreditkarten/methodik/">So bewerten wir →</a></p>
</main>
{footer(P2)}''')
        if alt:
            fa=R+atrel+'index.html'; sa=open(fa).read()
            sa=re.sub(r'\n<link rel="alternate" hreflang="de-DE" href="https://finvallo.com/de/kreditkarten/bestenlisten/[^"]*"><link rel="alternate" hreflang="de-AT" href="[^"]*">','',sa)
            sa=sa.replace(f'<link rel="canonical" href="https://finvallo.com/{atrel}">',f'<link rel="canonical" href="https://finvallo.com/{atrel}">'+alt,1); open(fa,'w').write(sa)
    return lists,best
KORREKTUREN=[
 ('Barclays','Die Barclays-Kreditkarten heißen seit Februar 2026 easybank (BAWAG-Gruppe). Konditionen aus den aktuellen easybank-Preisverzeichnissen.'),
 ('Miles & More Credit Cards','Herausgeber ist seit Oktober 2025 die Deutsche Bank, nicht mehr die DKB. Ältere Portaldaten mit DKB-Preisverzeichnis sind veraltet.'),
 ('American Express Green Card','Für Neukunden ersetzt durch die „American Express Card“ (55 € pro Jahr bei jährlicher Zahlung).'),
 ('GMX / WEB.DE Mastercard Gold','Heute eine gemeinsame Karte: WEB.Cent Mastercard Gold, Herausgeber Advanzia Bank, mit 0,5 % Cashback.'),
 ('TUI Card','Kein Auslandseinsatzentgelt außerhalb des EWR; die oft genannten 0,59 % gelten laut Preisverzeichnis nur für Nicht-Euro-Währungen im EWR.'),
 ('1822direkt Visa Classic','Aktuelle Jahresgebühr 36 € statt der in Portalen genannten 29,90 €.'),
 ('Berliner Volksbank GoldCard','Laut Bank 5 € pro Monat (60 € im Jahr) statt der in Portalen genannten 107,40 €.'),
 ('Klarna Kreditkarte','Die Kreditkartenfunktion gibt es nur noch mit einer kostenpflichtigen Klarna-Mitgliedschaft.'),
 ('PAYBACK Visa Flex+','Wird nicht mehr angeboten; aktuell gibt es die PAYBACK Visa Kreditkarte und die Variante auf Guthabenbasis.'),
 ('ADAC Kreditkarte','Herausgeber ist seit September 2024 die Solaris SE, die Karte ist eine Visa mit Zusatzpaketen; Classic/Gold gibt es nicht mehr.'),
 ('Hanseatic Bank GoldCard','Das alte Preisverzeichnis ist offline (HTTP 410); die Werte stammen aus dem aktuellen PLV 07/2026.'),
 ('easybank Kreditkarte','Volle Rückzahlung per Lastschrift kostet 2 € pro Monat; kostenlos komplett zurückzahlen geht nur per Überweisung.'),
]
def methodik_page(cards,priv):
    rel='de/kreditkarten/methodik/'; P='../../../'
    t='So bewerten wir Kreditkarten in Deutschland | Finvallo'
    d='Die Finvallo-Methodik für Kreditkarten in Deutschland: 7 Kriterien, feste Regeln, offene Gewichte. Mit Rechenbeispiel und Datenquellen.'
    ex=priv[0]
    rows=lambda L: ''.join(f'<tr><td>{a}</td><td>{b}</td></tr>' for a,b in L)
    rules=[('Jahresgebühr · 25 %','Was die Karte ab dem zweiten Jahr kostet. Aktionen im ersten Jahr zählen bei den Extras.',[('0 €','5,0'),('bis 25 €','4,6'),('bis 50 €','4,2'),('bis 100 €','3,6'),('bis 150 €','3,0'),('bis 250 €','2,4'),('bis 450 €','1,8'),('über 450 €','1,2')]),
           ('Zahlen im Ausland · 15 %','Was eine Zahlung in US-Dollar insgesamt extra kostet, also Auslandseinsatzentgelt und Kursaufschlag zusammen.',[('0 %','5,0'),('bis 0,5 %','4,8'),('bis 1 %','4,4'),('bis 1,5 %','4,0'),('bis 2 %','3,4'),('bis 2,7 %','2,6'),('bis 3,2 %','2,0'),('darüber','1,5')]),
           ('Reiseversicherung · 20 %','Wie umfassend der Reiseschutz ist, der ohne Aufpreis enthalten ist.',[('Premium-Reiseschutz','5,0'),('umfassender Reiseschutz (mit Mietwagen)','4,7'),('Reiseversicherung mit Reiserücktritt','4,2'),('Basis-Reiseschutz','3,0'),('keine Reiseversicherung','1,0')]),
           ('Kartenart & Akzeptanz · 10 %','Wo die Karte angenommen wird. Debit- und Prepaid-Karten gehen fast überall, werden aber bei Kautionen für Mietwagen oder Hotels oft abgelehnt.',[('Kredit- oder Charge-Karte mit Visa oder Mastercard','5,0'),('Kredit- oder Charge-Karte, Netz nicht bestätigt','4,5'),('Debit- oder Prepaid-Karte mit Visa oder Mastercard','3,5'),('American Express','3,0'),('Diners Club','2,0')]),
           ('Alltag & Flexibilität · 10 %','Durchschnitt aus bis zu drei Punkten. Was wir nicht wissen, zählt nicht mit.',[('kein Konto beim Anbieter nötig','5,0 (sonst 2,5)'),('automatische Abbuchung','5,0 (sonst 3,0)'),('Apple Pay / Google Pay bestätigt','5,0')]),
           ('Bargeld · 10 %','Was eine Abhebung von 200 € am Automaten in Deutschland kostet.',[('kostenlos','5,0'),('kostenlos, aber ab Tag 1 verzinst','4,5'),('bis 2 €','4,2'),('bis 4 €','3,4'),('bis 7 €','2,6'),('darüber','2,0')]),
           ('Extras · 10 %','Jede Karte startet bei 2,5 Sternen. Für jedes Extra gibt es einen Zuschlag, höchstens bis 5,0.',[('Cashback, Punkte oder Partner-Rabatte inklusive','+1,0'),('kostenlose Lounge-Besuche','+1,0'),('nur Lounge-Mitgliedschaft','+0,4'),('Meilen','+0,5'),('Guthaben oder Partner-Abos','+0,5'),('FastTrack','+0,3'),('Aktion im 1. Jahr','+0,3')])]
    rb=''.join(f'<h3 style="margin-top:22px">{a}</h3><p class="note">{b}</p><div class="tbl"><table><tbody>{rows(L)}</tbody></table></div>' for a,b,L in rules)
    exrows=''.join(f'<tr><td><b>{E(p["k"])}</b><br><small class="mut">{E(p["v"])}</small></td><td>{p["w"]} %</td><td>{de1(p["s"])}</td></tr>' for p in ex['score']['parts'])
    fq=[('Wie bewertet Finvallo Kreditkarten in Deutschland?','Jede Karte bekommt in sieben Kriterien nach festen Regeln 1 bis 5 Sterne: Jahresgebühr (25 %), Reiseversicherung (20 %), Zahlen im Ausland (15 %), Kartenart, Alltag, Bargeld und Extras (je 10 %). Die Gesamtnote ist der gewichtete Durchschnitt.'),
        ('Woher kommen die Daten?','Aus den Preis- und Leistungsverzeichnissen, Produktseiten und Versicherungsbedingungen der deutschen Anbieter. Werte, die wir nur bei Vergleichsportalen finden, markieren wir mit „Sek.“.'),
        ('Beeinflussen Provisionen die Bewertung?','Nein. Ob wir mit einem Anbieter eine Partnerschaft haben, spielt für Sterne und Reihenfolge keine Rolle.')]
    ld=graph(rel,t,d,[('Deutschland','de/'),('Kreditkarten','de/kreditkarten/'),('Methodik',rel)],[{"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in fq]}])
    alt=f'\n<link rel="alternate" hreflang="de-DE" href="https://finvallo.com/{rel}"><link rel="alternate" hreflang="de-AT" href="https://finvallo.com/at/kreditkarten/methodik/">'
    write(rel,head(t,d,rel,P,ld,alt=alt)+f'''{HDR(P,rel)}
<div class="wrap"><main id="app">
<h1>So bewerten wir Kreditkarten in Deutschland</h1><p class="lede">Jede Karte bekommt 1 bis 5 Sterne. Ob wir mit einem Anbieter eine Partnerschaft haben, spielt für Sterne und Reihenfolge keine Rolle. Hier steht genau, wie die Sterne entstehen.</p>
<div class="facts prose"><p><b>Kurz gesagt:</b> Sieben Kriterien, feste Regeln, gleiche Gewichte für alle {len(cards)} Karten. Fehlt eine bestätigte Angabe, zählt das Kriterium mit 2,5 Sternen. Bewertet wird nur, wenn die Jahresgebühr bekannt ist und mindestens 5 der 7 Kriterien bestätigt sind. Stand: {STAND_DE}.</p></div>
<h2>Die Gewichte</h2><div class="tbl"><table><thead><tr><th>Kriterium</th><th>Gewicht</th></tr></thead><tbody>{rows([("Jahresgebühr","25 %"),("Reiseversicherung","20 %"),("Zahlen im Ausland","15 %"),("Kartenart &amp; Akzeptanz","10 %"),("Alltag &amp; Flexibilität","10 %"),("Bargeld","10 %"),("Extras","10 %")])}</tbody></table></div>
<h2>Die Regeln je Kriterium</h2>{rb}
<h2>Was die Sterne bedeuten</h2><div class="tbl"><table><tbody>{rows([("ab 4,5 Sternen","Sehr gut"),("ab 4,0 Sternen","Gut"),("ab 3,5 Sternen","Befriedigend"),("ab 3,0 Sternen","Ausreichend"),("unter 3,0 Sternen","Mangelhaft")])}</tbody></table></div>
<h2>Beispiel: {E(ex["titel"])}</h2><p class="note">So kommt die Karte auf {de1(ex["stars"])} Sterne.</p><div class="tbl"><table><thead><tr><th>Kriterium</th><th>Gewicht</th><th>Sterne</th></tr></thead><tbody>{exrows}<tr><td><b>Gesamt</b></td><td>100 %</td><td><b>{de1(ex["stars"])}</b></td></tr></tbody></table></div>
<h2>Was die Sterne nicht zeigen</h2><div class="prose"><p>Teure Premiumkarten verlieren durch die Jahresgebühr Sterne, auch wenn sich Guthaben und Lounges für Vielreisende lohnen können. Zinsen für Teilzahlung zählen nicht mit, weil sie nur anfallen, wenn du nicht alles zahlst. Für deinen eigenen Fall nimm den <a href="{P}at/kreditkarten/rechner/?land=DE">Kostenrechner</a> und die <a href="../bestenlisten/">Bestenlisten</a>.</p></div>
<h2>Woher die Daten kommen</h2><div class="prose"><p>Zuerst zählen die deutschen Preis- und Leistungsverzeichnisse, Verträge, Versicherungsbedingungen und Produktseiten der Anbieter. Haben wir einen Wert nur von einem Vergleichsportal oder Fachblog, steht „Sek.“ daneben. Konditionen aus Österreich übernehmen wir nicht. Alle Quellen stehen im <a href="../faktencheck/">Faktencheck</a>.</p></div>
<h2>Fragen und Antworten</h2><div class="faq">{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q,a in fq)}</div>
</main>
{footer(P)}''')
    fa=R+'at/kreditkarten/methodik/index.html'; sa=open(fa).read()
    if 'hreflang="de-DE" href="https://finvallo.com/de/kreditkarten/methodik/"' not in sa:
        sa=sa.replace('<link rel="canonical" href="https://finvallo.com/at/kreditkarten/methodik/">','<link rel="canonical" href="https://finvallo.com/at/kreditkarten/methodik/">'+alt,1); open(fa,'w').write(sa)
def faktencheck_page(cards):
    rel='de/kreditkarten/faktencheck/'; P='../../../'
    t='Faktencheck Kreditkarten Deutschland: alle Quellen | Finvallo'
    d=f'Woher die Daten der {len(cards)} Kreditkarten in Deutschland stammen: Preisverzeichnisse, Stand und wo Vergleichsportale veraltet waren.'
    corr=''.join(f'<div class="corr"><div class="f">{E(a)} <span class="tag">Korrektur</span></div><span>{E(b)}</span></div>' for a,b in KORREKTUREN)
    rows=''.join(f'<tr><td><a class="lnk" href="../{c["slug"]}/">{E(c["titel"])}</a></td><td>{ext(c.get("preis") or c.get("quelle"),"Preisverzeichnis" if c.get("preis") else "Produktseite")}</td><td>{E(c.get("stand") or "–")}</td><td>{E(", ".join(SEKN.get(x,x) for x in c["sek"]) or "–")}</td></tr>' for c in sorted(cards,key=lambda c:c['titel'].lower()))
    nsek=sum(1 for c in cards if c['sek'])
    ld=graph(rel,t,d,[('Deutschland','de/'),('Kreditkarten','de/kreditkarten/'),('Faktencheck',rel)])
    write(rel,head(t,d,rel,P,ld)+f'''{HDR(P,rel)}
<div class="wrap"><main id="app">
<h1>Faktencheck: Kreditkarten in Deutschland</h1><p class="lede">Für jede Karte zeigen wir, aus welchem Dokument die Werte stammen und welche Angaben nur aus Sekundärquellen kommen.</p>
<div class="facts prose"><p><b>Kurz gesagt:</b> Wir haben {len(cards)} Karten mit den Preis- und Leistungsverzeichnissen der Anbieter geprüft (Stand {STAND_DE}). Bei {len(cards)-nsek} Karten stammen alle bewertungsrelevanten Werte direkt vom Anbieter, bei {nsek} Karten ist mindestens ein Wert mit „Sek.“ markiert. Vergleichsportale waren bei mehreren Karten veraltet.</p></div>
<h2>Wo Vergleichsportale veraltet waren</h2><div style="display:grid;gap:10px">{corr}</div>
<h2>Quellen je Karte</h2><div class="tbl wide"><table><thead><tr><th>Karte</th><th>Quelle</th><th>Stand</th><th>Nur Sekundärquelle</th></tr></thead><tbody>{rows}</tbody></table></div>
</main>
{footer(P)}''')
SEKN={'fee':'Jahresgebühr','fee1':'1. Jahr','fx':'Ausland','fxText':'Ausland','cash':'Bargeld','cashText':'Bargeld','pay':'Apple/Google Pay','auto':'Abbuchung','insText':'Versicherung','tier':'Versicherung','bonus':'Bonus','cbText':'Cashback','soll':'Zins','effz':'Zins','zinsfrei':'zinsfreie Tage','rahmen':'Kreditrahmen','lgText':'Lounge','creditsText':'Guthaben','konto':'Konto','cashInterest':'Bargeldzinsen','feeNote':'Gebührenhinweis','giro':'Konto nötig','netz':'Kartennetz'}

if __name__=='__main__': main()
