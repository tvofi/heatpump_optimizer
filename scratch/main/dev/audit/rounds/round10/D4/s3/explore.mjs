// D4-s3 exploration probe (non-findings only): per-state rendered font sizes, font families, legend dot vs series paint, light and dark. Run: VW=1280 HPO_PLANDATA=... NODE_PATH=... node dev/audit/rounds/round10/D4/s3/explore.mjs
import { createRequire } from "node:module"; import { readFileSync } from "node:fs";
import { planStates, setupSensorStates, qaTopologies, DEFAULT_SPACE, DEFAULT_DHW, HOUR } from "../../../../../../tests/card_rig.mjs";
const require = createRequire(import.meta.url); const { chromium } = require("playwright");
const plan = JSON.parse(readFileSync(process.env.HPO_PLANDATA, "utf8"));
const SRC = readFileSync("custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js", "utf8");
const THEMES = {
  light: `--primary-color:#03a9f4;--primary-text-color:#212121;--secondary-text-color:#727272;--text-primary-color:#ffffff;--primary-background-color:#fafafa;--secondary-background-color:#e5e5e5;--card-background-color:#ffffff;--divider-color:rgba(0,0,0,.12);--error-color:#db4437;--warning-color:#ffa600;--success-color:#43a047;`,
  dark: `--primary-color:#03a9f4;--primary-text-color:#e1e1e1;--secondary-text-color:#9b9b9b;--text-primary-color:#ffffff;--primary-background-color:#111111;--secondary-background-color:#282828;--card-background-color:#1c1c1c;--divider-color:rgba(225,225,225,.12);--error-color:#db4437;--warning-color:#ffa600;--success-color:#43a047;`};
const setupSt = () => { const st = { ...planStates(plan), ...setupSensorStates() }; st[DEFAULT_SPACE].attributes.setup_topology = qaTopologies().base; return st; };
const STATES = [
  ["tile", planStates(plan), []], ["expanded", planStates(plan), [["cardClick"]]],
  ["no_plan", {}, []], ["setup", setupSt(), [["cardClick"], ["page", "setup"]]],
];
const b = await chromium.launch({ executablePath: process.env.HPO_CHROMIUM || undefined });
for (const theme of ["light", "dark"]) for (const [name, st, steps] of STATES) {
  const ctx = await b.newContext({ viewport: { width: +process.env.VW||1280, height: 800 }, reducedMotion: "reduce" });
  await ctx.clock.setFixedTime(Date.parse(plan.dhw_plan.forecast[0].t) + 6 * HOUR);
  const page = await ctx.newPage(); await page.goto("about:blank"); await page.addScriptTag({ content: SRC });
  const r = await page.evaluate(async ([css, st, steps, dark]) => {
    const s = document.createElement("style"); s.textContent = `html{${css}} body{margin:0;padding:8px;font-family:Arial;background:var(--primary-background-color)}`; document.head.appendChild(s);
    customElements.define("ha-card", class extends HTMLElement { constructor() { super(); this.attachShadow({ mode: "open" }).innerHTML = "<style>:host{display:block;background:var(--card-background-color)}</style><slot></slot>"; } });
    const c = document.createElement("heatpump-optimizer-card"); c.setConfig({ type: "custom:heatpump-optimizer-card" });
    c.hass = { states: st, language: "en", themes: { darkMode: dark } }; document.body.appendChild(c);
    await new Promise((r) => setTimeout(r, 80));
    for (const [op, a] of steps) { if (op === "cardClick") c._onCardClick({}); if (op === "page") { c.dialog.page = a; c._render(); } await new Promise((r) => setTimeout(r, 80)); }
    const root = c.shadowRoot; const d = root.querySelector("dialog[open]"); const sc = d || root;
    const sizes = {}, fams = {};
    for (const el of sc.querySelectorAll("*")) {
      if (!el.getClientRects().length) continue;
      const own = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim()); if (!own) continue;
      const cs = getComputedStyle(el); const k = (el instanceof SVGElement ? (parseFloat(cs.fontSize)*el.getScreenCTM().a).toFixed(1)+"px" : cs.fontSize) + (el instanceof SVGElement ? " svg" : "");
      (sizes[k] = sizes[k] || []).push((el.getAttribute("class") || el.tagName).split(" ")[0]);
      fams[cs.fontFamily] = (fams[cs.fontFamily] || 0) + 1;
    }
    const chips = [...sc.querySelectorAll(".legend .chip, .legend button")].map((ch) => { const k = ch.dataset.key; const dot = ch.querySelector(".dot");
      const ser = sc.querySelector(`.series[data-key='${k}']`); const scs = ser && getComputedStyle(ser);
      return [k, dot && getComputedStyle(dot).backgroundColor, dot && getComputedStyle(dot).backgroundImage.slice(0,40), scs && (scs.stroke !== "none" ? scs.stroke : scs.fill)]; });
    return { sizes: Object.fromEntries(Object.entries(sizes).map(([k, v]) => [k, [...new Set(v)].slice(0, 8).join(",") + " n=" + v.length])), fams, chips };
  }, [THEMES[theme]+`} heatpump-optimizer-card{display:block;width:${(+process.env.VW||1280)-16}px`, st, steps, theme === "dark"]);
  await page.screenshot({path:`${process.env.TMPDIR}/d4s3-${name}-${theme}-${process.env.VW}.png`, fullPage:true}); console.log(theme, name, JSON.stringify(r, null, 0)); await ctx.close();
}
await b.close();
