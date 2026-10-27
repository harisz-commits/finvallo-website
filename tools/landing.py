# Erzeugt die Landingpages: / (Startseite), /at/, /de/ im gleichen Design.
import json,re,html,os,sys
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','public')+'/'
E=html.escape
STAR='M12 2.5l2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 17.4l-5.9 3.1 1.2-6.5L2.5 9.4l6.6-.9z'
FLAG={'AT':'<svg class="flag" viewBox="0 0 30 20" aria-hidden="true"><rect width="30" height="20" fill="#c8102e"/><rect y="6.67" width="30" height="6.67" fill="#fff"/></svg>',
      'DE':'<svg class="flag" viewBox="0 0 30 20" aria-hidden="true"><rect width="30" height="6.67" fill="#000"/><rect y="6.67" width="30" height="6.67" fill="#dd0000"/><rect y="13.33" width="30" height="6.67" fill="#ffce00"/></svg>'}
def stars(v,uid):
    out=''
    for i in range(5):
        f=max(0,min(1,v-i))
        if f>=.75: out+=f'<svg viewBox="0 0 24 24"><path d="{STAR}" fill="var(--star)"/></svg>'
        elif f>=.25: out+=f'<svg viewBox="0 0 24 24"><defs><linearGradient id="hs{uid}"><stop offset="50%" stop-color="var(--star)"/><stop offset="50%" stop-color="var(--star-off)"/></linearGradient></defs><path d="{STAR}" fill="url(#hs{uid})"/></svg>'
        else: out+=f'<svg viewBox="0 0 24 24"><path d="{STAR}" fill="var(--star-off)"/></svg>'
    return f'<span class="st" aria-hidden="true">{out}</span>'
def de(x): return f'{x:.1f}'.replace('.',',')
def ic(p): return f'<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{p}</svg>'
I={
'robo':'<rect x="5" y="8" width="14" height="11" rx="2.5"/><path d="M12 4v4M9 13h.01M15 13h.01M9.5 16h5"/>','btc':'<circle cx="12" cy="12" r="9"/><path d="M9.5 7.5v9M9.5 8h3.5a2 2 0 0 1 0 4H9.5h4a2 2 0 0 1 0 4H9.5M11 6v2M11 16v2"/>','lock':'<rect x="5" y="10" width="14" height="10" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
'card':'<rect x="2.5" y="5" width="19" height="14" rx="2.5"/><path d="M2.5 10h19M6 15h4"/>',
'trophy':'<path d="M8 4h8v5a4 4 0 0 1-8 0zM8 6H5a3 3 0 0 0 3 4M16 6h3a3 3 0 0 1-3 4M12 13v4M8.5 20h7M10 17h4"/>',
'brief':'<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5h6v2M3 12h18"/>',
'calc':'<rect x="5" y="2.5" width="14" height="19" rx="2"/><path d="M8 6.5h8M8 11h.01M12 11h.01M16 11h.01M8 14.5h.01M12 14.5h.01M16 14.5h.01M8 18h.01M12 18h4"/>',
'bank':'<path d="M3 9.5L12 4l9 5.5M5 10v8M9.5 10v8M14.5 10v8M19 10v8M3 20h18"/>',
'chart':'<path d="M3 17l5.5-5.5 4 4L21 7M15 7h6v6"/>',
'pie':'<path d="M12 3v9h9a9 9 0 1 1-9-9z"/><path d="M15 3.5A9 9 0 0 1 20.5 9H15z"/>',
'book':'<path d="M4 4.5h6a2 2 0 0 1 2 2V20a2 2 0 0 0-2-2H4zM20 4.5h-6a2 2 0 0 0-2 2V20a2 2 0 0 1 2-2h6z"/>',
'shield':'<path d="M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
'search':'<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
'coin':'<circle cx="12" cy="12" r="9"/><path d="M14.5 9.5c-.5-1-1.5-1.5-2.5-1.5-1.5 0-2.5.8-2.5 2s1 1.7 2.5 2 2.5.8 2.5 2-1 2-2.5 2c-1 0-2-.5-2.5-1.5M12 6.5v1.5M12 16v1.5"/>',
'arrow':'<path d="M5 12h14M13 6l6 6-6 6"/>',
'plane':'<path d="M10.5 13.5L3 11l1.5-1.5 7.5 1 4-4.5a2 2 0 0 1 3 3l-4.5 4 1 7.5L14 22l-2.5-7.5-3 3V20l-1.5 1.5-1-3.5-3.5-1L4 15.5h2.5z"/>',
'star':'<path d="'+STAR+'"/>',
'globe':'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
}
def tile(P,href,icon,t,sub,soon=False):
    tag='div' if soon else 'a'; h='' if soon else f' href="{P}{href}"'
    badge='<span class="hp-soon">Bald</span>' if soon else ''
    dis=' aria-disabled="true"' if soon else ''
    return f'<{tag} class="hp-tile"{h}{dis}><span class="hp-ic">{ic(I[icon])}</span><span><b>{t}{badge}</b><small>{sub}</small></span></{tag}>'
