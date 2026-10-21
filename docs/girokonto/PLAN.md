# Plan: Girokonten Österreich auf finvallo (Stand 21.10.2026)

Grundlage: `markt.md` (Marktliste), `konkurrenz.md` (durchblicker, AK-Bankenrechner, Capitalo, CHECK24, finanz.at), `recht.md` (VZKG, VZKDV, UWG, MedienG, UrhG). Noch kein Code.

## 1. Ziel

Der genaueste Girokonto-Vergleich in Österreich, im selben Design wie die Kreditkarten.
Unser Vorteil gegenüber den anderen:
- Jede Zahl kommt aus der Entgeltinformation der Bank (Pflicht-PDF nach VZKG), mit Link und Datum. Die Portale haben nachweislich falsche Werte (Capitalo, CHECK24), durchblicker zeigt veraltete Daten.
- Offene Bewertung mit Gewichten (durchblicker und CHECK24 legen das nicht offen).
- Rechnung mit den offiziellen AK-Nutzertypen, plus persönliche Rechnung mit Bonus und Zinsen. Aufschlüsselung je Posten, das macht niemand vollständig.
- Neobanken und Filialbanken in einer Liste (der AK-Rechner hat keine Neobanken).

## 2. Markt

- Rund 199 Kontomodelle für Privatpersonen in Österreich, davon rund 25 Basiskonten.
- 157 davon stehen im AK-Bankenrechner.
- Neobanken für Österreich: Trade Republic (einzige mit AT-IBAN), N26, Revolut, bunq, Vivid, DKB, Tomorrow, Wise.
- Kein Girokonto in Österreich: Openbank, Klarna, Bitpanda. Hello bank gibt es nicht mehr (easybank).
- Kernproblem regionale Preise: Raiffeisen (Landesbanken plus über 300 lokale Banken), Sparkassen (gleiche Namen, verschiedene Preise), Volksbanken.

## 3. Umfang beim Start (Vorschlag)

Phase 1, rund 60 Konten:
- Alle überregionalen Banken: Bank Austria, BAWAG, easybank, bank99, Bank Direkt, DADAT, Anadi, Wüstenrot, Oberbank, BKS, BTV, Sparda und Volksbank Wien, Hypo-Banken.
- Erste Bank (Wien) als Referenz für die Sparkassen, je Raiffeisen-Landesbank ein Referenzkonto.
- Alle Neobanken.
- Je Bank alle Kontoarten: Gehalt, Privat, Student, Jugend, Pension, Basiskonto.

Regionale Banken: Referenzinstitut mit dem Hinweis „Preise können bei deiner Bank im Bundesland abweichen“ und Bundesland-Filter. Phase 2: restliche Sparkassen, Volksbanken und Raiffeisenbanken, soweit Entgeltinformationen online sind.

## 4. Datenquellen und Regeln

- Hauptquelle: Entgeltinformation (PDF) und Produktseite der Bank. Je Konto: Link, Datum der Entgeltinformation, geprüft am, Hash der Datei.
- AK-Bankenrechner nur zum Finden der Konten und zum Gegenprüfen. Nicht übernehmen (Datenbankschutz §§ 76c ff UrhG). Wir verlinken auf ihn.
- Vergleichsportale nie als Quelle.
- Wöchentlicher Abgleich: Hat sich das PDF geändert (Hash), wird das Konto neu geprüft. Banken müssen Entgeltänderungen 2 Monate vorher ankündigen.
- Fehlendes als „keine Angabe“, in der Bewertung 2,5 Sterne mit Hinweis „Datenlücke“ (wie bei Kreditkarten).

## 5. Datenmodell je Konto

**Stammdaten:** Bank, Rechtsträger, Sitzland, Art (Kreditinstitut, E-Geld-Institut), Einlagensicherung (System, Land, Betrag), IBAN-Land, Kontoname, Kontoart, Verrechnung (Pauschale, Einzel, Mischform), Eröffnung (online, Video-Ident, Filiale), Bundesländer, Filialen, Selbstbedienung.

