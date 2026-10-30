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
| Affiliate-Links pflegen | Partnerlinks liegen in `tools/daten/affiliate.json` (Schlüssel = Slug der Produktseite, Bank-Slug beim Festgeld, Anbieterkürzel). Neue Produkte oder Links dort eintragen, `check.py` meldet Schlüssel ohne Seite. Noch ohne Partnerlink, obwohl im Programm: Bigbank AT (nicht im Vergleich), Suresse, PSD Bank, Tide, Vivid Business, Wallester (keine Produkte auf der Seite). | Haris, dann Claude |
| sameAs im Schema | Profile (LinkedIn, X usw.) fehlen noch, siehe „Profile anlegen“. | Haris, dann Claude |
| CSP-Header | Content-Security-Policy fehlt in `server/security-headers.conf`; erst auf dem Server testen, da Inline-Skripte (Rechner, JSON-LD) betroffen sind. | Claude (braucht Freigabe) |

## Regeln aus dem Qualitäts-Check (29.10.)
- FAQ nur mit Fragen, die zur Seite gehören. Dieselbe Frage auf mehr als 4 Seiten bricht `check.py` ab. Kreditkartenseiten haben nur dann einen FAQ-Block, wenn es eine kartenspezifische Frage gibt (Lieferzeit, Ausschlüsse der Reiseversicherung).
- Festgeld hat keine Laufzeit- und Bestenlisten-Seiten mehr, alles läuft über den Filter im Vergleich. Alte Adressen leiten per 301 auf den Vergleich mit gesetztem Filter.
- Review-Schema entfernt (29.10.): die Sterne bleiben sichtbar, aber ohne unsichtbare Auszeichnung „bewertet von“.
- Offen: Rechner AT/DE zusammenlegen (vorerst nicht), Tempo neuer Seiten.
- Girokonto-Bestenlisten nach Thema (29.10.): Texte in `tools/giro_listen_texte_a/b/c.py`, Zusatzdaten in `tools/daten/<land>/girokonten-extra.json`. Lücken: bei 37 DE- und 30 AT-Konten ist die Zahl der Unterkonten nicht belegt, bei 29 DE- und 32 AT-Konten die Bonitätsabfrage. AT hat noch keine Listen „mit Kreditkarte“, „ohne KSV“ und „nachhaltige Banken“ (zu wenige Konten oder Banken).
- Kreditkarten (30.10.): Business-Karten und Karten nur für bestimmte Gruppen sind raus (`karten.aufnehmen()`), reine Studentenkarten stehen nur in der Bestenliste „Studierende“. Der Ratgeber „Firmenkreditkarte“ ist entfallen (`ratgeber.ENTFALLEN`), `ratgeber_business.py` bleibt ungenutzt im Repo.
