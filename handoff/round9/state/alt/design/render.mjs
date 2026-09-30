// node render.mjs <in.html|svg> <out.png> <width> <height> [scale] [transparent]
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
const [,, inp, out, w, h, scale = '1', transp = '0'] = process.argv;
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: +scale });
await page.goto('file://' + path.resolve(inp));
await page.waitForTimeout(150);
await page.screenshot({ path: out, omitBackground: transp === '1', clip: { x: 0, y: 0, width: +w, height: +h } });
await browser.close();
