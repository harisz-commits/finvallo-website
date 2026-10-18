# Ratgeber (nur DE): „Geld abheben mit der Kreditkarte“, Gegenstück zu /at/ratgeber/bargeld-beheben/ (hreflang-Paar).
# Eigener Text für Deutschland (Geldautomat, Girocard, Automatenverbünde, andere Karten); Gebühren live aus den DE-Kartendaten.
# Aufruf aus ratgeber.build('de'): register(art,P,best,K,nprv,eur,KM)
import html,re
E=lambda s: html.escape(str(s)) if s is not None else ''

def _tbl(head,rows):
    h=''.join(f'<th>{c}</th>' for c in head)
    b=''.join('<tr>'+''.join(f'<td>{c}</td>' for c in r)+'</tr>' for r in rows)
    return f'<div class="tbl wide"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'

def kind(c):
    v=c.get('cash') or []; k=v[0] if v else None
    if k=='free': return 0
    if k=='freeN': return 1
    if k=='free_interest': return 2
    if k=='fix': return 0 if (len(v)>1 and v[1]==0) else 3
    return 4
def zins(c): return kind(c)==2 or bool(re.search(r'Zins|Sollzins',c.get('cashText') or ''))

# Rechenbeispiele: Gebühr der Bank je Abhebung (erste im Monat), ohne Betreiberentgelt. Regeln aus den Preisangaben der Karten.
# Spalten: 100 € Deutschland, 300 € Italien (Euro), 500 € Türkei (Lira), 200 € Thailand (Baht). Werte als Funktionen (amount, inland, euro, fx%, soll%).
def _int(a,soll,d=20): return a*soll/100*d/365
def _pm(a,p,m): return max(a*p/100,m)
RULES={
 'tf-bank-mastercard-gold':            lambda a,i,e,fx,s:(_int(a,s),'nur Zinsen, 20 Tage'),
 'advanzia-bank-gebuehrenfrei-mastercard-gold': lambda a,i,e,fx,s:(_int(a,s),'nur Zinsen, 20 Tage'),
 'hanseatic-bank-genialcard':          lambda a,i,e,fx,s:(3.95 if i else 0,''),
 'deutschland-kreditkarte-classic':    lambda a,i,e,fx,s:(3.95 if i else 0,''),
 'dkb-visa-kreditkarte':               lambda a,i,e,fx,s:(0,'ab 50 €'),
 'ing-visa-card':                      lambda a,i,e,fx,s:(0 if e else a*0.022,'' if e else '2,2 % in Fremdwährung'),
 'consorsbank-credit-card-gold-light': lambda a,i,e,fx,s:(0,''),
 'trade-republic-karte':               lambda a,i,e,fx,s:(0 if a>=100 else 1,'ab 100 €'),
 'n26-standard':                       lambda a,i,e,fx,s:(0 if e else a*0.017,'2 Euro-Abhebungen im Monat gratis' if e else '1,7 % in Fremdwährung'),
 'revolut-standard':                   lambda a,i,e,fx,s:((max((a-200)*0.02,1) if a>200 else 0),'bis 200 € im Monat gratis'),
 'c24-bank-smart':                     lambda a,i,e,fx,s:(0,'4 Abhebungen im Monat gratis'),
 'sparkasse-kreditkarte-classic':      lambda a,i,e,fx,s:(_pm(a,2,7.5) if i else (0 if e else a*fx/100),'' if i else 'Ausland ohne Sparkassen-Entgelt'),
 'volksbank-classiccard':              lambda a,i,e,fx,s:(a*0.02 if i else (0 if e else a*fx/100),''),
 'deutsche-bank-mastercard-standard':  lambda a,i,e,fx,s:(_pm(a,2.5,5.75)+(0 if e else a*fx/100),''),
 'commerzbank-classickreditkarte':     lambda a,i,e,fx,s:(_pm(a,1.95,5.98)+(0 if e else a*fx/100),''),
 'postbank-mastercard':                lambda a,i,e,fx,s:(_pm(a,2.5,5)+(0 if e else a*fx/100),''),
 'payback-visa-kreditkarte':           lambda a,i,e,fx,s:(_pm(a,2,5) if i else 0,'' if i else 'Ausland gebührenfrei'),
 'miles-und-more-blue-credit-card':    lambda a,i,e,fx,s:(_pm(a,2,5)+(0 if e else a*fx/100),''),
 'american-express-card':              lambda a,i,e,fx,s:(_pm(a,4,5)+(0 if e else a*fx/100),'erst nach 6 Monaten'),
 'bank-norwegian-visa-kreditkarte':    lambda a,i,e,fx,s:(0,''),
}
SZEN=[(100,True,True),(300,False,True),(500,False,False),(200,False,False)]

