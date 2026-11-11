// R10-PRODUCT-PAGE-REDESIGN (#201): the design note's acceptance list for
// docs/index.html, the part that needs the two trees or a browser (checks 4-11
// of design/R10-PRODUCT-PAGE-REDESIGN, section 10; checks 1-3 are
// tests/doc_claims.py and tools/site/day_chart.mjs themselves).
//
//    node dev/audit/harnesses/r10_product_page.mjs [--base <ref>]
//
// playwright is resolved from NODE_PATH and Chromium from
// PLAYWRIGHT_BROWSERS_PATH, as tests/card_browser.mjs does. The working tree's
// docs/ is served from a loopback port (so the page's own fonts and images load
// and every request is seen); the base page is read with `git show <ref>` and
// served from memory beside it. <ref> defaults to the merge base with
// origin/main.
//
// One line per check: `ok` or `FAIL`, then what was measured. Exit 1 on any
// FAIL. EXPECTED at a head that meets the note: RESULT fails=0
//
// What it does not establish: one engine (Chromium); no screen reader; touch is
// not exercised; a browser without :has() is not simulated (the rule under
// `@supports not selector(:has(*))` is read as text only).
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..", "..");
const DOCS = path.join(ROOT, "docs");
const git = (...a) => execFileSync("git", a, { cwd: ROOT, encoding: "utf8", maxBuffer: 1 << 26 });
const at = process.argv.indexOf("--base");
const BASE_REF = at >= 0 ? process.argv[at + 1] : git("merge-base", "origin/main", "HEAD").trim();
const HEAD_SRC = fs.readFileSync(path.join(DOCS, "index.html"), "utf8");
const BASE_SRC = git("show", `${BASE_REF}:docs/index.html`);

const WIDTHS = [360, 390, 768, 1440];
const THEMES = ["light", "dark"];
const ANCHORS = ["top", "main", "how", "card", "features", "works-with", "install", "limits", "ai", "docs"];
const SIZE_CAP = 70000;

let fails = 0;
function check(name, pass, detail = "") {
  if (!pass) fails++;
  console.log(`${pass ? "ok  " : "FAIL"} ${name}${detail ? "  [" + detail + "]" : ""}`);
}

// ---- static: links, anchors, embedding, size (checks 4-6)
const hrefs = src => [...new Set(src.match(/href="[^"#][^"]*"/g) || [])].sort();
const hb = hrefs(BASE_SRC), hh = hrefs(HEAD_SRC);
const gone = hb.filter(h => !hh.includes(h)), added = hh.filter(h => !hb.includes(h));
check("4 links: the set of non-fragment href values is the base's", !gone.length && !added.length && hb.length > 0,
  `${hh.length} at the head, ${hb.length} at the base; gone ${JSON.stringify(gone)}; added ${JSON.stringify(added)}`);
const counts = ANCHORS.map(id => [id, (HEAD_SRC.match(new RegExp(`\\sid="${id}"`, "g")) || []).length]);
check("5 anchors: each of the ten ids appears exactly once", counts.every(([, n]) => n === 1), counts.map(([i, n]) => `${i}=${n}`).join(" "));
const bytes = Buffer.byteLength(HEAD_SRC);
check("6 nothing embedded: no data: address", !/data:/.test(HEAD_SRC));
check(`6 size: the page is under ${SIZE_CAP} bytes`, bytes < SIZE_CAP, `${bytes} bytes; the base is ${Buffer.byteLength(BASE_SRC)}`);
check("fallback rule present: without :has() every control-path answer and its name is displayed (text only)",
  /@supports not selector\(:has\(\*\)\) \{ \.cp \.pp \{ display: grid[^}]*\} \}/.test(HEAD_SRC)
  && /@supports not selector\(:has\(\*\)\) \{ \.cp \.pph \{ display: block \} \}/.test(HEAD_SRC));

// ---- the server
const TYPES = { ".html": "text/html; charset=utf-8", ".woff2": "font/woff2", ".png": "image/png", ".svg": "image/svg+xml", ".css": "text/css" };
const server = http.createServer((req, res) => {
  const url = new URL(req.url, "http://x");
  if (url.pathname === "/__base.html") { res.writeHead(200, { "content-type": TYPES[".html"] }); res.end(BASE_SRC); return; }
  const rel = url.pathname === "/" ? "index.html" : decodeURIComponent(url.pathname.slice(1));
  const file = path.join(DOCS, rel);
  if (!file.startsWith(DOCS + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { "content-type": TYPES[path.extname(file)] || "application/octet-stream" });
  res.end(fs.readFileSync(file));
});
await new Promise(r => server.listen(0, "127.0.0.1", r));
const ORIGIN = `http://127.0.0.1:${server.address().port}`;

const FONTS = [...HEAD_SRC.matchAll(/url\((site\/fonts\/[^)]+)\)/g)].map(m => "/" + m[1]);
const IMAGES = [...HEAD_SRC.matchAll(/(?:src|srcset)="(img\/[^"]+)"/g)].map(m => "/" + m[1]);
const ALLOWED = new Set(["/", ...FONTS, ...IMAGES]);

const browser = await chromium.launch();
async function open(opts = {}, url = "/", init = null) {
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, ...opts });
  const page = await ctx.newPage();
  const seen = { console: [], requests: [] };
  page.on("console", m => seen.console.push(`${m.type()}: ${m.text()}`));
  page.on("pageerror", e => seen.console.push(`pageerror: ${e.message}`));
  page.on("request", r => seen.requests.push(r.url()));
  if (init) await page.addInitScript(init);
  await page.goto(ORIGIN + url, { waitUntil: "load" });
  return { ctx, page, seen };
}
const settle = (page, ms = 250) => page.waitForTimeout(ms);
/** Walk the whole page so every lazy image and every reveal has had its turn. */
async function walk(page) {
  const h = await page.evaluate(() => document.documentElement.scrollHeight);
  const step = Math.max(200, Math.floor((page.viewportSize().height) * 0.6));
  for (let y = 0; y <= h; y += step) { await page.evaluate(v => scrollTo({ top: v, behavior: "instant" }), y); await settle(page, 60); }
  await page.evaluate(() => scrollTo({ top: 0, behavior: "instant" }));
  await settle(page);
}

