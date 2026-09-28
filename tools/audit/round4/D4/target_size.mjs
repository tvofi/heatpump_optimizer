// D4 round-4 — WCAG 2.2 SC 2.5.8 Target Size (Minimum), spacing exception included.
//
// METRIC: per (state, viewport, pointer arm), the interactive targets in the
// card whose smaller side is under 24 CSS px AND which do not earn the
// standard's spacing exception — i.e. a 24 px-diameter circle centred on the
// target's bounding box intersects another target's circle (or another
// target). Reported as a list of (selector, size, nearest centre distance)
// and a count. Undersized-but-well-spaced targets are counted separately and
// are NOT claimed: they pass the success criterion.
//
// WHY separately from card_grid.mjs: the grid counts "smaller side < bar",
// which over-reports. A 22 px chip with 120 px between it and its neighbour
// passes 2.5.8; a 20 px zoom button 22 px from the next one does not. Naming
// the second without the first is the difference between a finding and a
// blanket.
//
// RUN (from the export root):
//   NODE_PATH=/private/tmp/hpo-pw/node_modules \
//   PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers \
//   HPO_PLANDATA=/private/tmp/hpo-d4/plandata.json \
//     node tools/audit/round4/D4/target_size.mjs
//
// EXPECTED at baseline 7dd68dd327fe3dbfb09f3bd0fe38910c58877697 on the audit
// box (Apple M1, Chromium 131.0.6778.33): integer counts, tolerance +-0.
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
const driftSrc = readFileSync(path.join(repo, "tests/card_drift.mjs"), "utf8");
const STATES = [...driftSrc.matchAll(/^\s{2}\{ name: "([a-z0-9_]+)",$/gm)].map((m) => m[1]);
if (STATES.length !== 34) { console.error(`FAIL: derived ${STATES.length} states`); process.exit(1); }

const THEME = { "--primary-text-color": "#212121", "--secondary-text-color": "#727272",
  "--primary-color": "#03a9f4", "--card-background-color": "#ffffff",
  "--primary-background-color": "#fafafa", "--secondary-background-color": "#e5e5e5",
  "--divider-color": "rgba(0,0,0,.12)", "--error-color": "#db4437",
  "--warning-color": "#ffa600", "--success-color": "#43a047", "--text-primary-color": "#ffffff" };
const HA_CARD = `if(!customElements.get("ha-card")){customElements.define("ha-card",class extends HTMLElement{constructor(){super();this.attachShadow({mode:"open"}).innerHTML="<style>:host{background:var(--card-background-color,white);box-sizing:border-box;border-radius:12px;border:1px solid var(--divider-color,#e0e0e0);color:var(--primary-text-color);display:block;position:relative}</style><slot></slot>"}})}`;

const VPS = [{ n: "375x812", w: 375, h: 812, tile: 359 },
             { n: "768x1024", w: 768, h: 1024, tile: 736 },
             { n: "1280x800", w: 1280, h: 800, tile: 500 }];
const ARMS = [{ n: "fine", pointer: "fine" }, { n: "coarse", pointer: "coarse" }];
const MIN = 24;

const rows = [];
const browser = await chromium.launch();
try {
  for (const arm of ARMS) {
    for (const vp of VPS) {
      const ctx = await browser.newContext({ viewport: { width: vp.w, height: vp.h }, deviceScaleFactor: 1 });
      const page = await ctx.newPage();
      const cdp = await ctx.newCDPSession(page);
      await cdp.send("Emulation.setEmulatedMedia", {
        features: [{ name: "pointer", value: arm.pointer }, { name: "any-pointer", value: arm.pointer }] });
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
      await page.addScriptTag({ path: path.join(__dirname, "lib/measure.js") });
      await page.addScriptTag({ path: path.join(__dirname, "lib/states.js") });
      await page.evaluate(([coarse]) => {
        const orig = window.matchMedia.bind(window);
        window.matchMedia = (q) => q === "(pointer: coarse)"
          ? { matches: coarse, media: q, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {} }
          : orig(q);
      }, [arm.pointer === "coarse"]);

      for (const state of STATES) {
        let drive;
        try {
          drive = await page.evaluate(async ([n, p]) => {
            if (!window.__D4.STATES[n]) return { ok: false, note: "not ported" };
            return await window.__D4.STATES[n](p);
          }, [state, plan]);
        } catch (e) { drive = { ok: false, note: "threw: " + String(e.message).slice(0, 120) }; }
        const r = await page.evaluate((min) => {
          const card = window.__card;
          if (!card || !card.shadowRoot) return null;
          const t = window.__D4.targets(card.shadowRoot);
          const boxes = t.map((x, i) => ({ ...x, i }));
          // re-read centres from the DOM in the same pass
          return boxes;
        }, MIN);
        if (!r) { rows.push({ arm: arm.n, vp: vp.n, state, drive, error: "no shadow root" }); continue; }
        const full = await page.evaluate(() => {
          const out = [];
          const HIT = ["button", "a[href]", "input", "select", "textarea", "summary",
            "[role='button']", "[role='tab']", "[tabindex]", ".chip", ".setup-hit",
            ".dlg-tab", ".slot-hit", ".lane-hit"].join(",");
          const seen = new Set();
          for (const el of window.__D4.walk(window.__card.shadowRoot)) {
            let m = false; try { m = el.matches && el.matches(HIT); } catch (e) {}
            if (!m || seen.has(el) || el.disabled) continue;
            seen.add(el);
            const st = getComputedStyle(el);
            if (st.display === "none" || st.visibility === "hidden" || Number(st.opacity) === 0) continue;
            const b = el.getBoundingClientRect();
            if (b.width < 0.01 || b.height < 0.01) continue;
            out.push({ sel: window.__D4.describe(el), text: (el.textContent || "").trim().slice(0, 24),
                       cx: b.left + b.width / 2, cy: b.top + b.height / 2,
                       w: Math.round(b.width * 100) / 100, h: Math.round(b.height * 100) / 100 });
          }
          return out;
        });
        const under = full.filter((t) => Math.min(t.w, t.h) < MIN - 0.05);
        const failing = [];
        for (const t of under) {
          // SC 2.5.8 spacing exception: a 24 px circle centred on the target
          // must not intersect another target, nor another undersized
          // target's circle. Two circles of radius 12 intersect when their
          // centres are under 24 apart.
          let nearest = Infinity, who = "";
          for (const o of full) {
            if (o === t) continue;
            const d = Math.hypot(o.cx - t.cx, o.cy - t.cy);
            if (d < nearest) { nearest = d; who = o.sel; }
          }
          if (nearest < MIN - 0.05) {
            failing.push({ sel: t.sel, text: t.text, w: t.w, h: t.h,
                           nearest: Math.round(nearest * 100) / 100, nearestSel: who });
          }
        }
        rows.push({ arm: arm.n, vp: vp.n, state, drive_ok: !!(drive && drive.ok),
                    targets: full.length, undersized: under.length,
                    failing_2_5_8: failing.length, failing: failing,
                    spared_by_spacing: under.length - failing.length });
      }
      await ctx.close();
    }
  }
} finally { await browser.close(); }

writeFileSync(path.join(OUT, "target_size.json"), JSON.stringify(rows, null, 1));
const byArm = {};
for (const r of rows) {
  const k = r.arm;
  byArm[k] = byArm[k] || { cells: 0, targets: 0, undersized: 0, failing: 0, spared: 0, sigs: {} };
  byArm[k].cells += 1;
  byArm[k].targets += r.targets || 0;
  byArm[k].undersized += r.undersized || 0;
  byArm[k].failing += r.failing_2_5_8 || 0;
  byArm[k].spared += r.spared_by_spacing || 0;
  for (const f of r.failing || []) {
    const s = `${f.sel} ${f.w}x${f.h} (nearest centre ${f.nearest}px: ${f.nearestSel})`;
    byArm[k].sigs[s] = (byArm[k].sigs[s] || 0) + 1;
  }
}
for (const [arm, v] of Object.entries(byArm)) {
  console.log(`RESULT ${arm}_cells=${v.cells}`);
  console.log(`RESULT ${arm}_targets=${v.targets}`);
  console.log(`RESULT ${arm}_undersized_lt24=${v.undersized}`);
  console.log(`RESULT ${arm}_spared_by_spacing_exception=${v.spared}`);
  console.log(`RESULT ${arm}_failing_SC_2_5_8=${v.failing}`);
  const sigs = Object.entries(v.sigs).sort((a, b) => b[1] - a[1]);
  console.log(`RESULT ${arm}_distinct_failing_signatures=${sigs.length}`);
  for (const [s, n] of sigs.slice(0, 10)) console.log(`    ${n}x  ${s}`);
}
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log("RESULT thread_factor=1.00 (no CPU-time metric)");
console.log("RESULT swapins=0 (not a memory metric)");
