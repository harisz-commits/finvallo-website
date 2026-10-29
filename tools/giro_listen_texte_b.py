# Erklärtexte für die Girokonto-Bestenlisten: unterkonten, ohne-schufa / ohne-ksv, direktbanken, neobanken, nachhaltige-banken.
# Aufruf aus girokonto.texte(): texte(land, ctx) -> {slug: {'lede', 'secs', 'faq'}}.
# Alle Aussagen über konkrete Konten kommen aus ctx; feste Zahlen nur für Gesetze und Allgemeines.
import html, statistics

E = html.escape


# ---------- Helfer ----------
def _p(*xs):
    o = ''
    for x in xs:
        if not x:
            continue
        o += x if x.lstrip().startswith(('<ul', '<ol', '<h3', '<p>', '<p ')) else f'<p>{x}</p>'
    return f'<div class="prose">{o}</div>'


def _ul(*xs, tag='ul'):
    return f'<{tag}>' + ''.join(f'<li>{x}</li>' for x in xs if x) + f'</{tag}>'


def _ol(*xs):
    return _ul(*xs, tag='ol')


def _tbl(head, rows):
    if not rows:
        return ''
    h = ''.join(f'<th>{x}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f'<td>{x}</td>' for x in r) + '</tr>' for r in rows)
    return f'<div class="tbl wide"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


def _a(u, t):
    return f'<a href="{E(u)}" target="_blank" rel="noopener">{E(t)}</a>'


def _k(k):
    return k['score']['kosten']['total']


def _kt(c, k):
    return c['eur'](_k(k)) + ' €'


def _n(n, a, b):
    return f'{n} {a if n == 1 else b}'


def _und(xs):
    xs = [x for x in xs if x]
    if not xs:
        return ''
    return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' und ' + xs[-1]


def _banken(X):
    out = []
    for k in X:
        if k['bank'] not in out:
            out.append(k['bank'])
    return out


def _med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def _dz(c, k):
    s = k.get('sollzins')
    return c['pct'](s) if s is not None else 'keine Angabe'


def _quellen(c, links, X, intro=None):
    seen, bl = set(), []
    for k in X:
        if k['bank'] in seen or not k.get('quelle'):
            continue
        seen.add(k['bank'])
        bl.append(_a(k['quelle'], f'Preise und Bedingungen bei {k["bank"]}'))
        if len(bl) >= 10:
            break
    return _p(intro or '', _ul(*[_a(u, t) for u, t in links], *bl))


_LAND = {'DE': 'Deutschland', 'AT': 'Österreich', 'LT': 'Litauen', 'NL': 'Niederlande', 'FR': 'Frankreich', 'ES': 'Spanien',
         'BE': 'Belgien', 'LU': 'Luxemburg', 'IE': 'Irland', 'IT': 'Italien'}


def _es_land(k):
    t = (k.get('einlagensicherung') or '').lower()
    for key, land in (('litau', 'Litauen'), ('niederl', 'Niederlande'), ('franz', 'Frankreich'), ('österreich', 'Österreich'),
                      ('austria', 'Österreich'), ('raiffeisen-sicherung', 'Österreich'), ('deutsch', 'Deutschland'), ('edb', 'Deutschland'),
                      ('bvr', 'Deutschland'), ('sparkassen', 'Deutschland'), ('einsig', 'Deutschland')):
        if key in t:
            return land
    return ''


def _es(k):
    t = (k.get('einlagensicherung') or '').lower()
    land = _es_land(k)
    s = f'gesetzliche Einlagensicherung {land}' if land else 'laut Konditionen der Bank'
    if 'treuhand' in t:
        s += ', Guthaben teils auf Treuhandkonten bei Partnerbanken'
    if 'kontoführung durch' in t:
        s += ', Konto bei einer Partnerbank geführt'
    return s


def _ibanT(code):
    return f'{_LAND.get(code, code)} ({code})' if code else 'keine Angabe'


def _neo_rows(c, X):
    by = {}
    for k in X:
        by.setdefault(k['bank'], []).append(k)
    rows = []
    for b, ks in by.items():
        ib = sorted({k.get('iban') or '' for k in ks} - {''})
        ab = min(ks, key=lambda k: k['kf_jahr'])
        rows.append([E(b), ', '.join(_ibanT(i) for i in ib) or 'keine Angabe', _es(ks[0]), str(len(ks)), E(c['kfT'](ab))])
    return rows, by


def _tarife(c, X):
    """Gratis-Tarife und Bezahltarife einer Liste."""
    frei = [k for k in X if k['kf_jahr'] == 0]
    bez = [k for k in X if k['kf_jahr'] > 0]
    frei_teuer = [k for k in frei if _k(k) > 0]
    return frei, bez, frei_teuer


def _eingang(X):
    xs = [k['gratis']['eingang_min'] for k in X if k.get('gratis') and k['gratis'].get('eingang_min')]
    return (min(xs), max(xs)) if xs else None


def _vgl_satz(c, a, b, wer):
    if a == 0:
        return f'Mindestens die Hälfte der Standardkonten {wer} kostet im Standardfall nichts, bei den Standardkonten der Banken mit Filialen in unserem Vergleich liegt der Median bei {c["eur"](b)} € im Jahr.'
    return f'Im Standardfall kosten die Standardkonten {wer} im Mittel (Median) {c["eur"](a)} € im Jahr, die Standardkonten der Banken mit Filialen in unserem Vergleich {c["eur"](b)} €.'


def _filial_std(c, ausser):
    return [k for k in c['alle'] if k['art'] == 'standard' and k['bank'] not in ausser and k.get('eroeffnung') in ('filiale', 'beides')]


# ---------- Unterkonten ----------
def _uk_daten(c):
    X = c['lists'].get('unterkonten') or []
    if not X:
        return None
    n = len(X)
    b = len(_banken(X))
    iban = [k for k in X if k.get('unterkonten_iban')]
    ints = [k['unterkonten'] for k in X if isinstance(k.get('unterkonten'), int) and not isinstance(k.get('unterkonten'), bool)]
    mx = max(ints) if ints else None
    top = [k for k in X if mx and k.get('unterkonten') == mx]
    billig = min(X, key=_k)
    frei = [k for k in X if _k(k) == 0]
    s = f'In der Liste stehen {_n(n, "Konto", "Konten")} von {_n(b, "Bank", "Banken")}. '
    if mx and 1 < mx < 50:
        s += f'Die meisten Unterkonten, bis zu {mx}, bietet {_und([c["link"](k) for k in top[:3]])}. '
    elif mx and mx >= 50:
        s += f'Die meisten Unterkonten bietet {_und([c["link"](k) for k in top[:3]])}. '
    s += f'Im Standardfall am günstigsten ist {c["link"](billig)} mit {_kt(c, billig)} im Jahr'
    s += (f'. {_n(len(frei), "Konto kostet", "Konten kosten")} dich im Standardfall gar nichts.' if len(frei) > 1 else '.')
    rows = [[c['link'](k), E(c['ukT'](k)), E(c['kfT'](k)), _kt(c, k)] for k in X]
    return dict(X=X, n=n, iban=iban, s=s, rows=rows)


def _unterkonten_de(c):
    d = _uk_daten(c)
    secs = []
    secs.append(('Wofür Unterkonten gut sind', _p(
        'Ein Unterkonto ist ein zweiter Topf innerhalb deines Girokontos. Das Geld bleibt bei derselben Bank, du siehst alles in einer App, aber es liegt getrennt vom Hauptkonto. Was dort liegt, gibst du nicht aus Versehen im Supermarkt aus.',
        'Das klingt banal, wirkt aber. Wer nur ein Konto hat, sieht am Monatsanfang einen hohen Kontostand und unterschätzt, was davon schon verplant ist: Miete, Strom, Versicherungen, Handyvertrag, das Abo fürs Fitnessstudio. Mit Unterkonten schiebst du diese Beträge direkt nach dem Gehaltseingang beiseite. Was auf dem Hauptkonto bleibt, darfst du ausgeben.',
        'Ein Beispiel: Du bekommst 2.300 € netto. Am Gehaltstag gehen per Dauerauftrag 1.050 € auf ein Unterkonto für Fixkosten, 200 € auf eines für Urlaub und 150 € auf eines für den Notgroschen. Auf dem Hauptkonto bleiben 900 € für Essen, Freizeit und alles andere. Du siehst jeden Tag, wie viel davon noch übrig ist, ohne eine Tabelle zu führen.',
        'Unterkonten ersetzen kein Haushaltsbuch, aber sie nehmen dir einen großen Teil der Arbeit ab. Und sie machen sichtbar, wofür du sparst. Ein Topf namens „Auto-Reparatur“ fühlt sich anders an als eine anonyme Zahl auf dem Sparkonto. Die Hemmschwelle, ihn für einen spontanen Einkauf zu plündern, ist höher.')))
    secs.append(('Echtes Unterkonto mit IBAN oder nur ein Space?', _p(
        'Banken nutzen die Begriffe nicht einheitlich. Mal heißt es Unterkonto, mal Space, Pocket, Topf oder Zweitkonto. Für dich zählt eine Frage: Hat das Unterkonto eine eigene IBAN oder nicht?',
        'Ein Unterkonto mit eigener IBAN ist rechtlich ein eigenes Zahlungskonto. Du kannst dir dorthin Geld überweisen lassen, Lastschriften darauf laufen lassen und es Vermieter oder Versicherung als Bankverbindung angeben. Es bekommt einen eigenen Kontoauszug.',
        'Ein Space ohne eigene IBAN ist dagegen eher eine Markierung in der App. Das Geld liegt technisch auf deinem Hauptkonto, die Bank zeigt es dir nur getrennt an. Zahlungen von außen landen immer auf dem Hauptkonto, du verschiebst sie dann per Fingertipp. Für Budget und Sparziele reicht das völlig.')
        + _tbl(['Merkmal', 'Unterkonto mit eigener IBAN', 'Space ohne eigene IBAN'], [
            ['Geld von außen empfangen', 'ja, direkt', 'nein, nur über das Hauptkonto'],
            ['Lastschriften für Miete, Strom, Versicherung', 'ja, direkt vom Unterkonto', 'nein, sie laufen über das Hauptkonto'],
            ['Eigener Kontoauszug', 'ja', 'meist nicht'],
            ['Geld zwischen den Töpfen verschieben', 'sofort, innerhalb der Bank', 'sofort, in der App'],
            ['Als Bankverbindung weitergeben', 'ja', 'nein'],
        ])
        + _p('Wenn du nur sparen und budgetieren willst, reichen Spaces. Wenn Fixkosten automatisch von einem eigenen Topf abgehen sollen, brauchst du echte Unterkonten mit IBAN. Dann merkst du sofort, wenn das Geld für die Fixkosten nicht reicht, statt dass eine Lastschrift still dein Freizeitbudget anknabbert.',
             f'Bei {len(d["iban"])} der {d["n"]} Konten in unserer Liste hat jedes Unterkonto laut Bank eine eigene IBAN.' if d and d['iban'] else '')))
    if d:
        secs.append(('Die Unterkonten der Konten in unserer Liste', _p(d['s'])
                     + _tbl(['Konto', 'Unterkonten laut Bank', 'Kontoführung', 'Kosten im Jahr (Standardfall)'], d['rows'])
                     + _p('Die Kosten im Jahr beziehen sich auf unseren Standardfall aus der Methodik, also Kontoführung, Karte und typische Nutzung. Was die Bank zu Zahl, IBAN und Preis der Unterkonten angibt, steht in der zweiten Spalte.')))
    secs.append(('Was Unterkonten kosten', _p(
        'Es gibt drei Preismodelle. Erstens: Unterkonten sind im Kontomodell inklusive, oft mit einer festen Höchstzahl. Zweitens: Jedes weitere Konto kostet extra, zum Beispiel ein paar Euro im Monat. Drittens: Die Zahl der Unterkonten hängt vom Tarif ab. Im Gratis-Tarif gibt es wenige, im Premium-Tarif mehr.',
        'Rechne deshalb nicht nur mit der Kontoführung des Hauptkontos. Kostet der größere Tarif 5 € mehr im Monat, sind das 60 € im Jahr, nur damit du mehr Töpfe hast. Frag dich ehrlich, ob du fünf Töpfe brauchst oder ob drei auch reichen.',
        'Bei Unterkonten mit eigener IBAN schau zusätzlich auf diese Posten: Kosten für eine zweite Karte, Gebühren für Lastschriften oder Überweisungen vom Unterkonto und eine eigene Kontoführungsgebühr pro Unterkonto. Bei Spaces fällt das meist weg, weil es technisch ein Konto bleibt.',
        'Eine Alternative für Rücklagen ist ein kostenloses Tagesgeldkonto. Das ist kein Unterkonto, bringt aber oft Zinsen. Für Geld, an das du selten ranmusst, ist das häufig die bessere Lösung. Für ein Budget im Alltag ist es zu umständlich, weil du Geld nur über dein Referenzkonto hin- und herschieben kannst.',
        f'Kostenlose Hauptkonten findest du in der Liste {c["liste"]("kostenlos", "kostenlose Girokonten")}.')))
    secs.append(('So nutzt du Unterkonten im Alltag', _p(
        _ul('<b>Fixkosten-Konto.</b> Alle Lastschriften laufen hier. Am Gehaltstag füllst du es mit der Summe deiner festen Kosten plus einem kleinen Puffer. Jährliche Beiträge wie Kfz-Versicherung oder Haftpflicht teilst du durch zwölf und legst den Betrag jeden Monat dazu. Dann trifft dich die Rechnung im Januar nicht unvorbereitet.',
            '<b>Notgroschen.</b> Eine verbreitete Faustregel sind drei Monatsausgaben, bei unsicherem Job oder Selbstständigkeit eher sechs. Dieser Topf ist für die kaputte Waschmaschine, nicht für den Urlaub. Gib ihm einen klaren Namen und rühr ihn nur im Notfall an.',
            '<b>Sparziele.</b> Urlaub, neues Fahrrad, Geschenke zu Weihnachten. Ein Topf pro Ziel, gefüllt mit einem festen Betrag per Dauerauftrag. Viele Apps zeigen einen Fortschrittsbalken. Das motiviert mehr, als man denkt.',
            f'<b>Gemeinsame Ausgaben.</b> Wenn ihr als Paar oder WG Miete und Einkauf teilt, zahlt jeder einen festen Betrag auf einen gemeinsamen Topf. Manche Banken erlauben geteilte Unterkonten, bei anderen brauchst du dafür ein {c["liste"]("gemeinschaftskonto", "Gemeinschaftskonto")}.',
            f'<b>Steuern bei Nebeneinkünften.</b> Wer nebenbei selbstständig etwas verdient, legt einen Teil jeder Einnahme für Einkommensteuer und gegebenenfalls Umsatzsteuer beiseite. Ein eigener Topf verhindert, dass dieses Geld im Alltag verschwindet. Mehr dazu im Ratgeber {c["rg"]("konto-selbststaendige", "Konto für Selbstständige")}.'),
        'Bleib bei wenigen Töpfen. Drei bis fünf reichen den meisten Menschen. Wer zwanzig Töpfe mit je 30 € führt, verliert den Überblick wieder und verbringt mehr Zeit mit Umbuchen als mit Leben.',
        'Praktisch sind Regeln, die von allein laufen: ein Dauerauftrag am Tag nach dem Gehaltseingang, Aufrunden bei Kartenzahlungen oder ein fester Prozentsatz jedes Eingangs. Welche Automatiken es gibt, unterscheidet sich stark zwischen den Banken.')))
    secs.append(('Zinsen, Steuern und Einlagensicherung', _p(
        'Einige Banken zahlen auf Unterkonten Zinsen, manchmal nur in bestimmten Tarifen. Für die Steuer ist egal, in welchem Topf das Geld liegt: Zinsen sind Kapitalerträge. Bis zum Sparerpauschbetrag von 1.000 € im Jahr pro Person, 2.000 € bei Zusammenveranlagung, bleiben sie steuerfrei, wenn du der Bank einen Freistellungsauftrag erteilst. Darüber zieht die Bank Abgeltungsteuer von 25 % plus Solidaritätszuschlag und gegebenenfalls Kirchensteuer ab.',
        'Sitzt die Bank im Ausland, zieht sie meist keine deutsche Steuer ab und nimmt keinen Freistellungsauftrag an. Dann trägst du die Zinsen selbst in der Anlage KAP deiner Steuererklärung ein.',
        f'Bei der Einlagensicherung zählt die Bank, nicht das einzelne Konto. Hauptkonto, Unterkonten und Tagesgeld bei derselben Bank sind zusammen bis 100.000 € pro Person gesetzlich geschützt. Liegt bei dir mehr bei einer Bank, verteilst du es besser auf mehrere Institute. Mehr dazu im Ratgeber {c["rg"]("einlagensicherung", "Einlagensicherung")}.')))
    secs.append(('Typische Fehler und wie du sie vermeidest', _p(
        'Unterkonten funktionieren nur, wenn das System zu deinem Leben passt. Diese Stolpersteine sehen wir am häufigsten:',
        _ul('<b>Der Puffer fehlt.</b> Ist das Fixkostenkonto exakt auf die Summe der Lastschriften gefüllt, reicht eine Preiserhöhung beim Strom, und eine Lastschrift platzt. Leg 5 bis 10 % mehr hinein, als du rechnerisch brauchst.',
            '<b>Lastschriften vergessen.</b> Wer Unterkonten mit eigener IBAN einführt, muss den Zahlungspartnern die neue IBAN mitteilen. Das passiert nicht von allein. Geh die Kontoauszüge der letzten zwölf Monate durch, damit du auch jährliche Abbuchungen wie den Rundfunkbeitrag oder die Hausratversicherung erwischst.',
            '<b>Minus im Hauptkonto, Guthaben im Topf.</b> Bei manchen Banken rutscht das Hauptkonto in den Dispo, obwohl in einem Topf genug Geld liegt. Dann zahlst du Zinsen auf dein eigenes Geld. Prüf, ob die Bank Töpfe automatisch ausgleicht, und behalte das Hauptkonto im Blick.',
            '<b>Der Notgroschen ist zu leicht erreichbar.</b> Ein Topf, den du per Fingertipp leerst, wird schneller geplündert. Manche legen die Notreserve deshalb bewusst auf ein Tagesgeldkonto bei einer anderen Bank, wo eine Überweisung einen Tag dauert.',
            '<b>Keine Regel für Überschüsse.</b> Bleibt am Monatsende etwas auf dem Hauptkonto, entscheide vorher, wohin es geht, etwa zur Hälfte in den Notgroschen und zur Hälfte in ein Sparziel.'),
        'Zieh nach drei Monaten Bilanz. Passen die Beträge? Ist ein Topf ständig leer, ist der Betrag zu klein oder das Ziel zu groß. Pass die Daueraufträge an, statt jeden Monat von Hand umzubuchen. Nach einem halben Jahr läuft das System bei den meisten von allein.')))
    secs.append(('Checkliste vor der Kontoeröffnung', _p(
        _ul('Brauchst du eine eigene IBAN pro Topf, weil Lastschriften direkt davon abgehen sollen, oder reichen Spaces?',
            'Wie viele Unterkonten gibt es in dem Tarif, den du wirklich nutzen willst, und was kostet jedes weitere?',
            'Kannst du Daueraufträge und Regeln zwischen den Töpfen anlegen?',
            'Lassen sich Unterkonten mit anderen Personen teilen?',
            'Gibt es Zinsen, und gelten sie für alle Töpfe oder nur für bestimmte?',
            'Kannst du ein Unterkonto jederzeit schließen, ohne das Hauptkonto zu kündigen?',
            'Bekommst du für jedes Unterkonto einen eigenen Auszug? Für Nebenkostenabrechnung oder Steuererklärung ist das praktisch.'),
        f'Wenn du schon ein Konto hast und nur wegen der Unterkonten wechseln willst: Die Kontowechselhilfe nach dem Zahlungskontengesetz nimmt dir das Umstellen von Daueraufträgen und Lastschriften ab. Wie das geht, steht im Ratgeber {c["rg"]("girokonto-wechseln", "Girokonto wechseln")}.')))
    secs.append(('Quellen', _quellen(c, [
        ('https://www.gesetze-im-internet.de/zkg/', 'Zahlungskontengesetz (ZKG)'),
        ('https://www.gesetze-im-internet.de/estg/__20.html', 'Einkommensteuergesetz § 20: Kapitalerträge und Sparerpauschbetrag'),
        ('https://www.edb-banken.de/', 'Entschädigungseinrichtung deutscher Banken'),
        ('https://www.bafin.de/', 'Bundesanstalt für Finanzdienstleistungsaufsicht (BaFin)'),
        ('https://www.verbraucherzentrale.de/', 'Verbraucherzentralen'),
    ], d['X'] if d else [])))
    faq = [
        ('Kann ich mir mein Gehalt direkt auf ein Unterkonto überweisen lassen?', 'Nur wenn das Unterkonto eine eigene IBAN hat. Dann gibst du deinem Arbeitgeber einfach diese IBAN. Bei Spaces ohne eigene IBAN geht das Gehalt aufs Hauptkonto. Du kannst dann einen Dauerauftrag oder eine Regel einstellen, die einen Teil am selben Tag weiterschiebt.'),
        ('Kann ich bei einer Sparkasse oder Volksbank auch Unterkonten anlegen?', 'Ja, die meisten Filialbanken eröffnen dir auf Wunsch ein zweites Girokonto oder ein Sparkonto. Das zweite Girokonto kostet aber oft eine eigene Kontoführungsgebühr. Frag nach dem Preis, bevor du mehrere Konten eröffnest.'),
        ('Ist Geld auf einem Unterkonto vor einer Pfändung geschützt?', f'Nein. Gläubiger können alle Konten pfänden, auch Unterkonten. Geschützt ist nur ein Pfändungsschutzkonto, und davon darfst du nur eines haben (§ 850k ZPO). Mehr im Ratgeber {c["rg"]("p-konto", "P-Konto")}.'),
        ('Was passiert mit den Unterkonten, wenn ich mein Girokonto kündige?', 'Meist kündigst du alles zusammen. Die Bank überweist das Guthaben aller Töpfe auf ein Konto deiner Wahl. Stell vorher alle Lastschriften um, die auf einem Unterkonto mit eigener IBAN laufen, sonst platzen sie.'),
        ('Darf ich ein privates Unterkonto für mein Gewerbe nutzen?', 'Das hängt von den Bedingungen der Bank ab. Viele private Girokonten sind laut AGB nur für private Zwecke gedacht. Bei kleinen Nebeneinnahmen drücken Banken oft ein Auge zu, verlassen kannst du dich darauf nicht. Für ein Gewerbe ist ein eigenes Geschäftskonto die saubere Lösung.'),
    ]
    lede = 'Unterkonten trennen dein Geld nach Zweck, ohne dass du ein zweites Konto bei einer anderen Bank brauchst. Hier siehst du, welche Girokonten das können, wo jedes Unterkonto eine eigene IBAN hat und was du dafür zahlst.'
    return dict(lede=lede, secs=secs, faq=faq)


def _unterkonten_at(c):
    d = _uk_daten(c)
    secs = []
    secs.append(('Ein Konto, mehrere Töpfe', _p(
        'Stell dir dein Girokonto als Geldbörse mit mehreren Fächern vor. Im Hauptfach liegt, was du im Alltag mit der Bankomatkarte ausgibst. In den anderen Fächern liegt Geld, das schon verplant ist oder das du bewusst zur Seite legst. Genau das sind Unterkonten: getrennte Bereiche bei derselben Bank, die du in einer App verwaltest.',
        'In Österreich ist das besonders praktisch wegen des 13. und 14. Gehalts. Urlaubs- und Weihnachtsgeld kommen auf einen Schlag und sind ebenso schnell weg, wenn sie am Hauptkonto liegen. Schiebst du einen Teil davon sofort in einen eigenen Topf, finanzierst du damit die großen Brocken des Jahres: Kfz-Versicherung, Pickerl und Service, die Jahresabrechnung für Strom und Gas, Geschenke.',
        'So kann das aussehen: 2.100 € netto im Monat. 780 € gehen per Dauerauftrag auf ein Fixkostenkonto für Miete, Strom, ORF-Beitrag, Handy und Versicherungen. 150 € kommen in den Topf „Notreserve“, 120 € in „Urlaub“. Rund 1.050 € bleiben für den Alltag.',
        'Ab diesem Moment siehst du am Hauptkonto nur noch, was du wirklich ausgeben kannst. Das ist der ganze Trick. Du musst nicht jede Rechnung im Kopf haben, weil das Geld dafür schon woanders liegt.',
        'Unterkonten sind kein neues Produkt. Klassische Banken bieten seit langem Zweitkonten an, nur waren die oft umständlich und kosteten ein eigenes Entgelt. Neu ist, dass Apps sie bequem machen: Ein neuer Topf ist in Sekunden angelegt, Geld in Echtzeit verschoben.')))
    secs.append(('Eigene IBAN oder nur virtuelle Töpfe', _p(
        'Bei österreichischen Banken heißt ein echtes Unterkonto oft schlicht zweites Konto oder Zusatzkonto. Es hat eine eigene IBAN, eigene Kontoauszüge und kann Lastschriften und Überweisungen empfangen. Neobanken nennen ihre Töpfe Spaces, Pockets oder Unterkonten, und nicht alle haben eine eigene IBAN.',
        'Den Unterschied merkst du bei Lastschriften. Strom, Miete oder Versicherung buchen per SEPA-Lastschrift ab. Das geht nur von einem Konto mit eigener IBAN. Ein virtueller Topf ohne IBAN kann das nicht, die Abbuchung läuft immer übers Hauptkonto.',
        f'Achte bei ausländischen Anbietern auch darauf, welche IBAN die Unterkonten bekommen. Eine deutsche, niederländische oder litauische IBAN ist im SEPA-Raum gleichwertig, wird aber nicht überall reibungslos akzeptiert. Mehr dazu in der Liste {c["liste"]("neobanken", "Neobanken")}.')
        + _tbl(['Was du vorhast', 'Reicht ein virtueller Topf?', 'Eigene IBAN nötig?'], [
            ['Urlaubsgeld beiseitelegen', 'ja', 'nein'],
            ['Notreserve getrennt halten', 'ja', 'nein'],
            ['Miete und Strom automatisch von einem eigenen Topf abbuchen lassen', 'nein', 'ja'],
            ['Haushaltsbeitrag vom Partner oder der Partnerin direkt empfangen', 'nein', 'ja'],
            ['Einnahmen aus einem Nebenjob getrennt sammeln', 'eher nein', 'ja'],
        ])
        + _p(f'In unserer Liste hat bei {len(d["iban"])} der {d["n"]} Konten jedes Unterkonto laut Bank eine eigene IBAN.' if d and d['iban'] else '')))
    if d:
        secs.append(('So sieht es bei den Konten in der Liste aus', _p(d['s'])
                     + _tbl(['Konto', 'Unterkonten laut Bank', 'Kontoführungsentgelt', 'Kosten im Jahr (Standardfall)'], d['rows'])
                     + _p('Die Jahreskosten stammen aus unserem Standardfall, wie in der Methodik beschrieben: Kontoführungsentgelt, Karte und übliche Nutzung. Was die Bank selbst zu ihren Unterkonten sagt, findest du in der zweiten Spalte.')))
    secs.append(('Welche Kosten du einrechnen solltest', _p(
        'Viele Banken in Österreich verrechnen das Kontoführungsentgelt pro Quartal. Ein Zusatzkonto kostet dann oft noch einmal ein eigenes Entgelt, manchmal ermäßigt. Frag nach, ob für das zweite Konto dieselben Entgelte pro Buchung gelten wie für das Hauptkonto. Bei Konten mit Entgelt je Buchungszeile kann jede Umbuchung zwischen den Töpfen etwas kosten. Dann wird ein System mit vielen kleinen Daueraufträgen teuer.',
        'Bei Neobanken ist die Zahl der Töpfe oft an den Tarif gebunden. Im Gratis-Tarif bekommst du wenige, in den Bezahltarifen mehr. Kostet der größere Tarif 5 € mehr im Monat, sind das 60 € im Jahr. Prüf also, ob du die zusätzlichen Töpfe wirklich brauchst.',
        'Eine Alternative für Rücklagen ist ein Online-Sparkonto. Es ist kein Unterkonto im engeren Sinn, bringt aber häufig Zinsen und lässt sich mit dem Girokonto verknüpfen. Für Geld, das du jeden Monat bewegst, ist das zu träge, für die Notreserve oft ideal.',
        'Rechne einmal durch, was dich dein Topfsystem im Jahr kostet: Kontoführung des Hauptkontos, Entgelt für Zusatzkonten, Buchungszeilen und eventuell eine zweite Karte. Erst dann vergleichst du fair.',
        f'Girokonten, die dich unter Bedingungen nichts kosten, findest du unter {c["liste"]("kostenlos", "kostenlose Girokonten")}.')))
    secs.append(('Gemeinsam haushalten mit Unterkonten', _p(
        'Viele Paare lösen gemeinsame Ausgaben mit einem Haushaltskonto. Jeder zahlt einen fixen Betrag ein, davon gehen Miete, Betriebskosten und der Wocheneinkauf ab. Das klappt mit einem Gemeinschaftskonto oder mit einem geteilten Topf, wenn die Bank das anbietet.',
        'Halbe-halbe ist nicht immer fair. Verdient eine Person deutlich mehr, ist eine Aufteilung nach Einkommen oft gerechter. Beispiel: 2.800 € und 1.800 € netto, gemeinsame Kosten 1.500 €. Nach Einkommen zahlt die eine Person rund 913 €, die andere rund 587 €. Jedem bleibt anteilig gleich viel zum Leben.',
        'Haltet bei einem gemeinsamen Topf fest, wer wie viel einzahlt und was daraus bezahlt wird. Das klingt bürokratisch, erspart aber Streit, gerade wenn sich Einkommen ändern, etwa durch Karenz oder Teilzeit.',
        f'Wichtig: Bei einem Gemeinschaftskonto haften beide für ein Minus. Bei einem geteilten Topf innerhalb eines Einzelkontos gehört das Geld rechtlich der Person, auf die das Konto läuft. Wer eine klare Lösung will, schaut in die Liste {c["liste"]("gemeinschaftskonto", "Gemeinschaftskonten")}.',
        f'Für Kinder und Jugendliche gibt es eigene Konten, auf die Eltern Einblick haben. Die findest du unter {c["liste"]("kinder-jugendkonto", "Kinder- und Jugendkonten")}.')))
    secs.append(('Zinsen, KESt und Einlagensicherung', _p(
        'Zahlt die Bank Zinsen auf ein Unterkonto, fällt Kapitalertragsteuer an. Bei Zinsen aus Bankguthaben sind das 25 %. Eine österreichische Bank zieht die KESt automatisch ab, du musst nichts tun.',
        'Ein Beispiel: 6.000 € Notreserve in einem Topf mit 2 % Zinsen bringen 120 € im Jahr. Davon gehen 30 € KESt ab, 90 € bleiben dir.',
        'Bei einer Bank ohne Sitz oder Zweigstelle in Österreich ist das oft anders. Zieht sie keine österreichische KESt ab, musst du die Zinsen selbst in der Einkommensteuererklärung angeben, in der Beilage E 1kv. Frag im Zweifel beim Kundenservice nach, ob die KESt für Österreich einbehalten wird.',
        f'Für die Einlagensicherung zählen alle Konten einer Person bei derselben Bank zusammen, Unterkonten eingeschlossen. Bis 100.000 € sind sie gesetzlich gesichert. Bei Privatbanken, Volksbanken und Hypos zahlt die Einlagensicherung AUSTRIA, Sparkassen und Raiffeisenbanken haben eigene Sicherungseinrichtungen. Details im Ratgeber {c["rg"]("einlagensicherung", "Einlagensicherung")}.')))
    secs.append(('Stolperfallen im ersten Jahr', _p(
        'Ein Topfsystem braucht ein paar Monate, bis es rund läuft. Diese Fehler passieren am Anfang besonders oft:',
        _ul('<b>Zu knapp gerechnet:</b> Teilbeträge für Strom und Gas werden angepasst, viele Versicherungen sind indexiert. Plane beim Fixkostenkonto einen Puffer ein, sonst wird eine Lastschrift nicht eingelöst und der Zahlungsempfänger verrechnet Spesen.',
            '<b>Jahreszahlungen übersehen:</b> Kfz-Versicherung, Haushaltsversicherung, Vereinsbeiträge, das Klimaticket. Geh die Kontoauszüge eines ganzen Jahres durch, addiere alle Jahres- und Quartalszahlungen und teil die Summe durch zwölf. Diesen Betrag legst du jeden Monat zurück.',
            '<b>Überziehung am Hauptkonto:</b> Liegt Geld im Topf, aber das Hauptkonto ist im Minus, zahlst du Sollzinsen auf dein eigenes Geld. Stell dir eine Benachrichtigung ein, wenn der Kontostand unter einen bestimmten Betrag fällt.',
            '<b>Sonderzahlungen sofort verplant:</b> Leg vor dem Urlaubs- und Weihnachtsgeld fest, welcher Anteil in welchen Topf geht. Ein fixer Plan schlägt jeden guten Vorsatz.',
            '<b>Zu viele Töpfe:</b> Mehr als fünf brauchen die wenigsten. Jeder zusätzliche Topf ist eine Zahl mehr, die du im Kopf behalten musst.'),
        'Mach nach dem ersten Quartal einen Check: Welche Töpfe sind ständig leer, welche wachsen ohne Zweck? Pass die Daueraufträge an. Nach einem Jahr hast du alle Jahreszahlungen einmal erlebt, und das System läuft meist von allein.')))
    secs.append(('Worauf du beim Vergleich achten solltest', _p(
        _ul('Wie viele Töpfe bekommst du in deinem Tarif, und was kostet jeder weitere?',
            'Hat jeder Topf eine eigene IBAN, und aus welchem Land kommt sie?',
            'Kostet eine Umbuchung zwischen den Töpfen etwas, etwa als Buchungszeile?',
            'Gibt es Automatiken wie Daueraufträge zwischen Töpfen, Aufrunden bei Kartenzahlungen oder Sparregeln am Gehaltstag?',
            'Kannst du Töpfe mit anderen teilen, ohne gleich ein Gemeinschaftskonto zu eröffnen?',
            'Bekommst du für jedes Konto einen eigenen Kontoauszug? Das hilft bei der Abrechnung mit Mitbewohnern.'),
        f'Wechseln geht in Österreich mit dem Kontowechselservice nach dem Verbraucherzahlungskontogesetz (VZKG): Die neue Bank holt sich Daueraufträge und Lastschriften von der alten. Wie das abläuft, steht im Ratgeber {c["rg"]("girokonto-wechseln", "Girokonto wechseln")}.')))
    secs.append(('Quellen', _quellen(c, [
        ('https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20009550', 'Rechtsinformationssystem des Bundes (RIS): Verbraucherzahlungskontogesetz'),
        ('https://www.einlagensicherung.at/', 'Einlagensicherung AUSTRIA'),
        ('https://www.bmf.gv.at/', 'Bundesministerium für Finanzen: Kapitalertragsteuer'),
        ('https://www.fma.gv.at/', 'Finanzmarktaufsicht (FMA)'),
        ('https://www.arbeiterkammer.at/', 'Arbeiterkammer: Konsumentenschutz Bankgeschäfte'),
    ], d['X'] if d else [])))
    faq = [
        ('Kann mein Arbeitgeber das Gehalt auf zwei Konten aufteilen?', 'Manche Lohnverrechnungen machen das, verpflichtet sind sie nicht. Einfacher ist ein Dauerauftrag: Das Gehalt kommt aufs Hauptkonto, und am selben oder nächsten Tag geht ein fixer Betrag automatisch in den Topf.'),
        ('Bekommt jedes Unterkonto eine eigene Bankomatkarte?', 'Das hängt von der Bank ab. Zu einem Zusatzkonto mit eigener IBAN kannst du oft eine eigene Karte bestellen, die meist extra kostet. Virtuelle Töpfe haben in der Regel keine eigene Karte. Manche Apps erlauben, eine Karte mit einem bestimmten Topf zu verknüpfen.'),
        ('Ist Guthaben auf einem Unterkonto vor Exekution geschützt?', f'Nicht automatisch. Ein Pfändungsschutzkonto wie in Deutschland gibt es in Österreich nicht. Wird dein Konto gepfändet, kannst du beim Exekutionsgericht beantragen, dass der unpfändbare Teil von Gehalt oder Pension freigegeben wird (§ 292i EO). Das gilt für jedes Konto, auch für Töpfe. Mehr im Ratgeber {c["rg"]("pfaendungsschutzkonto", "Pfändungsschutz am Konto")}.'),
        ('Kann ein Unterkonto mein Sparbuch ersetzen?', 'Für eine Notreserve ja, solange du jederzeit an das Geld kommen willst. Ein Sparkonto mit Bindung bringt meist mehr Zinsen, dafür kommst du nicht sofort ran. Viele kombinieren beides: ein Topf am Girokonto für kurzfristige Ausgaben, ein Sparkonto für den Rest.'),
        ('Was passiert mit Daueraufträgen, wenn ich einen Topf lösche?', 'Daueraufträge auf oder von diesem Topf laufen ins Leere oder werden von der Bank gestoppt. Lösch zuerst die Aufträge, buch das Guthaben um und schließ dann den Topf. Bei Konten mit eigener IBAN gibst du die neue Verbindung vorher allen Zahlungspartnern bekannt.'),
    ]
    lede = 'Mit Unterkonten teilst du dein Geld in Töpfe für Fixkosten, Rücklagen und Ziele, alles bei einer Bank. Diese Liste zeigt Girokonten in Österreich, die das anbieten, und was du dabei zahlst.'
    return dict(lede=lede, secs=secs, faq=faq)


# ---------- Ohne Schufa / ohne KSV ----------
def _bon_daten(c, slug, bon):
    X = c['lists'].get(slug) or []
    if not X:
        return None
    n = len(X)
    billig = min(X, key=_k)
    frei = [k for k in X if _k(k) == 0]
    dispo = [k for k in X if k.get('sollzins') is not None]
    s = f'In unserer Liste stehen {_n(n, "Konto", "Konten")} von {_n(len(_banken(X)), "Bank", "Banken")}, bei denen die Bank laut eigener Angabe bei der Eröffnung keine {bon}-Auskunft einholt. '
    s += f'Am günstigsten ist im Standardfall {c["link"](billig)} mit {_kt(c, billig)} im Jahr. '
    if len(frei) > 1:
        s += f'{_n(len(frei), "Konto kostet", "Konten kosten")} dich im Standardfall gar nichts. '
    if dispo:
        s += f'Einen Sollzins für eine Überziehung nennt die Bank bei {_n(len(dispo), "Konto", "Konten")}.'
    rows = [[c['link'](k), E(k.get('bonitaet_text') or f'keine {bon}-Abfrage'), E(c['kfT'](k)), _kt(c, k)] for k in X]
    return dict(X=X, s=s, rows=rows)


def _basis(c):
    B = [k for k in c['alle'] if k['art'] == 'basis']
    if not B:
        return None
    lo = min(B, key=_k)
    hi = max(B, key=_k)
    return dict(B=B, lo=lo, hi=hi, n=len(B))


def _ohne_schufa(c):
    d = _bon_daten(c, 'ohne-schufa', 'Schufa')
    b = _basis(c)
    secs = []
    secs.append(('Was „ohne Schufa“ bei einem Girokonto bedeutet', _p(
        'Bei den meisten Banken läuft bei der Kontoeröffnung im Hintergrund eine Anfrage bei der Schufa. Die Bank sieht dann, ob es offene Zahlungsausfälle, eine Insolvenz oder andere negative Einträge gibt, und bekommt einen Score. Ein Konto ohne Schufa-Abfrage heißt: Die Bank verzichtet auf diese Anfrage. Deine Identität prüft sie trotzdem, das schreibt das Geldwäschegesetz vor.',
        'Ohne Schufa heißt nicht ohne Spuren. Viele Banken melden ein neues Konto nach der Eröffnung an die Schufa, auch wenn sie vorher nicht gefragt haben. Ein Girokonto an sich ist für deinen Score aber kein Minuspunkt.',
        'Wichtig ist der Unterschied zwischen Abfrage und Meldung. Bei der Abfrage holt die Bank Informationen über dich ein. Bei der Meldung teilt sie der Schufa mit, dass du jetzt ein Konto bei ihr hast. Ein Konto ohne Schufa-Abfrage kann also trotzdem gemeldet werden.',
        'Und ohne Schufa heißt meistens auch ohne Dispo. Wer deine Bonität nicht prüft, gibt dir in der Regel keinen Kreditrahmen. Für viele Menschen mit Schulden ist genau das gewollt: Das Konto kann nicht ins Unbegrenzte rutschen.')))
    secs.append(('Warum Banken die Schufa fragen', _p(
        'Ein Girokonto ist für die Bank ein kleines Risiko. Mit einem Dispo leiht sie dir Geld. Auch ohne Dispo kann das Konto ins Minus rutschen, etwa wenn eine Lastschrift abgebucht wird, obwohl nichts mehr drauf ist, oder wenn Kartenzahlungen erst Tage später gebucht werden. Diese geduldete Überziehung kostet Zinsen und muss die Bank im Zweifel eintreiben.',
        'Die Schufa-Auskunft hilft der Bank abzuschätzen, wie wahrscheinlich so etwas ist. Manche Banken lehnen bei negativen Einträgen ab, andere eröffnen das Konto, aber ohne Dispo. Banken, die ganz auf die Abfrage verzichten, begrenzen das Risiko anders: kein Kreditrahmen, eine Karte, die meist nur bei Deckung funktioniert, und Lastschriften, die bei leerem Konto zurückgehen.',
        f'Für dich heißt das: Ein Konto ohne Schufa-Abfrage ist praktisch ein Guthabenkonto. Du kannst nur ausgeben, was drauf ist. Platzt eine Lastschrift, verlangt der Zahlungsempfänger oft eine Gebühr für die Rücklastschrift. Halte also immer einen kleinen Puffer. Was ein Dispo kostet, wenn du doch einen bekommst, steht im Ratgeber {c["rg"]("dispo", "Dispo")}.',
        'Im Alltag kommst du mit so einem Konto gut zurecht, wenn du ein paar Dinge im Blick behältst:',
        _ul('<b>Lastschriften timen:</b> Leg Abbuchungstermine kurz hinter den Geldeingang. Viele Zahlungspartner lassen dich den Tag wählen.',
            '<b>Vormerkungen einplanen:</b> Hotels, Mietwagenfirmen und manche Tankstellen reservieren vorab einen Betrag auf deiner Karte. Auf einem Guthabenkonto muss dieser Betrag verfügbar sein.',
            '<b>Handyvertrag und Ratenkauf:</b> Hier prüft der Anbieter deine Schufa selbst, unabhängig von deinem Konto. Prepaid-Tarife funktionieren ohne Prüfung.',
            '<b>Warnung einstellen:</b> Viele Apps melden sich, wenn der Kontostand unter einen Betrag fällt, den du festlegst.'))))
    if d:
        secs.append(('Konten ohne Schufa-Abfrage in der Liste', _p(d['s'])
                     + _tbl(['Konto', 'Bei der Eröffnung laut Bank', 'Kontoführung', 'Kosten im Jahr (Standardfall)'], d['rows'])
                     + _p('Die Angaben zur Abfrage stammen von den Banken selbst. Sie können sich ändern, und manche Banken behalten sich vor, später doch eine Auskunft einzuholen, etwa wenn du einen Dispo beantragst.')))
    bt = ''
    if b:
        bt = f'In unserem Vergleich stehen {b["n"]} Basiskonten. Am günstigsten ist im Standardfall {c["link"](b["lo"])} mit {_kt(c, b["lo"])} im Jahr, am teuersten {c["link"](b["hi"])} mit {_kt(c, b["hi"])}.'
    secs.append(('Das Basiskonto: dein Recht auf ein Girokonto', _p(
        'Wenn keine Bank dich nimmt, hilft das Zahlungskontengesetz (ZKG). Jeder, der sich rechtmäßig in der EU aufhält, hat Anspruch auf ein Basiskonto. Das gilt auch für Wohnungslose, Geflüchtete und Menschen mit negativer Schufa. Alle Banken, die Girokonten für Privatkunden anbieten, müssen es einrichten. Selbst wenn die Bank deine Schufa-Einträge kennt, darf sie dich deshalb nicht ablehnen.',
        'Ablehnen darf die Bank nur aus Gründen, die im Gesetz stehen, etwa wenn du in Deutschland schon ein nutzbares Zahlungskonto hast oder in den letzten drei Jahren wegen einer Straftat gegen genau diese Bank verurteilt wurdest. Sie muss innerhalb von zehn Geschäftstagen nach deinem vollständigen Antrag entscheiden. Eine Ablehnung muss schriftlich kommen, mit Begründung und Hinweis, wo du dich beschweren kannst. Die BaFin hat dafür ein eigenes Verwaltungsverfahren, daneben gibt es die Schlichtungsstellen der Banken.',
        'Ein Basiskonto kann alles, was du im Alltag brauchst: Gehalt empfangen, überweisen, Lastschriften, Daueraufträge, Debitkarte, Bargeld abheben. Einen Dispo gibt es nicht. Die Gebühren müssen angemessen sein (§ 41 ZKG). Der Bundesgerichtshof hat am 30. Juni 2020 entschieden (XI ZR 119/19), dass eine Bank den Mehraufwand für Basiskonten nicht allein auf deren Inhaber abwälzen darf. Ein zu hoher Preis ist dann unwirksam.',
        'Für den Antrag brauchst du einen Ausweis. Wer keinen deutschen Pass oder Personalausweis hat, kann sich auch mit anderen anerkannten Papieren ausweisen, etwa mit einer Duldung oder einem Ankunftsnachweis. Zusatzprodukte wie Versicherungen oder eine Kreditkarte musst du für ein Basiskonto nicht abschließen.',
        bt,
        f'Wie du ein Basiskonto beantragst und was du tun kannst, wenn die Bank sich querstellt, erklärt der Ratgeber {c["rg"]("basiskonto", "Basiskonto")}.')))
    secs.append(('Trotz negativer Schufa zu einem Konto: so gehst du vor', _p(
        _ol('<b>Erst nachsehen, was wirklich drinsteht.</b> Viele vermuten einen negativen Eintrag, der längst gelöscht ist oder nie existiert hat. Wie du an deine Daten kommst, steht weiter unten.',
            '<b>Ein Konto ohne Schufa-Abfrage wählen,</b> wenn du ein ganz normales Girokonto willst und kein Basiskonto. Die Konten oben in der Liste sind dafür der Startpunkt.',
            '<b>Ein Basiskonto beantragen,</b> wenn dich keine Bank nimmt. Nutz dafür das Antragsformular, das die Bank bereithalten muss, und heb eine Kopie auf.',
            f'<b>Bei einer Pfändung ein P-Konto einrichten.</b> Jedes Girokonto kann auf Antrag in ein Pfändungsschutzkonto umgewandelt werden. Ist schon gepfändet, muss die Bank das spätestens zum Beginn des vierten Geschäftstags nach deinem Antrag umsetzen (§ 850k ZPO). Dann bleibt ein Grundfreibetrag geschützt. Mehr im Ratgeber {c["rg"]("p-konto", "P-Konto")}.',
            '<b>Hilfe holen.</b> Schuldnerberatungen der Verbraucherzentralen, der Wohlfahrtsverbände und der Kommunen helfen kostenlos oder sehr günstig, auch beim Gespräch mit Gläubigern.'),
        'Vorsicht bei Anbietern, die gegen Vorkasse ein „Konto ohne Schufa“ oder eine „Schufa-Löschung“ versprechen. Seriöse Banken verlangen für die Eröffnung keine Gebühr vorab, und niemand kann korrekte Einträge einfach löschen lassen. Wer dafür Geld nimmt, verdient an deiner Notlage.')))
    secs.append(('Konto ohne Schufa, Basiskonto, P-Konto: was wann passt', _p(
        'Die drei Begriffe werden oft durcheinandergeworfen. Sie lösen aber verschiedene Probleme und lassen sich kombinieren.')
        + _tbl(['Lösung', 'Für wen', 'Was du bekommst', 'Worauf achten'], [
            ['Konto ohne Schufa-Abfrage', 'wer ein normales Konto ohne Bonitätsprüfung möchte', 'Girokonto, meist ohne Dispo', 'Bedingungen und Gebühren der Bank, Angaben können sich ändern'],
            ['Basiskonto', 'wer von Banken abgelehnt wird', 'gesetzlich garantierte Grundfunktionen, kein Dispo', 'Gebühren vergleichen, Ablehnung schriftlich verlangen'],
            ['P-Konto', 'wer gepfändet wird oder eine Pfändung erwartet', 'Schutz eines monatlichen Grundfreibetrags', 'nur ein P-Konto pro Person'],
            ['Prepaid-Kreditkarte', 'als Ergänzung, etwa für Onlinekäufe', 'Karte ohne Kreditrahmen', 'ersetzt kein Girokonto, keine Lastschriften'],
        ])
        + _p('Ein Basiskonto lässt sich als P-Konto führen. Und wer bei einer Bank ohne Schufa-Abfrage ein Konto eröffnet, kann es später ebenfalls umwandeln lassen. Entscheidend ist, dass du erst einmal ein Konto hast, auf das Gehalt, Rente oder Sozialleistungen fließen können. Ohne Konto wird fast alles schwieriger, von der Wohnungssuche bis zum Jobantritt.')))
    secs.append(('Was im Schufa-Score steckt', _p(
        'Die Schufa speichert Daten, die Banken, Händler, Telefonanbieter und Inkassounternehmen melden. Dazu gehören:',
        _ul('Girokonten und Kreditkarten',
            'Kredite und Ratenkäufe, mit Betrag und Laufzeit',
            'Handy- und Leasingverträge',
            'Zahlungsausfälle, aber nur unter Bedingungen: Die Forderung ist fällig, du wurdest nach Fälligkeit mindestens zweimal schriftlich gemahnt, zwischen erster Mahnung und Meldung lagen mindestens vier Wochen, du wurdest vorher auf die mögliche Meldung hingewiesen, und du hast die Forderung nicht bestritten. Alternativ hat ein Gericht sie festgestellt.',
            'Insolvenzverfahren und Einträge aus den öffentlichen Schuldnerverzeichnissen'),
        'Nicht gespeichert werden Einkommen, Vermögen, Beruf, Nationalität oder Familienstand. Fragst du bei einer Bank nur nach den Konditionen für einen Kredit, fließt das ebenfalls nicht in deinen Score ein.',
        'Negative Einträge bleiben nicht für immer. Erledigte Zahlungsausfälle löscht die Schufa nach festen Fristen, die in den Verhaltensregeln der Auskunfteien stehen. Bezahle offene Forderungen deshalb so schnell wie möglich, damit sie als erledigt gemeldet werden und die Frist zu laufen beginnt.')))
    secs.append(('Selbstauskunft: kostenlos und schnell', _p(
        'Nach Artikel 15 der Datenschutz-Grundverordnung darfst du kostenlos erfahren, was die Schufa über dich speichert. Den Antrag stellst du online auf der Seite der Schufa oder per Post. Die kostenpflichtigen Produkte, die dir dabei angeboten werden, brauchst du dafür nicht.',
        'Prüf die Auskunft Zeile für Zeile. Stimmt die Adresse? Gibt es Verträge, die du nicht kennst? Ist eine Forderung als offen eingetragen, die du längst bezahlt hast? Falsche Einträge muss die Schufa berichtigen oder löschen. Schreib dazu mit Nachweisen an die Schufa. Hilft das nicht, kannst du dich an die Ombudsstelle der Schufa oder an die hessische Datenschutzaufsicht wenden, die für die Schufa zuständig ist.',
        'Neben der Schufa gibt es weitere Auskunfteien wie Creditreform Boniversum, CRIF oder Infoscore. Auch dort kannst du kostenlos Auskunft verlangen. Wenn eine Bank ein Konto ablehnt, darfst du fragen, auf welche Auskunftei sie sich gestützt hat.',
        'Plane etwas Zeit ein. Die Schufa muss dir die Auskunft spätestens innerhalb eines Monats schicken. Wer sie für eine Wohnungsbewerbung braucht, fordert sie besser früh an.')))
    secs.append(('Quellen', _quellen(c, [
        ('https://www.gesetze-im-internet.de/zkg/', 'Zahlungskontengesetz (ZKG): Basiskonto'),
        ('https://www.gesetze-im-internet.de/zpo/__850k.html', 'Zivilprozessordnung § 850k: Pfändungsschutzkonto'),
        ('https://www.gesetze-im-internet.de/bdsg_2018/__31.html', 'Bundesdatenschutzgesetz § 31: Meldung von Forderungen an Auskunfteien'),
        ('https://www.meineschufa.de/service/datenkopie', 'Schufa: Datenkopie nach Art. 15 DSGVO'),
        ('https://www.bafin.de/', 'BaFin: Beschwerde und Verwaltungsverfahren zum Basiskonto'),
        ('https://www.verbraucherzentrale.de/', 'Verbraucherzentralen: Schuldnerberatung und Basiskonto'),
    ], d['X'] if d else [])))
    faq = [
        ('Sieht mein Arbeitgeber, dass ich ein Konto ohne Schufa-Prüfung habe?', 'Nein. Dein Arbeitgeber bekommt nur die IBAN, an der man nicht erkennt, wie die Bank dich geprüft hat. Auch einem Basiskonto sieht man das von außen nicht an.'),
        ('Bekomme ich ohne Schufa-Prüfung eine Kreditkarte?', 'Eine echte Kreditkarte mit Kreditrahmen fast nie, denn dafür prüft jede Bank die Bonität. Möglich ist eine Debitkarte oder eine Prepaid-Kreditkarte, die du vorher auflädst. Bei Mietwagen oder Hotelkautionen werden solche Karten manchmal nicht akzeptiert.'),
        ('Kann die Bank mein Basiskonto wieder kündigen?', 'Nur aus Gründen, die das Zahlungskontengesetz nennt. Dazu gehört etwa, dass über das Konto mehr als 24 Monate keine Zahlung lief, dass du es für verbotene Zwecke genutzt hast oder bei der Eröffnung falsche Angaben gemacht hast. Eine Kündigung muss die Bank begründen.'),
        ('Verschlechtert eine Kontoeröffnung meinen Schufa-Score?', 'Ein neues Girokonto an sich nicht. Wichtig ist, dass du es ohne Rückstände führst. Kredite, Ratenkäufe und vor allem Zahlungsausfälle wirken sich deutlich stärker aus als ein Konto.'),
        ('Was ist der Unterschied zwischen einem Konto ohne Schufa und einem P-Konto?', 'Beim Konto ohne Schufa geht es um die Eröffnung: Die Bank fragt nicht nach. Ein P-Konto schützt dagegen bei einer Pfändung einen Grundbetrag deines Guthabens. Beides lässt sich kombinieren: Du kannst ein Konto ohne Schufa-Abfrage eröffnen und es bei Bedarf in ein P-Konto umwandeln lassen.'),
    ]
    lede = 'Hier findest du Girokonten, bei denen die Bank laut eigenen Angaben bei der Eröffnung keine Schufa-Auskunft einholt. Dazu: welche Wege es sonst gibt, wenn dein Schufa-Score schlecht ist.'
    return dict(lede=lede, secs=secs, faq=faq)


def _ohne_ksv(c):
    d = _bon_daten(c, 'ohne-ksv', 'KSV1870')
    b = _basis(c)
    secs = []
    secs.append(('Was eine KSV-Abfrage bei der Kontoeröffnung ist', _p(
        'Wenn du in Österreich ein Girokonto eröffnest, schaut die Bank oft in die Datenbanken des KSV1870. Für Banken wichtig sind vor allem zwei: die Konsumentenkreditevidenz mit laufenden Krediten und Leasingverträgen und die Warnliste der österreichischen Kreditinstitute. In der Warnliste melden Banken vertragswidriges Verhalten, etwa fällig gestellte Kredite oder missbräuchlich verwendete Karten.',
        'Daneben gibt es die CRIF, eine weitere große Auskunftei. Sie sammelt unter anderem Zahlungserfahrungen von Händlern, Telefonanbietern und Inkassobüros. Manche Banken fragen dort statt beim KSV1870 oder zusätzlich.',
        'Ein Konto ohne KSV-Abfrage heißt: Die Bank verzichtet bei der Eröffnung auf diese Anfrage. Ausweis und Daten prüft sie trotzdem, das verlangt das Finanzmarkt-Geldwäschegesetz. Ohne gültigen Lichtbildausweis bekommst du nirgends ein Konto.',
        'Viele erfahren erst bei der Kontoeröffnung von einem negativen Eintrag. Eine Absage ohne Begründung ist frustrierend. Du darfst aber fragen, auf welche Auskunftei sich die Bank gestützt hat, und dort nachsehen, was über dich gespeichert ist. Oft ist der Eintrag alt, längst bezahlt oder schlicht falsch.',
        'Wie streng eine Bank prüft, entscheidet sie selbst. Kein Gesetz schreibt eine KSV-Abfrage bei jedem Konto vor. Deshalb unterscheiden sich die Banken hier spürbar.',
        'Die Warnliste ist übrigens nicht öffentlich. Nur Banken können sie einsehen, und nur, wenn es um ein Geschäft mit dir geht.')))
    secs.append(('Warum österreichische Banken nachfragen', _p(
        'Viele Girokonten in Österreich kommen mit einem Überziehungsrahmen, oder die Bank räumt ihn nach einigen Monaten ein. Das ist ein Kredit. Bevor die Bank dir den gibt, will sie wissen, ob du andere Kredite hast und ob es dabei Probleme gab.',
        'Auch ohne Rahmen kann ein Konto ins Minus gehen, etwa durch eine Lastschrift oder durch Kartenzahlungen, die verspätet gebucht werden. Diese Überschreitung muss die Bank dann eintreiben. Die Abfrage soll das Risiko vorher abschätzen.',
        'Für die Bank ist die Abfrage billig und schnell, für dich kann sie den Unterschied zwischen Zusage und Absage machen. Banken, die darauf verzichten, setzen auf Konten, bei denen ein größerer Ausfall kaum möglich ist.',
        f'Banken, die nicht abfragen, gehen anders vor: Sie geben keinen Überziehungsrahmen, die Karte funktioniert meist nur mit Guthaben, und Lastschriften ohne Deckung werden nicht eingelöst. Für dich ist das kein Nachteil, solange du einen Puffer am Konto lässt. Zahlungsempfänger verrechnen für eine nicht eingelöste Lastschrift oft Spesen und Mahngebühren. Was eine Überziehung sonst kostet, erklärt der Ratgeber {c["rg"]("kontoueberziehung", "Kontoüberziehung")}.',
        'Mit einem Konto ohne Überziehungsrahmen lebt es sich gut, wenn du ein paar Punkte kennst:',
        _ul('<b>Abbuchungen nach dem Gehalt:</b> Leg Lastschriften für Miete, Strom und Versicherung auf die Tage kurz nach dem Gehalts- oder Pensionseingang.',
            '<b>Reservierungen auf der Karte:</b> Hotels, Mietautos und manche Tankstellen sperren vorab einen Betrag. Der muss am Konto verfügbar sein.',
            '<b>Handy und Energie:</b> Mobilfunker und Energieanbieter prüfen deine Bonität oft selbst. Eine Absage dort hat nichts mit deinem Konto zu tun. Ein Wertkartenhandy funktioniert ohne Prüfung.',
            '<b>Benachrichtigung bei niedrigem Stand:</b> In vielen Apps lässt sich eine Warnung einstellen, bevor das Konto leer ist.'))))
    if d:
        secs.append(('Konten ohne KSV-Abfrage in der Liste', _p(d['s'])
                     + _tbl(['Konto', 'Bei der Eröffnung laut Bank', 'Kontoführungsentgelt', 'Kosten im Jahr (Standardfall)'], d['rows'])
                     + _p('Was in der zweiten Spalte steht, sagt die Bank selbst. Beantragst du später einen Überziehungsrahmen oder eine Kreditkarte, kann sie dann sehr wohl eine Auskunft einholen.')))
    bt = ''
    if b:
        voll = [k for k in b['B'] if _k(k) == 80]
        bt = f'In unserem Vergleich stehen {b["n"]} Basiskonten. Am günstigsten ist im Standardfall {c["link"](b["lo"])} mit {_kt(c, b["lo"])} im Jahr'
        bt += f'; {len(voll)} davon verlangen im Standardfall 80 € im Jahr.' if voll else '.'
    secs.append(('Basiskonto nach VZKG: Anspruch für alle', _p(
        'Seit 2016 hat in Österreich jeder, der sich rechtmäßig in der EU aufhält, Anspruch auf ein Basiskonto. Das regelt das Verbraucherzahlungskontogesetz (VZKG). Es gilt auch für Menschen ohne festen Wohnsitz, für Asylwerbende und für Menschen mit Einträgen beim KSV1870.',
        'Die Bank muss das Konto spätestens zehn Geschäftstage nach deinem vollständigen Antrag eröffnen oder den Antrag ablehnen. Ablehnen darf sie nur aus Gründen, die im Gesetz stehen: wenn du in Österreich schon ein Zahlungskonto hast, das du nutzen kannst, oder wenn du wegen einer Straftat gegen die Bank angeklagt oder verurteilt bist. Eine Ablehnung muss schriftlich und begründet kommen, mit Hinweis auf die Beschwerde bei der FMA und die Schlichtungsstelle.',
        'Das Entgelt ist gesetzlich gedeckelt. Im Gesetz stehen 80 € im Jahr, der Betrag wird an die Inflation angepasst. Laut Arbeiterkammer liegt die Grenze derzeit bei 83,45 € im Jahr. Für besonders schutzbedürftige Menschen, etwa mit Mindestsicherung, Ausgleichszulage oder Studienbeihilfe, gilt auf Antrag die Hälfte, derzeit 41,73 €.',
        'Für den Antrag brauchst du einen amtlichen Lichtbildausweis. Einen festen Wohnsitz darf die Bank nicht zur Bedingung machen. Und das Basiskonto ist kein Konto zweiter Klasse: Die IBAN ist eine ganz normale österreichische IBAN, Arbeitgeber und AMS überweisen darauf wie auf jedes andere Konto.',
        'Lehnt eine Bank dein Basiskonto ab, verlang die Begründung schriftlich. Damit kannst du dich beschweren und gleichzeitig bei einer anderen Bank einen neuen Antrag stellen.',
        bt,
        f'Ein Basiskonto enthält Ein- und Auszahlungen, Überweisungen, Daueraufträge, Lastschriften und eine Bankomatkarte. Einen Überziehungsrahmen gibt es nicht. Mehr im Ratgeber {c["rg"]("basiskonto", "Basiskonto")}.')))
    secs.append(('Mit Eintrag beim KSV1870 zu einem Konto', _p(
        _ol('<b>Eigene Daten anfordern.</b> Bevor du dich auf eine Absage einstellst, schau nach, was über dich gespeichert ist. Wie das geht, steht weiter unten.',
            '<b>Ein Konto ohne Abfrage wählen,</b> wenn du ein normales Girokonto möchtest. Die Konten in der Liste oben sind ein guter Startpunkt.',
            '<b>Ein Basiskonto verlangen,</b> wenn eine Bank ablehnt. Lehnt sie auch das ab, wende dich an die Gemeinsame Schlichtungsstelle der österreichischen Kreditwirtschaft, an die FMA oder an die Arbeiterkammer.',
            f'<b>Bei einer Kontopfändung schnell den Kontenschutz beantragen.</b> Ein Pfändungsschutzkonto wie in Deutschland gibt es in Österreich nicht. Du beantragst beim Exekutionsgericht, dass der unpfändbare Teil von Gehalt oder Pension freigegeben wird (§ 292i EO). Mehr im Ratgeber {c["rg"]("pfaendungsschutzkonto", "Pfändungsschutz am Konto")}.',
            '<b>Zur Schuldenberatung gehen.</b> Die staatlich anerkannten Schuldenberatungen in allen Bundesländern helfen kostenlos und vertraulich: mit einem Überblick über alle Forderungen, beim Verhandeln mit Gläubigern und auf dem Weg in ein Schuldenregulierungsverfahren, den sogenannten Privatkonkurs.'),
        'Finger weg von Angeboten, die dir gegen Vorauszahlung ein „Konto ohne KSV“ oder einen „Kredit ohne KSV“ versprechen. Eine seriöse Bank verlangt für die Kontoeröffnung nichts vorab. Wer Geld vorher will und dann nicht liefert, ist ein Betrüger.',
        'Viele Menschen mit Einträgen schieben das Thema auf, aus Scham oder weil es unangenehm ist. Das kostet meist Geld, weil Zinsen und Inkassokosten weiterlaufen. Wer früh handelt, zahlt fast immer weniger. Und Vorsicht bei Werbung für schnelle Kredite: Neue Schulden zu hohen Zinsen machen die Lage selten besser.',
        'Ein Basiskonto oder ein Konto ohne Abfrage ist auch ein Neustart. Wer ein paar Monate zuverlässig wirtschaftet, hat später bessere Karten, wenn es um einen Überziehungsrahmen oder ein Konto bei einer anderen Bank geht.')))
    secs.append(('Konto ohne Abfrage, Basiskonto, Kontenschutz im Vergleich', _p(
        'Die drei Lösungen helfen in unterschiedlichen Lagen. Diese Übersicht zeigt, was wann passt:')
        + _tbl(['Lösung', 'Passt, wenn', 'Was du bekommst', 'Zu beachten'], [
            ['Konto ohne KSV-Abfrage', 'du ein reguläres Konto ohne Bonitätsprüfung möchtest', 'Girokonto, meist ohne Überziehungsrahmen', 'Entgelte und Bedingungen der Bank'],
            ['Basiskonto nach VZKG', 'dich Banken ablehnen', 'gesetzlicher Mindestumfang, laut Arbeiterkammer derzeit höchstens 83,45 € im Jahr', 'Nachweis, wenn dir das ermäßigte Entgelt zusteht'],
            ['Kontenschutz nach § 292i EO', 'dein Konto gepfändet wurde', 'Freigabe des unpfändbaren Teils von Gehalt oder Pension', 'nur auf Antrag beim Exekutionsgericht, kein eigenes Kontomodell'],
            ['Prepaid-Karte', 'du nur online oder im Urlaub zahlen willst', 'Karte ohne Kreditrahmen', 'kein Konto, keine Lastschriften'],
        ])
        + _p('Die Wege lassen sich verbinden. Auch bei einem Basiskonto kannst du nach einer Pfändung den Kontenschutz beantragen. Wichtig ist zuerst, dass Lohn, Pension, Arbeitslosengeld oder Sozialleistungen überhaupt auf ein Konto fließen können. Ohne Konto werden schon Miete und Handyrechnung zum Problem.',
        'Unsicher, was zu dir passt? Schuldenberatung und Arbeiterkammer beraten kostenlos und kennen die Praxis der Banken in deinem Bundesland.')))
    secs.append(('Welche Daten deine Bonität in Österreich prägen', _p(
        'Einen einzigen Score, der für alle gilt, gibt es nicht. Jede Auskunftei rechnet mit eigenen Daten, und Banken gewichten sie unterschiedlich. Grob fließt das hier ein:',
        _ul('<b>Konsumentenkreditevidenz beim KSV1870:</b> Kredite, Leasingverträge und Kreditrahmen, gemeldet von Banken und Leasingfirmen, samt Verlauf der Rückzahlung.',
            '<b>Warnliste der Banken:</b> Meldungen über vertragswidriges Verhalten, etwa wenn ein Kredit fällig gestellt oder ein Konto wegen Rückständen gekündigt wurde.',
            '<b>Zahlungserfahrungen:</b> offene Forderungen aus Handel, Telekom und Inkasso, gesammelt von KSV1870, CRIF und anderen.',
            '<b>Öffentliche Daten:</b> Insolvenzen und Schuldenregulierungsverfahren aus der Ediktsdatei der Justiz.'),
        'Dein Einkommen, Vermögen oder Beruf kennt die Auskunftei nicht. Das prüft die Bank bei Bedarf selbst, etwa über Lohnzettel oder Kontoauszüge.',
        'Für dich heißt das: Ein einzelner Rückstand bei einem Onlinehändler kann bei der einen Auskunftei stehen und bei der anderen nicht. Deshalb kann dich eine Bank ablehnen und die nächste nicht.',
        'Wurde ein Rückstand bezahlt, sollte das auch gemeldet werden. Falsche oder veraltete Einträge musst du nicht hinnehmen. Nach der DSGVO hast du ein Recht auf Berichtigung und unter Umständen auf Löschung. Ist eine Auskunftei uneinsichtig, kannst du dich bei der Datenschutzbehörde beschweren.',
        'Ein häufiger Irrtum: Wer einmal einen Eintrag hatte, bleibt nicht für immer gesperrt. Auskunfteien dürfen Daten nur so lange speichern, wie sie für den Zweck nötig sind. Ist ein Rückstand bezahlt und liegt er Jahre zurück, frag nach, ob der Eintrag noch gespeichert werden darf.')))
    secs.append(('Selbstauskunft beim KSV1870 und bei der CRIF', _p(
        'Nach Artikel 15 DSGVO darfst du kostenlos erfahren, welche Daten eine Auskunftei über dich gespeichert hat. Du schickst einen Antrag mit Kopie deines Ausweises, online oder per Post. Beide Auskunfteien bieten auch kostenpflichtige Bonitätsprodukte an. Für den Blick auf deine eigenen Daten brauchst du sie nicht.',
        'Lies die Antwort genau. Sind alle Kredite noch aktuell? Steht ein längst bezahlter Betrag noch als offen drin? Gibt es eine Adresse, an der du nie gewohnt hast? Solche Fehler kommen vor, gerade nach Umzügen oder bei häufigen Namen.',
        'Die Auskunft lohnt sich auch vor der Wohnungssuche. Viele Vermieter wollen eine Bonitätsauskunft sehen. Wenn du vorher weißt, was drinsteht, kannst du Fehler korrigieren lassen, bevor sie dich eine Wohnung kosten.',
        'Fordere die Auskunft am besten bei beiden Auskunfteien an. Banken nutzen unterschiedliche Quellen, und ein Fehler bei der einen fällt dir sonst nicht auf.',
        'Die Auskunftei muss dir innerhalb eines Monats antworten. Plane das ein, wenn du die Auskunft für eine Wohnung oder einen Kredit brauchst.',
        'Bewahr die Auskunft gut auf. Wurde ein Fehler korrigiert, kannst du nach ein paar Wochen eine neue anfordern und prüfen, ob die Änderung angekommen ist.')))
    secs.append(('Quellen', _quellen(c, [
        ('https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20009550', 'Rechtsinformationssystem des Bundes (RIS): Verbraucherzahlungskontogesetz'),
        ('https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=10001700', 'RIS: Exekutionsordnung, § 292i Kontenschutz'),
        ('https://www.ksv.at/', 'KSV1870: Datenauskunft'),
        ('https://www.crif.at/', 'CRIF Österreich: Selbstauskunft'),
        ('https://www.dsb.gv.at/', 'Österreichische Datenschutzbehörde'),
        ('https://www.schuldenberatung.at/', 'Staatlich anerkannte Schuldenberatungen'),
        ('https://www.fma.gv.at/', 'Finanzmarktaufsicht (FMA)'),
        ('https://www.arbeiterkammer.at/beratung/konsument/Geld/Konto/Recht_auf_ein_Girokonto.html', 'Arbeiterkammer: Basiskonto'),
    ], d['X'] if d else [])))
    faq = [
        ('Bekomme ich mit einem KSV-Eintrag eine Bankomatkarte?', 'Beim Basiskonto ja, eine Zahlungskarte gehört zum gesetzlichen Mindestumfang. Bei anderen Konten entscheidet die Bank. Oft gibt es eine Debitkarte, die nur mit Guthaben funktioniert.'),
        ('Kann ich mit einem Konto ohne KSV-Abfrage meine Bonität verbessern?', 'Nicht direkt. Ein Konto ohne Kreditrahmen ist kein Kredit und taucht deshalb nicht positiv in der Kreditevidenz auf. Was wirklich hilft: offene Forderungen bezahlen, Ratenvereinbarungen einhalten und falsche Einträge korrigieren lassen.'),
        ('Gilt das Recht auf ein Basiskonto auch im Privatkonkurs?', 'Ja. Das VZKG knüpft den Anspruch nicht an deine Bonität. Ein laufendes Schuldenregulierungsverfahren ist kein Grund, dir das Basiskonto zu verweigern. Einen Überziehungsrahmen gibt es beim Basiskonto ohnehin nicht.'),
        ('Was kostet ein Basiskonto, wenn ich Mindestsicherung beziehe?', 'Für besonders schutzbedürftige Menschen ist das Entgelt auf die Hälfte des normalen Höchstbetrags gedeckelt, laut Arbeiterkammer derzeit auf höchstens 41,73 € im Jahr. Leg der Bank dazu einen aktuellen Nachweis vor, etwa den Bescheid.'),
        ('Fragen ausländische Banken auch beim KSV1870 nach?', f'Das ist unterschiedlich. Manche fragen bei Auskunfteien in ihrem Sitzland nach, manche bei österreichischen, manche gar nicht. Ob und wo, steht in den Bedingungen oder der Datenschutzerklärung der Bank. Was du bei Banken mit Sitz im Ausland sonst beachten solltest, steht in der Liste {c["liste"]("neobanken", "Neobanken")}.'),
    ]
    lede = 'Hier stehen Girokonten in Österreich, bei denen die Bank laut eigenen Angaben bei der Eröffnung nicht beim KSV1870 nachfragt. Dazu erfährst du, welche Rechte du mit einem negativen Bonitätseintrag hast.'
    return dict(lede=lede, secs=secs, faq=faq)


# ---------- Direktbanken ----------
def _direkt_daten(c):
    X = c['lists'].get('direktbanken') or []
    if not X:
        return None
    ban = _banken(X)
    neo = set(_banken(c['lists'].get('neobanken') or []))
    fil = _filial_std(c, set(ban) | neo)
    md = _med([_k(k) for k in X if k['art'] == 'standard'])
    mf = _med([_k(k) for k in fil])
    frei = [k for k in X if _k(k) == 0]
    ein = _eingang(X)
    sz = [k['sollzins'] for k in X if k.get('sollzins') is not None]
    zus = [b for b in ban if any(('zusätzlich' in (k.get('einlagensicherung') or '').lower() or 'freiwillig' in (k.get('einlagensicherung') or '').lower())
                                 and 'nicht geprüft' not in (k.get('einlagensicherung') or '').lower() for k in X if k['bank'] == b)]
    ausl = [b for b in ban if any((k.get('iban') or c['code']) != c['code'] for k in X if k['bank'] == b)]
    alt = [k['gratis']['alter_unter'] for k in X if k.get('gratis') and k['gratis'].get('alter_unter')]
    return dict(X=X, ban=ban, fil=fil, md=md, mf=mf, frei=frei, ein=ein, sz=sz, zus=zus, ausl=ausl, alt=(min(alt), max(alt)) if alt else None)


def _alt_satz(d):
    if not d or not d['alt']:
        return ''
    lo, hi = d['alt']
    if lo == hi:
        return f'In dieser Liste gilt eine solche Altersgrenze bei {lo} Jahren: Wer jünger ist, zahlt keine Kontoführung, auch ohne Geldeingang.'
    return f'In dieser Liste liegen solche Altersgrenzen zwischen {lo} und {hi} Jahren: Wer jünger ist, zahlt keine Kontoführung, auch ohne Geldeingang.'


def _direkt_tab(c, d, at):
    rows = []
    for k in d['X']:
        r = [c['link'](k), E(c['kfT'](k)), E(c['kurzbed'](k)), _dz(c, k)]
        if at:
            r.append(E(k.get('iban') or ''))
        r.append(_kt(c, k))
        rows.append(r)
    head = ['Konto', 'Kontoführungsentgelt' if at else 'Kontoführung', 'Gratis, wenn', 'Sollzins' if at else 'Dispozins'] + (['IBAN'] if at else []) + ['Kosten im Jahr (Standardfall)']
    return _tbl(head, rows)


def _direkt_satz(c, d, at):
    s = f'In der Liste stehen {_n(len(d["X"]), "Konto", "Konten")} von {_n(len(d["ban"]), "Direktbank", "Direktbanken")}. '
    if d['frei']:
        s += f'{_n(len(d["frei"]), "Konto kostet", "Konten kosten")} dich in unserem Standardfall nichts, entweder ohne Bedingung oder weil die Gratis-Bedingung im Standardfall erfüllt ist. '
    if d['ein']:
        lo, hi = d['ein']
        s += (f'Wo die Gratis-Kontoführung an einen Eingang geknüpft ist, liegt die Schwelle zwischen {c["eur"](lo)} € und {c["eur"](hi)} € im Monat. ' if lo != hi
              else f'Wo die Gratis-Kontoführung an einen Eingang geknüpft ist, liegt die Schwelle bei {c["eur"](lo)} € im Monat. ')
    if len(d['sz']) > 1:
        s += f'Die {"Sollzinsen für den Überziehungsrahmen" if at else "Dispozinsen"} reichen von {c["pct"](min(d["sz"]))} bis {c["pct"](max(d["sz"]))}.'
    return s


def _direktbanken_de(c):
    d = _direkt_daten(c)
    secs = []
    vgl = ''
    if d and d['md'] is not None and d['mf'] is not None and d['fil']:
        vgl = 'Das zeigt sich in unseren Daten. ' + _vgl_satz(c, d['md'], d['mf'], 'der Direktbanken in dieser Liste')
    secs.append(('Was eine Direktbank ausmacht', _p(
        'Eine Direktbank hat keine Filialen, in die du gehen kannst. Konto eröffnen, Überweisungen, Karte sperren, Dispo ändern: Alles läuft über Website, App oder Telefon. Viele Direktbanken gibt es schon seit Jahrzehnten, oft als Tochter einer großen Bank. Sie sind also keine Start-ups, sondern etablierte Institute, meist mit Banklizenz in Deutschland oder als deutsche Niederlassung einer europäischen Bank.',
        f'Der Unterschied zur Neobank: Direktbanken kommen aus der Zeit von Telefon- und Onlinebanking und bieten meist die ganze Palette, also Girokonto, Tagesgeld, Depot, Ratenkredit und Baufinanzierung. Neobanken sind jünger, ganz aufs Smartphone ausgelegt und starten oft mit einem schmaleren Angebot. Die findest du in der Liste {c["liste"]("neobanken", "Neobanken")}.',
        'Ohne Filialnetz sparen Direktbanken Miete und Personal. Einen Teil davon geben sie an dich weiter, mit günstiger Kontoführung, wenn du eine Bedingung erfüllst, oder mit besseren Zinsen aufs Tagesgeld.',
        'Fast alles, was eine Filialbank kann, kann auch eine Direktbank: Gemeinschaftskonto, Kreditkarte, Tagesgeld, Depot, Ratenkredit. Was fehlt, ist der Ort, an dem du jemandem gegenübersitzt. Für viele ist das kein Verlust mehr, für manche schon, etwa bei einer Erbschaft oder einer großen Finanzierung.',
        vgl)))
    if d:
        secs.append(('Die Direktbanken in der Liste', _p(_direkt_satz(c, d, False)) + _direkt_tab(c, d, False)
                     + _p('Die Jahreskosten stammen aus unserem Standardfall, wie in der Methodik beschrieben. Erfüllst du die Gratis-Bedingung nicht, zahlst du die Kontoführung aus der zweiten Spalte.')))
    secs.append(('Vorteile und Nachteile auf einen Blick', _p(
        '<b>Was für eine Direktbank spricht:</b>',
        _ul('Kontoführung oft kostenlos, wenn du einen Geldeingang hast oder unter einer Altersgrenze bist.',
            'Rund um die Uhr erreichbar, Überweisungen und Kartensperre jederzeit in der App.',
            'Tagesgeld, Depot und Sparpläne oft günstig und im selben Login.',
            'Kontoeröffnung in einem Tag per Video-Ident oder Online-Ausweis.',
            'Ausgereiftes Onlinebanking, häufig mit Einbindung von Konten anderer Banken.'),
        '<b>Was dagegen spricht:</b>',
        _ul('Keine Beratung vor Ort, kein Schalter, kein Schließfach.',
            'Bargeld einzahlen ist umständlich und kostet oft Gebühren.',
            'Hilfe nur per Telefon oder Chat, zu Stoßzeiten mit Wartezeit.',
            'Gratis-Bedingungen wie Mindestgeldeingang oder Altersgrenze. Fällt die Bedingung weg, kostet das Konto Geld.',
            'Die Girocard ist bei manchen nur gegen Aufpreis zu haben.'))))
    secs.append(('Bargeld abheben und einzahlen ohne Filiale', _p(
        'Abheben ist bei Direktbanken meist kein Problem. Mit der Debitkarte oder Kreditkarte hebst du an vielen Automaten ab. Prüf aber die Details: Manche Banken erlauben nur eine bestimmte Zahl kostenloser Abhebungen pro Monat, andere nur ab einem Mindestbetrag. Automatenbetreiber dürfen ein eigenes Entgelt verlangen, das dir vor der Auszahlung angezeigt wird. Dann kannst du noch abbrechen.',
        'Eine gute Alternative ist die Supermarktkasse. Bei vielen Händlern kannst du beim Einkauf mit Karte Bargeld mitnehmen, oft ab einem kleinen Mindesteinkauf. Das kostet in der Regel nichts.',
        'Einzahlen ist schwieriger. Direktbanken haben keine eigenen Einzahlautomaten. Manche arbeiten mit Partnerbanken zusammen, an deren Automaten du einzahlen kannst, andere bieten Einzahlungen per Code an der Supermarktkasse an. Beides kostet häufig eine Gebühr. Wer regelmäßig Bargeld einnimmt, etwa Trinkgeld in der Gastronomie oder Einnahmen vom Flohmarkt, sollte das vor der Kontoeröffnung klären.',
        'Wie viel Bargeld dich jedes Konto kostet, steht im Vergleich bei jedem Konto unter Bargeld.',
        'Für den Urlaub lohnt ein Blick auf die Bedingungen im Ausland. Manche Direktbanken erlauben kostenlose Abhebungen mit der Kreditkarte weltweit, andere verlangen einen Prozentsatz vom Betrag. Bei Zahlungen in fremder Währung kommt oft ein Auslandseinsatzentgelt hinzu.')))
    secs.append(('Worauf du bei einer Direktbank achten solltest', _p(
        _ul('<b>Gratis-Bedingung:</b> Zählt nur Gehalt, oder auch eine Überweisung von dir selbst? Bei manchen Banken reicht jeder Eingang, bei anderen muss es ein echter Lohn oder eine Rente sein.',
            '<b>Karte:</b> Eine Debitkarte mit Visa- oder Mastercard-Funktion ist heute Standard. Die Girocard kostet bei einigen extra. Brauchst du sie, weil dein Bäcker nur Girocard nimmt, rechne den Preis ein.',
            f'<b>Dispo:</b> Die Zinsen unterscheiden sich spürbar. Wer öfter ins Minus rutscht, sollte darauf mehr achten als auf die Kontoführung. Mehr im Ratgeber {c["rg"]("dispo", "Dispo")}.',
            '<b>Bargeld:</b> Wie viele kostenlose Abhebungen gibt es im Monat, und gilt das auch im Ausland?',
            '<b>Erreichbarkeit:</b> Gibt es eine Hotline rund um die Uhr? Kannst du die Karte in der App sperren und wieder entsperren?',
            '<b>Zusatzprodukte:</b> Brauchst du ein Gemeinschaftskonto, ein Tagesgeld oder ein Depot bei derselben Bank?'),
        'Ein Rechenbeispiel zum Dispo: Du bist im Jahr im Schnitt drei Monate lang mit 500 € im Minus. Bei 12 % Dispozins kostet das rund 15 €, bei 9 % rund 11 €. Bei höheren Beträgen und längerer Dauer wächst der Unterschied schnell.',
        'Und lies die Gratis-Bedingung genau. Steht dort Geldeingang, Gehaltseingang oder Eingang von mindestens einem bestimmten Betrag? Zählt der Kalendermonat oder ein Durchschnitt? Gerade bei unregelmäßigem Einkommen, etwa als Freiberufler oder im Minijob, entscheidet das darüber, ob du zahlst.')))
    zt = ''
    if d and d['zus']:
        zt = f'Bei {len(d["zus"])} der {len(d["ban"])} Direktbanken in dieser Liste kommt laut Bank eine zusätzliche freiwillige Sicherung hinzu.'
    secs.append(('Wechsel zur Direktbank in fünf Schritten', _p(
        'Ein Kontowechsel klingt nach Papierkram, ist aber in Deutschland gut geregelt. Das Zahlungskontengesetz verpflichtet Banken zur Kontowechselhilfe. Ein Entgelt dafür darf die Bank nur verlangen, wenn es vereinbart und angemessen ist (§ 26 ZKG).',
        _ol('Konto online beantragen und die Identität per Video oder Online-Ausweis bestätigen.',
            'Die Kontowechselhilfe im Onlinebanking starten. Die neue Bank holt sich bei der alten Bank die Liste deiner Daueraufträge, Lastschriften und regelmäßigen Eingänge.',
            'Auswählen, welche Zahlungspartner die neue Bank über die neue IBAN informieren soll, etwa Arbeitgeber, Vermieter, Versicherungen.',
            'Das alte Konto ein paar Wochen parallel laufen lassen und auf vergessene Abbuchungen achten, vor allem jährliche.',
            'Erst dann das alte Konto kündigen und das Restguthaben übertragen lassen.'),
        f'Was dabei schiefgehen kann und wie du es vermeidest, steht im Ratgeber {c["rg"]("girokonto-wechseln", "Girokonto wechseln")}.')))
    secs.append(('Für wen sich eine Direktbank lohnt', _p(
        'Eine Direktbank passt gut, wenn du ein regelmäßiges Gehalt hast, Bankgeschäfte am Handy erledigst und selten Bargeld einzahlst. Dann bekommst du ein günstiges Konto mit allem, was eine Bank bieten kann, inklusive Dispo, Tagesgeld und Depot.',
        'Gut passt sie auch als Zweitkonto. Viele behalten ihr Konto bei Sparkasse oder Volksbank für Bargeld und Beratung und nutzen die Direktbank für Sparen und Investieren. Umgekehrt geht es auch: Gehalt und Alltag bei der Direktbank, ein kleines Konto vor Ort für Einzahlungen.',
        f'Für junge Leute ist die Kontoführung bei vielen Direktbanken bis zu einer Altersgrenze kostenlos. {_alt_satz(d)}',
        f'Weniger geeignet ist eine Direktbank, wenn du regelmäßig Bargeld einzahlst, Wert auf persönliche Beratung legst oder die Gratis-Bedingung nicht erfüllst. Ohne Geldeingang kann ein Konto bei einer Direktbank ähnlich viel kosten wie eines mit Filiale. Konten, die ganz ohne Bedingung gratis sind, findest du unter {c["liste"]("ohne-geldeingang", "Gratis-Girokonten ohne Geldeingang")}.')))
    secs.append(('Sicherheit beim Onlinebanking', _p(
        f'Direktbanken sind genauso sicher wie Filialbanken. Für dein Guthaben gilt dieselbe gesetzliche Einlagensicherung: 100.000 € pro Person und Bank. Viele Banken sind zusätzlich Mitglied in einem freiwilligen Sicherungsfonds ihres Verbands. Mehr im Ratgeber {c["rg"]("einlagensicherung", "Einlagensicherung")}.',
        zt,
        'Das größere Risiko sind Betrüger, die dich anrufen oder anschreiben. Seit der EU-Zahlungsdiensterichtlinie PSD2 brauchst du für Logins und Zahlungen zwei Faktoren, etwa Passwort und Freigabe in der App. Betrüger versuchen deshalb, dich zur Freigabe zu überreden: mit falschen SMS, gefälschten Websites oder Anrufen angeblicher Bankmitarbeiter.',
        _ul('Deine Bank fragt dich nie nach PIN, TAN oder Passwort.',
            'Gib in der App nur frei, was du selbst gerade ausgelöst hast, und lies den Text der Freigabe.',
            'Ruf im Zweifel selbst bei der Bank an, unter der Nummer von deren Website oder deiner Karte, nicht unter der aus der SMS.',
            'Karte weg? Sperr sie in der App oder über den Sperr-Notruf 116 116.'),
        'Bei nicht autorisierten Zahlungen trägst du höchstens 50 € selbst, wenn du nicht grob fahrlässig gehandelt hast (§ 675v BGB). Melde den Verlust sofort. Für alles, was danach passiert, haftest du nicht mehr.',
        'Sicher sein muss auch dein Gerät: Halte Betriebssystem und Banking-App aktuell, nutze eine Bildschirmsperre und installiere Apps nur aus den offiziellen Stores.')))
    secs.append(('Quellen', _quellen(c, [
        ('https://www.gesetze-im-internet.de/bgb/__675v.html', 'BGB § 675v: Haftung bei nicht autorisierten Zahlungen'),
        ('https://www.gesetze-im-internet.de/zkg/', 'Zahlungskontengesetz (ZKG): Kontowechselhilfe'),
        ('https://www.edb-banken.de/', 'Entschädigungseinrichtung deutscher Banken'),
        ('https://einlagensicherungsfonds.de/', 'Einlagensicherungsfonds des Bankenverbands'),
        ('https://www.bsi.bund.de/', 'Bundesamt für Sicherheit in der Informationstechnik: Onlinebanking'),
        ('https://www.bafin.de/', 'BaFin: Verbraucherschutz'),
    ], d['X'] if d else [])))
    faq = [
        ('Wie eröffne ich ein Konto bei einer Direktbank?', 'Online in wenigen Schritten. Deine Identität bestätigst du per Video-Chat mit Ausweis, mit der Online-Ausweisfunktion deines Personalausweises oder per Postident in einer Postfiliale. Danach kommen Karte und Zugangsdaten per Post oder direkt in die App.'),
        ('Bekomme ich bei einer Direktbank Kontoauszüge für Vermieter oder Behörden?', 'Ja. Kontoauszüge stehen als PDF im elektronischen Postfach und lassen sich ausdrucken oder weiterleiten. Papierauszüge per Post kosten bei manchen Banken extra.'),
        ('Gibt es bei Direktbanken persönliche Beratung?', 'Am Telefon, per Chat oder Video, aber nicht vor Ort. Für Baufinanzierungen arbeiten manche Direktbanken mit Vermittlern zusammen, die dich auch persönlich treffen.'),
        ('Was mache ich, wenn die App einer Direktbank ausfällt?', 'Nutze das Onlinebanking im Browser oder die Telefon-Hotline. Kartenzahlungen funktionieren meist weiter, weil sie über die Kartennetze laufen. Für den Notfall schadet etwas Bargeld oder eine zweite Karte von einer anderen Bank nicht.'),
        ('Eignet sich eine Direktbank für Selbstständige?', f'Für private Konten nur, wenn die Bank die geschäftliche Nutzung erlaubt. Viele Direktbanken haben eigene Geschäftskonten oder schließen Selbstständige aus. Mehr im Ratgeber {c["rg"]("konto-selbststaendige", "Konto für Selbstständige")}.'),
    ]
    lede = (f'Direktbanken haben keine Filialen, dafür oft niedrige Gebühren und gutes Onlinebanking. Hier vergleichen wir {_n(len(d["X"]), "Konto", "Konten")} von {_n(len(d["ban"]), "Direktbank", "Direktbanken")} in Deutschland und zeigen, wo die Unterschiede liegen.'
            if d else 'Direktbanken haben keine Filialen, dafür oft niedrige Gebühren und gutes Onlinebanking. Hier zeigen wir, welche Konten sich lohnen und wo die Unterschiede liegen.')
    return dict(lede=lede, secs=secs, faq=faq)


def _direktbanken_at(c):
    d = _direkt_daten(c)
    secs = []
    secs.append(('Direktbank, Filialbank, Neobank: die Unterschiede', _p(
        'Eine Direktbank betreut dich nur online und telefonisch. Sie hat keine Filiale, in die du mit einer Frage gehen kannst. Anders als Neobanken sind Direktbanken oft Teil einer bekannten Bankengruppe und bieten neben dem Konto auch Sparprodukte, Wertpapiere und teils Kredite an.',
        'Die Grenzen verschwimmen, weil auch Filialbanken heute gute Apps haben. Der Kern bleibt: Bei einer Direktbank zahlst du nicht für ein Filialnetz, das du nicht nutzt.',
        'Für dich zählt am Ende, was du von einer Bank brauchst. Wer einmal im Jahr eine Frage hat und sonst alles am Handy erledigt, zahlt bei einer Filialbank für etwas, das er kaum nutzt. Wer regelmäßig Bargeld bringt oder Beratung schätzt, ist bei einer Direktbank falsch.')
        + _tbl(['Merkmal', 'Filialbank', 'Direktbank', 'Neobank'], [
            ['Beratung vor Ort', 'ja', 'nein', 'nein'],
            ['Kontoeröffnung', 'Filiale oder online', 'online, per Video-Identifikation oder je nach Bank mit ID Austria', 'in der App, meist per Video-Identifikation'],
            ['Karte', 'Debitkarte (Bankomatkarte)', 'Debitkarte', 'Debitkarte, oft zuerst virtuell'],
            ['IBAN', 'österreichisch', 'meist österreichisch', 'oft aus dem Sitzland der Bank'],
            ['Angebot', 'Konto, Sparen, Kredite, Wohnbau, Beratung', 'Konto, Sparen, Wertpapiere, teils Kredite', 'Konto, teils Sparen und Wertpapiere'],
            ['Bargeld einzahlen', 'am Schalter oder Automaten', 'umständlich', 'kaum möglich'],
        ])
        + _p(f'Mehr zu den App-Banken findest du in der Liste {c["liste"]("neobanken", "Neobanken")}.',
        'Rechtlich gibt es keinen Unterschied: Für Direktbanken gelten dieselben Gesetze wie für Filialbanken, vom VZKG bis zur Einlagensicherung.')))
    if d:
        extra = ''
        if d['md'] is not None and d['mf'] is not None and d['fil']:
            extra = 'Zum Vergleich: ' + _vgl_satz(c, d['md'], d['mf'], 'der Direktbanken in dieser Liste')
        if d['ausl']:
            extra += f' {_und([E(b) for b in d["ausl"]])} {"vergibt" if len(d["ausl"]) == 1 else "vergeben"} laut unseren Daten keine österreichische IBAN.'
        secs.append(('Die Direktbanken in der Liste', _p(_direkt_satz(c, d, True), extra) + _direkt_tab(c, d, True)
                     + _p('Die Jahreskosten stammen aus unserem Standardfall laut Methodik. Erfüllst du die Bedingung für das Gratis-Konto nicht, zahlst du das Kontoführungsentgelt aus der zweiten Spalte.')))
    secs.append(('Was für eine Direktbank spricht und was dagegen', _p(
        '<b>Dafür:</b>',
        _ul('Niedrigeres oder gar kein Kontoführungsentgelt, wenn dein Gehalt oder deine Pension aufs Konto kommt.',
            'Alles rund um die Uhr erledigen, ohne Öffnungszeiten.',
            'Wertpapiere und Sparpläne oft günstiger als bei der Hausbank.',
            'Kontowechselservice nach dem VZKG: Die neue Bank holt Daueraufträge und Lastschriften von der alten.'),
        '<b>Dagegen:</b>',
        _ul('Kein Schalter für Bargeld, Münzen oder Erlagscheine.',
            'Bei Problemen telefonisch, mit Warteschleife zu Stoßzeiten.',
            'Die Gratis-Bedingung hängt oft an Gehalt oder Pension. Wer Arbeitslosengeld, Kinderbetreuungsgeld oder Studienbeihilfe bekommt, sollte prüfen, ob das zählt.',
            'Für eine Wohnbaufinanzierung fehlt das Gespräch vor Ort, auch wenn manche Direktbanken Kredite telefonisch oder online beraten.'),
        'Unterm Strich ist eine Direktbank vor allem eine Preisfrage. Die Leistung ist vergleichbar, nur der Weg dorthin ist ein anderer.')))
    secs.append(('Bargeld in Österreich: Bankomat, Kassa, Einzahlung', _p(
        'In Österreich wird noch viel bar bezahlt. Mit der Debitkarte einer Direktbank hebst du am Bankomaten ab wie mit jeder anderen Karte. An Geräten der Banken ist das meist kostenlos, bei Geräten unabhängiger Betreiber kann ein Entgelt anfallen. Das wird dir vor der Auszahlung angezeigt, dann kannst du noch abbrechen.',
        'Bargeld bekommst du auch an der Supermarktkassa: Bei einigen Handelsketten kannst du beim Bezahlen mit Karte Geld mitnehmen.',
        'Einzahlen ist der Schwachpunkt. Direktbanken haben keine eigenen Kassen. Manche lassen Einzahlungen an Automaten einer Partnerbank zu, oft gegen Entgelt. Sonst bleibt der Umweg über ein zweites Konto bei einer Filialbank. Wer Bargeld aus Trinkgeld, Vermietung oder einem Marktstand hat, sollte das vor dem Wechsel klären.',
        'Münzen sind ein eigenes Thema. Wer etwa ein Sparschwein leert, braucht eine Bank mit Münzzählautomat. Bei Direktbanken gibt es das nicht. Wer dagegen überwiegend mit Karte oder Handy zahlt, merkt den Unterschied zur Filialbank im Alltag kaum.',
        'Für den Urlaub außerhalb der Eurozone zählen Entgelt pro Behebung und Wechselkurs. Was jedes Konto hier verlangt, steht im Vergleich unter Bargeld.')))
    secs.append(('Checkliste für die Wahl', _p(
        _ul('<b>Gratis-Bedingung:</b> Zählt nur Gehalt und Pension oder jeder Eingang? Was passiert in Monaten ohne Eingang, etwa in der Karenz?',
            '<b>Kontoführungsentgelt pro Quartal:</b> Rechne aufs Jahr hoch und addiere Kartenentgelt, Buchungszeilen und Kontoauszüge per Post.',
            f'<b>Überziehungsrahmen:</b> Sollzinsen und Überschreitungszinsen vergleichen. Mehr dazu im Ratgeber {c["rg"]("kontoueberziehung", "Kontoüberziehung")}.',
            '<b>Karte:</b> Debit Mastercard oder Visa Debit? Funktionieren Apple Pay oder Google Pay?',
            '<b>IBAN:</b> Eine österreichische IBAN macht dir das Leben mit Lohnverrechnung und Behörden am leichtesten, auch wenn eine IBAN aus einem anderen EU-Land rechtlich gleichwertig ist.',
            '<b>Erreichbarkeit:</b> Hotline-Zeiten, Chat, Rückruf, Kartensperre in der App.',
        '<b>Wertpapiere:</b> Wenn du ein Depot willst, vergleich Ordergebühren und Depotentgelt gleich mit.',
        '<b>Kontoauszüge:</b> Elektronisch im Postfach ist meist gratis, per Post kostet es bei vielen Banken extra.',
        f'<b>Gemeinschaftskonto:</b> Wenn ihr zu zweit ein Konto wollt, prüf, ob die Bank das anbietet. Eine Übersicht steht unter {c["liste"]("gemeinschaftskonto", "Gemeinschaftskonten")}.'),
        'Rechenbeispiel Überziehung: Bist du im Schnitt drei Monate im Jahr mit 800 € im Minus, kostet das bei 7 % Sollzinsen rund 14 € und bei 11 % rund 22 €. Wer selten ins Minus rutscht, schaut eher aufs Kontoführungsentgelt.')))
    secs.append(('So wechselst du zu einer Direktbank', _p(
        'Das VZKG gibt dir einen Anspruch auf einen Kontowechselservice, wenn beide Konten in Österreich geführt werden. Die neue Bank erledigt dabei das meiste: Mit deiner Ermächtigung holt sie bei der alten Bank die Liste der Daueraufträge und Lastschriften, richtet die Daueraufträge neu ein und informiert auf Wunsch die Zahlungspartner.',
        _ol('Konto online eröffnen, Identität per Video oder ID Austria bestätigen.',
            'Die Ermächtigung für den Kontowechsel erteilen, meist direkt im Onlinebanking.',
            'Arbeitgeber oder Pensionsversicherung die neue IBAN mitteilen, falls das nicht die Bank übernimmt.',
            'Ein, zwei Monate beide Konten laufen lassen, damit auch Quartals- und Jahresabbuchungen umgestellt sind.',
            'Das alte Konto kündigen. Nach sechs Monaten Laufzeit darf die Bank für die Kündigung kein Entgelt verlangen.'),
        f'Mehr Details im Ratgeber {c["rg"]("girokonto-wechseln", "Girokonto wechseln")}. Bei einer Bank mit Sitz im Ausland gilt der Kontowechselservice nach VZKG nicht, dann stellst du Daueraufträge und Lastschriften selbst um.',
        'Plane den Wechsel in einem ruhigen Monat, nicht kurz vor dem Urlaub oder einer großen Zahlung. Dann fällt es weniger ins Gewicht, wenn eine Lastschrift einmal noch beim alten Konto landet.')))
    secs.append(('Für wen eine Direktbank passt', _p(
        'Wer ein regelmäßiges Gehalt oder eine Pension bekommt und Bankgeschäfte am Handy erledigt, spart bei einer Direktbank meist am meisten. Manche bieten eigene Pensionskonten mit ähnlichen Bedingungen an.',
        f'Für junge Leute ist die Kontoführung oft bis zu einer Altersgrenze gratis. {_alt_satz(d)}',
        'Gut passt eine Direktbank auch für Menschen, die oft umziehen, zwischen Wien und den Bundesländern pendeln oder eine Zeit lang im Ausland arbeiten. Die Bank ist überall gleich erreichbar, die nächste Filiale spielt keine Rolle.',
        f'Für Familien kann eine Kombination sinnvoll sein: die Erwachsenen bei der Direktbank, das Jugendkonto bei einer Bank mit Filiale in der Nähe, damit die Kinder auch einmal selbst hingehen können. Passende Konten stehen unter {c["liste"]("kinder-jugendkonto", "Kinder- und Jugendkonten")}.',
        'Wer unsicher ist, testet eine Direktbank erst als Zweitkonto, etwa für ein Sparkonto oder ein Depot, und zieht mit dem Gehaltskonto später nach.',
        f'Weniger passt sie für Selbstständige mit Bargeld-Einnahmen, für Menschen, die Beratung zu Wohnbau oder Vorsorge vor Ort wollen, und für alle, die sich mit Apps schwertun. Dann ist eine Filialbank oder eine Kombination aus beiden die bessere Wahl. Günstige Konten aller Banken findest du unter {c["liste"]("kostenlos", "kostenlose Girokonten")}.')))
    secs.append(('Sicherheit, Einlagensicherung und Haftung', _p(
        'Eine Direktbank unterliegt derselben Aufsicht wie jede andere Bank, in Österreich der FMA und bei großen Instituten zusätzlich der Europäischen Zentralbank. Guthaben ist bis 100.000 € pro Person und Bank gesetzlich gesichert. Bei Privatbanken, Volksbanken und Hypos zahlt im Ernstfall die Einlagensicherung AUSTRIA, Sparkassen und Raiffeisenbanken haben eigene Sicherungseinrichtungen. Hat eine Bank ihren Sitz in einem anderen EU-Land, gilt die Einlagensicherung dort.',
        f'Wie das genau funktioniert, steht im Ratgeber {c["rg"]("einlagensicherung", "Einlagensicherung")}.',
        'Phishing-SMS mit Links zu gefälschten Bank-Websites sind ein Dauerthema. Für Freigaben brauchst du seit der Zahlungsdiensterichtlinie PSD2 zwei Faktoren, meist die App der Bank. Gib nichts frei, das du nicht selbst ausgelöst hast, und klick nie auf Links in Nachrichten, die angeblich von deiner Bank kommen. Eine verlorene Karte sperrst du sofort in der App oder über die Sperrhotline deiner Bank.',
        'Für nicht autorisierte Zahlungen haftest du nach dem Zahlungsdienstegesetz 2018 höchstens mit 50 €, sofern du nicht grob fahrlässig warst (§ 68 ZaDiG 2018). Ab der Sperrmeldung zahlst du nichts mehr.',
        'Halte Smartphone und Banking-App aktuell, nutze eine Displaysperre und lade Apps nur aus den offiziellen Stores. Und Vorsicht bei Anrufen: Echte Bankmitarbeiter verlangen nie, dass du am Telefon einen Code nennst oder eine Zahlung freigibst.')))
    secs.append(('Quellen', _quellen(c, [
        ('https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20009550', 'Rechtsinformationssystem des Bundes (RIS): Verbraucherzahlungskontogesetz'),
        ('https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20010182', 'RIS: Zahlungsdienstegesetz 2018'),
        ('https://www.fma.gv.at/', 'Finanzmarktaufsicht (FMA)'),
        ('https://www.einlagensicherung.at/', 'Einlagensicherung AUSTRIA'),
        ('https://www.oenb.at/', 'Oesterreichische Nationalbank'),
        ('https://www.arbeiterkammer.at/', 'Arbeiterkammer: Bankenrechner und Konsumentenschutz'),
        ('https://eur-lex.europa.eu/eli/reg/2024/886/oj', 'EU-Verordnung 2024/886 über Echtzeitüberweisungen'),
    ], d['X'] if d else [])))
    sfaq = 'Die meisten Banken bieten nach einer Bonitätsprüfung einen an. Die Höhe richtet sich nach deinem regelmäßigen Eingang.'
    if d:
        m = [k for k in d['X'] if k.get('sollzins') is not None]
        sfaq = f'Bei {len(m)} der {len(d["X"])} Konten in dieser Liste nennt die Bank einen Sollzins für den Überziehungsrahmen. Ob und wie hoch du ihn bekommst, entscheidet die Bank nach einer Bonitätsprüfung, meist abhängig von deinem regelmäßigen Eingang.'
    faq = [
        ('Bekomme ich bei einer Direktbank einen Überziehungsrahmen?', sfaq),
        ('Wie identifiziere ich mich für ein Konto bei einer Direktbank?', 'Meist per Video-Identifikation mit Reisepass oder Personalausweis, je nach Bank auch mit ID Austria. Manche bieten noch die Identifikation per Post oder über eine Partnerstelle an.'),
        ('Wie schnell ist eine Überweisung zwischen Filialbank und Direktbank da?', 'Eine normale SEPA-Überweisung ist spätestens am nächsten Bankwerktag gutgeschrieben. Seit Oktober 2025 müssen Banken in der Eurozone Echtzeitüberweisungen senden können, zum selben Preis wie eine normale Überweisung. Dann ist das Geld in Sekunden da.'),
        ('Muss ich mein altes Konto sofort kündigen?', f'Nein. Du kannst beide Konten eine Zeit lang parallel führen, bis alle Daueraufträge und Lastschriften umgestellt sind. Bedenke nur, dass du so lange zweimal Kontoführungsentgelt zahlst. Wie der Wechsel geht, steht im Ratgeber {c["rg"]("girokonto-wechseln", "Girokonto wechseln")}.'),
        ('Kann ich bei einer Direktbank Erlagscheine einzahlen?', 'Nicht am Schalter, weil es keinen gibt. Zahlscheine begleichst du per Überweisung in der App, meist durch Scannen des QR-Codes am Erlagschein.'),
    ]
    lede = (f'Direktbanken führen dein Konto ohne Filiale, per App und Website. Hier vergleichen wir {_n(len(d["X"]), "Konto", "Konten")} von {_n(len(d["ban"]), "Direktbank", "Direktbanken")}, die du in Österreich eröffnen kannst.'
            if d else 'Direktbanken führen dein Konto ohne Filiale, per App und Website. Hier erfährst du, für wen sich das lohnt und worauf du achten solltest.')
    return dict(lede=lede, secs=secs, faq=faq)


# ---------- Neobanken ----------
def _neo_daten(c):
    X = c['lists'].get('neobanken') or []
    if not X:
        return None
    rows, by = _neo_rows(c, X)
    frei, bez, frei_teuer = _tarife(c, X)
    fremd_es = [b for b, ks in by.items() if _es_land(ks[0]) and _es_land(ks[0]) != c['N']]
    lokal_iban = [b for b, ks in by.items() if any(k.get('iban') == c['code'] for k in ks)]
    fremd_iban = [b for b in by if b not in lokal_iban]
    iban_trotz = [b for b, ks in by.items() if b in lokal_iban and b in fremd_es]
    treu = [b for b, ks in by.items() if 'treuhand' in (ks[0].get('einlagensicherung') or '').lower()]
    sz = [b for b, ks in by.items() if any(k.get('sollzins') is not None for k in ks)]
    billig = min(X, key=_k)
    return dict(X=X, rows=rows, by=by, frei=frei, bez=bez, frei_teuer=frei_teuer, fremd_es=fremd_es, lokal_iban=lokal_iban,
                fremd_iban=fremd_iban, iban_trotz=iban_trotz, treu=treu, sz=sz, billig=billig)


def _tarif_satz(c, d):
    s = ''
    if d['frei']:
        s += f'In dieser Liste {"gibt es" if len(d["frei"]) != 1 else "gibt es"} {_n(len(d["frei"]), "Tarif", "Tarife")} ohne Kontoführungsgebühr'
        s += f' und {_n(len(d["bez"]), "Bezahltarif", "Bezahltarife")}' if d['bez'] else ''
        s += '. '
    if len(d['bez']) > 1:
        lo = min(k['kf_jahr'] for k in d['bez'])
        hi = max(k['kf_jahr'] for k in d['bez'])
        s += f'Die Bezahltarife kosten zwischen {c["eur"](lo)} € und {c["eur"](hi)} € im Jahr.'
    return s


def _neobanken_de(c):
    d = _neo_daten(c)
    secs = []
    secs.append(('Was eine Neobank ist', _p(
        'Neobanken sind Banken, die vom ersten Tag an für das Smartphone gebaut wurden. Kontoeröffnung in der App, Ausweis per Video, die Karte zuerst virtuell im Handy und ein paar Tage später als Plastik im Briefkasten. Jede Kartenzahlung erscheint sofort als Push-Nachricht, die Karte sperrst du mit einem Fingertipp.',
        'Hinter dem Begriff stecken sehr verschiedene Firmen. Manche haben eine eigene Vollbanklizenz, manche führen die Konten über eine Partnerbank, manche sitzen gar nicht in Deutschland, sondern in einem anderen EU-Land und bieten ihre Konten hier über den europäischen Pass an. Im Alltag merkst du davon nichts. Wichtig wird es erst bei Einlagensicherung, Steuern und Beschwerden.',
        'Typisch ist das Tarifmodell: ein Gratis-Konto als Einstieg und mehrere Bezahltarife mit mehr Unterkonten, Versicherungen, günstigeren Abhebungen oder einer Karte aus Metall.',
        'Bekannt geworden sind Neobanken mit einem Versprechen: Banking so einfach wie eine Messenger-App. Das hat die ganze Branche verändert. Push-Nachrichten, Kartensperre per App und Echtzeitüberweisungen bieten heute auch viele klassische Banken. Der Vorsprung ist kleiner geworden, das Preismodell aber oft noch ein anderes.',
        _tarif_satz(c, d) if d else '')))
    secs.append(('Neobank, Direktbank, Filialbank: wo die Unterschiede liegen', _p(
        f'Direktbanken gibt es seit Jahrzehnten. Sie haben auch keine Filialen, bieten aber meist die volle Palette mit Dispo, Ratenkredit, Baufinanzierung und Depot, und ihr Onlinebanking funktioniert im Browser genauso wie in der App. Neobanken sind enger gestrickt: Vieles geht nur in der App, und den Kundenservice erreichst du meist per Chat. Die etablierten Direktbanken findest du unter {c["liste"]("direktbanken", "Direktbanken")}.',
        'Filialbanken wie Sparkassen, Volksbanken und Großbanken bieten Beratung vor Ort, Einzahlautomaten und Schließfächer. Dafür kostet das Konto meist eine monatliche Gebühr.',
        'Bei Beschwerden gilt: Für Banken mit Sitz in Deutschland ist die BaFin zuständig, für Banken aus dem EU-Ausland die Aufsicht im Sitzland. Bei deren Zweigniederlassungen in Deutschland beaufsichtigt die BaFin nur einzelne Bereiche.')
        + _tbl(['Merkmal', 'Neobank', 'Direktbank', 'Filialbank'], [
            ['Hauptzugang', 'App', 'Website und App', 'Filiale, Website und App'],
            ['Kundenservice', 'Chat in der App, teils Telefon', 'Telefon und Chat', 'Filiale und Telefon'],
            ['Dispo', 'nicht bei allen', 'meist ja', 'ja'],
            ['Bargeld einzahlen', 'selten, meist über Partner gegen Gebühr', 'über Partner, oft gegen Gebühr', 'am Automaten der Bank'],
            ['Girocard', 'selten', 'teils gegen Aufpreis', 'meist inklusive'],
            ['Preismodell', 'Gratis-Tarif plus Abos', 'gratis unter Bedingungen', 'monatliche Gebühr, teils mit Rabatten'],
        ])))
    if d:
        s = f'In der Liste stehen {_n(len(d["X"]), "Konto", "Konten")} von {_n(len(d["by"]), "Neobank", "Neobanken")}. '
        if d['iban_trotz']:
            s += f'Aufgepasst: {_und([E(b) for b in d["iban_trotz"]])} {"vergibt" if len(d["iban_trotz"]) == 1 else "vergeben"} eine deutsche IBAN, die gesetzliche Einlagensicherung liegt laut Bank aber in einem anderen Land.'
        secs.append(('Sitz, IBAN und Einlagensicherung der Neobanken in der Liste', _p(s)
                     + _tbl(['Bank', 'IBAN', 'Einlagensicherung laut Bank', 'Konten in der Liste', 'Kontoführung ab'], d['rows'])
                     + _p('Die Angaben stammen aus den Bedingungen der Banken. Einzelheiten zu jedem Konto stehen im Vergleich.')))
    secs.append(('Einlagensicherung: Sitzland zählt, nicht die IBAN', _p(
        'Die IBAN sagt nur, in welchem Land das Konto technisch geführt wird. Welche Einlagensicherung greift, hängt davon ab, wo die Bank ihren Sitz hat und welche Lizenz das Konto führt. Eine Bank aus Litauen kann dir eine deutsche IBAN geben, im Ernstfall zahlt trotzdem die litauische Einlagensicherung.',
        'Gesetzlich sind in der ganzen EU 100.000 € pro Person und Bank geschützt, nach einheitlichen Regeln. Die Auszahlung muss innerhalb von sieben Arbeitstagen erfolgen. Hat die Bank eine Zweigniederlassung in Deutschland, ist die deutsche Einlagensicherung deine Anlaufstelle, das Geld kommt aber aus dem Sicherungssystem des Sitzlands.',
        'Ein Sonderfall sind Anbieter, die Kundengelder nicht selbst halten, sondern bei Partnerbanken oder in Geldmarktfonds anlegen. Dann gilt die Einlagensicherung der jeweiligen Partnerbank. Fondsanteile sind gar nicht durch die Einlagensicherung geschützt. Sie werden getrennt vom Vermögen des Anbieters verwahrt, können aber im Wert schwanken. Lies in den Bedingungen nach, wo dein Geld liegt.',
        'Ein Rechenbeispiel: Du hast 60.000 € bei einer Neobank aus Litauen und 70.000 € bei einer deutschen Bank. Beide Guthaben sind voll geschützt, weil jede Bank für sich zählt. Lägen die 130.000 € bei einer einzigen Bank, wären 30.000 € über der gesetzlichen Grenze.',
        'Prüfen kannst du das selbst. Im Impressum und im Preis- und Leistungsverzeichnis steht, welche Gesellschaft dein Konto führt. Den Namen gibst du in die Unternehmensdatenbank der BaFin ein. Dort siehst du, ob die Bank in Deutschland zugelassen ist oder über den EU-Pass tätig wird.',
        f'Freiwillige Sicherungsfonds der deutschen Bankenverbände, die über 100.000 € hinaus schützen, gibt es bei Banken aus dem Ausland in der Regel nicht. Bei einem normalen Kontostand spielt das keine Rolle, bei großen Beträgen schon. Mehr im Ratgeber {c["rg"]("einlagensicherung", "Einlagensicherung")}.')))
    ft = ''
    if d and d['frei_teuer']:
        ft = f'Bei {len(d["frei_teuer"])} der {len(d["frei"])} Gratis-Tarife in dieser Liste fallen in unserem Standardfall trotzdem Kosten an, etwa für die Karte oder für Bargeld.'
    secs.append(('Vorteile und Nachteile von Neobanken', _p(
        '<b>Stark sind Neobanken hier:</b>',
        _ul('Konto in wenigen Minuten eröffnet, ohne Termin und ohne Papier.',
            'Push-Nachricht bei jeder Buchung, Kartensperre und Limits per Fingertipp.',
            'Oft günstige Kartenzahlungen in fremder Währung.',
            f'Unterkonten oder Spaces für Budget und Sparziele, teils mit anderen geteilt. Mehr unter {c["liste"]("unterkonten", "Girokonten mit Unterkonten")}.',
            'Apple Pay und Google Pay ab dem ersten Tag.'),
        '<b>Schwächen:</b>',
        _ul('Kundenservice meist per Chat. Wird ein Konto wegen einer Prüfung gesperrt, kann es dauern, bis du wieder Zugriff hast.',
            'Bargeld einzahlen ist schwierig oder teuer.',
            'Ein Dispo fehlt oft oder gibt es nur nach Bonitätsprüfung.',
            'Selten eine Girocard, was bei manchen kleinen Händlern stört.',
            'Im Gratis-Tarif kosten Abhebungen oder die Plastikkarte oft extra.'),
        'Wie gut eine Neobank ist, merkst du oft erst im Problemfall. Lies vor der Eröffnung, wie der Kundenservice erreichbar ist: nur Chat, Chat mit Rückruf oder auch Telefon? Gibt es eine Notfallnummer für die Kartensperre, falls dein Handy weg ist?',
        'Neobanken ändern ihr Angebot außerdem schneller als klassische Banken: neue Tarife, neue Preise, gestrichene Leistungen. Änderungen der Entgelte muss dir die Bank zwei Monate vorher mitteilen. Lies diese Mitteilungen, statt sie wegzuklicken.',
        ft)))
    secs.append(('Was Neobanken wirklich kosten', _p(
        'Gratis heißt bei Neobanken: keine monatliche Gebühr. Kosten entstehen trotzdem, sobald du etwas nutzt, das der Tarif nicht abdeckt. Typisch sind:',
        _ul('Versand oder Ausgabe der physischen Karte',
            'Abhebungen über einem monatlichen Freibetrag oder unter einem Mindestbetrag',
            'Aufschläge beim Währungstausch, bei manchen Anbietern über einer Monatsgrenze oder am Wochenende',
            'Bargeld-Einzahlungen über Partner',
            'Ersatzkarten bei Verlust'),
        'Unser Standardfall rechnet solche Posten mit ein. Deshalb kann ein Gratis-Tarif in der Rangliste mehr kosten als ein Tarif mit kleiner Monatsgebühr, in dem Karte und Abhebungen enthalten sind.'
        + (f' Im Standardfall am günstigsten ist in dieser Liste {c["link"](d["billig"])} mit {_kt(c, d["billig"])} im Jahr.' if d else ''),
        'Bei Bezahltarifen lohnt ein ehrlicher Blick auf die Extras. Eine Auslandsreise-Krankenversicherung kostet einzeln oft nur einen kleinen Betrag im Jahr, ein Tarif lohnt sich selten allein deshalb. Rechne nur mit den Leistungen, die du tatsächlich nutzt.',
        'Dazu kommen Kosten, die gar nicht von der Bank stammen. Manche Automatenbetreiber verlangen ein eigenes Entgelt. Und bei Kartenzahlungen außerhalb des Euroraums bieten Terminals oft an, direkt in Euro abzurechnen. Lehne das ab und zahle in Landeswährung, der Kurs vor Ort ist meist schlechter als der deiner Bank.')))
    secs.append(('Eröffnung, Schufa und Steuer-ID', _p(
        'Für die Eröffnung brauchst du in der Regel einen Wohnsitz in Deutschland, einen gültigen Ausweis und ein Smartphone. Die Identität prüft die Bank per Video oder mit dem Online-Ausweis. Dabei fragt sie deine Steuer-Identifikationsnummer ab, weil Banken sie für Meldungen an das Finanzamt erfassen müssen.',
        f'Auch Neobanken fragen oft bei der Schufa an, besonders wenn es um Dispo oder Kreditkarte geht. Wer ein Konto ganz ohne Abfrage sucht, schaut in die Liste {c["liste"]("ohne-schufa", "Girokonten ohne Schufa-Abfrage")}.',
        'Die Eröffnung ist schnell, aber nicht immer sofort fertig. Bei Rückfragen zur Identität oder zur Herkunft größerer Beträge kann es Tage dauern. Plane den Umzug deines Gehaltskontos deshalb nicht auf den letzten Drücker, und lass dein altes Konto laufen, bis alles funktioniert.',
        'Übrigens: Du darfst so viele Girokonten haben, wie du willst. Eine Neobank neben deiner Hausbank ist völlig normal. Nur ein P-Konto darf es nicht doppelt geben.')))
    secs.append(('Für wen eine Neobank passt', _p(
        'Gut passt eine Neobank, wenn du das Smartphone sowieso für alles nutzt, viel reist und im Ausland mit Karte zahlst, oder ein zweites Konto für Budget und Urlaub suchst. Viele nutzen eine Neobank genau so: Gehalt und Lastschriften laufen über ein klassisches Konto, die Neobank ist das Konto für den Alltag oder die Reise.',
        'Weniger gut passt sie, wenn du regelmäßig Bargeld einzahlst, einen Dispo brauchst, gern mit einem Menschen am Schalter sprichst oder ein Konto für ein Gewerbe suchst.',
        'Ein Tipp zum Tarif: Fang mit dem Gratis-Tarif an. Upgrades gehen jederzeit, Downgrades teils erst nach einer Mindestlaufzeit. Rechne vor dem Upgrade, ob du die Extras wirklich nutzt. Eine Reiseversicherung im Tarif lohnt nur, wenn du nicht schon eine hast.',
        'Ein typisches Setup sieht so aus: Das Gehalt kommt aufs Hauptkonto bei einer Direkt- oder Filialbank. Am Monatsanfang geht ein fester Betrag per Dauerauftrag auf die Neobank. Mit deren Karte zahlst du im Alltag und auf Reisen. So hast du dein Budget im Griff, und fällt eine Bank einmal aus, bleibt dir die andere.',
        f'Für Studierende und Azubis ist eine Neobank oft ein guter Start, weil der Gratis-Tarif ohne Geldeingang auskommt. Vergleich trotzdem mit den Studentenkonten klassischer Banken, siehe {c["liste"]("studenten", "Girokonten für Studierende")}.')))
    secs.append(('Quellen', _quellen(c, [
        ('https://eur-lex.europa.eu/eli/dir/2014/49/oj', 'EU-Richtlinie 2014/49 über Einlagensicherungssysteme'),
        ('https://eur-lex.europa.eu/eli/reg/2012/260/oj', 'EU-Verordnung 260/2012 (SEPA), Art. 9: Erreichbarkeit von Konten'),
        ('https://www.edb-banken.de/', 'Entschädigungseinrichtung deutscher Banken'),
        ('https://www.bafin.de/', 'BaFin: Unternehmensdatenbank und Verbraucherbeschwerden'),
        ('https://www.gesetze-im-internet.de/estg/__20.html', 'Einkommensteuergesetz § 20: Kapitalerträge'),
    ], d['X'] if d else [])))
    faq = [
        ('Muss mein Arbeitgeber eine IBAN aus Litauen oder den Niederlanden akzeptieren?', 'Ja. Die SEPA-Verordnung der EU verbietet es, eine Zahlung abzulehnen, nur weil das Konto in einem anderen EU-Land geführt wird. Klappt es trotzdem nicht, weis den Arbeitgeber freundlich darauf hin. Die Verbraucherzentralen helfen, wenn das nichts bringt.'),
        ('Muss ich Zinsen von einer ausländischen Neobank selbst versteuern?', 'In der Regel ja. Eine Bank ohne Sitz in Deutschland zieht keine Abgeltungsteuer ab und nimmt keinen Freistellungsauftrag an. Du trägst die Zinsen in der Anlage KAP deiner Steuererklärung ein. Der Sparerpauschbetrag gilt dabei trotzdem.'),
        ('Darf eine Neobank mein Konto einfach sperren?', 'Bei Verdacht auf Geldwäsche oder Betrug muss jede Bank Zahlungen prüfen und darf das Konto während der Prüfung einfrieren. Frag beim Kundenservice nach dem Grund und schreib alles schriftlich. Hilft das nicht, kannst du dich an die Aufsicht oder die Schlichtungsstelle im Sitzland der Bank wenden, bei deutschen Banken an die BaFin.'),
        ('Gibt es bei Neobanken eine Girocard?', 'Selten. Meist bekommst du eine Debitkarte von Visa oder Mastercard. Die akzeptieren fast alle Händler, an einzelnen Kassen und Automaten geht aber nur die Girocard. Wer darauf angewiesen ist, behält ein zweites Konto mit Girocard.'),
        ('Was passiert mit meinem Geld, wenn eine Neobank pleitegeht?', 'Bis 100.000 € zahlt die gesetzliche Einlagensicherung des Landes, in dem die Bank ihren Sitz hat, innerhalb von sieben Arbeitstagen. Liegen deine Gelder bei Partnerbanken oder in Geldmarktfonds, gelten deren Regeln. Welche Sicherung bei welcher Bank greift, steht in der Tabelle oben.'),
    ]
    lede = (f'Neobanken funktionieren fast nur über das Smartphone. Hier vergleichen wir {_n(len(d["X"]), "Konto", "Konten")} von {_n(len(d["by"]), "Neobank", "Neobanken")} in Deutschland und erklären, worauf du bei Sitzland, IBAN und Einlagensicherung achten solltest.'
            if d else 'Neobanken funktionieren fast nur über das Smartphone. Hier erfährst du, worauf du bei Sitzland, IBAN und Einlagensicherung achten solltest.')
    return dict(lede=lede, secs=secs, faq=faq)


def _neobanken_at(c):
    d = _neo_daten(c)
    secs = []
    secs.append(('So funktionieren Neobanken', _p(
        'Du lädst eine App, fotografierst deinen Ausweis, machst ein kurzes Video-Selfie, und wenige Minuten später hast du ein Konto mit virtueller Karte im Handy. So läuft es bei Neobanken. Eine Filiale oder ein Formular auf Papier gibt es nicht. Vieles, wofür du bei der Hausbank anrufen müsstest, stellst du selbst in der App ein: Kartenlimits, Online-Zahlungen, Einsatz im Ausland, Sperre.',
        'Viele Neobanken, die in Österreich aktiv sind, sind keine österreichischen Banken. Sie haben ihre Lizenz in Deutschland, Litauen, den Niederlanden oder einem anderen EU-Land und bieten ihre Konten über den europäischen Pass hier an. Das ist erlaubt. Die Aufsicht führt dann die Behörde im Sitzland, nicht die FMA.',
        'Der Kundenservice sitzt oft im Ausland, und manche Dokumente gibt es nur auf Englisch. Prüf vor der Eröffnung, ob dir die Bank Vertrag und Preisliste auf Deutsch zur Verfügung stellt.',
        'Im Alltag fühlt sich eine Neobank an wie jede andere App. Unterschiede zeigen sich bei Fragen, die selten vorkommen: Wer hilft bei einer Kontosperre? Welche Einlagensicherung gilt? Wer zieht die Steuer ab? Genau darum geht es weiter unten.',
        'Für die Eröffnung brauchst du einen gültigen Reisepass oder Personalausweis, ein Smartphone und meist einen Wohnsitz in Österreich. Die Bank fragt außerdem nach deiner steuerlichen Ansässigkeit. Das gehört zum internationalen Informationsaustausch und ist reine Routine.',
        'Das Preismodell ist fast überall gleich: ein Gratis-Tarif als Einstieg und Bezahltarife mit mehr Unterkonten, Versicherungen, günstigeren Behebungen oder einer Metallkarte.',
        _tarif_satz(c, d) if d else '')))
    if d:
        s = f'In der Liste stehen {_n(len(d["X"]), "Konto", "Konten")} von {_n(len(d["by"]), "Neobank", "Neobanken")}. '
        if d['fremd_iban']:
            s += f'{len(d["fremd_iban"])} von ihnen {"gibt" if len(d["fremd_iban"]) == 1 else "geben"} dir laut unseren Daten keine österreichische IBAN. '
        if d['fremd_es']:
            s += f'Bei {len(d["fremd_es"])} liegt die gesetzliche Einlagensicherung außerhalb Österreichs.'
        secs.append(('IBAN und Einlagensicherung im Überblick', _p(s)
                     + _tbl(['Bank', 'IBAN', 'Einlagensicherung laut Bank', 'Konten in der Liste', 'Kontoführungsentgelt ab'], d['rows'])
                     + _p('Die Angaben stammen aus den Bedingungen der Banken. Anbieter ändern das gelegentlich, etwa wenn sie eine Zweigniederlassung in Österreich eröffnen. Prüf es vor der Eröffnung noch einmal.')))
    secs.append(('Ausländische IBAN: was das im Alltag bedeutet', _p(
        'Seit der SEPA-Umstellung 2014 funktionieren Überweisungen und Lastschriften im ganzen SEPA-Raum gleich. Die SEPA-Verordnung der EU verbietet Arbeitgebern, Versicherungen, Behörden und Händlern, eine Zahlung abzulehnen, nur weil die IBAN aus einem anderen EU-Land stammt. Das nennt man IBAN-Diskriminierung.',
        'In der Praxis klappt das meist, aber nicht immer. Manche Lohnverrechnungen, kleinere Vereine oder Online-Formulare akzeptieren noch immer nur AT-IBANs. Dann hilft ein freundlicher Hinweis auf die Verordnung. Bleibt der Zahlungspartner stur, unterstützt dich die Arbeiterkammer.',
        'Für Familienbeihilfe, Arbeitslosengeld oder Pension gibst du einfach deine IBAN an. Auch öffentliche Stellen müssen Konten aus anderen EU-Ländern akzeptieren.',
        'Das gilt auch für das Finanzamt: Für die Gutschrift aus der Arbeitnehmerveranlagung kannst du ein Konto in einem anderen EU-Land angeben.',
        'Wer auf Nummer sicher gehen will, nutzt für Gehalt und Lastschriften ein Konto mit AT-IBAN und die Neobank als Zweitkonto für Alltag und Reisen. Das ist in Österreich ein häufiges Modell.',
        'Bei Zinsen zählt der Sitz der Bank. Ohne österreichische Zweigstelle zieht die Bank in der Regel keine KESt ab. Du gibst die Zinsen dann selbst in der Einkommensteuererklärung mit der Beilage E 1kv an. Der Steuersatz für Zinsen aus Bankguthaben bleibt bei 25 %.')))
    tt = ''
    if d and d['treu']:
        tt = f'Bei {_und([E(b) for b in d["treu"]])} liegen die Kundengelder laut Bank teils auf Treuhandkonten bei Partnerbanken. Dann greift die Einlagensicherung der jeweiligen Partnerbank, mit 100.000 € je Partnerbank.'
    secs.append(('Einlagensicherung: worauf es ankommt', _p(
        'Für die Einlagensicherung zählt das Land, in dem die Bank ihren Sitz und ihre Lizenz hat. Ein Konto bei einer deutschen Neobank sichert die Entschädigungseinrichtung deutscher Banken, eines bei einer litauischen Bank die litauische Einlagensicherung. Die Einlagensicherung AUSTRIA ist für diese Banken nicht zuständig.',
        'Der gesetzliche Schutz ist in der EU gleich hoch: 100.000 € pro Person und Bank, Auszahlung innerhalb von sieben Arbeitstagen. Für bestimmte Lebensereignisse, etwa nach dem Verkauf einer privat genutzten Wohnung, nach Heirat, Scheidung oder Pensionsantritt, sieht das österreichische Gesetz zwölf Monate lang einen Schutz bis 500.000 € vor (§ 12 ESAEG). Bei ausländischen Banken gelten die Regeln ihres Sitzlands.',
        'Ein Rechenbeispiel: 50.000 € bei einer Neobank aus den Niederlanden und 80.000 € bei einer österreichischen Bank sind beide voll geschützt, weil jede Bank für sich zählt. Lägen die 130.000 € bei einer Bank, wären 30.000 € über der Grenze.',
        'Prüfen kannst du jede Bank in der Unternehmensdatenbank der FMA. Dort steht, ob ein Institut in Österreich eine Konzession hat, eine Zweigstelle betreibt oder nur über den EU-Pass Dienstleistungen anbietet.',
        'Für die meisten ist das Thema übrigens beruhigend: Wer weniger als 100.000 € bei einer Bank hat, ist überall in der EU gleich geschützt.',
        tt,
        f'Mehr dazu im Ratgeber {c["rg"]("einlagensicherung", "Einlagensicherung")}.')))
    ft = ''
    if d and d['frei_teuer']:
        ft = f'Bei {len(d["frei_teuer"])} der {len(d["frei"])} Gratis-Tarife in dieser Liste entstehen in unserem Standardfall trotzdem Kosten, zum Beispiel für die physische Karte oder Behebungen.'
    secs.append(('Stärken und Schwächen', _p(
        '<b>Das spricht für eine Neobank:</b>',
        _ul('Gratis-Tarife, die oft ohne Gehaltseingang auskommen.',
            'Echtzeit-Benachrichtigung bei jeder Zahlung.',
            'Günstiges Bezahlen in fremden Währungen, oft gut für Reisen.',
            f'Spaces oder Unterkonten zum Sparen. Mehr unter {c["liste"]("unterkonten", "Girokonten mit Unterkonten")}.',
            'Eröffnung in wenigen Minuten.'),
        '<b>Das spricht dagegen:</b>',
        _ul('Oft keine österreichische IBAN.',
            'Kein oder nur ein kleiner Überziehungsrahmen.',
            'Bargeld einzahlen ist kaum möglich.',
            'Service per Chat, persönliche Ansprechpersonen gibt es nicht.',
            'Den Kontowechselservice nach VZKG, bei dem die neue Bank alles für dich umstellt, gibt es nur zwischen Konten in Österreich. Bei einer Bank im Ausland stellst du Daueraufträge und Lastschriften selbst um.'),
        'Neobanken ändern ihre Tarife häufiger als klassische Banken. Änderungen bei den Entgelten muss die Bank dir zwei Monate vorher mitteilen, und du kannst bis dahin kostenlos kündigen.',
        ft)))
    secs.append(('Was der Gratis-Tarif wirklich kostet', _p(
        'Ein Tarif ohne Kontoführungsentgelt ist nicht automatisch kostenlos. Entgelte fallen bei Neobanken oft dort an, wo du sie nicht erwartest: bei der Lieferung der Plastikkarte, bei Behebungen über einem Monatskontingent, beim Wechseln von Fremdwährungen über einer Grenze oder für eine Ersatzkarte.',
        'Unser Standardfall berücksichtigt typische Nutzung inklusive Karte und Bargeld. So siehst du in der Rangliste, was ein Konto im Jahr tatsächlich kostet, nicht nur, was auf dem Preisschild steht.'
        + (f' Am günstigsten ist im Standardfall {c["link"](d["billig"])} mit {_kt(c, d["billig"])} im Jahr.' if d else ''),
        'Bei den Bezahltarifen gilt: Rechne die Extras einzeln. Brauchst du die Versicherungen wirklich, oder hast du sie über eine Kreditkarte oder die Haushaltsversicherung schon? Ist dir eine Metallkarte einen Aufpreis wert? Oft reicht der kleinste Tarif, und das Geld für den großen ist auf einem Sparkonto besser aufgehoben.',
        'Ein Kostenpunkt kommt gar nicht von der Bank: Im Urlaub außerhalb der Eurozone fragen Kassen und Bankomaten oft, ob sie gleich in Euro abrechnen sollen. Wähle immer die Landeswährung. Bei der Umrechnung vor Ort ist der Kurs meist deutlich schlechter als der deiner Bank.',
        'Schau nach dem ersten Monat in die Umsätze, welche Entgelte angefallen sind. Dann weißt du, ob der Tarif zu deiner Nutzung passt.')))
    secs.append(('Kontosperre, Beschwerde, Schlichtung', _p(
        'Neobanken prüfen Zahlungen stark automatisiert. Deshalb kommt es vor, dass ein Konto vorübergehend gesperrt wird, etwa nach einer ungewöhnlich hohen Überweisung. Bei Verdacht auf Geldwäsche muss die Bank Fragen stellen und darf dir den Grund nicht immer nennen.',
        _ul('Antworte schnell und vollständig auf Rückfragen, etwa mit Lohnzettel oder Kaufvertrag.',
            'Halte die Kommunikation fest, am besten mit Bildschirmfotos aus dem Chat.',
            'Führe ein zweites Konto bei einer anderen Bank, damit du in so einer Phase zahlen kannst.',
        'Kündige größere Überweisungen, etwa für ein Auto oder eine Kaution, vorher im Chat an, wenn die Bank das anbietet, und halte Belege bereit.',
            'Hilft der Kundenservice nicht weiter, wende dich an die Aufsicht oder Schlichtungsstelle im Sitzland der Bank. Bei Banken mit Sitz in Österreich sind das die FMA und die Gemeinsame Schlichtungsstelle der österreichischen Kreditwirtschaft.'),
        'Für Streit mit Banken im EU-Ausland gibt es Unterstützung: Das Europäische Verbraucherzentrum Österreich hilft bei grenzüberschreitenden Problemen, und über das Netzwerk FIN-NET findest du die zuständige Schlichtungsstelle im anderen Land.',
        'Welche Stelle für deine Bank zuständig ist, muss sie dir in ihren Vertragsbedingungen nennen.')))
    secs.append(('Für wen sich eine Neobank lohnt', _p(
        'Als Zweitkonto ist eine Neobank für fast jeden einen Blick wert: für Reisen, für ein getrenntes Budget, für Online-Einkäufe mit einer virtuellen Karte, die du nach dem Kauf sperrst.',
        'Ein bewährtes Modell: Das Gehalt kommt auf ein Konto mit AT-IBAN. Am Monatsanfang überweist du per Dauerauftrag einen fixen Betrag auf die Neobank und zahlst damit im Alltag. Bei jeder Zahlung siehst du sofort, wie viel vom Budget noch übrig ist.',
        'Wer viel reist, profitiert am meisten. Kartenzahlungen in fremder Währung sind bei Neobanken oft günstiger als bei klassischen Banken, und eine virtuelle Karte schützt bei Online-Buchungen.',
        'Für Pensionistinnen und Pensionisten ist eine Neobank selten die erste Wahl. Wer Bargeld braucht und gern persönlich nachfragt, ist bei einer Bank mit Filiale meist besser aufgehoben.',
        f'Als einziges Konto passt sie, wenn dein Arbeitgeber oder deine Pensionsversicherung die IBAN problemlos akzeptiert, du kaum Bargeld einzahlst und keinen Überziehungsrahmen brauchst. Für Studierende kann das gut passen. Es lohnt sich aber, auch die Angebote der klassischen Banken zu vergleichen, siehe {c["liste"]("studenten", "Girokonten für Studierende")}.',
        f'Wer sein Gehalt lieber bei einer Bank mit Sitz in Österreich und ohne Filialbesuch führt, schaut in die Liste {c["liste"]("direktbanken", "Direktbanken")}.')))
    secs.append(('Quellen', _quellen(c, [
        ('https://eur-lex.europa.eu/eli/reg/2012/260/oj', 'EU-Verordnung 260/2012 (SEPA), Art. 9: Verbot der IBAN-Diskriminierung'),
        ('https://eur-lex.europa.eu/eli/dir/2014/49/oj', 'EU-Richtlinie 2014/49 über Einlagensicherungssysteme'),
        ('https://www.einlagensicherung.at/', 'Einlagensicherung AUSTRIA'),
        ('https://www.fma.gv.at/', 'Finanzmarktaufsicht (FMA): Unternehmensdatenbank'),
        ('https://www.bmf.gv.at/', 'Bundesministerium für Finanzen: Kapitalertragsteuer und Beilage E 1kv'),
        ('https://www.arbeiterkammer.at/', 'Arbeiterkammer: Konsumentenschutz'),
        ('https://europakonsument.at/', 'Europäisches Verbraucherzentrum Österreich'),
        ('https://finance.ec.europa.eu/consumer-finance-and-payments/retail-financial-services/financial-dispute-resolution-network-fin-net_de', 'FIN-NET: Schlichtung bei Finanzstreitigkeiten in der EU'),
    ], d['X'] if d else [])))
    if d and d['lokal_iban']:
        iq = f'Ja. In unserer Liste vergibt {_und([E(b) for b in d["lokal_iban"]])} eine österreichische IBAN. Die anderen geben dir eine IBAN aus ihrem Sitzland. Prüf das vor der Eröffnung, weil Anbieter es ändern können.'
    elif d:
        iq = 'In unserer Liste vergeben die Neobanken derzeit IBANs aus ihrem Sitzland. Prüf vor der Eröffnung, ob sich das geändert hat, und schau dir sonst die Direktbanken an.'
    else:
        iq = 'Manche Neobanken haben eine Zweigniederlassung in Österreich und vergeben österreichische IBANs, andere nicht. Prüf das vor der Eröffnung in den Bedingungen.'
    oq = 'Das hängt von der Bank ab. Viele Neobanken bieten keinen Überziehungsrahmen an.'
    if d:
        oq = (f'In dieser Liste nennt nur {_und([E(b) for b in d["sz"]])} einen Sollzins für eine Überziehung. Bei den anderen kannst du nur ausgeben, was am Konto ist.'
              if d['sz'] else 'Bei den Neobanken in dieser Liste nennt die Bank keinen Sollzins für eine Überziehung. Du kannst also nur ausgeben, was am Konto ist.')
    faq = [
        ('Gibt es Neobanken mit österreichischer IBAN?', iq),
        ('Muss ich ein Konto bei einer ausländischen Neobank dem Finanzamt melden?', 'Ein eigenes Meldeformular für ein Girokonto im EU-Ausland gibt es nicht. Die Banken melden Kontodaten aber im automatischen Informationsaustausch an die Steuerbehörden ihres Landes, die sie an Österreich weitergeben. Zinsen musst du selbst erklären, wenn keine KESt abgezogen wurde.'),
        ('Funktioniert die Karte einer Neobank an jedem Bankomaten?', 'An fast allen, denn die Karten laufen über Visa oder Mastercard. Wie viele Behebungen gratis sind, hängt vom Tarif ab. Unabhängige Betreiber können zusätzlich ein Entgelt verlangen, das dir vor der Behebung angezeigt wird.'),
        ('Bekomme ich bei einer Neobank einen Überziehungsrahmen?', oq),
        ('Wie kündige ich ein Konto bei einer Neobank?', 'Meist direkt in der App oder über den Chat. Stell vorher Gehalt, Daueraufträge und Lastschriften um und überweise das Guthaben auf ein anderes Konto. Bei Bezahltarifen prüfst du, ob eine Mindestlaufzeit gilt.'),
    ]
    lede = (f'Neobanken sind in Österreich beliebt, sitzen aber oft im Ausland. Hier vergleichen wir {_n(len(d["X"]), "Konto", "Konten")} von {_n(len(d["by"]), "Neobank", "Neobanken")} und zeigen, welche IBAN du bekommst und welche Einlagensicherung gilt.'
            if d else 'Neobanken sind in Österreich beliebt, sitzen aber oft im Ausland. Hier erfährst du, welche IBAN du bekommst und welche Einlagensicherung gilt.')
    return dict(lede=lede, secs=secs, faq=faq)


# ---------- Nachhaltige Banken ----------
def _nh_daten(c):
    X = c['lists'].get('nachhaltige-banken') or []
    if not X:
        return None
    ban = _banken(X)
    billig = min(X, key=_k)
    rows = [[c['link'](k), E(k['_bank'].get('kurz') or k['_bank'].get('text') or 'nachhaltige Bank'), E(c['kfT'](k)), _kt(c, k)] for k in X]
    std = [k for k in X if k['art'] == 'standard']
    alle_std = [k for k in c['alle'] if k['art'] == 'standard']
    mn = _med([_k(k) for k in std])
    ma = _med([_k(k) for k in alle_std])
    online = [k for k in X if k.get('eroeffnung') in ('online', 'beides')]
    sz = [k['sollzins'] for k in X if k.get('sollzins') is not None]
    kk = [k for k in X if k.get('kreditkarte')]
    kki = [k for k in X if k.get('kreditkarte_inkl')]
    s = f'In der Liste stehen {_n(len(X), "Konto", "Konten")} von {_n(len(ban), "Bank", "Banken")}. Am günstigsten ist im Standardfall {c["link"](billig)} mit {_kt(c, billig)} im Jahr.'
    return dict(X=X, ban=ban, rows=rows, mn=mn, ma=ma, online=online, sz=sz, kk=kk, kki=kki, s=s, std=std)


def _nachhaltig_de(c):
    d = _nh_daten(c)
    secs = []
    secs.append(('Was dein Girokonto mit Klima und Gesellschaft zu tun hat', _p(
        'Das Geld auf deinem Girokonto liegt nicht in einem Tresor. Die Bank nutzt Einlagen, um Kredite zu vergeben und Geld anzulegen. Ob damit ein Windpark, eine Schule, ein Kohlekraftwerk oder ein Rüstungsunternehmen finanziert wird, entscheidet die Bank. Bei einer konventionellen Bank hast du darauf keinen Einfluss und erfährst es meist auch nicht.',
        'Nachhaltige Banken drehen das um. Sie legen vorher fest, was sie finanzieren und was nicht, und legen offen, wohin das Geld geht. Manche gehen noch weiter und veröffentlichen ihre Unternehmenskredite einzeln.',
        'Dein Girokonto ist dabei ein kleiner, aber echter Hebel. Für die Bank sind Einlagen eine günstige Quelle für Kredite. Je mehr Menschen ihr Konto bei einer nachhaltigen Bank führen, desto mehr kann sie nach ihren Regeln verleihen.',
        'Die Idee ist nicht neu. Nachhaltige Banken gibt es in Deutschland seit Jahrzehnten, viele als Genossenschaft oder mit kirchlichem Hintergrund. Neu ist, dass sich mehr Menschen dafür interessieren und auch Großbanken mit grünen Produkten werben.',
        'Im Alltag merkst du kaum einen Unterschied. Du bekommst eine Karte, Onlinebanking, eine App und Überweisungen wie bei anderen Banken auch. Der Unterschied liegt darin, was die Bank im Hintergrund mit dem Geld macht.')))
    secs.append(('Woran du eine nachhaltige Bank erkennst', _p(
        _ul('<b>Kreditvergabe:</b> Entscheidend ist, wofür die Bank Kredite vergibt. Eine nachhaltige Bank finanziert gezielt Bereiche wie erneuerbare Energien, ökologische Landwirtschaft, bezahlbares Wohnen, Bildung, Gesundheit und Soziales. Frag nach, welcher Anteil der Kredite in solche Bereiche fließt.',
            '<b>Ausschlusskriterien:</b> Klare Ausschlüsse sind der Kern. Typisch sind Waffen und Rüstung, Kohle, Öl und Gas, Atomkraft, Gentechnik in der Landwirtschaft, Kinderarbeit und Spekulation mit Nahrungsmitteln. Wichtig ist, ob die Kriterien für die ganze Bank gelten oder nur für einzelne grüne Produkte.',
            '<b>Transparenz:</b> Veröffentlicht die Bank, wem sie Kredite gibt? Gibt es einen Nachhaltigkeitsbericht mit Zahlen statt Werbetexten?',
            '<b>Eigene Anlagen:</b> Auch das Geld, das die Bank selbst anlegt, etwa in Anleihen, sollte denselben Kriterien folgen.',
            '<b>Geschäftsmodell:</b> Keine Spekulation auf eigene Rechnung, keine Boni für riskante Geschäfte, oft eine genossenschaftliche Struktur, in der Kundinnen und Kunden mitbestimmen.',
        '<b>Beratung ohne Verkaufsdruck:</b> Eine Bank, die es ernst meint, verdient nicht vor allem an Provisionen für Fonds und Versicherungen. Frag, wie die Beraterinnen und Berater bezahlt werden.'),
        'Vorsicht vor Greenwashing. Ein „grünes Konto“ einer Großbank, bei dem für jede Kartenzahlung ein Baum gepflanzt wird, ändert nichts daran, wie die Bank sonst Kredite vergibt. Der Baum ist nett, der Hebel ist die Kreditvergabe.',
        'Ein guter Test ist die Frage nach dem Anteil. Eine Bank, die sagt, sie finanziere auch erneuerbare Energien, kann trotzdem viel Geld in Öl und Gas stecken. Eine nachhaltige Bank sagt dir, wie viel Prozent ihrer Kredite in welche Bereiche gehen.')))
    if d:
        secs.append(('Die Konten nachhaltiger Banken in der Liste', _p(d['s'])
                     + _tbl(['Konto', 'Nachhaltigkeit laut Bank', 'Kontoführung', 'Kosten im Jahr (Standardfall)'], d['rows'])
                     + _p('Was in der zweiten Spalte steht, beschreibt die Bank selbst. Ob dir ihre Kriterien reichen, prüfst du am besten in ihrem Nachhaltigkeitsbericht.')))
    secs.append(('Wie eine nachhaltige Bank mit deinem Geld arbeitet', _p(
        'Eine Bank hält nur einen kleinen Teil der Einlagen als Reserve. Der Rest steckt in Krediten und Anlagen. Bei einer großen Universalbank sind das Kredite an Unternehmen aller Branchen, Wertpapiere und Handelsgeschäfte. Bei einer nachhaltigen Bank fließt der größte Teil in Kredite an Unternehmen und Projekte, die zu ihren Kriterien passen.',
        'Ein Beispiel: Ein Solarpark braucht eine Finanzierung, eine Kita einen Umbau, ein Biohof eine neue Halle, ein Wohnprojekt bezahlbare Mietwohnungen. Die nachhaltige Bank prüft diese Kredite wie jede Bank darauf, ob sie zurückgezahlt werden. Zusätzlich prüft sie, was sie bewirken. Was nicht passt, lehnt sie ab, auch wenn es Gewinn verspricht.',
        'Weil diese Banken überwiegend klassisches Kreditgeschäft betreiben, sind ihre Berichte oft leichter zu lesen als die Bilanz einer Großbank. Du kannst also tatsächlich nachvollziehen, was mit deinem Geld passiert. Genau das ist der Unterschied zu einem Konto, bei dem nur die Werbung grün ist.',
        'Du kannst das selbst nachprüfen. Viele nachhaltige Banken schlüsseln ihre Kredite nach Branchen auf, manche nennen sogar die Kreditnehmer. Schau dir die Liste an und frag dich, ob du das mitfinanzieren willst.')))
    secs.append(('Fair Finance Guide und andere Prüfsteine', _p(
        'Einen staatlichen Nachweis für nachhaltige Banken gibt es in Deutschland nicht. Wer sich ein eigenes Urteil bilden will, findet aber unabhängige Hilfen.',
        _ul('<b>Fair Finance Guide Deutschland:</b> Ein unabhängiges Projekt bewertet die Richtlinien von Banken in Deutschland, etwa zu Klima, Menschenrechten, Waffen, Arbeitsrechten und Steuern. Du siehst dort, welche Regeln eine Bank sich selbst gibt und wie streng sie im Vergleich sind.',
            '<b>Global Alliance for Banking on Values:</b> ein weltweites Netzwerk von Banken, die sich auf werteorientiertes Wirtschaften verpflichten. Mitglieder müssen gemeinsame Grundsätze erfüllen.',
            '<b>Berichte der Bank:</b> Nachhaltigkeitsbericht, Kreditliste, Ausschlusskriterien. Je konkreter, desto besser.',
            '<b>Verbraucherzentralen:</b> Sie informieren über nachhaltige Banken und Geldanlage und ordnen Siegel und Werbeversprechen ein.'),
        'Ein Hinweis zu EU-Regeln: Die Offenlegungsverordnung und die EU-Taxonomie betreffen vor allem Fonds und andere Anlageprodukte. Für ein Girokonto gibt es keine verbindliche Einstufung als nachhaltig. Das Wort darf also jede Bank verwenden, umso wichtiger sind die Prüfsteine oben.',
        'Siegel für Banken als Ganzes gibt es kaum. Bekannte Siegel wie das FNG-Siegel beziehen sich auf Fonds. Wenn eine Bank mit einem Siegel wirbt, prüfe, wofür genau es vergeben wurde.',
        'Achte auch darauf, was eine Bank unter nachhaltig versteht. Manche Kirchenbanken legen den Schwerpunkt auf soziale und ethische Kriterien, andere Banken stärker auf Klima und Umwelt. Keines davon ist falsch, aber es sollte zu deinen eigenen Prioritäten passen.',
        'Der Fair Finance Guide bewertet nur eine Auswahl von Banken, darunter viele große. Nicht jede kleine Spezialbank taucht dort auf. Dann helfen ihre eigenen Berichte und die Mitgliedschaft in Netzwerken weiter.')))
    vt = ''
    if d and d['mn'] is not None and d['ma'] is not None:
        vt = f'In unseren Daten kosten die Standardkonten in dieser Liste im Standardfall im Mittel (Median) {c["eur"](d["mn"])} € im Jahr, über alle Standardkonten in unserem Vergleich sind es {c["eur"](d["ma"])} €.'
    secs.append(('Was ein Konto bei einer nachhaltigen Bank kostet', _p(
        vt,
        'Nachhaltige Banken sind selten die billigsten. Sie verzichten bewusst auf manche lukrativen Geschäfte, und viele beraten persönlich. Manche verlangen zusätzlich einen Mitgliedsbeitrag oder erwarten, dass du Genossenschaftsanteile zeichnest. Anteile sind kein Preis, sondern eine Beteiligung, die du bei Kündigung zurückbekommst. Im Fall einer Insolvenz können sie aber verloren gehen.',
        'Vergleiche immer den Jahrespreis im Standardfall, nicht nur die Monatsgebühr. Bei manchen Konten kommen Girocard, Kreditkarte und beleghafte Überweisungen dazu, bei anderen ist das meiste enthalten.',
        'Ein Rechenweg, der hilft: Teile den Aufpreis durch dein durchschnittliches Guthaben. Liegen im Schnitt 3.000 € auf dem Konto und kostet das nachhaltige Konto 60 € mehr im Jahr, zahlst du 2 % dafür, dass dieses Geld nach deinen Werten arbeitet.',
        f'Rechne den Aufpreis ehrlich: Kostet das nachhaltige Konto 60 € mehr im Jahr als ein Gratiskonto, sind das 5 € im Monat. Ob dir das die Gewissheit über dein Geld wert ist, entscheidest du. Junge Leute zahlen bei vielen Banken weniger, siehe {c["liste"]("studenten", "Girokonten für Studierende")}.')))
    secs.append(('Nachhaltig über das Girokonto hinaus', _p(
        'Das Girokonto ist ein Anfang. Mehr Wirkung hat oft das Geld, das länger liegt:',
        _ul('<b>Tagesgeld und Festgeld:</b> Bei einer nachhaltigen Bank steht dieses Geld länger zur Verfügung und kann in langfristige Kredite fließen.',
            '<b>Fonds und ETFs:</b> Achte auf strenge Ausschlüsse statt nur auf ein „ESG“ im Namen. Ein Fonds nach Artikel 9 der Offenlegungsverordnung verfolgt ein nachhaltiges Anlageziel, einer nach Artikel 8 bewirbt lediglich ökologische oder soziale Merkmale.',
            '<b>Altersvorsorge:</b> Frag bei betrieblicher Altersvorsorge und privaten Rentenverträgen nach den Anlagekriterien.',
            '<b>Versicherungen:</b> Auch Versicherer legen Beiträge an. Einige veröffentlichen eigene Ausschlusslisten.'),
        'Nachhaltigkeit ersetzt aber keine Prüfung von Kosten und Risiko. Ein teurer Fonds mit grünem Etikett ist kein gutes Geschäft, und ein Konto, das du dir nicht leisten willst, wechselst du nach drei Monaten wieder.',
        'Ein Beispiel: Wer 10.000 € Notreserve auf einem Tagesgeld bei einer nachhaltigen Bank parkt, gibt der Bank über Jahre Geld für Kredite. Das ist mehr Hebel als ein Girokonto, das am Monatsende fast leer ist.',
        'Und auch Strom- und Gasvertrag, Versicherungen und Altersvorsorge sind Hebel, oft sogar größere als das Konto.')))
    secs.append(('Fünf Fragen an deine Bank', _p(
        'Ob eine Bank zu dir passt, findest du am schnellsten mit ein paar direkten Fragen heraus. Eine gute nachhaltige Bank beantwortet sie ohne Ausflüchte:',
        _ol('Welche Branchen schließt ihr aus, für Kredite und für eure eigenen Anlagen?',
            'Wo kann ich nachlesen, wem ihr Kredite gebt?',
            'Gelten eure Regeln für die ganze Bank oder nur für bestimmte Produkte?',
            'Wer prüft, ob ihr euch daran haltet?',
            'Wie ist mein Geld abgesichert?'),
        f'Zur letzten Frage: Nachhaltige Banken in Deutschland sind gesetzlich genauso abgesichert wie alle anderen, bis 100.000 € pro Person. Genossenschaftsbanken gehören zusätzlich der Institutssicherung ihres Verbands an. Mehr im Ratgeber {c["rg"]("einlagensicherung", "Einlagensicherung")}.',
        f'Wer das Girokonto nicht wechseln will, kann zumindest das Ersparte zu einer nachhaltigen Bank bringen. Dort wirkt das Geld oft stärker, weil es länger liegt. Und wenn du wechselst, hilft dir die Kontowechselhilfe, siehe {c["rg"]("girokonto-wechseln", "Girokonto wechseln")}.')))
    secs.append(('Quellen', _quellen(c, [
        ('https://www.fairfinanceguide.de/', 'Fair Finance Guide Deutschland'),
        ('https://www.gabv.org/', 'Global Alliance for Banking on Values'),
        ('https://eur-lex.europa.eu/eli/reg/2019/2088/oj', 'EU-Offenlegungsverordnung 2019/2088'),
        ('https://www.verbraucherzentrale.de/', 'Verbraucherzentralen: nachhaltige Geldanlage'),
        ('https://www.gesetze-im-internet.de/zkg/', 'Zahlungskontengesetz (ZKG): Kontowechselhilfe'),
        ('https://www.bafin.de/', 'BaFin: Nachhaltige Finanzwirtschaft'),
    ], d['X'] if d else [])))
    if d:
        oq = (f'Bei {len(d["online"])} der {len(d["X"])} Konten in dieser Liste kannst du das Konto laut Bank online eröffnen. ' if d['online'] else 'Bei den Konten in dieser Liste läuft die Eröffnung laut Bank über die Filiale. ') + 'Die Identität bestätigst du dann per Video oder Postident.'
        dq = (f'Ja. Bei den Konten in dieser Liste nennen die Banken Dispozinsen zwischen {c["pct"](min(d["sz"]))} und {c["pct"](max(d["sz"]))}. ' if len(d['sz']) > 1 else 'Das hängt von der Bank ab. ') + 'Wie überall prüft die Bank vorher deine Bonität.'
        kq = (f'Bei {len(d["kk"])} der {len(d["X"])} Konten in dieser Liste bietet die Bank eine Kreditkarte an' + (f', inklusive ist sie bei {len(d["kki"])}.' if d['kki'] else ', gegen Aufpreis.')) if d['kk'] else 'Bei den Konten in dieser Liste ist laut unseren Daten keine Kreditkarte dabei. Frag bei der Bank nach, ob es eine gegen Aufpreis gibt.'
    else:
        oq = 'Bei vielen ja. Die Identität bestätigst du dann per Video oder Postident. Manche Banken setzen weiter auf persönliche Beratung in wenigen Filialen.'
        dq = 'In der Regel ja, wie bei anderen Banken nach einer Bonitätsprüfung.'
        kq = 'Das hängt von der Bank ab. Oft gibt es eine Kreditkarte gegen Jahresgebühr.'
    faq = [
        ('Sind Sparkassen und Volksbanken nachhaltige Banken?', 'Sie sind regional verankert und vergeben viele Kredite vor Ort. Das macht sie aber nicht automatisch nachhaltig im Sinne fester Ausschlusskriterien. Welche Regeln gelten, unterscheidet sich von Institut zu Institut. Frag nach dem Nachhaltigkeitsbericht.'),
        ('Kann ich ein Konto bei einer nachhaltigen Bank online eröffnen?', oq),
        ('Bekomme ich bei einer nachhaltigen Bank einen Dispo?', dq),
        ('Gibt es bei nachhaltigen Banken eine Kreditkarte?', kq),
        ('Wie finde ich heraus, was meine jetzige Bank finanziert?', 'Schau in den Nachhaltigkeitsbericht und die Ausschlusskriterien deiner Bank und vergleich sie im Fair Finance Guide. Auch Umweltorganisationen veröffentlichen regelmäßig Berichte darüber, welche Banken fossile Energie finanzieren.'),
    ]
    lede = 'Bei nachhaltigen Banken zählt nicht nur der Preis, sondern auch, was die Bank mit deinem Geld macht. Hier findest du Girokonten bei Banken mit klaren sozialen und ökologischen Regeln und erfährst, woran du echte Nachhaltigkeit erkennst.'
    return dict(lede=lede, secs=secs, faq=faq)


def _nachhaltig_at(c):
    d = _nh_daten(c)
    secs = []
    secs.append(('Warum die Bank zählt, nicht nur das Konto', _p(
        'Wenn du am Monatsende 1.500 € am Girokonto hast, arbeitet die Bank mit diesem Geld. Sie vergibt daraus Kredite für Häuser, Betriebe, Gemeinden und Energieprojekte und legt einen Teil in Wertpapieren an. Was davon finanziert wird, bestimmt die Bank. Bei einer nachhaltigen Bank hast du die Sicherheit, dass dabei klare Grenzen gelten.',
        'In Österreich lief das Thema lange über Sparprodukte und Fonds: grüne Sparbücher, ethische Fonds, das Umweltzeichen für Finanzprodukte. Beim Girokonto zählt dagegen die Bank als Ganzes, denn dein Kontoguthaben fließt in ihre gesamte Bilanz.',
        'Gerade in einem Land mit vielen regionalen Banken liegt der Gedanke nahe, dass das Geld ohnehin in der Gegend bleibt. Das stimmt teilweise. Regional heißt aber nicht automatisch nachhaltig: Auch eine Regionalbank kann Kredite für Projekte vergeben, die nicht zu deinen Werten passen.',
        'Ein Konto bei einer nachhaltigen Bank ist kein Verzicht. Du bekommst Bankomatkarte, Onlinebanking und Überweisungen wie überall. Der Unterschied liegt im Hintergrund, bei der Frage, wohin das Geld weiterwandert.',
        'Und noch etwas spricht dafür: Wer sich damit beschäftigt, was seine Bank finanziert, schaut meist auch genauer auf die eigenen Finanzen. Das allein ist schon ein Gewinn.',
        'Die Frage betrifft auch Menschen mit wenig Erspartem. Auch das Gehalt, das ein paar Tage am Konto liegt, gehört zu den Einlagen, mit denen die Bank arbeitet.')))
    secs.append(('Fünf Merkmale nachhaltiger Banken', _p(
        _ul('<b>Positivliste:</b> Die Bank sagt klar, wofür sie Kredite vergibt, etwa erneuerbare Energie, thermische Sanierung, Bio-Landwirtschaft, leistbares Wohnen, soziale Einrichtungen und Bildung.',
            '<b>Ausschlüsse für die ganze Bank:</b> keine Kredite und Veranlagungen bei Rüstung, fossiler Energie, Atomkraft, Glücksspiel oder Firmen mit Menschenrechtsverletzungen. Gilt das nur für einen Fonds, ist es kein Merkmal der Bank.',
            '<b>Offenlegung:</b> ein Nachhaltigkeits- oder Gemeinwohlbericht mit konkreten Zahlen, idealerweise eine Liste der finanzierten Projekte. Manche Banken erstellen eine Gemeinwohl-Bilanz nach den Regeln der Gemeinwohl-Ökonomie.',
            '<b>Unabhängige Prüfung:</b> externe Zertifizierungen oder die Mitgliedschaft in Netzwerken wie der Global Alliance for Banking on Values.',
            '<b>Fokus auf die Realwirtschaft:</b> Kredite an Menschen und Betriebe statt Handel auf eigene Rechnung, oft mit Schwerpunkt in der Region.'),
        'Achte darauf, ob eine Bank mit einzelnen grünen Produkten wirbt oder ob die Regeln für ihr gesamtes Geschäft gelten. Ein grüner Fonds im Angebot macht eine Bank nicht nachhaltig, wenn sie nebenbei Ölkonzerne finanziert.',
        'Eine einfache Faustregel: Je konkreter die Bank wird, desto ernster meint sie es. „Wir übernehmen Verantwortung“ ist ein Werbesatz. „Wir finanzieren keine Unternehmen, die mehr als 5 % ihres Umsatzes mit Kohle machen“ ist ein Kriterium.',
        'Oft übersehen wird der Umgang mit Mitarbeitenden und Kundschaft. Faire Gehälter, keine Verkaufsprovisionen und transparente Preise gehören für viele nachhaltige Banken genauso dazu wie der Klimaschutz.',
        'Hilfreich ist auch der Blick auf die Eigentümer. Gehört die Bank einer Genossenschaft, einer Stiftung oder einem großen Konzern? Das sagt nicht alles, erklärt aber, wessen Interessen am Ende zählen.')))
    if d:
        secs.append(('Was die Banken in der Liste bieten', _p(d['s'])
                     + _tbl(['Konto', 'Nachhaltigkeit laut Bank', 'Kontoführungsentgelt', 'Kosten im Jahr (Standardfall)'], d['rows'])
                     + _p('Die zweite Spalte gibt wieder, wie die Bank sich selbst beschreibt. Ihre genauen Kriterien stehen im Nachhaltigkeitsbericht.')))
    secs.append(('Was mit deinem Geld passiert: ein Beispiel', _p(
        'Stell dir vor, 2.000 Menschen haben im Schnitt 2.500 € auf ihren Konten bei einer nachhaltigen Bank. Das sind 5 Mio. €. Einen Teil hält die Bank als Reserve, mit dem Rest finanziert sie zum Beispiel Photovoltaik auf einem Gemeindedach, die thermische Sanierung eines Wohnhauses, einen Bio-Bauernhof und einen Betrieb für Menschen mit Behinderung.',
        'Jeder dieser Kredite wird geprüft wie bei jeder Bank: Kann der Kreditnehmer zurückzahlen? Dazu kommt die zweite Prüfung: Passt das Projekt zu den Kriterien? Ein Kredit für ein Chalet-Dorf auf der grünen Wiese oder für einen Ölhändler fällt hier durch, auch wenn er sicher wäre.',
        'Bei einer konventionellen Bank landet dasselbe Geld in einem großen Topf, aus dem alle Kredite und Veranlagungen bezahlt werden. Du erfährst nicht, was davon finanziert wird. Darin liegt der eigentliche Unterschied, nicht in der Farbe der Bankomatkarte.',
        'An der Sicherheit deines Guthabens ändert das nichts. Es ist gesetzlich gesichert, egal ob die Bank Photovoltaik oder Bürotürme finanziert. Das Geschäftsmodell ist meist schlicht: Einlagen annehmen und nach klaren Regeln als Kredit weitergeben.',
        'Aus vielen kleinen Kontoständen werden so reale Projekte. Das ist keine Spende und kein Verzicht, sondern ganz normales Bankgeschäft mit einem anderen Kompass.')))
    secs.append(('Gütesiegel und Orientierung in Österreich', _p(
        'Das Österreichische Umweltzeichen gibt es nach der Richtlinie UZ 49 auch für nachhaltige Finanzprodukte. Vergeben wird es vom zuständigen Bundesministerium, geprüft werden unter anderem Ausschlusskriterien und Transparenz. Ein Siegel gilt aber immer für das konkrete Produkt. Für die ganze Bank sagt es wenig.',
        'Ein Blick auf die Website lohnt. Seriöse Banken stellen ihre Kriterien, Berichte und Mitgliedschaften frei zugänglich online. Wer erst auf Nachfrage etwas zeigt, hat vielleicht nicht viel zu zeigen.',
        'In Deutschland bewertet der Fair Finance Guide die Richtlinien großer Banken. Für Bankengruppen, die in beiden Ländern tätig sind, kann ein Blick dorthin aufschlussreich sein.',
        'Für Versicherungen, Pensionskassen und Vorsorgekassen gibt es eigene Nachhaltigkeitsberichte und teils Zertifizierungen. Ein Blick dorthin lohnt, weil dort oft viel mehr Geld liegt als am Girokonto.',
        'Ein Siegel ist ein Hinweis, kein Beweis. Lies im Zweifel nach, welche Kriterien dahinterstehen und wer sie prüft.',
        'Weitere Orientierung geben die Nachhaltigkeitsberichte der Banken, Berichte von Umweltorganisationen über die Finanzierung fossiler Energie und Informationen von Arbeiterkammer und Verein für Konsumenteninformation.',
        'Seit 2021 müssen Finanzprodukte nach der EU-Offenlegungsverordnung angeben, ob sie ökologische oder soziale Merkmale bewerben. Das betrifft Fonds und Versicherungsprodukte, nicht das Girokonto. Ein „grünes Konto“ ist also kein geschützter Begriff.',
        'Und die FMA? Sie beaufsichtigt Banken auf Stabilität und die Einhaltung der Gesetze, nicht darauf, ob eine Bank nachhaltig ist. Sie hat aber einen Leitfaden veröffentlicht, wie Banken mit Nachhaltigkeitsrisiken umgehen sollen.')))
    vt = ''
    if d and d['mn'] is not None and d['ma'] is not None:
        vt = f'Ein Blick in unsere Daten: Die Standardkonten in dieser Liste kosten im Standardfall im Mittel (Median) {c["eur"](d["mn"])} € im Jahr, alle Standardkonten in unserem Vergleich {c["eur"](d["ma"])} €.'
    secs.append(('Kosten: was du für das gute Gewissen zahlst', _p(
        vt,
        'Nachhaltige Banken sind oft kleinere Institute oder Genossenschaften. Sie haben weniger Größenvorteile und verzichten bewusst auf manche Geschäfte. Das Kontoführungsentgelt liegt deshalb eher im Bereich klassischer Filialbanken als bei null.',
        'Rechne konkret: Ein Konto um 7 € pro Monat kostet 84 € im Jahr. Gegenüber einem Gratiskonto sind das 7 € im Monat dafür, dass dein Guthaben nach klaren Regeln verliehen wird. Bei Genossenschaftsbanken zeichnest du manchmal einen Geschäftsanteil, den du beim Austritt zurückbekommst.',
        'Als Mitglied einer Genossenschaftsbank hast du außerdem eine Stimme in der Generalversammlung, eine Form von Mitbestimmung, die es bei einer Aktienbank nicht gibt.',
        'Vergleiche immer den Jahrespreis, nicht nur das Kontoführungsentgelt pro Quartal. Rechne Bankomatkarte, Buchungszeilen und Kontoauszüge dazu. Erst dann siehst du, ob das nachhaltige Konto wirklich teurer ist als dein jetziges. Für Jugendliche, Studierende und Lehrlinge sind Konten bei vielen Banken günstiger oder gratis.',
        'Viele überschätzen den Aufpreis. Wer heute schon ein Konto mit Kontoführungsentgelt bei einer Filialbank hat, zahlt bei einer nachhaltigen Bank oft ähnlich viel. Der Vergleich mit dem eigenen Konto ist deshalb fairer als der mit einem Gratiskonto.',
        f'Wenn dir der Preis wichtiger ist, findest du günstige Alternativen unter {c["liste"]("kostenlos", "kostenlose Girokonten")}. Viele kombinieren beides: ein günstiges Konto für den Alltag und das Ersparte bei einer nachhaltigen Bank.')))
    secs.append(('Fragen, die du jeder Bank stellen kannst', _p(
        'Eine Bank, die es mit der Nachhaltigkeit ernst meint, beantwortet diese Fragen schnell und konkret. Ausweichende Antworten sind auch eine Antwort.',
        _ul('Gibt es eine öffentliche Ausschlussliste, und gilt sie für Kredite und für die eigenen Veranlagungen der Bank?',
            'Welcher Anteil der Kredite fließt in Bereiche wie Energie, Wohnen, Soziales oder Landwirtschaft?',
            'Wird ein Nachhaltigkeits- oder Gemeinwohlbericht veröffentlicht, und wer prüft ihn?',
            'Wie ist die Bank organisiert, und wer entscheidet über die Kriterien?',
            'Was kostet das Konto im Jahr, inklusive Bankomatkarte, Buchungen und Kontoauszügen?'),
        'Schreib die Antworten auf und vergleich zwei, drei Banken. Nach einer halben Stunde weißt du mehr als nach jeder Werbebroschüre.',
        'Vergleich die Antworten auch mit deinem eigenen Leben. Wer im Alltag auf Öffis und Bio achtet, will vielleicht nicht, dass das Ersparte in einen Flughafenausbau fließt. Wem soziale Themen wichtiger sind, legt den Schwerpunkt auf Wohnen, Pflege und Bildung.',
        'Gute Banken freuen sich über solche Fragen. Wenn dich niemand zurückruft, ist auch das eine Information.')))
    secs.append(('Halbe Lösungen, die trotzdem etwas bringen', _p(
        'Nicht jeder will sofort das Hauptkonto wechseln. Auch diese Schritte bewegen etwas:',
        _ul('<b>Spargeld verlagern:</b> Rücklagen liegen oft Jahre auf dem Konto. Da wirkt der Hebel stärker als beim Girokonto, das jeden Monat fast leer wird.',
            '<b>Bei der eigenen Bank nachfragen:</b> Gibt es eine Nachhaltigkeitsstrategie mit Ausschlüssen? Fragen von Kundinnen und Kunden zeigen Banken, dass das Thema zählt.',
            '<b>Wertpapiere prüfen:</b> Fonds mit Umweltzeichen oder strengen Ausschlüssen statt eines beliebigen Standardprodukts. Ein Hinweis auf „Artikel 8“ heißt nur, dass ein Fonds ökologische oder soziale Merkmale bewirbt, „Artikel 9“ steht für ein ausdrückliches Nachhaltigkeitsziel.',
            '<b>Vorsorge ansehen:</b> Bei der betrieblichen Vorsorgekasse und der Pensionskasse nachfragen, nach welchen Kriterien sie veranlagen.',
        '<b>Versicherungen:</b> Auch Versicherer veranlagen Prämien. Frag bei Lebens- und Pensionsversicherungen nach den Kriterien.',
        '<b>Im Betrieb mitreden:</b> Die Vorsorgekasse für die Abfertigung neu wählt der Arbeitgeber, in Betrieben mit Betriebsrat gemeinsam mit ihm. Sprich das Thema dort an.',
        '<b>Bürgerbeteiligungen:</b> Gemeinden und Energieversorger bieten Beteiligungen an Solar- oder Windkraftanlagen an. Das ist keine Bankeinlage und nicht durch die Einlagensicherung geschützt, aber ein direkter Weg, Geld in erneuerbare Energie zu stecken.'),
        f'Wenn du wechselst, übernimmt der Kontowechselservice nach dem VZKG die Umstellung für dich, siehe {c["rg"]("girokonto-wechseln", "Girokonto wechseln")}. Und keine Sorge um die Sicherheit: Auch bei nachhaltigen Banken ist dein Guthaben bis 100.000 € gesetzlich gesichert, mehr dazu unter {c["rg"]("einlagensicherung", "Einlagensicherung")}.',
        'Kleine Schritte zählen: Schon eine Notreserve von ein paar tausend Euro bei einer nachhaltigen Bank ist Geld, das jahrelang nach klaren Regeln arbeitet. Und wenn deine Bank eine eigene grüne Produktlinie hat, frag nach, ob die Kriterien auch für das Kreditgeschäft gelten.')))
    secs.append(('Quellen', _quellen(c, [
        ('https://www.umweltzeichen.at/', 'Österreichisches Umweltzeichen: nachhaltige Finanzprodukte (UZ 49)'),
        ('https://www.fma.gv.at/', 'Finanzmarktaufsicht (FMA): Nachhaltige Finanzen'),
        ('https://eur-lex.europa.eu/eli/reg/2019/2088/oj', 'EU-Offenlegungsverordnung 2019/2088'),
        ('https://www.gabv.org/', 'Global Alliance for Banking on Values'),
        ('https://www.econgood.org/', 'Gemeinwohl-Ökonomie'),
        ('https://www.arbeiterkammer.at/', 'Arbeiterkammer'),
        ('https://www.konsument.at/', 'Verein für Konsumenteninformation (VKI)'),
    ], d['X'] if d else [])))
    faq = [
        ('Sind Raiffeisenbanken oder Sparkassen in Österreich nachhaltige Banken?', 'Sie sind regional verankert und oft genossenschaftlich oder gemeinnützig organisiert. Das allein macht sie nicht nachhaltig im Sinne fester Ausschlusskriterien. Einzelne Institute haben eigene Schwerpunkte. Frag nach dem Nachhaltigkeitsbericht und den Ausschlüssen.'),
        ('Ist ein grünes Sparprodukt dasselbe wie eine nachhaltige Bank?', 'Nein. Bei einem grünen Sparprodukt verspricht die Bank, genau dieses Geld für bestimmte Zwecke zu verwenden. Das Girokonto und der Rest der Bank bleiben davon unberührt.'),
        ('Kann ich von Österreich aus ein Konto bei einer nachhaltigen Bank in Deutschland eröffnen?', f'Manche deutschen Banken nehmen Kundschaft aus Österreich an, viele nicht. Wenn es klappt, bekommst du eine deutsche IBAN, es gilt die deutsche Einlagensicherung, und Zinsen erklärst du selbst in der Beilage E 1kv. Was das sonst bedeutet, steht in der Liste {c["liste"]("neobanken", "Neobanken")}.'),
        ('Woran erkenne ich Greenwashing bei Banken?', 'Viele Bilder von Wäldern, aber keine Zahlen. Nachhaltigkeit nur bei einzelnen Produkten. Keine veröffentlichte Ausschlussliste. Vage Ziele für ferne Jahre ohne Zwischenschritte. Wenn die Bank auf konkrete Fragen ausweicht, ist das auch eine Antwort.'),
        ('Zahlen nachhaltige Banken weniger Zinsen aufs Ersparte?', 'Nicht unbedingt. Manche bieten marktübliche Zinsen, manche etwas weniger. Vergleich die Konditionen wie bei jeder anderen Bank.'),
    ]
    lede = 'Nachhaltige Banken verleihen dein Geld nur nach festen sozialen und ökologischen Regeln. Hier erfährst du, woran du solche Banken in Österreich erkennst, was ein Konto dort kostet und welche Konten es gibt.'
    return dict(lede=lede, secs=secs, faq=faq)


def texte(land, ctx):
    c = ctx
    if land == 'de':
        return {'unterkonten': _unterkonten_de(c), 'ohne-schufa': _ohne_schufa(c), 'direktbanken': _direktbanken_de(c),
                'neobanken': _neobanken_de(c), 'nachhaltige-banken': _nachhaltig_de(c)}
    if land == 'at':
        return {'unterkonten': _unterkonten_at(c), 'ohne-ksv': _ohne_ksv(c), 'direktbanken': _direktbanken_at(c),
                'neobanken': _neobanken_at(c), 'nachhaltige-banken': _nachhaltig_at(c)}
    return {}
