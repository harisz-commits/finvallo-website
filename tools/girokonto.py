# Girokonto-Vergleich Österreich und Deutschland: Liste mit Filtern, persönlicher Rechnung und aufklappbaren Konditionen je Konto, Bestenlisten, Methodik.
# Daten: daten/<land>/girokonten.json (jede Zahl aus der Entgeltinformation oder Preisliste der Bank, mit Quelle und Prüfdatum).
# Rechenlogik für die Jahreskosten gibt es zweimal: kosten() hier und calc() in public/assets/giro.js.
# check.py vergleicht beide (tools/giro-kontrolle.js). Läuft nach karten.py, vor header.py.
import json,os,re,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import karten as K
import affiliate
from score import eur,pct

E=K.E; dmy=K.dmy; de1=K.de1; R=K.R; SP=K.SP
LAND='at'
def dpath(land): return os.path.join(SP,'daten',land,'girokonten.json')
# Länderwerte. Rechtliches zum Basiskonto: AT laut Arbeiterkammer (Stand 10/2026), DE laut § 41 ZKG (angemessenes Entgelt)
CFG={'at':dict(N='Österreich',code='AT',iban_pro='Österreichische IBAN',iban_con='Keine österreichische IBAN',iban_a='eine österreichische IBAN',
        basis='Das gesetzliche Zahlungskonto mit grundlegenden Funktionen. Jede Bank muss es jedem Menschen mit rechtmäßigem Aufenthalt in der EU anbieten, auch ohne Einkommen und trotz Schulden. Es kostet laut Arbeiterkammer höchstens 83,45 € im Jahr, für besonders schutzbedürftige Menschen höchstens 41,73 €.',
        regional='Regionale Banken wie Sparkassen, Raiffeisenbanken, Volksbanken und Landes-Hypos haben je nach Bundesland eigene Preise. Sie fehlen deshalb, genauso wie E-Geld-Konten ohne Einlagensicherung.',
        extern='<p>Alle Konten in Österreich findest du im <a href="https://bankenrechner.arbeiterkammer.at/" target="_blank" rel="noopener">Bankenrechner der Arbeiterkammer ↗</a>.</p>',
        rg=[('kostenloses-girokonto','Kostenloses Girokonto'),('girokonto-wechseln','Konto wechseln'),('basiskonto','Basiskonto')],
        anb={'Erste Bank':'erste'},llms_vor='\n## Deutschland: Kreditkarten'),
     'de':dict(N='Deutschland',code='DE',iban_pro='Deutsche IBAN',iban_con='Keine deutsche IBAN',iban_a='eine deutsche IBAN',
        basis='Das Basiskonto nach dem Zahlungskontengesetz. Banken, die Girokonten für Verbraucher anbieten, müssen es jedem Menschen mit rechtmäßigem Aufenthalt in der EU anbieten, auch ohne Einkommen und trotz Schulden. Das Entgelt muss angemessen sein.',
        regional='Sparkassen, Volks- und Raiffeisenbanken und regionale Sparda- und PSD-Banken haben je nach Region eigene Preise und nehmen meist nur Kundinnen und Kunden aus ihrer Region. Sie fehlen deshalb, genauso wie E-Geld-Konten ohne Einlagensicherung.',
        extern='',rg=[('kostenloses-girokonto','Kostenloses Girokonto'),('girokonto-wechseln','Konto wechseln'),('basiskonto','Basiskonto')],anb={'HVB':'hypovereinsbank','HypoVereinsbank':'hypovereinsbank'},llms_vor='\n## Deutschland: Ratgeber')}
CC=CFG['at']; OTHER={}
ART={'standard':'Gehalts- und Privatkonto','premium':'Premiumkonto','student':'Studenten- und U28-Konto','jugend':'Jugendkonto','kinder':'Kinderkonto','basis':'Basiskonto'}
SEK=[('standard','Konten für alle',None),('student','Für Studierende und junge Erwachsene','Für Studierende, Menschen in Ausbildung oder bis zu einem bestimmten Alter. Danach stellt die Bank auf ein normales Konto um, das meist etwas kostet.'),
     ('jugend','Jugendkonten','Für Jugendliche, meist ab 14 Jahren. Danach stellt die Bank auf ein normales Konto um.'),
     ('kinder','Kinderkonten','Für Kinder unter 14 Jahren. Eröffnen können nur die Eltern oder andere gesetzliche Vertreter.'),
     ('basis','Basiskonten',None)]
def sektxt(a,txt): return CC['basis'] if a=='basis' else txt
# Standardfall für die Liste: so rechnen wir, bis du eigene Zahlen eingibst
PROFIL={'standard':dict(ein=1500,alter=35,abh=4),'premium':dict(ein=1500,alter=35,abh=4),'student':dict(ein=500,alter=22,abh=4),
        'jugend':dict(ein=0,alter=16,abh=2),'kinder':dict(ein=0,alter=10,abh=1),'basis':dict(ein=0,alter=35,abh=4)}
W=[('Kosten',40),('Bedingungen',10),('Bargeld',15),('Karten',10),('Zinsen',10),('Alltag &amp; Service',15)]

def load(land=None):
    d=json.load(open(dpath(land or LAND))); ks=[k for k in d['konten'] if k.get('aufnehmen',True)]
    for k in ks:
        k.setdefault('slug',K.slug(k['bank']+' '+k['name']))
    # Zusatzdaten für die Bestenlisten (Unterkonten, Bonitätsabfrage, Nachhaltigkeit): daten/<land>/girokonten-extra.json
    xp=os.path.join(SP,'daten',land or LAND,'girokonten-extra.json')
    X=json.load(open(xp,encoding='utf-8')) if os.path.exists(xp) else {}
    for k in ks:
        k.update(((X.get('konten') or {}).get(k['slug']) or {}))
        k['_bank']=(X.get('banken') or {}).get(k['bank']) or {}
    return d,ks

# ---------- Rechnung (gleich wie calc() in giro.js) ----------
def bedingung(g,ein,alter):
    if not g: return False
    e,a,v=g.get('eingang_min'),g.get('alter_unter'),g.get('verknuepfung')
    okE=e is not None and ein>=e; okA=a is not None and alter<a
    if e is None and a is None: return False
    if v=='und': return (e is None or okE) and (a is None or okA)
    return okE or okA
def passt(k,alter):
    a=k.get('alter') or {}
    return not ((a.get('min') is not None and alter<a['min']) or (a.get('max') is not None and alter>a['max']))
def kosten(k,ein,alter,abh):
    kf=k['kf_jahr']; met=bedingung(k.get('gratis'),ein,alter)
    if met: kf=k['gratis']['kf_bedingt']*12
    dk=k.get('debitkarte') or {}; card=0 if dk.get('inkl') else (dk.get('preis_jahr') or 0)
    b=k.get('bargeld') or {}; cash=0
    if b.get('frei_monat') is not None and b.get('danach_eur') is not None: cash=max(0,abh-b['frei_monat'])*b['danach_eur']*12
    return dict(total=round(kf+card+cash,2),kf=round(kf,2),card=card,cash=round(cash,2),met=met)
def jsdata(k):
    g=k.get('gratis') or {}; dk=k.get('debitkarte') or {}; b=k.get('bargeld') or {}; a=k.get('alter') or {}
    return {'kfj':k['kf_jahr'],'g':({'e':g.get('eingang_min'),'a':g.get('alter_unter'),'v':g.get('verknuepfung'),'b':g.get('kf_bedingt')} if k.get('gratis') else None),
            'dk':0 if dk.get('inkl') else (dk.get('preis_jahr') or 0),'cf':b.get('frei_monat'),'cd':b.get('danach_eur'),'amin':a.get('min'),'amax':a.get('max'),'art':k['art']}

# ---------- Texte ----------
def monat(x): return f'{eur(x)} €'
def kfT(k):
    if k['kf_jahr']==0: return 'kostenlos'
    p={'Monat':'pro Monat','Quartal':'pro Quartal','Jahr':'pro Jahr'}[k['kf_periode']]
    return f'{eur(k["kf_betrag"])} € {p}'
def gratisT(k):
    if k['kf_jahr']==0: return 'ohne Bedingung'
    g=k.get('gratis')
    if not g: return 'kein Gratis-Modell'
    return g.get('text') or 'mit Bedingung'
def eingangT(g):
    if g.get('eingang_min') is None: return None
    art='Gehalt oder Pension' if g.get('eingang_art')=='Gehalt/Pension' else 'Geldeingang'
    return f'ab {eur(g["eingang_min"])} € {art} pro Monat'
