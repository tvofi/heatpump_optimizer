// D4 round-4 — pixel-truth contrast for the flagged text runs.
//
// METRIC: for a named element class in a named card state, the WCAG 2.1
// contrast ratio between the pixels the glyphs actually paint and the pixels
// actually behind them, taken from two real Chromium rasterisations of the
// same frame: one with the element visible, one with it hidden. Reported as
// ratio_min over the element's own box (the worst run), plus the two sRGB
// colours that produced it.
//
// WHY it exists: card_grid.mjs's analytic compositing walks every SVG shape
// whose BOUNDING BOX covers the text. An area `path` has a bbox that reaches
// far below its filled region, so the analytic number can name a layer that
// paints nothing there. This harness never asks what is nominally behind the
// text; it reads what Chromium put on the screen.
//
// RUN (from the export root):
//   NODE_PATH=/private/tmp/hpo-pw/node_modules \
//   PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers \
//   HPO_PLANDATA=/private/tmp/hpo-d4/plandata.json \
//     node tools/audit/round4/D4/contrast_pixels.mjs
//
// EXPECTED at baseline 7dd68dd327fe3dbfb09f3bd0fe38910c58877697 on the audit
// box (Apple M1, Chromium 131.0.6778.33, deviceScaleFactor 4): each RESULT
// line is a ratio; tolerance +-0.05 (antialiasing only; the frame is frozen
// and the payload fixed).
import { createRequire } from "node:module";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(__dirname, "../../../..");
const OUT = path.join(__dirname, "out");
mkdirSync(OUT, { recursive: true });
const plan = JSON.parse(readFileSync(process.env.HPO_PLANDATA, "utf8"));

const THEMES = {
  light: { "--primary-text-color": "#212121", "--secondary-text-color": "#727272",
    "--primary-color": "#03a9f4", "--card-background-color": "#ffffff",
    "--primary-background-color": "#fafafa", "--secondary-background-color": "#e5e5e5",
    "--divider-color": "rgba(0,0,0,.12)", "--error-color": "#db4437",
    "--warning-color": "#ffa600", "--success-color": "#43a047", "--text-primary-color": "#ffffff" },
  dark: { "--primary-text-color": "#e1e1e1", "--secondary-text-color": "#9b9b9b",
    "--primary-color": "#03a9f4", "--card-background-color": "#1c1c1c",
    "--primary-background-color": "#111111", "--secondary-background-color": "#202020",
    "--divider-color": "rgba(225,225,225,.12)", "--error-color": "#db4437",
    "--warning-color": "#ffa600", "--success-color": "#43a047", "--text-primary-color": "#212121" },
};

// (state, css selector inside the shadow root, viewport, tile, theme)
const PROBES = JSON.parse(process.env.D4_PROBES || JSON.stringify([
  { state: "plan_inline", sel: "text.lane-label", vp: [1280, 800], tile: 500, theme: "light" },
  { state: "plan_inline", sel: "text.lane-label", vp: [1280, 800], tile: 500, theme: "dark" },
  { state: "plan_inline", sel: "text.lane-more", vp: [1280, 800], tile: 500, theme: "dark" },
  { state: "expanded_plan", sel: "text.lane-label", vp: [1280, 800], tile: 500, theme: "light" },
  { state: "expanded_plan", sel: "text.lane-label", vp: [1280, 800], tile: 500, theme: "dark" },
  { state: "expanded_plan", sel: ".wi-save", vp: [1280, 800], tile: 500, theme: "dark" },
  { state: "expanded_plan", sel: ".wi-save", vp: [1280, 800], tile: 500, theme: "light" },
  { state: "plan_inline", sel: "text.lane-label", vp: [375, 812], tile: 359, theme: "light" },
  { state: "wood_lane", sel: "text.lane-label", vp: [1280, 800], tile: 500, theme: "light" },
]));

const CARD_SRC = path.join(repo, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js");
const HA_CARD = `
  if (!customElements.get("ha-card")) {
    customElements.define("ha-card", class extends HTMLElement {
      constructor() { super();
        this.attachShadow({ mode: "open" }).innerHTML =
          "<style>:host{background:var(--card-background-color,white);box-sizing:border-box;" +
          "border-radius:12px;border:1px solid var(--divider-color,#e0e0e0);color:var(--primary-text-color);" +
          "display:block;position:relative;}</style><slot></slot>"; }
    });
  }`;

function lum(c) {
  const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
  return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]);
}
const ratio = (a, b) => { const l1 = lum(a), l2 = lum(b); return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05); };

