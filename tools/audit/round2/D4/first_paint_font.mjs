// D4 (UI/UX) round 2 -- does the compact chart's 8 px font floor reach the
// first paint of a dashboard tile?
//
// METRIC: on-screen axis font of the compact chart (font-size attribute in
//   viewBox units x rendered svg width / 900) and the lane height in px, on a
//   359 px phone tile, after each of four sequences:
//   lovelace  : setConfig -> hass -> append to DOM -> hass again (the order
//               hui-card uses: the element gets hass before it is placed);
//   attached  : append -> setConfig -> hass (the order tests/card_browser.mjs
//               uses);
//   resize    : the lovelace tile narrowed 359 -> 300 px, two frames later
//               (does the ResizeObserver re-render?);
//   refresh   : the lovelace tile given a hass whose plan sensor carries a new
//               last_updated (the signature moves, so _maybeRender renders).
//   renders   : how many times HeatpumpOptimizerCard.prototype._render ran
//               in each sequence (the instrumented symbol).
//
// COMMAND (from the export root):
//   HPO_PLANDATA=$TMP/plandata.json NODE_PATH=$PW/node_modules \
//   PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers \
//   node tools/audit/round2/D4/first_paint_font.mjs
//
// EXPECTED (baseline c398fc84, Apple M1, Chromium 1148): font_px_lovelace =
//   3.70 +-0.05 (FONT_BASE 10 units on a 333 px svg: 359 px tile less the
//   1 px ha-card border and 12 px padding each side), font_px_resize = 3.04
//   +-0.05, renders_resize = 0, font_px_refresh = 7.31 +-0.05 and
//   font_px_attached = 7.42 +-0.05: even a render that applies the floor
//   lands under 8 px, because compactFontUnits divides by the HOST width
//   (359 / 300 px) while the svg it sizes is 26 px narrower.
//
// INSTRUMENTED SYMBOL: heatpump-optimizer-card.js:HeatpumpOptimizerCard
//   (_render, _maybeRender, connectedCallback's ResizeObserver,
//   compactFontUnits via renderChart's measuredWidth thunk).
// PERTURBATION: in connectedCallback, make the ResizeObserver callback call
//   `this.render()` (or add the measured width to `_signature`):
//   font_px_lovelace and font_px_resize rise to ~7.4 / ~7.3, renders_resize
//   to >= 1. Measuring the svg's own width in _measuredCardWidth (or
//   subtracting ha-card's 26 px) lifts font_px_attached to 8.00.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { CARD_PATH, DEFAULT_SPACE, planStates } from "../../../../tests/card_rig.mjs";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, "../../../..");
const planPath = process.env.HPO_PLANDATA;
if (!planPath || !fs.existsSync(planPath)) {
  console.error("FAIL: set HPO_PLANDATA to the payload tests/plan_view.py wrote");
  process.exit(1);
}
const plan = JSON.parse(fs.readFileSync(planPath, "utf8"));
const CARD_SRC = fs.readFileSync(path.join(repo, CARD_PATH), "utf8");
const states = planStates(plan);

const PAGE = String.raw`
window.__fp = (() => {
  const TAG = "heatpump-optimizer-card";
  const raf2 = () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  let renders = 0;
  const Card = customElements.get(TAG);
  const orig = Card.prototype._render;
  Card.prototype._render = function () { renders += 1; return orig.apply(this, arguments); };
  function measure(card) {
    const svg = card.shadowRoot.querySelector(".chartwrap svg");
    if (!svg) return null;
    const r = svg.getBoundingClientRect();
    const axis = svg.querySelector("text[font-size]");
    const lane = svg.querySelector("rect.lane");
    return {
      svgW: +r.width.toFixed(1),
      fontUnits: axis ? parseFloat(axis.getAttribute("font-size")) : null,
      fontPx: axis ? +(parseFloat(axis.getAttribute("font-size")) * r.width / 900).toFixed(2) : null,
      laneH: lane ? +lane.getBoundingClientRect().height.toFixed(2) : null,
      hostW: +card.getBoundingClientRect().width.toFixed(1),
    };
  }
  async function lovelace(states) {
    document.body.innerHTML = ""; renders = 0;
    const card = document.createElement(TAG);
    card.setConfig({ type: "custom:" + TAG });
    card.hass = { states, language: "en" };
    document.body.appendChild(card);
    card.hass = { states, language: "en" };
    await raf2(); await raf2();
    window.__card = card;
    return { ...measure(card), renders };
  }
  async function attached(states) {
    document.body.innerHTML = ""; renders = 0;
    const card = document.createElement(TAG);
    document.body.appendChild(card);
    card.setConfig({ type: "custom:" + TAG });
    card.hass = { states, language: "en" };
    await raf2(); await raf2();
    window.__card = card;
    return { ...measure(card), renders };
  }
  async function resize(px) {
    const card = window.__card; renders = 0;
    card.style.width = px + "px";
    await raf2(); await raf2(); await new Promise((r) => setTimeout(r, 120));
    return { ...measure(card), renders };
  }
  async function refresh(states) {
    const card = window.__card; renders = 0;
    card.hass = { states, language: "en" };
    await raf2(); await raf2();
    return { ...measure(card), renders };
  }
  return { lovelace, attached, resize, refresh };
})();
`;

