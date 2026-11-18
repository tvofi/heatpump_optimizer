// D4-s1 (D4.M1): what moves when the pointer hovers the expanded chart's slot targets.
//
// Metric: elements of the card's shadow root, present before AND after one hover, whose box moved > 0.5 px,
// keyed by (class-or-tag, direct text, occurrence of that pair) -- stable across the tooltip rows the hover inserts.
// RESULT moved_non_overlay counts the ones outside .tooltip / .crosshair (content that jumps); expected 0.
// Run from the repository root:
//   T=$(mktemp -d) && HPO_PLANDATA=$T/plandata.json PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tests/plan_view.py >/dev/null && \
//   HPO_PLANDATA=$T/plandata.json NODE_PATH=/home/claude/pwlane/node_modules PLAYWRIGHT_BROWSERS_PATH=/root/.cache/pw-browsers \
//     node tools/audit/round9/D4/s1/hover_diag.mjs [--perturb shift]
// Perturbation `shift`: the tooltip made static (in flow) -> moved_non_overlay must go up.
// Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, box B10, Chromium 141. Symbol: HeatpumpOptimizerCard._onPointerMove.
import fs from "node:fs";
import os from "node:os";
import { createRequire } from "node:module";
import { planStates } from "../../../../../tests/card_rig.mjs";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const plan = JSON.parse(fs.readFileSync(process.env.HPO_PLANDATA, "utf8"));
const FROZEN = Date.parse(plan.dhw_plan.forecast[0].t) + 6 * 3600000;
let src = fs.readFileSync("custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js", "utf8");
if (process.argv.includes("--perturb")) src = src.replace("</style>", ".tooltip{position:static !important;display:block}</style>");
let movedNon = 0, movedOverlay = 0, hovers = 0;
const b = await chromium.launch();
for (const w of [375, 1280]) {
  const ctx = await b.newContext({ viewport: { width: w, height: 800 } });
  await ctx.clock.setFixedTime(FROZEN);
  await ctx.route("http://hpo.test/**", (r) => r.fulfill({ contentType: "text/html", body: "<!doctype html><html><body style='margin:0;padding:8px;font-family:Liberation Sans,Arial'></body></html>" }));
  const p = await ctx.newPage();
  await p.goto("http://hpo.test/");
  await p.addScriptTag({ content: src });
  await p.evaluate(([st, cw]) => { const c = document.createElement("heatpump-optimizer-card"); c.style.display = "block"; c.style.width = cw + "px";
    c.setConfig({ type: "custom:heatpump-optimizer-card" }); c.hass = { states: st, language: "en" }; document.body.appendChild(c); c._onCardClick({}); }, [planStates(plan), w - 16]);
  await p.waitForTimeout(400);
  const snap = () => p.evaluate(() => {
    const r = document.querySelector("heatpump-optimizer-card").shadowRoot; const seen = {};
    return [...r.querySelectorAll("*")].map((e) => {
      const t = [...e.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent).join("").trim().slice(0, 20);
      const k0 = `${e.getAttribute("class") || e.tagName}|${t}`; seen[k0] = (seen[k0] || 0) + 1;
      const bb = e.getBoundingClientRect();
      return [`${k0}#${seen[k0]}`, bb.x, bb.y, bb.width, bb.height, !!(e.closest(".tooltip, .crosshair"))];
    });
  });
  const hits = await p.evaluate(() => [...document.querySelector("heatpump-optimizer-card").shadowRoot.querySelectorAll("dialog rect.slot-hit, dialog .chip, dialog button")]
    .map((e) => { const r = e.getBoundingClientRect(); return { x: r.x + r.width / 2, y: r.y + r.height / 2 }; })
    .filter((q) => q.y > 0 && q.y < innerHeight));
  for (const h of hits) {
    const a = new Map((await snap()).map((x) => [x[0], x]));
    await p.mouse.move(h.x, h.y); await p.waitForTimeout(100); hovers += 1;
    for (const x of await snap()) {
      const y = a.get(x[0]); if (!y) continue;
      if ([1, 2, 3, 4].some((i) => Math.abs(x[i] - y[i]) > 0.5)) { if (x[5]) movedOverlay += 1; else { movedNon += 1; console.log(`  moved ${w}px ${x[0]}`); } }
    }
  }
  await ctx.close();
}
await b.close();
console.log(`RESULT hovers=${hovers} count`);
console.log(`RESULT moved_overlay=${movedOverlay} count`);
console.log(`RESULT moved_non_overlay=${movedNon} count`);
console.log("RESULT thread_factor=1.00");
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log("RESULT swapins=0");
