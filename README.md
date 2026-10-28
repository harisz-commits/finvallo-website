# Finvallo – Website

Statische, SEO- und KI-optimierte Website von finvallo.com.

- `public/` – die Website (wird von Nginx ausgeliefert)
- `server/setup.sh` – einmalige Einrichtung auf dem Server
- `server/update.sh` – Website aktualisieren

Einrichtung: `git clone https://github.com/harisz-commits/finvallo-website.git /var/www/finvallo && bash /var/www/finvallo/server/setup.sh`
Update: `bash /var/www/finvallo/server/update.sh`

## Aufbau
- Vergleiche je Land (`/at/`, `/de/`): Kreditkarten, Girokonten, Festgeld; dazu Bestenlisten, Ratgeber und Rechner.
- Alles wird aus Daten generiert: `bash tools/build.sh` baut alle Seiten neu und prüft sie (`scripts/seo-check.mjs`, danach `python3 tools/check.py`). Details in `tools/README.md`.
- Daten: `tools/daten/<land>/` (Girokonten, Festgeld, Karten AT), `tools/de-recherche/` (Karten DE), `tools/festgeld-recherche/` (Festgeld-Rohdaten).
