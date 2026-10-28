# Ratgeber „Kartentypen“ (AT und DE, gleicher Slug, hreflang-Paar): Kreditkarte, Charge-Karte, Debitkarte, Prepaid-Karte.
# Beide Fassungen sind eigenständig geschrieben (Begriffe, Rechtslage, Anbieter), die Zahlen kommen live aus den Kartendaten.
# Aufruf aus ratgeber.build(land): register(land,art,P,best,RC,eur,de1,pct)
import html
E=lambda s: html.escape(str(s)) if s is not None else ''
TYP={'Kreditkarte':'Kreditkarte mit Teilzahlung','Charge':'Charge-Karte','Debit':'Debitkarte','Prepaid':'Prepaid-Karte'}

def _tbl(head,rows):
    h=''.join(f'<th>{c}</th>' for c in head)
    b=''.join('<tr>'+''.join(f'<td>{c}</td>' for c in r)+'</tr>' for r in rows)
    return f'<div class="tbl wide"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'
def _lnk(c,P,land): return f'<a class="lnk" href="{P}{land}/kreditkarten/{c["slug"]}/">{E(c["titel"])}</a>'
def _fee(c,eur): return 'kostenlos' if c.get('fee')==0 else (f'{eur(c["fee"])} € im Jahr' if c.get('fee') is not None else 'Preis beim Anbieter')
def _span(xs,key):
    v=sorted(x[key] for x in xs if x.get(key) is not None)
    return (v[0],v[-1]) if v else None

