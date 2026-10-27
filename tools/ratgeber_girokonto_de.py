# Ratgeber (nur DE) zu Girokonten: Konto wechseln, Basiskonto, kostenloses Girokonto. Gleiche Slugs wie in AT (hreflang-Paare).
# Zahlen zu Konten kommen live aus daten/de/girokonten.json (über girokonto.py).
# Rechtliches: Zahlungskontengesetz (ZKG) §§ 20 bis 50, BGH XI ZR 119/19, BaFin, ZPO § 850k/§ 899, Pfändungsfreigrenzenbekanntmachung 2026,
# SEPA-Verordnung Art. 9; abgerufen am 27.10.2026 bei gesetze-im-internet.de, bundesgerichtshof.de, bafin.de und verbraucherzentrale.de.
# Aufruf aus ratgeber.build('de'): register(art,P,eur)
import html
E=lambda s: html.escape(str(s)) if s is not None else ''
ZKG=lambda n: f'https://www.gesetze-im-internet.de/zkg/__{n}.html'
BGH_BASIS='https://www.bundesgerichtshof.de/SharedDocs/Pressemitteilungen/DE/2020/2020084.html'
BAFIN_BASIS='https://www.bafin.de/DE/verbraucherinnen-verbraucher/themen-finanzprodukte/konten-zahlungen/konten/basiskonto/basiskonto_node.html'
BAFIN_IBAN='https://www.bafin.de/DE/verbraucherinnen-verbraucher/themen-finanzprodukte/konten-zahlungen/zahlungen/ueberweisungen-und-lastschriften/ueberweisungen-und-lastschriften.html'
VZ_PKONTO='https://www.verbraucherzentrale.de/wissen/geld-versicherungen/kredit-schulden-insolvenz/fragen-und-antworten-zum-pfaendungsschutzkonto-pkonto-5959'

def _tbl(head,rows):
    h=''.join(f'<th>{c}</th>' for c in head)
    b=''.join('<tr>'+''.join(f'<td>{c}</td>' for c in r)+'</tr>' for r in rows)
    return f'<div class="tbl wide"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'
def _ext(u,t): return f'<a href="{E(u)}" target="_blank" rel="noopener">{E(t)} ↗</a>'

