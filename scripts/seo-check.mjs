#!/usr/bin/env node
// SEO-Prüfung der gebauten Website (C26). Node 18+, ohne Abhängigkeiten.
// Aufruf nach jedem Build: node scripts/seo-check.mjs   → Exit-Code 1 bei Fehlern.
// Tests: A6 Kartenanzahl, A7 Meta Descriptions, A8 interne Links, B10.4 JSON-LD, B11.5 hreflang,
// B14.4 ein Prüfdatum je Seite, B15.1 zusammengeklebte Wörter, B15.3 doppelte Vor-/Nachteile,
// B17.3 Links außerhalb von <main>, B18.4 wortgleiche FAQ-Antworten, B20.8 Sitemap ohne noindex/301-Quellen.
import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const PUB = join(ROOT, 'public') + '/';
const GLUE_OK = ['1822direkt', 'ChatGPT', 'NordVPN', 'eSIM', 'PayPal', 'MasterCard', 'iPhone', 'iOS', 'myFlex', 'WiFi', 'BahnCard', 'eBay'];
const LATER = new Set(['assets/haris.jpg']); // Foto wird nachgeliefert
const ALLOWED = JSON.parse(readFileSync(join(ROOT, 'tools/daten/zaehler.json'), 'utf8'));
const unesc = s => s.replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#x27;|&#39;/g, "'");
const err = [];

function walk(d, out = []) {
  for (const f of readdirSync(d)) { const p = join(d, f); if (statSync(p).isDirectory()) walk(p, out); else if (f === 'index.html') out.push(p); }
  return out;
}
const pages = walk(PUB).concat(existsSync(PUB + '404.html') ? [PUB + '404.html'] : []);
const key = rel => rel.endsWith('index.html') ? rel.slice(0, -10) : rel;
const HREF = {}, FAQ = new Map(), NOINDEX = new Set(), DESC = [];

