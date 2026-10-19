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
TIERN={0:'keine',1:'Basis-Reiseschutz',2:'mit Reiserücktritt',3:'umfassend (inkl. Mietwagen)',4:'Premium'}
# ---------- Daten ----------
def cards(land):
    import karten
    if not hasattr(cards,'D'):
        cards.D=karten.prepare()
        global STAND, STAND_DE   # Stand = jüngstes Prüfdatum der Kartendaten
        STAND=max(karten.LANDS[l]['stand'] for l in karten.LANDS); STAND_DE='.'.join(reversed(STAND.split('-')))
    out=[]
    for c in cards.D[land][0]:
        out.append(dict(titel=c['titel'],url=f'{land}/kreditkarten/{c["slug"]}/',fee=c.get('fee'),fx=c.get('fx'),fxText=karten.fxT(c),cashText=karten.cashT(c),
          stars=c.get('stars'),tier=c.get('tier'),typ=c['typ'],netz=c.get('netz') or '',giro=c.get('giro'),auto=c.get('auto'),art=c['art'],
          lg=c.get('lgText') if c['ex'].get('lg') else None,cb=c.get('earnText') or (c.get('cbText') if c['ex'].get('cb') else None),ml=c['ex'].get('ml'),klasse=c['klasse'],bestand=c.get('nurfuer'),cash=c.get('cash'),effz=c.get('effz')))
    return [c for c in out if c['art']=='Privat' and not c.get('bestand')]
def rated(L): return sorted([c for c in L if c.get('stars') is not None],key=lambda c:(-c['stars'],c['fee'] if c['fee'] is not None else 1e9))
def link(c,P): return f'<a class="lnk" href="{P}{c["url"]}">{E(c["titel"])}</a>'
def table(rows,cols,P):
    h=''.join(f'<th>{c[0]}</th>' for c in cols)
    b=''.join('<tr>'+''.join(f'<td>{f(c,P)}</td>' for _,f in cols)+'</tr>' for c in rows)
    return f'<div class="tbl wide"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'
COL=dict(karte=('Karte',lambda c,P:link(c,P)),
         fee=('Jahresgebühr',lambda c,P:'kostenlos' if c['fee']==0 else (f'{eur(c["fee"])} €' if c['fee'] is not None else '–')),
         fx=('Zahlung Ausland',lambda c,P:E(c['fxText'] if c['fx'] not in (0,None) else ('0 %' if c['fx']==0 else '–'))),
         cash=('Bargeld',lambda c,P:E(c['cashText'] or '–')),
         ins=('Reiseversicherung',lambda c,P:TIERN.get(c['tier'],'–') if c['tier'] is not None else '–'),
         stars=('Bewertung',lambda c,P:f'{de1(c["stars"])} ★' if c.get('stars') is not None else '–'),
         netz=('Netz',lambda c,P:E(c['netz'])),typ=('Typ',lambda c,P:E(c['typ'])),
         lg=('Lounge',lambda c,P:E((c['lg'] or '')[:90])),cb=('Sammeln',lambda c,P:E((c['cb'] or '')[:90])))
