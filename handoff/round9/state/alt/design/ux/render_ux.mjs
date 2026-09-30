// node render_ux.mjs <in.html> <out.png> <width> [scale]  -- screenshots the #m element at the given viewport width
import { chromium } from 'playwright';
import path from 'path';
const [,, inp, out, w, scale = '2'] = process.argv;
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const page = await browser.newPage({ viewport: { width: +w, height: 900 }, deviceScaleFactor: +scale });
page.on('pageerror', (e) => console.error('pageerror', e.message));
await page.goto('file://' + path.resolve(inp));
await page.waitForTimeout(150);
const el = await page.$('#m');
const sw = await page.evaluate(() => document.documentElement.scrollWidth);
if (sw > +w) console.error(`overflow: ${inp} scrollWidth ${sw} > ${w}`);
await el.screenshot({ path: out });
await browser.close();
