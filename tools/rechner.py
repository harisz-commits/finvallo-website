# Finanzrechner für AT und DE (/at/rechner/, /de/rechner/), Logik in public/assets/calc.js
import json,os,re,html,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','public')+'/'
STAND='2026-10-12'; STAND_DE='12.10.2026'
E=lambda s: html.escape(str(s))
LN={'at':('Österreich','de-AT','de_AT'),'de':('Deutschland','de-DE','de_DE')}
def inp(id,label,val,suffix='',help=''):
    return f'<label><span class="flab">{label}</span><span class="inw"><input id="{id}" name="{id}" type="text" inputmode="decimal" value="{val}" autocomplete="off">{f"<em>{suffix}</em>" if suffix else ""}</span>{f"<small class=mut>{help}</small>" if help else ""}</label>'
def chk(id,label,help=''):
    return f'<label class="chkl"><span class="flab">{label}</span><span class="chkrow"><input id="{id}" name="{id}" type="checkbox" value="1"><span>Ja, abziehen</span></span>{f"<small class=mut>{help}</small>" if help else ""}</label>'
def sel(id,label,opts):
    return f'<label><span class="flab">{label}</span><select id="{id}" name="{id}">'+''.join(f'<option value="{v}"{" selected" if s else ""}>{t}</option>' for v,t,s in opts)+'</select></label>'
