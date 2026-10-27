# Girokonto-Vergleich Österreich: Liste mit Filtern und persönlicher Rechnung, Kontoseiten, Methodik.
# Daten: daten/at/girokonten.json (jede Zahl aus der Entgeltinformation oder Preisliste der Bank, mit Quelle und Prüfdatum).
# Rechenlogik für die Jahreskosten gibt es zweimal: kosten() hier und calc() in public/assets/giro.js.
# check.py vergleicht beide (tools/giro-kontrolle.js). Läuft nach karten.py, vor header.py.
import json,os,re,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import karten as K
from score import eur,pct

E=K.E; dmy=K.dmy; de1=K.de1; R=K.R; SP=K.SP
LAND='at'
DP=os.path.join(SP,'daten',LAND,'girokonten.json')
ART={'standard':'Gehalts- und Privatkonto','premium':'Premiumkonto','student':'Studenten- und U28-Konto','jugend':'Jugendkonto','kinder':'Kinderkonto','basis':'Basiskonto'}
SEK=[('standard','Konten für alle',None),('student','Für Studierende und junge Erwachsene','Für Studierende, Menschen in Ausbildung oder bis zu einem bestimmten Alter. Danach stellt die Bank auf ein normales Konto um, das meist etwas kostet.'),
     ('jugend','Jugendkonten','Für Jugendliche, meist ab 14 Jahren. Danach stellt die Bank auf ein normales Konto um.'),
     ('kinder','Kinderkonten','Für Kinder unter 14 Jahren. Eröffnen können nur die Eltern oder andere gesetzliche Vertreter.'),
     ('basis','Basiskonten','Das gesetzliche Zahlungskonto mit grundlegenden Funktionen. Jede Bank muss es jedem Menschen mit rechtmäßigem Aufenthalt in der EU anbieten, auch ohne Einkommen und trotz Schulden. Es kostet höchstens 80 € im Jahr, für besonders schutzbedürftige Menschen höchstens 40 €.')]
# Standardfall für die Liste: so rechnen wir, bis du eigene Zahlen eingibst
PROFIL={'standard':dict(ein=1500,alter=35,abh=4),'premium':dict(ein=1500,alter=35,abh=4),'student':dict(ein=500,alter=22,abh=4),
        'jugend':dict(ein=0,alter=16,abh=2),'kinder':dict(ein=0,alter=10,abh=1),'basis':dict(ein=0,alter=35,abh=4)}
W=[('Kosten',40),('Bedingungen',10),('Bargeld',15),('Karten',10),('Zinsen',10),('Alltag &amp; Service',15)]

def load():
    d=json.load(open(DP)); ks=[k for k in d['konten'] if k.get('aufnehmen',True)]
    for k in ks:
        k.setdefault('slug',K.slug(k['bank']+' '+k['name']))
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
    if not g: return '–'
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
    if k.get('kreditkarte_inkl'): p.append('Kreditkarte inklusive: '+k['kreditkarte_inkl'])
    b=k.get('bargeld') or {}
    if b.get('frei_monat') is None and b.get('danach_eur') is None and re.search(r'kostenlos|inklusive|gratis|0 €',b.get('text') or '',re.I) and not re.search(r'nur|bis|ab ',b.get('text') or ''): p.append('Bargeld am Automaten kostenlos')
    if k.get('iban')=='AT': p.append('Österreichische IBAN')
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
    if k.get('iban') and k['iban']!='AT': c.append('Keine österreichische IBAN')
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
        vk=('Debitkarte inklusive' if dk.get('inkl') else 'Debitkarte kostet extra')+(', Kreditkarte inklusive' if k.get('kreditkarte_inkl') else ''); okk=True
    parts.append(dict(k='Karten',w=10,s=sk,v=vk,ok=okk))
    z=k.get('ueberschreitung') or k.get('sollzins')
    if z is None:
        sz,vz,okz=(3.0,'keine Überziehung möglich',True) if k.get('kein_dispo') else (2.5,'nicht bestätigt',False)
    else:
        sz=5.0 if z<=7 else 4.0 if z<=9 else 3.0 if z<=11 else 2.5 if z<=13 else 2.0; vz=f'Überziehung {pct(z)}'; okz=True
        if (k.get('habenzins') or 0)>=1: sz=min(5.0,sz+0.5); vz+=f', Guthaben {pct(k["habenzins"])}'
    parts.append(dict(k='Zinsen',w=10,s=sz,v=vz,ok=okz))
    ss=2.0+(1 if k.get('iban')=='AT' else 0)+(1 if k.get('eroeffnung') in ('online','beides') else 0)+(1 if k.get('eroeffnung') in ('filiale','beides') else 0)
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
    if k.get('iban')=='AT': f.append('atiban')
    if k.get('eroeffnung') in ('filiale','beides'): f.append('filiale')
    if k.get('eroeffnung') in ('online','beides'): f.append('online')
    if k.get('kreditkarte_inkl'): f.append('kk')
    if k.get('gemeinschaftskonto'): f.append('gem')
    if (k.get('debitkarte') or {}).get('inkl'): f.append('dk')
    return ' '.join(f)
