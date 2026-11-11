// Pre-renders each ```mermaid block of README.md to a light and a dark PNG and records a source-hash manifest beside them.
//
// Why: the Home Assistant Marketplace renders README.md without mermaid, so a fence shows as raw code (R10-README-GRAPHICS,
// dev/audit/harnesses/r10_readme_marketplace_pipeline.mjs). README.md carries a <picture> directly above each block's
// (closed) <details>: the light PNG as the <img>, the dark PNG as a prefers-color-scheme: dark <source>; GitHub and tools/site/build_docs.mjs still draw the live diagram from the block.
//
// Run from the repository root after editing any mermaid block, then commit the PNGs and the manifest:
//   npm ci --prefix tools/site           # the mermaid pinned in tools/site/package-lock.json (pages.yml's install)
//   npm ci --prefix tests/pwlane && npx --prefix tests/pwlane playwright install chromium   # playwright, as tests/card_browser.mjs
//   NODE_PATH=$PWD/tests/pwlane/node_modules node docs/img/readme/render_mermaid.mjs
// Env: MERMAID_JS (default tools/site/node_modules/mermaid/dist/mermaid.min.js), HPO_CHROMIUM (default: playwright's own).
//
// tests/doc_claims.py compares SOURCES, not pixels: PNG bytes do not reproduce across machines (fonts, rasteriser). It
// refuses a block whose sha256 differs from the manifest's, and a PNG (either variant) whose sha256 differs from the manifest's.
// The dark variant uses mermaid's dark theme on docs/site/docs.css's dark --bg (#0b1a28).
import { createRequire } from 'module';
import crypto from 'crypto';
import fs from 'fs';
import path from 'path';

const { chromium } = createRequire(import.meta.url)('playwright');
const ROOT = process.cwd();
const README = path.join(ROOT, 'README.md');
const OUT = 'docs/img/readme';
const MANIFEST = path.join(ROOT, OUT, 'mermaid_figures.json');
const MERMAID_JS = process.env.MERMAID_JS || path.join(ROOT, 'tools/site/node_modules/mermaid/dist/mermaid.min.js');
// one entry per block, in README order; the count is checked against the README below
const NAMES = ['mermaid-how-the-pieces-fit', 'mermaid-setup-flow', 'mermaid-one-interval'];
const sha = (b) => crypto.createHash('sha256').update(b).digest('hex');

// the block body is what tests/doc_claims.py hashes: the text between the fence lines, trailing newline included
const blocks = [...fs.readFileSync(README, 'utf8').matchAll(/^```mermaid\n([\s\S]*?)^```/gm)].map((m) => m[1]);
if (blocks.length !== NAMES.length) throw new Error(`README.md has ${blocks.length} mermaid blocks, NAMES has ${NAMES.length}`);
const version = JSON.parse(fs.readFileSync(path.join(path.dirname(path.dirname(MERMAID_JS)), 'package.json'), 'utf8')).version;

const launch = process.env.HPO_CHROMIUM ? { executablePath: process.env.HPO_CHROMIUM } : {};
const browser = await chromium.launch(launch);
const page = await browser.newPage({ viewport: { width: 1200, height: 900 }, deviceScaleFactor: 2 });
await page.setContent('<!doctype html><body style="margin:0"><div id="fig" style="display:inline-block;width:1100px;padding:24px"></div></body>');
await page.addScriptTag({ path: MERMAID_JS });
const VARIANTS = [{ key: 'light', suffix: '', theme: 'neutral', bg: '#ffffff' }, { key: 'dark', suffix: '-dark', theme: 'dark', bg: '#0b1a28' }];
const figures = [];
for (const [i, src] of blocks.entries()) {
  const fig = { png: `${OUT}/${NAMES[i]}.png`, png_dark: `${OUT}/${NAMES[i]}-dark.png`, block_sha256: sha(src) };
  for (const v of VARIANTS) {
    await page.evaluate(async ([s, theme, bg]) => {
      document.body.style.background = bg;
      document.getElementById('fig').style.background = bg;
      const el = document.getElementById('fig');
      el.innerHTML = '';
      const pre = document.createElement('pre');
      pre.className = 'mermaid';
      pre.textContent = s;
      el.appendChild(pre);
      mermaid.initialize({ startOnLoad: false, theme, fontFamily: 'Helvetica, Arial, sans-serif' });
      await mermaid.run({ nodes: [pre] });
      await document.fonts.ready;
    }, [src, v.theme, v.bg]);
    const png = `${OUT}/${NAMES[i]}${v.suffix}.png`;
    await page.locator('#fig').screenshot({ path: path.join(ROOT, png) });
    fig[v.key === 'light' ? 'png_sha256' : 'png_dark_sha256'] = sha(fs.readFileSync(path.join(ROOT, png)));
  }
  figures.push(fig);
}
await browser.close();
fs.writeFileSync(MANIFEST, JSON.stringify({ generator: `${OUT}/render_mermaid.mjs`, mermaid: version, source: 'README.md', figures }, null, 1) + '\n');
console.log(`rendered ${figures.length * 2} images with mermaid ${version}`);
