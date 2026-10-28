# Festgeld-Vergleich Deutschland und Österreich: Liste mit Rechner und Filtern, Laufzeit-Seiten, Bestenlisten, Bankseiten, Angebotsseiten, Methodik.
# Daten: daten/<land>/festgeld.json (aus festgeld_daten.py, jede Zahl aus der Konditionsseite der Bank oder Plattform, mit Quelle und Prüfdatum),
# daten/festgeld-laender.json (Einlagensicherung und S&P-Länderrating je Sitzland).
# Rechnung gibt es zweimal: ertrag() hier und calc() in public/assets/festgeld.js. check.py vergleicht beide (tools/festgeld-kontrolle.js).
# Läuft nach girokonto.py, vor header.py. Schreibt daten/hreflang-festgeld.json (AT/DE-Paare derselben Bank) für eeat.py.
import hashlib,json,math,os,re,sys,datetime
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import karten as K
import affiliate
from score import eur,pct

E=K.E; dmy=K.dmy; R=K.R; SP=K.SP
LAND='de'
def dpath(land): return os.path.join(SP,'daten',land,'festgeld.json')
LP=os.path.join(SP,'daten','festgeld-laender.json')
HP=os.path.join(SP,'daten','hreflang-festgeld.json')
TODAY=datetime.date.today().isoformat()
CFG={'de':dict(N='Deutschland',code='DE',heim='deutsche',heimF='Deutsche Einlagensicherung',heimB='deutschen Banken',bl_slug='deutsche-banken',steuer_rechner='Abgeltungsteuer-Rechner',
        steuer='Zinsen sind in Deutschland Kapitalerträge. Deutsche Banken ziehen die Abgeltungsteuer (25 % plus Solidaritätszuschlag und gegebenenfalls Kirchensteuer) automatisch ab, soweit kein Freistellungsauftrag vorliegt. Bis 1.000 € Kapitalerträge im Jahr (2.000 € für Paare) bleiben mit Freistellungsauftrag steuerfrei. Bei Banken im Ausland musst du die Zinsen oft selbst in der Anlage KAP angeben, außer die Plattform führt die Steuer für dich ab.',
        sich='In Deutschland sichert die Entschädigungseinrichtung deutscher Banken (EdB) Einlagen bis 100.000 € pro Person und Bank. Viele private Banken sind zusätzlich im Einlagensicherungsfonds des Bankenverbands. Alle EU-Länder sichern Einlagen nach denselben Regeln bis 100.000 €; wie belastbar die Sicherung im Ernstfall ist, hängt aber auch von der Finanzkraft des Landes ab.',
        steuer_kurz='Abgeltungsteuer',anb={'HypoVereinsbank':'hypovereinsbank','HVB':'hypovereinsbank'}),
     'at':dict(N='Österreich',code='AT',heim='österreichische',heimF='Österreichische Einlagensicherung',heimB='österreichischen Banken',bl_slug='oesterreichische-banken',steuer_rechner='KESt-Rechner',
        steuer='Zinsen aus Spareinlagen kosten in Österreich 25 % Kapitalertragsteuer (KESt). Österreichische Banken behalten sie automatisch ein, damit ist die Steuer erledigt (Endbesteuerung). Bei Banken im Ausland wird die KESt meist nicht abgezogen: Dann musst du die Zinsen selbst in der Steuererklärung (E 1kv) angeben, außer die Plattform führt die Steuer für dich ab.',
        sich='In Österreich sichert die Einlagensicherung AUSTRIA (ESA) bzw. die Sparkassen-Haftungsgesellschaft Einlagen bis 100.000 € pro Person und Bank. Alle EU-Länder sichern Einlagen nach denselben Regeln bis 100.000 €; wie belastbar die Sicherung im Ernstfall ist, hängt aber auch von der Finanzkraft des Landes ab.',
        steuer_kurz='KESt',anb={'Erste Bank':'erste'})}
CC=CFG['de']; OTHER={}
# Laufzeiten mit eigener Seite: (Monate, Slug, Text)
LZ=[(1,'1-monat','1 Monat'),(3,'3-monate','3 Monate'),(6,'6-monate','6 Monate'),(9,'9-monate','9 Monate'),(12,'1-jahr','1 Jahr'),(18,'18-monate','18 Monate'),
    (24,'2-jahre','2 Jahre'),(36,'3-jahre','3 Jahre'),(48,'4-jahre','4 Jahre'),(60,'5-jahre','5 Jahre'),(72,'6-jahre','6 Jahre'),(84,'7-jahre','7 Jahre'),(96,'8-jahre','8 Jahre'),(120,'10-jahre','10 Jahre')]
LZT={m:t for m,_,t in LZ}
# Dativ für „mit … Laufzeit“ und „nach …“
def lzd(m):
    t=lzt(m)
    return re.sub(r'(\d+) Jahre$',r'\1 Jahren',t).replace('1 Jahr','1 Jahr').replace(' Monate',' Monaten').replace('1 Monat','1 Monat')
DEF_B=10000; DEF_M=12; MIN_LZ_SEITE=5; IM_HTML=60   # Einträge, die sofort im DOM stehen; der Rest in <template>
RAT={'AAA':22,'AA+':21,'AA':20,'AA-':19,'A+':18,'A':17,'A-':16,'BBB+':15,'BBB':14,'BBB-':13,'BB+':12,'BB':11,'BB-':10,'B+':9,'B':8,'B-':7}
ZZT={'jaehrlich':'jährlich','endfaellig':'am Ende der Laufzeit','monatlich':'monatlich','quartalsweise':'vierteljährlich','halbjaehrlich':'halbjährlich','wahlweise':'nach Wahl'}
LAENDER={}; GIRO={}; LZ_DA=set(); LZ_SEITEN=set(); PAIRS=[]

def lzt(m):
    if m in LZT: return LZT[m]
    if m<1: return f'{round(m*4)} Wochen' if m!=0.25 else '1 Woche'
    if m%12==0: return f'{m//12} Jahre'
    return f'{eur(m)} Monate'
def load(land=None):
    d=json.load(open(dpath(land or LAND),encoding='utf-8')); xs=d['angebote']
    for a in xs:
        a['slug']=a['id']; a.setdefault('bank_key',K.slug(a['bank'])); a.setdefault('bank_slug',a['bank_key'])
        # befristete Aktionen: „bis 30.10.2026“ im Text; abgelaufene fallen beim Bauen weg
        m=re.search(r'bis(?: einschließlich| zum)?\s+(\d{1,2})\.(\d{1,2})\.(\d{4})',a.get('aktion') or '')
        if m and f'{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}'<TODAY: a['aktion']=None
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
    return dict(fit=True,zins=best['zins'],ertrag=math.floor(e*100+0.5+1e-6)/100)  # kaufmännisch gerundet, wie festgeld.js
def jsdata(a):
    return {'z':[[z['monate'],z['zins'],z['min'],z['max']] for z in a['zinsen']],'amin':a.get('min_anlage'),'amax':a.get('max_anlage'),'ze':a.get('zinseszins')}
def lzslug_of(m):
    s=next((s for x,s,_ in LZ if x==m and x in LZ_SEITEN),None)
    return f'{s}/' if s else f'?laufzeit={m}'
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
ZM={'zinsmarkt-deutsche-bank':'Deutschen Bank','zinsmarkt-norisbank':'norisbank'}
def plattN(a):
    """Name des Vertriebswegs: Raisin, CHECK24, ZinsMarkt der Deutschen Bank, PickTheBank"""
    zm=next((v for k,v in ZM.items() if a['id'].endswith(k)),None)
    if zm: return f'ZinsMarkt der {zm}'
    v=a['vertrieb'].replace('andere: ','')
    return {'Check24':'CHECK24'}.get(v,v)
def vtT(a): return 'direkt bei der Bank' if not plattform(a) else f'über {plattN(a)}'
def vtK(a): return 'direkt' if not plattform(a) else plattN(a)
def vtS(a): return vtK(a).replace('ZinsMarkt der Deutschen Bank','ZinsMarkt Deutsche Bank')
def zzT(a): return ZZT.get(a.get('zinszahlung'),'keine Angabe')
def kdT(a): return {'nein':'nicht möglich','ja':'möglich','ja_mit_abschlag':'möglich, mit Abschlag'}.get(a.get('kuendigung'),'keine Angabe')
def vlT(a): return {'automatisch':'verlängert sich automatisch','keine':'Geld wird ausgezahlt','wahlweise':'Verlängerung wählbar'}.get(a.get('verlaengerung'),'keine Angabe')
def anlT(a):
    lo,hi=a.get('min_anlage'),a.get('max_anlage')
    if lo is None and hi is None: return None
    t=f'ab {eur(lo)} €' if lo is not None else 'ohne Mindestbetrag'
    return t+(f' bis {eur(hi)} €' if hi is not None else '')
