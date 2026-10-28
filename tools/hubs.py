# Übersichtsseiten je Land, die die drei Vergleiche bündeln: /<land>/bestenlisten/ (alle Bestenlisten) und /<land>/methodik/ (alle Bewertungsregeln).
# Läuft nach festgeld.py und vor header.py (Menüpunkt „Bestenlisten“ und Fußzeile „So bewerten wir“ zeigen hierher).
import html,json,os,re,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import karten as K
E=K.E; R=K.R; SP=K.SP; dmy=K.dmy
N={'at':'Österreich','de':'Deutschland'}

def pages(land,base):
    """[(rel, Titel aus <h1>, Kurztext aus description)] für alle index.html unter base, ohne die Übersicht selbst"""
    out=[]
    for d in sorted(os.listdir(R+base)) if os.path.isdir(R+base) else []:
        f=R+base+d+'/index.html'
        if not os.path.isfile(f): continue
        s=open(f,encoding='utf-8').read()
        h=re.search(r'<h1[^>]*>(.*?)</h1>',s,re.S); m=re.search(r'<meta name="description" content="([^"]*)"',s)
        if not h: continue
        out.append((base+d+'/',html.unescape(re.sub(r'<[^>]+>','',h.group(1)).strip()),html.unescape(m.group(1)) if m else ''))
    return out
def tile(P,rel,t,sub): return f'<a class="catcard" href="{P}{rel}"><b>{E(t)}</b><span style="color:var(--muted)">{E(sub)}</span><small>Liste ansehen →</small></a>'

def bestenlisten(land):
    rel=f'{land}/bestenlisten/'; P='../../'
    secs=[('Kreditkarten',f'{land}/kreditkarten/bestenlisten/'),('Girokonten',f'{land}/girokonto/bestenlisten/'),('Festgeld',f'{land}/festgeld/bestenlisten/')]
    blocks=''; n=0; items=[]
    for name,base in secs:
        if not os.path.isfile(R+base+'index.html'): continue
        xs=[x for x in pages(land,base) if not x[0].endswith('/lohnt-sich/')]
        if not xs: continue
        n+=len(xs); items+=xs
        blocks+=f'<h2>{name}</h2><p class="note"><a class="lnk" href="{P}{base}">Alle {name}-Bestenlisten mit Platz 1 bis 3 →</a></p><div class="catgrid">{"".join(tile(P,r,h,d) for r,h,d in xs)}</div>'
    t=f'Bestenlisten {N[land]} 2026: Kreditkarten, Girokonten, Festgeld | Finvallo'
    if len(t)>62: t=f'Bestenlisten {N[land]}: Karten, Konten, Festgeld | Finvallo'
    d=f'{n} Bestenlisten für {N[land]}: die besten Kreditkarten, Girokonten und Festgeld-Angebote nach Kategorie, sortiert nach offenen Regeln statt nach Provision.'
    ld=K.graph(rel,t,d,[(N[land],f'{land}/'),('Bestenlisten',rel)],[{"@type":"ItemList","name":f"Bestenlisten {N[land]}","numberOfItems":len(items),"itemListElement":[{"@type":"ListItem","position":i+1,"name":h,"url":f"https://finvallo.com/{r}"} for i,(r,h,_) in enumerate(items)]}])
    K.write(rel,K.head(t,d,rel,P,ld)+f'''{K.HDR(P,rel,("de" if land=="at" else "at")+"/bestenlisten/")}
<div class="wrap"><main id="app">
<h1>Bestenlisten für {N[land]}</h1>
<p class="lede">{n} Listen, in denen jeweils nur Produkte stehen, die eine klare Bedingung erfüllen: etwa „ohne Jahresgebühr“, „gratis mit Gehalt“ oder „vorzeitig kündbar“. Die Reihenfolge folgt unseren offenen Regeln, Provisionen spielen keine Rolle.</p>
{blocks}
<h2>Wie entstehen die Listen?</h2><div class="prose"><p>Kreditkarten und Girokonten bekommen Sterne nach festen Kriterien; in den Bestenlisten sind die Kriterien je nach Kategorie anders gewichtet. Festgeld sortieren wir nach Zins für Betrag und Laufzeit, weil dort die Einlagensicherung für alle gleich ist. Die Regeln stehen auf der <a href="../methodik/">Methodik-Seite</a>.</p></div>
</main>
{K.footer(P)}''')
    return n