DISCLAIMER='<div class="box disc"><b>Hinweis:</b> Alle Berechnungen sind Beispielrechnungen ohne Gewähr. Trotz sorgfältiger Prüfung können Fehler passieren, und Banken runden oder rechnen im Detail oft anders. Das Ergebnis ersetzt keine Beratung. Prüfe wichtige Entscheidungen mit den Unterlagen deiner Bank.</div>'
CALCS={}
def calc(slug,**kw): CALCS[slug]=kw
def define(land):
    N=LN[land][0]
    calc('zinseszins',icon='chart',t='Zinseszinsrechner & Sparrechner',mt='Zinseszinsrechner & Sparrechner | Finvallo',
      desc='Zinseszinsrechner und Sparrechner: Endkapital mit Startkapital, monatlicher Sparrate, Zins und Dynamik berechnen. Mit Jahrestabelle und Diagramm.',
      lede='Wie viel wird aus deinem Ersparten? Mit Startkapital, monatlicher Sparrate und Zinseszins.',
      form=inp('k0','Startkapital','10.000','€')+inp('pay','Monatliche Sparrate','200','€')+inp('r','Zins oder Rendite pro Jahr','5','%')+inp('y','Laufzeit','20','Jahre')+inp('dyn','Dynamik (Erhöhung der Rate pro Jahr)','0','%')+sel('when','Einzahlung',[('start','zu Monatsbeginn',True),('end','zu Monatsende',False)])
        +chk('tax','Steuer auf die Erträge abziehen' if land=='at' else 'Abgeltungsteuer abziehen','KESt 25 % oder 27,5 %, je nach Anlageart' if land=='at' else '25 % plus Soli = 26,375 %, ohne Kirchensteuer')
        +(sel('anl','Anlageart (für die Steuer)',[('bank','Sparbuch, Tagesgeld, Festgeld: 25 % jährlich',True),('wp','ETF, Aktien, Fonds, Anleihen: 27,5 % am Ende',False)]) if land=='at' else
          sel('anl','Anlageart (für die Steuer)',[('bank','Tagesgeld, Festgeld: jährlich auf die Zinsen',True),('etf','Aktien-ETF, Aktienfonds: am Ende, 30 % Teilfreistellung',False),('wp','Einzelaktien, Anleihen, sonstige Fonds: am Ende',False)])+inp('fb','Sparer-Pauschbetrag pro Jahr','1.000','€','1.000 € pro Person, 2.000 € bei Zusammenveranlagung; 0, wenn er anderswo verbraucht ist')),
      out='<div class="res"><div><small id="l1">Endkapital</small><b id="o1">–</b></div><div><small>Eingezahlt</small><b id="o2">–</b></div><div><small>Zinsen und Erträge</small><b id="o3">–</b></div><div><small id="l4">Steuer</small><b id="o4">–</b></div></div><p class="note" id="o5"></p><div id="chart" class="chart"></div><p class="note"><span class="lg a"></span> Einzahlungen <span class="lg b"></span> Zinsen</p><div class="tbl" id="tab"></div>',
      js=('''const on=!!(q('tax')&&q('tax').checked),anl=v('anl');
'''+("const tax=on?(anl==='bank'?{mode:'yearly',rate:0.25}:{mode:'end',rate:0.275}):null;" if land=='at' else
     "const fb=n('fb');const tax=on?(anl==='bank'?{mode:'yearly',rate:0.26375,allowance:fb}:{mode:'end',rate:0.26375,allowance:fb,tfs:anl==='etf'?0.3:0}):null;")+'''
const r=FinCalc.savings({start:n('k0'),pay:n('pay'),rate:n('r')/100,months:Math.round(n('y')*12),dyn:n('dyn')/100,payStart:v('when')==='start',tax:tax});
set('o1',FinCalc.eur(r.end));set('o2',FinCalc.eur(r.paid));set('o3',FinCalc.eur(r.interest));set('o4',on?FinCalc.eur(r.tax):'–');
q('l1').textContent=on?'Endkapital nach Steuer':'Endkapital';q('l4').textContent=on?('''+("anl==='bank'?'KESt (25 %, jährlich)':'KESt (27,5 %, am Ende)'" if land=='at' else "anl==='bank'?'Abgeltungsteuer (jährlich)':'Abgeltungsteuer (am Ende)'")+'''):'Steuer';
q('o5').textContent=on?(anl==='bank'?'Die Steuer wird jedes Jahr von den Zinsen abgezogen, danach verzinst sich nur der Rest. Tabelle und Diagramm zeigen die Werte nach Steuer.':'Die Steuer fällt erst am Ende auf den Gesamtgewinn an (Verkauf). Tabelle und Diagramm zeigen die Werte vor Steuer.'+('''+("' Jährlich besteuerte ausschüttungsgleiche Erträge und Ausschüttungen sind nicht enthalten.'" if land=='at' else "' Vorabpauschale und Ausschüttungen während der Laufzeit sind nicht enthalten; der Pauschbetrag wird einmal angesetzt.'")+''')):'';
FinCalc.bars(q('chart'),r.years.map(x=>({year:x.year,a:x.paid,b:x.interest})),['a','b'],['var(--card2)','var(--blue)']);
q('tab').innerHTML='<table><thead><tr><th>Jahr</th><th>Eingezahlt</th><th>Zinsen</th><th>Kapital</th></tr></thead><tbody>'+r.years.map(x=>`<tr><td>${x.year}</td><td>${FinCalc.eur(x.paid,0)}</td><td>${FinCalc.eur(x.interest,0)}</td><td><b>${FinCalc.eur(x.balance,0)}</b></td></tr>`).join('')+'</tbody></table>';'''),
      how='<p>Der Rechner simuliert jeden Monat: Die Sparrate kommt dazu, dann wird das Guthaben verzinst. Aus dem Jahreszins wird der passende Monatszins berechnet, sodass nach zwölf Monaten mit Zinseszins genau der angegebene Jahreszins herauskommt. Das nennt man konformen Zins: Bei 5 % im Jahr sind das rund 0,41 % im Monat, nicht 5 / 12 = 0,42 %. Mit Dynamik steigt die Sparrate jedes Jahr um den angegebenen Prozentsatz.</p>'+("<p>Mit dem Haken „Steuer abziehen“ rechnet der Rechner die KESt mit, und zwar je nach Anlageart unterschiedlich, weil sie zu verschiedenen Zeitpunkten anfällt: Auf Zinsen von Sparbuch, Tagesgeld und Festgeld behält die Bank 25 % bei jeder Gutschrift ein, also jedes Jahr; danach verzinst sich nur der Nettozins weiter. Das entspricht einer Eingabe von Zins × 0,75. Bei ETFs, Aktien, Fonds und Anleihen fallen 27,5 % auf Kursgewinne erst beim Verkauf an; bis dahin arbeitet das volle Kapital weiter. Der Rechner zieht sie deshalb einmal am Ende vom Gesamtgewinn ab. „Rendite × 0,725“ einzugeben wäre hier falsch und würde das Ergebnis um mehrere Prozent zu niedrig ausweisen. Nicht enthalten: die jährlich besteuerten ausschüttungsgleichen Erträge thesaurierender Fonds, Ausschüttungen während der Laufzeit, Verlustausgleich und ausländische Quellensteuer; das Nettoergebnis bei Wertpapieren liegt in Wirklichkeit etwas darunter.</p><p>Inflation und Kosten sind nicht abgezogen. Bei Aktien und ETFs ist die Rendite nicht garantiert und schwankt von Jahr zu Jahr.</p>'" if land=='at' else "<p>Mit dem Haken „Abgeltungsteuer abziehen“ rechnet der Rechner 25 % Abgeltungsteuer plus 5,5 % Solidaritätszuschlag darauf, zusammen 26,375 %, ohne Kirchensteuer. Der Zeitpunkt hängt von der Anlageart ab: Zinsen von Tagesgeld und Festgeld werden bei jeder Gutschrift besteuert, also jedes Jahr, abzüglich des Sparer-Pauschbetrags pro Jahr; danach verzinst sich nur der Rest weiter. Kursgewinne von ETFs, Aktien und Anleihen werden erst beim Verkauf besteuert; bis dahin arbeitet das volle Kapital. Der Rechner zieht die Steuer deshalb einmal am Ende vom Gesamtgewinn ab, bei Aktien-ETFs und Aktienfonds nach 30 % Teilfreistellung, und setzt den Pauschbetrag einmal an. Nicht enthalten: die jährliche Vorabpauschale bei thesaurierenden Fonds, Ausschüttungen während der Laufzeit, Verlustverrechnung und Kirchensteuer.</p><p>Inflation und Kosten sind nicht abgezogen. Bei Aktien und ETFs ist die Rendite nicht garantiert und schwankt von Jahr zu Jahr.</p>'"),
      faq=[('Was ist der Zinseszins?','Zinsen, die auf bereits erhaltene Zinsen gezahlt werden. Je länger du sparst, desto stärker wächst das Kapital dadurch.'),
           ('Welche Rendite ist realistisch?','Festgeld bringt feste Zinsen, Tagesgeld variable. Breit gestreute Aktien-ETFs haben historisch langfristig rund 6 bis 8 % pro Jahr gebracht, aber mit starken Schwankungen und ohne Garantie.'),
           ('Sind Steuern berücksichtigt?','Nur wenn du den Haken setzt. Dann zieht der Rechner '+('die KESt ab: 25 % jährlich bei Bankzinsen, 27,5 % am Ende bei ETFs, Aktien, Fonds und Anleihen.' if land=='at' else 'die Abgeltungsteuer mit Soli (26,375 %) ab: jährlich bei Tagesgeld und Festgeld, am Ende bei ETFs, Aktien und Anleihen, abzüglich Sparer-Pauschbetrag.')+' Ohne Haken ist das Ergebnis vor Steuern. Für eine einzelne Ertragssumme gibt es unseren '+('KESt-Rechner.' if land=='at' else 'Abgeltungsteuer-Rechner.')),
           ('Warum wird die Steuer bei ETFs anders gerechnet als bei Zinsen?','Zinsen werden jedes Jahr besteuert, Kursgewinne erst beim Verkauf. Beim ETF bleibt die Steuer also bis zum Ende im Depot und wird mitverzinst. Deshalb ist das Netto-Ergebnis bei gleicher Rendite höher als bei einem Sparkonto, und deshalb wäre es falsch, einfach die Rendite um den Steuersatz zu kürzen.')])
    calc('kreditrechner',icon='bank',t='Kreditrechner',mt='Kreditrechner: Rate, Zinsen, Tilgungsplan | Finvallo',
      desc='Kreditrechner: Monatsrate, Gesamtzinsen, effektiven Jahreszins und Tilgungsplan für einen Ratenkredit berechnen. Oder die Laufzeit aus einer Wunschrate.',
      lede='Was kostet ein Kredit pro Monat und insgesamt? Mit Tilgungsplan.',
      form=inp('K','Kreditbetrag','20.000','€')+inp('i','Sollzins pro Jahr','6','%')+sel('mode','Berechnen',[('rate','Monatsrate aus Laufzeit',True),('months','Laufzeit aus Monatsrate',False)])+inp('n','Laufzeit','60','Monate')+inp('A','Wunschrate','200','€','nur für „Laufzeit aus Monatsrate“'),
      out='<div class="res"><div><small>Monatsrate</small><b id="o1">–</b></div><div><small>Laufzeit</small><b id="o2">–</b></div><div><small>Zinsen gesamt</small><b id="o3">–</b></div><div><small>Effektiver Jahreszins</small><b id="o4">–</b></div></div><div class="tbl" id="tab"></div>',
      js='''const K=n('K'),i=n('i')/100;let A,N;
if(v('mode')==='rate'){N=Math.round(n('n'));A=FinCalc.annuity(K,i,N);}else{A=n('A');N=FinCalc.annuityMonths(K,i,A);}
if(!isFinite(N)){set('o1',FinCalc.eur(A));set('o2','nie');set('o3','–');set('o4',FinCalc.pct(FinCalc.effective(i)));q('tab').innerHTML='<p class="note">Die Rate ist kleiner als die monatlichen Zinsen. So wird der Kredit nie abbezahlt.</p>';return;}
const s=FinCalc.schedule(K,i,A);set('o1',FinCalc.eur(A));set('o2',FinCalc.months(s.months));set('o3',FinCalc.eur(s.interest));set('o4',FinCalc.pct(FinCalc.effective(i)));
q('tab').innerHTML='<table><thead><tr><th>Jahr</th><th>Zinsen</th><th>Tilgung</th><th>Restschuld</th></tr></thead><tbody>'+s.years.map(x=>`<tr><td>${x.year}</td><td>${FinCalc.eur(x.interest)}</td><td>${FinCalc.eur(x.principal)}</td><td><b>${FinCalc.eur(x.rest)}</b></td></tr>`).join('')+'</tbody></table>';''',
      how='<p>Gerechnet wird ein Annuitätendarlehen: Die Monatsrate bleibt gleich, der Zinsanteil sinkt und der Tilgungsanteil steigt. Die Monatsrate ergibt sich aus <i>Rate = Betrag × q × (1+q)<sup>n</sup> / ((1+q)<sup>n</sup> − 1)</i> mit q = Sollzins / 12 und n = Laufzeit in Monaten. Der effektive Jahreszins ist hier (1 + Sollzins/12)<sup>12</sup> − 1, ohne Gebühren.</p><p>Bearbeitungsgebühren, Restschuldversicherungen und Sondertilgungen sind nicht enthalten. Die letzte Rate ist bei Banken oft etwas kleiner.</p>',
      faq=[('Was ist der Unterschied zwischen Sollzins und effektivem Jahreszins?','Der Sollzins ist der vereinbarte Zinssatz. Der effektive Jahreszins im Kreditangebot rechnet zusätzlich vorgeschriebene Kosten ein und ist deshalb besser zum Vergleichen. Dieser Rechner zeigt nur den Effekt der monatlichen Verzinsung, ohne Gebühren. Der Effektivzins im Angebot kann deshalb höher sein.'),
           ('Kürzere oder längere Laufzeit?','Eine längere Laufzeit senkt die Monatsrate, erhöht aber die Zinsen insgesamt.')])
    calc('teilzahlung',icon='card',t='Teilzahlungsrechner für Kreditkarten',mt='Teilzahlungsrechner Kreditkarte: Zinsen & Dauer | Finvallo',
      desc='Was kostet die Teilzahlung bei der Kreditkarte? Rechner für Zinsen und Dauer bei Mindestrate, mit effektivem Jahreszins deiner Karte.',
      lede='Was kostet es, wenn du die Kreditkartenrechnung nur in Raten zahlst?',
      form=inp('B','Offener Betrag','2.000','€')+inp('e','Effektiver Jahreszins der Karte','22','%','steht im Preisverzeichnis, meist 15 bis 25 %')+inp('p','Mindestrate','3','%','vom offenen Betrag pro Monat')+inp('m','Mindestbetrag','20','€'),
      out='<div class="res"><div><small>Dauer bis abbezahlt</small><b id="o1">–</b></div><div><small>Zinsen gesamt</small><b id="o2">–</b></div><div><small>Zahlst du insgesamt</small><b id="o3">–</b></div></div><p class="note" id="o4"></p>',
      js='''const r=FinCalc.revolving({balance:n('B'),eff:n('e')/100,pct:n('p')/100,min:n('m')});set('o1',FinCalc.months(r.months));set('o2',FinCalc.eur(r.interest));set('o3',FinCalc.eur(r.paid));
q('o4').textContent=isFinite(r.interest)?`Zahlst du die Rechnung dagegen vollständig, fallen bei Einkäufen 0 € Zinsen an. Die Teilzahlung kostet dich also ${FinCalc.eur(r.interest)} extra.`:'Die Mindestrate ist kleiner als die monatlichen Zinsen. So wird der Betrag nie kleiner.';''',
      how='<p>Jeden Monat werden Zinsen auf den offenen Betrag berechnet (Monatszins aus dem effektiven Jahreszins), dann zahlst du die Mindestrate: den Prozentsatz vom offenen Betrag, aber mindestens den Mindestbetrag. Weil die Rate mit dem Betrag schrumpft, dauert es lange, bis alles bezahlt ist.</p><p>Banken rechnen oft taggenau und nach Buchungsdatum, deshalb weichen echte Abrechnungen etwas ab.</p>',
      faq=[('Wie vermeide ich Zinsen bei der Kreditkarte?','Stell die Rückzahlung auf 100 % oder zahl die ganze Rechnung bis zum Fälligkeitstag. Dann fallen für Einkäufe keine Zinsen an.'),
           ('Welche Karten haben keine Teilzahlung?','Charge-Karten buchen die ganze Rechnung einmal im Monat ab. Mehr dazu im Ratgeber Teilzahlung.')],
      links=[('../../ratgeber/teilzahlung/','Ratgeber: Teilzahlung'),('../../kreditkarten/','Kreditkarten vergleichen')])
    calc('entnahmeplan',icon='coin',t='Entnahmeplan-Rechner',mt='Entnahmeplan-Rechner: Wie lange reicht mein Geld? | Finvallo',
      desc='Entnahmeplan berechnen: Wie lange reicht dein Kapital bei monatlicher Entnahme und Rendite? Oder wie viel kannst du jeden Monat entnehmen?',
      lede='Wie lange reicht dein Kapital, wenn du jeden Monat etwas entnimmst?',
      form=inp('K','Kapital','200.000','€')+inp('r','Rendite pro Jahr','4','%')+sel('mode','Berechnen',[('months','Dauer aus Entnahme',True),('amount','Entnahme aus Dauer',False)])+inp('W','Monatliche Entnahme','1.000','€')+inp('y','Gewünschte Dauer','25','Jahre','nur für „Entnahme aus Dauer“'),
      out='<div class="res"><div><small id="l1">Reicht für</small><b id="o1">–</b></div><div><small>Summe der Entnahmen</small><b id="o2">–</b></div></div><p class="note" id="o3"></p>',
      js='''const K=n('K'),r=n('r')/100;
if(v('mode')==='months'){const W=n('W'),x=FinCalc.withdrawMonths(K,r,W);q('l1').textContent='Reicht für';set('o1',isFinite(x.months)?FinCalc.months(x.months):'unbegrenzt');set('o2',isFinite(x.months)?FinCalc.eur(x.total):'–');q('o3').textContent=isFinite(x.months)?'':'Die Erträge sind höher als die Entnahme. Das Kapital wird so nicht aufgebraucht.';}
else{const N=Math.round(n('y')*12),W=FinCalc.withdrawAmount(K,r,N);q('l1').textContent='Mögliche Entnahme pro Monat';set('o1',FinCalc.eur(W));set('o2',FinCalc.eur(W*N));q('o3').textContent=`Nach ${n('y')} Jahren ist das Kapital aufgebraucht.`;}''',
      how='<p>Die Entnahme erfolgt jeweils zu Monatsbeginn, danach wird das restliche Kapital mit dem Monatszins verzinst, der genau der angegebenen Jahresrendite entspricht. Die mögliche Entnahme für eine feste Dauer folgt aus der Rentenbarwertformel für vorschüssige Zahlungen.</p><p>Steuern, Kosten, Inflation und Schwankungen der Rendite sind nicht berücksichtigt. Fällt die Rendite in schlechten Jahren, reicht das Geld kürzer.</p>',
      faq=[('Was ist die 4-Prozent-Regel?','Eine Faustregel aus den USA: Im ersten Jahr 4 % des Depots entnehmen und den Betrag dann mit der Inflation anpassen. Sie basiert auf historischen US-Daten und ist keine Garantie.')])
    calc('inflationsrechner',icon='pie',t='Inflationsrechner',mt='Inflationsrechner: Kaufkraft berechnen | Finvallo',
      desc='Inflationsrechner: Wie viel ist dein Geld in einigen Jahren noch wert, und wie viel brauchst du später für die gleiche Kaufkraft?',
      lede='Wie viel ist dein Geld in einigen Jahren noch wert?',
      form=inp('a','Betrag heute','10.000','€')+inp('i','Inflationsrate pro Jahr','3','%')+inp('y','Zeitraum','10','Jahre'),
      out='<div class="res"><div><small>Kaufkraft danach</small><b id="o1">–</b></div><div><small>Nötiger Betrag für gleiche Kaufkraft</small><b id="o2">–</b></div><div><small>Kaufkraftverlust</small><b id="o3">–</b></div></div>',
      js='''const x=FinCalc.inflation(n('a'),n('i')/100,n('y'));set('o1',FinCalc.eur(x.real));set('o2',FinCalc.eur(x.needed));set('o3',FinCalc.pct(1-x.real/n('a')));''',
      how='<p>Kaufkraft = Betrag / (1 + Inflationsrate)<sup>Jahre</sup>. Der nötige Betrag für dieselbe Kaufkraft ist Betrag × (1 + Inflationsrate)<sup>Jahre</sup>.</p><p>Der Rechner nimmt eine gleichbleibende Inflation an. In Wirklichkeit schwankt sie von Jahr zu Jahr.</p>',
      faq=[('Wie hoch ist die Inflation?',f'Das veröffentlicht {"das Statistische Bundesamt (Destatis)" if land=="de" else "die Statistik Austria"} jeden Monat. Das Inflationsziel der Europäischen Zentralbank liegt bei 2 % pro Jahr.')])
    calc('renditerechner',icon='chart',t='Renditerechner',mt='Renditerechner: jährliche Rendite berechnen | Finvallo',
      desc='Renditerechner: jährliche Rendite (CAGR) und Gesamtrendite aus Anfangswert, Endwert und Anlagedauer berechnen.',
      lede='Wie viel Prozent pro Jahr hat deine Geldanlage gebracht?',
      form=inp('a','Anfangswert','10.000','€')+inp('b','Endwert','15.000','€')+inp('y','Anlagedauer','5','Jahre'),
      out='<div class="res"><div><small>Rendite pro Jahr</small><b id="o1">–</b></div><div><small>Gesamtrendite</small><b id="o2">–</b></div><div><small>Gewinn</small><b id="o3">–</b></div></div>',
      js='''const a=n('a'),b=n('b'),y=n('y');set('o1',FinCalc.pct(FinCalc.cagr(a,b,y)));set('o2',FinCalc.pct(b/a-1));set('o3',FinCalc.eur(b-a));''',
      how='<p>Die jährliche Rendite ist der durchschnittliche Zuwachs pro Jahr mit Zinseszins: (Endwert / Anfangswert)<sup>1/Jahre</sup> − 1. Man nennt sie auch CAGR.</p><p>Gilt nur für eine Einmalanlage ohne Zu- und Abflüsse. Bei Sparplänen ist die Rechnung komplizierter.</p>',
      faq=[('Warum ist die Jahresrendite kleiner als Gesamtrendite durch Jahre?','Wegen des Zinseszinses: Die Erträge eines Jahres bringen im nächsten Jahr selbst Erträge.')])
    if land=='de':
        calc('kapitalertragsteuer',icon='shield',t='Abgeltungsteuer-Rechner',mt='Abgeltungsteuer-Rechner 2026 mit Freibetrag | Finvallo',
          desc='Abgeltungsteuer berechnen: 25 % plus Solidaritätszuschlag und Kirchensteuer, mit Sparerpauschbetrag von 1.000 € bzw. 2.000 €.',
          lede='Wie viel Steuer zahlst du in Deutschland auf Zinsen, Dividenden und Kursgewinne?',
          form=inp('g','Kapitalerträge im Jahr','1.000','€')+sel('fb','Sparerpauschbetrag',[('1000','1.000 € (ledig)',False),('2000','2.000 € (zusammen veranlagt)',False),('0','schon ausgeschöpft',True)])+sel('k','Kirchensteuer',[('0','keine',True),('0.08','8 % (Bayern, Baden-Württemberg)',False),('0.09','9 % (übrige Bundesländer)',False)]),
          out='<div class="res"><div><small>Steuern gesamt</small><b id="o1">–</b></div><div><small>Netto-Ertrag</small><b id="o2">–</b></div><div><small>davon Abgeltungsteuer</small><b id="o3">–</b></div><div><small>Soli / Kirchensteuer</small><b id="o4">–</b></div></div>',
          js='''const x=FinCalc.taxDE({gain:n('g'),allowance:+v('fb'),church:+v('k')});set('o1',FinCalc.eur(x.total));set('o2',FinCalc.eur(x.net));set('o3',FinCalc.eur(x.abg));set('o4',FinCalc.eur(x.soli)+' / '+FinCalc.eur(x.kist));''',
          how='<p>Auf Kapitalerträge über dem Sparerpauschbetrag fallen 25 % Abgeltungsteuer an, darauf 5,5 % Solidaritätszuschlag. Mit Kirchensteuer sinkt die Abgeltungsteuer leicht, weil die Kirchensteuer abziehbar ist: Abgeltungsteuer = Erträge / (4 + Kirchensteuersatz). Insgesamt sind das 26,375 % ohne, 27,82 % mit 8 % und 27,99 % mit 9 % Kirchensteuer.</p><p>Nicht berücksichtigt: Teilfreistellung bei Fonds und ETFs, Vorabpauschale, Verlustverrechnung, Günstigerprüfung und ausländische Quellensteuer.</p>',
          faq=[('Wie hoch ist der Sparerpauschbetrag?','1.000 € pro Person und Jahr, 2.000 € bei Zusammenveranlagung. Dafür stellst du bei deiner Bank einen Freistellungsauftrag.'),
               ('Gilt das auch für ETFs?','Grundsätzlich ja. Bei Aktien-ETFs sind aber 30 % der Erträge steuerfrei (Teilfreistellung). Das rechnet dieser einfache Rechner nicht mit.')])
    else:
        calc('kapitalertragsteuer',icon='shield',t='KESt-Rechner (Kapitalertragsteuer)',mt='KESt-Rechner Österreich: 25 % und 27,5 % | Finvallo',
          desc='Kapitalertragsteuer in Österreich berechnen: 25 % auf Zinsen von Sparkonten, 27,5 % auf Dividenden, Kursgewinne, Fonds und Anleihen.',
          lede='Wie viel KESt zahlst du in Österreich auf deine Kapitalerträge?',
          form=inp('g','Kapitalerträge im Jahr','1.000','€')+sel('rt','Art der Erträge',[('0.275','Dividenden, Kursgewinne, Fonds, ETFs, Anleihen (27,5 %)',True),('0.25','Zinsen von Sparbuch, Tagesgeld, Festgeld bei Banken (25 %)',False)]),
          out='<div class="res"><div><small>KESt</small><b id="o1">–</b></div><div><small>Netto-Ertrag</small><b id="o2">–</b></div></div>',
          js='''const x=FinCalc.taxAT({gain:n('g'),rate:+v('rt')});set('o1',FinCalc.eur(x.total));set('o2',FinCalc.eur(x.net));''',
          how='<p>In Österreich gibt es keinen Freibetrag für Kapitalerträge. Zinsen aus Geldeinlagen bei Banken, also Sparbuch, Tagesgeld und Festgeld, werden mit 25 % besteuert. Für Dividenden, Kursgewinne, Fonds, ETFs und Anleihen gilt der Sondersteuersatz von 27,5 %. Bei inländischen Banken wird die KESt automatisch abgezogen.</p><p>Nicht berücksichtigt: Verlustausgleich, Regelbesteuerungsoption und ausländische Quellensteuer. Bei ausländischen Brokern musst du die Erträge oft selbst in der Steuererklärung angeben.</p>',
          faq=[('Gibt es in Österreich einen Freibetrag für Kapitalerträge?','Nein. Anders als in Deutschland mit dem Sparer-Pauschbetrag gibt es in Österreich keinen Freibetrag.'),
               ('Muss ich die KESt selbst zahlen?','Bei österreichischen Banken und Brokern wird sie automatisch abgezogen. Bei ausländischen Anbietern meist nicht, dann gibst du die Erträge in der Steuererklärung an.')])
    rates=[('0.19','19 % (Regelsatz)',True),('0.07','7 % (ermäßigt)',False)] if land=='de' else [('0.20','20 % (Normalsatz)',True),('0.13','13 % (ermäßigt)',False),('0.10','10 % (ermäßigt)',False)]
    calc('mehrwertsteuer',icon='calc',t='Mehrwertsteuer-Rechner' if land=='de' else 'Umsatzsteuer-Rechner (MwSt)',mt=f'Mehrwertsteuer-Rechner {N}: Brutto & Netto | Finvallo' if land=='de' else 'Umsatzsteuer-Rechner (MwSt) Österreich: Brutto & Netto | Finvallo',
      desc=f'Mehrwertsteuer in {N} berechnen: Brutto zu Netto und Netto zu Brutto mit {"19 % und 7 %" if land=="de" else "20 %, 13 % und 10 %"}.',
      lede='Brutto in Netto umrechnen oder umgekehrt.',
      form=inp('a','Betrag','100','€')+sel('from',f'Der Betrag ist',[('brutto','brutto (inkl. MwSt)',False),('netto','netto (ohne MwSt)',True)])+sel('rt','Steuersatz',rates),
      out='<div class="res"><div><small>Netto</small><b id="o1">–</b></div><div><small>Mehrwertsteuer</small><b id="o2">–</b></div><div><small>Brutto</small><b id="o3">–</b></div></div>',
      js='''const x=FinCalc.vat({amount:n('a'),rate:+v('rt'),from:v('from')});set('o1',FinCalc.eur(x.net));set('o2',FinCalc.eur(x.vat));set('o3',FinCalc.eur(x.gross));''',
      how=f'<p>Netto zu Brutto: Netto × (1 + Steuersatz). Brutto zu Netto: Brutto / (1 + Steuersatz). In {N} gelten {"19 % als Regelsatz und 7 % zum Beispiel für viele Lebensmittel und Bücher" if land=="de" else "20 % als Normalsatz, 10 % zum Beispiel für Lebensmittel, Bücher, Mieten und Beherbergung und 13 % zum Beispiel für Blumen, Theater oder Kino"}.</p>',
      faq=[('Was ist der Unterschied zwischen Brutto und Netto?','Brutto enthält die Mehrwertsteuer, netto nicht.')])