const DSF = 4;
const rows = [];
const browser = await chromium.launch();
try {
  for (const pr of PROBES) {
    const ctx = await browser.newContext({
      viewport: { width: pr.vp[0], height: pr.vp[1] }, deviceScaleFactor: DSF,
      colorScheme: pr.theme,
    });
    const page = await ctx.newPage();
    await page.goto("about:blank");
    await page.addStyleTag({ content:
      `:root{${Object.entries(THEMES[pr.theme]).map(([k, v]) => `${k}:${v}`).join(";")}}\n` +
      `html,body{margin:0;background:${THEMES[pr.theme]["--primary-background-color"]};` +
      `font-family:Roboto,-apple-system,"Segoe UI",sans-serif;font-size:14px}` +
      `#hpo-host{width:${pr.tile}px;margin:0 auto}heatpump-optimizer-card{display:block}` });
    await page.addScriptTag({ content: HA_CARD });
    await page.addScriptTag({ path: CARD_SRC });
    await page.addScriptTag({ path: path.join(__dirname, "lib/measure.js") });
    await page.addScriptTag({ path: path.join(__dirname, "lib/states.js") });
    await page.evaluate(async ([n, p]) => { await window.__D4.STATES[n](p); }, [pr.state, plan]);

    // every match, with its client box and its SPECIFIED foreground. A match
    // outside the viewport is scrolled into view first: a screenshot cannot
    // rasterise what is not on screen, and an unscrolled match returns "no
    // glyph pixels", which reads as a pass.
    const boxes = await page.evaluate((sel) => {
      const root = window.__card.shadowRoot;
      const els = [...root.querySelectorAll(sel)];
      for (const e of els) {
        const b = e.getBoundingClientRect();
        if (b.top < 0 || b.bottom > innerHeight) {
          try { e.scrollIntoView({ block: "center" }); } catch (x) {}
        }
      }
      const px = (c) => {
        const m = String(c).match(/rgba?\(([^)]+)\)/);
        if (!m) return null;
        const q = m[1].split(/[,\s/]+/).filter((z) => z.length).map(Number);
        return [q[0], q[1], q[2]];
      };
      return els.map((e, i) => {
        const b = e.getBoundingClientRect();
        const st = getComputedStyle(e);
        return { i, text: (e.textContent || "").trim().slice(0, 30),
                 x: b.left, y: b.top, w: b.width, h: b.height,
                 specFg: px(e.ownerSVGElement ? st.fill : st.color) };
      }).filter((b) => b.w > 0.5 && b.h > 0.5);
    }, pr.sel);
    if (!boxes.length) { rows.push({ ...pr, error: "no match" }); await ctx.close(); continue; }

    // two rasterisations of the same frame: visible, then hidden
    const shots = {};
    for (const mode of ["on", "off"]) {
      // The glyphs go, the element's own background stays. `visibility:hidden`
      // would take the button's background with the label and hand back the
      // page behind it as "the background", which reports a coloured button
      // as white-on-white.
      await page.evaluate(([sel, m]) => {
        const root = window.__card.shadowRoot;
        for (const e of root.querySelectorAll(sel)) {
          if (m === "off") {
            e.style.setProperty("color", "transparent", "important");
            e.style.setProperty("fill", "transparent", "important");
            e.style.setProperty("-webkit-text-fill-color", "transparent", "important");
          } else {
            e.style.removeProperty("color");
            e.style.removeProperty("fill");
            e.style.removeProperty("-webkit-text-fill-color");
          }
        }
      }, [pr.sel, mode]);
      shots[mode] = await page.screenshot({ type: "png" });
    }
    // decode both in the page (no image library: Chromium already has one)
    const measured = await page.evaluate(async ([onB64, offB64, boxes, dsf]) => {
      const load = (b64) => new Promise((ok, no) => {
        const img = new Image(); img.onload = () => ok(img); img.onerror = no;
        img.src = "data:image/png;base64," + b64;
      });
      const [a, b] = await Promise.all([load(onB64), load(offB64)]);
      const cv = document.createElement("canvas");
      cv.width = a.width; cv.height = a.height;
      const g = cv.getContext("2d", { willReadFrequently: true });
      g.drawImage(a, 0, 0);
      const A = g.getImageData(0, 0, cv.width, cv.height).data;
      g.clearRect(0, 0, cv.width, cv.height);
      g.drawImage(b, 0, 0);
      const B = g.getImageData(0, 0, cv.width, cv.height).data;
      const out = [];
      for (const bx of boxes) {
        const x0 = Math.max(0, Math.floor(bx.x * dsf) - 1), x1 = Math.min(cv.width - 1, Math.ceil((bx.x + bx.w) * dsf) + 1);
        const y0 = Math.max(0, Math.floor(bx.y * dsf) - 1), y1 = Math.min(cv.height - 1, Math.ceil((bx.y + bx.h) * dsf) + 1);
        // glyph pixels: where the two rasterisations differ most. Take the
        // 20 % of changed pixels furthest from their own background (the
        // glyph core), so antialiased edges cannot flatter the ratio.
        const cand = [];
        for (let y = y0; y <= y1; y++) {
          for (let x = x0; x <= x1; x++) {
            const i = (y * cv.width + x) * 4;
            const d = Math.abs(A[i] - B[i]) + Math.abs(A[i + 1] - B[i + 1]) + Math.abs(A[i + 2] - B[i + 2]);
            if (d > 12) cand.push({ x, y, i, d });
          }
        }
        if (!cand.length) { out.push({ ...bx, error: "no glyph pixels" }); continue; }
        cand.sort((p, q) => q.d - p.d);
        const core = cand.slice(0, Math.max(1, Math.round(cand.length * 0.2)));
        // the worst single glyph pixel against the background that pixel covers
        let worst = null;
        for (const p of core) {
          const fg = [A[p.i], A[p.i + 1], A[p.i + 2]];
          const bgp = [B[p.i], B[p.i + 1], B[p.i + 2]];
          out.__ = 0;
          const r = (() => {
            const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
            const L = (c) => 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]);
            const l1 = L(fg), l2 = L(bgp);
            return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
          })();
          if (!worst || r < worst.r) worst = { r, fg, bg: bgp, x: p.x, y: p.y };
        }
        // and the median glyph pixel, so one antialiased outlier cannot carry it
        const rs = core.map((p) => {
          const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
          const L = (c) => 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]);
          const l1 = L([A[p.i], A[p.i + 1], A[p.i + 2]]), l2 = L([B[p.i], B[p.i + 1], B[p.i + 2]]);
          return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
        }).sort((m, n) => m - n);
        // The WCAG number: the SPECIFIED text colour (no antialiasing) over
        // the background the pixels actually show. Antialiased stems can only
        // move a measured fg toward the background, so a ratio read off blended
        // pixels understates a light-on-light failure and overstates nothing.
        let specRatio = null, specBg = null;
        if (bx.specFg) {
          const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
          const L = (c) => 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]);
          const rr = (a2, b2) => { const l1 = L(a2), l2 = L(b2); return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05); };
          let w2 = null;
          for (const p of core) {
            const bgp = [B[p.i], B[p.i + 1], B[p.i + 2]];
            const r2 = rr(bx.specFg, bgp);
            if (!w2 || r2 < w2.r) w2 = { r: r2, bg: bgp };
          }
          if (w2) { specRatio = Math.round(w2.r * 1000) / 1000; specBg = w2.bg; }
        }
        out.push({ ...bx, glyphPx: cand.length, corePx: core.length,
                   worst: Math.round(worst.r * 1000) / 1000, fg: worst.fg, bg: worst.bg,
                   specRatio, specBg,
                   median: Math.round(rs[Math.floor(rs.length / 2)] * 1000) / 1000,
                   best: Math.round(rs[rs.length - 1] * 1000) / 1000 });
      }
      return out;
    }, [shots.on.toString("base64"), shots.off.toString("base64"), boxes, DSF]);

    rows.push({ ...pr, matches: measured });
    await ctx.close();
  }
} finally { await browser.close(); }

