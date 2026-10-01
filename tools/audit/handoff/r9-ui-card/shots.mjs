// R9-UI-3 before/after screenshots for the PR body: the card at 900 and 375 px,
// light and dark, against the solved plan tests/plan_view.py writes.
//   node tools/audit/handoff/r9-ui-card/shots.mjs <repo-or-worktree> <out-prefix>
// The merge base's shots come from a worktree at f67f598a (its own payload
// under /tmp/plandata-<hash>.json), the head's from this tree.
import { createRequire } from "node:module"; import fs from "node:fs"; import path from "node:path";
const require = createRequire(import.meta.url);
const { chromium } = require("/opt/node22/lib/node_modules/playwright");
const repo = process.argv[2], out = process.argv[3];
const rig = await import(path.join(repo, "tests/card_rig.mjs"));
const crypto = await import("node:crypto");
const plan = JSON.parse(fs.readFileSync(`/tmp/plandata-${crypto.createHash("sha256").update(path.join(repo,"tests")).digest("hex").slice(0,12)}.json`));
const st = rig.planStates(plan);
st["sensor.heat_pump_optimizer_indoor_temperature_optimizer"] = { state: "20.9", attributes: { device_class: "temperature", unit_of_measurement: "°C" } };
const THEMES = { light: "--primary-color:#03a9f4;--primary-text-color:#212121;--secondary-text-color:#727272;--card-background-color:#ffffff;--primary-background-color:#fafafa;--secondary-background-color:#e5e5e5;--divider-color:rgba(0,0,0,.12);--text-primary-color:#fff",
  dark: "--primary-color:#03a9f4;--primary-text-color:#e1e1e1;--secondary-text-color:#9b9b9b;--card-background-color:#1c1c1c;--primary-background-color:#111111;--secondary-background-color:#282828;--divider-color:rgba(225,225,225,.12);--text-primary-color:#fff" };
const FROZEN = Date.parse(plan.dhw_plan.forecast[0].t) + 6 * 3600000;
const browser = await chromium.launch();
for (const theme of ["light", "dark"]) for (const w of [900, 375]) {
  const ctx = await browser.newContext({ viewport: { width: w + 32, height: 1200 }, deviceScaleFactor: 1 });
  await ctx.clock.setFixedTime(FROZEN);
  const page = await ctx.newPage();
  await page.goto("about:blank");
  await page.addScriptTag({ path: path.join(repo, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js") });
  await page.evaluate(([css, w, st, dark]) => {
    const s = document.createElement("style");
    s.textContent = `html{${css}} body{margin:0;padding:16px;background:var(--primary-background-color);font-family:"Liberation Sans",Arial,sans-serif}`+
      `ha-card{display:block;background:var(--card-background-color);border-radius:12px;color:var(--primary-text-color)} heatpump-optimizer-card{display:block;width:${w}px}`;
    document.head.appendChild(s);
    const c = document.createElement("heatpump-optimizer-card");
    c.setConfig({ type: "custom:heatpump-optimizer-card" });
    c.hass = { states: st, language: "en", themes: { darkMode: dark } };
    document.body.appendChild(c);
  }, [THEMES[theme], w, st, theme === "dark"]);
  await page.waitForTimeout(300);
  await page.locator("heatpump-optimizer-card").screenshot({ path: `${out}-${theme}-${w}.png` });
  await ctx.close();
}
await browser.close();