def sichT(a):
    l=land(a); s=a.get('einlagensicherung') or {}
    w=s.get('waehrung')
    bt=f'{eur(s["betrag"])} {w}' if w and s.get('betrag') else f'{eur(s.get("betrag") or l.get("betrag") or 100000)} €'
    return (s.get('system') or l.get('sicherung') or f'gesetzliche Einlagensicherung {landN(a)}')+f', bis {bt} pro Person'
def steuerT(a):
    if a.get('steuer_auto') is True: return f'{CC["steuer_kurz"]} wird automatisch abgeführt'
    if a.get('steuer_auto') is False: return 'Zinsen selbst in der Steuererklärung angeben'
    return 'keine Angabe'
def neugeld(a): return a['id'].endswith('-neugeld')
def titel(a): return (a['bank'] if a['produkt'].lower() in a['bank'].lower() else f'{a["bank"]} {a["produkt"]}')+(' (Neugeld-Angebot)' if neugeld(a) else '')
def lzspan(a):
    l=laufzeiten(a)
    return lzt(l[0]) if len(l)==1 else f'{lzt(l[0])} bis {lzt(l[-1])}'
def geschwister(a,xs): return [x for x in xs if x['bank_key']==a['bank_key'] and x is not a]
def giro_links(a):
    """Girokonten derselben Bank im Girokonto-Vergleich: [(slug,name)]"""
    b=a['bank'].lower()
    return [(k['slug'],k['name']) for k in GIRO.get(LAND,[]) if k['bank'].lower()==b or k['bank'].lower().startswith(b+' ') or b.startswith(k['bank'].lower()+' ')]
def anb_rel(a):
    sl=CC['anb'].get(a['bank']) or K.slug(a['bank'])
    return f'{LAND}/kreditkarten/anbieter/{sl}/' if os.path.exists(R+f'{LAND}/kreditkarten/anbieter/{sl}/index.html') else None

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
    if a.get('verlaengerung')=='keine': p.append('Auszahlung am Laufzeitende, ohne automatische Verlängerung')
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
    if plattform(a): t+=f'<span class="tag typ">über {E(plattN(a))}</span>'
    return t
def btn(a,P=''):
    """Partnerlink nur bei Direktangeboten der Bank; über Raisin oder CHECK24 bleibt der Plattformlink"""
    key=a['bank_slug'] if not plattform(a) else None
    return affiliate.btn(LAND,'festgeld',key,a.get('vertrieb_url') or a['quelle'])
def bank_btn(ys):
    """Button auf der Bankseite: direkt zur Bank (Partnerlink, wenn vorhanden); nur wenn es ein Direktangebot gibt"""
    d=[y for y in ys if not plattform(y)]; a=(d or ys)[0]
    if not d and not affiliate.link(LAND,'festgeld',a['bank_slug']): return ''
    return '<p style="margin-top:14px">'+affiliate.btn(LAND,'festgeld',a['bank_slug'],a.get('vertrieb_url') or a['quelle'],text=f'Festgeld direkt bei {a["bank"]} eröffnen',cls='btn primary')+'</p>'