def kurzbed(k):
    if k['kf_jahr']==0: return 'Ohne Bedingung'
    g=k.get('gratis')
    if not g: return 'kein Gratis-Modell'
    bits=[x for x in (eingangT(g),f'unter {g["alter_unter"]} Jahren' if g.get('alter_unter') else None) if x]
    t=(' oder ' if g.get('verknuepfung')!='und' else ' und ').join(bits) if bits else (g.get('text') or 'mit Bedingung')
    pre='Gratis ' if g.get('kf_bedingt')==0 else f'{eur(g["kf_bedingt"])} € pro Monat '
    return pre+t
def cashT(k):
    b=k.get('bargeld') or {}
    return b.get('text') or 'keine Angabe'
def ibanT(k): return {'AT':'österreichische IBAN (AT)','DE':'deutsche IBAN (DE)','LT':'litauische IBAN (LT)','NL':'niederländische IBAN (NL)'}.get(k.get('iban'),f'IBAN aus {k.get("iban")}' if k.get('iban') else 'keine Angabe')
def wegT(k): return {'online':'nur online','filiale':'in der Filiale','beides':'online oder in der Filiale'}.get(k.get('eroeffnung'),'keine Angabe')
def fwT(k): return 'keine Angabe' if k.get('fremdwaehrung_prozent') is None else ('0 %' if k['fremdwaehrung_prozent']==0 else pct(k['fremdwaehrung_prozent']))
def zinsT(x): return 'keine Angabe' if x is None else pct(x)

def pros(k):
    p=[]; g=k.get('gratis')
    if k['kf_jahr']==0: p.append('Kontoführung kostenlos, ohne Bedingung')
    elif g and g.get('kf_bedingt')==0: p.append('Kontoführung gratis '+re.sub(r'^Gratis ','',kurzbed(k)))
    dk=k.get('debitkarte') or {}
    if dk.get('inkl'): p.append('Debitkarte inklusive')
    if k.get('kreditkarte_inkl'): p.append('Kreditkarte ohne Aufpreis: '+k['kreditkarte'])
    b=k.get('bargeld') or {}
    if b.get('frei_monat') is None and b.get('danach_eur') is None and re.search(r'kostenlos|inklusive|gratis|0 €',b.get('text') or '',re.I) and not re.search(r'nur|bis|ab ',b.get('text') or ''): p.append('Bargeld am Automaten kostenlos')
    if k.get('iban')==CC['code']: p.append(CC['iban_pro'])
    if k.get('eroeffnung') in ('online','beides'): p.append('Online eröffnen')
    if k.get('eroeffnung') in ('filiale','beides'): p.append('Beratung in der Filiale möglich')
    if k.get('gemeinschaftskonto'): p.append('Auch als Gemeinschaftskonto')
    if (k.get('habenzins') or 0)>=1: p.append(f'{pct(k["habenzins"])} Zinsen auf Guthaben')
    if k.get('fremdwaehrung_prozent')==0: p.append('Kartenzahlung in Fremdwährung ohne Aufschlag')
    return p
def cons(k):
    c=[]; g=k.get('gratis')
    if k['kf_jahr']>0 and not g: c.append(f'Kontoführung {eur(k["kf_jahr"])} € im Jahr')
    elif k['kf_jahr']>0 and g: c.append(f'Ohne die Bedingung {eur(k["kf_jahr"])} € im Jahr')
    dk=k.get('debitkarte') or {}
    if dk.get('inkl') is False: c.append('Debitkarte kostet extra'+(f' ({eur(dk["preis_jahr"])} € im Jahr)' if dk.get('preis_jahr') else ''))
    b=k.get('bargeld') or {}
    if b.get('frei_monat') is not None and b.get('danach_eur') is not None: c.append(f'Nur {b["frei_monat"]} Abhebung{"en" if b["frei_monat"]!=1 else ""} pro Monat gratis, danach {eur(b["danach_eur"])} €' if b['frei_monat'] else f'Jede Abhebung kostet {eur(b["danach_eur"])} €')
    if k.get('iban') and k['iban']!=CC['code']: c.append(CC['iban_con'])
    if k.get('eroeffnung')=='online': c.append('Keine Filialen')
    if (k.get('ueberschreitung') or k.get('sollzins') or 0)>=13: c.append(f'Hoher Überziehungszins ({pct(k.get("ueberschreitung") or k.get("sollzins"))})')
    if (k.get('fremdwaehrung_prozent') or 0)>=1: c.append(f'{pct(k["fremdwaehrung_prozent"])} Aufschlag bei Kartenzahlung in Fremdwährung')
    if k.get('einzelposten'): c.append('Manche Buchungen kosten extra')
    return c

# ---------- Bewertung ----------
def s_kosten(j):
    for lim,s in [(0,5.0),(30,4.6),(50,4.2),(80,3.8),(120,3.2),(180,2.6),(250,2.0)]:
        if j<=lim: return s
    return 1.5
def score(k):
    pr=PROFIL[k['art']]; ko=kosten(k,pr['ein'],pr['alter'],pr['abh']); parts=[]
    parts.append(dict(k='Kosten',w=40,s=s_kosten(ko['total']),v=f'{eur(ko["total"])} € im Jahr bei {"Gehalt von "+eur(pr["ein"])+" € " if pr["ein"] else ""}{pr["abh"]} Abhebungen pro Monat',ok=True))
    g=k.get('gratis')
    if k['kf_jahr']==0 or not g: sb,vb=(5.0,'gleicher Preis für alle') if k['kf_jahr']==0 else (3.0,'kein Gratis-Modell, fester Preis')
    elif g.get('eingang_min') is not None and g.get('alter_unter') is None:
        e=g['eingang_min']; sb=4.5 if e<=500 else 4.0 if e<=1000 else 3.5 if e<=1500 else 2.5; vb=f'gratis ab {eur(e)} € Eingang'
    else: sb,vb=4.0,'Bedingung: '+(g.get('text') or 'siehe Bank')
    if g and g.get('extra'): sb=max(2.5,sb-0.5); vb+=', dazu weitere Bedingungen'
    parts.append(dict(k='Bedingungen',w=10,s=sb,v=vb,ok=True))
    b=k.get('bargeld') or {}
    if not b.get('text'): sc,vc,okc=2.5,'nicht bestätigt',False
    elif b.get('frei_monat') is not None and b.get('danach_eur') is not None:
        f=b['frei_monat']; sc=4.0 if f>=5 else 3.0 if f>=2 else 2.5 if f>=1 else 2.0; vc=b['text']; okc=True
    else: sc,vc,okc=5.0,b['text'],True
    parts.append(dict(k='Bargeld',w=15,s=sc,v=vc,ok=okc))
    dk=k.get('debitkarte') or {}
    if dk.get('inkl') is None: sk,vk,okk=2.5,'nicht bestätigt',False
    else:
        sk=3.5 if dk.get('inkl') else 2.0
        if k.get('kreditkarte_inkl'): sk=5.0
        elif k.get('kreditkarte') and dk.get('inkl'): sk=4.0
        vk=('Debitkarte inklusive' if dk.get('inkl') else 'Debitkarte kostet extra')+(', Kreditkarte ohne Aufpreis' if k.get('kreditkarte_inkl') else ', Kreditkarte nur gegen Aufpreis oder nur 1. Jahr gratis' if k.get('kreditkarte') else ''); okk=True
    parts.append(dict(k='Karten',w=10,s=sk,v=vk,ok=okk))
    z=k.get('ueberschreitung') or k.get('sollzins')
    if z is None:
        sz,vz,okz=(3.0,'keine Überziehung möglich',True) if k.get('kein_dispo') else (2.5,'nicht bestätigt',False)
    else:
        sz=5.0 if z<=7 else 4.0 if z<=9 else 3.0 if z<=11 else 2.5 if z<=13 else 2.0; vz=f'Überziehung {pct(z)}'; okz=True
        if (k.get('habenzins') or 0)>=1: sz=min(5.0,sz+0.5); vz+=f', Guthaben {pct(k["habenzins"])}'
    parts.append(dict(k='Zinsen',w=10,s=sz,v=vz,ok=okz))
    ss=2.0+(1 if k.get('iban')==CC['code'] else 0)+(1 if k.get('eroeffnung') in ('online','beides') else 0)+(1 if k.get('eroeffnung') in ('filiale','beides') else 0)
    parts.append(dict(k='Alltag &amp; Service',w=15,s=float(ss),v=', '.join(x for x in (ibanT(k),wegT(k)) if x),ok=True))
    tot=round(sum(p['s']*p['w'] for p in parts)/100+1e-9,1)
    return dict(parts=parts,stars=tot,kosten=ko)
