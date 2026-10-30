# Erklärtexte für die Girokonto-Bestenlisten: gemeinschaftskonto, studenten, jugendkonto, kinderkonto (DE und AT).
# Aufruf aus girokonto.texte(land, ctx). Zahlen zu Konten kommen immer aus ctx, nie fest im Text.
# Übernimmt die Inhalte der früheren Ratgeber "Gemeinschaftskonto" und "Kinderkonto und Jugendkonto" (ratgeber_konto.py, ratgeber_konto_de.py).
# Rechtliches laut gesetze-im-internet.de, RIS, BMF, oesterreich.gv.at, BaFin und Arbeiterkammer, abgerufen am 29.10.2026,
# Ergänzungen für jugendkonto/kinderkonto (§§ 107, 113, 312g, 355 BGB, §§ 2, 5 JArbSchG, § 17 BBiG, § 32d EStG, oesterreich.gv.at) abgerufen am 30.10.2026.
import html,re

E=lambda s: html.escape(str(s)) if s is not None else ''
ABG='abgerufen am 29.10.2026'

# ---------- Quellen ----------
DE_BGB=lambda n: f'https://www.gesetze-im-internet.de/bgb/__{n}.html'
DE_ERBST=lambda n: f'https://www.gesetze-im-internet.de/erbstg_1974/__{n}.html'
DE_ZPO_850L='https://www.gesetze-im-internet.de/zpo/__850l.html'
DE_EINSIG='https://www.gesetze-im-internet.de/einsig/__8.html'
DE_BAFIN_ES='https://www.bafin.de/DE/verbraucherinnen-verbraucher/themen-finanzprodukte/geldanlage/einlagensicherung-anlegerentschaedigung/einlagensicherung-anlegerentschaedigung_node.html'
DE_BAFIN_DISPO='https://www.bafin.de/SharedDocs/FAQs/DE/Verbraucher/Bank/Produkte/Girokonto/DispoUeberziehungskredit/03_dispokredit_streichung_reduzierung.html'
DE_BAFIN_BASIS='https://www.bafin.de/DE/verbraucherinnen-verbraucher/themen-finanzprodukte/konten-zahlungen/konten/basiskonto/basiskonto_node.html'
DE_AO_154='https://www.gesetze-im-internet.de/ao_1977/__154.html'
DE_ESTG=lambda n: f'https://www.gesetze-im-internet.de/estg/__{n}.html'
DE_ZKG=lambda n: f'https://www.gesetze-im-internet.de/zkg/__{n}.html'
DE_GWG_12='https://www.gesetze-im-internet.de/gwg_2017/__12.html'
DE_SPERR='https://www.sperr-notruf.de/'
DE_BAFOEG='https://www.bafoeg-digital.de/'
EU_SEPA='https://eur-lex.europa.eu/eli/reg/2012/260/oj'
AT_ABGB_170='https://www.ris.bka.gv.at/Dokumente/Bundesnormen/NOR40146782/NOR40146782.pdf'
AT_GESCH='https://www.oesterreich.gv.at/de/themen/gesetze_und_recht/gerichtsorganisation_der_justiz/zivilrecht/8/Seite.1740386'
AT_BMF_SCHENK='https://www.bmf.gv.at/themen/steuern/steuern-von-a-bis-z/schenkungsmeldung.html'
AT_BMF_KEST='https://www.bmf.gv.at/themen/steuern/sparen-veranlagen/besteuerung-kapitalertraege-inland.html'
AT_BMF_KAP='https://www.bmf.gv.at/themen/steuern/sparen-veranlagen/information-zu-einkuenften-aus-kapitalvermoegen.html'
AT_ES='https://www.einlagensicherung.at/'
AT_BAWAG_ES='https://www.bawag.at/resource/blob/20382/0b242f44d97223b74e0fbe9675a27bb5/info-einlagensicherung-anlegerentschaedigung-data.pdf'
AT_AK_FAQ='https://wien.arbeiterkammer.at/beratung/konsumentenschutz/geld/konto/FAQ_Girokonten_2023.pdf'
AT_AK_JUGEND='https://ooe.arbeiterkammer.at/beratung/konsumentenschutz/geld/konto/Jugend--Lehrlingskonten-im-Vergleich.html'
AT_AK_RECHT='https://www.arbeiterkammer.at/beratung/konsument/Geld/Konto/Recht_auf_ein_Girokonto.html'
AT_AK_WECHSEL='https://wien.arbeiterkammer.at/kontowechsel'
AT_BANKENRECHNER='https://bankenrechner.arbeiterkammer.at/'
AT_VKRG='https://ris.bka.gv.at/Dokumente/BgblAuth/BGBLA_2026_I_36/BGBLA_2026_I_36.pdf'
AT_OEAD='https://oead.at/de/'

# ---------- Helfer ----------
def _ext(u,t): return f'<a href="{E(u)}" target="_blank" rel="noopener">{E(t)}</a>'
def _P(*ps): return '<div class="prose">'+''.join(p if re.match(r'\s*<(ul|ol|div|table)',p) else f'<p>{p.strip()}</p>' for p in ps if p and p.strip())+'</div>'
def _ul(items,cls=''): return f'<ul{" class="+chr(34)+cls+chr(34) if cls else ""}>'+''.join(f'<li>{x}</li>' for x in items)+'</ul>'
def _tbl(head,rows):
    h=''.join(f'<th>{x}</th>' for x in head)
    b=''.join('<tr>'+''.join(f'<td>{x}</td>' for x in r)+'</tr>' for r in rows)
    return f'<div class="tbl wide"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'
def _fmtl(L,und='und'):
    L=list(L)
    return ', '.join(L[:-1])+f' {und} '+L[-1] if len(L)>1 else (L[0] if L else '')
def _clean(s): return re.sub('\\s*[\u2013\u2014]\\s*',' - ',str(s or '')).strip()
def _txt(s,n=None):
    s=_clean(s)
    if n and len(s)>n: s=s[:n].rsplit(' ',1)[0].rstrip(',;:')+' …'
    return E(s)
def _banks(X):
    out=[]
    for k in X:
        if k['bank'] not in out: out.append(k['bank'])
    return out
def _kost(c,k): return c['eur'](k['score']['kosten']['total'])+' €'
def _dk(k): return (k.get('debitkarte') or {}).get('text') or ''
def _alt(k): return (k.get('alter') or {}).get('text') or ''
def _gtxt(k): return (k.get('gratis') or {}).get('text') or ''
def _all(k): return ' '.join([_alt(k),_gtxt(k),(k.get('gratis') or {}).get('sonst') or '',_dk(k),k.get('kreditkarte') or ''])
def _links(c,X,n=None): return _fmtl([c['link'](k) for k in (X[:n] if n else X)])
def _bed(k): return _gtxt(k) or _alt(k) or 'keine Angabe'
def _jung(c):
    return sorted([k for k in c['alle'] if k['art'] in ('standard','premium') and (k.get('gratis') or {}).get('alter_unter') and k['gratis'].get('kf_bedingt')==0],
                  key=lambda k:(-k['gratis']['alter_unter'],-k['stars']))
def _n(n,s,p): return f'{n} {s if n==1 else p}'
def _w(n,one,many): return one if n==1 else f'{n} {many}'


# =====================================================================
# Gemeinschaftskonto Deutschland
# =====================================================================
def _gem_de(c):
    X=c['lists'].get('gemeinschaftskonto') or []
    L=c['link']; eur=c['eur']; pct=c['pct']; rg=c['rg']; li=c['liste']
    n=len(X); B=_banks(X)
    frei0=[k for k in X if k['kf_jahr']==0]
    bed=[k for k in X if k['kf_jahr']>0 and (k.get('gratis') or {}).get('kf_bedingt')==0]
    billig=sorted(X,key=lambda k:(k['score']['kosten']['total'],-k['stars']))
    ohne_dispo=[k for k in X if k.get('sollzins') is None]
    mit_dispo=sorted([k for k in X if k.get('sollzins') is not None],key=lambda k:k['sollzins'])
    uk=[k for k in X if (k.get('unterkonten') or 0)>=1]
    onl=[k for k in X if k.get('eroeffnung')=='online']; fil=[k for k in X if k.get('eroeffnung') in ('filiale','beides')]

    p_menge=(f'In der Liste oben stehen {n} Konten von {len(B)} Banken, die es laut Bank auch als Gemeinschaftskonto gibt. '
             +(f'{_n(len(frei0),"davon kostet","davon kosten")} ohne jede Bedingung nichts, ' if frei0 else '')
             +(f'{len(bed)} weitere sind gratis, sobald eine Bedingung wie ein monatlicher Geldeingang erfüllt ist.' if bed else 'die übrigen kosten eine feste Kontoführungsgebühr.')) if X else 'Welche Konten es auch als Gemeinschaftskonto gibt, steht in der Liste oben.'
    rows=[(L(k),_kost(c,k),E(c['kurzbed'](k)),_txt(_dk(k),120)) for k in billig[:10]]

    secs=[
     ('Oder-Konto oder Und-Konto: was ihr eigentlich unterschreibt',
      _tbl(['','Oder-Konto','Und-Konto'],[
        ('Wer darf Geld bewegen','jeder Inhaber allein','nur alle Inhaber zusammen'),
        ('Karte und App','meist je Inhaber eine eigene Karte und ein eigener Zugang','Karten gibt es selten, Aufträge brauchen alle Freigaben'),
        ('Rechtlich','Gesamtgläubiger (§ 428 BGB), jeder kann die ganze Summe fordern','gemeinschaftliche Verfügung'),
        ('Passt zu','Paaren, Familien, Wohngemeinschaften','Erbengemeinschaften, Vereinen, Geschäftspartnern'),
        ('Größtes Risiko','einer räumt das Konto leer oder überzieht es','nichts geht, wenn einer nicht mitmacht')])+
      _P('Wenn ihr bei der Eröffnung nichts anderes vereinbart, bekommt ihr ein Oder-Konto. Das ist im Alltag praktisch: Du zahlst die Miete, dein Partner den Wocheneinkauf, und keiner muss den anderen fragen. Genau das ist aber auch der Haken. Jeder von euch kann jederzeit das ganze Guthaben abheben, ohne dass die Bank nachfragt.',
         'Ein Und-Konto bieten vor allem Filialbanken an, und meist nur auf Nachfrage. Für ein Paar ist es unpraktisch, weil jede Überweisung beide Unterschriften braucht. Sinnvoll ist es, wenn ihr euch gegenseitig kontrollieren wollt, etwa bei einem gemeinsam geerbten Betrag.',
         'Es gibt noch eine dritte Lösung, die viele übersehen: das Einzelkonto mit Kontovollmacht. Dann gehört das Konto nur einer Person, die andere darf verfügen, haftet aber nicht und hat keinen Anteil am Guthaben. Das passt, wenn nur einer das Geld verdient oder wenn ihr Steuerfragen aus dem Weg gehen wollt.')),
     ('So eröffnet ihr ein Gemeinschaftskonto',
      _P('Die Eröffnung läuft wie bei einem Einzelkonto, nur doppelt. Beide Inhaber müssen sich ausweisen, weil das Geldwäschegesetz die Bank verpflichtet, jeden Vertragspartner zu identifizieren (§ 12 GwG). Bei Online-Banken geht das per Video oder in der Postfiliale, bei Filialbanken am Schalter.',
         _ul(['<b>Ausweis</b> beider Inhaber, bei Reisepass zusätzlich eine Meldebescheinigung.',
              '<b>Steuer-ID</b> beider Inhaber. Banken müssen sie für jeden Kontoinhaber erfassen (§ 154 Abs. 2a AO).',
              '<b>Schufa-Abfrage</b> bei beiden, wenn ihr einen Dispo oder eine Kreditkarte wollt. Für ein reines Guthabenkonto fragen manche Banken nur eine Identitätsprüfung an.',
              '<b>Unterschrift beider</b> unter dem Kontovertrag, online meist per Klick oder qualifizierter elektronischer Signatur.']),
         (f'Von den {n} Konten in der Liste kannst du {len(onl)} nur online eröffnen, {len(fil)} auch oder nur in der Filiale. ' if X else '')+
         'Bei manchen App-Banken ist das Gemeinschaftskonto kein eigener Vertrag, sondern ein Zusatz: Beide brauchen zuerst ein eigenes Konto bei der Bank, dann lädt einer den anderen ein. Rechne dafür ein paar Tage ein.',
         'Wer schon ein Einzelkonto hat, fragt am besten zuerst, ob die Bank einen zweiten Inhaber hinzufügen kann. Das spart die neue IBAN und damit die Mitteilung an Arbeitgeber, Vermieter und Versicherungen. Geht das nicht, hilft die gesetzliche Kontowechselhilfe beim Umzug der Daueraufträge.')),
     ('Was ein Gemeinschaftskonto kostet',
      _P(p_menge,
         (f'Am günstigsten sind im Standardfall {_links(c,billig,3)}. ' if len(billig)>=3 else '')+
         'Die Preise unten gelten für einen typischen Haushalt mit Gehaltseingang. Beim Gemeinschaftskonto zahlt ihr die Kontoführung nur einmal, nicht pro Person. Ein Gemeinschaftskonto für zwei ist deshalb oft billiger als zwei Einzelkonten, die beide eine Gebühr kosten.')+
      (_tbl(['Konto','Kosten pro Jahr im Standardfall','Gratis, wenn','Karten laut Bank'],rows) if rows else '')+
      _P('Zwei Dinge solltest du vorher klären. Erstens die Gratis-Bedingung: Verlangt die Bank einen Mindestgeldeingang, zählt beim Gemeinschaftskonto meist alles, was auf das Konto kommt, also beide Gehälter zusammen. Frag aber nach, ob Umbuchungen vom eigenen Tagesgeld mitzählen. Zweitens die zweite Karte: Bei manchen Banken ist die Partnerkarte inklusive, bei anderen kostet sie ein paar Euro im Jahr extra. Das steht in der Spalte Karten.')),
     ('Haftung: Ein Minus gehört euch beiden',
      _P('Alle Inhaber haften der Bank als Gesamtschuldner (§ 421 BGB). Ein Beispiel: Dein Partner überzieht das Konto um 2.400 €. Die Bank darf die vollen 2.400 € von dir verlangen, auch wenn du keinen Cent davon ausgegeben hast. Wie ihr das untereinander ausgleicht, ist eure Sache. Das gilt für den Dispo, für die geduldete Überziehung und für Gebühren.',
         ('Wer das Risiko klein halten will, lässt den Dispo auf dem Gemeinschaftskonto auf null setzen oder sehr niedrig halten. '
          +(f'Ganz ohne Dispo laufen in der Liste {_n(len(ohne_dispo),"Konto","Konten")}, zum Beispiel {_links(c,ohne_dispo,3)}. ' if ohne_dispo else '')
          +(f'Bei den anderen liegt der Dispozins zwischen {pct(mit_dispo[0]["sollzins"])} und {pct(mit_dispo[-1]["sollzins"])} im Jahr. ' if len(mit_dispo)>1 else ''))
         +f'Wie der Dispo funktioniert und wie du ihn kündigst, steht im Ratgeber {rg("dispo","Dispo")}.',
         'Die Haftung endet nicht mit der Beziehung. Solange ihr beide Inhaber seid, steht ihr für jedes Minus gerade, auch für eines, das nach der Trennung entsteht. Deshalb ist der Widerruf der Einzelverfügung (unten bei der Trennung) so wichtig.')),
     ('Schenkungsteuer: wann das Finanzamt die Hälfte zählt',
      _P('Auf einem Oder-Konto geht das Finanzamt davon aus, dass jedem Inhaber die Hälfte gehört. Zahlt einer eine Erbschaft, eine Abfindung oder den Erlös aus einem Wohnungsverkauf ein, kann die Hälfte als Schenkung an den anderen gelten. Der Bundesfinanzhof hat das bestätigt, die Beweislast aber dem Finanzamt gegeben: Es muss zeigen, dass der andere Partner wirklich frei über seine Hälfte verfügen durfte (Urteil vom 23.11.2011, II R 33/10).')+
      _tbl(['Verhältnis','Freibetrag in 10 Jahren (§ 16 ErbStG)','Steuersatz auf den ersten Euro darüber'],[
        ('Ehe oder eingetragene Lebenspartnerschaft','500.000 €','7 %'),
        ('Eltern an ihr Kind','400.000 €','7 %'),
        ('Unverheiratete Paare, Freunde, WG','20.000 €','30 %')])+
      _P('Für Ehepaare ist das selten ein Problem. Für unverheiratete Paare schon. Rechenbeispiel: Deine Partnerin erbt 80.000 € und überweist sie auf euer Oder-Konto. Wertet das Finanzamt die Hälfte als Schenkung an dich, sind das 40.000 €. Nach dem Freibetrag von 20.000 € bleiben 20.000 €, darauf fallen in Steuerklasse III 30 % an, also 6.000 €.',
         _ul(['Große Einmalbeträge bleiben auf dem Einzelkonto dessen, dem sie gehören. Der Partner bekommt bei Bedarf eine Vollmacht.',
              'Haltet schriftlich fest, wem welches Guthaben gehört, bevor das Geld eingeht.',
              'Nutzt das Gemeinschaftskonto als Haushaltskonto für laufende Ausgaben, nicht als gemeinsames Sparbuch.',
              'Eine Schenkung musst du dem Finanzamt innerhalb von drei Monaten anzeigen (§ 30 ErbStG), auch wenn am Ende keine Steuer anfällt.']))),
     ('Todesfall: Was mit dem gemeinsamen Konto passiert',
      _P('Stirbt ein Inhaber eines Oder-Kontos, wird das Konto nicht gesperrt. Der überlebende Partner kann weiter Miete zahlen und einkaufen. An die Stelle des Verstorbenen treten aber seine Erben. Sie haben dieselben Rechte wie er und können die Einzelverfügung des Überlebenden widerrufen. Sind die Erben andere Menschen als der Partner, etwa Kinder aus einer früheren Ehe, kann das schnell zum Streit führen.',
         'Die Hälfte des Guthabens gehört im Zweifel zum Nachlass. Die Bank meldet die Kontostände des Verstorbenen dem Finanzamt (§ 33 ErbStG). Für Ehepartner ist das meist steuerlich ohne Folgen, weil der Freibetrag von 500.000 € auch im Erbfall gilt. Unverheiratete Partner haben auch beim Erben nur 20.000 € frei, und nur, wenn sie überhaupt im Testament stehen. Ohne Testament erben sie gar nichts.',
         'Beim Und-Konto ist es schwieriger: Der Überlebende kann nur zusammen mit den Erben verfügen, und die müssen sich erst ausweisen, oft mit Erbschein. Bis dahin liegt das Geld fest. Wer vorsorgen will, gibt sich gegenseitig eine Kontovollmacht, die über den Tod hinaus gilt, und regelt den Rest im Testament.')),
     ('Trennung, Kündigung und Pfändung',
      _P(_ul(['<b>Einzelverfügung widerrufen.</b> Jeder Inhaber kann der Bank mitteilen, dass ab sofort nur noch beide gemeinsam verfügen dürfen. Das ist der erste Schritt, wenn eine Trennung ansteht, denn es verhindert, dass einer das Konto leerräumt oder ins Minus zieht.',
              '<b>Guthaben teilen.</b> Untereinander steht euch im Zweifel je die Hälfte zu (§ 430 BGB). Hebt einer mehr ab, muss er den Überschuss ausgleichen. Wer nachweisen kann, dass das Geld nur von ihm stammt, kann eine andere Aufteilung durchsetzen.',
              '<b>Minus ausgleichen.</b> Ein Konto im Minus schließt keine Bank. Bis der Saldo auf null steht, haftet ihr beide weiter.',
              '<b>Daueraufträge umziehen.</b> Miete, Strom, Handy, Versicherungen: Alles muss auf die neuen Einzelkonten. Die Kontowechselhilfe nach § 20 ZKG erledigt das für dich, Details im Ratgeber '+rg('girokonto-wechseln','Girokonto wechseln')+'.',
              '<b>Gemeinsam kündigen.</b> Schließen können das Konto nur alle Inhaber zusammen. Weigert sich einer, bleibt nur der Widerruf der Einzelverfügung, damit niemand mehr allein handeln kann.']),
         'Eine Pfändung gegen einen Inhaber trifft auch das gemeinsame Konto. Ein Gemeinschaftskonto kann kein P-Konto sein. Das Gesetz gibt deshalb einen Monat Schutz: In dieser Zeit zahlt die Bank nichts an den Gläubiger aus, und jeder Inhaber kann verlangen, dass sein Anteil auf ein eigenes Konto bei derselben Bank übertragen wird, das er als P-Konto führt (§ 850l ZPO). Mehr dazu im Ratgeber '+rg('p-konto','P-Konto')+'.')),
     ('Gemeinschaftskonto oder geteilte Unterkonten',
      _P('Viele Paare brauchen gar kein vollständiges Gemeinschaftskonto. Ein beliebtes Modell sind drei Töpfe: Jeder behält sein eigenes Konto, und beide überweisen jeden Monat einen festen Betrag auf ein gemeinsames Haushaltskonto. Von dort gehen Miete, Strom und Einkauf ab. Was übrig bleibt, gehört jedem selbst. Das hält die Haftung und die Schenkungsfrage klein.',
         'Einige Banken bieten Unterkonten an, die du mit einer anderen Person teilen kannst. Das sieht aus wie ein Gemeinschaftskonto, ist rechtlich aber meist keins: Inhaber bleibt der, dem das Hauptkonto gehört. Der andere darf nur einzahlen oder auch ausgeben, je nach Freigabe. Für kleine gemeinsame Kassen, etwa Urlaub oder WG-Einkauf, reicht das völlig. '
         +(f'In dieser Liste gibt es {_n(len(uk),"Konto","Konten")}, bei {"dem" if len(uk)==1 else "denen"} du zusätzlich Unterkonten anlegen kannst: {_links(c,uk,4)}. ' if uk else '')
         +'Alle Konten mit Unterkonten stehen in der Liste '+li('unterkonten','Girokonten mit Unterkonten')+'.',
         'Ein Vorteil des echten Gemeinschaftskontos bleibt: die Einlagensicherung. Sie schützt 100.000 € je Einleger und Bank (§ 8 EinSiG), und das Guthaben auf einem Gemeinschaftskonto wird jedem Inhaber zur Hälfte zugerechnet (§ 7 EinSiG). Zwei Inhaber sind also mit bis zu 200.000 € abgesichert, solange keiner bei derselben Bank noch weiteres Geld liegen hat. Mehr im Ratgeber '+rg('einlagensicherung','Einlagensicherung')+'.')),
     ('Quellen',
      _P(_ul(['Gemeinschaftskonto möglich, Preise, Karten und Eröffnungsweg: Preis- und Leistungsverzeichnisse der Banken, verlinkt bei jedem Konto im Vergleich, Stand '+E(c['stand'])+'.',
              'Gesamtgläubiger und Ausgleich: '+_ext(DE_BGB(428),'§ 428 BGB')+', '+_ext(DE_BGB(430),'§ 430 BGB')+'; Haftung: '+_ext(DE_BGB(421),'§ 421 BGB')+'.',
              'Schenkung und Erbschaft: '+_ext(DE_ERBST(16),'§ 16 ErbStG (Freibeträge)')+', '+_ext(DE_ERBST(19),'§ 19 ErbStG (Steuersätze)')+', '+_ext(DE_ERBST(30),'§ 30 ErbStG (Anzeigepflicht)')+', '+_ext(DE_ERBST(33),'§ 33 ErbStG (Meldung der Banken)')+'; BFH, Urteil vom 23.11.2011, II R 33/10.',
              'Identifizierung und Steuer-ID: '+_ext(DE_GWG_12,'§ 12 GwG')+', '+_ext(DE_AO_154,'§ 154 AO')+'.',
              'Pfändung: '+_ext(DE_ZPO_850L,'§ 850l ZPO')+'; Kontowechsel: '+_ext(DE_ZKG(20),'§ 20 ZKG')+'.',
              'Einlagensicherung: '+_ext('https://www.gesetze-im-internet.de/einsig/__7.html','§ 7 EinSiG')+', '+_ext(DE_EINSIG,'§ 8 EinSiG')+', '+_ext(DE_BAFIN_ES,'BaFin, Einlagensicherung und Anlegerentschädigung')+', '+ABG+'.']))),
    ]
    faq=[
     ('Muss man verheiratet sein, um ein Gemeinschaftskonto zu eröffnen?','Nein. Jede volljährige Person kann mit einer anderen ein Gemeinschaftskonto eröffnen, auch unverheiratete Paare, Geschwister oder eine WG. Steuerlich gibt es aber einen Unterschied: Unverheiratete haben bei Schenkungen nur 20.000 € Freibetrag in zehn Jahren, Ehepartner 500.000 €.'),
     ('Kann ich mein bestehendes Girokonto in ein Gemeinschaftskonto umwandeln?','Bei vielen Banken ja, der zweite Inhaber muss sich dann ausweisen und den Vertrag mit unterschreiben. Manche Banken eröffnen stattdessen ein neues Konto mit neuer IBAN. Frag vorher nach, dann weißt du, ob du Arbeitgeber und Lastschriften umstellen musst.'),
     ('Sieht die Schufa das Gemeinschaftskonto bei beiden Partnern?','Ja, die Bank meldet das Konto in der Regel für jeden Inhaber. Ein Girokonto allein schadet dem Score nicht. Gerät das Konto aber in Zahlungsverzug und die Bank kündigt deshalb, kann das bei beiden einen negativen Eintrag auslösen.'),
     ('Kann ich mit meinen Eltern oder meinem erwachsenen Kind ein Gemeinschaftskonto führen?','Ja. Für die Unterstützung älterer Eltern ist aber oft eine Kontovollmacht das bessere Werkzeug: Du kannst Rechnungen bezahlen, ohne Miteigentümer des Guthabens zu werden. Bei Eltern und Kindern gilt ein Schenkungsfreibetrag von 400.000 €.'),
     ('Bekommt jeder Inhaber eine eigene Karte?','Bei fast allen Banken ja, jeder Inhaber bekommt eine eigene Karte auf seinen Namen und einen eigenen Online-Zugang. Ob die zweite Karte extra kostet, ist unterschiedlich. Das steht in der Kostentabelle auf dieser Seite.'),
    ]
    lede='Hier stehen alle Girokonten, die du laut Bank auch zu zweit eröffnen kannst, sortiert nach unserer Bewertung. Darunter erfährst du, wie Oder- und Und-Konto funktionieren, wer für ein Minus geradesteht und wann das Finanzamt mitrechnet.'
    return dict(lede=lede,secs=secs,faq=faq)


