# Ratgeber „Kostenlose Kreditkarte“ für AT und DE (gleicher Slug, hreflang-Paar). Ersetzt die kurze Fassung in ratgeber.py.
# Abgrenzung zur Bestenliste „Gratis“ (Rangfolge): hier geht es um die versteckten Kosten, Rechenbeispiele und die Wahl
# zwischen Gratis-Kreditkarte, Gratis-Debitkarte und Karte mit Jahresgebühr. Alle Zahlen live aus den Kartendaten.
# Aufruf aus ratgeber.build(land): register(land,art,P,best,K,nprv,eur,KM,de1,pct)
import html
E=lambda s: html.escape(str(s)) if s is not None else ''
TIERN={0:'keine',1:'einzelne Bausteine',2:'mit Reiserücktritt',3:'umfassend',4:'Premium'}

def _tbl(head,rows):
    h=''.join(f'<th>{c}</th>' for c in head)
    b=''.join('<tr>'+''.join(f'<td>{c}</td>' for c in r)+'</tr>' for r in rows)
    return f'<div class="tbl wide"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'

def register(land,art,P,best,K,nprv,eur,KM,de1,pct):
    from score import cash200
    N={'at':'Österreich','de':'Deutschland'}[land]; AB={'at':'beheben','de':'abheben'}[land]; AUS={'at':'KSV1870','de':'SCHUFA'}[land]
    priv=[c for c in K if c['art']=='Privat' and not c.get('nurfuer')]
    free=[c for c in priv if c.get('fee')==0]
    credit=sorted([c for c in free if c['typ'] in ('Kreditkarte','Charge')],key=lambda c:-(c.get('stars') or 0))
    debit=sorted([c for c in free if c['typ'] in ('Debit','Prepaid')],key=lambda c:-(c.get('stars') or 0))
    first=[c for c in priv if c.get('fee1')==0 and (c.get('fee') or 0)>0]
    def L(c,label=None): return f'<a class="lnk" href="{P}{land}/kreditkarten/{c["slug"]}/">{E(label or c["titel"])}</a>'
    def S(slug): return next(c for c in K if c['slug']==slug)
    def ins(c): return TIERN.get(c.get('tier'),'keine Angabe') if c.get('tier') is not None else 'keine Angabe'
    def zins(c):
        z=c.get('effz') or c.get('soll'); return pct(z) if z else ('keine Teilzahlung' if c['typ'] in ('Charge','Debit','Prepaid') else 'keine Angabe')
    def konto(c): return 'ja' if c.get('giro') else ('nein' if c.get('giro') is False else 'keine Angabe')
    def stars(c): return f'{de1(c["stars"])} ★' if c.get('stars') is not None else 'ohne'
    typ={'Kreditkarte':'Kreditkarte mit Rahmen','Charge':'Charge-Karte','Debit':'Debitkarte','Prepaid':'Prepaid'}
    def row(c): return (L(c),E(typ.get(c['typ'],c['typ'])),E(KM.fxT(c)),E(KM.cashT(c)[:90]),E(zins(c)),konto(c),E(ins(c)),stars(c))
    head=['Karte','Typ','Zahlung Ausland','Bargeld','Zins bei Teilzahlung','Konto beim Anbieter nötig','Reiseversicherung','Bewertung']
    t_credit=_tbl(head,[row(c) for c in credit]); t_debit=_tbl(head,[row(c) for c in debit])
    # Rechenbeispiel: ein Jahr mit drei Nutzungsprofilen, für die Gratis-Kreditkarten und eine Classic-Karte der Hausbank
    ref=S({'at':'bank-austria-classic','de':'sparkasse-kreditkarte-classic'}[land])
    def fxcost(c,a): return a*(c.get('fx') or 0)/100
    def cashcost(c,n,a,days=20):
        v=cash200(c.get('cash'))
        if v=='fi': z=(c.get('soll') or c.get('effz') or 0)/100; return n*a*z*days/365
        if v in (None,'no'): return None
        if v=='fn': return 0.0
        return n*float(v)*(a/200)
    def ex(c):
        fee=c.get('fee') or 0
        a=fee                                   # Alltag: 600 € im Monat im Inland, Rechnung voll bezahlt
        b=fee+fxcost(c,1500); cc=cashcost(c,2,200); b=None if cc is None else b+cc   # Urlaub außerhalb des Euroraums: 1.500 € Zahlungen, zweimal 200 € Bargeld
        z=c.get('effz') or c.get('soll'); t=None if not z else fee+1000*z/100*0.5*0.5    # 1.000 € über sechs Monate abbezahlt: Zins auf den durchschnittlichen Restbetrag (500 €) für ein halbes Jahr
        f=lambda x:'keine Angabe' if x is None else ('0 €' if x<0.005 else f'{eur(round(x+1e-9,2))} €')
        return (L(c),f(a),f(b),f(t) if c['typ']=='Kreditkarte' else 'keine Teilzahlung')
    sample=credit[:8]+[ref]
    t_ex=_tbl(['Karte','Alltag: 600 € im Monat, Rechnung voll bezahlt','Urlaub außerhalb des Euroraums: 1.500 € Zahlung, 2× 200 € Bargeld','1.000 € über sechs Monate in Teilzahlung'],[ex(c) for c in sample])
    t_first=_tbl(['Karte','1. Jahr','Danach'],[(L(c),'0 €',f'{eur(c["fee"])} €') for c in sorted(first,key=lambda c:c['fee'])[:12]])
    n_fx0=len([c for c in credit if c.get('fx')==0]); n_fi=len([c for c in credit if cash200(c.get('cash'))=='fi']); n_konto=len([c for c in credit if c.get('giro')]); n_ins=len([c for c in credit if (c.get('tier') or 0)>=2])
    top=credit[0] if credit else None
    zs=sorted(c['effz'] for c in credit if c.get('effz'))
    reisen=f'{best}reisen/'; gratis=f'{best}gratis/'
    if land=='at':
        tf=S('tf-bank-mastercard-gold'); ad=S('advanzia-bank-free-mastercard-gold'); sa=S('santander-card')
        intro=f'''<div class="prose"><p>„Kostenlos“ steht auf vielen Karten, aber in {N} gibt es nur {len(credit)} echte Kredit- oder Charge-Karten ohne Jahresgebühr, die jeder beantragen kann: {L(tf)}, {L(ad)} und {L(sa)}. Dazu kommen {len(debit)} Debitkarten der App-Banken, die ebenfalls nichts kosten, aber keinen Kreditrahmen haben. Alle anderen „Gratis“-Angebote der Hausbanken sind entweder nur im ersten Jahr frei oder an ein Studenten- oder Jugendkonto gebunden.</p>
<p>Die drei Gratis-Kreditkarten verdienen ihr Geld anders: TF Bank und Advanzia an Zinsen, wenn du die Rechnung nicht vollständig zahlst oder Bargeld behebst, Santander an der Teilzahlung. Wer das weiß und die Karte entsprechend nutzt, zahlt wirklich nichts. Wer es nicht weiß, zahlt mehr als bei einer Karte mit Jahresgebühr.</p></div>'''
        duel=_tbl(['',L(tf),L(ad),L(sa)],[
            ('<b>Kreditrahmen</b>',E(tf.get('rahmen') or 'keine Angabe'),E(ad.get('rahmen') or 'keine Angabe'),E(sa.get('rahmen') or 'keine Angabe')),
            ('<b>Zinsfrei bei voller Zahlung</b>',f'bis {tf.get("zinsfrei")} Tage',f'bis {ad.get("zinsfrei")} Tage','keine Angabe'),
            ('<b>Effektivzins Teilzahlung</b>',E(pct(tf['effz'])),E(pct(ad['effz'])),E(pct(sa['effz']))),
            ('<b>Zahlung außerhalb des Euroraums</b>',E(KM.fxT(tf)),E(KM.fxT(ad)),E(KM.fxT(sa))),
            ('<b>Bargeld</b>','0 € Gebühr, Zinsen ab Behebungstag','0 € Gebühr, Zinsen ab Behebungstag','kostenlos'),
            ('<b>Reiseversicherung</b>','Reiserücktritt 3.000 €, Arztkosten 1.000.000 €, Gepäck 2.500 €','Reiserücktritt 3.000 €, Arztkosten 1.000.000 €, Gepäck 2.500 €','keine'),
            ('<b>Bezahlen der Rechnung</b>','Überweisung, kein automatischer Einzug','Überweisung, kein automatischer Einzug','Überweisung, kein automatischer Einzug'),
            ('<b>Extras</b>','Buchungsportal-Vorteile','Einkaufsschutz, Preisschutz','1 % Cashback, höchstens 50 € im Jahr')])
        duel_txt=f'''<div class="prose"><p>TF Bank und Advanzia sind sich sehr ähnlich: gleiche Versicherungssummen, gleiche Bargeldregel, fast gleicher Zins. Die Unterschiede liegen im Selbstbehalt der Reiseversicherung (TF Bank 100 € fix, Advanzia 20 %), bei den Altersgrenzen (ab 70 schrumpft bei Advanzia die versicherte Reisedauer) und im Einkaufsschutz, den nur Advanzia hat. Beide verlangen für eine gültige Reiseversicherung, dass du mindestens die Hälfte der Reise mit der Karte bezahlst; die Details stehen im Ratgeber <a href="../reiseversicherung/">Reiseversicherung über die Kreditkarte</a>. Die Santander Card ist die einfachere Karte: kostenlose Behebungen ohne Zinsregel, 1 % Cashback, dafür keine Versicherung, ein kleinerer Rahmen und ein Zins von {pct(sa['effz'])}, sobald du nicht den vollen Betrag zahlst.</p></div>'''
        konto_txt=f'''<div class="prose"><p>Keine der drei Gratis-Kreditkarten verlangt ein Konto bei der Bank; sie buchen von deinem bestehenden Girokonto ab oder werden per Überweisung bezahlt. Anders die Hausbanken: Ihre Gold-Karten sind nur im Studentenkonto gratis (easybank bis 27) oder im ersten Jahr. Was Studierende bekommen, steht im Ratgeber <a href="../kreditkarte-studenten/">Kreditkarte als Student</a>.</p></div>'''
        kurz=(f'In {N} gibt es {len(credit)} echte Kreditkarten ohne Jahresgebühr für alle: {L(tf)}, {L(ad)} und {L(sa)}; dazu {len(debit)} kostenlose Debitkarten von N26, Revolut, Wise, Trade Republic und Bitpanda. '
              f'Alle {len(credit)} verlangen 0 % im Ausland. Geld kosten sie nur in drei Fällen: Bargeld (TF Bank und Advanzia verzinsen es ab dem Behebungstag), Teilzahlung ({pct(zs[0])} bis {pct(zs[-1])} effektiv). '
              f'Wer die Rechnung immer vollständig zahlt und Bargeld mit der Bankomatkarte behebt, zahlt mit diesen Karten wirklich nichts. Die Rangfolge aller Gratiskarten zeigt die <a class="lnk" href="{gratis}">Bestenliste ohne Jahresgebühr</a>.')
        bank_txt=f'Bankomatkarte'
    else:
        tf=S('tf-bank-mastercard-gold'); ad=S('advanzia-bank-gebuehrenfrei-mastercard-gold'); hb=S('hanseatic-bank-genialcard'); eb=S('easybank-kreditkarte'); bn=S('bank-norwegian-visa-kreditkarte')
        intro=f'''<div class="prose"><p>In {N} ist die Auswahl groß: {len(credit)} echte Kredit- oder Charge-Karten ohne Jahresgebühr, die jeder beantragen kann, dazu {len(debit)} kostenlose Debitkarten. Das klingt nach einem Käufermarkt, aber „0 € Jahresgebühr“ sagt wenig. Die Banken verdienen an den Gratiskarten an vier Stellen: an Zinsen, wenn die Rechnung in Raten läuft (bei Hanseatic, awa7 und Deutschland-Kreditkarte ist die Teilzahlung voreingestellt), an Bargeld (3,95 € im Inland bei Hanseatic und Deutschland-Kreditkarte, Zinsen ab dem Buchungstag bei TF Bank, Advanzia und GMX/WEB.DE), am Auslandseinsatzentgelt (Amex Blue 2 %, Amazon Visa 1,5 %, TARGOBANK 3,85 %) und am Girokonto, das die Karte voraussetzt (Consorsbank, norisbank, Volksbank).</p>
<p>Die {L(eb)} zeigt den Extremfall: 0 € Jahresgebühr, aber 2 € im Monat, wenn du die Rechnung zu 100 % per Lastschrift begleichst, also genau dann, wenn du die Karte richtig nutzt. Wer das weiß und die Karte entsprechend nutzt, zahlt wirklich nichts. Wer es nicht weiß, zahlt mehr als bei einer Karte mit Jahresgebühr.</p></div>'''
        duel=_tbl(['',L(tf),L(ad),L(hb),L(bn)],[
            ('<b>Kreditrahmen</b>',E(tf.get('rahmen') or 'keine Angabe'),E(ad.get('rahmen') or 'keine Angabe'),E(hb.get('rahmen') or 'keine Angabe'),E(bn.get('rahmen') or 'keine Angabe')),
            ('<b>Zinsfrei bei voller Zahlung</b>',f'bis {tf.get("zinsfrei")} Tage',f'bis {ad.get("zinsfrei")} Tage','Teilzahlung voreingestellt; auf 100 % umstellen','keine Angabe'),
            ('<b>Effektivzins Teilzahlung</b>',E(pct(tf['effz'])),E(pct(ad['effz'])),E(pct(hb['effz'])),E(pct(bn['effz']))),
            ('<b>Zahlung außerhalb des Euroraums</b>',E(KM.fxT(tf)),E(KM.fxT(ad)),E(KM.fxT(hb)),E(KM.fxT(bn))),
            ('<b>Bargeld</b>','0 € Entgelt, Zinsen ab Buchungstag','0 € Entgelt, Zinsen ab Abhebungstag','3,95 € im Inland, 0 € im Ausland','0 €'),
            ('<b>Reiseversicherung</b>','Reiserücktritt 3.000 €, Auslandskranken 1.000.000 €','Reiserücktritt 3.000 €, Auslandskranken 1.000.000 €, nur Auslandsreisen','keine','Reiserücktritt laut Anbieter, Summen nur aus zweiter Hand'),
            ('<b>Extras</b>','keine','Käuferschutz, Preisschutz','keine','keine')])
        duel_txt=f'''<div class="prose"><p>TF Bank und Advanzia sind das Reise-Duo: 0 % im Ausland, Reiseversicherung, Bargeld ohne Entgelt. Ihr Preis ist der Zins, sobald die Rechnung nicht vollständig bezahlt wird oder Bargeld fließt; die baugleiche {L(S("web-cent-mastercard-gold-gmx-web-de"))} von GMX/WEB.DE bringt dazu 1 % WEB.Cent-Cashback. Die {L(hb)} und die {L(S("awa7-visa-kreditkarte"))} sind die Alltagskarten ohne Versicherung: 0 % im Ausland, im Ausland kostenlos abheben, aber mit voreingestellter Teilzahlung, die du beim ersten Login auf 100 % stellen solltest. Die {L(bn)} ist jung am deutschen Markt; ihre Reiseversicherung deckt Rücktritt bis 2.000 € pro Person, wenn du mindestens 75 % der Reise mit der Karte zahlst. Welche Karte wofür taugt, zeigt die <a href="../reiseversicherung/">Reiseversicherung über die Kreditkarte</a> und der Ratgeber <a href="../bargeld-abheben/">Geld abheben</a>.</p></div>'''
        konto_txt=f'''<div class="prose"><p>Ob die Karte ein Konto bei der Bank braucht, entscheidet über die wahren Kosten. {n_konto} der {len(credit)} Gratis-Kreditkarten gibt es nur zum eigenen Girokonto, und das ist nur unter Bedingungen kostenlos: Consorsbank und norisbank ab 500 bis 700 € Geldeingang oder unter 30 beziehungsweise 31, Volksbank im Beispiel der Berliner Volksbank mit 3,95 € im Monat fürs Konto. Ohne den Geldeingang kostet die „kostenlose“ Karte über das Konto 47 bis 59 € im Jahr. TF Bank, Advanzia, Hanseatic, awa7, Deutschland-Kreditkarte, Bank Norwegian, Amex Blue, PAYBACK Amex und Amazon Visa buchen dagegen von jedem Girokonto ab.</p></div>'''
        kurz=(f'In {N} gibt es {len(credit)} echte Kredit- oder Charge-Karten ohne Jahresgebühr für alle und {len(debit)} kostenlose Debitkarten. {n_fx0} der {len(credit)} verlangen 0 % im Ausland, {n_ins} enthalten eine Reiseversicherung mit Reiserücktritt ({L(tf)}, {L(ad)}, {L(S("web-cent-mastercard-gold-gmx-web-de"))}, {L(bn)}), {n_konto} gibt es nur zum Girokonto der Bank. '
              f'Geld kosten sie an vier Stellen: Teilzahlung ({pct(zs[0])} bis {pct(zs[-1])} effektiv, bei mehreren Karten voreingestellt), Bargeld (3,95 € im Inland bei Hanseatic und Deutschland-Kreditkarte, Zinsen ab Tag eins bei TF Bank und Advanzia), Auslandseinsatzentgelt bei Amex Blue, Amazon und TARGOBANK, und das Konto, das manche Karte voraussetzt. '
              f'Die Rangfolge aller Gratiskarten zeigt die <a class="lnk" href="{gratis}">Bestenliste ohne Jahresgebühr</a>.')
        bank_txt='Girocard'
    art(land,'kostenlose-kreditkarte',
      h1=f'Kostenlose Kreditkarte in {N}: Was „ohne Jahresgebühr“ wirklich heißt',
      mt=f'Kostenlose Kreditkarte {N}: Was gratis wirklich heißt (2026) | Finvallo',
      desc=f'Kostenlose Kreditkarte in {N}: {len(credit)} echte Karten ohne Jahresgebühr, wo sie bei Bargeld, Ausland und Teilzahlung trotzdem Geld kosten, mit Rechenbeispielen.',
      lede=f'Ohne Jahresgebühr heißt nicht kostenlos. Die Banken verdienen an Zinsen, Bargeld, Ausland und Konto. Hier steht, bei welcher Karte du wirklich bei 0 € bleibst und wie.',
      kurz=kurz,
      secs=[
       ('Wie Banken an Gratiskarten verdienen',intro),
       ('Alle Kreditkarten ohne Jahresgebühr im Vergleich','<p class="note">Kredit- und Charge-Karten ohne Jahresgebühr, die jeder beantragen kann, sortiert nach unserer Bewertung. „Zins bei Teilzahlung“ ist der Effektivzins, wenn du die Rechnung nicht vollständig zahlst; Charge-Karten kennen keine Teilzahlung. „Konto nötig“ heißt, die Karte gibt es nur zum Girokonto der Bank.</p>'+t_credit+
        f'<div class="prose"><p class="note"><a class="lnk" href="{gratis}">Bestenliste: Karten ohne Jahresgebühr, mit Sternen und Kategorie-Noten →</a></p></div>'),
       ('Die wichtigsten Gratis-Kreditkarten im Detail',duel+duel_txt),
       ('Rechenbeispiel: Was kostet die Gratiskarte in einem Jahr?','<p class="note">Drei Nutzungsprofile, Kosten für ein Jahr aus den Daten der Karten berechnet. Alltag: nur Inland, Rechnung immer vollständig bezahlt. Urlaub: 1.500 € Kartenzahlungen außerhalb des Euroraums plus zweimal 200 € Bargeld, Rechnung nach 20 Tagen bezahlt. Teilzahlung: 1.000 € Rechnung, über sechs Monate in gleichen Raten abbezahlt (Zins näherungsweise auf den durchschnittlichen Restbetrag von 500 €). Betreiberentgelte am Automaten nicht enthalten. Zum Vergleich die Classic-Karte einer Hausbank mit Jahresgebühr.</p>'+t_ex+
        f'''<div class="prose"><p>Das Muster ist in allen drei Spalten dasselbe. Im Alltag mit voller Rückzahlung kostet die Gratiskarte nichts, die Hausbank-Karte ihre Jahresgebühr. Im Urlaub außerhalb des Euroraums schlägt das Auslandseinsatzentgelt der Hausbank zu ({E(KM.fxT(ref))} bei der {L(ref)}), während die Gratiskarten mit 0 % nur ein paar Euro Zinsen fürs Bargeld kosten. Bei der Teilzahlung dreht sich das Bild: Dann kostet die Gratiskarte mit {pct(zs[-1])} effektiv mehr als die Jahresgebühr jeder Hausbank, und zwar jedes Jahr. Die Karte ist also für Vollzahler gratis und für Teilzahler teuer; warum, erklärt der Ratgeber <a href="../teilzahlung/">Teilzahlung</a>.</p></div>'''),
       ('Konto-Pflicht: wenn die Karte gratis ist, aber das Konto nicht',konto_txt),
       ('Gratis-Kreditkarte oder Gratis-Debitkarte?','<p class="note">Debit- und Prepaid-Karten ohne Jahresgebühr, sortiert nach unserer Bewertung. Sie buchen sofort vom Guthaben ab; es gibt keinen Kreditrahmen und keine Teilzahlung.</p>'+t_debit+
        f'''<div class="prose"><p>Für den Alltag und fürs Ausland sind die Debitkarten der App-Banken oft die günstigere Wahl: kein Zinsrisiko, kein Entgelt im Ausland, Bargeld innerhalb der Kontingente gratis, keine Bonitätsprüfung. Was sie nicht können: eine Kaution reservieren. Autovermieter und manche Hotels verlangen eine echte Kreditkarte mit Rahmen, und online bezahlst du Flüge oder Mietwagen mit einer Debitkarte sofort vom Konto statt erst mit der Monatsrechnung. Die Kombination aus einer Gratis-Debitkarte für den Alltag und einer Gratis-Kreditkarte für Kaution und Versicherung kostet zusammen 0 € und deckt beides ab. Was beim Mietwagen gilt, steht im Ratgeber <a href="../mietwagen-kaution/">Mietwagen und Kaution</a>, der Unterschied der Kartentypen im Ratgeber <a href="../kartentypen/">Kredit-, Charge-, Debit- oder Prepaid-Karte</a>.</p></div>'''),
       ('„1. Jahr gratis“ ist keine kostenlose Karte','<p class="note">Karten mit Jahresgebühr, die im ersten Jahr nichts kosten, nach dem regulären Preis sortiert. Aktionen ändern sich; der Stand steht auf jeder Kartenseite.</p>'+t_first+
        f'''<div class="prose"><p>Das Gratisjahr ist ein Lockangebot, kein Preis. Ab dem zweiten Jahr zahlst du die reguläre Jahresgebühr, meist ohne gesonderte Erinnerung. Sinnvoll ist das nur, wenn du die Karte ohnehin wegen ihrer Leistungen willst, etwa Lounge-Zugang oder Reiseversicherung, und das Gratisjahr als Rabatt nimmst. Wer nur eine kostenlose Karte sucht, ist mit den Karten oben besser bedient. Ab wann sich eine Karte mit Jahresgebühr rechnet, zeigt die Seite <a href="{best}lohnt-sich/">Top-Kreditkarten: ab wann sie sich lohnen</a>.</p></div>'''),
       ('Checkliste: so bleibt die Gratiskarte wirklich gratis',f'''<div class="prose"><ol>
<li><b>Rückzahlung auf 100 % stellen.</b> Bei Karten mit Kreditrahmen gleich nach dem ersten Login prüfen, ob Teilzahlung voreingestellt ist, und auf vollständige Zahlung umstellen.</li>
<li><b>Rechnung pünktlich zahlen.</b> Bei Karten ohne automatischen Einzug den Termin in den Kalender; ein Tag zu spät kostet Zinsen auf den ganzen Betrag.</li>
<li><b>Bargeld mit der {bank_txt} oder Debitkarte.</b> Die Gratis-Kreditkarten verzinsen Bargeld ab dem ersten Tag oder verlangen ein Entgelt; Zahlen im Ratgeber <a href="../{"bargeld-beheben" if land=="at" else "bargeld-abheben"}/">Bargeld {AB}</a>.</li>
<li><b>Am Terminal in Landeswährung zahlen.</b> Sonst frisst die Umrechnung des Händlers den Vorteil von 0 % Auslandsentgelt.</li>
<li><b>Konto-Bedingungen lesen.</b> Gilt „kostenlos“ nur mit Geldeingang, Alter oder Studentenstatus, rechne den Kontopreis dazu.</li>
<li><b>Zusatzkosten kennen.</b> Ersatzkarten, Papierrechnungen und Mahngebühren stehen im Preisblatt; sie sind bei Gratiskarten oft höher als bei Karten mit Jahresgebühr.</li></ol></div>'''),
       ('Quellen','''<div class="prose"><ul><li>Jahresgebühren, Zinsen, Gebühren im Ausland, Bargeld, Kontobedingungen und Versicherungsstufen: Preisblätter und Bedingungen der Anbieter, verlinkt auf jeder Kartenseite; alle Zahlen und Rechenbeispiele werden beim Bauen dieser Seite aus den Kartendaten übernommen.</li></ul></div>'''),
      ],
      faq=[
       (f'Welche kostenlose Kreditkarte ist in {N} die beste?',f'Laut unserer Bewertung die {top["titel"]} mit {de1(top["stars"])} von 5 Sternen, vor allem wegen 0 % im Ausland, kostenlosem Bargeld und Reiseversicherung. Die Rangfolge aller Karten ohne Jahresgebühr steht in der Bestenliste; welche zu dir passt, hängt davon ab, ob du Bargeld brauchst, reist oder in Raten zahlst.' if top else 'Aktuell keine.'),
       ('Ist eine kostenlose Kreditkarte wirklich gratis?','Die Jahresgebühr ist 0 €. Kosten entstehen bei Bargeld, Teilzahlung, teils im Ausland und beim Konto, das manche Karte voraussetzt. Wer die Rechnung vollständig zahlt, im Ausland eine Karte mit 0 % nutzt und Bargeld mit der Debitkarte holt, bleibt bei 0 €.'),
       ('Womit verdienen Banken an kostenlosen Kreditkarten?',f'An Zinsen bei Teilzahlung ({pct(zs[0])} bis {pct(zs[-1])} effektiv bei den Gratiskarten in unserem Vergleich), an Bargeld, am Auslandseinsatzentgelt und an der Händlergebühr bei jeder Zahlung. Dazu kommen bei manchen Karten Ersatzkarten, Papierrechnungen und Mahngebühren.'),
       ('Brauche ich für eine kostenlose Kreditkarte ein neues Girokonto?',f'{len(credit)-n_konto} der {len(credit)} Gratis-Kreditkarten in unserem Vergleich funktionieren mit deinem bestehenden Konto.'+(f' Ein Konto beim Anbieter brauchst du für {", ".join(c["titel"] for c in credit if c.get("giro"))}.' if n_konto else '')),
       (f'Wird bei einer kostenlosen Kreditkarte die Bonität geprüft?',f'Ja. Für jede echte Kredit- oder Charge-Karte prüft die Bank deine Bonität, in {N} über {"die SCHUFA" if land=="de" else "den KSV1870"}. Ohne Prüfung bekommst du nur Debit- und Prepaid-Karten.'),
       ('Was ist der Unterschied zwischen kostenloser Kreditkarte und kostenloser Debitkarte?','Die Kreditkarte hat einen Rahmen und rechnet einmal im Monat ab; sie eignet sich für Kautionen bei Mietwagen und Hotel. Die Debitkarte bucht sofort vom Guthaben ab, hat kein Zinsrisiko und keine Bonitätsprüfung, wird aber für Kautionen oft nicht akzeptiert.'),
       ('Lohnt sich eine Karte mit Jahresgebühr statt einer Gratiskarte?','Nur, wenn du die Leistungen nutzt, die die Gratiskarten nicht haben: Lounge-Zugang, Mietwagen-Vollkasko, höhere Versicherungssummen oder Punkteprogramme. Für Vollzahler ohne diese Wünsche ist die Gratiskarte fast immer günstiger.'),
       ('Was bedeutet „1. Jahr gratis“?',f'Die Jahresgebühr entfällt nur im ersten Jahr, danach gilt der reguläre Preis. In unserem Vergleich betrifft das aktuell {len(first)} Karten, von {eur(min(c["fee"] for c in first))} € bis {eur(max(c["fee"] for c in first))} € ab dem zweiten Jahr.' if first else 'Die Jahresgebühr entfällt nur im ersten Jahr, danach gilt der reguläre Preis.'),
      ],
      related=['kreditkarte-beantragen','fremdwaehrung','teilzahlung'])
