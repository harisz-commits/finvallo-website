# Konkurrenzanalyse Girokonto Österreich - für finvallo.com

Stand der Erhebung: 21.10.2026. Angesehen wurden Startseiten, Ergebnislisten, Produkt- und Detailseiten, Unterseiten, FAQ, Methodik-PDFs und, wo nötig, die Daten bzw. JS-Konfiguration hinter den Rechnern. Rohdaten liegen unter `/tmp/claude-0/-home-user-finvallo-website/3c6f7d7e-62ca-517b-a336-7f6d5fd41c59/scratchpad/giro/raw/`.

**Einschränkungen:** durchblicker.at und finanz.at blocken direkte Abrufe per Cloudflare (403). Gelesen wurden sie über einen Render-Proxy (gerenderte Seite und JS-Datei). Der Tab „Tarifdetails“ mit den Teilnoten bei durchblicker wird erst beim Klick nachgeladen und war so nicht abrufbar. Die Teilnoten-Namen stammen deshalb aus deinem Briefing, die Gesamtnoten habe ich selbst gesehen. Bei CHECK24 liefert `girokonto.fin.check24.at` (ohne Pfad) einen 404-Fehler. Der Rechner läuft unter `/start`, die Daten kamen direkt über seine Frontend-API (`/frontend/GIRO/filterbar`, `/frontend/GIRO/product/filtered`, `/frontend/GIRO/product/{id}`).

---

## 0. Kurzfazit (TL;DR)

| | AK Bankenrechner | durchblicker | Capitalo | CHECK24.at | finanz.at |
|---|---|---|---|---|---|
| Rechner | Ja, 4 feste Warenkörbe + eigenes Profil (18 Felder) | Ja, 3 Nutzertypen × Kontoart × Online/Filiale, Geldeingang, Tiefststand | Nur Monatskosten aus Gebühr + Bankomat + Fremdwährung | Nur Geldeingang, Gemeinschaftskonto, Studentenkonto | **Kein Rechner** |
| Ranking nach | Jährliche Kontokosten (gesetzlich) | Ertrag/Kosten pro Jahr (inkl. Zinsen und Bonus im 1. Jahr) | „Empfehlung“ (Anzeige-Plätze oben) | Niedrigste Kontogebühr | - |
| Bewertung | keine | Produktnote 1,0-5,0 (Schulnote) | Capitalo Score in Punkten (130/140/150) → Sterne | Note 1-10 („Exzellent“) | - |
| Produkte | 79 (Gehaltskonto, Normal) | 42 Angebote, 19 Anbieter | 32 | 24 | - |
| Stärke | amtlich, vollständige Spesen, Filial- und Service-Daten | beste Gesamtrechnung, Ertrag statt nur Kosten | Methodik offengelegt, viel Content, E-E-A-T | Teilnoten mit Begründung, saubere Filter | - |
| Schwäche | Bedienung von 2004, keine Bewertung, keine Bonus- oder Karten-Logik, kein SEO | Methodik der Note nicht offengelegt, alter Blog | Fehlerhafte und widersprüchliche Daten, DE-Kriterien, Kostenrechnung zu simpel | Sichtbar falsche Gebühren, Tippfehler | veraltet (Hello bank, PayLife, „ab 2016“), Basiskonto-Deckel 80 € |

**Größte Lücke im Markt:** Niemand verbindet die amtliche AK-Logik („jährliche Kontokosten“ nach VZKG, mit transparentem Warenkorb) mit einer offengelegten Bewertung, einer Rechnung, die Bonus und Zinsen ehrlich einbezieht, und sauberen, geprüften Daten. Capitalo und CHECK24 haben jeweils sichtbare Datenfehler. durchblicker rechnet gut, legt aber nichts offen. Das ist genau finvallos Positionierung (unabhängige Sternebewertung + „Persönlich rechnen“).

---

## 1. AK Bankenrechner (www.bankenrechner.at/girokonto)

### 1.1 Rechtlicher Status (wichtig für unsere Texte)
- Laut **VZKG §§ 10-13** betreibt die Bundesarbeitskammer die **gesetzliche Vergleichswebsite** für Zahlungskonten. Die Seite selbst schreibt: „als einzige österreichische Vergleichswebsite für Girokonten festgelegt“. Einen Bankenrechner gibt es seit 2004.
- **§ 2 Z 28 VZKG** definiert die „jährlichen Kontokosten“ als *Summe aller Entgelte, die jährlich für die Nutzung der repräsentativsten mit einem Zahlungskonto verbundenen Dienste **ohne Berücksichtigung von Soll- und Habenzinsen** anfällt, wenn von bestimmten Annahmen über das Nutzungsverhalten ausgegangen wird*.
- **§ 11 VZKG** schreibt vor:
  - einen Rechner mit standardisierten Voreinstellungen zu Diensten, Nutzungsumfang und Verrechnungsart
  - eine Reihung nach den jährlichen Kontokosten
  - in der Ergebnisliste zusätzlich Sollzins und Habenzins (jeweils fix/variabel) sowie einen Link zur Entgeltinformation (§ 6 Abs. 5)
  - Links zu Filialen mit betreutem Schalter (Anzahl, Standorte, Öffnungszeiten), zu SB-Foyers und Automaten und zu den Fernkommunikationsmitteln mit Zeiten
  - Gleichbehandlung aller Banken und die Möglichkeit, auf ein Bundesland und/oder Basiskonten einzuschränken
  - offengelegte objektive Kriterien und die standardisierten Begriffe
  - eine Meldefunktion für falsche Daten (§ 11 Abs. 8-9)
- Die Banken melden ihre Daten selbst per Formular (§ 12). Die Teilnahme ist freiwillig. Die AK schreibt selbst: „kein vollständiger Marktüberblick“.
- **Standardisierte Begriffe**: Die FMA legt sie in der **Verbraucherzahlungskonto-Diensteverordnung (VZKDV, BGBl. II 60/2018)** fest. Es sind 13 Dienste:
  1. Kontoführung
  2. Internetbanking
  3. Anlassbezogener Kontoauszug
  4. Überweisung
  5. Gutschrift
  6. Dauerauftrag
  7. Lastschrift
  8. Information über Nicht-Durchführung
  9. Bereitstellung einer Debitkarte
  10. Bargeldeinzahlung
  11. Bargeldbehebung
  12. Eingeräumte Kontoüberziehung
  13. Überschreitung des Überziehungsrahmens

  Banken müssen diese Begriffe verwenden (§ 9 VZKG). **Diese Begriffe sollten wir für unsere Datenfelder und Labels übernehmen.**

### 1.2 Eingabefelder (vollständig)
Das Formular `girokonten1000` wird per POST an `/girokonto` geschickt:

| Feld (name) | Optionen |
|---|---|
| Kontotyp* (`opt_kategorie`) | Gehaltskonto (10), Basiskonto mit grundlegenden Funktionen (max. 83,45 Euro/Jahr) (60), Jugendkonto (50), Studentenkonto (40), Pensionskonto (30), Privatgirokonto (20) |
| Ich bin (Nutzertyp)* (`opt_nutzer`) | Normalnutzer (280 Buchungen/Jahr), Wenignutzer (160), Intensivnutzer (400), Onlinenutzer (350). Alternativ „Mein Nutzerprofil - Jetzt erstellen“ |
| Verrechnung nach (`opt_verrechnung`) | Pauschalpreisen, Einzelpreisen, Mischform, keine Einschränkung |
| Kreditkarte (`opt_kreditkarte_erw`) | nein / ja, ohne Versicherungsschutz / ja, mit Versicherungsschutz |
| Bundesland (`opt_bankstandort`) | 9 Bundesländer oder keine Einschränkung |
| versteckt | `opt_ueberziehen=-1`, `opt_sort` (0 = Kosten, 1 = Sollzins, 2 = Habenzins) |

