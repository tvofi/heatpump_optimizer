// R10-README-GRAPHICS: does README.md survive the Home Assistant Marketplace's markdown pipeline?
//
//   npm install --prefix "$DIR" marked@15.0.4 xss@1.0.15          # not repository dependencies
//   HPO_PIPELINE_MODULES=$DIR/node_modules node dev/audit/harnesses/r10_readme_marketplace_pipeline.mjs [--readme FILE]
//
// A REPLICA, not the shipped bundle: the finder measured homeassistant 2026.11.0b1 and home-assistant-frontend
// 20261028.1 and transcribed three stages. The stages, in the order the frontend runs them:
//   1. marked (gfm) turns the README into HTML (frontend src/resources/markdown-worker.ts);
//   2. js-xss filterXSS sanitizes it with the default allow-list plus `picture` and `source[src,srcset,sizes,media,type]`
//      (markdown-worker.ts:55-74); a `srcset` survives only when every candidate's URL passes the same test, else the whole
//      attribute is dropped (markdown-worker.ts:21-43). Its default safeAttrValue keeps an `src`/`href` only when it starts with http://,
//      https://, mailto:, tel:, data:image/, ftp://, ./, ../, # or /; anything else becomes "" (xss lib/default.js:176-194);
//   3. src/common/dom/rewrite-html-urls.ts:29-56 then resolves every a[href], img[src] and source[src|srcset] that is not absolute, `#` or `//`
//      against https://raw.githubusercontent.com/<repo>/<ref>/ (a .md target: https://github.com/<repo>/blob/<ref>/).
// So a bare `docs/x.png` is blanked in stage 2 and stage 3 turns the blank into the ref's directory, which is no image.
//
// Metric: every image and link README.md writes as repository-relative must end at <base>/<its own path>; every mermaid
// fence arrives as a plain <pre><code> because stage 2 drops its language class (no mermaid exists in the frontend).
//   RESULT relative_images=<n> resolved=<k>      -- red when k < n
//   RESULT relative_links=<n> resolved=<k>       -- red when k < n
//   RESULT absolute_images=<n> resolved=<k>      -- the null control: an absolute URL passes at every ref
//   RESULT picture_sources=<n> resolved=<k>      -- each <source srcset> (the dark PNG) ends at <base>/<its own path>
//   RESULT mermaid_fences=<n> plain_code=<k>     -- informational; fences are why the figures are committed PNGs
//   RESULT control bare=<blank|ok> dot=<blank|ok> absolute=<blank|ok>   -- the harness can go red: bare blank, dot and absolute ok
//   RESULT control srcset_bare=<stripped|kept> srcset_dot=<stripped|kept> light_img=<ok|blank>
//                                  -- a bare srcset is dropped while the light <img> of the same <picture> still resolves;
//                                     a ./ srcset is kept and resolved
// GitHub's own switching is not replicated here (it is GitHub's renderer): README.md's <picture> is the form GitHub documents.
// Exit 1 when any relative image, link or source is blank, or a control reads wrong; 0 otherwise. Red at the merge base, green at
// the head. --readme FILE reads another README (e.g. `git show origin/main:README.md > FILE`).
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const modules = process.env.HPO_PIPELINE_MODULES;
if (!modules) throw new Error("set HPO_PIPELINE_MODULES to a node_modules directory holding marked@15.0.4 and xss@1.0.15");
const req = createRequire(path.join(modules, "x.js"));
const { marked } = req("marked");
const xss = req("xss");

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const arg = process.argv.indexOf("--readme");
const readmePath = arg > 0 ? process.argv[arg + 1] : path.join(root, "README.md");
const BASE = "https://raw.githubusercontent.com/tvofi/heatpump_optimizer/v7.1.0/";
const BLOB = "https://github.com/tvofi/heatpump_optimizer/blob/v7.1.0/";