# =====================================================================
# Gemeinschaftskonto Österreich
# =====================================================================
def _gem_at(c):
    X=c['lists'].get('gemeinschaftskonto') or []
    L=c['link']; eur=c['eur']; pct=c['pct']; rg=c['rg']; li=c['liste']
    n=len(X); B=_banks(X)
    frei0=[k for k in X if k['kf_jahr']==0]
    bed=[k for k in X if k['kf_jahr']>0 and (k.get('gratis') or {}).get('kf_bedingt')==0]
    billig=sorted(X,key=lambda k:(k['score']['kosten']['total'],-k['stars']))
    mit_r=sorted([k for k in X if k.get('sollzins') is not None],key=lambda k:k['sollzins'])
    uk=[k for k in X if (k.get('unterkonten') or 0)>=1]
    mitinh=[k for k in X if re.search(r'Mitinhaber|Zeichnungsberecht|zusätzliche Debitkarte|weitere',_dk(k))]
    fil=[k for k in X if k.get('eroeffnung') in ('filiale','beides')]
    rows=[(L(k),_kost(c,k),E(c['kurzbed'](k)),_txt(_dk(k),120)) for k in billig[:10]]

    secs=[
     ('Oder-Konto, Und-Konto oder nur Zeichnungsrecht',
      _tbl(['','Oder-Konto','Und-Konto','Zeichnungsberechtigung'],[
        ('Wem gehört das Konto','allen Inhabern','allen Inhabern','nur dem Kontoinhaber'),
        ('Wer darf verfügen','jeder allein','nur alle gemeinsam','die berechtigte Person allein'),
        ('Wer haftet für ein Minus','alle Inhaber zur ungeteilten Hand','alle Inhaber zur ungeteilten Hand','nur der Inhaber'),
        ('Typisch für','Paare, Familien, WGs','Vereine, Verlassenschaften, Geschäftspartner','Pflege der Eltern, Partner ohne eigenes Einkommen')])+
      _P('Ohne ausdrückliche andere Vereinbarung führt die Bank ein Gemeinschaftskonto als Oder-Konto. Jeder von euch kann dann über das gesamte Guthaben verfügen, Überweisungen freigeben und mit der eigenen Bankomatkarte bezahlen. Für den gemeinsamen Haushalt ist das bequem.',
         'Ein Und-Konto bekommst du meist nur in der Filiale und auf Nachfrage. Jede Überweisung braucht dann die Zustimmung aller Inhaber. Für ein Paar ist das im Alltag zu umständlich, für einen gemeinsamen Erbteil oder eine Vereinskasse aber genau richtig.',
         'Die Zeichnungsberechtigung ist die leichteste Variante. Du bleibst allein Kontoinhaberin, die andere Person darf in deinem Namen verfügen. Sie haftet nicht für ein Minus und hat keinen Anspruch auf das Guthaben. Das reicht oft, wenn nur einer von euch Geld verdient oder wenn du für einen Elternteil Rechnungen bezahlst.')),
     ('Was ihr zur Eröffnung braucht',
      _P('Beide Inhaber werden von der Bank einzeln identifiziert, das schreibt das Finanzmarkt-Geldwäschegesetz vor. Bei Online-Banken läuft das per Video-Identifikation, bei Filialbanken mit dem Ausweis am Schalter.',
         _ul(['<b>Amtlicher Lichtbildausweis</b> beider Inhaber, also Reisepass, Personalausweis oder Führerschein, je nach Bank.',
              '<b>Wohnadresse</b>, bei manchen Banken mit Hauptwohnsitz in Österreich. Wer erst zugezogen ist, sollte das vorher klären.',
              '<b>Abfrage beim KSV1870</b>, wenn ihr einen Überziehungsrahmen oder eine Kreditkarte beantragt. Für ein reines Guthabenkonto entfällt sie oft.',
              '<b>Unterschrift beider</b> auf dem Kontovertrag, bei Online-Banken digital in der App.']),
         (f'Von den {n} Konten in der Liste kannst du {len(fil)} auch oder nur in einer Filiale eröffnen, die übrigen gehen nur online. ' if X else '')+
         'Bei App-Banken ist das gemeinsame Konto oft ein Zusatz zum eigenen Konto: Zuerst eröffnet jeder sein Einzelkonto, dann lädt einer den anderen in der App ein. Deshalb kann es ein paar Tage dauern, bis ihr loslegen könnt.',
         'Hast du schon ein Konto, frag nach, ob die Bank eine Mitinhaberin oder einen Mitinhaber hinzufügen kann. Dann bleibt die IBAN gleich, und du musst Arbeitgeber, Vermieter und Versicherungen nicht informieren.')),
     ('Kosten für zwei: Kontoführung und zweite Karte',
      _P((f'In der Liste stehen {n} Konten von {len(B)} Banken, die es auch als Gemeinschaftskonto gibt. '
          +(f'{_w(len(frei0),"Eines kostet","Konten kosten")} kein Kontoführungsentgelt ohne Bedingung, ' if frei0 else '')
          +(f'{len(bed)} weitere sind gratis, wenn ihr eine Bedingung wie einen monatlichen Gehaltseingang erfüllt. ' if bed else '')
          +(f'Im Standardfall am günstigsten sind {_links(c,billig,3)}.' if len(billig)>=3 else '')) if X else 'Welche Konten es auch als Gemeinschaftskonto gibt, steht in der Liste oben.',
         'Das Kontoführungsentgelt zahlt ihr nur einmal. Teurer wird es durch die zweite Bankomat- oder Debitkarte: Manche Banken verrechnen für die Karte des Mitinhabers ein Jahresentgelt, das beim Einzelkonto nicht anfällt.'
         +(f' Ein eigenes Entgelt für weitere Karten nennen zum Beispiel {_links(c,mitinh,3)}.' if mitinh else ''))+
      (_tbl(['Konto','Kosten pro Jahr im Standardfall','Gratis, wenn','Karten laut Bank'],rows) if rows else '')+
      _P('Ein einfaches Rechenbeispiel: Zahlt ihr heute für zwei Einzelkonten je 5 € im Monat, sind das zusammen 120 € im Jahr. Läuft alles über ein gemeinsames Konto, zahlt ihr das Entgelt nur einmal und spart 60 €. Ganz auf eigene Konten verzichten solltet ihr als Paar aber nicht: Jeder sollte ein Konto haben, auf das nur er selbst Zugriff hat, etwa als Notreserve für den Fall einer Trennung. Am besten eines ohne Kontoführungsentgelt.',
         'Achte bei Gratis-Bedingungen auf die Formulierung. Verlangt die Bank einen Gehalts- oder Pensionseingang, zählt beim Gemeinschaftskonto meist jeder Eingang dieser Art, egal von welchem Inhaber. Reine Umbuchungen vom eigenen Sparkonto zählen dagegen oft nicht. Einen Überblick über alle Konten mit ihren Entgelten bietet auch der '+_ext(AT_BANKENRECHNER,'Bankenrechner der Arbeiterkammer')+'.')),
     ('Solidarhaftung: Wenn einer überzieht, zahlen beide',
      _P('Alle Inhaber eines Gemeinschaftskontos haften der Bank nach den üblichen Geschäftsbedingungen zur ungeteilten Hand (§ 891 ABGB). Rutscht euer Konto um 1.800 € ins Minus, darf die Bank die ganzen 1.800 € von dir fordern, auch wenn dein Partner das Geld ausgegeben hat. Wer im Innenverhältnis wie viel schuldet, müsst ihr untereinander klären.',
         ('Den Überziehungsrahmen setzt ihr am besten niedrig an oder verzichtet ganz darauf. '
          +(f'Einige Konten haben gar keinen eingeräumten Rahmen. Wo es einen gibt, kostet er in dieser Liste zwischen {pct(mit_r[0]["sollzins"])} und {pct(mit_r[-1]["sollzins"])} Sollzinsen im Jahr. ' if len(mit_r)>1 else ''))
         +'Was Rahmen und Überschreitung kosten und welche neuen Informationspflichten ab 20. November 2026 gelten, steht im Ratgeber '+rg('kontoueberziehung','Kontoüberziehung')+'.',
         'Die Haftung gilt so lange, wie ihr beide Inhaber seid. Auch ein Minus, das erst nach einer Trennung entsteht, trifft beide. Das ist der wichtigste Grund, bei einer Trennung sofort zu handeln.')),
     ('Schenkungsmeldung: keine Steuer, aber eine Pflicht',
      _P('Eine Schenkungs- und Erbschaftssteuer gibt es in Österreich seit August 2008 nicht mehr. Geblieben ist eine Meldepflicht nach dem Schenkungsmeldegesetz, geregelt in § 121a BAO. Sie kann auch ein Gemeinschaftskonto betreffen: Zahlt einer von euch eine Erbschaft oder den Erlös aus einem Wohnungsverkauf auf das gemeinsame Oder-Konto ein, kann die Hälfte als Schenkung an den anderen gelten.')+
      _tbl(['Wer schenkt wem','Meldepflicht ab','Frist'],[
        ('Angehörige, dazu zählen Ehepartner und Lebensgefährten','mehr als 50.000 € innerhalb eines Jahres','drei Monate ab der Schenkung'),
        ('Andere Personen, etwa Freunde oder WG-Mitbewohner','mehr als 15.000 € innerhalb von fünf Jahren','drei Monate ab der Schenkung')])+
      _P('Die Meldung machst du am einfachsten über FinanzOnline. Sie kostet nichts. Wer sie absichtlich unterlässt, riskiert aber eine Geldstrafe von bis zu 10 % des geschenkten Betrags. Übliche Gelegenheitsgeschenke bis 1.000 € und Hausrat sind ausgenommen.',
         'Ein Beispiel: Du erbst 120.000 € und überweist alles auf das Konto, das du mit deinem Lebensgefährten teilst. Die Hälfte, also 60.000 €, kann als Schenkung an ihn gelten. Das liegt über 50.000 €, also ist eine Meldung fällig. Willst du das vermeiden, bleibt die Erbschaft auf deinem Einzelkonto, und ihr nutzt das gemeinsame Konto nur für den Haushalt.')),
     ('Wenn ein Inhaber stirbt',
      _P('Beim Oder-Konto bleibt der überlebende Inhaber nach den üblichen Geschäftsbedingungen der Banken verfügungsberechtigt. Miete und laufende Rechnungen können also weiter bezahlt werden. Das heißt aber nicht, dass das ganze Guthaben jetzt dem Überlebenden gehört. Der Anteil des Verstorbenen, im Zweifel die Hälfte, fällt in die Verlassenschaft.',
         'Das Verlassenschaftsverfahren führt ein Notar als Gerichtskommissär. Er fragt bei den Banken nach den Konten des Verstorbenen. Hebt der Überlebende vorher mehr als seinen Anteil ab, kann er das den Erben gegenüber ausgleichen müssen. Am besten sprecht ihr frühzeitig darüber, wer was bekommen soll, und haltet das in einem Testament fest. Lebensgefährten haben ohne Testament nur in Ausnahmefällen ein gesetzliches Erbrecht.',
         'Ein Und-Konto ist nach dem Tod eines Inhabers praktisch blockiert, bis die Erben feststehen. Für Paare ist das ein weiterer Grund, das Oder-Konto zu wählen und den Rest über Testament und Vollmachten zu regeln.')),
     ('Trennung oder Scheidung: das Konto sauber auflösen',
      _P(_ul(['<b>Einzelverfügung widerrufen.</b> Jeder Inhaber eines Oder-Kontos kann der Bank mitteilen, dass ab sofort nur noch beide gemeinsam verfügen dürfen. Das stoppt Abhebungen und neue Überziehungen.',
              '<b>Guthaben aufteilen.</b> Im Zweifel gehört jedem die Hälfte, egal wer mehr eingezahlt hat. Bei einer Scheidung zählen gemeinsame Ersparnisse zur Aufteilungsmasse nach dem Ehegesetz. Belege über eigene Einzahlungen, etwa aus einer Erbschaft, helfen dir dabei.',
              '<b>Saldo ausgleichen.</b> Solange das Konto im Minus ist, schließt die Bank es nicht, und beide haften weiter.',
              '<b>Zahlungen umziehen.</b> Gehalt, Miete, Strom und Daueraufträge gehören auf die neuen Einzelkonten. Der gesetzliche Kontowechsel-Service nimmt dir viel davon ab, siehe '+rg('girokonto-wechseln','Girokonto wechseln')+' und die '+_ext(AT_AK_WECHSEL,'Infos der Arbeiterkammer zum Kontowechsel')+'.',
              '<b>Gemeinsam kündigen.</b> Schließen können das Konto nur alle Inhaber zusammen.']),
         'Wird gegen einen Inhaber Exekution geführt, kann auch das gemeinsame Guthaben betroffen sein. Ein Pfändungsschutzkonto wie in Deutschland gibt es in Österreich nicht. Was am Konto geschützt ist und wie du den Kontenschutz beim Exekutionsgericht beantragst (§ 292i EO), steht im Ratgeber '+rg('pfaendungsschutzkonto','Pfändungsschutzkonto')+'.')),
     ('Gemeinsames Konto oder geteilte Unterkonten',
      _P('Ein gemeinsames Konto ist nicht die einzige Lösung. Viele Paare fahren gut mit dem Drei-Konten-Modell: Jeder behält sein eigenes Gehaltskonto, und beide zahlen einen festen Betrag auf ein gemeinsames Haushaltskonto ein. Das hält die Haftung überschaubar und die Frage, wem was gehört, einfach.',
         'Manche Banken erlauben, ein Unterkonto mit einer anderen Person zu teilen. Rechtlich bleibt das ein Teil deines Kontos, der andere bekommt nur Zugriff. Für eine Urlaubskasse oder die WG-Einkäufe passt das gut. Für das ganze Familienbudget fehlt dann aber die zweite Inhaberin, die auch allein Verträge mit der Bank regeln kann. '
         +(f'In dieser Liste kannst du bei {_w(len(uk),"einem Konto","Konten")} zusätzlich Unterkonten anlegen, zum Beispiel {_links(c,uk,4)}. ' if uk else '')
         +'Alle Konten mit Unterkonten findest du in der Liste '+li('unterkonten','Girokonten mit Unterkonten')+'.',
         'Für Ersparnisse auf dem gemeinsamen Konto gilt die Einlagensicherung pro Person: 100.000 € je Einleger und Bank, bei zwei Inhabern also bis zu 200.000 €, im Zweifel je zur Hälfte zugerechnet. Hast du bei derselben Bank noch ein eigenes Sparkonto, zählt es in deine 100.000 € mit. Mehr dazu im Ratgeber '+rg('einlagensicherung','Einlagensicherung')+'.')),
     ('Quellen',
      _P(_ul(['Gemeinschaftskonto möglich, Entgelte, Karten und Eröffnungsweg: Preisblätter und Entgeltinformationen der Banken, verlinkt bei jedem Konto im Vergleich, Stand '+E(c['stand'])+'.',
              'Solidarhaftung: § 891 ABGB; Kontoführung und Überziehung: Arbeiterkammer Wien, '+_ext(AT_AK_FAQ,'Fragen und Antworten zum Thema Girokonten')+'.',
              'Überziehung ab 20.11.2026: '+_ext(AT_VKRG,'BGBl. I Nr. 36/2026')+'.',
              'Schenkungsmeldung (§ 121a BAO): '+_ext(AT_BMF_SCHENK,'Bundesministerium für Finanzen, Schenkungsmeldung')+', '+ABG+'.',
              'Einlagensicherung: '+_ext(AT_ES,'Einlagensicherung AUSTRIA')+', '+_ext(AT_BAWAG_ES,'Informationsbogen zur Einlagensicherung (Beispiel BAWAG)')+'.']))),
    ]
    faq=[
     ('Können Lebensgefährten ohne Trauschein ein Gemeinschaftskonto eröffnen?','Ja, jede volljährige Person kann mit einer anderen ein gemeinsames Konto eröffnen. Bei der Schenkungsmeldung gelten Lebensgefährten als Angehörige, für sie liegt die Grenze also wie bei Ehepartnern bei 50.000 € pro Jahr.'),
     ('Kann ich mein bestehendes Konto zu einem Gemeinschaftskonto machen?','Bei vielen Banken ja: Die zweite Person wird als Mitinhaberin aufgenommen, identifiziert sich und unterschreibt. Manche Banken, vor allem App-Banken, eröffnen dafür ein eigenes gemeinsames Konto mit neuer IBAN.'),
     ('Bekommen beide Inhaber eine eigene Bankomatkarte?','In der Regel ja, jeder Inhaber bekommt eine Karte auf seinen Namen. Ob die zweite Karte gratis ist oder ein Jahresentgelt kostet, steht in der Kostentabelle auf dieser Seite.'),
     ('Mein Partner hat das gemeinsame Konto leergeräumt. Was kann ich tun?','Widerrufe sofort die Einzelverfügung bei der Bank, dann geht nur noch gemeinsam. Das abgehobene Geld kannst du von deinem Partner zurückfordern, soweit es mehr als seine Hälfte war. Bei Streit helfen die Arbeiterkammer oder ein Anwalt.'),
     ('Ist ein Gemeinschaftskonto mit meinen Eltern sinnvoll, um ihnen zu helfen?','Meist reicht eine Zeichnungsberechtigung: Du bezahlst ihre Rechnungen, ohne Miteigentümerin des Guthabens zu werden oder für ein Minus zu haften. Für den Fall, dass sie selbst nicht mehr entscheiden können, braucht es zusätzlich eine Vorsorgevollmacht.'),
    ]
    lede='Diese Liste zeigt alle Girokonten, die du laut Bank auch als gemeinsames Konto für zwei führen kannst, sortiert nach unserer Bewertung. Danach erklären wir, wie Oder- und Und-Konto funktionieren, wer für ein Minus haftet und wann du dem Finanzamt etwas melden musst.'
    return dict(lede=lede,secs=secs,faq=faq)


