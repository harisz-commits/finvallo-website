# Festgeld-Vergleich Deutschland und Österreich: Liste mit Rechner und Filtern, Laufzeit-Seiten, Angebotsseiten, Methodik.
# Daten: daten/<land>/festgeld.json (aus festgeld_daten.py, jede Zahl aus der Konditionsseite der Bank oder Plattform, mit Quelle und Prüfdatum),
# daten/festgeld-laender.json (Einlagensicherung und S&P-Länderrating je Sitzland).
# Rechnung gibt es zweimal: ertrag() hier und calc() in public/assets/festgeld.js. check.py vergleicht beide (tools/festgeld-kontrolle.js).
# Läuft nach girokonto.py, vor header.py.
import hashlib,json,os,re,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import karten as K
from score import eur,pct

E=K.E; dmy=K.dmy; R=K.R; SP=K.SP
LAND='de'
def dpath(land): return os.path.join(SP,'daten',land,'festgeld.json')
LP=os.path.join(SP,'daten','festgeld-laender.json')
CFG={'de':dict(N='Deutschland',code='DE',heim='deutsche',heimF='Deutsche Einlagensicherung',heimB='deutschen Banken',bl_slug='deutsche-banken',
        steuer='Zinsen sind in Deutschland Kapitalerträge. Deutsche Banken ziehen die Abgeltungsteuer (25 % plus Solidaritätszuschlag und gegebenenfalls Kirchensteuer) automatisch ab, soweit kein Freistellungsauftrag vorliegt. Bis 1.000 € Kapitalerträge im Jahr (2.000 € für Paare) bleiben mit Freistellungsauftrag steuerfrei. Bei Banken im Ausland musst du die Zinsen oft selbst in der Anlage KAP angeben, außer die Plattform führt die Steuer für dich ab.',
        sich='In Deutschland sichert die Entschädigungseinrichtung deutscher Banken (EdB) Einlagen bis 100.000 € pro Person und Bank. Viele private Banken sind zusätzlich im Einlagensicherungsfonds des Bankenverbands. Alle EU-Länder sichern Einlagen nach denselben Regeln bis 100.000 €; wie belastbar die Sicherung im Ernstfall ist, hängt aber auch von der Finanzkraft des Landes ab.',
        steuer_kurz='Abgeltungsteuer',llms_vor=None),
     'at':dict(N='Österreich',code='AT',heim='österreichische',heimF='Österreichische Einlagensicherung',heimB='österreichischen Banken',bl_slug='oesterreichische-banken',
        steuer='Zinsen aus Spareinlagen kosten in Österreich 25 % Kapitalertragsteuer (KESt). Österreichische Banken behalten sie automatisch ein, damit ist die Steuer erledigt (Endbesteuerung). Bei Banken im Ausland wird die KESt meist nicht abgezogen: Dann musst du die Zinsen selbst in der Steuererklärung (E 1kv) angeben, außer die Plattform führt die Steuer für dich ab.',
        sich='In Österreich sichert die Einlagensicherung AUSTRIA (ESA) bzw. die Sparkassen-Haftungsgesellschaft Einlagen bis 100.000 € pro Person und Bank. Alle EU-Länder sichern Einlagen nach denselben Regeln bis 100.000 €; wie belastbar die Sicherung im Ernstfall ist, hängt aber auch von der Finanzkraft des Landes ab.',
        steuer_kurz='KESt',llms_vor=None)}
CC=CFG['de']; OTHER={}
# Laufzeiten mit eigener Seite: (Monate, Slug, Text)
LZ=[(1,'1-monat','1 Monat'),(3,'3-monate','3 Monate'),(6,'6-monate','6 Monate'),(9,'9-monate','9 Monate'),(12,'1-jahr','1 Jahr'),(18,'18-monate','18 Monate'),
    (24,'2-jahre','2 Jahre'),(36,'3-jahre','3 Jahre'),(48,'4-jahre','4 Jahre'),(60,'5-jahre','5 Jahre'),(72,'6-jahre','6 Jahre'),(84,'7-jahre','7 Jahre'),(96,'8-jahre','8 Jahre'),(120,'10-jahre','10 Jahre')]
LZT={m:t for m,_,t in LZ}
DEF_B=10000; DEF_M=12; MIN_LZ_SEITE=5
RAT={'AAA':22,'AA+':21,'AA':20,'AA-':19,'A+':18,'A':17,'A-':16,'BBB+':15,'BBB':14,'BBB-':13,'BB+':12,'BB':11,'BB-':10,'B+':9,'B':8,'B-':7}
ZZT={'jaehrlich':'jährlich','endfaellig':'am Ende der Laufzeit','monatlich':'monatlich','quartalsweise':'vierteljährlich','halbjaehrlich':'halbjährlich','wahlweise':'nach Wahl'}
LAENDER={}

def lzt(m):
    if m in LZT: return LZT[m]
    if m<1: return f'{round(m*4)} Wochen' if m!=0.25 else '1 Woche'
    if m%12==0: return f'{m//12} Jahre'
    return f'{eur(m)} Monate'
def load(land=None):
    d=json.load(open(dpath(land or LAND),encoding='utf-8')); xs=d['angebote']
    for a in xs: a['slug']=a['id']
    return d,xs

# ---------- Rechnung (gleich wie calc() in festgeld.js) ----------
def ertrag(a,b,m):
    rows=[z for z in a['zinsen'] if z['monate']==m]
    if not rows: return dict(fit=False,why='lz')
    best=None
    for z in rows:
        if (z['min'] is None or b>=z['min']) and (z['max'] is None or b<=z['max']) and (best is None or z['zins']>best['zins']): best=z
    if best is None or (a.get('min_anlage') is not None and b<a['min_anlage']) or (a.get('max_anlage') is not None and b>a['max_anlage']):
        return dict(fit=False,why='betrag',zins=max(z['zins'] for z in rows))
    j=m/12; z=best['zins']/100
    e=b*((1+z)**j-1) if m>12 and a.get('zinseszins') is True else b*z*j
    return dict(fit=True,zins=best['zins'],ertrag=round(e+1e-9,2))
def jsdata(a):
    return {'z':[[z['monate'],z['zins'],z['min'],z['max']] for z in a['zinsen']],'amin':a.get('min_anlage'),'amax':a.get('max_anlage'),'ze':a.get('zinseszins')}