const whiteList = { ...xss.getDefaultWhiteList(), picture: [], source: ["src", "srcset", "sizes", "media", "type"] };
const srcsetSafe = (v) => v.split(",").every((c) => xss.safeAttrValue("img", "src", (c.trim().split(/\s+/)[0] || ""), {}) !== "");
const sanitizer = new xss.FilterXSS({
  whiteList, safeAttrValue: (tag, name, value, css) => (name === "srcset" ? (srcsetSafe(value) ? value : "") : xss.safeAttrValue(tag, name, value, css)),
});
const rewriteUrl = (v) => {  // export `E`: absolute, `#` and `//` stay; the rest resolves against the pinned ref
  if (/^[a-z][a-z0-9+.-]*:/i.test(v) || v.startsWith("#") || v.startsWith("//")) return v;
  return new URL(v, /\.md(?:$|[#?])/i.test(v) ? BLOB : BASE).href;
};
const rewriter = new xss.FilterXSS({
  whiteList, onTagAttr: (tag, name, value) => {
    const v = value.replace(/^"|"$/g, "");
    if ((name === "src" || name === "href") && (tag === "img" || tag === "a")) return `${name}="${rewriteUrl(v)}"`;
    if (tag === "source" && (name === "src" || name === "srcset"))
      return `${name}="${v.split(",").map((c) => c.trim().replace(/^\S+/, rewriteUrl)).join(", ")}"`;
    return undefined;
  },
});
const attrs = (html, tag, name) => [...html.matchAll(new RegExp(`<${tag}\\b[^>]*?\\s${name}="([^"]*)"`, "g"))].map((m) => m[1]);
const pipeline = (md) => {
  const raw = marked.parse(md, { gfm: true });
  return { raw, out: rewriter.process(sanitizer.process(raw)) };
};
const isAbs = (v) => /^[a-z][a-z0-9+.-]*:/i.test(v) || v.startsWith("//") || v.startsWith("#");
// a target resolves when the pipeline's result is exactly what GitHub would resolve it to
const measure = (md, tag, name) => {
  const { raw, out } = pipeline(md);
  const want = attrs(raw, tag, name), got = attrs(out, tag, name);
  const rows = want.map((w, i) => ({ w, ok: got[i] === rewriteUrl(w.replaceAll("&amp;", "&")) && got[i] !== BASE && got[i] !== BLOB }));
  return { rel: rows.filter((r) => !isAbs(r.w)), abs: rows.filter((r) => isAbs(r.w)) };
};

const readme = fs.readFileSync(readmePath, "utf8");
const sources = measure(readme, "source", "srcset");
const imgs = measure(readme, "img", "src"), links = measure(readme, "a", "href");
const n = (rows) => `${rows.length} resolved=${rows.filter((r) => r.ok).length}`;
console.log(`RESULT relative_images=${n(imgs.rel)}`);
console.log(`RESULT relative_links=${n(links.rel)}`);
console.log(`RESULT absolute_images=${n(imgs.abs)}`);
console.log(`RESULT picture_sources=${n(sources.rel)}`);
const { raw, out } = pipeline(readme);
const fences = (raw.match(/<code class="language-mermaid"/g) || []).length;
const plain = (out.match(/<pre><code>(?:flowchart|sequenceDiagram|graph)/g) || []).length;
console.log(`RESULT mermaid_fences=${fences} plain_code=${plain}`);

const ctl = (md) => (measure(md, "img", "src").rel.concat(measure(md, "img", "src").abs)[0]?.ok ? "ok" : "blank");
const control = { bare: ctl("![a](docs/x.png)"), dot: ctl("![a](./docs/x.png)"), absolute: ctl("![a](https://example.com/x.png)") };
console.log(`RESULT control bare=${control.bare} dot=${control.dot} absolute=${control.absolute}`);
const pic = (src) => pipeline(`<picture>\n<source media="(prefers-color-scheme: dark)" srcset="${src}">\n<img src="./docs/l.png" alt="a">\n</picture>\n`).out;
const sBare = pic("docs/d.png"), sDot = pic("./docs/d.png");
const sControl = { bare: /<source[^>]*srcset="[^"]+"/.test(sBare) ? "kept" : "stripped", dot: sDot.includes(`srcset="${BASE}docs/d.png"`) ? "kept" : "stripped",
  light: sBare.includes(`<img src="${BASE}docs/l.png"`) && sDot.includes(`<img src="${BASE}docs/l.png"`) ? "ok" : "blank" };
console.log(`RESULT control srcset_bare=${sControl.bare} srcset_dot=${sControl.dot} light_img=${sControl.light}`);
const controlsRight = control.bare === "blank" && control.dot === "ok" && control.absolute === "ok"
  && sControl.bare === "stripped" && sControl.dot === "kept" && sControl.light === "ok";
const red = imgs.rel.some((r) => !r.ok) || sources.rel.some((r) => !r.ok) || links.rel.some((r) => !r.ok) || imgs.abs.some((r) => !r.ok);
process.exit(red || !controlsRight ? 1 : 0);