def card(P,i,c):
    href=P+c['url'].replace('https://finvallo.com/','')
    fee='kostenlos' if not c['fee'] else (f"{c['fee']:.2f} €".replace('.',',')+' / Jahr')
    fx=(c.get('fxText') or '–').split(' (')[0].replace(' plus Kursaufschlag',' + Aufschlag')
    feats=''.join(f'<li>{E(p)}</li>' for p in c['pros'][:3])
    return f'''<article class="hp-card">
<div class="hp-card-top"><span class="rank r{i}" aria-label="Platz {i}">{i}</span><span class="hp-typ">{E({'Kreditkarte':'Kreditkarte','Charge':'Charge-Karte','Debit':'Debitkarte','Prepaid':'Prepaid-Karte'}.get(c['typ'],c['typ']))}</span></div>
<a class="hp-face-link" href="{href}" tabindex="-1" aria-hidden="true"><div class="face k-{c['klasse']}"><span class="pn">{E(c['anbieter'])}</span><span class="chipc"></span><span class="nw">{E((c.get('netz') or '').upper())}</span></div></a>
<div><small class="hp-by">{E(c['anbieter'])}</small><h3><a href="{href}">{E(c['titel'])}</a></h3>
<div class="stars">{stars(c['stars'],i)}<b>{de(c['stars'])}</b><span class="nt">{E(c['note'])}</span></div></div>
<dl class="hp-kv"><div><dt>Jahresgebühr</dt><dd>{fee}</dd></div><div><dt>Fremdwährung</dt><dd>{E(fx)}</dd></div></dl>
<ul class="hp-feat">{feats}</ul>
<a class="btn primary block" href="{href}">Details ansehen</a>
</article>'''
def load(land):
    p=R+f'{land.lower()}/daten/kreditkarten.json'
    if not os.path.exists(p): return None
    d=json.load(open(p)); return d if d.get('karten') else None
def top3(d,names=None):
    ks=[c for c in d['karten'] if c.get('stars') is not None and c.get('rank')]
    if names:
        K={c['titel']:c for c in ks}; return [K[n] for n in names]
    return sorted(ks,key=lambda c:(-c['stars'],c.get('rank') or 999))[:3]
def mark(hdr): return re.search(r'<svg class="mark".*?</svg>',hdr).group(0)
def herolands(P,at,dd):
    def one(code,href,name,sub): return f'<a class="hp-hl" href="{P}{href}" hreflang="de-{code}">{FLAG[code].replace(chr(34)+"flag"+chr(34),chr(34)+"flag big"+chr(34))}<span><b>{name}</b><small>{sub}</small></span>{ic(I["arrow"])}</a>'
    return one('AT','at/','Österreich',f'{len(at["karten"])} Karten im Vergleich')+one('DE','de/','Deutschland',f'{len(dd["karten"])} Karten im Vergleich' if dd else 'Ratgeber · Vergleich in Arbeit')