def note(s): return 'Sehr gut' if s>=4.5 else 'Gut' if s>=4.0 else 'Befriedigend' if s>=3.5 else 'Ausreichend' if s>=3.0 else 'Schwach'

def rate(ks):
    for k in ks:
        sc=score(k); k['score']=sc; k['stars']=sc['stars']; k['note']=note(sc['stars']); k['pros']=pros(k); k['cons']=cons(k)
    out={}
    for a,_,_ in SEK:
        xs=[k for k in ks if k['art']==a or (a=='standard' and k['art']=='premium')]
        xs.sort(key=lambda k:(-k['stars'],k['score']['kosten']['total'],k['bank'].lower(),k['name'].lower()))
        for i,k in enumerate(xs): k['rank']=i+1
        out[a]=xs
    return out

# ---------- Bausteine ----------
def face(k):
    return f'<div class="face k-Debit" aria-hidden="true"><span class="pn">{E(k["bank"])}</span><span class="chipc"></span><span class="nw">GIROKONTO</span></div>'
def starrow(k): return f'<div class="stars">{K.stars(k["stars"])} <b>{de1(k["stars"])}</b> <span class="nt">{k["note"]}</span></div>'
def flags(k):
    f=[]
    if k['kf_jahr']==0: f.append('gratis')
    if k.get('gratis') and k['gratis'].get('kf_bedingt')==0: f.append('bedingt')
    if k.get('iban')==CC['code']: f.append('landiban')
    if k.get('eroeffnung') in ('filiale','beides'): f.append('filiale')
    if k.get('eroeffnung') in ('online','beides'): f.append('online')
    if k.get('kreditkarte_inkl'): f.append('kk')
    if k.get('gemeinschaftskonto'): f.append('gem')
    if (k.get('debitkarte') or {}).get('inkl'): f.append('dk')
    return ' '.join(f)
def item(k,P,base,voll=True,extra=None,rank=None):
    pr=PROFIL[k['art']]; ko=k['score']['kosten']
    st=lambda good,t: f'<b class="{"good" if good else ""}">{E(t)}</b>'
    kf='kostenlos' if k['kf_jahr']==0 else f'{eur(k["kf_jahr"])} € im Jahr'
    tags=f'<span class="tag typ">{E(ART[k["art"]])}</span>'+(f'<span class="tag kl">{CC["code"]}-IBAN</span>' if k.get('iban')==CC['code'] else f'<span class="tag out">{E(k.get("iban") or "")}-IBAN</span>' if k.get('iban') else '')+f'<span class="tag out">{E(wegT(k).capitalize())}</span>'
    rn=rank or k['rank']
    rank=f'<span class="rank r{rn}">{rn}</span>' if rn<=3 else f'<span class="rank">{rn}</span>'
    akt=f'<div class="earn"><span>Aktion</span><b>{E(k["aktion"])}</b></div>' if k.get('aktion') else ''
    return f'''<article class="item" id="gk-{k["slug"]}" data-k='{E(json.dumps(jsdata(k),separators=(",",":")))}' data-f="{flags(k)}" data-art="{k["art"]}" data-cost="{ko["total"]}" data-q="{E((k["bank"]+" "+k["name"]).lower())}">
    <div class="ihead"><div style="display:flex;gap:10px;align-items:center">{rank}</div></div>
    <div class="irow">{face(k)}<div style="min-width:0"><h3 class="iname">{E(k["name"])}</h3><div class="iprov">{E(k["bank"])}</div>{starrow(k)}</div></div>
    <div class="tags">{tags}</div>
    <div class="stats"><div><small>Kontoführung regulär</small>{st(k["kf_jahr"]==0,kf)}</div><div><small>Günstiger, wenn</small>{st(bool(k.get("gratis")) or k["kf_jahr"]==0,kurzbed(k))}</div><div><small data-lbl>Deine Kosten im Jahr</small><b class="{"good" if ko["total"]==0 else ""}" data-out>{eur(ko["total"])} €</b></div></div>
    <p class="note" data-why style="margin:0">{E(why(k,ko,pr))}</p>
    {akt}
    <ul class="checks">{"".join(f"<li>{E(x)}</li>" for x in k["pros"][:4])}</ul>
    {f'<p class="note" style="margin:0"><b>{E(extra[0])}:</b> {E(extra[1])}</p>' if extra else ''}
    <div class="acts">{affiliate.btn(LAND,'girokonto',k['slug'],k.get('quelle2') or k['quelle'])}{"" if voll else f'<a class="btn ghost block" href="{P}{url(k)}">Alle Konditionen</a>'}</div>
    {mehr(k,P) if voll else ""}
  </article>'''
def url(k,land=None):
    """Adresse eines Kontos: Eintrag im Vergleich (eigene Kontoseiten gibt es nicht mehr)"""
    return f'{land or LAND}/girokonto/#gk-{k["slug"]}'
def mehr(k,P):
    """Aufklappbare Produktinfos im Listeneintrag: alle Konditionen, Kostenbeispiel, Vor- und Nachteile, Quelle"""
    gp=k['geprueft']; pc,kc=k['pros'],k['cons']
    pq=f'<a class="lnk" href="{E(k["quelle"])}" target="_blank" rel="noopener">{"Entgeltinformation" if "pdf" in k["quelle"].lower() else "Preise"} {E(k["bank"])} ↗</a>'
    return f'''<details class="more"><summary>Alle Konditionen</summary><div class="more-b">
    <div class="pc"><div class="box pro"><h4>Das spricht dafür</h4>{'<ul class="checks">'+"".join(f"<li>{E(x)}</li>" for x in pc)+'</ul>' if pc else '<p class="note">Keine bestätigten Vorteile.</p>'}</div>
    <div class="box con"><h4>Das spricht dagegen</h4>{'<ul class="checks neg">'+"".join(f"<li>{E(x)}</li>" for x in kc)+'</ul>' if kc else '<p class="note">Keine bekannten Nachteile.</p>'}</div></div>
    {cond_html(k)}
    <h4>Was kostet das Konto im Jahr?</h4>{beispiele(k)}
    <p class="src">Quelle: {pq}{f" (Stand {dmy(k['stand'])})" if k.get("stand") else ""} · geprüft am {dmy(gp)}. Bewertung {de1(k["stars"])} von 5, <a class="lnk" href="{P}{LAND}/girokonto/methodik/">so entstehen die Sterne</a>. Fehler gefunden? <a href="mailto:hallo@finvallo.com?subject=Korrektur%20{E(k['slug'])}">Schreib uns</a>.</p>
  </div></details>'''
def why(k,ko,pr):
    t=f'Gerechnet mit {eur(pr["ein"])} € Geldeingang pro Monat, {pr["alter"]} Jahren und {pr["abh"]} Abhebungen pro Monat'
    bits=[]
    if ko['kf']: bits.append(f'Kontoführung {eur(ko["kf"])} €')
    if ko['card']: bits.append(f'Debitkarte {eur(ko["card"])} €')
    if ko['cash']: bits.append(f'Abhebungen {eur(ko["cash"])} €')
    return t+(': '+', '.join(bits) if bits else '')+'.'

