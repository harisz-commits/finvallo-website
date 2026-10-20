// Rechnet den Kreditkarten-Rechner im Build mit den Standardwerten vor (B12).
// Nutzt die Rechenlogik aus public/assets/rechnen.js. Eingabe (stdin): {D, vals: {key: zahl}, on: [keys]}
// Ausgabe (stdout): {slug: {net, low, html}}
const path = require('path');
const R = require(path.join(__dirname, '..', 'public', 'assets', 'rechnen.js'));
const job = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const I = { num: k => { const v = +job.vals[k]; return isFinite(v) && v > 0 ? v : 0; }, on: k => (job.on || []).includes(k), has: k => k in job.vals };
const out = {};
for (const [slug, c] of Object.entries(job.D.cards)) {
  const r = R.calc(c, I, job.D);
  out[slug] = { net: r ? Math.round(r.net) : null, low: !r || r.low ? 1 : 0, html: R.resHTML(r) };
}
process.stdout.write(JSON.stringify(out));
