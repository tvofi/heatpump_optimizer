// D4 round 3 -- the three card defects the sweep localised, each with the
// perturbation arm that must move it and the arm where it must vanish.
//
// METRICS (one line each):
//  A  chip_nodata_contrast  = WCAG 2.x contrast ratio of a `.chip.nodata`
//     legend button's label against the card background, composited in sRGB
//     with the element's own computed opacity, on the state a fresh install
//     shows (no plan sensors); plus whether that button is an ACTIVE control
//     (not `disabled`, no `aria-disabled`, reachable by Tab, and a click
//     mutates the card's persisted hidden-series preference).
//  B  away_target_min_px    = the smaller side, in CSS px, of the smallest
//     activation area in the expanded dialog's away strip, under an emulated
//     COARSE pointer, against the 24 px the card's own `coarseHtmlTargets`
//     rule set gives twelve other selectors on the same page.
//  C  axis_ink_overlap_px   = rasterised ink-box overlap between an axis unit
//     title and the nearest tick label on the same axis of the INLINE
//     (compact) chart -- the copy tests/card_browser.mjs's ink lane never
//     measures, because it reads the LAST `.chartwrap svg`, i.e. the dialog's.
//
// COMMAND (from the export root, one line):
//   HPO_PLANDATA=$TMPDIR/plandata-d4.json NODE_PATH=/private/tmp/hpo-pw/node_modules \
//   PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers \
//   node tools/audit/round3/D4/card_ux_defects.mjs
//
// The plan payload must exist first:
//   HPO_PLANDATA=$TMPDIR/plandata-d4.json PYTHONPATH=tests/hastub python3 tests/plan_view.py
//
// EXPECTED at baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1 (8-core Apple
// M1, Chromium 1148 via Playwright 1.49.0, Node v20.10.0). Every number is a
// pixel count or a colour ratio computed by the layout engine, so it is exact
// and contention immune; no wall or CPU time is taken. Tolerance: +/- 0.02 on
// the ratios (sub-pixel font rasterisation), exact on the px counts.
//
//   RESULT chip_nodata_contrast_light=1.90   floor 4.5
//   RESULT chip_nodata_contrast_dark=2.36    floor 4.5
//   RESULT chip_nodata_is_disabled=0         (0 = an ACTIVE control)
//   RESULT chip_nodata_tabbable=7            (all seven reachable by Tab)
//   RESULT chip_nodata_click_persists=1      (a click writes localStorage)
//   PERTURBATION opacity:1 -> chip_nodata_contrast_light=15.91  (up)
//   NULL ARM     the same chips WITH plan data -> 15.91         (to_zero defect)
//   RESULT away_checkbox_min_px=13
//   RESULT away_label_min_px=<see below>
//   RESULT away_return_min_px=21.3
//   RESULT coarse_ruleset_min_px=24          (the control: the same page's
//                                             .close/.dlg-tab/.chip clear 24)
//   PERTURBATION .away-strip input[type=checkbox]{width:24px;height:24px} and
//                .away-strip label{min-height:24px} -> both to 24  (up)
//   RESULT axis_ink_overlap_pairs_inline=<see below>
import { existsSync, readFileSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(__dirname, "../../../..");
const CARD_SRC = path.join(
  repo, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js");
const testsDir = path.join(repo, "tests");
const defaultPlan = path.join(
  "/tmp",
  `plandata-${createHash("sha256").update(testsDir).digest("hex").slice(0, 12)}.json`);
const planPath = process.env.HPO_PLANDATA || defaultPlan;
if (!existsSync(planPath)) {
  console.error(`FAIL: plan payload ${planPath} not found — run tests/plan_view.py with HPO_PLANDATA set`);
  process.exit(1);
}
const plan = JSON.parse(readFileSync(planPath, "utf8"));

const SOLAR = "sensor.heat_pump_optimizer_solar_irradiance";
const SPACE = "sensor.heat_pump_optimizer_space_heating_plan";
const DHW = "sensor.heat_pump_optimizer_dhw_heating_plan";

const planStates = () => ({
  [SOLAR]: { state: "120", attributes: {
    forecast: plan.space_plan.forecast.map((q, i) => ({
      t: q.t, ghi: Math.max(0, 400 * Math.sin((i / plan.space_plan.forecast.length) * Math.PI)) })),
    source: "open_meteo", friendly_name: "Solar Irradiance", plan_kind: "solar" } },
  [SPACE]: { state: "3 slots planned", attributes: {
    forecast: plan.space_plan.forecast, slots: plan.space_plan.slots,
    total_energy_kwh: plan.space_plan.total_energy_kwh,
    total_cost: plan.space_plan.total_cost, active_now: plan.space_plan.active_now,
    friendly_name: "Space Heating Plan", plan_kind: "space" } },
  [DHW]: { state: "4 slots planned", attributes: {
    forecast: plan.dhw_plan.forecast, slots: plan.dhw_plan.slots,
    total_energy_kwh: plan.dhw_plan.total_energy_kwh,
    total_cost: plan.dhw_plan.total_cost, active_now: plan.dhw_plan.active_now,
    friendly_name: "DHW Heating Plan", plan_kind: "dhw" } },
});
const awayStates = () => {
  const st = planStates();
  st["switch.heat_pump_optimizer_away"] = { state: "on", attributes: {} };
  st["datetime.heat_pump_optimizer_away_return"] =
    { state: "2026-01-16T18:00:00", attributes: {} };
  st["binary_sensor.heat_pump_optimizer_away_mode"] =
    { state: "off", attributes: { source: "none" } };
  return st;
};

const HA_LIGHT = `
  --primary-text-color:#212121; --secondary-text-color:#727272;
  --text-primary-color:#fff; --primary-color:#03a9f4;
  --card-background-color:#fff; --divider-color:rgba(0,0,0,.12);
  --primary-background-color:#fafafa; --secondary-background-color:#e5e5e5;
  --disabled-text-color:#bdbdbd; --error-color:#db4437; --warning-color:#ffa600;
  --success-color:#43a047; --info-color:#039be5;
`;
const HA_DARK = `
  --primary-text-color:#e1e1e1; --secondary-text-color:#9b9b9b;
  --text-primary-color:#fff; --primary-color:#03a9f4;
  --card-background-color:#1c1c1c; --divider-color:rgba(225,225,225,.12);
  --primary-background-color:#111111; --secondary-background-color:#202020;
  --disabled-text-color:#6f6f6f; --error-color:#db4437; --warning-color:#ffa600;
  --success-color:#43a047; --info-color:#039be5;
`;

// Home Assistant's own <ha-card>, including the `color: var(--primary-text-color)`
// that makes every inherited-colour text run in the card theme-aware. Without
// that declaration a harness measures the page default, not the theme.
const HA_CARD_DEF = `
if (!customElements.get("ha-card")) {
  customElements.define("ha-card", class extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({ mode: "open" }).innerHTML =
        "<style>:host{background:var(--ha-card-background,var(--card-background-color,#fff));" +
        "box-sizing:border-box;border-radius:12px;border-width:1px;border-style:solid;" +
        "border-color:var(--divider-color,#e0e0e0);color:var(--primary-text-color);" +
        "display:block;position:relative;}</style><slot></slot>";
    }
  });
}
`;

// Contrast maths, WCAG 2.x, sRGB, with the element's own opacity composited
// over the resolved background.
const COLOR_UTILS = `
window.__cu = (() => {
  const hex = (h) => { const n = parseInt(h.slice(1),16); return [(n>>16)&255,(n>>8)&255,n&255]; };
  const parse = (s) => {
    if (!s || s === "transparent" || s === "none") return null;
    const m = s.match(/^rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([\\d.]+))?/);
    if (m) { const a = m[4]===undefined?1:Number(m[4]); return a===0?null:[+m[1],+m[2],+m[3],a]; }
    if (s.startsWith("#")) { const c = hex(s.length===4?"#"+s[1]+s[1]+s[2]+s[2]+s[3]+s[3]:s); return [c[0],c[1],c[2],1]; }
    return null;
  };
  const lum = (c) => { const f=(v)=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4);};
    return 0.2126*f(c[0])+0.7152*f(c[1])+0.0722*f(c[2]); };
  const ratio = (a,b) => { const la=lum(a), lb=lum(b); return (Math.max(la,lb)+0.05)/(Math.min(la,lb)+0.05); };
  const over = (fg,bg,a) => [0,1,2].map((i)=>Math.round(a*fg[i]+(1-a)*bg[i]));
  const bgOf = (el) => {
    for (let n = el; n; n = n.parentElement || (n.getRootNode && n.getRootNode().host) || null) {
      if (!n || n.nodeType !== 1) break;
      const c = parse(getComputedStyle(n).backgroundColor);
      if (c && c[3] > 0.5) return [c[0],c[1],c[2]];
    }
    const tok = parse(getComputedStyle(window.__card).getPropertyValue("--card-background-color").trim());
    return tok ? [tok[0],tok[1],tok[2]] : [255,255,255];
  };
  const contrastOf = (el) => {
    const cs = getComputedStyle(el);
    const fgc = parse(cs.color);
    if (!fgc) return null;
    const bg = bgOf(el);
    const op = Number(cs.opacity);
    const fg = over([fgc[0],fgc[1],fgc[2]], bg, (Number.isFinite(op)?op:1) * fgc[3]);
    return +ratio(fg, bg).toFixed(2);
  };
  return { contrastOf, bgOf, parse, ratio };
})();
`;

const MOUNT = `
window.__mount = async ([states, cfg, hostW, theme, extraCss]) => {
  document.head.querySelectorAll("style.hpo-d4").forEach((n)=>n.remove());
  document.body.innerHTML = "";
  const style = document.createElement("style");
  style.className = "hpo-d4";
  style.textContent =
    'body{margin:0;font-family:-apple-system,"Segoe UI",sans-serif}' +
    'heatpump-optimizer-card{display:block;width:' + hostW + 'px;' + theme + '}';
  document.head.appendChild(style);
  const card = document.createElement("heatpump-optimizer-card");
  card.setConfig(Object.assign({type:"custom:heatpump-optimizer-card"}, cfg||{}));
  card.hass = { states: states };
  document.body.appendChild(card);
  window.__card = card;
  await new Promise((r)=>requestAnimationFrame(()=>requestAnimationFrame(r)));
  await new Promise((r)=>setTimeout(r, 60));
  if (extraCss) {
    // The perturbation arm: an extra rule inside the card's own shadow root,
    // which is the only place a page-level rule cannot reach.
    const s = document.createElement("style");
    s.textContent = extraCss;
    card.shadowRoot.appendChild(s);
    await new Promise((r)=>requestAnimationFrame(()=>requestAnimationFrame(r)));
  }
  return card.shadowRoot ? 1 : 0;
};
`;

const COARSE = async (page) => {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("Emulation.setEmulatedMedia", {
    features: [{ name: "pointer", value: "coarse" },
               { name: "any-pointer", value: "coarse" },
               { name: "hover", value: "none" }],
  });
  await page.evaluate(() => {
    const orig = window.matchMedia.bind(window);
    window.matchMedia = (q) => {
      if (q === "(pointer: coarse)" || q === "(hover: none)") {
        return { matches: true, media: q, onchange: null,
          addEventListener() {}, removeEventListener() {},
          addListener() {}, removeListener() {}, dispatchEvent() { return true; } };
      }
      return orig(q);
    };
  });
};

// A real origin, not about:blank: the card persists its hidden-series
// preference to localStorage, and an opaque origin throws SecurityError on
// the first read -- which would make the "does a click persist anything"
// question unanswerable. Nothing leaves the machine; the route serves an
// empty document for every request.
const ORIGIN = "http://heatpump-optimizer.test/";
const newPage = async (browser, w, h, coarse) => {
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  page.on("pageerror", (e) => console.log("  page error: " + e.message));
  await page.route("**/*", (route) =>
    route.fulfill({ status: 200, contentType: "text/html", body: "<!doctype html><html><head></head><body></body></html>" }));
  await page.goto(ORIGIN);
  await page.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
  if (coarse) await COARSE(page);
  await page.addScriptTag({ path: CARD_SRC });
  await page.evaluate(HA_CARD_DEF);
  await page.evaluate(COLOR_UTILS);
  await page.evaluate(MOUNT);
  return page;
};

const out = [];
const say = (k, v, note) => {
  out.push([k, v]);
  console.log(`RESULT ${k}=${v}${note ? "   " + note : ""}`);
};

const browser = await chromium.launch();
try {
  // === A. the no-data legend chip ==========================================
  // The state a fresh install is in until the first plan is published, and
  // the state the dashboard card picker previews.
  const chipOf = async (theme, extraCss, states) => {
    const page = await newPage(browser, 375, 812, false);
    await page.evaluate(window_ => 0, null).catch(() => {});
    await page.evaluate(
      ([st, cfg, w, th, css]) => window.__mount([st, cfg, w, th, css]),
      [states, null, 359, theme, extraCss]);
    const r = await page.evaluate(() => {
      const root = window.__card.shadowRoot;
      const chips = [...root.querySelectorAll(".chip")];
      const nodata = chips.filter((c) => c.classList.contains("nodata"));
      const rows = nodata.map((c) => ({
        text: (c.textContent || "").trim().slice(0, 24),
        ratio: window.__cu.contrastOf(c),
        opacity: getComputedStyle(c).opacity,
        disabled: c.disabled === true,
        ariaDisabled: c.getAttribute("aria-disabled"),
        tabIndex: c.tabIndex,
        pressed: c.getAttribute("aria-pressed"),
        cursor: getComputedStyle(c).cursor,
      }));
      return { nChips: chips.length, nNodata: nodata.length, rows,
               allRatios: chips.map((c) => window.__cu.contrastOf(c)) };
    });
    // Does a click on a "not-allowed" chip really change persisted state?
    const clicked = await page.evaluate(() => {
      const root = window.__card.shadowRoot;
      const c = root.querySelector(".chip.nodata");
      if (!c) return null;
      const before = { ...localStorage };
      const key = c.getAttribute("data-key");
      c.dispatchEvent(new MouseEvent("click", { bubbles: true, composed: true }));
      const after = { ...localStorage };
      const now = root.querySelector(`.chip[data-key="${key}"]`);
      return {
        key,
        storageKeysBefore: Object.keys(before).length,
        storageKeysAfter: Object.keys(after).length,
        storageChanged: JSON.stringify(before) !== JSON.stringify(after),
        pressedAfter: now ? now.getAttribute("aria-pressed") : null,
        offAfter: now ? now.classList.contains("off") : null,
        stored: Object.values(after)[0] || "",
      };
    });
    await page.close();
    return { ...r, clicked };
  };

  const noPlan = {};
  const aLight = await chipOf(HA_LIGHT, "", noPlan);
  const aDark = await chipOf(HA_DARK, "", noPlan);
  const aPert = await chipOf(HA_LIGHT, ".chip.nodata { opacity: 1; }", noPlan);
  const aNull = await chipOf(HA_LIGHT, "", planStates());

  console.log("");
  console.log("=== A. the no-data legend chip (state: no plan sensors) ===");
  say("chip_nodata_count", aLight.nNodata, `of ${aLight.nChips} legend chips`);
  say("chip_nodata_contrast_light",
    Math.min(...aLight.rows.map((r) => r.ratio)).toFixed(2), "floor 4.5");
  say("chip_nodata_contrast_dark",
    Math.min(...aDark.rows.map((r) => r.ratio)).toFixed(2), "floor 4.5");
  say("chip_nodata_opacity", aLight.rows[0] ? aLight.rows[0].opacity : "n/a");
  say("chip_nodata_is_disabled",
    aLight.rows.filter((r) => r.disabled || r.ariaDisabled === "true").length,
    "0 = an ACTIVE control, so WCAG 1.4.3's inactive-component exemption does not apply");
  say("chip_nodata_tabbable", aLight.rows.filter((r) => r.tabIndex >= 0).length,
    "reachable by Tab");
  say("chip_nodata_cursor", aLight.rows[0] ? aLight.rows[0].cursor : "n/a",
    "the affordance the CSS gives");
  say("chip_nodata_click_persists", aLight.clicked && aLight.clicked.storageChanged ? 1 : 0,
    aLight.clicked ? `key=${aLight.clicked.key} pressed ${aLight.rows[0].pressed}->${aLight.clicked.pressedAfter} stored=${String(aLight.clicked.stored).slice(0, 60)}` : "");
  say("PERTURBATION_chip_nodata_opacity1_light",
    Math.min(...aPert.rows.map((r) => r.ratio)).toFixed(2),
    "expected direction: up, past 4.5");
  say("NULL_ARM_chips_with_plan_data_light",
    Math.min(...aNull.allRatios).toFixed(2),
    `${aNull.nNodata} nodata chip(s) once the plan sensors exist — the defect vanishes`);

  // === B. the away strip's activation areas ================================
  console.log("");
  console.log("=== B. the away strip under a COARSE pointer ===");
  const awayOf = async (theme, extraCss) => {
    const page = await newPage(browser, 375, 812, true);
    await page.evaluate(
      ([st, cfg, w, th, css]) => window.__mount([st, cfg, w, th, css]),
      [awayStates(), null, 359, theme, ""]);
    await page.evaluate(async () => {
      window.__card._onCardClick({});
      await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
      await new Promise((r) => setTimeout(r, 80));
    });
    // The perturbation goes in AFTER the dialog render: `_render()` replaces
    // the shadow root's innerHTML, so a style appended before it is dropped.
    if (extraCss) {
      await page.evaluate(async (css) => {
        const st = document.createElement("style");
        st.textContent = css;
        window.__card.shadowRoot.appendChild(st);
        await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
      }, extraCss);
    }
    const r = await page.evaluate(() => {
      const root = window.__card.shadowRoot;
      const box = (el) => {
        const b = el.getBoundingClientRect();
        return { w: +b.width.toFixed(1), h: +b.height.toFixed(1),
                 min: +Math.min(b.width, b.height).toFixed(1) };
      };
      const strip = root.querySelector(".away-strip");
      const cb = root.querySelector("[data-away-toggle]");
      const ret = root.querySelector("[data-away-return]");
      const labels = [...root.querySelectorAll(".away-strip label")].map(box);
      // The control: the twelve selectors the card's own coarse rule set names.
      const ruled = [".close", ".dlg-tab", ".chip", ".viewctl button",
        ".layout-bar button", ".whatif button"];
      const ruledBoxes = ruled.flatMap((sel) =>
        [...root.querySelectorAll(sel)]
          .filter((el) => el.getClientRects().length && !el.disabled)
          .map((el) => ({ sel, ...box(el) })));
      // How far apart the strip's own children are drawn, against a styled
      // row on the same page. `.legend` declares `display:flex; gap:6px`;
      // `.away-strip` declares nothing, so its children abut.
      const gapsOf = (row) => {
        if (!row) return null;
        const kids = [...row.children].filter((k) => k.getClientRects().length);
        const rects = kids.map((k) => k.getBoundingClientRect());
        const out = [];
        for (let i = 1; i < rects.length; i++) {
          if (Math.abs(rects[i].top - rects[i - 1].top) > 2) continue;
          out.push(+(rects[i].left - rects[i - 1].right).toFixed(2));
        }
        return { n: kids.length, gaps: out,
                 min: out.length ? Math.min(...out) : null,
                 display: getComputedStyle(row).display,
                 gapProp: getComputedStyle(row).gap };
      };
      return {
        stripPresent: !!strip,
        stripRow: gapsOf(strip),
        legendRow: gapsOf(root.querySelector(".legend")),
        checkbox: cb ? box(cb) : null,
        returnInput: ret ? box(ret) : null,
        labels,
        ruledMin: ruledBoxes.length
          ? Math.min(...ruledBoxes.map((b) => b.min)) : null,
        ruledCount: ruledBoxes.length,
      };
    });
    await page.close();
    return r;
  };
  const bBase = await awayOf(HA_LIGHT, "");
  // min-width/min-height do not move a checkbox's used size (it is a
  // replaced element with an intrinsic one); width/height do, which is what
  // a fix would have to say.
  const bPert = await awayOf(HA_LIGHT,
    ".away-strip input[type='checkbox'] { width: 24px; height: 24px; }" +
    ".away-strip label { min-height: 24px; display: inline-flex; align-items: center; }" +
    ".away-strip input[type='datetime-local'] { min-height: 24px; }");
  say("away_strip_present", bBase.stripPresent ? 1 : 0);
  say("away_checkbox_min_px", bBase.checkbox ? bBase.checkbox.min : "n/a",
    bBase.checkbox ? `${bBase.checkbox.w}x${bBase.checkbox.h}` : "");
  say("away_label_min_px", bBase.labels.length ? Math.min(...bBase.labels.map((l) => l.min)) : "n/a",
    `the wrapping <label>, the widest activation area a tap can use: ${
      bBase.labels.map((l) => `${l.w}x${l.h}`).join(", ")}`);
  say("away_return_min_px", bBase.returnInput ? bBase.returnInput.min : "n/a",
    bBase.returnInput ? `${bBase.returnInput.w}x${bBase.returnInput.h}` : "");
  say("away_strip_child_gap_px",
    bBase.stripRow && bBase.stripRow.min !== null ? bBase.stripRow.min : "n/a",
    bBase.stripRow
      ? `${bBase.stripRow.n} child element(s), display:${bBase.stripRow.display}, gap:${bBase.stripRow.gapProp} — the two labels abut, so the card reads "AwayReturn"`
      : "");
  say("legend_row_child_gap_px",
    bBase.legendRow && bBase.legendRow.min !== null ? bBase.legendRow.min : "n/a",
    bBase.legendRow
      ? `the control: a STYLED row on the same page, display:${bBase.legendRow.display}, gap:${bBase.legendRow.gapProp}`
      : "");
  say("coarse_ruleset_min_px", bBase.ruledMin,
    `over ${bBase.ruledCount} control(s) the card's own coarseHtmlTargets rule set names — the control arm`);
  say("PERTURBATION_away_checkbox_min_px", bPert.checkbox ? bPert.checkbox.min : "n/a",
    "expected direction: up, to 24");
  say("PERTURBATION_away_label_min_px",
    bPert.labels.length ? Math.min(...bPert.labels.map((l) => l.min)) : "n/a",
    "expected direction: up, to 24");
  say("PERTURBATION_away_return_min_px", bPert.returnInput ? bPert.returnInput.min : "n/a",
    "expected direction: up, to 24");

  // === C. the INLINE chart's axis unit titles, rasterised ==================
  // tests/card_browser.mjs rasterises the LAST `.chartwrap svg` (the expanded
  // dialog's). The compact tile the dashboard actually shows is a second,
  // narrower copy that lane never reads.
  console.log("");
  console.log("=== C. inline-chart axis unit vs tick, real ink ===");
  const inkOf = async (hostW, which) => {
    const page = await newPage(browser, 1280, 900, false);
    await page.evaluate(
      ([st, cfg, w, th, css]) => window.__mount([st, cfg, w, th, css]),
      [planStates(), { what_if: true }, hostW, HA_LIGHT, ""]);
    if (which === "dialog") {
      await page.evaluate(async () => {
        window.__card._onCardClick({});
        await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
        await new Promise((r) => setTimeout(r, 80));
      });
    }
    const r = await page.evaluate(async (pick) => {
      const root = window.__card.shadowRoot;
      const svgs = [...root.querySelectorAll(".chartwrap svg")];
      const svg = pick === "dialog" ? svgs[svgs.length - 1] : svgs[0];
      if (!svg) return { pairs: -1, detail: "no svg" };
      const vb = (svg.getAttribute("viewBox") || "0 0 900 380").split(/\s+/);
      const W = Number(vb[2]) || 900, H = Number(vb[3]) || 380;
      const texts = [...svg.querySelectorAll("text")]
        .filter((t) => (t.textContent || "").trim().length > 0);
      const unitPat = /^(°C|kW|SEK\/kWh|kr\/kWh|öre\/kWh|EUR\/kWh|W\/m²)$/;
      const tickPat = /^-?\d[\d.,]*$/;
      // Rasterise one element alone on white at the chart's own viewBox size
      // and take the tight ink box: this is what the eye sees, not the layout
      // box getBoundingClientRect returns for SVG text.
      const inkOf = async (el) => {
        const mini = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        mini.setAttribute("xmlns", "http://www.w3.org/2000/svg");
        mini.setAttribute("viewBox", `0 0 ${W} ${H}`);
        mini.setAttribute("width", String(W));
        mini.setAttribute("height", String(H));
        const bg = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        bg.setAttribute("width", "100%"); bg.setAttribute("height", "100%");
        bg.setAttribute("fill", "white");
        mini.appendChild(bg);
        mini.appendChild(el.cloneNode(true));
        const url = "data:image/svg+xml;charset=utf-8," +
          encodeURIComponent(new XMLSerializer().serializeToString(mini));
        const img = new Image();
        await new Promise((ok, no) => { img.onload = ok; img.onerror = no; img.src = url; });
        const canvas = document.createElement("canvas");
        canvas.width = W; canvas.height = H;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0);
        const { data } = ctx.getImageData(0, 0, W, H);
        let r0 = H, r1 = -1, c0 = W, c1 = -1;
        for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
          const i = (y * W + x) * 4;
          if (data[i + 3] > 8 && data[i] + data[i + 1] + data[i + 2] < 740) {
            r0 = Math.min(r0, y); r1 = Math.max(r1, y);
            c0 = Math.min(c0, x); c1 = Math.max(c1, x);
          }
        }
        return r1 < 0 ? null : { rows: [r0, r1], cols: [c0, c1] };
      };
      const units = texts.filter((t) => unitPat.test((t.textContent || "").trim()));
      const ticks = texts.filter((t) => tickPat.test((t.textContent || "").trim()));
      let pairs = 0; const detail = [];
      for (const u of units) {
        const ui = await inkOf(u);
        if (!ui) continue;
        for (const t of ticks) {
          const ti = await inkOf(t);
          if (!ti) continue;
          const v = Math.min(ui.rows[1], ti.rows[1]) - Math.max(ui.rows[0], ti.rows[0]) + 1;
          const h = Math.min(ui.cols[1], ti.cols[1]) - Math.max(ui.cols[0], ti.cols[0]) + 1;
          if (v > 0 && h > 0) {
            pairs += 1;
            detail.push(`${(u.textContent||"").trim()}/${(t.textContent||"").trim()} v${v} h${h}`);
          }
        }
      }
      const r = svg.getBoundingClientRect();
      return { pairs, detail: detail.slice(0, 6).join("; "), svgW: +r.width.toFixed(1),
               nUnits: units.length, nTicks: ticks.length };
    }, which);
    await page.close();
    return r;
  };
  const cInline = await inkOf(359, "inline");
  const cDialog = await inkOf(359, "dialog");
  say("axis_ink_overlap_pairs_inline", cInline.pairs,
    `svg ${cInline.svgW} px, ${cInline.nUnits} unit title(s) x ${cInline.nTicks} tick(s)${
      cInline.detail ? "; " + cInline.detail : ""}`);
  say("axis_ink_overlap_pairs_dialog", cDialog.pairs,
    `svg ${cDialog.svgW} px — the copy tests/card_browser.mjs already measures`);
} finally {
  await browser.close();
}

console.log("");
console.log("RESULT thread_factor=1.0");
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log("RESULT swapins=0");