# =====================================================================
# Studierende Deutschland
# =====================================================================
def _stu_de(c):
    X=c['lists'].get('studenten') or []
    L=c['link']; eur=c['eur']; pct=c['pct']; rg=c['rg']; li=c['liste']
    n=len(X)
    frei0=[k for k in X if k['kf_jahr']==0]
    teuer=[k for k in X if k['score']['kosten']['total']>0]
    maxs=[k for k in X if (k.get('alter') or {}).get('max') is not None]
    lang=sorted(maxs,key=lambda k:-k['alter']['max']); kurz=sorted(maxs,key=lambda k:k['alter']['max'])
    nachweis=[k for k in X if re.search(r'Nachweis|Studierende|Azubi|Schüler',_all(k))]
    azubi=[k for k in X if re.search(r'Azubi',_all(k))]
    frw=[k for k in X if re.search(r'[Ff]reiwillig',_all(k))]
    eu=[k for k in X if re.search(r'Meldeadresse',_all(k))]
    fil=[k for k in X if k.get('eroeffnung')=='filiale']
    disp=sorted([k for k in X if k.get('sollzins') is not None],key=lambda k:k['sollzins'])
    fx=[k for k in X if k.get('fremdwaehrung_prozent') is not None]
    fx0=[k for k in fx if k['fremdwaehrung_prozent']==0]
    fxmax=max(fx,key=lambda k:k['fremdwaehrung_prozent']) if fx else None
    jung=_jung(c)
    rows=[(L(k),E(c['altT'](k)),_kost(c,k),_txt(_bed(k),170)) for k in X]

    if disp:
        r=disp[-1]['sollzins']; zins=500*r/100*3/12
        bsp=(f'Ein Rechenbeispiel mit dem höchsten Dispozins in dieser Liste, {pct(r)}: Stehst du drei Monate lang mit 500 € im Minus, zahlst du rund {eur(round(zins,2))} € Zinsen. Das klingt wenig. '
             'Das Problem ist, dass ein Dispo selten nach drei Monaten weg ist. Wer jeden Monat ein Stück tiefer rutscht, zahlt am Ende auf ein paar tausend Euro Zinsen, ohne je einen Kredit beantragt zu haben.')
        spanne=(f'Bei den Konten in dieser Liste liegt der Dispozins zwischen {pct(disp[0]["sollzins"])} bei {L(disp[0])} und {pct(disp[-1]["sollzins"])}. ' if len(disp)>1 else '')
    else:
        bsp=''; spanne=''

    secs=[
     ('Worauf du bei einem Konto fürs Studium achten solltest',
      _P(('Konten für Studierende sind fast immer kostenlos. '+(f'Von den {n} Konten in dieser Liste kosten {len(frei0)} keine Kontoführungsgebühr, solange du die Bedingungen erfüllst. ' if X else ''))+
         'Der Preis allein entscheidet also selten. Wichtiger sind die Details, die dich im Studienalltag Geld oder Nerven kosten können:',
         _ul(['<b>Altersgrenze.</b> Wie lange bleibt das Konto gratis? Ein Studium mit Master und Pause dauert schnell bis Ende 20.',
              '<b>Karte.</b> Bekommst du eine Debitkarte, mit der du online bezahlen kannst, und gibt es eine girocard für Läden, die nur die nehmen?',
              '<b>Bargeld.</b> Kostet Abheben an fremden Automaten? Gerade in einer neuen Uni-Stadt hat deine Bank vielleicht keinen Automaten um die Ecke.',
              '<b>Ausland.</b> Was kostet Bezahlen in Fremdwährung, falls ein Auslandssemester außerhalb des Euroraums ansteht?',
              '<b>Was danach kommt.</b> Auf welches Konto stellt die Bank um, und was kostet es dann?']),
         'Musst du kein Studentenkonto nehmen? Nein. Viele normale Girokonten sind ebenfalls kostenlos, teils mit einer Altersgrenze von Ende 20 statt eines Studiennachweises. Die findest du in der Liste '+li('kostenlos','kostenlose Girokonten')+'. Ein echtes Studentenkonto lohnt sich vor allem, wenn du keinen regelmäßigen Geldeingang hast, denn viele Gratis-Konten verlangen einen.')),
     ('Altersgrenzen und Bedingungen im Überblick',
      (_tbl(['Konto','Alter','Kosten pro Jahr','Bedingung laut Bank'],rows) if rows else '')+
      _P(((f'Am längsten gratis bleibt laut Bank {L(lang[0])} mit einer Grenze von {E(c["altT"](lang[0]))}. ' if lang else '')
          +(f'Am kürzesten ist die Grenze bei {L(kurz[0])} ({E(c["altT"](kurz[0]))}). ' if len(kurz)>1 and kurz[0] is not lang[0] else '')
          +(f'{_w(len(teuer),"Ein Konto kostet","Konten kosten")} auch für junge Leute etwas, etwa {_links(c,teuer,2)}. ' if teuer else '')),
         'Lies die Altersangabe genau. „Bis 27 Jahre“ heißt bei den meisten Banken: bis zum Tag vor dem 28. Geburtstag. Manche Banken stellen am Geburtstag selbst um, andere zum Monats- oder Quartalsende. Das steht im Preis- und Leistungsverzeichnis.')),
     ('Studentenkonto oder normales Konto mit Altersrabatt',
      _P('Viele Online-Banken schenken jungen Leuten die Kontoführung auch ohne Studium. Bei diesen Konten zählt nur das Alter: Du brauchst keine Immatrikulationsbescheinigung, und bis zur Altersgrenze verlangt die Bank auch keinen Geldeingang. '
         +(f'Am längsten gilt der Altersrabatt bei {L(jung[0])}, nämlich bis zum {jung[0]["gratis"]["alter_unter"]}. Geburtstag.' if jung else ''))+
      (_tbl(['Konto','Gratis bis','Bedingung laut Bank'],[(L(k),f'zum {k["gratis"]["alter_unter"]}. Geburtstag',E(c['kurzbed'](k))) for k in jung[:8]]) if jung else '')+
      _P('Der Vorteil: Nach dem Studium musst du nicht wechseln. Mit dem ersten Gehalt erfüllst du die Bedingung für das Gratis-Konto meist ohnehin, und die IBAN bleibt dieselbe. Der Nachteil: Diese Konten sind fast immer reine Online-Konten. Bargeld bekommst du an fremden Automaten oder an der Supermarktkasse, Bargeld einzahlen ist umständlich, und eine girocard kostet teils extra. Wer gern in eine Filiale geht, ist mit einem Studentenkonto einer Filialbank besser bedient.')),
     ('Diese Unterlagen brauchst du',
      _P(_ul(['<b>Personalausweis oder Reisepass.</b> Mit Reisepass zusätzlich eine Meldebescheinigung, weil dort keine Adresse steht.',
              '<b>Nachweis über Studium oder Ausbildung.</b> Meist die Immatrikulationsbescheinigung, bei Azubis der Ausbildungsvertrag. '+(f'Ausdrücklich verlangt wird er zum Beispiel bei {_links(c,nachweis,3)}.' if nachweis else ''),
              '<b>Steuer-ID.</b> Die Bank muss sie für jeden Kontoinhaber erfassen (§ 154 Abs. 2a AO). Sie steht auf dem Brief des Bundeszentralamts für Steuern oder auf deiner Lohnsteuerbescheinigung.',
              '<b>Smartphone oder Termin.</b> Für die Identifizierung per Video oder in der Postfiliale, bei Filialbanken am Schalter.']),
         ((f'Nur in der Filiale eröffnen kannst du {_links(c,fil)}. ' if fil else '')
          +(f'Bei {_links(c,eu)} verlangt die Bank außerdem eine Meldeadresse in der EU. ' if eu else '')),
         'Du kommst aus dem Ausland und hast noch keine Meldeadresse? Dann wird es bei vielen Banken schwierig. Hier hilft das Recht auf ein Basiskonto: Jede Bank, die Girokonten anbietet, muss es dir eröffnen, wenn du dich rechtmäßig in der EU aufhältst (§ 31 ZKG). Ein Basiskonto ist kein Gratiskonto, aber ein vollwertiges Girokonto. Mehr im Ratgeber '+rg('basiskonto','Basiskonto')+'. Das Sperrkonto, das viele für das Visum brauchen, ist übrigens etwas anderes: Von dort fließt monatlich ein fester Betrag auf dein normales Girokonto.')),
     ('Dispo im Studium: lieber klein oder gar nicht',
      _P('Ein Konto für Studierende läuft erst einmal auf Guthabenbasis. Einen Dispo gibt es nur auf Antrag, ab 18 und nach Prüfung deiner Bonität bei der Schufa. Ohne festes Einkommen ist der Rahmen meist klein oder wird abgelehnt. Das ist kein Nachteil.',
         spanne+bsp if (spanne or bsp) else 'Dispozinsen sind teurer als fast jeder andere Kredit. Wer jeden Monat ein Stück tiefer ins Minus rutscht, zahlt am Ende auf ein paar tausend Euro Zinsen.',
         'Brauchst du für eine Anschaffung oder eine Überbrückung wirklich Geld, sind BAföG-Vorauszahlung, ein Studienkredit oder ein günstiger Ratenkredit meist billiger als ein Dispo. Wie du den Dispo begrenzt oder ganz streichen lässt, steht im Ratgeber '+rg('dispo','Dispo')+'.',
         'Ein Nebeneffekt des ersten eigenen Kontos: Es landet als positiver Eintrag bei der Schufa. Wer sein Konto ohne Rücklastschriften führt, baut damit eine saubere Bonitätsgeschichte auf, die später bei der ersten Wohnung oder dem Handyvertrag hilft.')),
     ('Auslandssemester: Karte, Gebühren und Adresse',
      _P('Im Euroraum ist das einfach. Kartenzahlungen und Überweisungen in Euro dürfen innerhalb der EU nicht mehr kosten als im Inland. Dein Erasmus-Zuschuss oder der Mietvorschuss für das Zimmer in Lissabon kommt per SEPA-Überweisung an wie jede Zahlung aus Deutschland.',
         'Außerhalb des Euroraums wird es teurer. Für Zahlungen in Fremdwährung verlangen viele Banken einen Aufschlag. '
         +((f'In dieser Liste reicht er von {pct(0) if fx0 else pct(min(k["fremdwaehrung_prozent"] for k in fx))} bis {pct(fxmax["fremdwaehrung_prozent"])} je Zahlung. ' if fxmax and fxmax['fremdwaehrung_prozent']>0 else '')
           +(f'Ohne Aufschlag mit der Karte zahlst du laut Bank bei {_links(c,fx0)}. ' if fx0 else ''))
         +'Bei 6.000 € Ausgaben in einem Semester in Schweden oder der Schweiz machen 2 % schon 120 € aus.',
         _ul(['Nimm eine zweite Karte mit, am besten eine Kreditkarte ohne Auslandseinsatzentgelt. Passende Konten stehen in der Liste '+li('mit-kreditkarte','Girokonten mit Kreditkarte')+'.',
              'Wähle am Automaten und im Laden immer die Abrechnung in Landeswährung, nicht in Euro. Die Umrechnung des Händlers ist fast immer teurer.',
              'Behalte deine Meldeadresse in Deutschland oder gib der Bank eine Adresse, unter der dich Post erreicht. Manche Studentenkonten setzen einen Wohnsitz in Deutschland oder der EU voraus.',
              'Prüfe vorher, ob dein Online-Banking mit einer ausländischen SIM-Karte funktioniert. Die Freigabe läuft heute meist über eine App, die eine Datenverbindung braucht.']))),
     ('Nach dem Studium: Umstellung und rechtzeitig wechseln',
      _P('Endet das Studium oder ist die Altersgrenze erreicht, stellt die Bank das Konto auf ein normales Modell um. Das passiert meist automatisch und ohne neuen Vertrag, aber mit neuen Preisen. Ein Konto für 9,90 € im Monat kostet 118,80 € im Jahr, Karten und Bargeld noch nicht eingerechnet. Was bei deinem Konto danach kommt, steht in der Tabelle oben in der Spalte Bedingung.',
         'Dein Konto musst du der Bank in vielen Fällen selbst abmelden: Die meisten Banken verpflichten dich in ihren Bedingungen, mitzuteilen, wenn der Studentenstatus endet. Wer den Nachweis einfach weiter schuldig bleibt, wird spätestens bei der nächsten Prüfung umgestellt.',
         'Schau dir zwei bis drei Monate vor der Umstellung an, was das neue Modell kostet. Mit dem ersten Gehalt erfüllst du bei vielen Banken die Bedingung für ein kostenloses Konto. Die Liste '+li('kostenlos','kostenlose Girokonten')+' zeigt, wo das geht. Der Wechsel selbst ist dank der Kontowechselhilfe nach § 20 ZKG schnell erledigt: Die neue Bank holt die Daueraufträge und Lastschriften bei der alten ab. Wie das genau läuft, steht im Ratgeber '+rg('girokonto-wechseln','Girokonto wechseln')+'.')),
     ('Azubis, Schüler und Freiwilligendienst',
      _P('Die Konten in dieser Liste sind nicht nur für Studierende gedacht. '
         +(f'Auch Auszubildende nennen die Bedingungen bei {_links(c,azubi,4)}. ' if azubi else '')
         +(f'Freiwilligendienst oder Bundesfreiwilligendienst zählen bei {_links(c,frw,3)}. ' if frw else '')
         +'Volljährige Schülerinnen und Schüler, Praktikanten und Volontäre sind bei vielen Banken ebenfalls dabei, solange sie einen Nachweis bringen.',
         'Für Azubis ist das Konto doppelt wichtig, weil hier die Ausbildungsvergütung eingeht. Gib deinem Ausbildungsbetrieb die IBAN rechtzeitig vor dem ersten Monat. Das Konto muss keine deutsche IBAN haben: Nach der SEPA-Verordnung darf ein Arbeitgeber keine Kontoverbindung aus einem anderen EU-Land ablehnen.',
         'Bist du noch keine 18, eröffnen deine Eltern das Konto mit dir zusammen. Konten für Minderjährige laufen ohne Dispo und stehen in den Listen '+li('jugendkonto','Jugendkonten')+' und '+li('kinderkonto','Kinderkonten')+'.')),
     ('Quellen',
      _P(_ul(['Altersgrenzen, Nachweise, Preise, Dispozinsen und Fremdwährungsentgelte: Preis- und Leistungsverzeichnisse und Produktseiten der Banken, verlinkt bei jedem Konto im Vergleich, Stand '+E(c['stand'])+'.',
              'Steuer-ID bei der Kontoeröffnung: '+_ext(DE_AO_154,'§ 154 AO')+'; Identifizierung: '+_ext(DE_GWG_12,'§ 12 GwG')+'.',
              'Basiskonto: '+_ext(DE_ZKG(31),'§ 31 ZKG')+', '+_ext(DE_BAFIN_BASIS,'BaFin, Basiskonto')+'; Kontowechselhilfe: '+_ext(DE_ZKG(20),'§ 20 ZKG')+'.',
              'Dispo: '+_ext(DE_BAFIN_DISPO,'BaFin, Fragen zum Dispokredit')+'.',
              'IBAN-Diskriminierung: '+_ext(EU_SEPA,'Verordnung (EU) Nr. 260/2012, Art. 9')+'; BAföG: '+_ext(DE_BAFOEG,'BAföG Digital')+', '+ABG+'.']))),
    ]
    faq=[
     ('Muss mein Konto eine deutsche IBAN haben, damit BAföG und Gehalt ankommen?','Nein. Behörden und Arbeitgeber dürfen eine IBAN aus einem anderen EU-Land nicht ablehnen, das regelt die SEPA-Verordnung. Wichtig ist nur, dass das Konto auf deinen Namen läuft.'),
     ('Wie oft muss ich die Immatrikulationsbescheinigung nachreichen?','Das legt jede Bank selbst fest. Manche wollen den Nachweis nur bei der Eröffnung, andere fragen jedes Jahr oder jedes Semester nach. Reichst du ihn nicht ein, stellt die Bank auf das normale Kontomodell um.'),
     ('Was passiert mit dem Studentenkonto, wenn ich das Studium abbreche?','Die Bank stellt auf ein normales Konto um, sobald sie davon erfährt oder der nächste Nachweis fehlt. Du bist meist verpflichtet, ihr das mitzuteilen. Kündigen musst du nicht, aber vergleichen lohnt sich.'),
     ('Bekomme ich als Student ohne Einkommen eine Kreditkarte?','Eine Debitkarte bekommst du bei fast jedem Konto ohne Prüfung. Eine echte Kreditkarte setzt eine Bonitätsprüfung voraus, viele Banken geben sie Studierenden ab 18 trotzdem, mit kleinem Limit. Für Reisen reicht oft eine Debitkarte von Visa oder Mastercard.'),
     ('Lohnt sich ein Studentenkonto, wenn ich schon ein kostenloses Girokonto habe?','Nur wenn das alte Konto bald Geld kostet, etwa weil der Geldeingang fehlt. Ein zweites Konto bringt sonst wenig. Für die Ordnung im Studium reichen Unterkonten oder ein Tagesgeldkonto.'),
    ]
    lede='Diese Liste zeigt Girokonten, die Banken speziell für Studierende, Azubis und junge Erwachsene anbieten, sortiert nach unserer Bewertung. Darunter steht, welche Altersgrenzen gelten, welche Unterlagen du brauchst und was nach dem Studium passiert.'
    return dict(lede=lede,secs=secs,faq=faq)