def laufzeiten(a): return sorted({z['monate'] for z in a['zinsen']})
def topzins(a,m=None):
    xs=[z['zins'] for z in a['zinsen'] if m is None or z['monate']==m]
    return max(xs) if xs else None

# ---------- Länder und Texte ----------
def land(a): return LAENDER.get(a['sitz']) or {}
def landN(a): return land(a).get('name') or a['sitz']
def rating(a):
    r=land(a).get('rating_sp')
    return None if r in (None,'','NR') else r
def ratnum(a): return RAT.get(rating(a) or '',0)
def heim(a): return a['sitz']==CC['code']
def plattform(a): return a['vertrieb']!='direkt'
def vtT(a): return 'direkt bei der Bank' if not plattform(a) else f'über {a["vertrieb"].replace("andere: ","")}'
def zzT(a): return ZZT.get(a.get('zinszahlung'),'keine Angabe')
def kdT(a): return {'nein':'nicht möglich','ja':'möglich','ja_mit_abschlag':'möglich, mit Abschlag'}.get(a.get('kuendigung'),'keine Angabe')
def vlT(a): return {'automatisch':'verlängert sich automatisch','keine':'Geld wird ausgezahlt','wahlweise':'Verlängerung wählbar'}.get(a.get('verlaengerung'),'keine Angabe')
def anlT(a):
    lo,hi=a.get('min_anlage'),a.get('max_anlage')
    if lo is None and hi is None: return 'keine Angabe'
    t=f'ab {eur(lo)} €' if lo is not None else 'ohne Mindestbetrag'
    return t+(f' bis {eur(hi)} €' if hi is not None else '')
def sichT(a):
    l=land(a); s=a.get('einlagensicherung') or {}
    w=s.get('waehrung')
    bt=f'{eur(s["betrag"])} {w}' if w and s.get('betrag') else f'{eur(s.get("betrag") or l.get("betrag") or 100000)} €'
    t=(s.get('system') or l.get('sicherung') or f'gesetzliche Einlagensicherung {landN(a)}')+f', bis {bt} pro Person'
    return t
def steuerT(a):
    if a.get('steuer_auto') is True: return f'{CC["steuer_kurz"]} wird automatisch abgeführt'
    if a.get('steuer_auto') is False: return 'Zinsen selbst in der Steuererklärung angeben'
    return 'keine Angabe'
def titel(a): return f'{a["bank"]} {a["produkt"]}'
def lzspan(a):
    l=laufzeiten(a)
    return lzt(l[0]) if len(l)==1 else f'{lzt(l[0])} bis {lzt(l[-1])}'

def pros(a):
    p=[]
    if heim(a): p.append(CC['heimF'])
    elif ratnum(a)>=RAT['AA']: p.append(f'Einlagensicherung in {landN(a)} (Länderrating {rating(a)})')
    if a.get('steuer_auto') is True: p.append(f'{CC["steuer_kurz"]} wird automatisch abgeführt')
    if a.get('zinszahlung') in ('jaehrlich','monatlich','quartalsweise','halbjaehrlich'): p.append(f'Zinsen {zzT(a)}')
    if a.get('zinseszins') is True and max(laufzeiten(a))>12: p.append('Zinseszins bei mehrjähriger Laufzeit')
    if a.get('kuendigung') in ('ja','ja_mit_abschlag'): p.append('Vorzeitig kündbar'+(' (mit Abschlag)' if a['kuendigung']=='ja_mit_abschlag' else ''))
    if a.get('min_anlage') is not None and a['min_anlage']<=1000: p.append(f'Schon ab {eur(a["min_anlage"])} € anlegen')
    if len(laufzeiten(a))>=6: p.append(f'{len(laufzeiten(a))} Laufzeiten zur Wahl')
    if a.get('verlaengerung')=='keine': p.append('Keine automatische Verlängerung')
    return p
def cons(a):
    c=[]
    if not heim(a): c.append(f'Einlagensicherung in {landN(a)}'+(f' (Länderrating {rating(a)})' if rating(a) else ''))
    if a.get('steuer_auto') is False: c.append('Zinsen selbst in der Steuererklärung angeben')
    if a.get('kuendigung')=='nein': c.append('Vorzeitig nicht kündbar')
    if a.get('neukunden_only') is True: c.append('Nur für Neukundinnen und Neukunden')
    if a.get('min_anlage') is not None and a['min_anlage']>=5000: c.append(f'Mindestanlage {eur(a["min_anlage"])} €')
    if a.get('zinszahlung')=='endfaellig' and max(laufzeiten(a))>12: c.append('Zinsen erst am Ende der Laufzeit')
    if a.get('verlaengerung')=='automatisch': c.append('Verlängert sich automatisch, wenn du nicht rechtzeitig kündigst')
    if a.get('konto_noetig'): c.append(f'Zusätzliches Konto nötig: {a["konto_noetig"]}')
    return c
def flags(a):
    f=[]
    if heim(a): f.append('heim')
    if a.get('steuer_auto') is True: f.append('steuer')
    if not plattform(a): f.append('direkt')
    if a.get('kuendigung') in ('ja','ja_mit_abschlag'): f.append('kuend')
    if a.get('neukunden_only') is not True: f.append('alle')
    return ' '.join(f)

# ---------- Bausteine ----------
def face(a): return f'<div class="face k-Debit" aria-hidden="true"><span class="pn">{E(a["bank"])}</span><span class="chipc"></span><span class="nw">FESTGELD</span></div>'
def tags(a):
    t=f'<span class="tag {"kl" if heim(a) else "out"}">Einlagensicherung {E(a["sitz"])}</span>'
    if rating(a): t+=f'<span class="tag out">Rating {E(rating(a))}</span>'
    t+=f'<span class="tag out">Zinsen {E(zzT(a))}</span>'
    if plattform(a): t+=f'<span class="tag typ">{E(vtT(a))}</span>'
    return t
