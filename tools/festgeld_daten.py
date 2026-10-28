# Festgeld: führt die Recherche-Dateien (festgeld-recherche/<GRUPPE>.json) zu den Daten je Land zusammen.
# Ergebnis: daten/<land>/festgeld.json (Angebote + nicht aufgenommen), daten/<land>/festgeld.csv (eine Zeile je Angebot und Laufzeit),
# daten/festgeld-laender.json (Einlagensicherung und Länderrating je Sitzland). Prüft Pflichtfelder und meldet Fehler.
# Aufruf: python3 tools/festgeld_daten.py   (danach festgeld.py bauen)
import csv,glob,json,os,re,sys
SP=os.path.dirname(os.path.abspath(__file__)); RD=os.path.join(SP,'festgeld-recherche'); DD=os.path.join(SP,'daten')
# Redaktionell nicht aufgenommen: id -> Grund
AUS={'opel-direktbank-festgeld-de':'Marke der Stellantis Bank mit denselben Konditionen; steht als Stellantis Bank im Vergleich.',
     'garantibank-kleeblatt-festgeld-de':'Die Bank-Website war bei der Prüfung nicht abrufbar; ohne Konditionen aus erster Hand nehmen wir das Angebot nicht auf.',
     'bigbank-festgeld-at':'Die Bank-Website war bei der Prüfung nicht abrufbar; ohne Konditionen aus erster Hand nehmen wir das Angebot nicht auf.'}
# Gründe in der öffentlichen Liste „nicht aufgenommen“: redaktionell neu formuliert (Name -> Grund)
GRUND={'Bank11direkt':'Website bei der Prüfung nicht erreichbar, keine Konditionen aus erster Hand.',
       'DKB Festgeld':'Die DKB nennt auf ihrer Website keine Annahme von Kundinnen und Kunden mit Wohnsitz in Österreich.',
       'AutoBank AG':'Website bei der Prüfung nicht erreichbar, keine aktuellen Konditionen aus erster Hand.',
       'Hello bank! (BNP Paribas S.A. Niederlassung Österreich)':'Kein Festgeld-Angebot gefunden.',
       'durchblicker.at (Sparzinsen)':'Vergleichsportal ohne eigenen Abschluss.',
       'My Money Bank':'Festgeld nur über Raisin, dort im Vergleich.'}
# Bankschlüssel: dieselbe Bank auf mehreren Wegen (direkt, Raisin, CHECK24, ZinsMarkt) bekommt denselben Schlüssel und Anzeigenamen
ALIAS={'ca-savings':'ca-consumer-finance','credit-agricole-savings':'ca-consumer-finance','pbb-direkt':'deutsche-pfandbriefbank','olb-bank':'olb','urbo':'urbo-bankas',
       'embank':'european-merchant-bank','rietumu-banka':'rietumu-bank','ca-auto-bank-s-p-a-niederlassung-deutschland':'ca-auto-bank','postbank':'postbank'}
RECHT=r'\b(ag|gmbh|plc|p\.l\.c\.?|s\.?a\.?|s\.?p\.?a\.?|a\.?s\.?|ab|as|uab|ead|publ|eg|n\.?v\.?|jsc|sucursal en españa|zweigniederlassung.*|niederlassung.*|branch.*|\(.*?\))\b'
def bank_key(a):
    if a.get('bank','').lower().startswith('postbank'): return 'postbank'
    s=(a.get('institut') or a['bank']).lower().replace('“','').replace('”','').replace('"','')
    s=re.sub(RECHT,'',s); k=slug(s)
    return ALIAS.get(k,k)
def bank_kurz(xs):
    """kürzester Markenname je Schlüssel, ohne Rechtsform"""
    out={}
    for a in xs:
        n=a['bank'].strip().rstrip(',').strip()
        n=re.sub(r'\s*,?\s*(S\.?A\.?,?\s*)?(Sucursal en España|Zweigniederlassung.*|Niederlassung.*|Branch.*)$','',n,flags=re.I).strip()
        n=re.sub(r'^(AB|AS|UAB|JSC)\s+','',n)
        for _ in range(2): n=re.sub(r'\s*,?\s+(AG|GmbH|plc|Plc|p\.l\.c\.?|S\.?A\.?|S\.?p\.?A\.?|A\.?S\.?|AB|AS|ASA|AD|EAD|UAB|eG|N\.?V\.?|Limited|Ltd\.?|d\.d\.)(\s*\(publ\))?\s*$','',n).strip().rstrip(',')
        k=a['bank_key']
        if k not in out or len(n)<len(out[k]): out[k]=n
    return out
