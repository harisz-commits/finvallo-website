# Ratgeber (nur DE) zu Festgeld: Festgeld oder Tagesgeld, Einlagensicherung, Zinstreppe, Kündigen, Plattformen, Steuern. Gleiche Slugs wie in AT (hreflang-Paare).
# Zahlen kommen live aus daten/de/festgeld.json und daten/festgeld-laender.json (dieselben Daten wie der Festgeld-Vergleich).
# Rechtliches: Einlagensicherung laut BaFin und EinSiG; Abgeltungsteuer, Sparer-Pauschbetrag, Günstigerprüfung und Anrechnung laut EStG (gesetze-im-internet.de);
# Widerruf und außerordentliche Kündigung laut BGB; Plattformen laut Deutsche Bank, CHECK24 und Raisin. Abgerufen am 28.10.2026.
# Aufruf aus ratgeber.build('de'): register(art,P,eur)
import html,json,os
E=lambda s: html.escape(str(s)) if s is not None else ''
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'daten')
BAFIN_ES='https://www.bafin.de/DE/Verbraucher/Bank/Einlagensicherung/einlagensicherung_node.html'
EDB='https://edb-banken.de'
BDB_FONDS='https://einlagensicherungsfonds.de/'
EINSIG8='https://www.gesetze-im-internet.de/einsig/__8.html'
ESTG=lambda n: f'https://www.gesetze-im-internet.de/estg/__{n}.html'
BGB=lambda n: f'https://www.gesetze-im-internet.de/bgb/__{n}.html'
DB_ZM='https://www.deutsche-bank.de/pk/sparen-und-anlegen/sparen/zinsmarkt.html'
C24_ANL='https://www.check24.de/geldanlage/ratgeber/geldanlagecenter-anlagekonto/'
RAISIN_QST='https://www.raisin.com/de-de/steuer/quellensteuer/'
RAISIN_ANL='https://www.raisin.com/de-de/so-funktionierts/anleitung/'
RIKS='https://storage.mfn.se/a24f7466-2756-4628-8b7c-bc9aa1084bfc/insattningsgarantins-maxbelopp-andras-till-1-150-000-kronor.pdf'
ABGERUFEN='28.10.2026'
SOLI=0.055

def _tbl(head,rows):
    h=''.join(f'<th>{c}</th>' for c in head)
    b=''.join('<tr>'+''.join(f'<td>{c}</td>' for c in r)+'</tr>' for r in rows)
    return f'<div class="tbl wide"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'
def _ext(u,t): return f'<a href="{E(u)}" target="_blank" rel="noopener">{E(t)} ↗</a>'
def _pct(x,d=2):
    s=f'{x:.{d}f}'.replace('.',','); return (s[:-3] if s.endswith(',00') else s)+' %'
def _dmy(s): return '.'.join(reversed(s.split('-'))) if s else ''
def _load():
    d=json.load(open(os.path.join(D,'de','festgeld.json'),encoding='utf-8'))
    L=json.load(open(os.path.join(D,'festgeld-laender.json'),encoding='utf-8'))
    return d,[a for a in d['angebote'] if a.get('status','ok')=='ok'],L
def _best(xs,m):
    c=[(z['zins'],a) for a in xs for z in a['zinsen'] if z['monate']==m]
    return max(c,key=lambda t:t[0]) if c else (None,None)
def _n(xs,m): return len({a['id'] for a in xs for z in a['zinsen'] if z['monate']==m})
def _vt(a):
    if a['vertrieb']=='ZinsMarkt': return 'ZinsMarkt der norisbank' if a['id'].endswith('zinsmarkt-norisbank') else 'ZinsMarkt der Deutschen Bank'
    return {'Check24':'CHECK24','direkt':'direkt'}.get(a['vertrieb'],a['vertrieb'].replace('andere: ',''))
def _sich(L,cc):
    l=L.get(cc) or {}
    w=l.get('waehrung') or '€'
    return f'{l["betrag"]:,.0f}'.replace(',','.')+(' '+w if w!='€' else ' €') if l.get('betrag') else '–'

