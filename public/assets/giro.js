/* Girokonto-Vergleich: Jahreskosten mit eigenen Zahlen, Filter und Sortierung.
   calc() rechnet genau wie kosten() in tools/girokonto.py (Kontrolle: tools/giro-kontrolle.js). */
(function () {
  function bed(g, ein, alter) {
    if (!g || (g.e === null && g.a === null)) return false;
    var okE = g.e !== null && ein >= g.e, okA = g.a !== null && alter < g.a;
    if (g.v === 'und') return (g.e === null || okE) && (g.a === null || okA);
    return okE || okA;
  }
  function calc(k, ein, alter, abh) {
    var met = bed(k.g, ein, alter), kf = met ? k.g.b * 12 : k.kfj, card = k.dk || 0, cash = 0;
    if (k.cf !== null && k.cf !== undefined && k.cd !== null && k.cd !== undefined) cash = Math.max(0, abh - k.cf) * k.cd * 12;
    var r = function (x) { return Math.round(x * 100) / 100; };
    return { total: r(kf + card + cash), kf: r(kf), card: card, cash: r(cash), met: met,
             fit: !((k.amin !== null && k.amin !== undefined && alter < k.amin) || (k.amax !== null && k.amax !== undefined && alter > k.amax)) };
  }
  if (typeof document === 'undefined') { module.exports = { calc: calc }; return; }

  var fmt = function (v) { return v.toLocaleString('de-DE', { minimumFractionDigits: v % 1 ? 2 : 0, maximumFractionDigits: 2 }) + ' €'; };
  var calcBox = document.getElementById('gcalc'), box = document.getElementById('filt');
  if (!box) return;
  var items = [].slice.call(document.querySelectorAll('article.item[data-k]'));
  items.forEach(function (it, i) { it.dataset.ord = i; it._k = JSON.parse(it.dataset.k); });
  var secs = [].slice.call(document.querySelectorAll('section.gsec'));
  var q = box.querySelector('[data-q]'), art = box.querySelector('[data-art]'), sort = box.querySelector('[data-sort]'),
      count = box.querySelector('[data-count]'), reset = box.querySelector('[data-reset]');
  var chips = [].slice.call(box.querySelectorAll('[data-flag]'));
  var inp = calcBox ? [].slice.call(calcBox.querySelectorAll('[data-in]')) : [];
  var touched = false;
  function val(n) { var e = calcBox && calcBox.querySelector('[data-in="' + n + '"]'); var v = e ? parseFloat(String(e.value).replace(',', '.')) : 0; return isFinite(v) && v > 0 ? v : 0; }
  function recalc() {
    if (!touched) return;
    var ein = val('ein'), alter = val('alter'), abh = val('abh');
    items.forEach(function (it) {
      var c = calc(it._k, ein, alter, abh), out = it.querySelector('[data-out]'), why = it.querySelector('[data-why]');
      it.dataset.cost = c.fit ? c.total : 1e9;
      out.textContent = c.fit ? fmt(c.total) : 'passt nicht';
      out.className = c.fit && c.total === 0 ? 'good' : '';
      var bits = [];
      if (c.kf) bits.push('Kontoführung ' + fmt(c.kf));
      if (c.card) bits.push('Debitkarte ' + fmt(c.card));
      if (c.cash) bits.push('Abhebungen ' + fmt(c.cash));
      why.textContent = !c.fit ? 'Dieses Konto ist nicht für dein Alter.' :
        'Mit deinen Zahlen' + (it._k.g ? (c.met ? ', Bedingung erfüllt' : ', Bedingung nicht erfüllt') : '') + (bits.length ? ': ' + bits.join(', ') : '') + '.';
      it.classList.toggle('dim', !c.fit);
    });
  }
  function apply() {
    recalc();
    var on = chips.filter(function (c) { return c.getAttribute('aria-pressed') === 'true'; }).map(function (c) { return c.dataset.flag; });
    var t = (q.value || '').toLowerCase().trim(), a = art.value, n = 0;
    items.forEach(function (it) {
      var f = ' ' + (it.dataset.f || '') + ' ';
      var ok = on.every(function (x) { return f.indexOf(' ' + x + ' ') >= 0; }) && (!t || it.dataset.q.indexOf(t) >= 0);
      it.hidden = !ok;
    });
    secs.forEach(function (s) {
      var list = s.querySelector('.list'), its = [].slice.call(list.querySelectorAll('article.item'));
      var sv = sort.value;
      its.sort(function (x, y) {
        if (sv === 'cost') return (+x.dataset.cost) - (+y.dataset.cost) || x.dataset.ord - y.dataset.ord;
        if (sv === 'name') return x.dataset.q.localeCompare(y.dataset.q, 'de');
        return x.dataset.ord - y.dataset.ord;
      });
      its.forEach(function (it) { list.appendChild(it); });
      var vis = its.filter(function (it) { return !it.hidden; }).length;
      s.hidden = (a && s.dataset.sec !== a) || !vis;
      if (!s.hidden) n += vis;
    });
    count.textContent = n === 1 ? '1 Konto' : n + ' Konten';
    reset.hidden = !(on.length || t || a || sort.value !== 'rank');
  }
  chips.forEach(function (c) { c.addEventListener('click', function () { c.setAttribute('aria-pressed', c.getAttribute('aria-pressed') === 'true' ? 'false' : 'true'); apply(); }); });
  [q, art, sort].forEach(function (el) { el.addEventListener(el === q ? 'input' : 'change', apply); });
  inp.forEach(function (el) { el.addEventListener('input', function () { touched = true; if (sort.value === 'rank') sort.value = 'cost'; apply(); }); });
  reset.addEventListener('click', function () {
    chips.forEach(function (c) { c.setAttribute('aria-pressed', 'false'); });
    q.value = ''; art.value = ''; sort.value = 'rank'; apply();
  });
  // Sprung auf ein Konto (#gk-…, auch von alten Kontoseiten): Filter lösen, Konditionen aufklappen, hinscrollen
  function zeige() {
    var h = decodeURIComponent(location.hash.slice(1)), it = h.indexOf('gk-') === 0 && document.getElementById(h);
    if (!it) return;
    if (it.hidden || (it.closest('section') || {}).hidden) reset.click();
    var d = it.querySelector('details.more'); if (d) d.open = true;
    it.scrollIntoView({ block: 'start' });
  }
  window.addEventListener('hashchange', zeige);
  box.hidden = false; if (calcBox) calcBox.hidden = false;
  apply(); zeige();
})();