# B12: Beispielsatz zu den Standardwerten, Zahlen aus dem vorgerechneten Ergebnis (o = id → Text)
EX={'zinseszins':lambda o,l:f'10.000 € Startkapital, 200 € Sparrate zu Monatsbeginn, 5 % Zins pro Jahr und 20 Jahre Laufzeit: Du zahlst {o["o2"]} ein und hast am Ende {o["o1"]}, davon {o["o3"]} Zinsen und Erträge.',
    'kreditrechner':lambda o,l:f'Ein Kredit über 20.000 € zu 6 % Sollzins und 60 Monaten Laufzeit kostet {o["o1"]} im Monat und insgesamt {o["o3"]} Zinsen, der effektive Jahreszins ohne Gebühren liegt bei {o["o4"]}.',
    'teilzahlung':lambda o,l:f'Zahlst du 2.000 € offenen Kreditkartenbetrag bei 22 % effektivem Jahreszins mit 3 % Mindestrate (mindestens 20 €) ab, dauert das {o["o1"]} und kostet {o["o2"]} Zinsen.',
    'entnahmeplan':lambda o,l:f'Entnimmst du aus 200.000 € Kapital bei 4 % Rendite jeden Monat 1.000 €, reicht das Geld für {o["o1"]}, insgesamt sind das {o["o2"]}.',
    'inflationsrechner':lambda o,l:f'10.000 € sind bei 3 % Inflation nach 10 Jahren nur noch {o["o1"]} wert, für dieselbe Kaufkraft bräuchtest du dann {o["o2"]}.',
    'renditerechner':lambda o,l:f'Werden aus 10.000 € in 5 Jahren 15.000 €, sind das {o["o2"]} Gesamtrendite und {o["o1"]} Rendite pro Jahr.',
    'kapitalertragsteuer':lambda o,l:(f'Auf 1.000 € Dividenden und Kursgewinne fallen in Österreich {o["o1"]} KESt (27,5 %) an, netto bleiben {o["o2"]}.' if l=='at' else
        f'Auf 1.000 € Kapitalerträge über dem Sparerpauschbetrag fallen ohne Kirchensteuer {o["o3"]} Abgeltungsteuer (25 %) und {o["o4"].split(" / ")[0]} Soli (5,5 %) an, zusammen {o["o1"]}, netto bleiben {o["o2"]}.'),
    'mehrwertsteuer':lambda o,l:f'100 € netto ergeben mit {"19 % MwSt" if l=="de" else "20 % USt"} {o["o3"]} brutto, die Steuer beträgt {o["o2"]}.'}
