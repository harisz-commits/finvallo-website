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
    out=[]
    if land=='at':
        rj=json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>',open(R+'at/kreditkarten/rechner/index.html').read(),re.S).group(1))
        urls={c['id']:c for c in json.load(open(R+'at/daten/kreditkarten.json'))['karten']}
        for c in rj['cards']:
            if c.get('land')!='AT' or c['id'] not in urls: continue
            u=urls[c['id']]
            out.append(dict(titel=u['titel'],url=u['url'].replace('https://finvallo.com/',''),fee=c.get('fee'),fx=c.get('fx'),fxText=c.get('fxText'),cashText=c.get('cashText'),
              stars=c.get('stars'),tier=c.get('tier'),typ=c['typ'],netz=c.get('netz') or '',giro=c.get('giro'),auto=c.get('auto'),art=c.get('art','Privat'),
              lg=c.get('lg') if c.get('lgf') else None,cb=c.get('cb') or c.get('earn'),ml=c.get('ml'),klasse=c.get('klasse'),bestand=c.get('bestand'),cash=c.get('cash')))
    else:
        import gen_de
        cs=gen_de.load(); gen_de.ratecards(cs)
        for c in cs:
            out.append(dict(titel=c['titel'],url=f'de/kreditkarten/{c["slug"]}/',fee=c.get('fee'),fx=c.get('fx'),fxText=gen_de.fxT(c),cashText=gen_de.cashT(c),
              stars=c.get('stars'),tier=c.get('tier'),typ=c['typ'],netz=c.get('netz') or '',giro=c.get('giro'),auto=c.get('auto'),art=c['art'],
              lg=c.get('lgText') if c['ex'].get('lg') else None,cb=c.get('cbText') if c['ex'].get('cb') else None,ml=c['ex'].get('ml'),klasse=c['klasse'],bestand=c.get('nurfuer'),cash=c.get('cash')))
    return [c for c in out if c['art']=='Privat' and not c.get('bestand')]
def rated(L): return sorted([c for c in L if c.get('stars') is not None],key=lambda c:(-c['stars'],c['fee'] if c['fee'] is not None else 1e9))
def link(c,P): return f'<a class="lnk" href="{P}{c["url"]}">{E(c["titel"])}</a>'
def table(rows,cols,P):
    h=''.join(f'<th>{c[0]}</th>' for c in cols)
    b=''.join('<tr>'+''.join(f'<td>{f(c,P)}</td>' for _,f in cols)+'</tr>' for c in rows)
    return f'<div class="tbl wide"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'
COL=dict(karte=('Karte',lambda c,P:link(c,P)),
         fee=('Jahresgebühr',lambda c,P:'kostenlos' if c['fee']==0 else (f'{eur(c["fee"])} €' if c['fee'] is not None else '–')),
         fx=('Ausland',lambda c,P:E(c['fxText'] if c['fx'] not in (0,None) else ('0 %' if c['fx']==0 else '–'))[:60]),
         cash=('Bargeld',lambda c,P:E((c['cashText'] or '–')[:60])),
         ins=('Reiseversicherung',lambda c,P:TIERN.get(c['tier'],'–') if c['tier'] is not None else '–'),
         stars=('Bewertung',lambda c,P:f'{de1(c["stars"])} ★' if c.get('stars') is not None else '–'),
         netz=('Netz',lambda c,P:E(c['netz'])),typ=('Typ',lambda c,P:E(c['typ'])),
         lg=('Lounge',lambda c,P:E((c['lg'] or '')[:90])),cb=('Sammeln',lambda c,P:E((c['cb'] or '')[:90])))
