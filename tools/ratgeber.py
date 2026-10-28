# Ratgeber-Artikel für AT und DE (gleiche Slugs, hreflang), Daten live aus den Kartendaten.
import json,re,os,html,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','public')+'/'
STAND='2026-10-12'; STAND_DE='12.10.2026'
E=lambda s: html.escape(str(s)) if s is not None else ''
LAND={'at':dict(name='Österreich',lang='de-AT',loc='de_AT',ab='beheben',abn='Behebung',auskunft='KSV1870',konto='Girokonto'),
      'de':dict(name='Deutschland',lang='de-DE',loc='de_DE',ab='abheben',abn='Abhebung',auskunft='Schufa',konto='Girokonto')}
def eur(x):
    s=f'{x:,.2f}'.replace(',','X').replace('.',',').replace('X','.'); return s[:-3] if s.endswith(',00') else s
def de1(x): return f'{x:.1f}'.replace('.',',')
def pct(x):
    s=f'{x:.2f}'.replace('.',','); return (s[:-3] if s.endswith(',00') else s)+' %'
TIERN={0:'keine',1:'Basis-Reiseschutz',2:'mit Reiserücktritt',3:'umfassend',4:'Premium'}
# ---------- Daten ----------
def cards(land):
    import karten
    if not hasattr(cards,'D'):
        cards.D=karten.prepare()
        global STAND, STAND_DE   # Stand = jüngstes Prüfdatum der Kartendaten
        STAND=max(karten.LANDS[l]['stand'] for l in karten.LANDS); STAND_DE='.'.join(reversed(STAND.split('-')))
    out=[]
    for c in cards.D[land][0]:
        out.append(dict(slug=c['slug'],titel=c['titel'],url=f'{land}/kreditkarten/{c["slug"]}/',fee=c.get('fee'),fx=c.get('fx'),fxText=karten.fxT(c),cashText=karten.cashT(c),
          stars=c.get('stars'),tier=c.get('tier'),typ=c['typ'],netz=c.get('netz') or '',giro=c.get('giro'),auto=c.get('auto'),art=c['art'],
          lg=c.get('lgText') if c['ex'].get('lg') else None,cb=c.get('earnText') or (c.get('cbText') if c['ex'].get('cb') else None),ml=c['ex'].get('ml'),klasse=c['klasse'],bestand=c.get('nurfuer'),cash=c.get('cash'),effz=c.get('effz')))
    return [c for c in out if c['art']=='Privat' and not c.get('bestand')]
def rated(L): return sorted([c for c in L if c.get('stars') is not None],key=lambda c:(-c['stars'],c['fee'] if c['fee'] is not None else 1e9))
def link(c,P): return f'<a class="lnk" href="{P}{c["url"]}">{E(c["titel"])}</a>'
def mietwagen(land):
    """Geprüfte Mietwagen-Profile je Karte (tools/daten/mietwagen.json), dieselbe Quelle wie die Kartenseiten."""
    import karten
    return {k.split('/',1)[1]:v for k,v in karten.MW.items() if k.startswith(land+'/')}
MWART={'kasko':'Kasko','sb':'Selbstbeteiligungsschutz','haft':'Zusatzhaftpflicht'}
def table(rows,cols,P):
    h=''.join(f'<th>{c[0]}</th>' for c in cols)
    b=''.join('<tr>'+''.join(f'<td>{f(c,P)}</td>' for _,f in cols)+'</tr>' for c in rows)
    return f'<div class="tbl wide"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'
COL=dict(karte=('Karte',lambda c,P:link(c,P)),
         fee=('Jahresgebühr',lambda c,P:'kostenlos' if c['fee']==0 else (f'{eur(c["fee"])} €' if c['fee'] is not None else '-')),
         fx=('Zahlung Ausland',lambda c,P:E(c['fxText'] if c['fx'] not in (0,None) else ('0 %' if c['fx']==0 else '-'))),
         cash=('Bargeld',lambda c,P:E(c['cashText'] or '-')),
         ins=('Reiseversicherung',lambda c,P:TIERN.get(c['tier'],'-') if c['tier'] is not None else '-'),
         stars=('Bewertung',lambda c,P:f'{de1(c["stars"])} ★' if c.get('stars') is not None else '-'),
         netz=('Netz',lambda c,P:E(c['netz'])),typ=('Typ',lambda c,P:E(c['typ'])),
         lg=('Lounge',lambda c,P:E((c['lg'] or '')[:90])),cb=('Sammeln',lambda c,P:E((c['cb'] or '')[:90])))
# ---------- Seite ----------
# Datum je Ratgeber (wie Frontmatter): published, updated (beim nächsten inhaltlichen Edit pflegen),
# optional corrections=[dict(date='JJJJ-MM-TT', note='…')] → Abschnitt „Korrekturen“ am Ende des Artikels.
DATES={
    ('at','business'): dict(published='2026-10-11', updated='2026-10-19'),
    ('at','fremdwaehrung'): dict(published='2026-10-11', updated='2026-10-15'),
    ('at','kartentypen'): dict(published='2026-10-11', updated='2026-10-28'),
    ('at','kostenlose-kreditkarte'): dict(published='2026-10-12', updated='2026-10-19'),
    ('at','kreditkarte-beantragen'): dict(published='2026-10-12', updated='2026-10-12'),
    ('at','lounges'): dict(published='2026-10-11', updated='2026-10-11'),
    ('at','mietwagen-kaution'): dict(published='2026-10-12', updated='2026-10-14'),
    ('at','ohne-bonitaetspruefung'): dict(published='2026-10-12', updated='2026-10-12'),
    ('at','punkte-sammeln-at'): dict(published='2026-10-12', updated='2026-10-19'),
    ('at','reiseversicherung'): dict(published='2026-10-11', updated='2026-10-18'),
    ('at','flugverspaetung-gepaeck'): dict(published='2026-10-18', updated='2026-10-18'),
    ('at','bargeld-beheben'): dict(published='2026-10-18', updated='2026-10-18'),
    ('at','kreditkarte-studenten'): dict(published='2026-10-18', updated='2026-10-18'),
    ('at','apple-pay-google-pay'): dict(published='2026-10-18', updated='2026-10-18'),
    ('at','teilzahlung'): dict(published='2026-10-11', updated='2026-10-19'),
    ('at','visa-mastercard-amex'): dict(published='2026-10-12', updated='2026-10-12'),
    ('de','bargeld-abheben'): dict(published='2026-10-18', updated='2026-10-18'),
    ('de','kreditkarte-studenten'): dict(published='2026-10-18', updated='2026-10-18'),
    ('de','apple-pay-google-pay'): dict(published='2026-10-18', updated='2026-10-18'),
    ('de','business'): dict(published='2026-10-11', updated='2026-10-19'),
    ('de','fremdwaehrung'): dict(published='2026-10-12', updated='2026-10-12'),
    ('de','kartentypen'): dict(published='2026-10-11', updated='2026-10-28'),
    ('de','kostenlose-kreditkarte'): dict(published='2026-10-12', updated='2026-10-19'),
    ('de','kreditkarte-beantragen'): dict(published='2026-10-12', updated='2026-10-12'),
    ('de','lounges'): dict(published='2026-10-12', updated='2026-10-12'),
    ('de','mietwagen-kaution'): dict(published='2026-10-12', updated='2026-10-14'),
    ('de','ohne-bonitaetspruefung'): dict(published='2026-10-12', updated='2026-10-12'),
    ('de','punkte-sammeln-de'): dict(published='2026-10-12', updated='2026-10-19'),
    ('de','reiseversicherung'): dict(published='2026-10-11', updated='2026-10-18'),
    ('de','teilzahlung'): dict(published='2026-10-11', updated='2026-10-19'),
    ('de','visa-mastercard-amex'): dict(published='2026-10-12', updated='2026-10-12'),
}
def dates(): return DATES
ARTS={}   # (land,slug) -> dict
def art(land,slug,**kw): ARTS[(land,slug)]=kw
def head(land,slug,a,P,ld,alt):
    css=open(R+'index.html').read(); v=re.search(r'site\.css\?v=([a-z0-9]+)',css).group(1); fv=re.search(r'favicon\.svg\?v=([a-z0-9]+)',css).group(1)
    url=f'https://finvallo.com/{land}/ratgeber/{slug}/'
    return f'''<!doctype html>
<html lang="{LAND[land]["lang"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(a["mt"])}</title>
<meta name="description" content="{E(a["desc"])}">
<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1">
<link rel="canonical" href="{url}">{alt}
<meta property="og:type" content="article">
<meta property="og:site_name" content="Finvallo">
<meta property="og:locale" content="{LAND[land]["loc"]}">
<meta property="og:title" content="{E(a["mt"])}">
<meta property="og:description" content="{E(a["desc"])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://finvallo.com/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0f1720">
<meta name='impact-site-verification' value='395412e1-70ac-412c-9ce9-5e53d7b5e5ef'>
<meta name="author" content="Finvallo-Redaktion">
<meta property="article:modified_time" content="{(DATES.get((land,slug)) or {}).get('updated') or STAND}">
<link rel="icon" href="{P}assets/favicon.svg?v={fv}" type="image/svg+xml">
<link rel="preload" href="{P}assets/fonts/figtree-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{P}assets/site.css?v={v}">
<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False)}</script>
</head>
<body>
'''
def footer(land,P):
    L=LAND[land]['name']
    return f'''<footer>
<span><b>finvallo</b> · Unabhängiger Finanzvergleich für {L}</span>
<span>Stand {STAND_DE} · Bewertung unabhängig von Provisionen, keine bezahlten Platzierungen · Mit * markierte Links sind Affiliate-Links.</span>
<span>Keine Finanzberatung. Konditionen vor Abschluss beim Anbieter prüfen.</span>
<nav aria-label="Fußzeile"><a href="{P}{land}/kreditkarten/methodik/">So bewerten wir</a><a href="{P}so-verdienen-wir-geld/">So verdienen wir Geld</a><a href="{P}ueber-uns/">Über Finvallo</a><a href="{P}impressum/">Impressum</a><a href="{P}datenschutz/">Datenschutz</a><a href="{P}llms.txt">Für KI-Assistenten</a></nav>
</footer>
</div>
</body>
</html>
'''
def render(land,slug):
    import header as H
    a=ARTS[(land,slug)]; P='../../../'; rel=f'{land}/ratgeber/{slug}/'; url='https://finvallo.com/'+rel
    other='de' if land=='at' else 'at'
    oslug=a.get('pair',slug)
    alt=''
    if (other,oslug) in ARTS or os.path.exists(R+f'{other}/ratgeber/{oslug}/index.html'):
        mine=f'<link rel="alternate" hreflang="{LAND[land]["lang"]}" href="{url}">'
        theirs=f'<link rel="alternate" hreflang="{LAND[other]["lang"]}" href="https://finvallo.com/{other}/ratgeber/{oslug}/">'
        alt='\n'+(mine+theirs if land=='de' else theirs+mine).replace('><','><')
    secs=''.join(f'<h2>{h}</h2>{b}' for h,b in a['secs'])
    fq=a.get('faq',[])
    rel_=''.join(f'<a class="catcard" href="../{s}/"><b>{E(ARTS[(land,s)]["h1"])}</b><small>Lesen →</small></a>' for s in a.get('related',[]) if (land,s) in ARTS)
    ld={"@context":"https://schema.org","@graph":[
        {"@type":"Organization","@id":"https://finvallo.com/#org","name":"Finvallo","url":"https://finvallo.com/","logo":"https://finvallo.com/assets/logo.svg"},
        {"@type":"WebSite","@id":"https://finvallo.com/#website","name":"Finvallo","url":"https://finvallo.com/","inLanguage":"de","publisher":{"@id":"https://finvallo.com/#org"}},
        {"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":LAND[land]['name'],"item":f"https://finvallo.com/{land}/"},{"@type":"ListItem","position":2,"name":"Ratgeber","item":f"https://finvallo.com/{land}/ratgeber/"},{"@type":"ListItem","position":3,"name":a['h1'],"item":url}]},
        {"@type":"Article","@id":url+"#article","headline":a['h1'],"description":a['desc'],"inLanguage":LAND[land]['lang'],"datePublished":a.get('pub',STAND),"dateModified":STAND,
         "author":{"@id":"https://finvallo.com/#org"},"publisher":{"@id":"https://finvallo.com/#org"},"mainEntityOfPage":url,"about":a.get('about') or f"Kreditkarten in {LAND[land]['name']}","image":"https://finvallo.com/assets/og.png"}]}
    if fq: ld['@graph'].append({"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":re.sub(r'<[^>]+>','',x)}} for q,x in fq]})
    land_div=(f'<div class="land" role="group" aria-label="Land wählen"><a href="{P}at/ratgeber/{oslug if land=="de" else slug}/" hreflang="de-AT" aria-current="{"true" if land=="at" else "false"}" title="Österreich">AT</a>'
              f'<a href="{P}de/ratgeber/{oslug if land=="at" else slug}/" hreflang="de-DE" aria-current="{"true" if land=="de" else "false"}" title="Deutschland">DE</a></div>') if alt else None
    hdr=H.build(rel,P,land_div or H.land_default(P))
    body=f'''{hdr}
<div class="wrap"><main id="app">
<div class="crumb"><span><a href="../">Ratgeber</a> › {E(a["h1"])}</span><span>Stand {STAND_DE}</span></div><h1>{E(a["h1"])}</h1><p class="lede">{a["lede"]}</p>
<div class="info"><span class="ic">i</span><div><p style="margin:0"><b>Kurz gesagt:</b> {a["kurz"]}</p></div></div>
{secs}
{"<h2>Fragen und Antworten</h2><div class='faq'>"+"".join(f"<details><summary>{E(q)}</summary><p>{x}</p></details>" for q,x in fq)+"</div>" if fq else ""}
{f'<h2>Weitere Beiträge</h2><div class="catgrid">{rel_}</div>' if rel_ else ""}
<p class="src" style="margin-top:18px">Zahlen aus dem Finvallo-Vergleich für {LAND[land]["name"]}, Stand {STAND_DE}. Konditionen ändern sich, prüfe sie vor dem Abschluss beim Anbieter.</p>
</main>
{footer(land,P)}'''
    os.makedirs(R+rel,exist_ok=True); open(R+rel+'index.html','w').write(head(land,slug,a,P,ld,alt)+body)

