#!/usr/bin/env node
// Live-Checks gegen https://finvallo.com (C26/B20, R8). Node 18+, nutzt curl, ohne Abhängigkeiten.
// Aufruf: node scripts/live-check.mjs   → druckt eine Tabelle, Exit-Code 1, wenn ein Check fehlschlägt.
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');

const curl = (args) => { try { return execFileSync('curl', ['-sS', '-m', '20', ...args], { encoding: 'utf8' }); } catch (e) { return 'FEHLER ' + (e.stderr || e.message).trim(); } };
const status = (url) => { const [code, loc] = curl(['-o', '/dev/null', '-w', '%{http_code} %{redirect_url}', url]).split(' '); return { code, loc: loc || '' }; };
const headers = (url) => curl(['-sI', '-H', 'Accept-Encoding: br, gzip', url]).toLowerCase();
const body = (url) => curl(['-s', url]);
const asset = () => { const m = curl(['https://finvallo.com/']).match(/assets\/site\.css\?v=[a-z0-9]+/); return m ? 'https://finvallo.com/' + m[0] : null; };
const maxAge = (h) => { const m = [...h.matchAll(/cache-control:[^\n]*max-age=(\d+)/g)].map(x => +x[1]); return m.length ? Math.min(...m) : null; };

const rows = [];
const check = (nr, what, ok, got) => rows.push([nr, what, ok ? 'ok' : 'FEHLER', got]);
let r;
r = status('https://www.finvallo.com/'); check('R8.1', 'www → ohne www (301)', r.code === '301' && r.loc === 'https://finvallo.com/', `${r.code} → ${r.loc}`);
r = status('http://finvallo.com/'); check('R8.2', 'http → https (301)', r.code === '301' && r.loc.startsWith('https://finvallo.com/'), `${r.code} → ${r.loc}`);
r = status('https://finvallo.com/at/kreditkarten'); check('R8.3', 'ohne Schrägstrich → mit (301)', r.code === '301' && r.loc === 'https://finvallo.com/at/kreditkarten/', `${r.code} → ${r.loc}`);
r = status('https://finvallo.com/gibt-es-nicht/'); const b404 = body('https://finvallo.com/gibt-es-nicht/');
check('R8.4', 'unbekannte Seite → 404 mit Navigation', r.code === '404' && /<nav/.test(b404) && /href="[^"]*at\/kreditkarten\/"/.test(b404) && /href="[^"]*de\/kreditkarten\/"/.test(b404), r.code + (/<nav/.test(b404) ? ', Navigation da' : ', ohne Navigation'));
const KEY = (readFileSync(join(ROOT, 'server/indexnow.py'), 'utf8').match(/KEY = '([0-9a-f]+)'/) || [])[1];
const kb = KEY ? body(`https://finvallo.com/${KEY}.txt`).trim() : '';
check('R8.5', 'IndexNow-Schlüsseldatei', !!KEY && kb === KEY, KEY ? (kb === KEY ? '200, Inhalt = Schlüssel' : 'fehlt oder falscher Inhalt') : 'kein Schlüssel im Repo');
// Soll-Stand: Startseite auf origin/main (das, was der Server zieht); ohne Git die lokale Datei
let mainHtml; try { execFileSync('git', ['-C', ROOT, 'fetch', '-q', 'origin', 'main']); mainHtml = execFileSync('git', ['-C', ROOT, 'show', 'origin/main:public/index.html'], { encoding: 'utf8' }); } catch { mainHtml = readFileSync(join(ROOT, 'public/index.html'), 'utf8'); }
const home = body('https://finvallo.com/'), want = (mainHtml.match(/<meta name="build" content="([^"]+)"/) || [])[1];
const got = (home.match(/<meta name="build" content="([^"]+)"/) || [])[1];
check('R8.6', 'Startseite = aktueller Build', got && got === want, got === want ? `build ${got}` : `live ${got || 'ohne Marker'}, Repo ${want}: Cache liefert alten Build`);
const h = headers('https://finvallo.com/'), ma = maxAge(h), enc = (h.match(/content-encoding: *(\S+)/) || [])[1];
check('R2', 'HTML: Cache höchstens 10 Minuten', ma !== null && ma <= 600, ma === null ? 'kein Cache-Control' : `max-age=${ma}`);
check('R2', 'HTML: gzip oder br', ['gzip', 'br'].includes(enc), enc || 'keine Komprimierung');
const a = asset();
if (a) { const ha = headers(a), mx = maxAge(ha); check('R2', 'CSS/JS: Cache 1 Jahr (versioniert)', mx !== null && mx >= 31536000, mx === null ? 'kein Cache-Control' : `max-age=${mx}` + ((ha.match(/cache-control/g) || []).length > 1 ? ' (Header doppelt)' : '')); }
else check('R2', 'CSS/JS: Cache 1 Jahr (versioniert)', false, 'CSS-Datei nicht gefunden');

// R8.7/R8.8: JSON-LD-Typen und Affiliate-Satz im Footer
for (const [u, need] of [['/', ['Organization', 'Person', 'WebSite']], ['/at/kreditkarten/tf-bank-mastercard-gold/', ['Product', 'Review', 'FAQPage', 'BreadcrumbList']], ['/at/ratgeber/fremdwaehrung/', ['Article', 'FAQPage', 'BreadcrumbList']]]) {
  const h = body('https://finvallo.com' + u), types = [];
  for (const m of h.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)) {
    try { const walk = x => { if (Array.isArray(x)) x.forEach(walk); else if (x && typeof x === 'object') { if (x['@type']) [].concat(x['@type']).forEach(t => types.includes(t) || types.push(t)); Object.values(x).forEach(walk); } }; walk(JSON.parse(m[1])); } catch { types.push('UNGÜLTIG'); }
  }
  const miss = need.filter(t => !types.includes(t));
  check('R8.7', `JSON-LD ${u}`, !miss.length, types.join(', ') + (miss.length ? ` (fehlt: ${miss.join(', ')})` : ''));
  const f = h.slice(h.lastIndexOf('<footer')).replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ');
  const aff = (f.match(/[^.·©]{0,140}Affiliate[^.·]*\./) || [''])[0].trim();
  check('R8.8', `Affiliate-Satz ${u}`, !!aff, aff || 'nicht gefunden');
}

const w = [6, 34, 6]; const pad = (s, n) => String(s).padEnd(n);
console.log(pad('Nr', w[0]) + ' | ' + pad('Check', w[1]) + ' | ' + pad('Status', w[2]) + ' | Ergebnis');
console.log('-'.repeat(w[0]) + '-+-' + '-'.repeat(w[1]) + '-+-' + '-'.repeat(w[2]) + '-+-' + '-'.repeat(30));
for (const x of rows) console.log(pad(x[0], w[0]) + ' | ' + pad(x[1], w[1]) + ' | ' + pad(x[2], w[2]) + ' | ' + x[3]);
process.exit(rows.some(x => x[2] !== 'ok') ? 1 : 0);
