// D4 round-4 verify-0-2 — verifier 2's OWN harness (independent of lib/measure.js
// and of the finder's contrast method).
//
// METRIC (four sub-metrics, own definitions):
//  (1) lane-label on-screen font size: SVG font-size attribute (viewBox
//      units) x svg rect width / viewBox width, per viewport tile, for every
//      text.lane-label; the same quantity for every other font-size-carrying
//      text for comparison (the card's own 8 px axis floor).
//  (2) lane-label contrast: WCAG 2.1 ratio between the SPECIFIED fill colour
//      and every distinct colour cluster covering >= 1 % of the pixels in the
//      label's bounding-box row band of ONE deviceScaleFactor-4 screenshot
//      (no on/off double rasterisation, no glyph-pixel detection: the
//      background dominates any text band, so the background colours are
//      read off a histogram of the band). Min over clusters, per label.
//  (3) wi-save contrast: WCAG 2.1 ratio between the button's computed
//      background-color and computed color (both opaque) under five theme
//      tables: stock HA light and stock HA dark (per HA frontend 2025.2
//      source: html-level --text-primary-color:#ffffff, never overridden in
//      any dark block), the custom-primary variant (#212121 — what
//      apply_themes_on_element.ts sets when the user picks a primary colour
//      whose contrast vs #212121 is >= 6; the default blue #03a9f4 measures
//      6.12), and the finder's dark table for reproduction.
//  (4) SC 2.5.8 target size with the spacing exception applied EXACTLY per
//      the standard's wording: an undersized target (< 24 px smaller side)
//      fails if its 24 px-diameter centre circle intersects a sized target's
//      BOUNDING BOX (circle-rect intersection) or another undersized
//      target's circle (centre distance < 24) — not the centre-distance
//      approximation the finder used for all neighbours.
//
// RUN (from the repository root):
//   NODE_PATH=/private/tmp/hpo-pw/node_modules \
//   PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers \
//   HPO_PLANDATA=/private/tmp/hpo-d4-v2own/plandata.json \
//     node tools/audit/round4/D4/v2_own.mjs
//
// EXPECTED at tree ae2a60b (claude/13-dimension-audit-920935) on this box
// (Apple M1, Chromium 131.0.6778.33): sizes exact +-0.05 px, counts exact
// +-0, contrast ratios +-0.1. load1 quoted, not gated: every number here is
// a length, a count or a colour ratio.
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
const CARD_SRC = path.join(repo, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js");
const driftSrc = readFileSync(path.join(repo, "tests/card_drift.mjs"), "utf8");
const STATES = [...driftSrc.matchAll(/^\s{2}\{ name: "([a-z0-9_]+)",$/gm)].map((m) => m[1]);
if (STATES.length !== 34) { console.error(`FAIL: derived ${STATES.length} states`); process.exit(1); }

// Home Assistant's OWN default theme variables, from the frontend source at
// 2025.2 (min supported per hacs.json): html-level block of
// src/resources/ha-style.ts plus darkStyles of src/resources/styles-data.ts,
// verified unchanged at 2025.8 / 2026.7 / dev (color.globals.ts). Stock dark
// does NOT override --text-primary-color — the html-level #ffffff stands in
// both modes. The finder's dark table asserted #212121; stock HA never
// produces that in either mode.
const STOCK = {
  light: { "--primary-text-color": "#212121", "--secondary-text-color": "#727272",
    "--primary-color": "#03a9f4", "--card-background-color": "#ffffff",
    "--primary-background-color": "#fafafa", "--secondary-background-color": "#e5e5e5",
    "--divider-color": "rgba(0,0,0,.12)", "--error-color": "#db4437",
    "--warning-color": "#ffa600", "--success-color": "#43a047",
    "--text-primary-color": "#ffffff" },
  dark: { "--primary-text-color": "#e1e1e1", "--secondary-text-color": "#9b9b9b",
    "--primary-color": "#03a9f4", "--card-background-color": "#1c1c1c",
    "--primary-background-color": "#111111", "--secondary-background-color": "#282828",
    "--divider-color": "rgba(225,225,225,.12)", "--error-color": "#db4437",
    "--warning-color": "#ffa600", "--success-color": "#43a047",
    "--text-primary-color": "#ffffff" },
};
const CUSTOM_PRIMARY_DARK = { ...STOCK.dark, "--text-primary-color": "#212121" };
const CUSTOM_PRIMARY_LIGHT = { ...STOCK.light, "--text-primary-color": "#212121" };
const FINDER_DARK = { ...STOCK.dark, "--text-primary-color": "#212121" };

const HA_CARD = `
  if (!customElements.get("ha-card")) {
    customElements.define("ha-card", class extends HTMLElement {
      constructor() { super();
        this.attachShadow({ mode: "open" }).innerHTML =
          "<style>:host{background:var(--card-background-color,white);box-sizing:border-box;" +
          "border-radius:12px;border:1px solid var(--divider-color,#e0e0e0);color:var(--primary-text-color);" +
          "display:block;position:relative}</style><slot></slot>"; }
    });
  }`;

function lum(c) {
  const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
  return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]);
}
const ratio = (a, b) => { const l1 = lum(a), l2 = lum(b); return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05); };
const parse = (s) => { const m = String(s).match(/rgba?\(([^)]+)\)/); if (!m) return null;
  const q = m[1].split(/[,\s/]+/).filter((z) => z.length).map(Number); return [q[0], q[1], q[2]]; };

