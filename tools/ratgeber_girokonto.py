# Ratgeber (nur AT) zu Girokonten: Konto wechseln, Basiskonto, kostenloses Girokonto.
# Zahlen zu Konten kommen live aus daten/at/girokonten.json (über girokonto.py).
# Rechtliches (Kontowechsel-Service §§ 14 bis 21 VZKG, Basiskonto) laut Arbeiterkammer und VZKG-Infoblatt der BAWAG,
# abgerufen am 27.10.2026. Abgrenzung: Bestenlisten = „welches Konto“, Ratgeber = „wie geht das, worauf achten“.
# Aufruf aus ratgeber.build('at'): register(art,P,eur)
import html
E=lambda s: html.escape(str(s)) if s is not None else ''
AK_WECHSEL='https://wien.arbeiterkammer.at/kontowechsel'
AK_BASIS='https://www.arbeiterkammer.at/beratung/konsument/Geld/Konto/Recht_auf_ein_Girokonto.html'
BAWAG_INFO='https://www.bawag.at/resource/blob/22272/9ee31cdf7ec055ec556e90d43c6a800d/infoblatt-vzkg-konto-data.pdf'
# Banken im Vergleich mit Sitz außerhalb Österreichs: für sie gilt der gesetzliche Kontowechsel-Service nicht
AUSLAND={'N26','Revolut','bunq','Trade Republic','Tomorrow','DKB'}

def _tbl(head,rows):
    h=''.join(f'<th>{c}</th>' for c in head)
    b=''.join('<tr>'+''.join(f'<td>{c}</td>' for c in r)+'</tr>' for r in rows)
    return f'<div class="tbl wide"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'
def _ext(u,t): return f'<a href="{E(u)}" target="_blank" rel="noopener">{E(t)} ↗</a>'

