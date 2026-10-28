# Ratgeber (nur AT) zu Festgeld: Festgeld oder Tagesgeld, Einlagensicherung, Zinstreppe, Kündigen, Plattformen, Steuern.
# Zahlen kommen live aus daten/at/festgeld.json und daten/festgeld-laender.json (dieselben Daten wie der Festgeld-Vergleich).
# Rechtliches: Einlagensicherung laut Arbeiterkammer Wien, FMA und Einlagensicherung AUSTRIA; KESt laut BMF (bmf.gv.at);
# Quellensteuer laut Produktinformationsblättern der Plattformen; Vorschusszinsen laut Arbeiterkammer Wien. Abgerufen am 28.10.2026.
# Aufruf aus ratgeber.build('at'): register(art,P,eur)
import html,json,os
E=lambda s: html.escape(str(s)) if s is not None else ''
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'daten')
AK_ES='https://wien.arbeiterkammer.at/beratung/konsumentenschutz/geld/sparen/Einlagensicherung.html'
AK_AUFL='https://wien.arbeiterkammer.at/beratung/konsumentenschutz/geld/sparen/Voreiliges_Aufloesen_von_Spareinlagen_kommt_teuer.html'
FMA_ES='https://www.fma.gv.at/en/banks/deposit-guarantee-schemes/'
ESA='https://www.einlagensicherung.at/'
BMF_INL='https://www.bmf.gv.at/themen/steuern/sparen-veranlagen/besteuerung-kapitalertraege-inland.html'
BMF_ALLG='https://www.bmf.gv.at/themen/steuern/sparen-veranlagen/information-zu-einkuenften-aus-kapitalvermoegen.html'
RAISIN_QST='https://www.raisin.com/de-at/steuer/quellensteuer/'
RAISIN_ANL='https://www.raisin.com/de-at/anleitung/'
PTB='https://pickthebank.eu/de/festgeld/osterreich/'
RIKS='https://storage.mfn.se/a24f7466-2756-4628-8b7c-bc9aa1084bfc/insattningsgarantins-maxbelopp-andras-till-1-150-000-kronor.pdf'
ABGERUFEN='28.10.2026'

def _tbl(head,rows):
    h=''.join(f'<th>{c}</th>' for c in head)
    b=''.join('<tr>'+''.join(f'<td>{c}</td>' for c in r)+'</tr>' for r in rows)
    return f'<div class="tbl wide"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'
def _ext(u,t): return f'<a href="{E(u)}" target="_blank" rel="noopener">{E(t)} ↗</a>'
def _pct(x):
    s=f'{x:.2f}'.replace('.',','); return (s[:-3] if s.endswith(',00') else s)+' %'
def _dmy(s): return '.'.join(reversed(s.split('-'))) if s else ''
def _load():
    d=json.load(open(os.path.join(D,'at','festgeld.json'),encoding='utf-8'))
    L=json.load(open(os.path.join(D,'festgeld-laender.json'),encoding='utf-8'))
    return d,[a for a in d['angebote'] if a.get('status','ok')=='ok'],L
def _best(xs,m):
    c=[(z['zins'],a) for a in xs for z in a['zinsen'] if z['monate']==m]
    return max(c,key=lambda t:t[0]) if c else (None,None)
def _n(xs,m): return len({a['id'] for a in xs for z in a['zinsen'] if z['monate']==m})
def _vt(a): return {'Raisin':'Raisin','direkt':'direkt','andere: PickTheBank':'PickTheBank'}.get(a['vertrieb'],a['vertrieb'].replace('andere: ',''))
def _sich(L,cc):
    l=L.get(cc) or {}
    w=l.get('waehrung') or '€'
    return f'{l["betrag"]:,.0f}'.replace(',','.')+(' '+w if w!='€' else ' €') if l.get('betrag') else '–'