const VPS = [{ n: "375x812", w: 375, h: 812, tile: 359 },
             { n: "768x1024", w: 768, h: 1024, tile: 736 },
             { n: "1280x800", w: 1280, h: 800, tile: 500 }];
const DSF = 4;
const results = { laneFont: [], laneContrast: [], wiSave: [], targets: [] };

const browser = await chromium.launch();
async function freshPage(vp, theme, freeze, pointer) {
  const ctx = await browser.newContext({ viewport: { width: vp.w, height: vp.h }, deviceScaleFactor: DSF });
  const page = await ctx.newPage();
  if (pointer) {
    const cdp = await ctx.newCDPSession(page);
    await cdp.send("Emulation.setEmulatedMedia", {
      features: [{ name: "pointer", value: pointer }, { name: "any-pointer", value: pointer }] });
  }
  await page.goto("about:blank");
  if (freeze) {
    const frozen = Date.parse(plan.dhw_plan.forecast[0].t) + 6 * 3600 * 1000;
    await page.addInitScript((f) => {
      const Real = Date;
      class Frozen extends Real { constructor(...a) { super(...(a.length ? a : [f])); } static now() { return f; } }
      window.Date = Frozen;
    }, frozen);
    await page.reload();
  }
  await page.addStyleTag({ content:
    `:root{${Object.entries(theme).map(([k, v]) => `${k}:${v}`).join(";")}}\n` +
    `html,body{margin:0;background:${theme["--primary-background-color"]};` +
    `font-family:Roboto,-apple-system,"Segoe UI",sans-serif;font-size:14px}` +
    `#hpo-host{width:${vp.tile}px;margin:0 auto}heatpump-optimizer-card{display:block}` });
  await page.addScriptTag({ content: HA_CARD });
  await page.addScriptTag({ path: CARD_SRC });
  await page.addScriptTag({ path: path.join(__dirname, "lib/states.js") }); // drivers only: no measurement lib
  if (pointer === "coarse" || pointer === "fine") {
    await page.evaluate(([coarse]) => {
      const orig = window.matchMedia.bind(window);
      window.matchMedia = (q) => q === "(pointer: coarse)"
        ? { matches: coarse, media: q, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {} }
        : orig(q);
    }, [pointer === "coarse"]);
  }
  return { ctx, page };
}

