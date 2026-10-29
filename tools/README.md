# Generator-Skripte

Alles neu bauen: `bash tools/build.sh` (idempotent, danach committen).

## Daten
- `daten/at/karten.json` – alle Karten Österreich (eine Zeile pro Wert, `geprueft` = Datum der letzten Prüfung, `blocks` = Texte zu Extras, Gebühren, Versicherung).
- `daten/at/anbieter.json` – Anbieter Österreich (Name, Typ, Sitz, Website, Kurztext).
- `daten/at/business.json` – weitere Business-Angebote Österreich.
- `de-recherche/*.json` – alle Karten Deutschland (`geprueft` je Karte), `INSTRUCTIONS.md` = Erfassungsregeln; `overrides.py` = redaktionelle Korrekturen.
- `daten/at/lohnt.json`, `daten/de/lohnt.json` – Guthaben, Lounges, Abos und Annahmen für „Ab wann lohnt sich …?“.
- `festgeld-recherche/<GRUPPE>.json` – Rohdaten Festgeld je Recherche-Gruppe (`INSTRUCTIONS.md` = Erfassungsregeln, `laender.json` = Einlagensicherung und S&P-Rating je Land). `festgeld_daten.py` führt sie zu `daten/<land>/festgeld.json` und `.csv` zusammen (nach neuer Recherche einmal ausführen).
- `sammeln.py` – Sammelraten für die Bestenlisten Meilen/Punkte und Cashback.

## Skripte (Reihenfolge wie in build.sh)
- `karten.py` – Karten-, Listen-, Anbieter-, Bestenlisten-Seiten, JSON-Daten, Sitemap, llms.txt und Kreditkarten-Rechner für AT und DE.
- `girokonto.py` - Girokonto-Vergleich je Land: Liste mit Kostenrechner, Filtern und aufklappbaren Konditionen je Konto (`assets/giro.js`), Bestenlisten, Methodik. Eigene Kontoseiten gibt es nicht mehr, alte Adressen leiten per 301 auf `#gk-<slug>` im Vergleich.
- `festgeld.py` – Festgeld-Vergleich je Land: Liste mit Zinsrechner und Filtern (`assets/festgeld.js`), aufklappbare Konditionen je Angebot (keine eigenen Angebots- oder Bankseiten, alte Adressen leiten per 301 auf den Eintrag im Vergleich), Laufzeit-Seiten, Bestenlisten, Methodik, JSON/CSV-Export; Rechnung wird in `check.py` gegen `festgeld.js` geprüft.
- `lohnt.py` – Seiten „Ab wann lohnt sich …?“ und der Block „Top-Karten, je nachdem wie du sie nutzt“ auf den Bestenlisten.
- `score.py` – Bewertung nach der Finvallo-Methodik.
- `ratgeber.py` (+ `ratgeber_*.py` je Thema und Land: Karten, Girokonto `ratgeber_girokonto*`/`ratgeber_konto*`, Festgeld `ratgeber_festgeld*`), `rechner.py`, `landing.py` – Ratgeber, Finanzrechner, Startseiten.
- `hubs.py` – Übersichten je Land: `/bestenlisten/` (alle Bestenlisten der drei Vergleiche) und `/methodik/` (alle Bewertungsregeln).
- `header.py` – Header/Navigation auf allen Seiten.
- `cleanup.py` – entfernt interne Notizen und vereinheitlicht Texte.
- `listui.py` – Filter und Fußnoten in den Kartenlisten.

## Wöchentliche Prüfung
Siehe `PRUEFUNG.md`.