**Die 13 Pflichtbegriffe der VZKDV**, je Preis, Einheit (Monat, Quartal, Vorgang), Inklusivmenge, Preis darüber, Kanal (online, Papier, Schalter):
Kontoführung, Internetbanking, Anlassbezogener Kontoauszug, Überweisung, Gutschrift, Dauerauftrag, Lastschrift, Information über Nicht-Durchführung, Bereitstellung einer Debitkarte, Bargeldeinzahlung, Bargeldbehebung, Eingeräumte Kontoüberziehung, Überschreitung des Überziehungsrahmens.

**Gratis-Bedingungen strukturiert:** Mindest-Geldeingang pro Monat, Altersgrenze, nur im 1. Jahr, sonstige (z. B. Kartenumsatz). Preis, wenn die Bedingung nicht erfüllt ist.

**Karten:** Debitkarte inklusive, 2. Debitkarte, Kreditkarte inklusive (welche, mit Verknüpfung zu unseren Kreditkartenseiten), Apple Pay, Google Pay.

**Bargeld:** eigene Automaten, Fremdautomaten Inland, Drittbetreiber (z. B. Euronet), Euroraum, Ausland, Einzahlen (Filiale, Automat).

**Ausland:** Fremdwährungsentgelt bei Kartenzahlung und bei Abhebungen.

**Zinsen:** Sollzins eingeräumte Überziehung, Sollzins Überschreitung, Habenzins, jeweils fix oder variabel, angekündigte Änderungen mit Datum.

**Bonus:** Betrag, Bedingungen, gültig bis, Quelle.

**Service:** Echtzeitüberweisung, Kontowechsel-Service, KESt-Abzug automatisch (bei Auslandsbanken meist nicht), Gemeinschaftskonto, Mindestalter, Kontoauszug, Hotline, App-Bewertung nur mit Quelle.

**Meta:** Quelle, Stand der Entgeltinformation, geprüft am, gültig ab, Hash.

## 6. Rechnung

Eine Rechenlogik für Liste, Bestenlisten, Produktseite und Rechner (wie bei den Kreditkarten):

1. **Jährliche Kontokosten wie AK** für die 4 offiziellen Nutzertypen (Wenig 160, Normal 280, Intensiv 400, Online 350 Buchungen pro Jahr). Ohne Zinsen und Bonus. Quelle genannt.
2. **Persönlich rechnen:** Geldeingang, durchschnittliches Guthaben und Tiefststand, Abhebungen (eigene, fremde, Ausland), Überweisungen online oder Papier, Kartenzahlungen, Alter, Online oder Filiale, gewünschte Karten.
3. **Ergebnis getrennt:** Kosten ab dem 2. Jahr, Ergebnis im 1. Jahr mit Bonus und Zinsen. Aufschlüsselung je Posten.
4. **Gratis-Bedingung prüfen:** „Bei deinem Geldeingang ist das Konto gratis“ oder „kostet x € pro Jahr“.
5. Kontrollbeispiele als Test in check.py (wie beim Kreditkartenrechner).

## 7. Bewertung (Vorschlag, offen gelegt)

| Kriterium | Gewicht |
|---|---|
| Kosten (Jahreskosten Normalnutzer ab 2. Jahr) | 35 % |
| Bedingungen für den Gratis-Preis (Hürde) | 10 % |
| Bargeld (Behebung, Einzahlen, Netz) | 10 % |
| Karten (Debit inklusive, Kreditkarte, Apple und Google Pay) | 10 % |
| Zinsen (Sollzins, Habenzins) | 10 % |
| Alltag und Service (Filiale oder App, AT-IBAN, Echtzeitüberweisung, Kontowechsel, KESt) | 15 % |
| Sicherheit (Einlagensicherung, Kreditinstitut oder E-Geld) | 10 % |

Bonus zählt nicht in die Sterne, nur in die Rechnung im 1. Jahr. Fehlende Daten 2,5 Sterne mit Hinweis. Eigene Reihenfolge je Nutzertyp in den Bestenlisten.

## 8. Seiten (gleiches Design wie Kreditkarten)

