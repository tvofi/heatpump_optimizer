// VERIFIER 1 (seat 0-1) round 4 — OWN harness for finding D4-01.
//
// METRIC (mine, independent of the finder's):
//   (a) ON-SCREEN GLYPH HEIGHT: the rendered ink extent of each visible
//       `text.lane-label` = getBBox() height (viewBox units) x svg client
//       width / viewBox width. The finder measured the font-size ATTRIBUTE
//       x the same scale; getBBox measures what was actually painted
//       (cap-to-descender), so the two definitions agree only if the
//       attribute is honest.
//   (b) PIXEL CONTRAST, ONE-RASTER-DIFF METHOD: rasterise the frame twice
//       at deviceScaleFactor 2 (finder: 4); in the second raster the
//       glyphs are removed by emptying `textContent` (finder: inline
//       `color`/`fill: transparent` styles). Glyph-core pixels = the 35 %
//       of changed pixels with the largest channel delta > 20 (finder: 20 %
//       and > 12). Report the MEDIAN ratio over core pixels of
//       measured-foreground vs measured-background (my own number), plus
//       the worst backdrop pixel against the specified fill.
//   (c) FLOOR CHECK: the minimum on-screen font px of every other chart
//       text (class not matching /lane-/) in the same svg, to show what the
//       card's 8 px axis floor does reach.
//
// RUN (from the repository root):
//   NODE_PATH=/private/tmp/hpo-pw/node_modules \
//   PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers \
//   HPO_PLANDATA=<private plandata.json> \
//     node tools/audit/round4/D4/d4_own_D4-01.mjs
//
// EXPECTED (verifier's own prediction, finder claims 6.4 px at 375x812 and
// 1.01-2.55:1): lane-label glyph height < 8 px at every tile, ratio_min
// under 4.5 in both themes. Tolerance: this is a different metric
// definition, so agreement is qualitative; both numbers are reported.
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

const THEMES = {
  light: { "--primary-text-color": "#212121", "--secondary-text-color": "#727272",
    "--primary-color": "#03a9f4", "--card-background-color": "#ffffff",
    "--primary-background-color": "#fafafa", "--secondary-background-color": "#e5e5e5",
    "--divider-color": "rgba(0,0,0,.12)", "--error-color": "#db4437",
    "--text-primary-color": "#ffffff" },
  dark: { "--primary-text-color": "#e1e1e1", "--secondary-text-color": "#9b9b9b",
    "--primary-color": "#03a9f4", "--card-background-color": "#1c1c1c",
    "--primary-background-color": "#111111", "--secondary-background-color": "#202020",
    "--divider-color": "rgba(225,225,225,.12)", "--error-color": "#db4437",
    "--text-primary-color": "#ffffff" },
};

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

// my own mount: setConfig and hass before attach, Lovelace order, no
// dependency on the finder's lib/states.js
const MOUNT = async (planJson) => {
  const raf = () => new Promise((r) => requestAnimationFrame(() => r()));
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const forecast = planJson.space_plan.forecast;
  const solar = forecast.map((p, i) => ({
    t: p.t, ghi: Math.max(0, 400 * Math.sin((i / forecast.length) * Math.PI)) }));
  const states = {
    "sensor.heat_pump_optimizer_solar_irradiance": { state: "120", attributes: {
      forecast: solar, source: "open_meteo", plan_kind: "solar" } },
    "sensor.heat_pump_optimizer_space_heating_plan": { state: "3 slots planned", attributes: {
      forecast, slots: planJson.space_plan.slots,
      total_energy_kwh: planJson.space_plan.total_energy_kwh,
      total_cost: planJson.space_plan.total_cost,
      active_now: planJson.space_plan.active_now, plan_kind: "space" } },
    "sensor.heat_pump_optimizer_dhw_heating_plan": { state: "4 slots planned", attributes: {
      forecast: planJson.dhw_plan.forecast, slots: planJson.dhw_plan.slots,
      total_energy_kwh: planJson.dhw_plan.total_energy_kwh,
      total_cost: planJson.dhw_plan.total_cost,
      active_now: planJson.dhw_plan.active_now, plan_kind: "dhw" } },
  };
  document.body.innerHTML = "";
  const host = document.createElement("div");
  host.id = "hpo-host";
  host.style.width = "100%";
  document.body.appendChild(host);
  const card = document.createElement("heatpump-optimizer-card");
  card.style.display = "block";
  card.setConfig({ type: "custom:heatpump-optimizer-card" });
  card.hass = { states };
  host.appendChild(card);
  await raf();
  card.hass = { states };
  await raf();
  await sleep(60);
  window.__card = card;
  return card;
};