def item(k,P,base):
    pr=PROFIL[k['art']]; ko=k['score']['kosten']
    st=lambda good,t: f'<b class="{"good" if good else ""}">{E(t)}</b>'
    kf='kostenlos' if k['kf_jahr']==0 else f'{eur(k["kf_jahr"])} € im Jahr'
    tags=f'<span class="tag typ">{E(ART[k["art"]])}</span>'+('<span class="tag kl">AT-IBAN</span>' if k.get('iban')=='AT' else f'<span class="tag out">{E(k.get("iban") or "")}-IBAN</span>' if k.get('iban') else '')+f'<span class="tag out">{E(wegT(k).capitalize())}</span>'
    rank=f'<span class="rank r{k["rank"]}">{k["rank"]}</span>' if k['rank']<=3 else f'<span class="rank">{k["rank"]}</span>'
    akt=f'<div class="earn"><span>Aktion</span><b>{E(k["aktion"])}</b></div>' if k.get('aktion') else ''
    return f'''<article class="item" id="gk-{k["slug"]}" data-k='{E(json.dumps(jsdata(k),separators=(",",":")))}' data-f="{flags(k)}" data-art="{k["art"]}" data-cost="{ko["total"]}" data-q="{E((k["bank"]+" "+k["name"]).lower())}">
    <div class="ihead"><div style="display:flex;gap:10px;align-items:center">{rank}</div></div>
    <div class="irow">{face(k)}<div style="min-width:0"><h3 class="iname"><a href="{base}{k["slug"]}/">{E(k["name"])}</a></h3><div class="iprov">{E(k["bank"])}</div>{starrow(k)}</div></div>
    <div class="tags">{tags}</div>
    <div class="stats"><div><small>Kontoführung regulär</small>{st(k["kf_jahr"]==0,kf)}</div><div><small>Günstiger, wenn</small>{st(bool(k.get("gratis")) or k["kf_jahr"]==0,kurzbed(k))}</div><div><small data-lbl>Deine Kosten im Jahr</small><b class="{"good" if ko["total"]==0 else ""}" data-out>{eur(ko["total"])} €</b></div></div>
    <p class="note" data-why style="margin:0">{E(why(k,ko,pr))}</p>
    {akt}
    <ul class="checks">{"".join(f"<li>{E(x)}</li>" for x in k["pros"][:4])}</ul>
    <div class="acts"><a class="btn primary block" href="{E(k.get("quelle2") or k["quelle"])}" target="_blank" rel="noopener">Zur Bank ↗</a><a class="btn ghost block" href="{base}{k["slug"]}/">Details ansehen</a></div>
  </article>'''
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
    o+=r('Kreditkarte inklusive',E(k['kreditkarte_inkl']) if k.get('kreditkarte_inkl') else 'nein')
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
def scorebox(k,P):
    s=k['score']
    rows=''.join(f'<tr><td><b>{p["k"]}</b><br><small class="mut">{E(p["v"])}</small></td><td>{p["w"]} %</td><td style="white-space:nowrap">{K.stars(p["s"])} {de1(p["s"])}</td></tr>' for p in s['parts'])
    gap=[p['k'] for p in s['parts'] if not p['ok']]
    gt=f'<p class="note" style="margin:0 0 10px"><b>Datenlücke:</b> Daten fehlen bei {K.fmtl(gap)}. {"Dieses Kriterium zählt" if len(gap)==1 else "Diese Kriterien zählen"} mit 2,5 Sternen.</p>' if gap else ''
    return f'''<div class="box"><div class="scorehead"><div class="big">{de1(k["stars"])}<small>/5</small></div><div>{K.stars(k["stars"])}<div style="margin-top:4px"><span class="badge ">{k["note"]}</span></div></div></div>
  <div class="tbl" style="margin:14px 0"><table class="sct"><thead><tr><th>Kriterium</th><th>Gewicht</th><th>Sterne</th></tr></thead><tbody>{rows}
  <tr><td><b>Gesamt</b><br><small class="mut">gewichteter Durchschnitt</small></td><td>100 %</td><td><b>{de1(k["stars"])}</b></td></tr></tbody></table></div>{gt}<a class="lnk" href="{P}{LAND}/girokonto/methodik/">ⓘ So funktioniert das Bewertungssystem</a></div>'''
