// EXPLORER: interactive-element sizes across card states, fine and coarse
// pointer. Flags any control whose smaller side is under the SC 2.5.8 floor
// (24 px; 44 px under a coarse pointer for SVG-drawn targets).
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
const bigStates = () => { const st = {}; for (let i=0;i<400;i++) st[`sensor.zz_probe_${String(i).padStart(3,"0")}`]={state:"20.0",attributes:{unit_of_measurement:"°C",friendly_name:`Probe ${String(i).padStart(3,"0")}`}};
  st["sensor.vedpanna_temperatur_temperature"]={state:"71.2",attributes:{unit_of_measurement:"°C",friendly_name:"Vedpanna temperatur"}};
  st["sensor.vedpanna_temperatur_temperature_2"]={state:"48.9",attributes:{unit_of_measurement:"°C",friendly_name:"Vedpanna temperatur"}}; return st; };
const baseStates = (extra) => ({
  "sensor.heat_pump_optimizer_solar_irradiance": { state: "120", attributes: { forecast: solarForecast, source: "open_meteo", plan_kind: "solar" } },
  "sensor.heat_pump_optimizer_space_heating_plan": { state: "3", attributes: { forecast: plan.space_plan.forecast, slots: plan.space_plan.slots, total_energy_kwh: plan.space_plan.total_energy_kwh, total_cost: plan.space_plan.total_cost, active_now: plan.space_plan.active_now, plan_kind: "space", setup_topology: topo, day_start_hour: 7, day_end_hour: 22 } },
  "sensor.heat_pump_optimizer_dhw_heating_plan": { state: "4", attributes: { forecast: plan.dhw_plan.forecast, slots: plan.dhw_plan.slots, total_energy_kwh: plan.dhw_plan.total_energy_kwh, total_cost: plan.dhw_plan.total_cost, active_now: plan.dhw_plan.active_now, plan_kind: "dhw", dhw_windows: "06:00-08:30, 17:00-22:00" } },
  "sensor.livingroom": { state: "21.3", attributes: {} }, "sensor.tank": { state: "47.5", attributes: {} }, "sensor.outside": { state: "unavailable", attributes: {} },
  ...(extra || {}) });

const SCEN = {
  inline:      { cfg: {}, drive: "" },
  expanded:    { cfg: { what_if: true }, drive: "window.__card._onCardClick({});" },
  setup:       { cfg: {}, drive: "window.__card._onCardClick({}); window.__card.dialog.page='setup'; window.__card._render();" },
  setup_edit:  { cfg: {}, drive: "window.__card._onCardClick({}); window.__card.dialog.page='setup'; window.__card._render(); const t=window.__card.shadowRoot.querySelector('.layout-edit-toggle'); if(t) t.click(); window.__card._render();" },
  picker:      { cfg: {}, extra: bigStates(), drive: "window.__card._onCardClick({}); window.__card.dialog.page='setup'; window.__card._render(); const h=[...window.__card.shadowRoot.querySelectorAll('.setup-hit')].find(x=>x.dataset.key==='wood_tank_top_entity'); if(h) h.dispatchEvent(new MouseEvent('click',{bubbles:true})); window.__card._render();" },
};

const COLLECT = (coarse) => {
  const root = window.__card.shadowRoot;
  const SEL = "button, .chip, .dlg-tab, .expand, .close, input, select, textarea, [tabindex], rect.setup-hit, rect.slot-hit, [role='button']";
  const out = [];
  const seen = new Set();
  for (const el of root.querySelectorAll(SEL)) {
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden" || el.disabled) continue;
    const b = el.getBoundingClientRect();
    if (b.width <= 0 || b.height <= 0) continue;
    const key = `${el.tagName}.${String(el.getAttribute("class") || "")}@${Math.round(b.x)},${Math.round(b.y)}`;
    if (seen.has(key)) continue; seen.add(key);
    const min = Math.min(b.width, b.height);
    const floor = coarse && (el.tagName === "rect") ? 44 : 24;
    out.push({ tag: el.tagName, cls: String(el.getAttribute("class") || ""), w: +b.width.toFixed(2), h: +b.height.toFixed(2), min: +min.toFixed(2), floor, under: min < floor - 0.05 });
  }
  return out;
};

const browser = await chromium.launch();
const report = [];
for (const coarse of [false, true]) {
  for (const [vpName, vp] of Object.entries({ phone: { width: 375, height: 812 }, tablet: { width: 768, height: 1024 }, desktop: { width: 1280, height: 800 } })) {
    for (const [scName, sc] of Object.entries(SCEN)) {
      const ctx = await browser.newContext({ viewport: vp });
      const page = await ctx.newPage();
      await page.goto("about:blank");
      if (coarse) {
        const cdp = await ctx.newCDPSession(page);
        await cdp.send("Emulation.setEmulatedMedia", { features: [{ name: "pointer", value: "coarse" }] });
      }
      await page.addScriptTag({ path: CARD_SRC });
      await page.evaluate(async ([st, cfg, drive, coarse]) => {
        if (coarse) { const o = window.matchMedia.bind(window); window.matchMedia = (q) => q === "(pointer: coarse)" ? { matches: true, media: q, onchange: null, addEventListener(){}, removeEventListener(){}, addListener(){}, removeListener(){}, dispatchEvent(){return true;} } : o(q); }
        if (!customElements.get("ha-card")) customElements.define("ha-card", class extends HTMLElement { constructor(){super();this.attachShadow({mode:"open"}).innerHTML="<style>:host{background:var(--card-background-color,white);box-sizing:border-box;border-radius:12px;border-width:1px;border-style:solid;border-color:var(--divider-color,#e0e0e0);display:block;position:relative;}</style><slot></slot>";} });
        const style = document.createElement("style");
        style.textContent = `body{margin:0;font-family:-apple-system,"Segoe UI",sans-serif}heatpump-optimizer-card{display:block;width:100%}`;
        document.head.appendChild(style);
        const card = document.createElement("heatpump-optimizer-card");
        card.setConfig(Object.assign({ type: "custom:heatpump-optimizer-card" }, cfg));
        card.hass = { states: st, language: "en" };
        document.body.appendChild(card);
        window.__card = card;
        await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
        await new Promise((r) => setTimeout(r, 60));
        if (drive) eval(drive);
        await new Promise((r) => setTimeout(r, 80));
      }, [baseStates(sc.extra), sc.cfg, sc.drive, coarse]);
      const controls = await page.evaluate(COLLECT, coarse);
      const under = controls.filter((c) => c.under);
      report.push({ coarse, vpName, scName, n: controls.length, under });
      await ctx.close();
    }
  }
}
await browser.close();
for (const r of report) {
  if (r.under.length) {
    console.log(`--- ${r.scName} ${r.vpName} coarse=${r.coarse}: ${r.under.length}/${r.n} under floor`);
    for (const u of r.under.slice(0, 8)) console.log(`    ${u.tag}.${u.cls} ${u.w}x${u.h} min=${u.min} floor=${u.floor}`);
  }
}
console.log("done");