MIN_ZINS=0.3   # Zinsstufen darunter sind Platzhalter der Plattform für geschlossene Laufzeiten
MIN_ANLAGE=50  # Mindestanlagen darunter sind Datenfehler (z. B. 1 €)
# interne Vermerke der Recherche (Aufteilung auf Gruppen, Dubletten, 0-%-Laufzeiten) nicht veröffentlichen
INTERN=re.compile(r'Gruppe|API|aufgenommen als|0,00–|laut Vorgaben|Teaser|Auftrag|nicht doppelt|Dublette|0,00 %|identisch mit|\((?:dort )?erfasst|\berfasst\)|unter diesem Namen erfasst|dort im Vergleich|, (?:dieses|das) ist erfasst|sind erfasst|\(erfasst\)|erfasst als')
def clean(t):
    if not t: return t
    t=t.replace('Kund:innen','Kundinnen und Kunden')
    t=re.sub(r'\s*\((?:HTTP|Verbindungs|TLS|Proxy)[^)]*\)','',t)
    ss=[x for x in re.split(r'(?<=[.;])\s+',t) if not re.search(r'HTTP|automatisierte Abrufe|gegengeprüft|manuell|[Ss]ekundärquelle|[Cc]apitalo|Vergleichsportal',x)]
    return ' '.join(ss).strip() or None

ZZ={'jaehrlich','endfaellig','monatlich','quartalsweise','halbjaehrlich','wahlweise'}
KD={'nein','ja','ja_mit_abschlag'}; VL={'automatisch','keine','wahlweise'}

def slug(s):
    s=s.lower().replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss').replace('&','und')
    return re.sub(r'[^a-z0-9]+','-',s).strip('-')
def num(x):
    if x is None or isinstance(x,(int,float)): return x
    try: return float(str(x).replace('.','').replace(',','.')) if re.search(r',\d',str(x)) else float(x)
    except ValueError: return None

def check(a,fehler):
    w=lambda t: fehler.append(f'{a.get("id")}: {t}')
    for f in ('id','markt','bank','produkt','vertrieb','sitz','zinsen','quelle'):
        if not a.get(f): w(f'Pflichtfeld {f} fehlt')
    if a.get('markt') not in ('de','at'): w(f'markt {a.get("markt")!r}')
    if a.get('zinszahlung') not in ZZ|{None}: w(f'zinszahlung {a.get("zinszahlung")!r}')
    if a.get('kuendigung') not in KD|{None}: w(f'kuendigung {a.get("kuendigung")!r}')
    if a.get('verlaengerung') not in VL|{None}: w(f'verlaengerung {a.get("verlaengerung")!r}')
    for z in a.get('zinsen') or []:
        if not isinstance(z.get('monate'),(int,float)) or not isinstance(z.get('zins'),(int,float)): w(f'Zinszeile kaputt: {z}')
        elif not 0<z['zins']<10: w(f'Zins unplausibel: {z}')
        elif not 0<z['monate']<=240: w(f'Laufzeit unplausibel: {z}')

def norm(a):
    a['id']=slug(a['id']); a['sitz']=(a.get('sitz') or '').upper()[:2]
    for f in ('min_anlage','max_anlage'): a[f]=num(a.get(f))
    zs=[]
    for z in a.get('zinsen') or []:
        z={'monate':num(z.get('monate')),'zins':num(z.get('zins')),'min':num(z.get('min')),'max':num(z.get('max'))}
        if isinstance(z['monate'],float) and z['monate'].is_integer(): z['monate']=int(z['monate'])
        zs.append(z)
    # Platzhalter-Zinsen (0,01 %) sind keine Angebote
    tot=[z for z in zs if (z['zins'] or 0)<MIN_ZINS]
    if tot:
        zs=[z for z in zs if z not in tot]
        a['hinweis']=((a.get('hinweis') or '')+' Einzelne Laufzeiten führt die Bank nur mit einem Platzhalterzins; sie fehlen hier.').strip()
    if a.get('min_anlage') is not None and num(a['min_anlage'])<MIN_ANLAGE: a['min_anlage']=None
    # Laufzeiten in Wochen (Recherche: 0,25 Monate je Woche) passen nicht in die Monatsrechnung: weglassen, im Hinweis nennen
    wo=[z for z in zs if z['monate'] is not None and z['monate']!=int(z['monate'])]
    if wo:
        zs=[z for z in zs if z not in wo]
        a['hinweis']=((a.get('hinweis') or '')+' Zusätzlich Laufzeiten in Wochen, die wir nicht vergleichen.').strip()
    a['zinsen']=sorted(zs,key=lambda z:(z['monate'] or 0,z['min'] or 0))
    a['es']=a.get('einlagensicherung') or {}
    a['hinweis']=clean(a.get('hinweis'))
    a.setdefault('sek',[]); a.setdefault('status','ok')
    v=a.get('vertrieb') or ''
    a['vertrieb']='direkt' if v.lower()=='direkt' else v
    return a

