/* Festgeld-Vergleich: Zins und Ertrag für Betrag und Laufzeit, Filter und Sortierung.
   calc() rechnet genau wie ertrag() in tools/festgeld.py (Kontrolle: tools/festgeld-kontrolle.js). */
(function () {
  // k.z = [[Monate, Zins p. a., Betrag ab, Betrag bis], ...], k.amin/k.amax = Mindest-/Höchstanlage, k.ze = Zinseszins
  function calc(k, b, m) {
    var rows = k.z.filter(function (r) { return r[0] === m; }), best = null;
    rows.forEach(function (r) {
      if ((r[2] === null || b >= r[2]) && (r[3] === null || b <= r[3]) && (!best || r[1] > best[1])) best = r;
    });
    if (!rows.length) return { fit: false, why: 'lz' };
    if (!best || (k.amin !== null && b < k.amin) || (k.amax !== null && b > k.amax)) {
      var top = rows.reduce(function (a, r) { return r[1] > a[1] ? r : a; }, rows[0]);
      return { fit: false, why: 'betrag', zins: top[1] };
    }
    var j = m / 12, z = best[1] / 100;
    var e = m > 12 && k.ze === true ? b * (Math.pow(1 + z, j) - 1) : b * z * j;
    return { fit: true, zins: best[1], ertrag: Math.floor(e * 100 + 0.5 + 1e-6) / 100 };  // kaufmännisch gerundet
  }
  if (typeof document === 'undefined') { module.exports = { calc: calc }; return; }

  var fmt = function (v, d) { return v.toLocaleString('de-DE', { minimumFractionDigits: d, maximumFractionDigits: d }); };
  var box = document.getElementById('filt'), calcBox = document.getElementById('fcalc');
  if (!box || !calcBox) return;
  var list = document.querySelector('.list[data-fg]');
  // Einträge jenseits der ersten 60 stehen in einem <template>. Alle Einträge werden gefiltert und sortiert,
  // aber nur die sichtbaren hängen im DOM; der Rest wartet in einem DocumentFragment (kleines DOM, schnelles Filtern).
  var tpl = list.querySelector('template[data-rest]'), frag = document.createDocumentFragment();
  if (tpl) { frag.appendChild(tpl.content); tpl.remove(); }
  var items = [].slice.call(list.querySelectorAll('article.item[data-k]')).concat([].slice.call(frag.querySelectorAll('article.item[data-k]')));
  items.forEach(function (it, i) { it.dataset.ord = i; it._k = JSON.parse(it.dataset.k); });
  var $ = function (s, el) { return (el || box).querySelector(s); };
  var betrag = $('[data-in="betrag"]', calcBox), lz = $('[data-in="lz"]', calcBox);
  var q = $('[data-q]'), sitz = $('[data-sitz]'), rat = $('[data-rat]'), zz = $('[data-zz]'), sort = $('[data-sort]'),
      count = $('[data-count]'), reset = $('[data-reset]'), more = document.querySelector('[data-more]');
  var chips = [].slice.call(box.querySelectorAll('[data-flag]'));
  var LIMIT = +list.dataset.limit || 0, open = false, def = { b: betrag.value, m: lz.value };

  // Startwerte aus der Adresse (?betrag=25000&laufzeit=24)
  try {
    var u = new URLSearchParams(location.search);
    if (u.get('betrag')) betrag.value = u.get('betrag');
    if (u.get('laufzeit') && lz.querySelector('option[value="' + u.get('laufzeit') + '"]')) lz.value = u.get('laufzeit');
  } catch (e) {}

  function num(el) { var v = parseFloat(String(el.value).replace(/\./g, '').replace(',', '.')); return isFinite(v) && v > 0 ? v : 0; }
  function apply() {
    var b = num(betrag), m = parseFloat(lz.value);
    var on = chips.filter(function (c) { return c.getAttribute('aria-pressed') === 'true'; }).map(function (c) { return c.dataset.flag; });
    var t = (q.value || '').toLowerCase().trim(), s = sitz.value, r = +rat.value || 0, z = zz.value, n = 0;
    items.forEach(function (it) {
      var c = calc(it._k, b, m), f = ' ' + (it.dataset.f || '') + ' ';
      it._c = c;
      var ok = c.why !== 'lz' && on.every(function (x) { return f.indexOf(' ' + x + ' ') >= 0; }) && (!t || it.dataset.q.indexOf(t) >= 0) &&
               (!s || it.dataset.sitz === s) && (+it.dataset.rat || 0) >= r && (!z || it.dataset.zz === z);
      it.hidden = !ok;
      it.classList.toggle('dim', ok && !c.fit);
      if (!ok) return;
      n++;
      it.querySelector('[data-zins]').textContent = c.zins !== undefined ? fmt(c.zins, 2) + ' %' : '–';
      it.querySelector('[data-ertrag]').textContent = c.fit ? fmt(c.ertrag, 2) + ' €' : 'passt nicht';
      it.querySelector('[data-lbl]').textContent = 'Zinsen für ' + fmt(b, 0) + ' €';
      var why = it.querySelector('[data-why]');
      if (why) why.textContent = c.fit ? '' : 'Dein Betrag liegt außerhalb der Anlagegrenzen dieses Angebots.';
    });
    var sv = sort.value;
    items.sort(function (x, y) {
      var cx = x._c, cy = y._c;
      if (cx.fit !== cy.fit) return cx.fit ? -1 : 1;
      if (sv === 'rat') return (+y.dataset.rat || 0) - (+x.dataset.rat || 0) || (cy.zins || 0) - (cx.zins || 0);
      if (sv === 'name') return x.dataset.q.localeCompare(y.dataset.q, 'de');
      return (cy.zins || 0) - (cx.zins || 0) || (+y.dataset.rat || 0) - (+x.dataset.rat || 0) || x.dataset.ord - y.dataset.ord;
    });
    var shown = 0;
    items.forEach(function (it) {
      it.classList.remove('over');
      if (!it.hidden) shown++;
      if (!it.hidden && (!LIMIT || open || shown <= LIMIT)) list.appendChild(it); else frag.appendChild(it);
    });
    if (more) { more.hidden = !LIMIT || open || shown <= LIMIT; more.textContent = 'Alle ' + shown + ' Angebote zeigen'; }
    count.textContent = n === 1 ? '1 Angebot' : n + ' Angebote';
    reset.hidden = !(on.length || t || s || r || z || sort.value !== 'zins');
    try {
      var p = new URLSearchParams(location.search);
      if (betrag.value !== def.b) p.set('betrag', String(b)); else p.delete('betrag');
      if (lz.value !== def.m) p.set('laufzeit', lz.value); else p.delete('laufzeit');
      var qs = p.toString(); history.replaceState(null, '', location.pathname + (qs ? '?' + qs : '') + location.hash);
    } catch (e) {}
  }
  chips.forEach(function (c) { c.addEventListener('click', function () { c.setAttribute('aria-pressed', c.getAttribute('aria-pressed') === 'true' ? 'false' : 'true'); apply(); }); });
  [q, betrag].forEach(function (el) { el.addEventListener('input', apply); });
  [sitz, rat, zz, sort].forEach(function (el) { el.addEventListener('change', apply); });
  // Auf den Laufzeit-Seiten stehen nur Angebote mit dieser Laufzeit: andere Laufzeit = Sprung zum Gesamtvergleich
  lz.addEventListener('change', function () {
    if (lz.dataset.nav) location.href = lz.dataset.nav + '?laufzeit=' + lz.value + (betrag.value !== def.b ? '&betrag=' + num(betrag) : '');
    else apply();
  });
  if (more) more.addEventListener('click', function () { open = true; apply(); });
  reset.addEventListener('click', function () {
    chips.forEach(function (c) { c.setAttribute('aria-pressed', 'false'); });
    q.value = ''; sitz.value = ''; rat.value = ''; zz.value = ''; sort.value = 'zins'; apply();
  });
  box.hidden = false; calcBox.hidden = false;
  apply();
})();
