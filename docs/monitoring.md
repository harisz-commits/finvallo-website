# Monitoring – wöchentliche Checkliste

Für den Betreiber von finvallo.com. Dauer etwa 20 Minuten pro Woche.

## Automatisch (läuft im Repo)

- `bash tools/build.sh` führt am Ende `node scripts/seo-check.mjs` aus: Kartenanzahlen, Meta Descriptions, interne Links,
  JSON-LD, hreflang, Prüfdaten, zusammengeklebte Wörter, doppelte Vor-/Nachteile, Navigationslinks, FAQ-Doppelungen, Sitemap.
  Bei einem Fehler endet der Build mit Exit-Code 1. Zusätzlich: `python3 tools/check.py`.
- `node scripts/live-check.mjs` prüft die Live-Seite: www → ohne www, http → https, Schrägstrich-Weiterleitung,
  404-Status, Cache-Header und Komprimierung. Gibt eine Tabelle aus.

## Jede Woche

1. **Google Search Console → Indexierung → Seiten**
   - Anzahl „Indexiert“ und „Nicht indexiert“ notieren (Verlauf siehe Tabelle unten).
   - Gründe unter „Warum Seiten nicht indexiert werden“ ansehen. Normal: „Seite mit Weiterleitung“ (die 301 der alten Anbieter-URLs),
     „Durch noindex-Tag ausgeschlossen“ (Impressum, Datenschutz, 404). Auffällig: „Gecrawlt – zurzeit nicht indexiert“ bei Kartenseiten,
     „Duplikat – Google hat eine andere Seite als kanonische Seite bestimmt“, „Nicht gefunden (404)“.
2. **Search Console → Leistung**
   - Filter „Land“: Österreich und Deutschland getrennt ansehen (Klicks, Impressionen, durchschnittliche Position).
   - Suchanfragen mit vielen Impressionen und wenig Klicks notieren: Kandidaten für bessere Titel/Descriptions.
3. **Bing Webmaster Tools**
   - „Site Explorer“: werden die Bereiche /at/ und /de/ vollständig angezeigt?
   - „IndexNow“: kommen die Meldungen nach jedem Update an (der Server meldet geänderte Seiten automatisch)?
4. **PageSpeed Insights (Mobil)** für drei URLs; LCP, CLS und INP notieren:
   - https://finvallo.com/
   - https://finvallo.com/at/kreditkarten/
   - https://finvallo.com/at/kreditkarten/tf-bank-mastercard-gold/
   - Zielwerte: LCP ≤ 2,5 s, CLS ≤ 0,1, INP ≤ 200 ms.
5. `node scripts/live-check.mjs` ausführen; jede Zeile muss „ok“ zeigen.

## Nach 4 Wochen ohne Indexierung

- Startseite und die beiden Vergleichsseiten in der Search Console per **URL-Prüfung → Indexierung beantragen** erneut anstoßen.
- Sitemap unter **Sitemaps** erneut einreichen (https://finvallo.com/sitemap.xml) und prüfen, ob die Zahl der erkannten URLs stimmt.
- Backlinks prüfen (Search Console → Links → „Top-verlinkende Websites“). Ohne externe Links indexiert Google neue Domains oft langsam:
  Profile aus `docs/profile-texte.md` anlegen und die Outreach-Liste (`docs/outreach-liste.md`) abarbeiten.

## Verlauf

| Woche | Indexiert | Nicht indexiert | Klicks AT | Klicks DE | LCP Start | Notiz |
|---|---|---|---|---|---|---|
| | | | | | | |