try {
  // ---------- (1) + (2): lane labels, plan_inline, per viewport x theme ----------
  for (const vp of VPS) {
    for (const themeName of ["light", "dark"]) {
      const { ctx, page } = await freshPage(vp, STOCK[themeName], true);
      await page.evaluate(async ([n, p]) => { await window.__D4.STATES[n](p); }, ["plan_inline", plan]);
      const lanes = await page.evaluate(() => {
        const root = window.__card.shadowRoot;
        const out = [];
        let axisMin = null;
        for (const svg of root.querySelectorAll(".chartwrap svg")) {
          const r = svg.getBoundingClientRect();
          const vb = (svg.getAttribute("viewBox") || "").split(/\s+/).map(Number);
          const scale = r.width / (vb[2] || 900);
          for (const t of svg.querySelectorAll("text.lane-label")) {
            const b = t.getBoundingClientRect();
            const st = getComputedStyle(t);
            out.push({ text: t.textContent.trim(),
              px: Math.round(Number(t.getAttribute("font-size")) * scale * 100) / 100,
              units: Number(t.getAttribute("font-size")),
              svgW: Math.round(r.width * 10) / 10, vbW: vb[2],
              x: b.left, y: b.top, w: b.width, h: b.height,
              fill: st.fill, visible: b.width > 0.5 });
          }
          const others = [...svg.querySelectorAll("text[font-size]")]
            .filter((t) => !/lane-/.test(t.getAttribute("class") || ""))
            .filter((t) => (t.textContent || "").trim())
            .map((t) => Number(t.getAttribute("font-size")) * scale);
          if (others.length) axisMin = axisMin == null ? Math.min(...others) : Math.min(axisMin, ...others);
        }
        out.__axisMin = axisMin;
        return out;
      });
      const axisMin = lanes.__axisMin; delete lanes.__axisMin;
      results.laneFont.push({ vp: vp.n, theme: themeName, axisMinPx: axisMin,
        labels: lanes.map((l) => ({ text: l.text, px: l.px, units: l.units, svgW: l.svgW, vbW: l.vbW })) });

      // (2) histogram clusters of the label band, from ONE screenshot
      if (lanes.length) {
        const shot = await page.screenshot({ type: "png" });
        const cl = await page.evaluate(async ([b64, ls, dsf]) => {
          const L = (c) => { const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
            return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); };
          const R = (a, b) => { const l1 = L(a), l2 = L(b); return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05); };
          const px = (s) => { const m = String(s).match(/rgba?\(([^)]+)\)/); if (!m) return null;
            const q = m[1].split(/[,\s/]+/).filter((z) => z.length).map(Number); return [q[0], q[1], q[2]]; };
          const img = new Image();
          await new Promise((ok, no) => { img.onload = ok; img.onerror = no; img.src = "data:image/png;base64," + b64; });
          const cv = document.createElement("canvas"); cv.width = img.width; cv.height = img.height;
          const g = cv.getContext("2d", { willReadFrequently: true }); g.drawImage(img, 0, 0);
          const out = [];
          for (const l of ls) {
            const x0 = Math.max(0, Math.floor(l.x * dsf)), x1 = Math.min(cv.width - 1, Math.ceil((l.x + l.w) * dsf));
            const y0 = Math.max(0, Math.floor(l.y * dsf)), y1 = Math.min(cv.height - 1, Math.ceil((l.y + l.h) * dsf));
            const exact = new Map(); let total = 0;
            for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) {
              const d = g.getImageData(x, y, 1, 1).data;
              const k = d[0] + "," + d[1] + "," + d[2];
              exact.set(k, (exact.get(k) || 0) + 1); total += 1;
            }
            // clusters: exact colours merged by rounding each channel to 16
            const clus = new Map();
            for (const [k, n] of exact) {
              const [r, gg, b] = k.split(",").map(Number);
              const ck = (r >> 4) + "," + (gg >> 4) + "," + (b >> 4);
              const e = clus.get(ck) || { n: 0, rep: null, repN: 0 };
              e.n += n; if (n > e.repN) { e.repN = n; e.rep = [r, gg, b]; }
              clus.set(ck, e);
            }
            const fg = px(l.fill);
            const keep = [...clus.entries()].filter(([k, e]) => e.n / total >= 0.01)
              .map(([k, e]) => ({ share: Math.round(e.n / total * 1000) / 1000, bg: e.rep,
                                  ratio: fg ? Math.round(R(fg, e.rep) * 1000) / 1000 : null }));
            keep.sort((a, b) => a.ratio - b.ratio);
            out.push({ text: l.text, fg, clusters: keep.slice(0, 4) });
          }
          return out;
        }, [shot.toString("base64"), lanes, DSF]);
        results.laneContrast.push({ vp: vp.n, theme: themeName, labels: cl });
      }
      await ctx.close();
    }
  }

  // ---------- (3): wi-save under five theme tables ----------
  {
    const vp = VPS[2];
    for (const [name, theme] of [
      ["stock_light", STOCK.light], ["stock_dark", STOCK.dark],
      ["custom_primary_dark", CUSTOM_PRIMARY_DARK], ["custom_primary_light", CUSTOM_PRIMARY_LIGHT],
      ["finder_dark", FINDER_DARK],
    ]) {
      const { ctx, page } = await freshPage(vp, theme, true);
      await page.evaluate(async ([n, p]) => { await window.__D4.STATES[n](p); }, ["expanded_plan", plan]);
      const m = await page.evaluate(() => {
        const root = window.__card.shadowRoot;
        const btn = root.querySelector(".wi-save");
        if (!btn) return null;
        const st = getComputedStyle(btn);
        return { color: st.color, bg: st.backgroundColor, text: btn.textContent.trim() };
      });
      if (m) {
        const r = ratio(parse(m.color), parse(m.bg));
        results.wiSave.push({ theme: name, fg: m.color, bg: m.bg, ratio: Math.round(r * 1000) / 1000 });
      }
      await ctx.close();
    }
  }

  // ---------- (4): SC 2.5.8, exact spacing exception, all states ----------
  for (const arm of ["fine", "coarse"]) {
    for (const vp of VPS) {
      const { ctx, page } = await freshPage(vp, STOCK.light, true, arm);
      for (const state of STATES) {
        let driveOk = true;
        try {
          driveOk = !!(await page.evaluate(async ([n, p]) => {
            if (!window.__D4.STATES[n]) return { ok: false };
            return await window.__D4.STATES[n](p);
          }, [state, plan])).ok;
        } catch (e) { driveOk = false; }
        const r = await page.evaluate(() => {
          const out = [];
          const HIT = ["button", "a[href]", "input", "select", "textarea", "summary",
            "[role='button']", "[role='tab']", "[tabindex]", ".chip", ".setup-hit",
            ".dlg-tab", ".slot-hit", ".lane-hit"].join(",");
          const stack = [window.__card.shadowRoot];
          const seen = new Set();
          const pushKids = (n) => {
            if (n.shadowRoot) stack.push(n.shadowRoot);
            if (n.children) for (const k of n.children) stack.push(k);
          };
          while (stack.length) {
            const n = stack.pop(); if (!n) continue;
            if (n.nodeType !== 1) { pushKids(n); continue; }
            let m = false; try { m = n.matches && n.matches(HIT); } catch (e) {}
            if (m && !seen.has(n) && !n.disabled) {
              seen.add(n);
              const st = getComputedStyle(n);
              if (st.display !== "none" && st.visibility !== "hidden" && Number(st.opacity) !== 0) {
                const b = n.getBoundingClientRect();
                if (b.width > 0.01 && b.height > 0.01) {
                  const cls = (n.getAttribute("class") || "").trim().split(/\s+/).slice(0, 2).join(".");
                  out.push({ sel: n.tagName.toLowerCase() + (cls ? "." + cls : ""),
                    cx: b.left + b.width / 2, cy: b.top + b.height / 2,
                    l: b.left, t: b.top, r: b.right, bo: b.bottom,
                    w: Math.round(b.width * 100) / 100, h: Math.round(b.height * 100) / 100 });
                }
              }
            }
            pushKids(n);
          }
          return out;
        });
        // exact SC 2.5.8: undersized t fails if its 24px centre circle hits a
        // sized target's BOX (circle-rect) or another undersized circle.
        // Two readings, both reported:
        //  strict  — any other target counts, including a container (a
        //            tabindex'd chart svg) that encloses the control;
        //  adjacent — containers that fully enclose the undersized target
        //            are ignored (they are not an adjacent competing target;
        //            the strict reading would fail almost every control
        //            drawn inside a focusable chart).
        const MIN = 24;
        const encloses = (o, t) => o.l <= t.cx && o.r >= t.cx && o.t <= t.cy && o.bo >= t.cy;
        const under = r.filter((t) => Math.min(t.w, t.h) < MIN - 0.05);
        const failing = [];
        const failingStrict = [];
        for (const t of under) {
          for (const mode of ["strict", "adjacent"]) {
            let bad = null;
            for (const o of r) {
              if (o === t) continue;
              if (mode === "adjacent" && encloses(o, t)) continue;
              const oUnder = Math.min(o.w, o.h) < MIN - 0.05;
              if (oUnder) {
                if (Math.hypot(o.cx - t.cx, o.cy - t.cy) < MIN - 0.05) { bad = { why: "circle-circle", o }; break; }
              } else {
                const nx = Math.max(o.l, Math.min(t.cx, o.r));
                const ny = Math.max(o.t, Math.min(t.cy, o.bo));
                if (Math.hypot(nx - t.cx, ny - t.cy) < 12 - 0.05) { bad = { why: "circle-box", o }; break; }
              }
            }
            const rec = bad ? { sel: t.sel, w: t.w, h: t.h, why: bad.why, other: bad.o.sel,
                                dist: Math.round(Math.hypot(bad.o.cx - t.cx, bad.o.cy - t.cy) * 100) / 100 } : null;
            if (rec) (mode === "strict" ? failingStrict : failing).push(rec);
          }
        }
        // the vc zoom pair, measured explicitly wherever it renders
        const vc = await page.evaluate(() => {
          const card = window.__card;
          if (!card || !card.shadowRoot) return [];
          const root = card.shadowRoot;
          const out = [];
          for (const d of root.querySelectorAll(".viewctl")) {
            const ins = [...d.querySelectorAll("button")].map((b) => {
              const bb = b.getBoundingClientRect();
              return { sel: b.className || b.tagName, w: Math.round(bb.width * 100) / 100, h: Math.round(bb.height * 100) / 100,
                       cx: bb.left + bb.width / 2 };
            });
            for (let i = 1; i < ins.length; i++) ins[i - 1].gapToNext = Math.round((ins[i].cx - ins[i - 1].cx) * 100) / 100;
            out.push(...ins);
          }
          return out;
        });
        results.targets.push({ arm, vp: vp.n, state, drive_ok: driveOk, targets: r.length,
          undersized: under.length, failing: failing.length, failing_strict: failingStrict.length,
          detail: failing.slice(0, 6), detail_strict: failingStrict.slice(0, 3), vc });
      }
      await ctx.close();
    }
  }
} finally { await browser.close(); }