// ---- 7: every text node under a source mark at the base is still on the page
{
  const texts = async url => {
    const { ctx, page } = await open({}, url);
    const out = await page.evaluate(() => {
      const norm = s => s.replace(/\s+/g, " ").trim();
      const marked = [], w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      for (let n = w.nextNode(); n; n = w.nextNode()) {
        const t = norm(n.data), owner = n.parentElement.closest("[data-src],[data-copy]");
        if (t && owner && owner.hasAttribute("data-src") && !n.parentElement.closest("script,style,svg")) marked.push(t);
      }
      return { marked, alts: [...document.images].map(i => norm(i.alt)), all: norm(document.body.textContent) };
    });
    await ctx.close();
    return out;
  };
  const base = await texts("/__base.html"), head = await texts("/");
  const headAlts = new Set(head.alts);
  const lostText = [...new Set(base.marked.filter(t => !head.all.includes(t)))];
  const lostAlt = base.alts.filter(a => !headAlts.has(a));
  check("7 sentences: every text node under a source mark at the base is on the page at the head",
    lostText.length === 0, `${base.marked.length} marked nodes at the base; missing ${JSON.stringify(lostText)}`);
  check("7 pictures: the only alternative text gone is the removed how-it-works picture's",
    lostAlt.length === 1 && lostAlt[0].startsWith("One optimization interval"), `gone ${JSON.stringify(lostAlt.map(a => a.slice(0, 60)))}`);
}

// ---- 8: widths x themes; no overflow, no console message, no request beyond the page's own
for (const width of WIDTHS) for (const theme of THEMES) {
  const { ctx, page, seen } = await open({ viewport: { width, height: 800 }, colorScheme: theme });
  await walk(page);
  const m = await page.evaluate(() => ({
    sw: document.documentElement.scrollWidth, iw: innerWidth,
    bg: getComputedStyle(document.body).backgroundColor,
    lazy: [...document.images].filter(i => i.getClientRects().length && (!i.complete || !i.naturalWidth)).map(i => i.getAttribute("src")),
    small: [...document.querySelectorAll("a.btn, button, .cp .opts label, a.iconbtn")]
      .filter(e => e.getClientRects().length).map(e => [e.textContent.trim().slice(0, 24) || e.getAttribute("aria-label"), Math.round(e.getBoundingClientRect().height)])
      .filter(([, h]) => h < 40),
  }));
  const paths = seen.requests.map(u => new URL(u)).map(u => (u.origin === ORIGIN ? u.pathname : u.href));
  const foreign = [...new Set(paths.filter(p => !ALLOWED.has(p)))];
  const tag = `${width}px ${theme}`;
  check(`8 ${tag}: scroll width equals window width`, m.sw === m.iw, `scrollWidth ${m.sw}, innerWidth ${m.iw}`);
  check(`8 ${tag}: no console message`, seen.console.length === 0, seen.console.slice(0, 3).join(" | "));
  check(`8 ${tag}: no request but the page, its fonts and its images`, foreign.length === 0 && paths.includes("/"),
    `${new Set(paths).size} distinct; other ${JSON.stringify(foreign)}`);
  check(`8 ${tag}: every image with a box loaded, theme background ${m.bg}`, m.lazy.length === 0 && m.bg === (theme === "dark" ? "rgb(11, 26, 40)" : "rgb(243, 248, 252)"), JSON.stringify(m.lazy));
  check(`floor ${tag}: buttons, tabs and chooser pills are at least 40 px tall`, m.small.length === 0, JSON.stringify(m.small));
  await ctx.close();
}