def defaults(form):
    d={m.group(1):m.group(2) for m in re.finditer(r'<input id="([^"]+)"[^>]*value="([^"]*)"',form)}
    for m in re.finditer(r'<select id="([^"]+)"[^>]*>(.*?)</select>',form):
        o=re.search(r'<option value="([^"]*)" selected',m.group(2)) or re.search(r'<option value="([^"]*)"',m.group(2)); d[m.group(1)]=o.group(1)
    return d
def prerender(calcs):
    """Rechnet alle Rechner mit Standardwerten über tools/prerender.js (dieselbe Logik wie im Browser)."""
    import subprocess
    jobs=[{'key':k,'js':c['js'],'vals':defaults(c['form'])} for k,c in calcs.items()]
    try: r=subprocess.run(['node',os.path.join(os.path.dirname(os.path.abspath(__file__)),'prerender.js')],input=json.dumps(jobs),capture_output=True,text=True,check=True)
    except Exception as e: print('Vorrendern nicht möglich (node fehlt?):',e); return {}
    return json.loads(r.stdout)
def fill(out,res):
    for id_,x in res.items():
        inner=x['html'] if x['html'] else E(x['text'])
        out=re.sub(rf'(<(\w+)\b[^>]*\bid="{id_}"[^>]*>).*?(</\2>)',lambda m:m.group(1)+inner+m.group(3),out,count=1,flags=re.S)
    return out
