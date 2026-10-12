# Generator-Skripte

- `gen_de.py` – erzeugt den Kreditkartenvergleich Deutschland (`public/de/kreditkarten/…`, `public/de/daten/kreditkarten.json`, Rechner-Daten, Sitemap, llms.txt) aus `de-recherche/*.json`.
- `score.py` – Bewertung nach der Finvallo-Methodik (identisch mit /at/kreditkarten/methodik/).
- `overrides.py` – redaktionelle Korrekturen und Kartennamen.
- `header.py` – setzt Header/Navigation auf allen Seiten neu.
- `landing.py` – erzeugt Startseite, /at/ und /de/.
- `de-recherche/` – Rohdaten der DE-Recherche (Stand 12.10.2026), `INSTRUCTIONS.md` = Erfassungsregeln.

Reihenfolge nach Datenänderung: `python3 tools/gen_de.py && python3 tools/header.py && python3 tools/landing.py`, danach CSS-Version (`site.css?v=`) erhöhen, falls CSS geändert wurde.