def main():
    fehler=[]; angebote={}; raus={'de':[],'at':[]}; gruppen={}
    for p in sorted(glob.glob(os.path.join(RD,'*.json'))):
        n=os.path.basename(p)[:-5]
        if n=='laender': continue
        d=json.load(open(p,encoding='utf-8'))
        if n.endswith('-nicht-aufgenommen'):
            for x in d:
                if x['name'] in GRUND: x['grund']=GRUND[x['name']]
                elif INTERN.search(x['grund']): continue
                x['grund']=clean(x['grund']) or 'Keine prüfbaren Konditionen.'
                raus[x.get('markt') if x.get('markt') in raus else 'de' if n.startswith('DE') else 'at'].append({'name':x['name'],'grund':x['grund'],'gruppe':n.split('-')[0]})
            continue
        gruppen[n]=len(d)
        for a in d:
            a=norm(a); a['gruppe']=n
            if a['status']!='ok':
                raus[a.get('markt','de')].append({'name':f'{a["bank"]} {a["produkt"]}','grund':a.get('hinweis') or 'kein Neugeschäft','gruppe':n}); continue
            if a['id'] in AUS:
                raus[a['markt']].append({'name':f'{a["bank"]} {a["produkt"]}','grund':AUS[a['id']],'gruppe':n}); continue
            if not a['sitz']:
                raus[a.get('markt','de')].append({'name':f'{a["bank"]} {a["produkt"]}','grund':'Die Bank nennt nicht, bei welcher Einlagenbank das Geld liegt; Einlagensicherung damit nicht prüfbar.','gruppe':n}); continue
            if not a.get('zinsen'):
                raus[a['markt']].append({'name':f'{a["bank"]} {a["produkt"]}','grund':'Alle Laufzeiten nur mit Platzhalterzins, faktisch kein Angebot.','gruppe':n}); continue
            check(a,fehler)
            a['bank_key']=bank_key(a)
            k=a['id']
            if k in angebote:
                # gleiche ID aus zwei Gruppen: das jüngere Prüfdatum gewinnt
                if (a.get('geprueft') or '')<=(angebote[k].get('geprueft') or ''): continue
            angebote[k]=a
    laender={}
    lp=os.path.join(RD,'laender.json')
    if os.path.exists(lp): laender=json.load(open(lp,encoding='utf-8'))
    for a in angebote.values():
        if a['sitz'] and a['sitz'] not in laender: fehler.append(f'{a["id"]}: Sitzland {a["sitz"]} fehlt in laender.json')
    json.dump(laender,open(os.path.join(DD,'festgeld-laender.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
    for land in ('de','at'):
        xs=sorted([a for a in angebote.values() if a['markt']==land],key=lambda a:(a['bank'].lower(),a['produkt'].lower(),a['vertrieb']))
        if not xs: continue
        for a in xs: a.pop('es',None)
        kurz=bank_kurz(xs)
        for a in xs: a['bank']=kurz[a['bank_key']]
        # Slug der Bankseite aus dem kurzen Namen; bei Namensgleichheit verschiedener Institute der Schlüssel
        seen={}
        for k,n in kurz.items(): seen.setdefault(slug(n),[]).append(k)
        for a in xs:
            sl=slug(a['bank']); a['bank_slug']=sl if len(seen[sl])==1 else a['bank_key']
        stand=max(a.get('geprueft') or a.get('stand') or '' for a in xs)
        os.makedirs(os.path.join(DD,land),exist_ok=True)
        json.dump({'land':land,'stand':stand,'angebote':xs,'nicht_aufgenommen':raus[land]},open(os.path.join(DD,land,'festgeld.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
        with open(os.path.join(DD,land,'festgeld.csv'),'w',newline='',encoding='utf-8') as f:
            cw=csv.writer(f,delimiter=';')
            cw.writerow(['id','bank','produkt','vertrieb','sitz','laufzeit_monate','zins_pa','betrag_min','betrag_max','min_anlage','max_anlage','zinszahlung','zinseszins','steuer_auto','kuendigung','verlaengerung','neukunden_only','stand','geprueft','quelle'])
            for a in xs:
                for z in a['zinsen']:
                    cw.writerow([a['id'],a['bank'],a['produkt'],a['vertrieb'],a['sitz'],z['monate'],z['zins'],z['min'],z['max'],a.get('min_anlage'),a.get('max_anlage'),a.get('zinszahlung'),a.get('zinseszins'),a.get('steuer_auto'),a.get('kuendigung'),a.get('verlaengerung'),a.get('neukunden_only'),a.get('stand'),a.get('geprueft'),a.get('quelle')])
        print(f'{land}: {len(xs)} Angebote, {len(raus[land])} nicht aufgenommen, Stand {stand}')
    print('Gruppen:',', '.join(f'{k} {v}' for k,v in gruppen.items()))
    if fehler:
        print(f'{len(fehler)} Hinweise:'); print('\n'.join(fehler[:80]))
    return 1 if any('Pflichtfeld' in x or 'kaputt' in x for x in fehler) else 0

if __name__=='__main__': sys.exit(main())
