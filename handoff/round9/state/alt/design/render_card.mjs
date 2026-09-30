// node render_card.mjs <card.js> <out.png> <light|dark> <width> [dialog]
import { chromium } from 'playwright';
import fs from 'fs';
const [,, cardJs, out, theme, width, mode = 'before'] = process.argv;
const plan = JSON.parse(fs.readFileSync('plandata.json', 'utf8'));
const solar = plan.space_plan.forecast.map((p, i) => ({ t: p.t, ghi: Math.max(0, 400 * Math.sin((i / plan.space_plan.forecast.length) * Math.PI)) }));
const states = {
  'sensor.heat_pump_optimizer_solar_irradiance': { state: '120', attributes: { forecast: solar, source: 'open_meteo', friendly_name: 'Solar Irradiance', plan_kind: 'solar' } },
  'sensor.heat_pump_optimizer_plan_space_heating': { state: '3 slots planned', attributes: { forecast: plan.space_plan.forecast, slots: plan.space_plan.slots, total_energy_kwh: plan.space_plan.total_energy_kwh, total_cost: plan.space_plan.total_cost, active_now: plan.space_plan.active_now, friendly_name: 'Space Heating Plan', plan_kind: 'space' } },
  'sensor.heat_pump_optimizer_plan_dhw_heating': { state: '4 slots planned', attributes: { forecast: plan.dhw_plan.forecast, slots: plan.dhw_plan.slots, total_energy_kwh: plan.dhw_plan.total_energy_kwh, total_cost: plan.dhw_plan.total_cost, active_now: plan.dhw_plan.active_now, friendly_name: 'DHW Heating Plan', plan_kind: 'dhw' } },
};
const HA = {
  light: { '--primary-text-color': '#212121', '--secondary-text-color': '#727272', '--card-background-color': '#ffffff', '--primary-background-color': '#fafafa', '--secondary-background-color': '#e5e5e5', '--divider-color': 'rgba(0,0,0,.12)', '--primary-color': '#03a9f4', '--text-primary-color': '#ffffff' },
  dark: { '--primary-text-color': '#e1e1e1', '--secondary-text-color': '#9b9b9b', '--card-background-color': '#1c1c1c', '--primary-background-color': '#111111', '--secondary-background-color': '#282828', '--divider-color': 'rgba(225,225,225,.12)', '--primary-color': '#03a9f4', '--text-primary-color': '#ffffff' },
}[theme];
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const page = await browser.newPage({ viewport: { width: +width + 48, height: 900 }, deviceScaleFactor: 2 });
page.on('pageerror', (e) => console.error('pageerror', e.message));
await page.goto('about:blank');
await page.addScriptTag({ path: cardJs });
await page.evaluate(([st, vars, dark, w]) => {
  const s = document.createElement('style');
  s.textContent = `body{margin:0;padding:24px;background:${vars['--primary-background-color']};font-family:Roboto,-apple-system,"Segoe UI",sans-serif}
   .wrap{width:${w}px;background:var(--card-background-color);border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,.2)}`;
  document.head.appendChild(s);
  for (const [k, v] of Object.entries(vars)) document.documentElement.style.setProperty(k, v);
  const wrap = document.createElement('div'); wrap.className = 'wrap';
  const card = document.createElement('heatpump-optimizer-card');
  wrap.appendChild(card); document.body.appendChild(wrap);
  card.setConfig({ type: 'custom:heatpump-optimizer-card' });
  card.hass = { states: st, themes: { darkMode: dark }, language: 'en', locale: { language: 'en' } };
  window.__card = card;
}, [states, HA, theme === 'dark', +width]);
await page.waitForTimeout(400);
if (mode === 'after') {
  await page.addScriptTag({ path: 'overlay.js' });
  const sp = plan.space_plan, dp = plan.dhw_plan;
  await page.evaluate(([d, dark]) => { window.__stats = d; window.__applyProposal(dark); },
    [{ price: sp.forecast[0].price.toFixed(2), kwh: (sp.total_energy_kwh + dp.total_energy_kwh).toFixed(1), cost: (sp.total_cost + dp.total_cost).toFixed(2), indoor: sp.forecast[0].room.toFixed(1) }, theme === 'dark']);
  await page.waitForTimeout(200);
}
const box = await page.evaluate(() => { const r = document.querySelector('.wrap').getBoundingClientRect(); return { x: r.x, y: r.y, width: r.width, height: r.height }; });
await page.screenshot({ path: out, clip: { x: box.x - 12, y: box.y - 12, width: box.width + 24, height: box.height + 24 } });
await browser.close();