def picker(P,at,dd):
    def one(code,href,name,sub):
        return f'<a class="hp-land" href="{P}{href}" hreflang="de-{code}">{FLAG[code].replace("class=\"flag\"","class=\"flag big\"")}<span><b>{name}</b><small>{sub}</small></span><span class="hp-land-go">{ic(I["arrow"])}</span></a>'
    ats=f'{len(at["karten"])} Karten im Vergleich'
    des=f'{len(dd["karten"])} Karten im Vergleich' if dd else 'Ratgeber · Kartenvergleich in Arbeit'
    return f'''<section class="hp-picker"><div class="hp-w"><h2>Für welches Land suchst du?</h2><p>Banken, Preise und Bedingungen unterscheiden sich. Wähle dein Land, dann siehst du nur Angebote, die du dort auch bekommst.</p>
<div class="hp-lands">{one("AT","at/","Österreich",ats)}{one("DE","de/","Deutschland",des)}</div></div></section>'''
def footer(P,hdr,year,stand,land='at'):
    o='de' if land=='at' else 'at'; N={'at':'Österreich','de':'Deutschland'}
    # Ratgeber-Spalte: die drei meistverlinkten Artikel (Zählung interner Links, Stand Oktober 2026)
    return f'''<footer class="hp-foot"><div class="hp-w">
<div class="hp-foot-grid">
<div class="hp-foot-brand"><a class="brand" href="{P or './'}">{mark(hdr)}<b>fin<span>vallo</span></b></a><p>Unabhängiger Finanzvergleich für Österreich und Deutschland.</p><div class="hp-foot-lands"><a href="{P}at/" hreflang="de-AT">{FLAG['AT']} Österreich</a><a href="{P}de/" hreflang="de-DE">{FLAG['DE']} Deutschland</a></div></div>
<div><h4>Vergleiche</h4><a href="{P}{land}/kreditkarten/">Kreditkarten {N[land]}</a><a href="{P}{o}/kreditkarten/" hreflang="de-{o.upper()}">Kreditkarten {N[o]}</a><a href="{P}{land}/kreditkarten/bestenlisten/">Bestenlisten</a><a href="{P}{land}/kreditkarten/business/">Business-Kreditkarten</a><a href="{P}{land}/kreditkarten/rechner/">Kartenrechner</a></div>
<div><h4>Ratgeber</h4><a href="{P}at/ratgeber/" hreflang="de-AT">Ratgeber Österreich</a><a href="{P}de/ratgeber/" hreflang="de-DE">Ratgeber Deutschland</a><a href="{P}{land}/ratgeber/teilzahlung/">Teilzahlung</a><a href="{P}{land}/ratgeber/reiseversicherung/">Reiseversicherung</a><a href="{P}{land}/ratgeber/kartentypen/">Kartentypen</a></div>
<div><h4>Unternehmen</h4><a href="{P}ueber-uns/">Über Finvallo</a><a href="{P}{land}/kreditkarten/methodik/">So bewerten wir</a><a href="{P}so-verdienen-wir-geld/">So verdienen wir Geld</a></div>
<div><h4>Rechtliches</h4><a href="{P}impressum/">Impressum</a><a href="{P}datenschutz/">Datenschutz</a><a href="{P}llms.txt">Für KI-Assistenten</a></div>
</div>
<div class="hp-foot-legal"><span>© {year} Finvallo · Stand {stand}</span><span>Keine Finanzberatung. Konditionen vor Abschluss beim Anbieter prüfen. Mit * markierte Links sind Affiliate-Links. Bewertung unabhängig von Provisionen, keine bezahlten Platzierungen.</span></div>
</div></footer>'''
def faqblock(faq):
    h=''.join(f'<details class="hp-faq"><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q,a in faq)
    ld=json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq]},ensure_ascii=False)
    return f'<section class="hp-sec"><div class="hp-w hp-narrow"><h2 class="hp-h">Häufig gestellte Fragen</h2><div class="hp-faqs">{h}</div></div></section>', ld
def guides(P,items):
    return ''.join(f'<a class="hp-post" href="{P}{h}"><span class="ct">{c}</span><b>{E(t)}</b><span class="hp-muted">{E(s)}</span><small>Weiterlesen →</small></a>' for h,c,t,s in items)