# ---------- Inhalte ----------
def fmtlist(L): return ', '.join(L[:-1])+' und '+L[-1] if len(L)>1 else (L[0] if L else '')
def build(land):
    C=cards(land); RC=rated(C); L=LAND[land]; N=L['name']; AB=L['ab']; AUS=L['auskunft']; P='../../../'
    credit=[c for c in RC if c['typ'] in ('Kreditkarte','Charge')]
    free=[c for c in credit if c['fee']==0]
    free_ins=[c for c in free if (c['tier'] or 0)>=2]
    deb=[c for c in RC if c['typ'] in ('Debit','Prepaid')]
    deb_free=[c for c in deb if c['fee']==0 and not c['giro']] or [c for c in deb if c['fee']==0]
    best=f'../../kreditkarten/bestenlisten/'
    # A) kostenlose Kreditkarte: Texte und Tabellen in ratgeber_kostenlos.py
    import karten, ratgeber_kostenlos
    ratgeber_kostenlos.register(land,art,P,best,cards.D[land][0],karten.card_count(land,'private'),eur,karten,de1,pct)
    import ratgeber_teilzahlung; ratgeber_teilzahlung.register(land,art,P,best,cards.D[land][0],karten.card_count(land,'private'),eur,karten,de1,pct)
    import ratgeber_kartentypen; ratgeber_kartentypen.register(land,art,P,best,RC,eur,de1,pct)
    import ratgeber_business; ratgeber_business.register(land,art,P,best,cards.D[land][0],karten.card_count(land,'private'),eur,karten,de1,pct)
    # B) Kreditkarte beantragen
    # AT und DE bekommen eigene Fassungen (Begriffe, Anbieter, Rechtslage), damit die Texte nicht als Duplikate gelten.
    kk=[c for c in credit if not c['giro']][:6]   # Karten ohne Girokonto-Pflicht
    if land=='at':
      art('at','kreditkarte-beantragen',
      h1='Kreditkarte beantragen in Österreich: so geht es Schritt für Schritt',
      mt='Kreditkarte beantragen in Österreich: Ablauf | Finvallo',
      desc='Kreditkarte in Österreich beantragen: Unterlagen, Video-Ident, KSV1870-Abfrage, Dauer und die häufigsten Gründe für eine Ablehnung. Mit Karten aus unserem Vergleich.',
      lede='Hausbank oder freier Kartenanbieter, Charge- oder Teilzahlungskarte: was du für den Antrag in Österreich brauchst und wo es hakt.',
      kurz='In Österreich bekommst du eine Kreditkarte entweder über deine Hausbank zum Girokonto oder direkt bei einem Kartenanbieter wie card complete, PayLife, American Express, Diners Club, Advanzia oder TF Bank. Du stellst den Antrag online, weist dich per Video-Ident oder in der Filiale aus, die Bank fragt den KSV1870 ab und legt den Rahmen fest. Bei Direktanbietern kommt die Zusage oft in Minuten, die Karte etwa eine Woche später mit der Post.',
      secs=[('Das brauchst du in Österreich','<div class="prose"><ul><li><b>Hauptwohnsitz in Österreich</b> und Volljährigkeit. Unter 18 gibt es nur Debit- oder Prepaid-Karten.</li><li><b>Einen gültigen Lichtbildausweis:</b> Reisepass oder Personalausweis, beim Video-Ident meist auch der Führerschein.</li><li><b>Ein Girokonto mit IBAN.</b> Die Karten von Bank Austria, Erste Bank, Raiffeisen oder BAWAG gibt es nur zum eigenen Konto. card complete, PayLife, American Express, Diners Club, Advanzia und TF Bank buchen von jedem SEPA-Konto ab.</li><li><b>Einkommensnachweis:</b> die letzten Lohnzettel, der Pensionsbescheid oder bei Selbstständigen der Einkommensteuerbescheid. Viele Anbieter fragen nur nach, manche verlangen den Upload.</li><li><b>Ein Smartphone mit Kamera</b> für Video-Ident, App und das Freigeben von Online-Zahlungen.</li></ul><p>Die Ausweispflicht ergibt sich aus dem Finanzmarkt-Geldwäschegesetz. Ohne Identifizierung bekommst du keine Karte mit Kreditrahmen, auch keine Charge-Karte.</p></div>'),
            ('Hausbank oder freier Anbieter: zwei Wege',f'<div class="prose"><p>In Österreich ist die Charge-Karte der Normalfall: Die Bank sammelt deine Umsätze und zieht sie einmal im Monat vom Konto ein. Bei Erste Bank und Sparkasse beantragst du sie in George, bei Raiffeisen in Mein ELBA, bei Bank Austria und BAWAG im Online-Banking. Die Bank kennt deine Kontobewegungen, deshalb geht die Prüfung schnell. Dafür zahlst du fast immer eine Jahresgebühr und im Ausland ein Bearbeitungsentgelt.</p><p>Der zweite Weg führt zu einem Anbieter ohne Konto-Pflicht. card complete gibt Visa und Mastercard aus, PayLife gehört zur BAWAG-Gruppe, dazu kommen American Express, Diners Club sowie Advanzia und TF Bank mit gebührenfreien Teilzahlungskarten. Du musst dein Konto nicht wechseln und kannst die Karte unabhängig von der Hausbank kündigen.</p></div>'+(table(kk,[COL['karte'],COL['typ'],COL['fee'],COL['fx'],COL['stars']],P)+f'<p class="note">Die am besten bewerteten Kredit- und Charge-Karten ohne Girokonto-Pflicht aus unserem Österreich-Vergleich. Die Abrechnung läuft über dein bestehendes Konto. <a class="lnk" href="{best}">Alle Bestenlisten →</a></p>' if kk else '')),
            ('So läuft der Antrag ab',f'''<div class="steps"><div class="step"><span class="no">1</span><div><b>Karte auswählen</b><p>Achte auf Jahresgebühr, Bearbeitungsentgelt im Ausland, Kosten fürs Beheben und den Versicherungsumfang. Unsere <a href="{best}">Bestenlisten</a> sortieren danach.</p></div></div>
<div class="step"><span class="no">2</span><div><b>Online-Antrag ausfüllen</b><p>Du gibst Name, Meldeadresse, Arbeitgeber, Nettoeinkommen und laufende Verpflichtungen wie Miete oder Kredite an. Falsche Angaben können später zur Kündigung führen.</p></div></div>
<div class="step"><span class="no">3</span><div><b>Identität nachweisen</b><p>Meist per Video-Ident mit dem Handy, bei Hausbanken auch in der Filiale. Wer schon Kunde ist, ist oft bereits identifiziert und überspringt den Schritt.</p></div></div>
<div class="step"><span class="no">4</span><div><b>Bonitätsprüfung</b><p>Die Bank fragt den KSV1870 ab, manche zusätzlich CRIF. Bei Karten mit Teilzahlung ist die Prüfung nach <a class="lnk" href="https://www.jusline.at/gesetz/vkrg/paragraf/7" target="_blank" rel="noopener">§ 7 VKrG</a> Pflicht, bei Charge-Karten prüfen die Banken ebenfalls, weil sie das Geld bis zur Abrechnung vorstrecken.</p></div></div>
<div class="step"><span class="no">5</span><div><b>Rahmen festlegen</b><p>Zu Beginn liegt der Rahmen oft bei 1.000 bis 3.000 €. Nach einigen Monaten pünktlicher Zahlung kannst du eine Erhöhung beantragen.</p></div></div>
<div class="step"><span class="no">6</span><div><b>Karte aktivieren</b><p>Die Karte kommt per Post, der PIN getrennt oder in der App. Bei vielen Anbietern kannst du die Karte sofort in Apple Pay oder Google Pay laden.</p></div></div></div>'''),
            ('Wie lange es dauert','<div class="prose"><p>Advanzia und TF Bank entscheiden automatisch, die Zusage kommt oft in wenigen Minuten. card complete, PayLife, American Express und Diners Club prüfen Unterlagen teils händisch, das dauert ein paar Werktage. Bei der Hausbank hängt es davon ab, ob ein Berater freigeben muss. Die physische Karte ist in der Regel nach 5 bis 10 Werktagen da, der PIN kommt in einem eigenen Brief. Wer die Karte für eine Reise braucht, sollte drei Wochen Vorlauf einplanen.</p></div>'),
            ('Warum Anträge in Österreich abgelehnt werden','<div class="prose"><p>Der häufigste Grund ist ein negativer Eintrag beim KSV1870, etwa aus einem Inkassofall oder einem gekündigten Kredit. Dazu kommen ein zu niedriges oder unregelmäßiges Einkommen, ein befristeter Vertrag oder die Probezeit, ein erst kürzlich gemeldeter Wohnsitz und viele Anfragen in kurzer Zeit. Manche Anbieter nennen Mindesteinkommen, die meisten entscheiden nach eigenem Ermessen und müssen den Grund nicht erklären.</p><p>Was du tun kannst: Fordere beim KSV1870 die kostenlose <a class="lnk" href="https://ksv.at/digitaler-antrag-art-15" target="_blank" rel="noopener">Auskunft nach Art. 15 DSGVO</a> an. Der kostenpflichtige InfoPass ist dafür nicht nötig, die Gratis-Auskunft dauert laut KSV nur länger. Falsche oder erledigte Einträge kannst du korrigieren oder löschen lassen. Stell danach nicht mehrere Anträge gleichzeitig, sondern einen gezielt. Bis es klappt, ist eine <a href="../ohne-bonitaetspruefung/">Debitkarte ohne KSV-Abfrage</a> die praktische Lösung.</p></div>'),
            ('Deine Rechte nach dem Abschluss','<div class="prose"><ul><li><b>Rücktritt:</b> Schließt du den Vertrag online oder per Post ab, kannst du nach dem Fern-Finanzdienstleistungs-Gesetz 14 Tage lang ohne Angabe von Gründen zurücktreten.</li><li><b>Haftung bei Missbrauch:</b> Nach <a class="lnk" href="https://gesetzefinden.at/bundesrecht/bundesgesetze/zadig-2018/para-68" target="_blank" rel="noopener">§ 68 ZaDiG 2018</a> haftest du bei leichter Fahrlässigkeit mit höchstens 50 €. Hast du den Verlust vor der Zahlung nicht bemerken können, haftest du gar nicht. Bei grober Fahrlässigkeit, etwa PIN auf der Karte, haftest du voll.</li><li><b>Kündigung:</b> Du kannst den Kartenvertrag jederzeit kündigen, die Frist darf höchstens einen Monat betragen. Die Jahresgebühr darf die Bank nur anteilig bis zum Vertragsende verrechnen.</li><li><b>Kein Entgelt für die Zusage:</b> Seriöse Anbieter verlangen für den Antrag nichts. Vorkasse ist ein Warnsignal.</li></ul></div>'),
            ('Tipps für den Start','<div class="prose"><ul><li>Bei Charge-Karten läuft die Abrechnung per Einzug vom Konto. Prüfe, dass am Abbuchungstag genug Guthaben da ist, sonst drohen Mahnspesen und ein KSV-Eintrag.</li><li>Bei Advanzia, TF Bank und Santander ist Teilzahlung möglich. Stell die Rückzahlung auf 100 %, die Zinsen liegen sonst bei rund 25 % im Jahr. Mehr dazu im Ratgeber <a href="../teilzahlung/">Teilzahlung</a>.</li><li>Lade die Karte gleich in Apple Pay oder Google Pay, dann zahlst du schon vor dem Postweg.</li><li>Vor einer Reise den Rahmen prüfen: Mietwagen und Hotel reservieren oft mehrere hundert Euro.</li><li>Lies die Versicherungsbedingungen, bevor du dich auf den Reiseschutz der Karte verlässt.</li></ul></div>')],
      faq=[('Wie lange dauert ein Kreditkartenantrag in Österreich?','Bei Advanzia und TF Bank kommt die Zusage oft in Minuten, bei card complete, PayLife oder der Hausbank nach einigen Werktagen. Die Karte selbst ist meist nach 5 bis 10 Werktagen im Briefkasten.'),
           ('Sieht der KSV1870 jeden Kreditkartenantrag?','Die Anfrage der Bank wird beim KSV1870 vermerkt. Eine einzelne Anfrage ist kein Problem. Mehrere Anträge in kurzer Zeit können Banken aber vorsichtig machen.'),
           ('Bekomme ich eine Kreditkarte ohne Girokonto bei der Bank?','Ja. card complete, PayLife, American Express, Diners Club, Advanzia und TF Bank verlangen kein Konto bei sich, sondern nur ein SEPA-Konto für die Abbuchung. Die Karten der Hausbanken gibt es dagegen nur zum eigenen Konto.'),
           ('Kann ich als Student oder ohne Einkommen eine Kreditkarte bekommen?','Studierende bekommen bei Erste Bank, Raiffeisen oder BAWAG oft eine Karte mit kleinem Rahmen zum Studentenkonto. Ohne Einkommen bleibt meist nur die Debitkarte. Details stehen im Ratgeber <a href="../kreditkarte-studenten/">Kreditkarte für Studierende</a>.'),
           ('Welche Kreditkarte ist in Österreich am besten?',f'In unserer Gesamtwertung liegt die {credit[0]["titel"]} vorne ({de1(credit[0]["stars"])} Sterne, Stand {STAND_DE}).')],
      related=['kostenlose-kreditkarte','ohne-bonitaetspruefung','kartentypen'])
    else:
      art('de','kreditkarte-beantragen',
      h1='Kreditkarte beantragen in Deutschland: so geht es Schritt für Schritt',
      mt='Kreditkarte beantragen in Deutschland: Ablauf | Finvallo',
      desc='Kreditkarte in Deutschland beantragen: Voraussetzungen, VideoIdent oder PostIdent, Schufa-Prüfung, Dauer und was bei einer Ablehnung hilft. Mit Karten aus unserem Vergleich.',
      lede='Sparkasse, Direktbank oder Kartenbank ohne Konto: wie der Antrag in Deutschland abläuft, was die Schufa dabei sieht und welche Rechte du danach hast.',
      kurz='Du beantragst die Karte online, stimmst der Schufa-Klausel zu, identifizierst dich per VideoIdent, PostIdent oder Online-Ausweis und die Bank prüft deine Bonität bei der Schufa. Bei Kartenbanken wie Hanseatic, Advanzia oder TF Bank kommt die Zusage oft in Minuten, die Karte nach ein bis zwei Wochen. Wichtig bei diesen Karten: die voreingestellte Teilzahlung auf 100 % umstellen, sonst zahlst du Zinsen.',
      secs=[('Voraussetzungen in Deutschland','<div class="prose"><ul><li><b>Wohnsitz in Deutschland</b> und mindestens 18 Jahre. Für Jugendliche gibt es nur Prepaid- und Debitkarten.</li><li><b>Personalausweis oder Reisepass</b> mit gültiger Meldeadresse. Bei Reisepass verlangen manche Anbieter zusätzlich die Meldebescheinigung.</li><li><b>Ein Girokonto</b> für die Lastschrift. Sparkassen, Volksbanken, Commerzbank, DKB oder ING geben die Karte nur zum eigenen Konto. Hanseatic, Advanzia, TF Bank, Bank Norwegian, Barclays oder American Express buchen von jedem deutschen Konto ab.</li><li><b>Regelmäßiges Einkommen.</b> Die meisten Anbieter fragen das Nettoeinkommen ab, Gehaltsnachweise verlangen sie nur bei hohen Rahmen oder Rückfragen.</li><li><b>Zustimmung zur Schufa-Klausel.</b> Ohne sie bearbeitet keine Bank den Antrag.</li></ul></div>'),
            ('Drei Anbietertypen: Hausbank, Direktbank, Kartenbank',f'<div class="prose"><p><b>Hausbanken</b> wie Sparkasse, Volksbank, Commerzbank oder Postbank geben Charge-Karten zum Girokonto aus. Du beantragst sie in der Filiale oder im Online-Banking, die Bank kennt deine Umsätze und entscheidet schnell. Dafür kostet die Karte meist 30 bis 100 € im Jahr und verlangt im Ausland 1,75 bis 2,35 % Auslandseinsatzentgelt.</p><p><b>Direktbanken</b> wie DKB, ING, comdirect oder Consorsbank liefern die Karte zum kostenlosen Konto. Oft ist das eine Visa Debitkarte, die echte Kreditkarte mit Rahmen gibt es gegen Aufpreis oder bei genug Geldeingang.</p><p><b>Kartenbanken</b> wie Hanseatic Bank, Advanzia, TF Bank, Bank Norwegian, Barclays oder American Express brauchen kein Konto bei sich. Sie leben von Teilzahlungszinsen, deshalb ist die Ratenzahlung bei vielen voreingestellt. Wer den Lastschrifteinzug auf 100 % stellt, nutzt die Karte zinsfrei.</p></div>'+(table(kk,[COL['karte'],COL['typ'],COL['fee'],COL['fx'],COL['stars']],P)+f'<p class="note">Die am besten bewerteten Kredit- und Charge-Karten ohne Konto-Pflicht aus unserem Deutschland-Vergleich. <a class="lnk" href="{best}">Alle Bestenlisten →</a></p>' if kk else '')),
            ('So läuft der Antrag ab',f'''<div class="steps"><div class="step"><span class="no">1</span><div><b>Karte auswählen</b><p>Vergleiche Jahresgebühr, Auslandseinsatzentgelt, Abhebungen und Versicherungen. Unsere <a href="{best}">Bestenlisten</a> zeigen je Zweck die günstigste Karte.</p></div></div>
<div class="step"><span class="no">2</span><div><b>Antrag ausfüllen</b><p>Name, Adresse, Beruf, Arbeitgeber, Nettoeinkommen, Miete und laufende Kredite. Dazu die Schufa-Klausel und bei Kartenbanken die Wahl des Rückzahlungsmodus.</p></div></div>
<div class="step"><span class="no">3</span><div><b>Identifizieren</b><p>VideoIdent per Handy dauert zehn Minuten. Alternativ PostIdent in der Postfiliale oder die Online-Ausweisfunktion des Personalausweises mit der AusweisApp.</p></div></div>
<div class="step"><span class="no">4</span><div><b>Schufa-Prüfung</b><p>Die Bank fragt Score und Einträge ab. Bei Karten mit Teilzahlung ist die Kreditwürdigkeitsprüfung nach <a class="lnk" href="https://www.gesetze-im-internet.de/bgb/__505a.html" target="_blank" rel="noopener">§ 505a BGB</a> Pflicht, bei Charge-Karten prüfen die Banken freiwillig, weil sie bis zur Abrechnung in Vorleistung gehen.</p></div></div>
<div class="step"><span class="no">5</span><div><b>Rahmen und Zusage</b><p>Der erste Rahmen liegt oft bei 500 bis 2.500 €. Manche Anbieter erhöhen ihn automatisch nach einigen Monaten, bei anderen stellst du einen Antrag.</p></div></div>
<div class="step"><span class="no">6</span><div><b>Karte und PIN</b><p>Karte und PIN kommen getrennt per Post. Viele Banken zeigen die PIN auch in der App und lassen die Karte vorab in Apple Pay oder Google Pay laden.</p></div></div></div>'''),
            ('Was die Schufa dabei sieht','<div class="prose"><p>Mit dem Antrag meldet die Bank eine „Anfrage Kreditkarte“ an die Schufa. Diese Anfrage bleibt zwölf Monate gespeichert und ist für andere Banken sichtbar. Wird die Karte ausgegeben, kommt der Vertrag als Positivmerkmal dazu. Eine gekündigte Karte wegen Zahlungsverzug ist dagegen ein Negativmerkmal und bleibt in der Regel drei Jahre nach Erledigung sichtbar.</p><p>Bevor du mehrere Anträge stellst, lohnt ein Blick in die eigenen Daten. Die <a class="lnk" href="https://www.schufa.de/datenkopie" target="_blank" rel="noopener">Datenkopie nach Art. 15 DSGVO</a> ist kostenlos, kommt per Post und zeigt Einträge, Score und die Stellen, die zuletzt angefragt haben. Die kostenpflichtigen Pakete von meineSCHUFA brauchst du dafür nicht.</p></div>'),
            ('Wie lange es dauert','<div class="prose"><p>Kartenbanken entscheiden automatisiert: Bei Hanseatic, Advanzia, TF Bank oder Bank Norwegian siehst du die Zusage oft direkt nach dem VideoIdent. Sparkassen und Volksbanken brauchen je nach Filiale ein paar Tage, vor allem wenn ein Berater freigibt. Die Karte liegt meist nach 7 bis 14 Tagen im Briefkasten, der PIN kommt in einem zweiten Brief. Direktbanken wie DKB oder N26 geben oft schon vorher eine virtuelle Karte für das Smartphone frei.</p></div>'),
            ('Warum Anträge abgelehnt werden','<div class="prose"><p>Die häufigsten Gründe: ein Negativmerkmal oder schwacher Score bei der Schufa, zu niedriges Einkommen, Probezeit oder befristeter Vertrag, Selbstständigkeit ohne Nachweise, ein Wohnsitz von weniger als sechs Monaten und viele Anfragen in kurzer Zeit. Banken müssen die Ablehnung nicht begründen, viele verweisen pauschal auf die Schufa.</p><p>Wenn es nicht klappt: Datenkopie anfordern, falsche oder erledigte Einträge löschen lassen, dann zwei bis drei Monate warten und gezielt bei einem Anbieter mit niedrigen Hürden anfragen. Bis dahin reicht für Online-Shopping und Reisen eine <a href="../ohne-bonitaetspruefung/">Debitkarte ohne Schufa-Prüfung</a>.</p></div>'),
            ('Deine Rechte nach dem Abschluss','<div class="prose"><ul><li><b>Widerruf:</b> Bei Abschluss im Fernabsatz hast du 14 Tage Widerrufsrecht ohne Angabe von Gründen.</li><li><b>Kündigung:</b> Nach <a class="lnk" href="https://www.gesetze-im-internet.de/bgb/__675h.html" target="_blank" rel="noopener">§ 675h BGB</a> kannst du jederzeit kündigen, die Frist darf höchstens einen Monat betragen. Die Jahresgebühr steht der Bank nur anteilig bis zum Vertragsende zu.</li><li><b>Haftung bei Missbrauch:</b> <a class="lnk" href="https://www.gesetze-im-internet.de/bgb/__675v.html" target="_blank" rel="noopener">§ 675v BGB</a> begrenzt deine Haftung bei verlorener oder gestohlener Karte auf 50 €. Hast du den Verlust nicht bemerken können, haftest du nicht. Bei grober Fahrlässigkeit, etwa PIN im Geldbeutel, haftest du voll.</li><li><b>Keine Gebühr für den Antrag:</b> Vorkasse oder Bearbeitungsgebühren für die Zusage sind in Deutschland ein sicheres Zeichen für ein unseriöses Angebot.</li></ul></div>'),
            ('Tipps für den Start','<div class="prose"><ul><li>Bei Hanseatic, Advanzia, TF Bank, Barclays oder der Amazon Visa den Rückzahlungsmodus auf 100 % per Lastschrift stellen. Die voreingestellte Rate von 3 % kostet sonst 15 bis 28 % Zinsen im Jahr. Mehr dazu im Ratgeber <a href="../teilzahlung/">Teilzahlung</a>.</li><li>Bei Charge-Karten der Hausbank reicht Guthaben am Abrechnungstag. Rückbuchungen wegen fehlender Deckung landen schnell in der Schufa.</li><li>Karte sofort in Apple Pay oder Google Pay laden, dann kannst du vor dem Postweg zahlen.</li><li>Vor einer Reise den Rahmen prüfen: Mietwagen und Hotels reservieren oft 300 € und mehr.</li><li>Versicherungsbedingungen lesen, bevor du dich auf den Reiseschutz verlässt.</li></ul></div>')],
      faq=[('Wie lange dauert ein Kreditkartenantrag in Deutschland?','Bei Kartenbanken wie Hanseatic, Advanzia oder TF Bank kommt die Zusage oft in Minuten, bei Sparkassen und Volksbanken nach einigen Tagen. Die Karte liegt meist nach 7 bis 14 Tagen im Briefkasten.'),
           ('Schadet ein Kreditkartenantrag meinem Schufa-Score?','Eine einzelne Anfrage senkt den Score nicht dauerhaft. Sie bleibt aber zwölf Monate sichtbar. Viele Anfragen in kurzer Zeit werten Banken als Risikosignal.'),
           ('Welche Kreditkarte bekomme ich ohne Konto bei der Bank?','Hanseatic Bank, Advanzia, TF Bank, Bank Norwegian, Barclays, American Express und die Amazon Visa brauchen kein Konto bei sich, sondern nur ein deutsches Girokonto für die Lastschrift.'),
           ('Kann ich eine Kreditkarte ohne Einkommen bekommen?','Echte Kreditkarten mit Rahmen setzen ein regelmäßiges Einkommen voraus. Studierende bekommen bei DKB, ING oder der Hausbank oft eine Debitkarte oder eine Karte mit kleinem Rahmen, siehe <a href="../kreditkarte-studenten/">Kreditkarte für Studierende</a>. Ohne Einkommen bleibt die Debit- oder Prepaid-Karte.'),
           ('Warum steht meine Karte auf Teilzahlung?','Kartenbanken verdienen an Zinsen und stellen deshalb oft eine Mindestrate ein. In der App oder im Online-Banking kannst du auf 100 % Rückzahlung per Lastschrift umstellen. Dann ist die Karte zinsfrei.'),
           ('Welche Kreditkarte ist in Deutschland am besten?',f'In unserer Gesamtwertung liegt die {credit[0]["titel"]} vorne ({de1(credit[0]["stars"])} Sterne, Stand {STAND_DE}).')],
      related=['kostenlose-kreditkarte','ohne-bonitaetspruefung','kartentypen'])
    # C) ohne Bonitätsprüfung
    alt_tab=table(deb_free[:8]+[c for c in deb if c['typ']=='Prepaid' and c not in deb_free][:3],[COL['karte'],COL['typ'],COL['fee'],COL['fx'],COL['cash'],COL['stars']],P)
    prep=[c for c in RC if c['typ']=='Prepaid']
    prep_txt=fmtlist([f'die {c["titel"]} ({eur(c["fee"])} € im Jahr, {pct(c["fx"]) if c["fx"] else "0 %"} im Ausland)' for c in prep[:4]])
    if land=='at':
      art('at','ohne-bonitaetspruefung',
      h1='Kreditkarte ohne KSV-Abfrage: was wirklich geht',
      mt='Kreditkarte ohne KSV in Österreich: was geht | Finvallo',
      desc='Kreditkarte ohne KSV1870-Prüfung in Österreich? Warum es keine echte gibt, welche Debit- und Prepaid-Karten ohne Bonitätsprüfung funktionieren und was dir immer zusteht.',
      lede='Ohne Bonitätsprüfung gibt es in Österreich keinen Kreditrahmen. Bankomatkarte, Neobank-Debitkarte, Prepaid und Basiskonto decken trotzdem fast alles ab.',
      kurz=f'Jede Bank in Österreich fragt vor einer Kredit- oder Charge-Karte den KSV1870 ab, bei Teilzahlungskarten schreibt das Verbraucherkreditgesetz die Prüfung vor. Ohne Prüfung bekommst du eine Debitkarte zum Girokonto, eine Debit Mastercard oder Visa Debit von N26, Revolut oder bunq oder eine Prepaid-Karte. {len(deb_free)} Debitkarten ohne Grundgebühr stehen in unserem Vergleich. Sie funktionieren online, im Ausland und mit Apple Pay, nur bei Kautionen für Mietwagen und Hotels stoßen sie an Grenzen.',
      secs=[('Warum es in Österreich keine Kreditkarte ohne Prüfung gibt','<div class="prose"><p>Bei einer Charge-Karte, dem österreichischen Standard, streckt die Bank jeden Umsatz bis zur Monatsabrechnung vor. Bei einer Karte mit Teilzahlung gibt sie dir einen echten Kredit. In beiden Fällen trägt sie das Risiko, dass du nicht zahlst. Für Karten mit Teilzahlung verlangt <a class="lnk" href="https://www.jusline.at/gesetz/vkrg/paragraf/7" target="_blank" rel="noopener">§ 7 Verbraucherkreditgesetz</a> ausdrücklich eine Prüfung der Kreditwürdigkeit. Bei Charge-Karten gilt das Gesetz nicht in jedem Fall, die Banken prüfen aber aus eigenem Interesse. Deshalb bietet kein seriöser Anbieter eine Karte mit Rahmen „ohne KSV“ an, auch nicht card complete, PayLife oder die Hausbanken.</p></div>'),
            ('Was der KSV1870 über dich speichert','<div class="prose"><p>Der Kreditschutzverband von 1870 sammelt Daten zu laufenden Krediten, Leasingverträgen, Kreditkarten und vor allem zu Zahlungsstörungen: Inkassofälle, Mahnklagen, gekündigte Kredite. Dazu führt er die Warnliste der Banken, in die ein Konto nach einem gekündigten Kredit oder einer Dauerüberziehung kommt. Ein Eintrag in der Warnliste führt bei fast allen Banken zur Ablehnung.</p><p>Du hast ein Recht darauf, deine Daten zu sehen. Die <a class="lnk" href="https://ksv.at/digitaler-antrag-art-15" target="_blank" rel="noopener">Auskunft nach Art. 15 DSGVO</a> ist kostenlos und kommt als PDF, laut KSV innerhalb der gesetzlichen Frist von einem Monat. Den kostenpflichtigen InfoPass brauchst du dafür nicht. Falsche Einträge musst du nicht hinnehmen: Du kannst Berichtigung oder Löschung verlangen, und bezahlte Forderungen müssen als erledigt gekennzeichnet werden.</p></div>'),
            ('Gute Alternativen ohne Kreditprüfung',alt_tab+f'<p class="note">Debitkarten ohne Grundgebühr und Prepaid-Karten aus unserem Österreich-Vergleich, sortiert nach Bewertung. Bei der Kontoeröffnung weist du dich per Video-Ident aus, eine KSV-Abfrage für einen Kreditrahmen gibt es nicht. Manche Banken fragen trotzdem die Warnliste ab, um Kontomissbrauch auszuschließen. <a class="lnk" href="{best}debit/">Alle Debitkarten ansehen →</a></p>'),
            ('Bankomatkarte und Basiskonto: was dir immer zusteht','<div class="prose"><p>Die Bankomatkarte zum Girokonto ist seit dem Ende von Maestro 2023 eine Debit Mastercard oder Visa Debit. Damit zahlst du online, im Ausland und mit Apple Pay oder Google Pay, und du behebst an jedem Bankomaten. Für die meisten Alltagszwecke ersetzt sie eine Kreditkarte, nur die Kaution beim Mietwagen und die Teilzahlung fehlen.</p><p>Wer wegen eines KSV-Eintrags kein normales Konto bekommt, hat nach dem Verbraucherzahlungskontogesetz Anspruch auf ein <a href="../basiskonto/">Basiskonto</a> mit Debitkarte. Es darf laut <a class="lnk" href="https://www.konsumentenfragen.at/konsumentenfragen/Aktuelles/Konsumentenfragen/Basiskonto_Deutsch.pdf" target="_blank" rel="noopener">Sozialministerium</a> höchstens rund 80 € im Jahr kosten, für sozial schutzwürdige Personen die Hälfte. Überziehung und Kreditkarte sind beim Basiskonto ausgeschlossen, die Debitkarte ist inklusive.</p></div>'),
            ('Prepaid in Österreich: wann sie sinnvoll ist',f'<div class="prose"><p>Eine Prepaid-Karte lädst du per Überweisung auf und gibst nur das Guthaben aus. In unserem Vergleich steht {prep_txt if prep else "derzeit keine Prepaid-Karte"}. Sinnvoll ist Prepaid für Jugendliche, für ein striktes Budget oder wenn du eine Karte brauchst, die auf keinen Fall ins Minus rutschen kann. Für alle anderen ist eine gebührenfreie Debitkarte die günstigere Wahl, weil das Aufladen entfällt und die Gebühren niedriger sind.</p></div>' if prep else '<div class="prose"><p>Prepaid-Karten lädst du per Überweisung auf und gibst nur das Guthaben aus. Für die meisten ist eine gebührenfreie Debitkarte die günstigere Wahl.</p></div>'),
            ('Wo Debit und Prepaid an Grenzen stoßen','<div class="prose"><ul><li><b>Mietwagen:</b> Viele Stationen reservieren die Kaution nur auf einer Kredit- oder Charge-Karte. Bei Debitkarten wird der Betrag abgebucht und erst Tage später zurücküberwiesen, Neobank-Karten lehnen manche Vermieter ganz ab. Details im Ratgeber <a href="../mietwagen-kaution/">Mietwagen und Kaution</a>.</li><li><b>Hotels und Tankautomaten:</b> Reservierungen von 100 bis 300 € blockieren dein Kontoguthaben, nicht einen Rahmen.</li><li><b>Zahlungsaufschub:</b> Das Geld geht sofort vom Konto. Wer die Monatsabrechnung als Puffer braucht, hat die nicht.</li><li><b>Versicherungen:</b> Reiseschutz gibt es fast nur bei den bezahlten Stufen der Neobanken, etwa N26 Go oder Revolut Premium.</li></ul></div>'),
            ('Vorsicht bei diesen Angeboten','<div class="prose"><p>Rund um „Kreditkarte ohne KSV“ tummeln sich Vermittler, die vom Wunsch nach einer schnellen Zusage leben. Finger weg bei:</p><ul><li>Vorkasse, „Bearbeitungsgebühr“ oder Vermittlungsprovision vor der Zusage. Seriöse Banken verlangen für den Antrag nichts.</li><li>„Garantierter Zusage“ für eine Karte mit Kreditrahmen. Die gibt es nicht.</li><li>Prepaid-Karten mit Monatsgebühr, Aufladegebühr und Gebühr pro Behebung. Zusammen kosten sie schnell mehr als 100 € im Jahr.</li><li>Angeboten aus dem Ausland, die mit „Kredit ohne KSV“ werben und Daten oder Vorauszahlungen sammeln.</li></ul><p>Bei Zweifeln hilft die Konsumentenberatung der Arbeiterkammer in deinem Bundesland.</p></div>'),
            ('Bonität aufbauen: so klappt es später mit der Kreditkarte','<div class="prose"><ol><li>Auskunft beim KSV1870 anfordern, Fehler korrigieren, erledigte Forderungen als erledigt kennzeichnen lassen.</li><li>Ein Girokonto über mindestens sechs Monate ohne Überziehung führen. Hausbanken geben ihre Charge-Karte eher an Kunden, deren Konto sie kennen.</li><li>Rechnungen, Handyvertrag und Raten pünktlich zahlen. Jeder neue Inkassofall verlängert die Sperre.</li><li>Nicht bei mehreren Anbietern gleichzeitig anfragen. Jede Anfrage ist beim KSV sichtbar.</li><li>Mit einer Karte mit kleinem Rahmen beginnen, etwa der Classic-Karte der Hausbank, und erst später auf Gold oder Teilzahlungskarten wechseln. Wie der Antrag abläuft, steht im Ratgeber <a href="../kreditkarte-beantragen/">Kreditkarte beantragen</a>.</li></ol></div>')],
      faq=[('Gibt es in Österreich eine Kreditkarte ganz ohne KSV?','Nein, nicht mit Kreditrahmen. Charge- und Teilzahlungskarten werden immer geprüft. Ohne Prüfung bekommst du Debit- und Prepaid-Karten mit Visa oder Mastercard.'),
           ('Reicht die Bankomatkarte für Online-Shopping und Reisen?','Ja. Als Debit Mastercard oder Visa Debit funktioniert sie online, im Ausland und in Apple Pay oder Google Pay. Nur bei Kautionen und bei der Teilzahlung ist sie keine Kreditkarte.'),
           ('Was kostet die Auskunft beim KSV1870?','Die Auskunft nach Art. 15 DSGVO ist kostenlos und kommt innerhalb eines Monats. Der kostenpflichtige InfoPass ist nur nötig, wenn eine Stelle eine Auskunft zur Vorlage verlangt.'),
           ('Bekomme ich mit negativem KSV-Eintrag ein Konto?','Ja. Das Basiskonto nach dem Verbraucherzahlungskontogesetz steht jedem Verbraucher mit rechtmäßigem Aufenthalt in der EU zu, mit Debitkarte, aber ohne Überziehung und ohne Kreditkarte.'),
           ('Wo gibt es Probleme mit Debitkarten?','Vor allem bei Mietwagen und Hotels. Dort wird die Kaution vom Konto abgebucht statt reserviert, und manche Stationen nehmen Debit- und Neobank-Karten gar nicht an.')],
      related=['kartentypen','kreditkarte-beantragen','mietwagen-kaution'])
    else:
      art('de','ohne-bonitaetspruefung',
      h1='Kreditkarte ohne Schufa: was wirklich geht',
      mt='Kreditkarte ohne Schufa in Deutschland: was geht | Finvallo',
      desc='Kreditkarte ohne Schufa in Deutschland? Warum es keine echte gibt, welche Debit- und Prepaid-Karten ohne Bonitätsprüfung funktionieren und woran du unseriöse Angebote erkennst.',
      lede='Ohne Schufa-Prüfung gibt es in Deutschland keinen Kreditrahmen. Debitkarte, Prepaid und Basiskonto decken den Alltag trotzdem ab, mit zwei Ausnahmen.',
      kurz=f'Jede deutsche Bank fragt vor einer Kredit- oder Charge-Karte die Schufa ab, bei Karten mit Teilzahlung ist die Kreditwürdigkeitsprüfung nach § 505a BGB Pflicht. Ohne Prüfung bekommst du eine Visa Debitkarte oder Debit Mastercard zum Girokonto, etwa bei DKB, ING, comdirect, N26 oder C24, oder eine Prepaid-Karte. {len(deb_free)} Debitkarten ohne Grundgebühr stehen in unserem Vergleich. Sie funktionieren online, im Ausland und mit Apple Pay, nur bei Kautionen für Mietwagen und Hotels stoßen sie an Grenzen.',
      secs=[('Warum die Schufa-Abfrage dazugehört','<div class="prose"><p>Bei einer Kreditkarte mit Teilzahlung schließt du rechtlich einen Verbraucherdarlehensvertrag. Die Bank muss vorher nach <a class="lnk" href="https://www.gesetze-im-internet.de/bgb/__505a.html" target="_blank" rel="noopener">§ 505a BGB</a> deine Kreditwürdigkeit prüfen, sonst darf sie den Vertrag nicht abschließen. Bei einer Charge-Karte, wie sie Sparkassen, Volksbanken oder American Express ausgeben, streckt die Bank das Geld nur bis zur Monatsabrechnung vor. Das Gesetz zwingt sie nicht zur Prüfung, aber sie trägt das Ausfallrisiko und fragt deshalb trotzdem bei der Schufa an. Deshalb gibt es weder bei Hanseatic, Advanzia oder TF Bank noch bei der Hausbank eine Karte mit Rahmen „ohne Schufa“.</p></div>'),
            ('Was in der Schufa steht und was nicht','<div class="prose"><p>Die Schufa speichert Positivdaten wie Girokonten, Kreditkarten, Kredite und Mobilfunkverträge sowie Negativmerkmale: Mahnbescheide, titulierte Forderungen, gekündigte Kredite, Privatinsolvenz. Daraus berechnet sie den Score. Anfragen von Banken bleiben zwölf Monate sichtbar, erledigte Negativmerkmale in der Regel drei Jahre. Einkommen, Vermögen oder Beruf kennt die Schufa nicht.</p><p>Die <a class="lnk" href="https://www.schufa.de/datenkopie" target="_blank" rel="noopener">Datenkopie nach Art. 15 DSGVO</a> bekommst du kostenlos direkt bei der Schufa, per Post innerhalb von etwa einer Woche. Sie zeigt alle Einträge, den Score und die Stellen, die zuletzt angefragt haben. Das kostenpflichtige Paket meineSCHUFA brauchst du dafür nicht, und Drittanbieter, die für die Datenkopie Geld verlangen, haben mit der Schufa nichts zu tun.</p></div>'),
            ('Gute Alternativen ohne Kreditprüfung',alt_tab+f'<p class="note">Debitkarten ohne Grundgebühr und Prepaid-Karten aus unserem Deutschland-Vergleich, sortiert nach Bewertung. Bei der Kontoeröffnung weist du dich per VideoIdent oder PostIdent aus, eine Schufa-Prüfung für einen Kreditrahmen entfällt. Manche Banken fragen die Schufa trotzdem ab, um Kontomissbrauch auszuschließen; ein Negativmerkmal kann dann zur Ablehnung des Kontos führen. <a class="lnk" href="{best}debit/">Alle Debitkarten ansehen →</a></p>'),
            ('Debitkarte zum Girokonto: der einfachste Weg','<div class="prose"><p>Die girocard reicht für Supermarkt und Geldautomat in Deutschland, aber nicht für Online-Shops, Hotels oder das Ausland außerhalb Europas. Dafür brauchst du eine Debitkarte mit Visa- oder Mastercard-Logo. Die gibt es bei DKB, ING, comdirect und Consorsbank zum Konto, bei N26, C24, Revolut oder Trade Republic ganz ohne Filialbank. Sie funktioniert online, in Apple Pay und Google Pay und an jedem Automaten, der Visa oder Mastercard nimmt.</p><p>Auf diesen Karten steht „Debit“. Händler und Vermieter erkennen daran, dass kein Kreditrahmen dahintersteht. Für Zahlungen spielt das keine Rolle, für Kautionen schon.</p><p>Wer wegen eines Negativmerkmals gar kein Konto bekommt, hat nach <a class="lnk" href="https://www.gesetze-im-internet.de/zkg/__31.html" target="_blank" rel="noopener">§ 31 Zahlungskontengesetz</a> Anspruch auf ein <a href="../basiskonto/">Basiskonto</a> mit Debitkarte. Überziehung und Kreditkarte sind dabei ausgeschlossen, Zahlungen, Lastschriften und Abhebungen eingeschlossen.</p></div>'),
            ('Prepaid-Kreditkarten in Deutschland',f'<div class="prose"><p>Prepaid-Karten tragen das Visa- oder Mastercard-Logo, funktionieren aber nur mit vorher aufgeladenem Guthaben. In unserem Vergleich stehen {prep_txt if prep else "derzeit keine Prepaid-Karten"}. Sparkassen und Volksbanken geben sie oft an Jugendliche ab 12 oder an Kunden aus, die keine Charge-Karte bekommen. Das Aufladen läuft per Überweisung oder Dauerauftrag vom Girokonto.</p><p>Der Haken sind die Kosten: Jahresgebühr, oft Auslandseinsatzentgelt und Gebühren fürs Abheben. Eine gebührenfreie Debitkarte kann das Gleiche und kostet nichts. Prepaid lohnt sich fast nur, wenn du bewusst eine Karte ohne Zugriff aufs Konto willst, etwa für Kinder oder als Zweitkarte für unsichere Online-Shops.</p></div>'),
            ('Wo Debit und Prepaid an Grenzen stoßen','<div class="prose"><ul><li><b>Mietwagen:</b> Sixt und Europcar nehmen Debitkarten in Deutschland nur für bestimmte Fahrzeugklassen, im Ausland oft gar nicht. Die Kaution wird abgebucht statt reserviert. Details im Ratgeber <a href="../mietwagen-kaution/">Mietwagen und Kaution</a>.</li><li><b>Hotels:</b> Die Reservierung bei Anreise blockiert dein Kontoguthaben, bei Prepaid-Karten lehnen viele Hotels ab.</li><li><b>Kein Zahlungsaufschub:</b> Das Geld geht sofort vom Konto, es gibt keine Monatsrechnung als Puffer.</li><li><b>Versicherungen:</b> Reiseschutz gibt es bei Debitkarten fast nur in den Bezahlstufen von N26, Revolut oder Tomorrow.</li></ul></div>'),
            ('Finger weg: unseriöse Angebote','<div class="prose"><p>„Kreditkarte ohne Schufa“ ist eine beliebte Suchanfrage, und entsprechend viele Vermittler werben damit. Erkennungsmerkmale für ein schlechtes Angebot:</p><ul><li>Vorkasse, „Bearbeitungsgebühr“ oder Provision, bevor es eine Zusage gibt. Seriöse Banken verlangen für den Antrag nichts.</li><li>„Garantierte Zusage“ oder „100 % Annahme“ für eine Karte mit Kreditrahmen.</li><li>Prepaid-Karten mit Monatsgebühr, Aufladegebühr und Gebühr pro Zahlung. Zusammen oft über 100 € im Jahr.</li><li>Kostenpflichtige Abos, die mit einer „Schufa-Auskunft“ locken und nur die kostenlose Datenkopie weiterreichen.</li></ul><p>Die Verbraucherzentralen warnen regelmäßig vor solchen Angeboten. Bei Zweifeln hilft die Beratungsstelle in deinem Bundesland.</p></div>'),
            ('Schufa-Score verbessern: so klappt es später mit der Kreditkarte','<div class="prose"><ol><li>Datenkopie anfordern, falsche oder veraltete Einträge löschen lassen. Erledigte Forderungen müssen als erledigt gekennzeichnet sein.</li><li>Ein Girokonto über mindestens sechs Monate ohne Dispo-Überziehung führen. Die eigene Bank gibt ihre Charge-Karte eher an Kunden mit geordnetem Konto.</li><li>Rechnungen, Handyvertrag und Raten pünktlich zahlen. Jeder neue Mahnbescheid verlängert die Sperre um Jahre.</li><li>Nicht bei mehreren Banken gleichzeitig anfragen. Jede Anfrage bleibt zwölf Monate sichtbar.</li><li>Unnötige alte Konten und Karten kündigen, bevor du neu anfragst. Viele offene Rahmen drücken den Score.</li><li>Mit einer Karte mit kleinem Rahmen anfangen und erst später auf Gold oder Reisekarten wechseln. Der Ablauf steht im Ratgeber <a href="../kreditkarte-beantragen/">Kreditkarte beantragen</a>.</li></ol></div>')],
      faq=[('Gibt es in Deutschland eine Kreditkarte ganz ohne Schufa?','Nein, nicht mit Kreditrahmen. Charge- und Teilzahlungskarten werden immer geprüft. Ohne Prüfung bekommst du Debit- und Prepaid-Karten mit Visa oder Mastercard.'),
           ('Reicht eine Debitkarte für Online-Shopping und Reisen?','Ja, wenn sie ein Visa- oder Mastercard-Logo trägt. Die girocard allein funktioniert online nicht. Nur bei Kautionen für Mietwagen und Hotels ist eine Debitkarte keine vollwertige Kreditkarte.'),
           ('Was kostet die Schufa-Datenkopie?','Nichts. Die Datenkopie nach Art. 15 DSGVO bestellst du direkt bei der Schufa, sie kommt per Post. Nur das Abo meineSCHUFA und Drittanbieter kosten Geld.'),
           ('Bekomme ich mit Negativmerkmal ein Girokonto?','Ja. Das Basiskonto nach § 31 Zahlungskontengesetz steht jedem Verbraucher mit rechtmäßigem Aufenthalt in der EU zu, mit Debitkarte, aber ohne Dispo und ohne Kreditkarte.'),
           ('Ist eine Prepaid-Kreditkarte besser als eine Debitkarte?','Meist nicht. Beide brauchen keine Kreditprüfung, aber die Debitkarte zum Konto ist in der Regel gebührenfrei und muss nicht aufgeladen werden. Prepaid lohnt sich vor allem für Kinder und als Zweitkarte.'),
           ('Wo gibt es Probleme mit Debitkarten?','Vor allem bei Mietwagen und Hotels. Dort wird die Kaution vom Konto abgebucht statt reserviert, und viele Stationen nehmen Debitkarten nur für kleinere Fahrzeugklassen.')],
      related=['kartentypen','kreditkarte-beantragen','mietwagen-kaution'])
    # D) Visa, Mastercard oder Amex
    from collections import Counter
    nets=Counter('Amex' if 'American' in c['netz'] else 'Visa' if c['netz']=='Visa' else 'Mastercard' if c['netz']=='Mastercard' else 'beide' for c in C)
    amex=[c for c in RC if 'American' in c['netz']]
    amexfx=sorted({c['fx'] for c in amex if c['fx'] is not None})
    diners=[c for c in RC if 'Diners' in c['netz']]
    amex_fx_txt=fmtlist([pct(x) for x in amexfx]) if amexfx else 'eine eigene Gebühr'
    nets_tab=(f'<div class="tbl"><table><thead><tr><th>Netz</th><th>Karten im Vergleich</th></tr></thead><tbody>'+''.join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k,v in [('Visa',nets['Visa']),('Mastercard',nets['Mastercard']),('American Express',nets['Amex']),('Diners Club',len([c for c in C if 'Diners' in c['netz']])),('Visa oder Mastercard wählbar',nets['beide'])] if v)+'</tbody></table></div>')
    net_best=''.join(f'<h3>{n}</h3>'+table([c for c in RC if f(c)][:3],[COL['karte'],COL['fee'],COL['fx'],COL['stars']],P) for n,f in [('Visa',lambda c:c['netz']=='Visa'),('Mastercard',lambda c:c['netz']=='Mastercard'),('American Express',lambda c:'American' in c['netz']),('Diners Club',lambda c:'Diners' in c['netz'])] if any(f(c) for c in RC))
    if land=='at':
      art('at','visa-mastercard-amex',
      h1='Visa, Mastercard oder American Express?',
      mt='Visa, Mastercard oder Amex in Österreich? | Finvallo',
      desc=f'Visa, Mastercard, American Express oder Diners Club: Akzeptanz in Österreich, Wechselkurse, Bearbeitungsentgelt und wer welche Karte ausgibt, mit Zahlen aus {len(C)} Karten.',
      lede='In Österreich entscheidet weniger das Logo als die Bank dahinter. Mit Diners Club hat das Land aber eine Besonderheit, die es sonst kaum gibt.',
      kurz=f'Visa und Mastercard werden in Österreich an praktisch jedem Terminal angenommen, seit die Bankomatkarte eine Debit Mastercard oder Visa Debit ist, erst recht. Welches der beiden Netze auf deiner Karte steht, hängt meist von der Bank ab: Bank Austria und Raiffeisen geben Mastercard aus, card complete, PayLife und Erste Bank lassen dich wählen. American Express und Diners Club werden seltener akzeptiert und verlangen {amex_fx_txt} (Amex) beziehungsweise 1,65 % (Diners) in fremder Währung, bringen aber Punkte, Lounges und Versicherungen.',
      secs=[('Akzeptanz in Österreich','<div class="prose"><p>Seit dem Ende von Maestro 2023 ist jede neue Bankomatkarte eine Debit Mastercard oder Visa Debit. Ein Terminal, das sie nimmt, nimmt damit auch Kreditkarten der beiden Netze. Deshalb kannst du mit Visa und Mastercard im Supermarkt, an der Tankstelle, beim Würstelstand mit Kartenterminal und in jedem Online-Shop zahlen. Unterschiede zwischen den beiden Netzen gibt es in Österreich praktisch keine.</p><p>American Express nehmen große Ketten, Hotels, Airlines, Tankstellen und viele Restaurants in Wien, kleinere Händler und Gastronomen am Land aber oft nicht. Diners Club ist ein Sonderfall: Die Karte gibt es in Österreich seit Jahrzehnten, und laut <a class="lnk" href="https://www.bankaustria.at/files/Diners_Partner_Akzeptanz_Infoblatt.pdf" target="_blank" rel="noopener">Diners Club</a> nehmen sie über 100.000 Akzeptanzstellen im Land, weltweit läuft sie über das Discover-Netz. Außerhalb Österreichs und Nordamerikas ist die Akzeptanz aber lückenhaft. Wer Amex oder Diners nutzt, sollte eine Visa oder Mastercard als Reserve dabeihaben.</p></div>'),
            ('Wer in Österreich welche Karte ausgibt','<div class="prose"><ul><li><b>Mastercard:</b> Bank Austria, Raiffeisen, Bank Direkt, bank99, Oberbank, easybank sowie Advanzia und TF Bank. Mastercard ist in Österreich das häufigste Netz.</li><li><b>Visa oder Mastercard wählbar:</b> card complete, PayLife (BAWAG-Gruppe), Erste Bank und Sparkasse, BAWAG. Die Konditionen sind bei beiden Varianten gleich.</li><li><b>Visa:</b> vor allem Debitkarten wie Trade Republic oder Wise, bei Revolut kommt es auf den Standort an.</li><li><b>American Express:</b> gibt die Karten in Österreich selbst aus, inklusive der BMW Card.</li><li><b>Diners Club:</b> eigene Karten über die DC Bank, von Classic bis Vintage.</li></ul></div>'),
            (f'So verteilen sich die {len(C)} Karten in unserem Österreich-Vergleich',nets_tab),
            ('Wechselkurse und Bearbeitungsentgelt','<div class="prose"><p>Visa und Mastercard rechnen Fremdwährungen zu eigenen Tageskursen um, die nahe am Devisenmittelkurs liegen und sich kaum unterscheiden. Teuer wird es durch das, was die Bank draufschlägt: ein Bearbeitungsentgelt von 1,35 bis 3,15 % bei den österreichischen Hausbanken, bei manchen zusätzlich ein Kursaufschlag. American Express verlangt in Österreich 2 %, Diners Club 1,65 %. Karten von Advanzia, TF Bank und den Neobanken rechnen ohne Aufschlag ab. Wie du das vermeidest und was der Oberste Gerichtshof zu den Entgelten von card complete entschieden hat, steht im Ratgeber <a href="../fremdwaehrung/">Gebühren im Ausland verstehen</a>.</p></div>'),
            ('Die besten Karten je Netz',net_best+f'<p class="note">Je Netz die drei am besten bewerteten Privatkarten aus unserem Vergleich. <a class="lnk" href="{best}">Alle Bestenlisten →</a></p>'),
            ('Amex und Diners Club: wann sich ein zweites Netz lohnt','<div class="prose"><p>American Express sammelt Membership Rewards, die sich zu Miles &amp; More, Flying Blue oder Hotelprogrammen übertragen lassen. Die Platinum Card bringt Lounge-Zugang und Reiseguthaben, kostet aber 690 € im Jahr. Diners Club bietet ein Bonusprogramm mit Meilen-Transfer, bei manchen Varianten Lounge-Zugang und ab Gold Reiseversicherungen. Beide lohnen sich für Leute, die viel mit der Karte zahlen und die Prämien gezielt einlösen. Ob die Rechnung aufgeht, steht im Ratgeber <a href="../punkte-sammeln-at/">Lohnt sich Punktesammeln in Österreich?</a>.</p><p>Für den Alltag empfiehlt sich die Kombination: eine gebührenfreie Visa oder Mastercard als Hauptkarte, dazu Amex oder Diners für Punkte und Versicherung. So bist du an jedem Terminal zahlungsfähig und sammelst trotzdem.</p></div>'),
            ('Welches Netz für welche Reise','<div class="prose"><ul><li><b>Euroraum:</b> egal, Visa und Mastercard kosten in Euro nichts extra.</li><li><b>USA und Kanada:</b> Visa, Mastercard, Amex und Diners (über Discover) werden gleich gut angenommen. Achte nur auf das Bearbeitungsentgelt.</li><li><b>Südostasien, Südamerika, Afrika:</b> Visa und Mastercard, am Automaten gelegentlich nur eines davon. Zwei Karten aus beiden Netzen sind die sicherste Lösung.</li><li><b>Niederlande und Deutschland:</b> Dort nehmen viele kleine Händler nur die nationale Debitkarte. Mit Visa oder Mastercard kommst du durch, mit Amex seltener.</li></ul></div>')],
      faq=[('Ist in Österreich Visa oder Mastercard besser?','Bei Akzeptanz und Kurs gibt es keinen Unterschied. Entscheidend ist, was die Bank verlangt: Jahresgebühr, Bearbeitungsentgelt und Kosten fürs Beheben.'),
           ('Kann ich beim Antrag das Netz wählen?','Bei card complete, PayLife, Erste Bank und BAWAG ja, zu gleichen Konditionen. Bank Austria, Raiffeisen, Advanzia und TF Bank geben nur Mastercard aus.'),
           ('Nimmt in Österreich jeder American Express?','Nein. Große Ketten, Hotels, Tankstellen und viele Restaurants ja, kleinere Geschäfte und Lokale oft nicht. Amex-Nutzer brauchen eine zweite Karte.'),
           ('Wie gut wird Diners Club akzeptiert?','In Österreich sehr gut, laut Diners Club bei über 100.000 Stellen. Im Ausland läuft die Karte über das Discover-Netz, das außerhalb Nordamerikas lückenhaft ist.'),
           ('Lohnt sich American Express trotzdem?','Für Vielzahler und Vielreisende oft ja: Membership Rewards, Guthaben und Versicherungen können die Jahresgebühr aufwiegen. Als einzige Karte ist sie wegen der Akzeptanz nicht ideal.')],
      related=['fremdwaehrung',WHY_AMEX['at'][0],'kostenlose-kreditkarte'])
    else:
      art('de','visa-mastercard-amex',
      h1='Visa, Mastercard oder American Express?',
      mt='Visa, Mastercard oder Amex in Deutschland? | Finvallo',
      desc=f'Visa, Mastercard oder American Express in Deutschland: Akzeptanz neben der girocard, Wechselkurse, Auslandseinsatzentgelt und wer welche Karte ausgibt, mit {len(C)} Karten im Vergleich.',
      lede='In Deutschland steht die girocard im Weg, nicht das Netz. Was Visa, Mastercard und Amex im Handel, online und im Ausland unterscheidet.',
      kurz=f'Visa und Mastercard werden in Deutschland an fast allen Terminals angenommen, die überhaupt Kreditkarten nehmen. Die eigentliche Lücke sind Bäcker, Kioske und kleine Läden, die nur girocard akzeptieren. Welches Netz du bekommst, hängt von der Bank ab: DKB, ING, Hanseatic und Barclays geben Visa aus, Advanzia, TF Bank, Deutsche Bank und Postbank Mastercard, Sparkassen und Commerzbank lassen dich wählen. American Express wird seltener angenommen und verlangt {amex_fx_txt} in fremder Währung, bringt aber Punkte, Payback und Versicherungen.',
      secs=[('Akzeptanz in Deutschland: die girocard steht dazwischen','<div class="prose"><p>Laut der Bundesbank-Studie zum Zahlungsverhalten besitzen 98 % der Erwachsenen in Deutschland eine Debitkarte, meist die girocard, aber nur jeder Zweite eine Kreditkarte. Entsprechend haben sich die Terminals entwickelt: Supermärkte, Drogerien, Tankstellen, Baumärkte und alle großen Ketten nehmen inzwischen Visa und Mastercard, auch Aldi und Lidl. Beim Bäcker, im Kiosk, in vielen Arztpraxen und auf Wochenmärkten läuft dagegen oft nur die girocard oder Bargeld. Zwischen Visa und Mastercard gibt es dabei keinen Unterschied: Ein Terminal, das eines nimmt, nimmt auch das andere.</p><p>American Express hat in den letzten Jahren aufgeholt. Edeka, Rewe, Aldi, Lidl, dm, Aral und die meisten Hotels und Airlines nehmen die Karte an. Bei kleineren Händlern und in der Gastronomie bleibt sie wegen der höheren Händlergebühren oft außen vor. Wer Amex nutzt, braucht eine Visa oder Mastercard als Reserve.</p></div>'),
            ('Wer in Deutschland welche Karte ausgibt','<div class="prose"><ul><li><b>Visa:</b> DKB, ING, comdirect, Consorsbank, Hanseatic Bank, Barclays, Bank Norwegian, Openbank, Eurowings, ADAC, Amazon und TARGOBANK.</li><li><b>Mastercard:</b> Advanzia, TF Bank, Deutsche Bank, Postbank, norisbank, HypoVereinsbank, N26, C24, Miles &amp; More, Hilton Honors und die WEB.Cent-Karte.</li><li><b>Visa oder Mastercard wählbar:</b> Sparkassen, Commerzbank, Revolut und Wise.</li><li><b>American Express:</b> gibt die Karten selbst aus, dazu kommen die Payback American Express und die BMW Card.</li></ul><p>Diners Club ist in Deutschland selten geworden und fehlt deshalb in unserem Vergleich.</p></div>'),
            (f'So verteilen sich die {len(C)} Karten in unserem Deutschland-Vergleich',nets_tab),
            ('Wechselkurse und Auslandseinsatzentgelt','<div class="prose"><p>Zahlst du in Dollar, Pfund oder Franken, rechnet das Netz zum eigenen Tageskurs um. Visa und Mastercard liegen dabei dicht beieinander, meist weniger als 0,5 % auseinander, mal ist das eine günstiger, mal das andere. Was den Unterschied macht, ist das Auslandseinsatzentgelt der Bank: Sparkassen, Volksbanken, Deutsche Bank und Postbank verlangen 1,75 bis 2,35 %, American Express 2 %, DKB und ING bei der Debitkarte 2,2 %. Advanzia, TF Bank, Hanseatic, Bank Norwegian und viele Gold-Karten verlangen 0 %. Was im Ausland noch dazukommt und wie du die Falle „in Euro zahlen“ umgehst, steht im Ratgeber <a href="../fremdwaehrung/">Gebühren im Ausland verstehen</a>.</p></div>'),
            ('Die besten Karten je Netz',net_best+f'<p class="note">Je Netz die drei am besten bewerteten Privatkarten aus unserem Vergleich. <a class="lnk" href="{best}">Alle Bestenlisten →</a></p>'),
            ('Debit oder Kredit: das Logo allein sagt es nicht','<div class="prose"><p>In Deutschland tragen immer mehr Karten das Visa- oder Mastercard-Logo, sind aber Debitkarten: die DKB Visa Debitkarte, die ING VISA Card, die comdirect Visa-Debitkarte, N26 und Trade Republic. Beim Bezahlen merkst du keinen Unterschied. Hotels, Autovermieter und manche Online-Shops schon: Sie lesen das Wort „Debit“ auf der Karte und lehnen sie für Kautionen ab oder verlangen einen Aufschlag. Wer eine Karte für Mietwagen braucht, sollte auf den Typ achten, nicht auf das Netz. Mehr dazu im Ratgeber <a href="../kartentypen/">Kredit-, Charge-, Debit- oder Prepaid-Karte</a>.</p></div>'),
            ('American Express in Deutschland: für wen','<div class="prose"><p>Amex lebt von Zusatzleistungen. Die Payback American Express ist kostenlos und sammelt Payback-Punkte bei jedem Einkauf, auch außerhalb der Partner. Gold und Platinum bringen Membership Rewards, Reiseversicherungen, bei Platinum Lounge-Zugang und Guthaben, kosten aber 240 beziehungsweise 720 € im Jahr. Das lohnt sich für Leute, die viel über die Karte laufen lassen und Punkte gezielt in Flüge tauschen. Für alle anderen bleibt die Rechnung aus dem Ratgeber <a href="../punkte-sammeln-de/">Lohnt sich Punktesammeln in Deutschland?</a>: Eine gebührenfreie Visa oder Mastercard als Hauptkarte, Amex als Zweitkarte für Punkte.</p></div>')],
      faq=[('Ist in Deutschland Visa oder Mastercard besser?','Nein. Akzeptanz und Kurs sind praktisch gleich. Entscheidend sind Jahresgebühr, Auslandseinsatzentgelt und Abhebungskosten der Bank.'),
           ('Warum nehmen viele kleine Läden keine Kreditkarte?','Weil die girocard für Händler günstiger ist und fast jeder Kunde eine hat. Kreditkarten kosten den Händler mehr Gebühr, Amex noch einmal mehr als Visa und Mastercard.'),
           ('Nimmt Aldi oder Lidl American Express?','Ja, die großen Supermärkte und Discounter nehmen inzwischen Amex an. Kleinere Händler und die Gastronomie oft nicht.'),
           ('Kann ich beim Antrag das Netz wählen?','Bei Sparkassen, Commerzbank, Revolut und Wise ja. DKB, ING, Hanseatic, Barclays, Advanzia und TF Bank geben nur ein Netz aus.'),
           ('Lohnt sich American Express trotzdem?','Für Vielzahler oft ja: Payback-Punkte oder Membership Rewards, Versicherungen und Guthaben können die Jahresgebühr aufwiegen. Als einzige Karte ist sie wegen der Akzeptanz nicht ideal.')],
      related=['fremdwaehrung',WHY_AMEX['de'][0],'kostenlose-kreditkarte'])
    # E) Mietwagen & Kaution
    # Mietwagen-Schutz nur aus geprüften Profilen (tools/daten/mietwagen.json), dieselbe Quelle wie die Kartenseiten
    MW=mietwagen(land); bys={c['slug']:c for c in C}
    rent=sorted([bys[k] for k in MW if k in bys and not MW[k].get('optional')],key=lambda c:(c['fee'] if c['fee'] is not None else 1e9))
    opt=[bys[k] for k in MW if k in bys and MW[k].get('optional')]
    kau=sorted([c for c in credit if re.search(r'visa|mastercard',c['netz'],re.I)],key=lambda c:(c['fee'] if c['fee'] is not None else 1e9,-(c.get('stars') or 0)))
    NL='nicht ausgewiesen'
    mcols=[COL['karte'],COL['fee'],('Art',lambda c,P:E(' + '.join(MWART[a] for a in MW[c['slug']]['art']))),
           ('Kasko',lambda c,P:E(MW[c['slug']].get('kasko') or NL)),('Selbstbeteiligung',lambda c,P:E(MW[c['slug']].get('sb') or NL)),
           ('Haftpflicht',lambda c,P:E(MW[c['slug']].get('haft') or NL)),('Eigenanteil',lambda c,P:E(MW[c['slug']].get('eigenanteil') or '')),
           ('Mietdauer',lambda c,P:E(MW[c['slug']].get('dauer') or '')),('Voraussetzungen',lambda c,P:E(MW[c['slug']].get('bedingungen') or ''))]
    kau_tab=(table(kau[:10],[COL['karte'],COL['typ'],COL['netz'],COL['fee']],P)+f'<p class="note">Kredit- und Charge-Karten mit Visa oder Mastercard, also mit Kreditrahmen und der breitesten Akzeptanz, sortiert nach Jahresgebühr. Hier stehen die 10 günstigsten der {len(kau)} passenden aus unserem {N}-Vergleich. Eine allgemeine Annahmegarantie gibt es nicht.</p>') if kau else '<p>Aktuell keine passende Karte in unserem Vergleich.</p>'
    rent_tab=(table(rent,mcols,P)+'<p class="note">Nur Karten, deren Versicherungsbedingungen wir für den Mietwagen geprüft haben, sortiert nach Jahresgebühr. Fehlt eine Karte, heißt das nicht, dass sie keinen Schutz hat. Die genauen Bedingungen und die Quelle stehen auf jeder Kartenseite.</p>'+((f'<p class="note"><b>Nur gegen Aufpreis:</b> '+'; '.join(f'{link(c,P)} ({E(MW[c["slug"]]["optional"])}, {E(MW[c["slug"]].get("sb") or "")})' for c in opt)+'.</p>') if opt else '')) if rent else '<p>Aktuell keine Karte mit bestätigtem Mietwagenschutz in unserem Vergleich.</p>'
    rent_n=('eine' if len(rent)==1 else str(len(rent)))+(f', am günstigsten die {rent[0]["titel"]}' if rent else '')
    if land=='at':
      art('at','mietwagen-kaution',
      h1='Kreditkarte für Mietwagen: Kaution und Versicherung',
      mt='Kreditkarte für Mietwagen: Kaution (Österreich) | Finvallo',
      desc=f'Mietwagen mit Kreditkarte aus Österreich: wie die Kaution reserviert wird, warum die Bankomatkarte oft nicht reicht und welche der {len(C)} Karten im Vergleich Kasko oder Selbstbehalt abdecken.',
      lede='Zwei Fragen, die du vor der Abholung getrennt klären musst: Nimmt die Station deine Karte für die Kaution? Und was deckt die Versicherung deiner Karte beim Mietwagen wirklich ab?',
      kurz=f'Für die Kaution brauchst du in der Regel eine Kredit- oder Charge-Karte mit Visa oder Mastercard auf den Namen des Hauptfahrers, in Österreich also zum Beispiel die Karte der Hausbank, von card complete oder PayLife. Die Bankomatkarte und Neobank-Debitkarten nehmen viele Stationen nicht oder nur für kleine Fahrzeugklassen. Versicherung ist eine zweite Frage: {rent_n} der Karten in unserem Österreich-Vergleich hat einen von uns geprüften Mietwagenschutz ohne Aufpreis. Ein „umfassender Reiseschutz“ sagt darüber nichts aus.',
      secs=[('Kaution, Kasko, Selbstbehalt: die Begriffe','<div class="prose"><p><b>Kaution:</b> Sicherheitsleistung, die der Vermieter bei der Abholung auf deiner Karte reserviert. Sie deckt Tankkosten, Mautgebühren, Strafen und den Selbstbehalt bei Schäden. Eine Kartenversicherung ersetzt sie nicht.</p><p><b>Kasko:</b> Schutz bei Schäden am Mietwagen oder Diebstahl. Beim Vermieter heißt sie meist CDW oder Vollkasko und hat einen Selbstbehalt von oft 500 bis 2.000 €.</p><p><b>Selbstbehalt-Schutz</b> (in den Kartenbedingungen oft Selbstbeteiligungsschutz): Deine Karte erstattet den Selbstbehalt, den du dem Vermieter gezahlt hast. Dafür musst du dessen Kasko behalten.</p><p><b>Zusatzhaftpflicht:</b> erhöht die Deckung für Schäden an Dritten. In Österreich und der EU ist eine Haftpflicht im Mietpreis enthalten, in den USA oft nur mit niedriger Summe.</p></div>'),
            ('So läuft die Kaution bei österreichischen Vermietern','<div class="prose"><p>Ob am Flughafen Wien, in Salzburg oder bei einer Station von Sixt, Europcar, Hertz, Avis oder Buchbinder: Beim Abholen reserviert der Vermieter einen Betrag auf deiner Karte, meist 300 bis 1.500 €, bei Premiumautos mehr, dazu oft eine Tankkaution. Bei einer Charge- oder Kreditkarte wird nichts abgebucht, aber dein Rahmen ist um diesen Betrag kleiner. Nach der Rückgabe gibt der Vermieter die Reservierung frei. Deine Bank muss den Betrag nach dem Zahlungsdienstegesetz unverzüglich freigeben, sobald sie den endgültigen Betrag kennt. In der Praxis dauert das einige Tage bis zwei Wochen, weil Vermieter die Freigabe oft erst nach der Endabrechnung schicken.</p><p>Wichtig ist der freie Rahmen: Bei einer Classic-Karte mit 1.500 € Rahmen ist nach der Kaution kaum noch Platz für Hotel und Tanken. Lass den Rahmen vor der Reise erhöhen oder nimm eine zweite Karte mit.</p></div>'),
            ('Bankomatkarte und Debitkarte: was in Österreich geht','<div class="prose"><p>Die Bankomatkarte ist seit 2023 eine Debit Mastercard oder Visa Debit und sieht einer Kreditkarte ähnlich. Für die Kaution behandeln Vermieter sie trotzdem anders: Der Betrag wird nicht reserviert, sondern vom Konto abgebucht und erst nach der Rückgabe zurücküberwiesen. Manche Stationen in Österreich nehmen sie für Klein- und Mittelklassewagen, andere nur mit gebuchter Vollkasko ohne Selbstbehalt, im Ausland lehnen viele sie ab. Karten von N26, Revolut oder bunq schließen manche Vermieter ausdrücklich aus, weil sie Karten von „Online-Banken“ nicht als Sicherheit akzeptieren. Prepaid-Karten wie die card complete Prepaid gehen fast nirgends.</p><p>Deshalb: Prüfe vor der Buchung die Zahlungsbedingungen des Vermieters für die konkrete Station und Fahrzeugklasse, nicht nur den Filter des Vergleichsportals.</p></div>'),
            ('Karten, die für Kautionen geeignet sind',kau_tab),
            ('Karten mit bestätigtem Mietwagenschutz in unserer Recherche',rent_tab),
            ('Was die Kartenversicherung aus Österreich meist nicht deckt','<div class="prose"><ul><li>Wohnmobile, Motorräder, Transporter und Luxusklassen sind fast immer ausgeschlossen.</li><li>Fahrer, die nicht im Mietvertrag stehen, und Fahrten unter Alkohol.</li><li>Reifen, Glas, Unterboden und Dach bei manchen Bedingungen, Innenraum fast immer.</li><li>Mieten über die Höchstdauer hinaus, oft 30 oder 31 Tage.</li><li>Mietwagen, die nicht mit der Karte bezahlt wurden. Die meisten Bedingungen verlangen die Zahlung der Miete mit genau dieser Karte.</li><li>Mietwagen im Wohnort oder in Österreich, wenn die Versicherung nur „auf Reisen“ gilt.</li></ul><p>Lies die Bedingungen der Karte, bevor du die Vermieterversicherung ablehnst. Im Zweifel ist die Vollkasko ohne Selbstbehalt beim Vermieter teurer, aber ohne Streit im Schadensfall.</p></div>'),
            ('Checkliste vor der Abholung','<div class="prose"><ul><li>Nimmt die Station deine Kartenmarke und deinen Kartentyp für die Kaution an?</li><li>Physische Karte auf den Namen des Hauptfahrers, keine Wallet-Karte</li><li>Freier Rahmen für Kaution plus Tankkaution plus Reiseausgaben</li><li>Mietdauer innerhalb der Grenze deiner Kartenversicherung</li><li>Fahrzeugklasse nicht ausgeschlossen</li><li>Alle Fahrer im Mietvertrag eingetragen</li><li>Vermieterkasko gebucht, wenn deine Karte nur den Selbstbehalt erstattet</li><li>Miete mit der versicherten Karte bezahlt</li><li>Land und Entfernung vom Wohnort passen zu den Bedingungen</li><li>Fotos bei Abholung und Rückgabe, Schäden sofort melden</li></ul></div>')],
      faq=[('Reicht die Bankomatkarte für die Mietwagen-Kaution?','In Österreich bei manchen Stationen für kleinere Fahrzeugklassen, im Ausland selten. Der Betrag wird abgebucht statt reserviert. Sicher ist nur eine Kredit- oder Charge-Karte mit Rahmen.'),
           ('Ist eine Reiseversicherung automatisch eine Mietwagen-Vollkasko?','Nein. Reiseversicherung ist ein Sammelbegriff. Ob Kasko, Selbstbehalt-Schutz oder Zusatzhaftpflicht enthalten sind, steht nur in den Bedingungen der konkreten Karte.'),
           ('Kann ich die Versicherung des Vermieters immer ablehnen?','Nein. Ein Selbstbehalt-Schutz setzt die Kasko des Vermieters voraus. Nur Karten mit eigener Kasko erlauben den Verzicht, und auch dort nur innerhalb ihrer Bedingungen.'),
           ('Muss ich den Mietwagen mit der versicherten Karte bezahlen?','Bei den meisten Karten ja, sonst gilt der Schutz nicht. Revolut nennt für den Mietwagen selbst keine Zahlungspflicht. Prüfe das vor der Buchung.'),
           ('Wie lange ist die Kaution blockiert?','Der Vermieter gibt sie nach der Rückgabe frei, die Bank muss sie dann unverzüglich entsperren. In der Praxis dauert das einige Tage bis zwei Wochen. Bei Debitkarten wird das Geld zurücküberwiesen, das kann länger dauern.')],
      related=['reiseversicherung','kartentypen','visa-mastercard-amex'])
    else:
      art('de','mietwagen-kaution',
      h1='Kreditkarte für Mietwagen: Kaution und Versicherung',
      mt='Kreditkarte für Mietwagen: Kaution (Deutschland) | Finvallo',
      desc=f'Mietwagen mit Kreditkarte aus Deutschland: wie Sixt, Europcar und Co. die Kaution reservieren, was girocard und Debit-Visa taugen und welche der {len(C)} Karten im Vergleich Kasko oder Selbstbeteiligung abdecken.',
      lede='Zwei Fragen, die du vor der Abholung getrennt klären musst: Nimmt die Station deine Karte für die Kaution? Und was deckt die Versicherung deiner Karte beim Mietwagen wirklich ab?',
      kurz=f'Für die Kaution verlangen die meisten Vermieter eine Kredit- oder Charge-Karte mit Visa oder Mastercard auf den Namen des Hauptfahrers. Die girocard geht nur bei wenigen Stationen in Deutschland, Visa Debitkarten von DKB, ING oder N26 nehmen Sixt und Europcar im Inland für bestimmte Fahrzeugklassen, im Ausland meist nicht. Versicherung ist eine zweite Frage: {rent_n} der Karten in unserem Deutschland-Vergleich hat einen von uns geprüften Mietwagenschutz ohne Aufpreis. Ein „umfassender Reiseschutz“ sagt darüber nichts aus.',
      secs=[('Kaution, Kasko, Selbstbeteiligung: die Begriffe','<div class="prose"><p><b>Kaution:</b> Sicherheitsleistung, die der Vermieter bei der Abholung auf deiner Karte reserviert. Laut <a class="lnk" href="https://www.sixt.de/faqs/mietwagen-ohne-kreditkarte" target="_blank" rel="noopener">Sixt</a> deckt sie offene Posten wie Tankkosten, verspätete Rückgabe oder Extras, nicht die Schadenforderung selbst. Eine Kartenversicherung ersetzt sie nicht.</p><p><b>Kasko (CDW):</b> Schutz bei Schäden am Mietwagen oder Diebstahl, beim Vermieter meist mit Selbstbeteiligung von 500 bis 2.000 €. <b>Selbstbeteiligungsschutz:</b> Deine Karte erstattet die Selbstbeteiligung, die du dem Vermieter gezahlt hast; sie setzt dessen Kasko voraus. <b>Zusatzhaftpflicht:</b> erhöht die Deckung für Schäden an Dritten. In Deutschland und der EU ist die Haftpflicht im Mietpreis enthalten, in den USA oft nur mit niedriger Summe. Die Mallorca-Police deiner eigenen Kfz-Versicherung erhöht sie in Europa, nicht die Kartenversicherung.</p></div>'),
            ('Kaution bei Sixt, Europcar und Co.','<div class="prose"><p>Bei der Abholung autorisiert der Vermieter einen Betrag auf deiner Karte. Die Höhe richtet sich nach Fahrzeuggruppe und Mietpreis, bei Sixt steht sie im Buchungsprozess, bei Europcar und Hertz in den Mietbedingungen, meist 300 bis 1.500 €, bei Premiumautos mehr. Bei einer Kreditkarte ist das keine Zahlung, sondern eine Reservierung: Nichts wird abgebucht, aber dein Verfügungsrahmen sinkt. Nach der Rückgabe gibt der Vermieter die Reservierung frei, die Bank muss den Betrag dann unverzüglich entsperren. Sixt nennt 5 bis 10 Werktage, oft geht es schneller.</p><p>Immer mehr Stationen verlangen am Schalter die PIN der Kreditkarte statt einer Unterschrift. Die <a class="lnk" href="https://www.adac.de/produkte/finanzdienstleistungen/finanzratgeber/kreditkarte-beim-mietwagen/" target="_blank" rel="noopener">ADAC-Übersicht</a> erklärt, worauf die großen Vermieter achten. Plane den Rahmen großzügig: Kaution, Tankkaution und Hotelreservierung laufen gleichzeitig über dieselbe Karte.</p></div>'),
            ('girocard, Debit-Visa und Prepaid: was Vermieter annehmen','<div class="prose"><p>Die girocard ist in Deutschland bei fast keiner Station als Kaution möglich, im Ausland nie. Debitkarten mit Visa- oder Mastercard-Logo, etwa von DKB, ING, comdirect oder N26, nehmen Sixt und Europcar im Inland für Klein- bis obere Mittelklasse, nicht für SUV, Premium oder Transporter. Der Betrag wird dabei abgebucht und nach der Rückgabe zurücküberwiesen, dein Kontoguthaben ist so lange weg. Im Ausland akzeptieren viele Stationen Debitkarten gar nicht, auch wenn das Vergleichsportal „Kaution mit Debitkarte möglich“ anzeigt. Genau darum geht es in einer <a class="lnk" href="https://www.verbraucherzentrale.de/verbandsklagen/klage-gegen-check-24-125022" target="_blank" rel="noopener">Verbandsklage der Verbraucherzentrale gegen Check24</a>. Prepaid-Karten wie die Sparkasse Visa Card Basis gehen fast nirgends.</p><p>Prüfe deshalb die Zahlungsbedingungen des Vermieters für die konkrete Station und Fahrzeugklasse, nicht nur den Portal-Filter. Wenn du nur eine Debitkarte hast, ist eine gebührenfreie Kreditkarte mit Rahmen die einfachste Lösung, siehe <a href="../kostenlose-kreditkarte/">kostenlose Kreditkarte</a>.</p></div>'),
            ('Karten, die für Kautionen geeignet sind',kau_tab),
            ('Karten mit bestätigtem Mietwagenschutz in unserer Recherche',rent_tab),
            ('Was die Kartenversicherung aus Deutschland meist nicht deckt','<div class="prose"><ul><li>Wohnmobile, Motorräder, Transporter, Oldtimer und Luxusklassen.</li><li>Fahrer, die nicht im Mietvertrag stehen, und Fahrten unter Alkohol oder abseits befestigter Straßen.</li><li>Reifen, Glas, Unterboden und Dach bei vielen Bedingungen, Innenraum fast immer.</li><li>Mieten über die Höchstdauer hinaus, meist 30 oder 31 Tage am Stück.</li><li>Mietwagen, die nicht mit der versicherten Karte bezahlt wurden.</li><li>Anmietungen am Wohnort, wenn der Schutz nur auf Reisen ab einer Mindestentfernung gilt.</li><li>Die Haftpflicht gegenüber Dritten: Kartenversicherungen zahlen fast nur für den Mietwagen selbst.</li></ul><p>Lies die Bedingungen der Karte, bevor du die Vermieterversicherung ablehnst. Externe Selbstbeteiligungs-Versicherungen für 20 bis 60 € pro Jahr sind oft die günstigere Ergänzung als die Vollkasko ohne Selbstbeteiligung am Schalter.</p></div>'),
            ('Checkliste vor der Abholung','<div class="prose"><ul><li>Nimmt die Station deine Kartenmarke und deinen Kartentyp für die Kaution an?</li><li>Physische Karte auf den Namen des Hauptfahrers, PIN bekannt</li><li>Freier Rahmen für Kaution plus Tankkaution plus Reiseausgaben</li><li>Mietdauer innerhalb der Grenze deiner Kartenversicherung</li><li>Fahrzeugklasse nicht ausgeschlossen</li><li>Alle Fahrer im Mietvertrag eingetragen</li><li>Vermieterkasko gebucht, wenn deine Karte nur die Selbstbeteiligung erstattet</li><li>Miete mit der versicherten Karte bezahlt</li><li>Land und Entfernung vom Wohnort passen zu den Bedingungen</li><li>Fotos bei Abholung und Rückgabe, Schäden sofort melden</li></ul></div>')],
      faq=[('Kann ich die Kaution mit der girocard oder einer Debitkarte hinterlegen?','Mit der girocard fast nie. Mit Visa Debit oder Debit Mastercard bei Sixt und Europcar im Inland für bestimmte Fahrzeugklassen, der Betrag wird dann abgebucht statt reserviert. Im Ausland verlangen die meisten Stationen eine echte Kreditkarte.'),
           ('Ist eine Reiseversicherung automatisch eine Mietwagen-Vollkasko?','Nein. Reiseversicherung ist ein Sammelbegriff. Ob Kasko, Selbstbeteiligungsschutz oder Zusatzhaftpflicht enthalten sind, steht nur in den Bedingungen der konkreten Karte.'),
           ('Kann ich die Versicherung des Vermieters immer ablehnen?','Nein. Ein Selbstbeteiligungsschutz setzt die Kasko des Vermieters voraus. Nur Karten mit eigener Kasko erlauben den Verzicht, und auch dort nur innerhalb ihrer Bedingungen.'),
           ('Muss ich den Mietwagen mit der versicherten Karte bezahlen?','Bei den meisten Karten ja, sonst gilt der Schutz nicht. Revolut nennt für den Mietwagen selbst keine Zahlungspflicht. Prüfe das vor der Buchung.'),
           ('Wie lange ist die Kaution blockiert?','Nach der Rückgabe gibt der Vermieter die Reservierung frei, die Bank muss sie dann unverzüglich aufheben. Sixt nennt 5 bis 10 Werktage. Bei Debitkarten wird das Geld zurücküberwiesen, das kann länger dauern.')],
      related=['reiseversicherung','kartentypen','visa-mastercard-amex'])
    if land=='at':
        # AT-Fremdwährung mit derselben Struktur wie DE; Werte aus den Kartendaten
        HB=('Bank Austria Classic','Erste Bank und Sparkassen Smartcard','Raiffeisen Classic','BAWAG Weiß','card complete Classic ohne Versicherung')
        hb=[c for c in C if c['titel'] in HB]
        fx0=[c for c in credit if c['fx']==0][:10]
        fxs=sorted(c['fx'] for c in hb if c['fx'])
        art('at','fremdwaehrung',h1='Gebühren im Ausland verstehen',mt='Kreditkarte im Ausland: Gebühren verstehen (AT) | Finvallo',
          desc='Bearbeitungsentgelt, Kursaufschlag und die Falle „in Euro zahlen“: So vermeidest du unnötige Gebühren mit der Kreditkarte, wenn du aus Österreich verreist.',
          lede='Bearbeitungsentgelt, Kursaufschlag und die Falle „in Euro zahlen“.',
          kurz=f'Innerhalb des Euroraums kostet das Zahlen mit der Karte nichts extra. Außerhalb verlangen die Karten der großen österreichischen Banken in unserem Vergleich {pct(fxs[0])} bis {pct(fxs[-1])}. {len([c for c in credit if c["fx"]==0])} Kredit- und Charge-Karten in unserem Vergleich verlangen dafür 0 %.' if fxs else None,
          secs=[('Was beim Zahlen in Fremdwährung anfällt','<div class="prose"><p>Zahlst du in einer fremden Währung, verlangen viele Banken zwei Dinge: ein Bearbeitungsentgelt, oft 1,5 bis 1,65 %, und einen Aufschlag auf den Wechselkurs, in unserem Vergleich 1 bis 1,5 %. Zusammen sind das schnell 2,5 bis über 3 %. Achte deshalb immer auf beides.</p></div><div class="cond"><div class="r"><span>Urlaub in den USA, 1.000 € Ausgaben</span> <span></span></div><div class="r"><span>Karte mit 0 %</span> <span>0 €</span></div><div class="r"><span>Karte mit 1,5 %</span> <span>15 €</span></div><div class="r"><span>Karte mit 1,65 % + 1,5 %</span> <span>31,50 €</span></div></div>'),
                ('Typische Gebühren bei Hausbanken',table(hb,[COL['karte'],COL['fee'],COL['fx'],COL['cash']],P)+'<p class="note">Je Bank die günstigste Standardkarte aus unserem Vergleich. Wo ein Kursaufschlag dazukommt, steht er dabei. In unserer Bewertung zählt die Summe aus Entgelt und Aufschlag.</p>' if hb else ''),
                ('Karten ohne Auslandsgebühr',table(fx0,[COL['karte'],COL['fee'],COL['cash'],COL['stars']],P)+f'<p class="note"><a class="lnk" href="{best}ausland/">Zur Bestenliste: ohne Auslandsgebühr →</a></p>'),
                ('Die Falle „in Euro zahlen?“','<div class="info"><span class="ic">!</span><div><p style="margin:0">Fragt dich ein Terminal oder Geldautomat im Ausland, ob du in Euro statt in der Landeswährung zahlen willst, lehne ab. Bei der Umrechnung durch den Händler ist der Kurs fast immer schlechter als bei deiner Bank.</p></div></div>'),
                ('Bargeld im Ausland','<div class="prose"><p>Beim Beheben im Ausland fallen bis zu drei Kosten an: das Bearbeitungsentgelt für die Fremdwährung, eine Bargeldgebühr deiner Bank und eine Gebühr des Automatenbetreibers. Viele gebührenfreie Karten erstatten nur die eigenen Gebühren, nicht die des Betreibers. Was jede Karte für das Beheben verlangt, steht in den Tabellen oben und auf der jeweiligen Kartenseite.</p></div>'),
                ('Das Urteil zu card complete','<div class="prose"><p>Der Oberste Gerichtshof hat 2026 entschieden, dass card complete Bearbeitungsentgelt und Kursaufschlag in älteren Verträgen nicht doppelt verrechnen durfte. Die Arbeiterkammer sieht ein ähnliches Muster bei PayLife und BAWAG Rückerstattungen konnten laut <a class="lnk" href="https://wien.arbeiterkammer.at/cardcomplete" target="_blank" rel="noopener">Arbeiterkammer</a> bis 1. August 2026 beantragt werden; diese Frist ist abgelaufen.</p></div>')],
          faq=[('Kostet das Zahlen mit Kreditkarte in Euro-Ländern extra?','Nein. Zahlungen in Euro innerhalb des Euroraums kosten wie im Inland, meist also nichts.'),
               ('Wie hoch ist die Gebühr für Fremdwährung bei österreichischen Banken?',f'Bei den Standardkarten der großen Banken in unserem Vergleich {pct(fxs[0])} bis {pct(fxs[-1])}, je nachdem ob ein Kursaufschlag dazukommt. Karten ohne Auslandsgebühr verlangen 0 %.' if fxs else 'Das hängt von der Bank ab.'),
               ('Soll ich am Automaten im Ausland Euro oder Landeswährung wählen?','Immer die Landeswährung. Die Umrechnung in Euro durch den Automaten ist fast immer teurer.')],
          related=['kostenlose-kreditkarte','visa-mastercard-amex','reiseversicherung'])
        # Reiseversicherung und Flugverspätung/Gepäck (nur AT): Texte und Tabellen in ratgeber_reise.py
        import karten, ratgeber_reise
        ratgeber_reise.register(art,P,best,cards.D['at'][0],karten.card_count('at','private'),eur)
        import ratgeber_bargeld; ratgeber_bargeld.register(art,P,best,cards.D['at'][0],karten.card_count('at','private'),eur,karten)
        import ratgeber_studenten; ratgeber_studenten.register(art,P,best,cards.D['at'][0],karten.card_count('at','private'),eur,karten)
        import ratgeber_wallet; ratgeber_wallet.register(art,P,best,cards.D['at'][0],karten.card_count('at','private'),eur,karten)
        import ratgeber_girokonto; ratgeber_girokonto.register(art,P,eur)
        import ratgeber_konto; ratgeber_konto.register(art,P,eur)
        import ratgeber_festgeld; ratgeber_festgeld.register(art,P,eur)
    if land=='de':
        import karten, ratgeber_bargeld_de
        ratgeber_bargeld_de.register(art,P,best,cards.D['de'][0],karten.card_count('de','private'),eur,karten)
        import ratgeber_reise_de; ratgeber_reise_de.register(art,P,best,cards.D['de'][0],karten.card_count('de','private'),eur,karten)
        import ratgeber_studenten_de; ratgeber_studenten_de.register(art,P,best,cards.D['de'][0],karten.card_count('de','private'),eur,karten)
        import ratgeber_wallet_de; ratgeber_wallet_de.register(art,P,best,cards.D['de'][0],karten.card_count('de','private'),eur,karten)
        import ratgeber_girokonto_de; ratgeber_girokonto_de.register(art,P,eur)
        import ratgeber_konto_de; ratgeber_konto_de.register(art,P,eur)
        import ratgeber_festgeld_de; ratgeber_festgeld_de.register(art,P,eur)
        lou=[c for c in RC if c['lg']]
        art('de','lounges',h1='Lounge-Zugang mit der Kreditkarte',mt='Lounge-Zugang mit Kreditkarte in Deutschland: Bedingungen und Gäste | Finvallo',
          desc='Welche Kreditkarten in Deutschland kostenlosen Zugang zu Flughafen-Lounges geben: Priority Pass, Besuche pro Jahr und Begleitpersonen.',
          lede='Welche Karten dich in Deutschland wirklich gratis in die Lounge bringen.',
          kurz=f'Nur {len(lou)} Privatkarten in unserem Deutschland-Vergleich enthalten kostenlose Lounge-Besuche, darunter {fmtlist([c["titel"] for c in lou[:3]])}. Viele andere Karten bieten nur eine Priority-Pass-Mitgliedschaft, bei der jeder Besuch rund 30 € kostet.',
          secs=[('Mitgliedschaft ist nicht gleich Gratis-Besuch','<div class="prose"><p>Viele Karten werben mit dem Priority Pass. Entscheidend ist, ob die Besuche kostenlos sind. Bei Commerzbank Gold und Premium oder der Postbank Platinum bekommst du nur die Mitgliedschaft und zahlst jeden Besuch. Andere Karten enthalten eine feste Zahl an Gratis-Besuchen oder unbegrenzten Zugang.</p></div>'),
                ('Karten mit kostenlosen Lounge-Besuchen',table(lou,[COL['karte'],COL['lg'],COL['fee']],P)+f'<p class="note"><a class="lnk" href="{best}lounge/">Bestenliste Lounge-Zugang ansehen →</a></p>'),
                ('Darauf musst du achten','<div class="prose"><p>Prüfe, ob Begleitpersonen mitzählen oder extra kosten, ob die Besuche pro Kalender- oder Vertragsjahr gelten und ob ein Mindestumsatz nötig ist.</p></div>')],
          faq=[('Welche Kreditkarte hat unbegrenzten Lounge-Zugang?','In unserem Vergleich zum Beispiel '+fmtlist([c['titel'] for c in lou if re.search(r'nbegrenzt|kostenfrei|Kostenlose',c['lg'] or '')][:3])+'.'),
               ('Was ist der Priority Pass?','Ein Lounge-Programm mit über 1.500 Lounges weltweit. Ob die Besuche kostenlos sind, hängt von deiner Karte ab.')],
          related=['reiseversicherung','punkte-sammeln-de','fremdwaehrung'])
        hb=[c for c in RC if c['titel'] in ('Sparkasse Kreditkarte Classic','Deutsche Bank Mastercard Standard','Postbank Mastercard','Commerzbank ClassicKreditkarte','Volksbank ClassicCard')]
        fx0=[c for c in credit if c['fx']==0][:10]
        art('de','fremdwaehrung',h1='Gebühren im Ausland verstehen',mt='Kreditkarte im Ausland: Gebühren verstehen (DE) | Finvallo',
          desc='Auslandseinsatzentgelt, Wechselkurs und die Falle „in Euro zahlen“: So vermeidest du unnötige Gebühren mit der Kreditkarte, wenn du aus Deutschland verreist.',
          lede='Was eine Zahlung in fremder Währung wirklich kostet und wie du es vermeidest.',
          kurz=f'Innerhalb des Euroraums kostet das Zahlen mit der Karte nichts extra. Außerhalb verlangen viele Hausbanken in Deutschland ein Auslandseinsatzentgelt von etwa 1,75 bis 2,35 %. {len([c for c in credit if c["fx"]==0])} Kredit- und Charge-Karten in unserem Vergleich verlangen dafür 0 %. Wähle am Terminal und Automaten immer die Landeswährung, nicht Euro.',
          secs=[('Was beim Zahlen in Fremdwährung anfällt','<div class="prose"><p>Zahlst du in US-Dollar, Pfund oder Franken, rechnet Visa oder Mastercard zum Tageskurs um. Dazu kommt bei vielen Banken ein <b>Auslandseinsatzentgelt</b> als Prozentsatz vom Betrag. Bei Zahlungen in Euro innerhalb der EU darf die Bank laut EU-Recht nicht mehr verlangen als im Inland.</p></div>'),
                ('Typische Gebühren bei Hausbanken',table(hb,[COL['karte'],COL['fee'],COL['fx'],COL['cash']],P) if hb else ''),
                ('Karten ohne Auslandsgebühr',table(fx0,[COL['karte'],COL['fee'],COL['cash'],COL['stars']],P)+f'<p class="note"><a class="lnk" href="{best}ausland/">Bestenliste ohne Auslandsgebühr →</a></p>'),
                ('Die Falle „in Euro zahlen“','<div class="prose"><p>Im Ausland fragen Terminals und Geldautomaten oft, ob du in Euro oder in Landeswährung zahlen willst. Das heißt dynamische Währungsumrechnung. Wählst du Euro, rechnet der Händler oder Automatenbetreiber zu einem eigenen, meist deutlich schlechteren Kurs um. Wähle deshalb immer die Landeswährung, dann gilt der Kurs von Visa oder Mastercard.</p></div>'),
                ('Bargeld im Ausland','<div class="prose"><p>Beim Abheben fallen bis zu drei Kosten an: das Auslandseinsatzentgelt, eine Bargeldgebühr deiner Bank und eine Gebühr des Automatenbetreibers. Viele gebührenfreie Karten erstatten nur die eigenen Gebühren, nicht die des Betreibers.</p></div>')],
          faq=[('Kostet das Zahlen mit Kreditkarte in Euro-Ländern extra?','Nein. Zahlungen in Euro innerhalb des Euroraums kosten wie im Inland, meist also nichts.'),
               ('Wie hoch ist das Auslandseinsatzentgelt?','Bei Hausbanken meist 1,75 bis 2,35 %, bei American Express 2 %. Viele Direktbanken und Gold-Karten verlangen 0 %.'),
               ('Soll ich am Automaten im Ausland Euro oder Landeswährung wählen?','Immer die Landeswährung. Die Umrechnung in Euro durch den Automaten ist fast immer teurer.')],
          related=['kostenlose-kreditkarte','visa-mastercard-amex','reiseversicherung'])