def item(a,P,base,m,rank,hide=False):
    r=ertrag(a,DEF_B,m)
    zt=f'{pct(r["zins"])}' if r.get('zins') is not None else '–'
    et=f'{eur(r["ertrag"])} €' if r['fit'] else 'passt nicht'
    ak=a.get('aktion') or ''
    if len(ak)>140: ak=ak[:140].rsplit(' ',1)[0].rstrip(' .,;:!')+' …'
    akt=f'<div class="earn"><span>Aktion</span><b>{E(ak)}</b></div>' if ak else ''
    rk=f'<span class="rank{" r"+str(rank) if rank<=3 else ""}">{rank}</span>' if rank else ''
    return f'''<article class="item" id="fg-{a["slug"]}" data-k='{E(json.dumps(jsdata(a),separators=(",",":")))}' data-f="{flags(a)}" data-sitz="{a["sitz"]}" data-rat="{ratnum(a)}" data-zz="{a.get("zinszahlung") or ""}" data-q="{E((a["bank"]+" "+a["produkt"]+" "+vtK(a)).lower())}"{" hidden" if hide else ""}>
    <div class="ihead"><div style="display:flex;gap:10px;align-items:center">{rk}</div></div>
    <div class="irow">{face(a)}<div style="min-width:0"><h3 class="iname"><a href="{base}{a["slug"]}/">{E(titel(a))}</a></h3><div class="iprov">{E(landN(a))} · {E(vtT(a))}</div></div></div>
    <div class="tags">{tags(a)}</div>
    <div class="stats"><div><small>Zins p. a.</small><b class="good" data-zins>{zt}</b></div><div><small data-lbl>Zinsen für {eur(DEF_B)} €</small><b data-ertrag>{et}</b></div><div><small>Mindestanlage</small><b>{eur(a["min_anlage"])+" €" if a.get("min_anlage") is not None else "keine"}</b></div></div>
    <p class="note" data-why style="margin:0"></p>
    {akt}
    <ul class="checks">{"".join(f"<li>{E(x)}</li>" for x in pros(a)[:3])}</ul>
    <div class="acts">{btn(a)}<a class="btn ghost block" href="{base}{a["slug"]}/">Details ansehen</a></div>
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
    <label class="fq"><span class="sr">Suche</span><input type="search" data-q placeholder="Bank oder Plattform suchen" autocomplete="off"></label>
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
    sl=rest[len('festgeld/'):].strip('/')
    other=f'{o}/{rest}' if (not sl or sl in OTHER.get(o,set())) and OTHER.get(o) else (f'{o}/festgeld/' if OTHER.get(o) else f'{o}/')
    return K.HDR(P,rel,other)
def head(t,d,rel,P,ld): return K.head(t,d,rel,P,ld)
def faqhtml(fq): return '<div class="faq">'+''.join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q,a in fq)+'</div>'
def faqld(fq): return {"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in fq]}
def S(xs): return dmy(max(a['geprueft'] for a in xs))
def nbanken(xs): return len({a['bank_key'] for a in xs})
def steuerlink(P): return f'<a class="lnk" href="{P}{LAND}/rechner/kapitalertragsteuer/">{CC["steuer_rechner"]}</a>'
def zinslink(P): return f'<a class="lnk" href="{P}{LAND}/rechner/zinseszins/">Zinseszinsrechner</a>'
def rg_links(P):
    """Festgeld-Ratgeber, sobald es sie gibt"""
    rg=[('festgeld-oder-tagesgeld','Festgeld oder Tagesgeld?'),('einlagensicherung','Einlagensicherung erklärt'),('zinstreppe','Zinstreppe'),('festgeld-kuendigen','Vorzeitig kündigen'),('festgeld-plattformen','Raisin, CHECK24 und Co.'),('festgeld-steuern','Steuern auf Zinsen')]
    xs=[(s,t) for s,t in rg if os.path.exists(R+f'{LAND}/ratgeber/{s}/index.html')]
    return ' · '.join(f'<a class="lnk" href="{P}{LAND}/ratgeber/{s}/">{t}</a>' for s,t in xs)

# ---------- Bestenlisten ----------
FCATS=[
 dict(k='kuendbar',t='Vorzeitig kündbar',h='Festgeld, das du vorzeitig kündigen kannst',d='Angebote, bei denen du vor dem Laufzeitende an dein Geld kommst, meist mit Zinsabschlag. Wie die Bank den Abschlag rechnet, steht auf der Angebotsseite.',f=lambda a:a.get('kuendigung') in ('ja','ja_mit_abschlag')),
 dict(k='ab-1000-euro',t='Ab 1.000 €',h='Festgeld ab 1.000 € Anlage',d='Angebote mit einer Mindestanlage von höchstens 1.000 €, für alle, die mit kleineren Beträgen anfangen wollen.',f=lambda a:a.get('min_anlage') is not None and a['min_anlage']<=1000),
 dict(k='steuer-automatisch',t='Steuer automatisch',h=None,d=None,f=lambda a:a.get('steuer_auto') is True),
 dict(k='direkt',t='Direkt bei der Bank',h='Festgeld direkt bei der Bank',d='Angebote, die du ohne Plattform direkt bei der Bank abschließt. Du brauchst nur ein Konto bei dieser Bank, oft ein kostenloses Tagesgeld- oder Verrechnungskonto.',f=lambda a:not plattform(a)),
 dict(k='raisin',t='Über Raisin',h='Festgeld über Raisin (WeltSparen)',d='Alle Angebote, die du über die Plattform Raisin abschließt: eine Anmeldung, ein Verrechnungskonto, viele Banken aus der EU. Steuer und Einlagensicherung hängen von der jeweiligen Bank ab.',f=lambda a:a['vertrieb']=='Raisin'),
 dict(k='check24',t='Über CHECK24',h='Festgeld über CHECK24',d='Alle Angebote, die über das CHECK24-Anlagekonto bei der C24 Bank laufen. Die Einlagen liegen bei der jeweiligen Partnerbank.',f=lambda a:a['vertrieb']=='Check24'),
 dict(k='neugeld',t='Aktionen',h='Festgeld mit Aktion oder Neugeld-Bonus',d='Angebote mit befristeter Aktion, Bonus oder Zinsaufschlag für neues Geld. Aktionen enden oft nach wenigen Wochen; prüfe das Datum beim Anbieter.',f=lambda a:bool(a.get('aktion')) or neugeld(a)),
]
def fcats():
    cs=[]
    for c in FCATS:
        c=dict(c)
        if c['k']=='steuer-automatisch': c['h']=f'Festgeld mit automatischer {CC["steuer_kurz"]}'; c['d']=f'Angebote, bei denen die {CC["steuer_kurz"]} automatisch abgeführt wird. Du musst die Zinsen nicht selbst in der Steuererklärung angeben.'
        cs.append(c)
    cs.insert(0,dict(k=CC['bl_slug'],t=CC['heimF'],h=f'Festgeld bei {CC["heimB"]}',d=f'Angebote, bei denen die {CC["heim"]} Einlagensicherung greift. Dafür verzichtest du oft auf ein paar Zehntel Prozent Zinsen gegenüber Banken aus anderen EU-Ländern.',f=heim))
    return cs

# ---------- Listen ----------
def kennzahlen(xs,m):
    ok=[a for a in xs if ertrag(a,DEF_B,m)['fit']]
    if not ok: return None
    best=ordnen(ok,m)[0]; hb=[a for a in ok if heim(a)]
    bh=ordnen(hb,m)[0] if hb else None
    zs=sorted(ertrag(a,DEF_B,m)['zins'] for a in ok)
    return dict(best=best,bz=ertrag(best,DEF_B,m)['zins'],bh=bh,bhz=ertrag(bh,DEF_B,m)['zins'] if bh else None,med=zs[len(zs)//2],n=len(ok))
def gen_fq(xs,m,art,name=''):
    """art: 'alle' (Gesamtvergleich), 'lz' (Laufzeit-Seite), 'sub' (Bestenliste)"""
    N=CC['N']; kz=kennzahlen(xs,m); fq=[]
    wo={'alle':'Im Gesamtvergleich','lz':f'Unter den Angeboten mit {lzd(m)} Laufzeit','sub':f'In der Liste „{name}“'}[art]
    if kz:
        fq.append((f'Wo gibt es aktuell die höchsten Festgeldzinsen für {lzt(m)}?',f'{wo} zahlt laut unserer Auswertung {titel(kz["best"])} mit {pct(kz["bz"])} pro Jahr ({vtT(kz["best"])}, Einlagensicherung {landN(kz["best"])}).'+(f' Bei {CC["heimB"]} liegt {titel(kz["bh"])} mit {pct(kz["bhz"])} vorn.' if kz['bh'] and kz['bh'] is not kz['best'] else '')+f' Stand: {S(xs)}.'))
    if art=='lz' and kz:
        k12=kennzahlen(xs,DEF_M) if m!=DEF_M else None
        fq.append((f'Lohnt sich Festgeld mit {lzd(m)} Laufzeit?',f'Von den {kz["n"]} passenden Angeboten mit {lzd(m)} Laufzeit zahlt die Hälfte mindestens {pct(kz["med"])} pro Jahr'+(f', bei 1 Jahr Laufzeit sind es {pct(k12["med"])}' if k12 else '')+'. '+('Längere Bindung bringt hier also mehr Zins.' if k12 and kz['med']>k12['med'] else 'Längere Bindung bringt hier also nicht mehr Zins.' if k12 and kz['med']<k12['med'] else '')+' Binde nur Geld, das du in dieser Zeit sicher nicht brauchst.'))
        fq.append((f'Wann bekomme ich bei {lzt(m)} Laufzeit die Zinsen?',f'Das hängt vom Angebot ab: {sum(1 for a in xs if a.get("zinszahlung")=="jaehrlich")} der {len(xs)} Angebote zahlen jährlich, {sum(1 for a in xs if a.get("zinszahlung")=="endfaellig")} erst am Ende der Laufzeit. '+('Bei Laufzeiten über einem Jahr zählt, ob die Bank jährliche Zinsen mitverzinst (Zinseszins); das steht bei jedem Angebot.' if m>12 else 'Bei Laufzeiten bis zu einem Jahr macht das für den Ertrag keinen Unterschied.')))
        fq.append((f'Was passiert nach {lzd(m)}?',f'{sum(1 for a in xs if a.get("verlaengerung")=="keine")} Angebote zahlen das Geld samt Zinsen auf dein Referenzkonto aus, {sum(1 for a in xs if a.get("verlaengerung")=="automatisch")} verlängern sich automatisch, wenn du nicht rechtzeitig kündigst. Prüfe das vor dem Abschluss, damit dein Geld nicht ungewollt weitere {lzt(m)} gebunden ist.'))
        return fq
    if art=='sub' and kz:
        fq.append(('Wie viele Angebote gibt es in dieser Liste?',f'{len(xs)} Angebote, davon passen {kz["n"]} zu {eur(DEF_B)} € und {lzt(m)} Laufzeit. Mit dem Rechner oben siehst du die Zinsen für deinen eigenen Betrag und andere Laufzeiten.'))
        return fq
    fq+=[('Wie sicher ist Festgeld?',CC['sich']),
         ('Wie werden Festgeld-Zinsen versteuert?',CC['steuer']),
         ('Kann ich Festgeld vorzeitig kündigen?','Meist nicht: Das Geld ist bis zum Ende der Laufzeit fest angelegt. Manche Banken erlauben eine vorzeitige Auflösung, dann meist mit Zinsabschlag. Ob das geht, steht bei jedem Angebot. Geld, das du kurzfristig brauchen könntest, liegt besser auf einem Tagesgeldkonto.'),
         ('Was ist der Unterschied zwischen Festgeld und Tagesgeld?','Beim Festgeld legst du Geld für eine feste Zeit zu einem festen Zins an. Beim Tagesgeld kommst du jeden Tag an dein Geld, dafür kann die Bank den Zins jederzeit ändern.'),
         ('Spielen Provisionen eine Rolle?','Nein. Wir sortieren nach Zins für deinen Betrag und deine Laufzeit. Provisionen haben keinen Einfluss auf die Reihenfolge, und es gibt keine bezahlten Platzierungen.')]
    return fq
def zinskurve(xs,P,cur=None):
    """Tabelle: bester Zins und Median je Laufzeit, mit Links auf die Laufzeit-Seiten"""
    rows=''
    for m,s,t in LZ:
        if m not in LZ_SEITEN: continue
        kz=kennzahlen([a for a in xs if m in laufzeiten(a)],m)
        if not kz: continue
        lnk=f'<b>{t}</b>' if m==cur else f'<a class="lnk" href="{P}{LAND}/festgeld/{s}/">{t}</a>'
        rows+=f'<tr><td>{lnk}</td><td><b>{pct(kz["bz"])}</b><br><small class="mut">{E(titel(kz["best"]))}</small></td><td>{pct(kz["med"])}</td><td>{kz["n"]}</td></tr>'
    return f'<div class="tbl wide"><table><thead><tr><th>Laufzeit</th><th>Höchster Zins</th><th>Hälfte zahlt mindestens</th><th>Angebote</th></tr></thead><tbody>{rows}</tbody></table></div><p class="note">Für {eur(DEF_B)} € Anlage, Stand {S(xs)}. Mit deinem Betrag rechnest du in der Liste.</p>'
def liste_html(X,P,base,m):
    """Angebote als <article>; die ersten IM_HTML sichtbar im DOM, der Rest in <template>, das festgeld.js beim Start einhängt"""
    rank=0; vis_html=''; rest=''; n=0
    for a in X:
        vis=m in laufzeiten(a); fit=vis and ertrag(a,DEF_B,m)['fit']
        if fit: rank+=1
        h=item(a,P,base,m,rank if fit else 0,hide=not vis)
        n+=1
        if n<=IM_HTML: vis_html+=h
        else: rest+=h
    return vis_html+(f'<template data-rest>{rest}</template>' if rest else '')
def list_page(xs,d,m=DEF_M,lzslug=None,sub=None):
    """Gesamtvergleich (alle Angebote), Laufzeit-Seite (lzslug) oder Bestenliste (sub = Eintrag aus fcats())."""
    N=CC['N']; base='' if not (lzslug or sub) else '../' if lzslug else '../../'
    if lzslug:
        rel=f'{LAND}/festgeld/{lzslug}/'; P='../../../'
        X=[a for a in xs if m in laufzeiten(a)]
        h1=f'Festgeld {lzt(m)}: Zinsen im Vergleich'
    elif sub:
        rel=f'{LAND}/festgeld/bestenlisten/{sub["k"]}/'; P='../../../../'
        X=[a for a in xs if sub['f'](a)]
        h1=sub['h']
    else:
        rel=f'{LAND}/festgeld/'; P='../../'; X=xs; h1=f'Festgeld-Vergleich {N}'
    X=ordnen(X,m); kz=kennzahlen(X,m); n=len(X); nb=nbanken(X); st=S(xs)
    shown=[a for a in X if m in laufzeiten(a)]
    if lzslug:
        t=f'Festgeld {lzt(m)} {N}: Zinsen von {nb} Banken | Finvallo'
        ds=f'Festgeld mit {lzd(m)} Laufzeit in {N}: {n} Angebote von {nb} Banken.'+(f' Bis {pct(kz["bz"])} Zinsen pro Jahr, Stand {st}.' if kz else '')+' Mit Zinsrechner, Einlagensicherung und Länderrating.'
    elif sub:
        t=f'{sub["h"]} ({CC["code"]}) 2026 | Finvallo'
        if len(t)>62: t=f'Festgeld {sub["t"]} {N} 2026 | Finvallo'
        ds=f'{sub["h"]} in {N}: {n} Angebote von {nb} Banken'+(f', bis {pct(kz["bz"])} Zinsen für {lzt(m)}' if kz else '')+f'. Mit Zinsrechner, Stand {st}.'
    else:
        t=f'Festgeld-Vergleich {N} 2026: {n} Angebote | Finvallo'
        ds=f'{n} Festgeld-Angebote von {nb} Banken für {N} verglichen: Zinsen nach Laufzeit und Betrag, Einlagensicherung, Länderrating, Zinszahlung und Steuer.'
    ds=K.fit_desc(ds) if hasattr(K,'fit_desc') else ds[:155]
    fq=gen_fq(X,m,'lz' if lzslug else 'sub' if sub else 'alle',sub['t'] if sub else '')
    crumbs=[(N,f'{LAND}/'),('Festgeld',f'{LAND}/festgeld/')]+([(lzt(m),rel)] if lzslug else [('Bestenlisten',f'{LAND}/festgeld/bestenlisten/'),(sub['t'],rel)] if sub else [])
    top=[a for a in X if ertrag(a,DEF_B,m)['fit']][:10]
    ld=K.graph(rel,t,ds,crumbs,[{"@type":"ItemList","name":h1,"numberOfItems":len(top),"itemListElement":[{"@type":"ListItem","position":i+1,"name":titel(a),"url":f"https://finvallo.com/{LAND}/festgeld/{a['slug']}/"} for i,a in enumerate(top)]},faqld(fq)],date=max(a['geprueft'] for a in xs))
    kurz=''
    if kz:
        kurz=f'<b>Kurz gesagt:</b> Für {eur(DEF_B)} € und {lzt(m)} zahlt {E(titel(kz["best"]))} am meisten: {pct(kz["bz"])} pro Jahr, Einlagensicherung {E(landN(kz["best"]))}.'
        if kz['bh'] and kz['bh'] is not kz['best']: kurz+=f' Bestes Angebot mit {E(CC["heim"])}r Einlagensicherung: {E(titel(kz["bh"]))} mit {pct(kz["bhz"])}.'
        kurz+=f' Die Hälfte der {kz["n"]} passenden Angebote zahlt mindestens {pct(kz["med"])}. Stand: {st}.'
    up=P+f'{LAND}/festgeld/'
    lzlinks=' · '.join(f'<a class="lnk" href="{up}{s}/"{" aria-current=page" if s==lzslug else ""}>{t_}</a>' for x,s,t_ in LZ if x in LZ_SEITEN)
    bllinks=' · '.join(f'<a class="lnk" href="{up}bestenlisten/{c["k"]}/"{" aria-current=page" if sub and c["k"]==sub["k"] else ""}>{E(c["t"])}</a>' for c in fcats() if BL.get(c['k']))
    if lzslug: lede=f'Alle Festgeld-Angebote mit {lzd(m)} Laufzeit für Kundinnen und Kunden aus {N}, sortiert nach Zins für deinen Betrag. Jede Zahl stammt von der Konditionsseite der Bank oder der Plattform, über die du abschließt.'
    elif sub: lede=sub['d']
    else: lede=f'{n} Festgeld-Angebote von {nb} Banken, die Kundinnen und Kunden aus {N} annehmen. Wähle Betrag und Laufzeit, filtere nach Einlagensicherung, Länderrating und Zinszahlung. Jede Zahl stammt von der Konditionsseite der Bank oder der Plattform. Provisionen haben keinen Einfluss auf die Reihenfolge.'
    nav=up if lzslug else None
    nb_lz=''
    if lzslug:
        ms=[x for x,_,_ in LZ if x in LZ_SEITEN]; i=ms.index(m)
        nb_lz='<h2>Zinsen nach Laufzeit</h2>'+zinskurve(xs,P,m)
        if 0<i<len(ms)-1 or len(ms)>1:
            nachbarn=[x for x in (ms[i-1] if i>0 else None,ms[i+1] if i<len(ms)-1 else None) if x]
            nb_lz+='<p class="note">Kürzer oder länger binden: '+' · '.join(f'<a class="lnk" href="{up}{lzslug_of(x)}">Festgeld {lzt(x)}</a>' for x in nachbarn)+'</p>'
    rg=rg_links(P)
    crumb=f'<div class="crumb"><span><a href="{up}">Festgeld</a> › {"<a href=../>Bestenlisten</a> › "+E(sub["t"]) if sub else E(lzt(m))}</span><span>Stand {st}</span></div>' if (lzslug or sub) else ''
    body=f'''{hdr(P,rel)}
