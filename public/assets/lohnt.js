/* „Ab wann lohnt sich die Karte?“: rechnet die genutzten Vorteile gegen die Jahresgebühr.
   [data-lohnt] = Rechner auf der Kartenseite, [data-lohnt-hub] = Filter auf der Übersicht der Top-Karten. */
(function () {
  var eur = function (v) { return Math.round(v).toLocaleString('de-DE') + ' €'; };
  var sign = function (v) { return (v >= 0 ? '+' : '−') + eur(Math.abs(v)); };
  function num(el) { if (!el) return 0; var v = parseFloat(String(el.value).replace(',', '.')); return isFinite(v) && v > 0 ? v : 0; }
  var lim = function (v) { return v === null ? Infinity : v; };

  /* Ergebnis auf der Kartenseite; I: spend, lounge, guests (Zahlen), credit(i), welcome, vers (Haken). */
  function result(D, I) {
    var spend = I.spend;
    var lv = D.minsp && spend * 12 < D.minsp ? 0 : Math.min(I.lounge, lim(D.visits));
    var gv = Math.min(I.guests, lv, lim(D.guests));
    var pts = spend * 12 / 100 * D.pp100; if (D.pmax) pts = Math.min(pts, D.pmax);
    var v = (lv + gv) * D.lounge + pts;
    D.credits.forEach(function (c, i) { if (I.credit(i)) v += c.v; });
    if (I.welcome) v += D.welcome;
    if (I.vers) v += D.vers;
    var net = v - D.fee, txt;
    if (net >= 0) txt = 'Bei dieser Nutzung holst du die Jahresgebühr wieder herein und hast ' + eur(net) + ' im Jahr mehr, als die Karte kostet.';
    else {
      var more = Math.ceil(-net / D.lounge), free = lim(D.visits) - lv;
      txt = 'Bei dieser Nutzung kostet dich die Karte ' + eur(-net) + ' im Jahr mehr, als sie bringt.' +
        (D.minsp && spend * 12 < D.minsp ? ' Die Lounge-Besuche sind erst ab ' + eur(D.minsp) + ' Umsatz im Jahr kostenlos.' : D.visits !== 0 && more <= free ? ' Mit etwa ' + more + ' Lounge-Besuchen mehr wäre sie im Plus.' : ' Eine günstigere Karte passt besser zu dir.');
    }
    return { val: eur(v), net: sign(net), good: net >= 0, txt: txt };
  }
  /* Im Build (Node): nur die Rechnung bereitstellen, tools/lohnt.py rechnet damit den mittleren Fall vor. */
  if (typeof document === 'undefined') { module.exports = { result: result }; return; }

  var box = document.querySelector('[data-lohnt]');
  if (box) (function () {
    var D = JSON.parse(box.getAttribute('data-lohnt'));
    var q = function (s) { return box.querySelector(s); };
    function calc() {
      var r = result(D, { spend: num(q('[data-in="spend"]')), lounge: num(q('[data-in="lounge"]')), guests: num(q('[data-in="guests"]')),
        credit: function (i) { var c = q('[data-credit="' + i + '"]'); return !!(c && c.checked); },
        welcome: !!(q('[data-welcome]') && q('[data-welcome]').checked), vers: !!(q('[data-vers]') && q('[data-vers]').checked) });
      q('[data-out="val"]').textContent = r.val;
      var n = q('[data-out="net"]'); n.textContent = r.net; n.className = r.good ? 'good' : 'bad';
      q('[data-out="txt"]').textContent = r.txt;
    }
    box.addEventListener('input', calc); box.addEventListener('change', calc);
    box.hidden = false; calc();
  })();

  var hub = document.querySelector('[data-lohnt-hub]');
  if (hub) (function () {
    var D = JSON.parse(hub.getAttribute('data-lohnt-hub'));
    var q = function (s) { return hub.querySelector(s); };
    function calc() {
      var wien = num(q('[data-in="wien"]')), lounge = num(q('[data-in="lounge"]')), guests = num(q('[data-in="guests"]')), spend = num(q('[data-in="spend"]'));
      var lvl = +q('[data-in="vers"]').value, wel = q('[data-welcome]').checked;
      var want = [].slice.call(hub.querySelectorAll('[data-item]')).filter(function (c) { return c.checked; }).map(function (c) { return c.dataset.item; });
      var res = {};
      D.cards.forEach(function (c) {
        var lv = c.minsp && spend * 12 < c.minsp ? 0 : Math.min(c.wien ? wien : wien + lounge, lim(c.visits)), gv = Math.min(guests, lv, lim(c.guests));
        var pts = spend * 12 / 100 * c.pp100; if (c.pmax) pts = Math.min(pts, c.pmax);
        var v = (lv + gv) * D.lounge + pts + c.fix + (wel ? c.welcome : 0);
        want.forEach(function (k) { if (c.it[k]) v += c.it[k]; });
        var low = lvl > 0 && c.tier < lvl;
        if (lvl > 0 && !low) v += D.vers[String(lvl)];
        res[c.s] = { net: v - c.fee, val: v, fee: c.fee, low: low };
      });
      [].slice.call(document.querySelectorAll('.catgrid')).forEach(function (g) {
        var tiles = [].slice.call(g.querySelectorAll('[data-card]'));
        if (!tiles.length) return;
        tiles.sort(function (a, b) {
          var x = res[a.dataset.card], y = res[b.dataset.card];
          return (x.low - y.low) || (y.net - x.net);
        });
        tiles.forEach(function (t) {
          var r = res[t.dataset.card], n = t.querySelector('[data-net]');
          n.hidden = false; n.className = 'lnet ' + (r.net >= 0 ? 'good' : 'bad');
          n.textContent = sign(r.net) + ' pro Jahr' + (r.low ? ' · Versicherung schwächer als gewünscht' : '');
          t.querySelector('[data-def]').textContent = 'Deine Vorteile ' + eur(r.val) + ', Jahresgebühr ' + r.fee.toLocaleString('de-DE', { maximumFractionDigits: 2 }) + ' €';
          t.classList.toggle('dim', r.low);
          g.appendChild(t);
        });
      });
    }
    hub.addEventListener('input', calc); hub.addEventListener('change', calc);
    hub.hidden = false; calc();
  })();
})();