# ---------- statische Artikel korrigieren, Übersichten, hreflang, Sitemap, llms ----------
DE_FIX={
 'teilzahlung':[('In Österreich liegen diese Zinsen bei den gebührenfreien Karten bei rund 25 % effektiv im Jahr.','In Deutschland liegen diese Zinsen bei den gebührenfreien Karten meist zwischen 18 und 25 % effektiv im Jahr.')],
 'business':[('../../../at/kreditkarten/business/','../../kreditkarten/business/')],
 'reiseversicherung':[('../../../at/kreditkarten/bestenlisten/reisen/','../../kreditkarten/bestenlisten/reisen/')],
}
PAIRS={('at','punkte-sammeln-at'):('de','punkte-sammeln-de'),('de','punkte-sammeln-de'):('at','punkte-sammeln-at'),('at','bargeld-beheben'):('de','bargeld-abheben'),('de','bargeld-abheben'):('at','bargeld-beheben')}
WHY_AMEX={'at':('punkte-sammeln-at','Österreich'),'de':('punkte-sammeln-de','Deutschland')}
def why_amex(land):
    slug,N=WHY_AMEX[land]
    return (f'<h2 id="bestenliste">Warum steht Amex in der Bestenliste nicht auf Platz 1?</h2><div class="prose"><p>Beide Rechnungen stimmen, sie gehen nur von verschiedenen Nutzern aus. '
            f'Unsere <a href="../../kreditkarten/bestenlisten/punkte/">Bestenliste Meilen &amp; Punkte</a> bewertet jeden Punkt vorsichtig mit 0,5 Cent, rechnet mit 1.000 € Umsatz im Monat und zieht Jahresgebühr und Aufpreise ab. Sie zeigt also, was nach der Gebühr übrig bleibt. '
            f'So passt sie für die meisten, die Punkte für Gutscheine oder Economy-Flüge einlösen. Dort liegen Karten mit niedriger Gebühr vorne, die teure Gold Card und Platinum Card landen weiter hinten. Wer lieber Geld zurück will, findet die <a href="../../kreditkarten/bestenlisten/cashback/">Bestenliste Cashback</a>.</p>'
            f'<p>Dieser Ratgeber rechnet dagegen mit 1 bis 2 Cent pro Punkt und dem Turbo-Bonus. Diesen Wert erreichst du nur, wenn du die Punkte gezielt in Business- oder First-Class-Flüge über Partnerprogramme tauschst. '
            f'Wenn du das vorhast und viel mit der Karte zahlst, lohnt sich American Express. Wenn nicht, nimm eine Karte aus der Bestenliste.</p></div>')

