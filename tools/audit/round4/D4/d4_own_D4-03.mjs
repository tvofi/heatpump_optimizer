// VERIFIER 1 (seat 0-1) round 4 — OWN harness for finding D4-03.
//
// METRIC (mine, independent of the finder's):
//   The bounding boxes of the card's view-zoom controls (.vc-out/.vc-in/
//   .vc-reset), read with getBoundingClientRect under a DEFAULT fine
//   pointer (no CDP media emulation at all — the honest desktop default),
//   at tile widths 359 / 500 / 736, frozen clock so the plan is editable.
//   SC 2.5.8 applied with my OWN geometry: a target is failing when
//   min(w,h) < 24 AND a 24 px-diameter circle centred on its bbox centre
//   intersects ANY other target's bounding box (circle-rect intersection,
//   not the finder's centre-distance-only test) or any other undersized
//   target's circle. Control arm: coarse pointer (CDP + matchMedia stub,
//   both, as the card reads the query in JS too) must lift the pair above
//   24 px, which shows the floor works where it is applied.
//
// RUN (from the repository root):
//   NODE_PATH=/private/tmp/hpo-pw/node_modules \
//   PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers \
//   HPO_PLANDATA=<private plandata.json> \
//     node tools/audit/round4/D4/d4_own_D4-03.mjs
//
// EXPECTED (verifier's own prediction, finder claims 20.22x20.22 at
// 22.22 px centres fine / floor holds coarse): sizes and spacings within
// +-0.1 px; fail counts integer +-0.
import { createRequire } from "node:module";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(__dirname, "../../../..");
const OUT = path.join(__dirname, "out");
mkdirSync(OUT, { recursive: true });
const plan = JSON.parse(readFileSync(process.env.HPO_PLANDATA, "utf8"));
const CARD_SRC = path.join(repo, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js");

const THEME = { "--primary-text-color": "#212121", "--secondary-text-color": "#727272",
  "--primary-color": "#03a9f4", "--card-background-color": "#ffffff",
  "--primary-background-color": "#fafafa", "--secondary-background-color": "#e5e5e5",
  "--divider-color": "rgba(0,0,0,.12)", "--error-color": "#db4437",
  "--text-primary-color": "#ffffff" };
const HA_CARD = `
  if (!customElements.get("ha-card")) {
    customElements.define("ha-card", class extends HTMLElement {
      constructor() { super();
        this.attachShadow({ mode: "open" }).innerHTML =
          "<style>:host{background:var(--card-background-color,white);box-sizing:border-box;" +
          "border-radius:12px;border:1px solid var(--divider-color,#e0e0e0);color:var(--primary-text-color);" +
          "display:block;position:relative}</style><slot></slot>"; }
    });
  }`;

const MOUNT = async (planJson) => {
  const raf = () => new Promise((r) => requestAnimationFrame(() => r()));
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const forecast = planJson.space_plan.forecast;
  const solar = forecast.map((p, i) => ({
    t: p.t, ghi: Math.max(0, 400 * Math.sin((i / forecast.length) * Math.PI)) }));
  const states = {
    "sensor.heat_pump_optimizer_solar_irradiance": { state: "120", attributes: { forecast: solar, plan_kind: "solar" } },
    "sensor.heatpump_optimizer_space_heating_plan": { state: "3", attributes: {
      forecast, slots: planJson.space_plan.slots, total_cost: planJson.space_plan.total_cost,
      active_now: planJson.space_plan.active_now, plan_kind: "space" } },
  };
  // entity ids must match what the card looks for; reuse the finder's ids
  delete states["sensor.heatpump_optimizer_space_heating_plan"];
  states["sensor.heat_pump_optimizer_space_heating_plan"] = { state: "3 slots planned", attributes: {
    forecast, slots: planJson.space_plan.slots,
    total_energy_kwh: planJson.space_plan.total_energy_kwh,
    total_cost: planJson.space_plan.total_cost,
    active_now: planJson.space_plan.active_now, plan_kind: "space" } };
  states["sensor.heat_pump_optimizer_dhw_heating_plan"] = { state: "4 slots planned", attributes: {
    forecast: planJson.dhw_plan.forecast, slots: planJson.dhw_plan.slots,
    total_energy_kwh: planJson.dhw_plan.total_energy_kwh,
    total_cost: planJson.dhw_plan.total_cost,
    active_now: planJson.dhw_plan.active_now, plan_kind: "dhw" } };
  document.body.innerHTML = "";
  const host = document.createElement("div");
  host.id = "hpo-host"; host.style.width = "100%";
  document.body.appendChild(host);
  const card = document.createElement("heatpump-optimizer-card");
  card.style.display = "block";
  card.setConfig({ type: "custom:heatpump-optimizer-card" });
  card.hass = { states };
  host.appendChild(card);
  await raf(); card.hass = { states }; await raf(); await sleep(60);
  window.__card = card;
  return true;
};

const VPS = [{ n: "375x812", w: 375, h: 812, tile: 359 },
             { n: "768x1024", w: 768, h: 1024, tile: 736 },
             { n: "1280x800", w: 1280, h: 800, tile: 500 }];

const rows = [];
const browser = await chromium.launch();
try {
  for (const arm of [{ n: "fine-default", emulate: false, coarse: false },
                     { n: "coarse", emulate: true, coarse: true }]) {
    for (const vp of VPS) {
      const ctx = await browser.newContext({ viewport: { width: vp.w, height: vp.h }, deviceScaleFactor: 1 });
      const page = await ctx.newPage();
      if (arm.emulate) {
        const cdp = await ctx.newCDPSession(page);
        await cdp.send("Emulation.setEmulatedMedia", {
          features: [{ name: "pointer", value: "coarse" }, { name: "any-pointer", value: "coarse" }] });
      }
      await page.goto("about:blank");
      const frozen = Date.parse(plan.dhw_plan.forecast[0].t) + 6 * 3600 * 1000;
      await page.addInitScript((f) => {
        const Real = Date;
        class Frozen extends Real {
          constructor(...a) { super(...(a.length ? a : [f])); }
          static now() { return f; }
        }
        window.Date = Frozen;
      }, frozen);
      await page.reload();
      await page.addStyleTag({ content:
        `:root{${Object.entries(THEME).map(([k, v]) => `${k}:${v}`).join(";")}}` +
        `html,body{margin:0;background:#fafafa;font-family:Roboto,-apple-system,sans-serif;font-size:14px}` +
        `#hpo-host{width:${vp.tile}px;margin:0 auto}heatpump-optimizer-card{display:block}` });
      await page.addScriptTag({ content: HA_CARD });
      await page.addScriptTag({ path: CARD_SRC });
      await page.evaluate(MOUNT, plan);
      if (arm.emulate) {
        await page.evaluate(() => {
          const orig = window.matchMedia.bind(window);
          window.matchMedia = (q) => q === "(pointer: coarse)"
            ? { matches: true, media: q, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {} }
            : orig(q);
        });
        // the style block is built per render; re-render so _coarsePointer() sees the stub
        await page.evaluate(() => { window.__card._render && window.__card._render(); });
        await page.waitForTimeout(60);
      }
      const data = await page.evaluate(() => {
        const root = window.__card.shadowRoot;
        const HIT = ["button", "a[href]", "input", "select", "textarea", "summary",
          "[role='button']", "[tabindex]", ".chip", ".slot-hit", ".lane-hit", ".setup-hit"].join(",");
        const out = [];
        const seen = new Set();
        const walk = (n) => {
          for (const el of n.querySelectorAll("*")) {
            let m = false; try { m = el.matches(HIT); } catch (e) {}
            if (m && !seen.has(el) && !el.disabled) {
              seen.add(el);
              const st = getComputedStyle(el);
              if (st.display !== "none" && st.visibility !== "hidden") {
                const b = el.getBoundingClientRect();
                if (b.width > 0.01 && b.height > 0.01) {
                  out.push({ sel: el.tagName.toLowerCase() + "." + (el.getAttribute("class") || "").trim().split(/\s+/)[0],
                    cx: b.left + b.width / 2, cy: b.top + b.height / 2,
                    x: b.left, y: b.top, w: b.width, h: b.height });
                }
              }
            }
            if (el.shadowRoot) walk(el.shadowRoot);
          }
        };
        walk(root);
        return out;
      });
      // my own SC 2.5.8: circle-rect intersection against EVERY other target
      const R = 12;
      const circleHitsRect = (cx, cy, rx0, ry0, rx1, ry1) => {
        const nx = Math.max(rx0, Math.min(cx, rx1));
        const ny = Math.max(ry0, Math.min(cy, ry1));
        return Math.hypot(cx - nx, cy - ny) < R;
      };
      const zoom = data.filter((t) => /^button\.vc-(in|out|reset)$/.test(t.sel));
      const failing = [];
      for (const t of data) {
        const min = Math.min(t.w, t.h);
        if (min >= 24 - 0.05) continue;
        let hit = null;
        for (const o of data) {
          if (o === t) continue;
          if (circleHitsRect(t.cx, t.cy, o.x, o.y, o.x + o.w, o.y + o.h)) { hit = o.sel; break; }
          const oMin = Math.min(o.w, o.h);
          if (oMin < 24 - 0.05 && Math.hypot(o.cx - t.cx, o.cy - t.cy) < 2 * R) { hit = o.sel + " (circle)"; break; }
        }
        if (hit) failing.push({ sel: t.sel, w: Math.round(t.w * 100) / 100, h: Math.round(t.h * 100) / 100, hitBy: hit });
      }
      rows.push({ arm: arm.n, vp: vp.n, zoom, failingCount: failing.length,
                  failingZoom: failing.filter((f) => /^button\.vc-/.test(f.sel)),
                  failingSample: failing.slice(0, 5) });
      await ctx.close();
    }
  }
} finally { await browser.close(); }

writeFileSync(path.join(OUT, "d4_own_D4-03.json"), JSON.stringify(rows, null, 1));
for (const r of rows) {
  const vcOut = r.zoom.find((t) => t.sel === "button.vc-out");
  const vcIn = r.zoom.find((t) => t.sel === "button.vc-in");
  const d = vcOut && vcIn ? Math.hypot(vcOut.cx - vcIn.cx, vcOut.cy - vcIn.cy) : null;
  console.log(`RESULT ${r.arm}|${r.vp} vc_out=${vcOut ? vcOut.w.toFixed(2) + "x" + vcOut.h.toFixed(2) : "absent"} vc_in=${vcIn ? vcIn.w.toFixed(2) + "x" + vcIn.h.toFixed(2) : "absent"} centre_dist=${d != null ? d.toFixed(2) : "na"} px`);
  console.log(`RESULT ${r.arm}|${r.vp} failing_2_5_8_all_targets=${r.failingCount} failing_zoom=${r.failingZoom.length}`);
}
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log("RESULT thread_factor=1.00 (no CPU-time metric)");
console.log("RESULT swapins=0 (not a memory metric)");