<div class="wrap"><main id="app">
{crumb}
<h1>{E(h1)}</h1>
  <p class="lede">{E(lede)}</p>
  {f'<div class="facts prose"><p>{kurz}</p></div>' if kurz else ''}
  <p class="note" style="margin:6px 0 14px">Laufzeiten: {lzlinks}<br>Bestenlisten: {bllinks}<br><a class="lnk" href="{up}bank/">Alle Banken</a> · <a class="lnk" href="{up}methodik/">So vergleichen wir</a>{" · Ratgeber: "+rg if rg else ""}</p>
  {calcbox(m,nav)}
  {filterbox(X,len(shown))}
  <div class="list" data-fg data-limit="30">{liste_html(X,P,base,m)}</div>
  <button type="button" class="btn ghost block" data-more hidden>Alle Angebote zeigen</button>
  {nb_lz}
  <h2>Festgeld: das Wichtigste in Kürze</h2><div class="prose"><p><b>Zins und Laufzeit:</b> Der Zins steht für die ganze Laufzeit fest. Längere Laufzeiten bringen nicht immer mehr Zinsen; vergleiche deshalb mehrere Laufzeiten{"" if lzslug else " (siehe Tabelle unten)"}.</p>
  <p><b>Sicherheit:</b> {E(CC["sich"])}</p><p><b>Steuern:</b> {E(CC["steuer"])} Was nach Steuern bleibt, rechnest du mit dem {steuerlink(P)} aus, wie dein Geld über viele Jahre wächst, mit dem {zinslink(P)}.</p>
  <p><b>Konto für die Auszahlung:</b> Die Zinsen und am Ende das Geld gehen auf ein Referenzkonto. Ein passendes, günstiges Konto findest du im <a href="{P}{LAND}/girokonto/">Girokonto-Vergleich</a>.</p></div>
  {"" if lzslug else "<h2>Zinsen nach Laufzeit</h2>"+zinskurve(xs,P)}
  <h2>Fragen und Antworten</h2>{faqhtml(fq)}
  {"" if (lzslug or sub) else f'<p class="note" style="margin-top:18px">Die Daten gibt es offen als <a class="lnk" href="../daten/festgeld.json">JSON</a> und <a class="lnk" href="../daten/festgeld.csv">CSV</a>, frei nutzbar mit Quellenangabe.</p>'}
</main>
{K.footer(P)}'''
    body=body.replace('</body>',script(P),1)
    K.write(rel,head(t,ds,rel,P,ld)+body)

def bestenlisten_hub(xs):
    N=CC['N']; base=f'{LAND}/festgeld/bestenlisten/'; P='../../../'; st=S(xs)
    cats=[c for c in fcats() if BL.get(c['k'])]
    tiles=''
    for c in cats:
        X=BL[c['k']]; kz=kennzahlen(X,DEF_M)
        top=kz['best'] if kz else X[0]
        tiles+=f'<a class="catcard" href="{c["k"]}/"><span class="ct">{E(c["t"])}</span><b>{E(titel(top))}</b><span>{pct(kz["bz"]) if kz else pct(topzins(top))} für {lzt(DEF_M) if kz else lzspan(top)}</span><small>{len(X)} Angebote · Liste ansehen →</small></a>'
    t=f'Beste Festgeld-Angebote {N} 2026 nach Kategorie | Finvallo'
    d=f'Die besten Festgeld-Angebote in {N} nach Kategorie: {", ".join(c["t"].lower() for c in cats[:5])} und mehr. Stand {st}.'
    ld=K.graph(base,t,d,[(N,f'{LAND}/'),('Festgeld',f'{LAND}/festgeld/'),('Bestenlisten',base)],[{"@type":"ItemList","name":f"Bestenlisten Festgeld {N}","itemListElement":[{"@type":"ListItem","position":i+1,"name":c['h'],"url":f"https://finvallo.com/{base}{c['k']}/"} for i,c in enumerate(cats)]}])
    K.write(base,head(t,d,base,P,ld)+f'''{hdr(P,base)}
