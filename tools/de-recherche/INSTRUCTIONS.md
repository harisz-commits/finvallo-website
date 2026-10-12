# Recherche-Auftrag: Kreditkarten Deutschland für finvallo.com

Du recherchierst die aktuellen Konditionen (Stand Oktober 2026) einer Gruppe deutscher Karten für Neukunden in Deutschland.
Ergebnis: EINE JSON-Datei (Liste von Objekten) unter dem Pfad, der dir im Auftrag genannt wird. Sonst nichts verändern – NICHT im Git-Repo /home/user/finvallo-website arbeiten.

## Quellen-Regeln (wichtig)
- Primärquelle = Preis- und Leistungsverzeichnis (PLV), Konditionsübersicht, AGB/Versicherungsbedingungen oder Produktseite des Anbieters selbst. Immer zuerst dort prüfen.
- Werte, die du NUR bei einem Vergleichsportal/Blog findest, trägst du ein, schreibst aber den Feldnamen in die Liste "sek".
- Erfinde nichts. Unbekannt = null (und nicht in "sek").
- Konditionen für Österreich oder andere Länder NICHT übernehmen.
- Gibt es eine Karte nicht mehr für Neukunden, trag sie mit "status":"eingestellt" und Quelle ein (sonst "status":"aktiv").
- Bietet ein Anbieter deiner Gruppe weitere Privat- oder Business-Kreditkarten in DE an, die nicht in deiner Liste stehen, ergänze sie.
- Als Startpunkt gibt es Portaldaten von finanzfluss.de (Stand 08.10.2026) in
  /tmp/claude-0/-home-user-finvallo-website/3c6f7d7e-62ca-517b-a336-7f6d5fd41c59/scratchpad/de_ff.json (Feld "label"; "plv" = dort verlinktes PLV, oft veraltet). Nur als Hinweis, nicht als Quelle.

## Werkzeuge
- Seiten/PDFs als Text holen: bash /tmp/claude-0/-home-user-finvallo-website/3c6f7d7e-62ca-517b-a336-7f6d5fd41c59/scratchpad/get.sh <name> <url>
  -> legt .../scratchpad/plv/<name>.txt ab (PDF via pdftotext). Nutze eindeutige Namen mit deinem Gruppenpräfix (z. B. grpA_tf_plv).
  Viele Seiten sind JavaScript-lastig: dann WebFetch oder WebSearch nutzen, PDF-Links über WebSearch finden.
- Nutze WebSearch mit mode "standard".

## Was du pro Karte erfasst (JSON-Felder)
key            eindeutiger slug, z. B. "tf-bank-mastercard-gold"
status         "aktiv" | "eingestellt"
anbieter       Marke/Bank wie Kunden sie kennen, z. B. "TF Bank", "American Express", "Deutsche Bank"
herausgeber    ausgebende Bank, falls anders (z. B. "Advanzia Bank" für GMX), sonst null
p              Anbieter-slug, z. B. "tf-bank"
name           Kartenname ohne Anbieter, z. B. "Mastercard Gold"
art            "Privat" | "Business"
typ            "Kreditkarte" (revolvierend, Teilzahlung möglich/voreingestellt) | "Charge" (Monatsrechnung wird komplett abgebucht) | "Debit" | "Prepaid"
klasse         "Basis" | "Std" | "Gold" | "Premium"   (Premium = Platinum/Metal/Black/Ultra o.ä.)
netz           "Visa" | "Mastercard" | "American Express" | "Visa/Mastercard"
fee            Jahresgebühr AB DEM 2. JAHR in € als Zahl, für eine Hauptkarte, OHNE Bedingungen (Monatsgebühr ×12). Ist sie nur unter Bedingung 0 € (z. B. Umsatz, Gehaltseingang, Girokonto-Modell), trag den Preis OHNE Bedingung ein und erklär es in feeNote.
fee1           Gebühr im 1. Jahr, falls abweichend (sonst null)
feeNote        Text, z. B. "4,90 € pro Monat" oder "0 € bei 5.000 € Jahresumsatz, sonst 29 €" oder "nur mit Girokonto XY (… €/Monat)"
konto          falls die Karte nur mit Girokonto/Depot beim Anbieter geht: Name + Kosten des günstigsten Kontomodells, sonst null
fx             Gesamtaufschlag bei Kartenzahlung in US-Dollar in % (Auslandseinsatzentgelt + evtl. Kursaufschlag) als Zahl; 0 wenn kostenlos
fxText         kurzer Text, z. B. "0 %", "1,75 %", "2 % (Amex-Kurs)"
cash           Kosten für eine Abhebung von 200 € am Automaten IM INLAND (Deutschland), kodiert als Liste:
               ["free"] kostenlos | ["free_interest"] kostenlos, aber ab Tag 1 verzinst | ["fix", 3.95] fester Betrag |
               ["pctmin", 2, 5] Prozent mit Mindestbetrag | ["pct", 2] | ["fixpct", fix, pct] | ["freeN", N, danach_eur] N Gratis-Abhebungen/Monat, danach Betrag | ["no"] nicht möglich
