# Ratgeber „Firmenkreditkarte“ für AT und DE (gleicher Slug „business“, hreflang-Paar). Ersetzt die statische Kurzfassung.
# Gebühren, Fremdwährung, Bargeld, Versicherung und Rückzahlung kommen aus den Kartendaten; Mitarbeiterkarten, Haftung,
# Export, Rechtsform und Zahlungsziel aus daten/{land}/business-merkmale.json (Anbieterunterlagen, Stand im JSON).
# Aufruf aus ratgeber.build(land): register(land,art,P,best,K,nprv,eur,KM,de1,pct)
import html,json,os,re
E=lambda s: html.escape(str(s)) if s is not None else ''
SP=os.path.dirname(os.path.abspath(__file__))

def _tbl(head,rows):
    h=''.join(f'<th>{c}</th>' for c in head)
    b=''.join('<tr>'+''.join(f'<td>{c}</td>' for c in r)+'</tr>' for r in rows)
    return f'<div class="tbl wide"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'

def register(land,art,P,best,K,nprv,eur,KM,de1,pct):
    N={'at':'Österreich','de':'Deutschland'}[land]
    MJ=json.load(open(SP+f'/daten/{land}/business-merkmale.json'))
    def M(c):
        s=c['slug']
        if s in MJ: return MJ[s]
        for k in ('n26-business','bunq-business'):
            if s.startswith(k.split('-')[0]+'-') and k in MJ: return MJ[k]
        return {}
    biz=[c for c in K if c['art']!='Privat']
    kc=sorted([c for c in biz if c['typ'] in ('Kreditkarte','Charge')],key=lambda c:(c.get('fee') or 0))
    dc=sorted([c for c in biz if c['typ'] not in ('Kreditkarte','Charge')],key=lambda c:(c.get('fee') or 0))
    alle=kc+dc
    def L(c): return f'<a class="lnk" href="{P}{land}/kreditkarten/{c["slug"]}/">{E(c["titel"])}</a>'
    def fee(c):
        f=c.get('fee'); t='kostenlos' if f==0 else (f'{eur(f)} €' if f is not None else 'keine Angabe')
        if c.get('fee1')==0 and f: t+=' <small>(1. Jahr 0 €)</small>'
        elif c.get('fee1') and f and c['fee1']<f: t+=f' <small>(1. Jahr {eur(c["fee1"])} €)</small>'
        return t
    def fxs(c):
        v=c.get('fx'); return 'keine Angabe' if v is None else ('0 %' if v==0 else pct(v))
    def cashs(c):
        t=c.get('cashText') or KM.cashT(c) or 'keine Angabe'
        t=re.split(r';|\s\(',t)[0].strip()
        return t if len(t)<=70 else t[:67].rstrip()+'…'
    def konto(c):
        g=c.get('giro'); kp=M(c).get('konto_pflicht')
        if g is True or kp is True: return 'ja'
        if g is False or kp is False: return 'nein'
        return 'keine Angabe'
    def haft_short(c):
        h=M(c).get('haftung')
        if not h: return 'keine Angabe'
        if 'persönlich' in h and 'zusätzlich' in h: return 'Inhaber persönlich, bei Gesellschaft auch die Firma'
        if 'persönlich' in h: return 'Inhaber persönlich'
        if 'gesamtschuldnerisch' in h or 'solidarisch' in h: return 'Firma und Inhaber gemeinsam'
        return E(h)
    def zk(c):
        z=M(c).get('zusatzkarten'); return E(z) if z else 'keine Angabe'
    def zz(c):
        z=M(c).get('zahlungsziel'); return E(z) if z else 'keine Angabe'
    def ins(c):
        t=c.get('tier'); i=c.get('insText')
        if i and i.startswith('Keine'): return 'keine'
        if t is None and not i: return 'keine Angabe'
        if t==0: return 'keine'
        return {1:'Basis',2:'mittel',3:'umfangreich',4:'Premium'}.get(t,'ja')+(' <small>(Reise)</small>' if t else '')
    def typ(c): return {'Kreditkarte':'Kreditkarte (Teilzahlung)','Charge':'Charge (Monatsrechnung)','Debit':'Debit (Geschäftskonto)'}.get(c['typ'],c['typ'])
    t_ueber=_tbl(['Karte','Typ','Jahresgebühr','Konto beim Anbieter nötig','Mitarbeiterkarten laut Anbieter','Haftung laut Bedingungen','Zahlungsziel'],
                 [(L(c),typ(c),fee(c),konto(c),zk(c),haft_short(c),zz(c)) for c in alle])
    t_kost=_tbl(['Karte','Jahresgebühr','Fremdwährung','Bargeld','Reiseversicherung','Buchhaltungsexport laut Anbieter'],
                [(L(c),fee(c),fxs(c),E(cashs(c)),ins(c),E(M(c).get('export') or 'keine Angabe')) for c in alle])
    # Rechenbeispiel: zwei Nutzungsprofile, Kosten pro Jahr aus Gebühr, Fremdwährung und Bargeld
    import score
    def cost(c,fxvol,ncash):
        f=c.get('fee') or 0
        fx=(c.get('fx') or 0)/100*fxvol
        cc=score.cash200(c.get('cash'))
        cash=cc*ncash if isinstance(cc,(int,float)) else 0.0
        return f+fx+cash
    rows=[]
    for c in alle:
        a=cost(c,0,0); b=cost(c,24000*0.2,6)
        rows.append((L(c),f'{eur(round(a,2))} €',f'{eur(round(b,2))} €'))
    t_bsp=_tbl(['Karte','Inland, keine Barabhebung','Mit Reisen: 4.800 € in Fremdwährung, 6 Abhebungen à 200 €'],rows)
    cheap_in=min(alle,key=lambda c:cost(c,0,0)); cheap_out=min(alle,key=lambda c:cost(c,4800,6))
    exp_out=max(kc,key=lambda c:cost(c,4800,6))
    with_staff=[c for c in alle if M(c).get('zusatzkarten') and not M(c)['zusatzkarten'].lower().startswith('keine') and not c['slug'].startswith(('bunq-free','bunq-core'))]
    no_staff=[c for c in alle if (M(c).get('zusatzkarten') or '').lower().startswith('keine')]
    haft_firma=[c for c in alle if M(c).get('haftung') and ('gesamtschuldnerisch' in M(c)['haftung'] or 'solidarisch' in M(c)['haftung'])]
    haft_none=[c for c in alle if not M(c).get('haftung')]
    konto_ja=[c for c in alle if konto(c)=='ja']; konto_nein=[c for c in alle if konto(c)=='nein']
    export_ja=[c for c in alle if M(c).get('export') and 'kein' not in M(c)['export'][:12].lower()]
    names=lambda X: ', '.join(L(c) for c in X)
    kleinbetrag='400 €' if land=='at' else '250 €'
    kb_norm='§ 11 Abs. 6 UStG' if land=='at' else '§ 33 Umsatzsteuer-Durchführungsverordnung'
    if land=='at':
        intro=f'''<div class="prose"><p>In {N} ist das Angebot an Firmenkreditkarten klein: In unserem Vergleich stehen {len(biz)} Business-Karten, {names(kc)} als Charge-Karten mit Monatsrechnung und {names(dc)} als Debitkarte zum Geschäftskonto. Dazu kommen die Business-Karten von card complete und PayLife, die über Rahmenvereinbarungen mit dem Unternehmen laufen und die wir unten kurz einordnen.</p>
<p>Die erste Frage ist nicht, welche Karte, sondern ob überhaupt eine eigene Firmenkarte nötig ist. Als Einzelunternehmer darfst du geschäftliche Ausgaben auch mit einer Privatkarte bezahlen; steuerlich zählt die Rechnung, nicht die Karte. Eine getrennte Karte spart vor allem Zeit: Die Monatsabrechnung enthält nur Betriebsausgaben, nichts muss aussortiert werden. Bei einer GmbH liegt die Sache anders: Die Gesellschaft ist eine eigene Person, private und betriebliche Zahlungen gehören von Anfang an getrennt, und eine Karte, die auf die Gesellschaft läuft oder zumindest über das Firmenkonto abgerechnet wird, ist der saubere Weg.</p></div>'''
        weitere=f'''<div class="prose"><p>Außerhalb unserer Rangliste gibt es drei Angebote, die für Firmen mit mehreren Mitarbeitern oft die erste Adresse sind: Die <b>card complete Visa Business Classic</b> (58,30 € im Jahr, Platinum 126,30 €) wird nur mit Firmenhaftung ausgestellt, Mitarbeiterkarten laufen über eine Rahmenvereinbarung mit dem Unternehmen, das Zahlungsziel beträgt 20 Tage. Die <b>PayLife Business Classic</b> (31 €) und <b>Business Gold</b> (64 €, im ersten Jahr 32 € bis 31.12.2026) zeigen im Smart Data Portal die Umsätze aller Mitarbeiterkarten und exportieren sie als XLS oder CSV; der Rahmen liegt bei 2.200 € bzw. 5.000 € im Monat. Preise je Mitarbeiterkarte nennen beide Anbieter nicht öffentlich, sie stehen in der Rahmenvereinbarung.</p></div>'''
        haftung=f'''<div class="prose"><p>Bei den Amex-Karten haftet laut Mitgliedschaftsbedingungen der Hauptkarteninhaber persönlich; ist das Unternehmen eine GmbH oder AG, haftet es zusätzlich gesamtschuldnerisch, und Zusatzkarteninhaber haften für ihre eigenen Umsätze mit. Bei N26 Business Metal läuft das Konto auf die Person, nicht auf eine Firma, eine Gesellschaft kann es gar nicht eröffnen. Bei der Oberbank regeln die Sonderbedingungen nur die Haftung des Kontoinhabers, eine Trennung zwischen Firma und Karteninhaber steht dort nicht; card complete stellt Business-Karten ausschließlich mit Firmenhaftung aus.</p>
<p>Für Einzelunternehmer ändert die Haftungsklausel wenig: Sie haften ohnehin mit dem Privatvermögen. Für Geschäftsführer einer GmbH ist sie der wichtigste Satz im Vertrag: Unterschreibst du als Hauptkarteninhaber, stehst du für die Kartenumsätze mit deinem Privatvermögen ein, auch für die der Mitarbeiterkarten. Frag vor dem Antrag schriftlich nach, ob die Karte mit reiner Firmenhaftung möglich ist.</p></div>'''
        mitarbeiter=f'''<div class="prose"><p>In unserem Vergleich bieten nur die Amex-Karten Mitarbeiterkarten an: bis zu 99 Zusatzkarten, im ersten Jahr kostenlos, danach 30 € je Business-Zusatzkarte und 60 € je Gold-Zusatzkarte im Jahr; Zusatzkarten dürfen nur Teilhaber, Vorstände oder Mitarbeiter bekommen. Eigene Limits je Zusatzkarte nennt Amex Österreich nicht, das Umsatz- und Bargeldlimit gilt kontoweit. N26 Business Metal ist personengebunden, Karten dürfen nicht weitergegeben werden; dafür gibt es bis zu fünf physische und sechs virtuelle Karten für den Inhaber selbst, etwa für Abos und Online-Dienste. Die Oberbank nennt in keiner Unterlage Mitarbeiterkarten. Wer mehrere Mitarbeiter ausstatten will, landet in {N} daher meist bei card complete oder PayLife mit Rahmenvereinbarung, oder bei den Firmenkarten der Hausbank.</p></div>'''
        zahlungsziel=f'''<div class="prose"><p>Charge-Karten geben Liquidität: Zwischen Einkauf und Abbuchung liegen bei der Oberbank laut Anbieter bis zu sechs Wochen (Umsatzübersicht zu Monatsbeginn, Abbuchung zehn Arbeitstage später), bei Amex Business Gold laut Produktseite bis zu 50 Tage. Die Amex Business Card hat kein ausgewiesenes verlängertes Ziel; die Rechnung wird per Lastschrift eingezogen, Verzugszinsen fallen erst 30 Tage nach Abrechnungsdatum an. Die Debitkarte von N26 bucht sofort ab, ein Zahlungsziel gibt es nicht. Teilzahlung mit Zinsen bietet in {N} keine der Firmenkarten in unserem Vergleich an.</p></div>'''
        kurz=(f'{len(biz)} Firmenkarten in unserem {N}-Vergleich: {names(kc)} als Charge-Karten, {names(dc)} als Debitkarte. Nur Amex bietet Mitarbeiterkarten (bis 99, ab dem 2. Jahr 30 bzw. 60 € je Karte); bei Amex haftet der Karteninhaber persönlich, bei einer GmbH zusätzlich die Firma. Export in die Buchhaltung bietet keine der vier Karten laut Unterlagen, N26 immerhin CSV-Kontoauszüge. '+(f'In beiden Nutzungsprofilen unseres Rechenbeispiels ist die {L(cheap_in)} am günstigsten.' if cheap_in is cheap_out else f'Im Inland ohne Barabhebung ist die {L(cheap_in)} am günstigsten, mit Fremdwährung die {L(cheap_out)}.'))
    else:
        intro=f'''<div class="prose"><p>In {N} stehen {len(biz)} Business-Karten in unserem Vergleich, von der kostenlosen Debitkarte zum Geschäftskonto (N26, bunq, SumUp) über Charge-Karten der Filialbanken (Deutsche Bank, Postbank, Commerzbank, Sparkasse) bis zur Amex Business Platinum für 850 € im Jahr. Echte Kreditkarten mit Teilzahlung sind die Ausnahme: nur die beiden TARGOBANK-Karten, mit 15,24 % Sollzins.</p>
<p>Die erste Frage ist nicht, welche Karte, sondern ob überhaupt eine eigene Firmenkarte nötig ist. Als Freiberufler oder Einzelunternehmer darfst du Betriebsausgaben auch mit der Privatkarte bezahlen; steuerlich zählt die Rechnung, nicht die Karte. Eine getrennte Karte spart Zeit, weil die Abrechnung nur Betriebsausgaben enthält. Bei GmbH und UG liegt die Sache anders: Die Gesellschaft ist eine eigene Person, private und betriebliche Zahlungen gehören getrennt, und eine Karte, die auf die Gesellschaft läuft oder über das Firmenkonto abgerechnet wird, ist der saubere Weg. N26 Business ist dafür ungeeignet, weil das Konto nur auf den Namen einer Person läuft, bunq Free ebenfalls; bunq ab Core, SumUp und die Banken nehmen auch Gesellschaften.</p></div>'''
        weitere=''
        haftung=f'''<div class="prose"><p>Bei {len(haft_firma)} der {len(biz)} Business-Karten regeln die Bedingungen eine gemeinsame Haftung: {names(haft_firma)}. Bei Postbank und Commerzbank ist der Karteninhaber Vertragspartner und das Unternehmen tritt der Schuld bei (gesamtschuldnerisch; der Mitarbeiter haftet nur für seine eigenen Umsätze). Bei Amex haftet der Hauptkarteninhaber persönlich, eine GmbH oder Personengesellschaft zusätzlich. Bei {len(haft_none)} Modellen steht in den öffentlichen Unterlagen keine Regel, darunter Deutsche Bank, Miles &amp; More, TARGOBANK, Sparkasse und alle Debitkarten; bei N26 läuft das Konto ohnehin auf die Person.</p>
<p>Für Einzelunternehmer ändert die Klausel wenig: Sie haften ohnehin mit dem Privatvermögen. Für Geschäftsführer einer GmbH oder UG ist sie der wichtigste Satz im Vertrag: Unterschreibst du als Hauptkarteninhaber, stehst du für die Kartenumsätze mit deinem Privatvermögen ein, auch für die der Mitarbeiterkarten. Lass dir vor dem Antrag schriftlich bestätigen, ob die Karte mit reiner Firmenhaftung möglich ist; bei Rahmenvereinbarungen (Postbank, Commerzbank, Sparkasse) ist das die übliche Form.</p></div>'''
        mitarbeiter=f'''<div class="prose"><p>Mitarbeiterkarten gibt es bei {len(with_staff)} der {len(biz)} Business-Karten. Am großzügigsten ist Amex: bis zu 99 Zusatzkarten, bei Business Gold und den Amazon-Karten ohne Aufpreis, bei der Business Card 30 € je Karte, bei Platinum eine Platinum- und bis zu 98 Gold-Zusatzkarten inklusive. Die Filialbanken rechnen je Karte den vollen Jahrespreis: Postbank 30 bzw. 80 €, Commerzbank 34,90 bzw. 79,90 €, Deutsche Bank 29 bzw. 79 €, Sparkasse 37,50 bis 60 € (Beispiel Berliner Sparkasse); Miles &amp; More Business verlangt für jede Zusatzkarte denselben Monatspreis wie für die Hauptkarte. Eigene Limits je Karte bestätigen Amex, Postbank, Commerzbank, Deutsche Bank und bunq; bei Postbank wird der Rahmen je Karte mit der Bank vereinbart.</p>
<p>Keine Mitarbeiterkarten gibt es bei {names(no_staff)}: Das Konto läuft auf den eigenen Namen, Karten dürfen nicht weitergegeben werden. Dafür gibt es dort bis zu sechs virtuelle Karten für den Inhaber, etwa für Abos und Online-Dienste. bunq bietet Mitarbeiterkarten erst ab Pro Business (drei Karten inklusive), SumUp im Geschäftskonto Plus bis zu drei Karten für das Team.</p></div>'''
        zahlungsziel=f'''<div class="prose"><p>Charge-Karten geben Liquidität, und die Spanne ist groß: Amex Business Platinum zieht erst 28 Tage nach der Abrechnung ein, insgesamt bis zu 58 Tage nach dem Einkauf; Business Gold auf Antrag 20 Tage nach Abrechnung, bis zu 50 Tage; die Amazon Business Cards 20 Tage, für Amazon-Einkäufe wahlweise 60 bzw. 90 Tage statt Punkten. TARGOBANK bucht 20 Tage nach Rechnungsdatum ab (bis zu 50 Tage), Deutsche Bank 10 Tage nach der Abrechnung (mit PlusPaket 20), Postbank 10 Tage. Commerzbank und die Amex Business Card ziehen die Rechnung sofort nach Erstellung ein, ein verlängertes Ziel gibt es dort nicht. Die Debitkarten buchen sofort ab.</p>
<p>Teilzahlung bieten nur die TARGOBANK-Karten an (Mindestrate 5 %, mindestens 10 €, 15,24 % Sollzins); für ein Unternehmen ist das in aller Regel teurer als ein Kontokorrentkredit und nur als kurze Überbrückung vertretbar.</p></div>'''
        kurz=(f'{len(biz)} Firmenkarten in unserem {N}-Vergleich, von 0 € (Debitkarten zum Geschäftskonto) bis 850 € (Amex Business Platinum). Mitarbeiterkarten gibt es bei {len(with_staff)} davon, bei Amex Business Gold und den Amazon-Karten ohne Aufpreis, bei den Filialbanken zum vollen Jahrespreis je Karte; N26 Business hat keine. '
              f'Gemeinsame Haftung von Firma und Karteninhaber ist bei Postbank, Commerzbank und Amex geregelt, bei {len(haft_none)} Modellen gar nicht. Buchhaltungsexport (CSV oder Schnittstellen) nennen die Unterlagen bei {len(export_ja)} Modellen, DATEV nur bunq. '+(f'In beiden Nutzungsprofilen unseres Rechenbeispiels ist die {L(cheap_in)} am günstigsten.' if cheap_in is cheap_out else f'Im Inland ohne Barabhebung ist die {L(cheap_in)} am günstigsten, mit Reisen die {L(cheap_out)}.'))
    buchhaltung=f'''<div class="prose"><p>Die Karte ersetzt keinen Beleg. Für den Vorsteuerabzug brauchst du eine Rechnung, der Kartenbeleg oder die Monatsabrechnung reicht nicht; bis {kleinbetrag} brutto genügt eine Kleinbetragsrechnung mit Name des Verkäufers, Datum, Menge, Betrag und Steuersatz ({kb_norm}). Was die Karte leistet, ist die Zuordnung: Jede Zahlung steht mit Datum und Händler auf einer Abrechnung, die nur Betriebsausgaben enthält. Je mehr Buchungen, desto wichtiger wird der Weg der Daten in die Buchhaltung.</p>
<p>Hier trennen sich die Anbieter: {"Export in Dateiform nennen "+", ".join(sorted({c["anbieter"] for c in export_ja}))+" (N26, bunq und SumUp als CSV, die Amazon Business Cards als CSV der Umsatzsteuerdetails für Amazon-Umsätze, TARGOBANK per EBICS über das Business-Konto); einen direkten Abgleich mit Buchhaltungssoftware (DATEV, sevdesk, Sage und andere) bietet in unserem Vergleich nur bunq, Amex Business Platinum liefert eine Belegverarbeitung über GetMyInvoices mit. Die Filialbanken und Miles &amp; More nennen in ihren Unterlagen keinen Export, nur die Umsatzanzeige im Online-Banking; dort hilft der Kontoauszug des Geschäftskontos, auf dem die Kartenabrechnung als eine Buchung erscheint." if land=="de" else "Keine der vier Karten nennt in ihren Unterlagen einen Export in Buchhaltungsformate; N26 liefert Kontoauszüge und Kontoaktivität als PDF oder CSV, Amex PDF-Rechnungen der letzten 24 Monate in der App. Die Business-Karten von PayLife exportieren im Smart Data Portal als XLS oder CSV, card complete übergibt Umsatzdaten auf Wunsch an MobileXpense. Für die meisten Einzelunternehmer reicht der Kontoauszug des Geschäftskontos, auf dem die Kartenabrechnung als eine Buchung erscheint; die Einzelposten liefert die Monatsabrechnung."}</p>
<p>Zwei Regeln, die unabhängig von der Karte gelten: Die Jahresgebühr einer betrieblich genutzten Karte ist eine Betriebsausgabe. Und private Einkäufe mit der Firmenkarte sind bei einer GmbH eine Entnahme, die als Gehalt, Darlehen oder verdeckte Gewinnausschüttung zu behandeln ist; beim Einzelunternehmer eine Privatentnahme, die gebucht werden muss. Wer die Karte gemischt nutzt, verliert den Zeitvorteil wieder.</p></div>'''
    vers_rows=[c for c in alle if c.get('insText') or c.get('tier')]
    versicherung=f'''<div class="prose"><p>Reiseversicherungen hängen an der Karte, mit der die Reise bezahlt wird, und bei Firmenkarten oft an einer Bedingung mehr: {"Miles &amp; More Gold Business versichert laut Anbieter nur geschäftlich veranlasste Reisen, dafür bis zu fünf Angestellte mit; Amex Business Platinum deckt Rücktritt bis 6.000 €, Auslandskrankenschutz bis 120 Tage mit 10 % Selbstbehalt und Mietwagen-Kasko; Business Gold hat Auslandskranken- und Mietwagenschutz, aber keinen Reiserücktritt; die Amex Business Card nur Reisekomfort und Verkehrsmittel-Unfall. Bei N26 Business Go und Metal versichert Allianz Assistance Rücktritt, Auslandskranken und Gepäck, bei bunq Elite Business laut Drittquelle nur die Geschäftsführung. Deutsche Bank, Postbank, TARGOBANK Premium und Sparkasse nennen Versicherungspakete, deren Bedingungen wir nicht im Detail geprüft haben." if land=="de" else "Für die vier Karten in unserem Österreich-Vergleich liegen uns keine geprüften Versicherungsbedingungen vor; die Amex-Leistungsübersichten nennen Reiseleistungen, deren Summen wir noch nicht übernommen haben. Rechne vor einer Geschäftsreise nicht mit dem Schutz der Privatkarte: Private Policen schließen Dienstreisen teils aus, und Firmenkarten versichern oft nur den Karteninhaber, nicht die Mitarbeiter, die mit einer Zusatzkarte reisen."} Details stehen auf der jeweiligen Kartenseite und im Versicherungsblatt des Anbieters.</p></div>'''
    bsp_note=f'<p class="note">Kosten pro Jahr aus Jahresgebühr (ab dem 2. Jahr), Fremdwährungsentgelt und Bargeldentgelt der Karte. Profil „Mit Reisen“: 24.000 € Umsatz im Jahr, davon 20 % in Fremdwährung, sechs Abhebungen à 200 €. Mitarbeiterkarten, Kontogebühren, Zinsen und Versicherungen sind nicht enthalten; bei Debitkarten kommt die Kontoführung dazu (in der Jahresgebühr der N26-, bunq- und SumUp-Karten bereits enthalten).</p>'
    bsp=f'''<div class="prose"><p>Das Muster: Im Inland entscheidet allein die Jahresgebühr, und die ist bei den Debitkarten null oder die Kontogebühr. Mit Reisen dreht sich das Bild, weil die Filialbanken und Amex 1,5 bis 3,85 % auf Fremdwährung aufschlagen und Bargeld 2 bis 4 % kostet: Die {L(cheap_out)} ist dann am günstigsten, die {L(exp_out)} am teuersten. Ab etwa 5.000 € Fremdwährungsumsatz im Jahr ist das Fremdwährungsentgelt wichtiger als die Jahresgebühr.</p></div>'''
    checkliste='''<div class="prose"><ul>
<li><b>Rechtsform passt?</b> N26 Business und bunq Free nur für Personen unter eigenem Namen; GmbH und UG brauchen Banken, bunq ab Core, SumUp oder Amex.</li>
<li><b>Wer haftet?</b> Steht es nicht in den Bedingungen, schriftlich fragen. Für Geschäftsführer: Firmenhaftung oder Mithaftung mit Privatvermögen?</li>
<li><b>Mitarbeiterkarten:</b> Anzahl, Preis je Karte, eigene Limits je Karte, getrennte Abrechnung je Mitarbeiter.</li>
<li><b>Konto beim Anbieter nötig?</b> Wenn ja, zählt die Kontogebühr zu den Kartenkosten.</li>
<li><b>Zahlungsziel:</b> Für Liquidität zählt der Abstand zwischen Einkauf und Abbuchung, nicht der Werbesatz.</li>
<li><b>Export:</b> CSV reicht für die Steuerberatung, DATEV- oder API-Anbindung spart bei vielen Buchungen am meisten.</li>
<li><b>Fremdwährung und Bargeld:</b> Bei Reisen die größeren Posten, siehe Rechenbeispiel.</li>
<li><b>Versicherung:</b> Gilt sie für Mitarbeiter mit Zusatzkarte und für Dienstreisen? Steht im Versicherungsblatt, nicht auf der Produktseite.</li></ul></div>'''
    quellen=f'''<div class="prose"><ul><li>Jahresgebühren, Fremdwährungs- und Bargeldentgelte, Rückzahlung und Versicherungen: Preisverzeichnisse und Bedingungen der Anbieter, verlinkt auf jeder Kartenseite; die Tabellen werden beim Bauen dieser Seite aus den Kartendaten berechnet.</li>
<li>Mitarbeiterkarten, Haftung, Rechtsform, Zahlungsziel und Export: Produktseiten, Preisverzeichnisse, Antragsformulare und Bedingungen der Anbieter, geprüft am 19.10.2026. Wo ein Anbieter keine Angabe macht, steht „keine Angabe“.</li>
<li>Kleinbetragsrechnung bis {kleinbetrag}: {kb_norm}.</li></ul></div>'''
    secs=[('Brauchst du überhaupt eine Firmenkarte?',intro),
          ('Alle Firmenkarten im Überblick','<p class="note">Kredit- und Charge-Karten zuerst, dann Debitkarten, jeweils nach Jahresgebühr sortiert. „Mitarbeiterkarten“, „Haftung“ und „Zahlungsziel“ stammen aus den Anbieterunterlagen; „keine Angabe“ heißt, dass der Anbieter dazu öffentlich nichts sagt.</p>'+t_ueber+(weitere if weitere else '')+f'<p class="note"><a class="lnk" href="{P}{land}/kreditkarten/business/">Rangliste mit Bewertung: alle Business-Karten →</a></p>'),
          ('Was die Karten kosten: Gebühr, Fremdwährung, Bargeld, Export','<p class="note">Reiseversicherung: Einstufung aus unseren Kartendaten (Basis bis Premium), „keine Angabe“, wenn uns die Bedingungen des Anbieters nicht vorliegen.</p>'+t_kost),
          ('Haftung: wer für die Kartenumsätze geradesteht',haftung),
          ('Mitarbeiterkarten und Limits',mitarbeiter),
          ('Zahlungsziel und Abrechnung',zahlungsziel),
          ('Buchhaltung: Belege, Export, private Nutzung',buchhaltung),
          ('Versicherungen auf Geschäftsreisen',versicherung),
          ('Rechenbeispiel: Kosten pro Jahr bei zwei Nutzungsprofilen',bsp_note+t_bsp+bsp),
          ('Checkliste vor dem Antrag',checkliste),
          ('Quellen',quellen)]
    faq=[('Brauche ich als Einzelunternehmer eine Firmenkreditkarte?',f'Nein, Betriebsausgaben darfst du auch mit der Privatkarte bezahlen; steuerlich zählt die Rechnung. Eine eigene Karte spart Zeit, weil die Abrechnung nur Betriebsausgaben enthält. {"Für Selbstständige in Österreich reicht oft die Debitkarte zum Geschäftskonto oder die Amex Business Card mit kostenlosem erstem Jahr." if land=="at" else "Für Freiberufler reicht oft die kostenlose Debitkarte zum Geschäftskonto (N26, bunq, SumUp)."}'),
         ('Wer haftet bei einer Firmenkreditkarte?',f'Das regeln die Bedingungen, und zwar unterschiedlich: {"Bei Amex haftet der Karteninhaber persönlich, eine GmbH oder AG zusätzlich; bei N26 läuft das Konto auf die Person; die Oberbank regelt die Frage nicht. card complete stellt Business-Karten nur mit Firmenhaftung aus." if land=="at" else "Bei Postbank, Commerzbank und Amex haften Unternehmen und Karteninhaber gemeinsam, bei vielen anderen Karten steht keine Regel in den öffentlichen Unterlagen."} Einzelunternehmer haften ohnehin mit dem Privatvermögen; Geschäftsführer sollten vor dem Antrag klären, ob reine Firmenhaftung möglich ist.'),
         ('Welche Firmenkarte hat kostenlose Mitarbeiterkarten?',f'{"In Österreich keine dauerhaft: Amex gibt bis zu 99 Zusatzkarten im ersten Jahr kostenlos, danach 30 € (Business) bzw. 60 € (Gold) je Karte und Jahr. N26 und Oberbank bieten keine Mitarbeiterkarten." if land=="at" else "Amex Business Gold, Amazon Business Card und Amazon Business Prime Card: bis zu 99 Zusatzkarten ohne Aufpreis. Bei Business Platinum sind eine Platinum- und bis zu 98 Gold-Zusatzkarten inklusive. Die Filialbanken berechnen je Mitarbeiterkarte den vollen Jahrespreis."}'),
         ('Kann eine GmbH ein N26-Geschäftskonto mit Karte nutzen?','Nein. N26 Business läuft nur auf den Namen einer selbstständigen Person, nicht auf eine Firma; Mitarbeiterkarten gibt es nicht. '+("Für eine GmbH kommen in Österreich die Business-Karten von Amex, card complete oder PayLife mit Rahmenvereinbarung in Frage." if land=='at' else "Für GmbH und UG kommen bunq ab Core, SumUp, die Filialbanken oder Amex in Frage.")),
         ('Reicht der Kreditkartenbeleg für die Buchhaltung?',f'Nein. Für den Vorsteuerabzug brauchst du eine Rechnung; bis {kleinbetrag} brutto genügt eine Kleinbetragsrechnung ({kb_norm}). Kartenbeleg und Monatsabrechnung belegen nur die Zahlung, nicht den Umsatzsteuerausweis.'),
         ('Wie lange ist das Zahlungsziel bei Firmenkreditkarten?',f'{"Oberbank: Abbuchung zehn Arbeitstage nach der Umsatzübersicht, laut Anbieter bis zu sechs Wochen nach dem Einkauf; Amex Business Gold laut Produktseite bis zu 50 Tage. N26 bucht sofort ab." if land=="at" else "Von sofort (Commerzbank, Amex Business Card, alle Debitkarten) über 10 Tage nach Abrechnung (Deutsche Bank, Postbank) und 20 Tage (TARGOBANK, Amazon Business, Amex Gold auf Antrag) bis 28 Tage nach Abrechnung bei Amex Business Platinum, insgesamt bis zu 58 Tage."}'),
         ('Darf ich mit der Firmenkarte privat bezahlen?','Technisch ja, buchhalterisch ist es eine Privatentnahme, bei einer Gesellschaft eine Entnahme, die als Gehalt, Darlehen oder verdeckte Gewinnausschüttung behandelt werden muss. Wer gemischt nutzt, verliert den Zeitvorteil der getrennten Abrechnung.'),
         ('Gilt die Reiseversicherung der Firmenkarte auch für Mitarbeiter?',f'{"Miles & More Gold Business versichert bis zu fünf Angestellte mit, aber nur auf geschäftlich veranlassten Reisen; bei Amex gilt der Schutz für den Karteninhaber der jeweiligen Karte, mit der bezahlt wurde." if land=="de" else "Das steht im Versicherungsblatt der jeweiligen Karte; für die österreichischen Business-Karten liegen uns die Bedingungen noch nicht vor."} Grundsätzlich gilt der Schutz nur für Reisen, die mit der Karte bezahlt wurden, und oft nur für den Karteninhaber.')]
    art(land,'business',
      h1=f'Firmenkreditkarte in {N}: Haftung, Mitarbeiterkarten, Buchhaltung und Kosten',
      mt=f'Firmenkreditkarte {N}: Haftung, Mitarbeiterkarten, Kosten | Finvallo',
      desc=f'Firmenkreditkarte in {N}: Haftung, Mitarbeiterkarten, Zahlungsziel, Buchhaltungsexport und Jahreskosten aller Business-Karten laut Anbieter.',
      lede='Haftung, Mitarbeiterkarten, Zahlungsziel und Buchhaltungsexport entscheiden bei Firmenkarten mehr als die Jahresgebühr. Hier stehen die Angaben der Anbieter zu allen Business-Karten in unserem Vergleich.',
      kurz=kurz,secs=secs,faq=faq,
      related=['kostenlose-kreditkarte','fremdwaehrung','kartentypen'])