def register(land,art,P,best,RC,eur,de1,pct):
    by={t:sorted([c for c in RC if c['typ']==t],key=lambda c:(-c['stars'],c.get('fee') or 0)) for t in TYP}
    n={t:len(v) for t,v in by.items()}; tot=len(RC)
    top=lambda t,k=3:by[t][:k]
    kk=by['Kreditkarte']; effz=_span(kk,'effz'); zf=_span(kk,'zinsfrei')
    fx0={t:sum(1 for c in by[t] if c.get('fx')==0) for t in TYP}
    gratis={t:sum(1 for c in by[t] if c.get('fee')==0) for t in TYP}
    giro={t:sum(1 for c in by[t] if c.get('giro')) for t in TYP}
    ins={t:sum(1 for c in by[t] if (c.get('tier') or 0)>=2) for t in TYP}
    rows=[]
    for t in TYP:
        xs=by[t]
        if not xs: continue
        rows.append([TYP[t],str(n[t]),f'{gratis[t]} kostenlos',f'{fx0[t]} mit 0 %',f'{ins[t]} mit Reiserücktritt',_lnk(xs[0],P,land)+f' ({de1(xs[0]["stars"])} ★)'])
    uebersicht=_tbl(['Kartentyp','Karten im Vergleich','Jahresgebühr','Fremdwährung','Reiseversicherung','Bestbewertet'],rows)
    def beispiele(t,k=4,extra=None):
        xs=top(t,k)
        if not xs: return ''
        head=['Karte','Jahresgebühr','Fremdwährung','Bewertung']+([extra[0]] if extra else [])
        rs=[[_lnk(c,P,land),_fee(c,eur),E(c.get('fxText') or ('0 %' if c.get('fx')==0 else '-')),f'{de1(c["stars"])} ★']+([extra[1](c)] if extra else []) for c in xs]
        return _tbl(head,rs)
    zins_col=('Zins bei Teilzahlung',lambda c:(pct(c['effz'])+' effektiv') if c.get('effz') else 'keine Angabe')
    tage_col=('Zinsfrei bis',lambda c:(f'{c["zinsfrei"]} Tage') if c.get('zinsfrei') else 'bis zur Abbuchung')

    if land=='at':
        bl=f'{best}'
        art('at','kartentypen',pub='2026-10-11',about='Kartentypen in Österreich',
          h1='Kreditkarte, Charge-Karte, Debitkarte oder Prepaid: Was passt zu dir?',
          mt='Kartentypen Österreich: Kredit, Charge, Debit, Prepaid | Finvallo',
          desc=f'Die vier Kartentypen in Österreich erklärt: Kreditkarte mit Teilzahlung, Charge-Karte der Hausbank, Debitkarte, Prepaid. Mit Zahlen aus {tot} Karten.',
          lede='„Kreditkarte“ steht in Österreich auf vielen Karten, die gar keinen Kredit geben. Was die vier Typen unterscheidet, wo du beim Mietwagen scheiterst und welcher Typ zu dir passt.',
          kurz=f'In Österreich sind {n["Charge"]} der {tot} bewerteten Karten Charge-Karten (Monatsabrechnung vom Konto), nur {n["Kreditkarte"]} echte Kreditkarten mit Teilzahlung, dazu {n["Debit"]} Debitkarten und {n["Prepaid"]} Prepaid-Karten. Für Mietwagen und Hotels brauchst du eine Charge- oder Kreditkarte; für den Alltag und fürs Ausland sind Debitkarten der App-Banken oft günstiger.',
          secs=[
           ('Die vier Typen auf einen Blick',f'<div class="prose"><p>Alle vier zahlen kontaktlos, online und im Ausland. Der Unterschied liegt darin, <b>wann</b> das Geld von deinem Konto geht und <b>wer</b> dafür haftet, wenn es nicht da ist.</p></div>'+uebersicht+'<p class="note">Zahlen aus dem Finvallo-Vergleich für Österreich, nur bewertete Privatkarten.</p>'),
           ('Charge-Karte: der österreichische Normalfall',f'<div class="prose"><p>Was Bank Austria, Erste Bank, BAWAG, Raiffeisen oder card complete als „Kreditkarte“ verkaufen, ist fast immer eine Charge-Karte: Die Bank sammelt deine Umsätze einen Monat lang und bucht die Summe dann in einem Stück von deinem Girokonto ab. Zinsen fallen nicht an, weil du nichts in Raten zahlst. Du bekommst einen Rahmen, der sich nach deiner Bonität richtet, und einen Zahlungsaufschub von bis zu sechs Wochen.</p>'
            f'<p>Der Preis dafür ist die Jahresgebühr: {gratis["Charge"]} der {n["Charge"]} Charge-Karten sind kostenlos, der Rest kostet zwischen rund 20 € und über 400 € im Jahr. Dafür steckt bei {ins["Charge"]} von ihnen eine Reiseversicherung mit Storno drin, und Mietwagenfirmen akzeptieren sie für die Kaution. Bei {giro["Charge"]} von ihnen brauchst du ein Girokonto derselben Bank.</p></div>'+beispiele('Charge',4,tage_col)),
           ('Echte Kreditkarte: Teilzahlung ist möglich, aber teuer',f'<div class="prose"><p>Nur {n["Kreditkarte"]} Karten in unserem Österreich-Vergleich sind Kreditkarten im Wortsinn, vor allem die gebührenfreien Karten von TF Bank und Advanzia. Du bekommst eine Monatsrechnung und entscheidest selbst, ob du alles oder nur einen Teil überweist. Der Rest wird zum Kredit, '+(f'mit {pct(effz[0])} bis {pct(effz[1])} effektivem Jahreszins' if effz else 'mit Zinsen von über 20 %')+'. Solange du die Rechnung komplett und pünktlich zahlst, kostet die Karte nichts.</p>'
            f'<p>Zwei Dinge sollten Österreicherinnen und Österreicher wissen: Erstens ziehen diese Banken die Rechnung meist nicht per Lastschrift ein, du musst selbst überweisen, sonst läuft die Teilzahlung automatisch an. Zweitens gilt bei Bargeldbehebungen oft keine zinsfreie Zeit; die Zinsen laufen ab dem Tag der Behebung. Für Kautionen und Reiseversicherung sind diese Karten dagegen so gut wie Charge-Karten, einige sogar besser.</p></div>'+beispiele('Kreditkarte',4,zins_col)+f'<p class="note">Mehr zu Raten und Zinsen im <a class="lnk" href="{P}at/ratgeber/teilzahlung/">Ratgeber Teilzahlung</a>.</p>'),
           ('Debitkarte: Bankomatkarte und App-Banken',f'<div class="prose"><p>Die klassische Bankomatkarte deines Girokontos ist eine Debitkarte: Jede Zahlung geht sofort vom Konto ab. Neu ist, dass Debitkarten von Visa und Mastercard („Debit Mastercard“, „Visa Debit“) inzwischen fast überall funktionieren, wo Kreditkarten gehen, auch online und im Ausland. Darauf setzen N26, Revolut, bunq, Trade Republic und Tomorrow, die in Österreich gar keine Charge-Karten anbieten.</p>'
            f'<p>Der Vorteil: {fx0["Debit"]} der {n["Debit"]} Debitkarten im Vergleich verlangen 0 % Aufschlag in Fremdwährung, bei Charge-Karten der Hausbanken sind es meist 1,5 bis 2 %. Der Nachteil: Mietwagenfirmen und manche Hotels blocken auf Debitkarten keine Kaution oder nur gegen hohe Sicherheitsleistung, und Reiseversicherung gibt es nur in den bezahlten Premium-Stufen. Ein Konto beim Anbieter brauchst du immer.</p></div>'+beispiele('Debit',4)+f'<p class="note">Alle Debitkarten in der <a class="lnk" href="{bl}debit/">Bestenliste Debit &amp; App-Banken</a>.</p>'),
           ('Prepaid-Karte: Guthaben statt Bonität',f'<div class="prose"><p>Eine Prepaid-Karte lädst du vorher auf und zahlst nur, was drauf ist. Deshalb fragt der Anbieter nicht beim KSV1870 nach, und auch Jugendliche oder Menschen mit negativer Bonitätsauskunft bekommen sie. In Österreich ist die Auswahl klein: {n["Prepaid"]} Prepaid-Karten stehen im Vergleich. Sie kosten oft Gebühren fürs Aufladen oder eine Jahresgebühr, und beim Mietwagen gelten sie wie Debitkarten.</p>'
            f'<p>Wer eine Karte ohne Bonitätsprüfung sucht, fährt mit der kostenlosen Debitkarte einer App-Bank meist besser als mit Prepaid, weil es dort weder Lade- noch Jahresgebühr gibt. Details im <a class="lnk" href="{P}at/ratgeber/ohne-bonitaetspruefung/">Ratgeber Kreditkarte ohne KSV-Abfrage</a>.</p></div>'+beispiele('Prepaid',3)),
           ('Welcher Typ passt zu dir?','<div class="prose"><ul>'
            '<li><b>Du mietest Autos oder buchst Hotels:</b> Charge-Karte oder echte Kreditkarte. Nur dort blockt der Vermieter die Kaution problemlos.</li>'
            '<li><b>Du willst Reiseversicherung mit Storno:</b> Charge- oder Kreditkarte mit Versicherungspaket, meist ab der Gold-Stufe. Debit nur bei Premium-Abos.</li>'
            '<li><b>Du zahlst oft in Fremdwährung:</b> Debitkarte einer App-Bank oder eine der wenigen Charge-Karten mit 0 % Aufschlag.</li>'
            '<li><b>Du willst keine Rechnung vergessen:</b> Charge-Karte der Hausbank, die Abbuchung läuft automatisch. Bei TF Bank und Advanzia musst du selbst überweisen.</li>'
            '<li><b>Du hast keine oder eine schlechte Bonität:</b> Debit- oder Prepaid-Karte. Beide brauchen keinen Kreditrahmen.</li>'
            '<li><b>Du willst Raten zahlen können:</b> Echte Kreditkarte, aber nur als Reserve. Dauerhaft sind die Zinsen zu hoch; ein Ratenkredit ist günstiger.</li></ul>'
            f'<p>Viele Österreicherinnen und Österreicher kombinieren: die Bankomatkarte fürs Inland, eine kostenlose Charge- oder Kreditkarte für Reisen und Kautionen. Den Preis bei deiner Nutzung rechnet der <a class="lnk" href="{P}at/kreditkarten/rechner/">Kartenrechner</a> aus.</p></div>'),
           ('Was auf der Karte steht und was es heißt','<div class="prose"><p>Auf Debitkarten steht „Debit“ unter dem Visa- oder Mastercard-Logo, oft auch „Debit Mastercard“ in der Kartennummer-Zeile. Charge- und Kreditkarten tragen keinen Zusatz. Ob eine Karte Teilzahlung erlaubt, erkennst du am Preisblatt: Steht dort ein Sollzins für die Teilzahlung, ist es eine echte Kreditkarte. Steht nur ein Überziehungszins fürs Konto, ist es eine Charge-Karte. Im Finvallo-Vergleich zeigt jede Kartenseite den Typ oben neben dem Namen.</p></div>')],
          faq=[('Ist eine Charge-Karte eine Kreditkarte?','Für Händler, Hotels und Mietwagenfirmen ja: Sie läuft über Visa oder Mastercard und hat einen Rahmen. Im Wortsinn nein, weil die Bank den Monatsumsatz komplett abbucht und keine Raten anbietet. In Österreich sind fast alle Bankkarten mit Kreditkartenlogo Charge-Karten.'),
               ('Kann ich mit einer Debitkarte ein Auto mieten?',f'Oft nicht oder nur mit Einschränkungen. Viele Vermieter verlangen eine Charge- oder Kreditkarte auf den Namen des Fahrers, weil sie die Kaution darauf blocken. Details im <a class="lnk" href="{P}at/ratgeber/mietwagen-kaution/">Ratgeber Mietwagen und Kaution</a>.'),
               ('Welche Karte bekomme ich ohne KSV-Abfrage?','Debit- und Prepaid-Karten, weil sie keinen Kreditrahmen haben. Charge- und Kreditkarten prüfen die Bonität immer.'),
               ('Was kostet die Teilzahlung bei einer echten Kreditkarte?',(f'Bei den Karten im Vergleich {pct(effz[0])} bis {pct(effz[1])} effektiv im Jahr.' if effz else 'Über 20 % effektiv im Jahr.')+' Zahlst du die Rechnung komplett bis zur Fälligkeit, fallen keine Zinsen an.'),
               ('Ist die Bankomatkarte eine Debitkarte?','Ja. Jede Zahlung geht sofort vom Girokonto ab. Neuere Bankomatkarten laufen als Debit Mastercard oder Visa Debit und funktionieren damit auch online und im Ausland.')],
          related=['visa-mastercard-amex','mietwagen-kaution','ohne-bonitaetspruefung','teilzahlung'])
    else:
        bl=f'{best}'
        art('de','kartentypen',pub='2026-10-11',about='Kartentypen in Deutschland',
          h1='Kartentypen in Deutschland: Kreditkarte, Charge, Debit oder Prepaid?',
          mt='Kartentypen Deutschland: Kreditkarte, Debit, Prepaid | Finvallo',
          desc=f'Kreditkarte, Charge, Debit und Prepaid in Deutschland erklärt: Unterschiede bei Abrechnung, Schufa, Mietwagen und Gebühren. Zahlen aus {tot} Karten.',
          lede='Seit DKB, ING und die Sparkassen auf Debitkarten umgestellt haben, ist der Unterschied zwischen „Visa Card“ und echter Kreditkarte für viele zur Falle geworden. Hier steht, was die vier Typen können und wo sie scheitern.',
          kurz=f'Von {tot} bewerteten Karten in Deutschland sind {n["Kreditkarte"]} echte Kreditkarten mit Teilzahlung, {n["Charge"]} Charge-Karten mit Monatsabrechnung, {n["Debit"]} Debitkarten und {n["Prepaid"]} Prepaid-Karten. Für Mietwagen, Hotels und Reiseversicherung brauchst du eine Kredit- oder Charge-Karte; Debitkarten sind im Alltag und fürs Ausland oft günstiger, scheitern aber an der Kaution.',
          secs=[
           ('Die vier Typen auf einen Blick','<div class="prose"><p>Alle vier laufen über Visa oder Mastercard (bei Amex nur Charge und Kredit) und funktionieren an denselben Terminals. Der Unterschied: <b>wann</b> das Geld von deinem Konto geht, <b>ob</b> ein Kreditrahmen dahintersteht und <b>wie</b> die Schufa ins Spiel kommt.</p></div>'+uebersicht+'<p class="note">Zahlen aus dem Finvallo-Vergleich für Deutschland, nur bewertete Privatkarten.</p>'),
           ('Echte Kreditkarte: Rahmen, Rechnung, Teilzahlung',f'<div class="prose"><p>Die klassische Kreditkarte gibt dir einen Kreditrahmen. Du bekommst einmal im Monat eine Abrechnung und kannst wählen: alles zahlen oder in Raten. {n["Kreditkarte"]} Karten im Vergleich funktionieren so, darunter fast alle gebührenfreien Karten von Direktbanken und Kartenanbietern wie Bank Norwegian, TF Bank, Advanzia, Hanseatic oder Barclays-Nachfolger easybank. Der Haken ist der Zins bei Teilzahlung: '+(f'{pct(effz[0])} bis {pct(effz[1])} effektiv im Jahr' if effz else 'oft über 20 % effektiv')+'. Wer die Rechnung komplett zahlt, zahlt nichts.</p>'
            f'<p>Achte auf die Voreinstellung: Einige Anbieter stellen die Teilzahlung automatisch ein, du musst auf 100 % umstellen oder jeden Monat selbst überweisen. Bei Bargeldabhebungen laufen bei vielen dieser Karten die Zinsen ab dem ersten Tag. Zinsfrei bleibt der Einkauf bis zur Fälligkeit, '+(f'je nach Karte {zf[0]} bis {zf[1]} Tage' if zf else 'meist rund sieben Wochen')+'.</p></div>'+beispiele('Kreditkarte',5,zins_col)+f'<p class="note">Rechenbeispiele im <a class="lnk" href="{P}de/ratgeber/teilzahlung/">Ratgeber Teilzahlung</a>.</p>'),
           ('Charge-Karte: die Kreditkarte der Hausbanken',f'<div class="prose"><p>Sparkassen, Volksbanken, Deutsche Bank, Commerzbank, Postbank und die Filialbanken geben meist Charge-Karten aus: Umsätze werden gesammelt und einmal im Monat komplett vom Girokonto abgebucht. Raten gibt es nicht, Zinsen deshalb auch nicht, dafür einen echten Rahmen, den Vermieter und Hotels für die Kaution blocken können. {n["Charge"]} Charge-Karten stehen im Vergleich; {giro["Charge"]} davon gibt es nur zum Girokonto derselben Bank, {ins["Charge"]} enthalten eine Reiseversicherung mit Storno.</p>'
            f'<p>Preislich sind Charge-Karten die teuerste Gruppe: {gratis["Charge"]} der {n["Charge"]} sind kostenlos, die Gold-Stufen der Hausbanken kosten 60 bis 120 € im Jahr und verlangen im Ausland meist 1,75 bis 2 % Aufschlag. Dafür bekommst du Filiale, Beratung und bei vielen eine Lastschrift, die keine Rechnung vergisst.</p></div>'+beispiele('Charge',4,tage_col)),
           ('Debitkarte: girocard und „Visa Card“ der Direktbanken',f'<div class="prose"><p>Die girocard (früher EC-Karte) ist die bekannteste Debitkarte: sofortige Abbuchung, keine Kreditlinie. Seit 2021 haben DKB, ING, comdirect, Consorsbank und viele Sparkassen ihre Standardkarte auf eine <b>Visa Debit</b> oder <b>Debit Mastercard</b> umgestellt. Die sieht aus wie eine Kreditkarte, bucht aber sofort ab, und genau das führt zu Problemen: Mietwagenfirmen und Hotels lehnen sie für die Kaution häufig ab, und manche Händler im Ausland erkennen sie nicht als Kreditkarte an.</p>'
            f'<p>Im Alltag ist die Debitkarte dafür oft die günstigste Wahl: {gratis["Debit"]} der {n["Debit"]} Debitkarten im Vergleich sind kostenlos, {fx0["Debit"]} verlangen 0 % in Fremdwährung. Neobanken wie N26, Revolut, bunq, Trade Republic oder Scalable geben in Deutschland nur Debitkarten aus. Ein Konto beim Anbieter brauchst du immer.</p></div>'+beispiele('Debit',5)+f'<p class="note">Alle Debitkarten in der <a class="lnk" href="{bl}debit/">Bestenliste Debit &amp; App-Banken</a>.</p>'),
           ('Prepaid-Karte: ohne Schufa, aber mit Gebühren',f'<div class="prose"><p>Prepaid-Karten funktionieren nur mit vorher eingezahltem Guthaben. Weil kein Kredit dahintersteht, gibt es keine Schufa-Abfrage; sie sind die typische Karte für Jugendliche, für Menschen mit negativem Schufa-Eintrag oder als Zweitkarte mit festem Budget. {n["Prepaid"]} Prepaid-Karten stehen im Vergleich, darunter die Guthabenkarten von Sparkassen, Commerzbank und PAYBACK sowie Krypto-Karten wie Crypto.com. Viele verlangen Jahresgebühr oder Ladegebühren, und beim Mietwagen gelten sie wie Debitkarten.</p>'
            f'<p>Wer nur die Schufa umgehen will, bekommt mit einer kostenlosen Debitkarte einer Direkt- oder Neobank meist mehr fürs Geld. Welche Karten ohne Schufa-Abfrage auskommen, steht im <a class="lnk" href="{P}de/ratgeber/ohne-bonitaetspruefung/">Ratgeber Kreditkarte ohne Schufa</a>.</p></div>'+beispiele('Prepaid',4)),
           ('Welcher Typ passt zu dir?','<div class="prose"><ul>'
            '<li><b>Mietwagen, Hotel, Kaution:</b> echte Kreditkarte oder Charge-Karte. Mit Debit und Prepaid riskierst du am Schalter eine Absage.</li>'
            '<li><b>Reiseversicherung mit Rücktritt:</b> Kredit- oder Charge-Karte mit Versicherungspaket, bei Debit nur in Premium-Abos wie N26 Go oder Revolut Premium.</li>'
            '<li><b>Zahlen im Ausland:</b> gebührenfreie Kreditkarte oder Debitkarte einer Neobank mit 0 % Fremdwährungsentgelt; die Charge-Karten der Hausbanken sind hier die teuersten.</li>'
            '<li><b>Keine Rechnung vergessen:</b> Charge-Karte mit Lastschrift oder eine Kreditkarte, bei der du den Ausgleich auf 100 % per Lastschrift stellst.</li>'
            '<li><b>Ohne Schufa oder mit festem Budget:</b> Debit oder Prepaid.</li>'
            '<li><b>Raten zahlen können:</b> echte Kreditkarte, aber nur als Reserve. Für größere Summen ist ein Ratenkredit deutlich billiger.</li></ul>'
            f'<p>Die typische Kombination in Deutschland: girocard oder Debitkarte des Girokontos für den Alltag, dazu eine kostenlose echte Kreditkarte für Reisen und Kautionen. Was dich das bei deiner Nutzung kostet, rechnet der <a class="lnk" href="{P}de/kreditkarten/rechner/">Kartenrechner</a>.</p></div>'),
           ('So erkennst du den Typ','<div class="prose"><p>Auf Debitkarten steht „Debit“ unter dem Netzwerklogo, oft auch im Namen („Visa Debitkarte“, „Debit Mastercard“). Prepaid-Karten tragen „Prepaid“ oder „auf Guthabenbasis“ im Namen. Kreditkarten und Charge-Karten sehen gleich aus; der Unterschied steht im Preis- und Leistungsverzeichnis: Nennt es einen Sollzins für Teilzahlung oder einen „Kreditrahmen mit Ratenzahlung“, ist es eine echte Kreditkarte. Steht nur „Abrechnung monatlich per Lastschrift“, ist es eine Charge-Karte. Im Finvallo-Vergleich steht der Typ auf jeder Kartenseite oben neben dem Namen.</p></div>')],
          faq=[('Ist die Visa Card der DKB oder ING eine Kreditkarte?','Nein, beide sind Debitkarten: Jede Zahlung geht sofort vom Girokonto ab, es gibt keinen Kreditrahmen. Deshalb nehmen Mietwagenfirmen sie oft nicht für die Kaution. Beide Banken bieten gegen Aufpreis zusätzlich eine echte Kreditkarte an.'),
               ('Was ist der Unterschied zwischen Charge-Karte und Kreditkarte?','Beide haben einen Rahmen und rechnen monatlich ab. Die Charge-Karte bucht die Summe komplett vom Konto ab, die Kreditkarte lässt dich in Raten zahlen (gegen Zinsen). Für Händler, Hotels und Vermieter sind beide „Kreditkarten“.'),
               ('Kann ich mit einer Debitkarte ein Auto mieten?',f'Oft nicht oder nur mit hoher Kaution und Zusatzversicherung. Die meisten Vermieter verlangen eine echte Kreditkarte oder Charge-Karte auf den Namen des Fahrers. Details im <a class="lnk" href="{P}de/ratgeber/mietwagen-kaution/">Ratgeber Mietwagen und Kaution</a>.'),
               ('Welche Karte gibt es ohne Schufa?','Prepaid-Karten und die meisten Debitkarten, weil beide keinen Kreditrahmen haben. Kredit- und Charge-Karten fragen die Schufa immer ab.'),
               ('Wie teuer ist die Teilzahlung?',(f'Bei den Karten im Vergleich {pct(effz[0])} bis {pct(effz[1])} effektiv im Jahr.' if effz else 'Meist zwischen 15 und 25 % effektiv im Jahr.')+' Wer die Abrechnung komplett bis zur Fälligkeit begleicht, zahlt keine Zinsen.')],
          related=['visa-mastercard-amex','mietwagen-kaution','ohne-bonitaetspruefung','teilzahlung'])