// ---- contrast floor, from the page's own tokens in each theme
for (const theme of THEMES) {
  const { ctx, page } = await open({ colorScheme: theme });
  const worst = await page.evaluate(() => {
    const cs = getComputedStyle(document.documentElement), v = n => cs.getPropertyValue(n).trim();
    const lum = hex => { const c = [1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16) / 255).map(x => (x <= .03928 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4)); return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]; };
    const ratio = (a, b) => { const [x, y] = [lum(v(a)), lum(v(b))].sort((p, q) => q - p); return (x + .05) / (y + .05); };
    const body = [["--ink", "--bg"], ["--ink", "--surface"], ["--ink", "--well"], ["--ink-2", "--bg"], ["--ink-2", "--surface"], ["--ink-2", "--well"], ["--ink-2", "--hero-a"],
      ["--accent", "--surface"], ["--accent", "--bg"], ["--accent", "--well"], ["--accent-ink", "--accent"], ["--heat", "--surface"]];
    return { body: body.map(([a, b]) => [`${a} on ${b}`, +ratio(a, b).toFixed(2)]).sort((p, q) => p[1] - q[1])[0], title: +Math.min(ratio("--heat", "--hero-a"), ratio("--heat", "--hero-b")).toFixed(2) };
  });
  check(`floor ${theme}: every body text pair of tokens is at least 4.5 to 1`, worst.body[1] >= 4.5, `lowest ${worst.body[0]} = ${worst.body[1]}`);
  check(`floor ${theme}: the title's ember words are at least 3 to 1 on the hero wash`, worst.title >= 3, `${worst.title}`);
  await ctx.close();
}

// ---- 9: the story, down and back up, on the two-column and the one-column layout
const vizState = page => page.evaluate(() => ({
  s: [1, 2, 3, 4, 5].filter(i => document.getElementById("viz").classList.contains("s" + i)),
  on: [...document.querySelectorAll("#steps .st.on")].map(s => +s.dataset.step),
}));
for (const width of [1440, 390]) {
  const { ctx, page } = await open({ viewport: { width, height: 800 } });
  const centre = n => page.evaluate(k => {
    const r = document.querySelector(`#steps .st[data-step="${k}"]`).getBoundingClientRect();
    scrollTo({ top: scrollY + r.top + r.height / 2 - innerHeight / 2, behavior: "instant" });
  }, n);
  const got = [];
  for (const n of [1, 2, 3, 4, 5, 4, 3, 2, 1]) {
    await centre(n); await settle(page, 300);
    const st = await vizState(page);
    got.push([n, st.s.join(""), st.on.join("")]);
  }
  const want = n => "12345".slice(0, n);
  check(`9 ${width}px: step n at mid-viewport gives the chart exactly layers 1 to n, down and back up, and marks step n current`,
    got.every(([n, s, on]) => s === want(n) && on === String(n)), got.map(([n, s, on]) => `${n}:${s || "-"}/${on || "-"}`).join(" "));
  await page.evaluate(() => scrollTo({ top: 0, behavior: "instant" })); await settle(page, 300);
  const top = await vizState(page);
  const sticky = await page.evaluate(() => getComputedStyle(document.getElementById("viz")).position);
  check(`9 ${width}px: above the first step the chart is the bare grid, and the chart card is pinned`, top.s.length === 0 && top.on.length === 0 && sticky === "sticky", `layers ${top.s.join("") || "-"}, position ${sticky}`);
  await ctx.close();
}

