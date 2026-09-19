// EXPLORER: WCAG contrast of EVERY text-bearing element across states,
// themes and viewports. The shipped lane checks four named sites; this
// checks all of them and reports the worst offenders.
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
  "sensor.heat_pump_optimizer_space_heating_plan": { state: "3", attributes: { forecast: plan.space_plan.forecast, slots: plan.space_plan.slots, total_energy_kwh: plan.space_plan.total_energy_kwh, total_cost: plan.space_plan.total_cost, active_now: plan.space_plan.active_now, plan_kind: "space", setup_topology: topo, day_start_hour:7, day_end_hour:22 } },
  "sensor.heat_pump_optimizer_dhw_heating_plan": { state: "4", attributes: { forecast: plan.dhw_plan.forecast, slots: plan.dhw_plan.slots, total_energy_kwh: plan.dhw_plan.total_energy_kwh, total_cost: plan.dhw_plan.total_cost, active_now: plan.dhw_plan.active_now, plan_kind: "dhw", dhw_windows: "06:00-08:30, 17:00-22:00" } },
  "sensor.livingroom": { state: "21.3", attributes: {} }, "sensor.tank": { state: "47.5", attributes: {} }, "sensor.outside": { state: "unavailable", attributes: {} },
};
const SCEN = {
  inline:   { cfg: {}, drive: "" },
  expanded: { cfg: { what_if: true }, drive: "window.__card._onCardClick({});" },
  setup:    { cfg: {}, drive: "window.__card._onCardClick({}); window.__card.dialog.page='setup'; window.__card._render();" },
};
const THEMES = {
  HA_light: "--primary-text-color:#212121;--secondary-text-color:#727272;--text-primary-color:#fff;--primary-color:#03a9f4;--card-background-color:#fff;--divider-color:rgba(0,0,0,.12);",
  HA_dark:  "--primary-text-color:#e1e1e1;--secondary-text-color:#9b9b9b;--text-primary-color:#fff;--primary-color:#03a9f4;--card-background-color:#1c1c1c;--divider-color:rgba(225,225,225,.12);",
  none:     "",
};
const RATIO_FN = () => {
  const hex = (h) => { const n = parseInt(h.slice(1), 16); return [(n>>16)&255,(n>>8)&255,n&255]; };
  const parse = (s) => { if (!s || s === "transparent" || s === "none") return null;
    const m = s.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?/);
    if (m) return { rgb: [+m[1],+m[2],+m[3]], a: m[4] === undefined ? 1 : +m[4] };
    if (s.startsWith("#")) { const r = hex(s.length===4?`#${s[1]}${s[1]}${s[2]}${s[2]}${s[3]}${s[3]}`:s); return { rgb: r, a: 1 }; }
    return null; };
  const lum = (c) => { const f=(v)=>{v/=255;return v<=0.03928?v/12.92:((v+0.055)/1.055)**2.4;}; return 0.2126*f(c[0])+0.7152*f(c[1])+0.0722*f(c[2]); };
  const ratio = (a,b) => { const la=lum(a),lb=lum(b); return (Math.max(la,lb)+0.05)/(Math.min(la,lb)+0.05); };
  const over = (fg,bg,a) => fg.map((v,i)=>Math.round(a*v+(1-a)*bg[i]));
  window.__contrast = { parse, ratio, over, lum };
};
const COLLECT = () => {
  const { parse, ratio, over } = window.__contrast;
  const root = window.__card.shadowRoot;
  const out = [];
  const bgOf = (el) => {
    for (let n = el; n; n = n.parentElement || (n.getRootNode && n.getRootNode().host) || null) {
      const bg = parse(getComputedStyle(n).backgroundColor);
      if (bg && bg.a > 0.99) return bg.rgb;
    }
    return [255,255,255];
  };
  const walk = (node) => {
    for (const el of node.querySelectorAll("*")) {
      const txt = [...el.childNodes].filter((n) => n.nodeType === 3 && n.textContent.trim()).map((n) => n.textContent.trim()).join(" ");
      if (!txt) continue;
      const cs = getComputedStyle(el);
      if (cs.display === "none" || cs.visibility === "hidden" || +cs.opacity === 0) continue;
      if (el.getClientRects().length === 0) continue;   // SVG <title>/<desc> and other non-rendered nodes
      const isSvg = el.namespaceURI && el.namespaceURI.includes("svg");
      const colRaw = isSvg ? (cs.fill || el.getAttribute("fill")) : cs.color;
      const c = parse(colRaw);
      if (!c) continue;
      const bg = bgOf(el);
      const fg = c.a < 1 ? over(c.rgb, bg, c.a) : c.rgb;
      const r = ratio(fg, bg);
      const fs = parseFloat(cs.fontSize) || 12;
      const bold = (parseInt(cs.fontWeight) || 400) >= 700;
      const large = fs >= 24 || (fs >= 18.66 && bold);
      out.push({ tag: el.tagName, cls: String(el.getAttribute("class") || "").slice(0, 30), r: +r.toFixed(2), fs: +fs.toFixed(1), need: large ? 3 : 4.5, s: txt.slice(0, 34), fg: fg.join(","), bg: bg.join(",") });
    }
  };
  walk(root);
  return out;
};
const browser = await chromium.launch();
const report = [];
for (const [thName, theme] of Object.entries(THEMES)) {
  for (const [scName, sc] of Object.entries(SCEN)) {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
    await page.goto("about:blank");
    await page.addScriptTag({ path: CARD_SRC });
    await page.evaluate(async ([st, theme, cfg, drive]) => {
      if (!customElements.get("ha-card")) customElements.define("ha-card", class extends HTMLElement { constructor(){super();this.attachShadow({mode:"open"}).innerHTML="<style>:host{background:var(--card-background-color,white);box-sizing:border-box;border-radius:12px;border-width:1px;border-style:solid;border-color:var(--divider-color,#e0e0e0);display:block;position:relative;}</style><slot></slot>";} });
      const style = document.createElement("style");
      style.textContent = `body{margin:0;font-family:-apple-system,"Segoe UI",sans-serif}heatpump-optimizer-card{display:block;width:900px;${theme}}`;
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
    }, [states, theme, sc.cfg, sc.drive]);
    await page.evaluate(RATIO_FN);
    const rows = await page.evaluate(COLLECT);
    const bad = rows.filter((x) => x.r < x.need - 0.05);
    report.push({ thName, scName, total: rows.length, bad });
    await page.close();
  }
}
await browser.close();
for (const r of report) {
  if (r.bad.length) {
    console.log(`=== ${r.thName} ${r.scName}: ${r.bad.length}/${r.total} under AA`);
    const byText = new Map();
    for (const b of r.bad) { const k = `${b.tag}.${b.cls}|${b.s}`; if (!byText.has(k)) byText.set(k, b); }
    for (const b of [...byText.values()].slice(0, 14)) console.log(`    ${b.r}:1 (need ${b.need}, ${b.fs}px) fg=${b.fg} bg=${b.bg} ${b.tag}.${b.cls} "${b.s}"`);
  }
}
console.log("done");