# =====================================================================
# Studierende Österreich
# =====================================================================
def _stu_at(c):
    X=c['lists'].get('studenten') or []
    L=c['link']; eur=c['eur']; pct=c['pct']; rg=c['rg']; li=c['liste']
    n=len(X)
    frei0=[k for k in X if k['kf_jahr']==0]
    bedingt=[k for k in X if k['kf_jahr']>0]
    maxs=[k for k in X if (k.get('alter') or {}).get('max') is not None]
    lang=sorted(maxs,key=lambda k:-k['alter']['max']); kurz=sorted(maxs,key=lambda k:k['alter']['max'])
    insk=[k for k in X if re.search(r'Inskription|Studienbestätigung|Nachweis',_all(k))]
    isic=[k for k in X if 'ISIC' in _dk(k)]
    wohn=[k for k in X if re.search(r'Wohnsitz|wohnhaft',_all(k))]
    plus=[k for k in X if re.search(r'Guthaben|positive',(k.get('gratis') or {}).get('sonst') or '')]
    lehre=[k for k in X if re.search(r'Lehrling|Lehre|Berufsanw',_all(k))]
    erwerb=[k for k in X if re.search(r'[Ee]rwerbstätig',_all(k))]
    eingang=[k for k in X if (k.get('gratis') or {}).get('eingang_min')]
    kk=[k for k in X if re.search(r'Student|Studierend',k.get('kreditkarte') or '')]
    fil=[k for k in X if k.get('eroeffnung')=='filiale']
    disp=sorted([k for k in X if k.get('sollzins') is not None],key=lambda k:k['sollzins'])
    fx=[k for k in X if k.get('fremdwaehrung_prozent') is not None]
    rows=[(L(k),E(c['altT'](k)),_kost(c,k),_txt(_bed(k),170)) for k in X]
    rows_b=[(L(k),_txt(_dk(k),110),_txt((k.get('bargeld') or {}).get('text'),150)) for k in X]
    jung=_jung(c)
    grenz=sorted({k['alter']['max']+1 for k in maxs})
    p_grenz=(f'Die Grenzen liegen je nach Bank zwischen dem {grenz[0]}. und dem {grenz[-1]}. Geburtstag. ' if len(grenz)>1 else '')

    secs=[
     ('Was ein gutes Studentenkonto in Österreich ausmacht',
      _P(('Fast alle großen Banken in Österreich haben ein eigenes Konto für Studierende. '+(f'In dieser Liste sind es {n}, {len(frei0)} davon ohne Kontoführungsentgelt' if X else '')+(f', bei {len(bedingt)} weiteren entfällt das Entgelt, solange du jung genug bist oder eine Bedingung erfüllst. ' if bedingt else ('. ' if X else ''))),
         'Gratis sind sie also fast alle. Unterschiede gibt es bei den Dingen, die erst im Alltag auffallen:',
         _ul(['<b>Wie lange gratis?</b> '+p_grenz+'Mit Bachelor, Master und einem Jahr Pause kommst du schnell darüber.',
              '<b>Welcher Nachweis?</b> Inskriptionsbestätigung bei der Eröffnung oder jedes Jahr neu?',
              '<b>Bankomatkarte.</b> Ist die Debitkarte inklusive, und kannst du damit online und mit dem Handy zahlen?',
              '<b>Bargeld.</b> Kostet die Behebung an fremden Bankomaten in Österreich etwas? Gerade in kleineren Uni-Städten ist das ein Thema.',
              '<b>Umstellung.</b> Auf welches Konto wechselt die Bank danach, und was kostet es?']),
         'Bei Karte und Bargeld unterscheiden sich die Studentenkonten mehr als beim Preis. Die Tabelle zeigt, was laut Bank inkludiert ist:')+
      (_tbl(['Konto','Karte laut Bank','Bargeld laut Bank'],rows_b) if rows_b else '')+
      _P('Wer viel mit Bargeld zahlt, etwa am Würstelstand oder in der WG-Kasse, sollte auf Behebungen an fremden Bankomaten achten. In Österreich verrechnen manche private Automatenbetreiber ein eigenes Entgelt, das die Bank weitergibt. Wer fast nur mit Karte oder Handy zahlt, kann diesen Punkt vernachlässigen.')),
     ('Studentenkonto oder Gratis-Konto für junge Erwachsene',
      _P('Ein Studentenkonto ist nicht die einzige Möglichkeit, als junger Mensch nichts für das Konto zu zahlen. Einige Banken verzichten bei ihrem normalen Konto bis zu einer Altersgrenze auf das Kontoführungsentgelt, ganz ohne Inskriptionsbestätigung und ohne Gehaltseingang. '
         +(f'In unserem Vergleich sind das {_links(c,jung,4)}. ' if jung else ''))+
      (_tbl(['Konto','Gratis bis','Bedingung laut Bank'],[(L(k),f'zum {k["gratis"]["alter_unter"]}. Geburtstag',E(c['kurzbed'](k))) for k in jung[:6]]) if jung else '')+
      _P('Das lohnt sich vor allem, wenn du neben dem Studium arbeitest oder bald fertig bist. Mit dem ersten Gehalt bleibt das Konto oft einfach gratis, und du musst nach dem Abschluss nicht wechseln. Wer dagegen eine Filiale in der Nähe will, Bargeld einzahlt oder Wert auf persönliche Beratung legt, fährt mit dem Studentenkonto einer Filialbank besser. Wenn du ohnehin bald ein regelmäßiges Gehalt hast, schau auch in die Liste '+li('kostenlos','kostenlose Girokonten')+'.')),
     ('Altersgrenzen und Nachweise im Vergleich',
      (_tbl(['Konto','Alter','Kosten pro Jahr','Bedingung laut Bank'],rows) if rows else '')+
      _P(((f'Am längsten gratis bleibst du laut Bank bei {L(lang[0])} ({E(c["altT"](lang[0]))}). ' if lang else '')
          +(f'Die früheste Grenze hat {L(kurz[0])} ({E(c["altT"](kurz[0]))}). ' if len(kurz)>1 and kurz[0] is not lang[0] else '')
          +(f'Eine Inskriptions- oder Studienbestätigung verlangen ausdrücklich {_links(c,insk,4)}. ' if insk else '')
          +(f'Bei {_links(c,isic)} ist die Debitkarte gleichzeitig ein internationaler Studierendenausweis (ISIC), mit dem du Rabatte bei Museen, Reisen und Software bekommst. ' if isic else '')),
         'Achte auf die Formulierung der Altersgrenze. „Bis 26 Jahre“ und „bis zum 27. Geburtstag“ meinen dasselbe. „Bis zur Vollendung des 30. Lebensjahres“ heißt: bis zum Tag vor dem 30. Geburtstag.')),
     ('Eröffnung: Unterlagen und Ablauf',
      _P(_ul(['<b>Amtlicher Lichtbildausweis</b>, also Reisepass oder Personalausweis. Bei der Online-Eröffnung läuft die Identifizierung per Video.',
              '<b>Inskriptions- oder Studienbestätigung</b> deiner Uni, FH oder Pädagogischen Hochschule, als PDF aus dem Studierendenportal.',
              '<b>Meldezettel</b> oder zumindest eine österreichische Wohnadresse. '+(f'Einen Wohnsitz in Österreich setzen zum Beispiel {_links(c,wohn,3)} voraus.' if wohn else ''),
              '<b>Steuerliche Ansässigkeit.</b> Die Bank fragt, in welchem Land du steuerpflichtig bist. Das ist Pflicht nach dem internationalen Informationsaustausch und hat für dich keine Kosten.']),
         (f'Nur nach Termin in der Filiale oder per Beratung eröffnest du {_links(c,fil)}. Bei den anderen geht es auch online. ' if fil else ''),
         'Du kommst zum Studieren aus dem Ausland und bekommst kein Studentenkonto, weil dir eine Unterlage fehlt? Dann hast du in Österreich ein Recht auf ein Basiskonto, wenn du dich rechtmäßig in der EU aufhältst. Das regelt das Verbraucherzahlungskontogesetz. Mehr dazu im Ratgeber '+rg('basiskonto','Basiskonto')+' und bei der '+_ext(AT_AK_RECHT,'Arbeiterkammer')+'.')),
     ('Überziehungsrahmen im Studium',
      _P('Ein Studentenkonto startet ohne Überziehungsrahmen. Einen Rahmen bekommst du nur auf Antrag, als Volljährige und nach einer Bonitätsprüfung, bei der die Bank auch beim KSV1870 nachfragen kann. Ohne regelmäßiges Einkommen fällt er klein aus.',
         ((f'Bei den Konten in dieser Liste kostet ein eingeräumter Rahmen zwischen {pct(disp[0]["sollzins"])} und {pct(disp[-1]["sollzins"])} Sollzinsen im Jahr. ' if len(disp)>1 else '')
          +(f'Bei 600 € Minus über vier Monate sind das mit {pct(disp[-1]["sollzins"])} rund {eur(round(600*disp[-1]["sollzins"]/100*4/12,2))} € Zinsen. ' if disp else '')
          +'Teurer wird eine Überschreitung ohne vereinbarten Rahmen.'),
         (f'Wichtig: Bei {_links(c,plus)} ist das Konto laut Bank nur gratis, solange es im Plus ist. Rutschst du ins Minus, kann dafür das reguläre Kontoführungsentgelt fällig werden, zusätzlich zu den Zinsen. ' if plus else '')
         +'Ab 20. November 2026 muss dich die Bank bei einer längeren, deutlichen Überschreitung schriftlich informieren und bei regelmäßigem Minus eine Beratung anbieten, sofern sie eine hat, und dich auf die Schuldnerberatung hinweisen. Alles zu Rahmen, Überschreitung und den neuen Regeln steht im Ratgeber '+rg('kontoueberziehung','Kontoüberziehung')+'.')),
     ('Auslandssemester mit dem österreichischen Konto',
      _P('Mit Erasmus+ oder einem Joint-Study-Platz bist du schnell ein halbes Jahr im Ausland. Im Euroraum brauchst du dafür kein neues Konto: Kartenzahlungen und Überweisungen in Euro kosten in der EU nicht mehr als in Österreich, und dein Stipendium kommt per SEPA-Überweisung an. Infos zu den Programmen hat der '+_ext(AT_OEAD,'OeAD')+'.',
         'Außerhalb des Euroraums verrechnen fast alle Banken ein Entgelt für Kartenzahlungen in Fremdwährung, oft eine Kombination aus Prozentsatz und Fixbetrag je Zahlung. '
         +(f'Der prozentuale Teil liegt bei den Konten dieser Liste zwischen {pct(min(k["fremdwaehrung_prozent"] for k in fx))} und {pct(max(k["fremdwaehrung_prozent"] for k in fx))}. ' if len(fx)>1 else '')
         +'Bei vielen kleinen Zahlungen, etwa Kaffee und Busticket in Kopenhagen oder Prag, summiert sich der Fixbetrag schneller als der Prozentsatz.',
         _ul(['Nimm eine zweite Karte mit, falls die erste gesperrt wird oder verloren geht. Konten mit inkludierter Kreditkarte stehen in der Liste '+li('mit-kreditkarte','Girokonten mit Kreditkarte')+'.',
              'Wähle bei Kartenzahlung und am Automaten immer die Landeswährung. Die Umrechnung in Euro durch den Händler kostet fast immer mehr.',
              'Behalte deinen Hauptwohnsitz in Österreich oder sag der Bank Bescheid, wenn du ihn abmeldest. Manche Studentenkonten setzen den Wohnsitz voraus.',
              'Prüfe vor der Abreise, ob die Freigabe in der Banking-App auch ohne österreichische SIM-Karte funktioniert.']))),
     ('Nach dem Studium: wann die Bank umstellt',
      _P('Mit dem Ende der Altersgrenze oder des Studiums stellt die Bank dein Konto auf ein reguläres Modell um, meist automatisch. Das neue Konto kostet dann in der Regel ein Kontoführungsentgelt, und auch die Bankomatkarte ist oft nicht mehr gratis. Wohin genau umgestellt wird, steht in der Tabelle oben.',
         'Du musst nicht bei der alten Bank bleiben. Zwei bis drei Monate vor dem Stichtag lohnt ein Vergleich: Mit dem ersten Gehalt erfüllst du bei vielen Konten die Bedingung für die kostenlose Kontoführung. Der Kontowechsel-Service nach dem Verbraucherzahlungskontogesetz überträgt Daueraufträge und Einzugsermächtigungen auf das neue Konto. Wie das geht, steht im Ratgeber '+rg('girokonto-wechseln','Girokonto wechseln')+'.',
         'Melde der Bank ein abgeschlossenes oder abgebrochenes Studium, wenn sie das in ihren Bedingungen verlangt. Wer weiter die Gratis-Konditionen nutzt, obwohl die Voraussetzungen weggefallen sind, muss mit einer Nachverrechnung rechnen.')),
     ('Lehrlinge und junge Berufstätige',
      _P('Nicht jedes Konto in dieser Liste ist nur für Studierende. '
         +(f'Lehrlinge oder alle in Aus- und Weiterbildung nennen die Bedingungen bei {_links(c,lehre,3)}. ' if lehre else '')
         +(f'{_links(c,erwerb)} richtet sich an junge Erwachsene in einem Dienstverhältnis. ' if erwerb else '')
         +(f'Bei {_links(c,eingang)} hängt die Gratis-Kontoführung an einem monatlichen Geldeingang. ' if eingang else ''),
         'Für Lehrlinge unter 18 oder 20 gibt es außerdem eigene Jugendkonten, die meist bis zum 19. oder 20. Geburtstag gratis laufen. Sie stehen in der Liste '+li('jugendkonto','Jugendkonten')+'.',
         (f'Eine Kreditkarte zu Studierenden-Konditionen bieten {_links(c,kk,3)} an. ' if kk else '')
         +'Einen Vergleich der Jugend- und Lehrlingskonten veröffentlicht auch die '+_ext(AT_AK_JUGEND,'Arbeiterkammer Oberösterreich')+'.')),
     ('Quellen',
      _P(_ul(['Altersgrenzen, Nachweise, Entgelte, Sollzinsen und Fremdwährungsentgelte: Preisblätter, Entgeltinformationen und Produktseiten der Banken, verlinkt bei jedem Konto im Vergleich, Stand '+E(c['stand'])+'.',
              'Überziehung ab 20.11.2026: '+_ext(AT_VKRG,'BGBl. I Nr. 36/2026')+'; Girokonten allgemein: '+_ext(AT_AK_FAQ,'Arbeiterkammer Wien, Fragen und Antworten zum Thema Girokonten')+'.',
              'Recht auf ein Basiskonto: '+_ext(AT_AK_RECHT,'Arbeiterkammer, Recht auf ein Girokonto')+'; Kontowechsel: '+_ext(AT_AK_WECHSEL,'Arbeiterkammer Wien, Kontowechsel')+'.',
              'Jugend- und Lehrlingskonten: '+_ext(AT_AK_JUGEND,'Arbeiterkammer Oberösterreich')+'; Auslandsstudium: '+_ext(AT_OEAD,'OeAD')+', '+ABG+'.']))),
    ]
    faq=[
     ('Gilt ein FH-Studium oder eine Pädagogische Hochschule für das Studentenkonto?','In aller Regel ja. Die Banken verlangen eine Bestätigung über ein ordentliches Studium an einer Universität, Fachhochschule oder Hochschule in Österreich. Bei Lehrgängen und außerordentlichen Studien frag vorher nach.'),
     ('Brauche ich als Studentin aus dem Ausland einen Hauptwohnsitz in Österreich?','Bei vielen Banken ja, oft zusammen mit einem Meldezettel. Hast du die Wohnung schon, melde dich zuerst an und eröffne dann das Konto. Klappt es trotzdem nicht, hast du ein Recht auf ein Basiskonto.'),
     ('Kann ich mit 28 noch ein Studentenkonto eröffnen?', ('Bei einigen Banken ja. '+(f'Die höchste Altersgrenze in dieser Liste hat {E(lang[0]["bank"])} mit {E(c["altT"](lang[0]))}. ' if lang else '')+'Bei den meisten anderen endet das Angebot mit dem 27. Geburtstag.')),
     ('Muss ich der Bank sagen, wenn ich mit dem Studium fertig bin?','Meist ja, die Bedingungen verpflichten dich, Änderungen bei den Voraussetzungen zu melden. Viele Banken fragen außerdem selbst nach einem neuen Nachweis. Danach gilt das reguläre Kontomodell.'),
     ('Wird die Studienbeihilfe auf jedes Konto überwiesen?','Ja, auf jedes Girokonto, das auf deinen Namen läuft. Es muss kein Studentenkonto und auch keine österreichische IBAN sein, solange das Konto in der EU geführt wird.'),
    ]
    lede='Hier stehen die Girokonten, die Banken in Österreich für Studierende und junge Erwachsene in Ausbildung anbieten, sortiert nach unserer Bewertung. Darunter erfährst du, wie lange sie gratis bleiben, welche Nachweise du brauchst und was nach dem Studium kommt.'
    return dict(lede=lede,secs=secs,faq=faq)