def cond_html(k):
    r=lambda a,b: f'<div class="r"><span>{a}</span><span>{b}</span></div>'
    na='<span class="mut na">keine Angabe</span>'; v=lambda x: E(x) if x not in (None,'') else na
    g=k.get('gratis'); dk=k.get('debitkarte') or {}; b=k.get('bargeld') or {}
    o='<div class="cond" style="margin-bottom:14px"><div class="gh">Kosten</div>'
    o+=r('Kontoführung regulär',E(kfT(k))+(f' <small class="mut">({eur(k["kf_jahr"])} € im Jahr)</small>' if k['kf_periode']!='Jahr' and k['kf_jahr'] else ''))
    o+=r('Günstiger, wenn',E(g['text']) if g else ('kostenlos ohne Bedingung' if k['kf_jahr']==0 else 'kein Gratis-Modell'))
    if g and g.get('sonst'): o+=r('Weitere Bedingungen',E(g['sonst']))
    o+=r('Debitkarte',v(dk.get('text')))
    o+=r('Kreditkarte',('ohne Aufpreis: ' if k.get('kreditkarte_inkl') else '')+E(k['kreditkarte']) if k.get('kreditkarte') else 'nicht dabei')
    if k.get('einzelposten'): o+=r('Extra-Kosten je Buchung',E(k['einzelposten']))
    if k.get('hinweis'): o+=r('Hinweis',E(k['hinweis']))
    if k.get('aktion'): o+=r('Aktion',E(k['aktion']))
    o+='</div><div class="cond" style="margin-bottom:14px"><div class="gh">Bargeld und Ausland</div>'
    o+=r('Bargeld am Automaten',v(b.get('text')))+r('Bargeld außerhalb des Euroraums',v(b.get('ausland')))+r('Kartenzahlung in Fremdwährung',E(fwT(k)) if k.get('fremdwaehrung_prozent') is not None else na)
    o+='</div><div class="cond" style="margin-bottom:14px"><div class="gh">Zinsen</div>'
    o+=r('Eingeräumte Überziehung',E(zinsT(k.get('sollzins'))) if k.get('sollzins') is not None else ('nicht möglich' if k.get('kein_dispo') else na))
    o+=r('Überschreitung',E(zinsT(k.get('ueberschreitung'))) if k.get('ueberschreitung') is not None else na)
    o+=r('Zinsen auf Guthaben',E(zinsT(k.get('habenzins'))) if k.get('habenzins') is not None else na)
    o+='</div><div class="cond" style="margin-bottom:14px"><div class="gh">Konto und Bank</div>'
    a=k.get('alter') or {}
    o+=r('Kontoart',E(ART[k['art']]))+(r('Wer kann es eröffnen',E(a['text'])) if a.get('text') else '')
    o+=r('Eröffnung',E(wegT(k)))+r('IBAN',E(ibanT(k)))+r('Gemeinschaftskonto',{True:'möglich',False:'nicht möglich'}.get(k.get('gemeinschaftskonto'),'keine Angabe'))
    o+=r('Einlagensicherung',v(k.get('einlagensicherung')))
    return o+'</div>'
def beispiele(k):
    rows=[]
    for ein in (0,500,1000,1500,2500):
        alt=PROFIL[k['art']]['alter']; ko=kosten(k,ein,alt,4)
        rows.append(f'<tr><td>{eur(ein)} €</td><td>{eur(ko["kf"])} €</td><td>{eur(ko["card"]+ko["cash"])} €</td><td><b>{eur(ko["total"])} €</b></td></tr>')
    return f'<div class="tbl"><table><thead><tr><th>Geldeingang pro Monat</th><th>Kontoführung</th><th>Karte und Abhebungen</th><th>Im Jahr</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div><p class="note">Mit {PROFIL[k["art"]]["alter"]} Jahren und 4 Abhebungen am Automaten pro Monat. Nicht enthalten: Überziehungszinsen, Buchungen am Schalter und Leistungen, die du extra bestellst.</p>'
def head(t,d,rel,P,ld): return K.head(t,d,rel,P,ld)
def hdr(P,rel):
    o='de' if LAND=='at' else 'at'; rest=rel.split('/',1)[1]
    sl=rest.split('/')[1] if rest.startswith('girokonto/') and rest.count('/')>=2 else ''
    if not OTHER.get(o): other=f'{o}/'
    elif sl and sl not in ('methodik','bestenlisten') and sl not in OTHER[o]: other=f'{o}/girokonto/'
    elif sl=='bestenlisten' and rest.count('/')>=3 and not os.path.exists(R+f'{o}/{rest}index.html'): other=f'{o}/girokonto/bestenlisten/'   # Liste gibt es im anderen Land nicht
    else: other=f'{o}/{rest}'
    return K.HDR(P,rel,other)

BLG={}
def calcbox():
    return '''<div class="box lcalc" id="gcalc" hidden>
    <h2 style="margin-top:0">Was kostet das Konto dich?</h2>
    <p class="note" style="margin:0 0 10px">Trag deine Zahlen ein. Wir prüfen bei jedem Konto die Gratis-Bedingung und rechnen die Kosten für ein Jahr.</p>
    <div class="lgrid"><label><span class="flab">Geldeingang pro Monat (€)</span><input type="number" min="0" step="100" value="1500" data-in="ein" name="ein"></label>
    <label><span class="flab">Dein Alter</span><input type="number" min="0" max="120" value="35" data-in="alter" name="alter"></label>
    <label><span class="flab">Abhebungen am Automaten pro Monat</span><input type="number" min="0" max="60" value="4" data-in="abh" name="abh"></label></div>
    <p class="note" style="margin:8px 0 0">Gehalt oder Pension zählt bei allen Banken als Geldeingang. Manche Banken zählen nur Gehalt oder Pension, das steht beim Konto.</p>
  </div>'''
def filterbox(n):
    chips=[('gratis','Kostenlos ohne Bedingung'),('bedingt','Gratis mit Bedingung'),('landiban',CC['iban_pro']),('filiale','Mit Filiale'),('online','Online eröffnen'),('kk','Kreditkarte ohne Aufpreis'),('gem','Gemeinschaftskonto')]
    opt=lambda xs:''.join(f'<option value="{v}">{t}</option>' for v,t in xs)
    return f'''<div class="box filt" id="filt" hidden>
    <label class="fq"><span class="sr">Suche</span><input type="search" data-q placeholder="Konto oder Bank suchen" autocomplete="off"></label>
    <div class="chips">{"".join(f'<button type="button" class="chip" data-flag="{a}" aria-pressed="false">{t}</button>' for a,t in chips)}</div>
    <div class="frow"><select data-art aria-label="Kontoart">{opt([("","Alle Kontoarten")]+[(a,t) for a,t,_ in SEK])}</select>
    <select data-sort aria-label="Sortierung">{opt([("rank","Nach Bewertung"),("cost","Günstigste für dich zuerst"),("name","Nach Name")])}</select></div>
    <div class="fbot"><b data-count>{n} Konten</b><button type="button" class="lnk" data-reset hidden>Filter zurücksetzen</button></div>
  </div>'''