def hero(eyebrow,h1,p,ctas,art):
    return f'''<section class="hp-hero"><div class="hp-w hp-hero-in"><div class="hp-hero-txt">
<span class="hp-eyebrow">{eyebrow}</span><h1>{h1}</h1><p>{p}</p><div class="hp-cta">{ctas}</div></div>{art}</div></section>'''
def art(c0,land):
    b=f'<div class="hp-badge">{stars(c0["stars"],0)}<span><b>{de(c0["stars"])} / 5</b> · Bestbewertet</span></div>' if c0 else ''
    return f'<div class="hp-hero-art" aria-hidden="true"><div class="face k-Premium a1"><span class="pn">finvallo</span><span class="chipc"></span><span class="nw">VISA</span></div><div class="face k-Gold a2"><span class="pn">Gold</span><span class="chipc"></span><span class="nw">MASTERCARD</span></div><div class="face k-Debit a3"><span class="pn">Debit</span><span class="chipc"></span><span class="nw">VISA</span></div>{b}{f'<div class="hp-art-flag">{FLAG[land]}</div>' if land else ''}</div>'
def stats(items): return '<section class="hp-stats"><div class="hp-w">'+''.join(f'<div><b>{a}</b><span>{b}</span></div>' for a,b in items)+'</div></section>'
def sec(h,sub,inner,alt=False,id_=''):
    i=f' id="{id_}"' if id_ else ''
    return f'<section class="hp-sec{" hp-alt" if alt else ""}"{i}><div class="hp-w"><h2 class="hp-h">{h}</h2><p class="hp-sub">{sub}</p>{inner}</div></section>'
def topcards(P,d,land,names=None,base='at/kreditkarten/'):
    t=top3(d,names); n=len(d['karten']); stand='.'.join(reversed(d['stand'].split('-')))
    best=[('gratis','Ohne Jahresgebühr'),('reisen','Für Reisen'),('ausland','Im Ausland zahlen'),('punkte','Meilen & Punkte'),('cashback','Cashback'),('lounge','Lounge-Zugang'),('premium','Premium'),('studium','Für Studierende'),('debit','Debitkarten')]
    chips=''
    if os.path.isdir(R+base+'bestenlisten'):
        chips='<div class="hp-chips"><span>Beste Karte nach Kategorie:</span><div class="chips">'+''.join(f'<a class="chip" href="{P}{base}bestenlisten/{s}/">{x}</a>' for s,x in best if os.path.isdir(R+base+'bestenlisten/'+s))+'</div></div>'
    inner=f'<div class="hp-cards">{"".join(card(P,i+1,c) for i,c in enumerate(t))}</div>{chips}<div class="hp-more"><a class="btn" href="{P}{base}">Alle {n} Karten anzeigen →</a></div>'
    return t, sec(f'Die besten Kreditkarten in {land}',f'Die drei bestbewerteten Karten laut Finvallo-Bewertung. Stand: {stand}.',inner,True,'bestbewertet')
