# Festgeld: führt die Recherche-Dateien (festgeld-recherche/<GRUPPE>.json) zu den Daten je Land zusammen.
# Ergebnis: daten/<land>/festgeld.json (Angebote + nicht aufgenommen), daten/<land>/festgeld.csv (eine Zeile je Angebot und Laufzeit),
# daten/festgeld-laender.json (Einlagensicherung und Länderrating je Sitzland). Prüft Pflichtfelder und meldet Fehler.
# Aufruf: python3 tools/festgeld_daten.py   (danach festgeld.py bauen)
import csv,glob,json,os,re,sys
SP=os.path.dirname(os.path.abspath(__file__)); RD=os.path.join(SP,'festgeld-recherche'); DD=os.path.join(SP,'daten')
# Redaktionell nicht aufgenommen: id -> Grund
AUS={'opel-direktbank-festgeld-de':'Marke der Stellantis Bank mit denselben Konditionen; steht als Stellantis Bank im Vergleich.'}
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
    a['zinsen']=sorted(zs,key=lambda z:(z['monate'] or 0,z['min'] or 0))
    a['es']=a.get('einlagensicherung') or {}
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
            for x in d: raus[x.get('markt') if x.get('markt') in raus else 'de' if n.startswith('DE') else 'at'].append({'name':x['name'],'grund':x['grund'],'gruppe':n.split('-')[0]})
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
            check(a,fehler)
            if not a.get('zinsen'): continue
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
