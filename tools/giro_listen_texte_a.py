# Erklärtexte für die Girokonto-Bestenlisten kostenlos, ohne-geldeingang, mit-kreditkarte und praemie (DE und AT).
# Aufruf aus girokonto.texte(land, ctx). Alle Zahlen über Konten kommen aus ctx, nie fest im Text.
# Rechtliches: BGB §§ 504a, 675g, 675h; ZKG §§ 5, 10, 20, 31 ff.; EinSiG § 8; BGH XI ZR 26/20 (27.04.2021); SEPA-Verordnung (EU) 260/2012 Art. 9;
# AT: VZKG, ZaDiG 2018, ESAEG (Einlagensicherung AUSTRIA), Arbeiterkammer. Abgerufen am 29.10.2026.
import html,re
E=lambda s: html.escape(str(s)) if s is not None else ''

# ---------- Quellen ----------
Q_DE=dict(
    bgb675g=('https://www.gesetze-im-internet.de/bgb/__675g.html','§ 675g BGB: Änderung des Zahlungsdiensterahmenvertrags'),
    bgb675h=('https://www.gesetze-im-internet.de/bgb/__675h.html','§ 675h BGB: Kündigung des Zahlungsdiensterahmenvertrags'),
    bgb504a=('https://www.gesetze-im-internet.de/bgb/__504a.html','§ 504a BGB: Beratungspflicht bei dauerhafter Überziehung'),
    zkg=('https://www.gesetze-im-internet.de/zkg/','Zahlungskontengesetz (ZKG)'),
    zkg20=('https://www.gesetze-im-internet.de/zkg/__20.html','§ 20 ZKG: Kontowechselhilfe'),
    bgh=('https://www.bundesgerichtshof.de/SharedDocs/Pressemitteilungen/DE/2021/2021088.html','BGH, Urteil vom 27.04.2021, XI ZR 26/20: Zustimmung zu Entgeltänderungen'),
    einsig=('https://www.gesetze-im-internet.de/einsig/__8.html','§ 8 Einlagensicherungsgesetz: 100.000 € je Person und Bank'),
    sepa=('https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32012R0260','SEPA-Verordnung (EU) Nr. 260/2012, Art. 9'),
    bafin=('https://www.bafin.de/DE/verbraucherinnen-verbraucher/themen-finanzprodukte/konten-zahlungen/konten/basiskonto/basiskonto_node.html','BaFin: Basiskonto'),
    schufa=('https://www.schufa.de/','SCHUFA Holding AG'),
)
Q_AT=dict(
    ak_bank=('https://bankenrechner.arbeiterkammer.at/','Bankenrechner der Arbeiterkammer'),
    ak_wechsel=('https://wien.arbeiterkammer.at/kontowechsel','Arbeiterkammer: Kontowechsel'),
    ak_basis=('https://www.arbeiterkammer.at/beratung/konsument/Geld/Konto/Recht_auf_ein_Girokonto.html','Arbeiterkammer: Recht auf ein Girokonto'),
    ris=('https://www.ris.bka.gv.at/','Rechtsinformationssystem des Bundes (VZKG, ZaDiG 2018, ESAEG)'),
    fma=('https://www.fma.gv.at/','Finanzmarktaufsicht (FMA)'),
    es=('https://www.einlagensicherung.at/','Einlagensicherung AUSTRIA'),
    sepa=('https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32012R0260','SEPA-Verordnung (EU) Nr. 260/2012, Art. 9'),
    ksv=('https://www.ksv.at/','KSV1870'),
    bmf=('https://www.bmf.gv.at/','Bundesministerium für Finanzen'),
)

# ---------- Bausteine ----------
def ext(q): return f'<a href="{E(q[0])}" target="_blank" rel="noopener">{E(q[1])} ↗</a>'
def prose(*xs): return '<div class="prose">'+''.join(xs)+'</div>'
def p(s): return f'<p>{s}</p>'
def ul(xs): return '<ul>'+''.join(f'<li>{x}</li>' for x in xs if x)+'</ul>'
def ol(xs): return '<ol>'+''.join(f'<li>{x}</li>' for x in xs if x)+'</ol>'
def tbl(head,rows):
    if not rows: return ''
    h=''.join(f'<th>{c}</th>' for c in head)
    b=''.join('<tr>'+''.join(f'<td>{c}</td>' for c in r)+'</tr>' for r in rows)
    return f'<div class="tbl wide"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'
def und(xs):
    xs=[x for x in xs if x]
    if not xs: return ''
    return xs[0] if len(xs)==1 else ', '.join(xs[:-1])+' und '+xs[-1]
def zahl(n,gross=False):
    w={0:'kein',1:'ein',2:'zwei',3:'drei',4:'vier',5:'fünf',6:'sechs',7:'sieben',8:'acht',9:'neun',10:'zehn',11:'elf',12:'zwölf'}.get(n,str(n))
    return w[0].upper()+w[1:] if gross else w
def konten(n,gross=False): return f'{zahl(n,gross)} Konto' if n==1 else f'{zahl(n,gross)} Konten'
def quellen_banken(xs,limit=30):
    seen=set(); out=[]
    for k in xs:
        u=k.get('quelle')
        if not u or u in seen: continue
        seen.add(u); out.append(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(k["bank"])}: {E(k["name"])} ↗</a>')
        if len(out)>=limit: break
    return out

def tot(k): return k['score']['kosten']['total']
def dk(k): return (k.get('debitkarte') or {})
def bar(k): return (k.get('bargeld') or {})
def girocard_preis(k):
    t=dk(k).get('text') or ''
    for seg in re.split(r'[;.]\s',t):
        if re.search(r'giro ?card|Girokarte',seg,re.I) and re.search(r'\d+(,\d+)? ?€',seg) and not re.search(r'kostenlos|inklusive',seg,re.I):
            return seg.strip()
    return None
def physisch_kostet(k):
    t=dk(k).get('text') or ''
    return bool(re.search(r'(physisch|Versand|Liefergebühr|Classic \d+ ?€ einmalig|Karte \d+ ?€ einmalig)',t,re.I))
def nur_digital(k): return bool(re.search(r'nur 1 digitale|nur eine digitale|keine physische',dk(k).get('text') or '',re.I))
def profil():
    try:
        import girokonto as G
        return G.PROFIL['standard']
    except Exception:
        return None
def standardfall(ctx):
    pr=profil()
    if not pr: return 'im Standardfall unseres Vergleichs'
    return f'im Standardfall unseres Vergleichs ({ctx["eur"](pr["ein"])} € Geldeingang im Monat, {pr["alter"]} Jahre, {pr["abh"]} Abhebungen im Monat)'
def aktion_typen(k):
    t=k.get('aktion') or ''; s=set()
    if re.search(r'Prämie|Bonus|Cash',t) and k.get('aktion_eur'): s.add('geld')
    if re.search(r'Kontoführung[^;]{0,80}(gratis|kostenlos|kostenfrei)|(gratis|kostenlos|kostenfrei)e? Kontoführung|Monate kostenlos ohne',t,re.I): s.add('zeit')
    if re.search(r'metal card|Kartengebühr[^;]*übernommen|Kreditkarte[^;]{0,60}(1\. Jahr|im 1\. Jahr)[^;]{0,10}gratis',t,re.I): s.add('karte')
    if re.search(r'zins',t,re.I): s.add('zins')
    if re.search(r'gutschein',t,re.I): s.add('gutschein')
    if re.search(r'\d+ Tage[^;]*gratis',t): s.add('probe')
    return s
def aktion_bed(k):
    t=k.get('aktion') or ''; s=set()
    if re.search(r'Geldeingang|Gehalt|Eingang',t): s.add('eingang')
    if re.search(r'Kontowechsel',t): s.add('wechsel')
    if re.search(r'Werbe|E-Mail',t): s.add('werbung')
    if re.search(r'Transaktion|Einzug',t): s.add('trans')
    if re.search(r'mind\. \d+ Monate|Konto mind',t): s.add('lauf')
    if re.search(r'Neuk|Neueröffnung|erstem Girokonto|Neu',t): s.add('neu')
    if re.search(r'Legitimation',t): s.add('legi')
    if re.search(r'\d{1,2}\.\d{1,2}\.(\d{4})?',t): s.add('frist')
    return s


