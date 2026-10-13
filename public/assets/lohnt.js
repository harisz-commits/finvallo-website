/* Rechner „Ab wann lohnt sich die Karte?“: rechnet die genutzten Vorteile gegen die Jahresgebühr. */
(function () {
  var box = document.querySelector('[data-lohnt]');
  if (!box) return;
  var D = JSON.parse(box.getAttribute('data-lohnt'));
  var q = function (s) { return box.querySelector(s); };
  var all = function (s) { return [].slice.call(box.querySelectorAll(s)); };
  var eur = function (v) { return Math.round(v).toLocaleString('de-DE') + ' €'; };
  function num(el) { var v = parseFloat(String(el.value).replace(',', '.')); return isFinite(v) && v > 0 ? v : 0; }
  function calc() {
    var lounge = num(q('[data-in="lounge"]')), guests = num(q('[data-in="guests"]')), spend = num(q('[data-in="spend"]')), sub = q('[data-in="subs"]');
    var lv = D.visits === null ? lounge : Math.min(lounge, D.visits);
    var gv = Math.min(guests, lv, D.guests === 'unbegrenzt' ? Infinity : D.guests);
    var pts = spend * 12 / 100 * D.pp100; if (D.pmax) pts = Math.min(pts, D.pmax);
    var v = lv * D.lounge + gv * D.lounge + pts + (sub ? num(sub) * 12 : 0);
    all('[data-credit]').forEach(function (c) { if (c.checked) v += D.credits[+c.dataset.credit].v; });
    var w = q('[data-welcome]'); if (w && w.checked) v += D.welcome;
    if (q('[data-vers]').checked) v += D.vers;
    var net = v - D.fee;
    q('[data-out="val"]').textContent = eur(v);
    var n = q('[data-out="net"]'); n.textContent = (net >= 0 ? '+' : '−') + eur(Math.abs(net)); n.className = net >= 0 ? 'good' : 'bad';
    var t = q('[data-out="txt"]');
    if (net >= 0) t.textContent = 'Bei dieser Nutzung holst du die Jahresgebühr wieder herein und hast ' + eur(net) + ' im Jahr mehr, als die Karte kostet.';
    else {
      var more = Math.ceil(-net / D.lounge);
      var free = D.visits === null ? Infinity : D.visits - lv;
      t.textContent = 'Bei dieser Nutzung kostet dich die Karte ' + eur(-net) + ' im Jahr mehr, als sie bringt.' +
        (more <= free ? ' Mit etwa ' + more + ' Lounge-Besuchen mehr wäre sie im Plus.' : ' Eine günstigere Karte passt besser zu dir.');
    }
  }
  box.addEventListener('input', calc); box.addEventListener('change', calc);
  box.hidden = false; calc();
})();