def item(a,P,base,m,rank,hide=False):
    r=ertrag(a,DEF_B,m)
    zt=f'{pct(r["zins"])}' if r.get('zins') is not None else '–'
    et=f'{eur(r["ertrag"])} €' if r['fit'] else 'passt nicht'
    akt=f'<div class="earn"><span>Aktion</span><b>{E(a["aktion"])}</b></div>' if a.get('aktion') else ''
    rk=f'<span class="rank{" r"+str(rank) if rank<=3 else ""}">{rank}</span>' if rank else ''
    return f'''<article class="item" id="fg-{a["slug"]}" data-k='{E(json.dumps(jsdata(a),separators=(",",":")))}' data-f="{flags(a)}" data-sitz="{a["sitz"]}" data-rat="{ratnum(a)}" data-zz="{a.get("zinszahlung") or ""}" data-q="{E((a["bank"]+" "+a["produkt"]+" "+a["vertrieb"]).lower())}"{" hidden" if hide else ""}>
    <div class="ihead"><div style="display:flex;gap:10px;align-items:center">{rk}</div></div>
    <div class="irow">{face(a)}<div style="min-width:0"><h3 class="iname"><a href="{base}{a["slug"]}/">{E(titel(a))}</a></h3><div class="iprov">{E(landN(a))} · {E(vtT(a))}</div></div></div>
    <div class="tags">{tags(a)}</div>
    <div class="stats"><div><small>Zins p. a.</small><b class="good" data-zins>{zt}</b></div><div><small data-lbl>Zinsen für {eur(DEF_B)} €</small><b data-ertrag>{et}</b></div><div><small>Mindestanlage</small><b>{eur(a["min_anlage"])+" €" if a.get("min_anlage") is not None else "keine"}</b></div></div>
    <p class="note" data-why style="margin:0"></p>
    {akt}
    <ul class="checks">{"".join(f"<li>{E(x)}</li>" for x in pros(a)[:3])}</ul>
    <div class="acts"><a class="btn primary block" href="{E(a.get("vertrieb_url") or a["quelle"])}" target="_blank" rel="noopener nofollow">Zum Angebot ↗</a><a class="btn ghost block" href="{base}{a["slug"]}/">Details ansehen</a></div>
  </article>'''

def calcbox(m,nav=None):
    opts=''.join(f'<option value="{x}"{" selected" if x==m else ""}>{lzt(x)}</option>' for x in sorted(LZ_DA))
    return f'''<div class="box lcalc" id="fcalc" hidden>
    <h2 style="margin-top:0">Wie viel Zinsen bekommst du?</h2>
    <div class="lgrid"><label><span class="flab">Anlagebetrag (€)</span><input type="number" min="0" step="500" value="{DEF_B}" data-in="betrag" name="betrag" inputmode="numeric"></label>
    <label><span class="flab">Laufzeit</span><select data-in="lz" name="laufzeit"{f' data-nav="{nav}"' if nav else ""}>{opts}</select></label></div>
    <p class="note" style="margin:8px 0 0">Zinsen vor Steuern. Bei mehr als 12 Monaten rechnen wir mit Zinseszins nur, wenn die Bank die Zinsen mitverzinst.</p>
  </div>'''
def filterbox(xs,n):
    chips=[('heim',CC['heimF']),('steuer',f'{CC["steuer_kurz"]} automatisch'),('direkt','Direkt bei der Bank'),('kuend','Vorzeitig kündbar'),('alle','Auch für Bestandskunden')]
    opt=lambda v:''.join(f'<option value="{a}">{b}</option>' for a,b in v)
    ls=sorted({a['sitz'] for a in xs},key=lambda c:(c!=CC['code'],(LAENDER.get(c) or {}).get('name') or c))
    return f'''<div class="box filt" id="filt" hidden>
    <label class="fq"><span class="sr">Suche</span><input type="search" data-q placeholder="Bank suchen" autocomplete="off"></label>
    <div class="chips">{"".join(f'<button type="button" class="chip" data-flag="{a}" aria-pressed="false">{t}</button>' for a,t in chips)}</div>
    <div class="frow"><select data-sitz aria-label="Land der Einlagensicherung">{opt([("","Alle Länder")]+[(c,(LAENDER.get(c) or {}).get("name") or c) for c in ls])}</select>
    <select data-rat aria-label="Länderrating mindestens">{opt([("","Jedes Länderrating"),(RAT["AAA"],"Rating AAA"),(RAT["AA-"],"Rating mindestens AA-"),(RAT["A-"],"Rating mindestens A-"),(RAT["BBB-"],"Rating mindestens BBB-")])}</select>
    <select data-zz aria-label="Zinszahlung">{opt([("","Jede Zinszahlung"),("jaehrlich","Zinsen jährlich"),("endfaellig","Zinsen am Ende"),("monatlich","Zinsen monatlich"),("quartalsweise","Zinsen vierteljährlich")])}</select>
    <select data-sort aria-label="Sortierung">{opt([("zins","Höchster Zins zuerst"),("rat","Bestes Länderrating zuerst"),("name","Nach Name")])}</select></div>
    <div class="fbot"><b data-count>{n} Angebote</b><button type="button" class="lnk" data-reset hidden>Filter zurücksetzen</button></div>
  </div>'''
def ordnen(xs,m):
    """Sortierung wie im Browser: passende zuerst, dann Zins, Länderrating."""
    def key(a):
        r=ertrag(a,DEF_B,m)
        return (r.get('why')=='lz',not r['fit'],-(r.get('zins') or 0),-ratnum(a),a['bank'].lower())
    return sorted(xs,key=key)
def script(P):
    v=hashlib.sha256(open(R+'assets/festgeld.js','rb').read()).hexdigest()[:8]
    return f'<script src="{P}assets/festgeld.js?v={v}" defer></script>\n</body>'

def hdr(P,rel):
    o='at' if LAND=='de' else 'de'; rest=rel.split('/',1)[1]
    sl=rest.split('/')[1] if rest.count('/')>=2 else ''
    other=f'{o}/{rest}' if (not sl or sl in OTHER.get(o,set())) and OTHER.get(o) else (f'{o}/festgeld/' if OTHER.get(o) else f'{o}/')
    return K.HDR(P,rel,other)