def register(art,P,best,K,nprv,eur,KM):
    T={c['slug']:c for c in K}
    for s in RULES:
        if s not in T: raise SystemExit(f'ratgeber_bargeld_de: unbekannte Karte {s}')
    priv=[c for c in K if c['art']=='Privat']
    def L(slug,label=None): return f'<a class="lnk" href="{P}de/kreditkarten/{slug}/">{E(label or T[slug]["titel"])}</a>'
    def fee(c):
        f=c.get('fee'); t='kostenlos' if f==0 else (f'{eur(f)} €' if f is not None else 'keine Angabe')
        return t+(' <small>(nur für bestimmte Gruppen)</small>' if c.get('nurfuer') else '')
    def E2(x): return eur(round(x+1e-9,2))
    n_free=len([c for c in priv if kind(c)==0]); n_lim=len([c for c in priv if kind(c)==1]); n_int=len([c for c in priv if kind(c)==2]); n_fix=len([c for c in priv if kind(c)==3]); n_pct=len([c for c in priv if kind(c)==4])
    n_zins=len([c for c in priv if zins(c)])
    typ={'Kreditkarte':'Kreditkarte','Charge':'Charge-Karte','Debit':'Debitkarte','Prepaid':'Prepaid'}
    order=sorted(priv,key=lambda c:(kind(c),c.get('fee') if c.get('fee') is not None else 1e9,c['titel']))
    alle=_tbl(['Karte','Typ','Jahresgebühr','Bargeld: Entgelt der Bank','Fremdwährung','Zinsen ab Buchungstag'],
              [(L(c['slug']),E(typ.get(c['typ'],c['typ'])),fee(c),E(KM.cashT(c)),E(KM.fxT(c)),'ja' if zins(c) else 'nein') for c in order])
    rows=[]
    for s,fn in RULES.items():
        c=T[s]; cells=[]
        for a,i,e in SZEN:
            v,n=fn(a,i,e,c.get('fx') or 0,c.get('soll') or c.get('effz') or 0)
            cells.append(('kostenlos' if v==0 else f'{E2(v)} €')+(f' <small>({E(n)})</small>' if n else ''))
        rows.append((L(s),*cells))
    beispiele=_tbl(['Karte','100 € in Deutschland','300 € in Italien (Euro)','500 € in der Türkei (Lira)','200 € in Thailand (Baht)'],rows)
    tf=T['tf-bank-mastercard-gold']; ad=T['advanzia-bank-gebuehrenfrei-mastercard-gold']; z_tf=tf.get('soll'); z_ad=ad.get('soll')
    zins_tbl=_tbl(['Abhebung','Tage bis zur Zahlung','Zinsen TF Bank','Zinsen Advanzia','Zum Vergleich: 2,5 %, mind. 5,75 €'],[
        (f'{eur(a)} €',f'{d} Tage',f'{E2(_int(a,z_tf,d))} €',f'{E2(_int(a,z_ad,d))} €',f'{E2(max(a*0.025,5.75))} €') for a,d in ((100,5),(200,20),(500,20),(500,45),(1000,45))])
    ext=lambda u,t: f'<a class="lnk" href="{u}" target="_blank" rel="noopener">{t}</a>'
    Q_VO=ext('https://gesetze.legal/eu/vo_eu_2021_1230/3','Artikel 3 der Verordnung (EU) 2021/1230')
    Q_EVZ=ext('https://www.evz.de/finanzen-versicherungen/geld-abheben-im-ausland.html','Europäisches Verbraucherzentrum')

    art('de','bargeld-abheben',pair='bargeld-beheben',
      h1='Geld abheben mit der Kreditkarte: Was es in Deutschland und im Ausland wirklich kostet',
      mt='Geld abheben mit Kreditkarte: Gebühren im Vergleich (Deutschland 2026) | Finvallo',
      desc='Geld abheben mit der Kreditkarte: Entgelte aller Karten in Deutschland, Inland gegen Ausland, Zinsfalle bei Gratiskarten und Rechenbeispiele.',
      lede='In Deutschland ist die Lage verkehrt herum: Viele Karten verlangen im Inland ein Entgelt und sind im Ausland kostenlos. Dazu kommen Automatenbetreiber, Fremdwährung und bei den Gratiskarten Zinsen ab dem ersten Tag.',
      kurz=(f'Von den {nprv} Privatkarten in unserem Deutschland-Vergleich heben {n_free} ohne Entgelt ab, {n_lim} mit einem monatlichen Freikontingent und {n_int} ohne Entgelt, aber mit Zinsen ab dem Buchungstag. '
            f'{n_pct} verlangen einen Prozentsatz, meist 2 bis 4 % mit 5 bis 7,50 € Mindestbetrag, {n_fix} einen Festbetrag je Abhebung. '
            f'Typisch deutsch: Hanseatic GenialCard, awa7 und Deutschland-Kreditkarte kosten 3,95 € im Inland und nichts im Ausland, Sparkasse und Volksbank verlangen im Inland 2 % und im Ausland nur das Auslandsentgelt. '
            f'Ohne Entgelt und ohne Fremdwährungsaufschlag weltweit: {L("dkb-visa-kreditkarte")}, {L("consorsbank-credit-card-gold-light")}, {L("c24-bank-smart")} und {L("trade-republic-karte")} ab 100 €; mit Zinsen ab dem ersten Tag {L("tf-bank-mastercard-gold")} und {L("advanzia-bank-gebuehrenfrei-mastercard-gold")}.'),
      secs=[
       ('Was eine Abhebung wirklich kostet: vier Posten',f'''<div class="prose"><p>Auf dem Kontoauszug steht eine Abhebung als ein Betrag. Dahinter stecken bis zu vier Posten:</p><ol>
<li><b>Das Entgelt deiner Bank.</b> Bei Charge-Karten der Filialbanken meist 2 bis 2,5 % mit 5 bis 7,50 € Mindestbetrag, bei American Express 4 %. Viele Direktbanken verlangen stattdessen einen Festbetrag (3,95 € bei Hanseatic und Deutschland-Kreditkarte) oder gar nichts. Die Besonderheit in Deutschland: Bei Sparkassen, Volksbanken, Hanseatic, awa7, Payback Visa und anderen gilt das Entgelt nur im Inland, im Ausland hebst du ohne Bankentgelt ab.</li>
<li><b>Das Auslandseinsatzentgelt.</b> Außerhalb des Euroraums kommen bei den meisten Karten 1,5 bis 2,5 % auf den Betrag, bei manchen dazu ein Umrechnungsentgelt von 0,5 %. Es gilt für Abhebungen wie für Zahlungen; die Details stehen im Ratgeber <a href="../fremdwaehrung/">Gebühren im Ausland</a>.</li>
<li><b>Das Entgelt des Automatenbetreibers.</b> In Deutschland verlangen Banken an fremden Automaten je nach Verbund 3 bis 10 € von Girocard-Nutzern; mit der Kreditkarte entfällt dieses Entgelt meist, weil die Abrechnung über Visa oder Mastercard läuft. Unabhängige Betreiber wie Euronet verlangen dagegen überall ein eigenes Entgelt, das vor der Bestätigung angezeigt wird.</li>
<li><b>Zinsen.</b> Bei echten Kreditkarten mit Kreditrahmen (TF Bank, Advanzia, GMX/WEB.DE, Hilton Honors, Eurowings, Instabank, Targobank) fallen auf Bargeld Sollzinsen ab dem Buchungstag an, auch wenn die Abhebung selbst kostenlos ist. Bei {n_zins} der {nprv} Privatkarten in unserem Vergleich steht das so in den Preisangaben.</li></ol>
<p>Charge-Karten von Sparkasse, Deutsche Bank, Commerzbank oder Postbank verrechnen keine Zinsen, weil der Betrag einmal im Monat vom Girokonto abgebucht wird; dafür liegt ihr Entgelt selten unter 2 %. Debitkarten der Direkt- und Neobanken (DKB, ING, C24, N26, Trade Republic) buchen sofort ab und sind beim Entgelt meist am günstigsten.</p></div>'''),
       ('Alle Karten im Vergleich: Entgelt, Fremdwährung, Zinsen','<p class="note">Sortiert nach Gebührenmodell: zuerst kostenlos, dann mit Freikontingent, dann verzinst, dann Festbetrag, dann Prozentsatz; innerhalb der Gruppe nach Jahresgebühr. „Bargeld“ ist das Entgelt der kartenausgebenden Bank je Abhebung, ohne Betreiberentgelt. Karten, die es nur für bestimmte Gruppen gibt, sind gekennzeichnet.</p>'+alle+
        f'''<div class="prose"><p>Ein paar Regeln aus dem Kleingedruckten, die in der Tabelle nur verkürzt stehen: DKB und ING verlangen einen Mindestbetrag von 50 € pro Abhebung, darunter kostet es (ING 1,95 €) oder geht nicht. {L("n26-standard")} ist in Euro zweimal im Monat gratis, in Fremdwährung immer 1,7 %. Bei American Express ist Bargeld erst sechs Monate nach Ausstellung und nach Freischaltung möglich, höchstens 750 € in sieben Tagen. Commerzbank Premium und Postbank mit Giro extra plus haben Kontingente, die an das Girokonto gebunden sind.</p>
<p class="note"><a class="lnk" href="{best}ausland/">Bestenliste: Karten ohne Auslandsgebühr →</a></p></div>'''),
       ('Die Zinsfalle: „0 € Gebühr“ bei TF Bank, Advanzia und GMX/WEB.DE',f'''<div class="prose"><p>{L("tf-bank-mastercard-gold")}, {L("advanzia-bank-gebuehrenfrei-mastercard-gold")} und die baugleiche {L("web-cent-mastercard-gold-gmx-web-de")} werben mit kostenlosen Abhebungen weltweit, und das stimmt: kein Entgelt, kein Auslandseinsatzentgelt. Der Haken steht daneben. Bargeld wird ab dem Buchungstag verzinst, bei TF Bank mit {E(KM.pct(z_tf))} Sollzins im Jahr, bei Advanzia mit 1,86 % im Monat ({E(KM.pct(z_ad))} im Jahr). Die zinsfreie Zeit, die für Einkäufe gilt, gibt es für Bargeld nicht.</p>
<p>Wie viel das ausmacht, hängt nur von Betrag und Tagen ab:</p></div>'''+zins_tbl+
        f'''<div class="prose"><p>Bei kleinen Beträgen und schneller Zahlung sind die Zinsen also billiger als das Entgelt einer Filialbank: 200 € für 20 Tage kosten rund {E2(_int(200,z_tf))} € statt 5,75 €. Teuer wird es, wenn du nur den Mindestbetrag der Rechnung zahlst; dann laufen die Zinsen Monat für Monat weiter. Wer die Karte für Bargeld nutzt, sollte die Rechnung deshalb immer vollständig begleichen. Ob du den Betrag schon vor der Rechnung zurücküberweisen kannst, steht in den Bedingungen der Karte; bei einer sofortigen Rückzahlung bleiben nur die Zinsen für wenige Tage.</p>
<p>Wer gar keine Zinsen will, hat in Deutschland mehr Auswahl als in Österreich: {L("dkb-visa-kreditkarte")}, {L("consorsbank-credit-card-gold-light")}, {L("hanseatic-bank-genialcard")} im Ausland, {L("deutschland-kreditkarte-classic")} im Ausland, {L("c24-bank-smart")} und {L("trade-republic-karte")} heben ohne Entgelt und ohne Zinsen ab, teils mit Mindestbetrag oder Monatskontingent.</p></div>'''),
       ('Rechenbeispiele: vier Situationen, zwanzig Karten','<p class="note">Entgelt der Bank für eine einzelne Abhebung, jeweils die erste im Monat, ohne Betreiberentgelt. Bei TF Bank und Advanzia stehen die Zinsen für 20 Tage bis zur Zahlung der Rechnung. Italien hat den Euro, deshalb fällt dort kein Auslandseinsatzentgelt an.</p>'+beispiele+
        f'''<div class="prose"><p>Drei Muster zeigen die Beispiele. Erstens: Im Inland sind die Direktbanken und die Festbetrag-Karten günstig, die Filialbanken teuer; 100 € bei der Sparkasse kosten 7,50 €, bei der Deutschen Bank 5,75 €, bei DKB, Consorsbank, C24 oder Trade Republic nichts. Zweitens: Im Euro-Ausland drehen sich die Verhältnisse bei vielen Karten um, weil das Inlandsentgelt wegfällt: Sparkasse, Volksbank, Hanseatic, Deutschland-Kreditkarte und Payback Visa heben in Italien ohne Entgelt ab. Drittens: Außerhalb des Euroraums entscheidet das Auslandseinsatzentgelt; {L("deutsche-bank-mastercard-standard")} und {L("postbank-mastercard")} liegen bei 500 € in der Türkei über 20 €, {L("american-express-card")} bei 30 €, die Karten ohne Auslandsentgelt bei null.</p>
<p>Der Mindestbetrag macht kleine Abhebungen unverhältnismäßig teuer: 50 € mit einer 2,5-Prozent-Karte und 5,75 € Minimum kosten 11,5 %. Lieber einmal 300 € als sechsmal 50 €, und bei DKB oder ING ohnehin mindestens 50 €.</p></div>'''),
       ('Euro-Ausland: Abhebungen dürfen nicht mehr kosten als zu Hause',f'''<div class="prose"><p>Innerhalb der EU gilt für Zahlungen in Euro eine einfache Regel: Deine Bank darf für eine grenzüberschreitende Zahlung in Euro nicht mehr verlangen als für dieselbe Zahlung im Inland ({Q_VO}). Für Abhebungen in Italien, Spanien, Kroatien oder Griechenland heißt das: dasselbe Entgelt wie in Deutschland, kein Auslandseinsatzentgelt. Ausgenommen sind nur die Währungsumrechnung und das Entgelt des Automatenbetreibers.</p>
<p>In Deutschland wirkt die Regel in beide Richtungen. Karten, die im Inland kostenlos sind, bleiben es im Euroraum. Karten mit Inlandsentgelt dürfen es auch in Italien verlangen; dass Sparkassen, Volksbanken oder Hanseatic im Ausland darauf verzichten, ist eine freiwillige Entscheidung der Bank, kein Gesetz. Mit der Girocard hebst du im Euroraum zu den Bedingungen deines Girokontos ab, meist an fremden Automaten gegen ein Entgelt der Automatenbank; für die Girocard ist die Kreditkarte im Ausland deshalb oft die günstigere Wahl, im Inland der eigene Automatenverbund.</p>
<p>In der Schweiz, in Großbritannien, Polen, Tschechien, Dänemark, der Türkei und überall außerhalb des Euroraums greift die Regel nicht. Dort zählt die Tabelle oben, und dort zahlt sich eine Karte ohne Auslandseinsatzentgelt am meisten aus.</p></div>'''),
       ('Betreiberentgelt und die Euro-Falle am Automaten','''<div class="prose"><p>Zwei Kosten entstehen erst am Gerät, und beide kannst du mit einem Blick auf den Bildschirm vermeiden.</p>
<p><b>Das Betreiberentgelt.</b> Unabhängige Betreiber, in Europa vor allem Euronet, verlangen für die Abhebung ein eigenes Entgelt, das vor der Bestätigung angezeigt wird. Es kommt zu allem dazu, was deine Bank berechnet, und keine Karte in unserem Vergleich erstattet es. Automaten von Banken verlangen es bei Kreditkarten seltener. Siehst du am Bildschirm ein Entgelt, brich ab und such den nächsten Bankautomaten.</p>
<p><b>Die Umrechnung in Euro.</b> Außerhalb des Euroraums fragt der Automat, ob er in Euro oder in Landeswährung abrechnen soll, oft mit einem vorgerechneten „garantierten“ Betrag. Wähle immer die Landeswährung. Entscheidest du dich für Euro, rechnet der Betreiber zu seinem eigenen Kurs um, und der ist fast immer deutlich schlechter als der Kurs von Visa oder Mastercard. Das Auslandseinsatzentgelt deiner Bank fällt trotzdem an, weil die Abhebung im Ausland stattfand.</p></div>'''),
       ('Girocard, Debitkarte oder Kreditkarte: was wofür',f'''<div class="prose"><p><b>Im Inland</b> ist die Girocard am eigenen Automatenverbund (Sparkassen, Cash Group der Großbanken, CashPool, BankCard ServiceNetz der Volksbanken) meist kostenlos, an fremden Automaten dagegen teuer. Direktbanken ohne eigene Automaten gleichen das mit kostenlosen Visa- oder Mastercard-Debitkarten aus: {L("dkb-visa-kreditkarte")} (ab 50 €), {L("ing-visa-card")} (ab 50 €, in Euro), {L("c24-bank-smart")} (viermal im Monat), {L("trade-republic-karte")} (ab 100 €), {L("n26-standard")} (zweimal im Monat).</p>
<p><b>Außerhalb des Euroraums</b> zählt das Auslandseinsatzentgelt. Ohne Aufschlag heben {L("dkb-visa-kreditkarte")}, {L("consorsbank-credit-card-gold-light")}, {L("c24-bank-smart")}, {L("trade-republic-karte")} und {L("revolut-standard")} (bis 200 € im Monat) ab; ING und N26 Standard verlangen in Fremdwährung 2,2 beziehungsweise 1,7 %. Die Girocard ist außerhalb des Euroraums oft gar nicht einsetzbar oder nur mit dem Entgelt des Girokontos.</p>
<p><b>Was die Debitkarte nicht kann:</b> Sie ersetzt keine Kreditkarte bei Mietwagen und manchen Hotels, die eine Kaution reservieren wollen. Für Reisen ist die Kombination deshalb ideal: eine Debitkarte für Bargeld, eine Kreditkarte für Kaution, Flug und Versicherung. Was beim Mietwagen gilt, steht im Ratgeber <a href="../mietwagen-kaution/">Mietwagen und Kaution</a>.</p></div>'''),
       ('Sechs Regeln für günstiges Bargeld','''<div class="prose"><ol>
<li><b>Wenige große Abhebungen statt vieler kleiner.</b> Mindestbeträge von 5 bis 7,50 € machen kleine Abhebungen teurer, als der Prozentsatz vermuten lässt; bei 2 % und 7,50 € Minimum zahlst du bis 375 € immer den Mindestbetrag.</li>
<li><b>Bankautomat statt Euronet.</b> Betreiberentgelte stehen am Bildschirm; bei einem Entgelt abbrechen und weitergehen.</li>
<li><b>Landeswährung wählen.</b> Nie die Umrechnung in Euro am Automaten annehmen.</li>
<li><b>Mindestbeträge kennen.</b> DKB und ING ab 50 €, Trade Republic ab 100 €; darunter kostet es oder geht nicht.</li>
<li><b>Mit Karte zahlen, wo es geht.</b> Bei Karten ohne Auslandseinsatzentgelt ist die Zahlung im Geschäft kostenlos, die Abhebung nicht immer.</li>
<li><b>Bei Gratiskarten die Rechnung sofort voll bezahlen.</b> Bei TF Bank, Advanzia und GMX/WEB.DE laufen die Zinsen ab dem Buchungstag; wer nur den Mindestbetrag zahlt, zahlt sie monatelang.</li></ol></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Entgelte und Zinsen: Preis- und Leistungsverzeichnisse der Anbieter, verlinkt auf jeder Kartenseite; die Werte werden beim Bauen dieser Seite aus den Kartendaten übernommen.</li>
<li>Gleiche Entgelte für grenzüberschreitende Zahlungen in Euro: {Q_VO}.</li>
<li>Betreiberentgelte, Anzeige am Automaten und Umrechnung in Euro: {Q_EVZ}.</li></ul></div>'''),
      ],
      faq=[
       ('Was kostet Geld abheben mit der Kreditkarte in Deutschland?','Bei Charge-Karten der Filialbanken 2 bis 2,5 % des Betrags, mindestens 5 bis 7,50 €, also 7,50 € für 100 € bei der Sparkasse oder 5,75 € bei der Deutschen Bank. Hanseatic GenialCard und Deutschland-Kreditkarte verlangen 3,95 € im Inland. Kostenlos sind DKB, Consorsbank Gold Light, C24, Trade Republic ab 100 € sowie TF Bank und Advanzia, bei den letzten beiden mit Zinsen ab dem Buchungstag.'),
       ('Welche Kreditkarte hebt im Ausland kostenlos ab?','Ohne Entgelt und ohne Auslandseinsatzentgelt: DKB Visa Kreditkarte (ab 50 €), Consorsbank Credit Card Gold Light, C24 Smart (viermal im Monat), Trade Republic (ab 100 €) und Revolut Standard bis 200 € im Monat. Hanseatic GenialCard, Deutschland-Kreditkarte und Payback Visa sind im Ausland ebenfalls ohne Entgelt. TF Bank und Advanzia verlangen kein Entgelt, verzinsen den Betrag aber ab dem ersten Tag.'),
       ('Warum kostet die Abhebung mit der Advanzia Mastercard Gold Zinsen?','Weil sie eine echte Kreditkarte ist: Bargeld gilt als Kredit und wird ab dem Abhebungstag mit 1,86 % im Monat verzinst, die zinsfreie Zeit gilt nur für Einkäufe. Bei 200 € und 20 Tagen bis zur Rechnung sind das rund 2,45 €, also weniger als das Entgelt einer Filialbank. Teuer wird es nur, wenn du die Rechnung nicht vollständig bezahlst.'),
       ('Warum ist die Sparkassen-Kreditkarte im Ausland billiger als im Inland?','Weil das Entgelt von 2 %, mindestens 7,50 €, nur für Abhebungen im Inland gilt; im Ausland verzichtet die Sparkasse darauf. Außerhalb des Euroraums fällt dann nur das Auslandseinsatzentgelt an, bei der Berliner Sparkasse 1,9 %. Die genauen Sätze unterscheiden sich je Sparkasse.'),
       ('Kostet Geld abheben in Italien oder Spanien mehr als in Deutschland?','Nein. Für Abhebungen in Euro innerhalb der EU darf deine Bank nicht mehr verlangen als im Inland. Bei vielen deutschen Karten ist es sogar weniger, weil das Inlandsentgelt im Ausland entfällt. Dazu kann ein Entgelt des Automatenbetreibers kommen, das am Bildschirm angezeigt wird.'),
       ('Soll ich am Automaten in Euro oder in Landeswährung abheben?','Immer in Landeswährung. Wählst du Euro, rechnet der Automatenbetreiber zu seinem eigenen, meist deutlich schlechteren Kurs um. Das Auslandseinsatzentgelt deiner Bank fällt in beiden Fällen an.'),
       ('Was ist das Betreiberentgelt am Geldautomaten?','Ein Entgelt, das der Betreiber des Automaten verlangt, nicht deine Bank. Es wird vor der Bestätigung angezeigt und kommt zu allen Entgelten deiner Karte dazu. Keine Karte in unserem Vergleich erstattet es. Bankautomaten verlangen es bei Kreditkarten seltener als unabhängige Betreiber wie Euronet.'),
       ('Kann ich mit American Express in Deutschland Geld abheben?','Ja, aber teuer und mit Hürden: 4 %, mindestens 5 €, dazu 2 % Auslandseinsatzentgelt außerhalb des Euroraums, höchstens 750 € in sieben Tagen (Gold und Platinum 1.500 €), und erst sechs Monate nach Ausstellung nach Freischaltung. Für Bargeld eignet sich daneben eine Visa- oder Mastercard besser.'),
      ],
      related=['fremdwaehrung','kostenlose-kreditkarte','reiseversicherung'])