cashText       Text für Inland UND Ausland, z. B. "3,95 € im Inland, 0 € im Ausland"
cashInterest   true wenn Bargeld ab Tag 1 verzinst wird, sonst false/null
soll           Sollzins p. a. (Zahl) bei Teilzahlung, sonst null
effz           effektiver Jahreszins (Zahl), sonst null
rahmen         Kreditrahmen-Text, falls bekannt
zinsfrei       max. zinsfreie Tage (Zahl), falls bekannt
giro           true, wenn ein Girokonto/Depot beim Anbieter NÖTIG ist; false wenn ein beliebiges Referenzkonto reicht
auto           true, wenn der Saldo automatisch (Lastschrift/Kontoverrechnung) komplett ausgeglichen werden kann; false wenn nur Überweisung
autoNote       z. B. "Teilzahlung 3 % voreingestellt, auf 100 % umstellbar"
pay            true wenn Apple Pay UND/ODER Google Pay offiziell unterstützt, false wenn nein, null wenn unbekannt
payText        z. B. "Apple Pay und Google Pay"
tier           Reiseversicherung inklusive (ohne Aufpreis):
               0 = keine Reiseversicherung (Einkaufs-/Rückgabeschutz allein zählt nicht)
               1 = Basis (z. B. nur Reiseunfall, nur Auslandskranken, nur Verspätung)
               2 = mit Reiserücktritt (typisches Gold-Paket: Rücktritt/Abbruch + Auslandskranken + Gepäck/Verspätung, OHNE Mietwagen)
               3 = umfassend (Rücktritt + Auslandskranken + Mietwagen-Vollkasko/Selbstbehalt-Ersatz + weitere)
               4 = Premium (Platinum-Niveau: alles aus 3 mit hohen Summen, weltweit, Familie, oft Lounge-Karten)
insText        2–4 Sätze: was ist versichert, wichtigste Summen, Bedingung (z. B. 50 % mit Karte bezahlt), Altersgrenzen, Selbstbehalt
insQuelle      URL der Versicherungsbedingungen/Leistungsübersicht
ex             Objekt mit Extras (nur true setzen, wenn ohne Aufpreis enthalten):
               cb (Cashback oder Bonuspunkte bei normalen Einkäufen, auch Membership Rewards/Payback), lg (kostenlose Lounge-Besuche),
               lgm (nur Lounge-Mitgliedschaft ohne Gratisbesuche), ml (Meilen sammeln), credits (Guthaben/Partner-Abos/Reiseguthaben),
               ft (FastTrack), offer (Aktion/Bonus im 1. Jahr bzw. Willkommensbonus aktuell gültig)
cbText         Text zu Cashback/Punkten (Sammelrate!)
lgText         Text zu Lounge
creditsText    Text zu Guthaben
bonus          aktueller Willkommensbonus (Text inkl. Bedingung und Enddatum), sonst null
extra          Liste kurzer Vorteile (max. 6), z. B. "Partnerkarte kostenlos", "Bargeld bis 1.000 € pro Tag"
cons_extra     Liste kurzer Nachteile (max. 5), z. B. "Teilzahlung ist voreingestellt", "Überweisung vom Kartenkonto kostet 3,95 €"
quelle         URL Produktseite
preis          URL des PLV/Konditionsblatts (PDF), das du gelesen hast
stand          Version/Datum des PLV, z. B. "PLV 07/2026"
sek            Liste der Feldnamen, die nur aus Portalen/Blogs stammen
notiz          freie Notiz für die Redaktion (Widersprüche, Unsicherheiten)

## Qualität
- Lies die Zahlen im PLV wirklich nach (Jahresgebühr, Auslandseinsatz, Bargeld Inland, Zinsen).
- Achte auf Fallen: Monats- statt Jahresgebühr, Gebühr nur im 1. Jahr frei, Wechselkurs-Aufschlag zusätzlich zum Entgelt (z. B. Amex: 2 % Auslandseinsatzentgelt), "kostenlos nur mit Gehaltseingang", Abhebung am Bankschalter vs. Automat.
- Bei Debitkarten von Neobanken: Jahresgebühr = Kontomodell-Preis ×12 (Karte gibt es nur mit Konto) -> giro=true, konto=Name.
- Schreib die Datei zwischendurch (nach jeder 3. Karte) neu, damit nichts verloren geht. Gültiges JSON (UTF-8, ensure_ascii=False).
- Am Ende: kurze Zusammenfassung (Anzahl Karten, welche unsicher/eingestellt, welche ergänzt).
