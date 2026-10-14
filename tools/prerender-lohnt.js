// Rechnet den „Ab wann lohnt sich“-Rechner im Build für den mittleren typischen Fall vor (B12).
// Nutzt public/assets/lohnt.js. Eingabe (stdin): [{key, D, I: {spend, lounge, guests, credits: [i], welcome, vers}}]
const path = require('path');
const L = require(path.join(__dirname, '..', 'public', 'assets', 'lohnt.js'));
const jobs = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const out = {};
for (const j of jobs) out[j.key] = L.result(j.D, Object.assign({}, j.I, { credit: i => j.I.credits.includes(i) }));
process.stdout.write(JSON.stringify(out));
