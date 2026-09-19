// EXPLORER: does a Swedish session really render the English sentence when
// the what-if cost comes out the same? Drives the production `deltaHtml()` on
// a zero-delta cost and reads the hint it produces, in en and in sv.
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
const states = {
  "sensor.heat_pump_optimizer_solar_irradiance": { state: "120", attributes: { forecast: solarForecast, source: "open_meteo", plan_kind: "solar" } },
  "sensor.heat_pump_optimizer_space_heating_plan": { state: "3", attributes: { forecast: plan.space_plan.forecast, slots: plan.space_plan.slots, total_energy_kwh: plan.space_plan.total_energy_kwh, total_cost: plan.space_plan.total_cost, active_now: plan.space_plan.active_now, plan_kind: "space", day_start_hour: 7, day_end_hour: 22 } },
  "sensor.heat_pump_optimizer_dhw_heating_plan": { state: "4", attributes: { forecast: plan.dhw_plan.forecast, slots: plan.dhw_plan.slots, total_energy_kwh: plan.dhw_plan.total_energy_kwh, total_cost: plan.dhw_plan.total_cost, active_now: plan.dhw_plan.active_now, plan_kind: "dhw" } },
};
const browser = await chromium.launch();
for (const lang of ["en", "sv-SE"]) {
  const page = await browser.newPage({ viewport: { width: 900, height: 900 } });
  await page.goto("about:blank");
  await page.addScriptTag({ path: CARD_SRC });
  const out = await page.evaluate(async ([st, lang]) => {
    if (!customElements.get("ha-card")) customElements.define("ha-card", class extends HTMLElement { constructor(){super();this.attachShadow({mode:"open"}).innerHTML="<style>:host{display:block}</style><slot></slot>";} });
    const card = document.createElement("heatpump-optimizer-card");
    card.setConfig({ type: "custom:heatpump-optimizer-card", what_if: true });
    card.hass = { states: st, language: lang };
    document.body.appendChild(card);
    window.__card = card;
    await new Promise((r) => setTimeout(r, 150));
    // Exercise the production branch: cls === "" picks stats.delta_detail_same.
    const panel = card.manual;
    panel.costDelta = () => ({ planned: 12.34, edited: 12.34, delta: 0 });
    const html = panel.deltaHtml();
    const div = document.createElement("div");
    div.innerHTML = html;
    return { html: html.replace(/\s+/g, " ").trim(), hint: (div.querySelector(".wi-hint") || {}).textContent };
  }, [states, lang]);
  console.log(`--- language=${lang}`);
  console.log(`    hint: ${JSON.stringify(out.hint)}`);
  await page.close();
}
await browser.close();
