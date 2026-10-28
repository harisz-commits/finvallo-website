# Ratgeber (nur DE): „Was kostet die Kreditkarte bei der Sparkasse?“
# Sparkassen haben je Institut eigene Preise und veröffentlichen sie nur im eigenen Preisverzeichnis. Die Suchanfragen dazu
# („sparkasse kreditkarte gold kosten“, „visa card basis sparkasse“) landen bei uns, deshalb gibt es hier die Preise von
# 13 großen Sparkassen nebeneinander. Daten: daten/de/sparkassen-karten.json (aus den PLV-PDFs, mit Stand je Sparkasse).
# Aufruf aus ratgeber.build('de'): register(art,P,eur,pct)
import html,json,os,re
E=lambda s: html.escape(str(s)) if s is not None else ''
SP=os.path.dirname(os.path.abspath(__file__))
D=json.loads(open(os.path.join(SP,'daten','de','sparkassen-karten.json'),encoding='utf-8').read().replace('–','-').replace('—','-'))
def _p(x): return f'{x:g}'.replace('.',',')
STUFE={'standard':('Standard','Standard / Classic / Silber'),'gold':('Gold','Gold'),'platinum':('Platinum','Platinum'),'basis':('Basis','Basis (Prepaid)'),'debit':('Sparkassen-Card','Sparkassen-Card (Debit)')}

def _tbl(head,rows):
    h=''.join(f'<th>{c}</th>' for c in head)
    b=''.join('<tr>'+''.join(f'<td>{c}</td>' for c in r)+'</tr>' for r in rows)
    return f'<div class="tbl wide"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'
def _ext(u,t): return f'<a href="{E(u)}" target="_blank" rel="noopener">{E(t)} ↗</a>'
def _dmy(iso): y,m,d=iso.split('-'); return f'{d}.{m}.{y}'
def stufe(k):
    n=k['name'].lower()
    if k['typ']=='Debit': return 'debit'
    if k['typ']=='Prepaid' or 'basis' in n: return 'basis'
    if 'platin' in n: return 'platinum'
    if 'gold' in n: return 'gold'
    if k['typ']=='Kreditkarte': return None   # X-TENSION, Starter: eigene Produkte, nicht vergleichbar
    return 'standard'
def karten(s,st):
    return [k for k in s['karten'] if stufe(k)==st]
def preis(s,st):
    ks=[k for k in karten(s,st) if k.get('jahresgebuehr') is not None]
    if not ks: return None
    lo=min(k['jahresgebuehr'] for k in ks); hi=max(k['jahresgebuehr'] for k in ks)
    return (lo,hi)
def geld(x,eur): return f'{eur(x)} €'
def spanne(st,eur):
    v=[p for s in D for p in [preis(s,st)] if p]
    if not v: return None
    return min(x[0] for x in v),max(x[1] for x in v)