def register(art,P,eur):
    d,xs,L=_load()
    stand=_dmy(d['stand'])
    F=f'{P}at/festgeld/'; F1=f'{F}1-jahr/'; FH=f'{F}bestenlisten/oesterreichische-banken/'; FM=f'{F}methodik/'
    RK=f'{P}at/rechner/kapitalertragsteuer/'; RZ=f'{P}at/rechner/zinseszins/'
    def L_(a): return f'<a class="lnk" href="{F}{a["id"]}/">{E(a["bank"])}</a> <small class="mut">({E(_vt(a))})</small>'
    n=len(xs)
    raisin=[a for a in xs if a['vertrieb']=='Raisin']; direkt=[a for a in xs if a['vertrieb']=='direkt']; ptb=[a for a in xs if 'PickTheBank' in a['vertrieb']]
    heim=[a for a in xs if a['sitz']=='AT']; auslan=[a for a in xs if a['sitz']!='AT']
    auto=[a for a in xs if a['steuer_auto']]; manuell=[a for a in xs if not a['steuer_auto']]
    kuend=[a for a in xs if a['kuendigung'] in ('ja','ja_mit_abschlag')]; nokuend=[a for a in xs if a['kuendigung']=='nein']
    flex=[a for a in xs if 'Flexgeld' in (a['produkt'] or '')]
    verl={k:[a for a in xs if a['verlaengerung']==k] for k in ('automatisch','wahlweise','keine')}
    z3,a3=_best(xs,3); z6,a6=_best(xs,6); z12,a12=_best(xs,12); z24,a24=_best(xs,24); z36,a36=_best(xs,36); z60,a60=_best(xs,60)
    zh12,ah12=_best(heim,12)
    mins=sorted({a['min_anlage'] for a in xs if a['min_anlage']})
    zz=[a for a in xs if a['zinseszins'] is True]
    laender=sorted({a['sitz'] for a in xs},key=lambda c:(-len([a for a in xs if a['sitz']==c]),c))
    zweig=[a for a in xs if a['zweigniederlassung']]
    se=[a for a in xs if a['sitz']=='SE']
    sek=L.get('SE',{}).get('betrag',1150000)

    # ---------- 1. Festgeld oder Tagesgeld ----------
    art('at','festgeld-oder-tagesgeld',
      h1='Festgeld oder Tagesgeld: Was passt wann in Österreich?',
      mt='Festgeld oder Tagesgeld in Österreich? | Finvallo',
      desc=f'Festgeld oder Tagesgeld in Österreich: Wo die Unterschiede liegen, wann Zinsbindung besser ist als Flexibilität und wie du beides kombinierst. Mit Zinsen aus {n} Festgeld-Angeboten.',
      about='Festgeld in Österreich',
      lede='Beim Tagesgeld kommst du jederzeit an dein Geld, beim Festgeld ist der Zins für die Laufzeit fix. Welche Variante besser ist, hängt davon ab, wann du das Geld brauchst.',
      kurz=(f'Festgeld bindet dein Geld für eine feste Laufzeit, dafür steht der Zins vorher fest. Im Vergleich zahlen die besten Angebote für 1 Jahr bis {_pct(z12)} ({E(a12["bank"])}), für 3 Jahre bis {_pct(z36)}. '
            'Tagesgeld bleibt täglich verfügbar, der Zins kann aber jederzeit sinken. Sinnvoll ist meist die Kombination: Notgroschen aufs Tagesgeld, den Rest fest anlegen, am besten in mehreren Laufzeiten.'),
      secs=[
       ('Der Unterschied in einem Satz',f'''<div class="prose"><p>Beim Festgeld leihst du der Bank Geld für eine feste Zeit, etwa 6 Monate, 1 Jahr oder 5 Jahre. Dafür bekommst du einen Zins, der sich während der Laufzeit nicht ändert. Beim Tagesgeld liegt das Geld auf einem Sparkonto ohne Bindung. Du kannst es jederzeit aufs Girokonto überweisen, die Bank kann den Zins aber jederzeit anpassen, meist mit kurzer Ankündigung.</p>
<p>Beide Varianten sind Einlagen. Sie fallen unter die gesetzliche Einlagensicherung bis 100.000 € pro Person und Bank, und auf die Zinsen fällt 25 % KESt an. Der Unterschied liegt nur in Bindung und Zins.</p></div>'''),
       ('Festgeld und Tagesgeld im Vergleich',_tbl(['','Festgeld','Tagesgeld'],[
            ('Verfügbarkeit','erst am Ende der Laufzeit, vorzeitig meist gar nicht oder nur mit Abschlag','täglich'),
            ('Zins','für die ganze Laufzeit fix','variabel, die Bank kann ihn jederzeit ändern'),
            ('Zinshöhe im Vergleich',f'bis {_pct(z12)} für 1 Jahr, bis {_pct(z36)} für 3 Jahre, bis {_pct(z60)} für 5 Jahre','meist nur für Neukunden hoch, danach oft deutlich weniger'),
            ('Mindestanlage',f'je nach Angebot ab {eur(mins[0])} € bis {eur(mins[-1])} €','meist ab 0 € oder 1 €'),
            ('Nachschießen','nicht möglich, jede Anlage ist ein eigener Vertrag','jederzeit'),
            ('Planbarkeit','du weißt am ersten Tag, was am Ende herauskommt','du weißt nur den Zins von heute'),
            ('Einlagensicherung','100.000 € pro Person und Bank','100.000 € pro Person und Bank'),
            ('Steuer','25 % KESt, bei österreichischen Banken automatisch','25 % KESt, bei österreichischen Banken automatisch')])+
        f'<div class="prose"><p>Die Zinsen stammen aus dem <a href="{F}">Festgeld-Vergleich</a> mit Stand {stand}. Dort siehst du für jede Laufzeit, welche Bank gerade vorne liegt.</p></div>'),
       ('Wann Festgeld die bessere Wahl ist',f'''<div class="prose"><p>Festgeld passt, wenn du das Geld für die Laufzeit sicher nicht brauchst und den Zins festhalten willst. Drei typische Fälle:</p><ul>
<li><b>Du erwartest sinkende Zinsen.</b> Die Zinsen für Tagesgeld folgen den Leitzinsen der EZB mit etwas Verzögerung. Beim Festgeld hast du den Satz von heute für die ganze Laufzeit sicher. Umgekehrt gilt: Steigen die Zinsen, bist du beim Festgeld eingesperrt.</li>
<li><b>Du sparst auf ein Ziel mit Datum.</b> Autokauf in zwei Jahren, Eigenmittel für eine Wohnung in drei Jahren: Dann weißt du, wie lange das Geld weg sein darf, und nimmst genau diese Laufzeit.</li>
<li><b>Du willst dich nicht kümmern.</b> Tagesgeld-Zinsen gelten oft nur für Neukunden und nur für ein paar Monate. Wer den hohen Zins behalten will, muss regelmäßig wechseln. Beim Festgeld ist das Thema für die Laufzeit erledigt.</li></ul>
<p>Im Vergleich liegt der beste Zins für 1 Jahr bei {_pct(z12)}, für 2 Jahre bei {_pct(z24)} und für 5 Jahre bei {_pct(z60)}. Längere Laufzeiten bringen also nicht automatisch mehr Zins. Prüfe vor dem Abschluss die <a href="{F1}">Angebote für 1 Jahr</a> und die längeren Laufzeiten nebeneinander.</p></div>'''),
       ('Wann Tagesgeld besser ist','''<div class="prose"><p>Tagesgeld passt für alles, was du kurzfristig brauchen könntest:</p><ul>
<li><b>Notgroschen.</b> Zwei bis drei Monatsausgaben sollten jederzeit greifbar sein, für die kaputte Waschmaschine, die Autoreparatur oder eine Phase ohne Einkommen. Dieses Geld gehört nie ins Festgeld.</li>
<li><b>Geld mit unklarem Zweck.</b> Weißt du noch nicht, ob du in sechs Monaten eine größere Anschaffung machst, bleibt das Geld besser flexibel. Ein vorzeitig aufgelöstes Festgeld kostet fast immer den Zins.</li>
<li><b>Parkposition.</b> Wer in Etappen in Aktien oder ETFs investiert, parkt den Rest auf dem Tagesgeld.</li></ul>
<p>Wichtig beim Tagesgeld: Lies das Kleingedruckte zur Zinsgarantie. Viele Banken garantieren den Zins nur für 3 bis 6 Monate und nur für neues Geld. Danach gilt der Basiszins, der oft weit darunter liegt.</p></div>'''),
       ('Die Kombination: Notgroschen flexibel, Rest fest',f'''<div class="prose"><p>Die meisten fahren mit einer Mischung am besten:</p><ol>
<li><b>Notgroschen aufs Tagesgeld.</b> Zwei bis drei Monatsausgaben, bei unsicherem Einkommen mehr. Dieses Geld muss nicht den höchsten Zins bringen, es muss da sein.</li>
<li><b>Geld mit Datum ins Festgeld.</b> Alles, was du in einem bekannten Zeitraum nicht brauchst, legst du zum festen Zins an. Die Laufzeit richtet sich nach dem Zeitpunkt, an dem du das Geld brauchst, nicht nach dem höchsten Zins.</li>
<li><b>Größere Beträge auf Stufen verteilen.</b> Statt alles auf eine Laufzeit zu setzen, teilst du den Betrag auf 1, 2 und 3 Jahre. So wird jedes Jahr ein Teil frei, und du kannst zu den dann gültigen Zinsen neu anlegen. Wie das genau geht, steht im Beitrag zur <a href="../zinstreppe/">Zinstreppe</a>.</li></ol>
<p>Rechne vor dem Abschluss nach: Der <a href="{RZ}">Zinseszinsrechner</a> zeigt, was aus einem Betrag über mehrere Jahre wird, der <a href="{RK}">KESt-Rechner</a>, was nach Steuer übrig bleibt. Beachte dabei, dass bei den meisten Festgeldern die Zinsen jährlich ausgezahlt werden und nicht mitverzinst werden. Im Vergleich ist nur bei {len(zz)} von {n} Angeboten ein Zinseszins vorgesehen.</p></div>'''),
       ('Worauf du beim Festgeld noch achten solltest',f'''<div class="prose"><ul>
<li><b>Einlagensicherung.</b> {len(heim)} der {n} Angebote im Vergleich kommen von Banken mit Sitz in Österreich, {len(auslan)} von Banken in anderen EU-Ländern. Überall gilt die Grenze von 100.000 € pro Person und Bank, zuständig ist aber die Sicherung des Sitzlandes. Mehr dazu im Beitrag zur <a href="../einlagensicherung/">Einlagensicherung</a>.</li>
<li><b>Steuer.</b> Bei {len(auto)} Angeboten führt die Bank die KESt automatisch ab, bei {len(manuell)} musst du die Zinsen selbst in der Steuererklärung angeben. Das sind vor allem die Angebote über Plattformen. Mehr im Beitrag <a href="../festgeld-steuern/">Festgeld und Steuern</a>.</li>
<li><b>Kündigung.</b> Nur {len(kuend)} der {n} Angebote lassen sich vorzeitig auflösen, und dann fast immer mit Abschlag. Was dabei gilt, steht im Beitrag <a href="../festgeld-kuendigen/">Festgeld kündigen</a>.</li>
<li><b>Laufzeitende.</b> {len(verl["automatisch"])} Angebote verlängern sich automatisch, wenn du nichts tust. Trag dir das Ende der Laufzeit in den Kalender ein.</li></ul>
<p>Wie wir die Angebote bewerten, steht in der <a href="{FM}">Methodik</a>.</p></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Zinsen, Mindestanlage, Kündigung, Verlängerung und Steuerabwicklung: Konditionsseiten und Produktinformationsblätter der Banken und Plattformen, verlinkt auf jeder Angebotsseite im <a href="{F}">Festgeld-Vergleich</a>, Stand {stand}.</li>
<li>Einlagensicherung: {_ext(AK_ES,"Arbeiterkammer Wien, Einlagensicherung")}, abgerufen am {ABGERUFEN}.</li>
<li>KESt auf Zinsen: {_ext(BMF_INL,"BMF, Besteuerung inländischer Kapitalerträge")}, abgerufen am {ABGERUFEN}.</li></ul></div>'''),
      ],
      faq=[
       ('Was ist der Unterschied zwischen Festgeld und Tagesgeld?','Festgeld hat eine feste Laufzeit und einen festen Zins. Tagesgeld ist täglich verfügbar, der Zins kann sich aber jederzeit ändern. Beide sind durch die Einlagensicherung bis 100.000 € pro Person und Bank geschützt.'),
       ('Bringt Festgeld mehr Zinsen als Tagesgeld?',f'Meist ja, wenn man die Aktionszinsen für Neukunden beim Tagesgeld herausrechnet. Im Vergleich liegt der beste Festgeld-Zins für 1 Jahr bei {_pct(z12)}, für 5 Jahre bei {_pct(z60)}, Stand {stand}.'),
       ('Wie viel Geld sollte aufs Tagesgeld, wie viel ins Festgeld?','Als Notgroschen zwei bis drei Monatsausgaben aufs Tagesgeld. Alles, was du in einem bekannten Zeitraum sicher nicht brauchst, kann ins Festgeld, am besten auf mehrere Laufzeiten verteilt.'),
       ('Kann ich Festgeld vorzeitig auflösen, wenn ich das Geld doch brauche?',f'Bei {len(nokuend)} der {n} Angebote im Vergleich nicht. Bei den übrigen ist es möglich, aber mit Abschlag, etwa Vorschusszinsen oder einem Zins von 0,01 %. Für unsicheres Geld ist Tagesgeld die bessere Wahl.'),
       ('Welche Laufzeit ist beim Festgeld sinnvoll?','Die Laufzeit sollte zu dem Zeitpunkt passen, an dem du das Geld brauchst. Bei größeren Beträgen hilft eine Zinstreppe: ein Drittel auf 1, 2 und 3 Jahre, dann wird jedes Jahr ein Teil frei.'),
      ],
      related=['zinstreppe','einlagensicherung','festgeld-kuendigen'])

    # ---------- 2. Einlagensicherung ----------
    lrow=[]
    for cc in laender:
        l=L.get(cc) or {}; k=[a for a in xs if a['sitz']==cc]
        r=l.get('rating_sp') or '–'; r='kein Rating' if r=='NR' else r
        lrow.append((E(l.get('name') or cc),len(k),E(l.get('sicherung') or '–'),_sich(L,cc),E(r)))
    art('at','einlagensicherung',
      h1='Einlagensicherung in Österreich und der EU: Was wirklich geschützt ist',
      mt='Einlagensicherung Österreich: 100.000 € erklärt | Finvallo',
      desc=f'Einlagensicherung in Österreich: 100.000 € pro Person und Bank, Auszahlung in 7 Arbeitstagen, ESA, Sparkassen und Raiffeisen. Was bei Banken aus {len(laender)-1} anderen EU-Ländern gilt.',
      about='Festgeld in Österreich',
      lede='Geht eine Bank pleite, ersetzt die Einlagensicherung dein Guthaben bis 100.000 €. Die Regeln sind in der ganzen EU gleich, die Kassen dahinter sind es nicht.',
      kurz=(f'In jedem EU-Land sind Einlagen bis 100.000 € pro Person und Bank gesetzlich gesichert, Zinsen eingerechnet. Die Auszahlung muss innerhalb von 7 Arbeitstagen starten, ohne Antrag. Bei einem Gemeinschaftskonto gilt die Grenze pro Inhaber, also 200.000 € zu zweit. '
            f'In Österreich sichern drei Einrichtungen: die Einlagensicherung AUSTRIA (ESA), die Sparkassen-Haftungs GmbH und die Österreichische Raiffeisen-Sicherungseinrichtung. Bei Banken aus dem EU-Ausland zahlt die Sicherung des Sitzlandes. Im Vergleich betrifft das {len(auslan)} von {n} Angeboten.'),
      secs=[
       ('So funktioniert die gesetzliche Einlagensicherung','''<div class="prose"><p>Jede Bank in der EU, die Einlagen annimmt, muss Mitglied einer anerkannten Einlagensicherung sein. Die Banken zahlen jedes Jahr Beiträge in einen Fonds ein. Kann eine Bank ihre Einlagen nicht mehr auszahlen, stellt die Aufsicht den Sicherungsfall fest, und die Sicherungseinrichtung zahlt den Kundinnen und Kunden ihr Guthaben aus. Die Regeln dafür stehen in der EU-Richtlinie über Einlagensicherungssysteme, in Österreich umgesetzt im Einlagensicherungs- und Anlegerentschädigungsgesetz (ESAEG).</p>
<p>Die wichtigsten Punkte laut Arbeiterkammer:</p><ul>
<li><b>100.000 € pro Person und Bank</b>, inklusive Zinsen. Hast du bei derselben Bank ein Girokonto, ein Sparbuch und ein Festgeld, werden alle zusammengezählt.</li>
<li><b>Pro Bank mit eigener Konzession.</b> Markenbanken ohne eigene Konzession zählen zur Mutterbank. Zwei Konten bei zwei verschiedenen Banken sind dagegen zweimal gesichert.</li>
<li><b>Auszahlung innerhalb von 7 Arbeitstagen</b>, automatisch. Du musst keinen Antrag stellen.</li>
<li><b>Gemeinschaftskonto:</b> Die Grenze gilt je Kontoinhaber. Ein Paar mit einem gemeinsamen Konto ist also bis 200.000 € geschützt.</li>
<li><b>Bis 500.000 € für 12 Monate</b> bei bestimmten Einlagen, zum Beispiel aus dem Verkauf einer selbst genutzten Wohnimmobilie. Diese Erhöhung musst du beantragen und belegen.</li>
<li><b>Gesichert sind</b> Sparbücher, Giro-, Festgeld- und Sparkonten, Bausparverträge und Wertpapierverrechnungskonten. Wertpapiere im Depot gehören dir ohnehin und sind nicht Teil der Einlagensicherung.</li></ul></div>'''),
       ('Wer in Österreich sichert',f'''<div class="prose"><p>Österreich hat laut Finanzmarktaufsicht drei anerkannte Sicherungseinrichtungen:</p><ul>
<li><b>Einlagensicherung AUSTRIA Ges.m.b.H. (ESA)</b> für die meisten Banken: Aktienbanken, Volksbanken, Hypo-Landesbanken und Bausparkassen. Nach eigenen Angaben hat sie 75 Mitgliedsinstitute.</li>
<li><b>Sparkassen-Haftungs GmbH</b> für die Erste Bank und die Sparkassen. Das ist ein institutsbezogenes Sicherungssystem: Der Sparkassen-Haftungsverbund soll ein Mitglied schon vor der Pleite stützen, und er ist zugleich als gesetzliche Einlagensicherung anerkannt.</li>
<li><b>Österreichische Raiffeisen-Sicherungseinrichtung eGen (ÖRS)</b> für den Raiffeisen-Sektor, seit November 2021 eigenständig.</li></ul>
<p>Für dich als Sparerin oder Sparer macht es keinen Unterschied, welche der drei zuständig ist: Grenze, Frist und Ablauf sind gleich. Welche Einrichtung für ein Angebot gilt, steht im „Informationsbogen für Einleger“, den dir jede Bank vor dem Abschluss geben muss. Im <a href="{F}">Festgeld-Vergleich</a> steht sie auf jeder Angebotsseite. Die {len(heim)} Angebote von Banken mit Sitz in Österreich findest du gesammelt in der Liste <a href="{FH}">österreichische Banken</a>.</p></div>'''),
       ('Banken aus anderen EU-Ländern: Heimatlandprinzip',f'''<div class="prose"><p>Legst du Geld bei einer Bank mit Sitz in Italien, Estland oder Schweden an, gilt auch dort die Grenze von 100.000 €. Zuständig ist aber die Einlagensicherung des Landes, in dem die Bank ihre Konzession hat. Das nennt man Heimatlandprinzip. Es gilt auch, wenn die Bank in Österreich eine Zweigniederlassung betreibt: Im Vergleich betrifft das zum Beispiel {", ".join(L_(a) for a in zweig) if zweig else "derzeit kein Angebot"}. Eine österreichische Adresse heißt also nicht, dass die ESA zahlt.</p>
<p>Im Sicherungsfall einer ausländischen Bank wickelt die Sicherung des Sitzlandes die Auszahlung ab, bei Zweigniederlassungen in Zusammenarbeit mit der österreichischen Einrichtung. Die Frist von 7 Arbeitstagen gilt EU-weit. Praktisch heißt das: Die Kommunikation läuft womöglich auf Englisch oder in der Landessprache, und die Fonds sind unterschiedlich groß.</p></div>'''),
       ('Was ein Länderrating aussagt, und was nicht',_tbl(['Sitzland','Angebote im Vergleich','Sicherungseinrichtung','Gesichert','S&amp;P-Rating'],lrow)+
        f'''<div class="prose"><p>Die Fonds der Einlagensicherung sind für einzelne Pleiten ausgelegt, nicht für eine Krise des ganzen Bankensystems. Reicht der Fonds nicht, muss der Staat einspringen. Deshalb zeigen wir das langfristige Länderrating von S&amp;P Global für das Sitzland: Es ist ein Hinweis darauf, wie gut ein Staat im Ernstfall nachschießen könnte.</p>
<p>Das Rating sagt aber nichts über die Bank selbst aus. Eine Bank in einem AAA-Land kann pleitegehen, eine Bank in einem BBB-Land solide sein. Die Einlagensicherung greift in beiden Fällen gleich. Das Rating ist also kein Grund, ein Angebot auszuschließen, aber ein Grund, bei großen Beträgen auf mehrere Banken und Länder zu streuen. Die Ratings stammen vom {_dmy(max((v.get("rating_stand") or "") for v in L.values()))}, Details stehen in der <a href="{FM}">Methodik</a>.</p></div>'''),
       ('Beispiel Fremdwährung: Sicherung in schwedischen Kronen',f'''<div class="prose"><p>Länder ohne Euro sichern den Gegenwert von 100.000 € in ihrer Währung, und sie rechnen den Betrag nur alle fünf Jahre neu um. In Schweden gilt seit 1. Jänner 2026 eine Grenze von {eur(sek)} SEK pro Person und Bank, festgelegt zum Wechselkurs vom 3. Juli 2025. Schwankt der Kurs danach, ist dein Euro-Guthaben etwas mehr oder etwas weniger als 100.000 € wert.</p>
<p>Im Vergleich betrifft das {len(se)} Angebote von Banken mit Sitz in Schweden{": "+", ".join(L_(a) for a in se) if se else ""}. Plattformen wie Raisin begrenzen die Anlage bei solchen Banken auf 100.000 €. Wer sicher gehen will, bleibt etwas darunter, etwa bei 95.000 €, damit auch die Zinsen und ein Kursrückgang der Krone noch Platz haben.</p>
<p>Umgekehrt gilt: Ein Festgeld in US-Dollar oder britischen Pfund bei einer EU-Bank ist ebenfalls gesichert, die Sicherung zahlt aber in Euro oder in der Landeswährung des Sitzlandes aus. Das Währungsrisiko trägst du selbst.</p></div>'''),
       ('Freiwillige Sicherung und Anlegerentschädigung','''<div class="prose"><p>In Deutschland sichern private Banken über den freiwilligen Einlagensicherungsfonds des Bankenverbands zusätzlich Beträge über 100.000 €. Im Vergleich steht das bei den betroffenen deutschen Banken auf der Angebotsseite. Ein Rechtsanspruch besteht darauf nicht, die gesetzlichen 100.000 € sind die einzige verbindliche Grenze. In Österreich gibt es keine vergleichbare freiwillige Sicherung über die gesetzliche Grenze hinaus.</p>
<p>Nicht verwechseln: Die Anlegerentschädigung ersetzt bis 20.000 €, wenn eine Bank oder Wertpapierfirma Wertpapiere von Kundinnen und Kunden veruntreut hat. Mit Festgeld hat sie nichts zu tun.</p></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Grenze, Frist, Gemeinschaftskonten, 500.000 € für 12 Monate: {_ext(AK_ES,"Arbeiterkammer Wien, Einlagensicherung")}, abgerufen am {ABGERUFEN}.</li>
<li>Die drei Sicherungseinrichtungen: {_ext(FMA_ES,"FMA, Deposit Guarantee Schemes")}; Mitgliedsinstitute: {_ext(ESA,"Einlagensicherung AUSTRIA")}, abgerufen am {ABGERUFEN}.</li>
<li>Schweden: {_ext(RIKS,"Riksgälden, Pressemitteilung vom 30.10.2025 zur Anpassung auf 1.150.000 SEK")}.</li>
<li>Sicherungseinrichtung und Länderrating je Angebot: Informationsbögen der Banken und tradingeconomics.com, verlinkt im <a href="{F}">Festgeld-Vergleich</a>.</li></ul></div>'''),
      ],
      faq=[
       ('Wie viel Geld ist bei einer Bankpleite in Österreich geschützt?','100.000 € pro Person und Bank, inklusive Zinsen. Bei Gemeinschaftskonten gilt die Grenze je Inhaber. In Sonderfällen, etwa nach dem Verkauf der eigenen Wohnung, sind 12 Monate lang bis 500.000 € geschützt.'),
       ('Wie schnell bekomme ich mein Geld?','Die gesetzliche Frist beträgt 7 Arbeitstage ab Feststellung des Sicherungsfalls. Die Auszahlung läuft automatisch, du musst keinen Antrag stellen.'),
       ('Gilt die Einlagensicherung auch bei Festgeld über Raisin?','Ja. Dein Geld liegt bei der Partnerbank, und für diese gilt die Einlagensicherung ihres Sitzlandes bis 100.000 €. Das kostenlose Verrechnungskonto bei der Raisin Bank in Deutschland ist über die deutsche Einlagensicherung geschützt.'),
       ('Ist eine Bank in Italien oder Lettland unsicherer als eine in Österreich?','Die gesetzliche Grenze ist überall 100.000 €. Ob ein Land seinen Fonds im Ernstfall stützen kann, zeigt das Länderrating als groben Hinweis. Über die einzelne Bank sagt es nichts aus. Bei großen Beträgen auf mehrere Banken verteilen.'),
       ('Was passiert bei einer schwedischen Bank mit meinem Euro-Guthaben?',f'Schweden sichert {eur(sek)} SEK pro Person und Bank, den Gegenwert von 100.000 € zum Kurs vom Juli 2025. Fällt die Krone, sinkt der gesicherte Euro-Betrag etwas. Plattformen begrenzen die Anlage deshalb auf 100.000 €.'),
      ],
      related=['festgeld-plattformen','festgeld-oder-tagesgeld','festgeld-steuern'])

    # ---------- 3. Zinstreppe ----------
    T=30000; S=T/3
    st=[(1,z12,a12),(2,z24,a24),(3,z36,a36)]
    zrow=[(f'Stufe {i}',f'{eur(S)} €',f'{j} Jahr{"e" if j>1 else ""}',_pct(z),L_(a),f'{eur(round(S*z/100*j,2))} €') for i,(j,z,a) in enumerate(st,1)]
    ztot=sum(S*z/100*j for j,z,_ in st)
    all3=T*z36/100*3; all1=T*z12/100
    zrow.append(('Gesamt',f'{eur(T)} €','1 bis 3 Jahre','','',f'{eur(round(ztot,2))} €'))
    art('at','zinstreppe',
      h1='Zinstreppe: Festgeld auf mehrere Laufzeiten verteilen',
      mt='Zinstreppe: Festgeld-Leiter in Österreich | Finvallo',
      desc=f'Zinstreppe in Österreich erklärt: 30.000 € auf drei Laufzeiten verteilt, durchgerechnet mit aktuellen Zinsen bis {_pct(z36)}. Vorteile, Nachteile und wann sich die Festgeld-Leiter lohnt.',
      about='Festgeld in Österreich',
      lede='Alles auf fünf Jahre, und dann steigen die Zinsen? Oder alles auf ein Jahr, und dann fallen sie? Die Zinstreppe nimmt dir diese Wette ab.',
      kurz=(f'Bei einer Zinstreppe teilst du den Betrag auf mehrere Festgelder mit gestaffelten Laufzeiten, etwa je ein Drittel auf 1, 2 und 3 Jahre. Jedes Jahr wird eine Stufe frei, die du zum dann gültigen Zins wieder auf die längste Laufzeit anlegst. '
            f'Mit den besten Zinsen aus dem Vergleich bringen 30.000 € auf drei Stufen in den ersten drei Jahren {eur(round(ztot))} € Zinsen vor Steuer, alles auf 3 Jahre {eur(round(all3))} €. Dafür kommst du jedes Jahr an ein Drittel heran.'),
      secs=[
       ('Das Prinzip','''<div class="prose"><p>Festgeld hat ein Problem: Du musst dich heute für eine Laufzeit entscheiden, ohne zu wissen, wie sich die Zinsen entwickeln. Wählst du lang, verpasst du steigende Zinsen. Wählst du kurz, musst du bei fallenden Zinsen schlechter neu anlegen.</p>
<p>Die Zinstreppe, auch Festgeld-Leiter oder Laddering genannt, umgeht das. Du teilst den Betrag in gleich große Stufen und legst jede Stufe mit einer anderen Laufzeit an: 1 Jahr, 2 Jahre, 3 Jahre. Nach einem Jahr wird die erste Stufe fällig. Du legst sie neu an, und zwar auf 3 Jahre, weil die anderen beiden Stufen dann noch 1 und 2 Jahre laufen. Nach dem dritten Jahr hat jede Stufe 3 Jahre Laufzeit, und trotzdem wird jedes Jahr ein Drittel frei.</p></div>'''),
       ('Rechenbeispiel: 30.000 € auf drei Stufen',_tbl(['Stufe','Betrag','Laufzeit','Zins','Bestes Angebot im Vergleich','Zinsen bis Ende der Laufzeit'],zrow)+
        f'''<div class="prose"><p>Gerechnet mit den besten Zinsen je Laufzeit aus dem <a href="{F}">Festgeld-Vergleich</a>, Stand {stand}, vor Steuer und ohne Zinseszins, weil die meisten Banken die Zinsen jährlich auszahlen. Zum Vergleich: {eur(T)} € komplett auf 3 Jahre zu {_pct(z36)} bringen {eur(round(all3))} €, komplett auf 1 Jahr zu {_pct(z12)} nur {eur(round(all1))} €, danach musst du neu anlegen.</p>
<p>Die Treppe liegt also unter der 3-Jahres-Anlage, solange die Zinsen für kurze Laufzeiten niedriger sind. Dafür hast du nach 12 Monaten {eur(S)} € in der Hand und kannst reagieren, wenn die Zinsen gestiegen sind. Ist der Zins für 1 Jahr höher als für 3 Jahre, dreht sich das Bild, und die Treppe liegt vorne.</p>
<p>Die Angebote in der Tabelle stammen von verschiedenen Banken. Das ist kein Nachteil: Bei einem Betrag von {eur(T)} € bleibst du ohnehin weit unter der Grenze der Einlagensicherung. Bei größeren Beträgen hilft die Verteilung auf mehrere Banken, die 100.000 € pro Bank nicht zu überschreiten. Nach Steuer rechnet der <a href="{RK}">KESt-Rechner</a>.</p></div>'''),
       ('Vorteile der Zinstreppe','''<div class="prose"><ul class="checks">
<li><b>Jedes Jahr Geld verfügbar.</b> Du musst nie ein Festgeld vorzeitig auflösen, weil regelmäßig eine Stufe fällig wird.</li>
<li><b>Keine Zinswette.</b> Du legst jedes Jahr ein Drittel zum dann gültigen Zins an. Steigen die Zinsen, profitierst du schrittweise. Fallen sie, hast du zwei Drittel noch zum alten Zins.</li>
<li><b>Auf Dauer der lange Zins.</b> Nach der Anlaufphase läuft jede Stufe 3 Jahre und bekommt den Zins für 3 Jahre, und trotzdem bleibt die Treppe beweglich.</li>
<li><b>Einlagensicherung einfach einhalten.</b> Wer die Stufen bei verschiedenen Banken anlegt, bleibt automatisch unter 100.000 € pro Bank.</li></ul></div>'''),
       ('Nachteile und Grenzen',f'''<div class="prose"><ul>
<li><b>Mehr Aufwand.</b> Drei Verträge statt einem, jedes Jahr eine Entscheidung, bei mehreren Banken mehrere Logins. Plattformen wie Raisin bündeln das unter einem Konto, dafür musst du die Zinsen dort selbst versteuern. Mehr dazu im Beitrag zu den <a href="../festgeld-plattformen/">Festgeld-Plattformen</a>.</li>
<li><b>Mindestanlage.</b> Viele Angebote verlangen mindestens 5.000 € oder 10.000 €. Bei 9.000 € Gesamtbetrag wird es mit drei Stufen eng. Im Vergleich liegt die Mindestanlage je nach Angebot zwischen {eur(mins[0])} € und {eur(mins[-1])} €.</li>
<li><b>Automatische Verlängerung.</b> {len(verl["automatisch"])} der {n} Angebote verlängern sich von selbst, wenn du am Laufzeitende nichts tust. Dann läuft die Stufe zum dann gültigen Zins weiter, womöglich bei einer Bank, die nicht mehr vorne liegt. Trag dir die Fälligkeiten ein.</li>
<li><b>Weniger Zins in der Anlaufphase.</b> Solange kurze Laufzeiten schlechter verzinst sind, bringt die Treppe in den ersten Jahren weniger als die lange Anlage, siehe Rechenbeispiel.</li></ul></div>'''),
       ('Wann sich die Zinstreppe lohnt',f'''<div class="prose"><p>Die Treppe lohnt sich, wenn du einen Betrag ab etwa 15.000 € für mehrere Jahre anlegen willst, aber nicht sicher bist, ob du zwischendurch etwas brauchst, und wenn du keine Meinung dazu hast, wohin die Zinsen gehen. Sie ist das Gegenteil von Markt-Timing.</p>
<p>Sie lohnt sich nicht, wenn du das Geld zu einem festen Termin brauchst, etwa für einen Wohnungskauf in drei Jahren. Dann nimmst du genau diese Laufzeit. Sie lohnt sich auch nicht für den Notgroschen, der gehört aufs Tagesgeld, siehe <a href="../festgeld-oder-tagesgeld/">Festgeld oder Tagesgeld</a>.</p>
<p>Varianten: Wer länger planen kann, baut die Treppe mit 1 bis 5 Jahren in fünf Stufen. Im Vergleich gibt es für 5 Jahre {_n(xs,60)} Angebote, bis {_pct(z60)} bei {L_(a60)}. Wer es einfacher will, nimmt zwei Stufen mit 1 und 2 Jahren. Die Seiten <a href="{F1}">1 Jahr</a>, <a href="{F}2-jahre/">2 Jahre</a> und <a href="{F}3-jahre/">3 Jahre</a> zeigen die Angebote je Stufe.</p></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Zinsen und Mindestanlage: Konditionsseiten der Banken und Plattformen, verlinkt auf jeder Angebotsseite im <a href="{F}">Festgeld-Vergleich</a>, Stand {stand}. Die Beispielrechnung übernimmt beim Bauen dieser Seite den jeweils besten Zins je Laufzeit.</li>
<li>Einlagensicherung: {_ext(AK_ES,"Arbeiterkammer Wien, Einlagensicherung")}, abgerufen am {ABGERUFEN}.</li></ul></div>'''),
      ],
      faq=[
       ('Was ist eine Zinstreppe?','Eine Aufteilung des Anlagebetrags auf mehrere Festgelder mit gestaffelten Laufzeiten, etwa 1, 2 und 3 Jahre. Jede fällige Stufe wird auf die längste Laufzeit neu angelegt. So ist jedes Jahr ein Teil verfügbar.'),
       ('Bringt die Zinstreppe mehr Zinsen als ein einzelnes Festgeld?',f'In der Anlaufphase meist weniger als die lange Laufzeit, solange kurze Laufzeiten niedriger verzinst sind. Im Beispiel mit 30.000 € sind es {eur(round(ztot))} € statt {eur(round(all3))} € in drei Jahren. Dafür bist du flexibler und profitierst von steigenden Zinsen.'),
       ('Wie viele Stufen sind sinnvoll?','Drei Stufen mit 1, 2 und 3 Jahren sind der Standard. Mit mehr Geld und Geduld gehen fünf Stufen bis 5 Jahre. Entscheidend ist, dass jede Stufe die Mindestanlage der Bank erreicht.'),
       ('Muss ich alle Stufen bei derselben Bank anlegen?','Nein. Oft liegt für jede Laufzeit eine andere Bank vorne. Bei Beträgen über 100.000 € ist die Verteilung auf mehrere Banken wegen der Einlagensicherung sogar nötig.'),
       ('Was passiert, wenn eine Stufe fällig wird und ich nichts tue?',f'Je nach Angebot wird das Geld ausgezahlt oder das Festgeld verlängert sich automatisch zum dann gültigen Zins. Im Vergleich verlängern sich {len(verl["automatisch"])} von {n} Angeboten automatisch. Details stehen im Beitrag „Festgeld kündigen“.'),
      ],
      related=['festgeld-oder-tagesgeld','festgeld-kuendigen','festgeld-plattformen'])

    # ---------- 4. Festgeld kündigen ----------
    krow=[(L_(a),E(a['kuendigung_text'] or 'keine Angabe')) for a in sorted(kuend,key=lambda a:(a['vertrieb']!='direkt',a['bank'].lower()))]
    vrow=[('Keine Verlängerung',len(verl['keine']),'Das Geld kommt am Laufzeitende aufs Verrechnungs- oder Referenzkonto. Du musst nichts tun.'),
          ('Verlängerung wählbar',len(verl['wahlweise']),'Du entscheidest vor dem Ende, ob das Festgeld weiterläuft. Ohne Entscheidung wird meist ausgezahlt, prüfe die Voreinstellung.'),
          ('Automatische Verlängerung',len(verl['automatisch']),'Ohne Weisung läuft das Festgeld mit derselben Laufzeit zum dann gültigen Zins weiter. Du musst rechtzeitig vorher auszahlen lassen.')]
    vorsch=[a for a in kuend if 'Vorschuss' in (a['kuendigung_text'] or '')]
    nullz=[a for a in kuend if '0,01' in (a['kuendigung_text'] or '')]
    art('at','festgeld-kuendigen',
      h1='Festgeld kündigen: Geht das vorzeitig, und was kostet es?',
      mt='Festgeld kündigen in Österreich: Geht das? | Finvallo',
      desc=f'Festgeld vorzeitig kündigen in Österreich: Bei {len(nokuend)} von {n} Angeboten nicht möglich, sonst mit Vorschusszinsen oder 0,01 % Zins. Flexgeld, Todesfall, automatische Verlängerung und Fristen.',
      about='Festgeld in Österreich',
      lede='Festgeld heißt fest. Trotzdem gibt es Ausnahmen, und am Laufzeitende lauert eine andere Falle: die automatische Verlängerung.',
      kurz=(f'Ein Festgeld kannst du normalerweise nicht vorzeitig kündigen. Im Vergleich schließen {len(nokuend)} von {n} Angeboten das aus. {len(kuend)} Angebote erlauben eine vorzeitige Auflösung, aber mit Abschlag: '
            f'entweder Vorschusszinsen von 1 ‰ pro Monat der nicht eingehaltenen Bindung oder ein Zins von nur 0,01 % für die ganze Zeit. Nach dem Abschluss hast du 14 Tage Widerrufsrecht. '
            f'Am Laufzeitende verlängern sich {len(verl["automatisch"])} Angebote automatisch, wenn du nicht rechtzeitig auszahlen lässt.'),
      secs=[
       ('Warum Festgeld nicht kündbar ist',f'''<div class="prose"><p>Beim Festgeld vereinbarst du mit der Bank eine Laufzeit und einen Zins. Die Bank plant mit diesem Geld, zum Beispiel für Kredite mit derselben Laufzeit. Deshalb ist eine ordentliche Kündigung im Vertrag ausgeschlossen. Du kommst erst am Ende der Laufzeit an das Geld, auch wenn du es dringend brauchst. Das ist kein Fehler des Produkts, sondern der Preis für den festen Zins.</p>
<p>Zwei Dinge gelten trotzdem immer:</p><ul>
<li><b>Widerrufsrecht.</b> Schließt du online oder per Post ab, kannst du den Vertrag innerhalb von 14 Tagen widerrufen, ohne Angabe von Gründen. Das steht im Fernfinanzdienstleistungs-Gesetz. Die Plattformen nennen diese Frist ausdrücklich in ihren Bedingungen.</li>
<li><b>Außerordentliche Kündigung aus wichtigem Grund.</b> Bei schweren Vertragsverletzungen der Bank oder in Ausnahmefällen, die im Vertrag stehen, kann der Vertrag vorzeitig beendet werden. Geldbedarf allein ist kein wichtiger Grund.</li></ul></div>'''),
       ('Wo eine vorzeitige Auflösung möglich ist',_tbl(['Angebot','Regel bei vorzeitiger Auflösung'],krow)+
        f'''<div class="prose"><p>Stand {stand}, laut Konditionen und Produktinformationsblättern der Anbieter. Zwei Muster kommen immer wieder vor:</p><ul>
<li><b>Vorschusszinsen.</b> Die Bank zieht 1 ‰ (ein Promille) pro Monat der nicht eingehaltenen Bindung ab, meist höchstens bis zur Höhe der Zinsen. Die Arbeiterkammer rechnet vor: 10.000 € mit einem Jahr Bindung, nach sechs Monaten aufgelöst, kosten 60 € Vorschusszinsen. Das frisst den Zinsertrag auf. Im Vergleich arbeiten {len(vorsch)} Angebote mit Vorschusszinsen.</li>
<li><b>Strafzins von 0,01 %.</b> Die Bank zahlt aus, verzinst das Geld aber rückwirkend nur mit 0,01 % pro Jahr. Praktisch bekommst du den Einsatz ohne Zinsen zurück. Das gilt bei {len(nullz)} Angeboten.</li></ul>
<p>Dazu kommt das <b>Flexgeld</b> über Raisin: ein Festgeld, das du jederzeit kündigen kannst. Dann gilt für die gesamte Anlagedauer ein niedrigerer Basiszins, bei manchen Banken 0 %, und die Auszahlung dauert einige Wochen. Im Vergleich gibt es {len(flex)} Flexgeld-Angebote{": "+", ".join(L_(a) for a in flex) if flex else ""}. Flexgeld ist eine Versicherung gegen Geldbedarf, die du mit dem Basiszins bezahlst.</p></div>'''),
       ('Sonderfälle: Todesfall, Härtefall, Insolvenz der Bank','''<div class="prose"><p><b>Todesfall.</b> Stirbt die Kontoinhaberin oder der Kontoinhaber, gehört das Festgeld zur Verlassenschaft. Bis zur Einantwortung sperrt die Bank das Konto, danach können die Erben darüber verfügen. Ob die Bank die Bindung vorzeitig auflöst, regeln ihre Bedingungen. Viele Banken tun das aus wichtigem Grund ohne Vorschusszinsen, andere lassen das Festgeld bis zum Ende weiterlaufen. Frag bei der Bank nach und lass dir die Regel schriftlich geben.</p>
<p><b>Härtefall.</b> Arbeitslosigkeit, Krankheit oder Scheidung sind rechtlich kein Grund, aus dem Vertrag zu kommen. Manche Banken lösen in solchen Fällen trotzdem auf, aus Kulanz und gegen Abschlag. Ein Anspruch besteht nicht. Wer solche Risiken sieht, hält mehr auf dem Tagesgeld oder wählt kürzere Laufzeiten.</p>
<p><b>Insolvenz der Bank.</b> Dann endet das Festgeld vorzeitig, und die Einlagensicherung zahlt bis 100.000 € pro Person und Bank innerhalb von 7 Arbeitstagen aus. Die Zinsen bis zum Sicherungsfall sind mitgesichert. Mehr im Beitrag zur <a href="../einlagensicherung/">Einlagensicherung</a>.</p></div>'''),
       ('Am Laufzeitende: automatische Verlängerung und Fristen',_tbl(['Regel','Angebote im Vergleich','Was das für dich heißt'],vrow)+
        f'''<div class="prose"><p>Die automatische Verlängerung ist die häufigste Falle beim Festgeld. Das Geld wird dann für dieselbe Laufzeit zu dem Zins angelegt, der an diesem Tag gilt, und der ist oft niedriger als der Aktionszins beim Abschluss. Wer das verhindern will, muss vor dem Laufzeitende aktiv werden. Die Fristen stehen in den Bedingungen: Bei Raisin kannst du die Verlängerung bis 2 Tage vor Laufzeitende im Online-Banking abschalten, andere Banken verlangen eine Weisung einige Tage oder Wochen vorher. Die Frist für jedes Angebot steht auf der Angebotsseite im <a href="{F}">Festgeld-Vergleich</a>.</p>
<p>Bei Angeboten ohne Verlängerung wird das Geld am Ende aufs Referenzkonto oder Verrechnungskonto überwiesen. Dort liegt es dann oft unverzinst, bis du es neu anlegst. Auch hier hilft ein Kalendereintrag.</p></div>'''),
       ('Vor dem Abschluss prüfen','''<div class="prose"><ul class="checks">
<li>Brauche ich das Geld in der Laufzeit sicher nicht? Notgroschen gehört aufs Tagesgeld.</li>
<li>Was steht im Vertrag zur vorzeitigen Auflösung: ausgeschlossen, Vorschusszinsen oder Strafzins?</li>
<li>Was passiert am Laufzeitende: Auszahlung, Wahl oder automatische Verlängerung? Bis wann muss ich mich melden?</li>
<li>Werden die Zinsen jährlich ausgezahlt oder erst am Ende? Bei langen Laufzeiten ist das ein Unterschied.</li>
<li>Wie komme ich an die Bank heran: Online-Banking, App, Brief? Bei Plattformen läuft alles über das Plattform-Konto.</li>
<li>Habe ich das Laufzeitende im Kalender, mit einer Erinnerung zwei Wochen vorher?</li></ul></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Kündigungsregeln und Verlängerung je Angebot: Konditionsseiten, Bedingungen und Produktinformationsblätter der Banken und Plattformen, verlinkt auf jeder Angebotsseite im <a href="{F}">Festgeld-Vergleich</a>, Stand {stand}.</li>
<li>Vorschusszinsen und Rechenbeispiel: {_ext(AK_AUFL,"Arbeiterkammer Wien, Voreiliges Auflösen von Spareinlagen kommt teuer")}, abgerufen am {ABGERUFEN}.</li>
<li>Einlagensicherung im Insolvenzfall: {_ext(AK_ES,"Arbeiterkammer Wien, Einlagensicherung")}, abgerufen am {ABGERUFEN}.</li></ul></div>'''),
      ],
      faq=[
       ('Kann ich ein Festgeld vorzeitig kündigen?',f'Normalerweise nicht. Im Vergleich schließen {len(nokuend)} von {n} Angeboten eine vorzeitige Auflösung aus. Wo sie möglich ist, kostet sie Vorschusszinsen oder den Zins für die ganze Laufzeit.'),
       ('Was sind Vorschusszinsen?','Ein Abzug von meist 1 ‰ pro Monat der nicht eingehaltenen Bindung, höchstens bis zur Höhe der Zinsen. Bei 10.000 € und sechs Monaten zu früh sind das 60 €.'),
       ('Was ist Flexgeld?','Ein Festgeld über Raisin, das du jederzeit kündigen kannst. Dann gilt rückwirkend ein niedrigerer Basiszins, bei manchen Banken 0 %. Hältst du die Laufzeit durch, bekommst du den vollen Zins.'),
       ('Kann ich ein Festgeld nach dem Abschluss widerrufen?','Ja, bei Abschluss online oder per Post innerhalb von 14 Tagen ohne Angabe von Gründen. Danach gilt die Bindung.'),
       ('Was passiert mit dem Festgeld im Todesfall?','Es gehört zur Verlassenschaft. Nach der Einantwortung können die Erben darüber verfügen. Ob die Bank die Bindung vorzeitig und ohne Abschlag auflöst, hängt von ihren Bedingungen ab.'),
       ('Was ist eine automatische Verlängerung?',f'Ohne deine Weisung legt die Bank das Geld am Laufzeitende für dieselbe Laufzeit zum dann gültigen Zins neu an. Im Vergleich gilt das bei {len(verl["automatisch"])} von {n} Angeboten. Die Frist, bis zu der du widersprechen musst, steht auf der Angebotsseite.'),
      ],
      related=['festgeld-oder-tagesgeld','zinstreppe','festgeld-plattformen'])

    # ---------- 5. Plattformen ----------
    def _cnt(xs_,f): return len([a for a in xs_ if f(a)])
    prow=[('Direkt bei der Bank',len(direkt),f'{_cnt(direkt,lambda a:a["steuer_auto"])} von {len(direkt)}',f'{_cnt(direkt,lambda a:a["kuendigung"] in ("ja","ja_mit_abschlag"))}','Konto bei der Bank, Legitimation je Bank neu','je nach Bank, meist kostenlos'),
          ('Raisin',len(raisin),f'{_cnt(raisin,lambda a:a["steuer_auto"])} von {len(raisin)}',f'{_cnt(raisin,lambda a:a["kuendigung"] in ("ja","ja_mit_abschlag"))}','Raisin-Konto bei der Raisin Bank AG (Frankfurt), einmal VideoIdent','kostenlos'),
          ('PickTheBank',len(ptb),f'{_cnt(ptb,lambda a:a["steuer_auto"])} von {len(ptb)}',f'{_cnt(ptb,lambda a:a["kuendigung"] in ("ja","ja_mit_abschlag"))}','Konto direkt bei der Bank, Online-Identifizierung über die Plattform','kostenlos')]
    zr12,ar12=_best(raisin,12); zd12,ad12=_best(direkt,12)
    art('at','festgeld-plattformen',
      h1='Festgeld-Plattformen: Raisin, PickTheBank und der Direktabschluss',
      mt='Festgeld-Plattformen Österreich: Raisin & Co. | Finvallo',
      desc=f'Festgeld-Plattformen in Österreich: Wie Raisin und PickTheBank funktionieren, wo dein Geld liegt, was es kostet und wer die KESt abführt. {len(raisin)} von {n} Angeboten im Vergleich laufen über Raisin.',
      about='Festgeld in Österreich',
      lede='Eine Anmeldung, viele Banken aus ganz Europa: Das ist das Versprechen der Plattformen. Es stimmt, hat aber einen Haken bei der Steuer.',
      kurz=(f'Über eine Festgeld-Plattform legst du mit einem Konto bei Banken aus mehreren EU-Ländern an. In Österreich ist Raisin die wichtigste: {len(raisin)} der {n} Angebote im Vergleich laufen über das kostenlose Raisin-Konto bei der Raisin Bank AG in Frankfurt. '
            f'Dein Geld liegt bei der jeweiligen Partnerbank, gesichert durch deren Einlagensicherung bis 100.000 €. Der Haken: Keines der Plattform-Angebote führt die KESt ab, du musst die Zinsen selbst in der Beilage E1kv erklären. '
            f'Beim Direktabschluss bei einer österreichischen Bank ist die Steuer dagegen mit dem Abzug erledigt.'),
      secs=[
       ('So funktioniert eine Festgeld-Plattform',f'''<div class="prose"><p>Eine Plattform ist ein Vermittler. Sie sammelt Festgeld-Angebote von Banken, die selbst keine Filialen oder keine Kundschaft in Österreich haben, und wickelt die Anlage ab. Bei Raisin läuft das so:</p><ol>
<li><b>Registrieren und legitimieren.</b> Du eröffnest online ein Raisin-Konto und bestätigst deine Identität einmal per VideoIdent. Das Raisin-Konto ist ein Verrechnungskonto bei der Raisin Bank AG in Frankfurt. Es kostet nichts.</li>
<li><b>Angebot wählen.</b> Du suchst dir ein Festgeld einer Partnerbank aus und gibst den Betrag ein. Weitere Anlagen bei anderen Partnerbanken brauchen keine neue Legitimation.</li>
<li><b>Geld überweisen.</b> Du überweist vom Referenzkonto auf das Raisin-Konto oder erteilst eine Einzugsermächtigung. Raisin leitet den Betrag an die Partnerbank weiter.</li>
<li><b>Laufzeitende.</b> Die Partnerbank zahlt Kapital und Zinsen auf das Raisin-Konto zurück. Von dort überweist du es aufs Referenzkonto oder legst neu an.</li></ol>
<p>Bei den meisten Raisin-Angeboten läuft die Anlage über eine Treuhandvereinbarung: Die Raisin Bank hält das Festgeld in deinem Auftrag bei der Partnerbank. Gesichert ist das Geld trotzdem auf deinen Namen, bei der Einlagensicherung des Landes, in dem die Partnerbank sitzt.</p>
<p>PickTheBank funktioniert anders. Die Plattform vergleicht Angebote und leitet dich zur Eröffnung weiter, das Festgeldkonto wird aber direkt bei der Bank eröffnet, und du zahlst direkt an die Bank. Ein Verrechnungskonto gibt es nicht. Im Vergleich gibt es über PickTheBank {len(ptb)} Angebot{"e" if len(ptb)!=1 else ""}{": "+", ".join(L_(a) for a in ptb) if ptb else ""}.</p></div>'''),
       ('Die Wege im Vergleich',_tbl(['Weg','Angebote','KESt automatisch','Vorzeitig kündbar','Konto und Legitimation','Kosten'],prow)+
        f'''<div class="prose"><p>Stand {stand}. Der beste Zins für 1 Jahr liegt über Raisin bei {_pct(zr12)} ({L_(ar12)}), direkt bei einer Bank bei {_pct(zd12)} ({L_(ad12)}). Die Reihenfolge wechselt mit jeder Zinsänderung, im <a href="{F1}">Vergleich für 1 Jahr</a> siehst du den aktuellen Stand. Wer nur österreichische Banken will, filtert in der Liste <a href="{FH}">österreichische Banken</a>.</p></div>'''),
       ('Was es kostet',f'''<div class="prose"><p>Für dich nichts. Raisin verlangt weder für das Konto noch für die Anlage oder die Rücküberweisung etwas, auch Auslandsüberweisungen sind laut Plattform kostenlos. PickTheBank nennt sich selbst eine Informationsquelle und nimmt vom Anleger kein Geld. Die Plattformen verdienen an den Partnerbanken, die für die Vermittlung zahlen. Das ist auch der Grund, warum die Plattform-Angebote nicht immer die höchsten Zinsen haben: Die Vermittlungsgebühr muss die Bank irgendwo hereinholen.</p>
<p>Versteckte Kosten gibt es an anderer Stelle: Zinsen, die auf dem Verrechnungskonto liegen, bringen nichts, bis du sie neu anlegst. Und wer die Steuer selbst erklären muss, bezahlt mit Zeit, siehe unten.</p></div>'''),
       ('Steuer: der große Unterschied',f'''<div class="prose"><p>Bei einer österreichischen Bank behält die Bank 25 % KESt von den Zinsen ein und führt sie ans Finanzamt ab. Damit ist die Steuer erledigt, du musst nichts angeben. Im Vergleich gilt das bei {len(auto)} von {n} Angeboten, fast alle davon Direktabschlüsse.</p>
<p>Über Raisin und PickTheBank ist das anders: Die Partnerbanken sitzen im Ausland und führen keine österreichische KESt ab. Die Zinsen kommen brutto, oder nach Abzug einer ausländischen Quellensteuer, auf dein Verrechnungskonto. Du musst sie in der Einkommensteuererklärung in der Beilage E1kv angeben. Der Steuersatz bleibt 25 %, es ist also nicht mehr Steuer, nur mehr Arbeit. Raisin stellt dir dafür eine Jahresaufstellung bereit. Bei Banken in Portugal, Lettland oder Litauen kommt die Quellensteuer dazu, die du mit einer Ansässigkeitsbescheinigung senken und dann in Österreich anrechnen kannst. Das ganze Verfahren steht im Beitrag <a href="../festgeld-steuern/">Festgeld und Steuern</a>.</p>
<p>Vergisst du die Angabe, ist das Steuerhinterziehung. Die Plattformen melden Zinsen im Rahmen des automatischen Informationsaustauschs der EU an die Finanzverwaltung, das Finanzamt erfährt also davon.</p></div>'''),
       ('Wo dein Geld wirklich liegt',f'''<div class="prose"><p>Dein Geld liegt bei der Partnerbank, nicht bei der Plattform. Für die Einlagensicherung zählt deshalb das Sitzland der Partnerbank: Italien, Estland, Portugal, Schweden oder ein anderes EU-Land, jeweils bis 100.000 € pro Person und Bank. Das Verrechnungskonto bei der Raisin Bank AG ist über die deutsche Einlagensicherung geschützt, dort liegt das Geld aber nur kurz. Geht die Plattform selbst pleite, bleibt dein Festgeld bei der Partnerbank bestehen.</p>
<p>Über Raisin kommen im Vergleich Banken aus {len({a["sitz"] for a in raisin})} Ländern. Welches Land und welche Sicherungseinrichtung für ein Angebot gelten, steht auf jeder Angebotsseite, zusammen mit dem Länderrating. Mehr dazu im Beitrag zur <a href="../einlagensicherung/">Einlagensicherung</a>.</p></div>'''),
       ('Plattform oder Direktabschluss?','''<div class="prose"><p><b>Für die Plattform spricht:</b></p><ul class="checks">
<li>Eine Legitimation, ein Login, viele Banken. Praktisch für eine Zinstreppe über mehrere Banken.</li>
<li>Zugang zu Banken, die in Österreich sonst nicht anbieten, oft mit höheren Zinsen.</li>
<li>Einfaches Streuen über mehrere Länder, um unter 100.000 € pro Bank zu bleiben.</li></ul>
<p><b>Für den Direktabschluss spricht:</b></p><ul>
<li>KESt wird automatisch abgeführt, keine Steuererklärung nötig.</li>
<li>Keine ausländische Quellensteuer und kein Papierkram mit Ansässigkeitsbescheinigungen.</li>
<li>Du bist direkt Kunde der Bank, mit Ansprechpartner in Österreich und oft mit vorzeitiger Auflösung gegen Abschlag.</li>
<li>Kein Umweg über ein Verrechnungskonto, das Geld kommt am Ende direkt aufs eigene Konto.</li></ul>
<p>Faustregel: Wer ohnehin eine Steuererklärung macht und größere Beträge streuen will, gewinnt mit der Plattform an Auswahl. Wer es einfach will, bleibt bei einer österreichischen Bank und verzichtet auf ein paar Zehntel Prozent.</p></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Ablauf und Kosten bei Raisin: {_ext(RAISIN_ANL,"Raisin Österreich, So funktioniert Raisin")}, abgerufen am {ABGERUFEN}.</li>
<li>PickTheBank: {_ext(PTB,"PickTheBank, Festgeld in Österreich")}, abgerufen am {ABGERUFEN}.</li>
<li>Steuerabwicklung, Quellensteuer, Kündigung und Einlagensicherung je Angebot: Produktinformationsblätter und Konditionsseiten, verlinkt auf jeder Angebotsseite im <a href="{F}">Festgeld-Vergleich</a>, Stand {stand}.</li>
<li>KESt und Erklärungspflicht: {_ext(BMF_ALLG,"BMF, Allgemeine Informationen zu Einkünften aus Kapitalvermögen")}, abgerufen am {ABGERUFEN}.</li></ul></div>'''),
      ],
      faq=[
       ('Ist Festgeld über Raisin sicher?','Dein Geld liegt bei der Partnerbank und ist über die Einlagensicherung ihres Sitzlandes bis 100.000 € pro Person und Bank geschützt. Das Verrechnungskonto bei der Raisin Bank AG fällt unter die deutsche Einlagensicherung. Eine Pleite der Plattform selbst berührt dein Festgeld nicht.'),
       ('Was kostet Raisin?','Nichts. Konto, Anlage und Rücküberweisung sind kostenlos. Die Plattform wird von den Partnerbanken bezahlt.'),
       ('Führt Raisin die KESt ab?',f'Nein. Keines der {len(raisin)} Raisin-Angebote im Vergleich führt die österreichische KESt ab. Du gibst die Zinsen selbst in der Beilage E1kv an, der Steuersatz bleibt 25 %.'),
       ('Wie unterscheidet sich PickTheBank von Raisin?','PickTheBank vermittelt dich zur Bank, das Festgeldkonto wird direkt dort eröffnet, und du zahlst direkt an die Bank. Raisin führt ein eigenes Verrechnungskonto, über das alle Anlagen laufen.'),
       ('Lohnt sich die Plattform gegenüber dem Direktabschluss?',f'Wenn die Plattform-Angebote höhere Zinsen bringen und du die Steuererklärung nicht scheust, ja. Im Vergleich liegt der beste 1-Jahres-Zins über Raisin bei {_pct(zr12)}, direkt bei {_pct(zd12)}, Stand {stand}.'),
      ],
      related=['festgeld-steuern','einlagensicherung','zinstreppe'])

    # ---------- 6. Steuern ----------
    B=10000; br=B*z12/100; kest=br*0.25
    srow=[('Bank in Österreich, zum Beispiel '+L_(ah12),f'{eur(round(B*zh12/100,2))} €','25 % KESt, automatisch abgezogen',f'{eur(round(B*zh12/100*0.75,2))} €','nichts, Endbesteuerung'),
          ('Bank im Ausland ohne Quellensteuer, zum Beispiel über Raisin in Italien oder Estland',f'{eur(round(br,2))} €','0 % im Ausland, 25 % in Österreich',f'{eur(round(br*0.75,2))} €','Zinsen in der Beilage E1kv angeben'),
          ('Bank in Portugal mit Ansässigkeitsbescheinigung',f'{eur(round(br,2))} €','10 % Quellensteuer, in Österreich 25 % minus 10 % angerechnet',f'{eur(round(br*0.75,2))} €','E1kv ausfüllen, Quellensteuer angeben, Bescheinigung vorher einreichen'),
          ('Bank in Portugal ohne Ansässigkeitsbescheinigung',f'{eur(round(br,2))} €','28 % Quellensteuer, davon nur 10 % anrechenbar, plus 15 % in Österreich',f'{eur(round(br*(1-0.28-0.15),2))} € bis zur Rückerstattung','E1kv, dazu Rückforderung von 18 % beim portugiesischen Finanzamt')]
    qrow=[('Portugal','28 %','10 %','Ansässigkeitsbescheinigung und Formular 21-RFI, spätestens 4 Wochen vor der Zinszahlung'),
          ('Lettland','25,5 %','10 %','Ansässigkeitsbescheinigung, spätestens 8 Wochen vor Fälligkeit'),
          ('Litauen','15 %','10 %','Ansässigkeitsbescheinigung und Steuerformular, spätestens 4 Wochen vor der Zinszahlung'),
          ('Spanien (Zweigniederlassung)','19 %','5 %','Steueransässigkeitsformular rechtzeitig einreichen'),
          ('Italien, Estland, Schweden, Frankreich, Malta, Deutschland','0 %','–','nichts, Zinsen kommen brutto')]
    art('at','festgeld-steuern',
      h1='Festgeld und Steuern in Österreich: KESt, E1kv und Quellensteuer',
      mt='Festgeld und Steuern in Österreich: KESt | Finvallo',
      desc=f'Festgeld-Zinsen versteuern in Österreich: 25 % KESt, bei inländischen Banken automatisch, bei ausländischen über die Beilage E1kv. Quellensteuer in Portugal, Lettland und Litauen anrechnen. Mit Rechenbeispiel.',
      about='Festgeld in Österreich',
      lede='Auf Zinsen zahlst du in Österreich 25 % Kapitalertragsteuer. Die Frage ist nur, wer sie abführt: die Bank oder du.',
      kurz=(f'Zinsen aus Festgeld sind Einkünfte aus Kapitalvermögen und kosten 25 % KESt. Eine Bank in Österreich zieht die Steuer automatisch ab, damit ist alles erledigt (Endbesteuerung). Eine Bank im Ausland tut das nicht: Dann gibst du die Zinsen in der Beilage E1kv zur Einkommensteuererklärung an, weiterhin mit 25 %. '
            f'Im Vergleich führen {len(auto)} von {n} Angeboten die KESt automatisch ab, bei {len(manuell)} musst du selbst erklären. Behält das Ausland Quellensteuer ein, kannst du sie bis zum Satz des Doppelbesteuerungsabkommens anrechnen, meist 10 %.'),
      secs=[
       ('25 % KESt auf Zinsen',f'''<div class="prose"><p>Zinsen aus Geldeinlagen bei Banken, also aus Sparbuch, Tagesgeld und Festgeld, unterliegen in Österreich der Kapitalertragsteuer von 25 %. Das ist der niedrigere der beiden KESt-Sätze: Für Dividenden, Fonds und Anleihen gelten 27,5 %. Die Steuer wird isoliert vom übrigen Einkommen berechnet, deine Zinsen erhöhen also nicht den Steuersatz auf dein Gehalt.</p>
<p>Einen Freibetrag wie den deutschen Sparer-Pauschbetrag gibt es in Österreich nicht. Jeder Euro Zinsen wird besteuert. Nur wenn dein gesamtes Einkommen so niedrig ist, dass dein Tarif unter 25 % liegt, kannst du in der Steuererklärung die Regelbesteuerung beantragen. Dann werden die Zinsen mit deinem normalen Steuersatz besteuert und die KESt angerechnet. Das lohnt sich etwa für Studierende oder Pensionistinnen mit geringem Einkommen.</p>
<p>Beispiel: {eur(B)} € ein Jahr lang zum besten Zins im Vergleich, {_pct(z12)} bei {L_(a12)}, bringen {eur(round(br,2))} € Zinsen. Davon gehen {eur(round(kest,2))} € KESt ab, {eur(round(br-kest,2))} € bleiben. Für andere Beträge rechnet der <a href="{RK}">KESt-Rechner</a>.</p></div>'''),
       ('Bank in Österreich: Endbesteuerung',f'''<div class="prose"><p>Hat die Bank ihren Sitz in Österreich, behält sie die 25 % direkt bei der Zinsgutschrift ein und führt sie ans Finanzamt ab. Auf dem Kontoauszug siehst du Bruttozins, KESt und Nettozins. Damit ist die Einkommensteuer auf diese Zinsen abgegolten, du musst sie in keiner Steuererklärung mehr angeben. Das BMF nennt das Endbesteuerung. Sie gilt auch für Zweigniederlassungen ausländischer Banken in Österreich, die als inländische auszahlende Stelle gelten.</p>
<p>Im Vergleich führen {len(auto)} von {n} Angeboten die KESt automatisch ab. Das sind fast alle Direktabschlüsse bei Banken mit Sitz in Österreich, gesammelt in der Liste <a href="{FH}">österreichische Banken</a>. Auf jeder Angebotsseite steht unter „Steuer“, ob die KESt abgeführt wird.</p></div>'''),
       ('Bank im Ausland: selbst erklären mit E1kv',f'''<div class="prose"><p>Eine Bank in Italien, Estland oder Schweden führt keine österreichische KESt ab. Die Zinsen kommen brutto bei dir an. Du bist dann selbst verpflichtet, sie zu erklären, und zwar in der Beilage E1kv zur Einkommensteuererklärung (Formular E1). Der Steuersatz ist derselbe, 25 %. Das Finanzamt setzt die Steuer im Bescheid fest, und du zahlst sie nach. Im Vergleich betrifft das {len(manuell)} Angebote, darunter alle {len(raisin)} über Raisin. Die Plattformen nennen solche Angebote „nicht steuereinfach“.</p>
<p>So gehst du vor:</p><ol>
<li>Sammle die Jahresaufstellung der Bank oder Plattform. Raisin stellt sie im Online-Banking bereit.</li>
<li>Reiche die Einkommensteuererklärung über FinanzOnline ein. Die Frist ist der 30. Juni des Folgejahres, auf Papier der 30. April. Wer sonst nur die Arbeitnehmerveranlagung macht, muss wegen der ausländischen Zinsen auf die Einkommensteuererklärung E1 wechseln, sobald die Kapitaleinkünfte ohne KESt-Abzug 22 € im Jahr übersteigen.</li>
<li>Trag die Zinsen in der Beilage E1kv unter den Einkünften aus Kapitalvermögen ein, die dem Sondersteuersatz von 25 % unterliegen. Im Ausland einbehaltene Quellensteuer trägst du im Feld für die anrechenbare ausländische Steuer ein.</li></ol>
<p>Nicht erklären ist keine Option. Die Banken melden Zinsen von EU-Bürgerinnen und EU-Bürgern über den automatischen Informationsaustausch an das Wohnsitzland. Das österreichische Finanzamt bekommt die Daten also auch ohne dich.</p></div>'''),
       ('Ausländische Quellensteuer: Sätze und Anrechnung',_tbl(['Sitzland der Bank','Quellensteuer ohne Nachweis','Mit Ansässigkeitsbescheinigung','Was du einreichen musst'],qrow)+
        f'''<div class="prose"><p>Sätze laut Produktinformationsblättern der Angebote im <a href="{F}">Festgeld-Vergleich</a>, Stand {stand}. Sie gelten je Bank, nicht pauschal je Land: Raisin selbst nennt für Lettland in seiner Länderübersicht 20 %, die Produktblätter der lettischen Banken im Vergleich 25,5 % seit 2025. Verlässlich ist nur das Produktinformationsblatt des konkreten Angebots.</p>
<p>Die Anrechnung in Österreich hat eine Grenze: Du kannst nur so viel ausländische Steuer anrechnen, wie das Doppelbesteuerungsabkommen dem anderen Staat zugesteht, bei Portugal, Lettland und Litauen 10 %. Hat die Bank mehr einbehalten, weil deine Ansässigkeitsbescheinigung fehlte, bekommst du den Rest nur vom ausländischen Finanzamt zurück. Das dauert Monate und ist mühsam. Reiche die Bescheinigung deshalb vor der ersten Zinszahlung ein. Du bekommst sie als Formular ZS-A über FinanzOnline, meist innerhalb weniger Tage. Bei Portugal und Litauen braucht die Bank zusätzlich ein eigenes Formular.</p></div>'''),
       ('Rechenbeispiel: 10.000 € für ein Jahr',_tbl(['Weg','Zinsen brutto','Steuer','Netto','Was du tun musst'],srow)+
        f'''<div class="prose"><p>Gerechnet mit dem besten Zins für 1 Jahr im Vergleich, {_pct(z12)}, für die inländische Zeile mit dem besten Zins einer Bank mit Sitz in Österreich, {_pct(zh12)}. Die Nettobeträge bei korrekter Anrechnung sind gleich hoch, der Unterschied liegt in der Arbeit. Ohne Ansässigkeitsbescheinigung fehlen dir bis zur Rückerstattung aus Portugal 18 % der Zinsen.</p></div>'''),
       ('Was bei Gemeinschaftskonten, Kindern und Zinsgutschrift gilt',f'''<div class="prose"><ul>
<li><b>Gemeinschaftskonto.</b> Die Zinsen werden steuerlich den Inhabern anteilig zugerechnet, bei zwei Inhabern je zur Hälfte. Für die KESt bei einer inländischen Bank ändert das nichts. Bei ausländischen Zinsen erklärt jede Person ihren Anteil. Im Vergleich erlauben nur {len([a for a in xs if a.get("gemeinschaftskonto")])} Angebote ein Gemeinschaftskonto.</li>
<li><b>Kinder.</b> Zinsen auf einem Sparkonto, das dem Kind gehört, sind Einkünfte des Kindes. Eine inländische Bank zieht die KESt genauso ab. Hat das Kind sonst kein Einkommen, kann sich die Regelbesteuerung lohnen, dann bekommt es die KESt über die Steuererklärung zurück.</li>
<li><b>Zeitpunkt.</b> Steuerpflichtig sind die Zinsen in dem Jahr, in dem sie gutgeschrieben werden. Bei einem Festgeld über 3 Jahre mit Zinszahlung am Ende fällt die ganze Steuer im dritten Jahr an, bei jährlicher Auszahlung jedes Jahr ein Teil. Für die Höhe der Steuer macht das bei 25 % keinen Unterschied.</li>
<li><b>Verluste.</b> Zinsen lassen sich nicht mit Verlusten aus Aktien oder Fonds verrechnen. Der Verlustausgleich gilt nur innerhalb der Einkünfte mit 27,5 %.</li></ul></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>KESt-Satz, Endbesteuerung, Erklärungspflicht bei ausländischen Zinsen, isolierte Besteuerung: {_ext(BMF_INL,"BMF, Besteuerung inländischer sowie im Inland bezogener Kapitalerträge")} und {_ext(BMF_ALLG,"BMF, Allgemeine Informationen zu Einkünften aus Kapitalvermögen")}, abgerufen am {ABGERUFEN}.</li>
<li>Quellensteuersätze, Fristen und Formulare je Bank: Produktinformationsblätter der Angebote, verlinkt auf jeder Angebotsseite im <a href="{F}">Festgeld-Vergleich</a>, Stand {stand}; Länderübersicht und Formular ZS-A: {_ext(RAISIN_QST,"Raisin Österreich, Quellensteuer")}, abgerufen am {ABGERUFEN}.</li>
<li>Steuerabwicklung je Angebot (automatisch oder selbst): Angaben der Banken und Plattformen, Stand {stand}.</li></ul>
<p>Dieser Beitrag ersetzt keine Steuerberatung. Bei größeren Beträgen im Ausland lohnt sich die Frage an eine Steuerberaterin oder einen Steuerberater.</p></div>'''),
      ],
      faq=[
       ('Wie hoch ist die Steuer auf Festgeld-Zinsen in Österreich?','25 % Kapitalertragsteuer, bei allen Banken gleich. Der höhere Satz von 27,5 % gilt nur für Dividenden, Fonds und Anleihen, nicht für Zinsen aus Geldeinlagen.'),
       ('Muss ich Festgeld-Zinsen in der Steuererklärung angeben?','Bei einer Bank in Österreich nicht, die KESt wird automatisch abgezogen und die Steuer ist damit erledigt. Bei einer Bank im Ausland ja, in der Beilage E1kv zur Einkommensteuererklärung.'),
       ('Gibt es in Österreich einen Freibetrag für Zinsen?','Nein. Anders als in Deutschland wird jeder Euro Zinsen besteuert. Nur wer insgesamt so wenig verdient, dass sein Steuersatz unter 25 % liegt, kann die Regelbesteuerung beantragen und bekommt KESt zurück.'),
       ('Was ist mit der Quellensteuer in Portugal oder Lettland?','Die Bank behält dort 28 % beziehungsweise 25,5 % ein. Mit einer Ansässigkeitsbescheinigung aus FinanzOnline sinkt der Satz auf 10 %, und diese 10 % rechnest du in Österreich auf die KESt an. Zu viel einbehaltene Steuer musst du im Ausland zurückfordern.'),
       ('Was bedeutet „nicht steuereinfach“?','Dass die Bank die österreichische KESt nicht abführt und du die Zinsen selbst erklären musst. Das gilt bei allen Raisin-Angeboten im Vergleich. Mehr Steuer zahlst du dadurch nicht, nur mehr Arbeit.'),
       ('Bis wann muss ich ausländische Zinsen erklären?','Die Einkommensteuererklärung über FinanzOnline ist bis 30. Juni des Folgejahres fällig, auf Papier bis 30. April. Mit Steuerberatung gelten längere Fristen.'),
      ],
      related=['festgeld-plattformen','einlagensicherung','festgeld-oder-tagesgeld'])
