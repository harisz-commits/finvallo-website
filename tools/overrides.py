# Redaktionelle Korrekturen nach Prüfung der Agenten-Ergebnisse (key -> Felder)
O={
 'american-express-business-gold-card':{'tier':1,'_why':'kein Reiserücktritt; nur Auslandskranken + Mietwagen'},
 'bmw-premium-card-carbon':{'tier':3,'_why':'kein Reiseunfall/Reisekomfort -> nicht Premium-Niveau'},
}
def apply(c):
    if 'mercedes' in c.get('key',''): c['status']='unsicher'
    if any(x in c.get('key','') for x in ('senator','hon-circle','frequent-traveller')): c['nurfuer']='Nur für Miles & More Statuskunden (Frequent Traveller, Senator, HON Circle)'
    k=c.get('key','')
    for kk,v in O.items():
        if k==kk: c.update({a:b for a,b in v.items() if not a.startswith('_')})
    if k.startswith('adac') and 'platin' in k: c['klasse']='Gold'
    # wie AT (TF Bank): inklusive Cashback/Punkte/Partner-Rabatte zählen als Extra; nur gegen Aufpreis oder „kein“ zählt nicht
    t=c.get('cbText') or ''
    if t:
        paid=bool(re.search(r'nur gegen|gegen Aufpreis',t))
        has=bool(re.search(r'\d+(,\d+)? ?%|Partner|Punkt|Meile|Rabatt',t,re.I))
        c.setdefault('ex',{})['cb']= has and not paid
    return c
TITLE={
 'gmx-web-de-web-cent-kreditkarte-mastercard-gold':'WEB.Cent Mastercard Gold (GMX / WEB.DE)',
 'klarna-card-standard':'Klarna Card','klarna-kreditkarte-everywhere':'Klarna Kreditkarte Everywhere',
 'crypto-com-visa-prepaid-card-midnight-level-up-basic':'Crypto.com Visa Card Midnight',
 'crypto-com-visa-prepaid-card-ruby-steel-level-up-plus':'Crypto.com Visa Card Ruby Steel',
 'crypto-com-visa-prepaid-card-jade-indigo-level-up-pro':'Crypto.com Visa Card Jade/Indigo',
 'trading-212-212-card':'Trading 212 Card','magenta-pay-telekom-visa-debit-virtuell':'Magenta Pay Visa Debitkarte',
 'hanseatic-bank-awa7-visa-kreditkarte':'awa7 Visa Kreditkarte',
 'american-express-bmw-card-von-american-express':'BMW Card von American Express',
 'american-express-bmw-premium-card-carbon':'BMW Premium Card Carbon',
 'american-express-payback-american-express-karte':'PAYBACK American Express Karte',
 'american-express-dm-payback-american-express-karte':'dm PAYBACK American Express Karte',
 'american-express-amazon-business-american-express-card':'Amazon Business American Express Card',
 'american-express-amazon-business-prime-american-express-card':'Amazon Business Prime American Express Card',
}
import re
def title(c,slugf):
    n=c['name']; a=c['anbieter']
    first=a.split()[0].lower()
    t=n if (a.lower() in n.lower() or n.lower().startswith(first)) else f'{a} {n}'
    t0=slugf(t)
    if t0 in TITLE: return TITLE[t0]
    t=re.sub(r'\s*\([^)]*\)','',t).strip()
    return t
