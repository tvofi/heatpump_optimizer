// probe3: does the dialog (setup + expanded) overflow a phone viewport?
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
    { key: "wood_tank_top_entity", label: "Wood tank top", place: "wood_tank", entity: null, domains: ["sensor"] } ] };
const states = {
  "sensor.heat_pump_optimizer_solar_irradiance": { state: "120", attributes: { forecast: solarForecast, source: "open_meteo", plan_kind: "solar" } },
  "sensor.heat_pump_optimizer_space_heating_plan": { state: "3", attributes: { forecast: plan.space_plan.forecast, slots: plan.space_plan.slots, total_energy_kwh: plan.space_plan.total_energy_kwh, total_cost: plan.space_plan.total_cost, active_now: plan.space_plan.active_now, plan_kind: "space", setup_topology: topo } },
  "sensor.heat_pump_optimizer_dhw_heating_plan": { state: "4", attributes: { forecast: plan.dhw_plan.forecast, slots: plan.dhw_plan.slots, total_energy_kwh: plan.dhw_plan.total_energy_kwh, total_cost: plan.dhw_plan.total_cost, active_now: plan.dhw_plan.active_now, plan_kind: "dhw" } },
  "sensor.livingroom": { state: "21.3", attributes: {} }, "sensor.tank": { state: "47.5", attributes: {} }, "sensor.outside": { state: "unavailable", attributes: {} },
};
const browser = await chromium.launch();
for (const [label, page0] of [["setup", "setup"], ["expanded", "plan"]]) {
  for (const w of [375, 768, 1280]) {
    const page = await browser.newPage({ viewport: { width: w, height: 900 } });
    await page.goto("about:blank");
    await page.addScriptTag({ path: CARD_SRC });
    await page.evaluate(async ([st, drive]) => {
      const style = document.createElement("style");
      style.textContent = `body{margin:0;font-family:-apple-system,"Segoe UI",sans-serif}heatpump-optimizer-card{display:block;width:100%}`;
      document.head.appendChild(style);
      const card = document.createElement("heatpump-optimizer-card");
      card.setConfig({ type: "custom:heatpump-optimizer-card", what_if: true });
      card.hass = { states: st, language: "en" };
      document.body.appendChild(card);
      window.__card = card;
      await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
      card._onCardClick({});
      if (drive === "setup") { card.dialog.page = "setup"; card._render(); }
      await new Promise((r) => setTimeout(r, 80));
    }, [states, page0]);
    const info = await page.evaluate((which) => {
      const root = window.__card.shadowRoot;
      const vw = window.innerWidth;
      const de = document.documentElement;
      const svg = which === "setup" ? root.querySelector("svg.setup-svg") : root.querySelector(".chartwrap svg");
      const dialog = root.querySelector("dialog");
      const r = svg ? svg.getBoundingClientRect() : null;
      const dr = dialog ? dialog.getBoundingClientRect() : null;
      return { vw, docScrollW: de.scrollWidth, docClientW: de.clientWidth,
        svg: r ? { left: +r.left.toFixed(1), right: +r.right.toFixed(1), width: +r.width.toFixed(1) } : null,
        dialog: dr ? { left: +dr.left.toFixed(1), right: +dr.right.toFixed(1), width: +dr.width.toFixed(1) } : null };
    }, page0);
    console.log(`${label} vp=${w}: docScrollW=${info.docScrollW} clientW=${info.docClientW} hscroll=${info.docScrollW - info.docClientW}; svg=${JSON.stringify(info.svg)}; dialog=${JSON.stringify(info.dialog)}`);
    await page.close();
  }
}
await browser.close();