<div class="wrap"><main id="app">
<div class="crumb"><span><a href="../">Festgeld</a> › Bestenlisten</span><span>Stand {st}</span></div>
<h1>Beste Festgeld-Angebote in {N} nach Kategorie</h1><p class="lede">Nicht jedes Angebot passt zu jedem. Hier findest du die besten Angebote für deinen Fall, sortiert nach Zins für {eur(DEF_B)} € und {lzt(DEF_M)}. Mit deinem Betrag und deiner Laufzeit rechnest du in jeder Liste.</p>
<div class="catgrid">{tiles}</div>
<h2>Wie entstehen die Listen?</h2><div class="prose"><p>Jede Liste zeigt nur Angebote, die eine klare Bedingung erfüllen, etwa „vorzeitig kündbar“ oder „{E(CC["heimF"]).lower()}“. Innerhalb der Liste gilt dieselbe Reihenfolge wie im <a href="../">Festgeld-Vergleich</a>: höchster Zins zuerst, bei gleichem Zins das bessere Länderrating. Wie wir rechnen, steht in der <a href="../methodik/">Methodik</a>.</p></div>
</main>
{K.footer(P)}''')

# ---------- Bankseiten ----------
def bank_pages(xs):
    N=CC['N']; base=f'{LAND}/festgeld/bank/'; P='../../../../'; st=S(xs)
    by={}
    for a in xs: by.setdefault(a['bank_key'],[]).append(a)
    rows=''
    for k,ys in sorted(by.items(),key=lambda kv:kv[1][0]['bank'].lower()):
        a=ys[0]; tz=max(topzins(y) for y in ys)
        rows+=f'<tr><td><a class="lnk" href="{a["bank_slug"]}/">{E(a["bank"])}</a><br><small class="mut">{E(landN(a))}</small></td><td>{len(ys)}</td><td>{E(", ".join(sorted({vtK(y) for y in ys})))}</td><td><b>{pct(tz)}</b></td></tr>'
    t=f'Festgeld nach Bank: {len(by)} Banken in {N} | Finvallo'
    d=f'Alle {len(by)} Banken im Festgeld-Vergleich {N} mit ihren Angeboten direkt, über Raisin, CHECK24 oder andere Plattformen. Höchster Zins je Bank, Stand {st}.'
    ld=K.graph(base,t,d,[(N,f'{LAND}/'),('Festgeld',f'{LAND}/festgeld/'),('Banken',base)],[{"@type":"ItemList","name":f"Banken im Festgeld-Vergleich {N}","numberOfItems":len(by),"itemListElement":[{"@type":"ListItem","position":i+1,"name":ys[0]['bank'],"url":f"https://finvallo.com/{base}{ys[0]['bank_slug']}/"} for i,(k,ys) in enumerate(sorted(by.items(),key=lambda kv:kv[1][0]['bank'].lower()))]}])
    K.write(base,head(t,d,base,'../../../',ld)+f'''{hdr('../../../',base)}
<div class="wrap"><main id="app">
<div class="crumb"><span><a href="../">Festgeld</a> › Banken</span><span>Stand {st}</span></div>
<h1>Festgeld nach Bank</h1><p class="lede">{len(by)} Banken mit Festgeld für Kundinnen und Kunden aus {N}. Viele gibt es auf mehreren Wegen: direkt, über Raisin oder über CHECK24, oft mit verschiedenen Zinsen. Auf der Bankseite stehen alle Wege nebeneinander.</p>
<div class="tbl wide"><table><thead><tr><th>Bank</th><th>Angebote</th><th>Abschluss</th><th>Höchster Zins</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="note"><a class="lnk" href="../">Zum Festgeld-Vergleich mit Rechner →</a> · <a class="lnk" href="../methodik/">So vergleichen wir →</a></p>
</main>
{K.footer('../../../')}''')
    for k,ys in by.items():
        a=ys[0]; rel=f'{base}{a["bank_slug"]}/'; ys=sorted(ys,key=lambda y:(plattform(y),-topzins(y)))
        ms=sorted({m for y in ys for m in laufzeiten(y)})
        th=''.join(f'<th>{E(vtK(y))}{" (Neugeld)" if neugeld(y) else ""}</th>' for y in ys)
        tb=''
        for m in ms:
            tb+=f'<tr><td>{lzt(m)}</td>'+''.join(f'<td>{pct(topzins(y,m)) if topzins(y,m) is not None else "–"}</td>' for y in ys)+'</tr>'
        cards=''.join(f'<a class="catcard" href="../../{y["slug"]}/"><span class="ct">{E(vtT(y))}</span><b>{E(titel(y))}</b><span>bis {pct(topzins(y))} · {E(lzspan(y))}</span><small>Anlage {E(anlT(y) or "keine Angabe")} · Details →</small></a>' for y in ys)
        tz=max(topzins(y) for y in ys)
        t=f'{a["bank"]} Festgeld {N}: Zinsen und Wege zum Abschluss | Finvallo'
        if len(t)>62: t=f'{a["bank"]} Festgeld ({CC["code"]}): alle Angebote | Finvallo'
        d=f'{a["bank"]} Festgeld für {N}: {len(ys)} {"Angebot" if len(ys)==1 else "Angebote"} ({", ".join(sorted({vtK(y) for y in ys}))}), bis {pct(tz)} Zinsen. Einlagensicherung {landN(a)}, Stand {st}.'
        d=K.fit_desc(d) if hasattr(K,'fit_desc') else d[:155]
        gl=giro_links(a); ar=anb_rel(a)
        mehr=''
        if gl: mehr+=f'<p class="note">Girokonten von {E(a["bank"])} im Vergleich: '+', '.join(f'<a class="lnk" href="{P}{LAND}/girokonto/{s}/">{E(n)}</a>' for s,n in gl)+'</p>'
        if ar: mehr+=f'<p class="note"><a class="lnk" href="{P}{ar}">Kreditkarten von {E(a["bank"])} →</a></p>'
        fq=[(f'Wo bekomme ich bei {a["bank"]} den höchsten Festgeldzins?',f'Für Kundinnen und Kunden in {N} zahlt {a["bank"]} den höchsten Zins aktuell {vtT(max(ys,key=topzins))}: bis {pct(tz)} pro Jahr. Die Tabelle oben zeigt alle Wege nebeneinander. Stand: {st}.'),
            (f'Wie sicher ist Festgeld bei {a["bank"]}?',f'Einlagen bei {a["bank"]} ({a.get("institut") or a["bank"]}) sind über die {sichT(a)} geschützt'+(f', Länderrating {landN(a)} (S&P) {rating(a)}.' if rating(a) else '.')+' Das gilt unabhängig davon, über welchen Weg du abschließt, weil das Geld immer bei dieser Bank liegt.')]
        ld=K.graph(rel,t,d,[(N,f'{LAND}/'),('Festgeld',f'{LAND}/festgeld/'),('Banken',base),(a['bank'],rel)],[{"@type":"BankOrCreditUnion","@id":f"https://finvallo.com/{rel}#bank","name":a.get('institut') or a['bank'],"url":f"https://finvallo.com/{rel}"},faqld(fq)],date=max(y['geprueft'] for y in ys))
        K.write(rel,head(t,d,rel,P,ld)+f'''{hdr(P,rel)}
