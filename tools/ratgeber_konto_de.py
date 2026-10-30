# Ratgeber (nur DE) zu Girokonten: Dispo, Gemeinschaftskonto, P-Konto, Kinder- und Jugendkonto, Konto für Selbstständige.
# Zahlen zu Konten kommen live aus daten/de/girokonten.json (json.load, Pfad relativ zu dieser Datei).
# Rechtliches: §§ 504, 504a, 505 BGB, Art. 247a § 2 EGBGB (BGH XI ZR 46/20), Umsetzung der Richtlinie (EU) 2023/2225 (BGBl. 2026 I Nr. 139, ab 20.11.2026),
# §§ 850k, 850l, 899 ff. ZPO, Pfändungsfreigrenzenbekanntmachung 2026, § 8 EinSiG, BFH II R 33/10, §§ 104 bis 110 und 1629 BGB, § 19 UStG, § 147 AO;
# laut gesetze-im-internet.de, recht.bund.de, bmj.de, bafin.de und verbraucherzentrale.de, abgerufen am 28.10.2026.
# hreflang-Paare: dispo ↔ kontoueberziehung, p-konto ↔ pfaendungsschutzkonto, sonst gleiche Slugs.
# Aufruf aus ratgeber.build('de'): register(art,P,eur)
import html,json,os,re
E=lambda s: html.escape(str(s)) if s is not None else ''
DATA=os.path.join(os.path.dirname(os.path.abspath(__file__)),'daten','de','girokonten.json')
BGB=lambda n: f'https://www.gesetze-im-internet.de/bgb/__{n}.html'
ZPO=lambda n: f'https://www.gesetze-im-internet.de/zpo/__{n}.html'
BGBL_2026_139='https://www.recht.bund.de/bgbl/1/2026/139/regelungstext.pdf'
BAFIN_DISPO='https://www.bafin.de/SharedDocs/FAQs/DE/Verbraucher/Bank/Produkte/Girokonto/DispoUeberziehungskredit/03_dispokredit_streichung_reduzierung.html'
BAFIN_ES='https://www.bafin.de/DE/verbraucherinnen-verbraucher/themen-finanzprodukte/geldanlage/einlagensicherung-anlegerentschaedigung/einlagensicherung-anlegerentschaedigung_node.html'
EINSIG_8='https://www.gesetze-im-internet.de/einsig/__8.html'
KWG_ANH='https://www.gesetze-im-internet.de/kredwg/anhang_i.html'
VZ_PKONTO='https://www.verbraucherzentrale.de/wissen/geld-versicherungen/kredit-schulden-insolvenz/fragen-und-antworten-zum-pfaendungsschutzkonto-pkonto-5959'
PFGR_2026='https://www.gesetze-im-internet.de/pf_ndfreigrbek_2026/BJNR0500A0026.html'
BMJ_PF='https://www.bmj.de/DE/Themen/FinanzenUndAnlegerschutz/ZwangsvollstreckungPfaendungsschutz/Pfaendungsfreigrenzen.html'
USTG_19='https://www.gesetze-im-internet.de/ustg_1980/__19.html'
AO_147='https://www.gesetze-im-internet.de/ao_1977/__147.html'
ABGERUFEN='abgerufen am 28.10.2026'

def _tbl(head,rows):
    h=''.join(f'<th>{c}</th>' for c in head)
    b=''.join('<tr>'+''.join(f'<td>{c}</td>' for c in r)+'</tr>' for r in rows)
    return f'<div class="tbl wide"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'
def _ext(u,t): return f'<a href="{E(u)}" target="_blank" rel="noopener">{E(t)} ↗</a>'
def _pct(x):
    s=f'{x:.3f}'.rstrip('0').rstrip('.').replace('.',','); return s+' %'