writeFileSync(path.join(OUT, "v2_own.json"), JSON.stringify(results, null, 1));

for (const row of results.laneFont) {
  const pxs = row.labels.map((l) => l.px);
  console.log(`RESULT lane_font ${row.vp} ${row.theme}: n=${row.labels.length}` +
    (pxs.length ? ` min=${Math.min(...pxs).toFixed(2)} max=${Math.max(...pxs).toFixed(2)}` : "") +
    ` axis_other_min=${row.axisMinPx != null ? row.axisMinPx.toFixed(2) : "na"}`);
}
for (const row of results.laneContrast) {
  for (const l of row.labels) {
    const c0 = l.clusters[0];
    console.log(`RESULT lane_contrast ${row.vp} ${row.theme} "${l.text}": min_cluster_ratio=${c0 ? c0.ratio : "na"} fg=rgb(${l.fg}) worst_bg=rgb(${c0 ? c0.bg : []}) share=${c0 ? c0.share : "na"}`);
  }
}
for (const r of results.wiSave) console.log(`RESULT wi_save ${r.theme}: fg=${r.fg} bg=${r.bg} ratio=${r.ratio}`);
const byArm = {};
for (const t of results.targets) {
  byArm[t.arm] = byArm[t.arm] || { cells: 0, targets: 0, under: 0, failing: 0, failingStrict: 0, sigs: {}, undriven: 0, vc: {} };
  const a = byArm[t.arm];
  a.cells += 1; a.targets += t.targets; a.under += t.undersized; a.failing += t.failing; a.failingStrict += t.failing_strict;
  if (!t.drive_ok) a.undriven += 1;
  for (const f of t.detail) {
    const k = `${f.sel} ${f.w}x${f.h} ${f.why}->${f.other} d=${f.dist}`;
    a.sigs[k] = (a.sigs[k] || 0) + 1;
  }
  for (const v of (t.vc || [])) {
    const k = `${v.sel} ${v.w}x${v.h}` + (v.gapToNext != null ? ` gap=${v.gapToNext}` : "");
    a.vc[k] = (a.vc[k] || 0) + 1;
  }
}
for (const [arm, a] of Object.entries(byArm)) {
  console.log(`RESULT targets_${arm}: cells=${a.cells} targets=${a.targets} undersized=${a.under} failing_adjacent_2_5_8=${a.failing} failing_strict_2_5_8=${a.failingStrict} undriven_cells=${a.undriven}`);
  for (const [k, n] of Object.entries(a.sigs).sort((x, y) => y[1] - x[1]).slice(0, 8)) console.log(`    ${n}x  ${k}`);
  console.log(`    vc zoom-button geometry:`);
  for (const [k, n] of Object.entries(a.vc).sort((x, y) => y[1] - x[1]).slice(0, 6)) console.log(`    ${n}x  ${k}`);
}
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log("RESULT thread_factor=1.00 (no CPU-time metric)");
console.log("RESULT swapins=0 (not a memory metric)");