const CASES = [
  { name: "plan_inline", vp: [375, 812], tile: 359, theme: "light", expand: false },
  { name: "plan_inline", vp: [375, 812], tile: 359, theme: "dark", expand: false },
  { name: "plan_inline", vp: [1280, 800], tile: 500, theme: "light", expand: false },
  { name: "expanded_plan", vp: [1280, 800], tile: 500, theme: "light", expand: true },
  { name: "expanded_plan", vp: [1280, 800], tile: 500, theme: "dark", expand: true },
];

const DSF = 2;
const rows = [];
const browser = await chromium.launch();
try {
  for (const c of CASES) {
    // frozen clock, so the editable lane strip is actually drawn
    const frozen = Date.parse(plan.dhw_plan.forecast[0].t) + 6 * 3600 * 1000;
    const ctx = await browser.newContext({
      viewport: { width: c.vp[0], height: c.vp[1] }, deviceScaleFactor: DSF, colorScheme: c.theme });
    const page = await ctx.newPage();
    await page.goto("about:blank");
    await page.addInitScript((f) => {
      const Real = Date;
      class Frozen extends Real {
        constructor(...a) { super(...(a.length ? a : [f])); }
        static now() { return f; }
      }
      window.Date = Frozen;
    }, frozen);
    await page.reload();
    await page.addStyleTag({ content:
      `:root{${Object.entries(THEMES[c.theme]).map(([k, v]) => `${k}:${v}`).join(";")}}` +
      `html,body{margin:0;background:${THEMES[c.theme]["--primary-background-color"]};` +
      `font-family:Roboto,-apple-system,sans-serif;font-size:14px}` +
      `#hpo-host{width:${c.tile}px;margin:0 auto}heatpump-optimizer-card{display:block}` });
    await page.addScriptTag({ content: HA_CARD });
    await page.addScriptTag({ path: CARD_SRC });
    await page.evaluate(MOUNT, plan);
    if (c.expand) {
      await page.evaluate(() => {
        window.__card._onCardClick({});
        return true;
      });
      await page.waitForTimeout(80);
    }
    // scroll the lane strip into view for the raster
    const labels = await page.evaluate(() => {
      const root = window.__card.shadowRoot;
      const out = [];
      for (const svg of root.querySelectorAll(".chartwrap svg")) {
        const r = svg.getBoundingClientRect();
        const vbAttr = (svg.getAttribute("viewBox") || "").split(/\s+/);
        const vbW = Number(vbAttr[2]) || 900;
        const scale = r.width / vbW;
        for (const t of svg.querySelectorAll("text")) {
          const cls = t.getAttribute("class") || "";
          if (!/lane-label/.test(cls)) continue;
          const bb = t.getBBox();
          const b = t.getBoundingClientRect();
          b.x; // touch
          out.push({ text: t.textContent.trim(), bboxH: bb.height * scale,
                     fontAttr: Number(t.getAttribute("font-size")) * scale,
                     x: b.left, y: b.top, w: b.width, h: b.height });
        }
        // floor check: every other chart text with a font-size attr
        for (const t of svg.querySelectorAll("text")) {
          const cls = t.getAttribute("class") || "";
          if (/lane-/.test(cls)) continue;
          if (!(t.getAttribute("font-size") || "").length) continue;
          if (!(t.textContent || "").trim().length) continue;
          out.otherMin = Math.min(out.otherMin === undefined ? Infinity : out.otherMin,
            Number(t.getAttribute("font-size")) * scale);
        }
      }
      return out;
    });
    // scroll the LAST svg (the lane strip) to mid-viewport
    await page.evaluate(() => {
      const svgs = window.__card.shadowRoot.querySelectorAll(".chartwrap svg");
      const last = svgs[svgs.length - 1];
      if (last) last.scrollIntoView({ block: "center" });
    });
    await page.waitForTimeout(50);
    // re-read client boxes after the scroll
    const boxes = await page.evaluate(() => {
      const root = window.__card.shadowRoot;
      const out = [];
      for (const t of root.querySelectorAll("text.lane-label")) {
        const b = t.getBoundingClientRect();
        if (b.width > 0.5 && b.height > 0.5) out.push({
          text: t.textContent.trim(), x: b.left, y: b.top, w: b.width, h: b.height,
          specFill: getComputedStyle(t).fill });
      }
      return out;
    });

    // rasterise on (glyphs) and off (textContent emptied)
    const on = await page.screenshot({ type: "png" });
    await page.evaluate(() => {
      for (const t of window.__card.shadowRoot.querySelectorAll("text.lane-label")) t.textContent = "";
    });
    await page.waitForTimeout(30);
    const off = await page.screenshot({ type: "png" });

    const measured = await page.evaluate(async ([onB64, offB64, boxes, dsf]) => {
      const load = (b64) => new Promise((ok, no) => {
        const img = new Image(); img.onload = () => ok(img); img.onerror = no;
        img.src = "data:image/png;base64," + b64; });
      const [A, B] = await Promise.all([load(onB64), load(offB64)]);
      const cv = document.createElement("canvas");
      cv.width = A.width; cv.height = A.height;
      const g = cv.getContext("2d", { willReadFrequently: true });
      g.drawImage(A, 0, 0);
      const DA = g.getImageData(0, 0, cv.width, cv.height).data;
      g.clearRect(0, 0, cv.width, cv.height);
      g.drawImage(B, 0, 0);
      const DB = g.getImageData(0, 0, cv.width, cv.height).data;
      const L = (c) => {
        const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
        return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); };
      const rr = (a, b) => { const l1 = L(a), l2 = L(b); return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05); };
      const res = [];
      for (const bx of boxes) {
        const x0 = Math.max(0, Math.floor(bx.x * dsf)), x1 = Math.min(cv.width - 1, Math.ceil((bx.x + bx.w) * dsf));
        const y0 = Math.max(0, Math.floor(bx.y * dsf)), y1 = Math.min(cv.height - 1, Math.ceil((bx.y + bx.h) * dsf));
        const cand = [];
        for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) {
          const i = (y * cv.width + x) * 4;
          const d = Math.abs(DA[i] - DB[i]) + Math.abs(DA[i + 1] - DB[i + 1]) + Math.abs(DA[i + 2] - DB[i + 2]);
          if (d > 20) cand.push({ i, d });
        }
        if (!cand.length) { res.push({ ...bx, error: "no glyph pixels" }); continue; }
        cand.sort((p, q) => q.d - p.d);
        const core = cand.slice(0, Math.max(1, Math.round(cand.length * 0.35)));
        const ratios = core.map((p) => rr([DA[p.i], DA[p.i + 1], DA[p.i + 2]], [DB[p.i], DB[p.i + 1], DB[p.i + 2]])).sort((m, n) => m - n);
        // specified fill vs the worst backdrop pixel among core pixels
        const m = String(bx.specFill).match(/rgba?\(([^)]+)\)/);
        let specWorst = null;
        if (m) {
          const q = m[1].split(",").map(Number);
          const spec = [q[0], q[1], q[2]];
          let w = null;
          for (const p of core) {
            const bg = [DB[p.i], DB[p.i + 1], DB[p.i + 2]];
            const r2 = rr(spec, bg);
            if (!w || r2 < w.r) w = { r: r2, bg };
          }
          specWorst = Math.round(w.r * 1000) / 1000;
        }
        res.push({ ...bx, nPx: cand.length,
          medianRatio: Math.round(ratios[Math.floor(ratios.length / 2)] * 1000) / 1000,
          minRatio: Math.round(ratios[0] * 1000) / 1000,
          specWorst, bg: [DB[core[0].i], DB[core[0].i + 1], DB[core[0].i + 2]] });
      }
      return res;
    }, [on.toString("base64"), off.toString("base64"), boxes, DSF]);

    rows.push({ ...c, otherChartTextMinPx: labels.otherMin,
                glyphHeights: labels.filter((l) => l.bboxH !== undefined).map((l) => Math.round(l.bboxH * 100) / 100),
                fontAttrs: labels.filter((l) => l.fontAttr !== undefined).map((l) => Math.round(l.fontAttr * 100) / 100),
                measured });
    await ctx.close();
  }
} finally { await browser.close(); }

