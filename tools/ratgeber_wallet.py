# Ratgeber (nur AT): „Apple Pay und Google Pay in Österreich“. Die Anbieter-Tabelle kommt live aus daten/at/anbieter.json
# (Feld wallet, Stand je Anbieter), die Kartenzahlen aus den Kartendaten. Keine andere Seite der Website zielt auf dieses Thema.
# Aufruf aus ratgeber.build('at'): register(art,P,best,K,nprv,eur,KM)
import html,json,os
E=lambda s: html.escape(str(s)) if s is not None else ''
SP=os.path.dirname(os.path.abspath(__file__))

def _tbl(head,rows):
    h=''.join(f'<th>{c}</th>' for c in head)
    b=''.join('<tr>'+''.join(f'<td>{c}</td>' for c in r)+'</tr>' for r in rows)
    return f'<div class="tbl wide"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'

def register(art,P,best,K,nprv,eur,KM):
    A=json.load(open(SP+'/daten/at/anbieter.json'))
    priv=[c for c in K if c['art']=='Privat']
    byp={}
    for c in priv: byp.setdefault(c['p'],[]).append(c)
    def L(slug,label=None):
        c=next(x for x in K if x['slug']==slug); return f'<a class="lnk" href="{P}at/kreditkarten/{slug}/">{E(label or c["titel"])}</a>'
    def Lp(p): return f'<a class="lnk" href="{P}at/kreditkarten/anbieter/{p}/">{E(A[p]["name"])}</a>' if os.path.exists(os.path.join(SP,'..','public','at','kreditkarten','anbieter',p,'index.html')) else E(A[p]['name'])
    def jn(v): return 'ja' if v else ('nein' if v is False else 'unklar')
    rows=[]; n_both=n_one=n_none=n_unk=0; stand=None
    order=sorted((p for p in byp if p in A and A[p].get('wallet')),key=lambda p:(0 if (A[p]['wallet'].get('apple') and A[p]['wallet'].get('google')) else 1 if (A[p]['wallet'].get('apple') or A[p]['wallet'].get('google')) else 2 if (A[p]['wallet'].get('apple') is False) else 3, A[p]['name'].lower()))
    for p in order:
        w=A[p]['wallet']; a,g=w.get('apple'),w.get('google')
        if a and g: n_both+=1
        elif a or g: n_one+=1
        elif a is False and g is False: n_none+=1
        else: n_unk+=1
        stand=max(stand or '',w.get('stand') or '')
        karten=', '.join(L(c['slug'],c['name'] if c.get('name') and c['name']!='Karte' else c['titel']) for c in sorted(byp[p],key=lambda c:(c.get('fee') if c.get('fee') is not None else 1e9))[:4])+(f' und {len(byp[p])-4} weitere' if len(byp[p])>4 else '')
        rows.append((Lp(p),jn(a),jn(g),E(w.get('app') or 'keine Angabe'),E(w.get('wear') or 'keine Angabe'),E(w.get('hinweis') or ''),karten))
    tbl=_tbl(['Anbieter','Apple Pay','Google Pay','Einrichtung über','Wearables laut Anbieter','Hinweis','Karten im Vergleich'],rows)
    ext=lambda u,t: f'<a class="lnk" href="{u}" target="_blank" rel="noopener">{t}</a>'
    Q_APPLE=ext('https://support.apple.com/de-at/109516','Liste von Apple')
    Q_GOOGLE=ext('https://support.google.com/wallet/answer/12059326?hl=de&co=GENIE.CountryCode%3DAT','Liste von Google')
    Q_BA=ext('https://www.bankaustria.at/google-pay.jsp','Bank Austria')
    Q_RAI=ext('https://www.raiffeisen.at/de/online-banking/mobile-payment/googlepay.html','Raiffeisen')
    Q_AMEX=ext('https://www.americanexpress.com/at/vorteile/service-sicherheit/zahlungsarten/kontaktlos','American Express Österreich')
    std='.'.join(reversed((stand or '2026-10-18').split('-')))
    art('at','apple-pay-google-pay',
      h1='Apple Pay und Google Pay in Österreich: Welche Banken und Kreditkarten funktionieren',
      mt='Apple Pay und Google Pay in Österreich: alle Banken und Kreditkarten 2026 | Finvallo',
      desc='Apple Pay und Google Pay in Österreich: welche Banken und Karten mitmachen, welche nicht (Amex, card complete), Einrichtung, Limits und Haftung.',
      lede='Die Listen von Apple und Google sind unvollständig, die Bankseiten verstreut. Hier stehen alle Herausgeber aus unserem Vergleich an einem Ort, mit Quelle und Prüfdatum.',
      kurz=(f'Von den {len(order)} Kartenherausgebern in unserem Österreich-Vergleich unterstützen {n_both} sowohl Apple Pay als auch Google Pay, {n_one} nur eines davon oder nur eines belegt, {n_none} keines, und bei {n_unk} fehlt ein aktueller Beleg. '
            f'Die großen Lücken: {Lp("american-express")} bietet in Österreich weder Apple Pay noch Google Pay an, die {L("santander-card")} ebenfalls nicht, und für card complete und Diners Club haben wir keinen aktuellen Beleg gefunden. '
            f'Bank Austria hat Google Pay im April 2025 nachgereicht, Raiffeisen und Oberbank inzwischen auch; damit sind alle großen Hausbanken auf beiden Plattformen. Extra kosten tut das Bezahlen mit dem Handy bei keinem Anbieter.'),
      secs=[
       ('Warum die offiziellen Listen nicht reichen',f'''<div class="prose"><p>Apple führt eine {Q_APPLE} der teilnehmenden Banken je Land, Google eine {Q_GOOGLE} der unterstützten Zahlungsmethoden. Beide sind für Österreich unvollständig. In der Google-Liste fehlen zum Beispiel Bank Austria, Oberbank, PayLife, easybank, Advanzia und TF Bank, obwohl alle sechs auf ihren eigenen Seiten Google Pay anbieten und erklären. In der Apple-Liste fehlen card complete und Diners Club, deren frühere Apple-Pay-Seite heute auf die Kartenübersicht weiterleitet. Wer nur die Listen liest, bekommt also ein falsches Bild.</p>
<p>Wir haben deshalb für jeden Herausgeber in unserem Vergleich die eigene Hilfeseite gelesen und nur das übernommen, was dort steht. Wo ein Anbieter nichts sagt und auch in keiner Liste steht, schreiben wir „unklar“ statt zu raten. Das Prüfdatum steht in den Daten jedes Anbieters, zuletzt am {std}.</p></div>'''),
       ('Alle Herausgeber im Vergleich: Apple Pay, Google Pay, Wearables','<p class="note">Sortiert: zuerst Anbieter mit beiden Diensten, dann mit einem, dann ohne, dann ohne Beleg. „Einrichtung über“ nennt die App, die der Anbieter für die Aktivierung vorsieht; bei den meisten geht es auch direkt in Apple Wallet oder Google Wallet. „Wearables“ nur, wenn der Anbieter sie selbst nennt.</p>'+tbl+
        f'''<div class="prose"><p>Drei Dinge fallen auf. Erstens: Die Neobanken (N26, Revolut, Wise, Trade Republic, Bitpanda) und die beiden Gratis-Kreditkarten von TF Bank und Advanzia waren von Anfang an auf beiden Plattformen; bei Advanzia kannst du die digitale Karte laut Anbieter sogar nutzen, bevor die Plastikkarte ankommt. Zweitens: Die Hausbanken haben Google Pay jahrelang verweigert und auf eigene Apps gesetzt (RaiPay bei Raiffeisen, Mobile Geldbörse bei Bank Austria, Oberbank Wallet), inzwischen aber nachgezogen; BAWAG und easybank im März 2023, {Q_BA} im April 2025, {Q_RAI} und Oberbank danach. Drittens: Die Lücken liegen bei den reinen Kartengesellschaften. {Q_AMEX} nennt auf seiner Seite nur das kontaktlose Zahlen mit der Plastikkarte, und bei card complete, Diners Club und den von card complete ausgegebenen bank99-Kreditkarten fehlt jeder aktuelle Hinweis.</p>
<p>Für die Wahl der Karte heißt das: Wer unbedingt mit dem Handy zahlen will, sollte American Express und die Santander Card streichen und bei card complete oder Diners Club vor dem Antrag nachfragen. Alle anderen Herausgeber in unserem Vergleich funktionieren mit dem iPhone; mit Android alle außer den genannten und, bis ein Beleg vorliegt, bunq.</p></div>'''),
       ('So richtest du die Karte ein','''<div class="prose"><p><b>Apple Pay (iPhone, Apple Watch):</b> Wallet-App öffnen, Plus-Symbol, „Debit- oder Kreditkarte“, Karte abfotografieren oder Daten eintippen, Bestätigung der Bank abwarten. Die Bank prüft die Karte per SMS-Code, über ihre App oder telefonisch; bei BAWAG und PayLife muss dafür eine Mobilnummer hinterlegt sein. Für die Apple Watch wiederholst du den Vorgang in der Watch-App unter „Wallet &amp; Apple Pay“; die Karte muss dort separat hinzugefügt werden.</p>
<p><b>Google Pay (Android, Wear OS):</b> Google Wallet-App öffnen, „Zu Wallet hinzufügen“, „Zahlungskarte“, Karte scannen, Bestätigung der Bank. Einige Banken wollen, dass du die Karte aus ihrer eigenen App heraus hinzufügst: Oberbank verlangt die Oberbank Wallet, Raiffeisen die Mein ELBA App bei Debitkarten (nicht bei Kreditkarten), Bank Austria die MobileBanking App. Google Pay braucht ein Android ab Version 11 bei Raiffeisen, ab Version 5 bei TF Bank; das Gerät darf nicht gerootet sein.</p>
<p><b>Wearables ohne Apple und Google:</b> Garmin Pay und Swatch Pay funktionieren bei Erste, Raiffeisen, Bank Direkt und Oberbank, Garmin Pay und Fitbit Pay bei Wise. Dort fügst du die Karte in der App des Uhrenherstellers hinzu, nicht in Google Wallet.</p>
<p>Was nicht geht: Prepaid-Karten lassen sich bei den meisten Anbietern nicht hinterlegen, und eine Karte, die noch nicht aktiviert ist, wird abgelehnt. Bei einem neuen Handy musst du alle Karten neu hinzufügen; die Token sind an das Gerät gebunden.</p></div>'''),
       ('Limits, PIN und was am Terminal anders ist','''<div class="prose"><p>Mit der Plastikkarte verlangt das Terminal in Österreich ab einem gewissen Betrag die PIN, bei kontaktlosen Zahlungen meist ab 50 € oder nach mehreren kleinen Zahlungen hintereinander. Mit dem Handy entfällt das: Du bestätigst jede Zahlung mit Face ID, Fingerabdruck oder Code am Gerät, und diese Bestätigung ersetzt die PIN. Der Betrag ist dann nur durch das Limit deiner Karte begrenzt. An manchen alten Terminals musst du trotzdem die Karten-PIN eintippen; das ist eine Eigenheit des Terminals, kein Fehler der Wallet.</p>
<p>Online zahlst du mit Apple Pay in Safari und in Apps, mit Google Pay in Chrome und Android-Apps, jeweils ohne Kartennummer einzutippen. Die Freigabe nach den EU-Regeln zur starken Kundenauthentifizierung passiert direkt am Gerät. Für Hotel- und Mietwagenkautionen bleibt es aber bei der physischen Kreditkarte; was dort gilt, steht im Ratgeber <a href="../mietwagen-kaution/">Mietwagen und Kaution</a>.</p>
<p>Gebühren ändern sich durch die Wallet nicht. Eine Zahlung in Fremdwährung kostet mit dem Handy genauso viel wie mit der Karte, bei den Hausbanken also 1,35 bis 3,15 %, bei den Karten ohne Auslandsgebühr 0 %. Welche das sind, zeigt der Ratgeber <a href="../fremdwaehrung/">Gebühren im Ausland</a>. Bargeld am Automaten geht mit dem Handy nur an Geräten mit NFC-Leser, und es kostet dasselbe wie mit der Karte.</p></div>'''),
       ('Sicherheit: Token statt Kartennummer, und was bei Verlust passiert','''<div class="prose"><p>Beim Hinzufügen wird nicht deine Kartennummer auf dem Handy gespeichert, sondern eine Gerätekontonummer, ein sogenannter Token. Der Händler sieht nur diesen Token, nie die echte Nummer. Ein gestohlenes Terminal-Protokoll nützt Betrügern deshalb nichts, und der Token lässt sich einzeln sperren, ohne dass du die Plastikkarte ersetzen musst.</p>
<p>Geht das Handy verloren, sperrst du die Wallet aus der Ferne: bei Apple über „Wo ist?“ mit dem Modus „Verloren“, bei Android über „Mein Gerät finden“. Beides sperrt oder löscht die hinterlegten Karten, die Plastikkarte bleibt gültig. Zusätzlich kannst du bei deiner Bank den Token der Wallet sperren lassen, ohne die Karte selbst zu sperren. Ohne Entsperren des Geräts kann niemand zahlen, weil jede Zahlung Face ID, Fingerabdruck oder den Code verlangt.</p>
<p>Für die Haftung gelten dieselben Regeln wie bei der Karte: Nach dem Zahlungsdienstegesetz haftest du bei missbräuchlicher Nutzung grundsätzlich nur bis 50 €, außer du hast grob fahrlässig gehandelt, etwa den Gerätecode weitergegeben. Melde einen Verlust deshalb sofort, dann endet auch dieser Betrag.</p></div>'''),
       ('Welche Karte für wen','''<div class="prose"><ul>
<li><b>iPhone und Android im Haushalt, eine gemeinsame Karte:</b> jede Hausbank-Karte außer card complete und Diners Club, oder TF Bank und Advanzia ohne Jahresgebühr.</li>
<li><b>Garmin oder Swatch am Handgelenk:</b> Erste Bank und Sparkassen, Raiffeisen, Bank Direkt, Oberbank; mit der Wise-Karte auch Fitbit.</li>
<li><b>Karte sofort nutzen, bevor die Plastikkarte da ist:</b> Advanzia (laut Anbieter nach der Identitätsprüfung) und die Neobanken, die die Karte zuerst digital ausgeben.</li>
<li><b>Membership Rewards sammeln und trotzdem mit dem Handy zahlen:</b> geht in Österreich nicht; American Express unterstützt hier weder Apple Pay noch Google Pay. Wer beides will, nimmt eine zweite Karte fürs Handy.</li></ul></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>{Q_APPLE} der teilnehmenden Banken in Europa (Abschnitt Österreich) und {Q_GOOGLE} der unterstützten Zahlungsmethoden in Österreich.</li>
<li>Hilfeseiten der Anbieter zu Apple Pay und Google Pay, je Anbieter in unseren Daten mit Adresse und Prüfdatum hinterlegt, unter anderem {Q_BA}, {Q_RAI}, {Q_AMEX}.</li>
<li>Haftung bei Kartenmissbrauch: Zahlungsdienstegesetz 2018, § 68 (Höchstbetrag 50 €).</li></ul></div>'''),
      ],
      faq=[
       ('Welche Banken in Österreich unterstützen Apple Pay?','Alle großen Hausbanken: Erste Bank und Sparkassen, Raiffeisen, Bank Austria, BAWAG, easybank, Oberbank, bank99 (Debitkarte), dazu PayLife, Bank Direkt, TF Bank, Advanzia, N26, Revolut, Wise, Trade Republic, Bitpanda und bunq. Nicht dabei: American Express Österreich und die Santander Card; für card complete und Diners Club fehlt ein aktueller Beleg.'),
       ('Welche Banken in Österreich unterstützen Google Pay?','Erste Bank und Sparkassen, Raiffeisen, Bank Direkt, Bank Austria (seit April 2025), BAWAG und easybank (seit März 2023), Oberbank, PayLife, TF Bank, Advanzia, N26, Revolut, Wise, Trade Republic und Bitpanda. Nicht: American Express und Santander. Unklar: card complete, Diners Club, bunq und die bank99-Kreditkarten.'),
       ('Funktioniert American Express mit Apple Pay in Österreich?','Nein. American Express Österreich nennt auf seiner Seite nur das kontaktlose Zahlen mit der Plastikkarte und steht weder in der Apple- noch in der Google-Liste für Österreich. In Deutschland ist das anders; die österreichischen Karten sind davon ausgenommen.'),
       ('Kostet das Bezahlen mit Apple Pay oder Google Pay extra?','Nein. Kein Anbieter in unserem Vergleich verlangt für die Wallet eine Gebühr. Fremdwährungsentgelt und Bargeldgebühren sind dieselben wie bei der Plastikkarte.'),
       ('Brauche ich für Google Pay die App meiner Bank?','Bei Oberbank ja (Oberbank Wallet), bei Bank Austria die MobileBanking App, bei Raiffeisen die Mein ELBA App nur für Debitkarten. Bei TF Bank, Advanzia, PayLife, BAWAG, easybank und den Neobanken kannst du die Karte direkt in Google Wallet hinzufügen.'),
       ('Was passiert bei Apple Pay, wenn ich mein Handy verliere?','Du sperrst das Gerät über „Wo ist?“ im Modus „Verloren“, damit sind die Karten in der Wallet gesperrt. Die Plastikkarte bleibt gültig. Zahlen kann ohne Face ID, Fingerabdruck oder Gerätecode niemand. Zusätzlich kannst du bei deiner Bank den Wallet-Token sperren lassen.'),
       ('Gibt es ein Limit beim Bezahlen mit dem Handy?','Kein eigenes Wallet-Limit. Weil du jede Zahlung am Gerät bestätigst, entfällt die PIN-Abfrage ab 50 €, die bei der Plastikkarte gilt. Es gilt nur das Limit deiner Karte.'),
       ('Kann ich Garmin Pay oder Fitbit Pay in Österreich nutzen?','Garmin Pay und Swatch Pay bei Erste Bank und Sparkassen, Raiffeisen, Bank Direkt und Oberbank; Garmin Pay und Fitbit Pay mit der Wise-Karte. Die Karte wird in der App des Uhrenherstellers hinzugefügt.'),
       ('Funktioniert Google Pay mit der Bank Austria?','Ja, seit April 2025 für BankCard, MegaCard und die Bank Austria Kreditkarte. Die Einrichtung läuft über die MobileBanking App, auch für Wear-OS-Uhren.'),
       ('Kann ich Prepaid-Karten in Apple Pay oder Google Pay hinterlegen?','Meist nicht. Prepaid-Produkte lassen sich in der Regel nicht hinzufügen; ob es bei deiner Karte geht, steht beim Anbieter. Debitkarten der Neobanken sind die Alternative ohne Bonitätsprüfung.'),
      ],
      related=['kostenlose-kreditkarte','visa-mastercard-amex','fremdwaehrung'])
