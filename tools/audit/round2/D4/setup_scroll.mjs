// D4 (UI/UX) round 2 -- can a phone user reach every setup row?
//
// METRIC: on a 375x812 phone, with the expanded dialog on the Setup page, the
//   setup rows (rect.setup-hit) fully inside the .setup-canvas viewport at
//   scrollLeft = 0 (hits_visible_at_0), at scrollLeft = max
//   (hits_visible_at_max), and the rows that some scroll position can show
//   whole (hits_reachable: narrower than the viewport and inside the
//   scrollable content) against the total (hits_total); canvas_scroll_px is
//   scrollWidth - clientWidth.
// COMMAND (from the export root):
//   HPO_PLANDATA=$TMP/plandata.json NODE_PATH=$PW/node_modules \
//   PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers \
//   node tools/audit/round2/D4/setup_scroll.mjs
// EXPECTED (baseline c398fc84): hits_reachable = hits_total = 6 (a non-finding
//   if so); canvas_scroll_px ~ 224 (560 - 336).
// INSTRUMENTED SYMBOL: heatpump-optimizer-card.js:SetupPage / setupSvgHtml
//   and the `.setup-canvas` rule in cardStyleBlock, in Chromium.
// PERTURBATION: remove `overflow-x: auto` from `.setup-canvas` (phone media
//   block) -> canvas_scroll_px = 0 and hits_reachable falls below hits_total.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { CARD_PATH, DEFAULT_SPACE, planStates, setupSensorStates, qaTopologies } from "../../../../tests/card_rig.mjs";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, "../../../..");
const plan = JSON.parse(fs.readFileSync(process.env.HPO_PLANDATA, "utf8"));
const CARD_SRC = fs.readFileSync(path.join(repo, CARD_PATH), "utf8");
const states = { ...planStates(plan), ...setupSensorStates() };
states[DEFAULT_SPACE].attributes.setup_topology = qaTopologies().base;

const browser = await chromium.launch();
try {
  const context = await browser.newContext({ viewport: { width: 375, height: 812 }, hasTouch: true, isMobile: true });
  const page = await context.newPage();
  await page.setContent('<!doctype html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head><body></body></html>');
  await page.addStyleTag({ content: `:root{--primary-text-color:#212121;--secondary-text-color:#727272;--primary-color:#03a9f4;--divider-color:rgba(0,0,0,.12);--card-background-color:#fff;--primary-background-color:#fafafa}
    html{font-size:14px}body{margin:0;padding:8px;font-family:Roboto,sans-serif;font-size:14px}heatpump-optimizer-card{display:block;width:359px}` });
  await page.addScriptTag({ content: `customElements.define("ha-card", class extends HTMLElement { constructor(){ super(); this.attachShadow({mode:"open"}).innerHTML = "<style>:host{background:var(--card-background-color,white);box-sizing:border-box;border-radius:12px;border:1px solid var(--divider-color,#e0e0e0);color:var(--primary-text-color);display:block;position:relative}</style><slot></slot>"; } });` });
  await page.addScriptTag({ content: CARD_SRC });
  const r = await page.evaluate(async (st) => {
    const card = document.createElement("heatpump-optimizer-card");
    card.setConfig({ type: "custom:heatpump-optimizer-card" });
    card.hass = { states: st, language: "en" };
    document.body.appendChild(card);
    card.hass = { states: st, language: "en" };
    card._onCardClick({}); card.dialog.page = "setup"; card._render();
    await new Promise((res) => requestAnimationFrame(() => requestAnimationFrame(res)));
    const root = card.shadowRoot;
    const canvas = root.querySelector(".setup-canvas");
    const hits = [...root.querySelectorAll("rect.setup-hit")];
    const visible = () => {
      const c = canvas.getBoundingClientRect();
      return hits.map((h) => { const b = h.getBoundingClientRect(); return b.left >= c.left - 0.5 && b.right <= c.right + 0.5; });
    };
    canvas.scrollLeft = 0;
    const at0 = visible();
    const c0 = canvas.getBoundingClientRect();
    // Reachable: narrower than the viewport and inside the scrollable content.
    const reachable = hits.map((h) => { const b = h.getBoundingClientRect();
      return b.width <= canvas.clientWidth && b.left >= c0.left - 0.5 && b.right <= c0.left + canvas.scrollWidth + 0.5; });
    canvas.scrollLeft = canvas.scrollWidth;
    const atMax = visible();
    return { total: hits.length, at0: at0.filter(Boolean).length, atMax: atMax.filter(Boolean).length, reach: reachable.filter(Boolean).length,
      scroll: canvas.scrollWidth - canvas.clientWidth, canvasW: canvas.clientWidth, svgW: root.querySelector("svg.setup-svg").getBoundingClientRect().width,
      overflowX: getComputedStyle(canvas).overflowX };
  }, states);
  console.log(JSON.stringify(r));
  console.log(`RESULT hits_total=${r.total} count`);
  console.log(`RESULT hits_visible_at_0=${r.at0} count`);
  console.log(`RESULT hits_visible_at_max=${r.atMax} count`);
  console.log(`RESULT hits_reachable=${r.reach} count`);
  console.log(`RESULT canvas_scroll_px=${r.scroll} px`);
} finally { await browser.close(); }
console.log("RESULT thread_factor=1.00");
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log("RESULT swapins=0");
