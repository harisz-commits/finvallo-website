# Ratgeber „Teilzahlung“ für AT und DE (gleicher Slug, hreflang-Paar). Ersetzt die statische Kurzfassung.
# Zinsen, zinsfreie Fristen, Rückzahlungsweg und Rahmen kommen live aus den Kartendaten (soll, effz, zinsfrei, auto, rahmen).
# Die Rechenbeispiele sind ein Tilgungsmodell mit offen genannten Annahmen (Mindestrate 3 %, mindestens 30 €).
# Aufruf aus ratgeber.build(land): register(land,art,P,best,K,nprv,eur,KM,de1,pct)
import html
E=lambda s: html.escape(str(s)) if s is not None else ''

def _tbl(head,rows):
    h=''.join(f'<th>{c}</th>' for c in head)
    b=''.join('<tr>'+''.join(f'<td>{c}</td>' for c in r)+'</tr>' for r in rows)
    return f'<div class="tbl wide"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'

def monthly(c):
    """Monatszins aus dem Sollzins; fehlt er, aus dem Effektivzins zurückgerechnet."""
    if c.get('soll'): return c['soll']/100/12
    if c.get('effz'): return (1+c['effz']/100)**(1/12)-1
    return None
def amort(B,r,pct=0.03,mn=30.0,fix=None,cap=600):
    bal=B; m=0; tot=0.0
    while bal>0.005 and m<cap:
        i=bal*r; tot+=i; bal+=i
        pay=fix if fix else max(pct*bal,mn); pay=min(pay,bal); bal-=pay; m+=1
    return m,tot

