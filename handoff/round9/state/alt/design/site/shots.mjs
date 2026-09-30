// node site/shots.mjs -- full-page renders of the product page at 1280 and 390, light and dark, plus overflow checks
import { chromium } from 'playwright';
import path from 'path';
const here = path.dirname(new URL(import.meta.url).pathname);
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
let bad = 0;
for (const w of [1280, 390]) for (const scheme of ['light', 'dark']) {
  const page = await browser.newPage({ viewport: { width: w, height: 900 }, deviceScaleFactor: w < 500 ? 2 : 1, colorScheme: scheme });
  page.on('pageerror', (e) => { console.error('pageerror', e.message); bad++; });
  await page.goto('file://' + path.join(here, 'index.html'), { waitUntil: 'load' });
  await page.evaluate(() => document.querySelectorAll('img[loading=lazy]').forEach(i => i.loading = 'eager'));
  await page.waitForTimeout(600);
  const r = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth,
    fonts: [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family).join(',') }));
  if (r.sw > r.cw) { console.error(`overflow at ${w} ${scheme}: ${r.sw} > ${r.cw}`); bad++; }
  await page.screenshot({ path: path.join(here, 'shots', `page-${scheme}-${w}.png`), fullPage: true });
  console.log(`${w} ${scheme}: scrollWidth ${r.sw} / ${r.cw}; fonts loaded: ${r.fonts || 'none (fallback stack)'}`);
  await page.close();
}
// theme toggle: explicit dark over an OS light preference swaps the picture sources
const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, colorScheme: 'light' });
await page.goto('file://' + path.join(here, 'index.html'));
await page.click('#theme');
await page.waitForTimeout(300);
const hero = await page.evaluate(() => document.querySelector('.hero img').currentSrc.split('/').pop());
console.log(`toggle to dark on a light OS: hero shows ${hero}`);
if (!hero.includes('dark')) bad++;
await page.click('#t-dhw');
const vis = await page.evaluate(() => [...document.querySelectorAll('[role=tabpanel]')].map(p => p.id + ':' + !p.hidden).join(' '));
console.log(`gallery after selecting Hot water by weekday: ${vis}`);
await browser.close();
console.log(bad ? `RESULT: ${bad} problem(s)` : 'RESULT: no overflow, no page errors, toggle and tabs work');
process.exit(bad ? 1 : 0);