# =====================================================================
# KOSTENLOS
# =====================================================================
def kostenlos_de(c):
    eur,pct,L,LI,RG=c['eur'],c['pct'],c['link'],c['liste'],c['rg']
    X=c['lists'].get('kostenlos') or []
    pur=[k for k in X if k['kf_jahr']==0]
    bed=sorted([k for k in X if k['kf_jahr']>0 and k.get('gratis')],key=lambda k:(k['gratis'].get('eingang_min') or 0))
    ein=[k['gratis']['eingang_min'] for k in bed if k['gratis'].get('eingang_min') is not None]
    alt=sorted({k['gratis']['alter_unter'] for k in bed if k['gratis'].get('alter_unter')})
    gc=[k for k in X if girocard_preis(k)]
    mind50=[k for k in X if re.search(r'ab 50 €',bar(k).get('text') or '')]
    limit=[k for k in X if bar(k).get('frei_monat') is not None]
    fw0=[k for k in X if k.get('fremdwaehrung_prozent')==0]
    fws=[k['fremdwaehrung_prozent'] for k in X if k.get('fremdwaehrung_prozent')]
    zs=[k['sollzins'] for k in X if k.get('sollzins')]
    beleg=[k for k in X if re.search(r'beleghaft|Schalter|postalisch|Brief',k.get('einzelposten') or '',re.I)]
    einz=[k for k in X if re.search(r'einzahlung',k.get('einzelposten') or '',re.I)]
    teuer=sorted([k for k in X if tot(k)>0],key=lambda k:-tot(k))
    filial=[k for k in X if k.get('eroeffnung') in ('filiale','beides')]
    eigen=[k for k in bed if re.search(r'eigene|Überträge|Umbuchungen',k['gratis'].get('eingang_art') or '',re.I)]
    undef=[k for k in bed if re.search(r'nicht näher definiert',k['gratis'].get('eingang_art') or '',re.I)]
    gehalt=[k for k in bed if re.search(r'Gehalt',k['gratis'].get('eingang_art') or '') and not re.search(r'jeder',k['gratis'].get('eingang_art') or '')]
    extra=[k for k in bed if k['gratis'].get('sonst') and re.search(r'immer nötig|Teilnahme|Vorteilsprogramm',k['gratis'].get('sonst') or '')]
    S=[]
    # 1
    S.append(('Was „kostenlos“ beim Girokonto genau bedeutet',prose(
        p('Wenn eine Bank ihr Konto „kostenlos“ nennt, meint sie fast immer nur eines: die monatliche Kontoführungsgebühr. Alles andere steht in der Entgeltinformation und im Preis- und Leistungsverzeichnis. Dort findest du die Preise für die Karte, für Abhebungen, für Überweisungen auf Papier, für den Dispo und für Zahlungen in fremder Währung. Ein Konto ohne Grundgebühr kann dich also trotzdem Geld kosten, wenn es nicht zu deinem Alltag passt.'),
        p(f'In dieser Liste stehen {konten(len(X))}, bei denen die Kontoführung nichts kostet. '
          +(f'{zahl(len(pur),True)} davon sind ohne jede Bedingung gratis. ' if pur else '')
          +(f'Bei {konten(len(bed))} hängt die Gratis-Kontoführung an einer Bedingung, meist an einem monatlichen Geldeingang' if bed else '')
          +(f' zwischen {eur(min(ein))} und {eur(max(ein))} €' if ein else '')
          +(f' oder, je nach Bank, an einem Alter unter {" oder ".join(str(a) for a in alt)} Jahren' if alt else '')+('.' if bed else '')),
        p(f'Banken müssen dir vor dem Abschluss eine Entgeltinformation geben, in der die wichtigsten Preise einheitlich aufgelistet sind (§ 5 ZKG). Einmal im Jahr bekommst du außerdem eine Entgeltaufstellung, in der steht, was du tatsächlich bezahlt hast (§ 10 ZKG). Genau diese zwei Dokumente lohnen einen Blick, bevor du ein Konto „kostenlos“ nennst.'))))
    # 2
    rows=[(L(k),E(c['kurzbed'](k)),E(c['kfT'](k)),E(k['gratis'].get('eingang_art') or 'keine Angabe')) for k in bed]
    S.append(('Bedingungslos gratis oder gratis mit Geldeingang',
        prose(p(f'Ein bedingungslos kostenloses Konto kostet dich keine Grundgebühr, egal ob im Monat 3.000 € oder gar nichts eingeht. Diese Konten findest du gesammelt in der Liste {LI("ohne-geldeingang","Gratis ohne Geldeingang")}. Die zweite Gruppe ist nur gratis, solange du eine Bedingung erfüllst. Fällt sie weg, verlangt die Bank den normalen Preis, oft schon im Folgemonat.'))
        +tbl(['Konto','Gratis, wenn','Sonst','Was als Eingang zählt'],rows)
        +prose(p('Bei den Konten mit Bedingung lohnt sich die Frage: Was passiert, wenn mein Gehalt einmal ausbleibt? Typische Fälle sind Elternzeit mit Elterngeld unter der Grenze, ein Jobwechsel mit einer Lücke, ein Sabbatical oder der Wechsel in die Selbstständigkeit mit unregelmäßigen Einnahmen. Mit Altersgrenze ist das Konto bis zu einem Geburtstag gratis, danach greift die Eingangsregel.'
          +(f' Bei {und([L(k) for k in extra])} reicht der Geldeingang allein nicht, dazu kommen weitere Pflichten, die beim Konto stehen.' if extra else '')))))
    # 3
    S.append(('Was als Geldeingang zählt und was nicht',prose(
        p('Hier unterscheiden sich die Banken stärker, als es die Werbung vermuten lässt. Grob gibt es drei Varianten:'),
        ul(['<b>Jeder Eingang.</b> Gehalt, Rente, Elterngeld, Kindergeld, aber auch eine Überweisung von Freunden zählen. Ausgenommen sind meist Wertpapierverkäufe, Zinsen, Stornos und Rücklastschriften.',
            '<b>Nur Überweisungen von außen.</b> Bareinzahlungen und Umbuchungen zwischen deinen eigenen Konten bei derselben Bank oder Bankgruppe zählen nicht.',
            '<b>Nur Gehalt.</b> Die Bank erwartet einen Eingang, der wie ein Gehalt aussieht. Rente oder Arbeitslosengeld kann darunterfallen, muss aber nicht. Frag im Zweifel vorher nach.']),
        p((f'Ausdrücklich ausgeschlossen sind Überträge von eigenen Konten bei {und([L(k) for k in eigen])}. ' if eigen else '')
          +(f'Bei {und([L(k) for k in undef])} sagt die Entgeltinformation nicht genau, was zählt. ' if undef else '')
          +(f'Nur Gehalt im engeren Sinn nennen {und([L(k) for k in gehalt])}. ' if gehalt else '')
          +'Viele Menschen erfüllen die Bedingung mit einem Dauerauftrag von einem anderen eigenen Konto. Ob das klappt, hängt allein von den Bedingungen der Bank ab. Wo sie solche Überträge nicht ausschließen, ist es in der Regel erlaubt, eine Garantie dafür gibt es aber nicht.'),
        p('Achte auch auf den Zeitpunkt. Die meisten Banken prüfen pro Kalendermonat. Kommt dein Gehalt am 31. und wird erst am 1. gebucht, kann der Eingang im falschen Monat landen. Manche Banken rechnen dann den Preis für genau diesen einen Monat ab.'))))
    # 4
    S.append(('Diese Kosten fallen trotz kostenloser Kontoführung an',prose(
        p('Die Kontoführung ist nur ein Posten. Diese Punkte entscheiden darüber, ob ein Gratis-Konto am Jahresende wirklich nichts gekostet hat:'),
        ul([f'<b>Karte.</b> Eine Debitkarte ist bei fast allen Konten dabei. Wer zusätzlich eine girocard will, zahlt bei {konten(len(gc))} in dieser Liste extra, etwa bei {und([L(k) for k in gc[:3]])}. Bei manchen Neobanken ist nur die virtuelle Karte gratis, die Plastikkarte kostet einmalig Versand.' if gc else '<b>Karte.</b> Prüfe, ob die Debitkarte und eine eventuelle girocard im Preis enthalten sind.',
            f'<b>Abheben.</b> {konten(len(limit),True) if limit else "Einige Konten"} in der Liste haben eine feste Zahl an Gratis-Abhebungen pro Monat, danach kostet jede einzelne. '+(f'Bei {konten(len(mind50))} ist Abheben mit der Debitkarte erst ab 50 € kostenlos, darunter wird ein Entgelt fällig. ' if mind50 else '')+'Am fremden Automaten kann außerdem der Betreiber ein eigenes Entgelt verlangen. Mehr dazu im Ratgeber '+RG('bargeld-abheben','Bargeld abheben')+'.',
            f'<b>Einzahlen.</b> Direktbanken haben keine Schalter. Bargeld einzahlen geht oft nur über Partner wie Supermärkte oder Automaten anderer Banken, und das kostet bei {konten(len(einz))} in der Liste laut Preisverzeichnis Geld.' if einz else '<b>Einzahlen.</b> Ohne Schalter ist Bargeld einzahlen oft nur über Partner möglich und kostet dann.',
            f'<b>Überweisungen.</b> Online ist eine Überweisung praktisch immer gratis. Auf Papier, per Telefon oder am Schalter kostet sie bei {konten(len(beleg))} in der Liste extra. Eilüberweisungen sind fast überall kostenpflichtig.' if beleg else '<b>Überweisungen.</b> Online gratis, auf Papier oft nicht.',
            (f'<b>Zahlen im Ausland.</b> Außerhalb des Euroraums verlangen viele Banken ein Auslandseinsatzentgelt auf jede Kartenzahlung, in dieser Liste bis zu {pct(max(fws))}. ' if fws else '<b>Zahlen im Ausland.</b> ')+(f'{konten(len(fw0),True)} verlangen dafür nichts. ' if fw0 else '')+'Details im Ratgeber '+RG('fremdwaehrung','Fremdwährung')+'.',
            (f'<b>Dispo.</b> Rutscht dein Konto ins Minus, zahlst du Zinsen, in dieser Liste zwischen {pct(min(zs))} und {pct(max(zs))} im Jahr. ' if zs else '<b>Dispo.</b> Ein Minus kostet Zinsen. ')+'Eine gesetzliche Obergrenze gibt es nicht. Mehr im Ratgeber '+RG('dispo','Dispo')+'.',
            '<b>Kleinkram.</b> Ersatzkarte nach Verlust, Rücklastschrift mangels Deckung, Kontoauszug per Post: Das sind selten große Beträge, aber sie stehen in keinem Werbebanner.']))))
    # 5
    pr=profil()
    rows=[(L(k),E(c['kfT'](k)),f'{eur(bar(k)["frei_monat"])} pro Monat' if bar(k).get('frei_monat') is not None else 'keine feste Grenze',('0 %' if k.get('fremdwaehrung_prozent')==0 else (pct(k['fremdwaehrung_prozent']) if k.get('fremdwaehrung_prozent') else 'keine Angabe')),f'{eur(tot(k))} €') for k in X]
    S.append(('Rechenbeispiel: Was die Konten im Jahr kosten',
        prose(p(f'Wir rechnen jedes Konto {standardfall(c)}. Dann zählt nicht nur die Kontoführung, sondern auch eine kostenpflichtige Karte und Abhebungen über dem Gratis-Kontingent.'))
        +tbl(['Konto','Kontoführung ohne Bedingung','Gratis-Abhebungen','Auslandseinsatz','Kosten im Jahr'],rows)
        +prose(p((f'{konten(len(teuer),True)} kosten in dieser Rechnung trotz kostenloser Kontoführung Geld. Am meisten sind es beim {L(teuer[0])} mit {eur(tot(teuer[0]))} € im Jahr, vor allem wegen der Abhebungen oder der Karte. ' if teuer else 'In dieser Rechnung kostet keines der Konten etwas. ')
          +'Hebst du seltener ab oder zahlst du fast alles mit Karte, sieht es anders aus. Deine eigenen Zahlen trägst du im '+f'<a class="lnk" href="{c["G"]}">Girokonto-Vergleich</a>'+' ein, dann rechnet die Seite für dich.'))))
    # 6
    S.append(('Wenn die Bank aus „kostenlos“ später „kostenpflichtig“ macht',prose(
        p('Ein Gratis-Konto ist kein Versprechen für immer. In den letzten Jahren haben viele Banken Gebühren eingeführt oder die Grenze für den Geldeingang angehoben. Das dürfen sie, aber nicht einfach so.'),
        ul(['Die Bank muss dir eine Änderung spätestens zwei Monate vor dem geplanten Termin mitteilen (§ 675g BGB).',
            'Bis dahin kannst du kostenlos und fristlos kündigen.',
            'Seit dem Urteil des Bundesgerichtshofs vom 27.04.2021 (XI ZR 26/20) reicht Schweigen nicht mehr als Zustimmung zu neuen Entgelten. Die Bank braucht deine ausdrückliche Zustimmung, etwa per Klick im Online-Banking. Stimmst du nicht zu, darf sie dir das Konto mit einer Frist von mindestens zwei Monaten kündigen.']),
        p(f'Wenn die Mitteilung kommt, lies sie ganz. Oft ändert sich nicht die Grundgebühr, sondern die Bedingung: höherer Mindesteingang, girocard nicht mehr inklusive, weniger Gratis-Abhebungen. Passt es nicht mehr, hilft dir die gesetzliche Kontowechselhilfe nach § 20 ZKG. Die neue Bank holt dabei die Daueraufträge und Lastschriften von der alten. Wie das abläuft, steht im Ratgeber {RG("girokonto-wechseln","Konto wechseln")}.'))))
    # 7
    S.append(('So findest du das passende Gratis-Konto',prose(
        p('Geh die Fragen der Reihe nach durch. Am Ende bleiben meist zwei oder drei Konten übrig.'),
        ol(['<b>Wie viel geht jeden Monat ein, und ist das sicher?</b> Wenn ja, kommen auch die Konten mit Bedingung infrage. Wenn nein, schau zuerst auf die bedingungslosen Konten.',
            '<b>Wie alt bist du?</b> '+(f'Je nach Bank ist das Konto unter {" oder ".join(str(a) for a in alt)} Jahren auch ohne Eingang gratis. ' if alt else '')+'Für Studierende gibt es außerdem die Liste '+LI('studenten','Girokonten für Studierende')+'.',
            '<b>Wie oft brauchst du Bargeld?</b> Wer jede Woche abhebt, achtet auf die Zahl der Gratis-Abhebungen und den Mindestbetrag.',
            '<b>Brauchst du eine girocard?</b> Manche Händler, Behörden und Parkautomaten nehmen nur sie. Dann prüfe, ob sie im Preis enthalten ist.',
            '<b>Reist du außerhalb des Euroraums?</b> Dann zählt das Auslandseinsatzentgelt.',
            '<b>Willst du eine Filiale?</b> '+(f'In dieser Liste kannst du {konten(len(filial))} auch in einer Filiale eröffnen: {und([L(k) for k in filial])}.' if filial else 'Die Konten in dieser Liste eröffnest du online.')]),
        p(f'Mit einer Kreditkarte dazu wird es noch günstiger, wenn du viel reist. Die passenden Konten stehen in der Liste {LI("mit-kreditkarte","Girokonten mit Kreditkarte")}.'))))
    # Quellen
    S.append(('Quellen',prose(ul([ext(Q_DE['zkg'])+': Entgeltinformation (§ 5) und Entgeltaufstellung (§ 10)',ext(Q_DE['zkg20']),ext(Q_DE['bgb675g']),ext(Q_DE['bgh']),ext(Q_DE['bgb504a'])]
        +quellen_banken(X)+['Preise, Bedingungen und Bargeld-Regeln: Entgeltinformationen und Preisverzeichnisse der Banken, verlinkt bei jedem Konto im Vergleich. Stand: '+E(c['stand'])+'.']))))
    F=[('Zählt eine Überweisung von meinem eigenen Konto als Geldeingang?',
        'Das legt jede Bank selbst fest. '+(f'Bei {und([L(k) for k in eigen])} zählen Überträge von eigenen Konten ausdrücklich nicht. ' if eigen else '')+'Wo die Bedingungen nichts ausschließen, reicht oft ein Dauerauftrag von einem Konto bei einer anderen Bank. Sicher bist du erst, wenn es in den Bedingungen steht oder der Kundenservice es bestätigt.'),
       ('Was passiert, wenn mein Gehalt einen Monat lang ausbleibt?',
        'Bei den meisten Konten mit Bedingung zahlst du dann für diesen Monat die normale Kontoführungsgebühr. Das Konto wird nicht gekündigt. Sobald wieder genug eingeht, ist es wieder gratis. Liegst du unter der Altersgrenze der Bank, spielt der Eingang keine Rolle.'),
       ('Darf meine Bank für ein kostenloses Konto plötzlich Gebühren verlangen?',
        'Ja, aber nur mit Vorlauf und mit deiner Zustimmung. Die Bank muss dich mindestens zwei Monate vorher informieren. Seit dem BGH-Urteil von 2021 braucht sie deine aktive Zustimmung. Lehnst du ab, kann sie das Konto kündigen. Du kannst bis zum Stichtag kostenlos kündigen und wechseln.'),
       ('Gibt es ein kostenloses Girokonto mit Filiale?',
        (f'Ja, in dieser Liste kannst du {konten(len(filial))} auch in der Filiale eröffnen: {und([L(k) for k in filial])}. ' if filial else '')+'Bei Filialbanken ist die Kontoführung aber fast immer an einen Geldeingang gebunden. Beratung am Schalter, Überweisungen auf Papier und Bargeld am Schalter kosten oft trotzdem extra.'),
       ('Gibt es eine Obergrenze für Dispozinsen?',
        'Nein. In Deutschland gibt es keine gesetzliche Obergrenze für Dispozinsen. Bist du sechs Monate am Stück im Schnitt mit mehr als 75 % deines Rahmens im Minus, muss dir die Bank aber eine Beratung zu günstigeren Alternativen anbieten (§ 504a BGB).')]
    return dict(lede='Hier findest du alle Girokonten für Erwachsene, bei denen die Kontoführung nichts kostet, sortiert nach unserer Bewertung. Darunter erklären wir, welche Kosten trotzdem anfallen können und was als Geldeingang zählt.',secs=S,faq=F)