def register(art,P,eur,pct):
    n=len(D); staende=sorted(s['stand'] for s in D)
    L=lambda slug,t:f'<a class="lnk" href="{P}de/kreditkarten/{slug}/">{t}</a>'
    sp={st:spanne(st,eur) for st in STUFE}
    fx=[k['fremdwaehrung_prozent'] for s in D for k in s['karten'] if stufe(k)=='standard' and k.get('fremdwaehrung_prozent') is not None]
    fx0=[s['sparkasse'] for s in D if any(stufe(k)=='gold' and k.get('fremdwaehrung_prozent')==0 for k in s['karten'])]
    # Preistabelle je Sparkasse
    rows=[]
    for s in sorted(D,key=lambda s:(preis(s,'gold') or (999,))[0]):
        def z(st):
            p=preis(s,st)
            if p is None: return '-'
            return geld(p[0],eur) if p[0]==p[1] else f'{eur(p[0])} bis {eur(p[1])} €'
        rows.append([f'{E(s["sparkasse"])}<br><small class="mut">Stand {_dmy(s["stand"])}</small>',z('standard'),z('gold'),z('platinum'),z('basis'),z('debit')])
    preistab=_tbl(['Sparkasse','Standard','Gold','Platinum','Basis','Sparkassen-Card'],rows)
    # Gold im Detail: Fremdwährung, Bargeld, Versicherung
    grows=[]
    for s in sorted(D,key=lambda s:s['sparkasse']):
        g=karten(s,'gold')
        if not g: continue
        k=g[0]; rv=k.get('reiseversicherung') or 'keine Angabe'
        grows.append([E(s['sparkasse']),geld(k['jahresgebuehr'],eur) if k.get('jahresgebuehr') is not None else '-',pct(k['fremdwaehrung_prozent']) if k.get('fremdwaehrung_prozent') is not None else 'keine Angabe',E((k.get('bargeld_text') or 'keine Angabe')[:90]),E(rv[:110])])
    goldtab=_tbl(['Sparkasse','Gold im Jahr','Fremdwährung','Bargeld am Automaten','Reiseversicherung'],grows)
    # Kontomodelle mit Karte
    inkl=[s for s in D if re.search(r'inkl\.|inklusive|unentgeltlich|kostenlos',s.get('hinweis') or '') and re.search(r'Kreditkarte|Mastercard|Gold|Standard',s.get('hinweis') or '')]
    krows=[[E(s['sparkasse']),E(s['hinweis'])] for s in D if s.get('hinweis')]
    kontotab=_tbl(['Sparkasse','Kontomodelle und was dazugehört'],krows)
    q=' · '.join(_ext(s['quelle'],s['sparkasse']) for s in sorted(D,key=lambda s:s['sparkasse']))
    gs,gold,pl,ba,de=sp['standard'],sp['gold'],sp['platinum'],sp['basis'],sp['debit']
    art('de','sparkasse-kreditkarte-kosten',about='Kreditkarten der Sparkassen',
      h1=f'Was kostet die Kreditkarte bei der Sparkasse? Preise von {n} Sparkassen',
      mt='Was kostet die Sparkassen-Kreditkarte? Preise 2026 | Finvallo',
      desc=f'Sparkassen-Kreditkarte Standard, Gold, Platinum und Basis: Jahresgebühr, Fremdwährung und Bargeld bei {n} Sparkassen von Berlin bis München, aus den Preisverzeichnissen.',
      lede='Jede Sparkasse macht ihre eigenen Preise, und auf sparkasse.de steht keiner. Hier sind die Jahresgebühren von Berlin bis München nebeneinander, aus den aktuellen Preisverzeichnissen.',
      kurz=f'Die Standard-Kreditkarte kostet bei den {n} Sparkassen hier zwischen {eur(gs[0])} und {eur(gs[1])} € im Jahr, die Gold-Karte zwischen {eur(gold[0])} und {eur(gold[1])} €. Die Basis-Karte für Jugendliche und Leute ohne Bonität liegt bei {eur(ba[0])} bis {eur(ba[1])} €. Dazu kommen fast überall {_p(min(fx))} bis {_p(max(fx))} % beim Zahlen in Fremdwährung und 2 bis 3 % fürs Bargeld. Kostenlos ist die Kreditkarte nur in einzelnen Premium-Kontomodellen.',
      secs=[
       ('Warum die Sparkasse keinen Preis nennt','<div class="prose"><p>Es gibt nicht die eine Sparkasse, sondern rund 340 rechtlich eigenständige Institute. Jedes legt seine Preise selbst fest, in seinem Preis- und Leistungsverzeichnis. Die Karten heißen überall gleich, Sparkassen-Mastercard Standard, Gold, Platinum, Basis, aber die Jahresgebühr für dieselbe Karte kann in Köln 30 € und in Hannover 42 € kosten. Wer „Sparkasse Kreditkarte Kosten“ googelt, bekommt deshalb nur Antworten für eine bestimmte Stadt oder gar keine.</p>'
        f'<p>Wir haben die Preisverzeichnisse von {n} großen Sparkassen gelesen, von der Berliner Sparkasse bis zur Stadtsparkasse München. Die Tabelle zeigt die Jahresgebühr für die Hauptkarte. Steht ein Bereich, gibt es mehrere Varianten (Mastercard und Visa zu verschiedenen Preisen oder je nach Kontomodell).</p></div>'),
       ('Jahresgebühren im Vergleich',preistab+f'<p class="note">Jahresgebühr für die Hauptkarte laut Preisverzeichnis, Stand je Sparkasse siehe Tabelle. „-“ heißt: diese Karte gibt es dort nicht oder sie steht nicht im Preisverzeichnis. Die Sparkassen-Card ist die girocard zum Konto; bei 0 € ist sie im Kontopreis enthalten.</p>'),
       ('Standard, Gold, Platinum, Basis: was dahintersteckt',f'<div class="prose"><p><b>Standard (auch Classic oder Silber):</b> Die normale Kreditkarte, bei fast allen Sparkassen eine Charge-Karte, also einmal im Monat komplett vom Konto abgebucht. {eur(gs[0])} bis {eur(gs[1])} € im Jahr, ohne Versicherungen. Für Mietwagen und Hotels reicht sie.</p>'
        f'<p><b>Gold:</b> Dieselbe Karte mit Versicherungspaket: Auslandskranken, Reiserücktritt, oft Gepäck und Mietwagen-Kasko. {eur(gold[0])} bis {eur(gold[1])} € im Jahr. Lohnt sich nur, wenn du die Versicherungen sonst extra kaufen würdest; die Bedingungen (Reise mit der Karte bezahlt, Altersgrenzen, Selbstbehalt) stehen im Versicherungsheft der jeweiligen Sparkasse.</p>'
        f'<p><b>Platinum:</b> Mehr Versicherungssummen, Concierge, teils Lounge-Zugang. {eur(pl[0])} bis {eur(pl[1])} € im Jahr. Für die meisten zu teuer; wer so viel ausgeben will, bekommt bei American Express oder den Direktbanken mehr dafür.</p>'
        f'<p><b>Basis:</b> Eine Prepaid-Karte, die nur mit aufgeladenem Guthaben bezahlt. Keine Bonitätsprüfung, deshalb die Karte für Jugendliche ab 12 oder 14 und für Leute mit Schufa-Eintrag. Kostet trotzdem {eur(ba[0])} bis {eur(ba[1])} € im Jahr, was im Vergleich zu kostenlosen Debitkarten der App-Banken viel ist.</p>'
        f'<p><b>Sparkassen-Card:</b> Die girocard, inzwischen meist mit Debit Mastercard oder Visa Debit kombiniert, damit sie auch online geht. Bei vielen Sparkassen im Konto enthalten, bei manchen {eur(de[1])} € im Jahr. Sie ist keine Kreditkarte, auch wenn ein Mastercard-Logo drauf ist.</p>'
        f'<p>Einige Sparkassen haben zusätzlich eine echte Kreditkarte mit Ratenzahlung (Mastercard X-TENSION oder Starter-Karte, 12 bis 24 € im Jahr). Die zählt hier nicht als Standard, weil sie anders abrechnet; Details im Ratgeber <a class="lnk" href="{P}de/ratgeber/kartentypen/">Kartentypen</a>.</p></div>'),
       ('Gold-Karte: Fremdwährung, Bargeld, Versicherung',goldtab+'<p class="note">Fremdwährung = Aufschlag beim Zahlen außerhalb des Euroraums. Bargeld = Gebühr der Sparkasse, dazu kann der Automatenbetreiber etwas verlangen. Versicherungsbedingungen laut Produktseite der Sparkasse; vor dem Abschluss im Versicherungsheft prüfen.</p>'
        +(f'<div class="prose"><p>Auffällig: {", ".join(fx0)} verlangen bei der Gold-Karte 0 % Fremdwährungsaufschlag, alle anderen 1 bis 2,5 %. Wer viel außerhalb des Euroraums zahlt, spart damit bei 5.000 € Jahresumsatz 50 bis 125 € gegenüber den Kollegen.</p></div>' if fx0 else '')),
       ('Wann die Kreditkarte im Konto drin ist','<div class="prose"><p>Die meisten Sparkassen verkaufen Konto und Karte getrennt. Ein paar Premium-Kontomodelle enthalten eine Kreditkarte, und bei einigen gibt es Rabatte für junge Kunden, mit denen die Standardkarte auf 0 € fällt. Das steht bei keiner Sparkasse auf der Kartenseite, sondern beim Konto. Die Übersicht:</p></div>'+kontotab
        +'<div class="prose"><p>Rechne das durch: Ein Premium-Konto für 15 € im Monat mit Gold-Karte kostet 180 € im Jahr. Ein günstiges Konto plus Gold-Karte einzeln liegt oft darunter. Die Karte „gratis“ im Konto ist nur dann ein Vorteil, wenn du das teure Konto ohnehin wolltest.</p></div>'),
       ('Ist die Sparkassen-Kreditkarte ihr Geld wert?',f'<div class="prose"><p>Verglichen mit kostenlosen Kreditkarten ist sie teuer: {L("sparkasse-kreditkarte-gold","Die Sparkassen Gold")} kostet 60 bis 96 € im Jahr und verlangt im Ausland Aufschlag, während gebührenfreie Karten wie die Bank Norwegian Visa oder die TF Bank Mastercard Gold dasselbe Versicherungspaket ohne Jahresgebühr und mit 0 % Fremdwährungsentgelt bieten. Der Unterschied: Bei der Sparkasse hängt die Karte am Girokonto, die Abrechnung läuft automatisch, und du hast eine Filiale, wenn etwas schiefgeht. Die Gratis-Karten musst du selbst überweisen, sonst läuft die Teilzahlung mit über 20 % Zinsen an.</p>'
        f'<p>Wer die Karte zwei-, dreimal im Jahr für Hotel, Mietwagen und Onlinekäufe braucht, fährt mit der Standard-Karte der eigenen Sparkasse ordentlich und ohne Überraschungen. Wer viel reist, viel in Fremdwährung zahlt oder die Versicherungen wirklich nutzen will, findet im <a class="lnk" href="{P}de/kreditkarten/">Kreditkarten-Vergleich</a> günstigere Karten. Die Sparkassen-Karten selbst stehen dort mit den Preisen der Berliner Sparkasse als Beispiel: {L("sparkasse-kreditkarte-classic","Standard")}, {L("sparkasse-kreditkarte-gold","Gold")} und {L("sparkasse-visa-card-basis","Visa Card Basis")}.</p></div>'),
       ('Woher die Preise kommen',f'<div class="prose"><p>Alle Zahlen stammen aus den Preis- und Leistungsverzeichnissen der Sparkassen, die jede auf ihrer Website als PDF veröffentlicht, geprüft am {_dmy(max(s["geprueft"] for s in D))}. Der Stand des Dokuments steht in der Tabelle; die Preisverzeichnisse ändern sich ein- bis zweimal im Jahr. Deine Sparkasse ist nicht dabei? Suche auf ihrer Website nach „Preis- und Leistungsverzeichnis“ oder „Preisaushang“, dort stehen die Karten unter „Zahlungsverkehr“ oder „Kartengeschäft“.</p><p class="src">Quellen: {q}</p></div>')],
      faq=[('Was kostet die Kreditkarte bei der Sparkasse im Jahr?',f'Je nach Sparkasse und Karte: Standard {eur(gs[0])} bis {eur(gs[1])} €, Gold {eur(gold[0])} bis {eur(gold[1])} €, Platinum {eur(pl[0])} bis {eur(pl[1])} €, Basis (Prepaid) {eur(ba[0])} bis {eur(ba[1])} €. Die Preise deiner Sparkasse stehen in ihrem Preisverzeichnis.'),
           ('Was kostet die Sparkasse Gold-Kreditkarte?',f'Zwischen {eur(gold[0])} € (Naspa) und {eur(gold[1])} € (Stadtsparkasse München) im Jahr, die meisten Sparkassen nehmen 84 €. Dafür gibt es ein Versicherungspaket mit Auslandskranken und Reiserücktritt. Einzelheiten in der Gold-Tabelle oben.'),
           ('Ist die Sparkassen-Kreditkarte kostenlos?','Normalerweise nicht. Kostenlos wird sie nur in einzelnen Premium-Kontomodellen (zum Beispiel Kreissparkasse Köln S-GiroPlus XXL, Sparkasse Leipzig GiroPremium) oder mit Jugendrabatt, etwa bei der Sparkasse Bremen bis 25 Jahre. Wer eine dauerhaft kostenlose Kreditkarte will, findet sie bei Direktbanken, nicht bei der Sparkasse.'),
           ('Was kostet die Visa Card Basis der Sparkasse?',f'{eur(ba[0])} bis {eur(ba[1])} € im Jahr, meist 30 bis 42 €. Sie ist eine Prepaid-Karte ohne Bonitätsprüfung, also für Jugendliche und für alle, die keine normale Kreditkarte bekommen. Die Visa Card Basis der Berliner Sparkasse steht als Beispiel im Vergleich.'),
           ('Welche Gebühren kommen bei der Sparkassen-Kreditkarte dazu?',f'Beim Zahlen in Fremdwährung {_p(min(fx))} bis {_p(max(fx))} % Aufschlag (bei der Gold-Karte einiger Sparkassen 0 %), beim Bargeldabheben 2 bis 3 % des Betrags, mindestens 5 bis 7,50 €, auch am eigenen Automaten. Innerhalb des Euroraums kostet das Bezahlen im Laden nichts extra.'),
           ('Mastercard oder Visa bei der Sparkasse?','Die Konditionen sind in der Regel gleich, du wählst nur das Netz. Einige Sparkassen geben im Neugeschäft nur noch Mastercard aus (zum Beispiel KölnBonn), die Stadtsparkasse München nimmt für die Visa Standard 10 € mehr als für die Mastercard. Für die Akzeptanz ist es egal.')],
      related=['kartentypen','kostenlose-kreditkarte','reiseversicherung','fremdwaehrung'])
