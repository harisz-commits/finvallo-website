#!/usr/bin/env node
// Live-Checks gegen https://finvallo.com (C26, B20.1–B20.5). Node 18+, nutzt curl, ohne Abhängigkeiten.
// Aufruf: node scripts/live-check.mjs   → druckt eine Tabelle, Exit-Code 1, wenn ein Check fehlschlägt.
import { execFileSync } from 'node:child_process';

const curl = (args) => { try { return execFileSync('curl', ['-sS', '-m', '20', ...args], { encoding: 'utf8' }); } catch (e) { return 'FEHLER ' + (e.stderr || e.message).trim(); } };
const status = (url) => { const [code, loc] = curl(['-o', '/dev/null', '-w', '%{http_code} %{redirect_url}', url]).split(' '); return { code, loc: loc || '' }; };
const headers = (url) => curl(['-sI', '-H', 'Accept-Encoding: br, gzip', url]).toLowerCase();
const asset = () => { const m = curl(['https://finvallo.com/']).match(/assets\/site\.css\?v=[a-z0-9]+/); return m ? 'https://finvallo.com/' + m[0] : null; };
const maxAge = (h) => { const m = [...h.matchAll(/cache-control:[^\n]*max-age=(\d+)/g)].map(x => +x[1]); return m.length ? Math.min(...m) : null; };

const rows = [];
const check = (nr, what, ok, got) => rows.push([nr, what, ok ? 'ok' : 'FEHLER', got]);
let r;
r = status('https://www.finvallo.com/'); check('B20.1', 'www → ohne www (301)', r.code === '301' && r.loc === 'https://finvallo.com/', `${r.code} → ${r.loc}`);
r = status('http://finvallo.com/'); check('B20.2', 'http → https (301)', r.code === '301' && r.loc.startsWith('https://finvallo.com/'), `${r.code} → ${r.loc}`);
r = status('https://finvallo.com/at/kreditkarten'); check('B20.3', 'ohne Schrägstrich → mit (301)', r.code === '301' && r.loc === 'https://finvallo.com/at/kreditkarten/', `${r.code} → ${r.loc}`);
r = status('https://finvallo.com/gibt-es-nicht/'); check('B20.4', 'unbekannte Seite → 404', r.code === '404', r.code);
const h = headers('https://finvallo.com/'), ma = maxAge(h), enc = (h.match(/content-encoding: *(\S+)/) || [])[1];
check('B20.5', 'HTML: Cache höchstens 1 Stunde', ma !== null && ma <= 3600, ma === null ? 'kein Cache-Control' : `max-age=${ma}`);
check('B20.5', 'HTML: gzip oder br', ['gzip', 'br'].includes(enc), enc || 'keine Komprimierung');
const a = asset();
if (a) { const ha = headers(a), mx = maxAge(ha); check('B20.5', 'Assets: Cache mindestens 30 Tage', mx !== null && mx >= 2592000, mx === null ? 'kein Cache-Control' : `max-age=${mx}` + ((ha.match(/cache-control/g) || []).length > 1 ? ' (Header doppelt)' : '')); }
else check('B20.5', 'Assets: Cache mindestens 30 Tage', false, 'CSS-Datei nicht gefunden');

const w = [6, 34, 6]; const pad = (s, n) => String(s).padEnd(n);
console.log(pad('Nr', w[0]) + ' | ' + pad('Check', w[1]) + ' | ' + pad('Status', w[2]) + ' | Ergebnis');
console.log('-'.repeat(w[0]) + '-+-' + '-'.repeat(w[1]) + '-+-' + '-'.repeat(w[2]) + '-+-' + '-'.repeat(30));
for (const x of rows) console.log(pad(x[0], w[0]) + ' | ' + pad(x[1], w[1]) + ' | ' + pad(x[2], w[2]) + ' | ' + x[3]);
process.exit(rows.some(x => x[2] !== 'ok') ? 1 : 0);