ICONS={'chart':'<path d="M3 17l5.5-5.5 4 4L21 7M15 7h6v6"/>','bank':'<path d="M3 9.5L12 4l9 5.5M5 10v8M9.5 10v8M14.5 10v8M19 10v8M3 20h18"/>','card':'<rect x="2.5" y="5" width="19" height="14" rx="2.5"/><path d="M2.5 10h19M6 15h4"/>','coin':'<circle cx="12" cy="12" r="9"/><path d="M14.5 9.5c-.5-1-1.5-1.5-2.5-1.5-1.5 0-2.5.8-2.5 2s1 1.7 2.5 2 2.5.8 2.5 2-1 2-2.5 2c-1 0-2-.5-2.5-1.5"/>','pie':'<path d="M12 3v9h9a9 9 0 1 1-9-9z"/>','shield':'<path d="M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6z"/>','calc':'<rect x="5" y="2.5" width="14" height="19" rx="2"/><path d="M8 6.5h8M8 11h.01M12 11h.01M16 11h.01M8 14.5h.01M12 14.5h.01M16 14.5h.01"/>'}
def ic(k): return f'<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[k]}</svg>'
def page(land,rel,title,desc,body,ld_extra,alt):
    import header as H
    N,lang,loc=LN[land]; P='../'*rel.count('/'); url='https://finvallo.com/'+rel
    css=open(R+'index.html').read(); v=re.search(r'site\.css\?v=([a-z0-9]+)',css).group(1); fv=re.search(r'favicon\.svg\?v=([a-z0-9]+)',css).group(1)
    other='de' if land=='at' else 'at'; orel=rel.replace(land+'/',other+'/',1)
    landdiv=(f'<div class="land" role="group" aria-label="Land wählen"><a href="{P}{rel.replace(land+"/","at/",1)}" hreflang="de-AT" aria-current="{"true" if land=="at" else "false"}" title="Österreich">AT</a>'
             f'<a href="{P}{rel.replace(land+"/","de/",1)}" hreflang="de-DE" aria-current="{"true" if land=="de" else "false"}" title="Deutschland">DE</a></div>')
    ld={"@context":"https://schema.org","@graph":[{"@type":"Organization","@id":"https://finvallo.com/#org","name":"Finvallo","url":"https://finvallo.com/","logo":"https://finvallo.com/assets/logo.svg"},
        {"@type":"WebPage","@id":url+"#page","url":url,"name":title,"description":desc,"inLanguage":lang,"dateModified":STAND,"publisher":{"@id":"https://finvallo.com/#org"}}]+ld_extra}
    alts=f'\n<link rel="alternate" hreflang="de-AT" href="https://finvallo.com/{rel.replace(land+"/","at/",1)}"><link rel="alternate" hreflang="de-DE" href="https://finvallo.com/{rel.replace(land+"/","de/",1)}">' if alt else ''
    h=f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1">