def kostenlos_at(c):
    eur,pct,L,LI,RG=c['eur'],c['pct'],c['link'],c['liste'],c['rg']
    X=c['lists'].get('kostenlos') or []
    pur=[k for k in X if k['kf_jahr']==0]
    bed=sorted([k for k in X if k['kf_jahr']>0 and k.get('gratis')],key=lambda k:(k['gratis'].get('eingang_min') or 0))
    ein=[k['gratis']['eingang_min'] for k in bed if k['gratis'].get('eingang_min') is not None]
    alt=sorted({k['gratis']['alter_unter'] for k in bed if k['gratis'].get('alter_unter')})
    nurgehalt=[k for k in bed if (k['gratis'].get('eingang_art') or '')=='Gehalt/Pension']
    jeder=[k for k in bed if 'jeder' in (k['gratis'].get('eingang_art') or '')]
    quartal=[k for k in X if k.get('kf_periode')=='Quartal']
    nachfrist=[k for k in bed if re.search(r'3 Monate|> ?3 Monate',k['gratis'].get('sonst') or '')]
    jedermonat=[k for k in bed if re.search(r'JEDEM Monat|jedem Monat des',(k['gratis'].get('sonst') or '')+(k['gratis'].get('text') or ''))]
    fremd=[k for k in X if k.get('iban') and k['iban']!=c['code']]
    fws=[k['fremdwaehrung_prozent'] for k in X if k.get('fremdwaehrung_prozent')]
    fw0=[k for k in X if k.get('fremdwaehrung_prozent')==0]
    zs=[k['sollzins'] for k in X if k.get('sollzins')]
    ohnedispo=[k for k in X if not k.get('sollzins')]
    limit=[k for k in X if bar(k).get('frei_monat') is not None]
    trafik=[k for k in X if re.search(r'Trafik',(bar(k).get('text') or '')+(k.get('einzelposten') or ''))]
    schalter=[k for k in X if re.search(r'Schalter|originalschriftlich',(k.get('einzelposten') or '')+(bar(k).get('text') or ''))]
    teuer=sorted([k for k in X if tot(k)>0],key=lambda k:-tot(k))
    S=[]
    S.append(('Gratis heißt beim Girokonto: kein Kontoführungsentgelt',prose(
        p('Österreichische Banken verrechnen für ein Girokonto ein Kontoführungsentgelt, oft pro Quartal. Ein „Gratiskonto“ ist eines, bei dem dieses Entgelt wegfällt. Die übrigen Positionen der Preisliste bleiben: Bankomatkarte, Behebungen, Buchungen am Schalter, Überziehungszinsen, Zahlungen in fremder Währung.'),
        p(f'In dieser Liste sind {konten(len(X))} für Erwachsene, bei denen die Kontoführung nichts kostet. '
          +(f'{zahl(len(pur),True)} davon sind gratis, ohne dass du irgendetwas erfüllen musst. ' if pur else '')
          +(f'{zahl(len(bed),True)} werden gratis, sobald jeden Monat genug Geld eingeht' if bed else '')
          +(f', je nach Bank ab {eur(min(ein))} bis {eur(max(ein))} €' if ein else '')
          +(f', oder solange du je nach Bank jünger als {" oder ".join(str(a) for a in alt)} Jahre bist' if alt else '')+('.' if bed else '')
          +(f' Bei {konten(len(quartal))} wird das Entgelt pro Quartal abgerechnet, deshalb steht im Kontoauszug dann ein größerer Betrag auf einmal.' if quartal else '')),
        p('Was eine Bank wofür verlangt, muss sie dir vor Vertragsabschluss in einer standardisierten Entgeltinformation zeigen. Das schreibt das Verbraucherzahlungskontogesetz (VZKG) vor. Einmal im Jahr bekommst du außerdem eine Aufstellung aller Entgelte, die du bezahlt hast. Ein Vergleich aller Banken, auch der regionalen, steht im '+ext(Q_AT['ak_bank'])+'.'))))
    rows=[(L(k),E(c['kurzbed'](k)),E(c['kfT'](k)),E(k['gratis'].get('sonst') or '')) for k in bed]
    S.append(('Gratis mit Gehalts- oder Geldeingang: so funktioniert es',
        prose(p('Viele österreichische Banken machen das Konto gratis, wenn regelmäßig ein Gehalt oder eine Pension eingeht. Für sie ist das ein Zeichen, dass du das Konto als Hauptkonto nutzt. Deshalb heißen solche Konten oft „Gehaltskonto“ oder „Pensionskonto“. Die Regeln im Detail:'))
        +tbl(['Konto','Gratis, wenn','Sonst','Gut zu wissen'],rows)
        +prose(p((f'{und([L(k) for k in nurgehalt])} {"zählt" if len(nurgehalt)==1 else "zählen"} nur Gehalt, Lohn oder Pension. ' if nurgehalt else '')
          +(f'Bei {und([L(k) for k in jeder])} reicht jeder Eingang, also auch Familienbeihilfe oder eine Überweisung vom eigenen Sparkonto bei einer anderen Bank. ' if jeder else '')
          +(f'{und([L(k) for k in nachfrist])} {"gibt" if len(nachfrist)==1 else "geben"} dir eine Schonfrist: Erst wenn der Eingang länger als drei Monate fehlt, gelten die normalen Preise. ' if nachfrist else '')
          +(f'Bei {und([L(k) for k in jedermonat])} muss der Eingang in jedem Monat des Quartals da sein, sonst kostet das ganze Quartal. ' if jedermonat else '')),
          p('Rechne mit Lücken: Karenz, Bildungskarenz, Arbeitslosigkeit oder ein Jobwechsel können den Eingang unterbrechen. Ob Kinderbetreuungsgeld oder Arbeitslosengeld vom AMS als „Gehalt“ zählt, regeln die Banken unterschiedlich. Frag vorher nach, wenn du so eine Phase planst. Wer gar keine Bedingung will, findet die passenden Konten in der Liste '+LI('ohne-geldeingang','Gratis ohne Geldeingang')+'.'))))
    S.append(('Kosten, die auch beim Gratiskonto anfallen',prose(
        ul(['<b>Bankomatkarte.</b> Bei allen Konten in der Liste ist eine Debitkarte dabei. Bei den Neobanken ist oft nur die digitale Karte gratis, für die Plastikkarte zahlst du einmalig einen Betrag für Karte oder Versand. Für zusätzliche Karten, etwa für Zeichnungsberechtigte, verlangen manche Banken ein Jahresentgelt.',
            f'<b>Behebungen.</b> {konten(len(limit),True)} in der Liste haben eine feste Zahl an Gratis-Behebungen, danach kostet jede einzelne. ' if limit else '<b>Behebungen.</b> Prüfe, wie viele Behebungen gratis sind. '
            +'An Bankomaten unabhängiger Betreiber kann zusätzlich ein Entgelt anfallen, das vor der Behebung am Bildschirm angezeigt wird. Mehr im Ratgeber '+RG('bargeld-beheben','Bargeld beheben')+'.',
            '<b>Bargeld einzahlen.</b> Online-Banken haben keinen Schalter. '+(f'Bei {und([L(k) for k in trafik])} geht das in Trafiken, gegen Entgelt. ' if trafik else '')+(f'Aufträge auf Papier oder am Schalter kosten extra, etwa bei {und([L(k) for k in schalter[:3]])}.' if schalter else ''),
            '<b>Überweisungen.</b> Elektronisch sind sie bei Gratiskonten inklusive. Ein Auftrag auf Papier oder ein manuell angelegter Dauerauftrag kann extra kosten.',
            (f'<b>Fremdwährung.</b> Zahlst du außerhalb des Euroraums mit Karte, verlangen die meisten Banken einen Aufschlag, in dieser Liste bis zu {pct(max(fws))}. ' if fws else '<b>Fremdwährung.</b> ')+(f'{konten(len(fw0),True)} verzichten darauf. ' if fw0 else '')+'Mehr im Ratgeber '+RG('fremdwaehrung','Fremdwährung')+'.',
            (f'<b>Überziehung.</b> Wer ins Minus rutscht, zahlt Sollzinsen, in dieser Liste zwischen {pct(min(zs))} und {pct(max(zs))} im Jahr. ' if zs else '<b>Überziehung.</b> ')+(f'Bei {konten(len(ohnedispo))} nennt die Preisliste keinen Sollzins, dort gibt es meist keinen Überziehungsrahmen. Frag nach, wenn du einen brauchst. ' if ohnedispo else '')+'Mehr im Ratgeber '+RG('kontoueberziehung','Kontoüberziehung')+'.',
            '<b>Aktionen statt Dauerpreis.</b> „Im ersten Jahr gratis“ ist kein Gratiskonto. Nach der Aktion zahlst du den vollen Preis. Solche Konten stehen bei uns in der Liste '+LI('praemie','Girokonten mit Prämie')+', nicht hier.']))))
    rows=[(L(k),E(c['kfT'](k)),E(k.get('iban') or ''),('0 %' if k.get('fremdwaehrung_prozent')==0 else (pct(k['fremdwaehrung_prozent']) if k.get('fremdwaehrung_prozent') else 'keine Angabe')),f'{eur(tot(k))} €') for k in X]
    S.append(('Was die Gratiskonten im Jahr tatsächlich kosten',
        prose(p(f'Gerechnet {standardfall(c)}. Erfüllst du die Gratis-Bedingung nicht, kostet das Konto so viel wie in der Spalte „Kontoführung ohne Bedingung“.'))
        +tbl(['Konto','Kontoführung ohne Bedingung','IBAN','Fremdwährung','Kosten im Jahr'],rows)
        +prose(p((f'Trotz kostenloser Kontoführung kosten {konten(len(teuer))} in dieser Rechnung Geld, am meisten das {L(teuer[0])} mit {eur(tot(teuer[0]))} € im Jahr. Der Grund sind fast immer Behebungen über dem Gratis-Kontingent. ' if teuer else '')
          +(f'{konten(len(fremd),True)} haben keine österreichische IBAN. Das ist erlaubt: Laut SEPA-Verordnung darf kein Arbeitgeber und keine Firma eine IBAN aus einem anderen SEPA-Land ablehnen. ' if fremd else '')
          +f'Mit deinen eigenen Zahlen rechnest du im <a class="lnk" href="{c["G"]}">Girokonto-Vergleich</a>.'))))
    S.append(('Wenn die Bank die Entgelte ändert',prose(
        p('Ein Konto, das heute gratis ist, kann morgen etwas kosten. Die Bank muss dir eine Änderung aber mindestens zwei Monate vorher mitteilen, so verlangt es das Zahlungsdienstegesetz (ZaDiG 2018). Bis zum Inkrafttreten kannst du den Vertrag kostenlos kündigen. Manche Banken haben außerdem Klauseln, mit denen sie Entgelte an einen Index wie den Verbraucherpreisindex anpassen. Ob das bei deinem Konto so ist, steht im Kontovertrag.'),
        p('Gefällt dir eine Änderung nicht, musst du nicht alles selbst umstellen. Banken in Österreich müssen einen Kontowechsel-Service anbieten. Die neue Bank informiert dann Arbeitgeber und Lastschrift-Partner. Für Banken ohne österreichischen Sitz gilt dieser gesetzliche Service nicht immer. Mehr dazu im Ratgeber '+RG('girokonto-wechseln','Konto wechseln')+' und bei der '+ext(Q_AT['ak_wechsel'])+'.'))))
    S.append(('Checkliste vor der Eröffnung',prose(
        ol(['<b>Bedingung realistisch prüfen.</b> Geht jeden Monat sicher genug ein? Auch in der Karenz?',
            '<b>Bargeld-Gewohnheiten zählen.</b> Wie oft hebst du ab, und wo? In kleinen Orten gibt es oft nur Bankomaten der regionalen Banken.',
            '<b>IBAN prüfen.</b> Brauchst du eine österreichische IBAN, etwa weil ein Formular es (unrechtmäßig) verlangt, schränkt das die Auswahl ein.',
            '<b>Bankomatkarte und App.</b> Gibt es eine physische Karte? Funktionieren Apple Pay und Google Pay? Mehr im Ratgeber '+RG('apple-pay-google-pay','Apple Pay und Google Pay')+'.',
            '<b>Einlagensicherung.</b> Pro Person und Bank sind 100.000 € gesetzlich gesichert, bei österreichischen Banken über die Einlagensicherung AUSTRIA. Details im Ratgeber '+RG('einlagensicherung','Einlagensicherung')+'.',
            '<b>Kündigung beim alten Konto.</b> Erst wechseln, dann kündigen. Sonst stehen Lastschriften ohne Deckung im Raum.']))))
    pens=[k for k in bed if 'Pension' in (k['gratis'].get('eingang_art') or '')+k['name']]
    jung=[k for k in bed if k['gratis'].get('alter_unter')]
    unbegr=[k for k in X if re.search(r'unbegrenzt',bar(k).get('text') or '')]
    S.append(('Welches Gratiskonto zu welcher Lebenslage passt',prose(
        p('Das beste Gratiskonto ist das, dessen Bedingung du ohne Nachdenken jeden Monat erfüllst. Ein paar typische Fälle:'),
        ul([(f'<b>Pension.</b> Bei {und([L(k) for k in pens])} zählt die Pension ausdrücklich als Eingang. Wichtig ist, dass die Pensionsversicherung direkt auf dieses Konto überweist. ' if pens else '<b>Pension.</b> Achte darauf, dass die Pension als Eingang zählt. ')+'Wer gerne am Schalter Rat holt, zahlt bei einer Filialbank mehr, bekommt dafür aber persönliche Betreuung.',
            (f'<b>Erstes kleines Gehalt.</b> Den niedrigsten Mindesteingang verlangt das {L(bed[0])} mit {eur(bed[0]["gratis"]["eingang_min"])} € im Monat. ' if bed and bed[0]['gratis'].get('eingang_min') is not None else '<b>Erstes kleines Gehalt.</b> ')+'Für Lehrlinge und Teilzeitkräfte ist das oft der entscheidende Punkt.',
            (f'<b>Unter 30.</b> {und([L(k) for k in jung])} {"ist" if len(jung)==1 else "sind"} für junge Leute auch ohne Eingang gratis. Die genaue Altersgrenze steht in der Tabelle oben. ' if jung else '<b>Unter 30.</b> ')+'Wer noch studiert, schaut zusätzlich in die Liste '+LI('studenten','Girokonten für Studierende')+'.',
            (f'<b>Viel Bargeld.</b> Unbegrenzt gratis beheben kannst du laut Preisliste bei {und([L(k) for k in unbegr])}. ' if unbegr else '<b>Viel Bargeld.</b> ')+'Achte darauf, ob das nur im Euroraum oder nur an bestimmten Bankomaten gilt.',
            '<b>Paare.</b> Nicht jedes Gratiskonto gibt es als gemeinsames Konto. Mehr in der Liste '+LI('gemeinschaftskonto','Gemeinschaftskonten')+'.']))))
    S.append(('Quellen',prose(ul([ext(Q_AT['ak_bank']),ext(Q_AT['ak_wechsel']),ext(Q_AT['ris']),ext(Q_AT['es']),ext(Q_AT['sepa'])]
        +quellen_banken(X)+['Preise, Bedingungen und Bargeld-Regeln: Entgeltinformationen und Preisblätter der Banken, verlinkt bei jedem Konto im Vergleich. Stand: '+E(c['stand'])+'.']))))
    F=[('Zählt Kinderbetreuungsgeld oder Arbeitslosengeld als Gehaltseingang?',
        'Das regelt jede Bank selbst. Wo nur „Gehalt oder Pension“ steht, ist das nicht sicher.'+(f' Bei {und([L(k) for k in jeder])} zählt jeder Eingang, dort reicht es also, wenn der Betrag hoch genug ist.' if jeder else '')+' Frag am besten schriftlich nach, bevor die Karenz beginnt.'),
       ('Was passiert, wenn mein Gehalt einmal zu spät kommt?',
        'Die Bank prüft meist am Monatsende. Fehlt der Eingang in diesem Monat, verrechnet sie für diesen Zeitraum das normale Entgelt.'+(f' Großzügiger sind {und([L(k) for k in nachfrist])}: dort gelten die normalen Preise erst, wenn mehrere Monate nichts kommt.' if nachfrist else '')),
       ('Ist ein Gratiskonto mit deutscher oder litauischer IBAN ein Problem?',
        'Rechtlich nicht. Die SEPA-Verordnung der EU verbietet es Arbeitgebern, Vermietern und Firmen, eine IBAN aus einem anderen SEPA-Land abzulehnen. In der Praxis kann es bei einzelnen Formularen trotzdem hängen. Dann hilft ein Hinweis auf Artikel 9 der SEPA-Verordnung.'),
       ('Darf die Bank mein Gratiskonto kostenpflichtig machen?',
        'Ja, mit mindestens zwei Monaten Vorlauf. In dieser Zeit kannst du kostenlos kündigen. Bei Unklarheiten helfen die Arbeiterkammer und die Konsumentenschutz-Beratung.'),
       ('Gibt es Gratiskonten mit Filiale?',
        'Ohne Bedingung kaum. Filialbanken verlangen für normale Konten fast immer ein Kontoführungsentgelt, oft gibt es nur in Aktionen ein Gratisjahr. Gratis sind bei ihnen meist Konten für Studierende, Jugendliche und Kinder. Siehe die Listen '+LI('studenten','Studierende')+' und '+LI('kinder-jugendkonto','Kinder und Jugendliche')+'.')]
    return dict(lede='Alle Girokonten für Erwachsene in Österreich, bei denen kein Kontoführungsentgelt anfällt, ohne Bedingung oder mit Gehaltseingang. Dazu, welche Entgelte trotzdem kommen können.',secs=S,faq=F)


