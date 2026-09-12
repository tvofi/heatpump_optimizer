// D4 round-4 verify-0-3 — verifier 3's own harness, written without reusing the
// finder's measurement code (only the lib/states.js state drivers, which are
// fixtures, and the card source itself).
//
// METRICS (one per finding, all executed in real Chromium 131, dsf=4 where
// rasterised, frozen clock 6 h into the captured day):
//   V3_D4_01_fontpx:  on-screen CSS-px size of every text.lane-label in
//     plan_inline/wood_lane/expanded_plan = font-size attribute x (svg rect
//     width / viewBox width). Bar: the card's own 8 px axis floor.
//   V3_D4_01_contrast: WCAG 2.1 ratio of the SPECIFIED fill of each
//     text.lane-label against the pixel behind each glyph core, from two
//     rasterisations of one frame (labels painted vs fill:transparent).
//     Bar 4.5:1.
//   V3_D4_02_contrast: same two-raster method for button.wi-save under FOUR
//     theme tables: stock_light and stock_dark are derived from Home
//     Assistant's own frontend source (ha-style.ts + darkStyles at tag
//     20250205.0, i.e. the minimum this card supports per hacs.json, and
//     cross-checked at current dev) in which --text-primary-color is #ffffff
//     in BOTH modes (darkStyles does not override it); custom_primary_* is
//     the applyThemesOnElement path where the user customised the default
//     theme's primary colour and HA itself sets --text-primary-color to
//     #212121 in BOTH modes. Bar 4.5:1. Plus the pure arithmetic ratio from
//     computed styles (the fill is opaque, so arithmetic is exact).
//   V3_D4_03_targets: WCAG 2.2 SC 2.5.8 for .vc-in/.vc-out/.vc-reset under
//     fine and coarse pointers (CDP + matchMedia stub): smaller side < 24 and
//     centre distance to the nearest target < 24 (two r=12 circles
//     intersect), i.e. the spacing exception does not rescue.
//
// RUN (from the worktree root):
//   NODE_PATH=/private/tmp/hpo-pw/node_modules \
//   PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers \
//   HPO_PLANDATA=/private/tmp/hpo-d4-v3/plandata.json \
//     node tools/audit/round4/D4/verify3_own.mjs
//
// EXPECTED at claude/13-dimension-audit-920935 (worktree ae2a60b): the
// numbers quoted in tools/audit/round4/D4/verify-0-3.md, tolerance +-0.05 on
// ratios (antialiasing), +-0.05 px on sizes.
import { createRequire } from "node:module";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, "out");
mkdirSync(OUT, { recursive: true });
const repo = path.resolve(__dirname, "../../../..");
const plan = JSON.parse(readFileSync(process.env.HPO_PLANDATA, "utf8"));
const CARD_SRC = path.join(repo, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js");

// ---- theme tables -------------------------------------------------------
// BASE: HA frontend ha-style.ts html{} block (tag 20250205.0 and dev agree on
// these values for the variables the card consumes).  STOCK_DARK: exactly the
// keys HA's darkStyles/darkColorStyles object sets -- and it does NOT contain
// --text-primary-color, which therefore keeps the base #ffffff.  This is the
// attack on the finder's table, which asserts #212121 there.
const BASE = {
  "--primary-text-color": "#212121", "--secondary-text-color": "#727272",
  "--text-primary-color": "#ffffff", "--text-light-primary-color": "#212121",
  "--primary-color": "#03a9f4", "--accent-color": "#ff9800",
  "--card-background-color": "#ffffff", "--primary-background-color": "#fafafa",
  "--secondary-background-color": "#e5e5e5",
  "--divider-color": "rgba(0,0,0,.12)", "--error-color": "#db4437",
  "--warning-color": "#ffa600", "--success-color": "#43a047",
  "--disabled-text-color": "#bdbdbd",
};
const STOCK_DARK_OVERRIDES = { // every key of HA darkStyles that BASE also carries
  "--primary-background-color": "#111111", "--card-background-color": "#1c1c1c",
  "--secondary-background-color": "#282828", "--primary-text-color": "#e1e1e1",
  "--secondary-text-color": "#9b9b9b", "--disabled-text-color": "#6f6f6f",
  "--divider-color": "rgba(225,225,225,.12)",
};
const THEMES = {
  stock_light: BASE,
  stock_dark: { ...BASE, ...STOCK_DARK_OVERRIDES }, // --text-primary-color stays #ffffff
  custom_primary_light: { ...BASE, "--text-primary-color": "#212121" },
  custom_primary_dark: { ...BASE, ...STOCK_DARK_OVERRIDES, "--text-primary-color": "#212121" },
};

const HA_CARD = `
  if (!customElements.get("ha-card")) {
    customElements.define("ha-card", class extends HTMLElement {
      constructor() { super();
        this.attachShadow({ mode: "open" }).innerHTML =
          "<style>:host{background:var(--ha-card-background,var(--card-background-color,white));" +
          "box-sizing:border-box;border-radius:12px;border:1px solid var(--divider-color,#e0e0e0);" +
          "color:var(--primary-text-color);display:block;position:relative;padding:0}</style><slot></slot>"; }
    });
  }
  if (!customElements.get("ha-icon")) {
    customElements.define("ha-icon", class extends HTMLElement {
      connectedCallback(){ this.style.display="inline-block"; this.style.width="24px"; this.style.height="24px"; }
    });
  }`;

const DSF = 4;
const lum = (c) => {
  const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
  return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]);
};
const ratio = (a, b) => (Math.max(lum(a), lum(b)) + 0.05) / (Math.min(lum(a), lum(b)) + 0.05);
const r3 = (x) => Math.round(x * 1000) / 1000;