def register(land,art,P,best,K,nprv,eur,KM,de1,pct):
    N={'at':'Österreich','de':'Deutschland'}[land]; AUS={'at':'KSV1870','de':'SCHUFA'}[land]
    priv=[c for c in K if c['art']=='Privat']
    rev=sorted([c for c in priv if c['typ']=='Kreditkarte' and (c.get('soll') or c.get('effz'))],key=lambda c:(c.get('effz') or c.get('soll') or 99))
    charge_opt=[c for c in priv if c['typ']=='Charge' and (c.get('soll') or c.get('effz'))]
    def L(c,label=None): return f'<a class="lnk" href="{P}{land}/kreditkarten/{c["slug"]}/">{E(label or c["titel"])}</a>'
    def fee(c):
        f=c.get('fee'); return ('kostenlos' if f==0 else (f'{eur(f)} €' if f is not None else 'keine Angabe'))+(' <small>(nur für bestimmte Gruppen)</small>' if c.get('nurfuer') else '')
    def z(v): return pct(v) if v else 'keine Angabe'
    def zf(c):
        v=c.get('zinsfrei')
        return 'keine' if v==0 else (f'bis {v} Tage' if v else 'keine Angabe')
    def weg(c):
        if c.get('autoNote'): return c['autoNote'][:140]+('…' if len(c['autoNote'])>140 else '')
        return 'Lastschrift möglich' if c.get('auto') else ('Überweisung, kein Einzug' if c.get('auto') is False else 'keine Angabe')
    preset=[c for c in rev if 'voreingestellt' in (c.get('autoNote') or '')]
    def E2(x): return eur(round(x+1e-9,2))
    tbl=_tbl(['Karte','Jahresgebühr','Sollzins p. a.','Effektivzins p. a.','Zinsfrei bei voller Zahlung','Rückzahlung laut Anbieter','Rahmen laut Anbieter'],
             [(L(c),fee(c),E(z(c.get('soll'))),E(z(c.get('effz'))),E(zf(c)),E(weg(c)),E(c.get('rahmen') or 'keine Angabe')) for c in rev])
    # Rechenbeispiele
    rows=[]
    seen=set(); ex=[]
    for c in rev:
        rate=c.get('effz') or c.get('soll')
        if land=='de' and (rate in seen or len(ex)>=11): continue
        seen.add(rate); ex.append(c)
    hi_c0=max((c for c in rev if c.get('effz')),key=lambda c:c['effz'])
    if hi_c0 not in ex: ex.append(hi_c0)
    for c in ex:
        r=monthly(c)
        if r is None: continue
        m1,t1=amort(1000,r); m2,t2=amort(1000,r,fix=100); m3,t3=amort(2000,r)
        rows.append((L(c),E(z(c.get('effz')) if c.get('effz') else z(c.get('soll'))+' (Sollzins, Effektivzins keine Angabe)'),f'{E2(t1)} € Zinsen, {m1} Monate',f'{E2(t2)} € Zinsen, {m2} Monate',f'{E2(t3)} € Zinsen, {m3//12} Jahre und {m3%12} Monate'))
    t_ex=_tbl(['Karte','Zinssatz p. a.','1.000 € mit Mindestrate (3 %, mind. 30 €)','1.000 € mit 100 € im Monat','2.000 € mit Mindestrate'],rows)
    zs=[c.get('effz') for c in rev if c.get('effz')]; lo,hi=min(zs),max(zs)
    lo_c=next(c for c in rev if c.get('effz')==lo); hi_c=next(c for c in rev if c.get('effz')==hi)
    n_auto=len([c for c in rev if c.get('auto')]); n_ueb=len([c for c in rev if c.get('auto') is False])
    reisen=f'{best}gratis/'
    r_hi=monthly(hi_c); m_hi,t_hi=amort(1000,r_hi); m_hf,t_hf=amort(1000,r_hi,fix=100)
    hz=(f'{z(hi_c["soll"])} Sollzins' if hi_c.get('soll') else f'{z(hi)} effektiv')
    hzl=f'{hi_c["titel"]} ({hz})'
    if land=='at':
        intro=f'''<div class="prose"><p>In {N} ist die klassische Kreditkarte eine Charge-Karte: Die Bank zieht die Monatsrechnung vollständig vom Konto ein, Zinsen gibt es nicht. Echte Kreditkarten mit Teilzahlung sind die Ausnahme, in unserem Vergleich {len(rev)} Karten: {", ".join(L(c) for c in rev)}. Dazu bieten {L(next(c for c in charge_opt if "easybank" in c["slug"]))} und die Erste-Karten eine Teilzahlungsfunktion als Option zur Charge-Karte an, bei der Erste mit {z(next(c for c in charge_opt if "erste" in c["slug"]).get("effz"))} effektiv deutlich günstiger.</p>
<p>Die Gratiskarten von TF Bank und Advanzia leben von der Teilzahlung. Sie verlangen keine Jahresgebühr, dafür {z(hi)} effektiv, sobald die Rechnung nicht vollständig bezahlt wird. Weil diese Karten per Überweisung bezahlt werden und kein automatischer Einzug läuft, reicht ein vergessener Termin, und die Teilzahlung beginnt von selbst.</p></div>'''
        ausschalten=f'''<div class="prose"><p>Bei TF Bank und Advanzia gibt es keinen Schalter, den du umlegen könntest: Die Rechnung kommt einmal im Monat, und du überweist den vollen Betrag bis zum Fälligkeitstag. Alles, was fehlt, wird zum verzinsten Kredit. Trag den Termin in den Kalender oder richte einen Dauerauftrag mit Puffer ein, den du bei Bedarf anpasst. Bei der Santander Card ist es genauso; sie wird ebenfalls per Überweisung bezahlt. Bei easybank und Erste ist die Teilzahlung eine Option im Online-Banking; wer sie nie aktiviert, zahlt keine Zinsen.</p>
<p>Ob die Rechnung vollständig bezahlt ist, siehst du in der App oder im Kundenportal unter dem offenen Saldo. Steht dort nach dem Zahltag noch ein Betrag, läuft die Teilzahlung.</p></div>'''
        vergleich=f'''<div class="prose"><p>Zum Vergleich: Ein Ratenkredit einer Bank oder der Rahmen am Girokonto kosten in der Regel weniger als die {z(hi)} der Gratis-Kreditkarten; die genauen Sätze stehen in den Preisblättern der Banken und hängen von Bonität und Laufzeit ab. Wer einen Betrag länger als zwei oder drei Monate braucht, fährt mit einem Ratenkredit fast immer besser als mit der Kartenteilzahlung. Für ein paar Tage bis zur nächsten Gehaltszahlung ist die Teilzahlung dagegen verkraftbar: 1.000 € für einen Monat kosten bei {hz} rund {E2(1000*r_hi)} €.</p>
<p>Die Zinsen der Kreditkarten in {N} müssen als Effektivzins angegeben werden; er enthält den Sollzins und die Art der Verzinsung, nicht aber Jahresgebühr oder Bargeldentgelte. Vergleiche deshalb immer den Effektivzins, nicht den Sollzins; bei Advanzia werden aus 1,86 % im Monat {z(hi)} im Jahr.</p></div>'''
        kurz=(f'Von den Privatkarten in unserem {N}-Vergleich erlauben {len(rev)} eine Teilzahlung: {", ".join(L(c) for c in rev)}, mit {z(lo)} bis {z(hi)} effektivem Jahreszins. '
              f'Charge-Karten der Hausbanken kennen keine Teilzahlung, easybank und Erste bieten sie als Option. '
              f'Bei den Gratiskarten läuft die Teilzahlung automatisch an, sobald die Rechnung nicht vollständig per Überweisung bezahlt ist: 1.000 € mit der Mindestrate kosten bei der {hzl} rund {E2(t_hi)} € Zinsen und dauern {m_hi} Monate, mit 100 € im Monat {E2(t_hf)} € und {m_hf} Monate. Wer die Rechnung immer vollständig zahlt, zahlt auf Einkäufe keine Zinsen. Bargeld verzinsen manche Karten trotzdem ab dem Abhebungstag.')
    else:
        intro=f'''<div class="prose"><p>In {N} ist die Teilzahlung bei Kreditkarten weit verbreitet: {len(rev)} der Privatkarten in unserem Vergleich sind echte Kreditkarten mit Kreditrahmen und Teilzahlungsfunktion, von Direktbanken (Hanseatic, Advanzia, TF Bank, Bank Norwegian, Consors Finanz, Openbank), Handelspartnern (Amazon, IKEA, ADAC) und Airlines (Miles &amp; More, Eurowings, Turkish Airlines). Bei {len(preset)} davon ist die Teilzahlung laut Preisverzeichnis voreingestellt ({', '.join(L(c) for c in preset)}): Wer nach dem Antrag nichts ändert, zahlt jeden Monat nur die Mindestrate und auf den Rest Zinsen.</p>
<p>Die Spanne ist groß: {z(lo)} effektiv bei der {L(lo_c)} bis {z(hi)} bei der {L(hi_c)}. Die Miles &amp; More Karten der Deutschen Bank liegen mit {z(10.05)} Sollzins am unteren Ende, die Gratiskarten von Advanzia, TF Bank und GMX/WEB.DE sowie Bank Norwegian mit 24 bis 25 % am oberen. Charge-Karten der Filialbanken (Sparkasse, Deutsche Bank, Commerzbank, Postbank) kennen keine Teilzahlung; Klarna und Volkswagen Bank bieten sie als Option an.</p></div>'''
        ausschalten=f'''<div class="prose"><p>Bei den meisten deutschen Karten ist die Teilzahlung eine Einstellung: In der App oder im Kundenportal stellst du die Rückzahlung auf 100 % („Gesamtbetrag per Lastschrift“) um, und die Bank zieht die ganze Rechnung ein. {n_auto} der {len(rev)} Teilzahlungskarten bieten den Lastschrifteinzug an. Prüfe die Einstellung gleich nach dem ersten Login; bei {len(preset)} Modellen aus unserem Vergleich steht sie laut Preisverzeichnis standardmäßig auf Teilzahlung mit 2,5 bis 10 % Mindestrate. Bei der easybank Kreditkarte kostet die 100-Prozent-Lastschrift 2 € im Monat; gratis bleibt dort nur die Vollzahlung per Überweisung oder der Soforteinzug in der App.</p>
<p>Bei TF Bank, Bank Norwegian, Instabank und Miles &amp; More myFlex gibt es keinen Einzug: Du überweist die Rechnung selbst bis zum Fälligkeitstag, und was fehlt, wird zum verzinsten Kredit. Trag den Termin in den Kalender oder richte einen Dauerauftrag mit Puffer ein. Ob die Rechnung vollständig bezahlt ist, siehst du am offenen Saldo in der App; steht dort nach dem Zahltag noch ein Betrag, läuft die Teilzahlung.</p></div>'''
        vergleich=f'''<div class="prose"><p>Zum Vergleich: Ein Ratenkredit oder der Dispo am Girokonto kosten in der Regel weniger als die 20 bis 25 % der Gratis-Kreditkarten; die genauen Sätze stehen in den Preisverzeichnissen und hängen von Bonität und Laufzeit ab. Wer einen Betrag länger als zwei oder drei Monate braucht, fährt mit einem Ratenkredit fast immer besser als mit der Kartenteilzahlung. Für ein paar Tage bis zum nächsten Gehalt ist die Teilzahlung verkraftbar: 1.000 € für einen Monat kosten bei {hz} rund {E2(1000*r_hi)} €.</p>
<p>Die Zinsen müssen als Effektivzins angegeben werden; er enthält den Sollzins und die Art der Verzinsung, nicht aber Jahresgebühr oder Bargeldentgelte. Bei Hanseatic GoldCard und Deutschland-Kreditkarte Gold liegt der Effektivzins deshalb deutlich über dem Sollzins, weil die Jahresgebühr eingerechnet wird. Vergleiche immer den Effektivzins, und bei Monatsangaben (Advanzia: 1,86 % im Monat) rechne auf das Jahr hoch.</p></div>'''
        kurz=(f'{len(rev)} der Privatkarten in unserem {N}-Vergleich sind echte Kreditkarten mit Teilzahlung, mit {z(lo)} ({L(lo_c)}) bis {z(hi)} ({L(hi_c)}) effektivem Jahreszins. '
              f'Bei {len(preset)} davon ist die Teilzahlung voreingestellt (unter anderem Hanseatic, awa7, Deutschland-Kreditkarte, easybank, Eurowings, IKEA); bei TF Bank, Bank Norwegian und Instabank läuft sie an, sobald die Rechnung nicht vollständig überwiesen ist. '
              f'1.000 € mit der Mindestrate kosten bei der {hzl} rund {E2(t_hi)} € Zinsen und dauern {m_hi} Monate, mit 100 € im Monat {E2(t_hf)} € und {m_hf} Monate. Wer die Rückzahlung auf 100 % stellt, zahlt auf Einkäufe keine Zinsen. Bargeld verzinsen manche Karten trotzdem ab dem Abhebungstag.')
    art(land,'teilzahlung',
      h1=f'Teilzahlung bei Kreditkarten in {N}: Was sie kostet und wie du sie abschaltest',
      mt=f'Teilzahlung bei Kreditkarten in {N}: Zinsen aller Karten, Rechenbeispiele | Finvallo',
      desc=f'Teilzahlung bei Kreditkarten in {N}: Effektivzinsen aller Karten mit Kreditrahmen, was 1.000 € mit Mindestrate kosten und wie du sie abschaltest.',
      lede='Die Rate klingt klein, der Zins ist es nicht. Hier stehen die Zinsen aller Karten mit Teilzahlung, was ein Restbetrag über Monate kostet und welche Einstellung dich davor schützt.',
      kurz=kurz,
      secs=[
       ('Was Teilzahlung ist und warum sie die Gratiskarten finanziert',intro+'''<div class="prose"><p>Teilzahlung (auch Revolving Credit oder Ratenfunktion) heißt: Du musst die Monatsrechnung nicht ganz bezahlen, sondern nur eine Mindestrate, bei den Karten in unserem Vergleich 2,5 bis 10 % des offenen Betrags mit einem Mindestbetrag von 15 bis 50 €. Der Rest bleibt als Kredit stehen und wird verzinst. Die zinsfreie Frist von 49 bis 90 Tagen, mit der viele Karten werben, gilt nur, wenn du die Rechnung vollständig bezahlst. Bleibt etwas offen, verzinsen viele Banken nicht nur den Rest, sondern neue Einkäufe ab dem Buchungstag; die Frist ist dann weg. Bargeld wird bei fast allen Karten mit Teilzahlung ab dem Buchungstag verzinst, zinsfreie Frist oder nicht.</p></div>'''),
       ('Alle Karten mit Teilzahlung im Vergleich','<p class="note">Echte Kreditkarten mit Kreditrahmen und Teilzahlungsfunktion, sortiert nach Effektivzins. „Zinsfrei bei voller Zahlung“ ist die längste Frist zwischen Einkauf und Fälligkeit; sie gilt nur, wenn die Rechnung komplett bezahlt wird. „Rückzahlung laut Anbieter“: ob die Bank den Betrag einziehen kann oder du selbst überweisen musst, und was voreingestellt ist.</p>'+tbl+
        f'''<div class="prose"><p>Die Sortierung zeigt das Muster: Je weniger die Karte kostet, desto höher der Zins. Die Karten ohne Jahresgebühr liegen fast alle über 20 %, die Karten mit Jahresgebühr (ADAC, TARGOBANK Gold, Openbank, Miles &amp; More) darunter. Die Bank holt sich das Geld entweder über die Gebühr oder über den Zins; wer die Rechnung immer vollständig zahlt, umgeht beides nur bei der Gratiskarte.</p>
<p class="note"><a class="lnk" href="{reisen}">Bestenliste: Karten ohne Jahresgebühr →</a></p></div>''' if land=='de' else f'''<div class="prose"><p class="note"><a class="lnk" href="{reisen}">Bestenliste: Karten ohne Jahresgebühr →</a></p></div>'''),
       ('Rechenbeispiele: was ein Restbetrag wirklich kostet','<p class="note">Tilgungsmodell mit den Zinsen der Karte: monatliche Verzinsung aus dem Sollzins (fehlt er, aus dem Effektivzins zurückgerechnet), Mindestrate 3 % des offenen Betrags, mindestens 30 €, keine neuen Einkäufe. Die tatsächliche Mindestrate der Karte kann abweichen; sie steht im Preisblatt. Jahresgebühren sind nicht enthalten.</p>'+t_ex+
        f'''<div class="prose"><p>Die Mindestrate ist die Falle, nicht der Zins allein. Bei der {L(hi_c)} ({hz}) kosten 1.000 € mit der Mindestrate rund {E2(t_hi)} € Zinsen und sind erst nach {m_hi} Monaten getilgt, weil die Rate mit dem Saldo schrumpft und gegen Ende fast nur noch Zinsen deckt. Mit einer festen Rate von 100 € ist derselbe Betrag nach {m_hf} Monaten weg und kostet {E2(t_hf)} €. Bei 2.000 € mit Mindestrate wird aus der Rechnung ein Kredit über Jahre, mit Zinsen in der Größenordnung des geliehenen Betrags.</p>
<p>Die Regel daraus: Wenn Teilzahlung, dann mit einer festen, möglichst hohen Rate, nie mit der Mindestrate. Und keine neuen Einkäufe mit der Karte, solange ein Saldo offen ist, weil auch die ab dem ersten Tag verzinst werden.</p></div>'''),
       ('So schaltest du die Teilzahlung ab',ausschalten),
       ('Teilzahlung, Ratenkredit oder Kontorahmen?',vergleich),
       ('Wann Teilzahlung vertretbar ist','''<div class="prose"><ul>
<li><b>Überbrückung für Tage, nicht Monate.</b> Eine unerwartete Rechnung kurz vor dem Gehalt: Zinsen für zwei Wochen sind ein kleiner Betrag. Ab dem zweiten Monat ist ein Ratenkredit günstiger.</li>
<li><b>Nur mit fester Rate.</b> In der App die Rate auf den höchsten Betrag stellen, den du sicher aufbringst, nicht auf die Mindestrate.</li>
<li><b>Karte währenddessen nicht nutzen.</b> Neue Einkäufe werden bei offenem Saldo meist sofort verzinst. Für den Alltag in dieser Zeit die Debitkarte nehmen.</li>
<li><b>Sondertilgung, sobald Geld da ist.</b> Bei allen Karten in unserem Vergleich kannst du jederzeit mehr zahlen; jede Überweisung senkt den verzinsten Saldo sofort.</li></ul></div>'''),
       ('Quellen','''<div class="prose"><ul><li>Soll- und Effektivzinsen, zinsfreie Fristen, Rückzahlungsweg und Rahmen: Preisblätter und Bedingungen der Anbieter, verlinkt auf jeder Kartenseite; die Werte und Rechenbeispiele werden beim Bauen dieser Seite aus den Kartendaten berechnet.</li></ul></div>'''),
      ],
      faq=[
       ('Was ist Teilzahlung bei der Kreditkarte?','Die Möglichkeit, die Monatsrechnung nicht vollständig, sondern nur mit einer Mindestrate zu bezahlen. Der Rest bleibt als Kredit stehen und wird verzinst, bei den Karten in unserem Vergleich mit '+z(lo)+' bis '+z(hi)+' effektiv im Jahr.'),
       ('Wie hoch sind die Zinsen bei Teilzahlung?',f'In unserem {N}-Vergleich zwischen {z(lo)} ({lo_c["titel"]}) und {z(hi)} ({hi_c["titel"]}) effektiv im Jahr. Die Gratiskarten liegen fast alle über 20 %, Karten mit Jahresgebühr meist darunter.'),
       ('Was kosten 1.000 € in Teilzahlung?',f'Mit der Mindestrate (3 %, mindestens 30 €) bei der {hzl} rund {E2(t_hi)} € Zinsen über {m_hi} Monate. Mit 100 € im Monat {E2(t_hf)} € über {m_hf} Monate. Für einen einzigen Monat rund {E2(1000*r_hi)} €.'),
       ('Wie schalte ich die Teilzahlung aus?','Bei Karten mit Lastschrift in der App die Rückzahlung auf 100 % stellen. Bei Karten ohne Einzug (TF Bank, Advanzia in Österreich, Bank Norwegian, Instabank) die Rechnung bis zum Fälligkeitstag vollständig überweisen; was fehlt, wird automatisch zum verzinsten Kredit.'),
       ('Gilt die zinsfreie Frist auch bei Teilzahlung?','Nein. Die 49 bis 90 Tage gelten nur, wenn die Rechnung vollständig bezahlt wird. Bleibt ein Rest offen, verzinsen viele Banken auch neue Einkäufe ab dem Buchungstag. Bargeld wird fast immer ab dem ersten Tag verzinst.'),
       ('Ist Teilzahlung bei der Kreditkarte voreingestellt?','Bei einigen Karten ja, in Deutschland laut Preisverzeichnis bei Hanseatic, awa7, Deutschland-Kreditkarte, easybank, Eurowings, IKEA und Miles & More myFlex. Bei Karten ohne Lastschrift beginnt sie von selbst, wenn die Überweisung zu niedrig ausfällt. Prüfe die Einstellung nach dem ersten Login.'),
       (f'Wirkt sich Teilzahlung auf die {AUS}-Bewertung aus?','Der Kartenrahmen selbst ist vermerkt. Pünktliche Zahlungen sind unproblematisch; ausgereizte Rahmen über lange Zeit und versäumte Raten wirken negativ. Ein dauerhaft offener Saldo ist auch ein Signal an die Bank, den Rahmen nicht zu erhöhen.'),
       ('Ist ein Ratenkredit günstiger als die Teilzahlung?','In der Regel ja, deutlich. Die Kartenteilzahlung kostet bei den Gratiskarten 20 bis 25 % effektiv; Ratenkredite liegen bei guter Bonität meist weit darunter. Für mehr als zwei oder drei Monate lohnt sich die Umschuldung.'),
      ],
      related=['kostenlose-kreditkarte','kartentypen','kreditkarte-beantragen'])