Bei Kontotyp „Basiskonto“ blendet ein JS-Aufruf (`BasisKonto()`) die Felder Verrechnung und Kreditkarte aus.

**Eigenes Nutzerprofil (`/girokontoNutzer`)**: 18 Pflichtfelder für die Anzahl pro Jahr.
- Gutschriften
- Bargeldeinzahlung am Automaten
- Überweisungen automatisiert
- Überweisungen manuell
- Bargeldbehebung am Schalter
- Bargeldbehebung am Automat/Bankomat
- Bezahlung mit Debitkarte im Euro-Raum
- Dauerauftrag-Durchführungen
- Lastschrift-Durchführungen
- Anlassbezogene Kontoauszüge (1 pro Monat inkludiert)
- Nichtdurchführung mangels Deckung
- Debitkarte(n)
- Dauerauftrag Eröffnung, Änderung und Schließung, jeweils am Schalter und online (6 Felder)

Optional kann man eine E-Mail angeben und bekommt dann einen Link mit anonymem Code zum Wiederladen. Als Hilfe empfiehlt die AK, die Kontoauszüge der letzten 12 Monate zur Hand zu nehmen.

### 1.3 Offizielle AK-Nutzertypen = Musterwerte (PDF „Giro_Nutzermodelle_2018.pdf“)
Die jährlichen Kontokosten beruhen auf „vier fixen Modellannahmen … als ‚Warenkörbe‘“. **Das sind die einzigen offiziellen Musterwerte in Österreich**, Stand 2018 und seither unverändert verlinkt.

| Transaktionen pro Jahr | Wenig | Normal | Viel (im Formular „Intensiv“) | Online |
|---|---:|---:|---:|---:|
| Gutschriften | 17 | 28 | 30 | 24 |
| Bargeldeinzahlung am Automaten (Eigenerlag) | 1 | 2 | 4 | 2 |
| Überweisungen automatisiert | 6 | 24 | 36 | 40 |
| Überweisungen manuell | 8 | 12 | 12 | 0 |
| Bargeldbehebung am Schalter/Kassa | 12 | 6 | 6 | 0 |
| Bargeldbehebung am Bankomaten (Euro-Raum) | 24 | 50 | 80 | 50 |
| Bankomatkassenzahlung POS (Euro-Raum) | 40 | 74 | 116 | 108 |
| Dauerauftrag - Durchführung | 12 | 24 | 36 | 20 |
| Lastschrift - Durchführung | 40 | 60 | 80 | 106 |
| **Summe Transaktionen/Jahr** | **160** | **280** | **400** | **350** |
| ≈ pro Monat | 13-14 | 23-24 | 33-34 | 29-30 |
| *Sonstige Dienste/Jahr:* | | | | |
| Bereitstellung Debitkarte | 1 | 1 | 1 | 1 |
| Kontoauszugsduplikat (6 Monate zurück) | 0 | 1 | 1 | 0 |
| Nichtdurchführung mangels Deckung | 0 | 0 | 1 | 1 |
| Dauerauftrag Eröffnung (Schalter / online) | 1 / 0 | 2 / 0 | 3 / 0 | 0 / 1 |
| Dauerauftrag Änderung (Schalter / online) | 1 / 0 | 2 / 0 | 3 / 0 | 0 / 1 |
| Dauerauftrag Schließung (Schalter / online) | 1 / 0 | 2 / 0 | 3 / 0 | 0 / 1 |

Daraus folgen:
- Überweisungen gesamt: 14 / 36 / 48 / 40
- Abhebungen gesamt (Schalter + Automat): 36 / 56 / 86 / 50

**Formel (laut AK):** Kontoführung pro Jahr + Spesen der Transaktionen + Debitkarte (Jahresgebühr) + Zusatzspesen (Duplikat, Dauerauftragseröffnung usw.) = „Jährliche Kontokosten“. Wenn eine Kreditkarte gewünscht ist, kommen deren Kosten dazu und das Ergebnis heißt „Jährliche Kosten Konto + Kreditkarte“. **Zinsen, Bonus und Neukundenaktionen fließen nicht ein.**

**Pauschalkonto (AK-Definition):** Internetbanking, Überweisungen, alle Gutschriften, Daueraufträge, Lastschriften, eine Debitkarte, Bareinzahlungen und Barbehebungen (auch in der Filiale) sind in der Kontoführung enthalten. Beim Einzelpreiskonto kostet jede Buchung extra (7 Cent bis mehrere Euro). Mischform heißt zum Beispiel: Die Pauschale deckt nur elektronische Buchungen. AK-Faustregel: Je intensiver man das Konto nutzt, desto eher lohnt sich die Pauschale.

**Reihung bei gleichen Kosten** (FAQ und Ergebnisseite):
1. Jährliche Kontokosten
2. Sollzinsen (niedriger zuerst)
3. Kreditkarte(n) mit oder ohne Versicherung im Paket inkludiert
4. Habenzinsen
5. Alphabet

Zum Vergleich der zweite Musterwert-Satz am Markt, die **durchblicker-Profile** (Abschnitt 2.3). Er weicht ab und unterscheidet nach Kontoart.

### 1.4 Kontoarten-Definitionen (FAQ-PDF)
- Gehaltskonto: setzt regelmäßige Gehaltseingänge voraus.
- Privatgirokonto: ohne regelmäßige Eingänge, teils mit monatlichem Mindesteingang.
- Studentenkonto: Inskriptionsbestätigung, meist bis 27.
- Jugendkonto: Schüler und Lehrlinge, meist bis 19, danach automatische Umstellung.
- Pensionskonto: regelmäßige Pension.
- Basiskonto („Zahlungskonto mit grundlegenden Funktionen“): Jede Bank muss es anbieten, keine Überziehung, gesetzlicher Kostendeckel. **Im Formular steht 83,45 €/Jahr (§ 26 VZKG, indexiert), für besonders Schutzbedürftige 41,73 €. Das FAQ-PDF nennt noch die veralteten Werte 80 € und 40 €.** Die Konten für Schutzbedürftige zeigt der Rechner nicht.

### 1.5 Ergebnisliste
Spalten: Produktname, Bankinstitut, Sollzinsen (% + fix/variabel), Habenzinsen (% + fix/variabel), Jährliche Kontokosten. Ein Kreditkarten-Icon markiert eine inkludierte Karte mit Namen, zum Beispiel „R-CardService Kreditkarte Platinum … in den jährlichen Kontokosten enthalten“. Dazu „Mehr Infos“, „Stand: Oktober 2026“ und ein PDF-Download.
- Sortierbar per Klick auf die Spalten Sollzinsen, Habenzinsen und Kontokosten.
- Beispiel Gehaltskonto/Normalnutzer/keine Einschränkung: **79 Produkte**. Platz 1 und 2 haben 0,00 € (DADAT Gratis Gehaltskonto ab 1.000 €/Monat, Wüstenrot ZERO), es folgen bank99 aktivkonto99 bildung/jugend mit 3,74 € und Anadi mit 12,43 €. Das teuerste ist Raiffeisen Online Konto Kärnten mit 509,89 €.
- Hinweistexte unter der Liste: Basiskonto-Deckel, Reihungsmethode, Legende.

### 1.6 Detailseite (`/girokontoDetail?idgirokonto=…`)
- **Bank:** Adresse, Telefon/Fax, E-Mail und Web, Beschreibung der Bank
- **Service-Informationen zur Bank:** Filialen mit betreutem Schalter (Anzahl + Link zum Filialfinder), Selbstbedienungsfoyers, Kontakt per Fernkommunikation mit Zeiten, Link zum Zahlungsverkehrs-Glossarium der Bank, **Link zur Entgeltinformation** des Kontomodells
- **Produkt:**
  - Name/Bedingung, Art der Verrechnung, jährliche Kontokosten für das gewählte Modell
  - Sollzins mit Art und **vollständiger Zinsgleitklausel** (z. B. 3-Monats-Euribor + 6,9 PP, Rundung auf 0,125, Stichtage)
  - Sollzins außerhalb des Kontorahmens, Habenzins mit Art
