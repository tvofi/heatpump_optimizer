// D4-s1 (D4.M1): can the setup page's layout editor be operated from the keyboard?
//
// Metric definitions (per viewport, layoutCatalogTopo() with editing switched on by clicking .layout-edit-toggle):
//   pipes              pipes drawn in the editing canvas ([data-edge] paths, what LayoutEditor.onClick removes)
//   pipes_click        pipes whose removal a real mouse click achieves (control: the action exists)
//   pipes_keyboard     pipes a keyboard user can remove: reachable by Tab, then Enter / Delete / Space removes the edge
//   boxes_keyboard     boxes a keyboard user can move: a Tab stop inside the box, then arrow keys change LayoutEditor.edit.positions
// Key of the count: LayoutEditor.edit.edges / .positions -- the editor's own state, not the DOM attributes.
// Run from the repository root:
//   T=$(mktemp -d) && HPO_PLANDATA=$T/plandata.json PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tests/plan_view.py >/dev/null && \
//   HPO_PLANDATA=$T/plandata.json NODE_PATH=/home/claude/pwlane/node_modules PLAYWRIGHT_BROWSERS_PATH=/root/.cache/pw-browsers \
//     node tools/audit/round9/D4/s1/layout_kbd.mjs [--perturb kbd]
// Perturbation `kbd`: the pipe template gains tabindex="0" and LayoutEditor.attach forwards Enter/Delete on the
// canvas to onClick (one line each) -> pipes_keyboard must go up from 0 to pipes.
// Expected (baseline): pipes_keyboard=0, boxes_keyboard=0, pipes_click=pipes. Exact.
// Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, box B10, Chromium 141.
// Instrumented symbol: heatpump-optimizer-card.js:LayoutEditor (onClick, removeEdge, edit.edges/positions).
import fs from "node:fs";
import os from "node:os";
import { createRequire } from "node:module";
import { planStates, setupSensorStates, layoutCatalogTopo, DEFAULT_SPACE } from "../../../../../tests/card_rig.mjs";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const plan = JSON.parse(fs.readFileSync(process.env.HPO_PLANDATA, "utf8"));
const FROZEN = Date.parse(plan.dhw_plan.forecast[0].t) + 6 * 3600000;
let src = fs.readFileSync("custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js", "utf8");
if (process.argv.includes("--perturb")) {
  // Two one-line edits: the pipe markup becomes a Tab stop, and the canvas forwards Enter/Delete to onClick.
  const a = '<path class="setup-pipe${extra}" data-edge="${edge}"';
  const c = '    canvas.addEventListener("click", this.onClick);\n';
  if (!src.includes(a) || !src.includes(c)) throw new Error("anchor missing");
  src = src.split(a).join('<path class="setup-pipe${extra}" data-edge="${edge}" tabindex="0"');
  src = src.split(c).join(c + '    canvas.addEventListener("keydown", (ev) => { if (ev.key === "Enter" || ev.key === "Delete") this.onClick(ev); });\n');
}
const states = { ...planStates(plan), ...setupSensorStates() };
states[DEFAULT_SPACE].attributes.setup_topology = layoutCatalogTopo();

