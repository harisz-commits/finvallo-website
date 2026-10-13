# Generator-Skripte

Alles neu bauen: `bash tools/build.sh` (idempotent, danach committen).

## Daten
- `daten/at/karten.json` – alle Karten Österreich (eine Zeile pro Wert, `geprueft` = Datum der letzten Prüfung, `blocks` = Texte zu Extras, Gebühren, Versicherung).
- `daten/at/anbieter.json` – Anbieter Österreich (Name, Typ, Sitz, Website, Kurztext).
- `daten/at/business.json` – weitere Business-Angebote Österreich.
- `de-recherche/*.json` – alle Karten Deutschland (`geprueft` je Karte), `INSTRUCTIONS.md` = Erfassungsregeln; `overrides.py` = redaktionelle Korrekturen.
- `sammeln.py` – Sammelraten für die Bestenlisten Meilen/Punkte und Cashback.

## Skripte (Reihenfolge wie in build.sh)
- `karten.py` – Karten-, Listen-, Anbieter-, Bestenlisten-Seiten, JSON-Daten, Sitemap, llms.txt und Kreditkarten-Rechner für AT und DE.
- `score.py` – Bewertung nach der Finvallo-Methodik.
- `ratgeber.py`, `rechner.py`, `landing.py` – Ratgeber, Finanzrechner, Startseiten.
- `header.py` – Header/Navigation auf allen Seiten.
- `cleanup.py` – entfernt interne Notizen und vereinheitlicht Texte.
- `listui.py` – Filter und Fußnoten in den Kartenlisten.

## Wöchentliche Prüfung
Siehe `PRUEFUNG.md`.