def beispiele(k):
    rows=[]
    for ein in (0,500,1000,1500,2500):
        alt=PROFIL[k['art']]['alter']; ko=kosten(k,ein,alt,4)
        rows.append(f'<tr><td>{eur(ein)} €</td><td>{eur(ko["kf"])} €</td><td>{eur(ko["card"]+ko["cash"])} €</td><td><b>{eur(ko["total"])} €</b></td></tr>')
    return f'<div class="tbl"><table><thead><tr><th>Geldeingang pro Monat</th><th>Kontoführung</th><th>Karte und Abhebungen</th><th>Im Jahr</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div><p class="note">Mit {PROFIL[k["art"]]["alter"]} Jahren und 4 Abhebungen am Automaten pro Monat. Nicht enthalten: Überziehungszinsen, Buchungen am Schalter und Leistungen, die du extra bestellst.</p>'
def faq(k):
    g=k.get('gratis'); q=[]
    q.append((f'Was kostet das {k["name"]} von {k["bank"]}?',f'Die Kontoführung kostet regulär {kfT(k)}'+(f'. {g["text"].rstrip(".")}' if g else '')+'.'))
    if g: q.append(('Wann ist das Konto günstiger?',g['text']+(f' Weitere Bedingungen: {g["sonst"]}' if g.get('sonst') else '')))
    q.append(('Ist eine Debitkarte dabei?',(k.get('debitkarte') or {}).get('text') or 'Dazu haben wir keine bestätigte Angabe.'))
    q.append(('Kann ich das Konto online eröffnen?',{'online':'Ja, nur online.','filiale':'Nein, nur in der Filiale.','beides':'Ja, online oder in der Filiale.'}.get(k.get('eroeffnung'),'Dazu haben wir keine bestätigte Angabe.')))
    q.append(('Welche IBAN bekomme ich?',f'Eine {ibanT(k)}.' if k.get('iban') else 'Dazu haben wir keine bestätigte Angabe.'))
    if k.get('einlagensicherung'): q.append(('Wie sicher ist mein Geld?',f'Guthaben auf dem {k["name"]} von {k["bank"]} ist über die gesetzliche Einlagensicherung geschützt: {k["einlagensicherung"]}.'))
    return q

def head(t,d,rel,P,ld): return K.head(t,d,rel,P,ld)
def hdr(P,rel): return K.HDR(P,rel,'de/')