# =====================================================================
# Kinder und Jugendliche: gemeinsame Helfer
# =====================================================================
DE_JARBSCHG=lambda n: f'https://www.gesetze-im-internet.de/jarbschg/__{n}.html'
DE_BBIG_17='https://www.gesetze-im-internet.de/bbig_2005/__17.html'
AT_VERTRAG='https://www.oesterreich.gv.at/de/themen/gesetze_und_recht/gerichtsorganisation_der_justiz/zivilrecht/8/Seite.1740317'
AT_FERIAL='https://www.oesterreich.gv.at/de/themen/arbeit_beruf_und_pension/berufsleben/jugendrechte-arbeit/Seite.1740314'
AT_LEHRE='https://www.oesterreich.gv.at/de/themen/bildung_und_ausbildung/lehre-und-berufsbildende-schulen/Seite.333902'

def _min(k): return (k.get('alter') or {}).get('min')
def _bar(k): return (k.get('bargeld') or {}).get('text') or ''
def _wlim(k):
    t=_dk(k)+' '+_bar(k)
    m=re.findall(r'(\d+)\s*€\s*(?:/|pro\s)Woche',t)+re.findall(r'Wochenlimit\D{0,10}(\d+)\s*€',t)
    return max(int(x) for x in m) if m else None
def _fw(X):
    v=[k['fremdwaehrung_prozent'] for k in X if k.get('fremdwaehrung_prozent') is not None]
    return (min(v),max(v)) if v else None


# =====================================================================
# Kinderkonto Deutschland
# =====================================================================
def _kk_de(c):
    X=c['lists'].get('kinderkonto') or []
    L=c['link']; pct=c['pct']; rg=c['rg']; li=c['liste']
    n=len(X)
    frei0=[k for k in X if k['kf_jahr']==0]
    geburt=[k for k in X if _min(k)==0]
    ab7=[k for k in X if _min(k)==7]
    kunde=[k for k in X if re.search(r'Elternteil|Kunde',_alt(k))]
    onl=[k for k in X if k.get('eroeffnung') in ('online','beides')]; fil=[k for k in X if k.get('eroeffnung')=='filiale']
    giro=[k for k in X if 'girocard' in _dk(k).lower()]
    deb=[k for k in X if re.search(r'Visa|Mastercard',_dk(k))]
    ab12=[k for k in X if re.search(r'ab 12',_dk(k))]
    zins=sorted([k for k in X if (k.get('habenzins') or 0)>0],key=lambda k:-k['habenzins'])
    akt=[k for k in X if k.get('aktion')]
    um=[k for k in X if re.search(r'danach|automatisch|Umstellung|StartKonto',_alt(k))]
    bis17=[k for k in X if (k.get('alter') or {}).get('max')==17]
    fw=_fw(X)
    rows_k=[(L(k),E(c['altT'](k)),_txt(_dk(k),140),_txt(_bar(k),140)) for k in X]
    rows_u=[(L(k),E(c['altT'](k)),_txt(_alt(k),160)) for k in X]
    jl=li('jugendkonto','Jugendkonten')

    secs=[
     ('Was ein Kinderkonto ist und ab welchem Alter es geht',
      _P('Ein Kinderkonto ist ein Girokonto, das auf den Namen deines Kindes läuft und das du als Elternteil eröffnest und verwaltest. Es läuft auf Guthabenbasis, hat keinen Dispo und kostet bei fast allen Banken keine Kontoführungsgebühr. '
         +(f'In dieser Liste stehen {_n(n,"Konto","Konten")}, {len(frei0)} davon ohne Kontoführungsgebühr. ' if X else ''),
         (f'Schon ab der Geburt geht es bei {_links(c,geburt)}. ' if geburt else '')
         +(f'Ab 7 Jahren starten {_links(c,ab7)}. ' if ab7 else '')
         +'Andere Banken nennen gar kein Mindestalter und nehmen jedes minderjährige Kind. Das genaue Alter steht in der Rangliste oben bei jedem Konto.',
         'Ob Baby oder Grundschulkind: Wann sich ein eigenes Konto lohnt, hängt weniger vom Alter ab als vom Geld, das reinkommt. Für Geldgeschenke zur Geburt, zur Taufe oder vom Patenonkel reicht ein Konto, das nur ihr Eltern bedient. Eine Karte für das Kind wird erst interessant, wenn es regelmäßig Taschengeld bekommt und allein einkaufen geht. Viele Familien fangen damit mit 10 bis 12 Jahren an.',
         'Achte nicht auf den Namen des Produkts. Kinderkonto, Junior-Konto oder Konto u18 meinen oft dasselbe, und manche Banken führen dein Kind mit einem einzigen Konto vom ersten Geburtstag bis zum 18. Konten, die sich eher an Teenager richten, findest du in der Liste '+jl+'.')),
     ('Geschäftsfähigkeit: was dein Kind rechtlich selbst darf',
      _P('Ein Konto auf den Namen eines Kindes ist rechtlich nichts Besonderes. Spannend wird es bei der Frage, was das Kind mit dem Geld darf. Das BGB unterscheidet nach Alter:',
         _ul(['<b>Bis zum 7. Geburtstag</b> ist dein Kind geschäftsunfähig (§ 104 BGB). Was es selbst erklärt, zählt rechtlich nicht. Alles rund ums Konto erledigt ihr Eltern.',
              '<b>Ab 7 bis 17</b> ist es beschränkt geschäftsfähig (§ 106 BGB). Für alles, was ihm nicht nur einen rechtlichen Vorteil bringt, braucht es eure Einwilligung (§ 107 BGB). Ein Geschenk annehmen darf es allein, einen Kauf abschließen grundsätzlich nicht.',
              '<b>Die Ausnahme ist das Taschengeld.</b> Bezahlt dein Kind mit Geld, das ihr ihm zur freien Verfügung gegeben habt, ist der Kauf von Anfang an wirksam (§ 110 BGB). Das gilt auch, wenn es mit der Karte vom eigenen Konto zahlt.']),
         'Für ein Grundschulkind heißt das im Alltag: Das Eis im Freibad, das Sammelalbum am Kiosk oder die Fahrkarte für den Bus sind gedeckt, wenn das Geld vom Taschengeld kommt. Kauft dein Kind dagegen ohne Rücksprache ein teures Spielzeug, hängt der Kauf in der Luft, bis ihr ihn genehmigt (§ 108 BGB). Sagt ihr nein, muss der Händler das Geld zurückgeben.',
         'Bei Käufen in Apps und Spielen kommt es darauf an, womit bezahlt wird. Hängt am Tablet eure eigene Karte oder euer Konto, ist es euer Vertrag, und der Taschengeldparagraf hilft nicht weiter. Sperrt deshalb In-App-Käufe in den Einstellungen des Geräts, bevor das Kind allein spielt.')),
     ('Die Eröffnung: Rolle der Eltern',
      _P('Das Konto eröffnet ihr als gesetzliche Vertreter. Habt ihr gemeinsam das Sorgerecht, vertretet ihr das Kind auch gemeinsam (§ 1629 BGB). Die Bank verlangt deshalb meist die Unterschriften beider Eltern. Hast du allein das Sorgerecht, weist du das nach, zum Beispiel mit einer Bescheinigung des Jugendamts oder einem Gerichtsbeschluss.',
         _ul(['Personalausweis oder Reisepass beider Eltern',
              'Geburtsurkunde des Kindes oder ein Kinderreisepass',
              'die Steuer-ID des Kindes, die es kurz nach der Geburt bekommen hat (§ 154 Abs. 2a AO)',
              'eine Identifizierung per Video, in der Postfiliale oder in der Filiale, je nach Bank auch für das Kind']),
         ((f'Bei {_links(c,kunde)} muss ein Elternteil oder das Kind schon Kunde der Bank sein. ' if kunde else '')
          +(('Alle Konten in dieser Liste eröffnest du online oder per Post, ' if len(onl)==n else f'Online oder per Post eröffnest du {len(onl)} der {n} Konten, ') if X else '')
          +(f'nur in der Filiale geht es bei {_links(c,fil)}. ' if fil else ('eine Filiale brauchst du dafür nicht. ' if X else ''))
          +(f'Für {_w(len(akt),"ein Konto","Konten")} gibt es gerade ein Startguthaben, alle laufenden Aktionen findest du in der Liste '+li('praemie','Girokonten mit Prämie')+'.' if akt else '')),
         'Wichtig für später: Kontoinhaber ist das Kind, ihr handelt nur für es. Das Geld gehört ihm, auch wenn ihr es eingezahlt habt. Ihr dürft davon Dinge für das Kind bezahlen, etwa die Klassenfahrt oder ein Fahrrad, aber nicht euren eigenen Urlaub. Größere Summen müsst ihr wirtschaftlich anlegen (§ 1642 BGB). Einen Kredit oder Dispo für das Kind dürft ihr nicht einfach vereinbaren, dafür bräuchte es die Genehmigung des Familiengerichts (§ 1643 BGB).')),
     ('Karten und Limits für Kinder',
      _P('Für das Kinderkonto gibt es zwei Arten von Karten. Die girocard ist in Deutschland an fast jeder Kasse und jedem Automaten bekannt, im Internet aber kaum zu gebrauchen. Eine Debitkarte von Visa oder Mastercard bucht ebenfalls sofort vom Guthaben ab, funktioniert aber auch online und im Urlaub. '
         +(f'Von den {n} Konten in dieser Liste gibt es bei {len(giro)} eine girocard und bei {len(deb)} eine Visa- oder Mastercard-Debitkarte. ' if X else '')
         +(f'Eine zusätzliche Karte ab 12 Jahren gegen Aufpreis bieten {_links(c,ab12)} an.' if ab12 else ''))+
      (_tbl(['Konto','Alter','Karte laut Bank','Bargeld laut Bank'],rows_k) if rows_k else '')+
      _P('Bei Kindern zählt vor allem, dass die Karte nicht mehr hergibt als geplant. Stellt in der App oder in der Filiale ein Tageslimit oder ein Wochenlimit ein. Ein guter Startwert ist das Taschengeld einer Woche. Erhöhen könnt ihr später immer noch. Viele Banken sperren für Minderjährige automatisch Glücksspiel und Angebote für Erwachsene. Schaut trotzdem nach, ob sich Online-Zahlungen getrennt ausschalten lassen.',
         'Eine Prepaid-Kreditkarte, die nur über vorher aufgeladenes Guthaben läuft, bieten einige Banken erst für Jugendliche an. Für jüngere Kinder ist eine Debitkarte mit niedrigem Limit meist die einfachere Lösung.',
         'Übt das Bezahlen mit eurem Kind ein paar Mal gemeinsam. Zeigt ihm, wie man die PIN verdeckt eingibt, und vereinbart, dass sie nirgends notiert wird. Geht die Karte verloren, sperrt ihr sie über die App oder den Sperr-Notruf 116 116.')),
     ('Taschengeld-Apps oder echtes Konto?',
      _P('Neben den Kinderkonten der Banken gibt es Taschengeld-Apps. Das Prinzip: Ihr ladet Geld in die App, das Kind bekommt eine Karte oder zahlt mit dem Handy, und ihr seht jede Zahlung sofort. Manche Apps bieten Sparziele, Aufgaben gegen Belohnung und Benachrichtigungen bei jedem Einkauf.',
         'Bevor ihr euch für so eine App entscheidet, lohnt ein Blick ins Kleingedruckte:',
         _ul(['<b>Wer ist Vertragspartner?</b> Bei vielen Apps seid ihr Eltern der Kunde, und das Kind nutzt nur eine Karte. Ein Konto mit eigener IBAN auf den Namen des Kindes ist das dann nicht.',
              '<b>Was kostet es?</b> Ein Monatsbeitrag von ein paar Euro summiert sich über Jahre. Die Kinderkonten in dieser Liste kosten dagegen '+(('keine' if len(frei0)==n else 'überwiegend keine')+' Kontoführungsgebühr' if X and len(frei0)*2>=n else 'oft wenig oder nichts')+'.',
              '<b>Kann jemand Geld überweisen?</b> Oma und Opa wollen zum Geburtstag vielleicht direkt etwas schicken. Mit einer eigenen IBAN geht das einfach.',
              '<b>Was passiert später?</b> Ein Bankkonto lässt sich bis 18 und darüber hinaus weiterführen. Eine App müsst ihr irgendwann durch ein Konto ersetzen.']),
         'Für viele Familien ist die Kombination sinnvoll: das Kinderkonto als feste Adresse für Geldgeschenke und Taschengeld, dazu die Banking-App der Bank, in der ihr Limits setzt und die Umsätze anschaut. Die meisten Banken in dieser Liste bieten genau das, ohne Zusatzkosten.')),
     ('Sparen und Zinsen fürs Kind',
      _P('Das Girokonto ist zum Bezahlen da, nicht zum Sparen. '
         +(f'Den höchsten Guthabenzins in dieser Liste zahlt {L(zins[0])} mit {pct(zins[0]["habenzins"])}. ' if zins else 'Die Konten in dieser Liste zahlen auf das Guthaben keine oder kaum Zinsen. ')
         +'Für Geld, das länger liegen bleibt, eignet sich ein Tagesgeldkonto auf den Namen des Kindes. Viele Banken bieten es passend zum Kinderkonto an, oft in derselben App.',
         'Wer bis zum Führerschein oder zum Studium spart, wählt häufig einen Fonds-Sparplan im Kinderdepot. Das ist kein Konto, die Kurse schwanken, dafür ist über viele Jahre mehr Ertrag möglich. Ein paar Euro im Monat reichen für den Anfang.',
         'Guthaben auf dem Kinderkonto ist über die gesetzliche Einlagensicherung bis 100.000 € je Einleger und Bank geschützt (§ 8 EinSiG). Welche Sicherung bei welcher Bank greift, steht bei jedem Konto im Vergleich und im Ratgeber '+rg('einlagensicherung','Einlagensicherung')+'.',
         'Denkt an eines: Was auf Konten und Depots des Kindes liegt, gehört dem Kind. Ab dem 18. Geburtstag entscheidet es allein darüber. Wer das Geld lieber selbst in der Hand behalten will, spart auf eigenen Namen und schenkt später.')),
     ('Steuer: Freistellungsauftrag und NV-Bescheinigung',
      _P('Zinsen und andere Kapitalerträge sind auch bei Kindern steuerpflichtig. Die Abgeltungsteuer beträgt 25 % (§ 32d EStG), die Bank zieht sie direkt ab. Jedes Kind hat aber einen eigenen Sparer-Pauschbetrag von 1.000 € im Jahr (§ 20 Abs. 9 EStG), unabhängig von euren eigenen Freibeträgen.',
         'Damit die Bank den Pauschbetrag berücksichtigt, gebt ihr einen Freistellungsauftrag im Namen des Kindes ab. Bei gemeinsamem Sorgerecht unterschreiben beide Eltern. Liegt das Geld bei mehreren Banken, könnt ihr die 1.000 € aufteilen.',
         'Hat das Kind keine weiteren Einkünfte, kommt eine NV-Bescheinigung in Frage. Die stellt das Finanzamt aus, und dann behält die Bank gar keine Steuer ein (§ 44a EStG). Steuerfrei bleiben die Erträge dann bis zum Grundfreibetrag plus Sparer-Pauschbetrag. Das lohnt sich bei größeren Vermögen, etwa nach einer Erbschaft. Für ein paar hundert Euro Taschengeldguthaben reicht der Freistellungsauftrag.',
         'Schenkungsteuer spielt bei normalen Geldgeschenken keine Rolle. Jeder Elternteil kann seinem Kind innerhalb von zehn Jahren 400.000 € steuerfrei schenken, Großeltern ihrem Enkelkind 200.000 € (§ 16 ErbStG).')),
     ('Vom Kinderkonto zum Jugendkonto',
      _P('Was passiert, wenn aus dem Kind ein Teenager wird, regelt jede Bank anders. '
         +(f'Bei {len(bis17)} der {n} Konten in dieser Liste bleibt es bis zum 18. Geburtstag dasselbe Konto. ' if bis17 else '')
         +(f'Eine automatische Umstellung schon vor 18 oder ein festes Folgemodell nennen {_links(c,um)}. ' if um else '')
         +'Die Bedingungen laut Bank:')+
      (_tbl(['Konto','Alter','Altersgrenze und Umstellung laut Bank'],rows_u) if rows_u else '')+
      _P('Mit etwa 12 bis 14 Jahren ändern sich die Wünsche: Das Kind will online bestellen, mit dem Handy zahlen und mehr selbst entscheiden. Prüft dann, ob euer Konto das mitmacht oder ob ein Wechsel sinnvoll ist. Konten, die auf diese Phase zugeschnitten sind, zeigt die Liste '+jl+'.',
         'Am 18. Geburtstag endet eure Rolle als gesetzliche Vertreter. Ab dann entscheidet euer Kind allein, kann einen Dispo beantragen und das Konto wechseln. Ein Gespräch über Geld vor diesem Tag schadet nie.')),
     ('Quellen',
      _P(_ul(['Alter, Karten, Bargeld, Zinsen, Eröffnung und Umstellung: Preis- und Leistungsverzeichnisse und Produktseiten der Banken, verlinkt bei jedem Konto im Vergleich, Stand '+E(c['stand'])+'.',
              'Geschäftsfähigkeit und Vertretung: '+', '.join(_ext(DE_BGB(x),f'§ {x} BGB') for x in (104,106,107,108,110,1629,1642,1643))+'.',
              'Steuern: '+_ext(DE_ESTG(20),'§ 20 EStG')+', '+_ext(DE_ESTG('32d'),'§ 32d EStG')+', '+_ext(DE_ESTG('44a'),'§ 44a EStG')+', '+_ext(DE_ERBST(16),'§ 16 ErbStG')+'; Steuer-ID: '+_ext(DE_AO_154,'§ 154 AO')+'.',
              'Einlagensicherung: '+_ext(DE_EINSIG,'§ 8 EinSiG')+', '+_ext(DE_BAFIN_ES,'BaFin')+'; Kartensperre: '+_ext(DE_SPERR,'Sperr-Notruf 116 116')+', '+ABG+'.']))),
    ]
    faq=[
     ('Können Großeltern ein Konto für ihr Enkelkind eröffnen?','Ein Konto auf den Namen des Kindes können nur die Eltern als gesetzliche Vertreter eröffnen. Großeltern können aber ein Sparkonto auf ihren eigenen Namen anlegen und bestimmen, dass das Guthaben später dem Enkel zusteht (Vertrag zugunsten Dritter, § 328 BGB). Bis dahin bleibt das Geld ihres.'),
     ('Dürfen Eltern Geld vom Kinderkonto abheben?','Ja, aber nur für das Kind, etwa für die Klassenfahrt oder ein Fahrrad. Für eigene Ausgaben dürfen sie das Geld nicht nehmen, es gehört dem Kind. Wer es trotzdem tut, muss es später zurückzahlen.'),
     ('Wird das Kindergeld auf das Kinderkonto überwiesen?','Normalerweise nicht. Kindergeld bekommen die Eltern auf ihr eigenes Konto. Viele geben aber einen Teil davon per Dauerauftrag als Taschengeld an das Kinderkonto weiter.'),
     ('Kann ein Elternteil das Kinderkonto allein eröffnen?','Nur wenn er das alleinige Sorgerecht hat und das nachweisen kann. Bei gemeinsamem Sorgerecht vertreten beide Eltern das Kind gemeinsam, die Bank verlangt dann beide Unterschriften.'),
     ('Lohnt sich ein Konto schon für ein Baby?','Für Geldgeschenke zur Geburt kann es sinnvoll sein, damit das Geld von Anfang an getrennt vom Haushaltskonto liegt. Für Zinsen ist ein Tagesgeldkonto auf den Namen des Kindes meist besser. '+(f'Ab der Geburt geht ein Girokonto zum Beispiel bei {_links(c,geburt)}.' if geburt else 'Ob ein Konto ab der Geburt möglich ist, steht bei jedem Konto im Vergleich.')),
    ]
    lede='Kinderkonten im Vergleich: Girokonten, die du als Elternteil für dein Kind eröffnest, sortiert nach unserer Bewertung. Darunter erfährst du, was dein Kind rechtlich selbst darf, welche Karte und welches Limit passen, wie es mit Zinsen und Freistellungsauftrag aussieht und was im Teenageralter passiert.'
    return dict(lede=lede,secs=secs,faq=faq)