PROG={'at':'<div class="prose"><p>Vier Wege, mit österreichischen Kreditkarten zu sammeln:</p><ul>\n<li><b>Membership Rewards (American Express):</b> 1 Punkt pro Euro, bei der Gold Card mit Turbo 1,5. Die Teilnahme kostet bei der Gold Card 30 € im Jahr, bei der Platinum Card ist sie inklusive. Punkte lassen sich in Partnerprogramme übertragen, die Liste steht oben.</li>\n<li><b>Miles &amp; More:</b> das Programm von Austrian, Lufthansa und Swiss. Direkt sammelst du mit der Austrian Miles &amp; More Premiumcard von Erste Bank und Sparkasse (1 Meile je 1,50 €), indirekt über das Bonusprogramm von Diners Club (1 Punkt je 8 €, 4 Meilen je Punkt, 25 € im Jahr).</li>\n<li><b>Hotelpunkte:</b> die Hilton Honors Kreditkarte gibt 1 Punkt pro Euro, 2 in Hilton-Hotels. Pro Stück sind Hotelpunkte deutlich weniger wert als Meilen.</li>\n<li><b>Cashback und App-Banken:</b> Revolut sammelt RevPoints, Trade Republic zahlt 1 % Saveback in den Sparplan, die Erste Bank gibt bis 0,6 % Online-Cashback. Einfach, aber meist weniger als gut eingelöste Meilen.</li></ul>\n<p>Punkte, die du in mehrere Programme übertragen kannst, sind am flexibelsten: Du entscheidest erst beim Einlösen, wo sie am meisten bringen. Übertragungen gehen nur in eine Richtung, also erst übertragen, wenn die Prämie feststeht.</p></div>',
      'de':'<div class="prose"><p>Vier Wege, mit deutschen Kreditkarten zu sammeln:</p><ul>\n<li><b>Membership Rewards (American Express):</b> 1 Punkt pro Euro bei Gold und Platinum (mit Turbo 1,5), bei der Blue Card nur gegen Aufpreis. Übertragbar auf Airline- und Hotelprogramme, die Liste steht oben.</li>\n<li><b>Miles &amp; More:</b> mit den Miles &amp; More Credit Cards 1 Meile je 2 €, für Prämienflüge bei Lufthansa, Austrian, Swiss und Partnern; mit Blue und Gold verfallen die Meilen nicht.</li>\n<li><b>Payback:</b> mit der Payback American Express 1 Punkt je 3 €, 1 Punkt ist 1 Cent wert und lässt sich 1:1 zu Miles &amp; More übertragen.</li>\n<li><b>Cashback:</b> Geld zurück auf jeden Einkauf, etwa 0,5 % bei der WEB.Cent-Karte, oder Partner-Cashback bei vielen Banken. Am einfachsten zu vergleichen, weil der Wert feststeht.</li></ul>\n<p>Punkte, die du in mehrere Programme übertragen kannst, sind am flexibelsten: Du entscheidest erst beim Einlösen, wo sie am meisten bringen. Übertragungen gehen nur in eine Richtung, also erst übertragen, wenn die Prämie feststeht.</p></div>'}
