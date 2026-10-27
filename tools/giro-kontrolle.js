// Vergleicht die Girokonto-Rechnung im Browser (assets/giro.js) mit kosten() in girokonto.py. Eingabe über stdin (aus check.py). Exit 1 bei Abweichung.
const path = require('path');
const G = require(path.join(__dirname, '..', 'public', 'assets', 'giro.js'));
let s = ''; process.stdin.on('data', d => s += d).on('end', () => {
  let bad = 0;
  for (const t of JSON.parse(s)) {
    const r = G.calc(t.k, t.ein, t.alter, t.abh);
    if (Math.abs(r.total - t.want) > 0.005) { bad++; console.log(`Girokonto-Kontrolle FEHLER: ${t.name} (${t.ein} €, ${t.alter} J., ${t.abh} Abh.): JS ${r.total} €, Python ${t.want} €`); }
  }
  process.exit(bad ? 1 : 0);
});
