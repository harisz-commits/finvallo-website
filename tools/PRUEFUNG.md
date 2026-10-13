# Wöchentliche Prüfung der Kreditkarten (jeden Samstag)

Ziel: Alle Konditionen auf finvallo.com stimmen mit den Unterlagen der Anbieter überein, und jede Karte zeigt das echte Datum ihrer letzten Prüfung.

## 1. Vorbereitung
- Repository `harisz-commits/finvallo-website`, Branch `main` aktuell holen.
- Neuen Branch anlegen: `pruefung-JJJJ-MM-TT` (Datum von heute).
- `tools/README.md` lesen.

## 2. Daten prüfen
Daten liegen in:
- Österreich: `tools/daten/at/karten.json` (Anbieter in `tools/daten/at/anbieter.json`)
- Deutschland: `tools/de-recherche/A.json` bis `G.json` und `de_cards.json` (Regeln in `tools/de-recherche/INSTRUCTIONS.md`)

Für jede Karte das Preisverzeichnis (`preis`) und die Produktseite (`quelle`) des Anbieters öffnen und vergleichen:
- Jahresgebühr (`fee`, `fee1`, `feeNote`, bei AT auch `price`/`period`)
- Fremdwährung (`fx`, `fxText`) und Bargeld (`cash`, `cashText`)
- Reiseversicherung (`tier`, Texte in `blocks.ins` bzw. `insText`)
- Zinsen (`soll`, `effz`), Konto nötig (`giro`), Abbuchung (`auto`), Apple/Google Pay (`pay`)
- Lounge (`lgText`, `ex.lg`), Cashback/Punkte/Meilen (`cbText`, `earnText`, `ex.cb`, `ex.ml`; Sammelraten in `tools/sammeln.py`)
- Aktionen (`bonus`, bei AT `offer` mit `end` = TT.MM.JJJJ). Abgelaufene Aktionen entfernen und `fee1` anpassen.
- Gibt es die Karte nicht mehr: bei DE `"status": "eingestellt"`, bei AT `"status": "eingestellt"` setzen (die Seite fällt dann weg).

Regeln:
- Nur Werte ändern, die in Unterlagen des Anbieters stehen. Vergleichsportale und Blogs sind keine Quelle.
- In Datenfelder, die auf der Seite erscheinen, nie interne Notizen schreiben (kein „laut Recherche“, „hochgeladen“, „Portal“, „unklar“ usw.).
- Konnte eine Karte vollständig geprüft werden (auch ohne Änderung): `geprueft` auf das heutige Datum setzen (JJJJ-MM-TT).
- Konnte sie nicht geprüft werden (Seite gesperrt, PDF fehlt): `geprueft` NICHT ändern und die Karte in der Zusammenfassung unter „nicht prüfbar“ aufführen.
- Neue Karten am Markt oder neue Anbieter nur in der Zusammenfassung als Hinweis nennen, nicht selbst anlegen.
- Viele Karten: die Anbieter auf mehrere parallele Agenten verteilen (z. B. je 5 bis 8 Anbieter pro Agent) und die Ergebnisse danach zusammenführen.

## 3. Bauen und prüfen
```
bash tools/build.sh
python3 tools/check.py
```
`check.py` muss „alles in Ordnung“ melden. Sonst Fehler beheben und neu bauen. Nichts veröffentlichen, solange Fehler gemeldet werden.

## 4. Veröffentlichen zur Freigabe
- Commit auf dem Branch `pruefung-JJJJ-MM-TT`, pushen.
- Pull Request gegen `main` erstellen, Titel: `Wochenprüfung TT.MM.JJJJ: X Änderungen`.
- Im PR-Text auf Deutsch:
  1. Tabelle der Änderungen: Karte | Feld | alt | neu | Quelle (Link)
  2. Liste „nicht prüfbar“ mit Grund
  3. Hinweise: neue Karten, eingestellte Karten, auffällige Änderungen bei Bestenlisten-Platz 1
- Den PR NICHT selbst mergen. Der Inhaber gibt frei, danach geht die Seite automatisch live (Server holt `main` alle 5 Minuten).
- Gab es keine einzige Änderung, trotzdem einen PR erstellen (die Prüfdaten sind neu).

## 5. Abschluss
Zum Schluss eine kurze Zusammenfassung auf Deutsch ausgeben: Anzahl geprüfter Karten, Anzahl Änderungen, die wichtigsten Änderungen, nicht prüfbare Karten und den Link zum PR.