for (const f of pages) {
  const rel = f.slice(PUB.length), s = readFileSync(f, 'utf8'), body = s.slice(s.indexOf('<body'));
  const base = 'https://finvallo.com/' + key(rel), me = rel.split('/')[0];
  if (/<meta name="robots" content="noindex/.test(s)) NOINDEX.add(key(rel));
  // A8: interne Links (keine 404, Land der Seite, Umschalter mit hreflang)
  for (const m of body.matchAll(/<a\b[^>]*href="([^"#?]*)[^"]*"[^>]*>/g)) {
    const h = m[1]; if (!h || /^(mailto:|tel:|javascript)/.test(h)) continue;
    let u; try { u = new URL(h, base); } catch { err.push(`${rel}: kaputter Link ${h}`); continue; }
    if (u.host !== 'finvallo.com') continue;
    const p = u.pathname.replace(/^\//, ''), t = p === '' || p.endsWith('/') ? p + 'index.html' : p;
    if (!existsSync(PUB + t) && rel !== '404.html' && !LATER.has(t)) err.push(`A8 ${rel}: Link ins Leere ${h}`);
    const to = p.split('/')[0];
    if (['at', 'de'].includes(me) && ['at', 'de'].includes(to) && to !== me && !/hreflang|lang-switch/.test(m[0])) err.push(`A8 ${rel}: Link ins andere Land ohne hreflang ${h}`);
  }
  for (const m of body.matchAll(/src="([^"#?]*)/g)) {
    let u; try { u = new URL(m[1], base); } catch { continue; }
    const p = u.pathname.replace(/^\//, '');
    if (u.host === 'finvallo.com' && !existsSync(PUB + p) && !LATER.has(p)) err.push(`A8 ${rel}: Datei fehlt ${m[1]}`);
  }
  // B10.4: JSON-LD gültig, @context vorhanden; FAQ-Antworten sammeln (B18.4)
  for (const m of s.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)) {
    let j; try { j = JSON.parse(m[1]); } catch (e) { err.push(`B10.4 ${rel}: JSON-LD ungültig (${e.message})`); continue; }
    if (!j['@context']) err.push(`B10.4 ${rel}: JSON-LD ohne @context`);
    for (const n of (j['@graph'] || [j])) if (n['@type'] === 'FAQPage') for (const q of n.mainEntity || []) {
      const a = (q.acceptedAnswer || {}).text || ''; if (a.length > 120) { if (!FAQ.has(a)) FAQ.set(a, new Set()); FAQ.get(a).add(key(rel)); }
    }
  }
  // B11.5: hreflang sammeln
  const alts = {}; for (const m of s.matchAll(/<link rel="alternate" hreflang="(de-AT|de-DE)" href="https:\/\/finvallo\.com\/([^"]*)">/g)) alts[m[1]] = m[2];
  HREF[key(rel)] = alts;
  for (const a of Object.values(alts)) if (!existsSync(PUB + a + 'index.html')) err.push(`B11.5 ${rel}: hreflang-Ziel fehlt ${a}`);
  // B15.1: zusammenklebende Wörter im sichtbaren Text
  let tx = body.replace(/<(script|style|svg)\b[\s\S]*?<\/\1>/g, '').replace(/<\/?(?:p|div|li|ul|ol|h[1-6]|tr|td|th|table|section|article|aside|nav|header|footer|main|br|summary|details|label|option|select|dt|dd|button|form|small|b)\b[^>]*>/g, '\n');
  tx = unesc(tx.replace(/<[^>]+>/g, '')).replace(/https?:\/\/\S+|\b[\w.-]+\.(?:com|net|de|at)\b/g, '');
  for (const m of tx.matchAll(/[a-zäöüß][A-ZÄÖÜ]{2,}|\d(?!\d)[A-Za-zÄÖÜäöü]{2,}/g)) {
    const ctx = tx.slice(Math.max(0, m.index - 8), m.index + m[0].length + 8);
    if (!GLUE_OK.some(w => ctx.includes(w))) { err.push(`B15.1 ${rel}: zusammengeklebt „${tx.slice(Math.max(0, m.index - 10), m.index + m[0].length + 10).trim()}“`); break; }
  }
  // B15.3: doppelte Vor-/Nachteile auf Kartenseiten (normalisiert)
  for (const m of s.matchAll(/<ul class="checks(?: neg)?">([\s\S]*?)<\/ul>/g)) {
    const seen = new Set();
    for (const li of m[1].matchAll(/<li>([\s\S]*?)<\/li>/g)) {
      const n = unesc(li[1].replace(/<[^>]+>/g, '')).toLowerCase().replace(/[^\p{L}\p{N} ]/gu, '').replace(/\s+/g, ' ').trim();
      if (seen.has(n)) err.push(`B15.3 ${rel}: doppelter Punkt „${n.slice(0, 60)}“`); seen.add(n);
    }
  }
  // B17.3: höchstens 35 Links außerhalb von <main>
  const outside = body.replace(/<main\b[\s\S]*?<\/main>/g, ''); const nl = (outside.match(/<a\s/g) || []).length;
  if (nl > 35) err.push(`B17.3 ${rel}: ${nl} Links außerhalb von <main>`);
  // B14.4: höchstens ein Prüf-/Stand-Datum
  const bt = body.replace(/<script[\s\S]*?<\/script>|<p class="src">[\s\S]*?<\/p>/g, '').replace(/<[^>]+>/g, ' ');
  const ds = new Set([...bt.matchAll(/(?:Stand:|[Gg]eprüft am|geprüft bis|Aktualisiert am)\s*(\d{2}\.\d{2}\.\d{4})/g)].map(m => m[1]));
  if (ds.size > 1) err.push(`B14.4 ${rel}: mehrere Prüfdaten ${[...ds].join(', ')}`);
  // A7: Meta Description
  const d = s.match(/<meta name="description" content="(.*?)"/);
  if (!d && rel !== '404.html') err.push(`A7 ${rel}: keine Beschreibung`);
  if (d) { const t = unesc(d[1]); if (t.length > 160) err.push(`A7 ${rel}: Beschreibung zu lang (${t.length})`); if (t.length < 70) err.push(`A7 ${rel}: Beschreibung zu kurz (${t.length})`); if (/(…|\.\.\.)\s*$/.test(t)) err.push(`A7 ${rel}: Beschreibung endet mit …`); }
  // A6: Kartenanzahlen nur aus card_count() bzw. Bestenlisten-Zählern
  if (ALLOWED[me]) {
    const t = s.replace(/<script[\s\S]*?<\/script>/g, '');
    for (const m of t.matchAll(/(?<![\w.,])(\d{2,3}) (?:bewerteten |bewertete )?(?:Privatkarten|Kreditkarten|Karten)\b/g)) {
      const n = +m[1];
      if (n >= 20 && !ALLOWED[me].includes(n) && !t.slice(Math.max(0, m.index - 8), m.index).endsWith('Trading ')) err.push(`A6 ${rel}: Kartenanzahl „${m[0]}“ stammt nicht aus card_count()`);
    }
  }
}
// B11.5: symmetrisch
for (const [r, alts] of Object.entries(HREF)) for (const t of Object.values(alts)) {
  const o = HREF[t] || {}; if (JSON.stringify(Object.entries(o).sort()) !== JSON.stringify(Object.entries(alts).sort())) err.push(`B11.5 hreflang nicht symmetrisch: ${r} ↔ ${t}`);
}
// B18.4: wortgleiche FAQ-Antworten nur auf Länderpaaren (gegenseitiges hreflang) und / als Kopie von /at/
for (const [a, ps] of FAQ) {
  if (ps.size < 2) continue;
  const groups = new Set([...ps].map(p => Object.values(HREF[p] || {}).sort().join('|')));
  const g = [...groups][0].split('|');
  const home = new Set(['', 'at/', ...Object.values(HREF['at/'] || {})]);
  if ((groups.size === 1 && [...ps].every(p => g.includes(p))) || [...ps].every(p => home.has(p))) continue;
  err.push(`B18.4 FAQ-Antwort auf ${ps.size} Seiten: „${a.slice(0, 70)}…“ (${[...ps].sort().slice(0, 3).join(', ')})`);
}
// B20.8: Sitemap ohne noindex-Seiten und ohne 301-Quellen
const sm = [...readFileSync(PUB + 'sitemap.xml', 'utf8').matchAll(/<loc>https:\/\/finvallo\.com\/([^<]*)<\/loc>/g)].map(m => m[1]);
const redir = new Set([...readFileSync(join(ROOT, 'server/redirects.conf'), 'utf8').matchAll(/location = \/(\S*) \{/g)].map(m => m[1]));
for (const u of sm) {
  if (!existsSync(PUB + (u === '' || u.endsWith('/') ? u + 'index.html' : u))) err.push(`B20.8 Sitemap: Seite fehlt ${u}`);
  if (NOINDEX.has(u)) err.push(`B20.8 Sitemap enthält noindex-Seite ${u}`);
  if (redir.has(u)) err.push(`B20.8 Sitemap enthält Weiterleitung ${u}`);
}
if (sm.length !== new Set(sm).size) err.push('B20.8 Sitemap: doppelte Einträge');

console.log(`${pages.length} Seiten, ${sm.length} Sitemap-Einträge geprüft`);
if (err.length) { console.log('FEHLER:\n' + err.slice(0, 100).join('\n') + (err.length > 100 ? `\n… und ${err.length - 100} weitere` : '')); process.exit(1); }
console.log('alles in Ordnung');
