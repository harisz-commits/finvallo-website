# Ratgeber (nur AT) zu Girokonten: Kontoüberziehung, Gemeinschaftskonto, Pfändungsschutz, Kinder- und Jugendkonto, Konto für Selbstständige.
# Zahlen zu Konten kommen live aus daten/at/girokonten.json (json.load, Pfad relativ zu dieser Datei).
# Rechtliches: VKrG 2026 (BGBl. I Nr. 36/2026, gilt ab 20.11.2026), § 292i EO, § 291a EO, § 170 ABGB, § 891 ABGB, § 121a BAO, § 132 BAO,
# ESAEG; laut RIS/Parlament, Arbeiterkammer Wien (FAQ Girokonten 2023), oesterreich.gv.at, BMF, USP und WKO, abgerufen am 28.10.2026.
# hreflang-Paare: kontoueberziehung ↔ dispo, pfaendungsschutzkonto ↔ p-konto, sonst gleiche Slugs.
# Aufruf aus ratgeber.build('at'): register(art,P,eur)
import html,json,os,re
E=lambda s: html.escape(str(s)) if s is not None else ''
DATA=os.path.join(os.path.dirname(os.path.abspath(__file__)),'daten','at','girokonten.json')
AK_FAQ='https://wien.arbeiterkammer.at/beratung/konsumentenschutz/geld/konto/FAQ_Girokonten_2023.pdf'
AK_JUGEND='https://ooe.arbeiterkammer.at/beratung/konsumentenschutz/geld/konto/Jugend--Lehrlingskonten-im-Vergleich.html'
AK_TIPPS='https://www.arbeiterkammer.at/beratung/konsument/Geld/Kredite/Tipps_fuer_Kreditnehmer_bei_Zahlungsproblemen_2021.pdf'
VKRG_2026='https://ris.bka.gv.at/Dokumente/BgblAuth/BGBLA_2026_I_36/BGBLA_2026_I_36.pdf'
EO_292I='https://www.jusline.at/gesetz/eo/paragraf/292i'
GV_EXMIN='https://www.oesterreich.gv.at/de/lexicon/E/Seite.991092'
GV_PENSION='https://www.oesterreich.gv.at/de/themen/arbeit_beruf_und_pension/pension/1/Seite.270300'
GV_GESCH='https://www.oesterreich.gv.at/de/themen/gesetze_und_recht/gerichtsorganisation_der_justiz/zivilrecht/8/Seite.1740386'
ABGB_170='https://www.ris.bka.gv.at/Dokumente/Bundesnormen/NOR40146782/NOR40146782.pdf'
SCHULDEN='https://www.schuldenberatung.at/'
BAWAG_ES='https://www.bawag.at/resource/blob/20382/0b242f44d97223b74e0fbe9675a27bb5/info-einlagensicherung-anlegerentschaedigung-data.pdf'
BMF_SCHENK='https://www.bmf.gv.at/themen/steuern/steuern-von-a-bis-z/schenkungsmeldung.html'
WKO_KU='https://www.wko.at/steuern/pauschalierung-kleinunternehmer'
WKO_KU2='https://www.wko.at/sbg/news/was-aendert-sich-2025-bei-der-kleinunternehmerregelung-'
WKO_GEWINN='https://www.wko.at/steuern/gewinnermittlung'
USP_AUFBEW='https://www.usp.gv.at/steuern-finanzen/steuerliche-gewinnermittlung/weitere-informationen-zur-steuerlichen-gewinnermittlung/betriebliches-rechnungswesen/aufbewahrungspflicht.html'
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
    def L(k,label=None): return f'<a class="lnk" href="{P}at/girokonto/{k["slug"]}/">{E(label or k["name"])}</a> <small class="mut">({E(k["bank"])})</small>'
    G1=f'{P}at/girokonto/'; B=f'{G1}bestenlisten/'; RG=f'{P}at/ratgeber/'
    alle=[k for k in ks if k['art'] in ('standard','premium')]
    kfT=lambda k:'kostenlos' if k['kf_jahr']==0 else f'{eur(k["kf_jahr"])} € im Jahr'
    altT=lambda k:E((k.get('alter') or {}).get('text') or 'keine Angabe')
    debT=lambda k:E((k.get('debitkarte') or {}).get('text') or 'keine Angabe')

    # ---------- 1. Kontoüberziehung ----------
    rahmen=sorted([k for k in alle if k.get('sollzins') is not None],key=lambda k:(k['sollzins'],k['kf_jahr']))
    ueber=sorted([k for k in alle if k.get('ueberschreitung') is not None],key=lambda k:(k['ueberschreitung'],k['kf_jahr']))
    ohne=[k for k in alle if k.get('sollzins') is None and k.get('ueberschreitung') is None]
    rmin,rmax=rahmen[0],rahmen[-1]; umin,umax=ueber[0],ueber[-1]
    zrow=[(L(k),_pct(k['sollzins']),_pct(k['ueberschreitung']) if k.get('ueberschreitung') is not None else 'keine Angabe',kfT(k)) for k in rahmen[:10]]
    art('at','kontoueberziehung',pair='dispo',
      h1='Kontoüberziehung in Österreich: Überziehungsrahmen, Zinsen und deine Rechte',
      mt='Kontoüberziehung Österreich: Zinsen und Rechte | Finvallo',
      desc=f'Kontoüberziehung in Österreich: Rahmen oder Überschreitung, Zinsen von {_pct(rmin["sollzins"])} bis {_pct(umax["ueberschreitung"])} im Vergleich, was die Bank darf und was ab 20.11.2026 neu ist.',
      about='Girokonten in Österreich',
      lede='Ins Minus zu gehen ist bequem, aber teuer. Wer die Regeln kennt, zahlt weniger Zinsen und erlebt keine Überraschung, wenn die Bank den Rahmen kürzt.',
      kurz=(f'Beim Überziehungsrahmen vereinbarst du mit der Bank, wie weit du ins Minus darfst. Alles darüber hinaus ist eine Überschreitung, die die Bank nur duldet und teurer verrechnet. '
            f'Im Vergleich kostet der Rahmen je nach Konto {_pct(rmin["sollzins"])} bis {_pct(rmax["sollzins"])} im Jahr, eine Überschreitung {_pct(umin["ueberschreitung"])} bis {_pct(umax["ueberschreitung"])}. '
            'Ab 20. November 2026 gilt das neue Verbraucherkreditgesetz 2026: Die Bank muss dich 30 Tage vor einer Kürzung des Rahmens informieren und dir die Rückzahlung in zwölf Monatsraten anbieten.'),
      secs=[
       ('Überziehungsrahmen oder Überschreitung: der Unterschied',f'''<div class="prose"><p>Das Gesetz kennt zwei Arten, ein Konto zu überziehen:</p><ul>
<li><b>Überziehungsrahmen</b> (im Gesetz „Überziehungsmöglichkeit“): ein ausdrücklicher Kreditvertrag. Die Bank verpflichtet sich, dir bis zu einem vereinbarten Betrag Geld zur Verfügung zu stellen, der über dein Guthaben hinausgeht. Dafür prüft sie deine Bonität, meist beim KSV1870. Den Rahmen bekommst du nur auf Antrag und nur mit regelmäßigem Einkommen.</li>
<li><b>Überschreitung</b>: Du gehst ins Minus, ohne dass ein Rahmen vereinbart ist, oder du überziehst den Rahmen. Die Bank duldet das stillschweigend, sie muss es aber nicht. Sie kann Lastschriften und Überweisungen auch ablehnen. Einen Anspruch darauf hast du laut Arbeiterkammer nicht.</li></ul>
<p>Beide Formen sind ein Kredit. Die Bank prüft deshalb laufend, ob du ihn zurückzahlen kannst. Sinkt dein Einkommen, etwa durch Arbeitslosigkeit oder Karenz, kann sie den Rahmen verkleinern oder streichen.</p></div>'''),
       ('Was das Überziehen kostet',_tbl(['Konto','Zinsen im Rahmen','Zinsen bei Überschreitung','Kontoführung'],zrow)+
        f'''<div class="prose"><p>Die Tabelle zeigt die zehn Konten für alle mit den niedrigsten Zinsen im Rahmen. Über alle {len(alle)} Konten für alle im Vergleich reicht die Spanne im Rahmen von {_pct(rmin["sollzins"])} ({L(rmin)}) bis {_pct(rmax["sollzins"])} ({L(rmax)}). Für eine Überschreitung verlangen die Banken {_pct(umin["ueberschreitung"])} ({L(umin)}) bis {_pct(umax["ueberschreitung"])} ({L(umax)}). Bei {len(ohne)} Konten, vor allem von Online-Banken aus dem Ausland, gibt es keinen Rahmen oder keine Angabe dazu.</p>
<p>Zum Vergleich: Die Arbeiterkammer Wien hat 2023 bei 81 Kontoprodukten im Rahmen Zinsen von 5,9 % bis 13,75 % gezählt, im Mittel 10,625 %. Für eine Überschreitung kamen 4 bis 5 Prozentpunkte dazu. Eine gesetzliche Obergrenze für Überziehungszinsen gibt es in Österreich nicht. Die Zinsen sind aber laut Arbeiterkammer verhandelbar, vor allem mit guter Bonität und einem Angebot einer anderen Bank in der Hand.</p>
<p>Ein Rechenbeispiel: Wer das ganze Jahr mit 2.000 € im Minus ist, zahlt bei 10 % Zinsen 200 €. Bei 17 % sind es 340 €. Das ist mehr als die meisten Konten im Jahr an Kontoführung kosten.</p></div>'''),
       ('Was die Bank darf und was nicht',f'''<div class="prose"><p>Die Bank darf den Rahmen kürzen oder kündigen, wenn sich deine Bonität verschlechtert. Sie darf eine Überschreitung jederzeit beenden und den offenen Betrag zurückverlangen. Bisher passierte das manchmal von heute auf morgen. Das ändert das <b>Verbraucherkreditgesetz 2026</b> (VKrG 2026), das am 20. November 2026 in Kraft tritt und auch für bestehende, unbefristete Konten gilt:</p><ul class="checks">
<li>Die Bank muss dich <b>mindestens 30 Tage</b>, bevor eine Kürzung oder Streichung des Rahmens wirksam wird, auf dem vereinbarten Weg informieren (§ 35 VKrG 2026). Für Überschreitungen gilt dasselbe (§ 38).</li>
<li>Vor einer Zwangsvollstreckung muss sie dir ohne zusätzliche Kosten anbieten, den gekürzten Betrag in <b>zwölf gleichen Monatsraten</b> zum vereinbarten Sollzinssatz zurückzuzahlen. Früher zurückzahlen darfst du immer.</li>
<li>Bei einem Rahmen bekommst du <b>mindestens einmal im Monat</b> einen Kontoauszug mit den in Anspruch genommenen Beträgen, dem Saldo und dem Sollzinssatz (§ 33).</li>
<li>Eine Erhöhung des Sollzinssatzes wird erst wirksam, wenn dich die Bank darüber informiert hat (§ 34).</li></ul>
<p>Was die Bank nicht darf: dir ohne deine Zustimmung einen Rahmen aufdrängen, Zinsen ohne klare Regel ändern oder dich ohne Vorwarnung in die Exekution schicken. Ein Basiskonto hat keinen Rahmen, dort ist eine Überziehung grundsätzlich nicht möglich. Mehr dazu im Ratgeber <a href="{RG}basiskonto/">Basiskonto</a>.</p></div>'''),
       ('Wann dich die Bank warnen muss','''<div class="prose"><p>Dauert eine erhebliche Überschreitung länger als einen Monat, muss dich die Bank ab 20. November 2026 unverzüglich auf Papier oder einem anderen dauerhaften Datenträger informieren: dass eine Überschreitung vorliegt, über den Betrag, den Sollzinssatz, allfällige Verzugszinsen und Entgelte sowie den Rückzahlungstermin (§ 37 Abs. 2 VKrG 2026). Überziehst du regelmäßig, muss sie dir eine Beratung anbieten, sofern sie eine hat, und dich kostenfrei an eine Schuldnerberatung verweisen (§ 37 Abs. 3).</p>
<p>Schon bisher gilt laut Arbeiterkammer: Liegt eine Überschreitung länger als drei Monate durchgehend über dem Eineinhalbfachen deiner durchschnittlichen monatlichen Eingänge, muss die Bank der jährlichen Entgeltaufstellung die Standardinformation zu einem Ratenkredit beilegen, der deinen Bedarf günstiger decken könnte, und dir eine Beratung dazu anbieten. In der Entgeltaufstellung stehen außerdem die tatsächlich verrechneten Sollzinsen des Jahres. Dort siehst du schwarz auf weiß, was dich das Minus gekostet hat.</p></div>'''),
       ('Alternativen zum Dauerminus',f'''<div class="prose"><ul>
<li><b>Ratenkredit.</b> Bist du seit Monaten im Minus, ist ein Ratenkredit meist deutlich günstiger und hat ein festes Ende. Mit dem <a href="{P}at/rechner/kreditrechner/">Kreditrechner</a> siehst du, welche Rate bei welcher Laufzeit nötig ist. Vergleiche den Effektivzins, nicht nur den Sollzins.</li>
<li><b>Rückzahlungsvereinbarung.</b> Will die Bank den Rahmen kürzen, empfiehlt die Arbeiterkammer, einen schrittweisen Abbau in Raten zu vereinbaren, statt alles auf einmal zurückzuzahlen.</li>
<li><b>Kreditkarte mit Teilzahlung.</b> Nur in Ausnahmefällen sinnvoll, weil die Zinsen oft höher sind als beim Überziehungsrahmen. Was dabei zu beachten ist, steht im Ratgeber <a href="{RG}teilzahlung/">Teilzahlung bei Kreditkarten</a>.</li>
<li><b>Günstigeres Konto.</b> Wenn du den Rahmen nur ein paar Tage im Monat brauchst, zählt der Zinssatz im Rahmen. Im <a href="{G1}">Girokonto-Vergleich</a> steht er auf jeder Kontoseite.</li>
<li><b>Schuldnerberatung.</b> Die staatlich anerkannten Schuldenberatungen beraten kostenlos, auch bevor es ernst wird.</li></ul></div>'''),
       ('Rahmen kündigen oder reduzieren','''<div class="prose"><p>Du kannst den Überziehungsrahmen jederzeit reduzieren oder ganz kündigen. Dafür reicht eine Nachricht an die Bank, am besten schriftlich oder im Online-Banking. Vorher musst du das Konto ausgleichen oder mit der Bank vereinbaren, wie du den offenen Betrag abbaust. Ein kleinerer Rahmen ist eine gute Bremse, wenn du merkst, dass das Minus jeden Monat wächst. Wer gar keinen Rahmen will, kann bei vielen Banken auch ein Konto auf Guthabenbasis führen.</p>
<p>Wichtig bei einem Kontowechsel: Das alte Konto muss ausgeglichen sein, sonst kann es nicht geschlossen werden. Wie der Wechsel abläuft, steht im Ratgeber <a href="../girokonto-wechseln/">Girokonto wechseln</a>.</p></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Zinsen im Rahmen und bei Überschreitung: Entgeltinformationen der Banken, verlinkt auf jeder Kontoseite. Die Werte werden beim Bauen dieser Seite aus den Kontodaten übernommen.</li>
<li>Verbraucherkreditgesetz 2026, §§ 32 bis 38 und § 45: {_ext(VKRG_2026,"BGBl. I Nr. 36/2026 (RIS)")}, {ABGERUFEN}.</li>
<li>Zinsspannen 2023, Verhandeln, Rahmenkürzung, Informationspflichten: Arbeiterkammer Wien, {_ext(AK_FAQ,"Fragen und Antworten zum Thema Girokonten (2023)")}; Arbeiterkammer, {_ext(AK_TIPPS,"Tipps bei Zahlungsproblemen beim Kredit (2021)")}.</li></ul></div>'''),
      ],
      faq=[
       ('Was ist der Unterschied zwischen Überziehungsrahmen und Überschreitung?','Der Überziehungsrahmen ist ein vereinbarter Kredit bis zu einem festen Betrag. Eine Überschreitung ist alles darüber hinaus oder ein Minus ohne Rahmen. Die Bank duldet sie nur, sie muss es nicht, und sie verrechnet dafür meist höhere Zinsen.'),
       ('Wie hoch sind die Überziehungszinsen in Österreich?',f'Im Vergleich kostet der Rahmen je nach Konto {_pct(rmin["sollzins"])} bis {_pct(rmax["sollzins"])} im Jahr, eine Überschreitung {_pct(umin["ueberschreitung"])} bis {_pct(umax["ueberschreitung"])}. Eine gesetzliche Obergrenze gibt es nicht.'),
       ('Darf die Bank meinen Überziehungsrahmen einfach streichen?','Sie darf ihn kürzen oder kündigen, etwa wenn dein Einkommen sinkt. Ab 20. November 2026 muss sie dich aber mindestens 30 Tage vorher informieren und dir vor einer Zwangsvollstreckung die Rückzahlung in zwölf Monatsraten anbieten.'),
       ('Muss mich die Bank warnen, wenn ich dauerhaft im Minus bin?','Ja. Bei einer erheblichen Überschreitung über mehr als einen Monat muss sie dich ab 20. November 2026 schriftlich über Betrag, Zinsen und Rückzahlungstermin informieren. Bei regelmäßiger Überschreitung muss sie dir eine Beratung anbieten und auf die Schuldnerberatung verweisen.'),
       ('Kann ich den Rahmen selbst kündigen?','Ja, jederzeit. Du musst nur das Konto ausgleichen oder mit der Bank vereinbaren, wie du den offenen Betrag abbaust.'),
       ('Ist ein Ratenkredit günstiger als das Minus am Konto?','Meist ja, wenn du länger als ein paar Monate im Minus bist. Ein Ratenkredit hat einen niedrigeren Zins und ein festes Ende. Vergleiche den Effektivzins.'),
      ],
      related=['gemeinschaftskonto','pfaendungsschutzkonto','konto-selbststaendige','kostenloses-girokonto','basiskonto'])

    # ---------- 2. Gemeinschaftskonto ----------
    gem=sorted([k for k in alle if k.get('gemeinschaftskonto') is True],key=lambda k:(k['kf_jahr'],k['bank'].lower()))
    nogem=sorted({k['bank'] for k in alle if k.get('gemeinschaftskonto') is False})
    gbank=sorted({k['bank'] for k in gem})
    grow=[(L(k),kfT(k),E((k.get('debitkarte') or {}).get('text') or 'keine Angabe'),E({'online':'nur online','filiale':'in der Filiale','beides':'online oder in der Filiale'}.get(k.get('eroeffnung'),'keine Angabe'))) for k in gem]
    art('at','gemeinschaftskonto',
      h1='Gemeinschaftskonto in Österreich: Oder-Konto, Und-Konto und die Haftung',
      mt='Gemeinschaftskonto Österreich: Haftung, Banken | Finvallo',
      desc=f'Gemeinschaftskonto in Österreich: Oder- oder Und-Konto, Haftung, Trennung, Einlagensicherung doppelt und {len(gem)} Konten im Vergleich, die es als Gemeinschaftskonto gibt.',
      about='Girokonten in Österreich',
      lede='Ein gemeinsames Konto macht die Haushaltskasse einfach. Es bindet aber auch zwei Menschen aneinander, bei Schulden genauso wie beim Guthaben.',
      kurz=(f'Beim Oder-Konto darf jeder Inhaber allein über das ganze Guthaben verfügen, beim Und-Konto nur alle gemeinsam. Für ein Minus haften alle Inhaber solidarisch, also jeder für den gesamten Betrag. '
            f'Im Vergleich bieten {len(gbank)} Banken ein Gemeinschaftskonto an, {len(nogem)} schließen es aus. Die Einlagensicherung gilt pro Person, bei zwei Inhabern sind also bis zu 200.000 € geschützt. '
            'Eine Schenkungssteuer gibt es in Österreich nicht, größere Beträge musst du aber dem Finanzamt melden.'),
      secs=[
       ('Oder-Konto oder Und-Konto',_tbl(['','Oder-Konto','Und-Konto'],[
            ('Wer darf verfügen','jeder Inhaber allein, über das ganze Guthaben','nur alle Inhaber gemeinsam'),
            ('Alltag','Überweisung, Karte, Dauerauftrag ohne den anderen','jede Überweisung braucht beide Unterschriften'),
            ('Typisch für','Paare, Familien, Wohngemeinschaften','Vereine, Erbengemeinschaften, Geschäftspartner'),
            ('Risiko','ein Inhaber kann das Konto allein leerräumen oder überziehen','blockiert, wenn einer nicht mitmacht'),
            ('Karten','meist eine Karte pro Inhaber','meist keine Karten')])+
        '<div class="prose"><p>Vereinbarst du nichts anderes, ist ein Gemeinschaftskonto ein Oder-Konto. Fast alle Konten im Vergleich sind Oder-Konten. Ein Und-Konto bieten Banken meist nur auf Nachfrage und selten mit Karte.</p></div>'),
       ('Wer haftet',f'''<div class="prose"><p>Alle Inhaber eines Gemeinschaftskontos haften der Bank gegenüber als Solidarschuldner (§ 891 ABGB). Das heißt: Überzieht dein Partner das Konto um 3.000 €, kann die Bank die vollen 3.000 € von dir verlangen, auch wenn du nie etwas abgehoben hast. Wie ihr das Geld intern aufteilt, ist der Bank egal. Deshalb solltest du den Überziehungsrahmen bei einem Gemeinschaftskonto klein halten oder ganz darauf verzichten. Wie der Rahmen funktioniert und was er kostet, steht im Ratgeber <a href="../kontoueberziehung/">Kontoüberziehung</a>.</p>
<p>Auch für die Kontoführung und die Karten haften beide. Zeichnungsberechtigte sind etwas anderes: Sie dürfen über das Konto verfügen, sind aber keine Inhaber und haften nicht. Bei manchen Banken kostet die Karte für Mitinhaber oder Zeichnungsberechtigte extra, etwa bei easybank 14,04 € bis 28,08 € im Jahr.</p></div>'''),
       ('Diese Konten gibt es als Gemeinschaftskonto',_tbl(['Konto','Kontoführung','Karten','Eröffnung'],grow)+
        f'''<div class="prose"><p>Das sind {len(gem)} Konten von {_fmtl(gbank)}. Nicht als Gemeinschaftskonto gibt es laut Bankangaben die Konten von {_fmtl(nogem)}. Bei den übrigen Banken fehlt eine bestätigte Angabe, frag dort vor der Eröffnung nach. Die Rangfolge nach Bewertung steht in der Bestenliste <a href="{B}gemeinschaftskonto/">Gemeinschaftskonten</a>. Die Kontoführung kostet beim Gemeinschaftskonto meist dasselbe wie beim Einzelkonto, nur die zweite Karte kann extra kosten.</p>
<p>Bei Online-Banken aus dem Ausland, etwa N26, Revolut oder bunq, läuft das Gemeinschaftskonto oft als Zusatz zum eigenen Konto jedes Partners. Beide brauchen dann ein eigenes Konto bei dieser Bank.</p></div>'''),
       ('Einlagensicherung: 100.000 € pro Person','''<div class="prose"><p>Die gesetzliche Einlagensicherung schützt 100.000 € pro Einleger und Bank, nicht pro Konto. Bei einem Gemeinschaftskonto mit zwei Inhabern sind also bis zu 200.000 € geschützt. Ohne andere schriftliche Vereinbarung wird das Guthaben im Sicherungsfall zu gleichen Teilen auf die Inhaber aufgeteilt. Hat ein Inhaber bei derselben Bank noch ein eigenes Konto, zählt sein Anteil am Gemeinschaftskonto zu seinen 100.000 € dazu.</p>
<p>Das gilt für Banken mit Sitz in Österreich über die Einlagensicherung AUSTRIA. Konten bei N26, Revolut oder bunq sind über die Einlagensicherung in Deutschland, Litauen oder den Niederlanden geschützt, ebenfalls mit 100.000 € pro Person. Welche Sicherung gilt, steht auf jeder Kontoseite.</p></div>'''),
       ('Trennung: So löst du ein Gemeinschaftskonto auf','''<div class="prose"><ol>
<li><b>Einzelverfügung widerrufen.</b> Nach den Geschäftsbedingungen der Banken kann jeder Inhaber eines Oder-Kontos der Bank mitteilen, dass er die Einzelverfügung des anderen widerruft. Danach geht nur noch gemeinsam. Das stoppt, dass einer das Konto leerräumt.</li>
<li><b>Guthaben aufteilen.</b> Im Zweifel gehört das Guthaben beiden zur Hälfte, unabhängig davon, wer eingezahlt hat. Könnt ihr euch nicht einigen, entscheidet das Gericht. Belege über eigene Einzahlungen helfen.</li>
<li><b>Minus ausgleichen.</b> Ein Gemeinschaftskonto im Minus kann nicht geschlossen werden. Die Bank hält sich an beide.</li>
<li><b>Daueraufträge und Lastschriften umziehen.</b> Miete, Strom, Versicherungen und Abos auf das neue Einzelkonto umstellen. Die Checkliste dazu steht im Ratgeber <a href="../girokonto-wechseln/">Girokonto wechseln</a>.</li>
<li><b>Gemeinsam kündigen.</b> Kündigen und schließen können nur alle Inhaber zusammen. Ein Inhaber allein kann nur seinen Ausstieg als Inhaber verlangen, wenn die Bank das zulässt.</li></ol></div>'''),
       ('Schenkungsmeldung statt Schenkungssteuer',f'''<div class="prose"><p>Eine Schenkungs- und Erbschaftssteuer gibt es in Österreich seit 2008 nicht mehr. Dafür gilt eine Meldepflicht (§ 121a BAO): Schenkungen zwischen Angehörigen, also auch zwischen Ehepartnern und Lebensgefährten, musst du dem Finanzamt melden, wenn sie innerhalb eines Jahres 50.000 € übersteigen. Zwischen anderen Personen liegt die Grenze bei 15.000 € in fünf Jahren. Zahlt ein Partner eine Erbschaft oder einen Hausverkauf auf das gemeinsame Oder-Konto ein, kann die Hälfte als Schenkung an den anderen gelten. Für die Meldung ist das Formular Schenk 1 bei FinanzOnline da; sie ist kostenlos, nur das Versäumnis kostet.</p>
<p>Bei einer Pfändung gegen einen Inhaber kann das gemeinsame Guthaben betroffen sein. Was dann geschützt ist, steht im Ratgeber <a href="../pfaendungsschutzkonto/">Pfändungsschutz am Konto</a>.</p></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Gemeinschaftskonto möglich oder nicht, Kartenpreise, Eröffnung: Angaben der Banken, verlinkt auf jeder Kontoseite. Die Werte werden beim Bauen dieser Seite aus den Kontodaten übernommen.</li>
<li>Einlagensicherung bei Gemeinschaftskonten (ESAEG): {_ext(BAWAG_ES,"BAWAG, Information zur Einlagensicherung und Anlegerentschädigung")}, {ABGERUFEN}.</li>
<li>Schenkungsmeldung: {_ext(BMF_SCHENK,"Bundesministerium für Finanzen, Schenkungsmeldung")}, {ABGERUFEN}.</li>
<li>Solidarhaftung: § 891 ABGB; Überziehung und Haftung: Arbeiterkammer Wien, {_ext(AK_FAQ,"Fragen und Antworten zum Thema Girokonten (2023)")}.</li></ul></div>'''),
      ],
      faq=[
       ('Was ist der Unterschied zwischen Oder-Konto und Und-Konto?','Beim Oder-Konto darf jeder Inhaber allein über das ganze Guthaben verfügen. Beim Und-Konto geht nur gemeinsam, jede Überweisung braucht alle Inhaber. Ohne andere Vereinbarung ist ein Gemeinschaftskonto ein Oder-Konto.'),
       ('Hafte ich für die Schulden meines Partners am Gemeinschaftskonto?','Ja. Alle Inhaber haften solidarisch, die Bank kann den vollen Minusbetrag von jedem verlangen. Halte den Überziehungsrahmen deshalb klein.'),
       ('Welche Banken bieten in Österreich ein Gemeinschaftskonto an?',f'Im Vergleich: {_fmtl(gbank)}. Nicht als Gemeinschaftskonto gibt es die Konten von {_fmtl(nogem)}.'),
       ('Ist das Guthaben auf einem Gemeinschaftskonto doppelt gesichert?','Ja. Die Einlagensicherung gilt mit 100.000 € pro Einleger und Bank. Bei zwei Inhabern sind bis zu 200.000 € geschützt, ohne andere Vereinbarung je zur Hälfte.'),
       ('Kann ein Partner das Gemeinschaftskonto allein kündigen?','Nein. Kündigen und schließen können nur alle Inhaber gemeinsam. Jeder kann aber die Einzelverfügung des anderen widerrufen, dann geht nur noch gemeinsam.'),
       ('Fällt Schenkungssteuer an, wenn mein Partner viel Geld einzahlt?','Nein, eine Schenkungssteuer gibt es in Österreich nicht. Schenkungen zwischen Angehörigen über 50.000 € in einem Jahr musst du aber dem Finanzamt melden.'),
      ],
      related=['kontoueberziehung','pfaendungsschutzkonto','kinderkonto-jugendkonto','kostenloses-girokonto','girokonto-wechseln'])

    # ---------- 3. Pfändungsschutz am Konto ----------
    basis=sorted([k for k in ks if k['art']=='basis'],key=lambda k:k['kf_jahr'])
    grund=1308.39
    art('at','pfaendungsschutzkonto',pair='p-konto',
      h1='Pfändungsschutz am Konto in Österreich: So bleibt dir das Existenzminimum',
      mt='Kontopfändung Österreich: Existenzminimum sichern | Finvallo',
      desc=f'Kontopfändung in Österreich: Kein P-Konto, aber ein Antrag nach § 292i EO beim Exekutionsgericht. Existenzminimum 2026 ({eur(grund)} €), 14-Tage-Frist und Ablauf.',
      about='Girokonten in Österreich',
      lede='Wird dein Konto gepfändet, ist erst einmal alles gesperrt, auch das Gehalt für Miete und Essen. Das Gesetz lässt dir das Existenzminimum, aber nur, wenn du es beantragst.',
      kurz=(f'Anders als in Deutschland gibt es in Österreich kein Pfändungsschutzkonto, das automatisch einen Freibetrag schützt. Stattdessen stellst du nach einer Kontopfändung beim Exekutionsgericht einen Antrag nach § 292i Exekutionsordnung. '
            f'Das Gericht hebt die Pfändung dann für den unpfändbaren Teil deiner Einkünfte bis zum nächsten Zahltag auf. Der allgemeine Grundbetrag des Existenzminimums liegt 2026 bei {eur(grund)} € im Monat. '
            'Die Bank darf gepfändetes Guthaben frühestens 14 Tage nach Zustellung an den Gläubiger auszahlen, so lange hast du Zeit.'),
      secs=[
       ('Was bei einer Kontopfändung passiert','''<div class="prose"><p>Hat ein Gläubiger einen Exekutionstitel, etwa ein Urteil oder einen Zahlungsbefehl, kann er beim Bezirksgericht die Forderungsexekution auf dein Konto beantragen. Die Bank ist dann Drittschuldnerin. Sie darf dir nichts mehr auszahlen, bis zur Höhe der Forderung. Die Pfändung erfasst das Guthaben zum Zeitpunkt der Zustellung und, je nach Beschluss, auch künftige Eingänge.</p>
<p>Zwei Schutzregeln gelten dabei (§ 292i EO):</p><ul>
<li><b>14 Tage Sperre.</b> Gepfändetes Guthaben einer Privatperson darf die Bank frühestens 14 Tage, nachdem ihr der Überweisungsbeschluss zugestellt wurde, an den Gläubiger zahlen oder hinterlegen. In dieser Zeit kannst du den Antrag auf Kontenschutz stellen.</li>
<li><b>Existenzminimum auf Antrag.</b> Wurden beschränkt pfändbare Einkünfte wie Gehalt, Pension oder Arbeitslosengeld auf das Konto überwiesen, hebt das Exekutionsgericht die Pfändung auf deinen Antrag so weit auf, wie das Guthaben dem unpfändbaren Teil dieser Einkünfte bis zum nächsten Zahltag entspricht.</li></ul>
<p>Pfändet das Finanzamt, gilt dieselbe Regel nach § 54 Abgabenexekutionsordnung. Der Antrag geht dann an das Finanzamt statt an das Gericht.</p></div>'''),
       ('Das Existenzminimum 2026',_tbl(['Posten','Betrag pro Monat','Grundlage'],[
            ('Allgemeiner Grundbetrag (Ausgleichszulagenrichtsatz für Alleinstehende)',f'{eur(grund)} €','§ 291a Abs. 1 EO'),
            ('Erhöhter Grundbetrag, wenn keine Sonderzahlungen (13. und 14. Gehalt) ausbezahlt werden',f'{eur(round(grund*7/6,2))} €','um ein Sechstel erhöht, § 291a Abs. 2 EO'),
            ('Unterhaltsgrundbetrag je Person, der du gesetzlich Unterhalt zahlst (höchstens fünf)',f'{eur(round(grund*0.2,2))} €','20 % des Grundbetrags, § 291a Abs. 2 EO')])+
        f'''<div class="prose"><p>Das Existenzminimum ist der Teil deines Einkommens, der bei einer Lohn- oder Gehaltspfändung unpfändbar bleibt. Der Grundbetrag ist an den Ausgleichszulagenrichtsatz gekoppelt, der 2026 bei {eur(grund)} € liegt. Vom Einkommen über dem Grundbetrag bleibt dir zusätzlich ein Teil als Steigerungsbetrag. Die genauen Werte stehen in den Existenzminimum-Tabellen des Justizministeriums, sie sind in 20-Euro-Schritten aufgebaut. Ganz unpfändbar sind unter anderem Familienbeihilfe, Kinderbetreuungsgeld und Pflegegeld (§ 290 EO).</p>
<p>Wichtig: Bei einer Lohnpfändung behält dein Arbeitgeber den pfändbaren Teil ein und überweist dir nur das Existenzminimum. Landet dieses Geld auf einem gepfändeten Konto, wäre es ohne den Kontenschutz ein zweites Mal weg. Genau das verhindert der Antrag nach § 292i EO.</p></div>'''),
       ('So stellst du den Antrag',f'''<div class="prose"><ol>
<li><b>Schnell handeln.</b> Du hast 14 Tage ab Zustellung des Beschlusses an die Bank. Die Bank informiert dich meist mit einem Brief über die Pfändung.</li>
<li><b>Antrag beim Exekutionsgericht.</b> Zuständig ist das Bezirksgericht, das die Exekution bewilligt hat. Es steht auf dem Beschluss. Der Antrag heißt „Antrag auf Aufhebung der Pfändung nach § 292i EO“ und ist formlos möglich. Beim Amtstag des Gerichts hilft man dir beim Ausfüllen.</li>
<li><b>Glaubhaft machen.</b> Leg Kontoauszüge und Gehalts- oder Pensionsabrechnungen bei, die zeigen, dass beschränkt pfändbare Einkünfte auf das Konto kamen und wie hoch dein Existenzminimum ist.</li>
<li><b>Dringenden Unterhalt beantragen.</b> Brauchst du sofort Geld für Miete und Essen, kannst du beantragen, dass das Gericht vorab den Teil freigibt, den du bis zum nächsten Zahltag dringend brauchst (§ 292i Abs. 3 EO). Das geht ohne Anhörung des Gläubigers, wenn ein Aufschub für dich unzumutbar wäre.</li>
<li><b>Für jede Pfändung neu.</b> Der Beschluss gilt für das gepfändete Guthaben bis zum nächsten Zahltag. Läuft die Pfändung weiter, musst du den Antrag für die nächsten Eingänge wieder stellen.</li></ol>
<p>Hilfe bekommst du kostenlos bei den staatlich anerkannten Schuldenberatungen ({_ext(SCHULDEN,"schuldenberatung.at")}). Sie prüfen auch, ob ein Schuldenregulierungsverfahren sinnvoll ist.</p></div>'''),
       ('Welches Konto bei Pfändung',f'''<div class="prose"><p>Eine Pfändung ist kein Grund, dir ein Konto zu verweigern. Jede Person mit rechtmäßigem Aufenthalt in der EU hat Anspruch auf ein <a href="../basiskonto/">Basiskonto</a>, auch mit Schulden oder im Privatkonkurs. Es hat keinen Überziehungsrahmen, du kannst also nicht weiter ins Minus rutschen. Im Vergleich kosten Basiskonten {eur(basis[0]["kf_jahr"])} € bis {eur(basis[-1]["kf_jahr"])} € im Jahr, für besonders schutzbedürftige Personen gilt auf Antrag die Hälfte.</p>
<p>Ein Gemeinschaftskonto ist bei einer Pfändung ungünstig, weil das gemeinsame Guthaben betroffen sein kann. Besser ist ein eigenes Konto für jede Person. Auch sinnvoll: Lass dir Gehalt oder Pension auf ein Konto überweisen, auf dem sonst nichts liegt. Dann ist leicht nachzuweisen, dass das Guthaben aus beschränkt pfändbaren Einkünften stammt.</p>
<p>Die Bank darf dein Konto wegen einer Pfändung kündigen, wenn das in ihren Bedingungen steht. Beim Basiskonto ist die Kündigung nur aus gesetzlichen Gründen erlaubt.</p></div>'''),
       ('Unterschied zu Deutschland','''<div class="prose"><p>In Deutschland wandelt die Bank ein Girokonto auf Verlangen in ein Pfändungsschutzkonto um. Dort ist dann automatisch ein Grundfreibetrag pro Monat geschützt, ohne Gericht. In Österreich gibt es dieses Modell nicht. Der Schutz hängt am Antrag beim Exekutionsgericht und am Nachweis, woher das Geld kommt. Dafür ist die Lohnpfändung in Österreich schon beim Arbeitgeber auf das Existenzminimum beschränkt. Wer in Deutschland arbeitet und dort ein Konto hat, liest besser den deutschen Ratgeber zum P-Konto, oben über den Länderschalter erreichbar.</p></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Kontenschutz: {_ext(EO_292I,"§ 292i Exekutionsordnung (Fassung seit 1.7.2021)")}, {ABGERUFEN}.</li>
<li>Existenzminimum und Ausgleichszulagenrichtsatz 2026: {_ext(GV_EXMIN,"oesterreich.gv.at, Existenzminimum")} und {_ext(GV_PENSION,"oesterreich.gv.at, Pensionsanpassung 2026")}, {ABGERUFEN}. Grundlage: § 291a EO.</li>
<li>Schuldenberatung: {_ext(SCHULDEN,"ASB Schuldnerberatungen GmbH")}.</li>
<li>Preise der Basiskonten: Entgeltinformationen der Banken, verlinkt auf jeder Kontoseite.</li></ul></div>'''),
      ],
      faq=[
       ('Gibt es in Österreich ein Pfändungsschutzkonto?','Nein. Es gibt kein P-Konto wie in Deutschland. Nach einer Kontopfändung beantragst du beim Exekutionsgericht, dass die Pfändung für das Existenzminimum aufgehoben wird (§ 292i EO).'),
       ('Wie viel bleibt mir bei einer Kontopfändung?',f'Der unpfändbare Teil deiner Einkünfte bis zum nächsten Zahltag. Der allgemeine Grundbetrag liegt 2026 bei {eur(grund)} € im Monat, mehr bei Unterhaltspflichten und ohne Sonderzahlungen.'),
       ('Wie viel Zeit habe ich nach der Pfändung?','14 Tage. So lange darf die Bank gepfändetes Guthaben nicht an den Gläubiger auszahlen, gerechnet ab Zustellung des Überweisungsbeschlusses an die Bank.'),
       ('Wo stelle ich den Antrag?','Beim Bezirksgericht, das die Exekution bewilligt hat. Pfändet das Finanzamt, beim Finanzamt. Der Antrag ist formlos, Kontoauszüge und Gehaltsabrechnungen gehören dazu.'),
       ('Darf mir die Bank wegen einer Pfändung das Konto kündigen?','Ein normales Konto kann sie kündigen, wenn das in ihren Bedingungen steht. Ein Basiskonto bekommst du trotzdem, es darf nur aus gesetzlichen Gründen gekündigt werden.'),
      ],
      related=['kontoueberziehung','gemeinschaftskonto','basiskonto','kostenloses-girokonto','girokonto-wechseln'])

    # ---------- 4. Kinderkonto und Jugendkonto ----------
    kinder=sorted([k for k in ks if k['art']=='kinder'],key=lambda k:((k.get('alter') or {}).get('min') or 0,k['bank'].lower()))
    jugend=sorted([k for k in ks if k['art']=='jugend'],key=lambda k:((k.get('alter') or {}).get('min') or 0,k['bank'].lower()))
    krow=[(L(k),altT(k),debT(k),kfT(k)) for k in kinder]
    jrow=[(L(k),altT(k),debT(k),kfT(k)) for k in jugend]
    jfree=[k for k in jugend if k['kf_jahr']==0]; jpaid=[k for k in jugend if k['kf_jahr']>0]
    jmin=min((k.get('alter') or {}).get('min') or 99 for k in jugend)
    art('at','kinderkonto-jugendkonto',
      h1='Kinderkonto und Jugendkonto in Österreich: Ab wann, mit welcher Karte, zu welchen Regeln',
      mt='Kinderkonto und Jugendkonto Österreich | Finvallo',
      desc=f'Kinderkonto und Jugendkonto in Österreich: ab welchem Alter, wer eröffnet, Karten und Limits, was mit 18 passiert. {len(kinder)} Kinder- und {len(jugend)} Jugendkonten im Vergleich.',
      about='Girokonten in Österreich',
      lede='Das erste eigene Konto ist ein kleiner Schritt in die Selbstständigkeit. Welche Karte das Kind bekommt und wie viel es abheben darf, legt die Bank fest, die Eltern haben das letzte Wort.',
      kurz=(f'Ein Kinderkonto eröffnen die Eltern, bei vielen Banken ab der Geburt oder ab 7 Jahren. Ab 14 gibt es Jugendkonten, die Jugendliche mit eigenem Einkommen teils ohne Unterschrift der Eltern eröffnen können. '
            f'Beide laufen auf Guthabenbasis, ohne Überziehungsrahmen, und sind bis auf wenige Ausnahmen kostenlos: {len(kinder)} Kinderkonten und {len(jfree)} von {len(jugend)} Jugendkonten im Vergleich kosten keine Kontoführung. '
            'Die Debitkarte hat ein Wochenlimit, meist 50 € bei Kindern und 200 bis 400 € bei Jugendlichen. Mit 18 bis 20 stellt die Bank auf ein normales Konto um.'),
      secs=[
       ('Ab welchem Alter und wer eröffnet',f'''<div class="prose"><p>Das österreichische Recht teilt Minderjährige in zwei Gruppen (§ 170 ABGB):</p><ul>
<li><b>Unter 14 (unmündig):</b> Das Kind kann nur Taschengeldgeschäfte selbst abschließen. Ein Konto eröffnen die Eltern oder andere gesetzliche Vertreter. Das Kind ist Kontoinhaber, die Eltern verwalten das Konto. Banken verlangen den Ausweis der Eltern, die Geburtsurkunde oder den Ausweis des Kindes und bei getrennten Eltern oft die Unterschrift beider Obsorgeberechtigten.</li>
<li><b>14 bis 17 (mündig):</b> Jugendliche dürfen über ihr Einkommen aus eigener Arbeit, etwa die Lehrlingsentschädigung, selbst verfügen und sich damit verpflichten, solange ihre Lebensbedürfnisse gedeckt bleiben. Darauf stützen sich Banken, die ein Jugendkonto ab 14 ohne Unterschrift der Eltern eröffnen. Im Vergleich sagen das easybank und Wüstenrot Bank ausdrücklich. Andere Banken verlangen bis 18 die Zustimmung der Eltern.</li></ul>
<p>Das jüngste Einstiegsalter für ein Jugendkonto im Vergleich sind {jmin} Jahre beim spark7 Jugendkonto der Erste Bank, unter 14 mit gesetzlichem Vertreter. Für Studierende und junge Erwachsene gibt es danach eigene Konten, die in der Bestenliste <a href="{B}studenten/">Studentenkonten</a> stehen.</p></div>'''),
       ('Kinderkonten im Vergleich',_tbl(['Konto','Alter','Karte und Limit','Kontoführung'],krow)+
        f'''<div class="prose"><p>Alle {len(kinder)} Kinderkonten im Vergleich sind kostenlos. Die Karte bekommt das Kind meist ab 6 oder 7 Jahren, oft ohne Kontaktlos-Funktion und mit einem Limit von 50 € pro Woche. Online-Zahlungen sind bei vielen Kinderkarten gesperrt. Die Rangfolge steht in der Bestenliste <a href="{B}kinder/">Kinderkonten</a>.</p>
<p>Nicht im Vergleich sind Kinderkarten, die am Konto der Eltern hängen, etwa bei N26, Revolut oder bunq. Dort hat das Kind kein eigenes Konto mit eigener IBAN, und bei bunq kostet das nur zusammen mit einem bezahlten Abo der Eltern.</p></div>'''),
       ('Jugendkonten im Vergleich',_tbl(['Konto','Alter','Karte und Limit','Kontoführung'],jrow)+
        f'''<div class="prose"><p>{len(jfree)} der {len(jugend)} Jugendkonten sind kostenlos{", nur "+_fmtl([k["name"]+" ("+k["bank"]+")" for k in jpaid])+" kostet Kontoführung" if jpaid else ""}. Jugendkonten haben keinen Überziehungsrahmen, einen Kredit dürfen Minderjährige nicht aufnehmen. Die Debitkarte funktioniert in Geschäften, am Bankomaten und meist auch online und in Apple Pay oder Google Pay. Das Wochenlimit liegt je nach Bank bei 200 bis 400 €, die Eltern können es oft anpassen. Die Rangfolge steht in der Bestenliste <a href="{B}jugend/">Jugendkonten</a>.</p></div>'''),
       ('Taschengeldkonto oder Jugendkonto',_tbl(['','Kinderkonto (Taschengeldkonto)','Jugendkonto'],[
            ('Alter','ab Geburt oder ab 7 bis 13','ab 14 (spark7 ab 10) bis 17 bis 20'),
            ('Eröffnung','nur durch die Eltern','mit eigenem Einkommen teils allein, sonst mit den Eltern'),
            ('Karte','Debitkarte ab 6 oder 7, kleines Limit, teils ohne Kontaktlos und Online-Zahlung','Debitkarte mit Kontaktlos, Online-Zahlung und Wallet'),
            ('Überziehen','nicht möglich','nicht möglich'),
            ('Wofür','Taschengeld, erste Einkäufe, Sparen','Lehrlingsentschädigung, Ferialjob, Handy, Ausgehen'),
            ('Danach','automatisch Jugendkonto','automatisch Erwachsenenkonto, oft erst ab 20')])+
        '<div class="prose"><p>Ein Sparbuch oder Sparkonto ist etwas anderes: Dort gibt es keine Karte und keine Überweisungen, dafür Zinsen. Für Taschengeld, das ausgegeben werden soll, ist das Kinderkonto praktischer.</p></div>'),
       ('Was mit 18 passiert','''<div class="prose"><p>Mit 18 endet die Vertretung durch die Eltern. Das Konto gehört dem Kind schon vorher, ab jetzt kann es allein darüber bestimmen, auch einen Überziehungsrahmen beantragen und die Eltern als Verfügungsberechtigte streichen. Die Bank stellt das Konto nicht immer sofort um:</p><ul>
<li>easybank stellt easy youth mit 18 automatisch auf easy gratis um.</li>
<li>Bank Austria führt das MegaCard-Konto bis zum vollendeten 20. Lebensjahr und stellt dann auf das Online-Konto um.</li>
<li>BAWAG stellt im Monat nach dem 20. Geburtstag um, bank99 mit dem 21. Geburtstag.</li>
<li>Erste Bank führt das spark7 Jugendkonto für Schülerinnen, Schüler und Lehrlinge bis zum 19. Geburtstag gratis und stellt dann auf das s Plus Konto um.</li></ul>
<p>Nach der Umstellung kostet das Konto meist Kontoführung. Studierende bekommen bei vielen Banken ein Studentenkonto, das weiter gratis ist. Wer nicht studiert, vergleicht am besten rechtzeitig vor der Umstellung: Im <a href="../kostenloses-girokonto/">Ratgeber zum kostenlosen Girokonto</a> stehen die Konten ohne Kontoführung, und der <a href="../girokonto-wechseln/">Kontowechsel</a> ist mit dem gesetzlichen Service einfach.</p></div>'''),
       ('Worauf Eltern achten sollten','''<div class="prose"><ul class="checks">
<li>Limit der Karte: Lässt es sich in der App anpassen, und sind Online-Zahlungen sperrbar?</li>
<li>Bargeld: Gibt es Gratis-Abhebungen auch an fremden Bankomaten?</li>
<li>Bedingung: Muss ein Elternteil Kunde der Bank sein? Bei easybank ja, bei anderen nicht.</li>
<li>Zinsen auf Guthaben: Manche Kinderkonten verzinsen das Guthaben, das steht auf der Kontoseite.</li>
<li>Umstellung: Wann und auf welches Konto stellt die Bank um, und was kostet es dann?</li>
<li>Wohnsitz: Manche Banken verlangen, dass der Hauptwohnsitz seit mindestens einem Jahr in Österreich ist.</li></ul></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Alter, Karten, Limits, Umstellung, Kontoführung: Produktseiten und Entgeltinformationen der Banken, verlinkt auf jeder Kontoseite. Die Werte werden beim Bauen dieser Seite aus den Kontodaten übernommen.</li>
<li>Geschäftsfähigkeit von Kindern und Jugendlichen: {_ext(GV_GESCH,"oesterreich.gv.at, Übersicht der Geschäftsfähigkeit")} und {_ext(ABGB_170,"§ 170 ABGB (RIS)")}, {ABGERUFEN}.</li>
<li>Jugend- und Lehrlingskonten: Arbeiterkammer Oberösterreich, {_ext(AK_JUGEND,"Jugend- und Lehrlingskonten im Vergleich")}.</li></ul></div>'''),
      ],
      faq=[
       ('Ab welchem Alter kann mein Kind ein Konto haben?','Ein Kinderkonto eröffnen die Eltern bei vielen Banken ab der Geburt, die Karte gibt es meist ab 6 oder 7 Jahren. Ein Jugendkonto gibt es ab 14, beim spark7 Jugendkonto der Erste Bank ab 10.'),
       ('Kann ein 14-Jähriger ein Konto ohne Eltern eröffnen?','Mit eigenem Einkommen, etwa einer Lehrlingsentschädigung, erlaubt das Gesetz ab 14 eigene Verfügungen. easybank und Wüstenrot Bank eröffnen Jugendkonten ohne Unterschrift der Eltern, andere Banken verlangen sie bis 18.'),
       ('Kann ein Jugendkonto überzogen werden?','Nein. Kinder- und Jugendkonten laufen auf Guthabenbasis, einen Kredit dürfen Minderjährige nicht aufnehmen.'),
       ('Was kostet ein Kinderkonto?',f'Alle {len(kinder)} Kinderkonten im Vergleich sind kostenlos, ebenso {len(jfree)} von {len(jugend)} Jugendkonten.'),
       ('Was passiert mit dem Jugendkonto mit 18?','Das Kind bestimmt ab 18 allein über das Konto. Die Bank stellt je nach Modell mit 18, 19, 20 oder 21 auf ein normales Konto um, das dann meist Kontoführung kostet.'),
      ],
      related=['gemeinschaftskonto','konto-selbststaendige','kostenloses-girokonto','girokonto-wechseln','basiskonto'])

    # ---------- 5. Konto für Selbstständige ----------
    kand=sorted([k for k in alle if not (k.get('gratis') and k['gratis'].get('eingang_min') is not None and 'gehalt' in ((k['gratis'].get('eingang_art') or '')+(k['gratis'].get('text') or '')).lower() and k['kf_jahr']>0)],key=lambda k:(k['kf_jahr'],k['bank'].lower()))
    gehbed=[k for k in alle if k.get('gratis') and 'unselbst' in ((k['gratis'].get('sonst') or '')+(k['gratis'].get('text') or '')).lower()]
    srow=[(L(k),kfT(k),E((k.get('gratis') or {}).get('text') or ('kostenlos ohne Bedingung' if k['kf_jahr']==0 else 'keine')),E({'AT':'österreichisch','DE':'deutsch','LT':'litauisch','NL':'niederländisch'}.get(k.get('iban'),'keine Angabe'))) for k in kand[:10]]
    art('at','konto-selbststaendige',
      h1='Konto für Selbstständige in Österreich: Privatkonto oder Geschäftskonto?',
      mt='Konto für Selbstständige in Österreich | Finvallo',
      desc='Konto für Selbstständige in Österreich: Wann du ein Geschäftskonto brauchst, was Banken bei Privatkonten erlauben, Buchhaltung, Umsatzsteuer und passende Konten.',
      about='Girokonten in Österreich',
      lede='Als Einzelunternehmerin oder Freiberufler zwingt dich kein Gesetz zu einem Geschäftskonto. Deine Bank und dein Steuerberater sehen das oft anders.',
      kurz=('Einzelunternehmen und freie Berufe brauchen in Österreich kein eigenes Geschäftskonto, eine GmbH schon. Viele Banken schließen die geschäftliche Nutzung eines Privatkontos in ihren Bedingungen aber aus oder stellen dann auf ein teureres Modell um. '
            'Ein getrenntes Konto erleichtert die Einnahmen-Ausgaben-Rechnung, die Umsatzsteuer und eine Prüfung durch das Finanzamt. Belege musst du sieben Jahre aufbewahren. '
            'Bis 55.000 € Umsatz im Jahr kannst du die Kleinunternehmerregelung nutzen und keine Umsatzsteuer verrechnen.'),
      secs=[
       ('Brauchst du ein Geschäftskonto?',f'''<div class="prose"><p>Für Einzelunternehmen und freie Berufe gibt es in Österreich keine gesetzliche Pflicht, ein eigenes Geschäftskonto zu führen. Das bestätigt die Wirtschaftskammer. Die Einnahmen-Ausgaben-Rechnung verlangt nur, dass du jede Einnahme und Ausgabe mit Beleg nachweisen kannst. Anders bei Kapitalgesellschaften: Für eine GmbH oder FlexKapG brauchst du schon bei der Gründung ein Konto auf den Namen der Gesellschaft, weil das Stammkapital dort eingezahlt wird und die Bank die Einzahlung bestätigt.</p>
<p>Trotzdem sprechen drei Gründe für ein getrenntes Konto, auch wenn es nur ein zweites Privatkonto ist:</p><ol>
<li><b>Die Bank.</b> Die Geschäftsbedingungen vieler Banken erlauben das Privatkonto nur für private Zwecke. Regelmäßige Kundenzahlungen, Kartenterminals oder viele Buchungen fallen auf. Die Bank kann dann auf ein Geschäftskonto umstellen oder kündigen.</li>
<li><b>Das Finanzamt.</b> Bei einer Prüfung musst du Kontoauszüge vorlegen. Liegen private und betriebliche Buchungen auf einem Konto, siehst du das ganze Privatleben mit, und ungeklärte Eingänge können als Einnahmen gewertet werden.</li>
<li><b>Der Überblick.</b> Umsatzsteuer, Sozialversicherung bei der SVS und Einkommensteuer kommen in Vorauszahlungen. Auf einem eigenen Konto siehst du, was davon schon weg ist.</li></ol></div>'''),
       ('Was die Banken im Vergleich dazu sagen',f'''<div class="prose"><p>Die Banken im Vergleich bieten Privatkonten an. Ob sie eine geschäftliche Nutzung dulden, steht in den Geschäftsbedingungen, nicht in der Entgeltinformation. Ein paar Hinweise aus den Kontodaten:</p><ul>
<li>Gehaltskonten setzen oft ein Gehalt aus unselbstständiger Arbeit voraus. {("Bei "+_fmtl([k["name"]+" ("+k["bank"]+")" for k in gehbed])+" gilt die Gratis-Bedingung ausdrücklich nur für unselbstständige Erwerbstätigkeit; ohne Gehaltseingang zahlst du den normalen Preis.") if gehbed else "Für Selbstständige zählt die Gratis-Bedingung dann nicht."}</li>
<li>N26, Revolut und bunq haben eigene Geschäftskonten für Selbstständige. Ihre Privatkonten sind laut Bedingungen nur für private Zwecke gedacht. Diese Geschäftskonten sind nicht im Vergleich, weil der Vergleich Privatkonten bewertet.</li>
<li>Filialbanken wie Erste Bank, BAWAG, Bank Austria und bank99 führen Geschäftskonten als eigene Produkte mit eigener Preisliste, meist mit Preis pro Buchung.</li></ul>
<p>Frag vor der Eröffnung schriftlich nach, ob du das Konto für dein Einzelunternehmen nutzen darfst. Die Antwort hebst du auf.</p></div>'''),
       ('Welche Privatkonten für ein kleines Unternehmen in Frage kommen',_tbl(['Konto','Kontoführung','Gratis-Bedingung','IBAN'],srow)+
        f'''<div class="prose"><p>Die Tabelle zeigt die zehn günstigsten Konten für alle ohne Gehaltsbedingung, nach der regulären Kontoführung sortiert. Für ein Nebengewerbe mit ein paar Buchungen im Monat reicht oft ein kostenloses Konto. Wer viele Buchungen hat, achtet auf Konten mit Pauschalpreis statt Einzelpreisen. Eine österreichische IBAN ist für Kunden und Behörden am einfachsten, obwohl sie laut SEPA-Verordnung jede EU-IBAN annehmen müssen. Alle Konten mit Jahreskosten für dein Profil stehen im <a href="{G1}">Girokonto-Vergleich</a>.</p>
<p>Für Ausgaben unterwegs und online ist eine eigene Firmenkarte praktisch. Welche es gibt und was sie kosten, steht im <a href="{P}at/kreditkarten/business/">Vergleich der Business-Kreditkarten</a> und im Ratgeber <a href="{RG}business/">Business-Kreditkarten</a>.</p></div>'''),
       ('Buchhaltung: Trennung und Belege',f'''<div class="prose"><p>Die meisten Einzelunternehmen rechnen mit der Einnahmen-Ausgaben-Rechnung ab. Dabei zählt, wann Geld auf dem Konto ankommt oder abgeht. Ein eigenes Konto ist dafür die einfachste Grundlage: Der Kontoauszug ist das Journal, jede Buchung braucht einen Beleg. Bücher, Aufzeichnungen und Belege musst du laut § 132 BAO <b>sieben Jahre</b> aufbewahren, gerechnet ab Ende des Kalenderjahres, auch elektronisch. Bei Grundstücken gelten längere Fristen.</p>
<p>Privatentnahmen überweist du als festen Betrag im Monat auf das Privatkonto, statt private Einkäufe vom Geschäftskonto zu zahlen. So bleibt die Einnahmen-Ausgaben-Rechnung sauber, und du siehst, was das Unternehmen wirklich abwirft. Verlangt deine Steuerberaterin eine Verrechnungsschnittstelle, prüfe, ob die Bank Umsätze als CSV oder CAMT exportiert und ob Buchhaltungsprogramme sich anbinden lassen. Online-Banken sind hier oft weiter als Filialbanken.</p></div>'''),
       ('Umsatzsteuer und Kleinunternehmer',f'''<div class="prose"><p>Bis 55.000 € Umsatz brutto im Jahr bist du Kleinunternehmer und verrechnest keine Umsatzsteuer, darfst dann aber auch keine Vorsteuer abziehen. Überschreitest du die Grenze um höchstens 10 %, also bis 60.500 €, bleibst du im laufenden Jahr noch befreit. Darüber hinaus wirst du ab dem Umsatz, mit dem du die Grenze reißt, steuerpflichtig. Die Grenze gilt seit 2025 und war davor 35.000 € netto.</p>
<p>Verrechnest du Umsatzsteuer, musst du sie in der Umsatzsteuervoranmeldung an das Finanzamt abführen, je nach Umsatz monatlich oder vierteljährlich. Das Geld auf dem Konto gehört also zum Teil nicht dir. Ein eigenes Unterkonto oder Sparziel für die Umsatzsteuer verhindert, dass es ausgegeben wird. Zum Umrechnen zwischen netto und brutto hilft der <a href="{P}at/rechner/mehrwertsteuer/">Mehrwertsteuerrechner</a>.</p></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>Kontoführung, Gratis-Bedingungen und IBAN: Entgeltinformationen der Banken, verlinkt auf jeder Kontoseite. Die Werte werden beim Bauen dieser Seite aus den Kontodaten übernommen.</li>
<li>Kleinunternehmerregelung: WKO, {_ext(WKO_KU,"Pauschalierung für Kleinunternehmer")} und {_ext(WKO_KU2,"Was ändert sich 2025 bei der Kleinunternehmerregelung")}; Gewinnermittlung: {_ext(WKO_GEWINN,"WKO, Gewinnermittlung: Methoden im Vergleich")}, {ABGERUFEN}.</li>
<li>Aufbewahrungspflicht: {_ext(USP_AUFBEW,"Unternehmensserviceportal, Aufbewahrungspflicht (§ 132 BAO)")}, {ABGERUFEN}.</li></ul></div>'''),
      ],
      faq=[
       ('Muss ich als Einzelunternehmer ein Geschäftskonto haben?','Nein, eine gesetzliche Pflicht gibt es für Einzelunternehmen und freie Berufe nicht. Eine GmbH braucht ein Konto auf ihren Namen. Die Bank kann die geschäftliche Nutzung eines Privatkontos aber in ihren Bedingungen ausschließen.'),
       ('Darf ich mein Privatkonto für mein Unternehmen nutzen?','Nur wenn die Bank das erlaubt. Viele Geschäftsbedingungen beschränken das Privatkonto auf private Zwecke. Frag schriftlich nach, bevor Kundenzahlungen darauf eingehen.'),
       ('Welches Konto im Vergleich passt für Selbstständige?','Kostenlose Konten ohne Gehaltsbedingung, etwa von Online-Banken, oder ein zweites Privatkonto mit Pauschalpreis. Gehaltskonten setzen oft unselbstständige Arbeit voraus, dann gilt die Gratis-Bedingung nicht.'),
       ('Wie lange muss ich Kontoauszüge und Belege aufheben?','Sieben Jahre ab Ende des Kalenderjahres, auch elektronisch (§ 132 BAO). Bei Grundstücken länger.'),
       ('Ab wann muss ich Umsatzsteuer verrechnen?','Ab 55.000 € Umsatz brutto im Jahr. Eine Überschreitung um höchstens 10 % im laufenden Jahr ist einmal erlaubt. Darunter bist du Kleinunternehmer ohne Umsatzsteuer und ohne Vorsteuerabzug.'),
      ],
      related=['kontoueberziehung','gemeinschaftskonto','kostenloses-girokonto','girokonto-wechseln','basiskonto'])