async function makePage(browser, { vp, tile, theme, pointer, freeze }) {
  const ctx = await browser.newContext({
    viewport: { width: vp[0], height: vp[1] }, deviceScaleFactor: DSF,
    colorScheme: theme.includes("dark") ? "dark" : "light",
  });
  const page = await ctx.newPage();
  const cdp = await ctx.newCDPSession(page);
  await cdp.send("Emulation.setEmulatedMedia", {
    features: [{ name: "pointer", value: pointer }, { name: "any-pointer", value: pointer }],
  });
  await page.goto("about:blank");
  if (freeze) {
    await page.addInitScript((f) => {
      const Real = Date;
      class Frozen extends Real {
        constructor(...a) { super(...(a.length ? a : [f])); }
        static now() { return f; }
      }
      window.Date = Frozen;
    }, freeze);
    await page.reload();
  }
  const t = THEMES[theme];
  await page.addStyleTag({ content:
    `:root{${Object.entries(t).map(([k, v]) => `${k}:${v}`).join(";")}}` +
    `html,body{margin:0;background:${t["--primary-background-color"]};` +
    `font-family:Roboto,-apple-system,"Segoe UI",sans-serif;font-size:14px}` +
    `#hpo-host{width:${tile}px;margin:0 auto}heatpump-optimizer-card{display:block}` });
  await page.addScriptTag({ content: HA_CARD });
  await page.addScriptTag({ path: CARD_SRC });
  await page.addScriptTag({ path: path.join(__dirname, "lib/states.js") });
  await page.evaluate((coarse) => {
    const orig = window.matchMedia.bind(window);
    window.matchMedia = (q) => q === "(pointer: coarse)"
      ? { matches: coarse, media: q, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {} }
      : orig(q);
  }, pointer === "coarse");
  return { ctx, page };
}

