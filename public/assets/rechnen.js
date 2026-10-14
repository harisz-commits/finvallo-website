/* „Persönlich rechnen“ auf der Kartenliste: Ergebnis pro Jahr je Karte und die Rechnung dazu. */
(function () {
  var box = document.getElementById('rbox'), el = document.getElementById('rdata');
  if (!box || !el) return;
  var D = JSON.parse(el.textContent);
  var q = function (s) { return box.querySelector('[data-r="' + s + '"]'); };
  var num = function (s) { var e = q(s); if (!e) return 0; var v = parseFloat(String(e.value).replace(',', '.')); return isFinite(v) && v > 0 ? v : 0; };
  var lim = function (v) { return v === null || v === undefined ? Infinity : v; };
  var eur = function (v) { return Math.round(v).toLocaleString('de-DE') + ' €'; };
  var eur2 = function (v) { return v.toLocaleString('de-DE', { minimumFractionDigits: v % 1 ? 2 : 0, maximumFractionDigits: 2 }) + ' €'; };
  var pct = function (v) { return v.toLocaleString('de-DE', { maximumFractionDigits: 2 }) + ' %'; };
  var sign = function (v) { return (v >= 0 ? '+' : '−') + eur(Math.abs(v)); };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var items = [].slice.call(document.querySelectorAll('#list article.item'));
  var sort = document.querySelector('#filt [data-sort]');
  if (sort && !sort.querySelector('option[value="net"]')) { var o = document.createElement('option'); o.value = 'net'; o.textContent = 'Nach deinem Ergebnis'; sort.appendChild(o); }

  /* Bargeldkosten für n Abhebungen zu je a € im Jahr. */
  function cash(c, n, a) {
    var k = c.cash;
    if (!n) return { v: 0 };
    if (!k) return { v: 0, t: 'Bargeldkosten unbekannt, nicht gerechnet', unk: 1 };
    switch (k[0]) {
      case 'free': return { v: 0, t: n + ' Abhebungen ohne Automatengebühr' };
      case 'free_interest': var z = (c.effz || 20) / 100 / 12 * a * n; return { v: z, t: n + ' Abhebungen ohne Gebühr, aber etwa ein Monat Zinsen (' + pct(c.effz || 20) + ' im Jahr)' };
      case 'fix': return { v: k[1] * n, t: n + ' × ' + eur2(k[1]) };
      case 'pct': return { v: a * k[1] / 100 * n, t: n + ' × ' + pct(k[1]) + ' von ' + eur(a) };
      case 'pctmin': return { v: Math.max(a * k[1] / 100, k[2]) * n, t: n + ' × ' + pct(k[1]) + ' (mindestens ' + eur2(k[2]) + ') von ' + eur(a) };
      case 'fixpct': return { v: (k[1] + a * k[2] / 100) * n, t: n + ' × (' + eur2(k[1]) + ' + ' + pct(k[2]) + ' von ' + eur(a) + ')' };
      case 'freeN': var extra = Math.max(0, n - k[1] * 12); return { v: extra * k[2], t: extra ? (k[1] + ' pro Monat gratis, ' + extra + ' × ' + eur2(k[2])) : (k[1] + ' Abhebungen pro Monat gratis') };
      case 'no': return { v: 0, t: 'Mit dieser Karte kannst du kein Bargeld abheben', warn: 1 };
    }
    return { v: 0, t: 'Bargeldkosten unbekannt, nicht gerechnet', unk: 1 };
  }

  function calc(c) {
    var S = num('spend') * 12, F = Math.min(num('fxs'), S || Infinity), n = num('cn'), a = num('ca');
    var w = num('wien'), l = num('lounge'), g = num('guests'), lvl = +(q('vers') || { value: 0 }).value;
    var rows = [], plus = 0, minus = 0, inc = false;
    var add = function (t, v, d) { rows.push([t, v, d || '']); if (v >= 0) plus += v; else minus -= v; };
    /* Punkte, Cashback, Meilen */
    if (c.pct) {
      var base = c.fxo ? F : S * (c.anteil || 1), e = base * c.pct / 100, capped = c.cap && e > c.cap;
      if (capped) e = c.cap;
      var d = pct(c.pct) + ' auf ' + eur(base) + (c.fxo ? ' Fremdwährungsumsatz' : c.anteil ? ' (geschätzter Online-Anteil ' + pct(c.anteil * 100) + ')' : ' Umsatz') + (capped ? ', gedeckelt auf ' + eur(c.cap) : '');
      if (c.kosten) {
        if (e > c.kosten) { add('Cashback und Punkte', e, d + (c.ph ? '. ' + c.ph : '')); add('Teilnahme am Bonusprogramm', -c.kosten); }
        else rows.push(['Bonusprogramm', 0, 'Die Teilnahme (' + eur(c.kosten) + ') lohnt sich bei deinem Umsatz nicht, deshalb nicht gerechnet']);
      } else if (e) add('Cashback und Punkte', e, d + (c.ph ? '. ' + c.ph : ''));
    }
    (c.fix || []).forEach(function (x) { add(x[0], x[1]); });
    /* Lounge */
    if (c.lg) {
      var want = c.lg.w ? w : w + l, lv = Math.min(want, lim(c.lg.v));
      if (c.lg.m && S < c.lg.m) { if (want) rows.push(['Lounge', 0, 'Gratis erst ab ' + eur(c.lg.m) + ' Umsatz im Jahr']); lv = 0; }
      if (lv) add('Lounge', lv * D.lounge, lv + ' × ' + eur(D.lounge) + (c.lg.w ? ', nur am Flughafen Wien' : ''));
      var gv = Math.min(g, lv, lim(c.lg.g));
      if (gv) add('Begleitung in der Lounge', gv * D.lounge, gv + ' × ' + eur(D.lounge));
      if (c.lg.w && l) rows.push(['Lounge im Ausland', 0, 'nicht enthalten']);
    }
    /* Guthaben und Abos */
    if (c.cr && q('cr') && q('cr').checked) add('Guthaben der Karte', c.cr);
    if (c.sb && q('sb') && q('sb').checked) add('Partner-Abos', c.sb, 'zum günstigsten regulären Preis');
    /* Reiseversicherung */
    var low = lvl > 0 && c.tier < lvl;
    if (lvl > 0 && !low) add('Reiseversicherung', D.vers[String(lvl)], 'statt eigener Polizze (' + D.tiers[String(lvl)] + ')');
    if (low) rows.push(['Reiseversicherung', 0, c.tier ? 'schwächer als gewünscht' : 'nicht enthalten', 1]);
    /* Kosten */
    if (c.fee === null || c.fee === undefined) return null;
    add('Jahresgebühr', -c.fee);
    if (F) {
      if (c.fx === null || c.fx === undefined) { rows.push(['Fremdwährung', 0, 'Gebühr unbekannt, nicht gerechnet', 1]); inc = true; }
      else if (c.fx) add('Fremdwährungsgebühr', -F * c.fx / 100, pct(c.fx) + ' auf ' + eur(F));
      else rows.push(['Fremdwährungsgebühr', 0, '0 % auf ' + eur(F)]);
    }
    if (n) {
      var cs = cash(c, n, a);
      if (cs.v) add('Bargeld im Ausland', -cs.v, cs.t); else rows.push(['Bargeld im Ausland', 0, cs.t, cs.warn || cs.unk]);
      if (cs.unk || ((c.fx === null || c.fx === undefined) && a)) inc = true;
      if (c.fx && a) add('Fremdwährung beim Abheben', -n * a * c.fx / 100, pct(c.fx) + ' auf ' + eur(n * a));
    }
    return { net: plus - minus, rows: rows, low: low || inc, inc: inc };
  }

  function render(it, r) {
    var b = it.querySelector('[data-res]');
    if (!r) { b.innerHTML = '<p class="note" style="margin:0">Jahresgebühr unbekannt, deshalb kein Ergebnis.</p>'; b.hidden = false; it.dataset.net = ''; it.dataset.low = 1; return; }
    it.dataset.net = Math.round(r.net); it.dataset.low = r.low ? 1 : 0;
    var rows = r.rows.map(function (x) {
      var v = x[1] ? '<b class="' + (x[1] > 0 ? 'good' : 'bad') + '">' + sign(x[1]) + '</b>' : '<b class="mut">' + (x[3] ? '!' : '0 €') + '</b>';
      return '<tr><td>' + esc(x[0]) + (x[2] ? '<br><small class="mut">' + esc(x[2]) + '</small>' : '') + '</td><td class="nw">' + v + '</td></tr>';
    }).join('');
    b.innerHTML = '<details><summary><span>Dein Ergebnis pro Jahr' + (r.inc ? ' <small class="mut">(ohne unbekannte Kosten)</small>' : '') + '</span><b class="' + (r.net >= 0 ? 'good' : 'bad') + '">' + sign(r.net) + '</b><small>Rechnung</small></summary>' +
      '<table><tbody>' + rows + '<tr class="sum"><td>Ergebnis</td><td class="nw"><b class="' + (r.net >= 0 ? 'good' : 'bad') + '">' + sign(r.net) + '</b></td></tr></tbody></table></details>';
    b.hidden = false;
  }

  function run() {
    if (!box.open) { items.forEach(function (it) { var b = it.querySelector('[data-res]'); if (b) b.hidden = true; delete it.dataset.net; }); if (sort && sort.value === 'net') { sort.value = 'rank'; } if (window.finvalloFilter) window.finvalloFilter(); return; }
    items.forEach(function (it) {
      var m = it.querySelector('h3.iname a'); if (!m) return;
      var s = m.getAttribute('href').replace(/\/$/, '').split('/').pop(), c = D.cards[s];
      if (c) render(it, calc(c));
    });
    if (sort && sort.value !== 'net' && !box.dataset.touched) { sort.value = 'net'; box.dataset.touched = 1; }
    if (window.finvalloFilter) window.finvalloFilter();
  }
  box.addEventListener('input', run); box.addEventListener('change', run); box.addEventListener('toggle', run);
  box.hidden = false;
})();
