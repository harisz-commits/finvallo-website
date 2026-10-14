# Profiltexte für Social- und Firmenprofile

Gilt für: LinkedIn-Unternehmensseite, Crunchbase, X-Bio, Instagram-Bio.

**Kernsatz (Grundlage aller Varianten):**

> Finvallo – unabhängiger Kreditkartenvergleich für Österreich und Deutschland. Offene Bewertung nach sieben Kriterien, Rechner statt Empfehlungen, keine Finanzberatung.

Die Zeichenzahlen sind inklusive Leerzeichen gezählt.

## Kurz (≤ 50 Zeichen) – 49 Zeichen

Für: X-Name-Zusatz, Instagram-Kategorie/erste Bio-Zeile, Crunchbase „Short Description“ (falls stark begrenzt).

```
Unabhängiger Kreditkartenvergleich für AT und DE.
```

## Mittel (≤ 150 Zeichen) – 145 Zeichen

Für: Instagram-Bio (max. 150), X-Bio (max. 160), LinkedIn-Tagline (max. 120 – dort ggf. die Kurzvariante nehmen), Crunchbase „Short Description“.

```
Finvallo – unabhängiger Kreditkartenvergleich für Österreich und Deutschland. Offene Bewertung nach sieben Kriterien, Rechner statt Empfehlungen.
```

## Lang (≤ 300 Zeichen) – 275 Zeichen

Für: LinkedIn „Info“/Übersicht (Einstieg), Crunchbase „Full Description“ (Einstieg).

```
Finvallo – unabhängiger Kreditkartenvergleich für Österreich und Deutschland. Offene Bewertung nach sieben Kriterien, Rechner statt Empfehlungen, keine Finanzberatung. Rund 77 Karten in Österreich und 165 in Deutschland, Bestenlisten, Ratgeber und Rechner. Betrieben in Wien.
```

## Weitere Profilangaben

- Website: https://finvallo.com
- Kontakt: hallo@finvallo.com
- Standort: Wien, Österreich
- Branche (LinkedIn): Finanzdienstleistungen / Online-Medien – je nach verfügbarer Auswahl

## Nach dem Anlegen: `sameAs` ergänzen

Sobald die Profile angelegt sind, deren URLs in das Array `sameAs` des Organization-JSON-LD auf finvallo.com eintragen, z. B.:

```json
"sameAs": [
  "https://www.linkedin.com/company/<slug>",
  "https://www.crunchbase.com/organization/<slug>",
  "https://x.com/<handle>",
  "https://www.instagram.com/<handle>"
]
```

Nur tatsächlich existierende, öffentlich erreichbare Profil-URLs eintragen.
