/* Filter und Sortierung für die Kartenliste (alle Karten bleiben im HTML, nur Ein-/Ausblenden). */
(function () {
  var box = document.getElementById('filt'), list = document.getElementById('list');
  if (!box || !list) return;
  var items = [].slice.call(list.querySelectorAll('article.item'));
  items.forEach(function (it, i) { it.dataset.ord = i; });
  var q = box.querySelector('[data-q]'), typ = box.querySelector('[data-typ]'), netz = box.querySelector('[data-netz]'),
      sort = box.querySelector('[data-sort]'), count = box.querySelector('[data-count]'), reset = box.querySelector('[data-reset]');
  var chips = [].slice.call(box.querySelectorAll('[data-flag]'));
  function norm(s) { return (s || '').toLowerCase(); }
  function apply() {
    var on = chips.filter(function (c) { return c.getAttribute('aria-pressed') === 'true'; }).map(function (c) { return c.dataset.flag; });
    var t = norm(q.value).trim(), n = 0;
    items.forEach(function (it) {
      var f = ' ' + (it.dataset.f || '') + ' ';
      var ok = on.every(function (x) { return f.indexOf(' ' + x + ' ') >= 0; })
        && (!typ.value || it.dataset.typ === typ.value)
        && (!netz.value || norm(it.dataset.netz).indexOf(netz.value) >= 0)
        && (!t || norm(it.dataset.q).indexOf(t) >= 0);
      it.hidden = !ok; if (ok) n++;
    });
    var s = sort.value, arr = items.slice();
    if (s === 'fee') arr.sort(function (a, b) { return (+a.dataset.fee) - (+b.dataset.fee) || a.dataset.ord - b.dataset.ord; });
    else if (s === 'name') arr.sort(function (a, b) { return norm(a.dataset.q).localeCompare(norm(b.dataset.q), 'de'); });
    else arr.sort(function (a, b) { return a.dataset.ord - b.dataset.ord; });
    arr.forEach(function (it) { list.appendChild(it); });
    count.textContent = n === 1 ? '1 Karte' : n + ' Karten';
    var active = on.length || typ.value || netz.value || t || s !== 'rank';
    reset.hidden = !active;
  }
  chips.forEach(function (c) {
    c.addEventListener('click', function () { c.setAttribute('aria-pressed', c.getAttribute('aria-pressed') === 'true' ? 'false' : 'true'); apply(); });
  });
  [q, typ, netz, sort].forEach(function (el) { el.addEventListener(el === q ? 'input' : 'change', apply); });
  reset.addEventListener('click', function () {
    chips.forEach(function (c) { c.setAttribute('aria-pressed', 'false'); });
    q.value = ''; typ.value = ''; netz.value = ''; sort.value = 'rank'; apply();
  });
  box.hidden = false;
  apply();
})();