- **Wichtige Kosten im Detail, die eingerechnet sind:**
  - Kontoführung pro Quartal, ohne und mit Überziehung
  - inkludierte Leistungen
  - Debitkarte pro Jahr, Kreditkarte pro Jahr bzw. Zusatzkosten für Kreditkarten (z. B. Visa Classic 21,60 €, Visa Gold mit Versicherung 80,40 €)
  - Dauerauftrag Änderung und Löschung (Schalter/online)
  - Sonstige Spesen: Bareinzahlung auf ein institutsfremdes Konto, Lastschrift-Nichtdurchführung (6,41 €), Kontoauszugsduplikat
- „Letzte Aktualisierung: 08.04.2026 10:06“ je Produkt

### 1.7 Bewertungssystem
Keines. Die Seite rankt nur nach Kosten.

### 1.8 Vertrauen und SEO
- Title: „Girokonten im Test - Bankenrechner der Arbeiterkammern“
- Meta-Description: „Girokonten im Test - Die besten Konditionen im Land“
- H1: „Girokonto - die besten Konditionen“
- Untertitel: „Offizielle österreichische Vergleichswebsite“
- Vertrauen entsteht über den Absender BAK, den Gesetzesbezug und das Fehlen jeglicher Werbung.
- **Keine Unterseiten** (Gratis-, Studenten-, ohne-Gehaltseingang-Seiten usw.), **kein Ratgeber**, nur 2 PDFs (Info-Nutzertypen, FAQ). Die Ergebnisse liegen hinter einem POST und sind damit nicht indexierbar.

### 1.9 Gut gemacht
- Rechtssichere, objektive Kennzahl
- Vollständige Spesen inklusive Schalter, Duplikat und Daueraufträge
- Eigenes Nutzerprofil
- Filial- und Service-Informationen
- Zinsgleitklausel im Wortlaut
- Aktualisierungsdatum je Produkt
- Bundesland-Filter

### 1.10 Lücken
- UX aus den 2000ern, Popup-PDFs, mobil schwach
- Keine Erklärung im Ergebnis, warum ein Konto teurer ist (keine Kostenaufschlüsselung pro Posten in der Liste)
- Bedingungen wie Mindesteingang stehen nur im Produktnamen; man kann den eigenen Gehaltseingang nicht eingeben, also bleibt offen, ob ich die Gratis-Bedingung erfülle
- Kein Bonus, kein Habenzins-Ertrag (gesetzlich bewusst ausgeschlossen), keine Neobanken (N26, Revolut, Trade Republic fehlen, weil die Teilnahme freiwillig ist und Auslandsbanken nicht melden)
- Kein Kartenvergleich, kein Fremdwährungs- oder Auslandsszenario, keine Apple-/Google-Pay-Info
- Inkonsistenz: Formular sagt „Intensivnutzer“, PDF sagt „Vielnutzer“; FAQ nennt 80 €, Formular 83,45 €; Nutzermodelle von 2018
- Keine Bewertung oder Qualitätsaussage

---

## 2. durchblicker.at (durchblicker.at/girokonto)

### 2.1 SEO und Seitenstruktur
- `/girokonto`
  - Title: „Girokonto & Bankkonto Vergleich Österreich | durchblicker.at“
  - Hero: „In 5 Minuten online Konto eröffnen und dabei bis zu 200 Euro sparen“
  - Kontotyp-Teaser (angestellt …), Siegel „Branchensieger finanzen“ (ÖGVS)
  - H3: „Bestes Girokonto August 2026“ (im Oktober noch nicht aktualisiert)
  - „19 sorgfältig ausgewählte Anbieter“, Experte mit Foto: Manuel Wukovits
- Inhaltsverzeichnis:
  - Bankkonto eröffnen oder Kontowechsel
  - Girokonto einfach erklärt
  - Unterschied Gehaltskonto vs. Privatkonto (mit Tabelle)
  - Was ist bei der Auswahl zu beachten (Anzahl Kreditkarten, Überziehungsrahmen, Online- vs. Filialbank, Kontoführungsgebühren)
  - Das kostenlose Gehaltskonto
  - Service für den Kontowechsel
  - SEPA-Echtzeitüberweisungen (9.1.2025 empfangen, 9.10.2025 ohne Aufpreis senden, Empfängerüberprüfung, ab 2027 weitere Währungen)
  - „So funktioniert's“ in 4 Schritten (Kontotyp → Banken vergleichen → Konto eröffnen → Sparen „bis zu 250 Euro“; im selben Text stehen also 200 und 250 €)
- FAQ auf `/girokonto` (ohne Fragetitel, nur Absätze): Kontowechsel nach VZKG; Weiterleitung zur Bank und Gehaltsbescheinigung; Konten 2 Monate parallel laufen lassen, Kündigung per E-Mail, Brief oder Filiale. Dazu „durchblicker-Tipp“, Blog-News, „Tipps zum Girokonto“ und „Unsere Mission“ (größtes Tarifvergleichsportal, Fixkosten-Experte).
- Unterseiten:
  - `/gratis-konto`: „Online Konto - Gratis Konto Vergleich Österreich“, H1 „Der Gratis Konto-Vergleich für Österreich“, Tabelle mit Auswahlkriterien (Kontoführung, Überziehungszinsen, Habenzinsen, Bankomatkarte, Kreditkarte, Durchschnittssaldo), FAQ: „Wie finde ich das optimale online Konto?“, „Was kostet ein online Konto?“
  - `/studentenkonto`: Title „ᐅ Österreichs Studentenkonto Vergleich **2025**“ (veraltet)
  - `/jugendkonto`: „ツ Jugendkonto Vergleich Österreich 2026“, FAQ z. B. „Wie lange kann man ein Jugendkonto nutzen?“
  - `/konto`, `/gratis-kreditkarte`, `/kreditkarte`
  - Anbieterseiten `/anbieter/girokonto/{bank}` für 22 Banken: austriananadi, bank99, bankaustria, bankdirekt, bawagpsk, dadat, denizbank, dkb, easybank, erstebank, number26, revolut, rlbnoewien, rlbstmk, spardabank, sparkasseooe, spkpottenstein, tomorrow, volksbankwien, wuestenrotbank u. a. Sie enthalten Kurztext, „Jetzt Preise einholen“, Kontakt und Blog-Teaser.
  - Blog-Kategorie `/b/girokonto` mit Beiträgen von 2021, 2023 und 2025, z. B. „Alles rund ums Girokonto: Kosten, Gebühren und Kündigung“, „Kostenfallen vermeiden: Bezahlen & Geldabheben im Ausland“, „Bezahlen im Urlaub: Bargeld, Kreditkarte oder Bankomatkarte?“
  - **Keine eigene Seite** „Konto ohne Gehaltseingang“, „Basiskonto“, „Pensionskonto“, „Gemeinschaftskonto“

### 2.2 Rechner (Ergebnisseite `/girokonto/vergleich/ergebnis`)
Eingaben (aus `variator.js`, vollständig):

| Feld | Werte / Default |
|---|---|
| Kontoart | Privatkonto, Gehaltskonto (`angestellt`, Default), Pensionskonto, Studentenkonto, Schüler-/Jugendkonto |
| Nachhaltiges Konto | Schalter (Default aus) |
| Nutzertyp | Wenig / **Normal** / Intensiv + Link „Nutzertyp Details“ (PDF) |
| Geldeingang pro Monat | Slider 0-5.000 € (Raster 0/500/2.000/3.500/5.000), Default **1.500 €**, mit exakter Eingabe |
| Tiefststand pro Monat | Slider -5.000 bis +5.000 €, Default **0 €** |
| Kontonutzung | Online / Online & Filiale / Filiale (Default Online) |
| Karten | 2. Bankomatkarte (Schalter), Kreditkarte (Schalter) → Kreditkartenart Normal/Gold, 2. Kreditkarte (Schalter) |
| Ergebnis | Toggle „Inklusive Bonus im 1. Jahr“ |