const freezeMs = Date.parse(plan.dhw_plan.forecast[0].t) + 6 * 3600 * 1000;
const browser = await chromium.launch();
const results = { d401: [], d402: [], d403: [] };
try {
  // ================= D4-01: lane labels =================
  const d401Cells = [
    { state: "plan_inline", vp: [375, 812], tile: 359, theme: "stock_light" },
    { state: "plan_inline", vp: [375, 812], tile: 359, theme: "stock_dark" },
    { state: "plan_inline", vp: [768, 1024], tile: 736, theme: "stock_light" },
    { state: "expanded_plan", vp: [1280, 800], tile: 500, theme: "stock_light" },
    { state: "expanded_plan", vp: [1280, 800], tile: 500, theme: "stock_dark" },
    { state: "wood_lane", vp: [1280, 800], tile: 500, theme: "stock_light" },
  ];
  for (const cell of d401Cells) {
    const { ctx, page } = await makePage(browser, { ...cell, pointer: "fine", freeze: freezeMs });
    const drive = await page.evaluate(async ([n, p]) => {
      if (!window.__D4.STATES[n]) return { ok: false, note: "missing" };
      return window.__D4.STATES[n](p);
    }, [cell.state, plan]);
    // on-screen font size of every svg text, and which are lane labels
    const texts = await page.evaluate(() => {
      const r3 = (v) => Math.round(v * 100) / 100;
      const root = window.__card.shadowRoot;
      const out = [];
      for (const svg of root.querySelectorAll(".chartwrap svg")) {
        const r = svg.getBoundingClientRect();
        if (!r.width) continue;
        const vb = (svg.getAttribute("viewBox") || "0 0 900 380").split(/\s+/).map(Number);
        const scale = r.width / vb[2];
        for (const t of svg.querySelectorAll("text")) {
          const fs = t.getAttribute("font-size");
          const label = (t.textContent || "").trim();
          if (!fs || !label) continue;
          const b = t.getBoundingClientRect();
          out.push({
            cls: t.getAttribute("class") || "", text: label.slice(0, 24),
            attrFs: Number(fs), onScreenPx: r3(Number(fs) * scale),
            x: b.left, y: b.top, w: b.width, h: b.height,
            fill: getComputedStyle(t).fill,
          });
        }
      }
      return out;
    });
    // pixel contrast for lane labels: two rasters (labels painted vs fill
    // transparent), taken from Node, analysed in-page. A label outside the
    // viewport cannot be rasterised, so the card is scrolled until the lane
    // strip is on screen first (a screenshot cannot paint what is off-screen).
    await page.evaluate(() => {
      const root = window.__card.shadowRoot;
      const first = root.querySelector("text.lane-label");
      if (first) { try { first.scrollIntoView({ block: "center" }); } catch (x) {} }
    });
    const labelBoxes = await page.evaluate(() => {
      const root = window.__card.shadowRoot;
      return [...root.querySelectorAll("text.lane-label")].map((e) => {
        const b = e.getBoundingClientRect();
        const svg = e.ownerSVGElement;
        const sr = svg.getBoundingClientRect();
        const vbW = Number((svg.getAttribute("viewBox") || "0 0 900 380").split(/\s+/)[2]);
        return { text: (e.textContent || "").trim().slice(0, 24),
                 x: b.left, y: b.top, w: b.width, h: b.height,
                 specFill: getComputedStyle(e).fill,
                 onScreenPx: Math.round(Number(e.getAttribute("font-size")) * (sr.width / vbW) * 100) / 100 };
      }).filter((b) => b.w > 0.5 && b.h > 0.5);
    });
    const shots = {};
    for (const mode of ["on", "off"]) {
      await page.evaluate((off) => {
        for (const e of window.__card.shadowRoot.querySelectorAll("text.lane-label")) {
          if (off) e.style.setProperty("fill", "transparent", "important");
          else e.style.removeProperty("fill");
        }
      }, mode === "off");
      shots[mode] = await page.screenshot({ type: "png" });
    }
    const measured = await page.evaluate(async ([onB64, offB64, boxes, dsf]) => {
      const load = (b64) => new Promise((ok, no) => {
        const img = new Image(); img.onload = () => ok(img); img.onerror = no;
        img.src = "data:image/png;base64," + b64;
      });
      const [A, B] = await Promise.all([load(onB64), load(offB64)]);
      const cv = document.createElement("canvas");
      cv.width = A.width; cv.height = A.height;
      const g = cv.getContext("2d", { willReadFrequently: true });
      g.drawImage(A, 0, 0); const DA = g.getImageData(0, 0, cv.width, cv.height).data;
      g.clearRect(0, 0, cv.width, cv.height);
      g.drawImage(B, 0, 0); const DB = g.getImageData(0, 0, cv.width, cv.height).data;
      const spec = (c) => { const m = String(c).match(/rgba?\(([^)]+)\)/); if (!m) return null;
        const q = m[1].split(/[,\s/]+/).filter(Boolean).map(Number); return [q[0], q[1], q[2]]; };
      const rr = (a, b) => {
        const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
        const L = (c) => 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]);
        return (Math.max(L(a), L(b)) + 0.05) / (Math.min(L(a), L(b)) + 0.05);
      };
      const out = [];
      const r3 = (v) => Math.round(v * 1000) / 1000;
      for (const bx of boxes) {
        const x0 = Math.max(0, Math.floor(bx.x * dsf) - 1), x1 = Math.min(cv.width - 1, Math.ceil((bx.x + bx.w) * dsf) + 1);
        const y0 = Math.max(0, Math.floor(bx.y * dsf) - 1), y1 = Math.min(cv.height - 1, Math.ceil((bx.y + bx.h) * dsf) + 1);
        const cand = [];
        for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) {
          const i = (y * cv.width + x) * 4;
          const d = Math.abs(DA[i] - DB[i]) + Math.abs(DA[i + 1] - DB[i + 1]) + Math.abs(DA[i + 2] - DB[i + 2]);
          if (d > 12) cand.push({ i, d });
        }
        if (!cand.length) { out.push({ ...bx, error: "no glyph px" }); continue; }
        cand.sort((p, q) => q.d - p.d);
        const core = cand.slice(0, Math.max(1, Math.round(cand.length * 0.2)));
        const fg = spec(bx.specFill);
        let worst = null, worstBg = null;
        const all = [];
        for (const p of core) {
          const bg = [DB[p.i], DB[p.i + 1], DB[p.i + 2]];
          const r2 = fg ? rr(fg, bg) : null;
          if (r2 != null) { all.push(r2); if (!worst || r2 < worst) { worst = r2; worstBg = bg; } }
        }
        all.sort((a, b) => a - b);
        out.push({ ...bx, glyphPx: cand.length,
                   specWorst: worst != null ? r3(worst) : null, specBg: worstBg,
                   specMedian: all.length ? r3(all[Math.floor(all.length / 2)]) : null });
      }
      return out;
    }, [shots.on.toString("base64"), shots.off.toString("base64"), labelBoxes, DSF]);
    results.d401.push({ ...cell, drive_ok: drive && drive.ok,
                        texts: texts.length, laneLabels: measured,
                        sub8_nonlane: texts.filter((t) => !/lane-/.test(t.cls) && t.onScreenPx < 8 - 0.05).length,
                        sub8_lane: texts.filter((t) => /lane-/.test(t.cls) && t.onScreenPx < 8 - 0.05).length });
    await ctx.close();
  }

  // ================= D4-02: wi-save under four theme tables =================
  for (const theme of ["stock_light", "stock_dark", "custom_primary_light", "custom_primary_dark"]) {
    const { ctx, page } = await makePage(browser, { vp: [1280, 800], tile: 500, theme, pointer: "fine", freeze: freezeMs });
    const drive = await page.evaluate(async ([n, p]) => window.__D4.STATES[n](p), ["expanded_plan", plan]);
    const arith = await page.evaluate(() => {
      const b = window.__card.shadowRoot.querySelector(".wi-save");
      if (!b) return null;
      const st = getComputedStyle(b);
      return { label: (b.textContent || "").trim(), color: st.color, bg: st.backgroundColor };
    });
    const spec = (c) => { const m = String(c).match(/rgba?\(([^)]+)\)/); if (!m) return null;
      const q = m[1].split(/[,\s/]+/).filter(Boolean).map(Number); return [q[0], q[1], q[2]]; };
    const arithRatio = arith && spec(arith.color) && spec(arith.bg) ? r3(ratio(spec(arith.color), spec(arith.bg))) : null;
    // pixel measurement, same two-raster idea, button glyphs only
    await page.evaluate(() => {
      const b = window.__card.shadowRoot.querySelector(".wi-save");
      if (b) { try { b.scrollIntoView({ block: "center" }); } catch (x) {} }
    });
    const box = await page.evaluate(() => {
      const b = window.__card.shadowRoot.querySelector(".wi-save");
      const r = b.getBoundingClientRect();
      return { x: r.left, y: r.top, w: r.width, h: r.height, specFg: getComputedStyle(b).color };
    });
    const shots = {};
    for (const mode of ["on", "off"]) {
      await page.evaluate((off) => {
        const b = window.__card.shadowRoot.querySelector(".wi-save");
        if (off) {
          b.style.setProperty("color", "transparent", "important");
          b.style.setProperty("-webkit-text-fill-color", "transparent", "important");
        } else {
          b.style.removeProperty("color");
          b.style.removeProperty("-webkit-text-fill-color");
        }
      }, mode === "off");
      shots[mode] = await page.screenshot({ type: "png" });
    }
    const pix = await page.evaluate(async ([onB64, offB64, bx, dsf]) => {
      const load = (b64) => new Promise((ok, no) => {
        const img = new Image(); img.onload = () => ok(img); img.onerror = no;
        img.src = "data:image/png;base64," + b64;
      });
      const [A, B] = await Promise.all([load(onB64), load(offB64)]);
      const cv = document.createElement("canvas"); cv.width = A.width; cv.height = A.height;
      const g = cv.getContext("2d", { willReadFrequently: true });
      g.drawImage(A, 0, 0); const DA = g.getImageData(0, 0, cv.width, cv.height).data;
      g.clearRect(0, 0, cv.width, cv.height); g.drawImage(B, 0, 0);
      const DB = g.getImageData(0, 0, cv.width, cv.height).data;
      const x0 = Math.max(0, Math.floor(bx.x * dsf) - 1), x1 = Math.min(cv.width - 1, Math.ceil((bx.x + bx.w) * dsf) + 1);
      const y0 = Math.max(0, Math.floor(bx.y * dsf) - 1), y1 = Math.min(cv.height - 1, Math.ceil((bx.y + bx.h) * dsf) + 1);
      const m = String(bx.specFg).match(/rgba?\(([^)]+)\)/);
      const fg = m ? m[1].split(/[,\s/]+/).filter(Boolean).map(Number).slice(0, 3) : null;
      let worst = null, worstBg = null, n = 0;
      for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) {
        const i = (y * cv.width + x) * 4;
        const d = Math.abs(DA[i] - DB[i]) + Math.abs(DA[i + 1] - DB[i + 1]) + Math.abs(DA[i + 2] - DB[i + 2]);
        if (d <= 12) continue;
        n += 1;
        const bg = [DB[i], DB[i + 1], DB[i + 2]];
        const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
        const L = (c) => 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]);
        const rr = (Math.max(L(fg), L(bg)) + 0.05) / (Math.min(L(fg), L(bg)) + 0.05);
        if (worst == null || rr < worst) { worst = rr; worstBg = bg; }
      }
      return { glyphPx: n, worst: worst != null ? Math.round(worst * 1000) / 1000 : null, bg: worstBg };
    }, [shots.on.toString("base64"), shots.off.toString("base64"), box, DSF]);
    results.d402.push({ theme, drive_ok: drive && drive.ok, arith, arithRatio, pixel: pix });
    await ctx.close();
  }

  // ================= D4-03: zoom targets =================
  const d403Cells = [
    { state: "plan_inline", vp: [1280, 800], tile: 500, pointer: "fine" },
    { state: "plan_inline", vp: [768, 1024], tile: 736, pointer: "fine" },
    { state: "plan_inline", vp: [375, 812], tile: 359, pointer: "fine" },
    { state: "expanded_plan", vp: [375, 812], tile: 359, pointer: "fine" },
    { state: "plan_inline", vp: [375, 812], tile: 359, pointer: "coarse" },
    { state: "expanded_plan", vp: [375, 812], tile: 359, pointer: "coarse" },
  ];
  for (const cell of d403Cells) {
    const { ctx, page } = await makePage(browser, { ...cell, theme: "stock_light", freeze: freezeMs });
    const drive = await page.evaluate(async ([n, p]) => window.__D4.STATES[n](p), [cell.state, plan]);
    const buttons = await page.evaluate(() => {
      const r3 = (v) => Math.round(v * 100) / 100;
      const out = [];
      for (const svgHost of [window.__card.shadowRoot]) {
        for (const b of svgHost.querySelectorAll(".viewctl button")) {
          const r = b.getBoundingClientRect();
          if (r.width < 0.01) continue;
          out.push({ cls: b.className, disabled: b.disabled,
                     w: r3(r.width), h: r3(r.height),
                     cx: r.left + r.width / 2, cy: r.top + r.height / 2 });
        }
      }
      return out;
    });
    const pair = [];
    for (const t of buttons) {
      let nearest = null;
      for (const o of buttons) {
        if (o === t || o.disabled) continue;
        const d = Math.hypot(o.cx - t.cx, o.cy - t.cy);
        if (!nearest || d < nearest.d) nearest = { d: r3(d), cls: o.cls };
      }
      const under = Math.min(t.w, t.h) < 24 - 0.05;
      pair.push({ ...t, under24: under, nearest,
                  fails_2_5_8: under && nearest && nearest.d < 24 - 0.05 });
    }
    results.d403.push({ ...cell, drive_ok: drive && drive.ok, buttons: pair });
    await ctx.close();
  }
} finally { await browser.close(); }

