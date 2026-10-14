# Bewertung nach finvallo-Methodik (siehe /at/kreditkarten/methodik/)
W={'Jahresgebühr':25,'Reiseversicherung':20,'Zahlen im Ausland':15,'Kartenart & Akzeptanz':10,'Alltag & Flexibilität':10,'Bargeld':10,'Extras':10}
MISSING=2.5
TIER={0:(1.0,'Keine Reiseversicherung'),1:(3.0,'Basis-Reiseschutz'),2:(4.2,'Reiseversicherung inkl. Storno'),3:(4.7,'Umfassender Reiseschutz'),4:(5.0,'Premium-Reiseschutz')}
def eur(x):
    s=f'{x:,.2f}'.replace(',','X').replace('.',',').replace('X','.')
    return s[:-3] if s.endswith(',00') else s
def pct(x):
    s=f'{x:.2f}'.replace('.',','); return (s[:-3] if s.endswith(',00') else s)+' %'
def s_fee(f):
    if f==0: return 5.0
    for lim,s in [(25,4.6),(50,4.2),(100,3.6),(150,3.0),(250,2.4),(450,1.8)]:
        if f<=lim+1e-9: return s
    return 1.2
def s_fx(x):
    if x==0: return 5.0
    for lim,s in [(0.5,4.8),(1,4.4),(1.5,4.0),(2,3.4),(2.7,2.6),(3.2,2.0)]:
        if x<=lim+1e-9: return s
    return 1.5
def cash200(c):
    """Kosten in € für 200 € Inland; None=unbekannt; 'fi'=kostenlos aber verzinst"""
    if not c: return None
    k=c[0]
    if k=='free': return 0.0
    if k=='free_interest': return 'fi'
    if k=='fix': return float(c[1])
    if k=='pct': return 200*c[1]/100
    if k=='pctmin': return max(200*c[1]/100,c[2])
    if k=='fixpct': return c[1]+200*c[2]/100
    if k=='freeN': return 0.0 if c[1]>=1 else float(c[2])
    if k=='no': return 'no'
    return None
def s_cash(v):
    if v=='fi': return 4.5
    if v=='no': return 2.0
    if v==0: return 5.0
    for lim,s in [(2,4.2),(4,3.4),(7,2.6)]:
        if v<=lim+1e-9: return s
    return 2.0