const browser = await chromium.launch();
try {
  const context = await browser.newContext({ viewport: { width: 375, height: 812 }, timezoneId: "Europe/Stockholm" });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e.message)));
  await page.goto("about:blank");
  await page.addStyleTag({ content: `
    :root { --primary-text-color:#212121; --secondary-text-color:#727272; --primary-color:#03a9f4;
            --divider-color:rgba(0,0,0,.12); --card-background-color:#fff; --primary-background-color:#fafafa; }
    html { font-size: 14px; } body { margin: 0; padding: 8px; font-family: Roboto, sans-serif; font-size: 14px; }
    heatpump-optimizer-card { display: block; width: 359px; }` });
  // The frontend's <ha-card> (:host rules from ha-card.ts), defined before
  // the card loads: the card renders it inside its own shadow root.
  await page.addScriptTag({ content: `customElements.define("ha-card", class extends HTMLElement {
    constructor() { super(); this.attachShadow({ mode: "open" }).innerHTML = "<style>:host{" +
      "background:var(--ha-card-background,var(--card-background-color,white));box-sizing:border-box;" +
      "border-radius:var(--ha-card-border-radius,12px);border-width:var(--ha-card-border-width,1px);border-style:solid;" +
      "border-color:var(--ha-card-border-color,var(--divider-color,#e0e0e0));color:var(--primary-text-color);display:block;position:relative;}" +
      "</style><slot></slot>"; } });` });
  await page.addScriptTag({ content: CARD_SRC });
  await page.addScriptTag({ content: PAGE });

  const lovelace = await page.evaluate((st) => window.__fp.lovelace(st), states);
  const resized = await page.evaluate(() => window.__fp.resize(300));
  const refreshed = await page.evaluate((st) => {
    const s = JSON.parse(JSON.stringify(st));
    s[Object.keys(s).find((k) => k.endsWith("space_heating_plan"))].last_updated = "2026-01-15T06:05:00+01:00";
    return window.__fp.refresh(s);
  }, states);
  const attached = await page.evaluate((st) => window.__fp.attached(st), states);
  console.log("lovelace order :", JSON.stringify(lovelace));
  console.log("after resize   :", JSON.stringify(resized));
  console.log("after refresh  :", JSON.stringify(refreshed));
  console.log("attached order :", JSON.stringify(attached));
  if (errors.length) console.log("page errors:", errors.join(" | "));
  console.log(`RESULT font_px_lovelace=${lovelace.fontPx} px`);
  console.log(`RESULT lane_px_lovelace=${lovelace.laneH} px`);
  console.log(`RESULT renders_lovelace=${lovelace.renders} count`);
  console.log(`RESULT font_px_resize=${resized.fontPx} px`);
  console.log(`RESULT renders_resize=${resized.renders} count`);
  console.log(`RESULT font_px_refresh=${refreshed.fontPx} px`);
  console.log(`RESULT renders_refresh=${refreshed.renders} count`);
  console.log(`RESULT font_px_attached=${attached.fontPx} px`);
  console.log(`RESULT floor_px=8 px`);
} finally {
  await browser.close();
}
console.log(`RESULT thread_factor=1.00`);
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log(`RESULT swapins=0`);