def head(t,d,rel,P,ld): return K.head(t,d,rel,P,ld)
def faqhtml(fq): return '<div class="faq">'+''.join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q,a in fq)+'</div>'
def faqld(fq): return {"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in fq]}
def S(xs): return dmy(max(a['geprueft'] for a in xs))

# ---------- Listen ----------
def kennzahlen(xs,m):
    ok=[a for a in xs if ertrag(a,DEF_B,m)['fit']]
    if not ok: return None
    best=ordnen(ok,m)[0]; hb=[a for a in ok if heim(a)]
    bh=ordnen(hb,m)[0] if hb else None
    zs=sorted(ertrag(a,DEF_B,m)['zins'] for a in ok)
    return dict(best=best,bz=ertrag(best,DEF_B,m)['zins'],bh=bh,bhz=ertrag(bh,DEF_B,m)['zins'] if bh else None,med=zs[len(zs)//2],n=len(ok))
def gen_fq(xs,m=None):
    N=CC['N']; kz=kennzahlen(xs,m or DEF_M)
    fq=[]
    if kz:
        t=lzt(m or DEF_M)
        fq.append((f'Wo gibt es aktuell die höchsten Festgeldzinsen für {t}?',f'Am meisten zahlt laut unserem Vergleich {titel(kz["best"])} mit {pct(kz["bz"])} pro Jahr ({vtT(kz["best"])}, Einlagensicherung {landN(kz["best"])}).'+(f' Bei {CC["heimB"]} liegt {titel(kz["bh"])} mit {pct(kz["bhz"])} vorn.' if kz['bh'] and kz['bh'] is not kz['best'] else '')+f' Stand: {S(xs)}.'))
    fq+=[('Wie sicher ist Festgeld?',CC['sich']),
         ('Wie werden Festgeld-Zinsen versteuert?',CC['steuer']),
         ('Kann ich Festgeld vorzeitig kündigen?','Meist nicht: Das Geld ist bis zum Ende der Laufzeit fest angelegt. Manche Banken erlauben eine vorzeitige Auflösung, dann meist mit Zinsabschlag. Ob das geht, steht bei jedem Angebot. Geld, das du kurzfristig brauchen könntest, liegt besser auf einem Tagesgeldkonto.'),
         ('Was ist der Unterschied zwischen Festgeld und Tagesgeld?','Beim Festgeld legst du Geld für eine feste Zeit zu einem festen Zins an. Beim Tagesgeld kommst du jeden Tag an dein Geld, dafür kann die Bank den Zins jederzeit ändern.'),
         ('Spielen Provisionen eine Rolle?','Nein. Wir sortieren nach Zins für deinen Betrag und deine Laufzeit. Provisionen haben keinen Einfluss auf die Reihenfolge, und es gibt keine bezahlten Platzierungen.')]
    return fq
def list_page(xs,d,m=DEF_M,lzslug=None,sub=None):
    """Gesamtvergleich (m=12, alle Angebote), Laufzeit-Seite (lzslug) oder Unterliste (sub=(slug,titel,filter,text))."""
    N=CC['N']; base='' if not (lzslug or sub) else '../'
    if lzslug:
        rel=f'{LAND}/festgeld/{lzslug}/'; P='../../../'
        X=[a for a in xs if m in laufzeiten(a)]
        h1=f'Festgeld {lzt(m)}: Zinsen im Vergleich'
    elif sub:
        rel=f'{LAND}/festgeld/{sub[0]}/'; P='../../../'
        X=[a for a in xs if sub[2](a)]
        h1=sub[1]
    else:
        rel=f'{LAND}/festgeld/'; P='../../'; X=xs; h1=f'Festgeld-Vergleich {N}'
    X=ordnen(X,m); kz=kennzahlen(X,m); n=len(X); nb=len({a['bank'] for a in X}); st=S(xs)
    shown=[a for a in X if m in laufzeiten(a)]
    if lzslug:
        t=f'Festgeld {lzt(m)}: Zinsen von {nb} Banken im Vergleich | Finvallo'
        ds=f'Festgeld mit {lzt(m)} Laufzeit in {N}: {n} Angebote verglichen.'+(f' Bis {pct(kz["bz"])} Zinsen pro Jahr.' if kz else '')+f' Mit Zinsrechner, Stand {st}.'
    elif sub:
        t=f'{sub[1]} 2026 | Finvallo'
        ds=sub[3][:120].rsplit(' ',1)[0]+f'. Stand {st}.'
    else:
        t=f'Festgeld-Vergleich {N} 2026: {n} Angebote | Finvallo'
        ds=f'{n} Festgeld-Angebote von {nb} Banken für {N} verglichen: Zinsen nach Laufzeit und Betrag, Einlagensicherung, Länderrating, Zinszahlung und Steuer.'
    ds=K.fit_desc(ds) if hasattr(K,'fit_desc') else ds[:155]
    fq=gen_fq(X,m)
    crumbs=[(N,f'{LAND}/'),('Festgeld',f'{LAND}/festgeld/')]+([(lzt(m) if lzslug else sub[1],rel)] if (lzslug or sub) else [])
    top=[a for a in X if ertrag(a,DEF_B,m)['fit']][:10]
    ld=K.graph(rel,t,ds,crumbs,[{"@type":"ItemList","name":h1,"itemListElement":[{"@type":"ListItem","position":i+1,"name":titel(a),"url":f"https://finvallo.com/{LAND}/festgeld/{a['slug']}/"} for i,a in enumerate(top)]},faqld(fq)],date=max(a['geprueft'] for a in xs))
    rank=0; items=''
    for a in X:
        vis=m in laufzeiten(a)
        if vis and ertrag(a,DEF_B,m)['fit']: rank+=1
        items+=item(a,P,base,m,rank if vis and ertrag(a,DEF_B,m)['fit'] else 0,hide=not vis)
    kurz=''
    if kz:
        kurz=f'<b>Kurz gesagt:</b> Für {eur(DEF_B)} € und {lzt(m)} zahlt {E(titel(kz["best"]))} am meisten: {pct(kz["bz"])} pro Jahr, Einlagensicherung {E(landN(kz["best"]))}.'
        if kz['bh'] and kz['bh'] is not kz['best']: kurz+=f' Bestes Angebot mit {E(CC["heim"])}r Einlagensicherung: {E(titel(kz["bh"]))} mit {pct(kz["bhz"])}.'
        kurz+=f' Die Hälfte der {kz["n"]} passenden Angebote zahlt mindestens {pct(kz["med"])}. Stand: {st}.'
    lzlinks=' · '.join(f'<a class="lnk" href="{"../" if (lzslug or sub) else ""}{s}/"{" aria-current=page" if s==lzslug else ""}>{t_}</a>' for x,s,t_ in LZ if x in LZ_SEITEN)
    if lzslug: lede=f'Alle Festgeld-Angebote mit {lzt(m)} Laufzeit, sortiert nach Zins für deinen Betrag. Jede Zahl stammt von der Konditionsseite der Bank oder der Plattform, über die du abschließt.'
    elif sub: lede=sub[3]
    else: lede=f'{n} Festgeld-Angebote von {nb} Banken, die Kundinnen und Kunden aus {N} annehmen. Wähle Betrag und Laufzeit, filtere nach Einlagensicherung, Länderrating und Zinszahlung. Jede Zahl stammt von der Konditionsseite der Bank oder der Plattform. Provisionen haben keinen Einfluss auf die Reihenfolge.'
    nav=f'{P}{LAND}/festgeld/' if (lzslug or sub) else None
    raus=d.get('nicht_aufgenommen') or []
    fehlt='' if (lzslug or sub) else f'''<h2>Welche Banken fehlen und warum?</h2><div class="prose"><p>Wir nehmen nur Angebote auf, die man von überall in {N} abschließen kann und deren Einlagen über eine gesetzliche Einlagensicherung in der EU geschützt sind. Regionale Banken, die nur Kundschaft aus ihrer Region nehmen, fehlen. {len(raus)} geprüfte Angebote haben wir nicht aufgenommen, etwa weil es kein Neugeschäft gibt oder die Bank keine überprüfbaren Konditionen veröffentlicht.</p>
<details><summary>Liste ansehen</summary><ul>{"".join(f"<li><b>{E(x['name'])}</b>: {E(x['grund'])}</li>" for x in raus)}</ul></details></div>'''
    body=f'''{hdr(P,rel)}
<div class="wrap"><main id="app">
{f'<div class="crumb"><span><a href="../">Festgeld</a> › {E(lzt(m) if lzslug else sub[1])}</span><span>Stand {st}</span></div>' if (lzslug or sub) else ''}
<h1>{E(h1)}</h1>
  <p class="lede">{E(lede)}</p>
  {f'<div class="facts prose"><p>{kurz}</p></div>' if kurz else ''}
  <p class="note" style="margin:6px 0 14px">Laufzeiten: {lzlinks}<br>Nur mit {E(CC["heim"])}r Einlagensicherung: <a class="lnk" href="{"../" if (lzslug or sub) else ""}{CC["bl_slug"]}/">Festgeld bei {E(CC["heimB"])}</a> · <a class="lnk" href="{"../" if (lzslug or sub) else ""}methodik/">So vergleichen wir</a></p>
  {calcbox(m,nav if lzslug else None)}
  {filterbox(X,len(shown))}
  <div class="list" data-fg data-limit="30">{items}</div>
  <button type="button" class="btn ghost block" data-more hidden>Alle Angebote zeigen</button>
  <h2>Festgeld: das Wichtigste in Kürze</h2><div class="prose"><p><b>Zins und Laufzeit:</b> Der Zins steht für die ganze Laufzeit fest. Längere Laufzeiten bringen nicht immer mehr Zinsen; vergleiche deshalb mehrere Laufzeiten.</p>
  <p><b>Sicherheit:</b> {E(CC["sich"])}</p><p><b>Steuern:</b> {E(CC["steuer"])}</p></div>
  {fehlt}
  <h2>Fragen und Antworten</h2>{faqhtml(fq)}
</main>
{K.footer(P)}'''
    body=body.replace('</body>',script(P),1)
    K.write(rel,head(t,ds,rel,P,ld)+body)

# ---------- Angebotsseite ----------
def offer_page(a,xs):
    rel=f'{LAND}/festgeld/{a["slug"]}/'; P='../../../'; N=CC['N']
    tz=topzins(a); lzs=laufzeiten(a)
    t=f'{titel(a)}{" über "+a["vertrieb"] if plattform(a) else ""}: Zinsen {N} | Finvallo'
    if len(t)>65: t=f'{titel(a)}: Festgeld-Zinsen {CC["code"]} | Finvallo'
    if len(t)>65: t=f'{titel(a)} ({CC["code"]}) | Finvallo'
    d=f'{titel(a)} {vtT(a)}: bis {pct(tz)} Zinsen, Laufzeit {lzspan(a)}, Anlage {anlT(a)}. Einlagensicherung {landN(a)}, Zinsen {zzT(a)}.'
    d=K.fit_desc(d) if hasattr(K,'fit_desc') else d[:155]
    gp=a['geprueft']
    fq=[(f'Wie viel Zinsen zahlt {titel(a)}?',f'{titel(a)} zahlt je nach Laufzeit bis {pct(tz)} pro Jahr ({lzspan(a)}). Stand: {dmy(a.get("stand") or gp)}.'),
        ('Wie sicher ist das Geld?',f'Die Einlagen sind über die {sichT(a)} geschützt'+(f'. Länderrating {landN(a)} (S&P): {rating(a)}.' if rating(a) else '.')+(f' Zusätzlich: {a["einlagensicherung"]["freiwillig"]}.' if (a.get('einlagensicherung') or {}).get('freiwillig') else '')),
        ('Wann werden die Zinsen gezahlt?',(a.get('zinszahlung_text') or zzT(a)).rstrip('.')+'.'),
        ('Wird die Steuer automatisch abgezogen?',(a.get('steuer') or steuerT(a)).rstrip('.')+'.'),
        ('Kann ich vorzeitig an mein Geld?',(a.get('kuendigung_text') or kdT(a)).rstrip('.')+'.')]
    if plattform(a): fq.append((f'Wie schließe ich das Festgeld ab?',f'Über {a["vertrieb"].replace("andere: ","")}. '+(f'Dafür brauchst du: {a["konto_noetig"]}.' if a.get('konto_noetig') else 'Das Konto dort ist kostenlos.' if (a.get('kosten') or '').startswith('kostenlos') else '')))
    ld=K.graph(rel,t,d,[(N,f'{LAND}/'),('Festgeld',f'{LAND}/festgeld/'),(titel(a),rel)],
        [{"@type":"DepositAccount","@id":f"https://finvallo.com/{rel}#angebot","name":titel(a),"url":f"https://finvallo.com/{rel}","provider":{"@type":"BankOrCreditUnion","name":a.get('institut') or a['bank']},
          "areaServed":{"@type":"Country","name":N},"interestRate":tz,"amount":{"@type":"MonetaryAmount","currency":"EUR","minValue":a.get('min_anlage'),"maxValue":a.get('max_anlage')}},faqld(fq)],date=gp)
    rows=''
    for m in lzs:
        r=ertrag(a,DEF_B,m); zs=[z for z in a['zinsen'] if z['monate']==m]
        ztxt='<br>'.join(f'{pct(z["zins"])}'+(f' <small class="mut">({("ab "+eur(z["min"])+" €") if z["min"] is not None else ""}{" " if z["min"] is not None and z["max"] is not None else ""}{("bis "+eur(z["max"])+" €") if z["max"] is not None else ""})</small>' if (z['min'] is not None or z['max'] is not None) and len(zs)>1 else '') for z in zs)
        rows+=f'<tr><td>{lzt(m)}</td><td><b>{ztxt}</b></td><td>{eur(r["ertrag"])+" €" if r["fit"] else "–"}</td></tr>'
    r_=lambda k,v: f'<div class="r"><span>{k}</span><span>{v}</span></div>'
    na='<span class="mut na">keine Angabe</span>'; v=lambda x: E(x) if x not in (None,'') else na
    es=a.get('einlagensicherung') or {}
    cond=('<div class="cond" style="margin-bottom:14px"><div class="gh">Anlage</div>'+r_('Anlagebetrag',E(anlT(a)))+r_('Laufzeiten',E(', '.join(lzt(m) for m in lzs)))+r_('Zinszahlung',v(a.get('zinszahlung_text') or zzT(a)))
          +r_('Zinseszins',{True:'ja',False:'nein'}.get(a.get('zinseszins'),na))+r_('Vorzeitig kündbar',v(a.get('kuendigung_text') or kdT(a)))+r_('Am Laufzeitende',E(vlT(a)))
          +'</div><div class="cond" style="margin-bottom:14px"><div class="gh">Sicherheit</div>'+r_('Bank',E(a.get('institut') or a['bank']))+r_('Sitz der Einlagensicherung',E(landN(a)))
          +r_('Gesetzliche Einlagensicherung',E(sichT(a)))+(r_('Zusätzliche Sicherung',E(es['freiwillig'])) if es.get('freiwillig') else '')+r_('Länderrating (S&P)',v(rating(a)))
          +'</div><div class="cond" style="margin-bottom:14px"><div class="gh">Steuer und Abschluss</div>'+r_('Steuer',v(a.get('steuer') or steuerT(a)))+r_('Abschluss',E(vtT(a)))
          +r_('Zusätzliches Konto',v(a.get('konto_noetig')) if a.get('konto_noetig') else 'nicht nötig' if a.get('konto_noetig') is None and not plattform(a) else na)
          +r_('Kosten',v(a.get('kosten')))+r_('Eröffnung',v({'online':'online','filiale':'in der Filiale','beides':'online oder in der Filiale'}.get(a.get('eroeffnung'))))+r_('Legitimation',v(a.get('legitimation')))
          +r_('Nur für Neukunden',{True:'ja',False:'nein'}.get(a.get('neukunden_only'),na))+r_('Gemeinschaftskonto',{True:'möglich',False:'nicht möglich'}.get(a.get('gemeinschaftskonto'),na))
          +(r_('Aktion',E(a['aktion'])) if a.get('aktion') else '')+(r_('Hinweis',E(a['hinweis'])) if a.get('hinweis') else '')+'</div>')
    m0=DEF_M if DEF_M in lzs else lzs[0]
    sim=[x for x in xs if x is not a and m0 in laufzeiten(x) and ertrag(x,DEF_B,m0)['fit']]
    sim=ordnen(sim,m0)[:5]
    simt=''.join(f'<tr><td><a class="lnk" href="../{x["slug"]}/">{E(titel(x))}</a><br><small class="mut">{E(vtT(x))}</small></td><td><b>{pct(ertrag(x,DEF_B,m0)["zins"])}</b></td><td>{E(landN(x))}{" ("+E(rating(x))+")" if rating(x) else ""}</td></tr>' for x in sim)
    glance=f'{titel(a)} ist ein Festgeld der {a.get("institut") or a["bank"]}, abgeschlossen {vtT(a)}. Es gibt {len(lzs)} Laufzeit{"en" if len(lzs)>1 else ""} ({lzspan(a)}) mit bis zu {pct(tz)} Zinsen pro Jahr. Anlage {anlT(a)}, Zinsen {zzT(a)}. Die Einlagen sichert {landN(a)}. Stand: {dmy(a.get("stand") or gp)}.'
    pc,kc=pros(a),cons(a)
    body=f'''{hdr(P,rel)}
<div class="wrap"><main id="app">
<div class="crumb"><span><a href="../">Festgeld</a> › {E(a["bank"])}</span><span class="ok">✓ Geprüft am {dmy(gp)}</span></div>
  <div class="dh">{face(a)}<div style="min-width:0"><div class="tags">{tags(a)}</div>
    <h1>{E(titel(a))}{f' <small class="mut">über {E(a["vertrieb"].replace("andere: ",""))}</small>' if plattform(a) else ''}</h1></div></div>
  <div class="box feebox"><small>Zins pro Jahr</small><span class="big good">bis {pct(tz)}</span><small class="mut">Laufzeit {E(lzspan(a))} · Anlage {E(anlT(a))}</small>
    <a class="btn primary block" href="{E(a.get("vertrieb_url") or a["quelle"])}" target="_blank" rel="noopener nofollow">Zum Angebot ↗</a>
    <div class="actrow"><a class="plink" href="{E(a["quelle"])}" target="_blank" rel="noopener">Konditionen beim Anbieter ↗</a></div></div>
  <section class="facts box glance" aria-label="Auf einen Blick"><h2 style="margin-top:0">Auf einen Blick</h2><div class="prose"><p>{E(glance)}</p></div></section>
  <h2>Zinsen nach Laufzeit</h2>
  <div class="tbl"><table><thead><tr><th>Laufzeit</th><th>Zins p. a.</th><th>Zinsen für {eur(DEF_B)} €</th></tr></thead><tbody>{rows}</tbody></table></div>
  {'<p class="note"><b>Hinweis zur Quelle:</b> Einzelne Angaben zu diesem Angebot stammen aus Vergleichsportalen, weil die Bank sie nicht frei abrufbar veröffentlicht. Bitte vor dem Abschluss beim Anbieter prüfen.</p>' if a.get('sek') else ''}
  <p class="note">Zinsen vor Steuern{", mit Zinseszins bei mehr als 12 Monaten" if a.get("zinseszins") is True else ""}. Quelle: {K.ext(a["quelle"])}, Stand {dmy(a.get("stand") or gp)}.</p>
  <h2>Vorteile und Nachteile</h2>
  <div class="pc"><div class="box pro"><h3>Das spricht dafür</h3>{'<ul class="checks">'+"".join(f"<li>{E(x)}</li>" for x in pc)+'</ul>' if pc else '<p class="note">Keine besonderen Vorteile.</p>'}</div>
  <div class="box con"><h3>Das spricht dagegen</h3>{'<ul class="checks neg">'+"".join(f"<li>{E(x)}</li>" for x in kc)+'</ul>' if kc else '<p class="note">Keine bekannten Nachteile.</p>'}</div></div>
  <h2>Konditionen im Überblick</h2>{cond}
  {f"<h2>Andere Angebote für {lzt(m0)}</h2><div class='tbl wide'><table><thead><tr><th>Angebot</th><th>Zins p. a.</th><th>Einlagensicherung</th></tr></thead><tbody>{simt}</tbody></table></div><p class='note'><a class='lnk' href='../'>Alle Angebote im Festgeld-Vergleich →</a></p>" if simt else ""}
  <h2>Fragen und Antworten</h2>{faqhtml(fq)}
  <p class="src" style="margin-top:18px">Quelle: {K.ext(a["quelle"])}{" · "+K.ext(a["quelle2"]) if a.get("quelle2") else ""}. Konditionen vor dem Abschluss beim Anbieter prüfen.</p>
</main>
{K.footer(P)}'''
    K.write(rel,head(t,d,rel,P,ld)+body)

# ---------- Methodik ----------
def methodik_page(xs):
    rel=f'{LAND}/festgeld/methodik/'; P='../../../'; N=CC['N']
    t=f'So vergleichen wir Festgeld in {N} | Finvallo'
    d='Wie der Festgeld-Vergleich rechnet und sortiert: Zins für Betrag und Laufzeit, Zinseszins, Einlagensicherung, Länderrating, Steuer und Datenquellen.'
    ld=K.graph(rel,t,d,[(N,f'{LAND}/'),('Festgeld',f'{LAND}/festgeld/'),('So vergleichen wir',rel)],date=max(a['geprueft'] for a in xs))
    ls=sorted({a['sitz'] for a in xs},key=lambda c:(-(RAT.get((LAENDER.get(c) or {}).get('rating_sp') or '',0)),c))
    lrows=''.join(f'<tr><td>{E((LAENDER.get(c) or {}).get("name") or c)}</td><td>{E((LAENDER.get(c) or {}).get("sicherung") or "")}</td><td>{E({"NR":"kein Rating","":"keine Angabe"}.get((LAENDER.get(c) or {}).get("rating_sp") or "",(LAENDER.get(c) or {}).get("rating_sp")))}</td><td>{sum(1 for a in xs if a["sitz"]==c)}</td></tr>' for c in ls)
    body=f'''{hdr(P,rel)}
<div class="wrap"><main id="app">
<div class="crumb"><span><a href="../">Festgeld</a> › So vergleichen wir</span><span>Stand {S(xs)}</span></div>
<h1>So vergleichen wir Festgeld</h1>
<p class="lede">Beim Festgeld zählt vor allem eins: wie viel Zinsen du für deinen Betrag und deine Laufzeit bekommst. Deshalb vergeben wir keine Sterne, sondern sortieren nach Zins. Alles, was für die Sicherheit wichtig ist, zeigen wir offen daneben.</p>
<h2>Reihenfolge</h2><div class="prose"><p>Standard ist der höchste Zins für den gewählten Betrag (anfangs {eur(DEF_B)} €) und die gewählte Laufzeit (anfangs {lzt(DEF_M)}). Bei gleichem Zins steht das Angebot mit dem besseren Länderrating vorn. Angebote, die zu deinem Betrag nicht passen (Mindest- oder Höchstanlage), stehen am Ende. Du kannst auch nach Länderrating oder Name sortieren.</p></div>
<h2>So rechnen wir die Zinsen</h2><div class="prose"><p>Bis 12 Monate: Betrag × Zins × Monate / 12. Bei mehr als 12 Monaten rechnen wir mit Zinseszins (Betrag × ((1 + Zins)<sup>Jahre</sup> − 1)), wenn die Bank die jährlichen Zinsen mitverzinst; sonst ohne. Alle Beträge sind vor Steuern. Hängt der Zins vom Betrag ab, nehmen wir die Stufe, in die dein Betrag fällt. Banken rechnen tagesgenau, deshalb kann der Betrag um ein paar Cent abweichen.</p></div>
<h2>Einlagensicherung und Länderrating</h2><div class="prose"><p>{E(CC["sich"])} Als Hinweis auf die Finanzkraft zeigen wir das langfristige Länderrating von S&amp;P Global für das Land, dessen Einlagensicherung zuständig ist. Die Ratings haben wir am {dmy(max((v.get("rating_stand") or "2026-01-01") for v in LAENDER.values()))} über tradingeconomics.com abgeglichen; S&amp;P veröffentlicht sie nicht frei abrufbar. Hat S&amp;P ein Land nicht (mehr) bewertet, steht „kein Rating“.</p></div>
<div class="tbl wide"><table><thead><tr><th>Land</th><th>Einlagensicherung</th><th>Rating (S&amp;P)</th><th>Angebote</th></tr></thead><tbody>{lrows}</tbody></table></div>
<h2>Steuern</h2><div class="prose"><p>{E(CC["steuer"])}</p></div>
<h2>Woher die Daten kommen</h2><div class="prose"><p>Jede Zahl stammt von der Konditionsseite, dem Preisaushang oder dem Informationsbogen der Bank oder von der Produktseite der Plattform, über die du abschließt. Bei jedem Angebot stehen Quelle und Prüfdatum. Zinsen ändern sich oft; prüfe die Konditionen vor dem Abschluss beim Anbieter. Die Daten gibt es offen als <a class="lnk" href="../../daten/festgeld.json">JSON</a> und <a class="lnk" href="../../daten/festgeld.csv">CSV</a>.</p></div>
<h2>Wer nicht im Vergleich ist</h2><div class="prose"><p>Regionale Banken, die nur Kundschaft aus ihrer Region nehmen, Angebote ohne gesetzliche Einlagensicherung in der EU und Produkte mit schwankendem Zins (etwa Zuwachssparen) nehmen wir nicht auf.</p></div>
<p><a class="lnk" href="../">← Zum Festgeld-Vergleich</a></p>
</main>
{K.footer(P)}'''
    K.write(rel,head(t,d,rel,P,ld)+body)

def export(xs,d):
    os.makedirs(R+f'{LAND}/daten',exist_ok=True)
    keys=['slug','bank','institut','produkt','vertrieb','vertrieb_url','sitz','einlagensicherung','zinsen','min_anlage','max_anlage','zinszahlung','zinseszins','steuer_auto','kuendigung','verlaengerung','konto_noetig','neukunden_only','eroeffnung','aktion','quelle','stand','geprueft']
    out={'quelle':f'https://finvallo.com/{LAND}/festgeld/','stand':d['stand'],'anzahl':len(xs),'lizenz':'Frei nutzbar mit Quellenangabe Finvallo','angebote':[{k:a.get(k) for k in keys}|{'rating_sp':rating(a)} for a in xs]}
    open(R+f'{LAND}/daten/festgeld.json','w').write(json.dumps(out,ensure_ascii=False,indent=1))
    src=os.path.join(SP,'daten',LAND,'festgeld.csv')
    if os.path.exists(src): open(R+f'{LAND}/daten/festgeld.csv','w').write(open(src,encoding='utf-8').read())

def llms(xs,d):
    N=CC['N']; st=dmy(d['stand'])
    for fn in ('llms.txt','llms-full.txt'):
        p=R+fn
        if not os.path.exists(p): continue
        t=open(p,encoding='utf-8').read()
        t=re.sub(r'\n## '+N+r': Festgeld\n(?:- [^\n]*\n?)*','\n',t)
        b=f'\n## {N}: Festgeld\n- [Festgeld-Vergleich {N}](https://finvallo.com/{LAND}/festgeld/): {len(xs)} Angebote, Zinsen nach Betrag und Laufzeit, Einlagensicherung und Länderrating, Stand {st}\n'
        b+=''.join(f'- [Festgeld {t_}](https://finvallo.com/{LAND}/festgeld/{s}/)\n' for m,s,t_ in LZ if m in LZ_SEITEN)
        b+=f'- [Festgeld bei {CC["heimB"]}](https://finvallo.com/{LAND}/festgeld/{CC["bl_slug"]}/)\n- [So vergleichen wir Festgeld](https://finvallo.com/{LAND}/festgeld/methodik/)\n- [Daten als JSON](https://finvallo.com/{LAND}/daten/festgeld.json)\n'
        top=[a for a in ordnen(xs,DEF_M) if ertrag(a,DEF_B,DEF_M)['fit']][:5 if fn=='llms.txt' else 30]
        b+=''.join(f'- [{titel(a)}](https://finvallo.com/{LAND}/festgeld/{a["slug"]}/): {pct(ertrag(a,DEF_B,DEF_M)["zins"])} für {lzt(DEF_M)}, {vtT(a)}, Einlagensicherung {landN(a)}\n' for a in top)
        i=t.find('\n## Zitieren'); t=t.rstrip()+'\n'+b
        open(p,'w',encoding='utf-8').write(re.sub(r'\n{3,}','\n\n',t))

LZ_DA=set(); LZ_SEITEN=set()
def build_land():
    global LZ_DA,LZ_SEITEN
    K.use(LAND)
    d,xs=load()
    K.L.setdefault('stand',d['stand'])
    for a in xs: a.setdefault('geprueft',d['stand'])
    cnt={}
    for a in xs:
        for m in laufzeiten(a): cnt[m]=cnt.get(m,0)+1
    LZ_DA=set(cnt)
    LZ_SEITEN={m for m,_,_ in LZ if cnt.get(m,0)>=MIN_LZ_SEITE}
    for a in xs: offer_page(a,xs)
    list_page(xs,d)
    for m,s,_ in LZ:
        if m in LZ_SEITEN: list_page(xs,d,m,lzslug=s)
    list_page(xs,d,sub=(CC['bl_slug'],f'Festgeld bei {CC["heimB"]}',heim,
        f'Festgeld-Angebote, bei denen die {CC["heim"]} Einlagensicherung greift. Dafür verzichtest du oft auf ein paar Zehntel Prozent Zinsen gegenüber Banken aus anderen EU-Ländern. Bei {CC["heimB"]} wird die {CC["steuer_kurz"]} in der Regel automatisch abgeführt.'))
    methodik_page(xs); export(xs,d); llms(xs,d)
    print(f'Festgeld {LAND}:',len(xs),'Angebote,',len(LZ_SEITEN),'Laufzeit-Seiten')

def slugs(l):
    d,xs=load(l); cnt={}
    for a in xs:
        for m in laufzeiten(a): cnt[m]=cnt.get(m,0)+1
    return {a['slug'] for a in xs}|{s for m,s,_ in LZ if cnt.get(m,0)>=MIN_LZ_SEITE}|{'methodik',CFG[l]['bl_slug']}
def main():
    global LAND,CC
    if os.path.exists(LP): LAENDER.update(json.load(open(LP,encoding='utf-8')))
    for l in CFG:
        if os.path.exists(dpath(l)): OTHER[l]=slugs(l)
    for l in CFG:
        if l not in OTHER: continue
        LAND,CC=l,CFG[l]; build_land()
    LAND,CC='de',CFG['de']

if __name__=='__main__': main()