def list_page(ks,secs,d):
    rel=f'{LAND}/girokonto/'; P='../../'; n=len(ks); nb=len({k['bank'] for k in ks})
    N=CC['N']
    t=f'Girokonto-Vergleich {N} 2026: Kosten und Bewertung | Finvallo'
    ds=f'{n} Girokonten von {nb} überregionalen Banken in {N} verglichen: Kontoführung, Gratis-Bedingungen, Karten, Bargeld und Zinsen. Mit Kostenrechner.'
    top=secs['standard'][:10]
    ld=K.graph(rel,t,ds,[(CC['N'],f'{LAND}/'),('Girokonten',rel)],[{"@type":"ItemList","name":f"Beste Girokonten {N}","itemListElement":[{"@type":"ListItem","position":k['rank'],"name":f'{k["name"]} ({k["bank"]})',"url":f"https://finvallo.com/{url(k)}"} for k in top]}])
    sections=''
    for a,h,txt in SEK:
        xs=secs[a]
        if not xs: continue
        txt=sektxt(a,txt)
        sections+=f'<section class="gsec" data-sec="{a}"><h2>{h} <small class="mut">({len(xs)})</small></h2>{f"<p class=note>{E(txt)}</p>" if txt else ""}<div class="list">{"".join(item(k,P,"") for k in xs)}</div></section>'
    top1=secs['standard'][0]; gratis=[k for k in secs['standard'] if k['kf_jahr']==0]; st=dmy(max(k['geprueft'] for k in ks))
    kurz=(f'<b>Kurz gesagt:</b> Platz 1 ist das {E(top1["name"])} von {E(top1["bank"])} mit {de1(top1["stars"])} von 5 Sternen. {len(gratis)} der {len(secs["standard"])} Konten für alle sind ohne Bedingung kostenlos'
          +(f', weitere {sum(1 for k in secs["standard"] if k["kf_jahr"]>0 and k.get("gratis") and k["gratis"].get("kf_bedingt")==0)} mit Gehaltseingang oder Altersgrenze' if any(k["kf_jahr"]>0 and k.get("gratis") and k["gratis"].get("kf_bedingt")==0 for k in secs["standard"]) else '')+f'. Stand: {st}.')
    fq=[(f'Welches Girokonto ist in {N} das beste?',f'Laut Finvallo-Bewertung liegt das {top1["name"]} von {top1["bank"]} mit {de1(top1["stars"])} von 5 Sternen vorn. Die Bewertung rechnet mit einem typischen Fall ({eur(PROFIL["standard"]["ein"])} € Geldeingang, {PROFIL["standard"]["abh"]} Abhebungen pro Monat); mit deinen Zahlen kann ein anderes Konto besser passen. Stand: {st}.'),
        ('Welche Girokonten sind wirklich kostenlos?',f'{len(gratis)} Konten für alle kosten ohne Bedingung nichts'+(f', zum Beispiel {K.fmtl([k["name"]+" ("+k["bank"]+")" for k in gratis[:3]])}' if gratis else '')+'. Bei vielen anderen entfällt die Kontoführung ab einem monatlichen Geldeingang oder bis zu einem bestimmten Alter. Karte und Abhebungen können trotzdem extra kosten; das steht bei jedem Konto.'),
        ('Wie wechsle ich das Girokonto?','Mit dem gesetzlichen Kontowechsel-Service: Die neue Bank holt Daueraufträge, Lastschriften und Gehaltszahlungen von der alten Bank, du musst nur zustimmen. Wie das genau läuft, steht im Ratgeber „Konto wechseln“.')]
    ld['@graph'].append({"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in fq]})
    body=f'''{hdr(P,rel)}
<div class="wrap"><main id="app">
<div class="crumb"><span>{N} › Girokonten</span><span class="ok">✓ Geprüft bis {st}</span></div>
<h1>Girokonto-Vergleich {N}</h1>
  <p class="lede">{n} Girokonten von {nb} Banken, die überall in {N} Kundinnen und Kunden annehmen. Jede Zahl stammt aus der Entgeltinformation oder Preisliste der Bank. Sortiert nach unserer Bewertung, Provisionen haben keinen Einfluss.</p>
  <div class="facts prose"><p>{kurz}</p></div>
  <p class="note" style="margin:6px 0 14px">Bestenlisten: {" · ".join(f'<a class="lnk" href="bestenlisten/{c["k"]}/">{E(c["t"])}</a>' for c in gcats() if BLG.get(c["k"]))}{rgline(P,"<br>")}</p>
  {f'<p class="note">Geld, das du länger nicht brauchst, bringt auf dem Girokonto kaum Zinsen. Was du für feste Laufzeiten bekommst, zeigt der <a class="lnk" href="{P}{LAND}/festgeld/">Festgeld-Vergleich {N}</a>.</p>' if os.path.exists(R+f'{LAND}/festgeld/index.html') else ''}
  {calcbox()}
  {filterbox(n)}
  <details class="box howscore"><summary><span><b>So entstehen die Sterne</b><br><small>6 Kriterien, feste Regeln, offene Gewichtung</small></span><span class="lnk">anzeigen</span></summary>
    <div class="wbars">{"".join(f'<div class="wbar"><span>{a}</span><span class="t"><i style="width:{w*2.5}%"></i></span><em>{w} %</em></div>' for a,w in W)}</div>
    <p class="note">Die Kosten rechnen wir für einen typischen Fall: bei Konten für alle mit 1.500 € Gehalt pro Monat und 4 Abhebungen pro Monat. Jedes Kriterium bekommt nach festen Regeln 1 bis 5 Sterne, die Gesamtnote ist der gewichtete Durchschnitt. Fehlende Angaben zählen mit 2,5 Sternen. Studenten-, Jugend-, Kinder- und Basiskonten stehen in eigenen Listen.</p>
    <a class="lnk" href="methodik/">Alle Regeln →</a></details>
  {sections}
  <h2>Was in den Vergleich kommt</h2><div class="prose"><p>Konten, die man von überall in {N} eröffnen kann und deren Guthaben über eine gesetzliche Einlagensicherung geschützt ist. {CC["regional"]}</p>{CC["extern"]}</div>
  <h2>Fragen und Antworten</h2><div class="faq">{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q,a in fq)}</div>
  <p class="note" style="margin-top:18px">Die Daten gibt es offen als <a class="lnk" href="../daten/girokonten.json">JSON</a>, frei nutzbar mit Quellenangabe. Zinsen für Geld, das länger liegen kann: <a class="lnk" href="{P}{LAND}/festgeld/">Festgeld-Vergleich {N}</a>.</p>
</main>
{K.footer(P)}'''
    v=__import__('hashlib').sha256(open(R+'assets/giro.js','rb').read()).hexdigest()[:8]
    body=body.replace('</body>',f'<script src="{P}assets/giro.js?v={v}" defer></script>\n</body>',1)
    K.write(rel,head(t,ds,rel,P,ld)+body)

def methodik_page(ks):
    rel=f'{LAND}/girokonto/methodik/'; P='../../../'
    t=f'So bewerten wir Girokonten in {CC["N"]} | Finvallo'
    d='Die Regeln hinter den Sternen im Girokonto-Vergleich: 6 Kriterien, Gewichtung, Rechnung der Jahreskosten und Umgang mit fehlenden Daten.'
    ld=K.graph(rel,t,d,[(CC['N'],f'{LAND}/'),('Girokonten',f'{LAND}/girokonto/'),('So bewerten wir',rel)])
    rows=[('Kosten',40,'Jahreskosten im typischen Fall: Kontoführung, Debitkarte, wenn sie extra kostet, und Abhebungen über die Gratis-Menge. 0 € = 5 Sterne, bis 30 € = 4,6, bis 50 € = 4,2, bis 80 € = 3,8, bis 120 € = 3,2, bis 180 € = 2,6, bis 250 € = 2,0, darüber 1,5.'),
          ('Bedingungen',10,'Wie leicht du den günstigen Preis bekommst. Gleicher Preis für alle = 5 Sterne. Gratis ab bis zu 500 € Eingang = 4,5, bis 1.000 € = 4,0, bis 1.500 € = 3,5, darüber 2,5. Bedingungen mit Alter oder Ausbildung = 4,0. Kein Gratis-Modell = 3,0. Gilt der Gratis-Preis nur für Neukunden oder nur mit Zustimmung zu Werbung, gibt es 0,5 Sterne weniger.'),
          ('Bargeld',15,'Abhebungen am Automaten ohne Entgelt = 5 Sterne. Begrenzte Gratis-Menge: ab 5 pro Monat 4,0, ab 2 pro Monat 3,0, 1 pro Monat 2,5, jede Abhebung kostet 2,0.'),
          ('Karten',10,'Debitkarte inklusive = 3,5 Sterne. Gibt es dazu eine Kreditkarte gegen Aufpreis oder nur im 1. Jahr gratis = 4,0. Kreditkarte ohne Aufpreis dabei = 5,0. Debitkarte kostet extra = 2,0.'),
          ('Zinsen',10,'Zins für die Überziehung (bei zwei Sätzen der höhere): bis 7 % = 5 Sterne, bis 9 % = 4,0, bis 11 % = 3,0, bis 13 % = 2,5, darüber 2,0. Ab 1 % Zinsen auf Guthaben gibt es 0,5 Sterne dazu. Ohne Überziehung 3,0.'),
          ('Alltag &amp; Service',15,f'2 Sterne als Basis, je 1 Stern mehr für {CC["iban_a"]}, für Online-Eröffnung und für Filialen.')]
    tb=''.join(f'<tr><td><b>{a}</b></td><td>{w} %</td><td>{E(x)}</td></tr>' for a,w,x in rows)
    body=f'''{hdr(P,rel)}
<div class="wrap"><main id="app">
<h1>So bewerten wir Girokonten</h1>
<p class="lede">Jedes Konto bekommt in 6 Kriterien 1 bis 5 Sterne nach festen Regeln. Die Gesamtnote ist der gewichtete Durchschnitt. Provisionen spielen keine Rolle.</p>
<div class="tbl wide"><table><thead><tr><th>Kriterium</th><th>Gewicht</th><th>Regel</th></tr></thead><tbody>{tb}</tbody></table></div>
<h2>Welcher Fall zählt für die Kosten?</h2><div class="prose"><p>Konten für alle rechnen wir mit 1.500 € Gehalt pro Monat, 35 Jahren und 4 Abhebungen pro Monat. Studentenkonten mit 500 € Eingang und 22 Jahren, Jugendkonten mit 16 Jahren und 2 Abhebungen, Kinderkonten mit 10 Jahren und 1 Abhebung, Basiskonten ohne Einkommen. Mit deinen eigenen Zahlen rechnest du in der Liste.</p>
<p>Nicht in den Kosten: Überziehungszinsen, Buchungen am Schalter, Überweisungen auf Papier und befristete Aktionen. Aktionen zeigen wir beim Konto, sie zählen nicht in die Sterne.</p></div>
<h2>Fehlende Daten</h2><div class="prose"><p>Steht eine Angabe nicht in den Unterlagen der Bank, schreiben wir „keine Angabe“. Das Kriterium zählt dann mit 2,5 Sternen, damit fehlende Daten keinen Vorteil bringen.</p></div>
<h2>Warum keine Sterne für Sicherheit?</h2><div class="prose"><p>Alle Konten im Vergleich sind über eine gesetzliche Einlagensicherung in der EU bis 100.000 € pro Person und Bank geschützt. Das unterscheidet sie nicht, deshalb gibt es dafür keine Sterne. Konten ohne Einlagensicherung nehmen wir nicht auf.</p></div>
<p><a class="lnk" href="../">← Zum Girokonto-Vergleich</a></p>
</main>
{K.footer(P)}'''
    K.write(rel,head(t,d,rel,P,ld)+body)

def export(ks,d):
    os.makedirs(R+f'{LAND}/daten',exist_ok=True)
    keys=['slug','bank','name','art','kf_betrag','kf_periode','kf_jahr','gratis','alter','debitkarte','kreditkarte','kreditkarte_inkl','bargeld','fremdwaehrung_prozent','sollzins','ueberschreitung','habenzins','einzelposten','eroeffnung','iban','einlagensicherung','gemeinschaftskonto','aktion','quelle','quelle2','stand','geprueft','stars','rank']
    out={'quelle':f'https://finvallo.com/{LAND}/girokonto/','stand':d['stand'],'anzahl':len(ks),'lizenz':'Frei nutzbar mit Quellenangabe Finvallo','konten':[{x:k.get(x) for x in keys} for k in ks]}
    open(R+f'{LAND}/daten/girokonten.json','w').write(json.dumps(out,ensure_ascii=False,indent=1))

# ---------- Bestenlisten ----------
# Aufbau wie bei großen Vergleichsportalen: je Thema eine Seite mit Rangliste der passenden Konten,
# den besten drei im Detail, Erklärtext zum Thema und eigenen Fragen. Ein Konto kann in mehreren Listen stehen.
# Erklärtexte je Land: giro_listen_texte_*.py, Funktion texte(land, ctx) -> {slug: {'lede','secs','faq'}}.
ALLE=('standard','premium')
NEO={'de':{'N26','bunq','Revolut','Tomorrow','Trade Republic','C24'},'at':{'N26','bunq','Revolut','Tomorrow','Trade Republic'}}
DIREKT={'de':{'1822direkt','comdirect','Consorsbank','DKB','ING','norisbank','Openbank','Deutsche Skatbank'},'at':{'easybank','DADAT Bank','Bank Direkt','DKB'}}
def frei(k): return k['kf_jahr']==0 or (bool(k.get('gratis')) and k['gratis'].get('kf_bedingt')==0)
def altT(k):
    a=k.get('alter') or {}
    if a.get('min') is not None and a.get('max') is not None: return f'{a["min"]}-{a["max"]} Jahre'
    if a.get('max') is not None: return f'bis {a["max"]} Jahre'
    if a.get('min') is not None: return f'ab {a["min"]} Jahren'
    return 'keine Angabe'
def ukT(k):
    n=k.get('unterkonten')
    t=k.get('unterkonten_text') or (f'bis zu {n} Unterkonten' if isinstance(n,int) and n>1 else 'Unterkonten möglich')
    return t+(', jeweils mit eigener IBAN' if k.get('unterkonten_iban') and 'IBAN' not in t else '')
def _std(k): return (-k['stars'],k['score']['kosten']['total'],k['bank'].lower(),k['name'].lower())
def bonT(): return 'Schufa' if LAND=='de' else 'KSV1870'
def gcats():
    """Themenlisten je Land. f = wer in die Liste kommt, why = Kurzinfo je Konto zum Thema, sort = Reihenfolge."""
    L=LAND; bon=bonT()
    return [
 dict(k='kostenlos',t='Kostenlos',h='Kostenlose Girokonten',d=f'Konten für alle, bei denen die Kontoführung nichts kostet: entweder ohne Bedingung oder sobald eine Bedingung wie ein monatlicher Geldeingang erfüllt ist.',
      f=lambda k:k['art']=='standard' and frei(k),why=('Gratis, wenn',kurzbed)),
 dict(k='ohne-geldeingang',t='Gratis ohne Geldeingang',h='Gratis-Girokonten ohne Geldeingang',d='Konten, die ganz ohne Bedingung nichts kosten: kein Mindestgeldeingang, keine Altersgrenze, keine Aktivität nötig.',
      f=lambda k:k['art']=='standard' and k['kf_jahr']==0,why=('Debitkarte',lambda k:(k.get('debitkarte') or {}).get('text') or 'keine Angabe')),
 dict(k='unterkonten',t='Mit Unterkonten',h='Girokonten mit Unterkonten',d='Konten, zu denen du weitere Unterkonten oder Spaces anlegen kannst, etwa für Miete, Urlaub oder Rücklagen. Bei manchen hat jedes Unterkonto eine eigene IBAN.',
      f=lambda k:k['art'] in ALLE and (k.get('unterkonten') or 0)>=1,why=('Unterkonten',ukT)),
 dict(k='mit-kreditkarte',t='Mit Kreditkarte',h='Girokonten mit Kreditkarte',d='Konten, bei denen eine echte Kreditkarte ohne Aufpreis dabei ist.',
      f=lambda k:k['art'] in ALLE and bool(k.get('kreditkarte_inkl')),why=('Kreditkarte',lambda k:k.get('kreditkarte') or 'inklusive')),
 dict(k='praemie',t='Mit Prämie',h='Girokonten mit Prämie',d='Konten, für die die Bank neuen Kundinnen und Kunden gerade eine Prämie oder einen Bonus zahlt. Die Prämie zählt nicht in die Sterne, sie steht hier nur nach Höhe sortiert.',
      f=lambda k:k['art'] in ALLE+('student',) and bool(k.get('aktion')),why=('Prämie',lambda k:k['aktion']),sort=lambda k:(-(k.get('aktion_eur') or 0),)+_std(k)),
 dict(k='ohne-schufa' if L=='de' else 'ohne-ksv',t=f'Ohne {bon}-Abfrage',h=f'Girokonten ohne {bon}-Abfrage',d=f'Konten, bei denen die Bank laut eigenen Angaben bei der Eröffnung keine Auskunft bei der {bon} einholt.',
      f=lambda k:k['art'] in ALLE+('student',) and k.get('bonitaet')=='keine',why=('Bei der Eröffnung',lambda k:k.get('bonitaet_text') or f'keine {bon}-Abfrage')),
 dict(k='direktbanken',t='Direktbanken',h='Direktbanken im Vergleich',d='Banken ohne eigenes Filialnetz, bei denen du alles online, per App oder am Telefon erledigst. Gemeint sind etablierte Direktbanken, die reinen App-Banken stehen bei den Neobanken.',
      f=lambda k:k['art'] in ALLE and k['bank'] in DIREKT[L],why=('Gratis, wenn',kurzbed)),
 dict(k='neobanken',t='Neobanken',h='Neobanken im Vergleich',d='Junge Banken, die vor allem über das Smartphone funktionieren: Konto in Minuten eröffnet, alles in der App, oft mit Unterkonten und Echtzeit-Benachrichtigungen.',
      f=lambda k:k['art'] in ALLE and k['bank'] in NEO[L],why=('Gratis, wenn',kurzbed)),
 dict(k='nachhaltige-banken',t='Nachhaltige Banken',h='Girokonten bei nachhaltigen Banken',d='Konten bei Banken, die das Geld ihrer Kundschaft nach festen sozialen und ökologischen Regeln verleihen und anlegen.',
      f=lambda k:k['art'] in ALLE+('student',) and bool(k['_bank'].get('nachhaltig')),why=('Nachhaltigkeit',lambda k:k['_bank'].get('kurz') or k['_bank'].get('text') or 'nachhaltige Bank')),
 dict(k='gemeinschaftskonto',t='Gemeinschaftskonto',h='Gemeinschaftskonten im Vergleich',d='Konten für alle, die die Bank auch als gemeinsames Konto für zwei Personen anbietet.',
      f=lambda k:k['art'] in ALLE and k.get('gemeinschaftskonto') is True,why=('Gratis, wenn',kurzbed)),
 dict(k='studenten',t='Studierende',h='Girokonten für Studierende',d='Konten für Studierende, Azubis und junge Erwachsene bis zu einer Altersgrenze. Danach stellt die Bank meist auf ein normales Konto um.',
      f=lambda k:k['art']=='student',why=('Alter',altT)),
 dict(k='kinder-jugendkonto',t='Kinder und Jugendliche',h='Kinder- und Jugendkonten',d='Konten, die Eltern für ihre Kinder eröffnen, und Konten für Jugendliche, meist ab 10 oder 14 Jahren.',
      f=lambda k:k['art'] in ('kinder','jugend'),why=('Alter',altT)),
    ]
GCATS=[]
def best_lists(ks):
    out={}
    for c in gcats():
        xs=sorted([k for k in ks if c['f'](k)],key=c.get('sort') or _std)
        out[c['k']]=xs if len(xs)>=3 else []
    return out
def best_tag(k,BL):
    """Beste Platzierung eines Kontos in einer Bestenliste (nur Platz 1 bis 3)."""
    hits=[(BL[c['k']].index(k),c) for c in gcats() if k in BL.get(c['k'],[])[:3]]
    if not hits: return None
    i,c=min(hits,key=lambda x:x[0]); return i+1,c

def listen_ctx(land=None,ks=None,BL=None):
    """Alles, was ein Text-Modul für seine Seite braucht. Zahlen in Texten immer hieraus nehmen, nie fest schreiben."""
    global LAND,CC
    land=land or LAND
    if ks is None:
        old=(LAND,CC); LAND,CC=land,CFG[land]; K.use(land); _,ks=load(land); rate(ks); BL=best_lists(ks); LAND,CC=old
    P='../../../../'; G=f'{P}{land}/girokonto/'
    def link(k,label=None): return f'<a class="lnk" href="{G}#gk-{k["slug"]}">{E(label or k["name"])}</a> <small class="mut">({E(k["bank"])})</small>'
    def liste(slug,label): return f'<a class="lnk" href="{G}bestenlisten/{slug}/">{E(label)}</a>'
    def rg(slug,label): return f'<a class="lnk" href="{P}{land}/ratgeber/{slug}/">{E(label)}</a>' if os.path.exists(R+f'{land}/ratgeber/{slug}/index.html') else E(label)
    return dict(land=land,N=CFG[land]['N'],code=CFG[land]['code'],P=P,G=G,lists=BL,alle=ks,eur=eur,pct=pct,kfT=kfT,kurzbed=kurzbed,altT=altT,ukT=ukT,
                link=link,liste=liste,rg=rg,stand=dmy(max(k.get('geprueft') or k.get('stand') for k in ks)),bon=('Schufa' if land=='de' else 'KSV1870'))
def texte(land,ctx):
    out={}
    for m in ('giro_listen_texte_a','giro_listen_texte_b','giro_listen_texte_c'):
        try: mod=__import__(m)
        except ImportError: continue
        out.update(mod.texte(land,ctx) or {})
    return out

def top3(X,c,P):
    """Die besten drei im Detail: aus den Konditionen, keine Textbausteine"""
    o=''
    for i,k in enumerate(X[:3]):
        g=k.get('gratis'); dk=(k.get('debitkarte') or {}).get('text'); b=(k.get('bargeld') or {}).get('text')
        bits=[f'Die Kontoführung kostet {kfT(k)}'+(f'; {g["text"][0].lower()+g["text"][1:].rstrip(".")}' if g and g.get('text') else '')+'.']
        if dk: bits.append(f'Karte: {dk.rstrip(".")}.')
        if b: bits.append(f'Bargeld: {b.rstrip(".")}.')
        w=c['why'][1](k)
        if c['why'][0] not in ('Gratis, wenn',): bits.append(f'{c["why"][0]}: {w.rstrip(".")}.')
        pc=k['pros'][:3]; kc=k['cons'][:2]
        o+=(f'<div class="box" style="margin-bottom:12px"><h3 style="margin-top:0">{i+1}. {E(k["name"])} <small class="mut">von {E(k["bank"])}</small></h3>'
            f'<div style="margin:-4px 0 8px">{K.stars(k["stars"])} <b>{de1(k["stars"])}</b> <span class="mut">{k["note"]}</span></div>'
            f'<p style="margin:0 0 10px">{E(" ".join(bits))}</p>'
            +(f'<ul class="checks">{"".join(f"<li>{E(x)}</li>" for x in pc)}</ul>' if pc else '')
            +(f'<ul class="checks neg" style="margin-top:8px">{"".join(f"<li>{E(x)}</li>" for x in kc)}</ul>' if kc else '')
            +f'<p class="note" style="margin:10px 0 0"><a class="lnk" href="{P}{url(k)}">Alle Konditionen im Vergleich →</a></p></div>')
    return o

def bestenlisten(ks,BL):
    N=CC['N']; base=f'{LAND}/girokonto/bestenlisten/'; S=dmy(max(k['geprueft'] for k in ks))
    cats=[c for c in gcats() if BL.get(c['k'])]
    ctx=listen_ctx(LAND,ks,BL); TX=texte(LAND,ctx)
    tiles=''.join(f'<a class="catcard" href="{c["k"]}/"><span class="ct">{E(c["t"])}</span><b>{E(BL[c["k"]][0]["name"])} ({E(BL[c["k"]][0]["bank"])})</b><span>{K.stars(BL[c["k"]][0]["stars"])} {de1(BL[c["k"]][0]["stars"])}</span><small>{len(BL[c["k"]])} Konten · Liste ansehen →</small></a>' for c in cats)
    P='../../../'
    t=f'Girokonten {N} 2026: alle Bestenlisten | Finvallo'
    d=f'Girokonten in {N} nach Thema: kostenlos, ohne Geldeingang, mit Unterkonten, mit Kreditkarte, Direkt- und Neobanken, für Studierende, Kinder und Paare.'
    d=K.fit_desc(d) if hasattr(K,'fit_desc') else d[:155]
    ld=K.graph(base,t,d,[(CC['N'],f'{LAND}/'),('Girokonten',f'{LAND}/girokonto/'),('Bestenlisten',base)],[{"@type":"ItemList","name":f"Bestenlisten Girokonten {N}","itemListElement":[{"@type":"ListItem","position":i+1,"name":c['h'],"url":f"https://finvallo.com/{base}{c['k']}/"} for i,c in enumerate(cats)]}])
    K.write(base,head(t,d,base,P,ld)+f'''{hdr(P,base)}
<div class="wrap"><main id="app">
<div class="crumb"><span><a href="../">Girokonten</a> › Bestenlisten</span><span>Stand {S}</span></div>
<h1>Girokonten in {N} nach Thema</h1><p class="lede">Nicht jedes Konto passt zu jedem. Hier findest du die besten Konten für deinen Fall, jeweils mit Rangliste, den besten drei im Detail und allem, worauf es bei diesem Thema ankommt. Stand: {S}.</p>
<div class="catgrid">{tiles}</div>
<h2>Wie entstehen die Listen?</h2><div class="prose"><p>Jede Liste zeigt nur Konten, die eine klare Bedingung erfüllen, etwa „Kontoführung ohne Bedingung kostenlos“ oder „Unterkonten möglich“. Innerhalb der Liste zählt dieselbe Note wie im <a href="../">Girokonto-Vergleich</a>, nur bei den Prämien sortieren wir nach der Höhe der Prämie. Wie die Note entsteht, steht in der <a href="../methodik/">Methodik</a>.</p></div>
</main>
{K.footer(P)}''')
    nav=lambda kk:''.join(f'<a class="chip" href="../{c["k"]}/" aria-pressed="{"true" if c["k"]==kk else "false"}" style="text-decoration:none">{E(c["t"])}</a>' for c in cats)
    for c in cats:
        X=BL[c['k']]; rel=f'{base}{c["k"]}/'; P2='../../../../'; top=X[0]; T=TX.get(c['k']) or {}
        h1=f'{c["h"]} in {N}'
        t=f'{c["h"]} in {N} 2026 | Finvallo'
        if len(t)>62: t=f'{c["h"]} ({LAND.upper()}) 2026 | Finvallo'
        if len(t)>62: t=f'{c["h"]} | Finvallo'
        d=f'{c["h"]} in {N}: {len(X)} Konten im Vergleich, Platz 1 ist das {top["name"]} von {top["bank"]}. Mit allen Kosten und Bedingungen, Stand {S}.'
        if len(d)>155: d=f'{c["h"]} in {N}: {len(X)} Konten, Platz 1 {top["name"]} ({top["bank"]}). Stand {S}.'
        if len(d)>155: d=f'{c["h"]} in {N}: {len(X)} Konten im Vergleich, Stand {S}.'
        kurz=f'<b>Kurz gesagt:</b> {"Die höchste Prämie" if c["k"]=="praemie" else "Platz 1"} hat laut Finvallo das {E(top["name"])} von {E(top["bank"])}'+(f' ({de1(top["stars"])} von 5 Sternen)' if c['k']!='praemie' else f': {E(top["aktion"])}')+(f', vor dem {E(X[1]["name"])} von {E(X[1]["bank"])}' if len(X)>1 else '')+(f' und dem {E(X[2]["name"])} von {E(X[2]["bank"])}' if len(X)>2 else '')+f'. {len(X)} Konten in dieser Liste. Stand: {S}.'
        fq=[(f'Welches Konto ist in {N} am besten in der Liste „{c["t"]}“?',f'Laut Finvallo-Bewertung liegt das {top["name"]} von {top["bank"]} vorn, mit {de1(top["stars"])} von 5 Sternen. Stand: {S}.' if c['k']!='praemie' else f'Die höchste Prämie zahlt aktuell {top["bank"]} für das {top["name"]}: {top["aktion"]}. Stand: {S}.')]+list(T.get('faq') or [])
        items=''.join(item(k,P2,'',voll=False,extra=(c['why'][0],c['why'][1](k)),rank=i+1) for i,k in enumerate(X))
        secs=''.join(f'<h2>{E(h)}</h2>{x if x.lstrip().startswith("<") else "<div class=prose><p>"+x+"</p></div>"}' for h,x in (T.get('secs') or []))
        ld=K.graph(rel,t,d,[(CC['N'],f'{LAND}/'),('Girokonten',f'{LAND}/girokonto/'),('Bestenlisten',base),(c['t'],rel)],
            [{"@type":"ItemList","name":h1,"numberOfItems":len(X),"itemListElement":[{"@type":"ListItem","position":i+1,"name":f'{k["name"]} ({k["bank"]})',"url":f"https://finvallo.com/{url(k)}"} for i,k in enumerate(X)]},
             {"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":re.sub(r'<[^>]+>','',a)}} for q,a in fq]}])
        K.write(rel,head(t,d,rel,P2,ld)+f'''{hdr(P2,rel)}
<div class="wrap"><main id="app">
<div class="crumb"><span><a href="../../">Girokonten</a> › <a href="../">Bestenlisten</a> › {E(c["t"])}</span><span>Stand {S}</span></div><h1>{E(h1)}</h1><p class="lede">{T.get("lede") or E(c["d"])}</p>
<div class="facts prose"><p>{kurz}</p></div>
<div class="chips" style="margin:14px 0">{nav(c["k"])}</div>
<h2>Die {len(X)} Konten im Vergleich</h2>
<div class="list">{items}</div>
<p class="note" style="margin-top:8px">{"Sortiert nach Höhe der Prämie, bei gleicher Prämie nach Bewertung." if c["k"]=="praemie" else "Sortiert nach unserer Bewertung, bei gleicher Note steht das günstigere Konto vorn."} Mit deinen eigenen Zahlen rechnest du im <a class="lnk" href="../../">Girokonto-Vergleich</a>.</p>
<h2>Die besten drei im Detail</h2>{top3(X,c,P2)}
{secs}
<h2>Fragen und Antworten</h2><div class="faq">{"".join(f"<details><summary>{E(q)}</summary><p>{a}</p></details>" for q,a in fq)}</div>
<p class="note" style="margin-top:18px"><a class="lnk" href="../../">Zum Girokonto-Vergleich mit Rechner →</a> · <a class="lnk" href="../../methodik/">So bewerten wir →</a></p>
{rgline(P2,"P","</p>")}
</main>
{K.footer(P2)}''')