def score(c):
    """c: dict mit fee, tier, fx, typ, netz, giro, auto, pay, cash, ex{cb,lg,lgm,ml,credits,ft,offer}"""
    parts=[]; known=0
    def add(k,s,v,ok=True):
        nonlocal known
        if ok: known+=1
        parts.append({'k':k,'s':round(s,1),'v':v,'w':W[k]})
    f=c.get('fee')
    if f is None: add('Jahresgebühr',MISSING,'keine bestätigten Daten',False)
    else: add('Jahresgebühr',s_fee(f),'kostenlos' if f==0 else f'{eur(f)} € pro Jahr')
    t=c.get('tier')
    if t is None: add('Reiseversicherung',MISSING,'keine bestätigten Daten',False)
    else: add('Reiseversicherung',*TIER[t])
    x=c.get('fx')
    if x is None: add('Zahlen im Ausland',MISSING,'keine bestätigten Daten',False)
    else: add('Zahlen im Ausland',s_fx(x),'0 %' if x==0 else f'{pct(x)} pro Zahlung in US-Dollar')
    # Alltag: drei Punkte; was nicht bestätigt ist, zählt wie überall mit MISSING (2,5)
    vals=[];txt=[];conf=0
    g=c.get('giro')
    if g is None: vals.append(MISSING); txt.append('Konto beim Anbieter nicht bestätigt')
    else: vals.append(2.5 if g else 5.0); txt.append('Konto beim Anbieter nötig' if g else 'kein Konto beim Anbieter nötig'); conf+=1
    a=c.get('auto')
    if a is None: vals.append(MISSING); txt.append('Abbuchung nicht bestätigt')
    else: vals.append(5.0 if a else 3.0); txt.append('automatische Abbuchung' if a else 'Rechnung selbst überweisen'); conf+=1
    p=c.get('pay')
    if p is None: vals.append(MISSING); txt.append('Apple Pay / Google Pay nicht bestätigt')
    else: vals.append(5.0 if p else 1.0); txt.append('Apple Pay / Google Pay' if p else 'kein Apple Pay / Google Pay'); conf+=1
    if conf: add('Alltag & Flexibilität',sum(vals)/len(vals),', '.join(txt))
    else: add('Alltag & Flexibilität',MISSING,'keine bestätigten Daten',False)
    v=cash200(c.get('cash'))
    if v is None: add('Bargeld',MISSING,'keine bestätigten Daten',False)
    elif v=='fi': add('Bargeld',4.5,'kostenlos, aber ab Tag 1 verzinst')
    elif v=='no': add('Bargeld',2.0,'Bargeld nicht möglich')
    elif v==0: add('Bargeld',5.0,'kostenlos')
    else: add('Bargeld',s_cash(v),f'{eur(v)} € für 200 €')
    ex=c.get('ex') or {}; e=2.5; et=[]
    for k,b,t in [('cb',1.0,'Cashback oder Punkte'),('lg',1.0,'kostenlose Lounge-Besuche'),('lgm',0.4,'Lounge-Mitgliedschaft'),('ml',0.5,'Meilen'),('credits',0.5,'Guthaben oder Abos'),('ft',0.3,'FastTrack'),('offer',0.3,'Aktion im 1. Jahr')]:
        if ex.get(k) and not (k=='lgm' and ex.get('lg')): e+=b; et.append(t)
    add('Extras',min(5.0,e),', '.join(et) or 'keine besonderen Extras')
    typ=c.get('typ'); netz=c.get('netz') or ''
    if 'American Express' in netz: add('Kartenart & Akzeptanz',3.0,'American Express: wird seltener angenommen als Visa oder Mastercard')
    elif 'Diners' in netz: add('Kartenart & Akzeptanz',2.0,'Diners Club: wird nur eingeschränkt angenommen')
    elif typ in ('Debit','Prepaid'):
        lab='Debitkarte' if typ=='Debit' else 'Prepaid-Karte'
        nz=netz if netz in ('Visa','Mastercard','Visa/Mastercard') else 'Visa oder Mastercard'
        add('Kartenart & Akzeptanz',3.5,f'{lab} mit {nz}: fast überall nutzbar, bei Kautionen oft abgelehnt')
    elif typ in ('Kreditkarte','Charge'):
        if netz in ('Visa','Mastercard','Visa/Mastercard'): add('Kartenart & Akzeptanz',5.0,f'{netz}, als Kredit- oder Charge-Karte auch für Kautionen')
        else: add('Kartenart & Akzeptanz',4.5,'Kredit- oder Charge-Karte, Kartennetz noch nicht bestätigt')
    else: add('Kartenart & Akzeptanz',MISSING,'keine bestätigten Daten',False)
    order=['Jahresgebühr','Reiseversicherung','Zahlen im Ausland','Alltag & Flexibilität','Bargeld','Extras','Kartenart & Akzeptanz']
    parts.sort(key=lambda p:order.index(p['k']))
    avg=sum(p['s']*p['w'] for p in parts)/100
    rated = f is not None and known>=5
    stars=round(avg+1e-9,1) if rated else None
    return {'parts':parts,'stars':stars,'total':round(avg/5*100) if rated else None,'basis':known,'wsum':100}
def note(s):
    if s is None: return None
    return 'Sehr gut' if s>=4.5 else 'Gut' if s>=4.0 else 'Befriedigend' if s>=3.5 else 'Ausreichend' if s>=3.0 else 'Mangelhaft'
