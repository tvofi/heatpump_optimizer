// node site/docs_shots.mjs SITE_DIR OUT_DIR -- every built page at 1280 and 390, light and dark: overflow, page errors,
// mermaid drawn; full-page renders of a chosen few for the design record.
import { chromium } from 'playwright';
import fs from 'fs'; import path from 'path';
const [, , site, out] = process.argv;
fs.mkdirSync(out, { recursive: true });
const pages = fs.readdirSync(site).filter(f => f.endsWith('.html'));
const keep = new Set(['readme.html:1280:light', 'how-it-works.html:1280:dark', 'configuration.html:1280:light', 'setup.html:390:light', 'architecture.html:390:dark']);
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
let bad = 0;
for (const p of pages) for (const w of [1280, 390]) for (const scheme of ['light', 'dark']) {
  const page = await browser.newPage({ viewport: { width: w, height: 900 }, colorScheme: scheme, deviceScaleFactor: 1 });
  const errs = []; page.on('pageerror', e => errs.push(e.message));
  await page.goto('file://' + path.resolve(site, p), { waitUntil: 'load' });
  await page.waitForTimeout(p.match(/readme|how-it|config|architecture/) ? 2500 : 300);
  const r = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth,
    pre: document.querySelectorAll('pre.mermaid').length, drawn: document.querySelectorAll('pre.mermaid svg').length,
    broken: [...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.getAttribute('src')) }));
  const probs = [];
  if (r.sw > r.cw) probs.push(`overflow ${r.sw}>${r.cw}`);
  if (r.drawn < r.pre) probs.push(`mermaid ${r.drawn}/${r.pre} drawn`);
  if (r.broken.length) probs.push(`broken images ${r.broken.join(' ')}`);
  if (errs.length) probs.push(`page errors ${errs.join(' | ').slice(0, 200)}`);
  if (probs.length) { bad++; console.log(`${p} ${w} ${scheme}: ${probs.join('; ')}`); }
  if (keep.has(`${p}:${w}:${scheme}`)) await page.screenshot({ path: path.join(out, `${p.replace('.html', '')}-${scheme}-${w}.png`), fullPage: w < 500 ? false : false });
  await page.close();
}
await browser.close();
console.log(`${pages.length} pages x 2 widths x 2 themes: ${bad ? bad + ' with problems' : 'no overflow, no page errors, every image loads, every diagram drawn'}`);
process.exit(bad ? 1 : 0);