def _fmtl(L): return ', '.join(L[:-1])+' und '+L[-1] if len(L)>1 else (L[0] if L else '')
def _slug(s): return re.sub(r'-+','-',re.sub(r'[^a-z0-9]+','-',s.lower().replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss'))).strip('-')
def _load():
    d=json.load(open(DATA,encoding='utf-8')); ks=[k for k in d['konten'] if k.get('aufnehmen',True)]
    for k in ks: k.setdefault('slug',_slug(k['bank']+' '+k['name']))
    return d,ks

def register(art,P,eur):
    d,ks=_load()
    def L(k,label=None): return f'<a class="lnk" href="{P}de/girokonto/{ {'student':'bestenlisten/studenten/','jugend':'bestenlisten/jugendkonto/','kinder':'bestenlisten/kinderkonto/'}.get(k.get('art'),'') }#gk-{k["slug"]}">{E(label or k["name"])}</a> <small class="mut">({E(k["bank"])})</small>'
    G1=f'{P}de/girokonto/'; B=f'{G1}bestenlisten/'; RG=f'{P}de/ratgeber/'
    alle=[k for k in ks if k['art'] in ('standard','premium')]
    kfT=lambda k:'kostenlos' if k['kf_jahr']==0 else f'{eur(k["kf_jahr"])} € im Jahr'
    altT=lambda k:E((k.get('alter') or {}).get('text') or 'keine Angabe')
    debT=lambda k:E((k.get('debitkarte') or {}).get('text') or 'keine Angabe')
    wegT=lambda k:E({'online':'nur online','filiale':'in der Filiale','beides':'online oder in der Filiale'}.get(k.get('eroeffnung'),'keine Angabe'))

    # ---------- 1. Dispo ----------
    dispo=sorted([k for k in alle if k.get('sollzins') is not None],key=lambda k:(k['sollzins'],k['kf_jahr']))
    ged=sorted([k for k in alle if k.get('ueberschreitung') is not None],key=lambda k:(k['ueberschreitung'],k['kf_jahr']))
    ohne=[k for k in alle if k.get('sollzins') is None and k.get('ueberschreitung') is None]
    gleich=[k for k in alle if k.get('sollzins') is not None and k.get('ueberschreitung')==k['sollzins']]
    dmin,dmax=dispo[0],dispo[-1]; gmin,gmax=ged[0],ged[-1]
    drow=[(L(k),_pct(k['sollzins']),_pct(k['ueberschreitung']) if k.get('ueberschreitung') is not None else 'keine Angabe',kfT(k)) for k in dispo[:10]]
    art('de','dispo',pair='kontoueberziehung',
      h1='Dispo in Deutschland: Dispokredit, geduldete Überziehung und deine Rechte',
      mt='Dispo Deutschland: Zinsen, Rechte, Alternativen | Finvallo',
      desc=f'Dispokredit in Deutschland: eingeräumte und geduldete Überziehung, Dispozinsen von {_pct(dmin["sollzins"])} bis {_pct(gmax["ueberschreitung"])} im Vergleich, Warnpflicht der Bank, Kündigung und Alternativen.',
      about='Girokonten in Deutschland',
      lede='Der Dispo ist der teuerste Kredit, den die meisten Menschen je nutzen, und der einzige, den sie nie beantragt haben. Das Gesetz schützt dich dabei mehr, als viele wissen.',
      kurz=(f'Der Dispo ist eine eingeräumte Überziehung (§ 504 BGB): Die Bank erlaubt dir bis zu einem festen Betrag ins Minus. Alles darüber hinaus ist eine geduldete Überziehung (§ 505 BGB), die meist mehr kostet. '
            f'Im Vergleich liegen die Dispozinsen je nach Konto bei {_pct(dmin["sollzins"])} bis {_pct(dmax["sollzins"])}, bei geduldeter Überziehung bei {_pct(gmin["ueberschreitung"])} bis {_pct(gmax["ueberschreitung"])}. '
            'Nutzt du den Dispo sechs Monate lang zu mehr als 75 % aus, muss dir die Bank eine Beratung anbieten. Ab 20. November 2026 muss sie dich außerdem 30 Tage vor einer Kürzung informieren und eine Rückzahlung in zwölf Raten anbieten.'),
      secs=[
       ('Eingeräumte und geduldete Überziehung',f'''<div class="prose"><p>Das BGB unterscheidet zwei Fälle:</p><ul>
<li><b>Eingeräumte Überziehung</b> (§ 504 BGB), der Dispo: Die Bank räumt dir vertraglich einen Rahmen ein, meist das Zwei- bis Dreifache deines monatlichen Geldeingangs. Du kannst ihn nutzen, ohne jedes Mal zu fragen. Zinsen zahlst du nur auf den tatsächlich genutzten Betrag, tagesgenau.</li>
<li><b>Geduldete Überziehung</b> (§ 505 BGB): Du überziehst ohne Dispo oder über den Dispo hinaus, und die Bank lässt die Buchung durch. Sie muss das nicht. Sie kann Lastschriften zurückgeben und Überweisungen ablehnen, und sie darf dafür einen höheren Zins verlangen.</li></ul>
<p>Einen Anspruch auf einen Dispo hast du nicht. Die Bank räumt ihn nach einer Bonitätsprüfung ein, meist mit Schufa-Auskunft, und verlangt regelmäßige Eingänge wie Gehalt oder Rente. Bei einem Basiskonto gibt es keinen Dispo, es läuft auf Guthabenbasis. Mehr dazu im Ratgeber <a href="{RG}basiskonto/">Basiskonto</a>.</p></div>'''),
       ('Was der Dispo kostet',_tbl(['Konto','Dispozins','Geduldete Überziehung','Kontoführung'],drow)+
        f'''<div class="prose"><p>Die Tabelle zeigt die zehn Konten für alle mit dem niedrigsten Dispozins. Über alle {len(alle)} Konten für alle im Vergleich reicht die Spanne beim Dispo von {_pct(dmin["sollzins"])} ({L(dmin)}) bis {_pct(dmax["sollzins"])} ({L(dmax)}). Für eine geduldete Überziehung verlangen die Banken {_pct(gmin["ueberschreitung"])} ({L(gmin)}) bis {_pct(gmax["ueberschreitung"])} ({L(gmax)}). Bei {len(gleich)} Konten kostet die geduldete Überziehung dasselbe wie der Dispo, bei {len(ohne)} Konten gibt es keinen Dispo oder keine Angabe dazu, vor allem bei Banken aus dem EU-Ausland.</p>
<p>Eine gesetzliche Obergrenze für Dispozinsen gibt es in Deutschland nicht. Die Bank muss den Sollzins aber klar, eindeutig und auffallend nennen, im Preisaushang und auf ihrer Website (Art. 247a § 2 EGBGB). Der Bundesgerichtshof hat 2021 entschieden, dass eine Angabe wie „bis zu 10,90 %“ ohne den Mindestzins nicht reicht (Urteil XI ZR 46/20). Meist ist der Dispozins variabel und an einen Referenzzins gekoppelt. Steigt er, muss dich die Bank informieren.</p>
<p>Ein Rechenbeispiel: 1.500 € dauerhaft im Minus kosten bei 9 % Zinsen 135 € im Jahr, bei 15 % sind es 225 €. Ein Ratenkredit über dieselbe Summe wäre bei den meisten Banken günstiger und nach zwölf Raten erledigt.</p></div>'''),
       ('Wann die Bank dich beraten muss',f'''<div class="prose"><p>Zwei Pflichten stehen schon heute im Gesetz:</p><ul class="checks">
<li><b>Dispo dauerhaft genutzt</b> (§ 504a BGB): Nutzt du den Dispo sechs Monate ununterbrochen im Durchschnitt zu mehr als 75 % des Rahmens aus, muss dir die Bank ein Beratungsgespräch über günstigere Alternativen anbieten, etwa einen Ratenkredit. Annehmen musst du es nicht.</li>
<li><b>Geduldete Überziehung</b> (§ 505 Abs. 2 BGB): Bist du drei Monate ununterbrochen im Durchschnitt mit mehr als 50 % deines monatlichen Geldeingangs geduldet überzogen, gilt dieselbe Beratungspflicht.</li></ul>
<p>Mit dem Gesetz zur Umsetzung der neuen EU-Verbraucherkreditrichtlinie, das ab <b>20. November 2026</b> gilt, kommen weitere Pflichten dazu: Bei einer erheblichen geduldeten Überziehung von mehr als einem Monat muss dich die Bank unverzüglich über Betrag, Zins und Rückzahlungstermin informieren. Überziehst du regelmäßig, muss sie dir eine Beratung anbieten und dich kostenlos an eine Schuldnerberatung verweisen. Werbung für Dispokredite braucht künftig einen deutlichen Warnhinweis, dass Kreditaufnahme Geld kostet.</p></div>'''),
       ('Was die Bank darf',f'''<div class="prose"><p>Die Bank darf den Dispo ganz oder teilweise kündigen, so die BaFin. In der Regel tut sie das, wenn sich deine wirtschaftlichen Verhältnisse verschlechtert haben oder keine regelmäßigen Eingänge mehr kommen. Bisher reichte dafür eine angemessene Frist nach den AGB. Ab 20. November 2026 gilt:</p><ul class="checks">
<li>Die Bank muss dich <b>mindestens 30 Tage</b>, bevor eine Kürzung oder Streichung wirksam wird, informieren.</li>
<li>Vor einer Zwangsvollstreckung muss sie dir anbieten, den gekürzten Betrag <b>in zwölf gleichen Monatsraten</b> zum Dispozins zurückzuzahlen, ohne zusätzliche Kosten. Schneller zurückzahlen darfst du immer, eine Vorfälligkeitsentschädigung gibt es beim Dispo nicht.</li>
<li>Du bekommst <b>mindestens einmal im Monat</b> eine Information über den genutzten Betrag, den Saldo und den Sollzins, auf Papier oder im Online-Banking.</li>
<li>Die Bank darf dir keinen Dispo einräumen oder erhöhen, den du nicht ausdrücklich verlangt hast.</li></ul>
<p>Das gilt auch für Konten, die vor dem Stichtag eröffnet wurden. Was die Bank nicht darf: Zinsen ohne klare Regel anheben oder dich wegen einer kurzen Überziehung sofort kündigen. Bei Streit hilft die Verbraucherschlichtungsstelle bei der Deutschen Bundesbank oder die private Schlichtung des Bankenverbands.</p></div>'''),
       ('Alternativen zum Dispo',f'''<div class="prose"><ul>
<li><b>Ratenkredit.</b> Bei einem Minus, das seit Monaten nicht verschwindet, ist ein Ratenkredit fast immer günstiger. Fester Zins, feste Rate, festes Ende. Mit dem <a href="{P}de/rechner/kreditrechner/">Kreditrechner</a> siehst du, was eine Laufzeit kostet. Vorsicht bei Restschuldversicherungen, die beim Umschulden angeboten werden, sie sind laut Verbraucherzentralen teuer und leisten wenig.</li>
<li><b>Rahmenkredit.</b> Manche Banken bieten eine Kreditlinie mit niedrigerem Zins als der Dispo an, die du wie den Dispo flexibel nutzt.</li>
<li><b>Kreditkarte mit Teilzahlung.</b> Meist teurer als der Dispo, und die Teilzahlung ist oft voreingestellt. Was dabei zu beachten ist, steht im Ratgeber <a href="{RG}teilzahlung/">Teilzahlung bei Kreditkarten</a>.</li>
<li><b>Konto mit günstigem Dispo.</b> Wenn du den Dispo nur ein paar Tage im Monat brauchst, zählt der Dispozins. Er steht bei jedem Konto im <a href="{G1}">Girokonto-Vergleich</a>.</li>
<li><b>Schuldnerberatung.</b> Die Schuldnerberatungsstellen der Verbraucherzentralen, Wohlfahrtsverbände und Kommunen beraten kostenlos.</li></ul></div>'''),
       ('Dispo kündigen oder reduzieren',f'''<div class="prose"><p>Du kannst den Dispo jederzeit reduzieren oder kündigen, in vielen Apps mit zwei Klicks, sonst per Nachricht an die Bank. Vorher muss das Konto ausgeglichen sein oder du vereinbarst, wie du den Rest abbaust. Ein kleinerer Rahmen ist eine wirksame Bremse. Wer gar nicht ins Minus will, kann bei einigen Banken den Dispo auf 0 € setzen; Lastschriften, die nicht gedeckt sind, gehen dann zurück und können Gebühren beim Zahlungsempfänger auslösen.</p>
<p>Beim Kontowechsel muss das alte Konto ausgeglichen sein, bevor es schließt. Der Ablauf steht im Ratgeber <a href="../girokonto-wechseln/">Girokonto wechseln</a>.</p></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Dispozinsen und Zinsen bei geduldeter Überziehung: Preis- und Leistungsverzeichnisse der Banken, verlinkt bei jedem Konto im Vergleich. Die Werte werden beim Bauen dieser Seite aus den Kontodaten übernommen.</li>
<li>BGB: {_ext(BGB(504),"§ 504")}, {_ext(BGB("504a"),"§ 504a")}, {_ext(BGB(505),"§ 505")}, {ABGERUFEN}. Neue Regeln ab 20.11.2026: {_ext(BGBL_2026_139,"Gesetz zur Umsetzung der Richtlinie (EU) 2023/2225, BGBl. 2026 I Nr. 139")}.</li>
<li>Kündigung des Dispos: {_ext(BAFIN_DISPO,"BaFin, Darf die Bank den Dispositionskredit reduzieren oder streichen?")}.</li>
<li>Angabe des Dispozinses: Art. 247a § 2 EGBGB; BGH, Urteil vom 29.06.2021, XI ZR 46/20.</li></ul></div>'''),
      ],
      faq=[
       ('Was ist der Unterschied zwischen Dispo und geduldeter Überziehung?','Der Dispo ist ein vertraglich eingeräumter Rahmen (§ 504 BGB). Eine geduldete Überziehung ist ein Minus ohne Dispo oder über den Dispo hinaus (§ 505 BGB). Die Bank muss sie nicht dulden und verlangt dafür meist mehr Zinsen.'),
       ('Wie hoch sind die Dispozinsen?',f'Im Vergleich je nach Konto {_pct(dmin["sollzins"])} bis {_pct(dmax["sollzins"])}, bei geduldeter Überziehung {_pct(gmin["ueberschreitung"])} bis {_pct(gmax["ueberschreitung"])}. Eine gesetzliche Obergrenze gibt es nicht.'),
       ('Muss mich die Bank warnen, wenn ich dauerhaft im Dispo bin?','Ja. Nach sechs Monaten mit im Schnitt mehr als 75 % Auslastung muss sie eine Beratung anbieten (§ 504a BGB), bei geduldeter Überziehung nach drei Monaten über 50 % des Geldeingangs. Ab 20.11.2026 kommen weitere Informationspflichten dazu.'),
       ('Darf die Bank meinen Dispo streichen?','Ja, es gibt keinen Anspruch auf einen Dispo. Ab 20. November 2026 muss sie dich aber 30 Tage vorher informieren und vor einer Zwangsvollstreckung eine Rückzahlung in zwölf Monatsraten anbieten.'),
       ('Kann ich den Dispo selbst kündigen?','Ja, jederzeit und kostenlos. Das Konto muss vorher ausgeglichen sein oder du vereinbarst eine Rückzahlung mit der Bank.'),
       ('Lohnt sich ein Ratenkredit statt Dispo?','Bei einem Minus, das länger als ein paar Monate besteht, meist ja. Der Zins ist niedriger und die Schulden sind nach der Laufzeit weg. Vergleiche den Effektivzins und lehne eine Restschuldversicherung ab, wenn du sie nicht brauchst.'),
      ],
      related=['gemeinschaftskonto','p-konto','konto-selbststaendige','kostenloses-girokonto','basiskonto'])

    # ---------- 2. Gemeinschaftskonto ----------
    gem=sorted([k for k in alle if k.get('gemeinschaftskonto') is True],key=lambda k:(k['kf_jahr'],k['bank'].lower()))
    nogem=sorted({k['bank'] for k in alle if k.get('gemeinschaftskonto') is False and not any(x.get('gemeinschaftskonto') is True for x in alle if x['bank']==k['bank'])})
    gbank=sorted({k['bank'] for k in gem})
    grow=[(L(k),kfT(k),debT(k),wegT(k)) for k in gem]
    art('de','gemeinschaftskonto',
      h1='Gemeinschaftskonto in Deutschland: Oder-Konto, Haftung und die Schenkungsteuer-Falle',
      mt='Gemeinschaftskonto Deutschland: Haftung, Steuer | Finvallo',
      desc=f'Gemeinschaftskonto in Deutschland: Oder- oder Und-Konto, wer haftet, Einlagensicherung doppelt, Schenkungsteuer bei hohen Einzahlungen und {len(gem)} Konten im Vergleich.',
      about='Girokonten in Deutschland',
      lede='Ein gemeinsames Konto spart Überweisungen hin und her. Es hat aber zwei Haken, die viele erst bei der Trennung oder beim Finanzamt bemerken.',
      kurz=(f'Beim Oder-Konto kann jeder Inhaber allein über das ganze Guthaben verfügen, beim Und-Konto nur alle zusammen. Für ein Minus haften alle Inhaber als Gesamtschuldner. '
            f'Im Vergleich bieten {len(gbank)} Banken ein Gemeinschaftskonto an. Die Einlagensicherung schützt 100.000 € pro Person, bei zwei Inhabern also 200.000 €. '
            'Zahlt ein Partner eine große Summe auf das Oder-Konto ein, kann das Finanzamt die Hälfte als Schenkung werten. Für Ehepaare gilt ein Freibetrag von 500.000 € in zehn Jahren, für unverheiratete Paare nur 20.000 €.'),
      secs=[
       ('Oder-Konto oder Und-Konto',_tbl(['','Oder-Konto','Und-Konto'],[
            ('Verfügung','jeder Inhaber allein','nur alle Inhaber gemeinsam'),
            ('Karten','meist eine girocard oder Debitkarte pro Inhaber','meist keine'),
            ('Online-Banking','jeder mit eigenem Zugang','Freigabe durch alle nötig'),
            ('Üblich bei','Paaren, Familien, WGs','Erbengemeinschaften, Vereinen, Geschäftspartnern'),
            ('Risiko','einer räumt das Konto leer oder überzieht es','nichts geht, wenn einer nicht mitwirkt'),
            ('Pfändungsschutz','nicht als P-Konto möglich','nicht als P-Konto möglich')])+
        f'''<div class="prose"><p>Fast alle Gemeinschaftskonten für Privatkunden sind Oder-Konten. Ein Und-Konto bekommst du bei Filialbanken auf Nachfrage, bei Online-Banken selten. Bei ING, DKB, comdirect und norisbank ist das Gemeinschaftskonto eine Variante des normalen Girokontos zu denselben Preisen, bei Commerzbank und Postbank ebenfalls. N26, Revolut und bunq setzen voraus, dass beide Partner ein eigenes Konto bei der Bank haben.</p></div>'''),
       ('Wer haftet',f'''<div class="prose"><p>Alle Inhaber haften der Bank als Gesamtschuldner (§ 421 BGB). Rutscht das Konto ins Minus, kann die Bank den vollen Betrag von jedem Inhaber verlangen, egal wer das Geld ausgegeben hat. Das gilt für den Dispo, für geduldete Überziehungen und für die Kontoführung. Wer sich das Risiko sparen will, verzichtet beim Gemeinschaftskonto auf den Dispo oder hält ihn klein. Wie der Dispo funktioniert, steht im Ratgeber <a href="../dispo/">Dispo</a>.</p>
<p>Eine Kontovollmacht ist etwas anderes als ein Gemeinschaftskonto: Der Bevollmächtigte darf verfügen, ist aber nicht Inhaber, haftet nicht und hat keinen Anteil am Guthaben. Für Paare, bei denen nur einer das Geld verdient, ist das oft die einfachere Lösung, auch steuerlich.</p></div>'''),
       ('Diese Konten gibt es als Gemeinschaftskonto',_tbl(['Konto','Kontoführung','Karten','Eröffnung'],grow)+
        f'''<div class="prose"><p>Das sind {len(gem)} Konten von {_fmtl(gbank)}. {("Nicht als Gemeinschaftskonto gibt es laut Bankangaben die Konten von "+_fmtl(nogem)+". ") if nogem else ""}Bei den übrigen Banken fehlt eine bestätigte Angabe. Die Rangfolge nach Bewertung steht in der Bestenliste <a href="{B}gemeinschaftskonto/">Gemeinschaftskonten</a>. Achte auf die zweite Karte: Bei manchen Banken ist eine Partnerkarte inklusive, bei anderen kostet die zweite girocard 6 bis 10 € im Jahr.</p>
<p>Gratis-Bedingungen wie ein Mindestgeldeingang gelten beim Gemeinschaftskonto meist für das Konto insgesamt, beide Gehälter zählen also zusammen. Das steht bei jedem Konto im Vergleich.</p></div>'''),
       ('Einlagensicherung: 100.000 € pro Einleger',f'''<div class="prose"><p>Die gesetzliche Einlagensicherung schützt 100.000 € je Einleger und Bank (§ 8 EinSiG). Bei einem Gemeinschaftskonto gilt die Grenze für jeden Inhaber getrennt, zwei Inhaber sind also mit bis zu 200.000 € geschützt. Das Guthaben wird dafür zu gleichen Teilen zugerechnet, wenn nichts anderes vereinbart ist. Die BaFin rechnet ein Beispiel vor: Hat der Mann bei derselben Bank schon 100.000 € auf einem Tagesgeldkonto, ist sein Anspruch ausgeschöpft, und vom Gemeinschaftskonto mit 50.000 € bekommt nur die Frau ihre 25.000 €.</p>
<p>Viele Banken im Vergleich sichern über den freiwilligen Einlagensicherungsfonds oder die Institutssicherung der Sparkassen und Genossenschaftsbanken deutlich mehr ab. Für Konten bei Revolut (Litauen) und bunq (Niederlande) gilt die dortige gesetzliche Sicherung, ebenfalls mit 100.000 € pro Person. Was für dein Konto gilt, steht in den Konditionen des Kontos.</p></div>'''),
       ('Die Schenkungsteuer-Falle','''<div class="prose"><p>Zahlt ein Partner eine Erbschaft, eine Abfindung oder den Erlös aus einem Hausverkauf auf das gemeinsame Oder-Konto ein, geht das Finanzamt davon aus, dass die Hälfte dem anderen Partner geschenkt wurde. Der Bundesfinanzhof hat das 2011 bestätigt, dem Finanzamt aber die Beweislast auferlegt: Es muss zeigen, dass der andere Partner tatsächlich über die Hälfte verfügen konnte (Urteil vom 23.11.2011, II R 33/10). Wer nachweisen kann, dass das Geld nur dem Einzahler gehörte und der Partner es nicht für sich genutzt hat, kommt um die Steuer herum.</p>
<p>Die Freibeträge nach § 16 ErbStG machen den Unterschied: Ehepartner und eingetragene Lebenspartner haben 500.000 € in zehn Jahren frei, unverheiratete Paare nur 20.000 €. Für sie wird ein Oder-Konto bei größeren Summen schnell teuer. Drei Wege helfen:</p><ul>
<li>Große Einmalbeträge auf ein Einzelkonto des Einzahlers legen und dem Partner eine Vollmacht geben.</li>
<li>Eine schriftliche Vereinbarung, wem welches Guthaben gehört, bevor das Geld eingeht.</li>
<li>Vom Gemeinschaftskonto nur die laufenden Kosten bezahlen und es nicht als Sparkonto nutzen.</li></ul></div>'''),
       ('Trennung und Pfändung','''<div class="prose"><p><b>Trennung.</b> Jeder Inhaber eines Oder-Kontos kann der Bank gegenüber die Einzelverfügung des anderen widerrufen. Danach geht nur noch gemeinsam. Das sollte der erste Schritt sein, wenn eine Trennung ansteht. Im Zweifel gehört das Guthaben beiden zur Hälfte. Wer nach der Trennung mehr als die Hälfte abhebt, muss den Rest ausgleichen. Kündigen können nur alle Inhaber zusammen, und erst, wenn das Konto nicht im Minus ist. Daueraufträge und Lastschriften ziehen mit der <a href="../girokonto-wechseln/">Kontowechselhilfe</a> auf das neue Einzelkonto um.</p>
<p><b>Pfändung.</b> Ein Gemeinschaftskonto kann kein P-Konto sein. Wird gegen einen Inhaber gepfändet, darf die Bank einen Monat lang nichts an den Gläubiger auszahlen (§ 850l ZPO). In dieser Zeit kann jeder Inhaber verlangen, dass sein Anteil, im Zweifel die Hälfte, auf ein eigenes Konto übertragen wird, das er dann als P-Konto führen lässt. Mehr dazu im Ratgeber <a href="../p-konto/">P-Konto</a>.</p></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Gemeinschaftskonto möglich oder nicht, Karten, Eröffnung: Preis- und Leistungsverzeichnisse der Banken, verlinkt bei jedem Konto im Vergleich. Die Werte werden beim Bauen dieser Seite aus den Kontodaten übernommen.</li>
<li>Einlagensicherung: {_ext(EINSIG_8,"§ 8 EinSiG")}, {_ext(KWG_ANH,"Informationsbogen für den Einleger, Anhang I KWG")}, {_ext(BAFIN_ES,"BaFin, Einlagensicherung und Anlegerentschädigung")}, {ABGERUFEN}.</li>
<li>Schenkungsteuer: BFH, Urteil vom 23.11.2011, II R 33/10; Freibeträge: § 16 ErbStG.</li>
<li>Pfändung: {_ext(ZPO("850l"),"§ 850l ZPO")}; Haftung: {_ext(BGB(421),"§ 421 BGB")}.</li></ul></div>'''),
      ],
      faq=[
       ('Was ist ein Oder-Konto?','Ein Gemeinschaftskonto, bei dem jeder Inhaber allein über das ganze Guthaben verfügen darf. Beim Und-Konto müssen alle Inhaber gemeinsam handeln.'),
       ('Hafte ich für den Dispo meines Partners?','Ja. Alle Inhaber haften als Gesamtschuldner, die Bank kann den vollen Minusbetrag von jedem verlangen.'),
       ('Welche Banken bieten ein Gemeinschaftskonto an?',f'Im Vergleich: {_fmtl(gbank)}. Bei einigen Banken ist es eine Variante des normalen Girokontos zu denselben Preisen.'),
       ('Wie hoch ist die Einlagensicherung beim Gemeinschaftskonto?','100.000 € je Inhaber und Bank, also 200.000 € bei zwei Inhabern. Das Guthaben wird dafür je zur Hälfte zugerechnet.'),
       ('Fällt Schenkungsteuer an, wenn mein Partner Geld auf das gemeinsame Konto einzahlt?','Bei großen Beträgen kann das Finanzamt die Hälfte als Schenkung werten. Ehepartner haben 500.000 € in zehn Jahren frei, unverheiratete Paare 20.000 €. Es muss aber das Finanzamt beweisen, dass der Partner über das Geld verfügen konnte.'),
       ('Kann ein Gemeinschaftskonto ein P-Konto sein?','Nein. Bei einer Pfändung hat jeder Inhaber einen Monat Zeit, seinen Anteil auf ein eigenes Konto übertragen zu lassen und dieses als P-Konto zu führen (§ 850l ZPO).'),
      ],
      related=['dispo','p-konto','kinderkonto-jugendkonto','kostenloses-girokonto','girokonto-wechseln'])

    # ---------- 3. P-Konto ----------
    basis=sorted([k for k in ks if k['art']=='basis'],key=lambda k:(k['kf_jahr'],k['bank'].lower()))
    frei=1590; frei_raw=1587.40
    art('de','p-konto',pair='pfaendungsschutzkonto',
      h1='P-Konto in Deutschland: Pfändungsschutzkonto, Freibetrag 2026 und Umwandlung',
      mt='P-Konto Deutschland: Freibetrag 2026, Umwandlung | Finvallo',
      desc=f'P-Konto in Deutschland: Grundfreibetrag {eur(frei)} € seit 1. Juli 2026, Umwandlung in 4 Geschäftstagen, Bescheinigung für höhere Freibeträge, nur ein P-Konto pro Person.',
      about='Girokonten in Deutschland',
      lede='Wird dein Konto gepfändet, kommst du an kein Geld mehr, auch nicht an das Gehalt für die Miete. Das P-Konto schützt jeden Monat einen festen Betrag, automatisch und ohne Gericht.',
      kurz=(f'Jedes Girokonto kannst du bei deiner Bank in ein Pfändungsschutzkonto umwandeln lassen, die Bank hat dafür vier Geschäftstage Zeit (§ 850k ZPO). Auf dem P-Konto bleibt dir seit 1. Juli 2026 ein Grundfreibetrag von {eur(frei)} € im Monat, ohne Antrag bei Gericht. '
            'Mit einer Bescheinigung erhöht sich der Freibetrag, etwa für Kinder, Unterhalt oder Kindergeld. Nicht verbrauchtes Guthaben kannst du bis zu drei Monate übertragen. '
            'Pro Person ist nur ein P-Konto erlaubt, ein Gemeinschaftskonto kann keines sein.'),
      secs=[
       ('Was das P-Konto schützt',_tbl(['Schutz','Betrag oder Regel','Grundlage'],[
            ('Grundfreibetrag pro Kalendermonat',f'{eur(frei)} € (Pfändungsfreigrenze {eur(frei_raw)} €, aufgerundet auf volle 10 €)','§ 899 ZPO, § 850c ZPO'),
            ('Erhöhung für Unterhaltspflichten','fester Zusatzbetrag je Person, der du Unterhalt zahlst, mit Bescheinigung','§ 902 ZPO'),
            ('Kindergeld und bestimmte Sozialleistungen','in voller Höhe zusätzlich, mit Bescheinigung','§ 902 ZPO'),
            ('Einmalige Sozialleistungen, Nachzahlungen','geschützt nach Prüfung durch die Bank oder das Vollstreckungsgericht','§ 902, § 904, § 905 ZPO'),
            ('Ansparen','nicht verbrauchter Freibetrag wandert in die drei folgenden Monate','§ 899 Abs. 2 ZPO')])+
        f'''<div class="prose"><p>Der Grundfreibetrag folgt der Pfändungsfreigrenze für Arbeitseinkommen, die das Bundesjustizministerium jedes Jahr zum 1. Juli anpasst. Seit 1. Juli 2026 liegt sie bei {eur(frei_raw)} € im Monat, davor waren es 1.555 €. Auf dem P-Konto wird der Betrag auf volle 10 € aufgerundet, deshalb {eur(frei)} €. Der Schutz gilt für jedes Guthaben, egal ob es aus Gehalt, Rente, Bürgergeld oder einem Geschenk stammt.</p>
<p>Was über dem Freibetrag liegt, geht am Ende des Monats an den Gläubiger, es sei denn, du kannst ein höheres Existenzminimum nachweisen. Bei dauerhaft höherem Einkommen oder vielen Unterhaltspflichten setzt das Vollstreckungsgericht auf Antrag einen individuellen Freibetrag fest.</p></div>'''),
       ('So wandelst du dein Konto um',f'''<div class="prose"><ol>
<li><b>Verlangen, nicht beantragen.</b> Du hast einen Anspruch auf die Umwandlung, die Bank darf sie nicht ablehnen und nichts dafür verlangen (§ 850k ZPO). Das geht auch nach der Pfändung, nicht nur davor. Viele Banken bieten ein Formular im Online-Banking an.</li>
<li><b>Vier Geschäftstage.</b> Die Bank muss das Konto spätestens am vierten Geschäftstag nach deinem Verlangen als P-Konto führen. Verlangst du die Umwandlung innerhalb eines Monats nach Zustellung der Pfändung, wirkt der Schutz rückwirkend ab dem Pfändungstag.</li>
<li><b>Versicherung abgeben.</b> Du bestätigst, dass du kein anderes P-Konto führst. Die Bank meldet das P-Konto an die Schufa, damit niemand zwei hat. Die Meldung ist kein negativer Eintrag und wird nur dafür genutzt.</li>
<li><b>Bescheinigung nachreichen.</b> Für Erhöhungen über den Grundfreibetrag hinaus brauchst du eine Bescheinigung. Jobcenter, Familienkasse und andere Sozialleistungsträger müssen sie dir auf Antrag ausstellen. Schuldnerberatungsstellen, Rechtsanwälte, Steuerberater und Arbeitgeber können sie ausstellen, müssen aber nicht.</li></ol>
<p>Das P-Konto ist immer ein Einzelkonto. Ein Gemeinschaftskonto lässt sich nicht umwandeln; bei einer Pfändung hat jeder Inhaber einen Monat Zeit, seinen Anteil auf ein eigenes Konto übertragen zu lassen (§ 850l ZPO). Mehr dazu im Ratgeber <a href="../gemeinschaftskonto/">Gemeinschaftskonto</a>.</p></div>'''),
       ('Was ein P-Konto kostet und was es nicht kann',f'''<div class="prose"><p>Die Umwandlung ist gebührenfrei, und die Bank darf für ein P-Konto nicht mehr verlangen als für das normale Konto. Der Bundesgerichtshof hat Aufpreise für das P-Konto 2012 für unwirksam erklärt. Die normale Kontoführung bleibt aber bestehen. Ein kostenloses Girokonto bleibt also kostenlos, ein Konto für 5 € im Monat kostet weiter 5 €. Welche Konten ohne Kontoführung auskommen, steht im Ratgeber <a href="../kostenloses-girokonto/">kostenloses Girokonto</a>.</p>
<p>Was das P-Konto nicht kann: Es läuft auf Guthabenbasis. Ein Dispo wird mit der Umwandlung meist gekündigt, und einen neuen gibt es nicht. Manche Banken schränken Karten oder Online-Banking ein, das müssen sie aber nicht. Kreditkarten mit Kreditrahmen passen nicht zum P-Konto.</p></div>'''),
       ('Nur ein P-Konto, aber das ist dein Recht',f'''<div class="prose"><p>Jede Person darf nur ein P-Konto haben. Wer zwei führt, riskiert, dass das Vollstreckungsgericht eines davon bestimmt und der Schutz auf dem anderen entfällt. Die Bank darf die Umwandlung nicht verweigern, auch nicht mit dem Hinweis auf Schulden bei ihr selbst. Kündigt dir die Bank das Konto, hast du Anspruch auf ein <a href="../basiskonto/">Basiskonto</a> bei jeder anderen Bank, und du kannst schon beim Antrag verlangen, dass es als P-Konto geführt wird (§ 850k Abs. 1 ZPO). Im Vergleich kosten Basiskonten zwischen {eur(basis[0]["kf_jahr"])} € und {eur(basis[-1]["kf_jahr"])} € im Jahr.</p>
<p>Wenn die Pfändung erledigt ist, kannst du die Rückumwandlung verlangen. Die Bank muss sie spätestens am vierten Geschäftstag nach dem Monatsende umsetzen. Auch die Schufa-Meldung wird dann gelöscht.</p></div>'''),
       ('Checkliste bei Kontopfändung','''<div class="prose"><ul class="checks">
<li>Sofort die Umwandlung in ein P-Konto verlangen, schriftlich oder im Online-Banking, mit Datum.</li>
<li>Innerhalb eines Monats nach Zustellung der Pfändung handeln, dann gilt der Schutz rückwirkend.</li>
<li>Bescheinigung für Unterhalt, Kindergeld oder Sozialleistungen besorgen und einreichen.</li>
<li>Miete, Strom und Versicherungen prüfen: Lastschriften gehen nur durch, wenn der Freibetrag reicht.</li>
<li>Schuldnerberatung aufsuchen. Die Beratung bei Verbraucherzentralen, Wohlfahrtsverbänden und Kommunen ist kostenlos und oft Voraussetzung für die Bescheinigung.</li>
<li>Den Gläubiger kontaktieren: Eine Ratenzahlung kann die Pfändung beenden.</li></ul></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Pfändungsfreigrenze 2026: {_ext(PFGR_2026,"Pfändungsfreigrenzenbekanntmachung 2026 (BGBl. 2026 I Nr. 80)")} und {_ext(BMJ_PF,"Bundesministerium der Justiz, Pfändungsfreigrenzen")}, {ABGERUFEN}.</li>
<li>P-Konto: {_ext(ZPO("850k"),"§ 850k ZPO")}, {_ext(ZPO("850l"),"§ 850l ZPO")}, {_ext(ZPO(899),"§ 899 ZPO")}, {_ext(ZPO(902),"§ 902 ZPO")}, {_ext(ZPO(903),"§ 903 ZPO")}, {ABGERUFEN}.</li>
<li>Umwandlung, Bescheinigung, Gemeinschaftskonto, Kosten: {_ext(VZ_PKONTO,"Verbraucherzentrale, Fragen und Antworten zum P-Konto")}, {ABGERUFEN}.</li>
<li>Preise der Basiskonten: Preis- und Leistungsverzeichnisse der Banken, verlinkt bei jedem Konto im Vergleich.</li></ul></div>'''),
      ],
      faq=[
       ('Wie hoch ist der Freibetrag auf dem P-Konto 2026?',f'Seit 1. Juli 2026 sind {eur(frei)} € pro Kalendermonat geschützt. Mit Bescheinigung erhöht sich der Betrag für Unterhaltspflichten, Kindergeld und bestimmte Sozialleistungen.'),
       ('Wie schnell muss die Bank mein Konto umwandeln?','Spätestens am vierten Geschäftstag nach deinem Verlangen. Die Umwandlung ist kostenlos und darf nicht abgelehnt werden.'),
       ('Kann ich zwei P-Konten haben?','Nein, pro Person ist nur ein P-Konto erlaubt. Die Bank meldet es an die Schufa, damit das geprüft werden kann.'),
       ('Wer stellt die Bescheinigung aus?','Jobcenter, Familienkasse und andere Sozialleistungsträger müssen sie ausstellen. Schuldnerberatungen, Anwälte, Steuerberater und Arbeitgeber können es.'),
       ('Kostet ein P-Konto mehr als ein normales Konto?','Nein. Ein Aufpreis für das P-Konto ist unzulässig, die normale Kontoführung läuft aber weiter.'),
       ('Kann ein Gemeinschaftskonto ein P-Konto werden?','Nein. Jeder Inhaber kann bei einer Pfändung innerhalb eines Monats verlangen, dass sein Anteil auf ein eigenes Konto übertragen wird, das dann als P-Konto läuft.'),
      ],
      related=['dispo','gemeinschaftskonto','basiskonto','kostenloses-girokonto','girokonto-wechseln'])

    # ---------- 4. Kinderkonto und Jugendkonto ----------
    minder=sorted([k for k in ks if k['art'] in ('kinder','jugend')],key=lambda k:((k.get('alter') or {}).get('min') or 0,k['bank'].lower()))
    mrow=[(L(k),altT(k),debT(k),kfT(k)) for k in minder]
    mfree=[k for k in minder if k['kf_jahr']==0]
    geburt=[k for k in minder if ((k.get('alter') or {}).get('min') or 0)==0 and (k.get('alter') or {}).get('min') is not None]
    art('de','kinderkonto-jugendkonto',
      h1='Kinderkonto und Jugendkonto in Deutschland: Alter, Karten und was mit 18 passiert',
      mt='Kinderkonto und Jugendkonto Deutschland | Finvallo',
      desc=f'Kinderkonto und Jugendkonto in Deutschland: ab welchem Alter, wer eröffnet, girocard oder Debitkarte, Limits, Umstellung mit 18. {len(minder)} Konten für Minderjährige im Vergleich.',
      about='Girokonten in Deutschland',
      lede='Taschengeld aufs Konto statt ins Sparschwein: Das erste Girokonto lehrt den Umgang mit Geld. Die Regeln dafür stehen im BGB, die Konditionen setzt die Bank.',
      kurz=(f'Ein Konto für Kinder eröffnen die Eltern, bei beiden Sorgeberechtigten gemeinsam. Die meisten Banken im Vergleich bieten es ab 7 Jahren an, einige ab der Geburt. Ab 7 ist das Kind beschränkt geschäftsfähig und darf mit seinem Taschengeld selbst bezahlen (§ 110 BGB). '
            f'Konten für Minderjährige laufen auf Guthabenbasis, einen Dispo gibt es nicht. {len(mfree)} von {len(minder)} Konten im Vergleich sind kostenlos. '
            'Mit 18 endet die Vertretung durch die Eltern, und die Bank stellt auf ein Konto für junge Erwachsene oder ein normales Girokonto um.'),
      secs=[
       ('Ab welchem Alter und wer eröffnet',f'''<div class="prose"><p>Das BGB regelt, was Kinder selbst dürfen:</p><ul>
<li><b>Unter 7 Jahren:</b> geschäftsunfähig (§ 104 BGB). Ein Konto eröffnen die Eltern auf den Namen des Kindes, meist als Sparkonto oder Kinderkonto ohne Karte. Im Verglei­ch gibt es das {("bei "+_fmtl([k["name"]+" ("+k["bank"]+")" for k in geburt])) if geburt else "bei wenigen Banken"}.</li>
<li><b>7 bis 17 Jahre:</b> beschränkt geschäftsfähig (§ 106 BGB). Das Kind darf mit Geld, das ihm zur freien Verfügung überlassen wurde, selbst bezahlen, das ist der Taschengeldparagraf (§ 110 BGB). Für die Kontoeröffnung braucht es die Eltern. Bei gemeinsamem Sorgerecht unterschreiben beide (§ 1629 BGB), bei alleinigem Sorgerecht reicht ein Elternteil mit Nachweis.</li></ul>
<p>Das Kind ist Kontoinhaber, die Eltern sind gesetzliche Vertreter und verwalten das Konto. Sie können das Limit der Karte festlegen, Umsätze sehen und das Konto kündigen. Einen Kredit, auch einen kleinen Dispo, dürfen Minderjährige nicht aufnehmen, dafür bräuchte es das Familiengericht. Deshalb laufen alle Konten für Minderjährige auf Guthabenbasis.</p>
<p>Zur Eröffnung brauchen die Banken die Ausweise der Eltern, die Geburtsurkunde oder den Kinderausweis und die Steuer-ID des Kindes. Bei vielen Online-Banken muss ein Elternteil schon Kunde sein, etwa bei ING und DKB.</p></div>'''),
       ('Konten für Minderjährige im Vergleich',_tbl(['Konto','Alter','Karte','Kontoführung'],mrow)+
        f'''<div class="prose"><p>{len(mfree)} der {len(minder)} Konten sind kostenlos. Die Namen sind nicht geschützt: Was eine Bank Kinderkonto nennt, heißt bei der nächsten Jugendkonto oder Starter-Konto, oft für denselben Altersbereich von 7 bis 17. Die Rangfolgen stehen in den Bestenlisten <a href="{B}kinder/">Kinderkonten</a> und <a href="{B}jugend/">Jugendkonten</a>. Nicht im Vergleich sind Kinderkarten, die am Konto der Eltern hängen, etwa bei N26, Revolut oder bunq: Dort hat das Kind kein eigenes Konto mit eigener IBAN.</p></div>'''),
       ('Welche Karte das Kind bekommt','''<div class="prose"><p>Drei Kartentypen sind üblich:</p><ul>
<li><b>girocard.</b> Die klassische Bankkarte für Geschäfte und Geldautomaten in Deutschland. Online geht damit wenig. Bei ING gibt es sie für Minderjährige nicht, bei comdirect auf Wunsch kostenlos, bei BBBank und GLS ist sie dabei.</li>
<li><b>Visa oder Mastercard Debit.</b> Zahlt vom Guthaben, funktioniert im Laden, online, im Ausland und in Apple Pay oder Google Pay. ING, DKB, comdirect und TARGOBANK geben sie Minderjährigen kostenlos. Bei norisbank gibt es die Mastercard ab 12 Jahren für 12 € im Jahr, bei BBBank die Visa BasicCard ab 12 für 9,90 € im Jahr.</li>
<li><b>Prepaid-Kreditkarte.</b> Wird vorher aufgeladen, etwa für Reisen. Nur bei wenigen Banken, oft gegen Gebühr.</li></ul>
<p>Limits legen die Eltern in der App fest, etwa pro Tag oder pro Woche. Viele Banken sperren Glücksspiel- und Erwachsenenangebote für Minderjährige automatisch. Abheben ist bei den meisten Konten an eigenen Automaten kostenlos, an fremden kostet es teils 3 bis 4 €, das steht in den Konditionen des Kontos.</p></div>'''),
       ('Taschengeldkonto oder Jugendkonto',_tbl(['','Taschengeldkonto (Kinderkonto)','Jugendkonto'],[
            ('Alter','ab Geburt oder ab 7','ab 7 oder 12 bis 17'),
            ('Karte','oft keine oder girocard mit kleinem Limit','Debitkarte mit Online-Zahlung und Wallet'),
            ('Zweck','Taschengeld, Geldgeschenke, Sparen','Ausbildung, Nebenjob, Handyvertrag, Abos'),
            ('Online-Banking','Eltern','Kind mit eigenem Zugang, Eltern mit Einsicht'),
            ('Dispo','nein','nein'),
            ('Danach','Jugendkonto','Konto für junge Erwachsene oder normales Girokonto')])+
        '<div class="prose"><p>Ab etwa 10 bis 12 Jahren empfehlen Verbraucherzentralen ein eigenes Girokonto mit Karte, abhängig von der Reife des Kindes. Vorher reicht meist ein Sparkonto, das die Eltern verwalten. Für Azubis und Studierende ab 18 gibt es eigene Konten, siehe die Bestenliste <a href="../../girokonto/bestenlisten/studenten/">Konten für Studierende und Azubis</a>.</p></div>'),
       ('Was mit 18 passiert','''<div class="prose"><p>Mit dem 18. Geburtstag wird das Kind voll geschäftsfähig, die Eltern verlieren den Zugriff, und das Konto gehört allein dem jungen Erwachsenen. Die Bank stellt das Modell um, je nach Bank sofort oder später:</p><ul>
<li>Commerzbank führt das StartKonto weiter, wenn Ausbildung oder Studium nachgewiesen werden, sonst kostet es später 9,90 € im Monat.</li>
<li>TARGOBANK stellt das Starter-Konto mit 18 automatisch auf das Plus-Konto um.</li>
<li>BBBank führt das Junge Girokonto bis zum 30. Geburtstag kostenfrei, danach wird es zum BBBank-Girokonto.</li>
<li>GLS Bank führt das Konto U18 als GLS Konto 18-27 weiter, mit 12 € Kontoführung im Jahr.</li>
<li>norisbank stellt mit 18 auf das Girokonto um, DKB, ING und comdirect auf ihr normales Girokonto, das jeweils mit Geldeingang oder bis zu einem bestimmten Alter kostenlos bleibt.</li></ul>
<p>Ab 18 kann der Kontoinhaber auch einen Dispo beantragen. Ob das sinnvoll ist, steht im Ratgeber <a href="../dispo/">Dispo</a>. Lohnt sich das umgestellte Konto nicht, ist der Wechsel mit der <a href="../girokonto-wechseln/">Kontowechselhilfe</a> schnell erledigt, die besten kostenlosen Konten stehen im Ratgeber <a href="../kostenloses-girokonto/">kostenloses Girokonto</a>.</p></div>'''),
       ('Worauf Eltern achten sollten','''<div class="prose"><ul class="checks">
<li>Müssen beide Eltern unterschreiben, und geht die Eröffnung online oder nur per Post und Postident?</li>
<li>Muss ein Elternteil Kunde der Bank sein?</li>
<li>Welche Karte gibt es ab welchem Alter, und was kostet eine zweite oder eine Ersatzkarte?</li>
<li>Lassen sich Limits und Online-Zahlungen in der App einstellen und sperren?</li>
<li>Gibt es Zinsen auf das Guthaben? Bei einigen Kinderkonten ja, das steht in den Konditionen des Kontos.</li>
<li>Was passiert mit 18, und was kostet das Konto dann?</li></ul></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Alter, Karten, Kontoführung, Umstellung: Preis- und Leistungsverzeichnisse und Produktseiten der Banken, verlinkt bei jedem Konto im Vergleich. Die Werte werden beim Bauen dieser Seite aus den Kontodaten übernommen.</li>
<li>Geschäftsfähigkeit und Vertretung: {_ext(BGB(104),"§ 104 BGB")}, {_ext(BGB(106),"§ 106 BGB")}, {_ext(BGB(110),"§ 110 BGB")}, {_ext(BGB(1629),"§ 1629 BGB")}, {ABGERUFEN}.</li></ul></div>'''),
      ],
      faq=[
       ('Ab welchem Alter kann mein Kind ein Girokonto haben?','Die meisten Banken im Vergleich eröffnen Konten für Minderjährige ab 7 Jahren, einige schon ab der Geburt. Eröffnen müssen die Eltern, bei gemeinsamem Sorgerecht beide.'),
       ('Kann ein Jugendlicher allein ein Konto eröffnen?','Nein. Bis 18 braucht es die Eltern als gesetzliche Vertreter. Mit seinem Taschengeld darf ein Kind ab 7 aber selbst bezahlen (§ 110 BGB).'),
       ('Kann ein Jugendkonto überzogen werden?','Nein. Konten für Minderjährige laufen auf Guthabenbasis. Einen Kredit dürfen Minderjährige nicht aufnehmen.'),
       ('Bekommt mein Kind eine Kreditkarte?','Keine echte Kreditkarte. Üblich sind girocard und Visa oder Mastercard Debit, die vom Guthaben abbuchen. Prepaid-Karten gibt es bei wenigen Banken.'),
       ('Was kostet ein Kinderkonto?',f'{len(mfree)} von {len(minder)} Konten für Minderjährige im Vergleich sind kostenlos. Bei einigen kostet eine zusätzliche Mastercard oder Visa ab 12 Jahren extra.'),
       ('Was passiert mit dem Konto mit 18?','Die Eltern verlieren den Zugriff, das Konto gehört dem jungen Erwachsenen allein. Die Bank stellt auf ein Konto für junge Erwachsene oder ein normales Girokonto um, teils sofort, teils erst mit 27 oder 30.'),
      ],
      related=['gemeinschaftskonto','konto-selbststaendige','kostenloses-girokonto','girokonto-wechseln','basiskonto'])

    # ---------- 5. Konto für Selbstständige ----------
    kand=sorted([k for k in alle if not (k.get('gratis') and k['gratis'].get('eingang_min') is not None and 'gehalt' in ((k['gratis'].get('eingang_art') or '')+(k['gratis'].get('text') or '')).lower() and k['kf_jahr']>0)],key=lambda k:(k['kf_jahr'],k['bank'].lower()))
    srow=[(L(k),kfT(k),E((k.get('gratis') or {}).get('text') or ('kostenlos ohne Bedingung' if k['kf_jahr']==0 else 'keine')),wegT(k)) for k in kand[:10]]
    gesch=sorted({x['name'].split(' ')[0] for x in d.get('nicht_aufgenommen',[]) if re.search(r'gesch[äa]ftsk|business',x.get('name','')+x.get('grund',''),re.I)})
    art('de','konto-selbststaendige',
      h1='Konto für Selbstständige in Deutschland: Reicht das Privatkonto?',
      mt='Konto für Selbstständige in Deutschland | Finvallo',
      desc='Konto für Selbstständige in Deutschland: Wann ein Geschäftskonto Pflicht ist, was die AGB der Banken erlauben, Buchhaltung, Umsatzsteuer und welche Konten im Vergleich passen.',
      about='Girokonten in Deutschland',
      lede='Freiberufler und Einzelunternehmer dürfen ihr Geschäft über ein normales Girokonto abwickeln. Ob die Bank mitspielt und ob das Finanzamt es dir leicht macht, ist eine andere Frage.',
      kurz=('Eine gesetzliche Pflicht zum Geschäftskonto gibt es für Freiberufler, Einzelunternehmer und GbR nicht. GmbH und UG brauchen ein Konto auf den Namen der Gesellschaft, schon für das Stammkapital. '
            'Viele Banken schließen die gewerbliche Nutzung eines Privatkontos in den AGB aus und bieten eigene Geschäftskonten an. Für die Buchhaltung ist ein getrenntes Konto fast Pflicht: Belege musst du acht Jahre aufbewahren, Bücher zehn. '
            'Bis 25.000 € Umsatz im Vorjahr und 100.000 € im laufenden Jahr gilt die Kleinunternehmerregelung ohne Umsatzsteuer.'),
      secs=[
       ('Wann ein Geschäftskonto Pflicht ist',f'''<div class="prose"><p>Das Gesetz schreibt kein Geschäftskonto vor. Freiberufler, Einzelkaufleute, Kleingewerbetreibende und Personengesellschaften wie die GbR dürfen ihre Umsätze über ein Privatkonto laufen lassen. Anders bei Kapitalgesellschaften: GmbH, UG und AG brauchen ein Konto auf den Namen der Gesellschaft, weil das Stammkapital dort eingezahlt wird und der Notar die Einzahlung sehen will. Das Konto gehört dann der Gesellschaft, nicht dir.</p>
<p>In der Praxis entscheidet aber nicht das Gesetz, sondern deine Bank. Ihre AGB legen fest, wofür das Konto gedacht ist. Steht dort „nur für private Zwecke“, verstößt du mit regelmäßigen Kundenzahlungen dagegen. Die Folgen reichen von einer Umstellung auf ein Geschäftskonto mit Preis pro Buchung bis zur Kündigung. Dazu kommt das Finanzamt: Bei einer Betriebsprüfung musst du die Kontoauszüge vollständig vorlegen, inklusive aller privaten Buchungen. Ungeklärte Eingänge kann der Prüfer als Betriebseinnahmen werten.</p></div>'''),
       ('Was die Banken im Vergleich erlauben',f'''<div class="prose"><p>Der Girokonto-Vergleich bewertet Privatkonten. Ob eine Bank gewerbliche Umsätze darauf duldet, steht in den AGB, nicht im Preisverzeichnis. Ein paar Anhaltspunkte aus den Kontodaten:</p><ul>
<li>{_fmtl(gesch) if gesch else "Mehrere Banken"} führen eigene Geschäftskonten, die nur für Geschäftskunden gedacht sind und deshalb nicht im Vergleich stehen. Bei diesen Banken ist das Privatkonto für Selbstständige meist tabu.</li>
<li>N26 und bunq haben eigene Business-Tarife, die wie die Privatkonten funktionieren, aber auf die Person als Unternehmer laufen. Für Einzelunternehmer ohne Handelsregister sind sie oft die einfachste Lösung mit App, Unterkonten und Export der Umsätze.</li>
<li>Filialbanken wie Commerzbank, Deutsche Bank, Postbank, HypoVereinsbank und die Genossenschaftsbanken bieten Geschäftskonten mit Preis pro Buchung, meist 0,10 € bis 0,50 € je Posten plus Grundpreis.</li>
<li>Gratis-Bedingungen mit Geldeingang zählen bei vielen Banken jeden Eingang, auch Kundenzahlungen. Manche verlangen aber ausdrücklich Gehalt oder Rente. Das steht bei jedem Konto im Vergleich.</li></ul>
<p>Frag vor der Eröffnung schriftlich nach, ob du das Konto für dein Unternehmen nutzen darfst, und bewahre die Antwort auf.</p></div>'''),
       ('Welche Privatkonten für ein kleines Unternehmen in Frage kommen',_tbl(['Konto','Kontoführung','Gratis-Bedingung','Eröffnung'],srow)+
        f'''<div class="prose"><p>Die Tabelle zeigt die zehn günstigsten Konten für alle ohne Gehaltsbedingung, sortiert nach regulärer Kontoführung. Für ein Nebengewerbe mit wenigen Buchungen reicht oft ein kostenloses Zweitkonto, wenn die Bank die Nutzung erlaubt. Wer viele Buchungen hat, achtet auf Pauschalpreise statt Einzelposten und auf Bargeldeinzahlung, die bei Online-Banken oft fehlt oder extra kostet. Alle Konten mit Jahreskosten für dein Profil stehen im <a href="{G1}">Girokonto-Vergleich</a>.</p>
<p>Für Ausgaben unterwegs, Software-Abos und Reisen ist eine Firmenkarte praktisch, die nicht an dein Privatkonto hängt. Viele Geschäftskonten haben eine Debitkarte schon dabei, das reicht für den Anfang oft.</p></div>'''),
       ('Buchhaltung: Trennung und Aufbewahrung',f'''<div class="prose"><p>Freiberufler und kleine Gewerbetreibende ermitteln den Gewinn mit der Einnahmenüberschussrechnung (§ 4 Abs. 3 EStG). Dabei zählt der Zahlungszeitpunkt, also der Kontoauszug. Ein eigenes Konto macht daraus eine einfache Liste: Jeder Eingang ist eine Einnahme, jeder Abgang eine Ausgabe oder eine Privatentnahme. Die Grundsätze ordnungsmäßiger Buchführung (GoBD) verlangen, dass Belege vollständig, unveränderbar und nachvollziehbar sind, auch digital.</p>
<p>Seit 2025 gilt für Buchungsbelege wie Rechnungen und Kontoauszüge eine <b>Aufbewahrungsfrist von acht Jahren</b> (§ 147 AO, verkürzt durch das Vierte Bürokratieentlastungsgesetz), für Bücher, Inventare und Jahresabschlüsse weiter zehn Jahre. Die Frist läuft ab Ende des Kalenderjahres, in dem der Beleg entstanden ist. Elektronische Kontoauszüge reichen, wenn sie unverändert gespeichert sind. Lade sie regelmäßig herunter, Banken stellen alte Auszüge im Online-Banking nicht unbegrenzt bereit.</p>
<p>Privatentnahmen überweist du am besten als festen Betrag im Monat auf das Privatkonto. Rücklagen für Einkommensteuer, Umsatzsteuer und Krankenversicherung gehören auf ein Unterkonto oder Tagesgeldkonto, damit sie nicht im Alltag verschwinden.</p></div>'''),
       ('Umsatzsteuer und Kleinunternehmer',f'''<div class="prose"><p>Seit 2025 gilt die Kleinunternehmerregelung (§ 19 UStG), wenn dein Umsatz im Vorjahr höchstens 25.000 € betrug und im laufenden Jahr 100.000 € nicht übersteigt. Dann weist du keine Umsatzsteuer aus und kannst keine Vorsteuer abziehen. Überschreitest du die 100.000 € im laufenden Jahr, bist du ab diesem Umsatz steuerpflichtig, nicht erst im nächsten Jahr. Alle gewerblichen und freiberuflichen Tätigkeiten einer Person werden zusammengezählt.</p>
<p>Wer Umsatzsteuer ausweist, gibt die Umsatzsteuer-Voranmeldung monatlich oder vierteljährlich über ELSTER ab und zahlt die Differenz aus eingenommener Umsatzsteuer und Vorsteuer. Das Geld auf dem Konto gehört also zum Teil dem Finanzamt. Ein eigenes Unterkonto dafür verhindert böse Überraschungen. Zum Umrechnen zwischen netto und brutto hilft der <a href="{P}de/rechner/mehrwertsteuer/">Mehrwertsteuerrechner</a>.</p></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Kontoführung, Gratis-Bedingungen und Eröffnung: Preis- und Leistungsverzeichnisse der Banken, verlinkt bei jedem Konto im Vergleich. Die Werte werden beim Bauen dieser Seite aus den Kontodaten übernommen.</li>
<li>Kleinunternehmerregelung: {_ext(USTG_19,"§ 19 UStG")}, {ABGERUFEN}.</li>
<li>Aufbewahrungsfristen: {_ext(AO_147,"§ 147 AO")}, {ABGERUFEN}.</li></ul></div>'''),
      ],
      faq=[
       ('Muss ich als Freiberufler ein Geschäftskonto haben?','Nein. Freiberufler, Einzelunternehmer und GbR dürfen ein Privatkonto nutzen, wenn die Bank das erlaubt. GmbH, UG und AG brauchen ein Konto auf den Namen der Gesellschaft.'),
       ('Darf ich mein Girokonto gewerblich nutzen?','Nur wenn die AGB der Bank es nicht ausschließen. Viele Banken erlauben das Privatkonto nur für private Zwecke und bieten eigene Geschäftskonten an. Frag schriftlich nach.'),
       ('Welches Konto aus dem Vergleich passt für Selbstständige?','Kostenlose Konten ohne Gehaltsbedingung oder ein günstiges Zweitkonto mit Pauschalpreis, sofern die Bank die Nutzung erlaubt. Für viele Buchungen und Bareinzahlungen eher ein Geschäftskonto.'),
       ('Wie lange muss ich Kontoauszüge aufbewahren?','Als Buchungsbelege acht Jahre ab Ende des Kalenderjahres, Bücher und Jahresabschlüsse zehn Jahre (§ 147 AO). Elektronisch reicht, wenn unverändert gespeichert.'),
       ('Ab wann muss ich Umsatzsteuer ausweisen?','Wenn dein Umsatz im Vorjahr über 25.000 € lag oder im laufenden Jahr 100.000 € übersteigt. Darunter gilt die Kleinunternehmerregelung ohne Umsatzsteuer und ohne Vorsteuerabzug.'),
      ],
      related=['dispo','gemeinschaftskonto','kostenloses-girokonto','girokonto-wechseln','basiskonto'])