def register(art,P,eur):
    import girokonto as G
    G.K.use('at')
    d,ks=G.load('at')
    for k in ks: k.setdefault('geprueft',d['stand'])
    G.rate(ks)
    def L(k,label=None): return f'<a class="lnk" href="{P}at/girokonto/{k["slug"]}/">{E(label or k["name"])}</a> <small class="mut">({E(k["bank"])})</small>'
    alle=[k for k in ks if k['art'] in ('standard','premium')]
    pr=G.PROFIL['standard']
    cost=lambda k:G.kosten(k,pr['ein'],pr['alter'],pr['abh'])['total']
    gratis=sorted([k for k in alle if k['kf_jahr']==0],key=lambda k:-k['stars'])
    bedingt=sorted([k for k in alle if k.get('gratis') and k['gratis'].get('eingang_min') is not None and k['gratis'].get('kf_bedingt')==0],key=lambda k:k['gratis']['eingang_min'])
    filial=[k for k in alle if k.get('eroeffnung') in ('filiale','beides') and not k.get('gratis') and k['kf_jahr']>0]
    nnull=len([k for k in alle if cost(k)==0])
    teuer=max(filial,key=lambda k:k['kf_jahr']) if filial else None
    basis=sorted([k for k in ks if k['art']=='basis'],key=lambda k:k['kf_jahr'])
    G1=f'{P}at/girokonto/'; B=f'{G1}bestenlisten/'

    # ---------- 1. Konto wechseln ----------
    aus=sorted({k['bank'] for k in alle if k['bank'] in AUSLAND})
    art('at','girokonto-wechseln',
      h1='Girokonto wechseln in Österreich: So geht der Kontowechsel',
      mt='Girokonto wechseln in Österreich: Ablauf, Fristen, Kosten | Finvallo',
      desc='Girokonto wechseln in Österreich: Die neue Bank übernimmt laut Gesetz die Arbeit. Ablauf in 3 Schritten, Fristen, Kosten und was bei Online-Banken anders ist.',
      about='Girokonten in Österreich',
      lede='Ein Kontowechsel klingt nach viel Arbeit. Das meiste macht aber die neue Bank für dich, so steht es im Gesetz.',
      kurz=('Wechselst du zwischen zwei Banken mit Sitz in Österreich, hilft dir der gesetzliche Kontowechsel-Service (§§ 14 bis 21 Verbraucherzahlungskontogesetz). '
            'Du gibst der neuen Bank einen schriftlichen Auftrag. Sie holt die Daten von der alten Bank, richtet Daueraufträge ein und informiert auf Wunsch deinen Arbeitgeber und andere Zahler. '
            'Die Übermittlung der Daten ist kostenlos, und die Kündigungsfrist beim alten Konto darf höchstens einen Monat betragen.'),
      secs=[
       ('So läuft der Wechsel ab',f'''<div class="prose"><ol>
<li><b>Neues Konto eröffnen.</b> Such dir ein Konto aus, das zu dir passt. Im <a href="{G1}">Girokonto-Vergleich</a> rechnest du mit deinem Gehalt und deinen Abhebungen aus, was jedes Konto im Jahr kostet.</li>
<li><b>Kontowechsel beauftragen.</b> Du gibst der neuen Bank eine schriftliche Ermächtigung und bekommst eine Kopie. Darin legst du fest, welche Daueraufträge, Lastschriften und Eingänge übertragen werden und wann das alte Konto schließen soll.</li>
<li><b>Abwarten und prüfen.</b> Die Banken tauschen die Daten aus. Danach prüfst du, ob Gehalt, Miete und Abbuchungen auf dem neuen Konto ankommen. Erst dann sollte das alte Konto schließen.</li></ol></div>'''),
       ('Die Fristen laut Gesetz',_tbl(['Schritt','Wer','Frist'],[
            ('Die neue Bank fragt bei der alten Bank an','neue Bank','2 Geschäftstage nach deinem Auftrag'),
            ('Die alte Bank schickt die Daten: Daueraufträge, Lastschriften und regelmäßige Eingänge der letzten 13 Monate, etwa Gehalt, Pension oder Familienbeihilfe','alte Bank','5 Geschäftstage'),
            ('Die neue Bank richtet die Aufträge ein und informiert Zahler und Empfänger','neue Bank','5 Geschäftstage')])+
        '<div class="prose"><p>Zusammen sind das etwa 12 Geschäftstage, also gut zwei Wochen. Willst du deinen Arbeitgeber und andere Zahler lieber selbst informieren, muss dir die Bank dafür Musterbriefe geben.</p></div>'),
       ('Was der Wechsel kostet','''<div class="prose"><p>Für die Übermittlung deiner Daten darf keine Bank etwas verlangen. Für weitere Leistungen darf sie nur dann etwas verrechnen, wenn das im Kontovertrag ausdrücklich steht und der Betrag angemessen ist. Bis zur Schließung darf die alte Bank die Kontoführung nur anteilig verrechnen. Ist das alte Konto im Minus, musst du es zuerst ausgleichen, sonst kann es nicht geschlossen werden.</p></div>'''),
       ('Wechsel zu einer Online-Bank aus dem Ausland',f'''<div class="prose"><p>Der gesetzliche Service gilt nur, wenn <b>beide Banken ihren Sitz in Österreich</b> haben. Im Vergleich betrifft das {E(G.K.fmtl(aus) if hasattr(G.K,"fmtl") else ", ".join(aus))}. Wechselst du zu einer Bank in einem anderen EU-Land, muss dir deine österreichische Bank die nötigen Daten kostenlos geben. Die Daueraufträge richtest du dann gemeinsam mit der neuen Bank ein, meist selbst in der App.</p>
<p>Manche dieser Banken geben dir keine österreichische IBAN, sondern eine aus Deutschland, Litauen oder den Niederlanden. Welche IBAN du bekommst, steht auf jeder Kontoseite. Laut SEPA-Verordnung der EU dürfen Arbeitgeber und Firmen eine IBAN aus einem anderen EU-Land nicht ablehnen.</p></div>'''),
       ('Checkliste für den Wechsel','''<div class="prose"><ul class="checks">
<li>Gehalt oder Pension: Hat der Arbeitgeber oder die Pensionsversicherung die neue IBAN?</li>
<li>Familienbeihilfe, Kinderbetreuungsgeld, Arbeitslosengeld: Ist das Finanzamt oder das AMS informiert?</li>
<li>Miete, Strom, Handy, Versicherungen, Abos: Laufen die Lastschriften über das neue Konto?</li>
<li>Daueraufträge: Sind alle beim neuen Konto eingerichtet?</li>
<li>Karten: Sind Bankomatkarte und Kreditkarte, die am alten Konto hängen, ersetzt? Hinterlegte Karten bei Online-Shops und Apps ändern.</li>
<li>Altes Konto: Ist es ausgeglichen, und ist der Schließungstermin so gewählt, dass noch ein Monat Puffer bleibt?</li></ul></div>'''),
       ('Lohnt sich der Wechsel?',f'''<div class="prose"><p>Bei {nnull} der {len(alle)} Konten für alle im Vergleich zahlst du mit {eur(pr["ein"])} € Gehalt und {pr["abh"]} Abhebungen pro Monat nichts für die Kontoführung. Ein Konto mit festem Preis ohne Gratis-Modell kostet dagegen bis zu {eur(teuer["kf_jahr"]) if teuer else "keine Angabe"} € im Jahr{f" ({L(teuer)})" if teuer else ""}. Wer viel in der Filiale erledigt, zahlt dafür meist etwas mehr. Wer alles in der App macht, kommt fast immer günstiger weg.</p>
<p>Passende Listen: <a href="{B}kostenlos/">kostenlose Girokonten</a>, <a href="{B}gehaltskonto/">Gehaltskonten</a> und <a href="{B}filiale/">Konten mit Filiale</a>.</p></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Ablauf, Fristen, Kosten und Kündigung: Arbeiterkammer Wien, {_ext(AK_WECHSEL,"Girokonto wechseln: Das sollten Sie wissen")}, abgerufen am 27.10.2026. Gesetzliche Grundlage: §§ 14 bis 21 Verbraucherzahlungskontogesetz (VZKG).</li>
<li>Kontopreise und IBAN: Entgeltinformationen der Banken, verlinkt auf jeder Kontoseite.</li></ul></div>'''),
      ],
      faq=[
       ('Wie lange dauert ein Kontowechsel in Österreich?','Mit dem gesetzlichen Kontowechsel-Service etwa 12 Geschäftstage: 2 Tage für die Anfrage der neuen Bank, 5 Tage für die Daten der alten Bank und 5 Tage zum Einrichten der Aufträge.'),
       ('Was kostet ein Kontowechsel?','Die Übermittlung deiner Daten ist kostenlos. Die alte Bank darf die Kontoführung bis zur Schließung nur anteilig verrechnen. Weitere Entgelte sind nur erlaubt, wenn sie im Vertrag stehen und angemessen sind.'),
       ('Muss ich meinem Arbeitgeber selbst die neue IBAN geben?','Nein, das kann die neue Bank im Rahmen des Kontowechsel-Service für dich erledigen. Du kannst es aber auch selbst machen, die Bank muss dir dafür Musterbriefe geben.'),
       ('Gilt der Kontowechsel-Service auch für N26 oder Revolut?','Nein. Der gesetzliche Service gilt nur, wenn beide Banken ihren Sitz in Österreich haben. Bei einem Wechsel in ein anderes EU-Land muss dir deine Bank die Daten aber kostenlos geben.'),
       ('Wie lange ist die Kündigungsfrist beim alten Konto?','Höchstens einen Monat. Den Schließungstermin bestimmst du selbst. Ein Konto im Minus muss zuerst ausgeglichen werden.'),
      ],
      related=['basiskonto','kostenloses-girokonto'])

    # ---------- 2. Basiskonto ----------
    brow=[(L(k),E(G.kfT(k)),f'{eur(k["kf_jahr"])} €',E(G.wegT(k))) for k in basis]
    art('at','basiskonto',
      h1='Basiskonto in Österreich: Das Recht auf ein Konto für alle',
      mt='Basiskonto Österreich: Anspruch, Kosten, Ablehnung | Finvallo',
      desc='Basiskonto in Österreich: Wer Anspruch hat, was es höchstens kosten darf (83,45 €, ermäßigt 41,73 € im Jahr), was dabei ist und wann die Bank ablehnen darf.',
      about='Girokonten in Österreich',
      lede='Ohne Konto geht heute fast nichts. Deshalb hat in Österreich jede und jeder das Recht auf ein Basiskonto, auch mit Schulden oder im Privatkonkurs.',
      kurz=('Seit September 2016 darf jede Verbraucherin und jeder Verbraucher mit rechtmäßigem Aufenthalt in der EU bei einer österreichischen Bank ein Basiskonto eröffnen. '
            'Die Kontoführung darf laut Arbeiterkammer höchstens 83,45 € im Jahr kosten, für besonders schutzbedürftige Personen auf Antrag höchstens 41,73 €. '
            'Die Bank muss das Konto innerhalb von 10 Geschäftstagen eröffnen und darf nur aus zwei Gründen ablehnen.'),
      secs=[
       ('Wer Anspruch hat','''<div class="prose"><p>Anspruch hat jede Verbraucherin und jeder Verbraucher mit rechtmäßigem Aufenthalt in der EU, egal wo sie oder er wohnt. Auch Menschen ohne Aufenthaltsrecht, die aus rechtlichen oder tatsächlichen Gründen nicht abgeschoben werden können, haben Anspruch. Schlechte Bonität, Schulden oder ein Privatkonkurs sind kein Grund für eine Ablehnung. Das Basiskonto ist für Privatpersonen gedacht, nicht für Firmen.</p></div>'''),
       ('Was ein Basiskonto kann','''<div class="prose"><ul class="checks">
<li>Geld einzahlen und abheben, mit Bankomatkarte</li>
<li>Überweisungen, Daueraufträge und Lastschriften</li>
<li>mit der Karte im Geschäft und online zahlen</li>
<li>Online-Banking, wenn die Bank es anbietet</li></ul>
<p>Nicht dabei sind ein Überziehungsrahmen und eine Kreditkarte. Du kannst also nicht ins Minus gehen.</p></div>'''),
       ('Was es kosten darf','''<div class="prose"><p>Laut Arbeiterkammer darf die Kontoführung höchstens <b>83,45 € im Jahr</b> kosten. Für sozial oder wirtschaftlich besonders schutzbedürftige Personen gilt auf Antrag eine Grenze von <b>41,73 € im Jahr</b>. Dazu zählen unter anderem:</p><ul>
<li>Menschen mit Mindestsicherung</li>
<li>Menschen mit Ausgleichszulage zur Pension oder einer Pension in dieser Höhe</li>
<li>Menschen mit Arbeitslosengeld oder Notstandshilfe in dieser Höhe</li>
<li>Studierende mit Studienbeihilfe</li>
<li>Lehrlinge mit niedriger Lehrlingsentschädigung</li>
<li>Menschen mit Befreiung von der Rundfunkgebühr</li>
<li>Menschen im Schuldenregulierungsverfahren (Privatkonkurs)</li>
<li>Obdachlose, Asylwerberinnen und Asylwerber</li></ul>
<p>Den ermäßigten Preis bekommst du nur, wenn du ihn bei der Bank beantragst und nachweist.</p></div>'''),
       ('Basiskonten im Vergleich',_tbl(['Konto','Kontoführung','Im Jahr','Eröffnung'],brow)+
        f'<div class="prose"><p>Die meisten Banken verlangen 80 € im Jahr, die Wüstenrot Bank weniger. Die Preise stammen aus den Entgeltinformationen der Banken. Alle Basiskonten stehen auch im <a href="{G1}">Girokonto-Vergleich</a>. Bei vielen Banken eröffnest du das Basiskonto nur in der Filiale.</p></div>'),
       ('Wann die Bank ablehnen darf','''<div class="prose"><p>Nur in zwei Fällen:</p><ol>
<li>Du hast in Österreich schon ein Girokonto, mit dem du die gleichen Zahlungen machen kannst. Ausnahme: Das Konto wurde gekündigt oder du hast es selbst gekündigt und kannst das zeigen.</li>
<li>Gegen dich läuft ein Strafverfahren wegen einer Straftat gegen die Bank oder ihre Mitarbeitenden, oder du wurdest dafür verurteilt und die Strafe ist noch nicht getilgt.</li></ol>
<p>Eine Ablehnung muss die Bank schriftlich begründen. Sie muss dich auch darauf hinweisen, dass du dich bei der Finanzmarktaufsicht (FMA) oder bei der Schlichtungsstelle beschweren kannst. Bei Verdacht auf Geldwäsche gelten außerdem eigene Regeln.</p></div>'''),
       ('Wann die Bank kündigen darf','''<div class="prose"><p>Laut VZKG-Infoblatt der BAWAG darf eine Bank ein Basiskonto zum Beispiel kündigen, wenn 24 Monate lang keine Zahlungen über das Konto liefen, wenn du keinen rechtmäßigen Aufenthalt in der EU mehr hast, wenn du ein zweites Girokonto in Österreich eröffnet hast oder wenn das Konto absichtlich für illegale Zwecke genutzt wurde.</p></div>'''),
       ('So kommst du zum Basiskonto',f'''<div class="prose"><ol>
<li>Such dir eine Bank aus der Tabelle aus und frag ausdrücklich nach dem „Basiskonto“ oder „Zahlungskonto mit grundlegenden Funktionen“.</li>
<li>Bring einen Ausweis mit. Wenn du den ermäßigten Preis willst, auch einen Nachweis, etwa den Bescheid über Mindestsicherung oder Studienbeihilfe.</li>
<li>Die Bank muss das Konto spätestens 10 Geschäftstage nach dem vollständigen Antrag eröffnen.</li></ol>
<p>Laut einer Prüfung der Arbeiterkammer Wien vom Februar 2026 informieren Banken nicht immer richtig über das Basiskonto. Bestehe auf deinem Recht, und wende dich an die Arbeiterkammer, wenn es Probleme gibt.</p></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Anspruch, Höchstentgelt, Leistungen, Ablehnung, Frist: Arbeiterkammer, {_ext(AK_BASIS,"Bankkonto für Jedermann")}, abgerufen am 27.10.2026.</li>
<li>Schutzbedürftige Personen (Verordnung BGBl II 255/2016) und Kündigungsgründe: {_ext(BAWAG_INFO,"BAWAG, Information zum Verbraucherzahlungskonto (VZKG-Konto)")}.</li>
<li>Preise der Basiskonten: Entgeltinformationen der Banken, verlinkt auf jeder Kontoseite.</li></ul></div>'''),
      ],
      faq=[
       ('Wer hat Anspruch auf ein Basiskonto in Österreich?','Jede Verbraucherin und jeder Verbraucher mit rechtmäßigem Aufenthalt in der EU, auch mit Schulden, schlechter Bonität oder im Privatkonkurs. Auch Menschen, die nicht abgeschoben werden können, haben Anspruch.'),
       ('Was kostet ein Basiskonto?','Laut Arbeiterkammer höchstens 83,45 € im Jahr. Für besonders schutzbedürftige Personen, etwa mit Mindestsicherung oder Studienbeihilfe, auf Antrag höchstens 41,73 € im Jahr. Die meisten Banken im Vergleich verlangen 80 € im Jahr.'),
       ('Kann ich mit einem Basiskonto ins Minus gehen?','Nein. Ein Basiskonto hat keinen Überziehungsrahmen und keine Kreditkarte.'),
       ('Darf mir die Bank ein Basiskonto verweigern?','Nur wenn du in Österreich schon ein nutzbares Girokonto hast oder wegen einer Straftat gegen die Bank angeklagt oder verurteilt bist. Die Ablehnung muss schriftlich begründet werden.'),
       ('Wie schnell muss die Bank das Basiskonto eröffnen?','Spätestens 10 Geschäftstage, nachdem dein vollständiger Antrag bei der Bank eingegangen ist.'),
      ],
      related=['girokonto-wechseln','kostenloses-girokonto'])

    # ---------- 3. Kostenloses Girokonto ----------
    grow=[(L(k),E(G.cashT(k)),E(G.fwT(k)),E(G.ibanT(k)),f'{G.de1(k["stars"])} ★') for k in gratis]
    crow=[(L(k),E(G.kfT(k)),f'{eur(k["gratis"]["eingang_min"])} €',E(G.wegT(k)),f'{G.de1(k["stars"])} ★') for k in bedingt]
    zs=[k.get('ueberschreitung') or k.get('sollzins') for k in alle if (k.get('ueberschreitung') or k.get('sollzins'))]
    zmin,zmax=min(zs),max(zs)
    nonl=all(k.get('eroeffnung')=='online' for k in gratis)
    zahl=lambda n:{1:'ein',2:'zwei',3:'drei',4:'vier',5:'fünf',6:'sechs',7:'sieben',8:'acht',9:'neun',10:'zehn'}.get(n,str(n))
    art('at','kostenloses-girokonto',
      h1='Kostenloses Girokonto in Österreich: Worauf du achten musst',
      mt='Kostenloses Girokonto Österreich: Bedingungen und Kostenfallen | Finvallo',
      desc=f'Kostenloses Girokonto in Österreich: {len(gratis)} Konten ohne Bedingung, {len(bedingt)} gratis mit Gehaltseingang. Welche Kosten trotzdem anfallen und wie du sie vermeidest.',
      about='Girokonten in Österreich',
      lede='„Gratis“ heißt bei Girokonten nicht immer gratis. Oft hängt es an einer Bedingung, und manche Kosten kommen erst später.',
      kurz=(f'Im Vergleich sind {len(gratis)} Konten für alle ohne jede Bedingung kostenlos{", alle von Online-Banken" if nonl else ""}. '
            f'{len(bedingt)} weitere Konten werden gratis, wenn jeden Monat genug Geld eingeht, je nach Bank ab {eur(bedingt[0]["gratis"]["eingang_min"])} bis {eur(bedingt[-1]["gratis"]["eingang_min"])} €. '
            'Achte außerdem auf Kosten für Abhebungen, die Debitkarte, Zahlungen in fremder Währung und das Überziehen.'),
      secs=[
       ('Kostenlos ohne Bedingung',_tbl(['Konto','Bargeld','Fremdwährung','IBAN','Bewertung'],grow)+
        f'<div class="prose"><p>Diese Konten kosten nichts, egal wie viel Geld eingeht. Sie haben aber oft Grenzen beim Bargeld, und nicht alle geben dir eine österreichische IBAN. Die Rangfolge steht in der Bestenliste <a href="{B}kostenlos/">kostenlose Girokonten</a>.</p></div>'),
       ('Gratis mit Gehalt oder Pension',_tbl(['Konto','Sonst','Gratis ab Eingang pro Monat','Eröffnung','Bewertung'],crow)+
        f'<div class="prose"><p>Wichtig ist, was als Eingang zählt. Manche Banken zählen nur Gehalt oder Pension, andere jeden Eingang. Das steht beim Konto. Fällt der Eingang einmal weg, etwa in Karenz oder bei Jobwechsel, zahlst du den vollen Preis. Mehr dazu in der Bestenliste <a href="{B}gehaltskonto/">Gehaltskonten</a>.</p></div>'),
       ('Die versteckten Kosten',f'''<div class="prose"><ul>
<li><b>Abhebungen.</b> Manche Konten haben nur wenige Gratis-Abhebungen pro Monat, danach kostet jede bis zu 3 €. Wer oft Bargeld braucht, zahlt so schnell mehr als für ein Konto mit Kontoführungsgebühr.</li>
<li><b>Debitkarte.</b> Bei einigen Konten kostet die Karte extra, oder nur eine virtuelle Karte ist gratis.</li>
<li><b>Fremdwährung.</b> Zahlst du außerhalb des Euroraums, verlangen viele Banken einen Aufschlag auf jeden Einkauf. Einige Online-Banken verlangen nichts.</li>
<li><b>Überziehen.</b> Geht das Konto ins Minus, kostet das Zinsen. Im Vergleich sind das je nach Konto {G.pct(zmin) if hasattr(G,"pct") else zmin} bis {G.pct(zmax) if hasattr(G,"pct") else zmax} im Jahr.</li>
<li><b>Einzelne Buchungen.</b> Bei manchen Konten kosten Überweisungen am Schalter, Papier-Kontoauszüge oder eine Ersatzkarte extra.</li>
<li><b>Aktionen.</b> „Im ersten Jahr gratis“ ist kein Gratis-Konto. Danach zahlst du den normalen Preis.</li></ul></div>'''),
       ('So findest du das günstigste Konto für dich',f'''<div class="prose"><p>Ein Konto ist nur dann günstig, wenn es zu deinem Alltag passt. Im <a href="{G1}">Girokonto-Vergleich</a> gibst du deinen Geldeingang, dein Alter und deine Abhebungen pro Monat ein. Wir prüfen dann bei jedem Konto die Gratis-Bedingung und rechnen die Kosten für ein Jahr aus. Brauchst du eine Filiale, findest du die besten Konten in der Liste <a href="{B}filiale/">Konten mit Filiale</a>.</p>
<p>Für Studierende, Jugendliche und Kinder gibt es eigene Konten, die meist gratis sind: <a href="{B}studenten/">Studentenkonten</a>, <a href="{B}jugend/">Jugendkonten</a> und <a href="{B}kinder/">Kinderkonten</a>.</p></div>'''),
       ('Quellen','''<div class="prose"><ul>
<li>Preise, Bedingungen, Bargeld, Fremdwährung und IBAN: Entgeltinformationen und Preislisten der Banken, verlinkt auf jeder Kontoseite. Die Werte werden beim Bauen dieser Seite aus den Kontodaten übernommen.</li></ul></div>'''),
      ],
      faq=[
       ('Welche Girokonten sind in Österreich wirklich kostenlos?',f'Ohne jede Bedingung kostenlos sind im Vergleich: {", ".join(k["name"]+" ("+k["bank"]+")" for k in gratis)}. Weitere {len(bedingt)} Konten sind mit regelmäßigem Geldeingang gratis.'),
       ('Gibt es ein kostenloses Girokonto mit Filiale?','Bei Banken mit Filiale ist die Kontoführung meist nur für Studierende, Jugendliche und Kinder gratis oder nur mit Bedingung. Die besten Konten mit Filiale stehen in der Bestenliste „Mit Filiale“.'),
       ('Was zählt als Geldeingang für ein Gratis-Konto?','Das legt jede Bank selbst fest. Manche zählen nur Gehalt oder Pension, andere jeden Eingang. Die genaue Bedingung steht auf jeder Kontoseite.'),
       ('Ist ein Konto mit deutscher IBAN ein Problem?','Laut SEPA-Verordnung der EU dürfen Arbeitgeber und Firmen eine IBAN aus einem anderen EU-Land nicht ablehnen. Bei manchen Behörden oder Formularen kann es trotzdem länger dauern.'),
      ],
      related=['girokonto-wechseln','basiskonto'])