# =====================================================================
# OHNE GELDEINGANG
# =====================================================================
def ohne_de(c):
    eur,pct,L,LI,RG=c['eur'],c['pct'],c['link'],c['liste'],c['rg']
    X=c['lists'].get('ohne-geldeingang') or []
    phys=[k for k in X if physisch_kostet(k)]
    digi=[k for k in X if nur_digital(k)]
    lim=[k for k in X if bar(k).get('frei_monat') is not None]
    jede=[k for k in X if bar(k).get('frei_monat')==0]
    nodispo=[k for k in X if not k.get('sollzins')]
    dispo=[k for k in X if k.get('sollzins')]
    verw=[k for k in X if re.search(r'Verwahrentgelt',k.get('einzelposten') or '')]
    einz=[k for k in X if re.search(r'einzahlung',k.get('einzelposten') or '',re.I)]
    neo=[k for k in X if k.get('eroeffnung')=='online']
    gcp=[k for k in X if girocard_preis(k)]
    bon=[k for k in X if k.get('bonitaet')=='schufa']
    S=[]
    S.append(('Für wen ein Konto ohne Bedingung passt',prose(
        p('Ein Konto, das ganz ohne Mindesteingang gratis ist, nimmt dir eine Sorge ab: Du musst nie wieder nachrechnen, ob in diesem Monat genug eingegangen ist. Das ist vor allem in diesen Situationen praktisch:'),
        ul(['<b>Unregelmäßiges Einkommen.</b> Selbstständige, Freelancer und Saisonkräfte haben Monate mit viel und Monate mit wenig Geld.',
            '<b>Elternzeit, Sabbatical, Arbeitssuche.</b> Wenn das Gehalt für ein paar Monate wegfällt, kostet ein Konto mit Bedingung plötzlich Gebühren.',
            '<b>Zweitkonto.</b> Für Urlaub, Haushaltsgeld oder als Notfall-Reserve, falls bei der Hauptbank die Karte gesperrt ist.',
            '<b>Nach der Ausbildung.</b> Das Studentenkonto läuft aus, das erste Gehalt ist noch nicht da.',
            '<b>Rente mit kleinem Betrag.</b> Liegt die Rente unter der Grenze der Bank, hilft auch der regelmäßige Eingang nicht.']),
        p(f'In dieser Liste stehen {konten(len(X))}, deren Kontoführung ohne jede Bedingung nichts kostet. Konten, die nur mit Geldeingang oder bis zu einem Alter gratis sind, findest du in der Liste {LI("kostenlos","Kostenlose Girokonten")}.'))))
    rows=[(L(k),E(dk(k).get('text') or 'keine Angabe'),E(bar(k).get('text') or 'keine Angabe'),(pct(k['sollzins']) if k.get('sollzins') else 'kein Dispo')) for k in X]
    S.append(('Karte, Bargeld und Dispo im Überblick',
        prose(p('Die Kontoführung ist bei allen gleich: 0 €. Die Unterschiede liegen bei der Karte, beim Bargeld und beim Dispo.'))
        +tbl(['Konto','Karte','Bargeld','Dispo-Zins'],rows)))
    S.append(('Womit die Banken trotzdem Geld verdienen',prose(
        p('Kein Konto ist für die Bank umsonst. Wer keine Grundgebühr verlangt, verdient anders. Das zu wissen hilft, die Preisliste richtig zu lesen:'),
        ul(['<b>Kartenzahlungen.</b> Bei jeder Zahlung mit Debit- oder Kreditkarte bekommt die Bank einen kleinen Anteil vom Händler. Deshalb wollen Neobanken, dass du möglichst viel mit Karte zahlst.',
            '<b>Guthaben.</b> Dein Geld auf dem Konto kann die Bank anlegen. Bei hohen Guthaben verlangen manche Anbieter ein Verwahrentgelt'+(f', etwa {und([L(k) for k in verw])} laut Preisverzeichnis' if verw else '')+'.',
            '<b>Bezahlte Pakete.</b> Das Gratis-Konto ist der Einstieg. Mehr Abhebungen, Versicherungen oder eine Metallkarte gibt es im Abo.',
            '<b>Extras.</b> Ersatzkarte, Bargeld einzahlen, Abheben über dem Kontingent, Rücklastschriften.',
            '<b>Weitere Produkte.</b> Depot, Tagesgeld, Kredit. Die Bank hofft, dass du mehr nutzt als das Konto.']),
        p('Für dich heißt das: Ein Gratis-Konto ohne Bedingung ist dann wirklich gratis, wenn du die Extras nicht brauchst. Brauchst du sie oft, kann ein Konto mit Grundgebühr am Ende günstiger sein. Lies deshalb im Preisverzeichnis nicht nur die erste Zeile, sondern auch die Abschnitte zu Karten, Bargeld und Sonderleistungen.'))))
    S.append(('Darauf achtest du bei diesen Konten',prose(
        ul([(f'<b>Plastikkarte.</b> Bei {konten(len(phys))} kostet die physische Karte einmalig Geld oder Versand: {und([L(k) for k in phys])}. ' if phys else '<b>Plastikkarte.</b> Prüfe, ob die physische Karte gratis ist. ')+(f'{und([L(k) for k in digi])} {"gibt" if len(digi)==1 else "geben"} dir nur eine digitale Karte. Ohne Smartphone-Zahlung kommst du dann nicht weit.' if digi else ''),
            (f'<b>Bargeld.</b> {konten(len(lim),True)} begrenzen die Gratis-Abhebungen pro Monat. ' if lim else '<b>Bargeld.</b> ')+(f'Bei {und([L(k) for k in jede])} kostet jede einzelne Abhebung. ' if jede else '')+'Hebst du selten und dafür größere Beträge ab, spielt das kaum eine Rolle.',
            (f'<b>Bargeld einzahlen.</b> Bei {konten(len(einz))} kostet es laut Preisverzeichnis Geld, meist einen Prozentsatz vom Betrag. ' if einz else '<b>Bargeld einzahlen.</b> Prüfe, ob und wo es geht. ')+'Wer regelmäßig Bargeld einnimmt, etwa als Händler, ist bei einer Filialbank besser aufgehoben.',
            (f'<b>Dispo.</b> {konten(len(nodispo),True)} haben keinen Dispokredit. Eine Lastschrift ohne Deckung platzt dann einfach. ' if nodispo else '<b>Dispo.</b> ')+(f'Wo es einen gibt, liegt der Zins bei {pct(min(k["sollzins"] for k in dispo))} bis {pct(max(k["sollzins"] for k in dispo))} im Jahr.' if dispo else ''),
            (f'<b>girocard.</b> Bei {und([L(k) for k in gcp])} kostet sie extra. ' if gcp else '<b>girocard.</b> ')+'Neobanken bieten oft gar keine an. Wenn dein Bäcker oder dein Parkhaus nur girocard nimmt, ist das ein echter Nachteil.',
            '<b>Nur per App.</b> '+(f'{konten(len(neo),True)} in der Liste eröffnest du ausschließlich online. ' if neo else '')+'Telefonischer Service ist bei manchen Neobanken schwer zu erreichen, vieles läuft über den Chat.']))))
    S.append(('Kontoeröffnung Schritt für Schritt',prose(
        p('Die Eröffnung dauert bei den meisten Banken in dieser Liste zwischen zehn Minuten und einem Tag. So läuft sie ab:'),
        ol(['<b>Antrag ausfüllen.</b> Name, Anschrift, Geburtsdatum, Familienstand, Beruf. Dazu fragt die Bank nach deiner Steuer-Identifikationsnummer und ob du in einem anderen Land steuerpflichtig bist, etwa in den USA. Das ist Pflicht, keine Neugier.',
            '<b>Ausweis zeigen.</b> Banken müssen nach dem Geldwäschegesetz prüfen, wer du bist. Online geht das per Video-Ident (Videoanruf mit Ausweis vor der Kamera), per Online-Ausweisfunktion des Personalausweises oder mit Post-Ident in der Filiale der Deutschen Post.',
            f'<b>Bonitätsprüfung.</b> Viele Banken fragen bei der {E(c["bon"])} an. '+(f'Bei {und([L(k) for k in bon])} ist das laut unseren Daten der Fall. ' if bon else '')+'Ein Girokonto ohne Dispo bekommst du auch mit Einträgen oft, ein Konto mit Kreditrahmen eher nicht. Mehr in der Liste '+LI('ohne-schufa','Girokonten ohne Schufa-Abfrage')+'.',
            '<b>App einrichten.</b> Du koppelst dein Smartphone, legst eine PIN fest und bekommst die IBAN. Die digitale Karte ist sofort nutzbar, die Plastikkarte kommt in einigen Tagen per Post.',
            '<b>Erste Einzahlung.</b> Überweise einen kleinen Betrag von deinem bisherigen Konto. So prüfst du, dass alles klappt.',
            '<b>Umziehen oder nebenher nutzen.</b> Soll das neue Konto dein Hauptkonto werden, nutzt du die Kontowechselhilfe. Die neue Bank informiert dann Arbeitgeber und Vertragspartner. Wie das geht, steht im Ratgeber '+RG('girokonto-wechseln','Konto wechseln')+'.']))))
    S.append(('Wie viele Konten du haben darfst',prose(
        p('So viele du willst. In Deutschland gibt es keine Obergrenze für Girokonten. Zwei Ausnahmen gibt es:'),
        ul(['<b>P-Konto.</b> Ein Pfändungsschutzkonto darfst du nur einmal haben. Mehr im Ratgeber '+RG('p-konto','P-Konto')+'.',
            '<b>Basiskonto.</b> Einen Anspruch darauf hast du nur, wenn du noch kein nutzbares Zahlungskonto in Deutschland hast. Mehr im Ratgeber '+RG('basiskonto','Basiskonto')+'.']),
        p(f'Jedes neue Konto kann bei der {E(c["bon"])} gemeldet werden. Ein Girokonto ohne Dispo ist dort kein Kredit. Trotzdem gilt: Ein paar Konten mit klarem Zweck sind besser als zehn, die du nicht mehr überblickst. Ein gratis Zweitkonto ohne Bedingung ist dafür ideal, weil es dich nichts kostet, auch wenn du es monatelang kaum nutzt.'))))
    rows=[(L(k),E(k.get('einlagensicherung') or 'keine Angabe'),E(k.get('iban') or '')) for k in X]
    S.append(('Wo dein Guthaben gesichert ist',
        prose(p('Bei Konten ohne Gebühr landen oft Banken, die du noch nicht kennst. Deshalb lohnt der Blick auf die Einlagensicherung. In der EU sind Guthaben pro Person und Bank bis 100.000 € gesetzlich geschützt, in Deutschland nach § 8 Einlagensicherungsgesetz. Hat die Bank ihren Sitz in einem anderen EU-Land, springt die Sicherung dieses Landes ein, mit derselben Grenze. Eine deutsche IBAN sagt darüber nichts aus.'))
        +tbl(['Konto','Einlagensicherung laut Bank','IBAN'],rows)
        +prose(p('Liegt mehr als 100.000 € auf deinen Konten, verteil das Geld auf mehrere Banken. Mehr im Ratgeber '+RG('einlagensicherung','Einlagensicherung')+'.'))))
    hand=[k for k in X if re.search(r'viacash|CASH26|Handel|Barzahlen',bar(k).get('text') or '')]
    S.append(('Bargeld ohne Filiale besorgen',prose(
        p('Ohne eigene Automaten kommst du trotzdem gut an Bargeld. Diese Wege gibt es:'),
        ul(['<b>Am Automaten mit der Debitkarte.</b> Das geht an fast jedem Automaten mit Visa- oder Mastercard-Zeichen. Die Bank zählt die Abhebung auf dein Gratis-Kontingent an, der Automatenbetreiber kann zusätzlich ein Entgelt nehmen. Es wird vor der Auszahlung angezeigt, dann kannst du noch abbrechen.',
            (f'<b>An der Supermarktkasse.</b> Bei {und([L(k) for k in hand])} kannst du laut Preisverzeichnis auch im Handel Bargeld abheben, etwa über viacash oder CASH26. ' if hand else '<b>An der Supermarktkasse.</b> ')+'Viele Supermärkte zahlen dir beim Einkauf zusätzlich Bargeld aus, oft ab einem Mindesteinkauf. Ob deine Karte dafür funktioniert, hängt vom Händler ab.',
            '<b>Größere Beträge.</b> Brauchst du einmal mehr, etwa für einen Gebrauchtwagen, überweise lieber. Tageslimits der Karte liegen oft bei einigen hundert Euro und lassen sich in der App nur begrenzt erhöhen.']),
        p('Und falls du viel Bargeld einzahlen musst: Dafür sind Konten ohne Filiale schlicht nicht gebaut. Ein zweites Konto bei einer Filialbank kann dann sinnvoll sein.'))))
    S.append(('Quellen',prose(ul([ext(Q_DE['zkg']),ext(Q_DE['zkg20']),ext(Q_DE['bgb675h']),ext(Q_DE['bafin']),ext(Q_DE['einsig'])]
        +quellen_banken(X)+['Karten, Bargeld und Dispo: Entgeltinformationen und Preisverzeichnisse der Banken, verlinkt bei jedem Konto im Vergleich. Stand: '+E(c['stand'])+'.']))))
    F=[('Kann ich ein Girokonto ohne Einkommen eröffnen?',
        'Ja. Die Konten in dieser Liste verlangen keinen Geldeingang. Die Bank kann dich aber aus anderen Gründen ablehnen, etwa nach der Bonitätsprüfung. Dann bleibt dir das Basiskonto: Jede Bank, die Girokonten für Verbraucher anbietet, muss es dir eröffnen, auch ohne Einkommen.'),
       ('Kann die Bank mein Konto kündigen, wenn ich es kaum nutze?',
        'Ja. Banken dürfen ein Girokonto mit einer Frist von mindestens zwei Monaten ordentlich kündigen, wenn das im Vertrag so steht (§ 675h BGB). Bei Gratis-Konten ohne Bedingung passiert das bei reiner Nichtnutzung selten, ausgeschlossen ist es aber nicht.'),
       ('Bekomme ich bei einem Konto ohne Geldeingang einen Dispo?',
        (f'Bei {konten(len(dispo))} in dieser Liste ist ein Dispo grundsätzlich möglich. ' if dispo else '')+'Die Bank räumt ihn aber meist erst ein, wenn regelmäßig Geld eingeht und deine Bonität passt. '+(f'{konten(len(nodispo),True)} bieten gar keinen an.' if nodispo else '')),
       ('Was mache ich, wenn ein Händler meine Debitkarte nicht nimmt?',
        'Das kommt vor allem bei kleinen Geschäften vor, die nur die girocard akzeptieren. Dann hilft Bargeld oder eine girocard von einem anderen Konto. Wer viel in solchen Läden zahlt, wählt ein Konto mit girocard.')]
    return dict(lede='Diese Girokonten kosten keine Kontoführung, auch wenn kein Gehalt eingeht: kein Mindesteingang, keine Altersgrenze, keine Pflicht-Aktivität. Darunter: worauf es bei Karte, Bargeld und Dispo ankommt und wie die Eröffnung abläuft.',secs=S,faq=F)

