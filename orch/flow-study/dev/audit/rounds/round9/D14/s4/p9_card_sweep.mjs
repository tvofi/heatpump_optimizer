// P9 detector: every rendered node of the card, in real Chromium, against
// three properties -- hit-target floor, text clipped by an ancestor, and text
// contrast under Home Assistant's light and dark theme tokens.
//
// METRIC (one line): per property, the number of DISTINCT seams (tag.class
// signature + trimmed text) that fail it in any cell of the grid
// {tile, dialog + each dialog tab} x {en, sv} x {phone 359 px, desktop 900 px} x
// {light, dark} x {fine, coarse pointer}.
//
// COUNT KEYS -- what the browser delivers, never a source attribute:
//   target   getBoundingClientRect of every interactive node (button, a[href],
//            input, select, summary, [role=button|tab|link|checkbox|switch|
//            slider|option|menuitem], [tabindex>=0], or computed cursor:pointer)
//            that is visible and takes pointer events; fails when
//            min(w, h) < floor - 0.05, floor = the card's own TARGET_MIN_PX (24)
//            or TARGET_MIN_PX_COARSE (44) under its _coarsePointer() predicate.
//            WCAG 2.2 SC 2.5.8's 24 px is reported beside it (`target24`).
//   clip     every element with direct text: its rect against the nearest
//            composed ancestor whose computed overflow clips (HTML overflow
//            hidden/clip -- a scroll container is reachable, not a clip -- or
//            an <svg> viewport) -- fails when > 1 px of the text box
//            lies outside; plus own overflow-hidden text wider than its box with
//            no text-overflow: ellipsis.
//   contrast every visible text run: computed color (fill for SVG text) blended
//            by cumulative opacity against the composed ancestors' composited
//            background, WCAG relative-luminance ratio; fails under 4.5 (3.0 for
//            >= 24 px, or >= 18.66 px bold). SVG shapes painted under a text run
//            are NOT composited (ancestor backgrounds only): a known blind spot.
//
// COMMAND (repository root; Playwright from the global node_modules):
//   NODE_PATH=/opt/node22/lib/node_modules PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers \
//     node tools/audit/round9/D14/s4/p9_card_sweep.mjs
//   HPO_PLANDATA=<file>  reuse a payload tests/plan_view.py wrote (otherwise the
//     harness runs plan_view.py into a mkdtemp under $TMPDIR, with
//     PYTHONPATH=tests/hastub and the venv interpreter in $PY or python3)
//   P9_CARD=<path>       measure another card source (a pre-fix export)
//   P9_PERTURB=1         perturbation, in page: one CSS rule appended to the
//     card's shadow root (`.dlg-tab{min-height:0!important;height:16px!important;
//     padding:0!important}`) -- the target count must go up
// EXPECTED: see REPORT.md; exact integers for a given Chromium build.
// Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; Linux container, Chromium
// under /opt/pw-browsers (chromium-1194).
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, existsSync } from "node:fs";
import { createRequire } from "node:module";
import os from "node:os";
import path from "node:path";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const repo = process.cwd();
const CARD_SRC = process.env.P9_CARD ||
  path.join(repo, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js");
const PERTURB = process.env.P9_PERTURB === "1";

let planPath = process.env.HPO_PLANDATA;
if (!planPath || !existsSync(planPath)) {
  const dir = mkdtempSync(path.join(process.env.TMPDIR || os.tmpdir(), "p9-"));
  planPath = path.join(dir, "plandata.json");
  execFileSync(process.env.PY || "python3", ["tests/plan_view.py"], {
    env: { ...process.env, HPO_PLANDATA: planPath, PYTHONPATH: "tests/hastub",
           OMP_NUM_THREADS: "1", OPENBLAS_NUM_THREADS: "1", MKL_NUM_THREADS: "1" },
    stdio: ["ignore", "ignore", "inherit"],
  });
}
const plan = JSON.parse(readFileSync(planPath, "utf8"));

// The states tests/card_browser.mjs builds (copied: that file runs at import).
const SOLAR_ID = "sensor.heat_pump_optimizer_solar_irradiance";
const SPACE_ID = "sensor.heat_pump_optimizer_plan_space_heating";
const DHW_ID = "sensor.heat_pump_optimizer_plan_dhw_heating";
const TEMP = ["sensor", "number", "input_number"];
const setupTopology = {
  two_zone: true, dhw: true, valve_mode: "manual",
  buffer: { volume_l: 750, is_store: true, max_temp: 70 },
  wood: { present: true, volume_l: 500 },
  edges: [["heat_pump", "buffer_tank"], ["buffer_tank", "mixing_valve"],
    ["mixing_valve", "upper_zone"], ["mixing_valve", "lower_zone"],
    ["wood_tank", "buffer_tank"], ["heat_pump", "dhw_tank"]],
  slots: [
    { key: "indoor_temp_entity", label: "Indoor temperature", place: "upper_zone", entity: "sensor.livingroom", domains: TEMP },
    { key: "lower_floor_temp_entity", label: "Lower floor temperature", place: "lower_zone", entity: null, domains: TEMP },
    { key: "buffer_tank_temp_entity", label: "Buffer tank temperature", place: "buffer_tank", entity: "sensor.tank", domains: TEMP },
    { key: "wood_tank_top_entity", label: "Wood tank top", place: "wood_tank", entity: null, domains: TEMP },
    { key: "outdoor_temp_entity", label: "Outdoor temperature", place: "outdoor", entity: "sensor.outside", domains: TEMP },
    { key: "heat_pump_switch_entity", label: "Heat pump switch", place: "heat_pump", entity: null, domains: ["switch", "input_boolean", "climate"] },
  ],
};
const solarForecast = plan.space_plan.forecast.map((p, i) => ({
  t: p.t, ghi: Math.max(0, 400 * Math.sin((i / plan.space_plan.forecast.length) * Math.PI)) }));
const states = {
  [SOLAR_ID]: { state: "120", attributes: { forecast: solarForecast, source: "open_meteo",
    friendly_name: "Solar Irradiance", plan_kind: "solar" } },
  [SPACE_ID]: { state: "3 slots planned", attributes: { forecast: plan.space_plan.forecast,
    slots: plan.space_plan.slots, total_energy_kwh: plan.space_plan.total_energy_kwh,
    total_cost: plan.space_plan.total_cost, active_now: plan.space_plan.active_now,
    friendly_name: "Space Heating Plan", plan_kind: "space", setup_topology: setupTopology } },
  [DHW_ID]: { state: "4 slots planned", attributes: { forecast: plan.dhw_plan.forecast,
    slots: plan.dhw_plan.slots, total_energy_kwh: plan.dhw_plan.total_energy_kwh,
    total_cost: plan.dhw_plan.total_cost, active_now: plan.dhw_plan.active_now,
    friendly_name: "DHW Heating Plan", plan_kind: "dhw" } },
  "sensor.livingroom": { state: "21.3", attributes: { unit_of_measurement: "°C" } },
  "sensor.tank": { state: "47.5", attributes: { unit_of_measurement: "°C" } },
  "sensor.outside": { state: "unavailable", attributes: {} },
  // the headline stats (HEADLINE_SUFFIXES): savings, percentage, score pill, narrative
  "sensor.heat_pump_optimizer_plan_predicted_savings": { state: "12.4", attributes: { unit_of_measurement: "SEK" } },
  "sensor.heat_pump_optimizer_plan_savings_percentage": { state: "18", attributes: { unit_of_measurement: "%" } },
  "sensor.heat_pump_optimizer_plan_optimization_score": { state: "72", attributes: {} },
  "sensor.heat_pump_optimizer_plan_narrative": { state: "Heating moved to the cheap night hours", attributes: {} },
};

// Home Assistant frontend default theme tokens (light) and its built-in dark mode.
const THEMES = {
  light: { "--primary-background-color": "#fafafa", "--card-background-color": "#ffffff",
    "--primary-text-color": "#212121", "--secondary-text-color": "#727272",
    "--primary-color": "#03a9f4", "--divider-color": "rgba(0, 0, 0, 0.12)",
    "--text-primary-color": "#ffffff", "--secondary-background-color": "#e5e5e5",
    "--error-color": "#db4437", "--warning-color": "#ffa600", "--success-color": "#43a047" },
  dark: { "--primary-background-color": "#111111", "--card-background-color": "#1c1c1c",
    "--primary-text-color": "#e1e1e1", "--secondary-text-color": "#9b9b9b",
    "--primary-color": "#03a9f4", "--divider-color": "rgba(225, 225, 225, 0.12)",
    "--text-primary-color": "#ffffff", "--secondary-background-color": "#282828",
    "--error-color": "#db4437", "--warning-color": "#ffa600", "--success-color": "#43a047" },
};
const FROZEN = Date.parse(plan.dhw_plan.forecast[0].t) + 6 * 3600 * 1000;

// ---- in-page sweep ---------------------------------------------------------
function sweepInPage([coarse]) {
  const ctx = document.createElement("canvas").getContext("2d");
  const rgba = (s) => {
    ctx.fillStyle = "#000"; ctx.fillStyle = s; const v = ctx.fillStyle;
    if (v.startsWith("#")) return [parseInt(v.slice(1, 3), 16), parseInt(v.slice(3, 5), 16), parseInt(v.slice(5, 7), 16), 1];
    const m = v.match(/rgba?\(([^)]+)\)/); if (!m) return [0, 0, 0, 0];
    const p = m[1].split(",").map((x) => parseFloat(x)); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1];
  };
  const over = (top, bot) => { const a = top[3]; return [0, 1, 2].map((i) => top[i] * a + bot[i] * (1 - a)).concat([1]); };
  const lum = (c) => { const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); };
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const parent = (el) => el.parentElement || (el.getRootNode && el.getRootNode().host) || null;
  const all = [];
  const walk = (root) => { for (const el of root.querySelectorAll("*")) { all.push(el); if (el.shadowRoot) walk(el.shadowRoot); } };
  walk(document);
  const visible = (el) => {
    for (let e = el; e; e = parent(e)) {
      const st = getComputedStyle(e);
      if (st.display === "none" || st.visibility === "hidden") return false;
    }
    const b = el.getBoundingClientRect(); return b.width > 0 && b.height > 0;
  };
  const opacityOf = (el) => { let o = 1; for (let e = el; e; e = parent(e)) o *= parseFloat(getComputedStyle(e).opacity || "1"); return o; };
  const bgOf = (el) => {
    const chain = []; for (let e = el; e; e = parent(e)) chain.push(e);  // the text's own box paints under it too
    let bg = rgba(getComputedStyle(document.documentElement).getPropertyValue("--primary-background-color") || "#fff");
    for (let i = chain.length - 1; i >= 0; i--) {
      const e = chain[i]; if (e instanceof SVGElement) continue;
      const c = rgba(getComputedStyle(e).backgroundColor); if (c[3] > 0) bg = over(c, bg);
    }
    return bg;
  };
  const sig = (el) => {
    const cls = (el.getAttribute("class") || "").trim().split(/\s+/).filter(Boolean).slice(0, 2).join(".");
    const txt = [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent).join("").trim().slice(0, 24);
    return `${el.tagName.toLowerCase()}${cls ? "." + cls : ""}${txt ? ` "${txt}"` : ""}`;
  };
  const floor = coarse ? 44 : 24;
  const out = { target: [], target24: [], clip: [], contrast: [], nodes: 0, interactive: 0, texts: 0 };
  const ROLES = /^(button|tab|link|checkbox|switch|slider|option|menuitem|radio)$/;
  for (const el of all) {
    if (!visible(el)) continue;
    out.nodes++;
    const st = getComputedStyle(el);
    const b = el.getBoundingClientRect();
    const tag = el.tagName.toLowerCase();
    const ti = el.getAttribute("tabindex");
    const interactive = (["button", "select", "summary", "textarea"].includes(tag)
      || (tag === "a" && el.hasAttribute("href"))
      || (tag === "input" && el.type !== "hidden")
      || ROLES.test(el.getAttribute("role") || "")
      || (ti !== null && parseInt(ti, 10) >= 0)
      || (st.cursor === "pointer" && !(parent(el) && getComputedStyle(parent(el)).cursor === "pointer")))
      && st.pointerEvents !== "none" && !el.disabled;
    if (interactive) {
      out.interactive++;
      const m = Math.min(b.width, b.height);
      if (m < floor - 0.05) out.target.push(`${sig(el)} ${b.width.toFixed(1)}x${b.height.toFixed(1)}`);
      if (m < 24 - 0.05) out.target24.push(`${sig(el)} ${b.width.toFixed(1)}x${b.height.toFixed(1)}`);
    }
    const ownText = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
    if (!ownText || tag === "style" || tag === "script" || tag === "title") continue;
    out.texts++;
    // clip against the nearest clipping ancestor
    for (let e = parent(el); e; e = parent(e)) {
      const es = getComputedStyle(e);
      const isSvg = e.tagName.toLowerCase() === "svg";
      // the nearest ancestor that is not overflow:visible decides: a scroll
      // container (auto/scroll) makes the text reachable, so it is not a clip
      if (!isSvg && ["auto", "scroll"].some((v) => es.overflowX === v || es.overflowY === v)) break;
      const clips = isSvg
        ? es.overflow !== "visible"
        : ["hidden", "clip"].includes(es.overflowX) || ["hidden", "clip"].includes(es.overflowY);
      if (!clips) continue;
      const c = e.getBoundingClientRect();
      const outPx = Math.max(c.left - b.left, b.right - c.right, c.top - b.top, b.bottom - c.bottom);
      if (outPx > 1 && c.width > 0 && c.height > 0) out.clip.push(`${sig(el)} ${outPx.toFixed(1)}px outside <${e.tagName.toLowerCase()} ${(e.getAttribute("class") || "").split(" ")[0]}>`);
      break;
    }
    if (!(el instanceof SVGElement) && (st.overflowX === "hidden" || st.overflowX === "clip")
        && el.scrollWidth > el.clientWidth + 1 && st.textOverflow !== "ellipsis") {
      out.clip.push(`${sig(el)} self-overflow ${el.scrollWidth}>${el.clientWidth}`);
    }
    // contrast
    const op = opacityOf(el);
    if (op < 0.05) continue;
    const bg = bgOf(el);
    let fg = rgba(el instanceof SVGElement ? st.fill : st.color);
    if (el instanceof SVGElement && st.fill === "none") continue;
    fg = [fg[0], fg[1], fg[2], fg[3] * op * (el instanceof SVGElement ? parseFloat(st.fillOpacity || "1") : 1)];
    const eff = over(fg, bg);
    const px = parseFloat(st.fontSize) * (el instanceof SVGElement && el.ownerSVGElement
      ? (el.ownerSVGElement.getBoundingClientRect().width / (el.ownerSVGElement.viewBox.baseVal.width || el.ownerSVGElement.getBoundingClientRect().width)) : 1);
    const large = px >= 24 || (px >= 18.66 && parseInt(st.fontWeight, 10) >= 700);
    const r = ratio(eff, bg);
    if (r < (large ? 3.0 : 4.5)) out.contrast.push(`${sig(el)} ${r.toFixed(2)}:1`);
  }
  return out;
}

