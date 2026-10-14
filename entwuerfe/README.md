# Ratgeber-Entwürfe (C23)

Gerüste für neue Long-Tail-Ratgeber. Alle Dateien haben `draft: true` und werden **nicht gebaut** und **nicht in die Sitemap** aufgenommen.
Der Build liest dieses Verzeichnis nicht ein. Veröffentlichen heißt: Text liefern, alle `<!-- TODO: Text -->`-Slots füllen,
`draft: false` setzen und den Artikel in `tools/ratgeber.py` aufnehmen (Tabellen kommen dort aus den Kartendaten, siehe `DATEN:`-Zeilen).

| Datei | Land | Datenquelle der Tabelle |
|---|---|---|
| kreditkarte-ohne-ksv.md | AT | Debit-/Prepaid-Karten und Karten ohne Bonitätsprüfung aus `tools/daten/at/karten.json` |
| kreditkarte-ohne-schufa.md | DE | dito aus `tools/daten/de/karten.json` |
| kreditkarte-studenten.md | AT, DE | Bestenliste `studium` |
| revolut-vs-n26.md | AT, DE | alle Revolut- und N26-Tarife |
| card-complete-kursaufschlag.md | AT | Ausgliederung des Abschnitts „Das Urteil zu card complete“ aus `/at/ratgeber/fremdwaehrung/` |

`mietwagen-kaution` ist bereits erweitert (Tabelle „Karten, die für Kautionen geeignet sind“, live im Build).