writeFileSync(path.join(OUT, "d4_own_D4-01.json"), JSON.stringify(rows, null, 1));
for (const r of rows) {
  const gh = r.glyphHeights.length ? Math.min(...r.glyphHeights) : null;
  const fa = r.fontAttrs.length ? Math.min(...r.fontAttrs) : null;
  const med = r.measured.filter((m) => m.medianRatio != null).map((m) => m.medianRatio);
  const spec = r.measured.filter((m) => m.specWorst != null).map((m) => m.specWorst);
  console.log(`RESULT ${r.name}|${r.vp[0]}x${r.vp[1]}|${r.theme} glyphH_min=${gh} fontAttrPx_min=${fa} otherTextPx_min=${r.otherChartTextMinPx === Infinity || r.otherChartTextMinPx === undefined ? "na" : Math.round(r.otherChartTextMinPx * 100) / 100} ratio_median_min=${med.length ? Math.min(...med) : "na"} ratio_specWorst_min=${spec.length ? Math.min(...spec) : "na"}`);
  for (const m of r.measured) {
    if (m.medianRatio == null) { console.log(`    "${m.text}" ${m.error || "skipped"}`); continue; }
    console.log(`    "${m.text}" glyphPx=${m.nPx} median=${m.medianRatio} min=${m.minRatio} specWorst=${m.specWorst} bg=rgb(${m.bg})`);
  }
}
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log("RESULT thread_factor=1.00 (no CPU-time metric)");
console.log("RESULT swapins=0 (not a memory metric)");
