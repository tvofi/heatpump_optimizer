// D4 round 3 -- the screenshots the report points at. Not a measuring
// instrument: it re-renders the two states the findings name and writes PNGs.
//
//   HPO_PLANDATA=$TMPDIR/plandata-d4.json NODE_PATH=/private/tmp/hpo-pw/node_modules \
//   PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers \
//   node tools/audit/round3/D4/shots.mjs tools/audit/round3/D4/shots
import { existsSync, readFileSync, mkdirSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(__dirname, "../../../..");
const CARD_SRC = path.join(repo, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js");
const testsDir = path.join(repo, "tests");
const planPath = process.env.HPO_PLANDATA || path.join("/tmp",
  `plandata-${createHash("sha256").update(testsDir).digest("hex").slice(0, 12)}.json`);
if (!existsSync(planPath)) { console.error("run tests/plan_view.py first"); process.exit(1); }
const plan = JSON.parse(readFileSync(planPath, "utf8"));
const outDir = process.argv[2] || path.join(__dirname, "shots");
mkdirSync(outDir, { recursive: true });

const SOLAR = "sensor.heat_pump_optimizer_solar_irradiance";
const SPACE = "sensor.heat_pump_optimizer_space_heating_plan";
const DHW = "sensor.heat_pump_optimizer_dhw_heating_plan";
const planStates = () => ({
  [SOLAR]: { state: "120", attributes: { forecast: plan.space_plan.forecast.map((q,i)=>({t:q.t,
    ghi: Math.max(0, 400*Math.sin((i/plan.space_plan.forecast.length)*Math.PI))})),
    source:"open_meteo", friendly_name:"Solar Irradiance", plan_kind:"solar" } },
  [SPACE]: { state:"3 slots planned", attributes:{ forecast:plan.space_plan.forecast,
    slots:plan.space_plan.slots, total_energy_kwh:plan.space_plan.total_energy_kwh,
    total_cost:plan.space_plan.total_cost, active_now:plan.space_plan.active_now,
    friendly_name:"Space Heating Plan", plan_kind:"space" } },
  [DHW]: { state:"4 slots planned", attributes:{ forecast:plan.dhw_plan.forecast,
    slots:plan.dhw_plan.slots, total_energy_kwh:plan.dhw_plan.total_energy_kwh,
    total_cost:plan.dhw_plan.total_cost, active_now:plan.dhw_plan.active_now,
    friendly_name:"DHW Heating Plan", plan_kind:"dhw" } },
});
const awayStates = () => {
  const st = planStates();
  st["switch.heat_pump_optimizer_away"] = { state:"on", attributes:{} };
  st["datetime.heat_pump_optimizer_away_return"] = { state:"2026-01-16T18:00:00", attributes:{} };
  st["binary_sensor.heat_pump_optimizer_away_mode"] = { state:"off", attributes:{source:"none"} };
  return st;
};
const HA_LIGHT = `--primary-text-color:#212121;--secondary-text-color:#727272;
  --text-primary-color:#fff;--primary-color:#03a9f4;--card-background-color:#fff;
  --divider-color:rgba(0,0,0,.12);--primary-background-color:#fafafa;
  --secondary-background-color:#e5e5e5;--warning-color:#ffa600;--error-color:#db4437;
  --success-color:#43a047;--info-color:#039be5;`;
const HA_DARK = `--primary-text-color:#e1e1e1;--secondary-text-color:#9b9b9b;
  --text-primary-color:#fff;--primary-color:#03a9f4;--card-background-color:#1c1c1c;
  --divider-color:rgba(225,225,225,.12);--primary-background-color:#111111;
  --secondary-background-color:#202020;--warning-color:#ffa600;--error-color:#db4437;
  --success-color:#43a047;--info-color:#039be5;`;
const HA_CARD_DEF = `if (!customElements.get("ha-card")) {
  customElements.define("ha-card", class extends HTMLElement { constructor(){ super();
    this.attachShadow({mode:"open"}).innerHTML =
      "<style>:host{background:var(--card-background-color,#fff);box-sizing:border-box;"+
      "border-radius:12px;border-width:1px;border-style:solid;"+
      "border-color:var(--divider-color,#e0e0e0);color:var(--primary-text-color);"+
      "display:block;position:relative;}</style><slot></slot>"; }});}`;

const browser = await chromium.launch();
const shoot = async (name, states, theme, bg, after, coarse) => {
  const page = await browser.newPage({ viewport: { width: 420, height: 900 }, deviceScaleFactor: 2 });
  await page.route("**/*", (r) => r.fulfill({ status:200, contentType:"text/html",
    body:"<!doctype html><html><head></head><body></body></html>" }));
  await page.goto("http://heatpump-optimizer.test/");
  if (coarse) {
    const cdp = await page.context().newCDPSession(page);
    await cdp.send("Emulation.setEmulatedMedia", { features: [
      { name:"pointer", value:"coarse" }, { name:"any-pointer", value:"coarse" },
      { name:"hover", value:"none" }] });
    await page.evaluate(() => { const o = window.matchMedia.bind(window);
      window.matchMedia = (q) => (q === "(pointer: coarse)" || q === "(hover: none)")
        ? { matches:true, media:q, onchange:null, addEventListener(){}, removeEventListener(){},
            addListener(){}, removeListener(){}, dispatchEvent(){return true;} } : o(q); });
  }
  await page.addScriptTag({ path: CARD_SRC });
  await page.evaluate(HA_CARD_DEF);
  await page.evaluate(async ([st, th, pageBg]) => {
    const style = document.createElement("style");
    style.textContent = `body{margin:0;padding:16px;background:${pageBg};` +
      `font-family:-apple-system,"Segoe UI",sans-serif}` +
      `heatpump-optimizer-card{display:block;width:359px;${th}}`;
    document.head.appendChild(style);
    const card = document.createElement("heatpump-optimizer-card");
    card.setConfig({ type: "custom:heatpump-optimizer-card" });
    card.hass = { states: st, language: "en" };
    document.body.appendChild(card);
    window.__card = card;
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    await new Promise((r) => setTimeout(r, 80));
  }, [states, theme, bg]);
  if (after) await page.evaluate(after);
  await page.screenshot({ path: path.join(outDir, name + ".png"), fullPage: true });
  await page.close();
  console.log("wrote", name + ".png");
};
const openDialog = async () => {
  window.__card._onCardClick({});
  await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  await new Promise((r) => setTimeout(r, 100));
};
await shoot("D4-01-no-plan-light", {}, HA_LIGHT, "#fafafa", null, false);
await shoot("D4-01-no-plan-dark", {}, HA_DARK, "#111111", null, false);
await shoot("D4-01-plan-light-control", planStates(), HA_LIGHT, "#fafafa", null, false);
await shoot("D4-02-away-strip-coarse", awayStates(), HA_LIGHT, "#fafafa", openDialog, true);
await browser.close();
