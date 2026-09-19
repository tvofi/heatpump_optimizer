// screenshots of key card states for eyeball review.
import { createRequire } from "node:module";
import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(__dirname, "../../../..");
const plan = JSON.parse(readFileSync(process.env.HPO_PLANDATA, "utf8"));
const CARD_SRC = path.join(repo, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js");
const outDir = process.env.SHOT_DIR || "/tmp/heatpump-orch/audit-r5-D4";
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
  "sensor.heat_pump_optimizer_space_heating_plan": { state: "3 slots planned", attributes: { forecast: plan.space_plan.forecast, slots: plan.space_plan.slots, total_energy_kwh: plan.space_plan.total_energy_kwh, total_cost: plan.space_plan.total_cost, active_now: plan.space_plan.active_now, plan_kind: "space", setup_topology: topo, day_start_hour: 7, day_end_hour: 22 } },
  "sensor.heat_pump_optimizer_dhw_heating_plan": { state: "4 slots planned", attributes: { forecast: plan.dhw_plan.forecast, slots: plan.dhw_plan.slots, total_energy_kwh: plan.dhw_plan.total_energy_kwh, total_cost: plan.dhw_plan.total_cost, active_now: plan.dhw_plan.active_now, plan_kind: "dhw", dhw_windows: "06:00-08:30, 17:00-22:00" } },
  "sensor.livingroom": { state: "21.3", attributes: {} }, "sensor.tank": { state: "47.5", attributes: {} }, "sensor.outside": { state: "unavailable", attributes: {} },
};
const SHOTS = [
  { name: "plan-phone-en", w: 375, lang: "en", drive: "" },
  { name: "plan-phone-sv", w: 375, lang: "sv-SE", drive: "" },
  { name: "expanded-phone-en", w: 375, lang: "en", cfg: { what_if: true }, drive: "window.__card._onCardClick({});" },
  { name: "setup-phone-en", w: 375, lang: "en", drive: "window.__card._onCardClick({}); window.__card.dialog.page='setup'; window.__card._render();" },
  { name: "plan-desktop-sv", w: 1280, lang: "sv-SE", drive: "" },
  { name: "expanded-desktop-en", w: 1280, lang: "en", cfg: { what_if: true }, drive: "window.__card._onCardClick({});" },
];
const browser = await chromium.launch();
for (const s of SHOTS) {
  const page = await browser.newPage({ viewport: { width: s.w, height: 1000 } });
  await page.goto("about:blank");
  await page.addScriptTag({ path: CARD_SRC });
  await page.evaluate(async ([st, lang, cfg, drive]) => {
    if (!customElements.get("ha-card")) customElements.define("ha-card", class extends HTMLElement { constructor(){super();this.attachShadow({mode:"open"}).innerHTML="<style>:host{background:var(--card-background-color,white);box-sizing:border-box;border-radius:12px;border-width:1px;border-style:solid;border-color:var(--divider-color,#e0e0e0);display:block;position:relative;}</style><slot></slot>";} });
    const style = document.createElement("style");
    style.textContent = `body{margin:0;font-family:-apple-system,"Segoe UI",sans-serif}heatpump-optimizer-card{display:block;width:100%;--primary-text-color:#212121;--secondary-text-color:#727272;--primary-color:#03a9f4;--card-background-color:#fff;--divider-color:rgba(0,0,0,.12)}`;
    document.head.appendChild(style);
    const card = document.createElement("heatpump-optimizer-card");
    card.setConfig(Object.assign({ type: "custom:heatpump-optimizer-card" }, cfg || {}));
    card.hass = { states: st, language: lang };
    document.body.appendChild(card);
    window.__card = card;
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    await new Promise((r) => setTimeout(r, 60));
    if (drive) eval(drive);
    await new Promise((r) => setTimeout(r, 120));
  }, [states, s.lang, s.cfg, s.drive]);
  const el = await page.$("heatpump-optimizer-card");
  const buf = await el.screenshot({ type: "png" });
  writeFileSync(path.join(outDir, `shot-${s.name}.png`), buf);
  console.log(`shot-${s.name}.png`, buf.length, "bytes");
  await page.close();
}
await browser.close();
