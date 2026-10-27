// Vergleicht die Festgeld-Rechnung im Browser (assets/festgeld.js) mit ertrag() in festgeld.py. Eingabe über stdin (aus check.py). Exit 1 bei Abweichung.
const path = require('path');
const F = require(path.join(__dirname, '..', 'public', 'assets', 'festgeld.js'));
let s = ''; process.stdin.on('data', d => s += d).on('end', () => {
  let bad = 0;
  for (const t of JSON.parse(s)) {
    const r = F.calc(t.k, t.b, t.m), w = t.want;
    const same = r.fit === w.fit && (r.why || null) === (w.why || null) && (r.zins ?? null) === (w.zins ?? null) && Math.abs((r.ertrag || 0) - (w.ertrag || 0)) <= 0.005;
    if (!same) { bad++; console.log(`Festgeld-Kontrolle FEHLER: ${t.name} (${t.b} €, ${t.m} Monate): JS ${JSON.stringify(r)}, Python ${JSON.stringify(w)}`); }
  }
  process.exit(bad ? 1 : 0);
});
