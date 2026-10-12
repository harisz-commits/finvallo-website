# Finanzrechner für AT und DE (/at/rechner/, /de/rechner/), Logik in public/assets/calc.js
import json,os,re,html,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','public')+'/'
STAND='2026-10-12'; STAND_DE='12.10.2026'
E=lambda s: html.escape(str(s))
LN={'at':('Österreich','de-AT','de_AT'),'de':('Deutschland','de-DE','de_DE')}
def inp(id,label,val,suffix='',help=''):
    return f'<label>{label}<span class="inw"><input id="{id}" type="text" inputmode="decimal" value="{val}" autocomplete="off">{f"<em>{suffix}</em>" if suffix else ""}</span>{f"<small class=mut>{help}</small>" if help else ""}</label>'
def sel(id,label,opts):
    return f'<label>{label}<select id="{id}">'+''.join(f'<option value="{v}"{" selected" if s else ""}>{t}</option>' for v,t,s in opts)+'</select></label>'
DISCLAIMER='<div class="box disc"><b>Hinweis:</b> Alle Berechnungen sind Beispielrechnungen ohne Gewähr. Trotz sorgfältiger Prüfung können Fehler passieren, und Banken runden oder rechnen im Detail oft anders. Das Ergebnis ersetzt keine Beratung. Prüfe wichtige Entscheidungen mit den Unterlagen deiner Bank.</div>'
CALCS={}
def calc(slug,**kw): CALCS[slug]=kw
def define(land):
    N=LN[land][0]
    calc('zinseszins',icon='chart',t='Zinseszinsrechner & Sparrechner',mt='Zinseszinsrechner & Sparrechner | Finvallo',
      desc='Zinseszinsrechner und Sparrechner: Endkapital mit Startkapital, monatlicher Sparrate, Zins und Dynamik berechnen. Mit Jahrestabelle und Diagramm.',
      lede='Wie viel wird aus deinem Ersparten? Mit Startkapital, monatlicher Sparrate und Zinseszins.',
      form=inp('k0','Startkapital','10.000','€')+inp('pay','Monatliche Sparrate','200','€')+inp('r','Zins oder Rendite pro Jahr','5','%')+inp('y','Laufzeit','20','Jahre')+inp('dyn','Dynamik (Erhöhung der Rate pro Jahr)','0','%')+sel('when','Einzahlung',[('start','zu Monatsbeginn',True),('end','zu Monatsende',False)]),
      out='<div class="res"><div><small>Endkapital</small><b id="o1">–</b></div><div><small>Eingezahlt</small><b id="o2">–</b></div><div><small>Zinsen und Erträge</small><b id="o3">–</b></div></div><div id="chart" class="chart"></div><p class="note"><span class="lg a"></span> Einzahlungen <span class="lg b"></span> Zinsen</p><div class="tbl" id="tab"></div>',
      js='''const r=FinCalc.savings({start:n('k0'),pay:n('pay'),rate:n('r')/100,months:Math.round(n('y')*12),dyn:n('dyn')/100,payStart:v('when')==='start'});
set('o1',FinCalc.eur(r.end));set('o2',FinCalc.eur(r.paid));set('o3',FinCalc.eur(r.interest));
FinCalc.bars(q('chart'),r.years.map(x=>({year:x.year,a:x.paid,b:x.interest})),['a','b'],['var(--card2)','var(--blue)']);
q('tab').innerHTML='<table><thead><tr><th>Jahr</th><th>Eingezahlt</th><th>Zinsen</th><th>Kapital</th></tr></thead><tbody>'+r.years.map(x=>`<tr><td>${x.year}</td><td>${FinCalc.eur(x.paid,0)}</td><td>${FinCalc.eur(x.interest,0)}</td><td><b>${FinCalc.eur(x.balance,0)}</b></td></tr>`).join('')+'</tbody></table>';''',
      how='<p>Der Rechner simuliert jeden Monat: Die Sparrate kommt dazu, dann wird das Guthaben verzinst. Aus dem Jahreszins wird der passende Monatszins berechnet, sodass nach zwölf Monaten genau der angegebene Jahreszins herauskommt (konformer Zins). Mit Dynamik steigt die Sparrate jedes Jahr um den angegebenen Prozentsatz.</p><p><b>Beispiel:</b> 10.000 € Startkapital, 200 € im Monat, 5 % Zins, 20 Jahre: Du zahlst 58.000 € ein und hast am Ende rund 108.025 €, davon rund 50.025 € Zinsen.</p><p>Steuern, Inflation und Kosten sind nicht abgezogen. Bei Aktien und ETFs ist die Rendite nicht garantiert und schwankt von Jahr zu Jahr.</p>',
      faq=[('Was ist der Zinseszins?','Zinsen, die auf bereits erhaltene Zinsen gezahlt werden. Je länger du sparst, desto stärker wächst das Kapital dadurch.'),
           ('Welche Rendite ist realistisch?','Tagesgeld und Festgeld bringen aktuell feste Zinsen. Breit gestreute Aktien-ETFs haben historisch langfristig rund 6 bis 8 % pro Jahr gebracht, aber mit starken Schwankungen und ohne Garantie.'),
           ('Sind Steuern berücksichtigt?','Nein. Das Ergebnis ist vor Steuern. Für Steuern auf Kapitalerträge gibt es unseren Kapitalertragsteuer-Rechner.')])
    calc('kreditrechner',icon='bank',t='Kreditrechner',mt='Kreditrechner: Rate, Zinsen, Tilgungsplan | Finvallo',
      desc='Kreditrechner: Monatsrate, Gesamtzinsen, effektiven Jahreszins und Tilgungsplan für einen Ratenkredit berechnen. Oder die Laufzeit aus einer Wunschrate.',
      lede='Was kostet ein Kredit pro Monat und insgesamt? Mit Tilgungsplan.',
      form=inp('K','Kreditbetrag','10.000','€')+inp('i','Sollzins pro Jahr','6','%')+sel('mode','Berechnen',[('rate','Monatsrate aus Laufzeit',True),('months','Laufzeit aus Monatsrate',False)])+inp('n','Laufzeit','60','Monate')+inp('A','Wunschrate','200','€','nur für „Laufzeit aus Monatsrate“'),
      out='<div class="res"><div><small>Monatsrate</small><b id="o1">–</b></div><div><small>Laufzeit</small><b id="o2">–</b></div><div><small>Zinsen gesamt</small><b id="o3">–</b></div><div><small>Effektiver Jahreszins</small><b id="o4">–</b></div></div><div class="tbl" id="tab"></div>',
      js='''const K=n('K'),i=n('i')/100;let A,N;
if(v('mode')==='rate'){N=Math.round(n('n'));A=FinCalc.annuity(K,i,N);}else{A=n('A');N=FinCalc.annuityMonths(K,i,A);}
if(!isFinite(N)){set('o1',FinCalc.eur(A));set('o2','nie');set('o3','–');set('o4',FinCalc.pct(FinCalc.effective(i)));q('tab').innerHTML='<p class="note">Die Rate ist kleiner als die monatlichen Zinsen. So wird der Kredit nie abbezahlt.</p>';return;}
const s=FinCalc.schedule(K,i,A);set('o1',FinCalc.eur(A));set('o2',FinCalc.months(s.months));set('o3',FinCalc.eur(s.interest));set('o4',FinCalc.pct(FinCalc.effective(i)));
q('tab').innerHTML='<table><thead><tr><th>Jahr</th><th>Zinsen</th><th>Tilgung</th><th>Restschuld</th></tr></thead><tbody>'+s.years.map(x=>`<tr><td>${x.year}</td><td>${FinCalc.eur(x.interest)}</td><td>${FinCalc.eur(x.principal)}</td><td><b>${FinCalc.eur(x.rest)}</b></td></tr>`).join('')+'</tbody></table>';''',
      how='<p>Gerechnet wird ein Annuitätendarlehen: Die Monatsrate bleibt gleich, der Zinsanteil sinkt und der Tilgungsanteil steigt. Die Monatsrate ergibt sich aus <i>Rate = Betrag × q × (1+q)<sup>n</sup> / ((1+q)<sup>n</sup> − 1)</i> mit q = Sollzins / 12 und n = Laufzeit in Monaten. Der effektive Jahreszins ist hier (1 + Sollzins/12)<sup>12</sup> − 1, ohne Gebühren.</p><p><b>Beispiel:</b> 10.000 € zu 6 % Sollzins über 60 Monate: 193,33 € pro Monat, insgesamt 1.599,68 € Zinsen, effektiv 6,17 %.</p><p>Bearbeitungsgebühren, Restschuldversicherungen und Sondertilgungen sind nicht enthalten. Die letzte Rate ist bei Banken oft etwas kleiner.</p>',
      faq=[('Was ist der Unterschied zwischen Sollzins und effektivem Jahreszins?','Der Sollzins ist der vereinbarte Zinssatz. Der effektive Jahreszins rechnet die monatliche Zinsbelastung und vorgeschriebene Kosten mit ein und ist deshalb besser zum Vergleichen.'),
           ('Kürzere oder längere Laufzeit?','Eine längere Laufzeit senkt die Monatsrate, erhöht aber die Zinsen insgesamt.')])
    calc('teilzahlung',icon='card',t='Teilzahlungsrechner für Kreditkarten',mt='Teilzahlungsrechner Kreditkarte: Zinsen & Dauer | Finvallo',
      desc='Was kostet die Teilzahlung bei der Kreditkarte? Rechner für Zinsen und Dauer bei Mindestrate, mit effektivem Jahreszins deiner Karte.',
      lede='Was kostet es, wenn du die Kreditkartenrechnung nur in Raten zahlst?',
      form=inp('B','Offener Betrag','2.000','€')+inp('e','Effektiver Jahreszins der Karte','22','%','steht im Preisverzeichnis, meist 15 bis 25 %')+inp('p','Mindestrate','3','%','vom offenen Betrag pro Monat')+inp('m','Mindestbetrag','20','€'),
      out='<div class="res"><div><small>Dauer bis abbezahlt</small><b id="o1">–</b></div><div><small>Zinsen gesamt</small><b id="o2">–</b></div><div><small>Zahlst du insgesamt</small><b id="o3">–</b></div></div><p class="note" id="o4"></p>',
      js='''const r=FinCalc.revolving({balance:n('B'),eff:n('e')/100,pct:n('p')/100,min:n('m')});set('o1',FinCalc.months(r.months));set('o2',FinCalc.eur(r.interest));set('o3',FinCalc.eur(r.paid));
q('o4').textContent=isFinite(r.interest)?`Zahlst du die Rechnung dagegen vollständig, fallen bei Einkäufen 0 € Zinsen an. Die Teilzahlung kostet dich also ${FinCalc.eur(r.interest)} extra.`:'Die Mindestrate ist kleiner als die monatlichen Zinsen. So wird der Betrag nie kleiner.';''',
      how='<p>Jeden Monat werden Zinsen auf den offenen Betrag berechnet (Monatszins aus dem effektiven Jahreszins), dann zahlst du die Mindestrate: den Prozentsatz vom offenen Betrag, aber mindestens den Mindestbetrag. Weil die Rate mit dem Betrag schrumpft, dauert es lange, bis alles bezahlt ist.</p><p><b>Beispiel:</b> 2.000 € offen, 22 % effektiv, 3 % Mindestrate, mindestens 20 €: Es dauert 10 Jahre und 9 Monate und kostet rund 1.931 € Zinsen. Du zahlst also fast das Doppelte.</p><p>Banken rechnen oft taggenau und nach Buchungsdatum, deshalb weichen echte Abrechnungen etwas ab.</p>',
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
      how='<p>Die Entnahme erfolgt jeweils zu Monatsbeginn, danach wird das restliche Kapital mit dem Monatszins verzinst, der genau der angegebenen Jahresrendite entspricht. Die mögliche Entnahme für eine feste Dauer folgt aus der Rentenbarwertformel für vorschüssige Zahlungen.</p><p><b>Beispiel:</b> 200.000 € Kapital, 4 % Rendite, 25 Jahre: Du kannst rund 1.044 € pro Monat entnehmen.</p><p>Steuern, Kosten, Inflation und Schwankungen der Rendite sind nicht berücksichtigt. Fällt die Rendite in schlechten Jahren, reicht das Geld kürzer.</p>',
      faq=[('Was ist die 4-Prozent-Regel?','Eine Faustregel aus den USA: Im ersten Jahr 4 % des Depots entnehmen und den Betrag dann mit der Inflation anpassen. Sie basiert auf historischen US-Daten und ist keine Garantie.')])
    calc('inflationsrechner',icon='pie',t='Inflationsrechner',mt='Inflationsrechner: Kaufkraft berechnen | Finvallo',
      desc='Inflationsrechner: Wie viel ist dein Geld in einigen Jahren noch wert, und wie viel brauchst du später für die gleiche Kaufkraft?',
      lede='Wie viel ist dein Geld in einigen Jahren noch wert?',
      form=inp('a','Betrag heute','1.000','€')+inp('i','Inflationsrate pro Jahr','2','%')+inp('y','Zeitraum','10','Jahre'),
      out='<div class="res"><div><small>Kaufkraft danach</small><b id="o1">–</b></div><div><small>Nötiger Betrag für gleiche Kaufkraft</small><b id="o2">–</b></div><div><small>Kaufkraftverlust</small><b id="o3">–</b></div></div>',
      js='''const x=FinCalc.inflation(n('a'),n('i')/100,n('y'));set('o1',FinCalc.eur(x.real));set('o2',FinCalc.eur(x.needed));set('o3',FinCalc.pct(1-x.real/n('a')));''',
      how='<p>Kaufkraft = Betrag / (1 + Inflationsrate)<sup>Jahre</sup>. Der nötige Betrag für dieselbe Kaufkraft ist Betrag × (1 + Inflationsrate)<sup>Jahre</sup>.</p><p><b>Beispiel:</b> 1.000 € bei 2 % Inflation über 10 Jahre: Sie sind dann noch rund 820 € wert, für dieselbe Kaufkraft bräuchtest du rund 1.219 €.</p><p>Der Rechner nimmt eine gleichbleibende Inflation an. In Wirklichkeit schwankt sie von Jahr zu Jahr.</p>',
      faq=[('Wie hoch ist die Inflation?',f'Das veröffentlicht {"das Statistische Bundesamt (Destatis)" if land=="de" else "die Statistik Austria"} jeden Monat. Das Inflationsziel der Europäischen Zentralbank liegt bei 2 % pro Jahr.')])
    calc('renditerechner',icon='chart',t='Renditerechner',mt='Renditerechner: jährliche Rendite berechnen | Finvallo',
      desc='Renditerechner: jährliche Rendite (CAGR) und Gesamtrendite aus Anfangswert, Endwert und Anlagedauer berechnen.',
      lede='Wie viel Prozent pro Jahr hat deine Geldanlage gebracht?',
      form=inp('a','Anfangswert','10.000','€')+inp('b','Endwert','15.000','€')+inp('y','Anlagedauer','5','Jahre'),
      out='<div class="res"><div><small>Rendite pro Jahr</small><b id="o1">–</b></div><div><small>Gesamtrendite</small><b id="o2">–</b></div><div><small>Gewinn</small><b id="o3">–</b></div></div>',
      js='''const a=n('a'),b=n('b'),y=n('y');set('o1',FinCalc.pct(FinCalc.cagr(a,b,y)));set('o2',FinCalc.pct(b/a-1));set('o3',FinCalc.eur(b-a));''',
      how='<p>Die jährliche Rendite ist der durchschnittliche Zuwachs pro Jahr mit Zinseszins: (Endwert / Anfangswert)<sup>1/Jahre</sup> − 1. Man nennt sie auch CAGR.</p><p><b>Beispiel:</b> Aus 10.000 € werden in 5 Jahren 15.000 €: Das sind 50 % insgesamt und rund 8,45 % pro Jahr.</p><p>Gilt nur für eine Einmalanlage ohne Zu- und Abflüsse. Bei Sparplänen ist die Rechnung komplizierter.</p>',
      faq=[('Warum ist die Jahresrendite kleiner als Gesamtrendite durch Jahre?','Wegen des Zinseszinses: Die Erträge eines Jahres bringen im nächsten Jahr selbst Erträge.')])
    if land=='de':
        calc('kapitalertragsteuer',icon='shield',t='Abgeltungsteuer-Rechner',mt='Abgeltungsteuer-Rechner 2026 mit Freibetrag | Finvallo',
          desc='Abgeltungsteuer berechnen: 25 % plus Solidaritätszuschlag und Kirchensteuer, mit Sparerpauschbetrag von 1.000 € bzw. 2.000 €.',
          lede='Wie viel Steuer zahlst du in Deutschland auf Zinsen, Dividenden und Kursgewinne?',
          form=inp('g','Kapitalerträge im Jahr','2.500','€')+sel('fb','Sparerpauschbetrag',[('1000','1.000 € (ledig)',True),('2000','2.000 € (zusammen veranlagt)',False),('0','schon ausgeschöpft',False)])+sel('k','Kirchensteuer',[('0','keine',True),('0.08','8 % (Bayern, Baden-Württemberg)',False),('0.09','9 % (übrige Bundesländer)',False)]),
          out='<div class="res"><div><small>Steuern gesamt</small><b id="o1">–</b></div><div><small>Netto-Ertrag</small><b id="o2">–</b></div><div><small>davon Abgeltungsteuer</small><b id="o3">–</b></div><div><small>Soli / Kirchensteuer</small><b id="o4">–</b></div></div>',
          js='''const x=FinCalc.taxDE({gain:n('g'),allowance:+v('fb'),church:+v('k')});set('o1',FinCalc.eur(x.total));set('o2',FinCalc.eur(x.net));set('o3',FinCalc.eur(x.abg));set('o4',FinCalc.eur(x.soli)+' / '+FinCalc.eur(x.kist));''',
          how='<p>Auf Kapitalerträge über dem Sparerpauschbetrag fallen 25 % Abgeltungsteuer an, darauf 5,5 % Solidaritätszuschlag. Mit Kirchensteuer sinkt die Abgeltungsteuer leicht, weil die Kirchensteuer abziehbar ist: Abgeltungsteuer = Erträge / (4 + Kirchensteuersatz). Insgesamt sind das 26,375 % ohne, 27,82 % mit 8 % und 27,99 % mit 9 % Kirchensteuer.</p><p><b>Beispiel:</b> 2.400 € Erträge, ledig, ohne Kirchensteuer: 1.400 € sind steuerpflichtig. Darauf fallen 350 € Abgeltungsteuer und 19,25 € Soli an, zusammen 369,25 €.</p><p>Nicht berücksichtigt: Teilfreistellung bei Fonds und ETFs, Vorabpauschale, Verlustverrechnung, Günstigerprüfung und ausländische Quellensteuer.</p>',
          faq=[('Wie hoch ist der Sparerpauschbetrag?','1.000 € pro Person und Jahr, 2.000 € bei Zusammenveranlagung. Dafür stellst du bei deiner Bank einen Freistellungsauftrag.'),
               ('Gilt das auch für ETFs?','Grundsätzlich ja. Bei Aktien-ETFs sind aber 30 % der Erträge steuerfrei (Teilfreistellung). Das rechnet dieser einfache Rechner nicht mit.')])
    else:
        calc('kapitalertragsteuer',icon='shield',t='KESt-Rechner (Kapitalertragsteuer)',mt='KESt-Rechner Österreich: 25 % und 27,5 % | Finvallo',
          desc='Kapitalertragsteuer in Österreich berechnen: 25 % auf Zinsen von Sparkonten, 27,5 % auf Dividenden, Kursgewinne, Fonds und Anleihen.',
          lede='Wie viel KESt zahlst du in Österreich auf deine Kapitalerträge?',
          form=inp('g','Kapitalerträge im Jahr','2.500','€')+sel('rt','Art der Erträge',[('0.275','Dividenden, Kursgewinne, Fonds, ETFs, Anleihen (27,5 %)',True),('0.25','Zinsen von Sparbuch, Tagesgeld, Festgeld bei Banken (25 %)',False)]),
          out='<div class="res"><div><small>KESt</small><b id="o1">–</b></div><div><small>Netto-Ertrag</small><b id="o2">–</b></div></div>',
          js='''const x=FinCalc.taxAT({gain:n('g'),rate:+v('rt')});set('o1',FinCalc.eur(x.total));set('o2',FinCalc.eur(x.net));''',
          how='<p>In Österreich gibt es keinen Freibetrag für Kapitalerträge. Zinsen aus Geldeinlagen bei Banken, also Sparbuch, Tagesgeld und Festgeld, werden mit 25 % besteuert. Für Dividenden, Kursgewinne, Fonds, ETFs und Anleihen gilt der Sondersteuersatz von 27,5 %. Bei inländischen Banken wird die KESt automatisch abgezogen.</p><p><b>Beispiel:</b> 2.500 € Dividenden und Kursgewinne: 687,50 € KESt, netto bleiben 1.812,50 €.</p><p>Nicht berücksichtigt: Verlustausgleich, Regelbesteuerungsoption und ausländische Quellensteuer. Bei ausländischen Brokern musst du die Erträge oft selbst in der Steuererklärung angeben.</p>',
          faq=[('Gibt es in Österreich einen Freibetrag für Kapitalerträge?','Nein, anders als in Deutschland gibt es keinen Sparerfreibetrag.'),
               ('Muss ich die KESt selbst zahlen?','Bei österreichischen Banken und Brokern wird sie automatisch abgezogen. Bei ausländischen Anbietern meist nicht, dann gibst du die Erträge in der Steuererklärung an.')])
    rates=[('0.19','19 % (Regelsatz)',True),('0.07','7 % (ermäßigt)',False)] if land=='de' else [('0.20','20 % (Normalsatz)',True),('0.13','13 % (ermäßigt)',False),('0.10','10 % (ermäßigt)',False)]
    calc('mehrwertsteuer',icon='calc',t='Mehrwertsteuer-Rechner',mt=f'Mehrwertsteuer-Rechner {N}: Brutto & Netto | Finvallo',
      desc=f'Mehrwertsteuer in {N} berechnen: Brutto zu Netto und Netto zu Brutto mit {"19 % und 7 %" if land=="de" else "20 %, 13 % und 10 %"}.',
      lede='Brutto in Netto umrechnen oder umgekehrt.',
      form=inp('a','Betrag','100','€')+sel('from',f'Der Betrag ist',[('brutto','brutto (inkl. MwSt)',True),('netto','netto (ohne MwSt)',False)])+sel('rt','Steuersatz',rates),
      out='<div class="res"><div><small>Netto</small><b id="o1">–</b></div><div><small>Mehrwertsteuer</small><b id="o2">–</b></div><div><small>Brutto</small><b id="o3">–</b></div></div>',
      js='''const x=FinCalc.vat({amount:n('a'),rate:+v('rt'),from:v('from')});set('o1',FinCalc.eur(x.net));set('o2',FinCalc.eur(x.vat));set('o3',FinCalc.eur(x.gross));''',
      how=f'<p>Netto zu Brutto: Netto × (1 + Steuersatz). Brutto zu Netto: Brutto / (1 + Steuersatz). In {N} gelten {"19 % als Regelsatz und 7 % zum Beispiel für viele Lebensmittel und Bücher" if land=="de" else "20 % als Normalsatz, 10 % zum Beispiel für Lebensmittel, Bücher und Mieten und 13 % zum Beispiel für Blumen, Theater oder Beherbergung"}.</p><p><b>Beispiel:</b> {"119 € brutto bei 19 % sind 100 € netto und 19 € MwSt." if land=="de" else "120 € brutto bei 20 % sind 100 € netto und 20 € USt."}</p>',
      faq=[('Was ist der Unterschied zwischen Brutto und Netto?','Brutto enthält die Mehrwertsteuer, netto nicht.')])
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
<nav aria-label="Fußzeile"><a href="{P}{land}/kreditkarten/methodik/">So bewerten wir</a><a href="{P}so-verdienen-wir-geld/">So verdienen wir Geld</a><a href="{P}ueber-uns/">Über uns</a><a href="{P}impressum/">Impressum</a><a href="{P}datenschutz/">Datenschutz</a><a href="{P}llms.txt">Für KI-Assistenten</a></nav>
</footer>
</div>
</body>
</html>
'''
    os.makedirs(R+rel,exist_ok=True); open(R+rel+'index.html','w').write(h)
def build(land):
    CALCS.clear(); define(land); N=LN[land][0]
    for slug,c in CALCS.items():
        rel=f'{land}/rechner/{slug}/'
        fq=c.get('faq',[])
        links=''.join(f'<a class="btn ghost" href="{u}">{t} →</a>' for u,t in c.get('links',[]))
        others=''.join(f'<a class="catcard" href="../{s}/"><b>{E(x["t"])}</b><small>Zum Rechner →</small></a>' for s,x in CALCS.items() if s!=slug)
        body=f'''<div class="crumb"><span><a href="../">Rechner</a> › {E(c["t"])}</span><span>Stand {STAND_DE}</span></div>
<h1>{E(c["t"])}</h1><p class="lede">{E(c["lede"])}</p>
<form class="box calcbox" id="f" onsubmit="return false"><div class="calc">{c["form"]}</div></form>
<section class="box resbox" aria-live="polite"><h2 style="margin-top:0">Ergebnis</h2>{c["out"]}</section>
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
        page(land,rel,mt,c['desc'],body,ld,True)
    # Übersicht
    rel=f'{land}/rechner/'
    tiles=f'<a class="hp-tile" href="../kreditkarten/rechner/" onclick="this.href=\'../../at/kreditkarten/rechner/?land={land.upper()}\'"><span class="hp-ic">{ic("card")}</span><span><b>Kreditkarten-Kostenrechner</b><small>Was kostet dich eine Karte bei deiner Nutzung?</small></span></a>'
    tiles=f'<a class="hp-tile" href="../../at/kreditkarten/rechner/?land={land.upper()}"><span class="hp-ic">{ic("card")}</span><span><b>Kreditkarten-Kostenrechner</b><small>Was kostet dich eine Karte bei deiner Nutzung?</small></span></a>'
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
