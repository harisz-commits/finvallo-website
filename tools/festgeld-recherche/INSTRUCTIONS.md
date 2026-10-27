# Recherche-Auftrag: Festgeld Deutschland und Österreich für finvallo.com

Du recherchierst die aktuellen Festgeld-Konditionen (Stand Oktober 2026) einer Gruppe von Banken bzw. einer Plattform.
Ergebnis: EINE JSON-Datei (Liste von Objekten) unter `tools/festgeld-recherche/<GRUPPE>.json` im Repo `/home/user/finvallo-website`.
Sonst im Repo nichts ändern, nichts committen, nichts pushen. Zwischendateien (Seiten-Texte, PDFs) nur im Scratchpad deiner Sitzung.

## Was zählt als Festgeld
- Einlage mit fester Laufzeit und festem Zins: Festgeld, Termingeld, Sparbrief, Festzins-Sparen, Kapitalsparbuch/Kapitalsparkonto mit Bindung (AT), „Online Sparen fix“ o. ä.
- NICHT: Tagesgeld, Sparbuch ohne Bindung, Zuwachssparen mit variablem Zins, Fonds, Anleihen, Bausparen, Kinder-Sparpläne, Angebote nur für Firmenkunden.
- Nur Angebote für Privatkunden mit Wohnsitz im Zielmarkt (`markt`: "de" = Deutschland, "at" = Österreich). Ein Angebot, das es in beiden Märkten gibt, wird zweimal erfasst (je Markt ein Objekt).
- Regionale Banken, die nur Kundschaft aus ihrer Region nehmen (Sparkassen, Volks- und Raiffeisenbanken, Sparda, PSD), NICHT erfassen. Überregionale Online-Angebote regionaler Institute (z. B. Online-Marken, die bundesweit eröffnen) schon.

## Quellen-Regeln (wichtig)
- Primärquelle = Konditionsseite, Zinsübersicht, Preisaushang, Preis- und Leistungsverzeichnis, Informationsbogen für den Einleger oder Produktseite der Bank bzw. der Plattform, über die das Angebot läuft. Immer zuerst dort prüfen.
- Werte, die du NUR bei einem Vergleichsportal/Blog findest, trägst du ein, schreibst aber den Feldnamen in die Liste `sek`.
- Erfinde nichts. Unbekannt = null. Lieber ein Angebot weglassen (mit Grund in `nicht_aufgenommen`) als raten.
- Zinsen ändern sich oft. Trag die Zinsen ein, die die Quelle HEUTE für Neuanlagen zeigt, und das Datum in `stand`.
- Aktionszinsen nur für Neukunden: als normale Zinsen erfassen, aber `neukunden_only: true` und Text in `aktion`.

## Werkzeuge
- Seiten als Text: `curl -sL -A "Mozilla/5.0" <url>` (HTML) bzw. PDFs herunterladen und mit `pdftotext -layout` lesen. Viele Seiten sind JavaScript-lastig: dann WebFetch (über ToolSearch laden) oder nach einer JSON-API der Seite suchen (Netzwerk-Aufrufe im HTML, `__NEXT_DATA__`, `/api/`), oder WebSearch (mode "standard").
- Bei Plattformen (Raisin/WeltSparen, Zinspilot, Check24, Verivox, ZinsMarkt) lohnt fast immer die Suche nach der JSON-Schnittstelle, die die Angebotsliste lädt.