def trust(P,land='at'):
    return sec('So bewerten wir','Transparenz statt Werbeplätze: Unsere Regeln sind öffentlich.',f'''<div class="hp-trust">
<a href="{P}{land}/kreditkarten/methodik/"><span class="hp-ic">{ic(I['chart'])}</span><b>Feste, offene Regeln</b><span class="hp-muted">Sieben gewichtete Kriterien, für jede Karte gleich angewendet.</span><small>Zur Methodik →</small></a>
<a href="{P}{land}/kreditkarten/methodik/"><span class="hp-ic">{ic(I['search'])}</span><b>Geprüft beim Anbieter</b><span class="hp-muted">Konditionen aus Preisblatt und Anbieterseite, mit Quellenangabe.</span><small>So bewerten wir →</small></a>
<a href="{P}so-verdienen-wir-geld/"><span class="hp-ic">{ic(I['shield'])}</span><b>Provision ohne Einfluss</b><span class="hp-muted">Affiliate-Links sind gekennzeichnet und ändern keine Bewertung.</span><small>So verdienen wir Geld →</small></a></div>''')
SHIELD=ic(I['shield'])+' Unabhängig bewertet'
AT_GUIDES=[('at/ratgeber/kostenlose-kreditkarte/','Vergleich','Kostenlose Kreditkarte in Österreich','Welche Karten wirklich nichts kosten und wo die Haken liegen.'),
('at/ratgeber/fremdwaehrung/','Ausland','Gebühren im Ausland verstehen','Bearbeitungsentgelt, Kursaufschlag und die Falle „in Euro zahlen“.'),
('at/ratgeber/reiseversicherung/','Versicherung','Reiseversicherung über die Kreditkarte','Wann sie gilt, wer mitversichert ist und worauf du bei Storno achten musst.'),
('at/ratgeber/ohne-bonitaetspruefung/','Bonität','Kreditkarte ohne KSV-Abfrage','Was seriös möglich ist und welche Alternativen es gibt.'),
('at/ratgeber/mietwagen-kaution/','Reisen','Kreditkarte für Mietwagen und Kaution','Warum Vermieter eine echte Kreditkarte wollen.'),
('at/ratgeber/punkte-sammeln-at/','Punkte','Lohnt sich Punktesammeln in Österreich?','Amex, Miles & More und Hilton: was Punkte wirklich wert sind.')]
DE_GUIDES=[('de/ratgeber/kostenlose-kreditkarte/','Vergleich','Kostenlose Kreditkarte in Deutschland','Welche Karten wirklich nichts kosten und wo die Haken liegen.'),
('de/ratgeber/ohne-bonitaetspruefung/','Schufa','Kreditkarte ohne Schufa','Was seriös möglich ist und welche Alternativen es gibt.'),
('de/ratgeber/fremdwaehrung/','Ausland','Gebühren im Ausland verstehen','Auslandseinsatzentgelt und die Falle „in Euro zahlen“.'),
('de/ratgeber/mietwagen-kaution/','Reisen','Kreditkarte für Mietwagen und Kaution','Warum Vermieter eine echte Kreditkarte wollen.'),
('de/ratgeber/punkte-sammeln-de/','Punkte','Lohnt sich Punktesammeln in Deutschland?','Amex-Boni, Miles & More und Payback: was sich wirklich lohnt.'),
('de/ratgeber/kreditkarte-beantragen/','Antrag','Kreditkarte beantragen','Ablauf, Unterlagen und warum Anträge abgelehnt werden.')]
AT_TOP=None   # Top 3 aus der Rangliste

def page(rel, build):
    f=R+rel+'index.html'; src=open(f).read()
    head=src[:src.index('<body')]
    x='<link rel="alternate" hreflang="x-default" href="https://finvallo.com/">'
    while head.count(x)>1: head=head.replace(x+x,x)
    head=re.sub(r'<script type="application/ld\+json">\{"@context": "https://schema.org", "@type": "FAQPage".*?</script>\n','',head,flags=re.S)
    hdr=re.search(r'<a class="skip".*?</header>',src,re.S).group(0)
    P='../'*rel.count('/')
    body,ld=build(P,hdr)
    if ld: head=head.replace('</head>',f'<script type="application/ld+json">{ld}</script>\n</head>')
    open(f,'w').write(head+'<body class="hp">\n'+hdr+'\n<main id="app">\n'+body+'\n</main>\n'+footer(P,hdr,AT['stand'][:4],'.'.join(reversed(AT['stand'].split('-'))),'de' if rel.startswith('de/') else 'at')+'\n</body>\n</html>\n')

AT=load('AT'); DD=load('DE')
nA=len(AT['karten']); nG=len(json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'daten','at','girokonten.json')))['konten']); anbA=len({c['anbieter'] for c in AT['karten']})