WERT={'at':[('Cashback','genau 1 Cent pro Cent'),('Miles &amp; More Meile','rund 1 Cent, bei Business-Class-Flügen oft mehr'),('Membership-Rewards-Punkt','laut American Express 0,3 bis 0,5 Cent, über Meilen-Transfer je nach Einlösung mehr'),('Hilton-Punkt','0,4 bis 0,5 Cent'),('Sachprämien und Gutscheine','oft deutlich weniger als 1 Cent')],
      'de':[('Cashback','genau 1 Cent pro Cent'),('Payback-Punkt','fest 1 Cent, als Miles &amp; More Meile bei Flügen mehr'),('Miles &amp; More Meile','rund 1 Cent, bei Business-Class-Flügen oft mehr'),('Membership-Rewards-Punkt','laut American Express 0,3 bis 0,5 Cent, über Meilen-Transfer je nach Einlösung mehr'),('Hilton-Punkt','0,4 bis 0,5 Cent'),('Sachprämien und Gutscheine','oft deutlich weniger als 1 Cent')]}
def punkte_block(land):
    """Einstieg (Programme, Kartentabelle aus den Daten, Punktewerte, typische Fehler) für die statische Seite „Lohnt sich Punktesammeln“."""
    RC=rated(cards(land)); P='../../../'; N=LAND[land]['name']
    pts=[c for c in RC if c['cb'] or c['ml']]; n_all=len(pts); pts=pts[:25]
    wert='<div class="tbl"><table><thead><tr><th>Was</th><th>Vorsichtiger Wert</th></tr></thead><tbody>'+''.join(f'<tr><td>{a}</td><td>{b}</td></tr>' for a,b in WERT[land])+'</tbody></table></div>'
    return (f'<!-- GEN:punkte --><h2>Welche Programme es in {N} gibt</h2>{PROG[land]}'
            f'<h2>Alle Karten mit Punkten, Meilen oder Cashback</h2><p class="note">Alle bewerteten Privatkarten aus unserem {N}-Vergleich, die Punkte, Meilen oder Cashback geben, sortiert nach Bewertung'+(f', die {len(pts)} am besten bewerteten von {n_all}' if n_all>len(pts) else '')+'. „Sammeln“ nennt die Rate laut Anbieter.</p>'
            +table(pts,[COL['karte'],COL['cb'],COL['fee'],COL['stars']],P)+'<p class="note"><a class="lnk" href="../../kreditkarten/bestenlisten/punkte/">Bestenliste Meilen &amp; Punkte →</a> · <a class="lnk" href="../../kreditkarten/bestenlisten/cashback/">Bestenliste Cashback →</a></p>'
            f'<h2>Was ein Punkt wert ist</h2><div class="prose"><p>Unsere vorsichtigen Schätzungen; der tatsächliche Wert hängt davon ab, wofür du einlöst.</p></div>{wert}'
            '<h2>Typische Fehler</h2><div class="prose"><ul><li><b>Sachprämien und Gutscheine:</b> bringen pro Punkt am wenigsten.</li><li><b>Verfall:</b> viele Programme haben Verfallsregeln; Amex-Punkte verfallen nicht, solange die Karte läuft, Hilton-Punkte nach 24 Monaten ohne Aktivität'+(', Miles &amp; More Meilen ohne Verfallsschutz nach 36 Monaten' if land=='de' else '')+'.</li><li><b>Jahresgebühr nicht gegengerechnet:</b> eine Karte für über 200 € muss erst einmal so viele Punkte bringen; die Rechnung dazu steht oben.</li><li><b>Mehr ausgeben, nur um zu sammeln:</b> kein Punktewert ist so hoch wie 20 bis 25 % Teilzahlungszins.</li></ul></div><!-- /GEN:punkte -->')
