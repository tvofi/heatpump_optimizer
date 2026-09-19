// EXPLORER: the setup page's row hit rects.
//  (a) rendered height (CSS px) vs the SC 2.5.8 floor (24 px fine / 44 px coarse)
//  (b) per-column pitch overlap, and (c) -- the decisive one -- what a tap
//      aimed at each row's own visible label actually resolves to, via
//      shadowRoot.elementFromPoint at the label's screen point. The production
//      handler is a per-element click listener using ev.currentTarget, so the
//      element that hit-testing returns IS the slot the tap assigns.
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(__dirname, "../../../..");
const plan = JSON.parse(readFileSync(process.env.HPO_PLANDATA, "utf8"));
const CARD_SRC = path.join(repo, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js");
const solarForecast = plan.space_plan.forecast.map((p, i) => ({ t: p.t, ghi: Math.max(0, 400 * Math.sin((i / plan.space_plan.forecast.length) * Math.PI)) }));
const topo = { two_zone: true, dhw: true, valve_mode: "manual", buffer: { volume_l: 750, is_store: true, max_temp: 70 }, wood: { present: true, volume_l: 500 },
  edges: [["heat_pump","buffer_tank"],["buffer_tank","mixing_valve"],["mixing_valve","upper_zone"],["mixing_valve","lower_zone"],["wood_tank","buffer_tank"],["heat_pump","dhw_tank"]],
  slots: [ { key: "indoor_temp_entity", label: "Indoor temperature", place: "upper_zone", entity: "sensor.livingroom", domains: ["sensor"] },
    { key: "buffer_tank_temp_entity", label: "Buffer tank temperature", place: "buffer_tank", entity: "sensor.tank", domains: ["sensor"] },
    { key: "wood_tank_top_entity", label: "Wood tank top", place: "wood_tank", entity: null, domains: ["sensor"] },
    { key: "outdoor_temp_entity", label: "Outdoor temperature", place: "outdoor", entity: "sensor.outside", domains: ["sensor"] },
    { key: "lower_floor_temp_entity", label: "Lower floor temperature", place: "lower_zone", entity: null, domains: ["sensor"] } ] };
const states = {
  "sensor.heat_pump_optimizer_solar_irradiance": { state: "120", attributes: { forecast: solarForecast, source: "open_meteo", plan_kind: "solar" } },
  "sensor.heat_pump_optimizer_space_heating_plan": { state: "3", attributes: { forecast: plan.space_plan.forecast, slots: plan.space_plan.slots, total_energy_kwh: plan.space_plan.total_energy_kwh, total_cost: plan.space_plan.total_cost, active_now: plan.space_plan.active_now, plan_kind: "space", setup_topology: topo, day_start_hour: 7, day_end_hour: 22 } },
  "sensor.heat_pump_optimizer_dhw_heating_plan": { state: "4", attributes: { forecast: plan.dhw_plan.forecast, slots: plan.dhw_plan.slots, total_energy_kwh: plan.dhw_plan.total_energy_kwh, total_cost: plan.dhw_plan.total_cost, active_now: plan.dhw_plan.active_now, plan_kind: "dhw" } },
  "sensor.livingroom": { state: "21.3", attributes: {} }, "sensor.tank": { state: "47.5", attributes: {} }, "sensor.outside": { state: "unavailable", attributes: {} },
};
const ROWH = 17, HITBASE = 15, PAD = 16;
const MEASURE = (rowH, hitBase, pad) => {
  const root = window.__card.shadowRoot;
  const svg = root.querySelector("svg.setup-svg");
  const ctm = svg.getScreenCTM();
  const pt = (u, v) => { const p = svg.createSVGPoint(); p.x = u; p.y = v; return p.matrixTransform(ctm); };
  const sr = svg.getBoundingClientRect();
  const hits = [...root.querySelectorAll("rect.setup-hit")].map((r) => {
    const b = r.getBoundingClientRect();
    const ux = parseFloat(r.getAttribute("x")), uy = parseFloat(r.getAttribute("y")), uh = parseFloat(r.getAttribute("height"));
    // The label's baseline, reconstructed from the row geometry the card used.
    const textV = uy + rowH - 5 + (uh - hitBase) / 2;
    const aim = pt(ux + pad + 30, textV - 4);
    const under = root.elementFromPoint ? root.elementFromPoint(aim.x, aim.y) : null;
    return { key: r.dataset.key, x: +b.left.toFixed(1), top: +b.top.toFixed(2), h: +b.height.toFixed(2),
      aimsAt: under && under.dataset ? under.dataset.key : (under ? under.tagName : null) };
  });
  // per-column pitch/overlap
  const cols = new Map();
  for (const h of hits) { if (!cols.has(h.x)) cols.set(h.x, []); cols.get(h.x).push(h); }
  const colsOut = [];
  for (const [x, rows] of cols) {
    rows.sort((a, b) => a.top - b.top);
    let ov = 0;
    const pitch = rows.length > 1 ? +(rows[1].top - rows[0].top).toFixed(1) : null;
    for (let i = 1; i < rows.length; i++) ov = Math.max(ov, (rows[i-1].top + rows[i-1].h) - rows[i].top);
    colsOut.push({ x, n: rows.length, pitch, maxOverlap: +ov.toFixed(1) });
  }
  return { svgW: +sr.width.toFixed(1), scale: +(sr.width / 720).toFixed(4), n: hits.length,
    minH: +Math.min(...hits.map((h) => h.h)).toFixed(2), maxH: +Math.max(...hits.map((h) => h.h)).toFixed(2),
    misrouted: hits.filter((h) => h.aimsAt !== h.key).length,
    detail: hits.map((h) => `${h.key}->${h.aimsAt}`), cols: colsOut };
};
const browser = await chromium.launch();
console.log("tile ptr     svgW  scale  n minH   maxH   misrouted");
for (const coarse of [false, true]) {
  for (const w of [375, 768, 1280]) {
    const ctx = await browser.newContext({ viewport: { width: w, height: 900 } });
    const page = await ctx.newPage();
    await page.goto("about:blank");
    if (coarse) { const cdp = await ctx.newCDPSession(page); await cdp.send("Emulation.setEmulatedMedia", { features: [{ name: "pointer", value: "coarse" }] }); }
    await page.addScriptTag({ path: CARD_SRC });
    await page.evaluate(async ([st, coarse]) => {
      if (coarse) { const o = window.matchMedia.bind(window); window.matchMedia = (q) => q === "(pointer: coarse)" ? { matches: true, media: q, addEventListener(){}, removeEventListener(){}, addListener(){}, removeListener(){} } : o(q); }
      if (!customElements.get("ha-card")) customElements.define("ha-card", class extends HTMLElement { constructor(){super();this.attachShadow({mode:"open"}).innerHTML="<style>:host{background:var(--card-background-color,white);display:block}</style><slot></slot>";} });
      const card = document.createElement("heatpump-optimizer-card");
      card.setConfig({ type: "custom:heatpump-optimizer-card" });
      card.hass = { states: st, language: "en" };
      document.body.appendChild(card);
      window.__card = card;
      await new Promise((r) => setTimeout(r, 120));
      card._onCardClick({});
      card.dialog.page = "setup";
      card._render();
      await new Promise((r) => setTimeout(r, 120));
    }, [states, coarse]);
    const m = await page.evaluate(`(${MEASURE.toString()})(${ROWH},${HITBASE},${PAD})`);
    console.log(`${String(w).padEnd(5)} ${(coarse ? "coarse" : "fine").padEnd(7)} ${String(m.svgW).padEnd(6)} ${String(m.scale).padEnd(6)} ${String(m.n).padEnd(1)} ${String(m.minH).padEnd(6)} ${String(m.maxH).padEnd(6)} ${m.misrouted}/${m.n}`);
    console.log(`      cols ${JSON.stringify(m.cols)}`);
    if (m.misrouted) console.log(`      ${m.detail.join("  ")}`);
    await ctx.close();
  }
}
await browser.close();