def konto_page(k,ks,n):
    rel=f'{LAND}/girokonto/{k["slug"]}/'; P='../../../'
    t=f'{k["name"]} ({k["bank"]}): Kosten und Bewertung | Finvallo'
    if len(t)>65: t=f'{k["name"]} {k["bank"]} | Finvallo'
    d=f'{k["name"]} von {k["bank"]}: Kontoführung {kfT(k)}'+(f', {kurzbed(k).lower()}' if k.get('gratis') else '')+f'. Bewertung {de1(k["stars"])}/5, alle Kosten mit Quelle.'
    d=K.fit_desc(d) if hasattr(K,'fit_desc') else d[:155]
    gp=k['geprueft']
    ld=K.graph(rel,t,d,[('Österreich',f'{LAND}/'),('Girokonten',f'{LAND}/girokonto/'),(k['name'],rel)],
        [{"@type":"BankAccount","@id":f"https://finvallo.com/{rel}#konto","name":f'{k["name"]} ({k["bank"]})',"url":f"https://finvallo.com/{rel}","provider":{"@type":"BankOrCreditUnion","name":k['bank']},
          "areaServed":{"@type":"Country","name":"Österreich"},"feesAndCommissionsSpecification":f'Kontoführung {kfT(k)}; {gratisT(k)}',
          "review":{"@type":"Review","@id":f"https://finvallo.com/{rel}#review","author":{"@id":"https://finvallo.com/ueber-uns/#haris"},"publisher":{"@id":"https://finvallo.com/#org"},"datePublished":gp,
                    "reviewRating":{"@type":"Rating","ratingValue":k['stars'],"bestRating":5,"worstRating":1}}},
         {"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq(k)]}],date=gp)
    sek=next(s for s in SEK if s[0]==('standard' if k['art']=='premium' else k['art']))
    glance=f'Das {k["name"]} ist ein {ART[k["art"]]} von {k["bank"]}. Die Kontoführung kostet regulär {kfT(k)}'+(f'. {k["gratis"]["text"].rstrip(".")}' if k.get('gratis') else '')+f'. Finvallo bewertet es mit {de1(k["stars"])} von 5 Sternen, Platz {k["rank"]} von {n[sek[0]]} in der Liste „{sek[1]}“. Stand: {dmy(gp)}.'
    sim=[x for x in ks if x is not k and (x['art']==k['art'] or {x['art'],k['art']}<={'standard','premium'})]
    sim.sort(key=lambda x:abs(x['score']['kosten']['total']-k['score']['kosten']['total'])); sim=sorted(sim[:4],key=lambda x:-x['stars'])
    simt=''.join(f'<tr><td><a class="lnk" href="../{x["slug"]}/">{E(x["name"])}</a><br><small class="mut">{E(x["bank"])}</small></td><td>{E(kfT(x))}</td><td>{E(kurzbed(x))}</td><td style="white-space:nowrap">{de1(x["stars"])} ★</td></tr>' for x in sim)
    pc,kc=k['pros'],k['cons']
    body=f'''{hdr(P,rel)}
<div class="wrap"><main id="app">
<div class="crumb"><span><a href="../">Girokonten</a> › {E(k["bank"])}</span><span class="ok">✓ Geprüft am {dmy(gp)}</span></div>
  <div class="dh">{face(k)}<div style="min-width:0"><div class="tags"><span class="tag typ">{E(ART[k["art"]])}</span><span class="by">von {E(k["bank"])}</span></div>
    <h1>{E(k["name"])}</h1>{starrow(k)}</div></div>
  <div class="box feebox"><small>Kontoführung</small><span class="big{" good" if k["kf_jahr"]==0 else ""}">{E(kfT(k))}</span>{f'<small class="mut">{E(k["gratis"]["text"])}</small>' if k.get("gratis") else ""}
    <a class="btn primary block" href="{E(k.get("quelle2") or k["quelle"])}" target="_blank" rel="noopener">Zur Bank ↗</a>
    <div class="actrow"><a class="plink" href="{E(k["quelle"])}" target="_blank" rel="noopener">{"Entgeltinformation (PDF) ↗" if k["quelle"].lower().split("?")[0].endswith(".pdf") else "Preise beim Anbieter ↗"}</a></div></div>
  <section class="facts box glance" aria-label="Auf einen Blick"><h2 style="margin-top:0">Auf einen Blick</h2><div class="prose"><p>{E(glance)}</p></div></section>
  <h2>Vorteile und Nachteile</h2>
  <div class="pc"><div class="box pro"><h3>Das spricht dafür</h3>{'<ul class="checks">'+"".join(f"<li>{E(x)}</li>" for x in pc)+'</ul>' if pc else '<p class="note">Keine bestätigten Vorteile.</p>'}</div>
  <div class="box con"><h3>Das spricht dagegen</h3>{'<ul class="checks neg">'+"".join(f"<li>{E(x)}</li>" for x in kc)+'</ul>' if kc else '<p class="note">Keine bekannten Nachteile.</p>'}</div></div>
  <h2>Konditionen im Überblick</h2><p class="source-line">Quelle: <a class="lnk" href="{E(k["quelle"])}" target="_blank" rel="noopener">{"Entgeltinformation" if "pdf" in k["quelle"].lower() else "Preise"}</a> {E(k["bank"])}{f" (Stand {dmy(k['stand'])})" if k.get("stand") else ""} · geprüft am {dmy(gp)}</p>{cond_html(k)}
  <h2>Was kostet das Konto im Jahr?</h2>{beispiele(k)}
  <h2>So kommt die Bewertung zustande</h2>{scorebox(k,P)}
  {f"<h2>Ähnliche Konten</h2><div class='tbl wide'><table><thead><tr><th>Konto</th><th>Kontoführung</th><th>Günstiger, wenn</th><th>Bewertung</th></tr></thead><tbody>{simt}</tbody></table></div>" if simt else ""}
  <h2>Fragen und Antworten</h2><div class="faq">{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q,a in faq(k))}</div>
  <p class="src" style="margin-top:18px">Quelle: {K.ext(k["quelle"])}{" · Produktseite: "+K.ext(k["quelle2"]) if k.get("quelle2") else ""}. Konditionen vor dem Abschluss bei der Bank prüfen.</p>
</main>
{K.footer(P)}'''
    K.write(rel,head(t,d,rel,P,ld)+body)

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
    chips=[('gratis','Kostenlos ohne Bedingung'),('bedingt','Gratis mit Bedingung'),('atiban','Österreichische IBAN'),('filiale','Mit Filiale'),('online','Online eröffnen'),('kk','Kreditkarte inklusive'),('gem','Gemeinschaftskonto')]
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
    t='Girokonto-Vergleich Österreich 2026: Kosten und Bewertung | Finvallo'
    ds=f'{n} Girokonten von {nb} überregionalen Banken in Österreich verglichen: Kontoführung, Gratis-Bedingungen, Karten, Bargeld und Zinsen. Mit Kostenrechner.'
    top=secs['standard'][:10]
    ld=K.graph(rel,t,ds,[('Österreich',f'{LAND}/'),('Girokonten',rel)],[{"@type":"ItemList","name":"Beste Girokonten Österreich","itemListElement":[{"@type":"ListItem","position":k['rank'],"name":f'{k["name"]} ({k["bank"]})',"url":f"https://finvallo.com/{rel}{k['slug']}/"} for k in top]}])
    sections=''
    for a,h,txt in SEK:
        xs=secs[a]
        if not xs: continue
        sections+=f'<section class="gsec" data-sec="{a}"><h2>{h} <small class="mut">({len(xs)})</small></h2>{f"<p class=note>{E(txt)}</p>" if txt else ""}<div class="list">{"".join(item(k,P,"") for k in xs)}</div></section>'
    raus=d.get('nicht_aufgenommen') or []
    rtxt=''.join(f'<li><b>{E(x["name"])}</b>: {E(x["grund"])}</li>' for x in raus)
    body=f'''{hdr(P,rel)}
<div class="wrap"><main id="app">
<h1>Girokonto-Vergleich Österreich</h1>
  <p class="lede">{n} Girokonten von {nb} Banken, die überall in Österreich Kundinnen und Kunden annehmen. Jede Zahl stammt aus der Entgeltinformation oder Preisliste der Bank. Sortiert nach unserer Bewertung, Provisionen haben keinen Einfluss.</p>
  {calcbox()}
  {filterbox(n)}
  <details class="box howscore"><summary><span><b>So entstehen die Sterne</b><br><small>6 Kriterien, feste Regeln, offene Gewichtung</small></span><span class="lnk">anzeigen</span></summary>
    <div class="wbars">{"".join(f'<div class="wbar"><span>{a}</span><span class="t"><i style="width:{w*2.5}%"></i></span><em>{w} %</em></div>' for a,w in W)}</div>
    <p class="note">Die Kosten rechnen wir für einen typischen Fall: bei Konten für alle mit 1.500 € Gehalt pro Monat und 4 Abhebungen pro Monat. Jedes Kriterium bekommt nach festen Regeln 1 bis 5 Sterne, die Gesamtnote ist der gewichtete Durchschnitt. Fehlende Angaben zählen mit 2,5 Sternen. Studenten-, Jugend-, Kinder- und Basiskonten stehen in eigenen Listen.</p>
    <a class="lnk" href="methodik/">Alle Regeln →</a></details>
  {sections}
  <h2>Welche Banken fehlen und warum?</h2><div class="prose"><p>Wir nehmen nur Konten auf, die man von überall in Österreich eröffnen kann und deren Guthaben über eine gesetzliche Einlagensicherung geschützt ist. Regionale Banken wie Sparkassen, Raiffeisenbanken, Volksbanken und Landes-Hypos haben je nach Bundesland eigene Preise. Sie fehlen deshalb, genauso wie E-Geld-Konten ohne Einlagensicherung.</p>{f"<ul>{rtxt}</ul>" if rtxt else ""}<p>Alle Konten in Österreich findest du im <a href="https://bankenrechner.arbeiterkammer.at/" target="_blank" rel="noopener">Bankenrechner der Arbeiterkammer ↗</a>.</p></div>
</main>
{K.footer(P)}'''
    v=__import__('hashlib').sha256(open(R+'assets/giro.js','rb').read()).hexdigest()[:8]
    body=body.replace('</body>',f'<script src="{P}assets/giro.js?v={v}" defer></script>\n</body>',1)
    K.write(rel,head(t,ds,rel,P,ld)+body)

def methodik_page(ks):
    rel=f'{LAND}/girokonto/methodik/'; P='../../../'
    t='So bewerten wir Girokonten in Österreich | Finvallo'
    d='Die Regeln hinter den Sternen im Girokonto-Vergleich: 6 Kriterien, Gewichtung, Rechnung der Jahreskosten und Umgang mit fehlenden Daten.'
    ld=K.graph(rel,t,d,[('Österreich',f'{LAND}/'),('Girokonten',f'{LAND}/girokonto/'),('So bewerten wir',rel)])
    rows=[('Kosten',40,'Jahreskosten im typischen Fall: Kontoführung, Debitkarte, wenn sie extra kostet, und Abhebungen über die Gratis-Menge. 0 € = 5 Sterne, bis 30 € = 4,6, bis 50 € = 4,2, bis 80 € = 3,8, bis 120 € = 3,2, bis 180 € = 2,6, bis 250 € = 2,0, darüber 1,5.'),
          ('Bedingungen',10,'Wie leicht du den günstigen Preis bekommst. Gleicher Preis für alle = 5 Sterne. Gratis ab bis zu 500 € Eingang = 4,5, bis 1.000 € = 4,0, bis 1.500 € = 3,5, darüber 2,5. Bedingungen mit Alter oder Ausbildung = 4,0. Kein Gratis-Modell = 3,0.'),
          ('Bargeld',15,'Abhebungen am Automaten ohne Entgelt = 5 Sterne. Begrenzte Gratis-Menge: ab 5 pro Monat 4,0, ab 2 pro Monat 3,0, 1 pro Monat 2,5, jede Abhebung kostet 2,0.'),
          ('Karten',10,'Debitkarte inklusive = 3,5 Sterne, mit Kreditkarte inklusive = 5,0, Debitkarte kostet extra = 2,0.'),
          ('Zinsen',10,'Zins für die Überziehung (bei zwei Sätzen der höhere): bis 7 % = 5 Sterne, bis 9 % = 4,0, bis 11 % = 3,0, bis 13 % = 2,5, darüber 2,0. Ab 1 % Zinsen auf Guthaben gibt es 0,5 Sterne dazu. Ohne Überziehung 3,0.'),
          ('Alltag &amp; Service',15,'2 Sterne als Basis, je 1 Stern mehr für eine österreichische IBAN, für Online-Eröffnung und für Filialen.')]
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
    keys=['slug','bank','name','art','kf_betrag','kf_periode','kf_jahr','gratis','alter','debitkarte','kreditkarte_inkl','bargeld','fremdwaehrung_prozent','sollzins','ueberschreitung','habenzins','einzelposten','eroeffnung','iban','einlagensicherung','gemeinschaftskonto','aktion','quelle','quelle2','stand','geprueft','stars','rank']
    out={'quelle':f'https://finvallo.com/{LAND}/girokonto/','stand':d['stand'],'anzahl':len(ks),'lizenz':'Frei nutzbar mit Quellenangabe Finvallo','konten':[{x:k.get(x) for x in keys} for k in ks]}
    open(R+f'{LAND}/daten/girokonten.json','w').write(json.dumps(out,ensure_ascii=False,indent=1))

def llms(secs,d):
    """Abschnitt „Österreich: Girokonten“ in llms.txt und llms-full.txt (ersetzt den alten Abschnitt)."""
    st='.'.join(reversed(d['stand'].split('-')))
    for fn in ('llms.txt','llms-full.txt'):
        p=R+fn
        if not os.path.exists(p): continue
        t=open(p,encoding='utf-8').read()
        t=re.sub(r'\n## Österreich: Girokonten\n(?:- [^\n]*\n?)*','\n',t)
        n=sum(len(v) for v in secs.values())
        b=f'\n## Österreich: Girokonten\n- [Girokonto-Vergleich Österreich](https://finvallo.com/at/girokonto/): {n} Konten von Banken mit Angebot in ganz Österreich, Jahreskosten selbst rechnen, Stand {st}\n- [So bewerten wir Girokonten](https://finvallo.com/at/girokonto/methodik/)\n- [Daten als JSON](https://finvallo.com/at/daten/girokonten.json)\n'
        for a,h,_ in SEK:
            xs=secs.get(a) or []
            if fn=='llms.txt': xs=xs[:5 if a=='standard' else 2]
            b+=''.join(f'- [{k["name"]} ({k["bank"]})](https://finvallo.com/at/girokonto/{k["slug"]}/): {h}, {de1(k["stars"])}/5, {eur(kosten(k,PROFIL[k["art"]]["ein"],PROFIL[k["art"]]["alter"],PROFIL[k["art"]]["abh"])["total"])} € im Jahr im Beispiel\n' for k in xs)
        i=t.find('\n## Deutschland: Kreditkarten'); t=t[:i]+b+t[i:] if i>=0 else t.rstrip()+'\n'+b
        open(p,'w',encoding='utf-8').write(re.sub(r'\n{3,}','\n\n',t))

def main():
    K.use(LAND)
    if not os.path.exists(DP): print('girokonten.json fehlt'); return
    d,ks=load()
    K.L.setdefault('stand',d['stand'])
    for k in ks: k.setdefault('geprueft',d['stand'])
    secs=rate(ks); n={a:len(v) for a,v in secs.items()}
    for k in ks: konto_page(k,ks,n)
    list_page(ks,secs,d); methodik_page(ks); export(ks,d); llms(secs,d)
    print('Girokonten:',len(ks))

if __name__=='__main__': main()