## Felder pro Angebot (JSON)
```
id                eindeutiger slug: "<bank>-<produkt>-<markt>[-<vertrieb>]", z. B. "volkswagen-bank-festgeld-de", "bigbank-festgeld-at-raisin"
markt             "de" | "at"   (für Kundinnen und Kunden welchen Landes)
bank              Bank, wie Kunden sie kennen, z. B. "Volkswagen Bank", "Bigbank"
institut          rechtlicher Name der Einlagenbank, z. B. "Volkswagen Bank GmbH", "Bigbank AS"
produkt           Produktname, z. B. "Festgeld", "Sparbrief", "Kapitalsparbuch", "Festzins-Anlage"
vertrieb          "direkt" (bei der Bank selbst) | "Raisin" | "Zinspilot" | "Check24" | "Verivox" | "ZinsMarkt" | "andere: <Name>"
vertrieb_url      URL, über die man abschließt (Plattform-Produktseite oder Bankseite)
sitz              ISO-Land der Einlagenbank bzw. der Einlagensicherung, z. B. "DE", "AT", "EE", "FR"
zweigniederlassung true, wenn das Angebot über eine Zweigniederlassung im Zielmarkt läuft, die Einlagen aber nach dem Recht des Heimatlands gesichert sind
einlagensicherung { "system": z. B. "Entschädigungseinrichtung deutscher Banken (EdB)", "betrag": 100000,
                    "freiwillig": Text zur zusätzlichen freiwilligen Sicherung oder null }
zinsen            Liste aller angebotenen Laufzeiten:
                  [ { "monate": 12, "zins": 2.10, "min": null, "max": null } , ... ]
                  monate = Laufzeit in Monaten (1 Woche = 0.25, 1 Monat = 1, 3 Jahre = 36).
                  zins = Zinssatz p. a. in Prozent als Zahl (nominal, wie die Bank angibt).
                  Hängt der Zins vom Betrag ab: je Stufe ein eigener Eintrag mit min/max (€) für diese Stufe; sonst min/max null.
min_anlage        Mindestanlage in € (Zahl) oder null
max_anlage        Höchstanlage in € (Zahl) oder null (unbegrenzt = null, im Text erwähnen)
zinszahlung       "jaehrlich" | "endfaellig" | "monatlich" | "quartalsweise" | "halbjaehrlich" | "wahlweise"
zinszahlung_text  kurzer Text, z. B. "jährlich, bei Laufzeiten unter 12 Monaten am Ende"
zinseszins        true, wenn jährliche Zinsen bei mehrjähriger Laufzeit mitverzinst (thesauriert) werden; false wenn ausgezahlt; null unbekannt
steuer            Text: wie werden Steuern behandelt? DE: zieht die Bank Abgeltungsteuer ab, Freistellungsauftrag möglich? AT: wird KESt (25 %) automatisch abgeführt (Endbesteuerung) oder muss man die Zinsen selbst in der Steuererklärung angeben? Ausländische Quellensteuer?
steuer_auto       true, wenn die Steuer automatisch abgeführt wird (Abgeltungsteuer bzw. KESt), false wenn selbst zu erklären, null unbekannt
kuendigung        "nein" | "ja" | "ja_mit_abschlag" – vorzeitige Auflösung möglich?
kuendigung_text   Text zur vorzeitigen Verfügung (z. B. "nicht möglich", "möglich mit Vorschusszinsen 1 % p. a.")
verlaengerung     "automatisch" | "keine" | "wahlweise"  – was passiert am Laufzeitende?
konto_noetig      Text, falls ein weiteres Konto bei Bank/Plattform nötig ist (z. B. "kostenloses Tagesgeldkonto als Verrechnungskonto", "Raisin-Konto (kostenlos)"), sonst null
referenzkonto     true, wenn Auszahlung auf ein beliebiges eigenes Referenzkonto geht
neukunden_only    true | false | null
gemeinschaftskonto true | false | null
eroeffnung        "online" | "filiale" | "beides"
legitimation      z. B. "VideoIdent oder PostIdent", "ID Austria", "Filiale"
kosten            Kontoführungskosten (meist "kostenlos") oder Text
aktion            Text zu Aktionen/Boni oder null
quelle            URL der Primärquelle mit den Zinsen
quelle2           weitere URL (Konditionen/Preisverzeichnis/Informationsbogen) oder null
stand             Datum der Zinsangabe in der Quelle (YYYY-MM-DD), sonst heutiges Datum
geprueft          heutiges Datum (YYYY-MM-DD)
status            "ok" | "eingestellt" (kein Neugeschäft)
hinweis           1–2 Sätze Wichtiges (z. B. "Zins nur über die App", "Anlage nur in Schritten von 1.000 €") oder null
sek               Liste der Feldnamen, die NUR aus Sekundärquellen stammen ([] wenn keine)
```

Am Ende der Datei KEINE weiteren Objekte außer Angeboten. Angebote, die du bewusst nicht aufnimmst, schreibst du in eine zweite Datei
`tools/festgeld-recherche/<GRUPPE>-nicht-aufgenommen.json` als Liste `[{"name": "...", "markt": "de", "grund": "..."}]`.

## Abschluss
- Prüfe die Datei mit `python3 -c "import json;d=json.load(open('tools/festgeld-recherche/<GRUPPE>.json'));print(len(d))"`.
- Deine Antwort an den Auftraggeber: NUR eine kurze Zusammenfassung (Anzahl Angebote, Anzahl nicht aufgenommen, auffällige Probleme). KEINE Zinstabellen, keine Daten im Chat.