# ---------- Seite ----------
# Datum je Ratgeber (wie Frontmatter): published, updated (beim nächsten inhaltlichen Edit pflegen),
# optional corrections=[dict(date='JJJJ-MM-TT', note='…')] → Abschnitt „Korrekturen“ am Ende des Artikels.
DATES={
    ('at','business'): dict(published='2026-10-11', updated='2026-10-19'),
    ('at','fremdwaehrung'): dict(published='2026-10-11', updated='2026-10-15'),
    ('at','kartentypen'): dict(published='2026-10-11', updated='2026-10-11'),
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
    ('de','kartentypen'): dict(published='2026-10-11', updated='2026-10-11'),
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
         "author":{"@id":"https://finvallo.com/#org"},"publisher":{"@id":"https://finvallo.com/#org"},"mainEntityOfPage":url,"about":f"Kreditkarten in {LAND[land]['name']}","image":"https://finvallo.com/assets/og.png"}]}
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
    import ratgeber_business; ratgeber_business.register(land,art,P,best,cards.D[land][0],karten.card_count(land,'private'),eur,karten,de1,pct)
    # B) Kreditkarte beantragen
    art(land,'kreditkarte-beantragen',
      h1=f'Kreditkarte beantragen in {N}: so geht es Schritt für Schritt',
      mt=f'Kreditkarte beantragen {N}: Ablauf & Tipps | Finvallo',
      desc=f'Kreditkarte beantragen in {N}: welche Unterlagen du brauchst, wie {"die Schufa-Prüfung" if land=="de" else "die KSV-Prüfung"} abläuft, wie lange es dauert und warum Anträge abgelehnt werden.',
      lede='Von der Auswahl bis zur ersten Zahlung: was du brauchst und worauf es ankommt.',
      kurz=f'Du füllst online den Antrag aus, bestätigst deine Identität per Video- oder Online-Ident und die Bank prüft deine Bonität {"bei der Schufa" if land=="de" else "beim KSV1870"}. Bei Direktbanken dauert das oft nur Minuten, die Karte kommt nach etwa einer Woche per Post. Häufig kannst du sie vorher schon digital mit Apple Pay oder Google Pay nutzen.',
      secs=[('Das brauchst du',f'<div class="prose"><ul><li>Wohnsitz in {N} und meist mindestens 18 Jahre</li><li>Gültiger Ausweis oder Reisepass</li><li>Ein {"deutsches" if land=="de" else "österreichisches oder SEPA-"}Referenzkonto für die Abrechnung</li><li>Angaben zu Job und Einkommen, manchmal Gehaltsnachweise</li><li>Smartphone für Video-Ident und App</li></ul></div>'),
            ('So läuft der Antrag ab',f'''<div class="steps"><div class="step"><span class="no">1</span><div><b>Karte auswählen</b><p>Vergleiche Jahresgebühr, Auslandsgebühren, Bargeld und Versicherung. Unsere <a href="{best}">Bestenlisten</a> helfen dabei.</p></div></div>
<div class="step"><span class="no">2</span><div><b>Online-Antrag</b><p>Du gibst Name, Adresse, Beruf, Einkommen und Ausgaben an. Ehrliche Angaben sind wichtig, sonst droht die Kündigung.</p></div></div>
<div class="step"><span class="no">3</span><div><b>Identität bestätigen</b><p>Meist per Video-Ident oder mit dem Online-Ausweis, manchmal per Post-Ident oder in der Filiale.</p></div></div>
<div class="step"><span class="no">4</span><div><b>Bonitätsprüfung</b><p>Die Bank fragt {"die Schufa" if land=="de" else "den KSV1870"} ab und legt deinen Kreditrahmen fest.</p></div></div>
<div class="step"><span class="no">5</span><div><b>Karte aktivieren</b><p>Die Karte kommt per Post, den PIN bekommst du getrennt oder in der App.</p></div></div></div>'''),
            ('Warum Anträge abgelehnt werden',f'<div class="prose"><p>Die häufigsten Gründe sind ein schwacher {"Schufa-Score" if land=="de" else "Eintrag beim KSV1870"}, zu niedriges oder unregelmäßiges Einkommen, eine kurze Zeit an der aktuellen Adresse oder viele Kreditanfragen in kurzer Zeit. Stell deshalb nicht mehrere Anträge gleichzeitig. Wenn es nicht klappt, ist eine <a href="../ohne-bonitaetspruefung/">Debit- oder Prepaid-Karte</a> eine gute Alternative.</p></div>'),
            ('Tipps für einen guten Start','<div class="prose"><ul><li>Stell die Rückzahlung auf 100 %, damit keine Zinsen anfallen.</li><li>Aktiviere Apple Pay oder Google Pay, dann kannst du sofort zahlen.</li><li>Prüfe den Kreditrahmen und erhöhe ihn bei Bedarf vor einer Reise.</li><li>Lies die Versicherungsbedingungen, bevor du eine Reise buchst.</li></ul></div>')],
      faq=[('Wie lange dauert ein Kreditkartenantrag?','Bei Direktbanken kommt die Zusage oft in wenigen Minuten. Die Karte ist meist nach 5 bis 10 Werktagen da.'),
           (f'Schadet ein Kreditkartenantrag {"der Schufa" if land=="de" else "meiner Bonität"}?',
            'Eine normale Anfrage zur Kreditkarte senkt den Schufa-Score nicht dauerhaft. Viele Anfragen in kurzer Zeit können aber Banken vorsichtig machen.' if land=='de' else 'Eine einzelne Anfrage ist kein Problem. Viele Anträge in kurzer Zeit können Banken aber vorsichtig machen, weil sie beim KSV1870 sichtbar sind.'),
           ('Kann ich eine Kreditkarte ohne Einkommen bekommen?','Echte Kreditkarten setzen meist ein regelmäßiges Einkommen voraus. Studierende bekommen oft Karten mit kleinem Rahmen. Ohne Einkommen sind Debit- oder Prepaid-Karten die Alternative.'),
           (f'Welche Kreditkarte ist in {N} am besten?',f'In unserer Gesamtwertung liegt die {credit[0]["titel"]} vorne ({de1(credit[0]["stars"])} Sterne, Stand {STAND_DE}).')],
      related=['kostenlose-kreditkarte','ohne-bonitaetspruefung','kartentypen'])
    # C) ohne Bonitätsprüfung
    art(land,'ohne-bonitaetspruefung',
      h1=('Kreditkarte ohne Schufa: was wirklich geht' if land=='de' else 'Kreditkarte ohne KSV-Abfrage: was wirklich geht'),
      mt=('Kreditkarte ohne Schufa? Was wirklich geht | Finvallo' if land=='de' else 'Kreditkarte ohne KSV? Was wirklich geht | Finvallo'),
      desc=f'Kreditkarte ohne {"Schufa" if land=="de" else "KSV-Prüfung"}? Was seriös geht, welche Debit- und Prepaid-Karten es in {N} ohne Kreditprüfung gibt und wovor du dich hüten solltest.',
      lede=f'Echte Kreditkarten gibt es nicht ohne Bonitätsprüfung. Diese Alternativen funktionieren in {N} trotzdem.',
      kurz=f'Eine echte Kreditkarte mit Kreditrahmen bekommst du in {N} nicht ohne {"Schufa-Abfrage" if land=="de" else "Bonitätsprüfung"}. Debit- und Prepaid-Karten mit Visa oder Mastercard gibt es dagegen meist ohne Kreditprüfung, viele ohne Grundgebühr. Sie funktionieren fast überall, werden aber bei Mietwagen- und Hotelkautionen oft abgelehnt. Meide Angebote, die Vorkasse oder Gebühren für die „Vermittlung“ verlangen.',
      secs=[('Warum Kreditkarten geprüft werden',f'<div class="prose"><p>Bei einer Kredit- oder Charge-Karte gibt dir die Bank Geld im Voraus, bis die Monatsrechnung bezahlt ist. Deshalb muss sie nach dem Gesetz prüfen, ob du das zurückzahlen kannst. Sie fragt dazu {"die Schufa" if land=="de" else "den KSV1870"} ab.</p></div>'),
            (f'Gute Alternativen ohne Kreditprüfung',table(deb_free[:8]+[c for c in deb if c['typ']=='Prepaid' and c not in deb_free][:3],[COL['karte'],COL['typ'],COL['fee'],COL['fx'],COL['cash'],COL['stars']],P)+f'<p class="note">Debitkarten ohne Grundgebühr und Prepaid-Karten, sortiert nach unserer Bewertung. Bei Kontoeröffnung wird deine Identität geprüft, eine Kreditprüfung gibt es meist nicht. <a class="lnk" href="{best}debit/">Alle Debitkarten ansehen →</a></p>'),
            ('Vorsicht bei diesen Angeboten','<div class="prose"><ul><li>Anbieter, die vor der Zusage Geld verlangen, etwa als Vorkasse, für „Bearbeitung“ oder für eine Vermittlung</li><li>Karten mit hohen Monats- oder Aufladegebühren</li><li>Werbung mit „garantierter Zusage“ für echte Kreditkarten</li></ul><p>Seriöse Banken verlangen keine Vorauszahlung für einen Kreditkartenantrag.</p></div>'),
            (f'{"Schufa" if land=="de" else "Bonität"} verbessern',f'<div class="prose"><p>{"Fordere einmal im Jahr deine kostenlose Datenkopie bei der Schufa an und lass falsche Einträge löschen. Zahle Rechnungen pünktlich und stelle nicht viele Kreditanfragen auf einmal." if land=="de" else "Du kannst beim KSV1870 kostenlos Auskunft über deine Daten verlangen und falsche Einträge korrigieren lassen. Zahle Rechnungen pünktlich und stelle nicht viele Kreditanfragen auf einmal."} Nach einiger Zeit klappt es dann oft auch mit einer echten Kreditkarte.</p></div>')],
      faq=[(f'Gibt es eine Kreditkarte ganz ohne {"Schufa" if land=="de" else "KSV"}?','Echte Kreditkarten mit Kreditrahmen nicht. Debit- und Prepaid-Karten mit Visa oder Mastercard bekommst du meist ohne Kreditprüfung.'),
           ('Kann ich mit einer Debitkarte online bezahlen?','Ja. Debitkarten mit Visa oder Mastercard funktionieren online, im Ausland und mit Apple Pay oder Google Pay fast wie eine Kreditkarte.'),
           ('Wo gibt es Probleme mit Debitkarten?','Vor allem bei Kautionen für Mietwagen und Hotels. Dort verlangen viele Anbieter eine echte Kreditkarte.')],
      related=['kartentypen','kreditkarte-beantragen','mietwagen-kaution'])
    # D) Visa, Mastercard oder Amex
    from collections import Counter
    nets=Counter('Amex' if 'American' in c['netz'] else 'Visa' if c['netz']=='Visa' else 'Mastercard' if c['netz']=='Mastercard' else 'beide' for c in C)
    amex=[c for c in RC if 'American' in c['netz']]
    amexfx=sorted({c['fx'] for c in amex if c['fx'] is not None})
    art(land,'visa-mastercard-amex',
      h1='Visa, Mastercard oder American Express?',
      mt=f'Visa, Mastercard oder Amex in {N}? Unterschiede | Finvallo',
      desc=f'Visa, Mastercard oder American Express: Akzeptanz, Wechselkurse und Gebühren im Vergleich, mit Zahlen aus {len(C)} Karten in {N}.',
      lede='Welches Kartennetz du wählst, ist weniger wichtig als die Gebühren der Bank. Ein Unterschied bleibt aber.',
      kurz=f'Visa und Mastercard werden in {N} und weltweit praktisch überall gleich gut angenommen, die Wechselkurse liegen nah beieinander. Wichtiger sind die Gebühren deiner Bank. American Express wird seltener akzeptiert und verlangt in unserem Vergleich {fmtlist([pct(x) for x in amexfx]) if amexfx else "eine eigene Gebühr"} für Zahlungen in fremder Währung, punktet aber mit Membership Rewards, Versicherungen und Guthaben.',
      secs=[('Akzeptanz',f'<div class="prose"><p>Visa und Mastercard sind fast überall dabei, im Handel, online und am Geldautomaten. American Express nehmen viele große Ketten, Hotels und Airlines an, kleinere Geschäfte, Restaurants und Märkte aber oft nicht. Wer Amex nutzt, sollte deshalb eine zweite Karte mit Visa oder Mastercard dabeihaben.</p></div>'),
            ('Wechselkurse und Gebühren','<div class="prose"><p>Visa und Mastercard rechnen zu ihren eigenen Tageskursen um, die Unterschiede sind meist klein. Den Ausschlag gibt das Auslandseinsatzentgelt deiner Bank: von 0 % bis über 2 %. Mehr dazu in <a href="../fremdwaehrung/">Gebühren im Ausland verstehen</a>.</p></div>'),
            (f'So verteilen sich die Karten in {N}',f'<div class="tbl"><table><thead><tr><th>Netz</th><th>Karten im Vergleich</th></tr></thead><tbody>'+''.join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k,v in [('Visa',nets['Visa']),('Mastercard',nets['Mastercard']),('American Express',nets['Amex']),('Visa oder Mastercard wählbar',nets['beide'])] if v)+'</tbody></table></div>'),
            ('Die besten Karten je Netz',''.join(f'<h3>{n}</h3>'+table([c for c in RC if f(c)][:3],[COL['karte'],COL['fee'],COL['fx'],COL['stars']],P) for n,f in [('Visa',lambda c:c['netz']=='Visa'),('Mastercard',lambda c:c['netz']=='Mastercard'),('American Express',lambda c:'American' in c['netz'])] if any(f(c) for c in RC)))],
      faq=[('Ist Visa oder Mastercard besser?','Für dich als Kunde gibt es kaum Unterschiede bei Akzeptanz und Kurs. Entscheidend sind die Gebühren und Leistungen der Karte.'),
           ('Warum nimmt nicht jeder American Express?','Händler zahlen für Amex meist höhere Gebühren als für Visa oder Mastercard. Deshalb verzichten vor allem kleinere Geschäfte darauf.'),
           ('Lohnt sich American Express trotzdem?','Für Vielreisende oft ja: Punkteprogramm, Guthaben und Versicherungen können die Jahresgebühr aufwiegen. Als einzige Karte ist sie wegen der Akzeptanz aber nicht ideal.')],
      related=['fremdwaehrung',WHY_AMEX[land][0],'kostenlose-kreditkarte'])
    # E) Mietwagen & Kaution
    rent=[c for c in credit if (c['tier'] or 0)>=3]
    rent=sorted(rent,key=lambda c:(c['fee'] if c['fee'] is not None else 1e9))
    kau=sorted([c for c in credit if re.search(r'visa|mastercard',c['netz'],re.I)],key=lambda c:(c['fee'] if c['fee'] is not None else 1e9,-(c.get('stars') or 0)))
    art(land,'mietwagen-kaution',
      h1='Kreditkarte für Mietwagen und Kaution',
      mt=f'Mietwagen-Kaution mit Kreditkarte ({N}) | Finvallo',
      desc=f'Warum Autovermieter eine Kreditkarte für die Kaution wollen, was mit Debitkarten passiert und welche Karten in {N} Mietwagenschutz enthalten.',
      lede='Am Mietwagenschalter entscheidet die Karte, ob du dein Auto bekommst. Das musst du wissen.',
      kurz=f'Autovermieter blockieren für die Kaution meist mehrere hundert Euro auf einer echten Kreditkarte, die auf den Namen der fahrenden Person läuft. Debit- und Prepaid-Karten werden oft abgelehnt oder nur gegen teure Zusatzversicherung akzeptiert. {len(rent)} Kreditkarten in unserem {N}-Vergleich enthalten einen umfassenden Reiseschutz inklusive Mietwagen-Absicherung, die günstigste davon ist die {rent[0]["titel"]}.' if rent else 'Autovermieter blockieren für die Kaution meist mehrere hundert Euro auf einer echten Kreditkarte.',
      secs=[('So funktioniert die Kaution','<div class="prose"><p>Beim Abholen reserviert der Vermieter einen Betrag auf deiner Karte, meist zwischen 300 und 1.500 €. Das Geld wird nicht abgebucht, aber dein Kreditrahmen ist in dieser Höhe blockiert. Nach der Rückgabe wird die Reservierung aufgehoben, das kann einige Tage dauern. Plane deshalb genug Rahmen ein, vor allem im Urlaub.</p></div>'),
            ('Warum Debitkarten oft nicht reichen','<div class="prose"><p>Bei einer Debitkarte wird der Betrag direkt vom Konto reserviert. Viele Vermieter akzeptieren das nicht, weil sie im Schadensfall eine Kreditkarte mit Kreditrahmen wollen. Manche nehmen Debitkarten nur, wenn du ihre Vollkasko ohne Selbstbehalt dazubuchst. Lies die Bedingungen deiner Buchung vorher genau.</p></div>'),
            ('Karten, die für Kautionen geeignet sind',(table(kau[:10],[COL['karte'],COL['typ'],COL['netz'],COL['fee']],P)+f'<p class="note">Kredit- und Charge-Karten mit Visa oder Mastercard, also mit Kreditrahmen und der breitesten Akzeptanz, sortiert nach Jahresgebühr. Hier stehen die 10 günstigsten der {len(kau)} passenden aus unserem {N}-Vergleich. Ob der Vermieter die Karte annimmt, prüfst du am besten vorher.</p>') if kau else '<p>Aktuell keine passende Karte in unserem Vergleich.</p>'),
            ('Karten mit Mietwagen-Versicherung',(table(rent[:10],[COL['karte'],COL['fee'],COL['ins'],COL['stars']],P)+f'<p class="note">Kredit- und Charge-Karten mit umfassendem oder Premium-Reiseschutz, sortiert nach Jahresgebühr. Was genau versichert ist, steht auf jeder Kartenseite.</p>') if rent else '<p>Aktuell keine Karte mit Mietwagenschutz in unserem Vergleich.</p>'),
            ('Checkliste vor der Abholung','<div class="prose"><ul><li>Echte Kredit- oder Charge-Karte mit Hochprägung oder Name auf der Karte</li><li>Karte lautet auf die Person im Mietvertrag</li><li>Genug freier Kreditrahmen für die Kaution</li><li>Führerschein und Ausweis</li><li>Mietwagen mit der Karte bezahlt, damit deren Versicherung greift</li></ul></div>')],
      faq=[('Kann ich einen Mietwagen mit Debitkarte mieten?','Manchmal, aber oft nur mit Aufpreis oder Zusatzversicherung. Sicherer ist eine echte Kreditkarte.'),
           ('Wie hoch ist die Kaution beim Mietwagen?','Meist 300 bis 1.500 €, bei Premiumautos mehr. Der Betrag wird reserviert und nach der Rückgabe wieder freigegeben.'),
           ('Ersetzt die Kreditkarte die Vollkasko des Vermieters?','Manche Karten erstatten den Selbstbehalt oder bieten eine eigene Vollkasko, wenn du den Wagen mit der Karte bezahlst. Die Bedingungen unterscheiden sich stark.')],
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
    if land=='de':
        import karten, ratgeber_bargeld_de
        ratgeber_bargeld_de.register(art,P,best,cards.D['de'][0],karten.card_count('de','private'),eur,karten)
        import ratgeber_reise_de; ratgeber_reise_de.register(art,P,best,cards.D['de'][0],karten.card_count('de','private'),eur,karten)
        import ratgeber_studenten_de; ratgeber_studenten_de.register(art,P,best,cards.D['de'][0],karten.card_count('de','private'),eur,karten)
        import ratgeber_wallet_de; ratgeber_wallet_de.register(art,P,best,cards.D['de'][0],karten.card_count('de','private'),eur,karten)
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
 'kartentypen':[('Hohe Zinsen bei Teilzahlung (in Österreich rund 22–25 % effektiv)','Hohe Zinsen bei Teilzahlung (in Deutschland rund 15–25 % effektiv)'),
                ('In Österreich der Standard bei Bankkarten.','In Deutschland der Standard bei Karten von Sparkassen, Volksbanken und vielen Filialbanken.')],
 'teilzahlung':[('In Österreich liegen diese Zinsen bei den gebührenfreien Karten bei rund 25 % effektiv im Jahr.','In Deutschland liegen diese Zinsen bei den gebührenfreien Karten meist zwischen 18 und 25 % effektiv im Jahr.')],
 'business':[('../../../at/kreditkarten/business/','../../kreditkarten/business/')],
 'reiseversicherung':[('../../../at/kreditkarten/bestenlisten/reisen/','../../kreditkarten/bestenlisten/reisen/')],
}
PAIRS={('at','punkte-sammeln-at'):('de','punkte-sammeln-de'),('de','punkte-sammeln-de'):('at','punkte-sammeln-at'),('at','bargeld-beheben'):('de','bargeld-abheben'),('de','bargeld-abheben'):('at','bargeld-beheben')}
WHY_AMEX={'at':('punkte-sammeln-at','Österreich'),'de':('punkte-sammeln-de','Deutschland')}
def why_amex(land):
    slug,N=WHY_AMEX[land]
    return (f'<h2 id="bestenliste">Warum steht Amex in der Bestenliste nicht auf Platz 1?</h2><div class="prose"><p>Beide Rechnungen stimmen, sie gehen nur von verschiedenen Nutzern aus. '
            f'Unsere <a href="../../kreditkarten/bestenlisten/punkte/">Bestenliste Meilen &amp; Punkte</a> bewertet jeden Punkt vorsichtig mit 1 Cent, rechnet mit 1.000 € Umsatz im Monat und zieht Jahresgebühr und Aufpreise ab. Sie zeigt also, was nach der Gebühr übrig bleibt. '
            f'So passt sie für die meisten, die Punkte für Gutscheine oder Economy-Flüge einlösen. Dort liegen Karten mit niedriger Gebühr vorne, die teure Gold Card und Platinum Card landen weiter hinten. Wer lieber Geld zurück will, findet die <a href="../../kreditkarten/bestenlisten/cashback/">Bestenliste Cashback</a>.</p>'
            f'<p>Dieser Ratgeber rechnet dagegen mit 1 bis 2 Cent pro Punkt und dem Turbo-Bonus. Diesen Wert erreichst du nur, wenn du die Punkte gezielt in Business- oder First-Class-Flüge über Partnerprogramme tauschst. '
            f'Wenn du das vorhast und viel mit der Karte zahlst, lohnt sich American Express. Wenn nicht, nimm eine Karte aus der Bestenliste.</p></div>')