def fix_static():
    for land,(slug,N) in WHY_AMEX.items():
        f=R+f'{land}/ratgeber/{slug}/index.html'
        if not os.path.exists(f): continue
        s=open(f).read()
        s=re.sub(r'<h2 id="bestenliste">.*?</div>(?=\s*<h2)','',s,count=1,flags=re.S)
        i=s.find('<h2',s.find('Kurzantwort'))
        if i>0: s=s[:i]+why_amex(land)+'\n'+s[i:]
        s=re.sub(r'<!-- GEN:punkte -->.*?<!-- /GEN:punkte -->\n?','',s,flags=re.S)
        k=s.find('<h2>Die 5 wichtigsten Regeln</h2>')
        if k>0: s=s[:k]+punkte_block(land)+'\n'+s[k:]
        open(f,'w').write(s)
    for slug,reps in DE_FIX.items():
        f=R+f'de/ratgeber/{slug}/index.html'
        if not os.path.exists(f): continue
        s=open(f).read()
        for a,b in reps: s=s.replace(a,b)
        open(f,'w').write(s)
def slugs(land): return sorted(d for d in os.listdir(R+f'{land}/ratgeber') if os.path.isdir(R+f'{land}/ratgeber/{d}'))
def hreflang_all():
    for land in ('at','de'):
        other='de' if land=='at' else 'at'
        for slug in slugs(land):
            o=PAIRS.get((land,slug),(other,slug))[1]
            if not os.path.exists(R+f'{other}/ratgeber/{o}/index.html'): continue
            f=R+f'{land}/ratgeber/{slug}/index.html'; s=open(f).read()
            s=re.sub(r'\n?<link rel="alternate" hreflang="de-(AT|DE)" href="https://finvallo\.com/(at|de)/ratgeber/[^"]*">','',s)
            at_u=f'https://finvallo.com/at/ratgeber/{slug if land=="at" else o}/'; de_u=f'https://finvallo.com/de/ratgeber/{slug if land=="de" else o}/'
            alt=f'\n<link rel="alternate" hreflang="de-AT" href="{at_u}"><link rel="alternate" hreflang="de-DE" href="{de_u}">'
            s=re.sub(r'(<link rel="canonical" href="[^"]*">)',lambda m:m.group(1)+alt,s,count=1)
            # Länderschalter im Header auf das Gegenstück zeigen lassen
            s=re.sub(r'(<div class="land"[^>]*>.*?<a href=")[^"]*(" hreflang="de-AT")',lambda m:m.group(1)+'../../../'+at_u.split('finvallo.com/')[1]+m.group(2),s,count=1,flags=re.S)
            s=re.sub(r'(<div class="land"[^>]*>.*?<a href=")[^"]*(" hreflang="de-DE")',lambda m:m.group(1)+'../../../'+de_u.split('finvallo.com/')[1]+m.group(2),s,count=1,flags=re.S)
            open(f,'w').write(s)