<div class="wrap"><main id="app">
<div class="crumb"><span><a href="../../">Festgeld</a> › <a href="../">Banken</a> › {E(a["bank"])}</span><span>Stand {st}</span></div>
<h1>{E(a["bank"])}: Festgeld in {N}</h1>
<p class="lede">{E(a.get("institut") or a["bank"])}, Einlagensicherung {E(landN(a))}{" (Länderrating "+E(rating(a))+")" if rating(a) else ""}. {len(ys)} {"Angebot" if len(ys)==1 else "Angebote"} für Kundinnen und Kunden aus {N}: {E(", ".join(sorted({vtT(y) for y in ys})))}.</p>
<h2>Zinsen je Laufzeit und Abschlussweg</h2>
<div class="tbl wide"><table><thead><tr><th>Laufzeit</th>{th}</tr></thead><tbody>{tb}</tbody></table></div>
<p class="note">Höchster Zins je Laufzeit, Stand {st}. Mindestanlage, Zinszahlung und Kündigung unterscheiden sich je Weg und stehen auf der Angebotsseite.</p>
<h2>Die Angebote</h2><div class="catgrid">{cards}</div>
{bank_btn(ys)}
{mehr}
<h2>Fragen und Antworten</h2>{faqhtml(fq)}
<p class="note" style="margin-top:18px"><a class="lnk" href="../../">Zum Festgeld-Vergleich →</a> · <a class="lnk" href="../../methodik/">So vergleichen wir →</a></p>
</main>
{K.footer(P)}''')

# ---------- Angebotsseite ----------
def offer_page(a,xs):
    rel=f'{LAND}/festgeld/{a["slug"]}/'; P='../../../'; N=CC['N']
    tz=topzins(a); lzs=laufzeiten(a)
    vs='' if not plattform(a) else ' über '+vtS(a)
    t=f'{titel(a)}{vs}: Zinsen {N} | Finvallo'
    if len(t)>62: t=f'{titel(a)}{vs} ({CC["code"]}) | Finvallo'
    if len(t)>62: t=f'{a["bank"]} Festgeld{vs} ({CC["code"]}) | Finvallo'
    if len(t)>66: t=f'{a["bank"]} Festgeld {vtS(a)} {CC["code"]} | Finvallo'
    anl=anlT(a)
    d=f'{titel(a)} {vtT(a)}: bis {pct(tz)} Zinsen, Laufzeit {lzspan(a)}'+(f', Anlage {anl}' if anl else '')+f'. Einlagensicherung {landN(a)}, Zinsen {zzT(a)}, Stand {dmy(a.get("stand") or a["geprueft"])}.'
    d=K.fit_desc(d) if hasattr(K,'fit_desc') else d[:155]
    gp=a['geprueft']
    nm=f'{titel(a)} {vtT(a)}'; kurz=lambda x:x[:1].lower()+x[1:] if x and not x[:2].isupper() else x
    fq=[(f'Wie viel Zinsen zahlt {titel(a)}?',f'{nm} zahlt Kundinnen und Kunden in {N} je nach Laufzeit bis {pct(tz)} pro Jahr ({lzspan(a)}), laut Angabe vom {dmy(a.get("stand") or gp)}.'),
        ('Wie sicher ist das Geld?',f'Bei {nm} sind die Einlagen über die {sichT(a)} geschützt'+(f'. Länderrating {landN(a)} (S&P): {rating(a)}.' if rating(a) else '.')+(f' Zusätzlich: {a["einlagensicherung"]["freiwillig"]}.' if (a.get('einlagensicherung') or {}).get('freiwillig') else '')),
        ('Wann werden die Zinsen gezahlt?',f'Bei {nm}: '+kurz((a.get('zinszahlung_text') or zzT(a)).rstrip('.'))+'.'),
        ('Wird die Steuer automatisch abgezogen?',f'Bei {nm}: '+kurz((a.get('steuer') or steuerT(a)).rstrip('.'))+'.'),
        ('Kann ich vorzeitig an mein Geld?',f'Bei {nm}: '+kurz((a.get('kuendigung_text') or kdT(a)).rstrip('.'))+'.')]
    if plattform(a): fq.append((f'Wie schließe ich das Festgeld ab?',f'In {N} schließt du {titel(a)} {vtT(a)} ab. '+(f'Dafür brauchst du: {a["konto_noetig"]}.' if a.get('konto_noetig') else 'Das Konto dort ist kostenlos.' if (a.get('kosten') or '').startswith('kostenlos') else '')))
    gs=geschwister(a,xs)
    if gs: fq.append((f'Gibt es {a["bank"]} Festgeld auch auf anderen Wegen?',f'Ja, neben {titel(a)} ({vtT(a)}) gibt es '+'; '.join(f'{titel(g)} {vtT(g)} bis {pct(topzins(g))}' for g in gs)+f'. Das Geld liegt in jedem Fall bei {a.get("institut") or a["bank"]}, die Einlagensicherung ist dieselbe; Zinsen, Mindestanlage und Steuerabzug können sich unterscheiden.'))
    amt={"@type":"MonetaryAmount","currency":"EUR"}
    if a.get('min_anlage') is not None: amt["minValue"]=a['min_anlage']
    if a.get('max_anlage') is not None: amt["maxValue"]=a['max_anlage']
    dep={"@type":"DepositAccount","@id":f"https://finvallo.com/{rel}#angebot","name":titel(a),"url":f"https://finvallo.com/{rel}","provider":{"@type":"BankOrCreditUnion","name":a.get('institut') or a['bank']},
         "areaServed":{"@type":"Country","name":N},"interestRate":{"@type":"QuantitativeValue","value":tz,"unitText":"% p. a.","minValue":min(z['zins'] for z in a['zinsen']),"maxValue":tz},"amount":amt,
         "feesAndCommissionsSpecification":a.get('kosten') or 'kostenlos'}
    ld=K.graph(rel,t,d,[(N,f'{LAND}/'),('Festgeld',f'{LAND}/festgeld/'),(titel(a),rel)],[dep,faqld(fq)],date=gp)
    rows=''
    for m in lzs:
        r=ertrag(a,DEF_B,m); zs=[z for z in a['zinsen'] if z['monate']==m]
        ztxt='<br>'.join(f'{pct(z["zins"])}'+(f' <small class="mut">({("ab "+eur(z["min"])+" €") if z["min"] is not None else ""}{" " if z["min"] is not None and z["max"] is not None else ""}{("bis "+eur(z["max"])+" €") if z["max"] is not None else ""})</small>' if (z['min'] is not None or z['max'] is not None) and len(zs)>1 else '') for z in zs)
        lnk=f'<a class="lnk" href="../{lzslug_of(m)}">{lzt(m)}</a>' if m in LZ_SEITEN else lzt(m)
        rows+=f'<tr><td>{lnk}</td><td><b>{ztxt}</b></td><td>{eur(r["ertrag"])+" €" if r["fit"] else "–"}</td></tr>'
    r_=lambda k,v: f'<div class="r"><span>{k}</span><span>{v}</span></div>'
    na='<span class="mut na">keine Angabe</span>'; v=lambda x: E(x) if x not in (None,'') else na
    es=a.get('einlagensicherung') or {}
    cond=('<div class="cond" style="margin-bottom:14px"><div class="gh">Anlage</div>'+r_('Anlagebetrag',v(anl))+r_('Laufzeiten',E(', '.join(lzt(m) for m in lzs)))+r_('Zinszahlung',v(a.get('zinszahlung_text') or zzT(a)))
          +r_('Zinseszins',{True:'ja',False:'nein'}.get(a.get('zinseszins'),na))+r_('Vorzeitig kündbar',v(a.get('kuendigung_text') or kdT(a)))+r_('Am Laufzeitende',E(vlT(a)))
          +'</div><div class="cond" style="margin-bottom:14px"><div class="gh">Sicherheit</div>'+r_('Bank',E(a.get('institut') or a['bank']))+r_('Sitz der Einlagensicherung',E(landN(a)))
          +r_('Gesetzliche Einlagensicherung',E(sichT(a)))+(r_('Zusätzliche Sicherung',E(es['freiwillig'])) if es.get('freiwillig') else '')+r_('Länderrating (S&P)',v(rating(a)))
          +'</div><div class="cond" style="margin-bottom:14px"><div class="gh">Steuer und Abschluss</div>'+r_('Steuer',v(a.get('steuer') or steuerT(a)))+r_('Abschluss',E(vtT(a)))
          +r_('Zusätzliches Konto',v(a.get('konto_noetig')) if a.get('konto_noetig') else 'nicht nötig' if a.get('konto_noetig') is None and not plattform(a) else na)
          +r_('Kosten',v(a.get('kosten')))+r_('Eröffnung',v({'online':'online','filiale':'in der Filiale','beides':'online oder in der Filiale'}.get(a.get('eroeffnung'))))+r_('Legitimation',v(a.get('legitimation')))
          +r_('Nur für Neukunden',{True:'ja',False:'nein'}.get(a.get('neukunden_only'),na))+(r_('Gemeinschaftskonto',{True:'möglich',False:'nicht möglich'}[a['gemeinschaftskonto']]) if a.get('gemeinschaftskonto') is not None else '')
          +(r_('Aktion',E(a['aktion'])) if a.get('aktion') else '')+(r_('Hinweis',E(a['hinweis'])) if a.get('hinweis') else '')+'</div>')
    m0=DEF_M if DEF_M in lzs else lzs[0]
    sim=[x for x in xs if x is not a and x['bank_key']!=a['bank_key'] and m0 in laufzeiten(x) and ertrag(x,DEF_B,m0)['fit']]
    sim=ordnen(sim,m0)[:5]
    simt=''.join(f'<tr><td><a class="lnk" href="../{x["slug"]}/">{E(titel(x))}</a><br><small class="mut">{E(vtT(x))}</small></td><td><b>{pct(ertrag(x,DEF_B,m0)["zins"])}</b></td><td>{E(landN(x))}{" ("+E(rating(x))+")" if rating(x) else ""}</td></tr>' for x in sim)
    gst=''
    if gs:
        gst=f'<h2>{E(a["bank"])} Festgeld auf anderen Wegen</h2><div class="tbl wide"><table><thead><tr><th>Abschluss</th><th>Zins p. a. (höchster)</th><th>Laufzeiten</th><th>Steuer</th></tr></thead><tbody>'
        gst+=''.join(f'<tr><td><a class="lnk" href="../{g["slug"]}/">{E(vtT(g))}</a></td><td><b>bis {pct(topzins(g))}</b></td><td>{E(lzspan(g))}</td><td>{E(steuerT(g))}</td></tr>' for g in gs)
        gst+=f'</tbody></table></div><p class="note"><a class="lnk" href="../bank/{a["bank_slug"]}/">Alle Angebote von {E(a["bank"])} im Überblick →</a></p>'
    glance=f'{titel(a)} ist ein Festgeld der {a.get("institut") or a["bank"]}, abgeschlossen {vtT(a)}. Es gibt {len(lzs)} Laufzeit{"en" if len(lzs)>1 else ""} ({lzspan(a)}) mit bis zu {pct(tz)} Zinsen pro Jahr.'+(f' Anlage {anl}, Zinsen {zzT(a)}.' if anl else f' Zinsen {zzT(a)}.')+f' Einlagensicherung: {landN(a)}. Zinsen laut Anbieter vom {dmy(a.get("stand") or gp)}.'
    pc,kc=pros(a),cons(a)
    gl=giro_links(a); ar=anb_rel(a)
    mehr=''
    if gl: mehr+=f'<p class="note">Girokonten von {E(a["bank"])} im Vergleich: '+', '.join(f'<a class="lnk" href="{P}{LAND}/girokonto/{s}/">{E(n)}</a>' for s,n in gl)+'</p>'
    if ar: mehr+=f'<p class="note"><a class="lnk" href="{P}{ar}">Kreditkarten von {E(a["bank"])} →</a></p>'
    body=f'''{hdr(P,rel)}