Zusätzlich auf der Ergebnisseite:
- Filter, Anbieterfilter („Alle anzeigen“)
- „Details vergleichen“ (Gegenüberstellung `/ergebnis/gegenueberstellung`)
- „Vergleich senden“ per E-Mail
- „Erinnerung setzen“ (fixer Termin oder regelmäßig: monatlich, vierteljährlich, jährlich) mit Newsletter-Opt-in
- Kostenlose Telefonberatung 01/30 60 900 40 (Mo-Do 8-16:30, Fr 8-14)

### 2.3 Berechnungslogik
Aus dem FAQ-Tooltip „Warum unterscheiden sich die Ergebnisse von anderen Internet-Rechnern?“: Aus Geldeingang und Tiefststand wird *ein theoretischer Haben- bzw. Sollzinswert* berechnet, aus dem Nutzertyp *die Transaktionsgebühren* und dazu *ein Erstjahrespreis inklusive Neukundenrabatten*.
→ **„Ertrag / Kosten pro Jahr“** = Habenzinsen - Sollzinsen - Kontoführung - Transaktionen - Karten + (optional) Bonus bzw. Rabatt im 1. Jahr. Positive Werte bedeuten Ertrag („+ 8,44 €“), negative Kosten („- 780,00 €“).

Rückgerechnet: Bei 1.500 € Eingang und Tiefststand 0 nimmt durchblicker einen **Durchschnittssaldo von etwa 280-300 €** an:
- Trade Republic: 3,0 % → +8,44 €
- 0,01 % → +0,03 €
- s Kompakt: 46,68 € Gebühr - 0,06 € Zins = -46,62 €

Mit negativem Tiefststand entstehen Sollzinsen auf den Dispo.

**Nutzerprofile von durchblicker** („Nutzertyp_Information.pdf“). Sie sind kleiner als die der AK und nach Kontoart getrennt:

| Gehaltskonto (pro Jahr) | Wenig | Normal | Viel |
|---|---:|---:|---:|
| Gutschriften automatisiert/beleglos (inkl. Gehalt) | 19 | 26 | 34 |
| Bareinzahlung Automat | 1 | 1 | 1 |
| Gutschriften manuell/beleghaft (inkl. Schalter-Einzahlung) | 1 | 2 | 2 |
| Überweisungen automatisiert/beleglos | 6 | 15 | 25 |
| Überweisungen am Automaten | 8 | 12 | 12 |
| Überweisungen manuell/beleghaft | 2 | 3 | 3 |
| Barauszahlung Schalter | 3 | 2 | 1 |
| Bankomatauszahlung Euro-Raum | 25 | 45 | 62 |
| Bankomatkassenzahlung Euro-Raum | 18 | 50 | 115 |
| Dauerauftragsdurchführung | 4 | 8 | 12 |
| Lastschriftdurchführung | 34 | 69 | 99 |
| **Summe (≈/Monat)** | **121 (~10)** | **233 (~19)** | **366 (~31)** |

- Pensionskonto: 63 / 124 / 216
- Sonstige (Privat, Schüler, Student): 43 / 111 / 241

Zusätzlich gibt es Modifikationen für „nur Online-Banking“, „nur Filiale“ und „Anbieter hat keine Filialen“. Hinterlegt sind Einzelpreise pro Transaktion. durchblicker sagt selbst, das Ergebnis sei ein „Näherungswert“.

### 2.4 Ergebnisliste
- Kopf: „42 Angebote von € 8 bis € -780“; Hinweis zur Marktabdeckung („Eine 100%-ige Abdeckung … nicht garantieren“)
- Pro Zeile:
  - Logo, Produktname
  - „x % Habenzinsen, y % Überziehungszinsen“
  - Kontoführung („Gratis Kontoführung“ bzw. „2,58 € / Monat“)
  - Bedingungen („Monatlicher Gehaltseingang von mindestens € 1.000 erforderlich“, „Für alle unter 28“)
  - Besonderheiten (Deutsche/Litauische IBAN, „Smartphone erforderlich“, „Physische Bankkarte nur gegen Aufpreis“, „Nachhaltiges Konto“, „Zertifiziert mit dem österreichischen Umweltzeichen“, „inkl. Reiseversicherung“, „€ 100 Kontowechselbonus“, „€ 40 Cash-Bonus“)
  - Ertrag/Kosten, „zum Anbieter“, „Tarifdetails“ (Tab)
  - **Produktnote** (z. B. 1,7 „Ausgezeichnet“, 2,2 „Sehr Gut“)
- Sortierung standardmäßig nach Ertrag/Kosten (bestes zuerst). Trade Republic steht trotz 2,2 auf Platz 1.

### 2.5 Bewertungssystem „durchblicker Produktnote“
- Schulnotenskala (1,0 = bestes). Beobachtet: 1,2-2,5. Verbale Stufen: Ausgezeichnet (≤ ca. 1,9), Sehr Gut (2,0-2,5).
- Text: „unabhängige Leistungsbewertung … durch die durchblicker Finanz-Experten auf Basis der Produkt-Konditionen“.
- Teilnoten im Tarif-Tab (laut Briefing): Allgemeine Bedingungen, Konditionen, Karten, Einlagensicherung, Gebühren Online/Automat/Schalter.
- **Gewichtung und Kriterien nicht öffentlich**, keine Methodik-Seite.
- Auffällig: Teure Filial-Pakete bekommen Top-Noten (Relax-Konto 1,2, topkonto99 1,2, Bonus-Konto Premium 1,2), Neobanken nur 2,4-2,5. Die Note misst offenbar Leistungsumfang und nicht Preis/Leistung.

### 2.6 Vertrauen
- eKomi 4,5 mit 10.827 Bewertungen
- „Ihre Daten sind bei uns sicher“
- Siegel ÖGVS „Branchensieger finanzen“, „Bekannt aus“
- Experte mit Foto, Telefonberatung, App
- Mission: „Unabhängig & transparent, breiter Marktvergleich“

### 2.7 Gut gemacht
- Die realistischste Rechnung am Markt: Zinsen auf Basis von Geldeingang und Tiefststand, Nutzertyp × Online/Filiale, Erstjahr mit Bonus als Schalter
- Neobanken mit Hinweisen zu IBAN-Land und Smartphone-Pflicht
- Erinnerungsfunktion, Vergleich per E-Mail, Gegenüberstellung
- Nachhaltigkeits-Filter

### 2.8 Lücken
- Produktnote ohne offengelegte Methodik
- Nutzerprofile weichen von der AK ab, ohne dass das transparent gemacht wird
- Datierung inkonsistent: „Bestes Girokonto August 2026“ im Oktober, Studentenkonto „2025“
- Blog teils von 2021
- Keine Unterseiten zu „ohne Gehaltseingang“, Basiskonto, Pensionskonto, Gemeinschaftskonto
- Keine Kriterien zu Fremdwährung, Ausland oder Apple Pay im Rechner
- Ergebnis nur clientseitig gerendert, wenig indexierbarer Content
- Kosten nicht nach Posten aufgeschlüsselt (Kontoführung vs. Transaktionen vs. Karte)
- Kein Hinweis auf die AK-Methode und keine Kennzahl „jährliche Kontokosten“ nach VZKG

---

## 3. Capitalo (www.capitalo.at/girokonto)

### 3.1 SEO
- `/girokonto`
  - Title: „Girokonto Vergleich Österreich 10/2026: Beste Konten im Test | Capitalo“
  - H1: „Girokonto Vergleich Österreich **10/2026**: Ab 0 EUR“
  - Intro: „Welches Girokonto ist in Österreich wirklich kostenlos? Vergleiche Erste Bank, Raiffeisen, N26, Easybank, Bank99 …“
  - Badges: „Kontoführung ab 0 EUR/Monat“, „Aktualisiert 10/2026“, „Registrierung nötig: Nein“, „Vor 5 Tagen aktualisiert, Stand: 15. Oktober 2026“, „Anzeige“