def meta(land,slug):
    s=open(R+f'{land}/ratgeber/{slug}/index.html').read()
    h1=html.unescape(re.sub(r'<[^>]+>','',re.search(r'<h1>(.*?)</h1>',s,re.S).group(1)))
    d=html.unescape(re.search(r'<meta name="description" content="([^"]*)"',s).group(1))
    return h1,d
ORDER=['kostenloses-girokonto','girokonto-wechseln','basiskonto','dispo','kontoueberziehung','gemeinschaftskonto','p-konto','pfaendungsschutzkonto','kinderkonto-jugendkonto','konto-selbststaendige','festgeld-oder-tagesgeld','einlagensicherung','zinstreppe','festgeld-kuendigen','festgeld-plattformen','festgeld-steuern','kostenlose-kreditkarte','kreditkarte-studenten','kreditkarte-beantragen','fremdwaehrung','bargeld-beheben','bargeld-abheben','reiseversicherung','flugverspaetung-gepaeck','punkte-sammeln-at','punkte-sammeln-de','lounges','visa-mastercard-amex','apple-pay-google-pay','mietwagen-kaution','ohne-bonitaetspruefung','kartentypen','teilzahlung','business']
GRUPPEN=[('Girokonto',['kostenloses-girokonto','girokonto-wechseln','basiskonto','dispo','kontoueberziehung','gemeinschaftskonto','p-konto','pfaendungsschutzkonto','kinderkonto-jugendkonto','konto-selbststaendige']),
         ('Festgeld und Sparen',['festgeld-oder-tagesgeld','einlagensicherung','zinstreppe','festgeld-kuendigen','festgeld-plattformen','festgeld-steuern'])]
def index_pages():
    for land in ('at','de'):
        f=R+f'{land}/ratgeber/index.html'; s=open(f).read(); N=LAND[land]['name']
        ss=sorted(slugs(land),key=lambda x:ORDER.index(x) if x in ORDER else 99)
        tile=lambda x:f'<a class="catcard" href="{x}/"><b>{E(meta(land,x)[0])}</b><span style="color:var(--muted)">{E(meta(land,x)[1][:150])}</span><small>Lesen →</small></a>'
        rest=list(ss); blocks=''
        for name,sl in GRUPPEN:
            xs=[x for x in ss if x in sl]
            if not xs: continue
            rest=[x for x in rest if x not in xs]
            blocks+=f'<h2>{name}</h2><div class="catgrid">{"".join(tile(x) for x in xs)}</div>'
        blocks=f'<h2>Kreditkarten</h2><div class="catgrid">{"".join(tile(x) for x in rest)}</div>'+blocks
        s=re.sub(r'(<main id="app">.*?)<div class="catgrid">.*?</div>(\s*</main>)',lambda m:m.group(1)+blocks+m.group(2),s,count=1,flags=re.S)
        s=re.sub(r'(<main id="app">.*?</p>)(?:<h2>.*?</div>)+(\s*</main>)',lambda m:m.group(1)+blocks+m.group(2),s,count=1,flags=re.S)
        s=re.sub(r'<p class="lede">[^<]*</p>',f'<p class="lede">{len(ss)} Beiträge zu Kreditkarten, Girokonten und Festgeld, verständlich erklärt und mit Zahlen aus unseren Vergleichen. Alle Beiträge gelten für {N}.</p>',s,count=1)
        t=f'Ratgeber {N}: Kreditkarten, Girokonto, Festgeld | Finvallo'
        d=f'{len(ss)} Ratgeber für {N} zu Kreditkarten, Girokonten und Festgeld: Gebühren, Versicherung, Kontowechsel, Dispo, Einlagensicherung und Steuern, mit Zahlen aus unseren Vergleichen.'
        s=re.sub(r'<title>.*?</title>',f'<title>{E(t)}</title>',s,count=1)
        for a in ('name="description"','property="og:description"'): s=re.sub(rf'<meta {a} content="[^"]*">',f'<meta {a} content="{E(d)}">',s,count=1)
        s=re.sub(r'<meta property="og:title" content="[^"]*">',f'<meta property="og:title" content="{E(t)}">',s,count=1)
        open(f,'w').write(s)
def sitemap_llms():
    p=R+'sitemap.xml'; s=open(p).read()
    for land in ('at','de'):
        for x in slugs(land):
            u=f'https://finvallo.com/{land}/ratgeber/{x}/'
            if f'<loc>{u}</loc>' not in s: s=s.replace('</urlset>',f'<url><loc>{u}</loc><lastmod>{STAND}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>\n</urlset>')
    open(p,'w').write(s)
    for fn in ('llms.txt','llms-full.txt'):
        p=R+fn; s=open(p).read()
        for land,hd in (('at','## Österreich: Ratgeber'),('de','## Deutschland: Ratgeber')):
            ss=sorted(slugs(land),key=lambda x:ORDER.index(x) if x in ORDER else 99)
            blk=hd+'\n'+''.join(f'- [{meta(land,x)[0]} ({LAND[land]["name"]})](https://finvallo.com/{land}/ratgeber/{x}/): {meta(land,x)[1]}\n' for x in ss)
            s=re.sub(re.escape(hd)+r'\n(?:- .*\n?)*',blk,s,count=1)
        open(p,'w').write(s)