def b_root(P,hdr):
    t,tc=topcards(P,AT,'Österreich',AT_TOP)
    td,tcd=topcards(P,DD,'Deutschland',None,'de/kreditkarten/') if DD else (None,'')
    tcd=tcd.replace('id="bestbewertet"','id="bestbewertet-de"')
    tiles=''.join([tile(P,'at/kreditkarten/','card','Kreditkarten Österreich',f'{nA} Karten im Vergleich'),
      tile(P,'de/kreditkarten/','card','Kreditkarten Deutschland',f'{len(DD["karten"])} Karten im Vergleich' if DD else 'Ratgeber · Vergleich in Arbeit'),
      tile(P,'at/girokonto/','bank','Girokonten Österreich',f'{nG} Konten im Vergleich'),
      tile(P,'at/kreditkarten/bestenlisten/','trophy','Bestenlisten','Die besten Karten nach Kategorie'),
      tile(P,'at/kreditkarten/business/','brief','Business-Kreditkarten','Firmenkarten für Selbstständige'),
      tile(P,'at/kreditkarten/rechner/','calc','Kartenrechner','Was kostet dich deine Karte wirklich?'),
      tile(P,'at/ratgeber/','book','Ratgeber','Gebühren, Punkte, Versicherung erklärt'),
      tile(P,'at/rechner/','calc','Finanzrechner Österreich','Zinseszins, Kredit, KESt und mehr'),
      tile(P,'de/rechner/','calc','Finanzrechner Deutschland','Zinseszins, Kredit, Abgeltungsteuer und mehr')])
    fq,ld=faqblock(ROOT_FAQ(t,td))
    return (hero(SHIELD,'Dein unabhängiger Finanzvergleich für Österreich und Deutschland.',
        'Banken, Preise und Bedingungen unterscheiden sich. Wähle dein Land, dann siehst du nur Angebote, die du dort auch bekommst.',
        herolands(P,AT,DD),art(t[0],None))
      + stats([(nA,'Karten in Österreich'),(len(DD['karten']) if DD else '-','Karten in Deutschland'),(len({c['anbieter'].split()[0].lower().strip(',') for c in AT['karten']+(DD['karten'] if DD else [])}),'Banken und Anbieter'),(7,'offene Bewertungskriterien')])
      + sec('Unsere Vergleiche im Überblick','Finde das passende Finanzprodukt.',f'<div class="hp-tiles">{tiles}</div><p class="hp-sub" style="margin-top:16px">Weitere Vergleiche (Girokonto Deutschland, Tagesgeld, Depot) sind in Arbeit.</p>')
      + tc + tcd + trust(P)
      + sec('Ratgeber','Kreditkarten einfach erklärt.',f'<div class="hp-posts">{guides(P,AT_GUIDES[:3]+DE_GUIDES[:3])}</div><div class="hp-more"><a class="btn" href="{P}at/ratgeber/">Ratgeber Österreich →</a> <a class="btn ghost" href="{P}de/ratgeber/">Ratgeber Deutschland →</a></div>',True)
      + fq), ld
def ROOT_FAQ(t,td=None): return [
 ('Was kostet Finvallo?','Nichts. Du kannst alle Vergleiche ohne Registrierung nutzen. Wir finanzieren uns über Affiliate-Links, die mit * markiert sind. Die Provision hat keinen Einfluss auf Sterne oder Reihenfolge.'),
 ('Warum muss ich ein Land wählen?','Banken, Preise und Bedingungen sind in Österreich und Deutschland verschieden, und viele Karten gibt es nur in einem der beiden Länder. Deshalb vergleichen wir jedes Land getrennt und übernehmen keine Werte von einem Land ins andere.'),
 ('Wie bewertet Finvallo Kreditkarten?','Jede Karte wird nach sieben fest gewichteten Kriterien bewertet: Jahresgebühr (25 %), Reiseversicherung (20 %), Zahlen im Ausland (15 %) sowie Kartenart, Alltag, Bargeld und Extras (je 10 %). Die Regeln sind öffentlich.'),
 ('Welche Kreditkarte ist in Österreich die beste?',f'Laut Finvallo-Bewertung ist die {t[0]["titel"]} mit {de(t[0]["stars"])} von 5 Sternen die bestbewertete Kreditkarte, vor der {t[1]["titel"]} und der {t[2]["titel"]}. Welche Karte zu dir passt, hängt davon ab, wie du sie nutzt.'),
]+([(f'Welche Kreditkarte ist in Deutschland die beste?',f'In Deutschland liegt laut Finvallo-Bewertung die {td[0]["titel"]} mit {de(td[0]["stars"])} von 5 Sternen vorn, vor der {td[1]["titel"]} und der {td[2]["titel"]}.')] if td else [])+[
 ('Wie aktuell sind die Konditionen?','Wir prüfen die Konditionen regelmäßig direkt beim Anbieter und im Preisblatt. Jede Seite zeigt den Stand der Daten.'),
 ('Ist Finvallo eine Finanzberatung?','Nein. Finvallo vergleicht und erklärt, ersetzt aber keine persönliche Beratung. Prüfe die Konditionen vor dem Abschluss beim Anbieter.')]
