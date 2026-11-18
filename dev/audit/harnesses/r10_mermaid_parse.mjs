// usage: NODE_PATH=$(npm root -g) node dev/audit/harnesses/r10_mermaid_parse.mjs <tools/site dir> <file.md>... -- mermaid.parse in Chromium, with the pinned mermaid.min.js
// R10-ARCH-DOCS-FIRST item T1a: parse and render every ```mermaid block of the named files with the pinned
// mermaid (run `npm ci` in tools/site first), in Chromium, because mermaid.parse needs a DOM. Exit 1 on any failure.
// The gate does not run this: wiring a real parse into a check is R10-ARCH-DOCS (item T1).
import fs from 'node:fs'
import path from 'node:path'
import { createRequire } from 'node:module'
const require = createRequire(import.meta.url) // playwright resolves through NODE_PATH
const { chromium } = require('playwright')
const [site, ...files] = process.argv.slice(2)
const lib = fs.readFileSync(path.join(site, 'node_modules/mermaid/dist/mermaid.min.js'), 'utf8')
const version = JSON.parse(fs.readFileSync(path.join(site, 'node_modules/mermaid/package.json'))).version
const browser = await chromium.launch()
const page = await browser.newPage()
await page.setContent('<!doctype html><html><body></body></html>')
await page.addScriptTag({ content: lib })
let bad = 0, n = 0
for (const f of files) {
  const blocks = [...fs.readFileSync(f, 'utf8').matchAll(/^```mermaid\n([\s\S]*?)^```/gm)].map((m) => m[1])
  for (const [i, b] of blocks.entries()) {
    n++
    const r = await page.evaluate(async (src) => {
      try { await mermaid.parse(src); const { svg } = await mermaid.render('m' + Math.random().toString(36).slice(2), src); return svg.length ? 'ok' : 'empty render' }
      catch (e) { return 'FAIL ' + String(e.message || e).split('\n').slice(0, 4).join(' | ') }
    }, b)
    if (r !== 'ok') bad++
    console.log(`${r === 'ok' ? 'ok  ' : ''} ${r === 'ok' ? '' : r + ' :: '}${f} block ${i + 1}`)
  }
}
console.log(`mermaid ${version} parse+render in Chromium: ${n} block(s), ${bad} failure(s)`)
await browser.close()
process.exit(bad ? 1 : 0)