- **Hub und Liste** `/at/girokonto/`: Liste mit Filtern und „Persönlich rechnen“.
- **Kontoseite** `/at/girokonto/<konto>/`: Auf einen Blick, Kosten je Nutzertyp, Gratis-Bedingung, Karten, Bargeld, Zinsen, Bonus, Service, Für wen passt es und für wen nicht, FAQ, Quelle und Stand, Fehler melden.
- **Anbieterseiten** gemeinsam mit den Kreditkarten (eine Seite je Bank mit Konten und Karten).
- **Bestenlisten:** Gratis ohne Bedingung, Gratis mit Geldeingang (Tabelle der Schwellen: 400, 500, 700, 1.000, 1.500 €), Gehaltskonto, Studentenkonto, Jugendkonto, Pensionskonto, Online-Konto, mit Filiale, mit Kreditkarte, mit Bonus, je Nutzertyp (Wenig, Normal, Intensiv, Online), mit österreichischer IBAN.
- **Rechner:** „Kontokosten berechnen“ mit den AK-Nutzertypen (hat niemand als eigene Seite).
- **Ratgeber:** Basiskonto (83,45 € / 41,73 €), Konto wechseln (VZKG), Konto kündigen, Konto ohne Gehaltseingang, Neobanken und AT-IBAN, Bankomatgebühren und Fremdautomaten, Gemeinschaftskonto, Dispo und Überziehung, Einlagensicherung, Entgeltaufstellung lesen.

**Filter** (aus den Screenshots und der Analyse): Kontoart, kostenlos / bedingt kostenlos / kostenpflichtig, mit Bonus, Kreditkarte inklusive, Debitkarte gratis, Apple Pay, Google Pay, Online oder Filiale, Bundesland, österreichische IBAN, Einlagensicherung Land, Bankentyp, nachhaltig (nur mit Beleg, z. B. Umweltzeichen UZ 49).

## 9. Recht und Vertrauen

- Wir sind keine offizielle Vergleichsseite (das ist nur der AK-Bankenrechner). Nie „offiziell“ oder „zertifiziert“ schreiben.
- Vor der Liste: Hinweis, wie viele Konten wir vergleichen und dass nicht alle regionalen Banken drin sind.
- Bewertungsregeln direkt von der Liste verlinkt (§ 2 Abs. 6a UWG). Affiliate nie in der Sortierung.
- „Gratis“ nur, wenn es stimmt; Bonus immer mit Bedingungen.
- Link zum AK-Bankenrechner als Ergänzung.
- **Offener Punkt für dich:** Gewerbe mit der WKO klären (Affiliate ist gewerbsmäßig). Und prüfen lassen, ob Kreditkarten mit Kreditrahmen oder Überziehung als Kreditvermittlung (§ 136a GewO) gelten. Das betrifft auch den bestehenden Kreditkartenvergleich.

## 10. News

Ja, aber als **Konto-Radar** statt klassischer News:
- Eigene Meldungen aus unseren Daten: Gebührenerhöhung angekündigt, neue Gratis-Bedingung, Bonus neu oder beendet, Zinsänderung.
- Fakten sind frei. Fremde Artikel nur verlinken, nicht umschreiben (Presseverleger-Leistungsschutzrecht).
- Offenlegung nach Mediengesetz ist schon da.
- Erst nach dem Start (Phase 5), weil es den wöchentlichen Datenabgleich braucht.

## 11. Phasen

1. **Entscheidungen** (Punkt 12).
2. **Daten** für rund 60 Konten aus den Entgeltinformationen, Datenmodell, Prüfskript.
3. **Rechnung und Bewertung** mit Kontrollbeispielen.
4. **Seiten:** Hub und Liste, Kontoseiten, Anbieterseiten, Bestenlisten, Rechner.
5. **Ratgeber**, danach restliche regionale Banken, Konto-Radar.

## 12. Offene Entscheidungen

1. Start mit rund 60 Konten oder gleich alle rund 200?
2. Regionale Banken mit Referenzinstitut und Bundesland-Filter?
3. Gewichte der Bewertung wie in Punkt 7?
4. AK-Nutzertypen als Standard übernehmen?
5. Bonus nur in der Rechnung für das 1. Jahr, nicht in den Sternen?
6. Nachhaltig-Filter nur mit Beleg?
7. Adresse `/at/girokonto/` und Menüpunkt „Girokonten“ neben „Kreditkarten“?
8. WKO-Frage klären?
