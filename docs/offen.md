# Offene Punkte (für später)

Stand: 14.10.2026

| Punkt | Worum es geht | Wer |
|---|---|---|
| Musterbrief card complete | Abschnitt „So holst du dir das Geld zurück“ im Fremdwährungs-Ratgeber, mit Link auf die AK-Seite (wien.arbeiterkammer.at/cardcomplete). Kein AK-Text kopieren. | Entscheidung: Haris |
| Besucherzähler (Plausible) | Zählt Besucher ohne Cookies; Absatz in der Datenschutzerklärung ist vorbereitet. Kostet ab ca. 9 €/Monat. Einschalten in `tools/daten/site.json` (`analytics.enabled`). | Entscheidung: Haris |
| Foto für „Über Finvallo“ | `public/assets/haris.jpg` (quadratisch, ohne Nachnamen im Dateinamen/EXIF). | Haris liefert |
| Rich Results Test | search.google.com/test/rich-results mit finvallo.com/, einer Kartenseite und einer Bestenliste prüfen; Screenshot bei Fehlern. | Haris |
| Live-Check | `node scripts/live-check.mjs`: www/https/Schrägstrich/404/Cache. Nach dem nächsten Server-Update prüfen, ob der HTML-Cache-Header da ist. | Claude (braucht Freigabe) |
| Profile anlegen | LinkedIn, Crunchbase, X/Instagram mit Texten aus `docs/profile-texte.md` und Logos aus `public/assets/brand/`; danach Links in `sameAs` eintragen. | Haris, dann Claude |
| Long-Tail-Ratgeber | Entwürfe in `entwuerfe/` brauchen Text, bevor sie online gehen. | Haris oder Claude |
| Outreach | Liste in `docs/outreach-liste.md` abarbeiten, Presseaussendung in `docs/presseaussendung.md`. | Haris |