# ---------- Titel, H1 und FAQ nach echten Suchanfragen (Search Console, Oktober 2026) ----------
# Die Leute suchen nach konkreten Fragen und Produktnamen, nicht nach generischen Titeln. Hier passen wir die Ratgeber daran an.
def seo_faq(land):
    RC=rated(cards(land)); N=LAND[land]['name']; P='../../../'; bl=f'{P}{land}/kreditkarten/bestenlisten/'
    lou=[c for c in RC if c.get('lg')]; lnames=fmtlist([c['titel'] for c in lou[:4]])
    tz=sorted([c for c in RC if c['typ']=='Kreditkarte' and c.get('effz')],key=lambda c:c['effz'])
    free_ins=[c for c in RC if c.get('fee')==0 and (c.get('tier') or 0)>=2]
    gratis=[c for c in RC if c.get('fee')==0 and c['typ'] in ('Kreditkarte','Charge') and not c.get('giro')]
    deb=[c for c in RC if c['typ'] in ('Debit','Prepaid') and c.get('fee')==0]
    L=lambda c:f'<a class="lnk" href="{P}{land}/kreditkarten/{c["slug"]}/">{E(c["titel"])}</a>'
    at=land=='at'
    S={}
    S['visa-mastercard-amex']=dict(
        mt=f'Visa, Mastercard oder Amex: Akzeptanz ({land.upper()}) | Finvallo',
        h1='Visa, Mastercard oder American Express: Wo welche Karte angenommen wird',
        faq=[('Ist American Express Visa oder Mastercard?','Weder noch. American Express ist ein eigenes Kartennetz mit eigenen Karten, so wie Visa und Mastercard. Deshalb gibt es keine „Amex Visa“. Ob eine Karte angenommen wird, hängt davon ab, welches Netz der Händler freigeschaltet hat; Visa und Mastercard sind fast überall dabei, Amex deutlich seltener.'),
             ('Wo werden Visa und Mastercard akzeptiert?','Praktisch an jeder Stelle, die Kartenzahlung anbietet. Beide Netze haben weltweit über 100 Millionen Akzeptanzstellen, in Europa nimmt kaum ein Händler nur eines von beiden. Unterschiede gibt es eher bei Debitkarten: Manche Automaten und Hotels nehmen keine Debit-Varianten, egal von welchem Netz.'),
             ('Visa, Mastercard oder Amex: Was ist im Alltag besser?',f'Für die meisten ist es egal, ob Visa oder Mastercard auf der Karte steht; die Konditionen macht die Bank, nicht das Netz. American Express lohnt sich nur, wenn du Punkte sammeln willst und eine zweite Karte für die Läden hast, die Amex nicht nehmen. Welche Karte zu dir passt, zeigt der <a class="lnk" href="{P}{land}/kreditkarten/">Kreditkarten-Vergleich</a>.')])
    S['business']=dict(
        mt=f'Firmenkreditkarte ({land.upper()}): Haftung, private Nutzung | Finvallo',
        h1=f'Firmenkreditkarte in {N}: Wer haftet, was sie kostet und ob du sie privat nutzen darfst',
        faq=[('Darf ich die Firmenkreditkarte privat nutzen?','Bei den meisten Anbietern ist das vertraglich ausgeschlossen, und steuerlich ist es ein Problem: Private Ausgaben über die Firmenkarte gelten als Entnahme oder geldwerter Vorteil und müssen verbucht werden. Wer beides vermischt, macht sich die Buchhaltung unnötig schwer. Besser eine private Karte für Privates, die Firmenkarte nur fürs Geschäft.'),
             ('Kann ich meine private Kreditkarte für die Firma nutzen?',f'Als Einzelunternehmer ja, viele machen das am Anfang. Du musst die Belege dann sauber trennen und jeden geschäftlichen Umsatz einzeln erfassen. Sobald Mitarbeiter mitzahlen sollen oder du Umsätze automatisch in die Buchhaltung übernehmen willst, ist eine echte Firmenkarte einfacher; eine Übersicht steht unter <a class="lnk" href="{P}{land}/kreditkarten/business/">Business-Kreditkarten</a>.'),
             ('Bekomme ich eine Business-Kreditkarte mit Nebengewerbe?','Ja, die meisten Anbieter verlangen nur eine Gewerbeanmeldung oder den Nachweis der selbstständigen Tätigkeit, kein Mindestumsatz. Geprüft wird deine persönliche Bonität, weil du als Inhaber haftest. Bei Karten, die an ein Geschäftskonto gebunden sind, brauchst du zuerst das Konto.')])
    S['teilzahlung']=dict(
        mt=f'Kreditkarte mit Ratenzahlung ({land.upper()}): Zinsen, Kosten | Finvallo',
        h1=f'Kreditkarte mit Ratenzahlung in {N}: Was die Teilzahlung kostet und wie du sie abschaltest',
        faq=[(f'Welche Kreditkarte in {N} hat Ratenzahlung?',f'Nur echte Kreditkarten mit Kreditrahmen, nicht die Charge-Karten der Hausbanken. Im Vergleich sind das zum Beispiel {fmtlist([L(c) for c in tz[:3]])}. Alle rechnen bei Teilzahlung mit Zinsen zwischen {pct(tz[0]["effz"])} und {pct(tz[-1]["effz"])} effektiv im Jahr.' if tz else 'Nur echte Kreditkarten mit Kreditrahmen, nicht die Charge-Karten der Hausbanken.'),
             ('Gibt es eine Kreditkarte mit niedrigen Zinsen für die Teilzahlung?',f'Niedrig ist relativ: Die günstigste Teilzahlung im Vergleich liegt bei {pct(tz[0]["effz"])} ({tz[0]["titel"]}), die meisten Karten bei 20 bis 25 %. Ein Ratenkredit kostet meist weniger als die Hälfte. Teilzahlung lohnt sich nur für ein, zwei Monate, nicht als Dauerkredit.' if tz else 'Die meisten Karten verlangen 20 bis 25 % effektiv. Ein Ratenkredit ist fast immer billiger.'),
             ('Kann ich eine Reparatur oder einen größeren Kauf mit der Kreditkarte in Raten zahlen?','Ja, wenn die Karte Teilzahlung erlaubt: Du zahlst den Kauf ganz normal, überweist dann nur einen Teil der Monatsrechnung, der Rest läuft als Kredit weiter. Rechne vorher aus, was das kostet; bei 1.000 € und 25 % Zinsen sind es über ein Jahr rund 140 € Zinsen, wenn du in gleichen Raten tilgst.')])
    S['lounges']=dict(
        mt=f'Kreditkarte mit Lounge-Zugang ({land.upper()}): Priority Pass | Finvallo',
        h1=f'Kreditkarte mit Lounge-Zugang in {N}: Priority Pass, Besuche und Begleitpersonen',
        faq=[(f'Welche Kreditkarte in {N} hat Lounge-Zugang?',f'Im Vergleich enthalten {len(lou)} Karten kostenlose Lounge-Besuche, darunter {lnames}. Wie viele Besuche gratis sind und ob eine Begleitperson mitdarf, steht in der <a class="lnk" href="{bl}lounge/">Bestenliste Lounge-Zugang</a>.' if lou else 'Nur wenige Premiumkarten. Die Liste steht in der Bestenliste Lounge-Zugang.'),
             ('Welche Kreditkarte hat Priority Pass?','Priority Pass ist das größte Lounge-Programm und bei den meisten Premiumkarten dabei, etwa bei American Express Platinum. Wichtig ist der Unterschied zwischen Mitgliedschaft und Besuchen: Manche Karten geben dir nur den Ausweis, jeder Besuch kostet dann rund 30 €; andere enthalten eine feste Zahl Besuche oder unbegrenzten Zugang. Das steht bei jeder Karte unter „Lounge“.')]
            +([('Komme ich mit der Kreditkarte in die Lounges am Flughafen Wien?','Die Lounges in Wien-Schwechat sind an Priority Pass und an einzelne Kartenprogramme angeschlossen. Ob deine Karte dort gilt, hängt vom Programm ab, nicht von der Bank; prüfe die Lounge-Liste deines Programms vor dem Flug, weil sich die teilnehmenden Lounges ändern.')] if at else []))
    S['kostenlose-kreditkarte']=dict(
        mt='Gratis Kreditkarte Österreich: was sie kostet | Finvallo' if at else 'Kostenlose Kreditkarte Deutschland: die Haken | Finvallo',
        h1=f'Gratis Kreditkarte in {N}: Welche wirklich nichts kostet' if at else 'Kostenlose Kreditkarte in Deutschland: Welche wirklich nichts kostet',
        faq=[(f'Welche Kreditkarte ist in {N} gratis?',f'Dauerhaft ohne Jahresgebühr und ohne Pflicht zu einem Konto beim Anbieter sind im Vergleich {fmtlist([L(c) for c in gratis[:4]])}. Dazu kommen kostenlose Debitkarten wie {fmtlist([c["titel"] for c in deb[:3]])}. Gratis heißt aber nur: keine Jahresgebühr. Bargeld, Fremdwährung und Teilzahlung können trotzdem kosten.' if gratis else 'Die Liste steht in der Bestenliste ohne Jahresgebühr.'),
             ('Welche gratis Kreditkarte hat eine Reiseversicherung?',f'{fmtlist([L(c) for c in free_ins[:3]])}: alle ohne Jahresgebühr und mit Reiserücktritt und Auslandskranken. Bedingungen und Selbstbehalt stehen auf der Kartenseite.' if free_ins else 'Im Vergleich derzeit keine. Reiseversicherung gibt es meist erst ab der Gold-Stufe gegen Gebühr.')])
    S['fremdwaehrung']=dict(
        mt=f'Kreditkarte im Ausland: Gebühren und Kurs ({land.upper()}) | Finvallo',
        h1=f'Kreditkarte im Ausland: {"Bearbeitungsentgelt" if at else "Auslandseinsatzentgelt"}, Kursaufschlag und die Euro-Falle',
        faq=[('Was ist das Auslandseinsatzentgelt?' if not at else 'Was ist das Bearbeitungsentgelt für Fremdwährung?','Die Gebühr, die deine Bank auf jede Zahlung in einer anderen Währung als Euro aufschlägt, meist 1,5 bis 2 % des Betrags. Sie steht im Preisblatt der Karte. Dazu kann ein Kursaufschlag kommen, den du nicht als Gebühr siehst, sondern nur am schlechteren Wechselkurs.'),
             ('Welche Mastercard oder Visa hat keine Fremdwährungsgebühr?',f'Im Vergleich gibt es {sum(1 for c in RC if c.get("fx")==0)} Angebote mit 0 %, darunter ohne Jahresgebühr {fmtlist([L(c) for c in RC if c.get("fee")==0 and c.get("fx")==0][:3])}. Alle stehen in der <a class="lnk" href="{bl}ausland/">Bestenliste ohne Auslandsgebühr</a>.'),
             ('Kostet die Kreditkarte in der Schweiz oder in Großbritannien Gebühren?','Ja, dort zahlst du in Franken oder Pfund, also in Fremdwährung. Das Entgelt fällt genauso an wie in den USA oder in Thailand. Innerhalb des Euroraums kostet das Zahlen dagegen nichts extra, egal in welchem Land.')])
    S['mietwagen-kaution']=dict(
        mt=f'Mietwagen-Kaution: Kreditkarte oder Debit? ({land.upper()}) | Finvallo',
        h1='Mietwagen und Kaution: Warum der Vermieter eine echte Kreditkarte will',
        faq=[('Geht die Mietwagen-Kaution mit einer Debitkarte?','Bei den großen Vermietern meist nicht. Sie blocken die Kaution auf einem Kreditrahmen, den eine Debitkarte nicht hat. Manche Stationen nehmen Debitkarten gegen eine höhere Kaution und mit Vollkasko ohne Selbstbeteiligung, die du dann dort kaufen musst. Prüfe das vor der Buchung in den Mietbedingungen, nicht erst am Schalter.'),
             ('Ersetzt die Kreditkarte die Vollkasko beim Mietwagen?','Nur bei Karten mit Mietwagen-Versicherung, und auch dann meist nur den Selbstbehalt oder die Kasko bis zu einer Höchstsumme. Die Haftpflicht ist immer die des Vermieters. Ob deine Karte einen Mietwagen-Schutz hat, steht auf der Kartenseite unter „Mietwagen“.')])
    S['ohne-bonitaetspruefung']=dict(
        mt=f'Kreditkarte ohne {"KSV" if at else "Schufa"}: was wirklich geht ({land.upper()}) | Finvallo',
        h1=f'Kreditkarte ohne {"KSV-Abfrage" if at else "Schufa"}: Was wirklich geht und was nur Werbung ist',
        faq=[(f'Gibt es eine Kreditkarte ohne {"KSV" if at else "Schufa"} mit Verfügungsrahmen?','Nein. Ein Verfügungsrahmen ist ein Kredit, und den gibt keine Bank ohne Bonitätsprüfung. Angebote, die das versprechen, sind entweder Prepaid-Karten mit aufgeladenem Guthaben oder teure Kreditvermittler. Was ohne Prüfung geht, sind Debit- und Prepaid-Karten; die bezahlen nur, was auf dem Konto ist.'),
             ('Was ist eine Kreditkarte auf Guthabenbasis?','Eine Prepaid-Karte: Du lädst Geld auf und zahlst davon. Sie läuft über Visa oder Mastercard und funktioniert online und im Ausland, aber nicht für Kautionen bei Mietwagen oder Hotels. Oft kostet sie Jahres- oder Ladegebühren; eine kostenlose Debitkarte einer App-Bank ist meist die bessere Wahl.')])
    S['kreditkarte-studenten']=dict(
        mt=f'Kreditkarte für Studenten ({land.upper()}): ohne Einkommen | Finvallo')
    S['apple-pay-google-pay']=dict(mt=f'Apple Pay und Google Pay: Banken in {N} | Finvallo')
    S['reiseversicherung']=dict(
        mt=f'Kreditkarte mit Reiseversicherung: Vergleich ({land.upper()}) | Finvallo',
        faq=[('Brauche ich eine eigene Auslandskrankenversicherung, wenn meine Kreditkarte eine Reiseversicherung hat?','Kommt auf die Karte an. Viele Gold-Karten enthalten eine Auslandskrankenversicherung, aber oft nur für Reisen bis zu einer bestimmten Dauer, nur wenn du die Reise mit der Karte bezahlt hast, und mit Altersgrenzen. Lies auf der Kartenseite nach, ob „Auslandskranken“ dabei ist und welche Bedingung gilt. Fehlt sie oder passt die Bedingung nicht, kostet eine eigene Jahrespolizze nur 10 bis 20 € und gilt ohne Wenn und Aber.'),
             ('Welche Kreditkarte hat eine Reiseversicherung mit Storno?',f'Ohne Jahresgebühr: {fmtlist([L(c) for c in free_ins[:3]])}. Mit Gebühr fast alle Gold- und Platinum-Karten. Stornosummen und Selbstbehalt stehen in der <a class="lnk" href="{bl}reisen/">Bestenliste Reisen</a>.' if free_ins else 'Fast alle Gold- und Platinum-Karten. Stornosummen und Selbstbehalt stehen in der Bestenliste Reisen.')])
    S['flugverspaetung-gepaeck']=dict(mt='Flugverspätung: Was die Kreditkarte zahlt (AT) | Finvallo')
    S['bargeld-beheben' if at else 'bargeld-abheben']=dict(mt=f'{"Bargeld beheben" if at else "Geld abheben"} mit Kreditkarte: Gebühren ({land.upper()}) | Finvallo')
    S['kartentypen']=dict(mt=f'Kartentypen ({land.upper()}): Kredit, Charge, Debit, Prepaid | Finvallo' if at else 'Kartentypen (DE): Kreditkarte, Debit, Prepaid | Finvallo')
    S['girokonto-wechseln']=dict(mt=f'Girokonto wechseln ({land.upper()}): Ablauf, Fristen, Kosten | Finvallo')
    S['kostenloses-girokonto']=dict(mt='Kostenloses Girokonto Österreich: die Bedingungen | Finvallo' if at else 'Kostenloses Girokonto (DE): Bedingungen, Fallen | Finvallo')
    return S
# statische Artikel (ohne art()): nur Titel anpassen
STATIC_TITLES={('at','lounges'):'Kreditkarte mit Lounge-Zugang (AT): Priority Pass | Finvallo',
               ('at','punkte-sammeln-at'):'Meilen und Punkte sammeln mit Kreditkarte (AT) | Finvallo',
               ('de','punkte-sammeln-de'):'Meilen und Punkte sammeln mit Kreditkarte (DE) | Finvallo'}
def static_titles():
    for (land,slug),t in STATIC_TITLES.items():
        f=R+f'{land}/ratgeber/{slug}/index.html'
        if not os.path.exists(f) or (land,slug) in ARTS: continue
        s=open(f).read()
        s=re.sub(r'<title>.*?</title>',f'<title>{E(t)}</title>',s,count=1)
        s=re.sub(r'<meta property="og:title" content="[^"]*">',f'<meta property="og:title" content="{E(t)}">',s,count=1)
        open(f,'w').write(s)
def apply_seo(land):
    for slug,o in seo_faq(land).items():
        a=ARTS.get((land,slug))
        if not a: continue
        if o.get('mt'): a['mt']=o['mt']
        if o.get('h1'): a['h1']=o['h1']
        if o.get('faq'):
            have={q.lower() for q,_ in a.get('faq',[])}
            a['faq']=[x for x in o['faq'] if x[0].lower() not in have]+a.get('faq',[])
            a['faq']=a['faq'][:7]
def run():
    for land in ('at','de'): build(land); apply_seo(land)
    for (land,slug) in ARTS: render(land,slug)
    fix_static(); static_titles(); hreflang_all(); index_pages(); sitemap_llms()
    for (land,slug),a in ARTS.items():
        if len(a['mt'])>62: print(f'Titel zu lang ({len(a["mt"])}): {land}/{slug}: {a["mt"]}')
    print('Artikel neu/überarbeitet:',len(ARTS))
if __name__=='__main__': run()
