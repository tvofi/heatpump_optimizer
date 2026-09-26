// D4 verifier V3: D4-s1-04 by this seat's own metric -- with the setup layout editor opened by REAL
// clicks, walk the dialog with REAL Tab presses and count focus stops that land on a pipe
// (path.setup-pipe), a box (.setup-box) or a port inside .setup-canvas (a .setup-hit is the entity-row
// button that opens the picker, not a layout edit, and is excluded); beside it,
// the number of such elements the editor draws (the pointer-reachable population).
//
// Metric (one line): kbd_stops_on_editor_items = distinct pipe/box/port elements that receive focus
//   during 80 Tab presses from the dialog's first stop, layout editor open.
// Command (repository root):
//   T=$(mktemp -d) && HPO_PLANDATA=$T/plandata.json PYTHONPATH=tests/hastub /home/claude/venv/bin/python tests/plan_view.py >/dev/null && \
//   HPO_PLANDATA=$T/plandata.json NODE_PATH=/home/claude/pwlane/node_modules PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers \
//     node tools/audit/round9/D4/verify-v3/layout_focus.mjs
// Expected at 1936d5ca72a06556eeed4e8e5bf3dea520e517e1: kbd_stops_on_editor_items=0 (exact) with
//   pipes>0; perturbation --perturb: tabindex="0" injected on every path.setup-pipe after render -> >0.
// Machine: G2-V3 cloud container, 4 cores, Linux 6.18, Chromium (Playwright 1.56.1).
import fs from "node:fs";
import os from "node:os";
import { createRequire } from "node:module";
import { HOUR, planStates, setupSensorStates, layoutCatalogTopo, DEFAULT_SPACE } from "../../../../../tests/card_rig.mjs";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const cardSrc = fs.readFileSync("custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js", "utf8");
const plan = JSON.parse(fs.readFileSync(process.env.HPO_PLANDATA, "utf8"));
const FROZEN = Date.parse(plan.dhw_plan.forecast[0].t) + 6 * HOUR;
const PERTURB = process.argv.includes("--perturb");

const browser = await chromium.launch();
let stopsTotal = 0, pipesTotal = 0, boxesTotal = 0;
for (const vp of [375, 1280]) {
  const ctx = await browser.newContext({ viewport: { width: vp, height: 900 } });
  await ctx.clock.setFixedTime(FROZEN);
  await ctx.route("http://v3.test/**", (r) => r.fulfill({ contentType: "text/html", body: "<!doctype html><html><body></body></html>" }));
  const page = await ctx.newPage();
  await page.goto("http://v3.test/");
  await page.addScriptTag({ content: cardSrc });
  const st = { ...planStates(plan), ...setupSensorStates() };
  st[DEFAULT_SPACE].attributes.setup_topology = layoutCatalogTopo();
  await page.evaluate(([s, w]) => {
    customElements.define("ha-card", class extends HTMLElement {});
    const c = document.createElement("heatpump-optimizer-card");
    c.style.cssText = `display:block;width:${w}px`;
    c.setConfig({ type: "x" });
    c.hass = { states: s, language: "en", callService: async () => ({}) };
    document.body.appendChild(c);
  }, [st, vp - 16]);
  await page.waitForTimeout(100);
  const center = (sel) => page.evaluate((s) => { const r0 = document.querySelector("heatpump-optimizer-card").shadowRoot; const e = r0.querySelector(s); if (!e) return null; e.scrollIntoView({ block: "center" }); const r = e.getBoundingClientRect(); return { x: (r.left + r.right) / 2, y: (r.top + r.bottom) / 2 }; }, sel);
  await page.mouse.click(30, 30); await page.waitForTimeout(150);
  let p = await center(".dlg-tab[data-page='setup']"); if (p) { await page.mouse.click(p.x, p.y); await page.waitForTimeout(150); }
  p = await center("button.layout-edit-toggle"); if (p) { await page.mouse.click(p.x, p.y); await page.waitForTimeout(150); }
  if (PERTURB) await page.evaluate(() => { for (const e of document.querySelector("heatpump-optimizer-card").shadowRoot.querySelectorAll("path.setup-pipe")) e.setAttribute("tabindex", "0"); });
  const counts = await page.evaluate(() => { const r0 = document.querySelector("heatpump-optimizer-card").shadowRoot;
    return { pipes: r0.querySelectorAll(".setup-canvas path.setup-pipe").length, boxes: r0.querySelectorAll(".setup-canvas .setup-box").length, editing: !!r0.querySelector(".layout-edit-toggle.on, .layout-editing, .setup-canvas.editing") }; });
  const seen = new Set();
  const all = [];
  for (let k = 0; k < 80; k++) {
    await page.keyboard.press("Tab");
    const f = await page.evaluate(() => { let a = document.activeElement; while (a && a.shadowRoot && a.shadowRoot.activeElement) a = a.shadowRoot.activeElement;
      if (!a) return null; const inCanvas = !!(a.closest && a.closest(".setup-canvas"));
      return { tag: a.tagName.toLowerCase(), cls: String(a.getAttribute("class") || ""), edge: a.getAttribute("data-edge") || "", inCanvas }; });
    if (f) all.push(`${f.tag}.${f.cls}`);
    if (f && f.inCanvas && /setup-pipe|setup-box|setup-port/.test(f.cls)) seen.add(`${f.tag}.${f.cls}.${f.edge}`);
  }
  console.log(`# ${vp}px pipes=${counts.pipes} boxes=${counts.boxes} editing=${counts.editing} editor-item stops=${seen.size}; distinct stops=${[...new Set(all)].length}: ${[...new Set(all)].slice(0, 14).join(", ")}`);
  stopsTotal += seen.size; pipesTotal += counts.pipes; boxesTotal += counts.boxes;
  await ctx.close();
}
await browser.close();
console.log(`RESULT pipes_drawn=${pipesTotal} count`);
console.log(`RESULT boxes_drawn=${boxesTotal} count`);
console.log(`RESULT kbd_stops_on_editor_items=${stopsTotal} count`);
console.log("RESULT thread_factor=1.00");
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
const vm = fs.readFileSync("/proc/vmstat", "utf8").match(/pswpin (\d+)/);
console.log(`RESULT swapins=${vm ? vm[1] : 0}`);