# =====================================================================
# Jugendkonto Deutschland
# =====================================================================
def _jk_de(c):
    X=c['lists'].get('jugendkonto') or []
    L=c['link']; rg=c['rg']; li=c['liste']; pct=c['pct']
    n=len(X)
    frei0=[k for k in X if k['kf_jahr']==0]
    mins=sorted({_min(k) for k in X if _min(k) is not None})
    ohnemin=[k for k in X if _min(k) is None]
    onl=[k for k in X if k.get('eroeffnung') in ('online','beides')]; fil=[k for k in X if k.get('eroeffnung')=='filiale']
    giro=[k for k in X if 'girocard' in _dk(k).lower()]
    deb=[k for k in X if re.search(r'Visa|Mastercard',_dk(k))]
    nfc=[k for k in X if re.search(r'NFC|digital',_dk(k))]
    ab12=[k for k in X if re.search(r'ab 12',_dk(k))]
    prep=[k for k in X if re.search(r'Prepaid',k.get('kreditkarte') or '')]
    akt=[k for k in X if k.get('aktion')]
    fw=_fw(X)
    rows_k=[(L(k),E(c['altT'](k)),_txt(_dk(k),140),_txt(k.get('kreditkarte') or 'keine Angabe',120)) for k in X]
    rows_u=[(L(k),_txt(_alt(k),170)) for k in X]
    kl=li('kinderkonto','Kinderkonten')

    secs=[
     ('Ab welchem Alter es ein Jugendkonto gibt',
      _P('Ein Jugendkonto ist ein Girokonto für Minderjährige, das schon mehr kann als ein reines Elternkonto: eigene Karte, eigene App, oft Online-Zahlungen. '
         +(f'In dieser Liste stehen {_n(n,"Jugendkonto","Jugendkonten")}, {len(frei0)} davon ohne Kontoführungsgebühr. ' if X else '')
         +(f'Das Mindestalter liegt laut Bank bei {_fmtl([str(x) for x in mins],"oder")} Jahren' if mins else '')
         +(', ' if mins and ohnemin else ('. ' if mins else ''))
         +(f'bei {_links(c,ohnemin)} gibt es keine feste Untergrenze. ' if ohnemin else ''),
         'Die Grenze zwischen Kinder- und Jugendkonto ist in Deutschland fließend. Viele Banken führen ein einziges Konto für alle unter 18 und schalten mit dem Alter mehr Funktionen frei, etwa eine zweite Karte ab 12 oder eine Prepaid-Kreditkarte ab 14. Konten, die eher auf jüngere Kinder und die Kontrolle durch die Eltern zielen, stehen in der Liste '+kl+'.',
         'Typisch für ein Jugendkonto ist der Moment, in dem eigenes Geld dazukommt: der erste Ferienjob, das Gehalt vom Zeitungsaustragen oder die Ausbildungsvergütung. Ab dann brauchst du ein Konto, auf das ein Arbeitgeber überweisen kann, und eine Karte, mit der du auch online bezahlst.')),
     ('Was du als Jugendlicher selbst entscheiden darfst',
      _P('Bis zu deinem 18. Geburtstag bist du beschränkt geschäftsfähig (§ 106 BGB). Verträge brauchen grundsätzlich die Einwilligung deiner Eltern (§ 107 BGB). Es gibt aber zwei wichtige Ausnahmen:',
         _ul(['<b>Taschengeldparagraf (§ 110 BGB):</b> Was du mit Geld bezahlst, das dir deine Eltern zur freien Verfügung gegeben haben, ist sofort wirksam. Das Konzertticket für 45 €, die gebrauchte Jacke über eine Kleinanzeige oder neue Kopfhörer vom Ersparten gehören dazu, solange das Geld wirklich deins ist und der Kauf zu dem passt, wofür es gedacht war.',
              '<b>Arbeit mit Erlaubnis (§ 113 BGB):</b> Erlauben dir deine Eltern, einen Job anzunehmen, darfst du alles selbst regeln, was zu diesem Job gehört, also den Vertrag schließen, kündigen und den Lohn annehmen. Die Erlaubnis können deine Eltern auch wieder einschränken.']),
         'Nicht gedeckt sind Verträge, die dich über Monate binden. Handyvertrag, Fitnessstudio, Streaming-Abo oder Ratenkauf brauchen die Zustimmung deiner Eltern. Ohne sie ist der Vertrag schwebend unwirksam. Fordert der Anbieter deine Eltern zur Genehmigung auf, haben sie zwei Wochen Zeit. Sagen sie nichts, gilt sie als verweigert (§ 108 BGB).',
         'Für die Bank heißt das: Das Jugendkonto eröffnen in Deutschland deine Eltern als gesetzliche Vertreter mit dir zusammen, auch wenn du schon 16 bist. '
         +(f'Online oder per Post geht das bei {len(onl)} der {n} Konten' if X else '')
         +(f', nur in der Filiale bei {_links(c,fil)}. ' if fil else ('. ' if X else ''))
         +'Für dich brauchst du ab 16 einen eigenen Personalausweis, vorher reichen meist Geburtsurkunde oder Kinderreisepass.')),
     ('Ferienjob und Ausbildungsvergütung',
      _P('Arbeiten ist für Schülerinnen und Schüler streng geregelt. Das Jugendarbeitsschutzgesetz zählt alle unter 15 als Kinder, und wer noch vollzeitschulpflichtig ist, wird auch mit 15 bis 17 wie ein Kind behandelt (§ 2 JArbSchG). Für sie ist Beschäftigung grundsätzlich verboten, mit zwei wichtigen Ausnahmen (§ 5 JArbSchG):',
         _ul(['<b>Ab 13 Jahren</b> sind leichte, für Kinder geeignete Tätigkeiten erlaubt, wenn die Eltern einwilligen. Höchstens zwei Stunden am Tag, nicht zwischen 18 und 8 Uhr und nicht vor oder während des Unterrichts. Klassiker sind Zeitungen austragen, Nachhilfe geben oder mit Nachbars Hund rausgehen.',
              '<b>In den Schulferien</b> dürfen vollzeitschulpflichtige Jugendliche ab 15 höchstens vier Wochen im Kalenderjahr arbeiten.']),
         'Mit der Ausbildung ändert sich das. Als Azubi bekommst du eine Ausbildungsvergütung, die mit jedem Ausbildungsjahr steigt. Das Berufsbildungsgesetz schreibt eine Mindestvergütung vor, die jedes Jahr neu festgelegt wird (§ 17 BBiG). In vielen Branchen liegt der Tarif darüber.',
         'Für dein Konto bedeutet das: Dein Arbeitgeber braucht deine IBAN, und das Geld landet auf deinem Konto, nicht auf dem deiner Eltern. Ein Jugendkonto reicht dafür völlig. Viele Azubis bleiben auch nach dem 18. Geburtstag bei ihrer Bank, wenn die das Konto für Auszubildende weiter kostenlos führt. Welche Konten das tun, steht weiter unten bei der Umstellung.')),
     ('Kein Dispo, keine Überziehung',
      _P('Ein Jugendkonto läuft immer auf Guthabenbasis. Einen Dispo bekommst du vor 18 nicht, und zwar nicht aus Vorsicht der Bank, sondern aus rechtlichen Gründen: Ein Kredit für Minderjährige bräuchte neben der Zustimmung der Eltern auch die Genehmigung des Familiengerichts (§ 1643 BGB). Das macht keine Bank für ein Girokonto.',
         'Im Alltag merkst du das, wenn eine Zahlung abgelehnt wird, weil das Guthaben nicht reicht. Das ist gewollt. Ganz ausschließen lässt sich ein Minus aber nicht: Bucht ein Händler eine Kartenzahlung erst Tage später ab oder zieht ein Abo eine Lastschrift ein, kann das Konto kurz ins Minus rutschen. Gleich das dann sofort aus, sonst kann die Bank Gebühren für eine Rücklastschrift berechnen.',
         (f'Eine Prepaid-Kreditkarte ist keine Ausnahme von dieser Regel. Sie funktioniert nur mit vorher aufgeladenem Guthaben, etwa bei {_links(c,prep)}. ' if prep else 'Auch Prepaid-Kreditkarten für Jugendliche funktionieren nur mit vorher aufgeladenem Guthaben. ')
         +'Damit kannst du dort zahlen, wo eine echte Kreditkarte verlangt wird, zum Beispiel bei manchen Buchungen im Internet oder im Urlaub, ohne Schulden machen zu können.',
         'Ab 18 sieht das anders aus. Dann bietet dir die Bank vielleicht einen Dispo an. Wie teuer der ist und wie du ihn im Griff behältst, erklärt der Ratgeber '+rg('dispo','Dispo')+'.')),
     ('Karten, Apple Pay und Google Pay',
      _P((f'Bei {len(giro)} der {n} Konten bekommst du eine girocard, bei {len(deb)} eine Debitkarte von Visa oder Mastercard. ' if X else '')
         +'Die girocard ist für Läden und Automaten in Deutschland gedacht. Mit der Visa- oder Mastercard-Debitkarte zahlst du zusätzlich online und im Ausland. '
         +(f'Eine weitere Karte ab 12 Jahren gibt es gegen Aufpreis bei {_links(c,ab12)}. ' if ab12 else ''))+
      (_tbl(['Konto','Alter','Karte laut Bank','Kreditkarte laut Bank'],rows_k) if rows_k else '')+
      _P('Mit dem Handy zahlen geht, wenn deine Bank die Karte für Apple Pay oder Google Pay freigibt. Ob das auch für Minderjährige gilt, entscheidet jede Bank selbst, und manchmal braucht es dafür die Zustimmung der Eltern in der App. '
         +(f'Kontaktlos oder als digitale Karte nennen die Banken ausdrücklich bei {_links(c,nfc)}. ' if nfc else '')
         +'Frag im Zweifel vor der Eröffnung nach, wenn dir das Bezahlen mit dem Handy wichtig ist.',
         ('Für Klassenfahrt oder Urlaub außerhalb des Euroraums lohnt ein Blick auf den Aufschlag für Zahlungen in fremder Währung. '
          +(f'In dieser Liste liegt er zwischen {pct(fw[0])} und {pct(fw[1])}. ' if fw and fw[0]!=fw[1] else (f'In dieser Liste liegt er bei {pct(fw[0])}. ' if fw else ''))
          +'Bei einer Woche London mit 200 € Ausgaben macht das ein paar Euro Unterschied, bei einem Austauschjahr deutlich mehr.'),
         'Beim Bargeld lohnt ein Blick in die Konditionen. Kostenlos abheben kannst du meist nur an Automaten der eigenen Bank oder ihres Verbunds. An fremden Automaten zeigt dir der Bildschirm vorher an, was der Betreiber verlangt. Brich ab, wenn dir das zu teuer ist, und such einen anderen Automaten oder lass dir an der Supermarktkasse Geld auszahlen, wo das geht.')),
     ('Online einkaufen mit dem Jugendkonto',
      _P('Mit einer Debitkarte bestellst du online genauso wie Erwachsene. Die Bank fragt bei der Zahlung nicht nach deinem Alter. Bei den meisten Zahlungen bestätigst du den Kauf in der Banking-App, das schützt vor fremden Zugriffen auf deine Karte.',
         'Ein paar Regeln, die dir Ärger ersparen:',
         _ul(['<b>Probeabos genau lesen.</b> Viele Apps und Streamingdienste starten gratis und buchen danach jeden Monat ab. Ein Abo ist ein laufender Vertrag, für den du vor 18 die Zustimmung deiner Eltern brauchst. Kündige rechtzeitig, wenn du es nicht willst.',
              '<b>Widerrufsrecht nutzen.</b> Kaufst du online bei einem Händler, kannst du den Vertrag in der Regel 14 Tage lang ohne Begründung widerrufen (§ 312g und § 355 BGB). Es gibt Ausnahmen, etwa für versiegelte Software oder individuell angefertigte Waren.',
              '<b>Kartendaten nie per Chat weitergeben.</b> Wer dir auf Social Media oder im Spiel einen günstigen Deal gegen Vorkasse anbietet, will meistens nur dein Geld.',
              '<b>Benachrichtigungen einschalten.</b> Dann siehst du jede Zahlung sofort und merkst, wenn etwas nicht stimmt.']),
         'Bestellst du etwas, das deutlich über dein Taschengeld hinausgeht, ist der Kauf ohne Zustimmung deiner Eltern nicht wirksam. Der Händler kann die Ware zurückverlangen, und du bekommst dein Geld zurück. Einfacher ist es, vorher zu fragen. Geht deine Karte verloren oder siehst du eine Zahlung, die du nicht kennst, lass die Karte sofort sperren, in der App oder über den Sperr-Notruf 116 116.')),
     ('Mit 18: Umstellung und Wechsel',
      _P('Am 18. Geburtstag bist du voll geschäftsfähig. Deine Eltern verlieren den Zugriff auf dein Konto, und die Bank stellt dein Jugendkonto um. Wohin, steht in den Bedingungen:')+
      (_tbl(['Konto','Alter und Umstellung laut Bank'],rows_u) if rows_u else '')+
      _P('Manche Banken führen das Konto als Konto für junge Leute weiter, das bis zu einer Altersgrenze kostenlos bleibt, teils nur mit Nachweis über Studium oder Ausbildung. Andere stellen auf ihr normales Girokonto um, das dann eine Gebühr oder einen regelmäßigen Geldeingang kostet.',
         'Du musst das nicht hinnehmen. Ab 18 kannst du jederzeit wechseln. Studierst du oder machst eine Ausbildung, schau in die Liste '+li('studenten','Girokonten für Studierende')+'. Arbeitest du schon, sind die '+li('kostenlos','kostenlosen Girokonten')+' der bessere Startpunkt. Wie der Umzug mit Daueraufträgen und Gehalt klappt, steht im Ratgeber '+rg('girokonto-wechseln','Girokonto wechseln')+'.'
         +(f' Für {_w(len(akt),"ein Jugendkonto","Jugendkonten")} dieser Liste gibt es gerade eine Startprämie, mehr in der Liste '+li('praemie','Girokonten mit Prämie')+'.' if akt else ''))),
     ('Quellen',
      _P(_ul(['Alter, Karten, Kreditkarten, Eröffnung und Umstellung: Preis- und Leistungsverzeichnisse und Produktseiten der Banken, verlinkt bei jedem Konto im Vergleich, Stand '+E(c['stand'])+'.',
              'Geschäftsfähigkeit: '+', '.join(_ext(DE_BGB(x),f'§ {x} BGB') for x in (106,107,108,110,113,1643))+'.',
              'Jobs und Ausbildung: '+_ext(DE_JARBSCHG(2),'§ 2 JArbSchG')+', '+_ext(DE_JARBSCHG(5),'§ 5 JArbSchG')+', '+_ext(DE_BBIG_17,'§ 17 BBiG')+'.',
              'Online-Kauf: '+_ext(DE_BGB('312g'),'§ 312g BGB')+', '+_ext(DE_BGB(355),'§ 355 BGB')+'; Kartensperre: '+_ext(DE_SPERR,'Sperr-Notruf 116 116')+', '+ABG+'.']))),
    ]
    faq=[
     ('Kann ich mit 16 ohne meine Eltern ein Girokonto eröffnen?','In Deutschland in der Regel nicht. Bis 18 bist du beschränkt geschäftsfähig, und die Banken lassen das Konto von deinen Eltern als gesetzliche Vertreter mit eröffnen. Du bist aber Kontoinhaber, und das Geld darauf gehört dir.'),
     ('Können meine Eltern sehen, wofür ich mein Geld ausgebe?','Solange du minderjährig bist, vertreten sie dich und haben in der Regel Zugriff auf das Konto und die Umsätze. Wie genau, regelt jede Bank selbst. Ab 18 endet das, dann siehst nur noch du deine Buchungen.'),
     ('Kann meine Ausbildungsvergütung auf das Jugendkonto gehen?','Ja. Gib deinem Ausbildungsbetrieb die IBAN deines Jugendkontos. Ein eigenes Konto ist sogar sinnvoll, damit dein Lohn nicht auf dem Konto deiner Eltern landet. Prüf nur, wie lange die Bank das Konto nach deinem 18. Geburtstag kostenlos weiterführt.'),
     ('Was passiert, wenn mein Jugendkonto ins Minus rutscht?','Das kann passieren, wenn eine Zahlung später gebucht wird. Zahl das Minus schnell aus, sonst können Gebühren oder Mahnungen kommen. Ein Dispo, den du dauerhaft nutzen könntest, ist vor 18 nicht vorgesehen.'),
     ('Muss ich mein Jugendkonto mit 18 kündigen?','Nein, die Bank stellt es von selbst um. Du kannst aber jederzeit kündigen und zu einem Konto wechseln, das besser zu dir passt, etwa einem Konto für Studierende und Azubis.'),
    ]
    lede='Jugendkonten im Vergleich: Girokonten für Teenager, mit eigener Karte und App, sortiert nach unserer Bewertung. Darunter steht, was du mit dem Konto selbst entscheiden darfst, wie es mit Ferienjob und Ausbildungsvergütung läuft und was mit 18 passiert.'
    return dict(lede=lede,secs=secs,faq=faq)