// ---- 10: the fallback table
const layerState = () => {
  const vis = e => { const c = getComputedStyle(e); return +c.opacity === 1 && (c.transform === "none" || c.transform === "matrix(1, 0, 0, 1, 0, 0)"); };
  const anims = document.getAnimations();
  const q = s => [...document.querySelectorAll(s)];
  return {
    layers: q(".chart .lay").length, layersShown: q(".chart .lay").filter(vis).length,
    bars: q(".chart .bar").length, barsShown: q(".chart .bar").filter(vis).length,
    anims: anims.length, clock: anims.filter(a => a.timeline instanceof DocumentTimeline && a.playState === "running").length,
    transitions: q("body *").filter(e => getComputedStyle(e).transitionDuration.split(",").some(d => parseFloat(d) > 0)).length,
    progress: getComputedStyle(document.querySelector(".progress")).display,
    panels: q('#gallery [role="tabpanel"]').filter(e => getComputedStyle(e).display !== "none").length,
    tablist: getComputedStyle(document.querySelector(".seg")).display, theme: getComputedStyle(document.getElementById("theme")).display,
    viz: getComputedStyle(document.getElementById("viz")).position,
    s: [1, 2, 3, 4, 5].filter(i => document.getElementById("viz").classList.contains("s" + i)).join(""),
    on: q("#steps .st.on").length, stepH: Math.round(Math.max(...q("#steps .st").map(e => e.getBoundingClientRect().height))), vh: innerHeight,
    hiddenRv: q(".rv, .features .feat").filter(e => !vis(e)).length, sections: q("main section, .hero").filter(e => e.getClientRects().length).length,
  };
};
const choose = async page => {
  const out = [];
  for (const id of ["cp2", "cp3", "cp0", "cp1"]) {
    await page.locator(`label:has(#${id})`).click();
    out.push([id, await page.evaluate(() => [...document.querySelectorAll(".cp .pp")].filter(e => getComputedStyle(e).display !== "none").map(e => e.className.replace("pp ", "")).join(","))]);
  }
  return out;
};
const own = got => got.every(([id, shown]) => shown === "p" + id.slice(2));
for (const width of [1440, 390]) {
  const { ctx, page } = await open({ viewport: { width, height: 800 }, javaScriptEnabled: false });
  await walk(page); await settle(page, 3500);
  const m = await page.evaluate(layerState);
  const tag = `10 no script ${width}px`;
  check(`${tag}: all layers and bars are drawn at opacity 1`, m.layers === 7 && m.layersShown === 7 && m.bars > 0 && m.barsShown === m.bars, `${m.layersShown}/${m.layers} layers, ${m.barsShown}/${m.bars} bars`);
  check(`${tag}: no clock-driven animation is still running once the hero strip has drawn`, m.clock === 0, `${m.clock} running of ${m.anims} (the rest: the hero strip, finished, and the scroll-driven progress line)`);
  check(`${tag}: all four gallery panels are displayed; no tab list, no theme button`, m.panels === 4 && m.tablist === "none" && m.theme === "none", `${m.panels} panels, tab list ${m.tablist}, theme button ${m.theme}`);
  check(`${tag}: every section is visible and nothing waits for a reveal`, m.hiddenRv === 0 && m.sections === 9, `${m.hiddenRv} hidden, ${m.sections} sections with a box`);
  check(`${tag}: the steps are an ordinary list (${width < 900 ? "chart not pinned" : "chart pinned beside it"})`, m.stepH < m.vh * .5 && m.viz === (width < 900 ? "static" : "sticky"), `tallest step ${m.stepH}px of ${m.vh}px, chart position ${m.viz}`);
  const got = await choose(page);
  check(`${tag}: the chooser still works`, own(got), got.map(g => g.join("->")).join(" "));
  await ctx.close();
}
for (const width of [1440, 390]) {
  const { ctx, page, seen } = await open({ viewport: { width, height: 800 }, reducedMotion: "reduce" });
  await walk(page);
  const m = await page.evaluate(layerState);
  const tag = `10 reduced motion ${width}px`;
  check(`${tag}: the finished chart, pinned, no step marked current`, m.layersShown === 7 && m.barsShown === m.bars && m.s === "12345" && m.on === 0 && m.viz === "sticky", `layers ${m.s}, ${m.layersShown}/7 shown, ${m.on} current, position ${m.viz}`);
  check(`${tag}: no animation and no transition anywhere, no progress line`, m.anims === 0 && m.transitions === 0 && m.progress === "none", `${m.anims} animations, ${m.transitions} elements with a transition, progress ${m.progress}`);
  check(`${tag}: reveals at rest, a compact list, one gallery panel`, m.hiddenRv === 0 && m.stepH < m.vh * .5 && m.panels === 1, `${m.hiddenRv} hidden, tallest step ${m.stepH}px of ${m.vh}px, ${m.panels} panel`);
  check(`${tag}: no console message`, seen.console.length === 0, seen.console.slice(0, 3).join(" | "));
  await ctx.close();
}
{
  const { ctx, page, seen } = await open({}, "/", () => { delete window.IntersectionObserver; });
  await settle(page, 800);
  const m = await page.evaluate(layerState);
  const allIn = await page.evaluate(() => [...document.querySelectorAll(".rv")].every(e => e.classList.contains("in")));
  check("10 no intersection observer: the finished chart, every reveal at rest", m.s === "12345" && m.layersShown === 7 && allIn && m.hiddenRv === 0 && seen.console.length === 0, `layers ${m.s}, all reveals in ${allIn}, ${m.hiddenRv} hidden, ${seen.console.length} console`);
  await ctx.close();
}