<link rel="canonical" href="{url}">{alts}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Finvallo">
<meta property="og:locale" content="{loc}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://finvallo.com/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0f1720">
<meta name='impact-site-verification' value='395412e1-70ac-412c-9ce9-5e53d7b5e5ef'>
<link rel="icon" href="{P}assets/favicon.svg?v={fv}" type="image/svg+xml">
<link rel="preload" href="{P}assets/fonts/figtree-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{P}assets/site.css?v={v}">
<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False)}</script>
</head>
<body>
{H.build(rel,P,landdiv)}
<div class="wrap"><main id="app">
{body}
</main>
<footer>
<span><b>finvallo</b> · Unabhängiger Finanzvergleich für {N}</span>
<span>Stand {STAND_DE} · Rechner ohne Gewähr · Keine Finanz- oder Steuerberatung.</span>
<nav aria-label="Fußzeile"><a href="{P}{land}/kreditkarten/methodik/">So bewerten wir</a><a href="{P}so-verdienen-wir-geld/">So verdienen wir Geld</a><a href="{P}ueber-uns/">Über Finvallo</a><a href="{P}impressum/">Impressum</a><a href="{P}datenschutz/">Datenschutz</a><a href="{P}llms.txt">Für KI-Assistenten</a></nav>
</footer>
</div>
</body>
</html>
'''
    os.makedirs(R+rel,exist_ok=True); open(R+rel+'index.html','w').write(h)
def build(land):
    CALCS.clear(); define(land); N=LN[land][0]; PRE=prerender(CALCS)
    for slug,c in CALCS.items():
        o={k:v['text'] for k,v in PRE.get(slug,{}).items()}
        try: exs=f'<p class="note calc-ex"><b>Beispiel:</b> {E(EX[slug](o,land))}</p>' if o else ''
        except KeyError: exs=''
        rel=f'{land}/rechner/{slug}/'
        fq=c.get('faq',[])
        links=''.join(f'<a class="btn ghost" href="{u}">{t} →</a>' for u,t in c.get('links',[]))
        others=''.join(f'<a class="catcard" href="../{s}/"><b>{E(x["t"])}</b><small>Zum Rechner →</small></a>' for s,x in CALCS.items() if s!=slug)
        body=f'''<div class="crumb"><span><a href="../">Rechner</a> › {E(c["t"])}</span><span>Stand {STAND_DE}</span></div>