def register(art,P,eur):
    import girokonto as G
    G.K.use('de'); G.LAND,G.CC='de',G.CFG['de']
    d,ks=G.load('de')
    for k in ks: k.setdefault('geprueft',d['stand'])
    G.rate(ks)
    G.K.use('at'); G.LAND,G.CC='at',G.CFG['at']
    def L(k,label=None): return f'<a class="lnk" href="{P}de/girokonto/{k["slug"]}/">{E(label or k["name"])}</a> <small class="mut">({E(k["bank"])})</small>'
    alle=[k for k in ks if k['art'] in ('standard','premium')]
    pr=G.PROFIL['standard']
    cost=lambda k:G.kosten(k,pr['ein'],pr['alter'],pr['abh'])['total']
    gratis=sorted([k for k in alle if k['kf_jahr']==0],key=lambda k:-k['stars'])
    bedingt=sorted([k for k in alle if k.get('gratis') and k['gratis'].get('eingang_min') is not None and k['gratis'].get('kf_bedingt')==0],key=lambda k:(k['gratis']['eingang_min'],-k['stars']))
    nnull=len([k for k in alle if cost(k)==0])
    basis=sorted([k for k in ks if k['art']=='basis'],key=lambda k:(k['kf_jahr'],k['bank'].lower()))
    zs=[k.get('ueberschreitung') or k.get('sollzins') for k in alle if (k.get('ueberschreitung') or k.get('sollzins'))]
    G1=f'{P}de/girokonto/'; B=f'{G1}bestenlisten/'

    # ---------- 1. Konto wechseln ----------
    art('de','girokonto-wechseln',
      h1='Girokonto wechseln in Deutschland: So hilft dir die neue Bank',
      mt='Girokonto wechseln: Kontowechselhilfe, Fristen, Kosten | Finvallo',
      desc='Girokonto wechseln in Deutschland: Die neue Bank muss dir laut Zahlungskontengesetz helfen. Ablauf, Fristen, was kostenlos ist und was bei Banken im EU-Ausland gilt.',
      about='Girokonten in Deutschland',
      lede='Für den Wechsel musst du nicht jeden Zahlungspartner selbst anschreiben. Das Zahlungskontengesetz verpflichtet beide Banken, dir zu helfen.',
      kurz=('Die Kontowechselhilfe steht in den §§ 20 bis 26 Zahlungskontengesetz (ZKG). Du ermächtigst die neue Bank schriftlich oder im Online-Banking. '
            'Sie fordert die alte Bank auf, die Listen deiner Daueraufträge, Lastschriften und Eingänge zu schicken, richtet alles ein und informiert auf Wunsch deine Zahlungspartner. '
            'Die Listen und die Schließung des alten Kontos sind immer kostenlos.'),
      secs=[
       ('So läuft der Wechsel ab',f'''<div class="prose"><ol>
<li><b>Neues Konto eröffnen.</b> Im <a href="{G1}">Girokonto-Vergleich</a> rechnest du mit deinem Geldeingang und deinen Abhebungen aus, was jedes Konto im Jahr kostet.</li>
<li><b>Kontowechselhilfe beauftragen.</b> Du gibst der neuen Bank eine Ermächtigung, schriftlich oder im Online-Banking. Darin legst du fest, welche Daueraufträge, Lastschriften und Eingänge übertragen werden, ab wann das alte Konto nichts mehr ausführt und wann es schließen soll.</li>
<li><b>Abwarten und prüfen.</b> Die Banken tauschen die Daten aus. Danach prüfst du, ob Gehalt, Miete und Abbuchungen auf dem neuen Konto ankommen.</li></ol></div>'''),
       ('Die Fristen laut Gesetz',_tbl(['Schritt','Wer','Frist'],[
            ('Die neue Bank fordert die alte Bank auf, die Listen und Informationen zu schicken','neue Bank','2 Geschäftstage nach deiner Ermächtigung (§ 22 ZKG)'),
            ('Die alte Bank schickt die Listen: Daueraufträge, Lastschriften und eingehende Zahlungen der letzten 13 Monate','alte Bank','5 Geschäftstage (§ 23 ZKG)'),
            ('Die neue Bank richtet Daueraufträge ein, akzeptiert die Lastschriften und informiert Zahler und Empfänger','neue Bank','5 Geschäftstage nach Erhalt der Listen (§ 24 ZKG)')])+
        '<div class="prose"><p>Rechnet man die Fristen zusammen, sind das etwa 12 Geschäftstage. Das neue Konto übernimmt die Zahlungen frühestens 6 Geschäftstage, nachdem die neue Bank die Listen bekommen hat. Willst du deine Zahlungspartner lieber selbst informieren, kannst du Musterschreiben verlangen.</p></div>'),
       ('Was kostenlos ist und was nicht','''<div class="prose"><p>Immer kostenlos sind laut § 26 ZKG:</p><ul class="checks">
<li>der Zugang zu deinen Daten über Daueraufträge und Lastschriften</li>
<li>die Listen und Informationen, die die alte Bank schickt</li>
<li>die Schließung des alten Kontos</li></ul>
<p>Für die übrigen Leistungen der Kontowechselhilfe darf eine Bank ein Entgelt verlangen, aber nur, wenn es vereinbart ist, angemessen ist und sich an ihren tatsächlichen Kosten ausrichtet. Eine Vertragsstrafe für den Wechsel ist verboten. Die Kündigungsfrist für ein Girokonto darf höchstens einen Monat betragen, und für die Kündigung selbst darf die Bank nichts verlangen (§ 675h BGB).</p>
<p>Ein Guthaben auf dem alten Konto überweist die alte Bank zum gewünschten Datum auf das neue Konto. Ist das alte Konto im Minus, solltest du es vorher selbst ausgleichen.</p></div>'''),
       ('Wechsel zu einer Bank im EU-Ausland','''<div class="prose"><p>Die volle Kontowechselhilfe gilt nur, wenn beide Banken in Deutschland ansässig sind (§ 20 Abs. 2 ZKG). Wechselst du zu einer Bank in einem anderen EU-Land, muss deine alte Bank dir trotzdem helfen (§§ 27 bis 29 ZKG):</p><ul>
<li>Sie schickt dir kostenlos eine Liste deiner Daueraufträge, Lastschriftmandate und Eingänge der letzten 13 Monate.</li>
<li>Sie überweist das Guthaben auf dein neues Konto oder zahlt es dir aus.</li>
<li>Sie schließt das alte Konto, frühestens 6 Geschäftstage nach deiner Aufforderung.</li></ul>
<p>Deine Zahlungspartner informierst du in diesem Fall selbst. Wo eine Bank ihren Sitz hat, steht in ihrem Impressum. Eine deutsche IBAN allein sagt das nicht.</p></div>'''),
       ('Und wenn jemand die neue IBAN ablehnt?',f'''<div class="prose"><p>Laut Art. 9 der SEPA-Verordnung der EU darf niemand vorschreiben, in welchem EU-Land dein Konto geführt wird. Lehnt jemand eine IBAN aus einem anderen EU-Land ab, ist das laut BaFin „IBAN-Diskriminierung“. Verstöße von Banken meldest du der BaFin, Verstöße von anderen Firmen, etwa Arbeitgebern, Vermietern oder Versicherungen, der Wettbewerbszentrale.</p></div>'''),
       ('Checkliste für den Wechsel','''<div class="prose"><ul class="checks">
<li>Gehalt oder Rente: Hat der Arbeitgeber oder die Rentenversicherung die neue IBAN?</li>
<li>Kindergeld, Bürgergeld, Arbeitslosengeld: Sind Familienkasse, Jobcenter oder Agentur für Arbeit informiert?</li>
<li>Miete, Strom, Handy, Versicherungen, Abos: Laufen die Lastschriften über das neue Konto?</li>
<li>Finanzamt: Ist die neue IBAN für Erstattungen hinterlegt?</li>
<li>Karten: Sind girocard und Kreditkarte am alten Konto ersetzt? Hinterlegte Karten bei Shops und Apps ändern.</li>
<li>Altes Konto: Ist es ausgeglichen, und bleibt bis zur Schließung genug Zeit für letzte Abbuchungen?</li></ul></div>'''),
       ('Lohnt sich der Wechsel?',f'''<div class="prose"><p>Bei {nnull} der {len(alle)} Konten für alle im Vergleich zahlst du mit {eur(pr["ein"])} € Geldeingang und {pr["abh"]} Abhebungen pro Monat nichts. Viele Filialbanken kosten dagegen 5 bis 14 € im Monat. Passende Listen: <a href="{B}kostenlos/">kostenlose Girokonten</a>, <a href="{B}gehaltskonto/">Gehaltskonten</a> und <a href="{B}filiale/">Konten mit Filiale</a>.</p></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Zahlungskontengesetz: {_ext(ZKG(20),"§ 20")}, {_ext(ZKG(22),"§ 22")}, {_ext(ZKG(23),"§ 23")}, {_ext(ZKG(24),"§ 24")}, {_ext(ZKG(26),"§ 26")}, {_ext(ZKG(27),"§ 27")} bis {_ext(ZKG(29),"§ 29")}; Kündigung: {_ext("https://www.gesetze-im-internet.de/bgb/__675h.html","§ 675h BGB")}. Abgerufen am 27.10.2026.</li>
<li>IBAN-Diskriminierung: {_ext(BAFIN_IBAN,"BaFin, Überweisungen und Lastschriften")}.</li>
<li>Kontopreise: Entgeltinformationen der Banken, verlinkt auf jeder Kontoseite.</li></ul></div>'''),
      ],
      faq=[
       ('Wie lange dauert ein Kontowechsel?','Rechnet man die gesetzlichen Fristen zusammen, etwa 12 Geschäftstage: 2 Tage für die Aufforderung der neuen Bank, 5 Tage für die Listen der alten Bank und 5 Tage zum Einrichten.'),
       ('Ist die Kontowechselhilfe kostenlos?','Die Listen, der Zugang zu deinen Daten und die Schließung des alten Kontos sind immer kostenlos. Für weitere Leistungen darf eine Bank ein angemessenes Entgelt verlangen, wenn das vereinbart ist.'),
       ('Gilt die Kontowechselhilfe auch bei einer Bank im EU-Ausland?','Nur eingeschränkt. Die alte Bank muss dir kostenlos eine Liste deiner Zahlungen geben, das Guthaben überweisen und das Konto schließen. Deine Zahlungspartner informierst du selbst.'),
       ('Wie lange ist die Kündigungsfrist beim Girokonto?','Höchstens einen Monat, und für die Kündigung darf die Bank kein Entgelt verlangen.'),
       ('Darf mein Arbeitgeber eine IBAN aus einem anderen EU-Land ablehnen?','Nein. Laut SEPA-Verordnung darf niemand vorschreiben, in welchem EU-Land dein Konto geführt wird. Beschwerden über Firmen nimmt die Wettbewerbszentrale an, über Banken die BaFin.'),
      ],
      related=['basiskonto','kostenloses-girokonto'])

    # ---------- 2. Basiskonto ----------
    brow=[(L(k),E(G.kfT(k)),f'{eur(k["kf_jahr"])} €',E(G.wegT(k))) for k in basis]
    bmin=basis[0]; bmax=max(basis,key=lambda k:k['kf_jahr'])
    art('de','basiskonto',
      h1='Basiskonto in Deutschland: Das Recht auf ein Girokonto',
      mt='Basiskonto Deutschland: Anspruch, Kosten, Ablehnung | Finvallo',
      desc=f'Basiskonto in Deutschland: Wer Anspruch hat, was dabei ist, wann die Bank ablehnen darf und was es kostet. {len(basis)} Basiskonten im Vergleich.',
      about='Girokonten in Deutschland',
      lede='Jede Bank, die Girokonten für Verbraucher anbietet, muss dir ein Basiskonto eröffnen. Auch ohne festen Wohnsitz, mit Schulden oder mit negativer Schufa.',
      kurz=('Das Recht auf ein Basiskonto steht in § 31 Zahlungskontengesetz. Anspruch hat jeder Verbraucher mit rechtmäßigem Aufenthalt in der EU, auch Menschen ohne festen Wohnsitz und Asylsuchende. '
            'Die Bank muss dir den Vertrag spätestens 10 Geschäftstage nach deinem Antrag anbieten. Eine feste Preisgrenze gibt es nicht, das Entgelt muss aber angemessen sein. '
            f'Im Vergleich kosten Basiskonten zwischen {eur(bmin["kf_jahr"])} € und {eur(bmax["kf_jahr"])} € im Jahr.'),
      secs=[
       ('Wer Anspruch hat','''<div class="prose"><p>Anspruch hat jeder Verbraucher mit rechtmäßigem Aufenthalt in der EU. Dazu zählen ausdrücklich auch Menschen ohne festen Wohnsitz, Asylsuchende und Menschen ohne Aufenthaltstitel, die aus rechtlichen oder tatsächlichen Gründen nicht abgeschoben werden können (§ 31 ZKG). Eine negative Schufa oder Schulden sind kein Grund für eine Ablehnung.</p></div>'''),
       ('Was ein Basiskonto kann','''<div class="prose"><ul class="checks">
<li>Geld einzahlen und abheben</li>
<li>Überweisungen und Daueraufträge</li>
<li>Lastschriften</li>
<li>Zahlen mit Karte</li></ul>
<p>Die Bank muss diese Leistungen so anbieten wie bei ihren anderen Girokonten, und sie darf die Zahl der Buchungen nicht begrenzen (§ 38 ZKG). Einen Dispo gibt es nicht, das Basiskonto läuft auf Guthabenbasis. Du kannst schon beim Antrag verlangen, dass es als Pfändungsschutzkonto (P-Konto) geführt wird.</p></div>'''),
       ('Was es kosten darf',f'''<div class="prose"><p>Eine feste Obergrenze in Euro gibt es in Deutschland nicht. Das Entgelt muss laut § 41 ZKG angemessen sein, gemessen an marktüblichen Preisen und am Nutzerverhalten. Der Bundesgerichtshof hat 2020 entschieden, dass eine Bank die Mehrkosten für Basiskonten nicht allein auf die Inhaber von Basiskonten umlegen darf (Urteil XI ZR 119/19). Im Streit standen 8,99 € im Monat und 1,50 € für jede beleghafte Überweisung. Diese Entgeltklauseln waren unwirksam.</p></div>'''),
       ('Basiskonten im Vergleich',_tbl(['Konto','Kontoführung','Im Jahr','Eröffnung'],brow)+
        f'<div class="prose"><p>Die Preise stammen aus den Entgeltinformationen der Banken. Dazu können Kosten für Karten oder Abhebungen kommen, das steht auf jeder Kontoseite und im <a href="{G1}">Girokonto-Vergleich</a>.</p></div>'),
       ('Wann die Bank ablehnen darf','''<div class="prose"><p>Nur aus Gründen, die im Gesetz stehen (§§ 35 bis 37 ZKG), etwa:</p><ul>
<li>Du hast in Deutschland schon ein Girokonto, das du nutzen kannst. Ausnahme: Es wurde gekündigt oder du wurdest über die Schließung informiert.</li>
<li>Du wurdest in den letzten drei Jahren wegen einer vorsätzlichen Straftat gegen die Bank, ihre Mitarbeitenden oder Kunden verurteilt.</li>
<li>Die Bank hat dir im letzten Jahr ein Basiskonto berechtigt gekündigt, etwa wegen Zahlungsverzug.</li>
<li>Die Bank kann ihre Pflichten nach dem Geldwäschegesetz nicht erfüllen.</li></ul>
<p>Die Ablehnung muss kostenlos und in Textform kommen, mit Gründen und mit dem Hinweis, wie du dich wehren kannst.</p></div>'''),
       ('Wenn die Bank ablehnt oder nicht reagiert',f'''<div class="prose"><p>Du kannst bei der BaFin ein Verwaltungsverfahren beantragen, wenn die Bank ablehnt, nicht innerhalb von 10 Geschäftstagen entscheidet oder das Konto nicht innerhalb von 10 Geschäftstagen nach Vertragsschluss eröffnet (§ 48 ZKG). Die BaFin kann die Bank dann verpflichten, dir das Konto zu eröffnen. Das Verfahren ist laut BaFin für dich gebührenfrei. Andere Wege sind die Verbraucherschlichtungsstelle bei der Deutschen Bundesbank oder eine Klage vor Gericht.</p></div>'''),
       ('Wann die Bank kündigen darf','''<div class="prose"><p>Auch die Kündigung ist nur aus Gründen im Gesetz erlaubt (§ 42 ZKG). Mit mindestens zwei Monaten Frist zum Beispiel, wenn du mehr als 24 Monate lang keine Zahlung in Auftrag gegeben hast, wenn du ein zweites Girokonto in Deutschland eröffnet hast oder wenn du mit mehr als 100 € Entgelten über drei Monate im Verzug bist. Fristlos, wenn du das Konto vorsätzlich für verbotene Zwecke nutzt oder falsche Angaben gemacht hast.</p></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Zahlungskontengesetz: {_ext(ZKG(31),"§ 31")}, {_ext(ZKG(35),"§ 35")} bis {_ext(ZKG(37),"§ 37")}, {_ext(ZKG(38),"§ 38")}, {_ext(ZKG(41),"§ 41")}, {_ext(ZKG(42),"§ 42")}, {_ext(ZKG(48),"§ 48")}. Abgerufen am 27.10.2026.</li>
<li>Urteil: {_ext(BGH_BASIS,"BGH, Pressemitteilung 084/2020 zu XI ZR 119/19")}.</li>
<li>Verfahren: {_ext(BAFIN_BASIS,"BaFin, Basiskonto")}.</li>
<li>Preise der Basiskonten: Entgeltinformationen der Banken, verlinkt auf jeder Kontoseite.</li></ul></div>'''),
      ],
      faq=[
       ('Wer hat Anspruch auf ein Basiskonto?','Jeder Verbraucher mit rechtmäßigem Aufenthalt in der EU, auch Menschen ohne festen Wohnsitz, Asylsuchende und Geduldete. Schulden oder eine negative Schufa sind kein Ablehnungsgrund.'),
       ('Was kostet ein Basiskonto?',f'Eine feste Grenze gibt es nicht, das Entgelt muss angemessen sein. Im Vergleich kosten Basiskonten zwischen {eur(bmin["kf_jahr"])} € und {eur(bmax["kf_jahr"])} € im Jahr.'),
       ('Wie schnell muss die Bank reagieren?','Die Bank muss dir den Vertrag spätestens 10 Geschäftstage nach deinem Antrag anbieten oder ablehnen. Nach Vertragsschluss hat sie noch einmal 10 Geschäftstage, um das Konto zu eröffnen.'),
       ('Hat ein Basiskonto einen Dispo?','Nein. Das Basiskonto läuft auf Guthabenbasis, ohne Kreditgeschäft.'),
       ('Was kann ich tun, wenn die Bank ablehnt?','Du kannst bei der BaFin ein kostenloses Verwaltungsverfahren beantragen. Die BaFin kann die Bank verpflichten, das Konto zu eröffnen. Auch die Schlichtungsstelle der Bundesbank und eine Klage sind möglich.'),
       ('Kann das Basiskonto ein P-Konto sein?','Ja. Du kannst schon beim Antrag verlangen, dass es als Pfändungsschutzkonto geführt wird. Seit 1. Juli 2026 sind auf einem P-Konto 1.590 € pro Monat geschützt.'),
      ],
      related=['girokonto-wechseln','kostenloses-girokonto'])

    # ---------- 3. Kostenloses Girokonto ----------
    grow=[(L(k),E(G.cashT(k)),E(G.fwT(k)),f'{G.de1(k["stars"])} ★') for k in gratis]
    crow=[(L(k),E(G.kfT(k)),f'{eur(k["gratis"]["eingang_min"])} €',E(f'unter {k["gratis"]["alter_unter"]} Jahren' if k['gratis'].get('alter_unter') else 'nein'),f'{G.de1(k["stars"])} ★') for k in bedingt]
    nonl=all(k.get('eroeffnung')=='online' for k in gratis)
    art('de','kostenloses-girokonto',
      h1='Kostenloses Girokonto in Deutschland: Worauf du achten musst',
      mt='Kostenloses Girokonto Deutschland: Bedingungen und Kostenfallen | Finvallo',
      desc=f'Kostenloses Girokonto in Deutschland: {len(gratis)} Konten ohne Bedingung, {len(bedingt)} gratis mit Geldeingang oder unter einem bestimmten Alter. Welche Kosten trotzdem anfallen.',
      about='Girokonten in Deutschland',
      lede='Viele Banken werben mit dem kostenlosen Girokonto. Oft gilt das aber nur mit einer Bedingung, und manche Kosten stehen erst im Preisverzeichnis.',
      kurz=(f'Im Vergleich sind {len(gratis)} Konten für alle ohne jede Bedingung kostenlos{", alle zum Eröffnen online" if nonl else ""}. '
            f'{len(bedingt)} weitere werden gratis, wenn genug Geld eingeht, je nach Bank ab {eur(bedingt[0]["gratis"]["eingang_min"])} bis {eur(bedingt[-1]["gratis"]["eingang_min"])} € im Monat. Bei vielen reicht auch ein Alter unter 28 oder 30 Jahren. '
            'Achte außerdem auf Abhebungen, die girocard, Zahlungen in fremder Währung und den Dispo.'),
      secs=[
       ('Kostenlos ohne Bedingung',_tbl(['Konto','Bargeld','Fremdwährung','Bewertung'],grow)+
        f'<div class="prose"><p>Diese Konten kosten keine Kontoführung, egal wie viel Geld eingeht. Beim Bargeld gibt es oft Grenzen. Die Rangfolge steht in der Bestenliste <a href="{B}kostenlos/">kostenlose Girokonten</a>.</p></div>'),
       ('Gratis mit Geldeingang oder bis zu einem Alter',_tbl(['Konto','Sonst','Gratis ab Eingang pro Monat','Oder gratis','Bewertung'],crow)+
        f'<div class="prose"><p>Wichtig ist, was als Eingang zählt. Manche Banken zählen jeden Eingang, andere nur Gehalt oder Überweisungen von fremden Konten. Das steht beim Konto. Fällt der Eingang weg, etwa in Elternzeit oder bei Jobwechsel, zahlst du den vollen Preis. Mehr dazu in der Bestenliste <a href="{B}gehaltskonto/">Gehaltskonten</a>.</p></div>'),
       ('Die versteckten Kosten',f'''<div class="prose"><ul>
<li><b>Abhebungen.</b> Manche Konten haben nur wenige Gratis-Abhebungen pro Monat oder erst ab einem Mindestbetrag. An fremden Automaten kann es teuer werden.</li>
<li><b>girocard.</b> Oft ist nur eine Visa- oder Mastercard-Debitkarte dabei. Die girocard kostet bei manchen Banken extra.</li>
<li><b>Fremdwährung.</b> Außerhalb des Euroraums verlangen viele Banken einen Aufschlag auf jeden Einkauf, manche nichts.</li>
<li><b>Dispo.</b> Eine gesetzliche Obergrenze für Dispozinsen gibt es nicht. Im Vergleich liegen sie je nach Konto bei {G.pct(min(zs))} bis {G.pct(max(zs))} im Jahr. Bist du sechs Monate am Stück im Schnitt mit mehr als 75 % des Rahmens im Minus, muss dir die Bank eine Beratung anbieten (§ 504a BGB).</li>
<li><b>Einzelne Buchungen.</b> Beleghafte Überweisungen, Aufträge in der Filiale oder Ersatzkarten kosten oft extra.</li>
<li><b>Prämien.</b> Eine Prämie für die Eröffnung ist kein Dauerzustand. Entscheidend ist, was das Konto danach kostet.</li></ul></div>'''),
       ('So findest du das günstigste Konto für dich',f'''<div class="prose"><p>Im <a href="{G1}">Girokonto-Vergleich</a> gibst du deinen Geldeingang, dein Alter und deine Abhebungen pro Monat ein. Wir prüfen bei jedem Konto die Gratis-Bedingung und rechnen die Kosten für ein Jahr. Brauchst du eine Filiale, findest du die besten Konten in der Liste <a href="{B}filiale/">Konten mit Filiale</a>. Für junge Leute gibt es eigene Listen: <a href="{B}studenten/">Studierende und Azubis</a>, <a href="{B}jugend/">Jugendliche</a> und <a href="{B}kinder/">Kinder</a>.</p></div>'''),
       ('Quellen','''<div class="prose"><ul>
<li>Preise, Bedingungen, Bargeld und Fremdwährung: Entgeltinformationen und Preisverzeichnisse der Banken, verlinkt auf jeder Kontoseite. Die Werte werden beim Bauen dieser Seite aus den Kontodaten übernommen.</li>
<li>Beratung bei dauerhafter Überziehung: <a href="https://www.gesetze-im-internet.de/bgb/__504a.html" target="_blank" rel="noopener">§ 504a BGB ↗</a>.</li></ul></div>'''),
      ],
      faq=[
       ('Welche Girokonten sind in Deutschland wirklich kostenlos?',f'Ohne jede Bedingung kostenlos sind im Vergleich: {", ".join(k["name"]+" ("+k["bank"]+")" for k in gratis)}. Weitere {len(bedingt)} Konten sind mit Geldeingang oder bis zu einem bestimmten Alter gratis.'),
       ('Gibt es ein kostenloses Girokonto mit Filiale?','Bei Filialbanken ist die Kontoführung meist nur mit Bedingung gratis, etwa ab einem bestimmten Geldeingang oder für junge Leute. Die besten Konten mit Filiale stehen in der Bestenliste „Mit Filiale“.'),
       ('Was zählt als Geldeingang?','Das legt jede Bank selbst fest. Manche zählen jeden Eingang, andere nur Gehalt oder nur Überweisungen von Konten bei anderen Banken. Die genaue Bedingung steht auf jeder Kontoseite.'),
       ('Gibt es eine Obergrenze für Dispozinsen?','Nein, eine gesetzliche Obergrenze gibt es in Deutschland nicht. Bei dauerhafter hoher Überziehung muss dir die Bank aber eine Beratung anbieten.'),
      ],
      related=['girokonto-wechseln','basiskonto'])
