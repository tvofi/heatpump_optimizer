// zoom: high-DPI crop of a card region, to inspect overlapping labels.
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
const outDir = process.env.SHOT_DIR || "/tmp/heatpump-orch/audit-r5-D4/shots";
const solarForecast = plan.space_plan.forecast.map((p, i) => ({ t: p.t, ghi: Math.max(0, 400 * Math.sin((i / plan.space_plan.forecast.length) * Math.PI)) }));
const states = {
  "sensor.heat_pump_optimizer_solar_irradiance": { state: "120", attributes: { forecast: solarForecast, source: "open_meteo", plan_kind: "solar" } },
  "sensor.heat_pump_optimizer_space_heating_plan": { state: "3", attributes: { forecast: plan.space_plan.forecast, slots: plan.space_plan.slots, total_energy_kwh: plan.space_plan.total_energy_kwh, total_cost: plan.space_plan.total_cost, active_now: plan.space_plan.active_now, plan_kind: "space" } },
  "sensor.heat_pump_optimizer_dhw_heating_plan": { state: "4", attributes: { forecast: plan.dhw_plan.forecast, slots: plan.dhw_plan.slots, total_energy_kwh: plan.dhw_plan.total_energy_kwh, total_cost: plan.dhw_plan.total_cost, active_now: plan.dhw_plan.active_now, plan_kind: "dhw" } },
};
const browser = await chromium.launch();
for (const [name, w, lang] of [["phone-sv", 375, "sv-SE"], ["phone-en", 375, "en"]]) {
  const page = await browser.newPage({ viewport: { width: w, height: 1000 }, deviceScaleFactor: 4 });
  await page.goto("about:blank");
  await page.addScriptTag({ path: CARD_SRC });
  await page.evaluate(async ([st, lang]) => {
    if (!customElements.get("ha-card")) customElements.define("ha-card", class extends HTMLElement { constructor(){super();this.attachShadow({mode:"open"}).innerHTML="<style>:host{background:var(--card-background-color,white);box-sizing:border-box;border-radius:12px;border-width:1px;border-style:solid;border-color:var(--divider-color,#e0e0e0);display:block;position:relative;}</style><slot></slot>";} });
    const style = document.createElement("style");
    style.textContent = `body{margin:0;font-family:-apple-system,"Segoe UI",sans-serif}heatpump-optimizer-card{display:block;width:100%;--primary-text-color:#212121;--secondary-text-color:#727272;--primary-color:#03a9f4;--card-background-color:#fff;--divider-color:rgba(0,0,0,.12)}`;
    document.head.appendChild(style);
    const card = document.createElement("heatpump-optimizer-card");
    card.setConfig({ type: "custom:heatpump-optimizer-card" });
    card.hass = { states: st, language: lang };
    document.body.appendChild(card);
    window.__card = card;
    await new Promise((r) => setTimeout(r, 150));
  }, [states, lang]);
  const box = await page.evaluate(() => {
    const svg = window.__card.shadowRoot.querySelector(".chartwrap svg");
    const r = svg.getBoundingClientRect();
    return { x: r.x, y: r.y, width: r.width, height: r.height };
  });
  // bottom-left quadrant: lane labels + axis
  const clip = { x: Math.max(0, box.x), y: box.y, width: box.width * 0.55, height: box.height * 0.5 };
  await page.screenshot({ path: path.join(outDir, `zoom-lane-${name}.png`), clip });
  console.log(`zoom-lane-${name}.png`);
  await page.close();
}
await browser.close();
