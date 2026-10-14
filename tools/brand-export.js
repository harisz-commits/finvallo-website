// Erzeugt die Logo-Exporte für Profile (C21): public/assets/brand/logo-400x400.png und banner-1500x500.png.
// Einmalig ausführen mit Playwright (nicht Teil des Builds): NODE_PATH=$(npm root -g) node tools/brand-export.js
const { chromium } = require('playwright'); const fs = require('fs');
const R = require('path').join(__dirname, '..', 'public', 'assets') + '/';
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME || undefined });
  const font = `@font-face{font-family:Figtree;font-weight:800;src:url(file://${R}fonts/figtree-latin-800-normal.woff2)}`;
  const fav = fs.readFileSync(R + 'favicon.svg', 'utf8'), logo = fs.readFileSync(R + 'logo.svg', 'utf8');
  const shots = [
    ['logo-400x400.png', 400, 400, `<div style="width:400px;height:400px">${fav.replace('<svg ', '<svg width="400" height="400" ')}</div>`],
    ['banner-1500x500.png', 1500, 500, `<div style="width:1500px;height:500px;background:#f4f8f7;display:flex;align-items:center;justify-content:center;padding-left:190px;box-sizing:border-box">${logo.replace('<svg ', '<svg width="840" height="200" ')}</div>`],
  ];
  for (const [f, w, h, html] of shots) {
    const p = await b.newPage({ viewport: { width: w, height: h } });
    const tmp = require('os').tmpdir() + '/brand-tmp.html'; fs.writeFileSync(tmp, `<!doctype html><style>${font}html,body{margin:0}</style>${html}`);
    await p.goto('file://' + tmp); await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(300);
    await p.screenshot({ path: R + 'brand/' + f, omitBackground: false }); await p.close();
  }
  await b.close();
})();
