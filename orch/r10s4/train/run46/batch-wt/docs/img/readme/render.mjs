// node render.mjs <in.html|svg> <out.png> <width> <height> [scale] [transparent]
import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';
// createRequire, not a static import: resolves playwright from NODE_PATH or a global install, as tests/card_browser.mjs does
const { chromium } = createRequire(import.meta.url)('playwright');
const [,, inp, out, w, h, scale = '1', transp = '0'] = process.argv;
const browser = await chromium.launch({ executablePath: process.env.HPO_CHROMIUM || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: +scale });
await page.goto('file://' + path.resolve(inp));
await page.waitForTimeout(150);
await page.screenshot({ path: out, omitBackground: transp === '1', clip: { x: 0, y: 0, width: +w, height: +h } });
await browser.close();