def ohne_at(c):
    eur,pct,L,LI,RG=c['eur'],c['pct'],c['link'],c['liste'],c['rg']
    X=c['lists'].get('ohne-geldeingang') or []
    phys=[k for k in X if physisch_kostet(k)]
    digi=[k for k in X if nur_digital(k)]
    fremd=[k for k in X if k.get('iban') and k['iban']!=c['code']]
    heim=[k for k in X if k.get('iban')==c['code']]
    iban_namen={'DE':'Deutschland','LT':'Litauen','NL':'den Niederlanden','AT':'Österreich'}
    nodispo=[k for k in X if not k.get('sollzins')]
    dispo=[k for k in X if k.get('sollzins')]
    jede=[k for k in X if bar(k).get('frei_monat')==0]
    S=[]
    S.append(('Warum ein Konto ganz ohne Bedingung sinnvoll sein kann',prose(
        p('Die meisten österreichischen Gratiskonten setzen einen Gehalts- oder Pensionseingang voraus. Das passt, solange das Gehalt pünktlich kommt. Für viele Lebenslagen ist ein Konto ohne jede Bedingung aber entspannter:'),
        ul(['<b>Karenz und Bildungskarenz.</b> Kinderbetreuungsgeld zählt nicht bei jeder Bank als Gehalt.',
            '<b>Selbstständig oder neue Selbstständige.</b> Einnahmen kommen unregelmäßig, oft von vielen Kunden. Für das Geschäftliche lohnt ein Blick in den Ratgeber '+RG('konto-selbststaendige','Konto für Selbstständige')+'.',
            '<b>Zweitkonto.</b> Zum Sparen, für Reisen oder als Haushaltskonto mit dem Partner.',
            '<b>Studium vorbei.</b> Das Studentenkonto endet mit 26 oder 27, der erste Job beginnt erst später.',
            '<b>Kleine Pension.</b> Liegt die Pension unter der Mindestgrenze, hilft auch der regelmäßige Eingang nicht.']),
        p(f'In dieser Liste stehen {konten(len(X))}, die keine Bedingung haben. Konten, die nur mit Gehalt gratis sind, findest du in der Liste {LI("kostenlos","Kostenlose Girokonten")}.'),
        p('Ein Vorteil, der oft übersehen wird: Du musst dein Gehaltskonto nicht aufgeben, um ein solches Konto zu nutzen. Viele behalten ihr bestehendes Konto bei der Hausbank und eröffnen ein bedingungsloses Gratiskonto dazu, etwa für Online-Einkäufe, Abos oder das Urlaubsbudget. Wird die Karte dort einmal missbraucht, bleibt das Hauptkonto unberührt. Und wer später doch wechseln will, hat schon ein laufendes Konto, mit dem er Erfahrungen gesammelt hat.'))))
    rows=[(L(k),E(dk(k).get('text') or 'keine Angabe'),E(bar(k).get('text') or 'keine Angabe'),E(k.get('iban') or ''),(pct(k['sollzins']) if k.get('sollzins') else 'keiner')) for k in X]
    S.append(('Die Konten im Vergleich',
        prose(p('Kontoführung 0 €, aber Bankomatkarte, Behebungen, IBAN und Überziehungsrahmen sind verschieden geregelt.'))
        +tbl(['Konto','Karte','Bargeld','IBAN','Überziehungszins'],rows)))
    S.append(('Ausländische Banken: was das für dich heißt',prose(
        p((f'{konten(len(fremd),True)} in dieser Liste {"vergibt" if len(fremd)==1 else "vergeben"} keine österreichische IBAN, sondern eine aus '+und(sorted({iban_namen.get(k["iban"],k["iban"]) for k in fremd}))+'. ' if fremd else '')
          +(f'Eine österreichische IBAN bekommst du bei {und([L(k) for k in heim])}. ' if heim else '')
          +'Fast alle bedingungslos gratis Konten in Österreich kommen von Banken, die ihren Sitz in einem anderen EU-Land haben und hier ohne eigene Filialen arbeiten. Das hat ein paar Folgen:'),
        ul(['<b>IBAN.</b> Arbeitgeber, Vermieter, Versicherungen und Behörden müssen eine IBAN aus einem anderen SEPA-Land akzeptieren (Artikel 9 der SEPA-Verordnung). Weigert sich jemand, kannst du dich bei der Finanzmarktaufsicht beschweren.',
            '<b>Einlagensicherung.</b> Dein Guthaben ist bis 100.000 € geschützt, aber über die Einlagensicherung des Heimatlands der Bank, nicht über die Einlagensicherung AUSTRIA. Die Höhe ist in der EU einheitlich, im Ernstfall läuft die Auszahlung aber über eine ausländische Stelle.',
            '<b>KESt auf Zinsen.</b> Österreichische Banken ziehen die Kapitalertragsteuer automatisch ab. Banken ohne steuerliche Vertretung in Österreich tun das oft nicht. Dann musst du Zinsen selbst in der Steuererklärung angeben. Prüfe, was deine Bank dazu schreibt.',
            '<b>Kontowechsel-Service.</b> Der gesetzliche Service nach dem VZKG verpflichtet Banken in Österreich. Ausländische Anbieter machen ihn nicht immer mit, dann informierst du Arbeitgeber und Lastschrift-Partner selbst.',
            '<b>Beschwerden.</b> Zuständig ist meist die Aufsicht im Sitzland. Die Arbeiterkammer hilft dir trotzdem mit Beratung.']),
        p('Nichts davon ist ein Grund, die Finger von diesen Konten zu lassen. Die Banken stehen unter EU-Aufsicht und haben dieselben Regeln für Einlagensicherung und Zahlungsverkehr wie österreichische Banken. Du solltest die Unterschiede aber kennen, bevor du dein Gehalt dorthin umleitest. Steuerliche Fragen klärst du am einfachsten einmal mit dem Finanzamt oder in der Steuerberatung, bevor nennenswerte Zinsen anfallen.'))))
    S.append(('Bankomatkarte, Bargeld und Überziehen',prose(
        ul([(f'<b>Karte.</b> Bei {und([L(k) for k in phys])} ist nur die digitale Karte gratis, die Plastikkarte kostet einmalig. ' if phys else '<b>Karte.</b> ')+(f'{und([L(k) for k in digi])} {"bietet" if len(digi)==1 else "bieten"} gar keine Plastikkarte an. ' if digi else '')+'Mit einer digitalen Karte zahlst du per Smartphone, an manchen Bankomaten kannst du damit auch kontaktlos beheben.',
            '<b>Bargeld.</b> '+(f'Bei {und([L(k) for k in jede])} kostet jede Behebung. ' if jede else '')+'Prüfe in der Tabelle, ob es eine Grenze pro Monat, einen Mindestbetrag oder ein Entgelt pro Behebung gibt. Wer oft kleine Beträge behebt, zahlt sonst mehr als bei einem Gehaltskonto mit Kontoführungsentgelt.',
            '<b>Bargeld einzahlen.</b> Ohne Filiale ist das umständlich. Manche Anbieter arbeiten mit Partnern im Handel zusammen, oft gegen einen Prozentsatz. Wer regelmäßig Trinkgeld, Flohmarkt-Erlöse oder Bargeld von Kunden einzahlt, behält dafür besser ein Konto bei einer Bank mit Filiale oder Einzahlungsautomat.',
            (f'<b>Überziehen.</b> {konten(len(nodispo),True)} bieten keinen Überziehungsrahmen. ' if nodispo else '<b>Überziehen.</b> ')+(f'Bei {und([L(k) for k in dispo])} ist ein Rahmen möglich, mit {und([pct(k["sollzins"]) for k in dispo])} Sollzinsen. ' if dispo else '')+'Ohne Rahmen wird eine Lastschrift ohne Deckung abgelehnt, das kann beim Empfänger Mahnkosten auslösen.',
            '<b>Kartenlimits.</b> Für Zahlungen und Behebungen gibt es Tages- und Monatslimits. Bei Neobanken stellst du sie meist selbst in der App ein. Für größere Beträge, etwa eine Kaution, ist eine Überweisung oft der bessere Weg.',
            '<b>Zahlen in fremder Währung.</b> Die meisten Neobanken verrechnen beim Bezahlen in fremder Währung keinen eigenen Aufschlag. Am Wochenende oder bei exotischen Währungen gelten aber bei manchen Anbietern Zuschläge. Mehr im Ratgeber '+RG('fremdwaehrung','Fremdwährung')+'.']),
        p('Rechne für dich durch, wie oft du im Monat Bargeld brauchst und wo. Wer in einer Kleinstadt lebt und gern bar zahlt, ist mit einem Konto ohne Behebungsgrenze besser bedient als mit dem günstigsten Konto auf dem Papier.'))))
    S.append(('Eröffnung in fünf Schritten',prose(
        ol(['<b>App laden und Daten eingeben.</b> Name, Adresse, Geburtsdatum, Beruf und deine Steuer-Ansässigkeit. Wer in den USA steuerpflichtig ist, muss das angeben.',
            '<b>Identifizieren.</b> Banken müssen nach dem Finanzmarkt-Geldwäschegesetz prüfen, wer du bist. Bei Online-Banken geht das per Video-Ident mit Reisepass oder Personalausweis. Ein Führerschein reicht dafür meist nicht.',
            '<b>Prüfung abwarten.</b> Manche Banken holen eine Auskunft beim KSV1870 ein, vor allem wenn ein Überziehungsrahmen dazukommt. Mehr in der Liste '+LI('ohne-ksv','Girokonten ohne KSV-Abfrage')+'.',
            '<b>Karte aktivieren.</b> Die digitale Karte legst du in Apple Pay oder Google Pay ab. Die Plastikkarte, falls bestellt, kommt per Post.',
            '<b>Geld überweisen.</b> Eine erste Überweisung vom alten Konto zeigt, ob alles klappt. Soll das Konto dein Hauptkonto werden, gib die neue IBAN beim Arbeitgeber und bei Lastschrift-Partnern an.']),
        p('Halte vor dem Start einen gültigen Reisepass oder Personalausweis, dein Smartphone mit aktueller App-Version und eine gute Internetverbindung bereit. Die Video-Identifizierung scheitert am häufigsten an spiegelnden Ausweisen und schlechtem Licht. Plane zehn bis zwanzig Minuten ein. Bei manchen Anbietern bist du am selben Tag fertig, bei anderen dauert die Freigabe ein bis zwei Werktage.'))))
    S.append(('Mehrere Konten nebeneinander',prose(
        p('In Österreich darfst du so viele Girokonten haben, wie du möchtest. Ein Gratiskonto ohne Bedingung eignet sich deshalb gut als zweites Konto neben dem Gehaltskonto. Zwei Grenzen gibt es: Ein Pfändungsschutzkonto darfst du nur einmal führen ('+RG('pfaendungsschutzkonto','Ratgeber Pfändungsschutzkonto')+'), und das gesetzliche Basiskonto steht dir nur zu, wenn du noch kein Zahlungskonto in Österreich hast ('+RG('basiskonto','Ratgeber Basiskonto')+').'),
        p('Wer zwei Konten nutzt, sollte festlegen, welches wofür da ist. Ein bewährtes Muster: Gehalt und Fixkosten aufs Hauptkonto, ein fester Betrag per Dauerauftrag aufs Gratiskonto für Alltag und Reisen. So siehst du sofort, was im Monat noch übrig ist.'),
        p('Für Paare gibt es zwei Wege. Entweder jeder hat ein eigenes Gratiskonto und ihr überweist einen festen Anteil auf ein gemeinsames Konto für Miete und Einkauf. Oder ihr eröffnet ein echtes Gemeinschaftskonto. Nicht jede Neobank bietet das an, die Auswahl steht in der Liste '+LI('gemeinschaftskonto','Gemeinschaftskonten')+'. Manche Anbieter erlauben stattdessen geteilte Unterkonten, auf die beide zugreifen können. Mehr dazu in der Liste '+LI('unterkonten','Girokonten mit Unterkonten')+'.'))))
    rows=[(L(k),E(k.get('einlagensicherung') or 'keine Angabe'),E(iban_namen.get(k.get('iban'),k.get('iban') or ''))) for k in X]
    S.append(('Einlagensicherung der einzelnen Konten',
        tbl(['Konto','Einlagensicherung laut Bank','IBAN aus'],rows)
        +prose(p('Die gesetzliche Grenze von 100.000 € pro Person und Bank gilt in der ganzen EU. Bei österreichischen Banken zahlt im Ernstfall die Einlagensicherung AUSTRIA, bei ausländischen Banken die Stelle im Sitzland. Mehr im Ratgeber '+RG('einlagensicherung','Einlagensicherung')+'.'))))
    S.append(('Eine Neobank als Hauptkonto: geht das?',prose(
        p('Ja, viele nutzen eines dieser Konten als einziges Konto. Ein paar Dinge solltest du dann vorher klären:'),
        ul(['<b>Gehalt, Pension, Familienbeihilfe.</b> Alle Zahlungen kannst du auf eine ausländische IBAN überweisen lassen. Gib die neue IBAN rechtzeitig vor dem nächsten Zahltag bekannt.',
            '<b>Lastschriften.</b> Miete, Strom, Handy und Versicherungen buchen per SEPA-Lastschrift ab. Ohne Kontowechsel-Service musst du jedem Vertragspartner die neue IBAN selbst mitteilen.',
            '<b>Erreichbarkeit.</b> Support gibt es meist im Chat. Für dringende Fälle wie eine gesperrte Karte im Urlaub ist ein zweites Konto mit eigener Karte eine gute Rückversicherung.',
            '<b>Kontosperre.</b> Neobanken prüfen ungewöhnliche Zahlungen automatisch. Wird das Konto vorübergehend gesperrt, bis Fragen geklärt sind, kommst du in der Zeit nicht an dein Geld. Auch dagegen hilft ein zweites Konto.',
            '<b>Bargeldbedarf.</b> Wer oft bar zahlt, rechnet vorher nach, was die Behebungen im Monat kosten.']),
        p('Wer lieber eine österreichische Bank mit Filiale als Hauptkonto behält, nutzt das Gratiskonto als Zweitkonto. Das kostet nichts und bringt die Vorteile beider Welten.'),
        p('Ein Punkt, an den viele erst spät denken: Für den Antrag auf Familienbeihilfe, die Arbeitnehmerveranlagung oder Förderungen gibst du ebenfalls eine IBAN an. Das funktioniert mit ausländischen IBANs genauso. Prüfe nach dem Wechsel trotzdem bei FinanzOnline und bei der Sozialversicherung, ob dort noch die alte Kontonummer hinterlegt ist, damit Rückzahlungen nicht ins Leere laufen.'))))
    S.append(('Quellen',prose(ul([ext(Q_AT['sepa']),ext(Q_AT['fma']),ext(Q_AT['es']),ext(Q_AT['ak_basis']),ext(Q_AT['ak_wechsel']),ext(Q_AT['bmf'])]
        +quellen_banken(X)+['Karten, Bargeld, IBAN und Überziehung: Preislisten und Entgeltinformationen der Banken, verlinkt bei jedem Konto im Vergleich. Stand: '+E(c['stand'])+'.']))))
    F=[('Muss mein Arbeitgeber eine ausländische IBAN akzeptieren?',
        'Ja. Artikel 9 der SEPA-Verordnung verbietet es, eine IBAN aus einem anderen SEPA-Land abzulehnen. Das gilt für Arbeitgeber, Vermieter, Versicherungen und Behörden. Weigert sich jemand, kannst du das der Finanzmarktaufsicht melden.'),
       ('Muss ich Zinsen bei einer ausländischen Bank selbst versteuern?',
        'Oft ja. Eine Bank ohne Abzug der österreichischen KESt zahlt die Zinsen brutto aus. Dann gibst du sie in der Einkommensteuererklärung an. Manche ausländische Anbieter haben eine steuerliche Vertretung in Österreich und ziehen die KESt doch ab, das steht in deren Unterlagen.'),
       ('Kann ich bei diesen Konten Bargeld einzahlen?',
        'Nur eingeschränkt. Ohne Filialen geht es höchstens über Partner im Handel oder spezielle Automaten, und das kostet meist einen Prozentsatz. Wer regelmäßig Bargeld einzahlt, ist mit einem Konto bei einer Filialbank besser bedient.'),
       ('Bekomme ich ohne Gehaltseingang einen Überziehungsrahmen?',
        (f'Bei {konten(len(nodispo))} in dieser Liste gibt es keinen. ' if nodispo else '')+'Wo es einen gibt, setzt die Bank in der Regel ein regelmäßiges Einkommen und eine Bonitätsprüfung voraus. Ein Konto ohne Rahmen schützt dich dafür vor teuren Überziehungszinsen.')]
    return dict(lede='Konten, die in Österreich ganz ohne Bedingung gratis sind: kein Gehaltseingang, keine Altersgrenze. Darunter, was eine ausländische IBAN für dich bedeutet und worauf du bei Karte und Bargeld achtest.',secs=S,faq=F)