<div class="wrap"><main id="app">
<div class="crumb"><span><a href="../">Festgeld</a> › <a href="../bank/{a["bank_slug"]}/">{E(a["bank"])}</a></span><span class="ok">✓ Geprüft am {dmy(gp)}</span></div>
  <div class="dh">{face(a)}<div style="min-width:0"><div class="tags">{tags(a)}</div>
    <h1>{E(titel(a))}{f' <small class="mut">über {E(plattN(a))}</small>' if plattform(a) else ''}</h1></div></div>
  <div class="box feebox"><small>Zins pro Jahr</small><span class="big good">bis {pct(tz)}</span><small class="mut">Laufzeit {E(lzspan(a))}{" · Anlage "+E(anl) if anl else ""}</small>
    {btn(a)}
    <div class="actrow"><a class="plink" href="{E(a["quelle"])}" target="_blank" rel="noopener">Konditionen beim Anbieter ↗</a></div></div>
  <section class="facts box glance" aria-label="Auf einen Blick"><h2 style="margin-top:0">Auf einen Blick</h2><div class="prose"><p>{E(glance)}</p></div></section>
  <h2>Zinsen nach Laufzeit</h2>
  <div class="tbl"><table><thead><tr><th>Laufzeit</th><th>Zins p. a.</th><th>Zinsen für {eur(DEF_B)} €</th></tr></thead><tbody>{rows}</tbody></table></div>
  {'<p class="note"><b>Hinweis zur Quelle:</b> Einzelne Angaben zu diesem Angebot stammen aus Vergleichsportalen, weil die Bank sie nicht frei abrufbar veröffentlicht. Bitte vor dem Abschluss beim Anbieter prüfen.</p>' if a.get('sek') else ''}
  <p class="note">Zinsen vor Steuern{", mit Zinseszins bei mehr als 12 Monaten" if a.get("zinseszins") is True else ""}. Quelle: {K.ext(a["quelle"])}, Stand {dmy(a.get("stand") or gp)}. Was nach Steuern bleibt: {steuerlink(P)}.</p>
  <h2>Vorteile und Nachteile</h2>
  <div class="pc"><div class="box pro"><h3>Das spricht dafür</h3>{'<ul class="checks">'+"".join(f"<li>{E(x)}</li>" for x in pc)+'</ul>' if pc else '<p class="note">Keine besonderen Vorteile.</p>'}</div>
  <div class="box con"><h3>Das spricht dagegen</h3>{'<ul class="checks neg">'+"".join(f"<li>{E(x)}</li>" for x in kc)+'</ul>' if kc else '<p class="note">Keine bekannten Nachteile.</p>'}</div></div>
  <h2>Konditionen im Überblick</h2>{cond}
  {gst}
  {f"<h2>Andere Angebote für {lzt(m0)}</h2><div class='tbl wide'><table><thead><tr><th>Angebot</th><th>Zins p. a.</th><th>Einlagensicherung</th></tr></thead><tbody>{simt}</tbody></table></div><p class='note'><a class='lnk' href='../{lzslug_of(m0)}'>Alle Angebote für {lzt(m0)} →</a> · <a class='lnk' href='../'>Zum Festgeld-Vergleich →</a></p>" if simt else ""}
  <h2>Fragen und Antworten</h2>{faqhtml(fq)}
  {mehr}
  <p class="note"><a class="lnk" href="../methodik/">So vergleichen wir Festgeld</a> · <a class="lnk" href="../bestenlisten/{CC["bl_slug"]}/">Festgeld bei {E(CC["heimB"])}</a> · {zinslink(P)} · {steuerlink(P)}</p>
  <p class="src" style="margin-top:18px">Quelle: {K.ext(a["quelle"])}{" · "+K.ext(a["quelle2"]) if a.get("quelle2") else ""}. Konditionen vor dem Abschluss beim Anbieter prüfen. Fehler gefunden? <a href="mailto:hallo@finvallo.com?subject=Korrektur%20{E(a['slug'])}">Schreib uns</a>.</p>
</main>
{K.footer(P)}'''
    K.write(rel,head(t,d,rel,P,ld)+body)

# ---------- Methodik ----------
def methodik_page(xs):
    rel=f'{LAND}/festgeld/methodik/'; P='../../../'; N=CC['N']
    t=f'So vergleichen wir Festgeld in {N} | Finvallo'
    d=f'Wie der Festgeld-Vergleich für {N} rechnet und sortiert: Zins für Betrag und Laufzeit, Zinseszins, Einlagensicherung, Länderrating, Steuer und Datenquellen.'
    ld=K.graph(rel,t,d,[(N,f'{LAND}/'),('Festgeld',f'{LAND}/festgeld/'),('So vergleichen wir',rel)],date=max(a['geprueft'] for a in xs))
    ls=sorted({a['sitz'] for a in xs},key=lambda c:(-(RAT.get((LAENDER.get(c) or {}).get('rating_sp') or '',0)),c))
    lrows=''.join(f'<tr><td>{E((LAENDER.get(c) or {}).get("name") or c)}</td><td>{E((LAENDER.get(c) or {}).get("sicherung") or "")}</td><td>{E({"NR":"kein Rating","":"keine Angabe"}.get((LAENDER.get(c) or {}).get("rating_sp") or "",(LAENDER.get(c) or {}).get("rating_sp")))}</td><td>{sum(1 for a in xs if a["sitz"]==c)}</td></tr>' for c in ls)
    fq=[('Warum gibt es beim Festgeld keine Sterne?','Weil beim Festgeld fast nur der Zins zählt und alle Angebote dieselbe gesetzliche Einlagensicherung bis 100.000 € haben. Sterne würden Unterschiede vortäuschen, die es nicht gibt. Die Dinge, die neben dem Zins wichtig sind (Land, Rating, Steuer, Kündigung), zeigen wir offen und filterbar.'),
        ('Zählt ein Angebot über Raisin und direkt bei der Bank doppelt?','Ja, beide stehen in der Liste, weil Zins, Mindestanlage und Steuerabzug sich unterscheiden können. Bei der Zahl der Banken zählen wir jede Bank aber nur einmal. Auf der Bankseite stehen alle Wege nebeneinander.'),
        ('Wie oft werden die Zinsen geprüft?','Bei jedem Angebot steht das Prüfdatum. Zinsen ändern sich oft, vor allem bei Plattformen; deshalb prüfen wir die Listen regelmäßig und du solltest die Konditionen vor dem Abschluss beim Anbieter prüfen.')]
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
<h2>Woher die Daten kommen</h2><div class="prose"><p>Jede Zahl stammt von der Konditionsseite, dem Preisaushang oder dem Informationsbogen der Bank oder von der Produktseite der Plattform, über die du abschließt. Bei jedem Angebot stehen Quelle und Prüfdatum. Laufzeiten, die eine Plattform nur mit einem Platzhalterzins unter 0,3 % führt, lassen wir weg. Zinsen ändern sich oft; prüfe die Konditionen vor dem Abschluss beim Anbieter. Die Daten gibt es offen als <a class="lnk" href="../../daten/festgeld.json">JSON</a> und <a class="lnk" href="../../daten/festgeld.csv">CSV</a>.</p></div>
<h2>Was in den Vergleich kommt</h2><div class="prose"><p>Festgeld, Sparbriefe und Termineinlagen mit festem Zins, die man von überall im Land abschließen kann und deren Einlagen über eine gesetzliche Einlagensicherung in der EU geschützt sind. Regionale Angebote, Produkte mit schwankendem Zins (etwa Zuwachssparen) und Angebote, deren Konditionen wir nicht aus erster Hand prüfen konnten, nehmen wir nicht auf.</p></div>
<h2>Fragen und Antworten</h2>{faqhtml(fq)}
<p><a class="lnk" href="../">← Zum Festgeld-Vergleich</a> · {zinslink(P)} · {steuerlink(P)}</p>
</main>
{K.footer(P)}'''
    ld['@graph'].append(faqld(fq))
    K.write(rel,head(t,d,rel,P,ld)+body)

