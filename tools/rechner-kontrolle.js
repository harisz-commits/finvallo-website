// Kontrollbeispiele für die Bargeldrechnung im Kartenrechner (läuft in check.py). Exit 1 bei Abweichung.
const path = require('path');
const R = require(path.join(__dirname, '..', 'public', 'assets', 'rechnen.js'));
const D = { lounge: 30, vers: {}, tiers: {}, polizze: 'Polizze' };
const base = { fee: 0, fx: 0, tier: 0 };
const run = (c, vals) => { const I = { num: k => { const v = +(vals[k] || 0); return v > 0 ? v : 0; }, on: () => false, has: k => k in vals }; return -R.calc(c, I, D).rows.filter(x => /^(Bargeld|Cashback und Punkte)/.test(x[0])).reduce((s, x) => s + x[1], 0); };
const REV = { n: 5, a: 200, on: { pct: 2, min: 1 }, oa: { pct: 2, min: 1 } };
const F = [
  ['Trade Republic: 12 × 50 € = 12 €', { ...base, cash: ['fix', 0], cx: { min: 100, under: { fix: 1 } } }, { cin: 12, cia: 50 }, 12],
  ['Trade Republic: 12 × 100 € = 0 €', { ...base, cash: ['fix', 0], cx: { min: 100, under: { fix: 1 } } }, { cin: 12, cia: 100 }, 0],
  ['Revolut Standard: 12 × 500 € = 72 €', { ...base, cash: ['freeN', 1, 4], cx: REV }, { cin: 12, cia: 500 }, 72],
  ['Revolut Standard: 10 × 100 € in einem Reisemonat = 16 €', { ...base, cash: ['freeN', 1, 4], cx: REV }, { cn: 10, ca: 100, rm: 1 }, 16],
  ['N26 (2 gratis pro Monat): 30 × 100 € in 2 Reisemonaten = 52 €', { ...base, cash: ['freeN', 2, 2], cx: { n: 2, on: { fix: 2 } } }, { cn: 30, ca: 100, rm: 2 }, 52],
  ['TF Bank: 4 × 200 €, 22,6 % Sollzins, 30 Tage = 14,86 €', { ...base, cash: ['free_interest'], soll: 22.6 }, { cin: 4, cia: 200, td: 30 }, 14.86],
  ['Punkte 12.000 € Umsatz, 1 % Rate, Standard 0,5 Cent = 60 €', { ...base, pct: 1, pk: 1 }, { spend: 1000 }, -60],
  ['Punkte mit festem Anbieterwert 1 Cent (PAYBACK), Standard = 120 €', { ...base, pct: 1, pk: 1, pv: 1 }, { spend: 1000 }, -120],
  ['Punkte, 1 Cent gewählt = 120 €', { ...base, pct: 1, pk: 1 }, { spend: 1000, pv: 1 }, -120],
  ['Punkte 12.000 € Umsatz, 0,5 Cent = 60 €', { ...base, pct: 1, pk: 1 }, { spend: 1000, pv: 0.5 }, -60],
  ['Punkte nicht als Geld bewertet = 0 €', { ...base, pct: 1, pk: 1 }, { spend: 1000, pv: 0 }, 0],
  ['Echtes Cashback bleibt bei 0,5 Cent gleich = 120 €', { ...base, pct: 1 }, { spend: 1000, pv: 0.5 }, -120],
];
let bad = 0;
for (const [t, c, v, want] of F) { const got = Math.round(run(c, v) * 100) / 100; if (Math.abs(got - want) > 0.01) { bad++; console.log(`Rechner-Kontrolle FEHLER: ${t}, gerechnet ${got} €`); } }
process.exit(bad ? 1 : 0);