# =====================================================================
# MIT KREDITKARTE
# =====================================================================
def kk_de(c):
    eur,pct,L,LI,RG=c['eur'],c['pct'],c['link'],c['liste'],c['rg']
    X=c['lists'].get('mit-kreditkarte') or []
    A=[k for k in c['alle'] if k['art'] in ('standard','premium')]
    frei=[k for k in X if k['kf_jahr']==0 or (k.get('gratis') and k['gratis'].get('kf_bedingt')==0)]
    prem=[k for k in X if k['art']=='premium']
    bon=[k for k in X if re.search(r'Bonität',k.get('kreditkarte') or '')]
    vers=[k for k in X if re.search(r'Versicherung|Reise',k.get('kreditkarte') or '')]
    fw0=[k for k in X if k.get('fremdwaehrung_prozent')==0]
    sep=[k for k in A if not k.get('kreditkarte_inkl') and k.get('kreditkarte') and not re.search(r'nicht geprüft|ohne Kreditrahmen',k['kreditkarte'])]
    debitkk=[k for k in A if re.search(r'ohne Kreditrahmen',k.get('kreditkarte') or '')]
    erstj=[k for k in sep if re.search(r'1\. Jahr[^;]{0,15}(kostenlos|gratis|0 €)',k.get('kreditkarte') or '')]
    S=[]
    S.append(('Debitkarte, Charge-Karte, Revolving-Karte: der Unterschied',
        prose(p('Fast jedes Girokonto hat heute eine Karte mit Visa- oder Mastercard-Logo. Eine Kreditkarte ist das trotzdem meistens nicht. Entscheidend ist, wann das Geld von deinem Konto abgeht.'))
        +tbl(['Kartenart','Wann wird abgebucht?','Kreditrahmen','Typisch beim Girokonto'],[
            ('Debitkarte (z. B. Visa Debit, Debit Mastercard)','sofort bei jeder Zahlung','nein, nur Guthaben und Dispo','bei fast allen Konten dabei'),
            ('girocard','sofort','nein','oft gegen Aufpreis, bei Filialbanken Standard'),
            ('Charge-Kreditkarte','einmal im Monat gesammelt','ja, von der Bank festgelegt','häufigste Kreditkarte zum Girokonto'),
            ('Revolving-Kreditkarte','in Raten, Rest wird verzinst','ja','eher bei separaten Kreditkarten-Anbietern')])
        +prose(p('Für den Alltag reicht eine Debitkarte. Eine echte Kreditkarte zeigt ihren Vorteil dort, wo ein Händler Geld blockieren will, ohne es sofort abzubuchen: Mietwagen, Hotel, Tankstelle im Ausland. Mehr im Ratgeber '+RG('kartentypen','Kartentypen')+'.'))))
    rows=[(L(k),E(k.get('kreditkarte') or ''),E(c['kfT'](k)),E(c['kurzbed'](k)),f'{eur(tot(k))} €') for k in X]
    S.append(('Diese Konten haben eine Kreditkarte ohne Aufpreis',
        prose(p(f'In dieser Liste stehen {konten(len(X))}, bei denen eine echte Kreditkarte ohne extra Jahresgebühr dabei ist. '
            +(f'Bei {konten(len(frei))} davon ist auch die Kontoführung kostenlos, ohne Bedingung oder mit Geldeingang. ' if frei else '')
            +(f'{konten(len(prem),True)} sind Premiumkonten mit Grundgebühr, bei denen die Karte Teil eines Pakets ist.' if prem else '')))
        +tbl(['Konto','Kreditkarte','Kontoführung','Gratis, wenn','Kosten im Jahr'],rows)
        +prose(p(f'Die Jahreskosten sind {standardfall(c)} gerechnet. Die Kreditkarte selbst kostet dabei nichts, Fremdwährung und Bargeld mit der Kreditkarte sind nicht eingerechnet.'))))
    rows=[(L(k),E(k['kreditkarte'])) for k in sep]
    S.append(('Was die Kreditkarte bei anderen Konten kostet',
        prose(p(f'Bei {konten(len(sep))} im Vergleich gibt es eine Kreditkarte nur gegen Aufpreis. '
            +(f'{konten(len(erstj),True)} davon {"lockt" if len(erstj)==1 else "locken"} mit einem kostenlosen ersten Jahr, danach gilt der volle Preis. ' if erstj else '')
            +'Rechne den Kartenpreis zur Kontoführung dazu, dann siehst du, ob sich ein Konto mit inklusiver Karte lohnt.'))
        +tbl(['Konto','Kreditkarte laut Preisliste'],rows)
        +prose(p((f'Vorsicht bei Begriffen: {und([L(k) for k in debitkk])} {"nennt" if len(debitkk)==1 else "nennen"} {"seine" if len(debitkk)==1 else "ihre"} Karte zwar Kreditkarte, sie hat aber keinen Kreditrahmen. Für eine Mietwagen-Kaution reicht das nicht immer. ' if debitkk else '')
            +'Wer nur eine Kreditkarte sucht und das Girokonto behalten will, findet Alternativen im '+f'<a class="lnk" href="{c["P"]}de/kreditkarten/">Kreditkarten-Vergleich</a>.'))))
    S.append(('Wofür du eine echte Kreditkarte brauchst',prose(
        ul(['<b>Mietwagen.</b> Die meisten Vermieter verlangen eine Kreditkarte auf den Namen des Fahrers und blockieren eine Kaution. Mit Debitkarte klappt das oft nicht oder nur mit teurer Zusatzversicherung. Mehr im Ratgeber '+RG('mietwagen-kaution','Mietwagen-Kaution')+'.',
            '<b>Hotels und Ferienwohnungen.</b> Auch hier wird oft ein Betrag reserviert. Bei einer Debitkarte ist das Geld dann für ein paar Tage weg.',
            '<b>Reisen außerhalb Europas.</b> In den USA, Kanada oder Australien wird die Kreditkarte überall erwartet.',
            '<b>Zahlungsaufschub.</b> Bei einer Charge-Karte kommt die Abbuchung erst einmal im Monat. Das gibt dir ein paar Wochen Luft, ohne Zinsen.',
            '<b>Versicherungen.</b> '+(f'Bei {und([L(k) for k in vers])} sind Reiseversicherungen an die Karte gekoppelt. ' if vers else 'Goldkarten haben oft Reiseversicherungen dabei. ')+'Prüfe aber, ob du sie wirklich brauchst. Mehr im Ratgeber '+RG('reiseversicherung','Reiseversicherung')+'.']))))
    S.append(('Bonität und Kreditrahmen',prose(
        p(f'Für eine echte Kreditkarte prüft die Bank deine Bonität, in der Regel mit einer Anfrage bei der {E(c["bon"])}. '
          +(f'Bei {konten(len(bon))} in dieser Liste steht die Bonitätsprüfung ausdrücklich in den Bedingungen. ' if bon else '')
          +'Fällt die Prüfung negativ aus, bekommst du meist trotzdem das Konto, aber nur mit Debitkarte.'),
        p('Den Kreditrahmen legt die Bank fest, oft orientiert am Geldeingang. Am Anfang ist er häufig niedrig und steigt mit der Zeit. Weil eine Charge-Karte einmal im Monat vom Girokonto abgebucht wird, muss dort zu diesem Zeitpunkt genug Geld sein. Sonst rutschst du in den Dispo oder die Lastschrift platzt.'),
        p('Bietet die Bank dir an, die Kreditkartenrechnung in Raten zu zahlen, sei vorsichtig. Die Zinsen dafür sind meist deutlich höher als beim Dispo. Mehr im Ratgeber '+RG('teilzahlung','Teilzahlung')+'.'),
        p('Bist du gerade dabei, einen Kredit oder eine Baufinanzierung aufzunehmen, beantrage die Kreditkarte lieber danach. Jeder Kreditrahmen wird bei der Auskunftei gemeldet und kann deine Kreditwürdigkeit kurzzeitig anders aussehen lassen.'))))
    S.append(('Kosten bei der Nutzung im Blick behalten',prose(
        ul([(f'<b>Auslandseinsatz.</b> {konten(len(fw0),True)} in dieser Liste verlangen für Kartenzahlungen in fremder Währung kein Entgelt. ' if fw0 else '<b>Auslandseinsatz.</b> ')+'Bei den anderen kostet jede Zahlung außerhalb des Euroraums einen Prozentsatz. Achte am Terminal darauf, in der Landeswährung zu zahlen, nicht in Euro: Die Umrechnung des Händlers ist fast immer teurer.',
            '<b>Bargeld mit Kreditkarte.</b> Ob es etwas kostet, steht bei jedem Konto unter „Bargeld“ und im Preisverzeichnis. Bei manchen Karten ist es weltweit gratis, bei anderen kostet jede Abhebung ein festes Entgelt.',
            '<b>Partnerkarte.</b> Die Karte für den zweiten Kontoinhaber kostet bei manchen Banken extra, auch wenn die erste inklusive ist.',
            '<b>Ersatzkarte.</b> Bei Verlust fällt oft ein Entgelt an.']),
        p('Die girocard brauchst du trotzdem vielleicht: An manchen Kassen, Parkautomaten und Ladesäulen geht nur sie. Wenn das für dich wichtig ist, prüfe in der Tabelle, ob eine girocard beim Konto dabei ist.'))))
    S.append(('So kommst du zur Kreditkarte zum Konto',prose(
        ol(['<b>Konto mit Karte beantragen.</b> Bei den meisten Konten in dieser Liste wählst du die Kreditkarte direkt im Antrag aus. Bei manchen musst du sie gesondert anklicken, sonst bekommst du nur die Debitkarte.',
            f'<b>Bonitätsprüfung abwarten.</b> Die Bank holt eine Auskunft bei der {E(c["bon"])} ein. Das dauert meist nur Minuten, manchmal fragt sie nach Gehaltsnachweisen.',
            '<b>Kreditrahmen ansehen.</b> In der App siehst du, wie viel du pro Monat ausgeben kannst. Reicht er für deinen Urlaub nicht, frag nach einer Erhöhung, bevor du losfährst.',
            '<b>Abrechnung einstellen.</b> Prüfe, ob die Rechnung voll vom Girokonto abgebucht wird. Steht dort eine Teilzahlung, stell auf volle Rückzahlung um.',
            '<b>Karte ins Smartphone legen.</b> Mit Apple Pay oder Google Pay zahlst du kontaktlos, auch wenn die Plastikkarte noch unterwegs ist. Mehr im Ratgeber '+RG('apple-pay-google-pay','Apple Pay und Google Pay')+'.']),
        p('Willst du nur die Kreditkarte wechseln, nicht das Konto, schau in den '+f'<a class="lnk" href="{c["P"]}de/kreditkarten/">Kreditkarten-Vergleich</a>'+'. Viele Karten gibt es auch ohne neues Girokonto.'))))
    S.append(('Quellen',prose(ul([ext(Q_DE['schufa']),ext(Q_DE['zkg'])]+quellen_banken(X)+quellen_banken(sep,12)
        +['Kreditkarten, Bonitätsbedingungen und Preise: Entgeltinformationen und Preisverzeichnisse der Banken, verlinkt bei jedem Konto im Vergleich. Stand: '+E(c['stand'])+'.']))))
    F=[('Ist eine Visa Debit eine Kreditkarte?',
        'Nein. Sie trägt das Visa-Logo und funktioniert online und im Ausland wie eine Kreditkarte, bucht aber jede Zahlung sofort vom Girokonto ab. Einen Kreditrahmen hat sie nicht. Bei Mietwagen-Firmen und manchen Hotels wird sie deshalb nicht immer akzeptiert.'),
       ('Kann ich die Kreditkarte auch später noch dazu bestellen?',
        'Ja, bei den meisten Banken geht das jederzeit im Online-Banking. Dann prüft die Bank deine Bonität. Manche Aktionen, etwa ein kostenloses erstes Jahr, gelten aber nur, wenn du die Karte gleich mit dem Konto beantragst.'),
       ('Was passiert, wenn die Bank mir keine Kreditkarte gibt?',
        'Das Konto bekommst du meist trotzdem, nur eben mit Debitkarte. Eine Kreditkarte ohne Schufa-Abfrage gibt es als Prepaid-Karte, die du vorher auflädst. Mehr dazu im Ratgeber '+RG('ohne-bonitaetspruefung','Kreditkarte ohne Bonitätsprüfung')+'.'),
       ('Kann ich die Kreditkarte kündigen und das Konto behalten?',
        'In der Regel ja. Die Kreditkarte ist ein eigener Vertrag. Bei Paketkonten, in denen die Karte Teil des Preises ist, sinkt die Kontoführungsgebühr dadurch aber nicht.')]
    return dict(lede='Girokonten, bei denen eine echte Kreditkarte ohne extra Jahresgebühr dabei ist. Darunter erklären wir den Unterschied zur Debitkarte, wofür du eine Kreditkarte brauchst und was sie bei anderen Konten kostet.',secs=S,faq=F)

def kk_at(c):
    eur,pct,L,LI,RG=c['eur'],c['pct'],c['link'],c['liste'],c['rg']
    X=c['lists'].get('mit-kreditkarte') or []
    A=[k for k in c['alle'] if k['art'] in ('standard','premium')]
    inkl=[k for k in A if k.get('kreditkarte_inkl')]
    sep=[k for k in A if not k.get('kreditkarte_inkl') and k.get('kreditkarte')]
    erstj=[k for k in sep if re.search(r'1\. (Vertrags)?[Jj]ahr[^;]{0,15}(gratis|kostenlos|übernommen)',k.get('kreditkarte') or '')]
    cc=[k for k in sep if re.search(r'card complete',k.get('kreditkarte') or '')]
    pl=[k for k in sep if re.search(r'PayLife',k.get('kreditkarte') or '')]
    S=[]
    S.append(('Kreditkarte und Girokonto in Österreich: meist zwei Verträge',prose(
        p('In Österreich ist die Kreditkarte nur selten fester Teil des Girokontos. Viele Banken vermitteln sie über einen eigenen Kartenanbieter. Du schließt dann neben dem Kontovertrag einen zweiten Vertrag ab, die Abrechnung kommt einmal im Monat und wird vom Girokonto eingezogen.'
          +(f' Im Vergleich sind das zum Beispiel {und([L(k) for k in cc[:3]])} mit Karten von card complete' if cc else '')
          +(f' und {und([L(k) for k in pl])} mit PayLife-Karten' if pl else '')+('.' if cc or pl else '')),
        p(f'Ohne Aufpreis dabei ist eine echte Kreditkarte im Vergleich derzeit nur bei {konten(len(inkl))}'+(f': {und([L(k) for k in inkl])}' if inkl else '')+'. '
          +(f'Das sind {"ein Premiumkonto" if len(inkl)==1 else "Premiumkonten"} mit höherem Kontoführungsentgelt. ' if inkl and all(k['art']=='premium' for k in inkl) else '')
          +'Ob sich das rechnet, hängt davon ab, ob du die Karte samt Versicherungen sowieso kaufen würdest.'),
        p('Für dich hat die Trennung Vor- und Nachteile. Der Vorteil: Du kannst Konto und Karte unabhängig voneinander wählen und wechseln. Hast du ein günstiges Gratiskonto, aber keine Kreditkarte dabei, nimmst du einfach eine Karte eines anderen Anbieters dazu. Der Nachteil: Zwei Verträge heißt zwei Preislisten, zwei Kündigungsfristen und zwei Ansprechpartner, wenn etwas schiefgeht.'))))
    S.append(('Bankomatkarte oder Kreditkarte: was ist was',
        tbl(['Karte','Abbuchung','Rahmen','Wofür gut'],[
            ('Debitkarte (Bankomatkarte, Debit Mastercard, Visa Debit)','sofort vom Konto','nur Guthaben und Überziehungsrahmen','Alltag, Bankomat, Online-Shopping'),
            ('Kreditkarte mit Monatsabrechnung','einmal im Monat gesammelt','von der Bank festgelegt','Reisen, Mietwagen, Hotels, Kaution'),
            ('Kreditkarte mit Teilzahlung','in Raten, Rest verzinst','ja','nur, wenn du die Zinsen bewusst in Kauf nimmst'),
            ('Prepaid-Karte','vorher aufgeladen','nein','ohne Bonitätsprüfung, für Jugendliche')])
        +prose(p('Seit die alte Maestro-Bankomatkarte durch Debitkarten von Mastercard und Visa ersetzt wurde, kannst du mit der normalen Kontokarte auch online und weltweit zahlen. Viele brauchen deshalb keine eigene Kreditkarte mehr. Wo sie trotzdem fehlt, merkst du meist erst am Mietwagenschalter. Mehr im Ratgeber '+RG('kartentypen','Kartentypen')+'.'),
            p('Der Unterschied zeigt sich bei Reservierungen. Ein Hotel oder eine Tankstelle blockiert vorab einen Betrag. Bei der Kreditkarte schrumpft dadurch nur dein Kartenrahmen. Bei der Debitkarte ist das Geld auf dem Girokonto für einige Tage nicht verfügbar, auch wenn am Ende weniger abgebucht wird. Wer knapp kalkuliert, kann dadurch ins Minus rutschen. Für Visa und Mastercard ist es übrigens egal, ob deine Karte Debit oder Kredit ist, beide Netze funktionieren weltweit.'))))
    rows=[(L(k),E(k['kreditkarte']),'ja' if k.get('kreditkarte_inkl') else 'nein') for k in inkl+sep]
    S.append(('Welche Kreditkarten es zu den Konten gibt',
        prose(p('Diese Angaben stammen aus den Preisblättern der Banken. Die Preise gelten für die Kreditkarte zusätzlich zum Kontoführungsentgelt, außer die Karte ist inklusive.'))
        +tbl(['Konto','Kreditkarte','Inklusive'],rows)
        +prose(p((f'{konten(len(erstj),True)} bieten Neukunden ein kostenloses erstes Jahr. Danach läuft die Karte zum normalen Preis weiter, wenn du nicht rechtzeitig kündigst. Trag dir das Datum ein. ' if erstj else '')
            +f'Eine Übersicht aller Kreditkarten, auch ohne Girokonto, findest du im <a class="lnk" href="{c["P"]}at/kreditkarten/">Kreditkarten-Vergleich</a>.'))))
    S.append(('Wann sich eine Kreditkarte zum Konto lohnt',prose(
        ul(['<b>Du mietest Autos.</b> Ohne Kreditkarte auf deinen Namen wird es bei den meisten Vermietern schwierig. Mehr im Ratgeber '+RG('mietwagen-kaution','Mietwagen-Kaution')+'.',
            '<b>Du reist außerhalb Europas.</b> Hotels und Tankstellen reservieren Beträge vorab, mit Debitkarte ist dein Geld dann gebunden.',
            '<b>Du willst Versicherungen über die Karte.</b> Goldkarten haben oft Reiseversicherungen dabei. Vergleiche aber mit einer eigenen Jahresreiseversicherung. Mehr im Ratgeber '+RG('reiseversicherung','Reiseversicherung')+'.',
            '<b>Du willst einen kurzen Zahlungsaufschub.</b> Die Monatsabrechnung bringt dir ein paar Wochen, zinsfrei.']),
        p('Zahlst du dagegen fast nur im Inland und im Euroraum, reicht die Debitkarte. Dann sparst du dir die Kartengebühr.'),
        p('Eine einfache Faustregel: Kostet die Kreditkarte im Jahr mehr, als du damit an Fremdwährungsentgelten, Versicherungen oder Mietwagen-Extras sparst, brauchst du sie nicht. Bei einer Goldkarte mit Reiseversicherung kann sich die Rechnung umdrehen, wenn du mehrmals im Jahr verreist und die Versicherung sonst separat kaufen würdest. Lies dann aber die Bedingungen: Oft gilt der Schutz nur, wenn du die Reise mit der Karte bezahlt hast.'))))
    S.append(('KSV1870-Prüfung und Kartenrahmen',prose(
        p('Für eine Kreditkarte mit Monatsabrechnung prüft der Kartenanbieter deine Bonität, oft mit einer Anfrage beim KSV1870. Manche Banken verlangen außerdem einen Mindesteingang oder einige Monate Kontobeziehung, bevor du die Karte beantragen kannst. Wird sie abgelehnt, bleibt dir die Debitkarte oder eine Prepaid-Kreditkarte. Mehr im Ratgeber '+RG('ohne-bonitaetspruefung','Kreditkarte ohne Bonitätsprüfung')+'.'),
        p('Der Rahmen gilt pro Monat. Ist er ausgeschöpft, wird die Karte abgelehnt, bis die Abrechnung durch ist. Für einen großen Urlaub kannst du beim Anbieter oft vorübergehend eine Erhöhung beantragen.'),
        p('Der KSV1870 speichert Kreditkarten als Rahmen. Solange du die Abrechnung pünktlich zahlst, schadet das nicht. Ein offener Rahmen kann aber zählen, wenn du später einen Wohnkredit beantragst. Karten, die du nicht nutzt, kündigst du deshalb besser. Welche Daten der KSV1870 über dich speichert, kannst du nach der DSGVO kostenlos erfragen.'))))
    S.append(('Kosten neben der Jahresgebühr',prose(
        ul(['<b>Fremdwährung.</b> Zahlungen außerhalb des Euroraums kosten bei den meisten Karten einen Prozentsatz. Mehr im Ratgeber '+RG('fremdwaehrung','Fremdwährung')+'.',
            '<b>Bargeld mit der Kreditkarte.</b> Fast immer teuer: festes Entgelt plus Prozentsatz. Für Bargeld nimmst du besser die Debitkarte.',
            '<b>Teilzahlung.</b> Wer statt der vollen Abrechnung nur einen Teil zahlt, zahlt hohe Zinsen. Mehr im Ratgeber '+RG('teilzahlung','Teilzahlung')+'.',
            '<b>Zusatzkarte.</b> Für Partnerin oder Partner kostet sie meist extra.',
            '<b>Mindestumsatz.</b> Manche Karten sind nur ab einem bestimmten Jahresumsatz gratis. Erreichst du ihn nicht, wird die Gebühr fällig.',
            '<b>Euro statt Landeswährung.</b> Bietet dir ein Terminal oder Bankomat im Ausland an, in Euro abzurechnen, lehne ab. Die Umrechnung des Händlers ist fast immer teurer als die deiner Bank.']),
        p('Die Preise für Kreditkarten stehen nicht immer im Preisblatt des Kontos, sondern beim Kartenanbieter. Lies beide Dokumente, bevor du unterschreibst. Was dich ein Jahr mit Karte wirklich kostet, siehst du erst, wenn du Jahresgebühr, Fremdwährung und Bargeld zusammenzählst.'))))
    std=[k for k in A if k['art']=='standard']
    fw0=[k for k in std if k.get('fremdwaehrung_prozent')==0]
    fwv=[k['fremdwaehrung_prozent'] for k in std if k.get('fremdwaehrung_prozent')]
    haeufig=max(set(fwv),key=fwv.count) if fwv else None
    rows=[(L(k),'0 %' if k.get('fremdwaehrung_prozent')==0 else (pct(k['fremdwaehrung_prozent']) if k.get('fremdwaehrung_prozent') else 'keine Angabe'),'inklusive' if k.get('kreditkarte_inkl') else ('gegen Aufpreis' if k.get('kreditkarte') else 'keine Angabe')) for k in sorted(std,key=lambda k:(k.get('fremdwaehrung_prozent') if k.get('fremdwaehrung_prozent') is not None else 99,k['bank']))]
    S.append(('Ohne Kreditkarte reisen: was die Debitkarte im Ausland kostet',
        prose(p('Wer keine Kreditkarte will, zahlt im Urlaub mit der Debitkarte. Im Euroraum kostet das bei allen Konten nichts extra. Außerhalb des Euroraums verlangen die meisten Banken ein Fremdwährungsentgelt'
            +(f', am häufigsten {pct(haeufig)} vom Betrag' if haeufig else '')+'. '
            +(f'{konten(len(fw0),True)} verzichten darauf ganz, darunter {und([L(k) for k in fw0[:4]])}. ' if fw0 else '')
            +'Für eine Reise in die USA oder nach Großbritannien kann sich ein solches Konto als Reisekonto lohnen, auch neben deinem Hauptkonto.'))
        +tbl(['Konto','Fremdwährung mit Debitkarte','Kreditkarte'],rows)))
    S.append(('Kreditkarte beantragen: so läuft es ab',prose(
        ol(['<b>Antrag stellen.</b> Bei deiner Bank im Online-Banking oder direkt beim Kartenanbieter. Du gibst Einkommen, Beruf und Wohnsituation an.',
            '<b>Bonität wird geprüft.</b> Der Anbieter fragt beim KSV1870 nach und schaut sich deine Kontoeingänge an. Manche verlangen einen Gehaltszettel.',
            '<b>Karte und PIN kommen per Post.</b> Meist getrennt, aus Sicherheitsgründen. Die Karte aktivierst du in der App oder mit der ersten Zahlung mit PIN.',
            '<b>Abrechnung festlegen.</b> Die Monatsabrechnung wird per Lastschrift vom Girokonto eingezogen. Prüfe, dass dort am Einzugstag genug Geld liegt.',
            '<b>Kündigungstermin notieren.</b> Bei Aktionen mit Gratisjahr: Trag dir den Termin ein, an dem die Gebühr fällig wird.']),
        p('Mehr Details zu Unterlagen und Dauer stehen im Ratgeber '+RG('kreditkarte-beantragen','Kreditkarte beantragen')+'. Kostenlose Kreditkarten ohne Girokonto zeigt der Ratgeber '+RG('kostenlose-kreditkarte','Kostenlose Kreditkarte')+'.'))))
    S.append(('Quellen',prose(ul([ext(Q_AT['ksv']),ext(Q_AT['ak_bank']),ext(Q_AT['fma'])]+quellen_banken(inkl+sep,15)
        +['Kreditkarten und Preise: Preisblätter und Entgeltinformationen der Banken, verlinkt bei jedem Konto im Vergleich. Stand: '+E(c['stand'])+'.']))))
    F=[('Ist die Debit Mastercard eine Kreditkarte?',
        'Nein. Sie sieht aus wie eine und funktioniert online wie eine, bucht aber sofort vom Konto ab. Einen Kreditrahmen gibt es nicht. Bei Kautionen für Mietwagen oder Hotels wird sie deshalb oft nicht akzeptiert.'),
       ('Kann ich eine Kreditkarte ohne Girokonto bei derselben Bank haben?',
        'Ja. Kartenanbieter wie card complete oder PayLife vergeben Kreditkarten auch an Menschen, die woanders ihr Konto haben. Die Abrechnung wird dann per Lastschrift von deinem bestehenden Konto eingezogen.'),
       ('Was passiert nach dem kostenlosen ersten Jahr?',
        'Die Karte läuft weiter und kostet ab dann die normale Jahres- oder Monatsgebühr. Willst du sie nicht behalten, kündige vor Ablauf des ersten Jahres. Die Frist steht im Kartenvertrag.'),
       ('Bekomme ich eine Kreditkarte mit KSV-Eintrag?',
        'Eine Kreditkarte mit Monatsabrechnung meist nicht. Eine Prepaid-Kreditkarte geht fast immer, weil du nur ausgeben kannst, was vorher aufgeladen ist.')]
    return dict(lede='Girokonten in Österreich, bei denen eine echte Kreditkarte inklusive ist, und was die Kreditkarte bei den übrigen Konten kostet. Mit dem Unterschied zwischen Debit- und Kreditkarte.',secs=S,faq=F)