# ---------- Anbieterseiten der Kreditkarten: Abschnitt „Girokonten von …“ ----------
def anb_rel(bank):
    sl=CC['anb'].get(bank) or K.slug(bank)
    return f'{LAND}/kreditkarten/anbieter/{sl}/' if sl and os.path.exists(R+f'{LAND}/kreditkarten/anbieter/{sl}/index.html') else None
def anbieter_giro(ks):
    by={}
    for k in ks: by.setdefault(k['bank'],[]).append(k)
    for bank,xs in by.items():
        rel=anb_rel(bank)
        if not rel: continue
        f=R+rel+'index.html'; s=open(f,encoding='utf-8').read()
        s=re.sub(r'<!--giro-->.*?<!--/giro-->','',s,flags=re.S)
        xs=sorted(xs,key=lambda k:(-k['stars'],k['kf_jahr']))
        rows=''.join(f'<tr><td><a class="lnk" href="../../../girokonto/#gk-{k["slug"]}">{E(k["name"])}</a><br><small class="mut">{E(ART[k["art"]])}</small></td><td>{E(kfT(k))}</td><td>{E(kurzbed(k))}</td><td style="white-space:nowrap">{de1(k["stars"])} ★</td></tr>' for k in xs)
        blk=(f'<!--giro--><h2>Girokonten von {E(bank)}</h2><p class="note">{len(xs)} {"Konto" if len(xs)==1 else "Konten"} von {E(bank)} in unserem <a class="lnk" href="../../../girokonto/">Girokonto-Vergleich</a>, bewertet nach eigenen Regeln für Girokonten.</p>'
             f'<div class="tbl wide"><table><thead><tr><th>Konto</th><th>Kontoführung</th><th>Günstiger, wenn</th><th>Bewertung</th></tr></thead><tbody>{rows}</tbody></table></div><!--/giro-->')
        for mk in ('<h2>Für wen passt','<h2>Fragen und Antworten</h2>','</main>'):
            if mk in s: s=s.replace(mk,blk+mk,1); break
        open(f,'w',encoding='utf-8').write(s)

