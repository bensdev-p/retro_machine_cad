// Render preview PNGs from the offline viewer with the pre-installed Playwright Chromium.
// Usage: node tools/render_p2.js   (run after cad/p2_concept.py and tools/package_p2.py)
const path = require('path'); const { chromium } = require('playwright');
const OUT = path.resolve(__dirname, '../outputs/p2');
const shots = [
  ['01_operating_charcoal', 'operating', 'charcoal', 'operating'],
  ['02_operating_classic', 'operating', 'classic', 'operating'],
  ['03_closed_carry', 'closed', 'charcoal', 'closed'],
  ['04_closed_classic', 'closed', 'classic', 'closed'],
  ['05_rear_drawer', 'rear', 'charcoal', 'rear'],
  ['06_xray', 'xray', 'charcoal', 'xray'],
  ['07_front', 'operating', 'charcoal', 'front'],
  ['08_side_closed', 'closed', 'charcoal', 'side'],
  ['09_side_operating', 'operating', 'charcoal', 'side_op'],
  ['10_operating_stock_keyboard', 'operating', 'charcoal_stock_kb', 'operating'],
  ['11_operating_m_edition', 'operating', 'm_edition', 'operating'],
  ['12_closed_m_edition', 'closed', 'm_edition', 'closed'],
];
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await browser.newPage({ viewport: { width: 1400, height: 950 }, deviceScaleFactor: 2, colorScheme: 'light' });
  page.on('pageerror', e => { console.error('page error', e); process.exitCode = 1; });
  await page.goto('file://' + path.join(OUT, 'viewer.html'));
  await page.waitForFunction(() => window.__ready === true, null, { timeout: 120000 });
  await page.evaluate(() => { window.__pause = true; });
  page.setDefaultTimeout(240000);
  await page.addStyleTag({ content: 'header, #info { display:none !important }' });
  for (const [name, state, pal, view] of shots) {
    await page.evaluate(([s, p, v]) => window.__setup(s, p, v), [state, pal, view]);
        await page.screenshot({ path: path.join(OUT, 'previews', name + '.png'), animations: 'disabled', caret: 'initial' });
    console.log('rendered', name);
  }
  await browser.close();
})();
