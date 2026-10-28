# Offene Punkte (für später)

Stand: 28.10.2026

| Punkt | Worum es geht | Wer |
|---|---|---|
| Musterbrief card complete | Abschnitt „So holst du dir das Geld zurück“ im Fremdwährungs-Ratgeber, mit Link auf die AK-Seite (wien.arbeiterkammer.at/cardcomplete). Kein AK-Text kopieren. | Entscheidung: Haris |
| Besucherzähler (Plausible) | Zählt Besucher ohne Cookies; Absatz in der Datenschutzerklärung ist vorbereitet. Kostet ab ca. 9 €/Monat. Einschalten in `tools/daten/site.json` (`analytics.enabled`). | Entscheidung: Haris |
| Rich Results Test | search.google.com/test/rich-results mit finvallo.com/, einer Kartenseite und einer Bestenliste prüfen; Screenshot bei Fehlern. | Haris |
| Live-Check | `node scripts/live-check.mjs`: www/https/Schrägstrich/404/Cache. Nach dem nächsten Server-Update prüfen, ob der HTML-Cache-Header da ist. | Claude (braucht Freigabe) |
| Profile anlegen | LinkedIn, Crunchbase, X/Instagram mit Texten aus `docs/profile-texte.md` und Logos aus `public/assets/brand/`; danach Links in `sameAs` eintragen. | Haris, dann Claude |
| Long-Tail-Ratgeber | Entwürfe in `entwuerfe/` brauchen Text, bevor sie online gehen. | Haris oder Claude |
| Outreach | Liste in `docs/outreach-liste.md` abarbeiten, Presseaussendung in `docs/presseaussendung.md`. | Haris |
| Festgeld-Zinsen pflegen | Zinsen ändern sich oft (Plattformen wöchentlich, Aktionen enden). Recherche-Dateien in `tools/festgeld-recherche/` aktualisieren, dann `python3 tools/festgeld_daten.py` und `bash tools/build.sh`. Abgelaufene Aktionen mit Datum fallen beim Bauen automatisch weg. | Claude, regelmäßig |
| Festgeld: Banken ohne abrufbare Konditionen | Bigbank (AT), GarantiBank, Bank11direkt, Toyota Bank, AutoBank (AT) sperren automatisierte Abrufe; ohne Konditionen aus erster Hand nicht im Vergleich. Von Hand prüfen und eintragen. | Haris oder Claude |
| Girokonto-Daten | Felder Gemeinschaftskonto, Sollzins und Überschreitung fehlen bei vielen Konten („keine Angabe“, zählt neutral). Bankdokumente teils älter als 60 Tage (Stand im Datensatz). | Claude |
| Kreditkarten DE: alte Quelldokumente | Advanzia (PLV 07/2024), PAYBACK Visa (03/2024), HVB (02/2025) u. a. gegen das aktuelle Dokument prüfen; Prüfdatum ist frisch, Quelle alt. | Claude |
| Prüfdaten laufen gleichzeitig ab | Fast alle Karten wurden am 11./12.10. geprüft und sind um den 10.12. gleichzeitig fällig; Girokonto und Festgeld am 27.10. Prüfung staffeln. | Claude |
| Offene Ratgeber-Entwürfe | `entwuerfe/revolut-vs-n26.md` und `card-complete-kursaufschlag.md` (Entscheidung Haris, siehe oben). `kreditkarte-studenten.md` ist längst live, `ohne-ksv/-schufa` würden mit `ohne-bonitaetspruefung` konkurrieren – Entwürfe löschen. | Haris |
| Affiliate-Kennzeichnung | Es gibt noch keine Partnerlinks. Sobald es welche gibt: Button „Zum Anbieter*“ mit `rel="sponsored"`, Regel im Generator an einer Stelle. | Claude, wenn Partner da |
| sameAs im Schema | Profile (LinkedIn, X usw.) fehlen noch, siehe „Profile anlegen“. | Haris, dann Claude |
| CSP-Header | Content-Security-Policy fehlt in `server/security-headers.conf`; erst auf dem Server testen, da Inline-Skripte (Rechner, JSON-LD) betroffen sind. | Claude (braucht Freigabe) |