# =====================================================================
# PRÄMIE
# =====================================================================
TYP={'geld':'Geldprämie oder Bonus','zeit':'Kontoführung eine Zeit lang gratis','karte':'Karte gratis','zins':'Zinsaktion','gutschein':'Gutschein','probe':'Premium-Version zum Testen'}
def praemie_de(c):
    eur,pct,L,LI,RG=c['eur'],c['pct'],c['link'],c['liste'],c['rg']
    X=c['lists'].get('praemie') or []
    T={t:[k for k in X if t in aktion_typen(k)] for t in TYP}
    B={b:[k for k in X if b in aktion_bed(k)] for b in ('eingang','wechsel','werbung','trans','lauf','neu','legi','frist')}
    geld=sorted(T['geld'],key=lambda k:-(k.get('aktion_eur') or 0))
    S=[]
    S.append(('Welche Arten von Prämien es gibt',prose(
        p(f'In dieser Liste stehen {konten(len(X))}, für die die Bank gerade eine Aktion für neue Kundinnen und Kunden hat. Nicht jede Prämie ist Bargeld. Wir unterscheiden:'),
        ul([f'<b>{TYP[t]}.</b> '+{'geld':'Die Bank zahlt dir einen festen Betrag aufs Konto, sobald du alle Bedingungen erfüllt hast.',
                               'zeit':'Die normale Kontoführungsgebühr entfällt für einige Monate oder Jahre.',
                               'karte':'Eine sonst kostenpflichtige Karte gibt es eine Zeit lang gratis.',
                               'zins':'Statt Geld gibt es einen erhöhten Zins auf dem Tagesgeld, meist für ein paar Monate.',
                               'gutschein':'Statt Geld gibt es einen Gutschein, der nur bei einem bestimmten Partner gilt.',
                               'probe':'Du testest ein teureres Kontomodell eine Zeit lang gratis.'}[t]
            +f' Aktuell bei {und([L(k) for k in T[t]])}.' for t in TYP if T[t]]),
        p((f'Die höchste Geldprämie zahlt gerade das {L(geld[0])}: {eur(geld[0]["aktion_eur"])} €. ' if geld else '')
          +'In die Sterne-Bewertung fließt eine Prämie bei uns nicht ein, weil sie einmalig ist. Die Liste ist nach der Höhe der Prämie sortiert, nicht nach der Qualität des Kontos.'))))
    rows=[(L(k),E(k.get('aktion') or ''),E(c['kfT'](k)),E(c['kurzbed'](k)),f'{eur(tot(k))} €') for k in X]
    S.append(('Alle Aktionen mit Bedingungen',
        tbl(['Konto','Aktion laut Bank','Kontoführung','Gratis, wenn','Kosten im Jahr ohne Aktion'],rows)
        +prose(p(f'Die Kosten im Jahr sind {standardfall(c)} gerechnet, ohne die Aktion. So siehst du, was das Konto kostet, wenn die Prämie längst ausgegeben ist.'))))
    S.append(('Typische Bedingungen',prose(
        p('Eine Prämie gibt es fast nie nur für die Eröffnung. Diese Bedingungen tauchen in den aktuellen Aktionen auf:'),
        ul([(f'<b>Nur für Neukunden.</b> Bei {konten(len(B["neu"]))} steht das ausdrücklich in der Aktion. ' if B['neu'] else '<b>Nur für Neukunden.</b> ')+'Wer in den letzten Monaten oder Jahren schon ein Konto bei der Bank hatte, bekommt meist nichts. Wie lange „Neukunde“ zurückreicht, steht in den Teilnahmebedingungen.',
            f'<b>Geldeingang.</b> Bei {und([L(k) for k in B["eingang"]])} muss ein Mindestbetrag eingehen, oft im ersten vollen Kalendermonat. Bareinzahlungen und Umbuchungen eigener Konten zählen dafür häufig nicht.' if B['eingang'] else None,
            f'<b>Kartenzahlungen.</b> Bei {und([L(k) for k in B["trans"]])} musst du eine bestimmte Zahl an Zahlungen mit einem Mindestbetrag machen.' if B['trans'] else None,
            f'<b>Werbeeinwilligung.</b> Bei {und([L(k) for k in B["werbung"]])} musst du zustimmen, dass die Bank dich per E-Mail kontaktieren darf.' if B['werbung'] else None,
            f'<b>Mindestlaufzeit.</b> Bei {und([L(k) for k in B["lauf"]])} muss das Konto eine bestimmte Zeit bestehen bleiben.' if B['lauf'] else None,
            f'<b>Legitimation in einer Frist.</b> Bei {und([L(k) for k in B["legi"]])} muss die Identifizierung bis zu einem Stichtag abgeschlossen sein. Ein Video-Ident, der am letzten Tag scheitert, kostet dich die Prämie.' if B['legi'] else None,
            '<b>Zusatzprodukt.</b> Manche Aktionen verlangen, dass du eine Kreditkarte oder ein Depot gleich mit eröffnest. Das kann laufende Kosten auslösen.']))))
    S.append(('Fristen: der häufigste Grund, warum die Prämie ausbleibt',prose(
        p('Bei fast jeder Aktion gibt es mehrere Stichtage. Wer einen davon verpasst, geht leer aus, und die Bank muss nicht kulant sein. Typisch sind:'),
        ol(['<b>Antragsfrist.</b> Bis wann du den Antrag stellen musst. '+(f'{konten(len(B["frist"]),True)} in der Liste nennen dafür ein festes Datum.' if B['frist'] else ''),
            '<b>Frist für die Legitimation.</b> Bis wann du dich per Video oder Post identifiziert haben musst.',
            '<b>Erfüllungszeitraum.</b> In welchem Zeitraum der Geldeingang oder die Kartenzahlungen passieren müssen.',
            '<b>Auszahlungstermin.</b> Wann die Bank zahlt. Das kann Wochen oder Monate nach der Erfüllung sein.',
            '<b>Haltefrist.</b> Wie lange das Konto danach mindestens bestehen muss.']),
        p('Unser Tipp: Speichere die Teilnahmebedingungen als PDF, sobald du den Antrag abschickst. Trag jeden Stichtag in deinen Kalender ein. Und mach Screenshots, wenn du die Werbeeinwilligung erteilst. Falls die Prämie nicht kommt, hast du damit alles in der Hand, was du für eine Nachfrage brauchst.'))))
    ex=next((k for k in geld if k['kf_jahr']>0),None)
    exf=next((k for k in geld if tot(k)==0),None)
    S.append(('Rechnung: Lohnt sich die Prämie?',prose(
        p('Eine Prämie ist einmalig, die Kontoführung läuft jeden Monat. Rechne deshalb immer über zwei Jahre:'),
        ul([(f'Beim {L(ex)} gibt es {eur(ex["aktion_eur"])} €. Ohne Aktion kostet das Konto {standardfall(c)} {eur(tot(ex))} € im Jahr. Nach zwei Jahren bleiben dir also {eur(ex["aktion_eur"]-2*tot(ex))} € übrig, nach drei Jahren {eur(ex["aktion_eur"]-3*tot(ex))} €.' if ex else None),
            (f'Beim {L(exf)} gibt es {eur(exf["aktion_eur"])} €, und das Konto kostet im Standardfall nichts. Hier bleibt die Prämie auf Dauer ein echtes Plus, solange du die Gratis-Bedingung erfüllst.' if exf else None)]),
        p('Dazu kommt deine Zeit: Konto eröffnen, Legitimation, Bedingungen erfüllen, eventuell Daueraufträge umstellen. Für 50 € lohnt sich das für viele nicht, für einige hundert Euro schon. Ein Konto, das dauerhaft teuer ist, wird durch eine Prämie nicht billig. Die dauerhaft günstigen Konten stehen in der Liste '+LI('kostenlos','Kostenlose Girokonten')+'.'))))
    S.append(('Die Haken an Kontoprämien',prose(
        ul(['<b>Werbung.</b> Wer der Werbung per E-Mail oder Telefon zustimmt, bekommt sie auch. Du kannst die Einwilligung jederzeit widerrufen. Lies aber vorher nach, ob die Prämie erst nach einer bestimmten Zeit sicher ist.',
            f'<b>Bonitätsprüfung.</b> Jede Kontoeröffnung kann eine Anfrage bei der {E(c["bon"])} auslösen. Viele Eröffnungen in kurzer Zeit sehen nicht gut aus, wenn du gerade einen Kredit oder eine Wohnung suchst.',
            '<b>Kosten für Extras.</b> Eine mitbestellte Kreditkarte oder ein Depot kann nach der Aktion Geld kosten.',
            '<b>Rückforderung.</b> Kündigst du vor Ende der Haltefrist, kann die Bank die Prämie laut Bedingungen zurückfordern.',
            '<b>Gutscheine statt Geld.</b> Ein Reisegutschein mit Mindestbuchungswert ist nur etwas wert, wenn du ohnehin bei diesem Anbieter buchen würdest.',
            '<b>Steuern.</b> Ob und wie eine Prämie zu versteuern ist, hängt von deiner Situation ab. Bei großen Beträgen frag in der Steuerberatung nach.',
            '<b>Aktion endet früher.</b> Banken können eine Aktion vorzeitig beenden, wenn das Kontingent ausgeschöpft ist. Maßgeblich ist, was am Tag deines Antrags galt. Deshalb lohnt sich das PDF der Bedingungen.']))))
    S.append(('Mehrere Konten für mehrere Prämien?',prose(
        p('Gesetzlich darfst du in Deutschland so viele Girokonten haben, wie du willst. Prämienjäger nutzen das, eröffnen ein Konto, kassieren die Prämie und kündigen nach der Haltefrist. Das ist erlaubt, solange du alle Bedingungen ehrlich erfüllst.'),
        p('Die Banken wissen das. Deshalb schließen viele Aktionen Menschen aus, die in den letzten zwölf oder mehr Monaten schon Kunde waren, und manche zählen dabei alle Marken eines Konzerns zusammen. Wer bei einer Bank schon ein Tagesgeld oder ein Depot hat, gilt oft nicht mehr als Neukunde. Und wer sein altes Konto auflöst, sollte daran denken, dass Daueraufträge und Lastschriften umgezogen werden müssen. Dabei hilft die Kontowechselhilfe, mehr im Ratgeber '+RG('girokonto-wechseln','Konto wechseln')+'.'))))
    S.append(('Prämie sicher mitnehmen: Schritt für Schritt',prose(
        ol(['<b>Bedingungen komplett lesen.</b> Nicht nur das Werbebanner, sondern die Teilnahmebedingungen. Achte auf Neukunden-Definition, Mindesteingang, Zahl der Kartenzahlungen und Haltefrist.',
            '<b>Prüfen, ob du die Bedingungen ohne Tricks erfüllst.</b> Kommt dein Gehalt rechtzeitig? Schaffst du die Kartenzahlungen im Alltag?',
            '<b>Antrag stellen und sofort legitimieren.</b> Warte nicht bis zum letzten Tag mit dem Video-Ident. Wenn die Verbindung abbricht, fehlt dir die Zeit.',
            '<b>Bedingungen abhaken.</b> Gehalt umleiten oder Dauerauftrag einrichten, Kartenzahlungen machen, Werbeeinwilligung erteilen. Notier dir, wann du was erledigt hast.',
            '<b>Auszahlung kontrollieren.</b> Kommt die Prämie zum genannten Termin nicht, schreib dem Kundenservice mit deinen Nachweisen.',
            '<b>Danach entscheiden.</b> Passt das Konto, behältst du es. Wenn nicht, kündigst du nach Ablauf der Haltefrist und ziehst mit der Kontowechselhilfe zurück oder weiter.']))))
    S.append(('Quellen',prose(ul([ext(Q_DE['zkg20']),ext(Q_DE['bgb675h']),ext(Q_DE['schufa'])]+quellen_banken(X)
        +['Aktionen, Prämienhöhe und Teilnahmebedingungen: Aktionsseiten und Teilnahmebedingungen der Banken, verlinkt bei jedem Konto im Vergleich. Aktionen ändern sich oft, maßgeblich sind die Bedingungen der Bank am Tag deines Antrags. Stand: '+E(c['stand'])+'.']))))
    F=[('Bekomme ich die Prämie, wenn ich früher schon Kunde der Bank war?',
        'Meist nicht. Die meisten Aktionen gelten nur für Neukunden. Was das genau heißt, steht in den Teilnahmebedingungen: oft kein Konto bei dieser Bank in den letzten zwölf Monaten, manchmal auch bei anderen Marken desselben Konzerns.'),
       ('Darf ich das Konto nach der Auszahlung gleich wieder kündigen?',
        'Du darfst ein Girokonto jederzeit kündigen. Haben die Bedingungen aber eine Mindestlaufzeit, kann die Bank die Prämie zurückfordern, wenn du früher gehst. Warte deshalb, bis die Haltefrist abgelaufen ist.'),
       ('Wann wird die Prämie ausgezahlt?',
        'Das steht in den Teilnahmebedingungen. Oft vergehen nach Erfüllung aller Bedingungen noch einige Wochen bis Monate. Kommt die Prämie nach dem genannten Termin nicht, frag schriftlich nach und leg deine Nachweise bei.'),
       ('Kann ich die Werbeeinwilligung nach der Eröffnung widerrufen?',
        'Ja, ein Widerruf ist jederzeit möglich. Manche Aktionen verlangen aber, dass die Einwilligung bis zur Auszahlung besteht. Widerrufe deshalb erst, wenn die Prämie auf dem Konto ist.')]
    return dict(lede='Hier siehst du, welche Banken neuen Kundinnen und Kunden gerade eine Prämie, einen Bonus oder kostenlose Monate geben, sortiert nach der Höhe. Darunter: welche Bedingungen und Fristen gelten und wann sich das wirklich rechnet.',secs=S,faq=F)