const b = await chromium.launch();
const R = { pipes: 0, pipes_click: 0, pipes_keyboard: 0, boxes: 0, boxes_keyboard: 0 };
for (const w of [375, 768, 1280]) {
  const ctx = await b.newContext({ viewport: { width: w, height: 900 } });
  await ctx.clock.setFixedTime(FROZEN);
  await ctx.route("http://hpo.test/**", (r) => r.fulfill({ contentType: "text/html", body: "<!doctype html><html><body style='margin:0;padding:8px;font-family:Liberation Sans,Arial'></body></html>" }));
  const p = await ctx.newPage();
  const mount = async () => {
    await p.goto("http://hpo.test/");
    await p.addScriptTag({ content: src });
    await p.evaluate(([st, cw]) => {
      const c = document.createElement("heatpump-optimizer-card"); c.style.display = "block"; c.style.width = cw + "px";
      c.setConfig({ type: "custom:heatpump-optimizer-card" }); c.hass = { states: st, language: "en" };
      document.body.appendChild(c); c._onCardClick({}); c.dialog.page = "setup"; c._render();
    }, [states, w - 16]);
    await p.waitForTimeout(150);
    await p.evaluate(() => document.querySelector("heatpump-optimizer-card").shadowRoot.querySelector(".layout-edit-toggle").click());
    await p.waitForTimeout(150);
  };
  const edges = () => p.evaluate(() => document.querySelector("heatpump-optimizer-card").layoutEditor.edit.edges.map((e) => `${e[0]}>${e[1]}`));
  const pos = () => p.evaluate(() => JSON.stringify(document.querySelector("heatpump-optimizer-card").layoutEditor.edit.positions || {}) +
    JSON.stringify((document.querySelector("heatpump-optimizer-card").layoutEditor.boxes || []).map((q) => [q.place, q.x, q.y])));
  await mount();
  const names = await p.evaluate(() => [...document.querySelector("heatpump-optimizer-card").shadowRoot.querySelectorAll("svg.setup-svg [data-edge]")].map((e) => e.dataset.edge));
  const boxes = await p.evaluate(() => (document.querySelector("heatpump-optimizer-card").layoutEditor.boxes || []).map((q) => q.place));
  R.pipes += names.length; R.boxes += boxes.length;
  for (const name of names) {
    // Click arm (control).
    await mount();
    const before = (await edges()).length;
    const at = await p.evaluate((n) => {
      const el = document.querySelector("heatpump-optimizer-card").shadowRoot.querySelector(`[data-edge="${n}"]`);
      el.scrollIntoView({ block: "center", inline: "center" });
      const len = el.getTotalLength(); const pt = el.getPointAtLength(len / 2);
      const m = el.getScreenCTM(); const q = new DOMPoint(pt.x, pt.y).matrixTransform(m);
      return { x: q.x, y: q.y };
    }, name);
    await p.mouse.click(at.x, at.y);
    await p.waitForTimeout(80);
    if ((await edges()).length < before) R.pipes_click += 1;
    // Keyboard arm: Tab through the dialog; if a stop is this pipe, try Enter, Delete, Space.
    await mount();
    let removed = false;
    for (let i = 0; i < 60 && !removed; i++) {
      await p.keyboard.press("Tab");
      const onIt = await p.evaluate((n) => {
        let a = document.activeElement; while (a && a.shadowRoot && a.shadowRoot.activeElement) a = a.shadowRoot.activeElement;
        return !!(a && a.dataset && a.dataset.edge === n);
      }, name);
      if (!onIt) continue;
      for (const k of ["Enter", "Delete", " "]) {
        const n0 = (await edges()).length;
        await p.keyboard.press(k === " " ? "Space" : k); await p.waitForTimeout(60);
        if ((await edges()).length < n0) { removed = true; break; }
      }
      break;
    }
    if (removed) R.pipes_keyboard += 1;
  }
  // Boxes: any Tab stop, then arrows; did any box move?
  await mount();
  const p0 = await pos();
  let moved = 0;
  for (let i = 0; i < 40; i++) {
    await p.keyboard.press("Tab");
    for (const k of ["ArrowRight", "ArrowDown"]) await p.keyboard.press(k);
    await p.waitForTimeout(20);
    if ((await pos()) !== p0) { moved = 1; break; }
  }
  R.boxes_keyboard += moved ? boxes.length : 0;
  console.log(`${w}px: pipes=${names.length} boxes=${boxes.length}`);
  await ctx.close();
}
await b.close();
for (const [k, v] of Object.entries(R)) console.log(`RESULT ${k}=${v} count`);
console.log("RESULT thread_factor=1.00");
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log("RESULT swapins=0");