def b_at(P,hdr):
    t,tc=topcards(P,AT,'Österreich',AT_TOP,'at/kreditkarten/')
    tiles=''.join([tile(P,'at/kreditkarten/','card','Kreditkarten',f'{nA} Karten im Vergleich'),
      tile(P,'at/girokonto/','bank','Girokonten',f'{nG} Konten im Vergleich'),
      tile(P,'at/kreditkarten/bestenlisten/','trophy','Bestenlisten','Die besten Karten nach Kategorie'),
      tile(P,'at/kreditkarten/business/','brief','Business-Kreditkarten','Firmenkarten für Selbstständige'),
      tile(P,'at/kreditkarten/anbieter/','bank','Anbieter',f'{anbA} Banken und Kartenanbieter'),
      tile(P,'at/ratgeber/','book','Ratgeber','Gebühren, Punkte, Versicherung erklärt'),
      tile(P,'at/rechner/','calc','Finanzrechner','Zinseszins, Kredit, KESt und mehr')])
    fq,ld=faqblock([q for q in ROOT_FAQ(t) if not q[0].startswith('Warum muss')])
    return (hero(f'{FLAG["AT"]} Österreich · unabhängig bewertet','Kreditkarten in Österreich unabhängig vergleichen.',
        f'{nA} Kredit-, Debit- und Prepaid-Karten von {anbA} Anbietern, mit Gebühren, Versicherung und Bewertung.',
        f'<a class="btn primary" href="{P}at/kreditkarten/">Alle Kreditkarten {ic(I["arrow"])}</a><a class="btn ghost" href="{P}at/kreditkarten/bestenlisten/">Bestenlisten</a><a class="btn ghost" href="#bestbewertet">Bestbewertete Karten ansehen</a>',art(t[0],'AT'))
      + stats([(nA,'Kreditkarten verglichen'),(anbA,'Banken und Anbieter'),(7,'offene Bewertungskriterien'),(9,'Bestenlisten nach Kategorie')])
      + tc
      + sec('Alles für Österreich','Vergleiche, Werkzeuge und Ratgeber.',f'<div class="hp-tiles">{tiles}</div><p class="hp-sub" style="margin-top:16px">Weitere Vergleiche (Tagesgeld, Depot) sind in Arbeit.</p>')
      + trust(P,'at')
      + sec('Ratgeber für Österreich','Kreditkarten einfach erklärt.',f'<div class="hp-posts">{guides(P,AT_GUIDES)}</div><div class="hp-more"><a class="btn" href="{P}at/ratgeber/">Alle Ratgeber →</a></div>',True)
      + switch(P,'DE') + fq), ld
def switch(P,other):
    name={'AT':'Österreich','DE':'Deutschland'}[other]
    return f'<section class="hp-switch"><div class="hp-w"><span>{FLAG[other]} Du suchst Angebote für {name}?</span><a class="btn" href="{P}{other.lower()}/" hreflang="de-{other}">Zu {name} →</a></div></section>'