- Unterseiten:
  - `/girokonto/gratis`: „Gratis Konto Österreich 10/2026: Vergleich & Test“, H1 „Gratis Konto Österreich: Die besten kostenlosen Girokonten 10/2026“
  - `/girokonto/kostenlos`: „Kostenloses Girokonto: Gratis-Konten im Vergleich“, H1 „Kostenloses Girokonto Österreich: 0 EUR Kontoführung im Vergleich“ (**Keyword-Kannibalisierung mit /gratis**)
  - `/girokonto/gebuehren`: „Kontoführungsgebühren Vergleich Österreich 10/2026“. Meta nennt „34 Girokonten“, der Vergleich zeigt 32.
  - `/girokonto/gemeinschaftskonto`: „Gemeinschaftskonto Österreich: Vergleich 10/2026“, Und-/Oder-Konto, Haftung, Pfändung, Trennung, Todesfall
  - `/girokonto/ratgeber`:
    - „Gratis Konto ohne Gehaltseingang in Österreich 2026“ (`/girokonto/ratgeber/girokonto-ohne-gehaltseingang`)
    - „Beste Bank Österreich“
    - „Was ist ein Girokonto? - Definition, Funktionen & Kontoarten in Österreich“
    - „Konto wechseln in Österreich: Schritt-für-Schritt-Anleitung 2026“
    - „Konto eröffnen in Österreich: Anleitung, Unterlagen & Kosten 2026“
  - Produktseiten `/anbieter/{bank}/produkte/{produkt}`, Title-Muster „{Produkt} im Test 2026: Gebühren & Erfahrungen | Capitalo“
- Kein Studentenkonto, Jugendkonto, Pensionskonto oder Basiskonto als eigene Seite. Jugendkonten haben laut Methodik eine eigene Rubrik mit max. 100 Punkten.

### 3.2 Rechner, Filter und Sortierung (aus dem JS-Bundle)
- Rechner-State mit Defaults aus der Config:
  - `monthlyIncome` 1.500 €
  - `cashWithdrawalsPerMonth` 4 (Config; Code-Fallback 3)
  - `avgWithdrawalAmount` 100 €
  - `foreignTransactionsPerMonth` 0
  - `avgForeignTransactionAmount` 50 €

  In der UI sind das die Slider Geldeingang, Abhebungen, Betrag pro Abhebung und Auslandszahlungen (Anzahl und Betrag).
- Filter, 3 Gruppen:
  - Kosten: **Kostenlos 💚, Bedingt kostenlos 💛, Mit Bonus 🎁**
  - Karten: **Girocard gratis 💳, Kreditkarte gratis 💎**
  - Features: **Apple Pay, Google Pay, Dispo verfügbar, Mit Guthabenzins**
- Freitextsuche „Girokonto suchen…“
- Sortierung: **Empfehlung** (Default), Kosten (niedrigste), Kosten (höchste), Bonus (höchster), Bewertung (beste), Name (A-Z)
- „Zum 1:1-Vergleich hinzufügen“ (2 Konten); 12 von 32 werden zunächst angezeigt
- **Kostenformel (Monat):**
  - Kontoführung: entfällt, wenn der Geldeingang mindestens der Schwelle entspricht. Die Schwelle wird **per Regex aus dem Freitext** der Gratis-Bedingung gelesen („ab X EUR“, „mind. X €“ …).
  - plus Bankomatgebühren Inland: über das Freikontingent hinaus `max(% × Betrag, Mindestgebühr)` oder Fixgebühr. Bei Mindestabhebebetrag (Trade Republic 100 €) gibt es Gebühr oder „nicht möglich“.
  - plus Fremdwährungsgebühr % × (Anzahl × Betrag)
  - **Nicht eingerechnet:** Überweisungen, Buchungen, Karten-Jahresgebühr, Zinsen, Bonus. Der Willkommensbonus wird getrennt angezeigt („Willkommensbonus + 80,00 €“).
  - Ist eine Komponente unbekannt, steht „Angaben unvollständig“. Freikontingente pro Quartal werden „nicht auf den Monat umgerechnet“.

### 3.3 Ergebnisliste (Karte je Konto)
- Name, Bank, Score (z. B. „3,1 Befriedigend“), Kontoführung, Badges (Mobile App, „Dispo 12,50 %“, „Bargeld kostenlos“), Rang, „Empfehlung“/„Anzeige“
- **Monatliche Kosten** mit Zusatz „Ohne Geldeingang: 2,99 €/Monat“ und Aufschlüsselung („Kontoführung 0,00 € · 3x Abhebung 1,53 € (1 frei) · Ausland 0,00 €“)
- Gratis-Abhebungen, Bargeld Inland, Fremdwährung
- Vorteils-Chips und „+ x weitere Vorteile“
- Aufklappbar: Gebühren (Kontoführung, Auslandseinsatz), Zinsen (Dispo, Guthabenzins), Bargeld (Inland, Ausland, Gratis-Abhebungen, Mindestbetrag), Legitimation (Foto-/VideoIdent)
- „Zum Anbieter“, „Details ansehen“

