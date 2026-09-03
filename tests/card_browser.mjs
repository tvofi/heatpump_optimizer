// The real-browser layout lane (issue #96).
//
// card.mjs proves the card builds the right DOM against a hand-written
// stub whose getBoundingClientRect is a constant 900x400 -- so it cannot
// see anything about position, size or visibility. Three layout defects
// reached a user that way: the zoom-limited editing trap (v4.0.5),
// tooltip text overflowing its box (two causes: inherited nowrap plus a
// left-edge-only clamp), and legend chips 0.33px apart that read as one
// chip hiding three traces.
//
// This lane runs the real card in real Chromium and asserts geometry:
// boxes at coordinates, overlaps, contained edges, scroll vs client
// width. It consumes the same plan payload card.mjs does (run
// tests/plan_view.py first; this file resolves the same default).
//
// Own CI job, not a run.sh lane: it needs a browser the other lanes do
// not install, and it is excluded from the closures roster in
// tests/closure.py's NOT_A_TEST for exactly that reason -- the closures
// job would have to install Chromium to record it, which buys nothing:
// its dependency closure is the card source, the payload and itself.
import { strict as assert } from "node:assert";
import { createHash } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

// createRequire, not a static import: the lane must resolve playwright
// from wherever the CI job or developer put it (a bare `import` would
// demand node_modules inside the repository, which this repo does not
// have and should not grow for one lane).
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repo = path.join(__dirname, "..");

// Same plan-payload resolution as tests/card.mjs: argv, HPO_PLANDATA,
// then the per-checkout default plan_view.py writes.
const testsDir = __dirname;
const defaultPath = path.join(
  "/tmp",
  `plandata-${createHash("sha256").update(testsDir).digest("hex").slice(0, 12)}.json`
);
let planPath = process.argv[2] || process.env.HPO_PLANDATA || defaultPath;
if (!existsSync(planPath)) {
  console.error(`FAIL: plan payload ${planPath} not found — run tests/plan_view.py first`);
  process.exit(1);
}
const plan = JSON.parse(readFileSync(planPath, "utf8"));