def llms(secs,d):
    """Abschnitt „<Land>: Girokonten“ in llms.txt und llms-full.txt (ersetzt den alten Abschnitt)."""
    N=CC['N']
    st='.'.join(reversed(d['stand'].split('-')))
    for fn in ('llms.txt','llms-full.txt'):
        p=R+fn
        if not os.path.exists(p): continue
        t=open(p,encoding='utf-8').read()
        t=re.sub(r'\n## '+N+r': Girokonten\n(?:- [^\n]*\n?)*','\n',t)
        n=sum(len(v) for v in secs.values())
        b=f'\n## {N}: Girokonten\n- [Girokonto-Vergleich {N}](https://finvallo.com/{LAND}/girokonto/): {n} Konten von Banken mit Angebot in ganz {N}, Jahreskosten selbst rechnen, Stand {st}\n- [Bestenlisten Girokonten {N}](https://finvallo.com/{LAND}/girokonto/bestenlisten/): {", ".join(c["t"] for c in gcats())}\n- [So bewerten wir Girokonten](https://finvallo.com/{LAND}/girokonto/methodik/)\n- [Daten als JSON](https://finvallo.com/{LAND}/daten/girokonten.json)\n'
        for a,h,_ in SEK:
            xs=secs.get(a) or []
            if fn=='llms.txt': xs=xs[:5 if a=='standard' else 2]
            b+=''.join(f'- [{k["name"]} ({k["bank"]})](https://finvallo.com/{url(k)}): {h}, {de1(k["stars"])}/5, {eur(kosten(k,PROFIL[k["art"]]["ein"],PROFIL[k["art"]]["alter"],PROFIL[k["art"]]["abh"])["total"])} € im Jahr im Beispiel\n' for k in xs)
        i=t.find(CC['llms_vor']); t=t[:i]+b+t[i:] if i>=0 else t.rstrip()+'\n'+b
        open(p,'w',encoding='utf-8').write(re.sub(r'\n{3,}','\n\n',t))

