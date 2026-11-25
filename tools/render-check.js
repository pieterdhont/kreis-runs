// Headless visual check of Kreis Runs: gait stills, a low-angle close-up, a fast-run face, the 360° circle and a drag-orbit.
// Usage:  cd tools && npm install && npx playwright install chromium
//         node render-check.js ../app/kreis-runs out/check
// three.js is served from tools/node_modules so the check also runs offline. Set CHROME=/path/to/chrome to use a system browser.
const { chromium } = require('playwright');
const path = require('path');
const [, , htmlDirArg = '../app/kreis-runs', out = 'out/check'] = process.argv;
const htmlDir = path.resolve(htmlDirArg);
require('fs').mkdirSync(path.dirname(path.resolve(out)), { recursive: true });
(async () => {
  const browser = await chromium.launch({ ...(process.env.CHROME ? { executablePath: process.env.CHROME } : {}), args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await browser.newPage({ viewport: { width: 1280, height: 1000 } });
  page.on('pageerror', e => console.log('pageerror:', e.message));
  page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.log('console:', m.text().slice(0, 300)); });
  await page.route('**/*', r => {
    const u = r.request().url(), m = u.match(/cdn\.jsdelivr\.net\/npm\/three@0\.160\.0\/(.*)$/);
    if (m) return r.fulfill({ path: path.join(__dirname, 'node_modules/three', m[1]), contentType: 'application/javascript' });
    return u.startsWith('file://') ? r.continue() : r.abort();
  });
  await page.goto('file://' + path.join(htmlDir, 'index.html'));
  await page.evaluate(() => { try { localStorage.clear() } catch {} });
  await page.reload();
  await page.waitForTimeout(4500);
  const st = page.locator('#stage');
  const zoom = async v => { await page.evaluate(v => { const z = document.getElementById('zoom'); z.value = v; z.dispatchEvent(new Event('input')); }, v); };
  const snap = async (name, wait = 2500) => { await page.waitForTimeout(wait); await st.screenshot({ path: `${out}_${name}.png` }); };
  await zoom(560); await page.waitForTimeout(2500);
  for (let i = 0; i < 4; i++) { await page.click('#play'); await page.waitForTimeout(400); await st.screenshot({ path: `${out}_gait${i}.png` }); await page.click('#play'); await page.waitForTimeout(170 + i * 60); }
  await page.click('[data-cam=low]'); await zoom(640); await snap('low', 3500);
  await page.evaluate(() => { const s = document.getElementById('speed'); s.value = 2; s.dispatchEvent(new Event('input')); });
  await zoom(860); await snap('face_fast', 3500);
  await page.evaluate(() => { const s = document.getElementById('speed'); s.value = 1; s.dispatchEvent(new Event('input')); });
  await page.click('#zReset'); await page.click('[data-cam=side]'); await zoom(560);
  await page.click('[data-fx=circle]'); await snap('circle_a', 4000); await snap('circle_b', 3000); await snap('circle_c', 3000);
  await page.click('[data-fx=circle]');
  await page.mouse.move(640, 500); await page.mouse.down(); await page.mouse.move(900, 380, { steps: 10 }); await page.mouse.up(); await snap('drag', 2000);
  await browser.close();
})();