### 3.4 Produktseite (Beispiel Anadi Online Girokonto)
- H1 „… im Test 2026: Gebühren & Erfahrungen“
- „Capitalo Score: 3,9/5 Gut“, „Geprüft von Alexander Senger“, Preisbox, „Zum Angebot“
- Gliederung:
  - Überblick (Punkte und Note im Fließtext)
  - Vorteile/Nachteile (je 4 Punkte)
  - Vergleichstabelle mit 3 Wettbewerbern (Kontoführung, Dispo, Score)
  - Für wen eignet sich das Konto (ideal / weniger ideal)
  - So eröffnest du das Konto (3 Schritte)
  - Experten-Einschätzung („Alexander's Take“, Zitat)
  - Konditionen im Überblick (Kontotyp, Gebühren, Karten, Bargeld, Dispo inkl. Rahmen, Digital, Extras, Voraussetzungen)
  - Mini-Vergleich, FAQ mit 10 Fragen (Gebührenfreiheit, Karten, Abheben, Dispo, Guthabenzinsen, Eröffnung, Voraussetzungen, Apple Pay, Bargeld einzahlen, KSV-Prüfung)
  - Score-Box „102 von 130 Punkten (78 %)“, „So bewerten wir“, Anbieterprofil, Erfahrungen

### 3.5 Bewertungssystem „Capitalo Score“
- Rubrik Girokonto: max. **130 Punkte in 7 Kategorien**; Premium-Konten max. 150, Kinder/Jugend max. 100. Sterne = Punkte ÷ Max × 5.
- Notenschwellen (130er-Skala):
  - 117-130 Hervorragend
  - 104-116 Sehr gut
  - 91-103 Gut
  - 78-90 Befriedigend
  - 60-77 Ausreichend
  - 52-59 Mangelhaft
  - < 52 Ungenügend
- Kriterien (max. Punkte):
  - **Zahlungsverkehr 24**: Euro-Ausland per Karte zahlen 5, Fremdwährungsgebühr 6, Mobile Payment 5, SEPA-Überweisungen 4, Echtzeitüberweisung 4
  - **Bargeld 23**: *„Kostenlos Bargeld abheben in **Deutschland**“* 8 (teils „DE/AT“, max. 11), Anzahl Gratis-Abhebungen 5, Euro-Ausland 3, Fremdwährung 4, Bargeld einzahlen 3
  - **Karten 22**: Kartentyp 6, Debitkarte kostenlos 10, echte Kreditkarte 6
  - **Kontoführung 19**: Kosten als Aktivkonto 15, kostenlos ohne Aktivkonto 4
  - **Extras & Angebot 18**: Unterkonten 4, Tagesgeld inkl. 3, Zinsen 2, Dispozins 4, Gemeinschaftskonto 3, Multibanking 2
  - **Sicherheit 12**: Einlagensicherung 6, Ident-Verfahren 3, TAN-Verfahren 3
  - **Service 12**: Kundenservice 6, Kontowechselservice 3, App-Bewertung 3
- Versprechen: transparent, objektiv, aktuell („Konditionen täglich aktualisiert“), rechtlich fundiert. Hinweis: „Erstellt mit KI-Unterstützung, fachlich geprüft und freigegeben von Alexander Senger“ (Gründer).

### 3.6 Weitere Inhalte und FAQ (Hauptseite)
- „Das Wichtigste auf einen Blick“: Bestes Gehaltskonto, bestes Gratis-Konto, Gebührenfalle, Echtzeitüberweisung
- Bestenlisten: Gehaltskonto, Gratis-Konto, Premium-Konto, Direktbank
- „Worauf achten“: Gebühren, Karten, Dispo (Rechenbeispiel 500 € Dispo), Mobile Payment, Bankomat und Abheben
- „Was sich 2025/2026 geändert hat“: Instant Payments, Verification of Payee, Kontowechsel nach VZKG, Basiskonto
- FAQ:
  - Welches ist das beste Girokonto in Österreich?
  - Gibt es wirklich kostenlose Girokonten?
  - Was kostet ein Girokonto durchschnittlich? (zitiert AK-Bankenmonitoring: +62 % seit 2005)
  - Kann ich online eröffnen?
  - Wie funktioniert der Kontowechsel?
  - Was ist das Basiskonto und wer hat Anspruch? (83,45 €, ca. 34.500 eröffnet)
  - Welche Neobanken funktionieren in AT?
  - Wie sicher ist Online-Banking?

### 3.7 Vertrauen
„Geprüft und freigegeben von“ mit Person und Bio, Methodik-Box, Datum „Stand“, Trustpilot-Felder in den Daten, „Anzeige“-Kennzeichnung, DACH-Marke.

### 3.8 Gut gemacht
- Offengelegte Punkte-Methodik
- Sehr viel strukturierter Content, Produktseiten mit Vor-/Nachteilen und Zielgruppen
- „Bedingt kostenlos“ als eigener Filter, „Ohne Geldeingang: x €“ direkt in der Karte
- Mindestabhebebetrag und Freikontingente modelliert
- 1:1-Vergleich, Datum „Stand“ prominent

### 3.9 Schwächen und Fehler (konkret beobachtet)
- **Widersprüchliche Scores:**
  - easybank easy gratis in der Liste „3,1 Befriedigend“, in der Tabelle 103/130 = 4,0 Sterne
  - Sparkasse s Plus Konto „52/130 Mangelhaft“ (bei durchblicker 1,3 Ausgezeichnet)
  - Unterschiedliche Maximalpunkte (110/140, 109/150) in einer Tabelle, nur per Fußnote erklärt
- **Falsche oder widersprüchliche Daten:**
  - N26 Standard: Liste „Dispo 8,90 %, Unbegrenzt abheben“, Text „nur 3 Gratis-Abhebungen, 2 € je weitere“, Rohdaten 13,40 %
  - DADAT Gehaltskonto auf der Anadi-Produktseite mit „4,48 €/Monat“, sonst „0 € ab 1.000 €“
  - Raiffeisen Bonus Smart mit 2,99 € Kontoführung als „Monatliche Kosten 0,00 €“ gelistet, obwohl die Gratis-Bedingung unklar ist
  - Rohwert-Leak „Wohnsitz erforderlich: none“
- **Deutsche Kriterien** im AT-Score („Kostenlos Bargeld abheben in Deutschland“, „Schufa“-Strings im Code)
- Kostenrechnung ohne Buchungs- und Überweisungsentgelte, Kartengebühr, Zinsen oder Bonus, also keine echten Jahreskosten
- Default-Sortierung „Empfehlung“ mit Anzeigen oben; Platz 1 easybank mit Note 3,1
- Kannibalisierung /gratis vs. /kostenlos; „34“ vs. „32“ Konten
- KI-Texte mit Floskeln

---

## 4. CHECK24.at (www.check24.at/girokonto → girokonto.fin.check24.at/start)

### 4.1 SEO und Content
- Title: „Girokonto Vergleich 2026 » Günstig eröffnen“, H1: „Der CHECK24 Girokonten Vergleich“
- Hero: „Kostenlose Girokonten in Österreich - Top-Angebote mit Zusatzleistungen - bis zu 3 % Habenzins“; einzige Vorab-Frage „Studentenkonten anzeigen? Ja/Nein“
- Vertrauen: „Beste Kundenbewertungen 5/5, 1.539 Bewertungen“, „Top Kundenservice, kostenlose persönliche Beratung“, Login und Kundenkonto, Chat, CHECK24-Punkte, „Erste Monatsrate geschenkt!“-Banner (Kredit-Kampagne auf der Girokonto-Seite)
- Content-Blöcke:
  - Kurz zusammengefasst
  - In 2 Schritten
  - Was ist ein Girokonto?
  - Die Debitkarte
  - Der Überziehungsrahmen
  - Wer kann ein Girokonto eröffnen? (18+, Hauptwohnsitz AT, Lichtbildausweis, Einkommensnachweis)
  - Was kostet ein Girokonto? (Kontoführung, Transaktionskosten, Kartenkosten)
  - Arten: Gehaltskonto, Privatkonto, Basiskonto, Gemeinschaftskonto, Onlinekonto
  - Worauf achten (Bankwahl, Kostenfaktor, Online-Banking und Sicherheit, Zusatzleistungen)
  - Hinweis-Box zum Bankomatnetz, Wissen-Box zum Kontowechsel
- FAQ:
  - Wie eröffnet man ein Girokonto?
  - Welche Girokonten sind wirklich kostenlos?
  - Was ist das beste Girokonto?
  - Wie wird ein Girokonto gekündigt?
- Ratgeber:
  - Bank Austria Konto kündigen
  - Bawag Konto kündigen
  - Sparkasse Konto kündigen
  - Raiffeisen Konto kündigen
  - Gehaltskonto, Kontogebühren sparen, Kontowechsel-Service, Girokonto kündigen
- Autorin: Viktoria Maria Blaschek, MA, mit dem Vermerk „arbeitet nicht mehr bei CHECK24, Inhalte werden von der Redaktion betreut“
- Keine Unterseiten für Gratis-Konto, Studentenkonto, ohne Gehaltseingang usw. (nur als Filter bzw. Vorab-Frage)

### 4.2 Eingaben, Filter, Sortierung (API `filterbar`)
- Kopf („Angaben ändern“): Gemeinschaftskonto Nein/Ja, Monatlicher Geldeingang (optional, Default 1.500 €), Studentenkonto anzeigen Nein/Ja
- Filter:
  - Bankentyp: Direktbanken, Filialbanken, Regionalbanken, Alle (mit Definitionen)
  - Jährliche Kontoführungsgebühr: „0 € ohne Bedingungen“, „0 € mit Bedingungen“, „Kostenpflichtig“
  - Dispozins: unter 10 % / beliebig
  - Kostenlose Bargeldabhebung: Weltweit / Europaweit / Inland
  - Mind. Tarifbewertung: Egal / 7+ / 8+
  - Weitere: Kostenlose Kreditkarte
- Weitere API-Parameter: `cardSystem`, `allwaysFree`, `minMonthlyReceiptOfMoney`, `joinedAccount`, `depositType`
- Sortierung: **LOW_COSTS (Default, niedrigste mtl. Kontogebühr)**, BEST_GRADE, BEST_BONUS. Es gibt einen „Testsieger“ (aktuell Wüstenrot ZERO).
- **Berechnung:** Es gibt keine Jahreskostenrechnung. Angezeigt wird die monatliche Kontogebühr (0, wenn der Geldeingang die Bedingung erfüllt), dazu Dispo, Habenzins, Kreditkartengebühr und Bonus.

### 4.3 Ergebnisliste und Produktdetail
- Liste (24 Produkte):
  - Bank, Logo, Bankentyp
  - **mtl. Kontogebühr** mit Hilfetext (Bedingung)
  - Dispozins, Habenzins
  - mtl. Kreditkartengebühr, Kartensysteme (Visa/MC/Amex), Apple/Google Pay
  - Anzahl Bargeldautomaten
  - Note, Promotion-Chips („100 € Prämie sichern“, „Kreditkarte im 1. Jahr gratis“, „3 % Zinsen“)
  - Kundenbewertungen (bei Wüstenrot 0)
- Produktdetail:
  - **Allgemein:** Kontoname, Anbieter, Banking-App
  - **Gebühren Konto:** Kontoführung, Dispozins, Habenzins
  - **Karten:** Bankomatkarte, Kreditkarte
  - **Bezahlung Konto:** Überweisung, Dauerauftrag, Lastschrift
  - **Karte:** Fremdwährung mit Bankomat- und Kreditkarte
  - **Bargeldabhebung:** Bankomatkarte am GAA, fremde GAA in Fremdwährung, Kreditkarte am GAA und in Fremdwährung, am Schalter, Einzahlung
  - **Bonus & Rabatte:** Bonus, Cashback
  - Produktdetails als PDF, AGB-PDF der Bank (für den Abschluss direkt über CHECK24)

### 4.4 Bewertungssystem „CHECK24 Tarifbewertung“ (Gesamtnote 1-10)
Teilnoten mit erreichten und erreichbaren Punkten, je mit Begründung (Beispiel Wüstenrot ZERO, 9,4 „Exzellent“):
- **Gebühren und Erträge:**
  - Kontoführungsgebühren 15/20
  - Min. Geldeingang für Gratis-Konto 4/5
  - Überziehungszinsen 7/10
  - Habenzinsen 5/5
  - Kreditkartengebühren 3/5
  - Neukundenbonus 10/10
- **Kostenlose Bargeldverfügung:** Behebungen Inland 10/10, Einzahlungen Inland 10/10, Bankfilialen im Inland 5/5
- **Weitere Leistungen:** Online-Banking inkl. App 10/10, Mobiles Bezahlen 10/10
- Max. 100 Punkte; „je nach Relevanz mit unterschiedlicher Gewichtung“ (Gewichte nicht offen). Noten 7,3-9,4, also kaum Spreizung.

### 4.5 Gut gemacht
- Teilnoten mit Begründungstext, Filter „0 € mit/ohne Bedingungen“, Bankentyp-Filter mit Definition
- Gemeinschaftskonto-Schalter, Direktabschluss, Beratung

### 4.6 Fehler und Lücken (konkret beobachtet)
- **Falsche Gebühren in der Liste:** Bank Austria Online-Konto mit „mtl. Kontogebühr 0“, obwohl der Hilfetext 2,58 € nennt; Relax-Konto mit 0 trotz 10,37 €. Bei der Default-Sortierung „niedrigste Kosten“ landen sie deshalb oben.
- KontoBox Small mit dem Hilfetext der „Konto-Box Large“; topkonto99 mit dem Text des „smartkonto99“; DKB als „Filialbank“, Erste s Kompakt als „Direktbank“
- Neukundenbonus-Begründung („Plus 0,5 % Sparkonto“) widerspricht dem Chip (+1,4 %); „Kreditkartengebühren 2 €“ bei Wert 0
- Tippfehler: „Apple Play“, „Standart“, „beitragsftrei“, Feldname `withoutSchufaprufung`
- Kein Nutzertyp, keine Transaktionskosten, keine Jahreskosten, keine Zinsrechnung
- Gewichtung nicht offengelegt; autorenloser Content; Kredit-Banner auf der Konto-Seite

---

## 5. finanz.at (www.finanz.at/konto/)

### 5.1 SEO und Content
- `/konto/`: Title „Die besten Girokonten 2026 - Konto-Vergleich | Österreich“, H2 „Girokonten vergleichen: Alles über Ihr Girokonto“
- Reiner Text, **kein Rechner, keine Produktliste, kein Bewertungssystem**. Am Ende „Jetzt Girokonto in Österreich vergleichen“ ohne Ziel.
- Abschnitte:
  - Girokontovergleich für Österreich
  - Günstiges Girokonto finden (Studie Kampmann, Berg & Partner **2015**)
  - Geld sparen mit Girokonto-Vergleich („Stiftung Warentest: bis 200 € sparen“, Fakten aus DE)
  - Girokonto wechseln
  - Prämien und Willkommensboni, Startguthaben (50-100 €)
  - Verzinsung des Guthabens („Niedrigzinsphase“, „deutlich unter einem Prozent“, veraltet)
  - Dispo-Zinsen, Kostenlose Kreditkarte zum Girokonto
  - Warum wechseln, Pro und Contra (KSV-Meldung bei Kontoeröffnung)
  - Kontowechsel im Detail (12 Tage, Fintechs), Stolperfallen
  - Vorteile/Nachteile
- Unterseiten:
  - `/konto/gehaltskonto/`: „Gehaltskonto Vergleich 2026“, wirbt für das **Hello Gehaltskonto mit PayLife-Kreditkarte** (beide Marken gibt es so nicht mehr)
  - `/konto/studentenkonto/`
  - `/konto/jugendkonto/`
  - `/konto/basiskonto/`: „Basiskonto in Österreich - Konto für Arbeitslose, Obdachlose & Asylwerber“, Deckel „**80 Euro**“ (veraltet, heute 83,45 €)
  - `/konto/firmenkonto/`, `/konto/kreditkarte/`
- Interne Links teils kaputt: „Gas“ und „Versicherungen“ zeigen auf `/konto/`.
- FAQ (Gehaltskonto): „Wozu braucht man ein Gehaltskonto?“, „Unterschied Gehalts- und Girokonto?“
- Vertrauen: Disclaimer „Produkte stammen von Partnern, die uns entschädigen“, News-Teaser (Bargeld-Einzahlung, Bankgebühren-Rückforderung). Autoren und Stand fehlen.

### 5.2 Bewertung
Reine SEO-Textseite mit News-Reichweite und Domain-Autorität. Für Suchanfragen wie „Girokonto Vergleich“ oder „Gehaltskonto“ ist sie schlagbar.

---

## 6. Querschnitt: Was wir übernehmen, was wir besser machen

### 6.1 Rechner „Persönlich rechnen“: Empfehlung
1. **Zwei Ebenen anbieten:**
   - **Schnell:** Nutzertyp nach AK-Warenkorb (Wenig 160 / Normal 280 / Intensiv 400 / Online 350) als Voreinstellung, mit Quelle „Nutzermodelle der AK (Bankenrechner)“
   - **Persönlich:** Die 9 Transaktionsarten der AK als Zahlenfelder, zusammengefasst zu 4-5 Fragen (Abhebungen am Bankomat, am Schalter, Überweisungen online/Papier, Lastschriften + Daueraufträge, Kartenzahlungen) plus Eingang, Tiefststand und Ausland
2. **Kennzahlen getrennt ausweisen:**
   - „Jährliche Kontokosten (wie AK, ohne Zinsen und Bonus)“
   - „Ihr Ergebnis im 1. Jahr inkl. Bonus und Zinsen“ (wie durchblicker)
   - „ab dem 2. Jahr“

   Nur durchblicker zeigt etwas Ähnliches, und auch dort nicht als zwei getrennte Werte.
3. **Kostenaufschlüsselung pro Posten** (Kontoführung, Buchungen, Karten, Bargeld, Ausland, Zinsen, Bonus). Bisher macht das niemand vollständig; Capitalo nur teilweise.
4. **Gratis-Bedingung als Feld** (min. Geldeingang, Altersgrenze, Aktivkonto) statt sie aus Freitext zu lesen: „Erfülle ich die Bedingung? Ja/Nein, sonst kostet es x €“.
5. Karten: 2. Debitkarte, Kreditkarte (keine / Standard / Gold mit Versicherung), 2. Kreditkarte.
6. Filter: Kontoart (Gehalt, Privat, Student, Jugend, Pension, Basis, Gemeinschaftskonto), Bundesland bzw. Filialnähe, Online/Filiale, Bankentyp, „0 € ohne Bedingung / mit Bedingung / kostenpflichtig“, Apple/Google Pay, österreichische IBAN, Einlagensicherung AT/DE/LT.

### 6.2 Bewertung (finvallo-Sterne): Empfehlung
- **Methodik vollständig offenlegen** inklusive Gewichtung (Lücke bei durchblicker und CHECK24) und **eine Skala für alle Kontoarten** (Capitalos 130/140/150 verwirrt)
- **AT-spezifische Kriterien:**
  - österreichische IBAN
  - Bankomat-Netz AT (z. B. Bankomaten von Euronet in AT kostenpflichtig)
  - Bargeld einzahlen (Filiale, Automat, MARIE-Trafik)
  - Kontowechselservice nach VZKG
  - Einlagensicherung (ESA/Land)
  - KSV-Prüfung
  - Filialen pro Bundesland
  - Entgeltinformation verlinkt
- Preis/Leistung trennen von Leistungsumfang. Sonst bekommen teure Pakete Top-Noten wie bei durchblicker.
- Teilnoten mit Begründung je Konto (das macht CHECK24 gut), **mit Datum der Datenprüfung** und Link zur Entgeltinformation der Bank (macht die AK, sonst niemand)

### 6.3 Daten und Vertrauen
- Datenqualität als USP: Capitalo und CHECK24 zeigen sichtbar falsche Gebühren und Widersprüche. „Jedes Konto mit Entgeltinformation (PDF) abgeglichen, Stand TT.MM.JJJJ“ und eine Funktion „Fehler melden“ (analog § 11 Abs. 8 VZKG) wären starke Signale.
- Standardisierte Begriffe der VZKDV als Feldnamen verwenden.
- Unabhängigkeit: Anzeigen klar trennen. Default-Sortierung nach Kosten oder Score, nicht nach „Empfehlung“ (Kritikpunkt Capitalo).
- Autor und Prüfer mit Foto und Qualifikation (Capitalo und durchblicker machen das, CHECK24 schwach, finanz.at fehlt).

### 6.4 SEO-Lücken (Seiten, die Konkurrenten nicht oder schwach haben)

| Seite / Keyword | AK | durchblicker | Capitalo | CHECK24 | finanz.at |
|---|---|---|---|---|---|
| Girokonto Vergleich (Hub) | (POST) | ✓ | ✓ | ✓ | Text |
| Gratis / kostenloses Konto | - | ✓ | ✓ (2×, kannibalisiert) | Filter | - |
| Konto ohne Gehaltseingang | - | - | Ratgeber | Filter | - |
| Studentenkonto | Kontotyp | ✓ (Title „2025“) | - | Filter | ✓ alt |
| Jugendkonto | Kontotyp | ✓ | - | - | ✓ |
| Pensionskonto | Kontotyp | Kontoart | - | - | - |
| Basiskonto | Kontotyp | - | FAQ | Text | ✓ veraltet |
| Gemeinschaftskonto | - | - | ✓ | Filter | - |
| Kontoführungsgebühren / Gebührenvergleich | - | Blog | ✓ | Ratgeber | - |
| Konto wechseln (VZKG) | - | Text | Ratgeber | Ratgeber | Text |
| Konto kündigen je Bank | - | Blog | - | ✓ (4 Banken) | - |
| Girokonto mit Kreditkarte gratis | - | - | Filter | Filter | Text |
| Konto mit Apple Pay / Google Pay | - | - | Filter | - | - |
| Konto mit österreichischer IBAN / Neobanken in AT | - | Chips | FAQ | - | - |
| Konto für Ausland / Fremdwährung | - | Blog | Rechner-Slider | Filter | - |
| Online-Konto vs. Filialkonto | - | ✓ (Gratis-Seite) | Ratgeber „Beste Bank“ | Text | - |
| AK-Nutzertypen / Kontokosten berechnen | PDF | PDF | - | - | - |
| Produkt-Testseiten je Konto | Detail (nicht indexiert) | Anbieterseiten dünn | ✓ | - | - |

**Neue Chancen:**
- „Kontokosten berechnen“ bzw. „Was kostet mein Konto wirklich?“ auf Basis der AK-Warenkörbe: Niemand hat eine indexierbare, erklärende Seite dazu.
- „Gratis-Konto ohne Bedingungen“ vs. „mit Gehaltseingang“ als echte Bestenliste mit Schwellen-Tabelle (400 / 500 / 700 / 1.000 / 1.340 / 1.500 €)
- Pensionskonto, Basiskonto (aktuell 83,45 €/41,73 €), Konto mit AT-IBAN
- Bankomatgebühren in AT (Fremdbetreiber)
- Je Bank „Konto kündigen“ und „Kontowechsel“
- Bestenlisten mit Datum wie bei Kreditkarten: „Bestes Gehaltskonto 10/2026“, „Bestes Studentenkonto“, „Bestes Konto für Wenignutzer/Online“ (Nutzertyp-Bestenlisten gibt es bei niemandem)

### 6.5 Konkrete Fehler der Konkurrenz, die wir vermeiden
- Datumsangaben, die nicht zum aktuellen Monat passen (durchblicker „August“, „2025“)
- Veraltete Rechtswerte (Basiskonto 80 €)
- Uneinheitliche Begriffe (Intensiv/Viel)
- Widersprüche zwischen Liste, Tabelle und Produktseite (Capitalo, CHECK24)
- Deutsche Kriterien im AT-Produkt (Capitalo)
- Bedingungen per Regex aus Freitext (Capitalo)
- Anzeigen als Default-Sortierung

---

## 7. Quellen und Rohdaten
- AK:
  - https://www.bankenrechner.at/girokonto (Formular, POST-Ergebnis, Detailseite)
  - https://www.bankenrechner.at/files/files/Giro_Nutzermodelle_2018.pdf
  - https://www.bankenrechner.at/files/files/FAQ_Girokonten.pdf
  - https://www.bankenrechner.at/girokontoNutzer
- Gesetz:
  - VZKG BGBl. I 35/2016 (§ 2 Z 28, §§ 9-13, § 26): https://www.ris.bka.gv.at/Dokumente/BgblAuth/BGBLA_2016_I_35/BGBLA_2016_I_35.html
  - VZKDV BGBl. II 60/2018: https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20010171
- durchblicker:
  - https://durchblicker.at/girokonto, /girokonto/vergleich/ergebnis, /gratis-konto, /studentenkonto, /jugendkonto, /anbieter/girokonto/dadat
  - /templates/girokonto/variator(205046).js
  - https://durchblicker.at/res/pdf/Nutzertyp_Information.pdf
- Capitalo:
  - https://www.capitalo.at/girokonto, /girokonto/gratis, /girokonto/kostenlos, /girokonto/gebuehren, /girokonto/gemeinschaftskonto, /girokonto/ratgeber (+ Artikel)
  - /anbieter/anadibank/produkte/online-girokonto, /anbieter/easybank/produkte/easy-gratis
  - Next.js-Chunks (Filter- und Kostenlogik)
- CHECK24:
  - https://www.check24.at/girokonto/, https://girokonto.fin.check24.at/start
  - API `/frontend/GIRO/filterbar`, `/frontend/GIRO/product/filtered`, `/frontend/GIRO/product/613`
- finanz.at:
  - https://www.finanz.at/konto/, /konto/gehaltskonto/, /konto/studentenkonto/, /konto/basiskonto/
