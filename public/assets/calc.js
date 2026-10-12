/* Finvallo Rechner – gemeinsame Rechenfunktionen. Reine Funktionen, damit sie getestet werden können. */
(function(root){
  const F = {};
  // Monatszins aus effektivem Jahreszins (konformer Zins)
  F.monthlyFromEffective = r => Math.pow(1 + r, 1/12) - 1;
  // Zinseszins / Sparplan, monatliche Simulation
  F.savings = function({start=0, rate=0, months=0, yearsRateEff=true, pay=0, payStart=true, dyn=0}){
    const m = F.monthlyFromEffective(rate);
    let bal = start, paid = start, p = pay; const years = [];
    for (let i = 1; i <= months; i++){
      if (payStart){ bal += p; paid += p; }
      bal *= (1 + m);
      if (!payStart){ bal += p; paid += p; }
      if (i % 12 === 0 || i === months){
        years.push({year: Math.ceil(i/12), balance: bal, paid: paid, interest: bal - paid});
        if (i % 12 === 0) p = p * (1 + dyn);
      }
    }
    return {end: bal, paid: paid, interest: bal - paid, years};
  };
  // Annuitätendarlehen: Rate aus Betrag, Sollzins p. a. (monatlich i/12), Laufzeit in Monaten
  F.annuity = function(K, i, n){
    const q = i/12;
    if (n <= 0) return NaN;
    return q === 0 ? K/n : K * q * Math.pow(1+q, n) / (Math.pow(1+q, n) - 1);
  };
  // Laufzeit (Monate) aus Rate; Infinity wenn die Rate die Zinsen nicht deckt
  F.annuityMonths = function(K, i, A){
    const q = i/12;
    if (q === 0) return Math.ceil(K / A);
    if (A <= K*q) return Infinity;
    return Math.ceil(-Math.log(1 - K*q/A) / Math.log(1+q));
  };
  F.schedule = function(K, i, A, maxMonths=1200){
    const q = i/12; let rest = K, interest = 0, paid = 0; const years = []; let n = 0;
    let yi = 0, yt = 0;
    while (rest > 0.005 && n < maxMonths){
      n++; const z = rest*q; let t = A - z; if (t > rest) t = rest;
      rest -= t; interest += z; paid += z + t; yi += z; yt += t;
      if (n % 12 === 0 || rest <= 0.005){ years.push({year: Math.ceil(n/12), interest: yi, principal: yt, rest: Math.max(rest,0)}); yi = 0; yt = 0; }
    }
    return {months: n, interest, paid, years};
  };
  F.effective = i => Math.pow(1 + i/12, 12) - 1;
  // Kreditkarten-Teilzahlung: effektiver Jahreszins, Mindestrate in % und Mindestbetrag
  F.revolving = function({balance, eff, pct, min}){
    const m = F.monthlyFromEffective(eff); let b = balance, interest = 0, n = 0, paid = 0;
    while (b > 0.005 && n < 1200){
      n++; const z = b*m; b += z; interest += z;
      let pay = Math.max(b*pct, min); if (pay > b) pay = b;
      if (pay <= z && b > 0) { return {months: Infinity, interest: Infinity, paid: Infinity}; }
      b -= pay; paid += pay;
    }
    return {months: n, interest, paid};
  };
  // Entnahmeplan: Entnahme jeweils zu Monatsbeginn
  F.withdrawMonths = function(K, r, W, maxMonths=1200){
    const m = F.monthlyFromEffective(r); let b = K, n = 0, total = 0;
    while (n < maxMonths){
      if (b < W){ total += b; b = 0; n++; break; }
      b -= W; total += W; n++; b *= (1+m);
      if (b <= 0.005) break;
    }
    return {months: (n >= maxMonths && b > 0) ? Infinity : n, total, rest: b};
  };
  F.withdrawAmount = function(K, r, n){
    const m = F.monthlyFromEffective(r);
    return m === 0 ? K/n : K * m / ((1 - Math.pow(1+m, -n)) * (1+m));
  };
  F.cagr = (a, b, years) => Math.pow(b/a, 1/years) - 1;
  F.inflation = (amount, i, years) => ({real: amount/Math.pow(1+i, years), needed: amount*Math.pow(1+i, years)});
  // Kapitalertragsteuer
  F.taxDE = function({gain, allowance=1000, church=0}){
    const x = Math.max(0, gain - allowance);
    const abg = church ? x/(4+church) : x*0.25;
    const soli = abg*0.055, kist = abg*church;
    return {taxable: x, abg, soli, kist, total: abg+soli+kist, net: gain-(abg+soli+kist)};
  };
  F.taxAT = function({gain, rate=0.275}){ const t = Math.max(0,gain)*rate; return {taxable: Math.max(0,gain), total: t, net: gain - t}; };
  F.vat = function({amount, rate, from}){ return from === 'netto' ? {net: amount, vat: amount*rate, gross: amount*(1+rate)} : {gross: amount, net: amount/(1+rate), vat: amount - amount/(1+rate)}; };
  // Formatierung
  F.eur = (x, d=2) => isFinite(x) ? x.toLocaleString('de-DE', {minimumFractionDigits: d, maximumFractionDigits: d}) + ' €' : '–';
  F.pct = (x, d=2) => isFinite(x) ? (x*100).toLocaleString('de-DE', {minimumFractionDigits: d, maximumFractionDigits: d}) + ' %' : '–';
  F.num = v => { let t = String(v).trim().replace(/\s|€|%/g,'');
    if (t.includes(',')) t = t.replace(/\./g,'').replace(',','.');            // 1.234,56
    else if (/^\-?\d{1,3}(\.\d{3})+$/.test(t)) t = t.replace(/\./g,'');     // 10.000 = zehntausend
    const x = parseFloat(t); return isFinite(x) ? x : 0; };
  F.months = n => { if (!isFinite(n)) return 'nie (die Rate deckt nicht einmal die Zinsen)'; const y = Math.floor(n/12), m = n%12;
    return (y ? y + (y === 1 ? ' Jahr' : ' Jahre') : '') + (m ? (y ? ' und ' : '') + m + (m === 1 ? ' Monat' : ' Monate') : ''); };
  // einfaches Balkendiagramm (SVG)
  F.bars = function(el, rows, keys, colors){
    if (!el || !rows.length) { if (el) el.innerHTML=''; return; }
    const W = 640, H = 220, pad = 28, bw = (W - pad*2) / rows.length;
    const max = Math.max(...rows.map(r => keys.reduce((s,k)=>s+Math.max(0,r[k]),0))) || 1;
    let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Diagramm" style="width:100%;height:auto">`;
    rows.forEach((r,i) => { let y = H - pad; keys.forEach((k,j) => { const h = Math.max(0,r[k]) / max * (H - pad*2); y -= h;
      s += `<rect x="${pad + i*bw + bw*0.15}" y="${y}" width="${bw*0.7}" height="${h}" fill="${colors[j]}" rx="2"><title>Jahr ${r.year}: ${F.eur(r[k],0)}</title></rect>`; });
      if (rows.length <= 15 || i % Math.ceil(rows.length/15) === 0) s += `<text x="${pad + i*bw + bw/2}" y="${H-8}" font-size="11" text-anchor="middle" fill="currentColor" opacity=".6">${r.year}</text>`; });
    el.innerHTML = s + '</svg>';
  };
  root.FinCalc = F;
  if (typeof module !== 'undefined') module.exports = F;
})(typeof window !== 'undefined' ? window : globalThis);
