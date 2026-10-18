# Ratgeber (nur AT): „Bargeld beheben mit der Kreditkarte“. Alle Gebühren kommen live aus den Kartendaten
# (Felder cash/cashText, fx/fxText, fee, effz/soll). Aufruf aus ratgeber.build('at'): register(art,P,best,K,nprv,eur,KM)
import html
E=lambda s: html.escape(str(s)) if s is not None else ''

def _tbl(head,rows):
    h=''.join(f'<th>{c}</th>' for c in head)
    b=''.join('<tr>'+''.join(f'<td>{c}</td>' for c in r)+'</tr>' for r in rows)
    return f'<div class="tbl wide"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'

def kind(c):
    """Gruppe für Sortierung und Zählung: 0 kostenlos, 1 kostenlos mit Grenze, 2 kostenlos aber verzinst, 3 Fixbetrag, 4 Prozent."""
    v=c.get('cash') or []
    k=v[0] if v else None
    if k=='free': return 0
    if k=='freeN': return 1
    if k=='free_interest': return 2
    if k=='fix': return 0 if (len(v)>1 and v[1]==0) else 3
    return 4

# Gebühr der kartenausgebenden Bank für EINE Behebung (erste im Monat), ohne Betreibergebühr.
# eur_land: True = Behebung in Euro, sonst Fremdwährung. days: Tage bis zur Bezahlung (für verzinste Karten).
def cost(c,amount,eur_land,days=20):
    v=c.get('cash') or []; k=v[0] if v else None; s=c['slug']
    fx=(c.get('fx') or 0)/100
    fee=0.0; note=''
    if k=='free':
        if s.startswith('n26-') and s in ('n26-standard','n26-smart') and not eur_land: fee=amount*0.017; note='1,7 % in Fremdwährung'
        else: fee=0.0
    elif k=='free_interest':
        z=(c.get('soll') or c.get('effz') or 0)/100
        fee=amount*z*days/365; note=f'nur Zinsen, {days} Tage'
    elif k=='freeN':
        if s.startswith('revolut-'):
            lim={'revolut-standard':200,'revolut-plus':200,'revolut-premium':400,'revolut-metal':800,'revolut-ultra':2000}[s]
            over=max(0,amount-lim); fee=max(over*0.02,1) if over>0 else 0; note=f'bis {lim} € im Monat gratis'
        elif s=='wise-karte':
            over=max(0,amount-200); fee=(over*0.0175+0.5) if over>0 else 0; note='2× bis 200 € im Monat gratis'
        elif s=='card-complete-prepaid':
            fee=0; note='2 Behebungen im Monat gratis'
        else: fee=0
    elif k=='fix':
        if s=='trade-republic-karte': fee=1 if amount<100 else 0
        else: fee=v[1]
    elif k=='pctmin': fee=max(amount*v[1]/100,v[2])
    elif k=='fixpct': fee=v[1]+amount*v[2]/100
    else: return None,''
    if not eur_land: fee+=amount*fx
    return fee,note

BEISPIEL=['tf-bank-mastercard-gold','advanzia-bank-free-mastercard-gold','santander-card','n26-standard','n26-go','revolut-standard','wise-karte','trade-republic-karte',
          'easybank-kreditkarte','erste-bank-und-sparkassen-smartcard','raiffeisen-classic','bank-austria-classic','card-complete-classic-ohne-versicherung','paylife-classic','diners-club-classic','american-express-gold-card']