writeFileSync(path.join(OUT, "verify3_own.json"), JSON.stringify(results, null, 1));

// ---- RESULT lines ----
for (const c of results.d401) {
  const lanes = c.laneLabels.filter((l) => l.specWorst != null);
  const fonts = c.laneLabels.map((l) => l.onScreenPx);
  console.log(`RESULT V3_D4_01 ${c.state}|${c.vp[0]}x${c.vp[1]}|${c.theme} drive_ok=${c.drive_ok} n_labels=${c.laneLabels.length}` +
    (fonts.length ? ` font_min=${Math.min(...fonts)} font_max=${Math.max(...fonts)}` : "") +
    (lanes.length ? ` spec_worst=${Math.min(...lanes.map((l) => l.specWorst))} spec_best=${Math.max(...lanes.map((l) => l.specWorst))}` : "") +
    ` sub8_nonlane=${c.sub8_nonlane} sub8_lane=${c.sub8_lane}`);
  for (const l of lanes) console.log(`    "${l.text}" ${l.onScreenPx}px specWorst=${l.specWorst} specMedian=${l.specMedian} bg=rgb(${l.specBg}) glyphPx=${l.glyphPx}`);
}
for (const c of results.d402) {
  console.log(`RESULT V3_D4_02 ${c.theme} drive_ok=${c.drive_ok} arith=${c.arithRatio} pixel_worst=${c.pixel.worst} bg=rgb(${c.pixel.bg}) glyphPx=${c.pixel.glyphPx} label="${c.arith && c.arith.label}"`);
}
for (const c of results.d403) {
  const f = c.buttons.filter((b) => b.fails_2_5_8);
  console.log(`RESULT V3_D4_03 ${c.state}|${c.vp[0]}x${c.vp[1]}|${c.pointer} drive_ok=${c.drive_ok} buttons=${c.buttons.length} failing=${f.length}`);
  for (const b of c.buttons) {
    console.log(`    .${b.cls} ${b.w}x${b.h} disabled=${b.disabled} under24=${b.under24} nearest=${b.nearest ? b.nearest.d + " (." + b.nearest.cls + ")" : "na"} fails=${b.fails_2_5_8}`);
  }
}
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log("RESULT thread_factor=1.00 (no CPU-time metric)");
console.log("RESULT swapins=0 (not a memory metric)");
