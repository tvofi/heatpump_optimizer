// The documentation sub-page generator (R9-WEB-3, ported from the design prototype). It renders the README and every
// row of the README Documentation table into one HTML page each, in the product page's design, with markdown-it
// 14.1.0, the parser the repository already vendors at .claude/workflows/vendor/ (the path render_md.mjs requires).
// The docs stay the only source: nothing here is hand-written per document, so a page cannot say what its markdown
// does not. Nothing it makes is tracked: it writes only into the directory it is given, and the Pages workflow runs it
// at deploy (S7).
//
//   node tools/site/build_docs.mjs --root CHECKOUT --tree TREE.txt --out OUT [--mermaid PATH|native|none]
//
// CHECKOUT holds README.md and docs/; TREE.txt lists every tracked path (git ls-files), so a link to a file the site
// does not publish becomes a GitHub link and a link to nothing is an error. OUT stands for docs/ on the served site:
// pages land beside the product page (docs/index.html), and the images they reference keep their docs/ paths. Pages
// link the stylesheet at site/docs.css, which is docs/site/docs.css in the tree.
//
// The build is also the check. It exits 1, printing one FAIL line per failure, on: a README Documentation row whose
// file does not exist, or an EXCLUDE entry that is no longer a row; an image that does not resolve; a relative link to
// a file that is not tracked; an anchor to a heading the target page does not have; a third-party image or raw-HTML
// resource (badges render as their words); two documents with one page name; an untracked stylesheet; and the anchor,
// zero pages built.
import fs from 'node:fs'
import path from 'node:path'
import { createRequire } from 'node:module'
import { fileURLToPath } from 'node:url'

const require = createRequire(import.meta.url)
const _vendorOld = new URL('../../.claude/workflows/vendor/markdown-it.min.js', import.meta.url)
const _vendorNew = new URL('../policy/vendor/markdown-it.min.js', import.meta.url)
const MarkdownIt = require(fileURLToPath(fs.existsSync(_vendorOld) ? _vendorOld : _vendorNew))

const args = Object.fromEntries(process.argv.slice(2).reduce((a, v, i, all) => (v.startsWith('--') ? [...a, [v.slice(2), all[i + 1]]] : a), []))
const ROOT = args.root, OUT = args.out, MERMAID = args.mermaid || 'site/mermaid/mermaid.min.js'
const TREE = new Set(fs.readFileSync(args.tree, 'utf8').split('\n').filter(Boolean))
const TREE_DIRS = new Set([...TREE].flatMap((p) => p.split('/').slice(0, -1).map((_, i, a) => a.slice(0, i + 1).join('/'))))
const BLOB = 'https://github.com/tvofi/heatpump_optimizer/blob/main/'
const TREEURL = 'https://github.com/tvofi/heatpump_optimizer/tree/main/'
// Rows of the README Documentation table the site links to GitHub instead of rendering, each with its reason.
const EXCLUDE = { 'docs/backlog.md': 'an archive of what was built, not a reader doc (R9-RO-4 archives it)' }
const errors = []
const stats = { pages: 0, pageLinks: 0, anchors: 0, githubLinks: 0, images: 0, badges: 0, external: 0, mermaid: 0 }

