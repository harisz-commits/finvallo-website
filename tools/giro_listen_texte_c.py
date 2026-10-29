# Erklärtexte für die Girokonto-Bestenlisten: gemeinschaftskonto, studenten, kinder-jugendkonto (DE und AT).
# Aufruf aus girokonto.texte(land, ctx). Zahlen zu Konten kommen immer aus ctx, nie fest im Text.
# Übernimmt die Inhalte der früheren Ratgeber "Gemeinschaftskonto" und "Kinderkonto und Jugendkonto" (ratgeber_konto.py, ratgeber_konto_de.py).
# Rechtliches laut gesetze-im-internet.de, RIS, BMF, oesterreich.gv.at, BaFin und Arbeiterkammer, abgerufen am 29.10.2026.
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
         'Bist du noch keine 18, eröffnen deine Eltern das Konto mit dir zusammen. Konten für Minderjährige laufen ohne Dispo und stehen in der Liste '+li('kinder-jugendkonto','Kinder- und Jugendkonten')+'.')),
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
         'Für Lehrlinge unter 18 oder 20 gibt es außerdem eigene Jugendkonten, die meist bis zum 19. oder 20. Geburtstag gratis laufen. Sie stehen in der Liste '+li('kinder-jugendkonto','Kinder- und Jugendkonten')+'.',
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
# Kinder und Jugendliche Deutschland
# =====================================================================
def _kj_de(c):
    X=c['lists'].get('kinder-jugendkonto') or []
    L=c['link']; eur=c['eur']; pct=c['pct']; rg=c['rg']; li=c['liste']
    n=len(X)
    frei0=[k for k in X if k['kf_jahr']==0]
    geburt=[k for k in X if (k.get('alter') or {}).get('min')==0]
    ab7=[k for k in X if (k.get('alter') or {}).get('min')==7]
    kunde=[k for k in X if re.search(r'Elternteil|Kunde',_alt(k))]
    onl=[k for k in X if k.get('eroeffnung') in ('online','beides')]; fil=[k for k in X if k.get('eroeffnung')=='filiale']
    giro=[k for k in X if 'girocard' in _dk(k).lower()]
    deb=[k for k in X if re.search(r'Visa|Mastercard',_dk(k))]
    ab12=[k for k in X if re.search(r'ab 12',_dk(k))]
    prep=[k for k in X if re.search(r'Prepaid',k.get('kreditkarte') or '')]
    zins=sorted([k for k in X if (k.get('habenzins') or 0)>0],key=lambda k:-k['habenzins'])
    akt=[k for k in X if k.get('aktion')]
    rows_k=[(L(k),E(c['altT'](k)),_txt(_dk(k),150)) for k in X]
    rows_u=[(L(k),_txt(_alt(k),160)) for k in X]

    secs=[
     ('Ab welchem Alter dein Kind ein Konto haben kann',
      _P('Wie viel ein Kind beim Geld selbst entscheiden darf, regelt das BGB in drei Stufen:',
         _ul(['<b>Unter 7 Jahren</b> ist ein Kind geschäftsunfähig (§ 104 BGB). Ein Konto kann trotzdem auf seinen Namen laufen, die Eltern verwalten es vollständig. Das passt für Geldgeschenke zur Geburt oder zur Taufe. '+(f'Ab der Geburt geht das in dieser Liste bei {_links(c,geburt)}.' if geburt else ''),
              '<b>Von 7 bis 17 Jahren</b> ist es beschränkt geschäftsfähig (§ 106 BGB). Es darf mit seinem Taschengeld selbst einkaufen, für alles andere braucht es die Zustimmung der Eltern. '+(f'Ab 7 starten zum Beispiel {_links(c,ab7,3)}.' if ab7 else ''),
              '<b>Ab 18</b> gehört das Konto dem jungen Erwachsenen allein, die Eltern verlieren den Zugriff.']),
         (f'In der Liste stehen {n} Konten für Minderjährige, {len(frei0)} davon ohne Kontoführungsgebühr. ' if X else '')+
         'Die Bezeichnungen sind nicht geschützt. Was die eine Bank Kinderkonto nennt, heißt bei der nächsten Jugendkonto, Junior-Konto oder Starter-Konto, oft für genau dieselbe Altersspanne. Schau deshalb auf das Alter in der Liste, nicht auf den Namen.',
         'Wann ist ein eigenes Konto mit Karte sinnvoll? Eine feste Grenze gibt es nicht. Viele Familien starten mit 10 bis 12 Jahren, wenn das Kind allein zur Schule fährt und mehr als ein paar Euro im Monat bekommt. Vorher reicht oft ein Sparkonto, das die Eltern führen.')),
     ('Wer eröffnet und was ihr dafür braucht',
      _P('Das Konto eröffnen die Eltern als gesetzliche Vertreter. Haben beide das Sorgerecht, müssen auch beide zustimmen (§ 1629 BGB). Bei alleinigem Sorgerecht reicht ein Elternteil mit Nachweis, etwa einem Negativattest des Jugendamts oder einem Gerichtsbeschluss.',
         _ul(['Ausweise beider Eltern',
              'Geburtsurkunde oder Kinderreisepass, ab 16 den eigenen Personalausweis des Kindes',
              'Steuer-ID des Kindes, die es seit der Geburt hat (§ 154 Abs. 2a AO)',
              'Identifizierung per Video, in der Postfiliale oder in der Filiale, je nach Bank auch für das Kind']),
         ((f'Bei {_links(c,kunde)} setzt die Bank voraus, dass ein Elternteil oder das Kind schon Kunde ist. ' if kunde else '')
          +(f'Online oder per Post eröffnen kannst du {len(onl)} der {n} Konten, ' if X else '')
          +(f'nur in der Filiale geht es bei {_links(c,fil)}. ' if fil else ('' if not X else 'eine Filiale brauchst du dafür nicht. '))
          +(f'Gerade gibt es für {_w(len(akt),"ein Konto","Konten")} eine Startprämie oder ein Startguthaben, die aktuellen Aktionen stehen in der Liste '+li('praemie','Girokonten mit Prämie')+'.' if akt else '')),
         'Kontoinhaber ist immer das Kind. Die Eltern handeln nur für es. Daraus folgt etwas, das viele unterschätzen: Das Geld auf dem Konto gehört dem Kind. Eltern dürfen es verwalten und für das Kind ausgeben, aber nicht für sich selbst zurückholen. Sie müssen das Vermögen des Kindes wirtschaftlich anlegen (§ 1642 BGB).')),
     ('Der Taschengeldparagraf in der Praxis',
      _P('Paragraf 110 BGB sagt: Kauft ein Kind ab 7 etwas mit Geld, das ihm die Eltern zur freien Verfügung gegeben haben, ist der Kauf wirksam. Das gilt auch für Kartenzahlungen vom eigenen Konto. Ein paar Beispiele:',
         _ul(['<b>Kinokarte, Comic, Döner mit 12:</b> wirksam, wenn das Geld aus dem Taschengeld stammt.',
              '<b>Gebrauchtes Fahrrad für 150 € mit 14, bezahlt aus angespartem Taschengeld:</b> kann wirksam sein, wenn der Kauf zu dem passt, wofür die Eltern das Taschengeld gegeben haben. Im Zweifel lieber vorher fragen.',
              '<b>Handyvertrag oder Streaming-Abo mit 15:</b> nicht ohne Zustimmung der Eltern. Laufende Verträge mit monatlichen Zahlungen deckt der Taschengeldparagraf nicht, sie sind bis zur Genehmigung schwebend unwirksam (§ 108 BGB).',
              '<b>In-App-Käufe:</b> Hier kommt es darauf an, ob das Kind sie aus seinem Guthaben bezahlt. Über die Karte der Eltern im App-Store greift der Taschengeldparagraf nicht.']),
         'Einen Dispo oder Kredit darf ein Minderjähriger grundsätzlich nicht aufnehmen, dafür bräuchte es zusätzlich die Genehmigung des Familiengerichts (§ 1643 BGB). Deshalb laufen alle Konten in dieser Liste auf Guthabenbasis. Ein Minus ist im Normalfall nicht möglich. Rutscht das Konto doch einmal ins Minus, etwa durch eine spät gebuchte Kartenzahlung, sollten die Eltern es schnell ausgleichen.')),
     ('Karten, Limits und Bargeld',
      _P('Für Minderjährige gibt es zwei Kartentypen. Die girocard ist die klassische Karte für Läden und Automaten in Deutschland, online geht damit wenig. Die Debitkarte von Visa oder Mastercard zahlt ebenfalls direkt vom Guthaben, funktioniert aber auch online, im Ausland und mit dem Handy. '
         +(f'Eine girocard gibt es bei {len(giro)} der {n} Konten, eine Visa- oder Mastercard-Debitkarte bei {len(deb)}. ' if X else '')
         +(f'Eine Karte ab 12 Jahren gegen Aufpreis bieten {_links(c,ab12)} an. ' if ab12 else '')
         +(f'Eine Prepaid-Kreditkarte für Jugendliche gibt es bei {_links(c,prep)}.' if prep else ''))+
      (_tbl(['Konto','Alter','Karte laut Bank'],rows_k) if rows_k else '')+
      _P('Limits stellt ihr in der App oder in der Filiale ein, meist pro Tag oder pro Woche. Für den Anfang reicht ein Limit in Höhe des Wochentaschengelds. Viele Banken sperren Glücksspiel und Erwachsenenangebote für Minderjährige automatisch. Prüft trotzdem, ob ihr Online-Zahlungen getrennt sperren könnt, bis euer Kind damit umgehen kann.',
         'Beim Bargeld unterscheiden sich die Konten stärker. Manche erlauben kostenlose Abhebungen nur an den eigenen Automaten oder im Verbund, andere nur ab einem Mindestbetrag. Wohnt ihr nicht in der Nähe einer Filiale, ist eine Debitkarte, mit der man auch im Supermarkt an der Kasse Geld bekommt, praktisch.',
         'Für den Start hat sich bewährt: Das Taschengeld kommt per Dauerauftrag immer am selben Tag. Die PIN lernt das Kind auswendig, aufgeschrieben wird sie nirgends. In den ersten Monaten schaut ihr euch die Umsätze einmal pro Woche gemeinsam in der App an. So sieht das Kind, wohin das Geld geht, und ihr merkt früh, wenn ein Abo oder ein In-App-Kauf durchgerutscht ist. Geht die Karte verloren, wird sie sofort gesperrt, auch das sollte das Kind wissen.')),
     ('Zinsen und Sparen fürs Kind',
      _P('Auf einem Girokonto bringt Geld kaum Zinsen. '
         +(f'In dieser Liste zahlt den höchsten Guthabenzins {L(zins[0])} mit {pct(zins[0]["habenzins"])}. ' if zins else 'Die Konten in dieser Liste zahlen keine oder kaum Guthabenzinsen. ')
         +'Größere Beträge, etwa Geldgeschenke von Großeltern, gehören deshalb auf ein Tagesgeld- oder Sparkonto auf den Namen des Kindes. Viele Banken bieten das zum Kinderkonto passend an.',
         'Für langfristiges Sparen, etwa bis zum Führerschein oder Studium, nutzen viele Eltern einen Sparplan auf einen breit gestreuten Fonds im Kinderdepot. Das ist eine Geldanlage mit Kursschwankungen, kein Konto. Wichtig ist nur: Was auf Konten und Depots des Kindes liegt, gehört dem Kind. Mit 18 kann es frei darüber verfügen, auch wenn die Eltern sich etwas anderes gewünscht hätten.')),
     ('Steuern: Freistellungsauftrag und NV-Bescheinigung',
      _P('Auch Kinder zahlen Abgeltungsteuer auf Zinsen und andere Kapitalerträge. Jedes Kind hat aber einen eigenen Sparer-Pauschbetrag von 1.000 € im Jahr (§ 20 Abs. 9 EStG). Damit die Bank davon nichts abzieht, braucht sie einen Freistellungsauftrag. Den stellen die Eltern im Namen des Kindes, bei gemeinsamem Sorgerecht mit beiden Unterschriften.',
         'Hat das Kind darüber hinaus keine nennenswerten Einkünfte, gibt es eine NV-Bescheinigung beim Finanzamt (§ 44a EStG). Dann bleiben Kapitalerträge bis zum Grundfreibetrag plus Sparer-Pauschbetrag steuerfrei, die Bank behält gar keine Steuer ein. Für die meisten Kinder reicht der Freistellungsauftrag, die NV-Bescheinigung lohnt sich bei größeren Vermögen, etwa nach einer Erbschaft.',
         'Und die Schenkungsteuer? Eltern können jedem Kind innerhalb von zehn Jahren 400.000 € steuerfrei schenken, jeder Elternteil für sich. Großeltern 200.000 € je Enkelkind. Für Taschengeld und Geldgeschenke zu Geburtstagen spielt das keine Rolle.')),
     ('Was mit 18 passiert',
      _P('Am 18. Geburtstag wird das Kind voll geschäftsfähig. Die Eltern verlieren ihre Vertretungsmacht, ihre Zugänge zum Konto werden gesperrt, und der junge Erwachsene entscheidet allein. Ab jetzt kann er auch einen Dispo oder eine Kreditkarte beantragen. Die Bank stellt das Konto auf ein anderes Modell um:')+
      (_tbl(['Konto','Alter und Umstellung laut Bank'],rows_u) if rows_u else '')+
      _P('Einige Banken stellen auf ein Konto für junge Leute um, das bis Ende 20 kostenlos bleibt, oft nur mit Nachweis über Ausbildung oder Studium. Andere wechseln direkt auf ihr normales Girokonto, das dann eine Gebühr oder einen Geldeingang kostet. Konten für Studierende und Azubis findest du in der Liste '+li('studenten','Girokonten für Studierende')+'.',
         'Redet vor dem 18. Geburtstag über den Dispo. Ein Rahmen von ein paar hundert Euro ist schnell beantragt und teuer, wenn er dauerhaft genutzt wird. Was er kostet und wie man ihn begrenzt, steht im Ratgeber '+rg('dispo','Dispo')+'.')),
     ('Quellen',
      _P(_ul(['Alter, Karten, Zinsen, Eröffnung und Umstellung: Preis- und Leistungsverzeichnisse und Produktseiten der Banken, verlinkt bei jedem Konto im Vergleich, Stand '+E(c['stand'])+'.',
              'Geschäftsfähigkeit und Vertretung: '+_ext(DE_BGB(104),'§ 104 BGB')+', '+_ext(DE_BGB(106),'§ 106 BGB')+', '+_ext(DE_BGB(108),'§ 108 BGB')+', '+_ext(DE_BGB(110),'§ 110 BGB')+', '+_ext(DE_BGB(1629),'§ 1629 BGB')+', '+_ext(DE_BGB(1642),'§ 1642 BGB')+', '+_ext(DE_BGB(1643),'§ 1643 BGB')+'.',
              'Steuern: '+_ext(DE_ESTG(20),'§ 20 EStG')+', '+_ext(DE_ESTG('44a'),'§ 44a EStG')+', '+_ext(DE_ERBST(16),'§ 16 ErbStG')+'; Steuer-ID: '+_ext(DE_AO_154,'§ 154 AO')+'.',
              'Kartensperre: '+_ext(DE_SPERR,'Sperr-Notruf 116 116')+', '+ABG+'.']))),
    ]
    faq=[
     ('Können Großeltern ein Konto für ihr Enkelkind eröffnen?','Ein Konto auf den Namen des Kindes können nur die Eltern als gesetzliche Vertreter eröffnen. Großeltern können aber ein Sparkonto auf ihren eigenen Namen anlegen und bestimmen, dass das Guthaben später dem Enkel zusteht (Vertrag zugunsten Dritter, § 328 BGB). Bis dahin bleibt das Geld ihres.'),
     ('Dürfen Eltern Geld vom Kinderkonto abheben?','Ja, aber nur für das Kind, etwa für die Klassenfahrt oder ein Fahrrad. Für eigene Ausgaben dürfen sie das Geld nicht nehmen, es gehört dem Kind. Wer es trotzdem tut, muss es später zurückzahlen.'),
     ('Was tun, wenn die Karte meines Kindes verloren geht?','Sofort sperren lassen, rund um die Uhr über den Sperr-Notruf 116 116 oder in der Banking-App. Danach eine Ersatzkarte bestellen, die bei manchen Banken eine Gebühr kostet.'),
     ('Wird das Kindergeld auf das Konto des Kindes überwiesen?','Normalerweise nicht. Kindergeld bekommen die Eltern auf ihr Konto. Viele Eltern geben aber einen Teil als Taschengeld per Dauerauftrag an das Kinderkonto weiter.'),
     ('Wie viel Taschengeld ist für das Konto sinnvoll?','Das entscheiden die Eltern. Jugendämter veröffentlichen Empfehlungen, die mit dem Alter steigen, von wenigen Euro pro Woche bei Grundschulkindern bis zu einem Monatsbetrag für Jugendliche. Ab einem Monatsbetrag lohnt sich das Konto mit Karte, weil das Kind dann selbst einteilen muss.'),
    ]
    lede='Hier findest du Girokonten, die Eltern für ihre Kinder und Jugendlichen eröffnen können, sortiert nach unserer Bewertung. Darunter erklären wir, ab wann ein Kind ein Konto haben kann, was es mit dem Taschengeld selbst darf, welche Karte passt und was mit 18 passiert.'
    return dict(lede=lede,secs=secs,faq=faq)