<h1>{E(c["t"])}</h1><p class="lede">{E(c["lede"])}</p>
<form class="box calcbox" id="f" onsubmit="return false"><div class="calc">{c["form"]}</div></form>
<section class="box resbox" aria-live="polite"><h2 style="margin-top:0">Ergebnis</h2>{fill(c["out"],PRE.get(slug,{}))}</section>
{exs}
{DISCLAIMER}
<h2>So rechnet der Rechner</h2><div class="prose">{c["how"]}</div>
{f'<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:12px">{links}</div>' if links else ''}
<h2>Fragen und Antworten</h2><div class="faq">{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q,a in fq)}</div>
<h2>Weitere Rechner</h2><div class="catgrid">{others}</div>
<script src="../../../assets/calc.js?v={CJS}"></script>
<script>(function(){{const q=id=>document.getElementById(id),v=id=>q(id).value,n=id=>FinCalc.num(v(id)),set=(id,t)=>{{q(id).textContent=t}};
function run(){{try{{ {c["js"]} }}catch(e){{console.error(e)}}}}
q('f').addEventListener('input',run);q('f').addEventListener('change',run);run();}})();</script>'''
        ld=[{"@type":"WebApplication","name":c['t'],"url":f"https://finvallo.com/{rel}","applicationCategory":"FinanceApplication","operatingSystem":"Web","inLanguage":LN[land][1],"offers":{"@type":"Offer","price":0,"priceCurrency":"EUR"},"publisher":{"@id":"https://finvallo.com/#org"}},
            {"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":N,"item":f"https://finvallo.com/{land}/"},{"@type":"ListItem","position":2,"name":"Rechner","item":f"https://finvallo.com/{land}/rechner/"},{"@type":"ListItem","position":3,"name":c['t'],"item":f"https://finvallo.com/{rel}"}]}]
        if fq: ld.append({"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in fq]})
        mt=c['mt'] if (N in c['mt'] or 'KESt' in c['mt'] or 'Abgeltung' in c['mt']) else c['mt'].replace(' | Finvallo',f' ({land.upper()}) | Finvallo')
        ds=c['desc']
        if N not in ds:  # Land in die Description, damit AT und DE sich unterscheiden
            i=ds.find(':'); j=ds.find('?')
            ds=ds[:i-10]+f' für {N} berechnen'+ds[i:] if 0<i<45 and ds[:i].endswith(' berechnen') else ds[:i]+f' für {N}'+ds[i:] if 0<i<45 else ds[:j]+f' in {N}'+ds[j:] if j>0 else ds+f' Für {N}.'
        page(land,rel,mt,ds,body,ld,True)
    # Übersicht
    rel=f'{land}/rechner/'
    tiles=f'<a class="hp-tile" href="../kreditkarten/rechner/"><span class="hp-ic">{ic("card")}</span><span><b>Kreditkarten-Kostenrechner</b><small>Was kostet dich eine Karte bei deiner Nutzung?</small></span></a>'
    tiles=f'<a class="hp-tile" href="../../{land}/kreditkarten/rechner/"><span class="hp-ic">{ic("card")}</span><span><b>Kreditkarten-Kostenrechner</b><small>Was kostet dich eine Karte bei deiner Nutzung?</small></span></a>'
    tiles+=''.join(f'<a class="hp-tile" href="{s}/"><span class="hp-ic">{ic(c["icon"])}</span><span><b>{E(c["t"])}</b><small>{E(c["lede"])}</small></span></a>' for s,c in CALCS.items())
    body=f'''<h1>Finanzrechner für {N}</h1><p class="lede">Kostenlose Rechner für Sparen, Kredite, Kreditkarten und Steuern. Ohne Anmeldung, die Berechnung läuft direkt in deinem Browser.</p>