// ---- which documents: the README Documentation table, both ways ----
const readme = fs.readFileSync(path.join(ROOT, 'README.md'), 'utf8')
const docSec = readme.split(/^## Documentation\s*$/m)[1]?.split(/^## /m)[0] || ''
const allRows = [...docSec.matchAll(/^\|\s*\[[^\]]+\]\(([^)#]+)\)\s*\|\s*(.+?)\s*\|\s*$/gm)].map((m) => ({ src: m[1], blurb: m[2] }))
// A row naming an .html file is the product page itself (docs/index.html): the site's front, not rendered from markdown.
const rows = allRows.filter((r) => /\.md$/i.test(r.src))
if (rows.length) for (const x of Object.keys(EXCLUDE)) if (!rows.some((r) => r.src === x)) errors.push(`EXCLUDE names ${x}, which the README Documentation table no longer lists`)
const docs = [{ src: 'README.md', blurb: 'The overview: features, requirements, installation, entities, services and troubleshooting' }]
for (const r of rows) if (!EXCLUDE[r.src]) docs.push(r)
const outName = (src) => (src === 'README.md' ? 'readme.html' : path.posix.basename(src).replace(/\.md$/i, '.html').toLowerCase())
const PUBLISHED = new Map(docs.map((d) => [d.src, outName(d.src)]))
if (!rows.length) errors.push('ANCHOR: no rows found in the README Documentation table')
if (new Set(PUBLISHED.values()).size !== PUBLISHED.size) errors.push('two documents would be built to one page name')
if (!TREE.has('docs/site/docs.css')) errors.push('docs/site/docs.css is not tracked; the pages link it')

// ---- markdown-it with GitHub's heading slugs, callouts, figures, tables and mermaid ----
const md = new MarkdownIt({ html: true, linkify: false, typographer: false })
const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
const slugify = (t) => t.trim().toLowerCase().replace(/[^\p{L}\p{N}_\- ]/gu, '').replace(/ /g, '-')
const inlineText = (tok) => (tok.children || []).filter((c) => c.type === 'text' || c.type === 'code_inline').map((c) => c.content).join('')

md.core.ruler.push('gh_slugs', (state) => {
  const seen = new Map()
  const t = state.tokens
  for (let i = 0; i < t.length; i++) {
    if (t[i].type !== 'heading_open') continue
    const base = slugify(inlineText(t[i + 1]))
    const n = seen.get(base) || 0
    seen.set(base, n + 1)
    t[i].attrSet('id', n ? `${base}-${n}` : base)
  }
  // GitHub callouts: a blockquote whose first line is [!NOTE] / [!IMPORTANT] / ...
  for (let i = 0; i < t.length; i++) {
    if (t[i].type !== 'blockquote_open' || t[i + 2]?.type !== 'inline') continue
    const kids = t[i + 2].children || []
    const m = kids[0]?.type === 'text' && kids[0].content.match(/^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]$/)
    if (!m) continue
    t[i].attrJoin('class', 'callout')
    t[i].meta = { label: m[1][0] + m[1].slice(1).toLowerCase() }
    kids.splice(0, kids[1]?.type === 'softbreak' ? 2 : 1)
  }
})

let CUR = null // the source path being rendered
const slugsOf = new Map() // out page -> Set of heading ids
const pendingAnchors = [] // [fromSrc, outPage, fragment]

function resolveHref(href) {
  if (/^[a-z]+:/i.test(href) || href.startsWith('//')) { stats.external++; return { href, external: true } }
  const [p, frag] = href.split('#')
  if (!p) { pendingAnchors.push([CUR, outName(CUR), frag]); return { href } }
  const target = path.posix.normalize(path.posix.join(path.posix.dirname(CUR), decodeURI(p))).replace(/\/$/, '')
  if (PUBLISHED.has(target)) {
    stats.pageLinks++
    if (frag) pendingAnchors.push([CUR, PUBLISHED.get(target), frag])
    return { href: PUBLISHED.get(target) + (frag ? '#' + frag : '') }
  }
  if (target === 'docs/index.html') return { href: 'index.html' + (frag ? '#' + frag : '') }
  if (target.startsWith('docs/') && /\.(png|svg|jpe?g|gif|webp)$/i.test(target) && TREE.has(target)) return { href: target.slice(5) }
  if (TREE.has(target)) { stats.githubLinks++; return { href: BLOB + target + (frag ? '#' + frag : '') } }
  if (TREE_DIRS.has(target)) return { href: TREEURL + target }
  errors.push(`${CUR}: link to ${href} resolves to ${target}, which is not tracked`)
  return { href }
}

md.renderer.rules.link_open = (tokens, idx, opts, env, self) => {
  const r = resolveHref(tokens[idx].attrGet('href'))
  tokens[idx].attrSet('href', r.href)
  return self.renderToken(tokens, idx, opts)
}
md.renderer.rules.image = (tokens, idx) => {
  const tok = tokens[idx], src = tok.attrGet('src'), alt = tok.content
  if (/^(?:[a-z][a-z0-9+.-]*:|\/\/)/i.test(src)) { stats.badges++; return `<span class="badge">${esc(alt)}</span>` } // a badge or other third-party image: its words only
  const target = path.posix.normalize(path.posix.join(path.posix.dirname(CUR), src))
  if (!TREE.has(target) || !target.startsWith('docs/')) { errors.push(`${CUR}: image ${src} does not resolve under docs/`); return '' }
  stats.images++
  return `<img src="${esc(target.slice(5))}" alt="${esc(alt)}" loading="lazy">`
}
md.renderer.rules.paragraph_open = (tokens, idx, opts, env, self) => {
  const inl = tokens[idx + 1]
  const kids = inl?.children || []
  const only = kids.filter((k) => !(k.type === 'text' && !k.content.trim()))
  if (only.length === 1 && only[0].type === 'image' && !/^(?:[a-z][a-z0-9+.-]*:|\/\/)/i.test(only[0].attrGet('src'))) { tokens[idx].meta = 'fig'; return '<div class="fig">' }
  return self.renderToken(tokens, idx, opts)
}
md.renderer.rules.paragraph_close = (tokens, idx, opts, env, self) => {
  // the matching open is two tokens back for a one-image paragraph
  return tokens[idx - 2]?.meta === 'fig' ? '</div>\n' : self.renderToken(tokens, idx, opts)
}
md.renderer.rules.heading_open = (tokens, idx, opts, env, self) => {
  const id = tokens[idx].attrGet('id')
  return `${self.renderToken(tokens, idx, opts)}${tokens[idx].tag === 'h1' ? '' : `<a class="anchor" href="#${esc(id)}" aria-hidden="true" tabindex="-1">#</a>`}`
}
md.renderer.rules.blockquote_open = (tokens, idx, opts, env, self) => self.renderToken(tokens, idx, opts) + (tokens[idx].meta ? `<span class="label">${tokens[idx].meta.label}</span>` : '')
md.renderer.rules.table_open = () => '<div class="tbl"><table>\n'
md.renderer.rules.table_close = () => '</table></div>\n'
const defaultFence = md.renderer.rules.fence
md.renderer.rules.fence = (tokens, idx, opts, env, self) => {
  const tok = tokens[idx]
  if (tok.info.trim() === 'mermaid') { env.mermaid = true; stats.mermaid++; return `<pre class="mermaid">${esc(tok.content)}</pre>\n` }
  return defaultFence(tokens, idx, opts, env, self)
}
// Raw HTML passes through, so it is the one way a document could still ask another origin for something (S11).
const RAW_EXTERNAL = /<(?:img|script|iframe|source|embed|object|link)\b[^>]*\b(?:src|srcset|href|data)\s*=\s*["']?(?:[a-z][a-z0-9+.-]*:|\/\/)/i
for (const rule of ['html_block', 'html_inline']) {
  md.renderer.rules[rule] = (tokens, idx) => {
    if (RAW_EXTERNAL.test(tokens[idx].content)) errors.push(`${CUR}: raw HTML requests a third-party resource: ${tokens[idx].content.trim().slice(0, 80)}`)
    return tokens[idx].content
  }
}

// ---- render ----
const MARK = '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><symbol id="dusk" viewBox="0 0 48 48"><path d="M20 22 V26 H27 V35 H36 V22 Z" fill="var(--mk-heat)"/><path d="M6 12 H13 V19 H20 V26 H27 V35 H36 V13 H42" fill="none" stroke="var(--mk-line)" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></symbol></svg>'
const THEME_JS = `(()=>{const r=document.documentElement,b=document.getElementById("theme"),mq=matchMedia("(prefers-color-scheme: dark)");let s=null;try{s=localStorage.getItem("hpo-theme")}catch(e){}const dark=()=>r.dataset.theme?r.dataset.theme==="dark":mq.matches;function a(t){if(t)r.dataset.theme=t;else delete r.dataset.theme;b.setAttribute("aria-label",dark()?"Switch to light theme":"Switch to dark theme")}a(s);b.addEventListener("click",()=>{const t=dark()?"light":"dark";a(t);try{localStorage.setItem("hpo-theme",t)}catch(e){};if(window.__mermaidRedraw)window.__mermaidRedraw()});const d=document.querySelector("nav.side details");if(d&&matchMedia("(max-width: 900px)").matches)d.open=false})();`

const rendered = docs.map((d) => {
  CUR = d.src
  const env = {}
  if (!fs.existsSync(path.join(ROOT, d.src))) { errors.push(`README Documentation row ${d.src} names a file that does not exist`); return null }
  const src = fs.readFileSync(path.join(ROOT, d.src), 'utf8')
  const tokens = md.parse(src, env)
  const h1 = tokens.findIndex((t) => t.type === 'heading_open' && t.tag === 'h1')
  const title = h1 >= 0 ? inlineText(tokens[h1 + 1]) : d.src
  const h2 = tokens.flatMap((t, i) => (t.type === 'heading_open' && t.tag === 'h2' ? [[t.attrGet('id'), inlineText(tokens[i + 1])]] : []))
  const firstP = tokens.findIndex((t) => t.type === 'paragraph_open')
  const desc = firstP >= 0 ? inlineText(tokens[firstP + 1]).replace(/\s+/g, ' ').slice(0, 180) : title
  const html = md.renderer.render(tokens, md.options, env)
  slugsOf.set(outName(d.src), new Set(tokens.filter((t) => t.type === 'heading_open').map((t) => t.attrGet('id'))))
  return { ...d, out: outName(d.src), title, h2, desc, html, mermaid: !!env.mermaid }
}).filter(Boolean)
for (const [from, page, frag] of pendingAnchors) {
  stats.anchors++
  const ids = slugsOf.get(page)
  if (ids && frag && !ids.has(decodeURIComponent(frag).toLowerCase())) errors.push(`${from}: anchor #${frag} is not a heading of ${page}`)
}

// The rail names a page by its own h1, less the product name; the README is named as what it is.
const navLabel = (r) => {
  if (r.src === 'README.md') return 'Overview (README)'
  const t = r.title.replace(/^Heat Pump (Cost )?Optimizer:? ?/, '') || r.title
  return t[0].toUpperCase() + t.slice(1)
}
const sideNav = (cur) => rendered.map((r) => `<li><a href="${r.out}"${r.out === cur ? ' aria-current="page"' : ''}>${esc(navLabel(r))}</a></li>`).join('')
const mermaidJs = (on) => {
  if (!on || MERMAID === 'none' || MERMAID === 'native') return ''
  // one self-hosted UMD file, loaded only on pages that draw a diagram, redrawn in the other theme on toggle
  return `<script src="${MERMAID}" defer></script><script>addEventListener("DOMContentLoaded",()=>{const r=document.documentElement,dark=()=>r.dataset.theme?r.dataset.theme==="dark":matchMedia("(prefers-color-scheme: dark)").matches,pre=[...document.querySelectorAll("pre.mermaid")],src=pre.map(p=>p.textContent);async function draw(){pre.forEach((p,i)=>{p.removeAttribute("data-processed");p.textContent=src[i]});mermaid.initialize({startOnLoad:false,theme:dark()?"dark":"neutral",fontFamily:"Source Sans 3, system-ui, sans-serif"});await mermaid.run({nodes:pre})}window.__mermaidRedraw=draw;draw()})</script>`
}
const disclaimer = PUBLISHED.get('DISCLAIMER.md') || null
fs.mkdirSync(OUT, { recursive: true })
rendered.forEach((r, i) => {
  const prev = rendered[i - 1], next = rendered[i + 1]
  const page = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>${esc(r.title)} · Heat Pump Cost Optimizer</title>
<meta name="description" content="${esc(r.desc)}">
<link rel="stylesheet" href="site/docs.css">
</head>
<body>
${MARK}
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="bar">
  <a class="brand" href="index.html"><svg aria-hidden="true"><use href="#dusk"/></svg><span>Heat Pump Cost Optimizer</span></a>
  <nav class="links" aria-label="Site"><a href="index.html">Overview</a><a href="${rendered[1]?.out || 'readme.html'}" aria-current="true">Documentation</a><a href="index.html#install">Get started</a></nav>
  <div class="act"><button class="iconbtn" id="theme" type="button" aria-label="Switch to dark theme"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg></button>
  <a class="iconbtn" href="https://github.com/tvofi/heatpump_optimizer" aria-label="Source on GitHub"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 .5a11.5 11.5 0 0 0-3.64 22.41c.58.1.79-.25.79-.56v-2c-3.2.7-3.88-1.37-3.88-1.37-.52-1.33-1.28-1.69-1.28-1.69-1.05-.72.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.77 2.7 1.26 3.36.96.1-.75.4-1.26.73-1.55-2.55-.29-5.24-1.28-5.24-5.7 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.17 1.18a11 11 0 0 1 5.77 0c2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.23 2.76.11 3.05.74.81 1.19 1.84 1.19 3.1 0 4.43-2.7 5.4-5.26 5.69.41.36.78 1.06.78 2.14v3.17c0 .31.21.67.8.56A11.5 11.5 0 0 0 12 .5z"/></svg></a></div>
</div></header>
<div class="docwrap">
<nav class="side" aria-label="Documentation"><details open><summary class="eyebrow">Documentation</summary><ol>${sideNav(r.out)}</ol></details></nav>
<main id="main" class="prose">
<p class="eyebrow">Documentation</p>
${r.html}
<nav class="pn" aria-label="Previous and next">${prev ? `<a class="prev" href="${prev.out}"><span>Previous</span><b>${esc(prev.title)}</b></a>` : ''}${next ? `<a class="next" href="${next.out}"><span>Next</span><b>${esc(next.title)}</b></a>` : ''}</nav>
<p class="src">Rendered from <a href="${BLOB}${r.src}">${r.src}</a>, which is the source of truth; this page changes only when that file does.</p>
</main>
${r.h2.length >= 3 ? `<aside class="toc" aria-label="On this page"><p class="eyebrow">On this page</p><ol>${r.h2.map(([id, t]) => `<li><a href="#${esc(id)}">${esc(t)}</a></li>`).join('')}</ol></aside>` : '<span></span>'}
</div>
<footer class="site"><div class="bar"><a class="brand" href="index.html"><svg aria-hidden="true" style="width:24px;height:24px"><use href="#dusk"/></svg><span>Heat Pump Cost Optimizer</span></a><a href="https://github.com/tvofi/heatpump_optimizer">GitHub</a><a href="${BLOB}LICENSE">MIT License</a><a href="${disclaimer || BLOB + 'DISCLAIMER.md'}">Disclaimer</a></div></footer>
<script>${THEME_JS}</script>
${mermaidJs(r.mermaid)}
</body>
</html>
`
  fs.writeFileSync(path.join(OUT, r.out), page)
})
stats.pages = rendered.length
if (!rendered.length) errors.push('ANCHOR: zero pages built')
fs.writeFileSync(path.join(OUT, 'docs-manifest.json'), JSON.stringify({ built: rendered.map((r) => ({ src: r.src, out: r.out, mermaid: r.mermaid })), excluded: EXCLUDE }, null, 1))
console.log(Object.entries(stats).map(([k, v]) => `${k} ${v}`).join(', '))
console.log(`built ${rendered.length} page(s): ${rendered.map((r) => r.out).join(', ')}; excluded ${Object.keys(EXCLUDE).join(', ') || 'none'}`)
for (const e of errors) console.log('FAIL', e)
console.log('RESULT:', errors.length ? `${errors.length} failure(s)` : 'PASS')
process.exit(errors.length ? 1 : 0)
