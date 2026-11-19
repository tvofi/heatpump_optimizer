// R11-SEAM-card, D4-s1-01: the layout editor's pipe click target, counted the
// way the card's own click handler resolves it, at each pipe's best point.
//
// The finder's harness (plan/r11 dev/audit/rounds/round11/D4/s1/m1_pipes.mjs,
// sha1 f0f66a6e84d6) counts a pipe's band only where
// `shadowRoot.elementFromPoint` returns the visible `.setup-pipe` itself, and
// only across the pipe's midpoint. The fix gives each pipe an invisible twin
// on the same path (`.layout-pipe-hit`, `data-hit-edge`), drawn over the
// pipe and under the boxes, ports and rows, and `LayoutEditor.onClick`
// removes `data.edge || data.hitEdge`. Under the finder's rule the fixed card
// reads 576 still (the twin hides the stroke it measured). This companion
// changes two things, nothing else:
//   - a point counts when the element under it is the pipe OR its twin
//     naming the same edge -- the rule the production handler applies;
//   - the band is read at 19 points along the pipe (5 % to 95 % of its
//     length), each scrolled into the viewport first, and the pipe's figure
//     is its best point: a target is reachable where it is widest, and a
//     midpoint off-screen in a sideways-scrolling canvas read 0 px before.
// A pipe still under the floor at its best point is listed with the
// elements that cut its band there (a port, box, title or row, which the
// design draws above the twin so that each keeps its own gesture).
// Null control: the same scan on each `.layout-port-hit` (median px).
//
// Run from a tree that carries the round-11 export beside it (the finder's
// m1_browser.mjs, sha1 3326714a0c1e, renders the card at that tree):
//   PW=<playwright dir> PLAYWRIGHT_BROWSERS_PATH=<chromium lock> HPO_PLANDATA=<plan_view.py payload> \
//     node dev/audit/harnesses/r11_card_pipe_hit.mjs [PERTURB=1]
// PERTURB=1 drops the twin's width floor in memory (`Math.max(3.5,` ->
//   `Math.min(3.5,`): the count must go back to every pipe.
// Expected: base 1723f9fdc9 576 of 576 (no twin: the stroke alone); the head
// figure is the pull request body's.
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
  const inView = (x, y) => x >= 0 && y >= 0 && x < innerWidth && y < innerHeight;
  const bandAt = (el, edge, p, q) => {
    let P = new DOMPoint(p.x, p.y).matrixTransform(el.getScreenCTM());
    if (!inView(P.x, P.y)) {
      el.scrollIntoView({ block: "center", inline: "center" });
      P = new DOMPoint(p.x, p.y).matrixTransform(el.getScreenCTM());
      if (!inView(P.x, P.y)) return null;
    }
    const Q = new DOMPoint(q.x, q.y).matrixTransform(el.getScreenCTM());
    let dx = Q.x - P.x, dy = Q.y - P.y; const n = Math.hypot(dx, dy) || 1; dx /= n; dy /= n;
    const nx = -dy, ny = dx;
    let hit = 0; const cut = {};
    for (let s = -40; s <= 40; s += 0.25) {
      const e = r.elementFromPoint(P.x + nx * s, P.y + ny * s);
      if (e === el || (edge && e && e.dataset && e.dataset.hitEdge === edge)) hit += 0.25;
      else if (Math.abs(s) <= 22) { const k = e ? (e.getAttribute("class") || e.tagName).split(" ")[0] : "outside"; cut[k] = 1; }
    }
    return { px: +hit.toFixed(2), cut: Object.keys(cut).sort() };
  };
  const best = (el, edge) => {
    const len = el.getTotalLength ? el.getTotalLength() : 0;
    if (!(len > 0)) {
      const b = el.getBBox(); const p = { x: b.x + b.width / 2, y: b.y + b.height / 2 };
      return bandAt(el, edge, p, { x: p.x + 1, y: p.y }) || { px: 0, cut: ["outside"] };
    }
    let top = null;
    for (let i = 1; i <= 19; i++) {
      const at = (len * i) / 20;
      const got = bandAt(el, edge, el.getPointAtLength(at), el.getPointAtLength(Math.min(len, at + 1)));
      if (got && (!top || got.px > top.px)) top = got;
    }
    return top || { px: 0, cut: ["outside"] };
  };
  for (const el of r.querySelectorAll(".setup-svg.editing .setup-pipe")) {
    const edge = el.getAttribute("data-edge");
    out.push({ k: "pipe", edge, ...best(el, edge) });
  }
  // The null control as the finder ran it: one band through the port's centre.
  const centre = (el) => { const b = el.getBBox(); const p = { x: b.x + b.width / 2, y: b.y + b.height / 2 };
    return (bandAt(el, null, p, { x: p.x + 1, y: p.y }) || { px: 0 }).px; };
  for (const el of r.querySelectorAll(".setup-svg.editing .layout-port-hit")) out.push({ k: "port", px: centre(el) });
  return out;
})()`;
const env = { ...process.env, OUT, LIGHT: "1", PROBE, STATES: "layout_editing_dragged,layout_editing_tidy", WORKERS: "4" };
if (process.argv.includes("PERTURB=1") || process.env.PERTURB === "1") {
  env.HPO_PERTURB = JSON.stringify([["Math.max(3.5, _targetMinPx() * unitsPerPx)", "Math.min(3.5, _targetMinPx() * unitsPerPx)"]]);
}
execFileSync("node", [BROWSER], { env, stdio: ["ignore", "ignore", "inherit"] });
const recs = readFileSync(path.join(OUT, "renders.jsonl"), "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
let pipes = 0, under = 0, mn = Infinity, mx = 0, renders = 0; const ports = []; const residual = {};
for (const r of recs) {
  if (!Array.isArray(r.probe)) { console.log(`probe missing ${r.tag}: ${r.probe} ${r.threw || ""}`); continue; }
  renders++;
  const floor = r.pointer === "coarse" ? 44 : 24;
  for (const p of r.probe) {
    if (p.k === "port") { ports.push(p.px); continue; }
    pipes++; mn = Math.min(mn, p.px); mx = Math.max(mx, p.px);
    if (p.px < floor) {
      under++;
      const k = `${r.state} ${r.vp} ${r.pointer} ${p.edge} cut by ${p.cut.join("+") || "-"}`;
      (residual[k] = residual[k] || []).push(p.px);
    }
  }
}
for (const [k, v] of Object.entries(residual).sort()) console.log(`  residual: ${k}: ${v.length} renders, best ${Math.min(...v)}..${Math.max(...v)} px`);
const R = (k, v, u = "") => console.log(`RESULT ${k}=${v}${u ? " " + u : ""}`);
R("renders", renders, "renders");
R("pipes", pipes, "pipe targets");
R("pipe_hit_under_floor", under, "pipes under 24 px (44 coarse) at their best point, pipe or its twin");
R("pipe_hit_min_px", mn, "px");
R("pipe_hit_max_px", mx, "px");
ports.sort((a, b) => a - b);
R("port_hit_median_px", ports.length ? ports[ports.length >> 1] : "n/a", "px (null control)");
R("load1", os.loadavg()[0].toFixed(2));