def praemie_at(c):
    eur,pct,L,LI,RG=c['eur'],c['pct'],c['link'],c['liste'],c['rg']
    X=c['lists'].get('praemie') or []
    T={t:[k for k in X if t in aktion_typen(k)] for t in TYP}
    B={b:[k for k in X if b in aktion_bed(k)] for b in ('eingang','wechsel','werbung','trans','lauf','neu','legi','frist')}
    geld=sorted(T['geld'],key=lambda k:-(k.get('aktion_eur') or 0))
    stud=[k for k in X if k['art']=='student']
    bank_n=len({k['bank'] for k in X})
    S=[]
    S.append(('So sehen Kontoaktionen in Österreich aus',prose(
        p(f'In dieser Liste stehen {konten(len(X))} von {bank_n} Banken, die gerade eine Neukunden-Aktion haben. '+(f'{konten(len(stud),True)} davon sind Studentenkonten. ' if stud else '')+'Die Aktionen sind in Österreich sehr unterschiedlich. Wir teilen sie so ein:'),
        ul([f'<b>{TYP[t]}.</b> '+{'geld':'Ein fester Betrag als Bonus, oft an einen Kontowechsel oder Gehaltseingang geknüpft.',
                               'zeit':'Das Kontoführungsentgelt entfällt für einige Monate oder das erste Jahr.',
                               'karte':'Eine Karte, die sonst etwas kostet, gibt es eine Zeit lang gratis, etwa eine Kreditkarte im ersten Jahr.',
                               'zins':'Ein höherer Zins auf Guthaben für eine begrenzte Zeit.',
                               'gutschein':'Ein Gutschein bei einem Partner statt Geld.',
                               'probe':'Ein teureres Kontomodell zum Ausprobieren, danach gilt der gewählte Tarif.'}[t]
            +f' Aktuell bei {und([L(k) for k in T[t]])}.' for t in TYP if T[t]]),
        p((f'Den höchsten Gegenwert laut Bank bietet derzeit {L(geld[0])} mit {eur(geld[0]["aktion_eur"])} €. ' if geld else '')
          +'Bei gratis Kontoführung rechnen wir als Gegenwert das gesparte Entgelt. Die Prämie zählt nicht zur Sterne-Bewertung, sie sagt nichts darüber, wie gut das Konto nach der Aktion ist.'))))
    rows=[(L(k),E(k.get('aktion') or ''),f'{eur(k["aktion_eur"])} €' if k.get('aktion_eur') else 'keine Angabe',E(c['kfT'](k)),f'{eur(tot(k))} €') for k in X]
    S.append(('Alle Aktionen im Überblick',
        tbl(['Konto','Aktion laut Bank','Gegenwert','Kontoführung danach','Kosten im Jahr ohne Aktion'],rows)
        +prose(p(f'Die Jahreskosten gelten {standardfall(c)}, ohne Aktion. Sie zeigen, was dich das Konto kostet, wenn die Aktion vorbei ist.'))))
    S.append(('Kontowechsel-Bonus und andere Bedingungen',prose(
        p('Wofür die Bank zahlt, sagt viel über die Aktion. Sie will, dass du das Konto als Hauptkonto nutzt, nicht nur die Prämie abholst. Deshalb diese Bedingungen:'),
        ul([f'<b>Kontowechsel-Service.</b> Bei {und([L(k) for k in B["wechsel"]])} musst du den Kontowechsel über die Bank abwickeln und eine Mindestzahl an Lastschrift-Partnern umstellen lassen. Der gesetzliche Kontowechsel-Service ist für dich kostenlos, Daueraufträge und Lastschriften zieht die Bank für dich um.' if B['wechsel'] else None,
            f'<b>Gehalt oder Pension.</b> Bei {und([L(k) for k in B["eingang"]])} muss ein Mindesteingang kommen, meist innerhalb weniger Wochen oder Monate.' if B['eingang'] else None,
            (f'<b>Nur für Neukunden.</b> Bei {konten(len(B["neu"]))} steht das ausdrücklich dabei. ' if B['neu'] else '<b>Nur für Neukunden.</b> ')+'Wer schon ein Konto bei der Bank hat oder kürzlich hatte, ist meist ausgeschlossen.',
            '<b>Online-Eröffnung oder App-Login.</b> Einige Aktionen gelten nur, wenn du online eröffnest oder Internetbanking aktiv nutzt.',
            '<b>Kreditkarte nur mit Bonität.</b> Wo die Aktion eine Karte gratis macht, prüft der Kartenanbieter vorher deine Bonität, oft beim KSV1870.']))))
    S.append(('Stichtage, die du kennen musst',prose(
        p('Eine Aktion hat fast immer mehrere Fristen. '+(f'{konten(len(B["frist"]),True)} in dieser Liste nennen ein festes Datum. ' if B['frist'] else '')+'Achte auf:'),
        ol(['<b>Ende der Aktion.</b> Bis wann du eröffnen oder beauftragen musst.',
            '<b>Zeitraum für die Bedingungen.</b> Etwa „innerhalb von 90 Tagen“ für Gehaltseingang und Kontowechsel.',
            '<b>Gutschrift.</b> Ein Bonus wird oft erst Monate später gebucht.',
            '<b>Ende der Gratiszeit.</b> Bei gratis Kontoführung: ab wann das normale Entgelt gilt. Bei Abrechnung pro Quartal kann das Gratisjahr ein paar Monate länger oder kürzer sein, als du denkst.']),
        p('Lade die Aktionsbedingungen als PDF herunter, bevor du eröffnest. Aktionsseiten verschwinden oft, sobald die Aktion vorbei ist.'))))
    ex=next((k for k in geld if 'geld' in aktion_typen(k) and k['kf_jahr']>0),None)
    S.append(('Rechnet sich die Aktion?',prose(
        p('Rechne mit dem, was das Konto nach der Aktion kostet. Eine gratis Kontoführung im ersten Jahr ist nett, aber ab dem zweiten Jahr zahlst du den vollen Preis, und den meist für viele Jahre.'),
        p((f'Ein Beispiel: Beim {L(ex)} ist der Gegenwert laut Bank {eur(ex["aktion_eur"])} €. Ohne Aktion kostet das Konto {eur(tot(ex))} € im Jahr. Über drei Jahre gerechnet zahlst du also {eur(3*tot(ex)-ex["aktion_eur"])} € mehr, als du bekommst. ' if ex and 3*tot(ex)>ex['aktion_eur'] else (f'Ein Beispiel: Beim {L(ex)} ist der Gegenwert laut Bank {eur(ex["aktion_eur"])} €, das Konto kostet ohne Aktion {eur(tot(ex))} € im Jahr. ' if ex else ''))
          +'Ein Konto, das dauerhaft gratis ist, schlägt über die Jahre fast jede Aktion. Die findest du in der Liste '+LI('kostenlos','Kostenlose Girokonten')+'. Eine Aktion lohnt sich vor allem dann, wenn du das Konto ohnehin wolltest.'))))
    S.append(('Worauf du bei Aktionen aufpassen solltest',prose(
        ul(['<b>Automatische Verlängerung.</b> Eine Kreditkarte, die im ersten Jahr gratis ist, kostet danach. Wer sie nicht will, muss kündigen.',
            '<b>Paketpreise.</b> Bei teuren Kontomodellen deckt die Aktion oft nur einen kleinen Teil der Kosten ab.',
            '<b>Wechsel, aber richtig.</b> Kündige das alte Konto erst, wenn alle Lastschriften umgestellt sind. Über den gesetzlichen Kontowechsel-Service erledigt das die neue Bank.',
            '<b>Ausländische Anbieter.</b> Neobanken mit Sitz im Ausland machen beim gesetzlichen Kontowechsel-Service nicht immer mit, und ihre Zinsaktionen sind steuerlich anders zu behandeln: Ohne KESt-Abzug musst du die Zinsen selbst erklären.',
            '<b>Bonität.</b> Mehrere Konto- und Kartenanträge in kurzer Zeit können bei Banken und beim KSV1870 Spuren hinterlassen.']))))
    S.append(('Darf ich mehrere Konten eröffnen?',prose(
        p('Ja. In Österreich gibt es keine Höchstzahl für Girokonten. Du kannst also mehrere Aktionen nacheinander mitnehmen, solange du jeweils als Neukunde giltst. Für Studierende lohnt sich ein Blick in die Liste '+LI('studenten','Girokonten für Studierende')+', weil dort Konten und Aktionen ohne Kontoführungsentgelt besonders häufig sind.'),
        p('Bedenke aber den Aufwand. Jedes Konto braucht eine Identifizierung, eine App, einen Überblick über Karten und PINs. Und jedes Konto, das du nicht mehr brauchst, kostet nach der Aktion womöglich Geld, bis du es kündigst.'))))
    S.append(('Quellen',prose(ul([ext(Q_AT['ak_wechsel']),ext(Q_AT['ak_bank']),ext(Q_AT['ris']),ext(Q_AT['ksv'])]+quellen_banken(X)
        +['Aktionen und Teilnahmebedingungen: Aktionsseiten und Preisblätter der Banken, verlinkt bei jedem Konto im Vergleich. Aktionen ändern sich oft, es gelten die Bedingungen am Tag deines Antrags. Stand: '+E(c['stand'])+'.']))))
    F=[('Was ist ein Kontowechsel-Bonus?',
        'Eine Prämie, die die Bank nur zahlt, wenn du über ihren Kontowechsel-Service zu ihr wechselst und eine Mindestzahl an Lastschrift-Partnern oder Daueraufträgen mitnimmst. Der Service selbst ist gesetzlich geregelt und für dich kostenlos.'),
       ('Gelte ich als Neukunde, wenn ich bei der Bank schon ein Sparbuch habe?',
        'Das hängt von der Aktion ab. Manche Banken zählen nur Girokonten, andere jede Kundenbeziehung. Die Definition steht in den Teilnahmebedingungen. Im Zweifel frag vor der Eröffnung schriftlich nach.'),
       ('Was passiert nach dem Gratisjahr mit meinem Konto?',
        'Es läuft weiter, mit dem normalen Kontoführungsentgelt. Die Bank muss dich darauf nicht eigens hinweisen. Prüf vor Ablauf, ob das Konto noch zu dir passt, und wechsle sonst rechtzeitig.'),
       ('Kann ich die Prämie verlieren, wenn ich das Konto schnell wieder kündige?',
        'Ja, wenn die Bedingungen eine Mindestdauer vorsehen oder die Gutschrift erst nach Monaten erfolgt. Ist das Konto zum Gutschrifttermin schon geschlossen, gibt es meist nichts mehr.')]
    return dict(lede='Konten, für die österreichische Banken gerade einen Bonus, gratis Monate oder eine Karte schenken, sortiert nach dem Gegenwert. Darunter: die üblichen Bedingungen, die wichtigen Stichtage und wann sich eine Aktion rechnet.',secs=S,faq=F)


def texte(land,ctx):
    if land=='de':
        return {'kostenlos':kostenlos_de(ctx),'ohne-geldeingang':ohne_de(ctx),'mit-kreditkarte':kk_de(ctx),'praemie':praemie_de(ctx)}
    if land=='at':
        return {'kostenlos':kostenlos_at(ctx),'ohne-geldeingang':ohne_at(ctx),'mit-kreditkarte':kk_at(ctx),'praemie':praemie_at(ctx)}
    return {}