def register(art,P,best,K,nprv,eur,KM):
    T={c['slug']:c for c in K}
    priv=[c for c in K if c['art']=='Privat']
    def L(slug,label=None): return f'<a class="lnk" href="{P}at/kreditkarten/{slug}/">{E(label or T[slug]["titel"])}</a>'
    def fee(c):
        f=c.get('fee'); t='kostenlos' if f==0 else (f'{eur(f)} €' if f is not None else 'keine Angabe')
        return t+(' <small>(nur für bestimmte Gruppen)</small>' if c.get('nurfuer') else '')
    def zins(c): return 'ja' if kind(c)==2 else 'nein'
    def E2(x): return eur(round(x,2))
    n_free=len([c for c in priv if kind(c)==0]); n_lim=len([c for c in priv if kind(c)==1]); n_int=len([c for c in priv if kind(c)==2]); n_pct=len([c for c in priv if kind(c)==4]); n_fix=len([c for c in priv if kind(c)==3])
    typ={'Kreditkarte':'Kreditkarte','Charge':'Charge-Karte','Debit':'Debitkarte','Prepaid':'Prepaid'}
    order=sorted(priv,key=lambda c:(kind(c),c.get('fee') if c.get('fee') is not None else 1e9,c['titel']))
    alle=_tbl(['Karte','Typ','Jahresgebühr','Bargeld: Gebühr der Bank','Fremdwährung','Zinsen ab Behebung'],
              [(L(c['slug']),E(typ.get(c['typ'],c['typ'])),fee(c),E(KM.cashT(c)),E(KM.fxT(c)),zins(c)) for c in order])
    # Rechenbeispiele
    rows=[]
    for s in BEISPIEL:
        c=T[s]; a,na=cost(c,300,True); b,nb=cost(c,500,False); d,nd=cost(c,200,False)
        f=lambda x,n: ('kostenlos' if x==0 else f'{E2(x)} €')+(f' <small>({E(n)})</small>' if n else '')
        rows.append((L(s),f(a,na),f(b,nb),f(d,nd)))
    beispiele=_tbl(['Karte','300 € in Kroatien (Euro)','500 € in der Türkei (Lira)','200 € in Thailand (Baht)'],rows)
    tf=T['tf-bank-mastercard-gold']; ad=T['advanzia-bank-free-mastercard-gold']
    z_tf=(tf.get('soll') or tf.get('effz')); z_ad=(ad.get('soll') or ad.get('effz'))
    zins_tbl=_tbl(['Behebung','Tage bis zur Zahlung','Zinsen TF Bank','Zinsen Advanzia','Zum Vergleich: 3 %, mind. 4 €'],[
        (f'{eur(a)} €',f'{d} Tage',f'{E2(a*z_tf/100*d/365)} €',f'{E2(a*z_ad/100*d/365)} €',f'{E2(max(a*0.03,4))} €') for a,d in ((100,5),(200,20),(500,20),(500,45),(1000,45))])
    ext=lambda u,t: f'<a class="lnk" href="{u}" target="_blank" rel="noopener">{t}</a>'
    Q_VO=ext('https://gesetze.legal/eu/vo_eu_2021_1230/3','Artikel 3 der Verordnung (EU) 2021/1230')
    Q_EVZ=ext('https://www.evz.de/finanzen-versicherungen/geld-abheben-im-ausland.html','Europäisches Verbraucherzentrum')

    art('at','bargeld-beheben',pair='bargeld-abheben',
      h1='Bargeld beheben mit der Kreditkarte: Was es in Österreich und im Ausland wirklich kostet',
      mt='Bargeld beheben mit Kreditkarte: Gebühren im Vergleich (Österreich 2026) | Finvallo',
      desc='Was Bargeld am Bankomaten mit der Kreditkarte kostet: Gebühren aller Karten in Österreich, die Zinsfalle bei Gratiskarten und Rechenbeispiele für Kroatien, Türkei und Thailand.',
      lede='Bis zu vier Posten kommen bei einer Behebung zusammen: Bankgebühr, Fremdwährungsentgelt, Betreibergebühr und bei zwei Gratiskarten Zinsen ab dem ersten Tag.',
      kurz=(f'Von den {nprv} Privatkarten in unserem Vergleich beheben {n_free} ohne Gebühr, {n_lim} mit einem monatlichen Freikontingent und {n_int} ohne Gebühr, aber mit Zinsen ab dem Behebungstag. '
            f'{n_pct} verlangen einen Prozentsatz, meist 3 % mit 3,50 bis 4 € Mindestbetrag, {n_fix} einen Fixbetrag je Behebung. '
            f'Außerhalb des Euroraums kommt bei den meisten Hausbank-Karten das Fremdwährungsentgelt dazu, sodass 500 € in der Türkei je nach Karte 20 bis über 30 € kosten. '
            f'Am günstigsten sind {L("n26-go")} und {L("santander-card")} (kostenlos), {L("trade-republic-karte")} ab 100 € und, wenn du den Betrag schnell zurückzahlst, {L("tf-bank-mastercard-gold")} und {L("advanzia-bank-free-mastercard-gold")}.'),
      secs=[
       ('Was eine Behebung wirklich kostet: vier Posten','''<div class="prose"><p>Auf der Abrechnung erscheint eine Behebung als ein Betrag. Dahinter stecken bis zu vier Posten, und keine Karte nennt alle auf einen Blick:</p><ol>
<li><b>Die Bargeldgebühr deiner Bank.</b> Bei den meisten österreichischen Kreditkarten 3 % des Betrags, mindestens 3,50 bis 4 €. Bei Raiffeisen und Bank Direkt 0,35 € plus 3 %, bei easybank ein Fixbetrag von 3,63 €, bei PayLife und Oberbank 3,3 %. Sie fällt im Inland genauso an wie im Ausland.</li>
<li><b>Das Fremdwährungsentgelt.</b> Außerhalb des Euroraums kommen bei den Hausbank-Karten 1,35 bis 3,15 % auf den Betrag, teils mit Kursaufschlag. Es gilt für Behebungen genauso wie für Zahlungen; Details stehen im Ratgeber <a href="../fremdwaehrung/">Gebühren im Ausland</a>.</li>
<li><b>Die Gebühr des Automatenbetreibers.</b> Sie geht nicht an deine Bank, sondern an den Betreiber des Geräts, und sie steht in keinem Preisblatt. Betreiber wie Euronet zeigen sie vor der Bestätigung am Bildschirm an. Du kannst dann noch abbrechen.</li>
<li><b>Zinsen.</b> Bei echten Kreditkarten mit Kreditrahmen (TF Bank, Advanzia) ist die Behebung gebührenfrei, der Betrag wird aber ab dem Tag der Behebung verzinst, nicht erst nach der Rechnung.</li></ol>
<p>Charge-Karten der Hausbanken (Bank Austria, Erste, Raiffeisen, BAWAG, card complete, PayLife) verrechnen keine Zinsen, weil der Betrag einmal im Monat vom Konto abgebucht wird. Dafür kommen sie bei den Gebühren selten unter 3 %. Debitkarten der Neobanken (N26, Revolut, Wise, Trade Republic) buchen sofort vom Guthaben ab und sind bei der Gebühr meist am günstigsten.</p></div>'''),
       ('Alle Karten im Vergleich: Bargeldgebühr, Fremdwährung, Zinsen','<p class="note">Sortiert nach Gebührenmodell: zuerst kostenlos, dann mit Freikontingent, dann verzinst, dann Fixbetrag, dann Prozentsatz; innerhalb der Gruppe nach Jahresgebühr. „Bargeld“ ist die Gebühr der kartenausgebenden Bank je Behebung, ohne Betreibergebühr. Karten, die es nur für bestimmte Gruppen gibt, sind gekennzeichnet.</p>'+alle+
        f'''<div class="prose"><p>Zwei Besonderheiten stehen nicht in der Tabelle: Bei der {L("american-express-platinum-card")} ist Bargeld erst nach sechs bezahlten Monatsabrechnungen möglich. Bei {L("n26-standard")} und {L("n26-smart")} sind Behebungen in Euro unbegrenzt kostenlos, in Fremdwährung kosten sie 1,7 %; erst {L("n26-go")} und {L("n26-metal")} beheben auch in Fremdwährung gratis.</p>
<p class="note"><a class="lnk" href="{best}ausland/">Bestenliste: Karten ohne Auslandsgebühr →</a></p></div>'''),
       ('Die Zinsfalle: „0 € Behebungsgebühr“ bei TF Bank und Advanzia',f'''<div class="prose"><p>{L("tf-bank-mastercard-gold")} und {L("advanzia-bank-free-mastercard-gold")} werben mit kostenlosen Behebungen weltweit, und das stimmt: Es gibt keine Gebühr und kein Fremdwährungsentgelt. Der Haken steht im Preisblatt daneben. Bargeld wird ab dem Behebungstag verzinst, mit {E(KM.pct(z_tf))} (TF Bank) beziehungsweise {E(KM.pct(z_ad))} (Advanzia) im Jahr. Die zinsfreie Zeit, die für Einkäufe gilt, gibt es für Bargeld nicht.</p>
<p>Wie viel das ausmacht, hängt nur von Betrag und Tagen ab:</p></div>'''+zins_tbl+
        f'''<div class="prose"><p>Bei kleinen Beträgen und schneller Zahlung sind die Zinsen also deutlich billiger als die 3 % der Hausbanken: 200 € für 20 Tage kosten rund {E2(200*z_tf/100*20/365)} € statt 6 €. Teuer wird es, wenn du nur den Mindestbetrag der Rechnung zahlst; dann laufen die Zinsen auf den ganzen Betrag weiter, Monat für Monat. Wer die Karte für Bargeld nutzt, sollte die Rechnung deshalb immer vollständig begleichen. Ob du den Betrag schon vor der Rechnung zurücküberweisen kannst und wie das geht, steht in den Bedingungen der Karte; bei einer sofortigen Rückzahlung bleiben nur die Zinsen für wenige Tage.</p>
<p>Beide Karten gehören trotzdem zu den günstigsten Lösungen für Bargeld auf Reisen, weil der zweite große Posten, das Fremdwährungsentgelt, bei ihnen fehlt. Bei 500 € in Thailand sparst du gegenüber einer Hausbank-Karte mit 3 % plus 3,15 % Fremdwährung rund 25 € und zahlst dafür ein paar Euro Zinsen.</p></div>'''),
       ('Rechenbeispiele: drei Urlaube, sechzehn Karten','<p class="note">Gebühr der Bank für eine einzelne Behebung, jeweils die erste im Monat, ohne Betreibergebühr. Bei TF Bank und Advanzia stehen die Zinsen für 20 Tage bis zur Zahlung der Rechnung. Kroatien hat den Euro, deshalb fällt dort kein Fremdwährungsentgelt an.</p>'+beispiele+
        f'''<div class="prose"><p>Drei Dinge zeigen die Beispiele. Erstens: Im Euroraum spielt die Fremdwährung keine Rolle, dort zählt nur die Bargeldgebühr; die Hausbank-Karten kosten für 300 € etwa 9 €, die Neobanken nichts. Zweitens: Außerhalb des Euroraums verdoppelt sich die Rechnung bei den Hausbanken fast, weil 1,35 bis 3,15 % Fremdwährungsentgelt dazukommen; {L("bank-austria-classic")} und {L("card-complete-classic-ohne-versicherung")} liegen bei 500 € in der Türkei über 30 €. Drittens: Der Mindestbetrag macht kleine Behebungen unverhältnismäßig teuer. 50 € mit einer 3-Prozent-Karte kosten 4 €, also 8 %. Lieber einmal 300 € als sechsmal 50 €.</p>
<p>Die {L("american-express-gold-card")} steht in der Tabelle, weil viele sie auf Reisen dabeihaben: 3 % plus 2 % Fremdwährung sind für Bargeld ein schlechter Deal, und American Express wird an vielen Automaten gar nicht angenommen. Für Bargeld brauchst du daneben eine Visa- oder Mastercard.</p></div>'''),
       ('Euro-Ausland: Behebungen dürfen nicht mehr kosten als daheim',f'''<div class="prose"><p>Innerhalb der EU gilt für Zahlungen in Euro eine einfache Regel: Deine Bank darf für eine grenzüberschreitende Zahlung in Euro nicht mehr verlangen als für dieselbe Zahlung im Inland ({Q_VO}). Für Behebungen am Automaten in Italien, Spanien, Kroatien oder Griechenland heißt das: dieselbe Bargeldgebühr wie in Wien, kein Fremdwährungsentgelt. Ausgenommen sind nur Währungsumrechnung und die Gebühr des Automatenbetreibers.</p>
<p>Das hilft vor allem bei Karten, die im Inland günstig sind. Mit der Bankomatkarte deines Girokontos behebst du im Euroraum meist zu denselben Bedingungen wie zu Hause; was dein Konto dafür verlangt, steht in dessen Preisblatt, nicht im Preisblatt der Kreditkarte. Wer beides hat, nimmt im Euroraum die Bankomatkarte und spart sich die 3 % der Kreditkarte.</p>
<p>Umgekehrt ist auch klar: In der Schweiz, in Großbritannien, Tschechien, Polen, Ungarn, der Türkei und überall außerhalb des Euroraums greift die Regel nicht. Dort zählt die Tabelle oben, und dort lohnt sich eine Karte ohne Fremdwährungsentgelt am meisten.</p></div>'''),
       ('Betreibergebühr und die Euro-Falle am Automaten','''<div class="prose"><p>Zwei Kosten entstehen erst am Gerät, und beide kannst du mit einem Blick auf den Bildschirm vermeiden.</p>
<p><b>Die Betreibergebühr.</b> Unabhängige Betreiber, in Europa vor allem Euronet, verlangen für die Behebung eine eigene Gebühr, die vor der Bestätigung angezeigt wird. Sie kommt zu allem dazu, was deine Bank verrechnet, und keine Karte in unserem Vergleich erstattet sie. Automaten von Banken verlangen sie seltener. Siehst du am Bildschirm eine Gebühr, brich ab und such den nächsten Bankautomaten; in Städten ist er meist ein paar Hundert Meter entfernt.</p>
<p><b>Die Umrechnung in Euro.</b> Außerhalb des Euroraums fragt der Automat, ob er in Euro oder in Landeswährung abrechnen soll, oft mit einem vorgerechneten „garantierten“ Betrag. Wähle immer die Landeswährung. Entscheidest du dich für Euro, rechnet der Betreiber zu seinem eigenen Kurs um, und der ist fast immer deutlich schlechter als der Kurs von Visa oder Mastercard. Das Fremdwährungsentgelt deiner Bank fällt trotzdem an, weil die Behebung im Ausland stattfand. Warum das so ist, erklärt der Ratgeber <a href="../fremdwaehrung/">Gebühren im Ausland</a>.</p></div>'''),
       ('Debitkarte statt Kreditkarte: wann die Bankomatkarte besser ist',f'''<div class="prose"><p>Für Bargeld sind Debitkarten fast immer die bessere Wahl, weil das Geld direkt vom Konto kommt und keine Kreditkartenbank einen Prozentsatz dazwischenschaltet. Die Bankomatkarte deines Girokontos behebt an Automaten in Österreich und im Euroraum in der Regel zu den Konditionen deines Kontos, oft ohne Gebühr. Außerhalb des Euroraums verlangen die meisten Banken auch für die Bankomatkarte ein Entgelt; das steht im Preisblatt des Kontos.</p>
<p>Die Debitkarten der Neobanken sind für Reisen außerhalb des Euroraums gebaut: {L("n26-go")} und {L("n26-metal")} beheben unbegrenzt kostenlos, auch in Fremdwährung; {L("revolut-standard")} bis 200 € im Monat, die teureren Revolut-Tarife bis 400, 800 oder 2.000 €; {L("wise-karte")} zweimal bis 200 €; {L("trade-republic-karte")} ab 100 € kostenlos. N26, Revolut und Trade Republic rechnen laut unseren Daten ohne Aufschlag zum Kurs von Visa oder Mastercard um, Wise und bunq mit rund 0,5 %.</p>
<p>Was die Debitkarte nicht kann: Sie ersetzt keine Kreditkarte bei Mietwagen und manchen Hotels, die eine Kaution reservieren wollen. Für Reisen außerhalb des Euroraums ist die Kombination deshalb ideal: eine Debitkarte für Bargeld, eine Kreditkarte für Kaution, Flug und Versicherung. Was beim Mietwagen gilt, steht im Ratgeber <a href="../mietwagen-kaution/">Mietwagen und Kaution</a>.</p></div>'''),
       ('Sechs Regeln für günstiges Bargeld auf Reisen','''<div class="prose"><ol>
<li><b>Wenige große Behebungen statt vieler kleiner.</b> Der Mindestbetrag von 3,50 bis 4 € macht jede Behebung unter 130 € teurer als 3 %.</li>
<li><b>Bankautomat statt Euronet.</b> Betreibergebühren stehen am Bildschirm; bei einer Gebühr abbrechen und weitergehen.</li>
<li><b>Landeswährung wählen.</b> Nie die Umrechnung in Euro am Automaten annehmen.</li>
<li><b>Limit vorher prüfen.</b> Tages- und Monatslimits für Bargeld stehen in der App, und viele Banken lassen sie dort vorübergehend erhöhen. Eine abgelehnte Behebung im Ausland kostet zwar keine Gebühr, aber Zeit und Nerven.</li>
<li><b>Mit Karte zahlen, wo es geht.</b> Bei Karten ohne Fremdwährungsentgelt ist die Zahlung im Geschäft kostenlos, die Behebung nicht immer.</li>
<li><b>Bei Gratiskarten die Rechnung sofort voll bezahlen.</b> Bei TF Bank und Advanzia laufen die Zinsen ab dem Behebungstag; wer nur den Mindestbetrag zahlt, zahlt sie monatelang.</li></ol></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Gebühren und Zinsen: Preisblätter und Bedingungen der Anbieter, verlinkt auf jeder Kartenseite; Werte werden beim Bauen dieser Seite aus den Kartendaten übernommen.</li>
<li>Gleiche Entgelte für grenzüberschreitende Zahlungen in Euro: {Q_VO}.</li>
<li>Betreibergebühren, Anzeige am Automaten und Umrechnung in Euro: {Q_EVZ}.</li></ul></div>'''),
      ],
      faq=[
       ('Was kostet Bargeld beheben mit der Kreditkarte in Österreich?','Bei den meisten Karten der Hausbanken 3 % des Betrags, mindestens 3,50 bis 4 €, also 6 € für 200 €. Raiffeisen verlangt 0,35 € plus 3 %, easybank 3,63 € je Behebung, PayLife und Oberbank 3,3 %. Kostenlos beheben in Österreich N26, Santander, Trade Republic ab 100 € sowie TF Bank und Advanzia, bei den letzten beiden mit Zinsen ab dem Behebungstag.'),
       ('Welche Kreditkarte behebt im Ausland kostenlos?','Ohne Gebühr und ohne Fremdwährungsentgelt: N26 Go und N26 Metal, Santander Card, Trade Republic ab 100 €, Revolut innerhalb des Monatslimits (200 € beim Standard-Tarif) und Wise zweimal bis 200 €. TF Bank und Advanzia verlangen keine Gebühr, verzinsen den Betrag aber ab dem Behebungstag mit rund 25 % im Jahr.'),
       ('Warum kostet die Behebung mit der TF Bank Mastercard Gold Zinsen?','Weil die TF Bank Mastercard Gold eine echte Kreditkarte ist: Bargeld gilt als Kredit und wird ab dem Tag der Behebung verzinst, die zinsfreie Zeit gilt nur für Einkäufe. Bei 200 € und 20 Tagen bis zur Rechnung sind das rund 2,50 €, also weniger als die 6 € einer 3-Prozent-Karte. Teuer wird es nur, wenn du die Rechnung nicht vollständig bezahlst.'),
       ('Kostet Bargeld beheben in Italien oder Kroatien mehr als in Österreich?','Nein. Für Behebungen in Euro innerhalb der EU darf deine Bank nicht mehr verlangen als im Inland. Es fällt also nur die normale Bargeldgebühr deiner Karte an, kein Fremdwährungsentgelt. Dazu kann eine Gebühr des Automatenbetreibers kommen, die am Bildschirm angezeigt wird.'),
       ('Soll ich am Automaten in Euro oder in Landeswährung beheben?','Immer in Landeswährung. Wählst du Euro, rechnet der Automatenbetreiber zu seinem eigenen, meist deutlich schlechteren Kurs um. Das Fremdwährungsentgelt deiner Bank fällt in beiden Fällen an.'),
       ('Was ist die Betreibergebühr am Geldautomaten?','Eine Gebühr, die der Betreiber des Automaten verlangt, nicht deine Bank. Sie wird vor der Bestätigung angezeigt und kommt zu allen Gebühren deiner Karte dazu. Keine Karte in unserem Vergleich erstattet sie. Automaten von Banken verlangen sie seltener als unabhängige Betreiber wie Euronet.'),
       ('Ist die Bankomatkarte im Ausland günstiger als die Kreditkarte?','Im Euroraum meistens ja, weil die Bankomatkarte zu den Bedingungen deines Girokontos behebt und die Kreditkarte 3 % verlangt. Außerhalb des Euroraums kommt es auf das Preisblatt des Kontos an; dort sind die Debitkarten der Neobanken (N26, Revolut, Wise) oder die Gratiskarten von TF Bank und Advanzia meist günstiger.'),
       ('Kann ich mit American Express Bargeld beheben?','Ja, aber teuer: 3 %, mindestens 2,50 €, dazu 2 % Fremdwährungsentgelt außerhalb des Euroraums, und viele Automaten nehmen American Express nicht an. Bei der Platinum Card ist Bargeld erst nach sechs bezahlten Monatsabrechnungen möglich. Für Bargeld eignet sich daneben eine Visa- oder Mastercard besser.'),
      ],
      related=['fremdwaehrung','kostenlose-kreditkarte','reiseversicherung'])
