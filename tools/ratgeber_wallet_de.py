# Ratgeber (nur DE): „Apple Pay und Google Pay in Deutschland“, Gegenstück zur AT-Seite (gleicher Slug, hreflang-Paar).
# Anbieter-Tabelle live aus daten/de/wallet.json (Feld wallet je Herausgeber, Stand je Eintrag). Aufruf aus ratgeber.build('de').
import html,json,os
E=lambda s: html.escape(str(s)) if s is not None else ''
SP=os.path.dirname(os.path.abspath(__file__))

def _tbl(head,rows):
    h=''.join(f'<th>{c}</th>' for c in head)
    b=''.join('<tr>'+''.join(f'<td>{c}</td>' for c in r)+'</tr>' for r in rows)
    return f'<div class="tbl wide"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'

def register(art,P,best,K,nprv,eur,KM):
    W=json.load(open(SP+'/daten/de/wallet.json'))['wallet']
    priv=[c for c in K if c['art']=='Privat']
    byp={}
    for c in priv: byp.setdefault(c['p'],[]).append(c)
    name={p:byp[p][0]['anbieter'] for p in byp}
    def L(slug,label=None):
        c=next(x for x in K if x['slug']==slug); return f'<a class="lnk" href="{P}de/kreditkarten/{slug}/">{E(label or c["titel"])}</a>'
    def Lp(p):
        f=os.path.join(SP,'..','public','de','kreditkarten','anbieter',p,'index.html')
        return f'<a class="lnk" href="{P}de/kreditkarten/anbieter/{p}/">{E(name[p])}</a>' if os.path.exists(f) else E(name[p])
    def jn(v): return 'ja' if v else ('nein' if v is False else 'unklar')
    def rank(p):
        w=W[p]; a,g=w.get('apple'),w.get('google')
        return 0 if (a and g) else 1 if (a or g) else 2 if (a is False) else 3
    order=sorted((p for p in byp if p in W),key=lambda p:(rank(p),name[p].lower()))
    n_both=len([p for p in order if rank(p)==0]); n_one=len([p for p in order if rank(p)==1]); n_none=len([p for p in order if rank(p)==2]); n_unk=len([p for p in order if rank(p)==3])
    stand=max(W[p].get('stand','') for p in order)
    rows=[]
    for p in order:
        w=W[p]
        karten=', '.join(L(c['slug'],c['name'] if c.get('name') and c['name']!='Karte' else c['titel']) for c in sorted(byp[p],key=lambda c:(c.get('fee') if c.get('fee') is not None else 1e9))[:4])+(f' und {len(byp[p])-4} weitere' if len(byp[p])>4 else '')
        rows.append((Lp(p),jn(w.get('apple')),jn(w.get('google')),E(w.get('app') or 'keine Angabe'),E(w.get('wear') or 'keine Angabe'),E(w.get('hinweis') or ''),karten))
    tbl=_tbl(['Herausgeber','Apple Pay','Google Pay','Einrichtung über','Wearables laut Anbieter','Hinweis','Karten im Vergleich'],rows)
    ext=lambda u,t: f'<a class="lnk" href="{u}" target="_blank" rel="noopener">{t}</a>'
    Q_APPLE=ext('https://support.apple.com/de-de/109516','Liste von Apple')
    Q_GOOGLE=ext('https://support.google.com/wallet/answer/12059326?hl=de&co=GENIE.CountryCode%3DDE','Liste von Google')
    Q_SPK=ext('https://www.sparkasse.de/pk/produkte/konten-und-karten/bezahlverfahren/mobiles-bezahlen.html','Sparkasse')
    Q_PB=ext('https://www.postbank.de/privatkunden/services/online-banking/apple-pay.html','Postbank')
    Q_AMEX=ext('https://www.americanexpress.com/de-de/amexcited/benefits/apple-und-google-pay-mit-amex-kreditkarte-12423','American Express')
    std='.'.join(reversed((stand or '2026-10-18').split('-')))
    art('de','apple-pay-google-pay',
      h1='Apple Pay und Google Pay in Deutschland: Welche Banken und Kreditkarten funktionieren',
      mt='Apple Pay und Google Pay in Deutschland: alle Banken und Kreditkarten 2026 | Finvallo',
      desc='Welche deutschen Banken und Kreditkarten Apple Pay und Google Pay unterstützen, welche nicht (Sparkasse, Amazon Visa, Postbank Visa), wie du die Karte einrichtest und was bei Verlust gilt.',
      lede='Die Listen von Apple und Google sind unvollständig, und die Ausnahmen stecken im Kleingedruckten: Sparkassen ohne Google Pay, Postbank nur mit Mastercard, Amazon Visa ohne Apple Pay. Hier stehen alle Herausgeber aus unserem Vergleich an einem Ort.',
      kurz=(f'Von den {len(order)} Kartenherausgebern in unserem Deutschland-Vergleich unterstützen {n_both} sowohl Apple Pay als auch Google Pay, bei {n_one} ist nur eines belegt, bei {n_none} keines, und bei {n_unk} fehlt jeder Beleg. '
            f'Die wichtigsten Ausnahmen: Die Sparkassen bieten Apple Pay, für Android aber nur ihre eigene App „Mobiles Bezahlen“ statt Google Pay; bei Volksbanken und TARGOBANK ist Google Pay nicht belegt; die {L("postbank-mastercard")} läuft nur als Mastercard, nicht als Visa; die {L("amazon-visa")} läuft nur mit Google Pay, Apple schließt sie aus; die {L("ikea-family-kreditkarte")} nennt keine Wallet. '
            f'Anders als in Österreich unterstützt American Express in Deutschland beide Dienste mit jeder Karte. Extra kosten tut das Bezahlen mit dem Handy bei keinem Anbieter.'),
      secs=[
       ('Warum die offiziellen Listen nicht reichen',f'''<div class="prose"><p>Apple führt eine {Q_APPLE} der teilnehmenden Banken je Land, Google eine {Q_GOOGLE} der unterstützten Zahlungsmethoden. Beide sind für Deutschland lückenhaft. In der Google-Liste fehlen Sparkassen und Volksbanken (die Google Pay tatsächlich nicht anbieten), aber auch American Express, Postbank, HypoVereinsbank, TARGOBANK, TF Bank und easybank, von denen mehrere Google Pay auf ihren eigenen Seiten erklären. In der Apple-Liste fehlen Herausgeber wie Barclays, Ikano und Magenta Pay, und Cobranding-Karten stehen nur in einer Fußnote: „Cobranding-Karten von Amazon und American Express können nicht für Apple Pay verwendet werden“, was American Express selbst für seine PAYBACK-Karte anders darstellt.</p>
<p>Wir haben deshalb für jeden Herausgeber in unserem Vergleich die eigene Hilfeseite gelesen und nur das übernommen, was dort oder in einer der beiden Listen steht. Wo ein Anbieter nichts sagt, schreiben wir „unklar“ statt zu raten. Das Prüfdatum steht bei jedem Herausgeber in unseren Daten, zuletzt am {std}.</p></div>'''),
       ('Alle Herausgeber im Vergleich: Apple Pay, Google Pay, Wearables','<p class="note">Sortiert: zuerst Herausgeber mit beiden Diensten, dann mit einem belegten, dann ohne, dann ohne Beleg. „Einrichtung über“ nennt die App, die der Anbieter vorsieht; bei den meisten geht es auch direkt in Apple Wallet oder Google Wallet. „Wearables“ nur, wenn der Anbieter sie selbst nennt.</p>'+tbl+
        f'''<div class="prose"><p>Vier Muster fallen auf. Erstens: Direkt- und Neobanken (DKB, ING, comdirect, Consorsbank, N26, C24, Revolut, Trade Republic, Wise) und die Gratis-Kreditkarten (TF Bank, Advanzia, Hanseatic, Deutschland-Kreditkarte) laufen auf beiden Plattformen, meist ohne Umweg über eine Bank-App. Zweitens: Die Verbünde gehen eigene Wege. Die {Q_SPK} bietet Apple Pay für alle Sparkassen, auf Android aber die eigene App „Mobiles Bezahlen“; Google Pay gibt es dort nicht. Die Volksbanken und Raiffeisenbanken nennen für Android nur die digitalen Karten in der VR Banking App. Drittens: Die Kartennetz-Regel. Die {Q_PB} hinterlegt nur Mastercard, keine Visa Card; easybank (ehemals Barclays Privatkunden) nur Visa, keine Mastercard; bei comdirect, Commerzbank und Volksbanken bleibt die girocard außen vor, bei 1822direkt und den Sparkassen geht sie mit Apple Pay. Viertens: Cobranding-Karten sind der Problemfall. Die Amazon Visa läuft mit Google Pay, ist aber von Apple Pay ausgeschlossen; die IKEA Family Kreditkarte nennt keine Wallet, und bei der Turkish Airlines Mastercard nennt Advanzia nur Google Pay und Garmin Pay.</p>
<p>Ein Unterschied zu Österreich: {Q_AMEX} unterstützt in Deutschland Apple Pay und Google Pay mit jeder Karte, ausdrücklich auch mit der PAYBACK Amex. Wer Membership Rewards sammelt und mit dem Handy zahlen will, kann das hier.</p></div>'''),
       ('So richtest du die Karte ein','''<div class="prose"><p><b>Apple Pay (iPhone, Apple Watch):</b> Wallet-App öffnen, Plus-Symbol, „Debit- oder Kreditkarte“, Karte abfotografieren oder Daten eintippen, Bestätigung der Bank abwarten. Die Bank prüft die Karte per SMS-Code, in ihrer App oder mit TAN; bei Hanseatic läuft die Freigabe über die Mobile App mit App-TAN oder SMS-TAN, bei der Postbank über BestSign, bei der Sparkasse über die App Sparkasse. Für die Apple Watch wiederholst du den Vorgang in der Watch-App unter „Wallet &amp; Apple Pay“.</p>
<p><b>Google Pay (Android, Wear OS):</b> Google Wallet-App öffnen, „Zu Wallet hinzufügen“, „Zahlungskarte“, Karte scannen, Bestätigung der Bank. Einige Banken wollen, dass du die Karte aus ihrer eigenen App heraus hinzufügst: Hanseatic und die Deutschland-Kreditkarte über die Hanseatic Bank Mobile App, Postbank und HypoVereinsbank über ihre Banking-App, TF Bank wahlweise über die eigene App. Google Pay braucht ein Android mit NFC, bei American Express ab Version 9; das Gerät darf nicht gerootet sein.</p>
<p><b>Wearables ohne Apple und Google:</b> Garmin Pay bei Magenta Pay, Hilton Honors und der Turkish Airlines Mastercard (beide Advanzia) sowie bei Wise; Fitbit Pay bei Wise; Samsung Wallet laut FAQ bei den Miles &amp; More Karten. Dort fügst du die Karte in der App des Uhrenherstellers hinzu, nicht in Google Wallet.</p>
<p>Was nicht geht: Die girocard lässt sich bei comdirect, Commerzbank und Volksbanken nicht hinterlegen, Prepaid-Karten je nach Anbieter nicht, und eine Karte, die noch nicht aktiviert ist, wird abgelehnt. Bei einem neuen Handy musst du alle Karten neu hinzufügen; die Token sind an das Gerät gebunden.</p></div>'''),
       ('Limits, PIN und was am Terminal anders ist','''<div class="prose"><p>Mit der Plastikkarte verlangt das Terminal in Deutschland beim kontaktlosen Zahlen ab 50 € die PIN, bei kleineren Beträgen nach mehreren Zahlungen hintereinander. Mit dem Handy entfällt das: Du bestätigst jede Zahlung mit Face ID, Fingerabdruck oder Code am Gerät, und diese Bestätigung ersetzt die PIN. Der Betrag ist dann nur durch das Limit deiner Karte begrenzt. An manchen Terminals musst du trotzdem die Karten-PIN eintippen; das ist eine Eigenheit des Terminals, kein Fehler der Wallet.</p>
<p>Online zahlst du mit Apple Pay in Safari und in Apps, mit Google Pay in Chrome und Android-Apps, jeweils ohne Kartennummer einzutippen. Die Freigabe nach den EU-Regeln zur starken Kundenauthentifizierung passiert am Gerät. Für Hotel- und Mietwagenkautionen bleibt es bei der physischen Kreditkarte; was dort gilt, steht im Ratgeber <a href="../mietwagen-kaution/">Mietwagen und Kaution</a>.</p>
<p>Entgelte ändern sich durch die Wallet nicht. Eine Zahlung in Fremdwährung kostet mit dem Handy genauso viel wie mit der Karte, bei den Filialbanken also 1,5 bis 2,35 % Auslandseinsatzentgelt, bei den Karten ohne Auslandsentgelt 0 %. Welche das sind, zeigt der Ratgeber <a href="../fremdwaehrung/">Gebühren im Ausland</a>. Bargeld am Automaten geht mit dem Handy nur an Geräten mit NFC-Leser und kostet dasselbe wie mit der Karte; die Entgelte stehen im Ratgeber <a href="../bargeld-abheben/">Geld abheben</a>.</p></div>'''),
       ('Sicherheit: Token statt Kartennummer, und was bei Verlust passiert','''<div class="prose"><p>Beim Hinzufügen wird nicht deine Kartennummer auf dem Handy gespeichert, sondern eine Gerätekontonummer, ein sogenannter Token. Der Händler sieht nur diesen Token, nie die echte Nummer. Der Token lässt sich einzeln sperren, ohne dass du die Plastikkarte ersetzen musst.</p>
<p>Geht das Handy verloren, sperrst du die Wallet aus der Ferne: bei Apple über „Wo ist?“ mit dem Modus „Verloren“, bei Android über „Mein Gerät finden“. Beides sperrt oder löscht die hinterlegten Karten, die Plastikkarte bleibt gültig. Zusätzlich kannst du bei deiner Bank den Token der Wallet sperren lassen, auch über den Sperr-Notruf 116 116. Ohne Entsperren des Geräts kann niemand zahlen, weil jede Zahlung Face ID, Fingerabdruck oder den Code verlangt.</p>
<p>Für die Haftung gelten dieselben Regeln wie bei der Karte: Nach § 675v BGB haftest du bei missbräuchlicher Nutzung vor der Sperrmeldung grundsätzlich nur bis 50 €, außer du hast grob fahrlässig gehandelt, etwa den Gerätecode weitergegeben. Nach der Sperrmeldung haftest du nicht mehr. Melde einen Verlust deshalb sofort.</p></div>'''),
       ('Welche Karte für wen','''<div class="prose"><ul>
<li><b>iPhone und Android im Haushalt, eine gemeinsame Karte:</b> jede Direktbank-Karte (DKB, ING, comdirect, Consorsbank, norisbank), Deutsche Bank, Commerzbank, HypoVereinsbank, Postbank Mastercard oder die Gratis-Kreditkarten von TF Bank, Advanzia und Hanseatic. Nicht Sparkasse oder Volksbank, wenn der Android-Nutzer Google Pay statt der Bank-App will.</li>
<li><b>Garmin am Handgelenk:</b> Magenta Pay, Wise, Hilton Honors und Turkish Airlines Mastercard (Advanzia).</li>
<li><b>Karte sofort nutzen, bevor die Plastikkarte da ist:</b> Instabank (laut Anbieter nach der Kontoverifizierung) und die Neobanken, die die Karte zuerst digital ausgeben.</li>
<li><b>Punkte sammeln und mit dem Handy zahlen:</b> American Express Gold oder Platinum, PAYBACK Amex, PAYBACK Visa und Miles &amp; More laufen auf beiden Plattformen. Die Amazon Visa nicht auf dem iPhone.</li></ul></div>'''),
       ('Quellen',f'''<div class="prose"><ul>
<li>{Q_APPLE} der teilnehmenden Banken in Europa (Abschnitt Deutschland, Stand 2. Oktober 2026) und {Q_GOOGLE} der unterstützten Zahlungsmethoden in Deutschland.</li>
<li>Hilfeseiten der Herausgeber zu Apple Pay und Google Pay, je Herausgeber in unseren Daten mit Adresse und Prüfdatum hinterlegt, unter anderem {Q_SPK}, {Q_PB}, {Q_AMEX}.</li>
<li>Haftung bei Kartenmissbrauch: § 675v BGB (Höchstbetrag 50 €).</li></ul></div>'''),
      ],
      faq=[
       ('Welche Banken in Deutschland unterstützen Apple Pay?','Fast alle: Sparkassen, Volksbanken und Raiffeisenbanken, Deutsche Bank, Commerzbank, Postbank (nur Mastercard), HypoVereinsbank, DKB, ING, comdirect, Consorsbank, norisbank, 1822direkt, TARGOBANK, OLB, American Express, Hanseatic, TF Bank, Advanzia, N26, C24, Revolut, Trade Republic, Wise und weitere. Nicht: die Amazon Visa (nur Google Pay); ohne Beleg: IKEA Family Kreditkarte und Turkish Airlines Mastercard.'),
       ('Welche Banken in Deutschland unterstützen Google Pay?','Deutsche Bank, Commerzbank, Postbank (Mastercard), HypoVereinsbank, DKB, ING, comdirect, Consorsbank, norisbank, 1822direkt (Visa), OLB, American Express, Hanseatic, Deutschland-Kreditkarte, TF Bank, Advanzia, N26, C24, Revolut, Trade Republic, Wise, Klarna, Vivid und weitere. Nicht: die Sparkassen (eigene App „Mobiles Bezahlen“). Ohne Beleg: Volksbanken, TARGOBANK, Bank Norwegian, Mercedes Credit Card, Trading 212.'),
       ('Funktioniert Google Pay mit der Sparkasse?','Nein. Die Sparkassen bieten Apple Pay für das iPhone, für Android aber nur ihre eigene App „Mobiles Bezahlen“, in der Sparkassen-Card und Kreditkarte hinterlegt werden. Google Pay oder Google Wallet nennt die Sparkasse nicht, und sie steht nicht in der Google-Liste.'),
       ('Kann ich die Postbank Visa Card in Apple Pay hinterlegen?','Nein. Die Postbank hinterlegt nur Mastercard-Karten (Classic, Gold, Platinum, Postbank Card mit Mastercard-Funktion) in Apple Pay und Google Pay. Eine Visa Card kann laut Postbank nicht verwendet werden.'),
       ('Funktioniert American Express mit Apple Pay und Google Pay in Deutschland?','Ja, laut American Express mit jeder Karte, einschließlich der PAYBACK American Express Karte; Google Pay ab Android 9. Apples Länderliste nennt in einer Fußnote Cobranding-Karten von American Express als ausgeschlossen; American Express selbst sagt das Gegenteil, deshalb gilt für uns die Anbieterseite.'),
       ('Warum geht die Amazon Visa nicht mit Apple Pay?','Apple schließt in seiner Liste für Deutschland Cobranding-Karten von Amazon ausdrücklich aus. Google Pay funktioniert laut unseren Kartendaten; die Google-Liste führt dafür den Herausgeber Santander Consumer Bank.'),
       ('Kostet das Bezahlen mit Apple Pay oder Google Pay extra?','Nein. Kein Anbieter in unserem Vergleich verlangt für die Wallet ein Entgelt. Auslandseinsatzentgelt und Bargeldentgelte sind dieselben wie bei der Plastikkarte.'),
       ('Was passiert bei Apple Pay, wenn ich mein Handy verliere?','Du sperrst das Gerät über „Wo ist?“ im Modus „Verloren“, damit sind die Karten in der Wallet gesperrt; die Plastikkarte bleibt gültig. Zusätzlich kannst du den Wallet-Token bei deiner Bank oder über den Sperr-Notruf 116 116 sperren lassen. Vor der Sperrmeldung haftest du nach § 675v BGB höchstens mit 50 €, danach gar nicht.'),
       ('Gibt es ein Limit beim Bezahlen mit dem Handy?','Kein eigenes Wallet-Limit. Weil du jede Zahlung am Gerät bestätigst, entfällt die PIN-Abfrage ab 50 €, die bei der Plastikkarte gilt. Es gilt nur das Limit deiner Karte.'),
       ('Kann ich die girocard in Apple Pay oder Google Pay hinterlegen?','Für Apple Pay ja bei Sparkassen und 1822direkt (Sparkassen-Card); bei comdirect, Commerzbank und Volksbanken nicht. In Google Pay funktioniert die girocard bei keinem Anbieter in unserem Vergleich; dort hinterlegst du die Mastercard oder Visa.'),
      ],
      related=['kostenlose-kreditkarte','visa-mastercard-amex','bargeld-abheben'])