PROG={'at':'<div class="prose"><p>Vier Wege, mit österreichischen Kreditkarten zu sammeln:</p><ul>\n<li><b>Membership Rewards (American Express):</b> 1 Punkt pro Euro, bei der Gold Card mit Turbo 1,5. Die Teilnahme kostet bei der Gold Card 30 € im Jahr, bei der Platinum Card ist sie inklusive. Punkte lassen sich in Partnerprogramme übertragen, die Liste steht oben.</li>\n<li><b>Miles &amp; More:</b> das Programm von Austrian, Lufthansa und Swiss. Direkt sammelst du mit der Austrian Miles &amp; More Premiumcard von Erste Bank und Sparkasse (1 Meile je 1,50 €), indirekt über das Bonusprogramm von Diners Club (1 Punkt je 8 €, 4 Meilen je Punkt, 25 € im Jahr).</li>\n<li><b>Hotelpunkte:</b> die Hilton Honors Kreditkarte gibt 1 Punkt pro Euro, 2 in Hilton-Hotels. Pro Stück sind Hotelpunkte deutlich weniger wert als Meilen.</li>\n<li><b>Cashback und App-Banken:</b> Revolut sammelt RevPoints, Trade Republic zahlt 1 % Saveback in den Sparplan, die Erste Bank gibt bis 0,6 % Online-Cashback. Einfach, aber meist weniger als gut eingelöste Meilen.</li></ul>\n<p>Punkte, die du in mehrere Programme übertragen kannst, sind am flexibelsten: Du entscheidest erst beim Einlösen, wo sie am meisten bringen. Übertragungen gehen nur in eine Richtung, also erst übertragen, wenn die Prämie feststeht.</p></div>',
      'de':'<div class="prose"><p>Vier Wege, mit deutschen Kreditkarten zu sammeln:</p><ul>\n<li><b>Membership Rewards (American Express):</b> 1 Punkt pro Euro bei Gold und Platinum (mit Turbo 1,5), bei der Blue Card nur gegen Aufpreis. Übertragbar auf Airline- und Hotelprogramme, die Liste steht oben.</li>\n<li><b>Miles &amp; More:</b> mit den Miles &amp; More Credit Cards 1 Meile je 2 €, für Prämienflüge bei Lufthansa, Austrian, Swiss und Partnern; mit Blue und Gold verfallen die Meilen nicht.</li>\n<li><b>Payback:</b> mit der Payback American Express 1 Punkt je 3 €, 1 Punkt ist 1 Cent wert und lässt sich 1:1 zu Miles &amp; More übertragen.</li>\n<li><b>Cashback:</b> Geld zurück auf jeden Einkauf, etwa 0,5 % bei der WEB.Cent-Karte, oder Partner-Cashback bei vielen Banken. Am einfachsten zu vergleichen, weil der Wert feststeht.</li></ul>\n<p>Punkte, die du in mehrere Programme übertragen kannst, sind am flexibelsten: Du entscheidest erst beim Einlösen, wo sie am meisten bringen. Übertragungen gehen nur in eine Richtung, also erst übertragen, wenn die Prämie feststeht.</p></div>'}