def b_de(P,hdr):
    if DD:
        nD=len(DD['karten']); anbD=len({c['anbieter'] for c in DD['karten']})
        t,tc=topcards(P,DD,'Deutschland',None,'de/kreditkarten/')
    else:
        nD=None; t=None; tc=''
    tiles=''.join([tile(P,'de/kreditkarten/','card','Kreditkarten',f'{nD} Karten im Vergleich') if DD else tile(P,'','card','Kreditkarten-Vergleich','Wir sammeln und prüfen gerade alle Karten',True),
      tile(P,'de/ratgeber/punkte-sammeln-de/','star','Punkte & Meilen','Amex, Miles & More, Payback'),
      tile(P,'de/ratgeber/fremdwaehrung/','globe','Zahlen im Ausland','Gebühren und Kursaufschläge'),
      tile(P,'de/ratgeber/reiseversicherung/','plane','Reiseversicherung','Was die Karte wirklich abdeckt'),
      tile(P,'de/ratgeber/business/','brief','Firmenkreditkarten','Für Selbstständige und Firmen'),
      tile(P,'de/ratgeber/','book','Alle Ratgeber','Kreditkarten einfach erklärt'),
      tile(P,'de/rechner/','calc','Finanzrechner','Zinseszins, Kredit, Abgeltungsteuer und mehr')])
    faq=[('Gibt es den Kreditkartenvergleich auch für Deutschland?', f'Ja. Wir vergleichen {nD} Karten für Deutschland nach derselben Methode wie in Österreich.' if DD else 'Er ist in Arbeit. Wir sammeln und prüfen gerade die Konditionen aller Kreditkarten in Deutschland, direkt bei den Anbietern und in den Preisverzeichnissen. Danach erscheinen sie hier mit derselben Bewertung wie in Österreich.'),
     ('Warum übernehmt ihr nicht einfach die Werte aus Österreich?','Banken, Preise und Bedingungen sind in Deutschland anders, und viele Karten gibt es nur in einem der beiden Länder. Wir übernehmen deshalb keine Werte von einem Land ins andere.'),
     ('Was kostet Finvallo?','Nichts. Du kannst alles ohne Registrierung nutzen. Wir finanzieren uns über Affiliate-Links, die mit * markiert sind. Die Provision hat keinen Einfluss auf Sterne oder Reihenfolge.'),
     ('Wie bewertet Finvallo Kreditkarten?','Jede Karte wird nach sieben fest gewichteten Kriterien bewertet: Jahresgebühr (25 %), Reiseversicherung (20 %), Zahlen im Ausland (15 %) sowie Kartenart, Alltag, Bargeld und Extras (je 10 %). Die Regeln sind öffentlich.'),
     ('Ist Finvallo eine Finanzberatung?','Nein. Finvallo vergleicht und erklärt, ersetzt aber keine persönliche Beratung. Prüfe die Konditionen vor dem Abschluss beim Anbieter.')]
    fq,ld=faqblock(faq)
    if DD:
        st=stats([(nD,'Kreditkarten verglichen'),(anbD,'Banken und Anbieter'),(7,'offene Bewertungskriterien'),(9,'Bestenlisten nach Kategorie')])
        cta=f'<a class="btn primary" href="{P}de/kreditkarten/">Alle Kreditkarten {ic(I["arrow"])}</a><a class="btn ghost" href="{P}de/kreditkarten/bestenlisten/">Bestenlisten</a><a class="btn ghost" href="#bestbewertet">Bestbewertete Karten ansehen</a>'
        p=f'{nD} Karten von {anbD} Anbietern, mit Gebühren, Versicherung und Bewertung.'
    else:
        st=stats([(len(DE_GUIDES)+1,'Ratgeber für Deutschland'),(7,'offene Bewertungskriterien'),(0,'bezahlte Platzierungen'),('100 %','kostenlos')])
        cta=f'<a class="btn primary" href="{P}de/ratgeber/">Zu den Ratgebern {ic(I["arrow"])}</a><a class="btn ghost" href="{P}at/kreditkarten/">{FLAG["AT"]} Österreich-Vergleich</a>'
        p='Unabhängige Ratgeber zu Punkten, Meilen, Auslandsgebühren und Reiseversicherung. Der Kreditkartenvergleich für Deutschland ist in Arbeit.'
    return (hero(f'{FLAG["DE"]} Deutschland · unabhängig bewertet','Kreditkarten in Deutschland unabhängig vergleichen.',p,cta,art(t[0] if t else None,'DE'))
      + st + tc
      + sec('Alles für Deutschland','Vergleich und Ratgeber.',f'<div class="hp-tiles">{tiles}</div><p class="hp-sub" style="margin-top:16px">Weitere Vergleiche (Girokonto, Tagesgeld, Depot) sind in Arbeit.</p>', not DD)
      + ('' if DD else '')
      + trust(P,'de')
      + sec('Ratgeber für Deutschland','Kreditkarten einfach erklärt.',f'<div class="hp-posts">{guides(P,DE_GUIDES)}</div><div class="hp-more"><a class="btn" href="{P}de/ratgeber/">Alle Ratgeber →</a></div>',True)
      + switch(P,'AT') + fq), ld

page('',b_root); page('at/',b_at); page('de/',b_de)
print('ok')
