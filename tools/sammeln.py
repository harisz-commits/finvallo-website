import re
# Sammelwert für die Bestenliste „Meilen & Punkte“: was eine Karte bei normalem Umsatz zurückbringt.
# tier2 = (Höchstwert €/Jahr zur vollen Rate, Rate darüber)
# rate = Wert in % vom allgemeinen Kartenumsatz (1 Punkt/Meile = 1 Cent, Hilton-Punkt = 0,4 Cent),
# cap = Höchstwert € pro Jahr, extra = Aufpreis € pro Jahr für das Programm, tier2 = (Grenze €/Jahr, Rate darüber)
# Partner-, Reise- oder Kategorie-Rabatte zählen hier NICHT (rate 0).
REF=12000  # Referenz: 1.000 € Kartenumsatz pro Monat
AT={
 'Advanzia Bank Hilton Honors Kreditkarte':dict(rate=0.4,txt='1 Hilton-Punkt pro € (≈ 0,4 %)'),
 'American Express Gold Card':dict(rate=1.0,extra=30,txt='1 Membership-Rewards-Punkt pro € (Programm 30 €/Jahr)'),
 'American Express Platinum Card':dict(rate=1.0,txt='1 Membership-Rewards-Punkt pro €'),
 'American Express Card':dict(rate=1.0,extra=30,txt='1 Membership-Rewards-Punkt pro € (Programm 30 €/Jahr)'),
 'American Express BMW Card':dict(rate=1.0,txt='1 Membership-Rewards-Punkt pro € (inklusive)'),
 'American Express BMW Card Gold':dict(rate=1.0,txt='1 Membership-Rewards-Punkt pro € (inklusive)'),
 'Diners Club Gold':dict(rate=0.5,extra=25,txt='4 Meilen pro 8 € (Programm 25 €/Jahr)'),
 'Diners Club Golf':dict(rate=0.5,extra=25,txt='4 Meilen pro 8 € (Programm 25 €/Jahr)'),
 'Diners Club Vintage':dict(rate=0.5,txt='4 Miles & More Meilen pro 8 €'),
 'Erste Bank und Sparkassen Smartcard':dict(rate=0.3,cap=8,txt='0,3 % online, max. 8 €/Jahr'),
 'Erste Bank und Sparkassen GÖD Smartcard':dict(rate=0.3,cap=8,txt='0,3 % online, max. 8 €/Jahr'),
 'Erste Bank und Sparkassen Premiumcard':dict(rate=0.6,cap=30,txt='0,6 % online, max. 30 €/Jahr'),
 'Erste Bank und Sparkassen GÖD Premiumcard':dict(rate=0.6,cap=30,txt='0,6 % online, max. 30 €/Jahr'),
 'Erste Bank und Sparkassen Austrian Miles & More Premiumcard':dict(rate=0.67,txt='1 Meile pro 1,50 €'),
 'Santander Card':dict(rate=1.0,cap=50,txt='1 % Cashback, max. 50 €/Jahr'),
 'Revolut Standard':dict(rate=0.1,txt='1 RevPoint pro 10 €'),'Revolut Plus':dict(rate=0.1,txt='1 RevPoint pro 10 €'),
 'Revolut Premium':dict(rate=0.25,txt='1 RevPoint pro 4 €'),'Revolut Metal':dict(rate=0.5,txt='1 RevPoint pro 2 €'),'Revolut Ultra':dict(rate=1.0,txt='1 RevPoint pro €'),
 'Trade Republic Karte':dict(rate=1.0,cap=180,txt='1 % Saveback, max. 15 €/Monat'),
}
DE={
 'WEB.Cent Mastercard Gold (GMX / WEB.DE)':dict(rate=0.5,txt='0,5 % Cashback auf alles'),
 'Hilton Honors Kreditkarte':dict(rate=0.4,txt='1 Hilton-Punkt pro € (≈ 0,4 %)'),
 'Turkish Airlines Miles&Smiles Mastercard Gold':dict(rate=0.5,txt='1 Meile pro 2 €'),
 'Klarna Plus':dict(rate=0.5,txt='0,5 % Cashback'),'Klarna Premium':dict(rate=1.0,txt='1 % Cashback'),'Klarna Max':dict(rate=1.5,txt='1,5 % Cashback'),
 'Eurowings Kreditkarte Classic':dict(rate=0.5,txt='1 Prämienmeile pro 2 €'),'Eurowings Kreditkarte Premium':dict(rate=0.5,txt='1 Prämienmeile pro 2 €'),
 'Amazon Visa':dict(kind='cash',rate=0.5,txt='0,5 % in Amazon-Punkten (1 % bei Amazon)'),
 'IKEA Family Kreditkarte':dict(rate=1.0,cap=30,txt='1 % als IKEA-Guthaben, max. 30 €/Jahr'),
 'Miles & More Gold Credit Card':dict(rate=0.5,txt='1 Meile pro 2 €'),'Miles & More Blue Credit Card':dict(rate=0.5,txt='1 Meile pro 2 €'),'Miles & More MyFlex Credit Card':dict(rate=0.5,txt='1 Meile pro 2 €'),
 'TARGOBANK Gold-Karte':dict(rate=1.0,cap=100,txt='1 % Cashback, max. 100 €/Jahr'),
 'TARGOBANK Premium-Karte':dict(rate=1.0,cap=200,txt='1 Punkt pro € (100 Punkte = 1 €), max. 200 €/Jahr'),
 'American Express Platinum Card':dict(rate=1.0,txt='1 Membership-Rewards-Punkt pro €'),
 'American Express Gold Card':dict(rate=1.0,txt='1 Membership-Rewards-Punkt pro €'),
 'American Express Gold Card Rosé':dict(rate=1.0,txt='1 Membership-Rewards-Punkt pro €'),
 'American Express Card':dict(rate=1.0,txt='1 Membership-Rewards-Punkt pro €'),
 'PAYBACK American Express Karte':dict(rate=0.33,txt='1 °Punkt pro 3 €'),'dm PAYBACK American Express Karte':dict(rate=0.33,txt='1 °Punkt pro 3 € (doppelt bei dm)'),
 'BMW Card von American Express':dict(rate=1.0,txt='1 Membership-Rewards-Punkt pro €'),'BMW Premium Card Carbon':dict(rate=1.0,txt='1 Membership-Rewards-Punkt pro €'),
 'PAYBACK Visa Kreditkarte':dict(rate=0.2,txt='1 °Punkt pro 5 €'),'PAYBACK Visa Kreditkarte auf Guthabenbasis':dict(rate=0.2,txt='1 °Punkt pro 5 €'),
 'C24 Bank Smart':dict(rate=0.05,txt='0,05 % Basis-Cashback'),
 'C24 Bank Plus':dict(rate=0.5,tier2=(144,0.1),txt='0,5 % bis 12 €/Monat, danach 0,1 %'),
 'C24 Bank Max':dict(rate=1.0,tier2=(288,0.2),txt='1 % bis 24 €/Monat, danach 0,2 %'),
 'Trade Republic Karte':dict(rate=1.0,cap=180,txt='1 % Saveback, max. 15 €/Monat'),
 'Trading 212 Card':dict(rate=1.5,cap=180,txt='1,5 % Cashback, max. 15 €/Monat (mit Abo-Zahlung)'),
 'UnitPlus Mastercard':dict(rate=0.1,txt='0,1 % Cashback'),
 'Kraken Krak Card':dict(rate=0.5,txt='0,5 % ab ca. 200 € Guthaben'),
 'Crypto.com Visa Card Ruby Steel':dict(rate=0.75,cap=104,txt='1,5 % in CRO (Kursrisiko, zur Hälfte bewertet), Umsatzdeckel 1.250 $/Monat'),
 'Crypto.com Visa Card Jade/Indigo':dict(rate=1.25,cap=345,txt='2,5 % in CRO (Kursrisiko, zur Hälfte bewertet), Umsatzdeckel 2.500 $/Monat'),
 'Magenta Pay Visa Debitkarte':dict(rate=1.0,txt='1 % in Coins'),
 'Monese Mastercard Cashback':dict(rate=0.5,cap=30,txt='0,5 %, max. 2,50 €/Monat'),
}
def kind(m):
    if m.get('kind'): return m['kind']
    t=m.get('txt','')
    if re.search(r'Meile|Miles',t,re.I): return 'miles'
    if re.search(r'Membership|Hilton|°Punkt|RevPoint|Punkt je|Bonuspunkt|Punkte',t): return 'points'
    return 'cash'
def value(land,titel,spend=REF):
    m=(AT if land=='at' else DE).get(titel)
    if not m or not m.get('rate'): return None
    if 'tier2' in m:
        capv,r2=m['tier2']; s1=capv/(m['rate']/100)   # Umsatz, bis zu dem die volle Rate gilt
        v=min(spend,s1)*m['rate']/100+max(0,spend-s1)*r2/100
    else: v=spend*m['rate']/100
    if m.get('cap') is not None: v=min(v,m['cap'])
    return round(v-m.get('extra',0),2), m
def note(v):
    if v is None or v<=0: return None
    for lim,s in [(180,5.0),(120,4.5),(90,4.0),(60,3.5),(36,3.0)]:
        if v>=lim: return s
    return 2.5

def net_note(v):
    """Netto-Sammelwert (Sammelwert minus Jahresgebühr) in Sterne."""
    if v is None: return None
    for lim,s_ in [(150,5.0),(100,4.5),(60,4.0),(30,3.5),(0,3.0),(-50,2.5),(-150,2.0)]:
        if v>=lim: return s_
    return 1.5