WERT={'at':[('Cashback','genau 1 Cent pro Cent'),('Miles &amp; More Meile','rund 1 Cent, bei Business-Class-Flügen oft mehr'),('Membership-Rewards-Punkt','0,5 bis 1 Cent, bei Flügen über Transferpartner 1 bis 2 Cent'),('Hilton-Punkt','0,4 bis 0,5 Cent'),('Sachprämien und Gutscheine','oft deutlich weniger als 1 Cent')],
      'de':[('Cashback','genau 1 Cent pro Cent'),('Payback-Punkt','fest 1 Cent, als Miles &amp; More Meile bei Flügen mehr'),('Miles &amp; More Meile','rund 1 Cent, bei Business-Class-Flügen oft mehr'),('Membership-Rewards-Punkt','0,5 bis 1 Cent, bei Flügen über Transferpartner 1 bis 2 Cent'),('Hilton-Punkt','0,4 bis 0,5 Cent'),('Sachprämien und Gutscheine','oft deutlich weniger als 1 Cent')]}
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
ORDER=['kostenlose-kreditkarte','kreditkarte-studenten','kreditkarte-beantragen','fremdwaehrung','bargeld-beheben','bargeld-abheben','reiseversicherung','flugverspaetung-gepaeck','punkte-sammeln-at','punkte-sammeln-de','lounges','visa-mastercard-amex','apple-pay-google-pay','mietwagen-kaution','ohne-bonitaetspruefung','kartentypen','teilzahlung','business']
def index_pages():
    for land in ('at','de'):
        f=R+f'{land}/ratgeber/index.html'; s=open(f).read()
        ss=sorted(slugs(land),key=lambda x:ORDER.index(x) if x in ORDER else 99)
        tiles=''.join(f'<a class="catcard" href="{x}/"><b>{E(meta(land,x)[0])}</b><span style="color:var(--muted)">{E(meta(land,x)[1][:150])}</span><small>Lesen →</small></a>' for x in ss)
        s=re.sub(r'(<main id="app">.*?<div class="catgrid">).*?(</div>\s*</main>)',lambda m:m.group(1)+tiles+m.group(2),s,count=1,flags=re.S)
        s=re.sub(r'<p class="lede">[^<]*</p>',f'<p class="lede">{len(ss)} Beiträge, verständlich erklärt und mit Zahlen aus unserem Vergleich. Alle Beiträge gelten für {LAND[land]["name"]}.</p>',s,count=1)
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
def run():
    for land in ('at','de'): build(land)
    for (land,slug) in ARTS: render(land,slug)
    fix_static(); hreflang_all(); index_pages(); sitemap_llms()
    print('Artikel neu/überarbeitet:',len(ARTS))
if __name__=='__main__': run()