# =====================================================================
# Kinder und Jugendliche Österreich
# =====================================================================
def _kj_at(c):
    X=c['lists'].get('kinder-jugendkonto') or []
    L=c['link']; eur=c['eur']; pct=c['pct']; rg=c['rg']; li=c['liste']
    n=len(X)
    kinder=[k for k in X if k['art']=='kinder']; jugend=[k for k in X if k['art']=='jugend']
    frei0=[k for k in X if k['kf_jahr']==0]; bedingt=[k for k in X if k['kf_jahr']>0]
    geburt=[k for k in X if (k.get('alter') or {}).get('min')==0]
    unter14=sorted([k for k in jugend if ((k.get('alter') or {}).get('min') or 14)<14],key=lambda k:k['alter']['min'])
    allein=[k for k in X if re.search(r'(ohne|keine) Unterschrift der Eltern',_alt(k))]
    wohn=[k for k in X if re.search(r'Hauptwohnsitz',_alt(k))]
    kunde=[k for k in X if re.search(r'Bestandskunde|Kunde sein',_alt(k))]
    fil=[k for k in X if k.get('eroeffnung')=='filiale']
    nokontakt=[k for k in X if re.search(r'ohne (NFC|Kontaktlos)',_dk(k))]
    lim=[]
    for k in X:
        m=re.findall(r'(\d+)\s*€\s*(?:/|pro\s)Woche',_dk(k)+' '+((k.get('bargeld') or {}).get('text') or ''))
        if m: lim.append((k,max(int(x) for x in m)))
    lk=[x for k,x in lim if k['art']=='kinder']; lj=[x for k,x in lim if k['art']=='jugend']
    zins=sorted([k for k in X if (k.get('habenzins') or 0)>=0.5],key=lambda k:-k['habenzins'])
    akt=[k for k in X if k.get('aktion')]
    rows_k=[(L(k),E(c['altT'](k)),_txt(_dk(k),150)) for k in X]
    rows_u=[(L(k),_txt(_alt(k),170)) for k in X]

    secs=[
     ('Ab welchem Alter: Kinderkonto und Jugendkonto',
      _P('Das ABGB teilt Minderjährige in Altersstufen, und genau daran orientieren sich die Banken:',
         _ul(['<b>Unter 7 Jahren</b> darf ein Kind nur ganz kleine Alltagskäufe selbst machen, etwa Süßigkeiten vom Taschengeld. Ein Konto auf seinen Namen ist trotzdem möglich, die Eltern führen es. '+(f'Ab der Geburt geht das bei {_links(c,geburt)}.' if geburt else ''),
              '<b>Von 7 bis 13 Jahren</b> ist es unmündig minderjährig. Es darf geringfügige Geschäfte des täglichen Lebens selbst abschließen, also mit dem Taschengeld eine Jause oder ein Heft kaufen (§ 170 Abs. 3 ABGB). Hier setzen die Kinderkonten mit Karte an.',
              '<b>Ab 14 Jahren</b> ist es mündig minderjährig und darf über eigenes Einkommen, etwa die Lehrlingsentschädigung, selbst verfügen, soweit sein Lebensunterhalt nicht gefährdet ist (§ 170 Abs. 2 ABGB). Ab hier gibt es Jugendkonten.']),
         ((f'In dieser Liste stehen {len(kinder)} Kinderkonten und {len(jugend)} Jugendkonten. ' if X else '')
          +(f'{len(frei0)} davon kosten kein Kontoführungsentgelt, ' if X else '')
          +(f'bei {_links(c,bedingt)} entfällt es bis zu einer Altersgrenze. ' if bedingt else ('' if not X else 'ohne Bedingung. '))
          +(f'Ein Jugendkonto schon vor 14 gibt es bei {_links(c,unter14)}, dann mit den Eltern als Vertretern.' if unter14 else '')))),
     ('Wer eröffnet: Obsorge und eigene Unterschrift ab 14',
      _P('Für ein Kinderkonto braucht es die Eltern oder andere Obsorgeberechtigte. Sie unterschreiben den Vertrag, das Kind wird Kontoinhaber. Leben die Eltern getrennt, verlangen Banken oft die Zustimmung beider Obsorgeberechtigten oder einen Nachweis über die alleinige Obsorge.',
         _ul(['Lichtbildausweis der Eltern',
              'Geburtsurkunde des Kindes, ab dem Jugendkonto meist auch ein eigener Ausweis wie Reisepass oder Personalausweis',
              'Meldezettel oder Nachweis des Hauptwohnsitzes, je nach Bank']),
         ((f'Ein Jugendkonto ab 14 ohne Unterschrift der Eltern eröffnen laut Bank {_links(c,allein)}. Das stützt sich auf das Recht mündiger Minderjähriger, über ihr eigenes Einkommen zu verfügen. Andere Banken verlangen die Unterschrift der Eltern bis 18. ' if allein else 'Bei den meisten Banken unterschreiben die Eltern auch beim Jugendkonto mit. ')
          +(f'Einen Hauptwohnsitz in Österreich seit mindestens einem Jahr setzen {_links(c,wohn)} voraus. ' if wohn else '')
          +(f'Bei {_links(c,kunde)} muss ein Elternteil selbst schon Kunde sein. ' if kunde else '')
          +(f'Nur mit Termin in der Filiale oder bei einer Beraterin eröffnest du {_links(c,fil)}.' if fil else '')),
         'Das Geld auf dem Konto gehört dem Kind. Eltern dürfen es verwalten und für das Kind verwenden, aber nicht für sich selbst. Bei größeren Beträgen, etwa einer Erbschaft, kann das Pflegschaftsgericht mitreden.')),
     ('Taschengeld, Lehrlingsentschädigung und Verträge',
      _P('Was ein Kind mit seinem Konto rechtlich darf, hängt vom Alter und von der Herkunft des Geldes ab. Ein paar Beispiele aus dem Alltag:',
         _ul(['<b>Mit 9 eine Jause, ein Pickerlheft oder eine Kinokarte bezahlen:</b> wirksam, das sind geringfügige Geschäfte des täglichen Lebens.',
              '<b>Mit 12 eine Spielkonsole um 400 € vom Ersparten:</b> nicht ohne Zustimmung der Eltern. Das ist kein geringfügiges Geschäft mehr.',
              '<b>Mit 16 als Lehrling ein Moped aus der Lehrlingsentschädigung:</b> grundsätzlich möglich, solange Essen, Wohnen und Ausbildung nicht darunter leiden.',
              '<b>Handyvertrag oder Streaming-Abo:</b> Verträge mit laufenden Zahlungen brauchen bis 18 in der Regel die Zustimmung der Eltern. Wertkartenhandys sind die einfache Lösung.']),
         'Besonders heikel sind Käufe im Internet und in Spielen. Mit einer Debitkarte kann ein Jugendlicher online genauso bezahlen wie ein Erwachsener, die Bank prüft das Alter dabei nicht. Viele Banken schicken aber bei jeder Zahlung eine Mitteilung in die App. Redet mit eurem Kind darüber, wofür das Geld gedacht ist, bevor ihr Online-Zahlungen freischaltet. Kauft ein Kind ohne Zustimmung etwas, das über seine Altersstufe hinausgeht, ist der Vertrag nicht wirksam, und ihr könnt das Geld zurückfordern. In der Praxis ist das bei Online-Händlern im Ausland aber mühsam.',
         'Einen Kredit, auch einen Überziehungsrahmen, darf ein Minderjähriger nicht ohne gerichtliche Genehmigung aufnehmen. Deshalb laufen Kinder- und Jugendkonten auf Guthabenbasis. Eine Überschreitung ist im Normalfall nicht vorgesehen. Wie Überziehung bei Erwachsenen funktioniert und was sie kostet, steht im Ratgeber '+rg('kontoueberziehung','Kontoüberziehung')+'.')),
     ('Bankomatkarte und Limits',
      _P('Zu fast jedem Kinder- und Jugendkonto gehört eine Debitkarte. Bei Kindern ist sie bewusst eingeschränkt. '
         +(f'Ohne Kontaktlos-Funktion kommen zum Beispiel die Karten bei {_links(c,nokontakt)}. ' if nokontakt else '')
         +(f'Die Wochenlimits bei Kinderkonten liegen laut Bank bei {"bis zu " if len(set(lk))>1 else ""}{eur(max(lk))} €' if lk else '')
         +(f', bei Jugendkonten bei {"bis zu " if len(set(lj))>1 else ""}{eur(max(lj))} €. ' if lj else ('. ' if lk else ''))
         +'Die Eltern können Limits bei vielen Banken senken oder anheben.')+
      (_tbl(['Konto','Alter','Karte und Limit laut Bank'],rows_k) if rows_k else '')+
      _P('Ein Tipp für den Anfang: Setzt das Limit auf das Taschengeld einer Woche. Dann lernt das Kind, dass die Karte nicht mehr hergibt als das Konto. Online-Zahlungen und Zahlungen mit dem Handy schaltet ihr erst frei, wenn es mit der Karte im Geschäft gut klarkommt.',
         'Beim Bargeld sind die meisten Kinder- und Jugendkonten großzügig: Behebungen an Bankomaten in Österreich sind in der Regel inkludiert. Fremde Spesen von privaten Automatenbetreibern können trotzdem anfallen. Das steht bei jedem Konto im Vergleich.')),
     ('Zinsen und KESt auf dem Kinderkonto',
      _P(('Einige Kinderkonten verzinsen das Guthaben deutlich besser als ein normales Girokonto. '
          +(f'Den höchsten Habenzins in dieser Liste zahlen {_links(c,zins[:3])}, bis zu {pct(zins[0]["habenzins"])} im Jahr. Oft gilt das nur bis zu einem Höchstbetrag, der in den Konditionen steht. ' if zins else 'In dieser Liste sind die Habenzinsen aber gering. '))
         +'Für größere Beträge lohnt trotzdem ein Vergleich mit Sparkonten.',
         'Ein Sparbuch oder Sparkonto ist etwas anderes als ein Kinderkonto: Es hat keine Karte, keine Überweisungen nach außen und dient nur dem Ansparen. Für Geldgeschenke von Oma und Opa, die bis zum Führerschein liegen bleiben sollen, ist es oft die bessere Wahl. Für Taschengeld, das ausgegeben werden soll, ist das Kinderkonto mit Karte praktischer. Viele Familien kombinieren beides.',
         'Auf Zinsen von Bankguthaben fallen 25 % Kapitalertragsteuer an, auch bei Kindern. Die Bank zieht sie automatisch ab, damit ist die Steuer erledigt. Einen Freibetrag wie den Sparer-Pauschbetrag in Deutschland gibt es nicht. Hat das Kind kein oder nur ein geringes Einkommen, kann es sich die KESt über die Regelbesteuerungsoption in der Steuererklärung zurückholen. Bei ein paar Euro Zinsen lohnt der Aufwand selten, bei einer größeren Summe schon.',
         'Geldgeschenke an das Kind sind steuerfrei. Eine Schenkungssteuer gibt es in Österreich nicht. Schenken Eltern oder Großeltern innerhalb eines Jahres mehr als 50.000 €, muss das aber dem Finanzamt gemeldet werden.'
         +(f' Viele Banken zahlen zur Eröffnung außerdem ein Startguthaben, gerade bei {_w(len(akt),"einem Konto","Konten")} dieser Liste. Die Aktionen stehen in der Liste '+li('praemie','Girokonten mit Prämie')+'.' if akt else ''))),
     ('Mit 14, 18 oder 20: wann umgestellt wird',
      _P('Kinder- und Jugendkonten haben feste Altersgrenzen. Die Bank stellt das Konto beim Erreichen um, meist automatisch: zuerst vom Kinder- auf das Jugendkonto, später auf ein Konto für Erwachsene. Das passiert je nach Bank mit 18, 19, 20 oder 21.')+
      (_tbl(['Konto','Alter und Umstellung laut Bank'],rows_u) if rows_u else '')+
      _P('Mit 18 enden die Rechte der Eltern. Der junge Erwachsene kann sie als Verfügungsberechtigte streichen, einen Überziehungsrahmen beantragen und das Konto selbst kündigen. Wer studiert, bekommt bei vielen Banken danach ein Studentenkonto, siehe '+li('studenten','Girokonten für Studierende')+'. Wer arbeitet, findet Konten ohne Kontoführungsentgelt in der Liste '+li('kostenlos','kostenlose Girokonten')+'.')),
     ('Checkliste für Eltern vor der Eröffnung',
      _P(_ul(['Ab welchem Alter gibt es die Karte, und hat sie Kontaktlos- und Online-Funktion?',
              'Wie hoch ist das Wochenlimit, und können wir es in der App selbst ändern?',
              'Sehen wir als Eltern die Umsätze, auch beim Jugendkonto?',
              'Muss ein Elternteil Kunde der Bank sein, und braucht es beide Unterschriften?',
              'Wie hoch ist der Habenzins, und bis zu welchem Betrag gilt er?',
              'Wann und auf welches Konto wird umgestellt, und was kostet es danach?',
              'Gibt es eine Filiale oder Beratung in der Nähe, falls die Karte gesperrt werden muss?'],'checks'),
         'Nach der Eröffnung hilft ein fester Rhythmus. Überweist das Taschengeld per Dauerauftrag, zum Beispiel jeden Montag oder am Monatsersten. Setzt euch anfangs regelmäßig zusammen und schaut, was gekauft wurde. Wer früh lernt, ein Wochenbudget einzuteilen, hat es mit der ersten Lehrlingsentschädigung oder dem ersten Ferialjob leichter. Und erklärt eurem Kind, dass es den PIN-Code niemandem verrät, auch nicht Freunden.',
         'Einen Vergleich speziell für Jugendliche und Lehrlinge veröffentlicht die '+_ext(AT_AK_JUGEND,'Arbeiterkammer Oberösterreich')+'. Bei Problemen mit der Bank hilft die Konsumentenberatung der Arbeiterkammer in deinem Bundesland.')),
     ('Quellen',
      _P(_ul(['Alter, Karten, Limits, Habenzinsen, Eröffnung und Umstellung: Preisblätter, Entgeltinformationen und Produktseiten der Banken, verlinkt bei jedem Konto im Vergleich, Stand '+E(c['stand'])+'.',
              'Geschäftsfähigkeit Minderjähriger: '+_ext(AT_ABGB_170,'§ 170 ABGB (RIS)')+', '+_ext(AT_GESCH,'oesterreich.gv.at, Geschäftsfähigkeit')+'.',
              'Kapitalertragsteuer: '+_ext(AT_BMF_KEST,'BMF, Besteuerung von Kapitalerträgen')+', '+_ext(AT_BMF_KAP,'BMF, Einkünfte aus Kapitalvermögen')+'; Schenkungsmeldung: '+_ext(AT_BMF_SCHENK,'BMF')+'.',
              'Jugend- und Lehrlingskonten: '+_ext(AT_AK_JUGEND,'Arbeiterkammer Oberösterreich')+', '+ABG+'.']))),
    ]
    faq=[
     ('Braucht mein Kind für das Konto einen eigenen Ausweis?','Für ein Kinderkonto reichen meist die Geburtsurkunde und der Ausweis der Eltern. Für ein Jugendkonto verlangen viele Banken einen eigenen Lichtbildausweis des Kindes, also Reisepass oder Personalausweis.'),
     ('Kann mein Kind mit der Karte online einkaufen?','Bei Jugendkonten meist ja, bei Kinderkonten oft nicht oder erst nach Freischaltung durch die Eltern. Manche Kinderkarten haben auch keine Kontaktlos-Funktion. Das steht in der Kartentabelle auf dieser Seite.'),
     ('Muss die Lehrlingsentschädigung auf ein Jugendkonto gehen?','Nein, sie kann auf jedes Konto, das auf den Namen des Lehrlings läuft. Ein Jugendkonto ist dafür aber meist die günstigste Wahl, weil es bis 19 oder 20 gratis bleibt.'),
     ('Was passiert mit dem Geld auf dem Kinderkonto, wenn sich die Eltern scheiden lassen?','Nichts, es gehört dem Kind und fällt nicht in die Aufteilung zwischen den Eltern. Wer das Konto weiter verwaltet, hängt von der Obsorge ab.'),
     ('Was tun, wenn die Karte meines Kindes verloren geht?','Sofort sperren, über die Banking-App, die Hotline der Bank oder die Kartensperrhotline unter 0800 204 8800, aus dem Ausland +43 1 204 8800. Die gilt für Debitkarten der meisten österreichischen Banken, bei Neobanken sperrst du in der App. Die Ersatzkarte ist bei Kinder- und Jugendkonten oft gratis, das steht in den Konditionen.'),
    ]
    lede='Diese Liste zeigt Kinderkonten und Jugendkonten in Österreich, sortiert nach unserer Bewertung. Darunter erfährst du, ab welchem Alter dein Kind ein Konto haben kann, wer unterschreiben muss, welche Limits die Karte hat und wann die Bank umstellt.'
    return dict(lede=lede,secs=secs,faq=faq)


def texte(land,ctx):
    if land=='de':
        return {'gemeinschaftskonto':_gem_de(ctx),'studenten':_stu_de(ctx),'kinder-jugendkonto':_kj_de(ctx)}
    if land=='at':
        return {'gemeinschaftskonto':_gem_at(ctx),'studenten':_stu_at(ctx),'kinder-jugendkonto':_kj_at(ctx)}
    return {}
