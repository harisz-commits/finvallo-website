# hreflang: vorgeschlagene AT↔DE-Paare (zur Freigabe)

Automatisch gepaart werden Seiten mit gleichem Pfad nach `/at/` bzw. `/de/`. Manuelle Paare stehen in `tools/daten/hreflang-map.json` (bisher: Punktesammeln-Ratgeber, Advanzia Gold).

Vorschläge per Namensähnlichkeit (nicht übernommen). Ähnlichkeit 0–1:

| Ähnlichkeit | AT | DE | Einschätzung |
|---|---|---|---|
| 0,80 | /at/kreditkarten/wise-karte/ | /de/kreditkarten/wise-debitkarte/ | wahrscheinlich dasselbe Produkt → Freigabe empfohlen |
| 0,78 | /at/kreditkarten/advanzia-bank-hilton-honors-kreditkarte/ | /de/kreditkarten/hilton-honors-kreditkarte/ | gleiche Karte (Advanzia) → Freigabe empfohlen |
| 0,88 | /at/kreditkarten/oberbank-mastercard-gold/ | /de/kreditkarten/postbank-mastercard-gold/ | verschiedene Banken → nicht paaren |
| 0,78 | /at/kreditkarten/bank-austria-platinum/ | /de/kreditkarten/postbank-mastercard-platinum/ | verschiedene Banken → nicht paaren |
| 0,78 | /at/kreditkarten/oberbank-business-mastercard-klassik/ | /de/kreditkarten/commerzbank-business-card-classic/ | verschiedene Banken → nicht paaren |

Zum Übernehmen das Paar in `tools/daten/hreflang-map.json` unter `paare` eintragen.