def methodik(land):
    rel=f'{land}/methodik/'; P='../../'
    xs=[(f'{land}/kreditkarten/methodik/','Kreditkarten','7 Kriterien mit festen Gewichten: Jahresgebühr, Reiseversicherung, Zahlen im Ausland, Kartenart, Alltag, Bargeld, Extras. Fehlende Angaben zählen mit 2,5 Sternen.'),
        (f'{land}/girokonto/methodik/','Girokonten','6 Kriterien: Kosten im typischen Fall, Bedingungen für den günstigen Preis, Bargeld, Karten, Zinsen, Alltag und Service. Mit deinen eigenen Zahlen rechnest du im Vergleich.'),
        (f'{land}/festgeld/methodik/','Festgeld','Keine Sterne, sondern Sortierung nach Zins für Betrag und Laufzeit. Einlagensicherung, Länderrating, Steuer und Kündbarkeit zeigen wir offen und filterbar.')]
    xs=[x for x in xs if os.path.isfile(R+x[0]+'index.html')]
    t=f'So bewerten wir: Methodik für {N[land]} | Finvallo'
    d=f'Die Regeln hinter allen Finvallo-Vergleichen für {N[land]}: wie Kreditkarten und Girokonten ihre Sterne bekommen, wie Festgeld sortiert wird, woher die Daten stammen und was Provisionen nicht beeinflussen.'
    ld=K.graph(rel,t,d,[(N[land],f'{land}/'),('So bewerten wir',rel)])
    K.write(rel,K.head(t,d,rel,P,ld)+f'''{K.HDR(P,rel,("de" if land=="at" else "at")+"/methodik/")}
<div class="wrap"><main id="app">
<h1>So bewerten wir</h1>
<p class="lede">Jeder Vergleich auf Finvallo folgt festen, öffentlichen Regeln. Jede Zahl stammt aus dem Preisblatt, der Entgeltinformation oder der Konditionsseite des Anbieters und trägt ein Prüfdatum. Provisionen haben keinen Einfluss auf Sterne, Zinsen oder Reihenfolge.</p>
<div class="catgrid">{"".join(f'<a class="catcard" href="{P}{r}"><span class="ct">{h}</span><b>So bewerten wir {h}</b><span style="color:var(--muted)">{E(x)}</span><small>Alle Regeln →</small></a>' for r,h,x in xs)}</div>
<h2>Was für alle Vergleiche gilt</h2><div class="prose">
<p><b>Quelle zuerst.</b> Wir übernehmen keine Werte aus anderen Vergleichsportalen. Steht eine Angabe nicht in den Unterlagen des Anbieters, schreiben wir „keine Angabe“, und das Kriterium zählt neutral, damit fehlende Daten keinen Vorteil bringen.</p>
<p><b>Gleiche Regeln für alle.</b> Jedes Produkt wird mit denselben Regeln bewertet, egal ob es ein Partnerprogramm gibt oder nicht. Die Bewertung steht fest, bevor wir prüfen, ob ein Anbieter Provision zahlt. <a class="lnk" href="../../so-verdienen-wir-geld/">So verdient Finvallo Geld →</a></p>
<p><b>Ein Land, eine Liste.</b> Konditionen aus Deutschland gelten nicht für Österreich und umgekehrt. Deshalb gibt es jeden Vergleich zweimal, mit eigenen Daten.</p>
<p><b>Prüfdatum auf jeder Seite.</b> Banken ändern Preise ohne Ankündigung. Jede Produktseite zeigt, wann wir die Konditionen zuletzt geprüft haben. Fehler melden: <a class="lnk" href="mailto:korrektur@finvallo.com">korrektur@finvallo.com</a>.</p></div>
<p class="note"><a class="lnk" href="../bestenlisten/">Alle Bestenlisten →</a> · <a class="lnk" href="../../ueber-uns/">Über Finvallo →</a></p>
</main>
{K.footer(P)}''')

def main():
    for land in ('at','de'):
        K.use(land)
        if 'stand' not in K.L:   # Stand aus den Kartendaten, wie karten.py ihn setzt
            fp=os.path.join(SP,'daten',land,'festgeld.json'); gp=os.path.join(SP,'daten',land,'girokonten.json')
            K.L['stand']=max([json.load(open(x))['stand'] for x in (fp,gp) if os.path.exists(x)] or [K.TODAY])
        n=bestenlisten(land); methodik(land)
        print(f'Hub {land}: {n} Bestenlisten')
if __name__=='__main__': main()