def register(art,P,eur):
    d,xs,L=_load()
    stand=_dmy(d['stand'])
    F=f'{P}de/festgeld/'; F1=f'{F}1-jahr/'; FH=f'{F}bestenlisten/deutsche-banken/'; FM=f'{F}methodik/'
    RK=f'{P}de/rechner/kapitalertragsteuer/'; RZ=f'{P}de/rechner/zinseszins/'
    def L_(a): return f'<a class="lnk" href="{F}{a["id"]}/">{E(a["bank"])}</a> <small class="mut">({E(_vt(a))})</small>'
    n=len(xs)
    raisin=[a for a in xs if a['vertrieb']=='Raisin']; c24=[a for a in xs if a['vertrieb']=='Check24']; zm=[a for a in xs if a['vertrieb']=='ZinsMarkt']; direkt=[a for a in xs if a['vertrieb']=='direkt']
    heim=[a for a in xs if a['sitz']=='DE']; auslan=[a for a in xs if a['sitz']!='DE']
    auto=[a for a in xs if a['steuer_auto']]; manuell=[a for a in xs if a['steuer_auto'] is False]
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
    bvr=[a for a in xs if 'BVR' in (a['einlagensicherung'].get('system') or '')]
    spk=[a for a in xs if 'Sparkassen' in (a['einlagensicherung'].get('system') or '')]
    bdb=[a for a in xs if 'Bundesverband' in (a['einlagensicherung'].get('freiwillig') or '') or 'BdB' in (a['einlagensicherung'].get('freiwillig') or '')]
    gk=[a for a in xs if a.get('gemeinschaftskonto')]

    # ---------- 1. Festgeld oder Tagesgeld ----------
    art('de','festgeld-oder-tagesgeld',
      h1='Festgeld oder Tagesgeld: Was passt wann in Deutschland?',
      mt='Festgeld oder Tagesgeld in Deutschland? | Finvallo',
      desc=f'Festgeld oder Tagesgeld in Deutschland: Unterschiede, wann sich die Zinsbindung lohnt und wie du beides kombinierst. Mit aktuellen Zinsen aus {n} Festgeld-Angeboten bis {_pct(z60)}.',
      about='Festgeld in Deutschland',
      lede='Tagesgeld ist jederzeit verfügbar, Festgeld hat den festen Zins. Die richtige Antwort ist für die meisten: beides, nur in der richtigen Aufteilung.',
      kurz=(f'Festgeld bindet dein Geld für eine feste Laufzeit und sichert dir dafür den Zins. Im Vergleich zahlen die besten Angebote für 1 Jahr bis {_pct(z12)} ({E(a12["bank"])}), für 5 Jahre bis {_pct(z60)}. '
            'Tagesgeld bleibt täglich verfügbar, die Bank kann den Zins aber jederzeit senken, und die hohen Sätze gelten oft nur für Neukunden. Die sinnvolle Aufteilung: Notgroschen aufs Tagesgeld, den Rest fest, bei größeren Summen in mehreren Laufzeiten.'),
      secs=[
       ('Der Unterschied in einem Satz','''<div class="prose"><p>Beim Festgeld überlässt du der Bank einen Betrag für eine feste Zeit, von einem Monat bis zu zehn Jahren. Der Zins steht beim Abschluss fest und ändert sich nicht mehr. Beim Tagesgeld liegt das Geld auf einem Konto ohne Laufzeit. Du kannst es täglich aufs Girokonto holen, und die Bank kann den Zins mit kurzer Frist ändern.</p>
<p>Beides sind Einlagen: gesetzlich gesichert bis 100.000 € pro Person und Bank, und auf die Zinsen fällt Abgeltungsteuer an, soweit sie über dem Sparer-Pauschbetrag liegen. Der Unterschied liegt allein in Bindung und Zinsgarantie.</p></div>'''),
       ('Festgeld und Tagesgeld im Vergleich',_tbl(['','Festgeld','Tagesgeld'],[
            ('Verfügbarkeit','erst am Laufzeitende, vorzeitig meist gar nicht oder nur mit Abschlag','täglich'),
            ('Zins','für die ganze Laufzeit garantiert','variabel, die Bank kann ihn jederzeit ändern'),
            ('Zinshöhe im Vergleich',f'bis {_pct(z12)} für 1 Jahr, bis {_pct(z36)} für 3 Jahre, bis {_pct(z60)} für 5 Jahre','Aktionszins oft nur 3 bis 6 Monate für Neukunden, danach Basiszins'),
            ('Mindestanlage',f'je nach Angebot ab {eur(mins[0])} € bis {eur(mins[-1])} €','meist keine'),
            ('Nachschießen','nicht möglich, jede Anlage ist ein eigener Vertrag','jederzeit'),
            ('Planbarkeit','Ertrag steht am ersten Tag fest','nur der Zins von heute ist bekannt'),
            ('Einlagensicherung','100.000 € pro Person und Bank','100.000 € pro Person und Bank'),
            ('Steuer','Abgeltungsteuer, bei deutschen Banken automatisch, Freistellungsauftrag möglich','Abgeltungsteuer, bei deutschen Banken automatisch, Freistellungsauftrag möglich')])+
        f'<div class="prose"><p>Die Zinsen stammen aus dem <a href="{F}">Festgeld-Vergleich</a> mit Stand {stand}. Für jede Laufzeit gibt es eine eigene Seite, etwa <a href="{F1}">Festgeld für 1 Jahr</a>.</p></div>'),
       ('Wann Festgeld die bessere Wahl ist',f'''<div class="prose"><p>Festgeld passt, wenn du das Geld in der Laufzeit sicher nicht brauchst und dir den Zins von heute sichern willst:</p><ul>
<li><b>Du rechnest mit sinkenden Zinsen.</b> Tagesgeld-Zinsen folgen den Leitzinsen der EZB nach unten, meist innerhalb weniger Wochen. Beim Festgeld bleibt dein Satz stehen. Umgekehrt verpasst du steigende Zinsen.</li>
<li><b>Du sparst auf ein Datum.</b> Autokauf in zwei Jahren, Eigenkapital fürs Haus in vier Jahren: Dann weißt du, wie lange das Geld weg sein darf, und wählst genau diese Laufzeit.</li>
<li><b>Du willst keine Zins-Hopping-Arbeit.</b> Wer beim Tagesgeld immer den Aktionszins haben will, muss alle paar Monate die Bank wechseln. Beim Festgeld ist das Thema für die Laufzeit erledigt.</li></ul>
<p>Längere Laufzeit heißt nicht automatisch mehr Zins. Im Vergleich bringt 1 Jahr bis {_pct(z12)}, 2 Jahre bis {_pct(z24)} und 5 Jahre bis {_pct(z60)}. Schau dir die Laufzeiten nebeneinander an, bevor du dich bindest.</p></div>'''),
       ('Wann Tagesgeld besser ist','''<div class="prose"><p>Tagesgeld ist für alles da, was du kurzfristig brauchen könntest:</p><ul>
<li><b>Notgroschen.</b> Drei Monatsausgaben sollten jederzeit greifbar sein, für Reparaturen, Nachzahlungen oder eine Zeit ohne Einkommen. Dieses Geld gehört nie ins Festgeld.</li>
<li><b>Geld ohne klaren Zweck.</b> Weißt du nicht, ob du in einem halben Jahr eine größere Anschaffung machst, bleibt das Geld besser flexibel. Ein vorzeitig aufgelöstes Festgeld kostet fast immer den Zins.</li>
<li><b>Parkposition.</b> Wer in Etappen in ETFs investiert, parkt den Rest auf dem Tagesgeld.</li></ul>
<p>Lies beim Tagesgeld die Zinsgarantie genau. Viele Banken garantieren den Aktionszins nur für 3, 4 oder 6 Monate und nur für Neukunden oder neues Geld. Danach gilt der Basiszins, und der liegt oft bei der Hälfte oder weniger.</p></div>'''),
       ('Die Kombination: Notgroschen flexibel, Rest fest',f'''<div class="prose"><ol>
<li><b>Notgroschen aufs Tagesgeld.</b> Drei Monatsausgaben, bei unsicherem Einkommen oder Selbstständigkeit mehr. Der Zins ist hier zweitrangig, die Verfügbarkeit zählt.</li>
<li><b>Geld mit Datum ins Festgeld.</b> Alles, was du in einem bekannten Zeitraum nicht brauchst. Die Laufzeit folgt dem Zeitpunkt, an dem du das Geld brauchst, nicht dem höchsten Zins.</li>
<li><b>Größere Beträge staffeln.</b> Teile den Betrag auf 1, 2 und 3 Jahre auf. So wird jedes Jahr ein Teil frei, und du legst ihn zu den dann gültigen Zinsen neu an. Das ist die <a href="../zinstreppe/">Zinstreppe</a>.</li></ol>
<p>Rechne vorher nach: Der <a href="{RZ}">Zinseszinsrechner</a> zeigt, was aus einem Betrag über mehrere Jahre wird, der <a href="{RK}">Abgeltungsteuer-Rechner</a>, was nach Steuer und Sparer-Pauschbetrag übrig bleibt. Beachte, dass die meisten Banken die Zinsen jährlich auszahlen, ohne Zinseszins. Im Vergleich sehen nur {len(zz)} von {n} Angeboten einen Zinseszins vor.</p></div>'''),
       ('Worauf du beim Festgeld noch achten solltest',f'''<div class="prose"><ul>
<li><b>Einlagensicherung.</b> {len(heim)} der {n} Angebote im Vergleich stammen von Banken mit Sitz in Deutschland, {len(auslan)} von Banken in anderen EU-Ländern. Die Grenze von 100.000 € gilt überall, zuständig ist aber die Sicherung des Sitzlandes. Mehr im Beitrag zur <a href="../einlagensicherung/">Einlagensicherung</a>.</li>
<li><b>Steuer.</b> Bei {len(auto)} Angeboten führt die Bank die Abgeltungsteuer automatisch ab und berücksichtigt deinen Freistellungsauftrag, bei {len(manuell)} musst du die Zinsen in der Anlage KAP angeben. Mehr im Beitrag <a href="../festgeld-steuern/">Festgeld und Steuern</a>.</li>
<li><b>Kündigung.</b> Nur {len(kuend)} der {n} Angebote lassen sich vorzeitig auflösen, meist mit Abschlag. Details im Beitrag <a href="../festgeld-kuendigen/">Festgeld kündigen</a>.</li>
<li><b>Laufzeitende.</b> {len(verl["automatisch"])} Angebote verlängern sich automatisch, wenn du nichts tust. Trag dir das Ende der Laufzeit ein.</li></ul>
<p>Wie wir die Angebote sortieren und bewerten, steht in der <a href="{FM}">Methodik</a>.</p></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Zinsen, Mindestanlage, Kündigung, Verlängerung und Steuerabwicklung: Konditionsseiten und Produktinformationsblätter der Banken und Plattformen, verlinkt auf jeder Angebotsseite im <a href="{F}">Festgeld-Vergleich</a>, Stand {stand}.</li>
<li>Einlagensicherung: {_ext(BAFIN_ES,"BaFin, Einlagensicherung")}, abgerufen am {ABGERUFEN}.</li>
<li>Sparer-Pauschbetrag: {_ext(ESTG("20"),"§ 20 Abs. 9 EStG")}, abgerufen am {ABGERUFEN}.</li></ul></div>'''),
      ],
      faq=[
       ('Was ist der Unterschied zwischen Festgeld und Tagesgeld?','Festgeld hat eine feste Laufzeit und einen garantierten Zins. Tagesgeld ist täglich verfügbar, der Zins kann sich aber jederzeit ändern. Beide sind bis 100.000 € pro Person und Bank gesetzlich gesichert.'),
       ('Bringt Festgeld mehr Zinsen als Tagesgeld?',f'Über die ganze Laufzeit meist ja, weil Tagesgeld-Aktionszinsen nach wenigen Monaten auslaufen. Im Vergleich liegt der beste Festgeld-Zins für 1 Jahr bei {_pct(z12)}, für 5 Jahre bei {_pct(z60)}, Stand {stand}.'),
       ('Wie viel Geld gehört aufs Tagesgeld?','Als Notgroschen etwa drei Monatsausgaben, bei Selbstständigen mehr. Alles darüber, was du in einem bekannten Zeitraum nicht brauchst, kann ins Festgeld.'),
       ('Komme ich beim Festgeld im Notfall an mein Geld?',f'Bei {len(nokuend)} der {n} Angebote im Vergleich nicht. Bei den übrigen ist eine vorzeitige Auflösung möglich, aber mit Zinsverlust oder Gebühr. Unsicheres Geld gehört aufs Tagesgeld.'),
       ('Welche Laufzeit ist sinnvoll?','Die, die zum Zeitpunkt passt, an dem du das Geld brauchst. Bei größeren Beträgen hilft eine Zinstreppe mit 1, 2 und 3 Jahren, dann wird jedes Jahr ein Teil frei.'),
      ],
      related=['zinstreppe','einlagensicherung','festgeld-kuendigen'])

    # ---------- 2. Einlagensicherung ----------
    lrow=[]
    for cc in laender:
        l=L.get(cc) or {}; k=[a for a in xs if a['sitz']==cc]
        r=l.get('rating_sp') or '–'; r='kein Rating' if r=='NR' else r
        lrow.append((E(l.get('name') or cc),len(k),E(l.get('sicherung') or '–'),_sich(L,cc),E(r)))
    art('de','einlagensicherung',
      h1='Einlagensicherung in Deutschland und der EU: Was wirklich geschützt ist',
      mt='Einlagensicherung Deutschland: 100.000 € erklärt | Finvallo',
      desc=f'Einlagensicherung in Deutschland: 100.000 € pro Person und Bank, Auszahlung in 7 Arbeitstagen, EdB, Sparkassen, Genossenschaftsbanken und freiwilliger Fonds. Was bei Banken aus {len(laender)-1} EU-Ländern gilt.',
      about='Festgeld in Deutschland',
      lede='Geht eine Bank pleite, ersetzt die Einlagensicherung dein Guthaben bis 100.000 €. Die Regel ist EU-weit gleich, die Systeme dahinter unterscheiden sich.',
      kurz=(f'In jedem EU-Land sind Einlagen bis 100.000 € pro Person und Bank gesetzlich gesichert, Zinsen eingeschlossen. Die Auszahlung erfolgt innerhalb von 7 Arbeitstagen ohne Antrag. Bei einem Gemeinschaftskonto gilt die Grenze je Inhaber, zu zweit also 200.000 €. '
            f'In Deutschland sichert für private Banken die Entschädigungseinrichtung deutscher Banken (EdB), für Sparkassen und Genossenschaftsbanken deren Institutssicherung. Viele private Banken sichern über den freiwilligen Fonds des Bankenverbands zusätzlich. '
            f'Bei Banken aus dem EU-Ausland zahlt die Sicherung des Sitzlandes, im Vergleich betrifft das {len(auslan)} von {n} Angeboten.'),
      secs=[
       ('So funktioniert die gesetzliche Einlagensicherung','''<div class="prose"><p>Jede Bank in der EU, die Einlagen annimmt, muss einem anerkannten Einlagensicherungssystem angehören. Die Banken zahlen Beiträge in einen Fonds. Kann eine Bank Einlagen nicht mehr auszahlen, stellt die Aufsicht den Entschädigungsfall fest, in Deutschland die BaFin. Dann zahlt die Sicherungseinrichtung. Grundlage ist die EU-Richtlinie über Einlagensicherungssysteme, in Deutschland umgesetzt im Einlagensicherungsgesetz (EinSiG).</p>
<p>Die wichtigsten Regeln laut BaFin:</p><ul>
<li><b>100.000 € pro Kunde und Bank</b>, unabhängig von der Zahl der Konten. Girokonto, Tagesgeld und Festgeld bei derselben Bank werden zusammengerechnet.</li>
<li><b>Pro Bank mit eigener Lizenz.</b> Marken ohne eigene Banklizenz zählen zur Mutterbank. Zwei Banken, zweimal 100.000 €.</li>
<li><b>Auszahlung innerhalb von 7 Arbeitstagen</b>, ohne Antrag und ohne Nachweis.</li>
<li><b>Gemeinschaftskonto:</b> Jeder Inhaber hat einen eigenen Anspruch, bei zwei Inhabern also bis 200.000 €.</li>
<li><b>Bis 500.000 € für 6 Monate</b> nach Gutschrift bei besonderen Beträgen: Erlös aus dem Verkauf einer selbst genutzten Wohnimmobilie, Zahlungen zu Heirat, Scheidung, Renteneintritt oder Krankheit, bestimmte Versicherungsleistungen. Dafür musst du den Anspruch schriftlich mit Nachweisen geltend machen (§ 8 EinSiG).</li>
<li><b>Geschützt sind</b> Einlagen in Euro, in anderen EU-Währungen und in Fremdwährungen wie US-Dollar oder Franken. Wertpapiere im Depot gehören dir ohnehin und fallen nicht unter die Einlagensicherung.</li></ul></div>'''),
       ('Wer in Deutschland sichert',f'''<div class="prose"><p>Deutschland hat mehrere anerkannte Systeme, je nach Bankengruppe:</p><ul>
<li><b>Entschädigungseinrichtung deutscher Banken GmbH (EdB)</b> für private Banken, von der Großbank bis zur Autobank. Sie ist die gesetzliche Sicherung für die meisten Banken im Vergleich.</li>
<li><b>Sicherungssystem der Sparkassen-Finanzgruppe</b> für Sparkassen, Landesbanken und Landesbausparkassen. Das ist eine Institutssicherung: Der Haftungsverbund soll ein Mitglied schon vor der Pleite stützen, und er ist zugleich als gesetzliche Einlagensicherung anerkannt. Im Vergleich betrifft das {len(spk)} Angebot{"e" if len(spk)!=1 else ""}.</li>
<li><b>BVR Institutssicherung GmbH</b> für Volksbanken, Raiffeisenbanken, Sparda- und PSD-Banken, ebenfalls eine anerkannte Institutssicherung. Im Vergleich sind es {len(bvr)} Angebote.</li></ul>
<p>Dazu kommt die <b>freiwillige Sicherung</b>: Der Einlagensicherungsfonds des Bundesverbands deutscher Banken (BdB) schützt bei seinen Mitgliedsbanken Einlagen über 100.000 € hinaus. Die Sicherungsgrenze liegt seit 2025 bei höchstens 3 Millionen € je Privatperson und sinkt 2030 auf 1 Million €, je nach Eigenkapital der Bank auch deutlich darunter. Einen Rechtsanspruch gibt es darauf nicht, so die BaFin. Im Vergleich nennen {len(bdb)} Angebote diese Zusatzsicherung. Verbindlich bleiben nur die gesetzlichen 100.000 €.</p>
<p>Welches System für ein Angebot gilt, steht im „Informationsbogen für den Einleger“, den jede Bank vor dem Abschluss aushändigen muss, und im <a href="{F}">Festgeld-Vergleich</a> auf jeder Angebotsseite. Die {len(heim)} Angebote von Banken mit Sitz in Deutschland stehen gesammelt in der Liste <a href="{FH}">deutsche Banken</a>.</p></div>'''),
       ('Banken aus anderen EU-Ländern: Heimatlandprinzip',f'''<div class="prose"><p>Legst du bei einer Bank mit Sitz in Frankreich, Italien oder Schweden an, gilt auch dort die Grenze von 100.000 €, zuständig ist aber die Einlagensicherung des Landes, in dem die Bank ihre Lizenz hat. Das Heimatlandprinzip gilt auch, wenn die Bank in Deutschland eine Zweigniederlassung betreibt. Im Vergleich sind das {len(zweig)} Angebote, zum Beispiel {", ".join(L_(a) for a in zweig[:4])}. Eine deutsche Adresse, eine deutsche IBAN oder ein deutscher Kundenservice ändern daran nichts.</p>
<p>Bei Zweigniederlassungen hilft im Entschädigungsfall die EdB bei der Abwicklung, das Geld kommt aber aus dem Fonds des Sitzlandes. Die Frist von 7 Arbeitstagen gilt EU-weit. In der Praxis kann die Kommunikation in der Landessprache oder auf Englisch laufen, und die Fonds sind unterschiedlich gefüllt.</p></div>'''),
       ('Was ein Länderrating aussagt, und was nicht',_tbl(['Sitzland','Angebote im Vergleich','Sicherungseinrichtung','Gesichert','S&amp;P-Rating'],lrow)+
        f'''<div class="prose"><p>Die Sicherungsfonds sind für einzelne Pleiten ausgelegt, nicht für eine Krise des ganzen Bankensystems. Reicht der Fonds nicht, muss der Staat einspringen. Deshalb zeigen wir das langfristige Länderrating von S&amp;P Global für das Sitzland als Hinweis darauf, wie gut ein Staat im Ernstfall nachschießen könnte.</p>
<p>Über die einzelne Bank sagt das Rating nichts. Eine Bank in einem AAA-Land kann scheitern, eine Bank in einem BBB-Land solide sein, und die Einlagensicherung greift in beiden Fällen bis 100.000 €. Das Rating ist kein Grund, ein Angebot auszuschließen, aber ein Grund, große Beträge auf mehrere Banken und Länder zu verteilen. Ratings vom {_dmy(max((v.get("rating_stand") or "") for v in L.values()))}, Details in der <a href="{FM}">Methodik</a>.</p></div>'''),
       ('Beispiel Fremdwährung: Sicherung in schwedischen Kronen',f'''<div class="prose"><p>Länder ohne Euro sichern den Gegenwert von 100.000 € in ihrer Währung und rechnen ihn nur alle fünf Jahre neu um. Schweden hat die Grenze zum 1. Januar 2026 auf {eur(sek)} SEK pro Person und Bank angehoben, nach dem Wechselkurs vom 3. Juli 2025. Schwankt der Kurs danach, ist dein Euro-Guthaben etwas mehr oder etwas weniger als 100.000 € wert.</p>
<p>Das betrifft im Vergleich {len(se)} Angebote von Banken mit Sitz in Schweden, ob direkt wie bei {", ".join(L_(a) for a in se if a["vertrieb"]=="direkt")[:200] or "TF Bank"} oder über Raisin und CHECK24. Die Plattformen begrenzen die Anlage bei solchen Banken auf 100.000 €. Wer auf Nummer sicher gehen will, bleibt etwas darunter, etwa bei 95.000 €, damit Zinsen und ein schwächerer Kronenkurs noch Platz haben.</p>
<p>Umgekehrt gilt: Ein Festgeld in Dollar oder Pfund bei einer EU-Bank ist ebenfalls gesichert. Ausgezahlt wird aber in Euro oder der Landeswährung des Sitzlandes, das Währungsrisiko bleibt bei dir.</p></div>'''),
       ('Nicht verwechseln: Anlegerentschädigung','''<div class="prose"><p>Neben der Einlagensicherung gibt es die Anlegerentschädigung. Sie greift, wenn eine Bank oder ein Wertpapierhandelsunternehmen Wertpapiere oder Gelder aus Wertpapiergeschäften nicht zurückgeben kann, etwa bei Betrug. Sie ersetzt 90 % der Forderung, höchstens 20.000 €. Mit Festgeld hat sie nichts zu tun: Einlagen fallen immer unter die Einlagensicherung mit 100.000 €.</p></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Grenze, Frist, Gemeinschaftskonten, Sonderfälle bis 500.000 €, Fremdwährung, Systeme, freiwillige Fonds ohne Rechtsanspruch: {_ext(BAFIN_ES,"BaFin, Einlagensicherung")}, abgerufen am {ABGERUFEN}; Gesetz: {_ext(EINSIG8,"§ 8 EinSiG")}.</li>
<li>Entschädigungseinrichtung: {_ext(EDB,"Entschädigungseinrichtung deutscher Banken")}; freiwillige Sicherung: {_ext(BDB_FONDS,"Einlagensicherungsfonds des Bundesverbands deutscher Banken")}, abgerufen am {ABGERUFEN}.</li>
<li>Schweden: {_ext(RIKS,"Riksgälden, Pressemitteilung vom 30.10.2025 zur Anpassung auf 1.150.000 SEK")}.</li>
<li>Sicherungseinrichtung und Länderrating je Angebot: Informationsbögen der Banken und tradingeconomics.com, verlinkt im <a href="{F}">Festgeld-Vergleich</a>.</li></ul></div>'''),
      ],
      faq=[
       ('Wie viel Geld ist bei einer Bankpleite geschützt?','100.000 € pro Kunde und Bank, inklusive Zinsen. Bei Gemeinschaftskonten gilt die Grenze je Inhaber. In Sonderfällen, etwa nach einem Hausverkauf, sind sechs Monate lang bis 500.000 € geschützt.'),
       ('Wie schnell zahlt die Einlagensicherung?','Innerhalb von 7 Arbeitstagen, nachdem die BaFin den Entschädigungsfall festgestellt hat. Für Beträge bis 100.000 € musst du keinen Antrag stellen.'),
       ('Gilt die Einlagensicherung auch bei Festgeld über Raisin oder CHECK24?','Ja. Das Geld liegt bei der Partnerbank und ist über die Sicherung ihres Sitzlandes bis 100.000 € geschützt. Die Verrechnungskonten bei der Raisin Bank und der C24 Bank fallen unter die deutsche Einlagensicherung.'),
       ('Was bringt der freiwillige Einlagensicherungsfonds?','Bei Mitgliedsbanken des Bankenverbands sichert er Beträge über 100.000 € hinaus, seit 2025 bis höchstens 3 Millionen € je Privatperson. Einen Rechtsanspruch gibt es nicht. Verbindlich sind nur die gesetzlichen 100.000 €.'),
       ('Ist eine Bank in Italien oder Lettland unsicherer als eine deutsche?','Die gesetzliche Grenze ist dieselbe. Ob ein Land seinen Fonds im Ernstfall stützen kann, zeigt das Länderrating als groben Hinweis, über die einzelne Bank sagt es nichts. Bei großen Beträgen auf mehrere Banken verteilen.'),
      ],
      related=['festgeld-plattformen','festgeld-oder-tagesgeld','festgeld-steuern'])

    # ---------- 3. Zinstreppe ----------
    T=30000; S=T/3
    st=[(1,z12,a12),(2,z24,a24),(3,z36,a36)]
    zrow=[(f'Stufe {i}',f'{eur(S)} €',f'{j} Jahr{"e" if j>1 else ""}',_pct(z),L_(a),f'{eur(round(S*z/100*j,2))} €') for i,(j,z,a) in enumerate(st,1)]
    ztot=sum(S*z/100*j for j,z,_ in st)
    all3=T*z36/100*3; all1=T*z12/100
    zrow.append(('Gesamt',f'{eur(T)} €','1 bis 3 Jahre','','',f'{eur(round(ztot,2))} €'))
    art('de','zinstreppe',
      h1='Zinstreppe: Festgeld auf mehrere Laufzeiten verteilen',
      mt='Zinstreppe: Festgeld-Leiter in Deutschland | Finvallo',
      desc=f'Zinstreppe in Deutschland erklärt: 30.000 € auf drei Laufzeiten verteilt, durchgerechnet mit aktuellen Zinsen bis {_pct(z36)}. Vorteile, Nachteile und wann sich die Festgeld-Leiter lohnt.',
      about='Festgeld in Deutschland',
      lede='Alles auf fünf Jahre, und dann steigen die Zinsen? Alles auf ein Jahr, und dann fallen sie? Die Zinstreppe erspart dir diese Wette.',
      kurz=(f'Bei einer Zinstreppe verteilst du den Betrag auf mehrere Festgelder mit gestaffelten Laufzeiten, etwa je ein Drittel auf 1, 2 und 3 Jahre. Jedes Jahr wird eine Stufe fällig, die du zum dann gültigen Zins auf die längste Laufzeit neu anlegst. '
            f'Mit den besten Zinsen aus dem Vergleich bringen 30.000 € auf drei Stufen in drei Jahren {eur(round(ztot))} € Zinsen vor Steuer, alles auf 3 Jahre {eur(round(all3))} €. Dafür kommst du jedes Jahr an ein Drittel heran und bleibst bei steigenden Zinsen beweglich.'),
      secs=[
       ('Das Prinzip','''<div class="prose"><p>Festgeld zwingt dich zu einer Entscheidung über die Laufzeit, ohne dass du weißt, wohin die Zinsen gehen. Lang gebunden verpasst du steigende Zinsen, kurz gebunden musst du bei fallenden Zinsen schlechter neu anlegen.</p>
<p>Die Zinstreppe, auch Festgeld-Leiter oder Laddering genannt, löst das. Du teilst den Betrag in gleich große Stufen und gibst jeder Stufe eine andere Laufzeit: 1 Jahr, 2 Jahre, 3 Jahre. Nach einem Jahr wird die erste Stufe fällig. Du legst sie auf 3 Jahre neu an, weil die beiden anderen Stufen dann noch 1 und 2 Jahre laufen. Ab dem dritten Jahr hat jede Stufe die lange Laufzeit mit dem langen Zins, und trotzdem wird jedes Jahr ein Drittel frei.</p></div>'''),
       ('Rechenbeispiel: 30.000 € auf drei Stufen',_tbl(['Stufe','Betrag','Laufzeit','Zins','Bestes Angebot im Vergleich','Zinsen bis Ende der Laufzeit'],zrow)+
        f'''<div class="prose"><p>Gerechnet mit den besten Zinsen je Laufzeit aus dem <a href="{F}">Festgeld-Vergleich</a>, Stand {stand}, vor Steuer und ohne Zinseszins, weil die meisten Banken die Zinsen jährlich auszahlen. Zum Vergleich: {eur(T)} € komplett auf 3 Jahre zu {_pct(z36)} bringen {eur(round(all3))} €, komplett auf 1 Jahr zu {_pct(z12)} nur {eur(round(all1))} €, danach musst du neu anlegen.</p>
<p>Die Treppe bleibt also hinter der reinen 3-Jahres-Anlage zurück, solange kurze Laufzeiten niedriger verzinst sind. Dafür hast du nach 12 Monaten {eur(S)} € in der Hand und kannst reagieren, wenn die Zinsen gestiegen sind. Liegt der Zins für 1 Jahr über dem für 3 Jahre, dreht sich das Bild.</p>
<p>Die Angebote in der Tabelle kommen von verschiedenen Banken. Das ist kein Nachteil: Bei {eur(T)} € bleibst du ohnehin weit unter der Grenze der Einlagensicherung, bei größeren Beträgen hilft die Verteilung, unter 100.000 € pro Bank zu bleiben. Beachte den Sparer-Pauschbetrag: Mit Freistellungsaufträgen bei mehreren Banken teilst du die 1.000 € auf. Was nach Steuer bleibt, rechnet der <a href="{RK}">Abgeltungsteuer-Rechner</a>.</p></div>'''),
       ('Vorteile der Zinstreppe','''<div class="prose"><ul class="checks">
<li><b>Jedes Jahr Geld verfügbar.</b> Du musst nie ein Festgeld vorzeitig auflösen, weil regelmäßig eine Stufe fällig wird.</li>
<li><b>Keine Zinswette.</b> Jedes Jahr legst du ein Drittel zum aktuellen Zins an. Steigen die Zinsen, bist du schrittweise dabei. Fallen sie, laufen zwei Drittel noch zum alten Satz.</li>
<li><b>Auf Dauer der lange Zins.</b> Nach der Anlaufphase läuft jede Stufe 3 Jahre und bekommt den 3-Jahres-Zins, und die Treppe bleibt trotzdem beweglich.</li>
<li><b>Einlagensicherung einfach einhalten.</b> Wer die Stufen bei verschiedenen Banken anlegt, bleibt automatisch unter 100.000 € pro Bank.</li></ul></div>'''),
       ('Nachteile und Grenzen',f'''<div class="prose"><ul>
<li><b>Mehr Verwaltung.</b> Drei Verträge statt einem, jedes Jahr eine Entscheidung, bei mehreren Banken mehrere Logins und mehrere Freistellungsaufträge. Plattformen wie Raisin, CHECK24 oder der ZinsMarkt bündeln das unter einem Konto. Mehr dazu im Beitrag zu den <a href="../festgeld-plattformen/">Festgeld-Plattformen</a>.</li>
<li><b>Mindestanlage.</b> Viele Angebote verlangen 5.000 € oder 10.000 €. Mit 9.000 € Gesamtbetrag wird es bei drei Stufen eng. Im Vergleich liegt die Mindestanlage je nach Angebot zwischen {eur(mins[0])} € und {eur(mins[-1])} €.</li>
<li><b>Automatische Verlängerung.</b> {len(verl["automatisch"])} der {n} Angebote verlängern sich von selbst, wenn du am Laufzeitende nichts tust, womöglich zu einem schlechteren Zins. Trag dir jede Fälligkeit ein.</li>
<li><b>Weniger Zins in der Anlaufphase.</b> Solange kurze Laufzeiten niedriger verzinst sind, bringt die Treppe in den ersten Jahren weniger als die lange Anlage, siehe Rechenbeispiel.</li></ul></div>'''),
       ('Wann sich die Zinstreppe lohnt',f'''<div class="prose"><p>Die Treppe lohnt sich, wenn du ab etwa 15.000 € für mehrere Jahre anlegen willst, aber nicht sicher bist, ob du zwischendurch etwas brauchst, und wenn du keine Meinung dazu hast, wohin die Zinsen gehen. Sie ist das Gegenteil von Markt-Timing.</p>
<p>Sie lohnt sich nicht, wenn du das Geld zu einem festen Termin brauchst, etwa als Eigenkapital in drei Jahren. Dann nimmst du genau diese Laufzeit. Und sie lohnt sich nicht für den Notgroschen, der gehört aufs Tagesgeld, siehe <a href="../festgeld-oder-tagesgeld/">Festgeld oder Tagesgeld</a>.</p>
<p>Varianten: Wer länger planen kann, baut die Treppe mit 1 bis 5 Jahren in fünf Stufen. Für 5 Jahre gibt es im Vergleich {_n(xs,60)} Angebote, bis {_pct(z60)} bei {L_(a60)}. Wer es einfacher will, nimmt zwei Stufen mit 1 und 2 Jahren. Die Seiten <a href="{F1}">1 Jahr</a>, <a href="{F}2-jahre/">2 Jahre</a> und <a href="{F}3-jahre/">3 Jahre</a> zeigen die Angebote je Stufe.</p></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Zinsen und Mindestanlage: Konditionsseiten der Banken und Plattformen, verlinkt auf jeder Angebotsseite im <a href="{F}">Festgeld-Vergleich</a>, Stand {stand}. Die Beispielrechnung übernimmt beim Bauen dieser Seite den jeweils besten Zins je Laufzeit.</li>
<li>Einlagensicherung: {_ext(BAFIN_ES,"BaFin, Einlagensicherung")}; Sparer-Pauschbetrag: {_ext(ESTG("20"),"§ 20 Abs. 9 EStG")}, abgerufen am {ABGERUFEN}.</li></ul></div>'''),
      ],
      faq=[
       ('Was ist eine Zinstreppe?','Die Aufteilung eines Anlagebetrags auf mehrere Festgelder mit gestaffelten Laufzeiten, etwa 1, 2 und 3 Jahre. Jede fällige Stufe wird auf die längste Laufzeit neu angelegt. So ist jedes Jahr ein Teil verfügbar.'),
       ('Bringt die Zinstreppe mehr Zinsen als ein einzelnes Festgeld?',f'In der Anlaufphase meist weniger als die lange Laufzeit, solange kurze Laufzeiten niedriger verzinst sind. Im Beispiel mit 30.000 € sind es {eur(round(ztot))} € statt {eur(round(all3))} € in drei Jahren. Dafür bleibst du flexibel und profitierst von steigenden Zinsen.'),
       ('Wie viele Stufen sind sinnvoll?','Drei Stufen mit 1, 2 und 3 Jahren sind der Standard. Mit mehr Geld und Geduld gehen fünf Stufen bis 5 Jahre. Jede Stufe muss die Mindestanlage der Bank erreichen.'),
       ('Muss ich alle Stufen bei derselben Bank anlegen?','Nein. Für jede Laufzeit liegt oft eine andere Bank vorne. Bei mehr als 100.000 € ist die Verteilung auf mehrere Banken wegen der Einlagensicherung sogar nötig. Denk an den Freistellungsauftrag für jede Bank.'),
       ('Was passiert, wenn eine Stufe fällig wird und ich nichts tue?',f'Je nach Angebot wird ausgezahlt oder automatisch verlängert. Im Vergleich verlängern sich {len(verl["automatisch"])} von {n} Angeboten von selbst, zum dann gültigen Zins. Details im Beitrag „Festgeld kündigen“.'),
      ],
      related=['festgeld-oder-tagesgeld','festgeld-kuendigen','festgeld-plattformen'])

    # ---------- 4. Festgeld kündigen ----------
    krow=[(L_(a),E(a['kuendigung_text'] or 'keine Angabe')) for a in sorted(kuend,key=lambda a:(a['vertrieb']!='direkt',a['bank'].lower()))]
    vrow=[('Keine Verlängerung',len(verl['keine']),'Das Geld kommt am Laufzeitende aufs Verrechnungs- oder Referenzkonto. Du musst nichts tun.'),
          ('Verlängerung wählbar',len(verl['wahlweise']),'Du entscheidest vor dem Ende, ob das Festgeld weiterläuft. Ohne Entscheidung wird meist ausgezahlt, prüfe die Voreinstellung.'),
          ('Automatische Verlängerung',len(verl['automatisch']),'Ohne Weisung läuft das Festgeld mit derselben Laufzeit zum dann gültigen Zins weiter. Du musst rechtzeitig vorher auszahlen lassen.')]
    teil=[a for a in kuend if a['kuendigung']=='ja']
    art('de','festgeld-kuendigen',
      h1='Festgeld kündigen: Geht das vorzeitig, und was kostet es?',
      mt='Festgeld kündigen in Deutschland: Geht das? | Finvallo',
      desc=f'Festgeld vorzeitig kündigen in Deutschland: Bei {len(nokuend)} von {n} Angeboten ausgeschlossen, sonst mit Zinsverlust oder Gebühr. Flexgeld, Todesfall, Widerruf, automatische Verlängerung und Fristen.',
      about='Festgeld in Deutschland',
      lede='Festgeld heißt fest. Es gibt Ausnahmen, aber sie kosten. Und am Laufzeitende wartet die zweite Falle: die automatische Verlängerung.',
      kurz=(f'Ein Festgeld kannst du im Normalfall nicht vorzeitig kündigen. Im Vergleich schließen {len(nokuend)} von {n} Angeboten das aus. {len(kuend)} Angebote erlauben eine vorzeitige Auflösung, meist mit Abschlag: '
            f'der Zins fällt rückwirkend auf 0 % oder 0,01 %, oder es gibt eine Gebühr. Nach dem Online-Abschluss hast du 14 Tage Widerrufsrecht. '
            f'Am Laufzeitende verlängern sich {len(verl["automatisch"])} Angebote automatisch, wenn du nicht rechtzeitig auszahlen lässt.'),
      secs=[
       ('Warum Festgeld nicht kündbar ist','''<div class="prose"><p>Mit dem Festgeld vereinbarst du eine Laufzeit und einen festen Zins. Die Bank refinanziert damit Kredite mit ähnlicher Laufzeit. Deshalb schließt der Vertrag die ordentliche Kündigung aus. Du kommst erst am Laufzeitende an das Geld, auch wenn du es vorher dringend brauchst. Das ist der Preis für den garantierten Zins.</p>
<p>Zwei Rechte bleiben dir trotzdem:</p><ul>
<li><b>Widerruf.</b> Schließt du online, per App oder per Post ab, kannst du den Vertrag innerhalb von 14 Tagen widerrufen, ohne Angabe von Gründen (§ 312g BGB, Fernabsatz). Die Frist beginnt, sobald du die Widerrufsbelehrung erhalten hast. Die Plattformen nennen die Frist in ihren Bedingungen.</li>
<li><b>Außerordentliche Kündigung aus wichtigem Grund</b> (§ 314 BGB). Sie greift nur, wenn dir das Festhalten am Vertrag nicht zumutbar ist, etwa bei schweren Pflichtverletzungen der Bank. Eigener Geldbedarf ist kein wichtiger Grund. Manche Banken regeln in ihren Bedingungen, was dann gilt, etwa ein Zins von 0,01 % für die bisherige Laufzeit.</li></ul></div>'''),
       ('Wo eine vorzeitige Auflösung möglich ist',_tbl(['Angebot','Regel bei vorzeitiger Auflösung'],krow)+
        f'''<div class="prose"><p>Stand {stand}, laut Konditionen und Produktinformationsblättern der Anbieter. Drei Muster:</p><ul>
<li><b>Zins rückwirkend auf 0 % oder 0,01 %.</b> Die Bank zahlt den Anlagebetrag aus, nimmt dir aber die Zinsen für die ganze Zeit. Bereits gezahlte Zinsen werden verrechnet. Praktisch bekommst du den Einsatz zurück, sonst nichts.</li>
<li><b>Gebühr oder Vorschusszinsen.</b> Einige Banken verlangen einen festen Betrag, etwa 60 €, oder einen Prozentsatz der Anlage je Jahr Restlaufzeit, oder berechnen Vorschusszinsen auf den vorzeitig ausgezahlten Betrag.</li>
<li><b>Teilweise verfügbar.</b> {len(teil)} Angebote erlauben die Verfügung ohne Abschlag, aber nur über einen Teil des Betrags oder erst nach einer Mindestlaufzeit.</li></ul>
<p>Dazu kommt das <b>Flexgeld</b>: ein Festgeld, das du jederzeit kündigen kannst. Dann gilt für die gesamte Anlagezeit ein niedrigerer Zins, bei manchen Banken 0 %, und die Auszahlung dauert einige Wochen. Im Vergleich gibt es {len(flex)} Flexgeld-Angebote über Raisin, dazu ähnliche Varianten über CHECK24. Flexgeld ist eine Versicherung gegen Geldbedarf, die du mit dem niedrigeren Zins bezahlst.</p></div>'''),
       ('Sonderfälle: Todesfall, Härtefall, Insolvenz der Bank','''<div class="prose"><p><b>Todesfall.</b> Stirbt die Kontoinhaberin oder der Kontoinhaber, geht das Festgeld auf die Erben über. Sie weisen sich mit Erbschein, notariellem Testament mit Eröffnungsprotokoll oder einer über den Tod hinaus gültigen Vollmacht aus. Viele Banken lösen das Festgeld dann auf Wunsch ohne Abschlag auf, andere lassen es bis zum Laufzeitende weiterlaufen. Einen gesetzlichen Anspruch auf vorzeitige Auszahlung gibt es nicht, prüfe die Bedingungen der Bank.</p>
<p><b>Härtefall.</b> Arbeitslosigkeit, Krankheit oder Scheidung sind rechtlich kein Kündigungsgrund. Manche Banken lösen aus Kulanz auf, meist gegen Zinsverlust. Wer solche Risiken sieht, hält mehr auf dem Tagesgeld oder wählt kürzere Laufzeiten.</p>
<p><b>Insolvenz der Bank.</b> Dann endet das Festgeld, und die Einlagensicherung zahlt bis 100.000 € pro Person und Bank innerhalb von 7 Arbeitstagen, aufgelaufene Zinsen eingeschlossen. Mehr im Beitrag zur <a href="../einlagensicherung/">Einlagensicherung</a>.</p></div>'''),
       ('Am Laufzeitende: automatische Verlängerung und Fristen',_tbl(['Regel','Angebote im Vergleich','Was das für dich heißt'],vrow)+
        f'''<div class="prose"><p>Die automatische Verlängerung, auch Prolongation genannt, ist die häufigste Falle. Das Geld wird dann für dieselbe Laufzeit zu dem Zins angelegt, der an diesem Tag gilt, und der ist oft niedriger als beim Abschluss. Wer das verhindern will, muss vorher aktiv werden. Die Fristen stehen in den Bedingungen: Bei Raisin schaltest du die Verlängerung bis 2 Tage vor Laufzeitende im Online-Banking ab, bei CHECK24 beantragst du eine Verlängerung bis 3 Bankarbeitstage vor Fälligkeit, Direktbanken verlangen die Auszahlungsweisung je nach Haus 2 Tage bis 3 Monate vorher. Die Frist für jedes Angebot steht auf der Angebotsseite im <a href="{F}">Festgeld-Vergleich</a>.</p>
<p>Bei Angeboten ohne Verlängerung landet das Geld am Ende auf dem Referenz- oder Verrechnungskonto. Dort liegt es oft unverzinst, bis du es neu anlegst. Auch hier hilft ein Kalendereintrag, zwei Wochen vor dem Ende.</p></div>'''),
       ('Vor dem Abschluss prüfen','''<div class="prose"><ul class="checks">
<li>Brauche ich das Geld in der Laufzeit sicher nicht? Der Notgroschen gehört aufs Tagesgeld.</li>
<li>Was steht im Vertrag zur vorzeitigen Auflösung: ausgeschlossen, Zinsverlust, Gebühr?</li>
<li>Was passiert am Laufzeitende: Auszahlung, Wahl oder automatische Verlängerung? Bis wann muss ich mich melden?</li>
<li>Werden die Zinsen jährlich ausgezahlt oder erst am Ende? Bei langen Laufzeiten und für den Sparer-Pauschbetrag macht das einen Unterschied.</li>
<li>Wie erreiche ich die Bank: Online-Banking, App, Brief? Bei Plattformen läuft alles über das Plattform-Konto.</li>
<li>Steht das Laufzeitende im Kalender, mit Erinnerung zwei Wochen vorher?</li></ul></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Kündigungsregeln und Verlängerung je Angebot: Konditionsseiten, Bedingungen und Produktinformationsblätter der Banken und Plattformen, verlinkt auf jeder Angebotsseite im <a href="{F}">Festgeld-Vergleich</a>, Stand {stand}.</li>
<li>Widerruf im Fernabsatz: {_ext(BGB("312g"),"§ 312g BGB")}; Kündigung aus wichtigem Grund: {_ext(BGB("314"),"§ 314 BGB")}, abgerufen am {ABGERUFEN}.</li>
<li>Einlagensicherung im Insolvenzfall: {_ext(BAFIN_ES,"BaFin, Einlagensicherung")}, abgerufen am {ABGERUFEN}.</li></ul></div>'''),
      ],
      faq=[
       ('Kann ich ein Festgeld vorzeitig kündigen?',f'Normalerweise nicht. Im Vergleich schließen {len(nokuend)} von {n} Angeboten eine vorzeitige Auflösung aus. Wo sie möglich ist, verlierst du meist die Zinsen oder zahlst eine Gebühr.'),
       ('Was ist Flexgeld?','Ein Festgeld über eine Plattform, das du jederzeit kündigen kannst. Dann gilt rückwirkend ein niedrigerer Zins, bei manchen Banken 0 %. Hältst du die Laufzeit durch, bekommst du den vollen Zins.'),
       ('Kann ich ein Festgeld nach dem Abschluss widerrufen?','Ja, bei Abschluss online oder per Post innerhalb von 14 Tagen ohne Angabe von Gründen. Danach gilt die Bindung.'),
       ('Was passiert mit dem Festgeld im Todesfall?','Es geht auf die Erben über, die sich mit Erbschein oder Vollmacht ausweisen. Ob die Bank vorzeitig und ohne Abschlag auszahlt, hängt von ihren Bedingungen ab. Einen gesetzlichen Anspruch gibt es nicht.'),
       ('Was ist eine automatische Verlängerung?',f'Ohne deine Weisung legt die Bank das Geld am Laufzeitende für dieselbe Laufzeit zum dann gültigen Zins neu an. Im Vergleich gilt das bei {len(verl["automatisch"])} von {n} Angeboten. Die Frist für den Widerspruch steht auf der Angebotsseite.'),
       ('Kann ich bei Geldnot aus wichtigem Grund kündigen?','Nein. § 314 BGB verlangt, dass dir das Festhalten am Vertrag unzumutbar ist, etwa wegen Pflichtverletzungen der Bank. Eigener Geldbedarf reicht nicht. Manche Banken helfen aus Kulanz, gegen Zinsverlust.'),
      ],
      related=['festgeld-oder-tagesgeld','zinstreppe','festgeld-plattformen'])

    # ---------- 5. Plattformen ----------
    def _cnt(xs_,f): return len([a for a in xs_ if f(a)])
    def _ks(xs_): return f'{_cnt(xs_,lambda a:a["steuer_auto"])} von {len(xs_)}'
    def _kk(xs_): return str(_cnt(xs_,lambda a:a["kuendigung"] in ("ja","ja_mit_abschlag")))
    prow=[('Direkt bei der Bank',len(direkt),_ks(direkt),_kk(direkt),'Konto bei der Bank, Legitimation je Bank neu','je nach Bank, fast immer kostenlos'),
          ('Raisin',len(raisin),_ks(raisin),_kk(raisin),'Raisin-Konto bei der Raisin Bank AG (Frankfurt), einmal VideoIdent oder PostIdent','kostenlos'),
          ('CHECK24',len(c24),_ks(c24),_kk(c24),'CHECK24 Anlagekonto bei der C24 Bank, einmal VideoIdent','kostenlos'),
          ('ZinsMarkt (Deutsche Bank, norisbank)',len(zm),_ks(zm),_kk(zm),'Verrechnungskonto bei der Deutschen Bank oder norisbank, nur Einzelkonto','kostenlos')]
    zr12,ar12=_best(raisin,12); zc12,ac12=_best(c24,12); zd12,ad12=_best(direkt,12); zz12,az12=_best(zm,12)
    art('de','festgeld-plattformen',
      h1='Festgeld-Plattformen: Raisin, CHECK24, ZinsMarkt oder direkt?',
      mt='Festgeld-Plattformen Deutschland: Raisin & Co. | Finvallo',
      desc=f'Festgeld-Plattformen in Deutschland: Wie Raisin, CHECK24 und der ZinsMarkt der Deutschen Bank funktionieren, wo dein Geld liegt, was es kostet und wer die Steuer abführt. {len(raisin)+len(c24)+len(zm)} von {n} Angeboten laufen über Plattformen.',
      about='Festgeld in Deutschland',
      lede='Einmal legitimieren, dann bei Dutzenden Banken anlegen: Das bieten die Plattformen. Der Preis dafür ist bei ausländischen Banken die Steuererklärung.',
      kurz=(f'Über eine Festgeld-Plattform legst du mit einem Konto bei Banken aus ganz Europa an. Im Vergleich laufen {len(raisin)} Angebote über Raisin, {len(c24)} über CHECK24 und {len(zm)} über den ZinsMarkt der Deutschen Bank und norisbank, {len(direkt)} schließt du direkt bei der Bank ab. '
            f'Dein Geld liegt immer bei der Partnerbank, gesichert durch deren Einlagensicherung bis 100.000 €. Kosten fallen keine an. Die Steuer führen deutsche Partnerbanken und der ZinsMarkt automatisch ab, bei ausländischen Partnerbanken über Raisin und CHECK24 musst du die Zinsen in der Anlage KAP angeben.'),
      secs=[
       ('So funktioniert eine Festgeld-Plattform',f'''<div class="prose"><p>Eine Plattform vermittelt Festgelder von Banken, die in Deutschland keine eigene Kundschaft aufbauen wollen, und wickelt die Anlage über ein Verrechnungskonto ab. Der Ablauf ist bei Raisin und CHECK24 ähnlich:</p><ol>
<li><b>Registrieren und legitimieren.</b> Du eröffnest online ein Konto bei der Plattform und bestätigst deine Identität einmal per VideoIdent oder PostIdent. Bei Raisin ist das das Raisin-Konto bei der Raisin Bank AG in Frankfurt, bei CHECK24 das Anlagekonto bei der C24 Bank. Beide sind kostenlos.</li>
<li><b>Angebot wählen.</b> Du suchst ein Festgeld einer Partnerbank aus und gibst den Betrag ein. Für weitere Anlagen bei anderen Partnerbanken brauchst du meist keine neue Legitimation, einzelne Banken verlangen sie trotzdem.</li>
<li><b>Geld überweisen.</b> Du überweist vom Referenzkonto auf das Verrechnungskonto, die Plattform leitet den Betrag an die Partnerbank weiter.</li>
<li><b>Laufzeitende.</b> Die Partnerbank zahlt Kapital und Zinsen auf das Verrechnungskonto. Von dort überweist du es zurück oder legst neu an.</li></ol>
<p>Der <b>ZinsMarkt</b> der Deutschen Bank, auch bei der Tochter norisbank, funktioniert etwas anders. Du brauchst ein Konto bei der Deutschen Bank oder norisbank, ein Einzelkonto mit Online-Banking. Die Bank legt das Festgeld entweder treuhänderisch im eigenen Namen auf deine Rechnung bei der Partnerbank an oder als Bevollmächtigte in deinem Namen. Die Auswahl ist klein, im Vergleich {len(zm)} Angebote, dafür übernimmt die Deutsche Bank die Steuer, siehe unten. Gemeinschaftskonten sind ausgeschlossen.</p></div>'''),
       ('Die Wege im Vergleich',_tbl(['Weg','Angebote','Abgeltungsteuer automatisch','Vorzeitig kündbar','Konto und Legitimation','Kosten'],prow)+
        f'''<div class="prose"><p>Stand {stand}. Der beste Zins für 1 Jahr liegt über Raisin bei {_pct(zr12)} ({L_(ar12)}), über CHECK24 bei {_pct(zc12)} ({L_(ac12)}), über den ZinsMarkt bei {_pct(zz12)} ({L_(az12)}) und direkt bei einer Bank bei {_pct(zd12)} ({L_(ad12)}). Die Reihenfolge ändert sich mit jeder Zinsanpassung, im <a href="{F1}">Vergleich für 1 Jahr</a> siehst du den aktuellen Stand. Wer nur deutsche Banken will, nutzt die Liste <a href="{FH}">deutsche Banken</a>.</p></div>'''),
       ('Was es kostet','''<div class="prose"><p>Für dich nichts. Raisin, CHECK24 und der ZinsMarkt verlangen weder für das Konto noch für Anlage oder Rückzahlung etwas, auch Überweisungen ins Ausland sind kostenlos. Die Plattformen verdienen an den Partnerbanken, die für die Vermittlung zahlen. Deshalb ist der Zins über die Plattform manchmal etwas niedriger als beim Direktabschluss bei derselben Bank, manchmal aber auch höher, wenn die Bank über die Plattform gezielt Geld einsammelt. Im Vergleich stehen beide Varianten nebeneinander.</p>
<p>Ein Kostenpunkt ist indirekt: Geld, das auf dem Verrechnungskonto liegt, bringt nichts oder fast nichts. Wer die Zinsen nicht gleich wieder anlegt, verschenkt Rendite. Und wer die Steuer selbst erklären muss, zahlt mit Zeit.</p></div>'''),
       ('Steuer: automatisch oder selbst',f'''<div class="prose"><p>Entscheidend ist, wo die Partnerbank sitzt, nicht wo die Plattform sitzt:</p><ul>
<li><b>Deutsche Partnerbank</b> über Raisin oder CHECK24: Die Bank führt Abgeltungsteuer, Soli und gegebenenfalls Kirchensteuer ab und berücksichtigt den Freistellungsauftrag, den du über die Plattform einreichst. Im Vergleich sind das {_cnt(raisin,lambda a:a["steuer_auto"])} Angebote über Raisin und {_cnt(c24,lambda a:a["steuer_auto"])} über CHECK24.</li>
<li><b>Ausländische Partnerbank</b> über Raisin oder CHECK24: Die Zinsen kommen brutto oder nach Abzug einer ausländischen Quellensteuer. Du gibst sie in der Anlage KAP an, ein Freistellungsauftrag ist nicht möglich, der Sparer-Pauschbetrag wird erst in der Steuererklärung berücksichtigt. Das betrifft {len(manuell)} Angebote im Vergleich.</li>
<li><b>ZinsMarkt:</b> Die Deutsche Bank beziehungsweise norisbank behält bei allen {len(zm)} Angeboten die Steuer ein und berücksichtigt ihren Freistellungsauftrag, auch bei Partnerbanken aus Frankreich oder Schweden. Das ist der Hauptvorteil dieses Wegs.</li></ul>
<p>Die Plattformen liefern für ausländische Angebote eine Jahresaufstellung. Bei Banken in Portugal, Lettland oder Litauen fällt Quellensteuer an, die du mit einer Ansässigkeitsbescheinigung senken und in der Anlage KAP anrechnen kannst. Das ganze Verfahren steht im Beitrag <a href="../festgeld-steuern/">Festgeld und Steuern</a>.</p></div>'''),
       ('Wo dein Geld wirklich liegt',f'''<div class="prose"><p>Immer bei der Partnerbank. Für die Einlagensicherung zählt deshalb deren Sitzland: Frankreich, Italien, Schweden, Lettland oder ein anderes EU-Land, jeweils bis 100.000 € pro Person und Bank. Die Verrechnungskonten bei der Raisin Bank AG und der C24 Bank sind über die deutsche Einlagensicherung geschützt, dort liegt das Geld aber nur zwischen Überweisung und Anlage. Eine Pleite der Plattform selbst berührt dein Festgeld nicht, der Vertrag mit der Partnerbank bleibt bestehen.</p>
<p>Beim ZinsMarkt gilt dasselbe: Sobald das Festgeld bei der Partnerbank liegt, fällt es nicht mehr unter die Einlagensicherung der Deutschen Bank, sondern unter die des Sitzlandes der Partnerbank. Über Raisin kommen im Vergleich Banken aus {len({a["sitz"] for a in raisin})} Ländern, über CHECK24 aus {len({a["sitz"] for a in c24})}. Welches Land und welche Sicherungseinrichtung für ein Angebot gelten, steht auf jeder Angebotsseite. Mehr im Beitrag zur <a href="../einlagensicherung/">Einlagensicherung</a>.</p></div>'''),
       ('Plattform oder Direktabschluss?','''<div class="prose"><p><b>Für die Plattform spricht:</b></p><ul class="checks">
<li>Eine Legitimation, ein Login, viele Banken. Praktisch für eine Zinstreppe über mehrere Banken.</li>
<li>Zugang zu Banken aus ganz Europa, oft mit höheren Zinsen als deutsche Banken.</li>
<li>Einfaches Streuen über mehrere Banken und Länder, um unter 100.000 € pro Bank zu bleiben.</li>
<li>Ein Postfach für alle Zinsbescheinigungen und Unterlagen.</li></ul>
<p><b>Für den Direktabschluss spricht:</b></p><ul>
<li>Bei deutschen Banken wird die Steuer automatisch abgeführt, Freistellungsauftrag direkt bei der Bank.</li>
<li>Keine ausländische Quellensteuer, keine Ansässigkeitsbescheinigungen.</li>
<li>Du bist direkt Kunde der Bank, mit Ansprechpartner und manchmal mit Kulanz bei vorzeitiger Auflösung.</li>
<li>Kein Umweg über ein Verrechnungskonto, das Geld kommt am Ende direkt aufs eigene Konto.</li></ul>
<p>Faustregel: Wer ohnehin eine Steuererklärung macht und größere Beträge streuen will, gewinnt mit der Plattform an Auswahl. Wer es einfach will, bleibt bei einer deutschen Bank oder nimmt über die Plattform nur deutsche Partnerbanken. Wer Deutsche-Bank-Kunde ist, bekommt über den ZinsMarkt ausländische Zinsen mit deutscher Steuerabwicklung.</p></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Ablauf bei Raisin: {_ext(RAISIN_ANL,"Raisin, So funktioniert Raisin")}; CHECK24 Anlagekonto, Legitimation und Steuer: {_ext(C24_ANL,"CHECK24, Das Anlagekonto im Geldanlagecenter")}; ZinsMarkt, Treuhandanlage, Kosten, Steuer, Einzelkonto: {_ext(DB_ZM,"Deutsche Bank, ZinsMarkt")}, alle abgerufen am {ABGERUFEN}.</li>
<li>Steuerabwicklung, Quellensteuer, Kündigung und Einlagensicherung je Angebot: Produktinformationsblätter und Konditionsseiten, verlinkt auf jeder Angebotsseite im <a href="{F}">Festgeld-Vergleich</a>, Stand {stand}.</li>
<li>Einlagensicherung: {_ext(BAFIN_ES,"BaFin, Einlagensicherung")}, abgerufen am {ABGERUFEN}.</li></ul></div>'''),
      ],
      faq=[
       ('Ist Festgeld über Raisin oder CHECK24 sicher?','Das Geld liegt bei der Partnerbank und ist über die Einlagensicherung ihres Sitzlandes bis 100.000 € pro Person und Bank geschützt. Die Verrechnungskonten bei der Raisin Bank AG und der C24 Bank fallen unter die deutsche Einlagensicherung. Eine Pleite der Plattform berührt dein Festgeld nicht.'),
       ('Was kosten die Plattformen?','Nichts. Konto, Anlage und Rückzahlung sind bei Raisin, CHECK24 und ZinsMarkt kostenlos. Die Plattformen werden von den Partnerbanken bezahlt.'),
       ('Kann ich bei Raisin oder CHECK24 einen Freistellungsauftrag stellen?',f'Nur für deutsche Partnerbanken. Im Vergleich führen {_cnt(raisin,lambda a:a["steuer_auto"])} Raisin- und {_cnt(c24,lambda a:a["steuer_auto"])} CHECK24-Angebote die Steuer automatisch ab. Bei ausländischen Partnerbanken gibst du die Zinsen in der Anlage KAP an.'),
       ('Was ist der ZinsMarkt der Deutschen Bank?',f'Ein Marktplatz für Festgeld von Partnerbanken, nutzbar mit einem Einzelkonto bei der Deutschen Bank oder norisbank. Die Bank legt treuhänderisch an und führt die Abgeltungsteuer ab, auch bei ausländischen Banken. Im Vergleich sind es {len(zm)} Angebote.'),
       ('Lohnt sich die Plattform gegenüber dem Direktabschluss?',f'Wenn die Plattform-Angebote höhere Zinsen bringen und du die Steuererklärung nicht scheust, ja. Im Vergleich liegt der beste 1-Jahres-Zins über Raisin bei {_pct(zr12)}, über CHECK24 bei {_pct(zc12)}, direkt bei {_pct(zd12)}, Stand {stand}.'),
      ],
      related=['festgeld-steuern','einlagensicherung','zinstreppe'])

    # ---------- 6. Steuern ----------
    B=10000; br=B*z12/100
    def _de(br_,anr=0.0,kist=0.0):
        """Deutsche Steuer auf br_ Zinsen (Pauschbetrag ausgeschöpft): 25 % minus anrechenbare ausländische Steuer, Soli 5,5 % darauf, KiSt nach § 32d Abs. 1 EStG."""
        if kist: kap=(br_-4*anr)/(4+kist)
        else: kap=max(br_*0.25-anr,0)
        return kap,kap*SOLI,kap*kist
    k0,s0,_=_de(br); k9,s9,c9=_de(br,0,0.09)
    anr=br*0.15; kp,sp,_=_de(br,anr)
    srow=[('Deutsche Bank, Freistellungsauftrag über 1.000 € vorhanden, zum Beispiel '+L_(ah12),f'{eur(round(B*zh12/100,2))} €','0 €, Zinsen unter dem Sparer-Pauschbetrag',f'{eur(round(B*zh12/100,2))} €','Freistellungsauftrag bei der Bank stellen'),
          ('Deutsche Bank, Pauschbetrag schon ausgeschöpft',f'{eur(round(br,2))} €',f'{eur(round(k0+s0,2))} € (25 % plus Soli = {_pct(26.375,3)})',f'{eur(round(br-k0-s0,2))} €','nichts, die Bank führt ab'),
          ('Deutsche Bank, Pauschbetrag ausgeschöpft, 9 % Kirchensteuer',f'{eur(round(br,2))} €',f'{eur(round(k9+s9+c9,2))} € ({_pct(27.99)})',f'{eur(round(br-k9-s9-c9,2))} €','nichts, die Bank führt ab'),
          ('Ausländische Bank ohne Quellensteuer, zum Beispiel in Schweden oder Italien, Pauschbetrag ausgeschöpft',f'{eur(round(br,2))} €',f'{eur(round(k0+s0,2))} € über den Steuerbescheid',f'{eur(round(br-k0-s0,2))} €','Zinsen in der Anlage KAP angeben'),
          ('Bank in Portugal mit Ansässigkeitsbescheinigung, Pauschbetrag ausgeschöpft',f'{eur(round(br,2))} €',f'{eur(round(anr,2))} € Quellensteuer (15 %) plus {eur(round(kp+sp,2))} € in Deutschland',f'{eur(round(br-anr-kp-sp,2))} €','Anlage KAP mit anrechenbarer Quellensteuer, Bescheinigung vorher einreichen')]
    qrow=[('Portugal','28 %','15 %','Ansässigkeitsbescheinigung und Formular 21-RFI, spätestens 4 Wochen vor der Zinszahlung'),
          ('Lettland','25,5 %','10 %','Ansässigkeitsbescheinigung, bei Raisin spätestens 8 Wochen, bei CHECK24 28 Tage vor der Zinszahlung'),
          ('Litauen','15 %','10 %','Ansässigkeitsbescheinigung und Steuerformular, spätestens 4 Wochen vor der Zinszahlung; bei einzelnen Banken keine Reduktion'),
          ('Spanien','19 %','0 %','Ansässigkeitsbescheinigung, spätestens 4 Wochen vor der Zinszahlung'),
          ('Italien, Frankreich, Schweden, Estland, Malta, Niederlande','0 %','–','nichts, Zinsen kommen brutto')]
    art('de','festgeld-steuern',
      h1='Festgeld und Steuern in Deutschland: Abgeltungsteuer, Pauschbetrag, Anlage KAP',
      mt='Festgeld-Steuern Deutschland: Abgeltungsteuer | Finvallo',
      desc=f'Festgeld-Zinsen versteuern in Deutschland: 25 % Abgeltungsteuer plus Soli, 1.000 € Sparer-Pauschbetrag, Freistellungsauftrag, NV-Bescheinigung, Anlage KAP bei ausländischen Banken und Quellensteuer. Mit Rechenbeispiel.',
      about='Festgeld in Deutschland',
      lede='Zinsen sind Kapitalerträge: 25 % Abgeltungsteuer plus Soli, aber erst ab 1.000 € im Jahr. Wer das richtig einstellt, zahlt oft gar nichts.',
      kurz=(f'Festgeld-Zinsen kosten 25 % Abgeltungsteuer plus 5,5 % Solidaritätszuschlag darauf, zusammen {_pct(26.375,3)}, mit Kirchensteuer bis {_pct(27.99)}. Steuerfrei bleiben Kapitalerträge bis zum Sparer-Pauschbetrag von 1.000 € im Jahr, 2.000 € für zusammen veranlagte Paare. '
            f'Deutsche Banken ziehen die Steuer automatisch ab und berücksichtigen deinen Freistellungsauftrag. Im Vergleich gilt das bei {len(auto)} von {n} Angeboten. Bei {len(manuell)} Angeboten ausländischer Banken gibst du die Zinsen selbst in der Anlage KAP an und rechnest dort eine ausländische Quellensteuer an.'),
      secs=[
       ('Abgeltungsteuer, Soli und Kirchensteuer',f'''<div class="prose"><p>Zinsen aus Festgeld sind Einkünfte aus Kapitalvermögen (§ 20 EStG). Sie werden nicht mit deinem Gehalt zusammengerechnet, sondern pauschal mit 25 % besteuert (§ 32d Abs. 1 EStG). Darauf kommt der Solidaritätszuschlag von 5,5 % der Steuer, zusammen also {_pct(26.375,3)} der Zinsen. Der Soli fällt auf Kapitalerträge immer an, die Freigrenze beim Soli gilt nur für die Lohn- und Einkommensteuer.</p>
<p>Bist du Mitglied einer Kirche, zieht die Bank auch die Kirchensteuer ab: 8 % der Abgeltungsteuer in Bayern und Baden-Württemberg, 9 % in den anderen Ländern. Weil die Kirchensteuer als Sonderausgabe wirkt, sinkt die Abgeltungsteuer dann leicht, am Ende sind es {_pct(27.82)} beziehungsweise {_pct(27.99)}. Die Bank fragt deine Konfession automatisch beim Bundeszentralamt für Steuern ab, außer du hast dort einen Sperrvermerk gesetzt.</p>
<p>Beispiel: {eur(B)} € ein Jahr lang zum besten Zins im Vergleich, {_pct(z12)} bei {L_(a12)}, bringen {eur(round(br,2))} € Zinsen. Ohne Freistellungsauftrag gehen {eur(round(k0+s0,2))} € Steuer ab. Für andere Beträge rechnet der <a href="{RK}">Abgeltungsteuer-Rechner</a>.</p></div>'''),
       ('Sparer-Pauschbetrag und Freistellungsauftrag','''<div class="prose"><p>Kapitalerträge bis 1.000 € im Jahr bleiben steuerfrei, bei zusammen veranlagten Ehepaaren und eingetragenen Partnern 2.000 € (§ 20 Abs. 9 EStG). Das ist der Sparer-Pauschbetrag. Er gilt für alle Kapitalerträge zusammen: Zinsen, Dividenden, Fondsausschüttungen, Kursgewinne.</p>
<p>Damit die Bank ihn gleich berücksichtigt, stellst du einen <b>Freistellungsauftrag</b>. Den kannst du auf mehrere Banken verteilen, solange die Summe 1.000 € beziehungsweise 2.000 € nicht übersteigt. Bei einer Zinstreppe über drei Banken heißt das: drei Aufträge, aufgeteilt nach den erwarteten Zinsen. Zu viel freigestellt ist kein Drama, das Finanzamt gleicht das über die Steuererklärung aus, aber bewusst falsche Aufteilung ist nicht erlaubt. Ein Freistellungsauftrag geht nur bei Banken, die deutsche Abgeltungsteuer abführen.</p>
<p>Ist dein Einkommen so niedrig, dass du gar keine Einkommensteuer zahlst, etwa als Studentin, Rentner mit kleiner Rente oder Kind mit eigenem Sparguthaben, beantragst du beim Finanzamt eine <b>Nichtveranlagungsbescheinigung</b> (§ 44a EStG). Sie gilt bis zu drei Jahre. Mit ihr zahlt die Bank alle Zinsen ohne Abzug aus, auch über 1.000 € hinaus.</p></div>'''),
       ('Deutsche Bank: Steuer läuft automatisch',f'''<div class="prose"><p>Hat die Bank ihren Sitz in Deutschland oder eine deutsche Zweigniederlassung, behält sie Abgeltungsteuer, Soli und Kirchensteuer bei der Zinsgutschrift ein und führt sie ans Finanzamt ab. Mit dem Abzug ist die Steuer abgegolten, daher der Name. Du musst die Zinsen nicht in der Steuererklärung angeben. Die Bank schickt dir eine Steuerbescheinigung, die du nur brauchst, wenn du freiwillig veranlagst.</p>
<p>Im Vergleich führen {len(auto)} von {n} Angeboten die Steuer automatisch ab: die Direktabschlüsse bei Banken mit Sitz in Deutschland, gesammelt in der Liste <a href="{FH}">deutsche Banken</a>, die deutschen Partnerbanken über Raisin und CHECK24 sowie alle {len(zm)} Angebote über den ZinsMarkt der Deutschen Bank, bei dem die Deutsche Bank die Steuer auch für ausländische Partnerbanken einbehält. Auf jeder Angebotsseite steht unter „Steuer“, ob die Bank abführt.</p></div>'''),
       ('Ausländische Bank: Anlage KAP',f'''<div class="prose"><p>Eine Bank in Schweden, Italien oder Lettland führt keine deutsche Abgeltungsteuer ab. Die Zinsen kommen brutto bei dir an, oder nach Abzug einer ausländischen Quellensteuer. Du bist verpflichtet, sie in der Einkommensteuererklärung anzugeben, in der <b>Anlage KAP</b> im Abschnitt für Kapitalerträge, die nicht dem inländischen Steuerabzug unterlegen haben. Dort trägst du auch den noch nicht genutzten Sparer-Pauschbetrag und die anrechenbare ausländische Steuer ein. Das Finanzamt setzt dann 25 % plus Soli fest, nicht mehr als bei einer deutschen Bank. Im Vergleich betrifft das {len(manuell)} Angebote, fast alle über Raisin und CHECK24.</p>
<p>So gehst du vor:</p><ol>
<li>Sammle die Jahresaufstellung der Plattform oder Bank. Raisin und CHECK24 stellen sie im Online-Postfach bereit.</li>
<li>Reiche die Steuererklärung über ELSTER ein. Ohne Steuerberatung ist sie bis zum 31. Juli des Folgejahres fällig.</li>
<li>Trag die Zinsen in der Anlage KAP ein, dazu die im Ausland einbehaltene Quellensteuer. Das Finanzamt rechnet sie nach § 32d Abs. 5 EStG an.</li></ol>
<p>Nicht erklären ist keine Option. Die Banken melden Zinsen über den automatischen Informationsaustausch der EU an das Wohnsitzland, das Finanzamt bekommt die Daten also ohnehin.</p></div>'''),
       ('Ausländische Quellensteuer: Sätze und Anrechnung',_tbl(['Sitzland der Bank','Quellensteuer ohne Nachweis','Mit Ansässigkeitsbescheinigung','Was du einreichen musst'],qrow)+
        f'''<div class="prose"><p>Sätze laut Produktinformationsblättern der Angebote im <a href="{F}">Festgeld-Vergleich</a>, Stand {stand}. Sie gelten je Bank, nicht pauschal je Land: Raisin nennt in seiner Länderübersicht für Lettland 20 % und für Spanien 0 %, die Produktblätter der Banken im Vergleich 25,5 % beziehungsweise 19 %. Verlässlich ist nur das Produktinformationsblatt des konkreten Angebots.</p>
<p>Die Anrechnung in Deutschland hat eine Grenze: Du kannst ausländische Steuer nur bis zu dem Satz anrechnen, den das Doppelbesteuerungsabkommen dem anderen Staat zugesteht, bei Portugal 15 %, bei Lettland und Litauen 10 %. Hat die Bank mehr einbehalten, weil deine Ansässigkeitsbescheinigung fehlte, bekommst du den Rest nur vom ausländischen Finanzamt zurück. Das dauert und ist mühsam. Reiche die Bescheinigung deshalb vor der ersten Zinszahlung ein. Du bekommst sie bei deinem Finanzamt, die Plattformen stellen das Formular bereit und leiten es an die Bank weiter.</p></div>'''),
       ('Rechenbeispiel: 10.000 € für ein Jahr',_tbl(['Weg','Zinsen brutto','Steuer','Netto','Was du tun musst'],srow)+
        f'''<div class="prose"><p>Gerechnet mit dem besten Zins für 1 Jahr im Vergleich, {_pct(z12)}, in der ersten Zeile mit dem besten Zins einer Bank mit Sitz in Deutschland, {_pct(zh12)}. Solange die Zinsen unter dem Sparer-Pauschbetrag liegen, zahlst du bei korrekter Freistellung nichts. Bei der ausländischen Bank gilt das genauso, nur erst über die Steuererklärung. Bei Quellensteuer fällt der Soli nur auf den in Deutschland verbleibenden Teil an, deshalb ist das Netto dort minimal höher als bei der deutschen Bank.</p></div>'''),
       ('Günstigerprüfung: wenn dein Steuersatz unter 25 % liegt','''<div class="prose"><p>Liegt dein persönlicher Steuersatz unter 25 %, etwa bei geringem Einkommen, in der Rente oder im Studium, kannst du in der Anlage KAP die <b>Günstigerprüfung</b> beantragen (§ 32d Abs. 6 EStG). Das Finanzamt rechnet dann die Kapitalerträge zu deinem übrigen Einkommen und besteuert sie mit deinem Tarif, aber nur, wenn das für dich günstiger ist. Zu viel einbehaltene Abgeltungsteuer bekommst du zurück. Der Antrag gilt immer für alle Kapitalerträge eines Jahres, bei Ehepaaren für beide.</p>
<p>Ein Antrag in der Anlage KAP lohnt sich auch, wenn du den Sparer-Pauschbetrag nicht voll über Freistellungsaufträge genutzt hast, wenn eine Bank Kirchensteuer nicht abgezogen hat oder wenn ausländische Quellensteuer noch nicht berücksichtigt wurde (§ 32d Abs. 4 EStG).</p></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Steuersatz, Anrechnung ausländischer Steuer, Antrag und Günstigerprüfung: {_ext(ESTG("32d"),"§ 32d EStG")}; Sparer-Pauschbetrag: {_ext(ESTG("20"),"§ 20 Abs. 9 EStG")}; Freistellungsauftrag und NV-Bescheinigung: {_ext(ESTG("44a"),"§ 44a EStG")}, alle abgerufen am {ABGERUFEN}.</li>
<li>Quellensteuersätze, Fristen und Formulare je Bank: Produktinformationsblätter der Angebote, verlinkt auf jeder Angebotsseite im <a href="{F}">Festgeld-Vergleich</a>, Stand {stand}; Länderübersicht: {_ext(RAISIN_QST,"Raisin, Quellensteuer")}; Ansässigkeitsbescheinigung über CHECK24: {_ext(C24_ANL,"CHECK24, Anlagekonto")}, abgerufen am {ABGERUFEN}.</li>
<li>Steuerabwicklung je Angebot (automatisch oder selbst): Angaben der Banken und Plattformen, Stand {stand}.</li></ul>
<p>Dieser Beitrag ersetzt keine Steuerberatung. Bei größeren Beträgen im Ausland lohnt sich die Frage an eine Steuerberaterin oder einen Steuerberater.</p></div>'''),
      ],
      faq=[
       ('Wie hoch ist die Steuer auf Festgeld-Zinsen?',f'25 % Abgeltungsteuer plus 5,5 % Soli darauf, zusammen {_pct(26.375,3)}. Mit Kirchensteuer sind es {_pct(27.82)} oder {_pct(27.99)}. Steuerfrei bleiben Kapitalerträge bis 1.000 € im Jahr, 2.000 € für Paare.'),
       ('Muss ich Festgeld-Zinsen in der Steuererklärung angeben?','Bei einer deutschen Bank nicht, sie führt die Steuer ab. Bei einer ausländischen Bank ja, in der Anlage KAP. Der Steuersatz ist derselbe.'),
       ('Kann ich bei einer ausländischen Bank einen Freistellungsauftrag stellen?','Nein. Der Sparer-Pauschbetrag wird dann erst in der Steuererklärung über die Anlage KAP berücksichtigt. Ausnahme ist der ZinsMarkt der Deutschen Bank, der die Steuer auch für ausländische Partnerbanken abführt.'),
       ('Was ist mit der Quellensteuer in Portugal oder Lettland?','Die Bank behält dort 28 % beziehungsweise 25,5 % ein. Mit einer Ansässigkeitsbescheinigung deines Finanzamts sinkt der Satz auf 15 % beziehungsweise 10 %, und diesen Teil rechnest du in der Anlage KAP an. Zu viel einbehaltene Steuer musst du im Ausland zurückfordern.'),
       ('Wann lohnt sich die Günstigerprüfung?','Wenn dein persönlicher Steuersatz unter 25 % liegt, etwa bei geringem Einkommen, im Studium oder in der Rente. Das Finanzamt wendet dann den günstigeren Tarif an und erstattet zu viel gezahlte Abgeltungsteuer.'),
       ('Was bringt eine Nichtveranlagungsbescheinigung?','Wer keine Einkommensteuer zahlt, bekommt sie beim Finanzamt. Die Bank zahlt dann alle Zinsen ohne Abzug aus, auch über 1.000 € hinaus. Sie gilt bis zu drei Jahre.'),
      ],
      related=['festgeld-plattformen','einlagensicherung','festgeld-oder-tagesgeld'])