// ---- 11: the chooser, the gallery keys, the theme switch, the chart's shape for assistive technology
{
  const { ctx, page } = await open({});
  const got = await choose(page);
  check("11 chooser: checking each radio displays exactly its own pane", own(got), got.map(g => g.join("->")).join(" "));
  await page.locator("#cp1").focus(); await page.keyboard.press("ArrowRight");
  const kb = await page.evaluate(() => ({ id: document.querySelector(".cp input:checked").id, ring: getComputedStyle(document.querySelector(".cp label:has(input:checked)")).outlineStyle, names: [...document.querySelectorAll(".cp .pph")].filter(e => getComputedStyle(e).display !== "none").length }));
  check("11 chooser: the arrow key moves to the next radio, the ring is drawn on its pill, no pane name shows while :has() works", kb.id === "cp2" && kb.ring === "solid" && kb.names === 0, JSON.stringify(kb));

  await page.locator("#t-why").focus();
  const keys = [];
  for (const k of ["End", "Home", "ArrowLeft", "ArrowRight"]) {
    await page.keyboard.press(k);
    keys.push([k, await page.evaluate(() => [document.activeElement.id, [...document.querySelectorAll('#gallery [role="tabpanel"]')].filter(e => !e.hidden).map(e => e.id).join(",")].join("/"))]);
  }
  check("gallery: End, Home and the arrows select a tab and show only its panel",
    JSON.stringify(keys.map(k => k[1])) === JSON.stringify(["t-opt/p-opt", "t-why/p-why", "t-opt/p-opt", "t-why/p-why"]), keys.map(k => k.join("=")).join(" "));

  const before = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  await page.locator("#theme").click();
  const th = await page.evaluate(() => ({ bg: getComputedStyle(document.body).backgroundColor, saved: localStorage.getItem("hpo-theme"), media: [...document.querySelectorAll("source[data-theme-src]")].map(s => s.media).join("|"), label: document.getElementById("theme").getAttribute("aria-label") }));
  check("theme switch: stores the preference and rewrites the picture sources", before === "rgb(243, 248, 252)" && th.bg === "rgb(11, 26, 40)" && th.saved === "dark" && th.media === "all|all" && th.label === "Switch to light theme", JSON.stringify(th));

  const a11y = await page.evaluate(() => {
    const chart = document.querySelector(".chart");
    return {
      role: chart.getAttribute("role"), label: (chart.getAttribute("aria-label") || "").length,
      bare: [...chart.querySelectorAll("svg")].filter(s => s.getAttribute("aria-hidden") !== "true").length, text: chart.textContent.trim().length,
      steps: document.querySelectorAll("ol#steps > li").length, numbers: [...document.querySelectorAll("#steps .n")].filter(n => n.getAttribute("aria-hidden") !== "true").length,
      hero: document.querySelector(".hero-art").getAttribute("aria-hidden"), progress: document.body.firstElementChild.className + "/" + document.body.firstElementChild.getAttribute("aria-hidden"),
      week: [...document.querySelectorAll(".week > li > h4")].length,
    };
  });
  check("chart: one labelled image, its drawings hidden and without text; five steps in an ordered list, numbers hidden; hero strip and progress line hidden",
    a11y.role === "img" && a11y.label > 80 && a11y.bare === 0 && a11y.text === 0 && a11y.steps === 5 && a11y.numbers === 0 && a11y.hero === "true" && a11y.progress === "progress/true" && a11y.week === 4, JSON.stringify(a11y));
  await ctx.close();
}

await browser.close();
server.close();
console.log(`RESULT fails=${fails}`);
console.log(`RESULT base=${BASE_REF.slice(0, 12)}`);
process.exitCode = fails ? 1 : 0;