def rgline(P,pre,post=''):
    if not CC['rg']: return ''
    return ('<p class="note">' if pre=='P' else pre)+'Ratgeber: '+' · '.join(f'<a class="lnk" href="{P}{LAND}/ratgeber/{a}/">{E(b)}</a>' for a,b in CC['rg'])+post
def main():
    global LAND,CC
    for l in CFG:
        if os.path.exists(dpath(l)): OTHER[l]={k.get('slug') or K.slug(k['bank']+' '+k['name']) for k in json.load(open(dpath(l)))['konten']}
    for l in CFG:
        if l not in OTHER: continue
        LAND,CC=l,CFG[l]; build_land()
    LAND,CC='at',CFG['at']
def build_land():
    K.use(LAND)
    d,ks=load()
    K.L.setdefault('stand',d['stand'])
    for k in ks: k.setdefault('geprueft',d['stand'])
    secs=rate(ks); n={a:len(v) for a,v in secs.items()}
    BL=best_lists(ks); BLG.clear(); BLG.update(BL)
    import shutil
    for x in os.listdir(R+f'{LAND}/girokonto') if os.path.isdir(R+f'{LAND}/girokonto') else []:
        if x not in ('bestenlisten','methodik') and os.path.isdir(R+f'{LAND}/girokonto/{x}'): shutil.rmtree(R+f'{LAND}/girokonto/{x}')
    bestenlisten(ks,BL); anbieter_giro(ks)
    list_page(ks,secs,d); methodik_page(ks); export(ks,d); llms(secs,d)
    print('Girokonten:',len(ks))

if __name__=='__main__': main()
