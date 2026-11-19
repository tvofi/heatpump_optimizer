// R11-SEAM-card, D4-s1-01: the layout editor's pipe click target, counted the
// way the card's own click handler resolves it.
//
// The finder's harness (plan/r11 dev/audit/rounds/round11/D4/s1/m1_pipes.mjs,
// sha1 f0f66a6e84d6) counts a pipe's band only where
// `shadowRoot.elementFromPoint` returns the visible `.setup-pipe` itself. The
// fix gives each pipe an invisible twin on the same path
// (`.layout-pipe-hit`, `data-hit-edge`), drawn over it, and
// `LayoutEditor.onClick` removes `data.edge || data.hitEdge`: a point where
// the twin is on top removes the pipe, so under the finder's rule the fixed
// card reads 576 still (the twin hides the stroke it measured). This
// companion is that harness with one change: a point counts when the element
// under it is the pipe OR its twin naming the same edge -- the rule the
// production handler applies. Same renders, same scan, same null control
// (`.layout-port-hit`, median px).
//
// Run from a tree that carries the round-11 export beside it (the finder's
// m1_browser.mjs, sha1 3326714a0c1e, renders the card at that tree):
//   PW=<playwright dir> PLAYWRIGHT_BROWSERS_PATH=<chromium lock> HPO_PLANDATA=<plan_view.py payload> \
//     node dev/audit/harnesses/r11_card_pipe_hit.mjs [PERTURB=1]
// PERTURB=1 drops the twin's width floor in memory (`Math.max(3.5,` ->
//   `Math.min(3.5,`): the count must go back to every pipe.
// Expected: base 1723f9fdc9 576 of 576 (the base draws no twin, so the two
// rules agree there); head 0; port median as the finder's (30.5 px Linux,
// 31.25 px macOS).
import { execFileSync } from "node:child_process";
import { readFileSync, mkdtempSync, existsSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const BROWSER = path.join(HERE, "../rounds/round11/D4/s1/m1_browser.mjs");
if (!existsSync(BROWSER)) {
  console.error(`missing ${BROWSER}: export plan/r11's dev/audit/rounds/round11/D4/s1 beside this tree`);
  process.exit(2);
}
const OUT = mkdtempSync(path.join(process.env.TMPDIR || os.tmpdir(), "r11pipehit-"));
const PROBE = `(() => {
  const r = c.shadowRoot, out = [];
  const band = (el, edge) => {
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
      if (e === el || (edge && e && e.dataset && e.dataset.hitEdge === edge)) hit += 0.25;
    }
    return +hit.toFixed(2);
  };
  for (const el of r.querySelectorAll(".setup-svg.editing .setup-pipe")) {
    const edge = el.getAttribute("data-edge");
    out.push({ k: "pipe", edge, px: band(el, edge) });
  }
  for (const el of r.querySelectorAll(".setup-svg.editing .layout-port-hit")) out.push({ k: "port", px: band(el, null) });
  return out;
})()`;
const env = { ...process.env, OUT, LIGHT: "1", PROBE, STATES: "layout_editing_dragged,layout_editing_tidy", WORKERS: "4" };
if (process.argv.includes("PERTURB=1") || process.env.PERTURB === "1") {
  env.HPO_PERTURB = JSON.stringify([["Math.max(3.5, _targetMinPx() * unitsPerPx)", "Math.min(3.5, _targetMinPx() * unitsPerPx)"]]);
}
execFileSync("node", [BROWSER], { env, stdio: ["ignore", "ignore", "inherit"] });
const recs = readFileSync(path.join(OUT, "renders.jsonl"), "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
let pipes = 0, under = 0, mn = Infinity, mx = 0, renders = 0; const ports = [];
for (const r of recs) {
  if (!Array.isArray(r.probe)) { console.log(`probe missing ${r.tag}: ${r.probe} ${r.threw || ""}`); continue; }
  renders++;
  const floor = r.pointer === "coarse" ? 44 : 24;
  for (const p of r.probe) {
    if (p.k === "port") { ports.push(p.px); continue; }
    pipes++; mn = Math.min(mn, p.px); mx = Math.max(mx, p.px);
    if (p.px < floor) under++;
  }
}
const R = (k, v, u = "") => console.log(`RESULT ${k}=${v}${u ? " " + u : ""}`);
R("renders", renders, "renders");
R("pipes", pipes, "pipe targets");
R("pipe_hit_under_floor", under, "pipes under 24 px (44 coarse), pipe or its twin");
R("pipe_hit_min_px", mn, "px");
R("pipe_hit_max_px", mx, "px");
ports.sort((a, b) => a - b);
R("port_hit_median_px", ports.length ? ports[ports.length >> 1] : "n/a", "px (null control)");
R("load1", os.loadavg()[0].toFixed(2));
