// Rechnet die Finanzrechner im Build mit ihren Standardwerten vor (B12).
// Nutzt dieselbe Logik wie der Browser (public/assets/calc.js) und denselben Seiten-Code je Rechner.
// Eingabe (stdin): [{key, js, vals: {id: wert}}]; Ausgabe (stdout): {key: {id: {text, html}}}
const path = require('path');
const F = require(path.join(__dirname, '..', 'public', 'assets', 'calc.js'));
const jobs = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const out = {};
for (const job of jobs) {
  const els = {};
  const el = id => els[id] || (els[id] = { value: job.vals[id] !== undefined ? String(job.vals[id]) : '', textContent: '', innerHTML: '' });
  const q = el, v = id => el(id).value, n = id => F.num(v(id)), set = (id, t) => { el(id).textContent = t; };
  new Function('FinCalc', 'q', 'v', 'n', 'set', job.js)(F, q, v, n, set);
  out[job.key] = {};
  for (const [id, e] of Object.entries(els)) if (e.textContent || e.innerHTML) out[job.key][id] = { text: e.textContent, html: e.innerHTML };
}
process.stdout.write(JSON.stringify(out));
