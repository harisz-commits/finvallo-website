/* „Persönlich rechnen“ auf der Kartenliste: Ergebnis pro Jahr je Karte und die Rechnung dazu. */
(function () {
  var lim = function (v) { return v === null || v === undefined ? Infinity : v; };
  var eur = function (v) { return Math.round(v).toLocaleString('de-DE') + ' €'; };
  var eur2 = function (v) { return v.toLocaleString('de-DE', { minimumFractionDigits: v % 1 ? 2 : 0, maximumFractionDigits: 2 }) + ' €'; };
  var pct = function (v) { return v.toLocaleString('de-DE', { maximumFractionDigits: 2 }) + ' %'; };
  var sign = function (v) { return (v >= 0 ? '+' : '-') + eur(Math.abs(v)); };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };

  /* Bargeldkosten für n Abhebungen zu je a € im Jahr. */
  function cash(c, n, a, aus, td) {
    var k = aus && c.cashA ? c.cashA : c.cash;
    if (!n) return { v: 0 };
    if (!k) return { v: 0, t: 'Bargeldkosten unbekannt, nicht gerechnet', unk: 1 };
    switch (k[0]) {
      case 'free': return { v: 0, t: n + ' Abhebungen ohne Automatengebühr' };
      case 'free_interest': var sz = c.soll || 20, z = sz / 100 * (td || 0) / 365 * a * n; return { v: z, t: n + ' Abhebungen ohne Gebühr, aber Zinsen ab dem Abhebungstag: ' + pct(sz) + ' Sollzins für ' + (td || 0) + ' Tage' };
      case 'fix': return { v: k[1] * n, t: n + ' × ' + eur2(k[1]) };
      case 'pct': return { v: a * k[1] / 100 * n, t: n + ' × ' + pct(k[1]) + ' von ' + eur(a) };
      case 'pctmin': return { v: Math.max(a * k[1] / 100, k[2]) * n, t: n + ' × ' + pct(k[1]) + ' (mindestens ' + eur2(k[2]) + ') von ' + eur(a) };
      case 'fixpct': return { v: (k[1] + a * k[2] / 100) * n, t: n + ' × (' + eur2(k[1]) + ' + ' + pct(k[2]) + ' von ' + eur(a) + ')' };
      case 'freeN': var extra = Math.max(0, n - k[1] * 12); return { v: extra * k[2], t: extra ? ((c.ct ? c.ct + '; ' : k[1] + ' pro Monat gratis, ') + 'gerechnet: ' + extra + ' × ' + eur2(k[2])) : (c.ct || (k[1] + ' Abhebungen pro Monat gratis')) };
      case 'no': return { v: 0, t: 'Mit dieser Karte kannst du kein Bargeld abheben', warn: 1 };
    }
    return { v: 0, t: 'Bargeldkosten unbekannt, nicht gerechnet', unk: 1 };
  }

  /* Bargeld nach Monatsregel (c.cx): Inland gleichmäßig auf 12 Monate, Ausland auf rm Reisemonate verteilt. */
  function feeOf(o, x) { return o ? Math.max((o.fix || 0) + x * (o.pct || 0) / 100, o.min || 0) : 0; }
  function cashSim(c, ni, ai, n, a, rm) {
    var r = c.cx, M = [], i, res = { i: { v: 0, f: 0, cnt: 0, unk: 0 }, a: { v: 0, f: 0, cnt: 0, unk: 0 } };
    for (i = 0; i < 12; i++) M.push([]);
    for (i = 0; i < ni; i++) M[i % 12].push(['i', ai]);
    var R = Math.max(1, Math.min(12, Math.round(rm || 2)));
    if (!(c.cashA)) for (i = 0; i < n; i++) M[i % R].push(['a', a]);
    M.forEach(function (m) {
      var cnt = 0, sum = 0;
      m.forEach(function (w) {
        var amt = w[1], fee = 0, o = res[w[0]]; o.cnt++;
        if (r.min && amt < r.min) { if (r.under) fee = feeOf(r.under, amt); else o.unk = 1; o.v += fee; if (fee) o.f++; return; }
        if (r.steps) { var k = cnt, j; for (j = 0; j < r.steps.length; j++) { var st = r.steps[j]; if (st[0] === null || k < st[0]) { fee = st[1]; break; } k -= st[0]; } }
        else {
          var overN = r.n !== undefined && r.n !== null && cnt >= r.n;
          if (overN) fee = feeOf(r.on, amt);
          if ((!overN || r.both) && r.a !== undefined && r.a !== null) { var ex = Math.max(0, amt - Math.max(0, r.a - sum)); if (ex > 0) fee += feeOf(r.oa, ex); }
        }
        cnt++; sum += amt; o.v += fee; if (fee) o.f++;
      });
    });
    var txt = function (o, lab) { return o.cnt + ' Abhebungen' + lab + (o.f ? ', davon ' + o.f + ' mit Gebühr' : ', alle ohne Gebühr') + (c.ct ? ' (' + c.ct + ')' : '') + (o.unk ? '; Gebühr für kleine Beträge unbekannt' : ''); };
    return { i: { v: res.i.v, t: txt(res.i, ''), unk: res.i.unk }, a: { v: res.a.v, t: txt(res.a, ' in ' + R + ' Reisemonat' + (R > 1 ? 'en' : '')), unk: res.a.unk } };
  }

  /* Ergebnis einer Karte; I liefert die Eingaben (num: Zahl, on: Haken gesetzt), D die gemeinsamen Werte. */
  function calc(c, I, D) {
    var num = I.num, S = num('spend') * 12, F = Math.min(num('fxs'), S || Infinity), n = num('cn'), ni = num('cin'), a = num('ca'), ai = num('cia'), y1 = I.on('wel');
    var w = num('wien'), l = num('lounge'), g = num('guests'), lvl = num('vers'), rm = num('rm') || 2, td = I.has && I.has('td') ? num('td') : 30;
    var sim = c.cx && (ni || n) ? cashSim(c, ni, ai, n, a, rm) : null;
    var rows = [], plus = 0, minus = 0, inc = false;
    var add = function (t, v, d) { rows.push([t, v, d || '']); if (v >= 0) plus += v; else minus -= v; };
    /* Punkte, Cashback, Meilen */
    if (c.pct) {
      var own = I.has && I.has('pv') && !(I.raw && I.raw('pv') === 'd'), pvm = !c.pk ? 1 : own ? num('pv') : (c.pv || 0.5), base = c.fxo ? F : S * (c.anteil || 1), e = base * c.pct / 100 * pvm, capped = c.cap && e > c.cap * pvm;
      if (capped) e = c.cap * pvm;
      var d = pct(c.pct) + ' auf ' + eur(base) + (c.fxo ? ' Fremdwährungsumsatz' : c.anteil ? ' (geschätzter Online-Anteil ' + pct(c.anteil * 100) + ')' : ' Umsatz') + (capped ? ', gedeckelt auf ' + eur(c.cap * pvm) : '') + (c.pk ? ', bei ' + pct(pvm).replace(' %', '') + ' Cent pro Punkt ' + (!own && c.pv ? '(Wert laut Anbieter)' : '(Annahme)') : '');
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
    if (c.cr && I.on('cr')) add('Guthaben der Karte', c.cr, (c.crn || '') + (c.crx ? '; weitere ' + eur(c.crx) + ' Gourmet-Guthaben im Ausland möglich, nicht gerechnet' : ''));
    if (c.sb && I.on('sb')) add('Partner-Abos', c.sb * 0.6, '60 % von ' + eur(c.sb) + ', zum günstigsten regulären Preis');
    else if (c.sbl && I.on('sbl')) add('Partner-Abos', c.sbl, c.sbn + ', zum regulären Preis');
    if (c.esim && I.on('esim')) add('eSIM-Daten', Math.min(rm, 12) * c.esim[0] * c.esim[1], Math.min(rm, 12) + ' Reisemonate × ' + c.esim[0] + ' GB × ' + eur2(c.esim[1]) + ', nur außerhalb der EU sinnvoll');
    /* Reiseversicherung */
    var low = lvl > 0 && c.tier < lvl;
    if (lvl > 0 && !low) add('Reiseversicherung', D.vers[String(lvl)], 'statt eigener ' + (D.polizze || 'Polizze') + ' (' + D.tiers[String(lvl)] + ')');
    if (low) rows.push(['Reiseversicherung', 0, c.tier ? 'schwächer als gewünscht' : 'nicht enthalten', 1]);
    /* Kosten */
    if (c.wel && y1) add('Willkommensbonus', c.wel[0], c.wel[1]);
    if (c.fee === null || c.fee === undefined) return null;
    var fee = y1 && c.fee1 !== undefined ? c.fee1 : c.fee;
    add(y1 && c.fee1 !== undefined ? 'Jahresgebühr im 1. Jahr' : 'Jahresgebühr', -fee, y1 && c.fee1 !== undefined ? 'danach ' + eur2(c.fee) + ' im Jahr' : (c.fm ? 'bei Jahreszahlung, monatlich bezahlt ' + eur2(c.fm) + ' im Jahr' : ''));
    if (F) {
      if (c.fx === null || c.fx === undefined) { rows.push(['Fremdwährung', 0, 'Gebühr unbekannt, nicht gerechnet', 1]); inc = true; }
      else if (c.fx) add('Fremdwährungsgebühr', -F * c.fx / 100, pct(c.fx) + ' auf ' + eur(F));
      else rows.push(['Fremdwährungsgebühr', 0, '0 % auf ' + eur(F)]);
    }
    if (ni) {
      var ci = sim ? sim.i : cash(c, ni, ai, false, td);
      if (ci.v) add('Bargeld im Inland', -ci.v, ci.t); else rows.push(['Bargeld im Inland', 0, ci.t, ci.warn || ci.unk]);
      if (ci.unk) inc = true;
    }
    if (n) {
      var cs = sim && !c.cashA ? sim.a : cash(c, n, a, true, td);
      if (cs.v) add('Bargeld im Ausland', -cs.v, cs.t); else rows.push(['Bargeld im Ausland', 0, cs.t, cs.warn || cs.unk]);
      if (cs.unk || ((c.fx === null || c.fx === undefined) && a)) inc = true;
      var cf = c.cfx || c.fx;
      if (cf && a) add('Fremdwährung beim Abheben', -n * a * cf / 100, pct(cf) + ' auf ' + eur(n * a));
    }
    return { net: plus - minus, rows: rows, low: low || inc, inc: inc };
  }

  /* HTML der Rechnung unter einer Karte */
  function resHTML(r) {
    if (!r) return '<p class="note" style="margin:0">Jahresgebühr unbekannt, deshalb kein Ergebnis.</p>';
    var rows = r.rows.map(function (x) {
      var v = x[1] ? '<b class="' + (x[1] > 0 ? 'good' : 'bad') + '">' + sign(x[1]) + '</b>' : '<b class="mut">' + (x[3] ? '!' : '0 €') + '</b>';
      return '<tr><td>' + esc(x[0]) + (x[2] ? '<br><small class="mut">' + esc(x[2]) + '</small>' : '') + '</td><td class="nw">' + v + '</td></tr>';
    }).join('');
    return '<details><summary><span>Dein Ergebnis pro Jahr' + (r.inc ? ' <small class="mut">(ohne unbekannte Kosten)</small>' : '') + '</span><b class="' + (r.net >= 0 ? 'good' : 'bad') + '">' + sign(r.net) + '</b><small>Rechnung</small></summary>' +
      '<table><tbody>' + rows + '<tr class="sum"><td>Ergebnis</td><td class="nw"><b class="' + (r.net >= 0 ? 'good' : 'bad') + '">' + sign(r.net) + '</b></td></tr></tbody></table></details>';
  }
  /* Im Build (Node) nur die Rechenlogik bereitstellen: tools/rechnen.py rechnet damit die Standardwerte vor. */
  if (typeof document === 'undefined') { module.exports = { calc: calc, resHTML: resHTML }; return; }

  var box = document.getElementById('rbox'), el = document.getElementById('rdata');
  if (!box || !el) return;
  var D = JSON.parse(el.textContent);
  var q = function (s) { return box.querySelector('[data-r="' + s + '"]'); };
  var num = function (s) { var e = q(s); if (!e) return 0; var v = parseFloat(String(e.value).replace(',', '.')); return isFinite(v) && v > 0 ? v : 0; };
  var PAGE = !!box.dataset.page;
  if (PAGE && /[?&]land=DE/i.test(location.search) && /\/at\//.test(location.pathname)) { location.replace(location.pathname.replace('/at/', '/de/')); return; }
  var items = [].slice.call(document.querySelectorAll('.list article.item, #rlist article.item'));
  var sort = document.querySelector('#filt [data-sort]');
  if (sort && !sort.querySelector('option[value="net"]')) { var o = document.createElement('option'); o.value = 'net'; o.textContent = 'Nach deinem Ergebnis'; sort.appendChild(o); }


  var I = { num: num, on: function (k) { var e = q(k); return !!(e && e.checked); }, has: function (k) { return !!q(k); }, raw: function (k) { var e = q(k); return e ? String(e.value) : ''; } };
  function render(it, r) {
    var b = it.querySelector('[data-res]');
    it._r = r;
    b.innerHTML = resHTML(r); b.hidden = false;
    if (!r) { it.dataset.net = ''; it.dataset.low = 1; return; }
    it.dataset.net = Math.round(r.net); it.dataset.low = r.low ? 1 : 0;
  }

  /* Kreditkarten-Rechner: Filter, Rangliste, Vergleich */
  var list = document.getElementById('rlist');
  function fv(k) { var e = box.querySelector('[data-f="' + k + '"]'); return e ? e.value : ''; }
  function pageList() {
    var typ = fv('typ'), netz = fv('netz'), fmax = fv('fee'), n = 0;
    var nv = function (it) { var v = parseFloat(it.dataset.net); return isFinite(v) ? v : -1e9; };
    var arr = items.slice().sort(function (x, y) { return ((+x.dataset.low || 0) - (+y.dataset.low || 0)) || (nv(y) - nv(x)); });
    arr.forEach(function (it) {
      var ok = (!typ || it.dataset.typ === typ) && (!netz || (it.dataset.netz || '').indexOf(netz) >= 0) && (fmax === '' || +it.dataset.fee <= +fmax);
      it.hidden = !ok; if (ok) { n++; it.querySelector('[data-rank]').textContent = n; } list.appendChild(it);
    });
    document.querySelector('[data-rcount]').textContent = n === 1 ? '1 Karte' : n + ' Karten';
  }
  var bar = document.getElementById('rcmpbar'), cmp = document.getElementById('rcmp');
  function picked() { return items.filter(function (it) { var c = it.querySelector('[data-cmp]'); return c && c.checked; }); }
  function cmpBar() {
    if (!bar) return;
    var p = picked(); bar.hidden = !p.length;
    bar.querySelector('[data-cmpn]').textContent = p.length + (p.length === 1 ? ' Karte' : ' Karten') + ' ausgewählt' + (p.length < 2 ? ' (wähle mindestens 2)' : '');
    bar.querySelector('[data-cmpgo]').disabled = p.length < 2;
    items.forEach(function (it) { var c = it.querySelector('[data-cmp]'); if (c) c.disabled = !c.checked && p.length >= 4; });
    if (!cmp.hidden) cmpShow();
  }
  function cmpShow() {
    var p = picked().filter(function (it) { return it._r; });
    if (p.length < 2) { cmp.hidden = true; return; }
    var labels = [];
    p.forEach(function (it) { it._r.rows.forEach(function (x) { if (labels.indexOf(x[0]) < 0) labels.push(x[0]); }); });
    var cell = function (v) { return v ? '<b class="' + (v > 0 ? 'good' : 'bad') + '">' + sign(v) + '</b>' : '<span class="mut">-</span>'; };
    var h = '<div class="rcmphead"><h2 style="margin:0">Vergleich</h2><button type="button" class="lnk" data-cmpx>Schließen</button></div><div class="tbl"><table><thead><tr><th></th>' +
      p.map(function (it) { return '<th>' + esc(it.querySelector('h3').textContent) + '</th>'; }).join('') + '</tr></thead><tbody>' +
      labels.map(function (l) { return '<tr><td>' + esc(l) + '</td>' + p.map(function (it) { var x = it._r.rows.filter(function (r) { return r[0] === l; })[0]; return '<td class="nw">' + (x ? (x[1] ? cell(x[1]) : '<span class="mut">' + (x[3] ? '!' : '0 €') + '</span>') : '<span class="mut">-</span>') + '</td>'; }).join('') + '</tr>'; }).join('') +
      '<tr class="sum"><td>Ergebnis pro Jahr</td>' + p.map(function (it) { return '<td class="nw">' + cell(it._r.net) + '</td>'; }).join('') + '</tr></tbody></table></div>';
    cmp.innerHTML = h; cmp.hidden = false;
    cmp.querySelector('[data-cmpx]').onclick = function () { cmp.hidden = true; };
  }
  if (bar) {
    items.forEach(function (it) { var c = it.querySelector('[data-cmp]'); if (c) c.addEventListener('change', cmpBar); });
    bar.querySelector('[data-cmpgo]').addEventListener('click', function () { cmpShow(); cmp.scrollIntoView({ behavior: 'smooth', block: 'start' }); });
    bar.querySelector('[data-cmpclr]').addEventListener('click', function () { items.forEach(function (it) { var c = it.querySelector('[data-cmp]'); if (c) c.checked = false; }); cmp.hidden = true; cmpBar(); });
  }

  var last = '';
  function state() { return [].map.call(box.querySelectorAll('input,select'), function (e) { return e.type === 'checkbox' ? e.checked : e.value; }).join('|') + (box.open ? 'o' : ''); }
  function run() {
    var st = state(); if (st === last) return; last = st;
    if (PAGE) { items.forEach(function (it) { var m = it.querySelector('h3.iname a'), c = D.cards[m.getAttribute('href').replace(/\/$/, '').split('/').pop()]; if (c) render(it, calc(c, I, D)); }); pageList(); if (cmp && !cmp.hidden) cmpShow(); return; }
    if (!box.open) { items.forEach(function (it) { var b = it.querySelector('[data-res]'); if (b) b.hidden = true; delete it.dataset.net; }); if (sort && sort.value === 'net') { sort.value = 'rank'; } if (window.finvalloFilter) window.finvalloFilter(); return; }
    items.forEach(function (it) {
      var m = it.querySelector('h3.iname a'); if (!m) return;
      var s = m.getAttribute('href').replace(/\/$/, '').split('/').pop(), c = D.cards[s];
      if (c) render(it, calc(c, I, D));
    });
    if (sort && sort.value !== 'net' && !box.dataset.touched) { sort.value = 'net'; box.dataset.touched = 1; }
    if (window.finvalloFilter) window.finvalloFilter();
  }
  box.addEventListener('input', run); box.addEventListener('change', run); box.addEventListener('toggle', run);
  box.hidden = false;
  if (PAGE) run();
})();