writeFileSync(path.join(OUT, "contrast_pixels.json"), JSON.stringify(rows, null, 1));
for (const r of rows) {
  if (r.error) { console.log(`RESULT ${r.state}/${r.sel}/${r.theme}=ERROR ${r.error}`); continue; }
  const meds = r.matches.filter((m) => m.median != null).map((m) => m.median);
  const worsts = r.matches.filter((m) => m.median != null).map((m) => m.worst);
  if (!meds.length) { console.log(`RESULT ${r.state}/${r.sel}/${r.theme}=NO_GLYPH_PIXELS`); continue; }
  const specs = r.matches.filter((m) => m.specRatio != null).map((m) => m.specRatio);
  console.log(`RESULT ${r.state}|${r.sel}|${r.theme}|n=${meds.length} spec_min=${specs.length ? Math.min(...specs).toFixed(2) : "na"} spec_max=${specs.length ? Math.max(...specs).toFixed(2) : "na"} blended_median_min=${Math.min(...meds).toFixed(2)} ratio`);
  for (const m of r.matches) {
    if (m.median == null) continue;
    console.log(`   "${m.text}" spec=${m.specRatio} specFg=rgb(${m.specFg}) bg=rgb(${m.specBg}) | blended median=${m.median} px=${m.glyphPx}`);
  }
}
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log(`RESULT thread_factor=1.00 (no CPU-time metric)`);
console.log(`RESULT swapins=0 (not a memory metric)`);