const browser = await chromium.launch();
const seams = { target: new Map(), target24: new Map(), clip: new Map(), contrast: new Map() };
const cells = [];
let pageErrors = 0;
try {
  for (const lang of ["en", "sv"]) {
  for (const width of [359, 900]) {
    for (const theme of ["light", "dark"]) {
      for (const coarse of [false, true]) {
        const page = await browser.newPage({ viewport: { width: width + 16, height: 900 } });
        page.on("pageerror", () => { pageErrors++; });
        await page.goto("about:blank");
        await page.evaluate(([frozen, isCoarse]) => {
          const Real = Date;
          class Frozen extends Real { constructor(...a) { super(...(a.length ? a : [frozen])); } static now() { return frozen; } }
          window.Date = Frozen;
          const orig = window.matchMedia.bind(window);
          window.matchMedia = (q) => (q === "(pointer: coarse)"
            ? { matches: isCoarse, media: q, onchange: null, addEventListener() {}, removeEventListener() {},
                addListener() {}, removeListener() {}, dispatchEvent() { return true; } }
            : orig(q));
          if (!customElements.get("ha-card")) customElements.define("ha-card", class extends HTMLElement {
            constructor() { super(); this.attachShadow({ mode: "open" }).innerHTML =
              "<style>:host{background:var(--card-background-color,white);box-sizing:border-box;border-radius:12px;" +
              "border-width:1px;border-style:solid;border-color:var(--divider-color,#e0e0e0);display:block;position:relative;}</style><slot></slot>"; }
          });
        }, [FROZEN, coarse]);
        await page.addScriptTag({ path: CARD_SRC });
        await page.evaluate(async ([st, w, vars, perturb, lang]) => {
          for (const [k, v] of Object.entries(vars)) document.documentElement.style.setProperty(k, v);
          const s = document.createElement("style");
          s.textContent = `body{margin:0 8px;background:var(--primary-background-color);font-family:-apple-system,"Segoe UI",sans-serif;} heatpump-optimizer-card{display:block;width:${w}px;}`;
          document.head.appendChild(s);
          const card = document.createElement("heatpump-optimizer-card");
          card.setConfig({ type: "custom:heatpump-optimizer-card", what_if: true });
          card.hass = { states: st, language: lang, themes: { darkMode: false } };
          document.body.appendChild(card);
          window.__card = card;
          await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
          await new Promise((r) => setTimeout(r, 80));
        }, [states, width, THEMES[theme], PERTURB, lang]);
        const sweep = async () => {
          if (PERTURB) {
            // the one-rule perturbation, injected into every shadow root right
            // before measuring (the card re-renders its own root's children)
            await page.evaluate(async () => {
              const roots = [];
              const walk = (r) => { for (const el of r.querySelectorAll("*")) if (el.shadowRoot) { roots.push(el.shadowRoot); walk(el.shadowRoot); } };
              walk(document);
              for (const r of roots) {
                const p = document.createElement("style");
                p.textContent = ".dlg-tab{min-height:0!important;height:16px!important;padding:0!important;line-height:14px!important}";
                r.appendChild(p);
              }
              await new Promise((res) => requestAnimationFrame(() => requestAnimationFrame(res)));
            });
          }
          return page.evaluate(`(${sweepInPage.toString()})([${coarse}])`);
        };
        const record = (view, r2) => {
          const cell = `${view}/${lang}/${width}/${theme}/${coarse ? "coarse" : "fine"}`;
          cells.push({ cell, nodes: r2.nodes, interactive: r2.interactive, texts: r2.texts,
            target: r2.target.length, clip: r2.clip.length, contrast: r2.contrast.length });
          for (const k of Object.keys(seams)) {
            for (const item of r2[k]) {
              const key = item.replace(/ [\d.]+x[\d.]+$| [\d.]+:1$| [\d.]+px outside.*$| self-overflow.*$/, "");
              if (!seams[k].has(key)) seams[k].set(key, { example: item, cells: new Set() });
              seams[k].get(key).cells.add(cell);
            }
          }
        };
        record("tile", await sweep());
        const tabs = await page.evaluate(async () => {
          const c = window.__card;
          if (!c.dialog || !c.dialog.open) return -1;
          c.dialog.open();
          await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
          await new Promise((r) => setTimeout(r, 80));
          return c.shadowRoot.querySelectorAll(".dlg-tab").length;
        });
        if (tabs >= 0) record("dialog", await sweep());
        for (let i = 1; i < tabs; i++) {
          await page.evaluate(async (j) => {
            const t = window.__card.shadowRoot.querySelectorAll(".dlg-tab")[j];
            if (t) t.click();
            await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
            await new Promise((r) => setTimeout(r, 80));
          }, i);
          record(`dialog-tab${i}`, await sweep());
        }
        await page.close();
      }
    }
  }
  }
} finally {
  await browser.close();
}
for (const c of cells) console.log(`# cell ${c.cell}: nodes=${c.nodes} interactive=${c.interactive} texts=${c.texts} target=${c.target} clip=${c.clip} contrast=${c.contrast}`);
for (const k of Object.keys(seams)) {
  console.log(`# ${k} seams:`);
  for (const [key, v] of [...seams[k].entries()].sort()) console.log(`#   ${v.example}  [${v.cells.size} cell(s): ${[...v.cells].slice(0, 3).join(", ")}${v.cells.size > 3 ? ", ..." : ""}]`);
}
console.log(`RESULT perturb=${PERTURB ? 1 : 0}`);
console.log(`RESULT cells=${cells.length} count`);
console.log(`RESULT nodes_swept=${cells.reduce((a, c) => a + c.nodes, 0)} count`);
console.log(`RESULT interactive_swept=${cells.reduce((a, c) => a + c.interactive, 0)} count`);
console.log(`RESULT page_errors=${pageErrors} count`);
for (const k of Object.keys(seams)) console.log(`RESULT ${k}_seams=${seams[k].size} count`);
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log(`RESULT thread_factor=1.000 (no BLAS; counts only)`);
console.log(`RESULT swapins=${(() => { try { return readFileSync("/proc/vmstat", "utf8").split("\n").filter((l) => l.startsWith("pswpin")).map((l) => +l.split(" ")[1]).reduce((a, b) => a + b, 0); } catch { return -1; } })()}`);