# =====================================================================
# Kinderkonto Österreich
# =====================================================================
def _kk_at(c):
    X=c['lists'].get('kinderkonto') or []
    L=c['link']; eur=c['eur']; pct=c['pct']; rg=c['rg']; li=c['liste']
    n=len(X)
    frei0=[k for k in X if k['kf_jahr']==0]
    geburt=[k for k in X if _min(k)==0]
    ab7=[k for k in X if _min(k)==7]
    karte6=[k for k in X if re.search(r'ab 6|ab 6 Jahren|frühestens ab 6',_alt(k)+' '+_dk(k)+' '+_bar(k))]
    kunde=[k for k in X if re.search(r'Bestandskunde|Kunde sein',_alt(k))]
    onl=[k for k in X if k.get('eroeffnung') in ('online','beides')]; fil=[k for k in X if k.get('eroeffnung')=='filiale']
    nokontakt=[k for k in X if re.search(r'ohne (NFC|Kontaktlos)',_dk(k))]
    lims=[x for x in (_wlim(k) for k in X) if x]
    zins=sorted([k for k in X if (k.get('habenzins') or 0)>=0.5],key=lambda k:-k['habenzins'])
    akt=[k for k in X if k.get('aktion')]
    rows_k=[(L(k),E(c['altT'](k)),_txt(_dk(k),140),_txt(_bar(k),140)) for k in X]
    rows_u=[(L(k),E(c['altT'](k)),_txt(_alt(k),170)) for k in X]
    jl=li('jugendkonto','Jugendkonten')

    secs=[
     ('Kinderkonto in Österreich: für wen und ab wann',
      _P('Kinderkonten sind in Österreich klar von Jugendkonten getrennt. Das Kinderkonto ist für die Zeit vor dem 14. Geburtstag gedacht, also vor der Mündigkeit. Die Eltern eröffnen es, behalten den Überblick und legen fest, was die Karte darf. '
         +(f'In dieser Liste stehen {_n(n,"Kinderkonto","Kinderkonten")}, {len(frei0)} davon ohne Kontoführungsentgelt.' if X else ''),
         (f'Ab der Geburt eröffnen kannst du bei {_links(c,geburt)}. ' if geburt else '')
         +(f'Ab 7 Jahren geht es bei {_links(c,ab7)}. ' if ab7 else '')
         +(f'Die Karte nutzen darf das Kind bei {_links(c,karte6)} frühestens ab 6. ' if karte6 else '')
         +'Bis dahin ist das Konto eher ein Sparplatz für Geldgeschenke, die Karte kommt später.',
         'Sinnvoll wird die Karte, wenn dein Kind allein in die Schule geht, beim Bäcker die Jause kauft oder mit Freunden ins Schwimmbad fährt. Mit einem fixen Taschengeld auf dem Konto lernt es, dass Geld nicht nachwächst, wenn es weg ist. Für Teenager ab 14 gibt es eigene Modelle mit höheren Limits, siehe die Liste '+jl+'.')),
     ('Was Kinder unter 7 und bis 14 rechtlich dürfen',
      _P('Das ABGB staffelt die Geschäftsfähigkeit nach Alter. Für ein Kinderkonto zählen zwei Stufen:',
         _ul(['<b>Unter 7 Jahren</b> ist ein Kind gänzlich geschäftsunfähig. Trotzdem darf es kleine Anschaffungen des täglichen Lebens selbst machen, die Kinder in seinem Alter üblicherweise machen, also etwa eine Wurstsemmel oder ein Zuckerl. So ein Kauf wird wirksam, sobald das Kind bezahlt hat (§ 170 Abs. 3 ABGB). Geschenke ohne Verpflichtung darf es annehmen.',
              '<b>Von 7 bis 13 Jahren</b> ist es unmündig minderjährig und beschränkt geschäftsfähig. Taschengeldgeschäfte wie ein Buch, ein Stickeralbum oder eine Kinokarte gehen allein. Größere Geschäfte sind ohne Zustimmung der Eltern schwebend unwirksam: Sie gelten erst, wenn ihr nachträglich zustimmt.']),
         'Ein Beispiel: Dein Zehnjähriger kauft mit der Kinderkarte um 300 € ein Tablet. Das ist weder eine Kleinigkeit noch altersüblich. Stimmt ihr nicht zu, ist der Kauf von Anfang an ungültig. Der Händler bekommt das Tablet zurück, euer Kind das Geld. In der Praxis verhindern die niedrigen Limits der Kinderkarten solche Käufe meist schon an der Kassa.',
         'Und das Taschengeld selbst? Das darf das Kind für Taschengeldgeschäfte einsetzen, also für das, was Kinder in seinem Alter üblicherweise kaufen. Was über dieses Maß hinausgeht, braucht eure Zustimmung, auch wenn das Kind lange darauf gespart hat. Ein Volksschulkind, das sich vom Ersparten ein Rad um 250 € kaufen will, braucht euch also an seiner Seite. Erst ab 14 lockert das Gesetz diese Regel.',
         'Ein Konto auf den Namen des Kindes eröffnen und führen bleibt in beiden Altersstufen Sache der Eltern. Das Kind wird Kontoinhaber, handelt aber nur im Rahmen der Taschengeldgeschäfte selbst.')),
     ('Eröffnung: Obsorge, Unterlagen und Bestandskunden',
      _P('Für ein Kinderkonto unterschreiben die obsorgeberechtigten Eltern. Leben sie getrennt, verlangt die Bank oft beide Unterschriften oder einen Nachweis, dass ein Elternteil die alleinige Obsorge hat.',
         _ul(['Lichtbildausweis der Eltern',
              'Geburtsurkunde des Kindes',
              'je nach Bank ein Meldezettel des Kindes oder ein Nachweis über den Hauptwohnsitz']),
         ((f'Bei {_links(c,kunde)} muss ein Elternteil selbst schon Kunde der Bank sein. ' if kunde else '')
          +(f'Online oder mit Termin in der Filiale geht die Eröffnung bei {len(onl)} der {n} Konten, ' if X else '')
          +(f'nur in der Filiale bei {_links(c,fil)}. ' if fil else ('' if not X else 'eine Filiale ist nicht zwingend. '))
          +(f'Ein Startguthaben gibt es gerade bei {_w(len(akt),"einem Konto","Konten")} dieser Liste, alle Aktionen stehen in der Liste '+li('praemie','Girokonten mit Prämie')+'.' if akt else '')),
         'Auch wenn ihr einzahlt: Das Guthaben gehört dem Kind. Ihr dürft es für das Kind verwenden, zum Beispiel für den Skikurs oder die Schultasche, nicht aber für eigene Ausgaben. Bei größerem Vermögen, etwa nach einer Erbschaft, kann das Pflegschaftsgericht mitreden.')),
     ('Kinderkarte: Limits, Kontaktlos und Online',
      _P('Die Karte zum Kinderkonto ist eine Debitkarte mit bewusst engen Grenzen. '
         +(f'Die Wochenlimits liegen laut Bank bei {"bis zu " if len(set(lims))>1 else ""}{eur(max(lims))} €. ' if lims else '')
         +(f'Ohne Kontaktlos-Funktion kommen die Karten bei {_links(c,nokontakt)}, das Kind steckt die Karte also immer und gibt den PIN-Code ein. ' if nokontakt else '')
         +'Überweisungen und Zahlungen über dem Limit gehen nur über die Eltern.')+
      (_tbl(['Konto','Alter','Karte laut Bank','Bargeld laut Bank'],rows_k) if rows_k else '')+
      _P('Ein niedriges Limit ist bei Kindern ein Vorteil, kein Nachteil. Ist die Karte weg, ist höchstens ein Wochenbetrag in Gefahr. Und euer Kind lernt, sich das Geld einzuteilen. Ein guter Start: Taschengeld jeden Montag per Dauerauftrag, Limit auf denselben Betrag.',
         'Online-Einkäufe sind bei Kinderkarten oft gar nicht oder erst nach Freischaltung durch die Eltern möglich. Das ist bei Kindern unter 14 meistens auch sinnvoll. Wer Spiele am Handy erlaubt, sollte In-App-Käufe in den Geräteeinstellungen sperren, denn dort zahlt meist die Karte der Eltern.',
         'Bargeld am Bankomaten ist bei den meisten Kinderkonten inkludiert, allerdings nur im Rahmen des Limits. Bei Automaten privater Betreiber können trotzdem Fremdspesen anfallen. Zeigt eurem Kind, welche Bankomaten in der Nähe zur eigenen Bank gehören, und schaut die Spalte zum Bargeld in der Tabelle an.',
         'Geht die Karte verloren, sperrt ihr sie in der Banking-App oder über die Hotline der Bank. Die Nummer gehört ins Handy der Eltern und, sobald es eines hat, auch ins Handy des Kindes.')),
     ('Taschengeld-App, Prepaid-Karte oder Kinderkonto?',
      _P('Statt eines Kinderkontos bieten manche Anbieter Prepaid-Karten oder Taschengeld-Apps an. Ihr ladet Guthaben auf, das Kind zahlt damit, ihr seht alles im Handy. Für den Anfang klingt das bequem. Ein paar Fragen helfen bei der Entscheidung:',
         _ul(['<b>Gibt es eine eigene IBAN für das Kind?</b> Beim Kinderkonto ja. Dann können auch Oma, Opa oder die Taufpatin direkt etwas überweisen.',
              '<b>Was kostet es auf Dauer?</b> '+('Die Kinderkonten in dieser Liste kosten '+('kein Kontoführungsentgelt' if X and len(frei0)==n else 'meist wenig oder nichts')+'. ' if X else '')+'Eine App mit Monatsgebühr kostet über mehrere Jahre schnell mehr als gedacht.',
              '<b>Gibt es Zinsen?</b> Auf Prepaid-Guthaben gibt es normalerweise keine. Manche Kinderkonten verzinsen das Guthaben dagegen gut.',
              '<b>Wie geht es mit 14 weiter?</b> Ein Kinderkonto stellt die Bank auf das Jugendkonto um. Eine App müsst ihr irgendwann ersetzen.']),
         'Wer die Kontrolle einer App möchte, findet sie oft auch beim Kinderkonto selbst: Die meisten Banken zeigen die Umsätze in der App der Eltern und lassen Limits dort ändern. Fragt bei der Eröffnung konkret nach, wie das funktioniert.')),
     ('Zinsen, Sparbuch und KESt',
      _P('Anders als bei Erwachsenen lohnen sich manche Kinderkonten auch als Sparplatz. '
         +(f'Am meisten Habenzins zahlen hier {_links(c,zins[:3])}, bis zu {pct(zins[0]["habenzins"])} im Jahr. Oft gilt der Zins nur bis zu einem Höchstbetrag, der in den Konditionen steht. ' if zins else 'In dieser Liste ist der Habenzins allerdings gering. '),
         'Ein Sparbuch oder Sparkonto bleibt trotzdem eine Option. Es hat keine Karte und dient nur dem Ansparen. Für das Geld zur Erstkommunion oder Firmung, das bis zum Führerschein liegen bleiben soll, passt es oft besser als das Girokonto. Viele Familien nutzen beides: das Kinderkonto für das Taschengeld, das Sparbuch für die großen Geschenke.',
         'Auf Zinsen von Bankguthaben fallen 25 % Kapitalertragsteuer an, auch bei Kindern. Die Bank behält sie automatisch ein, eine Steuererklärung braucht es dafür nicht. Einen Freibetrag für Zinsen gibt es nicht. Hat das Kind kein oder nur ein geringes Einkommen, kann es sich die KESt mit der Regelbesteuerungsoption über die Steuererklärung zurückholen. Das lohnt sich erst bei größeren Beträgen.',
         'Geldgeschenke an das Kind sind steuerfrei, eine Schenkungssteuer gibt es in Österreich nicht. Schenken Eltern oder Großeltern innerhalb eines Jahres mehr als 50.000 €, muss das aber dem Finanzamt gemeldet werden. Wie das Guthaben bei einer Bankpleite geschützt ist, erklärt der Ratgeber '+rg('einlagensicherung','Einlagensicherung')+'.')),
     ('Mit 14 aufs Jugendkonto',
      _P('Am 14. Geburtstag wird dein Kind mündig minderjährig. Ab dann darf es über eigenes Einkommen, etwa aus einer Lehre, und über Taschengeld weitgehend selbst verfügen, solange seine Lebensbedürfnisse nicht gefährdet sind (§ 170 Abs. 2 ABGB). Die Banken reagieren darauf mit eigenen Jugendkonten. '
         +'Altersgrenzen und Umstellung laut Bank:')+
      (_tbl(['Konto','Alter','Altersgrenze und Umstellung laut Bank'],rows_u) if rows_u else '')+
      _P('Meistens passiert die Umstellung automatisch, die IBAN bleibt gleich. Mit dem Jugendkonto kommen höhere Limits, oft eine Karte mit Kontaktlos-Funktion und Online-Zahlungen. Redet vor dem 14. Geburtstag darüber, was sich ändert und welche Regeln in der Familie weiter gelten.',
         'Ein guter Zeitpunkt für neue Abmachungen: Vielleicht übernimmt euer Kind ab 14 selbst die Handy-Wertkarte oder das Geld für Kino und Ausflüge, und das Taschengeld steigt dafür. Wer die Verantwortung schrittweise abgibt, erspart sich mit 18 einen harten Schnitt.',
         'Ihr müsst nicht bei derselben Bank bleiben. Welche Jugendkonten es gibt und wie lange sie gratis bleiben, zeigt die Liste '+jl+'.')),
     ('Quellen',
      _P(_ul(['Alter, Karten, Limits, Habenzinsen, Eröffnung und Umstellung: Preisblätter, Entgeltinformationen und Produktseiten der Banken, verlinkt bei jedem Konto im Vergleich, Stand '+E(c['stand'])+'.',
              'Geschäftsfähigkeit: '+_ext(AT_ABGB_170,'§ 170 ABGB (RIS)')+', '+_ext(AT_VERTRAG,'oesterreich.gv.at, Vertragsabschluss durch Kinder und Jugendliche')+', '+_ext(AT_GESCH,'oesterreich.gv.at, Übersicht Geschäftsfähigkeit')+'.',
              'Kapitalertragsteuer: '+_ext(AT_BMF_KEST,'BMF, Besteuerung von Kapitalerträgen')+', '+_ext(AT_BMF_KAP,'BMF, Einkünfte aus Kapitalvermögen')+'; Schenkungsmeldung: '+_ext(AT_BMF_SCHENK,'BMF')+', '+ABG+'.']))),
    ]
    faq=[
     ('Braucht mein Kind für das Kinderkonto einen eigenen Ausweis?','Meist nicht. Für ein Kinderkonto reichen in der Regel die Geburtsurkunde und der Lichtbildausweis der Eltern. Einen eigenen Ausweis verlangen viele Banken erst beim Jugendkonto.'),
     ('Was passiert mit dem Geld auf dem Kinderkonto, wenn sich die Eltern scheiden lassen?','Nichts, es gehört dem Kind und fällt nicht in die Aufteilung zwischen den Eltern. Wer das Konto weiter verwaltet, hängt von der Obsorge ab.'),
     ('Kann ich das Limit der Kinderkarte erhöhen?','Bei vielen Banken ja, in der App oder in der Filiale. Manche Kinderkonten haben aber feste Obergrenzen, die sich erst mit dem Jugendkonto ändern. Was gilt, steht in der Kartentabelle auf dieser Seite.'),
     ('Ab wann darf mein Kind die Karte allein benutzen?',(f'Das legt die Bank fest. Bei {_links(c,karte6)} ist die Nutzung ab 6 möglich, bei den übrigen ab dem Mindestalter des Kontos. ' if karte6 else 'Das legt die Bank fest, meist ab 6 oder 7 Jahren. ')+'Ob euer Kind so weit ist, entscheidet ihr. Ein guter Test: Kann es sich die PIN merken und weiß es, was es tun soll, wenn die Karte weg ist?'),
     ('Sparbuch oder Kinderkonto: was ist besser?','Für Taschengeld, das ausgegeben wird, das Kinderkonto mit Karte. Für Geldgeschenke, die liegen bleiben sollen, ein Sparbuch oder Sparkonto. Vergleicht die Zinsen, manche Kinderkonten zahlen mehr als ein Sparbuch.'),
    ]
    lede='Kinderkonten in Österreich im Vergleich, sortiert nach unserer Bewertung. Darunter erfährst du, was Kinder unter 14 rechtlich selbst dürfen, wer das Konto eröffnet, welche Limits die Kinderkarte hat, wie es mit Zinsen und KESt aussieht und was mit 14 passiert.'
    return dict(lede=lede,secs=secs,faq=faq)


