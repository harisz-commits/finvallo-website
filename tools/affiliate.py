# Partnerlinks an einer Stelle: daten/affiliate.json. Gibt es für ein Produkt einen Partnerlink, zeigt der Button dorthin,
# trägt rel="sponsored" und den Stern (die Fußzeile erklärt: „Mit * markierte Links sind Affiliate-Links“).
# Ohne Partnerlink bleibt der normale Link zum Anbieter. Quellenlinks (Preisblatt, Konditionen) bleiben immer unverändert.
import json,os
from html import escape as E
SP=os.path.dirname(os.path.abspath(__file__))
A=json.load(open(os.path.join(SP,'daten','affiliate.json'),encoding='utf-8'))
TITLE='Affiliate-Link: Schließt du hier ab, bekommt Finvallo eine Provision. Für dich ändert sich am Preis nichts.'
def link(land,bereich,key):
    """Partnerlink oder None"""
    return ((A.get(land) or {}).get(bereich) or {}).get(key)
def btn(land,bereich,key,fallback,text='Zum Anbieter',cls='btn primary block',style=''):
    """Button zum Anbieter: Partnerlink mit Stern und rel=sponsored, sonst der normale Link"""
    st=f' style="{style}"' if style else ''
    u=link(land,bereich,key)
    if u: return f'<a class="{cls}"{st} href="{E(u)}" target="_blank" rel="sponsored noopener" title="{TITLE}">{text}* ↗</a>'
    return f'<a class="{cls}"{st} href="{E(fallback)}" target="_blank" rel="noopener">{text} ↗</a>'
def keys():
    """[(land, bereich, key)] aller eingetragenen Links, für check.py"""
    return [(l,b,k) for l in ('at','de') for b,m in (A.get(l) or {}).items() for k in m]
