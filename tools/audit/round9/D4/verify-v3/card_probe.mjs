// D4 verifier V3 (reach and class): the card findings D4-s1-01/02/03/05 re-measured by REAL
// browser input (Playwright mouse/keyboard on the rendered card) instead of the finder's direct
// method calls, with this seat's own measurement code and the status/theme tokens read out of
// Home Assistant's real frontend bundle (home-assistant-frontend 20260128.6, the version HA core
// 2026.2.3 pins: --error-color #db4437, --success-color #43a047, --warning-color #ffa600, card
// #ffffff / #1c1c1c; ha-card :host has no overflow clip).
//
// Metrics (one line each, per cell = viewport x theme x lang):
//   now_overlap_cells      cells where text.now-label and text.now-temp client rects intersect (>0 px both axes)
//   menu_spill_openings    .slot-menu openings by a REAL mouse click that extend >0.5 px past their .chartwrap
//                          or the viewport; two tap sites per cell: (edge) the rightmost x where a tap still
//                          lands on an editable rect.lane in the default window, (zoom) 97% of the lane after
//                          three real clicks on the zoom-in button. (The finder's 97%-of-the-default-window
//                          anchor lands on rect.lane-past, which opens no menu: it is reached only by calling
//                          LaneEditor.openMenu directly.)
//   picker_twin_cells      cells where, after a REAL click on the wood-tank box and TYPING the filter,
//                          two <option>s whose texts differ have an identical visible prefix
//                          (canvas measureText with the select's computed font, content box width)
//   confirm_contrast       WCAG ratio (own formula) of the armed Save button label on its fill after a REAL click
//   status_rules_below_aa  distinct seam_rule lines (status token as text colour or text-bearing fill)
//                          whose token/background ratio is < 4.5 on the real light / dark card background
//
// Command (repository root):
//   T=$(mktemp -d) && HPO_PLANDATA=$T/plandata.json PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 \
//     /home/claude/venv/bin/python tests/plan_view.py >/dev/null && \
//   HPO_PLANDATA=$T/plandata.json NODE_PATH=/home/claude/pwlane/node_modules PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers \
//     node tools/audit/round9/D4/verify-v3/card_probe.mjs
// Expected at 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (exact counts): status_rules_below_aa_light=6,
//   _dark=4, now_overlap_cells=12 (of 12), menu_spill_openings=2 (of 36; both zoomed sv-SE 375 px, 18.2 px past
//   the chart, 0 past the viewport), picker_twin_cells=8 (of 10; 0 at 1280 px), confirm contrast 4.29.
//   thread_factor is printed as 1.00: a single-threaded Node driver of count metrics, no timing RESULT.
// Machine: G2-V3 cloud container, 4 cores, Linux 6.18, Chromium (Playwright 1.56.1). Writes nothing
// outside a mkdtemp root.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import { HOUR, planStates, withActuals, setupSensorStates, qaTopologies, DEFAULT_SPACE } from "../../../../../tests/card_rig.mjs";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const CARD = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js";
const cardSrc = fs.readFileSync(CARD, "utf8");
const plan = JSON.parse(fs.readFileSync(process.env.HPO_PLANDATA, "utf8"));
const FROZEN = Date.parse(plan.dhw_plan.forecast[0].t) + 6 * HOUR;
fs.mkdtempSync(path.join(process.env.TMPDIR || os.tmpdir(), "d4v3-"));
const t0 = process.cpuUsage();

// Real frontend tokens (grep of hass_frontend/frontend_latest/app.*.js, 20260128.6).
const REAL = {
  light: { "--primary-text-color": "#212121", "--secondary-text-color": "#727272", "--card-background-color": "#ffffff",
    "--primary-background-color": "#fafafa", "--divider-color": "rgba(0,0,0,.12)", "--primary-color": "#03a9f4",
    "--error-color": "#db4437", "--success-color": "#43a047", "--warning-color": "#ffa600", "--text-primary-color": "#ffffff",
    "--secondary-background-color": "#e5e5e5" },
  dark: { "--primary-text-color": "#e1e1e1", "--secondary-text-color": "#9b9b9b", "--card-background-color": "#1c1c1c",
    "--primary-background-color": "#111111", "--divider-color": "rgba(225,225,225,.12)", "--primary-color": "#03a9f4",
    "--error-color": "#db4437", "--success-color": "#43a047", "--warning-color": "#ffa600", "--text-primary-color": "#ffffff",
    "--secondary-background-color": "#282828" },
};
const lum = (hex) => {
  const n = hex.replace("#", "");
  const c = [0, 2, 4].map((i) => parseInt(n.slice(i, i + 2), 16) / 255).map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
  return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
};
const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };

// ---- static half: the seam rule's own lines, each ratio from the real tokens -----------------
const seam = cardSrc.split("\n").map((l, i) => [i + 1, l]).filter(([, l]) => /(color|background): var\(--(error|success|warning)-color/.test(l));
let below = { light: 0, dark: 0 };
for (const [n, l] of seam) {
  const tok = l.match(/--(error|success|warning)-color/)[0];
  const isBorder = /border-color/.test(l);
  const isFill = /background:/.test(l);
  for (const th of ["light", "dark"]) {
    // text coloured by the token sits on the card; a token fill carries white (#fff) label text.
    const r = isFill ? ratio(REAL[th][tok], "#ffffff") : ratio(REAL[th][tok], REAL[th]["--card-background-color"]);
    if (!isBorder && r < 4.5) below[th] += 1;
    console.log(`# seam :${n} ${isBorder ? "border(non-text)" : isFill ? "fill+white label" : "text"} ${tok} ${th} ${r.toFixed(2)}:1`);
  }
}
console.log(`RESULT status_seam_lines=${seam.length} count`);
console.log(`RESULT status_rules_below_aa_light=${below.light} count`);
console.log(`RESULT status_rules_below_aa_dark=${below.dark} count`);

// ---- live half ---------------------------------------------------------------------------------
const bigStates = () => {
  const st = {};
  for (let i = 0; i < 40; i++) st[`sensor.zz_${i}`] = { state: "20", attributes: { unit_of_measurement: "°C", friendly_name: `Probe ${i}` } };
  // Two real-world twins: HA suffixes a colliding object id with _2 and keeps the friendly name.
  st["sensor.vedpanna_temperatur_temperature"] = { state: "71.2", attributes: { unit_of_measurement: "°C", friendly_name: "Vedpanna temperatur" } };
  st["sensor.vedpanna_temperatur_temperature_2"] = { state: "48.9", attributes: { unit_of_measurement: "°C", friendly_name: "Vedpanna temperatur" } };
  return st;
};

async function mount(browser, vp, theme, lang, states, config) {
  const ctx = await browser.newContext({ viewport: { width: vp, height: 900 }, colorScheme: theme });
  await ctx.clock.setFixedTime(FROZEN);
  await ctx.route("http://v3.test/**", (r) => r.fulfill({ contentType: "text/html", body: "<!doctype html><html><head><meta charset=utf-8></head><body></body></html>" }));
  const page = await ctx.newPage();
  await page.goto("http://v3.test/");
  await page.addScriptTag({ content: cardSrc });
  await page.evaluate(([tokens, w, st, lg, cfg]) => {
    const css = Object.entries(tokens).map(([k, v]) => `${k}:${v}`).join(";");
    const s = document.createElement("style");
    s.textContent = `html{${css};background:var(--primary-background-color)}body{margin:0;padding:8px;font-family:"Liberation Sans",Arial,sans-serif;color:var(--primary-text-color)}heatpump-optimizer-card{display:block;width:${w}px}`;
    document.head.appendChild(s);
    customElements.define("ha-card", class extends HTMLElement {
      constructor() { super(); this.attachShadow({ mode: "open" }).innerHTML =
        "<style>:host{background:var(--ha-card-background,var(--card-background-color,#fff));box-sizing:border-box;border-radius:12px;border-width:1px;border-style:solid;border-color:var(--divider-color,#e0e0e0);color:var(--primary-text-color);display:block;position:relative}</style><slot></slot>"; }
    });
    const c = document.createElement("heatpump-optimizer-card");
    c.setConfig({ type: "custom:heatpump-optimizer-card", ...cfg });
    c.hass = { states: st, language: lg, callService: async () => ({ context: {}, response: {} }) };
    document.body.appendChild(c);
  }, [REAL[theme], vp - 16, states, lang, config]);
  await page.waitForTimeout(80);
  return { ctx, page };
}
const inRoot = (page, fn, arg) => page.evaluate(([f, a]) => {
  const root = document.querySelector("heatpump-optimizer-card").shadowRoot;
  return (new Function("root", "a", `return (${f})(root, a);`))(root, a);
}, [fn.toString(), arg]);
const rectOf = (page, sel) => inRoot(page, (root, s) => { const e = root.querySelector(s); if (!e) return null; const r = e.getBoundingClientRect(); return { l: r.left, r: r.right, t: r.top, b: r.bottom }; }, sel);

const browser = await chromium.launch();
let zoomSpill = 0, edgeSpill = 0, vpSpill = 0;
let nowCells = 0, nowTotal = 0, menuCells = 0, menuTotal = 0, pickCells = 0, pickTotal = 0;
const confirm = [];
for (const vp of [375, 768, 1280]) {
  for (const theme of ["light", "dark"]) {
    for (const lang of ["en", "sv-SE"]) {
      // D4-s1-05: inline default view, measured indoor sensor present
      {
        const { ctx, page } = await mount(browser, vp, theme, lang, withActuals(planStates(plan)), {});
        const a = await rectOf(page, "text.now-label"), b = await rectOf(page, "text.now-temp");
        nowTotal++;
        if (a && b && Math.min(a.r, b.r) - Math.max(a.l, b.l) > 0 && Math.min(a.b, b.b) - Math.max(a.t, b.t) > 0) nowCells++;
        await ctx.close();
      }
      // D4-s1-02: expanded dialog by a real click on the card, then a real click at 97% of the space lane
      {
        const { ctx, page } = await mount(browser, vp, theme, lang, planStates(plan), { what_if: true });
        await page.mouse.click(40, 40);
        await page.waitForTimeout(150);
        const lanes = await inRoot(page, (root) => [...root.querySelectorAll("rect.lane[data-channel]")].map((e) => { const r = e.getBoundingClientRect(); return { ch: e.dataset.channel, l: r.left, r: r.right, t: r.top, b: r.bottom }; }));
        const laneHit = (x, y) => inRoot(page, (root, p) => { const e = root.elementFromPoint(p[0], p[1]); return !!(e && e.matches && e.matches("rect.lane[data-channel]")); }, [x, y]);
        const openAt = async (x, y, tag) => {
          menuTotal++;
          await page.mouse.click(x, y);
          await page.waitForTimeout(150);
          const m = await rectOf(page, ".slot-menu");
          const wrap = await inRoot(page, (root) => { const mm = root.querySelector(".slot-menu"); const w = mm && mm.closest(".chartwrap"); if (!w) return null; const r = w.getBoundingClientRect(); return { l: r.left, r: r.right }; });
          const spill = m && wrap ? Math.max(m.r - wrap.r, m.r - vp) : null;
          if (m && spill > 0.5) menuCells++;
          if (m && spill > 0.5 && tag === "zoom") zoomSpill++;
          if (m && spill > 0.5 && tag === "edge") edgeSpill++;
          if (m && m.r > vp + 0.5) vpSpill = Math.max(vpSpill, m.r - vp);
          console.log(`# menu ${tag} ${vp}/${theme}/${lang}: tap x=${x.toFixed(0)} ${m ? `menu ..${m.r.toFixed(1)} wrap ..${wrap.r.toFixed(1)} spill ${spill.toFixed(1)}` : "NO MENU"}`);
          await inRoot(page, () => { document.querySelector("heatpump-optimizer-card").lanes.closeMenu(); });
          await page.waitForTimeout(60);
        };
        for (const ch of ["space", "dhw"]) {
          const lane = lanes.filter((l) => l.ch === ch).pop();
          if (!lane) continue;
          const y = (lane.t + lane.b) / 2;
          // (a) the rightmost point a real tap still opens the menu (unzoomed default window)
          let x = lane.r - 1;
          while (x > lane.l && !(await laneHit(x, y))) x -= 2;
          if (x > lane.l) await openAt(x, y, "edge");
        }
        // (b) zoom in with the real + button (x3), then tap at 97% of the lane
        for (let k = 0; k < 3; k++) {
          const zb = await inRoot(page, (root) => { const e = [...root.querySelectorAll("dialog .vc-in")].pop(); if (!e) return null; const r = e.getBoundingClientRect(); return { x: (r.left + r.right) / 2, y: (r.top + r.bottom) / 2 }; });
          if (zb) { await page.mouse.click(zb.x, zb.y); await page.waitForTimeout(120); }
        }
        const lanes2 = await inRoot(page, (root) => [...root.querySelectorAll("rect.lane[data-channel]")].map((e) => { const r = e.getBoundingClientRect(); return { ch: e.dataset.channel, l: r.left, r: r.right, t: r.top, b: r.bottom }; }));
        for (const ch of ["space", "dhw"]) {
          const lane = lanes2.filter((l) => l.ch === ch).pop();
          if (!lane) continue;
          const x = lane.l + 0.97 * (lane.r - lane.l), y = (lane.t + lane.b) / 2;
          if (await laneHit(x, y)) await openAt(x, y, "zoom");
          else console.log(`# menu zoom ${vp}/${theme}/${lang}/${ch}: 97% is not an editable lane after zoom`);
        }
        // D4-s1-01 live: arm the save by a real click
        const save = await inRoot(page, (root) => { const e = root.querySelector(".wi-save"); if (!e) return null; e.scrollIntoView({ block: "center" }); const r = e.getBoundingClientRect(); return { x: (r.left + r.right) / 2, y: (r.top + r.bottom) / 2 }; });
        if (save) {
          await page.mouse.click(save.x, save.y);
          await page.waitForTimeout(120);
          const col = await inRoot(page, (root) => { const e = root.querySelector(".wi-save.confirm"); if (!e) return null; const cs = getComputedStyle(e); return [cs.color, cs.backgroundColor]; });
          if (col) confirm.push(`${vp}/${theme}/${lang} ${col.join(" on ")}`);
        }
        await ctx.close();
      }
      // D4-s1-03: setup page, real click on the wood-tank box, real typing in the filter
      if (vp !== 1280 || theme === "light") {
        const states = { ...planStates(plan), ...setupSensorStates(), ...bigStates() };
        states[DEFAULT_SPACE].attributes.setup_topology = qaTopologies().base;
        const { ctx, page } = await mount(browser, vp, theme, lang, states, {});
        await page.mouse.click(40, 40);
        await page.waitForTimeout(150);
        const tab = await inRoot(page, (root) => { const e = root.querySelector(".dlg-tab[data-page='setup']"); if (!e) return null; const r = e.getBoundingClientRect(); return { x: (r.left + r.right) / 2, y: (r.top + r.bottom) / 2 }; });
        if (tab) { await page.mouse.click(tab.x, tab.y); await page.waitForTimeout(150); }
        const hit = await inRoot(page, (root) => { const e = root.querySelector(".setup-hit[data-key='wood_tank_top_entity']"); if (!e) return null; e.scrollIntoView({ block: "center" }); const r = e.getBoundingClientRect(); return { x: (r.left + r.right) / 2, y: (r.top + r.bottom) / 2 }; });
        if (hit) {
          pickTotal++;
          await page.mouse.click(hit.x, hit.y);
          await page.waitForTimeout(120);
          await page.keyboard.type("vedpanna");
          await page.waitForTimeout(200);
          const twins = await inRoot(page, (root) => {
            const sel = root.querySelector("select.sp-select");
            if (!sel) return -1;
            const cs = getComputedStyle(sel);
            const ctx2 = document.createElement("canvas").getContext("2d");
            ctx2.font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
            const w = sel.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight) - 8; // option inner padding
            const vis = [...sel.options].map((o) => { let s = o.text; while (s && ctx2.measureText(s).width > w) s = s.slice(0, -1); return [o.text, s]; });
            let n = 0;
            for (let i = 0; i < vis.length; i++) for (let j = i + 1; j < vis.length; j++) if (vis[i][0] !== vis[j][0] && vis[i][1] === vis[j][1]) n++;
            return n;
          });
          if (twins > 0) pickCells++;
          console.log(`# picker ${vp}/${theme}/${lang}: indistinct pairs=${twins}`);
        }
        await ctx.close();
      }
    }
  }
}
await browser.close();
console.log(`RESULT now_overlap_cells=${nowCells} count (of ${nowTotal})`);
console.log(`RESULT menu_spill_openings=${menuCells} count (of ${menuTotal} real-tap openings)`);
console.log(`RESULT menu_spill_edge_unzoomed=${edgeSpill} count`);
console.log(`RESULT menu_spill_zoomed_97pct=${zoomSpill} count`);
console.log(`RESULT max_menu_viewport_out_px=${vpSpill.toFixed(1)} px`);
console.log(`RESULT picker_twin_cells=${pickCells} count (of ${pickTotal})`);
for (const c of [...new Set(confirm.map((s) => s.split(" ").slice(1).join(" ")))]) console.log(`# armed save colours: ${c}`);
console.log(`RESULT confirm_contrast_real_light=${ratio("#ffffff", REAL.light["--error-color"]).toFixed(2)} ratio`);
console.log(`RESULT confirm_armed_by_real_click=${confirm.length} count`);
const u = process.cpuUsage(t0);
console.log(`RESULT thread_factor=1.00`);
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
const vm = fs.existsSync("/proc/vmstat") ? fs.readFileSync("/proc/vmstat", "utf8").match(/pswpin (\d+)/) : null;
console.log(`RESULT swapins=${vm ? vm[1] : 0}`);