def export(xs,d):
    os.makedirs(R+f'{LAND}/daten',exist_ok=True)
    keys=['slug','bank','bank_key','institut','produkt','vertrieb','vertrieb_url','sitz','einlagensicherung','zinsen','min_anlage','max_anlage','zinszahlung','zinseszins','steuer_auto','kuendigung','verlaengerung','konto_noetig','neukunden_only','eroeffnung','aktion','quelle','stand','geprueft']
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
        b=f'\n## {N}: Festgeld\n- [Festgeld-Vergleich {N}](https://finvallo.com/{LAND}/festgeld/): {len(xs)} Angebote von {nbanken(xs)} Banken, Zinsen nach Betrag und Laufzeit, Einlagensicherung und Länderrating, Stand {st}\n'
        b+=''.join(f'- [Festgeld {t_} {N}](https://finvallo.com/{LAND}/festgeld/{s}/)\n' for m,s,t_ in LZ if m in LZ_SEITEN)
        b+=f'- [Bestenlisten Festgeld {N}](https://finvallo.com/{LAND}/festgeld/bestenlisten/): {", ".join(c["t"] for c in fcats() if BL.get(c["k"]))}\n- [Festgeld nach Bank](https://finvallo.com/{LAND}/festgeld/bank/)\n- [So vergleichen wir Festgeld](https://finvallo.com/{LAND}/festgeld/methodik/)\n- [Daten als JSON](https://finvallo.com/{LAND}/daten/festgeld.json)\n'
        top=[a for a in ordnen(xs,DEF_M) if ertrag(a,DEF_B,DEF_M)['fit']][:5 if fn=='llms.txt' else 30]
        b+=''.join(f'- [{titel(a)}](https://finvallo.com/{LAND}/festgeld/{a["slug"]}/): {pct(ertrag(a,DEF_B,DEF_M)["zins"])} für {lzt(DEF_M)}, {vtT(a)}, Einlagensicherung {landN(a)}\n' for a in top)
        # vor „## Optional“ einfügen, damit der Abschnitt nicht als überspringbar gilt
        i=t.find('\n## Optional'); t=(t[:i].rstrip()+'\n'+b+t[i:]) if i>=0 else t.rstrip()+'\n'+b
        open(p,'w',encoding='utf-8').write(re.sub(r'\n{3,}','\n\n',t))

# ---------- Anbieterseiten der Kreditkarten: Abschnitt „Festgeld von …“ ----------
def anbieter_festgeld(xs):
    by={}
    for a in xs: by.setdefault(a['bank_key'],[]).append(a)
    for k,ys in by.items():
        rel=anb_rel(ys[0])
        if not rel: continue
        f=R+rel+'index.html'; s=open(f,encoding='utf-8').read()
        s=re.sub(r'<!--festgeld-->.*?<!--/festgeld-->','',s,flags=re.S)
        ys=sorted(ys,key=lambda y:-topzins(y))
        rows=''.join(f'<tr><td><a class="lnk" href="../../../festgeld/{y["slug"]}/">{E(titel(y))}</a><br><small class="mut">{E(vtT(y))}</small></td><td><b>bis {pct(topzins(y))}</b></td><td>{E(lzspan(y))}</td></tr>' for y in ys)
        blk=(f'<!--festgeld--><h2>Festgeld von {E(ys[0]["bank"])}</h2><p class="note">{len(ys)} {"Angebot" if len(ys)==1 else "Angebote"} von {E(ys[0]["bank"])} in unserem <a class="lnk" href="../../../festgeld/">Festgeld-Vergleich</a>, sortiert nach Zins.</p>'
             f'<div class="tbl wide"><table><thead><tr><th>Angebot</th><th>Zins p. a.</th><th>Laufzeiten</th></tr></thead><tbody>{rows}</tbody></table></div><!--/festgeld-->')
        for mk in ('<h2>Für wen passt','<h2>Fragen und Antworten</h2>','</main>'):
            if mk in s: s=s.replace(mk,blk+mk,1); break
        open(f,'w',encoding='utf-8').write(s)

BL={}
def build_land():
    global LZ_DA,LZ_SEITEN,BL
    K.use(LAND)
    # der Ordner wird komplett neu erzeugt: Seiten weggefallener Angebote verschwinden
    import shutil; shutil.rmtree(R+f'{LAND}/festgeld',ignore_errors=True)
    d,xs=load()
    K.L.setdefault('stand',d['stand'])
    for a in xs: a.setdefault('geprueft',d['stand'])
    cnt={}
    for a in xs:
        for m in laufzeiten(a): cnt[m]=cnt.get(m,0)+1
    LZ_DA=set(cnt)
    LZ_SEITEN={m for m,_,_ in LZ if cnt.get(m,0)>=MIN_LZ_SEITE}
    BL={c['k']:[a for a in xs if c['f'](a)] for c in fcats()}
    BL={k:v for k,v in BL.items() if len(v)>=3}
    for a in xs: offer_page(a,xs)
    list_page(xs,d)
    for m,s,_ in LZ:
        if m in LZ_SEITEN: list_page(xs,d,m,lzslug=s)
    for c in fcats():
        if BL.get(c['k']): list_page(xs,d,sub=c)
    bestenlisten_hub(xs); bank_pages(xs); anbieter_festgeld(xs)
    methodik_page(xs); export(xs,d); llms(xs,d)
    print(f'Festgeld {LAND}:',len(xs),'Angebote,',nbanken(xs),'Banken,',len(LZ_SEITEN),'Laufzeit-Seiten,',len(BL),'Bestenlisten')

def slugs(l):
    d,xs=load(l); cnt={}
    for a in xs:
        for m in laufzeiten(a): cnt[m]=cnt.get(m,0)+1
    return {a['slug'] for a in xs}|{s for m,s,_ in LZ if cnt.get(m,0)>=MIN_LZ_SEITE}|{'methodik','bestenlisten','bank'}|{'bank/'+a['bank_slug'] for a in xs}
def pairs():
    """AT/DE-Seiten derselben Bank und desselben Abschlusswegs als hreflang-Paare (für eeat.py)"""
    if not all(os.path.exists(dpath(l)) for l in ('at','de')): return
    A={(a['bank_key'],vtK(a)):a['slug'] for a in load('at')[1]}
    D={(a['bank_key'],vtK(a)):a['slug'] for a in load('de')[1]}
    out=[[f'at/festgeld/{A[k]}/',f'de/festgeld/{D[k]}/'] for k in A if k in D]
    BA={a['bank_key']:a['bank_slug'] for a in load('at')[1]}; BD={a['bank_key']:a['bank_slug'] for a in load('de')[1]}
    out+=[[f'at/festgeld/bank/{BA[k]}/',f'de/festgeld/bank/{BD[k]}/'] for k in sorted(set(BA)&set(BD))]
    json.dump({'paare':out},open(HP,'w',encoding='utf-8'),ensure_ascii=False,indent=0)
def main():
    global LAND,CC
    if os.path.exists(LP): LAENDER.update(json.load(open(LP,encoding='utf-8')))
    for l in CFG:
        gp=os.path.join(SP,'daten',l,'girokonten.json')
        if os.path.exists(gp): GIRO[l]=[k for k in json.load(open(gp,encoding='utf-8'))['konten'] if k.get('aufnehmen',True)]
        for k in GIRO.get(l,[]): k.setdefault('slug',K.slug(k['bank']+' '+k['name']))
    for l in CFG:
        if os.path.exists(dpath(l)): OTHER[l]=slugs(l)
    for l in CFG:
        if l not in OTHER: continue
        LAND,CC=l,CFG[l]; build_land()
    pairs()
    LAND,CC='de',CFG['de']

if __name__=='__main__': main()