# ---------- Seite ----------
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
<meta name="author" content="Finvallo-Redaktion">
<meta property="article:modified_time" content="{STAND}">
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
<nav aria-label="Fußzeile"><a href="{P}{land}/kreditkarten/methodik/">So bewerten wir</a><a href="{P}so-verdienen-wir-geld/">So verdienen wir Geld</a><a href="{P}ueber-uns/">Über uns</a><a href="{P}impressum/">Impressum</a><a href="{P}datenschutz/">Datenschutz</a><a href="{P}llms.txt">Für KI-Assistenten</a></nav>
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
    # A) kostenlose Kreditkarte
    t3=free[:3]
    art(land,'kostenlose-kreditkarte',
      h1=f'Kostenlose Kreditkarte in {N}: die besten ohne Jahresgebühr',
      mt=f'Kostenlose Kreditkarte {N} 2026: Vergleich | Finvallo',
      desc=f'Kostenlose Kreditkarten in {N} im Vergleich: {len(free)} echte Kredit- und Charge-Karten ohne Jahresgebühr, mit Auslandsgebühren, Bargeld und Versicherung.',
      lede=f'Ohne Jahresgebühr heißt nicht automatisch kostenlos. Hier siehst du, welche Karten in {N} wirklich nichts kosten und wo die Haken liegen.',
      kurz=(f'In {N} gibt es laut unserem Vergleich {len(free)} echte Kredit- oder Charge-Karten ohne Jahresgebühr. Am besten bewertet sind {fmtlist([c["titel"]+f" ({de1(c["stars"])} Sterne)" for c in t3])}. '
            +(f'{len(free_ins)} davon haben sogar eine Reiseversicherung mit Reiserücktritt. ' if free_ins else '')+'Achte trotzdem auf Auslandsgebühren, Bargeldkosten und Zinsen bei Teilzahlung.'),
      secs=[('Die besten kostenlosen Kreditkarten',table(free[:12],[COL['karte'],COL['fx'],COL['cash'],COL['ins'],COL['stars']],P)+f'<p class="note">Nur Karten ohne Jahresgebühr, sortiert nach unserer Bewertung. <a class="lnk" href="{best}gratis/">Ganze Bestenliste ansehen →</a></p>'),
            ('Was „kostenlos“ wirklich bedeutet',f'''<div class="prose"><p>Eine Kreditkarte ohne Jahresgebühr kann trotzdem Geld kosten. Prüfe vor dem Antrag vier Punkte:</p><ul>
<li><b>Zahlen in fremder Währung:</b> Viele Karten verlangen 1,5 bis 2,5 % pro Zahlung außerhalb des Euroraums. Die besten Gratiskarten verlangen 0 %.</li>
<li><b>Bargeld {AB}:</b> Manche Karten nehmen eine feste Gebühr, andere verzinsen Bargeld ab dem ersten Tag.</li>
<li><b>Teilzahlung:</b> Bei echten Kreditkarten ist oft eine Ratenzahlung voreingestellt. Dann zahlst du rund 16 bis 25 % effektive Zinsen pro Jahr. Stell die Rückzahlung auf 100 % um.</li>
<li><b>Girokonto-Pflicht:</b> Manche Karten sind nur gratis, wenn du ein Konto beim Anbieter hast, das selbst etwas kostet.</li></ul></div>'''),
            ('Kostenlose Kreditkarte oder Debitkarte?',f'<div class="prose"><p>Viele Banken und App-Banken geben gratis eine Debitkarte aus. Die bucht jede Zahlung sofort vom Konto ab und hat keinen Kreditrahmen. Für den Alltag reicht das meist. Mietwagenfirmen und Hotels verlangen für die Kaution aber oft eine echte Kreditkarte. Mehr dazu in unseren Beiträgen zu <a href="../kartentypen/">Kartentypen</a> und <a href="../mietwagen-kaution/">Mietwagen-Kaution</a>.</p></div>')],
      faq=[(f'Welche kostenlose Kreditkarte ist in {N} die beste?',f'Laut Finvallo-Bewertung ist es die {free[0]["titel"]} mit {de1(free[0]["stars"])} von 5 Sternen, Stand {STAND_DE}.' if free else 'Aktuell keine.'),
           ('Ist eine kostenlose Kreditkarte wirklich gratis?','Die Jahresgebühr ist 0 €. Kosten entstehen aber bei Fremdwährung, Bargeld oder wenn du die Rechnung nicht vollständig zahlst. Mit der richtigen Karte und voller Rückzahlung bleibt sie gratis.'),
           ('Brauche ich für eine kostenlose Kreditkarte ein neues Girokonto?',f'Nicht unbedingt. {sum(1 for c in free if c["giro"] is False)} der {len(free)} Gratiskarten in unserem Vergleich funktionieren mit deinem bestehenden Konto.'),
           (f'Wird bei einer kostenlosen Kreditkarte die {AUS} geprüft?',f'Ja. Für jede echte Kredit- oder Charge-Karte prüft die Bank deine Bonität, in {N} meist über {"die Schufa" if land=="de" else "den KSV1870"}.')],
      related=['kreditkarte-beantragen','fremdwaehrung','teilzahlung'])
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
      mt=('Kreditkarte ohne Schufa 2026: echte Alternativen | Finvallo' if land=='de' else 'Kreditkarte ohne KSV 2026: echte Alternativen | Finvallo'),
      desc=f'Kreditkarte ohne {"Schufa" if land=="de" else "KSV-Prüfung"}? Was seriös geht, welche Debit- und Prepaid-Karten es in {N} ohne Kreditprüfung gibt und wovor du dich hüten solltest.',
      lede=f'Echte Kreditkarten gibt es nicht ohne Bonitätsprüfung. Diese Alternativen funktionieren in {N} trotzdem.',
      kurz=f'Eine echte Kreditkarte mit Kreditrahmen bekommst du in {N} nicht ohne {"Schufa-Abfrage" if land=="de" else "Bonitätsprüfung"}. Debit- und Prepaid-Karten mit Visa oder Mastercard gibt es dagegen meist ohne Kreditprüfung, viele ohne Grundgebühr. Sie funktionieren fast überall, werden aber bei Mietwagen- und Hotelkautionen oft abgelehnt. Meide Angebote, die Vorkasse oder Gebühren für die „Vermittlung“ verlangen.',
      secs=[('Warum Kreditkarten geprüft werden',f'<div class="prose"><p>Bei einer Kredit- oder Charge-Karte gibt dir die Bank Geld im Voraus, bis die Monatsrechnung bezahlt ist. Deshalb muss sie nach dem Gesetz prüfen, ob du das zurückzahlen kannst. Sie fragt dazu {"die Schufa" if land=="de" else "den KSV1870"} ab.</p></div>'),
            (f'Gute Alternativen ohne Kreditprüfung',table(deb_free[:10],[COL['karte'],COL['typ'],COL['fx'],COL['cash'],COL['stars']],P)+f'<p class="note">Debit- und Prepaid-Karten ohne Grundgebühr, sortiert nach unserer Bewertung. Bei Kontoeröffnung wird deine Identität geprüft, eine Kreditprüfung gibt es meist nicht. <a class="lnk" href="{best}debit/">Alle Debitkarten ansehen →</a></p>'),
            ('Vorsicht bei diesen Angeboten','<div class="prose"><ul><li>Anbieter, die vor der Zusage Geld verlangen, etwa für Nachnahme, „Bearbeitung“ oder eine Vermittlung</li><li>Karten mit hohen Monats- oder Aufladegebühren</li><li>Werbung mit „garantierter Zusage“ für echte Kreditkarten</li></ul><p>Seriöse Banken verlangen keine Vorauszahlung für einen Kreditkartenantrag.</p></div>'),
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
      faq=[('Ist Visa oder Mastercard besser?','Für dich als Kund:in gibt es kaum Unterschiede bei Akzeptanz und Kurs. Entscheidend sind die Gebühren und Leistungen der Karte.'),
           ('Warum nimmt nicht jeder American Express?','Händler zahlen für Amex meist höhere Gebühren als für Visa oder Mastercard. Deshalb verzichten vor allem kleinere Geschäfte darauf.'),
           ('Lohnt sich American Express trotzdem?','Für Vielreisende oft ja: Punkteprogramm, Guthaben und Versicherungen können die Jahresgebühr aufwiegen. Als einzige Karte ist sie wegen der Akzeptanz aber nicht ideal.')],
      related=['fremdwaehrung','punkte','kostenlose-kreditkarte'])
    # E) Mietwagen & Kaution
    rent=[c for c in credit if (c['tier'] or 0)>=3]
    rent=sorted(rent,key=lambda c:(c['fee'] if c['fee'] is not None else 1e9))
    art(land,'mietwagen-kaution',
      h1='Kreditkarte für Mietwagen und Kaution',
      mt=f'Mietwagen-Kaution mit Kreditkarte ({N}) | Finvallo',
      desc=f'Warum Autovermieter eine Kreditkarte für die Kaution wollen, was mit Debitkarten passiert und welche Karten in {N} Mietwagenschutz enthalten.',
      lede='Am Mietwagenschalter entscheidet die Karte, ob du dein Auto bekommst. Das musst du wissen.',
      kurz=f'Autovermieter blockieren für die Kaution meist mehrere hundert Euro auf einer echten Kreditkarte, die auf den Namen der fahrenden Person läuft. Debit- und Prepaid-Karten werden oft abgelehnt oder nur gegen teure Zusatzversicherung akzeptiert. {len(rent)} Kreditkarten in unserem {N}-Vergleich enthalten einen umfassenden Reiseschutz inklusive Mietwagen-Absicherung, die günstigste davon ist die {rent[0]["titel"]}.' if rent else 'Autovermieter blockieren für die Kaution meist mehrere hundert Euro auf einer echten Kreditkarte.',
      secs=[('So funktioniert die Kaution','<div class="prose"><p>Beim Abholen reserviert der Vermieter einen Betrag auf deiner Karte, meist zwischen 300 und 1.500 €. Das Geld wird nicht abgebucht, aber dein Kreditrahmen ist in dieser Höhe blockiert. Nach der Rückgabe wird die Reservierung aufgehoben, das kann einige Tage dauern. Plane deshalb genug Rahmen ein, vor allem im Urlaub.</p></div>'),
            ('Warum Debitkarten oft nicht reichen','<div class="prose"><p>Bei einer Debitkarte wird der Betrag direkt vom Konto reserviert. Viele Vermieter akzeptieren das nicht, weil sie im Schadensfall eine Kreditkarte mit Kreditrahmen wollen. Manche nehmen Debitkarten nur, wenn du ihre Vollkasko ohne Selbstbehalt dazubuchst. Lies die Bedingungen deiner Buchung vorher genau.</p></div>'),
            ('Karten mit Mietwagen-Versicherung',(table(rent[:10],[COL['karte'],COL['fee'],COL['ins'],COL['stars']],P)+f'<p class="note">Kredit- und Charge-Karten mit umfassendem oder Premium-Reiseschutz, sortiert nach Jahresgebühr. Was genau versichert ist, steht auf jeder Kartenseite.</p>') if rent else '<p>Aktuell keine Karte mit Mietwagenschutz in unserem Vergleich.</p>'),
            ('Checkliste vor der Abholung','<div class="prose"><ul><li>Echte Kredit- oder Charge-Karte mit Hochprägung oder Name auf der Karte</li><li>Karte lautet auf die Person im Mietvertrag</li><li>Genug freier Kreditrahmen für die Kaution</li><li>Führerschein und Ausweis</li><li>Mietwagen mit der Karte bezahlt, damit deren Versicherung greift</li></ul></div>')],
      faq=[('Kann ich einen Mietwagen mit Debitkarte mieten?','Manchmal, aber oft nur mit Aufpreis oder Zusatzversicherung. Sicherer ist eine echte Kreditkarte.'),
           ('Wie hoch ist die Kaution beim Mietwagen?','Meist 300 bis 1.500 €, bei Premiumautos mehr. Der Betrag wird reserviert und nach der Rückgabe wieder freigegeben.'),
           ('Ersetzt die Kreditkarte die Vollkasko des Vermieters?','Manche Karten erstatten den Selbstbehalt oder bieten eine eigene Vollkasko, wenn du den Wagen mit der Karte bezahlst. Die Bedingungen unterscheiden sich stark.')],
      related=['reiseversicherung','kartentypen','visa-mastercard-amex'])
    if land=='de':
        lou=[c for c in RC if c['lg']]
        art('de','lounges',h1='Lounge-Zugang mit der Kreditkarte',mt='Lounge-Zugang mit Kreditkarte in Deutschland | Finvallo',
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
        pts=[c for c in RC if c['cb'] or c['ml']][:12]
        art('de','punkte',h1='Punkte, Meilen und Cashback: der Einstieg',mt='Punkte & Meilen mit Kreditkarte (Deutschland) | Finvallo',
          desc='Punkte, Meilen oder Cashback? Welche Programme es in Deutschland gibt (Membership Rewards, Miles & More, Payback) und wie viel sie bringen.',
          lede='Welche Programme es in Deutschland gibt und wie viel sie wirklich bringen.',
          kurz='In Deutschland sammelst du mit Kreditkarten vor allem Membership Rewards (American Express), Meilen bei Miles & More, Payback-Punkte oder einfaches Cashback. Cashback ist am einfachsten, gut eingelöste Meilen und Punkte bringen meist mehr. Die Jahresgebühr sollte nicht höher sein als der Wert, den du sammelst.',
          secs=[('Die wichtigsten Programme','<div class="prose"><ul><li><b>Membership Rewards (Amex):</b> 1 Punkt pro Euro bei Gold und Platinum, übertragbar auf Airline- und Hotelprogramme. Bei der Blue Card nur gegen Aufpreis.</li><li><b>Miles & More:</b> Mit den Miles & More Credit Cards meist 1 Meile pro 2 €. Für Prämienflüge bei Lufthansa und Partnern.</li><li><b>Payback:</b> Mit den PAYBACK-Karten von American Express und Visa sammelst du °Punkte, 1 °Punkt ist 1 Cent wert.</li><li><b>Cashback:</b> Geld zurück auf jeden Einkauf, etwa 0,5 % bei der WEB.Cent-Karte oder Partner-Cashback bei vielen Banken.</li></ul></div>'),
                ('Karten mit Punkten, Meilen oder Cashback',table(pts,[COL['karte'],COL['cb'],COL['fee'],COL['stars']],P)+f'<p class="note"><a class="lnk" href="{best}punkte/">Bestenliste Meilen &amp; Punkte →</a></p>'),
                ('Was Punkte wert sind','<div class="prose"><p>Ein Payback-Punkt ist fest 1 Cent wert. Membership Rewards und Meilen sind am meisten wert, wenn du sie für Flüge in Business oder First Class einlöst. Für Sachprämien oder Gutscheine bekommst du oft deutlich weniger. Wie sich das rechnet, steht in <a href="../punkte-sammeln-de/">Lohnt sich Punktesammeln in Deutschland?</a></p></div>')],
          faq=[('Was ist besser: Cashback oder Meilen?','Cashback ist einfach und sicher. Meilen lohnen sich, wenn du gezielt Prämienflüge buchst.'),
               ('Bekomme ich Punkte für jede Zahlung?','Meist ja, aber oft nicht für Gebühren, Bargeld, Überweisungen oder bestimmte Händler wie Tankstellen.')],
          related=['punkte-sammeln-de','lounges','visa-mastercard-amex'])

# ---------- statische Artikel korrigieren, Übersichten, hreflang, Sitemap, llms ----------
DE_FIX={
 'kartentypen':[('Hohe Zinsen bei Teilzahlung (in Österreich rund 22–25 % effektiv)','Hohe Zinsen bei Teilzahlung (in Deutschland rund 15–25 % effektiv)'),
                ('In Österreich der Standard bei Bankkarten.','In Deutschland der Standard bei Karten von Sparkassen, Volksbanken und vielen Filialbanken.')],
 'teilzahlung':[('In Österreich liegen diese Zinsen bei den gebührenfreien Karten bei rund 25 % effektiv im Jahr.','In Deutschland liegen diese Zinsen bei den gebührenfreien Karten meist zwischen 18 und 25 % effektiv im Jahr.')],
 'business':[('../../../at/kreditkarten/business/','../../kreditkarten/business/')],
 'reiseversicherung':[('../../../at/kreditkarten/bestenlisten/reisen/','../../kreditkarten/bestenlisten/reisen/')],
}
PAIRS={('at','punkte-sammeln-at'):('de','punkte-sammeln-de'),('de','punkte-sammeln-de'):('at','punkte-sammeln-at')}
def fix_static():
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
ORDER=['kostenlose-kreditkarte','kreditkarte-beantragen','fremdwaehrung','reiseversicherung','punkte','punkte-sammeln-at','punkte-sammeln-de','lounges','visa-mastercard-amex','mietwagen-kaution','ohne-bonitaetspruefung','kartentypen','teilzahlung','business']
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