<div class="hp-tiles" style="margin-top:18px">{tiles}</div>
{DISCLAIMER}'''
    ld=[{"@type":"ItemList","name":f"Finanzrechner {N}","itemListElement":[{"@type":"ListItem","position":i+1,"name":c['t'],"url":f"https://finvallo.com/{rel}{s}/"} for i,(s,c) in enumerate(CALCS.items())]}]
    page(land,rel,f'Finanzrechner {N}: Zinsen, Kredit, Steuer | Finvallo',f'Kostenlose Finanzrechner für {N}: Zinseszins, Sparplan, Kredit, Kreditkarten-Teilzahlung, Entnahmeplan, Inflation, Rendite und Steuern.',body,ld,True)
    return list(CALCS)
def sitemap_llms(slugs):
    p=R+'sitemap.xml'; s=open(p).read()
    for land in ('at','de'):
        for u in [f'{land}/rechner/']+[f'{land}/rechner/{x}/' for x in slugs[land]]:
            loc=f'https://finvallo.com/{u}'
            if f'<loc>{loc}</loc>' not in s: s=s.replace('</urlset>',f'<url><loc>{loc}</loc><lastmod>{STAND}</lastmod><changefreq>monthly</changefreq><priority>0.6</priority></url>\n</urlset>')
    open(p,'w').write(s)
    for fn in ('llms.txt','llms-full.txt'):
        p=R+fn; s=open(p).read(); s=re.sub(r'\n## Finanzrechner\n(?:- .*\n?)*','\n',s)
        blk='\n## Finanzrechner\n'+''.join(f'- [{t} ({LN[l][0]})](https://finvallo.com/{l}/rechner/{x}/)\n' for l in ('de','at') for x,t in slugs[l+'_t'])
        s=s.rstrip()+'\n'+blk; open(p,'w').write(s)
CJS=''
def run():
    global CJS
    import hashlib
    CJS=hashlib.sha256(open(R+'assets/calc.js','rb').read()).hexdigest()[:8]
    out={}
    for land in ('at','de'):
        out[land]=build(land); out[land+'_t']=[(s,CALCS[s]['t']) for s in out[land]]
    sitemap_llms(out); print('Rechner:',out['at'],out['de'])
if __name__=='__main__': run()