const CARD_SRC = path.join(repo, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js");
const SOLAR_ID = "sensor.heat_pump_optimizer_solar_irradiance";
const SPACE_ID = "sensor.heat_pump_optimizer_space_heating_plan";
const DHW_ID = "sensor.heat_pump_optimizer_dhw_heating_plan";

let fails = 0;
function check(name, cond, detail = "") {
  console.log((cond ? "  ok  " : "  FAIL") + "  " + name);
  if (!cond) { if (detail) console.log("        " + detail); fails += 1; }
}

const solarForecast = plan.space_plan.forecast.map((p, i) => ({
  t: p.t,
  ghi: Math.max(0, 400 * Math.sin((i / plan.space_plan.forecast.length) * Math.PI)),
}));

// The setup page's diagram payload: what `describe_setup` publishes for a
// two-zone, two-tank house with a throttling valve and a wood furnace --
// the same shape tests/card.mjs builds, so the editor hits are the ones a
// fully-configured install offers.
const TEMP_DOMAINS = ["sensor", "number", "input_number"];
const setupTopology = {
  two_zone: true, dhw: true, valve_mode: "manual",
  buffer: { volume_l: 750, is_store: true, max_temp: 70 },
  wood: { present: true, volume_l: 500 },
  edges: [
    ["heat_pump", "buffer_tank"],
    ["buffer_tank", "mixing_valve"],
    ["mixing_valve", "upper_zone"],
    ["mixing_valve", "lower_zone"],
    ["wood_tank", "buffer_tank"],
    ["heat_pump", "dhw_tank"],
  ],
  slots: [
    { key: "indoor_temp_entity", label: "Indoor temperature",
      place: "upper_zone", entity: "sensor.livingroom", domains: TEMP_DOMAINS },
    { key: "lower_floor_temp_entity", label: "Lower floor temperature",
      place: "lower_zone", entity: null, domains: TEMP_DOMAINS },
    { key: "buffer_tank_temp_entity", label: "Buffer tank temperature",
      place: "buffer_tank", entity: "sensor.tank", domains: TEMP_DOMAINS },
    { key: "wood_tank_top_entity", label: "Wood tank top",
      place: "wood_tank", entity: null, domains: TEMP_DOMAINS },
    { key: "outdoor_temp_entity", label: "Outdoor temperature",
      place: "outdoor", entity: "sensor.outside", domains: TEMP_DOMAINS },
    { key: "heat_pump_switch_entity", label: "Heat pump switch",
      place: "heat_pump", entity: null,
      domains: ["switch", "input_boolean", "climate"] },
  ],
};
const states = {
  [SOLAR_ID]: { state: "120", attributes: {
    forecast: solarForecast, source: "open_meteo", friendly_name: "Solar Irradiance",
    plan_kind: "solar" } },
  [SPACE_ID]: { state: "3 slots planned", attributes: {
    forecast: plan.space_plan.forecast, slots: plan.space_plan.slots,
    total_energy_kwh: plan.space_plan.total_energy_kwh,
    total_cost: plan.space_plan.total_cost,
    active_now: plan.space_plan.active_now,
    friendly_name: "Space Heating Plan", plan_kind: "space",
    setup_topology: setupTopology } },
  [DHW_ID]: { state: "4 slots planned", attributes: {
    forecast: plan.dhw_plan.forecast, slots: plan.dhw_plan.slots,
    total_energy_kwh: plan.dhw_plan.total_energy_kwh,
    total_cost: plan.dhw_plan.total_cost,
    active_now: plan.dhw_plan.active_now,
    friendly_name: "DHW Heating Plan", plan_kind: "dhw" } },
  "sensor.livingroom": { state: "21.3", attributes: { unit_of_measurement: "°C" } },
  "sensor.tank": { state: "47.5", attributes: { unit_of_measurement: "°C" } },
  "sensor.outside": { state: "unavailable", attributes: {} },
};

const browser = await chromium.launch();
try {
  const page = await browser.newPage({ viewport: { width: 1024, height: 800 } });
  page.on("pageerror", (err) => {
    console.log(`  page error: ${err.message}`);
  });
  await page.goto("about:blank");
  await page.addScriptTag({ path: CARD_SRC });

  // The card, on a dashboard-sized tile: the host gets the panel width
  // Home Assistant would give it and a sane font, so every measurement
  // below is of the card as a user sees it, not of a collapsed div.
  await page.evaluate(([st]) => {
    const style = document.createElement("style");
    style.textContent = `
      body { margin: 0; font-family: -apple-system, "Segoe UI", sans-serif; }
      heatpump-optimizer-card { display: block; width: 900px; min-height: 400px; }
    `;
    document.head.appendChild(style);
    const card = document.createElement("heatpump-optimizer-card");
    document.body.appendChild(card);
    card.setConfig({ type: "custom:heatpump-optimizer-card" });
    card.hass = { states: st };
    window.__card = card;
  }, [states]);
  await page.waitForTimeout(200);

  // --- 1. The card really rendered, with real geometry --------------------
  // The largest svg in the shadow root, not the first: the card also
  // draws small inline icons as svg, and an 18x18 icon would make every
  // measurement below nonsense.
  const cardBox = await page.evaluate(() => {
    const card = window.__card;
    const svgs = card.shadowRoot ? [...card.shadowRoot.querySelectorAll("svg")] : [];
    let best = null;
    for (const svg of svgs) {
      const b = svg.getBoundingClientRect();
      if (!best || b.width * b.height > best.w * best.h) {
        best = { w: b.width, h: b.height, left: b.left, top: b.top };
      }
    }
    return best ? { ...best, cardW: card.getBoundingClientRect().width } : null;
  });
  check("the card renders an svg with real size on a dashboard tile",
    cardBox !== null && cardBox.w > 600 && cardBox.h > 200,
    cardBox ? `${cardBox.w.toFixed(0)}x${cardBox.h.toFixed(0)} px` : "no svg");

  // --- 2. Legend chips: distinct, not stacked into one --------------------
  // The shipped defect: three chips 0.33px apart on a 65k axis read as
  // one chip and hid three traces at once. Chips must be pairwise
  // separated by a visible gap, and every chip label must fit its box.
  const chips = await page.evaluate(() => {
    const root = window.__card.shadowRoot;
    return [...root.querySelectorAll(".legend-chip, .chip")].map((el) => {
      const b = el.getBoundingClientRect();
      return { x: b.x, y: b.y, w: b.width, h: b.height,
               text: (el.textContent || "").trim(),
               overflow: el.scrollWidth > el.clientWidth + 1 };
    });
  });
  check("legend chips exist for the rendered traces", chips.length >= 2,
    `${chips.length} chip(s): ${chips.map((c) => c.text).join(" | ")}`);
  let overlapPairs = [];
  for (let i = 0; i < chips.length; i++) {
    for (let j = i + 1; j < chips.length; j++) {
      const a = chips[i], b = chips[j];
      const gapX = Math.max(a.x - (b.x + b.w), b.x - (a.x + a.w));
      const gapY = Math.max(a.y - (b.y + b.h), b.y - (a.y + a.h));
      if (gapX < 2 && gapY < 2) overlapPairs.push(`${a.text}~${b.text} (${gapX.toFixed(2)}px apart)`);
    }
  }
  check("no two legend chips overlap or nearly touch", overlapPairs.length === 0,
    overlapPairs.slice(0, 4).join("; "));
  check("every legend chip's label fits inside it",
    chips.every((c) => !c.overflow && c.w > 4 && c.h > 8),
    chips.filter((c) => c.overflow).map((c) => c.text).join("; "));

  // --- 3. The tooltip: contained on BOTH edges, text inside its box ------
  // Hover across the whole chart width -- including the far left and far
  // right, where the two shipped causes lived: a clamp on the left edge
  // only, and inherited white-space:nowrap that made max-width inert
  // (scrollWidth > clientWidth). The exercised count guards against the
  // vacuous pass: a lane where no tooltip ever appeared must not report
  // "stays inside" about nothing.
  if (cardBox) {
    const contained = [];
    const overflows = [];
    let measured = 0;
    for (let frac of [0.02, 0.25, 0.5, 0.75, 0.98]) {
      const x = cardBox.left + cardBox.w * frac;
      const y = cardBox.top + cardBox.h * 0.35;
      await page.mouse.move(x, y);
      await page.waitForTimeout(120);
      const m = await page.evaluate(() => {
        const root = window.__card.shadowRoot;
        const tt = root && root.querySelector(".tooltip");
        if (!tt || !tt.textContent.trim()) return null;
        const card = window.__card.getBoundingClientRect();
        const b = tt.getBoundingClientRect();
        return {
          left: b.left - card.left, right: card.right - b.right,
          top: b.top - card.top, bottom: card.bottom - b.bottom,
          textFits: tt.scrollWidth <= tt.clientWidth + 1,
          w: b.width, h: b.height,
        };
      });
      if (!m) continue;
      measured += 1;
      if (m.left < -0.5 || m.right < -0.5 || m.top < -0.5 || m.bottom < -0.5) {
        contained.push(`x=${frac}: edges L${m.left.toFixed(0)} R${m.right.toFixed(0)}`);
      }
      if (!m.textFits) overflows.push(`x=${frac}`);
    }
    check("hovering the chart actually shows tooltips (the lane is not vacuous)",
      measured >= 2, `${measured}/5 hover positions produced a tooltip`);
    check("the tooltip stays inside the card on both edges, everywhere hovered",
      measured >= 2 && contained.length === 0, contained.join("; "));
    check("and its text fits its box (no inherited-nowrap overflow)",
      measured >= 2 && overflows.length === 0, overflows.join("; "));
  }

  // --- 4. The setup editor: hit targets a pointer can actually hit -------
  // The zoom-limited editing trap (v4.0.5): at real rendered sizes the
  // draggable hit rects must be big enough to click, and inside the svg
  // they belong to.
  const setup = await page.evaluate(() => {
    const card = window.__card;
    // Open the dialog first, exactly as card.mjs does: the setup page
    // renders inside it, and setting _dialogPage alone leaves the dialog
    // closed and the svg absent.
    card._onCardClick({});
    card.dialog.page = "setup";
    card._render();
    const svg = card.shadowRoot && card.shadowRoot.querySelector("svg.setup-svg");
    if (!svg) return null;
    const sb = svg.getBoundingClientRect();
    const hits = [...svg.querySelectorAll("rect.setup-hit")].map((r) => {
      const b = r.getBoundingClientRect();
      return { w: b.width, h: b.height,
               inside: b.left >= sb.left - 0.5 && b.right <= sb.right + 0.5
                     && b.top >= sb.top - 0.5 && b.bottom <= sb.bottom + 0.5,
               key: r.getAttribute("data-key") || "" };
    });
    return { hits, svgW: sb.width, svgH: sb.height };
  });
  check("the setup page renders its svg", setup !== null && setup.svgW > 300,
    setup ? `${setup.svgW.toFixed(0)}x${setup.svgH.toFixed(0)} px` : "no setup svg");
  if (setup) {
    const tiny = setup.hits.filter((h) => h.w < 8 || h.h < 8);
    const outside = setup.hits.filter((h) => !h.inside);
    check("every setup hit target is at least 8x8 px at real size",
      setup.hits.length > 0 && tiny.length === 0,
      `${setup.hits.length} hit(s); tiny: ${tiny.map((h) => `${h.key}:${h.w.toFixed(1)}x${h.h.toFixed(1)}`).join(", ")}`);
    check("and every hit target sits inside the setup svg",
      outside.length === 0,
      outside.map((h) => h.key).join(", "));
  }

  // --- D4-01: the compact chart's text at phone width ----------------------
  // The shipped defect, measured by the audit on a 287 px tile: axis text
  // at 3.19 px glyph height -- outlines gone. The card now floors the
  // rendered font (the viewBox-unit font grows as the tile narrows), and
  // the only honest place to prove it is a real layout engine: shrink the
  // host, re-render, and measure ON-SCREEN sizes. getComputedStyle is
  // useless here -- it reports the font-size attribute in user units,
  // with no viewBox scaling -- so the screen size is reconstructed from
  // the svg's own rect, the one transform that actually applies.
  const phoneFont = await page.evaluate(async () => {
    const card = window.__card;
    card.style.width = "287px";
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    card._render();
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    const root = card.shadowRoot;
    if (!root) return null;
    const chart = root.querySelector(".chartwrap svg");
    if (!chart) return null;
    const svgRect = chart.getBoundingClientRect();
    const scale = svgRect.width / 900;
    const labels = [...chart.querySelectorAll("text")]
      .filter((t) => (t.getAttribute("font-size") || "").length > 0);
    if (!labels.length) return null;
    const sizes = labels.map((t) => {
      const attr = Number(t.getAttribute("font-size"));
      const bbox = t.getBBox ? t.getBBox() : { height: 0 };
      return {
        screenFontPx: attr * scale,
        glyphScreenPx: bbox.height * scale,
        text: (t.textContent || "").trim().slice(0, 12),
      };
    });
    return {
      hostW: card.getBoundingClientRect().width,
      maxScreenFont: Math.max(...sizes.map((s) => s.screenFontPx)),
      maxGlyph: Math.max(...sizes.map((s) => s.glyphScreenPx)),
      n: sizes.length,
    };
  });
  check("a phone-width tile renders axis text at or above the 8 px floor",
    phoneFont !== null && phoneFont.maxScreenFont >= 8 - 0.05,
    phoneFont
      ? `host ${phoneFont.hostW.toFixed(0)} px, ${phoneFont.n} labels, ` +
        `largest on-screen font ${phoneFont.maxScreenFont.toFixed(2)} px, ` +
        `largest glyph box ${phoneFont.maxGlyph.toFixed(2)} px`
      : "no chart labels found");
  check("and the glyphs have real outlines again (height > 5 px)",
    phoneFont !== null && phoneFont.maxGlyph > 5,
    phoneFont ? `largest glyph ${phoneFont.maxGlyph.toFixed(2)} px on screen` : "none");

  // --- D4-01 / D4-02 / D4-04 (#256, #257, #259) ---------------------------
  // The audit's finding was not that the floor was wrong but that it never
  // applied: the card rendered at 3.70 px on a 359 px phone tile in the
  // order Lovelace mounts a card, and nothing re-rendered afterwards. The
  // checks above could not see it -- they call `card._render()` by hand
  // after resizing, and they read the LARGEST font in the chart. Everything
  // below mounts the card the way a dashboard does, touches nothing, and
  // reads the SMALLEST axis font, which is what the axis is actually drawn
  // at.
  //
  // A fresh page per scenario: a card that has already been laid out once
  // has a width, and the whole point of the Lovelace order is that the
  // first paint does not.
  const PHONE_TILE = 359;
  // <ha-card> is a Home Assistant element the card renders INSIDE its own
  // shadow root, where a page-level rule cannot reach it. Undefined, it is an
  // inline unknown element and its padding never shapes the chart -- which is
  // exactly the 26 px the shipped floor divided by the wrong width over
  // (#256). This is the frontend's own :host rule set.
  await page.evaluate(() => {
    if (customElements.get("ha-card")) return;
    customElements.define("ha-card", class extends HTMLElement {
      constructor() {
        super();
        this.attachShadow({ mode: "open" }).innerHTML =
          "<style>:host{background:var(--card-background-color,white);" +
          "box-sizing:border-box;border-radius:12px;border-width:1px;" +
          "border-style:solid;border-color:var(--divider-color,#e0e0e0);" +
          "display:block;position:relative;}</style><slot></slot>";
      }
    });
  });
  const mountScript = (order, tile, opts) => async ([st, ord, w, o]) => {
    document.head.querySelectorAll("style.hpo-test").forEach((n) => n.remove());
    document.body.innerHTML = "";
    const style = document.createElement("style");
    style.className = "hpo-test";
    style.textContent = `
      body { margin: 0; font-family: -apple-system, "Segoe UI", sans-serif; }
      heatpump-optimizer-card { display: block; width: ${w}px; }
    `;
    document.head.appendChild(style);
    const card = document.createElement("heatpump-optimizer-card");
    const cfg = Object.assign({ type: "custom:heatpump-optimizer-card" }, o || {});
    if (ord === "lovelace") {
      // What hui-card does: the element is configured and given its data
      // BEFORE it is placed, so its first paint has no width at all.
      card.setConfig(cfg);
      card.hass = { states: st };
      document.body.appendChild(card);
    } else {
      document.body.appendChild(card);
      card.setConfig(cfg);
      card.hass = { states: st };
    }
    window.__card = card;
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    await new Promise((r) => setTimeout(r, 60));
  };
  const mount = async (order, tile, opts) =>
    page.evaluate(mountScript(order, tile, opts), [states, order, tile, opts || null]);

  // The on-screen size of the axis text: the font-size attribute is in
  // viewBox units, so only the svg's own rect turns it into pixels.
  const axisFont = () => page.evaluate(() => {
    const root = window.__card.shadowRoot;
    const svgs = [...root.querySelectorAll(".chartwrap svg")];
    const out = [];
    for (const svg of svgs) {
      const r = svg.getBoundingClientRect();
      if (!r.width) continue;
      const vb = (svg.getAttribute("viewBox") || "0 0 900 380").split(/\s+/);
      const scale = r.width / (Number(vb[2]) || 900);
      // The axis and its annotations. The lane strip's own labels are drawn
      // at 0.8x deliberately and are D4-06's subject, not this floor's.
      const sizes = [...svg.querySelectorAll("text")]
        .filter((t) => (t.getAttribute("font-size") || "").length > 0)
        .filter((t) => (t.textContent || "").trim().length > 0)
        .filter((t) => !/lane-/.test(t.getAttribute("class") || ""))
        .map((t) => Number(t.getAttribute("font-size")) * scale);
      if (sizes.length) {
        out.push({ svgW: r.width, min: Math.min(...sizes), n: sizes.length });
      }
    }
    return out;
  });

  for (const order of ["lovelace", "attached"]) {
    await mount(order, PHONE_TILE);
    const f = await axisFont();
    check(`the ${order} mount order paints the axis at the 8 px floor on a phone tile`,
      f.length === 1 && f[0].min >= 8 - 0.05,
      f.length ? `svg ${f[0].svgW.toFixed(1)} px wide, smallest axis text ${f[0].min.toFixed(2)} px (${f[0].n} labels)`
               : "no chart text found");
  }

  // The ResizeObserver has to RE-RENDER, not just refresh a cached rect:
  // nothing else corrects the font, and the plan sensor that would is on a
  // 30-minute schedule by default.
  await mount("lovelace", PHONE_TILE);
  const resized = await page.evaluate(async () => {
    const card = window.__card;
    let renders = 0;
    const real = card._render.bind(card);
    card._render = (...a) => { renders += 1; return real(...a); };
    card.style.width = "300px";
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    await new Promise((r) => setTimeout(r, 80));
    const svg = card.shadowRoot.querySelector(".chartwrap svg");
    const rect = svg.getBoundingClientRect();
    const vb = (svg.getAttribute("viewBox") || "0 0 900 380").split(/\s+/);
    const scale = rect.width / (Number(vb[2]) || 900);
    const sizes = [...svg.querySelectorAll("text")]
      .filter((t) => (t.getAttribute("font-size") || "").length > 0)
      .filter((t) => (t.textContent || "").trim().length > 0)
      .filter((t) => !/lane-/.test(t.getAttribute("class") || ""))
      .map((t) => Number(t.getAttribute("font-size")) * scale);
    return { renders, svgW: rect.width, min: Math.min(...sizes) };
  });
  check("narrowing the tile re-renders the chart and holds the floor",
    resized.renders >= 1 && resized.min >= 8 - 0.05,
    `${resized.renders} render(s) on resize, svg ${resized.svgW.toFixed(1)} px, smallest axis text ${resized.min.toFixed(2)} px`);

  // The expanded dialog is not a wide chart just because it is a dialog: on
  // a phone it is 360 px across, and it had no floor at all.
  await page.setViewportSize({ width: 375, height: 812 });
  await mount("lovelace", PHONE_TILE, { what_if: true });
  await page.evaluate(async () => {
    window.__card.dialog.open();
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    await new Promise((r) => setTimeout(r, 80));
  });
  const dlgFont = await axisFont();
  check("the expanded dialog holds the 8 px floor on a phone too",
    dlgFont.length === 2 && dlgFont[1].min >= 8 - 0.05,
    dlgFont.length === 2
      ? `dialog svg ${dlgFont[1].svgW.toFixed(1)} px wide, smallest axis text ${dlgFont[1].min.toFixed(2)} px`
      : `${dlgFont.length} chart(s) measured`);

  // The editable slots are the ones still in the future, and the payload's
  // day is fixed while the wall clock is not: against the real clock every
  // slot is already locked, no `.slot-hit` is drawn at all, and a check on
  // slot targets measures an empty set. Freeze six hours into the captured
  // day, as tests/card.mjs does, which always leaves both a locked past and
  // an editable future.
  await page.evaluate(([frozen]) => {
    const Real = Date;
    class Frozen extends Real {
      constructor(...a) { super(...(a.length ? a : [frozen])); }
      static now() { return frozen; }
    }
    window.Date = Frozen;
  }, [Date.parse(plan.dhw_plan.forecast[0].t) + 6 * 3600 * 1000]);
  await mount("lovelace", PHONE_TILE, { what_if: true });
  await page.evaluate(async () => {
    window.__card.dialog.open();
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    await new Promise((r) => setTimeout(r, 80));
  });

  // D4-02: what a pointer or a Tab can land on, and how big it is. The
  // compact tile is a preview -- tapping it opens the dialog -- so it must
  // offer no lane or slot targets at all; the dialog's must clear 24 px.
  const targets = await page.evaluate(() => {
    const root = window.__card.shadowRoot;
    const svgs = [...root.querySelectorAll(".chartwrap svg")];
    const read = (svg) =>
      [...svg.querySelectorAll("rect")]
        .filter((r) => r.hasAttribute("tabindex") || r.getAttribute("role") === "button")
        .map((r) => {
          const b = r.getBoundingClientRect();
          return { cls: r.getAttribute("class"), w: b.width, h: b.height };
        });
    return { tile: read(svgs[0]), dialog: svgs[1] ? read(svgs[1]) : [] };
  });
  check("the compact tile offers no lane or slot target at all",
    targets.tile.length === 0,
    targets.tile.slice(0, 4).map((t) => `${t.cls} ${t.w.toFixed(1)}x${t.h.toFixed(1)}`).join(", "));
  const tooSmall = targets.dialog.filter((t) => Math.min(t.w, t.h) < 24 - 0.05);
  const dialogSlots = targets.dialog.filter((t) => /slot-hit/.test(t.cls || ""));
  check("the dialog really offers editable slot targets to measure",
    dialogSlots.length > 0,
    `${targets.dialog.length} target(s), ${dialogSlots.length} of them slots`);
  check("every lane and slot target in the dialog clears 24 px on both sides",
    targets.dialog.length > 0 && tooSmall.length === 0,
    `${targets.dialog.length} target(s); smallest ` +
    (targets.dialog.length
      ? targets.dialog
          .map((t) => `${t.cls} ${t.w.toFixed(1)}x${t.h.toFixed(1)}`)
          .sort()[0]
      : "none") +
    (tooSmall.length ? `; under: ${tooSmall.slice(0, 4).map((t) => `${t.cls} ${t.w.toFixed(1)}x${t.h.toFixed(1)}`).join(", ")}` : ""));

  // A target that falls short of the floor has to be BOXED IN, not merely
  // clipped on one side. The first review of this fix found every residual
  // target sitting next to 84-258 px of empty lane: the deficit was split in
  // half and each half clipped at its own constraint, so the half a
  // neighbour refused was thrown away instead of offered to the free side.
  // For each target this measures the span between the two things it may not
  // cross -- the nearest neighbouring INK on each side, else the plot edge --
  // and requires that a small target had nowhere to grow.
  const residual = await page.evaluate(() => {
    const root = window.__card.shadowRoot;
    const svgs = [...root.querySelectorAll(".chartwrap svg")];
    const svg = svgs[svgs.length - 1];
    if (!svg) return null;
    const r = svg.getBoundingClientRect();
    const vb = (svg.getAttribute("viewBox") || "0 0 900 380").split(/\s+/);
    const perUnit = r.width / (Number(vb[2]) || 900);
    const num = (el, a) => Number(el.getAttribute(a));
    const inks = [...svg.querySelectorAll("rect.slot")].map((e) => ({
      x1: num(e, "x"), x2: num(e, "x") + num(e, "width"), y: num(e, "y"),
    }));
    const out = [];
    for (const hit of svg.querySelectorAll("rect.slot-hit")) {
      const b = hit.getBoundingClientRect();
      const hx1 = num(hit, "x"), hx2 = hx1 + num(hit, "width"), hy = num(hit, "y");
      const mine = inks.find((i) => i.y === hy && i.x1 >= hx1 - 0.01 && i.x2 <= hx2 + 0.01);
      let limitL = -Infinity, limitR = Infinity;
      let covers = 0;
      for (const ink of inks) {
        if (ink.y !== hy) continue;
        if (mine && ink.x1 === mine.x1 && ink.x2 === mine.x2) continue;
        // The invariant: a target may never cover another slot's ink.
        if (hx1 < ink.x2 - 0.01 && hx2 > ink.x1 + 0.01) covers += 1;
        if (mine && ink.x2 <= mine.x1) limitL = Math.max(limitL, ink.x2);
        if (mine && ink.x1 >= mine.x2) limitR = Math.min(limitR, ink.x1);
      }
      out.push({
        w: b.width, h: b.height, covers,
        // Room the target could occupy without covering anything, in px.
        available: mine
          ? (Math.min(limitR, Number(vb[2])) - Math.max(limitL, 0)) * perUnit
          : b.width,
      });
    }
    return out;
  });
  const covering = (residual || []).filter((t) => t.covers > 0);
  check("no slot target covers another slot's ink",
    residual !== null && covering.length === 0,
    `${covering.length} of ${(residual || []).length} target(s) overlap a neighbour's ink`);
  const roomLeft = (residual || []).filter(
    (t) => Math.min(t.w, t.h) < 24 - 0.05 && t.available > 24 + 1);
  check("a slot target under the floor is boxed in, not merely clipped on one side",
    residual !== null && roomLeft.length === 0,
    roomLeft.slice(0, 4).map((t) =>
      `target ${t.w.toFixed(1)} px with ${t.available.toFixed(1)} px available`).join("; ")
    || `${(residual || []).length} target(s), all at or above the floor`);

  // D4-04: the empty state, which is what the dashboard card picker previews
  // before anything is configured. Its entity ids used to paint up to 47 px
  // outside the card and give the document 40 px of horizontal scroll.
  await page.evaluate(async ([w]) => {
    document.body.innerHTML = "";
    document.head.querySelectorAll("style.hpo-test").forEach((n) => n.remove());
    const style = document.createElement("style");
    style.className = "hpo-test";
    style.textContent =
      `body { margin: 0; } heatpump-optimizer-card { display: block; width: ${w}px; }`;
    document.head.appendChild(style);
    const card = document.createElement("heatpump-optimizer-card");
    card.setConfig({ type: "custom:heatpump-optimizer-card" });
    card.hass = { states: {} };
    document.body.appendChild(card);
    window.__card = card;
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  }, [PHONE_TILE]);
  const spill = await page.evaluate(() => {
    const root = window.__card.shadowRoot;
    const box = root.querySelector("ha-card") || window.__card;
    const cb = box.getBoundingClientRect();
    let worst = 0, who = "";
    const walk = (node) => {
      for (const el of node.querySelectorAll("*")) {
        if (!el.getClientRects().length) continue;
        const b = el.getBoundingClientRect();
        const out = Math.max(cb.left - b.left, b.right - cb.right, 0);
        if (out > worst) { worst = out; who = el.tagName.toLowerCase(); }
      }
    };
    walk(root);
    return {
      worst, who,
      hScroll: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      text: (root.querySelector(".empty") || {}).textContent ? 1 : 0,
    };
  });
  check("the empty state's entity ids stay inside the card box on a phone tile",
    spill.text === 1 && spill.worst <= 1,
    `worst overflow ${spill.worst.toFixed(1)} px (${spill.who || "none"}), document h-scroll ${spill.hScroll} px`);
  check("and the empty state gives the document no horizontal scroll",
    spill.hScroll <= 0, `${spill.hScroll} px of h-scroll`);
} finally {
  await browser.close();
}

console.log(fails ? `\n${fails} BROWSER CHECK(S) FAILED` : "\nALL BROWSER CHECKS PASSED");
process.exit(fails ? 1 : 0);