# =====================================================================
# Jugendkonto Österreich
# =====================================================================
def _jk_at(c):
    X=c['lists'].get('jugendkonto') or []
    L=c['link']; eur=c['eur']; pct=c['pct']; rg=c['rg']; li=c['liste']
    n=len(X)
    frei0=[k for k in X if k['kf_jahr']==0]; bedingt=[k for k in X if k['kf_jahr']>0]
    unter14=sorted([k for k in X if (_min(k) if _min(k) is not None else 14)<14],key=lambda k:_min(k))
    allein=[k for k in X if re.search(r'(ohne|keine) Unterschrift der Eltern',_alt(k))]
    wohn=[k for k in X if re.search(r'Hauptwohnsitz',_alt(k))]
    kunde=[k for k in X if re.search(r'Bestandskunde|Kunde sein',_alt(k))]
    fil=[k for k in X if k.get('eroeffnung')=='filiale']
    kontakt=[k for k in X if re.search(r'kontaktlos',_dk(k),re.I) and not re.search(r'ohne (NFC|Kontaktlos)',_dk(k))]
    lims=[x for x in (_wlim(k) for k in X) if x]
    ue=sorted([k for k in X if k.get('ueberschreitung')],key=lambda k:-k['ueberschreitung'])
    akt=[k for k in X if k.get('aktion')]
    fw=_fw(X)
    rows_k=[(L(k),E(c['altT'](k)),_txt(_dk(k),140),_txt(_bar(k),140)) for k in X]
    rows_u=[(L(k),E(c['altT'](k)),_txt(_alt(k),170),E(_kost(c,k))) for k in X]
    kl=li('kinderkonto','Kinderkonten')

    secs=[
     ('Jugendkonto: ab 14, manchmal früher',
      _P('Das Jugendkonto ist in Österreich das Konto für mündige Minderjährige, also für alle ab 14. Es löst das Kinderkonto ab und begleitet dich durch Schule, Lehre oder Ferialjob, je nach Bank bis 18, 19 oder 20. '
         +(f'In dieser Liste stehen {_n(n,"Jugendkonto","Jugendkonten")}, {len(frei0)} davon ohne Kontoführungsentgelt' if X else '')
         +(f', bei {_links(c,bedingt)} entfällt das Entgelt bis zu einer Altersgrenze. ' if bedingt else ('. ' if X else '')),
         (f'Schon vor 14 bekommst du ein Jugendkonto bei {_links(c,unter14)}, dann eröffnen es deine Eltern als gesetzliche Vertreter. ' if unter14 else '')
         +'Wer jünger ist, findet passende Modelle in der Liste '+kl+'.',
         'Der Unterschied zum Kinderkonto zeigt sich im Alltag: höhere Wochenlimits, meist Kontaktlos-Zahlung, Online-Shopping und eine eigene App, in der du selbst überweist. Das Konto ist für dich da, nicht mehr in erster Linie für deine Eltern.')),
     ('Mündig mit 14: was du selbst darfst',
      _P('Mit 14 wirst du mündig minderjährig. Du bist noch nicht voll geschäftsfähig, darfst aber deutlich mehr als vorher (§ 170 Abs. 2 ABGB):',
         _ul(['Über <b>Einkommen aus eigener Arbeit</b>, etwa dein Lehrlingseinkommen oder den Lohn vom Ferialjob, darfst du selbst verfügen.',
              'Über <b>Sachen, die dir zur freien Verfügung überlassen wurden</b>, also Taschengeld oder Geburtstagsgeld, ebenso.',
              'Die Grenze: Deine grundlegenden Lebensbedürfnisse dürfen nicht gefährdet sein. Wer das ganze Lehrlingseinkommen für ein Moped ausgibt und dann die Monatskarte nicht mehr zahlen kann, überschreitet sie.']),
         'Ein paar Beispiele: Neue Sneakers um 120 € vom eigenen Ersparten sind in Ordnung. Ein Handyvertrag mit 24 Monaten Laufzeit oder ein Ratenkauf brauchen dagegen die Zustimmung deiner Eltern. Ohne sie ist so ein Vertrag schwebend unwirksam und gilt erst, wenn sie nachträglich zustimmen. Ein Wertkartenhandy kaufst du dagegen ohne Probleme selbst.',
         'Online gilt dasselbe. Kaufst du im Spiel eine Währung oder schließt ein Abo für Musik ab, zählt nicht, mit welcher Karte du zahlst, sondern ob der Vertrag zu deinem Alter und deinem Geld passt. Ein einzelner Kauf um ein paar Euro ist kein Problem. Ein Abo, das jeden Monat abbucht, ist ein laufender Vertrag und braucht vor 18 die Zustimmung deiner Eltern.',
         'Wichtig für Lehrlinge: Den Lehrvertrag selbst darfst du nur mit Zustimmung deiner Eltern abschließen. Kleinere Jobs wie Babysitten oder einen Ferialjob darfst du dagegen ab 14 selbst annehmen, solange etwa die Schule nicht darunter leidet. Sonst können deine Eltern den Job untersagen.')),
     ('Eröffnen ohne Eltern?',
      _P('Weil du ab 14 über dein eigenes Einkommen verfügen darfst, lassen manche Banken dich das Jugendkonto ganz allein eröffnen. '
         +(f'Ohne Unterschrift der Eltern geht es laut Bank bei {_links(c,allein)}. ' if allein else '')
         +'Andere verlangen die Unterschrift deiner Eltern bis 18, auch wenn du schon Lehrling bist.',
         _ul(['ein eigener Lichtbildausweis, also Reisepass oder Personalausweis',
              'je nach Bank ein Meldezettel oder ein anderer Nachweis über den Hauptwohnsitz',
              'bei Eröffnung mit den Eltern auch deren Ausweise und eventuell ein Nachweis über die Obsorge']),
         ((f'Einen Hauptwohnsitz in Österreich seit mindestens einem Jahr setzen {_links(c,wohn)} voraus. ' if wohn else '')
          +(f'Bei {_links(c,kunde)} muss ein Elternteil schon Kunde sein. ' if kunde else '')
          +(f'Nur in der Filiale eröffnest du {_links(c,fil)}. ' if fil else '')
          +(f'Für {_w(len(akt),"ein Jugendkonto","Jugendkonten")} dieser Liste gibt es gerade einen Startbonus, Details in der Liste '+li('praemie','Girokonten mit Prämie')+'.' if akt else '')),
         'Auch wenn deine Eltern unterschreiben: Kontoinhaber bist du. Ab 18 entscheidest du allein, wer noch Zugriff hat.')),
     ('Lehrlingseinkommen und Ferialjob',
      _P('Als Lehrling bekommst du jeden Monat ein Lehrlingseinkommen, oft noch Lehrlingsentschädigung genannt. Die Höhe steht normalerweise im Kollektivvertrag deiner Branche und steigt mit jedem Lehrjahr. Dazu kommen Sonderzahlungen wie Urlaubs- und Weihnachtsgeld. Weil das Lehrlingseinkommen niedriger ist als ein Fachkräftegehalt, fällt in der Regel keine oder nur wenig Einkommensteuer an.',
         'Wie viel du in deinem Lehrberuf genau bekommst, erfährst du bei der Lehrlingsstelle der Wirtschaftskammer in deinem Bundesland oder im Berufslexikon des AMS.',
         'Einen Ferialjob darfst du annehmen, sobald du 15 bist und deine Schulpflicht beendet hast. Die Schulpflicht endet nach dem neunten Schuljahr am Tag vor den Sommerferien. Wirst du schon vorher 15, giltst du bis Ferienbeginn noch als Kind im Sinne des Kinder- und Jugendlichenbeschäftigungsgesetzes. Als Ferialarbeiter oder Ferialangestellter hast du einen befristeten Arbeitsvertrag mit Anspruch auf Lohn nach Kollektivvertrag. Ein echtes Ferialpraktikum kann dagegen auch unbezahlt sein.',
         'Für das Konto heißt das: Dein Lehrbetrieb oder Ferialarbeitgeber braucht deine IBAN, und das Geld kommt auf dein eigenes Konto. Gerade wenn du lernst, mit einem Monatsbudget auszukommen, hilft es, Miete, Handy und Monatskarte gleich nach dem Lohneingang per Dauerauftrag wegzubuchen.',
         'Ein einfacher Plan für den ersten Lohn: Zuerst kommt weg, was jeden Monat fix fällig ist. Dann legst du einen festen Betrag auf ein Sparkonto, auch wenn es nur 20 oder 30 € sind. Der Rest ist für Freizeit, Kleidung und Ausgehen. Wer das von Anfang an so macht, steht am Monatsende nicht mit leerem Konto da und hat nach der Lehre schon ein Polster für Führerschein oder erste Wohnung.')),
     ('Keine Überziehung: was bei einem Minus passiert',
      _P('Jugendkonten laufen auf Guthabenbasis. Einen Überziehungsrahmen bekommst du vor 18 nicht, denn einen Kredit dürfen Minderjährige nicht ohne gerichtliche Genehmigung aufnehmen. Ist nichts mehr drauf, lehnt die Karte die Zahlung ab.',
         'Ganz ausgeschlossen ist ein Minus trotzdem nicht. Wird eine Kartenzahlung erst Tage später gebucht oder zieht ein Anbieter eine Lastschrift ein, kann das Konto kurz ins Minus rutschen. Dann verrechnet die Bank Zinsen für die Überschreitung. '
         +(f'In dieser Liste nennen die Preisblätter dafür bis zu {pct(ue[0]["ueberschreitung"])} im Jahr, etwa bei {L(ue[0])}. ' if ue else '')
         +'Bei kleinen Beträgen und wenigen Tagen sind das Cent, aber das Minus sollte trotzdem schnell weg.',
         'Ab 18 kann dir die Bank einen Überziehungsrahmen anbieten. Was der kostet und wann er zur Falle wird, steht im Ratgeber '+rg('kontoueberziehung','Kontoüberziehung')+'.')),
     ('Bankomatkarte, Handy und Online-Shopping',
      _P('Zum Jugendkonto gehört eine Debitkarte, meist mit deutlich mehr Spielraum als beim Kinderkonto. '
         +(f'Die Wochenlimits liegen laut Bank bei {"bis zu " if len(set(lims))>1 else ""}{eur(max(lims))} €. ' if lims else '')
         +(f'Kontaktlos zahlen nennen ausdrücklich {_links(c,kontakt)}. ' if kontakt else ''))+
      (_tbl(['Konto','Alter','Karte laut Bank','Bargeld laut Bank'],rows_k) if rows_k else '')+
      _P('Mit dem Handy zahlen über Apple Pay oder Google Pay geht nur, wenn deine Bank die Karte dafür freigibt. Für Jugendliche handhaben das die Banken unterschiedlich, teils erst ab einem bestimmten Alter oder mit Zustimmung der Eltern. Wenn dir das wichtig ist, frag vor der Eröffnung nach.',
         'Online bezahlst du mit der Debitkarte wie Erwachsene. Bestätigt wird meist in der Banking-App. Pass bei Gratis-Testabos auf, die nach ein paar Tagen kostenpflichtig werden, und gib Kartendaten nie in Chats oder über Links aus Nachrichten ein.',
         ('Auf Reisen außerhalb des Euroraums kostet jede Kartenzahlung einen Aufschlag für Fremdwährung. '
          +(f'Bei den Jugendkonten in dieser Liste liegt er zwischen {pct(fw[0])} und {pct(fw[1])}. ' if fw and fw[0]!=fw[1] else (f'Bei den Jugendkonten in dieser Liste liegt er bei {pct(fw[0])}. ' if fw else ''))
          +'Für die Sprachreise nach England lohnt der Vergleich.'),
         'Bargeld bekommst du an Bankomaten deiner Bank meist ohne Entgelt, die genauen Regeln stehen in der Tabelle. Private Automatenbetreiber verlangen teils eigene Spesen, die die Bank an dich weitergibt. Schau vor dem Abheben auf den Hinweis am Bildschirm und brich ab, wenn eine Gebühr angezeigt wird.')),
     ('Mit 18, 19 oder 20: Umstellung und Wechsel',
      _P('Jugendkonten enden an einer festen Altersgrenze. Danach stellt die Bank meist automatisch auf ein Konto für Erwachsene um, und das kann etwas kosten:')+
      (_tbl(['Konto','Alter','Umstellung laut Bank','Jahreskosten im Vergleich'],rows_u) if rows_u else '')+
      _P('Mit 18 bist du voll geschäftsfähig. Deine Eltern verlieren ihre Rechte am Konto, und du entscheidest allein über Überziehungsrahmen, Kreditkarte und Kündigung. Läuft das Jugendkonto bei deiner Bank noch bis 19 oder 20 weiter, bleibt es so lange meist gratis.',
         'Danach lohnt der Vergleich. Wer studiert, findet passende Konten in der Liste '+li('studenten','Girokonten für Studierende')+'. Wer arbeitet, schaut bei den '+li('kostenlos','kostenlosen Girokonten')+'. Den Umzug mit Lohn und Daueraufträgen erklärt der Ratgeber '+rg('girokonto-wechseln','Girokonto wechseln')+'. Einen eigenen Vergleich für Jugendliche und Lehrlinge veröffentlicht die '+_ext(AT_AK_JUGEND,'Arbeiterkammer Oberösterreich')+'.')),
     ('Quellen',
      _P(_ul(['Alter, Karten, Limits, Überschreitungszinsen, Eröffnung und Umstellung: Preisblätter, Entgeltinformationen und Produktseiten der Banken, verlinkt bei jedem Konto im Vergleich, Stand '+E(c['stand'])+'.',
              'Geschäftsfähigkeit mündiger Minderjähriger, Lehrvertrag und kleinere Arbeiten: '+_ext(AT_ABGB_170,'§ 170 ABGB (RIS)')+', '+_ext(AT_VERTRAG,'oesterreich.gv.at, Vertragsabschluss durch Kinder und Jugendliche')+'.',
              'Lehrlingseinkommen: '+_ext(AT_LEHRE,'oesterreich.gv.at, Lehrlingseinkommen')+'; Ferialjob: '+_ext(AT_FERIAL,'oesterreich.gv.at, Ferialjob')+'.',
              'Jugend- und Lehrlingskonten: '+_ext(AT_AK_JUGEND,'Arbeiterkammer Oberösterreich')+', '+ABG+'.']))),
    ]
    faq=[
     ('Muss das Lehrlingseinkommen auf ein Jugendkonto gehen?','Nein, es kann auf jedes Konto, das auf deinen Namen läuft. Ein Jugendkonto ist dafür aber meist die günstigste Wahl, weil es bis 18, 19 oder 20 gratis bleibt.'),
     ('Kann ich mit 14 ohne meine Eltern ein Konto eröffnen?',(f'Bei manchen Banken ja, laut Bank etwa bei {_links(c,allein)}. ' if allein else 'Bei manchen Banken ja. ')+'Andere verlangen die Unterschrift der Eltern bis 18. Einen eigenen Lichtbildausweis brauchst du in jedem Fall.'),
     ('Darf ich mit 15 einen Handyvertrag abschließen?','Nicht allein. Ein Vertrag mit monatlichen Zahlungen über eine lange Laufzeit braucht bis 18 die Zustimmung deiner Eltern. Ein Wertkartenhandy oder eine Wertkarte kannst du dagegen selbst kaufen.'),
     ('Was tun, wenn meine Karte verloren geht?','Sofort sperren, über die Banking-App, die Hotline deiner Bank oder die Kartensperrhotline unter 0800 204 8800, aus dem Ausland +43 1 204 8800. Die gilt für Debitkarten der meisten österreichischen Banken, bei Neobanken sperrst du in der App.'),
     ('Bekomme ich mit dem Jugendkonto schon einen Überziehungsrahmen?','Nein. Vor 18 läuft das Konto nur auf Guthaben. Rutscht es durch eine spät gebuchte Zahlung trotzdem ins Minus, verrechnet die Bank Überschreitungszinsen, bis du ausgleichst.'),
    ]
    lede='Jugendkonten in Österreich im Vergleich, sortiert nach unserer Bewertung. Darunter liest du, was du ab 14 mit deinem Geld selbst darfst, ob du das Konto ohne Eltern eröffnen kannst, wie es mit Lehrlingseinkommen und Ferialjob läuft und wann die Bank umstellt.'
    return dict(lede=lede,secs=secs,faq=faq)


def texte(land,ctx):
    if land=='de':
        return {'gemeinschaftskonto':_gem_de(ctx),'studenten':_stu_de(ctx),'jugendkonto':_jk_de(ctx),'kinderkonto':_kk_de(ctx)}
    if land=='at':
        return {'gemeinschaftskonto':_gem_at(ctx),'studenten':_stu_at(ctx),'jugendkonto':_jk_at(ctx),'kinderkonto':_kk_at(ctx)}
    return {}
