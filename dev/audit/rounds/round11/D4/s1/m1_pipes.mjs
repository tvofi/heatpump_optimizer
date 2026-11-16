// D4.M1 witness harness (round 11, seat D4-s1): the layout editor's pipe click target.
//
// Metric: pipe_hit_px = for each `.setup-svg.editing .setup-pipe` the card draws in the
//   layout editor, the length (px) of the line through the pipe's midpoint, normal to the
//   pipe, along which `shadowRoot.elementFromPoint` returns that pipe (0.25 px steps,
//   +-40 px). Clicking a pipe is how a connection is removed (the card's own comment above
//   `.setup-svg.editing .setup-pipe`). Counted: pipes whose band is under 24 px (fine) or
//   44 px (coarse), D4-criteria F1. Count key: the production card's own hit test.
// Instrumented symbol: heatpump-optimizer-card.js:cardStyleBlock (the rule
//   `.setup-svg.editing .setup-pipe { stroke-width: 3.5; ... }`) through the rendered card.
// Perturbation: PERTURB=1 rewrites that rule's `stroke-width: 3.5` to `stroke-width: 60`
//   in memory (one-line production edit): pipe_hit_under_floor must go down.
// Null control: the same scan run on a `.layout-port-hit` (a target the card did size)
//   in the same renders: reported as port_hit_median_px (a port partly under a box reads less).
//   A pipe whose midpoint sits under a dragged box reads 0 px (counted, it is under the floor).
//
// Run from the export root (PW and PLAYWRIGHT_BROWSERS_PATH as m1_browser.mjs's header):
//   PW=$HOME/pwlane/node_modules/playwright PLAYWRIGHT_BROWSERS_PATH=$HOME/pw-browsers-lock \
//     HPO_PLANDATA=<plan_view.py payload> node dev/audit/rounds/round11/D4/s1/m1_pipes.mjs [PERTURB=1]
// Expected (baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B9, Chromium 158.0.8127.18):
//   pipe_hit_under_floor = 576 of 576 (exact); max band 5.75 px (1280); port median 30.5 px;
//   PERTURB=1 -> 296 (down; the rest sit under boxes or ports).
import { execFileSync } from "node:child_process";
import { readFileSync, mkdtempSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const OUT = mkdtempSync(path.join(process.env.TMPDIR || os.tmpdir(), "d4s1pipes-"));
const PROBE = `(() => {
  const r = c.shadowRoot, out = [];
  const band = (el, sel) => {
    const len = el.getTotalLength ? el.getTotalLength() : 0;
    const m = el.getScreenCTM();
    let p, q;
    if (len > 0) { p = el.getPointAtLength(len / 2); q = el.getPointAtLength(Math.min(len, len / 2 + 1)); }
    else { const b = el.getBBox(); p = { x: b.x + b.width / 2, y: b.y + b.height / 2 }; q = { x: p.x + 1, y: p.y }; }
    const P = new DOMPoint(p.x, p.y).matrixTransform(m), Q = new DOMPoint(q.x, q.y).matrixTransform(m);
    let dx = Q.x - P.x, dy = Q.y - P.y; const n = Math.hypot(dx, dy) || 1; dx /= n; dy /= n;
    const nx = -dy, ny = dx;
    P.y < 0 || P.y > innerHeight ? el.scrollIntoView({ block: "center" }) : 0;
    const P2 = new DOMPoint(p.x, p.y).matrixTransform(el.getScreenCTM());
    let hit = 0;
    for (let s = -40; s <= 40; s += 0.25) {
      const e = r.elementFromPoint(P2.x + nx * s, P2.y + ny * s);
      if (e === el) hit += 0.25;
    }
    return +hit.toFixed(2);
  };
  for (const el of r.querySelectorAll(".setup-svg.editing .setup-pipe")) out.push({ k: "pipe", edge: el.getAttribute("data-edge"), px: band(el) });
  for (const el of r.querySelectorAll(".setup-svg.editing .layout-port-hit")) out.push({ k: "port", px: band(el) });
  return out;
})()`;
const env = { ...process.env, OUT, LIGHT: "1", PROBE, STATES: "layout_editing_dragged,layout_editing_tidy", WORKERS: "4" };
if (process.argv.includes("PERTURB=1") || process.env.PERTURB === "1") {
  env.HPO_PERTURB = JSON.stringify([[".setup-svg.editing .setup-pipe { stroke-width: 3.5;", ".setup-svg.editing .setup-pipe { stroke-width: 60;"]]);
}
execFileSync("node", [path.join(HERE, "m1_browser.mjs")], { env, stdio: ["ignore", "ignore", "inherit"] });
const recs = readFileSync(path.join(OUT, "renders.jsonl"), "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
let pipes = 0, under = 0, mn = Infinity, mx = 0, renders = 0; const ports = [];
const byVp = {};
for (const r of recs) {
  if (!Array.isArray(r.probe)) { console.log(`probe missing ${r.tag}: ${r.probe} ${r.threw || ""}`); continue; }
  renders++;
  const floor = r.pointer === "coarse" ? 44 : 24;
  for (const p of r.probe) {
    if (p.k === "port") { ports.push(p.px); continue; }
    pipes++; mn = Math.min(mn, p.px); mx = Math.max(mx, p.px);
    if (p.px < floor) under++;
    const k = `${r.vp}/${r.pointer}`; byVp[k] = byVp[k] || []; byVp[k].push(p.px);
  }
}
for (const [k, v] of Object.entries(byVp).sort()) console.log(`  ${k}: pipes ${v.length}, band ${Math.min(...v)}..${Math.max(...v)} px`);
const R = (k, v, u = "") => console.log(`RESULT ${k}=${v}${u ? " " + u : ""}`);
R("renders", renders, "renders");
R("pipes", pipes, "pipe targets");
R("pipe_hit_under_floor", under, "pipes under 24 px (44 coarse)");
R("pipe_hit_min_px", mn, "px");
R("pipe_hit_max_px", mx, "px");
ports.sort((a, b) => a - b);
R("port_hit_median_px", ports.length ? ports[ports.length >> 1] : "n/a", "px (null control: the layout-port-hit targets the card sized, same scan)");
R("thread_factor", 1.0, "(no BLAS; node + chromium)");
R("load1", os.loadavg()[0].toFixed(2));
R("swapins", (readFileSync("/proc/vmstat", "utf8").match(/^pswpin (\d+)/m) || [0, "n/a"])[1]);
